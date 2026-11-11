# USB-C on the main board, power pads for charger board and cell

Status: 2026-11-06 · **Implemented** (formerly "variant E") in the main board; details, pin assignment and
layout are in [main-board-c6.md](main-board-c6.md). Rejected variants (charger board alone, charge controller on
A, charger board via USB-C cable, USB mux, etc.): [decision-history.md](decision-history.md). Complements
[hardware-concept.md](hardware-concept.md), [charger-board.md](charger-board.md) and [idea-power-bank.md](idea-power-bank.md).

Markers: **(verified)** = with a source or recalculated against the project files · **(unverified)** = from
memory or only from a secondary source.

## 1. What is implemented

Priorities of the project owner: (1) USB-C on the main board, also as 5 V input for **all operation incl.
motor** (e.g. power bank in the base), (2) charger board still possible, (3) directly soldered cell, if it comes
cheaply along. All three are met.

| Part | Implementation |
|---|---|
| J4 | HRO TYPE-C-31-M-12 (C165948, 16-pin, USB 2.0), horizontal on the long edge +y, center x ≈ 15.3, opening 0.7 mm behind the edge (y = 6.05). Second source HCTL HC-TYPE-C-16P-01A (C2894897, footprint verified, stock unverified) |
| R12, R13 | 5.1 k each CC1/CC2 to GND (sink); mandatory, otherwise a power bank/C power supply does not switch on VBUS |
| U5 | USBLC6-2SC6 (C7519), D+/D− passed through (main-board-c6.md 2.4) |
| D2 | SS34F (C60396, SMAF, 3 A): VBUS_J4 → VSYS |
| Q1 | AO3401A (C15127): S = VSYS, D = BAT_IN, G = VBUS_J4 |
| R14, R15 | 100 k / 100 k: VBUS divider → VBUS_DET (IO4), also gate pull-down Q1 and VBUS discharge |
| J1 | solder pads bottom: 1 BAT_IN, 2/3 no net, 4 GND (charger board v0.1; **flashing only via J4**) |
| J5 | solder pads bottom 2.5 × 3.5 mm: BAT_IN / GND for a protected cell |

A 6-pin USB-C type (e.g. TYPE-C-31-M-17) is not suitable: it has no data lines (verified, KiCad library).

## 2. Power path (principle Microchip AN1149, as on the charger board)

```
 VBUS (J4) ──┬──|>|── D2 Schottky ──────────────┬── VSYS ──> DRV8213 VM, LDO, divider R6/R7
             │                                  │
             └──────────┐ Gate                  │ S
                       Q1  AO3401A (P-MOSFET)   │
 BAT_IN ─────────────── D ──────────────────────┘    body diode: BAT_IN → VSYS
 (J1: charger board,    │
  J5: cell)         R14/R15 gate → GND
```

| Case | Result |
|---|---|
| USB only | VSYS ≈ 4.65 V via D2. Q1 blocks (gate 5 V), **nothing flows into the cell**. |
| cell/charger board only | gate pulled to GND via R14/R15, Q1 conducts (Rds(on) about 50–90 mΩ at 3–4 V, unverified) → VSYS ≈ VBAT |
| USB + cell | USB supplies, the cell rests: **flashing with battery connected without backfeed**. D2 prevents backfeed into the host. |
| cell reversed | Q1 blocks (Vgs = 0, body diode in reverse direction) → **reverse polarity protection** for everything behind VSYS (recalculated, check on the prototype) |

- Input range at the time 3.0–5.5 V; **today VSYS 3.0–6.6 V with a buck converter for 3.3 V, all current supply
  numbers in [main-board-c6.md](main-board-c6.md) 2.7.** The following points are the original analysis. No Schottky for BAT_IN: 0.35 V loss at a 3.2 V cell would push the LDO into dropout.
- D2 for the motor current: at 2 A about 0.45 V drop, VSYS about 4.5 V. Firmware: limit motor power on USB (VBUS_DET);
  a USB 2.0 port supplies only 500 mA.
- Voltage limits: AO3401A (30 V, ±12 V gate), DRV8213 (up to 11 V), AP2112K (max. 6 V) tolerate 5.5 V (unverified, datasheets).
- AP2112K: dropout about 250 mV at 600 mA; at a 3.3 V cell and Wi-Fi peaks about 3.1 V, the ESP runs from 3.0 V. Because the
  firmware cuts off the cell at about 3.3–3.4 V under load, the LDO is sufficient. A buck-boost is only worth it if the prototype shows brownouts.
- Inrush current: 2 × 47 µF behind D2 is more than USB allows on plug-in (10 µF); not critical in practice (unverified).
- **Measurement:** VBAT_ADC measures VSYS. With a cell directly connected this is the battery level; on USB, IO4 (VBUS_DET) reports "externally powered".

## 3. Operating rules

- **Two sockets (J4 + charger board or enclosure socket):** no mux, only the note "use only one socket". Each
  additional socket feeds in via its own diode at BAT_IN (charger board: D102). No cross current, no backfeed into
  a host. Without Q1, USB via A would charge the battery unregulated through Q101 of the charger board; Q1 is therefore mandatory.
- **Only one source per input:** never cell **and** charger board on BAT_IN at the same time.
- **Battery voltage never goes onto a USB socket.** The charger board is connected via pads and a soldered cable; for
  detachability use a dedicated, mistake-proof connector (e.g. JST-PH), not USB-C.
- **Direct cell only with protection circuit** (protected 18650/14500, LiPo pouch with PCM). Quiescent current in deep sleep today
  approx. 25 µA with the buck converter above 3.8 V, but likely several hundred µA to a few mA between 3.8 and 3.4 V
  (no power-save mode there, main-board-c6.md 2.7); from 3.3 V to deep discharge then takes weeks (unverified), so a
  cell must not stay connected forever.
- **Warning:** **Never** put a 14500 cell (3.7 V) **into the original compartment**. The compartment is in the motor circuit; the
  cell would be in series with the motor and would drive it uncontrolled via the body diodes of the H-bridge.
- **Power bank:** CC resistors switch on VBUS; the sleep current is far below any cut-off threshold. Keep it awake via
  firmware ([idea-power-bank.md](idea-power-bank.md)).

## 4. Mechanics

| Socket position | Space above top side | Socket (height above board) | Fits? |
|---|---|---|---|
| long edge, opening flush at y = 6.75 | 2.15 mm | 3.26 mm | no, corner protrudes about 0.4 mm beyond Ø 14.5 |
| **long edge, opening set back 0.7 mm** (y = 6.05) | 3.5 mm | 3.26 mm | **yes** (calculation r = 7.12 mm; 3D export 6.94 mm, main-board-c6.md 6) |

AA radius 7.25 mm, board top side at z = +0.5 mm (verified, recalculated). End-face, vertical and mid-mount sockets
are rejected (decision-history.md).

**Accessibility:** Rotate the shell in the compartment so the socket edge faces the compartment opening; then it can be plugged in with
the lid removed. In the old Louie (open compartment, C-cell adapter) the socket is reachable when installed.
Otherwise remove it for flashing; updates normally run via OTA.

**Mating forces at 0.8 mm:** insertion about 5–20 N, withdrawal 8–20 N (unverified). The THT tabs hold less in 0.8 mm than
in 1.6 mm. Countermeasures: fully solder all 4 tabs (paste-in-hole, unverified whether available in Economic), support the shell under the
socket (open, main-board-c6.md 6), for continuous operation on a power bank use an angled plug and strain relief on the
shell.

## 5. Still to check

| # | Item | How |
|---|---|---|
| U3 | Rds(on) AO3401A at Vgs = −3.0 V; heat at 2 A; reverse polarity protection | datasheet, prototype with lab power supply |
| U4 | note "use only one socket" in the wiring diagram | charger-board.md |
| U6 | sleep current with direct cell | measure; if needed LDO with low quiescent current |
| U7 | space for 18650/14500 holder in the base of new and old Louie | measure |
| U8 | retention of the tabs in 0.8 mm | 50 mating cycles on the prototype, side load |

## Sources

Retrieved on 2026-11-02 unless stated otherwise. Footprint dimensions from the KiCad 9 library
(`/usr/share/kicad/footprints/Connector_USB.pretty`).

- HRO TYPE-C-31-M-12: https://jlcpcb.com/partdetail/C165948 · https://lcsc.com/product-detail/C165948.html
- HCTL HC-TYPE-C-16P-01A: https://datasheet.lcsc.com/lcsc/2211161000_HCTL-HC-TYPE-C-16P-01A_C2894897.pdf
- Microchip AN1149 (load sharing), as in [charger-board.md](charger-board.md)
- USB-IF, Type-C Cable and Connector Specification (mating forces): https://www.usb.org/documents (values in the text unverified)
