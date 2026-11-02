# Firmware-Sprache: MicroPython, C/C++ oder Rust?

Stand: 2026-11-02 · Status: Entscheidungsvorlage. Ergänzt [software-konzept.md](software-konzept.md) Abschnitt 2
und 8, [modus-baukasten.md](modus-baukasten.md) und [web-ui-konzept.md](web-ui-konzept.md).

Markierungen: **(geprüft)** = in Doku oder Quelltext nachgesehen (Quelle unten), **(unsicher)** = Schätzung,
Erfahrungswert oder nur indirekt belegt, muss im Machbarkeitstest gemessen werden.

## Kurzfassung

- **Empfehlung: MicroPython bleibt die Plattform**, aber nicht mehr mit der Standard-Firmware, sondern mit
  einem **eigenen Firmware-Build** (mehr Sockets, frozen modules). Der Wechsel wird an einen **eintägigen
  Machbarkeitstest mit harten Abbruchkriterien** gebunden (Abschnitt 8).
- **Plan B ist C++ auf ESP-IDF-Basis** (Arduino-ESP32 3.x mit NimBLE-Arduino und ESPAsyncWebServer). Die
  Spiellogik wird dann eine portable C++-Bibliothek. Rust wird **jetzt nicht** gewählt: der Funkteil von
  `esp-hal` (`esp-radio`) ist im November 2026 noch Beta, die WLAN/BLE-Koexistenz ist dort als *unstable*
  markiert, und die Lernkurve ist für einen Python-Bastler am steilsten.
- **Externe Taster: BLE-BTHome passiv scannen** (z. B. Shelly BLU Button1). **433 MHz streichen**: Es gibt
  keinen freien GPIO, MicroPython kann es nicht, und es bringt keinen Vorteil gegenüber BLE. ESP-NOW nur als
  Option für Selbstbau-Taster, im Hotspot-Betrieb mit aktivem BLE wird ESP-NOW-Empfang von Espressif nicht
  unterstützt.
- **Unabhängig von der Sprache:** Laut Espressif ist BLE zusammen mit einem **SoftAP, an dem Clients hängen,
  „unterstützt, aber instabil“**. Das ist eine Eigenschaft des Funkteils, keine der Sprache. Der Test muss also
  gegen eine C++-Referenz messen, sonst wird die falsche Ursache bekämpft.
- **Schichten und Protokoll bleiben** (software-konzept.md 7 und 8). Neu ist nur eine Eingabequelle
  „Joker-Taster“ in der HAL und ein kleiner REST-Bereich zum Anlernen.

## 1. Was die neuen Anforderungen technisch bedeuten

| Anforderung | Technische Last | Sprachabhängig? |
|---|---|---|
| 8 Handys per WebSocket, 10 Zustände/s | 8 TCP-Verbindungen dauerhaft, dazu kurzlebige HTTP-Verbindungen (Browser öffnen 4–6 parallel), 80 Nachrichten/s | Ja: RAM pro Verbindung, Socket-Limit im Build |
| AP mit Captive Portal (DNS), mDNS | 1 UDP-Socket DNS, mDNS (ESP-IDF-Komponente) | wenig |
| Modus-Interpreter Schema 2 + Vorschau | CPU-Spitzen (Vorschau einer 3-min-Runde mit 10 Hz = 1800 Punkte, plus Bot-Probe), JSON-Verarbeitung bis 2 KB | Ja: Python ist ca. 10–50× langsamer als C (unsicher) |
| Joker per BLE (BTHome passiv) | BLE-Controller + NimBLE-Host dauerhaft aktiv, Funkzeit-Teilung mit WLAN | RAM ja, Funk nein |
| Joker per ESP-NOW | gleicher Kanal wie das WLAN nötig | nein |
| Joker per 433 MHz | Pulse mit 300–500 µs Breite dekodieren, braucht RMT-Empfang oder harte IRQs | **Ja**: in Python nicht machbar |
| PC-Simulator, Tests | gleiche Spiellogik auf dem PC | Ja |
| Update übers WLAN | Dateien oder ganze Firmware, 4 MB Flash | Ja |

**Socket-Rechnung:** ESP-IDF setzt `CONFIG_LWIP_MAX_SOCKETS` standardmäßig auf **10** (geprüft, Kconfig
ESP-IDF). Die MicroPython-Konfiguration für ESP32-C3 überschreibt diesen Wert nicht, sie setzt nur
`CONFIG_LWIP_MAX_ACTIVE_TCP=12` (geprüft, `sdkconfig.base` im MicroPython-Repo, Stand master). Bedarf im
Spiel: 1 Listen-Socket + 8 WebSocket + 1 DNS + 2–4 kurzlebige HTTP-Verbindungen = **12–14**. Das passt nicht
in 10. **Folge: Jede Option braucht einen eigenen Build mit z. B. 16 Sockets**, auch MicroPython. Der
Vorteil „fertige Firmware, nur Dateien hochladen“ gilt damit für die Firmware selbst nicht mehr, wohl aber
weiterhin für den Python-Code. (Ob der mDNS-Dienst einen eigenen Socket belegt: unsicher.)

**Hardware-Hinweis 433 MHz:** Laut [hardware-konzept.md](hardware-konzept.md) 5.5 sind alle GPIOs belegt.
Ein 433-MHz-Empfänger könnte nur an TXD (Pad J3, gibt beim Booten Daten aus) oder an INT/RXD (belegt durch
LIS2DH12). Das allein spricht schon gegen 433 MHz.

## 2. Option 1: MicroPython + Microdot + aioble

### 2.1 Speicher

| Messgröße | Wert | Status |
|---|---|---|
| Freier Heap ESP-IDF-Beispiel WLAN-STA auf C3 (IDF 5.5, ohne Python) | 219 KB | geprüft (Espressif ESP-Techpedia) |
| Freier Heap ESP-IDF-Beispiel WLAN+BLE (`bleprph_wifi_coex` 178 KB, „provision“ 126 KB; 205 KB gilt nur für reines BLE `bleprph`) | 126–178 KB | geprüft (korrigiert, siehe [analyse-funk-controller.md](analyse-funk-controller.md)) |
| Dasselbe mit Speicheroptimierung (IDF 5.2.2) | 178 → 248 KB | geprüft |
| Start-Heap MicroPython auf C3 (`MICROPY_GC_INITIAL_HEAP_SIZE`) | 64 KB, wächst bei Bedarf in weiteren Blöcken (Split-Heap) | geprüft (`mpconfigport.h`) |
| Bericht LOLIN C3 Mini, MicroPython 1.22.2: nach 40 KB eigener Daten und `import bluetooth` | GC gesamt 140 KB, **frei nur 17 KB** | geprüft (Issue #14293) |
| BLE-Start bei knappem Speicher | stürzte ab (Store access fault), seit März 2026 sauberer Fehler statt Absturz | geprüft (#14293, Fix b3d88cf) |
| NimBLE-Task-Stack in MicroPython | 6 KB, max. 4 BLE-Verbindungen | geprüft (`sdkconfig.ble`) |

Abschätzung für Louie: Von ca. 200 KB nach WLAN+BLE nimmt MicroPython 64–130 KB als Python-Heap. Für lwIP,
WLAN-Puffer und 8 TCP-Verbindungen bleiben **ca. 70–130 KB** im ESP-IDF-Heap (unsicher). Microdot,
aioble, Interpreter, Spielzustand und 8 WebSocket-Objekte im Python-Heap: ca. 50–80 KB (unsicher). **Das
geht vermutlich, aber knapp.** Das typische Fehlerbild ist nicht `MemoryError` in Python, sondern
`OSError: ENOMEM`/`ENOBUFS` aus dem IDF-Heap, obwohl `gc.mem_free()` noch genug anzeigt (geprüft, Issue
#7038, Maintainer-Antwort). Deshalb muss der Test **beide Heaps** messen (`gc.mem_free()` und
`esp32.idf_heap_info()`).

### 2.2 Funk

- **BLE passiv:** `aioble.scan(duration_ms, interval_us, window_us, active=False)` liefert Advertising-Daten
  asynchron (geprüft, aioble-Quelltext). BTHome-Parser in Python: ca. 50 Zeilen, unkritisch. Verbindungen
  zu Tastern sind nicht nötig, BTHome-Taster senden nur Advertising.
- **ESP-NOW:** Modul `espnow` plus `aioespnow` für asyncio vorhanden. Läuft parallel zum WLAN, aber
  Gegenstellen müssen auf dem Kanal des WLANs senden; im STA-Betrieb wechselt der Kanal mit dem Router.
  WLAN-Stromsparen macht den Empfang unzuverlässig (geprüft, MicroPython-Doku `espnow`).
- **433 MHz:** MicroPython stellt RMT **nur zum Senden** bereit („This code exposes the RMT TX feature“,
  geprüft, `esp32_rmt.c`). Pin-IRQs sind auf dem ESP32 nur „soft“ (kein `hard=True` im Port, geprüft
  `machine_pin.c`), Latenz 20–380 µs (geprüft, Forumsmessung, ältere Hardware). Bei Pulsbreiten von
  300–500 µs ist Dekodierung in Python **nicht zuverlässig machbar**. Ausweg nur über ein eigenes C-Modul
  (RMT-RX im C-Teil der Firmware) – möglich, aber dann wird C ohnehin gebraucht.

### 2.3 WebSocket, Latenz, GC

- Microdot läuft unter asyncio, ein Task pro Verbindung. 8 Clients sind ein RAM-, kein Logikproblem.
  Erfahrungsberichte nennen 6–7 WebSockets mit aktivem `gc.collect()` als machbar (unsicher, PyPI-Projekt,
  andere Bibliothek).
- **GC-Pausen:** Bei 64–130 KB Heap auf 160 MHz im einstelligen bis niedrigen zweistelligen ms-Bereich
  (unsicher). Joker-Budget: Ein Mensch nimmt bis ca. 150–200 ms keine Verzögerung wahr; Advertising-Abstand
  des Tasters, Funkzeit-Teilung und 50-ms-Spieltakt liegen zusammen bei ca. 100–250 ms (unsicher). **GC ist
  für Joker unkritisch**, solange Allokationen im Takt klein bleiben (vorallokierte Puffer, keine
  JSON-Neuerzeugung pro Client; ein JSON-String für alle 8).
- Motorsicherheit hängt nicht an Python: PWM erzeugt LEDC in Hardware, der Watchdog (`machine.WDT`)
  startet bei Hänger neu.

### 2.4 Frozen modules, Update

- Frozen modules (Bytecode im Flash) sparen RAM, weil Code nicht im Heap liegt (geprüft, MicroPython-Doku
  „manifest“). Da ohnehin ein eigener Build nötig ist, kostet das nichts extra.
- MicroPython hat eine OTA-Partitionstabelle für 4 MB: zwei App-Slots à **1,5 MB**, Rest Dateisystem
  (geprüft, `partitions-4MiB-ota.csv`). **Die Standard-Firmware
  MicroPython v1.29 ist bereits größer** (C3 1,61 MiB, C6 1,81 MiB, geprüft, siehe
  [analyse-funk-controller.md](analyse-funk-controller.md) 3b). Echtes OTA mit zwei Slots passt mit
  MicroPython also auf keinem der beiden Chips mit 4 MB. Es bleibt bei Stufe 1 aus software-konzept.md 8.3
  (Python-Dateien und Web-UI übers WLAN, MicroPython selbst per USB-C).

### 2.5 Risiken

1. IDF-Heap läuft unter Last leer (ENOMEM), nicht deterministisch, schwer zu debuggen.
2. Eigener Build nötig (ESP-IDF-Toolchain) – Mehraufwand einmalig, danach wie gewohnt.
3. Rechenzeit der Vorschau in Python (Gewitter-Modus mit Bot-Probe) blockiert die Ereignisschleife;
   Vorschau in Häppchen rechnen oder auf 5 Hz auflösen.
4. MicroPython-BLE auf C3 hatte Absturzfehler bei Speichermangel (behoben 2026, siehe oben). Version
   ≥ 1.29 verwenden.

## 3. Option 2: C/C++ (ESP-IDF oder Arduino-ESP32)

| Thema | Bewertung |
|---|---|
| RAM | 126–178 KB frei mit WLAN+BLE vor eigener Logik (geprüft, korrigiert); Spiellogik in C++ braucht nur wenige KB. ESPHome empfiehlt auf C3 trotzdem höchstens 5 BLE-Verbindungen (geprüft) – passives Scannen ist davon nicht betroffen. |
| Funk | Alles verfügbar: NimBLE (Scan, Verbindungen), ESP-NOW, RMT-Empfang für 433 MHz, Koexistenz-Einstellungen. |
| Webserver | `esp_http_server` mit WebSocket und `httpd_queue_work()` für asynchrones Senden an alle Clients (geprüft, IDF-Beispiel `ws_server`); `max_open_sockets` muss zu `LWIP_MAX_SOCKETS` passen (3 intern reserviert). Arduino: ESPAsyncWebServer, heute gepflegt unter ESP32Async (v3.12.1, Sept. 2026). |
| Reife | Höchste. Arduino-ESP32 3.3.12 (Sept. 2026), ESP-IDF v6.1 (Aug. 2026), NimBLE-Arduino 2.5.2 (Okt. 2026) (alle geprüft, GitHub-Releases). Captive-Portal-, OTA-, mDNS-Beispiele zahlreich. |
| Entwicklungstempo | Kompilieren + Flashen 20–60 s pro Zyklus (unsicher). Web-UI und Konfiguration bleiben Dateien im LittleFS, also ohne Flashen änderbar. |
| Simulator/Tests | Spiellogik als C++17-Bibliothek ohne Arduino-Header → am PC mit CMake bauen, Tests mit doctest/GoogleTest. PC-Simulator braucht einen eigenen Webserver (z. B. cpp-httplib oder Mongoose, der auch auf ESP32 läuft). Mehr Gerüst als in Python. |
| WASM | Kern per Emscripten nach WebAssembly → gleiche Vorschau im Browser möglich, aber Werkzeugkette zusätzlich. |
| OTA | Zwei App-Partitionen à ca. 1,6–1,9 MB + ca. 400 KB LittleFS passen in 4 MB, wenn keine Factory-Partition genutzt wird (geprüft als gängige Praxis, esp32.com-Thread; Firmwaregröße WLAN+BLE+Webserver ca. 1,2–1,6 MB, unsicher). Rollback über `esp_ota_mark_app_valid`. |
| Risiken | Speicherfehler (Pufferüberlauf, Use-after-free) in eigener C++-Logik; asynchrone Webserver-Callbacks sind fehleranfällig. Für einen Python-Bastler mittlere Lernkurve. |

## 4. Option 3: Rust

### 4.1 (a) `std` mit esp-idf-svc

- Rust über dem ESP-IDF: WLAN, NimBLE (Crate `esp32-nimble`), HTTP-Server mit WebSocket, mDNS, OTA (`EspOta`)
  – technisch alles, was C kann.
- **Aber:** Die `esp-idf-*`-Crates werden von der Community gepflegt; Espressif investiert „little to no paid
  developer time“ (geprüft, esp-idf-hal README / Rust-Book). Build kombiniert Cargo und CMake, erste Builds
  dauern lange, Fehler aus beiden Welten (unsicher, Erfahrungswert).
- Aktuell `esp-idf-svc` 0.53.0 (Sept. 2026, geprüft crates.io), also weiterhin vor 1.0.

### 4.2 (b) `no_std` mit esp-hal + Embassy + esp-radio

| Baustein | Stand Nov. 2026 | Status |
|---|---|---|
| `esp-hal` | 1.2.2, stabil seit 1.0 (Okt. 2025) – aber nur GPIO, UART, SPI, I²C, Zeit sind stabil, alles andere hinter `unstable` (LEDC, RMT, ADC) | geprüft |
| `esp-radio` (früher esp-wifi) | **1.0.0-beta.1** (beta.2 zurückgezogen), „nächstes Stabilisierungsziel“; WLAN STA/AP, BLE, ESP-NOW vorhanden, Feature `coex` als **unstable** markiert; braucht Allocator + `esp-rtos`, Optimierung O2/O3 | geprüft |
| BLE-Host | `trouble-host` 0.8.0 (über `bt-hci`), passiver Scan möglich | geprüft (Version), Scan-Reife unsicher |
| Webserver | `picoserve` 0.20.1 (axum-ähnlich, WebSocket-Callback) | geprüft |
| Captive DNS / mDNS | `edge-captive` / `edge-mdns` 0.8.0, no_std, ohne Allocator | geprüft |
| OTA | `esp-hal-ota` 0.7.2, C3 unterstützt, Rollback | geprüft |
| Toolchain C3 | RISC-V, normales stabiles Rust (`riscv32imc-unknown-none-elf`) | geprüft (esp-rs Book) |

Stärken: Kein FreeRTOS-Heap-Rätsel, Speicher wird zur Compile-Zeit sichtbar, async passt gut zu „8 Clients +
Scan + Spieltakt“. Die Spiellogik als `no_std`-Crate läuft **unverändert** auf dem PC (`cargo test`, Simulator
mit axum/tokio) und als **WebAssembly im Browser** – die beste Testbarkeit aller Optionen.

Schwächen: Genau die Teile, die Louie braucht (AP mit vielen Clients, BLE, Koexistenz), sind die
unfertigsten. Einen Fehler in der Koexistenz kann man hier nicht „nachschlagen“, es gibt wenig
Erfahrungsberichte mit SoftAP + BLE + 8 Clients (unsicher). Lernkurve (Ownership, Lifetimes, async ohne
Allocator, Embassy-Tasks) für einen Python-Bastler: steil, realistisch Wochen bis Monate bis zur
Produktivität (unsicher).

## 5. Option 4: Hybrid

| Variante | Idee | Bewertung |
|---|---|---|
| **H1: Kern in Rust, Firmware MicroPython** | Interpreter als Rust-Staticlib, als C-Modul in MicroPython eingebunden; dazu WASM im Browser | Technisch möglich, aber exotisch; zwei Werkzeugketten plus eigener Build. Lohnt nicht. (unsicher) |
| **H2: Kern in C++, Firmware C++, Vorschau per Emscripten** | Eine Implementierung für ESP, PC-Tests und Browser | Sauber, aber nur als Teil von Plan B sinnvoll. |
| **H3: Alles Python, Browser nutzt MicroPython-WebAssembly** | Derselbe `modes.py` läuft im Browser in MicroPython-WASM | `micropython.wasm` (1.29) ist 450 KB, **gzip ca. 195 KB** (geprüft, npm-Paket). Sprengt das 100-KB-Ziel des UI, ginge aber, wenn nur der Editor es nachlädt. Option für später. |
| **H4: Alles Python, Vorschau nur auf dem Server** | `POST /api/modes/preview` wie in modus-baukasten.md 2.8 | Eine Implementierung, kostet ESP-Rechenzeit. **Für V1 empfohlen.** |

Achtung: Der Web-PoC (`web/poc/index.html`) enthält bereits einen Schema-2-Interpreter in JavaScript. Das ist
eine **zweite Implementierung**, die mit der Firmware auseinanderlaufen wird. Für V1: Der JS-Interpreter
bleibt nur im PoC/Simulator, das echte UI holt die Vorschau vom Server (H4). Gemeinsame Testfälle (JSON-Modus
→ erwartete Kurve) im Repo verhindern Abweichungen, egal welche Sprache.

## 6. Externe Taster: Funkweg

| Kriterium | BLE BTHome passiv | ESP-NOW | 433 MHz |
|---|---|---|---|
| Fertige Taster | ja (Shelly BLU Button1, BTHome, AES-CCM-Verschlüsselung optional, Paket-ID gegen Doppelzählung) (geprüft) | nein, Selbstbau mit ESP + Batterie + Deep Sleep | ja, sehr billig |
| Zusatz-Hardware am Louie | keine | keine | Empfängermodul + GPIO (**keiner frei**) |
| Mit WLAN-STA | stabil (Y) | Empfang stabil (S), Kanal muss passen | unabhängig |
| Mit SoftAP + Clients | **C1: unterstützt, instabil** (geprüft) | mit aktivem BLE: Empfang nur im STA-Modus unterstützt (S) (geprüft) | unabhängig |
| Sicherheit | Verschlüsselung + Zähler | Verschlüsselung möglich | keine, Replay trivial |
| MicroPython | ja (aioble) | ja (espnow) | nein (nur mit C-Modul) |
| Latenz | Advertising-Burst beim Druck, „unter 1 s“ laut Hersteller (geprüft), real ca. 50–200 ms (unsicher) | wenige ms | wenige ms |

**Empfehlung:** BLE BTHome passiv. Taster werden im Admin-Bereich angelernt (MAC + optional Schlüssel) und
einem Platz zugeordnet. Scannen nur, wenn ein Modus mit Jokern läuft und mindestens ein Taster angelernt ist –
das spart Funkzeit für das WLAN. ESP-NOW nicht parallel zu BLE einplanen. 433 MHz streichen.

## 7. Bewertungsmatrix

Punkte 1 (schlecht) bis 5 (gut). Gewichte nach Projektzielen (Bastler, schnelles Entwickeln, Robustheit).

| Kriterium | Gewicht | MicroPython | C++ (Arduino/IDF) | Rust std | Rust no_std |
|---|---|---|---|---|---|
| RAM-Reserve | 3 | 2 | 5 | 4 | 4 |
| Funk (BLE, ESP-NOW, 433) | 2 | 3 (kein 433) | 5 | 4 | 3 (coex unstable) |
| Latenz Joker / Spieltakt | 1 | 4 | 5 | 5 | 5 |
| Robustheit / Watchdog | 3 | 3 | 4 | 4 | 3 (Funk-Beta) |
| Entwicklungstempo | 3 | 5 | 3 | 2 | 2 |
| Testbarkeit / PC-Simulator | 3 | 5 | 3 | 4 | 5 |
| Update übers WLAN | 1 | 4 (Dateien) | 5 (OTA) | 5 | 4 |
| Lernkurve (Python-Bastler) | 3 | 5 | 3 | 1 | 1 |
| Community / Beispiele | 2 | 3 | 5 | 2 | 3 |
| Risiko (Projekt bleibt stecken) | 3 | 3 | 4 | 2 | 2 |
| **Summe (gewichtet, max. 120)** | | **89** | **96** | **73** | **72** |

C++ liegt auf dem Papier knapp vorn. Der Abstand entsteht fast nur aus RAM-Reserve und Risiko, also genau aus
dem, was der Machbarkeitstest misst: Besteht MicroPython den Test, steigen dort RAM-Reserve auf 3 und Risiko
auf 4, die Summe auf **95** – gleichauf mit C++, bei klar besserem Tempo, Simulator und Lernkurve. Rust
verliert vor allem an Lernkurve und Reife des Funkteils; das kann sich mit `esp-radio` 1.0 ändern. Die
Entscheidung fällt deshalb durch die Messung, nicht durch die Tabelle.

## 8. Empfehlung und Machbarkeitstest

### 8.1 Empfehlung

1. **MicroPython (≥ 1.29) mit eigenem Build** bleibt Plattform, wenn der Test unten bestanden wird.
   Build-Änderungen: `CONFIG_LWIP_MAX_SOCKETS=16`, Microdot, aioble und `louie/core` als frozen modules,
   BLE-Logstufe niedrig, WLAN-Puffer nach Espressif-Leitfaden „Minimizing RAM Usage“ angepasst.
2. **433 MHz streichen**, BLE-BTHome als Taster-Funk, ESP-NOW optional nur ohne BLE.
3. **Plan B C++** (Arduino-ESP32 als Bibliothek, PlatformIO/pioarduino), wenn MicroPython an RAM oder
   Sockets scheitert, C++ aber nicht.
4. **Rust beobachten**: Neu bewerten, sobald `esp-radio` 1.0 erscheint und `coex` stabil ist.

Begründung: Es gibt noch keinen Firmware-Code; ein Wechsel kostet jetzt fast nichts. Darum wird nicht nach
Gefühl, sondern nach einer Messung an 1–2 Abenden entschieden. Die größte Unsicherheit (BLE + SoftAP) liegt im
Funkteil und betrifft alle Sprachen gleich; dafür lohnt sich ein Sprachwechsel nicht.

### 8.2 Aufbau (XIAO ESP32-C3)

- **Gerät A (Prüfling):** XIAO ESP32-C3 mit Testfirmware „louie-probe“: SoftAP (8 Clients erlaubt),
  Captive-DNS, mDNS, Microdot mit `/ws`, sendet 10×/s einen Zustand (ca. 250 Byte JSON) an alle Clients,
  passiver BLE-Scan, 50-ms-Spieltakt mit LEDC-PWM 20 kHz, Watchdog, Interpreter rechnet alle 30 s die
  Vorschau des Modus „Gewitter“ (modus-baukasten.md 6.2) mit Bot-Probe.
- **Gerät B (Tastensimulator):** zweiter XIAO, sendet alle 2 s ein BTHome-„press“-Advertising mit laufender
  Paket-ID (wie ein Shelly BLU Button) und setzt dabei einen GPIO. Gerät A setzt beim Erkennen einen GPIO.
  Beides mit Logikanalysator (oder dritter Board-Zeitstempel) messen. Zusätzlich 1 echter Shelly BLU Button.
- **Clients:** möglichst 8 echte Stationen (Handys, Tablets, alte Geräte) für das AP-Limit, plus ein
  PC-Skript, das zusätzlich WebSocket-Last erzeugt und Empfangszeitpunkte und Lücken protokolliert.
- **Referenz:** dieselbe Probe in C++ (Arduino-ESP32 + NimBLE-Arduino + ESPAsyncWebServer), ca. 1 Abend. Nur
  so lässt sich erkennen, ob ein Problem an MicroPython oder am Funkteil liegt.

### 8.3 Szenarien (je 2 h Dauerlauf)

| Nr. | Netz | BLE | Last |
|---|---|---|---|
| S1 | STA im Heimnetz | aus | 8 WS, 10/s |
| S2 | STA im Heimnetz | Scan passiv | 8 WS, 10/s, Taster alle 2 s |
| S3 | SoftAP, 8 Stationen | Scan passiv | wie S2 |
| S4 | SoftAP + STA (WLAN testen, software-konzept.md 3.3) | Scan passiv | 4 WS |
| S5 | wie S3, zusätzlich alle 10 s neue HTTP-Seitenaufrufe (Reload auf 2 Handys) | Scan passiv | Spitzen bei Sockets |

### 8.4 Messgrößen und Abbruchkriterien (MicroPython)

| Messgröße | Wie | Abbruch, wenn |
|---|---|---|
| Min. freier IDF-Heap / größter Block | `esp32.idf_heap_info(esp32.HEAP_DATA)` jede Sekunde loggen | < 30 KB frei oder größter Block < 8 KB |
| Min. freier Python-Heap | `gc.mem_free()` nach `gc.collect()` | < 20 KB |
| Fehler / Neustarts | Log, Reset-Grund | eine ENOMEM/ENOBUFS-Ausnahme oder ein Reset in 2 h |
| WebSocket-Zustellung | PC-Skript: Lücken > 300 ms, Anteil empfangener Zustände | < 98 % empfangen oder Lücke > 1 s |
| Joker-Erkennung STA (S2) | Gerät B vs. Gerät A, Zeitdifferenz | < 98 % innerhalb 300 ms |
| Joker-Erkennung SoftAP (S3) | wie oben | < 90 % innerhalb 300 ms – **nur Abbruch, wenn C++-Referenz deutlich besser ist** (sonst Funkgrenze) |
| Spieltakt-Jitter | Zeitstempel im 50-ms-Takt | > 100 ms Ausreißer |
| GC-Pause | `time.ticks_us()` um `gc.collect()` | > 30 ms |
| Vorschau „Gewitter“ | Rechenzeit, Speicherspitze | > 1,5 s oder > 30 KB |
| Firmwaregröße | Build-Ausgabe | > 1,5 MB (dann kein OTA, nur Datei-Update) – kein Abbruch |
| Captive Portal | iOS + Android | erscheint nicht – sprachunabhängig, eigenes Thema |

### 8.5 Entscheidung

| Ergebnis | Entscheidung |
|---|---|
| MicroPython besteht alle Kriterien | **MicroPython**, Konzept wie gehabt |
| MicroPython scheitert an Heap/Sockets/Resets, C++ besteht | **C++ (Plan B)** |
| Beide scheitern an Joker-Erkennung im SoftAP (S3) | Funkgrenze: BLE-Taster nur im STA-Betrieb anbieten oder Zustandsrate im Hotspot auf 5/s senken; **MicroPython bleibt** |
| Später wird 433 MHz doch Pflicht | C-Modul für RMT-RX in den eigenen MicroPython-Build, oder C++ |
| Beide scheitern an Heap | Clients auf 6 begrenzen, Zustand als Binär-/Delta-Nachricht, dann erneut testen |

## 9. Auswirkungen auf die Architektur (software-konzept.md 8)

- **Schichten bleiben** (`hal/`, `core/`, `net/`, `web/`, `store`). Neu:
  - `hal/buttons_ble.py` (BTHome-Scan, Parser, Paket-ID-Filter) und `hal/sim.py` mit simuliertem Taster
    (Knopf im Simulator-UI).
  - In `core/game.py` eine gemeinsame Joker-Eingabe: `joker(seat, kind, source)` mit `source` = `phone` |
    `button`. Sperre (`lock_s`), Konten und Fiesheit wirken gleich, die Spiellogik weiß nichts vom Funk.
  - `net/` schaltet den BLE-Scan nur ein, wenn nötig (Funkzeit).
- **Protokoll bleibt** (software-konzept.md 7). Erweiterungen, nicht Umbau:
  - `GET/POST/DELETE /api/admin/buttons` (anlernen: „jetzt Taster drücken“, Platz zuordnen).
  - WebSocket-Ereignis `{"t":"event","kind":"joker","seat":2,"src":"button"}`; im Zustand pro Spieler
    optional `"button":{"rssi":-71,"battery":90}`.
- **Vorschau:** bleibt `POST /api/modes/preview` (H4). Gemeinsame Golden-Tests (`tests/modes/*.json` →
  erwartete Kurve) gelten für jede Implementierung, auch für den JS-Interpreter im PoC und einen späteren
  C++-/Rust-Kern.
- **Bei Plan B (C++)** bleiben Web-UI, Protokoll, JSON-Formate (Modi, `config.json`) und Golden-Tests
  unverändert. `core/` wird nach C++ portiert, der PC-Simulator wird dann ein natives Programm mit
  eingebettetem Webserver; die Python-Version kann bis dahin als Referenz-Simulator weiterlaufen.
- **Updates (8.3):** bei MicroPython wie bisher (Dateien), echtes OTA passt mit MicroPython nicht (Firmware > 1,5 MB, geprüft); bei C++
  von Anfang an zwei App-Partitionen.

## 10. Quellen

- Espressif, RF-Koexistenz ESP32-C3 (IDF v6.1, Tabelle BLE × SoftAP = C1, ESP-NOW RX = S):
  https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/coexist.html
- Espressif ESP-Techpedia, RAM-Verbrauch (205/219 KB, 178→248 KB):
  https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/ram-usage.html
- ESP-IDF lwIP Kconfig (`LWIP_MAX_SOCKETS` default 10):
  https://github.com/espressif/esp-idf/blob/v5.4/components/lwip/Kconfig
- ESP-IDF HTTP-Server/WebSocket, `max_open_sockets`:
  https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/protocols/esp_http_server.html
  und Forum https://esp32.com/viewtopic.php?p=82482
- MicroPython ESP32-Port: `mpconfigport.h` (Heap 64 KB), `boards/sdkconfig.base`, `boards/sdkconfig.ble`,
  `esp32_rmt.c` (nur TX), `machine_pin.c`, `partitions-4MiB-ota.csv`:
  https://github.com/micropython/micropython/tree/master/ports/esp32
- MicroPython Issue #14293 (C3 BLE-Absturz, Heap-Zahlen, Fix 2026):
  https://github.com/micropython/micropython/issues/14293
- MicroPython Issue #7038 (ENOMEM aus FreeRTOS-Heap bei BLE + Netzwerk):
  https://github.com/micropython/micropython/issues/7038
- MicroPython `espnow`-Doku: https://docs.micropython.org/en/latest/library/espnow.html
- aioble: https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble
- Pin-IRQ-Latenz ESP32 (Forum): https://forum.pycom.io/post/5658
- MicroPython WebAssembly (npm): https://www.npmjs.com/package/@micropython/micropython-webassembly-pyscript
- esp-hal 1.0 Ankündigung: https://developer.espressif.com/blog/2025/10/esp-hal-1/
- esp-radio Doku (coex unstable, Heap-Anforderungen):
  https://docs.espressif.com/projects/rust/esp-radio/1.0.0-beta.2/esp32c3/esp_radio/index.html
- Versionen laut crates.io (abgefragt 2026-11-02): esp-radio, esp-hal, trouble-host, picoserve, edge-captive,
  edge-mdns, esp-hal-ota, esp-idf-svc – https://crates.io
- esp-idf-hal (Community-Status): https://github.com/esp-rs/esp-idf-hal ; Rust-Book:
  https://docs.espressif.com/projects/rust/book/
- picoserve: https://docs.rs/crate/picoserve/latest ; edge-net: https://docs.rs/crate/edge-net/0.15.0
- esp-hal-ota: https://docs.rs/crate/esp-hal-ota/0.7.1
- ESPHome Bluetooth Proxy (C3: max. 5 Verbindungen, passives Scannen):
  https://www.esphome.io/components/bluetooth_proxy.html
- Shelly BLU Button (BTHome, Paket-ID, Ereignisse): https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/button
- 4-MB-Partitionierung C3 mit OTA (Forum): https://esp32.com/viewtopic.php?p=128137
- Releases (GitHub, abgefragt 2026-11-02): MicroPython v1.29.0, Microdot v2.7.0, Arduino-ESP32 3.3.12,
  ESP-IDF v6.1, NimBLE-Arduino 2.5.2, ESPAsyncWebServer v3.12.1
