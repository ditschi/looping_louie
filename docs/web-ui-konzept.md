# Web-UI-Konzept: Rollen, Ansichten, Spielmodi, Werkstatt

Stand: 2026-11-01 · Status: Vorschlag, ersetzt Abschnitt 4 und 6.2 von [software-konzept.md](software-konzept.md)
in den genannten Punkten. Klickbarer Proof of Concept: [web/poc/index.html](../web/poc/index.html).

Erarbeitet von einem Agenten-Team: Kritik des alten Entwurfs (`web/prototype/`), Nutzungsszenarien,
Rollenmodell, Spielmodus-Konzept. Danach zusammengeführt, gebaut und mit Persona-Tests geprüft.

## 1. Bild vom Spiel

**Louie ist der Pilot** im Flugzeug, das um den Turm kreist. Jeder Mitspieler hat eine **Wippe**
und beschützt mit seiner Wippe **drei Hühner** (Chips). Wer alle Hühner verloren hat, ist raus.
Das UI zeigt Louie immer als Flugzeug/Pilot ✈️, Hühner nur als Chips der Spieler 🐔.

**Tempo-Skala**: 0 % = **Mindesttempo** (Louie dreht gerade zuverlässig), 100 % = **Fliehkraft-Grenze**
(darüber sinkt Louie durch die Fliehkraft nicht mehr ab und erwischt keine Hühner mehr, unspielbar).
Negative Werte = rückwärts. Beide Punkte werden pro Gerät kalibriert.

**Es geht um den Spaß am Tisch.** Alle sehen live, wer dabei ist und wer rausfliegt. Hühner werden nicht
gezählt, und niemand muss im Handy pflegen, dass er ausgeschieden ist. Dafür gibt es die optionale
Einstellung **„📊 Statistik & Ausscheiden“** (Standard **aus**). Ist sie aus, zeigt das UI nichts davon:
kein „Ich bin raus“, kein Sieger, keine Geister-Joker, kein Rundenende „letzter Spieler“. Ist sie an,
meldet sich jeder mit „Ich bin raus“, der Spielleiter kann den Sieger antippen, und es gibt eine
Abend-Statistik. Automatische Titel aus Joker-Ereignissen („Oberfiesling“) gibt es immer, weil sie
keine Eingabe brauchen.

## 2. Was der alte Entwurf falsch macht (Kurzfassung)

- Eine lange Scrollseite (Lobby ca. 1,5 Bildschirme, NOTAUS unterhalb des sichtbaren Bereichs).
- Ohne Spielleiter darf jeder Modus und Fiesheit ändern → wildes Umschalten.
- Spielleiter wird, wer zuerst tippt; was die Rolle darf und wie man sie abgibt, steht nirgends.
- Kein Einrichtungs-Assistent, kein Testmodus, keine Modi-Seite, Louie als Huhn dargestellt.
- Gut und übernommen: Phase bestimmt die Ansicht, QR + Farbe antippen, großer Halte-Knopf mit
  Ring, „wer hat gespult“, Geister-Boost, ehrliche Verbindungs-/Akku-Hinweise, Hebel-Hinweise.

## 3. Nutzungsszenarien (Auswahl, nach Häufigkeit)

| # | Szenario | Handys | Folgerung |
|---|---|---|---|
| S2 | **Familienabend** (Primärfall) | 1 | Eine Seite reicht. Handy liegt flach auf dem Tisch, Hände an den Wippen |
| S8 | Spielen ohne Handy | 0 | eigener **Hebel-Modus** (nicht „zuletzt gewählt“), damit bei der Oma kein Chaos läuft |
| S3 | Kindergeburtstag, Steuernder spielt nicht mit | 1 | „Nur steuern“, Profil Kinder, schnell neu starten |
| S4 | Party mit Gäste-Handys | 1 + 3–7 | Mitspieler-Handys explizit einschalten, QR, Onboarding < 30 s |
| S5 | Gast kommt während der Runde | +1 | zuschauen, „nächste Runde bist du dabei“ |
| S6 | Steuerhandy weg / Akku leer | – | Übergabe ohne Passwort, verwaiste Rolle übernehmen |
| S7 | Modus anpassen am Tisch | 1 | „nur diese Runde“ vs. speichern, Probefahrt |
| S1/S10 | Erstinbetriebnahme, Verschenken | 1 | Assistent mit Modell, Drehrichtung, Mindesttempo, Fliehkraft-Grenze, Passwort |
| S11 | Neue Modi entwickeln | 1 (+PC) | **Werkstatt**: trocken mit Zeitraffer, echt mit Totmannknopf |
| S9 | Fehlersuche | 1 | Diagnose hinter dem Schloss |

Physische Randbedingungen: Während der Runde ist das Handy vor allem **Anzeige**, mit höchstens
zwei riesigen Zielen. Lesbar aus 60–80 cm, keine Wischgesten, kein Querformat erzwingen. Ohne
HTTPS gibt es keinen Wake Lock, also muss das Handy nach dem Aufwachen sofort den richtigen Zustand
zeigen. Hebel und LED sind die Wahrheit. Für Kinder: Farben und Symbole statt Text.

## 4. Rollen

Für Nutzer sichtbar sind nur drei Dinge: **Steuern**, **Mitspielen** und das **Schloss 🔒**.

| Rolle | Wie | Darf |
|---|---|---|
| **Zuschauer** | Seite öffnen (Zustand „verbunden ohne Rolle“, keine wählbare Rolle) | Status sehen, „Mitspielen?“ bzw. „Steuerung anfragen“ |
| **Mitspieler** | nur wenn Mitspieler-Handys an sind: „Mitspielen“ antippen (ein Tipp) | Joker laut Modus, „Ich bin raus“ (wenn erfasst), Stopp |
| **Spielleiter** (genau einer) | automatisch das erste Handy, wenn die Steuerung frei ist; sonst Übergabe | Modus, Fiesheit, Mitspieler-Handys an/aus, Pause/Stopp, Spieler verwalten, Probefahrt, Modi anpassen |
| **Besitzer** (Admin) | Passwort hinter dem Schloss, gilt bis „Abmelden“ oder 5 min Leerlauf (Kopfzeile zeigt „🔓 Besitzer“) | zusätzlich Werkstatt, Einrichtung, WLAN, Grenzen, Profile, Rechte, Update |

**Spielleiter ≠ Besitzer.** Der Spielleiter braucht kein Passwort. Alles, was er auslöst, klemmt
der Server auf die Besitzer-Grenzen. Ein Kind am Leiter-Handy kann also höchstens Modus und
Fiesheit ändern, im Profil „Kinder“ auch nur innerhalb der freigegebenen Modi.

### 4.1 Spielleiter werden und abgeben

1. **Automatisch**: Ist die Steuerung frei, wird das erste Handy Spielleiter, ohne Klick.
   Nach der Ersteinrichtung ist das Einrichtungs-Handy Spielleiter.
2. **Anfrage**: Ein anderes Handy tippt „Steuerung anfragen“. Der Leiter bekommt ein Banner
   „Lena möchte steuern – Abgeben / Ablehnen“.
3. **Hebel-Bestätigung**: Nur wenn der Leiter **nicht antwortet** (15 s), darf der Anfragende den
   Hebel **3× schnell umlegen** (an-aus dreimal binnen 4 s; 30-s-Fenster, nur in BEREIT/ENDE, Motor
   bleibt aus). Physischer Zugriff schlägt Funk. Ein ausdrückliches **„Nein“ zählt**: Dann gibt es
   keine Eskalation. Während einer Runde wartet die Anfrage. Solange das Fenster offen ist, zeigen
   **alle** Handys „Hebel bestätigt gerade Max als Steuerer – nicht zum Starten benutzen“, und der Leiter
   kann abbrechen. Beim Ablehnen gibt es zusätzlich „Für heute sperren“ (Steuer- und Mitspiel-Anfragen).
4. **Verwaist**: Ist das Leiter-Handy 2 min getrennt (in einer Runde: bis Rundenende plus 2 min),
   sehen alle „Steuerung übernehmen“.
5. **Abgeben** im Leiter-Menü: an ein bestimmtes Handy oder „freigeben“ (mit Rückfrage).
6. **Nach Schlaf/Neustart** hat das Handy des letzten Leiters 2 min Vorrang, damit nicht zufällig ein
   Gast-Handy Leiter wird, das sich zuerst verbindet.
7. Besitzer-Einstellung **„Wer darf steuern“**: jeder (Standard) / nur mit Hebel-Bestätigung (Standard im Profil Kinder) / nur Besitzer.

### 4.2 Mitspieler-Handys (Multiplayer)

- **Standard: aus.** Andere Handys sind Zuschauer und sehen Status plus „Mitspielen?“. Die Anfrage
  geht als Banner an den Leiter, der sie mit einem Tipp annimmt. Damit sind auch die Mitspieler-Handys an.
- Der Leiter schaltet auf der Spiel-Seite **„Mitspieler-Handys“** ein. Sein Handy zeigt einen QR-Code
  (Vollbild zum Herzeigen). Wer beitritt, tippt **„Mitspielen“** und ist dabei: Der Name kommt vom
  **Namenswürfel**, und man kann ihn jederzeit **von Hand ändern** (Textfeld).
- **Farbe ist optional.** Standard ist ein **neutraler Hintergrund** ohne Farbe. Wer will, wählt eine
  Farbe (Schnellwahl der Standardfarben Rot, Gelb, Grün, Blau, dazu Lila, Orange, Türkis, Pink). **Farben
  dürfen mehrfach vorkommen** (z. B. zwei kombinierte Spiele mit je Rot). Spielleiter und Besitzer können
  Mitspielern eine Farbe zuweisen oder wegnehmen.
- **Spielerzahl** ist eine globale Besitzer-Einstellung (Standard 4, bis 8 für Umbauten und kombinierte
  Spiele). Sie begrenzt die mitspielenden Handys. Wer danach kommt, sieht „Alle Plätze belegt“.
- **Ein Spieler ist ein Platz mit Eingabegeräten.** Das virtuelle Spiel ist bewusst vom Tisch getrennt:
  Wer kein Gerät hat, kommt in der App nicht vor und hat eben keine Joker. Einem Spieler lassen sich
  **ein Handy, ein oder mehrere Funk-Taster, beides oder nichts** zuordnen (ohne Gerät nur sinnvoll mit
  Statistik). Wer per Handy beitritt, wählt „Neuer Platz“ oder „Zu Platz *Rot (Taster)* dazu“; nichts muss
  vorher entfernt werden. Anlernen und Tastenbelegung: siehe [geraete-anlernen.md](geraete-anlernen.md), Technik in [idee-funk-taster.md](idee-funk-taster.md).
- **Feste Handys am Platz, wechselnde Personen** (Party): Ein Handy bleibt am Stuhl liegen, die Leute
  rotieren. Deshalb ist der Zufallsname Standard, und es gibt **„🔄 Spielerwechsel“**: neuer Zufallsname,
  Werte des Abends (Titel, Vorteil) zurückgesetzt, ohne neu beizutreten.
- Der Leiter kann Mitspieler entfernen (zweiter Tipp zur Bestätigung). Entfernte Handys können erst
  wieder beitreten, wenn der Leiter eine neue Anfrage annimmt.
- Beitritt während der Runde ist möglich, man spielt aber erst ab der nächsten Runde mit.
  **Kontingente hängen am Mitspieler** (Sitzungs-Token), nicht an der Farbe; Neuladen setzt nichts zurück.
  Beim Countdown wird festgehalten, wer mitspielt. Ergebnis und Titel beziehen sich darauf.
- **Zuschauer** (später): eigene, deutlich andere Optik als der neutrale Mitspieler-Hintergrund,
  eventuell mit eigenen schwachen Zuschauer-Jokern.
- Ausschalten ist nur in BEREIT/ENDE möglich. Mitspieler werden dann wieder Zuschauer.

### 4.3 Nur steuern oder mitspielen (Leiter)

Eine deutliche Wahl auf der Spiel-Seite: **🎛️ Nur steuern** (Standard) / **🎮 Steuern + mitspielen**.
Beim Mitspielen (Farbe optional wie bei allen) bekommt der Leiter während der Runde **dasselbe Gamepad wie alle**
(alle Joker des Modus, z. B. Vorwärts-Boost und Rückwärts-Stoß, gleiche Kontingente) plus eine schmale
Leiterleiste (Pause, Stopp, Menü). Mitspielen ist nur mit eingeschalteten Mitspieler-Handys sinnvoll
und schaltet sie mit ein.

### 4.4 Rechte

| Aktion | Zuschauer | Mitspieler | Spielleiter | Besitzer |
|---|---|---|---|---|
| Status sehen | ✓ | ✓ | ✓ | ✓ |
| Stopp / Notaus im UI | – | ✓ | ✓ | ✓ |
| Joker (Boost, Rückwärts …), „Ich bin raus“ (für sich selbst) | – | ✓ | ✓ wenn er mitspielt | – |
| Modus wählen, Fiesheit, „nur diese Runde“ anpassen | – | – | ✓ (Hebel aus) | ✓ |
| Mitspieler-Handys an/aus, Spieler entfernen, Sieger antippen | – | – | ✓ | ✓ |
| Pause, Runde freigeben | – | – | ✓ | ✓ |
| Modus speichern | – | – | ✓ wenn erlaubt | ✓ |
| Probefahrt (10 s, Hebel an) | – | – | ✓ | ✓ |
| Profil Kinder/Familie/Party | – | – | – | ✓ |
| Werkstatt, Kalibrierung, WLAN, Grenzen, Rechte, Update | – | – | – | ✓ |

Den Stopp im UI sendet ein Handy mit Rolle, Zuschauer nicht (die kann jeder in Funkreichweite haben).
Er wird nie gedrosselt und mit Namen angezeigt. **Der eigentliche Notaus ist der Hebel**, und das
steht auch im UI.

### 4.5 Grenzfälle

- Leiter-Akku leer oder Tab im Hintergrund: Die Runde läuft weiter, der Hebel stoppt immer.
- Zwei Handys wollen gleichzeitig leiten: Der Server vergibt atomar, wer zuerst kommt.
- Reload oder kurzer WLAN-Abbruch: Das Token stellt Rolle, Name und Farbe wieder her.
- Schlaf oder Neustart: alle Rollen frei, Mitspieler-Handys aus.

## 5. Ansichten

Grundsatz: **Für eine normale Runde reicht eine Seite ohne Scrollen** (Ziel: alles Wichtige in
375 × 640 px sichtbar). Die Spiel-Seite **ändert sich mit der Phase**. Einstellungen sind immer
über die untere Leiste erreichbar, in der Runde über einen kleinen Menü-Knopf.

### 5.1 Steuerhandy (Spielleiter)

Untere Leiste mit drei Reitern: **Spiel · Modi · Mehr**.

| Phase | Spiel-Seite zeigt |
|---|---|
| **Bereit** | Große Statuszeile („Hebel umlegen zum Starten“), Hebel-Spiegel (nur Anzeige), **Modus-Karte** (antippen → Modi), **Fiesheit** als 5 Stufen, Zeile **Spieler** (Mitspieler mit Name/Farbe und Belegung „2/4“, Schalter „Mitspieler-Handys“, Wahl „Nur steuern / mitspielen“) |
| **Countdown** | Vollbild 3-2-1 auf allen Handys |
| **Läuft** | Vollbild ohne Leiste: Tempo groß, Modus, Restzeit falls vorhanden, Ticker der Ereignisse (wer hat welchen Joker gesetzt), 4 Farbkacheln mit Status (Handy, raus), unten zwei große Knöpfe **Pause** und **Stopp** (Stopp halten). Klein oben: ☰ Menü |
| **Pause** | Weiter (halten, danach wieder Countdown „Hände an die Wippen!“) / Stopp |
| **Ende** | optional Sieger antippen / Titel aus den Joker-Ereignissen („Oberfiesling“), Fiesheit direkt änderbar, „Nochmal = Hebel aus und wieder an“ (nur Hinweis, kein falscher Knopf), Modus ändern. Nach technischem Abbruch (blockiert, Akku) eine rote Statuskarte auf allen Handys und keine Titel |
| Sieger | Nur mit „Statistik & Ausscheiden“: Ist nur noch ein Spieler übrig, Banner „🏆 Lena hat gewonnen – Hebel aus“ |
| Hinweise | Hebel erst auf Aus · Louie schläft · Akku schwach · Blockiert · Verbindung weg |

**Modi**: Karten der Modi mit Symbol, Kurz-Satz, Handy-Bedarf (0 / 1 / alle) und Mini-Kurve.
Antippen → Detail mit Vorschau-Kurve und **Fiesheit**. „Anpassen“ öffnet wenige Regler und
„Für diese Runde“ oder „Als neuen Modus speichern“. „Probefahrt 10 s“ geht nur bei Hebel an.

**Mehr**: Spieler & Handys (QR, Liste, entfernen), Steuerung abgeben, Hebel-Modus (Modus ohne Handy),
Hilfe/Spielregeln, 🔒 Besitzer-Bereich.

### 5.2 Andere Handys

| Zustand | Ansicht |
|---|---|
| Mitspieler-Handys aus | **Zuschauer**: Status, Modus, Tempo; „Mitspielen?“ und „Steuerung anfragen“ |
| Mitspieler-Handys an, noch nicht dabei | **Mitspielen**: ein großer Knopf, darüber Name (🎲 / ✏️), „Plätze 2/4“ |
| Bereit (dabei) | Eigener Name groß, neutraler Hintergrund oder eigene Farbe, „🎨 Farbe“ (optional), Modus, „Warte auf Hebel“, eigene Joker der nächsten Runde |
| **Läuft** | **Gamepad**: ein bis zwei große Halte-Knöpfe (Joker laut Modus, Layout siehe [modus-baukasten.md](modus-baukasten.md)) mit Füllring, Kontingent-Punkten, Abklingring und globaler Sperre. Darunter klein: „Ich bin raus“ (nur wenn erfasst, Halten), Stopp |
| Raus | **Geist**: Geister-Boost-Knopf, falls im Modus vorgesehen |
| Ende | Ergebnis, Titel („Oberfiesling“), warten auf nächste Runde |

Meldungen (Toasts) erscheinen **oben** und verdecken nie Bedienelemente. Knöpfe verschieben sich nicht
unter dem Finger. Fachbegriffe (Interpreter, Totmann, Fake-out) stehen nur in der Werkstatt.

### 5.3 Besitzer-Bereich (🔒)

Profil Kinder/Familie/Party · Tempo-Deckel · Rückwärts- und Party-Grenzen · Rechte („Wer darf
steuern“, Modi speichern) · **Werkstatt** · WLAN · Gerät (Modell, Kalibrierung, Passwort,
Sichern/Laden, Update, Reset) · Diagnose. Jeder Bereich ist eine eigene Unterseite, keine lange Liste.

### 5.4 Ersteinrichtung

Assistent mit 6 Schritten, jeder Schritt passt auf einen Bildschirm: Modell → Drehrichtung
(„Hebel an. Fliegt Louie richtig herum?“) → Mindesttempo (Regler hoch, bis Louie zuverlässig dreht) → Fliehkraft-Grenze (weiter hoch, bis Louie nicht mehr absinkt) →
Besitzer-Passwort plus Hebel-Bestätigung → Heim-WLAN (optional) → Fertig (QR-Aufkleber, louie.local).

## 6. Spielmodi

### 6.1 Ein Modus besteht aus vier Schichten

| Schicht | Inhalt | Beispiel |
|---|---|---|
| **A Flugprofil** | Folge von Abschnitten: `const`, `ramp`, `steps`, `random`, `wave` | Druckkochtopf: Rampe 40 → 100 % in 120 s |
| **B Würze** | Ereignisse: Ruckler, Fake-out-Bremse, Pause, Schleichfahrt + Sprint, kurzer Rückwärtsstoß; Häufigkeit/min, Dauer, Vorwarnung | Turbulenzen |
| **C Mitspieler-Aktionen** | Rückspuler, Boost, Bremse; `who` = alle / Verbleibende / Ausgeschiedene; Kontingent, Abklingzeit, globale Sperre | Rückspul-Duell |
| **D Rundenende** | Hebel (immer), Zeit, letzter Spieler | Zeitrennen 90 s |

- **Jeder Modus muss ohne Schicht C spielbar sein.** Der Handy-Bedarf wird aus den Schichten abgeleitet.
- **Fiesheit 1–5**: Der Modus legt Stufe 3 fest. Eine feste Tabelle skaliert Tempo, Ereignishäufigkeit
  und Abklingzeiten. Stufe 1 hat nie Rückwärts und keine Fake-outs.
- **Klemmkette** in fester Reihenfolge, jede Stufe kann nur verschärfen: Modus → Fiesheit →
  „diese Runde“ → Tempo-Deckel des Profils → Besitzer-Grenzen → Motorschicht. Die Vorschau zeigt
  die **geklemmte** Kurve. Der Server berechnet sie mit demselben Interpreter (`POST /api/modes/preview`).

```json
{
  "id": "turbulenz", "v": 1, "name": "Turbulenzen", "icon": "🌪️", "owner": "builtin",
  "profile": [{"type": "random", "min": 35, "max": 80, "every_s": [3, 6], "for_s": null}],
  "spice":   [{"kind": "jolt", "per_min": 4, "dur_s": 0.4, "warn_s": 0.5, "from_s": 10},
              {"kind": "fakeout", "per_min": 2, "dur_s": 1.0}],
  "actions": [],
  "end":     {"type": "lever"}
}
```

### 6.2 Eingebaute Modi

| Modus | Idee | Handys |
|---|---|---|
| ✈️ **Klassisch** | konstantes Tempo, sanfter Anlauf (auch Standard als Hebel-Modus) | 0 |
| 🔥 **Druckkochtopf** | wird stetig schneller, Runden enden von selbst | 0 |
| 🎲 **Würfelmotor** | zufälliges Tempo in zufälligen Abständen | 0 |
| 🌪️ **Turbulenzen** | Würfelmotor plus Ruckler und Fake-out-Bremsen | 0 |
| ⏪ **Rückspul-Duell** | Klassisch plus Rückspuler-Joker für alle | je Spieler |
| 👻 **Letztes Huhn** | Druckkochtopf, Ausgeschiedene bekommen Geister-Boost (Geister-Joker nur mit „Statistik & Ausscheiden“) | je Spieler |

Modi, die Mitspieler-Handys brauchen, sind ohne Mitspieler-Handys wählbar, laufen dann aber ohne
Schicht C. Die Karte zeigt das mit „Mitspieler-Aktionen aus – Handys einschalten?“.

### 6.3 Drei Tiefen der Bedienung

1. **Schnellwahl** (V1, Spielleiter): Karte antippen, Fiesheit wählen.
2. **Anpassen** (V1, Spielleiter): 1–3 Regler je Schicht (Tempo, Joker, Zeitlimit),
   „für diese Runde“. Speichern erst ab Stufe 2 und nur, wenn es erlaubt ist.
3. **Modus-Baukasten** (Spielleiter, wenn „Modi erstellen“ erlaubt): eigene Modi aus Vorlagen und Bausteinen, siehe [modus-baukasten.md](modus-baukasten.md).

### 6.4 Lebenszyklus

Eingebaut (schreibgeschützt) → kopieren → anpassen → speichern (`owner`, `based_on`) → teilen
als JSON-Datei oder QR-Link `http://louie.local/#m=<base64url>`. Beim Import zeigt eine Vorschau,
wo geklemmt wird. Ein Import kann keine Grenzen aufweichen.

## 7. Werkstatt (Testmodus, nur Besitzer)

Die Werkstatt ist optisch deutlich markiert (gestreifter Rand), und auch hier gelten alle Grenzen.

**Hebel im Testbetrieb**: Normalerweise startet Hebel an sofort eine Runde. Solange die Werkstatt
offen ist oder eine Probefahrt vorbereitet wird, ist das Gerät im **Testbetrieb**: Hebel an gibt
nur den Motor frei, es startet keine Runde. Ablauf der Probefahrt: „Probefahrt“ tippen → Hebel an →
Knopf halten. Die Bereitschaft verfällt nach 60 s. Endet der Test bei Hebel an, folgt
„Hebel erst auf Aus“ (kein Überraschungsstart).

- **Trocken** (Motor fest auf 0, auch bei Hebel aus): Modus abspielen mit 0,5× / 1× / 4× / 16×,
  festem Zufalls-Seed, Kurve „Soll“ und „geklemmt“, simulierten Mitspielern (Spam / klug / nie)
  und Kennzahlen (Rückwärtsanteil, geschätzte Rundendauer, Ereignisse pro Minute).
- **Echt** (Hebel an, keine Runde, Akku ok): **Totmannknopf**. Der Motor läuft nur, solange der
  Knopf gehalten wird (Herzschlag 200 ms, Stopp nach 500 ms ohne Herzschlag). Nur 0,5× oder 1×,
  höchstens 60 s. Ereignisse lassen sich von Hand auslösen („Ruckler jetzt“, „Rückspuler jetzt“).
  Abgelehnte Auslöser nennen den Grund („Rückwärts-Sperre noch 4 s“).
- **Kalibrierung**: Drehrichtung, Mindesttempo (= 0 %), Fliehkraft-Grenze (= 100 %), Spürbarkeit der Ruckler,
  Leerlaufstrom (Basis der Blockier-Erkennung).

## 8. Folgen für Protokoll und Konzept

- WebSocket zusätzlich: `request_lead`, `handover`, `release_lead`, `request_join`, `allow_players`,
  `kick`, `leader_plays`, `chick_lost`, `estop`; Zustand: `multiplayer`, `leader_plays`, `lead_policy`.
- Rechte zusätzlich: `modes.select`, `modes.tweak`, `workshop.dry`, `workshop.motor`.
- Admin-Timeout 5 min statt 30 min. „Gast“ heißt jetzt „Zuschauer“.
- Neue Einstellung **Hebel-Modus** (Modus ohne Handy), unabhängig vom zuletzt gewählten Modus.

## 9. Offene Punkte

- [ ] Spürt man 0,3-s-Ruckler? (Prototyp)
- [ ] Hebel-Geste 3× umlegen: in der Praxis zuverlässig erkennbar? Status-LED soll das Fenster zusätzlich anzeigen.
- [ ] „Wer darf steuern“: Ist „jeder“ als Standard für Partys sicher genug?
- [x] Hühner zählen: entfällt. Ausscheiden und Statistik sind optional (Standard aus).
