#!/usr/bin/env python3
"""Route a board (default: main board) automatically and fill the ground zones afterwards.

Main board (4 layers): own router route_fix.py (default) or Freerouting. Charger board (2 layers):
Freerouting – flow: export Specctra DSN → Freerouting (Java) → import SES → fill zones.
Freerouting JAR: environment variable FREEROUTING_JAR or tools/freerouting.jar (see setup.sh).

Usage (via just):  just route [main-board|charger-board] [runs=N] [force=1] [pre=none,krt,krt-novip]
  (direct: route.py <board> [--runs N] [--force] [--pre LIST]; runs = number of attempts, default 6)

Pre-routers (main board only, own router; pre=…, environment variable ROUTE_PRE): starting states distributed
round-robin over the attempts. none = empty board (default); krt = KiCadRoutingTools (tools/krt, setup.sh) pre-routes
the signals, route_fix.py takes over its tracks as rip-up-able and routes the rest; krt-novip = the same without vias
in pads of the same net. KRT is deterministic and runs once per variant per invocation (about 1–2 min).
Example: pre=none,krt,krt-novip runs=18 → attempt 1 empty, 2 krt, 3 krt-novip, 4 empty, …; each start type gets
the cost variants in turn and then the seeds.

Keep-best gate (route_gate.py, docs/development.md): the best attempt of an invocation replaces the official
board only if it is better for the same design than the result in hardware/<board>/routing.json, if the design
has changed, or with force=1. Otherwise it ends up under build/<board>/route/rejected/.

Environment variables: ROUTE_RUNS (old: FREEROUTING_ATTEMPTS), ROUTE_PARALLEL (old: FREEROUTING_PARALLEL),
FREEROUTING_PASSES, FREEROUTING_JAR, ROUTE_VARIANTS, ROUTE_PLANE, ROUTE_GND, ROUTER (main board only).

Main board, 4 layers (main-board, docs/main-board-c6.md chapter 11):
- ROUTER=own (default; deprecated: ROUTER=eigen): maze router route_fix.py for all signals on F.Cu/In2.Cu/B.Cu, GND
  through layer In1 (stitching vias at the GND pads). The attempts differ in via and layer costs
  (ROUTER_VARIANTS); identical variants also scatter somewhat (ordering, see route_fix.py). From attempt 7 on the
  variants come again with seed 1, 2, … (route_fix.SEED: own ordering per seed). ROUTE_VARIANTS="3,4" selects
  individual attempts. For each attempt route_fix.py writes a trace (attempt_N/route_fix.trace.csv: time and open
  connections per round).
- ROUTER=freerouting: Freerouting as for the charger board, then route_fix.py for the remaining open connections.
  The GND layer In1 goes into the DSN file as a plane (ROUTE_PLANE=1, Freerouting connects GND with vias) or not
  (ROUTE_PLANE=0, GND only through stitching vias).
Must run with the system Python that contains the KiCad module pcbnew.
"""
import json
import os
import re
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from stitch import stitch, stitch_grid  # noqa: E402
import route_gate  # noqa: E402


def parse_args(argv):
    """board, attempts, force, pre-routers from "main-board runs=10 force=1 pre=none,krt" or "main-board --runs 10
    --force --pre none,krt"."""
    board, runs, force, pre = "main-board", None, False, None
    args = list(argv)
    while args:
        a = args.pop(0)
        key, _, value = a.lstrip("-").partition("=")
        if key in ("runs", "attempts"):
            runs = int(value or args.pop(0))
        elif key == "force":
            force = value.lower() not in ("0", "no", "false") if value else True
        elif key == "pre":
            pre = [x.strip() for x in (value or args.pop(0)).split(",") if x.strip()]
        elif not a.startswith("-") and "=" not in a:
            board = a
        else:
            sys.exit(f"Unknown option: {a} (allowed: runs=N, force=1, pre=none,krt,krt-novip)")
    return board, runs, force, pre


def env(name, old, default):
    """The English name takes precedence, the old one stays as an alias."""
    return os.environ.get(name, os.environ.get(old, default))


ROOT = Path(__file__).resolve().parent.parent.parent
BOARDS = {"main-board": "louie-main", "charger-board": "louie-charger"}
# also in the worker processes (forkserver re-imports the module, sys.argv is preserved)
BOARD, RUNS, FORCE, PRE = parse_args(sys.argv[1:])
PCB = ROOT / "hardware" / BOARD / f"{BOARDS[BOARD]}.kicad_pcb"
WORK = ROOT / "build" / BOARD / "route"
JAR = Path(os.environ.get("FREEROUTING_JAR", ROOT / "tools" / "freerouting.jar"))
PASSES = os.environ.get("FREEROUTING_PASSES", "40")
ATTEMPTS = RUNS or int(env("ROUTE_RUNS", "FREEROUTING_ATTEMPTS", "6"))
# concurrent attempts: one core and about 450 MB per attempt (own router); measurement see docs/development.md
PARALLEL = int(env("ROUTE_PARALLEL", "FREEROUTING_PARALLEL", "4"))
# Freerouting is deterministic and stops as soon as the result no longer improves; the number of passes
# therefore changes little. Different track widths (default / Supply), on the other hand, give clearly
# different results. Minimum width and clearances stay unchanged.
PASS_VARIANTS = [40, 25, 60, 15, 100, 30]
WIDTH_VARIANTS = [(0.17, 0.2), (0.2, 0.25), (0.15, 0.2), (0.18, 0.2), (0.2, 0.2), (0.16, 0.25),
                  (0.17, 0.25), (0.18, 0.25), (0.19, 0.2)]


# Nets that run entirely through copper zones and should not be routed by Freerouting.
# Charger board: GND is routed too, because otherwise the bridge on the bottom and the power tracks split the
# zones into islands (individual GND pads then stay unconnected).
FOUR_LAYER = BOARD == "main-board"  # main board: 4 layers, GND layer In1
# 4 layers: pass the GND plane In1 to Freerouting (default), GND is then routed too (vias to the plane)
PLANE_EXPORT = FOUR_LAYER and os.environ.get("ROUTE_PLANE", "1") == "1"
PLANE_NETS = [] if BOARD == "charger-board" or os.environ.get("ROUTE_GND") or PLANE_EXPORT else ["/GND"]
STITCH_NETS = ["/GND"] if FOUR_LAYER else PLANE_NETS
ROUTER = os.environ.get("ROUTER", "own") if FOUR_LAYER else "freerouting"
if ROUTER == "eigen":  # deprecated name
    if __name__ == "__main__":
        print("Note: ROUTER=eigen is deprecated, please use ROUTER=own", file=sys.stderr)
    ROUTER = "own"
# variants of the own router: (via cost in grid steps, cost factor F.Cu, cost factor B.Cu)
ROUTER_VARIANTS = [(30, 1.3, 1.15), (20, 1.3, 1.15), (40, 1.3, 1.15), (30, 1.6, 1.3), (25, 1.1, 1.0), (35, 1.5, 1.1)]
# Pre-routers (pre=…): starting states of the own router. KiCadRoutingTools (MIT,
# github.com/drandyhaas/KiCadRoutingTools, version in setup.sh) reads and writes .kicad_pcb directly; all signals
# except GND on F.Cu/In2.Cu/B.Cu, without touching the project DRC limits (--no-fix-drc-settings) and without going
# below the board minimums (--escalation board). Spike 2026-11-07 (docs/development.md): 2 and 6 open respectively, 0 DRC errors, about 1–2 min.
PRE = PRE or [x for x in os.environ.get("ROUTE_PRE", "none").split(",") if x]
KRT_DIR = ROOT / "tools" / "krt"
KRT_PYTHON = ROOT / "tools" / "krt-venv" / "bin" / "python"
PREROUTERS = {"none": None, "krt": [], "krt-novip": ["--same-net-pad-clearance", "0.1"]}
for _p in PRE:
    if _p not in PREROUTERS:
        sys.exit(f"Unknown pre-router: {_p} (allowed: {', '.join(PREROUTERS)})")


def drop_nets(dsn, nets):
    """Remove nets from the network section of the DSN file (Freerouting then ignores them)."""
    sys.path.insert(0, str(Path(__file__).parent))
    from sexpr import block_end
    text = dsn.read_text()
    for net in nets:
        start = text.find(f"(net {net}\n")
        if start < 0:
            start = text.find(f"(net {net} ")
        if start >= 0:
            text = text[:start] + text[block_end(text, start):]
        text = text.replace(f" {net}\n", "\n").replace(f" {net} ", " ").replace(f" {net})", ")")
    dsn.write_text(text)


def plane_layer_off(dsn):
    """4 layers: the keepout area "GND layer" (wire_keepout) would block Freerouting for vias as well and is
    therefore removed from the DSN (in KiCad it stays for the DRC). In1 stays free because the GND zone is in the
    DSN as a plane (PLANE_EXPORT). Formerly "(autoroute_settings (layer_rule In1.Cu (active off)))" was added here
    as well; with it Freerouting 2.5 reads an empty board, reports "0 unrouted" and writes an empty SES (spike
    2026-11-07)."""
    sys.path.insert(0, str(Path(__file__).parent))
    from sexpr import block_end
    text = dsn.read_text()
    while (start := text.find("(wire_keepout")) >= 0:
        line = text.rfind("\n", 0, start) + 1
        text = text[:line] + text[block_end(text, start):].lstrip(" ").lstrip("\n")
    dsn.write_text(text)


def freerouting_round(dsn, ses, keep_tracks, passes=None, pcb=None, work=None):
    """One Freerouting round. keep_tracks=False: remove all unlocked tracks first."""
    PCB, WORK = pcb or globals()["PCB"], work or globals()["WORK"]
    board = pcbnew.LoadBoard(str(PCB))
    if not keep_tracks:
        for track in list(board.GetTracks()):
            if not track.IsLocked():
                board.Delete(track)
        pcbnew.SaveBoard(str(PCB), board)

    # Export for Freerouting without copper zones: otherwise the filled zones count as occupied
    # copper and block routing. The zones are filled after the import.
    export = pcbnew.LoadBoard(str(PCB))
    for zone in list(export.Zones()):
        if not zone.GetIsRuleArea() and not (PLANE_EXPORT and zone.GetLayer() == pcbnew.In1_Cu):
            export.Delete(zone)
    if not pcbnew.ExportSpecctraDSN(export, str(dsn)):
        sys.exit("DSN export failed")
    drop_nets(dsn, PLANE_NETS)
    if FOUR_LAYER:
        if not PLANE_EXPORT:
            sys.exit("ROUTE_PLANE=0 no longer works with Freerouting 2.5: without a GND plane in the DSN "
                     "Freerouting would put signals on In1 (disabling it via layer_rule empties the board)")
        plane_layer_off(dsn)

    result = subprocess.run(["java", "-jar", str(JAR), "-de", str(dsn), "-do", str(ses), "-mp", str(passes or PASSES),
                             "--gui.enabled=false", "--router.automatic_neckdown=false"], capture_output=True, text=True)
    log = result.stdout + result.stderr
    (WORK / "freerouting.log").write_text(log)
    m = re.findall(r"final score: [\d.]+ \((\d+) unrouted", log)
    unrouted = int(m[-1]) if m else -1
    # empty board read (DSN unreadable): "baseline … for 0 unrouted items" and no track in the SES
    start_open = re.findall(r"baseline score [\d.]+ for (\d+) unrouted", log)
    if start_open and int(start_open[0]) == 0 and ses.exists() and "(wire" not in ses.read_text():
        raise RuntimeError(f"Freerouting read no open connections and routed nothing – check the DSN "
                           f"({WORK / 'freerouting.log'})")

    board = pcbnew.LoadBoard(str(PCB))
    if not pcbnew.ImportSpecctraSES(board, str(ses)):
        sys.exit("SES import failed")
    # Freerouting necks down tracks at small pads; nothing below the minimum width of the design rules
    min_w = board.GetDesignSettings().m_TrackMinWidth
    for track in board.GetTracks():
        if track.GetClass() == "PCB_TRACK" and track.GetWidth() < min_w:
            track.SetWidth(min_w)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(PCB), board)
    return unrouted


def remove_dangling_vias(PCB=PCB):
    """Remove vias and track pieces that Freerouting left without a connection (DRC: via_dangling,
    track_dangling); repeatedly, because new dangling ends can appear afterwards."""
    removed = 0
    for _ in range(4):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "drc.json"
            subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(PCB)],
                           capture_output=True)
            data = json.loads(report.read_text())
        spots = {v["type"]: [] for v in data.get("violations", [])}
        for v in data.get("violations", []):
            if v["type"] in ("via_dangling", "track_dangling"):
                spots[v["type"]] += [(item["pos"]["x"], item["pos"]["y"]) for item in v["items"]]
        if not spots.get("via_dangling") and not spots.get("track_dangling"):
            break
        board = pcbnew.LoadBoard(str(PCB))
        n = 0
        for t in [t for t in board.GetTracks() if not t.IsLocked()]:
            kind = "via_dangling" if t.GetClass() == "PCB_VIA" else "track_dangling"
            ends = [t.GetPosition()] if kind == "via_dangling" else [t.GetStart(), t.GetEnd()]
            if any(abs(pcbnew.ToMM(e.x) - sx) < 0.01 and abs(pcbnew.ToMM(e.y) - sy) < 0.01
                   for e in ends for sx, sy in spots.get(kind, [])):
                board.Delete(t)
                n += 1
        if not n:
            break
        removed += n
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        pcbnew.SaveBoard(str(PCB), board)
    return removed


def krt_preroute(start, project, name):
    """Pre-router KiCadRoutingTools on the unrouted board; returns the routed board (WORK/pre_<name>).
    The KRT tracks stay unlocked, so route_fix.py may rip them up."""
    import time
    if not (KRT_DIR / "py_router" / "route.py").exists() or not KRT_PYTHON.exists():
        sys.exit(f"KiCadRoutingTools not found ({KRT_DIR}, {KRT_PYTHON})\n→ run ./setup.sh")
    work = WORK / f"pre_{name}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    src, out = work / PCB.name, work / f"routed{PCB.suffix}"
    shutil.copy(start, src)
    for f in (project, project.with_suffix(".kicad_dru")):
        if f.exists():
            shutil.copy(f, work / f.name)
    board = pcbnew.LoadBoard(str(src))  # like attempt_own: only pre-routes (locked) remain
    for track in list(board.GetTracks()):
        if not track.IsLocked():
            board.Delete(track)
    pcbnew.SaveBoard(str(src), board)
    import route_fix
    if route_fix.GND_FANOUT_FIRST:  # GND vias before KRT, else KRT takes the space (test: 31 pads without via)
        done, failed = route_fix.gnd_fanout(src, log=lambda m: None)
        print(f"Pre-router {name}: GND fanout beforehand {done} vias, no space {len(failed)}", flush=True)
    cmd = [str(KRT_PYTHON), str(KRT_DIR / "py_router" / "route.py"), src.name, out.name, "--nets", "*",
           *[f"!{n}" for n in STITCH_NETS], "--layers", "F.Cu", "In2.Cu", "B.Cu", "--no-fix-drc-settings",
           "--escalation", "board", *PREROUTERS[name]]
    t0 = time.time()
    with open(work / "krt.log", "w") as log:
        result = subprocess.run(cmd, cwd=work, stdout=log, stderr=subprocess.STDOUT, timeout=1800)
    if result.returncode != 0 or not out.exists():
        sys.exit(f"Pre-router {name} failed (exit code {result.returncode}), see {work / 'krt.log'}")
    print(f"Pre-router {name}: {time.time() - t0:.0f} s → {out}", flush=True)
    return out


def plan(n):
    """Attempt n → (start type, cost variant, seed): start types round-robin, for each start type first the cost
    variants, then the seeds. Without pre-router (pre=none) as before: attempts 1–6 variants with seed 0, 7–12 with
    seed 1, …"""
    pre = PRE[(n - 1) % len(PRE)]
    m = (n - 1) // len(PRE)
    return pre, m % len(ROUTER_VARIANTS), m // len(ROUTER_VARIANTS)


def attempt(n, start, project):
    """One routing attempt in its own directory (runs in parallel with others). start: starting board (with a
    pre-router its result)."""
    work = WORK / f"attempt_{n}"
    work.mkdir(parents=True, exist_ok=True)
    pcb = work / PCB.name
    shutil.copy(start, pcb)
    for f in (project, project.with_suffix(".kicad_dru")):
        if f.exists():
            shutil.copy(f, work / f.name)
    if ROUTER == "own":
        return attempt_own(n, pcb)
    passes = PASS_VARIANTS[(n - 1) % len(PASS_VARIANTS)]
    track, supply = WIDTH_VARIANTS[(n - 1) % len(WIDTH_VARIANTS)]
    if BOARD == "main-board":
        board = pcbnew.LoadBoard(str(pcb))
        ns = board.GetDesignSettings().m_NetSettings
        ns.GetDefaultNetclass().SetTrackWidth(pcbnew.FromMM(track))
        if ns.HasNetclass("Supply"):
            ns.GetNetClassByName("Supply").SetTrackWidth(pcbnew.FromMM(supply))
        pcbnew.SaveBoard(str(pcb), board)
    dsn, ses = work / f"{BOARDS[BOARD]}.dsn", work / f"{BOARDS[BOARD]}.ses"
    unrouted = freerouting_round(dsn, ses, keep_tracks=False, passes=passes, pcb=pcb, work=work)
    if FOUR_LAYER:  # remaining connections with the own router
        import route_fix
        with open(work / "route_fix.log", "w") as log:
            route_fix.fix(pcb, log=lambda m: print(m, file=log, flush=True))
    for _ in range(2 if STITCH_NETS else 0):  # connect GND pads without zone contact with a via
        done, _failed = stitch(pcb, STITCH_NETS)
        if not done:
            break
    grid = stitch_grid(pcb)  # connect GND zones top/bottom on a grid
    removed = remove_dangling_vias(pcb)
    label = f"{passes} passes, track {track}/{supply} mm" if BOARD == "main-board" else f"{passes} passes"
    return n, label, unrouted, route_gate.measure(pcb, board=BOARD), grid, removed, pcb


def attempt_own(n, pcb):
    """4 layers: all signals with the own router (route_fix.py), then GND stitching."""
    import route_fix
    pre, variant, seed = plan(n)
    via_cost, f_cost, b_cost = ROUTER_VARIANTS[variant]
    route_fix.SEED = seed
    route_fix.VIA_COST = via_cost
    route_fix.LAYER_COST[pcbnew.F_Cu] = f_cost
    route_fix.LAYER_COST[pcbnew.B_Cu] = b_cost
    if pre == "none":  # otherwise keep the pre-router tracks (unlocked, so rip-up-able)
        board = pcbnew.LoadBoard(str(pcb))
        for track in list(board.GetTracks()):
            if not track.IsLocked():
                board.Delete(track)
        pcbnew.SaveBoard(str(pcb), board)
    (pcb.parent / "route_fix.trace.csv").unlink(missing_ok=True)
    with open(pcb.parent / "route_fix.log", "w") as log:
        out = lambda m: print(m, file=log, flush=True)  # noqa: E731
        done, still_open = route_fix.route_all(pcb, log=out, trace=pcb.parent / "route_fix.trace.csv")
        for _ in range(2):  # GND pads without zone contact to the GND layer In1 with a via
            stitched, _failed = stitch(pcb, STITCH_NETS)
            if not stitched:
                break
        grid = stitch_grid(pcb)
        out(f"GND islands connected: {route_fix.gnd_islands(pcb, log=out)}")
        grid += stitch_grid(pcb)
    removed = remove_dangling_vias(pcb)
    label = (f"own router, via cost {via_cost}, F {f_cost}, B {b_cost}" + (f", seed {seed}" if seed else "")
             + (f", pre-router {pre}" if pre != "none" else ""))
    return n, label, still_open, route_gate.measure(pcb, board=BOARD), grid, removed, pcb


def main():
    if ROUTER != "own" and not JAR.exists():
        sys.exit(f"Freerouting not found: {JAR}\n→ run ./setup.sh or set FREEROUTING_JAR")
    WORK.mkdir(parents=True, exist_ok=True)
    start = WORK / "start.kicad_pcb"
    best_file = WORK / "best.kicad_pcb"
    shutil.copy(PCB, start)
    project = PCB.with_suffix(".kicad_pro")
    # fingerprint of the design at the start (before routing), see route_gate.py
    fingerprint, why = route_gate.run_fingerprint(start, route_gate.load_record(BOARD), project)
    print(f"Design fingerprint {fingerprint[:12]} ({why})", flush=True)

    from concurrent.futures import ProcessPoolExecutor
    import route_score
    cfg = route_score.load_config(BOARD)
    best, results = None, []
    with ProcessPoolExecutor(max_workers=PARALLEL) as pool:
        # ROUTE_VARIANTS="3,4": only these attempts (repetition/scatter), otherwise 1..runs
        numbers = [int(x) for x in os.environ["ROUTE_VARIANTS"].split(",")] if os.environ.get("ROUTE_VARIANTS") \
            else list(range(1, ATTEMPTS + 1))
        # pre-routers: once beforehand per start type used (deterministic), attempts start from its result
        starts = {"none": start}
        if ROUTER == "own":
            for name in sorted({plan(n)[0] for n in numbers} - {"none"}):
                starts[name] = krt_preroute(start, project, name)
        elif PRE != ["none"]:
            sys.exit("pre=… is only available with the own router (ROUTER=own)")
        for n, label, unrouted, meas, grid, removed, pcb in pool.map(
                attempt, numbers, [starts[plan(n)[0]] if ROUTER == "own" else start for n in numbers],
                [project] * len(numbers)):
            first = "Router" if ROUTER == "own" else "Freerouting"
            extra = f", {removed} dangling vias/track pieces removed" if removed else ""
            print(f"Attempt {n} ({label}): {first} {unrouted} open → after stitching "
                  f"{route_gate.short(meas['metrics'], cfg, meas['details'])}, {grid} stitching vias{extra}", flush=True)
            # best attempt: first feasible, then smallest violation, then smallest score S (route_score.rank_key)
            key = route_score.rank_key(cfg, meas["metrics"], meas["details"])
            results.append((f"attempt {n}", meas))
            if best is None or key < best[0]:
                best = (key, n, label, meas)
                shutil.copy(pcb, best_file)
    for line in route_score.table(cfg, sorted(results, key=lambda r: route_score.rank_key(cfg, r[1]["metrics"],
                                                                                         r[1]["details"]))):
        print(line)
    for line in route_score.pareto(cfg, results):
        print(line)
    print(f"best attempt of this invocation: {best[1]} ({best[2]})")
    info = {"router": ROUTER, "variant": f"attempt {best[1]}: {best[2]}", "runs": len(numbers)}
    route_gate.gate(BOARD, best_file, fingerprint, best[3], info, force=FORCE)
    print(f"next: just drc {BOARD}")


if __name__ == "__main__":
    main()
