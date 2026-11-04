# Idee: optionale Zusatz-Hardware auf der Unterseite

Stand: 2026-11-03 · Status: Recherche, nichts beschlossen. Ergänzt [hardware-konzept.md](hardware-konzept.md),
[hauptplatine-c6.md](hauptplatine-c6.md) und [ideen.md](ideen.md).

**Abschnitt 0 ist der aktuelle Stand (ESP32-C6, 4 Lagen).** Die Abschnitte 1–6 darunter beschreiben den alten
**C3-Stand** vom 2026-11-01 und bleiben als Herleitung stehen. Wo sie Abschnitt 0 widersprechen, gilt Abschnitt 0.

---

## 0. Neubewertung für ESP32-C6 und 4 Lagen (Stand 2026-11-03)

Grundlage: [hauptplatine-c6.md](hauptplatine-c6.md) 2.3 und 11, [analyse-funk-controller.md](analyse-funk-controller.md)
3b, [idee-powerbank.md](idee-powerbank.md), [idee-funk-taster.md](idee-funk-taster.md), `hardware/mechanik/huelle.scad`.
Gemessen mit pcbnew an der 2-Lagen-Platine (verworfen, Commit c45c6de) und der 4-Lagen-Platine (0 offen; damals
`hardware/main-board-4l/louie-main-4l.kicad_pcb`, seit 2026-11-03 der Standard `hardware/main-board/louie-main.kicad_pcb`). Koordinaten: Platinenmitte = (0; 0),
Antenne bei −x, USB-C bei +x, +y = Seite der USB-C-Öffnung.

**Grundsatz des Auftraggebers:** Alles Essentielle liegt **oben** und wird komplett maschinell bestückt (einseitige
Economic PCBA bei JLC). Die Platine läuft **ohne jede Handarbeit** (Versorgung über USB-C; Akku-Kabel an J1/J5 sind
Einbau, nicht Bestückung). Die **Unterseite ist ausschließlich optional:** Pads, Footprints zum Handlöten,
Testpunkte. Nichts, was für den Grundbetrieb nötig ist, kommt nach unten. Bauteile unten werden **nie** bestückt,
sonst wird die PCBA zweiseitig und teurer.

### Kurzfassung

- **Ja, 4 Lagen bieten mehr Optionen, aber nicht wegen der Fläche.** Unten ist bei beiden Varianten gleich viel
  Platz frei (ca. 380 mm² ohne Courtyards). Neu ist: Bei 4 Lagen ist die Unterseite **keine Massefläche mehr**
  (GND liegt durchgehend auf In1), und für Stichleitungen gibt es In2. Ein zusätzliches Pad kostet ein Via und eine
  kurze Bahn, ohne eine Massefläche zu zerschneiden. Bei 2 Lagen zerschneidet jede neue Leitung unten die GND-Fläche,
  und es sind schon 13 Verbindungen offen.
- **Oben ist kein Platz mehr** (99 mm² frei, zerstückelt, kein 3 × 3 mm großes Stück). Neue Bauteile oben: keine.
- **Es lohnen sich wenige, gezielte Pads, nicht „alle Pins raus“.** Für realistische Erweiterungen reichen
  4 zusätzliche GPIOs (IO17 = RXD, IO20, IO21, IO23) plus IO22 für einen optionalen Lastpuls. **IO8 und IO15
  nicht herausführen** (Strapping, kein Bedarf).
- **Empfehlung unten (4 Lagen):** J6 „GPIO“ (3V3, RXD, IO20, IO21, GND), J7 „LED-Kette“ (VSYS über offene
  Lötbrücke, IO23, GND), Footprint Lastpuls an VBUS (DNP), DNP-Vorbeschaltung an IO5, 4 Testpunkte. Zusammen ca.
  110 mm² der freien 380 mm². **J2 muss 1 mm nach innen**, sonst liegen seine Pads halb außerhalb der Tasche der Hülle.
- **Bei 2 Lagen:** keine zusätzlichen Pads, solange die 13 offenen Verbindungen nicht geschlossen sind.

### 0.1 Bestandsaufnahme

#### Freie C6-GPIOs und ihre Eigenschaften

Belegt und schon an Pads: **IO2** INT (J2-5, LP-GPIO, Deep-Sleep-Wecken), **IO6/IO7** SDA/SCL (J2-3/4, LP-I²C),
**IO9** BOOT (J3-3), **IO16** TXD (J3-2), **EN** (J3-1), **IO5** (J3-5). IO0/1/3/4 (VBAT_ADC, ISEN_ADC, SENSE,
VBUS_DET) haben keine Pads und brauchen keine.

| GPIO (Modulpad, Lage) | ADC | Deep-Sleep-Wecken | Strapping / Boot | heute | Bewertung |
|---|---|---|---|---|---|
| **IO5** (10, Kante +y, x = −5,6) | ADC1_CH5 | **ja** (LP_GPIO5) | nur SDIO-Flanke, Pegel egal; JTAG MTDI (JTAG läuft über USB) | **J3-5** | einziger freier Pin mit ADC und Deep-Sleep-Wecken |
| IO8 (22, rechts, y = −3,2) | – | nein | **ja**: muss im Download-Modus (IO9 = 0) high sein; steuert mit eFuse das ROM-Log (unsicher) | R11 10 k nach 3V3, kein Pad | nicht herausführen |
| IO15 (20, rechts, y = −1,6) | – | nein | JTAG-Quelle, nur mit gebrannter eFuse wirksam | offen | frei nutzbar, aber kein Bedarf |
| **IO17** = RXD (30, Kante −y, x = −8,8) | – | nein | UART0-RX des ROM (Eingang beim Boot) | offen | **RXD zur Konsole** (TXD liegt schon auf J3) |
| **IO20** (26, Kante −y, x = −5,6) | – | nein | – | offen | frei |
| **IO21** (27, Kante −y, x = −6,4) | – | nein | – | offen | frei |
| **IO22** (28, Kante −y, x = −7,2) | – | nein | – | offen | frei |
| **IO23** (29, Kante −y, x = −8,0) | – | nein | – | offen | frei |

(Modulpads gelesen aus der 4-Lagen-Platine, geprüft; ADC/LP/Strapping aus analyse-funk-controller.md 3b.1, geprüft.)

- **Wecken:** Aus Deep Sleep wecken nur LP-GPIO0–7. Frei ist davon nur IO5. Alle anderen freien Pins wecken nur
  aus Light Sleep (180 µA beim C6). Für Spieltasten reicht das, weil das Spiel dann ohnehin läuft.
- **Boot-Glitches:** Das C6-Datenblatt nennt Pins mit kurzen Pegelspitzen beim Einschalten. Welche das genau sind,
  ist hier **nicht nachgelesen (unsicher)**. Darum gilt für alles, was schaltet: Gate mit Pull-down, Ausgang erst
  nach dem Boot aktiv. Ein Glitch von wenigen µs ist für Lastpuls, LED-Kette und Taster harmlos.
- **TXD (IO16)** gibt beim Booten das ROM-Log aus, bleibt also Konsole.

#### Vorhandene Pads (beide Varianten gleich, Unterseite)

| Pad | Lage (Mitte) | Pads | Netze |
|---|---|---|---|
| J1 | x = +14,5, y = +5,65 (Kante +y, unter USB-C) | 4 × 1,4 × 1,6 mm, Raster 2,0 | BAT_IN, –, –, GND |
| J2 | x = +3,4, y = +5,3 (Kante +y, unter LDO/Q1) | 5 × 1,4 mm, Raster 2,54 | 3V3, GND, SDA, SCL, INT |
| J3 | x = −8,55, y = −3,25 (unter dem Modul) | 5 × 1,4 mm, Raster 2,54 | EN, TXD, BOOT, GND, IO5 |
| J5 | x = +15,15, y = +2,55 (unter USB-C) | 2 × 2,5 × 3,5 mm | BAT_IN, GND |
| BT1/BT2 | x = −21,4 / +21,4 | je 2 × 2 mm | OUT_A / OUT_B (Endkontakte) |

Testpunkte TP1–TP8 aus dem C3-Stand gibt es nicht mehr.

#### Freie Fläche (gemessen, pcbnew-Raster 0,05 mm)

Nutzbar = Platine ohne Antennenbereich (x < −14,6), ohne Randstreifen 0,32 mm und ohne Bereich unter den
Endkappen (|x| > 22,2): **475 mm²**.

| | 2 Lagen | 4 Lagen |
|---|---|---|
| **Oben** frei von Courtyards | 99 mm² | 99 mm² (Platzierung gleich) |
| davon so groß, dass 2 × 2 mm passt / 3 × 3 mm passt | 20 / **0** mm² | 20 / **0** mm² |
| oben frei auch von Bahnen und Pads (+0,2 mm) | 35 mm² | 29 mm² |
| **Unten** frei von Courtyards | **382 mm²** (in der Tasche \|y\| ≤ 5,2: 312) | **382 mm²** (Tasche: 312) |
| unten frei auch von Bahnen und Pads (+0,2 mm) | 208 mm² | 185 mm² |
| davon 3 × 3 mm am Stück | 34 mm² | 9 mm² |
| Rolle der Unterseite | **GND-Fläche** (246 mm² in 2 Teilen), 13 Verbindungen offen | Signale + GND-Füllung; GND durchgehend auf In1 |

Größte kupferfreie Stücke unten bei 4 Lagen: x +12,8 … +19,2, y −4,2 … −0,5 (unter USB-C, neben J5, ca. 19 mm²)
und x +3,2 … +6,3, y −5,8 … −2,0 (unter C1/C2, ca. 11 mm²). Bei 4 Lagen lassen sich Bahnen unten auf In2 verlegen
(Router-Lauf nötig). Die nutzbare Fläche liegt also zwischen 185 und 380 mm². **Fläche ist unten nicht der Engpass.**

#### Bauhöhe unten

- Die Platinenunterseite liegt 0,3 mm unter der Zellachse. Die AA-Schale (`huelle.scad`) hat unter der Platine
  eine **Tasche 10,4 mm breit (|y| ≤ 5,2) und 2,0 mm tief**, außerhalb davon liegt die Platine auf.
- **Heute:** Bauteile unten bis ca. **1,5 mm** hoch (0,5 mm Luft für Lötzinn und Toleranz), nur in |y| ≤ 4,5.
  Litzen an den Pads ebenfalls nur in der Tasche oder im Kabelfenster (x = 10 … 19, +y).
- **Mit tieferer Tasche:** Rechnerisch mit 0,8 mm Restwand (Radius 6,45 mm) wären bei |y| ≤ 3 bis ca. 5,4 mm und
  bei |y| ≤ 4,5 bis ca. 4,3 mm Höhe möglich. Das ist nur eine Hüllkurvenrechnung (unsicher, Druckprobe).
  Die Angabe „1,0–1,2 mm“ in Abschnitt 1 stammt aus der Zeit vor der Tasche.
- **Befund J2:** Die J2-Pads reichen bis y = +6,0, die Tasche nur bis +5,2. Eine angelötete Litze drückt dort auf
  die Schale. **J2 um ca. 1 mm nach −y (Mitte y ≤ +4,3) verschieben** oder die Tasche dort verbreitern. Bei
  4 Lagen ist das Verschieben unkritisch.

### 0.2 Sinnbewertung: Welche zusätzlichen Pads lohnen sich?

| Kriterium | Befund |
|---|---|
| **Nutzen** | Realistische Erweiterungen: Kabel-Spieltasten (Notlösung bzw. Test für die Taster-Mitspieler aus idee-funk-taster.md 4.5, jetzt ohne Port-Expander), zweiter Taster mit Deep-Sleep-Wecken, externe LED-Kette, Lastpuls für Powerbanks, UART-RX zur Fehlersuche. Dafür reichen **IO5 (vorhanden) + IO17, IO20, IO21, IO22, IO23**. Für IO8 und IO15 gibt es keine Anwendung, die die anderen Pins nicht besser abdecken. |
| **Testbarkeit** | Heute messbar: 3V3, I²C, INT, EN, TXD, BOOT, IO5, BAT_IN, OUT_A/OUT_B. **Es fehlen VSYS, VBUS, ISEN (IPROPI) und SENSE**, gerade die Größen, die man bei der Inbetriebnahme von Motor, Strombegrenzung und Hebel braucht. Dazu fehlt **RXD**: Mit TXD allein ist die serielle Konsole einseitig. Sie ist der Notweg, wenn USB-CDC hängt oder USB-C gerade zum Messen an der Powerbank steckt. |
| **Risiko Antenne** | Alle Vorschläge liegen bei x ≥ −13,6 (wie J3). Die Sperrflächen bei x < −14,6 bleiben auf allen Lagen unberührt. |
| **Risiko Strapping** | IO8/IO15 nicht herausführen. RXD (IO17) ist im ROM nur Eingang; ein Taster nach GND beim Einschalten stört den Flash-Boot nicht (unsicher, am Muster testen). |
| **Risiko ESD** | Die Pads liegen im geschlossenen Batteriefach und werden im Spiel nicht berührt. Kritisch wird es erst bei Litzen nach außen (Taster, LED-Kette): **220–470 Ω in Reihe in der Leitung** (am Kabelende, Schrumpfschlauch) und Litze mit GND verdrillt. Auf der Platine keine TVS-Dioden (Platz, Aufwand) (unsicher, ob die Pin-ESD des C6 bei langen Leitungen reicht). |
| **Risiko Kurzschluss im Fach** | VSYS ist ungesichert (LiPo nur über seinen Schutz-IC, USB über D2). **VSYS deshalb nur über eine Lötbrücke, Standard offen**, und nicht neben GND. Keine dauerhaft spannungsführenden Pads außer 3V3 (LDO-Strombegrenzung). |
| **Aufwand 4 Lagen** | Je Pad ein Via und eine kurze Bahn auf In2; die Modulpads 26–30 liegen nebeneinander an der Kante −y, direkt über J3 und J6. Der Router muss neu laufen (20–60 min); dass alles ohne neue offene Verbindungen aufgeht, ist **unsicher**. Die Stitching-Vias unter dem Modul müssen J6 ausweichen (In1 bleibt GND, also unkritisch). |
| **Aufwand 2 Lagen** | Hoch: jede Leitung unten zerschneidet die GND-Fläche weiter, 13 Verbindungen sind schon offen. |

**Ein universeller Pad-Block?** Ja, aber verteilt nach Ort. Ein einziger Block mit 3V3, GND, VSYS, SDA, SCL und
4 GPIO wäre 10 Pads lang (25 mm bei 2,54 mm). Er müsste quer über die Platine laufen, zu Pins von beiden Modulkanten.
Sinnvoller ist: **I²C bleibt auf J2** (Kante +y, wo SDA/SCL/INT austreten), **die neuen GPIOs kommen auf J6** unter
dem Modul (Kante −y, wo IO17/20/21 austreten), **VSYS und LED-Daten auf J7** nahe dem VSYS-Band. Alle Blöcke im
Raster 2,54 mm mit 1,4-mm-Pads: geeignet für Litze und für Pogo-Pins (z. B. P75/P100). Testpunkte als runde Pads
Ø 1,0 mm.

### 0.3 Handlöt-Kandidaten neu bewertet (C6 + 4 Lagen)

„Oben“ = maschinell bestückt (essentiell oder sehr günstig mitzunehmen). „Unten“ = optional, Handlöten oder nur Pads.

| # | Bauteil | Nutzen fürs Spiel | Gehäuse handlötbar | Pins | Platz / Höhe | Empfehlung |
|---|---|---|---|---|---|---|
| K1 | LIS2DH12 | Klopfen, Anheben, Schütteln; INT auf IO2 → **jetzt Deep-Sleep-Wecken** | ★ LGA | I²C + IO2 | liegt **oben** (U4 + C15) | **oben lassen** (Entscheidung steht). Eigentlich optional: Grundbetrieb geht ohne |
| K2 | LIS2DW12 | wie K1, flacher, sparsamer | ★ | wie K1 | – | nur als Stücklisten-Alternative für U4 (Pin-Kompatibilität unsicher) |
| K3 | BMA400 | wie K1 | ★ | – | – | **entfällt**: Grund war IO2-Strapping, beim C6 kein Thema mehr |
| K4 | SC7A20 | wie K1 | ★ | – | – | höchstens Zweitquelle für U4 (Registerkompatibilität unsicher) |
| K5 | MMA8452Q | wie K1 | ★★ | – | – | nein (auslaufend) |
| K6 | I²C-Pads | jedes Breakout | ★★★ | 5 | J2 vorhanden | **unten, bleibt**; 1 mm nach innen schieben (0.1) |
| K7 | TMAG5273 | Magnet-Spielereien; Drehzahl gibt es schon über ISEN/PCNT | ★★★ SOT-23-6 | I²C | 1,45 mm passt jetzt in die Tasche | kein Footprint; bei Bedarf als Breakout an J2 |
| K8 | DRV5032 | Hall-Schalter | ★★★ | 1 GPIO (jetzt frei) | – | kein Footprint; extern an J6 (3V3/GND/GPIO) möglich |
| K9 | WS2812 auf der Platine | im Fach unsichtbar | ★★ | 1 | – | nein; stattdessen **J7 für eine externe Kette** |
| K10 | I²S-Mikrofon | Klatschen | ★ LGA | 3 | Schallloch | nein (3 Pins, Schallloch, geschlossenes Fach; MicroPython-I²S nur Standard-Modus) |
| K11 | Piezo-Summer | Töne | ★★★ | 1 | 1,9 mm: nur mit tieferer Tasche | nein; Töne über den Motor, externer Piezo an J6 möglich |
| K12 | MAX17048 | Akku-% | ★★ (Exposed Pad) | I²C | 2 × 2 mm | nein: VBAT_ADC misst mit dem C6-ADC bis 3,3 V; die Zelle sitzt ohnehin an der Ladeplatine |
| K13 | SHT40 | – | ★★ | I²C | – | nein |
| K14 | Lichtsensor | im Fach dunkel | ★★ | I²C | – | nein |
| K15 | Taster | zweiter Knopf, Kabel-Spieltasten | ★★★ | IO5 + 3 GPIO | Pads | **unten**: IO5 auf J3 (Deep-Sleep-Wecken), dazu IO17/20/21 auf J6 (Light Sleep) |
| K16 | Piezo-Scheibe an ADC | Klopfen | ★★★ extern | IO5 | Pads | nur über die DNP-Vorbeschaltung an IO5 (N4); doppelt zu K1 |
| **N1** | **Lastpuls Powerbank** (AO3400A + 47 Ω/1 W 2512 + 100 k Gate-Pull-down) | Powerbank bleibt im Standby an (idee-powerbank.md, Lösung C) | ★★★ SOT-23, 2512 | IO22 | ca. 9 × 4 mm, ≤ 1,25 mm hoch | **unten, DNP**: nur wenn der Firmware-Puls (Lösung D) nicht reicht |
| **N2** | Externe LED-Kette (WS2812/SK6812) | Status/Effekte außen am Spiel | Pads | IO23 + VSYS | 3 Pads | **unten, J7** |
| **N3** | UART-RX | Fehlersuche ohne USB | Pad | IO17 | 1 Pad | **unten, J6-2** |
| **N4** | DNP-Vorbeschaltung IO5 (R nach 3V3, R und C nach GND, 0402) | NTC, Widerstandsleiter (mehrere Tasten an einem ADC), Poti, Piezo-Ableitwiderstand | ★★★ 0402 | IO5 | ca. 8 mm² | **unten, DNP** |
| **N5** | Testpunkte VSYS, VBUS_J4, ISEN, SENSE | Inbetriebnahme, Prüfadapter | Pad Ø 1,0 | – | 4 × ca. 2 mm² | **unten** |
| N6 | Hall-Sensor für Hebel/Turm | Hebel und Drehung erkennt die Platine schon über SENSE und ISEN | ★★★ | 1 GPIO oder I²C | – | nein: die Platine liegt im Batteriefach, fern von Hebel und Turm |
| N7 | Zellspannung/Temperatur | VBAT wird schon gemessen; Schutz macht der Zell-IC | – | IO5 (ADC) | – | kein eigener Footprint; NTC über N4 möglich |
| N8 | Zweiter Motor/Vibration | – | – | – | – | nein (DRV8213 hat einen Kanal) |

### 0.4 Empfehlung für die 4-Lagen-Platine

**Oben:** keine neuen Bauteile. Es ist kein Platz frei, und für den Grundbetrieb fehlt nichts. Heute oben, aber
eigentlich optional: **U4 LIS2DH12 + C15** (bestückungsoptional, bleibt oben) und D1/R9 (Status-LED, sinnvoll).
Daran ändert sich nichts.

**Unten (alles optional, nichts bestückt):**

| Ref (Vorschlag) | Art | Belegung | Lage (grob) | Platz |
|---|---|---|---|---|
| **J6** „GPIO“ | nur Pads, 1 × 5, 2,54 mm, 1,4 mm | 1 3V3 · 2 RXD (IO17) · 3 IO20 · 4 IO21 · 5 GND | unter dem Modul parallel zu J3, y ≈ +0,6, x −13,6 … −3,5; Stiche von Modulpads 26/27/30 über In2 | ca. 12 × 2 mm = 24 mm² |
| **J7** „LED-Kette“ | nur Pads, 1 × 3, 2,54 mm | 1 VSYS (über JP1) · 2 IO23 · 3 GND | unter C1/C2, x ≈ +1 … +7, y ≈ −3,5 (in der Tasche) | ca. 8 × 2 mm = 16 mm² |
| **JP1** | Lötbrücke, **Standard offen** | VSYS → J7-1 | neben J7 | ca. 2 mm² |
| **Q2, R17, R18** (Lastpuls) | Footprints **DNP**: Q2 AO3400A (SOT-23), R17 47 Ω 1 W (2512), R18 100 k (0402, Gate → GND) | Drain über R17 an **VBUS_J4**, Gate an **IO22** | unter USB-C, Seite −y (x ≈ +9 … +19, y ≈ −5 … −2), zwischen den Schirmlaschen | ca. 40 mm² |
| **R19, R20, C16** (IO5-Vorbeschaltung) | Footprints **DNP**, 0402 | R19 IO5 → 3V3, R20 IO5 → GND, C16 IO5 → GND | direkt neben J3-5 | ca. 8 mm² |
| **TP1–TP4** | Testpunkte Ø 1,0 mm | VSYS, VBUS_J4, ISEN (IPROPI-Seite), SENSE | nahe vorhandenen Vias der Netze | ca. 8 mm² |
| J2 | verschieben | – | Mitte y ≤ +4,3 statt +5,3 | – |

Summe ca. **110 mm²** von 382 mm² freier Unterseite. Alle Bauteile unten ≤ 1,25 mm hoch, alle in |y| ≤ 5.

Hinweise zur Auslegung:
- **Lastpuls an VBUS statt VSYS:** Er kann dann physikalisch nur ziehen, wenn USB-C steckt, und nie den LiPo
  leeren. 47 Ω an 5 V ergeben ca. 105 mA und 0,53 W im Puls; bei 50 ms alle 9 s im Mittel ca. 3 mW. Der 2512
  (1 W) übersteht auch einen Firmware-Fehler mit Dauer-Ein (unsicher, Erwärmung in der geschlossenen Tasche messen).
  Passt der 2512 nicht zwischen die Schirmlaschen, als Rückfall 2 × 1206 100 Ω parallel oder Lage an VSYS
  (x +1 … +9) mit Freigabe in der Firmware über VBUS_DET.
- **J7/LED-Kette:** WS2812B braucht VDD ≥ 3,7 V; an VSYS mit LiPo unter 3,7 V außerhalb der Spezifikation. Bei
  VDD 4,6–5 V ist 3,3 V am DIN knapp (VIH = 0,7 × VDD) (unsicher). SK6812 oder eine LED mit 3,3-V-Daten wählen.
  Reihenwiderstand 330 Ω im Kabel.
- **J6:** Taster gegen GND mit internem Pull-up, Wecken aus Light Sleep. RXD und TXD (J3-2) ergeben zusammen die
  UART0-Konsole.
- **Prüfen vor dem Layout:** Pegelspitzen der C6-Pins beim Einschalten (Datenblatt), Router-Lauf mit den neuen
  Netzen (0 offen?), Hülle mit verschobenem J2.

**Lohnt nicht:**

| Was | Warum |
|---|---|
| alle 8 freien GPIOs herausführen | IO8 ist Strapping-Pin mit Pull-up, IO15 ohne Anwendung. Jedes Pad mehr heißt Doku, Router-Lauf und ein weiteres offenes Ende ohne Nutzen |
| ein einziger Universalblock mit 10 Pads | 25 mm lang, müsste beide Modulkanten verbinden; verteilt auf J2/J6/J7 sind die Wege kurz |
| Bauteile auf der Oberseite | kein 3 × 3 mm großes Stück frei; nichts davon ist essentiell |
| Bestückte Teile unten | zweiseitige PCBA, Mehrkosten, widerspricht dem Grundsatz |
| TVS-Dioden an den neuen Pads | Pads liegen im geschlossenen Fach; Reihenwiderstand im Kabel genügt (unsicher) |
| Summer, Mikrofon, Licht-/Feuchtesensor, MAX17048, Hall-Sensor, BMA400, MMA8452Q | siehe Tabelle 0.3 |
| Qwiic-Buchse | ca. 2,9 mm hoch (unsicher), Litze an J2 reicht |
| VSYS dauerhaft auf einem Pad | ungesichert; nur über Lötbrücke |

### 0.5 Bei 2 Lagen

**Keine zusätzlichen Pads**, solange die 13 offenen Verbindungen nicht geschlossen sind. Die Unterseite ist dort die
GND-Fläche, und jede neue Stichleitung zerteilt sie weiter. Machbar ohne neue Leitungen sind höchstens die
Verschiebung von J2 und Testpunkte direkt an vorhandenen Vias (VSYS, ISEN, SENSE). Lastpuls und J6/J7 nur mit der
4-Lagen-Platine.

---

## 0b. NeoPixel, vier Kabel-Taster, Piezo statt Beschleunigungssensor (Stand 2026-11-03)

Fragen des Auftraggebers: (1) Taugt J7 für eine NeoPixel-Kette und flexibel auch für eine einzelne LED oder einen
Taster? (2) Wie schließt man vier Kabel-Taster an (einer pro Arm)? (3) Piezo-Klopfsensor statt LIS2DH12, um das
Drücken der Wippen zu erkennen? (4) Gesamtbelegung der freien GPIOs und Pads unten.
Gilt für die 4-Lagen-Platine (wird Standard). **Grundsatz bleibt:** unten nur Pads und DNP-Footprints, nichts
Essentielles. Abschnitt 0b ergänzt Abschnitt 0 und ändert dort einige Punkte (Liste in 0b.5).

Datenblattwerte selbst gelesen (geprüft): ESP32-C6-Datenblatt v1.5 (Tabelle 2-2 Pin-Zustände, Tabelle 5-4
DC-Kennwerte, Tabelle 5-5 ADC), WS2812B (Worldsemi, Adafruit-Kopie). Aus Suchergebnissen bzw.
Datenblattauszügen (geprüft, nur Kennwert): WS2812B-V5, WS2812B-Mini, SK6812, 74AHCT1G125, SN74LV1T34, TPS22918.
Netze an U4/J2/J3/R11 aus `hardware/main-board/louie-main.kicad_pcb` gelesen (Stand während des Umbaus, 4 Lagen).

### Kurzfassung

1. **J7 taugt, mit drei Änderungen:** (a) LED-Typen der V5-Generation mit V_IH = 0,63 · VDD (WS2812B-V5,
   WS2812B-Mini-V3, WS2812B-2020) statt SK6812 bzw. alter WS2812B (0,7 · VDD); (b) **die Kette braucht einen
   Schalter in der Versorgung**, weil adressierbare LEDs auch dunkel Ruhestrom ziehen und den Akku im Deep Sleep
   leeren: optionaler Lastschalter U6 (TPS22918, SOT-23-6) mit Freigabe über **IO15**, JP1 bleibt als Überbrückung;
   (c) kein Pegelwandler auf der Platine: 74AHCT1G125 passt nicht (VCC 4,5–5,5 V, VSYS am Akku nur 3,0–4,2 V).
   J7 ist **flexibel ohne Zusatzteile auf der Platine**: NeoPixel-Kette, einzelne LED (mit Vorwiderstand im Kabel,
   LEDC-PWM) oder Taster (interner Pull-up). Was angeschlossen ist, entscheidet die Firmware.
2. **Vier Kabel-Taster: je ein eigener GPIO mit Pull-up** (Variante a). Belegung **S1 = IO5, S2 = IO20,
   S3 = IO21, S4 = IO8** auf einem neuen Pad-Block J6 „Spieler“. Gleichzeitige Drücke, Interrupt, < 1 ms
   Hardware-Latenz, zwei Adern je Arm. Widerstandsleiter (b) nur für Einzeldrücke zuverlässig, Portexpander (c) nur,
   wenn mehr als vier Eingänge gebraucht werden.
3. **LIS2DH12 oben behalten** (bestückungsoptional, wie entschieden), aber er erkennt nur „irgendwo wurde
   geschlagen“, nicht welcher Arm. **Kein Piezo auf der Platine.** Zum Erkennen der Wippe pro Arm einen
   **Kontakt unter der Wippe** (Reedkontakt + Magnet oder Mikroschalter) an den Kabel-Eingängen aus Punkt 2; ein
   Piezo je Arm geht an denselben Pads (digital, 1 MΩ + 100 kΩ im Kabel), ist aber die zweite Wahl.
   Nutzen ist mittel (Statistik, Treffer-Zuordnung, neue Modi), nicht für den Grundbetrieb.
4. **Pins:** IO5/IO20/IO21/IO8 Spieler-Eingänge, IO15 LED-Versorgung ein, IO17 RXD (Service, neu auf J3-5),
   IO22 Lastpuls, IO23 LED-Daten. Damit sind alle acht freien GPIOs verplant. Unten entstehen J6 (6 Pads), J7
   (3 Pads) mit U6/JP1/C17/R22 und RC-Footprints für die Eingänge, zusammen ca. 150 mm² von 382 mm².

### 0b.1 NeoPixel an J7

#### Pegel und Versorgung

| Größe | Wert | Quelle |
|---|---|---|
| C6 V_OH | ≥ 0,8 · VDD = **2,64 V** (bei hochohmiger Last, typ. nahe 3,3 V) | C6-DS Tab. 5-4 (geprüft) |
| C6 V_IH / V_IL (Eingang) | 0,75 · VDD = 2,48 V / 0,25 · VDD = 0,83 V | C6-DS Tab. 5-4 (geprüft) |
| C6 Pull-up/-down intern | 45 kΩ typ. | C6-DS Tab. 5-4 (geprüft) |
| C6 Treiberstrom | 20 mA Standard, bis 40 mA (PAD_DRIVER = 3) | C6-DS Tab. 2-2/5-4 (geprüft) |
| WS2812B (5050, alt) | VDD 3,5–5,3 V (abs.), Kennwerte bei 4,5–5,5 V; **V_IH 0,7 · VDD**; T0H 0,4 µs, T1H 0,8 µs, T0L 0,85 µs, T1L 0,45 µs je ±150 ns; Reset > 50 µs | WS2812B-DS (geprüft) |
| WS2812B-V5 | VDD 3,7–5,3 V; **V_IH 0,63 · VDD**; Reset > 280 µs | Worldsemi V5 (geprüft, Auszug) |
| WS2812B-Mini (3535) | VDD 3,7–5,3 V; V_IH 0,63 · VDD | WS2812B-Mini-DS (geprüft, Auszug) |
| WS2812B-2020 V6 | VDD 3,7–5,3 V; Ruhestrom ≤ 1 µA | siehe K9 (aus C3-Stand) |
| SK6812 / SK6805 | VDD 3,7–5,5 V; **V_IH 0,7 · VDD** | SK6812-DS (geprüft, Auszug) |

Was am DIN ankommt (3,3 V aus dem C6) gegen die Schwelle:

| Versorgung der LEDs | VDD | V_IH bei 0,7 · VDD | V_IH bei 0,63 · VDD | Bewertung |
|---|---|---|---|---|
| VSYS am Akku (über Q1) | 3,0–4,2 V | 2,1–2,94 V | 1,9–2,65 V | Pegel **ok**; **unter 3,7 V VDD außerhalb der Spezifikation** (Blau/Grün werden schwächer, Farbe kippt) |
| VSYS über USB (J4 → D2 SS34) bzw. Ladeplatine | ca. 4,6 V | **3,22 V** (knapp, nur 80 mV Reserve) | 2,90 V (ok) | 0,63-Typen ok, 0,7-Typen Glückssache |
| VBUS 5 V direkt | 5,0 V | **3,5 V** (außerhalb) | 3,15 V (knapp) | nicht vorsehen; außerdem nur mit USB |
| 3V3 aus dem LDO | 3,3 V | – | – | nein: VDD unter Spezifikation, und WLAN-Spitzen (382 mA) plus LEDs überfordern den AP2112K (600 mA) |

**Folgerung:** An VSYS mit **V5-Typen (0,63 · VDD)** ist der 3,3-V-Pegel im ganzen Bereich ausreichend, ohne
Pegelwandler. In der Praxis laufen auch SK6812 und alte WS2812B meist (unsicher). Unter ca. 3,6 V Akkuspannung
dimmt die Firmware die LEDs bzw. schaltet sie ab (VBAT_ADC wird ohnehin gemessen).

**Pegelwandler / Opfer-LED, bewertet:**

| Lösung | Bewertung |
|---|---|
| 74AHCT1G125 | **ungeeignet**: VCC 4,5–5,5 V (V_IH 2,0 V). Am Akku liegt VSYS bei 3,0–4,2 V, also außerhalb (geprüft, Nexperia-DS) |
| SN74LV1T34 (TI, SOT-23-5) | **passend, falls nötig**: Einzelversorgung 1,65–5,5 V, abgesenkte Eingangsschwellen, 3,3-V-Eingang bei 5-V-VCC zulässig (geprüft, TI-Produktseite). Nicht auf der Platine vorsehen (der Datenpfad müsste aufgetrennt werden); bei Bedarf als Winzling am Kettenanfang im Kabel |
| „Opfer-LED“ (erste LED über Diode mit VDD − 0,7 V versorgt, sie regeneriert den Pegel) | funktioniert an USB (4,6 V → 3,9 V), am Akku liegt die erste LED dann bei 2,3–3,5 V, also deutlich außerhalb. Nicht empfohlen |
| V5-LEDs direkt | **empfohlen**, null Bauteile |

#### Ruhestrom, Schalter in der Versorgung

Adressierbare LEDs ziehen auch dunkel Strom, je nach Typ einige 100 µA bis ca. 1 mA pro LED (alte Typen) bzw.
≤ 1 µA (WS2812B-2020 V6) (unsicher, typabhängig). Acht LEDs mit 0,6 mA = 5 mA; das ist das Hundertfache des
Deep-Sleep-Budgets (LDO 55 µA). Ein 1000-mAh-Akku wäre in gut einer Woche leer. JP1 allein schaltet nicht.

**Vorschlag U6 (DNP): Lastschalter TPS22918 (SOT-23-6)** zwischen VSYS und J7-1: VIN 1–5,5 V, 2 A, 52 mΩ,
Ruhestrom 8,7 µA typ. (geprüft, TI); Freigabe ON an **IO15** mit **R22 100 kΩ nach GND** (DNP). IO15 hat nach
dem Datenblatt beim Reset und danach keinen Pull-up (nur IE), schläft im Deep Sleep mit (kein LP-Pin) → R22 hält
U6 dann sicher aus. **JP1 (offen) liegt parallel zu U6**: Wer keinen Schalter will, schließt JP1 (dann nur LEDs mit
≤ 1 µA Ruhestrom oder Kette abziehen). ON-Schwelle für 3,3-V-Logik und Bauhöhe (DBV max. ca. 1,45 mm, Grenze
1,5 mm) vor dem Layout im Datenblatt prüfen (unsicher). TPS22918 hat **keine Strombegrenzung**: VSYS bleibt
ungesichert, darum im Kabel eine **PTC-Sicherung 0,5 A** (oder 0,75 A) vorsehen.

#### Strom, Spannungsfall, Abblockung, Serienwiderstand

- **Strom:** bis ca. 12 mA je Farbe, also ca. 36 mA je LED voll weiß (2020/3535); große 5050 bis ca. 50–60 mA
  (unsicher). Für Louie sinnvoll: 4 LEDs (eine je Spielerfarbe an den Armwurzeln) bis 8 LEDs. **Firmware-Deckel
  ca. 30 % Helligkeit** → 4 LEDs ≈ 40 mA, 8 LEDs ≈ 90 mA (unsicher). Der Motor zieht ohnehin 1–2 A aus VSYS.
- **Spannungsfall:** 2 × 40 cm Litze 0,08 mm² (AWG 28, ca. 0,21 Ω/m) ≈ 0,17 Ω; bei 0,1 A 17 mV, bei 0,5 A 85 mV
  (gerechnet). Unkritisch. Das Problem ist nicht der Abfall, sondern VSYS-Einbrüche beim Motoranlauf: Puffer an
  der Kette.
- **Abblockung:** pro LED 100 nF (in Streifen meist vorhanden), am Kettenanfang **10–47 µF**. Adafruit empfiehlt
  500–1000 µF für große Streifen an großen Netzteilen; für 4–8 LEDs reicht weniger (unsicher). Auf der Platine
  **C17 10 µF 0805 an J7-1 (DNP)** hinter U6.
- **Serienwiderstand 330 Ω (300–500 Ω) am Kettenanfang, also am LED-Ende des Kabels**, nicht an der Platine
  (Adafruit Best Practices, geprüft). Er dämpft Überschwinger und begrenzt den Strom, wenn DIN Spannung führt,
  bevor VDD anliegt. Auf der Platine bleibt IO23 → J7-2 eine direkte Bahn.
- **Kabel:** DIN mit GND verdrillt, bis ca. 1 m problemlos (Adafruit: „ein bis zwei Meter“). ESD: LEDs sitzen
  im Gehäuse unter Kunststoff; Serienwiderstand plus C6-ESD (HBM ± 2 kV, C6-DS) genügt (unsicher).
- **Einschaltverhalten:** IO23 hat beim Reset den internen Pull-up (C6-DS Tab. 2-2: IO18–IO23 = WPU beim Reset),
  danach ist er offen. Bis die Firmware die Kette initialisiert, kann DIN schweben → zufällige Farben. Mit U6 aus
  (R22) passiert nichts; bei geschlossenem JP1 früh im Boot `np.fill((0,0,0)); np.write()`.

#### Timing mit MicroPython auf dem C6

- `neopixel.NeoPixel(Pin(23), n)` nutzt `machine.bitstream` mit 800-kHz-Timing (400/850/800/450 ns). Auf dem
  ESP32-Port läuft `bitstream` über das **RMT**, wenn `SOC_RMT_SUPPORTED` (C6: ja) und `esp32.RMT.bitstream_rmt()`
  nicht abgeschaltet ist; sonst Bit-Banging (geprüft, `ports/esp32/machine_bitstream.c`). RMT-Takt 40 MHz →
  25 ns Auflösung, deutlich innerhalb ±150 ns.
- RMT erzeugt das Signal in Hardware; WLAN-Interrupts verschieben keine Bits. Bei langen Ketten muss der
  RMT-Speicher per Interrupt nachgefüllt werden. Ob das bei aktivem WLAN Aussetzer gibt, ist offen (unsicher);
  für 4–16 LEDs uninteressant. Der C6 hat 4 RMT-Kanäle (C6-DS), MicroPython vergibt sie dynamisch. Der Motor nutzt
  LEDC, also kein Konflikt.
- 8 LEDs × 24 bit × 1,25 µs = 0,24 ms pro Bild. Reset ≥ 280 µs (V5) ergibt sich in Python von selbst.
- Bit-Banging (Rückfall) würde durch WLAN gestört; RMT nicht abschalten.

#### J7 flexibel: Kette, einzelne LED oder Taster

**Ja, ohne Bauteil im Datenpfad.** J7-2 ist IO23 direkt; alles Weitere sitzt im Kabel. Die Firmware erfährt per
Einstellung („J7: LED-Kette n / LED / Taster / aus“), was angeschlossen ist.

| Nutzung | Anschluss | Firmware | JP1/U6 |
|---|---|---|---|
| NeoPixel-Kette (auch 1 LED = „RGB-LED“) | J7-1 VLED, J7-2 über 330 Ω an DIN, J7-3 GND, 10–47 µF am Anfang | `neopixel` (RMT), IO15 = 1 zum Einschalten | U6 bestückt (oder JP1 zu) |
| einzelne einfarbige LED | J7-2 → Vorwiderstand → LED → J7-3; z. B. 470 Ω–1 kΩ für 2–3 mA | `machine.PWM` (LEDC, 6 Kanäle, Motor belegt 2) | **offen lassen** |
| Taster | J7-2 → Taster → J7-3, optional 1 kΩ in Reihe | `Pin.IN, Pin.PULL_UP`, IRQ, Wecken nur aus Light Sleep | offen lassen |
| analoge RGB-LED (4 Beine) | geht an J7 **nicht** (3 PWM-Pins nötig); stattdessen eine einzelne WS2812/SK6812 nehmen | – | – |

Ein DNP-Serienwiderstand auf der Platine (mit ritzbarer Brücke) bringt nichts, was der Widerstand im Kabel nicht
auch leistet, und kostet einen Router-Lauf mehr. **Empfehlung:** J7 bleibt 1 × 3 (1 VLED · 2 IO23 · 3 GND, VLED
nicht neben GND), dazu U6 + R22 + C17 + JP1 als DNP-Block.

### 0b.2 Vier Kabel-Taster (ein Taster bzw. Kontakt pro Arm)

#### Pin-Budget

Freie GPIOs: IO5, IO8, IO15, IO17, IO20, IO21, IO22, IO23 (acht). Fest vergeben nach 0b.1 bzw. Abschnitt 0:
IO22 Lastpuls, IO23 LED-Daten, IO15 LED-Versorgung, IO17 RXD. **Bleiben genau vier: IO5, IO8, IO20, IO21.**

| GPIO | Pull im Betrieb | Reset-Zustand (C6-DS Tab. 2-2) | Deep-Sleep-Wecken | Besonderheit |
|---|---|---|---|---|
| IO5 | intern 45 k | IE (offen) | **ja** (LP-GPIO5) | einziger freier ADC-Pin; N4-Vorbeschaltung |
| IO20 | intern 45 k | WPU | nein (Light Sleep ja) | – |
| IO21 | intern 45 k | WPU | nein | – |
| IO8 | **R11 10 k extern** (vorhanden) | IE + R11 | nein | Strapping: nur im Download-Modus (IO9 = 0) muss IO8 = 1 sein. Ein gedrückter Taster stört also nur, wenn gleichzeitig BOOT gedrückt wird. ROM-Log-Steuerung über IO8 nur mit gebrannter eFuse (unsicher). **Abschnitt 0 sagte „IO8 nicht herausführen“; als Taster-Eingang ist er aber geeignet, der Pull-up ist schon da** |
| (IO17 RXD) | intern | IE + WPU | nein | Ersatz für S4, dann ohne UART-RX |

#### Vergleich

| Kriterium | (a) 4 GPIOs mit Pull-up | (b) Widerstandsleiter an IO5 (ADC) | (c) I²C-Portexpander an J2 |
|---|---|---|---|
| Gleichzeitige Drücke | **ja, alle 16 Kombinationen** | Einzeldrücke sicher; 16 Kombinationen nur knapp (s. u.) | ja (8 Eingänge) |
| Latenz | Flanken-IRQ, Hardware µs, MicroPython-IRQ < 1–2 ms (unsicher bei WLAN-Last) | Polling: ADC-Abfrage in einer Python-Schleife, 1–5 ms Raster; kein Schwellwert-IRQ in MicroPython | INT → IRQ → I²C-Lesen (≈ 0,3 ms bei 100 kHz) ≈ 1–2 ms |
| Entprellung | Software 5–20 ms; optional 10 nF auf der Platine (τ = 0,45 ms mit 45 k) | Mittelung über mehrere Messungen | Software |
| Störfestigkeit / ESD, 40 cm Kabel | 45 k intern ist hochohmig neben 1–2 A Motor-PWM → optional 10 k extern (DNP), 1 kΩ in Reihe im Kabel, Ader mit GND verdrillt | Kontakt- und Steckerwiderstände verschieben die Pegel; ADC ±40 mV (C6-DS) | I²C nur kurz (Expander neben der Platine), Tasterleitungen wie (a) |
| Deep-Sleep-Wecken | nur S1 an IO5 (`wake_on_ext1`/`wake_on_gpio`; Bug #17334 bei „ALL_LOW“ beachten, siehe hauptplatine-c6.md 2.5). Nicht nötig: Der Hebel weckt | praktisch nein: der „leichteste“ Taster zieht IO5 nur auf 2,9 V, unter V_IL 0,83 V kommt nichts | ja, wenn INT auf einem LP-Pin liegt (s. u.) |
| Pads | 4 Signale + GND (+ 3V3) | 1 Signal + GND + 3V3 | keine neuen (J2), INT siehe unten |
| Verkabelung | je Arm 2 Adern, sternförmig | **eine 2-Ader-Leitung durch alle Arme** möglich | wie (a) ab Expander |
| Kosten | 0 € auf der Platine | 5 Widerstände | Expander-Breakout ca. 1–3 € |

**Zur Widerstandsleiter (b), gerechnet:** Pull-up R0 = 10 k (R19 aus N4) nach 3V3, Taster k mit eigenem
Widerstand nach GND, parallel. Beste E24-Werte (Suche über alle Kombinationen, 1 % Toleranz):
**11 k, 18 k, 36 k, 68 k**. Einzeldrücke: 2,88 / 2,57 / 2,11 / 1,71 V (Abstände > 300 mV, sicher). Alle
16 Kombinationen liegen zwischen 1,13 und 3,3 V, der **kleinste Abstand im ungünstigsten Fall ist nur 28 mV**,
weniger als die absolute ADC-Ungenauigkeit (±40 mV). Mit Einlernen pro Gerät ginge es, mit Motorstörungen und
Kontaktwiderstand nicht zuverlässig. Gleichzeitige Drücke sind beim Spiel aber der Normalfall.

**Zum Expander (c):** PCF8574/TCA9534/MCP23008 (Typ offen). **Achtung INT:** J2-5 /INT ist auf der Platine mit
LIS2DH12 INT1 (U4 Pad 12) verbunden, und der LIS2DH12 treibt Push-Pull (nur Polarität umschaltbar, unsicher). Ein
Open-Drain-INT des Expanders darf dort nicht dazu. INT des Expanders also an **IO5** (S1-Pad), nicht an J2-5, oder U4
weglassen. (c) lohnt sich nur, wenn mehr als vier Eingänge gebraucht werden (z. B. Joker-Taster **und**
Wippen-Kontakt je Arm = 8).

**Empfehlung: (a).** Pad-Belegung siehe 0b.4 (J6 „Spieler“).

#### Stecker und Kabel

- **Kein Stecker auf der Platine:** unten sind nur ca. 1,5 mm Höhe frei; JST-SH (ca. 2,9 mm, unsicher) und PH
  passen nicht. Litze an J6 anlöten.
- Von J6 eine **6-adrige Leitung** (z. B. Flachband 1,27 mm oder dünne Litze) durch das Kabelfenster in die Basis
  zu einem kleinen **Verteiler** (Lochraster oder Klemmleiste). Dort je Arm eine **steckbare 2-polige Verbindung**
  (JST-PH 2,0 mm oder XH 2,5 mm mit Crimpkontakten), weil die Arme für die Schachtel abgenommen werden. 40 cm je
  Arm, Signal und GND verdrillt.
- **1 kΩ in Reihe** je Signalader am Platinenende (Schrumpfschlauch). Zusammen mit dem optionalen 10-nF-Footprint
  ergibt das ein RC-Glied (τ = 10 µs) gegen Einstreuung und ESD-Spitzen. Drückpegel mit 1 k: 0,07 V (45 k intern)
  bzw. 0,30 V (IO8, R11 10 k), beides < V_IL 0,83 V.

### 0b.3 Wippe erkennen: LIS2DH12, Piezo oder Kontakt

#### Wofür „Wippe gedrückt“?

| Nutzung | Wert | Bemerkung |
|---|---|---|
| **Statistik** (Schläge pro Spieler, Reaktionszeit nach 🎭 Fake-out bzw. ⏪) | mittel | nur mit „📊 Statistik & Ausscheiden“ sichtbar |
| **Treffer-Zuordnung** | mittel bis hoch, experimentell | Stromspitze beim Treffer (ideen.md „Treffer-Ahnung“) + welche Wippe in den letzten ca. 300 ms gedrückt wurde → „Lena hat Louie getroffen“. Ohne Wippen-Sensor gibt es nur die Stromspitze ohne Namen |
| **Neue Modi** („Munition“: n Schläge pro Runde; Wippen-Sperre als Strafe, angezeigt statt erzwungen) | mittel | Modus-Baukasten bräuchte ein neues Ereignis |
| Fehlstart beim Countdown („Hände an die Wippen!“) | gering | eher Spaß-Anzeige |
| **Joker auslösen** über die Wippe (z. B. Doppelschlag) | **nein** | Schlagen ist die Spielhandlung; Fehlauslösungen sind sicher. Joker gehören auf Handy, Funk-Taster oder Kabel-Taster |
| Ausscheiden erkennen | nein | Hühner fallen unabhängig von der Wippe |

Fazit: Nettes Zusatzwissen, kein Grundbetrieb. Also nur über die optionalen Eingänge, keine eigenen Bauteile oben.

#### (a) LIS2DH12 auf der Platine (Batteriefach)

- Ein Schlag auf eine Wippe geht über den Arm in die Basis und kommt als Stoß am Sensor an. **„Es wurde
  geschlagen“ ist plausibel** (Tap-Erkennung mit Hochpass, Schwelle über dem Motorrauschen). Bis 1,344 kHz ODR
  im Low-Power-Modus (ST, unsicher) reichen für Stöße.
- **Welcher Arm?** Die Arme liegen 90° auseinander; die Richtung des Stoßes in X/Y und das Kippen der Basis
  enthalten im Prinzip eine Richtung. Mit einem Sensor neben der Mitte, Kunststoff-Verbindungen, Spiel in den
  Steckverbindungen und dem Motor obendrauf ist eine **zuverlässige Zuordnung nicht zu erwarten** (unsicher, messen).
  Vier Spieler schlagen oft fast gleichzeitig.
- **Motorvibration** liegt ständig an (Drehfrequenz plus Getriebe); sie überlagert besonders schwache Schläge.
- Weitere Nutzen bleiben: Anheben/Umkippen → Motor aus (Sicherheit), Schütteln, Deep-Sleep-Wecken über IO2.
- **Bewertung: oben behalten** (schon platziert, ca. 0,40 $, Bestückungsoption). Er ersetzt keinen Sensor pro Arm.

#### (b) Piezo auf der Platine

Nein. Die Platine steckt in der AA-Hülle im Batteriefach, mechanisch schlecht angekoppelt; sie würde dasselbe
messen wie der LIS2DH12 (Gesamterschütterung), nur schlechter. Oben ist kein Platz, unten ist die Bauhöhe
zu klein (Piezo-Summer ≥ 1,9 mm, K11).

#### (c) Piezo-Scheibe je Arm per Kabel

- **ADC-Pins:** Der C6 hat ADC1 an IO0–IO6 (C6-DS, 7 Kanäle). Belegt: IO0 VBAT, IO1 ISEN, IO3 SENSE, IO4
  VBUS_DET, IO6 SDA. **Frei nur IO5**; IO2 nur, wenn U4 und J2-INT nicht genutzt werden. Vier analoge Piezos
  gehen also nicht.
- **Digital geht:** Ein kräftiger Schlag erzeugt an einer Piezo-Scheibe mit 1 MΩ Last mehrere Volt bis einige
  10 V (unsicher, am Muster messen; Lastwiderstand bestimmt untere Grenzfrequenz und Amplitude, MSI-App-Note
  „Interfacing Piezo Film to Electronics“). Der C6-Eingang schaltet bei 2,48 V (V_IH). So
  wird der Eingang zum Komparator mit fester Schwelle, und leichtes Motorbrummen bleibt darunter.
- **Beschaltung je Arm (alles im Kabel bzw. am Piezo):** 1 MΩ parallel zur Scheibe (Ableitwiderstand, Arduino
  Knock-Beispiel), **100 kΩ in Reihe** zum Pin. Die internen Klemmdioden des C6 begrenzen dann auf 3,3 V + 0,5 V
  mit < 0,3 mA bei 30 V Spitze (gerechnet). Wer mehr Reserve will: BAT54S (SOT-23) am Kabelende. Kein RC nötig:
  Scheibe (20–27 mm, ca. 10–20 nF, unsicher) und 1 MΩ ergeben τ ≈ 10–20 ms, der Impuls wird ohnehin gestreckt.
  Firmware: `Pin.IN` ohne Pull, `IRQ_RISING`, 50–100 ms Totzeit.
- **Nicht an IO8** (R11 10 k zieht den Pegel hoch, der Impuls bricht über 100 k/10 k ein). Piezo-Kanäle: IO5,
  IO20, IO21, ersatzweise IO17. Auf J6 den 10-k-Pull-up-Footprint (R23–R25) für Piezo-Kanäle leer lassen.
- **Analog an IO5:** Nur ein Kanal, z. B. „Summe aller Arme“ mit einstellbarer Schwelle. MicroPython hat auf dem
  C6 nur Einzelmessungen (`ADC.read_u16`/`read_uv`, einige 10 µs, praktisch 1–5 kHz Abtastung in einer Python-Schleife,
  unsicher); die Hardware kann 100 kSPS, DMA und Schwellwert-Interrupt (C6-DS 4.2.2.1), das ist aber nur in C
  (IDF `adc_continuous`) erreichbar.
- **Übersprechen:** Ein Schlag auf Arm 1 erschüttert auch Arm 2. Mit fester digitaler Schwelle können Nachbararme
  mit auslösen; Gegenmittel „erste Flanke gewinnt, 20 ms sperren“ (unsicher, messen).
- **Kosten:** Scheibe 0,10–0,30 €, 2 Widerstände, Kabel (unsicher).

#### (d) Kontakt unter der Wippe = Kabel-Taster aus 0b.2

| Art | Montage | Vorteile | Nachteile |
|---|---|---|---|
| **Reedkontakt + Magnet** (ca. 0,20–0,50 € + 0,10 €, unsicher) | Reed im Arm unter dem Spielerende der Wippe, kleiner Magnet unter der Wippe | berührungslos, keine Kraft, verändert das Spielgefühl nicht, 2 Adern, kein Übersprechen | Glasröhrchen bruchempfindlich (einkleben), Schaltabstand einstellen |
| **Mikroschalter** (0,20–1 €) | am Anschlag der Wippe | eindeutig, robust | Betätigungskraft kann das Schlaggefühl ändern; Befestigung je Modell |
| Kupferfolien-Kontakt | zwei Folienstreifen an Wippe und Anschlag | fast gratis | Verschleiß, Wackelkontakt |
| Hall-Schalter DRV5032 (K8) | wie Reed | prellfrei | braucht 3V3 = 3 Adern (J6-1) |
| Piezo (c) | aufkleben | keine Mechanik | Übersprechen, Schwelle fest |

Ein Kontakt liefert genau die gewünschte Information („Spieler 3 hat geschlagen“), ohne Signalverarbeitung, ohne
Übersprechen, mit der Schaltung aus 0b.2. **Das ist die einfachste Lösung.** Ob Joker-Taster oder
Wippen-Kontakt an einem Eingang hängt, ist reine Firmware-Einstellung (in geraete-anlernen.md ein weiterer
„Eingang“: Gerät = Kabel, Taste = S1–S4). Beides gleichzeitig je Arm braucht 8 Eingänge → Joker über Handy
bzw. Funk-Taster (V1), Wippe über J6; oder Expander (0b.2 c).

**Empfehlung 0b.3:** LIS2DH12 **oben behalten**. **Kein Piezo** auf der Platine. Wippen-Erkennung pro Arm
optional über **Reedkontakt (bzw. Mikroschalter) an J6**, Piezo je Arm nur als Plan B an denselben Pads.
Vorher an einem Muster ausprobieren, ob ein Reed unter die Wippe passt (Mechanik je Modell, unsicher).

### 0b.4 Gesamtbelegung der freien GPIOs

| GPIO (Modulpad) | Funktion | Pad | Pull / Beschaltung unten (alles DNP) | Wecken |
|---|---|---|---|---|
| **IO5** (10) | **S1** Spieler 1 (Taster/Reed/Piezo); alternativ ADC (Leiter, NTC, Piezo-Summe) | **J6-2** | intern 45 k; R19/R20/C16 (N4) jetzt neben J6-2 | **Deep Sleep** (LP) |
| **IO20** (26) | **S2** | J6-3 | intern; R23 10 k → 3V3, C18 10 nF → GND | Light Sleep |
| **IO21** (27) | **S3** | J6-4 | intern; R24 10 k, C19 10 nF | Light Sleep |
| **IO8** (22) | **S4** (nur Taster/Reed, kein Piezo) | J6-5 | **R11 10 k oben (vorhanden)**; C20 10 nF | Light Sleep |
| **IO15** (20) | LED-Versorgung ein (U6 ON) | – | **R22 100 k → GND** | – |
| **IO17** RXD (30) | UART0-RX (Konsole) | **J3-5 (neu)** | – | – |
| **IO22** (28) | Lastpuls Powerbank (N1) | – | R18 Gate → GND: **4,7–10 k statt 100 k** (s. 0b.5) | – |
| **IO23** (29) | LED-Daten / LED / Taster | **J7-2** | – | Light Sleep |

Ersatz: Wer die UART-Konsole nicht braucht, kann S4 auf IO17 legen (dann piezo-tauglich). IO2 (INT) und IO6/IO7
(I²C) bleiben auf J2.

**Pads und Footprints unten (4 Lagen):**

| Ref | Art | Belegung | Lage (grob) | Platz |
|---|---|---|---|---|
| **J6 „Spieler“** | Pads 1 × 6, 2,54 mm, 1,4 mm | 1 3V3 · 2 S1 IO5 · 3 S2 IO20 · 4 S3 IO21 · 5 S4 IO8 · 6 GND | unter dem Modul parallel zu J3 (y ≈ +0,6), x ca. −13,6 … −0,9; Stiche von Pads 10/22/26/27 über In2 | ca. 15 × 2 mm = 30 mm² |
| R23, R24, C18–C20 | 0402 DNP | Pull-ups S2/S3, 10 nF S2–S4 | direkt an J6 | ca. 6 mm² |
| R19, R20, C16 (N4) | 0402 DNP | IO5 → 3V3 / GND | an J6-2 statt an J3-5 | ca. 8 mm² |
| **J3** (geändert) | wie bisher | 1 EN · 2 TXD · 3 BOOT · 4 GND · **5 RXD (IO17)** | wie bisher | – |
| **J7 „LED“** | Pads 1 × 3, 2,54 mm | 1 VLED · 2 IO23 · 3 GND | unter C1/C2, x ≈ +1 … +7, y ≈ −3,5 (wie Abschnitt 0) | 16 mm² |
| **U6** | TPS22918 SOT-23-6, DNP | IN = VSYS, OUT = VLED, ON = IO15, CT/QOD offen bzw. nach DS | neben J7, in der Tasche | ca. 12 mm² |
| **JP1** | Lötbrücke, offen | VSYS → VLED (Umgehung von U6) | neben U6 | 2 mm² |
| C17, R22 | 0805 10 µF / 0402 100 k, DNP | VLED → GND / IO15 → GND | an U6 | ca. 5 mm² |
| Q2, R17, R18 (N1) | wie Abschnitt 0, R18 4,7–10 k | Lastpuls | unter USB-C | 40 mm² |
| TP1–TP4 | wie Abschnitt 0 | VSYS, VBUS_J4, ISEN, SENSE | – | 8 mm² |

Summe ca. **150 mm²** von 382 mm² freier Unterseite (Abschnitt 0: 110 mm²). Alle Teile ≤ 1,45 mm (U6 an der
Grenze, prüfen), alle in |y| ≤ 4,5. **Nichts davon ist für den Grundbetrieb nötig**, die Platine läuft unbestückt
unten wie bisher. Bei 2 Lagen gilt weiter 0.5 (keine neuen Pads).

### 0b.5 Änderungen gegenüber Abschnitt 0

| Punkt in Abschnitt 0 | neu (0b) | Grund |
|---|---|---|
| J6 = 3V3, RXD, IO20, IO21, GND | J6 = 3V3, IO5, IO20, IO21, IO8, GND | vier Spieler-Eingänge an einem Block |
| J3-5 = IO5 | **J3-5 = RXD (IO17)** | J3 wird ein vollständiger Service-Anschluss (EN, TXD, RXD, BOOT, GND, z. B. für einen Pogo-Adapter); RXD-Pad 30 liegt an derselben Kante wie J3 |
| IO8, IO15 nicht herausführen | IO8 = S4 (Pull-up vorhanden), IO15 = LED-Versorgung ein | alle vier freien Eingänge gebraucht; beide Pins sind dafür unkritisch |
| J7 = VSYS über JP1 | VLED über **U6 (DNP) oder JP1** | Ruhestrom der LEDs im Deep Sleep |
| N1: R18 100 k Gate → GND | **R18 4,7–10 k** | IO22 hat beim Reset den internen 45-k-Pull-up (C6-DS Tab. 2-2). Mit 100 k läge das Gate bei 3,3 V · 100/145 ≈ 2,3 V, AO3400A (V_th 0,65–1,45 V, unsicher) leitet während Reset und Boot. Mit 4,7 k: 0,31 V. Nur mit USB relevant und kurz, aber unnötig |
| Boot-Glitches „nicht nachgelesen“ | Das C6-Datenblatt v1.5 hat **keine Glitch-Tabelle** (gesucht), nennt aber die Reset-Zustände: IO18–IO23 mit Pull-up beim Reset, IO5/IO8/IO15 nur Eingang | Folgen für IO22/IO23 oben berücksichtigt |

Vor dem Layout prüfen: TPS22918 ON-Schwelle und Bauhöhe, LIS2DH12-INT (Push-Pull, CTRL_REG6), ob IO8 als Eingang
mit gedrücktem Taster den normalen Boot wirklich nicht beeinflusst (am XIAO-C6 testen), Platz für J6 mit sechs Pads
neben den Stitching-Vias unter dem Modul.

### Quellen zu 0b

- ESP32-C6 Series Datasheet v1.5 (Tab. 2-2 Pin-Zustände, 4.2.1.11 RMT, 4.2.2.1 SAR ADC, Tab. 5-4/5-5):
  https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf
- WS2812B-Datenblatt (Worldsemi, Kopie Adafruit): https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf
- WS2812B-V5 (Worldsemi): https://learn.watterott.com/kb/ws281x/WS2812B-v5.pdf
- WS2812B-Mini-V3: https://learn.watterott.com/kb/ws281x/WS2812B-Mini-v3.pdf
- SK6812 (OPSCO, LCSC C5378720): https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2303300930_OPSCO-Optoelectronics-SK6812_C5378720.pdf
- 74AHC1G125/74AHCT1G125 (Nexperia): https://pdf.elecfans.com/p/5172803.html
- TI SN74LV1T34: https://www.ti.com/product/SN74LV1T34
- TI TPS22918 (Datenblatt SLVSD76): https://www.ti.com/lit/pdf/SLVSD76, LCSC C2680345
- Adafruit NeoPixel Überguide, Best Practices: https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices
- MicroPython `machine_bitstream.c` (ESP32, RMT bzw. Bit-Banging):
  https://github.com/micropython/micropython/blob/master/ports/esp32/machine_bitstream.c
- MicroPython `esp32`-Modul (RMT.bitstream_rmt, Wecken): https://docs.micropython.org/en/latest/library/esp32.html
- Arduino „Detect a Knock“ (Piezo mit 1 MΩ): https://docs.arduino.cc/built-in-examples/sensors/Knock
- Measurement Specialties (heute TE), App-Note 01800004-000 „Interfacing Piezo Film to Electronics“, Rev B 2006
  (Lastwiderstand, Puffer): https://pages.hmc.edu/spjut/NewE80/PDFs/PiezoElectronics.pdf

---

**Ab hier alter Stand (ESP32-C3, 2026-11-01).** Die folgenden Abschnitte 1–6 gelten für den verworfenen ESP32-C3 mit kaum freien Pins (Pins, Strapping auf IO2,
Bauhöhe vor der Hüllen-Tasche). Aktuell ist Abschnitt 0.

Ziel: Auf der **Unterseite** der AA-Platine (46 × 13,5 mm, 0,8 mm) nur Kupfer-Pads vorsehen. Wer will,
lötet die Bauteile selbst ein. Kein Bestückungsaufwand, keine Mehrkosten in der Fertigung.

Markierungen: **(geprüft)** = mit Quelle belegt · **(unsicher)** = aus dem Gedächtnis oder nur aus
Sekundärquelle, vor dem Layout im Datenblatt prüfen. Preise sind grobe LCSC-Richtwerte (Stück, Stand der
Recherche) und schwanken.

---

## 1. Randbedingungen (aus dem Projekt)

| Punkt | Wert |
|---|---|
| Platz unten | ca. 10 × 9 mm unter dem ESP-Modul (teils Testpads 1,5 mm), ca. 15 × 12 mm rechte Hälfte; Antennenende frei |
| Bauhöhe unten | max. ca. 1,0–1,2 mm (runde AA-Mulde) |
| Freie GPIOs | IO2, IO8 (je 10k Pull-up, als Testpads TP7/TP8 schon da), RXD = GPIO20, TXD = GPIO21, IO9 (BOOT) |
| ADC | nur GPIO0–4; GPIO0/1/3 belegt (VBAT_ADC, ISEN_ADC, SENSE) → nur **IO2** wäre noch ADC |
| Versorgung | 3,3 V aus AP2112K (600 mA, Ruhestrom 55 µA typ.), VSYS = LiPo 3,0–4,2 V |
| Motortreiber | DRV8833 mit **beiden Kanälen parallel** → kein zweiter Kanal frei (z. B. für Vibrationsmotor) |

### Drei harte Regeln für alles, was an die freien Pins kommt

1. **Strapping-Pins**: Beim Reset muss **IO2 = 1** sein (sonst bootet der Chip nicht aus dem Flash), **IO8 = 1**
   für den Download-Modus, **IO9** wählt den Boot-Modus (0 = Download). Kein Sensor darf diese Pins beim
   Reset nach unten ziehen. **(geprüft)** [Espressif DevKitM-1 Doku][c3-strap], [RIOT ESP32-C3][riot-c3]
2. **Aufwecken aus Deep Sleep geht beim ESP32-C3 nur über GPIO0–5.** Von den freien Pins ist das nur
   **IO2**. GPIO8/9/20/21 wecken nur aus Light Sleep. **(geprüft)** [ESP-IDF Sleep Modes][idf-sleep]
3. **TXD (GPIO21)** gibt beim Booten das ROM-Log aus, ist also kurz ein **Ausgang**. Dort nie einen
   Push-Pull-Ausgang eines Sensors anschließen (zwei Treiber gegeneinander). Ein-Signale (Interrupts) gehören
   auf **RXD (GPIO20)**. TXD eignet sich für Ausgaben (z. B. LED-Daten). **(unsicher, Standardverhalten des ROM)**

### Strombudget

- 3,3-V-Schiene: WLAN braucht Spitzen von einigen 100 mA. Alle unten genannten Sensoren liegen im
  µA- bis unteren mA-Bereich und belasten den LDO **nicht nennenswert**. Ausnahme wäre nur Licht/Ton mit
  Leistung – die hängt man an VSYS, nicht an 3,3 V.
- Schlafstrom: Der LDO selbst braucht schon **55 µA** ([AP2112-Datenblatt][ap2112]), der VBAT-Teiler
  470k/470k ca. 4,5 µA. ESP32-C3 im **Light Sleep ca. 130 µA**, im Deep Sleep wenige µA
  ([Espressif Low-Power-Grundlagen][esp-lp]). Ein Sensor mit 2–10 µA fällt daneben kaum ins Gewicht.
  Deep Sleep statt Light Sleep spart nur Faktor ~2–3, weil der LDO-Ruhestrom bleibt.

---

## 2. Handlötbarkeit der Gehäuse (Bewertung)

| Gehäuse | Anschlüsse sichtbar? | Lötkolben | Heißluft/Heizplatte | Bewertung |
|---|---|---|---|---|
| SOT-23 / SOT-23-6 | ja, Beinchen | gut | – | ★★★ leicht |
| 0402/0603 R/C | ja | gut | – | ★★★ |
| DFN/TDFN/QFN mit Pads bis zur Kante | teilweise (Kante) | mit Flussmittel und verzinnten Pads machbar | gut | ★★ mittel |
| WS2812-2020 (Pads unten, an der Kante) | kaum | machbar, LED hitzeempfindlich | gut | ★★ mittel |
| LGA (Beschleunigungssensoren, MEMS-Mikrofon) | **nein**, Pads komplett unter dem Gehäuse | Glücksspiel, ohne Sichtkontrolle | **ja**, mit Flussmittel; auch Heizplatte | ★ schwer |

LGA mit dem Lötkolben ist nicht unmöglich: Hobby-Breakouts verlängern die Pads nach außen, verzinnen sie vor,
setzen das Bauteil auf und erhitzen die herausstehenden Pad-Enden – überschüssiges Lot fließt nach außen
([hackaday.io LIS3DH-Breakout][hd-lis3dh], [FEDEVEL-Forum LGA von Hand][fedevel]). Kontrolle ist aber nur
elektrisch möglich (I²C-Scan, WHO_AM_I). **Ehrliche Einschätzung**: Wer nur einen Lötkolben hat, sollte mit
Fehlversuchen rechnen; mit Heißluft und Flussmittel ist ein 2 × 2-mm-LGA gut machbar.

**Konsequenz fürs Layout**: Für LGA-Teile auf der Unterseite eine Handlöt-Variante des Footprints anlegen
(Pads ca. 0,3–0,5 mm nach außen verlängert). Unten ist Platz-Kosten = Kupfer = gratis.

---

## 3. Kandidaten

### K1 – Beschleunigungssensor ST LIS2DH12TR (Favorit)

| | |
|---|---|
| Gehäuse | LGA-12, 2,0 × 2,0 × 1,0 mm **(geprüft)** [ST][st-lis2dh12] |
| Schnittstelle | I²C (Adresse 0x18/0x19 über SA0) oder SPI; 2 Interrupt-Ausgänge |
| Strom | 2 µA bei 1 Hz Low-Power, 3 µA bei 10 Hz, ca. 10 µA bei 100 Hz, Power-down 0,5 µA **(geprüft)** [ST][st-lis2dh12], [LCSC][lcsc-lis2dh12] |
| Funktionen | Klick/Doppelklick-(Tap-)Erkennung, Freier Fall, Lage (6D), Wake-up, FIFO, Temperatursensor |
| Handlöten | ★ LGA, siehe oben |
| Verfügbarkeit | LCSC C110926, ca. 0,40 $ **(geprüft, Preis schwankt)** |
| Beschaltung | 100 nF an VDD, SA0 und CS per Pad festlegen (CS = 1 → I²C) |
| Platz/Höhe | ca. 4 × 4 mm inkl. Kondensator; 1,0 mm hoch → **passt** (Grenzwert, aber im Rahmen) |

**Problem mit dem Interrupt**: INT1/INT2 sind nach dem Einschalten **aktiv-high, Push-Pull**, also im Ruhezustand
**low** **(unsicher, Register CTRL_REG6 im Datenblatt prüfen)**. Auf IO2 würde das beim Einschalten den
Strapping-Pin runterziehen → Boot-Fehler. Darum INT **auf RXD (GPIO20)** legen → Aufwecken nur aus Light Sleep.

Spielideen: Tisch-Klopfen/Taste hauen erkennen („Bonus-Schlag“, „Rückspuler“, Strafrunde für Wut-Hauer),
Spiel hochgehoben/umgekippt → Motor sofort aus (Sicherheit), Schütteln zum Starten/Würfeln, Lage-Erkennung
für andere Spielzeuge (Auto fährt bergauf, Roboter fällt um), Motor-Vibrationsanalyse (blockiert der Arm?).

**Achtung (unsicher, muss getestet werden)**: Bei Looping Louie läuft der Motor ständig und schüttelt das Gehäuse.
Ob ein Schlag auf die Spieler-Wippe sich deutlich genug vom Motor-Grundrauschen abhebt, muss man messen. Hochpass
im Sensor + Tap-Schwelle + Auswertung im ESP ist der Plan.

### K2 – ST LIS2DW12TR (Alternative mit konfigurierbarem Open-Drain-INT)

| | |
|---|---|
| Gehäuse | LGA-12, 2,0 × 2,0 × **0,7 mm** **(geprüft)** [ST][st-lis2dw12] |
| Schnittstelle | I²C/SPI, INT1/INT2 per Register auf **Open-Drain** und aktiv-low umschaltbar **(geprüft: Open-Drain)** [ST Community][st-lis2dw12-int] |
| Strom | ab ca. 1 µA im Low-Power-Modus (ST wirbt mit 50 nA Power-down) [ST Blog][st-blog-lis2dw12] |
| Handlöten | ★ LGA |
| Verfügbarkeit | LCSC C189624, ca. 0,45–0,90 $ **(Preise schwanken)** [LCSC][lcsc-lis2dw12] |
| Bewertung | Flacher (0,7 mm) und sparsamer als K1. Nach dem **Einschalten** gilt aber auch hier Push-Pull aktiv-high **(unsicher)** → gleiche INT-Regel wie K1. |

### K3 – Bosch BMA400 (Option für Deep-Sleep-Wecken über IO2)

| | |
|---|---|
| Gehäuse | LGA-12, 2,0 × 2,0 mm, Höhe je nach Quelle 0,65–0,95 mm **(unsicher)** [adom-Wiki BMA400][adom-bma400] |
| Schnittstelle | I²C (0x14/0x15)/SPI, 2 INT |
| Besonderheit | Interrupts laut Sekundärquelle **standardmäßig Push-Pull aktiv-low** → Ruhepegel **high** → IO2 bleibt beim Boot high **(unsicher, im Bosch-Datenblatt prüfen!)** |
| Strom | einige µA im Low-Power-Modus, extra für Wearables/„Always-on“ ausgelegt (Zahlen im Datenblatt prüfen) |
| Verfügbarkeit | LCSC C437655, ca. 1,80–3,00 $ [LCSC][lcsc-bma400] |
| Bewertung | Teurer, aber der einzige Kandidat, bei dem INT auf IO2 (Deep-Sleep-Wecken) ohne Zusatzteile denkbar ist. Dann muss I²C auf IO8 + GPIO20 (zusätzlicher 10k-Pull-up auf GPIO20 als 0402 unten). |

### K4 – Silan SC7A20TR (billiger Klon)

LGA-12 2 × 2 mm, laut Händlern registerkompatibel zum LIS2DH12, LCSC C5126709
([LCSC][lcsc-sc7a20]). Preis und Kompatibilität **unsicher**; Doku eher chinesisch. Nur interessant, wenn der
LIS2DH12 nicht lieferbar ist. Gleicher Footprint → kann als Zweitquelle im Footprint gleich mit gedacht werden.

### K5 – NXP MMA8452Q (QFN, handlötfreundlicher – aber auslaufend)

| | |
|---|---|
| Gehäuse | QFN-16, 3 × 3 × 1,0 mm; Pads reichen bis zur Gehäusekante **(geprüft: Maße)** [LCSC][lcsc-mma8452] |
| Schnittstelle | I²C (0x1C/0x1D), 2 INT |
| Handlöten | ★★ mit Flussmittel und Lötkolben machbar (Kantenpads sichtbar) |
| Verfügbarkeit | LCSC C11360, ca. 1,00–1,40 $, Status **„Not recommended for new designs“** [LCSC][lcsc-mma8452] |
| Bewertung | Handlöten deutlich einfacher als LGA, aber 3 × 3 mm, höherer Strom als K1/K2 und auslaufend. Als Notlösung für Lötkolben-Nutzer okay, nicht als Hauptempfehlung. |

**Fazit Beschleunigungssensor**: Einen modernen, sparsamen Beschleunigungssensor mit Beinchen (SOT/SOIC) gibt es
praktisch nicht – alle aktuellen Typen sind LGA. **Ehrlich: LGA geht sicher nur mit Heißluft/Heizplatte und
Flussmittel.** Für alle anderen: K6 (fertiges Breakout per Kabel).

### K6 – Lötpads für ein externes I²C-Modul (Qwiic/STEMMA QT per Kabel)

| | |
|---|---|
| Bauteil | **kein Bauteil**: 4 Pads in einer Reihe: 3V3 · GND · SDA (IO8) · SCL (IO2), optional 5. Pad INT (GPIO20) |
| Steckverbinder? | Original-Qwiic-Buchse JST SH 4-pol. (z. B. SM04B-SRSS-TB) ist **ca. 2,9 mm hoch** **(unsicher, Maß prüfen)** → **passt nicht** unter die Platine. Darum Kabel direkt anlöten (z. B. abgeschnittenes Qwiic-Kabel). |
| Strom | je nach Modul; viele Breakouts haben eine Power-LED (~1 mA) und eigenen LDO → für Deep Sleep LED-Jumper auftrennen |
| Handlöten | ★★★ trivial |
| Platz | ca. 8 × 2 mm; die vorhandenen Testpads TP1 (3V3), TP2 (GND), TP7 (IO2), TP8 (IO8) liefern **schon genau diese Signale** – nur in eine Reihe mit 2,54 mm Raster legen |
| Bewertung | **Beste Lösung für alle ohne Heißluft.** Kabel ragt aus dem Batteriefach (Deckel-Spalt) oder Modul liegt mit im Fach. Funktioniert mit hunderten fertigen Modulen (LIS3DH, LIS2DH12, BMA400, Licht, Abstand, Gesten, OLED). |

### K7 – TI TMAG5273 (3D-Hall-Sensor über I²C, mit Beinchen)

| | |
|---|---|
| Gehäuse | **SOT-23-6** (2,9 × 2,8 mm), Höhe ca. 1,1–1,45 mm **(Höhe unsicher, prüfen – evtl. knapp)** [TI][ti-tmag5273] |
| Schnittstelle | I²C, INT-Pin; Pinbelegung SCL, GND, GND, VCC, INT, SDA |
| Strom | 2,3 mA aktiv, **1 µA** Wake-up-and-Sleep-Modus (weckt per INT bei Magnetfeldschwelle), 5 nA Sleep **(geprüft)** [TI][ti-tmag5273] |
| Handlöten | ★★★ |
| Spielideen | Umdrehungen des Arms zählen (Magnet am Arm/Zahnrad), Magnet-„Spielsteine“ erkennen, Deckel/Hebel-Stellung, Joystick-artige Bedienung mit Magnet |
| Bewertung | Einzige Sensor-Idee mit echten Beinchen am I²C-Bus. **Unsicher**: Ob der Magnet vom Batteriefach aus überhaupt nah genug an bewegte Teile kommt, hängt vom Spielzeug ab. Bei Looping Louie ist die Drehzahl schon über ISEN/SENSE (Motor-Stromwelligkeit) zugänglich. |

### K8 – TI DRV5032 (Hall-Schalter)

| | |
|---|---|
| Gehäuse | SOT-23 (2,92 × 2,37 mm) oder X2SON 1,4 × 1,1 × 0,4 mm **(geprüft)** [TI][ti-drv5032] |
| Schnittstelle | 1 digitaler Ausgang → braucht einen eigenen GPIO |
| Strom | 0,54 µA (5-Hz-Variante, 1,8 V) **(geprüft)** |
| Handlöten | SOT-23 ★★★, X2SON ★ |
| Bewertung | Sehr sparsam, aber frisst einen GPIO. Auf IO9 nur mit Open-Drain-Variante und nur, wenn beim Reset kein Magnet in der Nähe ist (sonst Download-Modus). Besser K7 nehmen (teilt den I²C-Bus). |

### K9 – Adressierbare RGB-LED WS2812B-2020

| | |
|---|---|
| Gehäuse | 2,0 × 2,0 × **0,84 mm** **(geprüft)** [WS2812B-2020-Datenblatt (TME)][ws2812-2020] |
| Versorgung | VDD **3,7–5,3 V** → an VSYS (LiPo 3,0–4,2 V): **unterhalb 3,7 V außerhalb der Spezifikation**, Blau/Grün werden schwächer oder Ausfälle **(Risiko)** |
| Datenpegel | 3,3-V-Logik bei VDD 4,2 V: VIH = 0,7 × VDD ≈ 2,9 V → knapp, meist okay **(unsicher)** |
| Strom | bis ca. 12 mA je Farbe; Ruhestrom je nach Version < 0,6 mA (alt) bzw. ≤ 1 µA (V6) [Datenblatt][ws2812-2020] |
| GPIO | 1 Ausgang → **TXD (GPIO21)** (RMT). Nebenwirkung: ROM-Bootlog auf TXD kann die LED beim Start kurz zufällig aufleuchten lassen. |
| Handlöten | ★★ |
| Bewertung | **Sinn fraglich**: Die Unterseite liegt im geschlossenen Batteriefach – Licht sieht niemand. Nur nützlich bei transparentem Gehäuse oder als Lichtleiter-Effekt. Statt LED auf der Platine lieber Pads für eine **externe** LED-Kette (VSYS, GND, DIN) vorsehen, die man nach außen führt. |

### K10 – I²S-MEMS-Mikrofon TDK ICS-43434

| | |
|---|---|
| Gehäuse | LGA-6, 3,5 × 2,65 × 0,98 mm **(geprüft)** [LCSC/JLC][jlc-ics43434], [TDK][tdk-ics43434] |
| Schnittstelle | I²S (SCK, WS, SD) → **3 GPIOs** |
| Strom | ca. 550 µA aktiv |
| Verfügbarkeit | LCSC C5656610, ca. 1,30 $ |
| Hinweis | ESP32-C3 kann **kein PDM-RX** → PDM-Mikrofone fallen weg, nur Standard-I²S geht **(geprüft)** [ESP-IDF I2S][idf-i2s] |
| Bewertung | Bottom-Port → bräuchte ein Schallloch durch die Platine, oben ist aber alles bestückt. Braucht 3 Pins (GPIO20, GPIO21 und IO9 oder den I²C-Bus aufgeben). Im geschlossenen Fach gedämpft. **Klatschen/Lautstärke-Spiele wären nett, aber für diese Platine eher nein.** Klopfen erkennt K1 besser (Körperschall). |

### K11 – Ton: Piezo-Summer bzw. „Motor als Lautsprecher“

- Flachster gängiger SMD-Piezo-Summer Murata PKMCS0909E4000-R1: 9 × 9 × **1,9 mm** **(geprüft)**
  ([RS][rs-pkmcs]); die PKLCS1212-Serie ist ca. 3 mm hoch ([TTI][tti-pkl]). → **Zu hoch** für die Unterseite.
- **Kostenlose Alternative**: Den Spielzeugmotor über den DRV8833 mit Tonfrequenz-PWM ansteuern (Piepsen,
  Melodien, „Startsignal“), wie es Drohnen-Regler machen. Braucht keine Hardware. Lautstärke und Klang hängen vom
  Motor ab **(unsicher, testen)**.
- Externer Piezo-Summer per Kabel an Pads (1 GPIO, z. B. TXD) ist möglich.

### K12 – Akku-Ladezustand Analog Devices (Maxim) MAX17048

| | |
|---|---|
| Gehäuse | TDFN-8, 2 × 2 mm, ca. 0,75–0,8 mm hoch, mit Exposed Pad **(Höhe unsicher)** |
| Schnittstelle | I²C, Adresse **0x36** (kein Konflikt mit Beschleunigungssensoren) |
| Strom | 23 µA aktiv, **3 µA Hibernate** **(geprüft)** [Flux/LCSC][flux-max17048] |
| Verfügbarkeit | LCSC C2682616 |
| Handlöten | ★★ Kantenpads gut; das Exposed Pad lässt sich von unten nicht per Durchkontaktierung löten (oben ist bestückt) – ob es angeschlossen sein **muss**, im Datenblatt prüfen **(unsicher)** |
| Bewertung | Liefert echten Ladezustand in % (ModelGauge). Nice-to-have: Die Platine misst VBAT schon über den Teiler an GPIO0/1. Geringe Priorität. |

### K13 – Temperatur/Feuchte Sensirion SHT40

DFN-4, ca. 1,5 × 1,5 × 0,5 mm, I²C 0x44, sehr geringer Ruhestrom **(Werte aus dem Gedächtnis, unsicher)**.
**Geringer Nutzen**: Der ESP32-C3 hat einen internen Temperatursensor, der LIS2DH12 auch. Feuchte im Batteriefach
ist für Spielzeug uninteressant. Höchstens für „Wetterstation-Spielereien“ – dann lieber per K6 extern.

### K14 – Lichtsensor (z. B. Lite-On LTR-303ALS-01, I²C)

Ca. 2 × 2 × 0,7 mm, I²C **(Maße unsicher)**. Im geschlossenen Batteriefach ist es dunkel → Nutzen fast nur
„Batteriefach geöffnet“-Erkennung. **Nicht empfohlen** auf der Platine; extern per K6 sinnvoll (z. B.
„Licht aus → Nachtmodus“).

### K15 – Taster

Taster im Batteriefach erreicht niemand. Sinnvoll: **Pads für einen externen Taster** an IO9 (BOOT) + GND, Kabel
nach außen (z. B. „Spiel-Taste“ am Gehäuse). IO9 hat einen internen Pull-up; Taster darf beim Einschalten nicht
gedrückt sein (sonst Download-Modus) – für einen Spielknopf vertretbar. Flache SMD-Taster (z. B. Alps SKTA-Serie,
2,6 × 1,6 mm) gibt es, Höhe und Bauform aber **unsicher** ([Mouser SKTA][mouser-skta]).

### K16 – Piezo-Scheibe als Klopfsensor an IO2 (ADC)

Eine externe Piezo-Scheibe (z. B. 20 mm) mit 1-MΩ-Ableitwiderstand und Schutzdiode/-widerstand an IO2 (ADC)
erkennt Klopfen sehr gut und kostet Cent. **Konflikt**: IO2 ist dann für I²C verloren und der Strapping-Pin
darf beim Boot nicht low werden (Ableitwiderstand gegen GND vs. 10k Pull-up: Pegel bleibt high, solange der
Widerstand ≥ 100 kΩ ist). Nur interessant, wenn man auf I²C ganz verzichtet.

---

## 4. Übersicht

| # | Bauteil | Funktion | Gehäuse / Höhe | Pins | Ruhestrom | Löten | Passt unten? |
|---|---|---|---|---|---|---|---|
| K1 | LIS2DH12TR | Beschleunigung | LGA-12 2×2 / 1,0 | I²C + INT (GPIO20) | 0,5–2 µA | ★ | ja |
| K2 | LIS2DW12TR | Beschleunigung | LGA-12 2×2 / 0,7 | I²C + INT | ~1 µA | ★ | ja |
| K3 | BMA400 | Beschleunigung | LGA-12 2×2 / ≤0,95 | I²C + INT (IO2 möglich) | µA | ★ | ja |
| K4 | SC7A20TR | Beschl. (Klon) | LGA-12 2×2 | I²C + INT | ? | ★ | ja |
| K5 | MMA8452Q | Beschleunigung | QFN-16 3×3 / 1,0 | I²C + INT | höher | ★★ | ja, NRND |
| K6 | 4–5 Pads | externes I²C-Modul | – | I²C (+INT) | modulabh. | ★★★ | ja |
| K7 | TMAG5273 | 3D-Hall | SOT-23-6 / ~1,1–1,45 | I²C + INT | 1 µA | ★★★ | Höhe prüfen |
| K8 | DRV5032 | Hall-Schalter | SOT-23 / X2SON | 1 GPIO | 0,5 µA | ★★★/★ | ja, GPIO knapp |
| K9 | WS2812B-2020 | RGB-LED | 2×2 / 0,84 | TXD | ≤1 µA–0,6 mA | ★★ | ja, aber unsichtbar |
| K10 | ICS-43434 | Mikrofon I²S | LGA-6 / 0,98 | 3 GPIO | 550 µA aktiv | ★ | nein (Pins, Schallloch) |
| K11 | Piezo-Summer | Ton | 9×9 / 1,9 | 1 GPIO | – | ★★★ | nein (Höhe) |
| K12 | MAX17048 | Akku-% | TDFN 2×2 / ~0,8 | I²C | 3 µA | ★★ | ja |
| K13 | SHT40 | Temp./Feuchte | DFN 1,5×1,5 / 0,5 | I²C | sehr gering | ★★ | ja, wenig Nutzen |
| K14 | LTR-303ALS | Licht | ~2×2 / 0,7 | I²C | gering | ★★ | ja, wenig Nutzen |
| K15 | Taster-Pads | Bedienung | – | IO9 | 0 | ★★★ | ja |
| K16 | Piezo-Scheibe | Klopfen (analog) | extern | IO2 (ADC) | 0 | ★★★ | statt I²C |

---

## 5. Empfehlung

### Pinbelegung

| Pin | Funktion | Begründung |
|---|---|---|
| **IO8** | I²C **SDA** | IO8 ist nur für den Download-Modus relevant. Hängt ein Slave nach einem Reset mitten in einer Übertragung und hält SDA low, bootet der Chip trotzdem normal aus dem Flash. |
| **IO2** | I²C **SCL** | IO2 muss beim Boot high sein. SCL wird von Slaves nicht aktiv runtergezogen (außer Clock-Stretching, das die genannten Sensoren nach meinem Kenntnisstand nicht nutzen – **unsicher**) → sicherer als SDA auf IO2. |
| **GPIO20 (RXD)** | Sammel-INT (Beschleunigung, ggf. Hall) | kein Strapping-Pin, beim Boot Eingang; weckt aus Light Sleep |
| **GPIO21 (TXD)** | frei / externe WS2812-Kette oder Summer | Ausgang, ROM-Log beim Boot beachten |
| **IO9** | externe Spiel-Taste | ist ohnehin BOOT |

Beide Pull-ups (10k) für I²C sind schon vorhanden. Firmware: beim Start I²C-Bus-Recovery (9 SCL-Takte).
Mehrere INT-Quellen an GPIO20 nur mit Open-Drain-Ausgängen zusammenschalten (+ 10k-Pull-up als 0402-Pad), sonst
nur einen INT anschließen.

Hinweis UART: Wenn GPIO20/21 belegt sind, entfällt die serielle Konsole auf diesen Pins. Programmieren und Log
laufen weiter über USB (USB-Serial-JTAG an GPIO18/19), das ist auf der Platine bereits so geplant.

### Top 4 (passen zusammen auf die Unterseite, nur I²C + 1 INT)

1. **K6 – I²C-Pads für externes Modul (Pflicht, gratis).** 3V3 · GND · SDA · SCL · INT in einer Reihe im
   2,54-mm-Raster (vorhandene Testpads umsortieren). Rettungsanker für alle ohne Heißluft und für jede künftige Idee.
2. **K1 – LIS2DH12TR (oder K2 LIS2DW12TR) mit Handlöt-Footprint**, INT1 → GPIO20, SA0 per Lötbrücke.
   Klopfen, Anheben/Umkippen (Sicherheitsstopp), Schütteln. ~0,40 $, 2 µA. Footprint so wählen, dass auch
   SC7A20 (K4) passt. Ehrlich dokumentieren: Einlöten mit Heißluft/Heizplatte, Lötkolben nur mit Erfahrung.
3. **K12 – MAX17048** (optional): echter Akku-Ladezustand in der App, selbe zwei Leitungen, 3 µA.
   Kantenpads lötbar; Exposed-Pad-Frage vorher klären.
4. **K15 – Pads für externen Taster an IO9** (gratis).

Ersatzweise statt K12: **K7 TMAG5273** als Hall-Sensor mit Beinchen, wenn ein Spielzeug einen Magnet-Anwendungsfall
hat – vorher die Bauhöhe des SOT-23-6 prüfen (evtl. > 1,2 mm).

### Platzschätzung

| Block | Fläche | Ort |
|---|---|---|
| LIS2DH12 + 100 nF (Handlöt-Pads) | ca. 4 × 4 mm | rechte Hälfte (15 × 12 mm) |
| MAX17048 + 2 × C | ca. 4 × 4 mm | rechte Hälfte |
| 5 Pads I²C/INT, 2,54 mm | ca. 12 × 2 mm (oder 1,5-mm-Pads mit 2,0 mm Raster: ca. 10 × 2 mm) | unter dem ESP-Modul (vorhandene Testpads), Antennenende frei |
| 2 Pads Taster | ca. 4 × 2 mm | Rest |

Alles hat in 15 × 12 mm + 10 × 9 mm Platz; alle Bauteile ≤ 1,0 mm hoch.

### Bewusst nicht empfohlen

Piezo-Summer (zu hoch → stattdessen Motor-Töne), Mikrofon (3 Pins, Schallloch, kein PDM-RX), RGB-LED auf der
Platine (im Fach unsichtbar, VDD-Spezifikation ab 3,7 V), Qwiic-Buchse (2,9 mm hoch), Vibrationsmotor (kein
freier Treiberkanal, zu dick), Licht/Feuchte auf der Platine (im Fach sinnlos).

---

## 6. Risiken und offene Punkte

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| Sensor zieht IO2 beim Reset low | Platine bootet nicht | Kein Push-Pull-INT auf IO2; SCL statt SDA auf IO2; nur Open-Drain/aktiv-low-Quellen (BMA400 prüfen) |
| I²C-Slave hält SDA nach Reset low | Bus hängt | SDA auf IO8 (bootet trotzdem), Bus-Recovery in Firmware |
| Deep-Sleep-Wecken durch Sensor | nur über IO2 möglich | Light Sleep (130 µA) akzeptieren – der LDO braucht ohnehin 55 µA; oder Variante K3 (BMA400-INT auf IO2, I²C auf IO8 + GPIO20) |
| Motorvibration überdeckt Klopfen | Fehlerkennung | Messen; Schwelle, Hochpass, Auswertung nur in Motorpausen |
| Bauhöhe | Platine klemmt in der AA-Mulde | nur Teile ≤ 1,0 mm; TMAG5273/SOT-23-6 vor Einsatz messen |
| LGA nicht lötbar ohne Heißluft | Frust beim Nutzer | Handlöt-Footprint + Alternative K6 klar dokumentieren |
| Strom | gering | Sensoren < 30 µA; externe Breakouts: Power-LED abtrennen |
| Antennennähe | schlechteres WLAN | keine Kupferflächen/Bauteile im Antennen-Freibereich, auch nicht unten |
| GPIO20/21 für Sensoren belegt | keine UART-Konsole | USB-Serial-JTAG nutzen |

Vor dem Layout im Datenblatt prüfen: LIS2DH12-INT-Reset-Polarität (CTRL_REG6), BMA400-INT-Reset-Werte,
MAX17048 Exposed Pad, TMAG5273-Höhe (DBV), Clock-Stretching der gewählten Slaves.

---

## Quellen

- `c3-strap` – Espressif, ESP32-C3-DevKitM-1 (Strapping-Pins): https://docs.espressif.com/projects/arduino-esp32/en/latest/boards/ESP32-C3-DevKitM-1.html
- `riot-c3` – RIOT OS, ESP32-C3 family: https://doc.riot-os.org/group__cpu__esp32__esp32c3.html
- `idf-sleep` – ESP-IDF Sleep Modes (ESP32-C3, `esp_deep_sleep_enable_gpio_wakeup` nur GPIO0–5): https://docs.espressif.com/projects/esp-idf/zh_CN/release-v5.1/esp32c3/api-reference/system/sleep_modes.html
- `idf-i2s` – ESP-IDF I2S (ESP32-C3: kein PDM-RX): https://docs.espressif.com/projects/esp-idf/en/release-v5.3/esp32c3/api-reference/peripherals/i2s.html
- `esp-lp` – Espressif Low-Power-Grundlagen: https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/performance/lowpower/lowpower-fundamental.html
- `ap2112` – AP2112-Datenblatt: https://cdn.sparkfun.com/assets/2/e/d/f/2/AP2112_datasheet.pdf
- `st-lis2dh12` – ST LIS2DH12: https://www.st.com/en/mems-and-sensors/lis2dh12.html
- `lcsc-lis2dh12` – LCSC LIS2DH12TR C110926: https://www.lcsc.com/product-detail/Motion-Sensors-Accelerometers_STMicroelectronics_LIS2DH12TR_STMicroelectronics-LIS2DH12TR_C110926.html
- `st-lis2dw12` – ST LIS2DW12: https://www.st.com/en/mems-and-sensors/lis2dw12.html
- `st-lis2dw12-int` – ST Community, LIS2DW12 Interrupt-Pins: https://community.st.com/mems-sensors-48/lis2dw12-how-are-the-interrupt-pins-internally-connected-74391
- `st-blog-lis2dw12` – ST Blog LIS2DW12: https://blog.st.com/?p=45925
- `lcsc-lis2dw12` – LCSC LIS2DW12TR C189624: https://lcsc.com/product-detail/Accelerometers_ST-LIS2DW12TR_C189624.html
- `adom-bma400` – BMA400 Hardware-Referenz (Sekundärquelle): https://wiki.adom.inc/adom/bma400-1-593000
- `lcsc-bma400` – LCSC BMA400 C437655: https://www.lcsc.com/product-image/C437655.html
- `lcsc-sc7a20` – LCSC SC7A20TR C5126709: https://www.lcsc.com/product-detail/Attitude-Sensor-Gyroscope_Hangzhou-Silan-Microelectronics-SC7A20TR_C5126709.html
- `lcsc-mma8452` – LCSC MMA8452QR1 C11360: https://www.lcsc.com/product-detail/C11360.html
- `hd-lis3dh` – hackaday.io, LIS3DH-Breakout (Handlöten LGA): https://hackaday.io/project/8369-lis3dh-breakout-board
- `fedevel` – FEDEVEL-Forum, LGA von Hand löten: https://fedevel.com/forum/beginners/17960-how-to-solder-packages-lga-and-others-by-hand
- `ti-tmag5273` – TI TMAG5273: https://www.ti.com/product/TMAG5273
- `ti-drv5032` – TI DRV5032: https://www.ti.com/product/DRV5032
- `ws2812-2020` – WS2812B-2020 V6 Datenblatt (TME): https://www.tme.com/Document/f57342b0dc3e7d573aa1f8b6b5942fcf/WS2812B-2020-V6_V1.2_EN.pdf
- `jlc-ics43434` – JLCPCB/LCSC ICS-43434 C5656610: https://jlcpcb.com/partdetail/ICS-43434/C5656610
- `tdk-ics43434` – TDK ICS-43434: https://invensense.tdk.com/en-us/products/ics-43434
- `rs-pkmcs` – RS, Murata PKMCS0909E4000 (9 × 9 × 1,9 mm): https://uk.rs-online.com/web/p/piezo-buzzers/9010898P
- `tti-pkl` – TTI, Murata PKL-Serie: https://www.tti.com/content/ttiinc/en/manufacturers/murata/products/murata-pkl-surface-mount-piezoelectric-sounders.html
- `flux-max17048` – MAX17048 (LCSC C2682616): https://www.flux.ai/lcsc/max17048gplust10~jvyd.md
- `mouser-skta` – Mouser, Alps SKTA: https://www.mouser.com.tr/new/alps-alpine/alps-skta-smt-tact-switches

[c3-strap]: https://docs.espressif.com/projects/arduino-esp32/en/latest/boards/ESP32-C3-DevKitM-1.html
[riot-c3]: https://doc.riot-os.org/group__cpu__esp32__esp32c3.html
[idf-sleep]: https://docs.espressif.com/projects/esp-idf/zh_CN/release-v5.1/esp32c3/api-reference/system/sleep_modes.html
[idf-i2s]: https://docs.espressif.com/projects/esp-idf/en/release-v5.3/esp32c3/api-reference/peripherals/i2s.html
[esp-lp]: https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/performance/lowpower/lowpower-fundamental.html
[ap2112]: https://cdn.sparkfun.com/assets/2/e/d/f/2/AP2112_datasheet.pdf
[st-lis2dh12]: https://www.st.com/en/mems-and-sensors/lis2dh12.html
[lcsc-lis2dh12]: https://www.lcsc.com/product-detail/Motion-Sensors-Accelerometers_STMicroelectronics_LIS2DH12TR_STMicroelectronics-LIS2DH12TR_C110926.html
[st-lis2dw12]: https://www.st.com/en/mems-and-sensors/lis2dw12.html
[st-lis2dw12-int]: https://community.st.com/mems-sensors-48/lis2dw12-how-are-the-interrupt-pins-internally-connected-74391
[st-blog-lis2dw12]: https://blog.st.com/?p=45925
[lcsc-lis2dw12]: https://lcsc.com/product-detail/Accelerometers_ST-LIS2DW12TR_C189624.html
[adom-bma400]: https://wiki.adom.inc/adom/bma400-1-593000
[lcsc-bma400]: https://www.lcsc.com/product-image/C437655.html
[lcsc-sc7a20]: https://www.lcsc.com/product-detail/Attitude-Sensor-Gyroscope_Hangzhou-Silan-Microelectronics-SC7A20TR_C5126709.html
[lcsc-mma8452]: https://www.lcsc.com/product-detail/C11360.html
[hd-lis3dh]: https://hackaday.io/project/8369-lis3dh-breakout-board
[fedevel]: https://fedevel.com/forum/beginners/17960-how-to-solder-packages-lga-and-others-by-hand
[ti-tmag5273]: https://www.ti.com/product/TMAG5273
[ti-drv5032]: https://www.ti.com/product/DRV5032
[ws2812-2020]: https://www.tme.com/Document/f57342b0dc3e7d573aa1f8b6b5942fcf/WS2812B-2020-V6_V1.2_EN.pdf
[jlc-ics43434]: https://jlcpcb.com/partdetail/ICS-43434/C5656610
[tdk-ics43434]: https://invensense.tdk.com/en-us/products/ics-43434
[rs-pkmcs]: https://uk.rs-online.com/web/p/piezo-buzzers/9010898P
[tti-pkl]: https://www.tti.com/content/ttiinc/en/manufacturers/murata/products/murata-pkl-surface-mount-piezoelectric-sounders.html
[flux-max17048]: https://www.flux.ai/lcsc/max17048gplust10~jvyd.md
[mouser-skta]: https://www.mouser.com.tr/new/alps-alpine/alps-skta-smt-tact-switches
