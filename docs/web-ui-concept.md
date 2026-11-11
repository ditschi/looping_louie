# Web UI concept: roles, views, game modes, workshop

Status: 2026-11-06 · proposal, replaces sections 4 and 6.2 of [software-concept.md](software-concept.md)
in the points named. Clickable proof of concept: [web/poc/index.html](../web/poc/index.html).

Developed by a team of agents: critique of the old draft (`web/prototype/`), usage scenarios,
role model, game mode concept. Then merged, built and checked with persona tests.

## 1. Picture of the game

**Louie is the pilot** in the plane that circles the tower. Each player has a **paddle**
and uses it to protect **three chickens** (chips). Whoever has lost all chickens is out.
The UI always shows Louie as plane/pilot ✈️, chickens only as the players' chips 🐔.

**Speed scale**: 0 % = **minimum speed** (Louie just turns reliably), 100 % = **centrifugal limit**
(above it Louie no longer drops because of the centrifugal force and stops hitting chickens; unplayable).
Negative values = backwards. Both points are calibrated per device.

**It is about the fun at the table.** Everyone sees live who is in and who drops out. Chickens are not
counted, and nobody has to record in the phone that they are out. For that there is the optional
setting **"📊 Statistics & elimination"** (PoC: „Statistik & Ausscheiden“, default **off**). When it is off,
the UI shows none of it: no "I'm out" (PoC: „Ich bin raus“), no winner, no ghost jokers, no round end "last player".
When it is on, everyone reports with "I'm out", the game master can tap the winner, and there is an
evening statistic. Automatic titles from joker events ("Master Meanie", PoC: „Oberfiesling“) always exist, because they
need no input.

## 2. What the old draft gets wrong (summary)

- One long scrolling page (lobby about 1.5 screens, EMERGENCY STOP below the visible area).
- Without a game master anyone may change mode and meanness → wild switching.
- Whoever taps first becomes game master; what the role may do and how to hand it over is stated nowhere.
- No setup wizard, no test mode, no modes page, Louie shown as a chicken.
- Good and kept: phase determines the view, QR + tap a color, big hold button with
  ring, "who rewound", ghost boost, honest connection/battery hints, lever hints.

## 3. Usage scenarios (selection, by frequency)

| # | Scenario | Phones | Consequence |
|---|---|---|---|
| S2 | **Family evening** (primary case) | 1 | One page is enough. Phone lies flat on the table, hands on the paddles |
| S8 | Playing without a phone | 0 | separate **lever mode** (not "last selected"), so Grandma does not get chaos |
| S3 | Children's birthday party, controller does not play | 1 | "Control only", Kids profile, quick restart |
| S4 | Party with guest phones | 1 + 3–7 | switch on player phones explicitly, QR, onboarding < 30 s |
| S5 | Guest arrives during the round | +1 | watch, "you're in next round" |
| S6 | Controller phone gone / battery empty | – | handover without password, take over orphaned role |
| S7 | Adjust mode at the table | 1 | "this round only" vs. save, test drive |
| S1/S10 | First setup, giving it as a gift | 1 | wizard with model, direction, minimum speed, centrifugal limit, password |
| S11 | Developing new modes | 1 (+PC) | **workshop**: dry with time-lapse, real with dead-man button |
| S9 | Troubleshooting | 1 | diagnostics behind the lock |

Physical constraints: during the round the phone is mainly a **display**, with at most
two huge targets. Readable from 60–80 cm, no swipe gestures, no forced landscape. Without
HTTPS there is no Wake Lock, so after waking up the phone must show the correct state immediately.
Lever and LED are the truth. For children: colors and symbols instead of text.

## 4. Roles

Users see only three things: **Control**, **Join game** and the **lock 🔒**.

| Role | How | May |
|---|---|---|
| **Spectator** | open the page (state "connected without role", not a selectable role) | see status, "Join game?" or "Request control" |
| **Player** | only when player phones are on: tap "Join game" (one tap) | jokers per mode, "I'm out" (if tracked), stop |
| **Game master** (exactly one) | automatically the first phone when control is free; otherwise handover | mode, meanness, player phones on/off, pause/stop, manage players, test drive, adjust modes |
| **Owner** (admin) | password behind the lock, valid until "Log out" or 5 min idle (header shows "🔓 Owner") | additionally workshop, setup, Wi-Fi, limits, profiles, permissions, update |

**Game master ≠ owner.** The game master needs no password. Everything he triggers is clamped by
the server to the owner limits. A child on the game master phone can therefore at most change mode and
meanness, and in the "Kids" profile only within the released modes.

### 4.1 Becoming game master and handing over

1. **Automatic**: if control is free, the first phone becomes game master, without a click.
   After first setup, the setup phone is game master.
2. **Request**: another phone taps "Request control". The game master gets a banner
   "Lena wants to control – Hand over / Decline".
3. **Lever confirmation**: only if the game master **does not answer** (15 s) may the requester
   **flip the lever 3× quickly** (on-off three times within 4 s; 30 s window, only in READY/END, motor
   stays off). Physical access beats radio. An explicit **"No" counts**: then there is
   no escalation. During a round the request waits. While the window is open, **all** phones show
   "Lever is confirming Max as controller – do not use it to start", and the game master
   can cancel. When declining there is also "Block for today" (control and join requests).
4. **Orphaned**: if the game master phone is disconnected for 2 min (in a round: until round end plus 2 min),
   everyone sees "Take over control".
5. **Hand over** in the game master menu: to a specific phone or "release" (with confirmation).
6. **After sleep/restart** the last game master's phone has priority for 2 min, so that a guest phone that
   happens to connect first does not become game master.
7. Owner setting **"Who may control"**: anyone (default) / only with lever confirmation (default in the Kids profile) / owner only.

### 4.2 Player phones (multiplayer)

- **Default: off.** Other phones are spectators and see status plus "Join game?". The request
  goes as a banner to the game master, who accepts it with one tap. This also switches player phones on.
- The game master switches on **"Player phones"** on the game page. His phone shows a QR code
  (full screen for showing around). Whoever joins taps **"Join game"** and is in: the name comes from the
  **name dice**, and it can be **edited by hand** at any time (text field).
- **Color is optional.** Default is a **neutral background** without color. Whoever wants picks a
  color (quick pick of the standard colors red, yellow, green, blue, plus purple, orange, turquoise, pink). **Colors
  may appear more than once** (e.g. two combined games with red each). Game master and owner can
  assign or remove a player's color.
- **Number of players** is a global owner setting (default 4, up to 8 for modifications and combined
  games). It limits the participating phones. Whoever comes after that sees "All seats taken".
- **A player is a seat with input devices.** The virtual game is deliberately separate from the table:
  whoever has no device does not appear in the app and simply has no jokers. A player can be assigned
  **a phone, one or more wireless buttons, both or nothing** (without a device only useful with
  statistics). Whoever joins by phone chooses "New seat" or "Join seat *Red (button)*"; nothing has to
  be removed first. Pairing and key assignment: see [device-pairing.md](device-pairing.md), technology in [idea-wireless-buttons.md](idea-wireless-buttons.md).
- **Fixed phones at the seat, changing people** (party): a phone stays on the chair, the people
  rotate. That is why the random name is the default, and there is **"🔄 Player change"**: new random name,
  the evening's values (titles, advantage) reset, without rejoining.
- The game master can remove players (second tap to confirm). Removed phones can only
  rejoin when the game master accepts a new request.
- Joining during the round is possible, but you only play from the next round.
  **Allowances belong to the player** (session token), not to the color; reloading resets nothing.
  At the countdown it is recorded who plays. Result and titles refer to that.
- **Spectators** (later): own, clearly different look from the neutral player background,
  possibly with their own weak spectator jokers.
- Switching off is only possible in READY/END. Players then become spectators again.

### 4.3 Control only or also play (game master)

A clear choice on the game page: **🎛️ Control only** (default) / **🎮 Control + play**.
When playing (color optional as for everyone), the game master gets **the same gamepad as everyone** during the round
(all jokers of the mode, e.g. forward boost and rewind kick, same allowances) plus a narrow
game master bar (pause, stop, menu). Playing along only makes sense with player phones switched on
and switches them on too.

### 4.4 Permissions

| Action | Spectator | Player | Game master | Owner |
|---|---|---|---|---|
| See status | ✓ | ✓ | ✓ | ✓ |
| Stop / emergency stop in the UI | – | ✓ | ✓ | ✓ |
| Jokers (boost, rewind …), "I'm out" (for oneself) | – | ✓ | ✓ if playing | – |
| Select mode, meanness, adjust "this round only" | – | – | ✓ (lever off) | ✓ |
| Player phones on/off, remove players, tap winner | – | – | ✓ | ✓ |
| Pause, release round | – | – | ✓ | ✓ |
| Save mode | – | – | ✓ if allowed | ✓ |
| Test drive (10 s, lever on) | – | – | ✓ | ✓ |
| Profile Kids/Family/Party | – | – | – | ✓ |
| Workshop, calibration, Wi-Fi, limits, permissions, update | – | – | – | ✓ |

The UI stop is sent by a phone with a role, not by spectators (anyone within radio range can be one).
It is never throttled and is shown with the name. **The real emergency stop is the lever**, and the
UI says so.

### 4.5 Edge cases

- Game master battery empty or tab in background: the round continues, the lever always stops.
- Two phones want to lead at the same time: the server assigns atomically, first come first served.
- Reload or short Wi-Fi dropout: the token restores role, name and color.
- Sleep or restart: all roles free, player phones off.

## 5. Views

Principle: **a normal round needs only one page without scrolling** (goal: everything important visible in
375 × 640 px). The game page **changes with the phase**. Settings are always
reachable via the bottom bar, during the round via a small menu button.

### 5.1 Controller phone (game master)

Bottom bar with three tabs: **Game · Modes · More**.

| Phase | Game page shows |
|---|---|
| **Ready** | Large status line ("Flip the lever to start"), lever mirror (display only), **mode card** (tap → Modes), **meanness** as 5 levels, **Players** row (players with name/color and occupancy "2/4", switch "Player phones", choice "Control only / play") |
| **Countdown** | Full screen 3-2-1 on all phones |
| **Running** | Full screen without bar: speed large, mode, remaining time if any, ticker of events (who used which joker), 4 color tiles with status (phone, out), at the bottom two large buttons **Pause** and **Stop** (hold to stop). Small at the top: ☰ menu |
| **Pause** | Resume (hold, then countdown again "Hands on the paddles!") / Stop |
| **End** | optionally tap winner / titles from joker events ("Master Meanie"), meanness directly changeable, "Again = lever off and on again" (hint only, no misleading button), change mode. After a technical abort (blocked, battery) a red status card on all phones and no titles |
| Winner | Only with "Statistics & elimination": if only one player is left, banner "🏆 Lena has won – lever off" |
| Hints | Lever to off first · Louie is asleep · Battery low · Blocked · Connection lost |

**Modes**: cards of the modes with icon, short sentence, phone requirement (0 / 1 / all) and mini curve.
Tap → detail with preview curve and **meanness**. "Adjust" opens a few sliders and
"For this round" or "Save as new mode". "Test drive 10 s" only works with lever on.

**More**: Players & phones (QR, list, remove), hand over control, lever mode (mode without phone),
help/game rules, 🔒 owner area.

### 5.2 Other phones

| State | View |
|---|---|
| Player phones off | **Spectator**: status, mode, speed; "Join game?" and "Request control" |
| Player phones on, not yet in | **Join game**: one large button, above it the name (🎲 / ✏️), "Seats 2/4" |
| Ready (in) | Own name large, neutral background or own color, "🎨 Color" (optional), mode, "Waiting for lever", own jokers for the next round |
| **Running** | **Gamepad**: one or two large hold buttons (jokers per mode, layout see [mode-builder.md](mode-builder.md)) with fill ring, allowance dots, cooldown ring and global lock. Below, small: "I'm out" (only if tracked, hold), stop |
| Out | **Ghost**: ghost boost button, if the mode provides one |
| End | Result, titles ("Master Meanie"), waiting for next round |

Messages (toasts) appear at the **top** and never cover controls. Buttons do not move
under the finger. Technical terms (interpreter, dead-man, fake-out) appear only in the workshop.

### 5.3 Owner area (🔒)

Profile Kids/Family/Party · speed cap · reverse and party limits · permissions ("Who may
control", saving modes) · **workshop** · Wi-Fi · device (model, calibration, password,
backup/restore, update, reset) · diagnostics. Each area is its own subpage, not a long list.

### 5.4 First setup

Wizard with 6 steps, each step fits on one screen: model → direction
("Lever on. Is Louie flying the right way round?") → minimum speed (slider up until Louie turns reliably) → centrifugal limit (further up until Louie no longer drops) →
owner password plus lever confirmation → home Wi-Fi (optional) → done (QR sticker, louie.local).

## 6. Game modes

### 6.1 A mode consists of four layers

| Layer | Content | Example |
|---|---|---|
| **A Flight profile** | sequence of segments: `const`, `ramp`, `steps`, `random`, `wave` | Pressure Cooker: ramp 40 → 100 % in 120 s |
| **B Spice** | events: jolt, fake-out brake, pause, creep + sprint, short reverse kick; frequency/min, duration, warning | Turbulence |
| **C Player actions** | rewind, boost, brake; `who` = all / remaining / eliminated; allowance, cooldown, global lock | Rewind Duel |
| **D Round end** | lever (always), time, last player | Time Race 90 s |

- **Every mode must be playable without layer C.** The phone requirement is derived from the layers.
- **Meanness 1–5**: the mode defines level 3. A fixed table scales speed, event frequency
  and cooldowns. Level 1 never has reverse and no fake-outs.
- **Clamp chain** in fixed order, each stage can only tighten: mode → meanness →
  "this round" → profile speed cap → owner limits → motor layer. The preview shows
  the **clamped** curve. The browser computes it via WebAssembly from the same Rust core crate as the
  firmware (fallback: server computation via `POST /api/modes/preview`).

```json
{
  "id": "turbulenz", "v": 1, "name": "Turbulence", "icon": "🌪️", "owner": "builtin",
  "profile": [{"type": "random", "min": 35, "max": 80, "every_s": [3, 6], "for_s": null}],
  "spice":   [{"kind": "jolt", "per_min": 4, "dur_s": 0.4, "warn_s": 0.5, "from_s": 10},
              {"kind": "fakeout", "per_min": 2, "dur_s": 1.0}],
  "actions": [],
  "end":     {"type": "lever"}
}
```

### 6.2 Built-in modes

The built-in modes ship with the default UI package; Classic is also in the firmware as fallback lever mode. The
device reads them into its mode catalog and can offer them without a phone
([firmware-architecture.md](firmware-architecture.md) 6.4). Another UI package can bring other modes.

| Mode | Idea | Phones |
|---|---|---|
| ✈️ **Classic** (PoC: „Klassisch“) | constant speed, gentle start (also the default lever mode) | 0 |
| 🔥 **Pressure Cooker** (PoC: „Druckkochtopf“) | gets steadily faster, rounds end by themselves | 0 |
| 🎲 **Dice Engine** (PoC: „Würfelmotor“) | random speed at random intervals | 0 |
| 🌪️ **Turbulence** (PoC: „Turbulenzen“) | Dice Engine plus jolts and fake-out brakes | 0 |
| ⏪ **Rewind Duel** (PoC: „Rückspul-Duell“) | Classic plus rewind joker for everyone | per player |
| 👻 **Last Chicken** (PoC: „Letztes Huhn“) | Pressure Cooker, eliminated players get ghost boost (ghost jokers only with "Statistics & elimination") | per player |

Modes that need player phones can be selected without player phones, but then run without
layer C. The card shows this with "Player actions off – switch on phones?".

### 6.3 Three depths of operation

1. **Quick pick** (V1, game master): tap the card, choose meanness.
2. **Adjust** (V1, game master): 1–3 sliders per layer (speed, jokers, time limit),
   "for this round". Saving only from level 2 and only if allowed.
3. **Mode builder** (game master, if "Create modes" is allowed): custom modes from templates and building blocks, see [mode-builder.md](mode-builder.md).

### 6.4 Life cycle

Built-in (read-only) → copy → adjust → save (`owner`, `based_on`) → share
as JSON file or QR link `http://louie.local/#m=<base64url>`. On import a preview shows
where clamping happens. An import cannot loosen any limits.

## 7. Workshop (test mode, owner only)

The workshop is clearly marked visually (striped border), and all limits apply here too.

**Lever in test operation**: normally lever on starts a round immediately. While the workshop
is open or a test drive is being prepared, the device is in **test operation**: lever on only
enables the motor, no round starts. Test drive sequence: tap "Test drive" → lever on →
hold button. Readiness expires after 60 s. If the test ends with lever on, it is followed by
"Lever to off first" (no surprise start).

- **Dry** (motor fixed at 0, also with lever off): play the mode at 0.5× / 1× / 4× / 16×,
  fixed random seed, curve "target" and "clamped", simulated players (spam / smart / never)
  and metrics (reverse share, estimated round duration, events per minute).
- **Real** (lever on, no round, battery ok): **dead-man button**. The motor only runs while the
  button is held (heartbeat 200 ms, stop after 500 ms without heartbeat). Only 0.5× or 1×,
  at most 60 s. Events can be triggered by hand ("Jolt now", "Rewind now").
  Rejected triggers state the reason ("Reverse lock 4 s left").
- **Calibration**: direction, minimum speed (= 0 %), centrifugal limit (= 100 %), perceptibility of jolts,
  idle current (basis of the block detection).

## 8. Consequences for protocol and concept

- WebSocket additionally: `request_lead`, `handover`, `release_lead`, `request_join`, `allow_players`,
  `kick`, `leader_plays`, `chick_lost`, `estop`; state: `multiplayer`, `leader_plays`, `lead_policy`.
- Additional permissions: `modes.select`, `modes.tweak`, `workshop.dry`, `workshop.motor`.
- Admin timeout 5 min instead of 30 min. "Guest" is now called "Spectator".
- New setting **lever mode** (mode without phone), independent of the last selected mode.

## 9. Languages (internationalization)

Decision 2026-11-03: the draft (`web/poc`) stays German. **The final version must be multilingual.**

- **Automatic detection** via the browser setting (`navigator.languages`, on first access also the
  `Accept-Language` header), fallback English. **Switch** at any time via More → Language; the choice is stored per
  phone (session token or `localStorage`).
- **Language scope (proposal, still to be confirmed):**
  - Main EU languages: English, German, French, Spanish, Italian, Polish, Dutch,
    Romanian, **Portuguese in the Brazilian variant (pt-BR)**, which is also understood in Portugal.
  - Widely spoken worldwide: Chinese (simplified), Hindi, Arabic, Japanese, Turkish, Indonesian,
    possibly Russian and Ukrainian.
- **Technology:**
  - All texts are in one file per language (JSON, key → text, with placeholders and plural forms
    via `Intl.PluralRules`). Numbers and times via `Intl.NumberFormat`.
  - The files are stored gzip-compressed in flash and only loaded when needed. Roughly 5–8 KB per language.
  - **No embedded fonts.** Chinese, Arabic, Hindi and Japanese use the phones' system fonts.
  - **Arabic is right-to-left:** build the layout from the start with CSS logical properties (`margin-inline-start`
    etc.) and `dir="rtl"`. Symbols like ⏪/⏩ keep their direction.
  - Children who cannot read: symbols and colors carry the meaning, text is secondary. This also helps with long
    translations (German, French).
  - Name dice: own word lists per language.
- **Translation:** English is the source language. All other languages are translated from English and
  proofread by native speakers before a release.

## 10. Open items

- [ ] Can you feel 0.3 s jolts? (prototype)
- [ ] Lever gesture flip 3×: reliably detectable in practice? The status LED should additionally show the window.
- [ ] "Who may control": is "anyone" as default safe enough for parties?
- [x] Counting chickens: dropped. Elimination and statistics are optional (default off).
