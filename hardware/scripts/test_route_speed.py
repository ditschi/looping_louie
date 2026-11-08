#!/usr/bin/env python3
"""Equivalence check of the run-time optimizations in route_fix.py (2026-11-07), without a routing run (about 2 min).

The optimizations must not change the search result (otherwise a long run would no longer be equivalent):
1. open_connections(): connection list from the in-process connectivity against the KiCad DRC (kicad-cli), on the
   board and on states with randomly removed tracks. Required: per net the same count and the same total length of
   the spanning tree (which is unique). On ties, edges may differ: several items at the same anchor point (track
   end on via) or several clusters at the same point (missing via between layers) – which edge KiCad takes then
   depends, in the DRC too, only on the order in the file.
2. Grid cache: masks() with and without cache bit-identical (several nets, widths, soft obstacles).
3. astar(): same path as the former version astar_ref() (copied unchanged below) for each open connection of a
   partly routed state, without and with soft obstacles and history costs, plus cases without a path (pre-check
   _reachable) and with goal_via.

Usage: test_route_speed.py [routed.kicad_pcb]   (just route-check-speed); exit code 1 on any difference.
Default: official board; the unrouted start board comes from build/main-board/route/start.kicad_pcb.
Must run with the system Python that contains pcbnew.
"""
import heapq
import json
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import route_fix as rf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
OFFICIAL = ROOT / "hardware" / "main-board" / "louie-main.kicad_pcb"


def astar_ref(grid, track, via, sources, targets, max_expand=1_000_000, goal_via=False, area_sources=(), area_targets=()):
    """A* over (layer, row, column). sources/targets: list of (layer, cell). Returns a list of (layer, cell).
    goal_via=True: no target, but the nearest spot on the start layer where a via fits
    (connecting a GND pad to the GND layer In1)."""
    layers = rf.SIGNAL_LAYERS
    li = {L: k for k, L in enumerate(layers)}
    blocked = np.stack([track[L] for L in layers])
    k = 1
    for L, c in list(sources) + list(targets):  # free the own terminal points
        blocked[li[L], max(0, c[0] - k):c[0] + k + 1, max(0, c[1] - k):c[1] + k + 1] = False
    # area start points (ISLAND_AREA_SEARCH): only free cells, free nothing
    sources = list(sources) + [(L, c) for L, c in area_sources if not blocked[li[L], c[0], c[1]]]
    via_ok = ~via
    tset = {(li[L], c) for L, c in targets}
    # area targets (ISLAND_AREA_SEARCH: connected GND fill): only free cells, free nothing
    tset |= {(li[L], c) for L, c in area_targets if not blocked[li[L], c[0], c[1]]}
    tl = list({c for _, c in targets})
    ny, nx = grid.ny, grid.nx

    def h(c):
        if goal_via:
            return 0
        return min(max(abs(c[0] - t[0]), abs(c[1] - t[1])) + 0.414 * min(abs(c[0] - t[0]), abs(c[1] - t[1]))
                   for t in tl)

    cost_l = [rf.LAYER_COST[L] for L in layers]
    extra = grid.fcost
    soft = np.stack([grid.soft[L] for L in layers]) if hasattr(grid, "soft") else np.zeros_like(blocked)
    soft_via = grid.soft_via if hasattr(grid, "soft_via") else np.zeros_like(via)
    hist = grid.hist if hasattr(grid, "hist") else np.zeros(blocked.shape)
    best, prev, dirs = {}, {}, {}
    heap = []
    for L, c in sources:
        s = (li[L], c)
        best[s] = 0
        dirs[s] = -1
        heapq.heappush(heap, (h(c), 0, s))
    n_exp = 0
    while heap:
        _, g, s = heapq.heappop(heap)
        if s in tset or (goal_via and via_ok[s[1]] and g > 0):
            path = [s]
            while s in prev:
                s = prev[s]
                path.append(s)
            return [(layers[l], c) for l, c in path[::-1]]
        if g > best.get(s, 1e18):
            continue
        n_exp += 1
        if n_exp > max_expand:
            return None
        l, c = s
        d = dirs[s]
        for kk, (di, dj, cost) in enumerate(rf.STEPS):
            n = (c[0] + di, c[1] + dj)
            if not (0 <= n[0] < ny and 0 <= n[1] < nx) or blocked[l, n[0], n[1]]:
                continue
            ng = g + cost * (extra[n] if l == 0 else cost_l[l]) + (rf.BEND_COST if d not in (-1, kk) else 0) \
                + (rf.RIP_COST if soft[l, n[0], n[1]] else 0) + hist[l, n[0], n[1]]
            ns = (l, n)
            if ng < best.get(ns, 1e18):
                best[ns] = ng
                prev[ns] = s
                dirs[ns] = kk
                heapq.heappush(heap, (ng + h(n), ng, ns))
        if via_ok[c] and not goal_via:
            for l2 in range(len(layers)):
                if l2 == l or blocked[l2, c[0], c[1]]:
                    continue
                ng = g + rf.VIA_COST + (rf.RIP_COST if soft_via[c] or soft[l2, c[0], c[1]] else 0)
                ns = (l2, c)
                if ng < best.get(ns, 1e18):
                    best[ns] = ng
                    prev[ns] = s
                    dirs[ns] = -1
                    heapq.heappush(heap, (ng + h(c), ng, ns))
    return None


def clusters(board):
    """UUID -> (net, cluster number) from the KiCad connectivity."""
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    out, k = {}, 0
    for x in list(board.GetPads()) + list(board.GetTracks()):
        if x.m_Uuid.AsString() in out:
            continue
        out[x.m_Uuid.AsString()] = (x.GetNetname(), k)
        stack = [x]
        while stack:
            y = stack.pop()
            for z in list(conn.GetConnectedTracks(y)) + list(conn.GetConnectedPads(y)):
                if z.m_Uuid.AsString() not in out and z.GetNetCode() == x.GetNetCode():
                    out[z.m_Uuid.AsString()] = (x.GetNetname(), k)
                    stack.append(z)
        k += 1
    return out


def drc_pairs(pcb):
    with tempfile.TemporaryDirectory() as tmp:
        r = Path(tmp) / "d.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(r), str(pcb)], capture_output=True)
        data = json.loads(r.read_text())
    return [[i["uuid"] for i in u["items"]] for u in data["unconnected_items"]
            if not any(f"[{n}]" in i["description"] for n in rf.SKIP_NETS for i in u["items"])
            and "Zone" not in " ".join(i["description"] for i in u["items"])]


def states(pcb, tmp, counts):
    """Board states with randomly removed signal tracks (one state per count)."""
    for k, n in enumerate(counts):
        board = pcbnew.LoadBoard(str(pcb))
        tracks = [t for t in board.GetTracks() if t.GetNetname() not in rf.SKIP_NETS]
        for t in random.Random(k).sample(tracks, min(n, len(tracks))):
            board.Delete(t)
        out = Path(tmp) / f"state_{k}.kicad_pcb"
        pcbnew.SaveBoard(str(out), board)
        yield n, out


def anchors(x):
    return [x.GetStart(), x.GetEnd()] if x.GetClass() in ("PCB_TRACK", "PCB_ARC") else [x.GetPosition()]


def tree_length(board, pairs):
    """Net -> (number of edges, total length in mm); edge length = shortest distance of the anchors of both items."""
    items = {x.m_Uuid.AsString(): x for x in list(board.GetPads()) + list(board.GetTracks())}
    out = {}
    for a, b in pairs:
        xa, xb = items[a], items[b]
        d = min((p - q).EuclideanNorm() for p in anchors(xa) for q in anchors(xb))
        n, total = out.get(xa.GetNetname(), (0, 0.0))
        out[xa.GetNetname()] = (n + 1, total + pcbnew.ToMM(d))
    return out


def check_connections(pcb, tmp):
    ok, total, t_drc, t_own = True, 0, 0.0, 0.0
    for n, state in states(pcb, tmp, [0, 2, 10, 40, 150]):
        t = time.time()
        drc = drc_pairs(state)
        t_drc += time.time() - t
        t = time.time()
        own = [[i["uuid"] for i in u["items"]] for u in rf.open_connections(state)]
        t_own += time.time() - t
        board = pcbnew.LoadBoard(str(state))
        cl = clusters(board)
        tree_d, tree_o = tree_length(board, drc), tree_length(board, own)
        same = tree_d.keys() == tree_o.keys() and all(
            tree_d[k][0] == tree_o[k][0] and abs(tree_d[k][1] - tree_o[k][1]) < 1e-6 for k in tree_d)
        pairs_d = {tuple(sorted(cl[u] for u in p)) for p in drc}
        edges = sum(1 for p in own if tuple(sorted(cl[u] for u in p)) not in pairs_d)
        elems = sum(1 for p in own if sorted(p) not in [sorted(q) for q in drc]) - edges
        total += len(drc)
        print(f"  {n:3d} tracks removed: DRC {len(drc)}, own {len(own)} open, spanning tree per net "
              f"{'equal' if same else 'DIFFERENT'}; on ties other edge {edges}, other item {elems}")
        ok &= same
    print(f"1 open_connections: {total} connections, DRC {t_drc:.1f} s, own {t_own:.2f} s → {'ok' if ok else 'ERROR'}")
    return ok


def check_masks(board):
    obstacles = rf.Obstacles(board)
    nets = sorted({p.GetNetname() for p in board.GetPads() if p.GetNetname() and p.GetNetname() not in rf.SKIP_NETS})
    rng = random.Random(1)
    soft = {t.m_Uuid.AsString() for t in board.GetTracks() if rng.random() < 0.3}
    ok, n = True, 0
    for name in nets[::3]:
        net = board.FindNet(name)
        for half in (0.075, 0.2):
            for soft_items in ((), soft):
                rf.Grid._cache.clear()
                ref = obstacles.masks(net, half, soft_items)
                ref_soft = ({L: m.copy() for L, m in obstacles.soft.items()}, obstacles.soft_via.copy())
                for _ in range(2):  # twice: second call entirely from the cache
                    got = obstacles.masks(net, half, soft_items)
                    ok &= all(np.array_equal(ref[0][L], got[0][L]) for L in rf.SIGNAL_LAYERS)
                    ok &= np.array_equal(ref[1], got[1]) and np.array_equal(ref_soft[1], obstacles.soft_via)
                    ok &= all(np.array_equal(ref_soft[0][L], obstacles.soft[L]) for L in rf.SIGNAL_LAYERS)
                n += 1
    print(f"2 grid cache: {n} grids with/without cache → {'ok' if ok else 'ERROR'}")
    return ok


def check_astar(pcb):
    board = pcbnew.LoadBoard(str(pcb))
    obstacles = rf.Obstacles(board)
    grid = obstacles.grid
    rng = np.random.default_rng(3)
    grid.hist = np.where(rng.random((3, grid.ny, grid.nx)) < 0.02, 10.0, 0.0)
    rippable = {t.m_Uuid.AsString() for t in board.GetTracks() if not t.IsLocked() or rng.random() < 0.5}
    ok, n, none, t_new, t_ref = True, 0, 0, 0.0, 0.0
    for u in rf.open_connections(pcb)[:8]:
        src, net = rf.end_cells(board, grid, u["items"][0])
        dst, _ = rf.end_cells(board, grid, u["items"][1])
        if not src or not dst:
            continue
        for soft_items in ({}, rippable):
            track, via = obstacles.masks(net, rf.W_MIN / 2, soft_items)
            grid.soft, grid.soft_via = obstacles.soft, obstacles.soft_via
            cases = [dict(sources=src, targets=dst)]
            if not soft_items:  # case without path: target walled in; GND-like search for a via spot
                walled = {L: m.copy() for L, m in track.items()}
                L0, (i, j) = dst[0]
                for L in rf.SIGNAL_LAYERS:
                    walled[L][max(0, i - 4):i + 5, max(0, j - 4):j + 5] = True
                    walled[L][max(0, i - 2):i + 3, max(0, j - 2):j + 3] = False
                cases.append(dict(sources=src, targets=[dst[0]], track=walled))
                cases.append(dict(sources=src[:1], targets=[], goal_via=True, max_expand=60_000))
            for c in cases:
                tr = c.pop("track", track)
                t = time.time()
                a = rf.astar(grid, tr, via, **c)
                t_new += time.time() - t
                t = time.time()
                b = astar_ref(grid, tr, via, **c)
                t_ref += time.time() - t
                n += 1
                none += a is None
                if a != b:
                    ok = False
                    print(f"  DIFFERENCE: {u['items'][0]['description']} | {u['items'][1]['description']} {c.keys()}")
    print(f"3 astar: {n} searches ({none} without path) equal to astar_ref, new {t_new:.1f} s, old {t_ref:.1f} s "
          f"→ {'ok' if ok else 'ERROR'}")
    return ok


def main():
    pcb = Path(sys.argv[1]) if len(sys.argv) > 1 else OFFICIAL
    with tempfile.TemporaryDirectory() as tmp:
        ok = check_connections(pcb, tmp)
        ok &= check_masks(pcbnew.LoadBoard(str(pcb)))
        _, partial = list(states(pcb, tmp, [0, 60]))[1]
        ok &= check_astar(partial)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
