# AUDIT-005 W1 — Source identities and active communication paths

Recorded 2026-09-10. W1 only: this establishes the comparison for
[AUDIT-005](../AUDIT-005.md); it does not rank overhead, recommend replacement
code or establish the cause of the observed lag.

## Selected sources

| Role | Exact selected source | Verification and limits |
| --- | --- | --- |
| Stock MOS (M) | v3.0.2, `8336409351ee5314e02801a7b72a4f1bb5282519` | Official checkout clean and detached at this tag. Official remote tags and the [latest release](https://github.com/AgonPlatform/agon-mos/releases/tag/v3.0.2) agree. |
| Stock VDP (V) | v2.16.0, `c7ac293d2aa81ddfa693390549bcd909069c8fc3` | Official checkout clean and detached at this tag. Official remote tags and the [latest release](https://github.com/AgonPlatform/agon-vdp/releases/tag/v2.16.0) agree. |
| Official documentation (D) | `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` | Clean checkout; living documentation snapshot, not a release-specific guarantee. Same selection as AUDIT-004. |
| EMOS (E) | v0.1.12, `82929c4b3e64c370d1102f46f61e8b600d57d665` | Project-owned checkout clean; HEAD equals the source commit in the deployed build manifest. All 240 recorded source-file hashes match the commit. |
| EMOS build adapter | `mos-agondev`, `85a3be5eea1d97cc2a8f336179e8c2f410731498` | Clean checkout matches the recorded builder commit; all 125 builder source hashes match. EMOS uses the AgonDev build/assembly preparation route; stock's declared ZDS II build is a separate provenance boundary. |
| P4 console (P) | r07, `52479f0ae9653e293031a1eed1b65f0cec9695cd` | All 6,439 source hashes recorded in the P4 manifest match the commit. All 5,314 recorded files under `vdp/` also match the current checkout. |
| Extender checkpoint | `258d0d9` | Later than P4 source, with documentation/evidence changes only. This audit's task/TODO/log edits are separate uncommitted documentation. |

The remote checks used read-only `git ls-remote --tags --refs` and official
latest-release pages on 2026-09-10. No fetch, checkout, reset or source edit
was performed in the reference or firmware repositories. No baseline mismatch
prevents this comparison. The stock references are source selections; W1 does
not claim to have read the current mainboard VDP flash.

## Deployed-build provenance

The retained local bundles were hashed directly. Every output listed below
matches its saved build manifest. This verifies the saved artifacts and their
recorded provenance, not a new readback of either powered board.

| Artifact | Recorded identity and integrity |
| --- | --- |
| EMOS image | `agon-emos-v0.1.12-b2026-09-10-03-50-35Z`, candidate; 130,219 bytes; SHA256 `2c261e290cd3e9af44a168775eabef4a514cf3262d9391fc4ce3dfe414ed5a77` |
| EMOS manifest | SHA256 `e24c430831d6a0aa90863257a479d772c1d0e3de7d2740957d9584e072552429`; records source E and the builder above, both clean at build time |
| EMOS supporting outputs | Matching `.elf`, `.map` and boot-smoke binary also verified. They remain available for W2; no new build or disassembly was performed. |
| P4 image | `uart-excom-console-r07-b2026-09-10-06-31-58Z`, candidate; factory SHA256 `8d6e97577632b1e70d7fcafef985fb433533893097d49e41ee641cfbc3c5fb40` |
| P4 manifest | SHA256 `8ae8dacd6a23282e37d7a3cf31791028d41f921113fbc7234887fe2ee5c382ed`; records clean source P |
| P4 supporting outputs | Matching application image, ELF and dependency lock also verified. W1 does not rebuild or requalify managed dependencies. |

[EMOS installation evidence](../../../hardware/designs/light2-harness-r03/tests/QUAL-003-2026-09-10-04-02-44Z/README.md)
records the Author's successful flash and the matching consumed SD payload.
[P4 deployment evidence](../../../hardware/designs/light2-harness-r03/tests/PORT-003-2026-09-10-06-32-58Z/README.md)
records verified r07 flashing, and the
[subsequent observation](../../../hardware/designs/light2-harness-r03/tests/PORT-003-2026-09-10-06-33-58Z/README.md)
records ExCom/slideshow function and unresolved typing latency. Neither is a
Nurples performance benchmark. Private bundle locations and verification
details are retained in ignored `agents/audit-005/w1-verification.json`.

## Documented contracts read before tracing

1. [D: MOS API][d-api]: `RST 10h` accepts a byte in A; `RST 18h` accepts a
   pointer and a count, or a delimiter when the count is zero. The documented
   stream return values and ADL/address rules belong to the comparison.
   AUDIT-004 already records a stock count-mode A-result discrepancy; W1 does
   not resolve or alter it.
2. [D: keyboard access][d-keyboard] and the API's `mos_setkbvector` /
   `mos_getkbmap` entries: applications use callbacks, sysvars, blocking key
   input or a held-key map. The callback runs in receive-interrupt context.
3. [D: VDP Serial Protocol][d-protocol]: replies/events carry a high-bit command
   byte, length and payload; MOS publishes the associated sysvars and flags.
   Keyboard payload is four bytes; keyboard settings payload is five bytes.
   The opcode list omits the wire command's high bit in its presentation.
4. [AUDIT-004 MOS trace](../AUDIT-004/trace-mos-interfaces.md) supplies existing
   ABI/flow-control context. Source is consulted here because instruction
   paths, receive ownership and EMOS dispatch are implementation details.

## Compact stock-versus-EMOS path map

M and E symbols below refer to the exact source commits above. Both forward
routes execute in the application's or MOS CLI's foreground call context;
there is no eZ80 background transmit task on these paths. UART writes admit
bytes to the peripheral, not proof of EDP rendering or browser presentation.

| Entry / effect | Stock MOS path | Active EMOS path and execution context |
| --- | --- | --- |
| One ordinary byte, `RST 10h` | `_rst_10_handler` → `UART0_serial_PUTCH` → optional `UART0_wait_CTS` → `UART0_serial_TX` → UART0 THR. [M vectors][m-vectors], [M serial][m-serial]. | `_rst_10_handler` → `EMOS_vdu_PUTCH`. Legacy selects retained UART0; ExCom selects `EMOS_vdu_console_PUTCH` → `emos_console_write_byte` → `emos_console_write_stream` → `emos_keyboard_send` → `transmit` → `uart1_keyboard_put` → UART1 THR. [E vectors][e-vectors], [E serial][e-serial], [E console][e-console], [E keyboard][e-keyboard], [E UART][e-uart]. |
| Counted stream, `RST 18h`, BC nonzero | `_rst_18_handler_0` loops through caller memory and calls `UART0_serial_PUTCH` for each byte. [M vectors][m-vectors]. | `_rst_18_handler_0` → `EMOS_vdu_WRITE`. Legacy runs the retained UART0 byte loop; ExCom uses `EMOS_vdu_console_WRITE` → `emos_console_write_stream` → `emos_keyboard_send`, whose loop calls `transmit`/`uart1_keyboard_put`. The outer C bridge is entered once per counted block, not once per byte. [E vectors][e-vectors], [E serial][e-serial], [E keyboard][e-keyboard]. |
| Delimited stream, `RST 18h`, BC zero | `_rst_18_handler_1` checks each byte against E and calls `UART0_serial_PUTCH` until the delimiter. [M vectors][m-vectors]. | The delimiter loop remains in `_rst_18_handler_1`, but each emitted byte calls `EMOS_vdu_PUTCH`; ExCom therefore follows the single-byte bridge above. [E vectors][e-vectors]. |
| MOS C `putch` / ordinary CLI output | `_putch`/`putch` assembly wrapper → `UART0_serial_PUTCH`. [M serial][m-serial]. | `_putch`/`putch` assembly wrapper → `EMOS_vdu_PUTCH` → committed route. This is a separate entry from the counted-stream path. [E serial][e-serial]. |
| Mainboard keyboard packet | UART0 IRQ → `_uart0_handler` → `UART0_serial_RX` → `vdp_protocol` framing/dispatch → `vdp_protocol_KEY` → user callback → sysvar publication → `keyboard_handler` held-map/reset handling. [M IRQ][m-irq], [M protocol][m-protocol], [M keyboard][m-keyboard]. | UART0 IRQ and assembly framing remain; KEY dispatch calls `emos_keyboard_mainboard`. If mainboard input is selected, `publish` → `emos_keyboard_effect` → `emos_keyboard_payload` → callback and sysvars → retained `keyboard_handler`. Settings use a separately gated path. These calls execute under the UART0 interrupt, with expanded register saving around C. [E IRQ][e-irq], [E protocol][e-protocol], [E keyboard][e-keyboard], [E bridge][e-bridge]. |
| Extender keyboard packet | Stock exposes general UART1 APIs but does not route UART1 packets into its VDP keyboard receiver. | P4 UART1 TX → eZ80 UART1 IRQ → `_emos_keyboard_irq_entry` → `uart1_keyboard_irq` → `emos_keyboard_byte` private framing → `dispatch` → `publish` → the same shared keyboard effects described above. `uart1_keyboard_irq` controls PC2 RTS while draining RX. [E bridge][e-bridge], [E UART][e-uart], [E keyboard][e-keyboard]. |
| Display replies / sysvars | UART0 IRQ → stock framing → `vdp_protocol_vector` → cursor, pixel, mode and other effect handlers. [M protocol][m-protocol]. | UART1 IRQ → private framing → `emos_console_packet`. Active, owned display replies pass through `effect` → `emos_vdp_effect` → `emos_vdp_dispatch` and the retained effect handlers. `effect` saves/restores the shared stock payload buffer; transition publication can invoke it with interrupts masked. During ExCom, UART0 display effects are filtered while independently selected keyboard/settings remain eligible. [E console][e-console], [E console bridge][e-console-io], [E protocol][e-protocol]. |
| Mainboard VBlank / MOS clock | `_vblank_handler` increments `_clock` by two per interrupt. [M IRQ][m-irq]. | The clock increment remains; the IRQ additionally calls `emos_keyboard_tick_entry` → `emos_keyboard_tick` for pending source return, partial-packet expiry and cleanup. This is distinct from foreground transmission and P4 logical frame execution. [E IRQ][e-irq], [E bridge][e-bridge], [E keyboard][e-keyboard]. |

The stock `UART1_serial_PUTCH` / `UART1_serial_TX` routines already exist
([M serial][m-serial]) and are reached by `mos_api_uputc`
([M API source][m-api]). EMOS retains that API but rejects its raw UART1 path
while the resident keyboard/console transport owns UART1
([E serial][e-serial]). Thus this routine is a comparison candidate, not the
routine currently transmitting ExCom graphics and not a supported application
bypass. Whether it can be adapted while preserving the resident contract is W2.

## P4 boundary and execution owners

1. [P: console hardware][p-console] configures UART1 for 1,152,000 baud,
   8N1, RTS/CTS, a 4,096-byte receive buffer and RX flow-control threshold 64.
   Under the [r03 wiring](../../../hardware/designs/light2-harness-r03/README.md),
   eZ80 PC0 TX feeds P4 GPIO22 RX; P4 GPIO12 TX feeds eZ80 PC1 RX.
   P4 GPIO11 RTS feeds eZ80 PC3 CTS; eZ80 PC2 RTS feeds P4 GPIO23 CTS.
2. [P: `processLoop`][p-main] is pinned to core 0 at priority 3. In this
   composition it runs `runConsole`, which owns USB-event pumping, UART
   receive/parser service and transmission of queued replies. In active ExCom,
   `VDUStreamProcessor::processNext` reads through
   [P: `ConsoleStream`][p-stream]; writes queue replies for UART transmission.
3. Drawing reaches the retained parser/controller interfaces. A separate
   [P: frame-service task][p-frame] invokes
   [P: `executeFrameWork`][p-display], which also publishes requested browser
   snapshots. This marks the rendering/snapshot boundary for W2; W1 neither
   measures its cost nor proposes new scheduling or core ownership.

## W1 result and handoff

The selected official references remain clean. EMOS source and builder match
the recorded deployed build; the later Extender checkpoint has no P4 source
drift. Saved binaries and source manifests verify. The path table distinguishes
stock routines retained, EMOS bridges, private receive framing, foreground
calls and interrupt/task contexts. It does not establish their timing cost.

No audit findings or repair instructions are issued in W1. No source repair,
build, test fixture, SD operation, firmware deployment, serial capture or
hardware reset was performed. A separately labelled notification emulator
alerts the Author to this document; it is not validation evidence. W2 awaits
the Author's next instruction.

[d-api]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md
[d-keyboard]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Keyboard.md
[d-protocol]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md
[m-vectors]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/vectors16.asm
[m-serial]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm
[m-irq]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/interrupts.asm
[m-protocol]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/vdp_protocol.asm
[m-keyboard]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/keyboard.asm
[m-api]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm
[e-vectors]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src_startup/vectors16.asm
[e-serial]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/serial.asm
[e-console]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/emos_console.c
[e-keyboard]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/emos_keyboard.c
[e-uart]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/uart.c
[e-irq]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/interrupts.asm
[e-protocol]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/vdp_protocol.asm
[e-bridge]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/emos_keyboard_io.asm
[e-console-io]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/emos_console_io.asm
[p-console]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/extender/transport/console_hardware.inc
[p-stream]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/extender/transport/console_stream.hpp
[p-main]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/video.ino
[p-frame]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/extender/display/p4_frame_service.cpp
[p-display]: https://github.com/bgates747/agon-extender/blob/52479f0ae9653e293031a1eed1b65f0cec9695cd/vdp/video/extender/display/p4_display_controller.cpp
