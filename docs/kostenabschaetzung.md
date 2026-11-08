# Kostenabschätzung: Fertigung und Bestückung der Hauptplatine

**Stand der Recherche:** 01.11.2026 (Web-Recherche, keine Angebote eingeholt, keine Logins/Bestellungen)
**Wechselkurs:** 1 EUR ≈ 1,13 USD → **1 USD ≈ 0,885 EUR** (Kurs Okt. 2026 lag zwischen ca. 1,12 und 1,16; Schwankung ±3 % geht direkt in alle Preise ein)

**Platine:** 46 × 13,5 mm (6,2 cm²), 2 Lagen, FR4 0,8 mm, 0,15/0,15 mm, Via 0,3/0,6 mm, grüne Maske, ca. 38 Bestückpositionen / 15 Teiletypen, ca. 135 Lötstellen pro Platine.

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
| Regeln 0,15 mm / Via 0,3 mm | Standard, kein Aufpreis (Aufpreis erst bei Bohrung < 0,3 mm) | [Q] |
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
