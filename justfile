# Looping Louie Wi-Fi upgrade – development commands
# Overview: just --list

kicad_python := env("KICAD_PYTHON", "/usr/bin/python3")
hw := "hardware"

# Check tools
check:
    @KICAD_PYTHON={{kicad_python}} {{hw}}/scripts/check_tools.sh

# Fetch missing LCSC parts from bom/parts.csv into hardware/lib
parts:
    @python3 {{hw}}/scripts/fetch_parts.py

# Fetch all LCSC parts again (overwrites)
parts-update:
    @python3 {{hw}}/scripts/fetch_parts.py --overwrite

# Generate the project symbols (hardware/lib/louie.kicad_sym)
symbols:
    @python3 {{hw}}/scripts/gen_symbols.py

# Generate the main board schematic from gen_main_schematic.py (overwrites!)
schematic: symbols
    @python3 {{hw}}/scripts/gen_main_schematic.py
    @just erc

# Set the AA outline of the main board (dimensions in hardware/scripts/board_outline.py)
outline:
    @{{kicad_python}} {{hw}}/scripts/board_outline.py 2>&1 | grep -v "swig/python detected a memory leak"

# Create and place the main board (4 layers, placement.py) from the schematic (overwrites the layout, old state → build/main-board/keep/)
pcb:
    @{{kicad_python}} {{hw}}/scripts/gen_main_pcb.py 2>&1 | grep -v "swig/python detected a memory leak"
    @just plot

# Relink the main board footprints to the schematic (after just schematic); layout and routing stay
pcb-sync:
    @{{kicad_python}} {{hw}}/scripts/gen_main_pcb.py --sync-links 2>&1 | grep -v "swig/python detected a memory leak"

# Main board end to end: create, route (gate: improvements only), ERC, DRC; options as for just route
main-board *args:
    @just pcb
    @just route main-board {{args}}
    @just erc
    @just drc

# old name (until 2026-11-03 a separate 4-layer variant hardware/main-board-4l/)
alias four-layer := main-board

# Placement with ratsnest as an image (build/main-board/placement.png)
plot:
    @{{kicad_python}} {{hw}}/scripts/plot_layout.py 2>&1 | grep -v "swig/python detected a memory leak"

# Main board: own router route_fix.py (ROUTER=own, default), ROUTER=freerouting for Freerouting + finishing;
# charger board: Freerouting. Options: runs=N (attempts, default 6), force=1 (bypass the gate),
# pre=none,krt,krt-novip (main board: starting states in turn, krt = pre-router KiCadRoutingTools, docs/development.md).
# Only a better result is accepted (hardware/<board>/routing.json)
# Route automatically and fill ground zones, board: main-board | charger-board
route board="main-board" *args:
    @{{kicad_python}} {{hw}}/scripts/route.py {{board}} {{args}} 2>&1 | grep -v "swig/python detected a memory leak\|Debug: Adding duplicate image handler"

# Long routing run (e.g. overnight, just route-long main-board runs=200 pre=none,krt,krt-novip) as its own
# systemd unit: keeps running when the terminal or the Claude app exits, memory limited (MemoryMax, otherwise a
# bug fills RAM and swap of the whole machine), no suspend meanwhile. Follow: journalctl --user -fu louie-route
# Abort: systemctl --user stop louie-route
route-long board="main-board" *args:
    systemd-run --user --unit=louie-route --collect -p MemoryMax=8G -p MemorySwapMax=2G \
        --working-directory="{{justfile_directory()}}" \
        systemd-inhibit --what=sleep:idle --why="Routing run {{board}}" "{{just_executable()}}" route {{board}} {{args}}
    @echo "Running as louie-route – follow: journalctl --user -fu louie-route"

# Quick test of the own router (route_fix.py) on the official board, without a routing run (approx. 1 min)
route-check:
    @{{kicad_python}} {{hw}}/scripts/test_route_fix.py 2>&1 | grep -v "swig/python detected a memory leak\|Debug: Adding duplicate image handler"

# Equivalence test of the route_fix.py speed optimizations (connection list vs. DRC, grid memory, A* vs.
# earlier version), approx. 3 min; optionally a routed state as input
route-check-speed *args:
    @{{kicad_python}} {{hw}}/scripts/test_route_speed.py {{args}} 2>&1 | grep -v "swig/python detected a memory leak\|Debug: Adding duplicate image handler"

# Re-record the routing result: hardware/<board>/routing.json from the official board (metrics via DRC)
route-baseline board="main-board":
    @{{kicad_python}} {{hw}}/scripts/route_gate.py init {{board}} 2>&1 | grep -v "swig/python detected a memory leak\|Debug: Adding duplicate image handler"

# Routing score of the official board and optionally further states (docs/routing-score.md), changes nothing:
# just score [board] [candidate.kicad_pcb …], e.g. just score main-board build/main-board/keep/*.kicad_pcb
score *args:
    @{{kicad_python}} {{hw}}/scripts/route_gate.py score {{args}} 2>&1 | grep -v "swig/python detected a memory leak\|Debug: Adding duplicate image handler"

# Explain the gate decision for a candidate (contributions, tipping factors, robustness): just explain [board] <candidate>
explain *args:
    @{{kicad_python}} {{hw}}/scripts/route_gate.py explain {{args}} 2>&1 | grep -v "swig/python detected a memory leak\|Debug: Adding duplicate image handler"

# Generate the charger board schematic from gen_charger_schematic.py (overwrites!)
charger-schematic:
    @python3 {{hw}}/scripts/gen_charger_schematic.py
    @just erc charger-board

# Create the charger board: outline, placement, bridge, zones (overwrites the layout!), then route
charger-pcb:
    @{{kicad_python}} {{hw}}/scripts/gen_charger_pcb.py 2>&1 | grep -v "swig/python detected a memory leak"
    @just route charger-board

# Check the schematic
erc board="main-board": (_out board)
    kicad-cli sch erc --exit-code-violations -o build/{{board}}/erc.rpt {{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_sch

# Check the board, including parity with the schematic
drc board="main-board": (_out board)
    kicad-cli pcb drc --schematic-parity --exit-code-violations -o build/{{board}}/drc.rpt {{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb

# Schematic as PDF
sch-pdf board="main-board": (_out board)
    kicad-cli sch export pdf -o build/{{board}}/{{"louie-" + replace(board, "-board", "")}}-schematic.pdf {{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_sch

# 3D views as PNG (top, bottom, oblique top, oblique bottom)
render board="main-board": (_out board + "/render")
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb
    out=build/{{board}}/render
    kicad-cli pcb render --side top    --width 1600 --height 700 -o $out/top.png    $pcb
    kicad-cli pcb render --side bottom --width 1600 --height 700 -o $out/bottom.png $pcb
    kicad-cli pcb render --side top --rotate '-45,0,30' --zoom 1.3 --width 1600 --height 900 -o $out/iso.png $pcb
    kicad-cli pcb render --side bottom --rotate '45,0,-30' --zoom 1.3 --width 1600 --height 900 -o $out/iso-bottom.png $pcb

# Fabrication data: Gerber, drill files, placement (CPL), BOM (+ ZIP)
fab board="main-board": (erc board) (drc board) (_out board + "/fab/gerber")
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb
    sch={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_sch
    out=build/{{board}}/fab
    kicad-cli pcb export gerbers -o $out/gerber/ $pcb
    kicad-cli pcb export drill --format excellon --excellon-separate-th -o $out/gerber/ $pcb
    # Placement and BOM without DNP parts (optional footprints on the bottom, docs/idea-optional-hardware.md 0b);
    # the full BOM with a DNP column is written next to it (-bom-all.csv)
    kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp -o $out/{{"louie-" + replace(board, "-board", "")}}-cpl.csv $pcb
    kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},LCSC Part' --exclude-dnp \
        --group-by 'Value,Footprint' -o $out/{{"louie-" + replace(board, "-board", "")}}-bom.csv $sch
    kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},LCSC Part,${DNP}' \
        --labels 'Reference,Value,Footprint,Qty,LCSC Part,DNP' --group-by 'Value,Footprint,${DNP}' \
        -o $out/{{"louie-" + replace(board, "-board", "")}}-bom-all.csv $sch
    rm -f $out/{{"louie-" + replace(board, "-board", "")}}-gerber.zip && zip -qj $out/{{"louie-" + replace(board, "-board", "")}}-gerber.zip $out/gerber/*
    echo "Fabrication data in $out/"

# 3D-printed parts (main board sleeve, charger board holder) as STL (build/mechanics/), previews as PNG
stl: (_out "mechanics")
    #!/usr/bin/env bash
    set -euo pipefail
    scad={{hw}}/mechanics/sleeve.scad
    for t in aa_shell cap_plus cap_minus c_sleeve; do
        openscad -q -D "part=\"print_$t\"" -o build/mechanics/$t.stl $scad
    done
    # previews without --render: keeps the colours (OpenSCAD 2021 cannot CGAL-render the imported board STL anyway)
    for t in assembly assembly_c exploded; do
        openscad -q -D "part=\"$t\"" --imgsize 1600,900 --viewall --autocenter \
            --camera 0,0,0,55,0,25,0 --colorscheme Tomorrow -o build/mechanics/$t.png $scad
    done
    # Charger board holder (AA compartment upright, or base)
    holder={{hw}}/mechanics/charger-holder.scad
    for t in shell cap_plus cap_minus base_holder; do
        openscad -q -D "part=\"print_$t\"" -o build/mechanics/charger_$t.stl $holder
    done
    openscad -q -D 'part="assembly"' --imgsize 1600,900 --viewall --autocenter \
        --camera 0,0,0,60,0,210,0 --colorscheme Tomorrow -o build/mechanics/charger_assembly.png $holder
    openscad -q -D 'part="assembly_base"' --imgsize 1600,900 --viewall --autocenter \
        --camera 0,0,0,55,0,25,0 --colorscheme Tomorrow -o build/mechanics/charger_assembly_base.png $holder
    echo "STL and previews in build/mechanics/"

# 3D model of the board: STEP (CAD), GLB (viewing), STL (3D printing/OpenSCAD) in build/<board>/3d/
model board="main-board": (_out board + "/3d")
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb
    out=build/{{board}}/3d
    kicad-cli pcb export step --force --subst-models --include-tracks --include-pads --include-zones \
        --include-silkscreen --include-soldermask -o $out/{{"louie-" + replace(board, "-board", "")}}.step $pcb >/dev/null
    kicad-cli pcb export glb  --force --subst-models --include-tracks --include-pads --include-zones \
        --include-silkscreen --include-soldermask -o $out/{{"louie-" + replace(board, "-board", "")}}.glb  $pcb >/dev/null
    kicad-cli pcb export stl  --force --subst-models -o $out/{{"louie-" + replace(board, "-board", "")}}.stl $pcb >/dev/null
    ls -la $out

# Check the main board envelope against the AA sleeve (radius < 7.25 mm, bottom only inside the pocket); run just model first
hull:
    @python3 {{hw}}/scripts/hull_check.py

# Main board additionally: inner layers (copper-l2-gnd, copper-l3-signal), placement and the sleeve assembly with
# the real board (needs just model); charger board with the prefix charger-
# Regenerate all images of a board (docs/images/: 3D, copper layers, schematic)
images board="main-board":
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb
    sch={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_sch
    out=docs/images
    pre={{ if board == "main-board" { "" } else { "charger-" } }}
    tmp=$(mktemp -d)
    mkdir -p $out
    kicad-cli pcb render --side top    --width 1800 --height 700 -o $out/${pre}board-top.png    $pcb >/dev/null
    kicad-cli pcb render --side bottom --width 1800 --height 700 -o $out/${pre}board-bottom.png $pcb >/dev/null
    kicad-cli pcb render --side top    --rotate '-45,0,30'  --zoom 1.3 --width 1800 --height 1000 -o $out/${pre}board-3d-top.png    $pcb >/dev/null
    kicad-cli pcb render --side bottom --rotate '45,0,-30'  --zoom 1.3 --width 1800 --height 1000 -o $out/${pre}board-3d-bottom.png $pcb >/dev/null
    for L in F B; do
        mirror=""; [ $L = B ] && mirror="--mirror"
        kicad-cli pcb export svg --mode-single --layers $L.Cu,Edge.Cuts,$L.Fab --fit-page-to-board \
            --exclude-drawing-sheet $mirror -o $tmp/cu_$L.svg $pcb >/dev/null
        inkscape $tmp/cu_$L.svg -w 1800 -b white -o $out/${pre}copper-$( [ $L = F ] && echo top || echo bottom ).png 2>/dev/null
    done
    kicad-cli sch export pdf -o $tmp/sch.pdf $sch >/dev/null
    inkscape $tmp/sch.pdf -o $out/${pre}schematic.png -d 110 2>/dev/null
    if [ {{board}} = main-board ]; then
        for spec in "In1.Cu:copper-l2-gnd" "In2.Cu:copper-l3-signal"; do
            layers=${spec%%:*}; name=${spec##*:}
            kicad-cli pcb export svg --mode-single --layers $layers,Edge.Cuts --fit-page-to-board \
                --exclude-drawing-sheet -o $tmp/$name.svg $pcb >/dev/null
            inkscape $tmp/$name.svg -w 1800 -b white -o $out/$name.png 2>/dev/null
        done
        {{kicad_python}} {{hw}}/scripts/plot_layout.py 2>&1 | grep -v "swig/python detected a memory leak" >/dev/null || true
        cp build/{{board}}/placement.png $out/placement.png
        # sleeve with the real board (3D export from just model; skipped if it is missing)
        if [ -f build/main-board/3d/louie-main.stl ]; then
            scad={{hw}}/mechanics/sleeve.scad
            openscad -q -D 'part="exploded"' -D 'board_stl=true' -D 'shell_alpha=0.6' --imgsize 1600,900 \
                --camera 0,0,1,60,0,205,125 --colorscheme Tomorrow -o $out/sleeve-exploded.png $scad
            openscad -q -D 'part="assembly"' -D 'board_stl=true' -D 'shell_alpha=0.6' --imgsize 1600,900 \
                --camera 0,0,0,60,0,205,85 --colorscheme Tomorrow -o $out/sleeve-assembly.png $scad
        else
            echo "build/main-board/3d/louie-main.stl missing: run just model for the sleeve images"
        fi
    fi
    rm -rf $tmp
    ls $out

# Firmware (firmware/louie-fw, Rust on ESP-IDF). The Cargo target directory lives outside the repo because the
# ESP-IDF build does not support spaces in its paths (firmware/louie-fw/README.md).
fw_dir := "firmware/louie-fw"
fw_target := env("CARGO_TARGET_DIR", env("HOME") / ".cache/louie-fw/target")

# Firmware: release build for a board (devkitc-c6 | louie-v1), prints the image size
fw-build board="devkitc-c6":
    #!/usr/bin/env bash
    set -euo pipefail
    cd {{fw_dir}}
    export CARGO_TARGET_DIR="{{fw_target}}" CARGO_WORKSPACE_DIR="$PWD/"
    cargo build --release --no-default-features --features board-{{board}}
    ls -l "{{fw_target}}/riscv32imac-esp-espidf/release/louie-fw"

# target: louie-fw (bring-up, LED mode) | lever_probe | boot_probe | pin_probe | adc_probe;
# port e.g. /dev/serial/by-id/usb-1a86_… (CH343 port, see just fw-ports)
# Firmware: build, flash and monitor on the dev board
fw-run target="louie-fw" port="":
    #!/usr/bin/env bash
    set -euo pipefail
    cd {{fw_dir}}
    export CARGO_TARGET_DIR="{{fw_target}}" CARGO_WORKSPACE_DIR="$PWD/"
    if [[ -n "{{port}}" ]]; then export ESPFLASH_PORT="{{port}}"; fi
    if [[ "{{target}}" == "louie-fw" ]]; then cargo run --release; else cargo run --release --example {{target}}; fi

# Firmware: serial monitor only (port as in fw-run)
fw-monitor port="":
    espflash monitor {{ if port != "" { "--port " + port } else { "" } }}

# Firmware: list the serial ports of the dev board (CH343 = 1a86, ESP32-C6 USB-Serial-JTAG = Espressif/303a)
fw-ports:
    @ls -l /dev/serial/by-id/ 2>/dev/null | grep -E "1a86|Espressif|303a" || echo "no dev board found (USB cable, dialout group?)"

# Delete generated output (build/)
clean:
    rm -rf build

_out dir:
    @mkdir -p build/{{dir}}
