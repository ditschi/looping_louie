# Idea: Zigbee mode ("On the go with buttons")

Status: 2026-11-06 · idea; hardware is prepared with the ESP32-C6, software later (Zigbee stack from
ESP-IDF, in C or from the Rust firmware via esp-idf).
Basis: [main-board-c6.md](main-board-c6.md) section 4 (coexistence), [idea-wireless-buttons.md](idea-wireless-buttons.md).

## 1. Why a separate operating mode

According to the Espressif coexistence table (C6), a **Zigbee coordinator works neither together with the own hotspot nor
together with the BLE scan** (both "X", not supported). Zigbee is therefore **a separate operating mode**, not an
extra function in party mode. One after the other, everything works, because it is the same radio.

| Operating mode | Radio | Control | Use |
|---|---|---|---|
| **Wi-Fi** (default) | home Wi-Fi or own hotspot, BLE scan for BTHome buttons | web UI on the phone, BTHome buttons | at home, party with phones |
| **On the go (Zigbee)** | no Wi-Fi, Louie is Zigbee coordinator | Zigbee buttons only (e.g. IKEA, Aqara) | on the go, party without phones, always the same mode |
| Home Wi-Fi + Zigbee (later) | Wi-Fi STA + coordinator ("C1", unstable) | web UI and Zigbee buttons | only if the test shows it is stable |

In on-the-go mode everyone plays with buttons. The **last selected game mode** runs (or the lever mode);
the button assignment is set up beforehand in Wi-Fi mode. Pairing the Zigbee buttons also happens in
Wi-Fi mode (the web UI briefly starts the coordinator for it; without a hotspot this only works on home Wi-Fi, or with
a wizard: "Hotspot will be disconnected for 60 s, pair the buttons now").

## 2. Back to Wi-Fi mode – without accidents

Requirement: The switch must **not happen during the game**, not even when everyone presses at the same time.
The key is the **lever**: during a round it is "on".

**Recommendation (two ways, both safe):**

1. **Lever off + hold any two buttons at the same time for 5 s** (decision 2026-11-02).
   - Only with the lever "off", so never in a running round.
   - Two **different** paired buttons, both pressed within 1 s. Not "all", because up to 8 can be
     connected. A single child cannot trigger this by accident.
   - **What the buttons report** (unverified, check in the test): Many Zigbee buttons report a start when held and an end
     on release, e.g. IKEA RODRET/STYRBAR as "Move" … "Stop" or Aqara as "hold" … "release". Then
     Louie measures the 5 s itself: both buttons are in the hold state at the same time. If a button reports "long press" only once
     without an end, the fallback is: two different buttons report "long" within 2 s, with the lever off. That
     does not happen in a game either.
   - Feedback via the status LED (fast blinking), because with the lever off the motor is disconnected. After that
     Wi-Fi or the hotspot starts.
2. **Lever gesture on wake-up** (already in the concept as "force hotspot", software-concept.md 3.1):
   wake Louie and flip the lever 5× quickly within 10 s. Works even when the button batteries
   are empty or the buttons are missing. This is the always-available rescue.

**Optional, to be decided later: start window.** After every wake-up, Louie is in Wi-Fi mode for 20 s first. If
a phone connects during this time, it stays there; otherwise it switches to on-the-go mode. Then usually no
gesture is needed at all. The price is that the buttons only work after 20 s.

**Rejected:** "All buttons at the same time" without the lever condition, because that can happen in a game. Likewise the BOOT button,
because it cannot be reached in the battery compartment.

## 3. Later: switch and show the game mode without a phone

- **Switch game mode:** With the lever off, e.g. hold a button for 3 s → next mode from a favorites list
  (set in Wi-Fi mode, e.g. Classic / Pressure cooker / Turbulence).
- **Show:** The status LED blinks the number of the mode (1×, 2×, 3×), or Louie "shows" the mode with a short
  typical movement as soon as the lever is on (only if noticeable and not disruptive).
- Meanness stays fixed at the last set value in on-the-go mode.

## 4. What to provide for now

- **Hardware:** nothing extra (same radio, same antenna). Useful are the **8 MB flash (C6-MINI-1-H8)**
  and a good antenna position (antenna fix L2 is done, [analysis-wireless-controllers.md](analysis-wireless-controllers.md) 2).
- **Status LED** is mandatory, because it is the only display in on-the-go mode.
- **Software:** The Zigbee stack only exists as a C library for ESP-IDF (`esp-zigbee-sdk`, precompiled). The
  Rust firmware runs on ESP-IDF and can include it as an IDF component and call it via FFI (unverified, not
  tried yet). Context: [firmware-architecture.md](firmware-architecture.md).

## 5. Open items

- [ ] Which Zigbee buttons (IKEA STYRBAR/RODRET, Aqara Mini) and how fast do they report a press?
- [ ] Start window yes/no, and how long?
- [ ] Zigbee + home Wi-Fi (C1) stable in the test?
