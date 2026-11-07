#!/usr/bin/env python3
"""Schnellprüfung der route_fix.py-Erweiterungen (2026-11-06), ohne stundenlangen Routing-Lauf.

Arbeitet auf einer Kopie der offiziellen Platine (Datei bleibt unverändert) und prüft:
1. ENDPOINT_VIAS: end_cells() liefert für ein Bahnstück, das an einem Via endet (VBAT_ADC-Stich an R6), Startzellen
   auf allen Signallagen; ohne die Option nur auf der Lage der Bahn.
2. VIA_UNDER_BODIES: Unter einem Bauteil unten (U6) gibt es auf der ungerouteten Platine zwischen den Pads
   zulässige Via-Stellen; in keinem fremden SMD-Pad und in keiner Antennen-Sperrfläche liegt eine.
3. Wiederholung der offenen Verbindungen: jede offene Signalverbindung der Platine einmal mit connect() versuchen,
   ohne und mit Aufreißen der Router-Bahnen, und das Ergebnis melden.
4. ISLAND_AREA_SEARCH: jede GND-Insel ohne Via einmal mit connect_gnd() anbinden, mit und ohne Flächensuche.

Aufruf: test_route_fix.py [platine.kicad_pcb]   (just route-check); Rückgabe 1, wenn Prüfung 1 oder 2 scheitert.
Muss mit dem System-Python laufen, das pcbnew enthält.
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
START = ROOT / "build" / "main-board" / "route" / "start.kicad_pcb"  # ungeroutete Platine des letzten Laufs


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
        print("1 ENDPOINT_VIAS: kein VBAT_ADC-Stich mit Via gefunden – übersprungen")
        return True
    item = {"uuid": stub.m_Uuid.AsString()}
    cells, _ = rf.end_cells(board, grid, item)
    layers_on = {L for L, _ in cells}
    rf.ENDPOINT_VIAS = False
    cells_off, _ = rf.end_cells(board, grid, item)
    rf.ENDPOINT_VIAS = True
    ok = layers_on == set(rf.SIGNAL_LAYERS) and {L for L, _ in cells_off} == {pcbnew.F_Cu}
    print(f"1 ENDPOINT_VIAS: Lagen mit Option {sorted(pcbnew.BOARD.GetStandardLayerName(L) for L in layers_on)}, "
          f"ohne {sorted(pcbnew.BOARD.GetStandardLayerName(L) for L, _ in cells_off)} → {'ok' if ok else 'FEHLER'}")
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
        print(f"2 VIA_UNDER_BODIES: {n_under} zulässige Via-Rasterpunkte im Courtyard von U6 (unten)")
        good &= n_under > 0
    bad = 0
    for pad in board.GetPads():
        if pad.GetDrillSize().x > 0 or pad.GetNetCode() == net.GetNetCode():
            continue
        c = g.cell(pad.GetPosition())
        if 0 <= c[0] < g.ny and 0 <= c[1] < g.nx and ok_cells[c]:
            bad += 1
    for z in board.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias() and z.GetZoneName().startswith("Antenne"):
            bb = z.GetBoundingBox()
            sel = g._sel(*(pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())))
            inner = ok_cells[sel][2:-2, 2:-2]
            bad += int(inner.sum())
    print(f"2 Via-in-Pad (fremde SMD-Pads) und Antenne: {bad} zulässige Stellen → {'ok' if bad == 0 else 'FEHLER'}")
    return good and bad == 0


def replay_open(pcb):
    board = pcbnew.LoadBoard(str(pcb))
    open_items = [u for u in rf.drc_unconnected(pcb)
                  if not any("[/GND]" in i["description"] or "Zone" in i["description"] for i in u["items"])]
    # aufreißbar: alles, was der Router gelegt hat (nicht in der ungerouteten Startplatine), außer GND
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
            print(f"3 {'geroutet' if res else 'kein Weg'}{' (Aufreißen erlaubt)' if rip else ''}: {desc}"
                  + (f" ({res[0]}" + (f", aufgerissen {', '.join(sorted(res[1]))}" if res[1] else "") + ")" if res else ""))
            n_ok += bool(res)
        print(f"3 offene Signalverbindungen: {n_ok} von {len(open_items)} geroutet"
              f"{' mit Aufreißen' if rip else ' ohne Aufreißen'}")


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
        print(f"4 GND-Inseln {'mit' if flag else 'ohne'} Flächensuche{', mit Aufreißen' if rip else ''}: "
              f"{n_ok} von {len(tasks)} angebunden ({'; '.join(','.join('.'.join(r) for r in t) for t in tasks)})")
    rf.ISLAND_AREA_SEARCH = True


def main(pcb=OFFICIAL):
    pcb = Path(pcb)
    with tempfile.TemporaryDirectory() as tmp:
        work = copy_board(pcb, tmp)
        board = pcbnew.LoadBoard(str(work))
        obstacles = rf.Obstacles(board)
        ok = check_endpoint_vias(board, obstacles.grid)
        # Via-Stellen unter Bauteilen: auf der ungerouteten Platine (geroutet ist um U6 oft alles belegt)
        import route_gate
        unrouted = route_gate.preroute_board("main-board", Path(tmp) / "unrouted")
        ub = pcbnew.LoadBoard(str(unrouted))
        ok &= check_via_under_bodies(ub, rf.Obstacles(ub))
        replay_open(work)
        replay_islands(copy_board(pcb, Path(tmp)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
