#!/usr/bin/env python3
"""Quick check of the route_fix.py extensions (2026-11-06), without an hours-long routing run.

Works on a copy of the official board (the file stays unchanged) and checks:
1. ENDPOINT_VIAS: end_cells() returns start cells on all signal layers for a track piece that ends at a via
   (VBAT_ADC stub at R6); without the option only on the track's layer.
2. VIA_UNDER_BODIES: under a component on the bottom (U6) there are allowed via spots between the pads on the
   unrouted board; none lies in a foreign SMD pad or in an antenna keepout area.
3. Replay of the open connections: try each open signal connection of the board once with connect(), without
   and with rip-up of the router tracks, and report the result.
4. ISLAND_AREA_SEARCH: connect each GND island without a via once with connect_gnd(), with and without area search.
5. OVAL_DRILLS: slotted hole of the J4 tab S1 blocked as a capsule (case from round M).
6. GND_FANOUT_FIRST: fanout on the unrouted board, afterwards no DRC errors except unconnected items.

Usage: test_route_fix.py [board.kicad_pcb]   (just route-check); exit code 1 if check 1, 2, 5 or 6 fails.
Must run with the system Python that contains pcbnew.
"""
import shutil
import sys
import tempfile
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import route_fix as rf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
OFFICIAL = ROOT / "hardware" / "main-board" / "louie-main.kicad_pcb"
START = ROOT / "build" / "main-board" / "route" / "start.kicad_pcb"  # unrouted board of the last run


def copy_board(pcb, tmp):
    out = Path(tmp) / pcb.name
    shutil.copy(pcb, out)
    for suf in (".kicad_pro", ".kicad_dru"):
        if pcb.with_suffix(suf).exists():
            shutil.copy(pcb.with_suffix(suf), out.with_suffix(suf))
    return out


def check_endpoint_vias(board, grid):
    stub = None
    for t in board.GetTracks():
        if t.GetClass() == "PCB_TRACK" and t.GetNetname() == "/VBAT_ADC" and t.IsLocked() and t.GetLayer() == pcbnew.F_Cu:
            if rf.endpoint_via_cells(board, grid, t):
                stub = t
                break
    if stub is None:
        print("1 ENDPOINT_VIAS: no VBAT_ADC stub with via found – skipped")
        return True
    item = {"uuid": stub.m_Uuid.AsString()}
    cells, _ = rf.end_cells(board, grid, item)
    layers_on = {L for L, _ in cells}
    rf.ENDPOINT_VIAS = False
    cells_off, _ = rf.end_cells(board, grid, item)
    rf.ENDPOINT_VIAS = True
    ok = layers_on == set(rf.SIGNAL_LAYERS) and {L for L, _ in cells_off} == {pcbnew.F_Cu}
    print(f"1 ENDPOINT_VIAS: layers with option {sorted(pcbnew.BOARD.GetStandardLayerName(L) for L in layers_on)}, "
          f"without {sorted(pcbnew.BOARD.GetStandardLayerName(L) for L, _ in cells_off)} → {'ok' if ok else 'ERROR'}")
    return ok


def check_via_under_bodies(board, obstacles):
    g = obstacles.grid
    net = board.FindNet("/GND")
    _, via = obstacles.masks(net, rf.W_MIN / 2)
    ok_cells = ~via
    fp = board.FindFootprintByReference("U6")
    good = True
    if fp is not None:
        box = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
        sel = g._sel(*(pcbnew.ToMM(v) for v in (box.GetLeft(), box.GetTop(), box.GetRight(), box.GetBottom())))
        n_under = int(ok_cells[sel].sum())
        print(f"2 VIA_UNDER_BODIES: {n_under} allowed via grid points in the courtyard of U6 (bottom)")
        good &= n_under > 0
    bad = 0
    for pad in board.GetPads():
        if pad.GetDrillSize().x > 0 or pad.GetNetCode() == net.GetNetCode():
            continue
        c = g.cell(pad.GetPosition())
        if 0 <= c[0] < g.ny and 0 <= c[1] < g.nx and ok_cells[c]:
            bad += 1
    for z in board.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias() and z.GetZoneName().startswith(("Antenna", "Antenne")):  # "Antenne": name before 2026-11-08
            bb = z.GetBoundingBox()
            sel = g._sel(*(pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())))
            inner = ok_cells[sel][2:-2, 2:-2]
            bad += int(inner.sum())
    print(f"2 via-in-pad (foreign SMD pads) and antenna: {bad} allowed spots → {'ok' if bad == 0 else 'ERROR'}")
    return good and bad == 0


def check_oval_drills(board, spot=(10.47, 4.53)):
    """5 through-hole pads: at the spot where in round M a VBUS via was too close to the J4 tab S1 (DRC rule
    "component hole to copper" 0.275 instead of 0.28 mm, measured between via hole and tab copper), no via center
    may lie now. The capsule for the slotted hole (OVAL_DRILLS) alone is not enough for this; the error was the
    clearance via hole – pad copper (0.25 instead of 0.28/0.30 mm)."""
    net = board.FindNet("/SDA")
    res = {}
    for flag in (False, True):
        rf.OVAL_DRILLS = flag
        obstacles = rf.Obstacles(board)
        _, via = obstacles.masks(net, rf.W_MIN / 2)
        c = obstacles.grid.cell(pcbnew.VECTOR2I(pcbnew.FromMM(100 + spot[0]), pcbnew.FromMM(75 + spot[1])))
        res[flag] = bool(via[c])
    rf.OVAL_DRILLS = True
    ok = res[True]
    print(f"5 through-hole pad clearance: via at {spot} blocked: circle {res[False]}, capsule {res[True]} → {'ok' if ok else 'ERROR'}")
    return ok


def check_fanout(unrouted):
    """6 GND_FANOUT_FIRST: fanout on the unrouted board; afterwards the DRC may report no errors except unconnected
    items (clearances, via-in-pad, antenna)."""
    work = Path(unrouted).with_name("fanout.kicad_pcb")
    shutil.copy(unrouted, work)
    for suf in (".kicad_pro", ".kicad_dru"):
        shutil.copy(Path(unrouted).with_suffix(suf), work.with_suffix(suf))
    done, failed = rf.gnd_fanout(work, log=lambda m: None)
    import route_score
    drc = route_score.run_drc(work)
    errors = [v for v in drc["violations"] if v["severity"] == "error" and v["type"] not in route_score.LIB_CHECKS]
    ok = not errors
    print(f"6 GND_FANOUT_FIRST: {done} vias placed, without space {len(failed)} ({', '.join(failed)}); "
          f"DRC errors {len(errors)} {sorted({v['type'] for v in errors})} → {'ok' if ok else 'ERROR'}")
    return ok


def replay_open(pcb):
    board = pcbnew.LoadBoard(str(pcb))
    open_items = [u for u in rf.drc_unconnected(pcb)
                  if not any("[/GND]" in i["description"] or "Zone" in i["description"] for i in u["items"])]
    # rip-up-able: everything the router placed (not in the unrouted start board), except GND
    start = pcbnew.LoadBoard(str(START)) if START.exists() else None

    def key(t):
        return (t.GetNetname(), t.GetLayer(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)
    pre = {key(t) for t in start.GetTracks()} if start else set()
    for rip in (False, True):
        b = pcbnew.LoadBoard(str(pcb))
        rippable = {t.m_Uuid.AsString(): t.GetNetname() for t in b.GetTracks()
                    if rip and key(t) not in pre and t.GetNetname() != "/GND"}
        n_ok = 0
        for u in open_items:
            obstacles = rf.Obstacles(b)
            res = rf.connect(b, obstacles, *u["items"], rippable=rippable)
            desc = " | ".join(i["description"] for i in u["items"])
            print(f"3 {'routed' if res else 'no path'}{' (rip-up allowed)' if rip else ''}: {desc}"
                  + (f" ({res[0]}" + (f", ripped up {', '.join(sorted(res[1]))}" if res[1] else "") + ")" if res else ""))
            n_ok += bool(res)
        print(f"3 open signal connections: {n_ok} of {len(open_items)} routed"
              f"{' with rip-up' if rip else ' without rip-up'}")


def replay_islands(pcb):
    start = pcbnew.LoadBoard(str(START)) if START.exists() else None

    def key(t):
        return (t.GetNetname(), t.GetLayer(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)
    pre = {key(t) for t in start.GetTracks()} if start else set()
    for flag, rip in ((False, False), (True, False), (True, True)):
        board = pcbnew.LoadBoard(str(pcb))
        rf.ISLAND_AREA_SEARCH = flag
        rippable = {t.m_Uuid.AsString(): t.GetNetname() for t in board.GetTracks()
                    if rip and key(t) not in pre and t.GetNetname() != "/GND"}
        tasks = rf.island_tasks(board)
        n_ok = 0
        for task in tasks:
            obstacles = rf.Obstacles(board)
            for ref, num in task:
                pad = next(p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber() == num)
                if rf.connect_gnd(board, obstacles, pad, rippable=rippable, exclude=set(task)):
                    n_ok += 1
                    break
        print(f"4 GND islands {'with' if flag else 'without'} area search{', with rip-up' if rip else ''}: "
              f"{n_ok} of {len(tasks)} connected ({'; '.join(','.join('.'.join(r) for r in t) for t in tasks)})")
    rf.ISLAND_AREA_SEARCH = True


def main(pcb=OFFICIAL):
    pcb = Path(pcb)
    with tempfile.TemporaryDirectory() as tmp:
        work = copy_board(pcb, tmp)
        board = pcbnew.LoadBoard(str(work))
        obstacles = rf.Obstacles(board)
        ok = check_endpoint_vias(board, obstacles.grid)
        # via spots under components: on the unrouted board (when routed, everything around U6 is often occupied)
        import route_gate
        unrouted = route_gate.preroute_board("main-board", Path(tmp) / "unrouted")
        ub = pcbnew.LoadBoard(str(unrouted))
        ok &= check_via_under_bodies(ub, rf.Obstacles(ub))
        ok &= check_oval_drills(ub)
        ok &= check_fanout(unrouted)
        replay_open(work)
        replay_islands(copy_board(pcb, Path(tmp)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
