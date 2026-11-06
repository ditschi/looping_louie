# Charger board

Status: 2026-11-06 · Schematic and layout generated (ERC/DRC without errors), not yet ordered

The charger board sits between USB-C, battery and main board: it charges the 1S LiPo and powers
the game directly while charging. It has the format of the main board so that it **fits into an AA compartment**. Alternatively
it is **glued into the base of the game**.

> **Note (main board with ESP32-C6 and its own USB-C socket J4):** Flashing is done
> **only via J4 on the main board** (decision of the project owner). J1 of the main board carries only
> **BAT_IN (pad 1) and GND (pad 4)**; pads 2/3 have no net. **D+/D− of the charger board are no longer
> needed**; its USB socket is for charging only. 2 wires are enough between J103 and J1 (J103-1 → J1-1,
> J103-4 → J1-4); J103-2/3 stay free. In a v0.2 of the charger board, U102 can be reduced to VBUS protection
> and the D+/D− traces can be dropped. The following sections describe state v0.1 (with data lines).

![Wiring](bilder/verdrahtung.png)

## 1. Mounting options

| | A: in the AA compartment (standard for 2× AA) | B: in the base |
|---|---|---|
| Where | compartment 2, **instead of the bridge board** | on the inner wall of the base, hole in the wall |
| Orientation | **upright** in the 3D-printed AA insert | flat in the base holder |
| USB-C | points **upward** out of the compartment (plug across the cell axis) | points outward through the wall |
| Bridge in the compartment | taken over by the charger board (BT101 ↔ BT102) | bridge board B required (2× AA only) |
| Battery | JST-PH or solder pads | **solder pads only** (the JST faces the wall) |
| For | new Louie, Chewie | old Louie (1× C); also 2× AA if the compartment should stay closed |

In both cases the battery lies in the base. With mounting A you have to remove the compartment lid to charge,
or cut a slot for the plug (about 13 × 7 mm) into the lid.

### Why upright and a horizontal socket

- The compartment contacts are at the ends of the AA form; no socket can go there.
- A **horizontal** USB-C socket on the long edge points upward when the board stands upright, i.e.
  across the cell axis ("90°"). If the same board lies flat in the base, the socket points sideways
  through the wall. **So one board fits both mounting options.**
- Upright (vertical) USB-C sockets are 6–11 mm high and do not fit into the AA form when lying flat;
  in the base they would point upward.
- Geometry in the compartment (Ø 14.5 mm): board 12.5 mm wide, back side 3.2 mm behind the cell axis. The
  corners lie at r = 7.0 mm; the center of the socket (3.26 mm high) lies almost exactly on the axis. The
  plug therefore enters centered from above. On the component side there is up to 8 mm of space.
- 1.6 mm board thickness: the socket is loaded when plugging in; the THT tabs hold best in 1.6 mm.
  The AA form allows this because the board does not lie flat.

## 2. Circuit

Schematic: [`hardware/charger-board/louie-charger.kicad_sch`](../hardware/charger-board/louie-charger.kicad_sch)
(generated with `just charger-schematic`), image: [bilder/lade-schaltplan.png](bilder/lade-schaltplan.png).
Components: [`hardware/bom/teile.csv`](../hardware/bom/teile.csv), rows `lade`.

| Block | Components | Design |
|---|---|---|
| USB-C | J101 HRO TYPE-C-31-M-12, R101/R102 5.1 k | 16-pin socket, CC resistors = sink: every USB-C power supply switches on 5 V (also C-to-C cables). |
| ESD | U102 USBLC6-2SC6 | D+, D− and VBUS against discharges when plugging in. |
| Charge controller | U101 MCP73831-2 (4.20 V), R103 2 k | charge current 1000 V / R103 = **500 mA** (2 h for 1000 mAh). For small batteries 3.3 k = 300 mA. Thermal regulation in the IC, slows down by itself when hot. |
| Charge indicator | D101 red, R104 1 k | STAT pulls to GND while charging: LED on. Full or no USB: off. Sits at the plug edge, visible from above. |
| Load sharing | D102 SS34, Q101 AO3401A, R105 100 k | Microchip AN1149. With USB: VBUS feeds the system via D102 (VSYS ≈ 4.6 V), Q101 blocks, the charge controller sees only the battery and terminates charging correctly. Without USB: R105 pulls the gate to GND, Q101 conducts, battery → VSYS. |
| Buffer | C101/C102 4.7 µF, C103 10 µF | The large motor buffers (3 × 47 µF) sit on the main board. |
| Connections | J102 JST-PH, TP101/TP102 solder pads, J103 solder pads | J103 has the same assignment as J1 of the main board: 1 VSYS, 2 D+, 3 D−, 4 GND. |
| Bridge | BT101, BT102, 1 mm trace on the bottom | Connects the two compartment contacts (motor circuit), electrically isolated from the rest. |

Circuit notes:

- **Play while charging:** With USB the motor also runs from VBUS. If the motor draws more than the power supply
  delivers, VSYS drops; below battery voltage − 0.7 V the battery helps via the body diode of Q101.
  The firmware measures VSYS (divider on the main board) and regulates the motor voltage based on it, so
  it is also correct at 4.6 V from USB. D102 (3 A) is rated for the 2 A current limit of the motor driver.
- **No charge detection to the main board:** J1 carries only BAT_IN and GND; there is no charge signal.
  USB on the charger board can be detected indirectly from VSYS > 4.3 V (VSYS measurement of the main board). USB on J4 of the
  main board reports VBUS_DET (IO4).
- **Battery protection:** Use only batteries with a built-in protection circuit (as in the hardware concept).

## 3. Board

Generated with `just charger-pcb` (outline, placement, pre-routing, then Freerouting):
[`hardware/scripts/gen_charger_pcb.py`](../hardware/scripts/gen_charger_pcb.py).

- **46 × 12.5 mm, 1.6 mm thick, 2 layers, assembled on top only** (15 components, plus 5 pure solder pads)
- Passives in 0603 (hand soldering possible, there is enough space)
- From the left: USB-C with ESD and CC resistors | charge controller, LED, load sharing | JST and battery pads | cable pads
- Bottom: bridge (1 mm, about 20 mΩ) along the edge, otherwise ground plane; GND is routed here as well because
  the bridge and power traces would otherwise split the plane into islands
- VBUS is pre-routed (via behind each VBUS pad, collected on the bottom); Freerouting cannot handle the fine pads
- Net classes: VSYS, BAT, bridge 0.8 mm; VBUS 0.5 mm; rest 0.2 mm

| Top | Bottom |
|---|---|
| ![top](bilder/lade-kupfer-oben.png) | ![bottom](bilder/lade-kupfer-unten.png) |

![3D](bilder/lade-platine-3d-oben.png)

DRC: no errors, no warnings, no unconnected items. On the USB footprint the silkscreen has been
removed (it ran over the board edge); the message "differs from library" is therefore disabled
in the project.

## 4. Mechanics

Model: [`hardware/mechanik/ladeplatine.scad`](../hardware/mechanik/ladeplatine.scad), export with `just stl`
(`lade_*.stl` in `build/mechanik/`).

### A: AA insert (upright)

![AA insert](../hardware/mechanik/lade_baugruppe.png)

Same principle as the insert of the main board: **shell** (circle segment behind the board,
printed upright) + **two end caps** with a vertical board slot, joined with filament dowels.
The nickel strips on BT101/BT102 run through the caps to the compartment contacts. The component side
is open; the compartment wall encloses it.

### B: base holder

![Base](../hardware/mechanik/lade_basis.png)

Flat tray with two tabs (Ø 2.2 mm for M2 or sheet metal screw, or simply glue it). The socket
sits on the **long edge** of the board (the plug lies in the board plane, across the long axis).
Therefore the board lies **with its long side against the wall**, not with its end face. The long
edge with the socket is flush with the open long side of the holder.

- Hole in the wall: **13.5 × 7.5 mm** (the overmold of the USB-C plug is up to about 12.4 × 6.5 mm)
- Hole center **4.4 mm** above the surface the holder stands on
- **9.8 mm** sideways from the left end of the holder (seen from inside onto the wall)
- For walls thicker than about 2 mm, push the holder into the hole or file the wall thinner from the inside
  so far that the plug goes fully into the socket (insertion depth about 6.5 mm).

## 5. Wiring

See image above ([SVG](bilder/verdrahtung.svg)).

| Charger board | Wire | Main board / battery | Cross-section |
|---|---|---|---|
| J103-1 VSYS ("V") | red | J1-1 BAT_IN | ≥ 0.25 mm² (motor current up to 2 A) |
| J103-2 D+ | – | – (J1-2 no net) | not needed, flashing via J4 of the main board |
| J103-3 D− | – | – (J1-3 no net) | not needed |
| J103-4 GND ("G") | black | J1-4 GND | ≥ 0.25 mm² |
| J102 pin 1 / pad "+" | red | battery + | battery cable |
| J102 pin 2 / pad "−" | black | battery − | battery cable |

**Check battery polarity before plugging in.** LiPo batteries with a JST-PH plug come with both
pinouts. On the board pin 1 is marked "+"; if necessary, swap the contacts in the plug
or solder to the solder pads.

## 6. Open items

| # | Item | Proposal |
|---|---|---|
| L1 | Does the plug fit into the compartment from above on the new Louie (lid, compartment edges)? | measure on the game; otherwise variant B |
| L2 | Heating of the MCP73831 at 500 mA in the closed compartment | measure on the prototype; otherwise R103 = 3.3 k (300 mA) |
| L3 | Polarity of the batteries used (JST-PH) | check when buying, choose a battery with matching pinout if needed |
| L4 | Contact pressure of the nickel strips on the compartment contacts (bridge carries motor current) | as main board (open items F3) |
| L5 | Wall thickness of the base and position of the hole | measure on the game, adapt holder if needed (`boden`, parameters in the SCAD file) |

## 7. Commands

```
just charger-schematic      generate schematic (overwrites!) + ERC
just charger-pcb            recreate and route the board (overwrites layout!)
just route charger-board    re-route only
just drc charger-board      DRC incl. schematic parity check
just images charger-board   images to docs/bilder/lade-*.png
just fab charger-board      fabrication data
just stl                    printed parts, incl. lade_*.stl
```
