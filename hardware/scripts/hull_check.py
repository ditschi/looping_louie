#!/usr/bin/env python3
"""Hüllkurvenprüfung der Hauptplatine gegen die AA-Hülle (hardware/mechanik/huelle.scad, docs/hauptplatine-c6.md Kapitel 6).

Liest das STL aus `just modell` (build/main-board/3d/louie-main.stl, Platine mit allen 3D-Modellen, auch der
nicht bestückten Teile unten) und prüft alle Eckpunkte:
- Radius um die Zellachse < AA-Radius 7,25 mm (Platinenoberseite 0,5 mm über der Achse, wie pcb_top in huelle.scad)
- unter der Platine nur in der Tasche: |y| <= 5,2 mm (fach_b / 2) und höchstens 2,0 mm tief (fach_tiefe), mit
  0,5 mm Luft für Lötzinn/Toleranz also Bauhöhe <= 1,5 mm
- unter den Endkappen (|x| > 22,2 mm) nur die Platine selbst

Aufruf: hull_check.py [datei.stl]   (just hull); Rückgabe 1, wenn eine Grenze verletzt ist.
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
STL = ROOT / "build" / "main-board" / "3d" / "louie-main.stl"
AA_RADIUS = 7.25
PCB_TOP_ABOVE_AXIS = 0.5   # huelle.scad pcb_top
PCB_T = 0.8
POCKET_HALF = 10.4 / 2     # huelle.scad fach_b
POCKET_DEPTH = 2.0         # huelle.scad fach_tiefe
SOLDER_GAP = 0.5           # Luft unter den Bauteilen unten (Lötzinn, Toleranz)
CAP_X = 22.2               # Innenfläche der Endkappen (pcb_l / 2 - ueberdeckung)
EPS = 0.02


def vertices(path):
    data = Path(path).read_bytes()
    if data[:5] == b"solid" and b"facet" in data[:400]:
        nums = re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)
        return np.array(nums, dtype=float)
    count = int.from_bytes(data[80:84], "little")
    rec = np.frombuffer(data[84:84 + 50 * count], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return rec["v"].reshape(-1, 3).astype(float)


def main(path=STL):
    v = vertices(path)
    # Platine: die Ebene mit den meisten Punkten bei z = 0 bzw. 0,8 (KiCad: Unterseite z = 0)
    zs = v[:, 2]
    bottom = 0.0 if np.isclose(zs, 0.0, atol=1e-3).sum() > np.isclose(zs, -PCB_T, atol=1e-3).sum() else -PCB_T
    top = bottom + PCB_T
    board = np.isclose(zs, bottom, atol=1e-3)
    xc = (v[board, 0].min() + v[board, 0].max()) / 2
    yc = (v[board, 1].min() + v[board, 1].max()) / 2
    x, y, z = v[:, 0] - xc, v[:, 1] - yc, v[:, 2] - (top - PCB_TOP_ABOVE_AXIS)
    # KiCad-STL: y wächst nach oben (gespiegelt zur Platinen-Ansicht); für |y| egal
    r = np.hypot(y, z)
    k = int(r.argmax())
    ok = True
    print(f"{Path(path).name}: {len(v)} Eckpunkte, Platine z {bottom:.2f} … {top:.2f} mm")
    print(f"  größter Radius {r[k]:.2f} mm bei x {x[k]:+.2f}, y {y[k]:+.2f}, z {z[k]:+.2f} (Grenze {AA_RADIUS} mm)")
    ok &= r[k] < AA_RADIUS
    below = z < (bottom - (top - PCB_TOP_ABOVE_AXIS)) - EPS
    if below.any():
        depth = (bottom - (top - PCB_TOP_ABOVE_AXIS)) - z[below]
        wide = np.abs(y[below]).max()
        print(f"  unten: größte Bauhöhe {depth.max():.2f} mm (Grenze {POCKET_DEPTH - SOLDER_GAP:.1f}), "
              f"größtes |y| {wide:.2f} mm (Tasche {POCKET_HALF})")
        ok &= depth.max() <= POCKET_DEPTH - SOLDER_GAP + EPS and wide <= POCKET_HALF + EPS
    caps = (np.abs(x) > CAP_X + EPS) & ((v[:, 2] > top + EPS) | (v[:, 2] < bottom - EPS))
    print(f"  unter den Endkappen (|x| > {CAP_X}): {int(caps.sum())} Punkte außerhalb der Platine")
    ok &= not caps.any()
    print("  Ergebnis: " + ("passt" if ok else "VERLETZT"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
