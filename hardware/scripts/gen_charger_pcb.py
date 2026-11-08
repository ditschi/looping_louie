#!/usr/bin/env python3
"""Creates the charger board: outline, components per the table below, design rules, bridge, ground pours.

Same format as the main board (46 mm long), but only 12.5 mm wide and 1.6 mm thick: in the AA compartment the
board stands **on edge**, the horizontal USB-C receptacle on the long edge points upwards out of the compartment
(plug across the cell axis). In the base it is glued on flat, the receptacle then points through a
hole in the side wall. See docs/charger-board.md.

Layout from left to right (mating side of the receptacle at -y = "top"):
  USB-C + ESD + CC resistors | charge controller, charge indicator, load sharing | JST-PH, battery solder pads |
  cable solder pads
Bottom: only the bridge (wide track between the end contacts) and ground pour.

Must run with the system Python that contains the KiCad module pcbnew.
Usage (via just):  just charger-pcb      afterwards: just route charger-board

Warning: removes all footprints, tracks and zones of the board and places them anew.
"""
from pathlib import Path

import pcbnew

import board_outline
import gen_main_pcb as base
from gen_main_pcb import add_track, add_via, ground_via_at_pad, mm, pad_of

HARDWARE = Path(__file__).resolve().parent.parent
SCH = HARDWARE / "charger-board" / "louie-charger.kicad_sch"
PCB = HARDWARE / "charger-board" / "louie-charger.kicad_pcb"
ORIGIN = board_outline.ORIGIN_MM
BOARD_L, BOARD_W, THICKNESS = 46.0, 12.5, 1.6
EDGE_Y = -BOARD_W / 2   # mating side of the USB-C receptacle
BRIDGE_TRACK = 1.0      # motor current up to 2 A: approx. 20 mOhm over 43 mm, main board uses 0.4 mm
BRIDGE_Y = 5.45         # close to the edge so that GND vias still fit above it

USB_X = -15.0
# reference -> (x, y, rotation, side); mm relative to the board centre
PLACEMENT = {
    # USB-C: opening flush with the -y edge (front edge in the footprint at +3.65 mm)
    "J101": (USB_X, EDGE_Y + 3.65, 180, "F"),
    "U102": (USB_X, 4.5, 0, "F"),          # ESD directly behind the data pins
    "R101": (USB_X + 3.5, 4.5, 90, "F"),   # CC1
    "R102": (USB_X - 3.3, 4.5, 90, "F"),   # CC2
    # row at the mating edge: charge indicator (visible from above) and gate pull-down
    "D101": (-7.0, -5.2, 0, "F"),
    "R104": (-4.0, -5.2, 180, "F"),
    "R105": (-1.0, -5.2, 0, "F"),
    # charge controller
    "C101": (-7.2, -1.2, 90, "F"),
    "U101": (-3.6, -1.2, 0, "F"),
    "C102": (-0.2, -1.2, 90, "F"),
    "R103": (1.8, -1.2, 90, "F"),
    # load sharing
    "D102": (-5.4, 4.3, 180, "F"),         # cathode (VSYS) on the right
    "Q101": (0.8, 4.3, 0, "F"),
    "C103": (4.0, 4.3, 90, "F"),
    # battery: JST-PH, opening also towards the -y edge; next to it solder pads as alternative
    "J102": (10.5, EDGE_Y + 5.1, 180, "F"),
    "TP101": (17.0, -3.4, 0, "F"),         # battery +
    "TP102": (17.0, 3.4, 0, "F"),          # battery -
    # cable to the main board (pinout as J1 there)
    "J103": (20.4, 0.5, 0, "F"),
    # bottom side: end contacts of the bridge
    "BT101": (-21.4, 0, 0, "B"),
    "BT102": (21.4, 0, 0, "B"),
}

SILK = [  # (text, x, y, size, side[, rotation])
    ("+", 12.6, 4.4, 0.8, "F"),            # pin 1 of the JST = battery +
    ("+", 15.2, -3.4, 0.8, "F"),           # solder pads TP101 / TP102
    ("-", 15.2, 3.4, 0.8, "F"),
    ("V", 22.2, -2.5, 0.8, "F"),           # cable solder pads J103: VSYS, D+, D-, GND
    ("D+", 22.2, -0.5, 0.8, "F", 90),      # vertical, otherwise too wide for the edge
    ("D-", 22.2, 1.5, 0.8, "F", 90),
    ("G", 22.2, 3.5, 0.8, "F"),
    ("CHARGE", -7.0, -3.6, 0.8, "F"),
    ("Louie Charger v0.1", 0, -2.0, 1.0, "B"),
    ("Bridge", 0, BRIDGE_Y, 0.8, "B"),
]


def pos(x, y):
    return pcbnew.VECTOR2I(mm(ORIGIN[0] + x), mm(ORIGIN[1] + y))


def setup_rules(board):
    """As the main board; net classes come from louie-charger.kicad_pro (Power 0.8 mm)."""
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.SetBoardThickness(mm(THICKNESS))
    ds.m_TrackMinWidth = mm(base.RULES["track_min"])
    ds.m_MinClearance = mm(base.RULES["clearance"])
    ds.m_ViasMinSize = mm(base.RULES["via_d"])
    ds.m_MinThroughDrill = mm(base.RULES["via_drill"])
    ds.m_CopperEdgeClearance = mm(base.RULES["edge"])


def add_text(board, text, x, y, size, side, angle=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetTextAngleDegrees(angle)
    t.SetText(text)
    t.SetPosition(pos(x, y))
    t.SetLayer(pcbnew.F_SilkS if side == "F" else pcbnew.B_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(max(0.1, size * 0.15)))
    if side == "B":
        t.SetMirrored(True)
    board.Add(t)


def preroute_bridge(board, fps):
    """Wide track on the bottom between the end contacts, past the THT tabs of the USB receptacle."""
    a, b = (pad_of(fps[r], "1").GetPosition() for r in ("BT101", "BT102"))
    y = mm(ORIGIN[1] + BRIDGE_Y)
    add_track(board, pad_of(fps["BT101"], "1").GetNet(), pcbnew.B_Cu, BRIDGE_TRACK,
              (a.x, a.y), (a.x, y), (b.x, y), (b.x, b.y))


def preroute_vbus(board, fps):
    """VBUS away from the fine USB pads (Freerouting cannot do this with 0.5 mm): a via behind each
    VBUS pad, on the bottom a common track to below the anode of D102, back up there."""
    usb = fps["J101"]
    net = pad_of(usb, "A4").GetNet()
    via_y = mm(ORIGIN[1] + 2.35)
    vias = []
    for num in ("A4", "A9"):
        q = pad_of(usb, num).GetPosition()
        add_track(board, net, pcbnew.F_Cu, 0.4, (q.x, q.y), (q.x, via_y))
        add_via(board, net, q.x, via_y)
        vias.append(q.x)
    anode = pad_of(fps["D102"], "2").GetPosition()
    add_track(board, net, pcbnew.B_Cu, 0.5, (min(vias), via_y), (anode.x, via_y))
    add_via(board, net, anode.x, via_y)
    add_track(board, net, pcbnew.F_Cu, 0.5, (anode.x, via_y), (anode.x, anode.y))
    # VBUS pin 5 of the ESD diode: via to its right, on the bottom onto the common track (on top CC1 would cross)
    pin5 = pad_of(fps["U102"], "5").GetPosition()
    v = (pin5.x + mm(1.11), pin5.y)
    add_track(board, net, pcbnew.F_Cu, 0.3, (pin5.x, pin5.y), v)
    add_via(board, net, *v)
    add_track(board, net, pcbnew.B_Cu, 0.4, v, (v[0], via_y), (max(vias), via_y))


def copper_zones(board, gnd):
    x0, x1 = ORIGIN[0] - BOARD_L / 2, ORIGIN[0] + BOARD_L / 2
    y0, y1 = ORIGIN[1] - BOARD_W / 2, ORIGIN[1] + BOARD_W / 2
    for layer, name in [(pcbnew.F_Cu, "GND top"), (pcbnew.B_Cu, "GND bottom")]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(gnd)
        zone.SetZoneName(name)
        zone.SetLocalClearance(mm(0.25))
        zone.SetMinThickness(mm(0.2))
        # fully connected: the fine GND pads of the USB receptacle would otherwise get only one thermal spoke
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            outline.Append(mm(x), mm(y))
        board.Add(zone)


def main():
    comps, nets = base.read_netlist(SCH)
    missing = set(comps) - set(PLACEMENT)
    if missing:
        raise SystemExit(f"No placement for: {', '.join(sorted(missing))}")

    board = pcbnew.LoadBoard(str(PCB)) if PCB.exists() else pcbnew.NewBoard(str(PCB))
    base.clear_board(board)
    for d in list(board.GetDrawings()):   # outline and texts are placed anew
        board.Delete(d)
    board_outline.draw_outline(board, BOARD_L, BOARD_W)
    setup_rules(board)

    netinfo = {}
    for name in nets:
        item = pcbnew.NETINFO_ITEM(board, name)
        board.Add(item)
        netinfo[name] = item
    pad_net = {(ref, pin): net for net, nodes in nets.items() for ref, pin in nodes}

    fps = {}
    for ref, comp in sorted(comps.items()):
        fp = base.load_footprint(comp["footprint"])
        board.Add(fp)
        fp.SetReference(ref)
        fp.SetValue(comp["value"])
        fp.SetPath(pcbnew.KIID_PATH(f"/{comp['uuid']}"))
        for pad in fp.Pads():
            net = pad_net.get((ref, pad.GetNumber()))
            if net:
                pad.SetNet(netinfo[net])
        x, y, rot, side = PLACEMENT[ref]
        fp.SetPosition(pos(x, y))
        fp.SetOrientationDegrees(rot)
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.5), mm(0.5)))
        fp.Reference().SetTextThickness(mm(0.08))
        fp.Reference().SetPosition(fp.GetPosition())
        fp.Value().SetVisible(False)
        # component silkscreen (outlines) stays, designators only on Fab
        for item in list(fp.GraphicalItems()):
            on_silk = item.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)
            # remove texts; for the USB receptacle also the outline lines (they run over the board edge)
            if on_silk and (item.GetClass() == "PCB_TEXT" or ref == "J101"):
                fp.Remove(item)
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            fp.Reference().SetLayer(pcbnew.B_Fab)
        fps[ref] = fp

    preroute_bridge(board, fps)
    preroute_vbus(board, fps)
    ground_via_at_pad(board, fps["U102"], "2", -1.06, -0.2, width=0.3)  # otherwise GND island between the pins
    copper_zones(board, netinfo["/GND"])
    for args in SILK:
        add_text(board, *args)
    pcbnew.SaveBoard(str(PCB), board)
    print(f"{PCB.relative_to(HARDWARE.parent)}: {BOARD_L} x {BOARD_W} x {THICKNESS} mm, {len(comps)} components")


if __name__ == "__main__":
    main()
