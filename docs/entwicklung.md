# Development

Status: 2026-11-06 · Setup and commands for hardware (KiCad) and docs. The firmware (Rust, std on ESP-IDF)
has no code yet; its tools and commands (toolchain, build, flash, tests, WebAssembly preview) will be added with
the firmware, see [firmware-architecture.md](firmware-architecture.md).

## Dependencies

Tested on Ubuntu 26.04. **Set up everything at once:**

```bash
./setup.sh
```

The script only installs what is missing and can be run again at any time.
Individually:

| Tool | Purpose | Installation | Required |
|---|---|---|---|
| KiCad ≥ 9 (incl. `kicad-cli`, Python module `pcbnew`) | schematic, layout, checks, manufacturing data | `sudo apt install kicad` | yes |
| easyeda2kicad | fetch symbols, footprints and 3D models of LCSC/JLC parts | `uv tool install easyeda2kicad` | yes |
| just | command runner (all development commands) | `sudo apt install just` | yes |
| zip, python3 | ZIP of the Gerber data, scripts | usually present | yes |
| kicad-packages3d | 3D models of the KiCad standard parts (for renders) | `sudo apt install kicad-packages3d` | recommended |
| Java ≥ 21 + Freerouting | autorouter for the charger board (`just route charger-board`, main board optional `ROUTER=freerouting`); `setup.sh` downloads `tools/freerouting.jar` | `sudo apt install default-jre` | for routing |
| python3-matplotlib | placement image (`just plot`) | `sudo apt install python3-matplotlib` | yes |

After installation, open KiCad once with the schematic and PCB editor so that the global
library tables are created. Then:

```bash
just check
```

### Python

- Scripts that edit the board (`board_outline.py`) need the `pcbnew` module and therefore run
  with the **system Python** (`/usr/bin/python3`), into which the KiCad package installs the module.
  Different path: `KICAD_PYTHON=/path/to/python3 just outline`.
- `fetch_parts.py` only needs the standard library and the `easyeda2kicad` command.
- There is deliberately no virtual environment: `pcbnew` cannot be installed via pip.

## Commands

```
just check         check tools
just parts         fetch missing LCSC parts from hardware/bom/teile.csv into hardware/lib
just parts-update  fetch all LCSC parts again
just symbols       generate project symbols (hardware/lib/louie.kicad_sym)
just schematic     generate the main board schematic from the generator (overwrites!) + ERC
just outline       set the AA outline of the main board (dimensions in hardware/scripts/board_outline.py)
just pcb           create and place the main board (4 layers) from the schematic (overwrites the layout!)
just plot          placement with ratsnest as an image (build/main-board/placement.png)
just pcb-sync      re-link footprints with the schematic (symbol UUID, value, DNP); layout and routing stay
just route         route the main board: own maze router (route_fix.py), GND via inner layer In1,
                   then fill ground planes; just route charger-board routes the charger board with Freerouting.
                   Options runs=N (attempts), force=1 (bypass the gate), see "Routing: keep the best result"
just main-board    complete main board: create, route, ERC, DRC (old names: just four-layer, just vierlagig)
just route-check   quick check of the own router on the official board (approx. 30 s, no routing run)
just route-baseline  recreate hardware/<board>/routing.json from the official board
just score         routing score of the official board (and other versions: just score main-board build/main-board/keep/*.kicad_pcb)
just explain       explain the gate decision for a candidate: just explain [board] <file.kicad_pcb>
just charger-schematic  generate the charger board schematic (overwrites!) + ERC
just charger-pcb   create, place and route the charger board (overwrites the layout!)
just erc           check the schematic
just drc           check the board, incl. comparison with the schematic
just sch-pdf       schematic as PDF
just render        3D views as PNG
just images        images to docs/bilder/ (3D, all four copper layers, schematic, placement; just images charger-board)
just modell        3D model as STEP/GLB/STL (build/main-board/3d/, envelope check in hardware/mechanik/huelle.scad)
just hull          check the envelope (after just modell): radius < 7.25 mm, bottom only in the pocket (|y| ≤ 5.2, ≤ 1.5 mm high)
just fab           manufacturing data (Gerber, drill data, placement, BOM, ZIP); DNP parts not in placement/BOM
just clean         delete build/
```

Recipes with a `board` parameter (`erc`, `drc`, `route`, `render`, `images`, `modell`, `fab`, `sch-pdf`) default to
the main board (`main-board`, 4 layers); `charger-board` is the charger board (2 layers).
All outputs go to `build/<board>/` (not in Git).

## Parts

- **The source of truth is `hardware/bom/teile.csv`**: function, value, manufacturer part, package,
  LCSC number, alternatives, status.
- Goal: **common parts** that are available from several distributors (LCSC, Mouser, DigiKey, Reichelt …),
  so that quotes can be obtained from different PCB manufacturers.
- Passive parts are generic and come from the KiCad standard libraries. Main board: **0402** (space in the
  AA format, machine assembly); charger board: 0603/0805 (also hand-solderable).
- ICs, modules and connectors go into the project library `hardware/lib/lcsc.*` via `just parts`.
  Own symbols and footprints (solder pads, test pads) are in `hardware/lib/louie.*`.
  The libraries are checked in, so the project also opens without internet.
- New part: add a row to `teile.csv` (`bibliothek` = `lcsc`, enter the LCSC number), then `just parts`.
- The EasyEDA API blocks briefly after too many requests (HTTP 403). The script therefore pauses
  between parts; if blocked, simply run it again later.

## Schematic

- The first schematic of the main board is generated by `hardware/scripts/gen_main_schematic.py`.
  The circuit is defined there as a Python list (parts, values, footprints, pin → net).
  Every pin gets a net label, unused pins a no-connect cross.
- Symbols: KiCad standard library where available. Own symbols (ESP32-C6-MINI-1, DRV8213DSG, LIS2DH12) and
  the solder pad/test pad footprints are generated by `hardware/scripts/gen_symbols.py` (`just symbols`), because
  the LCSC symbols have no pin types and the ERC check would be worthless with them.
- The symbol UUIDs are fixed (derived from project and reference): running `just schematic` again does not change the
  link to the board. Older boards or new parts without a layout change: `just pcb-sync`.
- **As soon as the schematic is edited in the KiCad GUI, the GUI version is authoritative.**
  Then do not run `just schematic` any more; it would overwrite the changes.

## Layout

- The main board has **4 layers** (decision 2026-11-03; stack-up JLC04081H-3313, 0.8 mm; In1 = GND layer,
  In2 = signals; [hauptplatine-c6.md](hauptplatine-c6.md) chapter 11; why not 2 layers:
  [decision-history.md](decision-history.md)). The charger board has 2 layers.
- `just pcb` recreates the board by script (`gen_main_pcb.py`): outline, stack-up, footprints with
  nets, design rules (also `louie-main.kicad_dru`), net classes, antenna keep-outs, pre-routes, thermal vias,
  ground planes on all layers. The placement is in `placement.py`: everything assembled on top; bottom only solder
  pads, test points and optional, unassembled footprints (DNP, [idee-optionale-hardware.md](idee-optionale-hardware.md) 0b).
- `just plot` draws top and bottom with ratsnest and reports overlaps.
- `just route` routes with the own router `route_fix.py` (`ROUTER=freerouting` as an alternative). Then `just drc`.
- Options of the own router are at the top of `route_fix.py`: `ENDPOINT_VIAS` (a via at a trace end or
  pad counts as a connection on all layers), `VIA_UNDER_BODIES` (`"bottom"`: vias between the pads under parts
  allowed, `"none"`: not allowed), `ISLAND_AREA_SEARCH` (search the whole fill area for a via for GND islands), `WIDTHS`
  (trace width per net, the last one is the minimum width), `MAX_ROUNDS` (steps per pass). Check with
  `just route-check`.
- Running `just pcb` overwrites the routed board; the old version is saved beforehand to
  `build/<board>/keep/before-pcb-<time>.kicad_pcb`.
- **Same as for the schematic:** as soon as routing or moving is done in the GUI, the GUI version is
  authoritative; `just pcb` would overwrite everything.

## Routing: keep the best result

The routers vary a lot (own router on 4 layers: 0–5 unrouted connections on the previous design). So that a
new run does not overwrite a better result, every `just route` goes through a gate (`hardware/scripts/route_gate.py`):

1. **Attempts:** `just route main-board runs=10` starts 10 attempts (default 6, in parallel `ROUTE_PARALLEL`, default 3).
   The best attempt goes to the gate: first feasible, then smallest violation, then smallest score S (same rules as
   the gate). The log shows a table of all attempts and the Pareto view.
2. **Metrics and score** (`hardware/scripts/route_score.py`, configuration `hardware/routing-score.toml`, rationale
   and definitions in [routing-score.md](routing-score.md)): kicad-cli DRC as JSON (twice, the second run with
   0.05 mm extra clearance) and pcbnew; zones are only refilled in memory; approx. 3–4 s per board.
   - **Hard constraints** (`[hard]`): `drc_errors`, `unconnected`, `antenna_intrusions` (copper of other nets in the
     antenna keep-outs), `power_width_violations` (current paths from `[[boards.<board>.paths]]`, width per
     IPC-2221, more than 2 mm too narrow).
   - **Soft metrics** (`[soft]`): score `S = Σ weight · value / scale`, smaller is better, e.g. GND islands,
     signal vias, signal length, detours, voltage drop of the current paths, coupling of the sense lines to OUT_A/OUT_B,
     length without GND reference, distance to the antenna, USB.
   - `weight` is the importance (user), `scale` the size of a "noticeable difference" (fixed). If the TOML changes
     (hash) or there is a new metrics version (`METRICS_VERSION`), the gate re-measures the official board.
3. **Result file** `hardware/<board>/routing.json` (checked in): design fingerprint, `board_hash` of the
   official board, all metrics, `score` (S, hard violations, contributions), `score_config_sha256`,
   `metrics_version`, `details` (current paths, worst nets), router and variant, timestamp, tool versions.
4. **Decision** (`route_score.decide()`):
   - same fingerprint:
     1. feasible beats infeasible; if both are infeasible, the smaller violation wins (count, then too-narrow
        length of the current paths; Deb's rule);
     2. otherwise the gate only accepts the run at **ΔS ≤ −1.0** (`min_improvement`) and if no metric with a veto
        (`max_regression`: voltage drop +30 mV, coupling +5 mm, antenna proximity +3 mm) gets worse;
     - accepted → replaces `louie-*.kicad_pcb` and `routing.json`;
     - not accepted → the official board stays; the run is saved under
       `build/<board>/route/rejected/<time>-<metrics>.kicad_pcb`
       (log line "New run: S … (+…), hard … → rejected (…; main drivers …)", log text: „Neuer Lauf: … → verworfen
       (…; Haupttreiber …)“). If `just pcb` overwrote the official board before, the gate restores the previous
       routing (from `build/<board>/keep/` or Git).
   - different fingerprint (design changed) → the best run becomes official, the baseline is reset
   - `just route <board> force=1` accepts without comparison
   Every accepted board is also stored as `build/<board>/keep/accepted-<time>-<metrics>.kicad_pcb`. The gate writes
   the full report of the last decision (contributions, tipping factors, robustness, current paths) to
   `build/<board>/route/score-report.txt`.
5. **Change weights:** only `weight` (and `min_improvement`) in `hardware/routing-score.toml`. `just score` and
   `just explain` show beforehand how the ranking changes; the robustness line shows whether a
   decision depends on the weights (below approx. 10 % or above 90 % of the random weight sets = stable).

**Fingerprint:** SHA-256 over the *unrouted* board as `just pcb` writes it (placement, pre-routes,
zone outlines, keep-outs, nets, board setup) plus `board.design_settings`/`net_settings` from the `.kicad_pro`
and the `.kicad_dru`. Normalized beforehand: without UUIDs (also in paths), generator/version identifiers,
plot settings and zone fills; elements sorted (KiCad sorts by UUID when saving). Saving again
or regenerating therefore does not change it, but a moved part position does.

It cannot be computed from a *routed* board: `route_fix.py` and `stitch.py` lock their traces and
vias just like the pre-routes, so "locked" does not distinguish design from routing. Therefore, at the start of a
run: if the start board (normalized) is the official one from `routing.json` (`board_hash`, i.e. running
`just route` again without `just pcb`), its stored fingerprint applies; otherwise the start board is the unrouted one
and its hash is the fingerprint. A routed board changed in the GUI therefore counts as a changed design.

**Further commands:**

```
just route-baseline main-board        create routing.json from the official board (generates the unrouted
                                      board for it in a temporary folder, checks that placement, zones,
                                      rules and all pre-routes match the official one)
route_gate.py check <board> <file>    send a board through the gate as a trial (changes nothing without --apply)
route_gate.py fingerprint <file>      fingerprint/content hash of a board
route_gate.py measure <file>          metrics, details and assessment of a board (JSON)
route_gate.py score [board] [file …]  score table, report per file and Pareto view (= just score)
route_gate.py explain [board] <file>  explain the decision against the official board (= just explain)
```

Environment variables (old names still work): `ROUTE_RUNS` (old `FREEROUTING_ATTEMPTS`), `ROUTE_PARALLEL`
(old `FREEROUTING_PARALLEL`), `ROUTER=own|freerouting` (main board; old `ROUTER=eigen`), `ROUTE_VARIANTS`,
`ROUTE_PLANE`, `ROUTE_GND`, `FREEROUTING_PASSES`, `FREEROUTING_JAR`. The working folders of the attempts are named
`build/<board>/route/attempt_<n>/`.

## KiCad projects

- Each board has its own project under `hardware/<board>/`.
- The project library tables (`sym-lib-table`, `fp-lib-table`) refer relatively to
  `${KIPRJMOD}/../lib/`. Nothing needs to be registered globally in KiCad.
- `*.kicad_prl` (local view settings) and backups are not checked in.

## Manufacturing

- `just fab` generates vendor-neutral data: Gerber with classic extensions, Excellon drill data,
  placement list (CSV) and BOM with an LCSC column.
- **DNP:** optional parts (bottom, `dnp` in the schematic and on the footprint, status "DNP/optional" in `teile.csv`)
  are missing from the placement list and BOM (`--exclude-dnp`); `…-stueckliste-alle.csv` lists them with a DNP column.
  This keeps assembly single-sided (top).
- For manufacturers with their own format (e.g. JLCPCB column names), the CSVs are adapted as needed.
