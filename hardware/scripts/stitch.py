"""Stitching vias: connect pads of zone nets (GND, VSYS) to their copper zone with a via.

For each affected pad, the nearest via position is searched in rings around the pad where the via and
its feed track do not come too close to other nets, which is not inside a keepout area and (on the
opposite layer) lies inside a zone of the same net.

4 layers: the opposite layer is always the continuous GND layer In1; vias are checked for clearance on
all four layers.
"""

import json
import math
import subprocess
import tempfile
from pathlib import Path

import pcbnew

VIA_D, VIA_DRILL, TRACK_W, CLEARANCE = 0.6, 0.3, 0.25, 0.2
EDGE_MARGIN = 0.6


def mm(v):
    return pcbnew.FromMM(v)


def cu_layers(board):
    """Copper layers of the board (2: F/B, 4: F/In1/In2/B)."""
    if board.GetCopperLayerCount() >= 4:
        return [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
    return [pcbnew.F_Cu, pcbnew.B_Cu]


def plane_layer(board, layer):
    """Layer on which a via from `layer` should reach the zone: the GND layer In1 on 4 layers,
    otherwise the opposite layer."""
    if board.GetCopperLayerCount() >= 4:
        return pcbnew.In1_Cu
    return pcbnew.B_Cu if layer == pcbnew.F_Cu else pcbnew.F_Cu


class Copper:
    """Pads and tracks of a board for clearance checks; placed vias and tracks are added to it."""

    def __init__(self, board):
        self.board = board
        self.items = [p for p in board.GetPads()] + list(board.GetTracks())
        self.layers = cu_layers(board)

    def collides(self, item, layer, net):
        """Does item (via/track) on layer come too close to copper of another net (or to any via)?"""
        shape = item.GetEffectiveShape(layer)
        return any(self._conflict(other, shape, layer, net) for other in self.items)

    @staticmethod
    def _conflict(other, shape, layer, net):
        same_net = other.GetNetCode() == net.GetNetCode() and net.GetNetCode() != 0
        if same_net and other.GetClass() != "PCB_VIA":  # always check vias (hole clearance)
            return False
        return other.IsOnLayer(layer) and other.GetEffectiveShape(layer).Collide(shape, mm(CLEARANCE))

    def via_fits(self, via, net):
        return not any(self.collides(via, layer, net) for layer in self.layers)

    def place(self, *new_items):
        for item in new_items:
            item.SetLocked(True)
            self.board.Add(item)
            self.items.append(item)


def new_via(board, pos, net):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pos)
    via.SetWidth(mm(VIA_D))
    via.SetDrill(mm(VIA_DRILL))
    via.SetNet(net)
    return via


def new_track(board, ends, layer, net):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(ends[0])
    track.SetEnd(ends[1])
    track.SetLayer(layer)
    track.SetWidth(mm(TRACK_W))
    track.SetNet(net)
    return track


HOLE_CLEARANCE = 0.3  # hole clearance (DRC 0.25 mm) with margin


def _near_hole(board, pos):
    """Is the via too close to a drill hole (including NPTH without copper, e.g. pegs of the USB connector)?"""
    for pad in board.GetPads():
        drill = pad.GetDrillSize()
        if drill.x <= 0:
            continue
        c = pad.GetPosition()
        r = max(drill.x, drill.y) / 2 + mm(VIA_D / 2 + HOLE_CLEARANCE)
        if (c.x - pos.x) ** 2 + (c.y - pos.y) ** 2 < r**2:
            return True
    return False


def _inside_board(board, pos):
    box = board.GetBoardEdgesBoundingBox()
    m = mm(EDGE_MARGIN)
    inside_x = box.GetLeft() + m < pos.x < box.GetRight() - m
    return inside_x and box.GetTop() + m < pos.y < box.GetBottom() - m


def _in_rule_area(board, pos):
    """Does the via (with radius and clearance) lie fully or partly inside a via keepout area?"""
    r = mm(VIA_D / 2)
    probes = [pos] + [pcbnew.VECTOR2I(pos.x + dx, pos.y + dy) for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r))]
    keepouts = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
    return any(z.Outline().Contains(q) for z in keepouts for q in probes)


def via_allowed(board, pos):
    """Inside the board, outside via keepouts and away from drill holes."""
    return _inside_board(board, pos) and not _in_rule_area(board, pos) and not _near_hole(board, pos)


def _in_zone(board, pos, layer, net):
    """Does pos (with via radius) lie inside the filled zone of the net on this layer?"""
    zones = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == net.GetNetCode()]
    return in_filled(zones, pos, layer)


def in_filled(zones, pos, layer, margin=VIA_D / 2):
    """Does pos (with margin in mm) lie in the filled area of one of the zones on this layer?"""
    return any(z.IsOnLayer(layer) and z.HitTestFilledArea(layer, pos, mm(margin)) for z in zones)


def ring_positions(centre, r0):
    """Candidate via positions in rings around centre: 10 rings from r0 (mm) in 0.2 mm steps, 24 per ring."""
    for step in range(10):
        r = r0 + 0.2 * step
        for k in range(24):
            a = 2 * math.pi * k / 24
            yield pcbnew.VECTOR2I(int(centre.x + mm(r * math.cos(a))), int(centre.y + mm(r * math.sin(a))))


def stitch_pad(copper, pad):
    """Place a via with feed track next to the pad. Return True if a position was found."""
    board, net = copper.board, pad.GetNet()
    pad_layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    other = plane_layer(board, pad_layer)
    c = pad.GetPosition()
    r0 = max(pad.GetSize().x, pad.GetSize().y) / 2 / 1e6 + VIA_D / 2 + 0.25
    for pos in ring_positions(c, r0):
        if not via_allowed(board, pos) or not _in_zone(board, pos, other, net):
            continue
        via, track = new_via(board, pos, net), new_track(board, (c, pos), pad_layer, net)
        if copper.via_fits(via, net) and not copper.collides(track, pad_layer, net):
            copper.place(via, track)
            return True
    return False


def unconnected_pads(board_file, nets):
    """Pads of the given nets that DRC reports as unconnected: list of (reference, pad number)."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "drc.json"
        subprocess.run(
            ["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(board_file)], capture_output=True
        )
        data = json.loads(report.read_text())
    descriptions = [
        item.get("description", "") for v in data.get("unconnected_items", []) for item in v.get("items", [])
    ]
    return sorted({pad for pad in map(pad_from_description, descriptions) if pad and pad[2] in nets})


def pad_from_description(desc):
    """(reference, pad number, net) from e.g. "Pad 2 [/GND] of C10 on F.Cu" (German KiCad: "von … auf"), or None."""
    parts = desc.split()
    if parts[:1] != ["Pad"] or len(parts) < 5:
        return None
    return parts[4], parts[1], parts[2].strip("[]")


def stitch_targets(board, board_file, nets, all_pads):
    """(reference, pad number) to stitch: every top-only pad of the nets, or the ones DRC reports unconnected."""
    if all_pads:
        return [
            (p.GetParentFootprint().GetReference(), p.GetNumber())
            for p in board.GetPads()
            if p.GetNetname() in nets and is_top_only(p)
        ]
    pcbnew.SaveBoard(str(board_file), board)
    return [(ref, num) for ref, num, _net in unconnected_pads(board_file, nets)]


def is_top_only(pad):
    return pad.IsOnLayer(pcbnew.F_Cu) and not pad.IsOnLayer(pcbnew.B_Cu)


def stitch(board_file, nets, all_pads=False):
    """Stitching for the nets; all_pads=True: every pad of these nets (before routing)."""
    board = pcbnew.LoadBoard(str(board_file))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    targets = list(dict.fromkeys(stitch_targets(board, board_file, nets, all_pads)))  # unique, order kept
    copper = Copper(board)
    done, failed = 0, []
    for ref, num in targets:
        pad = next(p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber() == num)
        if not (pad.IsOnLayer(pcbnew.F_Cu) or pad.IsOnLayer(pcbnew.B_Cu)):
            continue
        if stitch_pad(copper, pad):
            done += 1
        else:
            failed.append(f"{ref}.{num}")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(board_file), board)
    return done, failed


def grid_positions(box, pitch, margins=(1.0, 0.9)):
    """Positions on a pitch grid (mm) inside box, rows first; margins: (start, end) in mm."""
    start, end = margins
    y = box.GetTop() + mm(start)
    while y < box.GetBottom() - mm(end):
        x = box.GetLeft() + mm(start)
        while x < box.GetRight() - mm(end):
            yield pcbnew.VECTOR2I(int(x), int(y))
            x += mm(pitch)
        y += mm(pitch)


def stitch_grid(board_file, net_name="/GND", pitch=1.6):
    """Grid via stitching: place a via wherever filled zone of the net lies on top and bottom and a via
    fits with clearance. Connects zone islands to the opposite layer."""
    board = pcbnew.LoadBoard(str(board_file))
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    net = board.FindNet(net_name)
    zones = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == net.GetNetCode()]
    copper = Copper(board)
    added = grid_vias(copper, zones, net, pitch)
    filler.Fill(board.Zones())
    added += IslandStitcher(copper, zones, net).run()
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(str(board_file), board)
    return added


def grid_vias(copper, zones, net, pitch):
    """Vias on the grid wherever the net's zones are filled on top, bottom (and In1); returns the count."""
    board = copper.board
    need = (pcbnew.F_Cu, pcbnew.B_Cu) + ((pcbnew.In1_Cu,) if len(copper.layers) == 4 else ())
    added = 0
    for pos in grid_positions(board.GetBoardEdgesBoundingBox(), pitch):
        on_all = all(in_filled(zones, pos, layer, VIA_D / 2 + 0.05) for layer in need)
        if on_all and via_allowed(board, pos):
            added += 1 if try_via(copper, pos, net) else 0
    return added


def try_via(copper, pos, net):
    """Place a via at pos if it fits; returns it (truthy) or None."""
    via = new_via(copper.board, pos, net)
    if not copper.via_fits(via, net):
        return None
    copper.place(via)
    return via


class IslandStitcher:
    """For each zone island without its own via: fine search for a via spot with zone on the opposite layer,
    otherwise a via with stub track next to a pad of the island."""

    def __init__(self, copper, zones, net):
        self.copper, self.zones, self.net = copper, zones, net
        self.board = copper.board
        self.vias = [
            t for t in self.board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == net.GetNetCode()
        ]

    def run(self):
        added = 0
        for zone in self.zones:
            for layer in self.island_layers(zone):
                polys = zone.GetFilledPolysList(layer)
                outlines = [polys.Outline(i) for i in range(polys.OutlineCount())]
                added += sum(self.stitch_island(zone, layer, o) for o in outlines if not self.has_via(o))
        return added

    def island_layers(self, zone):
        """Layers of the zone whose islands need a via (not the continuous plane In1 on 4 layers)."""
        plane = pcbnew.In1_Cu if len(self.copper.layers) == 4 else None
        return [layer for layer in self.copper.layers if zone.IsOnLayer(layer) and layer != plane]

    def has_via(self, outline):
        return any(outline.PointInside(v.GetPosition()) for v in self.vias)

    def stitch_island(self, zone, layer, outline):
        """1 if a via was placed for the island, else 0."""
        island_pads = [
            p for p in self.board.GetPads() if self.is_island_pad(p, layer) and outline.PointInside(p.GetPosition())
        ]
        via = self.search(zone, layer, outline)
        if via:
            self.vias.append(via)
            return 1
        for pad in island_pads:  # fallback: via with stub track right next to a pad of the island
            if stitch_pad(self.copper, pad):
                self.vias.append(self.copper.items[-2])
                return 1
        return 0

    def is_island_pad(self, pad, layer):
        return pad.GetNetCode() == self.net.GetNetCode() and pad.IsOnLayer(layer)

    def search(self, zone, layer, outline):
        """First fitting via on a 0.25 mm grid over the island's bounding box, or None."""
        box = outline.BBox()
        other = plane_layer(self.board, layer)
        for pos in grid_positions(box, 0.25, margins=(0, 0)):
            if self.spot_ok((zone, layer, outline), pos, other):
                via = try_via(self.copper, pos, self.net)
                if via:
                    return via
        return None

    def spot_ok(self, island, pos, other):
        zone, layer, outline = island
        inside = outline.PointInside(pos) and via_allowed(self.board, pos)
        return inside and zone.HitTestFilledArea(layer, pos, mm(VIA_D / 2)) and in_filled(self.zones, pos, other)
