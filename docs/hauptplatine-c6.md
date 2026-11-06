# Hauptplatine mit ESP32-C6: Modul, Pinbelegung, Motortreiber, Lagenaufbau, Routing

Stand: 2026-11-06 · Beschreibt den aktuellen Stand der Hauptplatine (Platine A, `hardware/main-board/`).
Geltende Entscheidungen: **ESP32-C6-MINI-1**, Motortreiber **DRV8213DSG**, **USB-C J4** auf der Platine (Flashen
nur über J4), **4 Lagen**, einseitig maschinell bestückt (unten nur Pads, Testpunkte und DNP-Footprints).
Verworfene Varianten (C3, DRV8833, 2 Lagen, frühere USB-Varianten): [decision-history.md](decision-history.md).
Grundlagen: [analyse-funk-controller.md](analyse-funk-controller.md) 3b, [hardware-konzept.md](hardware-konzept.md),
[idee-usb-c-hauptplatine.md](idee-usb-c-hauptplatine.md). Firmware: [firmware-architecture.md](firmware-architecture.md).

Markierungen: **(geprüft)** = Quelle gelesen oder an den Projektdateien nachgerechnet · **(unsicher)** = Sekundärquelle,
Schätzung oder nicht im Datenblatt nachgelesen.

## Kurzfassung

- **Modul:** ESP32-C6-MINI-1, Ziel **-H8 (8 MB)**, Rückfall **-N4 (4 MB)**. Beide sind pin- und footprintgleich,
  man entscheidet erst bei der Bestellung. Das H8 ist seit 2026-11-06 auch bei JLC lieferbar (620 Stück).
- **Footprint:** eigener `lcsc:WIFIM-SMD_ESP32-C6-MINI-1`. **Nicht** den KiCad-Footprint `RF_Module:ESP32-C6-MINI-1`
  nehmen: Sein Courtyard enthält eine 43 × 20 mm große Antennen-Sperrzone (bricht `antenna_keepout()`), ein
  3D-Modell fehlt.
- **Motortreiber:** **DRV8213DSG** (WSON-8 2 × 2 mm) mit Strommessung (IPROPI), Strombegrenzung (2 A) und Autosleep.
  Kein Shunt, kein nSLEEP/nFAULT, nur 2 GPIOs.
- **Hebel:** „Hebel zu“ = HIGH (R3 nach GND, R4 nach 3V3); der Hebel weckt mit ANY_HIGH an IO3.
- **USB-C J4** mit ESD (durchgeschleift), CC-Widerständen und Power-Path (D2 für VBUS, Q1 für BAT_IN).
- **Zigbee:** Die Hardware braucht **nichts zusätzlich**. Ein Coordinator neben dem eigenen Hotspot oder neben
  BLE-Scan wird von Espressif **nicht unterstützt (X)**; Zigbee ist nur im Heim-WLAN realistisch.
- **Lagen:** 4 Lagen (JLC04081H-3313), In1 durchgehend GND, Regeln 0,15/0,15 mm, Via 0,3/0,5 mm (Kapitel 11).
- **Optionale Pads unten:** Spieler-Eingänge J6, LED-Anschluss J7, Testpunkte, DNP-Footprints (11.7).

---

## 1. Modul und Flash

| Kandidat | Maße (mm) | Flash | Antenne | Lieferbarkeit / Preis (2026-11-02) | Bewertung |
|---|---|---|---|---|---|
| **ESP32-C6-MINI-1-N4** (C5736265) | 13,2 × 16,6 × 2,4 | 4 MB | PCB | LCSC 1.380, JLC 3.921 Stk.; 4,14 / 3,63 USD (1/10) (geprüft) | **Rückfall**, sofort bestückbar |
| ESP32-C6-MINI-1-H4 (C6553337) | gleich | 4 MB, 105 °C | PCB | JLC 534; 4,48 / 3,84 (geprüft) | kein Vorteil |
| **ESP32-C6-MINI-1-H8** (C42403058) | gleich | **8 MB**, 105 °C | PCB | **JLC 620 Stk.** (geprüft, JLC-Teile-API 2026-11-06; am 2026-11-02 noch 0); LCSC 11,67 (1), 4,66 (200+) (geprüft). **Mouser ca. 4,70 €, ca. 6.000 Stk.** (unsicher, Suchtreffer) | **Ziel**, direkt bei JLC bestückbar |
| ESP32-C6-MINI-1U-H4 (C20627095) | 13,2 × 12,5 | 4 MB | U.FL | JLC 3.938; 4,20 (geprüft) | nur Plan B Antenne; ein 1U-H8 ist bei LCSC nicht gelistet |

Andere C6-Module passen nicht ins AA-Format oder haben mit PCB-Antenne nur 4 MB; ein Chip-Design (C6FH8 + eigene
Antenne) lohnt nicht (decision-history.md).

**Entscheidung:** **ESP32-C6-MINI-1-H8** einplanen. Gibt es zum Bestellzeitpunkt bei JLC kein H8, wird ohne
Layoutänderung das **N4** bestückt.

**Warum 8 MB:** Echtes OTA braucht zwei App-Partitionen; dazu kommen Web-UI, Modi und ggf. Zigbee. Mit 8 MB passen
z. B. 2 × 3 MiB App plus ca. 1,9 MiB Daten. Mit 4 MB (N4) wird OTA knapp; wie groß die Rust-Firmware (std auf
ESP-IDF) wird, ist noch nicht gemessen (unsicher). Partitionierung: [firmware-architecture.md](firmware-architecture.md).

---

## 2. Modul auf der Platine

### 2.1 Footprint (geprüft)

Footprint `lcsc:WIFIM-SMD_ESP32-C6-MINI-1` (erzeugt von `fetch_parts.py`): 53 Pads im 0,8-mm-Raster (0,8 × 0,4 mm),
Pad 49 aus 9 Teilflächen, Courtyard 13,2 × 16,6 mm, 3D-Modell des C6. Die Pads sind aus dem padgleichen
lcsc-Footprint des ESP32-C3-MINI-1 übernommen, weil der EasyEDA-Footprint des C6 bis 20 µm neben dem Raster liegt. GND-Pads 1, 2, 11, 14, 36–53;
3V3 = 3, EN = 8; NC = 4, 7, 21, 32–35. Antenne am Ende −y des Footprints → Platine −x.

Der KiCad-Footprint `RF_Module:ESP32-C6-MINI-1` ist padgleich (Pad 49 max. 5 µm verschoben), hat aber ein Courtyard
von 13,5 × 16,9 mm **plus Sperrzone 43,2 × 20,4 mm** (unbrauchbar für `antenna_keepout()`) und in KiCad 9 kein
3D-Modell.

### 2.2 Lage der Pads auf der Platine

Modul bei x = −8,8, Drehung 90°, Antenne bei −x (aus `louie-main.kicad_pcb` gelesen, geprüft):

| Modulseite | Pads (Reihenfolge) | Lage | Nachbarn |
|---|---|---|---|
| **rechts** (x = −3,9), y +4,8 → −4,8 | 12 IO0, 13 IO1, 14 GND, 15 IO6, 16 IO7, **17 IO12**, **18 IO13**, 19 IO14, 20 IO15, 21 NC, 22 IO8, 23 IO9, 24 IO18 | zum Treiber und zu USB-C | 0402-Reihe x = −1,9 |
| **Kante +y** (y = +5,9), x −12,8 → −4,8 | 1/2 GND, 3 3V3, 4 NC, 5 IO2, 6 IO3, 7 NC, 8 EN, 9 IO4, 10 IO5, 11 GND | ISEN-Seite | R5 (SENSE) |
| **Kante −y** (y = −5,9), x −4,8 → −12,8 | 25 IO19, 26 IO20, 27 IO21, 28 IO22, 29 IO23, 30 RXD/IO17, 31 TXD/IO16, 32–35 NC | VSYS-Band, C1/C2, LDO | J3 unten |

**Alle ADC-Pins (IO0–IO6) liegen in der +y-Hälfte.** USB (IO12/13) liegt mittig rechts und zeigt damit direkt zur
USB-C-Buchse J4 (x ≈ 10,5–20,1, Pads bei y ≈ −1,6). Dafür bleibt **ein Kanal bei y ≈ −0,5 … +1,2 frei**; der
kleine DRV8213 (Kapitel 3) sitzt an der Modulecke −y.

### 2.3 Pinbelegung (maßgeblich)

| GPIO (Pad) | Netz | Funktion | Begründung |
|---|---|---|---|
| IO0 (12) | VBAT_ADC | Teiler 470k/470k | ADC1_CH0; C6 misst bis 3,3 V → 5,5 V ergibt 2,75 V |
| IO1 (13) | ISEN_ADC | IPROPI über RC | ADC1_CH1, +y-Seite wie der Treiber-Abgriff |
| IO2 (5) | INT | INT-Pad J2 (Sensor-INT1 oder Erschütterungsschalter) | LP-GPIO → Deep-Sleep-Wecken, kein Strapping |
| IO3 (6) | SENSE | Hebel, Deep-Sleep-Wecken | LP-GPIO, bleibt |
| IO4 (9) | VBUS_DET | VBUS-Teiler (neu) | ADC1_CH4 + LP-Wecken beim Einstecken; Strapping nur SDIO-Flanke |
| IO5 (10) | IO5 | S1 Spieler-Eingang (J6-2) | ADC/Deep-Sleep-Wecken |
| IO6 (15) | SDA | I²C (LIS2DH12, J2) | LP-I²C (vom LP-Kern nutzbar) |
| IO7 (16) | SCL | I²C (J2) | LP-I²C |
| IO8 (22) | IO8 | Strapping, **10 k Pull-up**; S4 Spieler-Eingang (J6-5) | muss beim Download 1 sein, für SPI-Boot egal (11.7) |
| IO9 (23) | BOOT | J3, Taster gegen GND | interner Pull-up |
| IO12 (17) | USB_D− | J4 A7/B7 über ESD U5 (Pin 3 → 4) | fest im Chip |
| IO13 (18) | USB_D+ | J4 A6/B6 über ESD U5 (Pin 1 → 6) | fest im Chip |
| IO14 (19) | LED | Status-LED über 1 k | unterhalb des USB-Kanals |
| IO15 (20) | IO15 | Freigabe Lastschalter U6 (VLED an J7), R22 100 k nach GND | Strapping JTAG-Quelle, ohne eFuse wirkungslos; kein interner Pull |
| IO18 (24) | MOT_IN1 | DRV8213 IN1 (LEDC-PWM) | Modulecke unten rechts, nahe Treiber und VSYS-Band |
| IO19 (25) | MOT_IN2 | DRV8213 IN2 (LEDC-PWM) | dito |
| IO20 / IO21 (26/27) | IO20 / IO21 | S2 / S3 Spieler-Eingänge (J6-3/-4) | interner Pull-up |
| IO22 / IO23 (28/29) | – / IO23 | IO22 frei (Reserve) / LED-Daten J7-2 | Powerbank wach halten per Firmware (idee-powerbank.md) |
| IO17 RXD (30) | RXD | Konsole, J3-5 | |
| IO16 TXD (31) | TXD | J3, Konsole | ROM-Log |

**Bis auf IO22 (Reserve) sind alle GPIOs belegt**; IO5, IO8, IO15, IO17, IO20, IO21 und IO23 gehen auf optionale
Pads und nicht bestückte Footprints unten (11.7, idee-optionale-hardware.md 0b).

### 2.4 Strapping, USB, Reset

- **IO8:** 10 k nach 3V3 (R11). **IO9:** interner Pull-up reicht, Pad J3. **IO15:** Strapping ohne eFuse
  wirkungslos, R22 (DNP) nach GND. **IO4/IO5:** Pegel beim Booten egal (SDIO-Timing). **IO2** ist beim C6 kein
  Strapping-Pin; R10 ist SCL-Pull-up (geprüft, analyse-funk-controller.md 3b.1).
- **USB:** IO12 = D−, IO13 = D+. ESD (U5) direkt an J4 und **durchgeschleift**: J4 → U5 Pin 1/3 → unter dem
  Gehäuse → Pin 6/4 → Modul. D+/D− kreuzen an J4 (Reihenfolge B7 A6 A7 B6). Kein Stich zu J1: **Flashen nur über
  J4**; J1-2/3 sind ohne Netz.
- **ESD-Befund (geprüft, ST DS4260 Rev 5):** Beim USBLC6-2SC6 sind Pin 1/6 (I/O1) und 3/4 (I/O2) intern verbunden.
  ST zeigt den Abzweig zur ESD als „Unsuitable layout“ (Fig. 7) und das Durchschleifen als „Optimized layout“
  (Fig. 18): D+in Pin 1 → D+out Pin 6, D−in Pin 3 → D−out Pin 4. Jede Stichleitung addiert L·di/dt zur
  Klemmspannung (ca. 6 nH bei 10 mm → +144 V bei 8 kV). VBUS an Pin 5, GND an Pin 2; den von ST empfohlenen
  100-nF-Kondensator an VBUS gibt es nicht (D2 und die 47-µF-Puffer liegen dahinter). Zweitquelle UMW C2687116,
  gleiche Pinbelegung.
- **EN:** R2 10 k / C12 1 µF. Download geht beim C6 per USB-Serial-JTAG automatisch; BOOT bleibt als Notweg auf
  dem Pad.

### 2.5 Wecken über SENSE

**Beschaltung: R3 100 k OUT_A → GND, R4 10 k OUT_B → 3V3, R5 100 k SENSE → IO3.** „Hebel zu“ = HIGH.

| Zustand | SENSE | Wecken |
|---|---|---|
| Hebel offen | 0 V (über 100 k) | – |
| Hebel zu | 3,3 V × 100/110 ≈ **3,0 V** | ext1-Wecken ANY_HIGH an IO3 |
| Motor läuft | nicht aussagekräftig, Strom per IPROPI | – |

Ruhestrom bei geschlossenem Hebel ca. 30 µA. OUT_B speist bei VM = 5,5 V ca. 0,2 mA in die 3V3-Schiene zurück;
die Last nimmt das auf (unkritisch). **Sonderfall:** Bleibt der Hebel beim Einschlafen zu, muss die Firmware auf
LOW wecken oder per Timer prüfen (z. B. alle 5 s). Diesen Fall im Testaufbau prüfen ([test-hardware.md](test-hardware.md) 4.2).
Warum nicht der umgekehrte Pegel: decision-history.md.

### 2.6 Antenne (Befund L2 aus analyse-funk-controller.md)

`antenna_keepout()`: Regelflächen „Antenne“, „Antenne Rand“ und „Antenne Ende“ **auf allen vier Lagen**, mit
Verbot für Kupferfläche und Vias, **Leiterbahnen erlaubt**. Unter der Antenne liegt kein GND; die OUT_A-Bahn zu BT1
läuft unten im Randstreifen. Der Randstreifen liegt an der Kante **−y** (OUT_A läuft vom DRV8213 an der Modulecke
−y ohne Kreuzung zu BT1; elektrisch gleichwertig zu +y, unsicher → RSSI-Test in beiden Einbaurichtungen)
(analyse-funk-controller.md 2.3).

---

## 3. Motoransteuerung

**Entscheidung: DRV8213DSGR (C22407186), GAINSEL an GND, R_IPROPI (R1) 1,24 k (1 %) an GND, danach R8 1 k /
C14 100 nF zum ADC (IO1).** Den Kondensator nicht direkt an IPROPI legen, er würde die Stromregelung verzögern.
Begründung: Strommessung, Strombegrenzung und Autosleep sind eingebaut; das spart Shunt, nSLEEP/nFAULT, 2 GPIOs und
ca. 30 mm² gegenüber einem Treiber im HTSSOP-16. Verworfene Treiber (DRV8833, DRV8212, DRV8837): decision-history.md.

### 3.1 Daten DRV8213DSG

| Größe | Wert |
|---|---|
| VM | **1,65–11 V** (geprüft) |
| Rds(on) HS+LS | 240 mΩ typ. (GAINSEL = Low) (geprüft) |
| Strom | 4 A Spitze, OCP ca. 4 A, RθJA 65,9 K/W (geprüft) |
| Strommessung | **IPROPI** 205 µA/A, ±6 % ab 350 mA (geprüft) |
| Strombegrenzung | **ITRIP = 0,51 V / (R_IPROPI × 205 µA/A)**, R = 1,24 k → 2 A (geprüft) |
| Sleep | **Autosleep** nach 1 ms bei IN1 = IN2 = 0, < 60 nA (geprüft) |
| Fehler | Auto-Retry (OCP, TSD), kein Pin (DSG) |
| Bremsen / rückwärts | ja: 1/1 = Bremse, 0/0 = Coast (Hi-Z) (geprüft) |
| Gehäuse | WSON-8 2 × 2 mm mit EP, Courtyard ca. 7 mm² |
| Bauteile im Block | U2, R1 (R_IPROPI), C4, R8, C14 |
| GPIOs | **2** (IN1 = IO18, IN2 = IO19) |
| Preis 10 Stk. (JLC) | **0,93 USD** (C22407186, 3.749 Stk., Extended, 2026-11-02) |

### 3.2 Auslegung

- Läuft ab 3,0 V Akku bis 5,5 V USB, bremst, fährt rückwärts und ist in Coast/Autosleep hochohmig (für die
  Hebel-Erkennung nötig; dass im Sleep kein Ausgangs-Pull-down wirkt, ist unsicher → auf der Prototyp-Platine prüfen).
  Strombegrenzung 2 A.
- **Blockier-Erkennung:** IPROPI misst beim Fahren **und** in der Bremsphase. Daher PWM als **Fahren/Bremsen**:
  vorwärts IN1 = 1, IN2 = PWM mit Tastgrad (1 − d). Das ergibt 255 mV/A am ADC. Die Hardware-Stall-Erkennung gibt
  es nur im RTE-Gehäuse; die Firmware wertet Strom > Schwelle über eine Zeit x aus.
- **Wärme:** 1 A → 0,24 W → +16 K; 2 A Dauer (blockiert) → ca. 1 W → +63 K (geprüft, Rechnung mit RθJA). Die
  Firmware muss eine Blockade nach ≤ 0,5 s abschalten. 2 Thermal-Vias (0,3 mm) im EP.
- **PWM:** LEDC mit 20 kHz und ca. 11 Bit Auflösung reicht; MCPWM wird nicht gebraucht.
- **Eingänge:** IN1/IN2 haben interne 200-k-Pull-downs im DRV8213. **Während** des Resets ziehen die internen ~45-k-Pull-ups
  von IO18/IO19 beide Eingänge auf HIGH → Bremse (kein Antrieb, kein Anlauf möglich); nach dem Reset sind beide 0
  (Coast) (geprüft, C6-Datenblatt Tab. 2-1/2-2). Entscheidung offen (F17): so lassen oder externe 3,3-k-Pull-downs für
  Coast auch im Reset. Messung in Reset, Boot und Deep Sleep: [test-hardware.md](test-hardware.md) 4.4.
- Der DRV8213 und der Motorbetrieb werden erst auf der Prototyp-Platine getestet; auf dem Steckbrett gibt es keinen
  Motortreiber, nur Prüfungen vor der Bestellung (Motorstrom am Labornetzteil, Hebel-Netzwerk, Pegel) und LED-Modus
  ([test-hardware.md](test-hardware.md) 4, 5).

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
| Stack | `esp-zigbee-sdk`, vorkompilierte Bibliotheken, ESP-IDF 5.5.x, C-API | (geprüft) |
| Rust-Firmware | Da die Firmware auf ESP-IDF läuft (std, esp-idf-sys), lässt sich das SDK als ESP-IDF-Komponente einbinden und per FFI aufrufen | (unsicher, nicht erprobt) |
| Flash/RAM | Grob +0,5–0,8 MB App, 50–100 KB RAM für einen kleinen Coordinator. Für OTA wird 8 MB empfohlen | (unsicher) |
| Thread/Matter | gleiche Koexistenz-Grenzen (Thread-Router + SoftAP = X). Matter über WLAN braucht kein 802.15.4 | (geprüft / unsicher) |

**Einschätzung:** Mit eigenem Hotspot (Partymodus, 8 Handys) ist ein Zigbee-Coordinator **ausgeschlossen**, und
neben den BLE-BTHome-Tastern ebenfalls. Praktikabel wäre nur „Louie im Heim-WLAN (STA) + Zigbee“. Dort ist es aber
einfacher, die Taster über Home Assistant per WLAN anzubinden. **Vorgesehen ist:** C6, **8-MB-Flash (H8)**, die
Antennen-Sperrflächen (2.6) und ein guter Einbauort. Zigbee ist **kein Grund für weitere Bauteile**
(Betrieb: [idee-zigbee-betrieb.md](idee-zigbee-betrieb.md)).

---

## 5. Priorität Platine A, optionale Platine B

Vorgabe: **A funktioniert vollständig allein** (zweites Fach = Kupferbrücke oder Ladeplatine).

### 5.1 Inhalt von A

| Baugruppe | Status | Bemerkung |
|---|---|---|
| ESP32-C6-MINI-1 + C9, C10, R2, C12 | **Muss** | – |
| Motortreiber DRV8213 + R1, C4, R8, C14 | **Muss** | Strommessung per IPROPI (Kapitel 3) |
| LDO AP2112K + C8, C11 | **Muss** | optional RT9080 (C841192, ca. 2 µA Ruhestrom, Pinbelegung vor Tausch prüfen, unsicher) |
| SENSE (R3, R4, R5) | **Muss** | Pegel 2.5 |
| VBAT-Teiler (R6, R7, C13) | **Muss** (Unterspannung, Duty = U_soll/U_akku) | – |
| USB-C J4, ESD U5, CC R12/R13, D2, Q1, R14/R15 | **Muss** | ESD-Zweitquelle UMW; R14/R15 = VBUS_DET-Teiler und Gate-Pull-down Q1 |
| Puffer C1, C2 (47 µF) | **Muss** | – |
| Status-LED D1/R9 | sinnvoll (Diagnose ohne Handy) | – |
| BOOT/EN/TXD/RXD | **nur Pads** (J3, unten) | kein Taster oben |
| I²C-Pull-ups R10/R16, IO8-Pull-up R11 | auf A (Breakouts ohne Pull-ups, IO8-Strapping) | – |
| LIS2DH12 + C15 | oben, **bestückungsoptional** (DNP möglich) | INT1 an IO2; parallel Pads J2 |
| Optionale Pads/DNP unten | J6, J7, TP1/TP2, JP1; DNP: U6, F1, C17, R19, R20, C16, R22 | 11.7 |

### 5.2 Schnittstellen (Unterseite A)

| Pad | Netz | Zweck |
|---|---|---|
| J2-1…5 | 3V3, GND, SDA (IO6), SCL (IO7), INT (IO2) | Sensor-Breakout, Erschütterungsschalter (INT ↔ GND, interner Pull-up) oder Platine B |
| J3-1…5 | EN, TXD, BOOT, GND, RXD (IO17) | Service (UART0-Konsole, Download) |
| J1-1…4 | BAT_IN, –, –, GND | Ladeplatine: nur BAT_IN und GND; Pads 2/3 ohne Netz (Flashen nur über J4) |
| J5 +/− | BAT_IN, GND | geschützte Zelle direkt |
| J6, J7 | Spieler-Eingänge S1–S4, LED-Anschluss | 11.7 |

**Ohne Sensor:** Die Pull-ups auf A halten den Bus definiert. Die Firmware macht beim Start einen I²C-Scan (0x18/0x19)
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

### 5.4 Empfehlung

**A** = C6 + DRV8213 + LDO + SENSE + VBAT + IPROPI + USB-C-Stufe + LED, alles Übrige als Pads. **Zuerst nur A
fertigen**, im zweiten Fach die Kupferbrücke oder die Ladeplatine. Sensor oben bestückungsoptional, sonst Breakout
oder Federschalter an J2. Die **Ladeplatine v0.1** bleibt an J1 nutzbar (BAT_IN). Eine B-Platine erst später, und
dann nur als v0.2 „Lade + Sensor“.

---

## 6. Mechanik: USB-C gegen AA-Hüllkurve

Rechnung aus dem 3D-Export (`just modell`, `just hull` → `hull_check.py`, Eckpunkte von
`build/main-board/3d/louie-main.stl`; Platinenoberseite 0,5 mm über der Zellachse):

| Größe | Wert |
|---|---|
| J4 Vorderkante | y = +6,10 mm (Platinenkante 6,75) |
| J4 Oberkante | z = +3,75 mm über der Zellachse |
| größter Radius aller Bauteile | **6,94 mm** (J4, obere vordere Kante) bei AA-Radius 7,25 → **ca. 0,3 mm Luft** |
| Bauteile unter den Endkappen (x > 22,2) | keine |
| Unterseite | größtes \|y\| 4,80 mm (Tasche 5,2 mm), Bauhöhe unten siehe 11.7 |

`huelle.scad`: Kabelfenster auf **+y** (`kabel_seite = 1`, `kabel_x = 14,5`, `kabel_l = 9`) für J1 und J5 unter der
Buchse, Platinen-Dummy auf dem C6-Stand, Ansicht `teil = "kollision"`. Die Schale liegt unter der Platine, die
Buchse oben ist frei zugänglich; ein eigenes Buchsenfenster ist nicht nötig. **Offen:** Durch das Kabelfenster fehlt
unter J4 der Randsteg (+y) als Auflage; Steckkräfte gehen in die Lötlaschen (0,8-mm-Platine, idee-usb-c-hauptplatine.md).
Abhilfe: Fenster kürzer und tiefer oder Stützsteg zwischen J1 und J5 (am Druckteil testen).

## 7. Offene Punkte und Prüfungen vor der Bestellung

1. Prüfungen vor der Bestellung ([test-hardware.md](test-hardware.md) 4): Motorstrom, Hebel-Netzwerk, Wecken mit
   ANY_HIGH an IO3, Strapping, Pegel IO18/IO19 (F17), ADC-Teiler.
2. DRV8213 am Louie-Motor: Strom, Erwärmung bei Blockade, Hebel-Erkennung im Autosleep (Ausgänge Hi-Z).
3. H8-Bestand bei JLC zum Bestellzeitpunkt prüfen (2026-11-06: 620 Stück), sonst N4.
4. Routing der Platine mit den Pads unten abschließen (11.7), danach ERC/DRC 0 und 0 offen.
5. Gerber (`just fab`) in den JLC-Rechner (Website und JLCONE) laden, Aufbau JLC04081H-3313 auswählen, Preis und
   Fertigungszeit für 0,8 mm ablesen (kostenabschaetzung.md 5.7).
6. Layout im KiCad-GUI ansehen (Router-Umwege, Via-Anzahl), ggf. einzelne Bahnen glätten – danach gilt der GUI-Stand.
7. RSSI-Test (Antennen-Randstreifen −y, beide Einbaurichtungen).
8. Hülle: Auflage unter J4 (Kapitel 6), Druckprobe.
9. Andere Hersteller (Aisler, PCBWay) vor einer Bestellung dort gegenprüfen.

Teilkosten (10 Stück, LCSC/JLC 2026-11-02): C6-N4 3,60 USD, H8 ca. 5,4 USD (Mouser 4,70 €, unsicher), DRV8213
0,93 USD, USB-C-Stufe ca. 0,37 USD (J4 0,19, U5 0,05, D2 0,04, Q1 0,08, 3 R). Gesamtkosten: [kostenabschaetzung.md](kostenabschaetzung.md).

*Kapitel 8–10 sind entfallen (Verlauf in [decision-history.md](decision-history.md)); die Nummer 11 bleibt wegen
Verweisen aus Skripten und anderen Dokumenten.*

---

## 11. 4 Lagen: Aufbau, Regeln, Generator, Routing

**Entscheidung 2026-11-03: 4 Lagen** (Gründe und verworfene 2-Lagen-Variante: decision-history.md).
Die Platine liegt in `hardware/main-board/louie-main.kicad_pcb` (Projekt `louie-main.kicad_pro`, Regeldatei
`louie-main.kicad_dru`, Routing-Ergebnis `routing.json`); `just pcb`, `just route`, `just erc`, `just drc`,
`just images`, `just modell`, `just render`, `just fab` arbeiten ohne Parameter mit ihr. Alles wird aus den
Skripten erzeugt, nichts im GUI.

### 11.1 Lagenaufbau

**JLC-Standardaufbau JLC04081H-3313** (0,8 mm, 4 Lagen, außen 1 oz, innen 0,5 oz) **(unsicher)**: Werte aus
einer Stackup-Datei, die aus der Vorlage des JLC-Impedanzrechners erzeugt wurde (Hive-RSI-Lab/hive-hwde
PR 533, 2026-11-01); der JLC-Rechner selbst liefert die Werte nur per JavaScript und wurde nicht gelesen.
Die Summe 0,7992 mm passt zur Nenndicke. Vor der Bestellung im JLC-Bestellformular („Layer stackup“)
bestätigen.

| Lage | Material | Dicke | εr | Verwendung (gewählte Variante A) |
|---|---|---:|---:|---|
| L1 F.Cu | Kupfer 1 oz (inkl. Galvanik) | 0,035 mm | – | Bauteile, kurze Signale, GND-Füllung |
| Prepreg | 3313 (1 ×) | 0,0994 mm | 4,1 | |
| L2 In1.Cu | Kupfer 0,5 oz | 0,0152 mm | – | **GND durchgehend**, keine Bahnen (Sperrfläche „GND-Lage“) |
| Kern | FR4 | 0,5 mm | 4,48 | |
| L3 In2.Cu | Kupfer 0,5 oz | 0,0152 mm | – | Signale (Querungen, Busse), GND-Füllung dazwischen |
| Prepreg | 3313 (1 ×) | 0,0994 mm | 4,1 | |
| L4 B.Cu | Kupfer 1 oz | 0,035 mm | – | Lötpads (J1/J2/J3/J5/BT), Motor-Ausgänge, Signale, GND-Füllung |

Der Aufbau steht als `(stackup …)` in der `.kicad_pcb` (`STACKUP`, `write_stackup()` in `gen_main_pcb.py`).

**Lagenbelegung (Variante A):** Sig / **GND** / Sig+GND / Sig+GND, also 3 Signallagen. Andere Aufteilungen
(3V3-Fläche auf L3, zweimal GND, GND außen) sind verworfen (decision-history.md).

- **Routbarkeit:** Querungen und lange Busse laufen auf L3; L4 muss keine Massefläche sein. Eine 3V3-Fläche auf L3
  hilft nur 3V3 (10 Pads) und nimmt die Lage für die Querungen; im Probelauf mit Freerouting war sie nicht besser.
- **HF-Masse:** L2 liegt 0,1 mm unter den Bauteilen; Modul, DRV8213 und USB haben eine geschlossene Bezugsfläche.
  Unter der Antenne bleibt **auf allen vier Lagen** kein Kupfer: die Sperrflächen „Antenne“, „Antenne Rand“ und
  „Antenne Ende“ aus `antenna_keepout()` gelten für `AllCuMask` und stehen in der Datei mit
  `(layers "F.Cu" "B.Cu" "In1.Cu" "In2.Cu")` (geprüft); die GND-Flächen aller Lagen enden vor der Antenne.
- **USB:** Full-Speed (12 Mbit/s) braucht keine Impedanzkontrolle. 0,15-mm-Bahnen über GND im Abstand 0,1 mm
  ergeben grob 50 Ω einzeln (unsicher, Faustformel); das Paar ist vorgeroutet (ESD durchgeschleift, 2.4).
- **Motorstrom:** Die 0,4/0,5-mm-Hauptwege (OUT_A/OUT_B, VSYS, VBUS, BAT_IN) sind vorgeroutet; die Rückströme
  laufen über die durchgehende L2.

### 11.2 Designregeln (4 Lagen)

Quelle: [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), abgerufen 2026-11-03 (geprüft),
und kostenabschaetzung.md 5.4.

| Größe | JLCPCB 4 Lagen | Projektregel (`RULES`, `louie-main.kicad_dru`) | Reserve |
|---|---|---|---|
| Bahn / Abstand | 0,09 / 0,09 mm (außen 1 oz, innen 0,5 oz) | **0,15 / 0,15 mm**, Standardbahn 0,2 mm | +67 % |
| Via Bohrung / Ø | min. 0,15 / 0,25 mm; Aufpreis unter 0,3 mm Bohrung (bzw. 0,2/0,25 mit Ø < 0,45) | **0,3 / 0,5 mm**, Restring 0,1 mm | kein Aufpreis, Restring 2 × Minimum |
| Via-in-Pad | nur mit Aufpreis (POFV), frei erst ab 6 Lagen | **nicht verwendet** (Router sperrt Vias in Pads) | – |
| Via-Bohrung – Kupfer | 0,2 mm (innen) | 0,25 mm (Platinenregel) | +25 % |
| Bauteilbohrung – Bahn | 0,28 mm (empf. 0,35) | 0,28 mm außen | = Minimum |
| Bauteilbohrung – Kupfer innen | 0,3 mm | 0,3 mm (eigene DRC-Regel) | = Minimum |
| Lochabstand | 0,2 mm | 0,25 mm | +25 % |
| Kupfer – Fräskante | 0,2 mm | 0,3 mm (+ Sperrstreifen „Rand“) | +50 % |
| Leistungsbahnen | – | vorgeroutet 0,4/0,5 mm auf den Außenlagen (seit 2026-11-04 auch Q1 → VM, 11.7), 3V3 0,25 mm, VSYS-Abzweige 0,3–0,4 mm (nie schmaler) | – |

**Via 0,3/0,5 statt 0,3/0,6 mm:** Mit 0,6 mm Durchmesser blieben im Probe-Routing deutlich mehr Verbindungen
offen (Lauf 1: 13 statt 5); die Bohrung bleibt 0,3 mm, es gibt keinen Aufpreis, und 0,1 mm Restring ist das
Doppelte des JLC-Minimums (0,05 mm bei 0,15/0,25). Die Vias der Vorrouten haben ebenfalls 0,5 mm.

### 11.3 Umsetzung im Generator

| Datei | Aufgabe |
|---|---|
| `gen_main_pcb.py` | erzeugt die 4-Lagen-Platine in `hardware/main-board/`: `RULES`, `DRU` (Regeldatei), `STACKUP`, Umriss aus `board_outline.py`, In1 = GND-Fläche + Sperrfläche „GND-Lage“ (keine Bahnen), In2 = GND-Füllung, Vorrouten (USB, VBUS, BAT_IN, Motor, VSYS), `PLACEMENT_OVERRIDES` (u. a. **R15 um 180° gedreht**, sonst ist sein GND-Pad zwischen VBUS-Bahnen und dem USB-Paar eingeschlossen) |
| `placement.py` | Platzierung (einseitig bestückt, Teile unten nur Pads/DNP) |
| `route_fix.py` | eigener Labyrinth-Router: A* über F.Cu/In2.Cu/B.Cu im 0,05-mm-Raster, Vias 0,3/0,5 nur wo sie auf allen Lagen passen, Fluchtgassen vor den Modulpads, Aufreißen und neu routen mit Verlaufskosten, danach GND-Inseln per Via an In1, Neustart mit Vorrang der offenen Netze; deterministisch |
| `route.py`, `route_gate.py` | `main-board` (4 Lagen, `ROUTER=own` Standard mit 6 Kostenvarianten, oder `ROUTER=freerouting` + Nachrouten) und `charger-board` (2 Lagen, Freerouting); Keep-best-Gate gegen `routing.json` |
| `stitch.py` | Stitching für 4 Lagen (Gegenlage = In1, Abstandsprüfung auf allen Lagen) |
| `justfile` | `pcb`, `plot` ohne Parameter; `main-board` = anlegen + routen + ERC + DRC; `images` erzeugt auch die Innenlagen |

**Footprints:** U1 `lcsc:WIFIM-SMD_ESP32-C6-MINI-1` (2.1); U2 `Package_SON:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm`
(padgleich zu Texas DSG0008A, mit 3D-Modell); J4 `louie:USB_C_Receptacle_HRO_TYPE-C-31-M-12` (von `fetch_parts.py`,
3D-Modell des LCSC-Teils, kein Bestückungsdruck über der Kante); D2 EasyEDA-SMAF mit korrigiertem Courtyard.
GND-Pads sind voll an die Flächen angebunden (keine Wärmefallen; kleine Pads bekamen sonst nur eine Speiche).

**Bilder** (`just images`, `docs/bilder/`): `platine-*.png`, `kupfer-oben.png` = L1, `copper-l2-gnd.png` = L2,
`copper-l3-signal.png` = L3, `kupfer-unten.png` = L4, `platzierung.png`.

Befehle: `just pcb && just route && just erc && just drc` oder kurz `just main-board`; Bilder `just images`,
3D `just modell`. `just route` braucht je nach Variante 20–60 min (3 Varianten parallel, eigener Router in Python).

### 11.4 Routing-Ergebnis

**Stand des vorigen Designs (bis 2026-11-03, ohne die Pads aus 11.7; in Git HEAD und `routing.json`), Versuch 3, Via-Kosten 40:**

| Prüfung | Ergebnis |
|---|---|
| ERC (`just erc`) | **0 Fehler, 0 Warnungen** |
| DRC (`just drc`) | **0 Verstöße, 0 offene Verbindungen**, Schaltplan-Parität 0 Abweichungen, 0 Footprint-Fehler |
| Bahnen | F.Cu 225 mm, In2.Cu 186 mm, B.Cu 229 mm; **In1.Cu 0 mm** (GND-Lage frei von Bahnen) |
| Vias | 116 (0,3/0,5 bzw. 0,3/0,6 mm aus `stitch.py`), davon 46 GND |
| Antenne | Sperrflächen „Antenne“, „Antenne Rand“, „Antenne Ende“ auf F.Cu/In1/In2/B.Cu; darin **0 mm² Fläche auf allen vier Lagen**, keine Bahn und kein Via außer der erlaubten OUT_A-Bahn zu BT1 auf B.Cu im Randstreifen/Ende (wie 2 Lagen) (geprüft, pcbnew) |
| Hüllkurve | größter Radius **6,94 mm** (J4, wie 2 Lagen 6,93; +0,01 mm durch die Kupferdicken des Lagenaufbaus im 3D-Export) < 7,25 mm; x > 22,2: nur Platine (z ≤ 0,73 mm) (`build/main-board/3d/louie-main.stl`, gleiche Rechnung wie Kapitel 6) |
| Platzierung | identisch zu 2 Lagen bis auf R15 (180° gedreht, 11.3) |

**Warum ein eigener Router?** Freerouting 2.5.0 (wie bei 2 Lagen) blieb auf 4 Lagen bei **10–18 offenen
Signalverbindungen** (mehrere Einstellungen: In1 als Ebene mit/ohne GND-Anbindung, In2 als 3V3-Ebene, Fanout an/aus).
Dazu zwei Eigenheiten: Ohne Ebene behandelt Freerouting eine „power“-Lage als Signallage und legte Bahnen auf In1;
eine Sperrfläche nur für Bahnen auf In1 (`wire_keepout`) verhindert in 2.5.0 auch alle Vias. Die vorhandenen
Vorrouten (USB, VBUS, Motor) blieben unverändert; `route_fix.py` routet alle übrigen Signale, die GND-Anbindung
und die Inseln. `ROUTER=freerouting just route` ist als Alternative erhalten (Freerouting + Nachrouten).

**Streuung (gleiche Startplatine, verschiedene Kostenvarianten aus `ROUTER_VARIANTS`):**

| Lauf | Variante (Via-Kosten / F / B) | offene Verbindungen (DRC, nach Stitching) | weitere DRC-Meldungen |
|---|---|---:|---|
| A-1 | 1 (30 / 1,3 / 1,15) | 1 (GND-Insel) | 1 lose Bahn (0,14 mm) |
| A-2 | 2 (20 / 1,3 / 1,15) | 2 (GND-Inseln) | 1 Abstand VSYS–GND (U3), 1 lose Bahn |
| **A-3** | **3 (40 / 1,3 / 1,15)** | **0** | **keine** → übernommen |
| B-3 | 3 (Wiederholung) | 4 (GND-Inseln) | 1 lose Bahn |
| B-4 | 4 (30 / 1,6 / 1,3) | **0** | **keine** (zweiter sauberer Stand, `build/main-board/keep/variant4-0-open.kicad_pcb`, nicht eingecheckt) |
| B-5 | 5 (25 / 1,1 / 1,0) | 5 (GND-Inseln) | 1 lose Bahn |
| B-6 | 6 (35 / 1,5 / 1,1) | 1 (GND-Insel) | 1 Lochabstand (zwei ISEN_ADC-Vias), 2 lose Bahnen |

**Streuung über 7 Läufe: 0–5 offene Verbindungen (Median 1), 2 von 7 Läufen ganz sauber (DRC 0, 0 offen).**
Alle offenen Verbindungen sind GND-Flächeninseln, kein Signal. Die übrigen Meldungen sind Restfehler des eigenen
Routers (kurze lose Bahnstücke nach dem Aufreißen, je ein Abstands- bzw. Lochabstandsfehler); sie kommen nur in den
nicht übernommenen Läufen vor. `route.py` wählt den besten Lauf eines Aufrufs; offiziell wird er nur, wenn er besser ist als der Stand in
`hardware/main-board/routing.json` (Keep-best-Gate, `docs/entwicklung.md`).

Gleiche Kosten ergeben nicht bitgenau dasselbe (A-3 gegen B-3): Die Reihenfolge der offenen Verbindungen kommt aus dem
KiCad-DRC und hängt von den zufälligen UUIDs neu gebauter Bahnen ab. In allen Läufen sind **alle Signalverbindungen
geroutet**; offen bleiben nur GND-Flächeninseln um 0402-Teile neben dem Modul (C13/C14 mit Modulpads 11/52, C4/R3, C12),
für deren Via in der dichten Reihe kaum Platz ist. Laufzeit je Lauf 25–60 min (3–4 Läufe parallel).

**Bekannte Schwächen (vor einer Bestellung im GUI ansehen):** Der Router legt Bahnen im 0,05-mm-Raster mit 45°-Knicken;
manche Wege machen Umwege über Vias (116 statt 73 Vias bei 2 Lagen). Elektrisch unkritisch (keine schnellen Signale
außer USB-FS, das vorgeroutet ist), optisch nicht „handgeroutet“.

*11.5 und 11.6 (Vergleich 2/4 Lagen, Entscheidung) sind entfallen: decision-history.md. Kosten 4 Lagen:
ca. +3 / +6 / +10 € pro Auftrag bei 5 / 10 / 30 Stück, Fertigung +1–3 Werktage (kostenabschaetzung.md 5.6,
unsicher). Bestellvorbereitung: Kapitel 7.*

### 11.7 Optionale Pads unten und Batterie-Motorpfad (Stand 2026-11-04)

Umsetzung von idee-optionale-hardware.md 0/0b (Datenblattprüfung dort in 0b.6, Abweichungen in decision-history.md) und Befund 8.1 aus
routing-score.md. **Entscheidung 2026-11-05:** keine RC-Footprints an S2–S4 (J6 sind reine Pads; interne Pull-ups und
1 kΩ im Kabel genügen) und kein Hardware-Lastpuls (Q2/R17/R18 entfallen, IO22 bleibt frei; Powerbank wach halten per
Firmware, idee-powerbank.md). Alles aus den Generatoren, nichts im GUI. **Oben unverändert**; unten nur Pads, Testpunkte und
**nicht bestückte Footprints (DNP)**. DNP steht im Schaltplan (`dnp`) und am Footprint; `just fab` lässt diese Teile in
Bestückungsliste und Stückliste weg (`--exclude-dnp`), die einseitige Bestückung bleibt.

**Pads und Footprints unten** (Koordinaten: Platinenmitte, Ansicht von oben; alle Teile in der Tasche |y| ≤ 5,2 mm,
höchstes Teil U6 1,45 mm):

| Ref | Belegung | Lage | Bestückung |
|---|---|---|---|
| J3 | 1 EN · 2 TXD · 3 BOOT · 4 GND · **5 RXD (IO17)** | x −13,63 … −3,47, y −3,35 (vorher −3,25) | Pads |
| J6 „Spieler“ | 1 3V3 · 2 S1 IO5 · 3 S2 IO20 · 4 S3 IO21 · 5 S4 IO8 · 6 GND, Raster **2,0 mm** | x −3,63 … −13,63, y +3,2 (unter dem Modul zur Kante +y) | Pads |
| R19 / R20 / C16 | IO5 → 3V3 10 k / → GND 1 M / → GND 10 n (N4) | mittlere Reihe des Modul-Pads, x −11,9 / −9,8 / −7,8, y 0 | DNP |
| J7 „LED“ | 1 VLED · 2 IO23 · 3 GND | x +10,74 … +5,66, y −4,2 (Seite −y, weg vom Treiber) | Pads |
| U6 | TPS22918 VSYS → VLED_SW, ON = IO15, CT und QOD offen | Mitte (2,2; 1,5), oberhalb y −0,3 | DNP |
| JP1 | Lötbrücke VSYS → VLED_SW (Standard offen, Umgehung von U6), 0603-Pads (Lot oder 0 Ω) | (6,2; 1,8) zwischen VSYS- und VBUS-Bahn unten | Brücke |
| F1 | PTC 0,5 A (0805) VLED_SW → VLED | (6,2; −1,5), VLED_SW nach Norden zu JP1, VLED nach Süden zu J7 | DNP |
| C17, R22 | 10 µF an VLED; 100 k IO15 → GND | (14,7; −2,05) unter USB-C / (−13,7; 0) | DNP |
| TP1, TP2 | VSYS, VBUS (Ø 1,0 mm); TP3/TP4 entfallen (ISEN an R1, SENSE an R5 messen) | (8,4; 2,4), (12,2; −1,4) | Pads |
| J2 | wie bisher | **y +4,3** (vorher +5,3; Pads jetzt in der Tasche) | Pads |

Bestückungsvarianten J7: NeoPixel-Kette (U6 + F1 + C17 bestücken; oder JP1 schließen und F1 bestücken), einzelne
LED oder Taster an J7-2/J7-3 ohne Bauteile. **Ohne F1 (oder 0-Ω-Brücke an seiner Stelle) ist J7-1 stromlos.**

**Batterie-Motorpfad (Befund routing-score.md 8.1):** Q1 Pin 2 (VSYS) ist jetzt vorgeroutet: oben 0,5 mm zu zwei
Vias am Rand +y, unten 0,5 mm zwischen den J2-Pads 3/4 nach Süden, zwei Vias rechts neben C2 Pin 1, oben in dessen Pad
(`preroute_battery_vsys()`). Nur Außenlagen; IPC-2221 verlangt für 1,5 A bei 20 K außen 0,35 mm. Gemessen an der
ungerouteten Platine: Pfad Q1 → VM 13,6 mm, 2 Vias, 15,5 mΩ, **31,0 mV bei 2 A** (vorher 56,2 mV, 0,2 mm, teils In2),
keine Verletzung. `route_fix.py` routet VSYS nie unter 0,3 mm (außer zu R6 und TP1), VLED/VLED_SW mit 0,4 mm.

**Stand Routing: noch nicht fertig** (Verlauf in den Tabellen, aktueller Stand am Ende). Schaltplan ERC 0,
ungeroutete Platine DRC 0, Schaltplan-Abgleich 0. Abschnitt 11.4 beschreibt noch das Design vor den Pads unten.

| Anlauf | Änderung davor | Ergebnis |
|---|---|---|
| A | erste Fassung (J6 bei y = 0) | VBAT_ADC (R6) ohne Weg: J6 Pad 1 lag unter R6, wo das Via hingehört; abgebrochen |
| B | J6 nach y −1,3, J3 −3,35 | nach dem 1. Durchlauf 37–44 offen; Grenze 300 Schritte erreicht |
| C | Vorrouten VLED_SW, VBAT-Via; 800 Schritte | TP4 (SENSE) zwischen F1/C17/USB unerreichbar; abgebrochen |
| D | TP4, R22 verlegt | 1. Durchlauf bis 50 offen; VBUS-Gate-Zweig auf In2 bildete mit der VSYS-Bahn unten zwei Wände |
| E | VBUS-Zweig zurück auf B.Cu, TP3/TP4 ans rechte Ende | ISEN_ADC-Via neben J2 von C16 blockiert; abgebrochen |
| F | RC-Reihe tiefer, QOD schmal | nach ca. 550 Schritten 45–51 offen (alle vier Versuche), 1. Durchlauf 40 offen; nach 1 h abgebrochen |

Danach noch QOD von U6 offen gelassen (eine Verbindung weniger); nicht mehr geroutet.

**Fortsetzung 2026-11-05/06 (nach der Entscheidung, Log je Runde):**

| Runde | Änderung davor | Ergebnis |
|---|---|---|
| G | RC-Footprints S2–S4 und Lastpuls entfernt; R19/R20/C16 unter das Modul zur Kante +y (y 3,6) | route_fix, 4 Versuche: nach dem 1. Durchlauf 3 / 3 / 6 / 25 offen; offen blieben LED (U1.19–R9), SENSE (R5–U1.6, R5–TP4), ISEN_ADC (R8), EN, VSYS-Stich an R6. Durch Sitzungsende abgebrochen, nichts übernommen |
| H | J6 im 2,0-mm-Raster (`SolderPads_1x06_P2.00mm`) bei y = 0, x −13,63 … −3,63: J6 Pad 1/2 lagen bei y −1,3 genau unter der 0402-Reihe und den rechten Modulpads, wo der Router seine Vias braucht. GND-Vias im Modul-Pad 7 → 5 | `ROUTER=freerouting`, 3 Versuche (30 min): Freerouting meldet 0 offen, nach Import und route_fix bleiben 19 offen, 5 DRC-Fehler (bester Versuch 2). Weil das Design geändert ist, hat das Gate ihn als neue Basis übernommen (S 170,2, hart 21) |
| (I) | – | versehentlich von der gerouteten Platine aus gestartet (ohne `just pcb`); route_fix ergänzte nur, 16 offen, DRC 5; das Gate übernahm das als kleinere Verletzung (hart 18 statt 21, S 161,5) |
| J | `just pcb` (gleiches Design) | eigener Router, 4 Versuche, nach 40 min abgebrochen: J6 bei y = 0 liegt unter den rechten Modulpads 17–19, deren Fluchtwege nach innen Vias brauchen; LED (U1.19–R9) und ISEN_ADC ohne Weg |
| K | J6 nach y +3,2 (unter dem Modul zur Kante +y, Pads 2,5 … 3,9), R19/R20/C16 und R22 in die mittlere Reihe des Modul-Pads (y 0) | eigener Router, 4 Versuche; nach 47 min starb ein Arbeitsprozess (Speicher), der Aufruf brach ohne Gate ab. Bester Zwischenstand (Versuch 3, 1. Durchlauf 5 offene Signale) von Hand wie `route.py` nachbearbeitet (Stitching, GND-Inseln) und mit `route_gate.py check --apply` durchs Gate: **übernommen**, 14 offen (davon 9 GND-Flächenstücke), 2 DRC-Fehler, hart 16, S 169,8 |

**Stand nach Runde K (überholt durch Runde L, siehe unten):** offizielle Platine war Runde K, `routing.json` passt dazu
(Fingerabdruck 86f5c8e336). Harte Bedingungen: `unconnected` 14, `drc_errors` 2; `antenna_intrusions` 0,
`power_width_violations` 0 (Q1 → VM 0,5 mm außen). Offen:
- Signale: +3V3 an R16, EN (U1.8 und J3.1 zur EN-Bahn), ISEN (R1–U2.8), ISEN_ADC (R8); dazu 9 GND-Flächenstücke ohne
  Via (C8/C10–C14, C16, D1, R15, R20, U4, U6).
- DRC: 2 × Lochabstand zwischen einem SENSE-Via (Weg zu TP4 am rechten Ende) und der USB-C-Lasche S1.

**Vorschlag (Entscheidung Auftraggeber):**
1. TP3/TP4 entfernen (ISEN an R1, SENSE an R5 sind von oben messbar) – beseitigt die beiden DRC-Fehler und zwei lange
   Wege quer über die Platine.
2. J7-Gruppe weg vom Treiber: J7 liegt bei y −3,3 genau unter U2/R1/R8, wo ISEN/ISEN_ADC und die GND-Inseln ihre Vias
   brauchen. Entweder U6/JP1/F1/C17 ganz streichen (J7 nur Pads: IO23, GND, VSYS über Lötbrücke) oder J7 samt Gruppe
   unter USB-C −y (frei seit Q2/R18 entfallen sind; Platz prüfen).
3. Danach eine Runde mit 4 Versuchen; erst wenn dann noch etwas offen ist, `route_fix.py` erweitern (Start an
   Vorrouten-Vias auf allen Lagen, Vias unter Bauteilkörpern) – der VBAT_ADC-Stich zeigt das Problem.

| Runde | Änderung davor | Ergebnis |
|---|---|---|
| L | Entscheidung 2026-11-06: TP3/TP4 entfernt; J7 nach (8,2; −4,2) auf die Seite −y, C17 unter USB-C. Die ganze Gruppe passt unter USB-C nicht (U6 allein ja, dann kein Platz mehr für F1/JP1; Suche mit Abstandsprüfung): U6, F1, R22 in die Mitte oberhalb y −0,3, JP1 als 0603-Pads neben die VSYS-Vias; der Bereich unter Treiber/R1/R8 und rechts vom Modul bleibt frei. VLED-Vorroute entfällt. Hülle: Radius 6,94 mm, unten |y| ≤ 4,9 (Pads), Höhe U6 1,45 mm (Modell 1,64) | eigener Router, 4 Versuche ab `just pcb` (2 h): nach Stitching 12 / 29 / 12 / 19 offen; Versuch 3 vom Gate **übernommen** (Design geändert): 12 offen = 3 Signale + 9 GND-Flächenstücke, **0 DRC-Fehler**, hart 12, S 166,0. Versuch 1 hatte S 143,3, aber 2 DRC-Fehler |

**Stand 2026-11-06 nach Runde L:** offizielle Platine = Runde L, Versuch 3; `routing.json` passt (Fingerabdruck
7e41ca5b46). ERC 0, Schaltplan-Abgleich 0, DRC-Fehler 0 (Warnungen: Lochabstand zweier VLED-Vias, ein loses
VBAT_ADC-Via), `antenna_intrusions` 0, `power_width_violations` 0. Offen (`unconnected` 12):
- Signale: ISEN_ADC an R8 (zur vorgerouteten Bahn), LED (U1.19–R9), VLED_SW an F1.
- 9 GND-Flächenstücke ohne Via (F.Cu/B.Cu).

**Vorschlag `route_fix.py` (am 2026-11-06 freigegeben und umgesetzt, siehe Runde M):** Die drei offenen Signale liegen alle an
einem Bahnende bzw. Pad, das der Router nur auf seiner eigenen Lage anfährt (ISEN_ADC, VLED_SW) oder in der dichten
0402-Reihe rechts vom Modul (LED). Erweiterung:
1. Start und Ziel an Vorrouten-Vias und an Bahnenden auf allen Lagen erlauben (Via am Ende einer Vorroute = Anschluss
   auf F.Cu, In2 und B.Cu); das betrifft auch das VBAT_ADC-Via, das heute lose bleibt.
2. Vias unter Bauteilkörpern unten zulassen (zwischen den Pads, z. B. unter U6, C17), wenn der Abstand zu den Pads
   reicht.
3. GND-Inseln: Via auch in der Fläche neben dem Pad statt nur am Pad suchen (Stitching-Raster feiner).
Danach eine Runde mit 4 Versuchen.

**Umsetzung in `route_fix.py`** (Optionen oben in der Datei, je abschaltbar):
- `ENDPOINT_VIAS = True`: Ein Via desselben Netzes am Anschluss (Bahnende oder Pad, auch gesperrte Vorrouten-Vias)
  gilt als Start/Ziel auf F.Cu, In2 und B.Cu.
- `VIA_UNDER_BODIES = "bottom"`: Vias zwischen den Pads unter Bauteilkörpern sind erlaubt (war schon so, jetzt
  benannt und geprüft); `"none"` sperrt die Courtyards. Via-in-Pad und Antennen-Sperrflächen bleiben gesperrt.
- `ISLAND_AREA_SEARCH = True`: Für eine GND-Insel ohne Via sucht der Router die Via-Stelle in der ganzen Füllfläche
  der Insel, wenn es vom Pad aus nicht geht.
- Schnellprüfung `just route-check` (`test_route_fix.py`, ca. 30 s) an der Platine aus Runde L:
  - Der VBAT_ADC-Stich startet jetzt auf allen drei Lagen (vorher nur F.Cu).
  - 85 zulässige Via-Stellen unter U6, keine in fremden SMD-Pads oder in der Antennen-Sperrfläche.
  - Offene Signale: ohne Aufreißen 0 von 3, mit Aufreißen 2 von 3 (ISEN_ADC, LED); VLED_SW an F1 blieb ohne Weg.
    Ursache: F1 lag zwischen VSYS- und VBUS-Bahn unten eingeschlossen.
  - GND-Inseln: ohne Flächensuche 1 von 10 angebunden, mit Flächensuche 2 von 10.
- Deshalb F1 nach (6,2; −1,5), VLED_SW nach Norden zu JP1 (jetzt (6,2; 1,8)), VLED nach Süden zu J7. R22 zurück
  nach (−13,7; 0). Probe auf der ungerouteten Platine: VLED_SW, VLED, VSYS, IO15 allein geroutet, 0 offen.

| Runde | Änderung davor | Ergebnis |
|---|---|---|
| M | Router-Erweiterungen, F1/JP1/R22 wie oben, `just pcb` | läuft seit 20:49: eigener Router, 4 Versuche; nach dem 1. Durchlauf 12 / ? / **1** / 14 offen (Signale) |



Hauptgrund: Unter dem Modul und rechts daneben (x −14 … 0) lagen bisher nur J3 und die Vias, über die der Router die
Modulpads nach unten führt. Jetzt liegen dort J6, R17, acht RC-Footprints und J2-Nähe; dazu teilt die
0,5-mm-VSYS-Bahn die Unterseite von Nord nach Süd. Vorschläge (Entscheidung des Auftraggebers):
1. Unten weniger Footprints im Bereich des Moduls: Pull-ups R23/R24 weglassen (interne 45 k reichen laut 0b.2),
   RC-Footprints nur für IO5 (N4), C18–C20 entfallen oder ans Kabelende.
2. `route_fix.py` verbessern: Via-Plätze unter Bauteilkörpern (z. B. R17) nutzen, Bahnenden an Vorrouten-Vias auf allen
   Lagen als Start erlauben (der VBAT_ADC-Stich endet an einem Via, der Router startet nur auf F.Cu).
3. Freerouting als Vorstufe (`ROUTER=freerouting`) für diese Fassung probieren.
4. Teile unten an anderer Stelle in einer zweiten Fassung (z. B. R17/Q2 als 2 × 1206 neben USB-C; der Lastpuls ist inzwischen entfallen, siehe decision-history.md).

**Hüllkurve (`just modell`, `just hull`, alle Teile unten mit 3D-Modell):** größter Radius 6,94 mm (J4, unverändert)
< 7,25 mm; unten größtes |y| 4,80 mm (Tasche 5,2), Endkappen frei. Größte Bauhöhe unten 1,64 mm laut dem generischen
KiCad-Modell SOT-23-6 von U6; das TPS22918-DBV-Gehäuse ist laut TI höchstens 1,45 mm hoch. Die Tasche ist 2,0 mm tief,
es bleiben also 0,55 mm (Modell: 0,36 mm) statt der geplanten 0,5 mm Luft; `just hull` meldet mit dem Modell eine
Überschreitung der 1,5-mm-Grenze.

**DNP in den Fertigungsdaten (geprüft):** Bestückungsliste mit `--exclude-dnp` nur 36 Teile, alle oben; Stückliste
ohne U6, F1, C17, R22, Q2, R17, R18, R19/R20/R23/R24, C16/C18–C20; `…-stueckliste-alle.csv` führt sie als
„Nicht bestücken“.

**Weitere Generatoränderungen:**
- Netzklassen: `setup_rules()` löscht alle Muster und Klassen aus der `.kicad_pro` und setzt sie neu (Power: VSYS,
  BAT_IN, VBUS_J4, OUT_A, OUT_B, VLED, VLED_SW; Supply: +3V3, GND). Die alten Einträge (MOT_A/MOT_B, ISEN in Power,
  GND und VSYS doppelt) sind weg.
- Der OUT_A-Stich zu R3/R5 läuft auf In2 statt B.Cu (Platz für J7). Der VBUS-Zweig zum Gate von Q1 bleibt unten,
  jetzt bei x = 7,25 rechts an JP1 vorbei, Vias bei (8,3; −2,5) und (7,5; 3,2). Auf In2 bildete er mit der VSYS-Bahn
  unten zwei parallele Wände, der Router kam kaum noch von West nach Ost (37–50 offene Verbindungen).
- GND-Vias im Modul-Pad: wo unten ein Pad liegt (J6, R17), rückt das Via bis 1 mm zur Seite oder entfällt: 7 statt 9.
- Zusätzliche Vorrouten für den Router: VLED_SW (U6 Pin 6 → JP1 und F1) mit 0,4 mm auf B.Cu unter den VSYS-Vias
  hindurch (`preroute_vled()`), VBAT_ADC-Via links neben R6 (`preroute_vbat_escape()`). `route_fix.py` darf je
  Durchlauf 800 statt 300 Schritte machen (`MAX_ROUNDS`); mit den Teilen unten reichten 300 nicht mehr (37–44 offen).
- Unten rechts neben dem Modul (x −5 … 0) braucht der Router Platz für die Vias der Modulpads. TP3/TP4 und R22
  lagen dort zuerst (bzw. TP4 eingeschlossen zwischen F1, C17 und den USB-Bahnen) und blockierten ihn; jetzt TP3/TP4
  am rechten Ende, R22 links neben R17, die RC-Reihe rechts von R17 auf y 1,6 und C16 tiefer, damit neben J2 Pad 1
  das ISEN_ADC-Via (C14) wieder Platz hat.
- Erster Versuch mit J6 bei y = 0: J6 Pad 1 lag unter R6 (oben) genau dort, wo VBAT_ADC sein Via braucht; der Router
  fand für R6–R7 keinen Weg mehr. Deshalb J6 nach y −1,3 und J3 0,1 mm nach außen.
- Neue Footprints in `louie.pretty` (aus `gen_symbols.py`): `SolderPads_1x03/1x06_P2.54mm`, `TestPad_D1.0mm`.
- `just hull` (`hull_check.py`): Hüllkurve aus dem STL (Radius, Tasche, Endkappen).

---

## Quellen

- Footprints: `/usr/share/kicad/footprints/RF_Module.pretty/ESP32-C6-MINI-1.kicad_mod`, Symbol `/usr/share/kicad/symbols/RF_Module.kicad_sym`, Platine `hardware/main-board/louie-main.kicad_pcb` (pcbnew), alle geprüft
- LCSC-Produkt-API und JLC-Teilesuche (Preise, Lager, 2026-11-02): [C5736265](https://www.lcsc.com/product-detail/C5736265.html), [C42403058](https://www.lcsc.com/product-detail/C42403058.html), [C22407186](https://jlcpcb.com/partdetail/C22407186)
- Mouser ESP32-C6-MINI-1-H8 (Suchtreffer, Lager/Preis unsicher): <https://www.mouser.de/c/?q=ESP32-C6-MINI-1-H8>
- [ESP32-C6-MINI-1/1U Datenblatt](https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html)
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) (Fertigungsregeln, 11.2, abgerufen 2026-11-03)
- Lagenaufbau JLC04081H-3313: [Hive-RSI-Lab/hive-hwde PR 533](https://github.com/Hive-RSI-Lab/hive-hwde/pull/533/files) (aus der Vorlage des JLC-Impedanzrechners, 2026-11-01, unsicher); [JLC Impedanzrechner/Stackups](https://jlcpcb.com/impedance) (Werte nur per JavaScript, nicht gelesen)
- Freerouting 2.5.0 (`tools/freerouting.jar`, Build 2026-10-05): Log-Meldung „declared as a power layer but no plane is defined … treated as a signal layer“ (Kapitel 11.4)
- [ST USBLC6-2 Datenblatt DS4260](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) (Rev 5, Fig. 1/7/18, 2.4)
- [TI DRV8213 Datenblatt SLVSGV9](https://www.ti.com/lit/gpn/drv8213) (Pinbelegung DSG, IPROPI, VREF 510 mV, Autosleep, RθJA)
- [ESP-IDF RF Coexistence ESP32-C6](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html) (IDF v6.1)
- [esp-zigbee-sdk](https://github.com/espressif/esp-zigbee-sdk)
