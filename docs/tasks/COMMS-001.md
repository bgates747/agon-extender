# COMMS-001 — Deterministic mixed-carrier accuracy and endurance appliance

Smith requests a repeatable overnight communications fixture using UART1 and
eight-bit parallel between Agon and Extender, optionally extended to a Pi peer.
Receivers verify CRCs, report failures over UART1 and repeat a failed case up to
five failed attempts before advancing. Agon SD and independent Pi logs preserve
all attempts. Previously observed communication failures are the primary
motivation; their causes and severity remain unresolved. Smith's reported
one-to-two-hour uninterrupted UART match earlier on November 6 gives context
for suspecting communications in the later MechAgon freeze. That freeze is an
additional symptom, with its particular cause still unproven.

**State:** Design published before coding. Smith then authorises the largest
independent tranche on both tasks. Portable protocol/retry/orchestration,
host journal and real Pi peer pass sanitizer/source/CLI checks and an identified
eZ80 compile/link probe. Live mixed-carrier/VDU/MOS SD adapters remain; no
deployment, hardware invocation or overnight qualification.
**Owner:** Extender owns reusable appliance, EMOS/P4 accommodations and Pi peer.
Consumer owners retain their application code. This is separate from the blocked
Wolf endpoint decision in [PARALLEL-001](PARALLEL-001.md).
**Design:** [Mixed-carrier accuracy fixture r01](../testing/communications-accuracy-design.md).

Smith explicitly separates the complementary
[UART1/parallel performance task](COMMS-002.md). COMMS-001 remains an accuracy
and endurance appliance; do not combine executables/runs or derive benchmark
conclusions from its CRC/retry/logging loop.

## Scope and accepted requirements

1. Alternate UART1/PARLIO; include UART1→UART1, UART1→PARLIO,
   PARLIO→UART1 and PARLIO→PARLIO. Names refer to outbound/return local legs.
2. Exercise short bursts, sustained logical blocks, short/medium/long VDU
   command streams to P4, pure data, idle/busy transitions and supported mixed
   workload sequences. Include Pi5↔P4↔Agon cases.
3. Correctness is mandatory on every transfer using receiver CRC verification,
   identity/length/sequence checks and deterministic expected-byte comparison.
   Explicit fixture CRC authority supersedes the default no-CRC policy only
   within this selected appliance; production carrier formats stay unchanged.
4. Either endpoint reports a detected error through UART1 and requests a repeat.
   Interpret five failures in a row as five failed attempts total; preserve each
   attempt, reset its task-owned baseline and advance only after safe retirement.
5. Correlate failures with actual rejection/filter events where observable.
   Investigate missing filter observability instead of inventing counts.
6. No extra sniffers, wires or physical sensors. This tests accuracy rather than
   speed; timestamps support fault diagnosis, not a benchmark claim.
7. Run for configurable hours in available unattended bench windows; retain
   Agon SD progress/errors and Pi witness data, Escape/host stop and positive
   cleanup. Normal reservations remain in force; no autoexec test startup.

## Decision register

| ID | State | Decision or remaining issue |
|---|---|---|
| C01-D01 | Selected by Smith | Mixed UART1/parallel directions, VDU and pure-data workloads, CRC, UART error/repeat messages, five consecutive failures, SD logs and no sniffers |
| C01-D02 | Design interpretation | Five attempts total, not six; retry whole deterministic case with a fresh attempt ID, never silently replay an uncertain accepted transaction |
| C01-D03 | Owner implemented; source checked | Fixture CRC-32/ISO-HDLC, exact metadata+payload coverage and explicit wire encoding; independent received-byte oracle and protected error reports |
| C01-D04 | Unresolved owner source work | Smallest EMOS/P4 supported mixed-leg service: current UART and parallel NM endpoints are mutually exclusive compositions; no existing numeric ABI is assumed |
| C01-D05 | Source audit complete; telemetry gap remains | Reviewed fixed GPIO-filter API/register path exposes no rejected-pulse counter/event; correlation is unavailable, not zero. No extra sensor selected |
| C01-D06 | Proposed | Continue after known, positively retired failures; stop on unknown ownership, broken UART control or failed durable logging; no automatic reset/restart loop |
| C01-D07 | Proposed | Real streaming VDU observation separate from buffered validation sink; restore task-owned parser/display baseline before repeats |

The next technical decision is C01-D04. Recommended: a narrow diagnostic
composition and owner-admitted test service selecting each leg explicitly,
preserving ordinary production providers and EMOS routing. Alternative: changing
production protocols globally increases scope and firmware cost and is not
selected. Prerequisites are shared-pin return-to-UART proof, ROM/RAM/resource
fit and an unambiguous error channel. Its result determines the record size,
firmware pair and actual matrix that can be frozen. C01-D05 is an independent
source capability audit; unavailable telemetry must remain an explicit gap.

[Offline r01](COMMS-001/OFFLINE-R01.md) freezes the portable fixture protocol
and bounded source/build scope. [Source audit](COMMS-001/SOURCE-AUDIT-R01.md)
finds no rejected-pulse count in the reviewed fixed GPIO-filter API/register
path; record that telemetry as unavailable. The diagnostic owner interface is
still unresolved, so no physical retry capability is claimed.

## Bounded research précis

1. Official MOS API and VDU documentation were reviewed at documentation commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`; links and relied-on contracts are
   in the design. Before implementation, pin the relevant official source/tag
   baseline only where documentation is insufficient; keep references read-only.
2. Current `ext.netp` has one bounded pending record, foreground lifetime and
   positive RELEASE. A carrier fault retains ownership. NM payload is at most
   128 bytes; sustained blocks need application framing rather than a guessed
   raw-bulk ABI. Current `ext.net` and `ext.netp` compositions are separate.
3. EMOS owns display mode/routing and UART1/parallel shared-pin ownership. A
   UART NACK cannot be sent until that ownership has safely returned. The UART
   application driver must not replace EMOS's receive owner.
4. Prior filtered parallel tests pass bounded byte checks and a finite live
   consumer case. They did not count suppressed pulses or prove overnight
   reliability or erase previously observed communication failures. Smith's
   long uninterrupted UART observation is useful comparative experience, not
   a matched experiment. The later frozen watch used UART; do not attribute
   that particular failure to PARLIO without evidence.
5. Retain nominal selected-EMOS 120-count/s time units, P4/Pi monotonic clocks,
   wrap rules and correlation intervals. Generic upstream centisecond text is
   not the clock authority for this matched EMOS build.

## Implementation sequence

1. C01-01 [x] Record Smith's requirements, design, execution boundary and source
   limitations before code; maintain this task and the authoritative TODO link.
2. C01-02 [ ] Audit EMOS/P4 mixed-direction admission and positive UART return
   after both successful and refused parallel transfers. Document the smallest
   supported test interface and source/ROM/RAM cost before implementation.
3. C01-03 [x] Audit actual GPIO filter telemetry and define truthful per-endpoint
   counters/timestamps. Identify any requirement not measurable without probes.
4. C01-04 [ ] Freeze protocol schema, CRC coverage, deterministic corpus, VDU
   sandbox/baseline, five-attempt state machine, finite timeout/cancel policy,
   SD journal/rotation/commit format and Pi witness contract.
5. C01-05 [x] Implement offline portable case/record/CRC/state-machine/logging
   components and meaningful negative controls, including failed reports,
   duplicated/late messages, failed log writes and unresolved owner retirement.
6. C01-06 [ ] Implement the narrow owner adapters and real eZ80/P4/Pi endpoints;
   preserve EMOS mode ownership, normal startup and strict transport guards.
   Compile under actual FIFO reservations; record exact binaries/maps/configs,
   private bindings if any, source manifest and retained rollback identities.
7. C01-07 [ ] Qualify detector self-tests and one finite short full matrix under
   fresh normal bench custody. Preserve failure evidence; do not claim readiness
   from host-only parsing or a CRC unit test.
8. C01-08 [ ] Prepare a separate explicitly invoked hours-long run, with duration,
   matrix, seed, output paths, control-link failure boundary, selected recovery
   and cleanup, reservation and start/end records frozen before invocation.
9. C01-09 [ ] Report every first-pass/injected/recovered/exhausted/incomplete
   attempt, endpoint totals, telemetry availability, log completeness and exact
   restoration. Promote a recurring appliance only after tested acceptance.

## Validation and execution gates

1. Smith authorised implementation after design publication. Independent source
   and normal queued builds/checks can proceed; hardware still requires its
   supported adapter, exact freeze and actual custody. No test autorun.
2. Prove both receiver checks with known CRC vectors and independently generated
   bytes; exercise all verdicts and exactly five failed attempts. A later pass
   must retain nonzero first-pass errors and the original failure records.
3. Separate detector fault injection from unexpected errors. Never corrupt
   unrelated live application traffic, flash, startup or user files.
4. An endpoint unable to log, retire ownership or regain the UART1 control path
   stops new cases. Continuing after five failures requires a known clean state;
   it is not permission to reset and replay uncertain work.
5. Observe active bench constraints, appliance mode lifecycle, at least one
   second of settling after mode changes, explicit CLI invocation, supported
   cancellation, normal startup preservation and visible CLI restoration.
6. Current Wolf69 sole custody and Smith's post-test lease HOLD take precedence
   over any proposed overnight window. Prepare offline; neither idle hardware
   appearance nor an elapsed test estimate permits checkout or takeover.
7. Keep runtime binaries, captures and machine addresses in ignored local
   records. Tracked task/design contain portable contracts and references only.

## Results

[Offline result r01](COMMS-001/OFFLINE-RESULT-R01.md) and its structured record
retain15 Python/real TCP/CLI checks, a C++ ASan/UBSan suite,96 independent
C++/Python wire cases, modelled retirement/UART/five-attempt orchestration and
the8,381-byte identified eZ80 core/engine link. Source checks are not physical
qualification. No deployed appliance, rejected-pulse counter or overnight
accuracy result exists. Existing earlier passing cases remain their own evidence.
