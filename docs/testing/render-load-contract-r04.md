# Render load benchmark contract r04

## Executive summary

Fourth frozen benchmark contract under [BENCH-009](../tasks/BENCH-009.md), authorised
by the Author on2026-10-04. One eZ80 application submits deterministic progressive
workloads through EMOS to either VDP. Application-visible completion, P4 drawing/
presentation phases and hardware refresh are different measurements. No result
may be described as physical displayed FPS without independent output evidence.

The machine-readable `tests/performance/render_load/contract-r04.json` definition under `tests/performance/render_load`
is normative for counts, ordering and parameters. Freeze both hashes before
implementation. Changes require a new contract revision and fresh identified runs.

## Workload and execution

1. Default modes are20,8,136,21,149. Mainboard and P4 run equal modes/colour depths.
   Mode148 is not supported;21/149 supplies the512×384 double-buffer pair.
2. Each level preloads assets and40 generated template frames, performs8 warm-up
   frames, then repeats the deterministic40-frame cycle indefinitely. Space
   advances one case; Escape finishes the active case and exits the application.
   Presses are latched through the public MOS keyboard callback; release and
   typematic repeats cannot cause duplicate advancement. No timer advances cases.
   Integer trajectories use seed0xB009. Levels1,4,16,64 increase count or a stated
   area/overlap unit. Coordinates preserve an8-pixel top band for a frame marker.
3. Families: static control; growing rectangle area; lines/circles;16/32-pixel
   bitmaps; moving software/hardware sprites; fixed64 sprites with growing overlap;
   text/scroll; mixed primitives/bitmaps/sprites. Commands and asset formats are
   explicit. RGBA2222 is used for prepared bitmap assets.
4. Software/hardware sprite variants use the same images/positions, explicit API
   selection and one refresh after each complete movement batch. Setup resets
   sprites and painting/context state. Double-buffer setup initialises both buffers.
5. Automated runs use the same fixture and admitted keyboard path: the Pi injects
   Space at10-second wall-clock intervals after a20-second startup allowance.
   Actual case bounds and completed frames are recorded; compare rates and
   distributions, not equal work totals. Cases with fewer than64 measured frames
   are marked short and repeated at longer explicit intervals. A transition
   requested during preparation may end the next case prematurely; reject that
   result rather than silently stretching or claiming a fixed10-second window.
   Three passes alternate endpoint order mainboard/P4, P4/mainboard, mainboard/P4.
   Within each pass levels rise monotonically. Failures are outcomes, not discarded
   samples. Warm-up,
   loading, setup, SD saving and result retrieval are untimed. Retain up to31,402
   per-frame records in RAM; visual rendering continues after capacity, with
   truncation explicitly recorded. Complete automated distributions require no
   truncation. Checkpoint records only after a case ends.
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

## Revision authority and retained evidence

The Author requested longer runs, indefinite visual inspection, manual case
selection/exit and wall-clock scripted keypresses on2026-10-05. This changes
execution from fixed32-frame work to repeated templates and measured actual
windows. The frozen r01 contract and its successful two-case clock/protocol
pilots remain evidence; they are not long benchmark results.

Lossless SD packing is permitted outside measurement: the host validates the
packed stream against the original generated bytes, verifies one deployed
whole-file readback, and the eZ80 restores each complete case before setup and
warm-up. Packing does not change any measured VDU bytes. Fast upload retains
packet CRC checks and skips repeated whole-file verification passes.

The official [MOS memory map](../../../../agon-docs/docs/MOS.md#memory-map)
limits module-safe user RAM to0x040000–0x0AFFFF. r03 corrects the r02 prototype
record allocation:15,018 records at0x044000 and16,384 at0x080000. The latter
reuses unpacking memory after a whole case is restored at0x070000. Metadata
lives below the first record region. Code must fit below0x042000. No module,
MOS heap/stack or unmapped addresses are written. This capacity correction
does not change the drawing sequence or indefinite visual controls. r02
prototype failures remain informative evidence; no valid long results exist.

## r04 sprite setup correction

The r03 generator selected hardware/software only once, for the current sprite.
That could not establish the declared type for every active sprite. r04 selects
and configures each active sprite explicitly after attaching its RGBA2222 frame:
paint mode0, hardware or software API, then visibility. Old sprites are
deactivated before reset/frame-list changes. Setup remains outside measurement.
All trajectories, frame drawing bytes, case IDs, levels, clocks and controls stay
the same. Preserve r03 manifests, checkpoints and its unresolved mainboard warm-up
fence failure; do not relabel those sprite rows as correct r04 comparisons.
