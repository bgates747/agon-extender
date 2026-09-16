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
3. [ ] Validate capture against simple known patterns and selected pixel queries;
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

Author authorizes diagnostic flashing/testing through this request and previous
bench permissions; release reconfirmed this turn. Any newly necessary experiment
must be labelled self-assigned and documented before execution. Human validation
is required for emulator changes before those changes are committed. No such
changes are required for the primary hardware comparison.
