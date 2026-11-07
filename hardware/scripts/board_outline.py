#!/usr/bin/env python3
"""Legt die Hauptplatine im AA-Format an bzw. setzt ihren Umriss neu.

Aufruf (über just):  just outline
Muss mit dem System-Python laufen, das das KiCad-Modul pcbnew enthält.

Maße siehe docs/hardware-konzept.md, Kapitel 4.1.
"""
from pathlib import Path

import pcbnew

HARDWARE = Path(__file__).resolve().parent.parent
PCB = HARDWARE / "main-board" / "louie-main.kicad_pcb"

LENGTH_MM = 46.0  # AA = 50,5 mm; Rest bleibt für die Kontakte an den Enden
# 14,1 mm (vorher 13,5): AA-Ø 14,5, auf Platinenhöhe (z −0,3 … +0,5 um die Zellachse) ist der Kreis noch 14,47 mm
# breit; 14,1 lässt Luft für die Umrisstoleranz bei JLC (±0,2). Gewinn: eine Längsbahn mehr je Rand und Lage.
WIDTH_MM = 14.1
THICKNESS_MM = 0.8  # dünn, damit das Modul in der AA-Hülle Platz hat
# Enden: auf den 0,8 mm, mit denen die Platine in die Endkappen greift, schmaler (Zunge), damit der Kappenschlitz
# nicht breiter werden muss; Innenecken mit Fräserradius
TONGUE_W = 12.5
TONGUE_L = 0.8
MILL_R = 0.5      # Innenecken (Fräser 1,0 mm)
CORNER_MM = 0.3   # Außenecken
# Aussparung vor der USB-C-Buchse (J4 bei x = 15,3): 9 mm breit, 0,3 mm tief, damit die Buchsenöffnung wie bisher
# 0,7 mm hinter der Kante liegt (Platz für den Steckerkörper)
RECESS_X = (10.8, 19.8)
RECESS_DEPTH = 0.3
ORIGIN_MM = (100.0, 75.0)  # Platinenmitte auf dem Blatt


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(ORIGIN_MM[0] + x), mm(ORIGIN_MM[1] + y))


def add_shape(board, shape, **kwargs):
    item = pcbnew.PCB_SHAPE(board)
    item.SetShape(shape)
    item.SetLayer(pcbnew.Edge_Cuts)
    item.SetWidth(mm(0.05))
    for name, value in kwargs.items():
        getattr(item, f"Set{name}")(value)
    board.Add(item)


def _fillet(prev, v, nxt, r):
    """Tangentenpunkte und Bogenmitte einer 90°-Ecke v mit Radius r (konvex oder konkav)."""
    import math
    ax, ay = prev[0] - v[0], prev[1] - v[1]
    bx, by = nxt[0] - v[0], nxt[1] - v[1]
    la, lb = math.hypot(ax, ay), math.hypot(bx, by)
    ax, ay, bx, by = ax / la, ay / la, bx / lb, by / lb
    t1, t2 = (v[0] + r * ax, v[1] + r * ay), (v[0] + r * bx, v[1] + r * by)
    cx, cy = v[0] + r * (ax + bx), v[1] + r * (ay + by)
    d = math.hypot(v[0] - cx, v[1] - cy)
    mid = (cx + r * (v[0] - cx) / d, cy + r * (v[1] - cy) / d)
    return t1, mid, t2


def outline_path(length=LENGTH_MM, width=WIDTH_MM, tongue_w=TONGUE_W, tongue_l=TONGUE_L, recess=RECESS_X,
                 depth=RECESS_DEPTH):
    """Umriss als Liste von ("seg", a, b) und ("arc", start, mid, end), Koordinaten relativ zur Platinenmitte
    (x entlang der Länge, +y = Seite der USB-C-Öffnung)."""
    import math
    xe, xl, w2, t2 = length / 2, length / 2 - tongue_l, width / 2, tongue_w / 2
    rc, rm = CORNER_MM, MILL_R
    # Eckpunkte im Umlauf (Radius): Körper mit Zungen an beiden Enden
    verts = [((-xl, -w2), rc), ((xl, -w2), rc), ((xl, -t2), rm), ((xe, -t2), rc), ((xe, t2), rc), ((xl, t2), rm),
             ((xl, w2), rc), ((-xl, w2), rc), ((-xl, t2), rm), ((-xe, t2), rc), ((-xe, -t2), rc), ((-xl, -t2), rm)]
    n = len(verts)
    corners = [_fillet(verts[k - 1][0], verts[k][0], verts[(k + 1) % n][0], verts[k][1]) for k in range(n)]
    out = []
    for k in range(n):
        t1, mid, t2_ = corners[k]
        out.append(("arc", t1, mid, t2_))
        a, b = t2_, corners[(k + 1) % n][0]
        if k == 6 and recess:  # Kante +y von (xl, w2) nach (−xl, w2): Aussparung vor J4
            xa, xb = sorted(recess)
            y0 = w2 - depth            # Grund der Aussparung
            cy = y0 + rm                 # Fräsermitte (außerhalb der Platine)
            dx = math.sqrt(rm ** 2 - (cy - w2) ** 2)
            # rechts: Kante → Bogen hinunter auf den Grund; links umgekehrt
            r_top, r_bot = (xb - rm + dx, w2), (xb - rm, y0)
            l_bot, l_top = (xa + rm, y0), (xa + rm - dx, w2)

            def arc_mid(c, p, q):
                ang = (math.atan2(p[1] - c[1], p[0] - c[0]) + math.atan2(q[1] - c[1], q[0] - c[0])) / 2
                return (c[0] + rm * math.cos(ang), c[1] + rm * math.sin(ang))
            out.append(("seg", a, r_top))
            out.append(("arc", r_top, arc_mid((xb - rm, cy), r_top, r_bot), r_bot))
            out.append(("seg", r_bot, l_bot))
            out.append(("arc", l_bot, arc_mid((xa + rm, cy), l_bot, l_top), l_top))
            out.append(("seg", l_top, b))
        else:
            out.append(("seg", a, b))
    return [o for o in out if not (o[0] == "seg" and o[1] == o[2])]


def draw_outline(board, length=LENGTH_MM, width=WIDTH_MM):
    for item in list(board.GetDrawings()):
        if item.GetLayer() == pcbnew.Edge_Cuts:
            board.Remove(item)
    for kind, *pts in outline_path(length, width):
        if kind == "seg":
            add_shape(board, pcbnew.SHAPE_T_SEGMENT, Start=point(*pts[0]), End=point(*pts[1]))
        else:
            arc = pcbnew.PCB_SHAPE(board)
            arc.SetShape(pcbnew.SHAPE_T_ARC)
            arc.SetLayer(pcbnew.Edge_Cuts)
            arc.SetWidth(mm(0.05))
            arc.SetArcGeometry(point(*pts[0]), point(*pts[1]), point(*pts[2]))
            board.Add(arc)


def main():
    board = pcbnew.LoadBoard(str(PCB)) if PCB.exists() else pcbnew.NewBoard(str(PCB))
    board.GetDesignSettings().SetBoardThickness(mm(THICKNESS_MM))
    draw_outline(board)
    pcbnew.SaveBoard(str(PCB), board)
    print(f"{PCB.relative_to(HARDWARE.parent)}: {LENGTH_MM} x {WIDTH_MM} mm (Enden {TONGUE_W} mm), "
          f"{THICKNESS_MM} mm dick")


if __name__ == "__main__":
    main()
