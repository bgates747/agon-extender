# DIAG-001 — Implement recoverable failure reporting and crash records

## State

- Status: Not started — advisable during beta; hard v1 requirement
- Started: --
- Finished: --

## Namespace

`DIAG` identifies work whose primary product is operator-visible diagnostics,
machine-readable failure evidence, crash capture, or support-report artifacts
spanning more than one firmware or hardware owner.

## Prompting decision

This task implements the failure-reporting requirements accepted in
[`REMED-001` Work 2.d, `W2D-Q05`](REMED-001/mode-lifecycle-analysis.md#w2d-q05--post-commit-failure-policy)
and prohibited-behavior item `W2D-Q09.7`.
Mode and transport failures should, to the extent surviving components permit,
explain what failed, what the system did, and what happened to the running
program and resident state. Reports should aid consumer bug submissions rather
than reduce every failure to an opaque reset or timeout.

Structured reporting is advisable during beta but is not a beta release gate.
It is a hard v1 requirement.

EMOS recovery/reporting code and EDP/P4 diagnostic firmware must not send the
only report through a failed component when another accepted sink survives.
Diagnostic delivery must not delay or block safe recovery merely to reach a
preferred sink.

## Accepted durable-storage baseline

V1 requires a bounded durable crash-log sink in the P4's onboard SPI flash; an
installed P4 microSD card is not a prerequisite. The existing dedicated
`coredump` partition is the initial implementation candidate, but this task must
validate its size, format, coexistence with native ESP-IDF crash data, and
ability to hold the accepted project envelope before freezing that choice.

The flash record must be bounded, integrity-checked, power-loss-tolerant, and
wear-limited. It must not overlap application, OTA metadata, NVS, or OTA image
partitions, and failure to write it must not block recovery. P4 microSD may
hold richer history, screenshots, or export packages when present. Browser or
local video is a human-readable sink but is not durable by itself. After
mainboard recovery, EMOS may retrieve the P4 record and copy or export it
through another accepted sink.

When the mainboard is unresponsive, EDP records only evidence it actually has:
the last valid EMOS heartbeat/session, committed mode, pending transaction,
observed timeout or link state, and P4-local context. It must not invent eZ80
registers, PC, stack, or cause; those require prior EMOS checkpointing or a
future separately accepted observation mechanism.

## Intent

Provide a bounded failure-report path that remains useful when one display,
processor, transport, storage device, or parser is unavailable. Present a
descriptive report through a known-working human interface and preserve a
versioned machine-readable record without delaying or destabilizing recovery.

## Required report content

1. Stable failure/event identifier and schema revision.
2. Current, requested, pending, and fallback mode information where known.
3. Failed component, transport, readiness/transaction stage, timeout or reset
   reason, and the recovery action taken.
4. Plain-language consequences: program halted or resumed, last known eZ80 PC
   when captured, display/audio/buffer state lost or unknown, input unavailable,
   EDU sessions invalidated, or Legacy restored.
5. Exact available firmware, MOS/module, protocol, hardware, wiring/profile,
   build, procedure, and run identities under the versioning policy.
6. Bounded eZ80 PC, SP, register, and stack context where it can be captured
   safely and truthfully.
7. Bounded P4 reset, panic, exception, task, and backtrace context where
   available.
8. Timestamp and clock confidence, sequence number, integrity check, truncation
   flags, and unavailable-field reasons.

Never fabricate processor context or imply that a sampled PC caused an
asynchronous failure. Distinguish captured-at-failure, sampled-after-detection,
retained-before-reset, and unavailable evidence.

## Work

1. Inventory which diagnostics survive each Legacy, Dual, and exclusive failure
   class, including failed EDP display, failed onboard VDP, eZ80/MOS fault,
   transport loss, P4 reset/panic, storage loss, and whole-system reset.
2. Define a versioned machine-readable envelope and a compact human rendering
   from the same authoritative record.
3. Select prioritized sinks per failure class: onboard recovery screen, EDP
   screen when healthy, mandatory bounded P4 flash crash area, Agon SD, optional
   P4 microSD, serial diagnostic output, or later network retrieval. Do not
   assume one universal sink.
4. Define safe capture for eZ80 execution context and bounded stack windows,
   including what MOS support or assembly hooks are required.
5. Integrate native ESP-IDF panic/reset/backtrace evidence without replacing or
   obscuring upstream diagnostics.
6. Define recovery-screen ownership. In an exclusive failure, use of the
   onboard VDP is an explicit diagnostic/recovery action after application
   continuity has been disclaimed; it is not transparent display failover.
7. Bound rendering, capture, storage writes, retry, and timeout behavior so the
   diagnostic path cannot recursively crash, deadlock recovery, loop forever,
   or corrupt a filesystem merely to save a report.
8. Provide a deterministic export/package suitable for a user bug report and
   document how to retrieve it after fallback or reboot.
9. Qualify complete, partial, truncated, corrupt, unavailable-sink, repeated-
   failure, and diagnostic-path-failure cases across all applicable modes.
10. Evaluate a best-effort pre-activation unmanaged-traffic warning through an
    Extender-owned display or log. It may state only that no valid EMOS session
    exists, must treat silence as normal Legacy, must not drive Agon-facing
    wiring, and is not required when safe electrical isolation prevents the P4
    from observing host activity.

## Dependencies and gates

- Consume accepted SETUP-005 D002 lifecycle, D003 response ownership, D006
  failure behavior, D007 input, and D008 RTC/time decisions.
- Consume the project versioning registry and exact firmware/hardware/profile
  identities rather than inventing diagnostic-only labels.
- Coordinate with storage, partition, MOS, P4 panic, transport, and mode
  implementation owners before selecting persistent sinks.
- Do not make a successful fallback depend on writing a log or drawing a
  recovery screen.
- Do not expose arbitrary memory beyond the bounded accepted crash context
  without a separate review of user control and report contents.

## Completion criteria

1. Every accepted mode/transport failure class has prioritized surviving
   human and machine-readable diagnostic paths.
2. Reports identify consequences and recovery accurately, including unavailable
   context, rather than merely naming an error code.
3. Processor and stack evidence is bounded, provenance-labelled, and never
   fabricated.
4. Failure reporting cannot block or recursively defeat recovery.
5. Deterministic fault-injection tests prove rendering, persistence, retrieval,
   truncation, interrupted-write recovery, wear bounds, and fallback behavior.
