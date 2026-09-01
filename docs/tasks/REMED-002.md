# REMED-002 — Remediate open-task implementation and evidence-integrity findings

## State

- Status: In progress — Gate 1 complete; owner-task remediation pending
- Started: 2026-09-01 12:52 EDT
- Finished: --

## Namespace

`REMED` identifies bounded, cross-cutting remediation required after an audit,
corrective action, or superseding architectural decision. It does not replace
the task that owns each underlying design or implementation decision. A REMED
task coordinates conformance, ordering, validation, and closure across those
owners.

## Intent

Disposition and close the implementation, evidence-integrity, authority, and
preimplementation findings recorded by
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md),
including the existing PORT-008 pre-activation corrective action. Preserve the
audit's stable finding identities, evidence, severity, provenance, and product
boundaries while promoting accepted work into its existing authoritative task.

This task is the coordination and closure register requested after the audit.
It is not a second audit, a new architecture authority, or a monolithic
implementation owner. It does not authorize source changes, protocol or wiring
decisions, commits, builds, deployment, physical operations, or qualification.
The Author must accept, reject, reassign, or split proposed dispositions before
the owning task acts on them.

## Scope

1. Record the Author's disposition of `INTEGRITY-AUDIT-F001` through `F021`,
   `INTEGRITY-AUDIT-R001` through `R003`, the six previously recorded
   `PORT008-PROV` defects, and the open PORT-008 pre-activation corrective
   action.
2. Promote each accepted action, validation gate, workaround, upstream
   dependency, and removal condition into the task that owns the affected
   product, tool, record, or decision.
3. Coordinate correction order and cross-task release gates without copying
   detailed finding evidence or implementation checklists out of their owning
   tasks.
4. Re-evaluate evidence produced by a tool or source-identity path found
   defective before relying on that evidence for promotion.
5. Preserve the distinction between permanent EDP or EMOS surfaces,
   fixed-purpose PORT-008 prototypes, temporary diagnostic code, upstream
   dependency defects, local defects, design blockers, and prospective risks.

Out of scope are unreviewed repository-wide expansion, implementing accepted
work directly in this coordinator, silently expanding UPSTREAM-001, changing
an accepted architecture decision, and operating the physical bench.

## Authority boundary and dependencies

1. The completed review task is [AUDIT-003](AUDIT-003.md). The durable audit
   record owns finding content and provenance; this task owns disposition and
   closure state.
2. The active corrective action is
   [`CA-2026-09-01-001`](../decisions/CA-2026-09-01-001-port008-preactivation-ready.md).
   Its containment and resolution conditions remain binding.
3. [REMED-001](REMED-001.md) owns the four-mode conformance freeze. REMED-002
   may coordinate F009, F016, and F018, but cannot release, replace, or weaken
   that freeze.
4. Existing implementation and setup owners include
   [PORT-003](PORT-003.md), [PORT-004](PORT-004.md),
   [PORT-005](PORT-005.md), [PORT-006](PORT-006.md),
   [PORT-007](PORT-007.md), [PORT-008](PORT-008.md),
   [SETUP-005](SETUP-005.md), [SETUP-006](SETUP-006.md),
   [HW-001](HW-001.md), [QUAL-001](QUAL-001.md),
   [QUAL-002](QUAL-002.md), [MODE-001](MODE-001.md),
   [MODE-002](MODE-002.md), [DIAG-001](DIAG-001.md),
   [REMOTE-001](REMOTE-001.md), and [LINK-001](LINK-001.md).
5. [UPSTREAM-001](UPSTREAM-001.md) owns its existing lifecycle proposal only.
   An upstream bug report or contribution arising from this audit requires an
   explicit scope decision; upstream work never substitutes for a required
   local containment or correction.
6. [`docs/tasks/README.md`](README.md) governs task promotion and prevents this
   audit silo from becoming a competing production authority.
7. [`docs/versions/README.md`](../versions/README.md) governs every named build,
   candidate, baseline, fixture, profile, and qualification run.

## Active containment

Until the relevant owner task and the Author release a narrower boundary:

1. Do not perform another PORT-008 firmware change, flash, powered transfer,
   reset, or physical qualification run under proactive P4 READY behavior.
2. Do not promote the current PORT-008 sender, receiver, analyzer, or dirty
   corrective candidates as product firmware or qualified transport.
3. Keep EMOS ordinary Legacy VDU routing on the onboard UART path. EMOS owns
   any request to activate the Extender transport; the P4 must not self-assert
   bus ownership merely because it booted.
4. Do not advance PORT-003 Gate G until a reviewable Gate G contract exists and
   its transport and system-qualification prerequisites are satisfied.
5. Do not accept new qualification based on affected validators, sanitizer
   runners, build staging, or PORT-008 analyzers until their false-green paths
   are repaired and relevant earlier evidence is re-evaluated.
6. Do not use `light2-harness-r02` as a frozen qualification input while its
   schematic digest and generated projection disagree.
7. Do not begin mode-dependent QUAL-002 physical work while REMED-001's freeze
   remains active or treat QUAL-002's older local approval wording as a release.
8. Preserve all historical failed-run evidence and the present mixed dirty
   worktree. Neither this task nor the audit authorizes staging or committing
   it as a single qualified change.

## Finding disposition register

The Author accepted REMED-002-D001 on 2026-09-01. `Accepted` adopts the audit's
class and the listed owner split as the initial remediation disposition;
`Retained` keeps a prospective risk in the named design and test boundary
without reclassifying it as a current defect. Detailed evidence and provenance
stay in the audit record.

| Finding | Class | Proposed authoritative owner | Disposition |
|---|---|---|---|
| F001 | Permanent EDP runtime defect; upstream `vdp-gl` origin reimplemented locally | PORT-003 | Accepted |
| F002 | Permanent EDP runtime defect; upstream `vdp-gl` origin reimplemented and amplified locally | PORT-003 | Accepted |
| F003 | Permanent EDP runtime exposure of an upstream ESP-IDF defect | PORT-006; PORT-003 browser regression coverage | Accepted split |
| F004 | Local EDP parser-integration defect; audio temporary, safe rejection durable | PORT-003, PORT-004, PORT-008, and SETUP-005 | Accepted split |
| F005 | Local PORT-008 prototype porting defect | PORT-008 | Accepted |
| F006 | Local durable qualification-tool defect | QUAL-001 | Accepted |
| F007 | Local durable staging/provenance-tool defect | PORT-003 and PORT-008 | Accepted split |
| F008 | Local hardware artifact-control drift | HW-001; consumed by PORT-008 and QUAL-002 | Accepted split |
| F009 | Local normative-authority promotion defect | SETUP-005 and REMED-001 | Accepted split |
| F010 | Local task-ownership conflict | REMOTE-001 and LINK-001; implementation requires separate task authority | Accepted split |
| F011 | Local qualification test-oracle defect | PORT-003 | Accepted |
| F012 | Permanent EDP teardown-ownership defect on an upstream failure path | PORT-006 | Accepted |
| F013 | Local PORT-008 prototype lifecycle regression | PORT-008 | Accepted |
| F014 | Local uncommitted PORT-008 evidence-tool defect | PORT-008 | Accepted |
| F015 | Local PORT-008 version-record drift | PORT-008 | Accepted |
| F016 | Local qualification task-status defect | QUAL-002 and REMED-001 | Accepted split |
| F017 | Local preimplementation Gate G incompleteness | PORT-003 after prerequisites | Accepted |
| F018 | Local mode-lifecycle design gap | SETUP-005 and REMED-001; implementation requires separate task authority | Accepted split |
| F019 | Local remote-authorization design blocker | REMOTE-001, with PORT-006 and EMOS dependencies | Accepted |
| F020 | Local diagnostic confidentiality and retention design blocker | DIAG-001 | Accepted |
| F021 | Local construction and resource-authority ambiguity | HW-001, SETUP-006, PORT-007, and future hardware-object promotion owner | Accepted split |
| R001 | Prospective PORT-008 synchronization risk, not a proved defect | PORT-008 design and tests | Retained |
| R002 | Prospective input-injection risk in intentionally retained upstream behavior | PORT-005 design and tests | Retained |
| R003 | Prospective remote-exposure risk beyond the accepted trusted-LAN boundary | REMOTE-001, with PORT-006 dependencies | Retained |

## Existing PORT-008 provenance register

These entries prevent the remediation plan from silently omitting defects that
PORT-008 recorded before the audit. They do not create duplicate findings.

| Recorded defect | Present boundary | Coordinated disposition | State |
|---|---|---|---|
| `PORT008-PROV-P001` — EMOS UART divisor overflow | Upstream MOS portability defect; permanent EMOS correction already committed | Preserve the correction and require clean identity and qualification through the existing EMOS/PORT-008 gates | Accepted |
| `PORT008-PROV-P002` — EMOS length-object overlap | Local prototype adapter defect; dirty correction exists | PORT-008 must preserve the width invariant without promoting the exact adapter | Accepted |
| `PORT008-PROV-P003` — EMOS sender cadence | Local prototype adapter regression; dirty correction exists | PORT-008 must preserve qualified timing requirements without promoting the exact adapter | Accepted |
| `PORT008-PROV-P004` — P4 direction-enable omission | Local prototype adapter regression; dirty correction exists | PORT-008 must preserve fail-safe direction ownership and break-before-make behavior | Accepted |
| `PORT008-PROV-P005` — P4 pre-activation READY | Local boot-integration defect; corrective action open | PORT-008 remains contained until the corrective action's resolution conditions are met | Accepted |
| `PORT008-PROV-P006` — P4 ZDI recovery refusal | Local diagnostic defect corrected before first commit | Preserve historical provenance; no product action remains unless the behavior regresses | Closed historical |

## Decision register

| Decision | Question | State | Downstream effect |
|---|---|---|---|
| REMED-002-D001 | Accept the audit classes, proposed owners, containment, and review order as the initial remediation register? | Accepted by the Author, 2026-09-01 12:57 EDT | Accepted rows are promoted into owner tasks; split rows retain the actor-specific owner division recorded above |
| REMED-002-D002 | Should upstream reports or contributions for F001--F003 extend UPSTREAM-001 or receive separate task authority? | Pending after owner-task promotion and local correction design | Determines external contribution tracking; cannot delay local containment |
| REMED-002-D003 | Should the exact PORT-008 prototype adapters be repaired only for bounded investigation or be replaced after the activation contract is accepted? | Blocked on PORT-008 and SETUP-005 decisions | Determines prototype lifecycle without changing durable timing, width, ownership, or activation requirements |

### REMED-002-D001 accepted decision

The Author accepted the register as the starting disposition on 2026-09-01:
treat F001--F016 as definite
defects or authority defects, F017--F021 as required preimplementation design
closures, and R001--R003 as prospective risks that must remain in their named
task designs. Retain the audit's proposed owners unless an owner task review
shows that a narrower split is needed.

Alternative 1 is to accept only the immediate runtime findings. That shortens
the first implementation queue but leaves evidence tools capable of producing
false confidence and leaves known downstream ownership conflicts available to
future work. Alternative 2 is to reject or reassign individual findings; each
such disposition needs contrary evidence or an explicit replacement owner so
that a stable finding does not disappear from the work hierarchy.

The accepted decision authorizes task promotion and detailed planning only. It does not
authorize source edits, architecture changes, physical operations, or commits.

## Work 1 — Author disposition and task promotion

- [x] **1.a** Present REMED-002-D001 and record the Author's answer.
- [x] **1.b** Record an accepted, rejected, reassigned, or split disposition
  with rationale for every F-row; retain each R-row as a named design risk or
  record why it no longer applies.
- [x] **1.c** Add accepted actionable work to each authoritative task's
  instructions, decision register, dependencies, and validation gates. Link
  back to the stable audit finding rather than copying its evidence.
- [x] **1.d** Reconcile the six prior PORT-008 provenance entries with their
  current owner-task records and clean/dirty source identities.
- [x] **1.e** For every inherited upstream problem, record the exact upstream
  project and identity, local remedy, upstream issue or evidence where one is
  pursued, and the condition under which a workaround may be removed.
- [x] **1.f** Review the resulting task-detail changes as one bounded
  documentation set before proposing any implementation sequence or commit.

### Gate 1 — Disposition authority

Gate 1 passes when the Author has reviewed D001, every audit row has an
explicit disposition, every accepted action has one authoritative owner, and
no task or audit document competes with that owner.

### Work 1 execution record

The Author accepted D001 on 2026-09-01 at 12:57 EDT. F001--F016 are accepted
as definite runtime, evidence, configuration, or authority defects;
F017--F021 are accepted as preimplementation design closures; and R001--R003
are retained as prospective risks in their named designs. Split rows now name
separate actor-specific actions rather than competing owners.

The promotion pass updated PORT-003 through PORT-008, QUAL-001, QUAL-002,
SETUP-005, SETUP-006, HW-001, REMED-001, DIAG-001, REMOTE-001, and LINK-001.
Each task links the stable audit finding and owns only its implementation,
consumer gate, policy, research, or qualification portion. The detailed
evidence and exact upstream/local provenance remain solely in the audit.

The six prior PORT-008 provenance entries are reconciled in PORT-008: P001's
permanent EMOS correction remains qualification-gated; P002--P005 contribute
durable invariants without promoting the exact prototype adapters; and P006 is
closed historical diagnostic provenance. Exact upstream identities and
evidence remain recorded in the audit. Exact post-run P4 and EMOS dirty deltas
are preserved as historical patch evidence under PORT-008 without changing the
run manifests' dirty-source identity. Each retained dependency remedy must
record a removal condition when its owning task selects the implementation;
no workaround was silently selected during intake.

The bounded promotion set changes task documentation and QUAL-002's visible
blocked state only. It changes no source, normative architecture, firmware,
hardware artifact, procedure, evidence, qualification result, or physical
state. Local links, TODO/detail correspondence, whitespace, and diff checks
passed. Gate 1 is complete; implementation remains subject to each owner
task's existing Author gates and the containments above.

## Work 2 — Runtime and electrical containment

- [ ] **2.a** PORT-003 must give frame suspension and palette/Copper/frame
  publication one explicit synchronization and lifetime contract, then add
  deterministic concurrent interleaving tests for F001 and F002.
- [ ] **2.b** PORT-006 must make WebSocket transmission correct under positive
  short writes or pin a verified upstream correction, then fault-inject
  congestion and preserve immutable snapshot ownership through completion.
- [ ] **2.c** PORT-006 must retain ownership of a live HTTP server across every
  failed stop or rollback path, define callback lifetime, and validate retry,
  destruction, and partial-start failure for F012.
- [ ] **2.d** PORT-003, PORT-004, PORT-008, and SETUP-005 must ensure every
  reachable audio or updater command consumes or safely rejects its complete
  grammar before the retained parser resumes.
- [ ] **2.e** PORT-008 must replace the infinite external-clock wait with a
  bounded abort that releases READY and every direction output, including
  stopped-clock, stuck-VALID, and timeout tests.
- [ ] **2.f** PORT-008 must make receiver initialization transactional and
  retryable, unwind each partial resource path, and distinguish started from
  merely allocated state.
- [ ] **2.g** PORT-008 must resolve the pre-activation corrective action through
  an Author-approved EMOS-requested activation contract, deterministic
  fail-closed tests, and a separately authorized controlled physical run.
- [ ] **2.h** PORT-008 must resolve R001 through a documented ESP-IDF ordering
  guarantee or explicit synchronization appropriate to callback/task
  publication.

### Gate 2 — Runtime safety

Gate 2 passes only when each accepted high-severity runtime finding has an
accepted correction and decisive negative-path validation in its owner task.
The PORT-008 physical hold remains until the corrective action independently
meets every resolution condition.

## Work 3 — Evidence and configuration trust

- [ ] **3.a** QUAL-001 must validate exact task and decision identities,
  evidence-path existence, all owner/blocker fields, and freshness of stored
  generated-input digests, with adversarial negative tests for F006.
- [ ] **3.b** PORT-003 and PORT-008 must bind staged object and firmware bytes
  cryptographically to the recorded source commit and reject a build directory
  produced from another commit for F007.
- [ ] **3.c** PORT-003 host runners must make UBSan diagnostics fail the run,
  use an explicit non-recovering policy where appropriate, and prove the
  false-green probe fails for F011.
- [ ] **3.d** PORT-008 analyzers must return failure for invalid evidence,
  validate every procedure precondition they claim, verify data and
  setup/hold where required, and freeze exact accepted tool hashes for F014.
- [ ] **3.e** HW-001 must reconcile the r02 maintained schematic, frozen
  digest, generated projection, and applicability metadata before PORT-008 or
  QUAL-002 consumes that design.
- [ ] **3.f** PORT-008 must reconcile baseline and corrected-candidate MOS
  source identities under the versioning policy for F015.
- [ ] **3.g** Re-run or explicitly withdraw every promotion claim whose support
  depended materially on a corrected false-green tool or mismatched identity.

### Gate 3 — Evidence trust

Gate 3 passes when each corrected tool rejects its demonstrated adversarial
case, all consumed artifacts resolve to exact maintained bytes, and affected
earlier evidence has an explicit retained, rerun, superseded, or withdrawn
disposition.

## Work 4 — Architecture, ownership, and future gates

- [ ] **4.a** SETUP-005 and REMED-001 must promote all accepted lifecycle,
  reset, discovery, recovery, and transition decisions into ADR-0014 and the
  normative architecture before downstream implementation consumes them.
- [ ] **4.b** REMOTE-001 and LINK-001 must separate remote product ownership
  from direct-link research; any accepted implementation must receive a
  separately approved owner task.
- [ ] **4.c** QUAL-002 must expose REMED-001's active freeze and corrected
  four-mode prerequisites in its local state and gates.
- [ ] **4.d** PORT-003 must define Gate G's scope, fixtures, stop conditions,
  prerequisites, and acceptance criteria before implementation begins.
- [ ] **4.e** SETUP-005 and REMED-001 must name the processor that restarts,
  the owner and storage of a surviving target request, the EMOS commit point,
  and Legacy fallback. Accepted implementation and qualification must then be
  assigned separately.
- [ ] **4.f** REMOTE-001 must preserve authenticated remote-origin provenance
  through EMOS authorization or explicitly constrain remote terminal authority
  before selecting an input representation.
- [ ] **4.g** DIAG-001 must define classification, redaction, authentication,
  retention, export, and erase policy before capturing or exporting memory.
- [ ] **4.h** HW-001, SETUP-006, PORT-007, and the hardware-object promotion
  owner must establish one current construction and board-resource authority
  with revision applicability.
- [ ] **4.i** PORT-005 and REMOTE-001 must retain R002 and R003 in their design
  fixtures and security gates without presenting either as a current defect.

### Gate 4 — Downstream readiness

Gate 4 passes when accepted architecture is in normative authority, every
future implementation gate is actor-explicit and reviewable, and every
cross-task responsibility has one owner. Gate 4 does not itself release
REMED-001, PORT-008, QUAL-002, or any physical operation.

## Work 5 — Closure and durable promotion

- [ ] **5.a** Confirm that every finding has final disposition and every
  accepted correction has validation evidence or an explicitly open owner-task
  gate that prevents premature consumption.
- [ ] **5.b** Remove duplicate remediation checklists after their authoritative
  owner tasks contain the accepted work; preserve stable audit links and dated
  evidence.
- [ ] **5.c** Promote recurring test, validation, staging, configuration, and
  operating guidance from task silos into durable role-named locations, with
  one maintained authority for each construct.
- [ ] **5.d** Record completed corrections, retained risks, remaining external
  dependencies, released containments, and any deliberately unresolved owner
  gates in the current development log.
- [ ] **5.e** Review the final documentation and implementation change sets,
  run proportionate validation, and obtain separate Author approval for any
  commit, release, deployment, or physical qualification.

## Completion criteria

REMED-002 may close only when:

1. every F, R, prior PORT-008 provenance entry, and the corrective action has a
   final recorded disposition;
2. every accepted permanent runtime or evidence-tool defect is corrected and
   decisively validated in its owning task;
3. every accepted prototype correction is either kept visibly bounded or
   replaced without promoting fixed-purpose code into EDP or EMOS product
   authority;
4. every accepted architecture or ownership defect is corrected in its
   normative or task authority;
5. every prospective risk remains in the design and fixture gates of the task
   that could turn it into a defect;
6. evidence affected by F006, F007, F008, F011, F014, or F015 has been
   re-evaluated and cannot support an unqualified promotion claim; and
7. all remaining freezes and corrective actions are either closed by their
   own criteria or remain explicitly visible in every consumer that they
   block.

Closing this coordinator does not close another task, corrective action, or
freeze by implication.
