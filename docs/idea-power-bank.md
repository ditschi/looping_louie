# Idea: Power from a small USB-C power bank in the base

Status: 2026-11-06 · Research; the only decision so far: **no hardware load pulse, keep-alive via firmware**
(2026-11-05, section 5). Complements [hardware-concept.md](hardware-concept.md),
[charger-board.md](charger-board.md) and [idea-usb-c-main-board.md](idea-usb-c-main-board.md).

Markers: **(verified)** = with a source or recalculated against the project files · **(unverified)** = secondary source,
memory or assumption; check on the device before a decision.

## Summary

- **Yes, there are suitably small power banks**, e.g. the Anker Nano 5000 mAh at about 76 × 36 × 25 mm for about €19–28.
  Whether it fits into the base is open: there are no published dimensions for the cavity. It has to be measured.
- **The real problem is auto shut-off**, not the size. Almost all power banks switch off below
  about 45–150 mA after 10–60 s. In deep sleep the supply is then gone, and the lever no longer wakes anything.
- **True always-on power banks** (Voltaic V25) are too large and expensive and always-on only on the USB-A port. The
  "trickle" or "low-current" modes of Anker and Xiaomi end after 2 h and are useless for standby operation.
- **Recommendation:** The power bank is a **fallback supply for play time, without standby**. In
  power bank operation the Louie does not sleep but stays on with Wi-Fi (about 100 mA, keeps the power bank awake).
  After the idle time it switches off completely. To wake it, re-plug the cable or press the power bank button.
  With a built-in LiPo (charger board) the problem does not arise at all: the power bank then only charges, and the
  LiPo handles standby.
- **Better than any power bank:** an **18650 cell in a holder in the base on the existing charger board**. It is
  1S Li-ion like the LiPo, needs no boost converter and never switches off.

---

## 1. Space in the base

| Model | Known | Source / status |
|---|---|---|
| Louie new (Hasbro, 2× AA) | whole game **26.7 × 26.7 × 9.5 cm**, about 1 kg | retailer data [Galaxus][galaxus-ll] **(verified, outer dimensions)** |
| Louie old (Milton Bradley, 1× C) | larger than the new model, open C compartment | hardware-concept.md; base dimensions **unknown** |
| Loopin' Chewie | 2× AA (assumption in the project) | no dimensions found **(unverified)** |
| Cavity under or in the base | no teardown photos with dimensions found. CDTM had to "make some room" in the old Louie for a 9 V block (48 × 26 × 17 mm) | [CDTM][cdtm] **(unverified, qualitative only)** |

**Assumptions (unverified, measure on the game):**

- The project already plans a **1S LiPo with 1000–2000 mAh in the base** (hardware-concept.md 5.4). A flat
  pouch battery of this size is about 50 × 34 × 8 mm to 60 × 40 × 10 mm. At least this much space is therefore
  assumed.
- A **power bank with 5000 mAh is 3 to 5 times as large** (about 65–70 cm³). Whether the base has a chamber of
  about 80 × 40 × 26 mm that is not occupied by the motor, the gearbox or the screw bosses is **open**.
- Fallback without space: the power bank lies **next to the game**, and the cable runs through the hole of the
  base holder (13.5 × 7.5 mm, charger-board.md 4B) or from above into the compartment.

New open item **P1**: open the base, measure free chambers (L × W × H), photos in `docs/images/`.

## 2. Candidates (small power banks with USB-C)

| Model | Capacity | Dimensions (mm) | Output | Price DE/EU | Low-current / always-on | Source |
|---|---|---|---|---|---|---|
| **Anker Nano Power Bank 22.5 W** (A1653, foldable plug) | 5000 mAh | 76 × 35.5 × 25.4, 100 g | USB-C socket + plug, 5 V/3 A | about €19 (Amazon deal) to €28 (MediaMarkt AT) | trickle mode (double press, **max. 2 h**). Whether exactly this model has it is **unverified** | [Galaxus][anker-dim], [GIGA][giga], [MediaMarkt][mm-anker], [Anker FAQ][anker-trickle] |
| Forcell F-Energy Mini Power Watch | 1200 mAh | 70.5 × 40 × 15.9, 48 g | fixed USB-C cable | about €10–15 **(unverified)** | not known | [MediaMarkt AT][forcell] |
| INIU keychain power bank | up to 5000 mAh **(unverified)** | about 80 × 38 × 29 | USB-C | about €12 (deal) | not known | [china-gadgets][iniu] |
| Typical "lipstick" power bank (1× 18650) | 2600–3350 mAh | about Ø 22–25 × 90–100 | often USB-A only **(unverified)** | €8–15 | rarely | – |
| **Voltaic V25** | 6700 mAh | 80 × 82 × 24, 230 g | 2× USB-A (always-on), USB-C PD (**not** always-on) | $45 (≈ €50–55 in EU shops) | **yes**, USB-A only, self-consumption about 7 mA | [Voltaic][v25] **(verified)** |
| Voltaic V15 | 4000 mAh | 102 × 65 × 16 | USB-A 1 A | being discontinued | yes | [Modern Outpost][v15] |
| Xiaomi power banks (various) | – | – | – | – | low-current mode via double press, **ends after 2 h** | [Xiaomi FAQ][xiaomi] |

Current: the motor draws up to about 1 A peak; the DRV8213 limits to 2 A (ITRIP). A USB-C source with 5 V/3 A is enough.
Small 1000 mAh keychain banks often deliver only 1–1.5 A. Their overcurrent protection can trip at start-up; the
firmware ramps (hardware-concept.md 5.1) help against this **(unverified)**.

## 3. Core problem: auto shut-off

Typical thresholds: **IP5306 below 45 mA for 32 s** [datasheet summary][ip5306] **(verified)**. Other
power banks switch off below 50–200 mA, measured e.g. 150 mA [0110.be][0110] or 100 mA after about 10 s (Voltcraft)
[ESP32_KeepPowerbankAlive][kpa]. Whether a USB-C port with a 5.1 k resistor attached (Rd: main board R12/R13 on J4, charger board R101/R102)
stays on longer depends on the manufacturer. You cannot rely on it **(unverified)**.

Consumption of the Louie at 5 V: through the buck converter (U3, main-board-c6.md 2.7) the input current is roughly
the 3.3 V current × 3.3 V / (5 V × η), about 0.75 × the 3.3 V current at η ≈ 0.9 (unverified). The figures below are
3.3 V-side currents (with the earlier LDO input and output current were equal), so the power bank sees somewhat less.

| State | Current | Power bank stays on? |
|---|---|---|
| Wi-Fi connected, modem sleep off (`WIFI_PS_NONE`) | about 80–120 mA | mostly yes, just above the threshold **(unverified)** |
| Wi-Fi with modem sleep (default) | average about 20–40 mA | **no**, off after 10–60 s |
| Light sleep, Wi-Fi off | about 0.5–2 mA | no |
| Deep sleep | µA | no |

### Solutions compared

| Solution | How | Energy (power bank 5000 mAh ≈ 15 Wh usable at 5 V) | Effort | Rating |
|---|---|---|---|---|
| **A: Always-on power bank** | Voltaic V25 via USB-A → C cable | self-consumption 7 mA → about 3 weeks standby | none | ✓ technically clean, ✗ 80 × 82 mm, 230 g, about €50. Probably does not fit into the base |
| **B: Trickle/low-current mode** (Anker, Xiaomi) | double press | – | none | ✗ ends after 2 h, useless as standby |
| **C: Base-load pulse in hardware** | MOSFET + 47 Ω on VBUS, 555/RC clock, e.g. **100 mA for 50 ms every 8–9 s** (pattern from [ESP32_KeepPowerbankAlive][kpa], ready-made modules: [Pi Hut KeepAlive][pihut], about 100 mA at 50 % duty cycle, which is wasteful) | pulse: 100 mA × 50 ms / 9 s ≈ 0.6 mA → 3 mW. Plus power bank idle consumption, estimate 1–5 mA from the cell **(unverified)** → about 2–6 weeks | about 6 components on the **charger board** (only active when VBUS is present). Not planned on the main board (decision 2026-11-05, section 5) | ○ works with most power banks, tune the timing per model. Some average over longer windows |
| **D: Pulse via firmware** | light sleep, wake by timer about every 8 s and turn Wi-Fi/RF on for 0.2–0.5 s (80–120 mA) | average about 3–5 mA → about 4–6 days standby | firmware only | ○ testable without hardware. Whether such a short pulse keeps the power bank awake is **unverified** and model-dependent |
| **E: No sleep on USB** | on USB keep Wi-Fi connected, `WIFI_PS_NONE` | about 0.5 W → about 30 h | firmware only | ✓ ideal for a game night, ✗ no standby over days |
| **F: Accept the shut-off** | idle time → deep sleep → power bank off. Wake: press the power bank button or re-plug the cable | 0 | none | ✓ honest and simple. The lever then does not wake; the web UI has to explain this |
| Motor as load | – | – | – | ✗ does not work: with the lever "off" the motor circuit is open |

## 4. Alternatives without a ready-made power bank

| Alternative | Voltage | Rating |
|---|---|---|
| **18650 (or large LiPo) in a holder on the charger board** | 3.0–4.2 V directly on VSYS | ✓ **best solution**: no converter, no shut-off, charging via the existing USB-C socket. 18650: Ø 18 × 65 mm, about 2500–3500 mAh, holder about 77 × 21 × 19 mm **(unverified)** |
| Power bank module (IP5306) + 18650 | 5 V | ✗ The IP5306 has the same shut-off (45 mA/32 s). Only modules with "HOLD" or a bridged button stay on **(unverified)**. Double conversion 3.7 → 5 → 3.3 V wastes about 10–15 % |
| 2× AA + boost to 5 V | 5 V | ✗ The compartment is occupied by board A. No advantage over 1S Li-ion |
| **14500 Li-ion with USB-C charging socket** (e.g. Acebeam ARC14500-920, Nextorch 880 mAh, JetBeam JR145) | 3.7 V (no 1.5 V regulator!) | ○ unlike I1 (1.5 V cells, rejected) the voltage fits **without a converter**. But: only about 3 Wh. The compartments are connected via the motor circuit, so rewiring would be needed (compartment 2 becomes supply instead of bridge). Protected cells are often 52–53 mm long instead of 50.5 mm **(unverified)**. They must be removed for charging. [Battery Junction][bj14500] |

## 5. Recommendation

| Rank | Type | Dimensions | Price | Always-on | Needed |
|---|---|---|---|---|---|
| 1 | **18650 in a holder on the charger board** (instead of a power bank) | about 77 × 21 × 19 mm | about €8–12 (cell + holder) **(unverified)** | yes | nothing new, battery connection J102/TP101 |
| 2 | **Anker Nano 5000 mAh** as fallback via C-to-C cable | 76 × 35.5 × 25.4 mm | about €19–28 | no (trickle max. 2 h) | firmware: solution E + F |
| 3 | Voltaic V25, if true standby with a power bank is mandatory | 80 × 82 × 24 mm | about $45 | yes (USB-A) | USB-A-to-C cable, space outside the base |

**Firmware:**

- USB detection: USB-C on the main board (J4) via **VBUS_DET (IO4)**, which also wakes on plug-in
  (main-board-c6.md 2.3). USB on the charger board via the VSYS measurement (VBAT_ADC): **VSYS > 4.4 V ⇒
  "powered via USB"** (charger-board.md: VSYS ≈ 4.6 V via the Schottky diode).
- On USB: `WIFI_PS_NONE`, no deep sleep. After the idle time **deep sleep with a notice** that the lever does not wake
  in power bank operation.
- If a LiPo is present (VSYS drops only to battery voltage on unplugging), the normal flow applies. The power bank
  switching off is then harmless.
- Motor setpoint `duty = U_soll / VSYS`; at 5 V a smaller duty cycle results automatically.
- Solution D (timer wake plus radio burst) as setting "keep power bank awake"; test and note per model
  whether it works (P3).

**Hardware:** nothing for rank 1 and 2.

**Decision 2026-11-05: no hardware load pulse on the main board.** The firmware handles keep-alive:
timer wake plus short radio burst (solution D). Reasons:
- 47 Ω at 5 V draws about 105 mA; a Wi-Fi burst of the C6 draws about 80–120 mA. For the power bank's shut-off detection
  this is the same stimulus, just without an extra component (unverified per model, P3).
- Using the motor as a load via PWM does not work: the lever disconnects the motor circuit at rest.
- A cell in a holder on BAT_IN (3.0–4.2 V, already covered by the power path 3.0–6.6 V) never sleeps; it is the
  safe solution if the power bank switches off despite the radio burst.

IO22 stays free (reserve). Solution C on the charger board remains an idea. The DNP load pulse formerly planned
on the main board: see [decision-history.md](decision-history.md).

**Web UI ([web-ui-concept.md](web-ui-concept.md)):**

- Status display **"powered via USB"** instead of battery percent. The power bank charge level cannot be read.
- Whether a LiPo is being charged or a power bank without battery is supplying cannot be distinguished from VSYS alone. So
  keep the display neutral ("USB") or ask "battery installed: yes/no" in the settings.
- Without battery: show a notice before sleeping: "Louie is switching off. To wake it, press the power bank button or
  re-plug the cable. The lever does not wake it in power bank operation."
- If VSYS collapses during a round (power bank off or empty), the next start shows a status card
  "power interrupted" (reset reason brownout).

## 6. Open items

| # | Item | Proposal |
|---|---|---|
| P1 | Free chambers in the base (all three models) | open the base, measure, photograph |
| P2 | Does the Anker Nano hold at 80–120 mA permanently? Does the C port stay on with Rd? | test with a USB meter |
| P3 | Does a firmware pulse (solution D: timer wake + radio burst) keep the power bank awake? | try with 2–3 power banks; otherwise cell on BAT_IN |
| P4 | Motor start-up on small 1 A power banks | test overcurrent shut-off |

## Sources

- [galaxus-ll]: https://galaxus.de/en/s5/product/hasbro-gaming-looping-louie-german-board-games-288540
- [cdtm]: https://cdtm.com/blog/creating-circling-centerling-looping-louie-modding
- [anker-dim]: https://www.galaxus.nl/en/s1/product/anker-nano-5000-mah-18-w-50-wh-powerbanks-42820321
- [giga]: https://www.giga.de/tech/amazon-verkauft-kompakte-nano-powerbank-zum-spitzenpreis--01J69M6MSR4V71FC40ABBXMWQE
- [mm-anker]: https://www.mediamarkt.at/de/product/_anker-nano-powerbank-5000-mah-usb-c-schwarz-2063924.html
- [anker-trickle]: https://service.anker.com/eu/article-description/What-is-Trickle-Charging-Mode
- [forcell]: https://www.mediamarkt.at/de/product/_forcell-f-energy-mini-power-watch-1200mah-powerbank-1200mah-schwarz-139492849.html
- [iniu]: https://www.china-gadgets.de/iniu-5-000-mah-powerbank-schluesselbund-kabel-ueberfluessig/
- [v25]: https://voltaicsystems.com/V25
- [v15]: https://www.modernoutpost.com/product/voltaic-v15/
- [xiaomi]: https://www.mi.com/global/support/faq/details/KA-301691/
- [ip5306]: https://industrialmonitordirect.com/blogs/knowledgebase/ip5306-shuts-down-after-33-seconds-load-detection-fix
- [0110]: https://0110.be/posts/Powering_low_current_electronics_projects_with_power_banks
- [kpa]: https://www.github.com/Staubgeborener/ESP32_KeepPowerbankAlive
- [pihut]: https://thepihut.com/products/power-bank-keepalive-usb-c
- [bj14500]: https://www.batteryjunction.com/products/jetbeam-jr145

[galaxus-ll]: https://galaxus.de/en/s5/product/hasbro-gaming-looping-louie-german-board-games-288540
[cdtm]: https://cdtm.com/blog/creating-circling-centerling-looping-louie-modding
[anker-dim]: https://www.galaxus.nl/en/s1/product/anker-nano-5000-mah-18-w-50-wh-powerbanks-42820321
[giga]: https://www.giga.de/tech/amazon-verkauft-kompakte-nano-powerbank-zum-spitzenpreis--01J69M6MSR4V71FC40ABBXMWQE
[mm-anker]: https://www.mediamarkt.at/de/product/_anker-nano-powerbank-5000-mah-usb-c-schwarz-2063924.html
[anker-trickle]: https://service.anker.com/eu/article-description/What-is-Trickle-Charging-Mode
[forcell]: https://www.mediamarkt.at/de/product/_forcell-f-energy-mini-power-watch-1200mah-powerbank-1200mah-schwarz-139492849.html
[iniu]: https://www.china-gadgets.de/iniu-5-000-mah-powerbank-schluesselbund-kabel-ueberfluessig/
[v25]: https://voltaicsystems.com/V25
[v15]: https://www.modernoutpost.com/product/voltaic-v15/
[xiaomi]: https://www.mi.com/global/support/faq/details/KA-301691/
[ip5306]: https://industrialmonitordirect.com/blogs/knowledgebase/ip5306-shuts-down-after-33-seconds-load-detection-fix
[0110]: https://0110.be/posts/Powering_low_current_electronics_projects_with_power_banks
[kpa]: https://www.github.com/Staubgeborener/ESP32_KeepPowerbankAlive
[pihut]: https://thepihut.com/products/power-bank-keepalive-usb-c
[bj14500]: https://www.batteryjunction.com/products/jetbeam-jr145
