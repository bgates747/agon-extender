# QUAL-004 — Whole-image graphics correctness on physical VDP and P4

## Current acceptance summary

Retained coverage is **77 paired static scenes / 14,410,752 pixels** through
[packed expansion BM02](QUAL-004/packed-expansion/RESULTS.md).
[Extender sprite/scroll checks](QUAL-004/sprite-scroll/extender-followup/RESULTS.md)
passed all four checkpoints, with exact mainboard comparison for three;
INITIAL has a stock visual control, not a mainboard captured reference.
The earlier diagnostic panic remains [FWBUG-002](../firmware-bugs.md#fwbug-002),
with QUAL-004-CI01 deferred. BM03 and four Copper controls also remain deferred.
These are bounded image checks, not complete dynamic parity or performance
qualification. Earlier totals and installed-state statements below are dated
execution history; use this summary and TODO for current disposition.


## Executive summary

Author-authorized unattended correctness qualification, bounded to eight hours
from 2026-09-16 12:11:20 UTC (deadline 20:11:20 UTC). Bench release explicitly
confirmed by the Author. No audio or emulator notification. Mainboard hardware
is the compatibility oracle; emulator references are supplementary. Existing
39-case probe results are evidence of selected checks, not whole-image parity.
Rendering timing is secondary; no streaming-performance optimisation or Golem.
Author clarification: mark missing API functionality **not implemented**; do not
implement it in this run. Defer implementation to a separately authorised second
pass. Capture/test instrumentation is permitted and is not API implementation.

## Frozen execution contract

1. [x] Inventory reusable corpus, capture hooks, firmware identities and recovery.
   Pin official VDP v2.16.0 and applicable source/docs. Preserve current installed
   firmware/startup before changes; do not assume the Mac agent left old state.
2. [x] Implement task-local full-image acquisition and comparison. Capture after
   queue completion at a stable checkpoint; serial transfer is outside timing.
   Record dimensions, colour interpretation, palette, display/drawing page,
   sprite composition and integrity checks. Reject incomplete or mixed frames.
   Prefer existing stock pixel semantics and capture paths over new rendering.
3. [x] Validate capture against simple known patterns and selected pixel queries;
   negative controls must detect changed pixels, missing rows and corrupt data.
   Freeze candidate inputs before evidence-producing builds/runs. Official
   upstream checkouts remain read-only. Diagnostic firmware changes stay here.
4. [x] Run bounded coverage of primitives, clipping/viewports/origins, scrolling,
   colours/palettes, bitmap formats/transforms, fonts/text, contexts, buffered
   execution, software/hardware sprites and supported double-buffered modes.
   Reuse existing corpus first. Publish a coverage matrix: tested, unsupported,
   deferred, failed. Do not replace missing coverage with a blanket pass.
5. [x] Compare canonical logical colours for every captured pixel on both physical
   devices. Retain actual images and difference images, mismatch counts/bounds,
   commands, seeds, identities and durations. Diagnose mismatches with focused
   repeats; distinguish stock-shared defects from port regressions. No broad
   product fixes in this qualification chunk. Emulator-only success cannot
   substitute for mainboard hardware evidence.
6. [x] Restore verified pre-run firmware/startup and usable Legacy CLI. Publish
   executive summary, case table, secondary timing scopes, unresolved issues and
   next actions. Commit owned discrete work; no experimental push or alerts.

## Gates and budget

Eight hours is a maximum, not a target. Reserve the final hour for restoration
and reporting. Stop adding coverage when that reserve begins. Record wall time
for setup/run/retrieval separately. Keep temporary diagnostics out of production
applications; use /test paths. Do not change MOS firmware. Serial opening may
reset a device: use established stable identities and recovery procedures.
Hardware sprites may be composed during scanout; a background-only dump cannot
qualify sprite correctness. Record this as a coverage gap unless complete
composition is acquired faithfully. No frame-rate requirement for extraction.

## Decisions and scope changes

Self-assigned coverage refinement within the frozen scope: after the existing
63-scene cohort, reuse PORT-008's literal palette cases in modes9/10/11 and
add a small mode136 displayed/drawing-page control, if acquisition remains
healthy. These require the already-built all-depth diagnostic tap, not renderer
changes. Mode selection remains in startup. Cross-check calibration with the
ordinary stock pixel-query API. Do not defer restoration to chase extra coverage.

Author authorizes diagnostic flashing/testing through this request and previous
bench permissions; release reconfirmed this turn. Any newly necessary experiment
must be labelled self-assigned and documented before execution. Human validation
is required for emulator changes before those changes are committed. No such
changes are required for the primary hardware comparison.

Self-assigned acquisition response: the first fenced cohort stopped on a stock
scanout null-pointer crash while repeating BSP21_01. Permit normal mainboard
reset/startup isolation before each remaining replay; this changes test setup,
not graphics functionality. Keep the failed live-replay result and exclude live
sprite teardown from any passing claim. Do not repair the suspected stock race.

Static Copper coverage uses the existing PORT-008 literal oracle: setup/edit/
replace/reset at16 colours, setup at4 and2 colours. These six additional small
scenes accompany palette controls under the all-depth tap. Restart-isolate each
mainboard replay because Copper includes both software and hardware sprites.
This is the original graphics-coverage scope, not an implementation expansion.

Self-assigned bounded acquisition handling: the same stock scanout null-pointer
crash recurred during BSP26_01. For that exact known signature only, allow one
fresh-start retry per case, retain both attempts, and leave a twice-failed case
unqualified while continuing independent cases. Unknown failures still stop.
This is test orchestration, not a stock/P4 fix or permission to erase failures.
Use the unchanged committed per-case image procedure with fresh startup isolation.

Self-assigned bounded P4 setup response: after COP16_SETUP passed, P4 restarted
while the next mainboard boot re-selected P4 mode9; HTTP timed out and its keyboard
boot identity changed. No COP16_EDIT image was acquired. Cause is unproven. Retain
that mode-transition failure; do not qualify mode changes with active Copper.
For the remaining static Copper pairs, use ordinary Copper reset and sprite
cleanup after the P4 capture, before the next startup/mode selection. This is
fixture teardown only, not a firmware correction. Stop on another unexplained
restart; restore the original bench rather than chase implementation changes.

## First-pass closeout

Bounded run complete, awaiting Author review.66 static scene pairs match all
12,616,704 pixels. Reliability gate stopped eight prepared controls after the
second P4 mode-setup restart. Three mainboard diagnostic-build scanout crashes
and the unfenced alpha instability remain retained findings. No rendering fixes
or missing API implementations. Exact original mainboard app/startup restored;
P4/MOS unchanged, Legacy CLI usable, serial reader closed, no alerts.

Results and second-pass candidates: [RESULTS.md](QUAL-004/RESULTS.md).
Coverage and explicit **not implemented** entries: [COVERAGE.md](QUAL-004/COVERAGE.md).
Checkboxes indicate completion of the bounded qualification procedure, not blanket
API acceptance. Second-pass implementation and unresolved investigations are not
started by closing this run.

## Author review disposition — 2026-09-16

Author describes this first pass as overwhelmingly successful. Keep QUAL-004
open pending review of the exceptions; completion of the bounded execution goal
is not closure or blanket graphics acceptance. Review the three mainboard
scanout crashes, two P4 transition restarts, original unfenced instability and
remaining coverage before disposition. Missing implementations stay deferred.

## Firmware bug register cross-reference — 2026-09-20

[FWBUG-001](../firmware-bugs.md#fwbug-001--palette-deletion-advances-an-erased-map-iterator), [FWBUG-002](../firmware-bugs.md#fwbug-002). These stable bug identities supplement the original
finding IDs and evidence. Registration does not authorize repairs or turn
source-only findings into hardware reproductions. Use the same FWBUG ID for
any future dedicated disposal task; current dispositions remain in the register.

## Displayed-page follow-up — 2026-09-20

[Two frozen page controls](QUAL-004/page-controls/RESULTS.md) passed on physical
mainboard and P4: 153,600 pixels, zero differences, independent literal oracles
and repeat captures all equal. Cumulative static coverage is 68 scenes /
12,770,304 pixels across the identified campaigns. Six prepared controls remain
unqualified; earlier crashes remain open. Mainboard firmware/startup restored;
P4 and EMOS unchanged.

## Plain low-depth follow-up — 2026-09-20

[PAL4 and PAL2](QUAL-004/low-depth/RESULTS.md) passed complete physical image
comparison and independent literal oracles. Another 153,600 pixels match;
cumulative coverage is 70 scenes / 12,923,904 pixels. Four prepared Copper
controls and prior defects remain open. Original startup/mainboard firmware
restored; P4/EMOS unchanged.

## Static Mode7 follow-up — 2026-09-20

[TTSTATIC](QUAL-004/teletext/RESULTS.md) matches all 307,200 pixels between
mainboard and Extender. Static text/colours, mosaics and double-height examples
pass; dynamic teletext remains unqualified. Cumulative 71 scenes / 13,231,104
pixels. Four Copper controls and prior defects remain open. Original bench
restored and verified; no product firmware change.

## Sprite/scroll follow-up — stopped on mainboard failure

[Four-checkpoint qualification](QUAL-004/sprite-scroll/RESULTS.md) stopped on
SS_INITIAL before capture: mainboard LoadProhibited/address0x1c at stock
drawSpriteScanLine. Same retained FWBUG-002 signature; exact setup trigger and
diagnostic influence unresolved. No checkpoint passed; no P4 scene executed.
Existing coverage remains 71 scenes. Original bench restored and verified.

### Diagnostic-free sprite control

Published stock v2.16.0 did not panic during the Author-authorized single
30-second SS_INITIAL control, and accepted Escape/CLI afterward. See
[specific evidence and limits](QUAL-004/sprite-scroll/stock-control/RESULTS.md).
Sprite qualification stays blocked; investigate diagnostic influence before
asserting a stock-independent upstream crash. Bench restored; no renderer fix.

## Current capture failure protocol — 2026-09-20

Author supersedes earlier stop-on-failure/immediate-retry orchestration with the
[capture failure protocol](../qualification/capture-failure-protocol.md).
Continue independent cases after recording/recovering each capture failure;
after the suite, replay marked cases on official stock mainboard VDP or matching
EDP without capture instrumentation. Preserve both outcomes; no missing image
becomes a pass. Existing deferred Copper scope and historical results stand.

## Deferred capture-interference investigation — Author decision 2026-09-20

**QUAL-004-CI01** [ ] Deferred for token budget: investigate whether the mainboard
capture diagnostic causes or exposes sprite failures through instrumentation,
binary layout, timing or startup history. Retain FWBUG-002 and the
[stock control/visual evidence](QUAL-004/sprite-scroll/stock-control/RESULTS.md).
Do not assert proven diagnostic causation from one clean stock control. When
resumed, match startup history and fixture bytes, compare instrumented and
uninstrumented builds, and isolate the smallest relevant diagnostic change
before proposing a fix. Apply the equivalent capture-free comparison on EDP
only for failures actually observed there. No implementation authorized now.

Next bounded qualification work remains the outstanding sprite/scroll cases:
OVERLAP, EDGES and HIDDEN, plus P4 INITIAL which has not run. Apply the new
mark/recover/continue protocol; collect capture-free controls for failed cases
after the suite. Keep Copper and diagnostic repair deferred. Missing captures
remain unqualified even if a human visual control passes.

## Mainboard-only sprite continuation — results

Author-requested OVERLAP, EDGES and HIDDEN each captured twice with identical
pixels; all six attempts exited and accepted CLI commands. HIDDEN matches its
independent196608-pixel background oracle exactly. No failure-triggered stock
control required for this batch. [Evidence and limits](QUAL-004/sprite-scroll/mainboard-followup/RESULTS.md).
P4 remains deferred; paired total stays71. Earlier INITIAL panic remains open.

## Extender sprite continuation — passed within scope

[All four Extender checks](QUAL-004/sprite-scroll/extender-followup/RESULTS.md)
completed with stable frames and clean input/CLI return. OVERLAP/EDGES/HIDDEN
match all589824mainboard pixels; HIDDEN also matches its independent full oracle.
INITIAL lacks a mainboard capture and is not counted as paired parity. Cumulative
74paired scenes/13820928pixels; prior diagnostic failure remains deferred.

## Bitmap coverage inventory and bounded comparison

[Format/conversion map](QUAL-004/bitmap-coverage/REVIEW.md) finds existing evidence
for every public format and pre-existing packed-expansion/baked-transform fixtures.
Recommendation is a bounded exact comparison of existing packed-expansion cases,
not another basic-format smoke. Author subsequently authorized BM02 execution.

BM02 [passed](QUAL-004/packed-expansion/RESULTS.md): 1/2/4bpp packed expansion,
589824 exact paired pixels and independent oracles, after correcting fixture
buffer isolation. Cumulative77paired scenes /14410752pixels. BM03 remains deferred.
