# AUDIT-010 — Implementation integrity and resource-lifecycle audit

## Executive summary

**Accepted contract frozen by commit `8e300da5` on 2026-09-28.** Review the
Extender as an integrated product rather than another sequence of local fixes.
The first subtask researches documented and credibly reported failure patterns
of the exact GPT-6.0 and GPT-5.6 coding models, plus free/open-source tools that
can expose corresponding defects in a large mixed-language embedded codebase.
Only after that research is reviewed will the audit bind a source baseline,
map complete functions and resource ownership, run selected tools, perform the
manual review those tools cannot replace, pause for Author review, and implement
the accepted repairs without changing the audit baseline mid-review.

The immediate trigger is LCD-001's allocation-order result: mode20 and Nurples
render correctly when the P4 VDP allocates mode storage before game assets, but
the later mode20 request falls back to320×240 after those assets are loaded.
Allocating mode20 first coincided with a live P4 that answered ICMP while HTTP
connections reset. This reciprocal failure pattern makes the total P4 memory
and service lifecycle the first concrete audit case, not proof that LCD code is
the sole cause. No implementation, firmware build, flash, reset, SD mutation,
hardware run or production decision occurs before the audit findings review.

Created: 2026-09-28. Owning queue: `TODO.md`. Related implementation and
evidence owners: [LCD-001](LCD-001.md), [PORT-003](PORT-003.md),
[PORT-006](PORT-006.md), [AUDIT-006](AUDIT-006.md) and parked
[AUDIT-007](AUDIT-007.md).

## Purpose

Determine whether Extender's current behavior is supported by a coherent set of
functional contracts or has accumulated individually plausible additions whose
combined ownership, resource demand, error behavior and concurrency assumptions
are unsound. Identify source-backed defects and risks without attributing code
quality to a model merely from style or outcome. Model research informs review
checklists and controls; repository evidence determines findings.

The audit must answer these immutable review questions:

A10-Q01 [ ] Which processor, task, service or application owns every persistent and
   transition-time allocation, mutable state object, worker, queue and output
   buffer?

A10-Q02 [ ] Which functions must coexist, which are mutually exclusive, and what are
   their steady-state and peak internal-RAM, PSRAM, DMA-capable-memory, stack,
   socket and file-handle requirements?

A10-Q03 [ ] Are initialization, reconfiguration, failure rollback and teardown complete
   transactions, with truthful state visible to EMOS, applications, LCD,
   browser clients and diagnostics?

A10-Q04 [ ] Where have local feature additions duplicated responsibility, bypassed an
   architectural owner, retained maximum-size resources unnecessarily, or made
   one output/service impair another?

A10-Q05 [ ] Which defects can automated analysis demonstrate, which require manual
   contract tracing, and which remain hypotheses requiring bounded tests?

## Scope

Cover the complete project-owned multi-repository product closure: maintained
P4 firmware, host tools, active fixtures and build/package configuration in this
repository; Extender MOS (EMOS), `sdserve`, `sdjob` and owned support code in
`../agon-emos`; and project-owned MOS build integration in `../mos-agondev` where
it affects the resulting EMOS image. Record each repository's exact baseline and
keep findings and fixes in the owning repository.

Read official Agon documentation and selected upstream source before judging
MOS/VDP semantics. Official `../../agon-docs`, `../../agon-mos` and
`../../agon-vdp` checkouts remain read-only reference baselines, not audit
targets. Bind generated production identities separately from the development
sources under audit; neither a repository's Git HEAD nor the installed
diagnostic is production by assumption.

The source review has these immutable coverage items:

A10-S01 [ ] VDP mode selection, native controller replacement, allocation/fallback,
   graphics-context reset and published mode state.

A10-S02 [ ] Native drawing storage, retained buffers/assets, immutable snapshot slots,
   LCD composition and DSI scanout, PPA resources, browser encoding scratch and
   HTTP connection/task resources.

A10-S03 [ ] Renderer, snapshot, LCD, browser, UART, keyboard, storage and diagnostic task
   ownership; locks, suspension, queues, callbacks and teardown ordering.

A10-S04 [ ] Error propagation, rollback, degraded operation and observability across the
   eZ80/P4 UART boundary and each P4 service boundary.

A10-S05 [ ] Build-time feature combinations, compile-time branches, dead/stubbed paths,
   duplicated facilities, exceptional workarounds and missing integration tests.

A10-S06 [ ] Host Python tools and fixture builders where unsafe assumptions, weak receipt
   handling or test-only transformations could misstate target behavior.

Do not reopen accepted product decisions merely because alternatives exist.
Do not duplicate AUDIT-007's parked exhaustive upstream-FabGL inventory: consume
its retained findings and examine active integration contracts here. Promote a
new upstream-completeness question back to AUDIT-007 only if this audit finds a
specific uncovered dependency.

For bundled third-party source under `vdp/vendor`, exhaustively audit the parts
the project controls: local modifications, selected files and build branches,
configuration, wrappers, adapters, active interfaces, licenses/provenance and
assumptions made by project code. Do not perform another line-by-line audit of
untouched third-party internals. Follow an untouched internal implementation
only when an active call path, retained finding or demonstrated behavior makes
it material; record any newly uncovered exhaustive-upstream question for the
parked AUDIT-007 owner rather than silently expanding this scope.

Git history and superseded implementations are outside exhaustive coverage.
A bounded historical review is permitted only when one of these immutable
triggers applies. Before inspecting history, the auditor must pause and present
the trigger, exact question, proposed commits or date range and stopping
condition for Author acceptance. A plausible trigger is not authorization to
begin historical review. The resulting accepted review record must preserve
that approved scope and its conclusion:

A10-H01 — Current source, documentation and accepted architecture disagree, and
the relevant decision rationale cannot be resolved from current authorities.

A10-H02 — A demonstrated regression needs a bounded introduction point or a
known-good comparison to distinguish the responsible change.

A10-H03 — Current code contains an unexplained workaround, copied block, magic
constant or exceptional lifecycle whose removal condition or original contract
is absent from current documentation.

A10-H04 — Production or installed behavior comes from an older pinned commit
and differs materially from the maintained source being audited.

A10-H05 — License, attribution, security provenance or third-party source
identity cannot be established from the current tree and retained manifests.

A10-H06 — A persistent on-disk, wire or firmware format requires compatibility
with bytes produced by a prior implementation, and current tests/specification
do not establish that compatibility.

A10-H07 — Frozen evidence makes a material claim that conflicts with a current
finding, and reviewing the exact producing change is necessary to reconcile
the evidence rather than merely note its older scope.

Absent one of A10-H01 through A10-H07, the auditor must not inspect history to
search broadly for additional defects, reconstruct superseded designs, infer AI
authorship or enlarge current-source coverage.

## Work contract

### A10-01 [x] Model-risk and analysis-tool research

The Author reviewed the research and accepted A10-SET01 through A10-SET07 on
2026-09-28. BUILD-001's bounded host smoke provisioned LLVM 23.1.2 and Cppcheck
2.22.0 in ignored project state and validated a selected native compilation
action. Full source-wide execution remains A10-04 work after the native build
baseline is accepted; smoke findings do not authorize an early fix.

Research comes first and produces
[AI-RISK-AND-TOOLS.md](AUDIT-010/AI-RISK-AND-TOOLS.md), an ancillary document owned directly
by A10-01. Use current official OpenAI documentation for supported facts about the
exact GPT-6.0 and GPT-5.6 models. If either label is not publicly documented,
record that limit rather than substituting a different model. Clearly separate
official facts, reproducible evaluations, peer-reviewed or maintainer evidence,
and subjective community reports.

The research has these immutable subitems:

A10-01a [x] Identify failure modes relevant to long-lived, large-context software work:
   incomplete dependency tracing, locally correct/global inconsistent changes,
   instruction drift, fabricated API assumptions, weak error paths, concurrency
   and lifetime mistakes, test overfitting, false completion claims, and review
   bias toward generated code.

A10-01b [x] Determine what evidence exists for differences between GPT-6.0 and GPT-5.6,
   without converting popularity or anecdotes into measured comparative claims.

A10-01c [x] Survey external tools that are genuinely free and open source and applicable
   to this repository's C/C++, Python, assembly, build files and embedded ESP-IDF
   environment. Record license, maintained source, supported languages, analysis
   class, compilation-database needs, likely signal, expected false positives,
   resource cost and whether target execution is required.

A10-01d [x] Include candidates for compiler diagnostics/sanitizers where host execution
   is meaningful, static analysis, semantic queries, dependency/architecture
   checks, duplicate/dead-code detection, Python analysis, security scanning and
   repository policy enforcement. Do not recommend an AI-branded scanner merely
   because this audit was prompted by AI-generated code.

A10-01e [x] Map every recommended check to a concrete Extender risk and state what the
   tool cannot establish. Recommend the smallest justified tool set for A10-04;
   installation or execution waits for Author review of the research result.

Every web-derived statement in the ancillary document must link its source near
the claim. Prefer primary project documentation, source repositories, published
papers and official vulnerability databases. Preserve source dates and exact
tool versions available at research time. Do not submit source, firmware or
private bench data to hosted scanners or proprietary analysis services.

### A10-P01 [ ] Consolidate the development baseline under LCD-001

Complete this prerequisite after A10-01 review and before A10-02 freezes the
source-audit baseline. LCD-001 owns the source/build work: retain the working
current ExCom implementation and accepted LCD initialization, colour, timing,
320×240 scaling and centered512×384 mapping; remove the failed r72 whole-frame-
lock diagnostic; and leave the demonstrated late-mode20 allocation-order/HTTP
resource failure unfixed as audit evidence. Build and identify one combined
development configuration and perform only the bounded checks needed to show
that the intended baseline was assembled. Do not call this production, complete
LCD qualification or remediation of an AUDIT-010 finding.

### A10-02 [ ] Freeze the review baseline and coverage ledger

After A10-01 review, record exact Extender, component-owner, official-reference,
tool and production/installed identities. Inventory active source, generated
code, build branches and services before drawing conclusions. Create a coverage
ledger under `docs/tasks/AUDIT-010/` with stable area and finding identifiers.
Each row names the actor, files/symbols, function, state/resources, callers,
consumers, prior evidence, automated checks, manual checks and disposition.
The A10-P01 consolidated ExCom+LCD development configuration is the sole
exhaustive audit target. Use selected production v0.1.0 only as a bounded
comparison for regressions, ownership changes and resource growth; do not run a
second exhaustive audit of its superseded source closure.

### A10-03 [ ] Functional and resource architecture

Trace representative operations end to end and produce actor-explicit maps for
boot, mode change, ordinary drawing/presentation, browser connection, LCD-only
operation, simultaneous LCD/browser operation, storage transfer, input and
shutdown/recovery. For each transition record allocation order, capability,
size, lifetime, largest-contiguous-block requirement, failure return, rollback,
published state and consumer-visible consequence. Calculate budgets from source
and configuration, then distinguish those calculations from target measurements.

Use the two Nurples allocation orders as the first worked comparison. Explain
why late mode20 falls back while early mode20 renders and why HTTP resets only
in the observed early-mode20 case. Treat total exhaustion, fragmentation,
capability-specific heaps, leaked/retained resources and connection-task failure
as alternatives until evidence discriminates them.

Targeted diagnostic code changes are permitted when a discrete source question
cannot be resolved statically. Before each change, record the exact symbols and
behavior touched, observation added, expected perturbation, removal condition
and regression cases protecting previously passed behavior. Diagnostic code
must not contain a proposed fix or silently replace the baseline under review.
Every diagnostic build and hardware run still requires its own bounded procedure
and explicit Author authorization.

### A10-04 [ ] Automated analysis

Run only the A10-01 tool set accepted by the Author. Pin tool identities and exact
commands; prefer existing project environments, package-manager isolation or
reproducible containers without modifying global developer state. Generate or
validate compilation databases deliberately for the real selected ESP-IDF build.
Retain raw machine-readable results in the task silo and triage every reported
item as confirmed, false positive, accepted exception or unresolved. A clean
tool run is not evidence that architecture, concurrency or target memory use is
correct.

### A10-05 [ ] Manual integration review

Review every coverage-ledger area using A10-01's risk checklist and A10-03's maps.
Trace ownership and failure behavior across files and tasks rather than limiting
review to changed lines. Compare implementation with current architecture,
official contracts and accepted decisions. Look specifically for incremental
features that reserve resources globally, silently fall back, leave stale
published state, conflate logical completion with physical presentation, or
make unrelated services depend on allocation order.

### A10-06 [ ] Findings and independent validation proposals

Publish stable findings with severity, confidence, exact evidence, affected
actors, user-visible consequence, scope, proposed owner and removal/acceptance
condition. Separate demonstrated defects, source-proven contract violations,
tool warnings and hypotheses. Propose the smallest discriminating host or bench
validation for unresolved high-impact findings. A10-06 is complete only when
the complete audit coverage and findings set are ready for review; partial
findings do not advance independently to review or repair. This audit stage does
not itself authorize firmware changes or physical tests.

### A10-07 [ ] Author findings review and repair authorization

Present the coverage ledger, architecture/resource maps, automated-analysis
triage and findings for Author review. Record an explicit disposition for every
finding and coverage row. Freeze that reviewed audit result before changing
executable product code. The Author selects which fixes proceed only after the
complete audit has been reviewed; unaccepted and unresolved findings remain
visible. A10-07 produces one bounded, complete, itemized repair plan containing
the accepted findings, dependencies, order and validation requirements. The
Author approves that plan as a whole before A10-08 begins. Partial findings do
not authorize early implementation.

### A10-08 [ ] Implement accepted fixes

Implement accepted findings one at a time, in the order approved in A10-07.
Give each fix its own itemized implementation record, commit and validation;
do not combine unrelated corrections merely because the audit found them
together. Preserve finding IDs and link every source change to its accepted
finding, owner, expected behavior and removal/acceptance condition. Update
architecture/ADR, bug register and maintained guidance where an accepted
correction changes those authorities. Use source-contract and host validation
during implementation, but do not claim physical behavior from compilation or
static analysis.

### A10-09 [ ] Validate, review and close out repairs

Prepare bounded qualification for the changed functions, including hardware
work only after its explicit procedure and authorization. Present results and
remaining findings for Author review. Promote accepted production behavior under
the existing packaging/version/tag policy. Do not close AUDIT-010 because one
visible defect was fixed; closure requires a disposition for every coverage row
and finding, and accepted repairs must have their required validation or an
explicitly retained owner and limit.

## Unattended test execution contract

Reusable AUDIT-010 diagnostic and repair suites must not require an agent to
spend tokens polling ordinary progress. This is a functional requirement for
new or refreshed suites, not permission to retrofit frozen evidence silently.

A10-T01 [ ] The suite records durable start, phase, case, pass/fail/error and end
state with monotonic duration and UTC timestamps. A host interruption must leave
the last durable state distinguishable from completion.

A10-T02 [ ] The mainboard VDP shows concise human-readable phase and case status
where doing so does not invalidate the test. A procedure that cannot display
progress must say why and provide another durable progress channel; it must not
pretend an invisible run is visually observable.

A10-T03 [ ] The host controller starts the bounded run and then operates without
agent polling. It uses event/completion records rather than repeated conversational
status checks, fixed sleeps or inferred deadlines.

A10-T04 [ ] On ordinary completion or a detected terminal failure, the automated
controller restores or selects Legacy when the mainboard remains controllable,
establishes a usable mainboard prompt, preserves the final status display and
invokes the project's existing accepted audible-notification system without agent
monitoring. On hardware this uses the established `/extender/attention.txt` spoken
cue; emulator runs use the already established emulator notification path. Record
the cue execution receipt separately from whether the Author heard it. Do not
design or substitute a new notification mechanism under this audit.

A10-T05 [ ] Success, test failure, infrastructure failure and timeout are distinct
terminal records. A failure does not silently reset either board, discard partial
evidence, continue dependent cases or announce success. Each suite specifies how
its controller reaches Legacy and invokes the audible cue after a detected failure;
any reset or other recovery needed to do so must be separately pre-authorized.

A10-T06 [ ] The suite records preparation, fixture runtime, retrieval and
notification durations separately and uses retained comparable runs for future
estimates. An estimate is not an automatic reset or collection deadline.

A10-T07 [ ] Each diagnostic or repair code change declares a regression manifest
covering the previously passed functions it might affect. Run those protections
before accepting the new observation or fix; a new targeted pass cannot silently
supersede an older broader pass.

A10-T08 [ ] Browser video, keyboard capture, SD services and other consumers are
connected only when the case requires them. Record simultaneous-service cases
separately from isolated baselines so monitoring does not change the workload
being measured.

A10-T09 [ ] When a detected failure leaves the mainboard controllable, the runner
prints a concise failure identity and disposition on the Legacy screen and leaves
that text visible after the audible cue. The alert player, foreground SD service
and runner cleanup must not overwrite or obscure the failure display; if the
failure prevents any Legacy display, the durable terminal record states that
explicitly.

## Findings standard

Use IDs `AUDIT-010-F001` onward. Each finding uses these immutable fields:

A10-FIELD01 — Concise statement and severity.

A10-FIELD02 — Affected actor, source identity, files and symbols.

A10-FIELD03 — Violated or missing contract.

A10-FIELD04 — Direct evidence and counter-evidence.

A10-FIELD05 — Runtime/user consequence and affected configurations.

A10-FIELD06 — Confidence and unresolved alternatives.

A10-FIELD07 — Proposed owner, validation and disposition.

Never label code defective solely because an AI model may have produced it.
Never infer which model authored a change unless retained provenance establishes
that fact. Similarity to a published model failure pattern is a review lead, not
finding evidence.

## Validation and safety boundaries

A10-B01 — Contract drafting and A10-01 research are read-only with respect to firmware,
   hardware, SD cards, network services and component-owner repositories.

A10-B02 — Source scanners must operate locally on non-secret project material. Review
   licenses, installation scripts, network behavior and data handling before use.

A10-B03 — A scanner may write only ignored caches or task-owned output until its result
   format is reviewed. Do not mass-format or automatically rewrite source.

A10-B04 — No generated patch is accepted without source-contract review and relevant
   tests. Tool output and model review never replace human acceptance.

A10-B05 — Hardware diagnostics require a later explicit procedure and authorization.
   Do not reset or flash merely because a source finding predicts a failure.

A10-B06 — Targeted diagnostic source changes must remain observational, removable
and bounded to a discrete question. Preserve the audited baseline identity and
run the declared regression manifest before relying on their evidence.

## Draft decisions for Author review

AUDIT-010-D001 [x] **Accepted, 2026-09-28:** audit the integrated maintained
product first, using prior exhaustive audits as inputs rather than restarting
their inventories. The Author selected the broader product view because the
observed LCD/Nurples allocation order also affected HTTP availability and may
cross video, network and shared-service ownership boundaries.

AUDIT-010-D002 [x] **Accepted, 2026-09-28:** make model-risk/tool research
A10-01 a mandatory gate. The Author reviews its findings and recommended
minimal tool set before the agent installs or runs a new scanner or begins
source-wide findings work.

AUDIT-010-D003 [x] **Accepted, 2026-09-28:** execute the task in three ordered
stages: audit, Author review, then fix. Freeze reviewed findings before changing
executable product code. The audit and its review must both be complete before
any repair begins. A10-06 delivers the complete audit; A10-07 reviews it and
approves one bounded, complete, itemized repair plan; A10-08 then executes each
accepted fix individually with its own commit and validation. No partial finding
authorizes early implementation.

AUDIT-010-D004 [x] **Accepted, 2026-09-28:** exhaustively audit the current
maintained implementation and selected build closure. Exclude Git history and
superseded implementations unless one of A10-H01 through A10-H07 establishes a
bounded, recorded need and the Author accepts the proposed question, historical
range and stopping condition before inspection begins.

AUDIT-010-D005 [x] **Accepted, 2026-09-28:** audit the complete project-owned
multi-repository product closure across this repository, `../agon-emos` and the
applicable project-owned integration in `../mos-agondev`. Keep findings and
fixes with their owning repositories. Treat official Agon documentation, MOS
and VDP checkouts as read-only references rather than audit targets.

AUDIT-010-D006 [x] **Accepted, 2026-09-28:** apply an integration-focused audit
to bundled third-party source. Cover every project modification, selection,
configuration, wrapper, active interface and evidenced dependency, but do not
duplicate AUDIT-007 with a line-by-line review of untouched vendor internals.

AUDIT-010-D007 [x] **Accepted, 2026-09-28:** consolidate current development
ExCom and the substantially complete LCD implementation before A10-02 freezes
the audited baseline. Remove the failed r72 whole-frame-lock diagnostic, retain
accepted LCD behavior, and deliberately preserve the demonstrated allocation-
order/resource defect for audit. A10-P01 is a one-time baseline-preparation
exception to the audit-before-fix sequence, not authorization for opportunistic
remediation or production promotion.

AUDIT-010-D008 [x] **Accepted, 2026-09-28:** make the A10-P01 consolidated
ExCom+LCD development configuration the sole exhaustive audit target. Use
selected production v0.1.0 as a bounded comparison baseline for regressions,
ownership changes and resource growth, not as a second exhaustive target.

AUDIT-010-D009 [x] **Accepted, 2026-09-28:** permit targeted diagnostic-only
code changes for discrete unresolved questions. Each change requires a bounded
plan, explicit authorization, declared perturbation/removal condition and a
regression manifest protecting previously passed behavior. Diagnostics may
observe but must not contain an unreviewed fix.

AUDIT-010-D010 [x] **Accepted, 2026-09-28:** new or refreshed suites run
unattended after launch, retain durable progress/results, show mainboard status
where the test permits, and invoke the established audible-notification system in
Legacy after ordinary completion or a detected terminal failure. The automated
runner owns this action without agent monitoring. Reuse the existing hardware and
emulator paths; notification integration does not authorize a replacement alert
mechanism. A reset or other recovery needed to make a failure audible still
requires explicit advance authorization in that suite's contract. When the
mainboard remains controllable, the runner must also leave the failure identity
visible on the Legacy screen without notification output overwriting it.

## Contract review gate

A10-G01 [x] The Author reviews this draft, corrects its scope and accepts or
revises AUDIT-010-D001 through D010.

A10-G02 [x] The agent commits the accepted contract as its own frozen checkpoint.

A10-G03 [x] A10-01 began only after A10-G02. Its findings receive this later
commit and review; they must not be backfilled into the already frozen contract
as though known at its creation.
