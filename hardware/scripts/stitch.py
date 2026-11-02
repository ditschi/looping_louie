"""Stitching-Vias: verbindet Pads von Flächennetzen (GND, VSYS) per Via mit ihrer Kupferfläche.

Für jedes betroffene Pad wird ringförmig um das Pad die nächstgelegene Via-Position gesucht, an
der Via und Zuleitung keinen anderen Netzen zu nahe kommen, die nicht in einer Sperrfläche liegt
und (auf der Gegenlage) innerhalb einer Fläche desselben Netzes.
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


def _copper_items(board):
    items = [p for p in board.GetPads()] + list(board.GetTracks())
    return items


def _collides(board, items, shape, layer, net):
    for item in items:
        same_net = item.GetNetCode() == net.GetNetCode() and net.GetNetCode() != 0
        if same_net and item.GetClass() != "PCB_VIA":  # Vias immer prüfen (Bohrabstand)
            continue
        if not item.IsOnLayer(layer):
            continue
        if item.GetEffectiveShape(layer).Collide(shape, mm(CLEARANCE)):
            return True
    return False


HOLE_CLEARANCE = 0.3  # Lochabstand (DRC 0,25 mm) mit Reserve


def _near_hole(board, pos):
    """Liegt das Via zu nah an einer Bohrung (auch NPTH ohne Kupfer, z. B. Stifte der USB-Buchse)?"""
    for pad in board.GetPads():
        drill = pad.GetDrillSize()
        if drill.x <= 0:
            continue
        c = pad.GetPosition()
        r = max(drill.x, drill.y) / 2 + mm(VIA_D / 2 + HOLE_CLEARANCE)
        if (c.x - pos.x) ** 2 + (c.y - pos.y) ** 2 < r ** 2:
            return True
    return False


def _inside_board(board, pos):
    box = board.GetBoardEdgesBoundingBox()
    m = mm(EDGE_MARGIN)
    return box.GetLeft() + m < pos.x < box.GetRight() - m and box.GetTop() + m < pos.y < box.GetBottom() - m


def _in_rule_area(board, pos):
    """Liegt das Via (mit Radius und Abstand) ganz oder teilweise in einer Sperrfläche für Vias?"""
    r = mm(VIA_D / 2)
    probes = [pos] + [pcbnew.VECTOR2I(pos.x + dx, pos.y + dy) for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r))]
    return any(z.GetIsRuleArea() and z.GetDoNotAllowVias() and z.Outline().Contains(q)
               for z in board.Zones() for q in probes)


def _in_zone(board, pos, layer, net):
    """Liegt pos (mit Via-Radius) in der gefüllten Fläche des Netzes auf dieser Lage?"""
    return any(not z.GetIsRuleArea() and z.GetNetCode() == net.GetNetCode() and z.IsOnLayer(layer)
               and z.HitTestFilledArea(layer, pos, mm(VIA_D / 2)) for z in board.Zones())


def stitch_pad(board, pad, items):
    """Setzt ein Via mit Zuleitung neben das Pad. Gibt True zurück, wenn eine Position gefunden wurde."""
    net = pad.GetNet()
    pad_layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    other = pcbnew.B_Cu if pad_layer == pcbnew.F_Cu else pcbnew.F_Cu
    c = pad.GetPosition()
    r0 = max(pad.GetSize().x, pad.GetSize().y) / 2 / 1e6 + VIA_D / 2 + 0.25
    for step in range(10):
        r = r0 + 0.2 * step
        for k in range(24):
            a = 2 * math.pi * k / 24
            pos = pcbnew.VECTOR2I(int(c.x + mm(r * math.cos(a))), int(c.y + mm(r * math.sin(a))))
            if not _inside_board(board, pos) or _in_rule_area(board, pos) or _near_hole(board, pos):
                continue
            if not _in_zone(board, pos, other, net):
                continue
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pos)
            via.SetWidth(mm(VIA_D))
            via.SetDrill(mm(VIA_DRILL))
            via.SetNet(net)
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(c)
            track.SetEnd(pos)
            track.SetLayer(pad_layer)
            track.SetWidth(mm(TRACK_W))
            track.SetNet(net)
            if any(_collides(board, items, via.GetEffectiveShape(L), L, net) for L in (pcbnew.F_Cu, pcbnew.B_Cu)):
                continue
            if _collides(board, items, track.GetEffectiveShape(pad_layer), pad_layer, net):
                continue
            for item in (via, track):
                item.SetLocked(True)
                board.Add(item)
                items.append(item)
            return True
    return False


def unconnected_pads(board_file, nets):
    """Pads der angegebenen Netze, die laut DRC nicht verbunden sind: Liste (Referenz, Padnummer)."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(board_file)],
                       capture_output=True)
        data = json.loads(report.read_text())
    result = set()
    for v in data.get("unconnected_items", []):
        for item in v.get("items", []):
            desc = item.get("description", "")
            # z. B. "Pad 2 [/GND] von C10 auf F.Cu" bzw. englisch "Pad 2 [/GND] of C10 on F.Cu"
            parts = desc.split()
            if parts[:1] == ["Pad"] and len(parts) >= 5 and parts[2].strip("[]") in nets:
                result.add((parts[4], parts[1]))
    return sorted(result)


def stitch(board_file, nets, all_pads=False):
    """Stitching für die Netze; all_pads=True: jedes Pad dieser Netze (vor dem Routing)."""
    board = pcbnew.LoadBoard(str(board_file))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if all_pads:
        targets = [(p.GetParentFootprint().GetReference(), p.GetNumber()) for p in board.GetPads()
                   if p.GetNetname() in nets and p.IsOnLayer(pcbnew.F_Cu) and not p.IsOnLayer(pcbnew.B_Cu)]
    else:
        pcbnew.SaveBoard(str(board_file), board)
        targets = unconnected_pads(board_file, nets)
    items = _copper_items(board)
    done, failed = 0, []
    seen = set()
    for ref, num in targets:
        if (ref, num) in seen:
            continue
        seen.add((ref, num))
        pad = next(p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber() == num)
        if not pad.IsOnLayer(pcbnew.F_Cu) and not pad.IsOnLayer(pcbnew.B_Cu):
            continue
        if stitch_pad(board, pad, items):
            done += 1
        else:
            failed.append(f"{ref}.{num}")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(board_file), board)
    return done, failed


def stitch_grid(board_file, net_name="/GND", pitch=1.6):
    """Via-Stitching im Raster: überall, wo oben und unten gefüllte Fläche des Netzes liegt und ein
    Via mit Abstand passt, ein Via setzen. Verbindet Flächeninseln mit der Gegenlage."""
    board = pcbnew.LoadBoard(str(board_file))
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    net = board.FindNet(net_name)
    zones = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == net.GetNetCode()]
    items = _copper_items(board)
    box = board.GetBoardEdgesBoundingBox()
    added = 0
    y = box.GetTop() + mm(1.0)
    while y < box.GetBottom() - mm(0.9):
        x = box.GetLeft() + mm(1.0)
        while x < box.GetRight() - mm(0.9):
            pos = pcbnew.VECTOR2I(int(x), int(y))
            on_both = all(any(z.IsOnLayer(L) and z.HitTestFilledArea(L, pos, mm(VIA_D / 2 + 0.05)) for z in zones)
                          for L in (pcbnew.F_Cu, pcbnew.B_Cu))
            if on_both and _inside_board(board, pos) and not _in_rule_area(board, pos) and not _near_hole(board, pos):
                via = pcbnew.PCB_VIA(board)
                via.SetPosition(pos)
                via.SetWidth(mm(VIA_D))
                via.SetDrill(mm(VIA_DRILL))
                via.SetNet(net)
                if not any(_collides(board, items, via.GetEffectiveShape(L), L, net) for L in (pcbnew.F_Cu, pcbnew.B_Cu)):
                    via.SetLocked(True)
                    board.Add(via)
                    items.append(via)
                    added += 1
            x += mm(pitch)
        y += mm(pitch)
    filler.Fill(board.Zones())
    added += _stitch_islands(board, zones, net, items)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(str(board_file), board)
    return added


def _stitch_islands(board, zones, net, items):
    """Je Flächeninsel ohne eigenes Via: feine Suche nach einer Via-Stelle mit Fläche auf der Gegenlage."""
    vias = [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == net.GetNetCode()]
    added = 0
    for zone in zones:
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            if not zone.IsOnLayer(layer):
                continue
            other = pcbnew.B_Cu if layer == pcbnew.F_Cu else pcbnew.F_Cu
            polys = zone.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                outline = polys.Outline(i)
                if any(outline.PointInside(v.GetPosition()) for v in vias):
                    continue
                box = outline.BBox()
                placed = False
                island_pads = [p for p in board.GetPads() if p.GetNetCode() == net.GetNetCode()
                               and p.IsOnLayer(layer) and outline.PointInside(p.GetPosition())]
                y = box.GetTop()
                while y < box.GetBottom() and not placed:
                    x = box.GetLeft()
                    while x < box.GetRight() and not placed:
                        pos = pcbnew.VECTOR2I(int(x), int(y))
                        if (outline.PointInside(pos) and _inside_board(board, pos) and not _in_rule_area(board, pos)
                                and not _near_hole(board, pos)
                                and zone.HitTestFilledArea(layer, pos, mm(VIA_D / 2))
                                and any(z.IsOnLayer(other) and z.HitTestFilledArea(other, pos, mm(VIA_D / 2))
                                        for z in zones)):
                            via = pcbnew.PCB_VIA(board)
                            via.SetPosition(pos)
                            via.SetWidth(mm(VIA_D))
                            via.SetDrill(mm(VIA_DRILL))
                            via.SetNet(net)
                            if not any(_collides(board, items, via.GetEffectiveShape(L), L, net)
                                       for L in (pcbnew.F_Cu, pcbnew.B_Cu)):
                                via.SetLocked(True)
                                board.Add(via)
                                items.append(via)
                                vias.append(via)
                                added += 1
                                placed = True
                        x += mm(0.25)
                    y += mm(0.25)
                for pad in island_pads:  # Ausweg: Via mit Stichleitung direkt neben einem Pad der Insel
                    if placed:
                        break
                    if stitch_pad(board, pad, items):
                        vias.append(items[-2])
                        added += 1
                        placed = True
    return added
