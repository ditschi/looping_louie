# Cost estimate: manufacturing and assembly of the main board

Status: 2026-11-06 · Research 2026-11-01 to 2026-11-02 (web research, no quotes obtained, no logins/orders).
Costs for the test setup and prototype batches: [test-hardware.md](test-hardware.md).

**Exchange rate:** 1 EUR ≈ 1.13 USD → **1 USD ≈ 0.885 EUR** (Oct. 2026 between approx. 1.12 and 1.16; ±3 % goes directly
into all prices). Extra costs in USD net × 0.885 × 1.19 ≈ **USD × 1.05 = € gross**.

**Board:** 46 × 13.5 mm (6.2 cm²), **4 layers** (JLC04081H-3313), FR4 0.8 mm, trace/clearance 0.15/0.15 mm, via 0.3/0.5 mm,
green solder mask, **single-sided assembly** (top, approx. 36 placements; bottom only pads, test points and unassembled
DNP footprints). Parts: ESP32-C6-MINI-1 (-N4 or -H8), DRV8213DSG, AP2112K, USB-C J4 with ESD U5, D2, Q1,
LIS2DH12 (optional), passives 0402.

> **Legend:** **[Q]** = backed by a source (section 4 or 5.8) · **[S]** = own estimate/extrapolation.
> **(outdated, recalculate)** = number comes from the calculation for the earlier version (ESP32-C3, DRV8833, 2 layers)
> and was not fully recalculated. All final prices are [S]. A real quote (JLC calculator with Gerber + BOM +
> CPL, open-items.md F13) replaces this calculation.

---

## 1. Summary

- **Cheapest vendor: JLCPCB, Economic PCBA** (single-sided, 0.8–1.6 mm, 2/4/6 layers, up to 50 units). Assembly
  stays single-sided; the DNP parts on the bottom are not in the placement list and BOM.
- Below approx. 25 pcs, fixed costs dominate (setup, extended parts, stencil, shipping). From approx. 50 pcs the
  parts dominate (above all the ESP32-C6 module) and the **X-ray inspection of the module** (LGA, mandatory at JLC).
- **4 layers** cost only approx. +3 / +6 / +10 € per order compared with 2 layers at 5 / 10 / 30 pcs (section 5.6).
- **H8 instead of N4** costs approx. +1.8 USD per board; the H8 has been available at JLC since 2026-11-06 (620 pcs).

### Total costs in EUR incl. shipping, import VAT 19 % and customs (JLCPCB Economic, lead-free HASL) **[S]**

| Quantity | C6-**N4** total | N4 per board | C6-**H8** total | H8 per board |
|---:|---:|---:|---:|---:|
| 5   | ≈ 72–86 €   | ≈ 14–17 €   | ≈ 82–96 €   | ≈ 16–19 €   |
| 10  | ≈ 105–135 € | ≈ 10.50–13.50 € | ≈ 125–155 € | ≈ 12.50–15.50 € |
| 30  | ≈ 185–270 € | ≈ 6.20–9.00 € | ≈ 245–330 € | ≈ 8.20–11.00 € |
| 100 | ≈ 405 € (outdated, recalculate) | ≈ 4 € | ≈ 600 € (outdated, recalculate) | ≈ 6 € |

**Calculation:** The basis is the calculation of the earlier version (section 2.5: 5 / 10 / 30 / 100 pcs = 67 / 94 / 160 /
340 €), plus the 4-layer surcharge (section 5.6: +3 / +6 / +10 / +19 €) and the parts change per
[main-board-c6.md](main-board-c6.md) 7 (+0.45 USD/board with N4, +2.3 USD with H8, ≈ 0.47 € or 2.42 € gross).
This gives the **lower bound**. The **upper bound** uses the JLC unit prices at 10 pcs from
main-board-c6.md 7 for all parts (section 2.3; approx. +2.9 €/board). At 100 pcs only the lower calculation applies; tier
prices for 100+ were not collected for the C6 version. Economic PCBA takes at most 50 units: 100 pcs as a 2-up panel.

**Not included:** extra costs for global sourcing or consigned H8 modules; a sixth extended type if the
LIS2DH12 is assembled (+3.07 USD per order, section 2.2); X-ray for the DRV8213 (exposed pad, unverified).

### Other vendors (10 pcs) **[S]** (outdated, recalculate)

| Vendor | approx. total (10 pcs, earlier version) | Note |
|---|---:|---|
| JLCPCB Economic | ≈ 80–115 € | instant online price, LCSC parts stock; current version see table above |
| PCBWay | ≈ 110–170 € | assembly "from 29 USD / up to 20 pcs" (promotion) [Q], parts via DigiKey/Mouser (more expensive), quote only manual (1–2 days), DHL shipping more expensive; 4 layers approx. +20–40 USD (5.5) |
| Aisler (DE) | ≈ 300–400 € | no customs, manufacturing in DE/EU, but 75 € setup + 0.38 €/placement × pcs (older price list) [Q] → approx. 14 €/board for assembly alone; 4 layers 0.8 mm ENIG is a standard pool (5.5) |
| Eurocircuits (BE) | > 300 € (not verified) | only via online calculator with data; for small batches usually much more expensive than China |

---

## 2. Breakdown

### 2.1 PCB (JLCPCB)

Prices and rules for 4 layers: sections 5.2 and 5.4. General:

| Item | Value | Source |
|---|---|---|
| Economic PCBA allowed thickness | 0.8–1.6 mm → 0.8 mm is ok | [Q] |
| Small board (one side < 15 mm, delivered as single board) | +0.05 USD/pc | [Q] |
| Lead-free HASL | approx. +1–1.5 USD per order | [Q]/[S] |
| ENIG | approx. +16 USD for small quantities; surcharge if ENIG area > 30 % | [Q] (forum) / [S] |
| Via 0.3 mm drill | no surcharge (surcharge only below 0.3 mm) | [Q] |

**Lead-free HASL vs. ENIG:** HASL is cheaper but slightly uneven. ENIG (nickel/gold) is flat, stores better and is better
for fine pads (WSON-8 of the DRV8213, LGA pads of the module). Lead-free HASL usually works in practice for machine
assembly with a stencil. Extra cost of ENIG approx. 10–15 € per order → noticeable at 5–10 pcs, negligible at 100.

### 2.2 JLCPCB assembly fees (Economic PCBA) [Q]

| Fee | Economic |
|---|---:|
| Setup | 8.18 USD |
| Stencil | 1.53 USD |
| Extended part (per type) | 3.07 USD (Preferred Extended: 0) |
| SMT solder joint | 0.0016 USD |
| Minimum SMT amount per board/panel | 0.48 USD |
| X-ray (LGA/QFN/BGA, per part) | 1–10: 1.64 · 11–50: 0.82 · 51–200: 0.49 USD |
| Quantity | 2–50 (single boards or panels) |
| Board size | from 10 × 10 mm |
| Sides | single-sided only |
| Layers | 2, 4, 6; no fee depends on the layer count |

**Assumptions about the board [S]:**
- **Solder joints:** approx. 130–150 → approx. 0.22 USD; below the minimum of 0.48 USD → topped up for single
  boards, practically irrelevant in a 2-up/5-up panel.
- **Extended parts:** ESP32-C6, DRV8213, J4 (USB-C), D2, U5 per [main-board-c6.md](main-board-c6.md) 7 = 5 types
  → 15.35 USD per order; with LIS2DH12 6 types → 18.42 USD. AP2112K and passives Basic/Preferred depending on the LCSC number.
  Status not verified (JLC part pages do not show it without JavaScript).
- **X-ray:** for the module (JLC marks the ESP32-MINI modules as requiring X-ray [Q]). If the DRV8213 (exposed
  pad) counts as well, the tier changes – small overall effect.
- Scrap/minimum quantities of parts: flat 3–5 USD per order.

### 2.3 Parts

Unit prices at 10 pcs (LCSC/JLC, 2026-11-02) from [main-board-c6.md](main-board-c6.md) 7:

| Part | USD/pc | Status |
|---|---:|---|
| ESP32-C6-MINI-1-N4 | 3.60 | [Q] |
| ESP32-C6-MINI-1-H8 | approx. 5.4 (Mouser 4.70 €; available at JLC since 2026-11-06) | unverified |
| DRV8213DSG | 0.93 | [Q] |
| USB-C stage (J4 0.19, U5 0.05, D2 0.04, Q1 0.08, 3 R) | 0.37 | [Q] |
| LIS2DH12 + C15 (optional) | approx. 0.3 | unverified |
| AP2112K, passives 0402, LED | approx. 0.3 | [S] |
| **Total per board (10 pcs)** | **approx. 5.5 (N4) / 7.3 (H8)** | [S] |

The calculation of the earlier version assumed only approx. 2.30 USD/board for the BOM (LCSC tier prices, module
1.09 USD at 10+). The C3/C6 comparison in decision-history.md (cost change) gives 2.70 USD (JLC, 10 pcs) for the same
predecessor module. Because of this discrepancy the table in section 1 is given as a range. **Tier prices 30+/100+ for
the C6 version: (outdated, recalculate).**

### 2.4 Shipping, taxes, customs

| Item | Value | Source |
|---|---|---|
| JLC "Global Standard Direct Line" | cheapest option, only for goods value ≤ 59 USD | [Q] |
| Europacket (DDP) | example Jan. 2026: 7.90 € | [Q] |
| DHL Express | approx. 20–35 USD | [S] |
| Import VAT 19 % | on goods + shipping; up to 150 € goods value paid via IOSS when ordering, above that on import (DDP or carrier) | [Q] |
| **EU customs since 2026-07-01** | 150 € duty-free threshold abolished; flat **3 € customs per goods category** for shipments < 150 € (until 07/2028) | [Q] |
| Customs above 150 € | regular rate; for assembled PCBs typ. 0–3 % | [S] |
| Carrier clearance fee (without DDP) | 3–15 € | [Q] |

Assumed: shipping 6 / 8 / 10 / 12 / 15 € (5/10/25/50/100 pcs), plus 19 % VAT on top, plus 3 € or approx. 2 % customs. **[S]**

### 2.5 Calculation (10 pcs) [S]

Basis (earlier version, 2 layers, ESP32-C3 BOM):

| Item | USD |
|---|---:|
| Setup + stencil | 9.71 |
| 5 extended types × 3.07 | 15.35 |
| PCBs 10 pcs 2 layers incl. lead-free HASL / small-board surcharge | ≈ 5.00 |
| SMT 10 × 0.48 (minimum amount) | 4.80 |
| Parts 10 × 2.30 | 23.00 |
| X-ray module 10 × 1.64 | 16.40 |
| Scrap/MOQ buffer | 3.00 |
| **Total net** | **≈ 77 USD ≈ 68 €** |
| + shipping 8 €, × 1.19 VAT, + 3 € customs | **≈ 94 €** |

Current version: + 4 layers (PCBs ≈ 8–15 instead of 5 USD, section 5.2) ≈ +6 € · + parts C6-N4 10 × 0.45 USD
≈ +5 € (H8: 10 × 2.3 USD ≈ +24 €) → **≈ 105 € (N4) / ≈ 124 € (H8)**. With the JLC unit prices from 2.3 (10 × 5.5 or
7.3 USD instead of 10 × 2.75 or 4.6 USD) **≈ 134 € / ≈ 153 €**. Same extended count (5) as in the basis.

---

## 3. Cost drivers and savings

**Largest cost drivers (small quantities):**
1. **Extended parts** with Economic: 3.07 USD per type → 5–6 types = 15–18 USD, regardless of 5 or 50 boards.
2. **X-ray inspection of the module:** 1.64 USD/pc up to 10 pcs, then 0.82 / 0.49 USD.
3. **Module:** C6-N4 approx. 3.60 USD, H8 approx. 5.4 USD (10 pcs) – the largest item from approx. 30 pcs.
4. **Shipping/taxes:** fixed shipping costs + 19 % VAT + 3 € customs since July 2026; approx. 25 % of the total price at 5 pcs.
5. **Double-sided assembly** would force Standard PCBA (+43 USD setup, +15 USD stencil, panel with edge rails,
   practically at least 10 pcs). That is why the bottom has only pads and DNP footprints.

**Savings:**
- **Economic PCBA** – single-sided, thickness 0.8–1.6 mm, ≤ 50 units. Order 100 pcs as a **2-up panel**
  (50 panels); this also avoids the minimum SMT amount.
- **Create the panel yourself** (mouse-bite tabs, KiKit), with Economic without edge rails; JLC only charges the panel fee
  for several *different* designs. Saves the minimum SMT amount and the small-board surcharge; with 4 layers a
  5-up panel (approx. 46 × 72 mm) falls into the price band up to 100 × 100 mm (5.2).
- **Choose Basic/Preferred parts:** pick passives and possibly the LDO from the Basic or Preferred Extended list → every
  avoided extended type saves 3.07 USD.
- **Do not assemble the LIS2DH12** (DNP possible): saves approx. 0.3 USD/board and possibly one extended type.
- **N4 instead of H8** if 4 MB is enough (open-items.md F14): approx. −1.8 USD/board, and the N4 is available at JLC.
- **Lead-free HASL instead of ENIG** for small quantities (saves approx. 10–15 €).
- **Use quantity tiers:** between 10 and 30 pcs the total price rises much less than the quantity.
- **Stay below 150 € goods value** (IOSS, no post-clearance by the carrier) or choose DDP shipping.

---

## 4. Sources

Retrieved on 2026-11-01. Sources for the C6 and DRV8213 prices: [main-board-c6.md](main-board-c6.md), sources.

**JLCPCB**
- Assembly prices (setup, stencil, extended, X-ray, minimum amount): https://jlcpcb.com/help/article/pcb-assembly-price
- PCBA FAQ (panelization Economic, Preferred Extended): https://jlcpcb.com/help/article/98-pcb-assembly-faqs, https://jlcpcb.com/help/article/pcb-assembly-faqs
- Capabilities Economic vs. Standard (size, thickness, single-sided, quantity, edge rails): https://jlcpcb.com/capabilities/pcb-assembly-capabilities
- Surcharges (small boards, ENIG, drills): https://jlcpcb.com/help/article/In-what-cases-will-there-be-charged-extra
- Overview of PCBA prices (2024): https://techoverflow.net/2024/04/09/jlcpcb-pcba-assembly-price-overview/
- Saving tips: https://hwdocs.hackclub.dev/user-contrib-guides/jlc-cost-optimizing/
- Shipping to DE: https://www.eevblog.com/forum/manufacture/jlcpcb-shipping, https://www.mikrocontroller.net/topic/569557

**Parts**
- AP2112K-3.3TRG1: https://www.lcsc.com/product-image/C51118.html, https://origin-www.findchips.com/search/AP2112K-3.3TRG1

**Other vendors**
- PCBWay assembly: https://www.pcbway.com/pcb-assembly.html ; online calculator: https://www.pcbway.com/orderonline.aspx
- Aisler prices: https://community.aisler.net/t/our-simple-pricing/102 ; https://aisler.net/de
- Eurocircuits: https://www.eurocircuits.com

**Taxes/customs/exchange rate**
- EU 3 € customs from 2026-07-01: https://www.pwc.dk/en/articles-publications/2026/eu-abolishes-the-150-low-value-customs-duty-threshold-from-1-july-2026.html, https://globalimportblog.bakermckenzie.com/2026/07/02/eu-low-value-consignment-relief-abolished-and-eur-3-customs-duty-introduced-from-1-july-2026/
- EUR/USD 2026: https://www.poundsterlinglive.com/history/EUR-USD-2026

### What is verified, what is estimated?

| Verified [Q] | Estimated [S] |
|---|---|
| JLC assembly fees (setup, stencil, extended, solder joint, X-ray, minimum amount) | PCB price 4 layers for 10–100 pcs |
| JLC Economic capabilities (also 4 layers, 0.8 mm) | number of extended types (5–6) |
| Small-board surcharge | prices of passive parts, H8 price and sourcing |
| Unit prices C6-N4, DRV8213, USB-C stage at 10 pcs (main-board-c6.md 7) | tier prices of the C6 version from 30 pcs |
| EU customs rule 3 € from 07/2026 | shipping costs per quantity, customs rate above 150 € |
| Aisler fee structure (community page, possibly outdated) | PCBWay, Aisler and Eurocircuits total prices; all final totals |

Not verified: JLC Basic/Extended status of the individual LCSC numbers, current stock levels, PCBWay assembly prices
(manual quote only), Eurocircuits prices (calculator needs data), current Aisler assembly prices.

---

## 5. PCB with 4 layers (status 2026-11-02)

Decision 2026-11-03: the main board has 4 layers ([main-board-c6.md](main-board-c6.md) 11). The prices were
researched without login and without our own quote; the JLC online calculator only delivers them via JavaScript and was not
queried. **(verified)** = source read on 2026-11-02, **(unverified)** = extrapolation or forum report.

### 5.1 Short answer

- **PCB:** 4 layers cost **approx. 3–20 USD more per order** than 2 layers at JLCPCB for this small board
  (5–100 pcs), i.e. **approx. 0.2–1 € per board** (unverified).
- **Assembly:** no change. Economic PCBA is approved for 2, 4 and 6 layers and 0.8–1.6 mm; no
  assembly fee depends on the layer count (verified).
- **Lead time:** PCB fabrication 2–5 days instead of 1–2 days, i.e. **approx. 1–3 working days longer** (verified for
  1.6 mm/HASL; 0.8 mm unverified).

### 5.2 PCB alone (JLCPCB)

| Point | 4 layers | Status |
|---|---|---|
| Promo offer 5 pcs | 2 USD only up to **50 × 50 mm** (46 × 13.5 mm fits) | verified (LCSC price page, Hack Club guide) |
| Where does the 2 USD price apply? | since 2026-08-22 only in the JLCONE desktop app, no longer on the website | verified (JLC news); whether the 4-layer variant counts: unverified |
| Website price 5 pcs | "4 layers (10×10 cm) from 7 USD"; forum March 2026: 100 × 100 mm, 5 pcs = 5.92 € plus shipping | verified (JLC promo page, mikrocontroller.net) |
| Area price for larger quantities | 70.6 USD/m² board share; example 100 pcs 100 × 100 mm = 106.30 USD total (≈ 36 USD fixed share) | verified (JLC news 03/2024, since 08/2026 "standard base rate") |
| Engineering fee | for large boards (> 100 mm) up to 24 USD; low for small boards | forum 02/2026, unverified |
| Thickness 0.8 mm | allowed (0.4–2.0 mm); surcharge not documented; tolerance below 1.0 mm ±0.1 mm | allowance verified; price unverified |
| Copper | 1 oz outer, 0.5 oz inner (standard) | verified |
| Small-board surcharge (one side < 15 mm, single board) | 0.05 USD/pc | verified |
| ENIG | approx. +13–20 USD; surcharge if ENIG area > 30 % of the board | surcharge rule verified, amount unverified |
| Fabrication time (≤ 100 × 100 mm) | 5–50 pcs: 2–5 days | verified (1.6 mm, HASL) |

**Extrapolated PCB price, single boards, lead-free HASL, incl. small-board surcharge (USD, unverified):**

| Quantity | Total area | 4 layers | for comparison 2 layers (basis section 2.5) |
|---:|---:|---:|---:|
| 5   | 31 cm²  | 2 (JLCONE) / ≈ 5–7 (web) | 2 / ≈ 4 |
| 10  | 62 cm²  | ≈ 8–15  | ≈ 5 |
| 30  | 186 cm² | ≈ 15–25 | ≈ 9 |
| 100 | 621 cm² | ≈ 30–45 | ≈ 18 |

4-layer values: fixed share (engineering fee, films) plus 70.6 USD/m²; with such a small area the fixed share dominates.

**Saving tip panel:** a 5-up panel (approx. 46 × 72 mm, mouse-bite tabs, without edge rails) falls into the price band "up to
100 × 100 mm". 5 panels = 25 boards then cost about as much as 5 pcs of 100 × 100 mm (approx. 6–7 USD web, unverified).
Economic PCBA accepts panels (max. 50 units).

### 5.3 Assembly (PCBA, single-sided)

| Point | 4 layers | Status |
|---|---|---|
| Economic PCBA allowed | yes ("2, 4, 6 layers", 0.8–1.6 mm, 2–50 pcs, from 10 × 10 mm) | verified |
| Setup / stencil | 8.18 / 1.53 USD | verified |
| Extended parts, solder joints, X-ray | no layer dependency | verified |

### 5.4 Manufacturing rules at JLCPCB (1 oz)

| Rule | 4 layers (multilayer) | Design | Status |
|---|---|---|---|
| Min. trace/clearance | 0.09 / 0.09 mm | 0.15 / 0.15 mm | verified |
| Min. via (drill / ring) | 0.15 / 0.25 mm; 0.1 / 0.2 mm only at ≤ 1 mm thickness and ENIG/OSP | 0.3 / 0.5 mm | verified |
| Small drill surcharge | below 0.3 mm (per forum, with 4 layers possibly only below 0.2 mm) | 0.3 mm → no surcharge | verified / exception unverified |
| Via-in-pad (POFV, filled + plated over) | for a surcharge; free only from 6 layers | not used (unfilled vias, open-items.md A17) | verified (cost approx. 15–25 USD unverified) |
| Via to trace | 0.2 mm | – | verified |
| Clearance to board edge | ≥ 0.2 mm | – | verified |

At 0.8 mm and 4 layers the prepregs are thin; for USB 2.0 Full-Speed this is not critical. A JLC impedance stack-up for
0.8 mm/4 layers is not listed on the impedance page (unverified), but is not needed either.

### 5.5 PCBWay and Aisler (brief)

| Vendor | 4 layers | Extra cost vs. 2 layers | Status |
|---|---|---|---|
| **PCBWay** | forum reports: 4-layer prototype about twice as expensive as JLC; 120 × 60 mm, 5 pcs approx. 80 USD (2024) | for 46 × 13.5 mm approx. +20–40 USD/order | unverified |
| **Aisler** (DE, price formula job + area × quantity, min. 3 pcs) | **4 layers 0.8 mm ENIG Budget: 12 € + 0.156 €/cm²**, 125 µm trace/clearance, via 0.45 mm, 35 µm on all layers, Budget 10 days | see below | price list as of 08/2023, possibly outdated; 0.8 mm offer 10/2024 verified |

Aisler PCB price net for 6.2 cm², 4 layers 0.8 mm ENIG (extrapolation, unverified): 5 pcs ≈ 17 €, 10 pcs
≈ 22 €, 30 pcs ≈ 41 €, 100 pcs ≈ 109 €. At Aisler, 4 layers 0.8 mm is its own shared pool and therefore
comparatively cheap. Assembly at Aisler (75 € setup + placement fee, section 1) remains the big
cost block (unverified). Check Aisler rules (via 0.45 mm) against the design before ordering (open-items.md A9).

### 5.6 Extra cost of 4 layers per order and per board (JLCPCB, Economic PCBA, lead-free HASL)

Surcharge compared with the 2-layer calculation (section 2.5); included in the table in section 1.

| Quantity | Δ net USD | **Δ gross € per order** | **Δ € per board** | additional lead time |
|---:|---:|---:|---:|---|
| 5   | 0–5   | **≈ 3 €** (0–5)   | **≈ 0.60 €** (0–1.00) | +1–3 working days |
| 10  | 3–10  | **≈ 6 €** (3–10)  | **≈ 0.60 €** (0.30–1.00) | +1–3 working days |
| 30  | 6–16  | **≈ 10 €** (6–17) | **≈ 0.35 €** (0.20–0.55) | +1–3 working days |
| 100 | 12–27 | **≈ 19 €** (13–28)| **≈ 0.20 €** (0.13–0.28) | +1–3 working days |

All values unverified (no live quote). With ENIG the difference stays about the same; with the 5-up panel (5.2) it
tends to get smaller at 25–30 pcs.

### 5.7 Check before ordering

1. Load the Gerber (`just fab`) into the JLC calculator (website and JLCONE), choose stack-up JLC04081H-3313 and read off
   the real price and fabrication time for 0.8 mm/4 layers (surcharge for 0.8 mm?).
2. Check the antenna keep-out on In1/In2 in the DRC.
3. If EU manufacturing is wanted: request a quote from Aisler (4 layers 0.8 mm ENIG is a standard pool there) with the same data.

### 5.8 Sources (retrieved 2026-11-02)

- JLCPCB manufacturing capabilities (thicknesses, trace/clearance, vias, POFV, tolerances): https://jlcpcb.com/capabilities/pcb-capabilities (verified)
- JLCPCB assembly capabilities (Economic: 2/4/6 layers, 0.8–1.6 mm): https://jlcpcb.com/capabilities/pcb-assembly-capabilities (verified)
- JLCPCB assembly prices (no layer dependency): https://jlcpcb.com/help/article/pcb-assembly-price (verified)
- JLCPCB fabrication times 2 vs. 4 layers: https://jlcpcb.com/help/article/pcb-fabrication-services-and-production-time (verified)
- JLCPCB surcharges (small boards, ENIG > 30 %, drills < 0.3 mm): https://jlcpcb.com/help/article/In-what-cases-will-there-be-charged-extra (verified)
- JLCPCB 4-layer area price 70.6 USD/m², examples 100/500 pcs: https://jlcpcb.com/blog/special-discount-on-quality-4-layers-pcbs, https://jlcpcb.com/news/discount-on-quality-4-layer-pcbs (verified, as of 03/2024)
- JLCPCB price adjustment FR4 1/2/4 layers, 2026-08-03: https://jlcpcb.com/news/jlcpcb-fr4-pcb-price-adjustment-august2026 (verified, no concrete prices)
- JLCONE desktop, 2 USD offer only there (2026-08-22): https://jlcpcb.com/news/jlcpcb-jlcone-desktop-app (verified)
- "4 layers (10×10 cm) from 7 USD", coupon: https://jlcpcb.com/features/prototype-pcb-way (verified, promo page)
- 2 USD for 4 layers up to 50 × 50 mm: https://www.lcsc.com/pcba/price, https://highway.hackclub.com/guides/JLC-cost-optimizing (verified)
- Free thicknesses 0.8/1.0/1.2/1.6 mm: https://techoverflow.net/2024/11/26/what-pcb-thickness-options-are-free-of-charge-on-jlcpcb/ (not explicitly for 4 layers, unverified)
- Forum: JLC prices 2026 (4 layers 100 × 100 mm 5.92 €, engineering fee up to 24 USD): https://www.mikrocontroller.net/topic/583828 (unverified)
- Forum: JLC 4 layers 100 × 100 mm 9.55 USD, PCBWay approx. 80 USD for 120 × 60 mm (2024): https://eevblog.com/forum/manufacture/a-good-pcb-manufacture-for-hobby-pcb/msg5569241 (unverified)
- Via-in-pad free from 6 layers: https://jlcpcb.com/blog/Free-Via-in-Pad-on-6-20-Layer-PCBs-with-POFV (verified)
- PCBWay online calculator: https://www.pcbway.com/orderonline.aspx (not queried)
- Aisler price formula and table: https://community.aisler.net/t/our-simple-pricing (as of 08/2023, unverified)
- Aisler 4 layers 0.8 mm: https://community.aisler.net/t/aislers-new-0-8mm-4-layer-pcb-service/4399 (verified, 10/2024)
