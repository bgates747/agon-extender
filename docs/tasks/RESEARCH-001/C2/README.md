# C2 — micro-mp3 concurrency benchmark review

## Executive summary

**Retain the measurement pattern, not the harness unchanged or its causal
conclusion.** Independent worker state, per-call timings and separate setup
accounting are useful. But three/four workers oversubscribe two cores, so their
slowdown cannot establish PSRAM/bus contention. Elapsed decode time includes
preemption; it is not exclusive CPU execution. No Extender fix follows directly.

The source review also found a concrete harness failure-path problem: successful
task creations are counted, but result reporting assumes they occupy contiguous
slots from zero. An earlier creation failure followed by a success can read an
uninitialized result and omit a real result. Even total creation failure need
not set the overall success flag false. No failure was reproduced on hardware;
no upstream code was changed.

**Recommended avenue:** if later authorized under P01/P02, reuse our deterministic
workload with precreated workers, a common release barrier, explicit successful
worker IDs, output verification and bounded timing records. First compare one
worker on each core separately against two concurrent workers. Only then vary
memory placement while holding work fixed. C3 is next for source review, pending
Author approval. No new FPS/ms measurements, build, flash, reset or benchmark.

## 1. Baseline and reported performance

Contract26b1dea; upstream commit
`07c18fa2d045b89bcc19aa0c1dc5333ce69b39db`. Source hashes in
[provenance.json](provenance.json). Scope is benchmark harness/configuration and
conformance documentation, not a decoder arithmetic or full library audit.

Publisher's rounded P4 elapsed totals, milliseconds, each job decodes30seconds
of audio. These are not Agon measurements and not per-frame rendering latency.

| Work per job | One job | Two concurrent jobs | Three jobs | Four jobs |
|---|---:|---:|---:|---:|
| 320kbps clip | 1800 | 1800 | 3700 | 4100 |
| 128kbps clip | 1500 | 1500 | 3000 | 3200 |
| 64kbps clip | 1200 | 1200 | 2300 | 2500 |

Source: pinned [benchmark report][report]. Two jobs approximately double useful
throughput in the rounded results; they also double completed work. This is not
a mainboard-versus-Extender speedup. P4 defaults request360MHz CPU/200MHz hex
PSRAM; clocks resemble ours, but PlatformIO selects54.03.20 and a different
board. Exact compiled configuration, cache layout and SDK equivalence to our
IDF5.5.5 baseline are not established. No independently reproduced distributions
or raw P4 logs accompany this review.

## 2. What the harness actually measures

| Mechanism | Source behavior | Consequence for reuse |
|---|---|---|
| Worker state | Separate decoder, PCM buffer and result per worker; shared read-only input | Useful separation, but shared input/cache is unlike all graphics/network workloads |
| Start | Sequential task creation, alternating cores, priority1 | No common start barrier; startup skew and core asymmetry are unmeasured |
| Per-call timer | esp_timer_get_time around decode; aggregate only calls producing samples | Includes interruptions/preemption; excludes nonproductive calls from frame statistics |
| Run timer | Starts after PCM allocation, ends before its free; setup split after header probe | Not full allocation-to-destruction cost; decode remainder includes yields/bookkeeping and interruptions |
| Group timer | Starts before creation, ends after completion semaphore takes | Includes startup and worker start/finish logs; not pure decoding |
| Completion | Counting semaphore, then task self-deletion | Completion signal is not proof idle-task reclamation of task storage has finished |
| Memory | PCM uses MALLOC_CAP_DEFAULT, decoder lazy initialization; heap delta only for solo worker | Requested default capability is not actual placement; background allocations can still contaminate solo delta |
| Statistics | Count/min/max/mean/stddev, no retained per-call series | Cannot reconstruct p95/p99 or align stalls across workers |
| Correctness | Errors/samples inspected; output overwritten for next frame, no reference hash in timed harness | A success flag does not establish identical output under concurrent load |

Source: `examples/decode_benchmark/main/decode_benchmark.cpp`, specifically
`decode_full_file`, `decode_task`, and `app_main` in [pinned source][code].
Official [timer documentation][timer] describes time since timer initialization,
not task CPU time; stable HTML resolves to6.1. Installed5.5.5 header
`components/esp_timer/include/esp_timer.h` independently confirms that timebase.

The separate conformance harness compares reference PCM with numerical bounds;
its README explicitly distinguishes its gate from full ISO conformance. It is
not invoked by this concurrency benchmark. No audio/reference assets downloaded.

## 3. Findings and limits before borrowing code

1. **Creation-failure accounting defect:** `results` is uninitialized automatic
   storage. `tasks_created` counts successes, then the reporting loop reads
   `results[0..tasks_created-1]` rather than actual successful IDs. Failure to
   create task0 followed by successful task1 makes that loop inspect result0.
   The creation error branch does not mark `all_success=false`. Treat any creation
   failure as invalidating the comparison; this is a source finding, not a
   claimed explanation of the published successful runs.
2. **No bounded liveness guard:** semaphore waits use portMAX_DELAY. The input
   loop has no general positive-status/zero-progress limit. Whether that case
   is reachable requires decoder/API analysis; it is not asserted as a decoder
   bug. A reused unattended diagnostic needs durable progress and an explicit
   abort/report contract, not a silent indefinite collector.
3. **Logging can perturb other workers:** start/finish logs fall within group
   time, and one worker can finish/log while another is still timed. Recoverable
   decode errors can log inside the run. Store records and report after the
   measured interval for our comparisons.
4. **Memory deltas are not ownership tracing:** solo measurement avoids competing
   decoder allocations, but not every other system allocation/free. Boot minima
   accumulate across all iterations; they are not per-case peaks. Allocator
   placement, task reclamation and warm cache/order effects need controls.
5. **Bus claim is underdetermined:** fixed ascending1/2/3/4 order, oversubscription
   and yielding conflate scheduling and memory effects. One worker on core1
   alone is missing. Internal/PSRAM contrasts are not shown in the published
   table. Do not relabel wall-clock stalls as cache misses.

These findings do not justify editing upstream or disqualify its decoder. They
limit this harness's use as a causal performance instrument.

## 4. Local comparison and smallest proposed experiment

Our existing P02 controls already separate composition-only, prebuilt network
sending, full streaming and output-off. Keep those controls and their state
oracles; do not replace them with an MP3 throughput demo. The variable discard
repeat remains evidence that network sending alone is insufficient to explain
all observed tails. C2 adds a method, not evidence resolving that variation.

Under existing P01/P02 ownership, the smallest later diagnostic would hold
input size/bytes/operation count fixed and compare solo core0, solo core1 and
paired workers, with all allocation/warm-up complete before a common barrier.
Record worker start/end skew, completed work, timing distributions and verified
output. Keep startup/teardown and logging outside the timed interval. Use the
same CPU/memory clocks, placement, repeat/boot conditions and per-worker state.
Only after that control change internal/PSRAM placement, one variable at a time.

Wall elapsed time must remain separate from task running time, lock waits and
runnable delay. A placement-dependent slowdown would motivate further cache/
memory investigation, not by itself prove a bus bottleneck. Aggregate overhead
needs a probe-off control. There is no authorization to build this diagnostic
in the present source-only review. RLE remains deferred until C1–C5 dispositions.

## 5. Closeout and notification

Mainboard clear command VDU12 was emitted through freshly admitted native CLI
at the start; input completion is not independent visual readback. Standing
start-clear/end-voice protocol recorded in project guidance and the task history.
No firmware changes; accepted hardware voice closeout recorded separately.

[code]: https://github.com/esphome-libs/micro-mp3/blob/07c18fa2d045b89bcc19aa0c1dc5333ce69b39db/examples/decode_benchmark/main/decode_benchmark.cpp
[report]: https://github.com/esphome-libs/micro-mp3/blob/07c18fa2d045b89bcc19aa0c1dc5333ce69b39db/examples/decode_benchmark/README.md
[timer]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/system/esp_timer.html
