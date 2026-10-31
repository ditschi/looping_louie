# Ideensammlung und Gremium

Stand: 2026-11-01 · Status: Sammlung, nichts ist beschlossen. Ergänzt [software-konzept.md](software-konzept.md).

## 1. Vorgehen

1. **Fünf Ideen-Teams** (KI-Agenten) haben unabhängig voneinander gesammelt: Spielmodi & Spielmechanik,
   Party/Multiplayer/Trinkspiel, User Experience & Design, Besitzer- und Admin-Einstellungen,
   Hardware/Sicherheit/Robustheit. Ergebnis: **254 Ideen** (Katalog in Abschnitt 5).
2. Ein **Gremium aus vier Nutzertypen** hat jede Idee bewertet (0 = egal bis 3 = unbedingt) und
   angegeben, ob sie in V1 gehört:

   | Persona | Kurzprofil |
   |---|---|
   | Familien-Elternteil | 2 Kinder (6 und 9), Technik-Laie, will einfach, fair, sicher |
   | Party-Gastgeber | WG-Partys mit 6–10 Leuten, Trinkspiele, Chaos, Zuschauer |
   | Bastler/Besitzer | baut und verschenkt den Bausatz, will Robustheit und Einstellbarkeit |
   | Gelegenheitsspieler | Gast mit fremdem iPhone, 20 Sekunden Geduld, keine Anmeldung |

3. Die V1-Auswahl unten fasst Dubletten zusammen (z. B. vier Varianten des Rückspulers) und ist ein
   **Vorschlag** auf Basis der Stimmen. Endgültig entscheiden wir.

Legende im Katalog: Aufwand klein/mittel/groß · HW = mit geplanter Hardware machbar (ja / eingeschränkt / nein) ·
★ = Summe der Bewertungen (max. 12) · V1 = Stimmen für V1 (max. 4).

## 2. Was das Gremium sagt

- **Familie**: „Hebel umlegen, und es läuft.“ Sicherheit (Finger im Arm → Stopp) und ein Kinderprofil
  mit einem Tipp. Zwei, drei Modi reichen. Rückspuler ja, aber mit Kontingent, Sperrzeit und Vorwarnung.
  Saboteure, Wetten, Geheimmissionen bringen Streit. Trinkspiel nicht in V1. Bildschirme müssen Kinder
  ohne Lesen verstehen.
- **Party**: Alles entscheidet sich in den ersten 30 Sekunden: QR scannen, Huhn antippen, großer Knopf.
  Rückspuler mit Vorwarnung ist das Herz. Ausgeschiedene und Zuschauer brauchen etwas zu tun.
  Schadenfreude lebt davon, dass alle sehen, **wer** gespult hat. Wunsch für bald danach: Großbild am Fernseher.
- **Bastler**: Ein frisch eingelegtes Board darf nichts kaputt machen: sichere Standardwerte,
  Blockier-Erkennung, Richtungswechsel über Null, Turbo-Zeitbudget, Unterspannung, Update mit Rücksprung.
  Lehnt alles ab, was aus dem Motorstrom mehr Wissen vortäuscht, als die Hardware hat (Treffer zählen,
  Drehzahl, Chip-Erkennung). Wünscht Diagnose-Export und Kurzanleitung für Beschenkte.
- **Gast**: Größtes Risiko ist das Captive Portal auf dem iPhone. Rettungsseite, ehrliche Verbindungsanzeige,
  Wiederverbinden mit Platzgarantie sind wichtiger als jeder Spielmodus. Ein großer Knopf, keine
  Kontingent-Arithmetik. iOS hat keine Vibration und ohne HTTPS keinen Wake Lock → sichtbare Rückmeldung nötig.

**Einig über alle vier**: Rückspuler, QR-Lobby mit Hühnerfarben, Klassisch und Druckkochtopf,
Verbindungsanzeige, Gamepad-Ansicht, Countdown, Blockier-Erkennung, Notaus.

**Einig abgelehnt**: Modus-Editoren mit Zeitleiste oder Wenn-dann-Regeln (V1), Reaktionsduelle im
0,3-s-Fenster (WLAN-Latenz macht sie unfair), Auktionen, Strom-„Sensorik“ für Treffer oder Position.

## 3. Vorschlag für V1

### Spiel

| Funktion | Zusammengefasst aus | Notiz |
|---|---|---|
| **Klassisch plus** | modi-1 | auch Standard beim Spielen ohne Handy |
| **Druckkochtopf** (langsame Steigerung) | modi-2 | Runden enden von selbst |
| **Würfelmotor** (Zufall) | modi-6 | |
| **Fiesheits-Regler** von „Kindergeburtstag“ bis „Endgegner“ | modi-45 | skaliert alle Modusparameter innerhalb der Admin-Grenzen; ersetzt in V1 den Modus-Editor |
| **Mini-Ruckler** statt langer Rückwärtsfahrt | modi-10 | Spürbarkeit im Prototyp prüfen (Rampe) |
| **Rückspuler** mit Kontingent pro Spieler, globaler Sperre für alle, Halten zum Auslösen, Vorwarnung 0,5 s, Anzeige „wer hat gespult“ | party-1, modi-11, modi-12, technik-29, ux-9, ux-22 | Kern des Multiplayer-Spaßes |
| **Geister-Boost**: Ausgeschiedene bekommen Boost-Knöpfe | party-6, modi-28 | jeder hat bis zum Ende etwas zu tun |
| **„Ich bin raus“** per Selbstmeldung mit Bestätigung | party-24, ux-13 | Elektronik sieht die Chips nicht |

### Bedienung

| Funktion | Zusammengefasst aus |
|---|---|
| **QR-Lobby mit Hühnerfarben**: Huhn antippen statt Platz wählen, Namenswürfel statt Tippen | party-47, ux-4, ux-1, ux-2, ux-5 |
| **Drei-Sekunden-Onboarding** für Gäste, keine Anmeldung | ux-6 |
| **Gamepad-Ansicht**: ein großer Knopf, Querformat möglich | ux-7 |
| **Countdown-Ritual** 3-2-1 synchron auf allen Handys | ux-34 |
| **Verbindungs-Ampel** mit ehrlicher Sprache, **Wiederverbinden mit Platzgarantie** | ux-28, ux-40 |
| **Captive-Portal-Rettungsseite** mit Anleitung je Betriebssystem | ux-3 |
| **Hebel-Spiegel**: echter Hebel live im UI, zeigt Fehlbedienung | ux-30 |

### Besitzer / Admin

| Funktion | Zusammengefasst aus |
|---|---|
| **Profil-Schnellwahl** Kinder / Familie / Party (ein Tipp stellt Tempo, Rückwärts, Rückspuler, erlaubte Modi um) | party-39, besitzer-1, technik-33, ux-25 |
| **Tempo-Deckel** als großer Schieberegler | besitzer-3 |
| **Grenzen für Partyfunktionen** (Kontingente, Sperrzeiten) | party-49 |

### Technik und Sicherheit

| Funktion | Zusammengefasst aus |
|---|---|
| **Blockier-Erkennung** über Motorstrom mit Sofort-Stopp, ausgeblendet während des Anlaufs | technik-1, technik-2 |
| **Notaus** für den Spielleiter im UI | technik-32 |
| **Sichere Standardwerte**, solange kein Modell gewählt ist | technik-48 |
| **Richtungswechsel nur über Null** mit Totzeit | technik-3 |
| **Mehrstufiger Watchdog** (Motor-Task, Firmware, Hardware) | technik-16 |
| **Unterspannung in drei Stufen** (Warnung, Runde beenden, Schlaf) | technik-11 |
| **Turbo-Zeitbudget** über Nennspannung | technik-5 |
| **Rate-Limit** pro Sitzung, **Sitzplatz-Diebstahl** verhindern | technik-28, technik-30 |

Klickbarer Prototyp dieser Auswahl: [web/prototype/index.html](../web/prototype/index.html) (im Browser öffnen;
Hebel, Mitspieler, Verbindung und Akku werden über die Leiste „Simulation“ gesteuert).

## 4. Kandidaten für V1.1 und später

- **Zuschauer-Großbild** am TV/Tablet (ux-15), Zuschauer-Rolle mit Jubel/Buh (party-15, party-18)
- **Sabotage-Statistik und Titel** am Rundenende, Highlight-Ticker (party-30, party-48)
- **Update mit Rücksprung**, Konfiguration mit Prüfsumme, **Diagnose-Export** (technik-46, technik-47, technik-22)
- **Trinkspiel-Modus** mit einfacher Regelliste, alkoholfrei als Standard, Freischaltung durch Admin (party-33, party-34, besitzer-27)
- Fake-out-Bremse, Zeitrennen, sichtbares Rückwärts-Budget (modi-16, modi-20, modi-14/ux-48)
- Chaos-Taste für den Spielleiter (party-43)
- Modus-Editor (frühestens nach V1, wenn klar ist, was Fiesheits-Regler und Profile nicht abdecken)

## 5. Katalog aller Ideen

Innerhalb jedes Themas sortiert nach Bewertung des Gremiums.

### 5.1 Spielmodi & Spielmechanik (53)

- **Klassisch plus** — Konstante Geschwindigkeit wie im Original, nur einstellbar und mit sanfter Anlauframpe. Gedacht als Referenzmodus und Rückfallebene, wenn niemand ein Handy in die Hand nehmen will. *Hinweis: Ist praktisch der Hebel-ohne-Handy-Standard aus dem Konzept.*
  <br>`modi-1` · Geschwindigkeitsprofil · Aufwand klein · HW ja · ★ 11 · V1 4/4
- **Langsame Steigerung (Druckkochtopf)** — Die Runde beginnt gemütlich und wird alle paar Sekunden ein wenig schneller, bis die Turbo-Grenze erreicht ist. So entsteht ein natürlicher Spannungsbogen und Runden enden von selbst, ohne dass sie ewig dauern. *Hinweis: Der Baustein ramp_up ist schon vorgesehen; die Kurve (linear, exponentiell, Treppe) könnte wählbar sein.*
  <br>`modi-2` · Geschwindigkeitsprofil · Aufwand klein · HW ja · ★ 11 · V1 4/4
- **Rückspuler mit Joker-Kontingent** — Jeder Spieler hat pro Runde z. B. 2 Rückspul-Joker (0,5-1 s Rückwärts) mit Abklingzeit, ausgelöst per großem Knopf am Handy. Auf allen Handys erscheint, wer gespult hat, damit Rache und Absprachen entstehen. *Hinweis: Kern-Idee aus dem Auftrag; die globalen Rückwärtsgrenzen (Mindestabstand, Anteil) müssen weiter greifen.*
  <br>`modi-11` · Rückwärts in Maßen · Aufwand mittel · HW ja · ★ 10 · V1 3/4
- **Fiesheits-Regler (ein Regler für alles)** — Ein einziger Schieberegler von "Kindergeburtstag" bis "Endgegner" skaliert alle Modusparameter gemeinsam: Tempo, Zufall, Fake-outs, Rückwärtsanteil innerhalb der Admin-Grenzen. Das ist eine Schnelleinstellung für alle, die nicht basteln wollen.
  <br>`modi-45` · Balancing · Aufwand klein · HW ja · ★ 10 · V1 3/4
- **Ausgeschiedene als Störenfriede (Geistermodus)** — Wer raus ist, ist nicht arbeitslos: Ausgeschiedene bekommen Boosts, Fake-out-Bremsen oder Rückspuler, um die Verbleibenden zu ärgern. So hat jeder bis zum Rundenende etwas zu tun. *Hinweis: Erweitert "Last Chicken Standing" aus dem Konzept um mehr Aktionstypen.*
  <br>`modi-28` · Handicap & Balancing · Aufwand klein · HW ja · ★ 10 · V1 2/4
- **Fake-out-Bremse** — Louie bremst plötzlich stark ab, als würde er stehen bleiben, und beschleunigt dann wieder. Die Wippen-Spieler, die schon für einen Treffer ausgeholt haben, schlagen ins Leere. *Hinweis: Die aktive Bremse der H-Brücke macht das spürbar abrupt; die Rampe darf beim Bremsen nicht zu weich sein.*
  <br>`modi-16` · Pausen & Fake-outs · Aufwand klein · HW ja · ★ 9 · V1 1/4
- **Rückwärts-Zucker (Mini-Ruckler)** — Statt echter Rückwärtsphasen gibt es nur sehr kurze Richtungs-Ruckler von 0,3-0,5 s, die die Flugbahn stören, ohne dass man wehrlos wird. Das ist als Standard-Würze für alle Modi gedacht, die Rückwärts erlauben. *Hinweis: Wegen der Rampe gegen Brownout fällt die Richtungsumkehr träger aus; ob 0,3 s spürbar sind, muss der Prototyp zeigen.*
  <br>`modi-10` · Rückwärts in Maßen · Aufwand klein · HW eingeschränkt · ★ 8 · V1 3/4
- **Rückspul-Sperrfeuer (globale Abklingzeit)** — Nach jedem Rückspuler ist das Rückspulen für alle für einige Sekunden gesperrt, angezeigt als roter Ring auf allen Handys. Daraus entsteht ein Wettrennen: Wer zuerst drückt, hat den Joker, und alle anderen warten. *Hinweis: Verhindert Spam durch mehrere Spieler hintereinander.*
  <br>`modi-12` · Rückwärts in Maßen · Aufwand klein · HW ja · ★ 8 · V1 3/4
- **Rückwärts-Budget der Runde** — Die Runde hat ein gemeinsames Rückwärts-Budget (z. B. 5 s gesamt), das als Balken auf allen Handys sichtbar ist. Alle Rückspuler und Zufalls-Rückwärtsstöße zehren davon, und wenn es leer ist, gibt es nur noch vorwärts. *Hinweis: Macht die Admin-Grenze "max. Anteil an der Rundenzeit" für Spieler sichtbar.*
  <br>`modi-14` · Rückwärts in Maßen · Aufwand klein · HW ja · ★ 8 · V1 1/4
- **Zeitrennen (Survival-Timer)** — Die Runde dauert eine feste Zeit (z. B. 90 s). Gewonnen hat, wer am Ende noch die meisten Chips hat, gezählt von Hand und im Handy eingetragen. Runden sind so planbar, ideal für Partys mit wechselnden Spielern. *Hinweis: Chips zählt die Elektronik nicht, Eingabe per Handy oder durch den Spielleiter.*
  <br>`modi-20` · Rundenformat · Aufwand klein · HW ja · ★ 8 · V1 1/4
- **Schleichfahrt vor dem Sprint** — Louie wird für einige Sekunden fast unmerklich langsam (Kriechgang), alle entspannen sich, und dann kommt ein Sprint auf Turbo-Grenze. Die Ruhe vor dem Sturm ist das eigentliche Spielelement. *Hinweis: Mindestspannung beachten, sonst bleibt der Motor stehen; aus dem Modellprofil.*
  <br>`modi-19` · Pausen & Fake-outs · Aufwand klein · HW ja · ★ 8 · V1 0/4
- **Reiner Zufall (Würfelmotor)** — In zufälligen Abständen wird eine neue Zufallsgeschwindigkeit innerhalb von Min/Max gewählt. Das ist der einfachste Chaosmodus, und man kann mit ihm keinen Rhythmus lernen. *Hinweis: Entspricht speed.type=random aus dem Konzept.*
  <br>`modi-6` · Zufall · Aufwand klein · HW ja · ★ 7 · V1 3/4
- **Treppe mit Ansage** — Die Geschwindigkeit springt stufenweise nach oben, jede Stufe wird auf allen Handys mit Countdown angekündigt ("Stufe 4 in 3...2...1"). Die Vorfreude gehört hier zum Spiel, der Schreck wird zur Ansage. *Hinweis: Ohne Handy gibt es keine Ankündigung; als Ersatz könnte die Status-LED blinken (im Batteriefach aber schlecht sichtbar).*
  <br>`modi-5` · Geschwindigkeitsprofil · Aufwand klein · HW ja · ★ 7 · V1 0/4
- **Schwebe-Pause (Stopp mit Countdown)** — Louie hält kurz an, auf allen Handys läuft ein Countdown, und dann geht es mit voller Geschwindigkeit oder rückwärts weiter (Überraschung). Die Pause baut Spannung auf und gibt Zeit, Chips nachzuzählen.
  <br>`modi-17` · Pausen & Fake-outs · Aufwand klein · HW ja · ★ 7 · V1 0/4
- **Spielleiter als Dirigent** — Im Live-Modus steuert der Spielleiter Louie direkt mit einem Schieberegler und Effekt-Knöpfen (Fake-out, Sprint, Ruckler), wie ein DJ. Grenzen und Rampen setzt weiterhin der Server durch. *Hinweis: Die Latenz (bis ca. 100 ms plus Rampe) macht die Steuerung weich, aber ausreichend.*
  <br>`modi-50` · Spielmodus · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Gewichteter Zufall / Launen** — Statt gleichverteiltem Zufall hat Louie Launen: "verschlafen", "nervös" oder "wütend", jede mit eigener Geschwindigkeitsverteilung. Die Launen wechseln selbst zufällig, und die aktuelle Laune wird auf den Handys als Gesicht angezeigt.
  <br>`modi-7` · Zufall · Aufwand mittel · HW ja · ★ 6 · V1 0/4
- **Publikumsjoker (Zuschauer stimmen ab)** — Gäste ohne Platz können per Handy abstimmen: "schneller", "langsamer" oder "zurück". Wenn genug Stimmen in einem Zeitfenster zusammenkommen, wird die Aktion ausgelöst, und das Publikum ist damit Teil des Spiels. *Hinweis: Die Client-Zahl ist begrenzt (Ziel 8-10 am Hotspot); bei großen Partys ist das Heim-WLAN nötig.*
  <br>`modi-34` · Spieler-Interaktion · Aufwand mittel · HW eingeschränkt · ★ 6 · V1 0/4
- **Zufall mit Gedächtnis (fair random)** — Der Zufall merkt sich, wie lange es schon ruhig war, und erhöht dann die Wahrscheinlichkeit für einen Ausreißer (und umgekehrt). So gibt es keine minutenlangen Langeweile-Strecken und keine Dauer-Hektik, obwohl es zufällig wirkt. *Hinweis: Gut als Option für alle Zufallsbausteine statt als eigener Modus.*
  <br>`modi-8` · Zufall · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Fehlstart-Bluff** — Beim Rundenstart zuckt Louie kurz an, stoppt, zuckt wieder, und erst beim dritten Mal geht es wirklich los. Das ist ein kleiner Gag zu Rundenbeginn, abschaltbar für Kinder, die das nervt.
  <br>`modi-18` · Pausen & Fake-outs · Aufwand klein · HW ja · ★ 5 · V1 0/4
- **Best-of-3 / Best-of-5** — Mehrere Runden hintereinander, Siege werden auf den Handys gezählt, zwischen den Runden gibt es eine kurze Pause mit Zwischenstand. Wer den Matchball hat, bekommt optional ein Handicap. *Hinweis: Die Siegerermittlung braucht eine manuelle Eingabe ("ich bin raus" oder Spielleiter).*
  <br>`modi-21` · Rundenformat · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **King of the Hill (Herausforderer-Runden)** — Der Sieger bleibt sitzen, die Verlierer werden durch wartende Spieler ersetzt. Eine Siegesserie wird angezeigt ("Lisa: 4 in Folge") und erhöht ab einer bestimmten Länge automatisch die Schwierigkeit für den Champion.
  <br>`modi-23` · Rundenformat · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Sudden Death** — Wenn nur noch zwei Spieler übrig sind (vom Spielleiter markiert), schaltet der Modus auf eine eigene Endphase: schneller, mehr Fake-outs, und jeder hat einen letzten Rückspuler. So wird das oft zähe Duell am Ende kürzer und dramatischer. *Hinweis: Funktioniert nur, wenn die Ausgeschiedenen zuverlässig gemeldet werden.*
  <br>`modi-24` · Rundenformat · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Ein-Chip-Blitzrunde** — Jeder spielt nur mit einem Chip, Runde maximal 30 s und mit hoher Geschwindigkeit. Die Runden sind schnell, eignen sich zum Aufwärmen oder als Entscheidungsrunde bei Gleichstand. *Hinweis: Eher eine Spielregel mit passendem Modus-Preset als eine Firmware-Funktion.*
  <br>`modi-25` · Rundenformat · Aufwand klein · HW ja · ★ 5 · V1 0/4
- **Glücksrad zwischen den Runden** — Nach jeder Runde dreht der Verlierer ein Glücksrad auf dem Handy, das den Modifikator der nächsten Runde bestimmt ("doppelte Joker", "kein Rückwärts", "Turbo-Start"). Das bringt Abwechslung, ohne dass man Modi auswählen muss.
  <br>`modi-36` · Rundenformat · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Trinkspiel-Ereignisse** — Optionaler Erwachsenen-Modus: Bestimmte Motor-Ereignisse werden zu Trinkregeln, die auf den Handys erscheinen ("Rückwärts: der Auslöser trinkt", "Fake-out: alle, die gezuckt haben", "Sprint: letzter Chip-Verlierer"). Die Regeln sind editierbar, und es gibt eine alkoholfreie Variante mit Aufgaben statt Schlucken. *Hinweis: Nur per Admin freischaltbar und mit Altershinweis; nie als Standard.*
  <br>`modi-47` · Trinkspiel · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Wechselnder Dirigent** — Alle 20 s wechselt die Steuerung reihum an einen anderen Spieler, der Louie dann live lenkt, auch gegen die anderen. Wer gerade steuert, wird auf allen Handys groß angezeigt. *Hinweis: Der Dirigent spielt gleichzeitig mit; einhändige Bedienung neben der Wippe ist schwierig, eventuell nur Knöpfe statt Regler.*
  <br>`modi-51` · Spielmodus · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Kinder-Handicap pro Platz** — Pro Platz lässt sich ein Handicap einstellen, z. B. bekommt das jüngste Kind mehr Joker, die Erwachsenen weniger oder gar keinen Rückspuler. Damit können gemischte Altersgruppen gegeneinander spielen, ohne dass jemand immer verliert. *Hinweis: Die Motorgeschwindigkeit gilt für alle gleich; ein echtes Handicap am Spielfeld ist nicht möglich, nur bei den Handy-Aktionen.*
  <br>`modi-29` · Handicap & Balancing · Aufwand mittel · HW eingeschränkt · ★ 4 · V1 1/4
- **Herzschlag** — Die Geschwindigkeit pulsiert rhythmisch (schnell-langsam-schnell) wie ein Herzschlag, der im Lauf der Runde immer schneller wird. Wer den Rhythmus erkennt, kann ihn ausnutzen, bis er kippt. *Hinweis: Die Rampengrenze (max. V/s) dämpft sehr schnelle Pulse; die Periode sollte daher eher 1-3 s betragen.*
  <br>`modi-3` · Geschwindigkeitsprofil · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Wellengang** — Die Geschwindigkeit folgt einer langen, langsamen Sinuskurve mit leichtem Rauschen. Das fühlt sich an wie Seegang: lange ruhige Täler und dann ein Wellenkamm, bei dem alle hektisch werden.
  <br>`modi-4` · Geschwindigkeitsprofil · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Aufholjagd-Boost (Rubberbanding)** — Wer schon Chips verloren hat (eingetragen am Handy), bekommt mehr oder stärkere Boosts und Rückspuler als die Führenden. So bleiben auch zurückliegende Spieler beteiligt. *Hinweis: Die Chipzahl ist eine Selbstangabe, daher Missbrauch möglich (Kinder melden sich ärmer).*
  <br>`modi-27` · Handicap & Balancing · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Champion-Steuer** — Wer die letzte Runde gewonnen hat, verliert in der nächsten Runde Joker oder muss einen Rückspuler der anderen ohne Abklingzeit hinnehmen. Das ist eine einfache automatische Balancing-Regel für Serien.
  <br>`modi-30` · Handicap & Balancing · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Saboteur unter uns** — Einer der Spieler ist heimlich Saboteur und hat stärkere Rückspuler, die anonym ausgelöst werden. Am Ende tippt jeder, wer es war, und wer richtig tippt, bekommt Punkte. *Hinweis: Funktioniert nur mit eigenem Handy pro Spieler; Bildschirme müssen verdeckt bleiben.*
  <br>`modi-33` · Spieler-Interaktion · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Bündnis-Spuler** — Zwei Spieler müssen innerhalb von 2 s gemeinsam drücken, damit ein Rückspuler ausgelöst wird, der dann stärker oder länger ist. Daraus entstehen kurzfristige Allianzen und Verrat. *Hinweis: Wegen der WLAN-Latenz ist ein großzügiges Zeitfenster sinnvoll.*
  <br>`modi-35` · Spieler-Interaktion · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Louie hat Hunger (Blockier-Event)** — Wenn jemand Louies Flugzeug absichtlich festhält (Motorstrom steigt stark an), stoppt der Motor sofort zum Schutz, und auf den Handys erscheint "Foul! Wer war das?". Das Spiel kann daraus eine Strafe für die nächste Runde machen. *Hinweis: Die Blockiererkennung über den Strom ist realistisch, sie sagt aber nicht, wer blockiert hat. Sie dient vor allem dem Motorschutz und sollte unabhängig vom Spiel immer aktiv sein.*
  <br>`modi-37` · Motorstrom-Ereignisse · Aufwand mittel · HW eingeschränkt · ★ 4 · V1 0/4
- **Modus-Editor: Kurve malen** — Man malt mit dem Finger eine Geschwindigkeitskurve über die Zeit, die als Punkteliste gespeichert und interpoliert wird. Das ist besonders für Kinder intuitiv ("hier soll er ganz schnell werden"). *Hinweis: Die Server-Klemmung auf Rampe und Grenzen glättet zu steile Striche; die Vorschau sollte die geklemmte Kurve zeigen.*
  <br>`modi-42` · Modus-Editor · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Automatische Schwierigkeit (Lernender Louie)** — Louie merkt sich, wie lange Runden in dieser Gruppe dauern, und passt die Steigerung so an, dass Runden etwa eine Zielzeit (z. B. 2 min) treffen. Sind Runden zu lang, wird es schneller, sind sie zu kurz, gemütlicher. *Hinweis: Die Rundendauer kennt das Gerät (Start bis Hebel aus), zuverlässiger mit Ende-Meldung.*
  <br>`modi-46` · Balancing · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Trinkspiel: Rückspul-Preis** — Jeder Rückspuler kostet den Auslöser einen Schluck, oder er darf einen Schluck verteilen, wenn er jemanden rauswirft. Daraus entsteht ein Abwägen zwischen Ärgern und Selbstschutz. *Hinweis: Ist im Wesentlichen nur Text und Anzeige auf den Handys.*
  <br>`modi-48` · Trinkspiel · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Countdown-Bombe** — Ein sichtbarer Timer läuft ab, und bei null gibt es einen zufälligen Großeffekt (Sprint, Mini-Ruckler-Serie oder Vollbremsung). Spieler können den Timer per Handy mit Jokern verlängern oder verkürzen.
  <br>`modi-53` · Pausen & Fake-outs · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Hebel-Geste als Spielaktion** — Ohne Handy kann der Hebel im Spiel genutzt werden: kurz aus-an innerhalb von 0,5 s = Pause, doppelt = nächster Modus. Damit ist ein Teil der Funktionen auch für Runden ohne Handy erreichbar. *Hinweis: Verwechslungsgefahr mit normalem Stopp und mit den Wiederherstellungsgesten beim Start; der Hebel trennt den Motor dabei kurz hart.*
  <br>`modi-39` · Bedienung ohne Handy · Aufwand mittel · HW eingeschränkt · ★ 3 · V1 0/4
- **Modus-Editor: Ereignis-Würfel** — Statt einer festen Timeline gibt es eine Liste von Ereignissen mit Wahrscheinlichkeit pro Sekunde (Fake-out 5 %, Rückwärts-Ruckler 3 %, Sprint 4 %). Das UI zeigt zusätzlich eine geschätzte "Fiesheit" und die erwartete Rundendauer. *Hinweis: Passt eng zum bestehenden JSON-Schema (chance/duration).*
  <br>`modi-41` · Modus-Editor · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Modi teilen per QR-Code** — Ein selbst gebauter Modus wird als kompakter Code oder QR-Code exportiert, den andere Louie-Besitzer einscannen können. Ohne Cloud lässt er sich so von Party zu Party weitergeben. *Hinweis: Ohne HTTPS ist kein Kamerazugriff im Browser möglich; der QR-Code muss mit der System-Kamera-App gescannt werden, z. B. als Link mit Modus im URL-Fragment.*
  <br>`modi-44` · Modus-Editor · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Seed-Duell (gleicher Zufall für alle)** — Ein Zufallsablauf wird über einen Code (z. B. "HUHN-42") festgelegt und lässt sich wiederholen. Gruppen oder Turnierrunden können exakt denselben "zufälligen" Ablauf spielen, und man kann besonders fiese Seeds teilen. *Hinweis: Durch Motortoleranz und Akkustand ist das nicht bitgenau gleich, die Sollwerte schon.*
  <br>`modi-9` · Zufall · Aufwand klein · HW ja · ★ 2 · V1 0/4
- **Spiegelrunde** — Eine Sonderrunde, die komplett rückwärts läuft, aber deutlich langsamer, damit man sich wehren kann. Gedacht als seltener Event-Modus oder als Strafrunde, nie als Standard. *Hinweis: Kollidiert mit der Standardgrenze (max. 10 % Anteil); geht nur, wenn der Admin das explizit erlaubt. Ob der Mechanismus rückwärts gleich gut fliegt, ist zu prüfen.*
  <br>`modi-15` · Rückwärts in Maßen · Aufwand klein · HW eingeschränkt · ★ 2 · V1 0/4
- **Punktejagd über mehrere Runden** — Statt "wer zuletzt übrig ist" gibt es Punkte: Platzierung pro Runde, Bonus für eingesetzte Rückspuler, die jemanden rauswerfen, Malus für frühes Ausscheiden. Die Gesamtwertung läuft über den Abend. *Hinweis: Wer durch welchen Rückspuler rausflog, sieht die Elektronik nicht; das kann nur per Ehrlichkeitsknopf erfasst werden.*
  <br>`modi-26` · Rundenformat · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Auktion der Joker** — Vor der Runde bieten die Spieler mit Chips (echten, aus ihrem Vorrat) oder Punkten auf Extra-Rückspuler. Wer viel bietet, startet mit weniger Chips, hat aber mehr Waffen. *Hinweis: Die Chips sind physisch, gezählt wird von Hand; das UI verwaltet nur die Gebote.*
  <br>`modi-31` · Handicap & Balancing · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Geheime Missionen** — Jeder Spieler bekommt vor der Runde verdeckt auf seinem Handy eine Mission ("Löse 2 Rückspuler aus, während Platz 3 noch drin ist", "Überlebe 60 s ohne Joker"). Erfüllte Missionen bringen Bonuspunkte. *Hinweis: Nur Missionen, die sich über Handy-Aktionen und Zeit prüfen lassen, sind automatisch auswertbar, alles andere per Ehrlichkeit.*
  <br>`modi-32` · Spieler-Interaktion · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Konter-Spuler** — Wer zum Zeitpunkt eines Rückspulers ebenfalls innerhalb von 0,3 s drückt, hebt ihn auf (Louie zuckt nur), und der Auslöser verliert seinen Joker. Daraus wird ein Reaktionsduell zwischen den Handys. *Hinweis: WLAN-Latenz mehrerer Handys (50-200 ms, schwankend) macht das Timing unfair; dafür wäre ein großzügiges Fenster nötig.*
  <br>`modi-13` · Rückwärts in Maßen · Aufwand mittel · HW eingeschränkt · ★ 1 · V1 0/4
- **Turnierbaum für große Gruppen** — Bei mehr als 4 Leuten erzeugt das UI Vorrunden mit je bis zu 4 Spielern, die Sieger kommen ins Finale. Der Turnierbaum ist live auf allen Handys sichtbar, und das Finale bekommt einen eigenen, härteren Modus. *Hinweis: Hängt an Profilen/Multi-User (Stufe 3); RAM für Turnierdaten ist unkritisch, das UI ist der Aufwand.*
  <br>`modi-22` · Rundenformat · Aufwand groß · HW ja · ★ 1 · V1 0/4
- **Party-Marathon mit Saisons** — Ein Abend wird zur Saison: mehrere Modi in festgelegter oder zufälliger Reihenfolge, eine Gesamtwertung, ein Mid-Season-Twist (z. B. ab Runde 5 Rückspuler doppelt) und eine Siegerehrung am Ende. Das ist das Dach für Turnier-, Punkte- und Handicap-Ideen. *Hinweis: Braucht Profile und Persistenz über Runden (Flash-Schreibzyklen sparsam halten).*
  <br>`modi-49` · Rundenformat · Aufwand groß · HW ja · ★ 1 · V1 0/4
- **Musik-Synchron (Tempo nach BPM)** — Ein Handy spielt Musik ab, und Louies Geschwindigkeit folgt einem vorgegebenen BPM-Profil der Playlist (vom Nutzer eingegeben oder per Tap-Tempo). Wenn der Beat droppt, kommt ein Sprint. *Hinweis: Das Gerät hat keinen Lautsprecher oder Mikrofon; das Handy liefert nur Tempo-Sollwerte. Eine echte Audioanalyse im Browser ist ohne HTTPS (Mikrofon) nicht möglich.*
  <br>`modi-52` · Spielmodus · Aufwand groß · HW eingeschränkt · ★ 1 · V1 0/4
- **Treffer-Ahnung über Stromspitzen** — Experimentell: Kurze Stromspitzen, wenn Louie gegen eine Wippe oder einen Chip stößt, werden gezählt und als "Treffer-Zähler" bzw. Intensitätsanzeige gezeigt. Das Ergebnis ist kein Chip-Ergebnis, aber ein Gefühl für Action. *Hinweis: Sehr unsicher: Die Signale sind klein und verrauscht, und Shunt, RC-Filter und ADC-Rate müssen reichen. Erst auf dem Prototyp messen.*
  <br>`modi-38` · Motorstrom-Ereignisse · Aufwand groß · HW eingeschränkt · ★ 0 · V1 0/4
- **Modus-Editor: Baukasten-Timeline** — Ein Modus besteht aus einer Abfolge von Blöcken ("10 s konstant 50 %", "Zufall 30-80 % für 20 s", "Fake-out", "Schleichfahrt", "Wiederholen"), die man am Handy per Drag-and-drop anordnet. Eine Vorschaukurve zeigt den Verlauf, und eine Probefahrt läuft auf echter Hardware. *Hinweis: Das JSON-Format müsste von Parametern auf Sequenzen erweitert werden; die Größe pro Modus sollte begrenzt bleiben (Flash, RAM).*
  <br>`modi-40` · Modus-Editor · Aufwand groß · HW ja · ★ 0 · V1 0/4
- **Modus-Editor: Bedingungen (Wenn-dann)** — Einfache Regeln wie "wenn nur noch 2 Spieler übrig sind, dann +20 %" oder "nach 60 s Rückspuler für alle freischalten". Damit lassen sich dynamische Modi bauen, ohne zu programmieren. *Hinweis: Die Bedingungen hängen an Handy-Meldungen (Ausscheiden); eine eigene kleine Regel-Engine kostet Firmware-Aufwand und Testaufwand.*
  <br>`modi-43` · Modus-Editor · Aufwand groß · HW ja · ★ 0 · V1 0/4

### 5.2 Party, Multiplayer & Trinkspiel (49)

- **Rückspuler-Knopf** — Jeder Spieler hat auf dem Handy einen Rückspul-Knopf, der Louie für 0,5–1 s rückwärts zucken lässt. Kontingent pro Runde (z. B. 2) und ein sichtbarer Abklingring. Alle Handys zeigen kurz an, wer gespult hat, damit es Schadenfreude und Rache gibt. *Hinweis: Gleichzeitige Anfragen nicht addieren; globale Rückwärts-Grenzen (Dauer, Abstand, Anteil) gelten immer. Rampe beim Richtungswechsel nötig.*
  <br>`party-1` · Rückspuler & Sabotage · Aufwand klein · HW ja · ★ 11 · V1 4/4
- **Handy-QR-Lobby mit Plätzen in Hühnerfarben** — Ein großer QR-Code auf dem Bildschirm des Spielleiters lädt neue Handys ein, die direkt eine freie Farbe zugewiesen bekommen. Ist alles voll, landet man automatisch als Zuschauer. *Hinweis: QR-Erzeugung im Browser mit kleiner JS-Bibliothek.*
  <br>`party-47` · UX & Design · Aufwand klein · HW ja · ★ 11 · V1 4/4
- **Ausscheiden per Selbstmeldung** — Wer seinen letzten Chip verliert, tippt auf seinem Handy 'Ich bin raus'. Das Handy wechselt dann in den Ausgeschiedenen-Modus mit Boosts. Optional bestätigt der Spielleiter. *Hinweis: Grundlage für viele andere Ideen, da die Hardware Chip-Verluste nicht erkennt.*
  <br>`party-24` · Party-Moderation · Aufwand klein · HW ja · ★ 10 · V1 2/4
- **Turbo-Boost für Ausgeschiedene** — Wer raus ist, bekommt Boost-Knöpfe und kann Louie kurz beschleunigen, um die Verbleibenden zu ärgern. Hält ausgeschiedene Spieler bei der Stange statt gelangweilt zuzuschauen. *Hinweis: Ausscheiden muss manuell gemeldet werden (Spieler oder Spielleiter), die Elektronik sieht es nicht.*
  <br>`party-6` · Boosts · Aufwand klein · HW ja · ★ 9 · V1 3/4
- **Kinder- und Party-Profil** — Ein Schalter in der Lobby schaltet zwischen 'Kinder' (kein Rückwärts, keine Sabotage, keine Trinkregeln) und 'Party' (alles erlaubt). Admin legt fest, was im jeweiligen Profil sichtbar ist.
  <br>`party-39` · Party-Moderation · Aufwand klein · HW ja · ★ 9 · V1 3/4
- **Admin-Grenzen für Partyfunktionen** — Admin legt fest: max. Rückspuler pro Spieler, ob Zuschauer eingreifen dürfen, Trinkspiel erlaubt ja/nein, max. Zuschauerzahl, Pflichtpausen. So bleibt das Spiel auch im Party-Chaos fair und sicher. *Hinweis: Ergänzt die bestehenden Rückwärts-Grenzen aus dem Konzept.*
  <br>`party-49` · Party-Moderation · Aufwand klein · HW ja · ★ 8 · V1 3/4
- **Bremsfalle** — Statt rückwärts kann ein Spieler eine kurze Vollbremsung (0,5 s, Kurzschlussbremse) auslösen. Louie stoppt abrupt, das Flugzeug sackt ab und trifft unberechenbar. Sanftere Sabotage als Rückwärts. *Hinweis: Bremsen über H-Brücke vorhanden; Mechanik auf ruckartige Stopps prüfen.*
  <br>`party-5` · Rückspuler & Sabotage · Aufwand klein · HW ja · ★ 8 · V1 2/4
- **Hühner-Avatare und Spitznamen** — Spieler wählen in der Lobby einen Namen und ein Hühner-Emoji/Avatar in ihrer Farbe. Diese erscheinen bei allen Ereignissen ('Gackernde Gisela spult zurück!').
  <br>`party-29` · UX & Design · Aufwand klein · HW ja · ★ 8 · V1 1/4
- **Handy vibriert bei Gefahr** — Wird gerade ein Rückspuler, Boost oder eine Ereigniskarte ausgelöst, vibrieren alle Spielerhandys kurz. Haptisches Feedback, ohne aufs Display schauen zu müssen. *Hinweis: Vibration API nicht auf iOS Safari verfügbar.*
  <br>`party-27` · UX & Design · Aufwand klein · HW ja · ★ 7 · V1 2/4
- **Zeitlupen-Joker** — Jeder hat einmal pro Spiel einen Joker, der Louie für 3 s stark verlangsamt. Gut zum Verteidigen, wenn man selbst bedroht ist, oder um andere aus dem Takt zu bringen.
  <br>`party-8` · Boosts · Aufwand klein · HW ja · ★ 7 · V1 0/4
- **Zuschauer-Rolle** — Wer nicht mitspielt, scannt den QR-Code und bekommt eine Zuschauer-Ansicht: Live-Geschwindigkeit, Ereignisse, wer wen sabotiert hat, Wettschein. Zuschauer können begrenzt eingreifen (z. B. ein Boost pro Runde). *Hinweis: Viele WebSocket-Clients belasten den RAM des ESP32-C3; Zuschauer-Anzahl begrenzen (z. B. 6–8).*
  <br>`party-15` · Zuschauer · Aufwand mittel · HW ja · ★ 6 · V1 2/4
- **Zuschauer-Buh und -Jubel** — Zuschauer hämmern auf einen Jubel- oder Buh-Knopf. Erreicht der Jubelpegel eine Schwelle, gibt es einen kleinen Boost; bei viel Buh kurz langsamer. Das Publikum wird zum Teil des Spiels. *Hinweis: Button-Spam drosseln (Server sammelt pro Sekunde).*
  <br>`party-18` · Zuschauer · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Sabotage-Statistik und Titel** — Nach dem Spiel vergibt das System Titel: 'Größter Saboteur', 'Pechvogel' (am häufigsten Opfer), 'Boost-Junkie', 'Pazifist' (nichts eingesetzt). Sorgt für Gesprächsstoff. *Hinweis: Daten nur im RAM bis Ende der Session, kein Speichern nötig.*
  <br>`party-30` · Party-Moderation · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Alkoholfreier Modus als Standard** — Jede Trinkregel hat eine neutrale Variante: 'Schluck Wasser', 'Liegestütz', 'Witz erzählen', 'Kompliment machen'. Pro Spieler einstellbar, sodass gemischte Runden möglich sind. *Hinweis: Text-Bausteine, kaum Speicher.*
  <br>`party-34` · Trinkspiel · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Highlight-Ticker** — Ein laufender Ticker unten auf allen Handys erzählt die Runde: '12 s: Blau spult zurück', '20 s: Combo-Boost von Rot und Gelb'. Nach der Runde als Zusammenfassung zum Teilen (Screenshot).
  <br>`party-48` · UX & Design · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Angekündigter Rückspuler** — Der Rückspuler wird nicht sofort ausgelöst, sondern alle Handys zeigen einen 3-2-1-Countdown mit dem Namen des Saboteurs. Das macht Rückwärts weniger unfair, weil sich alle vorbereiten können, und erhöht die Spannung. *Hinweis: Admin-Variante: geheim vs. angekündigt.*
  <br>`party-3` · Rückspuler & Sabotage · Aufwand klein · HW ja · ★ 6 · V1 0/4
- **Sudden Death** — Bleiben zwei Spieler übrig, startet automatisch Sudden Death: steigende Geschwindigkeit, alle Ausgeschiedenen haben je einen Rückspuler und einen Boost. Alle Handys zeigen ein dramatisches Finale-Design. *Hinweis: Benötigt Ausscheiden-Meldungen.*
  <br>`party-40` · Spielmodi · Aufwand mittel · HW ja · ★ 6 · V1 0/4
- **Trinkspiel-Modus mit Regeln aus der Lobby** — Ein eigener Modus 'Party (18+)', der nach Rundenende Ansagen anzeigt: 'Wer ausgeschieden ist, trinkt einen Schluck', 'Der Saboteur verteilt 2 Schlucke'. Regeln sind eine wählbare Liste im UI. *Hinweis: Admin muss ihn freischalten; Standard aus.*
  <br>`party-33` · Trinkspiel · Aufwand mittel · HW ja · ★ 5 · V1 1/4
- **Chaos-Taste für den Spielleiter** — Der Spielleiter hat einen großen roten Chaos-Knopf: löst eine zufällige Kombination aus Boost, Bremse und kurzem Rückwärts aus. Einmal pro Runde, mit Countdown für alle.
  <br>`party-43` · Party-Moderation · Aufwand klein · HW ja · ★ 5 · V1 1/4
- **Ereigniskarten-Ziehen** — Alle 20–40 s erscheint auf allen Handys eine Ereigniskarte: 'Sturmböe' (Speed-Schwankungen), 'Windstille' (langsam), 'Looping-Rausch' (kurz Vollgas), 'Rückenwind' (mini-Rückwärts). Die Karte wird groß animiert, bevor sie wirkt. *Hinweis: Rückwärts-Karten müssen unter den globalen Grenzen bleiben.*
  <br>`party-10` · Ereigniskarten · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Glücksrad zwischen den Runden** — Nach jeder Runde dreht der Verlierer (oder Gewinner) auf dem Handy ein Glücksrad, das die Regel der nächsten Runde bestimmt: 'Nur Rückspuler', 'Doppelte Geschwindigkeit', 'Linke Hand', 'Augen zu für den Spielleiter' usw. *Hinweis: Physische Regeln (linke Hand) sind reine Ansagen, keine Technik.*
  <br>`party-12` · Ereigniskarten · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Modus-Wahl per Abstimmung in der Lobby** — Statt dass der Spielleiter wählt, schlägt das System 3 Modi vor und alle Handys stimmen 10 s lang ab. Bei Gleichstand entscheidet ein Zufallsrad.
  <br>`party-14` · Abstimmungen · Aufwand klein · HW ja · ★ 5 · V1 0/4
- **Team-Kapitän mit Fernsteuerung** — Pro Team spielt einer an der Wippe, der andere sitzt daneben mit dem Handy und setzt Rückspuler/Boosts ein. Rollen wechseln jede Runde. Kommunikation im Team wird zum Spiel.
  <br>`party-20` · Teams · Aufwand klein · HW ja · ★ 5 · V1 0/4
- **Rundenturnier mit Punktetabelle** — Mehrere Runden hintereinander, Punkte pro Platzierung. Die Lobby zeigt eine Tabelle, am Ende gibt es eine Siegerehrung mit Konfetti-Animation auf allen Handys. *Hinweis: Platzierung wird per Tipp vom Spielleiter oder den Spielern eingetragen.*
  <br>`party-23` · Party-Moderation · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Party-Moderator-Ansagen** — Ein Handy (z. B. am Lautsprecher) wird zum Moderator: Es spricht oder zeigt Ansagen wie 'Achtung, Rot ist in Gefahr!', 'Noch 10 Sekunden!', 'Wer hat da zurückgespult?'. Text-to-Speech im Browser. *Hinweis: Ton nur über Handys, die Platine hat keinen Lautsprecher. Web Speech API ist offline nicht auf allen Geräten verfügbar; Alternative vorab gespeicherte Sounds (Flash knapp).*
  <br>`party-25` · Party-Moderation · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Geheimer Saboteur** — Zu Rundenbeginn bekommt ein zufälliger Spieler heimlich einen Extra-Rückspuler. Nach der Runde stimmen alle ab, wer der Saboteur war. Richtig geraten: Saboteur verliert einen Punkt (oder trinkt), falsch: alle anderen. *Hinweis: Funktioniert nur, wenn Rückspuler anonym ausgelöst werden.*
  <br>`party-4` · Rückspuler & Sabotage · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Boost-Kombo** — Drücken zwei oder mehr Spieler innerhalb von 1 s gleichzeitig Boost, gibt es einen stärkeren Combo-Boost mit Effekt auf allen Handys ('DOPPEL-TURBO!'). Belohnt Absprachen und spontane Allianzen. *Hinweis: Turbo-Grenze aus Admin bleibt hart.*
  <br>`party-7` · Boosts · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Live-Abstimmung über die nächste Phase** — Mitten in der Runde poppt eine 5-s-Abstimmung auf: 'Schneller oder langsamer?' oder 'Rückwärtsstoß jetzt: ja/nein?'. Die Mehrheit entscheidet sofort. Zuschauer stimmen mit. *Hinweis: Spieler haben beide Hände an den Wippen; Abstimmen eher für Zuschauer und Ausgeschiedene.*
  <br>`party-13` · Abstimmungen · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Zuschauer-Wetten** — Vor der Runde setzen Zuschauer virtuelle Hühnerfedern auf den Spieler, der ihrer Meinung nach gewinnt. Am Ende Rangliste der besten Tipper. Optional: Quoten ändern sich nach Anzahl der Wetten. *Hinweis: Gewinner muss manuell eingetragen werden. Nur virtuelle Punkte, kein Geld.*
  <br>`party-16` · Zuschauer · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Pflicht-Pausen und Wasser-Runde** — Nach X Runden pausiert das Spiel automatisch, alle Handys zeigen 'Wasser-Pause – 2 Minuten'. Der Spielleiter kann verlängern, aber nicht überspringen (Admin-Einstellung).
  <br>`party-36` · Trinkspiel · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Energie-Leiste statt fester Kontingente** — Jeder Spieler hat eine Energie-Leiste, die sich langsam auflädt. Rückspuler kostet viel, Boost mittel, Zeitlupe wenig. Spieler entscheiden taktisch, wann sie was einsetzen. *Hinweis: Mehr UI-Komplexität; für Kinder evtl. zu abstrakt.*
  <br>`party-9` · Boosts · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Karte auf der Hand** — Jeder Spieler bekommt zu Rundenbeginn 3 zufällige Aktionskarten (Boost, Bremse, Rückspuler, Schild, Zeitlupe) und spielt sie per Wischgeste aus. Wie ein Kartenspiel parallel zum Brettspiel.
  <br>`party-11` · Ereigniskarten · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Teams 2 gegen 2** — Plätze werden zu zwei Teams zusammengefasst. Rückspuler und Boosts sind Team-Ressourcen, die auf dem Team-Handy geteilt sind. Ein Team verliert, wenn beide Spieler raus sind.
  <br>`party-19` · Teams · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Status-LED als Bühnenlicht** — Die Status-LED auf der Platine blinkt passend zum Spiel: Countdown-Blinken vor dem Start, schnelles Flackern bei Rückspulern, Dauerlicht beim Boost. Ein kleiner sichtbarer Hinweis im Spiel selbst. *Hinweis: Nur eine LED im Batteriefach, unter dem Spiel kaum sichtbar.*
  <br>`party-28` · UX & Design · Aufwand klein · HW eingeschränkt · ★ 3 · V1 0/4
- **Rache-Bonus** — Wer zurückgespult wurde, bekommt für 10 s einen Rache-Rückspuler, der nur gegen den Verursacher zählt (nach Ansage). Erzeugt kleine Fehden am Tisch. *Hinweis: Der Motor dreht für alle; 'gegen den Verursacher' ist nur Erzählung, physisch trifft es alle gleich.*
  <br>`party-31` · Rückspuler & Sabotage · Aufwand klein · HW eingeschränkt · ★ 3 · V1 0/4
- **Hebel-Geste als Tisch-Joker** — Wer ohne Handy spielt, kann über den Original-Hebel einen Effekt auslösen: zweimal schnell umlegen = Pause für alle (z. B. zum Nachfüllen der Getränke oder Chips sortieren). *Hinweis: Hebel trennt den Motor hardwareseitig; Gesten dürfen nicht mit Start/Stopp und Recovery-Gesten verwechselt werden.*
  <br>`party-32` · Party-Moderation · Aufwand mittel · HW eingeschränkt · ★ 3 · V1 0/4
- **Rückspuler kostet einen Schluck** — Im Trinkspiel-Modus darf man unbegrenzt zurückspulen, aber jeder Rückspuler kostet den Auslöser einen Schluck (bzw. alkoholfreie Aufgabe). Die Grenzen der Rückwärtsfahrt bleiben trotzdem aktiv.
  <br>`party-37` · Trinkspiel · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Ruhige Hände (Strom-Spionage)** — Wenn Louie blockiert wird (z. B. jemand hält das Flugzeug fest), steigt der Motorstrom. Das System erkennt das und ruft auf allen Handys 'Schummler!' aus, mit Strafe nach Regelwerk. *Hinweis: Nur grobes Blockieren erkennbar, wer es war, sieht die Elektronik nicht. Blockierschutz muss Motor ohnehin abschalten.*
  <br>`party-44` · Spielmodi · Aufwand mittel · HW eingeschränkt · ★ 3 · V1 0/4
- **Verräter-Modus** — Ein Teammitglied wird heimlich zum Verräter und arbeitet mit Rückspulern gegen das eigene Team. Wird er enttarnt, wechselt er das Team.
  <br>`party-21` · Teams · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Kopfgeld** — Zufällig wird ein Spieler zum 'Gejagten' erklärt (sein Huhn leuchtet auf allen Handys rot). Wer ihm einen Chip abnimmt, bekommt einen Bonus-Rückspuler. Fokussiert die Sabotage auf eine Person. *Hinweis: Chip-Verlust muss manuell gemeldet werden.*
  <br>`party-22` · Spielmodi · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Soundboard pro Spieler** — Jeder Spieler wählt einen Sieges- und einen Fluchsound. Bei Rückspulern spielt das Handy des Opfers einen Rücklauf-Sound ab. Kleine Sounddateien aus dem Flash. *Hinweis: Flash 4 MB: nur wenige, stark komprimierte Sounds. Alternativ per WebAudio synthetisiert.*
  <br>`party-26` · UX & Design · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Wahrheit oder Pflicht bei Chipverlust** — Wer einen Chip verliert, tippt es ein und bekommt eine Zufallskarte 'Wahrheit oder Pflicht'. Familien- und Erwachsenen-Kartendecks wählbar. *Hinweis: Kartentexte im Flash begrenzen, ggf. vom Admin hochladbar.*
  <br>`party-38` · Trinkspiel · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Auktion um Superkräfte** — Vor der Runde werden Superkräfte (Dreifach-Rückspuler, Schild, Mega-Boost) versteigert. Bezahlt wird mit Punkten aus vorigen Runden oder mit Schlucken im Trinkspiel.
  <br>`party-42` · Spielmodi · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Duell-Modus 1 gegen 1 per Handy** — Zwei Spieler halten je ein Handy, der Rest spielt an den Wippen. Die Handy-Duellanten bekämpfen sich mit Rückspulern und Boosts; wer am Ende den Favoriten am Tisch durchbringt, gewinnt.
  <br>`party-45` · Spielmodi · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Rückspul-Lotterie** — Statt dass Spieler gezielt zurückspulen, kaufen sie Lose. Zu einem zufälligen Zeitpunkt wird ein Los gezogen und dessen Besitzer darf einen Rückspuler auslösen. Weniger Reaktionsspiel, mehr Glück.
  <br>`party-46` · Rückspuler & Sabotage · Aufwand klein · HW ja · ★ 2 · V1 0/4
- **Rückspul-Konter (Schild)** — Wer gerade Opfer eines Rückspulers wird, kann innerhalb eines kurzen Fensters (ca. 0,3 s) einen Schild-Knopf drücken und den Stoß abbrechen. Ein Schild pro Runde. Fühlt sich an wie ein Reaktionsduell. *Hinweis: WLAN-Latenz am Handy (50–200 ms) macht das Fenster unfair; eher als 'Rückspuler wird mit kurzer Ankündigung verzögert' umsetzen.*
  <br>`party-2` · Rückspuler & Sabotage · Aufwand mittel · HW eingeschränkt · ★ 1 · V1 0/4
- **Live-Wetten während der Runde** — Zuschauer können während der Runde Mini-Wetten platzieren: 'Wer verliert als Nächstes einen Chip?' Wer richtig liegt, bekommt Punkte oder darf einen Boost auslösen. *Hinweis: Chip-Verluste muss jemand per Handy eintragen, sonst kein Auswerten möglich.*
  <br>`party-17` · Zuschauer · Aufwand groß · HW eingeschränkt · ★ 1 · V1 0/4
- **Schluck-Zähler mit Obergrenze** — Das UI zählt die Schlucke pro Spieler mit und erzwingt eine Pause oder Wasser-Runde, wenn eine einstellbare Grenze pro Stunde erreicht ist. Zeigt auch an, wie lange gespielt wurde. *Hinweis: Verantwortungsvolles Feature; Werte manuell bestätigt, nicht gemessen.*
  <br>`party-35` · Trinkspiel · Aufwand mittel · HW ja · ★ 1 · V1 0/4
- **Rhythmus-Modus zur Musik** — Ein Handy spielt Musik ab und gibt den Takt an den Server weiter; Louie wechselt zum Beat die Geschwindigkeit. Bei Drops gibt es kurze Boosts. *Hinweis: Beat-Erkennung im Browser aufwendig, Latenz zwischen Handy und Motor.*
  <br>`party-41` · Spielmodi · Aufwand groß · HW eingeschränkt · ★ 1 · V1 0/4

### 5.3 User Experience & Design (52)

- **Verbindungs-Ampel mit ehrlicher Sprache** — Oben rechts ein kleines Louie-Symbol: grün = verbunden, gelb blinkend = verbinde neu, rot = weg. Antippen zeigt Klartext ('Dein Handy hat das Louie-WLAN verlassen – wahrscheinlich, weil es kein Internet hat. Tippe hier, um zurückzukehren.') statt Fehlercodes.
  <br>`ux-28` · Fehler- und Verbindungsanzeigen · Aufwand klein · HW ja · ★ 11 · V1 4/4
- **Drei-Sekunden-Onboarding für Gäste** — Wer nur zuschaut, landet sofort auf einer Ansicht mit großem Status und einem einzigen Knopf 'Mitspielen'. Keine Menüs, kein Hamburger, keine Einstellungen sichtbar. Alles Weitere erscheint erst, wenn man eine Rolle hat (progressive Enthüllung).
  <br>`ux-6` · Bildschirmaufbau · Aufwand klein · HW ja · ★ 10 · V1 4/4
- **Spieler-Ansicht als Gamepad** — Während der Runde wird das Handy zum Ein-Knopf-Controller: oben schmaler Statusstreifen (Geschwindigkeit, Phase), Mitte ein riesiger Boost-Knopf mit Abklingring, darunter der Rückspuler-Knopf mit Kontingent-Punkten. Querformat optional, Knopf immer unter dem Daumen. Nichts, was man versehentlich wegwischt. *Hinweis: Ohne Wake Lock geht der Bildschirm aus – Hinweis 'Bildschirm-Timeout verlängern' oder Trick mit stummem Video-Loop prüfen.*
  <br>`ux-7` · Spieler-Ansicht · Aufwand mittel · HW ja · ★ 10 · V1 4/4
- **Countdown-Ritual vor dem Start** — Wenn der Spielleiter freigibt, zählen alle Handys synchron 3-2-1 mit großem Zahlen-Zoom und Propeller-Anlaufgeräusch, der Motor startet mit sanfter Rampe genau auf 'Los'. Macht jede Runde zum Event. *Hinweis: Gilt nur bei 'Start nach Freigabe'; bei Hebel-direkt-Start kurzer Ersatz-Jingle.*
  <br>`ux-34` · Animation / Sound · Aufwand klein · HW ja · ★ 10 · V1 4/4
- **Wiederverbinden mit Platzgarantie** — Wenn ein Handy kurz wegfällt (Bildschirm aus, WLAN gewechselt), bleibt sein Huhn 60 s reserviert und auf den anderen Handys halbtransparent mit Sanduhr. Beim Zurückkehren 'Willkommen zurück, Federico!' und alles ist wie vorher. *Hinweis: Baut auf dem geplanten Sitzungstoken auf.*
  <br>`ux-40` · Fehler- und Verbindungsanzeigen · Aufwand klein · HW ja · ★ 10 · V1 4/4
- **Lobby-QR auf dem Handy des Spielleiters** — Der Spielleiter tippt 'Freunde einladen' und sein Handy zeigt bildschirmfüllend den WLAN-QR und danach den Steuerungs-QR. Neue Mitspieler scannen einfach das Handy statt unter dem Spiel nach dem Aufkleber zu suchen. Wechselt automatisch alle 4 s zwischen beiden Codes. *Hinweis: QR-Generator muss als kleine JS-Datei offline im Flash liegen (ca. 5–10 KB); WLAN-Passwort wird dabei sichtbar, Admin-Schalter zum Abschalten.*
  <br>`ux-2` · Onboarding / Beitreten · Aufwand klein · HW ja · ★ 10 · V1 2/4
- **Vorwarnung vor Rückwärtsstoß** — 0,5 s bevor ein (geplanter oder per Rückspuler ausgelöster) Rückwärtsstoß greift, färbt sich bei allen Handys der Rand rot und es ertönt ein 'Piep-Piep' wie beim rückwärtsfahrenden LKW. Gibt den Opfern eine winzige Chance und macht Rückwärts weniger frustrierend. *Hinweis: Verzögerung muss serverseitig eingeplant werden; WLAN-Latenz kann die Vorwarnung schrumpfen lassen. Optional als Admin-Schalter.*
  <br>`ux-22` · Sound / Haptik · Aufwand klein · HW ja · ★ 9 · V1 4/4
- **Captive-Portal-Rettungsseite mit Daumen-Animation** — Die Portalseite zeigt nur einen riesigen Knopf 'Im Browser öffnen' und eine animierte Hand, die bei iOS/Android jeweils den richtigen Weg zeigt ('Ohne Internet verbunden bleiben' antippen). Erkennt das Betriebssystem am User-Agent und zeigt nur die passende Anleitung. *Hinweis: Verhalten der Portal-Browser ändert sich mit OS-Versionen; im Prototyp mit echten Geräten prüfen.*
  <br>`ux-3` · Onboarding / Beitreten · Aufwand mittel · HW ja · ★ 9 · V1 3/4
- **Huhn wählen statt Platz wählen** — Beim Beitreten sieht man das Spielbrett von oben als Illustration mit vier Hühnern in den Originalfarben. Man tippt auf 'sein' Huhn, das gackert kurz und hüpft. Bereits vergebene Hühner tragen den Spitznamen bzw. das Emoji des Besitzers und sind ausgegraut. *Hinweis: Farben je Modell (Louie alt/neu, Chewie) unterschiedlich – Farbpalette pro Modellprofil hinterlegen.*
  <br>`ux-4` · Onboarding / Beitreten · Aufwand klein · HW ja · ★ 9 · V1 2/4
- **Halten-zum-Auslösen für mächtige Aktionen** — Rückspuler und andere starke Eingriffe lösen erst nach kurzem Gedrückthalten (ca. 300 ms) mit sich füllendem Ring aus. Verhindert Fehlauslösung in der Hosentasche und macht den Moment dramatischer. Boost bleibt ein schneller Tipp.
  <br>`ux-9` · Spieler-Ansicht / Haptik · Aufwand klein · HW ja · ★ 8 · V1 4/4
- **Ein QR für alles (Aufkleber-Duo als Bild-Story)** — Der Aufkleber zeigt nicht nur zwei nackte QR-Codes, sondern eine kleine Comic-Leiste: 1. Louie winkt ins WLAN, 2. Louie zeigt aufs Steuerpult. Kinder verstehen die Reihenfolge ohne Text, Erwachsene scannen einfach nacheinander. Optional ein dritter Mini-QR 'Hilfe', der eine im Flash liegende Anleitungsseite öffnet. *Hinweis: Hilfe-QR funktioniert nur, wenn man schon im Louie-WLAN ist; Druckqualität bei kleinem Aufkleber testen.*
  <br>`ux-1` · Onboarding / Beitreten · Aufwand klein · HW ja · ★ 8 · V1 3/4
- **Selbstmeldung 'Ich bin raus' mit Bestätigung** — Spieler können selbst 'Mein letzter Chip ist weg' wischen; der Spielleiter bekommt einen kleinen Bestätigungs-Toast. Nimmt dem Spielleiter Arbeit ab und funktioniert auch ohne Spielleiter (dann gilt die Selbstmeldung direkt). *Hinweis: Mogeln möglich – als Party-Feature eher Feature als Bug.*
  <br>`ux-13` · Spieler-Ansicht · Aufwand klein · HW ja · ★ 8 · V1 2/4
- **Namenswürfel für Spitznamen** — Statt Tastatur gibt es einen Würfel-Knopf, der lustige Hühnernamen generiert ('Gackerline', 'Federico', 'Rührei-Rudi'). Kinder ohne Lese-/Schreibkenntnis kommen so ohne Tippen ins Spiel, Erwachsene können überschreiben. Im Trinkspiel-Modus andere Wortliste ('Eierlikör-Eddi'). *Hinweis: Wortlisten klein halten (wenige KB).*
  <br>`ux-5` · Onboarding / Kinderfreundlichkeit · Aufwand klein · HW ja · ★ 8 · V1 1/4
- **Hebel-Spiegel im UI** — Das UI zeigt den echten Hebel als großen Kippschalter-Grafik, der sich live mitbewegt. Bei Fehlbedienung (Hebel steht beim Aufwecken auf An) wackelt die Grafik und zeigt die Richtung, in die man ihn legen muss. Bei Hebel-Gesten werden die Umlegungen live mitgezählt ('3 von 5 – weiter so'). *Hinweis: Hebel trennt den Motor in Reihe – ob die Elektronik den Hebelzustand bei getrenntem Motor sicher erkennt, hängt von der Schaltung ab (laut Konzept vorgesehen).*
  <br>`ux-30` · Fehler- und Verbindungsanzeigen / Onboarding · Aufwand klein · HW ja · ★ 7 · V1 2/4
- **Sieger-Konfetti und Ehrenrunde** — Wenn nur noch ein Huhn übrig ist und der Spielleiter das bestätigt, regnet es auf allen Handys Konfetti in der Siegerfarbe, das Großbild zeigt das Siegerhuhn mit Krone, und Louie dreht eine langsame Ehrenrunde, bevor er stoppt. *Hinweis: Ehrenrunde nur wenn Hebel noch an ist.*
  <br>`ux-35` · Animation · Aufwand klein · HW ja · ★ 7 · V1 1/4
- **Rückwärts-Budget sichtbar machen** — Ein kleiner gemeinsamer Balken für alle zeigt, wie viel Rückwärtsanteil der Runde (z. B. 10 %) schon verbraucht ist. Ist er leer, sind alle Rückspuler grau mit Hinweis 'Louie hat genug vom Rückwärtsfliegen'. Macht die serverseitigen Grenzen verständlich statt frustrierend.
  <br>`ux-48` · Spieler-Ansicht / Fehleranzeigen · Aufwand klein · HW ja · ★ 7 · V1 1/4
- **Spielleiter-Cockpit** — Der Spielleiter sieht oben eine Live-Kurve der Geschwindigkeit (letzte 30 s) mit markierten Rückwärtsstößen und Boosts, darunter vier Hühner-Kacheln zum Antippen 'ausgeschieden', unten breite Pause- und Stopp-Leiste. Wichtige Aktionen in Daumenreichweite, Stopp knallrot und mit Bestätigung durch Wischen. *Hinweis: Stopp im UI ist Software; echter Not-Aus bleibt der Hebel – UI sollte das ehrlich anzeigen.*
  <br>`ux-10` · Spielleiter-Ansicht · Aufwand mittel · HW ja · ★ 7 · V1 0/4
- **Nur ein Handy macht Lärm** — Damit nicht sechs Handys gleichzeitig gackern, gibt es eine Rolle 'Lautsprecher': Standardmäßig spielt nur das Großbild oder der Spielleiter Sound, Spieler-Handys geben nur ihre eigenen Rückmeldungen leise wieder. Umschaltbar im Lobby-Menü.
  <br>`ux-20` · Sound / Ansagen · Aufwand klein · HW ja · ★ 7 · V1 0/4
- **Status-LED-Alphabet** — Klar definierte Muster für die eine Status-LED: Herzschlag (doppelt kurz, Pause) = bereit im WLAN, langsames Atmen = Hotspot aktiv, schnelles Flackern = Fehler, Morse-artiges 'kurz-lang' = wartet auf Hebel-Bestätigung, dreimal Aufblitzen = Hebel-Geste erkannt, Glimmen = Akku schwach. Auf dem QR-Aufkleber ist eine Mini-Legende aufgedruckt. *Hinweis: Nur eine einfarbige LED – alles muss über Rhythmus und Helligkeit (PWM) laufen, nicht über Farbe.*
  <br>`ux-31` · Status-LED-Sprache · Aufwand klein · HW ja · ★ 6 · V1 2/4
- **Eltern-Bremse** — Im Kindermodus begrenzt ein eigener Regler die Höchstgeschwindigkeit und deaktiviert Rückspuler/Rückwärts komplett. Sichtbar durch ein kleines Schnuller-Symbol im Status, damit Erwachsene verstehen, warum alles gemütlicher ist. *Hinweis: Durchsetzen muss der Server über die vorhandenen Grenzwerte, nicht das UI.*
  <br>`ux-25` · Kinderfreundlichkeit · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Freundliche Fehler-Comics** — Jeder bekannte Fehlerzustand hat eine Mini-Illustration mit Louie: 'Hebel steht auf An' (Louie zeigt auf den Hebel), 'Akku schwach' (Louie schwitzt), 'Motor blockiert' (Louie hängt in einer Wippe fest), 'Treiberfehler' (Louie mit Schraubenschlüssel). Jeweils ein konkreter nächster Schritt. *Hinweis: Motor-blockiert-Erkennung über Strommessung ist möglich, Schwellen müssen am Prototyp kalibriert werden; Grafiken als SVG klein halten.*
  <br>`ux-29` · Fehler- und Verbindungsanzeigen · Aufwand mittel · HW ja · ★ 6 · V1 1/4
- **Bildschirm-bleibt-an-Hilfe** — Da Wake Lock ohne HTTPS fehlt, zeigt das UI beim ersten Spielen einen kurzen Tipp, wie man die Display-Zeit verlängert, und testet optional den Trick mit einem stummen, unsichtbaren Video-Loop, der viele Handys wach hält. *Hinweis: Video-Trick ist browserabhängig und kostet Handy-Akku; das Video muss im Flash liegen (sehr klein halten).*
  <br>`ux-41` · Fehler- und Verbindungsanzeigen / UX · Aufwand klein · HW eingeschränkt · ★ 6 · V1 1/4
- **Ausgeschieden-Bildschirm mit Rachefunktion** — Wer ausscheidet, sieht ein Huhn mit Pflaster und einen Fake-Trauerflor, dann wechselt der Bildschirm in den 'Geister-Modus' mit halbtransparentem Design und Boost-/Rückspul-Knöpfen (falls der Modus das erlaubt). Ausscheiden wird so zum Rollenwechsel statt zum Rausfliegen. *Hinweis: Ausscheiden muss der Spielleiter oder der Spieler selbst melden – die Elektronik sieht keine Chips.*
  <br>`ux-12` · Spieler-Ansicht / Animation · Aufwand mittel · HW ja · ★ 6 · V1 0/4
- **Zuschauer-Großbild (TV/Tablet-Modus)** — Eine eigene Ansicht /tv für ein Tablet oder einen Laptop am Fernseher: großer animierter Louie, der in Echtzeit mit der echten Geschwindigkeit und Richtung kreist, vier Hühner mit Chipstand, Event-Ticker ('Anna boostet!', 'Rudi spult zurück!'), Rundenzeit. Kein Bedienelement, nur Show. *Hinweis: Jeder TV-Client zählt als WebSocket-Verbindung; Smart-TV-Browser oft schwach – Tablet/Laptop als Ziel.*
  <br>`ux-15` · Zuschauer-Großbild · Aufwand mittel · HW ja · ★ 6 · V1 0/4
- **Hühnerfarben mit Muster für Farbenblinde** — Jede Hühnerfarbe bekommt zusätzlich ein Symbol oder Muster (Punkte, Streifen, Stern, Herz) und eine Form der Kachel. Rot/Grün-Schwäche ist so kein Problem, und Kinder können 'Ich bin das Sternhuhn' sagen.
  <br>`ux-23` · Farben / Barrierefreiheit · Aufwand klein · HW ja · ★ 6 · V1 0/4
- **Geschwindigkeits-Tacho als Hühnerstress-Barometer** — Statt Prozentanzeige ein Thermometer mit Hühnergesichtern: entspannt, nervös, panisch, Federn fliegen. Bei Rückwärtsfahrt dreht sich die Skala sichtbar um. Kinder verstehen Geschwindigkeit ohne Zahlen.
  <br>`ux-36` · Design / Kinderfreundlichkeit · Aufwand klein · HW ja · ★ 6 · V1 0/4
- **Akku-Anzeige als Louie-Tankanzeige** — Akkustand der Platine als Tankuhr am Flugzeug: voll, halb, Reserve. Bei Reserve sagt die Ansage 'Louie muss bald tanken – noch etwa 2 Runden'. Schätzung aus mittlerer Leistungsaufnahme pro Runde. *Hinweis: Rundenschätzung ungenau, als grobe Angabe kennzeichnen.*
  <br>`ux-42` · Fehler- und Verbindungsanzeigen / Design · Aufwand klein · HW ja · ★ 5 · V1 2/4
- **Schlaf-Bildschirm mit schnarchendem Louie** — Geht das Gerät in Schlaf, zeigen alle Handys einen schnarchenden Louie und 'Hebel umlegen zum Wecken'. Eine Minute vorher fragt ein gähnender Louie 'Noch eine Runde?' mit großem 'Wach bleiben'-Knopf.
  <br>`ux-50` · Animation / Fehleranzeigen · Aufwand klein · HW ja · ★ 5 · V1 1/4
- **Rückspuler als Kassetten-Knopf** — Der Rückspul-Knopf sieht aus wie eine alte Kassetten-Taste mit Doppelpfeil. Beim Drücken spult eine kleine Bandanimation zurück, auf allen anderen Handys erscheint kurz ein VHS-Rauschen mit dem Namen des Übeltäters ('Rudi spult zurück!'). Kontingent als kleine Kassetten-Symbole, Abklingzeit als sich füllendes Band. *Hinweis: Server entscheidet über Erfolg; UI muss 'abgelehnt (Abklingzeit/global gesperrt)' sauber anzeigen.*
  <br>`ux-8` · Spieler-Ansicht / Animation · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Rollen-Farbcode im ganzen UI** — Jede Rolle hat eine Rahmenfarbe am Bildschirmrand: Gast grau, Spieler in der eigenen Hühnerfarbe, Spielleiter golden, Admin violett mit Schloss. Man sieht auf einen Blick, wessen Handy welche Macht hat – hilft auch beim Übergeben des Handys.
  <br>`ux-11` · Bildschirmaufbau · Aufwand klein · HW ja · ★ 5 · V1 0/4
- **Chip-Zähler per Antippen** — Jeder Spieler hat auf dem Handy drei Hühnerchip-Symbole und tippt einen weg, wenn er einen verliert. Das ergibt Live-Stand und Statistik, ohne Sensorik. Auf dem Großbild sieht man alle Chips aller Spieler. *Hinweis: Rein manuell; die Hardware erkennt Chipverluste nicht. Vergessene Eingaben verfälschen die Statistik.*
  <br>`ux-14` · Spieler-Ansicht · Aufwand klein · HW eingeschränkt · ★ 5 · V1 0/4
- **Ansager-Stimme über die Handys** — Das Handy des Spielleiters (oder das Großbild) sagt per Sprachsynthese an: 'Drei, zwei, eins – Louie hebt ab!', 'Achtung, Rückwärtsgang!', 'Gelb ist raus!'. Mehrere Stimm-Persönlichkeiten: Sportreporter, Flughafen-Durchsage, Bauernhof-Opa. *Hinweis: Web Speech API klingt je Gerät verschieden, braucht auf iOS eine Nutzergeste zum Freischalten; offline-Stimmen nicht auf allen Geräten vorhanden.*
  <br>`ux-18` · Sound / Ansagen · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Synthetische Soundeffekte statt Audiodateien** — Propellerbrummen, Gackern, Rückspul-Quietschen und Boost-Zischen werden per Web Audio API im Browser erzeugt (Oszillatoren, Rauschen). Spart Flash und klingt bewusst retro. Das Propellergeräusch folgt der echten Geschwindigkeit in der Tonhöhe. *Hinweis: Flash-Budget ~100 KB komprimiert spricht gegen Samples; Web Audio braucht Nutzergeste zum Start.*
  <br>`ux-19` · Sound / Ansagen · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Screenreader- und Großschrift-Unterstützung** — Saubere ARIA-Labels, Live-Regionen für Ansagen ('Runde läuft, Geschwindigkeit hoch'), respektiert Systemschriftgröße und 'Bewegung reduzieren'. Wer reduzierte Bewegung eingestellt hat, bekommt keine wackelnden Animationen und kein Bildschirmflackern.
  <br>`ux-26` · Barrierefreiheit · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Gleichzeitige Rückspuler als Kollisions-Gag** — Drücken zwei Spieler fast gleichzeitig den Rückspuler, zählt nur einer (laut Konzept nicht addiert). Das UI macht daraus einen Gag: 'Bandsalat! Gelb war schneller', der Verlierer bekommt seinen Rückspuler zurück. *Hinweis: Rückgabe des Kontingents ist eine Spielregel-Entscheidung.*
  <br>`ux-49` · Spieler-Ansicht / Animation · Aufwand klein · HW ja · ★ 5 · V1 0/4
- **Vibrations-Sprache (Android) mit iOS-Ersatz** — Kurz-kurz = Boost bereit, lang = Rückwärtsstoß kommt, dreifach = du bist dran beim Partyspiel. Auf iOS, wo Vibration im Browser fehlt, blitzt stattdessen der Bildschirmrand in der Hühnerfarbe und es klickt leise. *Hinweis: navigator.vibrate geht nur auf Android; iOS-Ersatz rein visuell/akustisch.*
  <br>`ux-21` · Haptik · Aufwand klein · HW eingeschränkt · ★ 4 · V1 1/4
- **Kindermodus: Bilder statt Text** — Ein Schalter in der Lobby macht das UI bilderbasiert: Icons statt Wörter, größere Knöpfe (≥ 72 px), keine Zahlen, nur 'langsam/schnell'-Schnecke-Rakete-Skala, keine Abbruch-Dialoge mit Kleingedrucktem. Gefährliche Menüs (Admin, Modus-Editor) komplett ausgeblendet.
  <br>`ux-24` · Kinderfreundlichkeit · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Handy weitergeben-Modus** — Für Runden mit nur einem oder zwei Handys: Das UI wechselt nach jeder Aktion auf einen Bildschirm 'Gib das Handy an Grün weiter' mit großem Farbbanner. Ein Handy reicht so für alle Spieler.
  <br>`ux-39` · Bildschirmaufbau · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Erstes-Mal-Tutorial als Probeflug** — Beim ersten Öffnen bietet das UI einen 30-Sekunden-Probeflug: Louie fliegt langsam, das Handy erklärt mit Sprechblasen 'Das ist dein Boost – probier ihn!', 'Das ist der Rückspuler – nur sparsam!'. Danach ein Häkchen 'Kenne ich schon' pro Gerät im localStorage. *Hinweis: Braucht Hebel an; Rückspuler-Demo in Mini-Dosis innerhalb der Rückwärts-Grenzen.*
  <br>`ux-43` · Onboarding · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Emoji-Reaktionen in Echtzeit** — Spieler und Zuschauer können Emojis werfen (Huhn, Lachen, Wut, Bier), die auf dem Großbild über den Bildschirm fliegen. Ratenbegrenzt, damit der ESP nicht geflutet wird. *Hinweis: Jede Reaktion ist eine WebSocket-Nachricht; serverseitig drosseln (z. B. 1 pro 2 s pro Client).*
  <br>`ux-45` · Zuschauer-Großbild / Party · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Sprache und Ton pro Gerät merken** — Jedes Handy merkt sich Lautstärke, Ansager-Stimme, Kindermodus, Kontrast und Hand (Links-/Rechtshänder, spiegelt Knopf-Anordnung) lokal. Kein Konto nötig, aber beim nächsten Abend ist alles wie gewohnt. *Hinweis: localStorage kann im privaten Modus leer sein – UI muss ohne funktionieren.*
  <br>`ux-46` · Barrierefreiheit / UX · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Druckbare Spielkarte mit Legende** — Im UI lässt sich eine A6-Karte zum Ausdrucken öffnen: QR-Codes, LED-Muster-Legende, Hebel-Gesten (5× = Hotspot, 10× = Passwort-Reset) und Notfall-Tipps. Liegt dann in der Spielschachtel. *Hinweis: Hebel-Gesten-Info nicht offen auf die Karte, wenn Kinder den Reset nicht kennen sollen – Admin-Option.*
  <br>`ux-52` · Onboarding / Barrierefreiheit · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Hoher-Kontrast- und Partylicht-Modus** — Ein Modus mit extrem großen Zahlen und Schwarz/Gelb für schummrige Partyräume, plus ein 'Discomodus', bei dem der Handybildschirm im Takt der Motorgeschwindigkeit in der Hühnerfarbe pulsiert und als Tischbeleuchtung dient. *Hinweis: Discomodus: Warnhinweis für Fotosensitivität, Blinkfrequenz begrenzen.*
  <br>`ux-27` · Design / Barrierefreiheit · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Ereignis-Ticker mit Schadenfreude-Statistik** — Am Rundenende zeigt jedes Handy eine kleine Karte: 'Du hast 2× zurückgespult, Anna hat danach einen Chip verloren (vielleicht wegen dir)'. Verbindung aus Zeitstempeln von Rückspuler und gemeldetem Chipverlust, mit Augenzwinkern formuliert. *Hinweis: Kausalität ist geraten, da Chipverluste nur manuell gemeldet werden.*
  <br>`ux-44` · Spieler-Ansicht / Party · Aufwand mittel · HW eingeschränkt · ★ 3 · V1 0/4
- **Mehrere Louies im Raum unterscheiden** — Wenn zwei Spiele im Raum sind (louie-a3f2, louie-91bc), bekommt jedes Gerät automatisch einen Namen und eine Akzentfarbe ('Louie Blau', 'Chewie Orange'). Ein Knopf 'Welcher bin ich?' lässt die Status-LED des gewählten Geräts wild blinken.
  <br>`ux-51` · Onboarding / Status-LED-Sprache · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **LED zählt Spieler mit** — Beim Beitreten eines Handys blinkt die LED so oft, wie Spieler verbunden sind. So merkt man am Tisch ohne Blick aufs Handy, dass 'der Neue' drin ist. *Hinweis: LED sitzt im Batteriefach – Sichtbarkeit im eingebauten Zustand prüfen (ggf. Lichtleiter).*
  <br>`ux-32` · Status-LED-Sprache · Aufwand klein · HW ja · ★ 2 · V1 0/4
- **Themen-Skins je Modell** — Je nach Modellprofil ändert sich das ganze UI: Louie alt = Bauernhof in Pastell, Louie neu = knallig-modern, Chewie = Weltraum mit Sternen und Laser-Sounds. Später freischaltbare Skins (Halloween, Weihnachten, Oktoberfest). *Hinweis: Kein Markenmaterial einbauen (Rechte); eigene Illustrationen. Flash-Budget im Blick behalten.*
  <br>`ux-37` · Design · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Trinkspiel-Haube** — Ein Admin- oder Spielleiter-Schalter blendet eine Trinkspiel-Schicht ein: beim Rückspuler erscheint auf dem Handy des Verursachers 'Prost auf deine Gemeinheit', bei Chipverlust ein Becher-Symbol. Optisch abgedunkeltes 'Bar'-Design. Im Kindermodus ist die Haube gesperrt und unsichtbar. *Hinweis: Verantwortungsvolle Formulierung, alkoholfreie Alternative ('Wasser/Schluck/Strafaufgabe') gleichberechtigt anbieten.*
  <br>`ux-38` · Design / Party · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Admin-Bereich als 'Hangar'** — Der Admin-Bereich ist optisch klar abgesetzt als Flugzeughangar mit Werkzeugwand: jede Kachel ein Werkzeug (WLAN-Antenne, Tacho für Grenzen, Rückwärtsgang-Hebel, Batterie). Kritische Einstellungen haben ein gelb-schwarzes Warnband und erklären in einem Satz, was passiert.
  <br>`ux-47` · Bildschirmaufbau / Design · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Großbild-Wiederholung des letzten Rückwärtsstoßes** — Nach jedem Rückspuler zeigt das Großbild eine kurze Zeitlupen-Animation des simulierten Louie inkl. Name des Verursachers und Kommentatorstimme. Die Elektronik liefert nur Zeit und Richtung, die Animation ist komplett im Browser berechnet. *Hinweis: Animation ist Simulation, nicht echte Flugzeugposition – die Elektronik kennt die Position nicht.*
  <br>`ux-16` · Zuschauer-Großbild / Animation · Aufwand mittel · HW ja · ★ 1 · V1 0/4
- **Louie-Position schätzen (Umdrehungszähler aus Strom)** — Das Großbild zeigt Louie an einer geschätzten Position, abgeleitet aus Geschwindigkeit und Zeit, eventuell korrigiert durch Stromspitzen, wenn das Flugzeug eine Wippe trifft. Wirkt live, ist aber nur eine Näherung. *Hinweis: Ohne Positionssensor driftet die Schätzung; Stromspitzen-Erkennung ist unsicher und müsste erst am Prototyp erforscht werden.*
  <br>`ux-17` · Zuschauer-Großbild · Aufwand groß · HW eingeschränkt · ★ 0 · V1 0/4
- **Motor als Lautsprecher und Signalgeber** — Der Motor 'zuckt' als Feedback ohne Handy: zwei kurze Ruckler = WLAN verbunden, ein langes Summen per hörbarer PWM-Frequenz = Fehler. Mit tieffrequenter PWM kann der Motor sogar leise Töne pfeifen (Startmelodie beim Einschalten). *Hinweis: Funktioniert nur bei Hebel an (Motor in Reihe mit dem Hebel); hörbare PWM erhöht Verluste – nur kurz einsetzen.*
  <br>`ux-33` · Status-LED-Sprache / Haptik · Aufwand mittel · HW eingeschränkt · ★ 0 · V1 0/4

### 5.4 Besitzer- und Admin-Einstellungen (41)

- **Tempo-Deckel als großer Schieberegler** — Ein einziger, prominenter Regler "Maximal so schnell" mit Vorschau-Animation des Fliegers, der alles andere (Modi, Boosts, Turbo) nach oben begrenzt. Darunter ein Satz in Klartext, z. B. "Louie fährt höchstens wie im Original". Eltern verstehen das sofort, ohne Volt oder Prozent. *Hinweis: Technisch nur eine Umrechnung auf die bestehenden Grenzwerte; Kalibrierung pro Modell nötig.*
  <br>`besitzer-3` · Profile & Grenzen · Aufwand klein · HW ja · ★ 8 · V1 3/4
- **QR-Code-Wand: Einladung auf dem Handy teilen** — Ein Admin- oder Spielleiter-Bildschirm zeigt riesig die zwei QR-Codes (WLAN beitreten, Steuerung öffnen) plus Kurzanleitung, damit man das Handy einfach in die Tischmitte legen kann. Optional mit Platzwahl-Link, der direkt Platz 3 reserviert. *Hinweis: QR-Erzeugung im Browser per kleiner JS-Bibliothek, offline im Flash.*
  <br>`besitzer-14` · WLAN & Netzwerk · Aufwand klein · HW ja · ★ 7 · V1 2/4
- **Profil-Schnellwahl: Kinder / Familie / Party / Erwachsene** — Vier große Kacheln im Admin-Bereich stellen mit einem Tipp ein ganzes Paket um: Geschwindigkeitsbereich, Rückwärts-Grenzen, Rückspuler-Kontingent, erlaubte Modi und ob Trinkspiel-Inhalte sichtbar sind. Der Besitzer muss nicht 30 Regler kennen, sondern wählt nur "Heute kommen die Nichten". Einzelwerte lassen sich danach trotzdem anpassen und das Paket als eigenes Profil speichern. *Hinweis: Baut auf den vorhandenen Admin-Grenzen auf; braucht klare Regel, was ein Profil überschreibt und was nicht.*
  <br>`besitzer-1` · Profile & Grenzen · Aufwand mittel · HW ja · ★ 7 · V1 1/4
- **Blockierschutz mit einstellbarer Empfindlichkeit** — Steigt der Motorstrom stark an (Finger, Arm verkeilt, Kind hält den Flieger fest), stoppt der Motor sofort und meldet das im UI. Der Besitzer stellt die Empfindlichkeit ein und ob danach automatisch weitergefahren oder auf Freigabe gewartet wird. Im Kinderprofil immer streng. *Hinweis: Wichtig auch gegen Überhitzung von Motor und H-Brücke; Rückwärtsstöße und Anlauf erzeugen ebenfalls Stromspitzen, Schwelle muss das unterscheiden.*
  <br>`besitzer-23` · Hardware-Sicherheit · Aufwand mittel · HW ja · ★ 7 · V1 1/4
- **Akku-Schutzeinstellungen** — Admin sieht Akkuzustand mit Ladezyklen-Schätzung und stellt Unterspannungs-Warnung, sanftes Rundenende und Abschaltschwelle ein. Option "Akkuschonend": Turbo nur oberhalb einer Mindestspannung, damit der Akku nicht leergesaugt wird und kein Brownout den ESP neu startet. *Hinweis: Abschaltschwelle nach unten hart begrenzen, damit LiPo nicht tiefentladen werden kann.*
  <br>`besitzer-24` · Hardware-Sicherheit · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Not-Aus-Knopf auf jedem Handy** — Admin kann einschalten, dass jedes verbundene Handy (nicht nur Spielleiter) einen roten Stopp-Knopf hat. Missbrauch wird protokolliert, und nach einem Stopp startet die Runde erst wieder über den Hebel. Im Kinderprofil standardmäßig an. *Hinweis: Hebel bleibt der eigentliche, softwareunabhängige Not-Aus.*
  <br>`besitzer-26` · Hardware-Sicherheit · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Trinkspiel-Freischaltung mit Altersbestätigung** — Trinkspiel-Inhalte (Regeln, Strafansagen, Modus-Texte) sind standardmäßig unsichtbar. Der Admin schaltet sie bewusst frei, bestätigt "alle Teilnehmenden sind volljährig" und kann sie an ein Ortsprofil oder Zeitfenster binden. Im Kinderprofil ist die Freischaltung nicht möglich. *Hinweis: Reine Selbstauskunft, kein echter Altersnachweis; ehrlich so kommunizieren.*
  <br>`besitzer-27` · Jugendschutz · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Spieler sperren oder rauswerfen** — Admin oder Spielleiter sieht alle verbundenen Handys (Spitzname, Platz, Verbindungszeit) und kann einzelne Sitzungen trennen, stummschalten (keine Boosts/Rückspuler) oder für den Abend sperren. Hilft gegen den einen Gast, der vom Sofa aus nur trollt. *Hinweis: Sperre nur pro Token, umgehbar durch Cookie löschen; für Spielzeug ausreichend.*
  <br>`besitzer-32` · Rechte & Rollen · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Gerätename und Persönlichkeit** — Der Besitzer gibt seinem Gerät einen Namen ("Louie vom Dachboden", "Chewie der Zweite"), ein Emoji und eine Hauptfarbe für das UI. Daraus werden Hotspot-Name, mDNS-Name (louie-dachboden.local) und Begrüßungstext abgeleitet. Bei mehreren Geräten auf einer Party sieht man sofort, welches welches ist. *Hinweis: Namen für SSID/Hostname auf erlaubte Zeichen einschränken.*
  <br>`besitzer-10` · Personalisierung · Aufwand klein · HW ja · ★ 4 · V1 1/4
- **Rückwärts-Budget als sichtbares Konto** — Statt drei abstrakter Grenzwerte (Dauer, Abstand, Anteil) sieht der Besitzer ein "Rückwärts-Konto pro Runde", z. B. 6 Sekunden, das Modus-Zufall und alle Rückspuler gemeinsam aufbrauchen. Im Spiel zeigt ein kleiner Balken, wie viel noch übrig ist. Das macht die Begrenzung für alle nachvollziehbar und fair. *Hinweis: Variante: getrennte Konten für Modus und Spieler.*
  <br>`besitzer-4` · Rückwärts & Rückspuler · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Rückspuler-Feintuning für Gastgeber** — Eigene Admin-Seite nur für den Rückspuler: Kontingent pro Spieler, Abklingzeit pro Spieler und global, Stoßlänge (0,3–1 s), ob Ausgeschiedene spulen dürfen, ob man sich selbst nach einem Rückspuler kurz schützen kann (Immunität), und ob zwei gleichzeitige Spuler sich gegenseitig aufheben. Als Vorlagen: "sanft", "gemein", "Chaos". *Hinweis: Richtungswechsel brauchen immer Rampe; sehr kurze Stöße (<0,3 s) evtl. mechanisch kaum spürbar, im Prototyp testen.*
  <br>`besitzer-5` · Rückwärts & Rückspuler · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Letzte-Runde-Knopf für Eltern** — Ein Admin- oder Spielleiter-Knopf "Das ist die letzte Runde" kündigt das Ende auf allen Handys groß an und sperrt danach neue Starts für eine einstellbare Zeit. Spart Diskussionen am Abend, weil das Spiel und nicht die Eltern Schluss sagt.
  <br>`besitzer-7` · Zeit & Ruhe · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Sicheres Update mit Rückfall** — Updates landen in einer zweiten Partition; startet die neue Firmware nicht sauber oder meldet der Admin innerhalb von 5 Minuten nicht "funktioniert", springt das Gerät automatisch auf die alte Version zurück. Zusätzlich Update nur bei ausreichendem Akku und Hebel aus. *Hinweis: 4 MB Flash reicht für zwei Partitionen plus Dateisystem nur knapp; Partitionierung früh festlegen.*
  <br>`besitzer-20` · Updates & Wartung · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Alkoholfrei-Schalter und Ersatzaufgaben** — Im Trinkspiel-Modus kann jeder Spieler für sich "alkoholfrei" wählen; Strafen werden dann zu Wasser, Saft, Kniebeugen oder lustigen Aufgaben. Der Besitzer kann festlegen, dass alkoholfrei der Standard ist und Alkohol pro Person aktiv gewählt werden muss.
  <br>`besitzer-28` · Jugendschutz · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Einstellungen sperren bis Spielende** — Option, dass während einer laufenden Runde nicht einmal der Admin Grenzen oder Profile ändern kann, außer Not-Aus. Verhindert, dass jemand heimlich den Turbo für sich hochdreht. Änderungen werden vorgemerkt und nach der Runde aktiv.
  <br>`besitzer-33` · Profile & Grenzen · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **Backup als Datei und als QR-Code** — Komplette Konfiguration (ohne Passwörter, optional mit WLANs) als JSON-Datei herunterladen und wieder einspielen. Zusätzlich: einzelne Modi als kompakter QR-Code oder Textschnipsel, den man fotografieren, per Messenger schicken oder an ein anderes Gerät verfüttern kann. *Hinweis: Herunterladen im unsicheren Kontext geht per Blob-Link; QR nur für kleine Modi (Längenlimit).*
  <br>`besitzer-15` · Backup & Teilen · Aufwand mittel · HW ja · ★ 3 · V1 1/4
- **Geräuschpegel und Klänge auf den Handys** — Das Gerät selbst hat keinen Lautsprecher, aber die Handys können Effekte abspielen (Motor-Brumm, Hühnergackern, Rückspul-Geräusch). Der Besitzer stellt ein: Sounds an/aus, nur auf dem Spielleiter-Handy, Lautstärke-Empfehlung, "Flüstermodus" ohne Töne und mit langsamerem Motor (der Motor selbst ist bei niedriger Drehzahl leiser). *Hinweis: Kein Buzzer auf der Platine; Ton nur über Browser. Audio-Dateien kosten Flash (4 MB), also wenige, kurze, komprimierte Clips. iOS spielt Audio erst nach Nutzerinteraktion.*
  <br>`besitzer-8` · Lautstärke & Atmosphäre · Aufwand mittel · HW eingeschränkt · ★ 3 · V1 0/4
- **Leisere Motorgeräusche durch PWM-Wahl** — Admin-Option, die PWM-Frequenz (z. B. 20 kHz unhörbar vs. tiefer für mehr Drehmoment) und die Rampensteilheit wählt. Ein "Leise"-Preset nutzt weiche Rampen und keine abrupten Richtungswechsel, damit nachts im Nebenzimmer niemand aufwacht. *Hinweis: Nur als Experten-Einstellung; Getriebegeräusch bleibt.*
  <br>`besitzer-9` · Lautstärke & Atmosphäre · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Hühnerfarben und Platznamen umbenennen** — Die vier Plätze lassen sich frei benennen und mit Farben versehen, passend zu den echten Chips oder zu eigenen Aufklebern (z. B. "Platz am Fenster", "Oma"). Bei Chewie andere Standardnamen passend zum Thema. Optional feste Stammspieler pro Platz.
  <br>`besitzer-11` · Personalisierung · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Gäste-Hotspot mit Wegwerf-Passwort** — Für Partys erzeugt der Admin ein Party-Passwort für den Hotspot, das nach dem Abend (oder nach X Stunden) automatisch verfällt und zum Aufkleber-Passwort zurückkehrt. Ein QR-Code dazu wird groß auf dem Admin-Handy angezeigt, damit Gäste ihn abscannen. *Hinweis: Zeitablauf ohne Uhr über Laufzeit/Neustart lösen; Wiederherstellung per Hebel-Geste bleibt.*
  <br>`besitzer-13` · WLAN & Netzwerk · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Werksreset in Stufen** — Drei Reset-Stufen statt einer: nur Statistik löschen, Einstellungen auf Standard (Modi und WLANs bleiben), alles löschen. Jede Stufe mit Klartext, was verloren geht, und Hebel-Bestätigung. Vor dem Komplettreset wird automatisch ein Backup zum Download angeboten.
  <br>`besitzer-35` · Updates & Wartung · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Schlaf- und Aufwach-Verhalten** — Einstellungen, wie schnell Louie einschläft, ob er per Hebel-Geste oder nur per Einschalten aufwacht, und ob er nach dem Aufwachen automatisch ins letzte Profil oder ins sichere Kinderprofil geht. Dazu ein Transportmodus, der WLAN komplett aus lässt, bis man ihn aktiv weckt. *Hinweis: GPIO-Wake aus Deep Sleep beim C3 laut Konzept noch zu bestätigen.*
  <br>`besitzer-40` · Zeit & Ruhe · Aufwand mittel · HW eingeschränkt · ★ 3 · V1 0/4
- **Party-Bericht am Ende des Abends** — Nach einer Party erstellt das UI eine Zusammenfassung zum Teilen (Bild oder Text): Anzahl Runden, wildester Rückspuler, Champion des Abends, längste Überlebenszeit. Der Besitzer stellt ein, ob Namen darin vorkommen oder alles anonym bleibt. *Hinweis: Bild per Canvas im Browser erzeugbar; Datenschutz bei Namen beachten.*
  <br>`besitzer-41` · Statistik · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Kindersicherung mit Hebel-Siegel** — Im Kinderprofil werden alle Turbo- und Rückwärtsfunktionen hart gesperrt, und das Lösen der Sperre verlangt neben dem Admin-Passwort ein Umlegen des Hebels in einem bestimmten Rhythmus. So kann ein Kind, das zufällig das Passwort kennt, aus dem Kinderzimmer heraus nichts freischalten, ohne am Spiel zu sein. *Hinweis: Wie bei der Ersteinrichtung: physischer Zugriff gilt als Besitzernachweis.*
  <br>`besitzer-2` · Jugendschutz · Aufwand klein · HW ja · ★ 2 · V1 0/4
- **Rundenzeit- und Spielzeit-Limit** — Der Besitzer legt fest: maximale Dauer einer Runde, maximale Spielzeit pro Tag oder pro Sitzung ("nach 45 Minuten ist Schluss"), und optional feste Ruhezeiten (z. B. nach 19:30 nur Gemütlich-Modus oder gar nicht). Kurz vor Ablauf kommt ein freundlicher Hinweis im UI ("Noch eine letzte Runde!"). *Hinweis: Uhrzeit nur bei Heim-WLAN per NTP sicher; im Hotspot kann das Handy die Zeit beim Verbinden mitliefern (manipulierbar).*
  <br>`besitzer-6` · Zeit & Ruhe · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Konfiguration auf andere Geräte klonen** — Ein Knopf "Diese Einstellungen auf ein anderes Louie übertragen" erzeugt ein Paket (Grenzen, Profile, Modi, Rechte), das man auf dem zweiten Gerät einspielt. Modellabhängige Werte (alter/neuer Louie, Chewie) werden dabei nicht blind übernommen, sondern über die Prozent-Logik umgerechnet. *Hinweis: Über Datei/Handy als Brücke einfach machbar.*
  <br>`besitzer-18` · Mehrere Geräte · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Update-Kanal und Update-Erinnerung** — Admin wählt "stabil" oder "experimentell". Im Heim-WLAN kann das UI (das Handy hat Internet) prüfen, ob es eine neuere Firmware gibt, und den Admin darauf hinweisen. Das Herunterladen macht das Handy, der Upload aufs Gerät läuft lokal. *Hinweis: Gerät selbst bleibt ohne Cloud; Prüfung nur im Browser. Herkunft der Datei per Signatur/Checksumme prüfen.*
  <br>`besitzer-19` · Updates & Wartung · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Spielstatistik für Besitzer** — Ein Statistik-Bereich zeigt: Anzahl Runden, Gesamtspielzeit, Lieblingsmodus, längste Runde, wie oft der Rückspuler gedrückt wurde und von wem, häufigster Sieger (falls Ausscheiden markiert wurde). Kann zurückgesetzt oder komplett abgeschaltet werden. *Hinweis: Gerät erkennt Ausscheiden nicht selbst; Sieger-Statistik nur so gut wie die Eingaben. Flash-Schreibzyklen schonen (gebündelt speichern).*
  <br>`besitzer-21` · Statistik · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Wartungsanzeige für Motor und Getriebe** — Aus Laufzeit und Motorstrom berechnet das Gerät einen "Gesundheitswert" und meldet z. B. "Motor braucht mehr Strom als früher, Getriebe prüfen oder Flugarm reinigen". Dazu Betriebsstundenzähler und Zähler für Blockierungen. *Hinweis: Motorstrommessung vorhanden, aber Aussagekraft muss am Prototyp erst kalibriert werden.*
  <br>`besitzer-22` · Statistik · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Hitze-Schätzung und Zwangspause** — Ohne Temperatursensor schätzt die Firmware aus Strom mal Zeit die Erwärmung von Motor und Treiber. Nach langen Turbo-Phasen erzwingt sie eine kurze Abkühlpause ("Louie muss tanken") und senkt die Höchstgeschwindigkeit, bis sich der Wert erholt hat. *Hinweis: Nur Modell, kein Messwert; der DRV8833 hat selbst eine Übertemperaturabschaltung als letzte Linie.*
  <br>`besitzer-25` · Hardware-Sicherheit · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Verantwortungs-Bremse im Trinkspiel** — Admin-Einstellungen für maximale Anzahl Strafschlucke pro Person und Stunde, Pflichtpausen nach einer Anzahl Runden und automatische Wasser-Runde. Erreicht jemand die Grenze, schaltet das UI für diese Person auf Ersatzaufgaben um. Optional ein deutlicher Hinweis "Kein Fahren nach dem Spiel". *Hinweis: Gerät kann nur zählen, was über die Handys eingegeben wird.*
  <br>`besitzer-29` · Jugendschutz · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Rechte-Matrix zum Antippen** — Statt einzelner Schalter eine Tabelle Rollen × Rechte (Gast, Spieler, Spielleiter, Profil) mit Häkchen: Modi speichern, Rückspulen, Boost, Spielleiter werden, Not-Aus, Statistik sehen. Darunter die Vorlagen "offen", "normal", "streng". *Hinweis: Passt direkt zur geplanten Rechte-Liste in der Konfiguration.*
  <br>`besitzer-30` · Rechte & Rollen · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Änderungsprotokoll** — Ein kurzes Logbuch im Admin-Bereich: wer (Sitzung/Profil) wann was geändert hat, wann Updates eingespielt wurden, wann Sperren oder Blockierungen ausgelöst haben. Die letzten 50 Einträge im Ringpuffer, als Datei exportierbar. *Hinweis: Zeitangaben ohne NTP nur relativ (seit Start).*
  <br>`besitzer-34` · Updates & Wartung · Aufwand klein · HW ja · ★ 2 · V1 0/4
- **Status-LED-Optionen** — Besitzer wählt, was die Status-LED zeigt: Netzmodus, Akkustand, Abklingzeit des Rückspulers, oder gar nichts ("dunkel" für Nachtpartys oder damit Kinder nicht davon abgelenkt werden). Helligkeit per PWM einstellbar. *Hinweis: Nur eine einfarbige LED im Batteriefach, wahrscheinlich schlecht sichtbar.*
  <br>`besitzer-36` · Personalisierung · Aufwand klein · HW ja · ★ 2 · V1 0/4
- **Modellprofil-Kalibrierung per Assistent** — Ein geführter Test misst Anlaufspannung, Leerlaufstrom und gefühlte Höchstgeschwindigkeit des konkreten Exemplars und speichert daraus ein eigenes Modellprofil. Besonders für alte, ausgeleierte Louies oder Bastler mit Fremdmotor. *Hinweis: Nutzt Motorstrommessung; Höchstgeschwindigkeit muss der Mensch per Augenmaß bestätigen.*
  <br>`besitzer-37` · Profile & Grenzen · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Eigene Texte und Sprachpakete** — Besitzer kann Ansagen und Beschriftungen überschreiben (Familienwitze, Dialekt, Hochzeitsparty-Motto) oder eine andere Sprache einspielen. Texte liegen zentral als JSON und lassen sich exportieren und teilen. *Hinweis: Flash-Platz für Sprachpakete begrenzt.*
  <br>`besitzer-39` · Personalisierung · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Mehrere Heim-WLANs mit Ortsprofilen** — Zu jedem gespeicherten WLAN gehört ein Ortsprofil: Zuhause = Kinderprofil, Ferienhaus = Familie, WG-Party = Erwachsene. Verbindet sich Louie mit dem Netz, ist automatisch das passende Profil aktiv. Ohne bekanntes Netz (Hotspot) gilt das vorsichtigste Profil. *Hinweis: Gute Sicherheitsvoreinstellung: unbekannter Ort = streng.*
  <br>`besitzer-12` · WLAN & Netzwerk · Aufwand mittel · HW ja · ★ 1 · V1 0/4
- **Turnier über mehrere Spiele** — Bei mehreren Geräten auf einer Party (Louie und Chewie) verknüpft ein Admin sie zu einem Turnier: gleiche Profile und Grenzen auf allen, gemeinsame Startfreigabe, Rangliste über alle Tische. Ein Gerät ist Chef, die anderen folgen. *Hinweis: Erfordert Gerät-zu-Gerät-Kommunikation (WLAN oder ESP-NOW); im Hotspot-Betrieb schwierig. Eher spätere Version.*
  <br>`besitzer-17` · Mehrere Geräte · Aufwand groß · HW eingeschränkt · ★ 1 · V1 0/4
- **Zweiter Admin / Mit-Besitzer** — Neben dem Haupt-Admin kann ein eingeschränkter "Gastgeber" mit eigener PIN angelegt werden: darf Profile wechseln, Party-Hotspot erzeugen und Rundenzeiten setzen, aber keine Grenzwerte, WLANs oder Updates ändern. Ideal, wenn ein Teenager die Party leitet. *Hinweis: Entspricht Stufe 3 aus dem Konzept; Klartext-Passwort-Problem ohne HTTPS bleibt.*
  <br>`besitzer-31` · Rechte & Rollen · Aufwand mittel · HW ja · ★ 1 · V1 0/4
- **Modus-Tauschbörse zwischen Geräten** — Stehen zwei Louies im selben WLAN, findet einer den anderen per mDNS und bietet an: "Modi von Louie-Dachboden übernehmen?". Auf Familientreffen oder in Spielecafés können Lieblingsmodi so ohne Internet wandern. Der empfangende Admin bestätigt jede Übernahme. *Hinweis: ESP muss als HTTP-Client zu anderem ESP gehen; RAM knapp. Einfachere Variante: über das Handy als Zwischenspeicher.*
  <br>`besitzer-16` · Mehrere Geräte · Aufwand groß · HW eingeschränkt · ★ 0 · V1 0/4
- **Bastler-Modus mit Rohwerten** — Ein verstecktes Experten-Menü (nach Admin-Login und Warnung) zeigt Live-Graphen von Strom, Spannung und PWM und erlaubt eigene Grenzen über den Standardrahmen hinaus, z. B. für Umbauten mit stärkerem Motor. Danach erscheint im normalen UI dauerhaft ein Hinweis "Experteneinstellungen aktiv". *Hinweis: Absolute Hardware-Grenzen (Treiberstrom, Akku) dürfen nie überschreitbar sein.*
  <br>`besitzer-38` · Bastler · Aufwand mittel · HW eingeschränkt · ★ 0 · V1 0/4

### 5.5 Hardware, Sicherheit & Robustheit (59)

- **Rückspuler-Sperrkreis** — Der Rückspuler wird global entprellt: Nach jedem Rückwärtsstoß gibt es eine globale Schutzzeit, in der niemand einen neuen auslösen kann, egal wie viele Spieler Kontingent haben. Zusätzlich ein Anteil-Deckel pro Runde. So können vier Handys zusammen keinen Dauer-Rückwärtslauf erzeugen. *Hinweis: Baut auf den Server-Grenzen aus dem Software-Konzept auf; wichtig ist die globale statt nur pro-Spieler-Abklingzeit.*
  <br>`technik-29` · Missbrauchsschutz · Aufwand klein · HW ja · ★ 10 · V1 4/4
- **Blockier-Erkennung mit Sofort-Stopp** — Steigt der Motorstrom über eine Schwelle und bleibt dort länger als ca. 200–300 ms (Louie hängt an einer Wippe, Finger im Arm), schaltet die Firmware auf Bremsen und dann aus. Im UI erscheint "Louie steckt fest", weiter geht es erst nach Hebel aus/an. Ergänzt die feste 2-A-Grenze des DRV8833, die nur begrenzt und nicht abschaltet. *Hinweis: Schwelle hängt vom Modell ab und muss gelernt werden (siehe Kalibrierfahrt); kurze Stromspitzen beim Anlauf ausblenden.*
  <br>`technik-1` · Motorschutz · Aufwand klein · HW ja · ★ 9 · V1 4/4
- **Spielleiter-Notaus im UI** — Auf jedem Spielleiter- und Admin-Bildschirm ein immer sichtbarer roter Stopp-Knopf, der sofort bremst, unabhängig vom Modus. Optional auch für Spieler-Handys freischaltbar ("jeder darf stoppen"), z. B. bei kleinen Kindern. *Hinweis: Ersetzt nicht den Hebel, der hardwareseitig trennt.*
  <br>`technik-32` · Kindersicherheit · Aufwand klein · HW ja · ★ 9 · V1 4/4
- **Richtungswechsel immer über Null mit Totzeit** — Vorwärts nach rückwärts geht nie direkt: Rampe auf 0, kurz bremsen, 50–150 ms Pause, dann Rampe in die Gegenrichtung. Gilt in der untersten Motorschicht, auch für Rückspuler-Stöße. So wird der Rückwärtsstoß gefühlt kurz, belastet aber Akku und Getriebe kaum. *Hinweis: Die Rampe frisst von einem 0,5-s-Stoß spürbar Zeit ab; Stoßdauer als Netto-Rückwärtszeit definieren.*
  <br>`technik-3` · Motorschutz · Aufwand klein · HW ja · ★ 8 · V1 4/4
- **Sichere Standardwerte bei unbekanntem Modell** — Solange kein Modellprofil gewählt ist, gilt das vorsichtigste Profil (1,5-V-Louie alt, kein Turbo, kein Rückwärts). Ein frisch verschenkter Bausatz kann so den alten 1,5-V-Motor nie mit 4,2 V überfahren.
  <br>`technik-48` · Motorschutz · Aufwand klein · HW ja · ★ 8 · V1 4/4
- **Sitzplatz-Diebstahl verhindern** — Ein belegter Platz kann nur übernommen werden, wenn der bisherige Client 60 s weg ist oder der Spielleiter freigibt. Verhindert, dass ein Gast den Platz eines Spielers kapert und dessen Boosts oder Rückspuler verbraucht. Neue Sitzungen pro Gerät begrenzen (Zweithandy-Trick).
  <br>`technik-30` · Missbrauchsschutz · Aufwand klein · HW ja · ★ 8 · V1 3/4
- **Mehrstufiger Watchdog** — Ebene 1: Motor-Task stoppt ohne frische Sollwerte nach 500 ms. Ebene 2: Hardware-Watchdog startet bei hängendem Hauptprogramm neu. Ebene 3: nach drei Abstürzen in Folge startet die Firmware im "sicheren Modus" ohne eigene Modi und ohne Updates, nur Klassisch plus Admin-Seite. *Hinweis: Sicherer Modus braucht eine unveränderliche Rückfall-Logik in den frozen modules.*
  <br>`technik-16` · Robustheit · Aufwand mittel · HW ja · ★ 7 · V1 4/4
- **Anlauf-Ausblendung und Soft-Start** — Beim Anfahren und bei jedem Richtungswechsel ist der Strom kurz hoch. Die Blockier-Erkennung wird dann für ein Zeitfenster ausgesetzt; gleichzeitig startet der Motor über eine Rampe statt mit vollem Tastgrad. Das verhindert Fehlalarme und Spannungseinbrüche.
  <br>`technik-2` · Motorschutz · Aufwand klein · HW ja · ★ 7 · V1 3/4
- **Unterspannung in drei Stufen** — Stufe 1 (z. B. 3,5 V unter Last): Warnung im UI und LED-Muster. Stufe 2 (3,4 V): Turbo und Rückwärts gesperrt, Höchstgeschwindigkeit sinkt. Stufe 3 (3,3 V): Runde endet sauber mit Hinweis, Motor aus, nur noch WLAN. Unter 3,2 V Deep Sleep, bevor die Akkuschutzschaltung hart abschaltet. *Hinweis: Spannung unter Last messen und mit Innenwiderstand korrigieren, sonst Fehlwarnungen bei Boosts.*
  <br>`technik-11` · Akkuschutz · Aufwand klein · HW ja · ★ 7 · V1 3/4
- **Hebel-Gesten mit Zeitfenster und Bestätigung** — Gesten (Hotspot erzwingen, Admin-Reset, Werksreset) gelten nur in den ersten 10 s nach dem Aufwecken und werden durch ein LED-/Piepsmuster quittiert; eine zweite Geste bestätigt. So löst kein Kind beim wilden Hebeln versehentlich einen Werksreset aus.
  <br>`technik-25` · Sicherheit · Aufwand klein · HW ja · ★ 7 · V1 2/4
- **Turbo-Zeitbudget** — Oberhalb der Nennspannung darf der Motor nur begrenzt laufen, z. B. max. 10 s am Stück und max. 20 % der Runde. Danach automatisch zurück auf 100 %. Admin stellt die Werte ein, Modi und Boosts können sie nicht überschreiben.
  <br>`technik-5` · Motorschutz · Aufwand klein · HW ja · ★ 6 · V1 3/4
- **Rate-Limit pro Sitzung und pro Gerät** — Der Server nimmt pro Sitzung nur eine begrenzte Zahl Aktionen pro Sekunde an (z. B. 5 Nachrichten/s, Boost-Taste nach Abklingzeit sonst ignoriert). Wer per Skript oder Dauerdrücken spammt, wird gedrosselt und im Spielleiter-Bildschirm markiert. Schützt auch den knappen RAM.
  <br>`technik-28` · Missbrauchsschutz · Aufwand klein · HW ja · ★ 6 · V1 3/4
- **Update mit Rücksprung und Probelauf** — Nach einem Update startet die neue Version im Probelauf. Erst wenn Selbsttest und Webserver laufen und der Admin "bestätigen" drückt (oder 3 Starts ohne Absturz), wird sie fest. Sonst automatisch zurück zur Vorversion. Updates nie während einer Runde und nur bei ausreichend Akku.
  <br>`technik-46` · Update-Sicherheit · Aufwand mittel · HW ja · ★ 6 · V1 2/4
- **Konfiguration mit Prüfsumme und Rückfallkopie** — config.json und Kalibrierung werden mit Prüfsumme gespeichert, zusätzlich eine letzte gute Kopie. Ist die Hauptdatei beschädigt (Stromausfall beim Schreiben), lädt die Firmware die Kopie bzw. sichere Standardwerte statt mit kaputten Grenzen zu fahren.
  <br>`technik-47` · Robustheit · Aufwand klein · HW ja · ★ 6 · V1 2/4
- **Hebel-Erkennung über Strom absichern** — Während der Fahrt wird "Hebel aus" am Strom-Null erkannt. Damit das nicht durch einen kurzen Stromnull bei Rampen oder Bremsen fehlinterpretiert wird, gilt ein Mindest-Tastgrad beim Prüfen und eine Bestätigung über SENSE nach kurzem Treiber-Sleep. Ergebnis: Rundenende wird zuverlässig erkannt.
  <br>`technik-49` · Robustheit · Aufwand klein · HW ja · ★ 6 · V1 2/4
- **Verbindungs-Limit und Gast-Kick** — Maximal z. B. 8 Clients; ist das Limit voll, werden reine Gäste ohne Platz zuerst getrennt. Spielleiter kann einzelne Geräte für die Partie sperren. Schützt den ESP vor zu vielen offenen WebSockets.
  <br>`technik-31` · Missbrauchsschutz · Aufwand klein · HW ja · ★ 6 · V1 1/4
- **Keine Telemetrie, sichtbar zugesichert** — Die Firmware baut nie eine Verbindung ins Internet auf (außer optional NTP und Update-Prüfung, beides abschaltbar und standardmäßig aus). Im Info-Bildschirm steht klar, was gespeichert wird. Wichtig, weil Kinder mitspielen und das Gerät verschenkt wird.
  <br>`technik-44` · Datenschutz · Aufwand klein · HW ja · ★ 5 · V1 2/4
- **Motor aus bei Verbindungsverlust des Spielleiters (optional)** — In Modi, die stark vom Handy abhängen (z. B. Spielleiter regelt live), fährt Louie auf eine sichere Grundgeschwindigkeit zurück, wenn der steuernde Client 3 s nichts sendet. Der Hebel funktioniert unabhängig weiter.
  <br>`technik-17` · Robustheit · Aufwand klein · HW ja · ★ 5 · V1 1/4
- **Selbsttest beim Start** — Nach dem Aufwecken prüft die Firmware in unter einer Sekunde: Motor angeschlossen (SENSE), Akkuspannung plausibel, Shunt-Nullpunkt, nFAULT inaktiv. Ergebnis als LED-Muster und als Ampel in der Diagnose. Hilft beim Nachbau, falsch eingelegte Platinen oder schlechte Kontakte zu finden.
  <br>`technik-20` · Diagnose · Aufwand klein · HW ja · ★ 5 · V1 1/4
- **Physischer Besitznachweis per Hebel** — Kritische Aktionen (Admin-Passwort setzen, Firmware-Update, Grenzwerte über Standard, Hotspot öffnen) müssen zusätzlich innerhalb von 30 s durch Hebel an/aus bestätigt werden. Wer nur im WLAN ist, aber nicht am Tisch sitzt, kann so nichts Wichtiges ändern.
  <br>`technik-27` · Zugangssicherheit · Aufwand klein · HW ja · ★ 5 · V1 1/4
- **Kindermodus mit Strom-Feingefühl** — Eine Admin-Voreinstellung: kein Turbo, kein Rückwärts, niedrigere Höchstgeschwindigkeit und deutlich empfindlichere Blockier-Erkennung, sodass Louie schon bei leichtem Gegenhalten mit dem Finger stoppt. Für Kleinkinder, die gern in den Arm greifen. *Hinweis: Empfindlichkeit durch das Strommessen begrenzt; leichtes Berühren erzeugt evtl. kaum Stromanstieg.*
  <br>`technik-33` · Kindersicherheit · Aufwand klein · HW ja · ★ 5 · V1 1/4
- **Sicherheitsgrenzen nur nach oben mit Hinweis** — Wenn der Admin Turbo-Grenze, Rückwärtsdauer oder Rampe über die Projekt-Empfehlung stellt, zeigt das UI einen klaren Hinweis zu Risiken (Motorverschleiß, Frust, Brownout) und verlangt Hebel-Bestätigung. Absolute Hartgrenzen (z. B. nie über 4,2 V Akku, nie über 2 A) sind fest im Code.
  <br>`technik-59` · Sicherheit · Aufwand klein · HW ja · ★ 5 · V1 1/4
- **Thermisches Motormodell (I²t)** — Die Firmware integriert den gemessenen Strom über die Zeit und schätzt so die Erwärmung von Motor und Treiber. Wird lange im Turbo gespielt oder oft blockiert, sinkt die erlaubte Höchstgeschwindigkeit sanft ("Louie ist erschöpft"), bis er sich abgekühlt hat. Schützt den kleinen Original-Motor, für den es kein Datenblatt gibt. *Hinweis: Modellparameter nur grob schätzbar; konservativ starten.*
  <br>`technik-4` · Motorschutz · Aufwand mittel · HW ja · ★ 5 · V1 0/4
- **Finger-Klemmschutz durch Rückweichen** — Wird eine Blockade erkannt, stoppt Louie nicht nur, sondern fährt einen winzigen Ruck zurück (z. B. 100 ms bei geringer Spannung), um einen eingeklemmten Finger oder ein verkeiltes Huhn freizugeben, und bleibt dann stehen. *Hinweis: Nur sehr kurz und schwach, sonst wird es selbst zur Gefahr; als Option.*
  <br>`technik-34` · Kindersicherheit · Aufwand klein · HW ja · ★ 5 · V1 0/4
- **Datensparsame Profile** — Profile enthalten nur Spitzname, Farbe und Emoji, keine echten Namen, keine Fotos, keine Geräte-IDs außer dem Zufallstoken. Statistik ist lokal und mit einem Knopf löschbar; nach x Tagen ohne Nutzung verfallen Profile automatisch.
  <br>`technik-43` · Datenschutz · Aufwand klein · HW ja · ★ 5 · V1 0/4
- **Brownout-Detektor und Ursachenspeicher** — Nach jedem Neustart liest die Firmware den Reset-Grund (Brownout, Watchdog, Absturz, normal) und speichert die letzten 10 mit Zeitstempel relativ zur Laufzeit und letzter Motorstufe. Häufen sich Brownouts bei Richtungswechseln, wird die Rampe automatisch flacher.
  <br>`technik-15` · Robustheit · Aufwand klein · HW ja · ★ 4 · V1 1/4
- **Sitzungs-Token härten** — Token sind zufällig (Hardware-RNG des ESP), laufen ab, werden bei Admin-Login neu erzeugt und sind an den Platz gebunden. Admin-Rechte nur per HttpOnly-Cookie, nie im localStorage. Ohne HTTPS bleibt ein Restrisiko, aber Kopieren eines Spieler-Tokens bringt keine Admin-Rechte.
  <br>`technik-40` · Netzsicherheit · Aufwand klein · HW ja · ★ 4 · V1 1/4
- **Restspielzeit-Anzeige** — Aus Ladezustand (Spannungskurve) und typischem Verbrauch pro Runde zeigt die Lobby "reicht noch für ca. 12 Runden" statt nur eines Prozentwerts. Für Partys verständlicher als Volt. *Hinweis: Ladezustand über Spannung bei LiPo nur grob; Lernwerte aus vergangenen Runden verbessern die Schätzung.*
  <br>`technik-13` · Akkuschutz · Aufwand mittel · HW ja · ★ 4 · V1 0/4
- **Ladeerkennung und Spielen beim Laden** — Wenn USB-Spannung anliegt (über das Kabel indirekt an steigender Akkuspannung erkennbar oder über einen VBUS-Teiler), zeigt das UI "lädt" und hält den Schlafmodus an. Optional Turbo beim Laden sperren, damit Power-Path und Laderegler nicht überlastet werden. *Hinweis: Ohne eigenen VBUS-Pin nur indirekt erkennbar; ein freier GPIO (IO2/IO8 sind Strapping-Pins) bräuchte Platinenänderung.*
  <br>`technik-14` · Akkuschutz · Aufwand mittel · HW eingeschränkt · ★ 4 · V1 0/4
- **Chip-Temperatur und Treiber-Übertemperatur** — Der ESP32-C3 hat einen internen Temperatursensor; zusammen mit nFAULT des DRV8833 (Übertemperatur, Überstrom) ergibt das eine einfache Hitzewarnung im Batteriefach. Bei Grenzwert: Turbo sperren, dann Pause mit Hinweis "Louie braucht eine Pause". *Hinweis: Interner Sensor misst den Chip, nicht Motor oder Akku; LiPo-Temperatur ist ohne NTC nicht messbar. NTC auf der Ladeplatine wäre eine Hardware-Erweiterung.*
  <br>`technik-18` · Robustheit · Aufwand klein · HW eingeschränkt · ★ 4 · V1 0/4
- **Getrenntes Gäste-Netz statt Heim-WLAN** — Im Heim-WLAN sieht jeder Partygast die Steuerung nur, wenn er im Heimnetz ist. Empfehlung im UI: Für Partys den eigenen Hotspot nutzen, damit Gäste nicht ins Heimnetz müssen. Louie bietet dafür einen Ein-Tipp-Umschalter "Party-Hotspot" an.
  <br>`technik-37` · Netzsicherheit · Aufwand klein · HW ja · ★ 4 · V1 0/4
- **nFAULT-Auswertung mit Klartext** — nFAULT wird nicht nur als "Fehler" gemeldet, sondern zusammen mit Strom und Spannung zum Zeitpunkt interpretiert: "Kurzschluss/Blockade", "Unterspannung am Treiber", "zu heiß". Fehlerprotokoll mit den letzten Ereignissen im Diagnose-Bereich. *Hinweis: DRV8833 unterscheidet die Ursachen nicht selbst; Interpretation ist Heuristik.*
  <br>`technik-19` · Diagnose · Aufwand klein · HW eingeschränkt · ★ 3 · V1 1/4
- **Diagnose-Export für Bastler** — Ein Knopf erzeugt eine JSON-Datei mit Firmware-Version, Modellprofil, Kalibrierwerten, Zählern, Fehlerlog und Reset-Gründen, ohne WLAN-Passwörter und Spielernamen. Kann man ins GitHub-Issue hängen, wenn man den Bausatz verschenkt hat und der Beschenkte Probleme hat.
  <br>`technik-22` · Diagnose · Aufwand klein · HW ja · ★ 3 · V1 1/4
- **Kalibrierfahrt beim Einrichten** — Im Einrichtungsassistenten fährt Louie 10–15 s mit mehreren Geschwindigkeiten in beide Richtungen. Gemessen werden Anlaufspannung (ab wann dreht er überhaupt), Leerlaufstrom je Stufe und Stromspitze beim Anlauf. Daraus setzt die Firmware Mindestspannung, Blockierschwelle und Hebel-Erkennungsschwelle automatisch. *Hinweis: Ersetzt teilweise das manuelle Messen der Turbo-Grenze; Turbo selbst nicht automatisch hochdrehen.*
  <br>`technik-8` · Kalibrierung · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Kontaktqualität im Batteriefach messen** — Springt der Motorstrom im Lauf kurz auf null, ohne dass der Hebel bewegt wurde, deutet das auf Wackelkontakt an Feder oder Blech. Die Diagnose zählt diese Aussetzer und zeigt "Kontakte prüfen". Wichtig, weil die Platine ohne Löten nur eingeklemmt ist. *Hinweis: Schwer zu unterscheiden von sehr kurzem Hebel-Wackeln; Dauer als Kriterium.*
  <br>`technik-21` · Diagnose · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Werksreset in Stufen** — Stufe 1: nur Admin-Passwort und WLANs zurücksetzen. Stufe 2: zusätzlich Konfiguration und Kalibrierung. Stufe 3: alles inklusive eigener Modi und Statistik. Per Admin-Seite oder lange Hebel-Geste; die Firmware selbst bleibt immer erhalten.
  <br>`technik-26` · Sicherheit · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Lautstärke-Grenzen für Handy-Sounds** — Admin legt eine maximale Lautstärke für Soundeffekte im Web-UI fest und kann eine Ruhezeit einstellen (z. B. ab 20 Uhr keine Sounds, keine Vibration). Für Partymodus abschaltbar. *Hinweis: Browser erlaubt keine echte Systemlautstärke; es geht nur um die Lautstärke der eigenen Audio-Elemente.*
  <br>`technik-35` · Kindersicherheit · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Partie-Code statt offenem Zugang** — Im Heim-WLAN erscheint auf dem Spielleiter-Handy ein vierstelliger Code oder QR-Code; nur wer ihn eingibt, kann einen Platz belegen. Verhindert, dass Mitbewohner oder Nachbarn im selben Netz heimlich Rückspuler drücken.
  <br>`technik-38` · Netzsicherheit · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Hotspot-Passwort rotieren** — Neben dem festen Aufkleber-Passwort kann der Admin ein temporäres Party-Passwort erzeugen, das nach dem Schlafmodus wieder verfällt. Der QR-Code wird dann auf dem Spielleiter-Handy angezeigt statt vom Aufkleber gescannt. *Hinweis: Gäste müssen sich nach jedem Wecken neu verbinden.*
  <br>`technik-39` · Netzsicherheit · Aufwand mittel · HW ja · ★ 3 · V1 0/4
- **Kraftmesser: Wer bremst Louie?** — Der Motorstrom steigt, wenn eine Wippe Louie stark anhebt oder ein Spieler das Flugzeug mechanisch bremst. Das UI zeigt live eine "Louie-Belastung"-Anzeige; Treffer mit hoher Last erscheinen als Effekt ("Bumm!"). Wer welcher Spieler war, sieht die Elektronik nicht, aber die Stimmung wird hörbar und sichtbar. *Hinweis: Ob Wippen-Treffer im Strom überhaupt messbar sind, muss am echten Spiel getestet werden; Rauschen durch PWM und Bürsten.*
  <br>`technik-50` · Motorstrom-Spielfunktion · Aufwand mittel · HW eingeschränkt · ★ 3 · V1 0/4
- **Überlast als Spielereignis "Louie wird sauer"** — Wird Louie wiederholt stark gebremst, reagiert der Modus: kurze Pause, dann ein Rachestoß nach vorne (innerhalb der Grenzen). Die Strommessung wird so vom Schutz zur Spielmechanik, und das Gegenhalten bekommt eine Konsequenz. *Hinweis: Nur sinnvoll, wenn Bremsen zuverlässig erkennbar ist; darf nie die Blockier-Abschaltung aushebeln.*
  <br>`technik-54` · Motorstrom-Spielfunktion · Aufwand mittel · HW eingeschränkt · ★ 3 · V1 0/4
- **Status-LED als Sicherheits-Ampel** — Neben dem Netzmodus zeigt die LED auch Sicherheitszustände: Doppelblitz = Blockade erkannt, Dauerflackern = Akku fast leer, langsames Pulsieren = Abkühlpause. So versteht man ohne Handy, warum Louie gerade nicht fliegt. *Hinweis: LED sitzt im Batteriefach; Sichtbarkeit von außen hängt vom Modell ab (altes Modell offen, neues mit Deckel).*
  <br>`technik-56` · Kindersicherheit · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Transport- und Lagermodus** — Admin oder Hebel-Geste schickt Louie in einen Tiefschlaf ohne Hebel-Wecken (nur per USB-Strom aufweckbar). Verhindert, dass Louie in der Spielekiste durch Rütteln am Hebel ständig aufwacht und den Akku leert. Ergänzt den optionalen Schiebeschalter. *Hinweis: Aufwecken nur per USB setzt eine VBUS-Erkennung oder Reset per USB voraus; sonst Wecken über langes Hebel-an halten.*
  <br>`technik-57` · Akkuschutz · Aufwand klein · HW eingeschränkt · ★ 3 · V1 0/4
- **Selbstentladungs-Wächter im Schlaf** — Der ESP wacht im Deep Sleep z. B. einmal am Tag per Timer auf, misst die Akkuspannung und geht bei kritischem Stand in einen noch tieferen Schlaf ohne weitere Timer. Beim nächsten Wecken warnt das UI: "Akku war lange leer, bitte laden."
  <br>`technik-58` · Akkuschutz · Aufwand klein · HW ja · ★ 3 · V1 0/4
- **Getriebe-Verschleißzähler** — Gesamtlaufzeit, Anzahl Starts, Richtungswechsel, Blockaden und Turbo-Sekunden werden selten (z. B. am Rundenende) ins Flash geschrieben. Im Diagnose-Bereich sieht der Besitzer, wie viel Louie schon hinter sich hat; optional Hinweis "Getriebe mal prüfen". *Hinweis: Flash-Schreibzyklen beachten: nur am Rundenende speichern.*
  <br>`technik-6` · Diagnose · Aufwand klein · HW ja · ★ 2 · V1 0/4
- **Leerlaufstrom-Trend als Verschleiß-Indikator** — Bei jeder Runde wird der mittlere Strom bei 100 % in den ersten Sekunden gespeichert. Steigt er über Wochen, ist das Getriebe schwergängig (Staub, Haare, ausgeleierter Arm). Die Diagnose zeigt eine kleine Kurve und schlägt Reinigen vor. *Hinweis: Streut mit Akkuspannung und Temperatur; nur grober Trend.*
  <br>`technik-7` · Diagnose · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Akku-Innenwiderstand schätzen** — Akkuspannung kurz vor und während einer Motorstufe plus gemessener Strom ergeben den Innenwiderstand. Steigt er stark, ist der LiPo gealtert oder zu klein; Diagnose zeigt "Akku schwach, Ersatz empfohlen". Hilft auch, eine echte Restlaufzeit-Anzeige zu rechnen.
  <br>`technik-12` · Akkuschutz · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Live-Oszilloskop für Strom und Spannung** — Admin-Ansicht mit einer scrollenden Kurve von Motorstrom, Akkuspannung und Sollwert (ca. 20 Werte/s über WebSocket). Praktisch zum Festlegen der Turbo-Grenze und um Blockier-Schwellen sichtbar zu machen. *Hinweis: Nur für Admin und nur außerhalb von Runden mit vielen Clients, sonst WebSocket-Last.*
  <br>`technik-23` · Diagnose · Aufwand mittel · HW ja · ★ 2 · V1 0/4
- **Motor als Lautsprecher (Piepsen)** — Mit kurzer PWM im hörbaren Bereich (z. B. 1–3 kHz, kleiner Tastgrad) gibt der Motor leise Töne von sich, ohne sich zu drehen. Damit kann Louie ohne Handy quittieren: Startton, Countdown, Fehlercode, "Akku leer". Leise genug, um nicht zu stören. *Hinweis: Lautstärke und Klang modellabhängig, im Spiel kaum hörbar; nicht bei laufendem Motor. Tastgrad klein halten, damit sich nichts bewegt.*
  <br>`technik-24` · Hardware-Trick · Aufwand klein · HW eingeschränkt · ★ 2 · V1 0/4
- **Spielzeit-Limit für Eltern** — Admin-Einstellung: max. Spielzeit pro Tag oder Anzahl Runden, danach nur noch Klassisch per Hebel oder gar nichts. Ohne echte Uhr zählt die Firmware ab Aufwecken; mit Heim-WLAN kann sie per NTP die Uhrzeit holen. *Hinweis: Im Hotspot-Betrieb keine Uhrzeit; Zeit vom ersten verbundenen Handy übernehmen wäre eine Alternative.*
  <br>`technik-36` · Kindersicherheit · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Treffer-Zähler aus Stromspitzen** — Jede kurze Stromspitze im Lauf wird als "Kontakt" gezählt (Louie trifft Wippe oder Chip). Am Rundenende gibt es eine Statistik: "Louie wurde 37-mal abgewehrt". Für Trinkspiel-Varianten: alle 10 Treffer ein Schluck für alle. *Hinweis: Unklar, ob einzelne Treffer sauber vom Rauschen trennbar sind; vorher mit dem Oszilloskop-Ansicht prüfen.*
  <br>`technik-51` · Motorstrom-Spielfunktion · Aufwand mittel · HW eingeschränkt · ★ 2 · V1 0/4
- **Automatische Modellerkennung** — Über den Wicklungswiderstand (SENSE-Teiler bei stehendem Motor) und den Leerlaufstrom bei kleiner Spannung schlägt die Firmware das passende Modellprofil vor (Louie alt 1,5 V vs. neu/Chewie 3 V). Der Nutzer bestätigt nur noch. *Hinweis: Unterscheidung neu vs. Chewie vermutlich nicht möglich; Auflösung des SENSE-Teilers bei wenigen Ohm sehr grob. Falsch erkanntes 1,5-V-Modell mit 3 V betreiben wäre schädlich, daher nur Vorschlag mit konservativem Default.*
  <br>`technik-9` · Kalibrierung · Aufwand mittel · HW eingeschränkt · ★ 1 · V1 0/4
- **Drehrichtung automatisch erkennen** — Statt "Dreht Louie richtig herum?" zu fragen, könnte eine Asymmetrie im Strombild (Getriebe/Arm läuft in eine Richtung leichter) die Richtung verraten. Realistischer: Richtung per Frage festlegen, aber per Hebel-Geste umschaltbar, falls das Handy fehlt. *Hinweis: Automatische Erkennung unsicher; Hebel-Geste als Fallback ist sicher machbar.*
  <br>`technik-10` · Kalibrierung · Aufwand klein · HW eingeschränkt · ★ 1 · V1 0/4
- **Admin-Funktionen nur im Hotspot oder per USB** — Option: Kritische Admin-Seiten (Update, WLAN-Passwörter, Werksreset) sind nur erreichbar, wenn man direkt mit dem Louie-Hotspot verbunden ist oder per USB-Konsole. Im Heim-WLAN bleibt nur das Spiel erreichbar. *Hinweis: Komfortverlust; als Admin-Option, nicht als Standard.*
  <br>`technik-41` · Netzsicherheit · Aufwand mittel · HW ja · ★ 1 · V1 0/4
- **WLAN-Zugangsdaten nie zurücklesbar** — Gespeicherte WLAN-Passwörter kann man im UI nur überschreiben oder löschen, nie anzeigen. Konfigurations-Export enthält sie standardmäßig nicht. Optional Verschlüsselung mit dem eFuse-Schlüssel des ESP32-C3 (Flash-Verschlüsselung). *Hinweis: Flash-Verschlüsselung erschwert Bastler-Zugriff per USB erheblich; eher nicht als Default.*
  <br>`technik-42` · Datenschutz · Aufwand mittel · HW eingeschränkt · ★ 1 · V1 0/4
- **Signierte Update-Pakete** — Update-Pakete (Python-Dateien, Web-UI) tragen eine Ed25519-Signatur des Projekts; die Firmware prüft sie vor dem Einspielen. Wer eigene Firmware will, kann per Admin-Option eigene Schlüssel hinterlegen oder die Prüfung bewusst abschalten (mit Hebel-Bestätigung). *Hinweis: Signaturprüfung in MicroPython ohne Web Crypto im Browser machbar (Prüfung auf dem ESP), aber Rechenzeit und Bibliothek klären; SHA-256-Prüfsumme als einfache Vorstufe.*
  <br>`technik-45` · Update-Sicherheit · Aufwand mittel · HW eingeschränkt · ★ 1 · V1 0/4
- **Rundenzeit-Messung ohne Sensor** — Der Bürstenmotor erzeugt im Strom eine Welligkeit pro Kommutierung; daraus ließe sich die Drehzahl schätzen (sensorlose Drehzahlmessung). Damit könnte die Firmware echte Umdrehungen zählen und die Geschwindigkeit bei Last nachregeln. *Hinweis: Ripple-Counting braucht schnelle ADC-Abtastung und gute Filterung; mit 20-kHz-PWM und RC-Filter am ADC fraglich. Alternative: Gegen-EMK in kurzen PWM-Pausen messen.*
  <br>`technik-52` · Motorstrom-Spielfunktion · Aufwand groß · HW eingeschränkt · ★ 0 · V1 0/4
- **Gegen-EMK-Drehzahlmessung in Pausen** — In kurzen Freilaufmomenten (einige ms) misst die Firmware die Spannung, die der drehende Motor selbst erzeugt. Das ergibt eine Drehzahl, mit der eine echte Drehzahlregelung möglich wird: Louie fliegt gleich schnell, egal wie stark gebremst wird, oder Spielmodi in Umdrehungen statt Sekunden. *Hinweis: SENSE-Pfad über 100k ist nur bei Treiber-Sleep nutzbar und eher langsam; Machbarkeit am Steckbrett prüfen.*
  <br>`technik-53` · Motorstrom-Spielfunktion · Aufwand groß · HW eingeschränkt · ★ 0 · V1 0/4
- **Erkennen, ob ein Chip auf Louie liegt** — Wildere Idee: Ein im Arm verkeilter Chip oder ein abgerissenes Flugzeug ändern das Lastprofil dauerhaft. Weicht der Leerlaufstrom stark vom kalibrierten Wert ab, fragt das UI "Ist Louie noch ganz?". *Hinweis: Chips sind sehr leicht; vermutlich nur grobe Defekte erkennbar.*
  <br>`technik-55` · Motorstrom-Spielfunktion · Aufwand mittel · HW eingeschränkt · ★ 0 · V1 0/4
