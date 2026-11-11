# Proposal: buck converter instead of the 3.3 V LDO (supply range 3.0–6.6 V)

Status: **decided 2026-11-11: rev B is the design to order** (branch `revb-buck`, section 10); rev A with the LDO stays
on `main` as a fallback. Decision proposal for review finding R-B1 ([review-2026-11-10.md](review-2026-11-10.md)).
Requirement from the project owner: **one main board for 1S Li-ion up to 4 × AA (VSYS 3.0–6.6 V)**, so the
hardware can also be used for other devices. Sections 1–9 are kept unchanged as the record of the proposal (written
before the implementation, so they speak of what "would" change); section 10 is the implemented state. Answers to
section 9: TPS62162, Murata DFE201612P, rev B now, 9 V / 2S stays out. The current numbers are maintained in
[main-board-c6.md](main-board-c6.md) 2.7, the decision record is in [decision-history.md](decision-history.md). **Datasheet delta review against the implemented
rev B: [wiring-review.md](wiring-review.md) section 8** (findings W18–W21, among them W21: no power-save mode below
VSYS ≈ 3.8 V, which limits the standby gain of section 4).

Markers: **(verified)** = read in the datasheet PDF (TI SLVSAM2E for the TPS6216x, SLVSE23 for the TPS62840) or
queried live from the JLCPCB parts API on 2026-11-10 · **(unverified)** = estimate; the generator, the router or a
prototype decides.

## 1. Recommendation in one paragraph

Replace the linear regulator U3 (SPX3819, SOT-23-5) by the synchronous buck **TPS62162DSGR** (fixed 3.3 V, 1 A,
3–17 V input, 17 µA quiescent, WSON-8 2 × 2 mm, the same DSG package as the DRV8213) with a 2.2 µH inductor in
2016 size and 10 µF in / 22 µF out. This removes the heat problem at 6.6 V (about 50 mW instead of 0.5 W), cuts
the standby current from 90–150 µA to roughly 25 µA, keeps every other part of the board unchanged, and costs
about 1 USD per board plus roughly 5 mm² of top-side area, which exists next to the present LDO once two VSYS
pre-route vias move. **It does not improve the empty-cell end**: in 100 % mode the buck is a 0.4–0.6 Ω pass
element, so the cut-off stays at about 3.4–3.5 V under a Wi-Fi peak, the same as with a good LDO. The TPS62840
(60 nA, 6.5 V) is the alternative if standby matters more than price; the TPS6216x is recommended because of
stock, price, the 17 V headroom and the shared footprint with U2.

Adapters (O4) are then only needed for sources above 6.6 V (9 V block, 2S) and for charging chemistry other than
1S Li-ion. The 17 V input of the TPS6216x would even allow a later 9 V / 2S specification after a review of the
divider, the DRV8213 (11 V max) and the R4 back-feed; that is deliberately **not** part of this proposal.

## 2. Requirements for the 3.3 V stage

| Requirement | Value | Why |
|---|---|---|
| Input | 3.0–6.6 V continuous, 7 V transient (4 fresh alkaline cells unloaded) | hardware-concept.md 5.4, main-board-c6.md 2.7 |
| Output | 3.3 V, ≥ 400 mA (ESP32-C6 TX peak about 380 mA), 150 mA average in hotspot mode | ESP32-C6 datasheet, firmware-architecture.md 7 |
| Standby | as low as possible; today about 100 µA total, of which 90–150 µA is U3 | wiring-review.md N17 |
| Dissipation at 6.4 V and 150 mA | must stay well below 0.3 W in the closed compartment | wiring-review.md N17 (SOT-23-5 θJA limit at about 135 mA) |
| Low end | as little dropout as possible at 380 mA, so the 3V3 rail stays ≥ 3.0 V down to a low VSYS | A3, F24 |
| Space | top side only (single-sided assembly), parts ≤ about 1.2 mm high at the edge, machine-assembled | hardware-concept.md 4.1 |
| Noise | ADC inputs (VBAT, ISEN), Wi-Fi/BLE antenna 20 mm away | – |

## 3. Candidates

JLC stock and prices queried on 2026-11-10 (USD, unit price at 10 pieces; all "Extended" parts). Datasheet
values **(verified)** unless marked.

| Part | VIN | IOUT | IQ | 100 % mode dropout at 380 mA | Package | Externals | JLC stock / price | Assessment |
|---|---|---|---|---|---|---|---|---|
| **TPS62162DSGR** (fixed 3.3 V) | **3–17 V** rec., 20 V abs | 1 A | **17 µA** typ, 30 max | HS 430 mΩ at 3 V → about 160 mV + inductor DCR 50 mV = **about 0.2 V** | WSON-8 2 × 2 mm, DSG0008A (same as DRV8213), 0.8 mm high | L 2.2 µH, CIN 10 µF, COUT 22 µF; FB to GND, EN to VIN | C40256, **4 992**, 0.97 | **recommended** |
| TPS62160DSGR (adjustable) | same | 1 A | 17 µA | same | same | plus FB divider (2 × 0402) | C324077, 12 701, 0.70 | fallback if the fixed part runs out; 2 more parts |
| TPS62840DLCR | 1.8–**6.5 V** rec., 7 V abs | 750 mA | **60 nA**, 100 % mode 120 nA | HS 430–600 mΩ at 3.6 V → about 0.2 V + DCR | VSON-8 1.5 × 2 mm (DLC) | L 2.2 µH, CIN ≥ 4.7 µF, COUT 10 µF; RSET 267 k for 3.3 V (1 %), MODE and STOP to GND | C2071859, 2 391, **3.31** | best standby; 3× the price, 6.5 V limit at the edge for fresh alkaline, own footprint |
| TPS62170DSGR | 3–17 V | 0.5 A | 17 µA | higher Rds | DSG | like TPS6216x | C124041, 2 049, 1.44 | 500 mA too close to the TX peak |
| TPS62085RLTR | 2.3–**6 V** rec. | 3 A | about 17 µA (unverified) | – | VSON-7 2 × 2 | 1 µH | C130072, 3 760, 0.57 | 6 V limit = O5 border, not 4 × alkaline |
| TPS628501DRLR | 2.7–**6 V** rec. | 1 A | 17 µA | – | SOT583 1.6 × 2.1 | 0.47 µH | C3193207, **4** | 6 V limit and no stock |
| TPS62130RGTR | 3–17 V | 3 A | 17 µA (unverified) | – | QFN-16 3 × 3 | 2.2 µH, larger | C43590, 25 429, 0.92 | too large |
| SPX3819M5-L-3-3 (today) | 2.5–16 V | 0.5 A | 90 typ / 150 max µA | 350–610 mV at 150–380 mA | SOT-23-5 | 2 caps | C20617301, 84 793, 0.08 | heat 0.5 W at 6.4 V / 150 mA; MLCC stability unverified (W14) |
| AP2112K-3.3 (O5) | 2.5–**6.0 V** rec., 6.5 abs | 0.6 A | 55 µA | 250 mV max at 600 mA | SOT-23-5 | 2 caps | C51118, 10 532, 0.15 | fine up to 3 × AA / 4 × NiMH, not 4 × alkaline |

TPS6216x facts **(verified, SLVSAM2E):** VIN 3–17 V recommended, 20 V absolute; IQ 17 µA typ (30 µA max over
temperature), shutdown 1.5 µA; UVLO falling 2.7 V typ (2.6–2.82 V), 180 mV hysteresis; high-side 300 mΩ typ at
VIN ≥ 6 V, 430 mΩ at 3 V, 600 mΩ max; low-side 120/165 mΩ; current limit 1.95 A typ; 2.25 MHz PWM, power-save
mode at light load; 100 % duty-cycle mode with VIN(min) = VOUT + IOUT × (RDS(on) + RL); EN high ≥ 0.9 V, abs max
VIN + 0.3 V (tie to VIN is allowed); FB of the fixed version to AGND; VOS to the output capacitor; PG open drain,
can stay open; exposed pad must be soldered and tied to AGND; θJA 61.8 K/W (DSG). Input capacitor 10 µF
recommended; TI's example uses 22 µF 6.3 V 0805 at the output, inductors 2.2–3.3 µH, 1.3–1.9 A, 2.0 × 2.5 mm
and up; "3.3 µH recommended for low input voltages to allow the full 1 A" (we need ≤ 0.5 A, so 2.2 µH is fine).

TPS62840 facts **(verified, SLVSE23):** VIN 1.8–6.5 V recommended, 7 V absolute; IQ 60 nA (36 nA typ into VIN,
56 nA into VOS), 120 nA in 100 % mode; 1.8 MHz; high-side 430 mΩ typ / 600 max at 3.6 V, 340/465 at 5 V; VOUT by
RSET on VSET (E96, 1 %): 3.3 V = 267 k for the TPS62840; COUT 3–40 µF effective (10 µF typical), CIN ≥ 1 µF
effective (4.7 µF typical); inductor 2.2 µH, TI lists 2.0 × 1.6 × 1.2 mm and 2.0 × 1.2 × 1.0 mm parts; STOP pin
halts switching for noise-free measurement windows; MODE pin selects forced PWM; θJA 105.6 K/W (DLC).

### 3.1 Inductor candidates (2.2 µH, 2016 = 2.0 × 1.6 mm, 1.0–1.2 mm high; JLC 2026-11-10)

Ripple at 6.6 V, 3.3 V out, 2.25 MHz, 2.2 µH: ΔI = 3.3 V × 0.5 / (2.25 MHz × 2.2 µH) ≈ **0.33 A p-p**; peak at 0.5 A
load about 0.67 A; at the 1.95 A current limit the inductor must not saturate hard, so ≥ 1.5 A saturation is
preferred. Low DCR matters for the 100 % mode dropout.

| Part | DCR | Irms / Isat | Stock | Price (10) | Note |
|---|---|---|---|---|---|
| **Murata DFE201612P-2R2M=P2** (C79317) | 144 mΩ | 1.5 / 2.1 A | 6 895 | 0.09 | recommended; 1.2 mm high |
| Murata DFE201610E-2R2M=P2 (C337891) | 140 mΩ | 1.7 / 2.4 A | 5 342 | 0.12 | 1.0 mm high, same family as TI's TPS62840 example |
| Sunlord WPN201610H2R2MT (C97005) | 170 mΩ | 1.45 / 2.15 A | 27 024 | 0.04 | cheapest with stock |
| Sunlord WPN201610U2R2MT (C71386) | 120 mΩ | 1.8 / 1.9 A | 845 | 0.05 | lowest DCR, little stock |
| Sunlord SWPA252012S2R2MT (C23894) | 216 mΩ | 1.25 / 2.07 A | 31 528 | 0.04 | 2.5 × 2.0 mm, if 2016 does not fit the router |

Multilayer types (MPL2016, MLP2016, 110 mΩ, 1.2 A) are not recommended: their saturation current is below the
converter's current limit.

## 4. The proposed circuit

```
VSYS ──┬── C8 10 µF/16 V 0603 ── GND
       ├── U3.2 VIN      U3.7 SW ──── L1 2.2 µH ───┬── +3V3 ──┬── C9 22 µF/10 V 0805 ── GND
       └── U3.3 EN                  U3.6 VOS ─────┘           └── C10 100 nF (stays, at the module side)
           U3.5 FB ── GND (AGND)    U3.8 PG open
           U3.1 PGND, U3.4 AGND, U3.9 EP ── GND (2 thermal vias to In1, as for U2)
```

- **C11 (1 µF at the old LDO output) is dropped**; C9 grows from 10 µF 0603 to 22 µF 0805 (TI's example; 22 µF
  0603 10 V exists but loses too much to DC bias). C8 grows from 1 µF 0402 to 10 µF 0603.
- **Net classes:** SW node short and 0.3 mm wide, L1 → C9 → VOS as a tight loop; VSYS into VIN 0.4 mm as today.
  The GND of C8, C9 and the EP meet at the exposed pad (single-point ground per the datasheet layout figure).
- **Thermal vias:** 2 × 0.3 mm in the EP like U2 (`gen_main_pcb.py` already does this for the DRV8213).
- **Electrical consequences:**

| Item | Today (SPX3819) | With TPS62162 |
|---|---|---|
| Dissipation 6.4 V, 150 mA | 0.47 W, SOT-23-5 at its θJA limit | about 50 mW (η ≈ 90 %) |
| Dissipation 4.0 V, 150 mA (Li-ion) | 0.1 W | about 40 mW |
| Standby (board total) | about 100 µA | about **25 µA**: 17 µA U3 + 5 µA VBAT divider + 2 µA LIS2DH12 + leakage; 14500 cell about 3 years, 4 × AA about 10 years |
| 3V3 at VSYS 3.5 V, 380 mA peak | 3V3 ≈ 2.9–3.15 V (dropout 350–610 mV) | 3V3 ≈ **3.3 V** down to VSYS ≈ 3.5 V, then 100 % mode: VSYS − 0.2 V (unverified: Rds at low VIN and DCR tolerance) |
| Firmware cut-off | 3.6 V (`VSYS_MIN_MV`) | **3.4–3.5 V** filtered (review R-B2); hard floor: UVLO 2.7 V |
| Output ripple / noise | none | 2.25 MHz, some mV p-p with 22 µF; power-save mode at light load (lower frequency pulses) |
| EMI | none | switch node 2 × 2 mm, 1.95 A limit; harmonics far below 2.4 GHz; keep the loop tight (unverified: RSSI test T4 covers it) |
| Start-up | immediate | soft start, PG optional; UVLO 2.7 V means a cell at 3.0 V starts |

**What the buck does not fix:** the Q1 body-diode case with USB plus a pack above 5.2 V (F28) and the LED LDO U6
stay as they are. Review R-B2 (cut-off on a filtered reading) still applies.

## 5. Space on the board

Current top-side parts around U3 (coordinates relative to the board centre, from `placement.py` and the board
file, **verified**):

| Ref | Footprint | x, y | Courtyard (approx.) |
|---|---|---|---|
| U3 | SOT-23-5 | 2.35, 4.80 | 3.2 × 3.2 → x 0.75…3.95, y 3.2…6.4 |
| C8 | 0402 | 1.05, 2.30 | 1.4 × 0.8 |
| C11 | 0402 | 3.05, 2.30 | 1.4 × 0.8 |
| C9 | 0603 | 5.60, 2.30 | 2.0 × 1.2 |
| C10 | 0402 | 8.30, 2.30 | 1.4 × 0.8 |
| Q1 | SOT-23 | 7.60, 4.85 | 3.2 × 3.2 → x 6.0…9.2 |
| R6, R7 | 0402, 90° | −0.40, 5.60 / 3.50 | 0.8 × 1.4 each |

Free today on top: **x 4.0…6.0, y 3.2…6.4 (about 6.4 mm²)**, except for the VSYS pre-route `preroute_battery_vsys()`:
0.5 mm track from Q1 pin 2 to two vias at **(4.67, 5.8)** and **(4.67, 5.0)**, then on the bottom south at x 4.67.
On the bottom under this area: J2 pads at y 4.3, x −1.68 / 0.86 / 3.40 / 5.94 / 8.48 (1.4 mm wide), and the
bottom VSYS track between J2 pads 3 and 4.

Area accounting (courtyards, **unverified**, the router decides): U3 SOT-23-5 10.2 mm² + C11 1.1 + C8 1.1 + C9 2.4
= 14.8 mm² today; new U3 WSON 2 × 2 about 6.8 mm² + L1 2016 about 4.8 + C8 0603 2.4 + C9 0805 3.8 = 17.8 mm²,
so **about +3 mm²**, plus room for the loop. Proposed placement sketch:

| Ref | New position | Note |
|---|---|---|
| U3 (WSON) | (1.8, 4.9), rotation so that VIN/EN face −x and SW/VOS face +x | EP vias at (1.25, 4.9) and (2.35, 4.9) fall between J2 pads 2 and 3 on the bottom (pad edges at x 1.56 and 2.70): 0.3 mm vias fit, 0.5 mm annular ring touches; shift J2 by 0.3 mm or use one EP via |
| C8 (0603) | (1.0, 2.5) | at VIN, GND to the EP side |
| L1 (2016) | (4.3, 4.9), rotated 90° | SW pad at x ≈ 3.0, output pad towards C9 |
| C9 (0805) | (5.3, 2.4) | replaces the 0603; VOS from here back to U3 pin 6 |
| VSYS vias of `preroute_battery_vsys()` | move to x ≈ 6.0 (between L1 and Q1, y 5.0/5.8) | keeps the 0.5 mm path Q1 → bottom → C2 |
| C11 | dropped | – |

Height: L1 1.0–1.2 mm and WSON 0.8 mm at y ≈ 5 are inside the envelope (the module at 2.4 mm sets the limit;
`just hull` confirms, review R-D7).

## 6. Change list

### Hardware generators and library

| File | Change |
|---|---|
| `hardware/scripts/gen_main_schematic.py` | U3 block: TPS62162DSGR (`lcsc` C40256) with pins 1 PGND, 2 VIN, 3 EN = VSYS, 4 AGND, 5 FB = GND, 6 VOS = +3V3, 7 SW = new net `SW3V3`, 8 PG open, 9 EP = GND; new L1 (`SW3V3` → `+3V3`); C8 → 10 µF 16 V 0603; C9 → 22 µF 10 V 0805; drop C11; comment block on the 3.0–6.6 V rationale |
| `hardware/scripts/gen_symbols.py` | symbol `louie:TPS62162DSG` (own symbol because of pin types for ERC, as for the DRV8213) and an inductor symbol if `Device:L` is not enough |
| `hardware/scripts/fetch_parts.py` | footprint: reuse `Package_SON:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm` (DSG0008A, verified for both TI parts) with the TI 3D model; inductor footprint `Inductor_SMD:L_2016_...` or the LCSC footprint of the chosen part (check pad size against the Murata drawing) |
| `hardware/scripts/placement.py` | positions from section 5; remove C11 |
| `hardware/scripts/gen_main_pcb.py` | `preroute_ties()`: drop the U3 VIN–EN tie or re-point it to the new pins; add a pre-route SW → L1 → C9 → VOS (0.3 mm, F.Cu) and VIN ← C8; EP thermal vias like U2; move the two VSYS vias in `preroute_battery_vsys()`; net class for `SW3V3` (0.3 mm, no vias) |
| `hardware/routing-score.toml`, `route_gate.py` | `SW3V3` in the power width check (0.3 mm) and, if useful, a "switch node length" soft metric |
| `hardware/bom/parts.csv` | U3 row, new L1 row (part, DCR, Isat), C8/C9 values, C11 removed; alternatives TPS62160 + divider, TPS62840 |
| `hardware/scripts/hull_check.py` | nothing (L1 is on top, below the module height) |

### Documents

| Document | Change |
|---|---|
| main-board-c6.md 2.7 | supply table: U3 = TPS62162, L1, dissipation, standby, cut-off; remove the SPX3819 rows; new section on the switch-node layout |
| hardware-concept.md 5.4, 5.5 | VSYS 3.0–6.6 V, U3/L1 rows, remove the stale AP2112K/470k text (review R-I1) |
| open-items.md | F18 (reference this proposal), F24 (cut-off 3.4–3.5 V filtered), F27 (SPX3819 load-step test replaced by section 7 below), A3 (rewrite for the buck); new assumption "buck stable with the chosen L/C" |
| wiring-review.md | delta review of the new block (pin by pin against SLVSAM2E) before ordering, same method as section 7 there |
| test-hardware.md 4.7 | replace the LDO load-step test by the buck test in section 7 |
| cost-estimate.md | +0.97 USD (U3) + 0.09 (L1) + 0.05 (caps) per board; one more extended type (inductor) +3.07 USD per order |
| decision-history.md | entry "LDO → buck (2026-11-xx)" with the rejected options O1/O3/O5 once decided |
| review-2026-11-10.md R-B1 | link to this proposal |

### Firmware

| File | Change |
|---|---|
| `firmware/louie-fw/src/main.rs` | `VSYS_MIN_MV` 3600 → about 3450 as a placeholder; comment that the buck is in 100 % mode below about 3.5 V; implement the filtered cut-off from review R-B2 in step 4 |
| `firmware/louie-fw/src/board/louie_v1.rs` | comments only (regulator type); no pin changes |
| firmware-architecture.md 7 (power) | standby budget about 25 µA; optional: note that a TPS62840 STOP pin would need a GPIO (none free except IO22), so it is not planned |

### Mechanics

Nothing: all new parts are on top and lower than the module.

## 7. Tests this adds (prototype board)

| Test | Pass |
|---|---|
| 3V3 ripple and spikes at 3.0 / 3.7 / 5.0 / 6.6 V VSYS, no load and 300 mA load (scope at C9, 20 MHz limit) | ≤ 30 mV p-p, no sustained ringing |
| Load step 0 → 300 mA (as in the old 4.7 setup, now on the prototype) | dip ≤ 150 mV, recovery ≤ 100 µs |
| 100 % mode entry: sweep VSYS down from 4.0 to 3.0 V at 150 mA and at 380 mA, read 3V3 | 3V3 ≥ 3.0 V down to VSYS ≈ 3.3 V at 150 mA, ≈ 3.5 V at 380 mA (sets the cut-off numbers) |
| Standby current of the board in deep sleep at 3.7 V and 6.0 V | ≤ 40 µA |
| Wi-Fi TX at 6.6 V, 10 min, temperature of U3 and L1 | < 60 °C in free air |
| ADC noise on VBAT_ADC and ISEN_ADC with the converter in power-save mode vs. a bench LDO on 3V3 | no visible difference at 10 Hz sampling |
| RSSI test T4 with and without the converter running (jumper VSYS → 3V3 from a bench supply) | no RSSI difference > 2 dB |

## 8. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Router cannot close the SW loop and the moved VSYS vias in the dense +y area | medium (unverified) | pre-route the whole block (VIN cap, SW, L1, C9, VOS) as locked tracks; fall back to the 2.5 × 2.0 mm inductor place or hand-finish (review R-A2) |
| TPS62162DSGR stock drops before ordering (4 992 today) | low | TPS62160DSGR (12 701) with an FB divider of 2 × 0402 (0.8 V reference: e.g. 1 M / 320 k, or 100 k / 32 k) |
| Power-save-mode pulses disturb the ADC readings | low | 100 nF filters on both ADC inputs already exist; forced PWM is not available on the fixed part; measure |
| 4 fresh alkaline cells unloaded: 6.6 V with the 17 V part | none | – (this is the reason not to take the 6.5 V TPS62840) |
| Low-end dropout equals the LDO | certain | accept: cut-off at about 3.4–3.5 V filtered; only a buck-boost would change this and it does not fit |

## 9. Open for the project owner

1. Go for TPS62162 (recommended) or TPS62840 (standby first, 3× price, 6.5 V limit)?
2. Inductor: Murata DFE201612P (recommended) or the cheaper Sunlord WPN201610H?
3. Do the layout change now (rev A, routing is open anyway) or keep SPX3819 for rev A and plan the buck for rev B?
4. Should the 9 V / 2S question (17 V input available) be looked at in the same step, or stay out as proposed?

## 10. Rev B trial (branch `revb-buck`, 2026-11-11)

Implemented as proposed in section 6, with the placement corrected to the real courtyards of the KiCad footprints
(the sketch in section 5 was too optimistic by about 0.3 mm):

| Ref | Position (x, y, rot) | Note |
|---|---|---|
| U3 TPS62162DSG | (2.4, 4.97, 90°) | pins 1–4 (PGND, VIN, EN, AGND) at y 5.9 towards the edge, pins 5–8 (FB, VOS, SW, PG) at y 4.0; **one** thermal via at (2.13, 4.97), centred in the gap between J2 pads 2 and 3 on the bottom (two do not fit) |
| L1 DFE201612P | (2.4, 2.2, 0°) | pad 1 (SW) under pin 7, pad 2 (+3V3) towards C9; pads end 0.2 mm above the USB pair in the channel (y 1.13) |
| C8 10 µF 0402 | (0.58, 5.6, 90°) | pad 1 (VSYS) at the edge side; R6/R7 moved 0.06 mm left to make room |
| C9 22 µF 0805 | (5.45, 2.1, 0°) | below Q1, pad 1 towards L1 pad 2 |
| Q1 | (7.6, 4.95) | 0.1 mm towards the edge so that the C9 courtyard clears it |
| VSYS vias (`preroute_battery_vsys`) | (5.5, 5.9) and (5.5, 6.47) | right of L1 instead of x 4.67; bottom path jogs back to x 4.67 |
| VSYS edge track | y 6.5, 0.3 mm | from the outer via west to C8 pad 1; VIN/EN tied and fed from it |
| C11 | dropped | – |
| J2 | unchanged (3.4, 4.3) | moving it down collided with U6, TP1 and R22 |

Pre-routed and locked: VIN–EN tie, VIN escape, SW (pin 7 → L1 pad 1, 0.2 mm next to the pads then 0.3 mm), L1 pad 2 →
C9 pad 1 (0.3 mm), VOS → L1 pad 2 (0.2 mm), GND stubs of PGND/AGND/FB into the exposed pad. Unrouted board: ERC 0,
DRC only the expected dangling pre-route vias, schematic parity 0. Quick router check: 52 of 54 signal connections
routable one by one with rip-up.

**Routing result (2026-11-11, `just route main-board runs=8`, own router, 4 in parallel, about 75 min):**

| Attempt | Variant (via cost / F / B) | Open after router | After stitching | DRC errors | GND islands | Vias | Track mm | S |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 30 / 1.3 / 1.15 | 0 | 0 | 3 | 0 | 160 | 816 | 129.0 |
| 2 | 20 / 1.3 / 1.15 | 2 | 2 | 0 | 0 | 157 | 930 | 141.7 |
| 3 | 40 / 1.3 / 1.15 | 1 | 1 | 0 | 0 | 157 | 857 | 128.3 |
| **4** | **30 / 1.6 / 1.3** | **0** | **0** | **0** (1 warning) | **0** | **162** | **806** | **112.3** |
| 5 | 25 / 1.1 / 1.0 | 0 | 0 | 0 | 0 | 167 | 862 | 120.2 |
| 6 | 35 / 1.5 / 1.1 | 0 | 0 | 0 | 0 | 157 | 857 | 125.1 |
| 7 | 30 / 1.3 / 1.15, seed 1 | 1 | 1 | 0 | 0 | 156 | 826 | 121.2 |
| 8 | 20 / 1.3 / 1.15, seed 1 | 1 | 0 | 0 | 1 | 155 | 806 | 124.3 |

Five of eight attempts are complete (0 open, 0 DRC errors); the gate took attempt 4. After removing one dangling
3V3 spur (two router segments, 1.05 mm, same clean-up as for the rev A baseline): **0 unconnected, 0 DRC errors,
0 warnings, 0 GND islands, schematic parity 0, 162 vias (90 signal), 805 mm track, S 110.3**, power paths within
width, antenna keepout clean (`hardware/main-board/routing.json`, fingerprint 53263dc0ea).
For comparison, rev A at the same commit: 0 open, 0 DRC, 0 islands, 157 vias, 808 mm. **The buck block costs
the router nothing measurable**; the switch node stayed on F.Cu as pre-routed (2.0 mm), 3V3 leaves the block on In2.

No router change was needed. Conclusion for the owner's decision rule ("if it does not auto-route, the option is
out"): it does.
