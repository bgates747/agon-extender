# Four-mode lifecycle analysis

- Parent task: [REMED-001](../REMED-001.md), Work 2.d
- Accepted decision: SETUP-005-D002
- Scope: discovery, selection, entry, exit, transition, reset, failure,
  recovery, fallback, and prohibited states
- State: Accepted 2026-08-24
- Prepared: 2026-08-23

## Purpose

Define a safe lifecycle for Legacy, Exclusive Compatible, Exclusive Extended,
and Dual modes without presuming that every mode has the same owner or can be
entered through the same software stack.

This analysis consumes the accepted D001 dispatcher and graceful-failure
invariant. It does not implement a MOS command, select persistent storage,
design response ingress, define physical transport signals, or authorize hot
switching.

## Source constraints

1. MOS `v3.0.2` initializes UART0 and waits indefinitely for the onboard VDP's
   General Poll before mounting the SD card or entering its normal command loop.
2. Official VDP `v2.16.0` waits for General Poll before starting its normal
   processing and physical-input loop.
3. Stock MOS has no Extender mode registry, dispatcher, capability negotiation,
   transport arbitration, durable service owner, or recovery command.
4. Stock MOS supports only Legacy. Every mode in which Extender is active,
   including Dual, requires Extender MOS (EMOS); direct application ownership
   of Extender hardware is unsupported caveat-emptor experimentation.
5. EMOS owns both the accepted VDU dispatcher and EDP-service activation.
6. Rev 1 has no direct onboard-VDP/EDP link; MOS/eZ80 relays all coordination.
7. Current firmware contains no implemented four-mode lifecycle to preserve.

## Proposed state factorization

Treat the formal operating mode as the supported combination of two separately
owned state planes.

### VDU-routing plane

Owned by EMOS whenever Extender support is installed because EMOS controls the
accepted semantic VDU dispatcher:

- `route:onboard`
- `route:edp-compatible`
- `route:edp-extended`

### EDP-service plane

Owned by EMOS. Linked application code is only an EDU API binding; optional
resident facilities remain subordinate clients or service providers and do not
own activation, transport hardware, or committed mode:

- `edp:inactive`
- `edp:active`

### Supported combinations

| VDU route | EDP service | Formal mode | Support boundary |
|---|---|---|---|
| onboard | inactive | Legacy | Extender is logically/electrically absent; stock behavior only. |
| onboard | active | Dual | Ordinary VDU remains onboard; EDU explicitly addresses EDP. |
| EDP Compatible | active | Exclusive Compatible | EDP is the sole compatibility display authority over the stock-UART backend. |
| EDP Extended | active | Exclusive Extended | EDP is the sole compatibility display authority over the forward-parallel backend. |

The combinations `route:edp-compatible + edp:inactive` and
`route:edp-extended + edp:inactive` are invalid because they would direct VDU
into an unavailable processor. No component may publish one of those partial
states as a mode.

This factorization keeps two logically independent state dimensions without
creating competing authorities: EMOS owns and commits both. Stock MOS cannot
activate EDP and therefore remains in Legacy.

## Accepted pull-discovery safety policy

Extender presence is pull-discovered. EDP/P4 firmware and carrier wiring may
not proactively announce Extender to the eZ80/mainboard while Legacy is
committed or a mode transaction is uncommitted.

1. During P4 power-off, power-on, ROM boot, firmware boot, reset, and committed
   Legacy, carrier wiring and interface circuitry keep every P4-to-eZ80 signal
   electrically isolated, released, or otherwise at its reviewed inactive
   level. The eventual hardware-design task must assign the physical enable and
   fail-safe owner; firmware behavior alone cannot qualify unpowered safety.
2. EDP/P4 firmware sends no boot log, presence byte, packet, interrupt, or GPIO
   announcement over an Agon-facing product transport before EMOS opens an
   explicit discovery transaction.
3. EMOS prepares the eZ80 receiver and any EMOS-controlled interface enable,
   then sends a discovery/readiness request over the selected eZ80 peripheral,
   transport implementation, and physical wiring.
4. EDP/P4 firmware replies only within that requested transaction. EMOS
   validates the response and alone decides whether to commit Dual or continue
   preparing an explicitly requested exclusive transition.
5. After activation, EDP/P4 firmware may emit asynchronous traffic only through
   an explicitly negotiated EDU session, callback, event channel, or other
   receiver already armed and owned by EMOS.
6. P4 reset invalidates all such permission. EDP/P4 firmware and carrier wiring
   return to the reviewed inactive state; EMOS discards or quarantines stale
   traffic until explicit rediscovery.
7. EMOS never feeds unexpected EDP traffic opportunistically into the onboard
   VDP's stock MOS packet parser and never treats a byte, edge, reset, or power
   event as mode authorization.
8. Rev 1 defines no proactive dedicated presence signal. Any later open-drain,
   interrupt, or other presence wiring requires a new actor-explicit hardware,
   firmware, race, reset, and qualification review and can only indicate
   possible presence—not authorize a mode change.

This policy is a hard v1 requirement. QUAL-002 owns power-order, reset-order,
electrical-isolation, boot-chatter, stale-traffic, and receiver-arming
qualification. D003 owns exact parser and response-domain handling.

## Accepted pre-activation fail-safe design boundary

Direct GPIO or transport use without an active EMOS transaction is unsupported
and caveat emptor. The following are normative requirements for project-produced
hardware, firmware, software, procedures, examples, and tests—not a privilege
boundary or non-bricking guarantee for external code that violates them.

1. Carrier hardware defaults all P4-to-Agon drivers disabled independently of
   P4 firmware and prevents contention and back-powering across supported power,
   reset, mode, and GPIO-ownership states.
2. Before activation, EDP/P4 firmware exposes only a minimal bounded activation
   recognizer. Ordinary VDU, EDU, update, flash-write, MOS-write, and other
   persistent operations remain unreachable.
3. The activation exchange must be explicitly framed, versioned,
   transaction-specific, integrity-checked, and staged so arbitrary ordinary
   bytes or GPIO activity cannot accidentally commit it. This prevents naïve
   activation; it does not authenticate EMOS against deliberate imitation.
4. Project EDP firmware handles malformed pre-activation traffic only through
   the bounded recognizer and may ignore, reject, log, or reset. External code
   that bypasses EMOS through direct peripheral, GPIO, flash, or protocol
   manipulation is outside the contract and may corrupt, damage, or brick
   either system.
5. Absence of a transaction is normal Legacy and does not prove EMOS is not
   installed. If hardware permits safe observation of unmanaged activity, EDP
   may report only that no valid EMOS session exists, using an Extender-owned
   out-of-band display or log. It sends no warning over Agon-facing wiring.

QUAL-002 owns carrier-level proof. The eventual activation-protocol and EDP
parser tasks own bounded recognizer and fuzz/fault evidence. This invariant
adds no support or non-bricking promise for direct-hardware clients, whether
their violation is naïve or deliberate.

## Accepted staged transition classes

### Live EDU-service transition

Legacy and Dual share `route:onboard`. Rev 1 may therefore transition between
them without changing ordinary VDU or canonical MOS VDP state:

```text
Legacy -- explicit EDU activation --> Dual
Dual   -- explicit EDU shutdown ----> Legacy
```

Entry remains explicit and discoverable. Merely powering P4 does not create
Dual mode. Once explicit activation succeeds, Dual is latched system state and
does not end when the initiating utility or last foreground caller exits.
Normal shutdown is explicit and coordinated with registered sessions and
persistent/background work; reset and failure follow Q05/Q06.

A successful explicit presence/version probe activates the EDP service and
therefore commits Dual mode. There is no separate stable “detected but
inactive” mode.

### Legacy hub

Legacy is the only supported direct source or destination for transitions to
or from another formal mode:

```text
Dual <--> Legacy <--> Exclusive Compatible
           ^
           |
           v
    Exclusive Extended
```

A request from one non-Legacy mode to another decomposes into two separately
bounded transitions through Legacy. Dual therefore shuts down to Legacy before
entering either exclusive mode; either exclusive mode returns to Legacy before
entering Dual or the other exclusive mode. Transition phases are not formal
modes and add no third truth-table dimension.

### Restart-mediated VDU-route transition baseline

Any Legacy-hub transition that changes the ordinary VDU route uses a controlled
restart in the proof-of-concept and beta baseline:

- Legacy to either exclusive mode; and
- either exclusive mode to Legacy.

This restart-mediated behavior remains an acceptable v1 fallback. It need not
preserve the running eZ80 program, eZ80 RAM, or volatile state resident in
either display processor. The operator must therefore treat a baseline
route-changing transition as disruptive.

Restart mediation gives MOS and both processors a clean parser, queue, sysvar,
transport, and ownership boundary and avoids pretending that divergent display
state can migrate transparently.

### State-preserving transition target

The aspirational v1 target is a quiesced route transition that preserves the
loaded eZ80 program and data and preserves resident processor state wherever
safe and practical. This is a firm v2 requirement and is owned by
[MODE-001](../MODE-001.md).

Preservation does not imply migration: onboard-VDP display assets do not
automatically become EDP assets, nor do EDP assets automatically become
onboard-VDP assets. The later work must define, per transition, which resident
state remains intact, which state becomes inactive or stale, which state must
be rebuilt, and whether switching Compatible/Extended transports can preserve
EDP state because authority remains on the same processor.

## Transaction model

Every accepted transition follows a prepare/commit/recover model.

1. **Request:** identify the desired mode through an installed facility.
2. **Local validation:** confirm the request is recognized, allowed from the
   current state, and supported by the installed MOS build or EDU runtime.
3. **Dependency validation:** EMOS checks required EDP firmware/API version,
   backend, optional resident-service requirements, hardware/profile
   declaration, and other
   mode-specific prerequisites without redirecting ordinary VDU.
4. **Prepare:** EMOS quiesces new requests, drains or explicitly discards its
   owned queues, permits no more than one attempt for this explicit request,
   and retains a recoverable current/last-known-good state. A design that must
   carry a pending attempt across an eZ80/MOS reset requires separately reviewed
   retained state; beta does not promise that mechanism.
5. **Initialize:** establish the target's processor, transport, parser, input,
   and response paths in the mode-specific boot order.
6. **Readiness:** complete target-specific General Poll/capability checks and
   prove every required owner is ready.
7. **Commit:** atomically publish the new supported combination and allow
   ordinary VDU or EDU work.
8. **Recover:** on any pre-commit failure, clear the pending request and restore
   the previous or safe fallback mode with a bounded diagnostic.

Activation never publishes an exclusive route before EDP readiness. Absence of
an Extender-specific command or API on stock MOS may produce the normal
`Invalid command` or unavailable-API result and leaves the machine unchanged.

## Mode-specific boot responsibilities

### Legacy

1. Keep all Extender-driven Agon-interface signals released and transceivers
   disabled.
2. Initialize onboard VDP through the stock MOS path.
3. Publish no EDP service and perform no Extender handshake.
4. Treat absent, unpowered, incompatible, or failed Extender as normal.
5. Make every cold boot reach fully operational Legacy before any optional
   `autoexec.txt` or manual Extender invocation.

### Dual

1. Boot onboard VDP and EMOS through the stock-compatible Legacy path.
2. Activate EDP only through an explicit EMOS EDU operation, including an
   explicit presence/version probe.
3. Negotiate EDU capabilities and allocate the separate result/event domain.
4. Leave ordinary VDU, stock response parser, canonical VDP sysvars, and input
   packets unchanged.
5. On activation failure, remain Legacy with stock behavior intact.

### Exclusive Compatible and Exclusive Extended

1. Reach fully operational Legacy first.
2. Begin entry only through an explicit `autoexec.txt` or manual invocation.
3. If currently in Dual, perform a coordinated EDP shutdown and commit Legacy
   before beginning the exclusive transition.
4. Stage the required dispatcher backend without publishing the route.
5. Retain or reinitialize the onboard VDP through the private MOS control route
   sufficiently to establish its accepted physical-input role.
6. Classify or drain its bootstrap responses so they cannot become the final
   EDP-authoritative display state.
7. Initialize EDP through the selected Compatible or Extended transport.
8. Complete the authoritative EDP General Poll and response-path readiness.
9. Commit the exclusive route only after input, command, response, and recovery
   prerequisites are ready.
10. Do not mirror ordinary VDU to the onboard VDP after commit.

Direct cold-boot entry into an exclusive mode is outside the v1 contract.
Automatic exclusive entry is permitted only as an explicit late
`autoexec.txt` invocation after Legacy is operational.

D003 and D007 own the exact response and input mechanisms behind these steps.

## Failure and recovery classes

### Before commit

Failure leaves or restores the previous stable mode. EMOS makes no more than
one attempt for one explicit request and does not autonomously re-arm it. This
does not guarantee suppression when a full reset causes `autoexec.txt` to issue
the same command again; cross-boot circuit breaking is deferred to
[MODE-002](../MODE-002.md). The failure record must identify the missing or
incompatible prerequisite without relying on the failed target display path to
show it.

### After commit

- **Legacy:** EDP/P4 failure is irrelevant to stock operation.
- **Dual:** EDP/EDU calls fail and Extender services stop, but onboard VDU and
  canonical MOS state continue. Invalidate all EDU sessions/results and commit
  Legacy when failure is detected; Dual cannot remain the formal mode with an
  inactive EDP service.
- **Either exclusive mode:** EDP or exclusive transport failure cannot
  transparently continue the application on the onboard VDP because parser,
  display, audio, buffer, callback, and response state have diverged. MOS should
  enter an explicit transient failure condition, stop accepting ordinary
  output into an unavailable backend, and make at most a bounded
  reinitialization attempt. If readiness cannot be restored, recover
  disruptively to Legacy. It may use the private onboard control path for a
  recovery diagnostic; doing so is not application continuation, transparent
  failover, or automatic state migration.
- **Onboard VDP failure in an exclusive mode:** EDP output may remain active,
  but physical keyboard/mouse service is degraded or absent. The system reports
  the loss without inventing P4-owned peripherals or changing canonical input
  ownership.

Automatic post-commit failover between display processors is not proposed for
v1. Recovery selects and reinitializes a stable mode rather than pretending to
preserve incompatible live state.

### Failure-report contract

Structured crash reporting is advisable during beta and a hard v1
requirement; it is not a beta release gate.

To the extent the surviving hardware and software permit, every detected mode
or transport failure must produce both a descriptive human report and a durable
machine-readable record suitable for consumer bug reporting.

The human report should use a known-working display path, normally the onboard
VDP in Dual or after recovery to Legacy. It must identify the failed component
or readiness stage, active/requested mode, immediate recovery action, and
practical consequences—for example that a running program was halted, display
state was lost, input is unavailable, or operation resumed in Legacy. Using the
onboard VDP for this recovery screen is an explicit diagnostic action, not
transparent continuation of the failed application.

Where safely obtainable, the report should include exact firmware/protocol/
module identities, reset and failure codes, eZ80 PC and SP, a bounded register
and stack snapshot, and P4 exception/backtrace context. It must never invent
unavailable context. Persistent logging must choose a sink that survives the
failure in question and must not block recovery, recurse on failure, or risk
filesystem corruption merely to produce a report. Exact capture mechanisms,
schema, sinks, retention, and qualification are owned by
[DIAG-001](../DIAG-001.md).

## Reset classes

| Reset event | Required lifecycle treatment |
|---|---|
| eZ80/MOS reset | Return through Legacy startup; do not trust previous dispatcher, parser, sessions, pending work, or canonical-state readiness merely because processors remained powered. |
| EDP/P4 reset in Legacy | No stock effect; Extender remains absent. |
| EDP/P4 reset in Dual | Invalidate EDU sessions/results, preserve onboard VDU, commit Legacy, and require explicit rediscovery before EDP use. |
| EDP/P4 reset in an exclusive mode | Mark exclusive path failed, block new VDU delivery, and require bounded EDP reinitialization or restart into a stable mode. |
| Onboard VDP reset in Legacy/Dual | Follow stock failure/recovery behavior; EDP does not impersonate its canonical responses. |
| Onboard VDP reset in an exclusive mode | Reinitialize the private physical-input role without sending ordinary VDU; classify bootstrap responses separately. |
| Whole-system reset/power cycle | Reach fully operational Legacy. An optional late `autoexec.txt` command may then request another mode through the normal transaction. |

Exact reset detection, persistence, timers, diagnostics, and hardware reset
signals remain implementation and qualification work.

## Selection, persistence, and reporting requirements

1. EMOS owns the desired/current VDU route and never infers it
   merely from traffic or P4 power.
2. EMOS owns EDP service activation in Legacy/Dual and reports explicit
   discovery, version, sessions, and background-service ownership.
3. A current formal mode is derived only from a supported committed combination
   of the two state planes.
4. EMOS permits one attempt per explicit transition request. Pending state is
   required only if the selected implementation carries that request across a
   restart; its retention mechanism requires separate review and is not a beta
   requirement.
5. A persisted preferred mode is not a v1 contract. It remains an exploratory
   possible v1 feature and later aspiration. If accepted, it should invoke the
   same late Legacy-hub transaction rather than create direct cold-boot entry.
6. Unknown, corrupt, or unsupported pending or future persisted selections
   fall back safely rather than black-holing VDU. Cross-boot suppression of an
   unchanged `autoexec.txt` request is deferred to MODE-002 regression evidence.
7. First-round fixed-backend EMOS builds may compile an available exclusive
   backend for development and qualification, but still enter it only through
   an explicit transaction after Legacy startup.
8. A later selectable EMOS build may need EMOS-owned requested, pending, committed,
   failure, and fallback records. Exact persistence, API, and storage decisions
   remain with W2D-Q07.
9. Diagnostics must remain available through a route independent of the target
   that failed wherever practical.

## Prohibited lifecycle behavior

1. the EMOS mode-transition coordinator publishing an exclusive route before a
   reviewed transport/wiring profile is selected, EMOS arms the eZ80 receiver
   and requests readiness, and EDP/P4 firmware returns a compatible identity,
   protocol version, and capability set; this protocol handshake does not
   substitute for QUAL-002 electrical qualification;
2. the EMOS VDU dispatcher switching backend during an eZ80 `RST.LIL 18h`
   operation, partial VDU command, in-flight response, or owned callback/event
   transaction;
3. EDP/P4 firmware or carrier wiring proactively announcing presence while
   Legacy is committed or a transaction is uncommitted, or the EMOS
   mode-transition coordinator changing committed mode merely because P4
   powered up, reset, or emitted bytes or edges, without the accepted explicit
   pull-discovery transaction;
4. the EMOS dispatcher, EDP interface firmware, or carrier wiring duplicating
   ordinary VDU traffic to both display processors during transition, except
   for separately identified qualification traffic or recovery diagnostics;
5. MOS recovery firmware rerouting application output to the onboard VDP while
   claiming that EDP-resident display/application state survived when it did
   not;
6. the EMOS mode-transition coordinator making more than one attempt for one
   explicit request or autonomously re-arming that request after failure;
   cross-boot suppression of a command reissued by `autoexec.txt` or a future
   persisted preference is not a beta requirement and remains a conditional v1
   target under MODE-002;
7. EMOS recovery/reporting code or EDP/P4 diagnostic firmware sending the only
   human or machine-readable failure report to the failed processor, display,
   transport, storage device, or physical connection when a surviving accepted
   sink is available; [DIAG-001](../DIAG-001.md) owns implementation and
   qualification of the prioritized reporting paths;
8. any eZ80 application, linked client, TSR, MOS Module, or resident service
   redirecting ordinary VDU, claiming Extender transport hardware, or changing
   committed mode outside the documented EMOS dispatcher/lifecycle operation;
9. MOS- or EDU-side status/reporting code naming an uncommitted, failed, or
   partial two-plane combination as a formal supported mode; and
10. the EMOS mode-transition coordinator directly transitioning between two
    non-Legacy formal modes rather than completing the accepted Legacy-hub
    sequence.

## Work 2.d question register

Questions are presented and disposed one at a time. Work 2.d closes only when
each is accepted, rejected with a replacement, or deferred to a named owner.

### `W2D-Q01` — Two-plane lifecycle model

- **Status:** Accepted 2026-08-23
- **Question:** Define each formal mode as a supported combination of distinct
  VDU-routing and EDP-service planes, using the four combinations in this
  analysis and prohibiting an exclusive route while EDP is inactive?
- **Recommendation:** Accept the two-plane factorization. The later EMOS-only
  decision supersedes the original assumption that the planes could have
  different software owners.
- **Disposition:** Accepted as amended. The formal mode is derived from the
  committed combination of the EMOS-owned VDU route and EMOS-owned EDP-service
  state. This two-plane truth table remains the lifecycle foundation; adding
  another independent state dimension requires a new architectural review
  rather than silently multiplying mode combinations. Stock MOS can represent
  only Legacy because it cannot activate the EDP-service plane.

### `W2D-Q02` — Rev 1 transition classes

- **Status:** Accepted 2026-08-23
- **Question:** Permit live Legacy↔Dual transitions through explicit EDU
  activation/shutdown, but require controlled restart for every v1 transition
  that changes the ordinary VDU route?
- **Recommendation:** Accept. It preserves stock VDU state in Dual while giving
  exclusive route changes a clean parser/sysvar/transport boundary.
- **Disposition:** Accepted with staged scope. Live Legacy↔Dual activation is
  retained. The proof-of-concept/beta baseline uses a disruptive controlled
  restart for every ordinary-VDU route change and remains an acceptable v1
  fallback. Preserving loaded eZ80 program/data and resident processor state is
  an aspirational v1 target and firm v2 requirement under MODE-001; it does not
  promise cross-processor migration of display assets. Amended by the Author
  on 2026-08-23 to make Legacy the mandatory hub: no direct non-Legacy-to-
  non-Legacy transition is contracted, and every such request must complete a
  safe transition to Legacy before attempting its destination.

### `W2D-Q03` — Transactional activation and safe fallback

- **Status:** Accepted 2026-08-23
- **Question:** Adopt the prepare/readiness/commit/recover transaction, including
  one EMOS attempt per explicit request, no pre-readiness route publication,
  bounded diagnostics, and safe fallback on missing or incompatible support?
- **Recommendation:** Accept. This expands the already accepted graceful-failure
  invariant into an implementable lifecycle contract.
- **Disposition:** Accepted as proposed. Mode activation validates and prepares
  every prerequisite before publishing new routing, commits only a complete
  supported truth-table state, and rolls back or falls back safely after a
  bounded pre-commit failure. Clarified on 2026-08-23: EMOS permits one attempt
  per explicit request and does not autonomously re-arm it. Preventing a full
  reset from causing `autoexec.txt` to issue the same command again would
  require retained state or equivalent command cooperation; that protection is
  not a beta requirement and is deferred to MODE-002 regression evidence. This
  coherence guarantee is separate from MODE-001's later eZ80 and display-state
  preservation work.

### `W2D-Q04` — Mode-specific boot orchestration

- **Status:** Accepted 2026-08-23
- **Question:** Adopt the Legacy, Dual, and exclusive boot responsibilities in
  this analysis while deferring response classification and input relay details
  to D003 and D007?
- **Recommendation:** Accept. The order respects both processors' General Poll
  requirements without mirroring ordinary VDU.
- **Disposition:** Accepted with a mandatory Legacy-first startup. Every cold
  boot reaches fully operational Legacy and makes no Extender contact unless an
  explicit late `autoexec.txt` or manual invocation occurs. A successful
  explicit presence/version probe activates EDP and commits Dual; failure
  leaves Legacy. Exclusive entry begins only after Legacy through such an
  explicit invocation. Persisted automatic mode selection is not a v1
  contract, although it remains an exploratory possible v1 feature and later
  aspiration. One-shot transaction state is separate and remains permitted.

### `W2D-Q05` — Post-commit failure policy

- **Status:** Accepted 2026-08-23
- **Question:** Reject transparent live failover in v1; preserve stock operation
  after EDP failure in Dual, but treat exclusive EDP/transport failure as an
  explicit failed state requiring reinitialization or restart into a stable
  mode?
- **Recommendation:** Accept. The processors' live parser/display/audio state
  cannot be represented as equivalent after failure.
- **Disposition:** Accepted with refinement. Detected EDP failure in Dual
  invalidates EDU work and commits Legacy while onboard VDU continues. An
  exclusive EDP/transport failure blocks VDU, permits only bounded
  reinitialization, and otherwise recovers disruptively to Legacy without
  claiming application/display continuity. Input loss may leave exclusive EDP
  output active but must be reported. Best-effort diagnostics must explain the
  failure and its consequences onscreen and in a durable log, including
  truthful bounded PC/register/stack or P4 exception context where safely
  obtainable. This reporting is advisable during beta and a hard v1
  requirement, not a beta gate. DIAG-001 owns implementation and qualification.

### `W2D-Q06` — Reset invalidation

- **Status:** Accepted 2026-08-23
- **Question:** Require every reset class to invalidate the affected sessions,
  parser/readiness claims, and pending work as described, rather than inferring
  readiness from retained power or memory?
- **Recommendation:** Accept. Exact detection and reset wiring remain later
  implementation details.
- **Disposition:** Accepted as proposed and aligned with the Legacy-first
  contract. A reset invalidates the affected component's sessions, parsers,
  readiness claims, pending work, and authority even when volatile bytes or
  another processor survive. Invalidation does not itself require erasing
  retained RAM. eZ80/MOS and whole-system reset return through Legacy; P4 reset
  in Dual commits Legacy; exclusive P4 failure follows Q05 recovery; and
  onboard-VDP reset in exclusive operation invalidates input until private
  reinitialization succeeds.

### `W2D-Q07` — Selection authority and persistence requirements

- **Status:** Accepted 2026-08-23
- **Question:** Define selection authority, authoritative state, transaction
  records, persistence scope, and fixed-backend behavior without selecting
  premature APIs or storage?
- **Recommendation:** Accept. The current MOS boot order makes premature
  selection of SD-backed storage unsound, and a duplicate authoritative mode
  variable could disagree with the accepted two-plane truth table.
- **Disposition:** Accepted with seven concrete provisions:

  1. Extender MOS (EMOS) is one complete backward-compatible replacement for
     stock MOS, not a side-by-side companion. Its dispatcher alone selects the
     ordinary VDU route; Legacy must retain stock MOS behavior and interfaces.
  2. EMOS owns EDP-service activation in Legacy/Dual. Stock MOS cannot activate
     Extender and supports only Legacy.
  3. Formal mode is derived from committed VDU route plus EDP-service state,
     not from an independent competing mode variable.
  4. EMOS lifecycle machinery records requested target, any implementation-
     required pending attempt, committed state, last failure, and fallback
     information.
  5. Records are runtime state unless a separately reviewed restart mechanism
     requires retention. Persisted user preference is not a v1 contract.
  6. Command/API names, storage, file formats, and exact data structures remain
     deferred.
  7. Fixed-backend development builds still boot Legacy and require explicit
     activation.

### `W2D-Q08` — Dual shutdown ownership

- **Status:** Accepted 2026-08-23
- **Question:** Latch Dual after successful explicit activation and return to
  Legacy only through coordinated explicit shutdown, reset, or failure rather
  than when an initiating or last foreground caller exits?
- **Recommendation:** Accept. A last-caller heuristic is unsafe for persistent
  media, network, storage, callback, or resident work and would immediately
  undo a successful probe after its utility exits.
- **Disposition:** Accepted as proposed. Successful probe/activation latches
  Dual as system state. Foreground exit and zero known callers do not deactivate
  EDP. A normal explicit shutdown coordinates with registered work and may
  refuse or time out safely when owners cannot quiesce; a separately explicit
  forced shutdown may invalidate outstanding work after warning. Completion
  deactivates EDP and commits Legacy. P4 reset/failure follows Q05/Q06. Exact
  registration, shutdown, timeout, warning, and force APIs remain deferred.

### Accepted VDU/EDU call and destination boundary

Application entry point identifies the call class; committed operating mode
selects the ordinary VDU destination:

| Call class | Legacy | Dual | Exclusive Compatible | Exclusive Extended |
|---|---|---|---|---|
| `RST.LIL 10h`/`RST.LIL 18h` and C-runtime VDU output | onboard VDP | onboard VDP | EDP compatible backend | EDP enhanced backend |
| Explicit EDU API | unavailable until EDP activation | EDP | EDP | EDP |

The EMOS dispatcher owns the mode-sensitive destination of conventional VDU
calls; their identity and stream semantics do not become EDU merely because
the selected backend terminates at the EDP. Explicit EDU calls retain their
versioned API and separate result domain.

An EDU-aware application may use both call classes. “Mixed-API application”
describes this software pattern and does not name a fifth operating mode. In
Dual the call classes deliberately address different processors; in either
exclusive mode they can address different interfaces of the EDP. Software may
also require Exclusive Extended and use conventional VDU restart calls for
efficient high-frequency compatible output rather than wrapping every transfer
in an EDU invocation. The eZ80 application or its launcher must verify or
request Exclusive Extended before issuing mode-sensitive output that would be
unsafe or meaningless if EMOS routed it to the onboard VDP.

### `W2D-Q09` — Prohibited behavior

- **Status:** Accepted 2026-08-24
- **Question:** Accept the ten actor-explicit prohibited lifecycle behaviors as
  hard v1 constraints?
- **Recommendation:** Accept. They make negative qualification requirements
  visible rather than relying on implementation convention.
- **Cross-cutting amendment:** During review, the Author removed all active
  stock-MOS Extender operation from scope and accepted the pre-activation
  fail-safe design boundary above. This amends the owners and prerequisites
  beneath items 1 and 3 without adding or renumbering a prohibited behavior.
- **Review progress:** Item 1 was accepted with EMOS as commit authority,
  EDP/P4 firmware as readiness respondent, carrier wiring as the physical path,
  and QUAL-002 as electrical authority; a successful protocol handshake does
  not qualify the wiring. Item 2 was accepted with fixed EMOS reset-vector and
  C-runtime handlers feeding one dispatcher: each invocation snapshots one
  backend; the EMOS coordinator blocks new calls, waits for active calls and
  owned response work to finish or be abandoned, reinitializes affected parser
  state, and then commits atomically. Beta does not add a second semantic VDU
  parser or promise that a running application can carry a multi-call partial
  command across the disruptive transition. Item 3 was accepted as the
  hard-v1 pull-discovery and
  no-unsolicited-presence policy; EMOS alone commits mode after an explicit
  request/response transaction, while EDP/P4 firmware and carrier wiring remain
  quiescent before activation. Item 4 was accepted: the EMOS dispatcher,
  EDP/P4 firmware, and carrier wiring never mirror ordinary application VDU to
  both processors. Legacy/Dual route ordinary VDU only to onboard VDP;
  exclusive modes route it only to EDP. Private input/bootstrap traffic,
  recovery diagnostics, and separately identified qualification traffic are
  targeted exceptions rather than mirrored application output. Item 6 was
  accepted with EMOS named as the
  mode-transition authority and narrowed to one attempt per explicit request.
  Cross-boot `autoexec.txt` suppression is deferred to MODE-002 and is not a
  beta requirement. Item 5 was accepted as enforcement of Q05: EMOS recovery
  may use the onboard VDP after exclusive EDP failure only after disclaiming
  application/display continuity, and must not claim lost or unknown EDP state
  survived. Item 7 was accepted: EMOS recovery/reporting code and EDP/P4
  diagnostic firmware must not send the only report through a failed component
  when another accepted sink survives, and reporting must not delay safe
  recovery. Item 8 was accepted and generalized: EMOS is the only supported
  VDU-route, Extender-transport, and mode authority. No supported application,
  linked client, TSR, MOS Module, or resident service may redirect or claim
  those resources except through an explicit EMOS operation. This is a
  supported-path ownership guarantee, not adversarial isolation from deliberate
  unrestricted eZ80 register/GPIO manipulation and makes no non-bricking
  guarantee for code that violates the normative contract. Item 9 was accepted:
  EMOS alone names the current formal mode from its committed state. EDP/P4
  firmware and applications may report local, requested, pending, readiness,
  transport, or failure state but must not name an uncommitted, failed, or
  partial combination as a formal mode. Item 10 was accepted: the EMOS
  mode-transition coordinator must complete a committed return to Legacy before
  attempting any different non-Legacy destination. Q09 and Work 2.d are closed.
- **Disposition:** All ten prohibited behaviors are accepted as hard v1
  lifecycle constraints, subject to the recorded beta exceptions and
  conditional later work for state preservation and cross-boot retry handling.
  EMOS owns every formal transition and uses Legacy as the mandatory hub. A
  future direct non-Legacy transition requires separate architecture,
  implementation, and qualification approval.
