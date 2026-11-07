# Routing-Qualität bewerten: harte Bedingungen + gewichteter Score

Stand 2026-11-04. **Umgesetzt** (Gewichte aus Abschnitt 3 vom Auftraggeber bestätigt): `hardware/scripts/route_score.py`
(Messung, `evaluate()`, `decide()`, Bericht), Konfiguration `hardware/routing-score.toml`, eingebaut in
`route_gate.py` (Gate, `just score`, `just explain`) und `route.py` (bester Versuch eines Aufrufs). Bedienung:
[entwicklung.md](entwicklung.md), Abschnitt „Routing: bestes Ergebnis behalten“. Abschnitte 1–4 beschreiben die
geltenden Regeln; Abschnitt 5 und 8 sind die Prototyp-Messung vom 2026-11-03 (Historie, vor dem Umbau der Platine).

**Abweichungen der Umsetzung vom Vorschlag:**
- `tight_clearance` zählt die beteiligten Elemente (Bahnen, Vias, Pads), nicht die gemeldeten Paare. Welche Paare
  kicad-cli 9.0.8 meldet, schwankt bei gleicher Platine von Lauf zu Lauf um ±2 % (228–232), die Elemente nicht (275).
  Skala unverändert 10.
- Board-Wissen (Netze, Antenne, Via-in-Pad-Liste, Modul, Strompfade) steht unter `[boards.<platine>]`; die
  allgemeinen Abschnitte sind Vorgaben. `thermal_vias_u2` heißt `thermal_vias` (Pad aus `[boards.*.module]`).
- `routing.json` speichert zusätzlich `details` und `score.parts`; `ranking` entfällt (`"decision": "hard+weighted"`).
- Befund 8.1 (VSYS-Pfad zu schmal) und 8.3 (Netzklassen) sind behoben: `gen_main_pcb.py` routet Q1 → C1/C2 mit 0,5 mm
  nur auf den Außenlagen vor, `route_fix.py` routet VSYS nie unter 0,3 mm, die Netzklassen werden beim Erzeugen neu
  gesetzt (hauptplatine-c6.md 11.7).

**Prüfung der Umsetzung (2026-11-04, Platine vor dem Umbau):** `just score main-board
build/main-board/keep/variant4-0-open.kicad_pcb` → wie im Prototyp gewinnt die offizielle Platine: beide verletzen
`power_width_violations`, Verletzung 1/10,0 mm gegen 1/23,0 mm → VERWERFEN; weich ΔS = +3,77 für variant4 (mit der
neuen `tight_clearance`-Zählung; Prototyp +3,07), Robustheit 0,5 % „übernehmen“. Ein bytegleicher Stand
(`best-0-open`) ergibt ΔS = 0,00.

## Kurzfassung

- **Heute** vergleicht das Gate lexikografisch (`drc_violations`, `unconnected`, `gnd_islands`, `via_count`,
  `track_length_mm`). Die erste Kennzahl mit einem Unterschied entscheidet allein. Dabei zählen eine GND-Insel
  mehr als beliebig viele Vias und Millimeter. Für Strompfade, Messleitungen, Antenne und Rückstromweg gibt es
  gar keine Kennzahl.
- **Vorschlag:** drei Stufen.
  1. **Harte Bedingungen** (DRC-Fehler, offene Verbindungen, Kupfer in der Antennen-Sperrfläche, zu schmale
     Strompfade). Wer sie verletzt, ist unzulässig. Sind beide Platinen unzulässig, gewinnt die kleinere
     Verletzung (Regel nach Deb).
  2. **Gewichtete Summe** der weichen Kennzahlen: `S = Σ weight_i · value_i / scale_i`.
     - `scale` legt fest, ab welcher Größe ein Unterschied als „ein Punkt“ zählt (fest, in Einheiten).
     - `weight` ist die Wichtigkeit und wird vom Nutzer gesetzt.
  3. **Schwelle und Veto.** Ein Kandidat ersetzt die offizielle Platine nur, wenn er um mindestens
     `min_improvement` Punkte besser ist (Standard 1,0). Einzelne kritische Kennzahlen dürfen sich zusätzlich
     nicht um mehr als `max_regression` verschlechtern.
  - Jeder Lauf schreibt einen **Sensitivitätsbericht**: Beitrag je Kennzahl, Anteil, „Kipp-Faktor“ des Gewichts,
    Robustheit gegen zufällige Gewichte und eine Pareto-Sicht.
- **Machbar:** Alle vorgeschlagenen Kennzahlen lassen sich mit `kicad-cli pcb drc` (JSON) und `pcbnew` (KiCad 9.0.8)
  automatisch berechnen. Die Messung dauert **3,5 s pro Platine**, einschließlich zweier DRC-Läufe.
- **Ergebnis 4 Lagen:** Die offizielle Platine (Versuch 3) gewinnt gegen `variant4-0-open`.
  - Ihre Verletzung der harten Bedingung ist kleiner: 10 statt 23 mm zu schmale Bahn im Batterie-Motorpfad.
  - Auch im weichen Score ist sie besser: ΔS = +3,07 für variant4. Variant4 führt zu längeren Messleitungen,
    mehr Vias und mehr Länge; dagegen steht 1 GND-Insel weniger.
  - Robust: In 98,9 % von 2000 zufälligen Gewichtssätzen (jedes Gewicht ×0,5 bis ×2) bleibt die offizielle
    Platine vorne.
  - **Das heutige lexikografische Gate hätte variant4 gewählt** (GND-Inseln 1 < 2).
- **Befund nebenbei (wichtig, beide 4-Lagen-Stände):**
  - Der Batteriestrom zum Motor (Q1 → VSYS → DRV8213 VM) läuft über Bahnen von **0,2–0,3 mm**, zum Teil auf
    In2 (0,5 oz).
  - Ursache: `route_fix.py` routet VSYS mit `WIDTHS["/VSYS"] = (0.3, 0.2)`.
  - Bei 2 A sind das 56 mV (offiziell) bzw. 89 mV (variant4) Spannungsabfall. Nach IPC-2221 trägt der Pfad
    weit weniger als 1,5 A Dauerstrom.
  - Die 2-Lagen-Platine (Freerouting, Netzklasse Power 0,4 mm) hat das Problem nicht. Abschnitt 8.

## 1. Warum nicht lexikografisch?

| | Lexikografisch (heute) | Harte Bedingungen + gewichtete Summe |
|---|---|---|
| Ausgleich zwischen Zielen | keiner: 1 Insel weniger schlägt +8 Vias, +36 mm, +19 mm Messleitung | ausdrücklich, über Gewichte |
| Neue Kennzahlen | jede neue Kennzahl hinten wirkt praktisch nie | jede wirkt nach ihrem Gewicht |
| Nachvollziehbar | sehr (eine Kennzahl entscheidet) | mit Beitragstabelle ebenso |
| Rauschen | kleinste Unterschiede (1 Via, 0,1 mm) ersetzen die Platine | Schwelle `min_improvement` |
| Gefahr | wichtige Eigenschaften (Strompfad, Antenne) fehlen ganz | Kompensation: viele kleine Gewinne verdecken einen echten Schaden → harte Bedingungen + Veto |
| Einstellen | Reihenfolge | Gewichte (Skalen bleiben fest) |

**Lexikografisch bleibt richtig für die harten Bedingungen.** Was auf keinen Fall passieren darf, wird nicht
gegen anderes verrechnet. Deshalb gelten die harten Bedingungen zuerst und die Summe nur unter den zulässigen
Platinen. Das entspricht den Zulässigkeitsregeln von Deb (2000) aus der Optimierung mit Nebenbedingungen:
- zulässig schlägt unzulässig;
- von zwei unzulässigen gewinnt die mit der kleineren Gesamtverletzung;
- von zwei zulässigen gewinnt der bessere Zielwert.

Freerouting verfährt intern ähnlich. Die Router-Bewertung zieht Punkte für offene Verbindungen und
Abstandsverletzungen ab. Der Optimierer gewichtet Mehrlänge (1000), Mehr-Vias (2000) und Knicke (500) gegen
untere Schranken. Er nimmt keinen Schritt an, der Verbindungen verliert oder DRC-Fehler erzeugt, und hört auf,
sobald ein Schritt weniger als 1 % bringt.

### Normierung: feste Skalen statt Verhältnis zur Basis

- **Verhältnis zur offiziellen Platine** (`value/value_official`):
  - Bei Basis 0 (GND-Inseln, Rückstromlücken auf 4 Lagen) ist es undefiniert.
  - Jede neue offizielle Platine verschiebt die Bedeutung aller Gewichte.
  - Abgelehnt.
- **Feste Skala** (`value/scale`): `scale` sagt, wie viel einer Größe ungefähr gleich schlimm ist.
  - Standardwerte: 10 Signal-Vias ≈ 50 mm Signalbahn ≈ 1 GND-Insel ≈ 5 mm Messleitung neben dem Motor ≈ 20 mV
    Abfall.
  - Gewichte bleiben über viele Läufe vergleichbar. Gewählt.
- Der Bericht zeigt trotzdem die Prozentänderung gegenüber der Basis, damit man sich die Größen besser
  vorstellen kann.

### Dass eine Kennzahl allein dominiert, wird verhindert durch

1. **Skalen**, die einen „spürbaren Unterschied“ beschreiben (nicht 1 mm, nicht 1 Via);
2. **Entscheidung über ΔS** zur offiziellen Platine statt über den absoluten S. Konstante Anteile wie die
   230 Fine-Pitch-Engstellen der Vorrouten heben sich dadurch auf.
3. die Spalte **Anteil** im Bericht. Liegt eine Kennzahl dauerhaft über ca. 50 %, ist ihre Skala zu klein
   gewählt.
4. **Veto** (`max_regression`) für Antenne, Strompfad und Messleitungen. Diese lassen sich nicht durch viele
   kleine Gewinne an anderer Stelle „abkaufen“.

### Gleichstand und Rauschen

- Die Messung ist deterministisch: gleicher Stand, gleiche Zahlen. Gestreut wird nur beim Routen (11.4 in
  hauptplatine-c6.md).
- Die Schwelle `min_improvement = 1,0` Punkt verhindert, dass ein praktisch gleichwertiger Lauf die eingecheckte
  Platine ersetzt. Das hält die Git-Historie ruhig und schützt eine im GUI geprüfte Platine.
- Bei |ΔS| < 1,0 bleibt die offizielle Platine; es gibt keinen weiteren Tie-Break.
- 1,0 Punkt entspricht bei den Standardgewichten z. B. 5 Signal-Vias, 50 mm Signalbahn oder 1/3 GND-Insel.

### Pareto-Sicht

Der Bericht prüft für alle Läufe eines Aufrufs und die offizielle Platine, ob eine andere in **allen** weichen
Kennzahlen mindestens gleich und in einer besser ist („dominiert“).
- Nicht dominierte Läufe sind echte Kompromisse. Erst dort entscheiden die Gewichte.
- Der Sieger einer gewichteten Summe mit positiven Gewichten ist immer Pareto-optimal.
- Umgekehrt findet eine gewichtete Summe nicht jeden Kompromiss: Punkte in nicht-konvexen Teilen der Front
  erreicht sie nicht (Das & Dennis 1997). Deshalb listet der Bericht die nicht dominierten Läufe mit auf, und
  man kann einen davon von Hand übernehmen (`force=1`).
- Im Prototyp sind alle drei Platinen nicht dominiert. Jede ist irgendwo besser, die Gewichte sind also nötig.

### Sensitivität

Je Kennzahl gibt der Bericht aus:
- **Punkte** `weight·(neu − alt)/scale` und **Anteil** an der Summe der Beträge;
- **Kipp-Faktor**: Mit welchem Faktor müsste man das Gewicht dieser einen Kennzahl multiplizieren, damit die
  Entscheidung kippt? Beispiel: „gnd_islands ×2,36“ heißt, mit Gewicht 7,1 statt 3 hätte variant4 gewonnen.
  „-“ heißt, diese Kennzahl allein kann die Entscheidung nicht kippen.
- **Robustheit**: Anteil von 2000 zufälligen Gewichtssätzen (jedes Gewicht log-gleichverteilt ×0,5 bis ×2),
  bei denen der Kandidat angenommen würde. Unter ca. 10 % oder über 90 % ist die Entscheidung stabil.

## 2. Kennzahlen

Gerechnet wird mit `kicad-cli pcb drc --format json --severity-all` (Schema `drc.v1.json`) und `pcbnew`
(KiCad 9, SWIG). Die Flächen werden im Speicher neu gefüllt (`ZONE_FILLER`), die Datei bleibt unverändert.
Spalte **Art**: H = hart (Grenzwert), W = weich (Gewicht/Skala), I = nur Information.

| Kennzahl (`key`) | Definition, Berechnung | Einheit | Art | Skala | Gewicht | Begründung Gewicht |
|---|---|---|---|---:|---:|---|
| `drc_errors` | DRC-Verstöße mit Schwere *error*, ohne Bibliotheksabgleich (wie heute) | Anzahl | H ≤ 0 | – | – | nicht fertigbar/prüfbar |
| `unconnected` | `unconnected_items` des DRC | Anzahl | H ≤ 0 | – | – | Funktion |
| `antenna_intrusions` | Bahn-/Via-Stücke fremder Netze in einer Sperrfläche `Antenne*` (auf deren Lagen), dazu Flächenfüllung darin > 0,01 mm²; erlaubt: `OUT_A` (Randstreifen zu BT1) | Anzahl | H ≤ 0 | – | – | Espressif: kein Kupfer unter der Antenne auf allen Lagen |
| `power_width_violations` | Je definiertem Strompfad (Pad → Pad, Tabelle 3) der Weg mit dem kleinsten Widerstand durch Bahnen/Vias (Dijkstra). Verletzung, wenn mehr als `neckdown_allow_mm` = 2 mm Bahn schmaler sind als nach IPC-2221 für `current_a` bei 20 K nötig | Anzahl Pfade | H ≤ 0 | – | – | Erwärmung, Motorstrom bis 2 A (IPROPI-Grenze) |
| `drc_warnings` | übrige DRC-Meldungen (lose Bahnen/Vias, Silk …) | Anzahl | W | 1 | 2 | jede ist Nacharbeit |
| `gnd_islands` | GND-Flächenstücke ohne Via/Durchsteckpad (wie heute) | Anzahl | W | 1 | 3 | hängen nur an SMD-Pads/Bahnen, schwache Masse |
| `signal_vias` | Vias außer GND | Anzahl | W | 10 | 2 | Lagenwechsel = Antipad in L2, Platz, Induktivität. **GND-Vias werden nicht bestraft** (heute zählen sie in `via_count` mit) |
| `signal_length_mm` | Bahnlänge außer GND | mm | W | 50 | 1 | Umwege, Kopplung, Fläche |
| `detour_worst5` | Mittel der 5 schlechtesten Netze: geroutete Länge / oktilinearer Minimalbaum der Pads (45°-Abstand `max+0,414·min`) | Verhältnis | W | 0,5 | 1 | findet einzelne irre Umwege, die in der Gesamtlänge untergehen |
| `bends` | Richtungswechsel zwischen Bahnen gleichen Netzes/gleicher Lage (außer GND) | Anzahl | W | 50 | 0,5 | Optik, Handnacharbeit, geringe elektrische Wirkung |
| `acute_angles` | Stöße gleichen Netzes unter 90° | Anzahl | W | 1 | 1 | Säurefallen (acid traps) |
| `overlapping_segments` | Bahnen gleichen Netzes, die übereinander zurücklaufen (Winkel ≈ 0°) | Anzahl | W | 1 | 0,5 | Router-Rest, Aufräumen |
| `via_in_pad` | Via in SMD-Pad, außer Liste (`U1:*` Modul-GND, `U2:*` Thermal-Pad) | Anzahl | W | 1 | 2 | Lot wird abgesaugt, kein gefülltes Via bestellt |
| `tight_clearance` | Zweiter DRC mit Zusatzregel „Abstand ≥ clearance + 0,05 mm“ für Bahn/Via/Pad (nicht Fläche, nicht Pad–Pad); Anzahl Verstöße | Anzahl | W | 10 | 1 | Fertigungsreserve; konstante Anteile (Fine-Pitch-Vorrouten) heben sich in ΔS auf |
| `power_drop_mv` | größter Spannungsabfall der Strompfade bei `peak_a`: Σ ρ·L/(w·t) je Bahn (t aus dem Lagenaufbau) + Via-Hülse (20 µm) | mV | W, Veto +30 | 20 | 2 | Motorleistung, Brown-out bei Anlauf |
| `sense_coupling_mm` | Länge der Messnetze (ISEN, ISEN_ADC, VBAT_ADC), die näher als 0,6 mm (Kante–Kante) an OUT_A/OUT_B liegt, auf gleicher Lage oder auf Lagen ohne GND-Ebene dazwischen | mm | W, Veto +5 | 5 | 3 | PWM-Flanken koppeln in die ADC-/IPROPI-Leitung |
| `sense_length_mm` | Gesamtlänge der Messnetze | mm | W | 10 | 1 | Antenne für Störungen, IPROPI-Knoten hochohmig |
| `return_gap_mm` | Länge von Signalbahnen ohne GND unter sich. Mit Ebene: Füllung der nächsten Ebene (4 Lagen: In1) muss unter dem Punkt liegen. Ohne Ebene (2 Lagen): Nachbarlage. Das eigene Via-Antipad zählt nicht | mm | W | 2 | 3 | Rückstromweg, EMV, USB |
| `antenna_proximity_mm` | Signalbahn (nicht GND, nicht erlaubt) innerhalb von 2 mm um die Antennen-Sperrflächen | mm | W, Veto +3 | 5 | 2 | Verstimmung/Einkopplung der Antenne |
| `stitch_gap_p95_mm` | 95-%-Wert des Abstands von GND-Füllung der Außenlagen (0,25-mm-Raster) zum nächsten GND-Via/Durchsteckpad | mm | W | 1 | 1 | Flächenzipfel ohne Anbindung (Resonanz, Rückstrom) |
| `gnd_vias_module` | GND-Vias im Umkreis von 1 mm um das Modul | Anzahl | W (−) | 4 | −0,5 | Espressif: viele GND-Vias am Modul; negativ = mehr ist besser |
| `usb_vias` | Vias auf USB_D+/D− | Anzahl | W | 2 | 1 | Lagenwechsel im Paar |
| `usb_skew_mm` | Längendifferenz D+/D− | mm | W | 5 | 0,5 | Full Speed (4–20 ns Flanken) unkritisch, Espressif nennt trotzdem gleiche Länge |
| `usb_stubs` | offene Bahnenden auf D+/D− (nicht an Pad/Via/Bahn) | Anzahl | W | 1 | 1 | ESD durchgeschleift lassen (Kapitel 10) |
| `ref_plane_mm2` | Fläche der GND-Ebene (In1) | mm² | I | 10 | 0 | korreliert mit `signal_vias` (Antipads) |
| `thermal_vias_u2`, `gnd_vias`, `via_count`, `track_length_mm`, `detour_total`, `stitch_gap_max_mm`, `layer_length_mm`, `usb_len_*` | zur Information und für den Vergleich mit heute | – | I | – | 0 | – |

**Nicht aufgenommen:**
- **Impedanz:** USB-FS ist vorgeroutet. Sie wäre nur mit Feldlöser sinnvoll.
- **Silk:** Silk-Meldungen laufen über `drc_warnings`.
- **Paralleler Lauf USB:** Das Paar ist vorgeroutet und in allen Läufen gleich.
- **Thermik des DRV8213 über Fläche:** Die Thermal-Vias legt der Generator fest. `thermal_vias_u2` steht nur
  zur Information im Bericht.

## 3. Konfigurationsdatei (Vorschlag `hardware/routing-score.toml`)

Englische Schlüssel. Der Nutzer ändert normalerweise nur `weight` (und `min_improvement`). `scale` und der
Board-Teil ändern sich nur, wenn sich das Design ändert.

```toml
version = 1

[decision]
min_improvement = 1.0   # Punkte; ~5 Signal-Vias oder 50 mm Signalbahn

[hard]                  # Kennzahl = höchster zulässiger Wert
drc_errors = 0
unconnected = 0
antenna_intrusions = 0
power_width_violations = 0

# weight: Wichtigkeit (0 = nur Bericht, 1 normal, 3 wichtig, 5 kritisch, negativ = mehr ist besser)
# scale:  so viel der Größe zählt als ein Punkt (vor Gewichtung)
# max_regression: optionales Veto gegenüber der offiziellen Platine
[soft]
drc_warnings         = { weight = 2.0,  scale = 1 }
gnd_islands          = { weight = 3.0,  scale = 1 }
signal_vias          = { weight = 2.0,  scale = 10 }
signal_length_mm     = { weight = 1.0,  scale = 50 }
detour_worst5        = { weight = 1.0,  scale = 0.5 }
bends                = { weight = 0.5,  scale = 50 }
acute_angles         = { weight = 1.0,  scale = 1 }
overlapping_segments = { weight = 0.5,  scale = 1 }
via_in_pad           = { weight = 2.0,  scale = 1 }
tight_clearance      = { weight = 1.0,  scale = 10 }
power_drop_mv        = { weight = 2.0,  scale = 20, max_regression = 30 }
sense_coupling_mm    = { weight = 3.0,  scale = 5,  max_regression = 5 }
sense_length_mm      = { weight = 1.0,  scale = 10 }
return_gap_mm        = { weight = 3.0,  scale = 2 }
antenna_proximity_mm = { weight = 2.0,  scale = 5,  max_regression = 3 }
stitch_gap_p95_mm    = { weight = 1.0,  scale = 1 }
gnd_vias_module      = { weight = -0.5, scale = 4 }
usb_vias             = { weight = 1.0,  scale = 2 }
usb_skew_mm          = { weight = 0.5,  scale = 5 }
usb_stubs            = { weight = 1.0,  scale = 1 }
ref_plane_mm2        = { weight = 0.0,  scale = 10 }

[nets]
gnd = "/GND"
power = ["/VSYS", "/BAT_IN", "/VBUS_J4", "/OUT_A", "/OUT_B", "/+3V3"]
sense = ["/ISEN", "/ISEN_ADC", "/VBAT_ADC"]
aggressors = ["/OUT_A", "/OUT_B"]
usb_pair = ["/USB_D+", "/USB_D-"]
coupling_gap_mm = 0.6
clearance_margin_mm = 0.05

[antenna]
area_prefix = "Antenne"
allowed_nets = ["/OUT_A"]
margin_mm = 2.0

[via_in_pad]
allowed = ["U2:*", "U1:*"]

[thermal]
copper_rise_k = 20
ipc_k_external = 0.048
ipc_k_internal = 0.024      # IPC-2221 konservativ; IPC-2152-Daten erlauben etwa 0,048
neckdown_allow_mm = 2.0     # Stiche an Fine-Pitch-Pins (DRV8213 0,3 mm)
resistivity_ohm_m = 1.72e-8
via_plating_um = 20

[[paths]]                   # current_a: Dauerstrom (Breite), peak_a: Spitze (Abfall)
name = "OUT_A U2 -> BT1"
from = "U2:2"
to = "BT1:1"
current_a = 1.5
peak_a = 2.0
# ebenso: OUT_B U2:3 -> BT2:1, VSYS D2:1 -> U2:1, VBUS J4:A4 -> D2:2, BAT J5:1 -> Q1:3, VSYS Q1:2 -> U2:1
```

**Strompfade:** 1,5 A Dauerstrom bei 20 K ergeben nach IPC-2221 mindestens **0,35 mm** außen (35 µm). Innen
(15,2 µm) sind es 2,07 mm mit k = 0,024 bzw. 0,80 mm mit k = 0,048. **Motorstrom gehört also auf die
Außenlagen.** Die 2 A sind die IPROPI-Stromgrenze (R1 1,24 k). Dauerstrom und Erwärmung sind nicht gemessen
(unsicher): Erst eine Strommessung am Motor (hardware-konzept.md, offene Punkte) liefert belastbare Werte für
`current_a`.

## 4. Bericht

`route_gate.py` gibt bei jeder Entscheidung aus (Beispiel aus dem Prototyp):

```
board           hard under_mm        S      dS  lexicographic(old gate)
4l-official        1     10.0    96.19   +0.00  (0, 0, 2, 116, 640.16)   hard: power_width_violations
4l-variant4        1     23.0    99.26   +3.07  (0, 0, 1, 124, 676.33)   hard: power_width_violations

=== 4l-variant4 vs 4l-official: REJECT (both infeasible, violation 1/23.0 mm vs 1/10.0 mm)
  metric                     official  candidate   points   share  flip-factor
  gnd_islands                       2          1    -3.00    23%  x2.36
  sense_length_mm               45.41      64.59    +1.92    15%  -
  tight_clearance                 230        245    +1.50    12%  -
  return_gap_mm                   0.3       1.08    +1.17     9%  -
  acute_angles                      3          4    +1.00     8%  -
  overlapping_segments             10          8    -1.00     8%  x5.07
  signal_vias                      70         74    +0.80     6%  -
  power_drop_mv                  81.6       88.8    +0.72     6%  -
  signal_length_mm              606.4      632.3    +0.52     4%  -
  gnd_vias_module                  26         30    -0.50     4%  x9.14
  detour_worst5                 2.021      2.217    +0.39     3%  -
  sense_coupling_mm              1.67       1.16    -0.31     2%  x14.31
  bends                           252        237    -0.15     1%  x28.15
  stitch_gap_p95_mm              3.29        3.3    +0.01     0%  -
  sum                                               +3.07
  robustness: soft decision 'accept' in 1.1 % of 2000 random weight sets (x0.5..x2)

Pareto (soft metrics with weight != 0):
  4l-official    non-dominated
  4l-variant4    non-dominated
```

Die Kurzzeile im Log bleibt wie heute, zum Beispiel:
`Neuer Lauf: S 99,3 (+3,1), hart 1 → verworfen (größere Verletzung power_width; Haupttreiber gnd_islands −3,0 / sense_length +1,9)`.

## 5. Prototyp-Ergebnisse (2026-11-03)

Gemessen wurden drei Platinen:
- **2 Lagen:** Commit c45c6de;
- **4 Lagen offiziell:** jetzt `hardware/main-board/louie-main.kicad_pcb`, inhaltsgleich mit dem früheren
  `main-board-4l`;
- **4 Lagen variant4:** `build/main-board-4l/keep/variant4-0-open.kicad_pcb`.

Für jede galten die eigenen Projektregeln. Die Kennzahlen des heutigen Gates stimmen mit `routing.json` überein
(116 Vias, 640,16 mm, 2 Inseln).

| Kennzahl | 4L offiziell | 4L variant4 | 2L (c45c6de) |
|---|---:|---:|---:|
| drc_errors / unconnected | 0 / 0 | 0 / 0 | 0 / **13** |
| power_width_violations (zu schmal) | **1** (9,98 mm) | **1** (23,0 mm) | 0 |
| gnd_islands | 2 | **1** | 2 |
| signal_vias / gnd_vias | **70** / 46 | 74 / 50 | 29 / 44 |
| signal_length_mm | **606,4** | 632,3 | 387,8 |
| detour_worst5 | **2,02** | 2,22 | 1,51 |
| bends / acute / overlapping | 252 / **3** / 10 | **237** / 4 / **8** | 152 / 14 / 5 |
| via_in_pad (C15:2, J1:4, J5:2 ×2) | 4 | 4 | 11 |
| tight_clearance | **230** | 245 | 41 (Regel 0,13) |
| power_drop_mv (max, 2 A) / Q1→VM | 81,6 / **56,2** | 81,6 / 88,8 | 81,6 / 36,5 |
| sense_coupling_mm | 1,67 | **1,16** | 1,66 |
| sense_length_mm | **45,4** | 64,6 | 21,4 |
| return_gap_mm | **0,3** | 1,1 | 78,2 (USB 28 mm) |
| antenna_intrusions / proximity_mm | 0 / 1,5 | 0 / 1,5 | 0 / 5,9 |
| stitch_gap_p95_mm | **3,29** | 3,30 | 3,85 |
| gnd_vias_module | 26 | **30** | 27 |
| usb_skew_mm / usb_vias / usb_stubs | 7,2 / 6 / 0 | 7,2 / 6 / 0 | 7,2 / 6 / 0 |
| **S** (Standardgewichte) | **96,2** | 99,3 | 201,9 |

**Welcher 4-Lagen-Stand gewinnt? Die offizielle Platine (Versuch 3).**
1. **Harte Stufe:** Beide verletzen `power_width_violations`, Pfad Q1 → U2 VM. Nach Deb entscheidet die kleinere
   Verletzung: offiziell 10 mm zu schmal (min. 0,2 mm, 3 Vias, 28 mΩ), variant4 23 mm (min. 0,25 mm, 5 Vias,
   44 mΩ).
2. **Weiche Stufe** (falls man den Pfad ausklammert): ΔS = +3,07 für variant4, also klar über der Schwelle.
   - Gegen variant4 sprechen: Messleitungen +19 mm, ISEN_ADC-Umweg 2,9×, +15 Engstellen, +4 Signal-Vias,
     +26 mm, Abfall +7 mV.
   - Für variant4 sprechen: 1 GND-Insel weniger (−3 Punkte), 2 Doppelbahnen weniger, 4 GND-Vias mehr am Modul.
3. **Robustheit:** 98,9 % der zufälligen Gewichtssätze behalten die offizielle Platine. Kippen würde es nur,
   wenn `gnd_islands` mehr als das 2,4-Fache wiegt (Gewicht > 7).
4. **Heutiges Gate:** Es hätte variant4 genommen, weil `gnd_islands` (1 < 2) vor Vias und Länge entscheidet.

Der 2-Lagen-Stand ist ein anderes Design (anderer Fingerabdruck) und wird im Gate nie gegen 4 Lagen
verglichen. Er dient hier nur als Plausibilitätsprobe:
- Die Kennzahl für den Rückstromweg erkennt die zerschnittene Unterseite (78 mm ohne Bezug, davon 28 mm USB).
- Die Strompfade sind dort breit genug (Freerouting, Netzklasse Power 0,4 mm).

## 6. Einbau in `route_gate.py` (Plan, nach Bestätigung der Gewichte)

1. **Neues Modul** `hardware/scripts/route_score.py`: `measure_all(pcb, cfg)` (Inhalt von `score_metrics.py`),
   `evaluate(cfg, metrics, details)` → `(hard_excess, hard_total, under_mm, S, parts)`,
   `decide(cfg, cand, official)` → `(accept, reason, report_lines)`. Konfiguration `hardware/routing-score.toml`;
   optional pro Platine `[boards.main-board]` für Netze und Pfade.
2. **`route_gate.measure()`** ruft `measure_all()` auf. Die bisherigen fünf Kennzahlen bleiben im Ergebnis
   (`via_count`, `track_length_mm` …), damit `short()`/`slug()` und alte `routing.json` lesbar bleiben.
3. **`rank()`** wird durch `decide()` ersetzt. `route.py` wählt den besten Versuch eines Aufrufs mit derselben
   Funktion: erst zulässig, dann kleinste Verletzung, dann kleinster S. Dazu kommt eine Pareto-Liste im Log.
4. **`routing.json`** bekommt zusätzlich:
   - `"score": {"S": …, "hard": …, "parts": {…}}`;
   - `"score_config_sha256"` (Hash der TOML);
   - `"metrics_version"`;
   - `"details"` (Pfade, schlechteste Netze).
   `"ranking"` entfällt bzw. wird `"decision": "hard+weighted"`.
5. **Neu messen statt gespeicherten Werten trauen:** Weicht `score_config_sha256` oder `metrics_version` ab
   (neue Gewichte, neue Kennzahl), misst das Gate die offizielle Platine neu (3,5 s). Gewichtsänderungen
   wirken damit sofort und fair.
6. **Befehle:**
   - `route_gate.py score <board> [datei …]`: Bericht ohne Entscheidung, auch für mehrere Dateien aus
     `build/<platine>/keep/`;
   - `route_gate.py explain <board> <kandidat>`: Beitragstabelle, Kipp-Faktoren, Robustheit;
   - `just route-score main-board`.
7. **Unverändert bleiben:** Fingerabdruck, Ablage unter `rejected/`, Wiederherstellen und `force=1`. Die
   Begründungstexte nennen statt „schlechter bei X“ die zwei größten Beiträge.
8. **Doku:** In entwicklung.md die Abschnitte „Kennzahlen“ und „Entscheidung“ ersetzen. Dieses Dokument wird
   nach der Umsetzung auf den Stand gekürzt (Entscheidungen), die Prototyp-Zahlen kommen in die Historie.

Laufzeit: Die Messung kostet 3,5 s pro Kandidat und Lauf, gegenüber 20–60 min Routing vernachlässigbar.

## 7. Grenzen und offene Punkte

- **Strompfad = ein Weg** (kleinster Widerstand). Parallele Wege und Flächen sind nicht eingerechnet, die
  Rechnung ist also konservativ. VSYS hat keine Fläche.
- **IPC-2221 ist konservativ.** KiCads eigener Rechner nutzt die Brooks/Adam-Anpassung an IPC-2152-Daten. Eine
  Umstellung darauf ist möglich (Formel ΔT = K·I^a·W^b·Th^c). Für die Entscheidung zwischen zwei Läufen ändert
  das wenig; für die harte Grenze wohl schon.
- **Die Kopplung** ist nur ein geometrischer Abstandsbereich (0,6 mm), keine Feldberechnung. Für den
  *Vergleich* von Läufen genügt das.
- **`tight_clearance`** zählt DRC-Paare und nicht deren Länge. Fine-Pitch-Pads erzeugen einen festen Sockel
  (ca. 200), der sich in ΔS aufhebt.
- **SWIG-Bindings** sind ab KiCad 9 abgekündigt (Entfernung geplant für KiCad 11). Nachfolger ist die IPC-API
  (`kicad-python`/`kipy`). Das betrifft das ganze Projekt, nicht nur den Score.
- `kicad-cli pcb drc --refill-zones` gibt es erst nach KiCad 9. Deshalb füllt der Prototyp im Speicher neu.
  Der DRC-Teil prüft (wie heute) die gespeicherte Füllung.
- **Gewichte sind Meinungen.** Die Robustheitszeile zeigt, ob eine Entscheidung an ihnen hängt.

## 8. Befunde nebenbei (aus dem Prototyp, nicht behoben)

1. **Batterie-Motorpfad zu schmal (4 Lagen, beide Stände).**
   - Q1:2 (VSYS) → U2:1 läuft über `route_fix.py`-Bahnen mit 0,2/0,3 mm, teils auf In2 (15 µm).
   - Bei 2 A ergibt das 56 mV (offiziell) bzw. 89 mV Abfall. Nach IPC-2221 trägt ein 0,2-mm-Stück auf In2 nur
     etwa 0,3 A bei 20 K.
   - Im Batteriebetrieb fließt der ganze Motorstrom so.
   - Vorschlag: Q1:2 → C2/VSYS-Hauptbahn in `gen_main_pcb.py` mit 0,5 mm auf F.Cu vorrouten oder
     `WIDTHS["/VSYS"]` für diesen Abschnitt auf 0,4 mm setzen. Danach neu routen.
2. **Via in Pad:**
   - C15:2 (0402, GND) hat ein Via im Pad, ebenso die Lötpads J1:4 und J5:2. Die Vias setzt vermutlich `stitch.py` bzw.
     `route_fix.py` (GND-Anbindung).
   - Bei 0402 droht Lotabsaugung und Tombstoning.
   - Vorschlag: Bei der GND-Anbindung Vias nur neben SMD-Pads setzen (außer Liste).
3. **Netzklassen-Muster in der `.kicad_pro` veraltet** (schon im 2-Lagen-Stand):
   - `ISEN`/`/ISEN` → Power, `GND` in Power und Supply, `MOT_A`/`MOT_B` gibt es nicht mehr.
   - Laut `gen_main_pcb.py` soll ISEN in der Standardklasse bleiben.
   - Wirkung: keine DRC-Fehler, aber falsche Sollbreiten.
4. **Doppelbahnen:** 8–10 Bahnen gleichen Netzes liegen übereinander zurück (`overlapping_segments`, +3V3 und
   EN auf B.Cu). Das ist ein Router-Rest, elektrisch harmlos. Aufräumen vor der Fertigung.
5. **USB:** D− ist 7,2 mm länger als D+ (vorgeroutet, in allen Ständen gleich). Für Full Speed unkritisch;
   Espressif empfiehlt dennoch gleiche Länge.

## Quellen

- KiCad 9 CLI (`pcb drc`, JSON, Schweregrade): https://docs.kicad.org/9.0/en/cli/cli.html (geprüft). DRC-Schema
  https://schemas.kicad.org/drc.v1.json (geprüft). `--refill-zones` nur in den Entwicklungs-Docs:
  https://docs.kicad.org/master/en/cli/cli.html (geprüft).
- KiCad Custom Rules: https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html#custom-design-rules (Abschnitt nicht
  gelesen, Syntax im Prototyp mit KiCad 9.0.8 erprobt).
- pcbnew-Python (ZONE, ZONE_FILLER): https://docs.kicad.org/doxygen-python-9.0/classpcbnew_1_1ZONE.html (nicht
  geöffnet). Abkündigung SWIG / IPC-API: https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/ (geprüft).
- IPC-2221 Strombelastbarkeit I = k·ΔT^0,44·A^0,725, k = 0,048 außen / 0,024 innen (nicht geprüft, Standardformel).
  IPC-2152: Innenlagen nicht so stark abzuwerten. Brooks/Adam, „Internal Trace Temperatures“, I-Connect007 2018:
  https://iconnect007.com/article/114225/brooks-bits-internal-trace-temperaturesmore-complicated-than-you-think/114228/pcb
  (geprüft). KiCad-Rechner (Brooks/Adam-Anpassung):
  https://docs.kicad.org/doxygen/tracks__width__versus__current__formula_8h_source.html (geprüft).
- USB Full Speed:
  - Renesas R01AN0628EJ0100, Guidelines for Full-Speed USB2.0 Board Design (empfiehlt auch für FS 90 Ω ±15 %):
    https://renesas.com/en/document/apn/full-speed-usb-guidelines-full-speed-usb20-board-design-rev100 (geprüft).
  - TI SPRAAR7J High-Speed Interface Layout Guidelines: https://www.ti.com/lit/an/spraar7j/spraar7j.pdf (geprüft).
  - FS-Flanken 4–20 ns (USB 2.0, nicht geprüft).
- Espressif ESP32-C6 Hardware Design Guidelines, PCB-Layout:
  https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/pcb-layout-design.html
  (geprüft)
  - Antenne am Rand und ohne Kupfer auf allen Lagen, 15 mm Freiraum, dichte GND-Vias am Modul.
  - USB: 90 Ω ±10 %, gleich lang, durchgehende Masse, wenige Vias.
  - Siehe auch analyse-funk-controller.md.
- TI DRV8213 Datenblatt SLVSGV9 (Layout 11.1: breite Bahnen VM/OUT/GND, Thermal-Pad mit Vias an innere
  GND-Lagen; IPROPI 8.4.2.2): https://www.ti.com/lit/ds/symlink/drv8213.pdf (geprüft). Keine eigene Vorgabe zur
  IPROPI-Leitungsführung; `sense_*` ist allgemeine Praxis.
- Freerouting-Bewertung (Router- und Optimierer-Score):
  https://github.com/freerouting/freerouting/blob/master/docs/scoring.md (geprüft).
- TopoR (Länge und Vias als Ziel, beliebige Winkel): https://en.wikipedia.org/wiki/TopoR (geprüft).
- Deb, K. (2000): An efficient constraint handling method for genetic algorithms. CMAME 186(2–4), 311–338,
  doi:10.1016/S0045-7825(99)00389-8 (bibliografisch geprüft).
- Das, I.; Dennis, J. E. (1997): A closer look at drawbacks of minimizing weighted sums of objectives for Pareto
  set generation. Structural Optimization 14, 63–69, doi:10.1007/BF01197559 (bibliografisch geprüft).
- Säurefallen: https://resources.pcb.cadence.com/blog/are-acid-traps-still-a-problem-for-pcbs (nicht geöffnet).
  Via-in-Pad/IPC-4761 Typ VII: https://sierraconnect.protoexpress.com/t/pcb-glossary-via-in-pad/3899 (nicht
  geöffnet).
