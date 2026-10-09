# PORT-008 — UART reservation and owner-core results

F02c2b2 passes both target builds, real-source host checks and linked eZ80
instruction checks. EMOS can now retain its existing serializer reservation
from before an offer through UART recovery and final status. P4 installs its
UART interrupt on the existing console task's core. These are prerequisites,
not a live parallel connection. No bench operations occurred.

EMOS uses **130,791 bytes**, leaving **281 bytes** below the 128 KiB limit.
Remaining coordinator work must reuse or replace existing code before adding
more machinery. No linker limit, ownership guard or production selection changed.

## Current private integration contract

1. EMOS calls `emos_keyboard_parallel_reserve` before offering a block. It
   acquires the existing serializer and Port C writer guard only with interrupts
   enabled, a UART owner, a packet boundary and no pending stop/fault.
2. While held, only `emos_keyboard_parallel_send` may submit control bytes. It
   reuses the ordinary bounded transmitter and deadline. A temporary executing
   state rejects recursive sends, parking and release from callbacks. This
   private API is not exposed through a MOS command or application gateway.
3. EMOS parks only after its coordinator proves peer quiescence. Busy/error
   parking retains the reservation. Successful UART restoration also retains
   it: ordinary writers cannot precede completion/status or recovery decisions.
   Release is explicit and requires UART restored, with no private send active.
4. Partial/failed TX requests the existing deferred fault path. Neither private
   nor ordinary `emos_keyboard_send` may append data while that fault or stop
   is pending. The coordinator must invalidate uncertain sessions rather than
   replay them. These leaves do not implement that coordinator.
5. P4's `beginConsole` configures pins/registers and constructs an inactive
   stream. `runConsole`, on existing process core 0, installs the UART driver
   before consuming events. The task and helper share one core constant; the
   helper refuses execution on another core. The identity banner follows driver
   startup. No new task, queue, baud rate or cross-core RPC was introduced.

The core requirement follows ESP-IDF 5.5.5's UART driver contract: the interrupt
is attached to the core calling `uart_driver_install`. See the vendored
`components/esp_driver_uart/include/driver/uart.h` in the selected native build
dependency (commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`), and the maintained
[`console_uart_owner.hpp`](../../../vdp/video/extender/transport/console_uart_owner.hpp).
The constructor review found no UART read in `VDUStreamProcessor` construction;
the console stream remains inactive before its existing session exchange.
Physical startup/input timing after this core change still needs qualification.

## Checks

| Check | Result | Scope and limit |
|---|---|---|
| Linked eZ80 reservation | 22 cases pass | Exact control TX, public/reentrant refusal, late partial RX, park/restore/status fencing, one-byte failure, bounded CTS timeout, IX/SP/IFF |
| Linked eZ80 parking | 289 cases pass | All LSR values, exact release/restore writes, late IRQ/TX and retained reservation |
| Linked public sender comparison | 375 cases pass | Admission build versus this candidate: same bytes, ports, deadlines, error/timeout outcomes and ABI |
| Linked complete UART IRQ comparison | 1,302 cases pass | Same effects and instruction count; primary/shadow registers, callbacks, stack and IFF |
| Actual keyboard C harness | Pass in ordinary and telemetry configurations, ASan/UBSan | Reservation, callbacks during send, errors and asynchronous serializer exclusion |
| P4 owner helper | Eight SDK combinations and startup linkage check pass, ASan/UBSan | Actual helper, wrong core, install/timeout failures, exact install arguments |
| Paired handover regression | 5,208 cases pass | Modeled peripheral completions, delayed peers, reset/cancel and queued input |
| Native profile checks | Eleven tests pass | Maintained source/profile ownership |
| EMOS full wrapper | Pass | All UART, Port C, keyboard, console, ABI and VDU guards |
| P4 native wrapper | Pass | P4-PC browser profile; frozen source closure, unchanged-source rebuild and maintained validator |

The linked checks use synthetic register/tick models, not wall-clock timing or
a full-system Fab boot. The ordinary 65,535-byte ready send changes from
2,293,841 to 2,293,863 interpreted instructions: **22 per call**, not per byte.
The complete sampled 16-byte UART IRQ remains 288 instructions. No hardware
throughput or latency claim follows from these counts.

| ROM measure | Admission baseline | Reservation candidate | Difference |
|---|---:|---:|---:|
| Image bytes | 130,551 | 130,791 | +240 (+0.184% of baseline) |
| Free bytes below 131,072 | 521 | 281 | −240 |

## Evidence and reproduction

The [machine-readable record](UART-RESERVATION-RESULT.json) hashes component
sources, tests, images and build evidence. Local logs and exact build snapshots
are retained under ignored `agents/port008-reservation`. Both images are
unversioned development checks, not deployable production selections.

From the Extender root:

```sh
.venv/bin/python -m unittest discover -s ../agon-emos/tests -p test_emos_keyboard.py -v
.venv/bin/python tests/console_uart_owner_test.py
.venv/bin/python tests/parallel_handover_test.py
```

Build EMOS through its maintained `firmware-check` wrapper. Generate `nm.txt`
from the same ELF with the selected toolchain's `ez80-none-elf-nm -an`, beside
its `MOS.bin`, then run each linked check against that directory:

```sh
cargo run --offline --release --manifest-path ../agon-emos/tests/uart_put_cpu/Cargo.toml \
  --bin uart_reservation -- IMAGE_DIRECTORY
cargo run --offline --release --manifest-path ../agon-emos/tests/uart_put_cpu/Cargo.toml \
  --bin uart_parking -- IMAGE_DIRECTORY
```

Host checks need sanitizer support. The P4 build uses the maintained `p4-console`
profile with board `p4-pc`; no board-specific private configuration is published
here. The previous admission/parking results remain frozen, including their
older reservation API behavior.

## Remaining boundary

F02c2b still owns fresh capability/session negotiation, live parser/coordinator
binding, P4 output reservation and queue/event/shift-register draining, peer
quiescence, deadlines, reset invalidation and the accepted mandatory physical
release fence at boot. F02c3 owns native payload binding. Ordinary UART startup
still runs today; this candidate does not implement the future boot fence or
enable ExExt. F03 remains the physical qualification gate after bench release.
No firmware was flashed, no hardware was contacted, and no SD content changed.
