# Looping Louie Wi-Fi upgrade

Retrofit electronics for Looping Louie (old and new) and Loopin' Chewie: plugs into the **battery compartment
without soldering** and makes the game controllable via a **web UI on the phone**, with
game modes, custom modes, game master and player roles. The original lever stays start/stop.

> Status (2026-11-06): restart (branch `v2`). Concept is done. Main board in design (4 layers, routing of the
> current version in progress), charger board designed, nothing ordered yet. Web UI as a clickable prototype
> (`web/poc`). Firmware planned in **Rust**, no code yet.
> The old MicroPython/ESP8266 version is in the tag `v1-legacy`.

## Components

| Assembly | Description |
|---|---|
| **Main board** | In the format of an AA cell, 4 layers, single-sided assembly: ESP32-C6-MINI-1 (Wi-Fi, BLE), H-bridge DRV8213 with current sensing, USB-C for flashing and 5 V operation, lever detection; solder pads on the bottom for player inputs, LEDs, I²C |
| **Charger board** | Also AA format: USB-C (charging), charge controller, LiPo connection. Sits upright in the second compartment (replaces the bridge there) or is glued into the base |
| **Bridge** | AA dummy made of copper for the second compartment when the charger board sits in the base |
| **C-cell adapter** | 3D-printed adapter so the main board fits into the C-cell compartment of the old Louie |
| **Firmware** | Rust (std on ESP-IDF); game logic as a hardware-free crate, runs on the ESP, in PC tests and as WebAssembly in the browser (mode preview) |
| **Web UI** | runs offline from the ESP; concept and clickable prototype in `web/poc` |

Details:
- Hardware: [docs/hardware-konzept.md](docs/hardware-konzept.md), [docs/hauptplatine-c6.md](docs/hauptplatine-c6.md),
  [docs/ladeplatine.md](docs/ladeplatine.md) (with wiring diagram)
- Software: [docs/firmware-architecture.md](docs/firmware-architecture.md), [docs/software-konzept.md](docs/software-konzept.md),
  [docs/web-ui-konzept.md](docs/web-ui-konzept.md), [docs/modus-baukasten.md](docs/modus-baukasten.md)
- Test setup before the board: [docs/test-hardware.md](docs/test-hardware.md)
- Open items and decisions: [docs/offene-punkte.md](docs/offene-punkte.md),
  history: [docs/decision-history.md](docs/decision-history.md)
- Costs: [docs/kostenabschaetzung.md](docs/kostenabschaetzung.md)

## Directories

```
docs/                 concepts, decisions, development guide, images
hardware/
  bom/teile.csv       BOM with manufacturer parts, LCSC numbers, alternatives
  lib/                project library (symbols, footprints, 3D) – created with just parts
  main-board/         KiCad project main board (4 layers)
  charger-board/      KiCad project charger board (2 layers)
  mechanik/           3D-printed parts (OpenSCAD): main board sleeve, charger board holder
  scripts/            generators (schematic, layout, placement), router with keep-best gate,
                      routing score, envelope check, part fetching, tool check
  routing-score.toml  weights of the routing score
web/
  poc/                clickable web UI prototype (one HTML file, offline)
  prototype/          first, outdated UI draft
firmware/             (planned) Rust firmware and core crate, see docs/firmware-architecture.md
tools/                downloaded tools (Freerouting), created by setup.sh, not in Git
justfile              all development commands (just --list)
setup.sh              installs all tools
```

## Quick start

```bash
./setup.sh     # install all tools (once, Ubuntu/Debian)
just check     # check tools
just --list    # all commands
```

Setup and workflow: [docs/entwicklung.md](docs/entwicklung.md)

## License

Using, building and adapting the project is free for **non-commercial purposes**; making money with the project
only with prior permission. Software: [PolyForm Noncommercial 1.0.0](LICENSES/PolyForm-Noncommercial-1.0.0.md),
hardware and docs: [CC BY-NC-SA 4.0](LICENSES/CC-BY-NC-SA-4.0.txt). Details and exceptions: [LICENSE](LICENSE).
