# QUAL-001 — Establish the durable compatibility qualification matrix

## State

- Status: Not started — plan approved by the Author on 2026-08-22
- Started: --
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

### QUAL-001.2 — Build deterministic infrastructure

1. Create the approved role-named directory and authority files.
2. Implement schema/semantic validation, deterministic generation, and tests.
3. Reject duplicate row identities, missing accepted VDU coverage, dangling
   task/code/evidence references, impossible status combinations, and edits to
   generated files.
4. Produce explicit white-background SVG only where a graph materially helps;
   the primary human interface should remain compact tables and focused views.

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

**Review Gate 2:** stop for Author review of coverage, classifications,
blockers, and generated views before making the matrix a gate for other tasks.

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
