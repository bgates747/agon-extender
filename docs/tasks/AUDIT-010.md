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

The immediate trigger is LCD-001's allocation-order result, but the Author has
now selected the last working pre-LCD product as the audit baseline. The LCD
experiment demonstrated that mode20 allocation order can affect both rendering
and HTTP availability; it is retained as a post-audit integration regression,
not folded into the source closure being audited. Complete the pre-LCD audit,
review and itemized fixes first. Only afterward may LCD-001 redeploy LCD support
as a separately reviewed delta. No implementation, firmware build, flash,
reset, SD mutation, hardware run or production decision occurs before the
applicable review gate.

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

A10-Q01 [x] Which processor, task, service or application owns every persistent and
   transition-time allocation, mutable state object, worker, queue and output
   buffer?

A10-Q02 [x] Which functions must coexist, which are mutually exclusive, and what are
   their steady-state and peak internal-RAM, PSRAM, DMA-capable-memory, stack,
   socket and file-handle requirements?

A10-Q03 [x] Are initialization, reconfiguration, failure rollback and teardown complete
   transactions, with truthful state visible to EMOS, applications, browser
   clients and diagnostics? Apply the same question to LCD during its later
   integration-delta review.

A10-Q04 [x] Where have local feature additions duplicated responsibility, bypassed an
   architectural owner, retained maximum-size resources unnecessarily, or made
   one output/service impair another?

A10-Q05 [x] Which defects can automated analysis demonstrate, which require manual
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

A10-S01 [x] VDP mode selection, native controller replacement, allocation/fallback,
   graphics-context reset and published mode state.

A10-S02 [x] Native drawing storage, retained buffers/assets, snapshot ownership,
   browser encoding scratch and HTTP connection/task resources in the pre-LCD
   baseline. LCD composition, DSI scanout and PPA additions are excluded from
   exhaustive baseline review and become a post-audit integration delta.

A10-S03 [x] Renderer, snapshot, browser, UART, keyboard, storage and diagnostic
   task ownership in the pre-LCD baseline; locks, suspension, queues, callbacks
   and teardown ordering. LCD task ownership is reviewed with the later delta.

A10-S04 [x] Error propagation, rollback, degraded operation and observability across the
   eZ80/P4 UART boundary and each P4 service boundary.

A10-S05 [x] Build-time feature combinations, compile-time branches, dead/stubbed paths,
   duplicated facilities, exceptional workarounds and missing integration tests.

A10-S06 [x] Host Python tools and fixture builders where unsafe assumptions, weak receipt
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

The Author clarified the source-lineage and duplication boundary on 2026-09-29.
Treat unchanged upstream code, closely ported/adapted upstream code and
project-new feature/capability code as three separate review and repair classes.
Do not attribute an inherited defect to a new Extender feature, or hide a
port-introduced defect inside an upstream finding. Before accepting a
project-new implementation or repair, establish whether the selected official
or bundled upstream already supplies the function. Also search project-owned
code for a second function or service with materially equivalent behavior and
ownership. Prefer reuse or consolidation; retain two implementations only with
an explicit difference in contract, actor, lifecycle or target.

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

### A10-P01 [x] Consolidate the development baseline under LCD-001 — superseded

Complete this prerequisite after A10-01 review and before A10-02 freezes the
source-audit baseline. LCD-001 owns the source/build work: retain the working
current ExCom implementation and accepted LCD initialization, colour, timing,
320×240 scaling and centered512×384 mapping; remove the failed r72 whole-frame-
lock diagnostic; and leave the demonstrated late-mode20 allocation-order/HTTP
resource failure unfixed as audit evidence. Build and identify one combined
development configuration and perform only the bounded checks needed to show
that the intended baseline was assembled. Do not call this production, complete
LCD qualification or remediation of an AUDIT-010 finding.

The Author superseded this unexecuted prerequisite on 2026-09-28. It is retained
verbatim as the frozen contract's earlier direction; no combined ExCom+LCD
baseline is to be assembled for AUDIT-010.

### A10-P02 [x] Establish the last working pre-LCD baseline

Before A10-02, BUILD-001 must reproduce the last retained working P4 product
before LCD integration: Extender source
`6c6bea3beb2f8abc89c5b1f40a0e7dd0890a084d`, hardware-tested build
`uart-excom-console-r61-b2026-09-28-03-12-48Z`, paired with the current accepted
development EMOS v0.1.23 source
`21a9ba27f1f346473d767c2c3053ee18e8911335`. Verify the retained identities and
functional evidence, express that P4 closure through the native ESP-IDF/CMake
authority, and complete host and bounded hardware equivalence before freezing
the audit baseline. This is the accepted A10-H02/A10-H04 bounded historical
review: inspect only the named retained source/build and the minimum current
build-infrastructure delta required to reproduce it; stop once identity,
closure and equivalence are established.

BUILD-001 completed this prerequisite on 2026-09-29. The immutable identities,
artifact hashes, actual linked graph and accepted analysis entry points are in
[BASELINE.md](AUDIT-010/BASELINE.md). The selected production bundle remains a
separate unchanged comparison.

### A10-02 [x] Freeze the review baseline and coverage ledger

After A10-01 review, record exact Extender, component-owner, official-reference,
tool and production/installed identities. Inventory active source, generated
code, build branches and services before drawing conclusions. Create a coverage
ledger under `docs/tasks/AUDIT-010/` with stable area and finding identifiers.
Each row names the actor, files/symbols, function, state/resources, callers,
consumers, prior evidence, automated checks, manual checks and disposition.
The A10-P02 native pre-LCD development configuration is the sole exhaustive
audit target. Use selected production v0.1.0 and retained later pre-LCD hardware
evidence only as bounded comparisons for regressions, ownership changes and
resource growth; do not run a second exhaustive audit of either superseded
source closure. Preserve the experimental LCD implementation outside this
baseline for the post-audit redeployment delta.

The frozen repository, build, artifact, production, installed/reference and
analysis-tool records are in [IDENTITIES.md](AUDIT-010/IDENTITIES.md). The
complete area/source/service/generated-state/test map is in
[COVERAGE-LEDGER.md](AUDIT-010/COVERAGE-LEDGER.md). A10-02 opened no findings
and changed no executable product source. The ledger is now at the Author
review boundary; do not begin A10-03 until that review is complete.

### A10-03 [x] Functional and resource architecture

Trace representative pre-LCD operations end to end and produce actor-explicit
maps for boot, mode change, ordinary drawing/presentation, browser connection,
storage transfer, input and shutdown/recovery. For each transition record
allocation order, capability, size, lifetime, largest-contiguous-block
requirement, failure return, rollback, published state and consumer-visible
consequence. Calculate budgets from source and configuration, then distinguish
those calculations from target measurements.

Use ordinary pre-LCD mode allocation and browser coexistence as the first worked
resource comparison. Retain the two LCD/Nurples allocation orders as a required
post-audit redeployment regression: the audit may identify baseline ownership
or lifetime risks relevant to it, but it must not import LCD code into the
frozen source closure or claim to explain that later failure without evidence.

Targeted diagnostic code changes are permitted when a discrete source question
cannot be resolved statically. Before each change, record the exact symbols and
behavior touched, observation added, expected perturbation, removal condition
and regression cases protecting previously passed behavior. Diagnostic code
must not contain a proposed fix or silently replace the baseline under review.
Every diagnostic build and hardware run still requires its own bounded procedure
and explicit Author authorization.

The Author accepted A10-02 on 2026-09-29. The completed static trace and
source-derived budgets are in
[ARCHITECTURE-RESOURCES.md](AUDIT-010/ARCHITECTURE-RESOURCES.md). It records the
seven required operation maps, fifteen resource rows, coexistence matrix,
worked mode-8/mode-20/browser comparison, five A10-05 review inputs and four
explicit measurement unknowns. It made no executable change, target
measurement or repair finding. Stop for Author review before A10-04 execution.

### A10-04 [x] Automated analysis

Run only the A10-01 tool set accepted by the Author. Pin tool identities and exact
commands; prefer existing project environments, package-manager isolation or
reproducible containers without modifying global developer state. Generate or
validate compilation databases deliberately for the real selected ESP-IDF build.
Retain raw machine-readable results in the task silo and triage every reported
item as confirmed, false positive, accepted exception or unresolved. A clean
tool run is not evidence that architecture, concurrency or target memory use is
correct.

Completed on 2026-09-29. [AUTOMATED-ANALYSIS.md](AUDIT-010/AUTOMATED-ANALYSIS.md)
records exact identities, commands/scopes, canaries, parse coverage, grouped
triage and eleven stable A10-05 candidates. The three reviewed local rules are
frozen in [A10-04-SEMGREP.yml](AUDIT-010/A10-04-SEMGREP.yml), and
[A10-04-EVIDENCE.json](AUDIT-010/A10-04-EVIDENCE.json) hash-binds the local raw
receipts and input manifests. Raw outputs remain
in the ignored local task silo because they contain machine-local paths. No
candidate is yet a confirmed finding or authorization to repair. Proceed to
the complete A10-05 review before findings assembly.

### A10-05 [x] Manual integration review

Review every coverage-ledger area using A10-01's risk checklist and A10-03's maps.
Trace ownership and failure behavior across files and tasks rather than limiting
review to changed lines. Compare implementation with current architecture,
official contracts and accepted decisions. Look specifically for incremental
features that reserve resources globally, silently fall back, leave stale
published state, conflate logical completion with physical presentation, or
make unrelated services depend on allocation order.

Completed on 2026-09-29. [MANUAL-REVIEW.md](AUDIT-010/MANUAL-REVIEW.md)
records the complete disposition of all 35 coverage rows and all eleven A10-04
candidates. It carries eleven manual-review conclusions plus the applicable
existing firmware-bug identities into A10-06. No history, executable source,
build, target or hardware operation was used, and no conclusion authorizes a
repair or physical diagnostic. Proceed through the later Author clarification
in A10-05a before findings assembly under A10-06 and the Author review gate.

### A10-05a [x] Source lineage and functional-duplication reconciliation

Added by Author clarification on 2026-09-29 after the initial A10-05 manual
pass. Complete this bounded reconciliation before A10-06 assigns final finding
IDs. It supplements rather than discards the A10-05 conclusions and does not
authorize implementation changes.

A10-05a01 [x] Classify every retained A10-MR conclusion and every applicable existing
   FWBUG input as `upstream-unchanged`, `upstream-ported/adapted`, or
   `project-new`. Record the exact source/reference boundary and the actor that
   owns any eventual repair.

A10-05a02 [x] For every closely ported/adapted function, compare the selected local
   implementation with the applicable upstream implementation and distinguish
   inherited behavior from port-introduced behavior. Handle the two origins as
   separate findings or repair items when their owners or remedies differ.

A10-05a03 [x] For every project-new function or capability implicated by a conclusion,
   search the selected official VDP/MOS source and bundled upstream/component
   interfaces for an existing implementation before proposing new code. Record
   reuse, adaptation or the exact missing contract that justifies a new owner.
   This is a current-source comparison, not permission to inspect history.

A10-05a04 [x] Search the project-owned P4, EMOS, host-tool and active-fixture closure
   for materially equivalent functions, services, state machines and resource
   owners. Distinguish intentional target-specific adapters from functional
   duplicates. Record the canonical owner and consolidation/removal condition
   for every duplicate candidate.

A10-05a05 [x] Publish the complete classification and comparison evidence in
   `AUDIT-010/LINEAGE-AND-DUPLICATION.md`. Every retained A10-06 finding and
   every proposed repair must reference its lineage result; unresolved
   equivalence becomes an explicit finding/validation question rather than an
   assumed reason to rewrite code.

Completed on 2026-09-29. The current-source comparison is recorded in
[LINEAGE-AND-DUPLICATION.md](AUDIT-010/LINEAGE-AND-DUPLICATION.md). It classifies
all eleven A10-MR conclusions and all seven applicable FWBUG inputs, separates
inherited behavior from P4 adaptations, checks every project-new conclusion
against selected upstream facilities, and records thirteen duplicate/parallel
implementation candidates with canonical owners or explicit dispositions. No
history, executable change, build, target or hardware operation was used.

### A10-06 [x] Findings and independent validation proposals

Publish stable findings with severity, confidence, exact evidence, affected
actors, user-visible consequence, scope, proposed owner and removal/acceptance
condition. Separate demonstrated defects, source-proven contract violations,
tool warnings and hypotheses. Propose the smallest discriminating host or bench
validation for unresolved high-impact findings. A10-06 is complete only when
the complete audit coverage and findings set are ready for review; partial
findings do not advance independently to review or repair. This audit stage does
not itself authorize firmware changes or physical tests. A10-06 begins only
after A10-05a is complete. It must keep upstream-unchanged,
upstream-ported/adapted and project-new findings separate, and must not propose
a new implementation until the upstream-equivalent and project-duplicate
checks are recorded.

Completed on 2026-09-29. [FINDINGS.md](AUDIT-010/FINDINGS.md) records fourteen
new stable findings, carries seven existing FWBUG identities without aliases,
ranks evidence and severity, supplies all nine required finding fields, and
defines thirteen smallest-discriminating validation proposals. The final
thirty-five-row disposition is linked from
[COVERAGE-LEDGER.md](AUDIT-010/COVERAGE-LEDGER.md). Five explicit limits prevent
tool gaps, deferred LCD work or unrelated historical evidence from being
reported as clean coverage. No executable source, build, target or hardware
state changed. Proceed to the complete A10-07 Author review; no finding yet
authorizes implementation or physical testing.

### A10-07 [x] Author findings review and repair authorization

Present the coverage ledger, architecture/resource maps, automated-analysis
triage and findings for Author review. Record an explicit disposition for every
finding and coverage row. Freeze that reviewed audit result before changing
executable product code. The Author selects which fixes proceed only after the
complete audit has been reviewed; unaccepted and unresolved findings remain
visible. A10-07 produces one bounded, complete, itemized repair plan containing
the accepted findings, dependencies, order and validation requirements. The
Author approves that plan as a whole before A10-08 begins. Partial findings do
not authorize early implementation.

The Author reviewed and approved the complete A10-06 findings and the complete
itemized A10-07 plan on 2026-09-29, including one-at-a-time implementation,
validation and acceptance pauses. [REPAIR-PLAN.md](AUDIT-010/REPAIR-PLAN.md)
records every coverage/finding disposition and the frozen dependency order.
The dedicated A10-07 documentation freeze precedes all executable repair work;
the Author authorized `A10-RP01` as the first A10-08 item.

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

The Author accepted RP01's minimal profile and host/build evidence, RP02's
sole-display-owner boundary and RP03's mutable-font repair on 2026-09-29; see
[RP01-PROFILE.md](AUDIT-010/RP01-PROFILE.md) and
[RP02-DISPLAY-OWNER.md](AUDIT-010/RP02-DISPLAY-OWNER.md), and
[RP03-MUTABLE-FONTS.md](AUDIT-010/RP03-MUTABLE-FONTS.md). The Author explicitly
deferred causal investigation of the newly passing Nurples mode switch until
the entire audit/repair sequence is complete. The Author accepted RP04 on
2026-09-30 after its [raw-SD dispatch candidate](AUDIT-010/RP04-RAW-SD-WRITE.md)
passed source, linked-image, emulator, full-ROM installation, the canonical
17-check paired hardware suite, and a manual Nurples ExCom run at 25–29 fps.
The Author accepted RP05 on 2026-09-30 after its checked-allocation candidate
passed clean-commit source qualification, exact-commit paired hardware
qualification and manual loaded-asset Nurples validation. RP06 is now the next
authorized repair item.

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

A10-T10 [ ] Before a physical case replaces `/autoexec.txt`, the runner retains
the exact prior bytes. Every successful terminal path restores those bytes,
independently reads them back, closes the listener and records the restoration.
Every failure path attempts the same restoration when an already-active service
makes that safe. If fixture completion is ambiguous, the runner must not reset or
type into the running program merely to recover startup; it records why exact
restoration was unavailable and leaves the recovery listener for operator action.

The maintained [host/browser/native regression suite](../testing/regression-suite.md)
implements this contract for its nonphysical closure: 54 explicit cases run
from an isolated shared clone of the resolved Extender commit and a fixed clean
EMOS commit, use durable phase/case records and a live SSH-console status stream, and
invoke the accepted Legacy spoken terminal hook without reset. It deliberately
uses host records rather than mainboard per-case messages because the host suite
does not own the foreground. Physical and manual fixtures retain their own
case-specific implementation obligations under A10-T01 through A10-T09.

The Author-launched first complete run passed all 54 cases on 2026-09-29 in
143.542507419 seconds, with unchanged clean Extender
`a8e6c5dc549f355f2264c1423609d2b147410a60` and EMOS
`21a9ba27f1f346473d767c2c3053ee18e8911335` source closures. The terminal hook
also succeeded; total detached-job duration was 163.236620222 seconds. The
[maintained suite guide](../testing/regression-suite.md) records exact phase
timings and evidence hashes. Because the run deliberately pins pre-RP04 EMOS,
it is the neighboring regression baseline, not acceptance of the raw-SD
candidate.

## Findings standard

Use IDs `AUDIT-010-F001` onward. Each finding uses these immutable fields:

A10-FIELD01 — Concise statement and severity.

A10-FIELD02 — Affected actor, source identity, files and symbols.

A10-FIELD03 — Violated or missing contract.

A10-FIELD04 — Direct evidence and counter-evidence.

A10-FIELD05 — Runtime/user consequence and affected configurations.

A10-FIELD06 — Confidence and unresolved alternatives.

A10-FIELD07 — Proposed owner, validation and disposition.

A10-FIELD08 — Source lineage: upstream-unchanged, upstream-ported/adapted or
project-new; exact reference/delta boundary and defect origin.

A10-FIELD09 — Upstream-equivalent and project-functional-duplicate check;
canonical owner, reuse/consolidation decision and justification for any retained
parallel implementation.

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

AUDIT-010-D004 [x] **Accepted, 2026-09-28; amended by D011:** exhaustively audit the current
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

AUDIT-010-D007 [x] **Accepted, 2026-09-28; superseded by D011:** consolidate current development
ExCom and the substantially complete LCD implementation before A10-02 freezes
the audited baseline. Remove the failed r72 whole-frame-lock diagnostic, retain
accepted LCD behavior, and deliberately preserve the demonstrated allocation-
order/resource defect for audit. A10-P01 is a one-time baseline-preparation
exception to the audit-before-fix sequence, not authorization for opportunistic
remediation or production promotion.

AUDIT-010-D008 [x] **Accepted, 2026-09-28; superseded by D011:** make the A10-P01 consolidated
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

AUDIT-010-D011 [x] **Accepted, 2026-09-28:** make the latest retained working
pre-LCD product the sole exhaustive audit target. BUILD-001 reproduces Extender
commit `6c6bea3beb2f8abc89c5b1f40a0e7dd0890a084d` through native ESP-IDF/CMake and
pairs it with current development EMOS v0.1.23 at
`21a9ba27f1f346473d767c2c3053ee18e8911335`. This supersedes D007 and D008
before their combined-baseline prerequisite executed.

AUDIT-010-D012 [x] **Accepted, 2026-09-28:** complete the exhaustive audit,
Author findings review and itemized accepted fixes on the pre-LCD baseline
before attempting to redeploy LCD support. LCD-001 then reapplies the LCD work
as a separately reviewable delta and reruns its geometry, mode-allocation,
browser-coexistence, service and gameplay regressions. Prior experimental LCD
success is evidence and reusable implementation material, not audited baseline
code or permission to merge it unchanged.

## Contract review gate

A10-G01 [x] The Author reviews this draft, corrects its scope and accepts or
revises AUDIT-010-D001 through D010. The Author subsequently accepted the
pre-LCD sequencing amendment in D011 and D012.

A10-G02 [x] The agent commits the accepted contract as its own frozen checkpoint.

A10-G03 [x] A10-01 began only after A10-G02. Its findings receive this later
commit and review; they must not be backfilled into the already frozen contract
as though known at its creation.
