# Offene Punkte, Annahmen und Alternativen

Stand: 2026-11-01 · Zum gemeinsamen Durchgehen. Bitte direkt hier kommentieren oder abhaken.

## Zwischenstand Layout Hauptplatine

| Variante | Ergebnis |
|---|---|
| **1: einseitig bestückt** (alles oben) | **Passt nicht.** Selbst dicht gepackt mit 0,4 mm Abstand und ohne Platz für Leiterbahnen bleiben 12 Bauteile übrig (`just pcb einseitig`). Neben dem Modul sind nur ca. 25 × 13 mm frei; die Bauteile bräuchten ca. 75 % dieser Fläche als reine Courtyard-Fläche. Mit zwei Lagen ist das nicht routbar. |
| **2: oben Maschine, unten Handlöten** | **Passt mit Reserve.** Oben 14 Bauteile (Modul, DRV8833, LDO, Puffer-/Abblockkondensatoren, Shunt, Stecker), unten 15 Kleinteile in 0603 plus Testpads und Endkontakte als reine Kupferflächen. Unten ist noch etwa die Hälfte frei. Platzierung ist DRC-sauber, Routing steht aus. |
| 3: beidseitig maschinell | nicht nötig (Variante 2 kann man auch beidseitig bestücken lassen, falls günstiger) |
| A + B (zwei Platinen) | **nicht nötig.** Platine B bleibt eine reine Brücke. |

Bilder: `just plot` → `build/main-board/placement.png`, `just render` → `build/main-board/render/`.

---

## Offene Fragen (Entscheidung durch dich)

| # | Frage | Optionen | Empfehlung |
|---|---|---|---|
| F1 | **Antenne und Endkontakt am selben Ende.** Das Modul liegt zwangsläufig mit der Antenne an einem Platinenende, dort sitzt aber auch der Batteriekontakt (Metall) und es muss eine Leiterbahn (MOT_A) zum Kontakt. Aktuell: 1,2 mm Streifen am Rand frei für diese Bahn. | a) so lassen und per Funktest prüfen · b) ESP32-C3-MINI-1**U** mit u.FL und kleiner Draht-/Flexantenne · c) Kontakt am Antennen-Ende über einen Draht außen an der Platine vorbei · d) Chip-Design (ESP32-C3FH4 + Chip-Antenne mittig), aufwendig | a) mit frühem Funktest am Steckbrett-Prototyp; b) als Plan B |
| F2 | **Kabelabgang J1:** Der JST-Stecker zeigt zur Platinenseite (+y). Wie kommt das Kabel aus dem Batteriefach (neues Modell: Deckel; altes Modell: offen)? | a) JST seitlich (jetzt) · b) Lötpads statt Stecker (spart Platz und Bauhöhe) · c) stehender JST (BM04B) · d) Stecker auf Brückenplatine B | am Fach ausprobieren; b) ist am robustesten |
| F3 | **Endkontakte (Mechanik):** Aktuell nur 2 × 2 mm Platzhalter-Pads unten an den Enden. | a) gebogene Lötfahnen wie beim Salto Sammy · b) Batteriekontakt-Clips (z. B. Keystone SMD) · c) Messingkappe/-niete · d) Federblech | Salto-Prinzip ansehen (Referenzkauf), dann entscheiden |
| F4 | **Halt der Platine im AA-Fach:** Die Platine liegt flach in einer runden Mulde. Wer zentriert sie und schützt die Unterseiten-Bauteile? | a) 3D-gedruckte Halbschale (wie C-Hülse, nur AA) · b) Schrumpfschlauch · c) nur durch Kontakte gehalten | a) |
| F5 | **Strapping-Pins IO2/IO8/IO9:** Sind die 10k-Pull-ups an IO2 und IO8 nötig? | Datenblatt ESP32-C3 prüfen; ggf. R10/R11 streichen | prüfen vor Bestellung |
| F6 | **LED D1** sitzt unten und ist im Fach nicht sichtbar. | a) behalten (Debug) · b) streichen · c) nach oben | a), kostet fast nichts |
| F7 | **Platinendicke 0,8 mm** (wegen Modulhöhe in der AA-Hülle). | 0,8 mm (Aufpreis bei manchen Herstellern) · 1,0 mm · 0,6 mm | Kostenabschätzung abwarten |
| F8 | **Bestückungsstrategie final.** | Variante 2 · einseitig mit 0402-Passiven (siehe Alternative unten) | Variante 2, nach Routing neu bewerten |
| F9 | **Lizenz** für Hardware und Firmware. | z. B. CERN-OHL-S/-P (Hardware), MIT/GPL (Firmware) | offen |
| F10 | **Ladeplatine:** Teile mit Status „zu prüfen“ in `hardware/bom/teile.csv`. | – | beim Ladeplatinen-Design |
| F12 | **ESP32-C3-MINI-1-N4 ist laut Mouser abgekündigt** (nicht für neue Designs). Nachfolger: ESP32-C3-MINI-1-**N4X**, pinkompatibel. | Lagerbestand bei JLCPCB/LCSC prüfen, LCSC-Nummer des N4X ermitteln und umstellen | umstellen, sobald verfügbar bestätigt |
| F13 | **Kosten:** Variante 2 entspricht kostenmäßig etwa Szenario A der [Kostenabschätzung](kostenabschaetzung.md) (einseitig maschinell, Economic), die Unterseite lötest du selbst. Ca. 9 €/Stück bei 10, ca. 3,40 €/Stück bei 100. | – | Angebot mit echten Daten einholen, wenn das Layout fertig ist |
| F11 | **Freerouting**: Ergebnis des Autorouters prüfen und ggf. von Hand nacharbeiten. | – | nach `just route` |

---

## Annahmen (bitte prüfen)

| # | Annahme | Warum unsicher | Erwogene Alternativen |
|---|---|---|---|
| A1 | Die Platine liegt leicht unter der Mitte der AA-Hülle, das Modul hat an den Ecken ca. **0,1 mm Luft**. | Theoretischer Wert; Fächer haben Spiel, aber keine Garantie. | dünnere Platine (0,6 mm), Platine tiefer legen, Chip-Design ohne Modul |
| A2 | **Motorstrom < 1 A**, DRV8833 parallel mit 2 A Begrenzung reicht. | Nicht gemessen. | DRV8871/DRV8876 (brauchen ≥ 4,5–6,5 V), TB6612 (≥ 4,5 V), nur MOSFET (kein Rückwärts) |
| A3 | **AP2112K** genügt; unter ca. 3,5 V Akku sinkt 3V3 leicht, ESP32-C3 läuft ab 3,0 V. Ruhestrom 55 µA. | Bei leerem Akku Brownout-Risiko bei WLAN-Spitzen. | TLV75533 (25 µA, ähnlich), Buck-Boost (z. B. TPS63802) für stabile 3,3 V bis 2,7 V Akku |
| A4 | **Hebel-Erkennung** mit 100k/10k/100k funktioniert: Hebel zu ≈ 0,3 V, offen ≈ 3,3 V; Deep-Sleep-Wake auf IO3. | Abhängig vom Motorwiderstand und Leckströmen des DRV8833 im Sleep. | Komparator, aktiver Messimpuls über die H-Brücke |
| A5 | **Akkuspannungs-Teiler 470k/470k** mit 100 nF ist genau genug. | Hochohmig, ESP-ADC-Eingang belastet. | 100k/100k (21 µA Dauerstrom), Teiler per MOSFET schaltbar |
| A6 | **Shunt 0,1 Ω**: Strombegrenzung 2 A und Strommessung über ADC (max. 200 mV) reichen für Hebel-Erkennung während der Fahrt. | ADC-Auflösung bei kleinen Strömen. | 0,2 Ω (1 A Grenze, doppelte Messspannung) |
| A7 | **WLAN-Reichweite** reicht trotz Motor und Metallkontakten in der Nähe. | Siehe F1. | ESP32-C3-MINI-1U |
| A8 | **USB (Full Speed) über das 4-adrige Kabel** und den JST-Stecker funktioniert. | Kurzes, ungeschirmtes Kabel – meist unkritisch. | Nur OTA + einmaliges Flashen über Testpads (2-adriges Kabel) |
| A9 | **Designregeln** 0,15 mm Bahn/Abstand, Via 0,3/0,6 mm fertigt jeder Hersteller zum Standardpreis. | Herstellerabhängig. | 0,2 mm Regeln (mehr Platzbedarf) |
| A10 | **Vias im Thermal-Pad** des DRV8833 (ungefüllt) sind für die Maschinenbestückung ok. | Lot kann in die Vias abfließen. | gefüllte/abgedeckte Vias (Aufpreis), Vias neben dem Pad |
| A11 | **LCSC-Footprint des ESP32-C3-MINI-1** stimmt mit dem Datenblatt überein. | Von easyeda2kicad konvertiert, nicht gegen das Datenblatt geprüft. | eigenen Footprint nach Datenblatt zeichnen – **vor Bestellung prüfen!** |
| A12 | **Loopin' Chewie** hat 2 × AA. | Nicht gesehen. | wird sonst nicht unterstützt (deine Vorgabe) |
| A13 | Die **Unterseiten-Bauteile** (max. ca. 0,9 mm hoch) stören in der AA-Hülle nicht. | Abhängig von F4. | – |
| A14 | **Testpads** (3V3, GND, EN, BOOT, TXD, RXD) reichen für Erstinbetriebnahme und Notfall-Flashen. | – | Tag-Connect-Footprint (größer) |

---

## Getroffene Entscheidungen und verworfene Alternativen

| Thema | Entscheidung | Verworfen, weil |
|---|---|---|
| Befehls-Runner | `just` | make: altmodische Syntax; mise: Kern ist Versionsverwaltung, KiCad nicht installierbar |
| Schaltplan | per Skript erzeugt (`just schematic`), danach GUI | atopile/SKiDL: kein normaler Schaltplan für Nachbauer |
| Symbole | KiCad-Standard, eigene für ESP32-C3-MINI-1 und DRV8833-parallel | LCSC-Symbole ohne Pin-Typen → ERC wertlos |
| Eine oder zwei Platinen im Fach | **eine** Hauptplatine + reine Brücke | A/B-Aufteilung: Kabel zwischen den Fächern, nicht nötig |
| Bestückung | Variante 2 (oben Maschine, unten Hand) | einseitig passt nicht (siehe oben) |
| **Alternative noch offen:** einseitig mit 0402 | Mit 0402-Passiven (≈ 40 % der 0603-Fläche) käme man oben auf ca. 60 % Belegung – immer noch sehr eng, nur maschinell bestückbar. | erst nach dem Routing von Variante 2 bewerten |
| DRV8833-Footprint | ohne eingebaute Thermal-Vias (die haben 0,2 mm Bohrung), eigene 0,3-mm-Vias | 0,2 mm kostet bei vielen Herstellern Aufpreis |
| Bestückungsdruck | Bezeichner nur auf der Fab-Ebene | auf 13,5 mm Breite nicht lesbar unterzubringen |
| Endkontakt-Pads | 2 × 2 mm Platzhalter | 3 × 3 mm kollidiert mit der Antennen-Sperrfläche |
| Routing | Freerouting (Autorouter) als Startpunkt | Skript-Routing: unrealistisch; nur Hand-Routing: dauert, kommt danach |

---

## Ideen (später analysieren)

### I1: Versorgung über USB-C-Akku-AA-Zellen statt LiPo + Ladeplatine

Idee: Bei den 2×AA-Modellen eine handelsübliche, per USB-C ladbare AA-Zelle als Stromquelle nutzen
(z. B. im zweiten Fach statt der Brücke). Laden wäre dann gelöst, Ladeplatine und externer Akku entfallen.

Erste Gedanken, noch nicht geprüft:
- Solche Zellen liefern **konstant 1,5 V** (interner Li-Ion-Akku + Abwärtswandler). Eine Zelle reicht nicht
  für ESP32 (3,3 V) und Motor → bräuchte einen Aufwärtswandler auf der Hauptplatine. Motorspannung über
  1,5 V hinaus (Turbo) ebenfalls nur per Aufwärtswandler.
- Belegt ein Fach → die Hauptplatine müsste dann allein in das andere Fach, und die Fachbrücke/Kontakte
  ändern sich (Akku-Zelle und Hauptplatine wären in Reihe statt Brücke).
- Strombelastbarkeit dieser Zellen (oft 2–3 A max., interne Schutzabschaltung) und Kapazität
  (meist 1500–2500 mWh) prüfen.
- Beim alten Modell (1× C) nicht direkt übertragbar.

### I2: USB-C-Buchse direkt auf der Hauptplatine, nach oben zeigend

Idee: Eine USB-C-Buchse senkrecht ("vertical"/"upright") auf der Platine, Öffnung nach oben bzw. zur Seite,
sodass man wie bei einer USB-C-Akkuzelle direkt ein Kabel an die Platine im Fach stecken kann.

Erste Gedanken, noch nicht geprüft:
- Es gibt **vertikale USB-C-Buchsen** (Platinenmontage, Stecker kommt senkrecht von oben) und
  **mid-mount**-Varianten. Bauhöhe vertikal meist 6–10 mm → passt in der AA-Hülle nur am Rand der Kurve
  bzw. gar nicht; mid-mount (Platinenausschnitt) könnte passen. Zu prüfen.
- Dann könnte der Laderegler auf die Hauptplatine; der Akku bleibt extern (oder I1).
- Zugänglichkeit: neues Modell hat einen Deckel → Buchse nur bei offenem Fach erreichbar.
