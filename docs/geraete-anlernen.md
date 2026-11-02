# Spieler, Geräte und Anlernen

Stand: 2026-11-02 · Status: Vorschlag. Funk-Taster = **BTHome über BLE, geplant für V1** (andere Funkwege abgelehnt). Ergänzt [web-ui-konzept.md](web-ui-konzept.md) (Abschnitt 4.2).
Technik der Funk-Taster: [idee-funk-taster.md](idee-funk-taster.md). Klickbar in [web/poc](../web/poc/index.html)
(Simulationsleiste „Funk-Taster“, Szenarien „Familie mit Tastern“ und „Gemischt“).

## 1. Grundsatz

Das virtuelle Spiel ist bewusst vom Tisch getrennt. Am Tisch zählt, was alle sehen. In der App zählt nur,
wer ein Eingabegerät hat.

- **Spieler** = ein Platz in der App: Name (Zufallsname Standard, von Hand änderbar), Farbe (optional,
  mehrfach erlaubt), Joker-Kontingente, Titel und Statistik.
- Einem Spieler sind **0..1 Handy** und **0..n Eingänge** zugeordnet. Möglich sind also: nur Handy, nur
  Taster, beides oder nichts. Ohne Gerät ist ein Spieler nur mit „📊 Statistik & Ausscheiden“ sinnvoll.
- Ein **Eingang** ist **Gerät + Taste + Ereignis** (einfach / doppelt / lang) → **Aktion**:
  Joker 1, Joker 2, „Ich bin raus“ (nur mit Statistik) oder nichts.
- **Joker 1 / Joker 2** beziehen sich auf den **aktuellen Modus** (erster bzw. zweiter Joker, z. B. ⏪ und ⏩).
  So passt eine Belegung zu jedem Modus, auch zu selbst gebauten.
- Kontingente, Abklingzeit und Sperren hängen **am Spieler**. Ob Handy oder Taster auslöst, ist egal.
  Beides läuft durch dieselbe Server-Prüfung.

## 2. Wer darf was

| Aktion | Wer | Warum |
|---|---|---|
| Taster **anlernen** und entfernen (`devices.json`) | Besitzer 🔒 | dauerhaft, Schutz vor fremden Geräten |
| Taster einem Spieler **zuordnen**, Tasten **belegen** | Spielleiter (und Besitzer) | gilt für den Abend, ändert sich mit den Leuten |
| Eigenes Handy einem Platz zuordnen | jeder beim Beitreten | „Neuer Platz“ oder „Zu Platz *Oma 🔘* dazu“ |

## 3. Anlernen (Besitzer)

🔒 → **🔘 Funk-Taster**. Die Liste zeigt pro Gerät Name, Typ, Tastenzahl, Batterie, Signal, „zuletzt
gesehen“ und an wen es gerade vergeben ist.

1. **＋ Taster anlernen** startet einen Lernmodus von 30 s: „Drück jetzt eine Taste am Taster“.
   Angenommen wird nur ein Gerät, das **in diesem Fenster** drückt und genug Signal hat. Nachbar-Geräte, die
   nur in Reichweite sind, erscheinen als Hinweis, werden aber nicht übernommen.
2. Erkannt: Typ und Tastenzahl (z. B. Shelly BLU Button1 = 1 Taste, Shelly BLU RC Button 4 = 4 Tasten). **Name** vergeben, z. B. „Taster Rot“.
3. Bei mehreren Tasten: **„Jede Taste einmal drücken“**. Im Bild leuchtet die jeweils gedrückte Taste auf.
   So stimmt die Zuordnung „links/rechts“ sicher.
4. Weiter zur **Belegung** (Abschnitt 4), oder „Später“.

Entfernen geht per Halten. Batterie schwach → Hinweis in der Liste und beim Spielleiter.

## 4. Belegung und Zuordnung (Spielleiter)

Erreichbar über **Mehr → Spieler & Handys → Spieler antippen → Geräte** oder direkt aus der Taster-Liste.

**Vorlagen für Mehrfach-Geräte** (ein Tipp, danach anpassbar):

| Vorlage | Ergebnis |
|---|---|
| 1 Spieler: ⏪ links, ⏩ rechts | eine Fernbedienung, ein Spieler, beide Joker |
| 2 Spieler à 2 Tasten | zwei Nachbarn teilen sich eine Fernbedienung |
| 4 Spieler à 1 Taste | vier Tasten, je ein Spieler mit Joker 1 |
| Eigene Belegung | Tabelle Taste × Ereignis → Spieler → Aktion |

**1-Tasten-Geräte**: einfach = Joker 1. Optional „Doppeldruck = Joker 2“ mit dem Hinweis „macht jeden
Einfach-Druck ca. 0,3 s langsamer“ (der Taster muss abwarten, ob ein zweiter Druck kommt). Empfehlung für
zwei Joker: ein Gerät mit zwei Tasten.

Beim Zuordnen kann man einen vorhandenen Spieler wählen oder **„＋ neuer Spieler“** (Zufallsname).
Spieler-Chips zeigen kleine Symbole 📱/🔘, damit man sieht, wer womit spielt.

## 5. Handy dazu

„Mitspielen“ bleibt ein Tipp. Nur wenn es Plätze **ohne Handy** gibt (z. B. reine Taster-Spieler), fragt
das Handy: **„Neuer Platz“** oder **„Zu Platz *Oma 🔘* dazu“**. Nichts muss vorher entfernt werden. Ein Spieler
mit Handy und Taster sieht am Handy auch, was der Taster ausgelöst hat, und den Verbrauch.

## 6. Rückmeldung ohne Display

- Der Taster selbst blinkt bzw. piept beim Druck (Shelly), das bestätigt nur „gesendet“.
- **Ticker** auf allen Handys: „🔘 Oma hat gespult“.
- **Abgelehnte Drücke** (Sperre, Kontingent leer) erscheinen dezent im Ticker des Spielleiters, weil der
  Taster kein Display hat.
- Später möglich: Status-LED am Louie kurz in der Spielerfarbe.

## 7. Datenmodell

```json
// devices.json – dauerhaft (Besitzer)
{"devices": [
  {"id": "d1", "name": "Taster Rot", "tech": "bthome", "model": "shelly-blu-button1",
   "addr": "38:39:8f:aa:bb:01", "keys": 1, "key": null, "last_seen": 1793560000, "battery": 92}
]}

// Abend-Zustand (RAM, optional gesichert) – Spielleiter
{"players": [
  {"pid": "p3", "name": "Kapitän Keks", "color": "red", "phone": null,
   "inputs": [{"dev": "d1", "btn": 0, "ev": "single", "act": "joker1"},
              {"dev": "d1", "btn": 0, "ev": "double", "act": "joker2"}]}
]}
```

`key` nimmt später den BTHome-Schlüssel auf (verschlüsselte Taster, Schutz gegen Nachsenden).

## 8. Offene Punkte

- [ ] Machbarkeitstest Stufe 0 aus [idee-funk-taster.md](idee-funk-taster.md) (BLE + Hotspot + 8 Handys, RAM)
- [ ] Belegung für den Abend sichern, damit sie einen Neustart übersteht?
- [ ] Soll der Spielleiter auch anlernen dürfen (Einstellung), damit Gäste ihre eigenen Taster mitbringen können?
