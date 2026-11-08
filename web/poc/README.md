# Web UI proof of concept (test environment)

Clickable prototype of the web UI following [docs/web-ui-concept.md](../../docs/web-ui-concept.md) and
[docs/mode-builder.md](../../docs/mode-builder.md).
A single file (`index.html`), vanilla JS, no external dependencies, runs offline.

**Language:** the PoC UI is in German (by decision; it is a throwaway prototype). The final web UI will be
multilingual. Quoted UI labels below are the German strings shown in the PoC, with an English gloss where helpful.

## Opening

Open `index.html` directly in the browser (`file://` is enough, no server needed).
In the built-in or shared browser this also works: `python3 -m http.server 8776 -d web/poc`
(pick a free port) and then open `http://localhost:8776/`.

- **Desktop (≥ 700 px):** the test environment on the left, several simulated phones on the right (375 × 720 px each).
- **Narrow (< 700 px, real phone):** one phone full screen, with a thin test bar at the top containing a
  phone switcher, lever, "＋📱" and 🧪 (expands the full test environment).

## What is simulated

- **Server** (JS object, single source of truth): phases Ready/Countdown/Running/Pause/End/Sleep,
  lever, battery, stall detection, roles (leader, player, spectator, owner session), player phones,
  player list (joker accounts, out status, result and title belong to the player, not to a colour), shared joker lock,
  rewind lock, ticker, requests (control/join) with 15 s timeout, orphaned control, seat guarantee, lever mode,
  test operation (test drive/workshop: the lever then does not start a round). The server checks all permissions;
  rejected actions come back as a toast with a reason.
- **Game modes schema 2** (flight plan · spice · jokers · end): segments constant, ramp, steps, sawtooth
  (hard/soft, snap-back kick, rising/falling), wave (sine/heartbeat), random, pause, with `repeat` and
  "afterwards: from the start / hold / end". Speed −100…100 % (0 % = minimum speed, 100 % = centrifugal limit),
  direction changes with a short stop. Jokers ⏩ boost, ⏪ rewind, 🛑 brake, 🎭 fake brake with "who may"
  (all/active/ghosts), account per type or shared, cooldown, shared lock. Every number is the value
  for nastiness 3 or a list of 5. One interpreter for game, preview, workshop and builder.
  Built in: Klassisch (classic), Druckkochtopf (pressure cooker), Würfelmotor (dice motor), Turbulenzen (turbulence),
  **Rückspul-Duell (rewind duel, ⏪ + ⏩)**, Letztes Huhn (last chicken).
- **Mode builder** (Modi → "＋ Neuer Modus" or ⧉ "Kopieren & bearbeiten"): template gallery (incl.
  sawtooth and the example **Gewitter** (thunderstorm)), overview with a fixed preview curve (clamped, reverse in red,
  spice/joker symbols, ▼ snap-back) and nastiness switcher, pages for flight plan (segment cards with
  ⋯ menu and undo), spice, jokers, end, live hints with one-tap suggestions, dry run with
  test players (bots), test drive, save with name/symbol/sentence, pro (nastiness table, JSON, import).
  The example "Sägezahn-Duell" (sawtooth duel) from the concept can be clicked through step by step.
- **Joining = one tap**: name from the name dice 🎲 or by hand ✏️. **Colour optional** (🎨: red, yellow, green, blue,
  purple, orange, turquoise, pink or none), default is neutral; colours may appear more than once. Leader and owner
  change the name and colour of any player (tap the player row or Players & phones).
- **Player count** (🔒 owner → limits, 2–8, default 4) limits the playing phones incl. a playing leader;
  after that "Alle Plätze belegt (4/4)" (all seats taken). Up to 8 players fit without scrolling (compact chips in 2 rows).
- **Player = seat** (name, colour optional) with 0..1 phone and 0..n **wireless button inputs** (device + key +
  single/double/long → joker 1, joker 2 = first/second joker of the mode, "Ich bin raus" (I'm out) only with statistics, or nothing).
  Quotas, cooldown and lock belong to the player, regardless of whether triggered by phone or button. Chips show 📱/🔘.
  Anyone with neither phone nor button does not appear in the app.
- **🔘 Pairing wireless buttons** (🔒 owner → 🔘 Funk-Taster): device list (type, keys, 🔋, 📶, last seen, assigned),
  "＋ Taster anlernen" (pair button) = 30 s learning mode ("Drück jetzt eine Taste" – press a key now; only nearby devices,
  signal better than −70 dBm) → type detected → name → for multi-key devices "Jede Taste einmal drücken" (press each key once)
  → assignment. Remove by holding. Hint about other people's devices in range.
- **Assignment** (control phone for the evening, owner too; More → 🔘 Funk-Taster or player sheet → "＋ Taster zuordnen"):
  templates "1 player ⏪/⏩", "2 players with 2 keys each", "4 players with 1 key each", "custom"; table key → player
  (existing or "＋ new player" with random name) → action. 1-key devices: optional "double press = joker 2" (hint: makes
  single presses about 0.3 s slower).
- **Phone joining**: if there are button-only seats, you choose "new seat" or "🔘 join seat …".
- **Button jokers** go through the same server check; ticker "🔘 ⏪ Oma hat zurückgespult" (Grandma rewound). Rejected button
  presses (lock, empty, not assigned) appear discreetly only in the control phone's ticker.
  "Statistics & elimination" and "last player" only refer to phone players; everyone sets themselves to
  "out", the leader only for correction (e.g. orphaned phone).
- **🔄 Player change** (party: fixed phones at the seat, changing people): on the player phone in Ready/End
  or in the leader's player sheet. New random name, colour stays, evening values reset, ticker
  "Platz von Lena: jetzt Kapitän Keks" (Lena's seat: now Captain Cookie). When joining, the random name is the default.
- **Spectators** see a muted, striped page with 👀; players are neutral with a name tag.
- **Permission "create modes"** (owner → permissions): off / drafts (default for children) / save.
- **Gamepad**: 1 joker = large round hold button, 2 jokers = two halves (⏪ left, ⏩ right) with their own
  dots and cooldown bars, with a shared account the dots are centred. After "Ich bin raus" ghost layout.
- **"📊 Statistik & Ausscheiden" (statistics & elimination)** (default OFF; leader under More → Players & phones, default
  in 🔒 owner → permissions). No automatic switch-on by the mode. OFF: no "I'm out", no tapping the winner, no out
  correction, no winner banner, no ghost layouts; ghost jokers are inactive, round end "last player" does not apply
  (mode card/detail and builder discreetly show "👻 Geister-Joker nur mit Statistik & Ausscheiden" – ghost jokers only
  with statistics & elimination).
  ON: "I'm out", winner, ghost jokers, "last player" and a small **evening statistic** (wins and jokers per
  player; reset on player change or restart). Titles from joker events always exist.
- **Control phone**: two-way choice "🎛️ Nur steuern / 🎮 Steuern + mitspielen" (control only / control + play; play =
  choose a colour, same gamepad as everyone plus leader bar, player phones are switched on too).
- **Calibration** (wizard and workshop): minimum speed (= 0 %) and centrifugal limit (= 100 %) with a small
  sketch. The top view shows "stockt" (stutters) below the minimum speed and "fliegt zu hoch" (flies too high) from the
  limit or at 100 %.
- **Lever confirmation**: only if the control phone has not answered for 15 s or is orphaned. Gesture: lever on-off
  3× quickly (within 4 s); in the simulation click the big lever button three times quickly.
- **After sleep/restart** the last control phone has priority for 20 s (real: 2 min).
- **Pause → continue** (hold 1 s) always goes through 3-2-1. Hold buttons give a hint if tapped too briefly.
- **Owner session** lasts until "Abmelden" (log out, header) or 5 min idle.
- **Phones**: each instance is its own session (token) with its own navigation. "WLAN trennen" (disconnect Wi-Fi),
  "neu laden" (reload; the token restores role and player seat), "✕" remove. Up to 9 phones (so that "all seats taken"
  can be tested).
- **🔘 Wireless buttons (simulated)** in the test bar: "＋ Gerät" (device: Button1, RC Button 4, WiZmote, a neighbour's
  foreign device), keys with click = single, double click = double, hold 1 s = long, battery and signal sliders,
  latency (BLE ≈ 350 ms, ESP-NOW ≈ 20 ms) and blink feedback.
- **Top view**: players as dots around the tower (grey or in their colour, 👻 when out), up to 8.
- **Time lapse** for server time. Deadlines are shortened: orphaned control and seat guarantee 20 s instead of 2 min.
- **Event log**: messages phone → server, server → phone(s) and hardware in WS format;
  `state` messages and heartbeats only with the checkbox ticked.

Owner password in the PoC: **`louie`** (or the one set in the wizard).

## Scenarios (quick start in the test environment)

| Scenario | Content |
|---|---|
| 🆕 First start / wizard | captive portal "Im Browser öffnen" (open in browser), then 8 steps (model, direction of rotation, minimum speed, centrifugal limit, password, Wi-Fi, profile, done). The hardware initially turns the wrong way; Louie only turns reliably from 18 % raw value and flies too high from 72 % |
| 👪 Family evening | Dad controls alone, everyone plays without a phone |
| 🧒 Children's birthday | profile Kinder (children: cap 55 %, 3 modes, nastiness ≤ 3, never reverse, modes only as draft) |
| 🎉 Party (4 phones) | Lena (red), Max and Oma (neutral) play with phones, rewind duel with ⏪ and ⏩ |
| 👻 Ghost hour (last chicken) | statistics & elimination on: "I'm out", ghost boost, last player wins, evening statistic |
| 🔄 Party rotation | 4 fixed phones (seats 1–4), "🔄 player change" between rounds |
| 🔘 Family with buttons | Dad controls with a phone, 4 Button1 for Oma/Opa/Mia/Tim (single = ⏪, double = ⏩), rewind duel, plus a neighbour's foreign device |
| 🔀 Mixed | Lena and Max with phones, RC Button 4: keys 1/2 = Max (phone + button), 3/4 = Oma (button only) |
| 🍽️ Big table (8 phones) | player count 8, Dad controls and plays, red twice and blue twice; "+ phone" → the 9th phone sees "Alle Plätze belegt (8/8)" (all seats taken) |
| 🚪 Guest joins a running round | spectator → "Mitspielen?" (join?) → colour → "nächste Runde dabei" (in next round) |
| 📵 Control phone disappears | Dad offline, after 20 s "Steuerung übernehmen" (take over control) |
| 🔧 Workshop | Dad as owner in the workshop (lever on for "Echt" – real) |

## Limits of the PoC

The QR code is a placeholder pattern; backup/restore/update only as a hint. Builder: no QR/file export,
import only via text field, per-player advantage (handicap) only as a switch in the mode, not in the round.
Calibration without the perceptibility and idle-current step.
