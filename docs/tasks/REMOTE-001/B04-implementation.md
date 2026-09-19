# Browser capture implementation and review boundary

B04 implements the accepted behaviour with P4-side provider arbitration. EMOS
and its packet receiver are unchanged. This is an experimental implementation;
local checks do not qualify physical input, LEDs or browser/OS shortcut handling.

## Retained paths

1. The P4 console owner still feeds `ProcessedKeyboard`, the retained VDP
   callbacks/sysvars and stock keyboard packet serializer over the existing UART.
   Browser events never pass through the physical USB takeover callback.
2. `InputOwner` combines the existing agent controller with bounded browser state.
   Capture cancels queued agent/browser events; old held releases drain before
   new input. Physical USB activity cancels browser ownership, including an
   unmapped physical key. Old socket cleanup cannot cancel a replacement owner.
3. Agent RPC retains its Origin prohibition, CRC/sequence checks and 20 ms pacing.
   Browser transitions have no artificial spacing; P4 supplies configured repeat,
   at most once per owner iteration without catch-up. Browser DOM repeats are
   suppressed. Both preserve the pressed key identity through release.
4. Video remains a separate socket. Screen-text reads do not touch input ownership.
   The isolated build retains the installed screen-text/codec composition; a
   build from ordinary tracked video source alone is not that composition.

## Browser wire contract

The current HTTP service admits `/keyboard/browser` only with an Origin exactly
matching `http://` plus its Host header. The existing service has no TLS endpoint.
This is cross-origin browser containment, not authentication against LAN peers.
Opening a socket does not acquire input. Each socket receives a P4-assigned ID;
server session destruction revokes that ID only.

Each binary message is exactly 16 bytes; fragmented/other application frames are
rejected. Integers are unsigned little endian.

| Bytes | Meaning |
|---|---|
| 0–2 | `BK`, protocol 1 |
| 3 | 1 Capture, 2 transition, 3 heartbeat, 4 release, 5 lock snapshot |
| 4–7 | P4 generation; zero on Capture |
| 8–11 | Sequence; 1 on Capture, then strictly increasing without wrap |
| 12–13 | USB HID usage and down (0/1), for transition |
| 14–15 | Known lock mask and absolute values, using stock modifier bits 16/32/64 |

Capture has zero bytes 12–15. It requires EMOS input admission and physical
neutrality. Its acknowledgement returns P4's generation. Replies echo sequence
and replace byte 3 with 0 accepted, 1 rejected/stale, or 2 unavailable. Client
rejection closes its session and requires explicit recapture. Control loss and
five-second lease expiry release held keys. Signed modular elapsed comparison
handles a stale console timestamp and timer wrap. The page sends one heartbeat
per second and also abandons missing replies. Browser queue capacity is 64
transitions with at most six ordinary keys held, plus modifiers.

## Mapping, locks and UI

P4 reuses the UK/US USB mapper, extended for keypad and lock keys. Numeric keypad
navigation follows retained FabGL's Num Lock plus Shift rule. The browser reports
physical positions; interpreted letters are used only to corroborate an otherwise
ambiguous Caps-off observation, never as the transmitted character.

A false `getModifierState` alone is not proof of reporting support. True observations
establish it; subsequent reliable events refresh it. Unknown lock state remains
visible. Caps-sensitive letters and Num-sensitive keypad presses require a known
or explicitly manual state; a blocked key is reported and must be pressed again.
Manual selectors say Manual on/off; the corresponding lock key toggles that
manual state. Num/Scroll-off reporting may require manual selection on browsers
that never report an affirmative state.

Physical USB maintains independent lock state. A USB LED worker publishes changes
through boot Output reports, outside the UART owner. Disconnect releases input
immediately and defers handle deletion while a control request owns it. Each
physical state gets one LED attempt, with failures logged; there is no retry
flood. Actual device LED support and unplug behaviour require bench acceptance.
The existing physical decoder's down-time lock transition convention is retained.

Controls remain inside the fullscreen container but outside the Agon image.
Bottom-edge mouse reveal does not change keyboard ownership. Moving focus to a
control releases held keys; leaving the panel, hiding the page or losing window
focus closes capture. The page never captures automatically after recovery.
Tab/Escape defaults are suppressed when delivered to the focused canvas. No
Keyboard Lock API is requested: browser/OS-reserved shortcuts, including native
fullscreen Escape, remain a platform qualification limit with explicit mouse
release/exit available.

## Local validation and remaining gates

Sanitizer tests exercise admission, unknown locks, key identity, repeat, timer
wrap/stale time, physical takeover, competing browser generations, stale socket
close, agent cancellation and absence of replay/pacing leakage. Chromium uses a
simulated acknowledging peer to exercise actual key events, focus cleanup,
manual state, video independence and fullscreen controls. Existing agent,
processed-key, USB and video-page regressions remain in the validation set.

An isolated P4 build verifies the native SDK integration, including WebSocket
session cleanup and USB control APIs. Local tests do not measure UART delivery
or certify macOS/browser reserved-key behaviour. Next physical gate: flash the
reviewed P4 image with authorization, then verify Legacy CLI, ExCom, USB takeover,
agent exclusion, locks/LEDs, unplug/reconnect and held movement. EMOS needs no
change and no SD fixture is required for ordinary CLI acceptance.
