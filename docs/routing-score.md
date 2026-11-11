# Rating routing quality: hard constraints + weighted score

Status 2026-11-04. **Implemented** (weights from section 3 confirmed by the client): `hardware/scripts/route_score.py`
(measurement, `evaluate()`, `decide()`, report), configuration `hardware/routing-score.toml`, built into
`route_gate.py` (gate, `just score`, `just explain`) and `route.py` (best attempt of one call). Usage:
[development.md](development.md), section "Routing: keep the best result". Sections 1–4 describe the rules in
force; sections 5 and 8 are the prototype measurement from 2026-11-03 (history, before the board was reworked).

**Deviations of the implementation from the proposal:**
- `tight_clearance` counts the items involved (tracks, vias, pads), not the reported pairs. Which pairs
  kicad-cli 9.0.8 reports varies by ±2 % from run to run on the same board (228–232); the items do not (275).
  Scale unchanged at 10.
- Board knowledge (nets, antenna, via-in-pad list, module, current paths) lives under `[boards.<board>]`; the
  general sections are defaults. `thermal_vias_u2` is called `thermal_vias` (pad from `[boards.*.module]`).
- `routing.json` additionally stores `details` and `score.parts`; `ranking` is dropped (`"decision": "hard+weighted"`).
- Findings 8.1 (VSYS path too narrow) and 8.3 (net classes) are fixed: `gen_main_pcb.py` pre-routes Q1 → C1/C2 at 0.5 mm
  on the outer layers only, `route_fix.py` never routes VSYS below 0.3 mm, and the net classes are set again on
  generation (main-board-c6.md 11.7).

**Check of the implementation (2026-11-04, board before the rework):** `just score main-board
build/main-board/keep/variant4-0-open.kicad_pcb` → as in the prototype, the official board wins: both violate
`power_width_violations`, violation 1/10.0 mm vs 1/23.0 mm → REJECT; soft ΔS = +3.77 for variant4 (with the
new `tight_clearance` count; prototype +3.07), robustness 0.5 % "accept". A byte-identical state
(`best-0-open`) gives ΔS = 0.00.

## Summary

- **Today** the gate compares lexicographically (`drc_violations`, `unconnected`, `gnd_islands`, `via_count`,
  `track_length_mm`). The first metric that differs decides on its own. One GND island therefore counts
  for more than any number of vias and millimetres. There is no metric at all for current paths, sense lines,
  antenna or return path.
- **Proposal:** three stages.
  1. **Hard constraints** (DRC errors, unconnected items, copper in the antenna keep-out area, current paths
     too narrow). A board that violates them is infeasible. If both boards are infeasible, the smaller
     violation wins (Deb's rule).
  2. **Weighted sum** of the soft metrics: `S = Σ weight_i · value_i / scale_i`.
     - `scale` defines the size at which a difference counts as "one point" (fixed, in units).
     - `weight` is the importance and is set by the user.
  3. **Threshold and veto.** A candidate replaces the official board only if it is better by at least
     `min_improvement` points (default 1.0). In addition, individual critical metrics must not get worse
     by more than `max_regression`.
  - Every run writes a **sensitivity report**: contribution per metric, share, "flip factor" of the weight,
    robustness against random weights and a Pareto view.
- **Feasible:** All proposed metrics can be computed automatically with `kicad-cli pcb drc` (JSON) and `pcbnew`
  (KiCad 9.0.8). The measurement takes **3.5 s per board**, including two DRC runs.
- **Result 4 layers:** The official board (attempt 3) wins against `variant4-0-open`.
  - Its violation of the hard constraint is smaller: 10 instead of 23 mm of too-narrow track in the battery–motor path.
  - It is also better in the soft score: ΔS = +3.07 for variant4. Variant4 leads to longer sense lines,
    more vias and more length; against that stands 1 GND island fewer.
  - Robust: in 98.9 % of 2000 random weight sets (each weight ×0.5 to ×2) the official board stays
    ahead.
  - **Today's lexicographic gate would have picked variant4** (GND islands 1 < 2).
- **Side finding (important, both 4-layer states):**
  - The battery current to the motor (Q1 → VSYS → DRV8213 VM) runs over tracks of **0.2–0.3 mm**, partly on
    In2 (0.5 oz).
  - Cause: `route_fix.py` routes VSYS with `WIDTHS["/VSYS"] = (0.3, 0.2)`.
  - At 2 A that is 56 mV (official) or 89 mV (variant4) of voltage drop. According to IPC-2221 the path carries
    far less than 1.5 A continuous current.
  - The 2-layer board (Freerouting, net class Power 0.4 mm) does not have the problem. Section 8.

## 1. Why not lexicographic?

| | Lexicographic (today) | Hard constraints + weighted sum |
|---|---|---|
| Trade-off between goals | none: 1 island fewer beats +8 vias, +36 mm, +19 mm sense line | explicit, via weights |
| New metrics | any new metric at the end practically never has an effect | each acts according to its weight |
| Traceable | very (one metric decides) | equally, with the contribution table |
| Noise | tiny differences (1 via, 0.1 mm) replace the board | threshold `min_improvement` |
| Risk | important properties (current path, antenna) are missing entirely | compensation: many small gains hide real damage → hard constraints + veto |
| Tuning | order | weights (scales stay fixed) |

**Lexicographic remains right for the hard constraints.** What must never happen is not traded off
against anything else. That is why the hard constraints apply first and the sum only among the feasible
boards. This matches Deb's (2000) feasibility rules from constrained optimization:
- feasible beats infeasible;
- of two infeasible ones, the one with the smaller total violation wins;
- of two feasible ones, the better objective value wins.

Freerouting works similarly internally. The router score deducts points for unconnected items and
clearance violations. The optimizer weights extra length (1000), extra vias (2000) and bends (500) against
lower bounds. It accepts no step that loses connections or creates DRC errors, and stops as soon as a step
gains less than 1 %.

### Normalization: fixed scales instead of ratio to the baseline

- **Ratio to the official board** (`value/value_official`):
  - With a baseline of 0 (GND islands, return gaps on 4 layers) it is undefined.
  - Every new official board shifts the meaning of all weights.
  - Rejected.
- **Fixed scale** (`value/scale`): `scale` says how much of a quantity is roughly equally bad.
  - Default values: 10 signal vias ≈ 50 mm signal track ≈ 1 GND island ≈ 5 mm sense line next to the motor ≈ 20 mV
    drop.
  - Weights stay comparable across many runs. Chosen.
- The report still shows the percentage change relative to the baseline, so the magnitudes are easier to
  picture.

### A single metric is prevented from dominating by

1. **scales** that describe a "noticeable difference" (not 1 mm, not 1 via);
2. **deciding on ΔS** relative to the official board instead of the absolute S. Constant parts such as the
   230 fine-pitch tight spots of the pre-routes cancel out this way.
3. the **share** column in the report. If one metric stays above about 50 %, its scale was chosen
   too small.
4. a **veto** (`max_regression`) for antenna, current path and sense lines. These cannot be "bought off" by many
   small gains elsewhere.

### Ties and noise

- The measurement is deterministic: same state, same numbers. Scatter only comes from routing (11.4 in
  main-board-c6.md).
- The threshold `min_improvement = 1.0` point prevents a practically equivalent run from replacing the checked-in
  board. This keeps the Git history quiet and protects a board that was checked in the GUI.
- With |ΔS| < 1.0 the official board stays; there is no further tie-break.
- At the default weights, 1.0 point corresponds e.g. to 5 signal vias, 50 mm signal track or 1/3 GND island.

### Pareto view

For all runs of one call and the official board, the report checks whether another one is at least equal in
**all** soft metrics and better in one ("dominated").
- Non-dominated runs are genuine trade-offs. Only there do the weights decide.
- The winner of a weighted sum with positive weights is always Pareto-optimal.
- Conversely, a weighted sum does not find every trade-off: it cannot reach points in non-convex parts of the
  front (Das & Dennis 1997). That is why the report also lists the non-dominated runs, and one of them can be
  adopted by hand (`force=1`).
- In the prototype all three boards are non-dominated. Each is better somewhere, so the weights are needed.

### Sensitivity

For each metric the report outputs:
- **points** `weight·(new − old)/scale` and **share** of the sum of absolute values;
- **flip factor**: by which factor would the weight of this one metric have to be multiplied for the
  decision to flip? Example: "gnd_islands ×2.36" means that with weight 7.1 instead of 3, variant4 would have won.
  "-" means this metric alone cannot flip the decision.
- **robustness**: share of 2000 random weight sets (each weight log-uniformly ×0.5 to ×2)
  for which the candidate would be accepted. Below about 10 % or above 90 % the decision is stable.

## 2. Metrics

Computed with `kicad-cli pcb drc --format json --severity-all` (schema `drc.v1.json`) and `pcbnew`
(KiCad 9, SWIG). The zones are refilled in memory (`ZONE_FILLER`); the file stays unchanged.
Column **Type**: H = hard (limit), S = soft (weight/scale), I = information only.

| Metric (`key`) | Definition, computation | Unit | Type | Scale | Weight | Reason for weight |
|---|---|---|---|---:|---:|---|
| `drc_errors` | DRC violations with severity *error*, without library check (as today) | count | H ≤ 0 | – | – | not manufacturable/testable |
| `unconnected` | `unconnected_items` of the DRC | count | H ≤ 0 | – | – | function |
| `antenna_intrusions` | track/via pieces of other nets in a keep-out area `Antenna*` (on its layers), plus zone fill inside it > 0.01 mm²; allowed: `OUT_A` (edge strip to BT1) | count | H ≤ 0 | – | – | Espressif: no copper under the antenna on any layer |
| `power_width_violations` | For each defined current path (pad → pad, table 3) the lowest-resistance route through tracks/vias (Dijkstra). Violation if more than `neckdown_allow_mm` = 2 mm of track is narrower than IPC-2221 requires for `current_a` at 20 K, or if the drop at `peak_a` exceeds the path's optional `max_drop_mv` | count of paths | H ≤ 0 | – | – | heating, motor current up to 2 A (IPROPI limit) |
| `drc_warnings` | remaining DRC messages (dangling tracks/vias, silk …) | count | S | 1 | 2 | each one is rework |
| `gnd_islands` | GND fill fragments without via/through-hole pad (as today) | count | S | 1 | 3 | attached only to SMD pads/tracks, weak ground |
| `signal_vias` | vias other than GND | count | S | 10 | 2 | layer change = antipad in L2, space, inductance. **GND vias are not penalized** (today they are included in `via_count`) |
| `signal_length_mm` | track length other than GND | mm | S | 50 | 1 | detours, coupling, area |
| `detour_worst5` | mean of the 5 worst nets: routed length / octilinear minimum spanning tree of the pads (45° distance `max+0.414·min`) | ratio | S | 0.5 | 1 | finds single crazy detours that get lost in the total length |
| `bends` | direction changes between tracks of the same net/same layer (except GND) | count | S | 50 | 0.5 | looks, manual rework, little electrical effect |
| `acute_angles` | same-net junctions below 90° | count | S | 1 | 1 | acid traps |
| `overlapping_segments` | same-net tracks running back over each other (angle ≈ 0°) | count | S | 1 | 0.5 | router leftover, clean-up |
| `via_in_pad` | via in an SMD pad, except list (`U1:*` module GND, `U2:*` thermal pad) | count | S | 1 | 2 | solder is wicked away, no filled via ordered |
| `tight_clearance` | second DRC with an extra rule "clearance ≥ clearance + 0.05 mm" for track/via/pad (not zone, not pad–pad); number of violations | count | S | 10 | 1 | manufacturing margin; constant parts (fine-pitch pre-routes) cancel out in ΔS |
| `power_drop_mv` | largest voltage drop of the current paths at `peak_a`: Σ ρ·L/(w·t) per track (t from the layer stack-up) + via barrel (20 µm) | mV | S, veto +30 | 20 | 2 | motor power, brown-out at start-up |
| `sense_coupling_mm` | length of the sense nets (ISEN, ISEN_ADC, VBAT_ADC) that lies closer than 0.6 mm (edge to edge) to OUT_A/OUT_B, on the same layer or on layers without a GND plane in between | mm | S, veto +5 | 5 | 3 | PWM edges couple into the ADC/IPROPI line |
| `sense_length_mm` | total length of the sense nets | mm | S | 10 | 1 | antenna for interference, IPROPI node is high-impedance |
| `return_gap_mm` | length of signal tracks without GND beneath them. With a plane: the fill of the nearest plane (4 layers: In1) must lie under the point. Without a plane (2 layers): adjacent layer. The track's own via antipad does not count | mm | S | 2 | 3 | return path, EMC, USB |
| `antenna_proximity_mm` | signal track (not GND, not allowed) within 2 mm of the antenna keep-out areas | mm | S, veto +3 | 5 | 2 | detuning of/coupling into the antenna |
| `stitch_gap_p95_mm` | 95th percentile of the distance from outer-layer GND fill (0.25 mm grid) to the nearest GND via/through-hole pad | mm | S | 1 | 1 | fill tongues without connection (resonance, return current) |
| `gnd_vias_module` | GND vias within 1 mm of the module | count | S (−) | 4 | −0.5 | Espressif: many GND vias at the module; negative = more is better |
| `usb_vias` | vias on USB_D+/D− | count | S | 2 | 1 | layer change within the pair |
| `usb_skew_mm` | length difference D+/D− | mm | S | 5 | 0.5 | Full Speed (4–20 ns edges) uncritical, Espressif still asks for equal length |
| `usb_stubs` | open track ends on D+/D− (not at pad/via/track) | count | S | 1 | 1 | keep ESD routed through (section 10) |
| `ref_plane_mm2` | area of the GND plane (In1) | mm² | I | 10 | 0 | correlates with `signal_vias` (antipads) |
| `thermal_vias_u2`, `gnd_vias`, `via_count`, `track_length_mm`, `detour_total`, `stitch_gap_max_mm`, `layer_length_mm`, `usb_len_*` | for information and for comparison with today | – | I | – | 0 | – |

**Not included:**
- **Impedance:** USB FS is pre-routed. It would only make sense with a field solver.
- **Silk:** silk messages go through `drc_warnings`.
- **USB parallel run:** the pair is pre-routed and identical in all runs.
- **DRV8213 thermals via copper area:** the generator fixes the thermal vias. `thermal_vias_u2` is in the
  report for information only.

## 3. Configuration file (proposal `hardware/routing-score.toml`)

English keys. The user normally only changes `weight` (and `min_improvement`). `scale` and the
board part only change when the design changes.

```toml
version = 1

[decision]
min_improvement = 1.0   # points; ~5 signal vias or 50 mm signal track

[hard]                  # metric = maximum allowed value
drc_errors = 0
unconnected = 0
antenna_intrusions = 0
power_width_violations = 0

# weight: importance (0 = report only, 1 normal, 3 important, 5 critical, negative = more is better)
# scale:  this much of the quantity counts as one point (before weighting)
# max_regression: optional veto relative to the official board
[soft]
drc_warnings         = { weight = 2.0,  scale = 1 }
gnd_islands          = { weight = 3.0,  scale = 1 }
signal_vias          = { weight = 2.0,  scale = 10 }
signal_length_mm     = { weight = 1.0,  scale = 50 }
detour_worst5        = { weight = 1.0,  scale = 0.5 }
bends                = { weight = 0.5,  scale = 50 }
acute_angles         = { weight = 1.0,  scale = 1 }
overlapping_segments = { weight = 0.5,  scale = 1 }
via_in_pad           = { weight = 2.0,  scale = 1 }
tight_clearance      = { weight = 1.0,  scale = 10 }
power_drop_mv        = { weight = 2.0,  scale = 20, max_regression = 30 }
sense_coupling_mm    = { weight = 3.0,  scale = 5,  max_regression = 5 }
sense_length_mm      = { weight = 1.0,  scale = 10 }
return_gap_mm        = { weight = 3.0,  scale = 2 }
antenna_proximity_mm = { weight = 2.0,  scale = 5,  max_regression = 3 }
stitch_gap_p95_mm    = { weight = 1.0,  scale = 1 }
gnd_vias_module      = { weight = -0.5, scale = 4 }
usb_vias             = { weight = 1.0,  scale = 2 }
usb_skew_mm          = { weight = 0.5,  scale = 5 }
usb_stubs            = { weight = 1.0,  scale = 1 }
ref_plane_mm2        = { weight = 0.0,  scale = 10 }

[nets]
gnd = "/GND"
power = ["/VSYS", "/BAT_IN", "/VBUS_J4", "/OUT_A", "/OUT_B", "/+3V3"]
sense = ["/ISEN", "/ISEN_ADC", "/VBAT_ADC"]
aggressors = ["/OUT_A", "/OUT_B"]
usb_pair = ["/USB_D+", "/USB_D-"]
coupling_gap_mm = 0.6
clearance_margin_mm = 0.05

[antenna]
area_prefix = "Antenna"
allowed_nets = ["/OUT_A"]
margin_mm = 2.0

[via_in_pad]
allowed = ["U2:*", "U1:*"]

[thermal]
copper_rise_k = 20
ipc_k_external = 0.048
ipc_k_internal = 0.024      # IPC-2221 conservative; IPC-2152 data allow about 0.048
neckdown_allow_mm = 2.0     # stubs at fine-pitch pins (DRV8213 0.3 mm)
resistivity_ohm_m = 1.72e-8
via_plating_um = 20

[[paths]]                   # current_a: continuous current (width), peak_a: peak (drop)
name = "OUT_A U2 -> BT1"
from = "U2:2"
to = "BT1:1"
current_a = 1.5
peak_a = 2.0
# likewise: OUT_B U2:3 -> BT2:1, VSYS D2:1 -> U2:1, VBUS J4:A4 -> D2:2, BAT J5:1 -> Q1:3, VSYS Q1:2 -> U2:1

[[paths]]                   # since 2026-11-11: 3V3 from the LDO to the module, with a drop limit
name = "3V3 U3 -> U1 3V3"
from = "U3:1"
to = "U1:3"
current_a = 0.15
peak_a = 0.38
max_drop_mv = 50            # hard: counts as power_width_violations
```

**Current paths:** 1.5 A continuous current at 20 K requires at least **0.35 mm** on the outside (35 µm) according to
IPC-2221. Inside (15.2 µm) it is 2.07 mm with k = 0.024 or 0.80 mm with k = 0.048. **So motor current belongs on the
outer layers.** The 2 A is the IPROPI current limit (R1 1.24 k). Continuous current and heating have not been
measured (uncertain): only a current measurement at the motor (hardware-concept.md, open items) will provide
reliable values for `current_a`.

**3V3 path (since 2026-11-11):** a complete, DRC-clean run of rev B had connected the module side of +3V3 through a
40 mm detour around the USB end (75 mV at 380 mA in this model). The path U3 → module pad 3 now has a hard limit of
50 mV at the TX peak; the current board has 14.6 mV (38 mΩ, main-board-c6.md 11.4).

## 4. Report

`route_gate.py` outputs the following for every decision (example from the prototype):

```
board           hard under_mm        S      dS  lexicographic(old gate)
4l-official        1     10.0    96.19   +0.00  (0, 0, 2, 116, 640.16)   hard: power_width_violations
4l-variant4        1     23.0    99.26   +3.07  (0, 0, 1, 124, 676.33)   hard: power_width_violations

=== 4l-variant4 vs 4l-official: REJECT (both infeasible, violation 1/23.0 mm vs 1/10.0 mm)
  metric                     official  candidate   points   share  flip-factor
  gnd_islands                       2          1    -3.00    23%  x2.36
  sense_length_mm               45.41      64.59    +1.92    15%  -
  tight_clearance                 230        245    +1.50    12%  -
  return_gap_mm                   0.3       1.08    +1.17     9%  -
  acute_angles                      3          4    +1.00     8%  -
  overlapping_segments             10          8    -1.00     8%  x5.07
  signal_vias                      70         74    +0.80     6%  -
  power_drop_mv                  81.6       88.8    +0.72     6%  -
  signal_length_mm              606.4      632.3    +0.52     4%  -
  gnd_vias_module                  26         30    -0.50     4%  x9.14
  detour_worst5                 2.021      2.217    +0.39     3%  -
  sense_coupling_mm              1.67       1.16    -0.31     2%  x14.31
  bends                           252        237    -0.15     1%  x28.15
  stitch_gap_p95_mm              3.29        3.3    +0.01     0%  -
  sum                                               +3.07
  robustness: soft decision 'accept' in 1.1 % of 2000 random weight sets (x0.5..x2)

Pareto (soft metrics with weight != 0):
  4l-official    non-dominated
  4l-variant4    non-dominated
```

The short line in the log stays as today, for example:
`New run: S 99.3 (+3.1), hard 1 → rejected (larger violation power_width; main drivers gnd_islands −3.0 / sense_length +1.9)`.

## 5. Prototype results (2026-11-03)

Three boards were measured:
- **2 layers:** commit c45c6de;
- **4 layers official:** now `hardware/main-board/louie-main.kicad_pcb`, identical in content to the former
  `main-board-4l`;
- **4 layers variant4:** `build/main-board-4l/keep/variant4-0-open.kicad_pcb`.

Each was measured with its own project rules. The metrics of today's gate match `routing.json`
(116 vias, 640.16 mm, 2 islands).

| Metric | 4L official | 4L variant4 | 2L (c45c6de) |
|---|---:|---:|---:|
| drc_errors / unconnected | 0 / 0 | 0 / 0 | 0 / **13** |
| power_width_violations (too narrow) | **1** (9.98 mm) | **1** (23.0 mm) | 0 |
| gnd_islands | 2 | **1** | 2 |
| signal_vias / gnd_vias | **70** / 46 | 74 / 50 | 29 / 44 |
| signal_length_mm | **606.4** | 632.3 | 387.8 |
| detour_worst5 | **2.02** | 2.22 | 1.51 |
| bends / acute / overlapping | 252 / **3** / 10 | **237** / 4 / **8** | 152 / 14 / 5 |
| via_in_pad (C15:2, J1:4, J5:2 ×2) | 4 | 4 | 11 |
| tight_clearance | **230** | 245 | 41 (rule 0.13) |
| power_drop_mv (max, 2 A) / Q1→VM | 81.6 / **56.2** | 81.6 / 88.8 | 81.6 / 36.5 |
| sense_coupling_mm | 1.67 | **1.16** | 1.66 |
| sense_length_mm | **45.4** | 64.6 | 21.4 |
| return_gap_mm | **0.3** | 1.1 | 78.2 (USB 28 mm) |
| antenna_intrusions / proximity_mm | 0 / 1.5 | 0 / 1.5 | 0 / 5.9 |
| stitch_gap_p95_mm | **3.29** | 3.30 | 3.85 |
| gnd_vias_module | 26 | **30** | 27 |
| usb_skew_mm / usb_vias / usb_stubs | 7.2 / 6 / 0 | 7.2 / 6 / 0 | 7.2 / 6 / 0 |
| **S** (default weights) | **96.2** | 99.3 | 201.9 |

**Which 4-layer state wins? The official board (attempt 3).**
1. **Hard stage:** both violate `power_width_violations`, path Q1 → U2 VM. Following Deb, the smaller
   violation decides: official 10 mm too narrow (min. 0.2 mm, 3 vias, 28 mΩ), variant4 23 mm (min. 0.25 mm, 5 vias,
   44 mΩ).
2. **Soft stage** (if the path is left out): ΔS = +3.07 for variant4, i.e. clearly above the threshold.
   - Against variant4: sense lines +19 mm, ISEN_ADC detour 2.9×, +15 tight spots, +4 signal vias,
     +26 mm, drop +7 mV.
   - For variant4: 1 GND island fewer (−3 points), 2 doubled tracks fewer, 4 more GND vias at the module.
3. **Robustness:** 98.9 % of the random weight sets keep the official board. It would only flip if
   `gnd_islands` weighed more than 2.4 times as much (weight > 7).
4. **Today's gate:** it would have taken variant4, because `gnd_islands` (1 < 2) decides before vias and length.

The 2-layer state is a different design (different fingerprint) and is never compared against 4 layers in the
gate. Here it only serves as a plausibility check:
- The return-path metric detects the cut-up bottom side (78 mm without reference, 28 mm of it USB).
- The current paths there are wide enough (Freerouting, net class Power 0.4 mm).

## 6. Integration into `route_gate.py` (plan, after the weights are confirmed)

1. **New module** `hardware/scripts/route_score.py`: `measure_all(pcb, cfg)` (content of `score_metrics.py`),
   `evaluate(cfg, metrics, details)` → `(hard_excess, hard_total, under_mm, S, parts)`,
   `decide(cfg, cand, official)` → `(accept, reason, report_lines)`. Configuration `hardware/routing-score.toml`;
   optionally per board `[boards.main-board]` for nets and paths.
2. **`route_gate.measure()`** calls `measure_all()`. The previous five metrics stay in the result
   (`via_count`, `track_length_mm` …), so that `short()`/`slug()` and old `routing.json` files remain readable.
3. **`rank()`** is replaced by `decide()`. `route.py` picks the best attempt of one call with the same
   function: feasible first, then smallest violation, then smallest S. A Pareto list in the log is added.
4. **`routing.json`** additionally gets:
   - `"score": {"S": …, "hard": …, "parts": {…}}`;
   - `"score_config_sha256"` (hash of the TOML);
   - `"metrics_version"`;
   - `"details"` (paths, worst nets).
   `"ranking"` is dropped or becomes `"decision": "hard+weighted"`.
5. **Re-measure instead of trusting stored values:** if `score_config_sha256` or `metrics_version` differ
   (new weights, new metric), the gate re-measures the official board (3.5 s). Weight changes thus take
   effect immediately and fairly.
6. **Commands:**
   - `route_gate.py score <board> [file …]`: report without decision, also for several files from
     `build/<board>/keep/`;
   - `route_gate.py explain <board> <candidate>`: contribution table, flip factors, robustness;
   - `just route-score main-board`.
7. **Unchanged:** fingerprint, storage under `rejected/`, restore and `force=1`. Instead of "worse at X",
   the reason texts name the two largest contributions.
8. **Docs:** replace the sections "Metrics" and "Decision" in development.md. After implementation this document
   is cut down to the current state (decisions), and the prototype numbers move to the history.

Runtime: the measurement costs 3.5 s per candidate and run, negligible compared with 20–60 min of routing.

## 7. Limits and open items

- **Current path = one route** (lowest resistance). Parallel routes and zones are not included, so the
  calculation is conservative. VSYS has no zone.
- **IPC-2221 is conservative.** KiCad's own calculator uses the Brooks/Adam fit to IPC-2152 data. Switching
  to it is possible (formula ΔT = K·I^a·W^b·Th^c). For the decision between two runs this changes
  little; for the hard limit it probably does.
- **Coupling** is only a geometric distance band (0.6 mm), not a field computation. For *comparing* runs
  that is sufficient.
- **`tight_clearance`** counts DRC pairs, not their length. Fine-pitch pads create a fixed base
  (approx. 200) that cancels out in ΔS.
- **SWIG bindings** are deprecated as of KiCad 9 (removal planned for KiCad 11). The successor is the IPC API
  (`kicad-python`/`kipy`). This affects the whole project, not just the score.
- `kicad-cli pcb drc --refill-zones` only exists after KiCad 9. That is why the prototype refills in memory.
  The DRC part checks (as today) the stored fill.
- **Weights are opinions.** The robustness line shows whether a decision depends on them.

## 8. Side findings (from the prototype, not fixed)

1. **Battery–motor path too narrow (4 layers, both states).**
   - Q1:2 (VSYS) → U2:1 runs over `route_fix.py` tracks of 0.2/0.3 mm, partly on In2 (15 µm).
   - At 2 A this gives 56 mV (official) or 89 mV drop. According to IPC-2221 a 0.2 mm piece on In2 carries only
     about 0.3 A at 20 K.
   - In battery operation the entire motor current flows this way.
   - Proposal: pre-route Q1:2 → C2/VSYS main track in `gen_main_pcb.py` at 0.5 mm on F.Cu, or
     set `WIDTHS["/VSYS"]` to 0.4 mm for this section. Then re-route.
2. **Via in pad:**
   - C15:2 (0402, GND) has a via in the pad, as do the solder pads J1:4 and J5:2. The vias are probably placed by `stitch.py` or
     `route_fix.py` (GND connection).
   - With 0402 there is a risk of solder wicking and tombstoning.
   - Proposal: for the GND connection, place vias only next to SMD pads (except list).
3. **Net class patterns in the `.kicad_pro` are outdated** (already in the 2-layer state):
   - `ISEN`/`/ISEN` → Power, `GND` in Power and Supply, `MOT_A`/`MOT_B` no longer exist.
   - According to `gen_main_pcb.py`, ISEN should stay in the default class.
   - Effect: no DRC errors, but wrong target widths.
4. **Doubled tracks:** 8–10 same-net tracks run back over each other (`overlapping_segments`, +3V3 and
   EN on B.Cu). This is a router leftover, electrically harmless. Clean up before manufacturing.
5. **USB:** D− is 7.2 mm longer than D+ (pre-routed, identical in all states). Uncritical for Full Speed;
   Espressif nevertheless recommends equal length.

## Sources

- KiCad 9 CLI (`pcb drc`, JSON, severities): https://docs.kicad.org/9.0/en/cli/cli.html (checked). DRC schema
  https://schemas.kicad.org/drc.v1.json (checked). `--refill-zones` only in the development docs:
  https://docs.kicad.org/master/en/cli/cli.html (checked).
- KiCad custom rules: https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html#custom-design-rules (section not
  read, syntax tested in the prototype with KiCad 9.0.8).
- pcbnew Python (ZONE, ZONE_FILLER): https://docs.kicad.org/doxygen-python-9.0/classpcbnew_1_1ZONE.html (not
  opened). SWIG deprecation / IPC API: https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/ (checked).
- IPC-2221 current capacity I = k·ΔT^0.44·A^0.725, k = 0.048 external / 0.024 internal (not checked, standard formula).
  IPC-2152: inner layers need not be derated as strongly. Brooks/Adam, "Internal Trace Temperatures", I-Connect007 2018:
  https://iconnect007.com/article/114225/brooks-bits-internal-trace-temperaturesmore-complicated-than-you-think/114228/pcb
  (checked). KiCad calculator (Brooks/Adam fit):
  https://docs.kicad.org/doxygen/tracks__width__versus__current__formula_8h_source.html (checked).
- USB Full Speed:
  - Renesas R01AN0628EJ0100, Guidelines for Full-Speed USB2.0 Board Design (recommends 90 Ω ±15 % even for FS):
    https://renesas.com/en/document/apn/full-speed-usb-guidelines-full-speed-usb20-board-design-rev100 (checked).
  - TI SPRAAR7J High-Speed Interface Layout Guidelines: https://www.ti.com/lit/an/spraar7j/spraar7j.pdf (checked).
  - FS edges 4–20 ns (USB 2.0, not checked).
- Espressif ESP32-C6 Hardware Design Guidelines, PCB layout:
  https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/pcb-layout-design.html
  (checked)
  - Antenna at the edge and without copper on any layer, 15 mm clearance, dense GND vias at the module.
  - USB: 90 Ω ±10 %, equal length, continuous ground, few vias.
  - See also analysis-wireless-controllers.md.
- TI DRV8213 datasheet SLVSGV9 (layout 11.1: wide tracks VM/OUT/GND, thermal pad with vias to inner
  GND layers; IPROPI 8.4.2.2): https://www.ti.com/lit/ds/symlink/drv8213.pdf (checked). No specific guidance on
  IPROPI routing; `sense_*` is general practice.
- Freerouting scoring (router and optimizer score):
  https://github.com/freerouting/freerouting/blob/master/docs/scoring.md (checked).
- TopoR (length and vias as objective, any angle): https://en.wikipedia.org/wiki/TopoR (checked).
- Deb, K. (2000): An efficient constraint handling method for genetic algorithms. CMAME 186(2–4), 311–338,
  doi:10.1016/S0045-7825(99)00389-8 (bibliographically checked).
- Das, I.; Dennis, J. E. (1997): A closer look at drawbacks of minimizing weighted sums of objectives for Pareto
  set generation. Structural Optimization 14, 63–69, doi:10.1007/BF01197559 (bibliographically checked).
- Acid traps: https://resources.pcb.cadence.com/blog/are-acid-traps-still-a-problem-for-pcbs (not opened).
  Via-in-pad/IPC-4761 type VII: https://sierraconnect.protoexpress.com/t/pcb-glossary-via-in-pad/3899 (not
  opened).
