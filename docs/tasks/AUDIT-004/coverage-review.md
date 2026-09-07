# Stock MOS/VDP communication coverage review — W4

[AUDIT-004](../AUDIT-004.md), recorded 2026-09-07. W4 is complete for the
[fixed baseline](baseline-and-research-map.md): MOS v3.0.2, VDP v2.16.0 and the
pinned official documentation. The review reconciles documented interfaces,
source dispatch tables, traffic producers/consumers and configuration branches
with the [inventory](communication-inventory.md) and [endpoint traces](communication-traces.md).
It required corrections within the existing **46 path families and 11 transport
references**, with no additional family identified in the reviewed surfaces.
The [W5 overview](README.md) presents these findings. The Author accepted the
audit on 2026-09-07 with the recorded evidence limits retained.

This is **coverage of communication families and source entry points**, not a
proof of all program behavior. The audit does not certify every opcode's
algorithm, every malformed input, external peer interoperability, a compiled
image, or physical timing/electrical behavior. The task register owns remaining
questions and any later scope decision. No Extender comparison or hardware
conclusion follows from this stock inventory.

## Reconciliation method

1. Revisited the official documentation's MOS and VDP navigation, then reconciled
   the matching selected-source tables, dispatch branches and actual call sites.
   Historical or future documentation was distinguished from implemented
   selected-release behavior. Undefined selectors, pure stubs and runtime gates
   were accounted for rather than silently counted as working interfaces.
2. Independently cross-checked MOS API/CLI/interrupt surfaces, VDP primary
   commands/reverse producers, and VDP peripheral/maintenance/configuration
   surfaces. The VDP entry scan accounted for all 47 files under `video/`,
   including internal rendering, audio and stream helpers; it did not treat
   each helper or unused include as a new external endpoint.
3. Followed indirect producers and alternate stream owners into existing IDs:
   named variables and pathname expansion, filesystem timestamps, callbacks,
   stored commands, terminal processing, transfers and debugging. Schematic
   routes and reached dependency files retain their authenticated identities.
4. Corrected stale W2 summaries and overbroad W3 statements in their owning
   traces. The tables below state the positive coverage; the final section
   states the remaining limits. Nothing was executed on an Agon or peripheral.

## MOS documentation and source coverage

The [API tables and guard][M-DISPATCH] contain 128 ordinary slots: 60 live
entries and 68 direct unavailable entries. The 39 FatFS slots contain 32 live
wrappers and seven pure unavailable wrappers. A live wrapper is not necessarily
a correct implementation: `0xA4` can act before returning an error. Selectors
`0xA7–0xFF` are rejected before dispatch. These counts describe table entries,
not separate communication channels.

| Documentation / source surface | Positive coverage and disposition | Existing IDs |
| --- | --- | --- |
| MOS API: ordinary file/handle/raw-sector and pathname entries; FatFS table | All implemented storage/path entries map to one card path or local file/path state. Conditional variable expansion and timestamp generation also reach RTC traffic. Pure FatFS stubs are `87,88,8C,9D,A0,A1,A5` hex; `A4` is a live fallthrough defect. [Tables][M-DISPATCH], [configuration][M-FFCONF] | A001/A007/A009/X003; T007 and conditional P012/T001 |
| MOS API: keyboard/editor, Sysvars/keymap/flags, callback registration, vectors, RTC, OSCLI, named variables | Every live ordinary-table entry in these groups has a supporting trace. Lookup/error/parsing/string helpers remain local A001 operations; reserved expression and other direct unavailable entries add no endpoint. [Tables][M-DISPATCH], [MOS trace](trace-mos-interfaces.md) | A001–A009, corresponding primary exchanges |
| MOS API: UART1 and I2C | Open/close/read/write, configured pins, CTS handling, interrupt/wait/error ownership; no generic GPIO/parallel protocol or I2C slave service inferred. [MOS trace](trace-mos-interfaces.md) | X001/X002, T005/T006 |
| C-function documentation/table | All 18 slots: 16 nonzero addresses and two reserved null entries. SD operations, FatFS printf/find, UART1 open, named-variable/expansion/path helpers, Sysvars and keymap pointers all map to existing families. C `f_printf` is available despite the RST API's printf stub. [Exact table][M-CFUN] | A001/A003/A009/X001/X003 |
| Star commands, MOS operation, scripts and aliases | All 45 normal command-table entries, reaching 36 distinct handlers, reconciled. File/directory, display, script/conditional, variable, execution and Time commands retain downstream dependencies. Source-only `Disc` changes SD delay selection. Debug test entry is separately gated. [Table][M-CLI], [catalogue][D-CLI] | A002/A004/A007–A010/X003 |
| Named variables and keyboard documentation | Code getter/setter calls, GS/argument expansion, line editing/completion and hotkeys are included. `resolvePath` can expand an RTC-derived variable before a file operation. [Path][M-PATH], [expansion][M-GS], [MOS trace](trace-mos-interfaces.md) | A004/A008/A009/X003 → P001/P009/P010/P012/P013/X010 as selected |
| Executables, RST and interrupt documentation/source | Reset, RST08/10/18/38, execution/return bridges, main-installed UART0/PB1/I2C handlers and application vector replacement accounted for. RST20/28/30, default NMI/maskable handlers and unexposed raw input helpers do not establish another public message service. [Vectors][M-VEC], [MOS trace](trace-mos-interfaces.md) | A001/A002/A005/A006/A010/A011; T001/T002/T006 |
| UART0 sender/parser and indirect producers | MOS output converges on UART0; reverse dispatch has exactly types `00–09`. Startup, editor/palette reads, code variables, timestamps and pathname expansion are included. No stock echo consumer or dynamic UART0 RTS writer found. [Primary trace](trace-primary-protocol.md), [MOS trace](trace-mos-interfaces.md) | T001/P006–P018; A002/A003/A005/A007/A009/X003 |

The documentation's future MOS modules and unified peripheral streams are not
implemented stock services in this baseline. Source-table coverage also excludes
fork-only work and arbitrary register access by separately loaded applications.

## VDP documentation and source coverage

All 13 VDP pages in the pinned documentation navigation were reconciled: VDP
overview, VDU Commands, Screen Modes, PLOT Commands, System Commands, Enhanced
Audio, Bitmaps, Buffered Commands, Context Management, Copper, Font, Tile Engine
and VDP Variables. The rows below group related pages without replacing their
opcode catalogues. Numeric selectors below are hexadecimal unless marked decimal.

| Documentation / source surface | Positive coverage and disposition | Existing IDs |
| --- | --- | --- |
| Overview/VDU: full byte dispatcher | Printable ranges, 00–1F controls and 7F; command-disable/resume, printer/console side effects and VDU23 subgroups. Unhandled control/subgroup values do not imply generic operand skipping or an error reply. [VDU][V-VDU], [system][V-SYS] | P001/P002/P011/P020–P022, X009/X010 |
| System Commands: all `vdu_sys_video` cases | Cursor/display; poll/query/device 80–99; glyph/font/transform; paging/viewport 9A–9F; buffered A0/update A1; coordinates/legacy/tile/swap/Copper/context/completion C0–CA cases; F2/F8/F9/FE/FF. Absent cases, including 97/C5–C7/C9, remain unimplemented. [Dispatch][V-SYS] | P001–P023, X010 |
| PLOT/Screen Modes | Every PLOT operation group reconciled: D0/E0/F0/F8 are unassigned/unimplemented; unsupported groups can still update plot state. Mode/legacy/Teletext, double-buffering and synchronization select the VGA family. Rendering correctness and monitor acceptance remain bounded. [PLOT][V-PLOT], [screen][V-SCREEN] | P001–P005/P010/P024, X006 |
| Bitmaps/Font | Bitmap/sprite selectors and custom mouse cursor creation; font 0/1/2/4/5 decimal implemented, 3 reserved, 10 placeholder and 20 debug. Hardware-sprite gate 2, default hardware choice requiring 0400 plus 2, and automatic mode notifications reconciled. [Sprites][V-SPR], [font][V-FONT] | P002/P010/P015/P016, X005/X006/X008 |
| Context/Tile/Copper | Context 0–7 decimal and debug 80; tile empty cases 02/12/19 versus constants 08/09/0A/0E/0F without dispatch; Copper 0–4 decimal. Gates 0300 (tile) and 0310 (Copper) test presence, not value. [Context][V-CTX], [layers][V-LAYERS], [system][V-SYS] | P003/P005/P010/P016/P017, X006/X008 |
| Buffered Commands | Outer decimal selectors 0–26,32–34,40–41,48,64–65,72,80–81,128; nested adjust/condition/transform/matrix/copy/split/reverse/compression grammars and debug output. Variable 1 gates affine/buffered transform operations. Unknown commands have no general return packet. [Dispatcher][V-BUF], [command trace](trace-command-stream.md) | P003/P004/P016/P017, X008 |
| Enhanced Audio | Outer decimal 0–14; sample 0–8 and debug 10; volume-envelope 0–2 and frequency-envelope 0–1. Command-specific response/no-response behavior, sample-buffer and separate audio-task dependencies retained. [Audio][V-AUDIO] | P004/P011, X007/X008 |
| VDP Variables | Computed versus stored values, context 1000–1FFF, device/event fields, keymap, query state, communication/feature flags and buffered variable reads. Reserved namespaces do not establish future APIs merely because values can be stored. [Variables][V-VAR], [context][V-CONTEXT] | P001–P018 through P004/P016/P017 |
| Callback/output controls | All registration/removal and invocation surfaces, event 0–5 and packet event ranges 0100–017F/0180–01FF, stream selection, suppression, echo and stored-call output restoration. Registration alone does not prove an event producer exists. [Callbacks][V-CB], [storage][V-BUFFERS], [execution][V-CALL] | P004/P016–P018; maintenance P020–P022/P025 |
| Reverse packets | Every normal `send_packet` caller: types 00–09 plus echo 0A/0B. Mode notifications from font/context/variable/display paths included. HEX/YMODEM/ZDI keyboard-formatted packets and raw terminal stream writes have distinct producers, without new packet-type IDs. [Packet/event source][V-PROCESS], [primary trace](trace-primary-protocol.md) | P006–P018/P019–P022/P025, T001 |
| System/VDU/update guidance and maintenance source | Terminal, HEX, both YMODEM directions, updater and ZDI console/command dispatch reconciled from the selected VDP side. External host/eZ80 utilities and ROM/framework download services remain separate evidence boundaries. [VDP trace](trace-vdp-interfaces.md) | P019–P025; T001/T003/T004 |
| Keyboard/mouse/device/display/audio/console controls | PS/2 defaults and command helpers, local control keys, variable setters, VGA controller selection, DAC selection, diagnostics, printer and console all mapped. All direct GPIO and serial consumers found in the application scan fit existing transports. [VDP trace](trace-vdp-interfaces.md), [board/dependencies](trace-hardware-and-dependencies.md) | X004–X010; T004/T008–T011 |

A `WiFi.h` include supplies no active networking service in the selected VDP
application. `OneWire_direct_gpio.h` supplies ZDI GPIO helpers, not an active
OneWire protocol. Library capabilities such as CVBS or sigma-delta audio are
not additional selected application endpoints; the inspected display/audio
construction chooses VGA and DAC GPIO25.

## Corrections incorporated into the traces

| Finding | Effect on the inventory / evidence |
| --- | --- |
| MOS UART0 RTS is statically asserted during setup; CTS is software-polled | VDP's CTS+RTS setting does not establish occupancy-controlled MOS receive backpressure. Manufacturer register definitions now support the direction/polarity interpretation. [Primary](trace-primary-protocol.md), [hardware](trace-hardware-and-dependencies.md); task E15. |
| Keyboard-event addresses differ from documentation | Selected source uses 0260–026F; documented 0250–025F collides with mouse fields at 0250–0255. Selected event fields also allow writes despite read-only prose. [Primary](trace-primary-protocol.md); E17. |
| Keyboard typematic documentation has wrong units/range/rounding | Delay is 250–1000 ms with floor-to-250 behavior; rate is an interval of 33–500 ms, with further device encoding quantization. Cached requests do not prove measured repeat timing. [Primary](trace-primary-protocol.md), [VDP](trace-vdp-interfaces.md); E17. |
| Callback order/lifetime and buffer-call behavior need qualification | Unordered storage does not promise registration order; clearing a buffer does not immediately unregister it. Ordinary cross-buffer calls restore output, while same-buffer recursion and tail-call jumps differ. [Command](trace-command-stream.md), [primary](trace-primary-protocol.md); E16. |
| Before-send callbacks depend on producer | Normal query/event producers invoke them; maintenance helpers that call `send_packet` directly skip them. After-output-attempt processing remains shared and proves no MOS receipt. [Primary](trace-primary-protocol.md); E16. |
| FatFS API A4 setlabel falls through | The label operation may occur before status 23 is returned. Distinct from seven pure FatFS stubs and from the already recorded raw-write dispatch defect. [MOS](trace-mos-interfaces.md); E18. |
| Mouse documentation overstates enable/reply behavior | Reset does not set VDP `mouseEnabled`; selected acceleration handlers return false and skip their intended notification. Source behavior was traced in W3; W4 makes the opposing documentation explicit. [VDP](trace-vdp-interfaces.md); E17. |
| Processor document and PB1 interrupt semantics resolved | The authenticated F92/F93 manual matches the inherited hash; the conflicting link is an L92 manual. PB1 is configured for rising-edge interrupts and the data-register write clears the request. Older board-PDF bytes remain unidentified. [Hardware](trace-hardware-and-dependencies.md); E03. |

Earlier findings E05–E14 remain in force: unsupported MOS echo reception,
eight-byte mode payload, output-attempt semantics, startup/session pacing,
API lookup status, block-count units, external-peer limits, parser defects,
raw API 73 read dispatch and RTC wait/indirect-producer behavior. These are
selected-source observations, not repair instructions or automatically adopted
Extender requirements.

## Configuration and lifecycle coverage

| Configuration | Established source boundary | Unverified boundary |
| --- | --- | --- |
| MOS selected Release/F92 build declarations | Startup API/vector/driver selection and boot configuration; DEBUG=0 excludes the conditional CLI test command. | No fresh build, binary identity or compiler ABI experiment. |
| VDP physical `esp32dev` | One declared PlatformIO environment; no USERSPACE/VDP_USE_WDT define; physical source forces DEBUG=0. Forced buffered diagnostics and ZDI host printing still write T004. | No new framework resolution/build; ROM/framework boot output is outside the application scan. |
| VDP USERSPACE source branches | ZDI implementation replaced with stubs; HEX returns immediately; startup/debug/scheduler glue differs. YMODEM and updater source/dispatch are not guarded away. | No emulator implementation selected or execution claimed for those unguarded services. |
| Experimental VDP_USE_WDT | Commented option; default disables core watchdogs. Conditional reset occurs at the main-loop top, which blocking maintenance does not reach until return. | Registration, deadline and recovery guarantee not established by that toggle. |
| Runtime flags, terminal and maintenance sessions | Presence/value distinctions, mode/legacy/feature selection, parser/output owner and inherited pacing are traced. | Exhaustive state combinations, recursion/callback mutation and interrupted-session recovery not tested. |
| Physical attachments/reset | Rev B schematic routes; mouse/ZDI pin overlap; shared board reset net distinguished from MOS, ESP32 and ZDI software actions. | Actual specimen, jumper/attachment state, reset sequencing and simultaneous accessory operation not established. |

Build/lifecycle citations and detailed branch evidence are in the
[baseline](baseline-and-research-map.md), [MOS trace](trace-mos-interfaces.md),
[VDP trace](trace-vdp-interfaces.md) and [board record](trace-hardware-and-dependencies.md).

## Explicit remaining evidence limits

1. **External peers:** terminal software, HEX/YMODEM utilities, `agon-flash`,
   host debug/download tools, peripheral firmware and card/device-specific
   behavior have no selected implementation baseline. Stock-side exchanges are
   traced; end-to-end interoperability is not established (task E11).
2. **Reached dependencies:** authenticated files establish the described UART,
   terminal, PS/2, VGA and audio boundaries. Deeper ESP-IDF UART/OTA/reset behavior,
   RTC-library internals, full driver algorithms and eZ80 debug-register
   semantics remain outside those traces (E04/E11).
3. **Historical board provenance:** the explicit Rev B PDF is authenticated;
   the older mismatching byte hash has no recovered source artifact. It is not
   evidence of a circuit revision change (E03).
4. **Configuration and execution:** no fresh compiled image, alternate build,
   compiler plain-char ABI check, exhaustive opcode/operand matrix, or proof of
   callback mutation/recursion correctness was produced (E19).
5. **Measurement questions:** configured rates, queue sizes and timeout
   constants do not establish delivered throughput, interrupt latency, packet
   loss, stalled-peer recovery, rendered/displayed completion, clock rate across
   modes, device reconnect behavior or signal quality. Cold/shared reset,
   VDP-only restart and interrupted session behavior remain specimen-dependent
   measurement questions, alongside UART/I2C/SD/device failures (E19).

The actionable disposition of E19 belongs to the task register. W5 presents
these limits for Author review; no measurement campaign is authorized here.
The held r02 design is still incomplete, its full wiring incomplete and its
complete circuit untested. W4 performed no firmware modification, build,
emulator or bench operation, and supplied no basis to resume that hardware work.

## Pinned source references

[D-CLI]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Star-Commands.md
[M-CFUN]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2340-L2360
[M-CLI]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c#L91-L140
[M-DISPATCH]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L156-L350
[M-FFCONF]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_fatfs/ffconf.h
[M-GS]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_sysvars.c#L486-L550
[M-PATH]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_file.c#L218-L277
[M-VEC]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/vectors16.asm#L65-L168
[V-AUDIO]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_audio.h
[V-BUF]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h
[V-BUFFERS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/buffers.h#L9-L17
[V-CALL]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h#L327-L473
[V-CB]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h#L2747-L2770
[V-CONTEXT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/context.h
[V-CTX]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_context.h#L12-L74
[V-FONT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_fonts.h#L12-L94
[V-LAYERS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_layers.h#L15-L239
[V-PLOT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/context/graphics.h#L650-L782
[V-PROCESS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h
[V-SCREEN]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h
[V-SPR]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sprites.h#L12-L229
[V-SYS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h
[V-VAR]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h
[V-VDU]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h
