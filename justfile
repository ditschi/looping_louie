# Looping Louie WLAN-Upgrade – Entwicklungsbefehle
# Übersicht: just --list

kicad_python := env("KICAD_PYTHON", "/usr/bin/python3")
hw := "hardware"
project := "louie-main"

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

# Schaltplan auf die Platine übertragen und platzieren (überschreibt Layout!), Variante: zweiseitig | einseitig
pcb variant="zweiseitig":
    @{{kicad_python}} {{hw}}/scripts/gen_main_pcb.py {{variant}} 2>&1 | grep -v "swig/python detected a memory leak"
    @just plot

# Platzierung mit Luftlinien als Bild (build/main-board/placement.png)
plot:
    @{{kicad_python}} {{hw}}/scripts/plot_layout.py 2>&1 | grep -v "swig/python detected a memory leak"

# Automatisch routen (Freerouting) und Masseflächen füllen
route:
    @{{kicad_python}} {{hw}}/scripts/route.py 2>&1 | grep -v "swig/python detected a memory leak"

# Schaltplan prüfen
erc board="main-board": (_out board)
    kicad-cli sch erc --exit-code-violations -o build/{{board}}/erc.rpt {{hw}}/{{board}}/{{project}}.kicad_sch

# Platine prüfen, inkl. Abgleich mit dem Schaltplan
drc board="main-board": (_out board)
    kicad-cli pcb drc --schematic-parity --exit-code-violations -o build/{{board}}/drc.rpt {{hw}}/{{board}}/{{project}}.kicad_pcb

# Schaltplan als PDF
sch-pdf board="main-board": (_out board)
    kicad-cli sch export pdf -o build/{{board}}/{{project}}-schaltplan.pdf {{hw}}/{{board}}/{{project}}.kicad_sch

# 3D-Ansichten als PNG (oben, unten, schräg)
render board="main-board": (_out board + "/render")
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{project}}.kicad_pcb
    out=build/{{board}}/render
    kicad-cli pcb render --side top    --width 1600 --height 700 -o $out/top.png    $pcb
    kicad-cli pcb render --side bottom --width 1600 --height 700 -o $out/bottom.png $pcb
    kicad-cli pcb render --side top --rotate '-45,0,30' --zoom 1.3 --width 1600 --height 900 -o $out/iso.png $pcb

# Fertigungsdaten: Gerber, Bohrdaten, Bestückung, Stückliste (+ ZIP)
fab board="main-board": (erc board) (drc board) (_out board + "/fab/gerber")
    #!/usr/bin/env bash
    set -euo pipefail
    pcb={{hw}}/{{board}}/{{project}}.kicad_pcb
    sch={{hw}}/{{board}}/{{project}}.kicad_sch
    out=build/{{board}}/fab
    kicad-cli pcb export gerbers -o $out/gerber/ $pcb
    kicad-cli pcb export drill --format excellon --excellon-separate-th -o $out/gerber/ $pcb
    kicad-cli pcb export pos --format csv --units mm --side both -o $out/{{project}}-bestueckung.csv $pcb
    kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},LCSC Part' \
        --group-by 'Value,Footprint' -o $out/{{project}}-stueckliste.csv $sch
    rm -f $out/{{project}}-gerber.zip && zip -qj $out/{{project}}-gerber.zip $out/gerber/*
    echo "Fertigungsdaten in $out/"

# Erzeugte Ausgaben löschen (build/)
clean:
    rm -rf build

_out dir:
    @mkdir -p build/{{dir}}
