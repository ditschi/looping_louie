# Hardware-Konzept: Looping Louie WLAN-Upgrade

Stand: 2026-10-31 · Status: Entwurf, Projektgerüst und Bauteilauswahl stehen

## 1. Ziel

Ein Nachrüst-Bausatz, der **ohne Löten** in das Batteriefach von Looping Louie (und Loopin' Chewie)
eingesetzt wird und das Spiel per **Web-UI vom Handy** steuerbar macht.

Anforderungen:

- **Original-Hebel bleibt** und ist der einzige Bedienknopf am Spiel: Start/Stopp der Runde
  (und Aufwecken der Elektronik, siehe 5.3).
- Elektronik ist nach dem Aufwecken **dauerhaft aktiv** und liefert einen Webserver aus,
  unabhängig davon, ob gerade gespielt wird.
- Spielmodus kann **nicht während einer laufenden Runde** gewechselt werden.
- Mehrere Clients gleichzeitig: Spielleiter + Spieler (Boosts von ausgeschiedenen Spielern usw.).
- Eigene Spielmodi anlegen und unter einem Namen speichern.
- Versorgung über **1S-LiPo mit USB-C-Ladung** statt 9-V-Block.
- **Eine Hauptplatine im AA-Format für alle Modelle**, nur der mechanische Adapter unterscheidet sich.
- Offen (KiCad), nachbaubar, bei JLCPCB o. Ä. bestückt bestellbar → verschenkbar.

## 2. Unterstützte Modelle

| Modell | Batteriefach | Nennspannung Motor | Spieler |
|---|---|---|---|
| Looping Louie alt (Milton Bradley) | 1× Baby (C), offenes Fach ohne Deckel, Blech auf einer Seite, Feder auf der anderen | 1,5 V | 4 |
| Looping Louie neu (Hasbro, kleiner) | 2× AA, zwei getrennte Kammern | 3 V | 4 |
| Loopin' Chewie | 2× AA (Annahme; falls nicht, wird Chewie nicht unterstützt) | 3 V | 3 |

Original-Schaltung: Batteriefach → Hebel → Motor. Im alten Modell nachweislich **nur Leitungen**,
kein Kondensator, keine Diode. Kein Regler, kein Rückwärtslauf.

## 3. Systemübersicht

```
        ┌──────────────────── Looping Louie (unverändert) ────────────────────┐
        │   Kontakt 1 ──── Hebel ──── Motor ──── Kontakt 2                    │
        └──────┬───────────────────────────────────────┬──────────────────────┘
               │                                       │
   ┌───────────┴───────────────┐            (2× AA: über Fachbrücke
   │ Platine A  (AA-Format)    │             und Platine B = Brücke)
   │  ESP32-C3 + Antenne       │                       │
   │  H-Brücke DRV8833         │───────────────────────┘
   │  3,3-V-Regler             │
   │  Hebel-Erkennung          │
   │  Puffer-Kondensator       │
   └───────────┬───────────────┘
               │ Kabel: VSYS, GND, USB D+, USB D−   (Flachband, außen oder innen verlegt)
   ┌───────────┴───────────────┐
   │ Ladeplatine (extern)      │
   │  USB-C, Laderegler,       │
   │  Power-Path, Akkuschutz   │──── JST ──── 1S-LiPo
   └───────────────────────────┘
```

## 4. Baugruppen

### 4.1 Platine A: Hauptplatine im AA-Format

**Vorgabe ist allein die Größe einer AA-Zelle** (Ø 14,5 × 50,5 mm). Dass das ins Fach passt, ist
bekannt; der *Salto Sammy* zeigt, dass Elektronik in diese Form passt.

- Platine **46 × 13,5 mm, 0,8 mm dick** (Startwerte in `hardware/scripts/board_outline.py`).
  Die Breite gibt das ESP32-C3-MINI-1 vor (13,2 mm). An den Enden bleiben je ca. 2 mm für die
  Kontakte (Mechanik offen).
- **Bauhöhe bei einseitiger Bestückung**: Die Platine liegt leicht unter der Mitte der AA-Hülle
  (Oberseite ca. 0,5 mm über der Mitte). Dann passt das Modul (13,2 × 2,4 mm) mit ca. 0,1 mm Luft
  an den Ecken. Schmale Bauteile (≤ 4 mm breit) dürfen bis ca. 6 mm hoch sein. Die Höhe ist also
  kein Problem, **knapp ist die Fläche**.

#### Bestückungsstrategie (in dieser Reihenfolge versuchen)

1. **Einseitig bestückt**: alle Bauteile oben, Platine vom Hersteller fertig bestückt.
2. **Oben bestückt, unten Handlöten**: Hersteller bestückt die Oberseite; auf der Unterseite liegen
   nur gut von Hand lötbare Teile (0603 und größer, keine Fine-Pitch-ICs, keine Pads unter dem
   Bauteil). Die Platine wird trotzdem beidseitig gefertigt, nur einseitig bestückt.
3. **Beidseitig bestückt**: letzter Ausweg (teurer, nicht bei jedem Hersteller günstig).

**Ergebnis (2026-11-01):** Mit 0603 passt Weg 1 nicht, Weg 2 passt. Aus Kostengründen gewählt:
**Weg 1b – einseitig mit 0402-Passiven und Lötpads statt Stecker** (passt, zu ca. 95 % geroutet).
Platine B bleibt eine reine Brücke. Details und Zahlen: [offene-punkte.md](offene-punkte.md).

Bauteile sind so gewählt, dass alle drei Wege gehen: kleinste Bauform 0603, ICs mit Beinchen
(SOT-23, HTSSOP), gängige Teile mehrerer Hersteller (siehe `hardware/bom/teile.csv`).
- **Die beiden Enden sind direkt die H-Brücken-Ausgänge** (OUT1 / OUT2). Deshalb ist die
  Einbaurichtung egal; „vorwärts“ wird einmalig in der Software kalibriert.
- Inhalt: ESP32-C3-MINI-1, DRV8833, 3,3-V-LDO, Polymer-Puffer-Kondensator, Hebel-Erkennung,
  Akkuspannungs-Teiler, Status-LED, Testpunkte, Lötpads oder Mini-Stecker (z. B. JST-SH) fürs Kabel.
- Layout: H-Brücke und Puffer am einen Ende, ESP-Modul mit Antenne am anderen, keine Massefläche
  unter der Antenne.

### 4.2 Platine B: Brücke (nur bei 2× AA)

- Reine Kupferbrücke oberes ↔ unteres Ende im AA-Format, keine Bauteile, sehr billig.
- Motorstrom läuft `Kontakt 1 → A → Fachbrücke → B → Kontakt 2`.
- **Reserve:** Reicht auch die beidseitige Bestückung von A nicht, ziehen Puffer-Kondensator und
  Kabelanschluss auf B um. Dann braucht es 2–3 Adern zwischen A und B über die Trennwand der
  Kammern; notfalls dafür etwas Plastik an der Trennwand wegschneiden (akzeptabel).
- Im Reservefall kommen beim alten Modell **beide Platinen in die C-Hülse** (siehe 6).
  Verworfen: eine breitere Sondervariante von A für die C-Hülse. Das wäre ein zweites
  Platinendesign ohne Vorteil, da A und B ohnehin in die Hülse passen.

### 4.3 Ladeplatine (extern)

- USB-C-Buchse, Laderegler mit **Power-Path** (z. B. BQ24072), damit man beim Laden spielen kann.
  Einfache Alternative: TP4056 + DW01.
- JST-PH-Buchse für den LiPo, optional Schiebeschalter als Transport-Aus.
- USB D+/D− werden zur Platine A durchgereicht → **eine Buchse zum Laden und Flashen**.
- Kabel zu A: 4 Adern (VSYS, GND, D+, D−), z. B. dünnes Flachband. Wird je nach Spiel außen
  am Gehäuse entlang geführt oder innen in der Basis verstaut.
- Akku und Ladeplatine sitzen in der Basis oder in einem kleinen externen Gehäuse.

## 5. Schaltungsdetails

### 5.1 Motorstufe

- **DRV8833** (2,7–10,8 V), beide H-Brücken parallel: laut Datenblatt bis ca. 3 A RMS / 4 A Spitze.
- **Shunt 0,1 Ω an AISEN/BISEN**: Der DRV8833 begrenzt damit selbst auf ca. 2 A (200 mV / 0,1 Ω),
  schützt also Motor, Akku und Platine. Gleichzeitig wird die Shunt-Spannung über ein RC-Filter
  vom ADC gemessen: Motorstrom für Anlauf-Erkennung und Hebel-Erkennung während der Fahrt.
- Versorgung VM direkt aus VSYS (LiPo 3,0–4,2 V).
- **PWM ca. 20 kHz**, damit nichts pfeift. Der alte Code nutzte 1 kHz, das ist hörbar.
- Rückwärtslauf und aktives Bremsen möglich.
- Rampen in der Firmware gegen Spannungseinbrüche (Lehre aus *MADXhh/LoopingLouieAdvanced*:
  sonst Brownout und Neustart bei Richtungswechsel).
- **Ströme müssen für das Layout nicht gemessen werden:** Bei 20 kHz glättet die Motorwicklung
  den Strom; der Mittelwert folgt der effektiven Spannung. Mit Tastgrad-Begrenzung und Rampen
  sieht der Motor etwa die Ströme wie an seiner Nennspannung. Auslegung mit Reserve
  (DRV8833 parallel, breite Bahnen auf Brücke und Kontakten). Eine Messung dient später nur
  zum Festlegen von Turbo-Grenze und Akkugröße.

### 5.2 Hebel-Erkennung über den Motorstromkreis

Der Original-Hebel liegt in Reihe mit dem Motor. Ist die H-Brücke im Sleep (Ausgänge hochohmig):

```
3,3 V ──[100k]──┬── OUT1 ── Kontakt 1 ── Hebel ── Motor (wenige Ω) ── Kontakt 2 ── OUT2 ──[10k]── GND
                │
           SENSE (GPIO, über Schutzwiderstand)
```

- Hebel **offen**: SENSE ≈ 3,3 V → „Stopp“
- Hebel **zu**: SENSE ≈ 0,3 V (Teiler 100k/10k über die Motorwicklung) → „Start“
- Liefert gleichzeitig: „Motor angeschlossen?“
- Während der Motor läuft, ist SENSE nicht aussagekräftig. Dann wird der Hebel per **Strom**
  erkannt: Bei offenem Hebel fließt trotz PWM kein Strom durch den Shunt (siehe 5.1).
- SENSE geht über einen Schutzwiderstand (100k) an den GPIO, weil OUT1 beim Fahren bis zur
  Akkuspannung (4,2 V) hochgeht.
- 10k nach GND an OUT2 kosten beim Rückwärtsfahren ca. 0,4 mA, vernachlässigbar.
- Altes Modell hat keine Entstörbauteile und keine Diode → Prinzip ohne Einschränkung nutzbar.
  Beim neuen Modell mögliche Entstörbauteile stören die DC-Messung nicht; eine Diode in Reihe
  wäre ein Problem (beim ersten neuen Modell prüfen).

Dass dieses Prinzip funktioniert, zeigt der *Salto Sammy Pro*: Dort wählt man den Modus durch
mehrfaches Umlegen des Original-Hebels.

### 5.3 Energiesparen und Aufwecken (kein extra Hauptschalter)

- Nach einstellbarer Leerlaufzeit (z. B. 15 min ohne Spiel und ohne Client): **Deep Sleep**.
  DRV8833 in Sleep, LDO mit geringem Ruhestrom → einige µA bis wenige zehn µA.
- **Aufwecken durch Umlegen des Louie-Hebels**: SENSE liegt auf einem Pin, der den ESP32-C3 aus
  dem Deep Sleep weckt (GPIO0–5).
- Nach dem Aufwecken startet zuerst das WLAN, die Runde erst beim nächsten Umlegen bzw. per
  Web-UI-Freigabe. Wie genau, entscheiden wir beim Software-Konzept.

### 5.4 Stromversorgung

- **1S-LiPo** 3,0–4,2 V mit Schutzschaltung, Größe nach Platz (z. B. 1000–2000 mAh).
- **Akkuspannung messen** (Spannungsteiler an ADC). Damit wird die Motorspannung unabhängig
  vom Ladezustand konstant geregelt: `duty = U_soll / U_akku`.
- Unterspannung: Spiel stoppen und im Web-UI warnen, bevor der Akkuschutz abschaltet.

### 5.5 Mikrocontroller: ESP32-C3

- ESP32-C3-MINI-1: 13,2 × 16,6 × 2,4 mm, Antenne integriert, bei JLCPCB bestückbar.
- **Native USB** (GPIO18/19): Flashen und Debug ohne USB-Seriell-Wandler.
- Updates später per WLAN (OTA).
- Pinbelegung (Stand Schaltplan `hardware/main-board/louie-main.kicad_sch`):

| GPIO | Netz | Funktion |
|---|---|---|
| IO0 | VBAT_ADC | ADC Akkuspannung (Teiler 470k/470k) |
| IO1 | ISEN_ADC | ADC Motorstrom (Shunt über RC-Filter) |
| IO2 | – | Strapping-Pin, 10k Pull-up, sonst frei |
| IO3 | SENSE | Hebel-Erkennung, Deep-Sleep-Wake |
| IO4 | MOT_IN1 | DRV8833 AIN1+BIN1 (PWM) |
| IO5 | MOT_IN2 | DRV8833 AIN2+BIN2 (PWM) |
| IO6 | MOT_nSLEEP | DRV8833 Sleep (low = aus) |
| IO7 | MOT_nFAULT | DRV8833 Fehler (Open Drain, interner Pull-up) |
| IO8 | – | Strapping-Pin, 10k Pull-up, sonst frei |
| IO9 | BOOT | Testpad; beim Reset auf GND = Download-Modus |
| IO10 | LED | Status-LED über 1k |
| IO18/IO19 | USB_D−/USB_D+ | Native USB über das Kabel zur Ladeplatine |
| RXD0/TXD0 | RXD/TXD | Testpads (serielle Konsole, Reserve) |

## 6. Mechanik und Adapter

| Modell | Platine A | Platine B | Adapter |
|---|---|---|---|
| 2× AA (neu, Chewie) | direkt in Kammer 1 | direkt in Kammer 2 (Brücke) | keiner; Kabel am Deckel vorbei |
| 1× C (alt) | in 3D-gedruckter C-Hülse | entfällt (im Reservefall ebenfalls in der Hülse, Brücke ungenutzt) | Hülse Ø 26 × 50 mm |

- Reservefall A + B in der C-Hülse: beide Platinen übereinander mit ca. 10 mm Abstand
  (je ±5 mm von der Mitte). Dort ist die Hülse noch ca. 24 mm breit, je Platine 4–5 mm
  Bauhöhe → passt mit Reserve. Gleiche Platinen und gleiches Kabel wie bei 2× AA.

- C-Hülse: Platine A sitzt mittig, an den Enden flache Kontaktflächen. Gegenüber liegen im Fach
  ein flaches Blech und eine Feder; der Pluspol-Nippel muss nicht nachgebildet werden, sofern das
  Blech flach anliegt. C-Zelle und AA-Zelle sind fast gleich lang (50 vs. 50,5 mm), es braucht
  also keine Längenüberbrückung.
- Altes Modell hat keinen Deckel → Kabel kommt einfach oben aus dem Fach.

## 7. Software (Kurzüberblick, Details in [software-konzept.md](software-konzept.md))

- Firmware: **MicroPython + Microdot** (asynchroner Webserver, WebSockets) als Empfehlung,
  da das bestehende Projekt MicroPython nutzt. Alternative: Arduino/PlatformIO mit
  ESPAsyncWebServer. Entscheidung offen.
- WLAN: bekanntes Netz, sonst eigener Access Point (vorhanden in `hardware/wifi.py`),
  dazu Captive Portal.
- Rollen: Spielleiter (wählt Modus, startet Freigabe, markiert ausgeschiedene Spieler),
  Spieler (Boosts usw.).
- Spielmodi als JSON im Flash, eigene Modi anlegen und benennen.
- Modus-Wechsel gesperrt, solange der Hebel auf „an“ steht bzw. eine Runde läuft.
- **Modellprofile**:

| Profil | U_nenn | 100 % entspricht | Turbo-Grenze (Vorschlag) | Spieler |
|---|---|---|---|---|
| Louie alt | 1,5 V | 1,5 V Motorspannung | 2,5 V | 4 |
| Louie neu | 3,0 V | 3,0 V | 4,0 V | 4 |
| Chewie | 3,0 V | 3,0 V | 4,0 V | 3 |

Die Turbo-Grenzen sind Schätzwerte und werden im Betrieb festgelegt.

## 8. Offene Punkte

- [ ] Funktest: ESP32-C3-Board mit Metallfeder vor der Antenne ins Fach legen, RSSI prüfen
- [ ] Neues Modell: prüfen, ob eine Diode in Reihe liegt (Hebel-Erkennung)
- [ ] Kontakte an den Platinenenden und Halt der Platine im AA-Fach (Halbschale?)
- [ ] Teile der Ladeplatine mit Status „zu prüfen“ in `teile.csv` bestätigen
- [ ] Lizenz für Hardware und Firmware festlegen
- [ ] Strapping-Pins IO2/IO8/IO9 gegen das ESP32-C3-Datenblatt prüfen (Pull-ups nötig?)
- [ ] AP2112K bei leerem Akku: Dropout ca. 250 mV bei 600 mA → unter ca. 3,5 V Akku sinkt 3V3 leicht; ESP32-C3 läuft ab 3,0 V
- [ ] Optional: Motorstrom messen (Turbo-Grenze, Akkugröße)
- [ ] Optional: *Salto Sammy Pro* als Referenz kaufen (Kontaktmechanik)

## 9. Nächste Schritte

1. Steckbrett-Prototyp: fertiges ESP32-C3-Board (z. B. Seeed XIAO ESP32-C3) + DRV8833-Modul +
   LiPo, inklusive Hebel-Erkennung und Deep-Sleep-Wake, am alten Modell.
2. Software-Konzept und neues Firmware-Gerüst auf dem Prototyp.
3. KiCad: Schaltplan und Layout von Platine A, Platine B, Ladeplatine; 3D-Modell der C-Hülse.

## Anhang A: Marktrecherche (Stand 2026-10)

Kommerzielle Module für das Batteriefach (alle ohne WLAN/App, nicht programmierbar):

- [Salto Sammy](https://www.saltosammy.de/produkt/salto-sammy-tuning-modul/): zwei Platinen in
  AA-Form (eine Brücke, eine Elektronik), 9-V-Block extern, zufällige Flugprofile, ca. 13,50 €.
- [Salto Sammy Pro](https://www.saltosammy.de/produkt/salto-sammy-pro/): zusätzlich rückwärts,
  Modus-Wahl über den Original-Hebel (1×/2×/3× schalten), ca. 17–25 €.
- Loopomator (Blasterparts): passt laut Hersteller für Louie und Chewie, 4× AA, ca. 15–19 €.
- CrazyLoops: eBay, Details unbekannt.

Open-Source-Projekte (Auswahl):

- [KevinSwayzee/looping_louie](https://github.com/KevinSwayzee/looping_louie): ESP32 + L293D,
  Web-UI über Raspberry Pi und MQTT, gute Sicherheitslogik (Watchdog, Rampen).
- [MADXhh/LoopingLouieAdvanced](https://github.com/MADXhh/LoopingLouieAdvanced) (MIT):
  ESP32, zufällige Zustände, Rampen gegen Brownout.
- [AimoLeffers/looping_louie_plus](https://github.com/AimoLeffers/looping_louie_plus) (GPL-3):
  ATtiny85 + MOSFET, alles in der Basis, Original-Schalter bleibt.
- [XPerianer/Looping_Louie_EV](https://github.com/XPerianer/Looping_Louie_EV) (GPL-3):
  Boost-Knöpfe pro Spieler, Spielmodi als Plugins.

Gefunden wurde **kein** Projekt mit WLAN-Web-UI direkt auf dem ESP (ohne Pi), mehreren
Rollen/Clients, eigenen Spielmodi und offenen KiCad-Daten für einen Batteriefach-Einsatz.

## Anhang B: Alter Projektstand (Tag `v1-legacy`)

- Hardware (Fritzing, `pcb/LoopingLouie-pcb.fzz`): Wemos D1 mini (ESP8266), N-MOSFET als
  Low-Side-Schalter + Freilaufdiode (nur vorwärts), 5-V-Schaltregler, 2 Schalter, 2 LEDs, Poti.
  Versorgung 9-V-Block. KiCad-Projekt praktisch leer.
- Software (MicroPython): WLAN mit AP-Fallback, Motor-PWM mit Rampe, Taster, LED, Timer
  funktionieren. Spiellogik (`game/`) und Web-UI (`webinterface/`) unfertig.
- PWM-Begrenzung für den 1,5-V-Motor am 9-V-Block: `MIN_SPEED = 100`, `MAX_SPEED = 200`
  (von 1023) in `looping_louie/webinterface/chatgpt.py` (im Tag `v1-legacy`).
