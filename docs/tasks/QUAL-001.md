# QUAL-001 — Establish the durable compatibility qualification matrix

## State

- Status: In progress — Works 1–3 complete; Review Gate 2 paused by operating-mode audit
- Started: 2026-08-22 22:59 EDT
- Finished: --

## Intent

Promote AUDIT-001's accepted compatibility-ledger concept into permanent,
role-named infrastructure under `docs/qualification/`. The matrix will connect
each accepted stock VDP behavior to its implementation owner, operating-mode
scope, transport and wiring dependencies, MOS-visible effects, evidence, and
qualification state throughout porting, release, and maintenance.

The matrix is a traceability and qualification authority. It does not redefine
VDU commands, create protocols, resolve open architecture questions, or turn a
successful build into a compatibility claim.

Under PORT-008-D003, mode-neutral r02 construction and component evidence is
recorded in HW-001, QUAL-002, and PORT-008 using the
[staged process](../qualification/staged-circuit-validation.md). Completion of
this task's four-mode matrix is not a prerequisite for those observations.
This task later links accepted evidence to its exact obligations; neither a
partial circuit result nor an unreviewed matrix can qualify a complete mode.

## Next bounded consumer — browser keyboard

REMOTE-001/PORT-005/PORT-008 and agon-emos INTEG-009 consume AUDIT-004
P013/P014 and A003–A005 for exact keyboard packets, event variables, MOS key
sysvars/count, virtual map, callbacks and read/editor behavior. Record those
specific obligations and declared test coverage before claiming parity. The
full matrix, other packet families, mouse and all-mode qualification remain
separate; do not require their completion before the selected UART keyboard
increment. Source-qualified exceptions in AUDIT-004 remain authoritative
research findings rather than silently corrected stock contracts.

## Authority and inputs

- [AUDIT-001](AUDIT-001.md), especially accepted decisions R01–R03 and the
  `C`, `X`, and `W` inventories.
- [SETUP-004 VDU inventory](SETUP-004/VDU-inventory.md), the accepted source
  for retained, mode-dependent, no-op, unresolved, and carved-out command
  dispositions.
- [ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md)
  and open decisions in [SETUP-005](SETUP-005.md).
- [Dependency infrastructure](../dependencies/README.md), source-selection
  records, task manifests, procedures, artifact registry, and run manifests.
- [Versioning policy](../versions/README.md).

## Required durable boundary

The maintained construct will live under `docs/qualification/` and provide:

1. a README defining authority, lifecycle, maintenance, and generated-file
   boundaries;
2. authoritative machine-readable compatibility records;
3. a schema and validator enforcing stable identity, enums, uniqueness,
   required fields, valid references, and evidence-state consistency;
4. deterministic generators for compact human-readable matrices and bounded
   task-, mode-, subsystem-, and release-oriented views; and
5. tests proving deterministic generation, source coverage, and rejection of
   malformed or contradictory records.

Exact filenames and schema mechanics are proposed during Work 1 and frozen at
Review Gate 1. YAML is the recommended human-maintainable authority; a JSON
Schema or equally deterministic validator may enforce structure. Generated
Markdown must never become a second source of truth.

## Work

### QUAL-001.1 — Define identity and schema

1. Define stable row identity without coupling it to mutable Markdown line
   numbers or task-local numbering.
2. Define how rows are derived from or linked to the accepted VDU inventory so
   command names and dispositions are not maintained independently in two
   places.
3. Define fields for official behavior authority, compatibility disposition,
   operating modes, implementation owner, source/dependency references,
   transport/wiring path, MOS packet/sysvar effects, carve-outs, blockers,
   qualification obligations, evidence, and status.
4. Distinguish `unknown`, `not_applicable`, `blocked`, `deferred`, `planned`,
   `implemented`, and `qualified` rather than overloading blank cells.
5. Keep compatibility-critical obligations separate from secondary Extender
   capability qualification while allowing shared tooling and evidence forms.

**Review Gate 1:** stop for Author review of the proposed layout, identity
rules, schema, lifecycle, and one small representative fixture before creating
the complete matrix.

#### QUAL-001.1 execution record

Work 1 produced the task-local
[Review Gate 1 proposal](QUAL-001/PROPOSAL.md), proposed
[JSON Schema](QUAL-001/schema/compatibility-matrix.schema.json), and
[representative YAML fixture](QUAL-001/fixtures/review-gate-1.yaml). No file
under the proposed durable `docs/qualification/` boundary was created, and no
VDU disposition, task ownership, operating-mode decision, implementation,
procedure, wiring, or qualification state was changed.

The proposal recommends:

1. reviewed normalized YAML inputs for interfaces, secondary capabilities,
   mode expectations, and obligations;
2. one deterministic generated canonical join with Markdown as projections;
3. a one-time Gate 2 promotion that imports the accepted VDU inventory exactly
   before replacing its independently edited Markdown role;
4. typed selector-derived interface IDs and separate claim-oriented obligation
   IDs;
5. independent interface-disposition, mode-expectation, implementation,
   qualification, and evidence axes; and
6. repository-native JSON Schema plus semantic validation rather than a
   database service.

The fixture contains four VDU interfaces, one secondary capability, one
cross-cutting qualification domain, five mode expectations, six qualification
obligations, two accepted evidence records, and two deliberately partial
evidence links. The repository `.venv` validated
the JSON Schema as Draft 2020-12, validated the fixture with zero schema errors,
and passed proposal-level uniqueness, tuple-uniqueness, referential-integrity,
blocked-state, subject/scope, and evidence-link invariants.

#### Review Gate 1 register

| ID | Proposed decision | Recommendation | Status |
|---|---|---|---|
| `QUAL-001-RG1-01` | Use normalized YAML collections and a generated canonical join rather than a hand-maintained flat matrix. | Accept | Accepted 2026-08-22 |
| `QUAL-001-RG1-02` | At Gate 2, promote the exactly imported VDU inventory into YAML authority and retire its independently edited Markdown role. | Accept | Accepted 2026-08-22 |
| `QUAL-001-RG1-03` | Use typed selector-derived interface IDs and separately stable obligation IDs. | Accept | Accepted 2026-08-22 |
| `QUAL-001-RG1-04` | Keep disposition, mode expectation, implementation state, qualification state, and evidence lifecycle independent. | Accept | Accepted 2026-08-22 |
| `QUAL-001-RG1-05` | Keep compatibility-critical and secondary capability qualification strictly separate. | Accept | Accepted 2026-08-22 |
| `QUAL-001-RG1-06` | Use repository-native YAML, JSON Schema, and semantic validators without a database service. | Accept | Accepted 2026-08-22 |
| `QUAL-001-RG1-07` | Accept the proposed durable layout and lifecycle as the boundary for Work 2. | Accept | Accepted 2026-08-22 |
| `QUAL-001-RG1-08` | Add normalized qualification domains as subjects for cross-cutting compatibility obligations. | Accept | Accepted 2026-08-22 |

Do not begin QUAL-001.2 until all eight Review Gate 1 items are disposed by the
Author.

All eight items were accepted by the Author on 2026-08-22. Review Gate 1 is
closed, and the approved Work 2 boundary may be implemented.

Work 2 preflight exposed compatibility obligations whose subjects span several
commands or have no command selector: shared compatibility transport,
operating-mode lifecycle, and assembled-system electrical behavior. Assigning
these claims to an arbitrary interface would falsely narrow them, while
classifying them as product capabilities would violate the accepted separation
between compatibility-critical and secondary work. RG1-08 therefore adds
stable `domain:extender:*` subjects solely to group such cross-cutting claims;
domains do not define commands, protocols, wiring, or architectural decisions.

### QUAL-001.2 — Build deterministic infrastructure

1. Create the approved role-named directory and authority files.
2. Implement schema/semantic validation, deterministic generation, and tests.
3. Reject duplicate row identities, missing accepted VDU coverage, dangling
   task/code/evidence references, impossible status combinations, and edits to
   generated files.
4. Produce explicit white-background SVG only where a graph materially helps;
   the primary human interface should remain compact tables and focused views.

#### QUAL-001.2 execution record

The approved role-named infrastructure now lives under
[`docs/qualification/`](../qualification/README.md). Nine reviewed semantic
collections feed one digest-bound canonical YAML join and deterministic compact
Markdown projections. The implemented model includes the RG1-08 domain subject
without changing the accepted interface, capability, mode, obligation, or
evidence roles. Sources, modes, evidence, and evidence links received their own
reviewed files because they were already normalized principal collections in
the approved model; the proposal's abbreviated tree had omitted their
filenames.

The permanent scripts build, render, validate, and check byte-identical
regeneration. JSON Schema Draft 2020-12 enforces record structure and closed
vocabularies. Semantic validation enforces global and tuple uniqueness,
complete interface/mode coverage, parent/subject/source/task/decision/dependency
referential integrity, blocker and qualification-evidence invariants, scope
separation, repository-local paths, and the exact pre-Gate-2 inventory import.
Ten tests exercise the valid model and deliberate duplicate, missing-coverage,
dangling-reference, blocker, evidence-scope, and false-qualification failures.

No graph was generated because the primary relationships are clearer as tables
and bounded task/mode views. The one-time import and initial mode seeding tools
live under `docs/tasks/QUAL-001/scripts/`, not the permanent recurring tooling.

### QUAL-001.3 — Populate the accepted baseline

1. Import every accepted VDU inventory item without changing its disposition.
2. Attach established implementation ownership and evidence from SETUP-004,
   PORT-001 through PORT-003, current ADRs, procedures, and runs.
3. Import AUDIT-001 compatibility obligations and wiring findings as linked
   qualification requirements, not duplicated command definitions.
4. Represent every SETUP-005-dependent field as blocked by its exact decision
   ID; do not infer an answer.
5. Preserve a separate view of secondary product-capability tests from
   AUDIT-001 without allowing them to satisfy compatibility-critical rows.

#### QUAL-001.3 execution record

The candidate reviewed baseline imports all **211** marked SETUP-004 entries
exactly: 185 supported, 17 retained mode-dependent, eight unsupported, one
unresolved, and no accepted no-op entries. Each has one immutable candidate ID,
and the validator rejects any selector, title, category, disposition, parent,
source, omission, addition, or identity difference from the accepted inventory.
The generated category-ordered VDU view is a candidate replacement projection;
the task-local inventory remains authoritative until this gate is accepted.

The superseded candidate contains 633 explicit interface/mode tuples:

- legacy mode routes all 211 VDU interfaces to the stock VDP;
- cooperative mode routes all 211 ordinary VDU interfaces to the stock VDP,
  consistent with ADR-0014's separate EDU path; and
- EDP-exclusive mode requires Extender for 185 supported entries, marks eight
  accepted carve-outs unsupported, and leaves 18 input/RTC entries unresolved
  under their exact SETUP-005 blockers.

This paragraph records the generated three-mode candidate as reviewed at the
time. It is not the accepted operating-mode vocabulary. The 2026-08-23 audit
and Author disposition replace it with Legacy, Exclusive Compatible, Exclusive
Extended, and Dual; corrected reviewed data will contain 844 tuples.

All 25 AUDIT-001 requirements are represented once as qualification
obligations: 19 compatibility-critical `C` requirements and six separate
secondary `X` capabilities. Fourteen are planned, ten are blocked by exact
SETUP-005 or PORT-003 gates, and deferred local MIPI output remains unknown and
unassigned. Established PORT-003 implementation state, PORT-004 through
PORT-008 and QUAL-002 ownership, source-selection nodes, the accepted harness
and fixture, three evidence records, and four deliberately partial evidence
links are attached. Nothing is marked qualified; inherited evidence and the
current frame-service run support only their stated narrow claims.

The baseline does not resolve SETUP-005, invent a transport or wiring contract,
promote inherited evidence, or alter a SETUP-004 disposition.

**Review Gate 2:** stop for Author review of coverage, classifications,
blockers, and generated views before making the matrix a gate for other tasks.

#### Review Gate 2 register

| ID | Candidate decision | Recommendation | Status |
|---|---|---|---|
| `QUAL-001-RG2-01` | Accept the exact 211-interface import and its stable identities. | Accept | Accepted 2026-08-23 |
| `QUAL-001-RG2-02` | Accept the complete legacy, EDP-exclusive, and cooperative mode classifications and owners. | Accept | Withdrawn 2026-08-23 — superseded by the four-mode taxonomy |
| `QUAL-001-RG2-02R` | Accept corrected Legacy, Exclusive Compatible, Exclusive Extended, and Dual classifications and owners. | Accept after regeneration and review | Open |
| `QUAL-001-RG2-03` | Accept the 19 compatibility-critical and six secondary AUDIT-001 obligation classifications. | Accept | Open |
| `QUAL-001-RG2-04` | Accept the current implementation, qualification, blocker, and deferral states as the initial baseline. | Accept | Open |
| `QUAL-001-RG2-05` | Accept the evidence records and deliberately partial claim links without qualifying any obligation. | Accept | Open |
| `QUAL-001-RG2-06` | Accept the canonical YAML, compact generated inventory/matrix, and bounded task/mode/blocker views. | Accept | Open |
| `QUAL-001-RG2-07` | Promote reviewed YAML to interface authority and retire independent editing of SETUP-004's task-local inventory during Work 4. | Accept | Open |

RG2-02 and all subsequent Review Gate 2 dispositions are paused by
[`AUDIT-2026-08-23-001`](../decisions/AUDIT-2026-08-23-001-operating-mode-semantics.md).
The audit confirms that the candidate three-mode cross product omits a distinct
P4-exclusive stock-UART mode. The Author subsequently accepted Legacy,
Exclusive Compatible, Exclusive Extended, and Dual as the four formal modes,
with stable IDs recorded in SETUP-005 and ADR-0014. Remaining mode boundaries
must be resolved before the reviewed records are corrected and this gate
resumes.

Do not begin QUAL-001.4 or change the SETUP-004 inventory's authority until all
active Review Gate 2 items are disposed by the Author.

### QUAL-001.4 — Integrate the maintenance contract

1. Update project task/process guidance so every implementation task names the
   matrix rows it satisfies, affects, blocks, or deliberately leaves open.
2. Define how accepted decisions, source changes, upstream imports, procedures,
   and run manifests update the matrix without copying their full contents.
3. Add task-closure and release checks that reject unexplained required rows
   while permitting explicit accepted carve-outs and deferrals.
4. Document promotion from task-local evidence into durable qualification
   records and how superseded/rejected evidence remains traceable.

## Dependencies and gates

- AUDIT-001 commit `c0a8f67` is the accepted planning authority.
- Do not begin PORT-003 Phase D implementation until QUAL-001 Review Gate 1 is
  accepted and the initial row/ownership model can receive its decisions.
- Do not claim matrix completeness merely because every VDU inventory line was
  imported; response, MOS, operating-mode, physical-sink, and bench obligations
  are independently tracked.
- Do not change SETUP-004 dispositions or ADR-0014 decisions inside this task.
- Do not create a database service or runtime dependency; repository-native
  YAML, deterministic generators, and validators must remain usable offline.

## Affected implementation

This task creates documentation infrastructure and validation tooling only. It
does not modify VDP, MOS, eZ80 application, transport, firmware, wiring, or test
fixture behavior.

Existing tasks gain planning dependencies on QUAL-001 in this tranche. They
will gain row-specific matrix references after Review Gate 2; those references
assign qualification ownership without moving implementation work into
QUAL-001.

## Completion criteria

1. The Author approves both review gates.
2. Every accepted VDU inventory item has exactly one authoritative matrix
   identity and no independently maintained duplicate description.
3. AUDIT-001 obligations have owners, blockers, deferrals, or accepted
   not-applicable dispositions.
4. Deterministic generation and validation pass from a clean checkout.
5. Existing tasks, procedures, and task templates describe their matrix update
   obligations.
6. The dated development log records promotion, and AUDIT-001 can cite the
   durable construct instead of acting as its permanent runtime home.
7. The validator rejects every adversarial authority, evidence, owner,
   blocker, and digest mutation required by accepted REMED-002 finding F006,
   and affected earlier qualification claims have been re-evaluated.

## Accepted REMED-002 finding

[REMED-002](REMED-002.md) assigns QUAL-001
`INTEGRITY-AUDIT-F006`. The detailed demonstrations and provenance remain in
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md).
Review Gate 2 remains paused.

1. [ ] Require exact, not prefix-plus-suffix, resolution of task, ADR,
   corrective-action, and other authority identifiers.
2. [ ] Validate every owner, decision, blocker, dependency, and evidence field
   that can support a qualification or deferral claim.
3. [ ] Resolve evidence references to existing in-repository paths and validate
   their declared record type and required identity where applicable.
4. [ ] Recompute and compare stored reviewed/generated input hashes rather than
   accepting schema-valid stale digests.
5. [ ] Add negative tests for dangling identifiers, nonexistent evidence,
   forged digests, stale generated inputs, and unsupported qualified states.
6. [ ] Re-evaluate any promoted record materially supported by the defective
   paths and mark it retained, regenerated, superseded, or withdrawn.

This is repository validation semantics; `jsonschema` is not the defect and a
schema-only pass cannot close this finding.
