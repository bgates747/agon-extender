# SETUP-003 Work 6 — Portability and ownership review

## Scope

This review records source facts from official Agon VDP `v2.16.0` and its
selected dependencies. It identifies runtime ownership, activation paths,
platform coupling, externally visible behavior, and omission fallout. It does
not assign retain/replace/stub/omit/defer dispositions; those belong to
[SETUP-004](../SETUP-004.md).

The machine-readable authority is
[`generated/portability.yaml`](generated/portability.yaml). It combines 5,610
mechanically extracted candidates with 12 reviewed subsystem records, 95
source-validated references, and six reproducible source-wide searches.

## Controlling distinction

Three relationships must not be conflated:

1. **Compiled** — PlatformIO selects a translation unit for compilation.
2. **Header-coupled** — a used source path must preprocess declarations or
   implementation from a header.
3. **Runtime-reached** — startup, a command, callback, task, or interrupt
   actually activates the code.

The Work 4 compilation database selects 31 vdp-gl translation units. Exact
official-source searches find no direct `CVBSGenerator`, `ICMP`, `DS3231`,
`MCP23S17`, or `TSI2C` reference. Those files are build inputs, but direct VDP
runtime reachability is not established. Conversely, `fabutils.h` is on the
broad FabGL header path and directly includes `soc/frc_timer_reg.h`; that P4
preprocessing failure cannot be dismissed merely because some vdp-gl drivers
are unused (`vdp-gl:src/fabgl.h:311`, `vdp-gl:src/fabutils.h:45`).

## Reviewed runtime map

| Subsystem | Activation | Physical/platform ownership | Protocol-visible or user-visible dependency |
|---|---|---|---|
| Startup orchestration | Unconditional `setup()` and `processLoop` | Arduino lifecycle, ESP32 watchdog APIs, pinned FreeRTOS tasks | All normal command processing |
| Primary VDP transport | Unconditional startup | UART2, fixed pins, RTS/CTS, Arduino `HardwareSerial` | All VDU input and VDPP output |
| Graphics/display | Unconditional startup, then command-driven | FabGL VGA/Canvas, GPIO, I2S1, DMA, ISR, primitive task | Text, graphics, modes, palettes, sprites, cursors, buffers |
| Physical PS/2 input | Unconditional initialization and continuous polling | FabGL PS2/keyboard/mouse, ULP, RTC GPIO, SENS, ISR, tasks | Keyboard/mouse commands, packets, variables, pause/control-key behavior |
| Terminal mode | `VDP_TERMINALMODE` | FabGL Terminal, VGA, UART, PS/2, timers, queues, tasks | CP/M-style terminal mode |
| Audio | Unconditional initialization, then command-driven | FabGL SoundGenerator, I2S0, DAC/sigma-delta, DMA, ISR, task | Audio commands, synthesis/sample behavior, status packets |
| Memory/PSRAM | Pervasive and allocation-driven | PSRAM APIs and capability heap; some Xtensa-specific paths | Buffer/sample capacity and free-PSRAM variables |
| RTC service | RTC commands and variable reads | ESP32Time software time service | RTC command, packet, and variables |
| Firmware updater | `VDP_UPDATER` | ESP OTA partitions and restart; active VGA state | Serial-stream firmware update and partition switching |
| Debug/ZDI/transfers | Console or maintenance commands | UART0, direct GPIO ZDI, CRC, PSRAM | Console/ZDI, HEX load, YMODEM transfer |

## Principal findings

1. **Top-level feature startup is not modular.** Display mode creation,
   transport initialization, process-task creation, and audio initialization
   occur directly in `setup()`. Physical PS/2 initialization occurs directly
   at the start of `processLoop` (`agon-vdp:video/video.ino:99`, `:118`,
   `:136`). There are no independent production switches for graphics, input,
   audio, terminal support, or updater support.

2. **The primary transport has a useful seam, but the stock binding is
   concrete.** `VDUStreamProcessor` accepts Arduino `Stream`, while official
   startup supplies `Serial2` and uses it for both command input and packet
   output (`agon-vdp:video/vdp_protocol.h:17`,
   `agon-vdp:video/vdu_stream_processor.h:261`, `:516`).

3. **Graphics semantics and physical scanout are conceptually separable but
   source-coupled.** Official state directly owns FabGL `Canvas` and concrete
   VGA controller types. Active vdp-gl VGA code directly programs ESP32 I2S1,
   GPIO, DMA, interrupts, and a pinned primitive task
   (`agon-vdp:video/agon_screen.h:11`,
   `vdp-gl:src/dispdrivers/vgapalettedcontroller.cpp:168`).

4. **Input omission has broader fallout than losing PS/2 sockets.** The normal
   processor loop polls FabGL keyboard/mouse objects; the results drive
   packets, VDP variables, callbacks, paged-mode behavior, control characters,
   terminal escape, debug abort, ZDI entry, and VGA cursor state
   (`agon-vdp:video/vdu_stream_processor.h:611`, `:704`, `:726`). SETUP-004
   must distinguish physical acquisition from those protocol and state
   contracts.

5. **Audio semantics and physical output are also coupled through concrete
   ownership.** Official startup creates a FabGL `SoundGenerator` and an audio
   task. In VGA mode, vdp-gl's automatic method selects the ESP32 DAC path,
   which uses I2S0 DMA and an interrupt (`agon-vdp:video/agon_audio.h:97`,
   `vdp-gl:src/devdrivers/soundgen.cpp:519`, `:624`).

6. **PSRAM behavior is partly abstracted and partly contractual.** Common
   allocators prefer PSRAM and can fall back to ordinary heap, but YMODEM and
   display paths use explicit capability allocations. Free SPIRAM is exposed
   through VDP variables (`agon-vdp:video/types.h:47`,
   `agon-vdp:video/vdp_variables.h:381`).

7. **The official updater is not network-based.** It receives firmware through
   the VDU stream and writes ESP OTA partitions. `WiFi` appears only as an
   include in `video.ino`; no official v2.16.0 WiFi API use was found
   (`agon-vdp:video/updater.h:30`, `:100`).

8. **The official RTC service does not use FabGL's compiled DS3231 driver.** It
   uses the global ESP32Time object for RTC commands, packets, and variables
   (`agon-vdp:video/video.ino:79`, `agon-vdp:video/vdu_sys.h:515`).

9. **Concurrency follows runtime ownership.** Active official paths create the
   process and audio tasks; active VGA, PS/2, keyboard/mouse, and terminal
   objects create further tasks, queues, timers, and interrupts. Task-creation
   code found in an uninstantiated compiled driver does not establish runtime
   activity.

## Handoff

The evidence is sufficient for SETUP-004 to review each upstream I/O-facing
component without guessing from filenames or compiler failures. That task must
preserve the separation between physical-driver disposition and compatibility
of VDP commands, return packets, variables, callbacks, and state behavior.
