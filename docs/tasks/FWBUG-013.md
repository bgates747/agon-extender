# FWBUG-013 — ExCom prompt cursor stops flashing at column zero

## Executive summary

At an EMOS command prompt in ExCom mode, the active text cursor does not flash
when it is initially on the first character position of an empty line. Typing
one character advances the cursor and starts flashing. Backspacing to the first
position stops flashing again, but using the left arrow to return to that same
position does not stop flashing.

The same screen coordinate therefore has different visible behavior depending
on how EMOS moved the cursor there. Preserve that asymmetry as the principal
diagnostic clue; do not classify this as a simple column-zero clipping defect
without evidence.

Created: 2026-09-29. Register identity: [FWBUG-013](../firmware-bugs.md#fwbug-013).
Related current audit: [AUDIT-010](AUDIT-010.md). Owning queue: `TODO.md`.

## State and evidence

F13-S01 — **Open; Author-reported physical observation.** The Author observed
the symptom at a MOS prompt while operating in ExCom on 2026-09-29. No agent
capture, source diagnosis, Legacy comparison or exact-build reconciliation has
yet been completed.

F13-S02 — Filing this report authorizes no build, deployment, reset, fixture
run, source repair or production promotion. Schedule investigation consistently
with the active AUDIT-010 review/repair gate.

F13-S03 — The report does not yet distinguish the physical Extender display
from browser replication or another P4 output surface. A later reproducer must
name every observed output rather than treating one as proof for all outputs.

## Reported reproduction

F13-R01 [ ] Boot the currently selected EMOS and EDP combination, enter ExCom,
and reach an ordinary EMOS command prompt with an empty input line.

F13-R02 [ ] Observe the cursor at the first character position, column zero.
Reported result: the cursor is visible but does not flash.

F13-R03 [ ] Type any ordinary character. Reported result: EMOS advances the
cursor and the cursor begins flashing.

F13-R04 [ ] Press Backspace so EMOS returns the cursor to column zero. Reported
result: the cursor stops flashing.

F13-R05 [ ] Type a character again, then press the left-arrow key so EMOS moves
the cursor to column zero without deleting the character. Reported result: the
cursor continues flashing.

F13-R06 [ ] Repeat the sequence after enough flash periods to distinguish a
stopped cursor from a phase reset or delayed first toggle. Record timing and
whether the cursor is persistently shown or hidden while stopped.

## Expected behavior

F13-E01 — At an active EMOS prompt, the text cursor flashes at every valid text
position, including column zero, unless EMOS or the VDP protocol explicitly
disables cursor flashing.

F13-E02 — Backspace and cursor-left may change text contents differently, but
arriving at the same active cursor position must not accidentally select
different flash behavior.

## Investigation items

F13-01 [ ] Reconcile the exact installed EMOS and EDP build identities from the
current deployment evidence before attributing the observation to production,
the audited pre-LCD baseline or another development build.

F13-02 [ ] Review the official MOS/VDP cursor and text-editing contracts in
`../../agon-docs`, then consult the read-only official MOS/VDP source only where
implementation detail is material. Record exact reference tags and commits.

F13-03 [ ] Reproduce the four states—initial column zero, typed column one,
backspace to column zero and left-arrow to column zero—on Legacy and ExCom.
Observe the physical output and browser output separately where applicable.

F13-04 [ ] Capture the forward VDU traffic and applicable reverse/input events
for each transition. Determine whether EMOS sends different cursor visibility,
flash, position or redraw commands for Backspace and left-arrow paths.

F13-05 [ ] If the command streams are equivalent, trace EDP cursor state,
flash-timer state, cursor bitmap/sprite visibility, text invalidation and frame
publication at column zero. If they differ, assign the producer-side behavior
to EMOS before altering EDP rendering.

F13-06 [ ] Construct the smallest deterministic fixture that distinguishes
coordinate from transition history. Follow the current rule that `/autoexec.txt`
selects the fixture video mode; the fixture must not switch modes itself.

F13-07 [ ] Complete AUDIT-010 review and then place any correction in its
itemized repair plan. Retest ordinary prompt editing, all screen edges, cursor
enable/disable, cursor shape, browser replication and existing text fixtures.

## Validation gates

F13-G01 [ ] Exact EMOS/EDP identities and output surfaces are recorded.

F13-G02 [ ] A retained reproduction distinguishes initial placement,
Backspace-to-zero and arrow-to-zero, including flash timing.

F13-G03 [ ] Evidence identifies whether EMOS command production, EDP command
consumption, cursor timing or output publication owns the defect.

F13-G04 [ ] The repaired cursor flashes at column zero after all three arrival
paths and retains correct behavior elsewhere.

F13-G05 [ ] Legacy behavior and existing text/cursor regressions remain intact;
no LCD, browser or other output is declared fixed without direct evidence.

## Non-goals

F13-N01 — This report does not redesign the cursor, change flash cadence, merge
Legacy and ExCom rendering, or infer that all column-zero cursor behavior is
broken.

F13-N02 — Do not mask the symptom by forcing a redraw or restarting the flash
timer on every input event until the responsible contract and actor are known.
