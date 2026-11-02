# Idee: Zigbee-Betrieb („Unterwegs mit Tastern“)

Stand: 2026-11-02 · Status: Idee, Hardware ist mit dem ESP32-C6 vorbereitet, Software später (nur C/ESP-IDF).
Grundlage: [hauptplatine-c6.md](hauptplatine-c6.md) Abschnitt 4 (Koexistenz), [idee-funk-taster.md](idee-funk-taster.md).

## 1. Warum eine eigene Betriebsart

Laut Espressif-Koexistenz-Tabelle (C6) geht ein **Zigbee-Coordinator weder zusammen mit dem eigenen Hotspot noch
zusammen mit dem BLE-Scan** (beides „X“, nicht unterstützt). Zigbee ist deshalb **eine eigene Betriebsart**, keine
Zusatzfunktion im Partymodus. Nacheinander geht dagegen alles, denn es ist dasselbe Funkteil.

| Betriebsart | Funk | Bedienung | Wofür |
|---|---|---|---|
| **WLAN** (Standard) | Heim-WLAN oder eigener Hotspot, BLE-Scan für BTHome-Taster | Web-UI am Handy, BTHome-Taster | Zuhause, Party mit Handys |
| **Unterwegs (Zigbee)** | kein WLAN, Louie ist Zigbee-Coordinator | nur Zigbee-Taster (z. B. IKEA, Aqara) | unterwegs, Party ohne Handys, immer derselbe Modus |
| Heim-WLAN + Zigbee (später) | WLAN-STA + Coordinator („C1“, instabil) | Web-UI und Zigbee-Taster | nur, wenn der Test es stabil zeigt |

Im Unterwegs-Betrieb spielen alle mit Tastern. Es läuft der **zuletzt gewählte Modus** (bzw. der Hebel-Modus),
die Belegung der Taster ist vorher im WLAN-Betrieb eingerichtet. Anlernen der Zigbee-Taster passiert ebenfalls im
WLAN-Betrieb (Web-UI startet dazu kurz den Coordinator, ohne Hotspot geht das nur im Heim-WLAN, oder mit
Assistent: „Hotspot wird für 60 s getrennt, jetzt Taster koppeln“).

## 2. Zurück in den WLAN-Betrieb – ohne Versehen

Anforderung: Der Wechsel darf **nicht während des Spiels** passieren, auch nicht, wenn alle gleichzeitig drücken.
Der Schlüssel ist der **Hebel**: Während einer Runde steht er auf „an“.

**Empfehlung (zwei Wege, beide sicher):**

1. **Hebel aus + zwei beliebige Taster gleichzeitig 5 s gedrückt halten** (Entscheidung 2026-11-02).
   - Nur bei Hebel „aus“, also nie in einer laufenden Runde.
   - Zwei **verschiedene** angelernte Taster, beide innerhalb von 1 s gedrückt. Nicht „alle“, weil bis zu 8 verbunden
     sein können. Ein einzelnes Kind kann das nicht zufällig auslösen.
   - **Was die Taster melden** (unsicher, im Test prüfen): Viele Zigbee-Taster melden beim Halten einen Beginn und beim
     Loslassen ein Ende, z. B. IKEA RODRET/STYRBAR als „Move“ … „Stop“ oder Aqara als „hold“ … „release“. Dann misst
     Louie die 5 s selbst: Beide Taster sind gleichzeitig im Haltezustand. Meldet ein Taster nur einmal „lang gedrückt“
     ohne Ende, gilt ersatzweise: zwei verschiedene Taster melden „lang“ innerhalb von 2 s, bei Hebel aus. Auch das
     passiert im Spiel nicht.
   - Rückmeldung über die Status-LED (schnelles Blinken), denn bei Hebel aus ist der Motor getrennt. Danach
     startet WLAN bzw. Hotspot.
2. **Hebel-Geste beim Aufwachen** (gibt es schon im Konzept als „Hotspot erzwingen“, software-konzept.md 3.1):
   Louie wecken und innerhalb von 10 s den Hebel 5× schnell umlegen. Funktioniert auch, wenn die Taster-Batterien
   leer sind oder die Taster fehlen. Das ist die immer verfügbare Rettung.

**Optional, später zu entscheiden: Startfenster.** Nach jedem Aufwachen ist Louie erst 20 s im WLAN-Betrieb. Verbindet
sich in dieser Zeit ein Handy, bleibt er dort, sonst wechselt er in den Unterwegs-Betrieb. Damit braucht man meist gar
keine Geste. Der Preis ist, dass die Taster erst nach 20 s funktionieren.

**Abgelehnt:** „Alle Taster gleichzeitig“ ohne Hebelbedingung, weil das im Spiel vorkommen kann. Ebenso der BOOT-Taster,
denn er ist im Batteriefach nicht erreichbar.

## 3. Später: Modus wechseln und anzeigen ohne Handy

- **Modus wechseln:** Bei Hebel aus z. B. einen Taster 3 s halten → nächster Modus aus einer Favoritenliste
  (im WLAN-Betrieb festgelegt, z. B. Klassisch / Druckkochtopf / Turbulenzen).
- **Anzeigen:** Status-LED blinkt die Nummer des Modus (1×, 2×, 3×), oder Louie „zeigt“ den Modus mit einer kurzen
  typischen Bewegung, sobald der Hebel an ist (nur wenn spürbar und nicht störend).
- Fiesheit bleibt im Unterwegs-Betrieb fest auf dem zuletzt eingestellten Wert.

## 4. Was jetzt schon vorzusehen ist

- **Hardware:** nichts zusätzlich (gleiches Funkteil, gleiche Antenne). Sinnvoll sind das **8-MB-Flash (C6-MINI-1-H8)**
  und eine gute Antennenlage (Antennenkorrektur L2).
- **Status-LED** ist Pflicht, weil sie im Unterwegs-Betrieb die einzige Anzeige ist.
- **Software:** Der Zigbee-Stack gibt es nur in C (esp-zigbee-sdk). Mit MicroPython geht das nicht ohne eigenes
  C-Modul. Realistisch also erst mit einer C-Firmware oder einem C-Modul, siehe [firmware-sprache.md](firmware-sprache.md).

## 5. Offene Punkte

- [ ] Welche Zigbee-Taster (IKEA STYRBAR/RODRET, Aqara Mini) und wie schnell melden sie einen Druck?
- [ ] Startfenster ja/nein, und wie lang?
- [ ] Zigbee + Heim-WLAN (C1) im Test stabil?
