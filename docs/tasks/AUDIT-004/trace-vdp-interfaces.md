# Stock VDP peripheral and maintenance traces — W3/W4

This [AUDIT-004](../AUDIT-004.md) evidence covers P019–P025 and X004–X010
from the [communication inventory](communication-inventory.md), including
their T002–T004/T008–T011 dependencies. Source inspection establishes the
software behavior below; it is not a physical test, a circuit recommendation,
or acceptance of the audit. This record incorporates W4 evidence corrections;
the completed [coverage reconciliation](coverage-review.md) remains a separate
audit deliverable.

The fixed sources are stock VDP **v2.16.0**, commit
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`; stock MOS **v3.0.2**, commit
`8336409351ee5314e02801a7b72a4f1bb5282519`; and official documentation
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. Library observations use the
historically resolved vdp-gl dependency
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`, with the reviewed files
authenticated against their Git blobs. This does not establish a new build.
Board-source provenance and physical route qualifications are recorded in
[the hardware and dependency trace](trace-hardware-and-dependencies.md).

## Shared execution and session rules

1. VDP `setup` configures the external `DBGSerial` UART, display and primary
   `VDPSerial`, creates `processLoop` on core 0, and initializes audio.
   `processLoop` initializes PS/2 and waits for eZ80 startup before repeatedly
   choosing terminal processing or `processor->processNext()`. A synchronous
   maintenance handler occupies that command-processing task until it returns;
   this does not mean that independent audio/library tasks stop.
   [VDP startup and loop][v-main-loop]
2. `DBGSerial` is ESP32 UART0, configured as 115200 baud, 8N1 on RX GPIO3/TX
   GPIO1. T004 is shared by console, printer, diagnostics and host transfer
   services. Their writes have no common message envelope, endpoint identifier,
   or write-result check in these application helpers. The board USB/serial
   bridge is distinct from ESP32 native USB. [Serial declaration/setup][v-main-config]
3. Primary-link `readByte_b()` waits indefinitely for input. It neither polls
   Escape nor supplies a session deadline. `readByte_t()` has a configured
   timeout; `readIntoBuffer()` uses stream `readBytes`, retries once when a
   read returns zero, and reports bytes remaining. Its `timeout` argument is
   not applied to those stream reads inside this implementation. Therefore a
   numeric parameter alone does not establish a complete operation deadline.
   [Read/discard helpers][v-reads]
4. HEX/YMODEM helpers send two-byte keyboard payloads `{value, 0}` through
   `send_packet`, whereas ordinary keyboard events have four payload bytes.
   They inherit the current output destination and one-packet suppression
   behavior; they do not reserve an independent reliable return channel.
   Their application-level acknowledgements are separate from UART pacing.
   [Transfer helpers][v-hex-helper], [YMODEM helpers][v-y-helpers],
   [packet output][v-packet]
5. **E08 resolution:** VDP startup selects RTS-only flow control, but MOS
   `wait_ESP32` subsequently sends variable `0x0101=1`, whose VDP setter selects
   RTS+CTS. Neither selected HEX nor YMODEM handler resets this setting.
   These sessions therefore inherit the configured UART state; the older
   HEX documentation's one-way-flow statement is not an unconditional rule
   for the selected stock pair. The application ACK/checksum protocols remain
   present in either setting. Actual electrical/driver pacing belongs to the
   primary-link and hardware traces. [Documented HEX discussion][d-hex],
   [MOS startup request][m-startup], [VDP setter][v-duplex-var],
   [VDP UART setup][v-duplex]

## Build and configuration boundaries

The selected PlatformIO declaration has one `esp32dev` environment and does
not define `USERSPACE` or `VDP_USE_WDT`. These source branches describe
configurations; no additional build or deployed-image identity is established.
[Build declaration][v-build]

| Configuration | Source-observed behavior and communication boundary |
| --- | --- |
| Physical build | `video.ino` forces `DEBUG=0`, so ordinary `debug_log` emits no application diagnostic bytes. Forced buffer diagnostics and ZDI's own host-print helper still write T004. Startup mode is 0. [Main switches][v-main-config], [loggers][v-debug], [forced caller][v-forced], [ZDI host writer][v-zdi-serial] |
| `USERSPACE` | Source forces `DEBUG=1`, expects external startup-mode and `debug_log` definitions, and adds a periodic scheduler yield. It excludes `zdi.h`, supplies ZDI entry stubs, and makes the HEX handler return immediately. YMODEM/updater includes and dispatch are not guarded away in this source; that does not establish that those services work in an emulator. No USERSPACE build was reviewed or changed. [Main switches and loop][v-main-build], [logger guard][v-debug], [ZDI stubs][v-ps2-stubs], [HEX guard][v-hex], [maintenance includes][v-system-includes], [transfer dispatch][v-transfer-select], [updater][v-updater] |
| `VDP_USE_WDT` | The experimental option is commented out. Default setup calls `disableCore0WDT` and `disableCore1WDT`; defining the option skips those calls and adds `esp_task_wdt_reset()` at the top of `processLoop`. Synchronous maintenance handlers do not reach that reset call until they return. Watchdog registration, expiration/panic behavior and recovery from a stalled session remain unverified. [Option][v-config], [setup and loop][v-main-loop] |

## P019 — Terminal mode on the primary UART

The documented eZ80 requester sends `VDU 23,0,&FF`. VDP dispatch calls
`startTerminal`; `processTerminal` creates a vdp-gl terminal bound to the
existing VGA controller and `VDPSerial`. While enabled, the VDP main task
passes primary-input bytes to `Terminal::write` one at a time and bypasses
normal `processNext`. vdp-gl queues those bytes for its character-consumer
task, which parses terminal controls and draws through its canvas. Its
keyboard-reader task obtains PS/2 virtual keys and sends terminal-encoded
bytes directly through the same hardware serial object, bypassing ordinary
VDP packet framing. The eZ80 terminal application is an external peer whose
source/version is not selected. [Terminal documentation][d-terminal],
[VDP state machine][v-terminal], [library input queue][l-term-queue],
[input task][l-term-input],
[library keyboard task][l-term-keys],
[library output][l-term-send]

1. `connectSerialPort(VDPSerial)` uses the library's default
   `autoXONXOFF=true`, sets software-flow state and sends an initial XON.
   Received XOFF/XON controls affect the terminal keyboard sender. The VDP
   loop manually reads the serial input; it does not call the library's
   `pollSerialPort()` helper that contains Arduino receive-threshold
   XON/XOFF generation. Do not infer all library flow-control mechanisms are
   active in this integration. Existing UART hardware configuration is not
   explicitly replaced by this overload. [Connection default][l-term-default],
   [connection implementation][l-term-connect], [flow helpers][l-term-flow],
   [unused polling alternative][l-term-poll], [received controls][l-term-ctrl]
2. `ESC _#Q!$` requests termination and `ESC _#S!$` suspension through the
   registered user-sequence callback; Ctrl+Alt+F12 also requests termination.
   Suspension returns command input to VDU processing but does not deactivate
   the terminal keyboard task. Termination destroys the terminal and calls
   `vdu_mode(videoMode)` to restore display state; that mode path resets VDP
   contexts and sends mode information. These are explicit state transitions,
   not evidence that arbitrary interrupted traffic is recoverable.
   [VDP transitions][v-terminal], [mode restoration][v-mode]
3. Terminal `begin()` returns allocation/setup success, which the VDP caller
   does not check. Queue insertion and character/escape input include
   indefinite waits; a truncated escape sequence has no general timeout at
   `getNextCode`. Serial output waits for available write space. Source
   provides no overall terminal-session completion guarantee under a stalled
   peer or resource failure. [Library initialization][l-term-begin],
   [queue waits][l-term-queue], [parser waits][l-term-input],
   [output waits][l-term-send]

## P020 — Intel HEX reception and eZ80 utility delivery

The eZ80 HEX utility requests `VDU 23,28`. Dispatch first attempts to read an
additional byte: timeout (`-1`) chooses HEX, byte `1` chooses YMODEM receive,
and byte `2` chooses YMODEM send. Another value has no selected action.
Thus immediate trailing bytes matter to session selection; the HEX selector
is not a self-contained length-delimited command in this implementation.
The `USERSPACE` HEX handler returns immediately. [Dispatch][v-transfer-select],
[handler][v-hex]

The external PC supplies text HEX records on T004. VDP `consumeHexMarker`
locates `:`, decodes length/address/type, and dispatches data, EOF, segment,
linear-address, or extended-format records. For a data record the VDP sends
start marker `1`, three address bytes most-significant first, length, then
payload bytes as keyboard packets on T001. Each header byte waits for an
arbitrary eZ80 ACK byte; payload bytes are sent without per-byte ACK, followed
by an unbounded wait for the utility's additive-checksum complement. EOF and
Escape release the caller with marker `0`, also awaiting an ACK.
Stock MOS is the packet carrier; it is not the HEX decoder or destination
writer. The external utility's memory/filesystem effects have not been
verified against an exact utility revision. [Documented utility boundary][d-hex],
[record sender and feedback][v-hex-records]

1. External serial reads use a configured 5 ms wait and return zero on
   timeout, rather than a distinct error result. Escape is checked during
   those external reads; it cannot interrupt an eZ80 `readByte_b()` wait.
   Marker scanning has no overall deadline. Invalid HEX characters are
   converted and left to checksum handling. [External reader][v-hex-reader]
2. Ordinary records accumulate checksum errors after forwarding data to
   eZ80. In extended mode, VDP compares per-record CRC16, returns its CRC16
   over T004, and maintains final CRC32 state; a mismatch causes the host to
   be asked indirectly to retransmit by the differing returned checksum.
   This source does not undo already forwarded eZ80 writes. Final CRC32 and
   address-overlap diagnostics are observations, not atomic-transfer or
   memory-protection guarantees. Host retry behavior and CRC-library semantics
   remain explicit external dependencies. [Record handling][v-hex-records],
   [extended checks and completion][v-hex-complete]

## P021/P022 — YMODEM host transfers with a separate eZ80 session protocol

Both directions create a `MOS_YmodemSession` and send keyboard value `'C'`
to the eZ80 utility. The name does not mean MOS implements that utility.
Session integers are four-byte little-endian values; VDP-to-eZ80 values use
keyboard packets, while eZ80-to-VDP values are raw primary-stream bytes read
with `readByte_b`. External YMODEM uses T004 CRC16 blocks, sequence/complement
bytes and ACK/NAK/CAN/`'C'` controls. Source constants select 128/1024-byte
blocks, 1200 ms external read waits, three retry attempts for sender phases,
and a 200 ms external-input discard at selected session boundaries. These
are configured operations, not guaranteed throughput or total deadlines.
[Helpers/constants][v-y-helpers], [external block format][v-y-block-out]

| Direction | Sender → VDP → receiver and observable effects | Coordination/completion |
| --- | --- | --- |
| P021: PC → eZ80 | `vdu_sys_ymodem_receive` requests CRC mode from the PC, receives/checks blocks and accumulates whole files in PSRAM. After the external session it calls `writeFiles` to send complete stored files to the eZ80 utility. | Each eZ80 file starts with marker 1/name length/name/size and requires `S1`; marker 2/length/data carries chunks of at most 1024 bytes and requires `S2`; marker 3/CRC32 requires `SV`; marker 4 closes the file and requires `S4`. Final marker 0 closes the session. [PC receiver][v-y-receive], [eZ80 writer][v-y-writefiles] |
| P022: eZ80 → PC | `readFiles` first reads eZ80 count/filename length/name/size/payload/CRC32 records into PSRAM until a zero count. Only then does `vdu_sys_ymodem_send` wait for the PC receiver's `'C'` and transmit the files. | PC block-zero and data phases use ACK, `'C'`, CAN and bounded individual retries; EOT ends each file, followed by an empty final block zero. Session close sends marker 0 to eZ80. The eZ80 utility's own file reads/status behavior is not selected evidence. [eZ80 reader][v-y-readfiles], [PC sender][v-y-send] |

The following are source-observed limits, not newly authorized repairs:

1. All eZ80 session reads/ACK waits can block indefinitely. P022's initial
   external `'C'` wait can also continue indefinitely, though it polls local
   Escape there. P021 polls Escape between external block reads; after abort
   it still calls `writeFiles`, which removes an incomplete final file but
   may deliver previously completed files. It ignores `writeFiles`' result
   before printing `Done` and closing. An abort is not an all-or-nothing
   cancellation of received files. [P021 finish][v-y-receive],
   [complete-file filter/ACK waits][v-y-writefiles], [P022 waits][v-y-send]
2. P022's final empty-block retry loop falls through to `Done` even if no
   final ACK arrived. P021 checks an empty end-of-batch marker before its
   timeout/CRC-validity checks; its invalid CRC/block-number branch sends NAK
   without incrementing `errors`. These paths do not establish bounded
   malformed-stream recovery or verified end-to-end success.
   [Final send phase][v-y-send-end], [receive loop][v-y-receive]
3. `readFiles` does not bound received `filename_length` before copying into
   its fixed local filename array, and ignores `addFile` failure before
   accessing the selected file. External `get_block` can write the filename
   terminator at index 100 of a 100-byte array, and its filename-termination
   scan does not advance the counter used in its bound. These are concrete
   unchecked-input paths; crash/corruption behavior was not exercised.
   `cancel_counter` is also uninitialized before a possible first CAN.
   Do not claim that arbitrary malformed input is safely rejected.
   [eZ80 filename handling][v-y-readfiles], [external header parsing][v-y-block-in],
   [allocation/results][v-y-session], [receive state][v-y-receive]

## P023 — VDP firmware update

The eZ80 `agon-flash` application supplies `VDU 23,0,&A1`, followed by
subcommand 0 (unlock), 1 (receive firmware), or 2 (switch firmware). The VDP
reads the literal unlock string, then accepts a 24-bit little-endian image
size, image data in blocks of at most 1024 bytes, and an additive-checksum
complement. It writes through ESP OTA calls, selects a boot partition and
restarts the ESP32. This service uses T001, not the external PC serial link.
No structured reply packet is emitted by the updater functions; their
`print`/`printFmt` diagnostics use local VDU rendering, with any configured
serial reflection applying as usual. The exact `agon-flash` peer and ESP OTA
implementation remain external-source boundaries. [Documentation][d-update],
[updater][v-updater], [local print helper][v-local-print]

1. The VDP starts locked; wrong/incomplete unlock does not clear the lock.
   A locked receive discards the advertised payload and checksum, subject to
   the shared discard helper's timeout. Invalid subcommands have no explicit
   error reply. During receive, VDP disables mouse/text cursors and sprites;
   most error paths restore text painting only. A read timeout can return
   without draining the remaining image, so delayed bytes can subsequently
   reach normal command dispatch. [Updater receive/error paths][v-updater]
2. Begin/write/checksum/boot-selection errors return through distinct paths.
   This source contains no `esp_ota_end` or `esp_ota_abort` call; consequently
   image finalization, resource cleanup and rollback claims cannot be inferred
   from the apparent success path. The switch-only path restarts even after
   `esp_ota_set_boot_partition` returns an error. No OTA or power-interruption
   experiment was performed. The official update guide's broad two-image
   recovery description does not establish the selected framework's exact
   finalization, cleanup or rollback behavior. [Updater completion/switch][v-updater-end],
   [documented recovery description][d-update-recovery]
3. On ESP software reset, `wait_eZ80` assumes MOS is already running, skips
   the initial poll wait and sends mode information. A physical reset and an
   updater restart therefore follow different startup branches. The board
   trace separately establishes the shared physical reset conductor; an ESP
   software restart does not prove assertion of that conductor or coordinated
   eZ80 recovery. [Post-reset entry][v-wait],
   [board reset evidence](trace-hardware-and-dependencies.md)

## P024 — Display timing to MOS

The driver route is now source-backed: VDP initializes its VGA controller;
vdp-gl's default `VGABaseController::begin()` maps VSync to **ESP32 GPIO15**.
`setupGPIO` assigns that output to the I2S1 GPIO stream, `packHVSync` creates
the selected modeline's sync levels, and the DMA layout includes VSync lines.
The separately recorded Rev B board evidence connects this VS net to both
the VGA connector and eZ80 PB1. [VDP controller entry][v-screen],
[library pin mapping][l-vga-pins], [sync generation][l-vga-sync],
[DMA layout][l-vga-dma], [board/MOS route evidence](trace-hardware-and-dependencies.md)

MOS startup configures PB1 as mode 9 rising-edge interrupt input, and
`init_interrupts` installs `vblank_handler` at `PORTB1_IVECT`. On receipt,
`_vblank_handler` disables interrupts, saves registers, reads PB_DR, ORs it
with mask `0x02` and writes it back (`SET_GPIO PB_DR, 2`), then adds
2 to the 32-bit `_clock` with carry into the fourth byte. It then restores
registers and re-enables interrupts before returning. The authenticated
F92/F93 specification defines writing 1 to an edge-triggered pin's data bit
as clearing its interrupt request, supplying the acknowledgement semantics
for this PB_DR write. `_clock` is the first four bytes of `_sysvars`, exposed
by the documented `sysvar_time` field.
This establishes the MOS state update per received interrupt; the increment
does not establish a measured frame rate or wall-clock accuracy.
[Vector installation][m-vblank-install], [interrupt receiver][m-vblank],
[GPIO mask operation][m-gpio-macro], [system-variable storage][m-clock],
[documented clock field][d-clock],
[W4 processor semantics and initialization evidence](trace-hardware-and-dependencies.md)

The `GPIO_ITRP=17` declaration is explicitly reference-only and is **not**
this producer. The board's GPIO17/ITRP route goes to PB0, a different net.
T002/P024 should be read with this W3 clarification rather than interpreting
the W2 candidate from the constant alone. Mode changes stop/reconfigure the
display controller; the trace makes no constant frame-rate or uninterrupted
VBLANK guarantee through those transitions. [Reference declaration][v-config],
[controller shutdown/configuration][v-screen], [library shutdown][l-vga-pins]

## P025 — ZDI and external debug console

With console mode enabled, incoming T004 byte `0x1A` enters ZDI; subsequent
console bytes are dispatched to `zdi_process_cmd`. On the physical build,
VDP drives GPIO26 as ZDI clock and changes GPIO27 direction for ZDI data.
Register primitives serialize register/data bits and disable interrupts
around their low-level exchange. The receiver is eZ80 debug hardware, not
MOS. **The reviewed Light 2 board does not internally connect these ESP32
header pins to the eZ80's separate ZDI header.** This service therefore needs
an appropriate external connection; this trace provides no wiring instruction.
The same ESP32 pins are the library's default second PS/2 port.
[Console dispatch][v-ps2-key], [ZDI pins][v-zdi-pins],
[bit/register paths][v-zdi-wire],
[board route](trace-hardware-and-dependencies.md), [PS/2 defaults][l-ps2-default]

1. `zdi_enter` reads eZ80 identification and refuses when both its product
   and revision comparisons differ. It sets clock-output state before that
   check; the refusal/exit branches clear the mode flag but do not explicitly
   restore PS/2 pin ownership. No PS/2/ZDI exclusion protocol or electrical
   safety claim is established. `USERSPACE` replaces these ZDI entry helpers
   with stubs. [Enter/exit][v-zdi-enter], [build-specific stubs][v-ps2-stubs]
2. Line commands request register/memory access, CPU mode changes,
   break/continue/step, eZ80 reset (`R` writes `ZDI_MASTER_CTL`) and eZ80
   peripheral initialization (`i`). The auxiliary `e` command calls
   `ez80_serial_write`, which constructs four-byte keyboard payloads
   `{keycode,0,0,1}` and calls global `processor->send_packet`, with a
   configured 100 µs delay after each call. This path uses T001 when the
   output stream selects that UART and requires a compatible eZ80 software
   receiver. It inherits the current output destination and suppression
   setting; the delay is not an acknowledgement or receipt guarantee.
   Other ZDI commands need not depend on MOS. [Command dispatch][v-zdi-command],
   [reset/entry][v-zdi-enter], [peripheral initializer][v-zdi-init],
   [auxiliary command][v-zdi-execute], [packet constructor][v-zdi-serial],
   [shared output behavior][v-packet]
3. Unknown line commands print an error; `q`/Escape exits command mode.
   The line editor decrements unsigned `charcnt` on backspace without checking
   zero, and can fill its 80-byte array without preserving a terminating zero.
   Binary memory inspection waits indefinitely for a PC reply, with `+` to
   advance and `-` to resend. Thus neither malformed console input nor a
   disappeared host has a general recovery guarantee. Target hardware
   responses, clock timing and external debugger protocol are not qualified.
   [Line editor][v-zdi-command], [binary response wait][v-zdi-binary]

## X004/X005 — Keyboard and mouse device boundaries

The VDP calls `PS2Controller::begin()` with default keyboard/virtual-key-queue
configuration. The authenticated library selects keyboard clock/data
GPIO33/32 and mouse clock/data GPIO26/27, initializes its ULP/RTC transport,
and creates keyboard and mouse objects. Keyboard scan conversion and mouse
updates run in library tasks. On Light 2 the USB-A-shaped keyboard connector
carries PS/2 through the board's conditioning circuit; it is not a USB-host
protocol. Mouse attachment is an external accessory on the second PS/2 port.
[VDP initialization][v-ps2-init], [library defaults][l-ps2-default],
[ULP setup][l-ps2-init], [board evidence](trace-hardware-and-dependencies.md)

1. **X004:** VDP sets UK layout, codepage 1252 and typematic values, and marks
   its own `kbEnabled=true`. The library's separate reset result determines
   actual keyboard availability. Normal `getKeyboardKey` converts virtual
   keys; `handleKeyboardAndMouse` stores VDP variables, invokes keyboard
   callbacks and drains the event queue into P014. Outgoing configuration
   calls set layout, LEDs and typematic behavior; VDP does not check the
   boolean device-command results before sending P013 state. The library's
   LED getters return cached requested values, not a new readback proving
   physical LEDs changed. [VDP keyboard path][v-ps2-key],
   [input/event ownership][v-input], [keyboard controls][v-key-controls],
   [library initialization/cache][l-keyboard]

   The keyboard-variable table incorrectly describes `0x0222` as accepting
   240–1000 and rounding to the nearest 250, and `0x0223` as characters per
   second. The dedicated command documentation and selected source use
   milliseconds: delay accepts 250–1000 and is floored to a multiple of 250;
   repeat interval accepts 33–500. The driver chooses the first supported
   interval at least as large as the requested one, while VDP retains the
   requested `kbRepeatRate`. These stored values are not measured physical
   repeat timing. [Variable-table discrepancy][d-key-vars],
   [documented command units][d-key-control], [VDP setter][v-ps2-key],
   [driver interval encoding][l-typematic]
2. **X005:** VDP begins with mouse reporting disabled. Enable resumes the
   library port and tests `isMouseAvailable`; disable suspends it. The library
   supplies mouse packets/deltas and absolute-position updates; VDP copies
   these to variables, runs a mouse callback and emits P015. A normal MOS
   packet receipt is therefore later than device sampling and may reflect
   callback-modified values. [VDP mouse path][v-mouse],
   [VDP event delivery][v-input], [library packet conversion][l-mouse]
3. Control parameters use the shared timed VDU readers and return early on
   incomplete arguments, without a universal negative reply. Mouse commands
   have differing acknowledgement conditions: enable/disable/reset clear
   delta variables after attempting the action; some settings do so only on
   a helper's successful return. The acceleration helpers mutate library
   values but return false, so those dispatch branches omit their intended
   delta-clear notification. `resetMouse` resets the library device but does
   not set VDP `mouseEnabled`; merely showing the cursor after reset does
   not prove reporting was enabled. This conflicts with the documentation's
   claim that successful reset enables the mouse and its blanket statement
   that all mouse controls send packets. [Mouse controls][v-mouse-controls],
   [helper behavior][v-mouse], [reset and reply documentation][d-mouse]
4. Library `PS2Device::sendCommand` locks the selected port, temporarily
   disables the other port's RX, transmits through `PS2Controller`, and waits
   for the expected reply until its configured command timeout. LED and
   typematic helpers require command/parameter ACKs; reset additionally
   expects self-test success. Device receive helpers stop on a received byte,
   parity/sync/clock error, or timeout. These operations explain why a VDP
   cached settings reply is weaker evidence than successful physical device
   configuration. [Device commands and receive boundary][l-ps2-device],
   [typematic/sample-rate commands][l-ps2-settings],
   [reset self-test][l-ps2-reset]
5. Dedicated device commands are not the only configuration entries.
   `setVDPVariable` routes keyboard layout/repeat/LED settings to the same
   helpers and controls local `controlKeys` handling; its mouse setters
   operate reporting enable, cursor visibility/position and device settings.
   Their notification conditions differ from the dedicated VDU controls.
   Local key processing may enable/disable/toggle printer output, invoke
   selected VDU controls or resume paged mode before event delivery to MOS.
   These are P013–P017/X004/X005/X009 interactions on existing transports,
   not new device links. [Variable controls][v-device-vars],
   [documented settings][d-device-vars], [local key actions][v-input]
6. These are device-driver and VDP boundaries, not firmware traces inside a
   particular keyboard or mouse. They establish configured queue/task and
   command behavior without promising lossless input during a blocked VDU
   session. External device-specific retries, detach/reconnect behavior and
   signal integrity remain bounded by the actual library/device/board evidence.

## X006/X007 — Presentation and audio effects

**X006:** VDP drawing code submits work to vdp-gl canvas/controller objects;
`changeMode` selects 2/4/8/16/64-colour controllers and modelines. Default
controller initialization maps RGB, HS and VS outputs as recorded in the
hardware trace. `changeResolution` explicitly enables background primitive
execution and disables background primitive timeout. Mode failure attempts
to restore the previous mode, then mode 1; this fallback is not a proof that
the monitor displayed a valid frame. Plot completion and buffer-swap waits
are library synchronization, distinct from MOS's physical VS interrupt.
Display-device acceptance, analog levels and every rendering opcode remain
outside this bounded endpoint trace. [VDP controller choices][v-screen-classes],
[setup/failure behavior][v-screen],
[mode fallback][v-mode], [VGA output mapping][l-vga-pins]

The selected mode dispatch also covers legacy mode choices, mode 7 teletext
and explicitly supported double-buffered modes. All use the VGA controller
family. `switchBuffer` requests a buffer swap when double buffered, or queues
a no-op and waits for VSync otherwise; these are P001/P005/P010/P024/X006 paths.
Palette/copper `updateSignalList` delegates to the paletted VGA controller
and does not establish another external GPIO interface. [Mode documentation][d-screen],
[mode branches][v-screen-modes], [buffer synchronization][v-screen-sync],
[palette signal-list entry][v-palette-signal]

**X007:** `initAudio` creates channels and a separate `audioDriver` task.
VDP control/sample operations update channel state; `setSampleRate` replaces
the sound generator under a mutex, reattaches channels and starts output.
For this VGA configuration, the library's automatic selection is DAC on
GPIO25, driven by I2S0/DMA; the reviewed board routes SOUND to its audio
output circuit. Channel/status results concern software state, not acoustic
readback. The library's alternate CVBS/sigma-delta choice is not selected by
this VGA application. Neither speaker/headphone response nor a physical
output feedback channel is present in this trace. Generator replacement/destruction and
driver allocations are source-observed operations; resource failure and
electrical power transitions are not qualified. [VDP audio owner][v-audio],
[DAC selection/start][l-audio-select], [DAC/DMA output][l-audio-dma],
[board route](trace-hardware-and-dependencies.md)

## X008/X009/X010 — Diagnostics, printer and console on T004

| Path | Trigger, sender and receiver | Configuration, interruption and error limits |
| --- | --- | --- |
| X008 diagnostics | VDP diagnostic helpers target `DBGSerial`; an external host displays/captures emitted bytes. | Physical `DEBUG=0` makes ordinary `debug_log` empty, including font/context/sample diagnostic selectors. The buffered-command debug selector calls `force_debug_log` and still emits bytes. ZDI's own unconditional host-print helper belongs to P025 on the same T004. Serial writes do not establish host receipt. [Definitions][v-debug], [forced caller][v-forced], [font][v-font-debug], [context][v-context-debug], [sample][v-sample-debug], [ZDI writer][v-zdi-serial] |
| X009 printer | Primary VDU 2 enables and VDU 3 disables forwarding; VDU 1 reads a following byte and forwards it when printer or console is enabled. Printable characters and selected controls are copied to `DBGSerial` while drawing continues. Local control-key handling can also enable/disable or toggle printer state. | Default off. A missing VDU 1 byte returns on read timeout. This is a serial forwarding service; it neither parses a physical printer protocol nor verifies printed output. [VDU dispatch][v-print-dispatch], [print batching][v-print], [local controls][v-input] |
| X010 console | `VDU 23,0,&FE,n` sets console mode; VDP writes dispatch bytes to `DBGSerial`. Incoming host bytes become synthetic key-down events, except ZDI entry/commands, and then follow the normal event/MOS path. | Default off. It is not an exact raw UART mirror: parameters consumed by normal readers are generally not copied to `DBGSerial` (for example `vdu_colour`), whereas printable batching has explicit additional serial writes. Console input gets priority over a physical key on each poll. No host-protocol boundary protects unrelated console, printer, forced diagnostic and transfer bytes from sharing T004. [Console dispatch][v-console], [key injection][v-ps2-key], [output/parameter distinction][v-print-dispatch], [print and colour reader][v-print] |

ROM download, browser/host flashing, recovery utilities and target-device
firmware remain external peers. Their existence in the official update guide
does not make them additional services implemented by this VDP application.
[Documented external update/recovery tools][d-external-update]

The W4 whole-`video/` entry scan found no active WiFi/Bluetooth/network service
call behind the `WiFi.h` include. `OneWire_direct_gpio.h` supplies the direct
GPIO operations used by ZDI; its name and platform helpers do not establish
an active OneWire device interface. MCU ROM/framework boot output remains
outside this application-source trace. [Main includes][v-main-build],
[ZDI helper include][v-zdi-pins], [ZDI GPIO operations][v-zdi-wire]

No source correction, build, deployment, reset, power or wiring operation was
performed for this trace.

[d-hex]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDU-Commands.md#L355-L405
[d-terminal]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md#L492-L520
[d-update]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/Updating-Firmware.md#L5-L27
[d-update-recovery]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/Updating-Firmware.md#L118-L128
[d-external-update]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/Updating-Firmware.md#L64-L130
[d-key-vars]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDP-Variables.md#L135-L146
[d-device-vars]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDP-Variables.md#L135-L173
[d-key-control]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md#L135-L149
[d-mouse]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md#L151-L256
[d-screen]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Screen-Modes.md#L19-L60
[m-startup]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/main.c#L77-L117
[m-vblank-install]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/main.c#L119-L125
[m-vblank]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/interrupts.asm#L40-L60
[m-gpio-macro]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/macros.inc#L28-L38
[m-clock]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/globals.asm#L86-L94
[d-clock]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L2078-L2082
[v-main-loop]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino#L99-L160
[v-main-config]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino#L53-L108
[v-main-build]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino#L48-L160
[v-build]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/platformio.ini#L11-L39
[v-config]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon.h#L22-L37
[v-system-includes]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L9-L21
[v-device-vars]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h#L53-L159
[v-reads]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L337-L442
[v-packet]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L516-L529
[v-duplex-var]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h#L243-L260
[v-duplex]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_protocol.h#L17-L30
[v-terminal]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino#L219-L340
[v-mode]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h#L301-L336
[v-transfer-select]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L115-L133
[v-hex-helper]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/hexload.h#L28-L32
[v-hex-reader]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/hexload.h#L19-L80
[v-hex]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/hexload.h#L114-L157
[v-hex-records]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/hexload.h#L159-L266
[v-hex-complete]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/hexload.h#L268-L303
[v-y-helpers]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L9-L146
[v-y-block-in]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L152-L239
[v-y-block-out]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L503-L566
[v-y-readfiles]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L297-L343
[v-y-writefiles]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L345-L432
[v-y-session]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L438-L498
[v-y-send]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L568-L724
[v-y-send-end]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L700-L724
[v-y-receive]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h#L726-L826
[v-updater]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/updater.h#L11-L129
[v-updater-end]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/updater.h#L132-L181
[v-local-print]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino#L346-L364
[v-wait]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L47-L65
[v-zdi-wire]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h#L294-L458
[v-zdi-pins]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h#L6-L22
[v-zdi-serial]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h#L262-L291
[v-zdi-init]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h#L1235-L1278
[v-zdi-enter]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h#L610-L661
[v-zdi-execute]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h#L1032-L1051
[v-zdi-command]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h#L1325-L1414
[v-zdi-binary]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h#L1081-L1144
[v-ps2-stubs]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_ps2.h#L31-L39
[v-ps2-init]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_ps2.h#L12-L67
[v-ps2-key]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_ps2.h#L71-L212
[v-key-controls]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L577-L604
[v-input]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L704-L782
[v-mouse]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_ps2.h#L238-L414
[v-mouse-controls]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L608-L725
[v-screen]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h#L186-L265
[v-screen-classes]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h#L38-L47
[v-screen-modes]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h#L265-L467
[v-screen-sync]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h#L469-L491
[v-palette-signal]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h#L85-L92
[v-audio]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_audio.h#L25-L108
[v-debug]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino#L176-L208
[v-forced]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h#L260-L290
[v-font-debug]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_fonts.h#L82-L92
[v-context-debug]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_context.h#L64-L71
[v-sample-debug]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_audio.h#L139-L158
[v-print-dispatch]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h#L16-L74
[v-print]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h#L190-L238
[v-console]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L379-L387
[l-term-default]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.h#L958-L972
[l-term-begin]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L324-L411
[l-term-connect]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L459-L474
[l-term-send]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L1839-L1883
[l-term-queue]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L1925-L1970
[l-term-input]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L2370-L2434
[l-term-keys]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L4617-L4675
[l-term-flow]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L528-L555
[l-term-poll]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L1761-L1790
[l-term-ctrl]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/terminal.cpp#L2518-L2528
[l-ps2-default]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/comdrivers/ps2controller.cpp#L1200-L1215
[l-ps2-init]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/comdrivers/ps2controller.cpp#L1115-L1178
[l-ps2-device]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/comdrivers/ps2device.cpp#L145-L202
[l-ps2-settings]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/comdrivers/ps2device.cpp#L279-L302
[l-typematic]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/comdrivers/ps2device.cpp#L272-L291
[l-ps2-reset]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/comdrivers/ps2device.cpp#L337-L343
[l-keyboard]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/devdrivers/keyboard.cpp#L67-L187
[l-mouse]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/devdrivers/mouse.cpp#L69-L188
[l-vga-pins]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vgabasecontroller.cpp#L90-L145
[l-vga-sync]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vgabasecontroller.cpp#L490-L500
[l-vga-dma]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vgabasecontroller.cpp#L580-L613
[l-audio-select]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/devdrivers/soundgen.cpp#L620-L665
[l-audio-dma]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/devdrivers/soundgen.cpp#L517-L585
