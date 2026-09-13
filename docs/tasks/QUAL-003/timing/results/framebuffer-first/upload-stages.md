# Upload-stage comparison — 2026-09-13

The Author requested loading results separately from rendering performance.
This report uses the existing physical `baseline39.csv` and
`baseline39-corpus.json`; no new hardware activity was required. Compare the
[rendering-only report](rendering-only.md) for drawing scopes.

## What was actually measured

1. Each selected stage includes bitmap asset uploads plus its original buffer
   commands, bitmap creation, scene commands and any transforms. All stage
   bytes were preloaded from Agon SD into eZ80 RAM before measurement. These
   are **not SD loading times**, isolated buffer-write times, or per-bitmap
   creation benchmarks. A buffer becoming populated and a bitmap being ready
   to draw are different events; this fixture has no separate timestamp for each.
2. Renderer-local elapsed time is measured on the destination processor from
   the admitted start through the final drawing completion. It includes the
   arriving stream, command handling and completion wait. Submission time is
   measured on eZ80 around the counted-output calls that transmit the stage.
   Submission can stall on transport/backpressure while the destination parses
   and renders. The intervals overlap and must not be added.
3. Tables show medians of three instrumentation-enabled draw passes. Each
   destination receives the same byte sequence. Percentage change is
   `100 × (EDP time / mainboard VDP time − 1)`; positive means EDP takes longer.
   Worst cases appear first by largest EDP time in the relevant table.
4. These are exploratory instrumented results at mode20, 512×384, 64 colours.
   Mainboard VGA remains active; no P4 video snapshots occurred. Hardware-sprite
   stage completion does not imply equivalent output composition.

## Upload-heavy stage elapsed time

These are destination-clock measurements in milliseconds, with microsecond
source resolution. Asset bytes exclude command wrappers; total bytes include
all commands in the measured stage. Setup outside the stage is excluded.

| Stage | Case | Asset bytes | Total bytes | VDP ms | EDP ms | Time change |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Opaque/cutout/alpha bitmap setup | BSP03_01 | 93,788 | 94,683 | 881.983 | 3165.200 | +258.9% |
| Hardware-sprite setup | BSP26_01 | 60,712 | 61,406 | 582.664 | 2048.142 | +251.5% |
| Mixed hardware/software setup | BSP27_01 | 48,852 | 49,420 | 481.969 | 1648.518 | +242.0% |
| Sprite positioning setup | BSP21_01 | 42,644 | 43,203 | 432.262 | 1447.800 | +234.9% |
| Overlapping software-sprite setup | BSP25_01 | 29,476 | 30,006 | 316.114 | 1014.921 | +221.1% |
| Deferred software-sprite setup | BSP22_01 | 25,732 | 26,195 | 265.365 | 881.525 | +232.2% |
| Transformed sprite-frame setup | BSP29_01 | 24,276 | 25,701 | 315.788 | 865.070 | +173.9% |
| Direct-versus-PLOT bitmap setup | BSP07_01 | 9,248 | 9,765 | 115.583 | 331.214 | +186.6% |

## Time spent submitting those stages from eZ80

The fixture records raw MOS ticks, incrementing by two per VBlank. The ms
columns below use the nominal mode20 60Hz cadence: `ticks × 1000 / 120`.
They are approximate conversions, not an independently calibrated eZ80 timer;
effective quantization is about 16.7ms. Raw tick medians are retained alongside
the conversion. Rounded decimal places do not imply sub-millisecond precision.

| Case | VDP raw ticks | EDP raw ticks | VDP submission ms (approx.) | EDP submission ms (approx.) | Time change |
| --- | ---: | ---: | ---: | ---: | ---: |
| BSP03_01 | 104 | 376 | 866.7 | 3133.3 | +261.5% |
| BSP26_01 | 68 | 244 | 566.7 | 2033.3 | +258.8% |
| BSP27_01 | 54 | 196 | 450.0 | 1633.3 | +263.0% |
| BSP21_01 | 48 | 172 | 400.0 | 1433.3 | +258.3% |
| BSP25_01 | 32 | 120 | 266.7 | 1000.0 | +275.0% |
| BSP22_01 | 30 | 104 | 250.0 | 866.7 | +246.7% |
| BSP29_01 | 32 | 102 | 266.7 | 850.0 | +218.8% |
| BSP07_01 | 12 | 38 | 100.0 | 316.7 | +216.7% |

## Completion after submission

For completeness, the following is the eZ80 time from sending the final END
request until its completion reply arrives. It includes the END transmission,
remaining destination work and return transport; it is not just rendering drain.
Zero ticks means below the timer resolution, not zero work. These independently
computed medians need not add exactly to other median intervals.

| Case | VDP raw ticks | EDP raw ticks | VDP completion ms (approx.) | EDP completion ms (approx.) |
| --- | ---: | ---: | ---: | ---: |
| BSP03_01 | 2 | 2 | 16.7 | 16.7 |
| BSP26_01 | 2 | 2 | 16.7 | 16.7 |
| BSP27_01 | 4 | 0 | 33.3 | 0.0 |
| BSP21_01 | 4 | 2 | 33.3 | 16.7 |
| BSP25_01 | 6 | 2 | 50.0 | 16.7 |
| BSP22_01 | 2 | 2 | 16.7 | 16.7 |
| BSP29_01 | 6 | 2 | 50.0 | 16.7 |
| BSP07_01 | 2 | 2 | 16.7 | 16.7 |

No percentage is presented for these very short completion intervals: 0/2/4/6
raw ticks are too coarsely quantized to support a useful fine-grained comparison.

## Interpretation and limits

1. EDP is slower in all eight upload-heavy stage elapsed measurements, by about
   174–259%. Most of the additional time is already present in the eZ80
   submission interval, before the final completion request.
2. The largest stage sends 94,683 total bytes, including 93,788 asset bytes.
   VDP takes 881.983ms versus EDP 3,165.200ms overall; corresponding submission
   estimates are 866.7ms and 3,133.3ms. The latter is consistent with the
   slowdown occurring during delivery/consumption of the stream.
3. This does not distinguish EMOS sending overhead, UART transfer capacity,
   flow-control stalls, P4 parser throughput, buffer allocation/consolidation,
   bitmap creation/conversion or transforms. It is not evidence that any one
   component alone causes the difference. Byte totals are aggregate asset bytes,
   not necessarily a single bitmap or a uniform pixel format.
4. Do not subtract primitive or software-sprite totals from elapsed time and
   call the remainder pure loading: execution overlaps delivery, rendering
   scopes overlap each other, and other costs remain unmeasured.
5. A standalone buffer-upload/bitmap-create benchmark with separate boundaries
   would be required for exact per-operation loading costs. That measurement
   was not run here. Hardware remains at the previously restored review stop.

## Quick code audit: stock UART and rendering scheduling

Audit requested by the Author after the loading comparison, 2026-09-13.
This was read-only: no firmware edit, build, deployment or new timing run.
The baseline stock reference is VDP v2.16.0, commit
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, with vdp-gl commit
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`. The mainboard diagnostic build uses
Arduino ESP32 2.0.14; the measured P4 build uses Arduino ESP32 3.3.11.

The measured P4 image is
`uart-excom-console-r17-b2026-09-13-13-07-24Z`. Its archived input manifest
matches the inspected `console_stream.hpp`, `console_hardware.inc` and
`stock_runtime_controller.hpp`. The current `stock_p4_service.cpp` differs
from that image's manifest, so its task-creation details were checked against
the image's archived source instead of assuming the working copy was identical.
Exact private build/source bundles remain in the ignored local evidence.

| Area | Mainboard VDP | P4 EDP | Finding |
| --- | --- | --- | --- |
| Buffer upload reads | `HardwareSerial::readBytes()` requests a block from the UART driver | Generic `Stream::readBytes()` repeatedly invokes a one-byte driver read through `ConsoleStream` | Confirmed loss of stock's bulk-read path; strongest throughput suspect |
| Parser scheduling | Continuously calls `processNext()` | Up to 64 parser invocations, housekeeping, then unconditional `delay(1)` | Additional scheduling overhead; not a 64-byte upload quota |
| Software RX buffer | 256 bytes | 4,096 bytes | P4 has more buffering, not less |
| UART configuration | 1,152,000 baud; RTS threshold 64; duplex-dependent CTS | 1,152,000 baud; RTS threshold 64; RTS/CTS enabled | No obvious lower baud configuration explains the ceiling |
| Parser task | Core0, priority3 | Core0, priority3 | Preserved |
| Drawing worker | Priority5, vertical-sync notification | Core0 priority5, periodic-timer notification | Broad priority relationship retained; wakeup implementation differs |
| Drawing budget | Controller supports a timeout, but Agon disables it | Drain until queue empty or suspended | Not evidence of removing an active stock fairness budget |
| Graphics synchronization | Original controller synchronization | Additional native/foreground mutexes | Confirmed architectural difference; contribution to upload slowdown unmeasured |
| Physical output | I2S/DMA emits VGA; ISR prepares scanlines and hardware-sprite overlays | Timer-driven output task and snapshot composition, with no snapshots in this pass | Execution environments are not identical |

### Confirmed bulk-read divergence

The retained parser's `readIntoBuffer()` calls `inputStream->readBytes()`.
The implementations behind that call differ:

```text
Mainboard:
readIntoBuffer()
  -> HardwareSerial::readBytes(buffer, length)
    -> uartReadBytes(..., length, timeout)
      -> UART driver block read

P4:
readIntoBuffer()
  -> generic Stream::readBytes(buffer, length)
    -> timedRead(), once per byte
      -> ConsoleStream::read()
        -> uart_read_bytes(..., &byte, 1, 0)
```

The stock Arduino `HardwareSerial.cpp` explicitly describes its override as
“Overrides Stream::readBytes() to be faster using IDF.” P4's `ConsoleStream`
does not override either bulk-read overload. Arduino 3.3.11's inherited
`Stream::readBytes()` calls `timedRead()` for each byte; `timedRead()` obtains
a millisecond timestamp and retries `read()` until success or timeout.
The P4 adapter therefore incurs repeated UART-driver calls and timer/polling
work throughout a payload. Its setup-byte and peek caches must also be
preserved by any eventual alternative implementation; blindly bypassing the
adapter would not preserve its stream contract.

This is a confirmed implementation difference and a credible explanation for
the observed nearly constant throughput ceiling. It is not yet proof of its
quantitative contribution. No controlled bulk-versus-byte comparison was run.
The audit does not establish that an agent deliberately removed an optimization:
the adapter simply does not preserve the stock accelerated path.

### Scheduling and output qualifications

1. The console loop's 64-unit budget counts parser invocations, not payload
   bytes. A single invocation can remain inside `readIntoBuffer()` for an
   entire uploaded buffer, without reaching the outer `delay(1)`. Therefore
   that delay is not sufficient evidence for a fixed 64-byte throughput cap.
2. Stock `agon_screen.h` enables background primitive execution and explicitly
   calls `enableBackgroundPrimitiveTimeout(false)`. The original worker has
   an optional budget, but Agon disables it. P4's drain-until-empty behavior
   is not, on this point, a departure from the selected stock configuration.
3. Mainboard VGA is not entirely CPU bit-banging. I2S/DMA emits the signal;
   the VGA controller ISR fills scanline buffers, decorates hardware sprites
   and notifies the drawing worker at the frame boundary. P4 replaces this
   hardware-specific mechanism with a timer and tasks. Additional mutexes
   protect shared native state; any waiting cost needs direct measurement.
4. The preferred suspect order from this quick audit is the missing bulk-read
   path, then parser scheduling and contention. This is a diagnostic ranking,
   not an authorization to change code or a proven root-cause ranking.

### Source references

Paths below are repository-relative unless identified as external references.
Use the exact recorded image archive when its source differs from the worktree.

| Evidence | Source |
| --- | --- |
| Retained payload reader | `vdp/video/vdu_stream_processor.h`, `VDUStreamProcessor::readIntoBuffer()` |
| P4 single-byte adapter and absent bulk override | `vdp/video/extender/transport/console_stream.hpp`, `ConsoleStream::read()` |
| P4 UART setup, parser budget and delay | `vdp/video/extender/transport/console_hardware.inc`, `beginConsole()` / `runConsole()` |
| P4 worker priorities and wakeups | Archived `vdp/video/extender/display/stock_p4_service.cpp`, `attach()` / `timerEntry()` |
| P4 drain semantics | `vdp/video/extender/display/stock_runtime_controller.hpp`, `drain()` |
| P4 additional mutexes | `vdp/video/extender/display/stock_native_access.hpp` |
| Stock UART setup and buffer constants | Official VDP v2.16.0 `video/vdp_protocol.h` and `video/agon.h` |
| Stock parser scheduling | Official VDP v2.16.0 `video/video.ino`, `setup()` / `processLoop()` |
| Stock disabling of drawing timeout | Official VDP v2.16.0 `video/agon_screen.h` |
| Stock scanout and worker | Selected vdp-gl `src/dispdrivers/vga2controller.cpp`, `ISRHandler()`; `vgabasecontroller.cpp`, `primitiveExecTask()` |
| Accelerated stock stream reads | Mainboard Arduino ESP32 2.0.14 `cores/esp32/HardwareSerial.cpp` and `esp32-hal-uart.c` |
| Generic P4 stream fallback | P4 Arduino ESP32 3.3.11 `cores/esp32/Stream.cpp`, `readBytes()` / `timedRead()` |
