# Web-UI Proof of Concept (Testumgebung)

Klickbarer Prototyp des Web-UI nach [docs/web-ui-konzept.md](../../docs/web-ui-konzept.md) und
[docs/modus-baukasten.md](../../docs/modus-baukasten.md).
Eine einzige Datei (`index.html`), Vanilla JS, ohne externe Abhängigkeiten, läuft offline.

## Öffnen

`index.html` direkt im Browser öffnen (`file://` genügt, kein Server nötig).
Im eingebauten oder geteilten Browser geht auch: `python3 -m http.server 8776 -d web/poc`
(freien Port wählen) und dann `http://localhost:8776/` öffnen.

- **Desktop (≥ 700 px):** links die Testumgebung, rechts mehrere simulierte Handys (je 375 × 720 px).
- **Schmal (< 700 px, echtes Handy):** ein Handy im Vollbild, oben eine dünne Testleiste mit
  Handy-Umschalter, Hebel, „＋📱“ und 🧪 (klappt die volle Testumgebung auf).

## Was simuliert ist

- **Server** (JS-Objekt, einzige Quelle der Wahrheit): Phasen Bereit/Countdown/Läuft/Pause/Ende/Schlaf,
  Hebel, Akku, Blockier-Erkennung, Rollen (Leiter, Mitspieler, Zuschauer, Besitzer-Sitzung), Mitspieler-Handys,
  Mitspielerliste (Joker-Konten, Raus-Status, Ergebnis und Titel hängen am Mitspieler, nicht an einer Farbe), gemeinsame Joker-Sperre, Rückspul-Sperre, Ticker, Anfragen
  (Steuerung/Mitspielen) mit 15-s-Timeout, verwaiste Steuerung, Platzgarantie, Hebel-Modus,
  Testbetrieb (Probefahrt/Werkstatt: Hebel startet dann keine Runde). Alle Rechte prüft der Server;
  abgelehnte Aktionen kommen mit Grund als Toast zurück.
- **Spielmodi Schema 2** (Flugplan · Würze · Joker · Ende): Abschnitte Konstant, Rampe, Stufen, Sägezahn
  (hart/weich, Rücksprung-Stoß, steigend/fallend), Welle (Sinus/Herzschlag), Zufall, Pause, mit `repeat` und
  „Danach: Von vorn / Halten / Ende“. Tempo −100…100 % (0 % = Mindesttempo, 100 % = Fliehkraft-Grenze),
  Richtungswechsel mit kurzem Halt. Joker ⏩ Schub, ⏪ Zurück, 🛑 Bremse, 🎭 Schein-Bremse mit „wer darf“
  (alle/Aktive/Geister), Konto je Art oder gemeinsam, Abklingzeit, gemeinsame Sperre. Jede Zahl ist der Wert
  für Fiesheit 3 oder eine 5er-Liste. Ein Interpreter für Spiel, Vorschau, Werkstatt und Baukasten.
  Eingebaut: Klassisch, Druckkochtopf, Würfelmotor, Turbulenzen, **Rückspul-Duell (⏪ + ⏩)**, Letztes Huhn.
- **Modus-Baukasten** (Modi → „＋ Neuer Modus“ oder ⧉ „Kopieren & bearbeiten“): Vorlagen-Galerie (inkl.
  Sägezahn und dem Beispiel **Gewitter**), Übersicht mit fester Vorschau-Kurve (geklemmt, rückwärts rot,
  Würze-/Joker-Symbole, ▼ Rücksprung) und Fiesheits-Umschalter, Seiten für Flugplan (Abschnitt-Karten mit
  ⋯-Menü und Rückgängig), Würze, Joker, Ende, Live-Hinweise mit Ein-Tipp-Vorschlägen, Trocken abspielen mit
  Test-Spielern (Bots), Probefahrt, Speichern mit Name/Symbol/Satz, Profi (Fiesheits-Tabelle, JSON, Import).
  Das Beispiel „Sägezahn-Duell“ aus dem Konzept lässt sich Schritt für Schritt nachklicken.
- **Mitspielen = ein Tipp**: Name vom Namenswürfel 🎲 oder von Hand ✏️. **Farbe optional** (🎨: Rot, Gelb, Grün, Blau,
  Lila, Orange, Türkis, Pink oder keine), Standard ist neutral; Farben dürfen mehrfach vorkommen. Leiter und Besitzer
  ändern Name und Farbe jedes Mitspielers (Spieler-Zeile antippen oder Spieler & Handys).
- **Spielerzahl** (🔒 Besitzer → Grenzen, 2–8, Standard 4) begrenzt die mitspielenden Handys inkl. mitspielendem Leiter;
  danach „Alle Plätze belegt (4/4)“. Bis 8 Mitspieler passen ohne Scrollen (kompakte Chips in 2 Reihen).
- **Spieler = Platz** (Name, Farbe optional) mit 0..1 Handy und 0..n **Funk-Taster-Eingängen** (Gerät + Taste +
  einfach/doppelt/lang → Joker 1, Joker 2 = erster/zweiter Joker des Modus, „Ich bin raus“ nur mit Statistik, oder nichts).
  Kontingente, Abklingzeit und Sperre hängen am Spieler, egal ob per Handy oder Taster ausgelöst. Chips zeigen 📱/🔘.
  Wer weder Handy noch Taster hat, kommt in der App nicht vor.
- **🔘 Funk-Taster anlernen** (🔒 Besitzer → 🔘 Funk-Taster): Geräteliste (Typ, Tasten, 🔋, 📶, zuletzt gesehen, zugeordnet),
  „＋ Taster anlernen“ = 30-s-Lernmodus („Drück jetzt eine Taste“; nur nahe Geräte, Signal besser als −70 dBm) → Typ
  erkannt → Name → bei Mehrfach-Geräten „Jede Taste einmal drücken“ → Belegung. Entfernen per Halten. Hinweis auf
  fremde Geräte in Reichweite.
- **Belegung** (Steuerhandy für den Abend, Besitzer auch; Mehr → 🔘 Funk-Taster oder Spieler-Sheet → „＋ Taster zuordnen“):
  Vorlagen „1 Spieler ⏪/⏩“, „2 Spieler à 2 Tasten“, „4 Spieler à 1 Taste“, „Eigene“; Tabelle Taste → Spieler (vorhanden
  oder „＋ neuer Spieler“ mit Zufallsname) → Aktion. 1-Tasten-Geräte: optional „Doppeldruck = Joker 2“ (Hinweis: macht
  Einfach-Drücke ca. 0,3 s langsamer).
- **Handy-Beitritt**: Gibt es reine Taster-Plätze, wählt man „Neuer Platz“ oder „🔘 Zu Platz … dazu“.
- **Taster-Joker** laufen über dieselbe Server-Prüfung; Ticker „🔘 ⏪ Oma hat zurückgespult“. Abgelehnte Taster-Drücke
  (Sperre, leer, nicht belegt) erscheinen dezent nur im Ticker des Steuerhandys.
  „Statistik & Ausscheiden“ und „letzter Spieler“ beziehen sich nur auf Handy-Mitspieler; jeder setzt sich selbst auf
  „raus“, der Leiter nur zur Korrektur (z. B. verwaistes Handy).
- **🔄 Spielerwechsel** (Party: feste Handys am Platz, wechselnde Personen): auf dem Mitspieler-Handy in Bereit/Ende
  oder im Mitspieler-Sheet des Leiters. Neuer Zufallsname, Farbe bleibt, Abend-Werte zurückgesetzt, Ticker
  „Platz von Lena: jetzt Kapitän Keks“. Beim Beitreten ist der Zufallsname Standard.
- **Zuschauer** sehen eine gedämpfte, gestreifte Seite mit 👀; Mitspieler sind neutral mit Namensschild.
- **Recht „Modi erstellen“** (Besitzer → Rechte): aus / Entwürfe (Standard Kinder) / Speichern.
- **Gamepad**: 1 Joker = großer runder Halte-Knopf, 2 Joker = zwei Hälften (⏪ links, ⏩ rechts) mit eigenen
  Punkten und Abklingbalken, bei gemeinsamem Konto Punkte mittig. Nach „Ich bin raus“ Geister-Layout.
- **„📊 Statistik & Ausscheiden“** (Standard AUS; Leiter unter Mehr → Spieler & Handys, Vorgabe im 🔒 Besitzer → Rechte).
  Kein automatisches Einschalten durch den Modus. AUS: kein „Ich bin raus“, kein Sieger antippen, keine Raus-Korrektur,
  kein Sieger-Banner, keine Geister-Layouts; Geister-Joker sind inaktiv, Rundenende „letzter Spieler“ entfällt
  (Modus-Karte/Detail und Baukasten zeigen dezent „👻 Geister-Joker nur mit Statistik & Ausscheiden“).
  AN: „Ich bin raus“, Sieger, Geister-Joker, „letzter Spieler“ und eine kleine **Abend-Statistik** (Siege und Joker pro
  Spieler; zurückgesetzt bei Spielerwechsel bzw. Neustart). Titel aus Joker-Ereignissen gibt es immer.
- **Steuerhandy**: Zweifach-Wahl „🎛️ Nur steuern / 🎮 Steuern + mitspielen“ (mitspielen = Farbe wählen,
  gleiches Gamepad wie alle plus Leiterleiste, Mitspieler-Handys gehen mit an).
- **Kalibrierung** (Assistent und Werkstatt): Mindesttempo (= 0 %) und Fliehkraft-Grenze (= 100 %) mit kleiner
  Skizze. Die Draufsicht zeigt „stockt“ unter dem Mindesttempo und „fliegt zu hoch“ ab der Grenze bzw. bei 100 %.
- **Hebel-Bestätigung**: nur wenn das Steuerhandy 15 s nicht antwortet oder verwaist ist. Geste: Hebel 3× schnell
  an-aus (binnen 4 s); in der Simulation den großen Hebel-Knopf dreimal schnell klicken.
- **Nach Schlaf/Neustart** hat das letzte Steuerhandy 20 s (echt 2 min) Vorrang.
- **Pause → Weiter** (1 s halten) läuft immer über 3-2-1. Halte-Knöpfe geben bei zu kurzem Tipp einen Hinweis.
- **Besitzer-Sitzung** hält bis „Abmelden“ (Kopfzeile) oder 5 min Leerlauf.
- **Handys**: jede Instanz ist eine eigene Sitzung (Token) mit eigener Navigation. „WLAN trennen“, „neu laden“
  (Token stellt Rolle und Mitspielerplatz wieder her), „✕“ entfernen. Bis zu 9 Handys (damit „Plätze belegt“ testbar ist).
- **🔘 Funk-Taster (simuliert)** in der Testleiste: „＋ Gerät“ (Button1, RC Button 4, WiZmote, fremdes Gerät eines
  Nachbarn), Tasten mit Klick = einfach, Doppelklick = doppelt, 1 s halten = lang, Batterie- und Signal-Regler,
  Verzögerung (BLE ≈ 350 ms, ESP-NOW ≈ 20 ms) und Blink-Rückmeldung.
- **Draufsicht**: Mitspieler als Punkte um den Turm (grau oder in ihrer Farbe, 👻 wenn raus), bis 8.
- **Zeitraffer** für die Server-Zeit. Fristen sind verkürzt: verwaiste Steuerung und Platzgarantie 20 s statt 2 min.
- **Ereignis-Log**: Nachrichten Handy → Server, Server → Handy(s) und Hardware im WS-Format;
  `state`-Nachrichten und Herzschläge nur mit Häkchen.

Besitzer-Passwort im PoC: **`louie`** (bzw. das im Assistenten gesetzte).

## Szenarien (Schnellstart in der Testumgebung)

| Szenario | Inhalt |
|---|---|
| 🆕 Erststart / Assistent | Captive-Portal „Im Browser öffnen“, dann 8 Schritte (Modell, Drehrichtung, Mindesttempo, Fliehkraft-Grenze, Passwort, WLAN, Profil, Fertig). Hardware dreht anfangs falsch herum; Louie dreht erst ab 18 % Rohwert zuverlässig und fliegt ab 72 % zu hoch |
| 👪 Familienabend | Papa steuert allein, alle spielen ohne Handy |
| 🧒 Kindergeburtstag | Profil Kinder (Deckel 55 %, 3 Modi, Fiesheit ≤ 3, nie rückwärts, Modi nur als Entwurf) |
| 🎉 Party (4 Handys) | Lena (Rot), Max und Oma (neutral) spielen mit Handy, Rückspul-Duell mit ⏪ und ⏩ |
| 👻 Geisterstunde (Letztes Huhn) | Statistik & Ausscheiden an: „Ich bin raus“, Geister-Boost, letzter Spieler gewinnt, Abend-Statistik |
| 🔄 Party-Rotation | 4 feste Handys (Platz 1–4), zwischen den Runden „🔄 Spielerwechsel“ |
| 🔘 Familie mit Tastern | Papa steuert mit Handy, 4 Button1 an Oma/Opa/Mia/Tim (einfach = ⏪, doppelt = ⏩), Rückspul-Duell, dazu ein fremdes Nachbar-Gerät |
| 🔀 Gemischt | Lena und Max mit Handy, RC Button 4: Tasten 1/2 = Max (Handy + Taster), 3/4 = Oma (nur Taster) |
| 🍽️ Großer Tisch (8 Handys) | Spielerzahl 8, Papa steuert und spielt mit, zweimal Rot und zweimal Blau; „+ Handy“ → 9. Handy sieht „Alle Plätze belegt (8/8)“ |
| 🚪 Gast kommt in laufende Runde | Zuschauer → „Mitspielen?“ → Farbe → „nächste Runde dabei“ |
| 📵 Steuerhandy verschwindet | Papa offline, nach 20 s „Steuerung übernehmen“ |
| 🔧 Werkstatt | Papa als Besitzer in der Werkstatt (für „Echt“ Hebel an) |

## Grenzen des PoC

QR-Code ist ein Platzhalter-Muster, Sichern/Laden/Update nur als Hinweis. Baukasten: kein QR-/Datei-Export,
Import nur per Textfeld, Vorteil pro Spieler (Handicap) nur als Schalter im Modus, nicht in der Runde.
Kalibrierung ohne Spürbarkeits- und Leerlaufstrom-Schritt.
