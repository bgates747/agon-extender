# PORT-008 activation bootstrap design

- Status: Rejected design alternative — retained for provenance only
- Date: 2026-09-01
- Owning task: [PORT-008](../../PORT-008.md)
- Corrective action:
  [`CA-2026-09-01-001`](../../../decisions/CA-2026-09-01-001-port008-preactivation-ready.md)

This task-local record preserves the design-only activation pass that proposed
`PORT-008-D001`. The Author rejected D001 on 2026-09-01. Nothing in the former
proposal amends an accepted hardware truth table, defines a protocol version,
authorizes source edits, assigns a build or procedure identity, permits
deployment, or approves a physical operation.

## Author disposition

1. Do not implement the receive-only common-UART listener, its Dormant-listen
   row, or the dedicated no-CTS EMOS bootstrap sender.
2. Retain the accepted all-controls-released Legacy/uncommitted rule and the
   current corrective-action containment. Production activation requires an
   intended-circuit solution that makes an EMOS-originated request observable.
3. Use r01 only for production-identical forward-parallel data-plane work under
   `PORT-008-D002`. The separate
   [production-equivalence audit](../production-equivalence/README.md) is the
   current authority for that boundary.
4. The detailed proposal, alternatives, state envelope, and validation matrix
   below remain historical research. Their conditional “if D001 is accepted”
   language is non-operative.

## Outcome

The accepted authorities contain a bootstrap deadlock that must be resolved
before an actor-explicit EMOS-requested activation transaction can be designed.

1. The accepted r02 truth table keeps `UART_FWD_OE_N`, `PAR_FWD_OE_N`,
   `UART_RETURN_OE_N`, and `READY_N` released in Legacy and while a mode
   transaction is uncommitted. No electrical path is enabled.
2. The accepted mode lifecycle requires EDP/P4 firmware and the carrier to
   remain quiescent until EMOS/eZ80 sends an explicit request. EDP/P4 may drive
   only the bounded activation response before EMOS commits.
3. When both Agon-to-P4 forward enables remain released, P4 cannot observe an
   EMOS request on either the common UART or the parallel control/data path.
4. Unconditional proactive `READY_N`, the behavior contained by the corrective
   action, lets EMOS observe P4 but reverses the required ownership and violates
   Legacy electrical absence.
5. Browser connection, network service readiness, an operator action on P4, or
   a periodic P4 polling window cannot repair the ownership contradiction.
   None is an EMOS-originated request over an accepted Agon transport.

The design originally stopped at one material decision: permit a receive-only
preactivation listener exception using the current r02 electrical topology,
including the P4-owned forward-enable control needed to create that input path,
or retain the all-controls-released truth table and require a new hardware arm
path. Because the exception changes an accepted truth-table interpretation and
test behavior, the Author must separately approve the next applicable hardware,
transport, and profile identities before controlled artifact/profile edits or
implementation. The Author selected the hardware-path alternative by rejecting
D001. This record does not assign the required successor circuit identity.

## Reviewed authority and baseline

1. [ADR-0014](../../../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md)
   and accepted `SETUP-005-D002` establish EMOS ownership, pull discovery,
   prepare/readiness/commit/recover, bounded precommit traffic, and fail-closed
   Legacy behavior.
2. [ADR-0016](../../../decisions/ADR-0016-v1-transport-electrical-core.md),
   [HW-001](../../HW-001.md), and
   [`v1-uart-parallel-circuit-proposal.md`](../../HW-001/v1-uart-parallel-circuit-proposal.md)
   establish the common UART, shared UART/parallel epochs, four P4-owned
   active-low controls, and current no-path Legacy/uncommitted truth-table row.
3. PORT-008 and the corrective action establish the retained VDU Stream
   boundary, official General Poll canary, three failed r01 attempts, proactive
   READY defect, and prohibition on another firmware or powered retry before an
   accepted activation design.
4. The committed r01 P4 adapter at repository commit
   `a495911945e8b4f55c95a00e901cd93cb5b68c73` unconditionally starts the
   receiver and asserts `READY_N` after arming PARLIO. The committed EMOS r01
   adapter at `agon-emos` commit
   `0e24b06abdb322fdb4e681a21242ccfebfc8ea65` waits for that assertion and
   sends General Poll before its route commit. Those adapters are predecessor
   evidence, not the accepted activation contract.
5. Official VDP `v2.16.0` and official MOS preserve the application-visible
   VDU stream and General Poll semantics. They define no Extender activation
   transaction; this bootstrap problem was created by the local split-processor
   integration.

At the time of this rejected design pass, files outside its then-authorized
scope were deliberately outside its evidence set. That sentence records the
pass's historical scope; it is not a current audit exclusion or a claim that
maintained sources remain unreviewed.

## Rejected decision `PORT-008-D001` — preactivation request carrier

### Question

For a controlled-beta transport using the current r02 electrical topology,
should EDP/P4 firmware enable only the Agon-to-P4 UART-forward bank as an
input-only preactivation listener while Legacy is committed, with the
UART-return bank, parallel-forward bank, and `READY_N` all released until a
valid EMOS/eZ80 activation request is accepted? This requires P4 GPIO15 to
assert the isolated `UART_FWD_OE_N` sink before the request, so the choice
explicitly relaxes the current all-P4-controls-released wording for controlled
beta while keeping every driver that can reach an eZ80 input disabled.

### Former recommendation — rejected

Accept the receive-only common-UART listener for controlled-beta development,
without treating it as final V1 Legacy electrical-absence qualification.

The resulting preactivation electrical row, under later Author-approved
artifact identities, would be:

| P4 control | Level | Effect before a valid request |
|---|---:|---|
| GPIO15 / `UART_FWD_OE_N` | 0 | Enable only Agon `PC0/TXD1` and `PC2/RTS1` toward P4 UART RX/CTS |
| GPIO17 / `PAR_FWD_OE_N` | 1 | Release `D1`, `D3`, `D4..D7`, `CLOCK`, and `VALID_N` forward paths |
| GPIO21 / `UART_RETURN_OE_N` | 1 | Keep P4 UART TX/RTS disconnected from eZ80 RX/CTS |
| GPIO20 / `READY_N` | 1 | Keep parallel admission released |

This is a deliberate amendment to the current r02 firmware-state truth table,
ADR-0014's quiescent-uncommitted wording, and the corrective action's current
containment description—not a claim that any already accepted text permits
listening. P4 actively sinks the forward-buffer enable control in the Agon
power domain, so D001 does relax the corrective action's literal requirement
that every P4/U4-originated Agon-domain signal remain released before the
request. The narrower eZ80-reachable return/data/admission set remains released:
the enabled buffer drives only toward P4 and no P4-controlled data or admission
path reaches an eZ80 input. Enabling that receive path does not prove that the
sender is EMOS: EDP can recognize only a syntactically valid activation frame.
Supported project code reserves emission of that frame to the explicit EMOS
operation, but exact bytes emitted by arbitrary external eZ80 UART code are
indistinguishable on the wire and remain outside the supported contract.

The listener contract is:

1. P4 preloads all four control latches released, configures its UART receive
   pins and peripheral plus every bounded activation-decoder resource, and only
   then asserts GPIO15 / `UART_FWD_OE_N`. On shutdown or failure, P4 releases
   GPIO15 before deinitializing the decoder, UART, or receive pins. It does not
   feed listener bytes to the retained VDU parser, EDU parser, updater, or a
   persistent-write path.
2. EMOS remains in Legacy until an explicit application, late autoexec, or
   operator command asks the EMOS mode coordinator to activate EDP. EMOS then
   owns eZ80 UART1 TX/RTS setup and transmits the future activation grammar with
   a dedicated bounded bootstrap sender that does not wait on `PC3/CTS1`.
   P4-to-eZ80 RTS is intentionally disconnected while `UART_RETURN_OE_N` is
   released, so the ordinary CTS-gated UART1 send path cannot carry this first
   request. Absence or unreadiness of P4 therefore ends in EMOS's bounded
   prerequisite failure rather than an unbounded flow-control wait.
3. An invalid, incomplete, replayed, mistimed, or unsupported request produces
   no additional P4/U4 assertion: `PAR_FWD_OE_N`, `UART_RETURN_OE_N`, and
   `READY_N` remain released, P4 UART TX/RTS remain disconnected from eZ80
   inputs, and only `UART_FWD_OE_N` remains asserted. EDP discards the request
   boundedly, retains `(0,1,1,1)`, and remains Dormant-listen.
4. Only after EDP has validated the request and prepared all response resources
   may a later accepted transaction design enable the UART-return path and
   acknowledge. `READY_N` remains reserved for an armed parallel receive epoch.
5. Every UART-to-parallel or parallel-to-UART change passes through an
   all-released break-before-make state. The electrical circuit executes the
   selected epoch; EMOS remains the sole mode and route-commit authority.
6. P4 reset or activation failure returns all four P4 controls to their
   hardware-released levels before software cleanup. A later software retry may
   restore only the receive-only listener after complete reverse-order unwind.

This choice uses the already accepted common UART direction, adds no wire, and
allows the later activation response to carry identity, protocol, and
capability data before any parallel VDU epoch. It also keeps activation control
separate from application-visible VDU bytes. It is a controlled-beta policy
exception, not a proof that Extender is electrically indistinguishable from
absence.

### Limitation retained by the recommendation

U1's inputs are permanently connected in the current r02 topology, so enabling
its outputs adds no incremental passive load on `PC0` or `PC2`. It does expose
those eZ80 levels to P4 and requires P4 to sink the Agon-domain forward-enable
control before any request. Existing r02 input-loading, floating-input, and
`READY_N` pull-up questions remain under `HW-001-Q007`; the controlled-beta
listener cannot qualify the stronger V1 claim that Legacy is electrically
indistinguishable from physical absence. If final V1 analysis rejects the
topology or policy, HW-001 must select switchable isolation, a hardware arm
input, or another harness revision.

Accepting D001 requires same-turn decision-level reconciliation of the
corrective action, ADR-0014, `docs/architecture.md`, ADR-0016, HW-001, PORT-008,
and the development log so accepted authorities never disagree. That
reconciliation must leave the frozen r02 artifact definition intact, mark it
insufficient for the accepted listener policy, and present the next applicable
artifact-identity decision without silently assigning an identity. D001 would
not by itself authorize controlled profile or firmware edits, flash, wiring
changes, or a powered run.

## Alternatives

### A — Add a hardware arm/request path

Keep the current no-path Legacy/uncommitted truth-table row. Add an
Agon-to-P4 request input whose passive state satisfies the final Legacy-absence
contract, or add switchable isolation that EMOS/eZ80 can arm without P4 first
enabling a shared transport bank.

This is the strongest route to strict electrical absence, but it requires
HW-001 analysis, Author approval of a new harness revision, new construction,
and new continuity/power/reset qualification before transport work resumes.

### B — Enable the complete parallel-forward path as the listener

Enable both r02 forward banks so EDP can observe `D0..D7`, `CLOCK`, and
`VALID_N` before activation, while leaving UART return and READY released.

This reaches the immediate parallel path directly but exposes more eZ80 levels
through enabled P4-side buffer outputs, expands noise and accidental-frame
exposure, cannot return the required identity/capability response without a
second epoch, and encourages the r01 General Poll workaround to become a
product handshake. It is not recommended.

### C — Use network, browser, operator, or timed P4 activation

Let P4 arm ingress after network readiness, browser connection, an operator
action, or a periodic interval.

This contradicts EMOS ownership and pull discovery, couples activation to an
unrelated subsystem, and does not establish an Agon-side transaction. It is
rejected unless the Author first reopens the accepted mode architecture.

## Non-operative proposed transaction envelope

D001 selects only how EDP can hear the first request. The complete transaction
still requires later decisions. The following state envelope constrains those
decisions without selecting their grammar or timing. Control tuples below are
ordered `UART_FWD_OE_N`, `PAR_FWD_OE_N`, `UART_RETURN_OE_N`, then `READY_N`.

| State | EMOS/eZ80 owner action | EDP/P4 owner action | Invariant |
|---|---|---|---|
| Safe/fault | Keep ordinary VDU on onboard VDP and treat EDP as unavailable | Hold all four controls released before initialization and throughout fault teardown | Canonical hardware-reset and fail-safe row is `(1,1,1,1)`; no transport path is enabled |
| Dormant-listen | Keep ordinary VDU on onboard VDP | After complete receive-side initialization, assert only the accepted UART input-path enable and listen only for activation control | Listener row is `(0,1,1,1)`; no P4-controlled data/admission path reaches an eZ80 input and no application parser receives bytes |
| Prepared | Hold saved eZ80 state and keep the public route Legacy | Validate one bounded request and prepare response resources | No acknowledgement before complete preparation |
| Transition | Change mux only under the EMOS activation owner | Release every enable before peripheral or mux change | After the old epoch's final release and before the first mux/peripheral mutation, the trace records `(1,1,1,1)` and retains all controls released until the new role is ready; conflicting enables never coexist |
| Transport ready | Keep public route Legacy pending validation | Acknowledge only through the selected activation response | Readiness is not formal-mode commit |
| Active | Atomically commit the selected EMOS planes and route | Enable only the selected transport epoch | Ordinary traffic follows the committed owner |
| Rollback | Restore onboard route and report bounded failure | Release all controls before reverse-order teardown | Bounded return to Safe/fault; Dormant-listen may be re-entered only by a fresh complete initialization/retry |

Transport-epoch readiness, EMOS mode commit, and user-visible activation success
are distinct events. No P4-local state may be reported as a formal mode.

One feasibility witness shows why the recommended listener is sufficient
without deciding the later protocol: the dedicated bounded EMOS bootstrap
sender can issue transport-control bytes on UART forward without waiting on
the disconnected `PC3/CTS1`; EDP can validate them and prepare its response
resources while UART return remains disabled. EMOS must arm its receive side
before P4 enables UART return and sends readiness. A later session-bound
confirmation can authorize P4 to enter its selected local transport epoch;
EMOS alone commits and names formal mode. Control and session metadata remain
below the raw VDU stream. The exact frame, all-released/remux ordering,
response, confirmation, epoch residency, and EMOS commit points remain Q001
and Q002. Under current authority the official General Poll is the first
post-commit ordinary-VDU canary; Q003 owns its exact failure and response
handling, not its precommit placement.

## Downstream questions retained for a future intended-circuit path

PORT-008 owns these questions and must present them to the Author one at a time:

1. `PORT-008-Q001` — Freeze the activation grammar, protocol version,
   integrity check, transaction identity/replay rule, deadlines, retry limit,
   bounded decoder behavior below the VDU/EDU application protocols, and the
   exact EMOS sender behavior required by the intended-circuit request carrier.
2. `PORT-008-Q002` — Freeze the request, P4 readiness response, EMOS
   confirmation, transport-epoch, and EMOS formal-mode commit ordering. EMOS
   alone commits and names formal mode; P4 prepares and reports readiness, then
   enters its local active epoch only after the selected session-bound
   confirmation. A shared PC0--PC3 level or guard interval is not a positive
   remux acknowledgement: for example, `PC2/RTS1` can legitimately be low as
   parallel `D2`. UART return stays disabled through preparation and remux and
   until P4 is ready to respond, then must be enabled before P4 transmits that
   response. The exact all-released, response, confirmation, and commit ordering
   remains open.
3. `PORT-008-Q003` — Freeze bounded fail-back and response staging for the
   official General Poll as the first post-commit ordinary-VDU canary. The r01
   prototype's precommit poll is a predecessor exception, not a production
   contract. Moving General Poll before commit would require an explicit
   amendment to ADR-0014 and the accepted SETUP-005-D002 lifecycle; Q003 may not
   silently make that change or inherit the prototype's discard-only behavior.
4. `PORT-008-Q004` — Define coordinated shutdown, P4 reset, eZ80-only reset,
   stale-epoch rejection, parser invalidation, and retry. The accepted r02
   topology does not itself clear stale P4 enables after an eZ80-only reset.

## Rejected design's deterministic validation boundary

After the remaining questions are accepted, host/source validation must use an
injected monotonic clock, enumerated failure points, fake GPIO/peripheral
adapters that default released, and one append-only cross-processor event
trace. It must prove at least:

1. hardware reset and every initialization failure retain Safe/fault with all
   four controls released; a successful receive-side initialization reaches
   Dormant-listen with only `UART_FWD_OE_N` asserted, Legacy still committed,
   and zero application-parser bytes for arbitrary no-request time;
2. among supported project code, only the explicit EMOS operation emits a
   syntactically valid request; arbitrary external eZ80 register, GPIO, or UART
   access remains outside the supported contract and is not authenticated by
   this wire protocol;
3. one finite generated matrix covers every truncation point and declared-
   length boundary, every supported and unsupported enum class, one-bit
   mutations of each protected field, enumerated integrity-mismatch classes,
   stale and duplicate transaction identities, and just-before/at/after each
   deadline; every invalid case fails without acknowledgement or persistent
   effect;
4. one finite grammar-derived resynchronization matrix covers every decoder
   state, every proper request-prefix length, every suffix/prefix overlap and
   byte alignment within the bounded retained window, the maximum permitted
   garbage span, and timeout reset, each followed by one valid request;
5. a fixed seeded Legacy-garbage corpus, mechanically verified to contain no
   valid activation-frame substring, supplements rather than substitutes for
   the grammar-derived resynchronization matrix;
6. failure after every EMOS and EDP preparation step unwinds in reverse order
   and permits a deterministic clean retry;
7. simultaneous or reentrant requests select one owner and return a defined
   bounded result to every loser;
8. after one UART/parallel epoch releases its last enable and before the first
   mux/peripheral mutation for the next epoch, the trace records `(1,1,1,1)`;
   controls remain released through new-role initialization, and conflicting
   directions never coexist;
9. `READY_N` asserts only after the parallel receiver and complete destination
   capacity are armed, then releases on completion, stopped clock, stuck
   validity, timeout, cancellation, reset, and every error;
10. reset or cancellation from every transaction state releases controls first,
   reaches Safe/fault before cleanup, and never resurrects a stale active epoch;
11. activation behavior is identical with the browser disconnected or connected;
   browser state changes only whether visible-frame evidence can be observed;
12. the first post-commit ordinary-VDU record is General Poll with exact
    official bytes and response ordering, with no transport-control bytes
    exposed to the retained VDU parser or MOS-owned response state.

Static and linked-image checks must additionally prove that no ordinary-ingress
or output-arm call remains unconditional in the P4 boot path, output latches
are preloaded released before direction changes, all waits and lengths are
bounded, only the activation owner changes transport enables, and pin identity
comes from the reviewed hardware profile. The linked eZ80 activation call graph
and disassembly must prove that the first request selects the dedicated
bootstrap sender, never reads or waits on `PC3/CTS1`, contains no unbounded
poll or loop, and configures then restores UART1 TX/RTS registers and idle
levels in the Q001-approved order.

These checks cannot prove high impedance, pad behavior, passive loading,
settling time, wiring continuity, physical reset behavior, or cross-signal
ordering at the assembled circuit.

## Future physical evidence boundary

No physical procedure is authorized by this design. A later separately
reviewed procedure must begin before P4 boot and observe the request marker,
all relevant enables, and READY in one time domain. It must distinguish a
logic-high endpoint from a disabled/high-impedance driver and cover no-request
boot, valid activation, absent P4, suppressed response, resets in each state,
stopped clock, stuck validity, abort, full General Poll, and clean retry.

Under active bench constraint BC-001, every eZ80 fixture must cold-boot from an
exact root `/autoexec.txt`, require no typed input, reach a deterministic
terminal state, and expose a non-keyboard evidence channel. HTTP 200 remains a
network-service observation only. A browser WebSocket is required before a run
that claims visible output, but it is neither an activation request nor an
activation prerequisite.

## r01 disposition

The preserved r01 harness has no accepted production activation path and cannot
qualify the rejected D001 transaction. Its proactive READY behavior remains
contained. The missing physical r01 CLOCK cause remains a separate PORT-008
diagnosis or explicit withdrawal gate. The r01 fixed adapters and failed runs
remain predecessor evidence and must not qualify activation, target common-
UART behavior, EMOS response parsing, r02 circuitry, or Legacy absence.

Under accepted D002, r01 may later execute only the production-identical
forward-parallel data plane from an explicitly supplied active-epoch boundary.
That is a separately identified qualification composition, not a revival of
D001 or the exact r01 adapters.

## Stop conditions

Do not reconcile an ADR, architecture rule, hardware profile, or corrective-
action condition to the rejected D001 design. Stop before production activation
implementation until HW-001 supplies an accepted intended-circuit request path
and PORT-008's applicable transaction questions are resolved.

The D002 data-plane boundary may receive separate source authorization without
settling activation. Stop before any artifact/profile edit, deployment, or
physical operation until its exact identities, evidence-integrity gates,
procedure, and Author approvals are satisfied. A separately authorized r01
CLOCK diagnostic may diagnose the preserved r01 failure but cannot qualify
activation or the intended circuit.
