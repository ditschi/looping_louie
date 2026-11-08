#!/usr/bin/env python3
"""Finishing pass on a routed main board: close open connections and GND islands with route_fix.py, where all
tracks of the router (not the pre-routes from `just pcb`) may be ripped up; then stitching as in route.py.

Usage: route_finish.py <routed.kicad_pcb> <unrouted.kicad_pcb> <target.kicad_pcb> [max_steps]
Afterwards the result goes through the gate like any run (route_gate.py check main-board <target> --start <unrouted>
--apply). Must run with the system Python that contains pcbnew.
"""
import shutil
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
ARGS = sys.argv[1:]
sys.argv = sys.argv[:1] + ["main-board"]  # route.py reads the board from argv on import
import route  # noqa: E402
import route_fix  # noqa: E402
from stitch import stitch, stitch_grid  # noqa: E402


def key(t):
    return (t.GetNetname(), t.GetLayer(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)


def main(routed, unrouted, target, max_rounds=200):
    routed, target = Path(routed), Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(routed, target)
    for suf in (".kicad_pro", ".kicad_dru"):
        if routed.with_suffix(suf).exists():
            shutil.copy(routed.with_suffix(suf), target.with_suffix(suf))
    pre = {key(t) for t in pcbnew.LoadBoard(str(unrouted)).GetTracks()}
    board = pcbnew.LoadBoard(str(target))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(target), board)
    rip = {t.m_Uuid.AsString(): t.GetNetname() for t in board.GetTracks()
           if key(t) not in pre and t.GetNetname() not in route_fix.SKIP_NETS}
    done, still = route_fix.fix(target, max_rounds=int(max_rounds), gnd=True, rip_tracks=rip,
                                log=lambda m: print(m, flush=True))
    print(f"route_fix: {done} routed, {still} open")
    for _ in range(2):
        d, _f = stitch(target, ["/GND"])
        if not d:
            break
    stitch_grid(target)
    print(f"GND islands: {route_fix.gnd_islands(target, log=lambda m: None)}")
    stitch_grid(target)
    if route_fix.ISLAND_AREA_SEARCH:
        print(f"vias in unconnected fill fragments: {route_fix.fragment_vias(target, log=print)}")
    print(f"dangling vias/tracks removed: {route.remove_dangling_vias(target)}")
    board = pcbnew.LoadBoard(str(target))  # refill zones at the end (DRC checks the stored fill)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(target), board)


if __name__ == "__main__":
    main(*ARGS)
