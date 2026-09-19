# Browser input reuse review — B01

## Executive summary

The current P4 processed-key path is the correct integration point. Reuse its
UK/US mapping, stock callbacks/packet serialization and EMOS receiver. Adapt
the historical browser event/focus handling selectively; do not restore its
network service or BrowserKeyboard owner class. The latter still reproduces the
false-expiry defect. The current host-input owner has already corrected that
timer arithmetic, but its automation pacing and no-repeat policy are not a
complete interactive keyboard contract.

This completes B01's source review only. Transport, competing input ownership,
repeat and mapping decisions remain under B02/B03 in the parent task. No product
source, installed firmware, SD content or emulator was changed for this review.

## Inspected sources and bounds

1. Extender baseline: `1572250003ea84919648e0cf410d0b6bdf5f9c9f`.
   Historical browser candidate: `1ce96dc97177c9818fe9254ad5a5500ffd6142c9`.
   Historical files can be inspected with `git show <commit>:<path>`; their
   retired build composition is not a deployment starting point.
2. EMOS baseline: `26ba8776bc147e262cd45dc808d5869740b1396e` in the sibling
   project. Inspected `src/emos.c` (`emos_keyinput_command`) and
   `src/emos_keyboard.c` (`emos_keyboard_select` and source admission).
3. Official documentation reviewed first: `docs/vdp/System-Commands.md` at
   agon-docs `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, specifically locale
   `23,0,&81`, keyboard control `23,0,&88`, VDP Protocol and Keyboard packet data.
   MOS owns received sysvars; keyboard packets carry keycode, modifiers, virtual
   key and down/up. Repeat delay/rate are keyboard settings, not browser video
   timing. The project mapper supports fewer locales than stock documentation.
4. Read-only reference checkouts remain clean at their latest locally available
   official release tags: MOS v3.0.2
   `8336409351ee5314e02801a7b72a4f1bb5282519`; VDP v2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. VDP
   `video/vdu_stream_processor.h` supplies the retained keyboard callback and
   packet construction pattern. This review did not fetch new upstream tags.
5. The installed candidate remains the experimental build recorded in
   [BENCH-006/BUILD.json](../BENCH-006/BUILD.json). Its preserved source overlay
   and rollback are identified in the ignored handoff/agent records. Local
   comparison found the console integration identical to maintained source, but
   the network service has additional codec routes and encoding logic. A plain
   HEAD build cannot be assumed to preserve installed video behaviour. No live
   connection was opened to inspect the bench.

## Reuse and replacement map

| Area | Evidence | Disposition |
|---|---|---|
| Browser key acquisition | Historical `vdp/video/extender/web/app.js`, `physicalKey` and `forwardKey` | Reuse the physical-code-to-HID-usage approach, focused-canvas event listeners and no-local-echo rule. Expand the reviewed map; do not paste the old US sample policy wholesale. |
| Capture UI | Historical `releaseKeyboard`, button handler and blur/visibility listeners | Reuse lifecycle concepts. Replace the take-control-only button and automatic canvas-click capture with the accepted explicit capture/release toggle and fresh admission requirement. |
| Old input transport | Historical `wired_network_service.cpp`, `keyboardPostHandshake` and `keyboardHandler` | Useful protocol/dispatch evidence, not a network rollback. It already used a separate `/keyboard` WebSocket, but shared the HTTP task with video. |
| Old owner class | [browser_keyboard.hpp](../../../vdp/video/extender/input/browser_keyboard.hpp) | Retained evidence only. Unsigned stale-time expiry is still present; it also lacks current physical/host arbitration. |
| Current remote owner | [remote_keyboard.hpp](../../../vdp/video/extender/input/remote_keyboard.hpp), [remote_target.hpp](../../../vdp/video/extender/input/remote_target.hpp) | Reuse epoch/session invalidation, validated bounded input, idempotent retries, signed modular lease comparison and source-specific cleanup. Browser-facing admission and interactive policy require explicit adaptation. |
| Layout and virtual keys | [usb_cli_keyboard.hpp](../../../vdp/video/extender/input/usb_cli_keyboard.hpp), [hid_key_mapping.hpp](../../../vdp/video/extender/input/hid_key_mapping.hpp) | Use the current mapper: UK/US, correct stock Backspace/arrows, function and editing keys. Retain down-time key identity for key-up. |
| Console integration | [console_hardware.inc](../../../vdp/video/extender/transport/console_hardware.inc), `runConsole` | Only the P4 console owner emits input. Join beside the existing remote `take` path; never pass browser events through the physical `emit` callback, which invokes physical takeover/cancellation. |
| Stock effects and wire | [processed_keyboard.hpp](../../../vdp/video/extender/input/processed_keyboard.hpp), [unavailable_input_adapter.hpp](../../../vdp/video/extender/input/unavailable_input_adapter.hpp), [vdu_stream_processor.h](../../../vdp/video/vdu_stream_processor.h) | Retain ordered callbacks, VDP variable effects and serializer. Do not construct replacement UART packets in HTTP or JavaScript. |
| EMOS admission | Sibling `emos_keyboard_select` | No receiver or wire change indicated. Keeping `EMOS KEYINPUT extender` and arbitrating browser/USB/host providers on P4 is the minimal proposal. The historical `browser` selector is a distinct EMOS state, not an automatic provider switch; changing between remote selectors currently requires mainboard in between. B02 must settle the public meaning before implementation. |

## Findings that bound the next work

1. **The old expiry bug is concrete, not a speculative Ethernet failure.**
   A heartbeat at time 100 followed by `expire(99)` revokes the old browser
   owner. Current RemoteKeyboard uses signed modular elapsed time and has a
   passing regression for this exact task ordering plus timer wrap. Preserve
   these semantics; increasing a timeout does not repair unsigned underflow.
   Historical physical correlation and the separate video-send failures remain
   in the parent task's September 9 findings, not a new performance claim.
2. **Separate socket is not separate execution.** Old browser input already
   used `/keyboard`; its page nevertheless required an open `/video` connection
   and released input when video closed. Both endpoints shared HTTP execution.
   The new adapter must distinguish input loss from video viewing policy, and
   verify admission/renewal progress under current compressed-video load. Merely
   selecting another URL does not solve shared-task stalls.
3. **The host controller is deliberately slower and stricter than an ordinary
   keyboard.** It emits at most one submitted transition per 20 ms, preserves
   spacing between batches, rejects duplicate down events and generates no
   remote typematic. That is at most 50 transitions/s, or 25 simple down/up
   character pairs/s before modifiers and other overhead. The browser cannot
   forward its historical repeated key-downs unchanged. Keep these automation
   guarantees while defining an interactive policy separately.
4. **The old mapping would regress useful keys.** Its DOM table omitted arrows,
   F keys and UK-specific positions; Tab, Alt and Meta caused release. The current
   mapper covers UK/US arrows/editing/F keys, but the host controller rejects
   Caps Lock and supports only six ordinary held keys. Keypad, other locales,
   composition and browser/OS-reserved shortcuts need a visible bounded policy.
   The user's current Mac/browser keyboard is part of acceptance, not something
   proven by old Chromium US-layout tests.
5. **Ownership is not additive.** Current physical USB presses cancel host
   automation; new sessions require physical neutrality. Cancellation drops
   unsent events and releases remote ordinary keys before modifiers. The old
   browser class released modifiers first and blindly took a new socket owner.
   Do not run two independent owners into the shared EMOS held-key map: one
   source's key-up could clear another source's held key. B02 must define browser
   versus agent ownership while preserving physical input and cleanup ordering.
6. **Preserve installed output and observation.** New input must retain the
   candidate's codecs/fullscreen assets and `/screen/text`, without opening a
   competing video viewer. Keep manifests/rollback intact and compare candidate
   overlay as well as tracked source before a future build. No fresh full P4
   build or hardware readiness is claimed by this review.

## Checks performed and test reuse

All four existing host checks passed from the baseline using the local Python
environment. C++ checks used their existing address/undefined-behaviour sanitizers:

| Check | Scope |
|---|---|
| `tests/test_remote_keyboard.py` | Bounded batches, mapping, duplicate requests, physical takeover, cancellation, admission, lease timing and wrap. |
| `tests/usb_cli_keyboard_test.py` | UK/US mapping, editing keys, repeat, neutral admission, loss and reserved queue cleanup. |
| `tests/browser_keyboard_test.py` | Historical mapping/session behaviours and pinned virtual-key values. Passing does not prove the absence of the stale-time defect. |
| `tests/processed_keyboard_test.py` | Actual retained callback/serializer method bodies and FIFO, with platform/context fakes. |

A temporary native probe against the retained BrowserKeyboard additionally
reproduced the old defect: `ready(true); take(1,0); heartbeat(1,100); expire(99);`
then `heartbeat(1,100)` returns false. The existing RemoteKeyboard regression
accepts a renewal at 100 followed by `tick(99)` and expires only at its true
deadline. No product fix or new firmware build was made.

Historical `tests/browser_keyboard_ui_test.py` at `1ce96dc` is useful for actual
DOM focus, key conversion, blur, Tab and stalled acknowledgements, but its fake
socket and old US-policy assertions must be adapted to the selected new contract.
Historical `tests/browser_keyboard_dispatch_test.py` explains the IDF handshake
initialization defect: session context belongs in the post-handshake callback,
not a GET handler skipped by that dispatch. It is tied to the selected IDF and
retired service methods, so it is not a current integration pass. Extend current
tests for host/browser contention, held-key handover, stale sessions, lease
interleaving, repeat and fullscreen/reconnect behaviour under B05.

## Recommended next decision

B02 should first choose a browser-specific input endpoint, with its own session
and explicit admission, rather than mixing key messages into the video protocol.
A separate WebSocket is a reasonable candidate for persistent interactive events;
it still needs measured service progress and ownership independent of the video
socket. A browser-facing HTTP adapter is an alternative that reuses more host
request machinery. Neither means removing the host endpoint's Origin rejection.
This is a recommendation awaiting review, not an accepted transport decision.
