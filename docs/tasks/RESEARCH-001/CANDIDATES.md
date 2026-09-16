# P4 implementation candidates — RESEARCH-001

## Executive summary

**Recommend studying Espressif's LVGL adapter for completion/ownership contracts,
and micro-mp3 for a small, reproducible concurrency diagnostic.** Neither proves
our cause or supplies a qualified fix. Five candidates survived source review;
they provide complementary techniques, not a leaderboard of fastest firmware.
No candidate was built, executed, flashed or benchmarked. No new performance
measurements were made. Golem remains excluded.

The key question remains whether P4 output work delays drawing through CPU
scheduling/locks, shared memory/cache traffic, or both. Separate cores do not
necessarily separate memory traffic. Our P02 composition-only repeat varies
substantially even without network sends; a network-only fix is premature.
[Existing evidence and limitations](../QUAL-003/debrief/P02/README.md) remain
unchanged. No matching implementation with independently reproduced, directly
comparable P4 rendering-plus-Ethernet tail measurements was found in this pass.

| Rank | Candidate | Most useful contribution | Evidence and material limit |
|---|---|---|---|
| 1 | Espressif `esp_lvgl_adapter` | Explicit buffer handoff, submission/completion distinction, blocking outside short state locks | Source inspected; LCD/DMA callbacks differ from our web output; no matching latency distribution |
| 2 | ESPHome `micro-mp3` benchmark | Controlled concurrent workers, per-call variability, memory accounting | Source plus author P4 measurements; audio throughput is not graphics latency; causal bus-contention claim overreaches its controls |
| 3 | NINA P4 display | Snapshot ownership separated from encoding/network; allocation and performance instrumentation | Real application and test infrastructure; occasional JPEG capture, not sustained lossless RGB222 streaming |
| 4 | Espressif GMF `esp_player` | Explicit stage queues, ownership and A/V pacing; useful overload semantics to inspect | Source and vendor figures; different clocks, workload and possible frame dropping |
| 5 | P4 Vectrex | Sparse redraw, separate producer/renderer, internal descriptors and explicit frame discard | Interesting design; cross-core state transitions deserve audit before reuse; frame-rate counters do not establish every-frame completion |

**First avenues after review:** retain QUAL-003's existing sequence. Use P01c/d
to attribute waits and actual task affinity; use P02 to resolve repeat/boot/order
variance and test one memory/placement or affinity variable at a time. Borrow
the benchmark *method*, not an MP3 decoder or new graphics stack. Keep P06's
P4-local producer/output control as the independent network-capacity experiment.
Do not add five parallel implementation tasks or replace FabGL with LVGL.
All experiments below are proposals awaiting review.

Subsequent Author clarification: six-bit transport packing is worth considering,
subject to auditing mode widths/colour depths and byte alignment. Full-frame
one-byte-per-pixel performance remains a hard goal for eventual 256-colour
palettes; sparse redraw or six-bit-only results cannot replace it. The
[P06 work contract](../QUAL-003/DEBRIEF-PLAN.md#p06--browser-delivery-audit-and-isolated-pattern-benchmark)
owns this requirement and the optional packing audit. No encoding change or
experiment has started.

## 1. Why these sources, and answers to the discussion

1. **Beyond HTTP:** discovery covered P4 emulators, audio, graphics adapters,
   multimedia pipelines, memory benchmarks and asymmetric multiprocessing.
   HTTP is only one possible consumer competing with drawing; PSRAM, cache,
   locks, runnable delay and interrupt placement remain separate hypotheses.
2. **Finding excellent work:** follow concrete source paths and failure reports,
   not adjectives or popularity. Inspect allocation flags, who may write each
   buffer, what releases it, whether a wait holds a lock, overload behavior,
   and what a reported FPS actually counts. Small reproducible tests with
   correctness checks carry more weight than impressive screenshots.
3. **Human versus generated code:** provenance can be recorded when disclosed;
   writing style cannot establish authorship or competence. We evaluate the
   implementation regardless. One benchmark below explicitly warns about AI
   generation; its inconsistent numerical claims, rather than that disclosure,
   are the reason not to rely on its conclusions.
4. **Espressif deserves serious consideration:** its examples expose supported
   API lifetimes, callback ordering and hardware constraints. That does not
   make a teaching example or isolated maximum-throughput configuration optimal
   for concurrent graphics and networking. Apply the same measurement and
   correctness scrutiny to vendor and independent work. Vendor implementations
   occupy two shortlist positions because of inspected mechanisms.
5. **What this review establishes:** pinned source behavior, reported results
   and worthwhile next checks. It does not certify any project's correctness,
   establish independent replication, or identify the smartest author. Recent
   commit samples and test trees were inspected as supporting provenance;
   maintenance activity is not a hardware performance test.

## 2. Published measurements — scopes must remain separate

These are author/vendor reports, **not our measurements**. No stock-versus-P4
percentage is calculated: these workloads cannot be compared with Agon drawing.

| Source and scope | Configuration | Published result | Proper interpretation |
|---|---|---|---|
| micro-mp3, decode each 30-second 64kbps clip | P4 360MHz, hex PSRAM; checked defaults select 200MHz | 1 worker ~1200ms; 2 workers together ~1200ms; 3 ~2300ms; 4 ~2500ms | Independent jobs can overlap well; 3/4 also share two CPUs, so their slowdown does not isolate the memory bus |
| GMF video maximum-performance table | P4 400MHz, PSRAM250MHz | H264 320×240:68fps; 640×480:18fps | Decode/playback capability under vendor conditions, not software primitive throughput or our browser presentation |
| NINA/Vectrex/adapter under our workload | No matching run | Not measured | Do not infer parity from a visible demo or configured refresh interval |

Sources: [micro-mp3 benchmark report][mp3-report], [GMF configuration and video
table][gmf-report]. Our selected build uses360MHz/200MHz with IDF5.5.5 and
Arduino3.3.11; see [local build facts](LOCAL-FACTS.json). None of these reports
supplies a matched mainboard baseline or verifies our board/SDK combination.

## 3. Candidate details

### C1 — Espressif LVGL adapter: best ownership/timing reference

In [the v9 bridge][lvgl-bridge], `switch_seq`, pending submission and waiter
state are protected by short critical sections. The worker leaves that section
before blocking on the completion semaphore; the ISR updates completion state.
This addresses the distinction between submitting a buffer and safely reusing
it. In [the adapter task][lvgl-task], task affinity and stack memory capabilities
are configurable, with internal-memory fallback for stack allocation.

The [component manifest][lvgl-manifest] declares adapter0.7.0, IDF>=5.5 and
LVGL8/9. This permits investigation against our IDF generation, not compatibility
certification. Its [README][lvgl-report] explicitly cautions that PPA can reduce
CPU work without a noticeable FPS gain, and documents a PPA freeze workaround.
Tree inspection found benchmark and LVGL8/9 test applications; they were not run.
Driver interrupt placement and every buffer mode were not exhaustively audited.

**Proposed check:** instrument our existing buffer handoff with sequence IDs and
separate wait/hold/completion timings, then verify no lost wakeup or premature
reuse under a deliberately slow output consumer. Retain stock VDP semantics;
do not import LCD vertical-sync pacing or DMA cache operations into a CPU-only
handoff without proving that those contracts apply. Owner: P01c/d and P02.

### C2 — micro-mp3: best small concurrency experiment pattern

Completed [focused review](C2/README.md): useful structure, but creation-failure
result accounting and timing confounders rule out unmodified diagnostic reuse.

[Benchmark source][mp3-code] creates independent decoder/output state, pins
workers to alternating cores, records each decode duration, and uses a counting
semaphore for completion. Heap deltas are trusted only during a single-worker
run. The source records setup separately and yields between calls. The
[conformance harness description][mp3-tests] compares PCM to reference vectors;
it is a separate correctness facility, not proof of concurrent P4 timing.

Important limits: workers start sequentially without a common release barrier;
whole-run time includes creation/completion overhead. Priority1 and per-call
yielding differ from our tasks. Three/four workers oversubscribe two cores, so
README attribution to bus contention is not established by that comparison.
The timed benchmark does not itself hash output against a concurrent reference.
[P4 defaults][mp3-config] fit our360/200MHz clocks; [PlatformIO configuration][mp3-platform]
selects a different platform package, so SDK equivalence is unproven.

**Proposed check:** adapt the measurement structure to our deterministic
composition/copy workload: fixed verified data, common start barrier, one/two
workers, internal/PSRAM variants, timing distributions and output hashes. Keep
aggregate reporting outside the timed window. Owner: P02, with P01 attribution.
Do not run the external audio firmware on the bench as a substitute.

### C3 — NINA display: relevant snapshot separation, not a stream benchmark

Completed [focused review](C3/README.md): ownership principle already present;
input-alignment explanation needs qualification and instrumentation has limits.

[The screenshot handler][nina-screen] serializes its reusable encoder buffers
with a screenshot mutex, holds the display lock only while obtaining an owned
LVGL snapshot, then unlocks before copying, JPEG encoding and HTTP sending.
Boot-reserved buffers reduce repeated allocation; fallback allocation still
exists. Source comments report stale/banded images with direct encoder input,
so the implementation copies to an encoder-allocated DMA-aligned buffer.
That observation applies to its JPEG hardware path, not evidence that our
CPU-only snapshots need cache flushing.

The screenshot mutex remains held through encoding and network output; it does
not bound their latency or make sustained capture free. [Performance code][nina-perf]
contains diagnostic facilities; [host tests][nina-tests] use platform shims and
cannot validate real scheduler/cache contention. [Dependency manifest][nina-manifest]
pins esp_lvgl_port2.8 to avoid an IDF6-only API; its BSP and Wi-Fi companion
hardware differ from ours. No suitable sustained capture distribution located.

Its timing state itself resides in PSRAM, and the allocation-failure hook prints
to UART. Those diagnostics need overhead/concurrency review before borrowing;
their presence alone is not evidence of low-impact measurement.

**Proposed check:** measure our display-lock duration separately from snapshot
conversion and send, retaining an owned immutable snapshot after unlock. If
that separation already exists, use it as a control rather than rewriting it.
Owner: P01c/d; output-only behavior remains P06. JPEG adoption is not proposed.

### C4 — GMF player: stage ownership and overload semantics

Completed [focused review](C4/README.md): retain explicit outcome accounting;
pacing/discard does not recover already-produced frame cost. No direct fix.

[Data-bus wrapper][gmf-bus] tracks timestamps and remaining byte counts in a
bounded metadata queue. It protects metadata with a mutex and delegates payload
acquisition/release to GMF; inspected paths release the metadata lock before
potentially waiting in the underlying bus. Full-queue and metadata-underrun
paths are explicit. This is useful code to trace, not proof every path is free
of races or unbounded waits.

[Clock synchronization][gmf-sync] has deliberate pacing and frame-discard paths,
including seeks and sufficiently late accelerated playback. Dropping a video
frame may be appropriate there; dropping a VDP command is not. [Scenario tests][gmf-tests]
exercise errors, recovery and concurrent control, but were not run here. The
pinned player is1.0.6; its component dependency graph and OAL allocation/IRQ
placement were not fully audited. The vendor's400/250MHz figures are inapplicable
as expected rates for our360/200MHz bench.

**Proposed check:** account for each output snapshot as produced, queued,
superseded, sent or still owned under consumer delay, while ensuring every VDP
command completes correctly. Separate presentation drops from game refresh
completion. Owner: P02/P06; no wholesale GMF adoption.

### C5 — Vectrex: useful sparse-work idea, weak handoff assurance

[Source][vectrex-code] places three descriptor slots in DRAM, uses VSYNC semaphore
wakeups, runs renderer on core0 and application/audio on core1. It compares old
and new vector lines instead of clearing whole framebuffers. These are useful
examples of reducing PSRAM work and separating producers from consumers.
The [README][vectrex-report] identifies IDF5.5.1 and360MHz/200MHz hardware; real
LCD/HDMI scanout differs from our output.

Caution from source inspection: `frame_slot_t.state` is volatile; the producer's
READY-to-FREE/reuse and consumer's READY-to-RENDERING operations in inspected
paths show no atomic claim or common critical section. That creates a plausible
cross-core ownership race requiring proof or correction before reuse. This is
not a reproduced failure. Picking the last READY array index also does not by
itself establish temporal newest-frame ordering. Deliberate discard and a
loop/VSYNC counter cannot establish every-frame rendering. No dedicated test
suite appeared in the inspected tree; reuse licensing remains unresolved.

**Proposed check:** on our own ownership model, verify exclusive claims and
monotonic frame IDs under slow-consumer pressure; keep VDP command ordering
intact. Owner: P02. Sparse drawing is an analogy, not authority to alter stock
rendering. Rank reduced despite the attractive demo.

## 4. Rejected or deferred leads

| Lead | Disposition and reason |
|---|---|
| [Espressif esp-amp][amp-report] | Genuine dedicated-core reference, but current P4 subcore lacks cache/XIP/PSRAM access and reserves internal memory. Architecture change far beyond ordinary FreeRTOS affinity. Defer, not a first experiment. |
| [ctag P4 FPU benchmark][fpu-report] | Explicitly disclosed AI-generated material. Independently of that, reported67MFLOPS combined and38 per core conflict arithmetically;32 versus41 is about22% lower, not29%. No trust in its broad hardware conclusions without rebuilding the methodology. Source retrieved, no execution. |
| [ESPHome P4 display performance issue](https://github.com/esphome/esphome/issues/16873) | Useful original integration report and source-change leads; LCD/RGB888/PPA is not our web path. Not an independently replicated solution for our jitter. |
| [Espressif MJPEG issue703](https://github.com/espressif/esp-iot-solution/issues/703) | Original reporter saw ~10fps instead of20 in particular scenes on rev1.0/IDF5.5.4. Shows why vendor examples need workload qualification; does not establish a shared cause. |
| P4 camera/ISP and ESP-VISION pipelines | Hardware DMA/scaling ownership references, but no closer software-drawing/streaming comparison found in this pass. Do not add camera dependencies. |
| P4 Car Audio DSP design, WLED/media demos, tgx-derived demos | Discovery leads not promoted: no equally persuasive inspected contention evidence in this bounded pass. This is not a judgment that these implementations are poor. |
| micro-vorbis | Similar diagnostic family; avoid mistaking its S3 dual-core table for a P4 result. micro-mp3 supplied the clearer P4 concurrency example. |

## 5. Evidence, provenance and review boundary

[Source ledger](CANDIDATE-SOURCES.json) pins repository revisions, selected file
hashes/URLs, commit dates and five-commit history samples. [Query ledger](QUERIES.md)
records discovery. Ignored local source copies contain no downloaded game ROMs,
media assets or executed sample code. No independent replication was established.
An API license label is not a complete licensing audit: micro-mp3/adapter carry
Apache identifiers, GMF inspected files use Espressif Modified MIT, and some
repositories have no top-level detected license. Review exact files before reuse.

This is a focused scout, not an exhaustive audit. Complete IRQ placement,
allocation chains, cancellation/error paths and performance on our board remain
unverified. The source URLs are pinned; latest documentation/search snippets are
only discovery aids. One guessed adapter benchmark README returned404 and was
not treated as evidence.

**Review requested:** select the next bounded diagnostic under QUAL-003, preferably
actual wait/memory attribution before architectural changes. No candidate build,
flash, benchmark, dependency upgrade or firmware test is authorized by this
writeup. The only hardware action for closure is the established spoken cue.

[mp3-report]: https://github.com/esphome-libs/micro-mp3/blob/07c18fa2d045b89bcc19aa0c1dc5333ce69b39db/examples/decode_benchmark/README.md

[mp3-code]: https://github.com/esphome-libs/micro-mp3/blob/07c18fa2d045b89bcc19aa0c1dc5333ce69b39db/examples/decode_benchmark/main/decode_benchmark.cpp

[mp3-tests]: https://github.com/esphome-libs/micro-mp3/blob/07c18fa2d045b89bcc19aa0c1dc5333ce69b39db/tests/conformance/README.md

[mp3-config]: https://github.com/esphome-libs/micro-mp3/blob/07c18fa2d045b89bcc19aa0c1dc5333ce69b39db/examples/decode_benchmark/sdkconfig.defaults.esp32p4

[mp3-platform]: https://github.com/esphome-libs/micro-mp3/blob/07c18fa2d045b89bcc19aa0c1dc5333ce69b39db/examples/decode_benchmark/platformio.ini

[lvgl-bridge]: https://github.com/espressif/esp-iot-solution/blob/6958385313b0e4fc1f3de259b1d677fca7d7d236/components/display/tools/esp_lvgl_adapter/src/display/bridge/v9/lvgl_bridge_v9.c

[lvgl-task]: https://github.com/espressif/esp-iot-solution/blob/6958385313b0e4fc1f3de259b1d677fca7d7d236/components/display/tools/esp_lvgl_adapter/src/adapter/esp_lv_adapter.c

[lvgl-report]: https://github.com/espressif/esp-iot-solution/blob/6958385313b0e4fc1f3de259b1d677fca7d7d236/components/display/tools/esp_lvgl_adapter/README.md

[lvgl-manifest]: https://github.com/espressif/esp-iot-solution/blob/6958385313b0e4fc1f3de259b1d677fca7d7d236/components/display/tools/esp_lvgl_adapter/idf_component.yml

[nina-screen]: https://github.com/chvvkumar/ESP32-P4-NINA-Display/blob/c7b34400f7373cad94caee7493413a8ec5b58864/main/web_handlers_display.c

[nina-perf]: https://github.com/chvvkumar/ESP32-P4-NINA-Display/blob/c7b34400f7373cad94caee7493413a8ec5b58864/main/perf_monitor.c

[nina-tests]: https://github.com/chvvkumar/ESP32-P4-NINA-Display/blob/c7b34400f7373cad94caee7493413a8ec5b58864/test/host/README.md

[nina-manifest]: https://github.com/chvvkumar/ESP32-P4-NINA-Display/blob/c7b34400f7373cad94caee7493413a8ec5b58864/main/idf_component.yml

[gmf-report]: https://github.com/espressif/esp-gmf/blob/4e477b7c5352a54e9a64cdafe3839abbaf143940/packages/esp_player/README.md

[gmf-bus]: https://github.com/espressif/esp-gmf/blob/4e477b7c5352a54e9a64cdafe3839abbaf143940/packages/esp_player/src/sync/player_data_bus.c

[gmf-sync]: https://github.com/espressif/esp-gmf/blob/4e477b7c5352a54e9a64cdafe3839abbaf143940/packages/esp_player/src/sync/player_sync.c

[gmf-tests]: https://github.com/espressif/esp-gmf/blob/4e477b7c5352a54e9a64cdafe3839abbaf143940/packages/esp_player/test_apps/main/test_scenario.c

[vectrex-code]: https://github.com/malbanGit/ESP32_P4_Vectrex/blob/caf2d9b77e1c9eaa5b7f8805fc0172650dbea051/main/main.c

[vectrex-report]: https://github.com/malbanGit/ESP32_P4_Vectrex/blob/caf2d9b77e1c9eaa5b7f8805fc0172650dbea051/README.md

[amp-report]: https://github.com/espressif/esp-amp/blob/e1b48925e7ef0f214f5465c1a0a2cb43446a7ffc/README.md

[fpu-report]: https://github.com/ctag-fh-kiel/esp32p4_fpu_benchmark/blob/df707faec5fd73a82ad2e358716f3c62a266239a/README.md

## C1 investigation status

[Source-only C1 report](C1/README.md) completes the authorized first investigation.
No immediate throughput fix established; Extender already has key ownership
mechanisms. Proposed wait attribution remains under P01c/d. Future MIPI utility
retained; no sample build/test. Await review before C2; RLE remains deferred.
