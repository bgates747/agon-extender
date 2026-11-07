# UART1 reserve protection during UART0 service

Prepare the smallest owner correction for the receive-reserve risk exposed by actual92. EMOS currently advertises UART1 READY while UART0 handlers mask interrupts; UART1 asserts STOP only after its own handler prologue. The correction must protect that interval and drain safely before READY returns. This is a selected source/build tranche under the existing async goal, not a proven cause, installed fix or new physical case.

## Evidence and bounded research

1. The matched diagnostic record reports first LSR0x63/OE before this drain consumes any byte; remaining16 is its loop budget, not FIFO occupancy. Exact parser layout is state2, command0x8f NM reply, length106, remaining32, used74, partial_at26. The106=32+74 relationship is internally consistent, not an identified lost byte.
2. PC2 is READY at the recorded UART0 RX endpoints and STOP at UART1 drain/fault; PC3 is reverse-direction permission. A zero foreground hold does not disprove the IRQ's STOP assertion. Each three-count fragment is nominal41.67us with marker/endpoint costs and missing prologues/tails/gaps. It is not complete IRQ latency or a safe delay budget.
3. Selected owner source is EMOS1727fa19, with ordinary unprofiled control954e3c54 and exact installed P4 sourcee14e0b8a. Official Agon MOS API14h–18h defines UART/vector ownership, not live replacement of EMOS RX. Established read-only references remain agon-docs f9806bd3, MOSv3.0.2/83364093 and VDPv2.16.0/c7ac293d. UART's source assessment98ec410 cites F92 PS015317 Table11: UART0 vector18h precedes UART1 vector1Ah among pending sources, without preemption inside DI handlers.
4. Relevant owner files: interrupts.asm, emos_uart0_rfc25_io.asm, emos_keyboard_io.asm, uart.c, emos_neta.c and emos_net_wire.h. P4 console_hardware.inc configures hardware CTS and bounded FIFO enqueue; it does not prove physical STOP response or initial eZ80 FIFO occupancy. Source hashes, exact failed RAM/map joins and immutable artifact paths are retained in ignored owner evidence.

## Selected implementation contract, before code

1. EMOS alone asserts PC2 STOP early in the UART0 RX/TX entry, before substantial register-save/parser/FIFO work, only while a healthy admitted app owns UART1. Preserve all incoming registers and the existing disabled-IRQ/RETI convention. Ordinary non-app UART0 behavior remains unchanged. No nested EI or generic U1 engine change.
2. Use a distinct private UART0 hold so an IRQ tail cannot clear the existing foreground hold. Every UART0 completion path, including TX CTS defer, normal block and final callback, must pass the guarded tail. Before reopening READY, run the existing bounded UART1 RX-first path while the guard remains held. Preserve its first acknowledging LSR and fail-closed behavior.
3. A16-byte cap is not proof of empty FIFO. Retain a private deferred-RX flag, keep STOP asserted, and provide bounded continuation through the existing admitted owner service/tick path. Clear the flag only after that same drain observes a clean empty status. No spin, extra throwaway LSR read, new timer, packet, checksum, allocation or resident serializer. Positive close must not treat deferred RX as idle.
4. The guarded tail releases only its own hold. Fault, owner loss, deferred RX or another hold keep STOP asserted. A future healthy clean-empty service may reopen READY through the owner's ordinary completion path. Refused close retains source/hook storage. Preserve source callback, later TEMT, reply and positive CLOSE as separate obligations.
5. Isolate maintained source in a new owner branch. Preserve actual92/486 inputs, current restoreda25f rollback and both prior firmware images. Diagnostic hooks stay optional; no new public syscall, SDK ABI or P4/baud/default change.

## Qualification and finite build tranche

1. Actual-source host controls cover foreground/UART0 holds, cap16/deferred continuation, no-hook paths, first error, owner loss, CTS defer, callback, source/drain/reply and refused close. Include negative controls for the former unprotected path, unconditional READY and cap-as-empty behavior.
2. Native wrapper checks remain mandatory. Add exact linked entry/exit/RETI/STOP/read-error-before-RBR guards, all three UART0 TX exits and RX exit. Keep the pending-before-IER/TEMT and admission-before-source-mutation checks. Report all source/ROM/BSS/map costs and static stack effects; do not call structural checks executed ISA.
3. Compile serially through the Pi FIFO with a finite15-minute guard, normal thermal/memory limits and joined children. Check ordinary control, corrected app owner and diagnostic-ON fit independently. If diagnostic ON does not fit, report the actual bound; never truncate a ROM, drop a validator or substitute an unrecorded image. No emulator.
4. Return exact source/artifact/map/cost and a new finite isolation-before-consumer dependency proposal. Physical work requires its own immutable case, fresh grant, sole operator, exact install/readback and incoming rollback. No92 replay or automatic576000 fallback. The paired576 artifact remains separate.

The parent NET-004 task owns this selected work and authoritative queue entry. This document is the bounded implementation record; no production promotion or new architecture decision is implied.
