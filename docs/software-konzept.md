# Software-Konzept: Firmware, Web-UI, Bedienung

Stand: 2026-11-01 · Status: Entwurf zur Diskussion. Ergänzt [hardware-konzept.md](hardware-konzept.md), Abschnitt 7.

## 1. Ziele und Leitplanken

- **Spielbar ohne Handy.** Hebel an = Runde mit dem zuletzt gewählten Modus. Das Web-UI ist ein
  Zusatz und keine Voraussetzung.
- **Zwei Netzbetriebsarten**: im bekannten WLAN (Handys behalten Internet) oder als eigener
  Hotspot, wenn kein bekanntes Netz da ist. Der Wechsel passiert automatisch.
- **Rollen**: normale Nutzer und Admin. Admin richtet WLANs ein, setzt Grenzwerte und kritische
  Einstellungen. Für den Anfang bewusst einfach, aber so gebaut, dass später ein
  Mehrbenutzersystem (Profile, eigene Modi pro Person) nur **ergänzt** und nicht umgebaut wird.
- **Alles offline.** Im Hotspot-Betrieb gibt es kein Internet, also auch kein CDN. Alle Dateien
  des Web-UI liegen im Flash des ESP32-C3.
- **Entwicklung parallel zur Hardware**: Spiellogik, Server und Web-UI laufen auch auf dem PC
  mit simuliertem Motor (siehe 9).
- **Sicherheit vor Komfort beim Motor**: Grenzwerte setzt immer der Server durch, nie das UI.

## 2. Sprache und Framework

### 2.1 Randbedingungen

ESP32-C3-MINI-1-N4: ein RISC-V-Kern mit 160 MHz, 400 KB SRAM (davon braucht das WLAN einen
großen Teil), **4 MB Flash**. Zeitkritisch ist nichts: PWM, Rampen und Messungen laufen im
10–50-ms-Raster, die PWM selbst erzeugt die Hardware (LEDC).

### 2.2 Optionen

| Option | Pro | Contra |
|---|---|---|
| **MicroPython + Microdot** | Schnellstes Entwickeln, Code ohne Flashen hochladen, Erfahrung aus v1 vorhanden. Microdot (async, WebSocket, Sessions) läuft **identisch auf CPython** → Simulator am PC. Spiellogik mit pytest testbar. | Mehr RAM-Verbrauch, Garbage-Collector-Pausen (für uns unkritisch). Wenige parallele Sockets. Einzelne ESP-Funktionen (GPIO-Wake im Deep Sleep beim C3, AP+STA) müssen auf dem Prototyp bestätigt werden. |
| Arduino / PlatformIO (C++) + ESPAsyncWebServer | Ausgereift, sparsam, viele Beispiele (Captive Portal, OTA, WiFiManager). | Langsamer Entwicklungszyklus (Kompilieren, Flashen). Kein natürlicher PC-Simulator, Tests aufwendiger. Asynchrone Lib hatte Wartungsphasen (heute Fork *ESP32Async*). |
| ESP-IDF (C) | Volle Kontrolle, beste Ressourcennutzung, OTA mit zwei Partitionen sauber. | Größter Aufwand für Webserver, JSON, Sessions. |
| Rust (esp-idf-svc oder esp-hal/Embassy) | Sicher, modern, gute async-Unterstützung. | Steile Lernkurve, ESP-Ökosystem noch in Bewegung, langsamer Einstieg. |
| ESPHome | Sehr schnell für Steuerung und WLAN-Fallback. | Eigene Spielmodi, Rollen, eigenes UI passen nicht ins Konzept. |

### 2.3 Empfehlung

**MicroPython + Microdot**, mit drei Absicherungen:

1. **Saubere Schichten** (siehe 8): Die Spiellogik kennt keine Hardware und kein Netz. Das
   Web-UI spricht nur das dokumentierte Protokoll (siehe 7). Sollte MicroPython an Grenzen stoßen,
   wird nur die Firmware nach C++ portiert. **Web-UI und Protokoll bleiben.**
2. **Früher Machbarkeitstest** auf dem Steckbrett-Prototyp (XIAO ESP32-C3), bevor viel Code
   entsteht: freier Heap nach WLAN-Start, 6 gleichzeitige WebSocket-Clients, AP+STA gleichzeitig,
   GPIO-Wake aus Deep Sleep, 20-kHz-PWM. Abbruchkriterium: einer dieser Punkte geht nicht.
3. **Für Releases einfrieren**: Python-Module als „frozen modules“ in die Firmware kompilieren.
   Das spart RAM und verkürzt den Start.

### 2.4 Web-UI-Technik

- **Preact + htm** (ca. 5 KB, JSX-ähnlich ohne Build-Schritt) als lokale Datei im Projekt.
  Alternative: reines JavaScript mit Web Components. Kein React, kein Tailwind-CDN.
- Build optional per `just web`: Dateien bündeln, minifizieren, **gzip**. Der ESP liefert die
  `.gz`-Dateien direkt mit `Content-Encoding: gzip` aus. Ziel: unter 100 KB komprimiert.
- **Achtung, kein HTTPS** (selbst signierte Zertifikate erzeugen Warnungen, TLS-Server ist auf dem
  C3 zu schwer). Im unsicheren Kontext fehlen im Browser: Web Crypto (`crypto.subtle`),
  Service Worker / PWA-Installation, Wake Lock (Bildschirm anlassen). Vibration (`navigator.vibrate`)
  geht auf Android, nicht auf iOS. Das UI muss ohne diese Dinge auskommen.

## 3. Netzwerk

### 3.1 Startablauf

```
Aufwecken / Einschalten
   │
   ├─ Hebel-Geste beim Start? (5× schnell umlegen) ──► Hotspot erzwingen (Wiederherstellung)
   │
   ├─ Scan → bekannte Netze nach Priorität und Signalstärke
   │      └─ verbinden (je max. 10 s) ──► OK ──► STA-Betrieb, mDNS „louie.local“
   │
   └─ kein Erfolg ──► Hotspot „Louie-XXXX“ (XXXX aus MAC), Captive Portal
                       └─ alle 2 min im Hintergrund nach bekannten Netzen suchen,
                          aber nur wenn keine Runde läuft und kein Client verbunden ist
```

- **Während einer Runde wird nie die Netzbetriebsart gewechselt.** Fällt das WLAN aus, läuft die
  Runde weiter (Hebel funktioniert immer), danach wird neu verbunden.
- Mehrere Netze speicherbar (Zuhause, Oma, Ferienhaus), mit Priorität.
- **Keine feste IP** wie in v1 (`.66` war im fremden Netz ein Kollisionsrisiko). Stattdessen
  mDNS `louie.local` (bei mehreren Geräten `louie-xxxx.local`) und DHCP.

### 3.2 Hotspot und Captive Portal

- WPA2 mit **gerätespezifischem Passwort** (aus der MAC abgeleitet), steht auf einem Aufkleber
  mit **zwei QR-Codes**: „WLAN beitreten“ (`WIFI:S:Louie-XXXX;T:WPA;P:…;;`) und
  „Steuerung öffnen“ (`http://192.168.4.1`). Admin kann den Hotspot auch offen schalten.
- Captive Portal: kleiner DNS-Server beantwortet alle Anfragen mit 192.168.4.1. Die Handys zeigen
  dann von selbst „Im Netzwerk anmelden“ an.
- Bekanntes Problem: Das Anmeldefenster (iOS „Captive Network Assistant“, Android-Portal-Ansicht)
  ist ein eingeschränkter Browser, der beim Verlassen schließt. Die Portalseite zeigt deshalb nur
  einen großen Knopf **„Im Browser öffnen“** plus Hinweis „Verbindung trotz fehlendem Internet
  behalten“. Das eigentliche UI läuft im normalen Browser. *Im Prototyp mit iOS und Android testen.*
- Maximale Clients am Hotspot ausreichend hoch setzen (Ziel 8; ESP-IDF erlaubt bis 10).

### 3.3 Neues WLAN einrichten (Admin)

1. Admin ist per Hotspot verbunden und wählt „WLAN hinzufügen“ → Liste aus Scan.
2. Der ESP testet die Zugangsdaten **im AP+STA-Betrieb**, der Hotspot bleibt also bestehen.
3. Ergebnis kommt live ins UI: „Verbunden mit *Heimnetz*. Louie ist dort unter
   http://louie.local (192.168.1.57) erreichbar.“ Knopf „Jetzt wechseln“ oder „Hotspot behalten“.
4. Erst nach Bestätigung wird der Hotspot abgeschaltet. Falsches Passwort → Fehlermeldung,
   nichts geht verloren.

Option für Admin: **Hotspot zusätzlich zum WLAN offen lassen** (für Gäste ohne Zugang zum
Heimnetz). Kostet etwas RAM und Funkzeit, deshalb standardmäßig aus.

## 4. Rollen und Berechtigungen

### 4.1 Rollen

| Rolle | Wie erhält man sie | Darf |
|---|---|---|
| **Gast** | Seite öffnen | Status sehen |
| **Spieler** | Platz/Farbe wählen (ohne Passwort) | Boosts u. ä. laut Modus |
| **Spielleiter** | Freie Rolle beanspruchen oder übergeben bekommen; eine pro Runde | Modus wählen, Runde freigeben/stoppen, Spieler als ausgeschieden markieren |
| **Admin** | Passwort eingeben (Sitzung läuft nach 30 min Leerlauf ab) | Alles inkl. WLAN, Grenzwerte, Modellprofil, Update, Werksreset |

Spieler und Spielleiter sind **Rollen in der laufenden Partie**, keine Konten. Admin ist
die einzige geschützte Stufe. Welche Rechte Spieler haben (z. B. „Modi speichern“, „Spielleiter
werden“), stellt der Admin ein (siehe 4.3).

### 4.2 Admin-Zugang

- **Ersteinrichtung**: Beim ersten Start legt man im Assistenten (siehe 6.1) das Admin-Passwort fest.
  Damit nicht jemand in Funkreichweite zuvorkommt, wird das mit **Umlegen des Hebels** bestätigt
  (physischer Zugriff = Besitzer).
- **Passwort vergessen**: Hebel-Geste beim Start (z. B. 10× umlegen) setzt das Admin-Passwort zurück.
  Spielmodi bleiben, WLANs werden aus Sicherheitsgründen ebenfalls gelöscht.
- Speicherung: gesalzener Hash (SHA-256, mehrfach iteriert) in `config.json`. Ohne HTTPS geht das
  Passwort im Klartext übers WLAN. Für ein Spielzeug im WPA2-Netz ist das vertretbar, wird aber
  im UI nicht verschwiegen („nicht dasselbe Passwort wie fürs Heimnetz verwenden“).
- Brute-Force-Bremse: nach 5 Fehlversuchen 1 min Sperre.

### 4.3 Technische Vorbereitung für Mehrbenutzer

Damit Mehrbenutzer später nur ein Zusatz ist:

- Jede Verbindung hat eine **Sitzung** (zufälliges Token, 128 bit, im `localStorage` und als Cookie).
  Neu laden oder kurzer WLAN-Abbruch → gleicher Platz, gleiche Rolle.
- Berechtigungen sind eine **Liste von Rechten**, keine festen Rollen im Code:
  `view`, `play`, `lead`, `modes.create`, `modes.delete_own`, `admin`.
  Eine Tabelle Rolle → Rechte steht in der Konfiguration.
- Gespeicherte Objekte (Modi) haben von Anfang an ein Feld `owner` (Sitzung bzw. später Profil-ID).
- Stufe 2: **Profile** mit Spitzname, Farbe, Emoji, ohne Passwort. Das Gerät merkt sich Profile pro
  Handy über das Token. Damit: eigene Modi, Statistik („Wer fliegt am häufigsten raus?“).
- Stufe 3 (nur bei Bedarf): Profile mit PIN, weitere Rollen.

## 5. Spiel

### 5.1 Zustände

```
          Hebel aus / Stopp im UI
   ┌────────────────────────────────────┐
   ▼                                    │
 BEREIT ──(Modus wählen)──► BEREIT ──Hebel an──► LÄUFT ──Ende laut Modus──► ENDE ──► BEREIT
   ▲                                    │  ▲
   │                                    ▼  │
   └──── Leerlauf 15 min ──► SCHLAF   PAUSE (Spielleiter)
```

- Modus wechseln nur in BEREIT/ENDE und bei Hebel „aus“.
- Hebel steht beim Aufwecken auf „an“ → **keine** Runde starten, UI zeigt „Hebel auf Aus stellen“.
  Danach gilt Hebel an = Start. Damit gibt es keinen Überraschungsstart beim Aufwecken.
- Optional (Admin-Einstellung): **Start nur nach Freigabe** durch den Spielleiter. Standard:
  Hebel startet direkt.
- Der Hebel liegt in Reihe mit dem Motor und trennt ihn also **immer hardwareseitig**. Der
  Stopp ist damit nie von der Software abhängig.

### 5.2 Spielmodi als Daten

Ein Modus ist eine JSON-Beschreibung, kein Code. Bausteine (aus v1 `config.yml` weiterentwickelt):

```json
{
  "id": "chaos",
  "name": "Chaos",
  "owner": "builtin",
  "speed": {"type": "random", "min": 30, "max": 90, "change_every_s": [2, 6]},
  "reverse": {"chance": 0.10, "duration_s": [0.5, 1.5]},
  "pause":   {"chance": 0.05, "duration_s": [1, 2]},
  "ramp_up": {"to": 100, "over_s": 120},
  "boost":   {"who": "out", "strength": 25, "duration_s": 2, "cooldown_s": 10, "per_round": 3},
  "rewind":  {"who": "all", "duration_s": 0.8, "cooldown_s": 20, "per_round": 2},
  "end":     {"type": "lever"}
}
```

- **Geschwindigkeiten in Prozent** des erlaubten Bereichs aus dem Modellprofil
  (0 % = Mindestspannung, 100 % = Nennspannung, darüber nur bis zur Turbo-Grenze).
  Ein Modus läuft dadurch unverändert auf altem und neuem Louie und auf Chewie.
- Der Server **klemmt** jeden Wert auf die Admin-Grenzen, auch bei Boosts und Probefahrt.
- **Rückwärtsfahrt**: erlaubt, aber standardmäßig nur in kleinen Dosen. Gegen einen rückwärts
  drehenden Louie kann man sich kaum wehren, lange Rückwärtsphasen sind also frustrierend.
  Der Server erzwingt (Admin-Grenzen, Standardwerte in Klammern): max. Dauer je Rückwärtsstoß
  (1,5 s), Mindestabstand zwischen zwei Stößen (8 s), max. Anteil an der Rundenzeit (10 %).
  Richtungswechsel immer über eine Rampe (Brownout, siehe Hardware-Konzept 5.1).
- **Rückspuler (Multi-User)**: Jeder Spieler kann vom Handy aus einen sehr kurzen Rückwärtsstoß
  (ca. 0,5–1 s) auslösen, um andere zu ärgern. Begrenzt durch Kontingent pro Runde, Abklingzeit
  und die globalen Rückwärts-Grenzen oben. Gleichzeitige Anfragen werden nicht addiert.
- Eingebaute Modi (Vorschlag): Klassisch, Gemütlich, Steigerung, Zufall, Chaos (mit Rückwärts),
  Last Chicken Standing (Boosts für Ausgeschiedene).

### 5.3 Dürfen Nutzer Modi speichern?

Vorschlag: **Ja, standardmäßig an, aber abschaltbar.** Begründung: Modi können durch das Klemmen
auf die Grenzen nichts kaputt machen, und „eigenen Modus bauen“ ist ein Spielspaß für Kinder.

- Jeder darf einen Modus für die nächste Runde anpassen, ohne zu speichern („nur diese Runde“).
- Speichern legt einen neuen Modus mit `owner` an. Löschen darf nur der Ersteller oder Admin.
- Admin kann: Speichern für Nutzer abschalten, Modi sperren, maximale Anzahl festlegen
  (Flash-Grenze, z. B. 30).
- Eingebaute Modi sind schreibgeschützt und lassen sich nur kopieren.

## 6. User Experience

Mobil zuerst, Hochformat, große Bedienelemente (≥ 48 px), einhändig, dunkles und helles Design,
deutsch (Texte zentral, Übersetzung später möglich). Live-Zustand per WebSocket; bei
Verbindungsabbruch ein deutlicher Hinweis und automatisches Neuverbinden.

### 6.1 Ersteinrichtung (Assistent im Hotspot)

1. Modell wählen: Louie alt / Louie neu / Chewie (Bilder)
2. Drehrichtung: „Hebel an. Dreht Louie richtig herum?“ → Ja / Nein (Richtung wird gespeichert)
3. Admin-Passwort festlegen, mit Hebel bestätigen
4. Optional: Heim-WLAN einrichten (siehe 3.3)
5. Fertig: Hinweis auf QR-Aufkleber und `louie.local`

### 6.2 Hauptansichten

| Ansicht | Inhalt |
|---|---|
| **Start / Lobby** | Großer Status („Bereit – Hebel umlegen“), aktueller Modus als Karte, Plätze 1–4 in Hühnerfarben zum Antippen, Akkustand, Spielleiter-Rolle frei/belegt |
| **Runde (Spieler)** | Großer Boost-Knopf mit Abklingring und Restanzahl, aktuelle Geschwindigkeit, „ausgeschieden“-Status |
| **Runde (Spielleiter)** | Geschwindigkeit live, Spieler als ausgeschieden markieren, Pause, Stopp |
| **Modi** | Liste, Details, „Anpassen“ mit Schiebereglern und Vorschau-Kurve, „Probefahrt“ (10 s, nur bei Hebel an) |
| **Admin** (hinter Schloss-Symbol) | WLAN, Modell & Grenzen, Rechte der Nutzer, Gerät, Update, Diagnose |

### 6.3 Admin-Einstellungen

| Bereich | Einstellungen |
|---|---|
| WLAN | Netze hinzufügen/entfernen/Priorität, Hotspot-Name und -Passwort, Hotspot zusätzlich offen, Hostname |
| Modell & Grenzen | Modellprofil, Mindest- und Nennspannung, Turbo-Grenze, max. Rampe (V/s), Drehrichtung |
| Rückwärts | erlaubt ja/nein, max. Dauer je Stoß, Mindestabstand, max. Anteil an der Runde, Rückspuler für Spieler ja/nein, Kontingent pro Spieler |
| Energie | Leerlaufzeit bis Schlaf, Unterspannungs-Warnung und -Abschaltung |
| Rechte | Modi speichern, Spielleiter werden, Start nur mit Freigabe |
| Gerät | Admin-Passwort ändern, Konfiguration sichern/laden (JSON), Neustart, Werksreset |
| Update | Firmware-Dateien hochladen (siehe 8.3) |
| Diagnose | Akku, Motorstrom, Hebelzustand, RSSI, freier Speicher, letzte Fehler |

### 6.4 Details, die oft vergessen werden

- **Schlaf trotz offener Tabs**: Handys halten WebSockets im Hintergrund offen. Schlaf hängt deshalb
  an „keine Runde und keine Bedienung seit 15 min“, nicht an „kein Client verbunden“.
  1 min vorher Hinweis im UI mit „Wach bleiben“.
- Nach dem Schlaf zeigt das UI „Louie schläft – Hebel umlegen zum Wecken“ und verbindet neu.
- **Status-LED** zeigt Netzmodus (z. B. langsam blinken = Hotspot, an = WLAN, schnell = Fehler),
  damit man ohne Handy weiß, wo man suchen muss.
- Akku niedrig: Warnung im UI, Runde endet sauber vor der Abschaltung.

## 7. Schnittstelle Browser ↔ Gerät

- **REST (JSON)** für Konfiguration und Verwaltung, **ein WebSocket** `/ws` für Live-Zustand
  und Aktionen während des Spiels. Der Server ist die einzige Quelle der Wahrheit; Clients senden
  Wünsche, der Server prüft Rechte und Grenzen.
- Zustand wird bei Änderungen gesendet, im Spiel höchstens 10× pro Sekunde.

| Methode | Pfad | Recht |
|---|---|---|
| GET | `/api/state` | view |
| POST | `/api/session` (Spitzname, Platz) | – |
| GET / POST | `/api/modes` | view / modes.create |
| PUT / DELETE | `/api/modes/{id}` | Ersteller oder admin |
| POST | `/api/admin/login`, `/api/admin/logout` | – / admin |
| GET / PUT | `/api/admin/config` | admin |
| GET | `/api/admin/wifi/scan` | admin |
| POST / DELETE | `/api/admin/wifi`, `/api/admin/wifi/{ssid}` | admin |
| POST | `/api/admin/update`, `/api/admin/reboot`, `/api/admin/reset` | admin |

WebSocket-Nachrichten (Auswahl):

```
Server → Client: {"t":"state", "phase":"running", "speed":62, "mode":"chaos", "lever":true,
                  "battery":3.85, "players":[…], "leader":"s_ab12"}
                 {"t":"event", "kind":"boost", "seat":2}
Client → Server: {"t":"boost"}  {"t":"rewind"}  {"t":"claim", "seat":3}  {"t":"lead"}
                 {"t":"select_mode", "id":"chaos"}  {"t":"out", "seat":1}  {"t":"stop"}
```

## 8. Aufbau der Firmware

### 8.1 Schichten

```
firmware/
  main.py                 Start, Verdrahtung der Teile
  louie/
    hal/                  Hardware: motor.py, lever.py, battery.py, led.py
      sim.py              dieselben Klassen simuliert (PC)
    core/                 reines Python, ohne Hardware und Netz
      game.py             Zustandsautomat, Runde
      modes.py            Modus-Interpreter → Sollgeschwindigkeit über der Zeit
      limits.py           Modellprofile, Klemmen, Rampen
      perms.py            Rollen → Rechte
    net/                  wifi.py (STA/AP/Fallback), dns.py (Captive Portal), mdns
    web/                  Microdot-App, REST, WebSocket-Hub, Sitzungen
    store.py              JSON-Dateien, atomar schreiben
  static/                 gebautes Web-UI (*.gz)
web/                      Quellen des Web-UI
tests/                    pytest gegen core/ und hal/sim.py
```

- **Motorsicherheit**: eigener Task mit Watchdog. Bekommt er 500 ms keine Sollwerte, fährt er auf 0.
  Rampen und Grenzen gelten in dieser untersten Schicht, egal was darüber passiert.
  Der Hardware-Watchdog des ESP startet bei hängender Firmware neu, der Motor steht dann.
- nFAULT des DRV8833 → Runde stoppen, Fehler im UI.

### 8.2 Speicher (LittleFS)

| Datei | Inhalt |
|---|---|
| `config.json` | Modellprofil, Grenzen, Rechte, Admin-Hash, Energie |
| `wifi.json` | bekannte Netze, Hotspot-Daten |
| `modes/*.json` | eigene Modi (eingebaute stecken in der Firmware) |
| `profiles.json` | später: Profile |

Schreiben nur bei Änderungen, immer erst in Temp-Datei, dann umbenennen (kein kaputtes JSON bei
Stromausfall). WLAN-Zugangsdaten liegen **nur auf dem Gerät**, nie im Git.

### 8.3 Updates

4 MB Flash reichen knapp für zwei vollständige Firmware-Partitionen plus Dateisystem. Daher:

- **Stufe 1**: Update der Python-Dateien und des Web-UI übers WLAN (Upload ins Dateisystem,
  mit Rücksprung auf die Vorversion, wenn der Start fehlschlägt). Deckt fast alle Änderungen ab.
- MicroPython selbst wird über USB-C aktualisiert (selten nötig).
- Echtes OTA mit zwei App-Partitionen erst prüfen, wenn die Firmwaregröße feststeht.

## 9. Entwicklung parallel zur Hardware

- `just sim`: startet den kompletten Server auf dem PC (CPython) mit `hal/sim.py`. Simulierter
  Hebel (Taste oder Knopf im UI), simulierter Motor, simulierter Akku. Das Web-UI zeigt im
  Simulator einen kleinen animierten Louie. Damit lassen sich UI und Spiellogik fertig bauen,
  bevor die Platine existiert.
- `just test`: pytest für Spiellogik, Modi, Grenzen, Rechte.
- `just flash` / `just upload`: MicroPython flashen bzw. Dateien per `mpremote` übertragen.
- Mehrere Handys testen: Simulator im Heimnetz starten und mit echten Handys verbinden.

## 10. Ausbaustufen

| Stufe | Inhalt |
|---|---|
| **0 – jetzt** | Simulator, Spiellogik mit Tests, Protokoll, UI-Gerüst; Machbarkeitstest MicroPython auf XIAO ESP32-C3 |
| **1 – MVP** | WLAN mit Hotspot-Fallback und Captive Portal, Ersteinrichtung, Admin-Passwort, eingebaute Modi, Hebel Start/Stopp, Live-Zustand, Boosts, Spielleiter |
| **2** | Eigene Modi speichern, Rechte-Einstellungen, Update übers WLAN, Diagnose |
| **3** | Profile, Statistik, weitere Sprachen, Mehrbenutzer-Rechte |

## 11. Offene Entscheidungen

- [ ] MicroPython bestätigen (Machbarkeitstest nach 2.3)
- [ ] Start per Hebel direkt oder nur nach Freigabe als Standard?
- [ ] Hotspot standardmäßig mit Passwort (Vorschlag) oder offen?
- [ ] Hebel-Gesten festlegen (Hotspot erzwingen, Admin-Reset) – Verwechslung mit normalem Spiel ausschließen
- [ ] Nutzer dürfen Modi speichern: Standard an (Vorschlag)?
- [ ] Captive-Portal-Verhalten auf iOS und Android im Prototyp prüfen
- [ ] Wie viele gleichzeitige Clients brauchen wir sicher (Vorschlag: 8)?
