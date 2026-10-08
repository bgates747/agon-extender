# PORT-008 — UART parking development results

## Executive summary

F02c2a supplies real EMOS register leaves and a native P4 SDK adapter for
suspending UART on the shared data pins. Target builds and host/linked eZ80
checks pass. The leaves remain private and unbound: ExExt admission, coordinated
startup/recovery and the physical parallel adapter are still required. No bench
access, flashing, SD changes or production promotion occurred.

The Author's preceding commit instruction was fulfilled before implementation:
Extender `2098c791` and EMOS `3237404` were pushed. This new emulator-coupled
tranche remains uncommitted for Author review.

## What changed

1. EMOS reserves its existing packet serializer and Port C lifecycle lock.
   A partial receive packet, active transmitter, pending fault or competing
   owner prevents parking. TEMT checks the shift register, not just the FIFO.
   An acknowledging LSR error read becomes a retained fault request.
2. EMOS retains logical keyboard ownership while parked. Its assembly byte and
   block transmitters, receive parser/IRQ, C completion/RTS tail, close/stop
   paths and timer reject or defer work that could touch shared pins. Held keys,
   packet state, baud rate and FIFOs survive normal suspension.
3. EMOS uses UART MCTL internal loopback to disconnect external RX before
   releasing the UART mux. This is receive isolation, not a transport test:
   TX is already empty and cannot run while parked. Interrupt masking alone
   would leave the receiver listening to parallel payload edges.
4. P4 checks software RX occupancy, hardware FIFO and TX shift-register idle,
   isolates RX/CTS through the GPIO matrix, and releases both UART output pads.
   Restore requires explicit local and peer release proofs. A partial restore
   failure attempts release of both outputs and leaves a sticky failure.
   No FIFO flush, driver deletion or synthetic key release manufactures quiet.
5. The P4 leaf requires its caller on the UART ISR installation core. Local
   interrupt exclusion then prevents an ISR from moving a byte between FIFO
   and software ring during inspection. The current console startup installs
   UART separately from its core-0 processing task; F02c2b must arrange the
   required affinity before using this adapter. Merely passing a core number
   is not proof of correct installation.

## Decisive source contracts

1. Zilog **PS015317-0120**, UART MCTL table, printed page 119: LOOP disconnects
   external RX and connects internal TX to RX. Printed page 120 documents
   LSR/TEMT. Reviewed local `PS0153-eZ80F92-eZ80F93-Product-Specification.pdf`.
   Official Agon GPIO and MOS UART API documentation remain the public
   contract; these leaves introduce no MOS API number.
2. ESP-IDF **5.5.5**, commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`:
   `components/esp_driver_uart/src/uart.c`, `uart_release_pin`, `uart_set_pin`,
   `uart_get_buffered_data_len`, `uart_wait_tx_done`; P4 `hal/uart_ll.h`.
   RX constant-high isolation reuses the driver's idiom. CTS is deliberately
   held high/blocked during parking. `uart_set_pin(..., -1, ...)` means no
   change, not release; rebinding actual pin numbers restores the matrix.

## Validation

| Check | Result | Boundary |
|---|---|---|
| Linked eZ80 parking | 289 cases pass | Actual linked park/restore, serializer/Port C locks, all LSR values, partial packet refusal, late IRQ/TX, register ordering, IX/SP/IFF |
| P4 SDK adapter | 196 cases pass under address/undefined sanitizers | Real adapter source; scripted SDK boundary, core mismatch, queue/FIFO/shift-register busy, failure cleanup |
| Existing eZ80 byte TX | 221,184 cases per image pass | Prior build versus candidate, port operations, results, ABI and IRQ state |
| Existing eZ80 block TX | 375 comparisons pass | Exact/partial sends, deadlines, owner/fault loss, frozen clock |
| Existing eZ80 complete IRQ | 1,302 comparisons pass | FIFO bound, callback behavior, register/IRQ preservation |
| Existing eZ80 parser | 8,683,703 comparisons pass | Headers, lengths, bounds, callback mutation, ownership |
| EMOS host checks | Receiver variants, 9 parallel and 6 provenance tests pass | Includes partial-packet and retained-key behavior; ordinary and telemetry profiles |
| Paired handover / reverse cores | 5,208 / 48 cases pass | Existing simulated endpoint regressions |
| P4 profile tests | 11 pass | Maintained source/profile closure |
| EMOS full wrapper | Pass; 130,135 bytes | All required linked ownership, ABI and routing checks; **937 bytes remaining** |
| Native P4 build | Pass | P4-PC browser profile; new adapter compiles against the pinned SDK; no live caller |

EMOS grows **509 bytes** over the preceding 129,626-byte image. Normal byte
transmit attempts gain two interpreted instructions (successful path 29–31
becomes 31–33). This is instruction-count evidence, not elapsed target time,
UART throughput or user-input latency. Physical performance remains unmeasured.

The stale EMOS provenance test's exact source list omitted the already-committed
handover unit; that expectation was updated. The linked pin-writer inventory
now admits only the two added leaves' exact Port C write sequences. No ownership
check was removed. Initial preparation/test-environment mistakes have no retained
diagnostic claim.

## Remaining gate

F02c2b must bind these leaves to the paired handover machines, negotiated
session/sequence/direction/length, complete queue/event draining, shared deadlines
and actual boot/reset pin fences. A UART in-flight start bit cannot be ruled out
by an empty FIFO alone: matching peer quiescence is mandatory. No unnegotiated
peer may trigger a pin handover. F02c3 still owns native PARLIO and the assembly
payload loop; F03 owns electrical and timing validation after bench release.

Artifacts and source hashes are in [UART-PARKING-RESULT.json](UART-PARKING-RESULT.json).
Local build/test evidence is retained under ignored `agents/port008-uart`;
timed checks use host monotonic seconds, not an eZ80 clock calibration.
This was instruction-emulator validation, not a full-system Fab boot.
