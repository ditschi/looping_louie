"""Variante 1 (Machbarkeitstest): alle bestückten Bauteile oben, dicht gepackt.

Testpads und Endkontakte sind reine Kupferflächen und liegen unten (keine Bestückung nötig).
Die übrigen Bauteile werden mit einem einfachen Regal-Packer und nur 0,4 mm Abstand in die
freie Fläche neben dem ESP-Modul gelegt, ohne Platz für Leiterbahnen. Passt es so nicht,
ist eine einseitig bestückte Platine ausgeschlossen.
"""

# Courtyard-Größen (mm) der verwendeten Footprints, Länge x Breite
SIZES = {
    "U2": (7.89, 5.59), "U3": (4.19, 3.49), "J1": (6.65, 7.89),
    "C1": (4.69, 2.39), "C2": (4.69, 2.39), "C3": (4.69, 2.39),
    "C9": (3.49, 2.05), "R1": (3.49, 2.05),
}
SMALL = ["C4", "C5", "C6", "C7", "C8", "C10", "C11", "C12", "C13", "C14",
         "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "D1"]
for ref in SMALL:
    SIZES[ref] = (3.05, 1.55)

GAP = 0.4
REGION = (-3.8, 21.5, -6.45, 6.45)  # x0, x1, y0, y1 neben dem Modul, 0,3 mm Randabstand

PLACEMENT = {
    "U1": (-9.96, 0, 90, "F"),
    "BT1": (-21.2, 0, 0, "B"), "BT2": (21.2, 0, 0, "B"),
    "TP1": (-12, -4.5, 0, "B"), "TP2": (-9, -4.5, 0, "B"), "TP3": (-6, -4.5, 0, "B"),
    "TP4": (-12, 4.5, 0, "B"), "TP5": (-9, 4.5, 0, "B"), "TP6": (-6, 4.5, 0, "B"),
}


def _pack():
    x0, x1, y0, y1 = REGION
    order = sorted(SIZES, key=lambda r: -SIZES[r][1])  # nach Höhe, höchste zuerst
    x, y, shelf_h, overflow = x0, y0, 0.0, []
    for ref in order:
        w, h = SIZES[ref]
        if x + w > x1:  # neues Regal
            x, y, shelf_h = x0, y + shelf_h + GAP, 0.0
        if y + h > y1:
            overflow.append(ref)
            continue
        PLACEMENT[ref] = (x + w / 2, y + h / 2, 0, "F")
        x += w + GAP
        shelf_h = max(shelf_h, h)
    # was nicht passt, landet sichtbar außerhalb der Platine
    for i, ref in enumerate(overflow):
        PLACEMENT[ref] = (-20 + 4 * i, 9.5, 0, "F")
    return overflow


OVERFLOW = _pack()
