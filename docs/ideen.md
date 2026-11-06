# Idea collection and panel

Status: 2026-11-06 · collection, nothing is decided. Extends [software-konzept.md](software-konzept.md).

## 1. Approach

1. **Five idea teams** (AI agents) collected independently: game modes & game mechanics,
   party/multiplayer/drinking game, user experience & design, owner and admin settings,
   hardware/safety/robustness. Result: **254 ideas** (catalog in section 5).
2. A **panel of four user types** rated every idea (0 = don't care to 3 = must have) and
   stated whether it belongs in V1:

   | Persona | Short profile |
   |---|---|
   | Family parent | 2 children (6 and 9), not technical, wants simple, fair, safe |
   | Party host | shared-flat parties with 6–10 people, drinking games, chaos, spectators |
   | Maker/owner | builds the kit and gives it away, wants robustness and configurability |
   | Casual player | guest with someone else's iPhone, 20 seconds of patience, no sign-up |

3. The V1 selection below merges duplicates (e.g. four variants of the rewind) and is a
   **proposal** based on the votes. We make the final decision.

Catalog legend: effort small/medium/large · HW = feasible with the planned hardware (yes / limited / no) ·
★ = sum of ratings (max. 12) · V1 = votes for V1 (max. 4).

## 2. What the panel says

- **Family**: "Flip the lever and it runs." Safety (finger in the arm → stop) and a kids profile
  with one tap. Two or three modes are enough. Rewind yes, but with allowance, lock time and warning.
  Saboteurs, bets, secret missions cause arguments. Drinking game not in V1. Children must understand screens
  without reading.
- **Party**: everything is decided in the first 30 seconds: scan QR, tap chicken, big button.
  Rewind with warning is the heart. Eliminated players and spectators need something to do.
  Gloating lives on everyone seeing **who** rewound. Wish for soon after: big screen on the TV.
- **Maker**: a freshly inserted board must not break anything: safe defaults,
  block detection, direction change through zero, turbo time budget, undervoltage, update with rollback.
  Rejects everything that pretends to know more from the motor current than the hardware has (counting hits,
  speed, chip detection). Wants diagnostics export and a quick guide for gift recipients.
- **Guest**: the biggest risk is the captive portal on the iPhone. Rescue page, honest connection indicator,
  reconnect with seat guarantee matter more than any game mode. One big button, no
  allowance arithmetic. iOS has no vibration and no Wake Lock without HTTPS → visible feedback needed.

**Agreed by all four**: rewind, QR lobby with chicken colors, Classic and Pressure Cooker,
connection indicator, gamepad view, countdown, block detection, emergency stop.

**Rejected by all**: mode editors with timeline or if-then rules (V1), reaction duels in a
0.3 s window (Wi-Fi latency makes them unfair), auctions, current "sensing" for hits or position.

## 3. Proposal for V1

### Game

| Feature | Merged from | Note |
|---|---|---|
| **Classic plus** | modi-1 | also the default when playing without a phone |
| **Pressure Cooker** (slow increase) | modi-2 | rounds end by themselves |
| **Dice Engine** (random) | modi-6 | |
| **Meanness slider** from "Kids' Party" to "Final Boss" | modi-45 | scales all mode parameters within the admin limits; replaces the mode editor in V1 |
| **Mini jolt** instead of long reverse travel | modi-10 | check perceptibility on the prototype (ramp) |
| **Rewind** with allowance per player, global lock for everyone, hold to trigger, warning 0.5 s, display "who rewound" | party-1, modi-11, modi-12, technik-29, ux-9, ux-22 | core of the multiplayer fun |
| **Ghost boost**: eliminated players get boost buttons | party-6, modi-28 | everyone has something to do until the end |
| **"I'm out"** by self-report with confirmation | party-24, ux-13 | the electronics cannot see the chips |

### Operation

| Feature | Merged from |
|---|---|
| **QR lobby with chicken colors**: tap a chicken instead of picking a seat, name dice instead of typing | party-47, ux-4, ux-1, ux-2, ux-5 |
| **Three-second onboarding** for guests, no sign-up | ux-6 |
| **Gamepad view**: one big button, landscape possible | ux-7 |
| **Countdown ritual** 3-2-1 in sync on all phones | ux-34 |
| **Connection traffic light** with honest wording, **reconnect with seat guarantee** | ux-28, ux-40 |
| **Captive portal rescue page** with instructions per operating system | ux-3 |
| **Lever mirror**: real lever live in the UI, shows misuse | ux-30 |

### Owner / admin

| Feature | Merged from |
|---|---|
| **Profile quick pick** Kids / Family / Party (one tap sets speed, reverse, rewind, allowed modes) | party-39, besitzer-1, technik-33, ux-25 |
| **Speed cap** as a large slider | besitzer-3 |
| **Limits for party features** (allowances, lock times) | party-49 |

### Technology and safety

| Feature | Merged from |
|---|---|
| **Block detection** via motor current with immediate stop, masked during start-up | technik-1, technik-2 |
| **Emergency stop** for the game master in the UI | technik-32 |
| **Safe defaults** as long as no model is selected | technik-48 |
| **Direction change only through zero** with dead time | technik-3 |
| **Multi-stage watchdog** (motor task, firmware, hardware) | technik-16 |
| **Undervoltage in three stages** (warning, end round, sleep) | technik-11 |
| **Turbo time budget** above nominal voltage | technik-5 |
| **Rate limit** per session, prevent **seat theft** | technik-28, technik-30 |

First clickable draft of this selection (outdated, see [web-ui-konzept.md](web-ui-konzept.md) and [web/poc](../web/poc/index.html)): [web/prototype/index.html](../web/prototype/index.html) (open in the browser;
lever, players, connection and battery are controlled via the "Simulation" bar).

## 4. Candidates for V1.1 and later

- **Spectator big screen** on TV/tablet (ux-15), spectator role with cheer/boo (party-15, party-18)
- **Sabotage statistics and titles** at round end, highlight ticker (party-30, party-48)
- **Update with rollback**, configuration with checksum, **diagnostics export** (technik-46, technik-47, technik-22)
- **Drinking game mode** with a simple rule list, alcohol-free by default, unlocked by admin (party-33, party-34, besitzer-27)
- Fake-out brake, Time Race, visible reverse budget (modi-16, modi-20, modi-14/ux-48)
- Chaos button for the game master (party-43)
- Mode editor (after V1 at the earliest, once it is clear what the meanness slider and profiles do not cover)

## 5. Catalog of all ideas

Within each topic sorted by the panel's rating.

### 5.1 Game modes & game mechanics (53)

- **Classic plus** — Constant speed as in the original, only adjustable and with a gentle start ramp. Intended as the reference mode and fallback when nobody wants to pick up a phone. *Note: This is practically the lever-without-phone default from the concept.*
  <br>`modi-1` · Speed profile · effort small · HW yes · ★ 11 · V1 4/4
- **Slow increase (Pressure Cooker)** — The round starts relaxed and gets a bit faster every few seconds until the turbo limit is reached. This creates a natural arc of tension, and rounds end by themselves without dragging on forever. *Note: The building block ramp_up is already planned; the curve (linear, exponential, staircase) could be selectable.*
  <br>`modi-2` · Speed profile · effort small · HW yes · ★ 11 · V1 4/4
- **Rewind with joker allowance** — Each player has e.g. 2 rewind jokers per round (0.5-1 s reverse) with cooldown, triggered by a big button on the phone. All phones show who rewound, so revenge and deals emerge. *Note: Core idea from the brief; the global reverse limits (minimum interval, share) must still apply.*
  <br>`modi-11` · Reverse in moderation · effort medium · HW yes · ★ 10 · V1 3/4
- **Meanness slider (one slider for everything)** — A single slider from "Kids' Party" to "Final Boss" scales all mode parameters together: speed, randomness, fake-outs, reverse share within the admin limits. It is a quick setting for everyone who does not want to tinker.
  <br>`modi-45` · Balancing · effort small · HW yes · ★ 10 · V1 3/4
- **Eliminated players as troublemakers (ghost mode)** — Whoever is out is not idle: eliminated players get boosts, fake-out brakes or rewinds to annoy the remaining players. So everyone has something to do until the round ends. *Note: Extends "Last Chicken Standing" from the concept with more action types.*
  <br>`modi-28` · Handicap & balancing · effort small · HW yes · ★ 10 · V1 2/4
- **Fake-out brake** — Louie suddenly brakes hard as if he were stopping, and then accelerates again. Paddle players who have already wound up for a hit swing into thin air. *Note: The active brake of the H-bridge makes this noticeably abrupt; the ramp must not be too soft when braking.*
  <br>`modi-16` · Pauses & fake-outs · effort small · HW yes · ★ 9 · V1 1/4
- **Reverse twitch (mini jolt)** — Instead of real reverse phases there are only very short direction jolts of 0.3-0.5 s that disturb the flight path without leaving players defenseless. Intended as the default spice for all modes that allow reverse. *Note: Because of the ramp against brownout, the direction reversal is more sluggish; whether 0.3 s is perceptible must be shown by the prototype.*
  <br>`modi-10` · Reverse in moderation · effort small · HW limited · ★ 8 · V1 3/4
- **Rewind barrage (global cooldown)** — After each rewind, rewinding is locked for everyone for a few seconds, shown as a red ring on all phones. This creates a race: whoever presses first gets the joker, and everyone else waits. *Note: Prevents spam by several players in a row.*
  <br>`modi-12` · Reverse in moderation · effort small · HW yes · ★ 8 · V1 3/4
- **Reverse budget of the round** — The round has a shared reverse budget (e.g. 5 s in total), visible as a bar on all phones. All rewinds and random reverse kicks draw from it, and when it is empty there is only forward. *Note: Makes the admin limit "max. share of round time" visible to players.*
  <br>`modi-14` · Reverse in moderation · effort small · HW yes · ★ 8 · V1 1/4
- **Time Race (survival timer)** — The round lasts a fixed time (e.g. 90 s). The winner is whoever has the most chips left at the end, counted by hand and entered in the phone. Rounds become plannable, ideal for parties with changing players. *Note: The electronics do not count chips; input by phone or by the game master.*
  <br>`modi-20` · Round format · effort small · HW yes · ★ 8 · V1 1/4
- **Creep before the sprint** — Louie becomes almost imperceptibly slow for a few seconds (crawl), everyone relaxes, and then a sprint to the turbo limit follows. The calm before the storm is the actual game element. *Note: Observe the minimum voltage, otherwise the motor stalls; taken from the model profile.*
  <br>`modi-19` · Pauses & fake-outs · effort small · HW yes · ★ 8 · V1 0/4
- **Pure randomness (Dice Engine)** — At random intervals a new random speed within min/max is chosen. This is the simplest chaos mode, and you cannot learn a rhythm in it. *Note: Corresponds to speed.type=random from the concept.*
  <br>`modi-6` · Randomness · effort small · HW yes · ★ 7 · V1 3/4
- **Announced staircase** — The speed jumps up in steps, each step announced on all phones with a countdown ("Level 4 in 3...2...1"). The anticipation is part of the game here; the shock becomes an announcement. *Note: Without a phone there is no announcement; as a substitute the status LED could flash (but it is hard to see in the battery compartment).*
  <br>`modi-5` · Speed profile · effort small · HW yes · ★ 7 · V1 0/4
- **Hover pause (stop with countdown)** — Louie stops briefly, a countdown runs on all phones, and then it continues at full speed or in reverse (surprise). The pause builds tension and gives time to recount chips.
  <br>`modi-17` · Pauses & fake-outs · effort small · HW yes · ★ 7 · V1 0/4
- **Game master as conductor** — In live mode the game master controls Louie directly with a slider and effect buttons (fake-out, sprint, jolt), like a DJ. The server still enforces limits and ramps. *Note: Latency (up to approx. 100 ms plus ramp) makes the control soft, but sufficient.*
  <br>`modi-50` · Game mode · effort small · HW yes · ★ 6 · V1 1/4
- **Weighted randomness / moods** — Instead of uniformly distributed randomness, Louie has moods: "sleepy", "nervous" or "angry", each with its own speed distribution. The moods change randomly by themselves, and the current mood is shown on the phones as a face.
  <br>`modi-7` · Randomness · effort medium · HW yes · ★ 6 · V1 0/4
- **Audience joker (spectators vote)** — Guests without a seat can vote by phone: "faster", "slower" or "back". When enough votes come together in a time window, the action is triggered, and the audience becomes part of the game. *Note: The number of clients is limited (target 8-10 on the hotspot); large parties need the home Wi-Fi.*
  <br>`modi-34` · Player interaction · effort medium · HW limited · ★ 6 · V1 0/4
- **Randomness with memory (fair random)** — The randomness remembers how long it has been quiet and then raises the probability of an outlier (and vice versa). So there are no minute-long boring stretches and no constant hectic, although it feels random. *Note: Better as an option for all random building blocks than as a separate mode.*
  <br>`modi-8` · Randomness · effort medium · HW yes · ★ 5 · V1 0/4
- **False-start bluff** — At round start Louie twitches briefly, stops, twitches again, and only the third time does it really start. A small gag at the start of the round, can be switched off for children who find it annoying.
  <br>`modi-18` · Pauses & fake-outs · effort small · HW yes · ★ 5 · V1 0/4
- **Best of 3 / best of 5** — Several rounds in a row, wins are counted on the phones, between rounds there is a short pause with the current standings. Whoever has match point optionally gets a handicap. *Note: Determining the winner needs manual input ("I'm out" or game master).*
  <br>`modi-21` · Round format · effort medium · HW yes · ★ 5 · V1 0/4
- **King of the hill (challenger rounds)** — The winner stays seated, the losers are replaced by waiting players. A winning streak is displayed ("Lisa: 4 in a row") and from a certain length automatically increases the difficulty for the champion.
  <br>`modi-23` · Round format · effort medium · HW yes · ★ 5 · V1 0/4
- **Sudden death** — When only two players are left (marked by the game master), the mode switches to its own end phase: faster, more fake-outs, and everyone has one last rewind. This makes the often drawn-out duel at the end shorter and more dramatic. *Note: Only works if eliminations are reported reliably.*
  <br>`modi-24` · Round format · effort medium · HW yes · ★ 5 · V1 0/4
- **One-chip lightning round** — Everyone plays with only one chip, round max. 30 s and at high speed. The rounds are quick and suit warming up or as a tie-breaker. *Note: More a game rule with a matching mode preset than a firmware feature.*
  <br>`modi-25` · Round format · effort small · HW yes · ★ 5 · V1 0/4
- **Wheel of fortune between rounds** — After each round the loser spins a wheel of fortune on the phone that determines the modifier for the next round ("double jokers", "no reverse", "turbo start"). This adds variety without having to pick modes.
  <br>`modi-36` · Round format · effort medium · HW yes · ★ 5 · V1 0/4
- **Drinking game events** — Optional adult mode: certain motor events become drinking rules that appear on the phones ("Reverse: the trigger drinks", "Fake-out: everyone who flinched", "Sprint: last chip loser"). The rules are editable, and there is an alcohol-free variant with tasks instead of sips. *Note: Only unlockable by admin and with an age notice; never the default.*
  <br>`modi-47` · Drinking game · effort medium · HW yes · ★ 5 · V1 0/4
- **Rotating conductor** — Every 20 s control passes in turn to another player, who then steers Louie live, even against the others. Whoever is currently steering is shown large on all phones. *Note: The conductor plays at the same time; one-handed operation next to the paddle is difficult, possibly only buttons instead of sliders.*
  <br>`modi-51` · Game mode · effort medium · HW yes · ★ 5 · V1 0/4
- **Kids' handicap per seat** — A handicap can be set per seat, e.g. the youngest child gets more jokers, the adults fewer or no rewinds at all. This lets mixed age groups play against each other without someone always losing. *Note: The motor speed is the same for everyone; a real handicap on the playing field is not possible, only for the phone actions.*
  <br>`modi-29` · Handicap & balancing · effort medium · HW limited · ★ 4 · V1 1/4
- **Heartbeat** — The speed pulses rhythmically (fast-slow-fast) like a heartbeat that gets faster and faster during the round. Whoever recognizes the rhythm can exploit it until it tips over. *Note: The ramp limit (max. V/s) dampens very fast pulses; the period should therefore be around 1-3 s.*
  <br>`modi-3` · Speed profile · effort small · HW yes · ★ 4 · V1 0/4
- **Swell** — The speed follows a long, slow sine curve with slight noise. It feels like a sea swell: long calm troughs and then a wave crest where everyone gets hectic.
  <br>`modi-4` · Speed profile · effort small · HW yes · ★ 4 · V1 0/4
- **Catch-up boost (rubberbanding)** — Whoever has already lost chips (entered on the phone) gets more or stronger boosts and rewinds than the leaders. This keeps trailing players involved. *Note: The chip count is self-reported, so abuse is possible (children report themselves poorer).*
  <br>`modi-27` · Handicap & balancing · effort medium · HW yes · ★ 4 · V1 0/4
- **Champion tax** — Whoever won the last round loses jokers in the next round or has to accept one of the others' rewinds without cooldown. A simple automatic balancing rule for streaks.
  <br>`modi-30` · Handicap & balancing · effort small · HW yes · ★ 4 · V1 0/4
- **Saboteur among us** — One of the players is secretly the saboteur and has stronger rewinds that are triggered anonymously. At the end everyone guesses who it was, and whoever guesses right gets points. *Note: Only works with one phone per player; screens must stay hidden.*
  <br>`modi-33` · Player interaction · effort medium · HW yes · ★ 4 · V1 0/4
- **Alliance rewind** — Two players must press together within 2 s to trigger a rewind, which is then stronger or longer. Short-term alliances and betrayal emerge. *Note: Because of Wi-Fi latency, a generous time window makes sense.*
  <br>`modi-35` · Player interaction · effort medium · HW yes · ★ 4 · V1 0/4
- **Louie is hungry (block event)** — If someone deliberately holds Louie's plane (motor current rises sharply), the motor stops immediately for protection, and the phones show "Foul! Who was that?". The game can turn this into a penalty for the next round. *Note: Block detection via current is realistic, but it does not say who blocked. It mainly serves motor protection and should always be active regardless of the game.*
  <br>`modi-37` · Motor current events · effort medium · HW limited · ★ 4 · V1 0/4
- **Mode editor: draw a curve** — You draw a speed curve over time with your finger; it is stored as a list of points and interpolated. Especially intuitive for children ("here he should get really fast"). *Note: The server clamping to ramp and limits smooths strokes that are too steep; the preview should show the clamped curve.*
  <br>`modi-42` · Mode editor · effort medium · HW yes · ★ 4 · V1 0/4
- **Automatic difficulty (learning Louie)** — Louie remembers how long rounds last in this group and adjusts the increase so that rounds hit a target time (e.g. 2 min). If rounds are too long, it gets faster; if they are too short, more relaxed. *Note: The device knows the round duration (start to lever off), more reliably with an end report.*
  <br>`modi-46` · Balancing · effort medium · HW yes · ★ 4 · V1 0/4
- **Drinking game: rewind price** — Every rewind costs the trigger a sip, or he may hand out a sip if he knocks someone out. This creates a trade-off between annoying others and protecting yourself. *Note: Essentially just text and display on the phones.*
  <br>`modi-48` · Drinking game · effort small · HW yes · ★ 4 · V1 0/4
- **Countdown bomb** — A visible timer runs down, and at zero there is a random big effect (sprint, mini jolt series or full brake). Players can extend or shorten the timer with jokers on their phone.
  <br>`modi-53` · Pauses & fake-outs · effort medium · HW yes · ★ 4 · V1 0/4
- **Lever gesture as game action** — Without a phone the lever can be used in the game: briefly off-on within 0.5 s = pause, twice = next mode. This makes part of the features reachable for rounds without a phone. *Note: Risk of confusion with normal stop and with the recovery gestures at start; the lever briefly cuts the motor hard.*
  <br>`modi-39` · Operation without phone · effort medium · HW limited · ★ 3 · V1 0/4
- **Mode editor: event dice** — Instead of a fixed timeline there is a list of events with a probability per second (fake-out 5 %, reverse jolt 3 %, sprint 4 %). The UI also shows an estimated "meanness" and the expected round duration. *Note: Fits closely with the existing JSON schema (chance/duration).*
  <br>`modi-41` · Mode editor · effort medium · HW yes · ★ 3 · V1 0/4
- **Share modes via QR code** — A custom mode is exported as a compact code or QR code that other Louie owners can scan. Without a cloud it can be passed on from party to party. *Note: Without HTTPS there is no camera access in the browser; the QR code must be scanned with the system camera app, e.g. as a link with the mode in the URL fragment.*
  <br>`modi-44` · Mode editor · effort medium · HW yes · ★ 3 · V1 0/4
- **Seed duel (same randomness for everyone)** — A random sequence is fixed via a code (e.g. "CHICK-42") and can be repeated. Groups or tournament rounds can play exactly the same "random" sequence, and particularly mean seeds can be shared. *Note: Because of motor tolerance and battery level it is not bit-identical, but the setpoints are.*
  <br>`modi-9` · Randomness · effort small · HW yes · ★ 2 · V1 0/4
- **Mirror round** — A special round that runs completely in reverse, but much slower so that you can defend yourself. Intended as a rare event mode or as a penalty round, never as the default. *Note: Conflicts with the default limit (max. 10 % share); only possible if the admin explicitly allows it. Whether the mechanism flies equally well in reverse needs checking.*
  <br>`modi-15` · Reverse in moderation · effort small · HW limited · ★ 2 · V1 0/4
- **Point hunt over several rounds** — Instead of "who is left last" there are points: placement per round, bonus for rewinds that knock someone out, penalty for early elimination. The overall ranking runs over the evening. *Note: The electronics cannot see who was knocked out by which rewind; this can only be recorded via an honesty button.*
  <br>`modi-26` · Round format · effort medium · HW limited · ★ 2 · V1 0/4
- **Joker auction** — Before the round, players bid with chips (real ones, from their supply) or points for extra rewinds. Whoever bids a lot starts with fewer chips but has more weapons. *Note: The chips are physical and counted by hand; the UI only manages the bids.*
  <br>`modi-31` · Handicap & balancing · effort medium · HW yes · ★ 2 · V1 0/4
- **Secret missions** — Before the round each player gets a hidden mission on their phone ("Trigger 2 rewinds while seat 3 is still in", "Survive 60 s without a joker"). Completed missions bring bonus points. *Note: Only missions that can be checked via phone actions and time are automatically evaluable; everything else relies on honesty.*
  <br>`modi-32` · Player interaction · effort medium · HW limited · ★ 2 · V1 0/4
- **Counter rewind** — Whoever also presses within 0.3 s at the moment of a rewind cancels it (Louie only twitches), and the trigger loses his joker. This becomes a reaction duel between the phones. *Note: Wi-Fi latency of several phones (50-200 ms, fluctuating) makes the timing unfair; a generous window would be needed.*
  <br>`modi-13` · Reverse in moderation · effort medium · HW limited · ★ 1 · V1 0/4
- **Tournament bracket for large groups** — With more than 4 people the UI creates preliminary rounds with up to 4 players each; the winners go to the final. The bracket is visible live on all phones, and the final gets its own, harder mode. *Note: Depends on profiles/multi-user (stage 3); RAM for tournament data is not critical, the UI is the effort.*
  <br>`modi-22` · Round format · effort large · HW yes · ★ 1 · V1 0/4
- **Party marathon with seasons** — An evening becomes a season: several modes in a fixed or random order, an overall ranking, a mid-season twist (e.g. from round 5 rewinds count double) and an award ceremony at the end. This is the umbrella for tournament, points and handicap ideas. *Note: Needs profiles and persistence across rounds (keep flash write cycles low).*
  <br>`modi-49` · Round format · effort large · HW yes · ★ 1 · V1 0/4
- **Music sync (speed by BPM)** — A phone plays music, and Louie's speed follows a given BPM profile of the playlist (entered by the user or via tap tempo). When the beat drops, a sprint follows. *Note: The device has no speaker or microphone; the phone only supplies speed setpoints. Real audio analysis in the browser is not possible without HTTPS (microphone).*
  <br>`modi-52` · Game mode · effort large · HW limited · ★ 1 · V1 0/4
- **Hit hunch via current spikes** — Experimental: short current spikes when Louie bumps into a paddle or a chip are counted and shown as a "hit counter" or intensity display. The result is not a chip result, but a feeling for action. *Note: Very uncertain: the signals are small and noisy, and the IPROPI current measurement of the DRV8213, RC filter and ADC rate must suffice. Measure on the prototype first.*
  <br>`modi-38` · Motor current events · effort large · HW limited · ★ 0 · V1 0/4
- **Mode editor: building-block timeline** — A mode consists of a sequence of blocks ("10 s constant 50 %", "random 30-80 % for 20 s", "fake-out", "creep", "repeat") that you arrange on the phone by drag-and-drop. A preview curve shows the progression, and a test drive runs on real hardware. *Note: The JSON format would have to be extended from parameters to sequences; the size per mode should stay limited (flash, RAM).*
  <br>`modi-40` · Mode editor · effort large · HW yes · ★ 0 · V1 0/4
- **Mode editor: conditions (if-then)** — Simple rules like "if only 2 players are left, then +20 %" or "after 60 s unlock rewinds for everyone". This lets you build dynamic modes without programming. *Note: The conditions depend on phone reports (elimination); a small custom rule engine costs firmware and test effort.*
  <br>`modi-43` · Mode editor · effort large · HW yes · ★ 0 · V1 0/4

### 5.2 Party, multiplayer & drinking game (49)

- **Rewind button** — Each player has a rewind button on the phone that makes Louie twitch backwards for 0.5–1 s. Allowance per round (e.g. 2) and a visible cooldown ring. All phones briefly show who rewound, so there is gloating and revenge. *Note: Do not add up simultaneous requests; global reverse limits (duration, interval, share) always apply. Ramp needed at direction change.*
  <br>`party-1` · Rewind & sabotage · effort small · HW yes · ★ 11 · V1 4/4
- **Phone QR lobby with seats in chicken colors** — A large QR code on the game master's screen invites new phones, which are directly assigned a free color. If everything is full, you automatically end up as a spectator. *Note: QR generation in the browser with a small JS library.*
  <br>`party-47` · UX & design · effort small · HW yes · ★ 11 · V1 4/4
- **Elimination by self-report** — Whoever loses their last chip taps 'I'm out' on their phone. The phone then switches to the eliminated mode with boosts. Optionally the game master confirms. *Note: Basis for many other ideas, since the hardware does not detect chip losses.*
  <br>`party-24` · Party moderation · effort small · HW yes · ★ 10 · V1 2/4
- **Turbo boost for eliminated players** — Whoever is out gets boost buttons and can briefly speed up Louie to annoy the remaining players. Keeps eliminated players engaged instead of watching bored. *Note: Elimination must be reported manually (player or game master); the electronics cannot see it.*
  <br>`party-6` · Boosts · effort small · HW yes · ★ 9 · V1 3/4
- **Kids and party profile** — A switch in the lobby toggles between 'Kids' (no reverse, no sabotage, no drinking rules) and 'Party' (everything allowed). The admin defines what is visible in each profile.
  <br>`party-39` · Party moderation · effort small · HW yes · ★ 9 · V1 3/4
- **Admin limits for party features** — The admin defines: max. rewinds per player, whether spectators may interfere, drinking game allowed yes/no, max. number of spectators, mandatory breaks. This keeps the game fair and safe even in party chaos. *Note: Extends the existing reverse limits from the concept.*
  <br>`party-49` · Party moderation · effort small · HW yes · ★ 8 · V1 3/4
- **Brake trap** — Instead of reverse, a player can trigger a short full brake (0.5 s, short-circuit brake). Louie stops abruptly, the plane sags and hits unpredictably. Gentler sabotage than reverse. *Note: Braking via H-bridge is available; check the mechanics for jerky stops.*
  <br>`party-5` · Rewind & sabotage · effort small · HW yes · ★ 8 · V1 2/4
- **Chicken avatars and nicknames** — Players choose a name and a chicken emoji/avatar in their color in the lobby. These appear with all events ('Clucking Clara rewinds!').
  <br>`party-29` · UX & design · effort small · HW yes · ★ 8 · V1 1/4
- **Phone vibrates on danger** — When a rewind, boost or event card is triggered, all player phones vibrate briefly. Haptic feedback without having to look at the display. *Note: Vibration API not available on iOS Safari.*
  <br>`party-27` · UX & design · effort small · HW yes · ★ 7 · V1 2/4
- **Slow-motion joker** — Everyone has one joker per game that slows Louie down strongly for 3 s. Good for defending when you are threatened yourself, or for throwing others off their rhythm.
  <br>`party-8` · Boosts · effort small · HW yes · ★ 7 · V1 0/4
- **Spectator role** — Whoever does not play scans the QR code and gets a spectator view: live speed, events, who sabotaged whom, betting slip. Spectators can interfere to a limited degree (e.g. one boost per round). *Note: Many WebSocket clients burden the RAM of the ESP32-C3; limit the number of spectators (e.g. 6–8).*
  <br>`party-15` · Spectators · effort medium · HW yes · ★ 6 · V1 2/4
- **Spectator boo and cheer** — Spectators hammer a cheer or boo button. If the cheer level reaches a threshold, there is a small boost; with a lot of booing, briefly slower. The audience becomes part of the game. *Note: Throttle button spam (server aggregates per second).*
  <br>`party-18` · Spectators · effort small · HW yes · ★ 6 · V1 1/4
- **Sabotage statistics and titles** — After the game the system awards titles: 'Biggest Saboteur', 'Unlucky Bird' (most often a victim), 'Boost Junkie', 'Pacifist' (used nothing). Provides talking points. *Note: Data only in RAM until the end of the session, no saving needed.*
  <br>`party-30` · Party moderation · effort small · HW yes · ★ 6 · V1 1/4
- **Alcohol-free mode as default** — Every drinking rule has a neutral variant: 'Sip of water', 'Push-up', 'Tell a joke', 'Give a compliment'. Adjustable per player, so mixed rounds are possible. *Note: Text snippets, hardly any memory.*
  <br>`party-34` · Drinking game · effort small · HW yes · ★ 6 · V1 1/4
- **Highlight ticker** — A running ticker at the bottom of all phones narrates the round: '12 s: Blue rewinds', '20 s: Combo boost from Red and Yellow'. After the round as a summary to share (screenshot).
  <br>`party-48` · UX & design · effort small · HW yes · ★ 6 · V1 1/4
- **Announced rewind** — The rewind is not triggered immediately; instead all phones show a 3-2-1 countdown with the saboteur's name. This makes reverse less unfair because everyone can prepare, and increases the tension. *Note: Admin variant: secret vs. announced.*
  <br>`party-3` · Rewind & sabotage · effort small · HW yes · ★ 6 · V1 0/4
- **Sudden death** — When two players are left, sudden death starts automatically: rising speed, all eliminated players have one rewind and one boost each. All phones show a dramatic finale design. *Note: Requires elimination reports.*
  <br>`party-40` · Game modes · effort medium · HW yes · ★ 6 · V1 0/4
- **Drinking game mode with rules from the lobby** — A separate mode 'Party (18+)' that shows announcements after round end: 'Whoever is out takes a sip', 'The saboteur hands out 2 sips'. Rules are a selectable list in the UI. *Note: The admin must unlock it; off by default.*
  <br>`party-33` · Drinking game · effort medium · HW yes · ★ 5 · V1 1/4
- **Chaos button for the game master** — The game master has a big red chaos button: triggers a random combination of boost, brake and short reverse. Once per round, with a countdown for everyone.
  <br>`party-43` · Party moderation · effort small · HW yes · ★ 5 · V1 1/4
- **Drawing event cards** — Every 20–40 s an event card appears on all phones: 'Gust' (speed fluctuations), 'Calm' (slow), 'Looping frenzy' (briefly full throttle), 'Tailwind' (mini reverse). The card is animated large before it takes effect. *Note: Reverse cards must stay within the global limits.*
  <br>`party-10` · Event cards · effort medium · HW yes · ★ 5 · V1 0/4
- **Wheel of fortune between rounds** — After each round the loser (or winner) spins a wheel of fortune on the phone that determines the rule of the next round: 'Rewinds only', 'Double speed', 'Left hand', 'Eyes closed for the game master' etc. *Note: Physical rules (left hand) are just announcements, no technology.*
  <br>`party-12` · Event cards · effort medium · HW yes · ★ 5 · V1 0/4
- **Mode choice by vote in the lobby** — Instead of the game master choosing, the system suggests 3 modes and all phones vote for 10 s. On a tie, a random wheel decides.
  <br>`party-14` · Votes · effort small · HW yes · ★ 5 · V1 0/4
- **Team captain with remote control** — Per team one plays at the paddle, the other sits next to them with the phone and uses rewinds/boosts. Roles swap every round. Communication within the team becomes the game.
  <br>`party-20` · Teams · effort small · HW yes · ★ 5 · V1 0/4
- **Round tournament with points table** — Several rounds in a row, points per placement. The lobby shows a table; at the end there is an award ceremony with a confetti animation on all phones. *Note: Placement is entered by a tap from the game master or the players.*
  <br>`party-23` · Party moderation · effort medium · HW yes · ★ 5 · V1 0/4
- **Party host announcements** — One phone (e.g. on a speaker) becomes the host: it speaks or shows announcements like 'Watch out, Red is in danger!', '10 seconds left!', 'Who just rewound?'. Text-to-speech in the browser. *Note: Sound only via phones; the board has no speaker. Web Speech API is not available offline on all devices; alternative: prerecorded sounds (flash is tight).*
  <br>`party-25` · Party moderation · effort medium · HW yes · ★ 5 · V1 0/4
- **Secret saboteur** — At round start a random player secretly gets an extra rewind. After the round everyone votes on who the saboteur was. Guessed right: the saboteur loses a point (or drinks); wrong: everyone else. *Note: Only works if rewinds are triggered anonymously.*
  <br>`party-4` · Rewind & sabotage · effort medium · HW yes · ★ 4 · V1 0/4
- **Boost combo** — If two or more players press boost within 1 s, there is a stronger combo boost with an effect on all phones ('DOUBLE TURBO!'). Rewards deals and spontaneous alliances. *Note: The admin turbo limit stays hard.*
  <br>`party-7` · Boosts · effort small · HW yes · ★ 4 · V1 0/4
- **Live vote on the next phase** — In the middle of the round a 5 s vote pops up: 'Faster or slower?' or 'Reverse kick now: yes/no?'. The majority decides immediately. Spectators vote too. *Note: Players have both hands on the paddles; voting is more for spectators and eliminated players.*
  <br>`party-13` · Votes · effort medium · HW yes · ★ 4 · V1 0/4
- **Spectator bets** — Before the round, spectators place virtual chicken feathers on the player they think will win. At the end, a ranking of the best tipsters. Optional: odds change with the number of bets. *Note: The winner must be entered manually. Only virtual points, no money.*
  <br>`party-16` · Spectators · effort medium · HW yes · ★ 4 · V1 0/4
- **Mandatory breaks and water round** — After X rounds the game pauses automatically, all phones show 'Water break – 2 minutes'. The game master can extend but not skip it (admin setting).
  <br>`party-36` · Drinking game · effort small · HW yes · ★ 4 · V1 0/4
- **Energy bar instead of fixed allowances** — Each player has an energy bar that recharges slowly. Rewind costs a lot, boost medium, slow motion little. Players decide tactically when to use what. *Note: More UI complexity; possibly too abstract for children.*
  <br>`party-9` · Boosts · effort medium · HW yes · ★ 3 · V1 0/4
- **Cards in hand** — At round start each player gets 3 random action cards (boost, brake, rewind, shield, slow motion) and plays them with a swipe gesture. Like a card game in parallel to the board game.
  <br>`party-11` · Event cards · effort medium · HW yes · ★ 3 · V1 0/4
- **Teams 2 vs 2** — Seats are combined into two teams. Rewinds and boosts are team resources shared on the team phone. A team loses when both players are out.
  <br>`party-19` · Teams · effort medium · HW yes · ★ 3 · V1 0/4
- **Status LED as stage light** — The status LED on the board flashes to match the game: countdown flashing before the start, fast flickering on rewinds, steady light on boost. A small visible hint in the game itself. *Note: Only one LED in the battery compartment, hardly visible under the game.*
  <br>`party-28` · UX & design · effort small · HW limited · ★ 3 · V1 0/4
- **Revenge bonus** — Whoever was rewound gets a revenge rewind for 10 s that only counts against the culprit (by announcement). Creates small feuds at the table. *Note: The motor turns for everyone; 'against the culprit' is just narrative, physically it hits everyone equally.*
  <br>`party-31` · Rewind & sabotage · effort small · HW limited · ★ 3 · V1 0/4
- **Lever gesture as table joker** — Whoever plays without a phone can trigger an effect via the original lever: flip twice quickly = pause for everyone (e.g. to refill drinks or sort chips). *Note: The lever disconnects the motor in hardware; gestures must not be confused with start/stop and recovery gestures.*
  <br>`party-32` · Party moderation · effort medium · HW limited · ★ 3 · V1 0/4
- **Rewind costs a sip** — In drinking game mode you may rewind without limit, but each rewind costs the trigger a sip (or an alcohol-free task). The reverse travel limits stay active anyway.
  <br>`party-37` · Drinking game · effort small · HW yes · ★ 3 · V1 0/4
- **Steady hands (current spying)** — If Louie is blocked (e.g. someone holds the plane), the motor current rises. The system detects this and calls out 'Cheater!' on all phones, with a penalty according to the rules. *Note: Only coarse blocking is detectable; the electronics cannot see who did it. Block protection must switch off the motor anyway.*
  <br>`party-44` · Game modes · effort medium · HW limited · ★ 3 · V1 0/4
- **Traitor mode** — A team member secretly becomes a traitor and works against their own team with rewinds. If unmasked, they switch teams.
  <br>`party-21` · Teams · effort medium · HW yes · ★ 2 · V1 0/4
- **Bounty** — A random player is declared 'hunted' (their chicken glows red on all phones). Whoever takes a chip from them gets a bonus rewind. Focuses the sabotage on one person. *Note: Chip loss must be reported manually.*
  <br>`party-22` · Game modes · effort medium · HW limited · ★ 2 · V1 0/4
- **Soundboard per player** — Each player chooses a victory and a curse sound. On rewinds the victim's phone plays a rewind sound. Small sound files from flash. *Note: Flash 4 MB: only a few, heavily compressed sounds. Alternatively synthesized via WebAudio.*
  <br>`party-26` · UX & design · effort medium · HW limited · ★ 2 · V1 0/4
- **Truth or dare on chip loss** — Whoever loses a chip enters it and gets a random 'truth or dare' card. Family and adult card decks selectable. *Note: Limit card texts in flash, possibly uploadable by the admin.*
  <br>`party-38` · Drinking game · effort medium · HW yes · ★ 2 · V1 0/4
- **Superpower auction** — Before the round, superpowers (triple rewind, shield, mega boost) are auctioned. Payment is with points from previous rounds or with sips in the drinking game.
  <br>`party-42` · Game modes · effort medium · HW yes · ★ 2 · V1 0/4
- **Duel mode 1 vs 1 by phone** — Two players each hold a phone, the rest play at the paddles. The phone duelists fight each other with rewinds and boosts; whoever gets their favorite at the table through wins.
  <br>`party-45` · Game modes · effort medium · HW yes · ★ 2 · V1 0/4
- **Rewind lottery** — Instead of players rewinding deliberately, they buy tickets. At a random moment a ticket is drawn and its owner may trigger a rewind. Less reaction game, more luck.
  <br>`party-46` · Rewind & sabotage · effort small · HW yes · ★ 2 · V1 0/4
- **Rewind counter (shield)** — Whoever is currently the victim of a rewind can press a shield button within a short window (approx. 0.3 s) and cancel the kick. One shield per round. Feels like a reaction duel. *Note: Wi-Fi latency on the phone (50–200 ms) makes the window unfair; better implemented as 'rewind is delayed with a short announcement'.*
  <br>`party-2` · Rewind & sabotage · effort medium · HW limited · ★ 1 · V1 0/4
- **Live bets during the round** — Spectators can place mini bets during the round: 'Who loses a chip next?' Whoever is right gets points or may trigger a boost. *Note: Someone must enter chip losses by phone, otherwise no evaluation is possible.*
  <br>`party-17` · Spectators · effort large · HW limited · ★ 1 · V1 0/4
- **Sip counter with upper limit** — The UI counts the sips per player and enforces a break or water round when an adjustable limit per hour is reached. Also shows how long has been played. *Note: Responsible feature; values confirmed manually, not measured.*
  <br>`party-35` · Drinking game · effort medium · HW yes · ★ 1 · V1 0/4
- **Rhythm mode to music** — A phone plays music and passes the beat to the server; Louie changes speed to the beat. On drops there are short boosts. *Note: Beat detection in the browser is complex; latency between phone and motor.*
  <br>`party-41` · Game modes · effort large · HW limited · ★ 1 · V1 0/4

### 5.3 User experience & design (52)

- **Connection traffic light with honest wording** — Top right a small Louie icon: green = connected, yellow flashing = reconnecting, red = gone. Tapping shows plain text ('Your phone has left the Louie Wi-Fi – probably because it has no internet. Tap here to return.') instead of error codes.
  <br>`ux-28` · Error and connection indicators · effort small · HW yes · ★ 11 · V1 4/4
- **Three-second onboarding for guests** — Whoever is only watching lands immediately on a view with a large status and a single button 'Join game'. No menus, no hamburger, no settings visible. Everything else only appears once you have a role (progressive disclosure).
  <br>`ux-6` · Screen layout · effort small · HW yes · ★ 10 · V1 4/4
- **Player view as gamepad** — During the round the phone becomes a one-button controller: at the top a narrow status strip (speed, phase), in the middle a huge boost button with cooldown ring, below it the rewind button with allowance dots. Landscape optional, button always under the thumb. Nothing that can be swiped away by accident. *Note: Without Wake Lock the screen turns off – check a hint 'extend screen timeout' or the trick with a silent video loop.*
  <br>`ux-7` · Player view · effort medium · HW yes · ★ 10 · V1 4/4
- **Countdown ritual before the start** — When the game master releases, all phones count 3-2-1 in sync with a large number zoom and a propeller start-up sound; the motor starts with a gentle ramp exactly on 'Go'. Makes every round an event. *Note: Only applies to 'start after release'; with direct lever start a short substitute jingle.*
  <br>`ux-34` · Animation / sound · effort small · HW yes · ★ 10 · V1 4/4
- **Reconnect with seat guarantee** — If a phone drops out briefly (screen off, Wi-Fi changed), its chicken stays reserved for 60 s and appears semi-transparent with an hourglass on the other phones. On return 'Welcome back, Federico!' and everything is as before. *Note: Builds on the planned session token.*
  <br>`ux-40` · Error and connection indicators · effort small · HW yes · ★ 10 · V1 4/4
- **Lobby QR on the game master's phone** — The game master taps 'Invite friends' and his phone shows the Wi-Fi QR full screen and then the control QR. New players simply scan the phone instead of searching for the sticker under the game. Switches automatically every 4 s between the two codes. *Note: The QR generator must be stored offline in flash as a small JS file (approx. 5–10 KB); the Wi-Fi password becomes visible in the process, admin switch to turn it off.*
  <br>`ux-2` · Onboarding / joining · effort small · HW yes · ★ 10 · V1 2/4
- **Warning before a reverse kick** — 0.5 s before a reverse kick (planned or triggered by a rewind) takes effect, the border turns red on all phones and a 'beep-beep' sounds like a reversing truck. Gives the victims a tiny chance and makes reverse less frustrating. *Note: The delay must be scheduled on the server; Wi-Fi latency can shrink the warning. Optional as an admin switch.*
  <br>`ux-22` · Sound / haptics · effort small · HW yes · ★ 9 · V1 4/4
- **Captive portal rescue page with thumb animation** — The portal page shows only a huge button 'Open in browser' and an animated hand that shows the right way on iOS/Android ('Stay connected without internet'). Detects the operating system from the user agent and shows only the matching instructions. *Note: Portal browser behavior changes with OS versions; check with real devices on the prototype.*
  <br>`ux-3` · Onboarding / joining · effort medium · HW yes · ★ 9 · V1 3/4
- **Pick a chicken instead of a seat** — When joining you see the game board from above as an illustration with four chickens in the original colors. You tap 'your' chicken, it clucks briefly and hops. Chickens already taken carry the owner's nickname or emoji and are greyed out. *Note: Colors differ per model (Louie old/new, Chewie) – store a color palette per model profile.*
  <br>`ux-4` · Onboarding / joining · effort small · HW yes · ★ 9 · V1 2/4
- **Hold to trigger for powerful actions** — Rewind and other strong interventions only trigger after a short hold (approx. 300 ms) with a filling ring. Prevents accidental triggering in the pocket and makes the moment more dramatic. Boost stays a quick tap.
  <br>`ux-9` · Player view / haptics · effort small · HW yes · ★ 8 · V1 4/4
- **One QR for everything (sticker duo as picture story)** — The sticker shows not just two bare QR codes but a small comic strip: 1. Louie waves into the Wi-Fi, 2. Louie points to the control panel. Children understand the order without text, adults simply scan one after the other. Optionally a third mini QR 'Help' that opens a guide page stored in flash. *Note: The help QR only works if you are already in the Louie Wi-Fi; test print quality on a small sticker.*
  <br>`ux-1` · Onboarding / joining · effort small · HW yes · ★ 8 · V1 3/4
- **Self-report 'I'm out' with confirmation** — Players can swipe 'My last chip is gone' themselves; the game master gets a small confirmation toast. Takes work off the game master and also works without a game master (then the self-report applies directly). *Note: Cheating possible – as a party feature more feature than bug.*
  <br>`ux-13` · Player view · effort small · HW yes · ★ 8 · V1 2/4
- **Name dice for nicknames** — Instead of a keyboard there is a dice button that generates funny chicken names (e.g. 'Cluckerella', 'Federico', 'Scrambled Sam'). Children who cannot read or write get into the game without typing, adults can overwrite. In drinking game mode a different word list (e.g. 'Eggnog Eddie'). *Note: Keep word lists small (a few KB).*
  <br>`ux-5` · Onboarding / child-friendliness · effort small · HW yes · ★ 8 · V1 1/4
- **Lever mirror in the UI** — The UI shows the real lever as a large toggle switch graphic that moves live. On misuse (lever is on when waking up) the graphic wobbles and shows the direction in which to flip it. With lever gestures the flips are counted live ('3 of 5 – keep going'). *Note: The lever disconnects the motor in series – whether the electronics reliably detect the lever state with the motor disconnected depends on the circuit (planned according to the concept).*
  <br>`ux-30` · Error and connection indicators / onboarding · effort small · HW yes · ★ 7 · V1 2/4
- **Winner confetti and lap of honor** — When only one chicken is left and the game master confirms it, confetti in the winner's color rains on all phones, the big screen shows the winning chicken with a crown, and Louie flies a slow lap of honor before stopping. *Note: Lap of honor only if the lever is still on.*
  <br>`ux-35` · Animation · effort small · HW yes · ★ 7 · V1 1/4
- **Make the reverse budget visible** — A small shared bar for everyone shows how much of the round's reverse share (e.g. 10 %) has been used. When it is empty, all rewinds are grey with the hint 'Louie has had enough of flying backwards'. Makes the server-side limits understandable instead of frustrating.
  <br>`ux-48` · Player view / error indicators · effort small · HW yes · ★ 7 · V1 1/4
- **Game master cockpit** — At the top the game master sees a live speed curve (last 30 s) with marked reverse kicks and boosts, below four chicken tiles to tap 'eliminated', at the bottom a wide pause and stop bar. Important actions within thumb reach, stop bright red and confirmed by swiping. *Note: Stop in the UI is software; the real emergency stop stays the lever – the UI should show this honestly.*
  <br>`ux-10` · Game master view · effort medium · HW yes · ★ 7 · V1 0/4
- **Only one phone makes noise** — So that six phones do not cluck at the same time, there is a 'speaker' role: by default only the big screen or the game master plays sound; player phones only play their own feedback quietly. Switchable in the lobby menu.
  <br>`ux-20` · Sound / announcements · effort small · HW yes · ★ 7 · V1 0/4
- **Status LED alphabet** — Clearly defined patterns for the single status LED: heartbeat (double short, pause) = ready on Wi-Fi, slow breathing = hotspot active, fast flicker = error, Morse-like 'short-long' = waiting for lever confirmation, three flashes = lever gesture detected, glow = battery low. A mini legend is printed on the QR sticker. *Note: Only one single-color LED – everything must work via rhythm and brightness (PWM), not color.*
  <br>`ux-31` · Status LED language · effort small · HW yes · ★ 6 · V1 2/4
- **Parent brake** — In kids mode a separate slider limits the top speed and disables rewinds/reverse completely. Visible through a small pacifier icon in the status, so adults understand why everything is more relaxed. *Note: The server must enforce this via the existing limits, not the UI.*
  <br>`ux-25` · Child-friendliness · effort small · HW yes · ★ 6 · V1 1/4
- **Friendly error comics** — Each known error state has a mini illustration with Louie: 'Lever is on' (Louie points at the lever), 'Battery low' (Louie sweats), 'Motor blocked' (Louie is stuck in a paddle), 'Driver fault' (Louie with a wrench). Each with a concrete next step. *Note: Motor-blocked detection via current measurement is possible, thresholds must be calibrated on the prototype; keep graphics small as SVG.*
  <br>`ux-29` · Error and connection indicators · effort medium · HW yes · ★ 6 · V1 1/4
- **Screen-stays-on help** — Since Wake Lock is missing without HTTPS, the UI shows a short tip the first time you play on how to extend the display timeout, and optionally tests the trick with a silent, invisible video loop that keeps many phones awake. *Note: The video trick depends on the browser and costs phone battery; the video must be in flash (keep it very small).*
  <br>`ux-41` · Error and connection indicators / UX · effort small · HW limited · ★ 6 · V1 1/4
- **Eliminated screen with revenge feature** — Whoever is eliminated sees a chicken with a band-aid and a fake mourning ribbon, then the screen switches to 'ghost mode' with a semi-transparent design and boost/rewind buttons (if the mode allows it). Elimination becomes a role change instead of being kicked out. *Note: The game master or the player must report elimination – the electronics cannot see chips.*
  <br>`ux-12` · Player view / animation · effort medium · HW yes · ★ 6 · V1 0/4
- **Spectator big screen (TV/tablet mode)** — A separate view /tv for a tablet or a laptop on the TV: large animated Louie circling in real time with the real speed and direction, four chickens with chip count, event ticker ('Anna boosts!', 'Rudi rewinds!'), round time. No controls, just show. *Note: Each TV client counts as a WebSocket connection; smart TV browsers are often weak – target tablet/laptop.*
  <br>`ux-15` · Spectator big screen · effort medium · HW yes · ★ 6 · V1 0/4
- **Chicken colors with patterns for color-blind players** — Each chicken color also gets a symbol or pattern (dots, stripes, star, heart) and a tile shape. Red/green weakness is then no problem, and children can say 'I'm the star chicken'.
  <br>`ux-23` · Colors / accessibility · effort small · HW yes · ★ 6 · V1 0/4
- **Speedometer as chicken stress barometer** — Instead of a percentage display, a thermometer with chicken faces: relaxed, nervous, panicked, feathers flying. In reverse the scale visibly flips. Children understand speed without numbers.
  <br>`ux-36` · Design / child-friendliness · effort small · HW yes · ★ 6 · V1 0/4
- **Battery display as Louie fuel gauge** — Battery level of the board as a fuel gauge on the plane: full, half, reserve. At reserve the announcement says 'Louie needs to refuel soon – about 2 rounds left'. Estimate from average power consumption per round. *Note: Round estimate is imprecise; mark it as a rough figure.*
  <br>`ux-42` · Error and connection indicators / design · effort small · HW yes · ★ 5 · V1 2/4
- **Sleep screen with snoring Louie** — When the device goes to sleep, all phones show a snoring Louie and 'Flip the lever to wake'. One minute before, a yawning Louie asks 'One more round?' with a large 'Stay awake' button.
  <br>`ux-50` · Animation / error indicators · effort small · HW yes · ★ 5 · V1 1/4
- **Rewind as cassette button** — The rewind button looks like an old cassette key with a double arrow. When pressed, a small tape animation rewinds; all other phones briefly show VHS noise with the culprit's name ('Rudi rewinds!'). Allowance as small cassette icons, cooldown as a filling tape. *Note: The server decides on success; the UI must show 'rejected (cooldown/globally locked)' cleanly.*
  <br>`ux-8` · Player view / animation · effort medium · HW yes · ★ 5 · V1 0/4
- **Role color code across the UI** — Each role has a frame color at the screen edge: guest grey, player in their own chicken color, game master gold, admin violet with a lock. You see at a glance whose phone has which power – also helps when handing the phone over.
  <br>`ux-11` · Screen layout · effort small · HW yes · ★ 5 · V1 0/4
- **Chip counter by tapping** — Each player has three chicken chip icons on the phone and taps one away when losing one. This gives live standings and statistics without sensors. The big screen shows all chips of all players. *Note: Purely manual; the hardware does not detect chip losses. Forgotten inputs distort the statistics.*
  <br>`ux-14` · Player view · effort small · HW limited · ★ 5 · V1 0/4
- **Announcer voice via the phones** — The game master's phone (or the big screen) announces via speech synthesis: 'Three, two, one – Louie takes off!', 'Watch out, reverse gear!', 'Yellow is out!'. Several voice personalities: sports reporter, airport announcement, farmyard grandpa. *Note: Web Speech API sounds different on each device, needs a user gesture on iOS to unlock; offline voices are not available on all devices.*
  <br>`ux-18` · Sound / announcements · effort medium · HW yes · ★ 5 · V1 0/4
- **Synthetic sound effects instead of audio files** — Propeller hum, clucking, rewind squeak and boost hiss are generated in the browser via the Web Audio API (oscillators, noise). Saves flash and sounds deliberately retro. The propeller sound follows the real speed in pitch. *Note: Flash budget ~100 KB compressed argues against samples; Web Audio needs a user gesture to start.*
  <br>`ux-19` · Sound / announcements · effort medium · HW yes · ★ 5 · V1 0/4
- **Screen reader and large text support** — Clean ARIA labels, live regions for announcements ('Round running, speed high'), respects system font size and 'reduce motion'. Whoever has set reduced motion gets no wobbling animations and no screen flicker.
  <br>`ux-26` · Accessibility · effort medium · HW yes · ★ 5 · V1 0/4
- **Simultaneous rewinds as collision gag** — If two players press rewind almost at the same time, only one counts (not added up, per the concept). The UI turns this into a gag: 'Tape tangle! Yellow was faster', the loser gets their rewind back. *Note: Returning the allowance is a game rule decision.*
  <br>`ux-49` · Player view / animation · effort small · HW yes · ★ 5 · V1 0/4
- **Vibration language (Android) with iOS substitute** — Short-short = boost ready, long = reverse kick coming, triple = your turn in the party game. On iOS, where vibration is missing in the browser, the screen edge flashes in the chicken color instead and there is a quiet click. *Note: navigator.vibrate only works on Android; iOS substitute purely visual/acoustic.*
  <br>`ux-21` · Haptics · effort small · HW limited · ★ 4 · V1 1/4
- **Kids mode: pictures instead of text** — A switch in the lobby makes the UI picture-based: icons instead of words, larger buttons (≥ 72 px), no numbers, only a 'slow/fast' snail-rocket scale, no cancel dialogs with small print. Dangerous menus (admin, mode editor) completely hidden.
  <br>`ux-24` · Child-friendliness · effort medium · HW yes · ★ 4 · V1 0/4
- **Pass-the-phone mode** — For rounds with only one or two phones: after each action the UI switches to a screen 'Pass the phone to Green' with a large color banner. So one phone is enough for all players.
  <br>`ux-39` · Screen layout · effort small · HW yes · ★ 4 · V1 0/4
- **First-time tutorial as test flight** — On first opening, the UI offers a 30-second test flight: Louie flies slowly, the phone explains with speech bubbles 'This is your boost – try it!', 'This is the rewind – use it sparingly!'. Afterwards a checkmark 'Already know it' per device in localStorage. *Note: Needs lever on; rewind demo in a mini dose within the reverse limits.*
  <br>`ux-43` · Onboarding · effort medium · HW yes · ★ 4 · V1 0/4
- **Emoji reactions in real time** — Players and spectators can throw emojis (chicken, laughter, anger, beer) that fly across the big screen. Rate-limited so the ESP is not flooded. *Note: Each reaction is a WebSocket message; throttle on the server (e.g. 1 per 2 s per client).*
  <br>`ux-45` · Spectator big screen / party · effort small · HW yes · ★ 4 · V1 0/4
- **Remember language and sound per device** — Each phone remembers volume, announcer voice, kids mode, contrast and hand (left-/right-handed, mirrors button layout) locally. No account needed, but the next evening everything is as usual. *Note: localStorage can be empty in private mode – the UI must work without it.*
  <br>`ux-46` · Accessibility / UX · effort small · HW yes · ★ 4 · V1 0/4
- **Printable game card with legend** — In the UI an A6 card can be opened for printing: QR codes, LED pattern legend, lever gestures (5× = hotspot, 10× = password reset) and emergency tips. It then lives in the game box. *Note: Do not put the lever gesture info openly on the card if children should not know the reset – admin option.*
  <br>`ux-52` · Onboarding / accessibility · effort small · HW yes · ★ 4 · V1 0/4
- **High-contrast and party-light mode** — A mode with extremely large numbers and black/yellow for dim party rooms, plus a 'disco mode' in which the phone screen pulses in the chicken color in time with the motor speed and serves as table lighting. *Note: Disco mode: photosensitivity warning, limit flash frequency.*
  <br>`ux-27` · Design / accessibility · effort small · HW yes · ★ 3 · V1 0/4
- **Event ticker with gloating statistics** — At round end each phone shows a small card: 'You rewound 2×, Anna lost a chip afterwards (maybe because of you)'. Connection from timestamps of rewind and reported chip loss, phrased with a wink. *Note: Causality is guessed, since chip losses are only reported manually.*
  <br>`ux-44` · Player view / party · effort medium · HW limited · ★ 3 · V1 0/4
- **Tell several Louies in the room apart** — If there are two games in the room (louie-a3f2, louie-91bc), each device automatically gets a name and an accent color ('Louie Blue', 'Chewie Orange'). A button 'Which one am I?' makes the status LED of the selected device flash wildly.
  <br>`ux-51` · Onboarding / status LED language · effort small · HW yes · ★ 3 · V1 0/4
- **LED counts players** — When a phone joins, the LED flashes as many times as players are connected. So you notice at the table without looking at the phone that 'the new one' is in. *Note: The LED sits in the battery compartment – check visibility when installed (possibly light guide).*
  <br>`ux-32` · Status LED language · effort small · HW yes · ★ 2 · V1 0/4
- **Theme skins per model** — Depending on the model profile, the whole UI changes: old Louie = farm in pastel, new Louie = bright and modern, Chewie = space with stars and laser sounds. Later unlockable skins (Halloween, Christmas, Oktoberfest). *Note: Do not include brand material (rights); own illustrations. Keep an eye on the flash budget.*
  <br>`ux-37` · Design · effort medium · HW yes · ★ 2 · V1 0/4
- **Drinking game overlay** — An admin or game master switch shows a drinking game layer: on a rewind the culprit's phone shows 'Cheers to your meanness', on chip loss a cup icon. Visually darkened 'bar' design. In kids mode the overlay is locked and invisible. *Note: Responsible wording; offer an alcohol-free alternative ('water/sip/penalty task') on equal terms.*
  <br>`ux-38` · Design / party · effort medium · HW yes · ★ 2 · V1 0/4
- **Admin area as 'hangar'** — The admin area is visually clearly set apart as an aircraft hangar with a tool wall: each tile a tool (Wi-Fi antenna, speedometer for limits, reverse gear lever, battery). Critical settings have a yellow-black warning stripe and explain in one sentence what happens.
  <br>`ux-47` · Screen layout / design · effort medium · HW yes · ★ 2 · V1 0/4
- **Big-screen replay of the last reverse kick** — After each rewind the big screen shows a short slow-motion animation of the simulated Louie, including the culprit's name and a commentator voice. The electronics only supply time and direction; the animation is computed entirely in the browser. *Note: The animation is a simulation, not the real plane position – the electronics do not know the position.*
  <br>`ux-16` · Spectator big screen / animation · effort medium · HW yes · ★ 1 · V1 0/4
- **Estimate Louie's position (revolution counter from current)** — The big screen shows Louie at an estimated position, derived from speed and time, possibly corrected by current spikes when the plane hits a paddle. Looks live, but is only an approximation. *Note: Without a position sensor the estimate drifts; current spike detection is uncertain and would first have to be researched on the prototype.*
  <br>`ux-17` · Spectator big screen · effort large · HW limited · ★ 0 · V1 0/4
- **Motor as speaker and signal device** — The motor 'twitches' as feedback without a phone: two short jolts = Wi-Fi connected, a long hum at an audible PWM frequency = error. With low-frequency PWM the motor can even whistle quiet tones (start melody at power-on). *Note: Only works with lever on (motor in series with the lever); audible PWM increases losses – use only briefly.*
  <br>`ux-33` · Status LED language / haptics · effort medium · HW limited · ★ 0 · V1 0/4

### 5.4 Owner and admin settings (41)

- **Speed cap as a large slider** — A single, prominent slider "At most this fast" with a preview animation of the plane, which caps everything else (modes, boosts, turbo). Below it a sentence in plain language, e.g. "Louie goes at most as fast as the original". Parents understand this immediately, without volts or percent. *Note: Technically just a conversion to the existing limits; calibration per model needed.*
  <br>`besitzer-3` · Profiles & limits · effort small · HW yes · ★ 8 · V1 3/4
- **QR code wall: share the invitation on the phone** — An admin or game master screen shows the two QR codes (join Wi-Fi, open control) huge plus a short guide, so you can simply put the phone in the middle of the table. Optionally with a seat-choice link that directly reserves seat 3. *Note: QR generation in the browser via a small JS library, offline in flash.*
  <br>`besitzer-14` · Wi-Fi & network · effort small · HW yes · ★ 7 · V1 2/4
- **Profile quick pick: Kids / Family / Party / Adults** — Four large tiles in the admin area change a whole package with one tap: speed range, reverse limits, rewind allowance, allowed modes and whether drinking game content is visible. The owner does not need to know 30 sliders but just picks "The nieces are coming today". Individual values can still be adjusted afterwards and the package saved as a custom profile. *Note: Builds on the existing admin limits; needs a clear rule on what a profile overrides and what not.*
  <br>`besitzer-1` · Profiles & limits · effort medium · HW yes · ★ 7 · V1 1/4
- **Block protection with adjustable sensitivity** — If the motor current rises sharply (finger, arm wedged, child holds the plane), the motor stops immediately and reports it in the UI. The owner sets the sensitivity and whether it continues automatically afterwards or waits for release. Always strict in the kids profile. *Note: Also important against overheating of motor and H-bridge; reverse kicks and start-up also produce current spikes, the threshold must distinguish these.*
  <br>`besitzer-23` · Hardware safety · effort medium · HW yes · ★ 7 · V1 1/4
- **Battery protection settings** — The admin sees the battery state with a charge cycle estimate and sets the undervoltage warning, soft round end and cut-off threshold. Option "battery-friendly": turbo only above a minimum voltage, so the battery is not drained and no brownout restarts the ESP. *Note: Hard lower bound on the cut-off threshold, so LiPos cannot be deep-discharged.*
  <br>`besitzer-24` · Hardware safety · effort small · HW yes · ★ 6 · V1 1/4
- **Emergency stop button on every phone** — The admin can enable that every connected phone (not just the game master) has a red stop button. Abuse is logged, and after a stop the round only restarts via the lever. On by default in the kids profile. *Note: The lever stays the real, software-independent emergency stop.*
  <br>`besitzer-26` · Hardware safety · effort small · HW yes · ★ 6 · V1 1/4
- **Drinking game unlock with age confirmation** — Drinking game content (rules, penalty announcements, mode texts) is invisible by default. The admin deliberately unlocks it, confirms "all participants are of legal age" and can bind it to a location profile or time window. Unlocking is not possible in the kids profile. *Note: Pure self-declaration, no real proof of age; communicate it honestly as such.*
  <br>`besitzer-27` · Youth protection · effort small · HW yes · ★ 6 · V1 1/4
- **Block or kick players** — The admin or game master sees all connected phones (nickname, seat, connection time) and can disconnect individual sessions, mute them (no boosts/rewinds) or block them for the evening. Helps against the one guest who only trolls from the sofa. *Note: Block only per token, can be bypassed by deleting the cookie; sufficient for a toy.*
  <br>`besitzer-32` · Permissions & roles · effort medium · HW yes · ★ 5 · V1 0/4
- **Device name and personality** — The owner gives the device a name ("Louie from the attic", "Chewie the Second"), an emoji and a main color for the UI. Hotspot name, mDNS name (louie-dachboden.local) and greeting text are derived from it. With several devices at a party you immediately see which is which. *Note: Restrict names for SSID/hostname to allowed characters.*
  <br>`besitzer-10` · Personalization · effort small · HW yes · ★ 4 · V1 1/4
- **Reverse budget as a visible account** — Instead of three abstract limits (duration, interval, share), the owner sees a "reverse account per round", e.g. 6 seconds, which mode randomness and all rewinds use up together. In the game a small bar shows how much is left. This makes the limit understandable and fair for everyone. *Note: Variant: separate accounts for mode and players.*
  <br>`besitzer-4` · Reverse & rewind · effort medium · HW yes · ★ 4 · V1 0/4
- **Rewind fine-tuning for hosts** — A separate admin page just for the rewind: allowance per player, cooldown per player and global, kick length (0.3–1 s), whether eliminated players may rewind, whether you can protect yourself briefly after a rewind (immunity), and whether two simultaneous rewinds cancel each other. As templates: "gentle", "mean", "chaos". *Note: Direction changes always need a ramp; very short kicks (<0.3 s) may be hardly perceptible mechanically, test on the prototype.*
  <br>`besitzer-5` · Reverse & rewind · effort medium · HW yes · ★ 4 · V1 0/4
- **Last-round button for parents** — An admin or game master button "This is the last round" announces the end prominently on all phones and then blocks new starts for an adjustable time. Saves discussions in the evening, because the game and not the parents says it's over.
  <br>`besitzer-7` · Time & quiet · effort small · HW yes · ★ 4 · V1 0/4
- **Safe update with fallback** — Updates go into a second partition; if the new firmware does not start cleanly or the admin does not report "works" within 5 minutes, the device automatically reverts to the old version. Additionally, update only with sufficient battery and lever off. *Note: 4 MB flash is only just enough for two partitions plus file system; define partitioning early.*
  <br>`besitzer-20` · Updates & maintenance · effort medium · HW yes · ★ 4 · V1 0/4
- **Alcohol-free switch and substitute tasks** — In drinking game mode each player can choose "alcohol-free" for themselves; penalties then become water, juice, squats or funny tasks. The owner can define that alcohol-free is the default and alcohol must be actively chosen per person.
  <br>`besitzer-28` · Youth protection · effort small · HW yes · ★ 4 · V1 0/4
- **Lock settings until the end of the game** — Option that during a running round not even the admin can change limits or profiles, except emergency stop. Prevents someone from secretly turning up the turbo for themselves. Changes are queued and become active after the round.
  <br>`besitzer-33` · Profiles & limits · effort small · HW yes · ★ 4 · V1 0/4
- **Backup as a file and as a QR code** — Download the complete configuration (without passwords, optionally with Wi-Fi networks) as a JSON file and restore it. Additionally: individual modes as a compact QR code or text snippet that you can photograph, send via messenger or feed to another device. *Note: Downloading in an insecure context works via a blob link; QR only for small modes (length limit).*
  <br>`besitzer-15` · Backup & sharing · effort medium · HW yes · ★ 3 · V1 1/4
- **Noise level and sounds on the phones** — The device itself has no speaker, but the phones can play effects (motor hum, chicken clucking, rewind sound). The owner sets: sounds on/off, only on the game master phone, volume recommendation, "whisper mode" without sounds and with a slower motor (the motor itself is quieter at low speed). *Note: No buzzer on the board; sound only via the browser. Audio files cost flash (4 MB), so few, short, compressed clips. iOS only plays audio after user interaction.*
  <br>`besitzer-8` · Volume & atmosphere · effort medium · HW limited · ★ 3 · V1 0/4
- **Quieter motor noise by PWM choice** — Admin option that selects the PWM frequency (e.g. 20 kHz inaudible vs. lower for more torque) and the ramp steepness. A "quiet" preset uses soft ramps and no abrupt direction changes, so nobody wakes up in the next room at night. *Note: Only as an expert setting; gear noise remains.*
  <br>`besitzer-9` · Volume & atmosphere · effort small · HW yes · ★ 3 · V1 0/4
- **Rename chicken colors and seat names** — The four seats can be freely named and given colors, matching the real chips or own stickers (e.g. "Seat by the window", "Grandma"). Other default names for Chewie to match the theme. Optionally fixed regular players per seat.
  <br>`besitzer-11` · Personalization · effort small · HW yes · ★ 3 · V1 0/4
- **Guest hotspot with disposable password** — For parties the admin creates a party password for the hotspot that automatically expires after the evening (or after X hours) and reverts to the sticker password. A matching QR code is shown large on the admin phone so guests can scan it. *Note: Solve expiry without a clock via uptime/restart; recovery via lever gesture remains.*
  <br>`besitzer-13` · Wi-Fi & network · effort medium · HW yes · ★ 3 · V1 0/4
- **Factory reset in stages** — Three reset stages instead of one: delete statistics only, settings to default (modes and Wi-Fi networks remain), delete everything. Each stage with plain text on what is lost, and lever confirmation. Before the full reset a backup is automatically offered for download.
  <br>`besitzer-35` · Updates & maintenance · effort small · HW yes · ★ 3 · V1 0/4
- **Sleep and wake behavior** — Settings for how quickly Louie falls asleep, whether he wakes via lever gesture or only by switching on, and whether after waking he automatically goes to the last profile or to the safe kids profile. Plus a transport mode that keeps Wi-Fi completely off until actively woken. *Note: GPIO wake from deep sleep on the C3 still to be confirmed per the concept.*
  <br>`besitzer-40` · Time & quiet · effort medium · HW limited · ★ 3 · V1 0/4
- **Party report at the end of the evening** — After a party the UI creates a summary to share (image or text): number of rounds, wildest rewind, champion of the evening, longest survival time. The owner sets whether names appear in it or everything stays anonymous. *Note: Image can be generated via canvas in the browser; observe privacy for names.*
  <br>`besitzer-41` · Statistics · effort medium · HW yes · ★ 3 · V1 0/4
- **Child lock with lever seal** — In the kids profile all turbo and reverse functions are hard-locked, and releasing the lock requires, besides the admin password, flipping the lever in a certain rhythm. So a child who happens to know the password cannot unlock anything from the children's room without being at the game. *Note: As with first setup: physical access counts as proof of ownership.*
  <br>`besitzer-2` · Youth protection · effort small · HW yes · ★ 2 · V1 0/4
- **Round time and play time limit** — The owner defines: maximum duration of a round, maximum play time per day or per session ("after 45 minutes it's over"), and optionally fixed quiet times (e.g. after 19:30 only relaxed mode or not at all). Shortly before expiry a friendly hint appears in the UI ("One last round!"). *Note: Time of day is only reliable with home Wi-Fi via NTP; on the hotspot the phone can supply the time when connecting (can be manipulated).*
  <br>`besitzer-6` · Time & quiet · effort medium · HW limited · ★ 2 · V1 0/4
- **Clone configuration to other devices** — A button "Transfer these settings to another Louie" creates a package (limits, profiles, modes, permissions) that you import on the second device. Model-dependent values (old/new Louie, Chewie) are not blindly copied but converted via the percentage logic. *Note: Easily doable via file/phone as a bridge.*
  <br>`besitzer-18` · Multiple devices · effort medium · HW yes · ★ 2 · V1 0/4
- **Update channel and update reminder** — The admin chooses "stable" or "experimental". On home Wi-Fi the UI (the phone has internet) can check whether newer firmware exists and point it out to the admin. The phone does the download; the upload to the device runs locally. *Note: The device itself stays without cloud; check only in the browser. Verify the file's origin via signature/checksum.*
  <br>`besitzer-19` · Updates & maintenance · effort medium · HW yes · ★ 2 · V1 0/4
- **Game statistics for owners** — A statistics area shows: number of rounds, total play time, favorite mode, longest round, how often the rewind was pressed and by whom, most frequent winner (if elimination was marked). Can be reset or switched off completely. *Note: The device does not detect elimination itself; winner statistics are only as good as the inputs. Spare flash write cycles (save in batches).*
  <br>`besitzer-21` · Statistics · effort medium · HW limited · ★ 2 · V1 0/4
- **Maintenance indicator for motor and gearbox** — From runtime and motor current the device calculates a "health value" and reports e.g. "Motor needs more current than before, check gearbox or clean flight arm". Plus an operating hours counter and a counter for blockings. *Note: Motor current measurement exists, but its significance must first be calibrated on the prototype.*
  <br>`besitzer-22` · Statistics · effort medium · HW limited · ★ 2 · V1 0/4
- **Heat estimate and forced break** — Without a temperature sensor the firmware estimates the heating of motor and driver from current times time. After long turbo phases it forces a short cool-down break ("Louie needs to refuel") and lowers the top speed until the value has recovered. *Note: Only a model, not a measurement; the DRV8213 itself has over-temperature shutdown as the last line.*
  <br>`besitzer-25` · Hardware safety · effort medium · HW limited · ★ 2 · V1 0/4
- **Responsibility brake in the drinking game** — Admin settings for the maximum number of penalty sips per person and hour, mandatory breaks after a number of rounds and an automatic water round. If someone reaches the limit, the UI switches to substitute tasks for that person. Optionally a clear notice "No driving after the game". *Note: The device can only count what is entered via the phones.*
  <br>`besitzer-29` · Youth protection · effort medium · HW yes · ★ 2 · V1 0/4
- **Tap-to-edit permission matrix** — Instead of individual switches, a table of roles × permissions (guest, player, game master, profile) with checkmarks: save modes, rewind, boost, become game master, emergency stop, see statistics. Below it the templates "open", "normal", "strict". *Note: Fits directly with the planned permission list in the configuration.*
  <br>`besitzer-30` · Permissions & roles · effort medium · HW yes · ★ 2 · V1 0/4
- **Change log** — A short logbook in the admin area: who (session/profile) changed what when, when updates were installed, when locks or blockings were triggered. The last 50 entries in a ring buffer, exportable as a file. *Note: Timestamps without NTP only relative (since start).*
  <br>`besitzer-34` · Updates & maintenance · effort small · HW yes · ★ 2 · V1 0/4
- **Status LED options** — The owner chooses what the status LED shows: network mode, battery level, rewind cooldown, or nothing at all ("dark" for night parties or so that children are not distracted by it). Brightness adjustable via PWM. *Note: Only one single-color LED in the battery compartment, probably poorly visible.*
  <br>`besitzer-36` · Personalization · effort small · HW yes · ★ 2 · V1 0/4
- **Model profile calibration via wizard** — A guided test measures start-up voltage, idle current and perceived top speed of the specific unit and stores its own model profile from that. Especially for old, worn-out Louies or makers with a third-party motor. *Note: Uses motor current measurement; a human must confirm the top speed by eye.*
  <br>`besitzer-37` · Profiles & limits · effort medium · HW yes · ★ 2 · V1 0/4
- **Custom texts and language packs** — The owner can override announcements and labels (family jokes, dialect, wedding party theme) or install another language. Texts are stored centrally as JSON and can be exported and shared. *Note: Flash space for language packs is limited.*
  <br>`besitzer-39` · Personalization · effort medium · HW yes · ★ 2 · V1 0/4
- **Several home Wi-Fi networks with location profiles** — Each saved Wi-Fi network has a location profile: home = kids profile, holiday house = family, shared-flat party = adults. When Louie connects to the network, the matching profile is active automatically. Without a known network (hotspot) the most cautious profile applies. *Note: Good safety default: unknown location = strict.*
  <br>`besitzer-12` · Wi-Fi & network · effort medium · HW yes · ★ 1 · V1 0/4
- **Tournament across several games** — With several devices at a party (Louie and Chewie), an admin links them into a tournament: same profiles and limits on all, shared start release, ranking across all tables. One device is the leader, the others follow. *Note: Requires device-to-device communication (Wi-Fi or ESP-NOW); difficult in hotspot operation. Rather a later version.*
  <br>`besitzer-17` · Multiple devices · effort large · HW limited · ★ 1 · V1 0/4
- **Second admin / co-owner** — Besides the main admin, a restricted "host" with its own PIN can be created: may switch profiles, create a party hotspot and set round times, but not change limits, Wi-Fi networks or updates. Ideal when a teenager runs the party. *Note: Corresponds to stage 3 from the concept; the plain-text password problem without HTTPS remains.*
  <br>`besitzer-31` · Permissions & roles · effort medium · HW yes · ★ 1 · V1 0/4
- **Mode exchange between devices** — If two Louies are on the same Wi-Fi, one finds the other via mDNS and offers: "Take over modes from Louie-Dachboden?". At family gatherings or in game cafés, favorite modes can travel this way without internet. The receiving admin confirms every transfer. *Note: The ESP must act as an HTTP client to the other ESP; RAM is tight. Simpler variant: via the phone as intermediate storage.*
  <br>`besitzer-16` · Multiple devices · effort large · HW limited · ★ 0 · V1 0/4
- **Maker mode with raw values** — A hidden expert menu (after admin login and a warning) shows live graphs of current, voltage and PWM and allows custom limits beyond the standard range, e.g. for modifications with a stronger motor. Afterwards the normal UI permanently shows a hint "Expert settings active". *Note: Absolute hardware limits (driver current, battery) must never be exceedable.*
  <br>`besitzer-38` · Maker · effort medium · HW limited · ★ 0 · V1 0/4

### 5.5 Hardware, safety & robustness (59)

- **Rewind lock circuit** — The rewind is debounced globally: after each reverse kick there is a global protection time in which nobody can trigger a new one, no matter how many players have allowance left. Plus a share cap per round. So four phones together cannot produce continuous reverse travel. *Note: Builds on the server limits from the software concept; what matters is the global cooldown instead of only per player.*
  <br>`technik-29` · Abuse protection · effort small · HW yes · ★ 10 · V1 4/4
- **Block detection with immediate stop** — If the motor current rises above a threshold and stays there longer than approx. 200–300 ms (Louie hangs on a paddle, finger in the arm), the firmware switches to braking and then off. The UI shows "Louie is stuck"; it only continues after lever off/on. Complements the 2 A current limit of the DRV8213 (ITRIP via R_IPROPI), which only limits and does not switch off. *Note: The threshold depends on the model and must be learned (see calibration run); mask short current spikes at start-up.*
  <br>`technik-1` · Motor protection · effort small · HW yes · ★ 9 · V1 4/4
- **Game master emergency stop in the UI** — On every game master and admin screen an always visible red stop button that brakes immediately, regardless of the mode. Optionally also enabled for player phones ("anyone may stop"), e.g. with small children. *Note: Does not replace the lever, which disconnects in hardware.*
  <br>`technik-32` · Child safety · effort small · HW yes · ★ 9 · V1 4/4
- **Direction change always through zero with dead time** — Forward to reverse never happens directly: ramp to 0, brake briefly, 50–150 ms pause, then ramp in the opposite direction. Applies in the lowest motor layer, also for rewind kicks. This makes the reverse kick feel short but hardly stresses battery and gearbox. *Note: The ramp noticeably eats time from a 0.5 s kick; define the kick duration as net reverse time.*
  <br>`technik-3` · Motor protection · effort small · HW yes · ★ 8 · V1 4/4
- **Safe defaults for an unknown model** — As long as no model profile is selected, the most cautious profile applies (1.5 V old Louie, no turbo, no reverse). So a freshly gifted kit can never overdrive the old 1.5 V motor with 4.2 V.
  <br>`technik-48` · Motor protection · effort small · HW yes · ★ 8 · V1 4/4
- **Prevent seat theft** — An occupied seat can only be taken over if the previous client has been gone for 60 s or the game master releases it. Prevents a guest from hijacking a player's seat and using up their boosts or rewinds. Limit new sessions per device (second phone trick).
  <br>`technik-30` · Abuse protection · effort small · HW yes · ★ 8 · V1 3/4
- **Multi-stage watchdog** — Level 1: the motor task stops after 500 ms without fresh setpoints. Level 2: the hardware watchdog restarts if the main program hangs. Level 3: after three crashes in a row the firmware starts in "safe mode" without custom modes and without updates, only Classic plus the admin page. *Note: Safe mode needs immutable fallback logic in the frozen modules.*
  <br>`technik-16` · Robustness · effort medium · HW yes · ★ 7 · V1 4/4
- **Start-up masking and soft start** — When starting and at every direction change, the current is briefly high. Block detection is then suspended for a time window; at the same time the motor starts via a ramp instead of at full duty cycle. This prevents false alarms and voltage dips.
  <br>`technik-2` · Motor protection · effort small · HW yes · ★ 7 · V1 3/4
- **Undervoltage in three stages** — Stage 1 (e.g. 3.5 V under load): warning in the UI and LED pattern. Stage 2 (3.4 V): turbo and reverse locked, top speed drops. Stage 3 (3.3 V): round ends cleanly with a hint, motor off, Wi-Fi only. Below 3.2 V deep sleep, before the battery protection circuit cuts off hard. *Note: Measure voltage under load and correct for internal resistance, otherwise false warnings on boosts.*
  <br>`technik-11` · Battery protection · effort small · HW yes · ★ 7 · V1 3/4
- **Lever gestures with time window and confirmation** — Gestures (force hotspot, admin reset, factory reset) only apply in the first 10 s after waking and are acknowledged by an LED/beep pattern; a second gesture confirms. So no child accidentally triggers a factory reset while wildly flipping the lever.
  <br>`technik-25` · Safety · effort small · HW yes · ★ 7 · V1 2/4
- **Turbo time budget** — Above the nominal voltage the motor may only run for a limited time, e.g. max. 10 s at a time and max. 20 % of the round. Afterwards automatically back to 100 %. The admin sets the values; modes and boosts cannot override them.
  <br>`technik-5` · Motor protection · effort small · HW yes · ★ 6 · V1 3/4
- **Rate limit per session and per device** — The server accepts only a limited number of actions per second per session (e.g. 5 messages/s, boost key otherwise ignored after cooldown). Whoever spams via script or constant pressing is throttled and marked on the game master screen. Also protects the scarce RAM.
  <br>`technik-28` · Abuse protection · effort small · HW yes · ★ 6 · V1 3/4
- **Update with rollback and trial run** — After an update the new version starts in a trial run. Only when the self-test and web server run and the admin presses "confirm" (or 3 starts without a crash) does it become permanent. Otherwise automatically back to the previous version. Never update during a round and only with sufficient battery.
  <br>`technik-46` · Update safety · effort medium · HW yes · ★ 6 · V1 2/4
- **Configuration with checksum and fallback copy** — config.json and calibration are stored with a checksum, plus a last good copy. If the main file is damaged (power failure while writing), the firmware loads the copy or safe defaults instead of running with broken limits.
  <br>`technik-47` · Robustness · effort small · HW yes · ★ 6 · V1 2/4
- **Secure lever detection via current** — While running, "lever off" is detected by zero current. So that this is not misinterpreted due to a brief zero current during ramps or braking, a minimum duty cycle applies when checking, plus a confirmation via SENSE after a short driver sleep. Result: round end is detected reliably.
  <br>`technik-49` · Robustness · effort small · HW yes · ★ 6 · V1 2/4
- **Connection limit and guest kick** — Maximum e.g. 8 clients; if the limit is reached, pure guests without a seat are disconnected first. The game master can block individual devices for the game. Protects the ESP from too many open WebSockets.
  <br>`technik-31` · Abuse protection · effort small · HW yes · ★ 6 · V1 1/4
- **No telemetry, visibly assured** — The firmware never connects to the internet (except optional NTP and update check, both switchable and off by default). The info screen clearly states what is stored. Important because children play and the device is given away.
  <br>`technik-44` · Privacy · effort small · HW yes · ★ 5 · V1 2/4
- **Motor off when the game master loses connection (optional)** — In modes that depend heavily on the phone (e.g. game master controls live), Louie drops back to a safe base speed if the controlling client sends nothing for 3 s. The lever keeps working independently.
  <br>`technik-17` · Robustness · effort small · HW yes · ★ 5 · V1 1/4
- **Self-test at start** — After waking, the firmware checks in under a second: motor connected (SENSE), battery voltage plausible, zero point of the current measurement (IPROPI). Result as an LED pattern and as a traffic light in diagnostics. Helps builders find wrongly inserted boards or bad contacts.
  <br>`technik-20` · Diagnostics · effort small · HW yes · ★ 5 · V1 1/4
- **Physical proof of ownership via lever** — Critical actions (set admin password, firmware update, limits above default, open hotspot) must additionally be confirmed within 30 s by lever on/off. Whoever is only on the Wi-Fi but not sitting at the table cannot change anything important.
  <br>`technik-27` · Access security · effort small · HW yes · ★ 5 · V1 1/4
- **Kids mode with current sensitivity** — An admin preset: no turbo, no reverse, lower top speed and much more sensitive block detection, so that Louie stops even with light finger resistance. For toddlers who like to reach into the arm. *Note: Sensitivity is limited by the current measurement; light touching may produce hardly any current rise.*
  <br>`technik-33` · Child safety · effort small · HW yes · ★ 5 · V1 1/4
- **Safety limits only upwards with a warning** — If the admin sets the turbo limit, reverse duration or ramp above the project recommendation, the UI shows a clear warning about risks (motor wear, frustration, brownout) and requires lever confirmation. Absolute hard limits (e.g. never above 4.2 V battery, never above 2 A) are fixed in the code.
  <br>`technik-59` · Safety · effort small · HW yes · ★ 5 · V1 1/4
- **Thermal motor model (I²t)** — The firmware integrates the measured current over time and so estimates the heating of motor and driver. If turbo is played for a long time or blocking happens often, the allowed top speed drops gently ("Louie is exhausted") until he has cooled down. Protects the small original motor, for which there is no datasheet. *Note: Model parameters can only be roughly estimated; start conservatively.*
  <br>`technik-4` · Motor protection · effort medium · HW yes · ★ 5 · V1 0/4
- **Finger pinch protection by backing off** — When a blockage is detected, Louie not only stops but makes a tiny jolt backwards (e.g. 100 ms at low voltage) to release a trapped finger or a wedged chicken, and then stays put. *Note: Only very short and weak, otherwise it becomes a hazard itself; as an option.*
  <br>`technik-34` · Child safety · effort small · HW yes · ★ 5 · V1 0/4
- **Data-minimal profiles** — Profiles contain only nickname, color and emoji, no real names, no photos, no device IDs other than the random token. Statistics are local and can be deleted with one button; profiles expire automatically after x days without use.
  <br>`technik-43` · Privacy · effort small · HW yes · ★ 5 · V1 0/4
- **Brownout detector and cause memory** — After every restart the firmware reads the reset reason (brownout, watchdog, crash, normal) and stores the last 10 with a timestamp relative to uptime and the last motor level. If brownouts pile up at direction changes, the ramp automatically becomes flatter.
  <br>`technik-15` · Robustness · effort small · HW yes · ★ 4 · V1 1/4
- **Harden session tokens** — Tokens are random (hardware RNG of the ESP), expire, are regenerated at admin login and are bound to the seat. Admin rights only via HttpOnly cookie, never in localStorage. Without HTTPS a residual risk remains, but copying a player token does not give admin rights.
  <br>`technik-40` · Network security · effort small · HW yes · ★ 4 · V1 1/4
- **Remaining play time display** — From the state of charge (voltage curve) and typical consumption per round, the lobby shows "enough for about 12 more rounds" instead of just a percentage. More understandable than volts for parties. *Note: State of charge via voltage is only rough for LiPo; learned values from past rounds improve the estimate.*
  <br>`technik-13` · Battery protection · effort medium · HW yes · ★ 4 · V1 0/4
- **Charge detection and playing while charging** — When USB voltage is present (indirectly detectable via rising battery voltage over the cable, or via a VBUS divider), the UI shows "charging" and pauses sleep mode. Optionally lock turbo while charging so that power path and charge controller are not overloaded. *Note: Without a dedicated VBUS pin only indirectly detectable; a free GPIO (IO2/IO8 are strapping pins) would need a board change.*
  <br>`technik-14` · Battery protection · effort medium · HW limited · ★ 4 · V1 0/4
- **Chip temperature and driver over-temperature** — The ESP32-C6 has an internal temperature sensor; together with the current trace at IPROPI (the DRV8213 switches off by itself at over-temperature; a fault pin is not connected) this gives a simple heat warning in the battery compartment. At the limit: lock turbo, then pause with the hint "Louie needs a break". *Note: The internal sensor measures the chip, not motor or battery; LiPo temperature cannot be measured without an NTC. An NTC on the charger board would be a hardware extension.*
  <br>`technik-18` · Robustness · effort small · HW limited · ★ 4 · V1 0/4
- **Separate guest network instead of home Wi-Fi** — On the home Wi-Fi every party guest only sees the control if they are on the home network. Recommendation in the UI: for parties use the own hotspot, so guests do not have to join the home network. Louie offers a one-tap toggle "Party hotspot" for this.
  <br>`technik-37` · Network security · effort small · HW yes · ★ 4 · V1 0/4
- **Fault analysis in plain language** — Driver faults are not just reported as "error" but interpreted from current (IPROPI), SENSE and voltage at the time: "short circuit/blockage", "undervoltage at the driver", "too hot". Fault log with the latest events in the diagnostics area. *Note: The DRV8213 has no fault pin on the board (no nFAULT connected); interpretation is heuristic.*
  <br>`technik-19` · Diagnostics · effort small · HW limited · ★ 3 · V1 1/4
- **Diagnostics export for makers** — A button creates a JSON file with firmware version, model profile, calibration values, counters, fault log and reset reasons, without Wi-Fi passwords and player names. Can be attached to a GitHub issue if you gave the kit away and the recipient has problems.
  <br>`technik-22` · Diagnostics · effort small · HW yes · ★ 3 · V1 1/4
- **Calibration run during setup** — In the setup wizard Louie runs for 10–15 s at several speeds in both directions. Measured are start-up voltage (from when does it turn at all), idle current per level and current spike at start-up. From this the firmware sets minimum voltage, block threshold and lever detection threshold automatically. *Note: Partly replaces manual measurement of the turbo limit; do not ramp up turbo itself automatically.*
  <br>`technik-8` · Calibration · effort medium · HW yes · ★ 3 · V1 0/4
- **Measure contact quality in the battery compartment** — If the motor current briefly jumps to zero while running without the lever being moved, this indicates a loose contact at spring or plate. Diagnostics count these dropouts and show "Check contacts". Important because the board is only clamped in without soldering. *Note: Hard to distinguish from very short lever wobbling; use duration as criterion.*
  <br>`technik-21` · Diagnostics · effort small · HW yes · ★ 3 · V1 0/4
- **Factory reset in stages** — Stage 1: reset only admin password and Wi-Fi networks. Stage 2: additionally configuration and calibration. Stage 3: everything including custom modes and statistics. Via admin page or long lever gesture; the firmware itself is always kept.
  <br>`technik-26` · Safety · effort small · HW yes · ★ 3 · V1 0/4
- **Volume limits for phone sounds** — The admin sets a maximum volume for sound effects in the web UI and can set a quiet time (e.g. from 20:00 no sounds, no vibration). Can be switched off for party mode. *Note: The browser does not allow real system volume; this only concerns the volume of the page's own audio elements.*
  <br>`technik-35` · Child safety · effort small · HW yes · ★ 3 · V1 0/4
- **Game code instead of open access** — On the home Wi-Fi a four-digit code or QR code appears on the game master phone; only whoever enters it can take a seat. Prevents flatmates or neighbors on the same network from secretly pressing rewinds.
  <br>`technik-38` · Network security · effort small · HW yes · ★ 3 · V1 0/4
- **Rotate hotspot password** — Besides the fixed sticker password, the admin can create a temporary party password that expires again after sleep mode. The QR code is then shown on the game master phone instead of being scanned from the sticker. *Note: Guests must reconnect after every wake-up.*
  <br>`technik-39` · Network security · effort medium · HW yes · ★ 3 · V1 0/4
- **Force meter: who is braking Louie?** — The motor current rises when a paddle lifts Louie strongly or a player mechanically brakes the plane. The UI shows a live "Louie load" indicator; hits with high load appear as an effect ("Boom!"). The electronics cannot see which player it was, but the mood becomes audible and visible. *Note: Whether paddle hits are measurable in the current at all must be tested on the real game; noise from PWM and brushes.*
  <br>`technik-50` · Motor current game feature · effort medium · HW limited · ★ 3 · V1 0/4
- **Overload as game event "Louie gets angry"** — If Louie is repeatedly braked hard, the mode reacts: short pause, then a revenge kick forwards (within the limits). The current measurement thus turns from protection into game mechanics, and holding against it has a consequence. *Note: Only useful if braking is reliably detectable; must never override the block shutdown.*
  <br>`technik-54` · Motor current game feature · effort medium · HW limited · ★ 3 · V1 0/4
- **Status LED as safety traffic light** — Besides the network mode, the LED also shows safety states: double flash = blockage detected, constant flicker = battery almost empty, slow pulsing = cool-down break. So you understand without a phone why Louie is not flying. *Note: The LED sits in the battery compartment; visibility from outside depends on the model (old model open, new one with lid).*
  <br>`technik-56` · Child safety · effort small · HW yes · ★ 3 · V1 0/4
- **Transport and storage mode** — Admin or lever gesture sends Louie into a deep sleep without lever wake-up (only wakeable via USB power). Prevents Louie from constantly waking up in the games box through jostling of the lever and draining the battery. Complements the optional slide switch. *Note: Wake-up only via USB requires VBUS detection or reset via USB; otherwise wake by holding lever on for a long time.*
  <br>`technik-57` · Battery protection · effort small · HW limited · ★ 3 · V1 0/4
- **Self-discharge guard during sleep** — The ESP wakes up from deep sleep e.g. once a day via timer, measures the battery voltage and at a critical level goes into an even deeper sleep without further timers. At the next wake-up the UI warns: "Battery was empty for a long time, please charge."
  <br>`technik-58` · Battery protection · effort small · HW yes · ★ 3 · V1 0/4
- **Gearbox wear counter** — Total runtime, number of starts, direction changes, blockages and turbo seconds are written to flash rarely (e.g. at round end). In the diagnostics area the owner sees how much Louie has already been through; optionally a hint "check the gearbox". *Note: Observe flash write cycles: save only at round end.*
  <br>`technik-6` · Diagnostics · effort small · HW yes · ★ 2 · V1 0/4
- **Idle current trend as wear indicator** — In each round the average current at 100 % during the first seconds is stored. If it rises over weeks, the gearbox is stiff (dust, hair, worn arm). Diagnostics show a small curve and suggest cleaning. *Note: Varies with battery voltage and temperature; only a rough trend.*
  <br>`technik-7` · Diagnostics · effort medium · HW yes · ★ 2 · V1 0/4
- **Estimate battery internal resistance** — Battery voltage shortly before and during a motor step plus the measured current give the internal resistance. If it rises sharply, the LiPo has aged or is too small; diagnostics show "Battery weak, replacement recommended". Also helps to compute a real remaining runtime display.
  <br>`technik-12` · Battery protection · effort medium · HW yes · ★ 2 · V1 0/4
- **Live oscilloscope for current and voltage** — Admin view with a scrolling curve of motor current, battery voltage and setpoint (approx. 20 values/s via WebSocket). Useful for setting the turbo limit and for making block thresholds visible. *Note: Only for admin and only outside rounds with many clients, otherwise WebSocket load.*
  <br>`technik-23` · Diagnostics · effort medium · HW yes · ★ 2 · V1 0/4
- **Motor as speaker (beeping)** — With short PWM in the audible range (e.g. 1–3 kHz, small duty cycle) the motor emits quiet tones without turning. This lets Louie acknowledge without a phone: start tone, countdown, error code, "battery empty". Quiet enough not to disturb. *Note: Volume and sound depend on the model, hardly audible in the game; not while the motor is running. Keep the duty cycle small so nothing moves.*
  <br>`technik-24` · Hardware trick · effort small · HW limited · ★ 2 · V1 0/4
- **Play time limit for parents** — Admin setting: max. play time per day or number of rounds, after that only Classic via lever or nothing at all. Without a real clock the firmware counts from wake-up; with home Wi-Fi it can get the time via NTP. *Note: No time of day in hotspot operation; taking the time from the first connected phone would be an alternative.*
  <br>`technik-36` · Child safety · effort medium · HW limited · ★ 2 · V1 0/4
- **Hit counter from current spikes** — Each short current spike while running is counted as a "contact" (Louie hits a paddle or chip). At round end there is a statistic: "Louie was fended off 37 times". For drinking game variants: every 10 hits a sip for everyone. *Note: Unclear whether individual hits can be cleanly separated from noise; check beforehand with the oscilloscope view.*
  <br>`technik-51` · Motor current game feature · effort medium · HW limited · ★ 2 · V1 0/4
- **Automatic model detection** — Via the winding resistance (SENSE divider with the motor stopped) and the idle current at low voltage, the firmware suggests the matching model profile (old Louie 1.5 V vs. new/Chewie 3 V). The user only confirms. *Note: Distinguishing new vs. Chewie is probably not possible; resolution of the SENSE divider at a few ohms is very coarse. Running a wrongly detected 1.5 V model at 3 V would be harmful, so only a suggestion with a conservative default.*
  <br>`technik-9` · Calibration · effort medium · HW limited · ★ 1 · V1 0/4
- **Detect direction automatically** — Instead of asking "Is Louie turning the right way?", an asymmetry in the current pattern (gearbox/arm runs more easily in one direction) could reveal the direction. More realistic: set the direction by question, but switchable via lever gesture if the phone is missing. *Note: Automatic detection is uncertain; a lever gesture as fallback is reliably feasible.*
  <br>`technik-10` · Calibration · effort small · HW limited · ★ 1 · V1 0/4
- **Admin functions only on the hotspot or via USB** — Option: critical admin pages (update, Wi-Fi passwords, factory reset) are only reachable when connected directly to the Louie hotspot or via USB console. On the home Wi-Fi only the game remains reachable. *Note: Loss of convenience; as an admin option, not as default.*
  <br>`technik-41` · Network security · effort medium · HW yes · ★ 1 · V1 0/4
- **Wi-Fi credentials never readable** — Saved Wi-Fi passwords can only be overwritten or deleted in the UI, never displayed. The configuration export does not contain them by default. Optional encryption with the eFuse key of the ESP32-C6 (flash encryption). *Note: Flash encryption makes maker access via USB considerably harder; rather not as default.*
  <br>`technik-42` · Privacy · effort medium · HW limited · ★ 1 · V1 0/4
- **Signed update packages** — Update packages (firmware image, web UI) carry an Ed25519 signature of the project; the firmware verifies it before installing. Whoever wants their own firmware can store their own keys via an admin option or deliberately switch off the check (with lever confirmation). *Note: Verification on the ESP in the firmware (Rust library or Secure Boot of ESP-IDF) is feasible, path still to be clarified; SHA-256 checksum as a simple first step.*
  <br>`technik-45` · Update safety · effort medium · HW limited · ★ 1 · V1 0/4
- **Round time measurement without a sensor** — The brushed motor produces a ripple in the current per commutation; the speed could be estimated from it (sensorless speed measurement). The firmware could then count real revolutions and readjust the speed under load. *Note: Ripple counting needs fast ADC sampling and good filtering; questionable with 20 kHz PWM and the RC filter at IPROPI. Alternative: measure back-EMF in short PWM pauses.*
  <br>`technik-52` · Motor current game feature · effort large · HW limited · ★ 0 · V1 0/4
- **Back-EMF speed measurement in pauses** — In short freewheeling moments (a few ms) the firmware measures the voltage that the turning motor generates itself. This gives a speed that makes real speed control possible: Louie flies equally fast no matter how hard he is braked, or game modes in revolutions instead of seconds. *Note: The SENSE path via 100k is only usable during driver sleep and rather slow; check feasibility on the breadboard.*
  <br>`technik-53` · Motor current game feature · effort large · HW limited · ★ 0 · V1 0/4
- **Detect whether a chip is lying on Louie** — Wilder idea: a chip wedged in the arm or a torn-off plane changes the load profile permanently. If the idle current deviates strongly from the calibrated value, the UI asks "Is Louie still in one piece?". *Note: Chips are very light; probably only gross defects are detectable.*
  <br>`technik-55` · Motor current game feature · effort medium · HW limited · ★ 0 · V1 0/4
