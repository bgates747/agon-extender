# Official-source audit supporting the overnight debrief

## Executive summary

Official documentation supports investigating receive/parser scheduling, return
packet service and snapshot/network interference before changing rasterizers.
It does **not** establish which task caused the recorded stalls. The installed
candidate uses ESP-IDF5.5.5; general SDK contracts below use official5.5-family
pages, with installed5.5.5 source/configuration checked where material. No
upstream files were changed and no hardware experiment ran for this audit.

## 1. Reference identities and boundaries

| Reference | Verified local revision | Role |
|---|---|---|
| Official agon-vdp |v2.16.0, c7ac293d2aa81ddfa693390549bcd909069c8fc3|Stock parser/graphics behavior|
| Official agon-mos |v3.0.2, 8336409351ee5314e02801a7b72a4f1bb5282519|Clock and SAVE behavior|
| Official agon-docs |f9806bd3cbff6ed5d1c08bef1d51fed11764b86b|VDU/sprite/buffer contracts|
| Mainboard diagnostic's vdp-gl |ac2dd598, pinned in mainboard-refresh-build.json|Matched primitive completion hooks|
| P4 SDK |ESP-IDF5.5.5, pinned dependencies.lock and installed version.cmake|Driver/RTOS implementation|
| Overnight final candidate |uart-excom-console-r44-b2026-09-15-17-06-32Z|Diagnostic installation, not production promotion|

The three official Agon checkouts are clean. Tags above describe the selected
baseline; this audit does not claim they are the latest releases on the web.
P4 build provenance is in ../nurples-parity/results/native-wait-r44-build.json
and its retained source snapshot. The compiler flags actually linked into a
candidate take precedence over repository defaults and incomplete compile databases.

## 2. Agon commands, queues and clocks

1. [Official bitmap/sprite API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Bitmaps-API.md)
   distinguishes software sprites from scanline-composed hardware sprites.
   The latter require RGBA8888/RGBA2222, and command15 explicitly refreshes
   sprites. Local Nurples reference assets are RGBA2222. The name does not
   mean a separate P4 GPU draws them: the retained controller composes rows
   in CPU code. A RefreshSprites completion is not proof of every hardware
   sprite row being presented.
2. [Official buffered commands](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Buffered-Commands-API.md)
   define buffer65535 WRITE as consume/discard. The recorder's nonce markers
   use that stream safely; diagnostic hooks are not a production VDU extension.
3. [Official VDU commands](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDU-Commands.md)
   and [VDP vdu.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h)
   show mode-information replies on text/graphics cursor and viewport changes.
   These replies are part of retained behavior; do not delete them to make
   a benchmark faster. The return stream contains far more than explicit queries.
4. [MOS interrupts.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/interrupts.asm)
   increments the clock by2 at each VBLANK. At nominal60Hz this is120counts/s,
   but successive readings normally change in steps of2: effective16.67ms
   granularity, not a1ms performance timer. Human wall time previously disagreed
   with a long-suite tick conversion. Do not silently calibrate it from its
   historical centisecond label.
5. [MOS mos.c](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c)
   retains create-new SAVE semantics. The initial fixture's unchecked save
   caused stale results; fresh nonce plus checked file replacement is mandatory.
6. Stock `video/vdu_sys.h::sendScreenPixel` waits for drawing completion via
   `video/agon_screen.h::waitPlotCompletion(false)`. That foreground drain
   changes execution/pacing when used every frame. Current explicit-refresh
   traces run the regular worker and dump only after the terminal fence.
7. Retained `vdp/vendor/vdp-gl/src/displaycontroller.cpp::execPrimitive` handles
   RefreshSprites by hide/show, then the optional completion hook. Its native
   lock is acquired **before** the old Primitive timing scope; `showSprites`
   likewise locks before its SoftwareSprites scope. Execution aggregates do
   not account for all lock acquisition or queue waiting. Empty showSprites
   calls need not redraw: `m_spritesHidden` guards the work.
8. Retained `vga64controller.cpp::ISRHandler` prepares two rows per interrupt
   (`VGA64_LinesCount=4`), and notifies drawing at vertical sync. P4 uses a
   timer-driven drawing task and demand-driven snapshots; there is no physical
   VGA blanking interval in its web path. Copy original row logic, then qualify
   the target-specific scheduling separately.

## 3. Espressif scheduling and timing

[IDF FreeRTOS5.5 for P4](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/system/freertos_idf.html)
describes priority-preemptive SMP scheduling constrained by affinity. An
unpinned ready task may preempt either eligible core; the two highest-priority
tasks need not run together. Shared memory access still contends. A task that
keeps running does not give a lower-priority task execution merely because it
has reached another loop iteration. This supports, but does not prove, the
r35 starvation interpretation. Same-core output changes already failed; do not
repeat them without a new discriminating measurement.

[IDF speed guidance5.5](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-guides/performance/speed.html)
lists timer priority22, event-loop20, TCP/IP18 and default Ethernet RX15.
[IDF lwIP5.5.5](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-guides/lwip.html)
identifies the TCP/IP task and configurable affinity. These are reasons to
measure ready-but-not-running intervals and actual task placement, not reasons
to raise the parser above the network stack blindly.

Verified candidate configuration/source:

| Actor | Priority | Affinity | Evidence/qualification |
|---|---:|---|---|
| ESP timer task |22|Core0|esp_task.h; candidate sdkconfig|
| lwIP TCP/IP |18|No affinity|candidate sdkconfig; esp_task.h|
| Drawing worker |5|Core0|stock_p4_service.cpp; build/link checks|
| VDP parser/UART owner |3|Core0|video.ino processLoop creation|
| Project network worker |3|No explicit affinity|wired_network_service.cpp uses xTaskCreate|
| Snapshot producer |2|Core1|r44 build options, stock_p4_service.cpp|
| USB library/driver |6/5|Source permits unpinned work|input/p4_usb_host.hpp; live placement not measured|
| Ethernet MAC RX |15 default|SDK/driver dependent|Official default only; runtime task placement not captured|

Ethernet RX's documented default is **not a live task census**. Review the exact
Arduino component selected by the build before asserting its final affinity;
a similarly named globally installed framework need not be that component.
Candidate CPU is360MHz, power management disabled, FreeRTOS tick1000Hz.
Task trace/runtime-statistics options are disabled. Their absence means we do
not currently have a scheduler trace to blame lwIP. The r44 native guard times
elapsed acquisition, including preemption, and deliberately excludes foreground
mutex acquisition, UART driver locks, remote-input locks and lock hold time.

[ESP Timer5.5](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/system/esp_timer.html)
provides microsecond time and task-dispatched callbacks; callbacks can be delayed
by other execution and should remain short. Inspect deadline-to-callback and
callback-to-worker latency separately. A configured240Hz opportunity timer is
not evidence of240 actual worker drains or240 rendered frames. Logical frame
notifications remain60Hz and the worker coalesces notifications.

## 4. UART buffering and return traffic

[IDF UART5.5.5](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/uart.html)
distinguishes the hardware FIFO, driver ring buffer, hardware flow control and
application reads. It documents nonblocking `uart_tx_chars`, RX timeout/full
interrupts, and overflow/error events. The installed driver source
`components/esp_driver_uart/src/uart.c` confirms `uart_read_bytes` takes an RX
mutex and retrieves ring-buffer items; `uart_get_buffered_data_len` reports the
driver's buffered-byte count. It is not total wire-to-render backlog.

Current `console_hardware.inc` installs RX4096bytes, no driver TX ring, a32-event
queue, two-symbol RX idle timeout and RTS threshold64 at1,152,000baud8N1.
`ConsoleStream::readBytes` preserves a block read for uploads; ordinary `read`
still calls the driver for one byte, as opposed to a new bulk upload algorithm.
The owner supplies its own8192byte reply queue and128byte maximum FIFO refill.
It stops parsing while software reply bytes remain; the hardware FIFO may drain
independently. This preserves packet order and protects partial replies from
being stranded by a blocking parser read. It does not prove zero per-command
owner overhead. Stock also performs parser/driver work: count and compare actual
paths rather than assume any C++ wrapper is intrinsically wasteful.

The idle timeout alone is not a plausible millisecond-scale wire idle explanation
at this baud without evidence of delayed interrupt/service. No receive-permission
stall was observed in the complete marked wire window. That does not measure
FIFO-to-ring latency, parser runnable latency or every semaphore wait. Preserve
packet order, keyboard releases and full-duplex service during any later test.

## 5. Memory and output boundaries

[IDF heap allocation5.5](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/system/mem_alloc.html)
and installed `esp_heap_caps.h` distinguish total free bytes from largest
allocatable block. Stock viewport allocation uses multiple pools. The former
single-block check could therefore reject a feasible full internal framebuffer.
r42 restored the multi-pool route, with partial-allocation cleanup and complete
PSRAM fallback; both test paths actually selected INTERNAL. It did not solve
frame spacing. No fixed reserve guarantees all future game/mode allocations.

512×384 one-byte RGB222 output is196608bytes before its32byte EVF header.
At60frames/s that is94.37Mbit/s payload alone. This is arithmetic, **not a
measured link ceiling**: framing, TCP/IP, Ethernet, copies and browser pacing add
costs. Do not promise60browser images/s from60game completions. Current full
snapshots, socket-completion durations and browser receipt must be counted and
reported separately. Sending a snapshot is not the same task as drawing a game
primitive; hardware sprite composition also happens during snapshot generation.

## 6. Research conclusions and limitations

1. Strong evidence: variable delay exists after forward UART delivery and
   before refresh enqueue; retained execution scopes are often faster on P4.
2. Strong constraint: prior bulk UART parity is not a short-command latency
   proof; return replies and keyboard/control work remain on the owner task.
3. Plausible, unproven: network/USB/event preemption, unmeasured lock/driver/owner
   costs, shared-memory contention, timer/worker phase interactions.
4. Not supported: rewrite rasterizers, remove stock replies, disable keyboard,
   increase drawing divisor indefinitely, blame the harness wiring, or declare
   physical scanout/browser parity from a queue or nominal mode counter.
5. Some official5.5.5 web pages were unavailable to the browser. The5.5-family
   docs and locally pinned5.5.5 headers/source supplied those contracts. No
   master/latest SDK behavior was substituted as proof of the installed build.
