# PORT-008 — Bidirectional development contract

## Executive summary

The 2026-10-08 authorization permits EMOS and EDP development and emulator/host
checks, not bench access. Reuse all eleven P4-PC harness signals and the proved
forward clock mechanism. First implement bounded reverse block cores in the
owning repositories. Then add coordinated UART/pad ownership and the native
adapter. No new application API, enabled ExExt command or file-transfer claim
follows from compiling these cores. PORT-008 F02a–d own the remaining work.

## Source and scope

The [prototype report](FORWARD-PROTOTYPE-REUSE.md) records measured forward
evidence, source identities and the current harness. Official
`agon-docs/docs/GPIO.md` confirms Port C/Port D exposure; the Zilog product
specification and existing EMOS GPIO helpers supply register semantics.
ESP-IDF 5.5.5 `esp_driver_parlio/include/driver/parlio_tx.h` defines external
clock input, TX shift edge, completion and explicit disable. TX idle data is
not high impedance. See the [Espressif TX reference](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/parlio/parlio_tx.html).

EMOS implementation belongs in sibling `agon-emos`, under INTEG-016. P4
implementation belongs in `vdp/video/extender/transport`. Existing forward
engines, UART keyboard handling and ordinary Legacy/ExCom remain unchanged.
The first reverse C loop is a correctness reference, not a throughput claim;
the production hot loop should use the existing assembly sender's idioms.

## Block-level candidate

| Signal | EMOS/eZ80 → P4 | P4 → EMOS/eZ80 |
|---|---|---|
| PC0–PC7 | EMOS drives; P4 receives | EMOS inputs; P4 transmits |
| PD5 CLOCK | EMOS clocks, P4 samples falling edge | EMOS clocks, candidate P4 shifts falling edge; EMOS reads after rising edge |
| PD7 VALID_N | EMOS asserts for bounded record | EMOS asserts for bounded record, releases after final read |
| PD4 READY_N | P4 grants receive capacity | P4 grants armed transmit block; releases only after DMA stopped and outputs released |

Both parties agree direction and exact nonzero length, at most 4096 bytes,
before the block. EMOS owns CLOCK and VALID in either direction. Idle CLOCK
is high; every byte has one falling and one rising edge. No READY polling per
byte. The candidate TX adapter must preserve the final byte until EMOS releases
VALID (including any PARLIO idle-data behavior); DMA completion alone must not
release pads or signal completion. First-byte alignment and final-byte hold
remain hardware gates. No assumptions about automatic driver tri-state.

An EMOS receive failure invalidates the entire destination block even if a
prefix was written. No partial payload is published as a successful read.
READY release acknowledges pad release, not a successful/validated payload.
The integrated coordinator must obtain the matching sequence/length/status
on resumed UART before publishing success; a P4 timeout also releases pads.
The existing checked/fast file-service policy will still own file integrity.
EDP retains the caller's immutable buffer until DMA is stopped. Both cores
reject nested work, enforce capacity/length and bound stalled clocks. Neither
core commits an operating mode or opens a physical bus by itself.
The caller must retain its existing atomic writer/lifecycle lock; the C engine's
busy flag does not replace that interrupt-safe ownership gate. The P4 backend
must latch VALID start/end edges per block, since a complete transfer may occur
between task polls. Completion publication may lag the final VALID edge;
the core waits within its deadline rather than diagnosing that delay as loss.

## Required integration before activation

1. **EMOS admission:** only its mode coordinator may request a parallel block.
   The existing service serializer must reject competing UART transactions.
   UART request/reply IDs and sequence checks remain to be assigned within the
   existing namespace; the first cores introduce no private wire protocol.
2. **P4 quiescence:** queue keyboard/reply output, drain actual UART shift
   registers as well as software/FIFO queues, disable TX and RTS pin drivers.
   EMOS must likewise drain UART1 and release PC0/PC2. Preserve incoming packet
   boundaries and keyboard state; do not discard partially received packets.
3. **Ownership acknowledgement:** use dedicated READY/VALID phase transitions
   to confirm both endpoints have released UART before either enables a data
   output. A UART ACK alone or a fixed delay is insufficient. The complete
   phase truth table remains F02c; block READY is not yet that table.
4. **Return:** EMOS finishes/stops CLOCK, releases VALID and its data outputs.
   P4 stops DMA and releases all eight data pads before READY completion.
   Restore the UART mux only after the reciprocal release acknowledgement.
   Bound blocks and resume queued input/control between blocks.
5. **Fault/reset:** cancel DMA and explicitly release drivers on every failure.
   Cleanup failure cannot advertise reusable pins. Reopening requires fresh
   admission; stale RAM/sequence state is insufficient. Reset of either CPU
   while the peer drives requires a boot-time fence before ordinary UART
   outputs are enabled, plus independently bounded P4 release. This is a
   required integration item, not established by host testing.
6. **Interrupts:** do not inherit the legacy fixture's long DI window. Audit
   UART ISR/RTS writers and reentrant VDU callbacks before mux changes. Use
   short atomic ownership transitions; benchmark the assembly payload loop
   only after correctness and input recovery are established.

## Verification and stop boundaries

### Existing integration seams found in the review

| Owner/source | Reuse or required change |
|---|---|
| EMOS `src/emos_parallel.c` and `emos_parallel_io.asm` | Retain the atomic Port C lifecycle/writer gate; existing forward entry deliberately rejects an active UART1 owner. Do not bypass this check to get ExExt running. |
| EMOS `src/uart.c`, `uart1_keyboard_stop/close/open` | Existing stop/close behavior is fault/release handling, not a transparent suspend/resume protocol. Add an explicitly reviewed suspension path preserving packet/key state. |
| EMOS `src/emos_keyboard_io.asm` | UART IRQ and transmit paths access shared Port C/RTS; fence them before changing pad direction, preserving the existing bounded interrupt policy. |
| EMOS `src/emos_console.c`, `emos_console_wire.h` | Current version-1 console control uses a 16-byte CRC-protected record, operations 1–5. Do not repurpose existing fields/operations silently for direction/length. |
| EDP `transport/console_hardware.inc`, `beginConsole/runConsole` | Existing single UART/parser owner and queued USB/network input are the integration point. `uart_wait_tx_done` exists; RX flush is not a TX drain. Startup currently enables UART unconditionally after the input fence, so reset recovery needs a new coordinated guard. |
| EDP board header generated from `vdp/build/boards/p4-pc.json` | Select current direct wiring. Old `p4_parallel_target_config.hpp` includes obsolete DevKit buffer-enable pins and must not be reused unchanged. |

These are F02c integration work, not additional queue items. In particular,
the private block engines do not authorize calling the old buffered-circuit
adapter on the direct P4-PC harness.

Host tests execute the maintained cores with deterministic peer operations:
exact patterned bytes, first/last byte, boundary lengths, failure injection,
deadline wrap/stall, premature end, missing peer and busy callers. A paired
test must execute both cores in one simulated exchange. Native P4 compilation
checks target types; linked eZ80/CPU emulation checks actual compiler output
where feasible. Emulation cannot establish real GPIO timing or contention.

No deployment, serial port, device network request, reset, SD access or GPIO
drive is permitted while the bench is occupied. Keep ordinary production and
the current installed images untouched. Preserve unrelated working-tree dirt.
Emulator-coupled changes remain uncommitted pending Author validation.
