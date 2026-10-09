# REMOTE-004 — Clipboard copy/paste feasibility

## Executive summary

Browser paste and the restored Reset Agon button were implemented, deployed
and accepted by the Author on 2026-10-09. The browser sends locale-aware balanced
key packets at adjustable cadence through the existing P4 capture owner.
Acknowledgement confirms P4 acceptance, not application consumption.
Broader clipboard research remains deferred. Remaining validation and production
promotion belong to the existing HDMI qualification/release boundary; the scoped
paste/reset acceptance does not certify a complete firmware release.

## Scope and dependencies

The browser host owns the clipboard and requests copy/paste explicitly. For
Extender paste, evaluate browser-to-P4 Ethernet input followed by P4-to-EMOS
keyboard packets over the existing UART wiring. EMOS retains routing and input
ownership. Preserve capture, physical-keyboard takeover and locale behavior from
[REMOTE-001](REMOTE-001.md); reuse [PORT-005](PORT-005.md) keyboard semantics.

For copy, first inspect the existing P4 `GET /screen/text` facility from
the [screen-text guide](../screen-text.md), with evidence under
[BENCH-006](BENCH-006.md). It uses retained VDP glyph recognition, not an
independent text buffer: font/colour, unknown-glyph, graphics and non-atomic
capture limitations matter. A new transcript is an alternative to investigate,
not an already selected requirement. Stock/Legacy readback remains separate.

The motivating conversation with the emulator developer reports that polling
keyboard APIs can overwrite unconsumed events, whereas applications using
`mos_setkbvector` can capture arrivals. Treat this as a research lead. Registering
a callback does not itself create an unlimited queue or guarantee arbitrary-rate
paste; measure buffering and consumption for each proposed supported path.

## Investigation work

**REMOTE-004-I01** [ ] Review official MOS keyboard and VDP text-readback
contracts, then relevant source. Map callback, polled input and CLI line-editor
consumption. Distinguish packet receipt from application acceptance and identify
what acknowledgement, if any, can safely represent consumption.

**REMOTE-004-I02** [ ] Assess Extender paste through the existing P4 keyboard
owner. Compare bounded, cancellable best-effort event injection with reliable
EMOS CLI/editor integration. Cover press/release ordering, input takeover,
held-key cleanup, modifiers/locks, locale/Unicode mapping, newline conversion,
unsupported characters, multiline command execution and disconnect recovery.
Do not claim a fixed delay guarantees delivery to arbitrary applications.

**REMOTE-004-I03** [ ] Assess browser copy using existing ExCom text readback
before proposing new text retention. Compare visible-screen extraction, selected
regions and console transcripts; distinguish text from pixels, font recognition
from original characters, and current display from historical output. Identify
host clipboard permissions and explicit user gestures required when implemented.

**REMOTE-004-I04** [ ] Assess a later stock MOS/VDP-compatible subset. Distinguish
unmodified stock firmware with a helper/application or emulator host integration
from changes requiring upstream firmware support. Name each sender, receiver,
transport and consumer. No assumption that stock hardware has Extender Ethernet
access; no edits to read-only upstream references.

**REMOTE-004-I05** [ ] Present feasibility, compatibility and cost side by side;
recommend the smallest useful first tranche and its tests. Propose tests for
callback and polling applications, CLI editing, long/multiline paste,
cancellation, ownership changes and copy fidelity. Stop for Author review.

## Open decisions

**REMOTE-004-D01** [ ] Select initial paste guarantee and supported consumers:
best-effort arbitrary applications, reliable CLI/editor, or a bounded combination.

**REMOTE-004-D02** [ ] Select initial copy semantics after reviewing existing
readback: visible text, selection, transcript, or a bounded combination.

**REMOTE-004-D03** [ ] Decide whether stock compatibility merits a follow-up and
whether it requires helper software, emulator integration or firmware changes.

No architectural option is accepted by recording this task. It does not change
the current audit/porting priority, reopen browser-performance work, or authorize
new firmware identities, flashing, emulator changes or upstream publication.

## Authorized first browser paste tranche — 2026-10-08

The Author now requests a browser paste window issuing paced key packets.
This authorizes the bounded implementation below; it supersedes the original
no-code gate for this slice only. Copy/readback, reliable consumer acknowledgements
and stock-only compatibility remain investigations. No bench operation, firmware
installation, production promotion or automatic publication is authorized.

REMOTE-004-P01 [x] — Add a compact Paste text dialog to the existing video/input
panel. The browser operator supplies text through normal OS paste, chooses
character cadence and Enter pause, and explicitly starts/stops sending. No
clipboard API permission or hidden automatic execution on paste. Normalize
CRLF/CR to one Enter each, support current UK/US printable mappings and tabs,
validate the whole bounded text before emitting events, and preserve known host
Caps Lock semantics. If Caps is unknown for letters, request a host key observation
in the text box rather than inventing a lock state.

REMOTE-004-P02 [x] — Reuse the admitted browser WebSocket, capture arbitration,
stock mapper and P4 console serializer. Send ordered balanced modifier/key
transitions at least 20 ms apart, wait for each P4 acknowledgement, never catch
up in a burst, and pause after Enter. P4 acknowledgement means queue acceptance,
not MOS consumption. Default 80 ms per character and 500 ms after Enter; allow
slower settings. Stop on focus/visibility/input loss, physical takeover, reset,
dialog closure or explicit stop. Do not replay an uncertain fragment or change
ordinary human/host-agent pacing. Video connection remains independent.

REMOTE-004-P03 [ ] — Exercise actual browser code against a local acknowledging
peer: both layouts/caps states, punctuation and newline conversion, prevalidation,
cadence, cancellation, missing/stale acknowledgements and existing capture/layout
behavior. Compare generated text with the existing Python mapper and retained
P4 mapping tests. Record results and handbook usage as candidate-only; pause for
review/deployment authorization. No hardware, emulator or firmware flash.

Research baseline: agon-docs `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
[keyboard methods](../../../../agon-docs/docs/mos/Keyboard.md),
[MOS API](../../../../agon-docs/docs/mos/API.md) mos_getkey/mos_setkbvector;
stock MOS v3.0.2 keyboard/sysvar handling and the existing BrowserCapture owner
confirm there is no application-consumption acknowledgement. Reuse
scripts/keyboard.py text_events and the current browser input handler's echoed
sequence/generation acknowledgement; no replacement UART serializer.

### Local implementation result

Browser source and the candidate operating notes are implemented.
`tests/browser_paste_ui_test.py` executes the actual page in local Chromium
against a mock P4 and compares its packets with `scripts/keyboard.py`. UK/US
mapping, host Caps Lock, punctuation, line breaks/tab, minimum transition
spacing, whole-text rejection, cancellation, focus loss, missing-event ACK and
admission timeout checks passed. Existing browser capture/fullscreen regression
checks also passed. No P4 connection, flash or bench operation was performed.

P03 remains open for final review and hardware deployment when the Author
releases the bench. This is candidate source, not a production claim.

### Authorized review deployment — 2026-10-09

The Author released the bench for flashing. A frozen copy of the tested
full HDMI r11 source received exactly three browser-file changes; current
parallel-transport development was excluded. New candidate
`rgb-001-r12-b2026-10-09-04-59-03Z` compiled and passed native validation.
Only the application slot was flashed and independently verified; retained
bootloader/partitions were verified and OTA metadata preserved. Served app.js
matched the tested source. A normal Agon reset restored Extender input.

A real browser submitted a harmless echo command through the new paste UI,
received every P4 acknowledgement and completed without JavaScript errors.
No independent MOS text readback or application-consumption guarantee is claimed.
The candidate remains installed for Author review; EMOS, mainboard VDP and
SD contents were not changed. Exact receipts and rollback references reside
in ignored `agents/browser-paste/deployment/`. P03 human review remains open.

### Browser reset restoration

Author accepted paste behavior and requested the missing reset control restored.
The retained HDMI baseline omitted reset endpoint configuration; its existing Pi
bridge also lacked the current P4 origin. Both local deployment settings were
corrected. The same frozen firmware source was rebuilt, application-only flashed
and independently verified. The actual browser button returned HTTP200/released,
and a fresh EMOS boot with admitted neutral input was verified. No EMOS, mainboard
VDP or SD changes. Exact candidate is recorded in the machine-local handback.
Paste acceptance is retained; production promotion remains within the existing
HDMI qualification/release boundary, not claimed complete by this scoped smoke.

### Author acceptance and publication

The Author reported paste success and independently confirmed the repaired
Reset Agon button, then authorized logical commits and publication. Accepted
source and routine usage live in the maintained web client and keyboard guide;
frozen machine-local deployment receipts remain unchanged. The existing
production selection is unchanged. P03 retains its broader unperformed checks;
no universal delivery, every-browser, or full-firmware qualification is claimed.
