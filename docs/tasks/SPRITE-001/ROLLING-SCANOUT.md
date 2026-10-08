# Rolling DSI scanout experiment — 2026-10-07

## Executive summary

**P4 scanout-time sprite composition works in isolation, but the prototype is
not ready for Nurples.** The Author saw clean backgrounds and32 moving sprites
at60 frame completions/s. Adding scrolling traffic on the other CPU core made
even the static background flicker. Refills became longer than a strip's nominal
scanout interval while frame counters still reported60Hz and no DMA errors.
Smaller strips did not remove that timing failure. The full Extender renderer
was not changed, and no hardware-sprite game run was attempted in this tranche.

This is the bounded one-hour experiment authorized in
[SPRITE-001](../SPRITE-001.md), from04:39:03 to05:39:03 UTC. Exact source/build
identities, raw-capture hashes, observations and host checks are retained in
[the portable results](ROLLING-SCANOUT.json). Local raw captures, frozen build
trees and flash receipts remain under `agents/sprite001/rolling/`.

## What the prototype does

1. The Pi builds/flashes a standalone P4 image. It contains no Agon transport,
   keyboard, network, SD or normal VDP command service. Agon stays idle during
   these tests. Its SD files and startup are untouched.
2. A project-owned derivative of pinned ESP-IDF5.5.5 splits the848×480 RGB888
   image into eight60-row, or twelve40-row DMA blocks. Both counts fit the
   hardware's four-bit block count. This does **not** demonstrate arbitrary
   descriptor lists or solve SCAN-001's much larger block-count problem.
3. Fixed descriptor addresses alternate two scratch buffers. After DMA retires
   one block, the P4 CPU fills that buffer for the block two positions ahead.
   The final block's refill is deferred until after the full-transfer callback
   rearms DMA. No live descriptor source addresses change.
4. The successful small-scene variants use internal SRAM scratch buffers.
   Background pixels remain in PSRAM; the CPU copies them before composing
   sprite pixels into the scratch buffer. Sprites never alter the background.
   This follows mainboard's scanout-composition principle, but uses much larger
   strips and a different P4 DMA peripheral.
5. The retained FabGL `rawDrawSpriteScanline` function body is unchanged. A small
   standalone type scaffold supplies immutable16×16 RGBA2222 assets copied from
   Nurples. Populations rise1→8→16→32 every600 frame completions. RGB888/RGB222
   adaptation initially converted full rows; the improved variant converts only
   sprite-covered spans, initializing all spans before drawing overlaps.
6. The final variants copy only512×384 at offset168,48; the848×480 border stays
   black. After3600 completed frames, core0 repeatedly scrolls a256×336 region
   in a **separate PSRAM allocation**, nominally60 times/s. The scanout/refill
   work is on core1. This loads shared memory without changing the displayed
   background. It is not actual Nurples, a live renderer or an exact workload
   model of the accepted scrolling implementation.

## Results

Rows put the failed load cases first, followed by the diagnostic controls.
Times are cumulative observed maxima since boot in the specified retained
capture, not stable percentile estimates. Populations, row counts and copied
areas differ as stated; do not compare unlike rows as a throughput ranking.

| Variant | Relevant load | Refill maximum, µs | DMA frames/s | Outcome |
|---|---|---:|---:|---|
| Centered copy,8 strips, SRAM |32 sprites + separate-core scrolling |3,045 |About60 |Author sees static left gray/checker boxes flicker, exposing red bars; timing gate fails |
| Centered copy,12 strips, SRAM |32 sprites + same separate-core scrolling |2,195 |About60 |Timing gate still fails; no separate Author visual acceptance recorded |
| Full-row sprite conversion,8 strips |8 sprites reached |4,330 |Falls from60 to30 |Author reports heavy disturbance and blue background |
| PSRAM scratch,8 strips |Synthetic square |3,751 |About30 |Severe flicker; missed block callbacks |
| SRAM scratch,8 strips, refill before DMA rearm |Synthetic square |1,477 |About30 |Blue/flickering; faster copy alone insufficient |
| SRAM scratch,8 strips, rearm before final refill |Synthetic square |1,480 |About60 |Author confirms stable black background and moving square |
| Covered-span sprite conversion,8 strips |32 sprites, no scrolling load |1,965 |About60 |Author: excellent, no sprite/background flicker; thin timing margin |
| Centered copy,8 strips, before load |32 sprites |1,415 |About60 |No conservative threshold exceedance before scrolling load |
| Centered copy,12 strips, initial capture |Up to16 sprites |811 |About60 |No conservative threshold exceedance in initial capture;32-sprite unloaded window not separately retained |
| Static8-block image |No refill/composition |N/A |About60 |Author confirms intact/stable picture and all four edges |

At the configured240MHz/7 pixel clock and1104 total pixels/line, nominal active
strip intervals are1,932µs for60 rows and1,288µs for40 rows. The memory-load
maxima are respectively **158% and170%** of those intervals. These are timing
warnings, not measured DMA read deadlines: FIFO behavior and interrupt delivery
must also be accounted for. The conservative instrumentation thresholds are
1,500µs and1,000µs; they count exceedances and never skip drawing.

An otherwise comparable synthetic-square control gives a useful isolated
comparison: moving scratch storage from PSRAM to SRAM reduced mean refill from
3,377.51 to1,400.37µs, **58.5% less**, but output remained30Hz until DMA rearming
was moved ahead of the final refill. The same square then reached60Hz with
essentially unchanged1,400.93µs mean refill. Means include copying, composition
and cache maintenance and are cumulative since boot.

The covered-span32-sprite case has1,385.77µs cumulative mean background-copy
time, before composition/cache work. Limiting copying to the logical image
reduces that cumulative copy mean to about730.5µs before concurrent load.
That is an intentional reduction in copied pixels, not a faster equivalent
full-image copy. Neither figure measures the Agon's game loop.

## Important failure interpretation

1. **A60Hz DMA counter is not a correctness test.** The loaded centered cases
   have zero recorded invalid-block, underrun, callback-sequence and cache API
   errors while refills exceed the nominal strip interval. DMA can keep sending
   bytes from a buffer the CPU has not finished preparing. The prototype has no
   independent buffer-generation check or fail-safe ownership/recovery path.
2. The Author first praised the unloaded picture, then reported flickering in
   static gray line/checker boxes at the left, with red bars appearing through
   them. These are part of the static pattern, not moving sprite objects. The
   later failure therefore limits the earlier pass; it is not solely a sprite
   transparency error. The initial conversational description as sprites
   revealing background was corrected after inspecting the fixture.
3. The visible failure coincides with the deliberately introduced other-core
   memory workload. Shared memory/cache contention and refill scheduling are
   leading explanations. This experiment does not isolate bus arbitration,
   cache effects, interrupt delay and CPU cost individually.
4. The earlier blue background and30Hz cases are useful failures, not evidence
   that the pattern intentionally uses blue or that the monitor runs at30Hz.
   Refilling before DMA rearm delayed the producer past the available vertical
   blank; changing ordering recovered60Hz. No physical HDMI clock measurement
   was performed.

## Reuse, verification and limits

The implementation is isolated under `vdp/dsi-strip-test/`. Its generator pins
the original DPI source hash and generates a build-local derivative; the pinned
SDK and official Agon reference checkouts remain unchanged. Build manifests
freeze each source tree; the current tree is the last12-strip variant, not all
earlier variants. Ordinary full firmware is not built from this project.

`tests/display/dsi_strip_sprite_test.py` compiles the retained stock sprite body,
verifies that body and four asset hashes, then compares **every pixel** against
an independent RGBA2222 reference for eight poses/populations using both strip
sizes:16 complete-frame comparisons pass. This proves those sampled software
compositions, not ISR safety, DMA timing, arbitrary sprite formats or lifetime.
Every flashed image had its segments read back and verified.

Serial measurements use P4 `esp_timer` microseconds, without external
calibration. Frame rates use roughly five-second deltas; cumulative counters
are read separately and can advance between printed lines. Refill/copy means
must not be mislabeled as steady-state32-sprite measurements. Initial deployment
captures last25s; extended captures retain32-sprite/load intervals. Build/flash,
observation and capture durations are separate from frame timing. Two early
host builds needed an escalated IDF frontend restart; one missing timer header
was corrected before any flash. These setup corrections are not hardware faults.

## Remaining boundary

SPR01-07 remains open. Before connecting the real VDP, the P4 output path needs
sufficient refill headroom under concurrent drawing and a defined response when
a buffer is late. Candidate research is DMA-assisted background copying or a
different buffer pipeline; neither was implemented or proved in this hour.
The four-bit block count still applies. Adding cores alone does not remove
contention on shared memory.

Real integration also needs an ISR-safe scene snapshot and bitmap lifetime
ownership, with correct mode-change/double-buffer retirement. The existing
native renderer's task mutex cannot simply be taken from this refill ISR.
Only after those gates should the existing small sprite fixtures precede the
authorized deterministic hardware-sprite Nurples run. No actual game, scrolling
renderer, input-response or complete Extender service qualification was performed
under the rolling output path. Production selection remains unchanged.
