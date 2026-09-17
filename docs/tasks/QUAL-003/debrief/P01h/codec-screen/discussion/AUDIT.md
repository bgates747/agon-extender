# Gemini architecture cross-reference audit

## Executive summary

**Useful prompts, but not a usable specification or a newly discovered fix.**
The proposal models a monochrome framebuffer eight times smaller than ours,
provides unsafe snapshot/TCP-buffer ownership, and recommends PARLIO/GDMA that
we already implement. Its credible performance suggestions mostly duplicate
our existing, incompletely exercised research queue.

**The most useful remaining experiments are controlled TCP/IP affinity and
selected lwIP IRAM placement—not copying this architecture wholesale.** Neither
has a demonstrated win in the reviewed records. Correct no-copy transmission is
another possible experiment, but requires acknowledgement-based buffer lifetime,
not the supplied code. First reconcile the historical 29.18 fps RLE2 baseline
with the later 13–14 fps controls; do not optimize against an unexplained slowdown.

No firmware, graphics, transport, scheduling or configuration changes were made
for this audit. The fullscreen r05-derived playtest firmware remains installed.
This audit does not benchmark it or endorse a 60 fps claim.

## Contract and scope — 2026-09-17

1. [x] A01: Enumerate claims and establish actual format, memory, core placement,
   transport and selected SDK configuration.
2. [x] A02: Match claims against retained experiments/code and official sources.
3. [x] A03: Record errors, overlap, untested options and recommendations.
4. [x] A04: Hardware voice completed; fresh stage6/audio_commands=pass receipt verified. Normal Escape exited Nurples, startup readback unchanged, SD service exited. Left Legacy MOS prompt with fullscreen r02 installed. No flash/reset during audit. Human hearing not assumed.

Author requested this goal. Research only; Golem excluded. Existing dirty UI
work is preserved. The source attachment remains unedited. Nurples was running,
so the screen was not reset/cleared at the start merely to erase an old cue.
Notification will use admitted keyboard/CLI, not a firmware flash.

## 1. Claim-by-claim findings

| Supplied claim or recommendation | Project cross-reference | Assessment |
|---|---|---|
| 512×384 “1bpp” means 24,576 bytes | Browser protocol RGB222 stores **one byte per pixel**, 196,608 bytes before its 32-byte envelope. Six-bit packing would be 147,456 bytes. | **Wrong workload.** Its formula implements one **bit**, two colours; it cannot represent our 64-colour frame. Future 256-colour support also needs a byte per pixel. |
| 24 KiB fits internal SRAM, therefore PSRAM contention disappears | RESEARCH-001 `FINDINGS.md`/`LOCAL-FACTS.json`: game framebuffer already internal; snapshot slots explicitly PSRAM; assets and other buffers still consume memory. Selected L2 cache128 KiB. | **Already partly done; conclusion false.** 768 KiB physical HP L2MEM is not 768 KiB free application heap. Cache, code/data, stacks and DMA buffers consume the budget. Internal memory still has concurrent masters. |
| Copy complete frame in less than a microsecond | No measurement supplied. Our row composition/copy involves native graphics ownership, palette/sprites and immutable publication. P01e/P01f record millisecond wall times. | **Unsupported.** Even its24,576-byte copy in1 µs implies24.576 GB/s payload, roughly49.152 GB/s read+write traffic. At360 MHz that is68 bytes copied per CPU cycle. Do not treat this as a P4 capability measurement. |
| `memcpy` live framebuffer without a lock is a safe snapshot | `presentation_snapshot_pool.cpp`, `agon_screen.h`; P01f/A ownership audit | **Unsafe as specified.** Renderer can change pixels or mode/storage while copy proceeds; a memcpy is not an atomic frame capture. It also omits composition of sprites/palette/cursor. Existing row locking does not promise every snapshot is one logical application frame, but deliberately protects mutable native state. |
| `NETCONN_NOCOPY` plus a reused buffer is safe asynchronous streaming | Installed lwIP `tcp_out.c::tcp_write` retains caller memory until ACK; `api_lib.c` default netconn write is blocking unless configured otherwise. P01f/A already traced sockets using `NETCONN_COPY`. | **Unsafe lifetime and misleading async claim.** A write return is not proof that every byte was acknowledged. The next memcpy can overwrite queued/retransmittable data. A16 ms sleep is not ownership release. |
| Replace browser socket path with raw TCP8080 | Existing browser uses HTTP/WebSocket framing, negotiated codec and credit/backpressure. | **Not a browser replacement.** Ordinary webpage JS cannot consume this arbitrary raw TCP service. No geometry/palette/frame IDs, reconnection or mode-change contract is supplied. It could only be a separate diagnostic with a suitable host client. |
| Network exclusively core0, VDP core1 | P01f/A task map: parser/draw core0, snapshot core1, TCP/IP/HTTP/network dispatcher unpinned; selected TCP/IP priority18. | **Not current allocation; not a law of the chip.** Core0/1 roles are software policy. Merely pinning an app sender does not place lwIP, Ethernet RX/interrupts or other system tasks. Full exclusivity is not established. |
| Isolate networking to prevent rendering stalls | P01e recorded a25.210 ms native lock hold while TCP/IP occupied24.737 ms on the owner core; other core substantially idle. P02c specifically proposes TCP/IP affinity. | **Known, still worth a clean test.** Reviewed same-core snapshot priority2/4 experiments failed; snapshot priority19 also failed. Those do not prove every carefully chosen networking-affinity experiment fails. No evidence found of the exact full segregation plan passing. |
| Use `-O2` and1 kHz RTOS tick | Actual candidate sdkconfig: `CONFIG_COMPILER_OPTIMIZATION_PERF=y`, `CONFIG_FREERTOS_HZ=1000`. | **Already configured.** Gemini's `CONFIG_FREERTOS_TICK_RATE_HZ` is not the selected IDF symbol. A1 kHz tick is not inherently less overhead than a lower tick rate. |
| Disable hardware stack guard for speed | Guard enabled. SDK describes stack-pointer boundary fault detection; our RLE2 diagnostic actually caught a stack fault earlier. | **No measured benefit; do not adopt.** This is hardware protection, not evidence of a heavy software check on every operation. |
| Increase TCP send and receive windows to49152 | Actual send32768, receive5760; RESEARCH-001 already records tuning as an option. | **Untested exact setting, not a guarantee.** Correct keys end `_DEFAULT`. P4 receive window controls incoming data; browser receive window constrains outgoing video. Increasing memory limits does not eliminate congestion, queue or ACK waits. |
| IRAM networking and `LWIP_ICACHE_OPTIMIZATION` | IRAM disabled, already listed in RESEARCH-001. Installed IDF has `LWIP_IRAM_OPTIMIZATION` and `LWIP_EXTRA_IRAM_OPTIMIZATION`; no matching ICACHE option found. | **Real untested knobs plus an unsupported knob name.** SDK estimates about10 KiB and17 KiB IRAM, respectively; first option documents limited dual-core benefit. It is code placement, not guaranteed cache persistence. |
| UART at1,152,000 baud with4 KiB RX buffer | Current `console_hardware.inc` already does this, with RTS/CTS and stock-like receive timeout. | **Existing basics; supplied replacement regresses flow control.** Its placeholder pins are not our mapping. `uart_driver_install` last argument is interrupt flags, not allocator capability flags; `ESP_ALLOC_CAP_INTERNAL` was not found in selected SDK headers. |
| Avoid per-strobe GPIO ISR; use PARLIO+GDMA into SRAM | `forward_parallel_stream.cpp` uses8-bit external-clock PARLIO RX, VALID delimiter,64-byte DMA burst, internal DMA allocation. SDK `parlio_rx.c` connects GDMA. `p4_parallel_target.cpp` and AUDIT-001 retain earlier lineage. | **Already implemented, not a new discovery.** Legacy PRX evidence is historical; existence of code is not blanket qualification of every current parallel configuration. This is eZ80→P4 ingress, not P4→browser output. |
| DMA frees core1 exclusively for drawing | Receiver still arms transactions, handles completion, asserts/releases READY, validates and copies to a stream buffer; protocol processing remains CPU work. | **Overstatement.** DMA removes per-byte sampling, not all ingestion overhead, flow control or bus contention. |

## 2. Numerical sanity check

Payload only; excludes Ethernet/TCP/WebSocket overhead and acknowledgement traffic:

| Representation,512×384 | Bytes/frame | Payload at60 fps |
|---|---:|---:|
| Gemini monochrome1-bit |24,576|11.79648 Mbit/s|
| Packed6-bit colour (not current stream) |147,456|70.77888 Mbit/s|
| Current uncompressed1-byte colour |196,608|94.37184 Mbit/s|
| Representative RLE2 frame,37,647 bytes |37,647|18.07056 Mbit/s|

Raw byte-per-pixel60Hz leaves little100-Mbit link margin. RLE2 changes that budget
substantially; it does not prove CPU/snapshot/scheduling costs are low enough.
The historical29.18 fps result and24.55 fps60-cycle run remain valid scoped
observations. Later13–14 fps controls must not silently replace those as our
platform ceiling. No new network or timing measurement was taken here.

`vTaskDelay(16 ms)` adds delay after work; it is not a60Hz deadline schedule.
Ignoring work entirely it suggests62.5Hz. Use explicit elapsed/deadline accounting
when designing a test; don't infer a measured rate from a sleep constant.

## 3. What is actually new or unfinished?

| Avenue | Novelty / evidence | Disposition |
|---|---|---|
| Separate TCP/IP task affinity, with all actual actors traced | Already explicit P02c; exact bounded treatment not completed in reviewed evidence | Keep existing owner, no duplicate task. First recover comparable baseline, then vary one owner at a time. Swapping all cores simultaneously would obscure attribution. |
| lwIP IRAM / extra TCP IRAM | Already explicit RESEARCH-001 candidate; selected build leaves disabled | Eligible measured follow-up after baseline, checking internal heap/largest block and actual code placement. Not a predicted fix. |
| Correct no-copy TCP lifetime | Copy path was already identified; no completed ACK-owned no-copy experiment found | Newly concrete experiment candidate from this conversation, **not** supplied implementation. First measure copy cost; design bounded immutable buffers, ACK/retransmission/error ownership and browser-compatible framing. Do not abandon supported socket APIs casually. |
| Internal snapshot storage | Memory placement already researched; current allocator still PSRAM | Existing unresolved experiment. Budget196,608 bytes per slot, plus renderer/codec/network memory; no promise a complete internal pool fits. |
| Exact49,152-byte send queue | Exact value not found as completed current game trial | Low-priority member of existing socket-tuning avenue; control byte workload and RTT, not a magical two-frame constant derived from monochrome. |
| PARLIO/GDMA | Present in code and historical evidence | No new architecture work warranted by this text. Follow existing parallel qualification contracts when that work resumes. |

**Recommended order:** (1) reconcile r05 versus later RLE2 results using identical
firmware/fixture/browser/boot/receiver conditions; (2) if long lock-owner preemption
remains, complete the existing narrow affinity investigation; (3) test targeted
IRAM/memory placement against a stable control; (4) only pursue no-copy or queue
size work if measured copy/send costs justify it. These are recommendations, not
authorization for new hardware experiments. Do not restart codec sweeps from this
conversation.

## 4. Evidence and primary sources

Local references are relative to repository root unless stated otherwise:

1. `docs/tasks/RESEARCH-001/FINDINGS.md`, especially §2 local facts and its existing
   targeted affinity/IRAM/socket recommendations; `C1/MEMORY.md` on lifetimes.
2. `docs/tasks/QUAL-003/DEBRIEF-PLAN.md`, P02c and its unexecuted scheduling gate.
3. `docs/tasks/QUAL-003/debrief/P01e/README.md` and
   `P01f/A/{OWNERSHIP,FINDINGS}.md`, `P01f/W/TABLES.md`: measured scheduler events,
   copy path and rejected treatments, not hypothetical diagrams alone.
4. `vdp/video/extender/transport/{forward_parallel_stream.cpp,p4_parallel_target.cpp,console_hardware.inc}`;
   `network/wired_network_service.cpp`: actual PHY is **IP101GRI**, not the
   supplied LAN8720. No alternative pin assignments were applied.
5. `vdp/video/extender/display/presentation_snapshot_pool.cpp` and installed
   candidate source `video/agon_screen.h`: immutable leases and PSRAM allocator.
6. Private retained candidate02 build cache provides the selected r05/r06 lineage
   sdkconfig and generated config header: IDF5.5.5,360MHz,1000Hz. Current fullscreen
   build retains r05 credit timing; no claim of a newly qualified performance rate.
7. Selected SDK under `vdp/.pio/packages/framework-espidf/`:
   `components/lwip/{Kconfig,lwip/src/core/tcp_out.c,lwip/src/api/api_lib.c}`;
   `components/esp_driver_uart/include/driver/uart.h`;
   `components/esp_driver_parlio/src/parlio_rx.c`;
   `components/esp_system/Kconfig`. These settle exact selected-version API and
   configuration semantics, rather than copying latest online API additions.
8. [Espressif lwIP guide,5.5.2](https://docs.espressif.com/projects/esp-idf/en/v5.5.2/esp32p4/api-guides/lwip.html):
   BSD sockets supported; netconn enabled but not officially supported for IDF
   applications. This matters to the proposed replacement, not just performance.
9. [Espressif PARLIO RX guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/parlio/parlio_rx.html):
   external clock/valid, GDMA, transaction lifetime and callbacks. Online stable
   currently resolves to6.1; use installed5.5.5 source for our exact implementation.
10. [Official P4 datasheet](https://documentation.espressif.com/esp32-p4_datasheet_en.html):
    HP memory/cache, multicore and DMA capabilities. Physical memory capacity is
    not runtime free heap. Consult board/driver source for actual PHY selection.

Research accessed2026-09-17. No claim that this audit proves every old experiment
was found or every proposed setting was tested; “not found” remains bounded to
reviewed project records. The supplied snippets were reviewed, not compiled or run.
