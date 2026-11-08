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
WIDTH_MM = 13.5  # ESP32-C3-MINI-1 ist 13,2 mm breit
THICKNESS_MM = 0.8  # dünn, damit das Modul in der AA-Hülle Platz hat
CORNER_MM = 0.5
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


def draw_outline(board):
    for item in list(board.GetDrawings()):
        if item.GetLayer() == pcbnew.Edge_Cuts:
            board.Remove(item)

    l, w, r = LENGTH_MM, WIDTH_MM, CORNER_MM
    # Koordinaten relativ zur Platinenmitte, x entlang der Länge
    x0, x1, y0, y1 = -l / 2, l / 2, -w / 2, w / 2
    for a, b in [((x0 + r, y0), (x1 - r, y0)), ((x1, y0 + r), (x1, y1 - r)),
                 ((x1 - r, y1), (x0 + r, y1)), ((x0, y1 - r), (x0, y0 + r))]:
        add_shape(board, pcbnew.SHAPE_T_SEGMENT, Start=point(*a), End=point(*b))
    d = r * (1 - 0.5 ** 0.5)  # Abstand des Bogenmittelpunkts von der Ecke
    for (cx, cy), (sx, sy), (ex, ey) in [((x0, y0), (x0, y0 + r), (x0 + r, y0)),
                                         ((x1, y0), (x1 - r, y0), (x1, y0 + r)),
                                         ((x1, y1), (x1, y1 - r), (x1 - r, y1)),
                                         ((x0, y1), (x0 + r, y1), (x0, y1 - r))]:
        mx = cx + d if cx == x0 else cx - d
        my = cy + d if cy == y0 else cy - d
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(mm(0.05))
        arc.SetArcGeometry(point(sx, sy), point(mx, my), point(ex, ey))
        board.Add(arc)


def main():
    board = pcbnew.LoadBoard(str(PCB)) if PCB.exists() else pcbnew.NewBoard(str(PCB))
    board.GetDesignSettings().SetBoardThickness(mm(THICKNESS_MM))
    draw_outline(board)
    pcbnew.SaveBoard(str(PCB), board)
    print(f"{PCB.relative_to(HARDWARE.parent)}: {LENGTH_MM} x {WIDTH_MM} mm, {THICKNESS_MM} mm dick")


if __name__ == "__main__":
    main()
