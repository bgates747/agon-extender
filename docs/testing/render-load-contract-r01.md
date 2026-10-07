# Render load benchmark contract r01

## Executive summary

Frozen first benchmark contract under [BENCH-009](../tasks/BENCH-009.md), authorised
by the Author on2026-10-04. One eZ80 application submits deterministic progressive
workloads through EMOS to either VDP. Application-visible completion, P4 drawing/
presentation phases and hardware refresh are different measurements. No result
may be described as physical displayed FPS without independent output evidence.

The adjacent machine-readable definition under `tests/performance/render_load`
is normative for counts, ordering and parameters. Freeze both hashes before
implementation. Changes require a new contract revision and fresh identified runs.

## Workload and execution

1. Default modes are20,8,136,21,149. Mainboard and P4 run equal modes/colour depths.
   Mode148 is not supported;21/149 supplies the512×384 double-buffer pair.
2. Each level preloads all assets and40 generated frames:8 warm-up,32 measured.
   Integer trajectories use seed0xB009. Levels1,4,16,64 increase count or a stated
   area/overlap unit. Coordinates preserve an8-pixel top band for a frame marker.
3. Families: static control; growing rectangle area; lines/circles;16/32-pixel
   bitmaps; moving software/hardware sprites; fixed64 sprites with growing overlap;
   text/scroll; mixed primitives/bitmaps/sprites. Commands and asset formats are
   explicit. RGBA2222 is used for prepared bitmap assets.
4. Software/hardware sprite variants use the same images/positions, explicit API
   selection and one refresh after each complete movement batch. Setup resets
   sprites and painting/context state. Double-buffer setup initialises both buffers.
5. Three passes alternate endpoint order mainboard/P4, P4/mainboard, mainboard/P4.
   Within each pass levels rise monotonically. Failures are outcomes, not discarded
   samples. Warm-up, loading, setup, SD saving and result retrieval are untimed.
6. The application contains no mode switch, UART/GPIO access or route override.
   `/autoexec.txt` selects EMOS route and `VDU 22 n` before loading it. Payloads
   are length-bounded and hash-verified after deployment. Frames are identical
   across endpoints; diagnostic run tags outside timing may differ.

## Measurements

1. Submission ends after counted MOS output returns; this includes eZ80 command
   copying, routing and transport backpressure. It is not rendering completion.
2. Completion follows official screen-pixel query23,0,0x84 and its matching MOS
   reply flag. The VDP query fences earlier Canvas work. Its cost includes the
   reply and MOS dispatch. It does not measure physical display or all recurring
   sprite/scanline work. Use empty controls to show overhead without subtracting
   it as a constant. Double-buffer frames include the ordinary swap command.
3. Throughput frames have no deliberate pacing. Paced frames target successive
   60Hz opportunities using raw MOS clock deadlines; they never omit workload
   updates to appear faster. PRT1 measures submission, completion and total wall
   intervals. Counts are /256 system-clock ticks, with saturation recorded as
   overflow/failure, never unwrapped. Raw MOS clock corroborates run duration.
4. Nominal PRT units are13.889µs/count at18.432MHz. Raw MOS time advances2 per
   mainboard60Hz vblank; it is120 units/s with16.67ms granularity. Clock calibration
   and immediate-read controls precede comparisons. A16.67ms active completion
   budget is1,200 nominal PRT counts; report clock limits beside deadline results.
5. The P4 diagnostic image measures discontiguous wall intervals for drawing drain,
   native-row lock waiting, row composition, RGB888 expansion, cache submission,
   complete conversions/submissions and DMA frame completion. These are not
   exclusive CPU times. Phase intervals crossing window boundaries are excluded
   and counted. Window bounds may exclude one in-flight conversion.
6. A small prepared bitmap encodes frame index and complement in the top band.
   It supports P4 complete-conversion identity checks and future camera observation;
   it does not prove a coherent image reached the monitor. Single-buffer writes
   can overlap scanout. Mainboard physical frame delivery remains unavailable.
7. Controls retain the same executable: no frame marker/timing probes, marker with
   timing probes disabled, and ordinary marker/timing. Compare perturbation.
   Diagnostic window records must match run tag/case ID with no missing closures.

## Diagnostic windows and output controls

1. An ordinary buffered write23,0,0xA0,65535,0,12,payload carries magic`B009`,
   version1, op(reset0/begin1/end2), little-endian caseID16, flags(timing bit0,
   frame marker bit1) and runTag24. Ordinary mainboard firmware consumes/discards
   the same bytes. Only an explicitly selected P4 diagnostic build observes them.
   No logging, replies, file I/O or network requests occur in per-frame timing.
2. Normal HDMI provides existing scanout and conversion. Held HDMI retains DMA
   scanout/logical hardware cadence but suppresses presentation conversion.
   Render-only retains logical buffers/resident RGB888 memory and ordinary drawing,
   suppresses conversion and starts no DSI DMA; a60Hz software clock supplies
   opportunities. This clock/resource difference must accompany comparisons.
3. Pair the full five-mode mainboard/normal-HDMI suite. Replay modes20/8 for
   held-HDMI and render-only controls with the same passes/workloads. The hold/off
   pair isolates scanout contention in native rendering; normal/hold isolates
   presentation interference. Neither pair isolates RGB expansion without phase
   instrumentation. No architectural timing change is promoted from these tests.

## Validity, recovery and reporting

1. Reject wrong mode/geometry, payload corruption, missing fence reply, timer
   overflow, transport failure, malformed/incomplete records or telemetry mismatch.
   Preserve checkpointed prior cases, mark failed cases, recover a known fixture,
   continue independent work and repeat affected cases without timing probes.
2. Keep finite preparation/runtime/retrieval clocks separately. Pilot evidence
   determines advance estimates; explicit bounded fixture deadlines govern recovery,
   never an assumed duration. Restore prior startup byte-for-byte and ordinary P4
   firmware at the end; verify admitted EMOS input and HTTP readiness.
3. Present worst cases first, ranked by P4/mainboard completion slowdown. Tables
   name endpoint/variant, units, baseline and `(P4−mainboard)/mainboard×100%` for
   equal application metrics. Report medians, ranges/p95, achieved application
   updates/s, over-budget frames, failures and phase costs separately.
4. Preserve exact source/tool/image identities, raw records, contract hashes and
   payload hashes. Do not claim production qualification or measured monitor FPS.
