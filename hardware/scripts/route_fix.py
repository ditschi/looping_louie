"""Labyrinth-Router für die 4-Lagen-Hauptplatine (docs/hauptplatine-c6.md Kapitel 11).

Freerouting lässt auf der 4-Lagen-Platine 10–20 Signalverbindungen offen (Kapitel 11.4). Dieses Skript routet
die Verbindungen selbst:

- Grundlage ist die Liste offener Verbindungen aus dem KiCad-DRC (Pad–Pad, Pad–Bahn, Bahn–Bahn).
- Für jede Verbindung sucht ein A* im 0,05-mm-Raster einen Weg über die Signallagen F.Cu, In2.Cu und B.Cu
  (In1 ist die GND-Lage und bleibt frei). Lagenwechsel nur an Stellen, an denen ein Via 0,3/0,5 mm auf allen
  vier Lagen Platz hat (Abstand, Bohrungen, Sperrflächen der Antenne und des Rands).
- Hindernisse werden geometrisch gerastert: fremde Bahnen und Pads mit Abstand 0,15 mm (+ Reserve), Vias,
  Bohrungen mit Loch–Kupfer-Abstand, Sperrflächen ohne Bahnen bzw. ohne Vias.
- Kosten: Länge, Knicke, Vias; Innenlage In2 billiger als die Außenlagen; F.Cu unter dem Funkmodul teuer,
  vor jedem Signal-Randpad des Moduls eine Fluchtgasse, die fremde Netze meiden.
- Aufreißen und neu routen (rip-up and reroute) mit Verlaufskosten nach PathFinder: eigene Bahnen sind weiche
  Hindernisse; nur wenn ein Weg anders nicht geht, werden die störenden Netze entfernt und später neu geroutet.
- Danach GND: Flächeninseln ohne Via bekommen von einem ihrer Pads eine kurze Bahn zu einem Via auf die GND-Lage.
- Bleibt etwas offen, beginnt route_all() von vorn und routet die offenen Netze zuerst.
- Bahnbreite je Netz: VSYS 0,4 mm (Teiler 0,15 mm), BAT_IN 0,4 mm, 3V3 0,25 mm (Engstellen 0,15 mm), sonst 0,15 mm.

Nicht bitgenau wiederholbar: Die Reihenfolge der offenen Verbindungen kommt aus dem KiCad-DRC und hängt von den
(zufälligen) UUIDs neu gebauter Bahnen ab; bei gleich langen Verbindungen entscheidet diese Reihenfolge. Wiederholte
Läufe mit gleichen Kosten streuen deshalb (docs/hauptplatine-c6.md 11.4). Ob das Ergebnis regelkonform ist,
entscheidet am Ende der KiCad-DRC (just drc).

Aufruf: über route.py main-board oder direkt: route_fix.py <platine.kicad_pcb> [netze] [mindestlänge]
"""
import heapq
import json
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pcbnew

GRID = 0.05          # mm
CLEAR = 0.158        # Abstand 0,15 mm + Reserve (Rasterfehler < 0,005 mm)
HOLE_CLEAR = 0.31    # Bauteilbohrung–Kupfer innen 0,3 mm + Reserve
VIA_HOLE_CLEAR = 0.26  # Via-Bohrung–Kupfer 0,25 mm + Reserve
EDGE = 0.32          # Kupfer–Rand 0,3 mm + Reserve
VIA_D, VIA_DRILL = 0.5, 0.3  # wie RULES_4L in gen_main_pcb.py
SKIP_NETS = {"/GND"}  # GND über die Fläche In1 und stitch.py
# VSYS: die Motor-Hauptwege sind in gen_main_pcb.py mit 0,5 mm vorgeroutet; hier nur LDO-Eingang und Teiler
WIDTHS = {"/VSYS": (0.3, 0.2), "/BAT_IN": (0.4,), "/+3V3": (0.25, 0.15)}
# Pads mit µA-Strom in Leistungsnetzen (Spannungsteiler VSYS): dort reicht die Mindestbahn
LOW_CURRENT_PADS = {"Pad 1 [/VSYS] von R6"}
W_MIN = 0.15
VIA_COST = 30        # in Rasterschritten (1,5 mm)
BEND_COST = 2
LAYER_COST = {pcbnew.F_Cu: 1.3, pcbnew.In2_Cu: 1.0, pcbnew.B_Cu: 1.15}
# F.Cu unter dem Funkmodul ist der einzige Ausweg für die Randpads (Abstand zwischen den Pads 0,4 mm, dazwischen
# passt keine Bahn); dort teuer, damit Bahnen nicht längs vor den Pads laufen, sondern bald per Via abtauchen.
MODULE_REF, MODULE_F_COST = "U1", 8.0
# Fluchtgasse vor jedem Signal-Randpad des Moduls (nach innen, Länge in mm): für fremde Netze teuer und ohne Vias
ESCAPE_LEN, ESCAPE_HALF, ESCAPE_COST = 1.4, 0.3, 40.0
# Aufreißen und neu routen: eigene Bahnen fremder Netze sind „weiche“ Hindernisse mit Zusatzkosten; findet der
# Weg nur durch sie hindurch, werden diese Netze entfernt und später neu geroutet (je Netz höchstens RIP_MAX mal).
RIP_COST, RIP_MAX, HIST_COST = 60.0, 10, 10.0
ORDER = "lang"  # lange Verbindungen zuerst (im Versuch am besten: 1 offen statt 14 bei "kurz")
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


class Grid:
    """Raster über die Platine mit Hilfsfunktionen zum Eintragen von Hindernissen."""

    def __init__(self, board):
        box = board.GetBoardEdgesBoundingBox()
        self.x0, self.y0 = pcbnew.ToMM(box.GetLeft()), pcbnew.ToMM(box.GetTop())
        self.nx = int(pcbnew.ToMM(box.GetWidth()) / GRID) + 1
        self.ny = int(pcbnew.ToMM(box.GetHeight()) / GRID) + 1
        xs = self.x0 + np.arange(self.nx) * GRID
        ys = self.y0 + np.arange(self.ny) * GRID
        self.X, self.Y = np.meshgrid(xs, ys)

    def empty(self):
        return np.zeros((self.ny, self.nx), dtype=bool)

    def _sel(self, xa, ya, xb, yb):
        i0 = max(0, int((ya - self.y0) / GRID) - 1)
        i1 = min(self.ny, int((yb - self.y0) / GRID) + 2)
        j0 = max(0, int((xa - self.x0) / GRID) - 1)
        j1 = min(self.nx, int((xb - self.x0) / GRID) + 2)
        return slice(i0, i1), slice(j0, j1)

    def circle(self, m, p, r):
        cx, cy = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
        s = self._sel(cx - r, cy - r, cx + r, cy + r)
        m[s] |= (self.X[s] - cx) ** 2 + (self.Y[s] - cy) ** 2 < r ** 2

    def segment(self, m, a, b, r):
        ax, ay, bx, by = (pcbnew.ToMM(v) for v in (a.x, a.y, b.x, b.y))
        s = self._sel(min(ax, bx) - r, min(ay, by) - r, max(ax, bx) + r, max(ay, by) + r)
        dx, dy = bx - ax, by - ay
        ll = dx * dx + dy * dy
        X, Y = self.X[s], self.Y[s]
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / ll, 0, 1) if ll > 0 else 0
        m[s] |= (X - ax - t * dx) ** 2 + (Y - ay - t * dy) ** 2 < r ** 2

    def polygon(self, m, pts, r):
        """Konvexes oder beliebiges Polygon (Liste (x, y) in mm), um r aufgeweitet: Inneres + Kanten-Schläuche."""
        xs = np.array([p[0] for p in pts])
        ys = np.array([p[1] for p in pts])
        s = self._sel(xs.min() - r, ys.min() - r, xs.max() + r, ys.max() + r)
        X, Y = self.X[s], self.Y[s]
        inside = np.zeros(X.shape, dtype=bool)
        n = len(pts)
        for k in range(n):  # Strahl-Test
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
        m[s] |= near

    def rect(self, m, box, r):
        xa, ya = pcbnew.ToMM(box.GetLeft()) - r, pcbnew.ToMM(box.GetTop()) - r
        xb, yb = pcbnew.ToMM(box.GetRight()) + r, pcbnew.ToMM(box.GetBottom()) + r
        s = self._sel(xa, ya, xb, yb)
        m[s] |= (self.X[s] > xa) & (self.X[s] < xb) & (self.Y[s] > ya) & (self.Y[s] < yb)

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
    """Hindernisse eines Platinenstands; masks() liefert die Sperrraster für ein Netz und eine Bahnbreite."""

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
            self.escapes = []  # (Netzcode, Rechteck in mm)
            for pad in module.Pads():
                if not pad.GetNetname() or pad.GetNetname() == "/GND" or pad.GetNumber() == "49" \
                        or pad.GetNetname().startswith("unconnected"):
                    continue
                q, b = pad.GetPosition(), pad.GetBoundingBox()
                dx, dy = c.x - q.x, c.y - q.y
                x0, x1 = pcbnew.ToMM(b.GetLeft()), pcbnew.ToMM(b.GetRight())
                y0, y1 = pcbnew.ToMM(b.GetTop()), pcbnew.ToMM(b.GetBottom())
                qx, qy = pcbnew.ToMM(q.x), pcbnew.ToMM(q.y)
                if abs(dy) > abs(dx):  # Pad an einer Längskante: Gasse in y-Richtung
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
        """Sperrraster je Signallage für die Mittellinie einer Bahn mit halber Breite `half`, und das
        Via-Raster (True = dort darf kein Via-Mittelpunkt liegen). Elemente in soft_items (UUIDs) landen statt
        dessen in self.soft (je Lage) und self.soft_via."""
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
                if same:  # Lochabstand 0,25 mm zum eigenen Via
                    g.circle(via, p, VIA_DRILL + 0.3)
                    continue
                g.circle(via, p, max(2 * rv + CLEAR, VIA_DRILL / 2 + VIA_HOLE_CLEAR + rv))
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
            if drill.x > 0:  # Bohrung: Loch–Kupfer auf allen Lagen
                r = pcbnew.ToMM(max(drill.x, drill.y)) / 2 + HOLE_CLEAR
                for L in SIGNAL_LAYERS:
                    g.circle(track[L], pad.GetPosition(), r + half)
                g.circle(via, pad.GetPosition(), r + rv)
            if pad.GetNetCode() == code and code != 0:
                if drill.x <= 0:  # kein Via ins eigene SMD-Pad (kein Via-in-Pad)
                    for L in (pcbnew.F_Cu, pcbnew.B_Cu):
                        if pad.IsOnLayer(L):
                            for pts in self._pad_pts(pad, L):
                                g.polygon(via, pts, rv + 0.05)
                continue
            for L in SIGNAL_LAYERS:
                if pad.IsOnLayer(L):
                    for pts in self._pad_pts(pad, L):
                        g.polygon(track[L], pts, CLEAR + half)
            for L in cu_of(pad):
                for pts in self._pad_pts(pad, L):
                    g.polygon(via, pts, max(CLEAR + rv, VIA_DRILL / 2 + VIA_HOLE_CLEAR))
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
        return track, via


def cu_of(pad):
    return [L for L in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if pad.IsOnLayer(L)]


STEPS = [(0, 1, 1.0), (1, 0, 1.0), (0, -1, 1.0), (-1, 0, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414),
         (-1, -1, 1.414)]


def astar(grid, track, via, sources, targets, max_expand=1_000_000, goal_via=False):
    """A* über (Lage, Zeile, Spalte). sources/targets: Liste (Lage, Zelle). Gibt Liste (Lage, Zelle) zurück.
    goal_via=True: kein Ziel, sondern die nächste Stelle auf der Startlage, an der ein Via Platz hat
    (Anbindung eines GND-Pads an die GND-Lage In1)."""
    layers = SIGNAL_LAYERS
    li = {L: k for k, L in enumerate(layers)}
    blocked = np.stack([track[L] for L in layers])
    k = 1
    for L, c in list(sources) + list(targets):  # eigene Anschlusspunkte freigeben
        blocked[li[L], max(0, c[0] - k):c[0] + k + 1, max(0, c[1] - k):c[1] + k + 1] = False
    via_ok = ~via
    tset = {(li[L], c) for L, c in targets}
    tl = list({c for _, c in targets})
    ny, nx = grid.ny, grid.nx

    def h(c):
        if goal_via:
            return 0
        return min(max(abs(c[0] - t[0]), abs(c[1] - t[1])) + 0.414 * min(abs(c[0] - t[0]), abs(c[1] - t[1]))
                   for t in tl)

    cost_l = [LAYER_COST[L] for L in layers]
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
        for kk, (di, dj, cost) in enumerate(STEPS):
            n = (c[0] + di, c[1] + dj)
            if not (0 <= n[0] < ny and 0 <= n[1] < nx) or blocked[l, n[0], n[1]]:
                continue
            ng = g + cost * (extra[n] if l == 0 else cost_l[l]) + (BEND_COST if d not in (-1, kk) else 0) \
                + (RIP_COST if soft[l, n[0], n[1]] else 0) + hist[l, n[0], n[1]]
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
                ng = g + VIA_COST + (RIP_COST if soft_via[c] or soft[l2, c[0], c[1]] else 0)
                ns = (l2, c)
                if ng < best.get(ns, 1e18):
                    best[ns] = ng
                    prev[ns] = s
                    dirs[ns] = -1
                    heapq.heappush(heap, (ng + h(c), ng, ns))
    return None


def end_cells(board, grid, item):
    """Anschlusszellen eines DRC-Elements: (Lage, Zelle)-Liste und Netz."""
    obj = next((o for o in list(board.GetTracks()) + list(board.GetPads()) if o.m_Uuid.AsString() == item["uuid"]),
               None)
    if obj is None:
        return None, None
    if obj.GetClass() == "PAD":
        return [(L, grid.cell(obj.GetPosition())) for L in SIGNAL_LAYERS if obj.IsOnLayer(L)], obj.GetNet()
    if obj.GetClass() == "PCB_VIA":
        return [(L, grid.cell(obj.GetPosition())) for L in SIGNAL_LAYERS], obj.GetNet()
    if obj.GetLayer() not in SIGNAL_LAYERS:
        return None, None
    s, e = obj.GetStart(), obj.GetEnd()
    n = max(1, int((e - s).EuclideanNorm() / mm(0.25)))
    cells = [(obj.GetLayer(), grid.cell(pcbnew.VECTOR2I(int(s.x + (e.x - s.x) * k / n), int(s.y + (e.y - s.y) * k / n))))
             for k in range(n + 1)]  # Punkte entlang der Bahn
    return cells, obj.GetNet()


def simplify(path):
    """Nur Knickpunkte und Lagenwechsel behalten."""
    out = [path[0]]
    for i in range(1, len(path) - 1):
        (l0, a), (l1, b), (l2, c) = path[i - 1], path[i], path[i + 1]
        if l0 != l1 or l1 != l2 or (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            out.append(path[i])
    out.append(path[-1])
    return out


def build(board, grid, net, path, width, start_pt=None, end_pt=None):
    """Bahnen und Vias aus dem Zellweg; erster/letzter Punkt exakt auf den Anschluss (Pad-/Bahnpunkt)."""
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
    """Weg suchen und bauen. rippable: {uuid: Netzname} eigener Bahnen, die aufgerissen werden dürfen.
    Gibt (Beschreibung, aufgerissene Netznamen, neue UUIDs) oder None zurück."""
    grid = obstacles.grid
    src, net = end_cells(board, grid, item_a)
    dst, _ = end_cells(board, grid, item_b)
    if not src or not dst:
        return None
    rippable = rippable or {}
    for soft_items in ({}, rippable):  # erst ohne Aufreißen, dann mit
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
            # Verlauf (PathFinder): umkämpfte Zellen werden für alle teurer, das bricht Pendel-Zyklen
            if ripped and hasattr(grid, "hist"):
                for L, c in conflict:
                    for l in ([SIGNAL_LAYERS.index(L)] if L is not None else range(len(SIGNAL_LAYERS))):
                        grid.hist[l, max(0, c[0] - 3):c[0] + 4, max(0, c[1] - 3):c[1] + 4] += HIST_COST
            return f"{'/'.join(layers)}, {nvias} Vias, {width} mm", ripped, new
    return None


def connect_gnd(board, obstacles, pad, rippable=None, exclude=()):
    """GND-Pad über eine kurze Bahn auf seiner Lage an ein neues Via (In1 ist GND) oder an vorhandenes GND-Kupfer
    (Via, Pad außerhalb von exclude) anbinden. Gibt (Beschreibung, aufgerissene Gruppen, neue UUIDs) oder None."""
    grid = obstacles.grid
    net = pad.GetNet()
    layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    src = [(layer, grid.cell(pad.GetPosition()))]
    code = net.GetNetCode()
    dst = [(layer, grid.cell(t.GetPosition())) for t in board.GetTracks()
           if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code]
    # Ziel nur Vias (sie erreichen die GND-Lage In1) und Durchsteckpads; ein SMD-Pad kann selbst in einer Insel liegen
    dst += [(layer, grid.cell(p.GetPosition())) for p in board.GetPads()
            if p.GetNetCode() == code and p.IsOnLayer(layer) and p.GetDrillSize().x > 0]
    rippable = rippable or {}
    for soft_items in ({}, rippable):
        if soft_items is rippable and not rippable:
            break
        for width in (0.25, W_MIN):
            track, via = obstacles.masks(net, width / 2, soft_items)
            grid.soft, grid.soft_via = obstacles.soft, obstacles.soft_via
            path = astar(grid, track, via, src, dst, max_expand=60_000, goal_via=True)
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
            to_copper = path[-1] in set(dst)
            if not to_copper:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(grid.point(path[-1][1]))
                v.SetWidth(mm(VIA_D))
                v.SetDrill(mm(VIA_DRILL))
                v.SetNet(net)
                v.SetLocked(True)
                board.Add(v)
            new = {t.m_Uuid.AsString() for t in board.GetTracks()} - before
            return f"GND-{'Bahn' if to_copper else 'Via'}, {width} mm", ripped, new
    return None


def gnd_tasks(board, net_name="/GND", near=0.9):
    """GND-SMD-Pads, die ein eigenes Via zur GND-Lage brauchen (nicht schon eines im/am Pad haben)."""
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
    """GND-Flächeninseln ohne Via und ohne Durchsteckpad (nach dem Füllen): je Insel die Pads darin.
    Ein Pad je Insel braucht eine Bahn zu einem Via (connect_gnd)."""
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
    # Pads ohne jede Flächenberührung (z. B. von Bahnen eingeschlossen) zählen einzeln
    return sorted(set(tasks))


def _owners(board, grid, rippable, cells, half):
    """Netze der aufreißbaren Elemente, die an den Zellen (Lage oder None = Via) stören."""
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


def fix(pcb, nets=None, min_len=0.0, max_rounds=300, log=print, priority=(), gnd=False):
    """Offene Signalverbindungen routen (nets: nur diese Netze; min_len: nur Verbindungen ab dieser Länge).
    Gibt (geroutet, noch offen) zurück."""
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

    def order_key(u):
        """Reihenfolge (ORDER): "kurz" = kurze zuerst, "lang" = lange zuerst, "modul" = Randpads des Moduls
        zuerst (nur eine Fluchtgasse), danach kurze."""
        module = any(f"von {MODULE_REF} " in i["description"] for i in u["items"])
        first = not any(f"[{n}]" in i["description"] for n in priority for i in u["items"])
        if ORDER == "lang":
            return (first, -length(u))
        if ORDER == "modul":
            return (first, not module, length(u))
        return (first, length(u))

    todo = []
    mine = {}        # UUID -> Gruppe der hier gebauten Elemente (Netzname bzw. "GND:Ref.Pad"), aufreißbar
    ripped_count = {}
    hist = None
    gnd_failed = set()
    gnd_open = []
    gnd_tries = {}
    # Bahnen von Freerouting (nicht gesperrt) sind ebenfalls aufreißbar, gruppiert nach Netz
    for t in pcbnew.LoadBoard(str(pcb)).GetTracks():
        if not t.IsLocked() and t.GetNetname() not in SKIP_NETS:
            mine[t.m_Uuid.AsString()] = t.GetNetname()
    import shutil
    snap, snap_open = Path(pcb).with_suffix(".fixbest"), None

    def finish(result, signals):
        """Bester Zwischenstand (wenigste offene Signalverbindungen) gewinnt, falls das Ende schlechter ist."""
        if snap_open is not None and snap_open < signals:
            shutil.copy(snap, pcb)
            result = (result[0], snap_open)
            log(f"  bester Zwischenstand übernommen: {snap_open} offen")
        if snap.exists():
            snap.unlink()
        return result

    for _ in range(max_rounds):
        open_items = [u for u in drc_unconnected(pcb) if wanted(u)]
        if snap_open is None or len(open_items) < snap_open:
            snap_open = len(open_items)
            shutil.copy(pcb, snap)
        todo = [u for u in open_items if tuple(sorted(i["uuid"] for i in u["items"])) not in failed]
        board = pcbnew.LoadBoard(str(pcb))
        gtodo = []
        if gnd and not todo:  # erst alle Signale, dann GND-Inseln ohne Via
            gnd_open = island_tasks(board)
            gtodo = [t for t in gnd_open if t not in gnd_failed]
        if not todo and not gtodo:
            if gnd_open:
                log(f"  GND-Inseln ohne Via: {'; '.join(', '.join('.'.join(r) for r in t) for t in gnd_open)}")
            return finish((done, len(open_items) + len(gnd_open)), len(open_items))
        allowed = {k: v for k, v in mine.items() if ripped_count.get(v, 0) < RIP_MAX}
        obstacles = Obstacles(board)
        if hist is None:
            hist = np.zeros((len(SIGNAL_LAYERS), obstacles.grid.ny, obstacles.grid.nx))
        obstacles.grid.hist = hist
        if gtodo:  # GND-Insel: ein Pad der Insel per Bahn an ein neues Via
            task = gtodo[0]
            gnd_tries[task] = gnd_tries.get(task, 0) + 1
            if gnd_tries[task] > 3:  # Schutz gegen Endlosschleifen
                gnd_failed.add(task)
                continue
            result = None
            for ref, num in task:
                pad = next(p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber() == num)
                result = connect_gnd(board, obstacles, pad, rippable=allowed, exclude=set(task))
                if result:
                    break
            group, desc = f"GND:{ref}.{num}", f"GND-Insel {', '.join('.'.join(r) for r in task)}"
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
            if ripped:  # nach dem Aufreißen alles neu versuchen
                failed, gnd_failed = set(), set()
            pcbnew.SaveBoard(str(pcb), board)
            done += 1
            log(f"  geroutet ({text}): {desc}" + (f"  — aufgerissen: {', '.join(sorted(ripped))}" if ripped else ""))
        else:
            if fail_key is None:
                gnd_failed.add(task)
            else:
                failed.add(fail_key)
            log(f"  kein Weg: {desc}")
    return finish((done, len(todo) + len(gnd_open)), len(todo))


def gnd_fanout(pcb, net_name="/GND", near=0.9, log=print, only=None, reach=3.0):
    """Jedes GND-SMD-Pad ohne eigenes GND-Via in der Nähe bekommt eine kurze Bahn zu einem Via (Dijkstra auf
    der Lage des Pads bis zur nächsten Stelle, an der ein Via Platz hat). Das Via erreicht die GND-Lage In1.
    Gibt (gesetzt, ohne Platz) zurück."""
    board = pcbnew.LoadBoard(str(pcb))
    net = board.FindNet(net_name)
    code = net.GetNetCode()
    done, failed = 0, []
    pads = [p for p in board.GetPads() if p.GetNetCode() == code and p.GetDrillSize().x <= 0
            and (only is None or (p.GetParentFootprint().GetReference(), p.GetNumber()) in only)]
    pads.sort(key=lambda p: (p.GetParentFootprint().GetReference(), p.GetNumber()))
    for pad in pads:
        q = pad.GetPosition()
        if any(t.GetClass() == "PCB_VIA" and t.GetNetCode() == code and (t.GetPosition() - q).EuclideanNorm() < mm(near)
               and pad.HitTest(t.GetPosition(), mm(VIA_D / 2 + 0.6)) for t in board.GetTracks()):
            continue
        layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
        obstacles = Obstacles(board)
        grid = obstacles.grid
        goal = None
        for width in (0.25, W_MIN):  # möglichst 0,25 mm, an Engstellen 0,15 mm
            track, via = obstacles.masks(net, width / 2)
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
        log(f"  GND-Via ohne Platz: {', '.join(failed)}")
    return done, failed


def gnd_islands(pcb, net_name="/GND", log=print):
    """GND-Flächeninseln (F.Cu/B.Cu/In2.Cu) ohne Via: von einem ihrer Pads eine Bahn zu einem Via (Reichweite
    bis 6 mm). Gibt die Zahl der angebundenen Inseln zurück."""
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
                    continue  # Durchsteckpad verbindet die Lagen
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
                        log(f"  GND-Insel ohne Via-Platz: {', '.join('.'.join(r) for r in inner)}")
    return fixed


def open_nets(pcb):
    """Netznamen der noch offenen Signalverbindungen."""
    nets = set()
    for u in drc_unconnected(pcb):
        for i in u["items"]:
            d = i.get("description", "")
            if "[" in d and "Zone" not in d:
                n = d[d.index("[") + 1:d.index("]")]
                if n not in SKIP_NETS:
                    nets.add(n)
    return nets


def route_all(pcb, restarts=1, log=print, gnd=True):
    """Alle Signale routen; bleiben Verbindungen offen, von vorn beginnen und deren Netze zuerst routen
    (Vorrang wächst mit jedem Neustart). Das beste Ergebnis bleibt in pcb. Gibt (geroutet, offen) zurück."""
    import shutil
    pcb = Path(pcb)
    start, best_file = pcb.with_suffix(".start"), pcb.with_suffix(".best")
    shutil.copy(pcb, start)
    priority, best = [], None
    for k in range(restarts + 1):
        shutil.copy(start, pcb)
        log(f"Lauf {k + 1}, Vorrang: {', '.join(priority) or '-'}")
        done, still_open = fix(pcb, log=log, priority=tuple(priority), gnd=gnd)
        log(f"Lauf {k + 1}: {done} geroutet, {still_open} offen")
        if best is None or still_open < best[1]:
            best = (done, still_open)
            shutil.copy(pcb, best_file)
        if still_open == 0:
            break
        more = sorted(open_nets(pcb) - set(priority))
        if not more:  # nur GND-Inseln offen: ein Neustart ohne neuen Vorrang ergäbe dasselbe
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
    RIP_MAX = int(os.environ.get("RIP_MAX", RIP_MAX))
    VIA_D = float(os.environ.get("VIA_D", VIA_D))

    if len(sys.argv) > 2:
        print(fix(Path(sys.argv[1]), nets=sys.argv[2].split(",") if sys.argv[2] else None,
                  min_len=float(sys.argv[3]) if len(sys.argv) > 3 else 0.0))
    else:
        print(route_all(Path(sys.argv[1])))
