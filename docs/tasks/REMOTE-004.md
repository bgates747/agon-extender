# REMOTE-004 — Clipboard copy/paste feasibility

## Executive summary

Low-priority, unscheduled investigation requested by the Author on 2026-09-20.
Investigate Extender-specific copy/paste first, then whether a useful subset
could support stock MOS/VDP. No implementation or hardware work authorized.
Existing keyboard transport and ExCom text readback may supply much of the
mechanism; application consumption, not transport speed, determines paste
reliability. Return a bounded proposal for Author review before coding.

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
