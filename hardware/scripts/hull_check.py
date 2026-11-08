#!/usr/bin/env python3
"""Envelope check of the main board against the AA sleeve (hardware/mechanics/sleeve.scad, docs/main-board-c6.md chapter 6).

Reads the STL from `just model` (build/main-board/3d/louie-main.stl, board with all 3D models, including the
unpopulated parts on the bottom) and checks all vertices:
- radius around the cell axis < AA radius 7.25 mm (board top 0.5 mm above the axis, like pcb_top in sleeve.scad)
- below the board only in the pocket: |y| <= 5.2 mm (pocket_w / 2) and at most 2.0 mm deep (pocket_depth), with
  0.5 mm clearance for solder/tolerance thus component height <= 1.5 mm
- under the end caps (|x| > 22.2 mm) only the board itself

Usage: hull_check.py [file.stl]   (just hull); returns 1 if a limit is violated.
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
STL = ROOT / "build" / "main-board" / "3d" / "louie-main.stl"
AA_RADIUS = 7.25
PCB_TOP_ABOVE_AXIS = 0.5   # sleeve.scad pcb_top
PCB_T = 0.8
POCKET_HALF = 10.4 / 2     # sleeve.scad pocket_w
POCKET_DEPTH = 2.0         # sleeve.scad pocket_depth
SOLDER_GAP = 0.5           # clearance under the bottom components (solder, tolerance)
CAP_X = 22.2               # inner face of the end caps (pcb_l / 2 - overlap)
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
    # board: the plane with the most points at z = 0 or 0.8 (KiCad: bottom side z = 0)
    zs = v[:, 2]
    bottom = 0.0 if np.isclose(zs, 0.0, atol=1e-3).sum() > np.isclose(zs, -PCB_T, atol=1e-3).sum() else -PCB_T
    top = bottom + PCB_T
    board = np.isclose(zs, bottom, atol=1e-3)
    xc = (v[board, 0].min() + v[board, 0].max()) / 2
    yc = (v[board, 1].min() + v[board, 1].max()) / 2
    x, y, z = v[:, 0] - xc, v[:, 1] - yc, v[:, 2] - (top - PCB_TOP_ABOVE_AXIS)
    # KiCad STL: y grows upwards (mirrored relative to the board view); irrelevant for |y|
    r = np.hypot(y, z)
    k = int(r.argmax())
    ok = True
    print(f"{Path(path).name}: {len(v)} vertices, board z {bottom:.2f} … {top:.2f} mm")
    print(f"  largest radius {r[k]:.2f} mm at x {x[k]:+.2f}, y {y[k]:+.2f}, z {z[k]:+.2f} (limit {AA_RADIUS} mm)")
    ok &= r[k] < AA_RADIUS
    below = z < (bottom - (top - PCB_TOP_ABOVE_AXIS)) - EPS
    if below.any():
        depth = (bottom - (top - PCB_TOP_ABOVE_AXIS)) - z[below]
        wide = np.abs(y[below]).max()
        print(f"  bottom: largest component height {depth.max():.2f} mm (limit {POCKET_DEPTH - SOLDER_GAP:.1f}), "
              f"largest |y| {wide:.2f} mm (pocket {POCKET_HALF})")
        ok &= depth.max() <= POCKET_DEPTH - SOLDER_GAP + EPS and wide <= POCKET_HALF + EPS
    caps = (np.abs(x) > CAP_X + EPS) & ((v[:, 2] > top + EPS) | (v[:, 2] < bottom - EPS))
    print(f"  under the end caps (|x| > {CAP_X}): {int(caps.sum())} points outside the board")
    ok &= not caps.any()
    print("  Result: " + ("OK" if ok else "VIOLATED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
