# Proposal: low standby current with a Li-ion cell (finding W21)

Status: **decided 2026-11-11: option A (LDO TPS7A2633) is implemented in rev B** (branch `revb-buck`); the sections
below are kept as the record of the comparison. Decision proposal for open item F29 / finding W21
([wiring-review.md](wiring-review.md) 8.2).
Requirement from the project owner: **a 1S Li-ion cell must be usable**, including a low standby current, on the same
board that also runs from 3–4 × AA (VSYS 3.0–6.6 V). At the time of writing rev B used the buck TPS62162;
the current design is in [main-board-c6.md](main-board-c6.md) 2.7.

Markers: **(verified)** = read in the datasheet PDF named in section 7, or queried live from the JLCPCB parts API on
2026-11-11 · **(unverified)** = estimate; a prototype measurement decides.

## 1. The problem

SLVSAM2E p.11 (TPS6216x): "When VIN decreases to typically 15% above VOUT, the TPS6216x does not enter power save
mode, regardless of the load current." For 3.3 V out this is **VIN below about 3.8 V**. Between about 3.8 V and the
start of 100 % mode (about 3.4 V) the converter switches in PWM at 2.25 MHz even when the board sleeps. The datasheet
gives no current for this case; sister parts of the same family specify the PWM no-load current as 5 mA (TPS629210)
and 8 mA (TPS62902) at 12 V in (verified). At 3.4–3.8 V it is lower but very likely **in the mA range** (unverified).

A 1S Li-ion cell spends a large part of its capacity between 3.8 and 3.4 V. With about 2 mA a 1000 mAh cell is empty
after about three weeks on the shelf instead of years. That rules out rev B as it is for the primary use case.

The same rule is in every other DCS-Control converter of the 3–17 V class that was checked: TPS629210, TPS62902 and
TPS6213x (verified). It is not a property of one part but of this converter family.

## 2. Requirements

| Requirement | Value | Source |
|---|---|---|
| Input | 3.0–6.6 V continuous (1S Li-ion to 4 × AA fresh), 7 V transient | main-board-c6.md 2.7 |
| Output | 3.3 V, ≥ 400 mA peak (ESP32-C6 TX about 380 mA), 150 mA average in hotspot mode | firmware-architecture.md 7 |
| Standby | low over the **whole** input range; board target ≤ 40 µA (test T13) | this proposal |
| Low end | 3V3 ≥ 3.0 V at the 380 mA peak down to the cut-off (3.4–3.5 V filtered) | review R-B2 |
| Heat | well below the limit in the closed compartment at 6.4 V and 150 mA | review R-B1 |
| Space | top side, the area of today's U3/L1/C8/C9 block | main-board-c6.md 2.7 |

Board standby without the regulator, the same for all options: ESP32-C6 in deep sleep about 7 µA, VBAT divider
680 k/470 k 3–6 µA, LIS2DH12 about 2 µA if fitted, plus leakage → **about 12–15 µA** (unverified sum).

## 3. Options

### A. Low-Iq LDO in a thermal-pad package: TPS7A2633 (WSON-6 2 × 2)

- **Data (verified, SBVS290B):** VIN 2.4–18 V, 500 mA, IQ 2 µA typ / 4.5 µA max at no load, ground current 11–15 µA at
  1 mA load (figure 9), dropout 173 / 280 mV (typ / max) at 250 mA and 355 / 590 mV at 500 mA, current limit
  525–970 mA, EN up to 18 V (tie to IN), stable with 1–100 µF ceramic output capacitors, θJA 73.3 K/W (JEDEC board,
  WSON with exposed pad). KiCad footprint `Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm`.
- **JLC (verified):** C2876256, 809 in stock, 0.66–0.76 USD (30+/10+). Adjustable TPS7A2601DRVR C2859671, 597 in
  stock, as a second source with a divider.
- **Standby:** no mode change over the whole range: about 2–3 µA for the regulator at deep-sleep load, board about
  15–18 µA (unverified). In dropout the IQ is not specified (unverified).
- **Heat:** the reason the owner rejected "a better LDO" on 2026-11-11 was the SPX3819 in SOT-23-5 with θJA 191 K/W
  (wiring review W17): 0.47 W at 6.4 V / 150 mA gave about +90 K. The TPS7A26 in WSON has 73.3 K/W:

  | VSYS, 150 mA average | Dissipation | Rise (θJA 73.3 K/W) | Note |
  |---|---|---|---|
  | 6.4 V (4 × alkaline, fresh) | 0.47 W | about +34 K | the small board may give more, +40–50 K (unverified) |
  | 5.3 V (4 × AA, mid-life / NiMH) | 0.30 W | about +22 K | most of the AA life |
  | 3.7–4.2 V (Li-ion) | 0.06–0.14 W | +4…+10 K | primary case |

  The thermal limit (TJ 125 °C at 40 °C ambient) is about 1.16 W, i.e. about 350 mA average at 6.6 V.
- **Low end:** at 380 mA about 0.27 V typ, up to about 0.45 V max (interpolated from the table) → 3V3 ≥ 3.0 V down to
  about VSYS 3.3–3.45 V; the cut-off stays at 3.4–3.5 V (3.5 V if the worst case is taken).
- **Efficiency:** with Li-ion the same as the buck (3.3 / 3.7 V ≈ 89 %). With 4 × AA the electronics draw 150 mA from
  the cells instead of about 105 mA with the buck. The motor draws most of the battery current during a round, so the
  play time drops by perhaps 10 % (unverified; motor current not measured yet, A2).
- **Layout:** no inductor, no switch node: W18, W20 and N23 disappear, and the ripple and ADC-noise tests become
  trivial. U3 keeps the 2 × 2 mm outline; C8 (≥ 1 µF, better 4.7–10 µF 16–25 V) at IN, C9 22 µF stays. The L1 area
  becomes free. New placement and routing run needed.
- **Cost:** about −0.3 USD per board compared with rev B (no L1), and one Extended type fewer.

### B. Buck with power-save mode down to 100 % mode: TPS62840 family

- **Data (verified, SLVSEC6D):** VIN 1.8–**6.5 V** recommended, **7 V absolute**; 750 mA; IQ 60 nA, **120 nA in 100 %
  mode**; no "no PFM near VOUT" rule: PFM down to the 100 % mode, set point +30 mV just before it; high side 430 /
  600 mΩ (typ / max) at 3.6 V; output voltage by one E96 resistor on VSET; TI lists the DFE201612E 2.2 µH as inductor,
  CIN 4.7 µF, COUT 10 µF. **EN, MODE, STOP: 6.5 V absolute**, so EN cannot be tied to VIN; the internal 200–450 kΩ EN
  pull-down is disconnected after start-up. EN from a divider, e.g. 220 k from VIN and 1 M to GND: 1.29 V at VIN 3.0 V
  with the worst-case pull-down during start (VIH 1.1 V), 5.7 V at 7 V after start, about 3 µA (calculated).
- **Packages and JLC (verified):** DLC VSON-8 1.5 × 2 mm (KiCad `Package_SON:VSON-8_1.5x2mm_P0.5mm`, to check against
  TI's land pattern) C2071859, 2 368 in stock, **3.4–3.7 USD**; YBG WCSP-6 1 × 1.5 mm C2071139, 3 039 in stock,
  0.84–0.94 USD (no MODE/STOP pin; X-ray at JLC and no hand rework); TPS62842DGR HVSSOP-8 3 × 3 mm C2873354, 44 929
  in stock, 0.33–0.35 USD, but about twice the area of the 2 × 2 mm WSON.
- **Standby:** about 0.1 µA regulator + 3 µA EN divider, board about 15–18 µA over the whole range (unverified).
- **Heat:** like the TPS62162 (about 50 mW at 6.4 V).
- **Low end:** 0.38 A × (0.6 + 0.144) Ω ≈ 0.28 V worst case, like rev B.
- **The catch:** 4 fresh alkaline cells sit at 6.3–6.6 V without load (unverified, 1.58–1.65 V per cell), i.e. up to
  0.1 V **above the recommended 6.5 V**, and in deep sleep there is no load to pull them down. The absolute maximum of
  7 V is not reached, but there is no margin left for plug-in transients. With NiMH (≤ 5.6 V) and 3 × AA it is fine.
- **Layout:** like rev B plus RSET and the EN divider (3 × 0402); W18 (L1 footprint) and W19 (C8) still apply.

### C. Hybrid: keep the TPS62162 for load, add a TPS7A26 for standby

- TPS7A2601 (adjustable) set to about 3.1 V on the same +3V3 rail; the buck EN driven by IO22 (the only free GPIO)
  with a pull-down, so it is **off by default**. In deep sleep IO22 cannot hold a level (only IO0–IO7 are LP GPIOs,
  datasheet-facts G1-ESP32-31), the pull-down switches the buck off and the LDO carries the µA load. After wake-up the
  firmware switches the buck on; at 3.3 V ± 3 % it is always above the LDO at 3.1 V ± 1 %, so the LDO idles.
- **Pros:** buck efficiency and heat in operation, LDO standby (about 15–20 µA) over the whole range.
- **Cons:** the ESP boots and sleeps at 3.1 V (spec minimum 3.0 V), the boot current comes from the LDO, a firmware
  fault leaves the board on the LDO (safe, but warm with 4 × AA), two regulators and about 4 more parts on an area that
  is already full, W18/W19 stay. Most complex option.

### D. Rejected without further work

| Option | Why not (verified unless noted) |
|---|---|
| Keep rev B and accept W21 | mA standby with Li-ion contradicts the requirement |
| TPS62160 (adjustable) at 3.1 V out | the PWM window shrinks to about 3.3–3.6 V but stays; ESP at 3.1 V ± 3 % is at its 3.0 V limit |
| TPS629210, TPS62902, TPS6213x | same 15 % rule as the TPS6216x |
| TPS62125 | 300 mA, below the TX peak |
| TPS62177 | VIN from 4.75 V |
| TPS7A25 | 300 mA |
| LT8607, LTC3621 (ADI) | JLC stock 0–39, 2.4–10 USD |
| L6981 (ST) | VIN from 3.5 V, SO-8 |
| Buck-boost TPS63802 | VIN max 5.5 V; buck-boost in general too large (rejected 2026-11-11) |
| Soft-power latch on the buck EN (lever or button starts the board) | the lever wake works through 3V3 (R4), so it would need a new wake path; large change |

## 4. Comparison

| | Rev B today (TPS62162) | **A: TPS7A2633 LDO** | B: TPS62840 buck | C: hybrid |
|---|---|---|---|---|
| Board standby, VSYS > 3.8 V | about 25–30 µA | **about 15–18 µA** | about 15–18 µA | about 15–20 µA |
| Board standby, VSYS 3.4–3.8 V (Li-ion) | **mA range** (W21) | about 15–18 µA | about 15–18 µA | about 15–20 µA |
| Heat at 6.4 V / 150 mA | about 50 mW | 0.47 W, about +34 K | about 50 mW | about 50 mW |
| VIN limit | 17 V | 18 V | **6.5 V rec. / 7 V abs** | 17 V |
| 3V3 drop at 380 mA (low end) | 0.22–0.26 V | 0.27 V typ, 0.45 V max | ≤ 0.28 V | 0.22–0.26 V |
| Switching noise (ADC, RSSI) | 2.25 MHz | **none** | PFM / 2 MHz | in operation |
| 4 × AA play time | best | about −10 % (unverified) | best | best |
| Parts in the block | U3, L1, C8, C9 | **U3, C8, C9** | U3, L1, C8, C9, 3 R | U3, L1, C8, C9, U7, C, 3 R |
| Open review findings | W18–W21 | none known | W18, W19, 6.5 V | W18, W19 |
| Regulator cost (JLC, 10+) | 1.06 USD | **0.76 USD** | 3.79 USD (DLC) | 1.8 USD |
| JLC stock (2026-11-11) | 4 823 | 809 | 2 368 (DLC) | 4 823 / 597 |

## 5. Recommendation

**Option A, TPS7A2633 in WSON-6.** It is the only option that meets the Li-ion requirement over the whole range
without a new risk. It also removes the open buck findings, makes the board quieter for the ADC and the antenna, and
is the cheapest and smallest. The price is heat with 4 fresh alkaline cells in hotspot mode, about +34 K by the
datasheet, which the WSON package handles. The extra heat that led to the rejection on 2026-11-11 came from the
SOT-23-5 package of the SPX3819, not from linear regulation as such. The other price is somewhat shorter play time
on 4 × AA.

Option B is the better choice only if 4 × AA play time or the last 0.3 W of heat matters more than the 6.5 V margin.
In that case, take the DLC package and the EN divider, and accept the out-of-spec phase on fresh alkaline cells.
Option C is not recommended: its complexity is out of proportion for a toy.

## 6. What would change with option A

| Area | Change |
|---|---|
| `gen_symbols.py`, `gen_main_schematic.py` | symbol TPS7A26 (fixed: 1 OUT, 2 NC → GND, 3 PG → GND or open, 4 EN = IN, 5 GND, 6 IN, pad GND); drop L1 and net SW3V3; C8 ≥ 4.7 µF 16–25 V at IN |
| `placement.py`, `gen_main_pcb.py` | U3 on the WSON-6 footprint, C8 at IN, C9 at OUT; drop `preroute_buck()` parts for SW/VOS; new routing run and baseline |
| `parts.csv` | U3 TPS7A2633DRVR C2876256 (second source TPS7A2601 + divider), L1 removed |
| `firmware/louie-fw/src/main.rs` | `VSYS_MIN_MV` placeholder 3500 stays (comment: LDO dropout) |
| Documents | main-board-c6.md 2.7, decision-history.md (rev C or rev B update), open-items F29/A3/A21, test-hardware 4.7 (T10/T11/T15 shrink to a 3V3 check, T13 standby, T14 temperature of U3 at 6.6 V), cost-estimate.md (−1 Extended type) |

A datasheet delta review of the new block follows the same method as wiring-review.md 8.

## 7. Sources

All read on 2026-11-11 (PDFs from ti.com, not committed). JLC stock and prices from the JLCPCB parts API on the same
day.
- TPS6216x SLVSAM2E (Rev. E, May 2017), p.11 power-save rule, p.6 IQ "device not switching".
- TPS7A26 SBVS290B (Oct 2019): electrical characteristics, figures 9–12, thermal information.
- TPS6284x SLVSEC6D (Mar 2020): absolute maximum ratings, 8.3.1 smart enable, 8.4.1 power-save mode, 8.4.3 100 % mode,
  device comparison table, 9.2.2 components.
- TPS629210 SLVSGE0B (Jan 2022) and TPS62902 SLVSFM1A (Nov 2023): IQ in PWM mode, power-save rule.
- TPS6213x SLVSAG7F (Nov 2021), TPS62125 SLVSAQ5E (May 2017), TPS6217x SLVSB35C (Jul 2015), TPS7A25 SBVS372C
  (Dec 2022), TPS63802 SLVSEU9D (Jan 2021): input range, output current, power-save rule.
- SPX3819 θJA 191 K/W: [wiring-review.md](wiring-review.md) W17.
