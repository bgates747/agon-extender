# Application UART service observer

This experimental recorder preserves the first receiver error and nearby
software service context. The published source and linked artifacts have
bounded build checks; native IRQ execution, timer behaviour and physical
service timing are still unqualified. No application or component installation
is implied by including these sources.

## Distinct stopped intervals

1. A completed outer span needs PRESENT, START_CAPTURED and END_CAPTURED,
   matching valid controls, nonzero nonincreasing counts in its epoch and no
   overflow/owner-invalid/missing-boundary conflict. Runtime DURATION_VALID
   stays clear. Equal counts mean zero quantized counts, not zero physical work.
2. An active first-fault prefix is a separate quantity. Require current flags
   PRESENT|START_CAPTURED|ACTIVE_AT_FAULT (0x13), a proven frozen RAW_ERROR with
   RX LSR validity/event0x40, the same nonzero current/global epoch, both start
   and global fault controls0x0d and nonzero descending counts, with no overflow,
   owner loss, invalid clock/configuration or unassigned validity conflict.
   Its endpoints are current start68..69/control74 and global fault92..93/
   control94. Never invent current END_CAPTURED, mutate the raw record, or label
   this interrupted prefix as a normally completed masked interval/CPU total.
3. Disarmed, expired, count-increased, zero, mismatched-epoch, no-active-span or
   unproved first-fault samples produce UNKNOWN. The raw error/context remains
   useful. Missing clocks are not short intervals; never use modular subtraction.
4. First/last-RBR sampling is absent from the current owner build. Query96 and
   gap116..127 have no writer and remain unknown, including when their raw bytes
   are zero. The rearm-gap flag marks excluded coverage, not a measured duration.
5. Prior complete span and active prefix measure different scopes. Neither is
   an all-IRQ service gap, physical STOP tail, FIFO occupancy or exclusive CPU
   attribution. Outer wrappers omit pre-marker saves and post-marker tails.
   Full register saves and24-byte history copies add observer work; a matched
   NULL observer control remains necessary for interpreting future results.

The consumer-owned stopped decoder at MechAgon
`docs/tasks/GOAL-001/irq-diagnostic-source/decode-irq.py` already implements the
separate `current_start_to_fault` rule. Its reported compiler363 nine-case
qualification includes an independent active-first-fault/epoch test. Extender
reviewed that source; it did not rerun or claim its native IRQ execution. UART's
review initially identified the incomplete owner prose and then narrowed the
remaining issue to this documentation closure. No recorder instructions, ROM,
extra status acknowledgement or timer read are required for that convention.

## Lifetime and artifacts

Call the pure one-time init for an OPEN4/NULL-marker control. Actual disposable
PRT1 admission is separate, before OPEN7 association; readiness remains enabled
for normal IRQ service between bounded register accesses. Frozen records are
never cleared after association. A timing-stop does not detach the service hook,
retire a live source or permit unload: positive owner close is still required.

The retained package-r01 remains immutable, including its original header hash.
The later header comment and this interpretation clarify the same schema2;
all declarations, record offsets, native code and checked binaries are unchanged.
Use the task's exact artifact manifest and consumer link checks, not a presumed
latest source or a header comment as a new device qualification.
