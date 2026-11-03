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
| Java ≥ 21 + Freerouting | Autorouter der Ladeplatine (`just route charger-board`, Hauptplatine optional `ROUTER=freerouting`); `setup.sh` lädt `tools/freerouting.jar` | `sudo apt install default-jre` | für Routing |
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
just pcb           Hauptplatine (4 Lagen) aus dem Schaltplan anlegen und platzieren (überschreibt Layout!)
just plot          Platzierung mit Luftlinien als Bild (build/main-board/placement.png)
just route         Hauptplatine routen: eigener Labyrinth-Router (route_fix.py), GND über die Innenlage In1,
                   danach Masseflächen füllen; just route charger-board routet die Ladeplatine mit Freerouting.
                   Optionen runs=N (Versuche), force=1 (Gate übergehen), siehe „Routing: bestes Ergebnis behalten“
just main-board    Hauptplatine komplett: anlegen, routen, ERC, DRC (alte Namen: just four-layer, just vierlagig)
just route-baseline  hardware/<platine>/routing.json aus der offiziellen Platine neu anlegen
just charger-schematic  Schaltplan der Ladeplatine erzeugen (überschreibt!) + ERC
just charger-pcb   Ladeplatine anlegen, platzieren und routen (überschreibt Layout!)
just erc           Schaltplan prüfen
just drc           Platine prüfen, inkl. Abgleich mit dem Schaltplan
just sch-pdf       Schaltplan als PDF
just render        3D-Ansichten als PNG
just images        Bilder nach docs/bilder/ (3D, alle vier Kupferlagen, Schaltplan, Platzierung; just images charger-board)
just modell        3D-Modell als STEP/GLB/STL (build/main-board/3d/, Hüllkurvenprüfung in hardware/mechanik/huelle.scad)
just fab           Fertigungsdaten (Gerber, Bohrdaten, Bestückung, Stückliste, ZIP)
just clean         build/ löschen
```

Rezepte mit `board`-Parameter (`erc`, `drc`, `route`, `render`, `images`, `modell`, `fab`, `sch-pdf`) nehmen ohne
Angabe die Hauptplatine (`main-board`, 4 Lagen); `charger-board` ist die Ladeplatine (2 Lagen).
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

- Die Hauptplatine hat **4 Lagen** (Entscheidung 2026-11-03; Lagenaufbau JLC04081H-3313, 0,8 mm; In1 = GND-Lage,
  In2 = Signale; [hauptplatine-c6.md](hauptplatine-c6.md) Kapitel 11). Die 2-Lagen-Variante ist verworfen und nur
  noch in Git (Commit c45c6de). Die Ladeplatine hat weiterhin 2 Lagen.
- `just pcb` legt die Platine per Skript neu an (`gen_main_pcb.py`): Umriss, Lagenaufbau, Footprints mit
  Netzen, Designregeln (auch `louie-main.kicad_dru`), Netzklassen, Antennen-Sperrflächen, Vorrouten, Thermal-Vias,
  Masseflächen auf allen Lagen. Die Platzierung steht in `placement.py` (alle Bauteile oben).
- `just plot` zeichnet Ober- und Unterseite mit Luftlinien und meldet Überlappungen.
- `just route` routet mit dem eigenen Router `route_fix.py` (`ROUTER=freerouting` als Alternative). Danach `just drc`.
- Wer `just pcb` aufruft, überschreibt die geroutete Platine; der alte Stand landet vorher in
  `build/<platine>/keep/before-pcb-<zeit>.kicad_pcb`.
- **Wie beim Schaltplan gilt:** Sobald im GUI geroutet oder verschoben wird, ist der GUI-Stand
  maßgeblich; `just pcb` würde alles überschreiben.

## Routing: bestes Ergebnis behalten

Die Router streuen stark (eigener Router auf 4 Lagen 0–5 offene Verbindungen; früher 2 Lagen/Freerouting 12–25). Damit ein
neuer Lauf kein besseres Ergebnis überschreibt, geht jedes `just route` durch ein Gate (`hardware/scripts/route_gate.py`):

1. **Versuche:** `just route main-board runs=10` startet 10 Versuche (Standard 6, parallel `ROUTE_PARALLEL`, Standard 3);
   der beste Versuch geht ins Gate.
2. **Kennzahlen** (kicad-cli-DRC als JSON + pcbnew), Rangfolge lexikografisch, kleiner ist besser:
   `drc_violations` (ohne Bibliotheksabgleich der Footprints), `unconnected`, `gnd_islands` (gefüllte Flächenstücke
   ohne Via/Durchsteckpad, nur über Bahnen angebunden), `via_count`, `track_length_mm`.
3. **Ergebnisdatei** `hardware/<platine>/routing.json` (eingecheckt): Fingerabdruck des Designs, `board_hash` der
   offiziellen Platine, Kennzahlen, Router und Variante, Zeitpunkt, Werkzeugversionen.
4. **Entscheidung:**
   - gleicher Fingerabdruck und besser → ersetzt `louie-*.kicad_pcb` und `routing.json`
   - gleicher Fingerabdruck, nicht besser → offizielle Platine bleibt; der Lauf landet unter
     `build/<platine>/route/rejected/<zeit>-<kennzahlen>.kicad_pcb`
     („Neuer Lauf: X offen, bisher Y → verworfen …“). Hat `just pcb` die offizielle Platine vorher überschrieben,
     stellt das Gate das bisherige Routing wieder her (aus `build/<platine>/keep/` oder Git).
   - anderer Fingerabdruck (Design geändert) → der beste Lauf wird offiziell, die Basis wird neu gesetzt
   - `just route <platine> force=1` übernimmt ohne Vergleich
   Jede übernommene Platine liegt zusätzlich als `build/<platine>/keep/accepted-<zeit>-<kennzahlen>.kicad_pcb`.

**Fingerabdruck:** SHA-256 über die *ungeroutete* Platine, wie `just pcb` sie schreibt (Platzierung, Vorrouten,
Flächen-Umrisse, Sperrflächen, Netze, Board-Setup) plus `board.design_settings`/`net_settings` aus der `.kicad_pro`
und die `.kicad_dru`. Vorher normalisiert: ohne UUIDs (auch in Pfaden), Generator-/Versionskennung,
Plot-Einstellungen und Flächenfüllungen; Elemente sortiert (KiCad sortiert beim Speichern nach UUID). Neu Speichern
oder neu Erzeugen ändert ihn also nicht, eine verschobene Bauteilposition schon.

Aus einer *gerouteten* Platine lässt er sich nicht berechnen: `route_fix.py` und `stitch.py` sperren ihre Bahnen und
Vias genauso wie die Vorrouten, „gesperrt“ unterscheidet also nicht Design und Routing. Deshalb gilt am Start eines
Laufs: Ist die Startplatine (normalisiert) die offizielle aus `routing.json` (`board_hash`, also erneutes
`just route` ohne `just pcb`), gilt deren gespeicherter Fingerabdruck; sonst ist die Startplatine die ungeroutete und
ihr Hash der Fingerabdruck. Eine im GUI geänderte geroutete Platine zählt damit als geändertes Design.

**Weitere Befehle:**

```
just route-baseline main-board        routing.json aus der offiziellen Platine anlegen (erzeugt die ungeroutete
                                      Platine dafür in einem temporären Ordner, prüft, dass Platzierung, Flächen,
                                      Regeln und alle Vorrouten zur offiziellen passen)
route_gate.py check <board> <datei>   eine Platine probeweise durchs Gate schicken (ohne --apply ändert es nichts)
route_gate.py fingerprint <datei>     Fingerabdruck/Inhalts-Hash einer Platine
route_gate.py measure <datei>         Kennzahlen einer Platine
```

Umgebungsvariablen (englische Namen; alte gehen weiter): `ROUTE_RUNS` (alt `FREEROUTING_ATTEMPTS`), `ROUTE_PARALLEL`
(alt `FREEROUTING_PARALLEL`), `ROUTER=own|freerouting` (Hauptplatine; alt `ROUTER=eigen`), `ROUTE_VARIANTS`,
`ROUTE_PLANE`, `ROUTE_GND`, `FREEROUTING_PASSES`, `FREEROUTING_JAR`. Die Arbeitsordner der Versuche heißen
`build/<platine>/route/attempt_<n>/`.

## KiCad-Projekte

- Jede Platine hat ein eigenes Projekt unter `hardware/<platine>/`.
- Die Projekt-Bibliothekstabellen (`sym-lib-table`, `fp-lib-table`) verweisen relativ auf
  `${KIPRJMOD}/../lib/`. Nichts muss global in KiCad eingetragen werden.
- `*.kicad_prl` (lokale Ansichtseinstellungen) und Backups werden nicht eingecheckt.

## Fertigung

- `just fab` erzeugt herstellerneutrale Daten: Gerber mit klassischen Endungen, Excellon-Bohrdaten,
  Bestückungsliste (CSV) und Stückliste mit LCSC-Spalte.
- Für Hersteller mit eigenem Format (z. B. JLCPCB-Spaltennamen) werden die CSVs bei Bedarf angepasst.
