# PORT-008 — Historical receiver build-environment comparison

## Executive summary

The GPIO-only reproduction of the formerly working PRX-06 receiver fails on
P4-PC. Source equality does not establish equality of SDK, toolchain, silicon,
configuration or DMA/cache behavior. Author approves a bounded offline comparison
of those differences before any further physical experiment. The existing header
cannot accommodate the proposed additional probe connection; no probe move is
part of this work.

BC01 [x] — Freeze the contract and existing work in logical commits before
research. Preserve unrelated component work and all retained hardware evidence.
Commit records are safety checkpoints, not release or hardware qualification.

BC02 [x] — Recover the actual historical SDK/compiler/configuration and silicon
identities from retained manifests, binaries, build logs and boot output. Compare
with the exact failed reproduction. Mark absent evidence unknown; do not infer
an original SDK from today's legacy checkout or a requested package version.
Record file/commit/hash provenance and distinguish configured from observed values.

BC03 [x] — Compare the pinned PARLIO/GDMA/cache implementations and generated
settings relevant to RX sample qualification, DMA buffer alignment/visibility,
EOF/length accounting, interrupts and chip-revision workarounds. Read local
vendor sources and supplied documentation first; use primary vendor sources if
local evidence is insufficient. Keep source review and measured hardware facts
separate. No firmware edits, rebuild experiment, flash, reset or rewiring.

BC04 [x] — Record a side-by-side comparison, rank concrete explanatory differences
and propose the smallest next discriminating check. Update the parent task,
current handoff and development log. Stop for discussion before a new bench
experiment. If the original environment cannot be reconstructed, state exactly
what remains unknown and what evidence would resolve it.

## Evidence and dependencies

1. [Historical reproduction](DEVKIT-CONTROL-R01.md): first slow1024-byte record
fails; exactly1024 source clocks and five observed source data bits match.
2. [Original forward prototype provenance](FORWARD-PROTOTYPE-REUSE.md) pins the
successful retained legacy run and original receiver/source hashes.
3. [Received-buffer snapshot](DATA-SNAPSHOT-R01.md) records separate current-pair
RX and reverse-output failures; do not collapse these into one proven cause.
4. Ignored local `agents/port008-live-qualification/devkit-control-r01` contains
exact failed images, build metadata and full capture. Machine identities and
installed/bench status remain in `HARDWARE.local.md`.
5. Official MOS/VDP reference checkouts remain read-only. This task changes no
MOS/VDP API, transport ownership, startup contract or production selection.

## Completion boundary

An explanatory candidate is not a diagnosed hardware or software defect. No
physical action is authorized by the offline comparison itself. Existing startup
and keyboard recovery remain preserved while this work runs.

## Completed review

[Results](BUILD-COMPARISON-R01-RESULTS.md) record the comparison, evidence gaps
and proposed single-record 40 MHz control. Research only; no bench change.
Pause for discussion before the proposed experiment.
