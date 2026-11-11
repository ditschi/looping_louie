"""Maze router for the 4-layer main board (docs/main-board-c6.md chapter 11).

Freerouting leaves 10–20 signal connections open on the 4-layer board (chapter 11.4). This script routes the
connections itself:

- The basis is the list of open connections from the KiCad DRC (pad–pad, pad–track, track–track).
- For each connection an A* on a 0.05 mm grid searches a path over the signal layers F.Cu, In2.Cu and B.Cu
  (In1 is the GND layer and stays free). Layer changes only at spots where a 0.3/0.5 mm via fits on all four
  layers (clearance, drill holes, keepout areas of the antenna and the board edge).
- Obstacles are rasterized geometrically: foreign tracks and pads with 0.15 mm clearance (+ margin), vias,
  drill holes with hole–copper clearance, keepout areas without tracks or without vias.
- Costs: length, bends, vias; inner layer In2 cheaper than the outer layers; F.Cu under the radio module
  expensive, in front of each signal edge pad of the module an escape lane that foreign nets avoid.
- Rip-up and reroute with PathFinder history costs: own tracks are soft obstacles; only if a path is not possible
  otherwise are the interfering nets removed and rerouted later.
- Then GND: zone islands without a via get a short track from one of their pads to a via onto the GND layer.
- If something stays open, route_all() starts over and routes the open nets first.
- Track width per net (WIDTHS): VSYS 0.4 mm, never below 0.3 mm (divider/test point 0.15 mm), BAT_IN/VLED 0.4 mm,
  3V3 0.25 mm (bottlenecks 0.15 mm), otherwise 0.15 mm.

Not bit-exactly repeatable: the order of the open connections depends on the (random) UUIDs of newly built tracks;
for connections of equal length and for several items at the same anchor point this order decides. Repeated runs
with the same costs therefore scatter (docs/main-board-c6.md 11.4). SEED > 0 additionally scatters the order on
purpose (route.py: attempts beyond the cost variants). Whether the result complies with the rules is decided at the
end by the KiCad DRC (just drc).

Run time (2026-11-07): the open connections come from the KiCad connectivity in-process (open_connections, same
edges as the DRC, without kicad-cli per round); rasterized obstacles are cached per geometry (Grid._patch); A*
works on flat indices. None of the three changes the search result (cross-check: test_route_fix.py).

Usage: via route.py main-board or directly: route_fix.py <board.kicad_pcb> [nets] [min_length]
"""
import heapq
import json
import math
import random
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import pcbnew

GRID = 0.05          # mm
CLEAR = 0.158        # clearance 0.15 mm + margin (grid error < 0.005 mm)
HOLE_CLEAR = 0.31    # component hole–copper inner 0.3 mm + margin
VIA_HOLE_CLEAR = 0.26  # via hole–copper 0.25 mm + margin
EDGE = 0.32          # copper–edge 0.3 mm + margin
VIA_D, VIA_DRILL = 0.5, 0.3  # like RULES_4L in gen_main_pcb.py
# Hole edge to hole edge for vias of other nets and drilled pads (board rule min_hole_to_hole 0.25 mm; at 0.25 the via
# spacing from the copper clearance is larger anyway, so this only acts above about 0.36 mm, e.g. JLC's 0.45 mm)
HOLE_TO_HOLE = 0.25
SKIP_NETS = {"/GND"}  # GND through the In1 zone and stitch.py
# Track widths per net (the first one first, the others at bottlenecks). The last one is the net's minimum width:
# nothing is ever routed below it (formerly VSYS 0.2 mm, docs/routing-score.md 8.1). The main motor paths
# (Schottky/Q1 → buffer → VM, OUT_A/OUT_B, VBUS, BAT_IN) are pre-routed in gen_main_pcb.py with 0.4–0.5 mm on the
# outer layers; here only the LDO input (up to about 0.4 A), LED LDO U6 and VLED (up to 0.5 A, PTC F1).
# Per IPC-2221 (20 K) 0.3 mm carries about 0.7 A outside, about 0.37 A inside (In2, 15 µm); so VLED at least 0.4 mm.
WIDTHS = {"/VSYS": (0.4, 0.3), "/BAT_IN": (0.4,), "/+3V3": (0.25, 0.15), "/VLED": (0.4,), "/VLED_SW": (0.4,)}
# pads with µA current in power nets (voltage divider VSYS, test point): the minimum track suffices there.
# The strings match the DRC/_describe() item description (German KiCad locale: "von" = "of").
LOW_CURRENT_PADS = {"Pad 1 [/VSYS] von R6", "Pad 1 [/VSYS] von TP1"}
W_MIN = 0.15
VIA_COST = 30        # in grid steps (1.5 mm)
BEND_COST = 2
LAYER_COST = {pcbnew.F_Cu: 1.3, pcbnew.In2_Cu: 1.0, pcbnew.B_Cu: 1.15}
# F.Cu under the radio module is the only way out for the edge pads (gap between the pads 0.4 mm, no track fits in
# between); expensive there so that tracks do not run along in front of the pads but dive down through a via soon.
MODULE_REF, MODULE_F_COST = "U1", 8.0
# escape lane in front of each signal edge pad of the module (inwards, length in mm): expensive and without vias
# for foreign nets
ESCAPE_LEN, ESCAPE_HALF, ESCAPE_COST = 1.4, 0.3, 40.0
# Rip-up and reroute: own tracks of foreign nets are "soft" obstacles with extra cost; if the path only goes through
# them, these nets are removed and rerouted later (at most RIP_MAX times per net).
RIP_COST, RIP_MAX, HIST_COST = 60.0, 10, 10.0
# Maximum number of routing steps per pass (route a connection, rip up, GND island). Since the optional parts
# below (2026-11-04) a pass needs more than the former 300 steps.
MAX_ROUNDS = 800
# Extensions 2026-11-06 (main-board-c6.md 11.7), each can be switched off:
# ENDPOINT_VIAS: if a via of the same net sits at the terminal (track or pad) (e.g. at the end of a pre-route), it
#   counts as start/target on all signal layers – before, the router started only on the track's layer.
# VIA_UNDER_BODIES: "bottom" = vias between the pads under component bodies on the bottom (unpopulated DNP parts)
#   allowed, under components on top only where their courtyard permits (module pad, thermal pad: as before);
#   "none" = under no component body. Via-in-pad always stays blocked, as do the antenna keepout areas.
# ISLAND_AREA_SEARCH: for a GND island without a via, search the via spot in the whole fill area of the island, not
#   only from one pad; in addition the track may end in an already connected GND fill on the same layer.
# GND_FANOUT_FIRST: before signal routing every GND SMD pad without a via nearby gets a short stub to its own via
#   onto the GND layer In1 (gnd_fanout); the signals avoid them. The island connection at the end stays as a
#   fallback.
# OVAL_DRILLS: block slotted holes (e.g. tabs of the USB-C connector) as a capsule instead of a circle.
GND_FANOUT_FIRST = True
# FANOUT_MODULE_CLEAR: no fanout via within this distance (mm) outward in front of a signal pad of the module. Between
#   the right module pads and the 0402 row (C13/C14) there are only 0.7 mm; a locked GND via there (from the GND pad
#   of C13/C14) blocked the 1.5 mm connections pad 12 -> C13 and pad 13 -> C14 (variant test 2026-11-08). 0 = off.
#   Off by default: with 1.0 mm in front of all 23 signal pads the displaced GND vias left IO8 open in 17 of 18
#   attempts and the mean got worse (base 6.3 -> 7.7, V1 4.3 -> 5.3 open); a narrower zone is still to be tested.
FANOUT_MODULE_CLEAR = 0
OVAL_DRILLS = True
ENDPOINT_VIAS = True
VIA_UNDER_BODIES = "bottom"
ISLAND_AREA_SEARCH = True
ORDER = "long"  # long connections first (best in the experiment: 1 open instead of 14 with "short")
ORDER_ALIASES = {"lang": "long", "kurz": "short", "modul": "module"}  # old German values
# SEED > 0: weight the length of each connection for the order with a fixed factor per net (1 ± SEED_JITTER).
# Gives more attempts their own order; SEED = 0 is the order without scatter.
SEED, SEED_JITTER = 0, 0.25
# CONN = "fast": open connections from the in-process connectivity (about 0.05 s), "drc": from kicad-cli (about 1 s)
CONN = "fast"
# run time per sub-step in seconds (for the trace in fix(trace=...))
TIMES = {"conn": 0.0, "masks": 0.0, "astar": 0.0}
SIGNAL_LAYERS = [pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]


def mm(v):
    return pcbnew.FromMM(v)


def drc_unconnected(pcb):
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(pcb)],
                       capture_output=True)
        data = json.loads(report.read_text())
    return data.get("unconnected_items", [])


def _describe(x):
    """Description of an item as in the (German-locale) DRC report; "[net]" and "von Ref" ("of Ref") are used.
    The German words are kept on purpose so that both sources give the same strings (see LOW_CURRENT_PADS)."""
    net, layer = x.GetNetname(), x.GetLayerName()
    if x.GetClass() == "PAD":
        return f"Pad {x.GetNumber()} [{net}] von {x.GetParentFootprint().GetReference()} auf {layer}"
    if x.GetClass() == "PCB_VIA":
        return f"Via [{net}] auf F.Cu - B.Cu"
    return f"Leiterbahn [{net}] auf {layer}, Länge {pcbnew.ToMM(x.GetLength()):.4f} mm"


def ratsnest(board, skip_nets=SKIP_NETS):
    """Open connections of the nets without copper zone as item pairs, like the KiCad ratsnest: clusters from the
    connectivity, then a minimum spanning tree over the anchors (pad center, track ends, via) with Kruskal. For
    edges of equal length (several items at the same point) KiCad prefers tracks; which of several tracks depends,
    there as here, on the order in the file. Returns None if a signal net has a copper zone (then the DRC
    applies)."""
    if any(not z.GetIsRuleArea() and z.GetNetname() not in skip_nets for z in board.Zones()):
        return None
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    by_net = {}
    for x in list(board.GetPads()) + list(board.GetTracks()):
        if x.GetNetCode() > 0 and x.GetNetname() not in skip_nets:
            by_net.setdefault(x.GetNetCode(), []).append(x)
    rank = {"PCB_TRACK": 0, "PCB_ARC": 0, "PAD": 1, "PCB_VIA": 2}
    out = []
    for items in by_net.values():
        uids = {x.m_Uuid.AsString() for x in items}
        cluster, k = {}, 0
        for x in items:
            if x.m_Uuid.AsString() in cluster:
                continue
            cluster[x.m_Uuid.AsString()] = k
            stack = [x]
            while stack:
                y = stack.pop()
                for z in list(conn.GetConnectedTracks(y)) + list(conn.GetConnectedPads(y)):
                    u = z.m_Uuid.AsString()
                    if u in uids and u not in cluster:
                        cluster[u] = k
                        stack.append(z)
            k += 1
        if k < 2:
            continue
        anchors = []  # (x, y, cluster, item)
        for x in sorted(items, key=lambda x: rank.get(x.GetClass(), 3)):
            pts = [x.GetStart(), x.GetEnd()] if rank.get(x.GetClass()) == 0 else [x.GetPosition()]
            anchors += [(q.x, q.y, cluster[x.m_Uuid.AsString()], x) for q in pts]
        edges = sorted(((ax - bx) ** 2 + (ay - by) ** 2, i, j)
                       for i, (ax, ay, ac, _) in enumerate(anchors)
                       for j, (bx, by, bc, _) in enumerate(anchors[i + 1:], i + 1) if ac != bc)
        parent = list(range(k))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for _, i, j in edges:
            ra, rb = find(anchors[i][2]), find(anchors[j][2])
            if ra != rb:
                parent[ra] = rb
                out.append((anchors[i][3], anchors[j][3]))
    return out


def open_connections(pcb, board=None):
    """Open connections in the format of drc_unconnected (items: uuid, description, pos in mm). CONN = "fast":
    ratsnest() in-process (same count and same spanning tree length as the DRC, cross-check in
    test_route_speed.py); otherwise, or with copper zones on signal nets, the KiCad DRC (reads the file pcb).
    board: already loaded board (saves LoadBoard, see fix())."""
    t0 = time.perf_counter()
    pairs = ratsnest(board if board is not None else pcbnew.LoadBoard(str(pcb))) if CONN == "fast" else None
    if pairs is None:
        result = drc_unconnected(pcb)
    else:
        result = [{"items": [{"uuid": x.m_Uuid.AsString(), "description": _describe(x),
                              "pos": {"x": pcbnew.ToMM(x.GetPosition().x), "y": pcbnew.ToMM(x.GetPosition().y)}}
                             for x in pair]} for pair in pairs]
    TIMES["conn"] += time.perf_counter() - t0
    return result


class Grid:
    """Grid over the board with helper functions for entering obstacles. The rasterized shapes (circle, segment,
    polygon, rectangle) are cached per geometry and radius (pads and most tracks do not change from round to
    round); the result is bit-identical to recomputing."""
    CACHE_BYTES = 200_000_000
    _cache, _cache_key, _cache_bytes = {}, None, 0

    def __init__(self, board):
        box = board.GetBoardEdgesBoundingBox()
        self.x0, self.y0 = pcbnew.ToMM(box.GetLeft()), pcbnew.ToMM(box.GetTop())
        self.nx = int(pcbnew.ToMM(box.GetWidth()) / GRID) + 1
        self.ny = int(pcbnew.ToMM(box.GetHeight()) / GRID) + 1
        xs = self.x0 + np.arange(self.nx) * GRID
        ys = self.y0 + np.arange(self.ny) * GRID
        self.X, self.Y = np.meshgrid(xs, ys)
        if Grid._cache_key != (self.x0, self.y0, self.nx, self.ny):  # different grid: clear the cache
            Grid._cache, Grid._cache_key, Grid._cache_bytes = {}, (self.x0, self.y0, self.nx, self.ny), 0

    def _patch(self, m, key, compute):
        """m[s] |= shape; shape (slice s, bool array) from the cache or compute()."""
        hit = Grid._cache.get(key)
        if hit is None:
            hit = compute()
            if Grid._cache_bytes > Grid.CACHE_BYTES:
                Grid._cache, Grid._cache_bytes = {}, 0
            Grid._cache[key] = hit
            Grid._cache_bytes += hit[1].nbytes + 200
        m[hit[0]] |= hit[1]

    def empty(self):
        return np.zeros((self.ny, self.nx), dtype=bool)

    def _sel(self, xa, ya, xb, yb):
        i0 = max(0, int((ya - self.y0) / GRID) - 1)
        i1 = min(self.ny, int((yb - self.y0) / GRID) + 2)
        j0 = max(0, int((xa - self.x0) / GRID) - 1)
        j1 = min(self.nx, int((xb - self.x0) / GRID) + 2)
        return slice(i0, i1), slice(j0, j1)

    def circle(self, m, p, r):
        self._patch(m, ("c", p.x, p.y, r), lambda: self._circle(p, r))

    def _circle(self, p, r):
        cx, cy = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
        s = self._sel(cx - r, cy - r, cx + r, cy + r)
        return s, (self.X[s] - cx) ** 2 + (self.Y[s] - cy) ** 2 < r ** 2

    def segment(self, m, a, b, r):
        self._patch(m, ("s", a.x, a.y, b.x, b.y, r), lambda: self._segment(a, b, r))

    def _segment(self, a, b, r):
        ax, ay, bx, by = (pcbnew.ToMM(v) for v in (a.x, a.y, b.x, b.y))
        s = self._sel(min(ax, bx) - r, min(ay, by) - r, max(ax, bx) + r, max(ay, by) + r)
        dx, dy = bx - ax, by - ay
        ll = dx * dx + dy * dy
        X, Y = self.X[s], self.Y[s]
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / ll, 0, 1) if ll > 0 else 0
        return s, (X - ax - t * dx) ** 2 + (Y - ay - t * dy) ** 2 < r ** 2

    def polygon(self, m, pts, r):
        """Convex or arbitrary polygon (list of (x, y) in mm), grown by r: interior + edge tubes."""
        self._patch(m, ("p", tuple(pts), r), lambda: self._polygon(pts, r))

    def _polygon(self, pts, r):
        xs = np.array([p[0] for p in pts])
        ys = np.array([p[1] for p in pts])
        s = self._sel(xs.min() - r, ys.min() - r, xs.max() + r, ys.max() + r)
        X, Y = self.X[s], self.Y[s]
        inside = np.zeros(X.shape, dtype=bool)
        n = len(pts)
        for k in range(n):  # ray casting test
            x1, y1, x2, y2 = xs[k], ys[k], xs[(k + 1) % n], ys[(k + 1) % n]
            cond = (y1 > Y) != (y2 > Y)
            with np.errstate(divide="ignore", invalid="ignore"):
                xc = x1 + (Y - y1) * (x2 - x1) / (y2 - y1)
            inside ^= cond & (X < xc)
        near = inside
        for k in range(n):
            ax, ay, bx, by = xs[k], ys[k], xs[(k + 1) % n], ys[(k + 1) % n]
            dx, dy = bx - ax, by - ay
            ll = dx * dx + dy * dy
            t = np.clip(((X - ax) * dx + (Y - ay) * dy) / ll, 0, 1) if ll > 0 else 0
            near = near | ((X - ax - t * dx) ** 2 + (Y - ay - t * dy) ** 2 < r ** 2)
        return s, near

    def rect(self, m, box, r):
        key = ("r", box.GetLeft(), box.GetTop(), box.GetRight(), box.GetBottom(), r)
        self._patch(m, key, lambda: self._rect(box, r))

    def _rect(self, box, r):
        xa, ya = pcbnew.ToMM(box.GetLeft()) - r, pcbnew.ToMM(box.GetTop()) - r
        xb, yb = pcbnew.ToMM(box.GetRight()) + r, pcbnew.ToMM(box.GetBottom()) + r
        s = self._sel(xa, ya, xb, yb)
        return s, (self.X[s] > xa) & (self.X[s] < xb) & (self.Y[s] > ya) & (self.Y[s] < yb)

    def border(self, m, r):
        k = int(math.ceil(r / GRID))
        m[:k, :] = True
        m[-k:, :] = True
        m[:, :k] = True
        m[:, -k:] = True

    def cell(self, p):
        return (int(round((pcbnew.ToMM(p.y) - self.y0) / GRID)), int(round((pcbnew.ToMM(p.x) - self.x0) / GRID)))

    def point(self, c):
        return pcbnew.VECTOR2I(mm(self.x0 + c[1] * GRID), mm(self.y0 + c[0] * GRID))


class Obstacles:
    """Obstacles of a board state; masks() returns the blocking grids for a net and a track width."""

    def __init__(self, board):
        self.board = board
        self.grid = Grid(board)
        self.pad_polys = {}
        g = self.grid
        g.extra_cost = np.full((g.ny, g.nx), LAYER_COST[pcbnew.F_Cu])
        module = board.FindFootprintByReference(MODULE_REF)
        if module is not None:
            m = g.empty()
            g.rect(m, module.GetCourtyard(pcbnew.F_CrtYd).BBox(), 0)
            g.extra_cost[m] = MODULE_F_COST
            c = module.GetPosition()
            self.escapes = []  # (net code, rectangle in mm)
            for pad in module.Pads():
                if not pad.GetNetname() or pad.GetNetname() == "/GND" or pad.GetNumber() == "49" \
                        or pad.GetNetname().startswith("unconnected"):
                    continue
                q, b = pad.GetPosition(), pad.GetBoundingBox()
                dx, dy = c.x - q.x, c.y - q.y
                x0, x1 = pcbnew.ToMM(b.GetLeft()), pcbnew.ToMM(b.GetRight())
                y0, y1 = pcbnew.ToMM(b.GetTop()), pcbnew.ToMM(b.GetBottom())
                qx, qy = pcbnew.ToMM(q.x), pcbnew.ToMM(q.y)
                if abs(dy) > abs(dx):  # pad on a long edge: lane in y direction
                    ya, yb = (y1, y1 + ESCAPE_LEN) if dy > 0 else (y0 - ESCAPE_LEN, y0)
                    rect = (qx - ESCAPE_HALF, ya, qx + ESCAPE_HALF, yb)
                else:
                    xa, xb = (x1, x1 + ESCAPE_LEN) if dx > 0 else (x0 - ESCAPE_LEN, x0)
                    rect = (xa, qy - ESCAPE_HALF, xb, qy + ESCAPE_HALF)
                self.escapes.append((pad.GetNetCode(), rect))
        else:
            self.escapes = []

    def _pad_pts(self, pad, layer):
        key = (pad.m_Uuid.AsString(), layer)
        if key not in self.pad_polys:
            poly = pcbnew.SHAPE_POLY_SET()
            pad.TransformShapeToPolygon(poly, layer, 0, mm(0.005), pcbnew.ERROR_OUTSIDE)
            outs = []
            for i in range(poly.OutlineCount()):
                o = poly.Outline(i)
                outs.append([(pcbnew.ToMM(o.CPoint(k).x), pcbnew.ToMM(o.CPoint(k).y)) for k in range(o.PointCount())])
            self.pad_polys[key] = outs
        return self.pad_polys[key]

    def masks(self, net, half, soft_items=()):
        """Blocking grid per signal layer for the center line of a track with half width `half`, and the via grid
        (True = no via center may lie there). Items in soft_items (UUIDs) go into self.soft (per layer) and
        self.soft_via instead."""
        t0 = time.perf_counter()
        g, code = self.grid, net.GetNetCode()
        hard_track = {L: g.empty() for L in SIGNAL_LAYERS}
        hard_via = g.empty()
        self.soft = {L: g.empty() for L in SIGNAL_LAYERS}
        self.soft_via = g.empty()
        rv = VIA_D / 2
        for t in self.board.GetTracks():
            same = t.GetNetCode() == code
            soft = (not same) and t.m_Uuid.AsString() in soft_items
            track, via = (self.soft, self.soft_via) if soft else (hard_track, hard_via)
            if t.GetClass() == "PCB_VIA":
                p = t.GetPosition()
                if same:  # hole clearance 0.25 mm to the own via
                    g.circle(via, p, VIA_DRILL + 0.3)
                    continue
                g.circle(via, p, max(2 * rv + CLEAR, VIA_DRILL / 2 + VIA_HOLE_CLEAR + rv, VIA_DRILL + HOLE_TO_HOLE + 0.01))
                for L in SIGNAL_LAYERS:
                    g.circle(track[L], p, max(rv + CLEAR + half, VIA_DRILL / 2 + VIA_HOLE_CLEAR + half))
                continue
            if same:
                continue
            L = t.GetLayer()
            w = pcbnew.ToMM(t.GetWidth()) / 2
            if L in track:
                g.segment(track[L], t.GetStart(), t.GetEnd(), w + CLEAR + half)
            g.segment(via, t.GetStart(), t.GetEnd(), w + max(CLEAR + rv, VIA_DRILL / 2 + VIA_HOLE_CLEAR))
        track, via = hard_track, hard_via
        for pad in self.board.GetPads():
            drill = pad.GetDrillSize()
            if drill.x > 0:  # drill hole: hole–copper on all layers; slot as capsule (OVAL_DRILLS)
                a, b, r = drill_capsule(pad)
                for L in SIGNAL_LAYERS:
                    g.segment(track[L], a, b, r + half)
                g.segment(via, a, b, max(r + rv, r - HOLE_CLEAR + VIA_DRILL / 2 + HOLE_TO_HOLE + 0.01))
            if pad.GetNetCode() == code and code != 0:
                if drill.x <= 0:  # no via into the own SMD pad (no via-in-pad)
                    for L in (pcbnew.F_Cu, pcbnew.B_Cu):
                        if pad.IsOnLayer(L):
                            for pts in self._pad_pts(pad, L):
                                g.polygon(via, pts, rv + 0.05)
                continue
            for L in SIGNAL_LAYERS:
                if pad.IsOnLayer(L):
                    for pts in self._pad_pts(pad, L):
                        g.polygon(track[L], pts, CLEAR + half)
            # via hole to the copper of a through-hole pad: project rule "component hole to copper" 0.28 mm (inner
            # 0.3 mm) instead of 0.25 mm – in round M a via was 0.275 mm from the J4 tab S1
            hole_cu = HOLE_CLEAR if drill.x > 0 else VIA_HOLE_CLEAR
            for L in cu_of(pad):
                for pts in self._pad_pts(pad, L):
                    g.polygon(via, pts, max(CLEAR + rv, VIA_DRILL / 2 + hole_cu))
        if VIA_UNDER_BODIES == "none":  # vias under no component body (courtyard), not required as before 2026-11-06
            for fp in self.board.GetFootprints():
                side = pcbnew.F_CrtYd if fp.GetSide() == pcbnew.F_Cu else pcbnew.B_CrtYd
                box = fp.GetCourtyard(side).BBox()
                if box.GetWidth() > 0 and fp.GetReference() != MODULE_REF:
                    g.rect(via, box, 0)
        for z in self.board.Zones():
            if not z.GetIsRuleArea():
                continue
            for L in SIGNAL_LAYERS:
                if z.GetDoNotAllowTracks() and z.IsOnLayer(L):
                    g.rect(track[L], z.GetBoundingBox(), half)
            if z.GetDoNotAllowVias():
                g.rect(via, z.GetBoundingBox(), rv)
        for L in SIGNAL_LAYERS:
            g.border(track[L], EDGE + half)
        g.border(via, EDGE + rv + 0.3)
        fcost = g.extra_cost.copy()
        for ncode, (xa, ya, xb, yb) in self.escapes:
            if ncode == code:
                continue
            sl = g._sel(xa, ya, xb, yb)
            inside = (g.X[sl] > xa) & (g.X[sl] < xb) & (g.Y[sl] > ya) & (g.Y[sl] < yb)
            fcost[sl][inside] = ESCAPE_COST
            via[sl] |= inside
        g.fcost = fcost
        TIMES["masks"] += time.perf_counter() - t0
        return track, via


def drill_capsule(pad):
    """Drill hole as a capsule: center line (a, b) and radius including hole–copper clearance. Round hole: a = b.
    With OVAL_DRILLS = False, as before, a circle with the large diameter (too small for slots: at the J4 tab S1
    5 µm were missing)."""
    d = pad.GetDrillSize()
    q = pad.GetPosition()
    big, small = max(d.x, d.y), min(d.x, d.y)
    if not OVAL_DRILLS or big == small:
        r = pcbnew.ToMM(big) / 2 + HOLE_CLEAR
        return q, q, r
    import math
    half = (big - small) / 2
    ang = math.radians(pad.GetOrientation().AsDegrees()) + (0 if d.x >= d.y else math.pi / 2)
    dx, dy = int(half * math.cos(ang)), int(-half * math.sin(ang))
    return (pcbnew.VECTOR2I(q.x - dx, q.y - dy), pcbnew.VECTOR2I(q.x + dx, q.y + dy),
            pcbnew.ToMM(small) / 2 + HOLE_CLEAR)


def cu_of(pad):
    return [L for L in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if pad.IsOnLayer(L)]


STEPS = [(0, 1, 1.0), (1, 0, 1.0), (0, -1, 1.0), (-1, 0, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414),
         (-1, -1, 1.414)]


def astar(grid, track, via, sources, targets, max_expand=1_000_000, goal_via=False, area_sources=(), area_targets=()):
    """A* over (layer, row, column). sources/targets: list of (layer, cell). Returns a list of (layer, cell).
    goal_via=True: no target, but the nearest spot on the start layer where a via fits
    (connecting a GND pad to the GND layer In1).
    States as flat index l·ny·nx + i·nx + j (same order as the tuple (l, (i, j)), hence the same decision at
    equal cost), grids as Python lists, heuristic row by row with numpy (same floating-point operations as the
    per-cell formula): same path as the former version with tuples and single numpy accesses, only faster
    (cross-check in test_route_fix.py)."""
    t0 = time.perf_counter()
    try:
        return _astar(grid, track, via, sources, targets, max_expand, goal_via, area_sources, area_targets)
    finally:
        TIMES["astar"] += time.perf_counter() - t0


def _reachable(blocked, via_ok, sources, tset, nn):
    """Is there any path at all from a source to a target? Connected components of the free cells per layer
    (8-neighborhood as in astar), joined at via spots where both layers are free. Without a path A* would
    otherwise search the whole reachable area before giving up; the result (None) is the same."""
    from scipy import ndimage
    nl = blocked.shape[0]
    labels = np.zeros(blocked.shape, dtype=np.int64)
    offset = 0
    for l in range(nl):
        lab, n = ndimage.label(~blocked[l], structure=np.ones((3, 3), dtype=bool))
        labels[l] = np.where(lab > 0, lab + offset, 0)
        offset += n
    parent = np.arange(offset + 1)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for l in range(nl):
        for l2 in range(l + 1, nl):
            both = via_ok & (labels[l] > 0) & (labels[l2] > 0)
            for a, b in np.unique(np.stack([labels[l][both], labels[l2][both]], axis=1), axis=0):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
    flat = labels.ravel()
    src = {find(labels[SIGNAL_LAYERS.index(L), c[0], c[1]]) for L, c in sources}
    return any(find(flat[t]) in src for t in tset)


def _astar(grid, track, via, sources, targets, max_expand, goal_via, area_sources, area_targets):
    layers = SIGNAL_LAYERS
    li = {L: k for k, L in enumerate(layers)}
    blocked = np.stack([track[L] for L in layers])
    k = 1
    for L, c in list(sources) + list(targets):  # free the own terminal points
        blocked[li[L], max(0, c[0] - k):c[0] + k + 1, max(0, c[1] - k):c[1] + k + 1] = False
    # area start points (ISLAND_AREA_SEARCH): only free cells, free nothing
    sources = list(sources) + [(L, c) for L, c in area_sources if not blocked[li[L], c[0], c[1]]]
    ny, nx = grid.ny, grid.nx
    nn = ny * nx
    tset = {li[L] * nn + c[0] * nx + c[1] for L, c in targets}
    # area targets (ISLAND_AREA_SEARCH: connected GND fill): only free cells, free nothing
    tset |= {li[L] * nn + c[0] * nx + c[1] for L, c in area_targets if not blocked[li[L], c[0], c[1]]}
    if not goal_via and not _reachable(blocked, ~via, sources, tset, nn):
        return None
    tl = list({c for _, c in targets})
    ti = np.array([t[0] for t in tl], dtype=np.int64)
    tj = np.array([t[1] for t in tl], dtype=np.int64)
    cols = np.arange(nx, dtype=np.int64)
    hrows = [None] * ny

    def hrow(i):
        """Heuristic of a row: min over the targets of max(|di|, |dj|) + 0.414·min(|di|, |dj|)."""
        di = np.abs(i - ti)[:, None]
        dj = np.abs(cols[None, :] - tj[:, None])
        row = (np.maximum(di, dj) + 0.414 * np.minimum(di, dj)).min(axis=0).tolist()
        hrows[i] = row
        return row

    def h(i, j):
        if goal_via:
            return 0
        row = hrows[i]
        return (row if row is not None else hrow(i))[j]

    nl = len(layers)
    blk = blocked.ravel().tolist()
    via_ok = (~via).ravel().tolist()
    cost_l = [LAYER_COST[L] for L in layers]
    extra = grid.fcost.ravel().tolist()
    soft = (np.stack([grid.soft[L] for L in layers]) if hasattr(grid, "soft") else np.zeros_like(blocked)).ravel().tolist()
    soft_via = (grid.soft_via if hasattr(grid, "soft_via") else np.zeros_like(via)).ravel().tolist()
    hist = (grid.hist if hasattr(grid, "hist") else np.zeros(blocked.shape)).ravel().tolist()
    best = [1e18] * (nl * nn)
    prev, dirs = {}, {}
    heap = []
    for L, c in sources:
        s = li[L] * nn + c[0] * nx + c[1]
        best[s] = 0
        dirs[s] = -1
        heapq.heappush(heap, (h(c[0], c[1]), 0, s))
    steps = [(di, dj, di * nx + dj, cost) for di, dj, cost in STEPS]
    heappush, heappop = heapq.heappush, heapq.heappop
    n_exp = 0
    while heap:
        _, g, s = heappop(heap)
        l, cell = divmod(s, nn)
        if s in tset or (goal_via and via_ok[cell] and g > 0):
            path = [s]
            while s in prev:
                s = prev[s]
                path.append(s)
            out = []
            for s in path[::-1]:
                l, cell = divmod(s, nn)
                out.append((layers[l], divmod(cell, nx)))
            return out
        if g > best[s]:
            continue
        n_exp += 1
        if n_exp > max_expand:
            return None
        ci, cj = divmod(cell, nx)
        d = dirs[s]
        base = l * nn
        lc = cost_l[l]
        for kk, (di, dj, dn, cost) in enumerate(steps):
            ni, nj = ci + di, cj + dj
            if not (0 <= ni < ny and 0 <= nj < nx):
                continue
            ncell = cell + dn
            ns = base + ncell
            if blk[ns]:
                continue
            ng = g + cost * (extra[ncell] if l == 0 else lc) + (BEND_COST if d not in (-1, kk) else 0) \
                + (RIP_COST if soft[ns] else 0) + hist[ns]
            if ng < best[ns]:
                best[ns] = ng
                prev[ns] = s
                dirs[ns] = kk
                heappush(heap, (ng + h(ni, nj), ng, ns))
        if via_ok[cell] and not goal_via:
            for l2 in range(nl):
                ns = l2 * nn + cell
                if l2 == l or blk[ns]:
                    continue
                ng = g + VIA_COST + (RIP_COST if soft_via[cell] or soft[ns] else 0)
                if ng < best[ns]:
                    best[ns] = ng
                    prev[ns] = s
                    dirs[ns] = -1
                    heappush(heap, (ng + h(ci, cj), ng, ns))
    return None


def end_cells(board, grid, item):
    """Terminal cells of a DRC item: list of (layer, cell) and net."""
    obj = next((o for o in list(board.GetTracks()) + list(board.GetPads()) if o.m_Uuid.AsString() == item["uuid"]),
               None)
    if obj is None:
        return None, None
    if obj.GetClass() == "PAD":
        cells = [(L, grid.cell(obj.GetPosition())) for L in SIGNAL_LAYERS if obj.IsOnLayer(L)]
        return cells + endpoint_via_cells(board, grid, obj), obj.GetNet()
    if obj.GetClass() == "PCB_VIA":
        return [(L, grid.cell(obj.GetPosition())) for L in SIGNAL_LAYERS], obj.GetNet()
    if obj.GetLayer() not in SIGNAL_LAYERS:
        return None, None
    s, e = obj.GetStart(), obj.GetEnd()
    n = max(1, int((e - s).EuclideanNorm() / mm(0.25)))
    cells = [(obj.GetLayer(), grid.cell(pcbnew.VECTOR2I(int(s.x + (e.x - s.x) * k / n), int(s.y + (e.y - s.y) * k / n))))
             for k in range(n + 1)]  # points along the track
    return cells + endpoint_via_cells(board, grid, obj), obj.GetNet()


def endpoint_via_cells(board, grid, obj):
    """ENDPOINT_VIAS: vias of the same net that touch the item (track end or pad) as terminals on all signal
    layers. Locked (pre-routed) vias count the same; the item itself stays unchanged."""
    if not ENDPOINT_VIAS:
        return []
    code = obj.GetNetCode()
    out = []
    for v in board.GetTracks():
        if v.GetClass() != "PCB_VIA" or v.GetNetCode() != code:
            continue
        q = v.GetPosition()
        r = mm(VIA_D / 2)
        if obj.GetClass() == "PAD":
            touch = obj.HitTest(q, r)
        else:
            w = obj.GetWidth() // 2
            touch = any((q - e).EuclideanNorm() <= w + r for e in (obj.GetStart(), obj.GetEnd()))
        if touch:
            out += [(L, grid.cell(q)) for L in SIGNAL_LAYERS]
    return out


def simplify(path):
    """Keep only bend points and layer changes."""
    out = [path[0]]
    for i in range(1, len(path) - 1):
        (l0, a), (l1, b), (l2, c) = path[i - 1], path[i], path[i + 1]
        if l0 != l1 or l1 != l2 or (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            out.append(path[i])
    out.append(path[-1])
    return out


def build(board, grid, net, path, width, start_pt=None, end_pt=None):
    """Tracks and vias from the cell path; first/last point exactly on the terminal (pad/track point)."""
    pts = [grid.point(c) for _, c in path]
    if start_pt is not None:
        pts[0] = start_pt
    if end_pt is not None:
        pts[-1] = end_pt
    for k, ((la, a), (lb, b)) in enumerate(zip(path, path[1:])):
        if la != lb:
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pts[k])
            via.SetWidth(mm(VIA_D))
            via.SetDrill(mm(VIA_DRILL))
            via.SetNet(net)
            via.SetLocked(True)
            board.Add(via)
            continue
        if pts[k] == pts[k + 1]:
            continue
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pts[k])
        t.SetEnd(pts[k + 1])
        t.SetLayer(la)
        t.SetWidth(mm(width))
        t.SetNet(net)
        t.SetLocked(True)
        board.Add(t)


def connect(board, obstacles, item_a, item_b, rippable=None):
    """Search and build a path. rippable: {uuid: net name} of own tracks that may be ripped up.
    Returns (description, ripped net names, new UUIDs) or None."""
    grid = obstacles.grid
    src, net = end_cells(board, grid, item_a)
    dst, _ = end_cells(board, grid, item_b)
    if not src or not dst:
        return None
    rippable = rippable or {}
    for soft_items in ({}, rippable):  # first without rip-up, then with
        if soft_items is rippable and not rippable:
            break
        widths = WIDTHS.get(net.GetNetname(), (W_MIN,))
        if any(i["description"].startswith(p) for i in (item_a, item_b) for p in LOW_CURRENT_PADS):
            widths = widths + (W_MIN,)
        for width in sorted(set(widths), reverse=True):
            track, via = obstacles.masks(net, width / 2, soft_items)
            grid.soft, grid.soft_via = obstacles.soft, obstacles.soft_via
            path = astar(grid, track, via, src, dst)
            if not path:
                continue
            ripped = set()
            conflict = []
            if soft_items:
                hit_cells = {(L, c) for L, c in path}
                via_cells = {c for (la, c), (lb, _) in zip(path, path[1:]) if la != lb}
                li = {L: k for k, L in enumerate(SIGNAL_LAYERS)}
                for L, c in hit_cells:
                    if obstacles.soft[L][c]:
                        ripped.add((L, c))
                for c in via_cells:
                    if obstacles.soft_via[c] or any(obstacles.soft[L][c] for L in SIGNAL_LAYERS):
                        ripped.add((None, c))
                conflict = list(ripped)
                nets = _owners(board, grid, rippable, ripped, width / 2)
                for t in list(board.GetTracks()):
                    if t.m_Uuid.AsString() in rippable and rippable[t.m_Uuid.AsString()] in nets:
                        board.Delete(t)
                ripped = nets
            before = {t.m_Uuid.AsString() for t in board.GetTracks()}
            path = simplify(path)
            build(board, grid, net, path, width)
            new = {t.m_Uuid.AsString() for t in board.GetTracks()} - before
            nvias = sum(1 for (la, _), (lb, _) in zip(path, path[1:]) if la != lb)
            layers = sorted({pcbnew.BOARD.GetStandardLayerName(L) for L, _ in path})
            # history (PathFinder): contested cells become more expensive for everyone, this breaks oscillation cycles
            if ripped and hasattr(grid, "hist"):
                for L, c in conflict:
                    for l in ([SIGNAL_LAYERS.index(L)] if L is not None else range(len(SIGNAL_LAYERS))):
                        grid.hist[l, max(0, c[0] - 3):c[0] + 4, max(0, c[1] - 3):c[1] + 4] += HIST_COST
            return f"{'/'.join(layers)}, {nvias} vias, {width} mm", ripped, new
    return None


def connect_gnd(board, obstacles, pad, rippable=None, exclude=()):
    """Connect a GND pad via a short track on its layer to a new via (In1 is GND) or to existing GND copper
    (via, pad outside exclude). Returns (description, ripped groups, new UUIDs) or None."""
    grid = obstacles.grid
    net = pad.GetNet()
    layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    src = [(layer, grid.cell(pad.GetPosition()))]
    code = net.GetNetCode()
    dst = [(layer, grid.cell(t.GetPosition())) for t in board.GetTracks()
           if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code]
    # targets only vias (they reach the GND layer In1) and through-hole pads; an SMD pad may itself lie in an island
    dst += [(layer, grid.cell(p.GetPosition())) for p in board.GetPads()
            if p.GetNetCode() == code and p.IsOnLayer(layer) and p.GetDrillSize().x > 0]
    rippable = rippable or {}
    area = island_cells(board, grid, pad, layer) if ISLAND_AREA_SEARCH else []
    # also target the GND fill on the same layer that already has a via (a short track suffices then)
    linked = linked_fill_cells(board, grid, code, layer) if ISLAND_AREA_SEARCH else []
    for soft_items in ({}, rippable):
        if soft_items is rippable and not rippable:
            break
        for width in (0.25, W_MIN):
            track, via = obstacles.masks(net, width / 2, soft_items)
            grid.soft, grid.soft_via = obstacles.soft, obstacles.soft_via
            path = astar(grid, track, via, src, dst, max_expand=60_000, goal_via=True, area_targets=linked)
            if not path and area:  # via spot anywhere in the fill area of the island
                path = astar(grid, track, via, [], [], max_expand=60_000, goal_via=True, area_sources=area)
            if not path:
                continue
            ripped = set()
            if soft_items:
                cells = {(L, c) for L, c in path if obstacles.soft[L][c]}
                end = path[-1][1]
                if obstacles.soft_via[end] or any(obstacles.soft[L][end] for L in SIGNAL_LAYERS):
                    cells.add((None, end))
                ripped = _owners(board, grid, rippable, cells, width / 2)
                for t in list(board.GetTracks()):
                    if rippable.get(t.m_Uuid.AsString()) in ripped:
                        board.Delete(t)
            before = {t.m_Uuid.AsString() for t in board.GetTracks()}
            path = simplify(path)
            build(board, grid, net, path, width)
            to_copper = path[-1] in set(dst) or path[-1] in set(linked)
            if not to_copper:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(grid.point(path[-1][1]))
                v.SetWidth(mm(VIA_D))
                v.SetDrill(mm(VIA_DRILL))
                v.SetNet(net)
                v.SetLocked(True)
                board.Add(v)
            new = {t.m_Uuid.AsString() for t in board.GetTracks()} - before
            return f"GND {'track' if to_copper else 'via'}, {width} mm", ripped, new
    return None


def island_cells(board, grid, pad, layer, step=2):
    """Grid cells of the filled GND zone on `layer` in which `pad` lies (every `step`-th cell)."""
    code = pad.GetNetCode()
    q = pad.GetPosition()
    for zone in board.Zones():
        if zone.GetIsRuleArea() or zone.GetNetCode() != code or not zone.IsOnLayer(layer):
            continue
        polys = zone.GetFilledPolysList(layer)
        for i in range(polys.OutlineCount()):
            outline = polys.Outline(i)
            if not outline.PointInside(q) and not pad.HitTest(outline.CPoint(0), mm(1.0)):
                if not any(pad.HitTest(outline.CPoint(k)) for k in range(0, outline.PointCount(), 4)):
                    continue
            box = outline.BBox()
            i0, j0 = grid.cell(pcbnew.VECTOR2I(box.GetLeft(), box.GetTop()))
            i1, j1 = grid.cell(pcbnew.VECTOR2I(box.GetRight(), box.GetBottom()))
            cells = []
            for ii in range(max(0, i0), min(grid.ny, i1 + 1), step):
                for jj in range(max(0, j0), min(grid.nx, j1 + 1), step):
                    if outline.PointInside(grid.point((ii, jj))):
                        cells.append((layer, (ii, jj)))
            return cells
    return []


def linked_fill_cells(board, grid, code, layer, step=3):
    """Grid cells of the fill areas on `layer` that are already connected through a via or through-hole pad."""
    anchors = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code]
    anchors += [p.GetPosition() for p in board.GetPads() if p.GetNetCode() == code and p.GetDrillSize().x > 0]
    cells = []
    for zone in board.Zones():
        if zone.GetIsRuleArea() or zone.GetNetCode() != code or not zone.IsOnLayer(layer):
            continue
        polys = zone.GetFilledPolysList(layer)
        for i in range(polys.OutlineCount()):
            outline = polys.Outline(i)
            if not any(outline.PointInside(a) for a in anchors):
                continue
            box = outline.BBox()
            i0, j0 = grid.cell(pcbnew.VECTOR2I(box.GetLeft(), box.GetTop()))
            i1, j1 = grid.cell(pcbnew.VECTOR2I(box.GetRight(), box.GetBottom()))
            for ii in range(max(0, i0), min(grid.ny, i1 + 1), step):
                for jj in range(max(0, j0), min(grid.nx, j1 + 1), step):
                    if outline.PointInside(grid.point((ii, jj))):
                        cells.append((layer, (ii, jj)))
    return cells


def fragment_vias(pcb, net_name="/GND", log=print):
    """ISLAND_AREA_SEARCH: every fill piece of the net on F.Cu/In2/B.Cu without a via and without a through-hole pad
    gets a via at the first spot in its fill where one fits (clearances as in routing). Refills afterwards.
    Returns the number of vias placed."""
    board = pcbnew.LoadBoard(str(pcb))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    net = board.FindNet(net_name)
    code = net.GetNetCode()
    obstacles = Obstacles(board)
    grid = obstacles.grid
    _, via = obstacles.masks(net, W_MIN / 2)
    added = 0
    for zone in board.Zones():
        if zone.GetIsRuleArea() or zone.GetNetCode() != code:
            continue
        for layer in SIGNAL_LAYERS:
            if not zone.IsOnLayer(layer):
                continue
            polys = zone.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                outline = polys.Outline(i)
                anchors = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA"
                           and t.GetNetCode() == code]
                anchors += [p.GetPosition() for p in board.GetPads() if p.GetNetCode() == code and p.GetDrillSize().x > 0]
                if any(outline.PointInside(a) for a in anchors):
                    continue
                box = outline.BBox()
                i0, j0 = grid.cell(pcbnew.VECTOR2I(box.GetLeft(), box.GetTop()))
                i1, j1 = grid.cell(pcbnew.VECTOR2I(box.GetRight(), box.GetBottom()))
                spot = None
                for ii in range(max(0, i0), min(grid.ny, i1 + 1)):
                    for jj in range(max(0, j0), min(grid.nx, j1 + 1)):
                        if not via[ii, jj] and outline.PointInside(grid.point((ii, jj))):
                            # the via must lie entirely inside the fill (otherwise it does not connect reliably)
                            q = grid.point((ii, jj))
                            r = mm(VIA_D / 2)
                            if all(outline.PointInside(pcbnew.VECTOR2I(q.x + dx, q.y + dy))
                                   for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r))):
                                spot = q
                                break
                    if spot:
                        break
                if spot is None:
                    log(f"  fill piece without via space: {board.GetLayerName(layer)} "
                        f"({pcbnew.ToMM(box.GetX()):.2f}; {pcbnew.ToMM(box.GetY()):.2f})")
                    continue
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(spot)
                v.SetWidth(mm(VIA_D))
                v.SetDrill(mm(VIA_DRILL))
                v.SetNet(net)
                v.SetLocked(True)
                board.Add(v)
                added += 1
                g = grid  # the via blocks its surroundings for further vias
                g.circle(via, spot, 2 * (VIA_D / 2) + CLEAR)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(pcb), board)
    return added


def gnd_tasks(board, net_name="/GND", near=0.9):
    """GND SMD pads that need their own via to the GND layer (do not already have one in/at the pad)."""
    code = board.FindNet(net_name).GetNetCode()
    vias = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code]
    out = []
    for p in board.GetPads():
        if p.GetNetCode() != code or p.GetDrillSize().x > 0:
            continue
        if any((v - p.GetPosition()).EuclideanNorm() < mm(near) and p.HitTest(v, mm(VIA_D / 2 + 0.6)) for v in vias):
            continue
        out.append((p.GetParentFootprint().GetReference(), p.GetNumber()))
    return sorted(out)


def island_tasks(board, net_name="/GND"):
    """GND zone islands without a via and without a through-hole pad (after filling): per island the pads in it.
    One pad per island needs a track to a via (connect_gnd)."""
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    code = board.FindNet(net_name).GetNetCode()
    vias = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code]
    pads = [p for p in board.GetPads() if p.GetNetCode() == code]
    tasks = []
    for zone in board.Zones():
        if zone.GetIsRuleArea() or zone.GetNetCode() != code:
            continue
        for layer in (pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
            if not zone.IsOnLayer(layer):
                continue
            polys = zone.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                outline = polys.Outline(i)
                if any(outline.PointInside(v) for v in vias):
                    continue
                if any(p.GetDrillSize().x > 0 and outline.PointInside(p.GetPosition()) for p in pads):
                    continue
                inner = sorted((p.GetParentFootprint().GetReference(), p.GetNumber()) for p in pads
                               if p.IsOnLayer(layer) and outline.PointInside(p.GetPosition()))
                if inner:
                    tasks.append(tuple(inner))
    # pads without any zone contact (e.g. enclosed by tracks) count individually
    return sorted(set(tasks))


def _owners(board, grid, rippable, cells, half):
    """Nets of the rip-up-able items that interfere at the cells (layer or None = via)."""
    rv = VIA_D / 2
    pts = [(L, pcbnew.ToMM(grid.point(c).x), pcbnew.ToMM(grid.point(c).y)) for L, c in cells]
    nets = set()
    for t in board.GetTracks():
        uid = t.m_Uuid.AsString()
        if uid not in rippable or rippable[uid] in nets:
            continue
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            px, py = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
            for L, x, y in pts:
                r = (2 * rv + CLEAR) if L is None else max(rv + CLEAR + half, VIA_DRILL / 2 + VIA_HOLE_CLEAR + half)
                if (x - px) ** 2 + (y - py) ** 2 < r * r:
                    nets.add(rippable[uid])
                    break
            continue
        a, b = t.GetStart(), t.GetEnd()
        ax, ay, bx, by = (pcbnew.ToMM(v) for v in (a.x, a.y, b.x, b.y))
        w = pcbnew.ToMM(t.GetWidth()) / 2
        for L, x, y in pts:
            if L is not None and L != t.GetLayer():
                continue
            r = w + (max(CLEAR + rv, VIA_DRILL / 2 + VIA_HOLE_CLEAR) if L is None else CLEAR + half)
            dx, dy = bx - ax, by - ay
            ll = dx * dx + dy * dy
            u = min(1, max(0, ((x - ax) * dx + (y - ay) * dy) / ll)) if ll > 0 else 0
            if (x - ax - u * dx) ** 2 + (y - ay - u * dy) ** 2 < r * r:
                nets.add(rippable[uid])
                break
    return nets


def fix(pcb, nets=None, min_len=0.0, max_rounds=None, log=print, priority=(), gnd=False, rip_tracks=None,
        trace=None, trace_label=""):
    """Route open signal connections (nets: only these nets; min_len: only connections of at least this length).
    trace: CSV file to which time, open connections and run time of the sub-steps are appended per round.
    Returns (routed, still open)."""
    max_rounds = max_rounds or MAX_ROUNDS
    done, failed = 0, set()

    def length(u):
        a, b = (u["items"][0]["pos"], u["items"][1]["pos"])
        return math.hypot(a["x"] - b["x"], a["y"] - b["y"])

    def wanted(u):
        text = " ".join(i.get("description", "") for i in u["items"])
        if any(f"[{n}]" in text for n in SKIP_NETS) or "Zone" in text:
            return False
        if nets is not None and not any(f"[{n}]" in text for n in nets):
            return False
        return length(u) >= min_len

    def weight(u):
        """SEED > 0: fixed factor 1 ± SEED_JITTER per net and seed, otherwise 1."""
        if not SEED:
            return 1.0
        d = u["items"][0]["description"]
        net = d[d.find("[") + 1:d.find("]")]
        return 1.0 + SEED_JITTER * (2 * random.Random(f"{SEED}:{net}").random() - 1)

    def order_key(u):
        """Order (ORDER): "short" = short ones first, "long" = long ones first, "module" = edge pads of the module
        first (only one escape lane), then short ones. The old German values lang/kurz/modul still work."""
        module = any(f"von {MODULE_REF} " in i["description"] for i in u["items"])  # "von" = "of" (DRC text)
        first = not any(f"[{n}]" in i["description"] for n in priority for i in u["items"])
        order = ORDER_ALIASES.get(ORDER, ORDER)
        if order == "long":
            return (first, -length(u) * weight(u))
        if order == "module":
            return (first, not module, length(u) * weight(u))
        return (first, length(u) * weight(u))

    todo = []
    mine = {}        # UUID -> group of the items built here (net name or "GND:Ref.Pad"), rip-up-able
    ripped_count = {}
    hist = None
    gnd_failed = set()
    gnd_open = []
    gnd_tries = {}
    # The board is loaded only once and then edited in memory (saved after each change): pcbnew does not free
    # loaded boards (about 4 MB per LoadBoard); with 2 LoadBoard per round an attempt grew to several GB over
    # ~900 rounds (2026-11-07: RAM and swap full, processes killed by the OOM killer).
    board = pcbnew.LoadBoard(str(pcb))
    # tracks from Freerouting (not locked) are rip-up-able as well, grouped by net
    for t in board.GetTracks():
        if not t.IsLocked() and t.GetNetname() not in SKIP_NETS:
            mine[t.m_Uuid.AsString()] = t.GetNetname()
    # rip_tracks: {UUID: net} of further rip-up-able tracks (finishing work on an already routed board whose router
    # tracks are locked; pre-routes do not belong in here)
    mine.update(rip_tracks or {})
    import shutil
    snap, snap_open = Path(pcb).with_suffix(".fixbest"), None
    t_start, rounds, times0 = time.perf_counter(), 0, dict(TIMES)
    if trace and not Path(trace).exists():
        Path(trace).write_text("run,round,t_s,open,best,action,conn_s,masks_s,astar_s\n")

    def note(action, n_open):
        """One line of the trace."""
        nonlocal times0
        if trace:
            dt = {k: TIMES[k] - times0[k] for k in TIMES}
            with open(trace, "a") as f:
                f.write(f"{trace_label},{rounds},{time.perf_counter() - t_start:.2f},{n_open},{snap_open},{action},"
                        f"{dt['conn']:.3f},{dt['masks']:.3f},{dt['astar']:.3f}\n")
        times0 = dict(TIMES)

    def finish(result, signals):
        """The best intermediate state (fewest open signal connections) wins if the end is worse."""
        if snap_open is not None and snap_open < signals:
            shutil.copy(snap, pcb)
            result = (result[0], snap_open)
            log(f"  best intermediate state restored: {snap_open} open")
        if snap.exists():
            snap.unlink()
        return result

    for rounds in range(1, max_rounds + 1):
        open_items = [u for u in open_connections(pcb, board) if wanted(u)]
        if snap_open is None or len(open_items) < snap_open:
            snap_open = len(open_items)
            shutil.copy(pcb, snap)
        todo = [u for u in open_items if tuple(sorted(i["uuid"] for i in u["items"])) not in failed]
        gtodo = []
        if gnd and not todo:  # first all signals, then GND islands without a via
            gnd_open = island_tasks(board)
            gtodo = [t for t in gnd_open if t not in gnd_failed]
        if not todo and not gtodo:
            if gnd_open:
                log(f"  GND islands without via: {'; '.join(', '.join('.'.join(r) for r in t) for t in gnd_open)}")
            note("end", len(open_items))
            return finish((done, len(open_items) + len(gnd_open)), len(open_items))
        allowed = {k: v for k, v in mine.items() if ripped_count.get(v, 0) < RIP_MAX}
        obstacles = Obstacles(board)
        if hist is None:
            hist = np.zeros((len(SIGNAL_LAYERS), obstacles.grid.ny, obstacles.grid.nx))
        obstacles.grid.hist = hist
        if gtodo:  # GND island: one pad of the island to a new via with a track
            task = gtodo[0]
            gnd_tries[task] = gnd_tries.get(task, 0) + 1
            if gnd_tries[task] > 3:  # guard against endless loops
                gnd_failed.add(task)
                continue
            result = None
            for ref, num in task:
                pad = next(p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber() == num)
                result = connect_gnd(board, obstacles, pad, rippable=allowed, exclude=set(task))
                if result:
                    break
            group, desc = f"GND:{ref}.{num}", f"GND island {', '.join('.'.join(r) for r in task)}"
            fail_key = None
        else:
            u = min(todo, key=order_key)
            desc = " | ".join(i["description"] for i in u["items"])
            result = connect(board, obstacles, *u["items"], rippable=allowed)
            group = None
            fail_key = tuple(sorted(i["uuid"] for i in u["items"]))
        if result:
            text, ripped, new = result
            if group is None:
                group = next(t.GetNetname() for t in board.GetTracks() if t.m_Uuid.AsString() in new) if new else ""
            for uid in new:
                mine[uid] = group

            for n in ripped:
                ripped_count[n] = ripped_count.get(n, 0) + 1
                for uid in [k for k, v in mine.items() if v == n]:
                    del mine[uid]
            if ripped:  # after a rip-up try everything again
                failed, gnd_failed = set(), set()
            pcbnew.SaveBoard(str(pcb), board)
            done += 1
            note("ripped" if ripped else "routed", len(open_items))
            log(f"  routed ({text}): {desc}" + (f"  — ripped up: {', '.join(sorted(ripped))}" if ripped else ""))
        else:
            if fail_key is None:
                gnd_failed.add(task)
            else:
                failed.add(fail_key)
            note("no_path", len(open_items))
            log(f"  no path: {desc}")
    return finish((done, len(todo) + len(gnd_open)), len(todo))


def module_pad_fronts(board, depth):
    """Rectangles (mm) outward in front of the module's signal pads (MODULE_REF), `depth` deep from the pad edge and
    as wide as the pad pitch (0.8 mm), for FANOUT_MODULE_CLEAR."""
    module = board.FindFootprintByReference(MODULE_REF)
    if module is None or depth <= 0:
        return []
    c, out = module.GetPosition(), []
    for pad in module.Pads():
        net = pad.GetNetname()
        if not net or net in SKIP_NETS or net.startswith("unconnected"):
            continue
        q, b = pad.GetPosition(), pad.GetBoundingBox()
        x0, x1, y0, y1 = pcbnew.ToMM(b.GetLeft()), pcbnew.ToMM(b.GetRight()), pcbnew.ToMM(b.GetTop()), pcbnew.ToMM(b.GetBottom())
        qx, qy = pcbnew.ToMM(q.x), pcbnew.ToMM(q.y)
        dx, dy = q.x - c.x, q.y - c.y
        if abs(dx) > abs(dy):  # pad on a long edge left/right: front in x direction
            out.append((x1, qy - 0.4, x1 + depth, qy + 0.4) if dx > 0 else (x0 - depth, qy - 0.4, x0, qy + 0.4))
        else:
            out.append((qx - 0.4, y1, qx + 0.4, y1 + depth) if dy > 0 else (qx - 0.4, y0 - depth, qx + 0.4, y0))
    return out


def gnd_fanout(pcb, net_name="/GND", near=0.9, log=print, only=None, reach=3.0):
    """Every GND SMD pad without its own GND via nearby gets a short track to a via (Dijkstra on the pad's layer
    up to the nearest spot where a via fits). The via reaches the GND layer In1.
    Returns (placed, without space)."""
    board = pcbnew.LoadBoard(str(pcb))
    net = board.FindNet(net_name)
    code = net.GetNetCode()
    done, failed = 0, []
    pads = [p for p in board.GetPads() if p.GetNetCode() == code and p.GetDrillSize().x <= 0
            and (only is None or (p.GetParentFootprint().GetReference(), p.GetNumber()) in only)]
    pads.sort(key=lambda p: (p.GetParentFootprint().GetReference(), p.GetNumber()))
    keep_clear = module_pad_fronts(board, FANOUT_MODULE_CLEAR)
    for pad in pads:
        q = pad.GetPosition()
        if any(t.GetClass() == "PCB_VIA" and t.GetNetCode() == code and (t.GetPosition() - q).EuclideanNorm() < mm(near)
               and pad.HitTest(t.GetPosition(), mm(VIA_D / 2 + 0.6)) for t in board.GetTracks()):
            continue
        layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
        obstacles = Obstacles(board)
        grid = obstacles.grid
        goal = None
        for width in (0.25, W_MIN):  # 0.25 mm if possible, 0.15 mm at bottlenecks
            track, via = obstacles.masks(net, width / 2)
            for xa, ya, xb, yb in keep_clear:  # FANOUT_MODULE_CLEAR, widened by via radius + clearance
                r = VIA_D / 2 + CLEAR
                xa, ya, xb, yb = xa - r, ya - r, xb + r, yb + r
                sl = grid._sel(xa, ya, xb, yb)
                via[sl] |= (grid.X[sl] > xa) & (grid.X[sl] < xb) & (grid.Y[sl] > ya) & (grid.Y[sl] < yb)
            blocked = track[layer]
            start = grid.cell(q)
            dist = {start: 0.0}
            prev = {}
            heap = [(0.0, start)]
            while heap:
                d, c = heapq.heappop(heap)
                if d > dist.get(c, 1e18):
                    continue
                if not via[c]:
                    goal = c
                    break
                if d > reach / GRID:
                    break
                for di, dj, cost in STEPS:
                    n = (c[0] + di, c[1] + dj)
                    if not (0 <= n[0] < grid.ny and 0 <= n[1] < grid.nx) or (blocked[n] and n != start):
                        continue
                    nd = d + cost
                    if nd < dist.get(n, 1e18):
                        dist[n] = nd
                        prev[n] = c
                        heapq.heappush(heap, (nd, n))
            if goal is not None:
                break
        ref = f"{pad.GetParentFootprint().GetReference()}.{pad.GetNumber()}"
        if goal is None:
            failed.append(ref)
            continue
        path = [goal]
        while path[-1] in prev:
            path.append(prev[path[-1]])
        path = simplify([(layer, c) for c in path[::-1]])
        pts = [grid.point(c) for _, c in path]
        pts[0] = q
        for a, b in zip(pts, pts[1:]):
            if a != b:
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(a)
                t.SetEnd(b)
                t.SetLayer(layer)
                t.SetWidth(mm(width))
                t.SetNet(net)
                t.SetLocked(True)
                board.Add(t)
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pts[-1])
        v.SetWidth(mm(VIA_D))
        v.SetDrill(mm(VIA_DRILL))
        v.SetNet(net)
        v.SetLocked(True)
        board.Add(v)
        done += 1
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(pcb), board)
    if failed:
        log(f"  GND via without space: {', '.join(failed)}")
    return done, failed


def gnd_islands(pcb, net_name="/GND", log=print):
    """GND zone islands (F.Cu/B.Cu/In2.Cu) without a via: a track from one of their pads to a via (reach up to
    6 mm). Returns the number of connected islands."""
    board = pcbnew.LoadBoard(str(pcb))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    net = board.FindNet(net_name)
    code = net.GetNetCode()
    vias = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code]
    pads = [p for p in board.GetPads() if p.GetNetCode() == code]
    fixed = 0
    for zone in board.Zones():
        if zone.GetIsRuleArea() or zone.GetNetCode() != code:
            continue
        for layer in (pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
            if not zone.IsOnLayer(layer):
                continue
            polys = zone.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                outline = polys.Outline(i)
                if any(outline.PointInside(v) for v in vias):
                    continue
                if any(p.GetDrillSize().x > 0 and outline.PointInside(p.GetPosition()) for p in pads):
                    continue  # a through-hole pad connects the layers
                inner = [(p.GetParentFootprint().GetReference(), p.GetNumber()) for p in pads
                         if p.IsOnLayer(layer) and outline.PointInside(p.GetPosition())]
                for ref in inner:
                    done, _ = gnd_fanout(pcb, net_name, near=0, log=lambda m: None, only={ref}, reach=6.0)
                    if done:
                        fixed += 1
                        board = pcbnew.LoadBoard(str(pcb))
                        break
                else:
                    if inner:
                        log(f"  GND island without via space: {', '.join('.'.join(r) for r in inner)}")
    return fixed


def open_nets(pcb):
    """Net names of the signal connections still open."""
    nets = set()
    for u in open_connections(pcb):
        for i in u["items"]:
            d = i.get("description", "")
            if "[" in d and "Zone" not in d:
                n = d[d.index("[") + 1:d.index("]")]
                if n not in SKIP_NETS:
                    nets.add(n)
    return nets


def route_all(pcb, restarts=1, log=print, gnd=True, trace=None):
    """Route all signals; if connections stay open, start over and route their nets first (the priority grows with
    each restart). The best result stays in pcb. trace: CSV trace per round (fix()).
    Returns (routed, open)."""
    import shutil
    pcb = Path(pcb)
    start, best_file = pcb.with_suffix(".start"), pcb.with_suffix(".best")
    if GND_FANOUT_FIRST and gnd:
        done, failed = gnd_fanout(pcb, log=log)
        log(f"GND fanout beforehand: {done} vias, without space: {len(failed)}")
    shutil.copy(pcb, start)
    priority, best = [], None
    for k in range(restarts + 1):
        shutil.copy(start, pcb)
        log(f"Run {k + 1}, priority: {', '.join(priority) or '-'}")
        done, still_open = fix(pcb, log=log, priority=tuple(priority), gnd=gnd, trace=trace, trace_label=k + 1)
        log(f"Run {k + 1}: {done} routed, {still_open} open")
        if best is None or still_open < best[1]:
            best = (done, still_open)
            shutil.copy(pcb, best_file)
        if still_open == 0:
            break
        more = sorted(open_nets(pcb) - set(priority))
        if not more:  # only GND islands open: a restart without new priority would give the same
            break
        priority += more
    shutil.copy(best_file, pcb)
    start.unlink()
    best_file.unlink()
    return best


if __name__ == "__main__":
    import os
    import sys
    ORDER = os.environ.get("ORDER", ORDER)
    SEED = int(os.environ.get("SEED", SEED))
    CONN = os.environ.get("CONN", CONN)
    RIP_MAX = int(os.environ.get("RIP_MAX", RIP_MAX))
    VIA_D = float(os.environ.get("VIA_D", VIA_D))

    if len(sys.argv) > 2:
        print(fix(Path(sys.argv[1]), nets=sys.argv[2].split(",") if sys.argv[2] else None,
                  min_len=float(sys.argv[3]) if len(sys.argv) > 3 else 0.0))
    else:
        print(route_all(Path(sys.argv[1])))
