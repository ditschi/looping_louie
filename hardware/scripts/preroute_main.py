"""Pre-routing of the main board (gen_main_pcb.py): only the critical tracks, the own router does the rest.

Motor outputs, VSYS/VBUS/BAT_IN, USB pair, CC, ADC stubs and short bridges, plus thermal vias of the DRV8213 and
the LDO. Track widths: docs/main-board-c6.md chapter 11.
"""

import board_outline
import pcbnew
from pcb_tools import RULES, add_track, add_via, mm, pad_of

ORIGIN = board_outline.ORIGIN_MM  # board centre
BOARD_W = board_outline.WIDTH_MM
POWER_TRACK = 0.4  # approx. 1.5 A at 35 µm copper; at the 0.5 mm pins of the DRV8213 only short 0.3 mm stubs
STUB_TRACK = 0.3  # stubs at fine-pitch pins
MAIN_TRACK = 0.5  # pre-routed VSYS main track (Schottky -> buffer -> VM)
SIGNAL_TRACK = 0.15  # pre-routed signal stubs
SUPPLY_TRACK = 0.25  # 3V3, GND (still fits the 0.5 mm pins of LIS2DH12/DRV8213)
EDGE_TRACK_Y = BOARD_W / 2 - 0.6  # distance of the edge tracks OUT_A/OUT_B from the centre (bottom)
COL1_X = -1.9  # 0402 row at the right module pins (placement.COL1)
VSYS_EDGE_Y = 6.5  # rev B: VSYS track along the +y edge from the Q1 vias to C8, U3 (IN, EN) and R6 (0.3 mm; edge
# clearance 0.4, 0.3 mm to the U3 pads ending at y 6.05)
VSYS_VIA_Y = 6.47  # outer VSYS via of preroute_battery_vsys (0.5 mm, stays inside the 0.32 mm edge keepout)


def thermal_vias(board, driver, gnd):
    """Two vias in the thermal pad (pad 9, 0.9 × 1.6 mm) of the DRV8213 to the ground pour on the bottom."""
    ep = next(p for p in driver.Pads() if p.GetNumber() == "9")
    c = ep.GetPosition()
    long_y = ep.GetBoundingBox().GetHeight() > ep.GetBoundingBox().GetWidth()
    for d in (-0.4, 0.4):
        add_via(board, gnd, c.x + (0 if long_y else mm(d)), c.y + (mm(d) if long_y else 0))


def preroute_supply(board, fps):
    """VSYS main track in advance (0.5 mm): cathode of Schottky D2 -> C1 -> C2 (vertical at the left
    pads), branch C1 -> C4 -> VM pin 1 of the DRV8213. The rest of VSYS (Q1, LDO, divider) and BAT_IN/VBUS
    are routed by Freerouting in the Power net class."""

    def at(ref, num):
        q = pad_of(fps[ref], num).GetPosition()
        return q.x, q.y

    net = pad_of(fps["C1"], "1").GetNet()
    k, c1, c2, c4, vm = at("D2", "1"), at("C1", "1"), at("C2", "1"), at("C4", "1"), at("U2", "1")
    add_track(board, net, (pcbnew.F_Cu, MAIN_TRACK), k, (c1[0], k[1] + mm(0.6)), c1, c2)
    add_track(board, net, (pcbnew.F_Cu, MAIN_TRACK), c1, (c4[0] + mm(0.3), c4[1]), c4)
    add_track(board, net, (pcbnew.F_Cu, STUB_TRACK), c4, (vm[0], vm[1] + mm(0.45)), vm)


def preroute_outputs(board, driver, contact_a, contact_b):
    """Outputs of the DRV8213 in advance: OUT1 (pin 2, OUT_A) and OUT2 (pin 3, OUT_B) each with a 0.3 mm stub to a
    via, on the bottom with 0.4 mm along the -y edge: OUT_A to the left under module and antenna (edge strip) to
    end contact BT1, OUT_B to the right to end contact BT2. Expects rotation 180° (pins 1–4 point to +x)."""
    assert round(driver.GetOrientationDegrees()) % 360 == 180, "preroute_outputs expects rotation 180°"
    pa, pb = pad_of(driver, "2").GetPosition(), pad_of(driver, "3").GetPosition()
    out_a, out_b = pad_of(driver, "2").GetNet(), pad_of(driver, "3").GetNet()
    edge_y = mm(ORIGIN[1] - EDGE_TRACK_Y)
    # OUT_A: via right of the pin, on the bottom diagonally under the driver to the edge, then to the left
    va = (pa.x + mm(1.15), pa.y)
    add_track(board, out_a, (pcbnew.F_Cu, STUB_TRACK), (pa.x, pa.y), va)
    add_via(board, out_a, *va)
    ca = next(iter(contact_a.Pads())).GetPosition()
    add_track(
        board,
        out_a,
        (pcbnew.B_Cu, POWER_TRACK),
        va,
        (va[0] - mm(0.75), edge_y),
        (ca.x + mm(0.8), edge_y),
        (ca.x, edge_y + mm(0.8)),
        (ca.x, ca.y),
    )
    # OUT_B: stub diagonally to the lower right (past GND pin 4), via, on the bottom along the edge to the right
    vb = (pb.x + mm(1.7), pb.y - mm(0.4))
    add_track(
        board, out_b, (pcbnew.F_Cu, STUB_TRACK), (pb.x, pb.y), (pb.x + mm(0.6), pb.y), (pb.x + mm(1.0), vb[1]), vb
    )
    add_via(board, out_b, *vb)
    cb = next(iter(contact_b.Pads())).GetPosition()
    add_track(
        board,
        out_b,
        (pcbnew.B_Cu, POWER_TRACK),
        vb,
        (vb[0], edge_y),
        (cb.x - mm(0.8), edge_y),
        (cb.x, edge_y + mm(0.8)),
        (cb.x, cb.y),
    )


def rel(x, y):
    """Point relative to the board centre (mm) as absolute coordinate (nm)."""
    return mm(ORIGIN[0] + x), mm(ORIGIN[1] + y)


def preroute_vbus(board, fps):
    """VBUS (up to 2 A) in advance:
    - left VBUS pad pair (A4/B9): on the band side on top with 0.5 mm diagonally to the anode of Schottky D2
    - the two VBUS pad pairs with each other via the body side: one via behind each pad (outside the
      holes), connected on the bottom. The band in front of the data pads thus stays free on the bottom for D-/D+
      (ESD flow-through).
    - ESD U5 pin 5 (VBUS) on top horizontally between the D+/D- vias to the diagonal track"""
    usb = fps["J4"]
    net = pad_of(usb, "A4").GetNet()
    left, right = sorted((pad_of(usb, n) for n in ("A4", "B4")), key=lambda p: p.GetPosition().x)
    ql, qr = left.GetPosition(), right.GetPosition()
    half = left.GetBoundingBox().GetHeight() // 2
    band, body = ql.y - half, ql.y + half  # pad ends: band (-y) and body (+y)
    # vertically to -y until below the ESD, then horizontally into the anode: above it there is room for R14/R15
    an = pad_of(fps["D2"], "2").GetPosition()
    y_run = an.y - mm(0.25)
    add_track(board, net, (pcbnew.F_Cu, MAIN_TRACK), (ql.x, band), (ql.x, y_run), (an.x, y_run))
    # body side: vias to the lower right of the pads (keep the receptacle holes at x ±2.9 / y -0.2 free)
    vl = (ql.x + mm(0.55), body + mm(0.82))
    vr = (qr.x - mm(0.55), body + mm(0.82))
    add_track(board, net, (pcbnew.F_Cu, 0.3), (ql.x, body), vl)
    add_track(board, net, (pcbnew.F_Cu, 0.3), (qr.x, body), vr)
    add_via(board, net, *vl)
    add_via(board, net, *vr)
    add_track(board, net, (pcbnew.B_Cu, MAIN_TRACK), vl, vr)
    # ESD pin 5 horizontally to the vertical VBUS track
    p5 = pad_of(fps["U5"], "5").GetPosition()
    add_track(board, net, (pcbnew.F_Cu, 0.3), (p5.x, p5.y), (ql.x, p5.y))
    # VBUS divider R14 (top, in the band): right VBUS pad to the vertical track
    r14 = pad_of(fps["R14"], "1").GetPosition()
    add_track(board, net, (pcbnew.F_Cu, 0.25), (r14.x, r14.y), (ql.x, r14.y))


def preroute_vbus_branches(board, fps):
    """VBUS to the gate of Q1 (edge +y, no load current, 0.25 mm) and VBUS_DET out of the band to the north:
    - VBUS: via above the anode of the Schottky, on the bottom to the north-west (west of the USB pair and right
      past the U6 group), via right of the gate pad (between J2 pads 4 and 5 on the bottom), on top to the gate. On In2 it
      was a second wall parallel to the VSYS track on the bottom; then the router could hardly get from west to east
      (main-board-c6.md 11.7).
    - VBUS_DET: R14–R15 directly; the path to the module (pad 9) is routed by route_fix.py"""
    net = pad_of(fps["J4"], "A4").GetNet()
    an = pad_of(fps["D2"], "2")
    a = rel(8.3, -2.5)
    b = rel(7.5, 3.2)
    q = an.GetPosition()
    add_track(board, net, (pcbnew.F_Cu, 0.25), (q.x, q.y), (a[0], q.y + mm(0.6)), a)
    add_via(board, net, *a)
    add_track(board, net, (pcbnew.B_Cu, 0.25), a, rel(7.25, -1.45), rel(7.25, 2.95), b)
    add_via(board, net, *b)
    g = pad_of(fps["Q1"], "1").GetPosition()
    add_track(board, net, (pcbnew.F_Cu, 0.25), b, (g.x, g.y))
    det = pad_of(fps["R14"], "2").GetNet()
    r14, r15 = pad_of(fps["R14"], "2").GetPosition(), pad_of(fps["R15"], "1").GetPosition()
    add_track(board, det, (pcbnew.F_Cu, SIGNAL_TRACK), (r14.x, r14.y), (r15.x, r15.y))


def preroute_right_end(board, fps):
    """Right end: OUT_B from R4 by via to the OUT_B track on the bottom, 3V3 from R4 to C15."""
    r4o, r4v, c15 = pad_of(fps["R4"], "1"), pad_of(fps["R4"], "2"), pad_of(fps["C15"], "1")
    q = r4o.GetPosition()
    v = (q.x, q.y - mm(0.62))
    add_track(board, r4o.GetNet(), (pcbnew.F_Cu, 0.25), (q.x, q.y), v)
    add_via(board, r4o.GetNet(), *v)
    a, b = r4v.GetPosition(), c15.GetPosition()
    add_track(board, r4v.GetNet(), (pcbnew.F_Cu, SUPPLY_TRACK), (a.x, a.y), (b.x, b.y))


def preroute_cc(board, fps):
    """CC1 (A5) via the body side of the receptacle to R12 left of J4 (the band is occupied by D-/D+);
    CC2 (B5) on the band side to R13."""
    usb = fps["J4"]
    a5, b5 = pad_of(usb, "A5"), pad_of(usb, "B5")
    half = a5.GetBoundingBox().GetHeight() // 2
    q = a5.GetPosition()
    r12 = pad_of(fps["R12"], "1").GetPosition()
    y = mm(ORIGIN[1] + 0.62)
    add_track(
        board,
        a5.GetNet(),
        (pcbnew.F_Cu, SIGNAL_TRACK),
        (q.x, q.y + half),
        (q.x, y),
        (r12.x + mm(0.35), y),
        (r12.x, r12.y),
    )
    q = b5.GetPosition()
    r13 = pad_of(fps["R13"], "1").GetPosition()
    add_track(
        board,
        b5.GetNet(),
        (pcbnew.F_Cu, SIGNAL_TRACK),
        (q.x, q.y - half),
        (q.x + mm(0.35), q.y - half - mm(0.4)),
        (r13.x, r13.y),
    )


def preroute_battery_vsys(board, fps):
    """Battery current to the motor (Q1 drain side VSYS → buffer C1/C2 → VM), up to 2 A, outer layers only
    (docs/routing-score.md 8.1: previously route_fix.py routed this path with 0.2–0.3 mm, partly on In2). Q1 pin 2
    on top to two vias at edge +y, on the bottom with 0.5 mm (IPC-2221: 1.5 A at 20 K needs 0.35 mm outer) between
    J2 pads 3/4 to the south, two vias right of C2 pin 1, on top into its pad (and via the C1–C2 track on to VM)."""
    net = pad_of(fps["Q1"], "2").GetNet()
    d = pad_of(fps["Q1"], "2").GetPosition()
    # rev B: the vias sit at x 5.5 (right of C8) instead of x 4.67, the second one towards the edge; from the outer
    # via the VSYS edge track (0.3 mm, y VSYS_EDGE_Y) runs west past C8 and U3 (preroute_ldo connects them) into R6
    # pad 1 (VBAT divider). On the bottom the path jogs back to x 4.67 (between J2 pads 3 and 4) and continues south.
    top, top2 = rel(5.5, pcbnew.ToMM(d.y) - ORIGIN[1]), rel(5.5, VSYS_VIA_Y)
    low, low2 = rel(5.0, -0.05), rel(5.0, -0.75)  # right of C2 pin 1; the gap C1/C2 stays free for signals
    add_track(board, net, (pcbnew.F_Cu, MAIN_TRACK), (d.x, d.y), top, top2)
    add_via(board, net, *top)
    add_via(board, net, *top2)
    r6 = pad_of(fps["R6"], "1").GetPosition()
    edge = (top2[0], mm(ORIGIN[1] + VSYS_EDGE_Y))
    add_track(board, net, (pcbnew.F_Cu, 0.3), top2, edge, (r6.x, edge[1]), (r6.x, r6.y))
    add_track(board, net, (pcbnew.B_Cu, MAIN_TRACK), top2, top, rel(4.67, 5.0), rel(4.67, 0.28), low, low2)
    add_via(board, net, *low)
    add_via(board, net, *low2)
    c2 = pad_of(fps["C2"], "1").GetPosition()
    for v in (low, low2):
        add_track(board, net, (pcbnew.F_Cu, MAIN_TRACK), v, (c2.x + mm(0.3), v[1]))


def preroute_led_ldo(board, fps):
    """LED LDO U6 (bottom, DNP): VIN (pin 1) with 0.4 mm on B.Cu straight to the battery VSYS track at x = 4.67, which
    runs 1.5 mm to its right; route_fix.py did not find this short path (variant test 2026-11-10)."""
    pad = pad_of(fps["U6"], "1")
    q = pad.GetPosition()
    add_track(board, pad.GetNet(), (pcbnew.B_Cu, 0.4), (q.x, q.y), (rel(4.67, 0)[0], q.y))


def preroute_adc_stubs(board, fps):
    """Short analog connections at the right module pins, locked so that no fanout via or foreign track takes the
    0.7 mm gap between the module pads and the 0402 row (variant test 2026-11-08, docs/main-board-c6.md 11):
    pad 12 (VBAT_ADC) -> C13, pad 13 (ISEN_ADC) -> C14, C13 -> R6 pin 2 above C13 pin 2 (GND), R6 pin 2 -> R7 pin 1.
    Replaces the former VBAT_ADC escape via at the old R6 place."""

    def q(ref, num):
        p = pad_of(fps[ref], num).GetPosition()
        return p.x, p.y

    for (ra, na), (rb, nb) in ((("U1", "12"), ("C13", "1")), (("U1", "13"), ("C14", "1")), (("R6", "2"), ("R7", "1"))):
        add_track(board, pad_of(fps[ra], na).GetNet(), (pcbnew.F_Cu, SIGNAL_TRACK), q(ra, na), q(rb, nb))
    c13, r6 = q("C13", "1"), q("R6", "2")
    y = (c13[1] + q("C14", "1")[1]) // 2  # between C14 and C13 pin 2
    add_track(board, pad_of(fps["C13"], "1").GetNet(), (pcbnew.F_Cu, SIGNAL_TRACK), c13, (c13[0], y), (r6[0], y), r6)


def preroute_bat_in(board, fps):
    """BAT_IN (up to 2 A) in advance: battery pad J5.1 on the bottom to cable pad J1.1 and between the tabs of J4
    to a via next to the drain of Q1."""
    net = pad_of(fps["J5"], "1").GetNet()
    j5, j1 = pad_of(fps["J5"], "1").GetPosition(), pad_of(fps["J1"], "1").GetPosition()
    d = pad_of(fps["Q1"], "3").GetPosition()
    add_track(
        board,
        net,
        (pcbnew.B_Cu, MAIN_TRACK),
        (j5.x, j5.y),
        (j5.x - mm(0.8), j5.y + mm(1.75)),
        (j1.x + mm(0.4), j1.y - mm(0.7)),
        (j1.x, j1.y),
    )
    left = pad_of(fps["J5"], "1").GetBoundingBox().GetLeft()
    y = mm(ORIGIN[1] + 1.6)
    v = (d.x + mm(1.05), mm(ORIGIN[1] + 2.2))
    add_track(board, net, (pcbnew.B_Cu, MAIN_TRACK), (j5.x, j5.y), (left + mm(0.3), y), (v[0] + mm(0.6), y), v)
    add_via(board, net, *v)
    add_track(board, net, (pcbnew.F_Cu, MAIN_TRACK), v, (v[0], d.y), (d.x, d.y))


def preroute_ties(board, fps):
    """Short connections where Freerouting fails:
    - U4 (LIS2DH12): 3V3 pins 9–10–2–3 (CS, SA0) and GND pins 5–6–7–8
    - U3 (LDO TPS7A2633): see preroute_ldo()
    - OUT_A to the detection resistors R3/R5: on In2 from the output via upwards, via, then R3.1 – R5.1
    """
    # LIS2DH12: 3V3 (9–10, 2–9 under the package, 2–3 for SA0) and the GND pins 5–8 connected; so only SCL, 3V3, SDA, INT
    # and GND go outside
    for ref, a, b in (
        ("U4", "9", "10"),
        ("U4", "2", "9"),
        ("U4", "2", "3"),
        ("U4", "5", "6"),
        ("U4", "6", "7"),
        ("U4", "7", "8"),
    ):
        pa, pb = pad_of(fps[ref], a), pad_of(fps[ref], b)
        add_track(
            board,
            pa.GetNet(),
            (pcbnew.F_Cu, 0.2),
            (pa.GetPosition().x, pa.GetPosition().y),
            (pb.GetPosition().x, pb.GetPosition().y),
        )
    preroute_ldo(board, fps)
    out_a = pad_of(fps["U2"], "2")
    va = (out_a.GetPosition().x + mm(1.15), out_a.GetPosition().y)
    r3, r5 = pad_of(fps["R3"], "1").GetPosition(), pad_of(fps["R5"], "1").GetPosition()
    v = (r3.x + mm(0.27), r3.y - mm(0.85))
    # on In2 (previously B.Cu): the bottom side stays free for J7
    add_track(board, out_a.GetNet(), (pcbnew.In2_Cu, STUB_TRACK), va, (v[0], va[1]), v)
    add_via(board, out_a.GetNet(), *v)
    add_track(board, out_a.GetNet(), (pcbnew.F_Cu, 0.25), v, (r3.x, r3.y), (r5.x, r5.y))


def ldo_thermal_vias(board, ldo, j2, gnd):
    """Two vias in the exposed pad (pad 7) of the LDO U3 (rev B, up to about 0.5 W with 4 x AA). Under the EP, on the
    bottom, lie the J2 pads (1.4 mm, pitch 2.54 mm, gap 1.14 mm): the vias sit centred in the gap between pads 2 and 3,
    one above the other (0.55 mm apart = 0.25 mm hole to hole), 0.17-0.18 mm clear of the U3 pin rows."""
    ep = pad_of(ldo, "7").GetPosition()
    p2, p3 = pad_of(j2, "2").GetPosition(), pad_of(j2, "3").GetPosition()
    x = (p2.x + p3.x) // 2
    for dy in (-0.27, 0.28):
        add_via(board, gnd, x, ep.y + mm(dy))


def preroute_ldo(board, fps):
    """3.3 V LDO TPS7A2633 (rev B, docs/proposal-supply-standby.md), U3 with rotation 270 at (2.4, 4.97): EN (4),
    GND (5), IN (6) at y 5.86 towards the edge, PG (3), NC (2), OUT (1) at y 4.08 towards the centre. Locked tracks:
    - EN and IN straight up into the VSYS edge track at y VSYS_EDGE_Y (0.2 mm next to the 0.65 mm pitch pads), C8 pad 1
      up into the same track (0.3 mm): EN is tied to IN through the track, C8 sits 0.8 mm right of IN
    - C8 pad 2 (GND) west into the exposed pad, GND (5), NC (2) and PG (3) stubs into the exposed pad
    - OUT (1) down into C9 pad 1 (0.3 mm), the output capacitor right under the pin
    - 3V3 trunk west to J2 pad 1 (via, In2, via, B.Cu, 0.3 mm); the rest of 3V3 is left to the router"""
    u3 = fps["U3"]
    assert round(u3.GetOrientationDegrees()) % 360 == 270, "preroute_ldo expects U3 with 270°"

    def q(ref, num):
        p = pad_of(fps[ref], num).GetPosition()
        return p.x, p.y

    vsys = pad_of(u3, "6").GetNet()
    y_edge = mm(ORIGIN[1] + VSYS_EDGE_Y)
    for num in ("4", "6"):
        p = q("U3", num)
        add_track(board, vsys, (pcbnew.F_Cu, 0.2), p, (p[0], y_edge))
    c8 = q("C8", "1")
    add_track(board, vsys, (pcbnew.F_Cu, 0.3), c8, (c8[0], y_edge))
    ep = pad_of(u3, "7")
    bb = ep.GetBoundingBox()
    gnd = ep.GetNet()
    g8 = q("C8", "2")
    add_track(board, gnd, (pcbnew.F_Cu, 0.25), g8, (bb.GetRight() - mm(0.1), g8[1]))
    p = q("U3", "5")
    add_track(board, gnd, (pcbnew.F_Cu, 0.2), p, (p[0], bb.GetBottom() - mm(0.1)))
    for num in ("2", "3"):
        p = q("U3", num)
        add_track(board, gnd, (pcbnew.F_Cu, 0.2), p, (p[0], bb.GetTop() + mm(0.1)))
    out, c9 = q("U3", "1"), q("C9", "1")
    net3 = pad_of(u3, "1").GetNet()
    bend = (out[0], out[1] - mm(0.6))
    add_track(board, net3, (pcbnew.F_Cu, 0.3), out, bend, (c9[0], bend[1] - abs(c9[0] - out[0])), c9)
    # 3V3 trunk to the module side (otherwise the router connected the module cluster through a 40 mm detour around
    # the USB end, about 0.36 ohm): via left of the OUT track, 0.3 mm on In2 west under C9, via, B.Cu into J2 pad 1;
    # from there the router has the short B.Cu path along the +y edge to module pad 3 (as in the buck trial).
    v1 = rel(2.675, 3.375)
    v2 = rel(-1.775, 2.525)
    j2 = q("J2", "1")
    add_track(board, net3, (pcbnew.F_Cu, 0.3), (bend[0], bend[1]), v1)
    add_via(board, net3, *v1)
    add_track(board, net3, (pcbnew.In2_Cu, 0.3), v1, rel(2.025, 2.725), rel(-1.475, 2.725), v2)
    add_via(board, net3, *v2)
    add_track(board, net3, (pcbnew.B_Cu, 0.3), v2, (j2[0], v2[1] + (j2[0] - v2[0])), j2)


def preroute_usb(board, fps):
    """USB D+/D- in advance, ESD U5 flow-through (ST DS4260 Fig. 7 "optimized layout", Fig. 18):
    J4 → U5 receptacle side (right, pin 1 D+ / pin 3 D-) → straight across under the package → U5 module side
    (left, pin 6 / pin 4) → via → on the bottom in the receptacle area → via → on top in the channel to the module
    (pads 18/17). No branch/stub.

    - D+ (A6–B6) connected via the band-side pad ends, from B6 diagonally to pin 1
    - D- (B7–A7) connected via the body-side pad ends; from B7 via, on the bottom under U5 to pin 3
    Expects U5 with rotation 180°.
    """
    usb, mod, esd = fps["J4"], fps["U1"], fps["U5"]
    assert round(esd.GetOrientationDegrees()) % 360 == 180, "preroute_usb expects U5 with 180°"

    def p(fp, num):
        q = pad_of(fp, num).GetPosition()
        return q.x, q.y

    a6, b6, a7, b7 = p(usb, "A6"), p(usb, "B6"), p(usb, "A7"), p(usb, "B7")
    dp, dm = pad_of(usb, "A6").GetNet(), pad_of(usb, "A7").GetNet()
    half = pad_of(usb, "A6").GetBoundingBox().GetHeight() // 2
    y_band, y_body = a6[1] - half - mm(0.3), a6[1] + half + mm(0.3)
    w = 0.2
    e1, e3, e4, e6 = p(esd, "1"), p(esd, "3"), p(esd, "4"), p(esd, "6")
    # pair connections at J4
    add_track(board, dp, (pcbnew.F_Cu, w), a6, (a6[0], y_band), (b6[0], y_band), b6)
    add_track(board, dm, (pcbnew.F_Cu, w), b7, (b7[0], y_body), (a7[0], y_body), a7)
    # D+: B6 → Pin 1 → Pin 6 → Via
    vp = (e6[0] - mm(1.51), e6[1] - mm(0.15))
    add_track(board, dp, (pcbnew.F_Cu, w), (b6[0], y_band), (e1[0] - mm(0.45), e1[1] + mm(0.45)), e1, e6, vp)
    add_via(board, dp, *vp)
    # D-: B7 → via → bottom → via right of pin 3 → pin 3 → pin 4 → via
    v1 = (b7[0] - mm(0.1), b7[1] - half - mm(0.93))
    v2 = (e3[0] + mm(1.06), e3[1] + mm(0.35))
    vm = (e4[0] - mm(1.56), e4[1] + mm(0.35))
    add_track(board, dm, (pcbnew.F_Cu, w), b7, v1)
    add_via(board, dm, *v1)
    add_track(board, dm, (pcbnew.B_Cu, w), v1, v2)
    add_via(board, dm, *v2)
    add_track(board, dm, (pcbnew.F_Cu, w), v2, e3, e4, vm)
    add_via(board, dm, *vm)
    # bottom: pair diagonally out of the band, horizontally past the solder tab S1 (through-hole pad), left of it
    # vertically upwards, then horizontally up to C10/R7 and by via up into the channel between
    # C2/R5 and the capacitor row C8–C10 (y = +0.83 D+, +1.11 D-). On the bottom only the area at the
    # receptacle is thus occupied; the board centre stays free on the bottom for north-south connections.
    m17, m18 = p(mod, "17"), p(mod, "18")
    tab = min((q for q in usb.Pads() if q.GetNumber() == "S1"), key=lambda q: (q.GetPosition().x, q.GetPosition().y))
    x_tab = tab.GetBoundingBox().GetLeft()
    yp1, ym1 = tab.GetBoundingBox().GetTop() - mm(0.47), tab.GetBoundingBox().GetTop() - mm(0.97)
    xp1, xm1 = x_tab - mm(0.33), x_tab - mm(0.83)
    yp, ym = mm(ORIGIN[1] - 0.6), mm(ORIGIN[1] - 1.05)
    up_p, up_m = rel(8.6, 0.4), rel(7.9, 1.4)  # vias into the channel
    add_track(board, dp, (pcbnew.B_Cu, w), vp, (vp[0] - (yp1 - vp[1]), yp1), (xp1, yp1), (xp1, yp), (up_p[0], yp), up_p)
    add_track(board, dm, (pcbnew.B_Cu, w), vm, (vm[0] - (ym1 - vm[1]), ym1), (xm1, ym1), (xm1, ym), (up_m[0], ym), up_m)
    add_via(board, dp, *up_p)
    add_via(board, dm, *up_m)
    wk = 0.15  # narrower in the channel so that a third track fits
    cp = mm(ORIGIN[1] + 0.85)  # 0.15 mm clearance to R5
    cm = cp + mm(wk + RULES["clearance"])  # +1,13
    xc = mm(ORIGIN[0] - 1.1)  # end of the channel in front of the 0402 row
    add_track(
        board, dp, (pcbnew.F_Cu, wk), up_p, (up_p[0] - (cp - up_p[1]), cp), (xc, cp), (xc - (cp - m18[1]), m18[1]), m18
    )
    add_track(
        board,
        dm,
        (pcbnew.F_Cu, wk),
        up_m,
        (up_m[0] - (up_m[1] - cm), cm),
        (m17[0] + mm(0.6), cm),
        (m17[0] + mm(0.3), m17[1]),
        m17,
    )


def preroute_all(board, fps, gnd):
    """All pre-routing in the order gen_main_pcb.py has always used."""
    thermal_vias(board, fps["U2"], gnd)
    ldo_thermal_vias(board, fps["U3"], fps["J2"], gnd)  # LDO EP (rev B)
    preroute_outputs(board, fps["U2"], fps["BT1"], fps["BT2"])
    preroute_supply(board, fps)
    preroute_usb(board, fps)
    preroute_vbus(board, fps)
    preroute_cc(board, fps)
    preroute_vbus_branches(board, fps)
    preroute_right_end(board, fps)
    preroute_ties(board, fps)
    preroute_bat_in(board, fps)
    preroute_battery_vsys(board, fps)
    preroute_adc_stubs(board, fps)
    preroute_led_ldo(board, fps)
