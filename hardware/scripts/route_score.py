#!/usr/bin/env python3
"""Routing score: hard constraints + weighted sum (docs/routing-score.md).

Measures a routed board (kicad-cli DRC as JSON + pcbnew; zones are refilled only in memory, the file stays
unchanged) and decides between two states:

1. hard constraints ([hard] in hardware/routing-score.toml): whoever violates them is infeasible. Feasible beats
   infeasible; of two infeasible ones the smaller total violation wins (Deb's rule), on a tie the shorter
   under-width current path length.
2. weighted sum of the soft metrics S = Σ weight · value / scale (smaller is better).
3. Threshold and veto: a candidate replaces the official board only if ΔS ≤ −min_improvement and no metric with
   max_regression gets worse by more than that.

Used by route_gate.py (gate, commands score/explain) and route.py (best attempt of an invocation).
Must run with the system Python that contains pcbnew.

Direct usage: route_score.py <board.kicad_pcb> [board]   metrics as JSON
"""
import fnmatch
import hashlib
import heapq
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG = ROOT / "hardware" / "routing-score.toml"
# increase when the computation of a metric changes: the gate then measures the official board again
METRICS_VERSION = 1
NM = 1e6
LIB_CHECKS = {"lib_footprint_issues", "lib_footprint_mismatch"}
STEP = 0.1  # mm, sampling step along the tracks
ROBUST_SAMPLES = 2000


def mm(v):
    return v / NM


# --- Configuration --------------------------------------------------------------------------------------------------

def load_config(board=None, path=None):
    """Load the TOML; [boards.<board>] overrides the general sections (nets, antenna, via_in_pad, paths …)."""
    path = Path(path) if path else CONFIG
    cfg = tomllib.loads(path.read_text())
    per_board = cfg.pop("boards", {})
    if board and board in per_board:
        for key, value in per_board[board].items():
            if isinstance(value, dict) and isinstance(cfg.get(key), dict):
                cfg[key] = {**cfg[key], **value}
            else:
                cfg[key] = value
    cfg.setdefault("paths", [])
    return cfg


def config_hash(path=None):
    return hashlib.sha256(Path(path or CONFIG).read_bytes()).hexdigest()


# --- DRC ------------------------------------------------------------------------------------------------------------

def run_drc(pcb, extra_rule=None):
    """kicad-cli DRC (JSON, all severities) of a copy including .kicad_pro/.kicad_dru; extra_rule is appended to the
    rules file."""
    pcb = Path(pcb)
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / pcb.name
        shutil.copy(pcb, copy)
        for suf in (".kicad_pro", ".kicad_dru"):
            if pcb.with_suffix(suf).exists():
                shutil.copy(pcb.with_suffix(suf), copy.with_suffix(suf))
        if extra_rule:
            dru = copy.with_suffix(".kicad_dru")
            text = dru.read_text() if dru.exists() else "(version 1)\n"
            dru.write_text(text + "\n" + extra_rule + "\n")
        out = Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "-o", str(out),
                        str(copy)], capture_output=True)
        return json.loads(out.read_text())


# --- Geometry -------------------------------------------------------------------------------------------------------

def seg_point_dist(px, py, ax, ay, bx, by):
    """Distance of many points (px, py) to many segments (a, b) → matrix [points, segments]."""
    dx, dy = bx - ax, by - ay
    ll = dx * dx + dy * dy
    ll = np.where(ll == 0, 1e-12, ll)
    t = ((px[:, None] - ax[None]) * dx[None] + (py[:, None] - ay[None]) * dy[None]) / ll[None]
    t = np.clip(t, 0, 1)
    qx, qy = ax[None] + t * dx[None], ay[None] + t * dy[None]
    return np.hypot(px[:, None] - qx, py[:, None] - qy)


def point_seg(x, y, s):
    return float(seg_point_dist(np.array([x]), np.array([y]), np.array([s["a"][0]]), np.array([s["a"][1]]),
                                np.array([s["b"][0]]), np.array([s["b"][1]]))[0, 0])


def samples(seg):
    (ax, ay), (bx, by) = seg["a"], seg["b"]
    n = max(1, int(math.ceil(seg["len"] / STEP)))
    t = (np.arange(n) + 0.5) / n
    return ax + t * (bx - ax), ay + t * (by - ay), seg["len"] / n


def octi(a, b):
    """45° distance (octilinear)."""
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


def mst_length(points, metric=octi):
    if len(points) < 2:
        return 0.0
    total = 0.0
    best = {i: metric(points[0], points[i]) for i in range(1, len(points))}
    while best:
        i = min(best, key=best.get)
        total += best.pop(i)
        for j in best:
            best[j] = min(best[j], metric(points[i], points[j]))
    return total


# --- Board model ----------------------------------------------------------------------------------------------------

class Board:
    def __init__(self, path):
        import pcbnew
        self.pcbnew = pcbnew
        self.board = b = pcbnew.LoadBoard(str(path))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        self.cu = list(b.GetEnabledLayers().CuStack())  # order F.Cu, In1, …, B.Cu
        self.name = {l: b.GetLayerName(l) for l in self.cu}
        self.segs, self.vias = [], []
        for t in b.GetTracks():
            net = str(t.GetNetname())
            if t.GetClass() == "PCB_VIA":
                try:
                    d = t.GetWidth(pcbnew.F_Cu)
                except TypeError:
                    d = t.GetWidth()
                self.vias.append(dict(net=net, p=(mm(t.GetPosition().x), mm(t.GetPosition().y)), d=mm(d),
                                      drill=mm(t.GetDrillValue()), item=t))
            else:
                a, e = t.GetStart(), t.GetEnd()
                self.segs.append(dict(net=net, layer=t.GetLayer(), a=(mm(a.x), mm(a.y)), b=(mm(e.x), mm(e.y)),
                                      w=mm(t.GetWidth()), len=mm(t.GetLength()), item=t))
        self.pads = []
        for fp in b.GetFootprints():
            for p in fp.Pads():
                self.pads.append(dict(ref=fp.GetReference(), num=p.GetNumber(), net=str(p.GetNetname()),
                                      p=(mm(p.GetPosition().x), mm(p.GetPosition().y)),
                                      smd=p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD,
                                      tht=p.GetDrillSize().x > 0, item=p))
        self.zones = [z for z in b.Zones() if not z.GetIsRuleArea()]
        self.rule_areas = [z for z in b.Zones() if z.GetIsRuleArea()]
        bb = b.GetBoardEdgesBoundingBox()
        self.bbox = (mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetRight()), mm(bb.GetBottom()))
        self.board_thickness = mm(b.GetDesignSettings().GetBoardThickness())
        self.thickness = self._copper_thickness()

    def _copper_thickness(self):
        pcbnew = self.pcbnew
        out = {l: 0.035 for l in self.cu}
        try:
            stack = self.board.GetDesignSettings().GetStackupDescriptor()
            for item in stack.GetList():
                if item.GetType() == pcbnew.BS_ITEM_TYPE_COPPER and item.GetThickness() > 0:
                    out[item.GetBrdLayerId()] = mm(item.GetThickness())
        except Exception:
            pass
        return out

    def gnd_fill(self, gnd, layer):
        return [z.GetFilledPolysList(layer) for z in self.zones if str(z.GetNetname()) == gnd and z.IsOnLayer(layer)]

    def pad(self, spec):
        ref, num = spec.split(":")
        return next((p for p in self.pads if p["ref"] == ref and p["num"] == num), None)

    def vec(self, x, y):
        return self.pcbnew.VECTOR2I(int(x * NM), int(y * NM))


def inside(B, polys, x, y):
    v = B.vec(x, y)
    return any(p.Contains(v) for p in polys)


# --- Metrics --------------------------------------------------------------------------------------------------------

def gnd_islands(B, gnd):
    """GND fill pieces without via and without through-hole pad (like the former route_gate.gnd_islands)."""
    vias = [v["item"].GetPosition() for v in B.vias if v["net"] == gnd]
    tht = [p["item"].GetPosition() for p in B.pads if p["net"] == gnd and p["tht"]]
    count = 0
    for z in B.zones:
        if str(z.GetNetname()) != gnd:
            continue
        for layer in z.GetLayerSet().CuStack():
            polys = z.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                if not any(polys.Outline(i).PointInside(v) for v in vias + tht):
                    count += 1
    return count


def angles(B, gnd):
    """Bends, acute angles (< 90°) and folded-back tracks per net/layer (tracks of the same net at a common
    end point)."""
    ends = defaultdict(list)
    for s in B.segs:
        if s["net"] == gnd or s["len"] < 1e-4:
            continue
        for p, q in ((s["a"], s["b"]), (s["b"], s["a"])):
            ends[(s["net"], s["layer"], round(p[0], 3), round(p[1], 3))].append((q[0] - p[0], q[1] - p[1]))
    bends = acute = overlaps = 0
    for vecs in ends.values():
        for i in range(len(vecs)):
            for j in range(i + 1, len(vecs)):
                (ax, ay), (bx, by) = vecs[i], vecs[j]
                c = (ax * bx + ay * by) / (math.hypot(ax, ay) * math.hypot(bx, by))
                ang = math.degrees(math.acos(max(-1, min(1, c))))
                if len(vecs) == 2 and ang < 179:
                    bends += 1
                if ang < 1:
                    overlaps += 1
                elif ang < 89.5:
                    acute += 1
    return bends, acute, overlaps


def detour(B, zone_nets):
    """Detour per net: routed length / octilinear minimum spanning tree of the pads."""
    per_net = {}
    length = defaultdict(float)
    for s in B.segs:
        length[s["net"]] += s["len"]
    pads = defaultdict(list)
    for p in B.pads:
        pads[p["net"]].append(p["p"])
    for net, pts in pads.items():
        if net in zone_nets or not net or net.startswith("unconnected") or len(pts) < 2 or length[net] == 0:
            continue
        ideal = mst_length(pts)
        if ideal > 0.5:
            per_net[net] = (round(length[net] / ideal, 3), ideal)
    worst = sorted(((k, v[0]) for k, v in per_net.items()), key=lambda kv: -kv[1])[:5]
    return per_net, worst


def plane_layers(B, gnd):
    """Layers without tracks with GND fill (4 layers: In1)."""
    used = {s["layer"] for s in B.segs}
    return [l for l in B.cu if l not in used and B.gnd_fill(gnd, l)]


def coupled_layers(B, planes):
    """Layer pairs that couple: same layer or no plane in between."""
    idx = {l: i for i, l in enumerate(B.cu)}
    pairs = set()
    for a in B.cu:
        for b in B.cu:
            lo, hi = sorted((idx[a], idx[b]))
            if not any(lo < idx[p] < hi for p in planes) and a not in planes and b not in planes:
                pairs.add((a, b))
    return pairs


def sense_coupling(B, cfg, planes):
    nets = cfg["nets"]
    pairs = coupled_layers(B, planes)
    gap = nets["coupling_gap_mm"]
    agg = [s for s in B.segs if s["net"] in nets["aggressors"]]
    total, per = 0.0, defaultdict(float)
    for s in B.segs:
        if s["net"] not in nets["sense"]:
            continue
        cand = [a for a in agg if (s["layer"], a["layer"]) in pairs]
        if not cand:
            continue
        px, py, dl = samples(s)
        ax = np.array([a["a"][0] for a in cand]); ay = np.array([a["a"][1] for a in cand])  # noqa: E702
        bx = np.array([a["b"][0] for a in cand]); by = np.array([a["b"][1] for a in cand])  # noqa: E702
        hw = np.array([a["w"] / 2 for a in cand])
        d = seg_point_dist(px, py, ax, ay, bx, by) - hw[None] - s["w"] / 2
        hit = (d.min(axis=1) < gap).sum() * dl
        total += hit
        per[s["net"]] += hit
    return round(total, 2), {k: round(v, 2) for k, v in per.items()}


def return_gaps(B, gnd, power, planes):
    """Signal track length without GND reference: with a plane, the nearest plane below the point must be filled;
    without a plane (2 layers), an adjacent layer. The antipad of the track's own via does not count."""
    fills = {l: B.gnd_fill(gnd, l) for l in B.cu}
    idx = {l: i for i, l in enumerate(B.cu)}
    total, per = 0.0, defaultdict(float)
    for s in B.segs:
        if s["net"] == gnd or s["net"] in power:
            continue
        i = idx[s["layer"]]
        if planes:
            neigh = [min(planes, key=lambda p: abs(idx[p] - i))]
        else:
            neigh = [B.cu[j] for j in (i - 1, i + 1) if 0 <= j < len(B.cu)]
        px, py, dl = samples(s)
        own = [(v["p"], v["d"] / 2 + 0.25) for v in B.vias if v["net"] == s["net"]]
        for x, y in zip(px, py):
            if any(math.hypot(x - q[0], y - q[1]) < r for q, r in own):
                continue
            if not any(inside(B, fills[l], x, y) for l in neigh):
                total += dl
                per[s["net"]] += dl
    worst = sorted(per.items(), key=lambda kv: -kv[1])[:5]
    return round(total, 2), [(k, round(v, 2)) for k, v in worst]


def usb(B, cfg):
    pair = cfg["nets"].get("usb_pair") or []
    if len(pair) != 2:
        return {}
    dp, dm = pair
    ln = {n: sum(s["len"] for s in B.segs if s["net"] == n) for n in (dp, dm)}
    vias = sum(1 for v in B.vias if v["net"] in (dp, dm))
    stubs = 0  # open track ends: touch neither a track of the same net nor a via nor a pad
    for n in (dp, dm):
        segs = [s for s in B.segs if s["net"] == n]
        ends = defaultdict(int)
        for s in segs:
            for p in (s["a"], s["b"]):
                ends[(s["layer"], round(p[0], 3), round(p[1], 3))] += 1
        for (layer, x, y), k in ends.items():
            if k > 1:
                continue
            v = B.vec(x, y)
            on_pad = any(p["net"] == n and p["item"].IsOnLayer(layer) and p["item"].HitTest(v) for p in B.pads)
            on_via = any(o["net"] == n and math.hypot(o["p"][0] - x, o["p"][1] - y) < o["d"] / 2 for o in B.vias)
            on_seg = any(s["layer"] == layer and point_seg(x, y, s) < s["w"] / 2 - 1e-3
                         and (round(s["a"][0], 3), round(s["a"][1], 3)) != (x, y)
                         and (round(s["b"][0], 3), round(s["b"][1], 3)) != (x, y) for s in segs)
            if not (on_pad or on_via or on_seg):
                stubs += 1
    return dict(usb_len_dp=round(ln[dp], 2), usb_len_dm=round(ln[dm], 2), usb_skew_mm=round(abs(ln[dp] - ln[dm]), 2),
                usb_vias=vias, usb_stubs=stubs)


def antenna(B, cfg, gnd):
    acfg = cfg["antenna"]
    areas = [z for z in B.rule_areas if z.GetZoneName().startswith((acfg["area_prefix"], "Antenne"))]  # "Antenne": name before 2026-11-08
    rects = []
    for z in areas:
        bb = z.GetBoundingBox()
        rects.append((mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetRight()), mm(bb.GetBottom())))
    intr, prox = 0, 0.0
    if not areas:
        return 0, 0.0, 0.0
    for s in B.segs:
        if s["net"] in acfg["allowed_nets"]:
            continue
        px, py, dl = samples(s)
        for x, y in zip(px, py):
            if any(z.Outline().Contains(B.vec(x, y)) and z.IsOnLayer(s["layer"]) for z in areas):
                intr += 1
                break
        if s["net"] == gnd:
            continue
        for x, y in zip(px, py):
            d = min(math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - y, 0, y - r[3])) for r in rects)
            if 0 < d < acfg["margin_mm"]:
                prox += dl
    for v in B.vias:
        if v["net"] in acfg["allowed_nets"]:
            continue
        if any(z.Outline().Contains(v["item"].GetPosition()) for z in areas):
            intr += 1
    fill = 0.0
    for z in B.zones:
        for l in z.GetLayerSet().CuStack():
            polys = z.GetFilledPolysList(l)
            for a in areas:
                if a.IsOnLayer(l):
                    o = B.pcbnew.SHAPE_POLY_SET(polys)
                    o.BooleanIntersection(a.Outline())
                    fill += mm(mm(o.Area()))
    if fill > 0.01:
        intr += 1
    return intr, round(prox, 2), round(fill, 3)


def via_in_pad(B, cfg):
    allowed = cfg["via_in_pad"]["allowed"]
    bad = []
    for v in B.vias:
        for p in B.pads:
            if p["smd"] and p["item"].HitTest(v["item"].GetPosition()):
                tag = f"{p['ref']}:{p['num']}"
                if not any(fnmatch.fnmatch(tag, a) for a in allowed):
                    bad.append(tag)
    return bad


def stitching(B, gnd):
    """95th percentile and maximum of the distance from GND fill on the outer layers (0.25 mm grid) to the nearest
    GND via/through-hole pad."""
    gv = np.array([v["p"] for v in B.vias if v["net"] == gnd] +
                  [p["p"] for p in B.pads if p["net"] == gnd and p["tht"]])
    pts = []
    x0, y0, x1, y1 = B.bbox
    for l in (B.cu[0], B.cu[-1]):
        fills = B.gnd_fill(gnd, l)
        for x in np.arange(x0 + 0.125, x1, 0.25):
            for y in np.arange(y0 + 0.125, y1, 0.25):
                if inside(B, fills, x, y):
                    pts.append((x, y))
    pts = np.array(pts)
    if len(pts) == 0 or len(gv) == 0:
        return None, None
    d = np.hypot(pts[:, None, 0] - gv[None, :, 0], pts[:, None, 1] - gv[None, :, 1]).min(axis=1)
    return round(float(np.percentile(d, 95)), 2), round(float(d.max()), 2)


def footprint_box(B, ref, margin):
    fp = B.board.FindFootprintByReference(ref)
    if fp is None:
        return None
    bb = fp.GetBoundingBox(False)
    return (mm(bb.GetX()) - margin, mm(bb.GetY()) - margin, mm(bb.GetRight()) + margin, mm(bb.GetBottom()) + margin)


def vias_in_box(B, gnd, box):
    if box is None:
        return None
    x0, y0, x1, y1 = box
    return sum(1 for v in B.vias if v["net"] == gnd and x0 <= v["p"][0] <= x1 and y0 <= v["p"][1] <= y1)


def thermal_vias(B, gnd, spec, margin=0.5):
    p = B.pad(spec) if spec else None
    if p is None:
        return None
    bb = p["item"].GetBoundingBox()
    return vias_in_box(B, gnd, (mm(bb.GetX()) - margin, mm(bb.GetY()) - margin,
                                mm(bb.GetRight()) + margin, mm(bb.GetBottom()) + margin))


# --- Current paths --------------------------------------------------------------------------------------------------

def ipc_width(i, dt, k, t_mm):
    """Minimum width (mm) per IPC-2221: I = k · ΔT^0.44 · A^0.725 (A in mil²)."""
    area_mil2 = (i / (k * dt ** 0.44)) ** (1 / 0.725)
    return area_mil2 / (t_mm / 0.0254) * 0.0254


def power_paths(B, cfg):
    """For each path (pad → pad, same net) the route with the lowest resistance through tracks and vias (Dijkstra);
    width against IPC-2221 (current_a), voltage drop at peak_a."""
    th = cfg["thermal"]
    rho = th["resistivity_ohm_m"]
    results = []
    for path in cfg.get("paths", []):
        a, b = B.pad(path["from"]), B.pad(path["to"])
        if a is None or b is None:
            results.append(dict(name=path["name"], connected=False, violation=True, missing=True))
            continue
        net = a["net"]
        nodes = ([("s", s) for s in B.segs if s["net"] == net] + [("v", v) for v in B.vias if v["net"] == net]
                 + [("p", p) for p in B.pads if p["net"] == net])

        def cost(kind, o):
            if kind == "s":
                return rho * o["len"] * 1e-3 / (o["w"] * 1e-3 * B.thickness[o["layer"]] * 1e-3)
            if kind == "v":
                return rho * B.board_thickness * 1e-3 / (math.pi * o["drill"] * 1e-3 * th["via_plating_um"] * 1e-6)
            return 0.0

        def touch(n1, n2):
            (k1, o1), (k2, o2) = sorted((n1, n2), key=lambda n: "psv".index(n[0]))
            if k1 == "p" and k2 == "p":
                return False
            if k1 == "s" and k2 == "s":
                if o1["layer"] != o2["layer"]:
                    return False
                return any(point_seg(e[0], e[1], q) <= q["w"] / 2 + 1e-3
                           for p, q in ((o1, o2), (o2, o1)) for e in (p["a"], p["b"]))
            if k1 == "s" and k2 == "v":
                return point_seg(o2["p"][0], o2["p"][1], o1) <= o2["d"] / 2 + o1["w"] / 2
            if k1 == "p" and k2 == "s":
                if not o1["item"].IsOnLayer(o2["layer"]):
                    return False
                return any(o1["item"].HitTest(B.vec(*e), int(o2["w"] / 2 * NM)) for e in (o2["a"], o2["b"]))
            if k1 == "p" and k2 == "v":
                return o1["item"].HitTest(o2["item"].GetPosition(), int(o2["d"] / 2 * NM))
            return False

        adj = defaultdict(list)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if touch(nodes[i], nodes[j]):
                    adj[i].append(j)
                    adj[j].append(i)
        start = next(i for i, n in enumerate(nodes) if n[0] == "p" and n[1] is a)
        goal = next(i for i, n in enumerate(nodes) if n[0] == "p" and n[1] is b)
        dist, prev = {start: 0.0}, {}
        heap = [(0.0, start)]
        while heap:
            d, i = heapq.heappop(heap)
            if i == goal:
                break
            if d > dist.get(i, 1e9):
                continue
            for j in adj[i]:
                nd = d + cost(*nodes[j])
                if nd < dist.get(j, 1e9):
                    dist[j], prev[j] = nd, i
                    heapq.heappush(heap, (nd, j))
        if goal not in dist:
            results.append(dict(name=path["name"], connected=False, violation=True))
            continue
        chain, i = [], goal
        while i != start:
            chain.append(nodes[i])
            i = prev[i]
        under, minw, nvia, length, inner = 0.0, 1e9, 0, 0.0, 0.0
        for kind, o in chain:
            if kind == "s":
                ext = o["layer"] in (B.cu[0], B.cu[-1])
                need = ipc_width(path["current_a"], th["copper_rise_k"],
                                 th["ipc_k_external"] if ext else th["ipc_k_internal"], B.thickness[o["layer"]])
                length += o["len"]
                minw = min(minw, o["w"])
                inner += 0 if ext else o["len"]
                if o["w"] < need - 1e-6:
                    under += o["len"]
            elif kind == "v":
                nvia += 1
        r = dist[goal]
        results.append(dict(name=path["name"], connected=True, r_mohm=round(r * 1e3, 1),
                            drop_mv=round(r * path["peak_a"] * 1e3, 1), length_mm=round(length, 2),
                            inner_mm=round(inner, 2), min_width_mm=round(minw, 3), vias=nvia,
                            under_width_mm=round(under, 2), violation=under > th["neckdown_allow_mm"]))
    return results


# --- Measurement ----------------------------------------------------------------------------------------------------

def measure_all(pcb, cfg, project=None):
    """All metrics of a board → (metrics, details). project: .kicad_pro whose rules (including .kicad_dru) should
    apply; if the board is not next to it, it is copied into a temporary directory for this."""
    pcb = Path(pcb)
    project = Path(project) if project else pcb.with_suffix(".kicad_pro")
    if project.resolve() != pcb.with_suffix(".kicad_pro").resolve():
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / f"{project.stem}.kicad_pcb"
            shutil.copy(pcb, copy)
            for f in (project, project.with_suffix(".kicad_dru")):
                if f.exists():
                    shutil.copy(f, Path(tmp) / f.name)
            return measure_all(copy, cfg)
    nets = cfg["nets"]
    gnd = nets["gnd"]
    drc = run_drc(pcb)
    viol = [v for v in drc["violations"] if v["type"] not in LIB_CHECKS]
    B = Board(pcb)
    clearance = mm(B.board.GetDesignSettings().m_MinClearance)
    margin_rule = (f'(rule "score_margin"\n  (condition "A.Type != \'Zone\' && B.Type != \'Zone\' && '
                   f'!(A.Type == \'Pad\' && B.Type == \'Pad\')")\n'
                   f'  (constraint clearance (min {clearance + nets["clearance_margin_mm"]:.3f}mm)))')
    # The involved items (track, via, pad) are counted, not the reported pairs: which pairs the DRC reports varies
    # from run to run by a few percent (KiCad 9.0.8, multiple threads), the items do not.
    tight = len({i["uuid"] for v in run_drc(pcb, margin_rule)["violations"] if v["type"] == "clearance"
                 for i in v["items"]})
    power = set(nets["power"])
    planes = plane_layers(B, gnd)
    zone_nets = {str(z.GetNetname()) for z in B.zones}
    per_net, worst = detour(B, zone_nets)
    bends, acute, overlaps = angles(B, gnd)
    coupling, coupling_per = sense_coupling(B, cfg, planes)
    gaps, gaps_worst = return_gaps(B, gnd, power, planes)
    intr, prox, ant_fill = antenna(B, cfg, gnd)
    vip = via_in_pad(B, cfg)
    p95, pmax = stitching(B, gnd)
    paths = power_paths(B, cfg)
    ref_area = sum(mm(mm(p.Area())) for p in B.gnd_fill(gnd, planes[0])) if planes else 0.0
    module = cfg.get("module", {})
    ideal = sum(v[1] for v in per_net.values())
    errors = sum(1 for v in viol if v["severity"] == "error")
    m = {
        # metrics of the former lexicographic gate (short line, file names, old routing.json)
        "drc_violations": len(viol),
        "via_count": len(B.vias),
        "track_length_mm": round(sum(s["len"] for s in B.segs), 2),
        # hard constraints
        "drc_errors": errors,
        "unconnected": len(drc["unconnected_items"]),
        "antenna_intrusions": intr,
        "power_width_violations": sum(1 for p in paths if p["violation"]),
        # soft metrics
        "drc_warnings": len(viol) - errors,
        "gnd_islands": gnd_islands(B, gnd),
        "signal_vias": sum(1 for v in B.vias if v["net"] != gnd),
        "gnd_vias": sum(1 for v in B.vias if v["net"] == gnd),
        "signal_length_mm": round(sum(s["len"] for s in B.segs if s["net"] != gnd), 2),
        "detour_total": round(sum(s["len"] for s in B.segs if s["net"] in per_net) / max(1e-9, ideal), 3),
        "detour_worst5": round(sum(v for _, v in worst) / max(1, len(worst)), 3),
        "bends": bends,
        "acute_angles": acute,
        "overlapping_segments": overlaps,
        "tight_clearance": tight,
        "power_drop_mv": max((p.get("drop_mv", 0) for p in paths), default=0),
        "sense_coupling_mm": coupling,
        "sense_length_mm": round(sum(s["len"] for s in B.segs if s["net"] in nets["sense"]), 2),
        "return_gap_mm": gaps,
        "antenna_proximity_mm": prox,
        "via_in_pad": len(vip),
        "stitch_gap_p95_mm": p95,
        "stitch_gap_max_mm": pmax,
        "gnd_vias_module": vias_in_box(B, gnd, footprint_box(B, module["ref"], module.get("margin_mm", 1.0)))
        if module.get("ref") else None,
        "thermal_vias": thermal_vias(B, gnd, module.get("thermal_pad")),
        "ref_plane_mm2": round(ref_area, 1),
        "layer_length_mm": {B.name[l]: round(sum(s["len"] for s in B.segs if s["layer"] == l), 1) for l in B.cu},
    }
    m.update(usb(B, cfg))
    details = {"paths": paths, "detour_worst": worst, "coupling_per_net": coupling_per,
               "return_gap_worst": gaps_worst, "via_in_pad": vip, "antenna_fill_mm2": ant_fill,
               "plane_layers": [B.name[l] for l in planes],
               "drc_types": sorted({v["type"] for v in viol}), "clearance_mm": clearance}
    return m, details


# --- Evaluation and decision ----------------------------------------------------------------------------------------

def evaluate(cfg, metrics, details=None):
    """→ dict(hard={metric: excess}, hard_total, under_mm, S, parts)."""
    details = details or {}
    hard = {k: max(0, metrics[k] - lim) for k, lim in cfg["hard"].items() if metrics.get(k) is not None}
    under = sum(p.get("under_width_mm", 0) for p in details.get("paths", []) if p.get("violation"))
    parts = {}
    for k, s in cfg["soft"].items():
        v = metrics.get(k)
        if v is None or s["weight"] == 0:
            continue
        parts[k] = s["weight"] * v / s["scale"]
    return dict(hard={k: v for k, v in hard.items() if v}, hard_total=sum(hard.values()), under_mm=round(under, 2),
                S=round(sum(parts.values()), 3), parts={k: round(v, 4) for k, v in parts.items()})


def rank_key(cfg, metrics, details=None):
    """Sort key (smaller is better) for the best attempt of an invocation: first feasible, then smallest violation
    (count, then under-width length), then smallest S."""
    e = evaluate(cfg, metrics, details)
    return (e["hard_total"], e["under_mm"], e["S"])


def _vetoes(cfg, cand, base):
    out = []
    for k, s in cfg["soft"].items():
        if "max_regression" in s and cand.get(k) is not None and base.get(k) is not None:
            if cand[k] - base[k] > s["max_regression"]:
                out.append(f"{k} +{cand[k] - base[k]:.2f} > {s['max_regression']}")
    return out


def decide(cfg, cand, official):
    """cand/official: dict(metrics=…, details=…). → (accept, reason, drivers). drivers: the two largest contributions
    to ΔS as text."""
    T = cfg["decision"]["min_improvement"]
    ec, eo = evaluate(cfg, cand["metrics"], cand.get("details")), evaluate(cfg, official["metrics"],
                                                                          official.get("details"))
    dS = ec["S"] - eo["S"]
    diffs = {k: ec["parts"].get(k, 0) - eo["parts"].get(k, 0) for k in set(ec["parts"]) | set(eo["parts"])}
    top = sorted(diffs.items(), key=lambda kv: -abs(kv[1]))[:2]
    drivers = " / ".join(f"{k} {v:+.1f}" for k, v in top if abs(v) >= 0.005) or "no differences"
    hc, ho = ec["hard_total"], eo["hard_total"]
    if ho == 0 and hc > 0:
        return False, f"hard constraint violated ({', '.join(ec['hard'])}), official board feasible", drivers
    if ho > 0 and hc == 0:
        return True, f"feasible, official board violates {', '.join(eo['hard'])}", drivers
    if ho > 0 and (hc, round(ec["under_mm"], 1)) != (ho, round(eo["under_mm"], 1)):
        better = (hc, ec["under_mm"]) < (ho, eo["under_mm"])
        return better, (f"both infeasible, violation {hc}/{ec['under_mm']:.1f} mm vs. {ho}/{eo['under_mm']:.1f} mm "
                        f"({'smaller' if better else 'larger'})"), drivers
    vetoes = _vetoes(cfg, cand["metrics"], official["metrics"])
    if vetoes:
        return False, "Veto: " + ", ".join(vetoes), drivers
    if dS <= -T:
        return True, f"ΔS {dS:+.2f} ≤ −{T:g}", drivers
    return False, f"ΔS {dS:+.2f} > −{T:g} (not better by the threshold)", drivers


def dominates(cfg, a, b):
    keys = [k for k, s in cfg["soft"].items() if s["weight"] != 0 and a.get(k) is not None and b.get(k) is not None]
    sign = {k: 1 if cfg["soft"][k]["weight"] > 0 else -1 for k in keys}
    return (all(sign[k] * a[k] <= sign[k] * b[k] for k in keys)
            and any(sign[k] * a[k] < sign[k] * b[k] for k in keys))


def fmt(v):
    if isinstance(v, float):
        return f"{v:.4g}" if abs(v) < 1000 else f"{v:.1f}"
    return str(v)


def table(cfg, boards):
    """boards: list of (name, dict(metrics, details)); the first one is the baseline for ΔS."""
    base = evaluate(cfg, boards[0][1]["metrics"], boards[0][1].get("details"))
    lines = [f"{'board':34} {'hard':>4} {'under_mm':>8} {'S':>8} {'dS':>7}  {'vias':>4} {'len_mm':>7}"]
    for name, b in boards:
        e = evaluate(cfg, b["metrics"], b.get("details"))
        m = b["metrics"]
        lines.append(f"{name[:34]:34} {e['hard_total']:>4} {e['under_mm']:>8.1f} {e['S']:>8.2f} "
                     f"{e['S'] - base['S']:>+7.2f}  {m.get('via_count', '?'):>4} {m.get('track_length_mm', 0):>7.1f}"
                     + ("   hard: " + ", ".join(f"{k}={v}" for k, v in e["hard"].items()) if e["hard"] else ""))
    return lines


def pareto(cfg, boards):
    lines = ["Pareto (soft metrics with weight ≠ 0):"]
    for name, b in boards:
        dom = [n for n, o in boards if n != name and dominates(cfg, o["metrics"], b["metrics"])]
        lines.append(f"  {name[:34]:34} " + (f"dominated by {', '.join(dom)}" if dom else "not dominated"))
    return lines


def explain(cfg, cand_name, cand, base_name, official):
    """Contribution table, flip factor per metric, robustness against random weights, paths (list of lines)."""
    T = cfg["decision"]["min_improvement"]
    accept, why, _ = decide(cfg, cand, official)
    ec, eo = evaluate(cfg, cand["metrics"], cand.get("details")), evaluate(cfg, official["metrics"],
                                                                          official.get("details"))
    dS = ec["S"] - eo["S"]
    lines = [f"=== {cand_name} vs. {base_name}: {'ACCEPT' if accept else 'REJECT'} ({why})"]
    if eo["hard_total"] or ec["hard_total"]:
        lines.append(f"  hard stage: official {eo['hard'] or 'feasible'} (too narrow {eo['under_mm']} mm), "
                     f"candidate {ec['hard'] or 'feasible'} (too narrow {ec['under_mm']} mm)")
    rows = []
    for k in sorted(set(ec["parts"]) | set(eo["parts"])):
        c = ec["parts"].get(k, 0) - eo["parts"].get(k, 0)
        rows.append((k, official["metrics"].get(k), cand["metrics"].get(k), c))
    rows.sort(key=lambda r: -abs(r[3]))
    tot = sum(abs(r[3]) for r in rows) or 1
    lines.append(f"  {'metric':24} {'official':>10} {'candidate':>10} {'points':>8}  {'share':>6}  flip-factor")
    for k, a, b, c in rows:
        if abs(c) < 0.005:
            continue
        # factor on the weight of this one metric at which the soft decision flips (ΔS = −T)
        f = 1 + (-T - dS) / c
        lines.append(f"  {k:24} {fmt(a):>10} {fmt(b):>10} {c:>+8.2f}  {abs(c) / tot:>5.0%}  "
                     + (f"x{f:.2f}" if f >= 0 else "-"))
    lines.append(f"  {'sum':24} {'S ' + fmt(eo['S']):>10} {'S ' + fmt(ec['S']):>10} {dS:>+8.2f}")
    rnd = random.Random(1)
    diffs = [r[3] for r in rows]
    n_acc = sum(1 for _ in range(ROBUST_SAMPLES) if sum(c * 2 ** rnd.uniform(-1, 1) for c in diffs) <= -T)
    lines.append(f"  robustness: soft decision \"accept\" in {100 * n_acc / ROBUST_SAMPLES:.1f} % of "
                 f"{ROBUST_SAMPLES} random weight sets (each ×0.5…×2)")
    for label, b in (("official", official), ("candidate", cand)):
        for p in (b.get("details") or {}).get("paths", []):
            if not p.get("connected"):
                lines.append(f"  path {label}: {p['name']}: not connected")
                continue
            lines.append(f"  path {label}: {p['name']}: {p['drop_mv']} mV, min. {p['min_width_mm']} mm, "
                         f"{p['vias']} vias, inner {p.get('inner_mm', 0)} mm, too narrow {p['under_width_mm']} mm"
                         + ("  ← violation" if p["violation"] else ""))
    return lines


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    board = sys.argv[2] if len(sys.argv) > 2 else "main-board"
    cfg = load_config(board)
    m, d = measure_all(sys.argv[1], cfg)
    print(json.dumps({"metrics": m, "details": d, "evaluation": evaluate(cfg, m, d)}, indent=2, ensure_ascii=False))
