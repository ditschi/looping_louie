# Entwicklung

## Abhängigkeiten

Getestet unter Ubuntu 26.04. **Alles auf einmal einrichten:**

```bash
./setup.sh
```

Das Skript installiert nur, was fehlt, und kann jederzeit erneut ausgeführt werden.
Einzeln:

| Werkzeug | Zweck | Installation | Pflicht |
|---|---|---|---|
| KiCad ≥ 9 (inkl. `kicad-cli`, Python-Modul `pcbnew`) | Schaltplan, Layout, Prüfungen, Fertigungsdaten | `sudo apt install kicad` | ja |
| easyeda2kicad | Symbole, Footprints und 3D-Modelle von LCSC/JLC-Teilen holen | `uv tool install easyeda2kicad` | ja |
| just | Befehls-Runner (alle Entwicklungsbefehle) | `sudo apt install just` | ja |
| zip, python3 | ZIP der Gerber-Daten, Skripte | meist vorhanden | ja |
| kicad-packages3d | 3D-Modelle der KiCad-Standardbauteile (für Renders) | `sudo apt install kicad-packages3d` | empfohlen |
| Java ≥ 21 + Freerouting | Autorouter (`just route`); `setup.sh` lädt `tools/freerouting.jar` | `sudo apt install default-jre` | für Routing |
| python3-matplotlib | Platzierungsbild (`just plot`) | `sudo apt install python3-matplotlib` | ja |

Nach der Installation KiCad einmal mit Schaltplan- und Platineneditor öffnen, damit die globalen
Bibliothekstabellen angelegt werden. Dann:

```bash
just check
```

### Python

- Skripte, die die Platine bearbeiten (`board_outline.py`), brauchen das Modul `pcbnew` und laufen
  deshalb mit dem **System-Python** (`/usr/bin/python3`), in das das KiCad-Paket das Modul installiert.
  Anderer Pfad: `KICAD_PYTHON=/pfad/zu/python3 just outline`.
- `fetch_parts.py` braucht nur die Standardbibliothek und das Kommando `easyeda2kicad`.
- Es gibt bewusst keine virtuelle Umgebung: `pcbnew` lässt sich nicht per pip installieren.

## Befehle

```
just check         Werkzeuge prüfen
just parts         fehlende LCSC-Teile aus hardware/bom/teile.csv nach hardware/lib holen
just parts-update  alle LCSC-Teile neu holen
just symbols       projekteigene Symbole erzeugen (hardware/lib/louie.kicad_sym)
just schematic     Schaltplan der Hauptplatine aus dem Generator erzeugen (überschreibt!) + ERC
just outline       AA-Umriss der Hauptplatine setzen (Maße in hardware/scripts/board_outline.py)
just pcb           Schaltplan auf die Platine übertragen und platzieren (überschreibt Layout!)
just plot          Platzierung mit Luftlinien als Bild (build/main-board/placement.png)
just route         automatisch routen (Freerouting) und Masseflächen füllen
just erc           Schaltplan prüfen
just drc           Platine prüfen, inkl. Abgleich mit dem Schaltplan
just sch-pdf       Schaltplan als PDF
just render        3D-Ansichten als PNG
just fab           Fertigungsdaten (Gerber, Bohrdaten, Bestückung, Stückliste, ZIP)
just clean         build/ löschen
```

Alle Ausgaben landen in `build/<platine>/` (nicht im Git).

## Bauteile

- **Quelle der Wahrheit ist `hardware/bom/teile.csv`**: Funktion, Wert, Herstellerteil, Gehäuse,
  LCSC-Nummer, Alternativen, Status.
- Ziel: **gängige Teile**, die es bei mehreren Distributoren gibt (LCSC, Mouser, DigiKey, Reichelt …),
  damit man bei verschiedenen Platinenherstellern Angebote einholen kann.
- Passive Bauteile sind generisch (Widerstände, Kondensatoren in 0603/0805/1206) und kommen aus den
  KiCad-Standardbibliotheken. 0603 als kleinste Größe, damit alles auch von Hand lötbar bleibt.
- ICs, Module und Stecker kommen über `just parts` in die Projektbibliothek `hardware/lib/lcsc.*`.
  Die Bibliothek ist eingecheckt, das Projekt öffnet also auch ohne Internet.
- Neues Teil: Zeile in `teile.csv` ergänzen (`bibliothek` = `lcsc`, LCSC-Nummer eintragen), dann `just parts`.
- Die EasyEDA-API sperrt bei zu vielen Abfragen kurzzeitig (HTTP 403). Das Skript pausiert deshalb
  zwischen den Teilen; bei einer Sperre einfach später erneut aufrufen.

## Schaltplan

- Der erste Schaltplan der Hauptplatine wird von `hardware/scripts/gen_main_schematic.py` erzeugt.
  Die Schaltung steht dort als Python-Liste (Bauteile, Werte, Footprints, Pin → Netz).
  Jeder Pin bekommt ein Netz-Label, unbenutzte Pins ein No-Connect-Kreuz.
- Symbole: KiCad-Standardbibliothek, wo vorhanden. Eigene Symbole (ESP32-C3-MINI-1,
  DRV8833 im Parallelbetrieb) erzeugt `hardware/scripts/gen_symbols.py`, weil die LCSC-Symbole
  keine Pin-Typen haben und die ERC-Prüfung damit wertlos wäre.
- **Sobald der Schaltplan im KiCad-GUI bearbeitet wird, ist der GUI-Stand maßgeblich.**
  Dann `just schematic` nicht mehr aufrufen, es würde die Änderungen überschreiben.

## Layout

- `just pcb` überträgt den Schaltplan per Skript auf die Platine (`gen_main_pcb.py`): Footprints mit
  Netzen, Designregeln, Netzklasse „Power“ (0,6 mm), Antennen-Sperrflächen, Thermal-Vias, Masseflächen.
  Die Platzierung steht in `placement_zweiseitig.py` (bzw. `placement_einseitig.py` als Machbarkeitstest).
- `just plot` zeichnet Ober- und Unterseite mit Luftlinien und meldet Überlappungen.
- `just route` routet mit Freerouting. Danach `just drc` und im GUI nacharbeiten.
- **Wie beim Schaltplan gilt:** Sobald im GUI geroutet oder verschoben wird, ist der GUI-Stand
  maßgeblich; `just pcb` würde alles überschreiben.

## KiCad-Projekte

- Jede Platine hat ein eigenes Projekt unter `hardware/<platine>/`.
- Die Projekt-Bibliothekstabellen (`sym-lib-table`, `fp-lib-table`) verweisen relativ auf
  `${KIPRJMOD}/../lib/`. Nichts muss global in KiCad eingetragen werden.
- `*.kicad_prl` (lokale Ansichtseinstellungen) und Backups werden nicht eingecheckt.

## Fertigung

- `just fab` erzeugt herstellerneutrale Daten: Gerber mit klassischen Endungen, Excellon-Bohrdaten,
  Bestückungsliste (CSV) und Stückliste mit LCSC-Spalte.
- Für Hersteller mit eigenem Format (z. B. JLCPCB-Spaltennamen) werden die CSVs bei Bedarf angepasst.
