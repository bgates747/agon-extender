# Provisional UART1 physical trial — failed, working ROM restored

The first selected MechAgon trial reported a UART1 receiver overrun after its
transmit source was released. The application deliberately quarantined because
wire drain and positive close were incomplete. The cause of the overrun remains
unresolved. Extender preserved the original status and post-reset RAM, restored
and independently verified the complete working ROM, and cleanly released the
bench. This is no async correctness, performance or 30 Hz qualification.

## Installation and exact scope

1. Fresh normal custody followed the predecessor's actual clean release. The
   incoming P4, mainboard VDP, startup and listener matched the frozen consumer
   binding. Initial CLI/read-EXIT, SAVE-only raw state, whole files, neutral input,
   idle worker and free programming ports passed.
2. Extender staged and independently compared both complete 131072-byte ROMs:
   candidate `043a0989b08a7429a2c52aca6a037660f8c19c067376173d17af7c46f1238c0f`
   and working rollback
   `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca`.
3. One candidate FLASH produced the exact identified automatic reboot,
   `agon-emos-eirene-r05-b2026-11-07-06-35-12Z`. Independent SAVE/GET compared
   all 131072 installed bytes. Raw mode/callback/backend zero, whole normal files,
   actual CLI, input/idle/free ports and joined readers passed before the actual
   stopped consumer handoff. No owner workload or additional reset ran.
4. MechAgon alone invoked its one frozen finite trial, using executable
   `cf910bd7e15533067f5c1cd886af0b3874258acfc4da087c1923e1bd784bfb4b`
   and map
   `330608002abab39fc98efe1c7aef74f8fd9de159453f285b92510423392872cb`.
   The source caller, SDK, generic core, firmware and 116-input consumer binding
   were unchanged during that invocation.

## Actual failure and independent evidence

The host reported peer reset 104 after five native intents and six host FRAME
sends. Its original 150-second observation expired without a native terminal or
CLI. All consumer parent/host/reader processes joined before actual stopped
return; Extender then alone performed the selected recovery and rollback.

| Retained first-fault field | Value | Interpretation |
|---|---:|---|
| Application result |6|Source-backed deliberate HALT quarantine|
| Native decisions / presentation records |5 / 5|Not a completed run|
| Native view frames |2|Not optical display evidence|
| Owner progress result / query |35 / 93|Local fault/refusal; not proof of remote BUSY|
| NM accepted / rejected |92 / 0|Last accepted query92 SEND reply|
| U1 phase / fault / error |3 / 2 / 0x02|FAULT / LINE_ERROR / UART receiver overrun|
| Source released / remaining bytes |1 / 0|Caller source release is established|
| Wire idle / positive close |0 / 0|Later drain and detach are unproved|
| Progress calls |378|No IRQ-latency timeline follows|

MechAgon's immutable text/rodata decode matches the exact executable/map and all
25 comparable original SD witnesses. Engine source/count/callback are zero;
the retained application association pointer is not proof a resident hook was
still installed when post-reset RAM was saved. The error does not undo an
already completed source-release callback. Logical `link_idle=1` is not a
positive U1 drain/detach result. Neither the host reset nor the reported receiver
overrun establishes external noise, a P4 defect, a generic U1 defect or the
underlying cause of the earlier watch freeze.

## Recovery, preservation and handback

1. The standing single Agon recovery failed its 60-second admission check. The
   selected paired recovery reset P4 once and observed its matched build/pad
   release, but an early HTTP readiness timeout occurred before its paired Agon
   step. Extender preserved the issued ledger, observed that same P4 initialized
   without resetting it again, then issued only the not-yet-issued paired Agon
   step once. Actual input admission and CLI returned. No test was replayed.
2. Before any subsequent LOAD or FLASH, Extender saved the complete 65536 bytes
   at application address 040000, SHA256
   `4a7aa3d3529425b98e40c6649df47f875e954eda822374918c67e044ef59a6cf`.
   This is explicitly **post-reset RAM**, not pre-reset register evidence. The
   original 1314-byte application status is independently retained, SHA256
   `0da0db39301a8b9ac0c490211c43f20b6dac9c27194e902519bd9cbd960953de`.
3. After preservation, the existing bounded feature getter confirmed absent
   VDPlet feature, restored callback, ordered clear and no retained buffer.
   The fresh boot had already removed the application's hook; the getter was
   cleanup evidence, not a second async test.
4. Extender flashed the exact retained working ROM once and independently
   SAVE/GET-compared all 131072 bytes with the rollback hash above. P4, native
   mainboard firmware/app-tail, startup and listener were unchanged. Full files,
   actual root CLI, cursor controls, raw mode/callback/route zero, neutral input,
   offline idle worker, free programming ports and joined actors passed.
5. The first final release failed to write the shared registry under restricted
   filesystem permissions after its cleanup checks. Extender retained that
   observation and obtained a genuinely new final observation before normal
   release; no old receipt was restamped. Actual release was
   **2026-11-07T07:48:31.562200+00:00**, with no waiting successor at that instant.
   All Extender target access stopped; SD remains mounted. The consumer received
   durable handback and immediate steering. No lease or new test follows from it.

Private device/network identities, exact request/lease, binary archives, original
journals and installation/recovery/readback/release receipts remain in ignored
request-local records. Production selection and version tags are unchanged.

## Matched source findings and limits

1. Matched EMOS source `2c4705310a49c7d97fc606bf47344cc36f68ab2e`,
   `src/uart.c::uart1_keyboard_open`, selects **1152000 baud, 8N1, hardware flow
   control**. Sixteen full character times are about 138.889 microseconds, or
   2560 configured CPU clocks at 18.432 MHz. That empty-FIFO scale is not a safe
   blackout budget: initial occupancy, in-flight bytes and STOP response matter.
2. `src/emos_keyboard_io.asm::_uart1_keyboard_irq` asserts receiver STOP before
   its bounded RX-first loop. Each iteration reads one LSR, checks errors, then
   reads data and may dispatch an application callback. Only a clean data-empty
   LSR reaches the app TX service. The 16-byte cap never treats its last data
   byte as status. The error path propagates the same LSR mask to the app.
3. This STOP protects processing after handler entry, not an earlier interval
   during which interrupts were masked. The app hook, parser callbacks and
   final `uart1_keyboard_irq_done` run under exclusion; that completion clears
   STOP before the remaining IRQ register restore. Foreground gateway locking
   also precedes its progress/RX-first call. These are concrete source seams,
   not measured excessive delays or an attribution of this failure.
4. UART0's existing `src/emos_uart0_rfc25_io.asm::WAIT_CTS` can wait under DI.
   MechAgon's reciprocal source-callback-plus-TEMT/NM gate reduces that exposure
   and must remain intact. The saved first fault supplies no timeline proving
   this path ran or caused the overrun. Shared callback/IRQ service latency and
   the matched P4's STOP-to-final-byte behavior still need correlation.
5. Retained matched P4 application source, independently joined to its source
   inventory, configures UART1 CTS/RTS at the same baud. In
   `vdp/video/extender/transport/console_hardware.inc`, complete NM replies enter
   the single `ConsoleStream` output queue; its sole console task uses
   `uart_tx_chars` to enqueue at most 128 bytes into available FIFO space and
   observes `uart_wait_tx_done` without blocking. The selected hardware CTS
   configuration, rather than per-byte application polling, controls onward TX.
   Neither queueing nor that configuration proves the actual STOP-to-final-byte
   response on this run. Their source hashes and unchanged archive join are
   retained privately; no new P4 build or execution was performed.
6. UART's unchanged core checks errors before TAIL/TEMT and retains its first
   fault. Its ordinary-C emitter performs bounded output and no CTS spin,
   DI/EI, RX read or vector installation. No generic core/emitter/register-save
   mismatch is identified. P4's RX reserve supports eZ80-to-P4 TX bursts; it
   does not prove safety of the opposite P4-to-eZ80 receive direction.

The current trial remains failed. Preserve the first error and independent
source/drain/reply lifetimes; do not suppress OE, force positive close, remove
the reciprocal guard or replay this trial. Remaining owner investigation is
tracked in the [active integration task](EMOS-ASYNC-R01.md).
