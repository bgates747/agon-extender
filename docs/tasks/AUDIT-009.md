# AUDIT-009 — Documentation accuracy, consolidation and external-agent usability

## Executive summary

**Author approved execution: one-hour unattended run, 2026-09-24
03:12:34–04:12:34 UTC.** Review
Extender documentation against maintained code, accepted decisions and retained
validation, then consolidate routine instructions into a small set of reliable
entry points. A person or an agent working on another project must be able to
find a supported capability, identify its prerequisites and limits, and use it
without reconstructing weeks of task history.

This audit changes documentation and navigation. It does not implement missing
features, change firmware, use the bench, rerun qualification or reopen settled
architecture. Unknowns remain explicit; a documented feature is not automatically
a deployed or qualified feature. TODO.md remains the single unfinished-work index.

## Scope and authority

| Material | Review and disposition |
|---|---|
| Extender root README, AGENTS, handoff, TODO and documentation indexes | Entry points, reading order, current scope, conflicting instructions and stale startup assumptions |
| Maintained operating guides and procedures | Commands, arguments, paths, prerequisites, errors, recovery, authorization and final state |
| Architecture, specifications, protocol/API contracts, ADRs and hardware documents | Current accepted design, implementation differences, unresolved decisions, ownership and qualification limits |
| Task documents and their evidence silos | Promote recurring instructions; reconcile stale status; retain useful experiments, failures and historical identities |
| Development logs, qualification records, manifests and version registry | Traceability, dates, exact artifact combinations, measured scope and frozen versus current claims |
| Tracked scripts, examples, fixtures and embedded documentation | Compare help, defaults, examples and operational behavior with their guides; inspect relevant code where material |
| Ignored HANDOFF/HARDWARE/agents records used in routine work | Review relevant current records locally; classify old records as history; never publish private topology or copy the whole agents archive |
| Product-owned agon-emos documentation | Reconcile EMOSlet ABI, CLI dispatcher, firmware ownership, source/build instructions and installed listener placement |
| Other project/canonical instructions and official references | Consult applicable authorities read-only; record cross-project corrections for their owners rather than editing unrelated projects |

Inventory all tracked human-readable documentation, including non-Markdown text,
relevant comments/help and generated-document sources. Account for binary manuals,
diagrams and vendor documentation by provenance and role; do not rewrite or audit
every upstream manual. Every inventoried item gets a disposition, even when its
body is retained unchanged. Exclude unrelated private conversations and unrelated
project documentation. Discovering a referenced dependency expands the inventory
only for the affected contract, not into another project's general audit.

Accepted architecture defines intended behavior. Maintained code defines what
is implemented; exact build/deployment receipts define what is installed; tests
and human reports support only their recorded scope. A conflict between these is
a finding, not permission to silently make one claim replace another. Historical
records remain true to their date, while current guides link to later dispositions.

## Organization and evidence discipline

Work in `docs/tasks/AUDIT-009/` during execution. Create only these audit aids:

| Artifact | Purpose |
|---|---|
| `INVENTORY.csv` | Repository/path, document role, audience, subject, owner, authority target, state and review disposition |
| `FINDINGS.md` | Stable A09-Fnnn finding IDs, exact claim/location, conflicting evidence, severity, proposed correction, owner and resolution |
| `AUTHORITY-MAP.md` | One proposed maintained destination per subject and redirects from duplicate/task-local material |
| `CHECKS.md` | Executed checks, exact inputs/results, walkthrough outcomes and explicitly untested instructions |
| `RESULTS.md` | Concise closeout: changed authorities, reconciled claims, unresolved gaps and acceptance limits |

Use the task file below as the actionable checklist; audit aids are evidence and
mappings, not additional competing queues. Work on one workflow or document family
at a time, in batches of at most ten documents. For each batch: record the input
set, compare claims, log findings, make approved documentation changes, check links
and examples, record completion, then select the next batch. Do not follow every
interesting reference recursively. Link an already-reviewed contract instead.

Classify findings as: operationally consequential error; incorrect capability or
qualification claim; missing required instruction; conflicting/duplicated authority;
stale status/navigation; or editorial-only. Fix operational and claim errors first.
Every correction must cite a source location, accepted decision, exact retained
result or explicitly labelled inference. Do not turn plausible behavior into fact.

## Review order and discrete work items

A09-01 [ ] Establish the review baseline. Record branch/commit and dirty state for
Extender and EMOS; preserve unrelated work. Identify which machine-local record
owns currently installed artifacts. Record relevant canonical policies and existing
review work, especially PLAN-001 queue reconciliation, so this audit does not
repeat an already resolved investigation. No endpoint access is required.

A09-02 [ ] Inventory documentation and references. Enumerate tracked documents,
script/example READMEs, relevant help producers and generated sources; identify
local operational handoff inputs separately. Classify current authority, draft,
historical evidence, vendor reference, duplicate or obsolete entry point. Check
README/index/TODO reachability and document owner. Explicitly record exclusions.
Do not read every large transcript before deciding its role.

A09-03 [ ] Map the external user's journeys. For each journey, identify its entry
point, host tool, Agon command, processor/service owners, transport, required
firmware/build, SD location, output/evidence and stop/recovery behavior. Prioritize:

| Journey | Required review points |
|---|---|
| Discover capabilities and start safely | Supported versus planned features; installed versus repository builds; bench ownership; Linux/Mac differences; machine-local endpoint discovery |
| Transfer files | Current `EMOS sdserve` EMOSlet invocation and `/emos` placement; Legacy/input prerequisites; normal/fast pairing; activate/stage semantics; sessions/resume; backup cleanup; held-open files; SD layout |
| Control and observe Agon remotely | Physical/browser/agent input ownership, pacing, locale/lock state, capture/release/fullscreen limits, reset actuator ownership, screen-text limitations and video connection behavior |
| Run another project's software | Deployment locations, load/run/utility distinctions, application-memory preservation limits, ExCom/Legacy routing, supported APIs and known command deferrals |
| Build, update and recover | Source ownership, canonical wrappers, required guards, identities, firmware selection, emulator profiles, flash authorization, preserved rollback and recovery readiness |
| Interpret tests/performance | Mainboard versus Extender, capture interference, browser versus rendering/pacing costs, sample scope, units, historical regressions and active bug dispositions |
| Understand hardware and future work | Installed DevKit versus planned P4-PC, wiring/as-built limits, USB/input, SD ownership, HDMI/MIPI/VGA and other deferred work without presenting plans as capabilities |

A09-04 [ ] Review the maintained operations documents first. Trace every executable
example through current CLI help or source; verify option names, path conventions,
required mode/input state, state-file lifecycle and success/error meaning. Mark
examples that require hardware as inspected but not executed. Explicitly compare
fast-transfer and EMOSlet instructions following the recent deployments. Flag
old reset prohibitions, old installation paths or old capability restrictions
for evidence-based reconciliation, not blind search-and-replace.

A09-05 [ ] Review architecture, protocols, specifications and ADRs. Check actor
ownership, EMOS routing rules, foreground versus resident work, formats and ABI,
wire assumptions, mode/input independence, implemented subsets and deferred
commands. Separate accepted-but-partial decisions from qualification status.
Map discrepancies to current tasks/bug IDs; do not change architecture to fit
an implementation accident. Refer material unresolved choices to the Author.

A09-06 [ ] Review task/status/evidence consistency. Reconcile TODO with task files,
accepted results, bug register, development logs and version records. Distinguish
completed scope, remaining acceptance, deliberately deferred work and superseded
experiments. Preserve valid historical measurements, failure conditions, artifact
identities and approvals. Add a short later-disposition link where old prose looks
like current guidance; do not rewrite old results into present-day claims. Do not
close a task merely because its code compiled or an unrelated game worked.

A09-07 [ ] Propose the consolidation map before moving content. Prefer existing
role-named guides, including mainboard SD, remote keyboard/control, SD layout,
recovery and protocols. Define a compact root landing page with a capability/status
overview and links to human quick starts, agent operation instructions and detailed
contracts. A short external-agent entry point should reference those same guides,
not duplicate command catalogs or create a second normative specification.
Record exact keep/merge/promote/redirect/retire dispositions and ask for Author
review if the map changes canonical policy or cross-project ownership.

A09-08 [ ] Consolidate approved, evidenced material in small subject batches.
Promote recurring task-local procedures to their maintained role-named authority;
replace duplicates with short contextual links. Give each operating procedure a
consistent structure: purpose/status, prerequisites/ownership, exact invocation,
expected outcome, failure/recovery, stop/final state, limitations and evidence.
Use plain language first, precise contracts beneath it. Retain provenance for
borrowed documentation and useful evidence; remove redundant explanations rather
than building another archive tree. Update all affected inbound links and indexes.

A09-09 [ ] Validate documentation mechanically and by walkthrough. Check repository-
relative links/anchors, missing targets, task/detail correspondence, command names
and options against their owning tools, stale path references, contradictory status
claims and leaked machine-specific details. Inspect generated sources rather than
patching output alone. Run only safe local help/parser/link checks; no command that
contacts a board, transfers a file, flashes or resets merely to validate an example.
Record tooling limitations instead of promising exhaustive semantic validation.

A09-10 [ ] Perform two fresh-reader walkthroughs from the proposed landing page:
a human using Mac/Linux host tools, and an agent in another project. Resolve how
each finds the endpoint, determines bench ownership/current firmware, starts and
stops an EMOSlet, chooses checked/fast transfer, handles an uncertain request and
locates authoritative limits. Repeat a read-only screen/control discovery journey.
Use documentation alone initially; record every answer requiring memory, an
unindexed task or source excavation as a remaining documentation gap. These are
desk walkthroughs, not hardware acceptance claims.

A09-11 [ ] Close out with coverage accounting. Every inventory item has a review
state and disposition; every consequential finding is fixed with evidence or has
an explicit owner/remaining gate. Summarize consolidated authorities and residual
unknowns for Author review. Update the dated development log and authoritative
TODO. Commit approved changes by documentation subject/task; do not sweep in
other agents' work or silently publish local bench details.

## Completion and stopping rules

The deliverable is usable current guidance with traceable limits, not a percentage
of files edited. Completion requires a navigable entry point, one maintained
source per operational contract, reconciled high-impact claims, successful local
checks/walkthroughs and an explicit unresolved-findings list.

If documentation exposes a product defect, record/link its existing task or bug
register entry and document the present limitation; do not implement a fix under
this audit. If evidence is absent, label the claim unverified and identify the
specific missing proof. No new bench tests, firmware builds, upstream research
campaigns, architecture redesign or wholesale task reordering are implied.

After each batch, retain a short next-batch pointer and progress state so another
agent can continue without repeating discovery. Stop for Author input only on a
material unresolved decision or expanded scope. The Author now authorizes documentation execution within the one-hour window.
No bench work is authorized. Stop at the deadline with honest partial coverage,
remaining findings and a precise continuation point if the full audit cannot fit.
