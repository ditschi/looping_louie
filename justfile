# Looping Louie WLAN-Upgrade – Entwicklungsbefehle
# Übersicht: just --list

kicad_python := env("KICAD_PYTHON", "/usr/bin/python3")
hw := "hardware"

# Werkzeuge prüfen
check:
    @KICAD_PYTHON={{kicad_python}} {{hw}}/scripts/check_tools.sh

# Fehlende LCSC-Teile aus bom/teile.csv nach hardware/lib holen
parts:
    @python3 {{hw}}/scripts/fetch_parts.py

# Alle LCSC-Teile neu holen (überschreibt)
parts-update:
    @python3 {{hw}}/scripts/fetch_parts.py --overwrite

# Projekteigene Symbole erzeugen (hardware/lib/louie.kicad_sym)
symbols:
    @python3 {{hw}}/scripts/gen_symbols.py

# Schaltplan der Hauptplatine aus gen_main_schematic.py erzeugen (überschreibt!)
schematic: symbols
    @python3 {{hw}}/scripts/gen_main_schematic.py
    @just erc

# AA-Umriss der Hauptplatine setzen (Maße in hardware/scripts/board_outline.py)
outline:
    @{{kicad_python}} {{hw}}/scripts/board_outline.py 2>&1 | grep -v "swig/python detected a memory leak"

# Schaltplan auf die Platine übertragen und platzieren (überschreibt Layout!), Variante: einseitig (C6-Stand) | zweiseitig (veraltet, C3)
pcb variant="einseitig":
    @{{kicad_python}} {{hw}}/scripts/gen_main_pcb.py {{variant}} 2>&1 | grep -v "swig/python detected a memory leak"
    @just plot

# Platzierung mit Luftlinien als Bild (build/main-board/placement.png)
plot:
    @{{kicad_python}} {{hw}}/scripts/plot_layout.py 2>&1 | grep -v "swig/python detected a memory leak"

# Automatisch routen (Freerouting) und Masseflächen füllen, board: main-board | charger-board
route board="main-board":
    @{{kicad_python}} {{hw}}/scripts/route.py {{board}} 2>&1 | grep -v "swig/python detected a memory leak\|Debug: Adding duplicate image handler"

# Schaltplan der Ladeplatine aus gen_charger_schematic.py erzeugen (überschreibt!)
charger-schematic:
    @python3 {{hw}}/scripts/gen_charger_schematic.py
    @just erc charger-board

# Ladeplatine anlegen: Umriss, Platzierung, Brücke, Flächen (überschreibt Layout!), danach routen
charger-pcb:
    @{{kicad_python}} {{hw}}/scripts/gen_charger_pcb.py 2>&1 | grep -v "swig/python detected a memory leak"
    @just route charger-board

# Schaltplan prüfen
erc board="main-board": (_out board)
    kicad-cli sch erc --exit-code-violations -o build/{{board}}/erc.rpt {{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_sch

# Platine prüfen, inkl. Abgleich mit dem Schaltplan
drc board="main-board": (_out board)
    kicad-cli pcb drc --schematic-parity --exit-code-violations -o build/{{board}}/drc.rpt {{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb

# Schaltplan als PDF
sch-pdf board="main-board": (_out board)
    kicad-cli sch export pdf -o build/{{board}}/{{"louie-" + replace(board, "-board", "")}}-schaltplan.pdf {{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_sch

# 3D-Ansichten als PNG (oben, unten, schräg oben, schräg unten)
render board="main-board": (_out board + "/render")
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb
    out=build/{{board}}/render
    kicad-cli pcb render --side top    --width 1600 --height 700 -o $out/top.png    $pcb
    kicad-cli pcb render --side bottom --width 1600 --height 700 -o $out/bottom.png $pcb
    kicad-cli pcb render --side top --rotate '-45,0,30' --zoom 1.3 --width 1600 --height 900 -o $out/iso.png $pcb
    kicad-cli pcb render --side bottom --rotate '45,0,-30' --zoom 1.3 --width 1600 --height 900 -o $out/iso-bottom.png $pcb

# Fertigungsdaten: Gerber, Bohrdaten, Bestückung, Stückliste (+ ZIP)
fab board="main-board": (erc board) (drc board) (_out board + "/fab/gerber")
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb
    sch={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_sch
    out=build/{{board}}/fab
    kicad-cli pcb export gerbers -o $out/gerber/ $pcb
    kicad-cli pcb export drill --format excellon --excellon-separate-th -o $out/gerber/ $pcb
    kicad-cli pcb export pos --format csv --units mm --side both -o $out/{{"louie-" + replace(board, "-board", "")}}-bestueckung.csv $pcb
    kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},LCSC Part' \
        --group-by 'Value,Footprint' -o $out/{{"louie-" + replace(board, "-board", "")}}-stueckliste.csv $sch
    rm -f $out/{{"louie-" + replace(board, "-board", "")}}-gerber.zip && zip -qj $out/{{"louie-" + replace(board, "-board", "")}}-gerber.zip $out/gerber/*
    echo "Fertigungsdaten in $out/"

# 3D-Druckteile (Hülle Hauptplatine, Halter Ladeplatine) als STL (build/mechanik/), Vorschau als PNG
stl: (_out "mechanik")
    #!/usr/bin/env bash
    set -euo pipefail
    scad={{hw}}/mechanik/huelle.scad
    for t in aa_schale kappe_plus kappe_minus c_huelse; do
        openscad -q -D "teil=\"druck_$t\"" -o build/mechanik/$t.stl $scad
    done
    for t in baugruppe baugruppe_c explosion; do
        openscad -q -D "teil=\"$t\"" --render --imgsize 1600,900 --viewall --autocenter \
            --camera 0,0,0,55,0,25,0 --colorscheme Tomorrow -o build/mechanik/$t.png $scad
    done
    # Halter der Ladeplatine (AA-Fach hochkant oder Basis)
    lade={{hw}}/mechanik/ladeplatine.scad
    for t in schale kappe_plus kappe_minus basis_halter; do
        openscad -q -D "teil=\"druck_$t\"" -o build/mechanik/lade_$t.stl $lade
    done
    openscad -q -D 'teil="baugruppe"' --imgsize 1600,900 --viewall --autocenter \
        --camera 0,0,0,60,0,210,0 --colorscheme Tomorrow -o build/mechanik/lade_baugruppe.png $lade
    openscad -q -D 'teil="baugruppe_basis"' --imgsize 1600,900 --viewall --autocenter \
        --camera 0,0,0,55,0,25,0 --colorscheme Tomorrow -o build/mechanik/lade_baugruppe_basis.png $lade
    echo "STL und Vorschau in build/mechanik/"

# 3D-Modell der Platine: STEP (CAD), GLB (Ansehen), STL (3D-Druck/OpenSCAD) in build/<platine>/3d/
modell board="main-board": (_out board + "/3d")
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

# Alle Bilder einer Platine neu erzeugen (docs/bilder/: 3D, Kupferlagen, Schaltplan; Ladeplatine mit Präfix lade-)
images board="main-board":
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_pcb
    sch={{hw}}/{{board}}/{{"louie-" + replace(board, "-board", "")}}.kicad_sch
    out=docs/bilder
    pre={{ if board == "main-board" { "" } else { "lade-" } }}
    tmp=$(mktemp -d)
    mkdir -p $out
    kicad-cli pcb render --side top    --width 1800 --height 700 -o $out/${pre}platine-oben.png  $pcb >/dev/null
    kicad-cli pcb render --side bottom --width 1800 --height 700 -o $out/${pre}platine-unten.png $pcb >/dev/null
    kicad-cli pcb render --side top    --rotate '-45,0,30'  --zoom 1.3 --width 1800 --height 1000 -o $out/${pre}platine-3d-oben.png  $pcb >/dev/null
    kicad-cli pcb render --side bottom --rotate '45,0,-30'  --zoom 1.3 --width 1800 --height 1000 -o $out/${pre}platine-3d-unten.png $pcb >/dev/null
    for L in F B; do
        mirror=""; [ $L = B ] && mirror="--mirror"
        kicad-cli pcb export svg --mode-single --layers $L.Cu,Edge.Cuts,$L.Fab --fit-page-to-board \
            --exclude-drawing-sheet $mirror -o $tmp/cu_$L.svg $pcb >/dev/null
        inkscape $tmp/cu_$L.svg -w 1800 -b white -o $out/${pre}kupfer-$( [ $L = F ] && echo oben || echo unten ).png 2>/dev/null
    done
    kicad-cli sch export pdf -o $tmp/sch.pdf $sch >/dev/null
    inkscape $tmp/sch.pdf -o $out/${pre}schaltplan.png -d 110 2>/dev/null
    if [ {{board}} = main-board ]; then
        {{kicad_python}} {{hw}}/scripts/plot_layout.py 2>&1 | grep -v "swig/python detected a memory leak" >/dev/null || true
        cp build/{{board}}/placement.png $out/platzierung.png
    fi
    rm -rf $tmp
    ls $out

# Erzeugte Ausgaben löschen (build/)
clean:
    rm -rf build

_out dir:
    @mkdir -p build/{{dir}}
