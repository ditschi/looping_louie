#!/usr/bin/env python3
"""Überträgt den Schaltplan auf die Platine und platziert die Bauteile nach der Tabelle unten.

- liest die Netzliste des Schaltplans (kicad-cli)
- setzt Footprints mit Netzen und Schaltplan-Verknüpfung (für den DRC-Abgleich)
- setzt Designregeln, Netzklassen und die Sperrfläche unter der Antenne
- routet vorab nur die kritischen Bahnen (Motorausgänge, VSYS/VBUS/BAT_IN, USB-Paar, kurze Brücken);
  den Rest übernimmt Freerouting (just route)

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

# Designregeln (docs/hauptplatine-c6.md, Abschnitt „Fertigungsregeln“): JLCPCB-Standardpreis für 2 Lagen,
# 1 oz ist 0,10/0,10 mm Bahn/Abstand, Via 0,3 mm Bohrung / 0,6 mm Durchmesser (Aufpreis erst bei Bohrung
# < 0,3 mm mit Durchmesser < 0,45 mm), Kupfer–Fräskante 0,2 mm, PTH–Bahn 0,28 mm. Hier mit Reserve:
# Abstand und Mindestbahn 0,13 mm (+30 %), Standardbahn 0,15 mm, Kantenabstand 0,3 mm, Loch–Kupfer 0,28 mm.
RULES = dict(clearance=0.13, track=0.15, track_min=0.13, via_d=0.6, via_drill=0.3, edge=0.3, hole_clearance=0.28,
             hole_to_hole=0.25, annular=0.15)
# Motorstrom und Einspeisung (bis 2 A). OUT_A/OUT_B und die Hauptwege von VBUS und BAT_IN sind vorgeroutet;
# die übrigen Anschlüsse dieser Netze (Erkennungswiderstände, Gate, Teiler, ESD) führen nur µA bis mA und
# bleiben wie ISEN (IPROPI) in der Standardklasse, damit Freerouting sie schmal führen kann.
POWER_NETS = ["/VSYS", "/BAT_IN"]
POWER_TRACK = 0.4  # ca. 1,5 A bei 35 µm Kupfer; an den 0,5-mm-Pins des DRV8213 nur kurze 0,3-mm-Stiche
STUB_TRACK = 0.3   # Stiche an Fine-Pitch-Pins
MAIN_TRACK = 0.5   # vorgeroutete VSYS-Hauptbahn (Schottky -> Puffer -> VM)
# Randstreifen im Antennenbereich, frei für die Leiterbahn OUT_A zum Endkontakt BT1. Kante -y, weil der
# DRV8213 an der Modulecke -y sitzt: OUT_A läuft so ohne Kreuzung unten am Rand entlang.
ANTENNA_TRACK_STRIP = 1.2
ANTENNA_TRACK_SIDE = -1
SUPPLY_TRACK = 0.25  # 3V3, GND (passt noch an die 0,5-mm-Pins von LIS2DH12/DRV8213)
EDGE_TRACK_Y = BOARD_W / 2 - 0.6  # Abstand der Randbahnen OUT_A/OUT_B von der Mitte (unten)
COL1_X = -1.9  # 0402-Reihe an den rechten Modulpins (placement_einseitig.COL1)



# Feste GND-Vias neben Pads (Referenz, Pad, dx, dy in mm)
GROUND_VIAS = []
# GND-Pins des DRV8213 (Pin 4 GND, Pin 7 GAINSEL) direkt aufs Thermal-Pad (dessen Vias führen nach unten)
EP_TIES = [("U2", "4", "9"), ("U2", "7", "9")]


def load_placement(variant):
    """Platzierungstabelle aus placement_<variante>.py: Referenz -> (x, y, Drehung, Seite).
    Koordinaten in mm relativ zur Platinenmitte, x entlang der Länge, Seite "F" oder "B"."""
    import importlib
    return importlib.import_module(f"placement_{variant}").PLACEMENT


def mm(v):
    return pcbnew.FromMM(v)


def pos(x, y):
    return pcbnew.VECTOR2I(mm(ORIGIN[0] + x), mm(ORIGIN[1] + y))


def read_netlist(sch=SCH):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "net.net"
        subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr",
                        "-o", str(out), str(sch)], check=True, capture_output=True)
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
    ds.m_HoleClearance = mm(RULES["hole_clearance"])
    ds.m_HoleToHoleMin = mm(RULES["hole_to_hole"])
    ds.m_ViasMinAnnularWidth = mm(RULES["annular"])
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
    # 3V3 und GND: Zuleitungen zu den 0402-Pads
    supply = pcbnew.NETCLASS("Supply")
    supply.SetClearance(mm(RULES["clearance"]))
    supply.SetTrackWidth(mm(SUPPLY_TRACK))
    supply.SetViaDiameter(mm(RULES["via_d"]))
    supply.SetViaDrill(mm(RULES["via_drill"]))
    ns.SetNetclass("Supply", supply)
    for net in ("/+3V3", "/GND"):
        ns.SetNetclassPatternAssignment(net, "Supply")


def antenna_keepout(board, module):
    """Sperrflächen unter dem Antennenteil des ESP-Moduls (docs/analyse-funk-controller.md 2.3, L2):

    - "Antenne": alle Lagen, keine Kupferfläche, keine Vias, keine Leiterbahnen
    - "Antenne Rand": Randstreifen (ANTENNA_TRACK_STRIP), alle Lagen, keine Kupferfläche und keine Vias,
      Leiterbahnen erlaubt (OUT_A zum Endkontakt). Früher sparte die Sperrfläche den Streifen ganz aus,
      dann lag oben ein GND-Streifen unter der Antenne.
    - "Antenne unten": keine Bauteile/Pads auf der Unterseite
    - "Antenne Ende": Platinenende vor der Antenne, keine Fläche und keine Vias, Endkontakt erlaubt
    """
    crt = module.GetCourtyard(pcbnew.F_CrtYd).BBox()
    pad_left = min(p.GetBoundingBox().GetLeft() for p in module.Pads())
    pad_right = max(p.GetBoundingBox().GetRight() for p in module.Pads())
    # Die Antenne liegt auf der Seite, auf der das Modul am weitesten über die Pads hinausragt.
    # Die Sperrfläche reicht von dort bis zum Platinenende.
    if pad_left - crt.GetLeft() > crt.GetRight() - pad_right:
        x0, x1 = crt.GetLeft(), pad_left - mm(0.5)
    else:
        x0, x1 = pad_right + mm(0.5), crt.GetRight()
    top, bot = mm(ORIGIN[1] - BOARD_W / 2), mm(ORIGIN[1] + BOARD_W / 2)
    strip = mm(ANTENNA_TRACK_STRIP)
    if ANTENNA_TRACK_SIDE < 0:
        main_y, strip_y = (top + strip, bot), (top, top + strip)
    else:
        main_y, strip_y = (top, bot - strip), (bot - strip, bot)

    def rule_area(name, layers, footprints, ys, xa=None, xb=None, tracks=True):
        xa, xb = x0 if xa is None else xa, x1 if xb is None else xb
        ya, yb = ys
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

    rule_area("Antenne", pcbnew.LSET.AllCuMask(), False, main_y)
    rule_area("Antenne Rand", pcbnew.LSET.AllCuMask(), False, strip_y, tracks=False)
    bottom = pcbnew.LSET()
    bottom.AddLayer(pcbnew.B_Cu)
    rule_area("Antenne unten", bottom, True, main_y)
    if x0 > mm(ORIGIN[0] - BOARD_L / 2):
        rule_area("Antenne Ende", pcbnew.LSET.AllCuMask(), False, (top, bot),
                  xa=mm(ORIGIN[0] - BOARD_L / 2), xb=x0, tracks=False)
    return pcbnew.ToMM(x1 - x0)


def edge_keepout(board, width=RULES["edge"] + 0.02):
    """Randstreifen ohne Leiterbahnen und Vias (Freerouting kennt den Kantenabstand nicht)."""
    x0, x1 = mm(ORIGIN[0] - BOARD_L / 2), mm(ORIGIN[0] + BOARD_L / 2)
    y0, y1 = mm(ORIGIN[1] - BOARD_W / 2), mm(ORIGIN[1] + BOARD_W / 2)
    w = mm(width)
    for xa, ya, xb, yb in [(x0, y0, x1, y0 + w), (x0, y1 - w, x1, y1), (x0, y0, x0 + w, y1), (x1 - w, y0, x1, y1)]:
        zone = pcbnew.ZONE(board)
        zone.SetIsRuleArea(True)
        zone.SetZoneName("Rand")
        zone.SetLayerSet(pcbnew.LSET.AllCuMask())
        zone.SetDoNotAllowTracks(True)
        zone.SetDoNotAllowVias(True)
        zone.SetDoNotAllowCopperPour(False)
        zone.SetDoNotAllowPads(False)
        zone.SetDoNotAllowFootprints(False)
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in [(xa, ya), (xb, ya), (xb, yb), (xa, yb)]:
            outline.Append(x, y)
        board.Add(zone)


def thermal_vias(board, driver, gnd):
    """Zwei Vias im Thermal-Pad (Pad 9, 0,9 × 1,6 mm) des DRV8213 zur Massefläche unten."""
    ep = next(p for p in driver.Pads() if p.GetNumber() == "9")
    c = ep.GetPosition()
    long_y = ep.GetBoundingBox().GetHeight() > ep.GetBoundingBox().GetWidth()
    for d in (-0.4, 0.4):
        add_via(board, gnd, c.x + (0 if long_y else mm(d)), c.y + (mm(d) if long_y else 0))


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
    """VSYS-Hauptbahn vorab (0,5 mm): Kathode der Schottky D2 -> C1 -> C2 (senkrecht an den linken
    Pads), Abzweig C1 -> C4 -> VM-Pin 1 des DRV8213. Der Rest von VSYS (Q1, LDO, Teiler) und BAT_IN/VBUS
    laufen über Freerouting in der Netzklasse Power."""
    def at(ref, num):
        q = pad_of(fps[ref], num).GetPosition()
        return q.x, q.y

    net = pad_of(fps["C1"], "1").GetNet()
    k, c1, c2, c4, vm = at("D2", "1"), at("C1", "1"), at("C2", "1"), at("C4", "1"), at("U2", "1")
    add_track(board, net, pcbnew.F_Cu, MAIN_TRACK, k, (c1[0], k[1] + mm(0.6)), c1, c2)
    add_track(board, net, pcbnew.F_Cu, MAIN_TRACK, c1, (c4[0] + mm(0.3), c4[1]), c4)
    add_track(board, net, pcbnew.F_Cu, STUB_TRACK, c4, (vm[0], vm[1] + mm(0.45)), vm)


def preroute_outputs(board, driver, contact_a, contact_b):
    """Ausgänge des DRV8213 vorab: OUT1 (Pin 2, OUT_A) und OUT2 (Pin 3, OUT_B) je mit 0,3-mm-Stich auf ein
    Via, unten mit 0,4 mm am Rand -y entlang: OUT_A nach links unter Modul und Antenne (Randstreifen) zum
    Endkontakt BT1, OUT_B nach rechts zum Endkontakt BT2. Erwartet Drehung 180° (Pins 1–4 zeigen nach +x)."""
    assert round(driver.GetOrientationDegrees()) % 360 == 180, "preroute_outputs erwartet Drehung 180°"
    pa, pb = pad_of(driver, "2").GetPosition(), pad_of(driver, "3").GetPosition()
    out_a, out_b = pad_of(driver, "2").GetNet(), pad_of(driver, "3").GetNet()
    edge_y = mm(ORIGIN[1] - EDGE_TRACK_Y)
    # OUT_A: Via rechts neben dem Pin, unten schräg unter dem Treiber hindurch zum Rand, dann nach links
    va = (pa.x + mm(1.15), pa.y)
    add_track(board, out_a, pcbnew.F_Cu, STUB_TRACK, (pa.x, pa.y), va)
    add_via(board, out_a, *va)
    ca = next(iter(contact_a.Pads())).GetPosition()
    add_track(board, out_a, pcbnew.B_Cu, POWER_TRACK, va, (va[0] - mm(0.75), edge_y), (ca.x + mm(0.8), edge_y),
              (ca.x, edge_y + mm(0.8)), (ca.x, ca.y))
    # OUT_B: Stich schräg nach rechts unten (am GND-Pin 4 vorbei), Via, unten am Rand nach rechts
    vb = (pb.x + mm(1.7), pb.y - mm(0.4))
    add_track(board, out_b, pcbnew.F_Cu, STUB_TRACK, (pb.x, pb.y), (pb.x + mm(0.6), pb.y),
              (pb.x + mm(1.0), vb[1]), vb)
    add_via(board, out_b, *vb)
    cb = next(iter(contact_b.Pads())).GetPosition()
    add_track(board, out_b, pcbnew.B_Cu, POWER_TRACK, vb, (vb[0], edge_y), (cb.x - mm(0.8), edge_y),
              (cb.x, edge_y + mm(0.8)), (cb.x, cb.y))


def rel(x, y):
    """Punkt relativ zur Platinenmitte (mm) als absolute Koordinate (nm)."""
    return mm(ORIGIN[0] + x), mm(ORIGIN[1] + y)


def preroute_vbus(board, fps):
    """VBUS (bis 2 A) vorab:
    - linkes VBUS-Padpaar (A4/B9): bandseitig oben mit 0,5 mm schräg zur Anode der Schottky D2
    - die beiden VBUS-Padpaare untereinander über die Körperseite: je ein Via hinter dem Pad (außerhalb der
      Bohrungen), unten verbunden. Das Band vor den Datenpads bleibt so unten frei für D-/D+ (ESD-Durchschleifung).
    - ESD U5 Pin 5 (VBUS) oben waagerecht zwischen den D+/D--Vias hindurch an die Schrägbahn"""
    usb = fps["J4"]
    net = pad_of(usb, "A4").GetNet()
    left, right = sorted((pad_of(usb, n) for n in ("A4", "B4")), key=lambda p: p.GetPosition().x)
    ql, qr = left.GetPosition(), right.GetPosition()
    half = left.GetBoundingBox().GetHeight() // 2
    band, body = ql.y - half, ql.y + half          # Padenden: Band (-y) und Körper (+y)
    # senkrecht nach -y bis unter die ESD, dann waagerecht in die Anode: oberhalb bleibt Platz für R14/R15
    an = pad_of(fps["D2"], "2").GetPosition()
    y_run = an.y - mm(0.25)
    add_track(board, net, pcbnew.F_Cu, MAIN_TRACK, (ql.x, band), (ql.x, y_run), (an.x, y_run))
    # Körperseite: Vias rechts unten neben den Pads (Bohrungen der Buchse bei x ±2,9 / y -0,2 freihalten)
    vl = (ql.x + mm(0.55), body + mm(0.82))
    vr = (qr.x - mm(0.55), body + mm(0.82))
    add_track(board, net, pcbnew.F_Cu, 0.3, (ql.x, body), vl)
    add_track(board, net, pcbnew.F_Cu, 0.3, (qr.x, body), vr)
    add_via(board, net, *vl)
    add_via(board, net, *vr)
    add_track(board, net, pcbnew.B_Cu, MAIN_TRACK, vl, vr)
    # ESD Pin 5 waagerecht an die senkrechte VBUS-Bahn
    p5 = pad_of(fps["U5"], "5").GetPosition()
    add_track(board, net, pcbnew.F_Cu, 0.3, (p5.x, p5.y), (ql.x, p5.y))
    # VBUS-Teiler R14 (oben im Band): VBUS-Pad rechts an die senkrechte Bahn
    r14 = pad_of(fps["R14"], "1").GetPosition()
    add_track(board, net, pcbnew.F_Cu, 0.25, (r14.x, r14.y), (ql.x, r14.y))


def preroute_vbus_branches(board, fps):
    """VBUS zum Gate von Q1 (Kante +y, ohne Laststrom, 0,25 mm) und VBUS_DET aus dem Band nach Norden:
    - VBUS: Via über der Anode der Schottky, unten nordwestlich (westlich am USB-Paar vorbei), Via zwischen
      C9 und Q1, oben ans Gate
    - VBUS_DET: R14–R15 direkt; den Weg zum Modul (Pad 9) routet Freerouting"""
    net = pad_of(fps["J4"], "A4").GetNet()
    an = pad_of(fps["D2"], "2")
    a = rel(9.3, -3.6)
    b = rel(5.5, 3.25)
    q = an.GetPosition()
    add_track(board, net, pcbnew.F_Cu, 0.25, (q.x, q.y), (a[0], q.y + mm(0.6)), a)
    add_via(board, net, *a)
    add_track(board, net, pcbnew.B_Cu, 0.25, a, rel(7.0, -1.3), rel(7.0, 2.5), rel(6.25, 3.25), b)
    add_via(board, net, *b)
    g = pad_of(fps["Q1"], "1").GetPosition()
    add_track(board, net, pcbnew.F_Cu, 0.25, b, (g.x, g.y))
    det = pad_of(fps["R14"], "2").GetNet()
    r14, r15 = pad_of(fps["R14"], "2").GetPosition(), pad_of(fps["R15"], "1").GetPosition()
    add_track(board, det, pcbnew.F_Cu, RULES["track"], (r14.x, r14.y), (r15.x, r15.y))


def preroute_right_end(board, fps):
    """Rechtes Ende: OUT_B von R4 per Via auf die OUT_B-Bahn unten, 3V3 von R4 nach C15."""
    r4o, r4v, c15 = pad_of(fps["R4"], "1"), pad_of(fps["R4"], "2"), pad_of(fps["C15"], "1")
    q = r4o.GetPosition()
    v = (q.x, q.y - mm(0.62))
    add_track(board, r4o.GetNet(), pcbnew.F_Cu, 0.25, (q.x, q.y), v)
    add_via(board, r4o.GetNet(), *v)
    a, b = r4v.GetPosition(), c15.GetPosition()
    add_track(board, r4v.GetNet(), pcbnew.F_Cu, SUPPLY_TRACK, (a.x, a.y), (b.x, b.y))


def preroute_vsys_r6(board, fps):
    """VSYS zum Teiler R6 (Pad rechts): von C4 zwischen R1/R8 und C4/R3 hindurch (Gasse x ≈ +1,1)."""
    c4, r6 = pad_of(fps["C4"], "1"), pad_of(fps["R6"], "1")
    q, r = c4.GetPosition(), r6.GetPosition()
    x = mm(ORIGIN[0] + 1.1)
    add_track(board, c4.GetNet(), pcbnew.F_Cu, RULES["track"], (q.x, q.y), (x, q.y + mm(0.38)), (x, r.y - mm(0.25)),
              (r.x, r.y))


def preroute_cc(board, fps):
    """CC1 (A5) über die Körperseite der Buchse zu R12 links neben J4 (das Band ist für D-/D+ belegt);
    CC2 (B5) bandseitig zu R13."""
    usb = fps["J4"]
    a5, b5 = pad_of(usb, "A5"), pad_of(usb, "B5")
    half = a5.GetBoundingBox().GetHeight() // 2
    q = a5.GetPosition()
    r12 = pad_of(fps["R12"], "1").GetPosition()
    y = mm(ORIGIN[1] + 0.62)
    add_track(board, a5.GetNet(), pcbnew.F_Cu, RULES["track"], (q.x, q.y + half), (q.x, y), (r12.x + mm(0.35), y),
              (r12.x, r12.y))
    q = b5.GetPosition()
    r13 = pad_of(fps["R13"], "1").GetPosition()
    add_track(board, b5.GetNet(), pcbnew.F_Cu, RULES["track"], (q.x, q.y - half), (q.x + mm(0.35), q.y - half - mm(0.4)),
              (r13.x, r13.y))


def preroute_bat_in(board, fps):
    """BAT_IN (bis 2 A) vorab: Akku-Pad J5.1 unten zum Kabel-Pad J1.1 und zwischen den Laschen von J4
    hindurch zu einem Via neben dem Drain von Q1."""
    net = pad_of(fps["J5"], "1").GetNet()
    j5, j1 = pad_of(fps["J5"], "1").GetPosition(), pad_of(fps["J1"], "1").GetPosition()
    d = pad_of(fps["Q1"], "3").GetPosition()
    add_track(board, net, pcbnew.B_Cu, MAIN_TRACK, (j5.x, j5.y), (j5.x - mm(0.8), j5.y + mm(1.75)),
              (j1.x + mm(0.4), j1.y - mm(0.7)), (j1.x, j1.y))
    left = pad_of(fps["J5"], "1").GetBoundingBox().GetLeft()
    y = mm(ORIGIN[1] + 1.6)
    v = (d.x + mm(1.05), mm(ORIGIN[1] + 2.2))
    add_track(board, net, pcbnew.B_Cu, MAIN_TRACK, (j5.x, j5.y), (left + mm(0.3), y), (v[0] + mm(0.6), y), v)
    add_via(board, net, *v)
    add_track(board, net, pcbnew.F_Cu, MAIN_TRACK, v, (v[0], d.y), (d.x, d.y))


def preroute_ties(board, fps):
    """Kurze Verbindungen, an denen Freerouting scheitert:
    - U4 (LIS2DH12): VDD Pin 9–10
    - U3 (AP2112K): VIN – EN um den GND-Pin herum
    - OUT_A zu den Erkennungswiderständen R3/R5: unten vom Ausgangs-Via nach oben, Via, dann R3.1 – R5.1
    """
    # LIS2DH12: 3V3 (2–9) und GND (3–8) unter dem Gehäuse verbunden; so gehen nur SCL, 3V3, SDA, INT nach außen
    for ref, a, b in (("U4", "9", "10"), ("U4", "2", "9"), ("U4", "3", "8")):
        pa, pb = pad_of(fps[ref], a), pad_of(fps[ref], b)
        add_track(board, pa.GetNet(), pcbnew.F_Cu, 0.2, (pa.GetPosition().x, pa.GetPosition().y),
                  (pb.GetPosition().x, pb.GetPosition().y))
    # LDO: VIN (1) und EN (3) liegen auf derselben Seite, dazwischen GND (2) -> links außen herum
    vin, en = pad_of(fps["U3"], "1"), pad_of(fps["U3"], "3")
    x = vin.GetBoundingBox().GetLeft() - mm(0.35)
    c8 = pad_of(fps["C8"], "1").GetPosition()
    add_track(board, vin.GetNet(), pcbnew.F_Cu, 0.3, (c8.x, c8.y), (c8.x, vin.GetPosition().y - mm(0.5)),
              (vin.GetPosition().x, vin.GetPosition().y))
    add_track(board, vin.GetNet(), pcbnew.F_Cu, 0.25, (vin.GetPosition().x, vin.GetPosition().y),
              (x, vin.GetPosition().y), (x, en.GetPosition().y), (en.GetPosition().x, en.GetPosition().y))
    out_a = pad_of(fps["U2"], "2")
    va = (out_a.GetPosition().x + mm(1.15), out_a.GetPosition().y)
    r3, r5 = pad_of(fps["R3"], "1").GetPosition(), pad_of(fps["R5"], "1").GetPosition()
    v = (r3.x + mm(0.27), r3.y - mm(0.85))
    add_track(board, out_a.GetNet(), pcbnew.B_Cu, STUB_TRACK, va, (v[0], va[1]), v)
    add_via(board, out_a.GetNet(), *v)
    add_track(board, out_a.GetNet(), pcbnew.F_Cu, 0.25, v, (r3.x, r3.y), (r5.x, r5.y))


def preroute_usb(board, fps):
    """USB D+/D- vorab, ESD U5 durchgeschleift (ST DS4260 Fig. 7 „optimized layout“, Fig. 18):
    J4 → U5 Buchsenseite (rechts, Pin 1 D+ / Pin 3 D-) → unter dem Gehäuse gerade hinüber → U5 Modulseite
    (links, Pin 6 / Pin 4) → Via → unten im Bereich der Buchse → Via → oben im Kanal zum Modul (Pads 18/17).
    Kein Abzweig/Stich.

    - D+ (A6–B6) über die bandseitigen Padenden verbunden, von B6 schräg auf Pin 1
    - D- (B7–A7) über die körperseitigen Padenden verbunden; von B7 Via, unten unter U5 hindurch zu Pin 3
    Erwartet U5 mit Drehung 180°.
    """
    usb, mod, esd = fps["J4"], fps["U1"], fps["U5"]
    assert round(esd.GetOrientationDegrees()) % 360 == 180, "preroute_usb erwartet U5 mit 180°"

    def p(fp, num):
        q = pad_of(fp, num).GetPosition()
        return q.x, q.y

    a6, b6, a7, b7 = p(usb, "A6"), p(usb, "B6"), p(usb, "A7"), p(usb, "B7")
    dp, dm = pad_of(usb, "A6").GetNet(), pad_of(usb, "A7").GetNet()
    half = pad_of(usb, "A6").GetBoundingBox().GetHeight() // 2
    y_band, y_body = a6[1] - half - mm(0.3), a6[1] + half + mm(0.3)
    w = 0.2
    e1, e3, e4, e6 = p(esd, "1"), p(esd, "3"), p(esd, "4"), p(esd, "6")
    # Paarverbindungen an J4
    add_track(board, dp, pcbnew.F_Cu, w, a6, (a6[0], y_band), (b6[0], y_band), b6)
    add_track(board, dm, pcbnew.F_Cu, w, b7, (b7[0], y_body), (a7[0], y_body), a7)
    # D+: B6 → Pin 1 → Pin 6 → Via
    vp = (e6[0] - mm(1.51), e6[1] - mm(0.15))
    add_track(board, dp, pcbnew.F_Cu, w, (b6[0], y_band), (e1[0] - mm(0.45), e1[1] + mm(0.45)), e1, e6, vp)
    add_via(board, dp, *vp)
    # D-: B7 → Via → unten → Via rechts neben Pin 3 → Pin 3 → Pin 4 → Via
    v1 = (b7[0] - mm(0.1), b7[1] - half - mm(0.93))
    v2 = (e3[0] + mm(1.06), e3[1] + mm(0.35))
    vm = (e4[0] - mm(1.56), e4[1] + mm(0.35))
    add_track(board, dm, pcbnew.F_Cu, w, b7, v1)
    add_via(board, dm, *v1)
    add_track(board, dm, pcbnew.B_Cu, w, v1, v2)
    add_via(board, dm, *v2)
    add_track(board, dm, pcbnew.F_Cu, w, v2, e3, e4, vm)
    add_via(board, dm, *vm)
    # unten: Paar schräg aus dem Band, waagerecht vor der Lötlasche S1 (Durchsteckpad) vorbei, links davon
    # senkrecht nach oben, dann waagerecht bis vor C10/R7 und per Via nach oben in den Kanal zwischen
    # C2/R5 und der Kondensatorreihe C8–C10 (y = +0,83 D+, +1,11 D-). Unten bleibt so nur der Bereich
    # an der Buchse belegt; die Platinenmitte bleibt unten frei für Nord-Süd-Verbindungen.
    m17, m18 = p(mod, "17"), p(mod, "18")
    tab = min((q for q in usb.Pads() if q.GetNumber() == "S1"), key=lambda q: (q.GetPosition().x, q.GetPosition().y))
    x_tab = tab.GetBoundingBox().GetLeft()
    yp1, ym1 = tab.GetBoundingBox().GetTop() - mm(0.47), tab.GetBoundingBox().GetTop() - mm(0.97)
    xp1, xm1 = x_tab - mm(0.33), x_tab - mm(0.83)
    yp, ym = mm(ORIGIN[1] - 0.6), mm(ORIGIN[1] - 1.05)
    up_p, up_m = rel(8.6, 0.4), rel(7.9, 1.4)      # Vias in den Kanal
    add_track(board, dp, pcbnew.B_Cu, w, vp, (vp[0] - (yp1 - vp[1]), yp1), (xp1, yp1), (xp1, yp), (up_p[0], yp), up_p)
    add_track(board, dm, pcbnew.B_Cu, w, vm, (vm[0] - (ym1 - vm[1]), ym1), (xm1, ym1), (xm1, ym), (up_m[0], ym), up_m)
    add_via(board, dp, *up_p)
    add_via(board, dm, *up_m)
    wk = 0.15  # im Kanal schmaler, damit eine dritte Bahn Platz hat
    cp, cm = mm(ORIGIN[1] + 0.83), mm(ORIGIN[1] + 1.11)
    xc = mm(ORIGIN[0] - 1.1)  # Ende des Kanals vor der 0402-Reihe
    add_track(board, dp, pcbnew.F_Cu, wk, up_p, (up_p[0] - (cp - up_p[1]), cp), (xc, cp),
              (xc - (cp - m18[1]), m18[1]), m18)
    add_track(board, dm, pcbnew.F_Cu, wk, up_m, (up_m[0] - (up_m[1] - cm), cm), (m17[0] + mm(0.6), cm),
              (m17[0] + mm(0.3), m17[1]), m17)


def copper_zones(board, gnd):
    """Kupferflächen: GND oben und unten über die ganze Platine.

    (Eine VSYS-Fläche unten wurde verworfen: Freerouting zerschneidet sie mit Signalen in Inseln.)
    """
    x0, x1 = ORIGIN[0] - BOARD_L / 2, ORIGIN[0] + BOARD_L / 2
    y0, y1 = ORIGIN[1] - BOARD_W / 2, ORIGIN[1] + BOARD_W / 2
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
        # voll angebunden: die kleinen GND-Pads (0402, USB-C, LGA) bekämen sonst nur eine Speiche
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
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
    edge_keepout(board)
    thermal_vias(board, footprints["U2"], netinfo["/GND"])
    preroute_outputs(board, footprints["U2"], footprints["BT1"], footprints["BT2"])
    preroute_supply(board, footprints)
    preroute_usb(board, footprints)
    preroute_vbus(board, footprints)
    preroute_cc(board, footprints)
    preroute_vbus_branches(board, footprints)
    preroute_vsys_r6(board, footprints)
    preroute_right_end(board, footprints)
    preroute_ties(board, footprints)
    preroute_bat_in(board, footprints)
    module_ground_vias(board, footprints["U1"])
    for ref, num, ep_num in EP_TIES:
        pin, ep = pad_of(footprints[ref], num), pad_of(footprints[ref], ep_num)
        q, e = pin.GetPosition(), ep.GetPosition()
        add_track(board, pin.GetNet(), pcbnew.F_Cu, 0.25, (q.x, q.y), (e.x, q.y))
    for ref, num, dx, dy in GROUND_VIAS:
        ground_via_at_pad(board, footprints[ref], num, dx, dy, width=0.3)
    copper_zones(board, netinfo["/GND"])
    pcbnew.SaveBoard(str(PCB), board)
    top = sum(1 for p in placement.values() if p[3] == "F")
    print(f"{PCB.relative_to(HARDWARE.parent)}: Variante '{variant}', {len(comps)} Bauteile "
          f"({top} oben, {len(comps) - top} unten), Antennen-Sperrfläche {keepout:.1f} mm")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "einseitig")
