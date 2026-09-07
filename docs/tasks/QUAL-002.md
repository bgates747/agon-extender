# QUAL-002 — Qualify assembled-system electrical absence, power, and reset behavior

## State

- Status: On hold for the present r02 hardware — incomplete wiring and no test
  of the complete circuit. Preliminary September 4 power-domain observations
  remain limited evidence, not full-circuit qualification. The Author paused
  design, construction, and hardware testing on 2026-09-07; existing mode and
  remediation gates remain open.
- Started: 2026-09-04 18:32 EDT
- Finished: --

## Intent

Qualify the Agon Light 2, onboard VDP, Extender P4, selected transport harness,
and attached measurement fixtures as one assembled system across power, reset,
idle, transfer, failure, and recovery states. Establish that legacy mode makes
Extender electrically and logically absent and that no supported power/reset
ordering back-powers, contends, wedges, or damages either board.

This task owns AUDIT-001 requirements `C15` and `C16` and wiring/fixture findings
`W04` and `W05`. It does not assume that the candidate breadboard already meets
production isolation requirements.

## Authority and inputs

- [AUDIT-001](AUDIT-001.md).
- [`light2-harness-r02`](../../hardware/designs/light2-harness-r02/README.md)
  and its `light2-extender-solderless-assembly-r02` construction target.
- [`light2-harness-r01`](../../hardware/designs/light2-harness-r01/README.md)
  only as the preserved predecessor baseline, plus
  [`la03-p4-probe-fixture-r01`](../../hardware/fixtures/la03-p4-probe-fixture-r01/README.md).
- PORT-008's accepted transport ownership states and controlled candidate.
- `SETUP-005-D002` mode lifecycle, reset, failure, and recovery decision.
- [Versioning and qualified-run policy](../versions/README.md).
- Ignored `HARDWARE.local.md` for current bench identity and safety boundaries.

## Required outcomes

1. Define the supported assembled-system power, reset, connection, and mode
   state space, including explicitly unsupported combinations.
2. Establish measurable limits and observations for rail separation,
   back-powering, line contention, high-impedance/released states, enable
   defaults, reset defaults, and recovery.
3. Demonstrate that powered and unpowered Extender states do not disturb normal
   onboard-VDP operation in legacy mode.
4. Exercise either-order board power, independent Agon/onboard-VDP/P4 resets,
   USB attachment changes, and selected failures during idle, forward transfer,
   return transfer, and rendering.
5. Verify deterministic recovery or the accepted visible failure without
   requiring unsafe manual intervention.
6. Determine whether `light2-harness-r02` is sufficient. If isolation,
   switching, biasing, protection, reset, connector, or measurement wiring must
   change, stop and create an Author-approved new revision before testing it.
7. Define fixture/probe revisions and multiple-capture or endpoint-oracle
   methods sufficient for each claim; an eight-channel analyzer must not be
   treated as simultaneous proof of unobserved signals or analog safety.
8. Keep Console8 outside the Light 2 result; it requires its own harness and
   later qualification.
9. Prove the accepted pull-discovery policy: EDP/P4 firmware and carrier wiring
   produce no proactive presence traffic or unsafe P4-to-eZ80 signal while
   Legacy is committed or a transaction is uncommitted; EMOS explicitly arms
   the receiver and initiates discovery.
10. Prove the accepted pre-activation fail-safe design boundary for every
    supported power, reset, mode, and GPIO-ownership state: hardware-safe
    defaults keep P4-to-Agon drivers disabled independently of P4 firmware and
    prevent contention or back-powering. Do not generalize this evidence into a
    non-bricking guarantee for external code that bypasses EMOS.

## Work

### Suspended staged work

The 2026-09-07 Author hold suspends construction and testing of the present
circuit. Its full wiring is incomplete and the complete circuit is untested.
The earlier sequence and stage-02 worksheet are superseded drafts; the
resistor-addition proposal was rejected. The following records are retained
for review, not as the next executable procedure.

The retained process references are [staged circuit validation](../qualification/staged-circuit-validation.md)
and the design's `wiring-order/sequence.yaml`. The [September 4 power-domain observations](../../hardware/designs/light2-harness-r02/wiring-order/tests/01-power-domains-results-2026-09-04.md)
are preliminary construction evidence. No full review gate or qualified outcome
has been inferred from those measurements.

1. [ ] **S1:** With HW-001, record in the design test directory the installed
   cumulative subset and its actual terminals, omissions, power sources/cables,
   and measurement access.
   Confirm present bench state before selecting the next ordered stage.
2. [ ] **S2:** Apply Review Gates 1 and 2 to that stage's state space, including
   already powered ICs and shared enables. Power/bias checks do not require
   completed UART/parallel firmware or production activation. Active-transfer
   stages require the applicable PORT-008 candidate and ownership preconditions.
3. [ ] **S3:** Identify the firmware used for the measurement. A passive or
   other scoped diagnostic may establish electrical behavior; production-
   candidate component claims require that component to execute with exact
   build provenance. Keep unrelated service initialization disabled.
4. [ ] **S4:** Keep each measurement record in the design test directory; link
   its disposition and limitations here and feed the next stage. Do not promote
   a power-domain check to GPIO-passivity, complete transport, Legacy-absence,
   reset, or mode evidence.

## Construction test sheets and results

The [r02 design test directory](../../hardware/designs/light2-harness-r02/wiring-order/tests/README.md)
owns the human test sheets and construction results. This task owns sequencing,
review gates, unresolved findings, and acceptance; it links to evidence instead
of containing the measurement record.

1. [Stage 01 power-domain results, 2026-09-04](../../hardware/designs/light2-harness-r02/wiring-order/tests/01-power-domains-results-2026-09-04.md):
   unpowered, P4-only, Agon-only, and dual-powered observations, including the
   passive P4 image provenance. Preliminary only; no qualification pass.
2. [Stage 02 startup/fail-safe bias sheet](../../hardware/designs/light2-harness-r02/wiring-order/tests/02-startup-and-fail-safe-bias-network.md):
   draft unpowered inspection, settled voltage and optional digital-startup
   worksheet. The Author requires permanent parts only; the expanded step
   depends on HW-001-Q011's permanent input-bias successor proposal. No readings
   or physical execution are recorded. Approve the circuit/identity change
   under HW-001, then record the applicable procedure review here.

### QUAL-002.1 — Define the qualification state matrix

1. Enumerate supported power sources, USB states, board-power orderings, reset
   sources, transport ownership states, operating modes, and active/idle cases.
2. Map each state and transition to expected GPIO direction, buffer-enable,
   rail, protocol, and recovery behavior.
3. Identify destructive or electrically unsafe combinations that must be
   excluded from testing until protective design changes exist.
4. Link each state to QUAL-001 compatibility obligations and PORT-008 transport
   states.
5. Include commands issued before, during, and after P4 boot, plus stale EDP
   traffic after P4 reset, and identify the EMOS, EDP/P4 firmware, eZ80
   peripheral, interface-circuit, and physical-wiring owner for each expected
   state.
6. Include bounded pre-activation malformed-pattern and supported
   direction-change cases produced through accepted fixtures and procedures.
   Identify direct register/GPIO bypass as unsupported and outside any
   non-bricking claim rather than attempting exhaustive adversarial proof.

### QUAL-002.2 — Audit the candidate hardware and measurement boundary

1. Review schematic-level paths, pull resistors, series resistance, transceiver
   enables, default pin states, common ground, independent rails, USB power,
   and possible phantom-power paths.
2. Determine which hardware element owns safe P4-to-eZ80 isolation before EDP
   firmware runs and whether any P4 ROM/boot path can drive product wiring.
3. Determine whether the P4 can safely observe pre-activation host activity
   while its Agon-facing drivers remain disabled. A warning path is optional
   and must not weaken isolation merely to make such activity observable.
4. Determine which claims require a logic analyzer, oscilloscope, meter,
   current-limited supply, endpoint integrity check, or multiple controlled
   captures.
5. Produce a no-change sufficiency finding or a bounded proposal for new
   harness/fixture revisions. Do not alter the live bench during this work.

**Review Gate 1:** Author approves the selected stage's supported states,
safety analysis, instrumentation, stop conditions, and any required design
revision before its procedure or experiment is authorized. This gate may be
satisfied for a bounded mode-neutral subset without approving the full future
power/reset/mode matrix. Acceptance names the exact subset and exclusions.

### QUAL-002.3 — Freeze candidate artifacts and procedures

1. Create or approve every required harness, fixture, profile, procedure, and
   firmware/eZ80 diagnostic identity under the versioning policy.
2. Separate non-destructive read-only preflight from power switching, reset,
   connection changes, flash, or fault-injection steps.
3. Define exact expected observations, tolerances, trigger/capture boundaries,
   recovery steps, abort conditions, and evidence retention.
4. Require committed clean inputs before decision-bearing qualification runs.

**Review Gate 2:** Author approves each physical procedure and confirms the
current bench state before execution.

### QUAL-002.4 — Execute bounded physical qualification

1. Run only approved non-destructive and safe state transitions.
2. Record exact wiring, fixture, probes, instruments, builds, procedures, and
   run identities.
3. Preserve failed, partial, aborted, and invalid evidence.
4. Stop on unexpected voltage, current, contention, heating, smoke, reset loop,
   data corruption, unstable ownership, or identity mismatch.
5. Restore and record a known safe final bench state after every run.

### QUAL-002.5 — Dispose findings

1. Promote qualified harness/fixture/procedure status only for the exact tested
   scope.
2. Feed results into QUAL-001 and every gated implementation task.
3. Create bounded corrective tasks for failures; do not silently patch wiring,
   firmware, or procedures during a qualification run.
4. Record explicit deferrals for production carrier, connector, ESD/EMC, or
   Console8 work not covered by the prototype qualification.

## Dependencies and sequencing gates

- Record mode-neutral construction evidence beside the design and link its
  disposition in this task using the versioning policy; the unfinished QUAL-001 mode matrix is not a prerequisite. QUAL-001
  must define the relevant obligations before compatibility claims are made.
- HW-001 supplies r02 circuit and stage construction authority. PORT-008 must
  define the relevant transport ownership and controlled candidate before an
  active-transfer test, not before power or passive-bias observations.
- Accepted `SETUP-005-D002` supplies the lifecycle foundation. REMED-001's
  four-mode freeze, open SETUP-005 decisions, HW-001-Q003/Q007/Q010, and this
  task's corrected execution gates still block approval of the full physical
  mode matrix.
- REMED-001's four-mode conformance freeze must explicitly release the
  applicable mode-dependent scope before that scope is physically qualified.
  Bounded tests that neither exercise nor claim those modes use their stage
  gates under PORT-008-D003; they do not release the full freeze.
- REMED-002 F008's frozen-input identity block was reconciled on 2026-09-01.
  A later connectivity/profile hash mismatch was recorded on 2026-09-05;
  HW-001 must reconcile it before r02 is claimed as a clean frozen
  qualification input. F016 still prohibits treating older plan approval as
  an execution release, and all stage electrical/physical gates remain.
- QUAL-002 Gate 2 is required before any physical power-order, reset-order,
  connection-change, or fault-injection run.
- A passing QUAL-002 scope is required before PORT-008 Gate 2, PORT-003 Gate G,
  or another task claims assembled Light 2 compatibility across power/reset
  boundaries.
- This task does not authorize access to the bench while the Author is absent.

## Explicit exclusions

- No Console8 wiring or claim.
- No production PCB, enclosure, connector, ESD, EMC, or regulatory
  qualification unless separately added and approved.
- No deliberate short circuit, overvoltage, destructive fault, or unsafe live
  rewiring.
- No assumption that legacy inherited runs qualify the current clean project.
- No changes to product protocol or operating-mode policy.

## Completion criteria

1. The Author approves both review gates and final evidence.
2. Every supported assembled-system state has a passed run or an explicit
   bounded qualification statement explaining why another evidence method is
   sufficient.
3. Legacy electrical/logical absence, either-order power, independent reset,
   transfer interruption, and recovery claims are supported without
   unexplained observation gaps.
4. Late P4 power-on, explicit EMOS discovery while P4 is still booting,
   bounded readiness, no unsolicited boot/reset traffic, and no-mainboard-reset
   Legacy-to-Dual activation have accepted evidence.
5. Required hardware revisions are qualified rather than edited in place.
6. QUAL-001, artifact registry, procedures, run manifests, task records, and
   development log agree on the exact scope and remaining deferrals.

## Accepted REMED-002 findings

[REMED-002](REMED-002.md) assigns QUAL-002 the consumer gate for
`INTEGRITY-AUDIT-F008` and the task-status correction for
`INTEGRITY-AUDIT-F016`. Evidence remains in
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md).

1. [ ] Consume `light2-harness-r02` only after HW-001 proves that its maintained
   schematic, profile digest, generated projection, relevant stage assembly
   mapping, and version identity agree. The 2026-09-05 connectivity digest
   mismatch remains a controlled-input blocker. The human schematic and
   separate wiring order guide construction; a missing whole-assembly map does not
   prohibit a documented, reviewed partial stage. Neither is electrical proof.
2. [ ] Make each future plan, procedure, and run state whether it exercises
   mode-dependent behavior and name the applicable REMED-001 release when it
   does. A mode-neutral stage states its narrower scope and exclusions.
3. [ ] Treat the 2026-08-22 plan approval as approval of scope only, never as
   authorization for bench access, a physical run, or mode-dependent evidence.
4. [x] Reconcile any earlier candidate record that relied on the mismatched r02
   identity before carrying it into a qualified run. No tracked run cited r02,
   so no run evidence required migration.
