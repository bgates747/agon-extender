# QUAL-004 — Whole-image graphics correctness on physical VDP and P4

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
4. [ ] Run bounded coverage of primitives, clipping/viewports/origins, scrolling,
   colours/palettes, bitmap formats/transforms, fonts/text, contexts, buffered
   execution, software/hardware sprites and supported double-buffered modes.
   Reuse existing corpus first. Publish a coverage matrix: tested, unsupported,
   deferred, failed. Do not replace missing coverage with a blanket pass.
5. [ ] Compare canonical logical colours for every captured pixel on both physical
   devices. Retain actual images and difference images, mismatch counts/bounds,
   commands, seeds, identities and durations. Diagnose mismatches with focused
   repeats; distinguish stock-shared defects from port regressions. No broad
   product fixes in this qualification chunk. Emulator-only success cannot
   substitute for mainboard hardware evidence.
6. [ ] Restore verified pre-run firmware/startup and usable Legacy CLI. Publish
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
