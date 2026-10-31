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
| Java | nur für den Autorouter Freerouting | z. B. `sudo apt install default-jre` | nein |

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
just outline       AA-Umriss der Hauptplatine setzen (Maße in hardware/scripts/board_outline.py)
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

## KiCad-Projekte

- Jede Platine hat ein eigenes Projekt unter `hardware/<platine>/`.
- Die Projekt-Bibliothekstabellen (`sym-lib-table`, `fp-lib-table`) verweisen relativ auf
  `${KIPRJMOD}/../lib/`. Nichts muss global in KiCad eingetragen werden.
- `*.kicad_prl` (lokale Ansichtseinstellungen) und Backups werden nicht eingecheckt.

## Fertigung

- `just fab` erzeugt herstellerneutrale Daten: Gerber mit klassischen Endungen, Excellon-Bohrdaten,
  Bestückungsliste (CSV) und Stückliste mit LCSC-Spalte.
- Für Hersteller mit eigenem Format (z. B. JLCPCB-Spaltennamen) werden die CSVs bei Bedarf angepasst.
