# PORT-008 — Session control-owner binding results

**EMOS's framed foreground exchange and P4's control-owner binding pass their
focused checks.** EMOS reuses its existing console buffer, CRC, reserved sender
and bounded wait. The final EMOS image uses **130,480 ROM bytes**, leaving
**592 free**. Both full target builds and P4 source verification pass. No physical adapter,
boot handshake, ExExt mode or parallel payload is enabled; no bench operation
or production change occurred.

## Implemented behavior

R01 — EMOS's private foreground negotiation checks actual serializer ownership
and completed UART recovery. Its existing FF/16 reply dispatcher distinguishes
version 1 and 2, validates fields/CRC and captures only the first matching reply.
Foreground code performs the session transitions. The shared helper explicitly
supports reusing that buffer in place, avoiding overlapping `memcpy`.

R02 — An active ExCom lease needs the same buffer's transaction/challenge for
LEAVE. EMOS refuses parallel negotiation while that lease owns the buffer;
the future mode coordinator must close it first. Failed/uncertain negotiation
invalidates capability and requests release recovery, retaining the serializer
reservation. It does not restore pads, release the writer lock or claim success.

R03 — P4's existing F7 owner branches to the new small `ParallelControl` adapter
for version 2. Preparation changes neither video mode nor the version-1 console
lease. Staged preparation expires at 2,000 ms, including unsigned clock wrap.
Expiry, accepted version-1 console transitions, existing TX timeout and fatal
transport failure invalidate capability and ask the existing sequencer to
recover. Only the existing console task transmits replies.

R04 — P4's actual `ConsoleStream` instantiates that adapter, but ordinary boot
never advances its physical handover recovery. It therefore refuses version-2
traffic. EMOS's negotiate function has no startup/mode caller. Tests supply
modeled completed recovery; they cannot prove real output enables are released.
The [control contract](PARALLEL-CONTROL.md) records the early UART pin-enable
paths which the later mandatory boot-release adapter must replace.

## ROM and RAM

Baseline is the preceding private session candidate, not production. Percentage
change is `(control candidate − session candidate) / session candidate × 100`.
The unchanged AUDIT-008 accounting tool read the final guarded EMOS image.

| Measure | Session candidate | Control candidate | Difference |
|---|---:|---:|---:|
| ROM free below 131,072, bytes | 860 | 592 | −268 |
| ROM used, bytes | 130,212 | 130,480 | +268 (+0.21%) |
| EMOS static RAM, bytes | 4,058 | 4,058 | 0 |

EMOS adds no resident session instance or second packet buffer. The existing
wait is nominally 5 s at the mainboard's 120 clock units/s, with its existing
stalled-clock iteration fuse. Private sends retain their own existing deadlines.
These are control bounds, not physical throughput measurements or native block
deadlines. Remaining ROM is tight; later binding must pass the same image guards.

## Validation

| Check | Result | Scope |
|---|---|---|
| Paired foreground/ISR control boundary | 218 cases pass, ASan/UBSan | Real EMOS exchange/dispatcher and P4 control owner; corrupted/semantic-invalid replies, duplicate protection, missing peer, frozen EMOS clock, send/ownership failure, active console refusal, cold P4 gate, exact/wrapping expiry |
| Complete-image eZ80 control | 10 cases pass | Actual reserved UART TX, receive framer and ISR dispatcher, foreground prepare/commit, duplicate/invalid/missing replies, IRQ/active-console refusal, memory/IX/SP/IFF and retained reservation |
| Previous paired session owners | 1,149 checks pass | Lifecycle, replay and block-admission prerequisites |
| Previous linked eZ80 session owners | 1,334 checks pass | Host/target agreement and actual reservation query |
| Linked UART reservation / parking | 22 / 289 cases pass | Existing reserved/private writer and release/restore behavior |
| Paired admission / handover | 18,097 / 5,208 checks pass | Existing direction/length/sequence gates and recovery machines |
| Actual retained console-control function | Pass | Version-1 lifecycle retained; cold version-2 rejection, recovered version-2 prepare/commit without display reset; console transition invalidates capability; inherited N002 negative control still fails as expected |
| Existing console, session, keyboard, owner-core, native UART parking and profile checks | Pass | Unchanged normal input/control behavior and generated-source contracts |
| Full maintained EMOS wrapper/link checks | Pass | No relaxed image, ABI, UART divisor, keyboard, parallel or VDU guard |
| Full P4-PC wrapper and frozen-source recheck | Pass | Build/validator and final source closure; no deployment |

The eZ80 interpreter models register/clock behavior and injects framed responses
through the actual receive function. It is not a whole-system Fab emulator run,
electrical test or performance measurement. Leak scanning was disabled because
the sandbox tracer prevents LeakSanitizer inspection; ASan/UBSan remained enabled.

## Evidence and next boundary

Local build/provenance, source snapshots, vectors, logs and ROM ledger are
retained in ignored `agents/port008-control/`. [The result manifest](PARALLEL-CONTROL-RESULT.json)
identifies exact artifacts, sources and logs. Reproduction uses
`tests/parallel_control_test.py` and the owner repository's offline
`parallel_control` CPU binary against the same wrapper-built `MOS.bin`/`nm.txt`.
Existing session, console and ownership tests are reused.

Mandatory reciprocal boot release, fresh boot identity and stale-byte quarantine,
complete queue/event/shift-register draining, per-block deadlines/status and
native payload binding remain open under c2b/c3. No result here proves physical
shared-pad safety. Changes remain uncommitted for Author review; unrelated EMOS
application-peer work is untouched.
