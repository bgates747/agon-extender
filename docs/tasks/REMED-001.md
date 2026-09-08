# REMED-001 — Reconcile the repository with the four-mode operating architecture

## State

- Status: In progress — Work 1 and the accepted D001/D002/F009 architecture
  promotions are complete; the remediation freeze remains active for open
  SETUP-005 decisions, task reconciliation, and four-mode qualification
  replacement work
- Started: 2026-08-23 17:02 EDT
- Finished: --

## Namespace

`REMED` identifies bounded, cross-cutting remediation required after an audit,
corrective action, or superseding architectural decision. It does not replace
the task that owns each underlying design or implementation decision. A REMED
task coordinates conformance, ordering, validation, and closure across those
owners.

## Intent

Bring every current authority, active task, reviewed machine record, generated
projection, implementation boundary, hardware assumption, procedure, and
qualification gate into conformance with
[`AUDIT-2026-08-23-001`](../decisions/AUDIT-2026-08-23-001-operating-mode-semantics.md)
and the accepted four-mode vocabulary:

- **Legacy mode** — `mode:extender:legacy`;
- **Exclusive Compatible mode** —
  `mode:extender:exclusive-compatible`, short form **Compatible**;
- **Exclusive Extended mode** — `mode:extender:exclusive-extended`, short form
  **Extended**; and
- **Dual mode** — `mode:extender:dual`.

This is a conformance task, not authority to resolve remaining SETUP-005
questions, invent firmware or protocols, change wiring, run the bench, or
silently reinterpret accepted source dispositions. Each substantive decision
remains with its named owner and Author review gate.

## Current-state freeze

From this task's start, the audited operating-mode state and every
mode-dependent consumer are frozen as **incomplete and potentially erroneous**
until this task closes or explicitly releases a bounded artifact:

1. Do not use the current three-mode QUAL-001 records or generated views as
   architectural authority, implementation input, or qualification scope.
2. Do not implement mode selection, transparent routing, response ownership,
   mode-dependent input/RTC/audio behavior, or mode transitions from stale
   terminology or classifications.
3. Do not perform a mode-dependent physical qualification run or create a new
   run identity against the superseded model.
4. Do not hand-edit generated qualification or dependency artifacts. Correct
   their reviewed authorities and regenerate them deterministically.
5. Preserve existing historical logs, runs, procedures, and predecessor
   evidence. They may describe the decisions or vocabulary in force at the
   time, but they are not current mode authority.
6. Treat current firmware and mode-neutral qualification as neither invalidated
   nor mode-qualified. The audit found no implemented Extender system-mode
   behavior; this freeze prevents new claims rather than presuming existing
   code is defective.
7. `light2-harness-r01` remains predecessor split-link evidence only. Current
   construction and component validation use r02's ordered circuit subsets
   under PORT-008-D003; r01 is not a stock-UART candidate.

The Author-accepted [staged process](../qualification/staged-circuit-validation.md)
permits preparation of mode-neutral circuit/component checks with their own
relevant prerequisites. Such a stage does not require the unfinished complete
mode matrix or release firmware. Physical execution still requires its
reviewed stage procedure and authorization; any test that exercises or claims
mode-dependent behavior remains subject to the freeze above.

This is a governance freeze, not a byte-for-byte source snapshot or release.
No commit, tag, version promotion, or generated-data promotion is authorized by
the governance freeze itself. The later source-freeze commits preserve the
review set but do not release this freeze, assign a version, or promote any
generated evidence.

## Authority and dependencies

- Operating-mode audit:
  [`AUDIT-2026-08-23-001`](../decisions/AUDIT-2026-08-23-001-operating-mode-semantics.md).
- Accepted architecture:
  [ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md)
  and [architecture.md](../architecture.md).
- Open architectural decisions: [SETUP-005](SETUP-005.md).
- Candidate qualification authority: [QUAL-001](QUAL-001.md) and
  [`docs/qualification/`](../qualification/README.md).
- Transport and system qualification: [PORT-008](PORT-008.md) and
  [QUAL-002](QUAL-002.md).
- Accepted source and compatibility surveys: [SETUP-004](SETUP-004.md) and
  [AUDIT-001](AUDIT-001.md).
- Versioning and run policy: [versions/README.md](../versions/README.md).

## Work 1 — Establish and preserve the remediation boundary

- [x] **1.a** Complete the repository-wide operating-mode audit and record
  stable findings, affected authorities, correction order, and unresolved
  decisions.
- [x] **1.b** Establish the design-audit document class and its authority
  boundary in `docs/decisions/README.md`.
- [x] **1.c** Freeze QUAL-001 Review Gate 2 mode promotion, withdraw the
  superseded three-mode `RG2-02`, and create replacement gate `RG2-02R` for the
  corrected four-mode classification.
- [x] **1.d** Mark current reviewed and generated qualification mode records as
  superseded candidate data while preserving deterministic reproducibility.
- [x] **1.e** Accept and record the four official names, stable IDs, and
  permitted short forms in SETUP-005, ADR-0014, architecture, and the current
  development log.
- [x] **1.f** Correct the inherited-harness assumption: preserve
  `light2-harness-r01` for Exclusive Extended only and require firmware-first
  requirements followed by a new Exclusive Compatible hardware design review.
- [x] **1.g** Add a visible operating-mode supersession notice to completed
  AUDIT-001 without rewriting its historical findings or stable requirement
  IDs.
- [x] **1.h** Declare the repository-wide mode-conformance freeze in this task,
  including its scope, exclusions, and release conditions.
- [x] **1.i** Review the initial audit-era edits as one bounded change set and
  classify every changed file as authority, task bookkeeping, reviewed input,
  generated output, historical record, or unrelated work before any commit is
  proposed.

### Work 1 execution record

Work 1.i reviewed all eight modified tracked files and all 43 untracked files
present on 2026-08-23. Classification is by authority role rather than file
extension:

| Files | Count | Classification | Freeze disposition |
|---|---:|---|---|
| `TODO.md` | 1 | Authoritative task index and task-state bookkeeping | Retain for review; it records QUAL-001 start state and REMED-001 registration only. |
| `docs/architecture.md` | 1 | Normative architecture | Preliminary four-mode correction; frozen pending Work 2 review of unresolved boundaries. |
| `docs/decisions/ADR-0014-edu-operating-modes-and-service-architecture.md` | 1 | Accepted but partial architecture decision authority | Accepted names are authoritative; other audit-era amendments remain subject to SETUP-005 reconciliation. |
| `docs/decisions/README.md` | 1 | Decision-process authority | Bounded addition of the design-audit record class; no product behavior. |
| `docs/decisions/AUDIT-2026-08-23-001-operating-mode-semantics.md` | 1 | Completed audit evidence and correction map | Retain as REMED-001 input; it does not itself authorize unresolved architecture or implementation. |
| `docs/tasks/AUDIT-001.md` | 1 | Completed historical task authority | Only a visible four-mode supersession notice was added; stable findings and requirement IDs remain unchanged. |
| `docs/tasks/PORT-008.md` | 1 | Active implementation/qualification task | Added stock-UART hardware boundary is accepted; complete task ownership and split remain frozen for Work 3. |
| `docs/tasks/QUAL-001.md` | 1 | Active qualification-infrastructure task and review-gate register | Work 1–3 execution records are retained; old RG2-02 is withdrawn and all mode promotion remains frozen. |
| `docs/tasks/SETUP-005.md` | 1 | Authoritative open-decision tracker | Accepted names and IDs are current; D001–D008 and affected analysis remain open under Work 2. |
| `docs/tasks/REMED-001.md` | 1 | Active conformance task | Current freeze and remediation plan; no implementation authority. |
| `docs/development/2026-08-23.md` | 1 | Dated historical record | Retain as contemporaneous provenance; amend only with later events rather than rewriting this entry. |
| `docs/qualification/README.md` | 1 | Durable qualification-process guidance | Correctly warns that current mode records are a superseded candidate; promotion remains blocked. |
| `docs/qualification/reviewed/*.yaml` | 9 | Human-maintained reviewed-input candidates | Interfaces and non-mode records remain candidates; modes, 633 mode expectations, and mode-scoped obligations are semantically superseded and frozen. |
| `docs/qualification/schema/*` | 2 | Durable schema authority and schema guidance | Structurally reusable; no four-mode architecture is encoded by the schema itself. |
| `docs/qualification/scripts/*` | 5 | Durable deterministic tooling | Build/model/validation are generally data-driven; renderer still hard-codes three columns and is frozen for Work 4. |
| `docs/qualification/tests/*` | 1 | Durable infrastructure tests | Internally passes against the frozen candidate but hard-codes 633 expectations; not evidence of four-mode correctness. |
| `docs/qualification/generated/**` | 17 | Deterministic generated output | Byte-reproducible but semantically superseded; preserve unchanged until reviewed inputs and generators are corrected together. |
| `docs/tasks/QUAL-001/PROPOSAL.md` | 1 | Task-local accepted proposal evidence | Historical design input, not current mode authority. |
| `docs/tasks/QUAL-001/fixtures/*` | 1 | Task-local proposal fixture | Historical three-mode fixture; retain as proposal evidence, not production input. |
| `docs/tasks/QUAL-001/schema/*` | 1 | Task-local proposal schema | Preserve as Gate 1 evidence; durable schema under `docs/qualification/` is the maintained implementation. |
| `docs/tasks/QUAL-001/scripts/*` | 2 | One-time task-local import/seed tooling | Import remains useful; three-mode seed is superseded and must not be rerun as current policy. |

The groups above account for every dirty path. No implementation source,
vendored source, build configuration, hardware profile, procedure, run
manifest, raw evidence, or bench-local file is changed or untracked.

#### Work 1.i findings

1. **No unrelated dirt found.** Every changed or untracked path belongs to
   QUAL-001 infrastructure, the operating-mode audit and accepted vocabulary,
   affected task bookkeeping, or REMED-001 itself.
2. **The dirty state is not one coherent final commit.** It combines the
   pre-audit QUAL-001 Work 1–3 candidate, the later audit and four-mode
   correction, and the remediation plan. Commit boundaries must be proposed
   only after the Author reviews this freeze and the semantic disposition of
   the superseded candidate.
3. **Deterministic does not mean current.** At this Work 1 checkpoint, the
   qualification generator and its then-current ten tests passed against the
   211-interface, three-mode, 633-tuple candidate. The suite later expanded,
   but that still proves internal consistency only; the accepted four-mode
   architecture requires 844 tuples and corrected obligations.
4. **Normative wording is partly ahead of open decisions.** Names, IDs, the
   common exclusive ownership direction, Dual's separate state domain, and the
   firmware-first stock-UART hardware boundary are accepted. Exact strict-mode
   carve-outs, lifecycle, response routing, input, RTC, and enhanced reverse
   semantics remain open. ADR-0014 and architecture must be reviewed in Work 2
   so accepted names are not mistaken for completion of those questions.
5. **The duplicate task-local and durable schemas are role-distinct but need to
   stay visibly so.** The task-local schema and fixture preserve Review Gate 1;
   the durable schema is the maintained implementation. Final conformance must
   ensure routine references never treat the proposal copy as production
   authority.
6. **PORT-008 is intentionally transitional.** It still plans the Exclusive
   Extended split link and now records that Exclusive Compatible needs
   firmware-first work and later new hardware. Work 3 must decide the final task
   split before either profile proceeds.

Work 1 is complete. The current state remains frozen; completion of this
inventory authorizes no correction, commit, generation, implementation,
hardware design, deployment, or physical test.

## Work 2 — Finish the architectural contract through SETUP-005

- [x] **2.a** Resolve the exact common ownership contract shared by Exclusive
  Compatible and Exclusive Extended, including logical authority over command
  processing, response production, parser effects, completion flags, sysvars,
  restart routing, input integration, RTC state, callbacks, and related eZ80
  assets. Accepted task-local inventory:
  [`exclusive-common-ownership.md`](REMED-001/exclusive-common-ownership.md).
- [x] **2.b** Produce the explicit Dual-mode ownership inventory required by
  `MODE-AUDIT-F003`: onboard-VDP-only, EDP-only, MOS-owned, separately
  namespaced, safely shareable, prohibited, and unresolved assets. Accepted
  task-local inventory:
  [`dual-mode-ownership.md`](REMED-001/dual-mode-ownership.md).
- [x] **2.c** Resolve D001 transparent routing separately for Exclusive
  Compatible and Exclusive Extended while factoring their common MOS-facing
  semantics. Analysis and question register:
  [`exclusive-routing-analysis.md`](REMED-001/exclusive-routing-analysis.md).
- [x] **2.d** Resolve D002 discovery, entry, exit, transitions, reset, failure,
  recovery, and fallback for all four modes, including deterministic Legacy
  bypass and prohibited transitions. Analysis and question register:
  [`mode-lifecycle-analysis.md`](REMED-001/mode-lifecycle-analysis.md).
- [ ] **2.e** Resolve D003 response delivery and MOS parser ownership for both
  exclusive modes and the separate EDU result domain in Dual mode. Defer final
  disposition until PORT-008 has produced the bounded Exclusive Extended
  vertical slice authorized by SETUP-005-D003; use its code and evidence to
  answer the cross-mode questions rather than attempting to settle them from a
  source survey alone.
- [ ] **2.f** Resolve D004 support boundaries for non-EDU-aware software in
  Dual mode without implying mirrored VDU traffic or shared canonical state.
- [ ] **2.g** Resolve D005 audio ownership and whether any mode may explicitly
  delegate EDP audio to the onboard VDP.
- [ ] **2.h** Resolve D006 maintenance/operator carve-outs, malformed-command
  behavior, and which modes carry the strict stock-observable failure promise.
- [ ] **2.i** Resolve D007 keyboard/mouse ownership, stock packet flow,
  EDP-local event delivery, configuration routing, and untouched-application
  behavior in both exclusive modes and Dual mode.
- [ ] **2.j** Resolve D008 RTC authority, read/set routing, MOS sysvars,
  persistence, synchronization, timezone, conflicts, and failure behavior in
  all four modes.
- [ ] **2.k** Freeze Exclusive Compatible's hardware-independent firmware
  demands: endpoint roles, stock-visible bytes, flow-control semantics, timing,
  buffering, reset, failure, and recovery. Do not infer physical circuitry from
  `light2-harness-r01`.
- [ ] **2.l** Freeze Exclusive Extended's enhanced reverse capabilities and
  distinguish product semantics from link-layer framing and pacing.
- [ ] **2.m** Update ADR-0014 and `docs/architecture.md` only with accepted
  decisions, retain unresolved items in SETUP-005, and review ADR completeness.

**Review Gate A:** The Author accepts all remaining SETUP-005 dispositions and
the resulting normative four-mode contract before production mode-dependent
implementation or qualification planning is released. PORT-008's bounded
Exclusive Extended response prototype is the sole current exception: it may
produce D003 discovery evidence under its fixed-backend, single-EMOS-writer,
Author-approved prototype gate but cannot make a production or cross-mode
claim.

### Current input amendment — 2026-09-08

SETUP-005 K001 selects browser → P4 → stock UART1 keyboard packets → EMOS as
the next increment. D003/D007 and Work 2.i are partially resolved for direction
and ownership; K002/K003 retain session/receiver details and broader mouse/
mode composition stays open. ADR-0014, architecture and the ownership inventory
are amended. The dated execution records below preserve earlier physical-input
assumptions; they do not require an onboard relay for browser keys. Parallel
work remains held while this bounded UART increment is reviewed.

### Work 2.a execution record

The task-local inventory separates semantic, storage, mechanism, and
physical authority across the common exclusive-mode path. It is grounded in
official VDP `v2.16.0`, MOS `v3.0.2`, and current official documentation. The
review confirms that the EDP owns command semantics, device state, and response
contents while MOS owns its restart ABI, response parser, canonical VDP sysvar
storage, completion flags, input hooks, and all eZ80 memory writes. The onboard
VDP remains the physical keyboard/mouse owner through v1.

The inventory deliberately leaves routing mechanics, mode lifecycle, audio
delegation, maintenance behavior, input relaying, RTC authority, and the two
separate physical transport contracts with D001–D008 and Works 2.c–2.l. The
Author accepted the task-local ownership boundary on 2026-08-23. Normative
promotion remains deferred to Work 2.m; no implementation, qualification data,
procedure, or hardware was changed.

### Work 2.b execution record

The task-local inventory expands the accepted “VDU/onboard plus
EDU/EDP” boundary into seven explicit classes: onboard-VDP-only, EDP-only,
MOS-owned, separately namespaced, safely shareable by deliberate copying or
coordination, prohibited collisions, and unresolved mechanisms. It establishes
that numeric or semantic similarity does not alias objects across processors;
the owning interface domain is part of every object's identity.

The inventory also identifies ten unresolved Dual-mode mechanisms and assigns
each to an existing decision or implementation owner. The Author accepted the
task-local boundary on 2026-08-23. Normative promotion remains deferred to
Work 2.m; no implementation, qualification data, procedure, transport, or
hardware was changed.

### Work 2.c execution record

Official MOS `v3.0.2` inspection found that a restart-only hook is incomplete:
`RST.LIL 10h`, the `RST.LIL 18h` byte loops, and MOS C-runtime `putch`/`printf`
all call the UART0 output routine independently. The candidate design inserts
one MOS-owned semantic VDU dispatcher above raw UART devices and gives it byte
and stream operations so the Extended transport can preserve block throughput.

Official VDP `v2.16.0` inspection also found that the onboard VDP remains in
`wait_eZ80()` until General Poll. Both exclusive modes therefore need a
controlled onboard-VDP bootstrap/configuration route if that processor is to
retain physical keyboard/mouse ownership; this route must never become mirrored
ordinary VDU. Exact startup and input mechanics remain assigned to D002, D003,
and D007.

Five questions are recorded in the task-local analysis and will be presented
one at a time. The Author accepted Q01 on 2026-08-23: both exclusive modes use
an Extender-enabled MOS routing modification in the first round. A later
MOS Modules-aligned service architecture is the aspirational route to genuinely
cooperative operation; [MOS-001](MOS-001.md) now owns its research,
architecture, possible mode supersession, and upstream alignment. That later
Modules path was cancelled by the Author on 2026-09-08 in favor of resident
EMOS extensions; MOS-001 is now a closed historical record. Q02 was
accepted on the same date: one MOS-owned byte/stream VDU dispatcher
captures restart and MOS C-runtime output while raw UART APIs retain their
device identities. Q03 was accepted with Legacy/Dual mapped to onboard UART0
and the two exclusive modes mapped to identical EDP parser semantics over their
respective backends. The Author also established a D002 invariant that missing
custom support must fail transactionally without changing the current mode;
stock MOS `Invalid command` is an acceptable result when no Extender facility
is installed. Q04 was accepted with MOS/eZ80 as the sole Rev 1 intermediary
between onboard VDP and EDP; no direct link is selected or guaranteed.
[LINK-001](LINK-001.md) owns a possible post-v1 bidirectional high-speed link,
with SPI only a candidate. Q05 permits fixed-backend MOS builds as necessary
Rev 1 staging artifacts without settling final runtime switching. The Author
accepted all five questions on 2026-08-23, closing Work 2.c and resolving D001.
No MOS code, firmware, qualification data, procedure, transport, wiring, or
hardware changed.

### Work 2.d execution record

The task-local candidate analysis factors lifecycle into an EMOS-owned VDU
route and a distinct EMOS-owned EDP-service state. Their four supported
combinations map
exactly to Legacy, Dual, Exclusive Compatible, and Exclusive Extended; the two
exclusive-route/EDP-inactive combinations are explicitly invalid.

The proposal permits live Legacy/Dual service activation because ordinary VDU
does not move. Its proof-of-concept/beta baseline makes every VDU-route change
restart-mediated while later work pursues safer state-preserving transitions.
It defines transactional activation, mode-specific boot responsibilities,
failure/reset classes, safe fallback, selection/persistence requirements, and
ten prohibited behaviors. Nine questions will be presented individually. The
Author accepted Q01 on 2026-08-23 and later amended its ownership boundary: the
committed EMOS-owned VDU route and EMOS-owned EDP-service state form a two-plane
truth table whose four supported
combinations are the four formal modes. Exclusive routes with inactive EDP are
invalid, and any proposed third independent state dimension requires explicit
architectural review. Q02 was accepted with staged scope: live Legacy/Dual
activation remains permitted; the proof-of-concept/beta baseline uses a
disruptive controlled restart for VDU-route changes and is an acceptable v1
fallback. State-preserving transitions are an aspirational v1 target and firm
v2 requirement under [MODE-001](MODE-001.md), without promising
cross-processor display-state migration. Q03 was accepted as the common
prepare/readiness/commit/recover transaction: no new route is published before
all prerequisites are ready and pre-commit failure restores a stable state.
The Extender MOS (EMOS) coordinator makes one attempt per explicit request and
does not autonomously re-arm it. Cross-boot suppression when `autoexec.txt`
reissues the same command requires retained state or equivalent cooperation; it
is not a beta requirement and is deferred to [MODE-002](MODE-002.md). No
implementation, qualification data, procedure, transport, wiring, or hardware
changed. The Author amended Q02
and accepted Q04 on 2026-08-23: Legacy is the mandatory transition hub; every
cold boot reaches fully operational Legacy; Extender contact occurs only after
an explicit late `autoexec.txt` or manual invocation; and a successful explicit
presence/version probe commits Dual. Exclusive entry is never a direct cold
boot operation. Persisted preferred-mode selection remains exploratory and is
not a v1 contract; one-shot transaction state remains a separate safety
mechanism. Q05 was accepted on 2026-08-23: EDP failure in Dual commits Legacy
without disturbing onboard VDU; exclusive EDP/transport failure blocks output
and either reinitializes within a bounded attempt or recovers disruptively to
Legacy without pretending application state survived. Structured failure
reporting is advisable during beta and a hard v1 requirement, but not a beta
gate. It must provide best-effort descriptive onscreen diagnostics and durable
machine-readable logs that identify practical consequences and include
truthful bounded processor context where safely obtainable.
[DIAG-001](DIAG-001.md) owns implementation and qualification.
Q06 was accepted on 2026-08-23: reset invalidates the affected component's
sessions, parsers, pending work, readiness, and authority even if RAM bytes or
other processors survive. Invalidation does not require erasure. eZ80/MOS and
whole-system resets return through Legacy, P4 reset in Dual commits Legacy, and
exclusive/onboard reset recovery follows the accepted failure and private-input
boundaries.
Q07 was accepted on 2026-08-23 and later amended. EMOS is a single complete
backward-compatible stock-MOS replacement whose dispatcher alone owns ordinary
VDU routing and whose EDU/lifecycle machinery alone owns EDP activation. Every
active Extender mode requires EMOS; stock MOS supports only Legacy. Formal mode
is derived from the two committed planes. Runtime lifecycle records include
requested, conditionally pending, committed, failure, and fallback information;
persisted user preference is not a v1 contract. Exact APIs/storage remain
deferred, and fixed-backend builds still require explicit activation after
Legacy startup.
Q08 was accepted on 2026-08-23. Successful explicit probe/activation latches
Dual as system state; it does not end when the initiating utility or last
foreground caller exits. Normal return to Legacy is an explicit coordinated
shutdown which may refuse or time out if registered work cannot quiesce. A
separately explicit forced shutdown may invalidate work after warning. Reset
and failure remain governed by Q05/Q06; exact session and shutdown APIs are
deferred.
Q09 item 3 was accepted on 2026-08-23 as a hard-v1 pull-discovery policy.
EDP/P4 firmware and carrier wiring remain quiescent while Legacy is committed
or a transaction is uncommitted. EMOS arms the eZ80-side receiver, initiates
the request, validates the EDP response, and alone commits mode. P4 reset
revokes asynchronous-send permission; EMOS quarantines stale traffic. Rev 1
defines no proactive presence signal. QUAL-002 owns power/reset order,
isolation, boot-chatter, and stale-traffic qualification; D003 owns parser and
response-domain mechanics.
Q09 item 1 was accepted on 2026-08-23. A reviewed transport/wiring profile must
be selected; EMOS arms the eZ80 receiver and sends the readiness request;
EDP/P4 firmware returns compatible identity, protocol, and capability data; and
EMOS alone commits the exclusive route. The handshake proves protocol
readiness, not electrical qualification; QUAL-002 remains the authority for the
physical wiring.
Q09 item 2 was accepted on 2026-08-23. EMOS installs one fixed set of modified
`RST.LIL 10h`, `RST.LIL 18h`, and C-runtime output handlers which call one VDU
dispatcher; mode changes do not swap vector tables. Each dispatcher invocation
uses one backend snapshot. The EMOS coordinator blocks new calls, waits for
active calls and owned response work to finish or be abandoned, reinitializes
affected parser state, and commits the new backend atomically. Beta adds no
second semantic VDU parser and does not preserve a multi-call partial command
across the disruptive transition.
Q09 item 4 was accepted on 2026-08-23. The EMOS dispatcher, EDP/P4 firmware,
and carrier wiring never mirror ordinary application VDU to both processors.
Legacy/Dual route ordinary VDU only to onboard VDP; exclusive modes route it
only to EDP. Private onboard input/bootstrap control, recovery diagnostics, and
separately identified qualification traffic remain targeted exceptions and are
not duplicated application output.

Q09 item 5 was accepted on 2026-08-23 as enforcement of Q05. After an exclusive
EDP failure, EMOS recovery may route diagnostics or restored Legacy output to
the onboard VDP only after explicitly disclaiming application and display
continuity. EMOS must not claim that lost or unknown EDP display, audio, buffer,
or application-visible state survived the fallback.

Q09 item 7 was accepted on 2026-08-24. EMOS recovery/reporting code and EDP/P4
diagnostic firmware must not send the only human or machine-readable failure
report through a failed processor, display, transport, storage device, or
physical connection when another accepted sink survives. Reporting must not
delay or block safe recovery merely to reach a preferred sink. DIAG-001 owns
the per-failure sink priorities and qualification.

The Author then made bounded P4 onboard-flash crash storage a hard v1
requirement. It is the minimum durable sink when the mainboard or optional P4
microSD is unavailable. The current dedicated `coredump` partition is a
candidate rather than a frozen format; DIAG-001 must qualify integrity,
interrupted writes, wear, native ESP-IDF coexistence, retrieval, and truthful
evidence boundaries. P4 microSD remains optional, and video/browser reporting
is not durable by itself.

Q09 item 8 was accepted and generalized on 2026-08-24. EMOS is the only
supported authority for ordinary VDU routing, Extender transport hardware, and
committed mode. Applications, linked clients, TSRs, MOS Modules, and resident
services may act only through an explicit documented EMOS operation. This is a
supported-path ownership guarantee, not adversarial isolation from deliberate
unrestricted eZ80 register or GPIO manipulation. The proof of concept and v1
do not require a bomb-proof privilege system; direct manipulation remains
unsupported caveat emptor and receives no non-bricking guarantee.

Q09 item 9 was accepted on 2026-08-24. EMOS is the sole authority that names
the current formal mode, and does so only from its committed state. EDP/P4
firmware and applications may report local, requested, pending, readiness,
transport, or failure state, but must not name an uncommitted, failed, or
partial combination as Legacy, Dual, Exclusive Compatible, or Exclusive
Extended.

Q09 item 10 was accepted on 2026-08-24. The EMOS mode-transition coordinator
must complete a committed transition to Legacy before attempting any different
non-Legacy destination. Direct non-Legacy transitions are outside the
proof-of-concept and v1 contract and require later separate architecture,
implementation, and qualification approval. This acceptance closes Q09,
REMED-001 Work 2.d, and SETUP-005-D002.

During Q09 review, the Author also accepted the distinction between call class
and mode-selected destination. `RST.LIL 10h`, `RST.LIL 18h`, and C-runtime
output remain VDU calls; EMOS routes them onboard in Legacy/Dual, to the EDP
compatible backend in Exclusive Compatible, and to the EDP enhanced backend in
Exclusive Extended. Explicit EDU calls remain a separate interface and result
domain. Applications may use both call classes without defining another mode,
and an application may intentionally require Exclusive Extended so it can use
conventional restart calls for efficient compatible output. Such software must
verify or request the required mode before issuing mode-sensitive output.

The Author then removed stock-MOS Extender operation from project scope. Direct
GPIO, UART, or parallel-bus experimentation remains physically possible but is
caveat emptor and does not constitute Dual or another supported mode. Linked
EDU code may exist only as an EMOS API binding. The Author nevertheless imposed
a hard project fail-safe pre-activation design boundary: carrier hardware defaults
P4-to-Agon drivers disabled independently of firmware; EDP firmware exposes
only a bounded, staged EMOS activation recognizer before commit; ordinary VDU,
EDU, update, and persistent-write operations remain unreachable; and valid
project-produced pre-activation handling remains bounded and safe. This is not
a guarantee for external code that bypasses EMOS; such code may corrupt,
damage, or brick either system. An optional warning
may use only an Extender-owned out-of-band display or log. QUAL-002 owns the
electrical proof; protocol/parser tasks own bounded malformed-input evidence.

## Work 3 — Reconcile active task ownership and sequencing

- [ ] **3.a** Decide whether PORT-008 becomes a multi-profile transport task or
  splits into separate Exclusive Compatible firmware and Exclusive Extended
  transport tasks. Preserve one shared official parser/packet compatibility
  authority.
- [ ] **3.b** Restructure the Exclusive Compatible firmware plan so deterministic
  implementation and host qualification proceed without physical hardware.
- [ ] **3.c** Preserve PORT-008's existing enhanced split-link work under
  Exclusive Extended and remove every implication that its harness qualifies
  Exclusive Compatible.
- [ ] **3.d** Add the explicit trigger for a later hardware-design task: create
  it only after Exclusive Compatible firmware requirements are mature enough
  to drive a circuit. That task must own design review, new revisioned hardware,
  safety review, procedures, and physical qualification.
- [ ] **3.e** Reconcile QUAL-002 with all four modes, including Legacy
  electrical absence, both exclusive ownership states, Dual coexistence, power
  and reset order, failure, and recovery.
- [ ] **3.f** Review PORT-003 and its qualification plan for mode-dependent
  claims. Preserve mode-neutral display implementation and evidence; add only
  accepted four-mode applicability and gates.
- [ ] **3.g** Reconcile PORT-004 audio obligations and output routes across all
  four modes without changing its guaranteed network/browser sink.
- [ ] **3.h** Reconcile PORT-005 input injection and future automatic routing
  across Exclusive Compatible, Exclusive Extended, and Dual.
- [ ] **3.i** Review PORT-006 and PORT-007 for mode-dependent service lifecycle,
  return-domain, startup, and failure assumptions; record explicit
  non-applicability where they are mode-independent.
- [ ] **3.j** Reconcile SETUP-004's accepted mode-dependent dispositions and
  VDU inventory annotations without reopening source-selection decisions that
  the audit did not invalidate.
- [ ] **3.k** Reconcile AUDIT-001 requirement applicability and ownership while
  preserving its accepted requirement IDs and historical evidence statements.
- [ ] **3.l** Update TODO ordering and every implementation/qualification gate
  so mode decisions, firmware contracts, generated qualification data, future
  hardware design, and physical tests occur in a coherent order.
- [ ] **3.m** Reconcile and sequence DIAG-001 against mode lifecycle, response
  routing, fallback, version identities, storage availability, and system
  qualification so failure reporting never depends solely on the component
  that failed.
- [ ] **3.n** Reconcile and sequence MODE-002 after beta regression evidence;
  do not make cross-boot `autoexec.txt` circuit breaking a beta requirement or
  v1 contract without demonstrated need and separate Author acceptance.

**Review Gate B:** The Author accepts the reconciled task ownership, task split,
and sequencing before any newly authorized production task begins
implementation. PORT-008's existing-task prototype exception remains bounded
by its own Author gate and cannot silently establish the final task split.

## Work 4 — Correct the durable qualification model

- [ ] **4.a** Replace candidate mode IDs with the four accepted IDs in reviewed
  mode vocabulary. Candidate-only IDs do not require an accepted-ID
  supersession relation, but their removal must remain explained by QUAL-001
  and this task.
- [ ] **4.b** Generate exactly one expectation tuple for every accepted
  interface/mode pair: currently 211 interfaces by four modes, or 844 tuples.
- [ ] **4.c** Keep all ordinary VDU expectations onboard-VDP-owned in Legacy and
  Dual unless an accepted command-specific decision says otherwise.
- [ ] **4.d** Apply the common exclusive compatibility surface to both Exclusive
  Compatible and Exclusive Extended, then represent transport-specific
  differences independently.
- [ ] **4.e** Reclassify every qualification obligation across the four modes,
  including transport, General Poll, response/sysvar fidelity, display, audio,
  input, RTC, lifecycle, electrical absence, malformed streams, carve-outs, and
  Console8 coverage.
- [ ] **4.f** Remove the current ambiguity in which EDP behavior reached through
  EDU in Dual mode is attached to a stock VDU interface row. Introduce explicit
  EDU interfaces, reviewed mappings, or another accepted subject type only
  after the EDU contract exists.
- [ ] **4.g** Update exact blockers and owner-task references to the reconciled
  SETUP-005, PORT, QUAL, and future hardware tasks.
- [ ] **4.h** Make the mode seeder consume the accepted four-mode policy rather
  than emitting the superseded three-mode set.
- [ ] **4.i** Make matrix rendering use reviewed mode order and labels rather
  than fixed Legacy/EDP-exclusive/Cooperative columns.
- [ ] **4.j** Replace the hard-coded 633-row unit assertion with an invariant
  derived from the reviewed interface and mode counts while explicitly
  checking the current expected total of 844.
- [ ] **4.k** Correct reviewed YAML first, regenerate canonical YAML and all
  Markdown/task/mode/blocker views deterministically, and reject hand-edited
  generated output.
- [ ] **4.l** Rerun schema, semantic, uniqueness, referential-integrity,
  complete-cross-product, evidence-scope, contradiction, determinism, and
  tracked-generation tests.
- [ ] **4.m** Present corrected `QUAL-001-RG2-02R` and all affected Review Gate 2
  classifications for Author review before authority promotion.

**Review Gate C:** The Author accepts the regenerated four-mode qualification
model and all remaining QUAL-001 Review Gate 2 items before QUAL-001 Work 4 or
mode-dependent qualification uses it as authority.

## Work 5 — Reconcile source-selection and dependency guidance

- [ ] **5.a** Audit reviewed SETUP-004 evidence and disposition records for old
  three-mode assumptions; change only mode applicability, owner, blocker, or
  explanatory scope unless a separate decision reopens source disposition.
- [ ] **5.b** Represent common exclusive behavior once and represent stock-UART
  versus enhanced-link adapters as distinct implementation and dependency
  nodes.
- [ ] **5.c** Keep upstream `legacyModes` unchanged and explicitly distinguish
  that stock VDU display-mode variable from Extender Legacy mode in agent-facing
  queries and documentation.
- [ ] **5.d** Update source-selection records so vendored, selected, excluded,
  replaced, and mode-conditional code remains unambiguous for future upstream
  merges.
- [ ] **5.e** Regenerate deterministic dependency artifacts and bounded views
  from corrected reviewed authorities; do not patch generated graph data.
- [ ] **5.f** Verify PORT-001/PORT-002 queries can identify code relevant to
  each official mode and transport without treating mode vocabulary as a
  compile-time source-selection decision unless explicitly accepted.

## Work 6 — Reconcile hardware, procedures, evidence, and public guidance

- [ ] **6.a** Keep `light2-harness-r01` and its inherited evidence explicitly
  scoped to Exclusive Extended; preserve `legacy-evidence` as provenance
  vocabulary rather than confusing it with Legacy mode.
- [ ] **6.b** Rename or qualify `legacy_uart_candidate` through the hardware
  profile's normal revision process so it cannot be mistaken for Legacy mode or
  Exclusive Compatible hardware authority.
- [ ] **6.c** Do not create or test Exclusive Compatible hardware until Work
  2.k is accepted and the separate hardware-design task is registered and
  approved.
- [ ] **6.d** Reconcile procedure templates and future run manifests so every
  mode-dependent claim names one official mode ID, transport profile, artifact
  identities, owner task, and accepted qualification boundary.
- [ ] **6.e** Preserve historical development logs, procedures, runs, and
  evidence as contemporaneous provenance. Add supersession notices or current
  log entries where needed; do not rewrite old outcomes into the new taxonomy.
- [ ] **6.f** Add the compact four-mode summary to README only after the
  normative boundaries and public compatibility wording are accepted.
- [ ] **6.g** Review versioning metadata and artifact records for stale mode,
  transport, harness, procedure, or qualification identities. Create new human-
  readable revisions where semantics changed; never relabel an old artifact.

## Work 7 — Validate conformance and release the freeze

- [ ] **7.a** Search all normative, active-task, reviewed-data, code-comment,
  procedure, and public-document surfaces for superseded mode names and IDs.
  Allow old terms only in clearly historical or superseded evidence.
- [ ] **7.b** Verify ADR-0014, architecture, SETUP-005, TODO, active tasks,
  reviewed qualification data, generated views, dependency records, hardware
  profiles, and development logs agree on names, IDs, ownership, transports,
  blockers, and sequencing.
- [ ] **7.c** Verify no firmware behavior, protocol, wiring, or qualification
  claim was changed merely by documentation reconciliation without its own
  accepted task and evidence.
- [ ] **7.d** Run every affected deterministic generator, validator, schema
  check, unit test, link/reference check, and clean-generation check.
- [ ] **7.e** Review the complete diff by authority class, confirm generated
  output derives from reviewed input, and identify any unrelated work that must
  remain outside the conformance commit.
- [ ] **7.f** Present the final conformance report, residual open decisions,
  deferred hardware work, and proposed commit boundaries to the Author.
- [ ] **7.g** Release only the bounded freezes whose authorities, tasks, data,
  and validation have passed their review gates. Do not declare global
  conformance while an unexplained stale consumer remains.
- [ ] **7.h** Record closure in the development log and mark REMED-001 complete
  only after Author acceptance. Commit and push remain separately authorized
  actions.

## Stop gates and exclusions

- No firmware, MOS, eZ80 application, protocol, wiring, hardware profile,
  procedure, generated qualification data, dependency graph, or bench state may
  be changed merely because this plan enumerates the work.
- Do not invent Exclusive Compatible circuitry before its firmware requirements
  are accepted.
- Do not use global text replacement on “legacy,” “mode,” “exclusive,” or
  “cooperative”; those words have unrelated historical and upstream meanings.
- Do not rewrite historical logs or run evidence to make old work appear to
  have used the new vocabulary.
- Do not commit, amend, tag, push, flash, deploy, or operate the bench without
  separate authorization.

## Completion criteria

1. All seven work sections and Review Gates A–C are complete and accepted.
2. Every audit finding has an accepted correction, an authoritative owner, or
   an explicit bounded deferral.
3. All current authorities and active consumers use the four official names and
   stable IDs consistently.
4. The corrected qualification model is deterministic, validated, reviewed,
   and promoted through QUAL-001 rather than by this task alone.
5. HW-001's current r02 common-UART design and PORT-008's candidate components
   follow the accepted staged process. Complete Exclusive Compatible claims
   retain the corresponding firmware/mode gates; the predecessor harness is
   never repurposed or relabeled as that design.
6. Historical evidence remains intact and clearly separated from current
   authority.
7. The Author accepts the final conformance report and explicitly releases the
   remediation freeze.

## Accepted REMED-002 coordination

The Author accepted REMED-001's split responsibilities for F009, F016, and
F018 in [REMED-002](REMED-002.md). The underlying evidence remains in
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md).
This intake does not release or replace the current four-mode freeze.

1. [x] **F009:** Treat promotion of accepted SETUP-005-D002 lifecycle content
   into ADR-0014 and `docs/architecture.md` as a prerequisite, not deferred
   cleanup, before downstream implementation consumes that decision.
2. [ ] **F016:** Require QUAL-002's local state and dependencies to name this
   freeze and the corrected four-mode release gates; its earlier plan approval
   cannot imply permission for mode-dependent physical qualification.
3. [ ] **F018:** Coordinate SETUP-005's actor-explicit decision for the beta
   restart carrier, retained target ownership, EMOS commit point, and Legacy
   fallback. Do not assign implementation to MODE-001 or MODE-002 implicitly;
   create a separately approved implementation/qualification task if the
   contract is accepted.

F009 completed on 2026-09-01. ADR-0014 and `docs/architecture.md` now contain
the full accepted D002 lifecycle contract and correct the stale unresolved-
dispatcher and controlled-mirroring statements. D003--D008, F016, F018, and
the four-mode conformance freeze remain open.

REMED-001 owns mode conformance and freeze release. REMED-002 owns the audit
disposition and cross-finding closure register; neither document substitutes
for SETUP-005's architecture decisions.
