"""Board helpers shared by the board generators (gen_main_pcb.py, gen_charger_pcb.py, preroute_main.py).

Coordinates are absolute nanometres unless a function says mm. Must run with KiCad's Python (pcbnew).
"""

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pcbnew
from sexpr import block_end

HARDWARE = Path(__file__).resolve().parent.parent
KICAD_FOOTPRINTS = Path("/usr/share/kicad/footprints")
PROJECT_FP_LIBS = {"lcsc": HARDWARE / "lib" / "lcsc.pretty", "louie": HARDWARE / "lib" / "louie.pretty"}

# Design rules (docs/main-board-c6.md 11.2): JLC multilayer 0.09/0.09 mm, via 0.15/0.25 mm, inner via–copper
# 0.2 mm, PTH–copper inner 0.3 mm, edge 0.2 mm. Generous here: 0.15/0.15 mm (+67 %), default track 0.2 mm,
# via 0.3/0.5 mm (no surcharge, annular ring 0.1 mm = 2 × JLC minimum, no via-in-pad; 0.6 mm diameter left
# considerably more open in trial routing). Hole–copper: vias 0.25 mm (JLC 0.2 mm), component holes 0.28 mm outer
# (JLC PTH–track 0.28) and 0.3 mm inner (JLC) via louie-main.kicad_dru (DRU).
RULES = dict(
    clearance=0.15,
    track=0.2,
    track_min=0.15,
    via_d=0.5,
    via_drill=0.3,
    edge=0.3,
    hole_clearance=0.25,
    hole_to_hole=0.25,
    annular=0.1,
)


def mm(v):
    return pcbnew.FromMM(v)


def read_netlist(sch):
    """Components {ref: {value, footprint, uuid, dnp, no_bom}} and nets {name: [(ref, pin)]} of a schematic."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "net.net"
        subprocess.run(
            ["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(out), str(sch)],
            check=True,
            capture_output=True,
        )
        text = out.read_text()
    comps = {}
    for m in re.finditer(r"\(comp \(ref \"([^\"]+)\"\)", text):
        block = text[m.start() : block_end(text, m.start())]
        comps[m.group(1)] = dict(
            value=re.search(r'\(value "([^"]*)"\)', block).group(1),
            footprint=re.search(r'\(footprint "([^"]*)"\)', block).group(1),
            uuid=re.findall(r'\(tstamps "([^"]*)"\)', block)[-1],
            dnp='(property (name "dnp"))' in block,
            no_bom='(property (name "exclude_from_bom"))' in block,
        )
    nets = {}
    for m in re.finditer(r"\(net \(code \"\d+\"\) \(name \"([^\"]*)\"\)", text):
        block = text[m.start() : block_end(text, m.start())]
        nets[m.group(1)] = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', block)
    return comps, nets


def drc_json(pcb):
    """kicad-cli DRC report of a board as parsed JSON (default severities)."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "drc.json"
        subprocess.run(
            ["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(pcb)], capture_output=True
        )
        return json.loads(report.read_text())


def set_minimum_rules(ds, rules=RULES):
    """Minimum track width, clearance, via size/drill and edge clearance (the charger board passes its own)."""
    ds.m_TrackMinWidth = mm(rules["track_min"])
    ds.m_MinClearance = mm(rules["clearance"])
    ds.m_ViasMinSize = mm(rules["via_d"])
    ds.m_MinThroughDrill = mm(rules["via_drill"])
    ds.m_CopperEdgeClearance = mm(rules["edge"])


def load_footprint(lib_id):
    nick, name = lib_id.split(":")
    lib = PROJECT_FP_LIBS.get(nick, KICAD_FOOTPRINTS / f"{nick}.pretty")
    fp = pcbnew.FootprintLoad(str(lib), name)
    if fp is None:
        raise RuntimeError(f"Footprint {lib_id} not found")
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    return fp


def clear_board(board):
    for fp in list(board.GetFootprints()):
        board.Delete(fp)
    for t in list(board.GetTracks()):
        board.Delete(t)
    for z in list(board.Zones()):
        board.Delete(z)


class Placer:
    """Adds the nets of a netlist to a board and places footprints with their pad nets and schematic link."""

    def __init__(self, board, nets, pos):
        self.board, self.pos = board, pos  # pos(x_mm, y_mm) -> VECTOR2I relative to the board centre
        self.netinfo = {}
        for name in nets:
            self.netinfo[name] = pcbnew.NETINFO_ITEM(board, name)
            board.Add(self.netinfo[name])
        self.pad_net = {(ref, pin): net for net, nodes in nets.items() for ref, pin in nodes}

    def place(self, ref, comp, where):
        """Footprint for comp at where = (x mm, y mm, rotation, side "F"/"B"); designator on the Fab layer only."""
        fp = load_footprint(comp["footprint"])
        self.board.Add(fp)
        fp.SetReference(ref)
        fp.SetValue(comp["value"])
        fp.SetPath(pcbnew.KIID_PATH(f"/{comp['uuid']}"))
        for pad in fp.Pads():
            net = self.pad_net.get((ref, pad.GetNumber()))
            if net:
                pad.SetNet(self.netinfo[net])
        x, y, rot, side = where
        fp.SetPosition(self.pos(x, y))
        fp.SetOrientationDegrees(rot)
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.5), mm(0.5)))
        fp.Reference().SetTextThickness(mm(0.08))
        fp.Reference().SetPosition(fp.GetPosition())
        fp.Value().SetVisible(False)
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            fp.Reference().SetLayer(pcbnew.B_Fab)
        return fp


def add_track(board, net, layer_width, *points):
    """Locked track through the points; layer_width = (layer, width in mm)."""
    layer, width = layer_width
    for a, b in zip(points, points[1:], strict=False):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(*a))
        track.SetEnd(pcbnew.VECTOR2I(*b))
        track.SetLayer(layer)
        track.SetWidth(mm(width))
        track.SetNet(net)
        track.SetLocked(True)
        board.Add(track)


def add_via(board, net, x, y):
    """Locked via with the board's via size and drill (set by set_minimum_rules before)."""
    ds = board.GetDesignSettings()
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(x, y))
    via.SetWidth(ds.m_ViasMinSize)
    via.SetDrill(ds.m_MinThroughDrill)
    via.SetNet(net)
    via.SetLocked(True)
    board.Add(via)


def pad_of(footprint, number):
    return next(p for p in footprint.Pads() if p.GetNumber() == number)


def ground_via_at_pad(board, pad, offset, width=0.4):
    """Fixed GND via next to a pad (offset (dx, dy) in mm from the pad centre) with a stub track."""
    q = pad.GetPosition()
    v = (q.x + mm(offset[0]), q.y + mm(offset[1]))
    add_track(board, pad.GetNet(), (pcbnew.F_Cu, width), (q.x, q.y), v)
    add_via(board, pad.GetNet(), *v)


def rect_outline(zone, rect):
    """Rectangle (x0, y0, x1, y1) in nm as the zone outline."""
    xa, ya, xb, yb = rect
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in [(xa, ya), (xb, ya), (xb, yb), (xa, yb)]:
        outline.Append(x, y)


@dataclass(frozen=True)
class Keepout:
    """Rule area: name, layer set and what it forbids (vias and copper pour are always forbidden unless allowed)."""

    name: str
    layers: object  # pcbnew.LSET
    tracks: bool = True
    vias: bool = True
    pour: bool = True
    footprints: bool = False


def rule_area(board, keepout, rect):
    zone = pcbnew.ZONE(board)
    zone.SetIsRuleArea(True)
    zone.SetZoneName(keepout.name)
    zone.SetLayerSet(keepout.layers)
    zone.SetDoNotAllowTracks(keepout.tracks)
    zone.SetDoNotAllowVias(keepout.vias)
    zone.SetDoNotAllowCopperPour(keepout.pour)
    zone.SetDoNotAllowPads(keepout.footprints)
    zone.SetDoNotAllowFootprints(keepout.footprints)
    rect_outline(zone, rect)
    board.Add(zone)


def layer_set(*layers):
    result = pcbnew.LSET()
    for layer in layers:
        result.AddLayer(layer)
    return result
