# Official VDP Architecture Précis

Status: Draft for Author review  
Source baseline: AgonPlatform/agon-vdp release `v2.16.0`,
[`c7ac293d2aa81ddfa693390549bcd909069c8fc3`](https://github.com/AgonPlatform/agon-vdp/commit/c7ac293d2aa81ddfa693390549bcd909069c8fc3),
verified as the latest official tag on 2026-08-20

## Scope

This document describes the official VDP firmware at tagged release `v2.16.0`. It
records source structure, build configuration, startup, runtime flow,
interfaces, state, dependencies, and implementation coupling. Material not
describing that firmware or its declared dependencies is outside its scope.

Primary sources:

- [official VDP repository](https://github.com/AgonPlatform/agon-vdp)
- [PlatformIO configuration](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/platformio.ini)
- [entry sketch](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino)
- [official Agon documentation](https://agonplatform.github.io/agon-docs/)

## System summary

The official VDP is a serial graphics terminal and hardware-service firmware
for the ESP32-PICO-based Agon VDP. MOS/eZ80 sends a BBC-style VDU byte stream
over UART. `VDUStreamProcessor` parses that stream and applies commands to text,
graphics, contexts, buffers, fonts, sprites, audio, input, terminal, and update
subsystems. Keyboard, mouse, status, query, and acknowledgement data return to
MOS as framed VDP protocol packets.

FabGL, through the AgonPlatform `vdp-gl` fork, supplies VGA controllers,
`Canvas`, terminal, PS/2, and sound facilities.

```text
eZ80/MOS --UART2 + flow control--> VDUStreamProcessor
                                      |
                 +--------------------+--------------------+
                 |        |        |       |       |       |
              Context   FabGL    buffers  audio   input   updater
                 |        |                  |       |       |
              drawing   VGA              audio   PS/2    OTA flash
                 |
eZ80/MOS <--framed response/event packets-------------------+
```

## Build configuration

The project is built with PlatformIO. `platformio.ini` sets `video/` as the
source directory and defines one `esp32dev` environment with:

- PlatformIO Espressif32 platform 6.6.0;
- generic `esp32dev` board and Arduino framework;
- QIO flash mode;
- 240 MHz CPU and 80 MHz flash declarations;
- C++17 and GNU C++17 with `-O2` optimization;
- PSRAM and the ESP32 PSRAM cache workaround;
- serial monitor at 115200 baud and upload at 600000 baud.

Declared libraries are AgonPlatform `vdp-gl` tag `all-the-plots`, ESP32Time
2.x, and CRC 1.x. The vdp-gl tag resolves to
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`. ESP32Time and CRC remain declared
as compatible version ranges, so the VDP commit alone does not identify their
exact resolved versions.

## Source organization

The repository root contains `platformio.ini`, `README.md`, `LICENSE`, and the
`video/` source tree. The firmware version is defined in `video/version.h`.

| Area | Principal files | Responsibility |
|---|---|---|
| Entry and orchestration | `video.ino`, `agon.h`, `version.h` | Startup, tasks, constants, terminal mode, version display |
| Transport and parsing | `vdp_protocol.h`, `vdu_stream_processor.h`, `vdu*.h` | UART setup, stream reads, command dispatch, return packets |
| Graphics state | `context.h`, `context/*`, `agon_screen.h` | Drawing/text state, viewports, cursors, modes, palette, canvas/controller ownership |
| Assets and operations | `buffers.h`, stream headers, `sprites.h`, `agon_fonts.h`, `compression.h` | PSRAM-backed data, buffered commands, sprites, fonts, compression |
| Audio | `agon_audio.h`, audio headers, `envelopes/*` | Sound generator, channels, task, samples, envelopes |
| Human input | `agon_ps2.h` | PS/2 keyboard/mouse setup, layouts, state, cursor, events |
| Maintenance and transfer | `updater.h`, `hexload.h`, `ymodem.h`, `zdi.h` | OTA update, data transfer, debugging facilities |
| Types and utilities | `types.h`, `span.h`, `mem_helpers.h`, `utils/*` | Types, PSRAM allocators, helpers, thread-safe event queue |

Most implementation is defined in headers included into `video.ino`, rather
than separately compiled `.cpp` files. Those headers frequently define
functions and global objects, making include order and the effective single
translation unit significant. `context/` is a visible subdivision for cursor,
font, graphics, and viewport behavior.

## Startup and task structure

Arduino supplies the framework entry and calls `setup()` and `loop()`.
`setup()`:

1. disables both core watchdogs unless `VDP_USE_WDT` is defined;
2. starts debug UART0 at 115200 baud on RX 3 and TX 1;
3. initializes the startup video mode and copies the default font;
4. configures the MOS/eZ80 VDP protocol UART;
5. constructs one `VDUStreamProcessor` around `VDPSerial`;
6. creates `processLoop`, pinned to core 0 at priority 3 with a 4096-byte stack (ESP-IDF counts this argument in bytes, not vanilla
   FreeRTOS stack words);
7. initializes audio; and
8. prints the firmware version on the boot screen.

Arduino's `loop()` sleeps forever in one-second intervals. `processLoop`
initializes keyboard and mouse, waits for eZ80 synchronization, and repeatedly
handles terminal mode or calls `VDUStreamProcessor::processNext()`.

Audio has another priority-3 task pinned to core 0. It loops over enabled audio
channels and delays for one FreeRTOS tick between passes.

## MOS/eZ80 serial interface

`agon.h` defines the VDP UART as 1,152,000 baud, TX 2, RX 34, RTS 13, CTS 14,
a 256-byte receive buffer, a 200 ms normal timeout, and a 10 ms fast timeout.
RTS connects to eZ80 CTS; CTS connects to eZ80 RTS.

`vdp_protocol.h` aliases `VDPSerial` to Arduino `Serial2`.
`setupVDPProtocol()` ends the prior instance, sizes the receive buffer, starts
8N1 serial, assigns flow-control pins, begins with RTS-only flow control, and
sets the stream timeout. `setVDPProtocolDuplex()` selects CTS/RTS or RTS-only
hardware flow control.

## Command input and parsing

The outer input is a BBC-style VDU byte stream. Printable and control bytes
select behavior; commands consume command-specific trailing arguments.

`VDUStreamProcessor` owns input/output `Stream`s, the current `Context` and
context stack, command/echo state, and an echo buffer. Read helpers cover timed
bytes, 16- and 24-bit integers, blocking bytes, bulk reads, discard, peek,
fixed/floating values, and reads from stored buffers.

`processNext()`:

1. checks frame/VSYNC-dependent work and callbacks;
2. restores temporary output streams when idle;
3. processes queued input events;
4. polls keyboard and mouse;
5. updates cursor flashing;
6. consumes one byte when active and input is pending;
7. handles paused processor states; and
8. processes the event queue again.

`processAllAvailable()` supports nested buffered-command execution. It
dispatches while its current input has bytes and deliberately omits event-queue
processing during that nested work.

## Output packets and events

`send_packet()` emits packet code plus `0x80`, one payload-length byte, then the
payload. It can suppress the next packet through a VDP variable and invokes
buffer callbacks after sending.

Return packet families include general poll, keyboard, cursor, screen
character, screen pixel, audio, mode, RTC, keyboard state, mouse, and echo.
Keyboard and mouse notifications use a global `ThreadSafeVariantDeque`; queued
event markers are expanded from current VDP-variable state when sent.

## Graphics and presentation

`agon_screen.h` owns global FabGL `Canvas` and `VGABaseController` pointers,
current mode and dimensions, logical scaling, pixel shape, colour depth, and a
64-entry palette. `getVGAController()` constructs a FabGL 2-, 4-, 8-, 16-, or
64-colour VGA controller. Palette operations update both FabGL controller state
and the VDP logical-to-physical colour mapping.

`Context` contains text/graphics cursors, fonts, paint options, viewports,
graphics origin, coordinate scaling, cursor behavior, and processor state. It
uses FabGL drawing types and calls `Canvas` extensively. The parser, graphics
state, and renderer are therefore not separated by a high-level,
renderer-independent draw-command interface.

FabGL `Canvas` targets a `BitmappedDisplayController`; the AgonPlatform fork
also contains a `GenericBitmappedDisplayController`.

## Buffers, contexts, fonts, and sprites

`VDUStreamProcessor` supports multiple contexts and context stacks. Its
constructor selects or creates context 0 using PSRAM-aware helpers.

Buffered commands can create writable streams, redirect output, call stored
command buffers, jump, copy, split, consolidate, reverse, transform, compress,
decompress, read variables, and register callbacks. Executing a buffer can
recursively feed bytes through the same parser.

Fonts are stored in PSRAM-aware maps and can be created from VDP buffers.
Sprites and bitmaps use FabGL types and can be created from incoming data,
buffers, or screen contents. The source also contains tile-bank, tile-map, and
tile-layer commands and state.

## Audio

`agon_audio.h` owns up to 32 `AudioChannel` pointers, a FabGL
`SoundGenerator`, a mutex, a PSRAM-backed sample map, and the audio task. Three
channels are enabled by default and the default sample rate is 16384 Hz.

Commands cover playback, status, volume, frequency, waveform, sample loading
and management, volume/frequency envelopes, enable/disable, reset, seek,
duration, sample rate, and waveform parameters.

## Keyboard, mouse, and terminal

`agon_ps2.h` initializes FabGL's PS/2 controller, supports multiple keyboard
layouts, and converts virtual-key data into Agon key state and VDP variables.
Mouse state includes position, deltas, buttons, wheel, cursor, sample rate,
resolution, scaling, and acceleration.

Terminal mode is a state machine. When enabled, it constructs a FabGL
`Terminal`, attaches it to the VGA controller, connects it to `VDPSerial`, and
handles special sequences. Serial bytes then go to the terminal instead of
ordinary VDU dispatch. Disabling it destroys the terminal and restores VDP
screen mode.

## Firmware update and transfer

The `VDP_UPDATER` family includes unlock, firmware reception, and firmware
switching. Firmware reception reads a 24-bit size, rejects data while locked,
selects the next ESP OTA partition, disables hardware sprite cursors, writes
1024-byte chunks with ESP OTA APIs, and checks a one-byte additive checksum
complement. The source also contains Intel HEX, YMODEM, and ZDI facilities.

## Networking and storage presence

`video.ino` includes `WiFi.h`, but the inspected startup and steady-state loop
do not initialize a network connection or service. The source does not present
a general local-filesystem service layer. Buffers, YMODEM, loader, and updater
code provide specific data or firmware mechanisms.

## Global state and coupling observations

- Numerous headers define global objects directly.
- `VDUStreamProcessor`, contexts, FabGL objects, buffers, palettes, fonts,
  sprites, audio channels, and VDP variables form a broad shared-state graph.
- PSRAM-aware allocation is embedded in context, buffer, font, sample, and
  asset structures.
- Parsing, frame checks, input polling, event delivery, and cursor behavior
  share `processLoop`.
- Audio runs concurrently in another priority-3 core-0 task and uses a mutex
  around sound-generator replacement.
- Stream reads include blocking and timeout-based paths.
- Buffered commands can redirect streams and recursively execute the parser.
- Watchdogs are normally disabled unless `VDP_USE_WDT` is defined.

## Glossary

- **Translation unit:** One source file after included header text is inserted
  and preprocessed.
- **Header-defined implementation:** Functions or globals defined in a header,
  not merely declared there.
- **FreeRTOS task:** An independently scheduled execution context sharing
  process memory.
- **Pinned task:** A task restricted to one CPU core.
- **Stream:** Arduino's byte-oriented read/write interface.
- **Context:** VDP drawing, text, cursor, viewport, font, colour, coordinate,
  and processor state.
- **Dispatch:** Selecting behavior according to a command byte.
- **PSRAM:** Pseudo-static RAM used for large dynamic objects and assets.
- **OTA:** Writing firmware to an update partition for a later boot.
