# Code health

> Introduced 2026-11-23 (owner decision: ai-health for all repos).

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
| Firmware | ai-health v0.4.0 (tree-sitter 0.26, language pack 1.25) | clippy with `--target riscv32imac-esp-espidf` and embedded lints (needs the ESP-IDF toolchain, not installed yet) |
| Python | ai-health v0.4.0 | ruff (lint and format, as in the other Python repos), without structural rules |

ai-health runs via `uvx --from git+https://github.com/epatel/ai-health@033d1867fe514867d944d9387ee72db0188eed47
aihealth` (the commit behind v0.4.0): no venv in the repo, the pin lives in one justfile variable. A commit pin
is served from the uv cache (about 0.2 s, offline too); a tag pin resolves over the network on every call
(about 1.6 s). One source per smell: structure comes from ai-health alone, so clippy's structural lints
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

Embedded patterns (interrupt callbacks, state machines as `match`, register values as integers) get no own
thresholds; where one is justified, the file carries `// aihealth: disable=<smell> -- <reason>` (see 6).

### 5. Usage

```bash
just code-health                 # scan of both components (text)
just code-health --format json   # for agents (also: markdown)
just code-health-delta           # staged changes against HEAD, exit 1 if worse
just code-health-delta --base origin/main
```

Every recipe passes `--config <component config>` explicitly: `aihealth scan <dir>` would otherwise look for
`<dir>/.aihealth.toml` and silently fall back to the defaults. With `--format json` the recipe returns one
object keyed by component (merged with jq). Runtime: about 1.3 s for both components (uv cache warm).

### 6. Gate

- Local: `aihealth delta --staged` per component (exit 1 on any degradation; new files must be free of
  smells), run by pre-commit (Q14) together with ruff and the suppression check.
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
worktrees and would block commits on branches without `.pre-commit-config.yaml`. After the merge,
`./setup.sh` installs them.

### 7. Result

Before (trial run of the coordinating session, 2026-11-23, not yet repeated here): firmware 9.15 with the
default curve, 8.55 with "strict" (worst: `src/main.rs`, `examples/lever_probe.rs`); Python 5.53 with the
default curve (worst: `route_fix.py`, `route_score.py`, `route.py`). After: to be filled in.

### 8. Skills

Checked on skills.sh (SKILL.md read): `wondelai/skills@refactoring-patterns` (recommended),
`apollographql/skills@rust-best-practices`, `kucherenko/jscpd@dry-refactoring`, `aklofas/kicad-happy@kicad`;
not suitable: `adamlipecz/esp32-firmware-engineer` (C/C++, no license), `mohitmishra786/low-level-dev-skills@embedded-rust`
(bare-metal `no_std`), `*@codehealth-mcp` (paid token). Installed: none yet.

### 9. Experience

- A first own tree-sitter prototype matched lizard exactly on Python's cyclomatic complexity; it was replaced
  by ai-health by owner decision (one tool across repos).
- Project-specific: the firmware is `std` on ESP-IDF and has never been built, so clippy needs the ESP-IDF
  download first. Behaviour of the Python scripts is verified through their outputs (byte-identical
  schematics/boards, identical routing score), not through unit tests.
