# HDMI-001 — Fixed 720p HDMI presentation for existing Agon modes

## Executive summary

The Author proposes presenting all currently implemented Agon video modes
through a fixed 1280×720, nominal 60 Hz HDMI output on P4-PC. This is a product
output adapter for the maintained VDP, beyond compile-time board selection.
Preserve mode-native drawing and expose the resulting pixels to a separate
HDMI presentation buffer. The Author now authorizes implementation, builds and
pre-flash validation as a goal task, stopping with a shell command for the
Author to flash. The Author selects
centered, unscaled 1:1 presentation with black letterboxing and pillarboxing,
RGB888 presentation and hardware-paced VDP frames. The Author's r03 startup
and bounded gameplay checks now pass. Complete mode coverage, measured game
presentation throughput and excess sprite flicker remain unresolved.

For the separately authorized smaller-output experiment, see
[HDMI-002](HDMI-002.md) and its
[640×480 failure analysis/native 512×384 lessons](HDMI-002/TIMING-LESSONS.md).
That static custom 848×480 pass has not changed this task's product output.

## Scope and ownership

1. P4 VDP retains the stock-shaped rendering family, logical mode dimensions,
   native packing, palettes, Copper effects, sprites, readback, buffer swaps,
   completion and logical frame progression. EMOS continues to own ordinary
   VDU routing, activation and transport selection.
2. A P4 HDMI adapter converts/composes the current logical display into a
   1280×720 presentation buffer. P4 DSI hardware scans that buffer through the
   P4-PC LT8912B bridge to the monitor at nominal 60 Hz, independently of
   logical mode changes. Do not require Agon applications to render at 720p.
3. Reuse one maintained source tree and BOARD-001 board selection. Preserve
   the DevKit browser build. HDMI replaces browser video in the new selection;
   browser keyboard and other web services remain available. Later runtime
   output switching will be owned by EMOS and is outside this tranche.
4. Cover every currently implemented mode, with an enumerated coverage matrix;
   do not imply that this implements previously missing VDP modes or commands.
5. Minimize measured CPU work, conversion, copying and memory contention.
   A fixed scanout timing alone does not make presentation free or guarantee
   60 rendered frames per second.
6. The Author authorizes source implementation, builds and offline checks.
   Stop before flashing and provide the exact Pi shell command. No reset,
   live fixture execution, production promotion, commit or publication is
   authorized by this tranche. Read the ignored
   bench record before any later physical work; retain factory rollback and
   informative failed evidence without routinely creating firmware backups.

## Dependencies and bounded research

1. [Architecture](../architecture.md), especially the sole display-owner and
   output-boundary rules; PORT-003 owns existing logical rendering.
2. [BOARD-001](BOARD-001.md) supplies board configuration, not HDMI integration.
   [LCD-001](LCD-001.md) contains reusable local-display adapter work and an
   AUDIT-010 integration gate. The Author explicitly selects this bounded
   pre-flash HDMI implementation now. Preserve the current dirty source
   baseline as experimental evidence; do not substitute it for an accepted
   audit or qualified production baseline.
3. [P4PC-001](P4PC-001.md) retains standalone experiments: matched 720p timing
   produced visible bars and motion with approximately 60 Hz hardware scanout.
   Its slow circle renderer is not a product-renderer benchmark. Native 640×480
   visual failures remain unresolved and do not block a fixed-720p approach.
4. Official Agon [screen modes](../../../../agon-docs/docs/vdp/Screen-Modes.md)
   and [VDP contracts](../../../../agon-docs/docs/VDP.md) are the initial
   read-only API references. Pin exact relevant documentation/source commits
   and inspect the maintained renderer before implementing.
5. Use only ESP-IDF **5.5.5** P4 documentation for implementation:
   [DSI/DPI](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/lcd/dsi_lcd.html)
   and [PPA](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/ppa.html).
   Verify actual input/output formats, alignment, stride, scaling and cache
   requirements against the pinned SDK and board silicon. Do not assume PPA
   accepts stock packed palette formats or reproduces Copper effects.
6. Manufacturer references are indexed in
   [P4-PC references](../hardware/esp32-p4-pc/README.md). Reuse the visually
   successful timing/bridge configuration with its exact provenance rather
   than selecting a superficially equivalent generic preset.

## Decision register

| ID | State | Decision / recommendation and consequences |
|---|---|---|
| H001-D01 | Accepted by Author | Keep HDMI at 1280×720 nominal 60 Hz across logical mode changes. This avoids physical timing changes; it still requires presentation work. |
| H001-D02 | Existing architecture requirement | Preserve mode-native rendering storage; HDMI representation belongs at the output boundary. Directly replacing every drawing buffer with RGB888 720p requires a separately reviewed architectural change. |
| H001-D03 | Accepted by Author | Center the unscaled logical image at 1:1 source-to-output pixel mapping, preserving its pixel geometry. Fill surrounding space black with letterboxing/pillarboxing. No enlargement, reduction or aspect correction by resampling. For fitting W×H images, left/top offsets are floor((1280−W)/2), floor((720−H)/2); any odd extra border pixel goes right/bottom. See ADR-0024. |
| H001-D04 | RGB888 accepted; implementation choice | Expand completed native signal rows directly into RGB888 HDMI memory without an RGB565 intermediate or resampling. Reuse existing palette/sprite row composition unchanged; additional indexed/Copper work is deferred. |
| H001-D05 | Accepted by Author | Double-buffer HDMI when the logical VDP mode is double-buffered and resources permit, otherwise single-buffer. Publish completed double buffers at a hardware frame boundary; single-buffer output may tear. |
| H001-D06 | Accepted by Author | HDMI replaces browser video for now. Preserve web keyboard and other web services. Future runtime switching belongs to EMOS, outside this implementation. |
| H001-D07 | Accepted by Author | Center and crop oversized images for now. A 1024×768 image loses 24 rows at top and bottom in the 720-line output. |
| H001-D08 | Accepted by Author; silicon constraint | Preserve vblank-paced drawing opportunities, waits and frame counters. Use IDF 5.5.5's pre-v3 DMA frame-completion callback as its emulated vblank, one tick per hardware frame, independent of conversion success. Original 70/75 Hz modelines physically run at fixed ~60 Hz in this experimental HDMI selection; preserve nominal metadata and report actual scanout separately. |

Material accepted decisions must be promoted through the normal ADR,
architecture and dated-log process. Open choices remain in this task.

## Subtasks

### H001-01 [x] Establish task ownership

Separate product HDMI integration from board selection and standalone demos;
record the fixed-720p proposal, dependencies, implementation boundary and gates.

### H001-02 [x] Audit current rendering and presentation contracts

Enumerate implemented modes, dimensions, storage formats, palette/Copper and
sprite composition, frame publication and existing LCD/browser adapter hooks.
Record exact source identities and prepare a bounded research précis. The
Author's explicit goal authorization selects the current experimental source
for this pre-flash tranche without closing the independent audit.

### H001-03 [x] Resolve presentation geometry and resource design

Apply accepted geometry, cropping, RGB888, mode-dependent buffering and HDMI
selection. Tabulate per-mode dimensions and borders. Budget memory explicitly:
one RGB888 720p buffer is 2,764,800 bytes; two are 5,529,600 bytes, excluding
logical buffers, intermediate storage, alignment and other services.

### H001-04 [x] Implement the shared-source HDMI adapter and build selection

Use the maintained display owner's output boundary and successful bridge timing.
Validate board/output combinations and record exact dependencies/configuration
in identified build manifests. Avoid adding LVGL as a replacement renderer.
Keep DevKit/browser behavior unchanged and explain hardware-specific workarounds.

### H001-05 [ ] Verify fidelity and separate performance costs

Run meaningful host checks for geometry, conversion, palette changes, clipping,
mode transitions and buffer lifetime. Build both boards. Measure logical drawing,
presentation conversion/placement, synchronization and hardware scanout separately.
Use identical scenes/workloads for scanout-on/off comparisons; include static,
dirty-region, full-screen, scrolling, sprites and palette/Copper workloads.
Report CPU time, wall time, memory traffic where measurable, rendered updates/s,
presented frames/s and hardware refresh Hz with baseline and percentage changes.
Target 60 Hz scanout; measure whether each workload can meet a 16.67 ms update
budget rather than interpreting scanout refresh as rendered frame rate.
Offline geometry, conversion, ownership, mode-transaction, HTTP and browser
checks pass; actual drawing/presentation/scanout performance requires the later
physical tranche. The Author requested stopping before flashing.

### H001-06 [ ] Perform separately authorized hardware review

After build checks, obtain deployment authorization for the concrete candidate.
Leave each visual state unchanged until the Author reports the result. Check
all implemented modes, geometry, tearing, transitions and representative games;
verify monitor timing and browser/input/SD regressions. Retain informative failures.
Do not treat serial or DMA completion as visual acceptance.
The Author's bounded r03 review confirms startup and visible Nurples, Aginvadors
and Rally gameplay; this does not close the all-mode/geometry review.

### H001-07 [ ] Qualify and close out accepted scope

Run the applicable canonical qualification suite against identified installed
bytes after authorization. Record explicit Author acceptance and known limits;
complete current documentation and production promotion with the agreed version
and publication authority. Standalone demo success does not qualify this adapter.

## Implementation précis and mode geometry

1. Official read-only VDP v2.16.0 is commit
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`; MOS v3.0.2 is
   `8336409351ee5314e02801a7b72a4f1bb5282519`; documentation is
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. VDP/MOS remain clean;
   the docs checkout contains an unrelated untracked macOS metadata file.
2. The maintained `video/agon_screen.h` owns modes and candidate replacement.
   `stock_p4_service.cpp` owns drawing/output tasks and frame notifications.
   `stock_runtime_controller.hpp` copies one protected native row;
   `stock_scanline.cpp` preserves existing depth, palette and sprite composition.
   HDMI expansion happens outside the native mutex. No new indexed/Copper
   interpretation or palette API is added.
3. Native visible-buffer generation changes with a logical swap under existing
   row exclusion. If it changes during double-buffer conversion, the HDMI
   adapter discards that candidate instead of publishing mixed source frames.
   Hardware frame completion wakes drawing first; drawing wakes HDMI output
   after draining the vblank batch and committing its queued swap/sprite work.
   Presentation never gates the independent hardware frame counter.
4. IDF 5.5.5 is pinned to `b774170ff46c393eeb5e495ea37936038d3f4f4f`.
   Olimex's read-only reference is `04032d68e5c727870f9d40beb9e37b7ab3a66916`.
   The bridge component is vendored verbatim with file hashes in
   `vdp/components/esp_lcd_lt8912b/UPSTREAM.json`. The ignored hardware précis
   retains exact successful demo-source identities and SDK callback analysis.
5. Timings reuse successful r06/r09: 60 MHz pixels, two 720 Mb/s lanes,
   horizontal pulse/back/front 32/28/10 (total1350), vertical5/13/3 (total741),
   calculated59.979Hz. The bridge receives matched timing over I²C; DSI streams
   pixels. The panel-owned RGB888 memory byte order is B,G,R, unlike browser RGB.

| Logical dimensions | Mode examples / coverage | Left/right borders | Top/bottom borders or crop |
|---|---|---:|---:|
| 1024×768 | 18/19, 146; legacy0 | 128 px | Crop24rows each side |
| 800×600 | 16/17, 145 | 240 px | 60 px |
| 640×512 | 24–26, 153/154 | 320 px | 104 px |
| 640×480 | 0–2, 7; 129/130; legacy3 | 320 px | 120 px |
| 640×256 | 27–30, 156–158 | 320 px | 232 px |
| 640×240 | 3–6, 132–134 | 320 px | 240 px |
| 512×384 | 20–23, 149–151; legacy1 | 384 px | 168 px |
| 320×240 | 8–11, 136–139 | 480 px | 240 px |
| 320×200 | 12–15, 140–143; legacy2 | 480 px | 260 px |

This table describes adapter geometry, not hardware mode acceptance. Original
70/75Hz modes run at the fixed HDMI cadence. Existing indexed/Copper behavior
is reused without additional work or new qualification claims.

## Gotchas and verification limits

1. On silicon v1.3 the SDK callback is DMA frame completion, not a distinct
   true-vsync interrupt. The driver starts the selected next framebuffer before
   calling the application. Initialize DSI/DMA and submit buffers on core1,
   verify the actual callback core, and publish submission metadata after the
   driver selection. A callback between selection and metadata may delay release
   by one frame; it must never release the old scanout buffer prematurely.
2. The HDMI output retains two allocated panel buffers when available but
   writes the active buffer for single-buffered VDP modes. Allocation fallback
   to one buffer and single-buffer modes may tear. Mode teardown joins output
   and callback ownership before logical resources are released.
3. The direct driver path performs cache writeback and buffer selection without
   a second pixel copy. Its API flushes complete updated rows. Borders are only
   cleared when a given buffer's geometry changes.
4. The first sandbox build could not reach Espressif's component registry;
   no firmware was produced. That ordinary preparation bundle was discarded
   after retrying with admitted network access. No device access occurred.
5. Host ASan/UBSan checks run with LeakSanitizer disabled because this sandbox
   uses ptrace; leak detection cannot operate in that environment. Host tests
   and compile success do not establish HDMI timing, tearing or conversion
   performance on the board.
6. Source review after the first passing HDMI build found concurrent draw/output
   wakeups could race a queued logical swap and repeatedly discard timely
   conversions. The r02 source sequences conversion after the drawing batch.
   The unflashed r01 source/image is retained as superseded diagnostic evidence;
   do not select it for deployment.

## Pre-flash handoff — 2026-10-04 local

The authorized implementation goal is complete through the pre-flash boundary.
The selected experimental candidate is `hdmi-001-r02-b2026-10-05-01-19-20Z`;
the earlier unflashed r01 is superseded. Exact images, source snapshot, manifests,
validation and the unexecuted Author flash command are retained under the ignored
`agents/hdmi001/` build directory. The local bench record owns the command's
device endpoint. No device was flashed or reset during this tranche.

| Check / artifact | Result |
|---|---|
| P4-PC HDMI final-source build and native validator | PASS |
| P4-DevKit browser final-source compile and validator | PASS; nondeployable compile control |
| Build/source-selection guards | 18 tests PASS; board profiles 5 tests PASS |
| Geometry, RGB888 expansion, clipping and HDMI buffer ownership | PASS; ASan/UBSan |
| Native buffer-swap exclusion/generation and mode-failure preservation | PASS |
| Actual service scheduling: queued swap precedes presentation; busy presentation leaves frame clock advancing; detach joins workers | PASS; host task/HDMI substrate |
| HTTP/browser variants and Chromium keyboard/video regressions | PASS |
| Manifest integrity, merged factory segments and exact source snapshot | PASS; 19 artifacts, 4 segments, 5,427 source files |
| Factory image | 1,781,440 bytes; SHA256 `e1cad846a701499e3afa5f1b3617170f838bbf0ad2a62f524b7ebc206cf559d5` |
| ELF | SHA256 `08dfd6437966918df7e7fc96d213048f866e814dffb7b736ff676ab9ce694f64` |
| Image headers | ESP32-P4 v1.0–1.99; IDF 5.5.5; 16 MiB DIO 80 MHz; valid checksums/hashes |

The scheduling fixture is `tests/display/hdmi_frame_scheduling_test.py`; it
compiles the actual display service, Canvas and native controller against the
host task substrate and a fake physical HDMI endpoint. It verifies ordering
and resource lifetime, not interrupt affinity, physical timing or performance.
The Author still owns installation and visual review. Rendered frame rate,
physical scanout, tearing and live input/SD regressions remain unmeasured, and
H001-05 through H001-07 remain open. No production selection, commit, tag or
publication changed.

## First product bench failure and r03 correction — 2026-10-04 local

The Author reports installing r02, no EMOS startup response after two P4-PC
power cycles, and no ping response. A previously authorized 30-second passive
USB capture records continuous uptime (202–222 seconds), three HDMI diagnostic
windows, roughly 20 converted updates/s and 60 DMA frames/s. HTTP status is
unreachable before and after capture. No serial command, modem-line pulse,
deliberate reset or flash was performed by the agent.

The output worker runs on core 1 at priority 6; Arduino's setup task runs on
core 1 at priority 1. Measured conversion is about 49.4 ms, exceeding the
16.67 ms frame period. Drawing therefore posts another notification while
conversion runs, and the output worker immediately starts another conversion
without blocking. This can starve setup before console and Ethernet startup.
The capture proves live conversion, not the precise setup instruction reached;
startup starvation is the source-supported diagnosis awaiting corrected-image
verification. The existing host scheduling substrate does not emulate FreeRTOS
priority starvation, which explains this gap in pre-flash coverage.

The r03 correction blocks the HDMI output worker for one scheduler tick after
each presentation attempt. `taskYIELD()` is insufficient because it only admits
equal-priority tasks. Pending frame opportunities still coalesce normally;
the hardware frame counter and drawing worker do not wait for conversion.
Browser builds retain their existing scheduling. The informative r02 image,
source archive and failure capture remain retained under ignored local evidence.
The agent will build/validate r03 and stop before flashing again.

### r03 pre-flash handoff

`hdmi-001-r03-b2026-10-05-01-47-13Z` passes the full P4-PC HDMI build and native
validator. The final-source DevKit browser incremental build/validator and
actual-service scheduling regression also pass. The SDK tick rate is 1,000 Hz,
so the new blocking pause is one millisecond. The corrected source leaves the
browser worker unchanged.

All 19 manifest artifacts, four merged flash segments and 5,427 exact archived
source files pass integrity/current-source checks. App/bootloader headers pass
checksum/hash validation and admit P4 v1.0–1.99, with 16 MiB DIO 80 MHz and
IDF 5.5.5. Factory image: 1,781,440 bytes; SHA256
`facab1a27574d8476be64ee19c2fe1b809f581f74ff6fd7c528958230b2c53c8`.
ELF SHA256: `d234e6ba6d6dcd6d6b9bd7b422e3efeb7f304be509e1d16ff27b7b407c8694f0`.
Exact source archive and pre-flash/command receipts remain in the ignored build
directory. The command is provided for the Author and has not been executed by
the agent. EMOS startup, network availability, visible HDMI output and performance
still require corrected-image bench verification; this fix does not claim to
improve the measured conversion throughput.

## r03 Author gameplay review and passive timing — 2026-10-04 local

1. The Author reports r03 works at startup. Nurples appears to play at full
   speed with occasional apparent frame skipping. Sprites flicker more than
   on the mainboard VDP, especially with many sprites; the mainboard comparison
   is approximately one or two flickers per second when busy, by human report.
   No matched-scene quantitative comparison was performed.
2. The Author also confirms Aginvadors and Rally at 320×240. The Author has
   not fully exercised every screen mode. These are bounded visual/gameplay
   results, not a measured 60-update/s claim or full feature acceptance.
   The Author additionally confirms modes **0, 3, 8 and 20** work at an EMOS
   prompt. Record these exact mode IDs as prompt checks; do not infer that every
   colour depth, double-buffered variant or corresponding game scene was tested.
3. A 30.212-second passive capture retains 2,130 bytes and three complete HDMI
   timing windows. HTTP keyboard status is reachable and ready before/after,
   with the same boot token. Logs report continuous uptime. No command,
   mode change, key injection, deliberate reset or flash was performed.
4. A display-status GET after capture reports mode20, 512×384, 64 colours,
   single-buffered, with fixed 1280×720 HDMI output. It was read about one minute
   after capture ended; the exact game/scene during capture is not independently
   identified. Do not label these samples a controlled Nurples benchmark.

The table ranks captured windows by worst conversion wall time, highest first.
Conversion includes existing row composition, native-lock waiting and RGB888
expansion; it is not an isolated bit-shifting or CPU-time measurement.

| Window ending at P4 uptime | Completed updates/s | DMA frame completion Hz | Conversion wall mean / max (ms) | Cache submission mean (ms) |
|---|---:|---:|---:|---:|
| 933.829 s | 19.221 | 59.954 | 50.126 / 53.173 | 0.686 |
| 953.882 s | 19.155 | 59.960 | 50.373 / 53.028 | 0.684 |
| 943.859 s | 19.242 | 60.020 | 50.054 / 51.363 | 0.679 |

These counters establish roughly 19.2 complete submissions/s during the capture,
with roughly 60 DMA frames/s. They do not count unique pictures observed by the
monitor. Independent logical frame timing can keep game motion at its intended
speed while presentation skips updates. No percent comparison to mainboard or
prior builds is justified without an equivalent identified scene/workload.

### H001-F01 — Excess sprite flicker remains open

The output pass protects native access one row at a time and may span several
logical frames. In single-buffered modes the P4 also writes the active HDMI
buffer. Mixed native sprite states and scanout/write overlap are therefore
plausible causes of the reported flicker, not proven root causes. Diagnose source
frame coherence and output tearing separately; profile row composition/locking
and RGB888 expansion separately before choosing a remedy. Preserve the accepted
mode-dependent buffering policy and EMOS ownership. New source changes and a
replacement firmware build have not been made in response to this report.

## Deterministic performance investigation

[BENCH-009](BENCH-009.md) owns the Author-authorized frozen shared benchmark
suite and optional output controls. Its controlled results will inform H001-F01
and presentation performance; passive r03 samples remain separate evidence.

### H001-F02 — Double-buffer presentation starvation candidate

The first controlled normal-HDMI benchmark pass records zero accepted HDMI
submissions in81 mode149 cases, including the light static case0, and one
mode136 case. Case0's application advances at60 updates/s while diagnostic
conversion attempts average35.176ms. These counters do not establish physical
displayed FPS. `HdmiOutput::publish` rejects a double-buffer row pass when its
native visible generation changes before completion; a35ms attempt can span
more than one60Hz swap. That condition is an explanation candidate, not an
independently attributed rejection reason. BENCH-009 owns ordinary-image
controls with benchmark hooks absent before interpretation. Any presentation
remedy belongs here and must preserve ordinary VDP vblank/swap behavior, frame
coherence and the accepted buffering policy. No renderer change is made by the
benchmark investigation.
