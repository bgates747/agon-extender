# Stock primary UART and reverse protocol — W3/W4

This bounded trace covers `AUDIT-004-T001` and `AUDIT-004-P006`–`P018` in
the [communication inventory](communication-inventory.md). It uses the fixed
[W1 identities](baseline-and-research-map.md): MOS v3.0.2 at `8336409351ee5314e02801a7b72a4f1bb5282519`,
VDP v2.16.0 at `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, and official docs at
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. Arduino-ESP32 wrapper evidence is
2.0.14 at `44da992b774f76777bb2e931dd76cfcf12b9fe70`, authenticated separately
against official Git objects. No reference source was modified.

Official [VDP operation][D-OV], [system commands and reverse protocol][D-SYS],
[VDP variables][D-VAR], [buffered output/events][D-BUF], [audio commands][D-AUD],
and [MOS result APIs][D-API] were read before implementation tracing. Source
observations below establish what these selected sources request or execute;
they are not electrical measurements or runtime tests. This record incorporates
W4 corrections; the [coverage review](coverage-review.md) states the audit's
scope and limits. Other primary families and application/device details have
their own traces. The hardware hold remains in force.

## T001 — shared transport, execution context and initialization

1. MOS sends ordinary VDU bytes through the [RST 10h/18h handlers][M-RST]
   and [`UART0_serial_PUTCH`][M-PUTCH]; C `putch` uses that same serial routine.
   The forward stream has no transport-level command envelope, sequence
   number or whole-command lock in these entry routines. Command handlers
   determine argument lengths. The official [stream description][D-STREAM]
   requires callers to avoid interleaving commands and payloads.
2. MOS [startup][M-START] installs its UART0 receiver before enabling
   interrupts, then opens UART0 with 1,152,000 baud, 8 data bits, one stop bit,
   no parity and hardware flow control. [UART setup][M-UART] configures eZ80
   PD0/PD1 for TX/RX and PD2/PD3 for RTS/CTS alternate functions, writes
   `UART0_MCTL=0x02`, enables/clears FIFOs with `FCTL=0x07`, and enables the
   requested receive interrupt. W4's authenticated
   [processor and board evidence](trace-hardware-and-dependencies.md) establishes
   that `MCTL=0x02` asserts RTS low and the TX routine polls inverted CTS status.
   No selected MOS receive path updates RTS according to receive occupancy.
   These settings therefore do not establish automatic bidirectional receive
   backpressure. The board source supplies Rev B routes, not a specimen's state.
3. VDP [configuration][V-CONFIG] declares TX GPIO2, RX GPIO34, RTS GPIO13,
   CTS GPIO14. [Protocol setup][V-PROTO] selects `Serial2`, 8N1 and the same
   baud rate, requests a 256-byte receive buffer, assigns the control pins,
   initially requests **RTS-only hardware flow control**, and sets the stream
   timeout to 200 ms. Later MOS requests CTS+RTS through P016. The source's
   “half/full duplex” names refer to flow-control selection here; the byte
   interface has both transmit and receive directions throughout.
4. The control threshold passed to `setHwFlowCtrlMode` is **64**, not the
   separate `UART_RX_THRESH=128` declaration. Arduino [buffer/mode wrappers][A-CONFIG]
   and [UART HAL setup][A-HALSET] pass the requested sizes/settings to the
   ESP-IDF UART driver. VDP does not check the flow-control or buffer-setting
   return values. Therefore these numbers describe requested configuration,
   not a measured capacity or guaranteed successful configuration.
5. VDP [setup/processLoop][V-MAIN] constructs one main stream processor with
   input, output and original output all initially referencing `VDPSerial`,
   then runs its processing task on core 0. It initializes keyboard/mouse,
   waits for eZ80 synchronization, and normally calls `processNext` repeatedly;
   terminal mode diverts this loop. [The processor][V-LOOP] drains queued
   events before keyboard/mouse handling and again after a command. Buffered
   commands can run within this context; reverse packets are not restricted
   to explicit eZ80 queries.
6. MOS [transmission][M-TX] polls CTS when configured, without a timeout in
   that wait. Its lower TX helper has a bounded iteration count, but
   [`UART0_serial_PUTCH`][M-PUTCH] retries that helper until it succeeds. This public
   blocking path has no overall transmit deadline. It reports UART-disabled
   failure rather than sending when the enable flag is clear. UART register
   acceptance is not a VDP command-completion acknowledgement.
7. VDP [single-byte reads][V-READ] poll the input and return `-1` after the
   configured tick interval; words read low byte then high byte using a fresh
   byte wait for each. The 200 ms value is not a whole-command deadline.
   `readByte_b` waits indefinitely for availability. `readIntoBuffer` calls
   the stream's `readBytes`, retries once after a zero-byte read, and reports
   remaining bytes on failure; its own `timeout` argument is not used to
   change the stream timeout. Arduino [read wrappers][A-IO] use the stream
   timeout for `readBytes` and zero timeout for individual `read` polls.
8. Arduino [write wrappers][A-IO] return the requested byte count; [the HAL][A-HALIO]
   calls `uart_write_bytes` without propagating its result. VDP's `writeByte`
   also ignores the result. ESP-IDF driver internals, scheduling, hardware FIFO
   limits, and the duration of blocked writes remain explicit lower-layer
   boundaries here. There is no source-level delivery acknowledgement added
   by these wrappers.

## T001 — reverse framing, MOS receiver and failure limits

VDP [send_packet][V-SEND] sends `type+0x80`, a single length byte, and payload
bytes through the current output stream. Multi-byte normal payload fields
are little-endian. This envelope has no checksum, sequence identifier or
MOS acknowledgement. The function accepts a 16-bit length but serializes the
length as one byte; the ordinary types below fit within MOS's 16-byte packet
buffer. Configurable echo is discussed separately under P018.

MOS's [UART0 interrupt handler][M-IRQ] disables interrupts, reads one byte and
passes it to [the parser][M-PARSE]. It does not drain a software ring in this
handler or inspect receive error bits; it also does not branch on the RX
routine's “no byte available” carry result. [The RX routine][M-RX] checks data
ready and reads the hardware receive register. Actual interrupt-cause and
line-error consequences require the peripheral evidence boundary above.

The parser has header, length, body and discard states. In header state it
ignores bytes below `0x80`; inside a payload, high-bit bytes are ordinary data.
It copies accepted-length payloads into a single reusable [buffer][M-BSS]
whose [size constant is 16 bytes][M-EQUS],
and dispatches types `0x00`–`0x09`. Receipt handlers copy results into MOS
SysVars and, for seven families, OR a result flag into the shared flag byte.
They do not queue independent result records. Initialization clears this BSS
state through [C startup][M-CSTART].

The following are **source-observed failure properties**, not bench results:

1. The parser accepts lengths zero through 16 without checking each type's
   required payload length. A known type with too short a payload still runs
   its handler, which reads the other bytes retained in the reusable buffer.
   Thus the flag alone does not establish that a complete valid result arrived.
2. For length greater than 16, the stock parser changes to discard state
   **without storing the received length**. Discard then decrements the old
   `_vdp_protocol_len`. In the ordinary post-reset/post-completed-packet case
   that old value is zero, so the byte counter wraps and discards 256 following
   bytes before returning to header state. This is the stock defect whose
   separate fork fix was excluded from W1; no fix is applied by this audit.
3. There is no elapsed-time timeout in the MOS parser. An interrupted payload
   continues consuming later bytes as its remaining body. Unknown types with
   an accepted length are consumed then ignored; an oversize unknown type
   reaches the same defective discard branch. Header scanning resumes only
   when the state machine returns to header state. This is not a general
   resynchronization guarantee.
4. [Result wait][M-WAIT] polls up to 250,000 iterations for all requested flag
   bits and returns `FR_OK` or `FR_TIMEOUT`. The source comment's approximate
   one-second duration is not a measured limit. A timeout neither cancels the
   command nor resets/drains either parser; a late result can still arrive.
   [Flag APIs][M-FLAGS] clear selected bits and call this wait. A result flag
   identifies a family, not a request instance, so automatic notifications
   or multiple requests of one family require caller coordination.
5. VDP command handlers commonly return when a required argument times out,
   without a generic error packet or discarded-remainder envelope. Later
   bytes can therefore enter normal dispatch as new command bytes. Not every
   handler checks timeouts consistently; P013/P016 identify concrete cases.
   Source inspection supplies no universal interrupted-command recovery
   guarantee.

## P006–P015 — request/event to observable MOS result

In the table, `w` means a two-byte little-endian word; lengths count payload
bytes only. The common T001 sender/receiver, timeout and framing rules above
apply to every row. Except where explicitly stated, family responses can
also be redirected or suppressed by P017. The MOS handlers linked in the
last column complete the processor-to-processor trace; application APIs and
callbacks are separately indexed by the inventory's A rows.

| ID | Initiator, forward request or event production | VDP return and MOS effect |
| --- | --- | --- |
| P006 | MOS `wait_ESP32` repeatedly emits `23,0,&80,1` until `_gp` is nonzero. VDP `wait_eZ80` consumes bytes, dispatches VDU 23 commands, and `sendGeneralPoll` reads the poll byte, sets its VDP variable, invokes the before-send callback and sends it back. Startup is the documented use. [MOS][M-POLL], [VDP][V-POLL] | Type `00`, length 1: poll byte. `vdp_protocol_GP` writes `_gp`; there is no pflag. VDP marks itself initialized after the send attempt and then sends mode info. MOS has no overall poll deadline; blocked TX can stop it before another poll. VDP skips poll waiting after `ESP_RST_SW`, based on its assumption MOS already runs. [Receiver][M-GPKEY], [startup branch][V-BOOT] |
| P007 | MOS/application sends `23,0,&82`. VDP runs its before-send callback then reads the current context's normalized text cursor coordinates. [Sender/producer][V-CURSOR] | Type `02`, length 2: `x,y`. MOS copies `_cursorX/_cursorY`, sets bit 0. No receipt queue or request ID. [Receiver][M-RESULTS] |
| P008 | `23,0,&83,xw,yw` uses character coordinates; `&93` uses graphics coordinates. Both check argument timeouts, call the context's screen-character reader, store the result variable, run a callback and serialize that variable. The [character-coordinate method][V-CHARCOORD] accepts byte coordinates although the command reader reads words. Screen/font recognition details remain rendering-method dependencies. [Dispatch][V-QUERY], [producer][V-CHAR] | Type `03`, length 1: character byte. MOS `vpd_protocol_SCRCHAR` writes `_scrchar`, sets bit 1. A callback may change the stored character before serialization. [Receiver][M-RESULTS] |
| P009 | `&84,xw,yw` waits for plot completion, reads a pixel, sets colour/position variables, invokes read-pixel and before-send callbacks. `&94,index` reads palette/current colours into the same result variables; an unrecognized active-colour selector returns without a packet. MOS's `readPalette` clears bit 2 before sending and optionally waits, but discards the wait return. [Producer][V-PIXEL], [MOS helper][M-QUERY] | Type `04`, length 4: `R,G,B,index`. MOS copies `_scrpixel` and `_scrpixelIndex`, sets bit 2. A response represents the variables after callbacks; it has no echoed query coordinates. [Receiver][M-RESULTS] |
| P010 | Explicit `&86`, VDP startup, mode changes and selected viewport/context/text-positioning changes call `sendModeInformation`. The ordinary mode-change path reports the resulting mode even after its fallback attempts. MOS `getModeInformation` clears bit 4, sends the query and waits; startup additionally spins until `_scrcolours!=0`, without its own deadline. [Producer][V-MODE], [mode transition][V-MODECHANGE], [other calls][V-MODECALLS], [MOS][M-QUERY], [startup][M-START] | Type `06`, **length 8**: `widthw,heightw,cols,rows,colours,mode`. MOS copies all eight bytes, including `_scrmode`, then sets bit 4. This resolves E06: the official summary omitted the final mode byte. It also means this flag can be set by automatic notifications. [Receiver][M-MODE] |
| P011 | `&85,channel,command,args` dispatches audio operations. Commands 0–14 call operation helpers and return command-specific status; command 1 queries a status bitfield. Sample loading reads a 24-bit length then uses buffer upload. Argument timeout returns before a status is sent. Unknown outer commands have no default response; unknown sample actions return status 0; the sample-debug action only logs. [Dispatch][V-AUDIO], [sample load/status producer][V-AUDIORESULT], [docs][D-AUD] | Type `05`, length 2: `channel,status`. MOS copies `_audioChannel/_audioSuccess`, sets bit 3. The `_audioSuccess` name does not make every status Boolean, nor does the packet indicate playback completion. Before-send callback runs, but the producer retains its local channel/status values; the source explicitly leaves variable-based replacement as TODO. [Receiver][M-RESULTS] |
| P012 | `&87,0` reads RTC; `&87,1,y,m,d,h,m,s` sets it. MOS `rtc_update` is conditional on `rtc_enable`, clears bit 5, sends read and waits. `mos_SETRTC` emits the six setter bytes. VDP checks each setter byte, interprets year as signed offset from 1980 and calls `rtc.setTime` only for resulting year ≥1970; set sends no acknowledgement. [MOS read/unpack][M-CLOCK], [MOS set][M-RTCSET], [VDP][V-RTC] | Type `07`, length 6: a packed 32-bit value followed by seconds and year-offset bytes. Low-to-high packed fields are month(4), day(5), weekday(3), yearday(9), hour(5), minute(6). MOS copies six bytes into `_rtc`, sets bit 5; `rtc_unpack` uses matching masks and a plain-`char` cast for the year offset; compiler plain-char signedness is not established here. ESP32Time calendar/validation behavior remains a library boundary. [Packing][V-TIMEPACK], [receiver][M-RTC] |
| P013 | `&81,locale` calls keyboard layout selection; `&98,on` toggles control keys; **neither sends type 08**. Only `&88,delayw,ratew,led` sets repeat/LED state and calls `sendKeyboardState`. Delay is retained unless within 250–1000 ms, then rounded down to a multiple of 250 ms; repeat interval is retained unless within 33–500 ms; LED 255 preserves LED state. These are source parameter rules, not measured response times. The locale handler does not check `-1`: missing locale narrows to 255 and selects the default UK branch. [Locale dispatch][V-LOCALE], [control-key dispatch][V-KEYINPUT], [status producer][V-KBCONFIG], [layout/state helpers][V-KBHELP] | Type `08`, length 5: `delayw,ratew,led`; both words use milliseconds. MOS copies five bytes into `_keydelay/_keyrate/_keyled` and sets **no pflag**. VDP reports its stored settings, not the keyboard's encoded repeat interval or command-success result. [Receiver][M-RTC], [stored settings][V-KBSTATE] |
| P014 | Physical/library virtual-key events and console injection enter `getKeyboardKey`; `&99,key` injects an updated virtual-key state into the keyboard library. VDP updates event variables, runs keyboard callback/control-key handling, then drains the event queue. [Input/query][V-KEYINPUT], [event production][V-KEYEVENT] | Type `01`, length 4: `keycode,modifiers,vkey,down`. Queue entries carry an event type; serialization samples current variables after before-send callback. MOS calls the registered `_user_kbvector` first, then copies fields, increments `_keycount`, and invokes `keyboard_handler` to update the keymap and process Ctrl+Alt+Delete. No pflag. Ordinary key retrieval sees MOS state, not a queue of all received packets. [VDP serialization][V-EVENTS], [MOS receiver][M-GPKEY], [keymap/reset][M-KEY] |
| P015 | `&89,subcommand,args` controls mouse state; movement is obtained through `mouseMoved`, updates VDP variables and triggers a hardware-event callback. State setters enqueue a mouse event. Enable/disable/reset/cursor/position cases queue via zeroed deltas; sample-rate/resolution/scaling/acceleration cases queue only when their helper succeeds. Unsupported area command reads its arguments but sends no result. Thus the docs' “all commands” response statement is too broad. [Commands][V-MOUSE], [variable scheduling][V-MOUSEVAR], [events][V-KEYEVENT] | Type `09`, length 10: `xw,yw,buttons,wheelDelta,deltaXw,deltaYw` in current OS coordinates. MOS copies ten bytes from `_mouseX` onward, sets bit 6. Receipt is not proof of a successfully attached mouse: e.g. enable queues data even if enable fails. Before-send callbacks may replace the variables. [Serialization][V-EVENTS], [receiver][M-RTC] |

**W4 typematic qualification (P013/P016).** The [system-command docs][D-KBCONFIG]
correctly describe milliseconds, but the [variable table][D-KBVARS] incorrectly
labels `0x0223` as characters per second and gives `0x0222` a 240 ms minimum
with nearest-250 rounding. The source instead uses the bounds and floor
rounding above. The reached keyboard [wrapper][L-KB-TYPEMATIC] calls
`PS2Device::send_cmdTypematicRateAndDelay`, whose [encoding table][L-TYPEMATIC]
rounds the repeat interval up to the first supported entry at least as large
as requested (for example, 34 ms becomes 37 ms). VDP retains the requested
in-range interval and ignores the library's Boolean success result. A type08
response therefore does not establish the keyboard's applied timing.

**W4 event-variable qualification (P014–P017).** The pinned [variable docs][D-EVENTVARS]
place keyboard event fields at `0x0250–0x025F`; the selected [source constants][V-EVENTIDS]
instead assign `0x0250–0x0255` to mouse positions/deltas in OS coordinates and
keyboard fields to `0x0260–0x026F`. Event production and packet serialization
use the source constants. Following the documented keyboard IDs can therefore
read or alter mouse state. The docs also mark mouse buttons/wheel and keyboard
event fields read-only, but the [setters][V-EVENTSET] permit stored updates.
Button/wheel writes queue mouse events; individual modifier, virtual-key and
down-state writes queue keyboard events. Combined modifiers update individual
modifier fields; individual modifiers also update the combined field. Other
keyboard payload/scancode fields can be stored without automatically queueing
an event. These source paths support callback payload editing; they do not
change physical key/button state or make every variable writable.

The event queue's [pushUnique implementation][V-QUEUE] suppresses another
pending event of the same type. `processEventQueue` retains the current entry
while callbacks run, then removes it; callback setters therefore do not
immediately requeue that same type. The event holds no immutable copy of the
payload: keyboard/mouse variables are read at dispatch. This is intentional
state coalescing in the selected source, not evidence that every physical
event becomes a distinct packet. Keyboard input processing drains the queue
after each retrieved keyboard item; nested buffered command processing
deliberately does not drain it itself. [Execution order][V-LOOP].

## P016–P018 — communication-changing controls

1. **P016, variables and flow control.** MOS [poll startup][M-POLL] sends
   `23,0,&F8,&0101w,1w` after seeing the poll response, then requests the Shift
   key state. VDP [variable setter][V-VARS] calls `setVDPProtocolDuplex(true)`
   before storing the variable. Clearing it calls the false/RTS-only variant.
   There is no dedicated protocol acknowledgement for this setting. This
   resolves E08 for normal selected-release startup: one-way hardware flow
   control is the VDP initial configuration, not the later MOS-requested
   configuration. HEX/YMODEM session inheritance is traced with those paths.
   A VDP-only software reset reruns RTS-only setup but skips waiting for MOS's
   poll; this code alone supplies no guarantee that an already running MOS
   reissues its variable settings.
2. **P016 malformed arguments.** [The `&F8/&F9` dispatch][V-VARDISPATCH] does
   not test `readWord_t` for `-1` before passing values to unsigned 16-bit
   setter/clearer arguments. A fully read variable ID `0x0101` with a timed-out
   value consequently requests nonzero/CTS+RTS mode; a missing ID can become
   `0xFFFF`. This is a source-inferred partial-command effect, not a tested
   hardware transition. It prevents a claim that all incomplete commands are
   ignored without state change.
3. **P017, selected output.** [Set-output][V-OUTPUT] selects null for buffer ID
   65535, the processor's original output for 0, or the first block of
   an existing buffer, if that block is writable. Invalid/nonwritable buffers
   leave the output as it was. [writeByte][V-OBJECT] silently does nothing for null and does not check
   successful bytes written otherwise. Parent/nested command-stream ownership
   and buffer-call restoration belong to P004's trace. The main processor
   restores original output on a VSYNC check with no pending input
   ([processNext][V-LOOP]); continuous traffic need not reach that condition.
4. **P017, packet events.** Normal query/event producers invoke their
   before-send callbacks before serializing data. HEX/YMODEM and auxiliary ZDI
   keyboard senders call `send_packet` directly, without that before-send step;
   their after-send event still follows the shared function. See the
   [session trace](trace-vdp-interfaces.md). [send_packet][V-SEND] first tests the presence of
   variable `0x0103`, clears it and returns if present; [the presence test][V-PRESENCE]
   makes even value zero count as suppression. Otherwise it attempts every
   output byte and invokes the after-send callback. Thus E07 resolves to
   **VDP after-output-attempt**, not
   “received from MOS” or MOS receipt. A null/full/failing output is not
   distinguished by `send_packet`; suppression skips the after-send callback.
   Producer-specific limits matter: audio retains its local arguments,
   cursor/mode read live context, RTC reads the clock, while key/mouse and
   colour/character/poll payloads sample variables after callbacks.
   **W4 qualification:** callbacks are stored and iterated as an unordered set,
   so source does not guarantee the [documentation's registration order][D-CALLBACKS].
   Buffer clearing does not unregister callbacks immediately; an attempt to
   call a missing buffer removes its registrations. Clearing and recreating
   the same ID before that attempt can retain the callback. [V-CALLBACKS],
   [V-CALLBACK-STORE], [V-CALLBACK-LIFETIME]
5. **P018, echo.** Echo starts disabled. Setting `0x0110` nonzero enables
   buffering; VDP flushes accumulated selected command/text bytes into type
   `0x0A` packets. System and sprite/transfer dispatches clear echo rather than
   promising a literal copy of every received byte. [Echo code][V-ECHO] uses
   `0x0102` as configured chunk size, falling back to 16 if zero. Disabling
   first flushes and may emit type `0x0B`, length 1, with the previous nonzero
   handle's low byte. [Enable/end handling][V-ECHOSTATE], [setter ordering][V-VARS].
   MOS [type dispatch][M-PARSE] consumes accepted-length `0x0A/0x0B` packets
   and ignores their unsupported types; it has no spool/echo consumer. This
   resolves E05 as VDP-side functionality with no stock MOS consumption.
   Configuring chunks above 16 also reaches MOS's oversize defect; lengths
   above 255 exceed the serialized one-byte length even on the VDP side.
   Neither effect is enabled by ordinary MOS startup.

## Evidence disposition and remaining boundaries

E05–E07 are resolved at the selected source level as described above. E08 is
resolved for normal startup and must retain the transfer-session distinction.
The newly observed parser length defects, missing argument checks, unchecked
write results and command-specific response exceptions are source findings;
they authorize no fixes or hardware changes. The owning task records any
follow-up disposition.

This trace stops at the ESP-IDF UART driver, ESP32Time calendar implementation,
and detailed keyboard/mouse/rendering library methods where explicitly
identified. W4 separately authenticates reached eZ80 UART/GPIO semantics;
rendering/audio device effects, all opcode validation and physical timing are
not proved by this family-level UART trace. Board reset/power routes have separate schematic
evidence in the [board trace](trace-hardware-and-dependencies.md), with no
specimen or sequencing guarantee. Source links establish reproducible
evidence, not a production qualification or exhaustive program verification.

## Pinned source references

[D-OV]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/VDP.md
[D-STREAM]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/Theory-of-operation.md#limitations
[D-SYS]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md#vdp-serial-protocol
[D-VAR]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDP-Variables.md#L98-L111
[D-KBCONFIG]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md#L133-L145
[D-KBVARS]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDP-Variables.md#L135-L146
[D-EVENTVARS]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDP-Variables.md#L154-L200
[D-BUF]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Buffered-Commands-API.md#L166-L195
[D-CALLBACKS]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Buffered-Commands-API.md#L860-L880
[D-AUD]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Enhanced-Audio-API.md
[D-API]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1250-L1288
[M-RST]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/vectors16.asm#L112-L160
[M-START]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/main.c#L177-L210
[M-POLL]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/main.c#L77-L125
[M-UART]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/uart.c#L37-L95
[M-TX]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm#L76-L112
[M-PUTCH]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm#L197-L263
[M-RX]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm#L141-L152
[M-IRQ]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/interrupts.asm#L62-L78
[M-PARSE]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/vdp_protocol.asm#L70-L162
[M-BSS]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/globals.asm#L86-L160
[M-EQUS]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/equs.inc#L22-L30
[M-CSTART]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/cstartup.asm#L35-L55
[M-WAIT]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c#L3140-L3155
[M-FLAGS]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1626-L1648
[M-GPKEY]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/vdp_protocol.asm#L164-L199
[M-RESULTS]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/vdp_protocol.asm#L201-L265
[M-MODE]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/vdp_protocol.asm#L267-L299
[M-RTC]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/vdp_protocol.asm#L301-L346
[M-QUERY]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_editor.c#L47-L68
[M-CLOCK]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/clock.c#L55-L88
[M-RTCSET]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c#L3015-L3035
[M-KEY]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/keyboard.asm#L23-L80
[V-CONFIG]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon.h#L24-L35
[V-PROTO]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_protocol.h#L17-L30
[V-MAIN]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino#L99-L155
[V-OBJECT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L261-L290
[V-READ]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L333-L442
[V-SEND]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L514-L529
[V-EVENTS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L531-L583
[V-LOOP]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L585-L644
[V-BOOT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L45-L65
[V-POLL]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L389-L404
[V-CURSOR]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L413-L428
[V-QUERY]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L174-L255
[V-CHAR]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L430-L439
[V-CHARCOORD]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/context/fonts.h#L189-L207
[V-PIXEL]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L441-L497
[V-MODE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L532-L549
[V-MODECHANGE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h#L301-L336
[V-MODECALLS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h#L73-L166
[V-AUDIO]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_audio.h#L25-L231
[V-AUDIORESULT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_audio.h#L233-L258
[V-RTC]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L513-L573
[V-TIMEPACK]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L29-L43
[V-KBCONFIG]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L575-L604
[V-LOCALE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L406-L411
[V-KBHELP]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_ps2.h#L69-L212
[V-KBSTATE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_ps2.h#L194-L212
[V-KEYINPUT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L272-L285
[V-KEYEVENT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L704-L769
[V-MOUSE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L606-L726
[V-MOUSEVAR]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h#L104-L209
[V-EVENTIDS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon.h#L468-L501
[V-EVENTSET]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h#L136-L260
[V-QUEUE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/utils/thread_safe_variant_deque.h#L35-L44
[V-VARS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h#L243-L275
[V-PRESENCE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h#L306-L349
[V-VARDISPATCH]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L370-L378
[V-OUTPUT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h#L451-L473
[V-CALLBACKS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h#L2748-L2773
[V-CALLBACK-STORE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/buffers.h#L11-L19
[V-CALLBACK-LIFETIME]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h#L327-L438
[V-ECHO]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L646-L702
[V-ECHOSTATE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h#L303-L318
[A-CONFIG]: https://github.com/espressif/arduino-esp32/blob/44da992b774f76777bb2e931dd76cfcf12b9fe70/cores/esp32/HardwareSerial.cpp#L599-L625
[A-IO]: https://github.com/espressif/arduino-esp32/blob/44da992b774f76777bb2e931dd76cfcf12b9fe70/cores/esp32/HardwareSerial.cpp#L510-L555
[A-HALSET]: https://github.com/espressif/arduino-esp32/blob/44da992b774f76777bb2e931dd76cfcf12b9fe70/cores/esp32/esp32-hal-uart.c#L162-L225
[A-HALIO]: https://github.com/espressif/arduino-esp32/blob/44da992b774f76777bb2e931dd76cfcf12b9fe70/cores/esp32/esp32-hal-uart.c#L340-L436
[L-KB-TYPEMATIC]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/devdrivers/keyboard.h#L326-L337
[L-TYPEMATIC]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/comdrivers/ps2device.cpp#L272-L291

## Firmware bug register cross-reference — 2026-09-20

[FWBUG-010](../../firmware-bugs.md#fwbug-010), [FWBUG-011](../../firmware-bugs.md#fwbug-011). These stable bug identities supplement the original
finding IDs and evidence. Registration does not authorize repairs or turn
source-only findings into hardware reproductions. Use the same FWBUG ID for
any future dedicated disposal task; current dispositions remain in the register.
