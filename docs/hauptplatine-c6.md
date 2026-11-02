# Hauptplatine mit ESP32-C6: Flash, Pinbelegung, Motortreiber, Zigbee, Umbau-Paket

Stand: 2026-11-02 · **Entscheidung des Auftraggebers: Wechsel von ESP32-C3-MINI-1 auf ESP32-C6-MINI-1, der C3 ist
verworfen.** Dieses Dokument baut auf [analyse-funk-controller.md](analyse-funk-controller.md) 3b,
[idee-usb-c-hauptplatine.md](idee-usb-c-hauptplatine.md) (Variante E) und [hardware-konzept.md](hardware-konzept.md)
auf und ist die Vorlage für den Umbau-Agenten. Der Umbau ist erfolgt, das Ergebnis steht in Kapitel 8.

Markierungen: **(geprüft)** = Quelle gelesen oder an den Projektdateien nachgerechnet · **(unsicher)** = Sekundärquelle,
Schätzung oder nicht im Datenblatt nachgelesen.

## Kurzfassung

- **Modul:** ESP32-C6-MINI-1 im **gleichen Footprint**. Ziel ist **-H8 (8 MB)**, Rückfall **-N4**. Beide sind
  pin- und footprintgleich, man entscheidet also erst bei der Bestellung. Das H8 ist bei Mouser lieferbar, bei
  JLC/LCSC aktuell **nicht**. Andere C6-Module passen nicht ins AA-Format oder haben mit PCB-Antenne nur 4 MB.
  Ein Chip-Design (C6FH8 + eigene Antenne) lohnt nicht.
- **Footprint:** Die Pads sind identisch zum C3 (bis auf 5 µm). **Nicht** den KiCad-Footprint `RF_Module:ESP32-C6-MINI-1`
  nehmen: Sein Courtyard enthält eine 43 × 20 mm große Antennen-Sperrzone. Das bricht `antenna_keepout()`, und ein
  3D-Modell fehlt.
- **Motortreiber:** **DRV8213DSG** (WSON-8 2 × 2 mm) statt DRV8833. Er hat eine Strommessung (IPROPI), eine
  Strombegrenzung und Autosleep eingebaut. Damit entfallen Shunt, VINT/VCP-Kondensatoren, nSLEEP und nFAULT.
  Das spart **ca. 39 mm²**, 3 Bauteile, 2 GPIOs und ca. 0,47 USD. **Das ist der größte Platzgewinn für USB-C.**
- **Hebel-Pegel umdrehen** (R3 nach GND, R4 nach 3V3): „Hebel zu“ = HIGH. Dann weckt der Hebel mit
  `WAKEUP_ANY_HIGH`, und der offene MicroPython-Fehler mit `WAKEUP_ALL_LOW` (#17334) betrifft den Normalfall nicht.
- **Zigbee:** Die Hardware braucht **nichts zusätzlich**. Ein Coordinator neben dem eigenen Hotspot wird von
  Espressif aber **nicht unterstützt (X)**, neben BLE-Scan ebenfalls nicht. Zigbee ist also nur im Heim-WLAN
  realistisch und nur in C (ESP-IDF). Vorsehen lässt sich jetzt nur das 8-MB-Flash.
- **Priorität A vor Sensor:** Der LIS2DH12 zieht auf **I²C/INT-Lötpads** um (Breakout oder später Platine B).
  Das bringt allein nur ca. 9 mm². Zusammen mit dem DRV8213 reicht der Platz für Variante E aber rechnerisch
  deutlich.
- **Kosten (10 Stück, inkl. USB-C-Stufe):** Bauteile ca. **+0,45 USD** pro Board mit C6-N4 bzw. **+2,3 USD** mit H8.
  Dazu kommen netto 2 Extended-Typen mehr (**+6 USD je Auftrag**). Zusammen ca. **+1,1 / +2,9 USD pro Board**.

---

## 1. Flash: Gibt es mehr als 4 MB im AA-Format?

| Kandidat | Maße (mm) | Flash | Antenne | Lieferbarkeit / Preis (2026-11-02) | Bewertung |
|---|---|---|---|---|---|
| **ESP32-C6-MINI-1-N4** (C5736265) | 13,2 × 16,6 × 2,4 | 4 MB | PCB | LCSC 1.380, JLC 3.921 Stk.; 4,14 / 3,63 USD (1/10) (geprüft) | **Rückfall**, sofort bestückbar |
| ESP32-C6-MINI-1-H4 (C6553337) | gleich | 4 MB, 105 °C | PCB | JLC 534; 4,48 / 3,84 (geprüft) | kein Vorteil |
| **ESP32-C6-MINI-1-H8** (C42403058) | gleich | **8 MB**, 105 °C | PCB | **LCSC/JLC 0 Stk.**; LCSC 11,67 (1), 4,66 (200+) (geprüft). **Mouser ca. 4,70 €, ca. 6.000 Stk.** (unsicher, Suchtreffer) | **Ziel**, über JLC Global Sourcing bzw. Vorbestellung oder als beigestelltes Teil |
| ESP32-C6-MINI-1U-H4 (C20627095) | 13,2 × 12,5 | 4 MB | U.FL | JLC 3.938; 4,20 (geprüft) | nur Plan B Antenne; ein 1U-H8 ist bei LCSC nicht gelistet |
| u-blox NORA-W406-00B (C42859755) | 10,4 × 14,3 × 1,9 | **4 MB** | PCB | JLC 10 Stk., 8,07 USD (geprüft) | 8 MB nur als NORA-W401-10B **ohne** PCB-Antenne (Antennenpin) (unsicher). Teurer, anderer Footprint, kein Gewinn |
| Ai-Thinker ESP-C6-12F | ca. 24 × 16 (unsicher) | 4 MB | PCB | – | **zu breit** (> 14,5 mm) |
| Seeed XIAO ESP32-C6 | 21 × 17,5 | 4 MB | PCB | – | Board, kein Modul; zu breit |
| Quectel / Murata mit C6 | – | – | – | kein C6-Modul gefunden (unsicher) | – |
| ESP32-C6FH8 (Chip, QFN-32 5 × 5) (C41459370) | Chip 5 × 5 | 8 MB im Gehäuse | **eigene** | JLC 0 Stk. (geprüft); C6FH4 C6908287: 258 Stk., 3,57 USD | siehe unten |

**Chip-Design (C6FH8):** Dazu gehören ein 40-MHz-Quarz, ca. 15 Passive, ein π-Anpassnetz, eine 50-Ω-Leitung auf
0,8 mm FR4 und eine Chip- oder Inverted-F-Antenne mit ca. 13 × 5 mm Freifläche. Der Flächengewinn gegenüber dem
Modul liegt bei grob 60–80 mm² (unsicher). Dagegen stehen die HF-Abstimmung mit VNA und eine **eigene
RED/CE-Funkprüfung** statt der Modulzulassung (mehrere k€, unsicher). Für ein verschenktes Kleinserien-Spielzeug
**nicht sinnvoll**.

**Fazit:** **ESP32-C6-MINI-1-H8** einplanen. Gibt es zum Bestellzeitpunkt bei JLC kein H8, wird ohne
Layoutänderung das **N4** bestückt.

**Folgen von nur 4 MB** (MicroPython v1.29, App C6 = 1,81 MiB, geprüft in 3b.4):

| Partitionierung | App | Dateisystem | Folge |
|---|---|---|---|
| Standard 4 MB (ohne OTA) | ca. 1,9 MiB | ca. 2 MiB | Update = Datei-Update (Python/Web-UI per WLAN), Firmware-Update nur per USB |
| eigene OTA-Tabelle 2 × 1,875 MiB | je 1,875 MiB | **ca. 190 KB** | knapp: Web-UI gzip ca. 50–150 KB plus Modi-JSON (unsicher). Frozen modules vergrößern die App → passt bald nicht mehr |
| **8 MB (H8)**, eigener Build | 2 × 3 MiB | ca. 1,9 MiB | echtes OTA, Platz für Web-UI und Modi, auch für eine spätere C-Firmware mit Zigbee |

---

## 2. Layout-Folgen des Wechsels

### 2.1 Footprint C3-MINI-1 gegen C6-MINI-1 (geprüft, Pad-Koordinaten verglichen)

| Merkmal | C3 (`lcsc:WIFIM-SMD_ESP32-C3-MINI-1`) | C6 (KiCad `RF_Module:ESP32-C6-MINI-1`) |
|---|---|---|
| Pads | 53 (+ Pad 49 aus 9 Teilflächen) | 53 (gleich) |
| Raster / Padgröße | 0,8 mm, 0,8 × 0,4 | gleich |
| Pad-Positionen | – | **identisch**, Pad 49 um max. 5 µm verschoben |
| GND-Pads | 1, 2, 11, 14, 36–53 | gleich |
| 3V3 / EN | 3 / 8 | gleich |
| NC | 4, 7, 9, 10, 15, 17, 24, 25, 28, 29, 32–35 | **4, 7, 21, 32–35** |
| Courtyard | 13,2 × 16,6 | **13,5 × 16,9 plus Sperrzone 43,2 × 20,4** → unbrauchbar für `antenna_keepout()` |
| 3D-Modell | `lcsc.3dshapes/…C3-MINI-1.wrl` | in KiCad 9 **nicht installiert** (`ESP32-C6-MINI-1.step` fehlt) |
| Antennenlage | Ende −y (Footprint) → Platine −x | gleich |

→ **Eigenen Footprint anlegen:** `lcsc:WIFIM-SMD_ESP32-C6-MINI-1`, entweder per `just parts` (easyeda2kicad, C5736265)
oder als Kopie der C3-Datei mit neuer LCSC-Eigenschaft und neuem 3D-Pfad. Das Modulgehäuse ist gleich groß, das
C3-3D-Modell taugt notfalls für den Kollisionscheck.

### 2.2 Lage der Pads auf der Platine

Modul bei x = −8,8, Drehung 90°, Antenne bei −x (aus `louie-main.kicad_pcb` gelesen, geprüft):

| Modulseite | Pads (Reihenfolge) | Lage | Nachbarn |
|---|---|---|---|
| **rechts** (x = −3,9), y +4,8 → −4,8 | 12 IO0, 13 IO1, 14 GND, 15 IO6, 16 IO7, **17 IO12**, **18 IO13**, 19 IO14, 20 IO15, 21 NC, 22 IO8, 23 IO9, 24 IO18 | zum Treiber und zu USB-C | 0402-Reihe x = −1,9 |
| **Kante +y** (y = +5,9), x −12,8 → −4,8 | 1/2 GND, 3 3V3, 4 NC, 5 IO2, 6 IO3, 7 NC, 8 EN, 9 IO4, 10 IO5, 11 GND | Shunt/ISEN-Seite, J2 unten | R5 (SENSE) |
| **Kante −y** (y = −5,9), x −4,8 → −12,8 | 25 IO19, 26 IO20, 27 IO21, 28 IO22, 29 IO23, 30 RXD/IO17, 31 TXD/IO16, 32–35 NC | VSYS-Band, C1/C2, LDO | J3 unten |

**Alle ADC-Pins (IO0–IO6) liegen in der +y-Hälfte.** USB (IO12/13) liegt mittig rechts und zeigt damit direkt zur
USB-C-Buchse (Variante E: x ≈ 10,5–20,1, Pads bei y ≈ −1,6). Dafür muss **ein Kanal bei y ≈ −0,5 … +1,2 frei
bleiben**. Mit dem DRV8833 (x 2,3–6,9, y −3,9…+1,9) wäre die Mitte zu; mit dem DRV8213 (Kapitel 3) geht es.

### 2.3 Finale Pinbelegung

| GPIO (Pad) | Netz | Funktion | Begründung |
|---|---|---|---|
| IO0 (12) | VBAT_ADC | Teiler 470k/470k | ADC1_CH0; C6 misst bis 3,3 V → 5,5 V ergibt 2,75 V, **R7 bleibt 470 k** (die Änderung auf 330 k aus Variante E entfällt) |
| IO1 (13) | ISEN_ADC | IPROPI über RC | ADC1_CH1, +y-Seite wie der Treiber-Abgriff |
| IO2 (5) | INT | INT-Pad J2 (Sensor-INT1 oder Erschütterungsschalter) | LP-GPIO → Deep-Sleep-Wecken, kein Strapping |
| IO3 (6) | SENSE | Hebel, Deep-Sleep-Wecken | LP-GPIO, bleibt |
| IO4 (9) | VBUS_DET | VBUS-Teiler (neu) | ADC1_CH4 + LP-Wecken beim Einstecken; Strapping nur SDIO-Flanke |
| IO5 (10) | – | Reserve (Pad J3) | ADC/Wecken: zweiter Taster |
| IO6 (15) | SDA | I²C (J2) | LP-I²C (nur für eine spätere C-Firmware nutzbar) |
| IO7 (16) | SCL | I²C (J2) | LP-I²C |
| IO8 (22) | – | Strapping, **10 k Pull-up** | muss beim Download 1 sein |
| IO9 (23) | BOOT | J3, Taster gegen GND | interner Pull-up |
| IO12 (17) | USB_D− | J4 A7/B7 über ESD U5 (Pin 3 → 4) | fest im Chip |
| IO13 (18) | USB_D+ | J4 A6/B6 über ESD U5 (Pin 1 → 6) | fest im Chip |
| IO14 (19) | LED | Status-LED über 1 k | unterhalb des USB-Kanals |
| IO15 (20) | – | Reserve, NC | Strapping JTAG-Quelle, ohne eFuse wirkungslos |
| IO18 (24) | MOT_IN1 | DRV8213 IN1 (LEDC-PWM) | Modulecke unten rechts, nahe Treiber und VSYS-Band |
| IO19 (25) | MOT_IN2 | DRV8213 IN2 (LEDC-PWM) | dito |
| IO20 / IO21 (26/27) | – | Reserve (nur bei DRV8833-Rückfall: nSLEEP / nFAULT) | |
| IO22 / IO23 (28/29) | – | Reserve (Lastpuls Powerbank, WS2812) | |
| IO17 RXD (30) | – | Reserve | |
| IO16 TXD (31) | TXD | J3, Konsole | ROM-Log |

**Frei: 8 GPIOs** (IO5, IO8, IO15, IO17, IO20–23), davon IO5 mit ADC und Wecken.

### 2.4 Strapping, USB, Reset

- **IO8:** 10 k nach 3V3 (bisher R11, bleibt). **IO9:** interner Pull-up reicht, Pad J3 bleibt. **IO15:** offen lassen.
  **IO4/IO5:** Pegel beim Booten egal (SDIO-Timing). **IO2** ist beim C6 kein Strapping-Pin mehr, R10 wird zum
  SCL-Pull-up (geprüft, 3b.1).
- **USB:** IO12 = D−, IO13 = D+. ESD (U5) direkt an J4 und **durchgeschleift** (Kapitel 10): J4 → U5 Pin 1/3 →
  unter dem Gehäuse → Pin 6/4 → Modul. D+/D− kreuzen an J4 (Reihenfolge B7 A6 A7 B6). Kein Stich zu J1:
  **Flashen nur über J4** (Entscheidung des Auftraggebers, Kapitel 8).
- **EN:** R2 10 k / C12 1 µF bleiben. Download geht beim C6 per USB-Serial-JTAG automatisch; BOOT bleibt als
  Notweg auf dem Pad.

### 2.5 Wecken über SENSE: Pegel umdrehen

Heute gilt: R3 100 k von 3V3 an OUT_A, R4 10 k von OUT_B an GND, „Hebel zu“ = 0,3 V. Dafür bräuchte man
`WAKEUP_ALL_LOW`, und genau dieser Weg ist auf dem C6 in MicroPython fehlerhaft (#17334, offen, geprüft in 3b.6).

**Vorschlag (0 Bauteile mehr): R3 100 k OUT_A → GND, R4 10 k OUT_B → 3V3.**

| Zustand | SENSE | Wecken |
|---|---|---|
| Hebel offen | 0 V (über 100 k) | – |
| Hebel zu | 3,3 V × 100/110 ≈ **3,0 V** | `WAKEUP_ANY_HIGH` an IO3 |
| Motor läuft | nicht aussagekräftig, Strom per IPROPI | – |

Der Ruhestrom bei geschlossenem Hebel bleibt mit 30 µA gleich. OUT_B speist bei VM = 5,5 V ca. 0,2 mA in die
3V3-Schiene zurück; die Last nimmt das auf (unkritisch). **Sonderfall:** Bleibt der Hebel beim Einschlafen zu, muss
die Firmware auf LOW wecken oder per Timer prüfen (z. B. alle 5 s). Diesen Fall am XIAO-C6 testen.

### 2.6 Antenne (L2)

`antenna_keepout()`: zusätzliche Regelfläche über dem Randstreifen `y1 … +W/2` von x0 bis x1, **auf allen Lagen**,
mit Verbot für Kupferfläche und Vias, **Leiterbahnen erlaubt**. Damit verschwindet der GND-Streifen oben unter der
Antenne, und die OUT_A-Bahn unten bleibt möglich (analyse-funk-controller.md 2.3).

---

## 3. Motoransteuerung

### 3.1 Optionen

| | DRV8833 parallel (heute) | **DRV8213DSG** | DRV8212 / DRV8837 |
|---|---|---|---|
| VM | 2,7–10,8 V | **1,65–11 V** (geprüft) | 1,65–11 V / 0–11 V |
| Rds(on) HS+LS | ca. 180 mΩ parallel (unsicher) | 240 mΩ typ. (GAINSEL = Low) (geprüft) | 280 mΩ |
| Strom | 3 A RMS / 4 A Spitze parallel | 4 A Spitze, OCP ca. 4 A, RθJA 65,9 K/W (geprüft) | 4 A / 1,8 A |
| Strommessung | Shunt 0,1 Ω + RC → ADC | **IPROPI** 205 µA/A, ±6 % ab 350 mA (geprüft) | keine → Shunt nötig |
| Strombegrenzung | über Shunt (ca. 2 A) | **ITRIP = 0,51 V / (R_IPROPI × 205 µA/A)**, R = 1,24 k → 2 A (geprüft) | keine |
| Sleep | nSLEEP-Pin nötig (aktiv ca. 1,7 mA, unsicher) | **Autosleep** nach 1 ms bei IN1 = IN2 = 0, < 60 nA (geprüft) | DRV8837: nSLEEP-Pin |
| Fehler | nFAULT | Auto-Retry (OCP, TSD), kein Pin (DSG) | – |
| Bremsen / rückwärts | ja | ja: 1/1 = Bremse, 0/0 = Coast (Hi-Z) (geprüft) | ja |
| Gehäuse / Courtyard | HTSSOP-16, ca. 38 mm² | **WSON-8 2 × 2, ca. 7 mm²** | SOT-563 / WSON-8 |
| Bauteile im Block | U2, R1, C4–C7, R8, C14 = **8** | U2, R_IPROPI, C4, R8, C14 = **5** | wie DRV8833 |
| GPIOs | 4 (IN1, IN2, nSLEEP, nFAULT) | **2** | 2–3 |
| Preis 10 Stk. (JLC) | 1,40 USD (C50506) | **0,93 USD** (C22407186, 3.749 Stk., Extended) | 0,65 / 0,19 |

### 3.2 Bewertung

- **DRV8213 erfüllt alles:** Er läuft ab 3,0 V Akku bis 5,5 V USB, bremst, fährt rückwärts und ist in Coast/Autosleep
  hochohmig (für die Hebel-Erkennung nötig; dass im Sleep kein Ausgangs-Pull-down wirkt, ist unsicher → am
  Prototyp prüfen). Die Strombegrenzung bleibt bei 2 A wie heute.
- **Blockier-Erkennung:** IPROPI misst beim Fahren **und** in der Bremsphase. Daher PWM als **Fahren/Bremsen**:
  vorwärts IN1 = 1, IN2 = PWM mit Tastgrad (1 − d). Das ergibt 255 mV/A am ADC (bisher 100 mV/A). Die
  Hardware-Stall-Erkennung gibt es nur im RTE-Gehäuse; die Firmware wertet daher Strom > Schwelle über eine
  Zeit x aus, wie bisher geplant.
- **Wärme:** 1 A → 0,24 W → +16 K; 2 A Dauer (blockiert) → ca. 1 W → +63 K (geprüft, Rechnung mit RθJA). Die
  Firmware muss eine Blockade nach ≤ 0,5 s abschalten. Thermal-Vias (2 × 0,3 mm) ins EP setzen.
- **MicroPython:** `machine.PWM` (LEDC) mit 20 kHz und ca. 11 Bit Auflösung reicht. MCPWM wird nicht gebraucht.
  Zwei parallele Kanäle mit getrennten GPIOs (Querstromgefahr) entfallen.
- **Eingänge:** IN1/IN2 haben 200-k-Pull-downs → Motor aus im Reset. Der von Variante E geforderte nSLEEP-Pull-down
  entfällt.
- **DRV8833 als Rückfall:** Falls der Prototyp mit DRV8213 thermisch oder wegen der Hebel-Erkennung scheitert.
  Dann nSLEEP an IO20 mit 100 k Pull-down (nicht fest verdrahten: aktiv ca. 1,7 mA zerstören den Schlafstrom);
  nFAULT an IO21 ist verzichtbar.
- Ein **Breakout** für den Steckbrett-Test ist nötig (DRV8213EVM, unsicher, ob einzeln lieferbar). Sonst den
  DRV8213 auf einen WSON-Adapter löten.

**Empfehlung: DRV8213DSGR (C22407186), GAINSEL an GND, R_IPROPI 1,24 k (1 %) an GND, danach R8 1 k / C14 100 nF
zum ADC.** Den Kondensator nicht direkt an IPROPI legen, er würde die Stromregelung verzögern.

---

## 4. Zigbee vorbereiten

| Frage | Befund | Status |
|---|---|---|
| Extra Hardware? | **Nein.** 802.15.4 nutzt dasselbe Funkteil und denselben HF-Pfad, also auch die Modulantenne | (geprüft) [C6-Koexistenz] |
| Zigbee + Wi-Fi SoftAP | Router/**Coordinator: X** (nicht unterstützt), End Device: C1 | (geprüft) |
| Zigbee + Wi-Fi STA | Router/Coordinator: C1, End Device: Y | (geprüft) |
| Zigbee + BLE-Scan | Router/Coordinator: **X**, End Device: C1 | (geprüft) |
| Espressif-Empfehlung Gateway | Zwei Chips mit getrennten Antennen (z. B. S3 + H2) | (geprüft) |
| Rollen | IKEA-/Aqara-Taster sind End Devices und brauchen ein Netz mit **Coordinator** (Trust Center). Ist Louie selbst End Device, kann er nur einem bestehenden Netz (ZHA/Zigbee2MQTT) beitreten, die Taster werden dort an ihn gebunden | (unsicher, Ablauf) |
| Stack | `esp-zigbee-sdk`, vorkompilierte Bibliotheken, ESP-IDF 5.5.x, nur C | (geprüft) |
| Flash/RAM | Grob +0,5–0,8 MB App, 50–100 KB RAM für einen kleinen Coordinator. Für OTA wird 8 MB empfohlen | (unsicher) |
| MicroPython | 802.15.4 im C6-Build deaktiviert, kein Modul. Ein eigenes C-Modul mit `esp-zigbee-lib` als eigener Task wäre theoretisch möglich, ist aber unveröffentlicht, RAM-intensiv und Wochenarbeit | (geprüft / unsicher) |
| Thread/Matter | gleiche Koexistenz-Grenzen (Thread-Router + SoftAP = X). Matter über WLAN braucht kein 802.15.4 | (geprüft / unsicher) |

**Ehrliche Einschätzung:** Mit eigenem Hotspot (Partymodus, 8 Handys) ist ein Zigbee-Coordinator **ausgeschlossen**,
und neben den BLE-BTHome-Tastern ebenfalls. Praktikabel wäre nur „Louie im Heim-WLAN (STA) + Zigbee“. Dort ist es
aber einfacher, die Taster über Home Assistant per WLAN anzubinden. **Jetzt vorsehen:** C6 (erledigt), **8-MB-Flash
(H8)**, die Antennenkorrektur L2 und ein guter Einbauort. Mehr Hardware gibt es nicht. Zigbee bleibt eine Option
für eine spätere C-Firmware und ist **kein Grund für weitere Bauteile**.

---

## 5. Priorität Platine A, optionale Platine B

Vorgabe: **A funktioniert vollständig allein** (zweites Fach = Kupferbrücke). USB-C und C6 haben Vorrang vor dem
Beschleunigungssensor.

### 5.1 Inhalt von A

| Baugruppe | Status | Vereinfachung |
|---|---|---|
| ESP32-C6-MINI-1 + C9, C10, R2, C12 | **Muss** | – |
| Motortreiber | **Muss** | DRV8213 statt DRV8833 + Shunt |
| LDO AP2112K + C8, C11 | **Muss** | optional RT9080 (C841192, ca. 2 µA Ruhestrom, Pinbelegung vor Tausch prüfen, unsicher) |
| SENSE (R3, R4, R5) | **Muss** | Pegel umdrehen (2.5) |
| VBAT-Teiler (R6, R7, C13) | **Muss** (Unterspannung, Duty = U_soll/U_akku) | – |
| Strommessung | **Muss** (Blockade) | IPROPI statt Shunt |
| USB-C J4, ESD U5, CC R12/R13, D2, Q1, R14 | **Muss** | ESD als UMW-Zweitquelle; VBUS_DET nutzt R14 als Teiler-Oberteil (+1 R) |
| Puffer C1, C2 (47 µF) | **Muss** | C3 entfällt (Variante E) |
| Status-LED D1/R9 | sinnvoll (Diagnose ohne Handy), 2 Teile | verzichtbar, wenn Platz fehlt |
| BOOT/EN/TXD | **nur Pads** (J3, unten) | kein Taster oben |
| I²C-Pull-ups R10/R11 | auf A (Breakouts ohne Pull-ups, IO8-Strapping) | – |
| **LIS2DH12 + C15** | **runter von A** | → Pads J2 |

### 5.2 Schnittstelle A ↔ B / Breakout (Unterseite A)

| Pad | Netz | Zweck |
|---|---|---|
| J2-1…5 | 3V3, GND, SDA (IO6), SCL (IO7), INT (IO2) | Sensor-Breakout, Erschütterungsschalter (INT ↔ GND, interner Pull-up) oder Platine B |
| J3-1…5 | EN, TXD, BOOT, GND, **IO5** (neu, falls Platz) | Service, zweiter Taster |
| J1-1…4 | BAT_IN, –, –, GND | Ladeplatine („B-Lade“): nur BAT_IN und GND; Pads 2/3 ohne Netz (Flashen nur über J4) |
| J5 +/− | BAT_IN, GND | geschützte Zelle direkt |

**Ohne B:** Die Pull-ups auf A halten den Bus definiert. Die Firmware macht beim Start einen I²C-Scan (0x18/0x19)
und schaltet „Wackeln“-Funktionen ab, wenn kein Sensor antwortet. INT bekommt per Software einen Pull-down
(bzw. Pull-up bei einem Schalter gegen GND). Das ist ohne Wirkung, wenn nichts angeschlossen ist.

### 5.3 Platine B im zweiten Fach

- **Machbar:** B übernimmt wie die heutige Ladeplatine die Brücke. Die Brückenbahn liegt **im Motorstromkreis**
  (PWM-Potenzial) und muss auf B **galvanisch getrennt** von GND/3V3 der B-Elektronik bleiben. Das Kabel zu A
  (5 Adern für den Sensor, mit Ladeschaltung 6: BAT_IN, GND, 3V3, SDA, SCL, INT) läuft wie heute über die Trennwand.
  I²C über ca. 10–15 cm bei 100 kHz ist unkritisch (unsicher).
- **Alter Louie (1 × C):** B liegt in der C-Hülse über A (hardware-konzept.md 6: 2 Platinen mit ca. 10 mm Abstand
  passen). Die Brücke bleibt ungenutzt.
- **Lohnt eine eigene B?** Für den Sensor allein **nein**: Ein fertiges Breakout (LIS3DH/LIS2DH12/MPU6050, ca.
  1–5 €, oft ca. 16–20 mm breit, unsicher) passt in die Basis oder die C-Hülse, im AA-Fach eher nicht. Noch
  einfacher ist ein **Federschalter** (z. B. SW-18010P) zwischen INT und GND: Er weckt beim Rütteln, ganz ohne I²C.
  **Eine B lohnt sich erst als „B-Lade + Sensor“**, also als Weiterentwicklung der heutigen Ladeplatine v0.2.

### 5.4 Platzgewinn auf A (Courtyard, Oberseite, grob)

| Maßnahme | gewonnen |
|---|---|
| LIS2DH12 (LGA-12, ca. 2,6 × 2,6) + C15 (0402) | **ca. 8–9 mm²** + zwei I²C-Bahnen und INT bis ans rechte Ende |
| Elko C3 (1206) | ca. 9 mm² (in Variante E schon eingerechnet) |
| **DRV8833 → DRV8213** (HTSSOP-16 → WSON-8) | **ca. 31 mm²** |
| Shunt R1 (0805) + C5, C6, C7 (0402) | ca. 8 mm² |
| Vorrouting IN1/IN2-Brücke und ISEN-Balken | Routing-Kanäle, nicht bezifferbar |
| neu: R15 (VBUS-Teiler), R16 (SDA-Pull-up) | −3 mm² |

Variante E fehlten nach dem Streichen von C3 **ca. 16 mm²** (75 mm² Bedarf auf 59 mm² Band). **Der Sensor allein
hilft kaum (ca. 9 mm²).** Er räumt aber genau die rechte Ecke neben J4, wo R4 und die ESD hin müssen. **Am meisten
bringt der DRV8213 (ca. 39 mm²).** Beides zusammen ergibt ca. +45 mm² Reserve; damit wird Variante E von „knapp,
unsicher“ zu „sollte passen“. Die Probeplatzierung (U1 in idee-usb-c-hauptplatine.md 8) bleibt Pflicht.

### 5.5 Empfehlung

**A** = C6 + DRV8213 + LDO + SENSE + VBAT + IPROPI + USB-C-Stufe + LED, alles Übrige als Pads. **Zuerst nur A
fertigen**, im zweiten Fach die Kupferbrücke. Sensor zunächst als Breakout oder Federschalter an J2. Die
**Ladeplatine v0.1** bleibt an J1 nutzbar (BAT_IN). Eine B-Platine erst später, und dann nur als v0.2 „Lade +
Sensor“.

---

## 6. Änderungsliste für den Umbau-Agenten (ein Paket: C6 + Variante E + L2 + A-Priorität)

### 6.1 Schaltplan (`gen_main_schematic.py`, `gen_symbols.py`)

| # | Änderung |
|---|---|
| S1 | U1: `lib` → neues Symbol `louie:ESP32-C6-MINI-1` (in `gen_symbols.py` analog zu C3, Pins wie KiCad `RF_Module:ESP32-C6-MINI-1`, geprüft) **oder** `RF_Module` in `LIBS` aufnehmen. Value `ESP32-C6-MINI-1-H8`, LCSC `C42403058` (Rückfall C5736265), fp `lcsc:WIFIM-SMD_ESP32-C6-MINI-1` |
| S2 | U1-Pins: `3:+3V3, 8:EN, 1:GND, 12:VBAT_ADC, 13:ISEN_ADC, 5:INT, 6:SENSE, 9:VBUS_DET, 15:SDA, 16:SCL, 22:IO8, 23:BOOT, 17:USB_D-, 18:USB_D+, 19:LED, 24:MOT_IN1, 25:MOT_IN2, 31:TXD, 10:IO5`; Rest NC |
| S3 | U2 → `louie:DRV8213DSG` (neu in `gen_symbols.py`: 1 VM, 2 OUT1, 3 OUT2, 4 GND, 5 IN2, 6 IN1, 7 GAINSEL, 8 IPROPI, 9 EP=GND), LCSC C22407186, fp `Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm`. Netze: VM=VSYS, OUT1=OUT_A, OUT2=OUT_B, IN1=MOT_IN1, IN2=MOT_IN2, GAINSEL=GND, IPROPI=ISEN |
| S4 | **Entfernen:** R1 (Shunt), C3, C5, C6, C7, U4 (LIS2DH12), C15, Netze VCP, VINT, DRV_nSLEEP, DRV_nFAULT, RXD |
| S5 | **Neu R1:** 1,24 k 1 % 0402, ISEN → GND (R_IPROPI). R8/C14 bleiben (ISEN → ISEN_ADC) |
| S6 | R3: 100 k **OUT_A → GND**; R4: 10 k **OUT_B → +3V3** (Pegel umdrehen) |
| S7 | R10: 10 k +3V3 → SCL; **R16 neu:** 10 k +3V3 → SDA; R11: 10 k +3V3 → IO8 (bleibt) |
| S8 | J2: `1:+3V3, 2:GND, 3:SDA, 4:SCL, 5:INT`; J3 auf 1×05: `EN, TXD, BOOT, GND, IO5` |
| S9 | Variante E (idee-usb-c-hauptplatine.md 7): J4 TYPE-C-31-M-12 (C165948), R12/R13 5,1 k, U5 USBLC6-2SC6 (C7519 bzw. C2687116), D2 SS34F (C60396, SMAF, VBUS_J4 → VSYS), Q1 AO3401A (C15127; S = VSYS, D = BAT_IN, G = VBUS_J4), J1-1 → BAT_IN, J5 (BAT_IN/GND) |
| S10 | R14 100 k VBUS_J4 → **VBUS_DET**, **R15 neu** 100 k VBUS_DET → GND (Teiler 5 V → 2,5 V, entlädt VBUS weiter) |
| S11 | R7 **bleibt 470 k** |
| S12 | Blocktitel „ESP32-C3“ → „ESP32-C6“, „Beschleunigungssensor“ → „Erweiterungs-Pads“ |

### 6.2 Layout (`placement_einseitig.py`, `gen_main_pcb.py`)

| # | Änderung |
|---|---|
| L1 | U1 bleibt bei (−8,8; 0; 90°). Footprint mit 13,2 × 16,6-Courtyard verwenden (2.1), sonst rechnet `antenna_keepout()` falsch |
| L2 | `antenna_keepout()`: Regelfläche Randstreifen (2.6) |
| L3 | **USB-Kanal** y ≈ −0,5 … +1,2 von x = −3,9 bis J4 freihalten; D1/R9 unter den Kanal (y ≈ −1…−2), R11/R10/R16 an IO8/IO7/IO6 |
| L4 | U2 (DRV8213) nahe Modulecke unten rechts (IO18/19) und am VSYS-Band, R1/R8/C14 Richtung +y zu IO1. Ausrichtung in der Probeplatzierung festlegen |
| L5 | `thermal_vias()`: für EP Pad 9 (0,9 × 1,6) 2 Vias, Abfrage `GetNumber()=="9"` |
| L6 | `preroute_driver()` **streichen** (keine Parallel-Eingänge mehr). `preroute_outputs()` neu: OUT1/OUT2 (Pins 2/3) je 0,4 mm + Via → unten zu BT1 (Randstreifen +y wie bisher) und BT2; ISEN-Balken entfällt. Die `assert` auf 90° anpassen |
| L7 | `preroute_supply()`: Schiene beginnt an Q1-Source/D2-Kathode statt J1-Via; Abzweige zu C3 und C7 entfallen; VM = DRV8213 Pin 1 direkt an C4 und Schiene |
| L8 | `ground_via_at_pad`: R1-Shunt- und C15-Vias streichen, für U2 Pin 4 GND-Via setzen |
| L9 | Variante-E-Platzierung (J4 bei x ≈ 15,3, Öffnung y = 6,05; ESD, Q1, D2 im Band y < −1,6; J1 unten an −y; J5 unten bei x ≈ 1–8) |
| L10 | Netzklassen: `/BAT_IN`, `/VBUS_J4` → Power; `/OUT_A`, `/OUT_B`, `/VSYS` wie bisher; `/ISEN` → Default (nur noch µA) |
| L11 | J2/J3 unter dem Modul, Pads nicht auf die GND-Vias von Pad 49 legen |
| L12 | `board_outline.py`: nur Kommentar (C6) |

### 6.3 BOM (`teile.csv`)

| Zeile | neu |
|---|---|
| U1 | ESP32-C6-MINI-1-H8, C42403058; Alternative ESP32-C6-MINI-1-N4 C5736265 (pinkompatibel) |
| U2 | DRV8213DSGR, C22407186, WSON-8 2 × 2; Alternative DRV8833PWPR C50506 (anderes Layout) |
| R1 | 1,24 k 1 % 0402 (IPROPI), ersetzt den Shunt |
| C1–C3 → C1–C2; C4–C5 → C4; C6, C7, U4, C15 | streichen |
| R16 | 10 k SDA-Pull-up; R15 100 k VBUS_DET |
| J4, R12, R13, U5, D2, Q1, R14, J5 | aus Variante E (LCSC siehe S9) |
| J2, J3 | Funktion neu (Sensor-/Service-Pads) |

### 6.4 Prüfen vor der Bestellung

1. Am XIAO-C6: Wecken mit `WAKEUP_ANY_HIGH` an IO3 bei umgedrehtem Pegel; Hotspot + BLE-Scan (beide Heaps).
2. DRV8213 am Louie-Motor: Strom, Erwärmung bei Blockade, Hebel-Erkennung im Autosleep (Ausgänge Hi-Z).
3. H8 bei JLC beschaffbar (Global Sourcing/beigestellt), sonst N4.
4. Probeplatzierung Variante E mit diesem Stand.

---

## 7. Kostenänderung pro Board (10 Stück, LCSC/JLC 2026-11-02)

| Posten | alt | neu | Δ USD |
|---|---|---|---|
| U1 | C3-N4 2,70 | C6-N4 3,60 / **H8 ca. 5,4** (Mouser 4,70 €, unsicher) | **+0,90 / +2,7** |
| U2 | DRV8833 1,40 | DRV8213 0,93 | **−0,47** |
| Shunt, C3, C5–C7, LIS2DH12 + C15 | ca. 0,05 + LIS ca. 0,3 (unsicher) | – | ca. −0,35 |
| R_IPROPI, R15, R16 | – | 3 × 0402 | +0,01 |
| USB-C-Stufe (J4 0,19, U5 0,05, D2 0,04, Q1 0,08, 3 R) | – | | +0,37 |
| **Summe Bauteile** | | | **ca. +0,45 (N4) / +2,3 (H8)** |
| Extended-Typen | C3, DRV8833, LIS2DH12 | C6, DRV8213, J4, D2, U5 | +2 Typen × 3,07 = +6,1 USD/Auftrag → +0,61/Board |
| **Gesamt bei 10 Stück** | | | **ca. +1,1 USD (N4) / +2,9 USD (H8)** |

Ohne die USB-C-Stufe (nur C6 + DRV8213 + Sensor auf Pads) wäre es ca. **±0 USD (N4)**. Röntgen bleibt für das Modul
gleich; der DRV8213 hat wie der DRV8833 ein Exposed Pad.

---

## 8. Ergebnis Umbau (Probeplatzierung und Routing, 2026-11-02)

Alles wird aus den Skripten erzeugt (`just symbols schematic pcb route`), nichts ist im GUI nachgearbeitet.

### 8.1 Prüfergebnisse (Stand nach Überarbeitung 2026-11-02, Regeln aus Kapitel 9)

| Prüfung | Ergebnis |
|---|---|
| ERC (`just erc`) | **0 Fehler, 0 Warnungen** |
| DRC (`just drc`) | **0 Verstöße**, Schaltplan-Parität 0 Abweichungen, **13 offene Verbindungen** (vorher 17) |
| Regeln | Abstand 0,13 mm, Mindestbahn 0,13 mm (vorher 0,1), Standardbahn 0,15 mm, Via 0,3/0,6 mm, Loch–Kupfer 0,28 mm, Rand 0,3 mm; keine Bahn unter 0,13 mm |
| Routing | ca. 90 % der Pad-Verbindungen; offen: 11 Signal-Teilstücke + 2 GND-Flächeninseln |
| Platzierung | 42 Bauteile ohne Courtyard-Überlappung, oben 475 mm², unten 111 mm² |
| Antenne | Sperrflächen unverändert (`antenna_keepout()`), keine Fläche/Vias im Antennenbereich (DRC 0) |
| 3D/Hüllkurve | größter Radius weiterhin **6,93 mm** (J4) < 7,25 mm, keine Bauteile unter den Endkappen (8.4) |

**Ziel 100 % auf 2 Lagen ist nicht erreicht.** Offene Verbindungen des besten Laufs (12 Freerouting-Varianten,
die Ergebnisse streuen von Lauf zu Lauf zwischen 12 und 25):

| Netz | offen | Lage des Problems |
|---|---|---|
| SCL (2), SDA, INT (2) | 5 | Bus vom Modul/J2 (unten, Kante +y) zum Sensor U4 in der Ecke rechts oben; INT zusätzlich zu Modulpad 5 (Kante +y unter dem Modul) |
| +3V3 | 2 | R2 ↔ J2-1; Sensorgruppe U4/R4/C15 rechts ↔ übriges 3V3-Netz |
| EN | 2 | Modulpad 8 und J3-1 zu R2/C12 |
| VBUS_DET | 1 | R14 (Band vor der ESD) ↔ Modulpad 9 (Kante +y) |
| VBAT_ADC, ISEN_ADC | 2 | R6/R8 (zweite 0402-Reihe, −y) ↔ C13/C14/Modulpads 12/13 (+y) |
| GND | 2 | zwei Inseln der oberen Fläche ohne Via-Platz |

**Warum es nicht aufgeht (Engstellen):**

1. **Nord-Süd-Querungen in der Mitte.** Zwischen Modul und J4 ist die Oberseite in Querrichtung zu (DRV8213/C1/C2/
   D2 an −y, LDO/C8–C10/Q1 an +y, dazwischen nur ein Kanal y ≈ 0,8…1,7 für 3 Bahnen, den das USB-Paar belegt).
   Alles, was von −y nach +y muss (VBAT_ADC, ISEN_ADC, SENSE, VBUS zum Gate, VBUS_DET, VSYS), geht über die
   Unterseite und zerschneidet dort die GND-Fläche.
2. **Lange Ost-West-Leitungen zum rechten Ende** (SDA, SCL, INT, 3V3 zum Sensor; vorher auch VBUS_DET) müssen
   genau diese Nord-Süd-Leitungen kreuzen und unter J4 durch zwei Engstellen zwischen den Lötlaschen (je ca. 2,3 mm).
   Die Reihenfolge der Leitungen an U4 (LGA, Pins in der Ecke) passt nicht zur Reihenfolge, die links gebraucht wird;
   auf zwei Lagen ist jede Umsortierung ein weiteres Via-Paar in einem Bereich ohne Via-Platz.
3. **Unterseite ist zugleich Massefläche:** Jede weitere Leitung unten erzeugt GND-Inseln (2 bleiben offen).
4. Ein vollständig vorgerouteter Bus unter dem Buchsenkörper wurde probiert (INT/SCL/SDA am Rand +x nach +y, unter
   J4 nach −x, 3V3 durch die Laschenlücke): Freerouting fand die Anschlüsse an den Bus-Enden links nicht, und die
   obere GND-Fläche zerfiel weiter (16–17 offen). Er ist deshalb nicht übernommen.

Die offenen Leitungen ließen sich im GUI vermutlich bis auf wenige schließen, aber nur mit Bahnen über die
Unterseite, die die Massefläche weiter zerteilen; regelkonform und mit brauchbarer GND-Fläche ist das auf 2 Lagen
nicht absehbar. **Empfehlung:** 4-Lagen-Analyse (Innenlage GND durchgehend, eine Innenlage für Bus/Querungen).

### 8.2 Umgesetzt (Kapitel 6)

| # | Stand |
|---|---|
| S1 | Symbol `louie:ESP32-C6-MINI-1` (gen_symbols.py), Value ESP32-C6-MINI-1-H8, LCSC C42403058 |
| S2 | Pinbelegung wie 2.3 |
| S3 | Symbol `louie:DRV8213DSG`; GAINSEL und EP an GND |
| S4/S5 | Shunt, C3, C5–C7, VCP/VINT/nSLEEP/nFAULT/RXD entfernt; R1 = 1,24 k 1 % (R_IPROPI) |
| S6 | R3 OUT_A → GND, R4 OUT_B → 3V3 (SENSE HIGH bei geschlossenem Hebel) |
| S7/S8 | R10 SCL, R16 SDA, R11 IO8; J2 = 3V3/GND/SDA/SCL/INT, J3 = EN/TXD/BOOT/GND/IO5 |
| S9/S10 | J4, R12/R13, U5, D2 SS34F, Q1 AO3401A, R14/R15 (VBUS_DET), J5 |
| S11/S12 | R7 470 k; Blocktitel neu |
| L1 | U1 bei (−8,8; 0; 90°), Courtyard 13,2 × 16,6 |
| L2 | `antenna_keepout()`: Randstreifen mit Verbot für Fläche und Vias, Bahnen erlaubt; oben unter der Antenne liegt kein GND mehr |
| L3 | USB-Paar vorgeroutet und durch die ESD **durchgeschleift** (Kapitel 10): J4 → U5 Pin 1/3 → Pin 6/4 → Vias → unten im Bereich der Buchse bis vor C10 → oben im Kanal (D+ y = +0,83, D− y = +1,11, je 0,15 mm) zum Modul |
| L4/L5/L6 | DRV8213 an der Modulecke −y (180°), 2 Thermal-Vias, OUT_A/OUT_B per Via unten am Rand −y zu BT1/BT2 |
| L7 | VSYS-Hauptbahn 0,5 mm: D2-Kathode → C1 → C2, C1 → C4 → VM |
| L9 | J4 bei x = 15,3, Öffnung y = 6,05; U5, R12, R13 im Band davor; J1 und J5 unten unter J4 |
| L10 | Netzklasse Power: VSYS, BAT_IN; VBUS- und BAT_IN-Hauptwege vorgeroutet (0,5 mm); ISEN Standard |
| L12 | board_outline.py: Kommentar C6 |
| BOM | teile.csv neu (Haupt-Zeilen) |

### 8.3 Abweichungen vom Paket (mit Begründung)

| Punkt | Abweichung | Grund |
|---|---|---|
| Sensor | LIS2DH12 + C15 **bleiben oben**, bestückungsoptional; INT an IO2 | Entscheidung des Auftraggebers während des Umbaus |
| J2 | I²C-Pads unten an der Kante **+y unter LDO/Q1** (Mitte x = 3,4, y = 5,3) | unter ESD/Sensor liegen jetzt die Vias der ESD-Durchschleifung |
| J3 | 5 Pads, unter dem Modul bei y = −3,25 | Abstand zu den GND-Vias von Pad 49 |
| J1 | nur BAT_IN (1) und GND (4), Pads 2/3 ohne Netz | **Entscheidung des Auftraggebers: Flashen nur über J4.** Footprint bleibt 4-polig (Kabelbelegung der Ladeplatine v0.1, deren D+/D− nicht mehr angeschlossen werden, ladeplatine.md) |
| U5 | **korrigiert:** durchgeschleift (Pin 1→6, 3→4), 180° bei x = 16,6 | Datenblatt geprüft, Abzweig ist laut ST „unsuitable layout“ (Kapitel 10) |
| Antennen-Randstreifen | an der Kante **−y** statt +y | OUT_A läuft vom DRV8213 (Modulecke −y) ohne Kreuzung am Rand zu BT1. Elektrisch gleichwertig (unsicher, RSSI-Test beide Richtungen) |
| U2-Footprint | `Package_SON:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm` | padgleich zu Texas DSG0008A, hat aber ein 3D-Modell |
| J4-Footprint | `louie:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | KiCad-Footprint, erzeugt von fetch_parts.py mit dem 3D-Modell des LCSC-Teils und ohne Bestückungsdruck über der Kante (KiCad 9 hat kein Modell) |
| U1-Footprint | `lcsc:WIFIM-SMD_ESP32-C6-MINI-1` = Pads des C3-Footprints + 3D-Modell des C6 | der EasyEDA-Footprint des C6 liegt bis 20 µm neben dem Raster |
| D2-Footprint | EasyEDA-SMAF mit korrigiertem Courtyard | Original-Courtyard kleiner als die Pads |
| Designregeln | Abstand **0,13** mm, Standardbahn 0,15 mm, Mindestbahn **0,13** mm (zwischenzeitlich 0,1), Loch–Kupfer 0,28 mm | JLC-Standard 0,10/0,10 mm mit 30 % Reserve (Kapitel 9) |
| GND-Flächen | Pads voll angebunden statt Wärmefallen | kleine GND-Pads (0402, USB-C, LGA) bekamen nur eine Speiche (DRC starved_thermal) |
| R4, C15 | rechts neben J4 bei x = 21,2 (R4 bei y = −1,6, OUT_B per Via auf die OUT_B-Bahn unten; C15 bei +1,6) | x > 22,2 liegt unter der Endkappe der Hülle; rechtes Ende entlastet |
| R14, R15 | VBUS-Teiler im Band links der ESD (x = 11,2, y = −3,45 / −4,49), VBUS-Bahn dafür senkrecht und dann bei y = −5,5 zur Anode | vorher am rechten Ende; VBUS liegt im Band direkt an |
| R12, R13 | R12 (CC1) links neben J4 bei (9,42; −1,0), CC1 über die Körperseite der Buchse; R13 (CC2) bleibt rechts | das Band vor den Datenpads ist von der ESD-Durchschleifung belegt |
| VBUS-Abzweige | Gate Q1: Via über der Anode, unten nach Norden, Via zwischen C9 und Q1; die beiden VBUS-Padpaare unten über die Körperseite verbunden | Band frei für die ESD; Freerouting fand das Gate nicht |
| `just pcb` | Vorgabe-Variante im justfile jetzt `einseitig` (vorher `zweiseitig`) | `placement_zweiseitig.py` ist noch C3-Stand und nicht nachgezogen |

### 8.4 Mechanik: USB-C gegen AA-Hüllkurve (rechnerisch, aus dem STEP/STL-Export)

Auswertung aller Eckpunkte von `build/main-board/3d/louie-main.stl` (Platinenoberseite 0,5 mm über der Zellachse; nach der Überarbeitung erneut gerechnet, unverändert):

| Größe | Wert |
|---|---|
| J4 Vorderkante | y = +6,10 mm (Platinenkante 6,75) |
| J4 Oberkante | z = +3,75 mm über der Zellachse |
| größter Radius aller Bauteile | **6,93 mm** (J4, obere vordere Kante) bei AA-Radius 7,25 → **0,32 mm Luft** |
| Bauteile unter den Endkappen (x > 22,2) | keine |

`huelle.scad`: Kabelfenster auf **+y** (`kabel_seite = 1`, `kabel_x = 14,5`, `kabel_l = 9`) für J1 und J5 unter der
Buchse, Platinen-Dummy auf den C6-Stand, neue Ansicht `teil = "kollision"`. Die Schale liegt unter der Platine, die
Buchse oben ist frei zugänglich; ein eigenes Buchsenfenster ist nicht nötig. **Offen:** Durch das Kabelfenster fehlt
unter J4 der Randsteg (+y) als Auflage; Steckkräfte gehen in die Lötlaschen (idee-usb-c-hauptplatine.md 2.5).
Abhilfe: Fenster kürzer und tiefer oder Stützsteg zwischen J1 und J5 (am Druckteil testen).

### 8.5 Offene Punkte

1. Die 13 offenen Verbindungen (8.1) sind auf 2 Lagen regelkonform nicht geschlossen → **4-Lagen-Analyse**.
2. ~~USBLC6-2SC6: interne Verbindung bestätigen~~ erledigt, durchgeschleift (Kapitel 10).
3. Antennen-Randstreifen −y: im RSSI-Test (beide Einbaurichtungen) mitprüfen.
4. Hülle: Auflage unter J4 (8.4), Druckprobe.
5. `placement_zweiseitig.py` (Variante 2, Rückfall „Teile von Hand unten“) ist nicht auf den C6-Stand gebracht.
6. Prüfpunkte 6.4 (XIAO-C6, DRV8213 am Motor, H8-Beschaffung) unverändert offen.
7. Ladeplatine v0.2: D+/D−-Durchreichung entfällt (ladeplatine.md, Hinweis).

---

## 9. Fertigungsregeln (JLCPCB, 2 Lagen, 0,8 mm, 1 oz)

Quelle: [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), abgerufen 2026-11-02 (geprüft).

| Größe | JLCPCB-Fähigkeit (2 Lagen, 1 oz) | Projektregel (`gen_main_pcb.py`, `RULES`) | Reserve |
|---|---|---|---|
| Bahnbreite / Abstand | **0,10 / 0,10 mm** (4/4 mil), Standardpreis; 2 oz: 0,16/0,16 | Abstand **0,13**, Mindestbahn **0,13**, Standardbahn **0,15** mm | +30 % |
| Pad – Bahn | 0,10 mm (1 oz) | 0,13 mm (allgemeiner Abstand) | +30 % |
| Via Bohrung / Durchmesser | min. 0,15 / 0,25 mm. **Aufpreis** bei Bohrung 0,1 oder 0,15 mm (jeder Ø) und bei 0,2/0,25 mm mit Ø < 0,45 mm. 0,1/0,2 mm nur bis 1 mm Dicke mit ENIG/OSP | **0,3 / 0,6 mm** (Restring 0,15 mm) | kein Aufpreis |
| Restring PTH (Bauteillöcher) | empfohlen ≥ 0,25, absolut 0,18 mm | Laschen von J4: 1,0 × 1,6/2,1 mm bei Bohrung 0,6 mm → 0,2 mm | ≥ Minimum |
| Lochabstand Via – Via | 0,2 mm (Pad-Bohrungen 0,45 mm) | 0,25 mm (`hole_to_hole`) | +25 % |
| Bohrung (PTH) – Bahn | 0,28 mm, empfohlen 0,35 | **0,28 mm** (`hole_clearance`, gilt für alle Bohrungen) | = Minimum; Vias halten durch Restring + Abstand 0,28 mm ein |
| Kupfer – Fräskante | ≥ 0,2 mm (V-Cut 0,4) | **0,3 mm** (`edge`) plus Sperrstreifen „Rand“ 0,32 mm für Freerouting | +50 % |
| Leistungsbahnen | – | Power 0,4 mm, vorgeroutete Hauptwege 0,5 mm, Supply (3V3/GND) 0,25 mm | – |

**Herkunft der alten Regeln 0,15/0,2:** Sie standen seit der ersten Probeplatzierung (Commit 90fb77e) in
`gen_main_pcb.py` als „konservativ, damit praktisch jeder Hersteller sie im Standardpreis fertigt“
(Abstand 0,15, Standardbahn 0,2, Mindestbahn 0,12 mm, Via 0,3/0,6 mm). Gestützt waren sie auf
offene-punkte.md A9/A15 und kostenabschaetzung.md („0,15 mm / Via 0,3 mm kein Aufpreis“). Die `.kicad_pro`
ist keine eigene Quelle: `setup_rules()` schreibt die Regeln bei `just pcb` hinein. Der Umbau-Agent hatte auf
0,13/0,15/**0,1** mm gesenkt; 0,1 mm Mindestbahn liegt **genau** auf der JLC-Grenze ohne Reserve und ist hier
auf 0,13 mm angehoben. Freerouting verjüngt Bahnen an kleinen Pads (Neckdown); das ist jetzt abgeschaltet
(`--router.automatic_neckdown=false`), und `route.py` hebt verbliebene schmalere Stücke auf die Mindestbreite an.

**Ohne Aufpreis sicher nutzbar:** 0,13 mm Abstand/Bahn, Via 0,3/0,6 mm, 1 oz, 0,8 mm (bei 2 Lagen kein
Dickenaufpreis, kostenabschaetzung.md). Andere Hersteller (Aisler, PCBWay) vor einer Bestellung dort gegenprüfen.

## 10. ESD-Baustein USBLC6-2SC6: Befund und Korrektur

Quelle: ST-Datenblatt USBLC6-2 (Doc ID 11265 Rev 5, DS4260), gelesen 2026-11-02 (geprüft). Verwendet wird
U5 = ST USBLC6-2SC6 (LCSC C7519), Zweitquelle UMW (C2687116, gleiche Pinbelegung).

| Frage | Befund |
|---|---|
| Pin 1/6 und 3/4 intern verbunden? | **Ja.** Fig. 1 „Functional diagram“ bezeichnet Pin 1 **und** 6 als I/O1, Pin 3 **und** 4 als I/O2; das KiCad-Symbol zeichnet die Leitung durchgehend von Pin 1 nach 6 bzw. 3 nach 4. Pro Leitung gibt es eine Schutzzelle (PSpice-Modell Fig. 16). |
| Richtige Anbindung | **Durchschleifen** („flow-through“): Fig. 7 zeigt den Abzweig (Stich zur ESD) ausdrücklich als „Unsuitable layout“ und die gerade Durchführung unter dem Gehäuse als „Optimized layout“; Fig. 18 „PCB layout considerations“: D+in an Pin 1, D+out an Pin 6, D−in an Pin 3, D−out an Pin 4. Begründung (Kap. 2.2/2.3): Jede Stichleitung addiert L·di/dt (ca. 6 nH bei 10 mm → +144 V bei 8 kV) zur Klemmspannung. |
| Bisheriger Stand | Abzweig: D+ an Pin 1, D− an Pin 3, Pins 6/4 als „unconnected“; die Leitung lief von J4 direkt zum Modul. **Nicht datenblattgerecht.** |
| Korrektur | Schaltplan: Pin 6 = USB_D+, Pin 4 = USB_D− (`gen_main_schematic.py`). Layout (`preroute_usb()`): U5 um 180° gedreht bei x = 16,6, J4 → Pin 1 (D+) bzw. Pin 3 (D−) → gerade Bahn unter dem Gehäuse → Pin 6/4 → Via → unten bis vor C10 → Kanal oben zum Modul. Die ESD liegt jetzt in Reihe zwischen Buchse und Modul. |

VBUS (Pin 5) liegt direkt an der VBUS-Bahn der Buchse, GND (Pin 2) an der Massefläche. Den von ST empfohlenen
100-nF-Kondensator an VBUS (Fig. 18) gibt es nicht; die Schottky D2 und die 47-µF-Puffer liegen dahinter.

---

## Quellen

- Pad-Vergleich: `hardware/lib/lcsc.pretty/WIFIM-SMD_ESP32-C3-MINI-1.kicad_mod`, `/usr/share/kicad/footprints/RF_Module.pretty/ESP32-C6-MINI-1.kicad_mod`, Symbol `/usr/share/kicad/symbols/RF_Module.kicad_sym`, Platine `hardware/main-board/louie-main.kicad_pcb` (pcbnew), alle geprüft
- LCSC-Produkt-API und JLC-Teilesuche (Preise, Lager, 2026-11-02): [C5736265](https://www.lcsc.com/product-detail/C5736265.html), [C42403058](https://www.lcsc.com/product-detail/C42403058.html), [C22407186](https://jlcpcb.com/partdetail/C22407186), [C50506](https://www.lcsc.com/product-detail/C50506.html), [C42859755 NORA-W406](https://jlcpcb.com/partdetail/C42859755)
- Mouser ESP32-C6-MINI-1-H8 (Suchtreffer, Lager/Preis unsicher): <https://www.mouser.de/c/?q=ESP32-C6-MINI-1-H8>
- [ESP32-C6-MINI-1/1U Datenblatt](https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html)
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) (Fertigungsregeln, Kapitel 9)
- [ST USBLC6-2 Datenblatt DS4260](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) (Rev 5, Fig. 1/7/18, Kapitel 10)
- [TI DRV8213 Datenblatt SLVSGV9](https://www.ti.com/lit/gpn/drv8213) (Pinbelegung DSG, IPROPI, VREF 510 mV, Autosleep, RθJA)
- [ESP-IDF RF Coexistence ESP32-C6](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html) (IDF v6.1)
- [esp-zigbee-sdk](https://github.com/espressif/esp-zigbee-sdk)
- u-blox NORA-W40: [Produktseite](https://www.u-blox.com/en/product/nora-w40-series), [Mouser](https://www.mouser.in/new/u-blox/u-blox-nora-w40-modules)
- MicroPython [#17334](https://github.com/micropython/micropython/issues/17334) (WAKEUP_ALL_LOW auf C6)
