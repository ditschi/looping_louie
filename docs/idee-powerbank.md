# Idee: Versorgung über eine kleine USB-C-Powerbank in der Basis

Stand: 2026-11-02 · Status: Recherche, nichts beschlossen. Ergänzt [hardware-konzept.md](hardware-konzept.md),
[ladeplatine.md](ladeplatine.md) und [idee-usb-c-hauptplatine.md](idee-usb-c-hauptplatine.md).

Markierungen: **(geprüft)** = mit Quelle oder an den Projektdateien nachgerechnet · **(unsicher)** = Sekundärquelle,
Gedächtnis oder Annahme, vor einer Entscheidung am Gerät prüfen.

## Kurzfazit

- **Ja, es gibt passend kleine Powerbanks**, z. B. die Anker Nano 5000 mAh mit ca. 76 × 36 × 25 mm für ca. 19–28 €.
  Ob sie in die Basis passt, ist offen: Für den Hohlraum gibt es keine veröffentlichten Maße. Man muss nachmessen.
- **Das eigentliche Problem ist die Auto-Abschaltung**, nicht die Größe. Fast alle Powerbanks schalten unter
  ca. 45–150 mA nach 10–60 s ab. Im Deep Sleep ist dann die Versorgung weg, und der Hebel weckt nichts mehr.
- **Echte Always-on-Powerbanks** (Voltaic V25) sind zu groß und teuer und nur am USB-A-Port always-on. Die
  „Trickle“- bzw. „Low-Current“-Modi von Anker und Xiaomi enden nach 2 h und taugen nicht für einen Bereitschaftsbetrieb.
- **Empfehlung:** Die Powerbank ist eine **Fallback-Versorgung für die Spielzeit, ohne Bereitschaft**. Im
  Powerbank-Betrieb schläft der Louie nicht, sondern bleibt mit WLAN an (ca. 100 mA, hält die Powerbank wach).
  Nach der Leerlaufzeit schaltet er sich ganz ab. Zum Wecken steckt man neu ein oder drückt den Powerbank-Knopf.
  Mit eingebautem LiPo (Ladeplatine) entsteht das Problem gar nicht: Die Powerbank lädt dann nur, und den
  Bereitschaftsbetrieb übernimmt der LiPo.
- **Besser als jede Powerbank:** eine **18650-Zelle im Halter in der Basis an der vorhandenen Ladeplatine**. Sie ist
  1S Li-Ion wie der LiPo, braucht keinen Aufwärtswandler und schaltet nie ab.

---

## 1. Platz in der Basis

| Modell | Bekannt | Quelle / Status |
|---|---|---|
| Louie neu (Hasbro, 2× AA) | Spiel gesamt **26,7 × 26,7 × 9,5 cm**, ca. 1 kg | Händlerangabe [Galaxus][galaxus-ll] **(geprüft, Außenmaß)** |
| Louie alt (Milton Bradley, 1× C) | größer als das neue Modell, offenes C-Fach | hardware-konzept.md; Maße der Basis **unbekannt** |
| Loopin' Chewie | 2× AA (Annahme im Projekt) | keine Maße gefunden **(unsicher)** |
| Hohlraum unter bzw. in der Basis | keine Teardown-Fotos mit Maßen gefunden. CDTM hat beim alten Louie für einen 9-V-Block (48 × 26 × 17 mm) „etwas Platz schaffen“ müssen | [CDTM][cdtm] **(unsicher, nur qualitativ)** |

**Annahmen (unsicher, am Spiel messen):**

- Das Projekt plant schon einen **1S-LiPo mit 1000–2000 mAh in der Basis** (hardware-konzept.md 5.4). Ein flacher
  Beutel-Akku dieser Größe hat ca. 50 × 34 × 8 mm bis 60 × 40 × 10 mm. Mindestens so viel Platz wird also
  angenommen.
- Eine **Powerbank mit 5000 mAh ist 3- bis 5-mal so groß** (ca. 65–70 cm³). Ob es in der Basis eine Kammer von
  ca. 80 × 40 × 26 mm gibt, die nicht vom Motor, vom Getriebe oder von den Schraubdomen belegt ist, ist **offen**.
- Fallback ohne Platz: Die Powerbank liegt **neben dem Spiel**, und das Kabel läuft durch das Loch des
  Basis-Halters (13,5 × 7,5 mm, ladeplatine.md 4B) oder von oben ins Fach.

Neuer offener Punkt **P1**: Basis öffnen, freie Kammern messen (L × B × H), Fotos in `docs/bilder/`.

## 2. Kandidaten (kleine Powerbanks mit USB-C)

| Modell | Kapazität | Maße (mm) | Ausgang | Preis DE/EU | Low-Current / Always-on | Quelle |
|---|---|---|---|---|---|---|
| **Anker Nano Power Bank 22,5 W** (A1653, Stecker klappbar) | 5000 mAh | 76 × 35,5 × 25,4, 100 g | USB-C-Buchse + Stecker, 5 V/3 A | ca. 19 € (Amazon-Aktion) bis 28 € (MediaMarkt AT) | Trickle-Modus (Doppeldruck, **max. 2 h**). Ob genau dieses Modell ihn hat, ist **unsicher** | [Galaxus][anker-dim], [GIGA][giga], [MediaMarkt][mm-anker], [Anker FAQ][anker-trickle] |
| Forcell F-Energy Mini Power Watch | 1200 mAh | 70,5 × 40 × 15,9, 48 g | USB-C-Kabel fest | ca. 10–15 € **(unsicher)** | nicht bekannt | [MediaMarkt AT][forcell] |
| INIU Schlüsselanhänger-Powerbank | bis 5000 mAh **(unsicher)** | ca. 80 × 38 × 29 | USB-C | ca. 12 € (Aktion) | nicht bekannt | [china-gadgets][iniu] |
| Typische „Lippenstift“-Powerbank (1× 18650) | 2600–3350 mAh | ca. Ø 22–25 × 90–100 | oft nur USB-A **(unsicher)** | 8–15 € | selten | – |
| **Voltaic V25** | 6700 mAh | 80 × 82 × 24, 230 g | 2× USB-A (always-on), USB-C PD (**nicht** always-on) | 45 $ (≈ 50–55 € in EU-Shops) | **ja**, nur USB-A, Eigenverbrauch ca. 7 mA | [Voltaic][v25] **(geprüft)** |
| Voltaic V15 | 4000 mAh | 102 × 65 × 16 | USB-A 1 A | auslaufend | ja | [Modern Outpost][v15] |
| Xiaomi Powerbanks (diverse) | – | – | – | – | Low-Current-Modus per Doppeldruck, **endet nach 2 h** | [Xiaomi FAQ][xiaomi] |

Strom: Der Motor zieht bis ca. 1 A Spitze, der DRV8833 begrenzt auf ca. 2 A. Eine USB-C-Quelle mit 5 V/3 A reicht.
Kleine 1000-mAh-Anhänger liefern oft nur 1–1,5 A. Beim Anlauf kann ihr Überstromschutz auslösen, die
Firmware-Rampen (hardware-konzept.md 5.1) helfen dagegen **(unsicher)**.

## 3. Kernproblem: Auto-Abschaltung

Typische Schwellen: **IP5306 unter 45 mA für 32 s** [Datenblatt-Zusammenfassung][ip5306] **(geprüft)**. Andere
Powerbanks schalten unter 50–200 mA ab, gemessen z. B. 150 mA [0110.be][0110] oder 100 mA nach ca. 10 s (Voltcraft)
[ESP32_KeepPowerbankAlive][kpa]. Ob ein USB-C-Port mit gestecktem 5,1-k-Widerstand (Rd, Ladeplatine R101/R102)
länger an bleibt, hängt vom Hersteller ab. Darauf kann man sich nicht verlassen **(unsicher)**.

Verbrauch des Louie an 5 V: Über den LDO (AP2112K) ist der Eingangsstrom gleich dem 3,3-V-Strom.

| Zustand | Strom | Powerbank bleibt an? |
|---|---|---|
| WLAN verbunden, Modem-Sleep aus (`WIFI_PS_NONE`) | ca. 80–120 mA | meist ja, knapp über der Schwelle **(unsicher)** |
| WLAN mit Modem-Sleep (Standard) | Mittel ca. 20–40 mA | **nein**, nach 10–60 s aus |
| Light Sleep, WLAN aus | ca. 0,5–2 mA | nein |
| Deep Sleep | µA | nein |

### Lösungen im Vergleich

| Lösung | Wie | Energie (Powerbank 5000 mAh ≈ 15 Wh nutzbar an 5 V) | Aufwand | Bewertung |
|---|---|---|---|---|
| **A: Always-on-Powerbank** | Voltaic V25 an USB-A → C-Kabel | Eigenverbrauch 7 mA → ca. 3 Wochen Bereitschaft | keiner | ✓ technisch sauber, ✗ 80 × 82 mm, 230 g, ca. 50 €. Passt vermutlich nicht in die Basis |
| **B: Trickle-/Low-Current-Modus** (Anker, Xiaomi) | Doppeldruck | – | keiner | ✗ endet nach 2 h, als Bereitschaft nutzlos |
| **C: Grundlast-Puls in Hardware** | MOSFET + 47 Ω an VBUS, 555/RC-Takt, z. B. **100 mA für 50 ms alle 8–9 s** (Muster aus [ESP32_KeepPowerbankAlive][kpa], fertige Module: [Pi Hut KeepAlive][pihut], ca. 100 mA bei 50 % Tastgrad, das ist verschwenderisch) | Puls: 100 mA × 50 ms / 9 s ≈ 0,6 mA → 3 mW. Dazu Leerlauf der Powerbank, Schätzung 1–5 mA aus der Zelle **(unsicher)** → ca. 2–6 Wochen | ca. 6 Bauteile auf der **Ladeplatine** (nur aktiv, wenn VBUS da ist). Auf A ist **kein GPIO frei** | ○ funktioniert mit den meisten Powerbanks, Takt je Modell abstimmen. Manche mitteln über längere Fenster |
| **D: Puls per Firmware** | Light Sleep, alle ca. 8 s per Timer aufwachen und 0,2–0,5 s WLAN/RF an (80–120 mA) | Mittel ca. 3–5 mA → ca. 4–6 Tage Bereitschaft | nur Firmware | ○ ohne Hardware testbar. Ob ein so kurzer Puls die Powerbank wach hält, ist **unsicher** und modellabhängig |
| **E: Kein Schlaf an USB** | an USB WLAN verbunden halten, `WIFI_PS_NONE` | ca. 0,5 W → ca. 30 h | nur Firmware | ✓ für einen Spieleabend ideal, ✗ keine Bereitschaft über Tage |
| **F: Abschaltung akzeptieren** | Leerlaufzeit → Deep Sleep → Powerbank aus. Wecken: Powerbank-Knopf drücken oder Kabel neu stecken | 0 | keiner | ✓ ehrlich und einfach. Der Hebel weckt dann nicht, das muss das Web-UI erklären |
| Motor als Last | – | – | – | ✗ geht nicht: Bei Hebel „aus“ ist der Motorkreis offen |

## 4. Alternativen ohne fertige Powerbank

| Alternative | Spannung | Bewertung |
|---|---|---|
| **18650 (oder großer LiPo) im Halter an der Ladeplatine** | 3,0–4,2 V direkt auf VSYS | ✓ **beste Lösung**: kein Wandler, keine Abschaltung, Laden über die vorhandene USB-C-Buchse. 18650: Ø 18 × 65 mm, ca. 2500–3500 mAh, Halter ca. 77 × 21 × 19 mm **(unsicher)** |
| Powerbank-Modul (IP5306) + 18650 | 5 V | ✗ Der IP5306 hat dieselbe Abschaltung (45 mA/32 s). Nur Module mit „HOLD“ oder gebrückter Taste bleiben an **(unsicher)**. Doppelte Wandlung 3,7 → 5 → 3,3 V verschenkt ca. 10–15 % |
| 2× AA + Boost auf 5 V | 5 V | ✗ Das Fach ist durch Platine A belegt. Kein Vorteil gegenüber 1S Li-Ion |
| **14500 Li-Ion mit USB-C-Ladebuchse** (z. B. Acebeam ARC14500-920, Nextorch 880 mAh, JetBeam JR145) | 3,7 V (kein 1,5-V-Regler!) | ○ anders als I1 (1,5-V-Zellen, verworfen) passt die Spannung **ohne Wandler**. Aber: nur ca. 3 Wh. Die Fächer sind über den Motorkreis verbunden, also müsste neu verdrahtet werden (Fach 2 wird Versorgung statt Brücke). Geschützte Zellen sind oft 52–53 mm lang statt 50,5 mm **(unsicher)**. Zum Laden muss man sie herausnehmen. [Battery Junction][bj14500] |

## 5. Empfehlung

| Rang | Bauform | Maße | Preis | Always-on | Nötig |
|---|---|---|---|---|---|
| 1 | **18650 im Halter an der Ladeplatine** (statt Powerbank) | ca. 77 × 21 × 19 mm | ca. 8–12 € (Zelle + Halter) **(unsicher)** | ja | nichts Neues, Akku-Anschluss J102/TP101 |
| 2 | **Anker Nano 5000 mAh** als Fallback per C-auf-C-Kabel | 76 × 35,5 × 25,4 mm | ca. 19–28 € | nein (Trickle max. 2 h) | Firmware: Lösung E + F |
| 3 | Voltaic V25, wenn echte Bereitschaft mit Powerbank Pflicht ist | 80 × 82 × 24 mm | ca. 45 $ | ja (USB-A) | USB-A-auf-C-Kabel, Platz außerhalb der Basis |

**Firmware:**

- USB-Erkennung über die vorhandene VSYS-Messung (VBAT_ADC): **VSYS > 4,4 V ⇒ „Versorgung über USB“**
  (ladeplatine.md: VSYS ≈ 4,6 V über die Schottky-Diode). Kein zusätzlicher GPIO nötig.
- An USB: `WIFI_PS_NONE`, kein Deep Sleep. Nach der Leerlaufzeit **Deep Sleep mit Hinweis**, dass der Hebel bei
  Powerbank-Betrieb nicht weckt.
- Ist ein LiPo vorhanden (VSYS fällt beim Abziehen nur auf die Akkuspannung), gilt der normale Ablauf. Das Abschalten
  der Powerbank ist dann harmlos.
- Motor-Sollwert wie bisher `duty = U_soll / VSYS`, an 5 V ergibt sich automatisch ein kleinerer Tastgrad.
- Optional Lösung D als Versuch (Testmodus „Powerbank wach halten“), Ergebnis je Modell notieren.

**Hardware:** Für Rang 1 und 2 nichts. Lösung C nur, wenn sich D als unzuverlässig erweist: Pulslast auf der
Ladeplatine (nur VBUS-seitig, unabhängig vom ESP).

**Web-UI ([web-ui-konzept.md](web-ui-konzept.md)):**

- Statusanzeige **„Versorgung über USB“** statt Akku-Prozent. Die Ladung der Powerbank ist nicht lesbar.
- Ob ein LiPo geladen wird oder eine Powerbank ohne Akku speist, ist an VSYS allein nicht unterscheidbar. Die
  Anzeige also neutral halten („USB“) oder in den Einstellungen „Akku verbaut: ja/nein“ abfragen.
- Ohne Akku: Vor dem Schlafen einen Hinweis zeigen: „Louie schaltet ab. Zum Wecken Powerbank-Knopf drücken oder
  Kabel neu stecken. Der Hebel weckt im Powerbank-Betrieb nicht.“
- Bricht VSYS während einer Runde ein (Powerbank aus oder leer), gibt es beim nächsten Start eine Statuskarte
  „Versorgung unterbrochen“ (Reset-Grund Brownout).

## 6. Offene Punkte

| # | Punkt | Vorschlag |
|---|---|---|
| P1 | Freie Kammern in der Basis (alle drei Modelle) | Basis öffnen, messen, fotografieren |
| P2 | Hält die Anker Nano bei 80–120 mA dauerhaft? Bleibt der C-Port mit Rd an? | mit USB-Messgerät testen |
| P3 | Hält ein Firmware-Puls (Lösung D) die Powerbank wach? | Versuch mit 2–3 Powerbanks |
| P4 | Motoranlauf an kleinen 1-A-Powerbanks | Überstromabschaltung testen |

## Quellen

- [galaxus-ll]: https://galaxus.de/en/s5/product/hasbro-gaming-looping-louie-german-board-games-288540
- [cdtm]: https://cdtm.com/blog/creating-circling-centerling-looping-louie-modding
- [anker-dim]: https://www.galaxus.nl/en/s1/product/anker-nano-5000-mah-18-w-50-wh-powerbanks-42820321
- [giga]: https://www.giga.de/tech/amazon-verkauft-kompakte-nano-powerbank-zum-spitzenpreis--01J69M6MSR4V71FC40ABBXMWQE
- [mm-anker]: https://www.mediamarkt.at/de/product/_anker-nano-powerbank-5000-mah-usb-c-schwarz-2063924.html
- [anker-trickle]: https://service.anker.com/eu/article-description/What-is-Trickle-Charging-Mode
- [forcell]: https://www.mediamarkt.at/de/product/_forcell-f-energy-mini-power-watch-1200mah-powerbank-1200mah-schwarz-139492849.html
- [iniu]: https://www.china-gadgets.de/iniu-5-000-mah-powerbank-schluesselbund-kabel-ueberfluessig/
- [v25]: https://voltaicsystems.com/V25
- [v15]: https://www.modernoutpost.com/product/voltaic-v15/
- [xiaomi]: https://www.mi.com/global/support/faq/details/KA-301691/
- [ip5306]: https://industrialmonitordirect.com/blogs/knowledgebase/ip5306-shuts-down-after-33-seconds-load-detection-fix
- [0110]: https://0110.be/posts/Powering_low_current_electronics_projects_with_power_banks
- [kpa]: https://www.github.com/Staubgeborener/ESP32_KeepPowerbankAlive
- [pihut]: https://thepihut.com/products/power-bank-keepalive-usb-c
- [bj14500]: https://www.batteryjunction.com/products/jetbeam-jr145

[galaxus-ll]: https://galaxus.de/en/s5/product/hasbro-gaming-looping-louie-german-board-games-288540
[cdtm]: https://cdtm.com/blog/creating-circling-centerling-looping-louie-modding
[anker-dim]: https://www.galaxus.nl/en/s1/product/anker-nano-5000-mah-18-w-50-wh-powerbanks-42820321
[giga]: https://www.giga.de/tech/amazon-verkauft-kompakte-nano-powerbank-zum-spitzenpreis--01J69M6MSR4V71FC40ABBXMWQE
[mm-anker]: https://www.mediamarkt.at/de/product/_anker-nano-powerbank-5000-mah-usb-c-schwarz-2063924.html
[anker-trickle]: https://service.anker.com/eu/article-description/What-is-Trickle-Charging-Mode
[forcell]: https://www.mediamarkt.at/de/product/_forcell-f-energy-mini-power-watch-1200mah-powerbank-1200mah-schwarz-139492849.html
[iniu]: https://www.china-gadgets.de/iniu-5-000-mah-powerbank-schluesselbund-kabel-ueberfluessig/
[v25]: https://voltaicsystems.com/V25
[v15]: https://www.modernoutpost.com/product/voltaic-v15/
[xiaomi]: https://www.mi.com/global/support/faq/details/KA-301691/
[ip5306]: https://industrialmonitordirect.com/blogs/knowledgebase/ip5306-shuts-down-after-33-seconds-load-detection-fix
[0110]: https://0110.be/posts/Powering_low_current_electronics_projects_with_power_banks
[kpa]: https://www.github.com/Staubgeborener/ESP32_KeepPowerbankAlive
[pihut]: https://thepihut.com/products/power-bank-keepalive-usb-c
[bj14500]: https://www.batteryjunction.com/products/jetbeam-jr145
