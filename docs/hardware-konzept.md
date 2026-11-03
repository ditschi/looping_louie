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
   │  ESP32-C6 + Antenne       │                       │
   │  H-Brücke DRV8833         │───────────────────────┘
   │  3,3-V-Regler             │
   │  Hebel-Erkennung          │
   │  Puffer-Kondensator       │
   └───────────┬───────────────┘
               │ Kabel: VSYS, D+, D−, GND (4 Adern, siehe ladeplatine.md)
   ┌───────────┴───────────────┐
   │ Ladeplatine (AA / Basis)  │
   │  USB-C, Laderegler,       │
   │  Power-Path, Akkuschutz   │──── JST ──── 1S-LiPo
   └───────────────────────────┘
```

## 4. Baugruppen

### 4.1 Platine A: Hauptplatine im AA-Format

**Vorgabe ist allein die Größe einer AA-Zelle** (Ø 14,5 × 50,5 mm). Dass das ins Fach passt, ist
bekannt; der *Salto Sammy* zeigt, dass Elektronik in diese Form passt.

- Platine **46 × 13,5 mm, 0,8 mm dick, 4 Lagen** (Entscheidung 2026-11-03): Lagenaufbau JLC-Standard
  **JLC04081H-3313** (0,8 mm, außen 1 oz, innen 0,5 oz); L1 Bauteile/Signale, L2 (In1) durchgehende GND-Lage,
  L3 (In2) Signale, L4 Lötpads/Signale; Regeln 0,15/0,15 mm, Via 0,3/0,5 mm. Vollständig geroutet (0 offen);
  die 2-Lagen-Variante blieb bei 13 offenen Verbindungen und ist verworfen (Details:
  [hauptplatine-c6.md](hauptplatine-c6.md) Kapitel 11). Maße in `hardware/scripts/board_outline.py`.
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
**Weg 1b – einseitig mit 0402-Passiven und Lötpads statt Stecker** (passt; auf 4 Lagen vollständig geroutet).
Platine B bleibt eine reine Brücke. Details und Zahlen: [offene-punkte.md](offene-punkte.md).

Bauteile sind so gewählt, dass alle drei Wege gehen: kleinste Bauform 0603, ICs mit Beinchen
(SOT-23, HTSSOP), gängige Teile mehrerer Hersteller (siehe `hardware/bom/teile.csv`).
- **Die beiden Enden sind direkt die H-Brücken-Ausgänge** (OUT1 / OUT2). Deshalb ist die
  Einbaurichtung egal; „vorwärts“ wird einmalig in der Software kalibriert.
- Inhalt (Stand C6-Umbau, Bauteilliste in 5.5): ESP32-C6-MINI-1, DRV8213, 3,3-V-LDO, USB-C mit ESD und
  Power-Path, 2 × 47 µF Puffer, Hebel-Erkennung, Spannungsteiler, Status-LED, LIS2DH12 (optional),
  Lötpads für Kabel, Zelle, I²C und Service.
- Layout: H-Brücke und Puffer am einen Ende, ESP-Modul mit Antenne am anderen, auf keiner der vier Lagen
  Kupfer unter der Antenne.

### 4.2 Platine B: Brücke (nur bei 2× AA)

- Reine Kupferbrücke oberes ↔ unteres Ende im AA-Format, keine Bauteile, sehr billig.
- **Entfällt, wenn die Ladeplatine hochkant in Fach 2 steckt** – sie hat dieselbe Brücke eingebaut.
- Motorstrom läuft `Kontakt 1 → A → Fachbrücke → B → Kontakt 2`.
- **Reserve:** Reicht auch die beidseitige Bestückung von A nicht, ziehen Puffer-Kondensator und
  Kabelanschluss auf B um. Dann braucht es 2–3 Adern zwischen A und B über die Trennwand der
  Kammern; notfalls dafür etwas Plastik an der Trennwand wegschneiden (akzeptabel).
- Im Reservefall kommen beim alten Modell **beide Platinen in die C-Hülse** (siehe 6).
  Verworfen: eine breitere Sondervariante von A für die C-Hülse. Das wäre ein zweites
  Platinendesign ohne Vorteil, da A und B ohnehin in die Hülse passen.

### 4.3 Ladeplatine

Ausgearbeitet in [ladeplatine.md](ladeplatine.md) (Schaltung, Layout, Halter, **Verdrahtungsbild**).

- **AA-Format** (46 × 12,5 × 1,6 mm). Steckt **hochkant** im zweiten AA-Fach und übernimmt dort die
  Brücke; die liegende USB-C-Buchse an der Längskante zeigt dann nach oben aus dem Fach.
  Alternativ flach in einem Halter in der Basis, Buchse durch ein Loch in der Wand.
- MCP73831 (500 mA) mit **Load-Sharing** (Schottky + P-MOSFET, Microchip AN1149): spielen beim Laden.
- ESD-Schutz USBLC6-2SC6, Ladeanzeige-LED, JST-PH und Lötpads für den Akku.
- ~~USB D+/D− werden zur Platine A durchgereicht~~ – entfällt mit der C6-Hauptplatine: Flashen nur über J4
  auf A, die USB-Buchse der Ladeplatine dient nur zum Laden (hauptplatine-c6.md, Kapitel 8).
- Kabel zu A: 2 Adern (VSYS → J1-1 BAT_IN, GND → J1-4); J1-2/3 sind ohne Netz.
- Der Akku sitzt in der Basis.

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

### 5.5 Mikrocontroller: ESP32-C3 → **Wechsel auf ESP32-C6** (Entscheidung 2026-11-02)

> **Der ESP32-C3 ist verworfen.** Neu ist das **ESP32-C6-MINI-1** (gleiche Größe 13,2 × 16,6 mm, integrierte
> Antenne). Gründe: etwa doppelt so viel freier RAM mit WLAN + BLE (BTHome-Taster in V1), 22 statt 15 GPIOs
> (8 frei statt keinem), ADC bis 3,3 V, Wecken aus LP-GPIOs, 802.15.4 (Zigbee/Thread) als Option für später;
> der C3-MINI-1-N4 ist bei LCSC als NRND markiert. Mehrkosten ca. +1 USD pro Board. Details:
> [analyse-funk-controller.md](analyse-funk-controller.md) (3b) und [hauptplatine-c6.md](hauptplatine-c6.md)
> (Umbau, Pinbelegung, Flash, Motoransteuerung, Zigbee). Die Angaben unten beschreiben den Stand nach dem
> C6-Umbau (Probeplatzierung, Routing noch nicht vollständig, siehe hauptplatine-c6.md Kapitel 8).

- **ESP32-C6-MINI-1-H8** (8 MB Flash, C42403058), Rückfall **-N4** (4 MB, C5736265) ohne Layoutänderung:
  13,2 × 16,6 × 2,4 mm, Antenne integriert. Footprint `lcsc:WIFIM-SMD_ESP32-C6-MINI-1` (Pads wie C3, 3D-Modell
  des C6; der KiCad-Footprint `RF_Module:ESP32-C6-MINI-1` wird wegen seiner Antennen-Sperrzone nicht genutzt).
- **Native USB** (IO12/IO13) über die **USB-C-Buchse J4 auf der Platine** (Variante E): Flashen, Debug und
  5-V-Betrieb inkl. Motor. Power-Path: VBUS über Schottky D2 auf VSYS, Akku/Ladeplatine (BAT_IN) über P-FET Q1.
- Updates später per WLAN (OTA).
- Pinbelegung (Stand Schaltplan `hardware/main-board/louie-main.kicad_sch`, Umbau 2026-11-02, Details und
  Begründungen in [hauptplatine-c6.md](hauptplatine-c6.md) 2.3):

| GPIO (Pad) | Netz | Funktion |
|---|---|---|
| IO0 (12) | VBAT_ADC | ADC VSYS (Teiler 470k/470k, bis 5,5 V → 2,75 V) |
| IO1 (13) | ISEN_ADC | ADC Motorstrom: IPROPI des DRV8213 über R1 1,24 k, RC 1 k/100 n (255 mV/A) |
| IO2 (5) | INT | INT1 des LIS2DH12 (bestückungsoptional) und Pad J2; LP-GPIO, weckt aus Deep Sleep |
| IO3 (6) | SENSE | Hebel-Erkennung, „Hebel zu“ = HIGH, Wecken mit `WAKEUP_ANY_HIGH` |
| IO4 (9) | VBUS_DET | VBUS-Teiler 100k/100k (USB gesteckt), ADC + LP-Wecken |
| IO5 (10) | IO5 | Reserve, Pad J3-5 (zweiter Taster) |
| IO6 (15) | SDA | I²C-Daten (LIS2DH12, Pad J2), 10k Pull-up R16 |
| IO7 (16) | SCL | I²C-Takt (LIS2DH12, Pad J2), 10k Pull-up R10 |
| IO8 (22) | IO8 | Strapping-Pin, 10k Pull-up R11 (beim Download 1) |
| IO9 (23) | BOOT | Pad J3-3, Taster gegen GND; beim Reset gedrückt = Download-Modus |
| IO12 / IO13 (17/18) | USB_D− / USB_D+ | USB-C J4 (ESD U5); J1-2/3 bleiben frei |
| IO14 (19) | LED | Status-LED über 1k |
| IO18 (24) | MOT_IN1 | DRV8213 IN1 (PWM) |
| IO19 (25) | MOT_IN2 | DRV8213 IN2 (PWM) |
| TXD0 / IO16 (31) | TXD | Pad J3-2 (serielle Konsole, ROM-Log) |
| IO15, IO17, IO20–IO23 | – | frei (IO20 = nSLEEP nur beim Rückfall DRV8833) |

Bauteile von Platine A (Stand Umbau, Quelle der Wahrheit: `hardware/bom/teile.csv`):

| Ref | Bauteil | Aufgabe |
|---|---|---|
| U1 | ESP32-C6-MINI-1-H8 (Rückfall -N4) | MCU, WLAN/BLE/802.15.4 |
| U2 | DRV8213DSGR (WSON-8 2 × 2) | H-Brücke mit IPROPI-Strommessung, Strombegrenzung 2 A (R1 1,24 k), Autosleep |
| U3 | AP2112K-3.3 | LDO 3,3 V |
| U4 + C15 | LIS2DH12 + 100 n | Beschleunigungssensor, **bestückungsoptional** (DNP möglich) |
| U5 | USBLC6-2SC6 | ESD USB |
| J4 | HRO TYPE-C-31-M-12 | USB-C an der Längskante +y, Öffnung 0,7 mm zurückgesetzt |
| D2, Q1 | SS34F (SMAF), AO3401A | Power-Path VBUS → VSYS bzw. BAT_IN → VSYS (Verpolschutz) |
| R12/R13, R14/R15 | 5,1 k, 100 k/100 k | CC-Senke, VBUS_DET-Teiler (zugleich Gate-Pull-down Q1) |
| C1, C2 | 47 µF 1206 | Puffer VSYS (C3 entfällt) |
| C4, C8–C14 | 0402/0603 | Abblock, EN-RC, ADC-Filter |
| R1–R11, R16 | 0402 | IPROPI, EN, Hebel-Erkennung (R3 OUT_A → GND, R4 OUT_B → 3V3, R5), Teiler, LED, Pull-ups |
| D1 | LED grün 0402 | Status |
| J1, J2, J3, J5 | Lötpads unten | Kabel Ladeplatine (BAT_IN, –, –, GND), I²C/INT, Service (EN, TXD, BOOT, GND, IO5), Zelle |
| BT1, BT2 | Pads unten | Endkontakte OUT_A / OUT_B |

## 6. Mechanik und Adapter

| Modell | Platine A | Platine B | Adapter |
|---|---|---|---|
| 2× AA (neu, Chewie) | direkt in Kammer 1 | Kammer 2: **Ladeplatine hochkant** (übernimmt die Brücke); Platine B nur, wenn die Ladeplatine in der Basis sitzt | AA-Einsatz der Ladeplatine; Kabel am Deckel vorbei |
| 1× C (alt) | in 3D-gedruckter C-Hülse | entfällt (im Reservefall ebenfalls in der Hülse, Brücke ungenutzt) | Hülse Ø 26 × 50 mm |

- Reservefall A + B in der C-Hülse: beide Platinen übereinander mit ca. 10 mm Abstand
  (je ±5 mm von der Mitte). Dort ist die Hülse noch ca. 24 mm breit, je Platine 4–5 mm
  Bauhöhe → passt mit Reserve. Gleiche Platinen und gleiches Kabel wie bei 2× AA.

- C-Hülse: Platine A sitzt mittig, an den Enden flache Kontaktflächen. Gegenüber liegen im Fach
  ein flaches Blech und eine Feder; der Pluspol-Nippel muss nicht nachgebildet werden, sofern das
  Blech flach anliegt. C-Zelle und AA-Zelle sind fast gleich lang (50 vs. 50,5 mm), es braucht
  also keine Längenüberbrückung.
- Altes Modell hat keinen Deckel → Kabel kommt einfach oben aus dem Fach.

### 6.1 Druckteile (`hardware/mechanik/huelle.scad`, Export: `just stl`)

Alle Teile drucken **ohne Stützmaterial**; Montage nur durch Stecken, kein Werkzeug.

| Teil | Anzahl | Druckausrichtung | Aufgabe |
|---|---|---|---|
| AA-Schale | 1 | aufrecht (gleicher Querschnitt über die Länge) | trägt die Platine von unten, Tasche für Lötpads und Kabel, Kabelfenster seitlich an J1 |
| Kappe plus / minus | je 1 | Innenseite auf dem Bett | halten die Platinenenden in einem Schlitz (0,8 mm Überdeckung), Pluspol-Nippel optional |
| C-Hülse | 1 (nur altes Modell) | aufrecht | AA→C-Adapter, Längsschlitz für das Kabel |

- **Oberseite im AA-Format offen:** Die Platine (13,5 mm) ist fast so breit wie die AA-Hülle
  (14,5 mm), über dem Modul bleibt am Rand keine Wandstärke. Das Fach selbst umschließt den
  Einsatz; beim C-Adapter ist er vollständig eingeschlossen.
- **Endkontakte:** Nickelband 4 × 0,15 mm auf BT1/BT2 löten, unter der Platine durch den
  Schlitz der Kappe führen und außen über die Mitte umbiegen (beantwortet F3 vorläufig).
- **Dübel:** 4 Stücke 1,75-mm-Filament à ca. 6 mm (Loch 1,95 mm), bei Bedarf mit einem Tropfen Kleber.
- Montage: Bänder anlöten → Kabel an J1 löten und durchs Fenster führen → Platine in die Schale
  → Kappen mit Dübeln aufstecken, Bänder umbiegen → (C) in die Hülse schieben, Kabel im Schlitz.

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
- [x] Teile der Ladeplatine in `teile.csv` geprüft (LCSC-Nummern verifiziert, 2026-11-01)
- [ ] Offene Punkte der Ladeplatine L1–L6 ([ladeplatine.md](ladeplatine.md))
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
