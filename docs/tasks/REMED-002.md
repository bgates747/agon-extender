# REMED-002 — Remediate open-task implementation and evidence-integrity findings

## Keyboard-priority amendment — 2026-09-08

SETUP-005 K001 selects the existing UART browser-keyboard path. F010 therefore
keeps LINK-001 outside its critical path; F019/R003 apply to session admission
and EMOS source authority while preserving stock keyboard wire bytes. R002's
ordered-event risk remains in PORT-005. The historical audit findings are not
rewritten or marked fixed by this documentation amendment.

## State

- Status: In progress — Gate 1 complete; PORT-003 Work 2.a findings recorded
  and broad hardening deferred under D004/D012; REMED-002-D003 resolved in
  favor of replacement production data-plane objects; the P4 and EMOS
  forward-data-plane compositions are software-integrated and local defects
  P008--P044 are recorded at the bounded host/source/build level; P034--P040
  have retained corrections, P042/P043 have checkpointed provisional corrections,
  and P041/P044 retain explicitly open validation/normalization paths,
  while owner-task target-runtime, provenance, activation, return, artifact,
  and physical remediation remains pending
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

1. Record the Author's disposition of `INTEGRITY-AUDIT-F001` through `F022`,
   `INTEGRITY-AUDIT-R001` through `R003`, the recorded `PORT008-PROV` defect
   register, and the open PORT-008 pre-activation corrective action.
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

PORT-008-D003 now sequences component work through r02's ordered circuit
stages under [staged circuit validation](../qualification/staged-circuit-validation.md).
Apply each finding to the code, observation method, and claim actually selected
by the stage. The deferred release-pair tool program is not a blanket gate on
power/bias or other independently evidenced circuit checks. Existing defects
remain open and no affected report is accepted merely by changing the process.

Until the relevant owner task and the Author release a narrower boundary:

1. Do not deploy, flash, reset, or perform another powered PORT-008 transfer or
   qualification run under the retired proactive-P4-READY behavior. D002's
   software-only replacement boundary does not relax that physical hold.
2. Do not promote the retired PORT-008 sender, receiver, analyzer, or the
   source-frozen but unidentified replacement integration as product firmware
   or qualified transport. Its recorded builds predate the source freeze.
3. Keep EMOS ordinary Legacy VDU routing on the onboard UART path. EMOS owns
   any request to activate the Extender transport; the P4 must not self-assert
   bus ownership merely because it booted.
4. Do not advance PORT-003 Gate G until a reviewable Gate G contract exists and
   its transport and system-qualification prerequisites are satisfied.
5. Treat predecessor validators, staging, and analyzers as historical evidence
   only. Repaired replacement checks support only their stated bounded claims;
   relevant earlier evidence still requires an explicit retained, rerun,
   superseded, or withdrawn disposition before reuse.
6. **Superseded containment:** the former `light2-harness-r02` digest/
   projection mismatch was reconciled under F008. That artifact-control repair
   does not qualify construction or electrical behavior. The later
   connectivity/profile discrepancy recorded on 2026-09-05 is now HW-001's
   explicit S3 controlled-input blocker.
7. Do not begin mode-dependent QUAL-002 physical work while REMED-001's freeze
   remains active or treat QUAL-002's older local approval wording as a release.
8. Preserve all task-controlled historical failed-run evidence and predecessor
   patch bytes. Dirty state alone is not an audit exclusion: review and mark
   stale maintained files unless an explicit current Author exclusion applies.
   Do not stage or represent the mixed worktree as one qualified change.

## Finding disposition register

The Author accepted REMED-002-D001 on 2026-09-01. `Accepted` adopts the audit's
class and the listed owner split as the initial remediation disposition;
`Retained` keeps a prospective risk in the named design and test boundary
without reclassifying it as a current defect. Detailed evidence and provenance
stay in the audit record.

| Finding | Class | Proposed authoritative owner | Disposition |
|---|---|---|---|
| F001 | Upstream `vdp-gl` synchronization defect reimplemented locally; Extender-specific manifestation not yet demonstrated | PORT-003 research record | Recorded; correction deferred pending D012 trigger evidence |
| F002 | Upstream mutation-exclusion defect with plausible local amplification; Extender-specific manifestation not yet demonstrated | PORT-003 research record | Recorded; correction deferred pending D012 trigger evidence |
| F003 | Permanent EDP runtime exposure of an upstream ESP-IDF defect | PORT-006; PORT-003 browser regression coverage | Accepted split |
| F004 | Local EDP parser-integration defect; audio temporary, safe rejection durable | PORT-003, PORT-004, PORT-008, and SETUP-005 | Accepted split |
| F005 | Local PORT-008 prototype porting defect | PORT-008 | Accepted |
| F006 | Local durable qualification-tool defect | QUAL-001 | Accepted |
| F007 | Local durable staging/provenance-tool defect | PORT-003 and PORT-008 | Accepted split |
| F008 | Local hardware artifact-control drift | HW-001; consumed by PORT-008 and QUAL-002 | Remediated 2026-09-01; digest and projections reconciled, physical gates unchanged |
| F009 | Local normative-authority promotion defect | SETUP-005 and REMED-001 | Remediated 2026-09-01; accepted D002 content promoted |
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
| F022 | Upstream official VDP/vdp-gl lifetime defect; no distinct Extender manifestation demonstrated | PORT-003 research record | Recorded; local correction and regression design deferred pending D012 trigger evidence |
| R001 | Prospective PORT-008 synchronization risk, not a proved defect | PORT-008 design and tests | Retained |
| R002 | Prospective input-injection risk in intentionally retained upstream behavior | PORT-005 design and tests | Retained |
| R003 | Prospective remote-exposure risk beyond the accepted trusted-LAN boundary | REMOTE-001, with PORT-006 dependencies | Retained |

## Existing PORT-008 provenance register

These entries prevent the remediation plan from silently omitting defects that
PORT-008 recorded before the audit. They do not create duplicate findings.

| Recorded defect | Present boundary | Coordinated disposition | State |
|---|---|---|---|
| `PORT008-PROV-P001` — EMOS UART divisor overflow | Upstream MOS portability defect; permanent EMOS correction already committed | Preserve the correction and require clean identity and qualification through the existing EMOS/PORT-008 gates | Accepted |
| `PORT008-PROV-P002` — EMOS length-object overlap | Local prototype adapter defect | The exact adapter is retired from production closure; the replacement engine uses an exact 16-bit bounded count and chunks larger application streams below the physical-record limit | Accepted/replaced |
| `PORT008-PROV-P003` — EMOS sender cadence | Local prototype adapter regression | The exact adapter is retired from production closure; the replacement engine preserves the qualified CLOCK/VALID/data cadence invariant | Accepted/replaced |
| `PORT008-PROV-P004` — P4 direction-enable omission | Local prototype adapter regression | The replacement target owner controls fail-safe direction and teardown; the predecessor remains prototype evidence and is excluded from the production composition | Accepted/replaced |
| `PORT008-PROV-P005` — P4 pre-activation READY | Local boot-integration defect; corrective action open | The fixed production-data-plane composition asserts readiness only inside its supplied active epoch, but production activation remains contained until the corrective action's resolution conditions are met | Accepted/partially replaced; activation open |
| `PORT008-PROV-P006` — P4 ZDI recovery refusal | Local diagnostic defect corrected before first commit | Preserve historical provenance; no product action remains unless the behavior regresses | Closed historical |
| `PORT008-PROV-P007` — bounded RST 18 return-value mismatch | Upstream official documentation says A returns the last byte; official MOS and current EMOS return zero on success | Record without correction or broad regression design; factoring must not silently change de-facto behavior unless an Extender-specific trigger reopens it | Recorded/deferred under D004 and PORT-003-D012 |
| `PORT008-PROV-P008` — EMOS selected-worktree forwarding omission | Local EMOS build-wrapper defect; generic `mos-agondev` honored the inputs it received | Forward `MOS_WORKTREE` through every EMOS build/qualification target and retain regression coverage | Corrected during production-object factoring |
| `PORT008-PROV-P009` — epoch commit could erase a concurrent writer fault | Local EMOS production-factoring defect; the epoch implementation is project-owned and absent from official MOS | Preserve the atomic begin/commit protocol and writer-contention regression | Corrected before handoff |
| `PORT008-PROV-P010` — epoch commit could overwrite a concurrent leave | Local EMOS production-factoring defect; official MOS has no corresponding epoch lifecycle | Preserve leave invalidation of in-progress entry and the fail-closed commit regression | Corrected before handoff |
| `PORT008-PROV-P011` — rejected writer could unlock before failure publication | Local EMOS production-factoring defect; official MOS has no corresponding writer/lease path | Preserve failure-before-unlock ordering and its adversarial regression | Corrected before handoff |
| `PORT008-PROV-P012` — linked verifier claim overstatement | Local EMOS evidence-tool defect; official MOS supplies no project parallel verifier | Keep success text bounded, require exact fixed-coordinator call edges and byte/block bridge ABI shapes, and retain false-green tests | Corrected and strengthened before v10 handoff |
| `PORT008-PROV-P013` — UART1 open versus parallel Port C epoch race | Local EMOS integration defect: official MOS legitimately owns Port C for UART1 and has no competing parallel epoch | Keep the shared atomic Port C reservation across every UART1 flag/mux/register mutation through active publication | Corrected during final reconciliation |
| `PORT008-PROV-P014` — UART1 guard initially profile-optional | Local EMOS build-profile parity defect; neither the macro nor the parallel owner exists upstream | Keep the guard unconditional in the maintained source, require both native ZDS and AgonDev source closures to include its dependencies, and retain parity regression coverage | Corrected during final reconciliation |
| `PORT008-PROV-P015` — failed adapter recovery could be discarded or followed by an ownership switch | Local EMOS coordinator defect; official MOS has no Extender adapter lifecycle or corresponding recovery transaction | Propagate recovery failure, retain the old mode/backend/adapter ownership, and make a repeated Legacy request retry retained fixed-route cleanup | Corrected with extracted production transaction/recovery tests before v10 handoff |
| `PORT008-PROV-P016` — private parallel statuses escaped into the public command-error domain | Local EMOS integration defect; official `mos_error()` is correct for its supported MOS/FatFS result domain and has no Extender parallel statuses | Retain the raw lifecycle diagnostic internally while mapping the public command result to a printable supported EMOS error | Corrected with public-result/raw-diagnostic tests before v10 handoff |
| `PORT008-PROV-P017` — idle target receive period treated as fatal | Local P4 target-policy defect; upstream PARLIO does not define Extender record/READY policy | Keep the advertised transaction armed while `VALID_N` is inactive and start the fatal deadline only after an active record begins | Corrected with host/source-contract checks; target runtime open |
| `PORT008-PROV-P018` — concurrent fault converted an advertised byte to synthetic `0xFF` | Local `ExtenderVdpStream` contract violation; the retained parser's `available()` then `read()` behavior is inherited upstream | Preserve exactly one advertised byte across the fault and block all later unadmitted input | Corrected with available/peek/read fault interleavings; retained-parser runtime gate open |
| `PORT008-PROV-P019` — fault publication raced record admission and success reporting | Local P4 data-plane defect; no upstream Extender admission boundary exists | Keep one nonblocking sequentially consistent cancellation edge, quarantine any pre-fault winner, and check fault/cancel/lease after commit | Corrected with arbitration and quarantine regressions |
| `PORT008-PROV-P020` — qualification cleanup failure was followed by lease revocation | Local non-release qualification-owner defect; no upstream counterpart exists | Retain sole ownership and retry idempotent teardown until success before revoking the epoch | Corrected with source-contract cleanup-path checks; target runtime open |
| `PORT008-PROV-P021` — process-task creation failure continued into a false-live boot | Local guarded P4 boot-integration defect; no upstream Extender qualification branch exists | Request transport stop and return before boot-screen and network publication | Corrected with source-contract startup-path checks |
| `PORT008-PROV-P022` — selected EMOS source/prepared-tree preflight checked the default stock pair | Local generic `mos-agondev` root-orchestration defect; official MOS supplies neither this prepared-tree boundary nor the product wrapper | Require EMOS to forward both maintained source and prepared tree, authenticate that exact pair before any object recipe, and reject redirected assembly output paths | Corrected in generic build tooling and paired regressions; fresh provenance build pending |
| `PORT008-PROV-P023` — qualification-only P4 definition reached production-object compile commands | Local P4 qualification-profile defect; official VDP has no Extender qualification macro or composition | Confine the role definition to qualification-only translation units, reject global build-flag reintroduction, and require fresh common-object records | Corrected in source selection/profile tooling; fresh provenance build pending |
| `PORT008-PROV-P024` — EMOS identity/fixed-role definitions reached every C compile command | Local EMOS/generic-build profile integration defect; official MOS has no EMOS role flags | Apply role definitions only to `src/emos.c` and require ordinary/fixed captures to prove identical common-unit commands and objects | Corrected in generic build tooling and EMOS profiles; fresh provenance build pending |
| `PORT008-PROV-P025` — P4 source/build/status identity definitions reached every translation unit | Local P4 identity-injector defect; official VDP has no Extender identity layer | Scope varying identity bytes to the boot identity owner, bind them to the approved build record, and retain exact common-command comparison | Corrected in source/identity tooling; fresh provenance build and Author-approved identities pending |
| `PORT008-PROV-P026` — fixed EMOS composition label replaced its firmware source/build identity | Local EMOS fixed-profile defect; official MOS has neither identity layer | Use the common `agon-emos` firmware lineage and a separate `port-008-forward-qualification` revision, scope both to `src/emos.c`, and report the latter as non-release | Corrected in the profile/diagnostic boundary; fresh provenance build and Author-approved identities pending |
| `PORT008-PROV-P027` — P4 fixed composition lacked an independent qualification identity | Local P4 qualification/identity-integration defect; official VDP has no Extender fixed composition | Bind the fixed caller to a separately revisioned qualification identity at the boot owner, forbid it in ordinary roles, and verify the final diagnostic/image | Corrected in source/identity tooling; Author-approved revision and fresh target evidence pending |
| `PORT008-PROV-P028` — EMOS selected toolchain was not forwarded to recursive producer targets | Local EMOS wrapper defect; official MOS has no AgonDev product wrapper | Forward the exact absolute selected toolchain through firmware, fixed, and qualification targets and test all three | Corrected with regression; fresh target evidence pending |
| `PORT008-PROV-P029` — generic recorder/build-interface draft admitted cross-unit/session and response ambiguity | Local pre-baseline `mos-agondev` evidence-tool defect; official MOS has no actual-step recorder | Require literal source scoping, unique sessions, exact recorder/session/kind producer chains, non-nested response records, and authenticated driver-selected assembler inputs | Corrected before retained evidence in `7e00798`/`64bbf34`; stale rehearsal invalidated |
| `PORT008-PROV-P030` — P4 recorder draft underbound actual argv/environment/runtime roots and dispatched backends | Local pre-baseline P4 evidence-tool defect; Espressif dispatch is intentional upstream behavior, while omitted backend authentication was local | Directly execute the round-tripped vector, bind deterministic environment/runtime/topology, generated inputs, and dispatcher/backend identities, and reject unsafe header/response paths | Corrected with host regressions before first commit; clean real capture pending |
| `PORT008-PROV-P031` — product gate draft admitted incomplete command/lineage/path/role/registry/identity/linked-instruction comparison | Local pre-baseline Work 2.e evidence-gate defect; no upstream MOS/VDP counterpart exists | Revalidate raw captures, freeze complete normalized commands, bind role and unique registry lineage, require calendar-valid build IDs and independently terminated identities, prove exact objects/direct contribution/owned symbols/linked instructions, and state closure limits | Corrected with adversarial host regressions; null fingerprints keep the gate ineligible pending clean rehearsal |
| `PORT008-PROV-P032` — active P4 recorder assumed the SCons extra-script namespace defines Python `__file__` | Local Work 2.e PlatformIO integration defect; official VDP has no actual-step recorder or extra-script hook | Resolve the committed hook from SCons `PROJECT_DIR`, exercise active installation with `__file__` absent, and reject the stopped invocation as evidence | Corrected after the first real rehearsal stopped before evidence creation; new committed clean capture pending |
| `PORT008-PROV-P033` — generic recorder normalized a quoted exact nested root as its enclosing root | Local `mos-agondev` actual-step-recorder defect; official MOS has no recorder or Clang probe replay | Apply one global longest-root pass with conservative delimiters, reject longer-component prefix matches, and recapture both EMOS roles | Corrected in generic commit `6d4008c` after the gate rejected both successful unversioned builds; fresh captures pending |
| `PORT008-PROV-P034` — P4 TEMPFILE callable and response contract mismatched the real producer | Local P4 evidence-tool defect; official VDP has no recorder counterpart | Match the exact SCons callable and authenticate the PlatformIO/SCons `piomaxlen` response contract | Retained correction and forced-long-command regression; fresh capture pending |
| `PORT008-PROV-P035` — P4 spawn classification could delegate an ambiguous target action | Local P4 recorder defect; official VDP has no recorder counterpart | Fail closed on every ambiguous or unclassifiable possible target action | Retained correction; fresh capture pending |
| `PORT008-PROV-P036` — P4 claimed paths were not rebound to actual expanded argv | Local P4 gate defect; official VDP has no evidence gate | Bind source, output, ELF, and map claims to exact expanded-argv operands | Retained correction and adversarial regressions |
| `PORT008-PROV-P037` — rooted directories and malformed/missing rooted tokens were underclassified | Local evidence-gate defect; no official MOS/VDP counterpart | Distinguish files from directories and reject malformed or absent rooted operands | Retained correction and regressions |
| `PORT008-PROV-P038` — rooted spelling could substitute for canonical file identity | Local evidence-gate defect; no official MOS/VDP counterpart | Resolve canonical identities and reject hardlink alias or duplicate ambiguity | Retained correction and regressions |
| `PORT008-PROV-P039` — root/suffix/symlink containment admitted escape or retargeting cases | Local evidence-gate defect; no official MOS/VDP counterpart | Require absolute contained roots, safe suffixes, and stable physical identity | Retained correction and regressions |
| `PORT008-PROV-P040` — zds2gas evidence hashed raw rather than semantic source text | Local generic evidence-tool defect; official MOS has no recorder counterpart | Hash UTF-8 universal-newline text matching zds2gas semantics | Retained correction and regression |
| `PORT008-PROV-P041` — Python boolean values could satisfy integer evidence fields | Local Python/JSON gate defect; no official MOS/VDP counterpart | Require exact integer types throughout evidence validation | Partly corrected; P4 `ascii_occurrences` and runtime `version_info` remain open |
| `PORT008-PROV-P042` — EMOS linked comparison rejected valid rebasing and undercovered allocated contributions | Local Work 2.e comparator defect; official MOS has no comparator counterpart | Verify object-to-link bytes and `r_imm24` relocations across every allocated section before canonical comparison | Checkpointed provisional correction; fresh evidence pending |
| `PORT008-PROV-P043` — EMOS coordinator lacked a policy-owned composition dependency delta | Local Work 2.e policy defect; official MOS has no qualification comparison policy | Permit exactly qualification-only `${PREPARED}/src/emos_parallel.h` | Checkpointed provisional correction and regression; fresh evidence pending |
| `PORT008-PROV-P044` — literal reserved placeholders can collide with substituted roots | Local recorder/validator normalization defect; no official MOS/VDP counterpart | Reject or unambiguously encode literal placeholders before normalization | P4 raw-command rejection retained; generic `mos-agondev` recorder path remains open |

## Decision register

| Decision | Question | State | Downstream effect |
|---|---|---|---|
| REMED-002-D001 | Accept the audit classes, proposed owners, containment, and review order as the initial remediation register? | Accepted by the Author, 2026-09-01 12:57 EDT | Accepted rows are promoted into owner tasks; split rows retain the actor-specific owner division recorded above |
| REMED-002-D002 | Should upstream reports or contributions for F001--F003 extend UPSTREAM-001 or receive separate task authority? | Deferred until an Extender-specific trigger or separately prioritized upstream test exists | Determines future external contribution tracking; creates no present local-correction obligation |
| REMED-002-D003 | Should the exact PORT-008 prototype adapters be repaired only for bounded investigation or be replaced with production objects? | Accepted by the Author, 2026-09-01: replace; retain exact adapters only as evidence or last-resort diagnosis | PORT-008 now software-integrates the new epoch-preconditioned production data-plane objects and a separately identified fixed-backend qualification composition; no new physical run has occurred, and target-runtime, provenance, activation, return, artifact, and intended-circuit work remain separately gated |
| REMED-002-D004 | Should source-level upstream defects be corrected during present Extender work without evidence of a distinct Extender trigger? | Accepted by the Author, 2026-09-01 | No. Record them, defer correction and regression design, and reopen only if deterministic evidence meets PORT-003-D012 or the defect blocks a selected Extender function. Current priority remains forward-parallel transport. |

PORT-008-D003, accepted 2026-09-05, changes that immediate sequencing to staged
r02 circuit validation, beginning with relevant power/bias and UART subsets.
D004's inherited-defect threshold and D003's prototype-replacement decision
remain binding. This register does not duplicate the owner task's stage queue.

### REMED-002-D001 accepted decision

The Author accepted the register as the starting disposition on 2026-09-01:
treat F001--F016 as definite
defects or authority defects, F017--F021 as required preimplementation design
closures, and R001--R003 as prospective risks that must remain in their named
task designs. Retain the audit's proposed owners unless an owner task review
shows that a narrower split is needed.

F022 was discovered later during PORT-003 Work 2.a's adversarial source trace.
It is not retroactively covered by D001. D004 and PORT-003-D012 now record and
defer it; rejected D011 supplies no implementation authority.

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
- [x] **1.d** Reconcile the initial seven PORT-008 provenance entries with their
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

Gate 1's execution record applies to the original F001--F021 register. A later
stable audit extension receives an incremental Author disposition in its
owning design decision; it does not rewrite the historical D001 acceptance.

### Work 1 execution record

The Author accepted D001 on 2026-09-01 at 12:57 EDT. F001--F016 are accepted
as definite runtime, evidence, configuration, or authority defects;
F017--F021 are accepted as preimplementation design closures; and R001--R003
are retained as prospective risks in their named designs. Split rows now name
separate actor-specific actions rather than competing owners.

F022 postdates that review. The Author recorded and deferred it through D004
and PORT-003-D012 on 2026-09-01.

The promotion pass updated PORT-003 through PORT-008, QUAL-001, QUAL-002,
SETUP-005, SETUP-006, HW-001, REMED-001, DIAG-001, REMOTE-001, and LINK-001.
Each task links the stable audit finding and owns only its implementation,
consumer gate, policy, research, or qualification portion. The detailed
evidence and exact upstream/local provenance remain solely in the audit.

The initial seven PORT-008 provenance entries are reconciled in PORT-008: P001's
permanent EMOS correction remains qualification-gated; P002--P005 contribute
durable invariants without promoting the exact prototype adapters; P006 is
closed historical diagnostic provenance; and P007 records an upstream RST 18
documentation/source discrepancy without selecting a correction. Exact upstream identities and
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

- [x] **2.a disposition:** PORT-003 recorded the F001/F002/F022/H001 source
  analysis and the rejected comprehensive correction. D004/D012 defer local
  correction and isolating regression design until reproducible evidence shows
  a distinct Extender trigger or obstruction of a selected Extender function.
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

PORT-008's accepted D002 immediate execution chain now groups 2.e, 2.f, and
2.h with the new production P4/EMOS data-plane implementation, non-release
fixed-backend composition, and candidate-object evidence. Those owner-task
steps may complete without 2.g; production activation and the corrective-
action physical hold remain separately blocked.

The 2026-09-01 software-only implementation supplies replacement objects for
all three findings and now replaces the ordinary EMOS parallel route, but it
does not close these checklist items. A later adversarial pass superseded the
first P4 completion claim with P017 through P021. The corrected receiver keeps
one advertised, armed transaction through indefinite sender idle, starts its
finite record deadline only after active `VALID_N`, and polls cancellation in
bounded slices. It also has a
capacity-plus-one DMA sentinel, direction/READY release before abort, and
transactional reverse-order cleanup. The retained Stream preserves exactly one
already-advertised byte across a fault, and the nonblocking cancellation edge
totally orders record admission so a pre-fault winner is quarantined rather
than reported as post-fault success. The qualification owner retries teardown
before revoking its lease, and process-task creation failure returns before
boot/network publication. The ISR publishes the completed byte
count through a lock-free release/acquire generation edge rather than a
`volatile` handoff. Sanitizer host fault injection, source-contract checks, and
an ESP32-P4 compile/link pass succeed. Closure of 2.e and 2.f still requires
target-runtime evidence for stopped CLOCK, stuck VALID, GPIO release, partial
peripheral start, and retry;
2.h still requires confirmation that the inspected pinned ESP-IDF 5.5.5
callback/cancellation behavior matches the target at runtime. None of this
changes the separate activation hold in 2.g. EMOS ordinary-dispatcher routing
and whole-transition UART1 mux ownership are software-integrated under
PORT-008/INTEG-002. Their source-freeze commits and pre-freeze linked checks do
not substitute for the open target-runtime or provenance gates.

### Work 2.a design status

PORT-003's design-only pass is recorded in
[`PORT-003/concurrency/README.md`](PORT-003/concurrency/README.md).
The Author rejected `PORT-003-D011` on 2026-09-01 because its comprehensive
gate, retained-common seams, lifetime drains, mutation rewrites, and fixture
program would harden upstream behavior without evidence that selected Extender
functionality manifests those failures differently from regular VDP operation.

Accepted D004/`PORT-003-D012` retain exact source findings and provenance but
defer correction and regression-test design. Reopening requires deterministic
evidence that a project-owned Extender transport, scheduler, presentation
reader, or other selected function reproducibly activates the failure in a new
way, or that the defect prevents that selected function from working. A future
correction should prefer project-owned containment and requires a separate
decision before retained common code changes.

This completes the Work 2.a disposition without claiming the findings fixed.
F001, F002, F022, and H001 do not independently block current PORT-008 work to
establish forward transport over parallel GPIO. No regression fixture is being
designed now.

### PORT-008 production-equivalence disposition

The Author rejected `PORT-008-D001` and accepted `PORT-008-D002` on
2026-09-01. The receive-only Legacy listener and no-CTS bootstrap sender are not
production work. D002 resolves REMED-002-D003 in favor of replacing the exact
r01 adapters with new production forward-parallel objects. Its original r01
test schedule is superseded by PORT-008-D003: use those components where
applicable in the ordered r02 stages, with separately scoped diagnostic
callers. A supplied active epoch still proves no activation or formal mode.
Actual r02 measurements may support their exact circuit claims; historical
r01 evidence does not supply them. Authenticate stage candidates now and
compare eventual release consumption later under PORT-008 Work 2.g.

Work 2.e, 2.f, and 2.h therefore apply to the new production P4 ingress and
control boundary rather than a patch promotion of `ForwardParallelStream`.
Work 2.g remains open: the rejected D001 design does not solve production
activation or close its corrective action. `PORT008-PROV-P007` records the
newly observed official RST 18 documentation/source return-value mismatch; D004
and PORT-003-D012 defer correction and broad regression design, while PORT-008
must avoid changing de-facto behavior accidentally during factoring.

### Gate 2 — Runtime safety

Gate 2 applies to findings whose accepted disposition selects present local
correction. Recorded upstream observations deferred by D004/D012 do not block
forward-transport investigation unless new evidence meets the trigger
threshold. The corrective action continues to hold retired proactive-READY
retries and production activation claims. PORT-008-D003 permits preparation
of bounded r02 stages outside that defective behavior; their physical
execution requires stage-specific approval and does not close the corrective
action or release mode-dependent gates.

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
- [x] **3.e** HW-001 reconciled the r02 maintained schematic, frozen
  digest, generated projection, and applicability metadata before PORT-008 or
  QUAL-002 consumes that design. This closes only F008 artifact identity;
  construction, electrical, and qualification gates remain open.
  That dated closure does not resolve the later connectivity/profile digest
  discrepancy now recorded under HW-001 S3.
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

- [x] **4.a** SETUP-005 and REMED-001 must promote all accepted lifecycle,
  reset, discovery, recovery, and transition decisions into ADR-0014 and the
  normative architecture before downstream implementation consumes them.
- [ ] **4.b** REMOTE-001 and LINK-001 must separate remote product ownership
  from direct-link research; any accepted implementation must receive a
  separately approved owner task.
- [x] **4.c** QUAL-002 exposes REMED-001's active freeze and corrected
  four-mode prerequisites in its local state and gates; the freeze remains
  unreleased.
- [ ] **4.d** PORT-003 must define Gate G's scope, fixtures, stop conditions,
  prerequisites, and acceptance criteria before implementation begins.
- [ ] **4.e** SETUP-005 and REMED-001 must name the processor that restarts,
  the owner and storage of a surviving target request, the EMOS commit point,
  and Legacy fallback. Accepted implementation and qualification must then be
  assigned separately.
- [ ] **4.f** REMOTE-001/PORT-006 and EMOS must define input-session admission,
  provenance, source selection and revocation. The Author selected stock UART
  keyboard packets on 2026-09-08; preserve origin/authority in the admitted
  session and EMOS ingress, not a proprietary per-key UART envelope. Normal
  keyboard authority includes stock command-line/key effects. Structured agent
  requests remain separate. This policy/implementation work is still open.
- [ ] **4.g** DIAG-001 must define classification, redaction, authentication,
  retention, export, and erase policy before capturing or exporting memory.
- [ ] **4.h** HW-001, SETUP-006, PORT-007, and the hardware-object promotion
  owner must establish one current construction and board-resource authority
  with revision applicability.
- [ ] **4.i** PORT-005 and REMOTE-001 must retain R002 and R003 in their design
  fixtures and security gates without presenting either as a current defect.

### Work 4.a execution record

SETUP-005 and REMED-001 completed F009 on 2026-09-01 by promoting the complete
accepted D002 lifecycle contract into ADR-0014 and `docs/architecture.md`.
This closes only Work 4.a; it does not resolve F016/F018, release the REMED-001
freeze, authorize PORT-008 implementation, or pass Gate 4.

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
- [x] **5.d** Record completed corrections, retained risks, remaining external
  dependencies, released containments, and any deliberately unresolved owner
  gates in the current development log, including the final stale-work and
  repository-cleanup disposition.
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

## Firmware bug register cross-reference — 2026-09-20

[FWBUG-012](../firmware-bugs.md#fwbug-012). These stable bug identities supplement the original
finding IDs and evidence. Registration does not authorize repairs or turn
source-only findings into hardware reproductions. Use the same FWBUG ID for
any future dedicated disposal task; current dispositions remain in the register.
