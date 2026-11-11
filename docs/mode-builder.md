# Mode builder: creating custom game modes

Status: 2026-11-06 · proposal, extends [web-ui-concept.md](web-ui-concept.md) section 6 (game modes)
and 7 (workshop). Extends the four-layer model (flight plan, spice, jokers, end) with sawtooth,
reverse speed in the flight plan, several joker kinds, joker accounts and a meanness table.

**Goal:** the game master builds a custom mode on the phone in under 2 minutes. Simple stays
simple (3 taps), complex is still possible (sawtooth with ⏩/⏪ jokers, ghost jokers, meanness table).
Principle: **every number has a good default. You only see what you want to change.**

## 1. Terms and speed scale

| UI term | Meaning |
|---|---|
| **Flight plan** | How fast Louie flies over time (layer A) |
| **Spice** | Random surprises from the device (layer B) |
| **Jokers** | Players' buttons on their phone (layer C) |
| **End** | When the round ends by itself (layer D, the lever always ends it) |
| **Meanness 1–5** | Difficulty, 🐣 Kids' Party (PoC: „Kindergeburtstag“) to 👹 Final Boss (PoC: „Endgegner“) |

**Speed** ranges from **−100 % to +100 %**:

```
 −100 %        −0 | 0 %                          100 %
 ◄── backwards ───┤├── forwards ───────────────────►
                   minimum speed       centrifugal limit
                   (turns reliably)    (unplayable above)
```

- 0 % means **minimum speed**, not standstill. Standstill is the **pause** segment (motor off).
- There is nothing between "0 %" and "−0 %". On a sign change the motor layer stops briefly
  (dead time) and starts in the other direction at minimum speed. The preview shows this as a small gap.
- Reverse is possible in the flight plan, in spice and in jokers. The owner limits (e.g. at most
  1.5 s at a time, at most 10 % share, reverse speed at most −50 %) always apply.

## 2. Data model (schema 2)

### 2.1 Overall structure

The JSON blocks in section 2 are sketches (`...` and `//` comments only for explanation); complete
examples are in sections 5 and 6.

```json
{
  "schema": 2, "id": "saegezahn-duell", "name": "Sawtooth Duel", "icon": "🪚",
  "desc": "Louie keeps getting faster and drops back. You push with ⏩ and ⏪.",
  "owner": "lena", "based_on": "saegezahn@1", "fies_default": 3, "handicap": true,
  "flight": { "segments": [ ... ], "after": "loop" },
  "spice":  [ ... ],
  "jokers": { "account": "separate", "lock_s": 5, "items": [ ... ] },
  "end":    { "time_s": null, "last_player": false, "plan_end": false },
  "seed": null
}
```

Derived (not in the JSON): `needs.phones` (there are jokers), `needs.out_report` (a joker with
`who: "alive"/"out"` or `end.last_player`). Only then does "I'm out" appear on the gamepads.

Where modes come from (firmware, UI package, own modes in LittleFS) and how they are selected:
[firmware-architecture.md](firmware-architecture.md) 6.4. The segment, spice and joker types of this schema are the
vocabulary of the core; a new type needs a firmware update, a new mode from existing types does not.

Compared with schema 1 (PoC), `profile` is now `flight.segments`, `actions` is called `jokers.items`, and `end` is flat
instead of `any/of`. The server upgrades schema 1 automatically on load.

### 2.2 Number or table: the meanness rule

**Every number in the mode is the value for meanness 3.** It is scaled automatically. Whoever wants
precision writes a **list with 5 values** (level 1–5) instead of the number; then nothing is scaled.

```json
"count": 2                  // automatic (count stays 2 at all levels)
"count": [4, 3, 2, 2, 1]    // table: Kids 4 jokers, Final Boss 1 joker
```

Automatic scaling (fixed in the firmware, matches the PoC):

| Field kind | 🐣 1 | 😊 2 | 😏 3 | 😈 4 | 👹 5 |
|---|---|---|---|---|---|
| Forward speed (all `v`, `from`, `to`, `min`, `max`) | ×0.7 | ×0.85 | ×1 | ×1.1 | ×1.2 |
| Reverse speed | **becomes 0 %** | ×0.85 | ×1 | ×1.1 | ×1.2 |
| Spice frequency (`per_min`) | ×0 | ×0.5 | ×1 | ×1.5 | ×2 |
| Joker strength (`strength`) | ×0.7 | ×0.85 | ×1 | ×1.1 | ×1.2 |
| Cooldown, lock (`cooldown_s`, `lock_s`) | ×1.6 | ×1.3 | ×1 | ×0.8 | ×0.65 |
| Joker count, durations, time limit | = | = | = | = | = |
| Joker ⏪ rewind kick | **becomes 🛑 brake** | | | | |

Reasoning: the **count** of jokers stays the same, so that "you have 3 jokers" stays reliable and
children do not have less fun. It gets meaner via strength, shorter cooldown and more spice.
Level 1 never has reverse. A ⏪ joker becomes a brake there, so the button stays.

### 2.3 Flight plan segments

Each segment has a duration (`for_s`, or it follows from the parameters) and optionally `repeat`
(count, default 1). `after` at the end of the plan: `"loop"` (from the start), `"hold"` (hold the last speed)
or `"end"` (round ends, only together with `end.plan_end`).

| Type | Symbol | Parameters (default) | More options |
|---|---|---|---|
| `const` Constant | ▬ | `v` 55, `for_s` 30 | – |
| `ramp` Ramp | ⟋ | `from` 30, `to` 80, `over_s` 60 | `curve` lin/exp |
| `steps` Steps | ▁▃▅ | `from` 30, `to` 90, `n` 4, `step_s` 15 | descending |
| `saw` **Sawtooth** | ⩘ | `from` 25, `to` 85, `rise_s` 10, `drop` hard, `repeat` 6 | `drop_s` (soft), `kick` kickback, `dir` rising/falling, `curve` |
| `wave` Wave | ∿ | `min` 35, `max` 75, `period_s` 20, `repeat` 3 | `shape` sine/heartbeat |
| `random` Random | 🎲 | `min` 30, `max` 85, `every_s` [2,6], `for_s` 60 | `fair` (no jump > 40 points) |
| `pause` Pause | ⏸ | `for_s` 3 | `warn_s` warning |

Sawtooth in detail: Louie rises in `rise_s` from `from` to `to` and then drops back, **hard**
(as fast as the motor layer allows) or **soft** (over `drop_s`). Optionally the `kick` adds
a short reverse kick at the drop (`{"v": -30, "s": 0.6}`). With `dir: "down"` the
speed falls slowly and jumps up ("inverted sawtooth").

### 2.4 Spice events

```json
{ "kind": "fakeout", "per_min": 2, "strength": 0, "dur_s": 1.0, "warn_s": 0, "from_s": 20 }
```

| `kind` | UI | Effect |
|---|---|---|
| `jolt` | ⚡ Jolt | short reverse twitch (0.3–0.5 s) |
| `fakeout` | 🎭 Fake brake | down to 0 % (minimum speed), then straight back up |
| `reverse` | ⏪ Rewind kick | `strength` −35 for `dur_s` 0.8 |
| `sprint` | 🚀 Sprint | to `strength` 95 for `dur_s` 2 |
| `creep_sprint` | 🐌 Creep + sprint | 0 % for 4 s, then sprint |
| `stall` | ⏸ Air pocket | motor off briefly |

Frequency in the UI: **rarely / sometimes / often** (0.5 / 1.5 / 3 per minute), more precise under "More options".

### 2.5 Jokers

```json
"jokers": {
  "account": "separate",          // "separate": one account per kind · "shared": one account for all kinds
  "shared_count": 3,              // only with "shared"
  "lock_s": 5,                    // shared lock: after every joker (no matter whose) x s quiet for everyone
  "items": [
    { "kind": "boost",  "who": "alive", "count": 2, "strength": 25, "dur_s": 2.0,
      "cooldown_s": 10, "hold_ms": 400, "from_s": 5 },
    { "kind": "rewind", "who": "alive", "count": 1, "strength": 35, "dur_s": 0.8,
      "cooldown_s": 20, "hold_ms": 400, "max": null }
  ]
}
```

| `kind` | UI | `strength` means | Default |
|---|---|---|---|
| `boost` | ⏩ Forward boost | + percentage points | +25 for 2 s |
| `rewind` | ⏪ Rewind kick | reverse speed | −35 for 0.8 s (≤ 1.5 s) |
| `brake` | 🛑 Brake | − percentage points, never below 0 % | −40 for 1.5 s |
| `fakeout` | 🎭 Fake brake | sprint afterwards (+ points) | 0.6 s brake, then +20 for 1 s |

- `who`: `all` (everyone), `alive` (active only), `out` (eliminated only = ghosts 👻).
- `cooldown_s` applies **per player**. With `separate` per kind, with `shared` for the whole player
  (rule: *the cooldown follows the account*).
- `max` (only with `shared`): at most this many of this kind from the shared account, e.g. "3 jokers, of which
  at most 1× ⏪".
- If the game master plays along ("control + play"), he gets the same jokers as everyone.

**Limit: at most 2 joker kinds per player state, at most 3 per mode.** So a player never sees
more than two buttons at the same time (active e.g. ⏩ + ⏪, ghosts e.g. 👻 Gust). Reasoning: the phone lies on the
table, one hand is on the paddle, the eyes are on Louie. You hit two screen halves blind and learn them in
one round. Three targets need a glance at the phone, and exactly then you lose a chicken. More kinds would
also make the cooldown rings and dots too small.

### 2.6 Round end

```json
"end": { "time_s": 120, "last_player": true, "plan_end": false }
```

The lever always ends the round and is therefore not in the JSON. Whatever happens first applies. `last_player` and ghost jokers
(`who: "out"`) only take effect when the setting "📊 Statistics & elimination" is on (default off). Otherwise they
are silently dropped, and the mode card points this out unobtrusively.

### 2.7 Advantage per player (handicap)

**Worth it, but keep it small (V1.1).** The advantage does not belong in the mode but to the round: in the
players row the game master taps a player → **Advantage: normal / +1 joker / +2 jokers** (with separate accounts +1 per
kind, with a shared account +1 in the account). It applies for the evening and belongs to the player. Only positive advantages
("Bonus for Lena") instead of penalties for adults; that feels better at the family table. A mode can
switch this off with `"handicap": false` (e.g. for tournament modes). Meanness still applies equally to everyone.

### 2.8 Limits and validation

Per mode at most 8 segments, 6 spice events, 3 joker kinds, 2 KB, and 30 custom modes. The editor checks
**while typing** with the same game logic as the firmware (Rust core crate as WebAssembly in the browser;
fallback: `POST /api/modes/preview` on the device) and reports in a friendly way:

| Situation | Hint (yellow = will be adjusted, red = cannot be saved) |
|---|---|
| Reverse share over the limit | 🟡 "Reverse share 18 % – limited to 10 %. [Kickback instead of negative start]" |
| Reverse too long at a time | 🟡 "2.0 s reverse at a time – 1.5 s allowed, Louie stops after that." |
| Boost over the limit | 🟡 "⏩ only partly works from 75 % (above 100 % Louie flies too high)." |
| Profile speed cap | 🟡 "Family profile allows at most 80 % – peaks are cut." |
| Jokers for ghosts, but no elimination | 🟢 "Players report with 'I'm out'. Switched on automatically." |
| Third joker kind for active players | 🔴 "At most 2 joker buttons at the same time. Tip: shared account." |
| Plan never ends and no end | 🟢 "Round only ends with the lever – intended?" |
| Segment without duration in the middle of the plan | 🔴 "'Random' runs forever, the segments after it never come. Set a duration?" |

Yellow hints do not block; they explain the clamped curve. Where possible, each hint has a
one-tap suggestion in square brackets.

## 3. Gamepad with several jokers

The hold button from the PoC stays the basic element: holding (400 ms, fill ring) triggers, sliding off
cancels. Dots show what is left, a grey ring the cooldown, a lock icon the shared lock.

**1 joker:** one large button, as in the PoC.

**2 jokers, recommendation: side by side, ⏪ left, ⏩ right.** Each half is a full hold button
(approx. 170 × 380 px) with its own dots and its own cooldown ring.

```
┌───────────────────────────────────────┐
│ 🔵 Lena          ✈️ 62 %      ☰       │
├───────────────────┬───────────────────┤
│                   │                   │
│                   │                   │
│        ⏪         │        ⏩         │
│      REWIND       │      BOOST        │
│                   │                   │
│      ●○           │      ●●○          │
│   (ring 12 s)     │                   │
│                   │                   │
├───────────────────┴───────────────────┤
│  🔒 Lock 3 s              I'm out ⏻  │
└───────────────────────────────────────┘
```

Reasoning:
- **Direction like on a remote control**: every child knows ⏪ left, ⏩ right from video. The phone edge serves as a
  tactile anchor; blind, you hit "left half / right half" more reliably than "top / bottom", because the phone lying
  flat is at an angle from the table edge and the top half is further away.
- Two colors (⏪ red, ⏩ green) and different vibration patterns (1× or 2× short, where the phone supports it).
- Holding both at the same time triggers nothing.
- Rejected: **one button plus a toggle**. You have to look which state applies, need two actions,
  and children trigger the wrong one. Stacked vertically also works but is the weaker choice (see above).

**Shared account** (e.g. "3 jokers, freely as ⏩ or ⏪"): same layout, but the dots appear **once
in the middle** between the buttons, and the cooldown greys out both halves. So you see immediately that it is one pot.

```
├───────────────────┬───────────────────┤
│        ⏪         │        ⏩         │
│                 ●●●○                  │
│      REWIND       │      BOOST        │
├───────────────────┴───────────────────┤
```

Both can be chosen per mode (`account`). Separate is strategically clearer ("I still have one ⏪"), shared
gives more freedom. Template: separate.

**3 jokers:** not allowed at the same time (2.5). Three kinds only exist spread across states, e.g. ⏩ + ⏪ for
active players and 👻 for ghosts. After "I'm out" the gamepad switches to the ghost layout (1 or 2 buttons,
violet, 👻 in the header). Later extension if needed: main button at the top across the full width plus two halves below.

**Controller phone with "play":** same gamepad, at the top a narrow game master bar (⏸ pause, ⏹ stop, ☰).

## 4. Editor UI

### 4.1 Ways in

`Modes` → **"+ Custom mode"** (gallery) or on a mode card **"Copy & edit"**. Built-in modes
stay read-only; you always edit a copy (draft, kept automatically in the browser).

### 4.2 Stage a: template gallery (E1)

```
┌───────────────────────────────────────┐
│ ←  New mode                           │
│ What do we start with?                │
│ ┌────────────┐ ┌────────────┐         │
│ │ ✈️ ▬▬▬▬     │ │ 🔥 ⟋        │         │
│ │ Classic    │ │ Pressure   │         │
│ │            │ │ Cooker     │         │
│ └────────────┘ └────────────┘         │
│ ┌────────────┐ ┌────────────┐         │
│ │ 🪚 ⩘⩘⩘     │ │ 🌊 ∿∿       │         │
│ │ Sawtooth   │ │ Wave       │         │
│ └────────────┘ └────────────┘         │
│ ┌────────────┐ ┌────────────┐         │
│ │ ⏪ ▬ 📱     │ │ 👻 ⟋ 📱     │         │
│ │ Rewind     │ │ Ghost      │         │
│ │ Duel       │ │ Hour       │         │
│ └────────────┘ └────────────┘         │
│ ┌────────────────────────────┐        │
│ │ ➕ Start empty              │        │
│ └────────────────────────────┘        │
└───────────────────────────────────────┘
```

Each tile shows a mini curve and 📱 if it contains jokers. Tapping opens the builder immediately.
Template names: Sawtooth (PoC: „Sägezahn“), Wave (PoC: „Welle“), Ghost Hour (PoC: „Geisterstunde“).

### 4.3 Stage b: builder overview (E2)

```
┌───────────────────────────────────────┐
│ ←  🪚 Sawtooth (copy)          Done   │
├───────────────────────────────────────┤
│ 100┤   /|   /|   /|   /|              │
│    │  / |  / |  / |  / |   ⏩ ⏪ ⚡     │
│  0 ┼─/──|─/──|─/──|─/──|──────────    │
│-50 ┤    ▼    ▼    ▼      0:00 – 2:00  │
│ Meanness  🐣  😊 [😏] 😈  👹          │
├───────────────────────────────────────┤
│ ✈️ Flight plan                      › │
│    Sawtooth 25→85 %, 10 s, 6× · Loop  │
├───────────────────────────────────────┤
│ 🌶️ Spice                            › │
│    ⚡ Jolt sometimes                   │
├───────────────────────────────────────┤
│ 🃏 Jokers                           › │
│    All: ⏩ 2× · ⏪ 1× (separate)       │
├───────────────────────────────────────┤
│ 🏁 End                              › │
│    Lever · after 2:00                 │
├───────────────────────────────────────┤
│  🟡 Reverse share 12 % → 10 %         │
├───────────────────────────────────────┤
│ [ ▶ Dry ]  [ 🔧 Test ]  [  Save  ]    │
└───────────────────────────────────────┘
```

- **The preview at the top stays in place** (approx. 130 px) on all editing pages. It shows the **clamped curve**
  (solid), the target curve only where clamping happens (dashed), reverse in red below the zero line,
  spice as small icons at the top, ▼ for kickbacks. Joker markers come from a bot sample
  ("3 bots, smart"), switch "Show jokers".
- **The meanness switch** below the curve only changes the preview and all displayed values (not the mode).
- Simple plans (one segment) show a **quick slider "Speed"** directly on the flight plan card.
- Hints appear as one line; tapping shows all.

### 4.4 Flight plan editor (E3)

```
┌───────────────────────────────────────┐
│ ←  Flight plan           [Preview ▲]  │
├───────────────────────────────────────┤
│ ┌───────────────────────────────────┐ │
│ │ 1 ⟋ Start-up  0→40 % in 4 s  ⋯    │ │
│ └───────────────────────────────────┘ │
│ ┌───────────────────────────────────┐ │
│ │ 2 ⩘ Sawtooth  25→85 %  ⩘⩘⩘  ⋯     │ │
│ │   10 s, hard, 6×   (1:00)         │ │
│ └───────────────────────────────────┘ │
│        [ ➕ Add segment ]              │
│                                       │
│ After:  ( Restart ) ( Hold ) ( End )  │
└───────────────────────────────────────┘
```

- Each segment card has number, symbol, short description, mini curve and duration. Tap → edit segment.
- **⋯ menu**: ↑ Move up · ↓ Move down · Copy · Delete (with "Undo" toast at the top). No dragging, no
  swipe gestures (see web UI concept 3).
- **Add** opens a page with 7 large tiles (▬ Constant, ⟋ Ramp, ▁▃▅ Steps, ⩘ Sawtooth, ∿ Wave,
  🎲 Random, ⏸ Pause). The new segment goes to the end and starts at the end speed of the previous one.

**Edit segment: sawtooth (E3b)**

```
┌───────────────────────────────────────┐
│ ←  ⩘ Sawtooth                Segment 2│
├───────────────────────────────────────┤
│ [ Preview, segment highlighted ]      │
├───────────────────────────────────────┤
│ From        ◄───●───────────►   25 %  │
│ To          ◄─────────●─────►   85 %  │
│ Rise        [ − ]   10 s   [ + ]      │
│ Drop        ( Hard )  ( Soft )        │
│ Repeat      [ − ]    6×    [ + ]  [∞] │
├───────────────────────────────────────┤
│ ▸ More options                        │
│   Direction   ( rising ) ( falling )  │
│   Kickback       [ on ]  −30 % 0.6 s  │
│   Soft over   1.5 s                   │
│   Rise shape  ( straight ) ( late )   │
│   🎚 Different per meanness           │
└───────────────────────────────────────┘
```

Speed slider: middle = 0 %, left in red = backwards (down to the owner limit), label "Minimum speed" at 0 and
"Limit" at 100. Numbers can also be typed directly by tapping the value. Steppers instead of sliders for times and
counts (more precise with the thumb).

### 4.5 Spice, jokers, end (E4–E6)

**Spice:** list of events as in the flight plan. Per event: **frequency** (rarely / sometimes / often),
**from minute**, for kicks **strength**. More options: duration, warning on the phones, exact rate per minute.

**Jokers (E5):**

```
┌───────────────────────────────────────┐
│ ←  Jokers                             │
├───────────────────────────────────────┤
│ 🙂 ALL PLAYERS                        │
│ ┌──────────────┐ ┌──────────────┐     │
│ │ ⏩ Boost   ⋯ │ │ ⏪ Rewind  ⋯ │     │
│ │ [−]  2×  [+] │ │ [−]  1×  [+] │     │
│ └──────────────┘ └──────────────┘     │
│ Account ( per kind ) ( shared )       │
├───────────────────────────────────────┤
│ 👻 ELIMINATED (ghosts)                │
│        [ ➕ Ghost joker ]              │
├───────────────────────────────────────┤
│ ▸ More options                        │
│   Shared lock            5 s          │
│   Advantage per player allowed [on]   │
│   🎚 Count per meanness               │
└───────────────────────────────────────┘
```

- The upper group is called "All players" (`who: "all"`). As soon as there are ghost jokers, the editor asks
  once: "Should eliminated players keep their ⏩/⏪?" No → the group is called "Active" (`who: "alive"`).
- Adding shows only the allowed kinds (⏩ ⏪ 🛑 🎭). If a state is full (2 kinds), the button is grey
  with an explanation.
- Tap a joker tile (⋯) → **joker page**: strength (weak / medium / strong), count. More options:
  duration, cooldown, hold (ms), only from second, "who may" (everyone / active / ghosts).
- With "shared", the two steppers become one stepper **"Jokers per player"** plus an optional "at most" per kind.

**Count per meanness** (opens the row of 5, pre-filled with the automatic values):

```
│ Count ⏩     🐣  😊  😏  😈  👹        │
│             [3] [3] [2] [2] [1]       │
│ Count ⏪     [0] [1] [1] [1] [1]       │
│             ↺ automatic               │
```

As soon as a field differs, the mode stores a list (2.2). "↺ automatic" turns it back into a number.

**End (E6):** "Lever off" (always, greyed out), **time limit** (off / 1 / 2 / 3 / 5 min / custom),
**When only one is left** (switch, hint: "Players report with 'I'm out'"),
**When the flight plan is over** (only selectable with "After: End").

### 4.6 Trying it out

| Button | What | Who |
|---|---|---|
| **▶ Dry run** | Motor stays off. Curve runs live at 1× / 4× / 16×, random seed fixed or 🎲. 2–4 bots with strategy (immediately / smart / saves / never), buttons "Bot 2 is out", "Bot 3: ⏪ now". Afterwards metrics: avg. speed, reverse share, joker uses/min, rejected because of lock, time at the 100 % limit | anyone with editor permission |
| **🔧 Real test drive** | Workshop rules: lever on starts no round, **dead-man button** (motor only while held), 1× or 0.5×. Game master: at most 10 s, start from second x selectable (e.g. "from the 1st drop"). Owner: up to 60 s and jokers by hand ("⏪ now") | game master 10 s, owner full |

### 4.7 Saving (E7)

Name (suggestion from the template), **icon** (grid with 24 emojis), **one sentence** of description (max. 80 characters,
appears on the mode card), **default meanness**. Below two buttons: **"Play this round only"**
(draft, without save permission) and **"Save"**. Saved modes appear in `Modes` with the tag "custom".

### 4.8 Stage c: pro

Under `Done ▾ → Pro`: **meanness table** for all numbers of the mode on one page (rows = fields,
columns = 🐣…👹, automatic values grey, own values black), **Show JSON** (formatted, "Copy"),
**export** as a file and as QR link `http://louie.local/#m=<base64url>`, **import** (paste or file), always with
preview and hints where clamping happens.

## 5. Walkthrough: "Sawtooth with ⏩/⏪ jokers"

Goal: every 10 s Louie rises from 25 to 85 % and drops back with a small reverse twitch. Each player
has 2× boost and 1× rewind. The round ends after 2 min.

| # | Screen | Tap | Result |
|---|---|---|---|
| 1 | Modes | "+ Custom mode" | gallery E1 |
| 2 | E1 | 🪚 Sawtooth | overview E2 with start-up + sawtooth 30→80 %, 12 s, 6×, loop, no jokers |
| 3 | E2 | flight plan card | E3 |
| 4 | E3 | card 2 (sawtooth) | E3b |
| 5 | E3b | From to 25, To to 85, Rise to 10 s | curve at the top updates immediately |
| 6 | E3b | More options → kickback on (−30 %, 0.6 s) | ▼ markers in the curve, line "Reverse share 5 %" green |
| 7 | E3b | (attempt) From to −20 % | 🟡 "Reverse share 20 % – limited to 10 %. 2.0 s at a time – 1.5 s allowed. [From 25 % + kickback]" → tap suggestion, back to 25 % |
| 8 | E3b → E2 | ← | flight plan card: "Sawtooth 25→85 %, 10 s, 6× · Loop" |
| 9 | E2 | jokers card | E5, empty |
| 10 | E5 | All players: ➕ → ⏩ Boost | tile ⏩ 2× (default) |
| 11 | E5 | All players: ➕ → ⏪ Rewind | tile ⏪ 1× (default), account "per kind" stays |
| 12 | E5 | More options → shared lock 5 s | – |
| 13 | E5 | 🎚 Count per meanness → ⏩ at 🐣 to 3 | 🟡 at preview meanness 🐣: "⏪ becomes 🛑 brake at level 1" |
| 14 | E2 | end card → time limit 2 min | card "Lever · after 2:00" |
| 15 | E2 | 🟡 "⏩ only partly works from 75 %" – noted | stays yellow, no obstacle |
| 16 | E2 | ▶ Dry, 4×, 3 bots "smart" | joker markers in the curve, metrics: reverse share 7 %, 0 rejected |
| 17 | E2 | 🔧 Test (lever on, hold button, from 0:08) | 10 s real: can you feel the twitch? |
| 18 | E7 | Save: "Sawtooth Duel", 🪚, "Ever faster, then a twitch. ⏩ and ⏪ for everyone." | mode in the list, selectable immediately |

Players' gamepad: layout "2 jokers side by side" (section 3), ⏪ with ● , ⏩ with ●●.

```json
{
  "schema": 2, "id": "saegezahn-duell", "name": "Sawtooth Duel", "icon": "🪚",
  "desc": "Ever faster, then a twitch. ⏩ and ⏪ for everyone.",
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

No joker needs "Statistics & elimination" (`who: "all"`), so "I'm out" does not appear.

## 6. Two more examples

### 6.1 Simple: "Classic, but slower" (3 taps)

1. `Modes` → Classic → **"Copy & edit"** (opens E2).
2. Drag the quick slider on the flight plan card from 55 to **40 %** (the curve at the top follows).
3. **Save** (suggested name: "Classic (copy)", editable, icon stays ✈️).

```json
{ "schema": 2, "id": "klassisch-langsam", "name": "Classic Relaxed", "icon": "✈️",
  "desc": "Like Classic, only more relaxed.", "based_on": "klassisch@1", "fies_default": 3,
  "flight": { "segments": [ { "type": "ramp", "from": 0, "to": 40, "over_s": 4 },
                            { "type": "const", "v": 40, "for_s": null } ], "after": "hold" },
  "spice": [], "jokers": { "items": [] }, "end": {} }
```

### 6.2 Complex: "Thunderstorm" ⛈️ (example name „Gewitter“)

Idea: Louie rocks in waves, and now and then there is "lightning" (fake brake without warning). Whoever is out becomes a
storm cloud 👻 and may push with 💨 Gust or kick back with ⚡ Lightning. Ends after 2 min or when only
one is left.

| Card | Settings (taps) |
|---|---|
| Template | 🌊 Wave |
| Flight plan | wave 35→75 %, period 20 s, ∞; start-up 4 s in front (from the template) |
| Spice | ➕ 🎭 fake brake "sometimes", from 0:15, More: warning 0 s · ➕ ⚡ jolt "rarely" |
| Jokers | Active: none · Ghosts: ➕ 💨 Gust (⏩, 3×, strong) · ➕ ⚡ Lightning (⏪, 1×) · account per kind |
| End | 2 min · "When only one is left" on → 🟢 "Players report with 'I'm out'" |
| Save | "Thunderstorm", ⛈️, "Whoever is out becomes a storm cloud." |

Active players only see status and at the bottom "I'm out ⏻" (hold). After that the gamepad switches to the
violet ghost layout with 💨 on the right and ⚡ on the left.

```json
{
  "schema": 2, "id": "gewitter", "name": "Thunderstorm", "icon": "⛈️",
  "desc": "Whoever is out becomes a storm cloud.", "based_on": "welle@1", "fies_default": 3,
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
      { "kind": "boost",  "who": "out", "label": "Gust",  "icon": "💨", "count": 3,
        "strength": 30, "dur_s": 2.0, "cooldown_s": 8, "hold_ms": 300 },
      { "kind": "rewind", "who": "out", "label": "Lightning", "icon": "⚡", "count": 1,
        "strength": 35, "dur_s": 0.8, "cooldown_s": 20, "hold_ms": 400 }
    ]
  },
  "end": { "time_s": 120, "last_player": true, "plan_end": false },
  "seed": null
}
```

`label`/`icon` are optional display names; `kind` determines the effect.

## 7. Who may use the builder

Owner setting **"Create modes"** (under 🔒 Permissions):

| Level | Game master | Owner |
|---|---|---|
| **off** | only quick pick and "this round only" sliders | everything |
| **Drafts** (default in the Kids profile) | open builder, dry run, "play this round only", no saving | everything |
| **Save** (default Family/Party) | additionally save, delete own modes, export | everything, including import, locking, deleting others' modes |

- Editing is possible at any time (also during a round; it changes nothing in the running game). **Playing** a
  draft only in READY/END with lever off, like any mode change.
- Player and spectator phones do not see the builder.
- Everything goes through the clamp chain (mode → meanness → this round → speed cap → owner limits →
  motor layer). A mode can never do more than the owner allows. The builder therefore needs no password.
- Kids profile: custom modes only appear in the quick pick if the owner releases them.

## 8. V1 and later

| Stage | Content |
|---|---|
| **V1** | Schema 2 complete in the core crate (incl. `saw`, reverse speed, joker accounts, 5-value lists, meanness rules), template gallery, builder overview with preview and meanness switch, flight plan editor with all 7 segments, spice, jokers (max. 2 per state, separate/shared), end, validation with hints, dry run (1×/4×, bots), test drive 10 s, saving with name/icon/sentence, permission "Create modes", copy/paste JSON |
| **V1.1** | Pro table for all fields, advantage per player, QR sharing, real workshop with jokers by hand, extended bot strategies |
| **Later** | Repeat segment groups ("segments 2–3 three times"), draw curve, if-then rules, 3 jokers at the same time, live conductor |

This moves the editor forward compared with [web-ui-concept.md](web-ui-concept.md) 6.3 (V1.1 there): the
project owner expects it, and because the data model and core crate already handle all layers, the
V1 version is mainly UI work.

## 9. Open items

- [ ] Does a 0.6 s kickback at −30 % feel intentional or like a fault? (test drive)
- [ ] Test ⏪ left / ⏩ right with children (against stacked).
- [ ] Is "count stays the same across meanness" right, or do families want fewer jokers at 👹?
- [ ] Vibration patterns do not work on iPhones in the browser; is the fill ring enough there?
