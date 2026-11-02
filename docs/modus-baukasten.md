# Modus-Baukasten: eigene Spielmodi erstellen

Stand: 2026-11-01 · Status: Vorschlag, ergänzt [web-ui-konzept.md](web-ui-konzept.md) Abschnitt 6 (Spielmodi)
und 7 (Werkstatt). Erweitert das Vier-Schichten-Modell (Flugplan, Würze, Joker, Ende) um Sägezahn,
Rückwärts-Tempo im Flugplan, mehrere Joker-Arten, Joker-Konten und eine Fiesheits-Tabelle.

**Ziel:** Der Spielleiter baut auf dem Handy in unter 2 Minuten einen eigenen Modus. Einfaches bleibt
einfach (3 Tipps), Komplexes geht trotzdem (Sägezahn mit ⏩/⏪-Joker, Geister-Joker, Fiesheits-Tabelle).
Grundsatz: **Jede Zahl hat einen guten Vorgabewert. Man sieht nur, was man ändern will.**

## 1. Begriffe und Tempo-Skala

| Begriff im UI | Bedeutung |
|---|---|
| **Flugplan** | Wie schnell Louie über die Zeit fliegt (Schicht A) |
| **Würze** | Zufällige Überraschungen vom Gerät (Schicht B) |
| **Joker** | Knöpfe der Spieler auf ihrem Handy (Schicht C) |
| **Ende** | Wann die Runde von selbst endet (Schicht D, Hebel beendet immer) |
| **Fiesheit 1–5** | Schwierigkeit, 🐣 Kindergeburtstag bis 👹 Endgegner |

**Tempo** reicht von **−100 % bis +100 %**:

```
 −100 %        −0 | 0 %                          100 %
 ◄── rückwärts ───┤├── vorwärts ───────────────────►
                   Mindesttempo        Fliehkraft-Grenze
                   (dreht zuverlässig) (darüber unspielbar)
```

- 0 % heißt **Mindesttempo**, nicht Stillstand. Stillstand ist der Abschnitt **Pause** (Motor aus).
- Zwischen „0 %“ und „−0 %“ gibt es nichts. Beim Vorzeichenwechsel hält die Motorschicht kurz an
  (Totzeit) und startet in der anderen Richtung beim Mindesttempo. Die Vorschau zeigt das als kleine Lücke.
- Rückwärts ist im Flugplan, in der Würze und bei Jokern möglich. Die Besitzer-Grenzen (z. B. höchstens
  1,5 s am Stück, höchstens 10 % Anteil, Rückwärts-Tempo höchstens −50 %) gelten immer.

## 2. Datenmodell (Schema 2)

### 2.1 Gesamtaufbau

Die JSON-Blöcke in Abschnitt 2 sind Skizzen (`...` und `//`-Kommentare nur zur Erklärung); vollständige
Beispiele stehen in Abschnitt 5 und 6.

```json
{
  "schema": 2, "id": "saegezahn-duell", "name": "Sägezahn-Duell", "icon": "🪚",
  "desc": "Louie wird immer schneller und fällt zurück. Ihr schubst mit ⏩ und ⏪.",
  "owner": "lena", "based_on": "saegezahn@1", "fies_default": 3, "handicap": true,
  "flight": { "segments": [ ... ], "after": "loop" },
  "spice":  [ ... ],
  "jokers": { "account": "separate", "lock_s": 5, "items": [ ... ] },
  "end":    { "time_s": null, "last_player": false, "plan_end": false },
  "seed": null
}
```

Abgeleitet (nicht im JSON): `needs.phones` (es gibt Joker), `needs.out_report` (ein Joker mit
`who: "alive"/"out"` oder `end.last_player`). Nur dann erscheint auf den Gamepads „Ich bin raus“.

Gegenüber Schema 1 (PoC) ist `profile` jetzt `flight.segments`, `actions` heißt `jokers.items`, und `end` ist flach
statt `any/of`. Der Server hebt Schema 1 beim Laden automatisch an.

### 2.2 Zahl oder Tabelle: die Fiesheits-Regel

**Jede Zahl im Modus ist der Wert für Fiesheit 3.** Sie wird automatisch skaliert. Wer es genau
will, schreibt statt der Zahl eine **Liste mit 5 Werten** (Stufe 1–5); dann wird nichts skaliert.

```json
"count": 2                  // automatisch (Anzahl bleibt bei allen Stufen 2)
"count": [4, 3, 2, 2, 1]    // Tabelle: Kinder 4 Joker, Endgegner 1 Joker
```

Automatische Skalierung (fest in der Firmware, entspricht dem PoC):

| Feld-Art | 🐣 1 | 😊 2 | 😏 3 | 😈 4 | 👹 5 |
|---|---|---|---|---|---|
| Tempo vorwärts (alle `v`, `from`, `to`, `min`, `max`) | ×0,7 | ×0,85 | ×1 | ×1,1 | ×1,2 |
| Tempo rückwärts | **wird 0 %** | ×0,85 | ×1 | ×1,1 | ×1,2 |
| Würze-Häufigkeit (`per_min`) | ×0 | ×0,5 | ×1 | ×1,5 | ×2 |
| Joker-Stärke (`strength`) | ×0,7 | ×0,85 | ×1 | ×1,1 | ×1,2 |
| Abklingzeit, Sperre (`cooldown_s`, `lock_s`) | ×1,6 | ×1,3 | ×1 | ×0,8 | ×0,65 |
| Joker-Anzahl, Dauern, Zeitlimit | = | = | = | = | = |
| Joker ⏪ Rückwärts-Stoß | **wird 🛑 Bremse** | | | | |

Begründung: Die **Anzahl** der Joker bleibt gleich, damit „du hast 3 Joker“ verlässlich bleibt und
Kinder nicht weniger Spaß haben. Fieser wird es über Stärke, kürzere Abklingzeit und mehr Würze.
Auf Stufe 1 gibt es nie Rückwärts. Ein ⏪-Joker wird dort zur Bremse, so bleibt der Knopf erhalten.

### 2.3 Flugplan-Abschnitte

Jeder Abschnitt hat eine Dauer (`for_s` oder sie ergibt sich aus den Parametern) und optional `repeat`
(Anzahl, Standard 1). `after` am Planende: `"loop"` (von vorn), `"hold"` (letztes Tempo halten)
oder `"end"` (Runde endet, nur zusammen mit `end.plan_end`).

| Typ | Symbol | Parameter (Vorgabe) | Mehr Optionen |
|---|---|---|---|
| `const` Konstant | ▬ | `v` 55, `for_s` 30 | – |
| `ramp` Rampe | ⟋ | `from` 30, `to` 80, `over_s` 60 | `curve` lin/exp |
| `steps` Stufen | ▁▃▅ | `from` 30, `to` 90, `n` 4, `step_s` 15 | absteigend |
| `saw` **Sägezahn** | ⩘ | `from` 25, `to` 85, `rise_s` 10, `drop` hart, `repeat` 6 | `drop_s` (weich), `kick` Rücksprung-Stoß, `dir` steigend/fallend, `curve` |
| `wave` Welle | ∿ | `min` 35, `max` 75, `period_s` 20, `repeat` 3 | `shape` Sinus/Herzschlag |
| `random` Zufall | 🎲 | `min` 30, `max` 85, `every_s` [2,6], `for_s` 60 | `fair` (kein Sprung > 40 Punkte) |
| `pause` Pause | ⏸ | `for_s` 3 | `warn_s` Vorwarnung |

Sägezahn im Detail: Louie steigt in `rise_s` von `from` auf `to` und springt dann zurück, **hart**
(so schnell, wie die Motorschicht erlaubt) oder **weich** (über `drop_s`). Optional zeigt der `kick`
beim Rücksprung einen kurzen Rückwärts-Stoß (`{"v": -30, "s": 0.6}`). Mit `dir: "down"` fällt das
Tempo langsam und springt hoch („umgekehrter Sägezahn“).

### 2.4 Würze-Ereignisse

```json
{ "kind": "fakeout", "per_min": 2, "strength": 0, "dur_s": 1.0, "warn_s": 0, "from_s": 20 }
```

| `kind` | UI | Wirkung |
|---|---|---|
| `jolt` | ⚡ Ruckler | kurzer Rückwärts-Zucker (0,3–0,5 s) |
| `fakeout` | 🎭 Schein-Bremse | auf 0 % (Mindesttempo), dann sofort wieder hoch |
| `reverse` | ⏪ Rückwärts-Stoß | `strength` −35 für `dur_s` 0,8 |
| `sprint` | 🚀 Sprint | auf `strength` 95 für `dur_s` 2 |
| `creep_sprint` | 🐌 Schleichen + Sprint | 0 % für 4 s, dann Sprint |
| `stall` | ⏸ Luftloch | Motor kurz aus |

Häufigkeit im UI: **selten / manchmal / oft** (0,5 / 1,5 / 3 pro Minute), genauer unter „Mehr Optionen“.

### 2.5 Joker

```json
"jokers": {
  "account": "separate",          // "separate": Konto je Art · "shared": ein Konto für alle Arten
  "shared_count": 3,              // nur bei "shared"
  "lock_s": 5,                    // gemeinsame Sperre: nach jedem Joker (egal wer) x s Ruhe für alle
  "items": [
    { "kind": "boost",  "who": "alive", "count": 2, "strength": 25, "dur_s": 2.0,
      "cooldown_s": 10, "hold_ms": 400, "from_s": 5 },
    { "kind": "rewind", "who": "alive", "count": 1, "strength": 35, "dur_s": 0.8,
      "cooldown_s": 20, "hold_ms": 400, "max": null }
  ]
}
```

| `kind` | UI | `strength` bedeutet | Vorgabe |
|---|---|---|---|
| `boost` | ⏩ Vorwärts-Boost | + Prozentpunkte | +25 für 2 s |
| `rewind` | ⏪ Rückwärts-Stoß | Rückwärts-Tempo | −35 für 0,8 s (≤ 1,5 s) |
| `brake` | 🛑 Bremse | − Prozentpunkte, nie unter 0 % | −40 für 1,5 s |
| `fakeout` | 🎭 Schein-Bremse | Sprint danach (+ Punkte) | 0,6 s Bremse, dann +20 für 1 s |

- `who`: `all` (alle), `alive` (nur Aktive), `out` (nur Ausgeschiedene = Geister 👻).
- `cooldown_s` gilt **pro Spieler**. Bei `separate` je Art, bei `shared` für den ganzen Spieler
  (Regel: *die Abklingzeit folgt dem Konto*).
- `max` (nur bei `shared`): höchstens so viele dieser Art aus dem gemeinsamen Konto, z. B. „3 Joker, davon
  höchstens 1× ⏪“.
- Spielt der Spielleiter mit („steuern + mitspielen“), bekommt er dieselben Joker wie alle.

**Begrenzung: höchstens 2 Joker-Arten pro Spielerzustand, höchstens 3 pro Modus.** Ein Spieler sieht also nie
mehr als zwei Knöpfe gleichzeitig (Aktive z. B. ⏩ + ⏪, Geister z. B. 👻 Böe). Begründung: Das Handy liegt auf dem
Tisch, eine Hand ist an der Wippe, der Blick ist bei Louie. Zwei Bildschirmhälften trifft man blind und lernt sie in
einer Runde. Drei Ziele brauchen einen Blick aufs Handy, und genau dann verliert man ein Huhn. Mehr Arten würden
außerdem die Abklingringe und Punkte zu klein machen.

### 2.6 Rundenende

```json
"end": { "time_s": 120, "last_player": true, "plan_end": false }
```

Der Hebel beendet immer und steht deshalb nicht im JSON. Es gilt, was zuerst eintritt. `last_player` und Geister-Joker
(`who: "out"`) wirken nur, wenn die Einstellung „📊 Statistik & Ausscheiden“ an ist (Standard aus). Sonst fallen
sie still weg, und die Modus-Karte weist dezent darauf hin.

### 2.7 Vorteil pro Spieler (Handicap)

**Lohnt sich, aber klein halten (V1.1).** Der Vorteil gehört nicht in den Modus, sondern zur Runde: In der
Spieler-Zeile tippt der Leiter einen Mitspieler an → **Vorteil: normal / +1 Joker / +2 Joker** (bei getrennten Konten +1 je
Art, bei gemeinsamem Konto +1 im Konto). Er gilt für den Abend und hängt am Mitspieler. Nur positive Vorteile
(„Bonus für Lena“) statt Strafen für Erwachsene, das fühlt sich am Familientisch besser an. Ein Modus kann
das mit `"handicap": false` abschalten (z. B. für Turnier-Modi). Die Fiesheit gilt weiter für alle gleich.

### 2.8 Grenzen und Validierung

Je Modus höchstens 8 Abschnitte, 6 Würze-Ereignisse, 3 Joker-Arten, 2 KB und 30 eigene Modi. Der Editor prüft
**während der Eingabe** mit demselben Interpreter wie der Server (`POST /api/modes/preview`) und meldet freundlich:

| Lage | Hinweis (gelb = wird angepasst, rot = kann nicht gespeichert werden) |
|---|---|
| Rückwärtsanteil über Grenze | 🟡 „Rückwärtsanteil 18 % – wird auf 10 % begrenzt. [Rücksprung-Stoß statt negativem Start]“ |
| Rückwärts zu lang am Stück | 🟡 „2,0 s rückwärts am Stück – erlaubt 1,5 s, Louie hält danach an.“ |
| Boost über die Grenze | 🟡 „⏩ wirkt ab 75 % nur teilweise (über 100 % fliegt Louie zu hoch).“ |
| Tempo-Deckel des Profils | 🟡 „Im Profil Familie höchstens 80 % – die Spitzen werden gekappt.“ |
| Joker für Geister, aber kein Ausscheiden | 🟢 „Spieler melden sich mit ‚Ich bin raus‘. Wird automatisch eingeschaltet.“ |
| Dritte Joker-Art für Aktive | 🔴 „Höchstens 2 Joker-Knöpfe gleichzeitig. Tipp: gemeinsames Konto.“ |
| Plan endet nie und kein Ende | 🟢 „Runde endet nur mit dem Hebel – so gewollt?“ |
| Abschnitt ohne Dauer mitten im Plan | 🔴 „‚Zufall‘ läuft endlos, die Abschnitte danach kommen nie. Dauer setzen?“ |

Gelbe Hinweise blockieren nicht, sie erklären die geklemmte Kurve. Jeder Hinweis hat, wo möglich, einen
Ein-Tipp-Vorschlag in eckigen Klammern.

## 3. Gamepad mit mehreren Jokern

Der Halte-Knopf aus dem PoC bleibt das Grundelement: halten (400 ms, Füllring) löst aus, Wegrutschen bricht
ab. Punkte zeigen den Rest, ein grauer Ring die Abklingzeit, ein Schloss-Symbol die gemeinsame Sperre.

**1 Joker:** ein großer Knopf, wie im PoC.

**2 Joker, Empfehlung: nebeneinander, ⏪ links, ⏩ rechts.** Jede Hälfte ist ein ganzer Halte-Knopf
(ca. 170 × 380 px) mit eigenen Punkten und eigenem Abklingring.

```
┌───────────────────────────────────────┐
│ 🔵 Lena          ✈️ 62 %      ☰       │
├───────────────────┬───────────────────┤
│                   │                   │
│                   │                   │
│        ⏪         │        ⏩         │
│     ZURÜCK        │      SCHUB        │
│                   │                   │
│      ●○           │      ●●○          │
│   (Ring 12 s)     │                   │
│                   │                   │
├───────────────────┴───────────────────┤
│  🔒 Sperre 3 s        Ich bin raus ⏻  │
└───────────────────────────────────────┘
```

Begründung:
- **Richtung wie bei der Fernbedienung**: ⏪ links, ⏩ rechts kennt jedes Kind vom Video. Die Handykante dient als
  Tast-Anker, blind trifft man „linke Hälfte / rechte Hälfte“ sicherer als „oben / unten“, denn das liegende Handy
  ist von der Tischkante aus schräg und die obere Hälfte weiter weg.
- Zwei Farben (⏪ rot, ⏩ grün) und verschiedene Vibrationsmuster (1× bzw. 2× kurz, wo das Handy es kann).
- Beide gleichzeitig halten löst nichts aus.
- Verworfen: **ein Knopf plus Umschalter**. Man muss hinschauen, welcher Zustand gilt, braucht zwei Handlungen,
  und Kinder lösen den falschen aus. Übereinander geht auch, ist aber die schwächere Wahl (siehe oben).

**Gemeinsames Konto** (z. B. „3 Joker, frei als ⏩ oder ⏪“): gleiches Layout, aber die Punkte stehen **einmal
mittig** zwischen den Knöpfen, und die Abklingzeit graut beide Hälften. So sieht man sofort, dass es ein Topf ist.

```
├───────────────────┬───────────────────┤
│        ⏪         │        ⏩         │
│                 ●●●○                  │
│     ZURÜCK        │      SCHUB        │
├───────────────────┴───────────────────┤
```

Beides ist pro Modus wählbar (`account`). Getrennt ist strategisch klarer („einen ⏪ habe ich noch“), gemeinsam
gibt mehr Freiheit. Vorlage: getrennt.

**3 Joker:** gleichzeitig nicht erlaubt (2.5). Drei Arten gibt es nur verteilt auf Zustände, z. B. ⏩ + ⏪ für
Aktive und 👻 für Geister. Nach „Ich bin raus“ wechselt das Gamepad auf das Geister-Layout (1 oder 2 Knöpfe,
violett, 👻 im Kopf). Spätere Ausbaustufe, falls nötig: Hauptknopf oben über die ganze Breite plus zwei halbe unten.

**Steuerhandy mit „mitspielen“:** gleiches Gamepad, oben eine schmale Leiterleiste (⏸ Pause, ⏹ Stopp, ☰).

## 4. Editor-UI

### 4.1 Wege hinein

`Modi` → **„+ Eigener Modus“** (Galerie) oder auf einer Modus-Karte **„Kopieren & ändern“**. Eingebaute Modi
bleiben schreibgeschützt, man bearbeitet immer eine Kopie (Entwurf, wird automatisch im Browser gehalten).

### 4.2 Stufe a: Vorlagen-Galerie (E1)

```
┌───────────────────────────────────────┐
│ ←  Neuer Modus                        │
│ Womit fangen wir an?                  │
│ ┌────────────┐ ┌────────────┐         │
│ │ ✈️ ▬▬▬▬     │ │ 🔥 ⟋        │         │
│ │ Klassisch  │ │ Druckkoch- │         │
│ │            │ │ topf       │         │
│ └────────────┘ └────────────┘         │
│ ┌────────────┐ ┌────────────┐         │
│ │ 🪚 ⩘⩘⩘     │ │ 🌊 ∿∿       │         │
│ │ Sägezahn   │ │ Welle      │         │
│ └────────────┘ └────────────┘         │
│ ┌────────────┐ ┌────────────┐         │
│ │ ⏪ ▬ 📱     │ │ 👻 ⟋ 📱     │         │
│ │ Rückspul-  │ │ Geister-   │         │
│ │ Duell      │ │ stunde     │         │
│ └────────────┘ └────────────┘         │
│ ┌────────────────────────────┐        │
│ │ ➕ Leer anfangen            │        │
│ └────────────────────────────┘        │
└───────────────────────────────────────┘
```

Jede Kachel zeigt Mini-Kurve und 📱, falls Joker drin sind. Antippen öffnet sofort den Baukasten.

### 4.3 Stufe b: Baukasten-Übersicht (E2)

```
┌───────────────────────────────────────┐
│ ←  🪚 Sägezahn (Kopie)        Fertig  │
├───────────────────────────────────────┤
│ 100┤   /|   /|   /|   /|              │
│    │  / |  / |  / |  / |   ⏩ ⏪ ⚡     │
│  0 ┼─/──|─/──|─/──|─/──|──────────    │
│-50 ┤    ▼    ▼    ▼      0:00 – 2:00  │
│ Fiesheit  🐣  😊 [😏] 😈  👹          │
├───────────────────────────────────────┤
│ ✈️ Flugplan                         › │
│    Sägezahn 25→85 %, 10 s, 6× · Loop  │
├───────────────────────────────────────┤
│ 🌶️ Würze                            › │
│    ⚡ Ruckler manchmal                 │
├───────────────────────────────────────┤
│ 🃏 Joker                            › │
│    Alle: ⏩ 2× · ⏪ 1× (getrennt)       │
├───────────────────────────────────────┤
│ 🏁 Ende                             › │
│    Hebel · nach 2:00                  │
├───────────────────────────────────────┤
│  🟡 Rückwärtsanteil 12 % → 10 %       │
├───────────────────────────────────────┤
│ [ ▶ Trocken ]  [ 🔧 Probe ] [Speichern]│
└───────────────────────────────────────┘
```

- **Vorschau oben bleibt stehen** (ca. 130 px) auf allen Bearbeitungsseiten. Sie zeigt die **geklemmte Kurve**
  (durchgezogen), die Soll-Kurve nur dort, wo geklemmt wird (gestrichelt), Rückwärts rot unter der Nulllinie,
  Würze als kleine Symbole oben, ▼ für Rücksprung-Stöße. Joker-Marker kommen aus einer Bot-Probe
  („3 Bots, klug“), Schalter „Joker zeigen“.
- **Fiesheits-Schalter** unter der Kurve ändert nur die Vorschau und alle angezeigten Werte (nicht den Modus).
- Einfache Pläne (ein Abschnitt) zeigen auf der Flugplan-Karte direkt einen **Schnellregler „Tempo“**.
- Hinweise erscheinen als eine Zeile, Antippen zeigt alle.

### 4.4 Flugplan-Editor (E3)

```
┌───────────────────────────────────────┐
│ ←  Flugplan             [Vorschau ▲]  │
├───────────────────────────────────────┤
│ ┌───────────────────────────────────┐ │
│ │ 1 ⟋ Anlauf  0→40 % in 4 s   ⋯     │ │
│ └───────────────────────────────────┘ │
│ ┌───────────────────────────────────┐ │
│ │ 2 ⩘ Sägezahn  25→85 %  ⩘⩘⩘  ⋯     │ │
│ │   10 s, hart, 6×   (1:00)         │ │
│ └───────────────────────────────────┘ │
│       [ ➕ Abschnitt hinzufügen ]       │
│                                       │
│ Danach:  ( Von vorn ) ( Halten ) (Ende)│
└───────────────────────────────────────┘
```

- Jede Abschnitt-Karte hat Nummer, Symbol, Kurzbeschreibung, Mini-Kurve und Dauer. Antippen → Abschnitt bearbeiten.
- **⋯-Menü**: ↑ Nach oben · ↓ Nach unten · Kopieren · Löschen (mit „Rückgängig“-Toast oben). Kein Ziehen, keine
  Wischgesten (siehe Web-UI-Konzept 3).
- **Hinzufügen** öffnet eine Seite mit 7 großen Kacheln (▬ Konstant, ⟋ Rampe, ▁▃▅ Stufen, ⩘ Sägezahn, ∿ Welle,
  🎲 Zufall, ⏸ Pause). Der neue Abschnitt kommt ans Ende und beginnt beim Endtempo des vorigen.

**Abschnitt bearbeiten: Sägezahn (E3b)**

```
┌───────────────────────────────────────┐
│ ←  ⩘ Sägezahn              Abschnitt 2│
├───────────────────────────────────────┤
│ [ Vorschau, Abschnitt hervorgehoben ] │
├───────────────────────────────────────┤
│ Von         ◄───●───────────►   25 %  │
│ Bis         ◄─────────●─────►   85 %  │
│ Anstieg     [ − ]   10 s   [ + ]      │
│ Rücksprung  ( Hart )  ( Weich )       │
│ Wiederholen [ − ]    6×    [ + ]  [∞] │
├───────────────────────────────────────┤
│ ▸ Mehr Optionen                       │
│   Richtung    ( steigend ) ( fallend )│
│   Rücksprung-Stoß  [ an ]  −30 % 0,6 s│
│   Weich über  1,5 s                   │
│   Anstiegs-Form  ( gerade ) ( spät )  │
│   🎚 Nach Fiesheit unterschiedlich    │
└───────────────────────────────────────┘
```

Tempo-Regler: Mitte = 0 %, links rot = rückwärts (bis zur Besitzer-Grenze), Beschriftung „Mindesttempo“ bei 0 und
„Grenze“ bei 100. Zahlen per Tipp auf den Wert auch direkt eintippbar. Stepper statt Regler für Zeiten und
Anzahlen (präziser mit dem Daumen).

### 4.5 Würze, Joker, Ende (E4–E6)

**Würze:** Liste der Ereignisse wie im Flugplan. Pro Ereignis: **Häufigkeit** (selten / manchmal / oft),
**ab Minute**, bei Stößen **Stärke**. Mehr Optionen: Dauer, Vorwarnung auf den Handys, genaue Rate pro Minute.

**Joker (E5):**

```
┌───────────────────────────────────────┐
│ ←  Joker                              │
├───────────────────────────────────────┤
│ 🙂 ALLE SPIELER                       │
│ ┌──────────────┐ ┌──────────────┐     │
│ │ ⏩ Schub   ⋯ │ │ ⏪ Zurück  ⋯ │     │
│ │ [−]  2×  [+] │ │ [−]  1×  [+] │     │
│ └──────────────┘ └──────────────┘     │
│ Konto  ( je Art )  ( gemeinsam )      │
├───────────────────────────────────────┤
│ 👻 AUSGESCHIEDENE (Geister)           │
│        [ ➕ Geister-Joker ]            │
├───────────────────────────────────────┤
│ ▸ Mehr Optionen                       │
│   Gemeinsame Sperre      5 s          │
│   Vorteil pro Spieler erlaubt  [an]   │
│   🎚 Anzahl nach Fiesheit             │
└───────────────────────────────────────┘
```

- Die obere Gruppe heißt „Alle Spieler“ (`who: "all"`). Sobald es Geister-Joker gibt, fragt der Editor
  einmal: „Sollen Ausgeschiedene ihre ⏩/⏪ behalten?“ Nein → Gruppe heißt „Aktive“ (`who: "alive"`).
- Hinzufügen zeigt nur die erlaubten Arten (⏩ ⏪ 🛑 🎭). Ist ein Zustand voll (2 Arten), ist der Knopf grau
  mit Erklärung.
- Joker-Kachel antippen (⋯) → **Joker-Seite**: Stärke (schwach / mittel / stark), Anzahl. Mehr Optionen:
  Dauer, Abklingzeit, Halten (ms), erst ab Sekunde, „wer darf“ (alle / Aktive / Geister).
- Bei „gemeinsam“ wird aus den zwei Steppern ein Stepper **„Joker pro Spieler“** plus je Art optional „höchstens“.

**Anzahl nach Fiesheit** (öffnet die 5er-Zeile, vorbefüllt mit den automatischen Werten):

```
│ Anzahl ⏩    🐣  😊  😏  😈  👹        │
│             [3] [3] [2] [2] [1]       │
│ Anzahl ⏪    [0] [1] [1] [1] [1]       │
│             ↺ automatisch             │
```

Sobald ein Feld abweicht, speichert der Modus eine Liste (2.2). „↺ automatisch“ macht wieder eine Zahl daraus.

**Ende (E6):** „Hebel aus“ (immer, ausgegraut), **Zeitlimit** (aus / 1 / 2 / 3 / 5 min / eigene),
**Wenn nur noch einer übrig ist** (Schalter, Hinweis: „Spieler melden sich mit ‚Ich bin raus‘“),
**Wenn der Flugplan zu Ende ist** (nur wählbar bei „Danach: Ende“).

### 4.6 Ausprobieren

| Knopf | Was | Wer |
|---|---|---|
| **▶ Trocken abspielen** | Motor bleibt aus. Kurve läuft live mit 1× / 4× / 16×, Zufalls-Seed fest oder 🎲. 2–4 Bots mit Strategie (sofort / klug / spart / nie), Knöpfe „Bot 2 ist raus“, „Bot 3: ⏪ jetzt“. Danach Kennzahlen: Ø-Tempo, Rückwärtsanteil, Joker-Einsätze/min, wegen Sperre abgelehnt, Zeit an der 100-%-Grenze | jeder mit Editor-Recht |
| **🔧 Probefahrt echt** | Werkstatt-Regeln: Hebel an startet keine Runde, **Totmannknopf** (Motor nur solange gehalten), 1× oder 0,5×. Spielleiter: höchstens 10 s, ab Sekunde x wählbar (z. B. „ab dem 1. Rücksprung“). Besitzer: bis 60 s und Joker von Hand („⏪ jetzt“) | Leiter 10 s, Besitzer voll |

### 4.7 Speichern (E7)

Name (Vorschlag aus Vorlage), **Symbol** (Raster mit 24 Emojis), **ein Satz** Beschreibung (max. 80 Zeichen,
erscheint auf der Modus-Karte), **Standard-Fiesheit**. Darunter zwei Knöpfe: **„Nur diese Runde spielen“**
(Entwurf, ohne Speicherrecht) und **„Speichern“**. Gespeicherte Modi erscheinen in `Modi` mit Kennzeichen „eigener“.

### 4.8 Stufe c: Profi

Unter `Fertig ▾ → Profi`: **Fiesheits-Tabelle** für alle Zahlen des Modus auf einer Seite (Zeilen = Felder,
Spalten = 🐣…👹, automatische Werte grau, eigene schwarz), **JSON anzeigen** (formatiert, „Kopieren“),
**Export** als Datei und als QR-Link `http://louie.local/#m=<base64url>`, **Import** (Einfügen oder Datei), immer mit
Vorschau und Hinweisen, wo geklemmt wird.

## 5. Durchgespielt: „Sägezahn mit ⏩/⏪-Joker“

Ziel: Louie steigt alle 10 s von 25 auf 85 % und fällt mit einem kleinen Rückwärts-Zucker zurück. Jeder Spieler
hat 2× Schub und 1× Zurück. Runde endet nach 2 min.

| # | Bildschirm | Tipp | Ergebnis |
|---|---|---|---|
| 1 | Modi | „+ Eigener Modus“ | Galerie E1 |
| 2 | E1 | 🪚 Sägezahn | Übersicht E2 mit Anlauf + Sägezahn 30→80 %, 12 s, 6×, Loop, keine Joker |
| 3 | E2 | Flugplan-Karte | E3 |
| 4 | E3 | Karte 2 (Sägezahn) | E3b |
| 5 | E3b | Von auf 25, Bis auf 85, Anstieg auf 10 s | Kurve oben aktualisiert sich sofort |
| 6 | E3b | Mehr Optionen → Rücksprung-Stoß an (−30 %, 0,6 s) | ▼-Marker in der Kurve, Zeile „Rückwärtsanteil 5 %“ grün |
| 7 | E3b | (Versuch) Von auf −20 % | 🟡 „Rückwärtsanteil 20 % – wird auf 10 % begrenzt. 2,0 s am Stück – erlaubt 1,5 s. [Von 25 % + Rücksprung-Stoß]“ → Vorschlag antippen, zurück auf 25 % |
| 8 | E3b → E2 | ← | Flugplan-Karte: „Sägezahn 25→85 %, 10 s, 6× · Loop“ |
| 9 | E2 | Joker-Karte | E5, leer |
| 10 | E5 | Alle Spieler: ➕ → ⏩ Schub | Kachel ⏩ 2× (Vorgabe) |
| 11 | E5 | Alle Spieler: ➕ → ⏪ Zurück | Kachel ⏪ 1× (Vorgabe), Konto „je Art“ bleibt |
| 12 | E5 | Mehr Optionen → Gemeinsame Sperre 5 s | – |
| 13 | E5 | 🎚 Anzahl nach Fiesheit → ⏩ bei 🐣 auf 3 | 🟡 bei Vorschau-Fiesheit 🐣: „⏪ wird auf Stufe 1 zur 🛑 Bremse“ |
| 14 | E2 | Ende-Karte → Zeitlimit 2 min | Karte „Hebel · nach 2:00“ |
| 15 | E2 | 🟡 „⏩ wirkt ab 75 % nur teilweise“ – zur Kenntnis | bleibt gelb, kein Hindernis |
| 16 | E2 | ▶ Trocken, 4×, 3 Bots „klug“ | Joker-Marker in der Kurve, Kennzahlen: Rückwärtsanteil 7 %, 0 abgelehnt |
| 17 | E2 | 🔧 Probe (Hebel an, Knopf halten, ab 0:08) | 10 s echt: spürt man den Zucker? |
| 18 | E7 | Speichern: „Sägezahn-Duell“, 🪚, „Immer schneller, dann Zucker. ⏩ und ⏪ für alle.“ | Modus in der Liste, sofort wählbar |

Gamepad der Spieler: Layout „2 Joker nebeneinander“ (Abschnitt 3), ⏪ mit ● , ⏩ mit ●●.

```json
{
  "schema": 2, "id": "saegezahn-duell", "name": "Sägezahn-Duell", "icon": "🪚",
  "desc": "Immer schneller, dann Zucker. ⏩ und ⏪ für alle.",
  "owner": "lena", "based_on": "saegezahn@1", "fies_default": 3, "handicap": true,
  "flight": {
    "segments": [
      { "type": "ramp", "from": 0, "to": 25, "over_s": 4 },
      { "type": "saw", "from": 25, "to": 85, "rise_s": 10, "drop": "hard",
        "kick": { "v": -30, "s": 0.6 }, "repeat": 6 }
    ],
    "after": "loop"
  },
  "spice": [],
  "jokers": {
    "account": "separate", "lock_s": 5,
    "items": [
      { "kind": "boost",  "who": "all", "count": [3, 2, 2, 2, 2], "strength": 25,
        "dur_s": 2.0, "cooldown_s": 10, "hold_ms": 400 },
      { "kind": "rewind", "who": "all", "count": 1, "strength": 35,
        "dur_s": 0.8, "cooldown_s": 20, "hold_ms": 400 }
    ]
  },
  "end": { "time_s": 120, "last_player": false, "plan_end": false },
  "seed": null
}
```

Kein Joker braucht „Statistik & Ausscheiden“ (`who: "all"`), also erscheint „Ich bin raus“ nicht.

## 6. Zwei weitere Beispiele

### 6.1 Einfach: „Klassisch, aber langsamer“ (3 Tipps)

1. `Modi` → Klassisch → **„Kopieren & ändern“** (öffnet E2).
2. Schnellregler auf der Flugplan-Karte von 55 auf **40 %** ziehen (Kurve oben folgt).
3. **Speichern** (Name vorgeschlagen: „Klassisch (Kopie)“, änderbar, Symbol bleibt ✈️).

```json
{ "schema": 2, "id": "klassisch-langsam", "name": "Klassisch gemütlich", "icon": "✈️",
  "desc": "Wie Klassisch, nur gemütlicher.", "based_on": "klassisch@1", "fies_default": 3,
  "flight": { "segments": [ { "type": "ramp", "from": 0, "to": 40, "over_s": 4 },
                            { "type": "const", "v": 40, "for_s": null } ], "after": "hold" },
  "spice": [], "jokers": { "items": [] }, "end": {} }
```

### 6.2 Komplex: „Gewitter“ ⛈️

Idee: Louie schaukelt in Wellen, ab und zu „blitzt“ es (Schein-Bremse ohne Vorwarnung). Wer raus ist, wird zur
Gewitterwolke 👻 und darf mit 💨 Böe schieben oder mit ⚡ Blitz zurückstoßen. Ende nach 2 min oder wenn nur
noch einer übrig ist.

| Karte | Einstellungen (Tipps) |
|---|---|
| Vorlage | 🌊 Welle |
| Flugplan | Welle 35→75 %, Periode 20 s, ∞; vorne Anlauf 4 s (aus der Vorlage) |
| Würze | ➕ 🎭 Schein-Bremse „manchmal“, ab 0:15, Mehr: Vorwarnung 0 s · ➕ ⚡ Ruckler „selten“ |
| Joker | Aktive: keine · Geister: ➕ 💨 Böe (⏩, 3×, stark) · ➕ ⚡ Blitz (⏪, 1×) · Konto je Art |
| Ende | 2 min · „Wenn nur noch einer übrig ist“ an → 🟢 „Spieler melden sich mit ‚Ich bin raus‘“ |
| Speichern | „Gewitter“, ⛈️, „Wer raus ist, wird zur Gewitterwolke.“ |

Aktive Spieler sehen nur Status und unten „Ich bin raus ⏻“ (halten). Danach wechselt das Gamepad auf das
violette Geister-Layout mit 💨 rechts und ⚡ links.

```json
{
  "schema": 2, "id": "gewitter", "name": "Gewitter", "icon": "⛈️",
  "desc": "Wer raus ist, wird zur Gewitterwolke.", "based_on": "welle@1", "fies_default": 3,
  "flight": {
    "segments": [
      { "type": "ramp", "from": 0, "to": 35, "over_s": 4 },
      { "type": "wave", "min": 35, "max": 75, "period_s": 20, "shape": "sine", "repeat": null }
    ],
    "after": "hold"
  },
  "spice": [
    { "kind": "fakeout", "per_min": 1.5, "dur_s": 1.0, "warn_s": 0, "from_s": 15 },
    { "kind": "jolt", "per_min": 0.5, "dur_s": 0.4, "warn_s": 0.5, "from_s": 30 }
  ],
  "jokers": {
    "account": "separate", "lock_s": 6,
    "items": [
      { "kind": "boost",  "who": "out", "label": "Böe",  "icon": "💨", "count": 3,
        "strength": 30, "dur_s": 2.0, "cooldown_s": 8, "hold_ms": 300 },
      { "kind": "rewind", "who": "out", "label": "Blitz", "icon": "⚡", "count": 1,
        "strength": 35, "dur_s": 0.8, "cooldown_s": 20, "hold_ms": 400 }
    ]
  },
  "end": { "time_s": 120, "last_player": true, "plan_end": false },
  "seed": null
}
```

`label`/`icon` sind optionale Anzeigenamen; die Wirkung bestimmt `kind`.

## 7. Wer darf den Baukasten nutzen

Besitzer-Einstellung **„Modi erstellen“** (unter 🔒 Rechte):

| Stufe | Spielleiter | Besitzer |
|---|---|---|
| **aus** | nur Schnellwahl und „nur diese Runde“-Regler | alles |
| **Entwürfe** (Standard im Profil Kinder) | Baukasten öffnen, trocken abspielen, „nur diese Runde spielen“, nicht speichern | alles |
| **Speichern** (Standard Familie/Party) | zusätzlich speichern, eigene Modi löschen, Export | alles, auch Import, Sperren, fremde Modi löschen |

- Bearbeiten geht jederzeit (auch während einer Runde, es ändert nichts am laufenden Spiel). **Spielen** eines
  Entwurfs nur in BEREIT/ENDE bei Hebel aus, wie jeder Moduswechsel.
- Mitspieler- und Zuschauer-Handys sehen den Baukasten nicht.
- Alles läuft durch die Klemmkette (Modus → Fiesheit → diese Runde → Tempo-Deckel → Besitzer-Grenzen →
  Motorschicht). Ein Modus kann nie mehr, als der Besitzer erlaubt. Der Baukasten braucht deshalb kein Passwort.
- Profil Kinder: eigene Modi erscheinen nur in der Schnellwahl, wenn der Besitzer sie freigibt.

## 8. V1 und später

| Stufe | Inhalt |
|---|---|
| **V1** | Schema 2 komplett im Interpreter (inkl. `saw`, Rückwärts-Tempo, Joker-Konten, 5er-Listen, Fiesheits-Regeln), Vorlagen-Galerie, Baukasten-Übersicht mit Vorschau und Fiesheits-Schalter, Flugplan-Editor mit allen 7 Abschnitten, Würze, Joker (max. 2 je Zustand, getrennt/gemeinsam), Ende, Validierung mit Hinweisen, Trocken abspielen (1×/4×, Bots), Probefahrt 10 s, Speichern mit Name/Symbol/Satz, Recht „Modi erstellen“, JSON kopieren/einfügen |
| **V1.1** | Profi-Tabelle für alle Felder, Vorteil pro Spieler, QR-Teilen, Werkstatt echt mit Jokern von Hand, Bot-Strategien erweitern |
| **Später** | Abschnitts-Gruppen wiederholen („Abschnitt 2–3 dreimal“), Kurve malen, Wenn-dann-Regeln, 3 Joker gleichzeitig, Live-Dirigent |

Damit wird der Editor gegenüber [web-ui-konzept.md](web-ui-konzept.md) 6.3 (dort V1.1) vorgezogen: Der
Auftraggeber erwartet ihn, und weil Datenmodell und Interpreter ohnehin alle Schichten können, ist die
V1-Fassung vor allem UI-Arbeit.

## 9. Offene Punkte

- [ ] Spürt man einen Rücksprung-Stoß von 0,6 s bei −30 % als Absicht oder als Fehler? (Probefahrt)
- [ ] ⏪ links / ⏩ rechts mit Kindern testen (gegen übereinander).
- [ ] Ist „Anzahl bleibt gleich über die Fiesheit“ richtig, oder wünschen sich Familien weniger Joker bei 👹?
- [ ] Vibrationsmuster gehen auf iPhones im Browser nicht; reicht dort der Füllring?
