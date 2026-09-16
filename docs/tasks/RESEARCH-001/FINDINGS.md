# P4 timing variability — internet research findings

## Executive summary

**No confirmed upstream defect was found that explains all of P02.** The search
found relevant P4-specific faults and documented mechanisms, but their triggers
must be checked rather than treated as our diagnosis. The most useful outcome
is a more precise investigation order: actual task/core and lock behavior,
PSRAM snapshot/cache effects, then socket/credit pacing. Firmware is unchanged.

Two facts sharpen the previous report:

1. **Internal framebuffer does not mean internal output buffers.** The selected
   stock-runtime constructor explicitly allocates snapshot slots in PSRAM.
   Thus their memory class is established by source, rather than unresolved;
   actual addresses/alignment/cache interactions remain unmeasured.
2. **“Async” does not mean the HTTP send task immediately returns.** Espressif
   confirms that the WebSocket API executes its sends in the caller; our queued
   work runs there and uses a complete-send override. Network wait time and
   runnable CPU time must be distinguished. [Espressif clarification](https://github.com/espressif/esp-idf/issues/9250).

| Existing measurement | Mainboard | P4 | Meaning |
|---|---:|---:|---|
| Software-sprite refresh spacing p95 | 17.063 ms | Normal 29.238 ms | Existing streamed tail, +71.35% |
| Composition-only spacing p95 | Same reference | 17.318 / 45.509 ms | Contradictory repeats; transmission is not the sole established explanation |
| Prebuilt transmission spacing p95 | Same reference | 25.026 / 21.428 ms | Tail exists without native composition |
| Full-frame socket scope mean | No equivalent measured | 17.082–17.702 ms | Wall time including waits; not exclusive CPU rendering cost |
| Normal/prebuilt sends in game window | Not applicable | 27.360–29.184/s | Separate from roughly60 refresh completions/s |

These are retained [P02 results](../QUAL-003/debrief/P02/TABLES.md), **not new
measurements**. The slow discard run averaged52.551 completions/s; other accepted
runs were near60. An initial pixel-query failure remains a separate reliability
observation. No Rally, hardware-sprite or Golem work was added.

### Recommended first avenues — agent recommendations for review

| Order | Investigation | Why it now has priority | Discriminating evidence |
|---|---|---|---|
| 1 | Repeat discard/normal with explicit P4 boot identity; record task affinities, effective priorities and native-lock wait/hold time | Discard variance prevents attribution; source creation affinity need not equal observed runtime state | Correlate slow refresh admission with runnable/blocked tasks and lock ownership; retain hashes/pixels |
| 2 | Record snapshot addresses, alignment and placement; separate row preparation, normalization and lock wait | Snapshot buffers are PSRAM despite internal game framebuffer; P4 cache is128KiB versus192KiB frame | Determine whether slow repeat spends time executing memory work or waiting/preempted; compare a matched-rate control |
| 3 | Trace HTTP queue, socket send and client-credit intervals on wired receiver | Prebuilt delivery remains roughly28–29/s; complete send is17–18ms | Packet/ACK timestamps and phase trace distinguish serialization, blocked send, scheduling and browser cadence |
| 4 | Only then select one affinity, targeted IRAM/cache, or socket-option experiment | Official advice describes tradeoffs, not a universal setting | One variable, same bytes/work, repeated baseline and rollback; no bundled tweaks |

This refines P02/P01c and P06; it does not create duplicate implementation work.
AUDIT-007's exhaustive FabGL audit remains required and unscheduled. Further
hardware experiments require the next agreed contract. No upgrade, cache flush,
priority change, protocol replacement or renderer modification was performed.

## 1. Search scope and evidence discipline

Searched P4 Ethernet/WebSocket throughput, graphics contention, PSRAM/cache,
SMP/affinity, clock/timer faults, errata, USB logging, and reset-dependent behavior;
then expanded to IDF/Arduino socket and FreeRTOS synchronization behavior. See
[query ledger](QUERIES.md). Technical conclusions rely on official documentation,
maintainer statements, source or original issue reports. An issue reporter's
claim is not a confirmed vendor diagnosis. Search-result similarity is not proof.

Access:2026-09-16 UTC, local evening September15. The selected build uses IDF5.5.5,
Arduino3.3.11 and retained boot reports P4 v1.3. Some versioned web pages failed
to load; current documentation is explicitly labelled below, with local5.5.5
source checks where material. Dynamic pages can change after this review.
No release note was found establishing an exact fix for our symptoms.

## 2. Exact local applicability

[Machine-readable facts and source hashes](LOCAL-FACTS.json) identify r45 and
its compiled configuration, not merely defaults from an unrelated installation.

| Item | Selected value/evidence | Implication |
|---|---|---|
| IDF / Arduino | 5.5.5 / 3.3.11; build metadata and retained boot | Matches the published [Arduino release pairing](https://github.com/espressif/arduino-esp32/releases/tag/3.3.11) |
| CPU / RTOS tick | 360MHz /1000Hz | Do not compare directly with400MHz examples or100Hz issue reproduction |
| Dynamic power management | `PM_ENABLE=false` | Automatic power scaling is not the first explanation |
| PSRAM | 200MHz, confirmed by retained boot | Known80MHz Arduino regression does not match |
| L2 cache | 128KiB,64-byte line | A196608-byte output frame exceeds L2 capacity; this is not itself a proven thrashing diagnosis |
| Framebuffer | Internal for all accepted game runs | Does not locate assets or output slots |
| Output snapshot allocation | `agon_screen.h::updateVGAController`, explicit `MALLOC_CAP_SPIRAM`, no internal fallback | Memory class known; allocation addresses not recorded |
| lwIP | Priority18, no configured affinity; send buffer32768, receive window5760 | Own receive window is not the receiver's window for outbound frames |
| HTTP / network worker | Priority5 unpinned / priority3 unpinned at creation | Different execution actors; don't pin the wrong one |
| Ethernet/lwIP IRAM options | Disabled | Potential measured experiment, not permission to consume scarce internal RAM blindly |
| Flash | Retained boot QIO80MHz; no PSRAM XiP | Compiled config has a conflicting derived `FLASHMODE` string; prefer verified boot evidence, investigate before changing build flags |

The `AGON_EXTENDER_INTERNAL_POOLS` option targets native renderer allocations;
it does **not** relocate snapshot slots. Source establishes the latter directly.
The native row guard is a recursive FreeRTOS-backed mutex, not an interrupt-off
spinlock across the whole frame. Separate snapshot pool transition guards and
network dispatch synchronization must not be conflated with that mutex.

## 3. P4-specific findings

### 3.1 Known Arduino PSRAM-speed regression — ruled down

[Arduino issue11651](https://github.com/espressif/arduino-esp32/issues/11651),
opened July26,2025, reports P4 core3.3.0 using80MHz PSRAM rather than200MHz.
[Lib-builder PR310](https://github.com/espressif/esp32-arduino-lib-builder/pull/310)
merged July29,2025 to enable200MHz configurations. Our compiled value and boot
both show200MHz. Do not prescribe this old fix or an SDK upgrade as the answer.
The report is useful chiefly as a reason to check actual boot/configuration.

### 3.2 Cache/memory contention — plausible, not established

The versioned [IDF5.5.5 external-RAM guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-guides/external-ram.html)
warns that bulk external-memory access can exhaust cache benefits and evict
cached instructions. It also describes allocation preferences and memory
restrictions. Its generic size example is not a measured threshold for our
configured128KiB P4 cache.

The [current P4 speed guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-guides/performance/speed.html)
describes the speed/internal-RAM tradeoff of larger cache and targeted IRAM.
Our192KiB PSRAM snapshots make this relevant even with an internal framebuffer.
It could contribute in both discard and transmission cases, but cannot by
itself explain why the identical discard workload differs so much between runs.
Measure before changing cache size; extra cache can displace the internal
allocations that made earlier candidates faster.

### 3.3 PPA/DSI contention reports — analogous resource sharing, different path

[LVGL issue9590](https://github.com/lvgl/lvgl/issues/9590), January14,2026,
reports P4 DSI underruns under heavy PPA load, with reduced burst length resolving
that reporter's case; it is closed via9612. Our web-output path uses neither
PPA nor physical DSI scanout. This is evidence that P4 graphics consumers can
contend for shared resources, **not** a transferable fix or explanation of our
framebuffer rendering. Do not apply its burst setting to an unused engine.

### 3.4 Flash stalls — credible mechanism, no observed trigger

[P4 issue18846](https://github.com/espressif/esp-idf/issues/18846), July14,2026,
requests flash auto-suspend support and reports cache/PSRAM problems during flash
operations on v1.3. It remained open/in progress when read. Official interrupt
and external-memory guidance independently documents flash-write/cache effects.
Our timed fixture does not intentionally write P4 flash; mainboard SD traffic
is not a P4 flash erase. First prove a flash/NVS operation overlaps a stall.
Do not enable auto-suspend merely because a Kconfig option is selectable.

### 3.5 Timer regression report — keep as measurement cross-check

[P4 issue18899](https://github.com/espressif/esp-idf/issues/18899), July29,2026,
reports non-monotonic `esp_timer_get_time()` and watchdog events on v1.3/IDF5.5.4,
with power management disabled and100Hz ticks. It was open, without a verified
fix established by this review. Same silicon revision is relevant, but the
reported large backwards jumps/watchdogs differ from our finite pacing tails.
Cross-check P4 elapsed time with MOS/host/wire time and reject discontinuities;
do not dismiss the slow discard run as a clock bug without evidence.

### 3.6 Silicon errata and transport-specific failures — not an exact match

The [official P4 errata index](https://documentation.espressif.com/esp-chip-errata/en/latest/esp32p4/index.html)
separates revision-specific DMA/MSPI/APM faults. Its v3.x memory-access items
must not be assigned to our v1.3 just because their titles mention PSRAM.
No documented generic25–45ms pacing fault was identified there. Any proposed
erratum workaround must first match revision, access path and trigger.

[IDF18798](https://github.com/espressif/esp-idf/issues/18798) reports completely
nonfunctional EMAC TX on v1.0, unlike sustained valid traffic here.
[ESP-Hosted197](https://github.com/espressif/esp-hosted-mcu/issues/197) concerns
P4/C6 SDIO exhaustion, unlike our wired EMAC output. Neither is evidence against
our wiring, nor a reason to change a working transport.

## 4. Broader IDF/Arduino mechanisms

### 4.1 Actual scheduling, runtime affinity and priority inheritance

The [current IDF SMP guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/system/freertos_idf.html)
(resolved to6.1) describes core-constrained scheduling and automatic pinning
on FPU/PIE use. The local5.5.5 RISC-V port's coprocessor cleanup and its FPU
unit test corroborate the pinning contract; this is not merely Xtensa folklore.
**No evidence yet shows our HTTP or lwIP task executes such instructions.**
Inspect runtime affinity and call paths before saying an unpinned-at-creation
task actually migrated or unexpectedly became pinned.

[Official interrupt guidance](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/system/intr_alloc.html)
explains allocation-core ownership. Moving a task after driver initialization
does not by itself relocate its interrupts. The P02 HTTP/lwIP/RX/ISR inventory
therefore remains necessary for a defensible core-isolation experiment.

The [FreeRTOS kernel book](https://github.com/FreeRTOS/FreeRTOS-Kernel-Book/blob/main/ch08.md)
describes priority inheritance and its limitations with multiple held mutexes.
This is a reason to record effective priorities and lock ownership. It is not
proof that our recursive mutex is buggy, nor that replacing it with a semaphore
would help. Same-address/shared-memory serialization also survives core isolation.

### 4.2 Official P4 Ethernet benchmark is not a mixed graphics prescription

The [versioned5.5.5 P4 iperf configuration](https://raw.githubusercontent.com/espressif/esp-idf/v5.5.5/examples/ethernet/iperf/sdkconfig.ci.default_ip101_esp32p4)
uses single-core execution and Ethernet/lwIP IRAM options for an isolated
throughput benchmark. Its own comments warn that a mixed application may benefit
from multicore responsiveness. It also disables watchdogs; **do not import that
configuration wholesale**. Use its workload as a P06 reference, preserve safety
and report configuration differences. This directly argues against assuming
that either “use both cores” or “put networking on one core” is universally best.

### 4.3 WebSocket send semantics, supported API and TCP pacing

The [Espressif maintainer response in9250](https://github.com/espressif/esp-idf/issues/9250)
confirms the misleading async name refers to usage outside the request, not
an immediately returning transport operation. Our `httpd_queue_work` use follows
that pattern. The selected send function sends the WS header and payload
separately; our override loops until each segment is complete or fails.
A17ms measured scope includes socket blocking and preemption, not17ms CPU burn.

The [IDF5.5.5 lwIP guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-guides/lwip.html)
supports BSD sockets, task-affinity tuning and `TCP_NODELAY`; raw lwIP/Netconn
are not a generally supported shortcut for application code. Our project does
not explicitly set `TCP_NODELAY` on the video socket in the inspected path.
That does not establish its runtime value or prove Nagle/delayed-ACK stalls.
Check socket options and capture packet/ACK timing before trying a one-option
control. Small headers/credit traffic are more relevant to that hypothesis
than bulk payload alone. It cannot explain the no-send discard slowdown.

[IDF14495](https://github.com/espressif/esp-idf/issues/14495) reports corrupt
WebSocket frames from concurrent calls on ESP32-S3/5.3.0. Our queued sender
serializes dispatch and retains full-frame correctness checks. Keep that
constraint; this report is not a match for valid but uneven delivery.

### 4.4 Throughput arithmetic and browser credit are separate from rendering

One frame has196608 payload bytes plus32EVF bytes. At a hypothetical100Mbit/s
link, those bytes alone occupy15.7312ms, before Ethernet/IP/TCP/WS overhead.
The17–18ms send scope is therefore compatible with substantial line service,
although socket acceptance can overlap actual transmission and this arithmetic
**does not measure negotiated speed or wire utilization**. The wired Pi's1Gb/s
link is not the P4's link speed.

Across the actual game windows, sends correspond to about43.0–45.9Mbit/s of EVF
bytes. A gap between active-send capacity and whole-window output can arise
from generation, dispatch, credits and receiver presentation. Our browser grants
credit after presentation via its animation loop. A roughly30FPS result could
reflect cadence interaction; no evidence yet establishes a fixed two-refresh
limit. Trace credit arrival/dispatch/send completion/presentation timestamps
before altering credit policy. This belongs to existing P06, not a new protocol.

### 4.5 Logging, heap and DMA checks: useful exclusions, not free fixes

The official speed guide warns that logging can block and that short timings
can depend on cached code layout. P02 dumps its large traces after gameplay,
but retains periodic service logging. A diagnostic run should identify those
writes rather than assume zero observer cost. Cache-counter or task tracing
must itself be measured against an unchanged normal control.

[Current P4 memory-synchronization guidance](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/system/mm_sync.html)
explains CPU/DMA visibility requirements. This is not a mandate to flush cache
on every CPU-to-CPU buffer handoff. The stock EMAC driver owns its DMA path;
prove a missing coherency boundary before touching it. Pixel-correct timing
variance is less suggestive of stale DMA contents than a reproducible corruption.

## 5. Disposition and next contract

Research completed without a demonstrated drop-in fix. Preserve both bad and
good repeats. The next proposed tranche should refine P02c/P01c, not launch an
unbounded tuning sweep: one matched boot/order matrix, actual task/lock state,
known PSRAM output placement and unchanged correctness gates. Choose a single
intervention only after those observations discriminate the hypotheses. P06
already owns socket/protocol/receiver experiments; AUDIT-007 owns broad FabGL
coverage. No blanket dependency upgrade, watchdog disable or speculative flush.

The retained r43 firmware, startup and MOS state remain unchanged by research.
Hardware voice notification and its fresh receipt are recorded separately.

## Implementation scouting extension

The Author-requested follow-up is in [CANDIDATES.md](CANDIDATES.md): five ranked
P4 source candidates, discussion rationale, caveats and proposed discriminating
checks. This extends discovery beyond HTTP; it does not replace this causal
assessment or authorize firmware experiments.
