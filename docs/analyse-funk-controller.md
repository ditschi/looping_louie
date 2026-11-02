# Analyse: Funk (WLAN + BLE), Antennen-Layout und Controller-Alternativen

Stand: 2026-11-02 · Anlass: BTHome-BLE-Taster (passiv scannen, z. B. Shelly BLU) sind V1-Feature, zusätzlich
zum WLAN (STA oder eigener Hotspot mit bis zu 8 Handys). Bezug: [hardware-konzept.md](hardware-konzept.md),
[idee-funk-taster.md](idee-funk-taster.md), [firmware-sprache.md](firmware-sprache.md).

**Kurzfassung**

- **Eine Antenne für WLAN + BLE ist kein Problem**, sondern so vorgesehen: Der ESP32-C3 hat **ein** Funkteil mit
  **einem** HF-Pfad, WLAN und BLE wechseln sich im Zeitmultiplex ab. Eine zweite Antenne bringt keine Trennung.
- **Begrenzend sind Funkzeit und Koexistenz** (BLE-Scan + SoftAP mit Clients = „C1, instabil“), nicht die Antenne.
- **Layout: zwei Änderungen** (GND-Streifen oben unter der Antenne entfernen; Antennen-Ende festlegen und testen).
  Der Rest ist im AA-Format nicht besser machbar und wird per RSSI-Test abgesichert.
- **Controller: bleiben beim C3-MINI-1**, den **ESP32-C6-MINI-1 als vorbereiteten Plan B** halten (gleiche
  Maße und gleiches Pad-Raster, +133 KB freier Heap mit WLAN+BLE, ca. +1 USD pro Board, aber Pins neu belegen).
- **Nachtrag 3b:** Der C6 bringt auch **8 freie GPIOs statt 0**, ADC bis 3,3 V und Deep-Sleep-Wecken durch den
  Sensor. Unter „Reserve/Zukunftssicherheit“ lautet die Empfehlung daher: **jetzt auf den C6 wechseln** (nach
  XIAO-C6-Test). Achtung: MicroPython passt bei 4 MB auf keinem der beiden Chips in die Standard-OTA-Tabelle.

---

## 1. Gemeinsame Antenne für WLAN und BLE

### 1.1 Ein Funkteil, Zeitmultiplex

| Aussage | Status |
|---|---|
| Jeder Chip hat **nur einen HF-Pfad**, WLAN und BLE können nicht gleichzeitig senden/empfangen; Umschaltung per Zeitmultiplex | (geprüft) [IDF Coexistence C3][idf-coex] |
| Bei „WLAN verbunden“ bekommen WLAN und BLE je Periode z. B. **50 %** | (geprüft) [IDF Coexistence C3][idf-coex] |
| BLE-Scan + **STA verbunden** = Y (stabil); BLE-Scan + **SoftAP verbunden** = **C1** (unterstützt, instabil); gilt gleich für C6 | (geprüft) [C3][idf-coex], [C6][idf-coex-c6] |
| Modul hat **einen** Antennenanschluss (MINI-1: PCB-Antenne, MINI-1U: U.FL) | (geprüft) [C3-MINI-1 Datenblatt][c3-mini-ds] |

**Zwei Antennen (WLAN auf der einen, BLE auf der anderen)?** Nein. Es gibt nur einen HF-Port. Mit einem externen
HF-Schalter kann die IDF zwar zwischen zwei Antennen umschalten (Antennen-Diversität). Das ändert aber nur, *welche*
Antenne der eine Funkteil gerade nutzt. Gleichzeitiger Betrieb wird dadurch nicht möglich (unsicher, Diversity-API
nicht im Detail geprüft). Eine zweite Antenne bringt also **keine Kapazität**, höchstens Empfangsgewinn bei schlechter
Lage. Dafür reicht ein besserer Platz für die eine Antenne.

### 1.2 Was wirklich begrenzt

| Faktor | Einschätzung |
|---|---|
| **Funkzeit WLAN** | 8 Handys × 10 Zustände/s ≈ 80 kleine Frames/s, je ca. 0,1–0,3 ms inkl. ACK → **ca. 2–3 % Funkzeit** (unsicher, Rechnung). Dazu Hintergrundverkehr der Handys. Kein Engpass. |
| **BLE-Anteil** | Solange BLE scannt, verzögern sich WLAN-Pakete um einige 10 ms (unsicher). Für Joker-Taster unkritisch. |
| **Koexistenz-Modus** | SoftAP + Clients + BLE-Scan = C1. **Größtes Risiko**, nur messbar (Stufe 0 in idee-funk-taster.md). |
| `esp_coex_preference_set` | **Veraltet**, Ersatz `esp_coex_status_bit_set/clear` (nur für Sonderfälle wie BLE-Mesh). Aus MicroPython ohnehin nicht erreichbar. (geprüft) [Sysprogs/IDF][coex-pref] |
| **Beacon-Intervall SoftAP** | Standard 100 ms beibehalten. Die Koexistenz-Periode richtet sich nach dem Beacon (geprüft, [idf-coex]); längere Intervalle verschlechtern die Handy-Verbindung. Espressif rät, bei Koexistenz die Standardwerte zu lassen. |
| **WLAN-Energiesparen** | Bei aktivem BT verlangt die IDF Modem-Sleep (kein `WIFI_PS_NONE`) (unsicher). Konflikt mit „ESP-NOW braucht PS aus“ beim Prototyp prüfen. |

### 1.3 Empfohlene Scan-Parameter (MicroPython `bluetooth`/aioble)

| Parameter | Wert | Begründung |
|---|---|---|
| Typ | **passiv** (`active=False`) | BTHome steht komplett im Advertising, kein Scan-Request nötig → weniger Funkzeit |
| Intervall / Fenster | **100 ms / 30–50 ms** (Duty 30–50 %) | Shelly sendet nach jedem Druck 1 s lang (geprüft, idee-funk-taster.md) → ≥ 3 Fenster pro Druck. Der MicroPython-Standard (1,28 s / 11,25 ms) ist zu träge. |
| Dauer | `gap_scan(0, …)` = Dauerscan, **nur in BEREIT/LÄUFT** und nur bei angelernten Tastern | Außerhalb: BLE aus, volle Funkzeit fürs WLAN |
| Filter | im IRQ sofort auf Service-UUID `0xFCD2` und bekannte MAC prüfen, Packet-ID-Dubletten verwerfen | wenig Python-Objekte, wenig GC |
| PHY | 1M, **kein Coded PHY** | Coded-PHY-Pakete belegen das Funkteil lange (geprüft, [idf-coex]) |

Fenster = Intervall (100 % Duty) ist erlaubt, der Koexistenz-Scheduler kürzt ohnehin. Der Test soll 30 % und 100 %
vergleichen (verpasste Drücke vs. WebSocket-Latenz).

---

## 2. Layout-Prüfung Funk (aktueller Stand)

### 2.1 Vorgaben Espressif (MINI-Module mit PCB-Antenne)

| Vorgabe | Status |
|---|---|
| PCB-Antenne **außerhalb** der Grundplatine, Einspeisepunkt nahe am Rand; sonst Grundplatine unter und neben der Antenne ausschneiden | (geprüft) [HW Design Guidelines C3][hdg-c3] |
| **≥ 15 mm Abstand in alle Richtungen** zu Metall im Gehäuse | (geprüft) [hdg-c3] |
| Kein Kupfer unter der Antenne auf **allen Lagen**; Modul **nicht mittig** mit Ausschnitten | (geprüft) [hdg-c3], [c3-mini-ds] |
| Viel Masse und **dichte GND-Vias** am Modul nahe der Antenne | (geprüft) [hdg-c3] |
| Gehäuse beeinflusst die Antenne → Endprodukt messen | (geprüft) [hdg-c3] |

Im AA-Format sind „Antenne über den Rand hinaus“ und „15 mm frei“ **nicht erfüllbar**: An beiden Enden sitzt ein
Batteriekontakt. Ziel ist daher: alles Vermeidbare vermeiden und das Unvermeidbare messen.

### 2.2 Befunde

Koordinaten in mm relativ zur Platinenmitte, Antenne bei −x (aus `louie-main.kicad_pcb`, gelesen mit pcbnew).

| # | Befund | Bewertung | Fundstelle |
|---|---|---|---|
| L1 | Modul am Platinenende, Antennenkante bei x = −19,84. Freihaltezone oben und unten von −19,84 bis −14,6 (5,2 mm) mit Verbot für Kupferfläche, Vias und Leiterbahnen; unten zusätzlich für Bauteile | **OK** | `gen_main_pcb.py` `antenna_keepout()` (Z. 133–175), `placement_einseitig.py` Z. 17 |
| L2 | **GND-Fläche oben reicht in die Antennenzone**: Streifen ca. 5,5 × 0,9 mm (y = 5,55…6,45) direkt unter der Antenne, weil die Sperrfläche den 1,2-mm-Randstreifen `ANTENNA_TRACK_STRIP` ausspart (gedacht nur für die Leiterbahn unten) | **Ändern** | `gen_main_pcb.py` Z. 37–38 und 144; sichtbar in `docs/bilder/kupfer-oben.png` unten links |
| L3 | Leiterbahn **OUT_A** (0,4 mm, Motor-PWM) unten im Randstreifen unter der Antenne (y = 6,15, x = −21,4…−14,0) zum Endkontakt BT1 | **Risiko**, nicht vermeidbar (der Endkontakt muss angeschlossen werden). Am Rand und dünn ist schon die beste Lage. | `route.py`/Board, `kupfer-unten.png` |
| L4 | Platinenende vor der Antenne 3,16 mm (−23…−19,84): keine Fläche, keine Vias, aber **Pad BT1 (2 × 2 mm) bei x = −21,4** plus **Nickelband** um die Kante. Das Metall sitzt 1,5–3 mm vor dem Antennenende, dahinter Plus-Blech oder Feder des Fachs. | **Risiko** (Hauptrisiko, prinzipbedingt) | `gen_main_pcb.py` Z. 168–174, `placement_einseitig.py` Z. 65, `hardware-konzept.md` 6.1 |
| L5 | 6 GND-Vias in der Pad-Reihe direkt vor der Antennenzone (x = −14,03), GND-Flächen oben und unten über die ganze Platine | **OK** | `module_ground_vias()` Z. 256 |
| L6 | FR4 unter der Antenne (0,8 mm) und 3 mm vor der Antenne nicht ausgeschnitten | **OK/akzeptiert** (Ausschnitt bräche die Endkontakt-Mechanik). Leichte Verstimmung (unsicher) | `board_outline.py` |
| L7 | Massefläche ca. 26 × 13,5 mm hinter der Antenne, etwa λ/4 lang | **OK** für eine Inverted-F-Antenne (unsicher, Faustregel) | – |
| L8 | Einbau: Platine liegt in der **offenen Druck-Schale**, beim alten Louie in der C-Hülse aus Kunststoff | **OK**, solange **kein Carbon-/Metall-Filament** verwendet wird (leitfähig, verstimmt). In `mechanik/README.md` vermerken. | `huelle.scad` |
| L9 | Motor/Getriebe in der Spielmitte, Batteriefach unter der Bodenplatte. Kunststoff ist unkritisch, Motor und Leitungen sind kleine Metallteile im Abstand von einigen cm | **Risiko gering** (unsicher), Messung | – |

### 2.3 Konkrete Änderungen

1. **L2 beheben** (Generator, vom Auftraggeber umzusetzen): In `antenna_keepout()` eine zusätzliche Regelfläche
   über den Randstreifen `y1…+W/2` legen, mit **Kupferfläche und Vias verboten, Leiterbahnen erlaubt**, auf allen
   Lagen. Damit bleibt die OUT_A-Bahn möglich, der GND-Streifen oben verschwindet.
2. **Antennen-Ende festlegen**: Die Einbaurichtung ist elektrisch egal (Software-Kalibrierung). Funktechnisch ist
   das **flache Plus-Blech** wahrscheinlich günstiger als die **Minus-Feder**: Die Feder ist eine Metallspirale mit
   einigen mm Länge, also ein möglicher Parasitärstrahler (unsicher). Im RSSI-Test (Hardware-Konzept 8, erster
   Punkt) **beide Richtungen** messen und das Ergebnis auf Kappe und Schale markieren (Pfeil „Antenne“).
3. Optional: BT1 so klein wie mechanisch möglich (z. B. 1,5 × 2 mm) und das Nickelband nur so lang wie nötig.
4. Nach Änderung: Fill prüfen, dass oben und unten zwischen x = −23 und −14,6 nur BT1 und OUT_A liegen.

### 2.4 Zusätzliche Antenne?

| Variante | Bewertung |
|---|---|
| Zweite **PCB-Leiterbahnantenne** unten | **Nein.** Das Modul hat schon eine abgestimmte Antenne und nur einen HF-Port. Eine Bahnantenne bräuchte MINI-1U oder Chip-Design, Matching-Netz (π-Glied), Abstimmung mit VNA und eine Freifläche von ca. 15 × 5 mm. Die gibt es nicht. |
| **C3-MINI-1U** (13,2 × 12,5 mm, U.FL) + FPC-Antenne | **Plan B, falls der RSSI-Test schlecht ausfällt.** Vorteil: Modul 4,1 mm kürzer (Platz für Bauteile), Antenne kann **aus dem Fach** heraus (z. B. FPC unter der Bodenplatte, mit dem Kabel durch den Deckelspalt). Kosten: Modul ca. gleich (unsicher), U.FL ca. 0,1–0,3 USD, FPC-Antenne mit 50–100 mm Kabel ca. 1–3 USD (unsicher). Nachteile: Handmontage, Stecker kann abfallen, ein Teil mehr beim Verschenken. U.FL-Höhe ca. 1,2 mm passt. |
| Mini-Chipantenne am Kabel im Fach | **Nein**, liegt am selben schlechten Ort wie die Modulantenne. |

---

## 3. Controller-Alternativen mit mehr RAM

Platinenbreite 13,5 mm, AA-Hülle Ø 14,5 mm (`board_outline.py`). **Module mit 15,4 mm Breite passen nicht.**

### 3.1 Vergleich

| Modul | Maße (mm) | SRAM / PSRAM | Funk | MicroPython (v1.29, Nov. 2026) | Freier Heap IDF, WLAN+BLE-Beispiel¹ | Preis LCSC 1 / 10 Stk. (USD) | Mehrkosten vs. C3 |
|---|---|---|---|---|---|---|---|
| **ESP32-C3-MINI-1-N4** (Ist) | 13,2 × 16,6 × 2,4 | 400 KB / – | WLAN 4, BLE 5 | ja, `ESP32_GENERIC_C3` | 126 KB (178 KB bleprph_wifi_coex) | 3,07 / 2,70 | – |
| **ESP32-C6-MINI-1-N4** | 13,2 × 16,6 × 2,4 | **512 KB** / – | WLAN 6 2,4 GHz, BLE 5.3, 802.15.4 | ja seit v1.24, `ESP32_GENERIC_C6` | **259 KB** | 4,14 / 3,63 | **+1,07 / +0,93** |
| ESP32-C5-MINI-1-N8R2 | **15,4 × 21,3** (1U: 15,4 × 15,4) | 384 KB / 2 MB | WLAN 6 **2,4 + 5 GHz**, BLE 5, 802.15.4 | ja seit v1.27, PSRAM seit v1.29 | 192 KB (ohne PSRAM-Nutzung) | nicht gefunden (unsicher, ca. 4–5) | ca. +1,5–2 (unsicher) |
| ESP32-C61-MINI-1-N8R8 | 13,2 × 16,6 × 2,4 | 320 KB / **8 MB** | WLAN 6 2,4 GHz, BLE 5.3 | **nein** (kein Board) | 80 KB (ohne PSRAM) | N4 bei Mouser ca. 3,39 € (unsicher) | ca. +0,5–1 (unsicher) |
| ESP32-S3-MINI-1-N4R2 | **15,4 × 20,5** | 512 KB / 2 MB | WLAN 4, BLE 5 | ja, `ESP32_GENERIC_S3` (SPIRAM) | 189 KB (ohne PSRAM) | 5,04 / 4,53, **kein Lager** | +2,0 / +1,8 |
| C3 + externes PSRAM | – | – | – | – | – | – | **geht nicht** |

¹ Espressif ESP-Techpedia, IDF 5.5, unoptimierte Beispiele („provision“ = BLE+WLAN-Koexistenz) (geprüft) [Techpedia][techpedia].
Hinweis: firmware-sprache.md nennt 205 KB für C3 „WLAN+BLE“; laut derselben Seite gehört dieser Wert zum
reinen BLE-Beispiel `bleprph`. WLAN+BLE liegt bei 126 KB (provision) bzw. 178 KB (bleprph_wifi_coex).

Quellen Maße/Speicher: [C3-MINI-1][c3-mini-ds], [C6-MINI-1][c6-mini-ds], [C5-MINI-1][c5-mini-ds],
[C61-MINI-1][c61-mini-ds], [S3-MINI-1][s3-mini-ds] (alle geprüft). Preise: LCSC-Produkt-API am 2026-11-02
(geprüft für C3, C6, S3). Hinweis: kostenabschaetzung.md rechnet mit 1,29 USD (JLC) für den C3; die Differenz
**C6 − C3 von ca. +1 USD** gilt bei beiden Quellen ähnlich (unsicher).

**Ausschlüsse:**

- **C5 und S3**: 15,4 mm breit > 14,5 mm AA-Hülle → passt nicht. Ein Chip-Design (C5-QFN + eigene Antenne) wäre
  HF-Entwicklung mit Matching und Zertifizierungsfragen → nicht sinnvoll.
- **C61**: passt mechanisch und hat 8 MB PSRAM. Aber **kein MicroPython-Port** (geprüft: Download-Seite listet C3,
  C5, C6, S3). Weniger internes SRAM als der C3. ADC nur an GPIO1/3/4/5, USB an GPIO12/13 → Pins neu belegen.
  Nur interessant für Plan B C++.
- **C3 + PSRAM**: Der ESP32-C3 hat keine PSRAM-Unterstützung (nur externes Flash); im MINI-1 sind die SPI-Pins
  zudem intern belegt (geprüft) [Atomic14 C3][atomic-c3], [IDF External RAM][idf-extram] (C3 nicht gelistet).

### 3.2 ESP32-C6-MINI-1 als „pin-naher Drop-in“?

Gleiche Maße, **53 Pads im selben Raster**. Die Antenne liegt am selben Ende, Freihaltezone und Platzierung bleiben
gleich (unsicher: Footprint-Zeichnungen Pad für Pad vergleichen). **Die Pad-Belegung unterscheidet sich aber**
(geprüft, Pin-Tabellen [C3][c3-mini-ds] und [C6][c6-mini-ds]):

| Pad | C3 (Netz heute) | C6 | Folge |
|---|---|---|---|
| 5, 6, 8, 12, 13, 22, 23, 30, 31 | IO2 SCL, IO3 SENSE, EN, IO0 VBAT_ADC, IO1 ISEN_ADC, IO8 SDA, IO9 BOOT, RXD, TXD | gleich | **bleibt** |
| 16 | IO10 LED | IO7 | Netz tauschen |
| 17, 18 | NC, IO4 MOT_IN1 | **IO12 USB_D−, IO13 USB_D+** | USB muss hierher |
| 19, 20, 21 | IO5, IO6, IO7 (Motor) | IO14, IO15, NC | neu belegen |
| 26, 27 | IO18/IO19 USB | IO20, IO21 | frei für Motor/LED |
| 9, 10, 15 | NC | IO4, IO5, IO6 | neue Pins |

Vorschlag (unsicher, Routing prüfen): USB → Pad 17/18; MOT_IN1/IN2 → Pad 9/10 (IO4/IO5); nSLEEP → Pad 15 (IO6);
nFAULT → Pad 16 (IO7); LED → Pad 26 (IO20). Ohne Eingriff bleiben die Funktionen: Deep-Sleep-Wake über IO3
(C6: LP-GPIO0–7), ADC an IO0/IO1 (C6: ADC1 an GPIO0–6), IO8/IO9 als Strapping (geprüft, [c6-mini-ds]).
IO4/IO5 sind beim C6 Strapping-Pins (MTMS/MTDI, nur SDIO-Timing). Die Pulldowns im DRV8833 halten sie beim Booten
low, das ist unkritisch (unsicher). IO2 ist beim C6 kein Strapping-Pin mehr.

**Aufwand:** Schaltplan ca. 7 Netze umhängen und die Seite rechts vom Modul neu routen. Footprint, Antennenzone,
Mechanik und BOM-Zeile bleiben bis auf die Teilenummer gleich. Strom: TX-Spitze 382 mA statt ca. 350 mA, RX ähnlich
(geprüft, [c6-mini-ds]) → LDO und Puffer reichen (unsicher, AP2112K 600 mA).

### 3.3 Was bringt mehr RAM für MicroPython?

MicroPython holt den GC-Heap aus dem IDF-Heap (Start 64 KB, wächst in Blöcken). Der Rest bleibt für lwIP, WLAN-Puffer
und NimBLE. Beim C6 bleiben mit WLAN+BLE **ca. +130 KB** mehr übrig als beim C3 (259 vs. 126 KB, gleiches Beispiel).
Das reicht, um **sowohl** den Python-Heap auf ca. 150–200 KB zu vergrößern **als auch** eine IDF-Reserve von
> 60 KB für 8 Sockets zu behalten (unsicher, Abschätzung). Beim C3 bleiben nach firmware-sprache.md nur ca. 70–130 KB
für beides. Das ist etwa **eine Verdopplung der Reserve** und entschärft das Hauptrisiko „ENOMEM im IDF-Heap“.
PSRAM (nur C5/S3/C61, hier nicht machbar) würde den Python-Heap komplett auslagern; das ist für dieses Projekt nicht nötig.

---

## 3b. ESP32-C6 im Detail: Vorteile, Grenzen, Pinbelegung

Stand 2026-11-02. Quellen: Datenblätter ESP32-C6 v1.5, C6-MINI-1 v1.5, ESP32-C3 v2.4, C3-MINI-1 v2.2 (PDF
gelesen), ESP-IDF-Doku, MicroPython v1.29.0 (Quellcode, ChangeLog, Issues). Ersetzt den Pin-Vorschlag aus 3.2.

### 3b.1 GPIOs und Neubelegung

| Merkmal | C3-MINI-1 | C6-MINI-1 | Status |
|---|---|---|---|
| Herausgeführte GPIOs | **15** (IO0–10, 18–21) | **22** (IO0–9, 12–23) | (geprüft) |
| Zusätzliche Pads beim C6 | – | Pad 9/10/15 (IO4/5/6), 24/25 (IO18/19), 28/29 (IO22/23) | (geprüft) |
| Strapping | IO2 (muss 1 sein), IO8, IO9 | IO8, IO9 (Bootmodus), IO4/IO5 (nur SDIO-Flanke), IO15 (JTAG-Quelle, nur mit eFuse wirksam) | (geprüft) |
| ADC | ADC1 an IO0–4, ADC2 an IO5 (unkalibriert, teils defekt) | ADC1 an **IO0–6** (7 Kanäle) | (geprüft) |
| ADC-Messbereich 11 dB | 0–2500 mV, ±35 mV | **0–3300 mV**, ±40 mV | (geprüft) |
| Deep-Sleep-Wecken per Pin | IO0–5 | LP-GPIO **IO0–7** | (geprüft) |
| Native USB | IO18/IO19 (Pad 26/27) | **IO12/IO13 (Pad 17/18)** | (geprüft) |

**Wichtig:** IO2 ist beim C6 **kein Strapping-Pin** mehr. Damit entfällt die Sorge aus idee-optionale-hardware.md,
dass ein Sensor-INT den Boot blockiert. Der größere ADC-Bereich macht den Teiler-Umbau aus idee-usb-c-hauptplatine.md
(5,5 V → max. 2,5 V) überflüssig: 470k/470k liefert 2,75 V und liegt im C6-Bereich.

**Vorschlag „C3 heute → C6 neu“** (Routing unsicher, rechte Modulseite neu legen):

| Funktion | C3 heute (Pad) | C6 neu (Pad) | Begründung |
|---|---|---|---|
| VBAT_ADC | IO0 (12) | **IO0 (12)** | ADC1_CH0, bleibt |
| ISEN_ADC | IO1 (13) | **IO1 (13)** | ADC1_CH1, bleibt |
| SENSE (Hebel, Wake) | IO3 (6) | **IO3 (6)** | LP_GPIO3, bleibt |
| LIS2DH12 INT1 | RXD = IO20 (30) | **IO2 (5)** | LP_GPIO2 → **Deep-Sleep-Wecken durch Klopfen/Bewegung**, kein Strapping mehr |
| I²C SDA | IO8 (22) | **IO6 (15)** | LP_I2C_SDA (LP-Kern kann den Sensor lesen) |
| I²C SCL | IO2 (5) | **IO7 (16)** | LP_I2C_SCL |
| MOT_IN1 / MOT_IN2 | IO4/IO5 (18/19) | **IO18/IO19 (24/25)** | keine Strapping-Pins, PWM über LEDC |
| MOT_nSLEEP | IO6 (20) | **IO20 (26)** | |
| MOT_nFAULT | IO7 (21) | **IO21 (27)** | |
| LED | IO10 (16) | **IO14 (19)** | |
| BOOT / Taster-Pad | IO9 (23) | **IO9 (23)** | bleibt |
| USB D−/D+ | IO18/19 (26/27) | **IO12/13 (17/18)** | fest im Chip |
| TXD (Konsole) | IO21 (31) | IO16 (31) | bleibt Reserve |

IO6/IO7 sind JTAG-Pins (MTCK/MTDO). Das ist unkritisch, weil JTAG über USB läuft (geprüft, Datenblatt 2.3.4).

**Frei nach Neubelegung: 8 GPIOs**, davon 5 ohne Einschränkung:

| GPIO (Pad) | Eigenschaften | Mögliche Nutzung |
|---|---|---|
| IO4 (9), IO5 (10) | ADC1_CH4/5, LP-GPIO (Deep-Sleep-Wake), Strapping nur SDIO | **VBUS-Erkennung** (Teiler), **zweiter Taster** mit Deep-Sleep-Wake |
| IO22 (28), IO23 (29) | frei | **Lastpuls-MOSFET Powerbank** (idee-powerbank.md, Lösung C), WS2812 |
| IO17 = RXD (30) | frei, da INT umgezogen | Hall-Schalter, Summer |
| IO8 (22) | Strapping (beim Download = 1), Pull-up nötig | Ausgang nach dem Boot |
| IO15 (20) | Strapping JTAG-Quelle (ohne eFuse wirkungslos) | Reserve |
| IO16 = TXD (31) | ROM-Log beim Boot | Konsole |

Zum Vergleich: Beim C3 sind alle 15 GPIOs belegt (TXD als einzige Reserve).

### 3b.2 LP-Kern und LP-Peripherie

| Aussage | Status |
|---|---|
| LP-RISC-V bis 20 MHz, 16 KB LP-SRAM, läuft im Deep Sleep weiter | (geprüft) [C6-DS] |
| LP-Kern erreicht **LP-GPIO0–7, LP-I²C (nur Master), LP-UART**; wird durch LP-Timer, LP-IO, HP-CPU, ETM, LP-UART geweckt | (geprüft) [idf-lpcore] |
| **ADC im Deep Sleep:** keine LP-ADC-API für den C6 in der IDF-Doku; Espressif-Forum: LP-ADC-Beispiel nur für P4 | (unsicher) [lp-forum] |
| MicroPython: `esp32.ULP` nur für den FSM-ULP von ESP32/S2/S3, **kein Zugriff auf den LP-Kern des C6** | (geprüft, `esp32_ulp.c` v1.29) |

Folgen: Der **Hebel** braucht den LP-Kern nicht. Das normale Wecken über LP-GPIO geht auch aus MicroPython
(`esp32.wake_on_gpio`, seit v1.27). Den **LIS2DH12 im Deep Sleep abfragen** ginge nur mit einem LP-Programm in C
(ESP-IDF-ULP) und einem eigenen MicroPython-Build. Die **Akkuspannung im Deep Sleep überwachen** geht nicht sinnvoll,
dafür kurz per Timer aufwachen.

### 3b.3 Peripherie C6 gegenüber C3

| Block | C3 | C6 | Nutzen für Louie |
|---|---|---|---|
| MCPWM | – | 1 Einheit, 3 Timer/3 Operatoren | Totzeit, synchrones Abtasten des Motorstroms. **Nicht in MicroPython** |
| PCNT | – | 4 Einheiten × 2 Kanäle | `esp32.PCNT`/`machine.Counter` auf dem C6 vorhanden (z. B. Drehzahl aus Strom-Rippel), (geprüft) |
| RMT | 2 TX + 2 RX | 4 Kanäle TX/RX | kein Unterschied für uns. MicroPython kann nur senden (geprüft) |
| LEDC | 6 | 6 | gleich |
| ADC | 12 Bit, 5 + 1 Kanäle | 12 Bit, 7 Kanäle, Schwellwert-Interrupt, 2 Filter | mehr Kanäle, größerer Bereich |
| Timer | 2 × 54 Bit + Systimer | gleich | gleich |
| Weitere | – | 2 × TWAI (CAN), SDIO-Slave, ETM, PARLIO, LP-UART, 802.15.4 | 802.15.4: MicroPython deaktiviert (`sdkconfig.c6`) |

(geprüft, [C6-DS], [C3-DS])

### 3b.4 Flash und OTA

| Punkt | Befund | Status |
|---|---|---|
| C6-MINI-1 Varianten | **N4** (4 MB, 85 °C), **H4** (4 MB, 105 °C), **H8** (8 MB, 105 °C). **N8 gibt es nicht**. MINI-1U (13,2 × 12,5 mm, U.FL) gleich. Flash im Chip (C6FH4/C6FH8) | (geprüft) [c6-mini-ds] |
| Verfügbarkeit H8 | JLC/LCSC C42403058: **0 Stück**, gelistet 12,37 USD | (geprüft 2026-11-02) |
| MicroPython v1.29.0 App-Größe | **C6 1.902.128 B (1,81 MiB)**, C3 1.689.200 B (1,61 MiB) | (geprüft, `.app-bin`) |
| OTA-Tabelle 4 MB | 2 × 0x180000 = **1,5 MiB** → **passt weder C6 noch C3** | (geprüft, `partitions-4MiB-ota.csv`) |

Mit 4 MB geht echtes OTA beim C6 nur mit eigener Tabelle (2 × 1,875 MiB) und dann nur ca. 190 KB Dateisystem, oder
mit verkleinertem Build (unsicher). Mit **H8** wären 2 × 3 MB + 2 MB Dateisystem bequem, aber H8 ist nicht lieferbar.
Der Normalweg bleibt das Datei-Update (firmware-sprache.md). Firmware-sprache.md ist hier zu korrigieren: Auch
der C3-Build liegt über 1,5 MB.

### 3b.5 Stromverbrauch (Modul- bzw. Chipdatenblatt, 3,3 V, 25 °C)

| Zustand | C3 | C6 | Status |
|---|---|---|---|
| WLAN TX 11b 1 Mbit/s, Spitze (Modul) | 350 mA | 382 mA | (geprüft) |
| WLAN RX HT20 (Modul) | 82 mA | 78 mA | (geprüft) |
| BLE TX ≈ 20 dBm / RX (Modul) | 340 / 86 mA | 309 (19 dBm) / 73 mA | (geprüft) |
| Modem-Sleep 160 MHz, CPU läuft (Takte aus/an) | 23 / 28 mA | 27 / 38 mA | (geprüft) |
| Light Sleep | 130 µA | **180 µA** (35 µA mit abgeschalteter Peripherie) | (geprüft) |
| Deep Sleep | 5 µA | 7 µA | (geprüft) |

Im Deep Sleep dominiert der LDO-Ruhestrom (ca. 55 µA), der Unterschied von 2 µA spielt keine Rolle. Im Betrieb
braucht der C6 bei laufender CPU ca. 4–10 mA mehr. Das ist gegenüber 80 mA RX und dem Motor unerheblich.
**WLAN 6 / TWT** wirkt nur im **STA-Betrieb** (geprüft, IDF-Beispiel `itwt`). Im Hotspot-Modus mit 8 Handys bringt es
nichts. Ob der C6-SoftAP 802.11ax spricht, ist für Handys ohnehin egal (unsicher).

### 3b.6 MicroPython auf dem C6

| Punkt | Befund | Status |
|---|---|---|
| Seit | **v1.24.0 (2024-10-25)**, aktuell v1.29.0 (2026-08-24) mit IDF 5.5.2 | (geprüft) |
| Boards | `ESP32_GENERIC_C6`, `SEEED_XIAO_ESP32C6` (seit v1.28), M5STACK_NANOC6, UM_TINYC6 | (geprüft) |
| BLE | NimBLE an (`sdkconfig.ble`, max. 4 Verbindungen), `bluetooth`/aioble laufen | (geprüft) |
| espnow | vorhanden. Ein Kanal-Test wird auf dem C6 übersprungen („workaround“) | (geprüft, ChangeLog v1.29) |
| Bug `lightsleep()` hängt (LP-WDT-Reset) seit v1.27 | Ursache IDF 5.5.2, behoben mit IDF 5.5.5 am 2026-08-26 **nach** v1.29 → Nightly bzw. v1.30 | (geprüft) [#19396] |
| Bug Deep-Sleep-Wake **`WAKEUP_ALL_LOW`** lässt den Pin hängen | **offen**. Betrifft SENSE (Hebel zu = low). Ausweg: auf den Gegenpegel wecken oder `wake_on_gpio` testen | (geprüft) [#17334] |
| aioble-Scan auf C6 läuft Stunden/Tage, dann `OSError -519` | offen, vermutlich Fragmentierung | (geprüft) [#18101] |
| `esp32.gpio_deep_sleep_hold` | auf dem C6 nicht vorhanden | (geprüft) [#19208] |
| Freier Heap | **keine veröffentlichten MicroPython-Zahlen für C6 gefunden**. IDF-Beispiele: STA 321 KB (C3 219), WLAN+BLE „provision“ 259 KB (C3 126) | (geprüft) [techpedia] |
| Gegenprobe C3 | MicroPython v1.27: nach `BLE.active(True)` nur noch 28 KB IDF-Heap, WLAN-STA scheitert mit „WiFi Out of Memory“. Laut Melder gleiches Bild auf dem C6, aber ohne Log | (geprüft für C3, unsicher für C6) [#18859] |

Der letzte Punkt zeigt das Hauptrisiko: Der MicroPython-GC-Heap kann dem IDF zu viel Speicher wegnehmen. Der Test
muss beide Heaps messen und notfalls den Python-Heap begrenzen. Auf dem C6 ist dafür ca. 100–130 KB mehr Platz.

### 3b.7 Preis und Verfügbarkeit (2026-11-02)

| Teil | LCSC 1/10/100 Stk. (USD) | Lager LCSC / JLC | JLC-Typ |
|---|---|---|---|
| C3-MINI-1-N4 (C2838502, NRND) | 3,07 / 2,70 / 2,14 | 20.022 / 22.187 | Extended |
| C3-MINI-1-H4X (C41349510) | JLC 3,11 / 2,73 | – / 3.544 | Extended |
| **C6-MINI-1-N4 (C5736265)** | **4,14 / 3,63 / 3,02** | 1.380 / 3.921 | Extended |
| C6-MINI-1-H4 (C6553337) | JLC 4,45 / 3,81 | – / 534 | Extended |
| C6-MINI-1U-H4 (C20627095) | JLC 4,20 / 3,76 | – / 3.938 | Extended |
| C6-MINI-1-H8 (C42403058) | JLC 12,37 | – / 0 | Extended |

(geprüft, LCSC- und JLC-Teile-API.) Beide Module sind Extended, die Bestückungsgebühr ist also gleich. Mehrkosten C6
ca. **+1,0 USD** (100 Stk. +0,88). **Testboard:** Seeed **XIAO ESP32-C6**, 5,20 USD, 4 MB, 512 KB SRAM, Deep Sleep
15 µA, eigenes MicroPython-Board (geprüft, Seeed-Shop/Wiki).

### 3b.8 Fazit Reserve und Zukunftssicherheit

Der C6 bringt mehr als RAM: **+7 GPIOs (8 frei statt 0)**, ADC bis 3,3 V, kein Strapping auf IO2, Deep-Sleep-Wecken
durch den Beschleunigungssensor, PCNT, MCPWM, LP-Kern, 802.15.4 und Wi-Fi 6. Er hat dieselben Maße und kostet ca.
1 USD mehr. Damit lösen sich drei offene Engpässe der Dokumente: VBUS-Erkennung, Lastpuls-GPIO für die Powerbank und
der Teiler-Umbau. Nachteile: Neubelegung und Routing der rechten Modulseite; das MicroPython-Binary ist 210 KB größer.
OTA mit zwei Slots geht bei 4 MB weder beim C6 noch beim C3 ohne Umbau. Dazu kommen einige offene C6-Fehler im
Sleep-Bereich. Den LP-Kern nutzt MicroPython nicht.

**Empfehlung:** Unter dem Gesichtspunkt „nicht am Limit bauen“ **jetzt auf den ESP32-C6-MINI-1-N4 wechseln**, solange
die Platine nicht bestellt ist. Mit dem C3 ist die Pinreserve schon heute null, und der RAM mit WLAN+BLE knapp. Vorher
auf einem XIAO ESP32-C6 drei Dinge prüfen: Hotspot mit 8 Handys plus aioble-Scan (beide Heaps), Deep-Sleep-Wecken
über SENSE mit dem gewählten Pegel und Light Sleep mit einem Nightly-Build (IDF 5.5.5). Fällt einer der Sleep-Tests
durch, ist das per Firmware lösbar und kein Grund, beim C3 zu bleiben.

---

## 4. Fazit

| Thema | Entscheidung |
|---|---|
| **(a) Antenne** | **Kein Handlungsbedarf** wegen WLAN + BLE: ein Funkteil, eine Antenne ist richtig. Keine zweite Antenne, keine Leiterbahnantenne. Ein Risiko bleibt die **Einbaulage** (Metall am Antennenende). Absichern per RSSI-Test mit Feder und Blech. Plan B ist MINI-1U + FPC-Antenne außerhalb des Fachs. |
| **(b) Layout** | **Ändern:** L2 (GND-Streifen oben unter der Antenne, Regelfläche für den Randstreifen). **Festlegen:** Antennen-Ende per Messung (vermutlich Plus-Blech), auf Kappe markieren. **Beibehalten:** OUT_A am Rand, BT1-Pad, GND-Vias. Keine leitfähigen Filamente. |
| **(c) Controller** | **Beim C3-MINI-1(-N4X) bleiben**, solange der Machbarkeitstest (Hotspot, 8 Handys, BLE-Scan, beide Heaps) besteht. Fällt MicroPython wegen RAM durch, ist der **ESP32-C6-MINI-1-N4 der bessere Plan als C++**: gleicher Footprint und Platz, doppelte RAM-Reserve, MicroPython-Port vorhanden, **ca. +1 USD pro Board** (LCSC 1 Stk. +1,07, 10 Stk. +0,93). Kein echter Drop-in: 7 Netze umhängen und neu routen. Den Test daher am besten gleich auf einem **C6-Board** (z. B. XIAO ESP32-C6) wiederholen, um den Unterschied zu messen. |

Empfehlung zur Abwägung: Da die Platine noch nicht bestellt ist und der Aufpreis ca. 1 USD beträgt, ist ein
**Wechsel auf den C6 schon jetzt vertretbar**, wenn der C3-Test knapp ausfällt (z. B. < 40 KB IDF-Reserve unter Last).
Nebeneffekte: 802.15.4 (Zigbee/Thread-Taster) wird möglich, und das Abkündigungsproblem C3-MINI-1-N4 → N4X entfällt.

---

## Quellen

[idf-coex]: https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-guides/coexist.html
[idf-coex-c6]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html
[coex-pref]: https://sourcevu.sysprogs.com/espressif/esp-idf/symbols/esp_coex_preference_set
[hdg-c3]: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html
[c3-mini-ds]: https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html
[c6-mini-ds]: https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html
[c5-mini-ds]: https://documentation.espressif.com/esp32-c5-mini-1_mini-1u_datasheet_en.html
[c61-mini-ds]: https://documentation.espressif.com/esp32-c61-mini-1_mini-1u_datasheet_en.html
[s3-mini-ds]: https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.html
[techpedia]: https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/ram-usage.html
[atomic-c3]: https://esp32.atomic14.com/socs/esp32-c3/
[idf-extram]: https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/external-ram.html
[C6-DS]: https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf
[C3-DS]: https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf
[idf-lpcore]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-reference/system/ulp-lp-core.html
[lp-forum]: https://esp32.com/viewtopic.php?p=135957
[#19396]: https://github.com/micropython/micropython/issues/19396
[#17334]: https://github.com/micropython/micropython/issues/17334
[#18101]: https://github.com/micropython/micropython/issues/18101
[#19208]: https://github.com/micropython/micropython/issues/19208
[#18859]: https://github.com/micropython/micropython/issues/18859

- Espressif, RF Coexistence ESP32-C3 / ESP32-C6: <https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-guides/coexist.html>, <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html>
- `esp_coex_preference_set` veraltet: <https://sourcevu.sysprogs.com/espressif/esp-idf/symbols/esp_coex_preference_set>
- Espressif Hardware Design Guidelines ESP32-C3, PCB-Layout: <https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html>
- Datenblätter: [C3-MINI-1](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html), [C6-MINI-1/1U](https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html), [C5-MINI-1/1U](https://documentation.espressif.com/esp32-c5-mini-1_mini-1u_datasheet_en.html), [C61-MINI-1/1U](https://documentation.espressif.com/esp32-c61-mini-1_mini-1u_datasheet_en.html), [S3-MINI-1/1U](https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.html)
- ESP-Techpedia, RAM-Verbrauch je Chip: <https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/ram-usage.html>
- C61-MINI-1 (Varianten, Preis ca. 2 USD in Menge): <https://www.cnx-software.com/2026/08/04/espressif-esp32-c61-mini-1-1u-wi-fi-6-and-ble-iot-module-2-dollars/>
- MicroPython Downloads (ESP32-Boards) und ChangeLog (C6 ab v1.24, C5 ab v1.27, C5-PSRAM in v1.29): <https://micropython.org/download/?port=esp32>, <https://micropython.org/resources/micropython-ChangeLog.txt>
- LCSC: [C3-MINI-1-N4 C2838502](https://www.lcsc.com/product-detail/C2838502.html), [C6-MINI-1-N4 C5736265](https://lcsc.com/product-detail/C5736265.html), [S3-MINI-1-N4R2 C3013941](https://lcsc.com/product-detail/image/ESP32-S3-MINI-1-N4R2_C3013941.html)
- ESP32-C3 ohne PSRAM: <https://esp32.atomic14.com/socs/esp32-c3/>, <https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/external-ram.html>
- Abschnitt 3b: SoC-Datenblätter [ESP32-C6 v1.5](https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf) und [ESP32-C3 v2.4](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf) (Pins, Strapping, ADC, Strom); Moduldatenblätter C6-MINI-1 v1.5 und C3-MINI-1 v2.2 (siehe oben)
- ESP-IDF LP-Core (C6): <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-reference/system/ulp-lp-core.html>; LP-ADC nur P4 (Forum): <https://esp32.com/viewtopic.php?p=135957>
- ESP-IDF Wi-Fi-Treiber C6 (iTWT nur Station): <https://docs.espressif.com/projects/esp-idf/en/v5.5.2/esp32c6/api-guides/wifi.html>
- MicroPython v1.29.0: Board `ESP32_GENERIC_C6` und `sdkconfig.c6`/`sdkconfig.ble`/`partitions-4MiB-ota.csv`/`esp32_ulp.c` unter <https://github.com/micropython/micropython/tree/v1.29.0/ports/esp32>; Firmware-Dateien <https://micropython.org/download/ESP32_GENERIC_C6/>, <https://micropython.org/download/ESP32_GENERIC_C3/>; esp32-Modul-Doku <https://docs.micropython.org/en/latest/library/esp32.html>
- MicroPython-Issues: [#19396 lightsleep C6](https://github.com/micropython/micropython/issues/19396), [PR #19558 IDF 5.5.5](https://github.com/micropython/micropython/pull/19558), [#17334 WAKEUP_ALL_LOW C6](https://github.com/micropython/micropython/issues/17334), [#18101 aioble -519](https://github.com/micropython/micropython/issues/18101), [#19208 gpio_deep_sleep_hold](https://github.com/micropython/micropython/issues/19208), [#18859 WLAN+BLE Heap C3/C6](https://github.com/micropython/micropython/issues/18859)
- JLC-Teile: [C6-MINI-1-H4 C6553337](https://jlcpcb.com/partdetail/C6553337), [C6-MINI-1-H8 C42403058](https://jlcpcb.com/partdetail/C42403058), [C6-MINI-1U-H4 C20627095](https://jlcpcb.com/partdetail/C20627095), [C3-MINI-1-H4X C41349510](https://jlcpcb.com/partdetail/C41349510)
- Seeed XIAO ESP32-C6: <https://www.seeedstudio.com/Seeed-Studio-XIAO-ESP32C6-p-5884.html>, <https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/>
