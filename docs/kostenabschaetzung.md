# Kostenabschätzung: Fertigung und Bestückung der Hauptplatine

**Stand der Recherche:** 01.11.2026 (Web-Recherche, keine Angebote eingeholt, keine Logins/Bestellungen)
**Wechselkurs:** 1 EUR ≈ 1,13 USD → **1 USD ≈ 0,885 EUR** (Kurs Okt. 2026 lag zwischen ca. 1,12 und 1,16; Schwankung ±3 % geht direkt in alle Preise ein)

**Platine:** 46 × 13,5 mm (6,2 cm²), 2 Lagen, FR4 0,8 mm, 0,15/0,15 mm, Via 0,3/0,6 mm, grüne Maske, ca. 38 Bestückpositionen / 15 Teiletypen, ca. 135 Lötstellen pro Platine.

> **Entscheidung 2026-11-03: Die Hauptplatine wird mit 4 Lagen gefertigt** (JLC04081H-3313, 0,8 mm, Regeln 0,15/0,15 mm, Via 0,3/0,5 mm; [hauptplatine-c6.md](hauptplatine-c6.md) Kapitel 11). Die Rechnungen in Abschnitt 1–3 gehen noch von 2 Lagen aus; die Mehrkosten für 4 Lagen stehen in Abschnitt 5 (ca. +3 / +6 / +10 € pro Auftrag bei 5 / 10 / 30 Stück, unsicher).

> **Legende:** **[Q]** = aus einer Quelle (siehe Abschnitt 4) belegt · **[S]** = eigene Schätzung / Hochrechnung, nicht verifiziert.
> Alle Endpreise sind **[S]**, weil sie aus belegten Einzelgebühren plus geschätzten Werten (Platinenpreis bei Menge, Versand, Ausschuss) zusammengesetzt sind. Ein echtes Angebot (JLCPCB-Rechner mit Gerber + BOM + CPL) ersetzt diese Rechnung.

---

## 1. Kurzfazit

- **Günstigster Anbieter: JLCPCB.** Szenario A (einseitig) mit *Economic PCBA*, Szenario B (beidseitig) geht bei JLCPCB **nur mit Standard PCBA** (Economic ist laut JLC-Capabilities nur einseitig).
- **Beidseitig kostet bei JLCPCB einmalig ca. 60–70 USD mehr** (Setup 51 statt 8 USD, Schablone 16 statt 1,5 USD) und erzwingt ein Nutzen-Panel mit Randstreifen (Standard PCBA min. 70 × 70 mm). Bei 5–10 Stück verdoppelt das fast den Preis; ab ca. 50 Stück ist der Unterschied nur noch ca. 1 €/Platine.
- Unterhalb ca. 25 Stück dominieren Fixkosten (Setup, Extended-Teile, Schablone, Versand). Ab ca. 50 Stück dominieren Bauteile (ESP32-Modul ≈ 1 USD, DRV8833 ≈ 0,45 USD) und die **Röntgenprüfung des ESP32-Moduls** (LGA, Pflicht bei JLC).

### Gesamtkosten in EUR inkl. Versand, Einfuhr-USt 19 % und Zoll (JLCPCB) **[S]**

| Menge | **A: einseitig (Economic)** gesamt | A pro Platine | Spanne A gesamt | **B: beidseitig (Standard)** gesamt | B pro Platine | Spanne B gesamt |
|---:|---:|---:|---:|---:|---:|---:|
| 5   | **≈ 67 €**  | ≈ 13,40 € | 55–85 €   | **≈ 143 €** ¹ | ≈ 28,60 € ¹ | 125–175 € |
| 10  | **≈ 94 €**  | ≈ 9,40 €  | 80–115 €  | **≈ 143 €**   | ≈ 14,30 €   | 125–175 € |
| 25  | **≈ 143 €** | ≈ 5,70 €  | 120–170 € | **≈ 185 €**   | ≈ 7,40 €    | 160–220 € |
| 50  | **≈ 235 €** | ≈ 4,70 €  | 200–280 € | **≈ 270 €**   | ≈ 5,40 €    | 235–320 € |
| 100 | **≈ 340 €** | ≈ 3,40 €  | 290–410 € | **≈ 385 €**   | ≈ 3,90 €    | 330–460 € |

¹ Bei Standard PCBA mit 5er-Nutzen ist die Mindestbestückung 2 Panels = 10 Platinen; „5 Stück" kostet daher praktisch so viel wie 10.

**Spanne:** untere Grenze = nur 3 Extended-Teiletypen, günstigster Versand, kein Zusatzausschuss; obere Grenze = 6 Extended-Typen, DHL/Express, Bauteil-Mindestmengen, ENIG.

### Vergleich andere Anbieter (10 Stück, Szenario A) **[S]**

| Anbieter | ca. gesamt (10 Stk.) | Bemerkung |
|---|---:|---|
| JLCPCB Economic | ≈ 80–115 € | Sofortpreis online, LCSC-Teilelager |
| PCBWay | ≈ 110–170 € | Bestückung „ab 29 USD / bis 20 Stk." (Aktion) [Q], Teile über DigiKey/Mouser (teurer), Angebot nur manuell (1–2 Tage), DHL-Versand teurer |
| Aisler (DE) | ≈ 300–400 € | Kein Zoll, Fertigung in DE/EU, aber 75 € Setup + 0,38 €/Bauteilposition×Stück (ältere Preisliste) [Q] → ca. 14 €/Platine nur Bestückung |
| Eurocircuits (BE) | > 300 € (nicht verifiziert) | Nur per Online-Rechner mit Daten; für Kleinserien erfahrungsgemäß deutlich teurer als China |

---

## 2. Aufschlüsselung

### 2.1 Leiterplatte (JLCPCB)

| Posten | Wert | Quelle |
|---|---|---|
| 2 Lagen ≤ 100 × 100 mm, 5 Stk. | 2 USD | [Q] |
| Dicke 0,8 mm | **kein Aufpreis** bei 2 Lagen, grüner Maske (0,8/1,0/1,2/1,6 mm frei) | [Q] techoverflow |
| Economic PCBA erlaubt Dicke | 0,8–1,6 mm → 0,8 mm ist ok | [Q] |
| Kleine Platine (eine Seite < 15 mm, Lieferung als Einzelplatine) | +0,05 USD/Stk. | [Q] |
| HASL bleifrei | ca. +1–1,5 USD pro Auftrag | [Q]/[S] |
| ENIG | ca. +16 USD bei Kleinmengen | [Q] (Forum) / [S] |
| Regeln 0,13 mm / Via 0,3/0,6 mm | Standard, kein Aufpreis (JLC 2 Lagen 1 oz: 0,10/0,10 mm; Aufpreis bei Bohrung 0,1/0,15 mm bzw. 0,2/0,25 mm mit Ø < 0,45 mm), siehe hauptplatine-c6.md „Fertigungsregeln“ | [Q] |
| 10 / 25 / 50 / 100 Stk. | ca. 5 / 8 / 12 / 18 USD inkl. Zuschläge | [S] |

**HASL bleifrei vs. ENIG:** HASL ist billiger, aber leicht uneben. ENIG (Nickel/Gold) ist plan, lagerfähiger und besser für feine Pads (HTSSOP-16, LGA-Pads des ESP32-Moduls). Für maschinelle Bestückung mit Schablone funktioniert bleifreies HASL bei diesen Bauformen in der Praxis meist problemlos. Mehrkosten ENIG ca. 10–15 € pro Auftrag → bei 5–10 Stück spürbar, bei 100 Stück vernachlässigbar.

**Szenario B:** Standard PCBA braucht mind. 70 × 70 mm Panel mit Randstreifen. Vorschlag: 5 Platinen übereinander (5 × 13,5 mm + Fräsabstände) mit ca. 12 mm breiten Randstreifen links/rechts → ca. 70 × 80 mm, bleibt im 100 × 100 mm-Preisband. **[S]**

### 2.2 Bestückungsgebühren JLCPCB [Q]

| Gebühr | Economic (A) | Standard (B, beidseitig) |
|---|---:|---:|
| Setup | 8,18 USD | 51,12 USD (einseitig 25,56) |
| Schablone | 1,53 USD | 16,42 USD (einseitig 8,21) |
| Extended-Teil (je Typ) | 3,07 USD (Preferred Extended: 0) | 1,53 USD |
| Lötstelle SMT | 0,0016 USD | 0,0016 USD |
| Mindest-SMT-Betrag pro Platine/Panel | 0,48 USD | 0,48 USD |
| Röntgen (LGA/QFN/BGA, pro Bauteil) | 1–10: 1,64 · 11–50: 0,82 · 51–200: 0,49 USD | gleich |
| Verpackung | frei | 0,50 USD + Fläche |
| Menge | 2–50 (Einzelplatinen oder Panels) | 2–80 000 |
| Platinengröße | ab 10 × 10 mm | ab 70 × 70 mm (→ Panel nötig) |
| Seiten | **nur einseitig** | ein- und beidseitig |

**Annahmen zur Platine [S]:**
- Lötstellen: ESP32-C3-MINI-1 ≈ 53, DRV8833 17, LDO 5, JST 6, 27 Zweipoler 54 → **≈ 135 Lötstellen = 0,22 USD**. Liegt unter dem Mindestbetrag 0,48 USD → bei Einzelplatinen wird auf 0,48 USD aufgefüllt; im 2er-/5er-Nutzen entfällt das praktisch.
- **Extended-Teile: 4–6 Typen** angenommen (ESP32-C3-MINI-1, DRV8833, JST SM04B sicher Extended; AP2112K, 47 µF/1206 und 0,1 Ω/0805 je nach gewählter LCSC-Nummer evtl. Basic/Preferred). Rechenbasis: 5 Typen → Economic 15,35 USD, Standard 7,65 USD. Status nicht verifiziert (JLC-Teileseiten zeigen den Status ohne JavaScript nicht an).
- **Röntgen:** nur für das ESP32-Modul angenommen (die JLC-Teileseite markiert es als röntgenpflichtig [Q]). Falls auch DRV8833 (Exposed Pad) gezählt wird, ändert sich die Staffel – Gesamteffekt gering.
- Ausschuss/Mindestmengen der Teile: pauschal 3–5 USD pro Auftrag.

### 2.3 Bauteile (LCSC/JLC-Preise in USD pro Stück)

| Teil | 1+ | 10+ | 30+ | 100+ | Quelle |
|---|---:|---:|---:|---:|---|
| ESP32-C3-MINI-1-N4 (C2838502) | 1,29 | 1,09 | 1,05 | 1,01 | [Q] |
| DRV8833PWPR (C50506) | 0,64 | 0,51 | 0,45 | ≈ 0,40 | [Q] / 100+ [S] |
| AP2112K-3.3TRG1 (C51118) | ≈ 0,08 | | | ab 0,055 | [Q] Staffelende / [S] |
| JST SM04B-SRSS-TB (C160404) | ≈ 0,17 | | | ≈ 0,13 | [Q] Großmenge 0,12 / [S] |
| 3× 47 µF 1206, 1× 10 µF 0805 | ≈ 0,13 gesamt | | | ≈ 0,10 | [S] |
| ca. 10× C 0603, 11× R 0603, 0,1 Ω 0805, LED | ≈ 0,07 gesamt | | | ≈ 0,05 | [S] |
| **Summe pro Platine** | **≈ 2,40** | **≈ 2,30** | **≈ 2,10** | **≈ 1,80** | [S] |

Zum Vergleich in DE/EU: ESP32-C3-MINI-1-N4 bei DigiKey ca. 2,72 € (1 Stk.) bis 1,67 € (650+), Comet ca. 1,92 € [Q]. **Wichtig:** Mouser führt das **ESP32-C3-MINI-1-N4 als obsolet/NRND**; Nachfolger ist **ESP32-C3-MINI-1-N4X** (Chip-Revision v1.1, pinkompatibel) [Q]. Vor der Bestellung JLC-Lagerbestand prüfen; ggf. auf N4X umstellen (eigene LCSC-Nummer suchen).

### 2.4 Versand, Steuern, Zoll

| Posten | Wert | Quelle |
|---|---|---|
| JLC „Global Standard Direct Line" | billigste Option, nur bei Warenwert ≤ 59 USD | [Q] |
| Europacket (DDP) | Beispiel Jan. 2026: 7,90 € | [Q] |
| DHL Express | ca. 20–35 USD | [S] |
| Einfuhrumsatzsteuer 19 % | auf Ware + Versand; bis 150 € Warenwert per IOSS beim Bestellen bezahlt, darüber beim Import (DDP oder Zusteller) | [Q] |
| **EU-Zoll seit 01.07.2026** | 150-€-Zollfreigrenze abgeschafft; pauschal **3 € Zoll pro Warenkategorie** bei Sendungen < 150 € (bis 07/2028) | [Q] |
| Zoll über 150 € | regulärer Satz; für bestückte Leiterplatten typ. 0–3 % | [S] |
| Abfertigungsgebühr Zusteller (ohne DDP) | 3–15 € | [Q] |

In der Tabelle angesetzt: Versand 6 / 8 / 10 / 12 / 15 € (5/10/25/50/100 Stk.), darauf 19 % USt, plus 3 € bzw. ca. 2 % Zoll. **[S]**

### 2.5 Rechenweg (Beispiel A, 10 Stück) [S]

| Posten | USD |
|---|---:|
| Setup + Schablone | 9,71 |
| 5 Extended-Typen × 3,07 | 15,35 |
| Leiterplatten 10 Stk. inkl. HASL bleifrei / Kleinzuschlag | ≈ 5,00 |
| SMT 10 × 0,48 (Mindestbetrag) | 4,80 |
| Bauteile 10 × 2,30 | 23,00 |
| Röntgen ESP32 10 × 1,64 | 16,40 |
| Ausschuss/MOQ-Puffer | 3,00 |
| **Summe netto** | **≈ 77 USD ≈ 68 €** |
| + Versand 8 €, × 1,19 USt, + 3 € Zoll | **≈ 94 €** |

Das Gleiche für B (10 Stück): Setup + Schablone 67,54 + Extended 7,65 + Verpackung + Panel-PCB ≈ 4 + 10 × (0,22 + 2,30 + 1,64) + Puffer ≈ 124 USD → ≈ 143 € brutto.

---

## 3. Kostentreiber und Sparmöglichkeiten

**Größte Kostentreiber (kleine Mengen):**
1. **Beidseitige Bestückung** → bei JLC Wechsel auf Standard PCBA: +43 USD Setup, +15 USD Schablone, Panel mit Randstreifen nötig, Mindestmenge praktisch 10 Stück.
2. **Extended-Teile** bei Economic: 3,07 USD je Typ → 5 Typen = 15 USD, egal ob 5 oder 50 Platinen.
3. **Röntgenprüfung ESP32-Modul:** 1,64 USD/Stk. bis 10 Stk., dann 0,82 / 0,49 USD → bei 5–10 Stück so teuer wie das Modul selbst.
4. **Versand/Steuern:** feste Versandkosten + 19 % USt + seit Juli 2026 3 € Zoll; bei 5 Stück ca. 25 % des Gesamtpreises.
5. **Bauteile** (vor allem ESP32-Modul) dominieren ab ca. 50 Stück.

**Sparmöglichkeiten:**
- **Einseitig bestücken (Szenario A)** – spart bei 5–25 Stück ca. 40–75 €. Die Platine ist schmal (13,5 mm), deshalb das Layout prüfen; falls einseitig nicht passt: Unterseite (15× 0603) per Hand löten und oben Economic bestücken lassen.
- **Economic statt Standard** – möglich bei einseitig, Dicke 0,8–1,6 mm, ≤ 50 Einheiten. Für 100 Stück als **2er-Nutzen** bestellen (50 Panels), das bleibt im Economic-Rahmen und vermeidet den Mindest-SMT-Betrag.
- **Nutzen selbst anlegen** (Mausbiss-Stege, KiKit), bei Economic ohne Randstreifen; JLC berechnet Panel-Gebühr nur bei mehreren *verschiedenen* Designs. Spart Mindest-SMT-Betrag und Kleinplatinen-Zuschlag.
- **Basic/Preferred-Teile wählen:** Passive (47 µF, 0,1 Ω, LED) und ggf. LDO gezielt aus der Basic- bzw. Preferred-Extended-Liste nehmen → jeder vermiedene Extended-Typ spart 3,07 USD (Economic).
- **HASL bleifrei statt ENIG** bei Kleinmengen (spart ca. 10–15 €).
- **Mengenstaffel nutzen:** zwischen 10 und 25 Stück steigt der Gesamtpreis nur um ca. 50 €, während der Stückpreis von ca. 9 € auf ca. 6 € fällt.
- **Unter 150 € Warenwert bleiben** (IOSS, keine Nachverzollung durch Zusteller) bzw. DDP-Versand wählen.
- **Teile vorkaufen** („Parts Pre-order") lohnt erst bei größeren Mengen bzw. knappen Teilen (ESP32-N4 ist abgekündigt).

---

## 4. Quellen

Abgerufen am 01.11.2026.

**JLCPCB**
- Bestückungspreise (Setup, Schablone, Extended, Röntgen, Mindestbetrag): https://jlcpcb.com/help/article/pcb-assembly-price
- PCBA-FAQ (Panelisierung Economic, Preferred Extended): https://jlcpcb.com/help/article/98-pcb-assembly-faqs, https://jlcpcb.com/help/article/pcb-assembly-faqs
- Fähigkeiten Economic vs. Standard (Größe, Dicke, einseitig, Menge, Randstreifen): https://jlcpcb.com/capabilities/pcb-assembly-capabilities
- Aufpreise (kleine Platinen, ENIG, Bohrungen): https://jlcpcb.com/help/article/In-what-cases-will-there-be-charged-extra
- Kostenlose Dicken: https://techoverflow.net/2024/11/26/what-pcb-thickness-options-are-free-of-charge-on-jlcpcb/
- Übersicht PCBA-Preise (2024): https://techoverflow.net/2024/04/09/jlcpcb-pcba-assembly-price-overview/
- Spartipps: https://hwdocs.hackclub.dev/user-contrib-guides/jlc-cost-optimizing/
- ESP32-Teileseite (Röntgen-Hinweis): https://jlcpcb.com/partdetail/C2838502
- Versand nach DE: https://www.eevblog.com/forum/manufacture/jlcpcb-shipping, https://www.mikrocontroller.net/topic/569557

**Bauteile**
- ESP32-C3-MINI-1-N4: https://www.lcsc.com/product-detail/C2838502.html, https://fat.lcsc.com/product-detail/RF-Modules_Espressif-Systems-ESP32-C3-MINI-1-N4_C2838502.html
- Status obsolet/NRND (Mouser): https://www.mouser.at/ProductDetail/356-ESP32-C3-MINI1N4 ; Nachfolger N4X: https://www.embeddedrelated.com/parts/p/ESP32-C3-MINI-1-N4X
- DigiKey/Comet (EUR): https://punchouttest.digikey.es/en/products/detail/espressif-systems/ESP32-C3-MINI-1-N4/13877574, https://store.comet.bg/en/CatalogueSchukat/Product/3068973
- DRV8833PWPR: https://www.lcsc.com/product-image/C50506.html
- AP2112K-3.3TRG1: https://www.lcsc.com/product-image/C51118.html, https://origin-www.findchips.com/search/AP2112K-3.3TRG1
- JST SM04B-SRSS-TB: https://www.lcsc.com/product-image/C160404.html

**Andere Anbieter**
- PCBWay Bestückung: https://www.pcbway.com/pcb-assembly.html ; Online-Rechner: https://www.pcbway.com/orderonline.aspx
- Aisler Preise: https://community.aisler.net/t/our-simple-pricing/102 ; https://aisler.net/de
- Eurocircuits: https://www.eurocircuits.com

**Steuern/Zoll/Kurs**
- EU 3-€-Zoll ab 01.07.2026: https://www.pwc.dk/en/articles-publications/2026/eu-abolishes-the-150-low-value-customs-duty-threshold-from-1-july-2026.html, https://globalimportblog.bakermckenzie.com/2026/07/02/eu-low-value-consignment-relief-abolished-and-eur-3-customs-duty-introduced-from-1-july-2026/
- EUR/USD 2026: https://www.poundsterlinglive.com/history/EUR-USD-2026

### Was ist verifiziert, was geschätzt?

| Verifiziert [Q] | Geschätzt [S] |
|---|---|
| JLC-Bestückungsgebühren (Setup, Schablone, Extended, Lötstelle, Röntgen, Mindestbetrag) | Leiterplattenpreis für 10–100 Stück |
| JLC-Fähigkeiten Economic/Standard | Anzahl Extended-Typen (4–6) |
| 0,8 mm ohne Aufpreis, Kleinplatinen-Zuschlag | Preise der Passivbauteile, AP2112K/JST bei Kleinmenge |
| LCSC-Staffelpreise ESP32-C3-MINI-1-N4, DRV8833 | Versandkosten je Menge, Zollsatz über 150 € |
| EU-Zollregel 3 € ab 07/2026 | PCBWay-, Aisler- und Eurocircuits-Gesamtpreise |
| Aisler-Gebührenstruktur (Stand der Community-Seite, evtl. veraltet) | Alle Endsummen in den Tabellen |

Nicht verifiziert werden konnten: JLC-Basic/Extended-Status der einzelnen LCSC-Nummern, aktuelle Lagerbestände, PCBWay-Bestückungspreise (nur manuelles Angebot), Eurocircuits-Preise (Rechner braucht Daten), aktuelle Aisler-Bestückungspreise (die Preisseite kann älter sein).

---

## 5. 2 vs. 4 Lagen (Hauptplatine, Stand 02.11.2026)

**Gewählt: 4 Lagen** (Entscheidung des Auftraggebers 2026-11-03; die 2-Lagen-Variante blieb bei 13 offenen Verbindungen).

**Frage:** Wie viel teurer wird die Hauptplatine (46 × 13,5 mm = 6,2 cm², FR4 0,8 mm, 1 oz außen, einseitig bestückt), wenn sie statt mit 2 mit 4 Lagen gefertigt wird?

**Vorgehen:** Web-Recherche ohne Login und ohne eigenes Angebot. Der JLC-Online-Rechner (cart.jlcpcb.com/quote) liefert die Preise nur per JavaScript; er wurde nicht abgefragt. Die Leiterplattenpreise für 10–100 Stück sind deshalb Hochrechnungen aus veröffentlichten Grundpreisen und Forenberichten und als **(unsicher)** markiert. Belegte Einzelangaben sind mit **(geprüft)** markiert (Quelle am 02.11.2026 gelesen).

### 5.1 Kurzantwort

- **Leiterplatte:** 4 Lagen kosten bei JLCPCB für diese kleine Platine **ca. 3–20 USD mehr pro Auftrag** (5–100 Stück). Das sind **ca. 0,2–1 € pro Board** (unsicher).
- **Bestückung:** **keine Änderung.** Economic PCBA ist für 2, 4 und 6 Lagen und 0,8–1,6 mm zugelassen (geprüft). Keine JLC-Bestückungsgebühr hängt von der Lagenzahl ab (geprüft).
- **Lieferzeit:** Leiterplattenfertigung 2–5 Tage statt 1–2 Tage, also **ca. 1–3 Werktage länger** (geprüft für 1,6 mm/HASL; 0,8 mm unsicher).
- **Gesamtpreis bestückt (JLC, Szenario A):** steigt bei 5 / 10 / 30 Stück um ca. **3 / 6 / 10 € pro Auftrag** bzw. **0,60 / 0,60 / 0,35 € pro Board** (unsicher).
- **Nutzen:** 4 Lagen erlauben großzügigere Regeln (0,15/0,15 mm oder 0,2/0,2 mm statt 0,13 mm Abstand und 0,1 mm Bahn), eine durchgehende GND-Lage und lösen voraussichtlich die 17 offenen Verbindungen (hauptplatine-c6.md 8.5).

### 5.2 Leiterplatte allein (JLCPCB)

| Punkt | 2 Lagen | 4 Lagen | Status |
|---|---|---|---|
| Lockangebot 5 Stück | 2 USD bis 100 × 100 mm | 2 USD nur bis **50 × 50 mm** (unsere 46 × 13,5 mm passen) | geprüft (LCSC-Preisseite, Hack-Club-Leitfaden) |
| Wo gilt der 2-USD-Preis? | seit 22.08.2026 **nur noch in der Desktop-App JLCONE**, nicht mehr auf der Website | gleich | geprüft (JLC-News 22.08.2026); ob die 4-Lagen-Variante mitzählt: unsicher |
| Website-Preis 5 Stück | ca. 4 USD | „4 layers (10×10 cm) from 7 USD“; Forum März 2026: 100 × 100 mm, 5 Stk. = 5,92 € zzgl. Versand | geprüft (JLC-Werbeseite, mikrocontroller.net) |
| Flächenpreis größere Mengen | – | 70,6 USD/m² Platinenanteil; Beispiel 100 Stk. 100 × 100 mm = 106,30 USD gesamt (≈ 36 USD Fixanteil) | geprüft (JLC-News 03/2024, Preis seit 08/2026 „Standard-Basisrate“) |
| Ingenieurgebühr | ca. 3–4 USD | bei großen Boards (> 100 mm) bis 24 USD; bei kleinen Boards gering | Forum 02/2026, unsicher |
| Dicke 0,8 mm | ohne Aufpreis | **zulässig** (0,4–2,0 mm für 4 Lagen); Aufpreis nicht belegt. Toleranz unter 1,0 mm: ±0,1 mm | Zulässigkeit geprüft; Preis **unsicher** – im Rechner prüfen |
| 1 oz außen / innen | 1 oz Standard | 1 oz außen Standard, innen 0,5 oz Standard | geprüft |
| Kleinplatinen-Zuschlag (eine Seite < 15 mm, Einzelplatine) | 0,05 USD/Stk. | gleich | geprüft |
| Oberfläche HASL bleifrei | ca. +1–1,5 USD/Auftrag | ähnlich | unsicher |
| ENIG | ca. +16 USD bei Kleinmengen | ähnlich (+13–20 USD); Zuschlag, wenn ENIG-Fläche > 30 % der Platine | Zuschlagsregel geprüft, Betrag unsicher |
| Fertigungszeit (≤ 100 × 100 mm) | 5 Stk.: 24 h, < 50 Stk.: 1–2 Tage | 5–50 Stk.: **2–5 Tage** | geprüft (1,6 mm, HASL) |

**Hochrechnung Leiterplattenpreis, Einzelplatinen, HASL bleifrei, inkl. Kleinplatinen-Zuschlag (USD, unsicher):**

| Menge | Fläche gesamt | 2 Lagen | 4 Lagen | Δ 4 Lagen |
|---:|---:|---:|---:|---:|
| 5   | 31 cm²  | 2 (JLCONE) / ≈ 4 (Web) | 2 (JLCONE) / ≈ 5–7 (Web) | **+0–3** |
| 10  | 62 cm²  | ≈ 5  | ≈ 8–15  | **+3–10** |
| 30  | 186 cm² | ≈ 9  | ≈ 15–25 | **+6–16** |
| 100 | 621 cm² | ≈ 18 | ≈ 30–45 | **+12–27** |

2-Lagen-Werte aus Abschnitt 2.1 (dort ebenfalls geschätzt). 4-Lagen-Werte: Fixanteil (Ingenieurgebühr, Filme) plus 70,6 USD/m²; bei so kleiner Fläche dominiert der Fixanteil.

**Spartipp Nutzen:** Ein 5er-Nutzen (ca. 46 × 72 mm, Mausbiss-Stege, ohne Randstreifen) liegt bei 4 Lagen im Preisband „bis 100 × 100 mm“. 5 Nutzen = 25 Boards kosten dann etwa so viel wie 5 Stück 100 × 100 mm (ca. 6–7 USD Web, unsicher). Economic PCBA nimmt Nutzen an (max. 50 Einheiten). Damit wird der Aufpreis für 25–30 Boards voraussichtlich kleiner als in der Tabelle.

### 5.3 Bestückung (PCBA, einseitig)

| Punkt | 2 Lagen | 4 Lagen | Status |
|---|---|---|---|
| Economic PCBA zulässig | ja | **ja** („2, 4, 6 layers“, 0,8–1,6 mm, 2–50 Stk., ab 10 × 10 mm) | geprüft |
| Setup / Schablone | 8,18 / 1,53 USD | gleich | geprüft |
| Extended-Teile, Lötstellen, Röntgen | – | gleich, keine Lagenabhängigkeit | geprüft |
| Standard PCBA (nur bei beidseitig nötig) | 25,56 USD Setup einseitig | gleich | geprüft |

**Gesamtpreis bestückt pro Board (JLC Economic, HASL bleifrei, inkl. Versand, 19 % USt, Zoll; Basis Tabelle Abschnitt 1, Stand C3-Bestückung; der C6-Stand kostet laut hauptplatine-c6.md 7 bei beiden Varianten ca. +1 €/Board mehr) (unsicher):**

| Menge | 2 Lagen gesamt | 2 Lagen pro Board | 4 Lagen gesamt | 4 Lagen pro Board |
|---:|---:|---:|---:|---:|
| 5  | ≈ 67 €  | ≈ 13,40 € | ≈ 70 €  | ≈ 14,00 € |
| 10 | ≈ 94 €  | ≈ 9,40 €  | ≈ 100 € | ≈ 10,00 € |
| 30 | ≈ 160 € | ≈ 5,35 €  | ≈ 170 € | ≈ 5,70 € |

30 Stück interpoliert zwischen 25 und 50 Stück aus Abschnitt 1. Umrechnung Mehrkosten: USD × 0,885 × 1,19 ≈ USD × 1,05 in Euro brutto.

### 5.4 Fertigungsregeln bei JLCPCB (1 oz)

| Regel | 1–2 Lagen | 4 Lagen (Mehrlagen) | Aktueller Entwurf | Status |
|---|---|---|---|---|
| Min. Bahn/Abstand | 0,10 / 0,10 mm | 0,09 / 0,09 mm | Bahn 0,1–0,15, Abstand 0,13 mm | geprüft |
| Min. Via (Bohrung / Ring) | 0,15 / 0,25 mm | 0,15 / 0,25 mm; 0,1 / 0,2 mm nur bei ≤ 1 mm Dicke und ENIG/OSP | 0,3 / 0,6 mm | geprüft |
| Aufpreis kleine Bohrung | unter 0,3 mm | unter 0,3 mm (laut Forum bei 4 Lagen evtl. erst unter 0,2 mm) | 0,3 mm → kein Aufpreis | geprüft / Ausnahme unsicher |
| Via-in-Pad (POFV, gefüllt + verkupfert) | gegen Aufpreis | **gegen Aufpreis**; kostenlos erst ab 6 Lagen | nicht verwendet | geprüft (Kosten ca. 15–25 USD unsicher) |
| Via zu Bahn | 0,2 mm | 0,2 mm | – | geprüft |
| Abstand zum Fräsrand | ≥ 0,2 mm | ≥ 0,2 mm | – | geprüft |

**Folgerung:** 4 Lagen brauchen keine feineren Regeln. Mit einer GND-Lage (L2) und einer Versorgungs-/Signallage (L3) kann der Entwurf auf **0,15/0,15 mm oder 0,2/0,2 mm** und Via 0,3/0,6 mm zurück. Via-in-Pad ist nicht nötig. Die Antennen-Sperrfläche muss auch auf L2/L3 gelten; `antenna_keepout()` setzt sie bereits „auf allen Lagen“ (hauptplatine-c6.md 4). Bei 0,8 mm und 4 Lagen sind die Prepregs dünn; für USB 2.0 Full-Speed ist das unkritisch. Ein JLC-Impedanzaufbau für 0,8 mm/4 Lagen ist auf der Impedanzseite nicht aufgeführt (unsicher), wird aber auch nicht gebraucht.

### 5.5 PCBWay und Aisler (kurz)

| Anbieter | 2 Lagen | 4 Lagen | Mehrkosten 4 Lagen | Status |
|---|---|---|---|---|
| **PCBWay** | ab 5 USD / 10 Stk. (bis 100 × 100 mm) | Forenberichte: 4-Lagen-Prototyp etwa doppelt so teuer wie JLC; 120 × 60 mm, 5 Stk. ca. 80 USD (2024) | für 46 × 13,5 mm ca. +20–40 USD/Auftrag | unsicher |
| **Aisler** (DE, Preisformel Job + Fläche × Menge, min. 3 Stk.) | 2 Lagen HASL Budget: 12 € + 0,067 €/cm²; ENIG Budget: 12 € + 0,097 €/cm²; 0,8 mm bei 2 Lagen seit 11/2025 („Beautiful Boards+“) | **4 Lagen 0,8 mm ENIG Budget: 12 € + 0,156 €/cm²**, 125 µm Bahn/Abstand, Via 0,45 mm, 35 µm auf allen Lagen, Budget 10 Tage | siehe unten | Preisliste Stand 08/2023, evtl. veraltet; 0,8-mm-Angebot 10/2024 geprüft |

Aisler-Leiterplattenpreis netto für 6,2 cm² (Hochrechnung, unsicher):

| Menge | 2 Lagen ENIG | 4 Lagen 0,8 mm ENIG | Δ |
|---:|---:|---:|---:|
| 5   | ≈ 15 €  | ≈ 17 €  | +2 € |
| 10  | ≈ 18 €  | ≈ 22 €  | +4 € |
| 30  | ≈ 30 €  | ≈ 41 €  | +11 € |
| 100 | ≈ 72 €  | ≈ 109 € | +37 € |

Bei Aisler ist 4 Lagen 0,8 mm ein eigener Sammel-Pool und damit vergleichsweise günstig. Die Bestückung bei Aisler (75 € Setup + Positionsgebühr, Abschnitt 1) bleibt der große Kostenblock und hängt nicht von der Lagenzahl ab (unsicher).

### 5.6 Mehrkosten 4 Lagen pro Auftrag und pro Board (JLCPCB, Economic PCBA, HASL bleifrei)

| Menge | Δ netto USD | **Δ brutto € pro Auftrag** | **Δ € pro Board** | zusätzliche Lieferzeit |
|---:|---:|---:|---:|---|
| 5   | 0–5   | **≈ 3 €** (0–5)   | **≈ 0,60 €** (0–1,00) | +1–3 Werktage |
| 10  | 3–10  | **≈ 6 €** (3–10)  | **≈ 0,60 €** (0,30–1,00) | +1–3 Werktage |
| 30  | 6–16  | **≈ 10 €** (6–17) | **≈ 0,35 €** (0,20–0,55) | +1–3 Werktage |
| 100 | 12–27 | **≈ 19 €** (13–28)| **≈ 0,20 €** (0,13–0,28) | +1–3 Werktage |

Alle Werte unsicher (kein Live-Angebot). Mit ENIG bei beiden Varianten bleibt die Differenz etwa gleich. Mit dem 5er-Nutzen (5.2) wird sie bei 25–30 Stück eher kleiner. Gegenüber dem Gesamtpreis (Abschnitt 1) sind das **ca. 4–7 %** bei 5–30 Stück.

### 5.7 Einschätzung

- **Die Mehrkosten sind gering:** bei 5–30 Stück einstellige Euro-Beträge pro Auftrag, unter 1 € pro Board. Die Bestückung kostet gleich viel, Economic PCBA bleibt möglich. Teurer und deutlich spürbarer wäre der Wechsel auf beidseitige Bestückung (+60–70 USD, Abschnitt 1).
- **Der Nutzen ist groß:** durchgehende GND-Lage unter Modul, DRV8213 und USB (bessere Masse für Funk und Motorströme), Routing mit großzügigeren Regeln, voraussichtlich 100 % geroutet statt 87 %. Weniger GUI-Nacharbeit und geringeres Fertigungsrisiko durch 0,13-mm-Abstände.
- **Zu prüfen vor der Bestellung:** (1) Gerber beider Varianten in den JLC-Rechner (Website und JLCONE) laden und den echten Preis für 0,8 mm/4 Lagen ablesen, besonders ob 0,8 mm bei 4 Lagen einen Aufpreis oder längere Fertigung hat. (2) Antennen-Sperrfläche auf L2/L3 im DRC kontrollieren. (3) Bei Aisler ist 4 Lagen 0,8 mm ENIG ein Standardpool; falls EU-Fertigung gewünscht ist, ist der Aufpreis dort ebenfalls klein.
- **Empfehlung:** Wenn das 2-Lagen-Routing nicht ohne viel Handarbeit auf 100 % kommt, lohnt sich 4 Lagen. Der Aufpreis von ca. 3–10 € pro Prototypenauftrag ist kleiner als eine zweite Platinenrunde wegen eines Layoutfehlers.

### 5.8 Quellen (abgerufen 02.11.2026)

- JLCPCB Fertigungsfähigkeiten (Dicken, Bahn/Abstand, Vias, POFV, Toleranzen): https://jlcpcb.com/capabilities/pcb-capabilities (geprüft)
- JLCPCB Bestückungsfähigkeiten (Economic: 2/4/6 Lagen, 0,8–1,6 mm): https://jlcpcb.com/capabilities/pcb-assembly-capabilities (geprüft)
- JLCPCB Bestückungspreise (keine Lagenabhängigkeit): https://jlcpcb.com/help/article/pcb-assembly-price (geprüft)
- JLCPCB Fertigungszeiten 2 vs. 4 Lagen: https://jlcpcb.com/help/article/pcb-fabrication-services-and-production-time (geprüft)
- JLCPCB Aufpreise (Kleinplatinen, ENIG > 30 %, Bohrungen < 0,3 mm): https://jlcpcb.com/help/article/In-what-cases-will-there-be-charged-extra (geprüft)
- JLCPCB 4-Lagen-Flächenpreis 70,6 USD/m², Beispiele 100/500 Stk.: https://jlcpcb.com/blog/special-discount-on-quality-4-layers-pcbs, https://jlcpcb.com/news/discount-on-quality-4-layer-pcbs (geprüft, Stand 03/2024)
- JLCPCB Preisanpassung FR4 1/2/4 Lagen, 03.08.2026: https://jlcpcb.com/news/jlcpcb-fr4-pcb-price-adjustment-august2026 (geprüft, keine konkreten Preise)
- JLCONE Desktop, 2-USD-Angebot nur noch dort (22.08.2026): https://jlcpcb.com/news/jlcpcb-jlcone-desktop-app (geprüft)
- „4 layers (10×10 cm) from 7 USD“, Coupon: https://jlcpcb.com/features/prototype-pcb-way (geprüft, Werbeseite)
- 2 USD für 4 Lagen bis 50 × 50 mm: https://www.lcsc.com/pcba/price, https://highway.hackclub.com/guides/JLC-cost-optimizing (geprüft)
- Freie Dicken 0,8/1,0/1,2/1,6 mm: https://techoverflow.net/2024/11/26/what-pcb-thickness-options-are-free-of-charge-on-jlcpcb/ (für 4 Lagen nicht ausdrücklich, unsicher)
- Forum: JLC-Preise 2026 (4 Lagen 100 × 100 mm 5,92 €, Ingenieurgebühr bis 24 USD): https://www.mikrocontroller.net/topic/583828 (unsicher)
- Forum: JLC 4 Lagen 100 × 100 mm 9,55 USD, PCBWay ca. 80 USD für 120 × 60 mm (2024): https://eevblog.com/forum/manufacture/a-good-pcb-manufacture-for-hobby-pcb/msg5569241 (unsicher)
- Via-in-Pad kostenlos ab 6 Lagen: https://jlcpcb.com/blog/Free-Via-in-Pad-on-6-20-Layer-PCBs-with-POFV (geprüft)
- PCBWay Online-Rechner: https://www.pcbway.com/orderonline.aspx (nicht abgefragt)
- Aisler Preisformel und Tabelle: https://community.aisler.net/t/our-simple-pricing (Stand 08/2023, unsicher)
- Aisler 4 Lagen 0,8 mm: https://community.aisler.net/t/aislers-new-0-8mm-4-layer-pcb-service/4399 (geprüft, 10/2024)
- Aisler 0,8 mm bei 2 Lagen: https://community.aisler.net/t/option-to-order-0-8mm-boards-for-simple-projects/5162 (geprüft, 11/2025)
