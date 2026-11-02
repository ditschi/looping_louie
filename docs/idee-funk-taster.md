# Idee: Funk-Taster als Mitspieler (Joker per Knopf)

Stand: 2026-11-02 · Status: **Entschieden: BTHome-BLE-Taster sind geplantes Feature für V1.** Alle anderen
Funkwege (ESP-NOW, 433/868 MHz, Zigbee/Thread, nRF24, Infrarot) sind **abgelehnt: zu kompliziert, kein Mehrwert**.
Die Abschnitte dazu bleiben als Begründung stehen. Ergänzt [software-konzept.md](software-konzept.md),
[web-ui-konzept.md](web-ui-konzept.md) (4.2), [modus-baukasten.md](modus-baukasten.md) (2.5, 3) und
[idee-optionale-hardware.md](idee-optionale-hardware.md).

Frage: *Kann unser Chip Bluetooth? Können wir z. B. 4 physische Taster kabellos koppeln, die Joker (⏩ Boost,
⏪ Rückwärts-Stoß) auslösen?* Erweitert auf **alle Funkwege**: BLE, ESP-NOW, 433/868 MHz, Zigbee/Thread,
nRF24, Infrarot, als Referenz Kabel. Dazu: **Anlernen**, Geräte mit mehreren Tasten, Datenmodell.

Markierungen: **(geprüft)** = mit Quelle belegt · **(unsicher)** = aus dem Gedächtnis, nur Sekundärquelle oder
eigene Abschätzung, im Machbarkeitstest messen. Preise sind grobe Richtwerte (DE/EU, Stand der Recherche).
Die UI des Anlernens gestaltet später jemand anderes; hier stehen nur die technischen Fakten.

---

## Kurzantwort

- **Ja, der ESP32-C3 kann Bluetooth Low Energy 5** (kein klassisches Bluetooth), auch als Scanner und als
  Central (max. 9 Verbindungen). WLAN und BLE teilen sich die vorhandene Antenne. **Keine Hardware-Änderung.**
  **(geprüft)** [Datenblatt][c3-mini-ds], [Multi-Connection-Guide][idf-multiconn]
- **Favorit: BTHome-Taster, die nur senden** (Shelly BLU Button1 / Tough 1 / RC Button 4). Der ESP hört passiv
  zu, keine Verbindungen. Ereignisse Einfach/Doppel/Dreifach/Lang, bis zu 4 Tasten pro Gerät.
- **Zwei Risiken**: (1) **BLE + eigener Hotspot mit verbundenen Handys** stuft Espressif als „unterstützt, aber
  instabil“ ein, im Heim-WLAN als stabil. **(geprüft)** [RF Coexistence C3][idf-coex] (2) **RAM** in MicroPython
  wird mit WLAN + 8 WebSockets + BLE knapp.
- **Plan B: ESP-NOW** (Eigenbau-Taster oder fertige WiZmote). Das ist WLAN-Funk, braucht keinen Zeitmultiplex,
  kaum RAM, und MicroPython kann es. Nachteil: Taster brauchen LiPo/AAA statt Knopfzelle.
- **433 MHz** ist am billigsten (Fernbedienung ab ca. 1–5 €), braucht aber einen **Empfänger plus Antenne in der
  Basis**, einen freien Pin und Dekodierung, die MicroPython schlecht kann. Höchstens später.
- **Zigbee/Thread, nRF24, Infrarot: nein** (Begründung in 4.6–4.8). **Kabel** über die I²C-Pads ist die
  zuverlässige, billige Referenz.
- **Stufen**: Stufe 0 = Machbarkeitstest mit 1 Shelly-Taster auf dem XIAO ESP32-C3 im Hotspot mit 6–8 Handys.
  Stufe 1 = BTHome-Taster in **V1** (Entscheidung 2026-11-02). ESP-NOW wird nicht weiter verfolgt.
  Antenne, Layout und Controller-Alternativen: [analyse-funk-controller.md](analyse-funk-controller.md).

---

## 1. Was der ESP32-C3 funkmäßig kann

| Punkt | Wert | Quelle |
|---|---|---|
| Bluetooth | **BLE 5**, Mesh; **kein Classic** (kein BR/EDR, kein klassisches HID) | **(geprüft)** [Datenblatt][c3-mini-ds] |
| BLE-PHY | 125 kbit/s, 500 kbit/s (Coded PHY = Long Range), 1 Mbit/s, 2 Mbit/s | **(geprüft)** [Datenblatt][c3-mini-ds] |
| Empfindlichkeit | −96 dBm (1M), −93 dBm (2M), −99 dBm (500k), −104 dBm (125k) | **(geprüft)** [Datenblatt][c3-mini-ds] |
| BLE-Rollen | Broadcaster, Observer (Scanner), Peripheral, Central | **(geprüft)** [MicroPython bluetooth][mp-bt] |
| Verbindungen | **max. 9** (NimBLE und Bluedroid), praktisch RAM-begrenzt | **(geprüft)** [Multi-Connection-Guide][idf-multiconn] |
| WLAN | 802.11 b/g/n 2,4 GHz, **ESP-NOW** | **(geprüft)** [Datenblatt][c3-mini-ds] |
| 802.15.4 (Zigbee/Thread) | **nein** (erst ESP32-C6/H2) | **(geprüft)** [zigpy-espzb][zigpy-espzb] |
| Antenne | **eine** Antenne, ein Funkteil für WLAN und BLE | **(geprüft)** [Datenblatt][c3-mini-ds] |

**Long Range (Coded PHY)** nützt uns nicht: Fertige Taster senden auf 1M-PHY, der Tisch ist klein, und
Coded-PHY-Pakete sind lang und stören das WLAN. **(geprüft)** [RF Coexistence C3][idf-coex]

---

## 2. Ein Funkteil für WLAN und BLE (Koexistenz)

Der C3 schaltet das Funkteil zwischen WLAN und BLE um. Bei „WLAN verbunden“ beginnt die Periode am Beacon
(> 100 ms), WLAN und BLE bekommen z. B. je **50 %**. **(geprüft)** [RF Coexistence C3][idf-coex]

| BLE | STA verbunden | SoftAP Beacon | **SoftAP verbunden** | ESP-NOW RX | ESP-NOW TX |
|---|---|---|---|---|---|
| Scan | Y | Y | **C1** | S | Y |
| Advertising | Y | Y | **C1** | S | Y |
| Verbunden | Y | Y | **C1** | S | Y |

Y = stabil · **C1 = unterstützt, Leistung instabil** · S = stabil nur im STA-Modus. **(geprüft)** [RF Coexistence C3][idf-coex]

- **Heim-WLAN (STA)**: stabil. **Eigener Hotspot mit bis zu 8 Handys = C1** → größtes Risiko, nur Messen hilft.
- **ESP-NOW ohne BLE** ist reines WLAN und taucht in dieser Tabelle nicht als Konflikt auf: Es läuft auf dem
  Kanal des Hotspots bzw. Routers mit. **(geprüft)** [MicroPython espnow][mp-espnow]
- Espressif rät, bei Koexistenz die Standard-Scanparameter zu behalten. **(geprüft)** [RF Coexistence C3][idf-coex]
  MicroPythons Standard (11,25 ms Fenster alle 1,28 s ≈ 0,9 %) ist für Taster aber viel zu dünn (siehe 3).
  Zielkonflikt → im Test Fenster = Intervall = 30…100 ms ausprobieren.
- WebSocket-Latenz: Bei 50 % BLE-Anteil verschieben sich WLAN-Pakete um einige 10 ms **(unsicher)**. Für
  10 Status-Updates/s unkritisch, solange nichts verloren geht.
- Regel: BLE-Scan **nur in BEREIT/LÄUFT und nur, wenn Taster gekoppelt sind**. Ohne Taster bleibt BLE aus.

---

## 3. MicroPython und BLE

| Punkt | Stand |
|---|---|
| Modul | `bluetooth` (NimBLE): Central, Scan, Verbindungen, GATT-Client **(geprüft)** [MicroPython bluetooth][mp-bt] |
| Scan-Standard | Intervall 1,28 s, Fenster 11,25 ms → **überschreiben** **(geprüft)** [MicroPython bluetooth][mp-bt] |
| aioble | async, passt zu Microdot; Beispiel `scan(5000, interval_us=30000, window_us=30000, active=True)` **(geprüft)** [aioble][aioble] |
| Passiv/aktiv | BTHome-Daten stehen im Advertising → **passiv reicht**. In Home Assistant löste passives Scannen Verzögerungen bei Shelly-Tastern **(geprüft, Forum)** [simon42][simon42] |
| AES-CCM | `cryptolib` kann ECB/CBC/CTR, **kein CCM** **(geprüft)** [cryptolib][mp-crypto] → CCM aus ECB selbst bauen **(unsicher: Laufzeit)** |

**RAM** (der heikle Punkt):

- ESP32-C3, MicroPython 1.22: nach Bluetooth-Start **nur 17 328 Byte frei**; mit vorher reservierten
  20-KB-Blöcken stürzte `ble.active(True)` ab. **(geprüft)** [Issue #14293][mp-14293]
- ESP32 (IDF 4.4): **WLAN-Stack ca. 45,5 KB, Bluetooth ca. 19 KB**, lwIP 4–7 KB pro Socket. **(geprüft)** [Issue #8940][mp-8940]
- C3: ab dem 4. Socket `ENOBUFS` in einem Bericht **(geprüft)** [Issue #14421][mp-14421] – betrifft die 8 WebSockets
  schon **ohne** BLE.
- `ENOMEM` trotz großem `gc.mem_free()` kommt oft aus dem IDF-Heap → `micropython.mem_info()` („max new split“)
  ansehen. **(geprüft)** [Diskussion #12316][mp-12316]
- Vorteil C3: BLE-Speicher aus dem normalen Heap, zur Laufzeit an-/abschaltbar. **(geprüft)** [Espressif-Blog][esp-mem]

Konsequenz: BLE **früh** aktivieren (vor der Zerstückelung), Module einfrieren, Parser ohne viele Objekte.
Reicht es nicht: **Arduino + NimBLE-Arduino** oder **ESP-IDF** (weniger RAM, Koexistenz-Parameter einstellbar).
Web-UI und Protokoll bleiben (Software-Konzept 2.3).

---

## 4. Die Wege im Einzelnen

### 4.1 BLE a) BTHome-Taster (nur Senden) – Favorit

**Protokoll** **(geprüft)** [BTHome-Format][bthome-format]: Service-UUID `0xFCD2`; erstes Byte: Bit 0 =
verschlüsselt, Bit 2 = „trigger-based“; Objekt `0x00` = **Packet-ID** (nur bei Änderung auswerten → Dubletten weg);
Objekt `0x3A` = Taster: `0x01` Druck, `0x02` Doppel, `0x03` Dreifach, `0x04` lang, `0x80` gehalten.

**Shelly BLU Button1** **(geprüft)** [Bedienungsanleitung][shelly-manual], [Shelly-BLE-API][shelly-api]:
sendet nach Druck **1 Sekunde lang** BTHome; **LED-Ring und Summer** zeigen die Anzahl der Drücke; AES-CCM
möglich; CR2032 bis 2 Jahre; Reichweite bis 10 m innen; 36 × 36 × 6 mm. **Mehrfachklick-Fenster einstellbar**:
800 / 550 / 300 / 150 / 90 / 55 ms. Konfiguration: 10 s halten → 1 min per GATT verbindbar.

**Shelly BLU RC Button 4 / Wall Switch 4**: **jedes Paket enthält alle 4 Tasten** als vier `0x3A`-Objekte an
fester Position; gleiche Ereignisse und Klick-Einstellung. **(geprüft)** [RC Button 4 API][shelly-rc4]

**Latenz** Knopf → Motor:

| Schritt | Zeit |
|---|---|
| Taster wartet auf möglichen 2. Klick | 55 / 300 / 800 ms (Einstellung) |
| Paket gesendet und empfangen (Advertising-Abstand, Scan-Fenster, 50 % Funkzeit) | ca. 20–100 ms **(unsicher)** |
| IRQ, Parser, Spiellogik, Motor-Task | ca. 5–30 ms **(unsicher)** |
| **Summe** | **ca. 100–200 ms** (55 ms) · **ca. 350–450 ms** (300 ms) · ca. 0,9 s (800 ms) |

Zum Vergleich: Der Halte-Knopf am Handy löst nach `hold_ms` **400 ms** aus (Modus-Baukasten 2.5). Ein Taster mit
300-ms-Fenster ist also **so schnell wie das Handy**.

**Doppelklick-Problem**: Bei Einfach = ⏩, Doppel = ⏪ wartet **jeder** Einfach-Druck das Fenster ab, und unter
300 ms schaffen Kinder keinen sicheren Doppelklick. Lösungen: (1) **eine Taste pro Joker** (RC Button 4,
Fenster 55 ms) – empfohlen; (2) ein Knopf, nur ein Joker; (3) Einfach = ⏩, **lang = ⏪** (ob „lang“ beim Erreichen
der Haltezeit oder beim Loslassen kommt: **(unsicher)**); (4) Einfach/Doppel mit 300 ms.

**Zuverlässigkeit**: 1 s Wiederholungen + Packet-ID → verpasste Drücke unwahrscheinlich, im Hotspot-Betrieb
(C1) **messen**. Zwei schnelle Einzel-Joker können als Doppelklick ankommen.

**Weitere BTHome/BLE-Advertiser**: Xiaomi/Mijia-Taster senden verschlüsselt (MiBeacon), Schlüssel nur über die
Xiaomi-Cloud **(unsicher)** → nicht empfohlen.

### 4.2 BLE b) Verbindungs-Taster – verworfen

- **iTag** (2–5 €): Knopf meldet nur bei bestehender GATT-Verbindung (Notify `FFE1`); ESPHome nennt **max. 3**
  iTags pro ESP32. **(geprüft)** [ESPHome iTag][esphome-itag] Piepen bei Abbruch, Schlafen, Neuverbinden
  **(unsicher)**. Im Hotspot-Betrieb (C1) zu wackelig.
- **BLE-HID-Fernbedienungen**: HID-Host über GATT mit Pairing/Bonding; viele Billig-Selfie-Auslöser sind
  **Classic** und für den C3 unsichtbar **(unsicher, je Modell)**.
- **Flic 2** (ca. 30 €, **unsicher**): offenes, aber aufwendiges Protokoll (Ed25519, X25519, Chaskey-LTS, Sitzung
  über GATT). **(geprüft)** [Flic-2-Protokoll][flic2-spec]

### 4.3 ESP-NOW – Plan B

- **WLAN-Rahmen ohne Verbindung**, Kanal = Kanal des Hotspots bzw. Routers. Bei STA muss der Energiesparmodus aus
  sein (`pm=PM_NONE`), ein aktiver AP schaltet ihn ohnehin ab. Bis 20 Peers, 6 davon verschlüsselt; asyncio über
  `aioespnow`. **(geprüft)** [MicroPython espnow][mp-espnow]
- Funklatenz **1–5 ms**, Unicast mit Bestätigung. **(geprüft, Sekundärquelle)** [hackaday ESP-NOW][hd-espnow]
- **RAM**: Das WLAN läuft ohnehin, ESP-NOW braucht nur Puffer (wenige KB) **(unsicher)**. Kein Zeitmultiplex.
- **Fertige Geräte**: **WiZmote** (Philips WiZ, 4 Tasten + Funktionstasten, 2× AAA) sendet ESP-NOW; WLED koppelt
  sie über die MAC („Last device seen“ → „+“) und verlangt dauerhaft waches WLAN. **(geprüft)** [WLED ESP-NOW][wled-espnow]
  Auf welchen Kanälen die WiZmote sendet und ob sie im Hotspot-Kanal ankommt: **(unsicher, testen)**.
  Espressifs **Knopfzellen-Schalter** (ESP32-C2, ESP-NOW) reagiert laut Hersteller in **≤ 150 ms**, CR2032 bis
  5 Jahre bei 10 Drücken/Tag – Referenzdesign, kein Handelsprodukt. **(geprüft)** [Espressif ESP-NOW][esp-espnow]
- **Eigenbau** (ESP32-C3-SuperMini o. ä. + Arcade-Taste + LiPo, ca. 6–10 €): Aus Deep Sleep bis zum ersten Paket
  ca. 100–300 ms (C/Arduino), mit MicroPython eher 0,5–1 s **(unsicher)**. Besser: im Spiel Light Sleep, Wecken per
  GPIO → < 20 ms. **Knopfzelle reicht nur mit Spezial-Design** (siehe Espressif) → LiPo/AAA. Den Kanal (Hotspot vs.
  Heim-WLAN) findet der Taster selbst: Kanäle durchprobieren, bis die Bestätigung kommt **(unsicher, Standardmuster)**.
  Bonus: Rückmeldung zum Taster (LED „angenommen“/„leer“) ist möglich, weil ESP-NOW in beide Richtungen geht.
- **Firmware**: Empfänger in MicroPython gut machbar. Taster-Seite für schnelles Aufwachen besser in C/Arduino.

### 4.4 433 / 868 MHz (EV1527 u. ä.)

- **Fernbedienungen**: EV1527 sendet **20 Bit Geräte-ID + 4 Datenbits** (Taste), OOK/ASK, wiederholt den Rahmen,
  solange gedrückt. **(geprüft)** [done.land EV1527][done-ev1527] Handsender mit 1–4 Tasten ab ca. 1 $ (Großhandel),
  in DE ca. 5–7 €. **(geprüft, Preise schwanken)** [Preisübersicht][ev1527-preis]
- **Empfänger nötig**: z. B. **RXB6** (Superhet, 3,0–5,5 V, **6 mA bei 3,3 V**, −116 dBm, **43 × 17 × 4 mm**,
  Enable-Pin für Stromsparen). **(geprüft, Händlerangaben)** [RXB6][rxb6] Dazu Drahtantenne λ/4 ≈ **17 cm**.
  Passt **nicht** in die AA-Form, nur **in die Basis** (wie Ladeplatine Einbau B), Kabel zur Hauptplatine.
- **Pins**: Daten auf **RXD (GPIO20)**, aber nur ohne Beschleunigungssensor-INT; sonst TXD (gibt beim Booten aus,
  Push-Pull-Konflikt → Serienwiderstand 1–4,7 kΩ **(unsicher)**). Für Enable fehlt ein weiterer Pin. Ohne Enable
  zieht der Empfänger 6 mA auch im Schlaf (LDO bleibt an) → ca. 140 mAh/Tag, **nicht tragbar**.
- **Dekodieren**: Pulsbreiten im Bereich einiger 100 µs. MicroPythons `esp32.RMT` kann **nur senden**, nicht
  empfangen. **(geprüft)** [MicroPython esp32][mp-esp32] Pin-IRQs plus GC-Pausen → fehleranfällig **(unsicher)**.
  In C/Arduino Standard (RMT-RX, rc-switch). Alternative: Empfängermodul mit eingebautem Decoder und UART-Ausgang
  **(unsicher, Produkte prüfen)**.
- **Latenz**: Rahmen ca. 30–50 ms; zwei gleiche Rahmen abwarten → ca. 60–120 ms **(unsicher)**. Ereignisse nur
  „gedrückt/hält“; Einfach/Lang leitet die Firmware aus der Dauer ab, Doppel aus Pausen.
- **Sicherheit**: Fester Code, kein Zähler, kinderleicht abzuhören und nachzusenden. Viele Fremdsender im Band
  (Wetterstationen, Klingeln) → nur angelernte IDs zählen. **868 MHz** (z. B. FS20, Homematic) ist proprietär,
  Empfänger seltener → nicht weiter verfolgt.
- **Batterie**: Sender schläft, sendet nur bei Druck (A23/CR2032, Jahre) **(unsicher)**.

### 4.5 Kabel (Referenz)

Pads sind da: **J2** = 3V3, GND, SDA (IO8), SCL (IO2), INT (RXD); **J3** = EN, TXD, BOOT (IO9), GND
(`hardware/scripts/gen_main_schematic.py`). 4 Spieltasten über einen **I²C-Port-Expander** (z. B. PCF8574/MCP23008,
**unsicher: Typ wählen**) am J2-Bus, INT auf RXD. Latenz < 10 ms, 100 % zuverlässig, keine Batterien, Kosten
ca. 5–15 € für 4 Arcade-Tasten, Kabel und Expander. Nachteil: Kabel über den Tisch. Gut als **Testwerkzeug**
für die Spiellogik („Taster-Mitspieler“), bevor Funk dazukommt.

### 4.6 Zigbee / Thread (802.15.4) – nein

- Der C3 hat kein 802.15.4. ESP32-C6 (WLAN 6 + BLE + 802.15.4) und H2 (nur 802.15.4) können Zigbee.
  **(geprüft)** [zigpy-espzb][zigpy-espzb]
- **C6 als Einzelchip**: Ein Zigbee-Koordinator verhält sich wie ein Router (dauernd empfangen). Espressif:
  Zigbee/Thread-**Router + WLAN-SoftAP = nicht unterstützt (X)**, mit STA nur C1. **(geprüft)** [RF Coexistence C6][idf-coex-c6]
  Damit fällt unser Hotspot-Betrieb weg.
- **C3 + H2 als Zweitchip** (Zigbee-NCP über UART): eigenes Modul, passt nicht in die AA-Form, braucht UART-Pins,
  eigenes Firmware-Projekt.
- **Firmware**: `esp-zigbee-sdk` nur in C; MicroPython hat **keine** Zigbee-Unterstützung (offener Wunsch).
  **(geprüft)** [MicroPython #11869][mp-11869] Rust: kein fertiger Zigbee-Stack **(unsicher)**.
- Taster (IKEA Rodret/Styrbar, Aqara Mini Switch) wären günstig (ca. 6–15 € **unsicher**), aber Netzaufbau,
  Beitritt, Binding und ZCL sind ein Projekt für sich. **Lohnt nicht.**

### 4.7 nRF24 (proprietäres 2,4 GHz) – nein

nRF24L01+-Module kosten ca. 1 €, brauchen aber SPI + CE + CSN (**5 Pins**, wir haben 2–3), jeder Taster braucht
zusätzlich einen eigenen Mikrocontroller. ESP-NOW leistet dasselbe **ohne** Zusatzfunk. Billige 2,4-GHz-Fernbedienungen
(Spielzeug) sind undokumentiert. MicroPython-Treiber gäbe es (`nrf24l01` in micropython-lib) **(unsicher)**.

### 4.8 Infrarot – nein

IR-Empfänger (TSOP-Typ, 1 Pin, < 1 mA **unsicher**) und Mini-Fernbedienungen (ca. 1–3 €) sind billig, MicroPython kann
NEC & Co. dekodieren ([micropython_ir][mp-ir] **unsicher: auf C3 getestet?**). Aber: **Sichtverbindung** zum Turm,
den der kreisende Arm verdeckt; Kinder zielen im Eifer nicht; Sonnenlicht stört; **baugleiche Fernbedienungen
senden identische Codes** → Spieler nicht unterscheidbar. Latenz ca. 70–110 ms (NEC-Rahmen ca. 68 ms) **(unsicher)**.

---

## 5. Gesamtvergleich (4 Spieler)

| | BLE BTHome | BLE iTag | ESP-NOW | 433 MHz | Kabel | Zigbee (C6/H2) | IR |
|---|---|---|---|---|---|---|---|
| Zusatz-HW am Louie | **keine** | keine | **keine** | Empfänger + 17-cm-Antenne in der Basis, Pins | Expander, Kabel | anderer Chip / Zweitchip | IR-Empfänger oben |
| Kosten 4 Taster | 60–100 € | 10–20 € | 25–40 € Eigenbau; WiZmote ca. 15–25 €/Stk. **(unsicher)** | 5–30 € + ca. 3 € Empfänger | 5–15 € | 25–60 € + Chip | 5–12 € |
| Latenz | 100–450 ms (Klick-Fenster) | < 100 ms verbunden | **< 20 ms** wach, 150–300 ms aus Schlaf | 60–120 ms | **< 10 ms** | ca. 50–100 ms **(unsicher)** | 70–110 ms |
| Reichweite | 10 m innen | ähnlich | 10–50 m | 10–30 m | Kabel | 10–20 m | Sicht |
| Zuverlässigkeit | gut, im Hotspot **C1** | Verbindungen reißen | sehr gut | gut, Störer im Band | perfekt | gut, Hotspot **X** | schlecht |
| Fremdgeräte/Sicherheit | MAC-Filter, optional AES + Zähler | gekoppelt | MAC-Filter, optional verschlüsselt | Fest-Code, Replay trivial | – | Netzschlüssel | keine |
| Batterie Taster | CR2032, bis 2 J. | Monate | LiPo/AAA (Eigenbau); 2× AAA (WiZmote) | Jahre | – | 1–2 J. **(unsicher)** | Monate–Jahre |
| Verfügbarkeit DE | gut (Shelly) | gut | Eigenbau; WiZmote mäßig | sehr gut | sehr gut | gut | sehr gut |
| Firmware-Aufwand | mittel | hoch | **niedrig–mittel** | mittel (C) / hoch (MP) | niedrig | sehr hoch | niedrig |
| RAM am Louie | **hoch** (BLE-Stack) | hoch | niedrig | niedrig | keiner | – | niedrig |
| MicroPython? | ja (`aioble`), RAM-Risiko | mühsam | **ja** (`espnow`) | **schlecht** (kein RMT-RX) → C | ja | **nein** (nur C) | ja |
| Bewertung | ★★★ | ★ | ★★★ Plan B | ★★ später | ★★ Referenz | ✗ | ✗ |

---

## 6. Anlernen und Geräte mit mehreren Tasten (technische Fakten)

### 6.1 Wie die Firmware Gerät, Taste und Ereignis erkennt

| Weg | Geräte-ID | Taste | Ereignis | Mehrfach-Erkennung |
|---|---|---|---|---|
| BTHome | **MAC** (+ optional 16-Byte-Schlüssel) | Position des `0x3A`-Objekts (1…n) | im Paket: 1×, 2×, 3×, lang, gehalten | **im Taster** (Klick-Fenster) |
| ESP-NOW Eigenbau | **MAC** | eigenes Feld | eigenes Feld (z. B. down/up, Zähler) | frei: im Taster oder im Louie |
| WiZmote | MAC | Tastencode | nur Druck **(unsicher)** | im Louie |
| 433 EV1527 | **20-Bit-ID** | 4 Datenbits (oft 1 Bit je Taste, **unsicher**, je Modell) | nur „Rahmen kommt“ | **im Louie** aus Dauer/Pausen |
| Kabel | Expander-Pin | Pin | Flanken | im Louie |

Die Tastenzahl eines BTHome-Geräts ergibt sich aus der **Anzahl der `0x3A`-Objekte** im Paket (RC Button 4 = 4,
Button1 = 1). **(geprüft)** [RC Button 4 API][shelly-rc4] Bei 433 MHz und WiZmote kennt der Louie die Tastenzahl
nicht; man lernt jede Taste einzeln an.

### 6.2 Ablauf Anlernen (technisch)

1. Louie geht in den **Lernmodus** (z. B. 30 s): BLE-Scan bzw. ESP-NOW-Empfang offen, alle Ereignisse **unbekannter**
   Geräte werden gesammelt (ID, Taste, Ereignis, RSSI, Zeitpunkt).
2. Gemeldet wird nur, was **während des Lernmodus gedrückt** wurde (nicht: was zufällig in der Luft ist). Bei
   BLE/ESP-NOW zusätzlich RSSI-Schwelle (z. B. > −70 dBm **unsicher**), damit der Nachbar-Taster nicht gewinnt.
3. Für Mehrtasten-Geräte: „Drücke jede Taste einmal“ → Louie sammelt die Tastennummern.
4. Gerät speichern (ID, Typ, Tastenzahl), danach **Belegung** zuweisen (6.3).
5. Bei BTHome mit Schlüssel: Schlüssel eingeben oder per GATT setzen **(unsicher)**; ab dann Zähler prüfen.

### 6.3 Ein Gerät auf mehrere Spieler aufteilen

**Technisch geht das bei allen Wegen**, weil jede Taste einzeln erkannt wird. Die Spiellogik sieht nur
„Eingang (Gerät, Taste, Ereignis) → Spieler, Joker-Platz“.

- **RC Button 4 = 4 Spieler mit je 1 Joker** oder **2 Spieler mit je ⏪/⏩**. BTHome meldet den Zustand **aller vier
  Tasten in jedem Paket** → gleichzeitige Drücke zweier Spieler kommen beide an. **(geprüft)** [RC Button 4 API][shelly-rc4]
- **433-MHz-4-Tasten-Sender**: Gleichzeitige Drücke ergeben je nach Encoder eine Bit-Kombination oder nur eine
  Taste **(unsicher)**. Zwei Spieler am selben Sender stören sich.
- Praktisch sinnvoll nur, wenn die Spieler **nebeneinander** sitzen (Gerät liegt zwischen ihnen). Eine 4-Tasten-
  Fernbedienung für 4 Plätze rund um den Tisch funktioniert physisch nicht.

### 6.4 Datenmodell-Vorschlag `devices.json`

Trennung: **Geräte** (Hardware, dauerhaft, Besitzer) ↔ **Belegung** (welche Taste spielt für wen). Joker werden
über den **Platz im Modus** (1. / 2. Joker) belegt, nicht über die Art – so passt die Belegung zu jedem Modus.

```json
{
  "schema": 1,
  "devices": [
    { "id": "d1", "tech": "bthome", "addr": "7c:c6:b6:12:34:56", "model": "SBBT-004CEU",
      "label": "Fernbedienung grau", "keys": 4, "aes_key": null, "click_ms": 55,
      "last": { "pid": 17, "counter": null, "bat": 80, "rssi": -58, "seen": 1793612680 } },
    { "id": "d2", "tech": "rf433", "addr": "ev1527:0x5A3C1", "label": "Handsender 1",
      "keys": 2, "keymap": { "1": 1, "2": 2 } },
    { "id": "d3", "tech": "espnow", "addr": "a0:76:4e:aa:bb:cc", "label": "Buzzer rot",
      "keys": 1, "lmk": null }
  ],
  "players": [
    { "id": "t1", "name": "Rakete", "color": "red",
      "inputs": [ { "dev": "d1", "key": 1, "ev": "press", "joker": 1 },
                  { "dev": "d1", "key": 2, "ev": "press", "joker": 2 },
                  { "dev": "d1", "key": 2, "ev": "long",  "action": "out" } ] },
    { "id": "t2", "name": "Blitz", "color": null,
      "inputs": [ { "dev": "d1", "key": 3, "ev": "press", "joker": 1 } ] }
  ]
}
```

- `tech`: `bthome` | `espnow` | `rf433` | `wired`. `addr` je Weg (MAC, EV1527-ID, Expander-Pin).
- `keymap` (433): empfangene Datenbits → Tastennummer.
- `last`: nur RAM/selten schreiben (Flash schonen); `counter` = letzter BTHome-Zähler bei Verschlüsselung.
- `players`: Taster-Spieler (Mitspieler ohne Display); zählen zur Spielerzahl. Kontingente hängen am Spieler
  wie beim Handy-Sitzungstoken.
- `joker`: 1 oder 2 = erster/zweiter Joker des aktuellen Modus; `action`: `out` („Ich bin raus“).
- Ein Eingang darf nur **einem** Spieler gehören (Prüfung beim Speichern).

---

## 7. Integration ins Konzept: Taster als Mitspieler

Grundsatz bleibt: **Ein Mitspieler ist ein Gerät** (web-ui-konzept 4.2) – Handy **oder Taster(-gruppe)**.

- Zählen zur **Spielerzahl** (Standard 4, bis 8). Kontingente, Abklingzeit, gemeinsame Sperre wie beim Handy.
  Die Spiellogik unterscheidet die Geräte nicht.
- **Rückmeldung ohne Display**: Shelly blinkt/piept selbst bei jedem Druck. Ob der Joker **angenommen** wurde,
  zeigt der Motor (das ist der Witz) und der **Ticker** auf allen Handys („🔴 Rakete: ⏩!“ / „kein ⏩ mehr“).
  Optional Status-LED am Louie. ESP-NOW-Eigenbau könnte eine LED am Taster zurückmelden.
- **Ausscheiden**: Leiter markiert den Taster-Spieler, oder eigene Taste/lang (siehe Datenmodell).
- **Vorteile**: Kinder ohne Handy spielen mit, kein Handy-Akku, kein WLAN-Beitritt, keine Bildschirm-Ablenkung.
  **Party-Rotation**: Taster bleibt am Platz, „🔄 Spielerwechsel“ gilt genauso.
- **Grenzen**: max. 2 Joker pro Spieler (passt zur Regel in Modus-Baukasten 2.5); kein Geister-Layout sichtbar.
- **Protokoll**: `players[]` bekommt `"dev":"phone"|"button"`, `"bat":80`; Ereignis
  `{"t":"event","kind":"boost","seat":2,"src":"button"}`; REST `GET/POST/DELETE /api/devices` und
  `POST /api/devices/learn` (Lernmodus starten/Ergebnis holen).

---

## 8. Empfehlung in Stufen

| Stufe | Inhalt | Ergebnis |
|---|---|---|
| **0 – Machbarkeit** (½–1 Tag) | XIAO ESP32-C3, MicroPython, **1 Shelly BLU RC Button 4** (oder Button1). Microdot-WebSocket wie im PoC, **Hotspot mit 6–8 Handys** + `aioble`-Passiv-Scan. Messen: `mem_info`, verpasste Drücke (100 zählen), Latenz Knopf → GPIO, WebSocket-Ping, Handy-Abbrüche. Gleicher Test im STA-Betrieb. **Parallel**: ESP-NOW-Empfang mit einem zweiten XIAO als Taster (1 h Aufwand). | Ja/Nein BLE, Vergleich ESP-NOW |
| 0b | Kabel-Taster am Expander als Spiellogik-Test | Taster-Spieler im Code |
| **1 – V1.1** | `net/ble.py` (BTHome), Lernmodus, `devices.json`, Belegung | Taster als Mitspieler |
| 1b | Verschlüsselung + Zähler, Batterieanzeige | Party-tauglich |
| **Plan B** | ESP-NOW-Taster (Eigenbau, ggf. WiZmote) | wenn BLE im Hotspot nicht trägt |
| später | 433 MHz mit Empfänger in der Basis, Dekodierung in C | billigste Taster |
| Plan C | Firmware nach Arduino/ESP-IDF | wenn nur der RAM das Problem ist |

**Abbruchkriterien für BLE (Stufe 0):**

- `mem_info` „max new split“ < 20 KB oder `ENOMEM`/Absturz in 30 min Dauerlauf (WLAN + 8 WebSockets + Scan).
- Mehr als **1 von 100** Drücken verpasst (Hotspot, 8 Handys).
- Latenz Knopf → Motor **> 500 ms** Median bzw. > 800 ms (95 %) bei 300-ms-Fenster; > 250 ms bei 55 ms.
- Handys verlieren die WebSocket-Verbindung oder Updates stocken > 1 s.

Fällt nur der Hotspot-Fall durch: BLE-Taster **nur im Heim-WLAN**, im Hotspot ESP-NOW.

---

## 9. Auswirkungen

**Hardware**: Für BLE und ESP-NOW **keine**. Antennenende weiter frei halten. Nur 433 MHz bräuchte Empfänger,
Antenne und Pins (Basis, J2/J3), Zigbee einen anderen Chip.

**Firmware** (Software-Konzept 8.1):

```
louie/
  net/ble.py        BTHome-Scanner-Task (aioble, passiv), Parser, Dedup (Packet-ID), Zähler/Schlüssel
  net/espnow.py     ESP-NOW-Empfang (aioespnow), gleiches Ereignisformat
  inputs.py         (Gerät, Taste, Ereignis) → Spieler + Joker-Platz → gleicher Wunsch wie per WebSocket
  store.py          + devices.json
```

- Eigene asyncio-Tasks, nur aktiv, wenn Geräte angelernt sind **und** Phase BEREIT/LÄUFT (bzw. Lernmodus).
- Motor-Task mit Watchdog unberührt; `core/` sieht nur „Spieler n will Joker k“.
- `hal/sim.py`: Tastendrücke per Tastatur für Tests ohne Funk.

**Firmware-Sprache je Weg** (Gesamtvergleich macht ein anderer Bericht): BTHome – MicroPython geht, C spart RAM ·
ESP-NOW – MicroPython gut, Taster-Seite besser C · 433 MHz – **C/ESP-IDF/Arduino deutlich besser** (RMT-RX) ·
Zigbee – **nur C** · iTag/HID/Flic – C · Kabel/IR – MicroPython.

---

## 10. Offene Punkte

- Advertising-Abstand der Shelly-Taster in der 1-s-Sendephase **(unsicher)** – im Test mitschneiden.
- „Lang“ beim Erreichen der Haltezeit oder beim Loslassen? **(unsicher)**
- Wie äußert sich C1 (BLE + SoftAP verbunden) praktisch? Nur messen hilft.
- Shelly-Schlüssel per GATT vom Louie setzen (Kopplung ohne Shelly-App)? **(unsicher)**
- Shelly BLU sendet mit **fester MAC** (keine wechselnde private Adresse)? Voraussetzung fürs Anlernen über die MAC. **(unsicher)**
- Shelly BLU nutzt **Legacy-Advertising** (BLE-4-Format, 1M PHY), kein Extended Advertising? Kann MicroPython/aioble bei Bedarf Extended Advertising scannen? **(unsicher)**
- WiZmote: Kanalverhalten, Preis, Verfügbarkeit in DE **(unsicher)**.
- Kombiniertes Spiel (2 Louies): ein Gerät nur bei einem Louie angelernt.

---

## Quellen

- `c3-mini-ds` – Espressif, ESP32-C3-MINI-1 Datenblatt: https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.pdf
- `idf-coex` – ESP-IDF, RF Coexistence (ESP32-C3): https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/coexist.html
- `idf-coex-c6` – ESP-IDF, RF Coexistence (ESP32-C6): https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html
- `idf-multiconn` – ESP-IDF, BLE Multi-Connection Guide (ESP32-C3): https://docs.espressif.com/projects/esp-idf/en/v6.0/esp32c3/api-guides/ble/ble-multiconnection-guide.html
- `mp-bt` – MicroPython, `bluetooth`: https://docs.micropython.org/en/latest/library/bluetooth.html
- `aioble` – micropython-lib, aioble: https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble/README.md
- `mp-crypto` – MicroPython, `cryptolib`: https://docs.micropython.org/en/latest/library/cryptolib.html
- `mp-espnow` – MicroPython, `espnow`: https://docs.micropython.org/en/latest/library/espnow.html
- `mp-esp32` – MicroPython, `esp32` (RMT nur Senden): https://docs.micropython.org/en/latest/library/esp32.html
- `mp-14293` / `mp-14421` – Issues #14293 (C3 BLE-Panic, Heap) und #14421 (Sockets): https://notes.alelec.net/assets/mpy-triage/pair/2039.html
- `mp-8940` – Issue #8940 (Heap WLAN/BLE/TLS): https://github.com/micropython/micropython/issues/8940
- `mp-12316` – Diskussion #12316: https://github.com/orgs/micropython/discussions/12316
- `mp-11869` – MicroPython, Wunsch Zigbee auf C6: https://notes.alelec.net/assets/mpy-triage/pair/906.html
- `esp-mem` – Espressif-Blog, Speicher ESP32 vs. C3: https://developer.espressif.com/blog/memory-availability-comparison-between-esp32-and-esp32-c3/
- `esp-espnow` – Espressif, ESP-NOW (Knopfzellen-Schalter): https://espressif.com/en/solutions/low-power-solutions/esp-now
- `bthome-format` – BTHome v2 Format: https://bthome.io/format/
- `bthome-enc` – BTHome Verschlüsselung: https://bthome.io/encryption/
- `shelly-api` – Shelly BLE-API, BLU Button: https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/button
- `shelly-rc4` – Shelly BLE-API, BLU RC Button 4: https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/wall_us
- `shelly-manual` – ShellyBLU Button1 Anleitung (PDF): https://www.netxl.com/shelly/docs/shelly-blu-button-user-manual.pdf
- `shelly-tough` – Shelly BLU Button Tough 1 (Shop DE): https://www.shelly.com/de/products/shelly-blu-button-tough-1-mocha
- `jacob-button1` – Jacob, Shelly BLU Button1: https://www.jacob.de/produkte/shelly-blu-button1-shelly-bb-r-artnr-8360883.html
- `netxl-rc4` – NetXL, Shelly BLU RC Button 4: https://www.netxl.com/controllers-and-hubs/shelly-blu-rc-button-4.md
- `simon42` – simon42-Forum, BLU Button 1 aktiv/passiv scannen: https://community.simon42.com/t/erstes-shelly-geraet-und-gleich-enttaeuscht-blu-button-1/79566
- `esphome-itag` – ESPHome, BLE iTag: https://esphome.io/cookbook/ble_itag.html
- `flic2-spec` – Flic 2 Protocol Specification: https://github.com/50ButtonsEach/flic2-documentation/wiki/Flic-2-Protocol-Specification
- `hd-espnow` – hackaday.io, ESP-NOW-Beispiel und Latenz: https://hackaday.io/project/164132-hello-world-for-esp-now
- `wled-espnow` – WLED, ESP-NOW-Fernbedienungen (WiZmote): https://kno.wled.ge/interfaces/espnow/
- `done-ev1527` – done.land, EV1527: https://done.land/components/data/datatransmission/wireless/shortrangedevice/am/ask/ev1527/
- `ev1527-preis` – Beispiel 4-Tasten-EV1527-Sender (ManoMano): https://www.manomano.es/p/smart-home-new-433mhz-4-key-ev1527-coding-key-remote-control-switch-rf-mitter-wireless-remote-c-217268109
- `rxb6` – TinyTronics, RXB6-Empfänger: https://www.tinytronics.nl/en/communication-and-signals/wireless/rf/modules/rxb6-433mhz-rf-receiver
- `zigpy-espzb` – zigpy-espzb (Zigbee mit ESP32-C6/H2): https://pypi.org/project/zigpy-espzb
- `mp-ir` – Peter Hinch, micropython_ir: https://github.com/peterhinch/micropython_ir

[c3-mini-ds]: https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.pdf
[idf-coex]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/coexist.html
[idf-coex-c6]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html
[idf-multiconn]: https://docs.espressif.com/projects/esp-idf/en/v6.0/esp32c3/api-guides/ble/ble-multiconnection-guide.html
[mp-bt]: https://docs.micropython.org/en/latest/library/bluetooth.html
[aioble]: https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble/README.md
[mp-crypto]: https://docs.micropython.org/en/latest/library/cryptolib.html
[mp-espnow]: https://docs.micropython.org/en/latest/library/espnow.html
[mp-esp32]: https://docs.micropython.org/en/latest/library/esp32.html
[mp-14293]: https://notes.alelec.net/assets/mpy-triage/pair/2039.html
[mp-14421]: https://notes.alelec.net/assets/mpy-triage/pair/2039.html
[mp-8940]: https://github.com/micropython/micropython/issues/8940
[mp-12316]: https://github.com/orgs/micropython/discussions/12316
[mp-11869]: https://notes.alelec.net/assets/mpy-triage/pair/906.html
[esp-mem]: https://developer.espressif.com/blog/memory-availability-comparison-between-esp32-and-esp32-c3/
[esp-espnow]: https://espressif.com/en/solutions/low-power-solutions/esp-now
[bthome-format]: https://bthome.io/format/
[bthome-enc]: https://bthome.io/encryption/
[shelly-api]: https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/button
[shelly-rc4]: https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/wall_us
[shelly-manual]: https://www.netxl.com/shelly/docs/shelly-blu-button-user-manual.pdf
[shelly-tough]: https://www.shelly.com/de/products/shelly-blu-button-tough-1-mocha
[jacob-button1]: https://www.jacob.de/produkte/shelly-blu-button1-shelly-bb-r-artnr-8360883.html
[netxl-rc4]: https://www.netxl.com/controllers-and-hubs/shelly-blu-rc-button-4.md
[simon42]: https://community.simon42.com/t/erstes-shelly-geraet-und-gleich-enttaeuscht-blu-button-1/79566
[esphome-itag]: https://esphome.io/cookbook/ble_itag.html
[flic2-spec]: https://github.com/50ButtonsEach/flic2-documentation/wiki/Flic-2-Protocol-Specification
[hd-espnow]: https://hackaday.io/project/164132-hello-world-for-esp-now
[wled-espnow]: https://kno.wled.ge/interfaces/espnow/
[done-ev1527]: https://done.land/components/data/datatransmission/wireless/shortrangedevice/am/ask/ev1527/
[ev1527-preis]: https://www.manomano.es/p/smart-home-new-433mhz-4-key-ev1527-coding-key-remote-control-switch-rf-mitter-wireless-remote-c-217268109
[rxb6]: https://www.tinytronics.nl/en/communication-and-signals/wireless/rf/modules/rxb6-433mhz-rf-receiver
[zigpy-espzb]: https://pypi.org/project/zigpy-espzb
[mp-ir]: https://github.com/peterhinch/micropython_ir
