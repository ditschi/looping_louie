# Idee: USB-C auf der Hauptplatine, Strom-Pads für eine direkt angelötete Zelle

Stand: 2026-11-02 · Status: Analyse, nichts beschlossen. Greift die Idee **I2** aus
[offene-punkte.md](offene-punkte.md) auf (I1 „USB-C-AA-Zellen“ ist verworfen). Ergänzt
[hardware-konzept.md](hardware-konzept.md), [ladeplatine.md](ladeplatine.md) und
[idee-optionale-hardware.md](idee-optionale-hardware.md).

Markierungen: **(geprüft)** = mit Quelle oder an den Projektdateien nachgerechnet · **(unsicher)** = aus dem
Gedächtnis oder nur aus einer Sekundärquelle, vor dem Layout im Datenblatt prüfen.

## Kurzfazit

Priorität des Auftraggebers: (1) USB-C auf der Hauptplatine, auch als 5-V-Eingang für den **ganzen Betrieb
inkl. Motor** (z. B. aus einer kleinen Powerbank in der Basis), (2) Ladeplatine weiter möglich, (3) direkt
angelötete Zelle nur, wenn sie billig mitfällt.

- **Die Höhe passt, die Fläche wird knapp.** Eine liegende 16-polige USB-C-Buchse (HRO TYPE-C-31-M-12)
  passt an der **Längskante am rechten Ende** (weit weg von der Antenne) in die AA-Hüllkurve, Öffnung 0,7 mm
  zurückgesetzt.
  - Sie belegt ca. **80 mm² auf beiden Lagen**. Mit ESD, CC-Widerständen und Power-Path kommen
    **ca. 105 mm²** dazu, auf einer Oberseite, die schon zu 60 % belegt und nur zu 95 % routbar ist.
  - Das geht nur mit Abstrichen: Puffer-Elko C3 weg, kleinere Gehäuse, LIS2DH12 versetzen, Kabel-Pads
    umziehen. Ob es reicht, **muss eine Probeplatzierung zeigen** (machbar, aber nicht sicher).
- **Power-Path:** VBUS über eine 3-A-Schottky auf VSYS, Zelle bzw. Ladeplatine über einen P-FET (Prinzip
  Microchip AN1149, wie auf der Ladeplatine). Beide Wege sind rückspeisesicher, der Eingang deckt 3,0–5,5 V ab.
  - Der P-FET ist **ohnehin Pflicht**, sobald die Ladeplatine zusätzlich zur Buchse auf A hängt. Sonst lädt
    USB den Akku ungeregelt über Q101 der Ladeplatine.
  - Damit fallen **Verpolschutz und die direkte Zelle fast gratis mit**: zwei Lötpads mehr.
- **Empfehlung:** **Variante E**: USB-C auf A + Unterseiten-Pads (BAT_IN, D+, D−, GND) für Ladeplatine,
  Gehäusebuchse oder Zelle. Erst nach Probeplatzierung bestellen.
  - Klappt die Platzierung nicht: Rückfall auf **Variante F** (Power-Path und Pads ohne Buchse) oder
    wenige Passive unten von Hand löten.
  - **Variante G** (Ladeplatine per USB-C-Kabel) ist weder einfacher noch sicherer: **nicht verfolgen**.
  - Zwei Buchsen gleichzeitig: nur Hinweis „nur eine Buchse benutzen“, kein Mux.

---

## 1. Ausgangslage (aus dem Projekt)

| Punkt | Stand |
|---|---|
| Platine A | 46 × 13,5 × 0,8 mm, Oberseite 0,5 mm über der Zellachse, einseitig bestückt (Variante 1b, 0402) |
| Belegung oben | 376 von 621 mm² Courtyard-Fläche ([platzierung.png](bilder/platzierung.png)), Freerouting „am Limit“ |
| Unterseite | nur Kupfer: **J1** (VSYS, D+, D−, GND; x = 18,5), **J2** (I²C), **J3** (Service), **BT1/BT2** (Endkontakte), Antennen-Sperrfläche x < −14,5 |
| Die Kabel-Pads liegen **schon unten** | J1 ist seit Variante 1b ein Lötpad-Satz auf der Unterseite. Dieser Teil des Wunsches ist erfüllt. |
| Versorgung | VSYS geht direkt auf DRV8833 (VM), LDO AP2112K und Teiler R6/R7 (VBAT_ADC). **Kein Verpolschutz** auf A; Power-Path und Akkuschutz sitzen auf der Ladeplatine. |
| Freie GPIOs | keine (alle belegt) → keine VBUS-Erkennung per Pin; USB nur indirekt an VSYS > 4,4 V erkennbar |

---

## 2. Mechanik

### 2.1 Höhe in der AA-Hüllkurve (geprüft, nachgerechnet)

AA-Radius 7,25 mm; Platinenoberseite bei z = +0,5 mm, Unterseite bei −0,3 mm.

| Lage der Buchse (y = Abstand von der Platinenmitte) | Platz über der Oberseite | Buchse (Höhe über Platine) | passt? |
|---|---|---|---|
| Mitte, y = ±4,5 (Buchse quer, Öffnung zur Stirnseite) | 5,2 mm | 3,2–3,3 mm | ja |
| Längskante, Öffnung bündig bei y = 6,75 | 2,15 mm | 3,26 mm | **nein**, Ecke ragt ca. 0,4 mm über Ø 14,5 |
| Längskante, Öffnung **0,7 mm zurückgesetzt** (y = 6,05) | 3,5 mm | 3,26 mm | **ja** (Ecke bei r = 7,12 mm) |
| vertikale Buchse (≥ 6,5 mm hoch) mittig | 6,5–6,75 mm | 6,5–11 mm | höchstens die allerflachsten, ohne Reserve (unsicher) |

Die Höhe ist damit kein Hindernis, wie in hardware-konzept.md 4.1 schon angenommen.

### 2.2 Wo? Stirnseite, Längskante, vertikal, Mid-Mount

| Lage | Bewertung |
|---|---|
| **Stirnseite** (Öffnung in Zellachse) | ✗ Dort sitzen Endkontakt BT2, Kappe und Nickelband. Zum Stecken müsste die Kappe ab und das Band aufgebogen werden. Am Antennen-Ende ist sie ohnehin verboten. |
| **Längskante, rechtes Ende** (Öffnung bei +y, Mitte x ≈ 15) | ✓ Weit weg von der Antenne (> 25 mm). Das Kabelfenster der AA-Schale liegt schon in dieser Gegend (`kabel_x = 18.5`). Gleiches Prinzip wie bei der Ladeplatine. |
| **vertikal** | ✗ Nur ohne jede Reserve. Der Stecker stünde 20 mm und mehr radial heraus, der Hebelarm ist am größten. |
| **Mid-Mount / „sinking“** (Platinenausschnitt) | ✗ Die Höhe wird gar nicht gebraucht. Der Ausschnitt von ca. 9 × 6,5 mm in 13,5 mm Breite schwächt die Platine und kostet beide Lagen. Die üblichen Typen „CB1.6“ sind für 1,6-mm-Platinen gedacht, mit 0,8 mm also unklar (unsicher). |

**Erreichbarkeit:** Die Schale dreht man so ins Fach, dass die Buchsenkante zur Fachöffnung zeigt. Dann
lässt sich wie bei der Ladeplatine (Einbauart A) **von oben stecken, wenn der Deckel ab ist**. Das Fach ist
rotationssymmetrisch, das Modul passt in jeder Drehlage gleich. Beim alten Louie (offenes Fach, C-Hülse)
zeigt die Kante nach oben, dort ist die Buchse im eingebauten Zustand erreichbar. Sonst gilt: zum Flashen
herausnehmen, die Kappen bleiben dran. Das reicht, denn Updates laufen normalerweise per OTA.

### 2.3 Kandidaten

**Wichtig:** 6-polige USB-C-Buchsen (z. B. HRO TYPE-C-31-M-17, GCT USB4125/4135) führen **nur VBUS, GND,
CC1, CC2 und keine Datenleitungen**. Zum Flashen sind sie nutzlos. Gebraucht wird eine 16-polige
USB-2.0-Buchse. **(geprüft: KiCad-Bibliothek, Beschreibung „USB 2.0, 6 pin“ beim M-17 ohne D+/D−-Pads)**

| Typ | LCSC | Bauform | Maße | Status |
|---|---|---|---|---|
| HRO TYPE-C-31-M-12 | C165948 | 16P, liegend, Top-Mount, 4 THT-Laschen | 8,94 × 7,35, Höhe ca. 3,2 | Extended; schon auf der Ladeplatine **(geprüft)** [JLC][jlc-hro] |
| HCTL HC-TYPE-C-16P-01A | C2894897 | wie M-12, gleiche Lochlage | ca. 8,94 × 7,3 | Zweitquelle **(Footprint geprüft, Lager unsicher)** [Datenblatt][hctl] |
| XKB U262-16XN-4BVC11 | C319148 | wie M-12 | ca. 8,94 × 7,3 | Zweitquelle **(unsicher)** |
| SHOU HAN TYPE-C 16PIN 2MD(073) | C2765186 | Top-Mount, sehr verbreitet bei JLC | ca. 8,94 × 7,3 | **(unsicher)** |
| SHOU HAN TYPE-C 16P CB1.6 073 / HCTL HC-TYPE-C-16P-CB1.6 | C2906290 / C2894902 | Mid-Mount („recessed“), Länge 6,5 | – | nicht empfohlen, siehe oben [JLC][jlc-cb16], [LCSC][lcsc-cb16] |

Footprint HRO M-12 (KiCad): Öffnung bei +3,65 mm, SMD-Pads bei ca. −4,0 mm, THT-Laschen bei x = ±4,32 und
y = −3,13 / +1,05, Stift-Löcher bei ±2,89 / −2,6 **(geprüft, KiCad-Bibliothek)**. Mit Öffnung bei y = +6,05 auf
der Platine belegt die Buchse **y = −1,6 … 6,75 und x = Mitte ± 4,8**, das sind ca. 9,6 × 8,4 = 80 mm², davon die
Laschen- und Lochzone auf **beiden** Lagen.

### 2.4 Flächenbilanz (Variante E, Buchse bei x ≈ 15,3)

| Zusätzlich oben | Gehäuse | Courtyard ca. |
|---|---|---|
| J4 USB-C | s. o. | 80 mm² |
| ESD (USBLC6-2SC6 / kleiner: SOT-666 oder 2 × TVS 0402) | SOT-23-6 / SOT-666 | 12 / 6 mm² |
| R CC1, CC2 5,1 k | 0402 | 3 mm² |
| D2 Schottky VBUS | SOD-123F / SOD-323 | 8 / 5 mm² |
| Q1 P-MOSFET Akku-Pfad | SOT-23 | 11 mm² |
| R Gate-Pull-down 100 k | 0402 | 1,5 mm² |
| **Summe** | | **ca. 105–115 mm²** |

Die Buchse verdrängt am rechten Ende **C3 (47 µF), R4, C8, C11 und die Kabel-Pads J1**. Für das Band
y < −1,6 (ca. 12 × 4,9 = 59 mm²) blieben C1, C2, U3, C8, C11, U4, C15, ESD, Q1, D2 und drei Widerstände,
zusammen **ca. 75 mm² auf 59 mm²**. **Ohne Abstriche passt das nicht.** Mögliche Abstriche: C3 streichen
(2 × 47 µF bleiben), ESD in SOT-666, D2 in SOD-323, LIS2DH12 und C15 rechts neben die Buchse
(x > 20, ca. 26 mm² frei bis auf R4). Damit wird es knapp machbar, aber nur per Probeplatzierung zu
entscheiden. Die Routing-Reserve wird dadurch eher kleiner.

### 2.5 Steckkräfte bei 0,8 mm

- Stecken ca. 5–20 N, Ziehen 8–20 N laut Type-C-Spezifikation **(unsicher, aus dem Gedächtnis)**. Kritischer
  sind seitliche Hebelkräfte am Kabel.
- Die THT-Laschen halten in 0,8 mm weniger als in 1,6 mm (genau deshalb hat die Ladeplatine 1,6 mm). Gegenmaßnahmen:
  - alle 4 Laschen voll verlöten (JLC: Paste-in-Hole) **(unsicher, ob in Economic)**
  - die AA-Schale **unter der Buchse vollflächig abstützen**
  - das Fenster der Schale eng um den Steckerkragen führen, damit die Schale die Hebelkraft aufnimmt und nicht die Lötstellen
  - Dauerbetrieb an der Powerbank: Das Kabel im Fach drückt ständig seitlich. Darum einen Winkelstecker
    nehmen und das Kabel an der Schale zugentlasten (Kabelbinder-Öse), statt es an der Buchse hängen zu lassen.

---

## 3. Elektrik

### 3.1 USB-Daten

- GPIO18/19 (D−/D+) direkt an A6/B6 bzw. A7/B7, kurz und parallel geführt. Der C3 braucht keinen Wandler;
  USB-Serial/JTAG läuft auch mit Fremdversorgung, also mit Akku statt VBUS **(geprüft)** [ESP-IDF][idf-usj].
- CC1/CC2 **je eigener** 5,1 k gegen GND (Senke). Nie zwei Buchsen an einem Widerstandspaar.
- ESD direkt an der Buchse. Jede Buchse bekommt ihren eigenen ESD-Schutz.

### 3.2 Power-Path (minimal und sicher)

Der Load-Sharing-Teil der Ladeplatine (Microchip AN1149) zieht auf die Hauptplatine um, nur ohne Laderegler:

```
 VBUS (J4) ──┬──|>|── D2 Schottky ──────────────┬── VSYS ──> DRV8833 VM, LDO, Teiler R6/R7
             │                                  │
             └──────────┐ Gate                  │ S
                       Q1  AO3401A (P-MOSFET)   │
 BAT_IN ─────────────── D ──────────────────────┘    Body-Diode: BAT_IN → VSYS
 (Pad: Zelle oder       │
  Ladeplatine)        R 100k  Gate → GND
```

| Fall | Ergebnis |
|---|---|
| nur USB | VSYS ≈ 4,65 V über D2. Q1 sperrt (Gate 5 V), **nichts fließt in die Zelle**. |
| nur Zelle | Gate über 100 k auf GND, Q1 leitet (Rds(on) ca. 50–90 mΩ bei 3–4 V, unsicher) → VSYS ≈ VBAT |
| USB + Zelle | USB versorgt, die Zelle ruht: **Flashen mit gestecktem Akku ohne Rückspeisung**. D2 verhindert die Rückspeisung in den Host. |
| Zelle verpolt | Q1 sperrt (Vgs = 0, Body-Diode in Sperrrichtung) → **Verpolschutz** für alles hinter VSYS **(nachgerechnet, im Prototyp prüfen)** |

- **D2:** 2–3-A-Schottky (der Motor kann bei USB-only bis 2 A ziehen). Firmware: Liegt VSYS über 4,4 V (USB), Motorleistung begrenzen; ein USB-2.0-Port liefert nur 500 mA.
- **LM66100** (ideale Diode, SC-70, 1,5 A, 0,15 µA) **(geprüft)** [TI][ti-lm66100] wäre als VBUS-Diode ohne 0,35 V Abfall möglich. Für den Akku-Pfad reichen 1,5 A nicht (2-A-Grenze des DRV8833).
- TPS2113A, TPS2116 (Power-MUX) gehen auch, sind aber größer, teurer und nicht nötig.
- **Einschaltstrom:** 3 × 47 µF hinter D2 sind mehr, als USB beim Stecken erlaubt (10 µF). Das ist heute an der Ladeplatine genauso und in der Praxis unkritisch **(unsicher)**.

### 3.3 Zwei Buchsen gleichzeitig (Hauptplatine + Ladeplatine bzw. Gehäusebuchse)

Vorgabe des Auftraggebers: **kein USB-Mux, nur der Hinweis „nur eine Buchse benutzen“**, VBUS aber
rückspeisesicher.

- **VBUS:** jede Buchse über ihre eigene Diode auf VSYS (Diode-OR). Auf A ist das D2. Eine zweite Buchse kommt immer **über BAT_IN** und bringt ihre Diode selbst mit: bei der Ladeplatine D102, bei einer reinen Buchsenplatine eine eigene Schottky. **Kein Querstrom, keine Rückspeisung in einen Host**, und A braucht kein zweites VBUS-Pad.
  - Alternative mit eigenem Pad VBUS_EXT: zweite Schottky D3 auf A plus Gate-OR für Q1 (BAT54C). Kostet ca. 12 mm² mehr, nur nötig, wenn Zelle **und** Gehäusebuchse gleichzeitig an A hängen sollen. Nicht vorsehen.
- **Ladeplatine (heutige v0.1) an BAT_IN:** Steckt nur die Buchse auf A, sperrt Q1 und die Body-Diode, die Akkuseite der Ladeplatine bleibt unberührt. Steckt nur die Ladeplatinen-Buchse, kommen 4,6 V über BAT_IN, Q1 leitet. **Funktioniert ohne Änderung an der Ladeplatine** (nachgerechnet).
  - Achtung: Ohne Q1 auf A (VSYS direkt am Pad) würde USB über die Hauptplatine den Akku **ungeregelt über Q101 der Ladeplatine laden**. Q1 ist also Pflicht, sobald es zwei Einspeisungen gibt.
- **D+/D− parallel, Stichleitung:** USB Full Speed (12 Mbit/s, Anstiegszeit 4–20 ns) verträgt Stichleitungen bis grob 10–15 cm gut. Das Kabel zur unbenutzten Buchse ist so eine Stichleitung. **Kabel ≤ 15 cm, D+/D− verdrillt** (unsicher, am Prototyp testen, wie A8/L6).
- **Beide gesteckt (zwei Hosts):** Beide Hosts treiben D+/D−. Die Enumeration scheitert oder bricht ab. Schaden ist nicht zu erwarten: USB-Treiber müssen Kurzschlüsse der Datenleitungen gegen GND, VBUS und die andere Leitung dauerhaft aushalten (USB 2.0, Kap. 7.1.1) **(unsicher, aus dem Gedächtnis)**. Zwei PCs bilden eine Masseschleife. Der **Hinweis reicht**.
- **USB-Mux** (TS3USB221: UQFN-10 1,5 × 2,0 mm, Auswahl über VBUS-Teiler) **(geprüft)** [TI][ti-ts3usb]: passt flächenmäßig, aber sechs USB-Leitungen mehr auf dieser Platine zu routen ist der eigentliche Engpass. **Nicht vorsehen.**

### 3.4 Zelle direkt ohne Ladeplatine: Tiefentladung

- **Ruhestrom im Deep Sleep** (Schätzung): LDO 55 µA + Teiler 4,5 µA + ESP ca. 5 µA + DRV8833-Sleep ca. 2 µA + LIS2DH12 ca. 1 µA ≈ **65–70 µA ≈ 1,6 mAh/Tag**. Q1 und D2 verbrauchen nichts.
- **Software-Abschaltung reicht nicht allein.** Selbst wenn die Firmware bei 3,3 V in den Deep Sleep geht, entlädt der LDO weiter. Ab ca. 3,3 V (Restkapazität grob 50–100 mAh) dauert es **ca. 1–2 Monate bis zur Tiefentladung** (unsicher). Im Spielzeugschrank ist das realistisch.
- **Deshalb: nur Zellen mit Schutzschaltung** (geschützte 18650/14500, LiPo-Pouch mit PCM). Sie schalten bei ca. 2,5–3,0 V ab. Die Software-Stufen (ideen.md, technik-11) bleiben als Komfort.
- **Optional:** LDO mit kleinem Ruhestrom (z. B. RT9080, ca. 2 µA, 600 mA, SOT-23-5, **unsicher**; oder TLV75533, 25 µA) senkt den Schlafstrom um Faktor 5–10. Hängt mit Annahme A3 zusammen.
- **Warnung:** Eine **14500-Zelle (3,7 V) niemals ins Original-Fach** stecken. Das Fach liegt im Motorstromkreis (Kammer 2 = Brücke). Die Zelle läge in Reihe mit dem Motor und würde ihn über die Body-Dioden des DRV8833 ungesteuert antreiben. 14500/18650 gehören in einen Halter in der Basis.

### 3.5 Grundsatz: Hauptplatine allein, breiter Eingang 3,0–5,5 V

Vorgabe des Auftraggebers: Die Hauptplatine soll für sich allein flexibel sein. Sie nimmt 3,0–5,5 V aus
USB-VBUS, von den Ladeplatinen-Pads (5 V oder Akkuspannung) oder direkt von einer Zelle im Halter. Im
zweiten Fach steckt nur die Brücke (Platine B). Wer extern lädt, bestellt eine Platine weniger. **Der
Power-Path aus 3.2 erfüllt das schon**, mit folgenden Einzelheiten:

| Thema | Bewertung |
|---|---|
| **Pfad je Quelle** | VBUS: Schottky (0,35 V bei 5 V sind egal) oder LM66100. **Zelle/Ladeplatine (BAT_IN): P-FET Q1**, kein Schottky, denn 0,35 V Verlust bei 3,2 V Zelle bringen den LDO in den Dropout. LM66100 im Zellpfad: nur 1,5 A, zu wenig. TPS2113A (Power-MUX, MSOP-8/SON): kann es, ist aber größer und teurer, bringt hier nichts. **Minimal = 1 Schottky + 1 P-FET + 1 Widerstand.** |
| **Rückspeisung** | Mit USB sperrt Q1 → keine Ladung der Zelle aus VBUS. D2 sperrt → kein Strom aus der Zelle in VBUS. Ladeplatine v0.1 an BAT_IN liefert 4,6 V oder Akkuspannung; beides läuft über Q1, ohne Konflikt. **Pro Eingang nur eine Quelle:** nie Zelle **und** Ladeplatine an BAT_IN. |
| **Spannungsgrenzen** | AO3401A (30 V, ±12 V Gate), DRV8833 (bis 10,8 V), AP2112K (max. 6 V) vertragen 5,5 V **(unsicher, Datenblätter)**. |
| **3,3-V-Regler** | AP2112K: Dropout ca. 250 mV bei 600 mA. Bei 3,3 V Zelle und WLAN-Spitzen ergibt das ca. 3,1 V, und der ESP läuft ab 3,0 V. Weil die Firmware die Zelle ohnehin bei ca. 3,3–3,4 V unter Last abschalten soll (Lebensdauer, Motor), **reicht der LDO**. Bei 5,5 V Eingang werden im Mittel ca. 0,2 W warm, das geht. Buck-Boost TPS63802 (2 A, ca. 11 µA Ruhestrom, VSON 2 × 3 mm + Spule + 2 × 22 µF, **unsicher**) kostet ca. 20 mm² mehr. Er lohnt sich nur, wenn der Prototyp Brownouts zeigt (Annahme A3). Sinnvoller ist ein **pinkompatibler LDO mit kleinem Ruhestrom** (siehe 3.4). |
| **Motor an VIN** | DRV8833 direkt an VSYS. Tastgrad = U_soll / VIN. 1,5-V-Motor an 5 V: 30 % (Turbo 2,5 V: 50 %). Bei 20 kHz und 8–10 Bit PWM ist das fein genug. Der Mittelstrom entspricht dem Betrieb an Nennspannung. Die Spitzen begrenzen Wicklungsinduktivität und die 2-A-Grenze des DRV8833. **Risiko:** Hängt die Firmware mit 100 % fest, sieht der 1,5-V-Motor das 3,3-Fache. Das gilt heute bei 4,2 V schon fast genauso. Abhilfe: Watchdog, harte Tastgrad-Obergrenze je Profil, nSLEEP mit Pull-down (Motor aus im Reset). |
| **Messung (VBAT_ADC)** | misst VSYS = VIN. Bei Zelle direkt ist das der echte Akkustand. VIN > ca. 4,45 V heißt „extern versorgt“ → im Web-UI „Netz/Ladeplatine“ statt Prozent. Grenze: LiHV-Zellen laden bis 4,35 V, USB hinter Schottky unter Last ist ≥ 4,3 V. Also mit Hysterese und bei stehendem Motor messen. **Ein zweiter ADC-Kanal lohnt nicht:** IO2 ist SCL (I²C, Strapping), der Akku läge hinter Q1 ohnehin nicht am Teiler. **Wichtig:** Der Teiler 470k/470k liefert bei 5,5 V 2,75 V am ADC. Der ADC des C3 misst nur bis ca. 2,5 V **(unsicher, ESP-IDF-ADC-Doku)**. → **Teiler auf ca. 0,41 ändern (z. B. 470 k oben / 330 k unten)**: 5,5 V → 2,27 V, 3,0 V → 1,24 V. |
| **Schutz bei Zelle direkt** | Verpolschutz durch Q1 (3.2). Tiefentladung: **nur geschützte Zellen**. Software-Stufen (Warnung 3,5 V, Rundenende 3,3 V, Deep Sleep 3,2 V) bleiben Komfort. Li-Ion nimmt unter ca. 2,5 V Schaden; nach längerer Zeit unter ca. 2 V nicht mehr laden **(unsicher, übliche Herstellerangabe)**. Mit 65–70 µA Ruhestrom dauert es von 3,3 V bis 2,5 V bei einer 2000-mAh-18650 ca. 2 Monate, bei einem 500-mAh-Pouch **ca. 2 Wochen** (Restkapazität grob 5 %, unsicher). Ein LDO mit ca. 2 µA streckt das etwa um Faktor 4. Selbst abschalten kann sich die Platine nicht (kein GPIO für LDO-EN). |

**Akkuspannung auf einer USB-C-Buchse der Ladeplatine (an den PC gesteckt):** Mit Rd an dieser Buchse
schaltet ein PC oder Netzteil 5 V auf. Mit einem A-auf-C-Kabel liegen die 5 V immer an (Rp im Kabel). Die 5 V
treffen über Q101 (leitet ohne eigenes VBUS) auf die Zelle: **ungeregeltes Laden mit bis zu 1,5–3 A**,
Brandgefahr. Ohne Rd schaltet ein C-auf-C-Host zwar nicht ein, ein A-auf-C-Kabel aber trotzdem. **Akkuspannung
gehört nie auf eine USB-Buchse.** Die Ladeplatine wird deshalb **per Pads und gelötetem Kabel** angebunden, für
Trennbarkeit mit einem **eigenen, verwechslungssicheren Stecker** (z. B. JST-PH 4- oder 5-polig auf der
Ladeplatinen-Seite), nicht per USB-C.

### 3.6 Betrieb an einer Powerbank über USB-C (was das für A heißt)

Die Powerbank-Auswahl und das Wecken klärt eine eigene Recherche. Für die Hauptplatine folgt daraus:

- **CC-Widerstände 5,1 k sind Pflicht.** Eine Powerbank schaltet VBUS an einer C-Buchse nur ein, wenn sie Rd sieht (mit C-auf-C-Kabel).
- **D2 für den Motorstrom auslegen:** 3-A-Schottky (z. B. SS34-Klasse in SMAF/SOD-123FL, Typ und LCSC-Nr. offen, **unsicher**). Bei 2 A fallen ca. 0,45 V ab, VSYS liegt bei ca. 4,5 V. Die LM66100 (1,5 A) reicht hier nicht.
- **Leiterbahn VBUS → D2 → VSYS ≥ 0,6 mm, 2 Vias.** VBUS-Pins der Buchse A4/A9/B4/B9 alle anschließen; über Kabel und Stecker fallen bei 2 A ca. 0,1–0,2 V ab (unsicher).
- **Ruhestrom im Deep Sleep:** 65–70 µA (3.4), das liegt weit unter jeder Abschaltschwelle von Powerbanks (typisch einige 10 mA, unsicher). Die Powerbank schaltet also ab, danach ist A stromlos und der Hebel weckt nichts mehr.
  - Hilfe allein durch Firmware: Der ESP hält z. B. alle 10–20 s für ca. 1 s das WLAN an (ca. 80–100 mA). Ob die Powerbank das als Last zählt, ist typabhängig.
  - Hilfe per Hardware: Lastwiderstand mit MOSFET. **Dafür ist kein GPIO frei.** Ginge nur über IO10 (Status-LED) und kostet Fläche: Widerstand für ca. 1 W Pulslast, z. B. 2512. **Nicht vorsehen.** Diese Frage gehört zur Powerbank-Auswahl (Powerbank mit „Low-Current-/Always-on-Modus“).
- **Erkennung:** VSYS > ca. 4,45 V heißt „extern versorgt“. Einen Akkustand der Powerbank gibt es nicht; das Web-UI zeigt „USB/Powerbank“.
- **Mechanik:** Das Kabel steckt dauerhaft im Fach. Beim 2×AA-Modell braucht der Deckel einen Ausschnitt, oder man nimmt die **Gehäusebuchse**: eine kleine Buchsenplatine in der Basis (USB-C, 2 × 5,1 k, ESD, Schottky), mit 2–4 Adern an BAT_IN/GND (und D+/D−) von A. Dann bleibt die Buchse auf A für das Flashen.

---

## 4. Pads auf der Unterseite

| Pad | Netz | Größe | Zweck |
|---|---|---|---|
| J1-1 „V“ | **BAT_IN** (bisher VSYS) | 1,4 × 1,6 (wie heute) | Ladeplatine v0.1 unverändert anschließbar (deren VSYS → BAT_IN) |
| J1-2/3 | D+ / D− | wie heute | zweite Buchse, Ladeplatine |
| J1-4 | GND | wie heute | |
| **J5 „+“ / „−“** | BAT_IN / GND | **2,5 × 3,5 mm**, ≥ 1 mm Abstand, Aufdruck +/− | Litzen 0,25–0,5 mm² (AWG 24–20) zum Zellhalter; 2 A Motorspitzen |
| (J6 „5V“) | VBUS_EXT | – | **entfällt**: Gehäusebuchse und Ladeplatine speisen über ihre eigene Diode an BAT_IN ein (3.3) |

- **Leiterbahnen** BAT_IN → Q1 → VSYS ≥ 0,6 mm oder als Fläche, je **2 Vias** pro Lagenwechsel (siehe A16). 0,4 mm reichen bei 2 A nur auf kurzen Stücken.
- **Konflikte:** J2/J3 (links unter dem Modul) und die Antennenzone bleiben unberührt. Die Endkontakte BT1/BT2 sind ebenfalls nicht betroffen.
  - Mit Buchse auf A (Variante E) belegen ihre Laschen und Löcher unten x ≈ 10,5–20, y ≈ −0,5…5. J1 muss dann an die Kante −y wandern (Reihe bei y ≈ −5,3, x ≈ 11–18), J5 nach x ≈ 1–8 unter den DRV8833 (GND-Pad nicht auf die Thermal-Vias legen: Lot fließt ab).
  - Die Pads unterbrechen die GND-Fläche und die Bahnen von Freerouting. **Pads vor dem Routing festlegen.**
- Die Kontaktbahn OUT_B läuft unten bei y ≈ 5,6 an der Kante entlang. Mit Buchse bleibt zwischen den vorderen Laschen (bis y ≈ 4,95) und dem Rand gerade Platz für sie (ca. 0,45 mm Abstand).

---

## 5. Varianten-Matrix

Kosten: Mehrkosten gegenüber heute, JLC Economic, 10 Stück, grob; Extended-Gebühr 3,07 USD je Teiletyp und
Auftrag ([kostenabschaetzung.md](kostenabschaetzung.md)).

| | Kurz | Platz auf A | Bauteile A (neu) | Kosten | Risiken | Bedienung (Kinder/Laien) | Kabel | Mechanik/3D |
|---|---|---|---|---|---|---|---|---|
| **A** heute | Ladeplatine mit USB-C extern | – | – | – | kein Verpolschutz auf A; ungeregeltes Laden bei falscher Verdrahtung | eine Buchse für alles, Akku fest | 4 Adern | fertig |
| **B** | USB-C auf A, Ladeplatine **ohne** USB (nur Lader) | ✗ +110 mm² | J4, ESD, 2 R, D2, Q1, R | +0,3 USD/Stk., +3–6 USD einmalig; Ladeplatine wird einfacher | Fläche, Steckkraft auf 0,8 mm; Laden nur bei offenem Fach | laden = Deckel ab, an der Platine stecken | **3 Adern** (VBUS, BAT, GND), kein USB im Kabel | Fenster in der Schale; Lader passt überall hin |
| **C** | USB-C auf A, Zelle mit Halter direkt, kein Laden | ✗ wie B | wie B | wie B + Halter 1–3 €, geschützte Zelle 5–8 €, Ladegerät | Tiefentladung, lose Li-Ion-Zellen | **Akkutausch in Sekunden**; Zellen nur durch Erwachsene | 2 Adern | Halter in der Basis (18650-Halter ca. 77 × 21 mm, Platz prüfen) |
| **D** | USB-C **mit** Laderegler auf A | ✗✗ +135 mm² | wie B + MCP73831, 3 Passive, LED | wie B + 0,3 USD | passt nicht; 500 mA Ladeverlust (ca. 0,3 W) im geschlossenen Fach neben dem ESP; die LED sieht keiner | wie heute | 2 Adern | – |
| **E** ★ | USB-C auf A **+ Pads** (BAT_IN, D+, D−, GND, große BAT/GND-Pads) für Ladeplatine, Gehäusebuchse **oder** Zelle | ✗→? +105 mm², nur mit Abstrichen | J4, ESD, 2 R, D2 (3 A), Q1, R | ca. +0,3 USD/Stk., +3–6 USD einmalig (J4, evtl. ESD/D2 Extended) | Fläche/Routing, Steckkraft 0,8 mm; zwei Hosts → Hinweis „nur eine Buchse“ | Powerbank oder Netzteil direkt; flashen an A; laden über Ladeplatine; Zelle tauschbar | 4 Adern (Ladeplatine, wie heute) / 2–4 (Gehäusebuchse) / 2 (Zelle) | Fenster + Stützsteg in der Schale, STEP prüfen |
| **F** (Rückfall) | **keine** Buchse auf A, Power-Path + Pads (BAT_IN, J5) | ✓ ca. 13–18 mm² | Q1, R 100k (+ D3, falls VBUS-Pad) | < 0,1 USD/Stk.; AO3401A vermutlich Basic **(unsicher)** | Ladeplatine wird doppelter PMOS (ca. 0,15 V bei 1 A) | wie A; Zelle direkt möglich; Flashen über Ladeplatine, Buchsenplatine oder Pogo-Adapter | 4 Adern (Ladeplatine) bzw. 2 (Zelle) | **keine Änderung** an Schale/Hülse |
| **G** | USB-C auf A, Ladeplatine **per USB-C-Kabel** gesteckt | ✗ wie B | wie B | wie B + Ladeplatine mit 2 Buchsen + Boost oder CC-Schalter (+1–3 €) | siehe Kapitel 6 | steckbar, aber Stecker im Fach | USB-C-Kabel | Deckel geht beim 2×AA nicht zu |

---

## 6. Variante G: Ladeplatine per USB-C-Kabel anstecken

**Energiefluss: Was liegt auf VBUS?**

| Option | Bewertung |
|---|---|
| (a) nackte Akkuspannung 3,0–4,2 V auf VBUS | ✗ **gefährlich.** Steckt jemand ein Netzteil oder einen PC an diese Buchse, speisen zwei Quellen gegeneinander. Über Q101 (leitet ohne eigenes VBUS) wird der Akku **ungeregelt geladen**, und es fließt Strom zurück in den Host. Nicht normgerecht. |
| (b) 5 V per Boost, Rp an CC (wie eine Powerbank) | normgerecht, aber: Boost für 2 A Motor heißt ca. 3 A aus der Zelle (Spule, IC z. B. TPS61088-Klasse, unsicher), Verlust 8–15 %. Ruhestrom Boost + LDO ca. 100–200 µA. **Powerbank-ICs (IP5306 u. a.) schalten bei kleiner Last ab** (unsicher) → **Hebel-Wecken aus dem Deep Sleep geht dann nicht mehr**. Bei UVLO bricht die Versorgung ohne Vorwarnung zusammen. |
| (c) Akkuspannung über Lastschalter nur bei erkannter Senke (Rp auf der Ladeplatine, Rd auf A, Quellen-Controller z. B. TPS25810-Klasse, unsicher) | Gegen PC und Netzteil sicher: die sehen Rp–Rp und schalten nichts. Bleibt aber nicht normgerecht (3–4,2 V statt 5 V), braucht Rückstromsperre gegen A-auf-C-Kabel. Auf A kostet D2 0,35 V: bei 3,4 V Zelle nur noch ca. 3,0 V VSYS → LDO-Dropout. |

**Motor aus 5 V VBUS:** Der DRV8833 kann bis 10,8 V; die PWM-Begrenzung auf Nennspannung und die Formel
`duty = U_soll / U_VSYS` funktionieren unverändert. 2 A Anlaufstrom über Kabel und zwei Stecker
(ca. 0,1–0,2 Ω hin und zurück, unsicher) kosten 0,2–0,4 V. Bei 5 V ist das egal, bei (c) schmerzt es.

**Daten:** Die Ladeplatine reicht D+/D− von der Außenbuchse zur Ausgangsbuchse durch. Flashen mit gestecktem
Akku geht.

**Akkustand:** Bei (b) sieht A nur 5 V. **SBU fällt aus:** Gewöhnliche USB-2.0-C-auf-C-Kabel haben keine
SBU-Adern (unsicher, Kabelspezifikation). CC ist durch Rp/Rd belegt. Ein Rp-Wert als Dreistufen-Code
(Default/1,5 A/3 A) wäre ein Hack, und für die Messung fehlt ein ADC-Pin. Bleibt eine LED-Anzeige auf der
Ladeplatine, im Web-UI dann **ohne Akkustand**. Bei (c) misst VBAT_ADC weiter, das ist der einzige Vorteil von (c).

**Mechanik:** Der Steckerkragen (ca. 12,4 × 6,5 mm, 15–20 mm lang) steht radial aus dem Fach. Auch
Winkelstecker bauen mindestens 10–12 mm hoch. **Beim 2×AA-Modell geht der Deckel nicht mehr zu**, es bräuchte
einen Ausschnitt. Beim alten Louie (offenes Fach) ginge es. Ein USB-C-Kabel ist deutlich steifer als vier dünne
Litzen; Knickschutz und kurze Kabel (15–30 cm) gibt es fertig.

**Ehrliche Bewertung:** G ist **nicht einfacher und nicht sicherer** als Lötpads plus 4-adriges Kabel. Es
braucht eine zweite Leistungselektronik (Boost oder Quellen-Controller), verliert entweder den Akkustand (b)
oder Spannungsreserve (c), und Stecker plus Kabel passen nicht unter den Deckel. Der einzige echte Vorteil, die
Trennbarkeit, geht billiger: **Ladeplatinen-Seite mit 4-poligem JST-PH/SH steckbar, Hauptplatinen-Seite
gelötet.** Die Bauhöhe zählt nur auf A (siehe F2). **Empfehlung: G nicht verfolgen.**

---

## 7. Empfehlung

### Hauptweg: Variante E (USB-C auf der Hauptplatine + Pads), nach Probeplatzierung

So decken sich die Prioritäten:
- (1) Die Buchse auf A trägt Flashen **und** Dauerbetrieb an Powerbank/Netzteil inkl. Motor.
- (2) Die Ladeplatine hängt unverändert (v0.1) an J1, angebunden per Pads und Kabel bzw. eigenem Stecker,
  **nicht per USB-C** (Kapitel 6 und 3.5). Ihre Aufgaben bleiben Akku laden und USB nach außen führen.
- (3) Die direkte Zelle kostet nur die Pads J5, weil Q1 für (2) ohnehin nötig ist.

Im zweiten AA-Fach steckt dann nur die Brücke (Platine B), wenn die Ladeplatine in der Basis sitzt oder
gar nicht verwendet wird.

```
 Oberseite, Blick von oben (x in mm, Antenne links)          Öffnung J4 → Kante +y
 +6.75 ┌────────┬──────────────┬────┬──────────────┬═════════════════════╗──────┐
       │ Anten- │              │0402│ R1  (Shunt)  ║  J4 USB-C 16P       ║ R4   │
       │ ne     │  ESP32-C3-   │Rei-│              ║  x ≈ 10,5 … 20,1    ║ U4   │
     0 │ frei   │  MINI-1      │he  │ DRV8833 (90°)║  y ≈ −1,6 … +6,75   ║ C15  │
       │        │              │    │              ╚══ THT-Laschen ══════╝      │
       │ BT1(u) │              │    │ C6 C7   C1 C2│ ESD  Q1  D2  U3 C8 C11    │BT2(u)
 -6.75 └────────┴──────────────┴────┴──────────────┴───────────────────────────┘
      -23     -14.5          -3.3  -1.5         10.5                 20.1   23
 Unterseite: J1 (BAT_IN, D+, D−, GND) als Reihe an der Kante −y (x ≈ 11–18),
 J5 (BAT_IN/GND groß) bei x ≈ 1–8, J2/J3 unverändert links,
 Laschen/Löcher von J4 bei x ≈ 10,5–20, y ≈ −0,5…5
```

**Schaltplan** (`gen_main_schematic.py`, nur beschreiben):

| Neu/geändert | Bauteil | Netze |
|---|---|---|
| J4 | HRO TYPE-C-31-M-12 (C165948), Zweitquelle HCTL HC-TYPE-C-16P-01A | A4/A9/B4/B9 → VBUS_J4; A6/B6 → USB_D+; A7/B7 → USB_D−; A5 → CC1; B5 → CC2; A1/A12/B1/B12/Schirm → GND |
| R12, R13 | 5,1 k 0402 | CC1/CC2 → GND |
| U5 | ESD: USBLC6-2SC6 (C7519) oder kleiner SOT-666 / 2 × 0402-TVS (offen) | USB_D+, USB_D−, VBUS_J4 |
| D2 | Schottky 3 A, SMAF/SOD-123FL (Typ offen) | VBUS_J4 → VSYS |
| Q1 | AO3401A (C15127) | S = VSYS, D = BAT_IN, G = VBUS_J4 |
| R14 | 100 k 0402 | VBUS_J4 → GND (Gate-Pull-down, entlädt VBUS) |
| J1 | Pin 1 **VSYS → BAT_IN**, Rest gleich | kompatibel zu J103 der Ladeplatine v0.1 |
| J5 | 2 Lötpads 2,5 × 3,5 mm, Footprint neu in `louie.pretty` | BAT_IN, GND |
| R7 | **470 k → 330 k** | VBAT_ADC-Teiler für bis 5,5 V (Firmware-Faktor 2,0 → 2,42) |
| C3 | **streichen** (oder 22 µF 0805) | Platz für J4 |
| teile.csv | Zeilen J4, R12–R14, U5, D2, Q1, J5; C1-C3 → C1-C2; J1-Funktion ändern | |

**Layout** (`placement_einseitig.py`, `gen_main_pcb.py`, nur beschreiben):

- **J4** oben, Öffnung 0,7 mm hinter der Kante +y, Mitte x ≈ 15,3. Seite „F“; die THT-Laschen gehen durch.
- **Weichen müssen:**
  - C3 (gestrichen)
  - R4 an die Kante +y bei x ≈ 21,5
  - C8 und C11 in das Band y < −1,6
  - U4 und C15 rechts neben J4 (x ≈ 21–22)
  - J1 auf die Unterseite an die Kante −y
- **ESD, Q1, D2** ins Band y < −1,6 zwischen C2 und U3. ESD direkt hinter den D+/D−-Pads von J4.
- `preroute_supply()`: Die VSYS-Schiene beginnt an Q1 (Source) und an der Kathode von D2 statt am Via von J1. J1-1 und J5 hängen an BAT_IN.
- Neue Vorroutings:
  - VBUS (die Pads A4/B9 bzw. B4/A9 sind fein, wie bei der Ladeplatine: Via hinter jedem VBUS-Pad, unten sammeln, 0,5 mm)
  - BAT_IN → Q1 → VSYS mit 0,6 mm und zwei Vias
- `preroute_outputs()`: Die OUT_B-Bahn unten bei y ≈ 5,6 muss an den vorderen Laschen (bis y ≈ 4,95) vorbei. Ggf. y = 5,8 nehmen und den Randabstand prüfen.
- Netzklassen: `/BAT_IN` und `/VBUS_J4` in die Klasse Power (0,4–0,6 mm). D+/D− als Paar kurz führen.
- `antenna_keepout()` bleibt unverändert, J4 liegt mehr als 25 mm von der Antenne weg.
- Danach wie gewohnt `just route`. Den Rest im GUI erledigen.

**Mechanik** (`huelle.scad`, nur beschreiben):
- Kabelfenster zum Buchsenfenster umbauen (`kabel_seite = +1`, `kabel_x` ≈ 15,3, `kabel_l` ≈ 13), mit Kragen um den Steckerkragen und Stützsteg unter J4.
- Platinen-Dummy um den Buchsenblock erweitern. Für die C-Hülse den Längsschlitz über die Buchse legen.

**Ladeplatine:** v0.1 bleibt nutzbar (J103-1 → BAT_IN, 4 Adern wie heute).
- Optional v0.2:
  - Kabelseite mit eigenem 4-poligem JST-Stecker (trennbar)
  - D102/Q101/R105 weglassen, weil das Load-Sharing A übernimmt (spart einen P-FET-Spannungsabfall)
- Daraus abgeleitet die **Gehäusebuchse**: USB-C, 2 × 5,1 k, ESD, Schottky, sonst nichts. Für Powerbank oder Netzteil in der Basis, wenn der Deckel zu bleiben soll.
- Hinweis „nur eine Buchse benutzen“ ins Verdrahtungsbild aufnehmen.

### Rückfall, falls die Probeplatzierung scheitert

1. **Variante 2** aus offene-punkte.md: wenige Passive (z. B. C8, C11, R4, C14) unten von Hand löten,
   **oder**
2. **Variante F:** nur Q1, R und Pads (BAT_IN, J5). Die Buchse bleibt auf Ladeplatine bzw. Gehäusebuchse;
   Erst-Flashen über ein USB-C-Breakout an J1.

**Nicht empfohlen:** D (passt nicht, Wärme), G (siehe Kapitel 6), USB-Mux, Mid-Mount- und vertikale
Buchsen, Buck-Boost statt LDO (nur bei Brownouts im Prototyp).

---

## 8. Vor der Umsetzung prüfen

| # | Punkt | Wie |
|---|---|---|
| U1 | Passt E wirklich? | Probeplatzierung in einer **Kopie** des Projekts (z. B. `placement_usb.py`) mit Courtyard-Check und einem Freerouting-Lauf |
| U2 | 3D-Kollision Buchse ↔ AA-Hüllkurve, Fachrand, Deckel | KiCad-STEP-Export + `huelle.scad` (Platinen-Dummy um J4 erweitern), am echten Fach messen (wie L1) |
| U3 | Rds(on) AO3401A bei Vgs = −3,0 V; Wärme bei 2 A; Verpolschutz | Datenblatt, Prototyp mit Labornetzteil |
| U4 | D+/D−-Stichleitung (zwei Buchsen, Kabel 15–30 cm) | Flashen mit beiden Kabellängen, `esptool` mehrfach |
| U5 | LCSC-Status (Basic/Extended, Lager) für AO3401A, Schottky, ESD-SOT-666, BAT54C, HCTL/XKB-Zweitquelle | JLC-Teilesuche |
| U6 | Schlafstrom mit Zelle direkt | messen; ggf. LDO mit kleinem Ruhestrom (A3) |
| U7 | Platz für 18650/14500-Halter in der Basis von neuem und altem Louie | nachmessen |
| U8 | Stecken in 0,8 mm: Halt der Laschen (E) | 50 Steckzyklen am Prototyp, seitlich belasten |

---

## Quellen

Abgerufen am 02.11.2026, soweit nicht anders angegeben. Footprint-Maße aus der KiCad-9-Bibliothek
(`/usr/share/kicad/footprints/Connector_USB.pretty`).

- [jlc-hro]: https://jlcpcb.com/partdetail/C165948 · LCSC: https://lcsc.com/product-detail/C165948.html
- [hctl]: https://datasheet.lcsc.com/lcsc/2211161000_HCTL-HC-TYPE-C-16P-01A_C2894897.pdf
- XKB U262: https://datasheet.lcsc.com/szlcsc/1811141824_XKB-Enterprise-U262-161N-4BVC11_C319148.pdf
- SHOU HAN 2MD(073): https://www.lcsc.com/product-detail/C2765186.html
- [jlc-cb16]: https://jlcpcb.com/partdetail/TYPE-C%2016P%20CB1.6%20073/C2906290 · [lcsc-cb16]: https://www.lcsc.com/product-detail/C2894902.html
- [ti-lm66100]: https://www.ti.com/product/LM66100
- [ti-ts3usb]: https://www.ti.com/product/TS3USB221A
- [idf-usj]: https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-guides/usb-serial-jtag-console.html
- Microchip AN1149 (Load-Sharing), wie in [ladeplatine.md](ladeplatine.md)
- USB-IF, Type-C Cable and Connector Specification (Kabeladern, Steckkräfte): https://www.usb.org/documents (Werte im Text unsicher)

[jlc-hro]: https://jlcpcb.com/partdetail/C165948
[hctl]: https://datasheet.lcsc.com/lcsc/2211161000_HCTL-HC-TYPE-C-16P-01A_C2894897.pdf
[jlc-cb16]: https://jlcpcb.com/partdetail/TYPE-C%2016P%20CB1.6%20073/C2906290
[lcsc-cb16]: https://www.lcsc.com/product-detail/C2894902.html
[ti-lm66100]: https://www.ti.com/product/LM66100
[ti-ts3usb]: https://www.ti.com/product/TS3USB221A
[idf-usj]: https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-guides/usb-serial-jtag-console.html
