# Code health

> Introduced 2026-11-23/24 (owner decision: ai-health for all repos).

Code health is scored with [ai-health](https://github.com/epatel/ai-health) (MIT), a deterministic,
CodeScene-style scorer (1–10, no AI in the core). Goal: **10 per component, i.e. no finding**; 9.5 is only the
lower limit on the way there. Healthy code is the precondition for agents to change it reliably; tests and
review stay necessary.

## Code health profile (Steckbrief)

### 1. Scope

Scored separately per component, each with its own config; the goal applies per component. There is no overall
score: the components use different file-size limits, and a mean would offset a weak part against a strong one.

| Component | Path | Config |
|---|---|---|
| Firmware (Rust, std on ESP-IDF) | `firmware/louie-fw/` | `firmware/louie-fw/.aihealth.toml` |
| Python scripts (generators, router, routing score) | `hardware/scripts/` | `hardware/scripts/.aihealth.toml` |

Not scored:

- `web/poc/index.html` (decision Q13: no score): a clickable throwaway prototype with about 3300 lines of
  inline JavaScript, changed twice so far. The real web UI is a separate, separately updatable package
  ([software-concept.md](software-concept.md)) that will not reuse this code. Moving the JS into a `.js` file
  would make it scoreable, but then it would have to be refactored to 10 (about 180 findings in the own
  prototype measurement), which is effort without benefit for code that is replaced. The real UI is written as
  `.js`/`.ts` modules from the start and becomes a third component with its own config.
  `web/prototype/` is outdated (README).
- KiCad projects, libraries, OpenSCAD, datasheets, docs: data, not code. Hardware gets its own checks
  (see 6, options).
- Shell scripts (`setup.sh`, `hardware/scripts/*.sh`) and the justfile: small, rarely changed; ai-health scores
  shell, so they can join the Python component later if wanted.

### 2. Tools and versions

| Component | Score | Linter (no structural gating) |
|---|---|---|
| Firmware | ai-health v0.4.0 (tree-sitter 0.26, language pack 1.25) | clippy (`just fw-lint`, target `riscv32imac-esp-espidf` from `.cargo/config.toml`, nightly-2026-09-15) with embedded lints in `Cargo.toml` `[lints.clippy]`: `undocumented_unsafe_blocks`, `multiple_unsafe_ops_per_block`, `large_stack_arrays`, `large_stack_frames`, `mem_forget`; rustfmt |
| Python | ai-health v0.4.0 | ruff (lint and format, as in the other Python repos), without structural rules |

ai-health runs via `uvx --from git+https://github.com/epatel/ai-health@033d1867fe514867d944d9387ee72db0188eed47
aihealth` (the commit behind v0.4.0): no venv in the repo, the pin lives in one justfile variable. A commit pin
is served from the uv cache (about 0.2 s for uvx to start, offline too); a tag pin resolves over the network on
every call (about 1.6 s). One source per smell: structure comes from ai-health alone, so clippy's structural lints
(`cognitive_complexity`, `too_many_lines`, `too_many_arguments`, `excessive_nesting`) and ruff's (`C901`,
`PLR09xx`, `PLR1702`) stay off. ruff uses line length 120 like the existing code; its first formatting run is
a commit of its own (formatting only, outputs unchanged).

### 3. Smells

All 13 ai-health smells map to CodeScene criteria: Brain Method, Large Method, Complex Method (cyclomatic),
Cognitive Complexity, Deep Nesting, Bumpy Road, Excess Arguments, Complex Conditional, Large File, Low Cohesion
(LCOM4), Primitive Obsession, Code Duplication; Deep Widget Tree and Missing .PHONY do not apply here.

Not covered: Brain Class / God Class (approximated by Large File + Low Cohesion), Large and Duplicated
Assertion Blocks (the Python tests are scripts against KiCad; Rust unit tests in `#[cfg(test)]` are not scored
by default), and CodeScene's organisational factors (developer congestion, former contributors).

### 4. Thresholds, weights, formula

ai-health defaults equal the CodeScene defaults (arguments > 4, cyclomatic > 9, function > 70 lines, nesting
≥ 4, bumpy road ≥ 2 bumps, complex conditional ≥ 2 operators, duplication). Profile "strict" on top (confirmed by the
owner, Q15):

```toml
[thresholds]
large_file = 600            # Python; 1000 in the firmware config
primitive_obsession = 0.3
[score]
decay = 8                   # stricter than the default 15
symbol_cap = 4
density_loc = 100000        # large files are not relieved through finding density
[delta]
tolerance = 0.0
```

Formula and weights: ai-health's (`src/aihealth/scoring.py`), unchanged. The two configs differ only in
`large_file`; `just code-health-config` checks that the rest is identical, so the profile changes in one
step for both.

Primitive Obsession is off in test code (owner decision Q18.1) via a separate config with
`[weights] primitive_obsession = 0`. Not needed here: the only tests are the two untyped router test scripts, where
the smell does not apply, and there are no Rust test modules.

Embedded patterns (interrupt callbacks, state machines as `match`, register values as integers) get no own
thresholds; where one is justified, the file carries `// aihealth: disable=<smell> -- <reason>` (see 6).

### 5. Usage

```bash
just code-health                 # scan of both components (text)
just code-health --format json   # for agents (also: markdown)
just code-health-delta           # working tree vs HEAD (the hook uses --staged), exit 1 if worse
just code-health-delta --base origin/main
just fw-lint                     # firmware: rustfmt check + clippy -D warnings
just hw-check                    # ERC, DRC, generator drift
just lint                        # all pre-commit hooks on all files
```

Every recipe passes `--config <component config>` explicitly: `aihealth scan <dir>` would otherwise look for
`<dir>/.aihealth.toml` and silently fall back to the defaults. With `--format json` the recipe returns one
document per component on stdout (the component name goes to stderr). Runtime: about 1.3 s for both components (uv cache warm).

Own logic beyond calling ai-health (owner principle: only where nothing else works, as thin as possible):

- the loop over the two components in `just code-health` / `code-health-delta`: one call per component, because
  each has its own config; no output processing
- `just code-health-config`: a three-line diff of the two configs, because ai-health has no include and the profile
  must change in one place for both
- `hardware/scripts/check_generated.py` (about 40 lines): the generator drift check, no tool covers it

### 6. Gate

- Local: `aihealth delta --staged` per component (exit 1 on any degradation; new files must be free of
  smells), run by pre-commit (Q14) together with ruff, the suppression check and, for firmware changes,
  `just fw-lint` (clippy with `-D warnings`, a few seconds once the target directory is built).
- CI: none exists. If added (checkout with `fetch-depth: 0`): `aihealth delta --base "$(git merge-base
  origin/main HEAD)" --head HEAD` as gate, plus the component scores of merge base and head side by side
  (Q6; `aihealth scan` of both revisions), and `aihealth scan` as report.
- Ratchet: the delta gate is the ratchet (tolerance 0), no baseline file.
- Suppressions: per file only, sparingly, always as `# aihealth: disable=<smell> -- <reason>` (`//` in Rust).
  Without the ` -- ` separator ai-health reads the free text as part of the smell name and the suppression
  silently does nothing. A check in the hook enforces a reason of at least 10 characters with the regex
  `aihealth:[ \t]*disable=(?![\w, \t]+-- .{10})` (a match is a violation).

Hardware checks (not part of the score), `just hw-check`, run by pre-commit when a KiCad file or a schematic
generator changes (about 4 s):

1. ERC and DRC (with schematic parity) of both boards via kicad-cli.
2. Drift check (`hardware/scripts/check_generated.py`): the generators reproduce the committed symbol library
   and schematics (UUIDs ignored, the charger schematic was committed with random ones); the files are
   restored afterwards.

Further options, not chosen for now: BOM consistency (LCSC number for every fitted part), routing score
regression against `routing.json`, envelope check `just hull` (needs `just model`), a CI job with the KiCad
image.

The hooks are not installed by this change: `pre-commit install` writes into the `.git/hooks` shared by all
worktrees. After the merge, `./setup.sh` installs them. Branches or worktrees created before the merge have no
`.pre-commit-config.yaml`, and the hook refuses to commit there ("No .pre-commit-config.yaml file was found"):
merge main into them, or commit with `PRE_COMMIT_ALLOW_NO_CONFIG=1`.

### 7. Result

Measured with the strict profile (`just code-health`), 2026-11-24:

| Component | Before | After | Files below 10 after |
|---|---|---|---|
| Firmware | 8.55 | **10.0** | none (14 of 14 healthy) |
| Python scripts | 3.69 | **6.45** | 8 of 24 |

Refactored to 10.0 (each with behaviour checked through outputs, see 9): `gen_symbols`, `gen_main_schematic`,
`gen_main_pcb` (split into `pcb_tools`, `preroute_main`), `gen_charger_pcb`, `route_gate`, `stitch`, `route`,
firmware `main.rs` and the three probes, `diag.rs`.

Remaining (worst first), not yet released for refactoring:

| File | Score | Note |
|---|---|---|
| `route_fix.py` | 1.01 | own router, 1194 LoC, 84 findings; router refactoring deferred by the owner |
| `route_score.py` | 1.21 | routing score, 740 LoC; part of the router refactoring |
| `test_route_speed.py`, `test_route_fix.py` | 3.56, 3.65 | router tests (scripts against KiCad) |
| `plot_layout.py`, `fetch_parts.py` | 6.46, 6.88 | one long `main` each |
| `route_finish.py`, `board_outline.py` | 8.23, 7.97 | `board_outline` got two more parameters with the charger outline fix on main (8.47 before) |

### 8. Skills

Checked on skills.sh (SKILL.md read): `wondelai/skills@refactoring-patterns` (recommended),
`apollographql/skills@rust-best-practices`, `kucherenko/jscpd@dry-refactoring`, `aklofas/kicad-happy@kicad`;
not suitable: `adamlipecz/esp32-firmware-engineer` (C/C++, no license), `mohitmishra786/low-level-dev-skills@embedded-rust`
(bare-metal `no_std`), `*@codehealth-mcp` (paid token). Installed (project-local, `.claude/skills/`, `skills-lock.json`):
`refactoring-patterns`, read in full before installing (refactoring catalogue, no executable instructions).

### 9. Experience

What worked:

- ai-health runs offline in about 1.3 s for both components once uv has cached the commit pin; agents get
  JSON and the delta gate. The component scan also reports cross-file duplicates that a single-file scan misses
  (here `setup_rules` in both board generators, the DRC JSON block in three scripts).
- Checking behaviour through outputs instead of unit tests: generators must reproduce symbols and schematics
  byte for byte; boards are compared item by item without UUIDs (KiCad sorts footprints and some children by
  random UUIDs, so a byte comparison fails even between two runs of the same code); the gate is compared with a
  command suite (score, explain, check dry run and `--apply`), the router with a full `runs=1` routing run against
  two runs of the old code. These checks caught one real regression risk early (a lint autofix that would have
  renamed a loop variable read through a closure in `route_fix.py`).
- The firmware gate pair: ai-health for structure, clippy only for embedded concerns (every `unsafe` FFI call
  states its reason). State machines stay a single `match` in a pure `next_state()`; dispatch tables split into
  small matches rather than being suppressed (suppressions are file-wide in ai-health, too coarse here).

What did not work or needs care:

- ai-health counts physical lines: the first ruff formatting run grew some files (e.g. `route_fix.py` 1110 →
  1194 LoC) and lowered their score slightly. Format first, before the gate exists.
- Extracting helpers can create Primitive Obsession (many `u32`/`bool` parameters) in firmware; methods that
  read the tick state are the better cut than free functions with raw values.
- Measurement noise in the routing score (project-specific): the DRC-based metrics of the same board vary by a
  few counts between runs (`tight_clearance`, DRC error count), so S differs by about 0.1–0.2. Gate decisions
  close to the threshold (min_improvement 1.0) can flip; worth a look in `route_score.py`.
- The pinned firmware nightly had never been built and did not build; `nightly-2026-09-15` does (details in
  `firmware/louie-fw/README.md`).
- `just charger-pcb` crashed on main (`board_outline` with a 12.5 mm wide board); the comparison stubbed the
  outline until the fix from a separate task was merged in, then compared against main's generator.

Transferable to other repos: the commit pin and explicit `--config`, the suppression regex, comparing generated
artefacts semantically, formatting before introducing the gate. Project-specific: KiCad checks
(`just hw-check`), the ESP-IDF toolchain pin, the routing-noise caveat.
