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
PROJECT_FP_LIBS = {"lcsc": HARDWARE / "lib" / "lcsc.pretty"}

ORIGIN = (100.0, 75.0)  # Platinenmitte (wie board_outline.py)
BOARD_L, BOARD_W = 46.0, 13.5

# Designregeln: konservativ, damit praktisch jeder Hersteller sie im Standardpreis fertigt
RULES = dict(clearance=0.15, track=0.2, track_min=0.15, via_d=0.6, via_drill=0.3, edge=0.3)
POWER_NETS = ["VSYS", "GND", "MOT_A", "MOT_B", "ISEN"]
POWER_TRACK = 0.6
# Streifen am Rand (+y) im Antennenbereich, frei für die Leiterbahn zum Endkontakt MOT_A
ANTENNA_TRACK_STRIP = 1.2



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

    def rule_area(name, layers, footprints):
        zone = pcbnew.ZONE(board)
        zone.SetIsRuleArea(True)
        zone.SetZoneName(name)
        zone.SetLayerSet(layers)
        zone.SetDoNotAllowTracks(True)
        zone.SetDoNotAllowVias(True)
        zone.SetDoNotAllowCopperPour(True)
        zone.SetDoNotAllowPads(footprints)
        zone.SetDoNotAllowFootprints(footprints)
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            outline.Append(x, y)
        board.Add(zone)

    rule_area("Antenne", pcbnew.LSET.AllCuMask(), footprints=False)
    bottom = pcbnew.LSET()
    bottom.AddLayer(pcbnew.B_Cu)
    rule_area("Antenne unten", bottom, footprints=True)
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


def gnd_zones(board, gnd):
    """Masseflächen auf beiden Lagen über die ganze Platine (Antennenbereich ist gesperrt)."""
    x0, x1 = mm(ORIGIN[0] - BOARD_L / 2), mm(ORIGIN[0] + BOARD_L / 2)
    y0, y1 = mm(ORIGIN[1] - BOARD_W / 2), mm(ORIGIN[1] + BOARD_W / 2)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(gnd)
        zone.SetZoneName(f"GND {pcbnew.LayerName(layer)}")
        zone.SetLocalClearance(mm(0.2))
        zone.SetMinThickness(mm(0.2))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefGap(mm(0.2))
        zone.SetThermalReliefSpokeWidth(mm(0.3))
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            outline.Append(x, y)
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
        footprints[ref] = fp

    keepout = antenna_keepout(board, footprints["U1"])
    thermal_vias(board, footprints["U2"], netinfo["/GND"])
    gnd_zones(board, netinfo["/GND"])
    pcbnew.SaveBoard(str(PCB), board)
    top = sum(1 for p in placement.values() if p[3] == "F")
    print(f"{PCB.relative_to(HARDWARE.parent)}: Variante '{variant}', {len(comps)} Bauteile "
          f"({top} oben, {len(comps) - top} unten), Antennen-Sperrfläche {keepout:.1f} mm")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "einseitig")
