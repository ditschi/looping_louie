#!/usr/bin/env python3
"""Überträgt den Schaltplan auf die Platine und platziert die Bauteile nach der Tabelle unten.

- liest die Netzliste des Schaltplans (kicad-cli)
- setzt Footprints mit Netzen und Schaltplan-Verknüpfung (für den DRC-Abgleich)
- setzt Designregeln, Netzklassen und die Sperrfläche unter der Antenne
- Leiterbahnen werden NICHT gezogen (siehe docs/offene-punkte.md)

Muss mit dem System-Python laufen, das das KiCad-Modul pcbnew enthält.
Aufruf (über just):  just pcb

Achtung: entfernt alle Footprints, Leiterbahnen und Zonen der Platine und setzt sie neu.
"""
import re
import subprocess
import tempfile
from pathlib import Path

import pcbnew

from sexpr import block_end

HARDWARE = Path(__file__).resolve().parent.parent
BOARD_DIR = HARDWARE / "main-board"
SCH = BOARD_DIR / "louie-main.kicad_sch"
PCB = BOARD_DIR / "louie-main.kicad_pcb"
KICAD_FOOTPRINTS = Path("/usr/share/kicad/footprints")
PROJECT_FP_LIBS = {"lcsc": HARDWARE / "lib" / "lcsc.pretty", "louie": HARDWARE / "lib" / "louie.pretty"}

ORIGIN = (100.0, 75.0)  # Platinenmitte (wie board_outline.py)
BOARD_L, BOARD_W = 46.0, 13.5

# Designregeln: konservativ, damit praktisch jeder Hersteller sie im Standardpreis fertigt
RULES = dict(clearance=0.15, track=0.2, track_min=0.12, via_d=0.6, via_drill=0.3, edge=0.3)
POWER_NETS = ["/OUT_A", "/OUT_B", "/ISEN"]  # Motorstrom
POWER_TRACK = 0.4  # passt noch an die 0,65-mm-Pins des DRV8833; ca. 1,5 A bei 35 µm Kupfer
# Streifen am Rand (+y) im Antennenbereich, frei für die Leiterbahn zum Endkontakt MOT_A
ANTENNA_TRACK_STRIP = 1.2
SUPPLY_TRACK = 0.3  # VSYS, 3V3, GND
# Unterseite: links GND-Fläche, rechts ab hier VSYS-Fläche (mm relativ zur Platinenmitte)
VSYS_SPLIT_X = 1.5



def load_placement(variant):
    """Platzierungstabelle aus placement_<variante>.py: Referenz -> (x, y, Drehung, Seite).
    Koordinaten in mm relativ zur Platinenmitte, x entlang der Länge, Seite "F" oder "B"."""
    import importlib
    return importlib.import_module(f"placement_{variant}").PLACEMENT


def mm(v):
    return pcbnew.FromMM(v)


def pos(x, y):
    return pcbnew.VECTOR2I(mm(ORIGIN[0] + x), mm(ORIGIN[1] + y))


def read_netlist():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "net.net"
        subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr",
                        "-o", str(out), str(SCH)], check=True, capture_output=True)
        text = out.read_text()
    comps = {}
    for m in re.finditer(r"\(comp \(ref \"([^\"]+)\"\)", text):
        block = text[m.start():block_end(text, m.start())]
        comps[m.group(1)] = dict(
            value=re.search(r'\(value "([^"]*)"\)', block).group(1),
            footprint=re.search(r'\(footprint "([^"]*)"\)', block).group(1),
            uuid=re.findall(r'\(tstamps "([^"]*)"\)', block)[-1],
        )
    nets = {}
    for m in re.finditer(r"\(net \(code \"\d+\"\) \(name \"([^\"]*)\"\)", text):
        block = text[m.start():block_end(text, m.start())]
        nets[m.group(1)] = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', block)
    return comps, nets


def load_footprint(lib_id):
    nick, name = lib_id.split(":")
    lib = PROJECT_FP_LIBS.get(nick, KICAD_FOOTPRINTS / f"{nick}.pretty")
    fp = pcbnew.FootprintLoad(str(lib), name)
    if fp is None:
        raise RuntimeError(f"Footprint {lib_id} nicht gefunden")
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    return fp


def clear_board(board):
    for fp in list(board.GetFootprints()):
        board.Delete(fp)
    for t in list(board.GetTracks()):
        board.Delete(t)
    for z in list(board.Zones()):
        board.Delete(z)


def setup_rules(board):
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.m_TrackMinWidth = mm(RULES["track_min"])
    ds.m_MinClearance = mm(RULES["clearance"])
    ds.m_ViasMinSize = mm(RULES["via_d"])
    ds.m_MinThroughDrill = mm(RULES["via_drill"])
    ds.m_CopperEdgeClearance = mm(RULES["edge"])
    ns = ds.m_NetSettings
    default = ns.GetDefaultNetclass()
    default.SetClearance(mm(RULES["clearance"]))
    default.SetTrackWidth(mm(RULES["track"]))
    default.SetViaDiameter(mm(RULES["via_d"]))
    default.SetViaDrill(mm(RULES["via_drill"]))
    power = pcbnew.NETCLASS("Power")
    power.SetClearance(mm(RULES["clearance"]))
    power.SetTrackWidth(mm(POWER_TRACK))
    power.SetViaDiameter(mm(RULES["via_d"]))
    power.SetViaDrill(mm(RULES["via_drill"]))
    ns.SetNetclass("Power", power)
    for net in POWER_NETS:
        ns.SetNetclassPatternAssignment(net, "Power")
    # VSYS: verteilt über die VSYS-Fläche unten, Zuleitungen zu den 0402-Pads etwas schmaler
    supply = pcbnew.NETCLASS("Supply")
    supply.SetClearance(mm(RULES["clearance"]))
    supply.SetTrackWidth(mm(SUPPLY_TRACK))
    supply.SetViaDiameter(mm(RULES["via_d"]))
    supply.SetViaDrill(mm(RULES["via_drill"]))
    ns.SetNetclass("Supply", supply)
    for net in ("/VSYS", "/+3V3", "/GND"):
        ns.SetNetclassPatternAssignment(net, "Supply")


def antenna_keepout(board, module):
    """Sperrfläche (Kupfer, Vias, Bauteile) unter dem Antennenteil des ESP-Moduls, beide Lagen."""
    crt = module.GetCourtyard(pcbnew.F_CrtYd).BBox()
    pad_left = min(p.GetBoundingBox().GetLeft() for p in module.Pads())
    pad_right = max(p.GetBoundingBox().GetRight() for p in module.Pads())
    # Die Antenne liegt auf der Seite, auf der das Modul am weitesten über die Pads hinausragt.
    # Die Sperrfläche reicht von dort bis zum Platinenende.
    if pad_left - crt.GetLeft() > crt.GetRight() - pad_right:
        x0, x1 = crt.GetLeft(), pad_left - mm(0.5)
    else:
        x0, x1 = pad_right + mm(0.5), crt.GetRight()
    y0, y1 = mm(ORIGIN[1] - BOARD_W / 2), mm(ORIGIN[1] + BOARD_W / 2 - ANTENNA_TRACK_STRIP)

    def rule_area(name, layers, footprints, xa=None, xb=None, tracks=True, ya=None, yb=None):
        xa, xb = x0 if xa is None else xa, x1 if xb is None else xb
        ya, yb = y0 if ya is None else ya, y1 if yb is None else yb
        zone = pcbnew.ZONE(board)
        zone.SetIsRuleArea(True)
        zone.SetZoneName(name)
        zone.SetLayerSet(layers)
        zone.SetDoNotAllowTracks(tracks)
        zone.SetDoNotAllowVias(True)
        zone.SetDoNotAllowCopperPour(True)
        zone.SetDoNotAllowPads(footprints)
        zone.SetDoNotAllowFootprints(footprints)
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in [(xa, ya), (xb, ya), (xb, yb), (xa, yb)]:
            outline.Append(x, y)
        board.Add(zone)

    rule_area("Antenne", pcbnew.LSET.AllCuMask(), footprints=False)
    bottom = pcbnew.LSET()
    bottom.AddLayer(pcbnew.B_Cu)
    rule_area("Antenne unten", bottom, footprints=True)
    # Platinenende vor der Antenne: keine Kupferfläche und keine Vias, aber Endkontakt und
    # dessen Leiterbahn erlaubt
    if x0 > mm(ORIGIN[0] - BOARD_L / 2):
        rule_area("Antenne Ende", pcbnew.LSET.AllCuMask(), footprints=False,
                  xa=mm(ORIGIN[0] - BOARD_L / 2), xb=x0, tracks=False,
                  ya=mm(ORIGIN[1] - BOARD_W / 2), yb=mm(ORIGIN[1] + BOARD_W / 2))
    return pcbnew.ToMM(x1 - x0)


def thermal_vias(board, driver, gnd):
    """Vias im Thermal-Pad des DRV8833 zur Massefläche unten (0,3 mm, gängige Herstellergröße)."""
    ep = next(p for p in driver.Pads() if p.GetNumber() == "17" and p.GetSize().x > mm(2))
    cx, cy = ep.GetPosition().x, ep.GetPosition().y
    horizontal = driver.GetOrientationDegrees() % 180 == 0
    for dx, dy in [(-0.8, -1.4), (0.8, -1.4), (-0.8, 0), (0.8, 0), (-0.8, 1.4), (0.8, 1.4)]:
        if horizontal:
            dx, dy = dy, dx
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(cx + mm(dx), cy + mm(dy)))
        via.SetWidth(mm(RULES["via_d"]))
        via.SetDrill(mm(RULES["via_drill"]))
        via.SetNet(gnd)
        via.SetLocked(True)
        board.Add(via)


def add_track(board, net, layer, width, *points):
    """Gesperrte Leiterbahn durch die Punkte (absolute Koordinaten in nm)."""
    for a, b in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(*a))
        track.SetEnd(pcbnew.VECTOR2I(*b))
        track.SetLayer(layer)
        track.SetWidth(mm(width))
        track.SetNet(net)
        track.SetLocked(True)
        board.Add(track)


def add_via(board, net, x, y):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(x, y))
    via.SetWidth(mm(RULES["via_d"]))
    via.SetDrill(mm(RULES["via_drill"]))
    via.SetNet(net)
    via.SetLocked(True)
    board.Add(via)


def preroute_driver(board, driver):
    """Verbindet die parallel geschalteten Pinpaare des DRV8833 vorab (Freerouting scheitert daran).

    - OUT2: Pins 4 und 5 liegen nebeneinander → kurze Brücke oben
    - IN1 (Pins 9/16) liegen an den Enden der Eingangsreihe → Vias in Reihenrichtung außerhalb
      der Reihe, Verbindung unten direkt unter der Pinreihe
    - IN2 (Pins 10/15) → Vias zum Platinenrand hin, Verbindung unten parallel dazu
    Funktioniert für jede Drehung um 0/90/180/270°.
    """
    center = driver.GetPosition()
    pad = {p.GetNumber(): p for p in driver.Pads() if max(p.GetSize().x, p.GetSize().y) < mm(2)}
    p4, p5 = pad["4"].GetPosition(), pad["5"].GetPosition()
    add_track(board, pad["4"].GetNet(), pcbnew.F_Cu, 0.3, (p4.x, p4.y), (p5.x, p5.y))

    def sign(v):
        return 1 if v > 0 else -1

    for (a, b), mode in [(("16", "9"), "row"), (("15", "10"), "out")]:
        net = pad[a].GetNet()
        ends = []
        for num in (a, b):
            pp = pad[num].GetPosition()
            dx, dy = pp.x - center.x, pp.y - center.y
            row_along_x = abs(pad["9"].GetPosition().y - pad["16"].GetPosition().y) < mm(0.1)
            if mode == "row":   # entlang der Reihe nach außen
                off = (sign(dx) * mm(0.88), 0) if row_along_x else (0, sign(dy) * mm(0.88))
            else:               # senkrecht zur Reihe nach außen (zum Rand)
                off = (0, sign(dy) * mm(1.24)) if row_along_x else (sign(dx) * mm(1.24), 0)
            vx, vy = pp.x + off[0], pp.y + off[1]
            add_track(board, net, pcbnew.F_Cu, 0.2, (pp.x, pp.y), (vx, vy))
            add_via(board, net, vx, vy)
            ends.append((vx, vy))
        add_track(board, net, pcbnew.B_Cu, 0.2, *ends)


def pad_of(footprint, number):
    return next(p for p in footprint.Pads() if p.GetNumber() == number)


def module_ground_vias(board, module):
    """GND-Vias in den Mittel-Pads des ESP-Moduls (wie von Espressif für die Massefläche empfohlen);
    die obere Massefläche erreicht die Pads unter dem Modul nicht."""
    gnd = None
    for pad in module.Pads():
        if pad.GetNumber() == "49" and min(pad.GetSize().x, pad.GetSize().y) > mm(0.8):
            gnd = pad.GetNet()
            q = pad.GetPosition()
            add_via(board, gnd, q.x, q.y)


def ground_via_at_pad(board, footprint, number, dx, dy, width=0.4):
    """Festes GND-Via neben einem Pad (dx/dy in mm relativ zur Padmitte) mit Stichleitung."""
    pad = pad_of(footprint, number)
    q = pad.GetPosition()
    v = (q.x + mm(dx), q.y + mm(dy))
    add_track(board, pad.GetNet(), pcbnew.F_Cu, width, (q.x, q.y), v)
    add_via(board, pad.GetNet(), *v)


def preroute_supply(board, fps):
    """VSYS vorab routen: Sammelschiene oben vom Kabel-Via über LDO, C2, C1 bis C4/C5, Abzweige zu
    C8, R6, C3 und über ein Via-Paar unten herum zum VM-Pin 12 des DRV8833 (der zwischen den
    Eingangspins liegt) samt VCP-Kondensator C7."""
    def at(ref, num):
        q = pad_of(fps[ref], num).GetPosition()
        return q.x, q.y

    net = pad_of(fps["C4"], "1").GetNet()
    bus_y = at("C1", "1")[1] - mm(0.5)                 # Unterkante der C1/C2-Pads
    c4, c5, c8 = at("C4", "1"), at("C5", "1"), at("C8", "1")
    u3_vin, u3_en = at("U3", "1"), at("U3", "3")
    j1 = at("J1", "1")
    via_j1 = (u3_en[0] + mm(1.1), bus_y)
    w, wb = POWER_TRACK, SUPPLY_TRACK
    add_track(board, net, pcbnew.F_Cu, w, (c4[0], bus_y), via_j1)
    add_via(board, net, *via_j1)
    add_track(board, net, pcbnew.B_Cu, w, via_j1, j1)
    add_track(board, net, pcbnew.F_Cu, wb, c5, c4, (c4[0], bus_y))
    add_track(board, net, pcbnew.F_Cu, wb, u3_vin, (u3_vin[0] - mm(1.05), u3_vin[1]), (u3_vin[0] - mm(1.05), bus_y))
    add_track(board, net, pcbnew.F_Cu, wb, c8, (c8[0], bus_y))
    # Abzweig zu R6 und C3
    r6, c3 = at("R6", "1"), at("C3", "1")
    add_track(board, net, pcbnew.F_Cu, wb, c5, (c5[0], c5[1] + mm(1.5)), (r6[0], r6[1] - mm(0.4)), r6)
    add_track(board, net, pcbnew.F_Cu, wb, r6, (r6[0], r6[1] + mm(0.9)), (c3[0] - mm(0.7), r6[1] + mm(0.9)), c3)
    # VM-Pin 12 und C7: Via unter dem Pin, unten nach rechts, Via hoch zur Schiene
    vm, c7 = at("U2", "12"), at("C7", "2")
    v1 = (vm[0], vm[1] - mm(1.14))
    v2 = (c4[0] + mm(0.48), v1[1])
    add_track(board, net, pcbnew.F_Cu, w, vm, v1, c7)
    add_via(board, net, *v1)
    add_track(board, net, pcbnew.B_Cu, w, v1, v2)
    add_via(board, net, *v2)
    add_track(board, net, pcbnew.F_Cu, w, v2, (c4[0], bus_y))


def preroute_outputs(board, driver, contact_a, contact_b, shunt, pulldown_b, isen_filter, sense_r):
    """Ausgangsseite des DRV8833 vorab routen (Pinfolge der Ausgangsreihe: nSLEEP, A, ISEN, B, B,
    ISEN, A, nFAULT – verschachtelt, daran scheitert der Autorouter).

    - ISEN: Pins 3 und 6 senkrecht nach außen auf einen Querbalken (darunter sitzt der Shunt R1)
    - OUT_B: von der Brücke 4–5 ein Via, unten weiter zum Endkontakt B
    - OUT_A: Pins 2 und 7 je ein Via, unten verbunden und weiter zum Endkontakt A
      (durch den Randstreifen neben der Antenne)
    Erwartet: Ausgangsreihe zeigt nach +y (Drehung 90°).
    """
    assert round(driver.GetOrientationDegrees()) % 360 == 90, "preroute_outputs erwartet Drehung 90°"
    pad = {p.GetNumber(): p for p in driver.Pads() if max(p.GetSize().x, p.GetSize().y) < mm(2)}
    row_y = pad["2"].GetPosition().y
    x = {n: pad[n].GetPosition().x for n in ("2", "3", "4", "5", "6", "7")}
    via_y, bar_y, link_y = row_y + mm(1.29), row_y + mm(2.05), row_y + mm(0.44)
    isen, out_a, out_b = pad["3"].GetNet(), pad["2"].GetNet(), pad["4"].GetNet()
    w = POWER_TRACK

    # ISEN
    add_track(board, isen, pcbnew.F_Cu, w, (x["3"], row_y), (x["3"], bar_y), (x["6"], bar_y), (x["6"], row_y))
    s1 = pad_of(shunt, "1").GetPosition()
    add_track(board, isen, pcbnew.F_Cu, w, (x["3"], bar_y), (s1.x, s1.y))
    f1 = pad_of(isen_filter, "1").GetPosition()  # Abgriff zum Strommess-Filter R8
    add_track(board, isen, pcbnew.F_Cu, SUPPLY_TRACK, (x["6"], bar_y), (f1.x - mm(0.32), bar_y), (f1.x, f1.y))
    # OUT_B
    mid_b = (x["4"] + x["5"]) // 2
    add_track(board, out_b, pcbnew.F_Cu, 0.3, (mid_b, row_y), (mid_b, via_y))
    add_via(board, out_b, mid_b, via_y)
    cb = next(iter(contact_b.Pads())).GetPosition()
    low_y = mm(ORIGIN[1] + BOARD_W / 2 - 1.15)
    add_track(board, out_b, pcbnew.B_Cu, w, (mid_b, via_y), (mid_b, low_y), (cb.x - mm(0.8), low_y), (cb.x, low_y - mm(0.8)),
              (cb.x, cb.y))
    r4 = pad_of(pulldown_b, "1").GetPosition()  # Pull-down R4 per Via auf die OUT_B-Bahn unten
    add_track(board, out_b, pcbnew.F_Cu, 0.3, (r4.x, r4.y), (r4.x, low_y))
    add_via(board, out_b, r4.x, low_y)
    # OUT_A
    for n in ("2", "7"):
        add_track(board, out_a, pcbnew.F_Cu, w, (x[n], row_y), (x[n], via_y))
        add_via(board, out_a, x[n], via_y)
    add_track(board, out_a, pcbnew.B_Cu, w, (x["2"], via_y), (x["2"], link_y), (x["7"], link_y), (x["7"], via_y))
    ca = next(iter(contact_a.Pads())).GetPosition()
    strip_y = mm(ORIGIN[1] + BOARD_W / 2 - ANTENNA_TRACK_STRIP / 2)
    run_y = mm(ORIGIN[1] + 4.95)
    add_track(board, out_a, pcbnew.B_Cu, w, (ca.x, ca.y), (ca.x, strip_y), (mm(ORIGIN[0] - 14.0), strip_y),
              (mm(ORIGIN[0] - 12.85), run_y), (x["2"] - mm(1.8), run_y), (x["2"], via_y))
    # SENSE-Schutzwiderstand R5 holt OUT_A per Via von der Bahn unten
    r5 = pad_of(sense_r, "1").GetPosition()
    add_track(board, out_a, pcbnew.F_Cu, SUPPLY_TRACK, (r5.x, r5.y), (r5.x, run_y))
    add_via(board, out_a, r5.x, run_y)


def copper_zones(board, gnd, vsys):
    """Kupferflächen: GND oben und unten über die ganze Platine.

    (Eine VSYS-Fläche unten wurde verworfen: Freerouting zerschneidet sie mit Signalen in Inseln.)
    """
    x0, x1 = ORIGIN[0] - BOARD_L / 2, ORIGIN[0] + BOARD_L / 2
    y0, y1 = ORIGIN[1] - BOARD_W / 2, ORIGIN[1] + BOARD_W / 2
    split = ORIGIN[0] + VSYS_SPLIT_X
    for layer, net, name, xa, xb, prio in [
        (pcbnew.F_Cu, gnd, "GND oben", x0, x1, 0),
        (pcbnew.B_Cu, gnd, "GND unten", x0, x1, 0),
    ]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(net)
        zone.SetZoneName(name)
        zone.SetAssignedPriority(prio)
        zone.SetLocalClearance(mm(0.2))
        zone.SetMinThickness(mm(0.2))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefGap(mm(0.2))
        zone.SetThermalReliefSpokeWidth(mm(0.3))
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in [(xa, y0), (xb, y0), (xb, y1), (xa, y1)]:
            outline.Append(mm(x), mm(y))
        board.Add(zone)


def main(variant):
    placement = load_placement(variant)
    comps, nets = read_netlist()
    missing = set(comps) - set(placement)
    if missing:
        raise SystemExit(f"Keine Platzierung für: {', '.join(sorted(missing))}")

    board = pcbnew.LoadBoard(str(PCB))
    clear_board(board)
    setup_rules(board)

    netinfo = {}
    for name in nets:
        item = pcbnew.NETINFO_ITEM(board, name)
        board.Add(item)
        netinfo[name] = item
    pad_net = {(ref, pin): net for net, nodes in nets.items() for ref, pin in nodes}

    footprints = {}
    for ref, comp in sorted(comps.items()):
        fp = load_footprint(comp["footprint"])
        board.Add(fp)
        fp.SetReference(ref)
        fp.SetValue(comp["value"])
        fp.SetPath(pcbnew.KIID_PATH(f"/{comp['uuid']}"))
        for pad in fp.Pads():
            net = pad_net.get((ref, pad.GetNumber()))
            if net:
                pad.SetNet(netinfo[net])
        x, y, rot, side = placement[ref]
        fp.SetPosition(pos(x, y))
        fp.SetOrientationDegrees(rot)
        # Bezeichner nur auf der Fab-Ebene: für Bestückungsdruck ist auf 13,5 mm kein Platz
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.5), mm(0.5)))
        fp.Reference().SetTextThickness(mm(0.08))
        fp.Reference().SetPosition(fp.GetPosition())
        fp.Value().SetVisible(False)
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            fp.Reference().SetLayer(pcbnew.B_Fab)
        footprints[ref] = fp

    keepout = antenna_keepout(board, footprints["U1"])
    thermal_vias(board, footprints["U2"], netinfo["/GND"])
    preroute_outputs(board, footprints["U2"], footprints["BT1"], footprints["BT2"], footprints["R1"], footprints["R4"],
                     footprints["R8"], footprints["R5"])
    preroute_supply(board, footprints)
    module_ground_vias(board, footprints["U1"])
    ground_via_at_pad(board, footprints["R1"], "2", 0.84, -0.35)   # Shunt: Motor-Rückstrom nach GND
    ground_via_at_pad(board, footprints["C12"], "2", 0.0, -1.0, width=0.25)
    ground_via_at_pad(board, footprints["C10"], "2", 0.0, -0.9, width=0.25)
    ground_via_at_pad(board, footprints["C15"], "2", 0.0, 0.9, width=0.25)
    copper_zones(board, netinfo["/GND"], netinfo["/VSYS"])
    pcbnew.SaveBoard(str(PCB), board)
    top = sum(1 for p in placement.values() if p[3] == "F")
    print(f"{PCB.relative_to(HARDWARE.parent)}: Variante '{variant}', {len(comps)} Bauteile "
          f"({top} oben, {len(comps) - top} unten), Antennen-Sperrfläche {keepout:.1f} mm")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "einseitig")
