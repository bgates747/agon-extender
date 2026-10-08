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

### Current bounded increment — F02c1, 2026-10-08

Implement and test the two private ownership sequencers before attaching
either to UART/GPIO. EMOS and EDP will request a transmit fence, wait for
software queues **and the shift register** to drain at a packet boundary,
release their shared pads, and acknowledge release on the dedicated controls.
Test both directions, delayed peers, failures, reset during every phase and
queued keyboard traffic with simulated adapters; execute EMOS's compiled
sequencer on the eZ80 instruction emulator. No changes to ordinary UART
startup, ISR, keyboard state or mode admission in this increment. The real
adapters and admission envelope remain F02c2 work; native PARLIO and the
assembly payload loop remain F02c3 work.

The sequencers are deliberately not new generic transport frameworks. Each
is a small transition function with explicit completed-adapter inputs and
requested-adapter actions. No transition function may treat a requested pad
release as completed. A deadline enters release/recovery, never blindly
restores UART. A failed cleanup stays fenced. Only the EMOS coordinator may
authorize a block after matching session/sequence/direction/length admission;
these functions do not encode or accept UART records themselves.

CLOCK distinguishes setup/return (low) from the byte-clock phase (initially
high). During setup PARLIO must remain disarmed, so changing CLOCK is not a
payload edge. UART idle is CLOCK low, VALID high, READY high. Entry is:
EMOS releases pads then VALID low; P4 releases pads then READY low; EMOS VALID
high; P4 READY high; EMOS CLOCK high; P4 arms the block then READY low. All
levels are held until the reciprocal acknowledgement. This separates the
release acknowledgement from payload readiness even with slow task polling.

After the block P4 stops DMA/releases its pads before READY high. EMOS then
releases its pads before CLOCK low/VALID high. EMOS observes READY high,
requests a fresh release acknowledgement with VALID low, and waits for READY
low. EMOS then restores its UART subset and raises VALID; P4 restores its
disjoint UART subset and raises READY. UART completion status requires the separately
matched admission descriptor; pad release alone never establishes success.

Cold start/reset uses the same return handshake, starting with **all shared
pads as inputs**, CLOCK low and VALID high. Neither CPU may restore its UART
outputs merely because the other looks idle. Tests model reset by dropping
the reset CPU's physical output enables as well as discarding its RAM state.
The physical boot fences, bounded polling source, UART/ISR serialization and
PARLIO's first/last-byte behavior remain mandatory before activation. This
model assumes working wires and honest adapters, not electrical fault tolerance.
P4 reset/cancellation announces recovery with READY low after its own release,
then raises READY only after CLOCK low/VALID high. This makes an otherwise
idle EMOS join recovery instead of silently assuming P4 retained its session.
The exact states, adapter contracts and limits are in [HANDOVER.md](HANDOVER.md).

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
   output. A UART ACK alone or a fixed delay is insufficient. F02c1 implements
   the candidate truth table with simulated adapters; F02c2 must bind it to
   actual completed UART/pad operations, including the boot path.
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

## Current UART integration slice — F02c2a, 2026-10-08

The Author authorized development after preserving F02c1; the bench remains
unavailable. Implement real register/SDK leaves but keep them unreachable from
ordinary startup and CLI mode switching. This bounds review of shared-pin and
IRQ behavior before adding wire admission and bootstrap recovery in F02c2b.

1. EMOS reserves the existing serializer and Port C lifecycle lock before
   suspending. No competing sender, selector or raw UART API may steal it.
   Normal pause must not synthesize key releases, clear parser state or flush
   received bytes. A partial packet or UART transmitter not fully empty keeps
   the request pending. Preserve errors acknowledged by LSR reads.
2. Keep EMOS keyboard ownership logically held while parked. Use a private
   parked owner state; guard byte/block output, receive IRQ, IRQ RTS tail,
   close/stop and timer processing before any shared-pin mutation. Resume only
   after caller-owned reciprocal release proof. Do not infer it from delay.
3. P4's single UART owner must fence new submissions and reach a complete
   packet boundary before parking. Require actual TX completion and no pending
   RX bytes, disconnect UART inputs while the pads carry parallel data, and
   explicitly release the two UART output pads. Restore only its UART subset
   after peer release. Retain queued keyboard events; no simulated disconnect.
4. Test ordinary behavior as well as parked behavior. Use actual eZ80 linked
   IRQ/TX code, register-access traces and deterministic delayed/failed SDK
   operations. Target builds include the dormant leaves for type/link checking.
   Host tests cannot establish peripheral timing or physical high impedance.
5. No ExExt command, new wire opcode or boot path is activated by these leaves.
   Full phase deadlines, mutual admission and reset fences remain c2b. The old
   active-UART exclusion in the forward adapter stays intact. C2a is not a
   complete ExExt implementation or permission to use an old circuit adapter.


F02c2a implementation and checks are recorded in
[UART-PARKING-RESULTS.md](UART-PARKING-RESULTS.md). EMOS's documented MCTL
loopback isolates external RX while TX is fenced and empty; P4 uses the
SDK's GPIO-matrix constant-input idiom. The P4 caller must share its UART
ISR installation core to make FIFO/ring inspection indivisible against that
ISR. Current startup/task affinity must be reconciled in F02c2b, not assumed.
The leaves remain unbound and both endpoints still require negotiated peer
quiescence: a local empty FIFO does not prove the other CPU has stopped.
