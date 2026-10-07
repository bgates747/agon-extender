# Resident rendering suite

## Executive summary

`resident-render-suite-r01` selects the existing frozen rendering fixtures and
Author-reviewed colour/art checks for permanent residence on the Agon SD card.
The Pi reuses executable and drawing-data bytes already installed under
`/extender`; routine invocation needs only a small plan and startup selection.
Raw measurements remain under `/agents/extender/results` and can be collected
after the Author mounts the card on a host. This is an experimental
regression selection, not complete mode or production qualification.

The [catalogue](../../tests/performance/render_load/resident-suite.json) pins
12 files by SD path, build identity, size and SHA-256. Its selections do not
alter the [r04 benchmark contract](render-load-contract-r04.md). Retain these
files between runs; all12 selected files pass mounted-card hash verification
on2026-10-05. Install missing files once rather than redeploying a suite
for each firmware build. Historical results and startup copies are evidence,
not reusable fixture inputs.

## Representative checks

| Check | Modes | What it exercises | Operator controls |
|---|---|---|---|
| Static paced and throughput, cases0/1 |20,8; case0 also136|Drawing/fence floor and paced opportunities; the frame marker still changes.|Space advances; Escape exits.|
| Quarter/full fills, cases7/9 |20,8; case9 also136|Moderate and large framebuffer write areas.|Same indefinite benchmark.|
|16 lines and16 circles, cases15/23 |20,8|Sparse geometry and CPU rasterization.|Same indefinite benchmark.|
|16/64 bitmaps, cases39/41 |20,8; case41 also136|Asset rendering at two loads.|Same indefinite benchmark.|
|16 software sprites, case46 |20,8,136|Movement, background traffic and swap behavior.|Same indefinite benchmark.|
| Numbered full-palette chart |20,8,136,21,149|64/16-colour correctness and fixed-source presentation; no drawing during its three10s diagnostic windows.|Holds indefinitely; Escape exits.|
| Nurples sprites over AgonWolf3D walls |20,8,136|Recognizable colours, transparency, clean old positions and double-buffer redraw.|Two poses/s; P pauses/resumes; Space steps while paused; Escape exits.|

The drawing selection contains22 mode/case combinations. It is a compact
smoke/comparison suite; it does not replace the paused full progressive campaign.
Four- and two-colour modes, Copper and hardware-sprite stress are outside this
selection. Application completion includes EMOS routing, transport, drawing and
the pixel-query reply. Report its milliseconds and1000/ms equivalent frames/s
separately from application updates, accepted HDMI submissions and DMA cadence.

The frozen double-buffered software-sprite workload measures move/refresh/swap
commands without adding a per-frame back-plane redraw. Stock double buffering
does not provide the single-buffer saved-background behavior. Use the familiar-
art mode136 check for clean animation: it explicitly redraws the back plane
before each pose. Its extra redraw work is outside case46's timing scope.

The colour charts have passed Author review on the native HDMI path;20/8/136
also passed direct-panel review. Familiar-art single-buffer modes use the exact
passed r01 binaries. Mode136 uses the corrected r02 binary passed on both
mainboard and P4. Do not select r01 mode136: its per-pose CLS disabled moving
sprites. The card may retain that historical executable outside this selection.

## Invocation and file lifetime

1. EMOS owns Legacy/mainboard and ExCom/P4 routing. Startup selects the route,
   keyboard admission and `VDU 22 n` before `LOAD`/`RUN`; fixtures do not switch
   modes. Read the current bench constraints and local bench record first.
2. The benchmark executable and data20/8/136.rle remain at their catalogued
   paths. The maintained [runner](render-load.md) creates an owned result
   directory, writes its256-byte `plan.bin`, and installs a small temporary
   `/autoexec.txt`. The plan names that run's fresh result path. The executable
   protects existing result files; never reuse a result directory to overwrite
   an earlier measurement.
3. Manual benchmark runs schedule no keys. Each selected case continues until
   the operator presses Space or Escape. Long visual holds can exhaust the
   finite31,402-record sample capacity while drawing continues; truncated runs
   are visual checks, not complete statistical distributions. Automated runs
   use the same resident executable and timed keypresses, with at least64 valid
   frames required per measured case.
4. Colour and familiar-art executables contain their own data. The existing
   staging tools use catalogued SD aliases and preserve an installed file when
   its bytes match. Their small untimed readback verifies identity; it is not a
   new upload. Diagnostic chart telemetry requires a matching diagnostic P4
   image; ordinary firmware can display the fixture but supplies no phase data.
5. Restore the exact original startup and ordinary P4 image at experiment
   closeout. Close the foreground SD listener and stop Agon card use before
   asking the Author to remove the card. Permanent fixtures stay installed.

## Local-card result collection

The bounded RGB888 comparison supports `--defer-retrieval`. The Pi saves P4
telemetry and SD file sizes after each fixture has returned, leaving bulk samples
on the card. `measured-awaiting-local-results` is pending validation, not a pass.
This collection choice changes neither drawing bytes nor measurement windows.

Supply the actual mounted root as `RENDER_SD`, the retained host evidence as
`RENDER_EVIDENCE`, and a fresh receipt path as `RENDER_COLLECTION`. If the card
is mounted on another host, first read the explicitly selected files into a
local snapshot preserving SD-relative paths. Verify the remote mount identity
before/after collection and SHA-256 of every transferred file; retain that source
receipt. The offline tools may then use the verified snapshot as `RENDER_SD`:

```sh
.venv/bin/python qualification/render_load_collect.py --sd-root "$RENDER_SD" --evidence "$RENDER_EVIDENCE" --receipt "$RENDER_COLLECTION"
```

The collector reads the card without modifying it. It verifies retained
startup/plan hashes, SD sizes, raw mode/tag/geometry/build identities, complete
checkpoint ordering, at least64 frames, frame/error/truncation flags and matched
closed P4 windows. It preserves the pending receipt before recording validated
outcomes and never overwrites differing local evidence. Invalid or missing
records remain excluded from performance summaries. Firmware restoration is
independent of result validation and must not be inferred from a collection pass.

The [resident verifier](../../qualification/resident_render_suite.py) checks
the same card against the catalogue without contacting or changing either board:

```sh
.venv/bin/python qualification/resident_render_suite.py --sd-root "$RENDER_SD" --receipt "$RENDER_RESIDENT_CHECK"
```

Use one verified installation receipt to justify reuse on an unchanged card.
Recheck if the card or fixture files change. A matching file hash proves resident
bytes, not their visible correctness on a new firmware or monitor.
