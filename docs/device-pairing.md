# Players, devices and pairing

Status: 2026-11-06 · proposal. Wireless button = **BTHome over BLE, planned for V1** (other radio paths rejected). Extends [web-ui-concept.md](web-ui-concept.md) (section 4.2).
Wireless button technology: [idea-wireless-buttons.md](idea-wireless-buttons.md). Clickable in [web/poc](../web/poc/index.html)
(simulation bar "Wireless buttons" (PoC: „Funk-Taster“), scenarios "Family with buttons" (PoC: „Familie mit Tastern“) and "Mixed" (PoC: „Gemischt“)).

## 1. Principle

The virtual game is deliberately separate from the table. At the table, what everyone sees counts. In the app, only
players with an input device count.

- **Player** = a seat in the app: name (random name by default, editable by hand), color (optional,
  duplicates allowed), joker allowances, titles and statistics.
- A player has **0..1 phone** and **0..n inputs**. So a player can have: only a phone, only
  buttons, both or nothing. Without a device a player only makes sense with "📊 Statistics & elimination".
- An **input** is **device + key + event** (single / double / long) → **action**:
  joker 1, joker 2, "I'm out" (only with statistics) or nothing.
- **Joker 1 / joker 2** refer to the **current mode** (first or second joker, e.g. ⏪ and ⏩).
  So one assignment fits every mode, including custom ones.
- Allowances, cooldown and locks belong **to the player**. It does not matter whether a phone or a button triggers.
  Both go through the same server check.

## 2. Who may do what

| Action | Who | Why |
|---|---|---|
| **Pair** and remove buttons (`devices.json`) | owner 🔒 | permanent, protection against foreign devices |
| **Assign** a button to a player, **map** keys | game master (and owner) | valid for the evening, changes with the people |
| Assign your own phone to a seat | everyone when joining | "New seat" or "Join seat *Grandma 🔘*" |

## 3. Pairing (owner)

🔒 → **🔘 Wireless buttons**. The list shows for each device name, type, number of keys, battery, signal, "last
seen" and who it is currently assigned to.

1. **＋ Pair button** starts a 30 s pairing mode: "Press a key on the button now".
   Only a device that presses **within this window** and has enough signal is accepted. Neighboring devices that
   are only in range appear as a hint but are not added.
2. Detected: type and number of keys (e.g. Shelly BLU Button1 = 1 key, Shelly BLU RC Button 4 = 4 keys). Assign a **name**, e.g. "Red button".
3. With several keys: **"Press each key once"**. The picture highlights the key being pressed.
   This makes the "left/right" assignment reliable.
4. Continue to **assignment** (section 4), or "Later".

Remove by holding. Low battery → hint in the list and for the game master.

## 4. Assignment and mapping (game master)

Reachable via **More → Players & phones → tap player → Devices** or directly from the button list.

**Templates for multi-key devices** (one tap, adjustable afterwards):

| Template | Result |
|---|---|
| 1 player: ⏪ left, ⏩ right | one remote, one player, both jokers |
| 2 players with 2 keys each | two neighbors share one remote |
| 4 players with 1 key each | four keys, one player each with joker 1 |
| Custom assignment | table key × event → player → action |

**1-key devices**: single = joker 1. Optional "double press = joker 2" with the hint "makes every
single press about 0.3 s slower" (the button has to wait whether a second press follows). Recommendation for
two jokers: a device with two keys.

When assigning, you can pick an existing player or **"＋ new player"** (random name).
Player chips show small icons 📱/🔘 so you can see who plays with what.

## 5. Adding a phone

"Join game" stays one tap. Only if there are seats **without a phone** (e.g. button-only players) does
the phone ask: **"New seat"** or **"Join seat *Grandma 🔘*"**. Nothing has to be removed first. A player
with phone and button also sees on the phone what the button triggered, and the usage.

## 6. Feedback without a display

- The button itself flashes or beeps on press (Shelly); this only confirms "sent".
- **Ticker** on all phones: "🔘 Grandma rewound".
- **Rejected presses** (lock, allowance used up) appear unobtrusively in the game master's ticker, because the
  button has no display.
- Possible later: status LED on Louie briefly in the player color.

## 7. Data model

```json
// devices.json – permanent (owner)
{"devices": [
  {"id": "d1", "name": "Red button", "tech": "bthome", "model": "shelly-blu-button1",
   "addr": "38:39:8f:aa:bb:01", "keys": 1, "key": null, "last_seen": 1793560000, "battery": 92}
]}

// Evening state (RAM, optionally saved) – game master
{"players": [
  {"pid": "p3", "name": "Captain Cookie", "color": "red", "phone": null,
   "inputs": [{"dev": "d1", "btn": 0, "ev": "single", "act": "joker1"},
              {"dev": "d1", "btn": 0, "ev": "double", "act": "joker2"}]}
]}
```

`key` will later hold the BTHome key (encrypted buttons, protection against replay). Additional technical
fields (packet ID, counter, RSSI): [idea-wireless-buttons.md](idea-wireless-buttons.md) 6.4. Storage location and format
(NVS or file) are defined in [firmware-architecture.md](firmware-architecture.md); `devices.json` stands for
the content here.

## 8. Open items

- [ ] Radio test on the test setup ([test-hardware.md](test-hardware.md): BLE + hotspot + 8 phones, heap)
- [ ] Save the evening's assignment so it survives a restart?
- [ ] Should the game master also be allowed to pair (setting), so guests can bring their own buttons?
