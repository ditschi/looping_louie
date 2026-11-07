#!/usr/bin/env python3
"""Zeichnet die Platzierung der Hauptplatine als PNG (Ober- und Unterseite übereinander):
Courtyards, Pads, Referenzen, Luftlinien (Ratsnest) und Sperrflächen. Meldet Überlappungen
und die Flächenbelegung.

Aufruf (über just):  just plot   → build/main-board/placement.png
"""
import itertools
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pcbnew  # noqa: E402

HARDWARE = Path(__file__).resolve().parent.parent
BOARD = sys.argv[1] if len(sys.argv) > 1 else "main-board"
PCB = HARDWARE / BOARD / ("louie-" + BOARD.replace("-board", "") + ".kicad_pcb")
OUT = HARDWARE.parent / "build" / BOARD / "placement.png"
ORIGIN = (100.0, 75.0)
NET_COLORS = {"GND": "#555555", "VSYS": "#d62728", "+3V3": "#ff7f0e", "MOT_A": "#9467bd", "MOT_B": "#8c564b"}


def to_xy(v):
    return pcbnew.ToMM(v.x) - ORIGIN[0], pcbnew.ToMM(v.y) - ORIGIN[1]


def box(b):
    x0, y0 = to_xy(pcbnew.VECTOR2I(b.GetLeft(), b.GetTop()))
    x1, y1 = to_xy(pcbnew.VECTOR2I(b.GetRight(), b.GetBottom()))
    return x0, y0, x1, y1


def overlap(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def mst(points):
    """Minimaler Spannbaum (Prim) über Punkte, gibt Kanten zurück."""
    if len(points) < 2:
        return []
    done, edges = {0}, []
    while len(done) < len(points):
        best = min(((i, j) for i in done for j in range(len(points)) if j not in done),
                   key=lambda e: math.dist(points[e[0]], points[e[1]]))
        edges.append((points[best[0]], points[best[1]]))
        done.add(best[1])
    return edges


def main():
    board = pcbnew.LoadBoard(str(PCB))
    side_axes = {}
    fig, axes = plt.subplots(2, 1, figsize=(16, 10.5))
    for ax, (side, layer, title) in zip(axes, [("F", pcbnew.F_CrtYd, "Oberseite (Bestückung)"),
                                               ("B", pcbnew.B_CrtYd, "Unterseite (Blick von oben, durchsichtig)")]):
        side_axes[side] = ax
        ax.set_title(title, loc="left", fontsize=11)
        ax.set_aspect("equal")
        ax.set_xlim(-24, 24)
        ax.set_ylim(7.5, -7.5)
        ex0, ey0, ex1, ey1 = box(board.GetBoardEdgesBoundingBox())
        for item in board.GetDrawings():  # Umriss (Edge.Cuts): Strecken und Bögen als Polylinie
            if item.GetLayer() == pcbnew.Edge_Cuts:
                if item.GetShape() == pcbnew.SHAPE_T_ARC:
                    pts = [to_xy(item.GetStart()), to_xy(item.GetArcMid()), to_xy(item.GetEnd())]
                else:
                    pts = [to_xy(item.GetStart()), to_xy(item.GetEnd())]
                ax.plot([q[0] for q in pts], [q[1] for q in pts], color="black", lw=1.5)
        for zone in board.Zones():
            if zone.GetIsRuleArea() and zone.GetZoneName() != "GND-Lage":  # In1 ganzflächig
                x0, y0, x1, y1 = box(zone.GetBoundingBox())
                ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, color="#ffd9d9", zorder=0))
                ax.text(x0 + 0.3, y1 - 0.3, zone.GetZoneName(), fontsize=7, color="#c00")

    courtyards = {"F": [], "B": []}
    area = {"F": 0.0, "B": 0.0}
    for fp in board.GetFootprints():
        side = "B" if fp.IsFlipped() else "F"
        layer = pcbnew.B_CrtYd if side == "B" else pcbnew.F_CrtYd
        shape = fp.GetCourtyard(layer)
        if shape.OutlineCount() == 0:
            continue
        b = box(shape.BBox())
        courtyards[side].append((fp.GetReference(), b))
        area[side] += (b[2] - b[0]) * (b[3] - b[1])
        ax = side_axes[side]
        ax.add_patch(plt.Rectangle((b[0], b[1]), b[2] - b[0], b[3] - b[1], fill=False,
                                   color="#1f77b4" if side == "F" else "#2ca02c", lw=1))
        for pad in fp.Pads():
            p = box(pad.GetBoundingBox())
            ax.add_patch(plt.Rectangle((p[0], p[1]), p[2] - p[0], p[3] - p[1], color="#e8b04b", alpha=0.8, lw=0))
        cx, cy = to_xy(fp.GetPosition())
        ax.text(cx, cy, fp.GetReference(), ha="center", va="center", fontsize=7, weight="bold")

    # Luftlinien: Pads je Netz, auf beiden Ansichten
    pads_by_net = {}
    for pad in board.GetPads():
        if pad.GetNetname():
            pads_by_net.setdefault(pad.GetNetname().lstrip("/"), []).append(to_xy(pad.GetPosition()))
    for net, pts in pads_by_net.items():
        color = NET_COLORS.get(net, "#1f77b4")
        for (x0, y0), (x1, y1) in mst(pts):
            for ax in axes:
                ax.plot([x0, x1], [y0, y1], color=color, lw=0.6, alpha=0.7)

    problems = []
    for side in "FB":
        for (ra, a), (rb, b) in itertools.combinations(courtyards[side], 2):
            if overlap(a, b) > 0.01:
                problems.append(f"{side}: {ra} überlappt {rb} ({overlap(a, b):.1f} mm²)")
        for ref, b in courtyards[side]:
            if b[0] < ex0 or b[2] > ex1 or b[1] < ey0 or b[3] > ey1:
                problems.append(f"{side}: {ref} ragt über den Platinenrand")

    usable = (ex1 - ex0) * (ey1 - ey0)
    fig.suptitle(f"Belegung (Courtyard-Fläche): oben {area['F']:.0f} mm², unten {area['B']:.0f} mm² "
                 f"von je {usable:.0f} mm²  ·  Luftlinien: grau GND, rot VSYS, orange 3V3", fontsize=11)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=110)
    print(f"{OUT.relative_to(HARDWARE.parent)}  oben {area['F']:.0f} mm², unten {area['B']:.0f} mm²")
    for p in problems:
        print("  ⚠", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
