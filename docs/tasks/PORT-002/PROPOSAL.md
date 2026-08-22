# PORT-002 Review Gate 1 — Source selection and merge guidance

Status: Review Gate 1 closed and approved by the Author on 2026-08-22;
implementation not started.

## Outcome

Extend the PORT-001 property graph to classify every file in each immutable
upstream source baseline and every project-owned adapter against named build
profiles. Keep the graph as the sole canonical machine-readable model. Generate
source-selection guides, queries, and tagged-release merge-attention reports as
digest-bound projections rather than independent authorities.

The model must distinguish four facts that are easy to conflate:

1. a file exists because a complete tagged release is available or vendored;
2. a named build actually or intentionally selects it;
3. a selected behavior or accepted disposition explains why; and
4. an upstream change deserves review even when the file is not compiled.

## Schema extension

The current schema's single `build_selection` value cannot represent multiple
profiles, planned versus observed selection, or a selected file containing an
excluded region. Adopt schema version `2.0.0` and replace that scalar as the
source-selection authority with normalized records.

### Build profiles

Add a top-level `build_profiles` collection. Each profile records:

- a stable typed ID and human label;
- whether it is an **observed build** or a **declared target**;
- target board, platform/framework identity, and build configuration identity;
- immutable source-baseline IDs;
- build-manifest, compilation-database, and build-log evidence; and
- the profile against which planned-versus-observed drift is checked, when
  applicable.

Seed two profiles:

- `build-profile:upstream:agon-vdp-v2.16.0-esp32` — the successful observed
  upstream control build; and
- `build-profile:extender:p4-default` — the accepted target selection for the
  normal P4 firmware build.

Runtime EDU modes do not become build profiles unless they later produce
different firmware images. A profile represents compile-time source selection,
not runtime routing policy.

### Complete file nodes

Generate one `file` node for every file in each immutable source tree, not only
files reached by the compiler. Each file node records:

- owner and immutable source ID;
- source-relative path, content hash, and broad file role;
- presence class: `upstream-reference`, `vendored`, `project-owned`, or
  `external-platform`; and
- exact evidence establishing its presence and identity.

The source-tree manifest is exhaustive. Documentation, examples, tests,
licenses, build metadata, and unused implementation remain visible even when
they are not eligible for a firmware image.

### Source-region nodes

Add `source-region` as a node kind. A region has a stable purpose-qualified ID,
one parent file, exact line/span fingerprints, and evidence. Region records are
used only where a reviewed boundary is materially narrower than the file.

This is required for fused sources. For example, `fabutils.cpp` remains selected
because retained utilities need it, while its FileBrowser and classic-ESP32
storage regions are deliberately excluded from the P4 target. The file record
must never be mislabeled as wholly excluded merely to express those decisions.

Selecting or including a file does not imply that every code region in that
file is compiled into the target. File-level selection records physical build
participation; region records separately describe conditional exclusion,
replacement, or other narrower treatment. An observed profile may claim a
region is excluded only when preprocessing/build evidence demonstrates the
effective boundary.

### Selection records

Add a top-level `selection_records` collection. Its unique key is
`(build_profile_id, subject_id)`, where the subject is a file or source region.
Each record contains:

- `status`: `selected`, `excluded`, `available-not-selected`,
  `not-applicable`, or `unresolved`;
- one or more typed cause records;
- mechanical evidence IDs and accepted task/ADR references as applicable;
- graph entry points explaining the retained behavior or adapter that reaches
  the subject;
- any governing SETUP-004 candidate/disposition IDs; and
- a structured unresolved reason when classification is incomplete.

`excluded` means a deliberate target decision. `available-not-selected` means
the file is absent from an observed closure without claiming that product
architecture forbids it. `not-applicable` covers material such as licenses and
documentation that is part of the release but not a firmware build candidate.

The legacy per-node `build_selection` value is removed from schema authority.
Human summaries may display a profile-specific status but must derive it from
the normalized record.

## Closed selection-cause vocabulary

Every cause has a class, evidence, and compatibility rules. A selection record
may carry multiple causes because mechanical mechanism and architectural reason
are different facts.

### Mechanical mechanisms

- `direct-build-input` — explicitly compiled translation unit or source entry;
- `build-rule-match` — selected by a library, glob, source filter, or equivalent
  build rule;
- `transitive-include` — reached through compiler dependency evidence;
- `header-defined-implementation` — executable implementation enters an
  effective translation unit through textual inclusion;
- `generated-build-input` — generated source or artifact selected by an
  evidenced build step.

### Reviewed architectural reasons

- `retained-compatibility-requirement` — selected behavior accepted by the VDU
  inventory or an ADR requires the subject;
- `project-adapter` — project-owned code is selected to satisfy a retained seam
  or replacement disposition;
- `inherited-broad-build-selection` — mechanically selected only because an
  upstream build rule is broader than the accepted target closure;
- `deliberate-exclusion` — an accepted task disposition or ADR excludes the
  subject from the named target profile;
- `non-runtime-upstream-content` — release material is retained for provenance,
  licensing, tests, examples, or documentation rather than firmware selection;
- `unresolved-selection` — evidence or an accepted decision is insufficient.

The vocabulary is closed and versioned. Adding a cause requires a schema and
validator change; free-form explanations do not become substitute causes.

## Validation contract

JSON Schema validates record shape. Project validation additionally enforces:

1. every immutable source-manifest file has exactly one file node;
2. every file has exactly one selection record per applicable build profile;
3. `(profile, subject)` tuples and all typed IDs are unique;
4. every observed `selected` record has mechanical build/include evidence;
5. every declared-target `selected` record has an evidenced closure or accepted
   compatibility/adapter reason;
6. every `excluded` record cites an accepted disposition or ADR;
7. `inherited-broad-build-selection` cannot be the sole justification for a
   declared-target selection;
8. `unresolved` records remain visible and fail release/qualification gates;
9. file, source-tree, and region-span fingerprints match immutable inputs;
10. region records resolve to selected parent files and cannot pretend that an
    unimplemented conditional boundary already exists;
11. observed-versus-declared selection drift is explicit and fails validation
    unless recorded as an expected transitional condition;
12. every graph entry point, evidence ID, disposition ID, and decision
    reference resolves;
13. a newly appearing upstream file defaults to `unresolved`, never silently to
    unselected; and
14. deterministic regeneration is byte-identical.

A generated SQLite database may later accelerate queries, but remains
disposable and digest-bound to the validated YAML graph.

## Durable artifact layout

Promote the accepted PORT-001 machinery into a continuing project boundary:

```text
docs/dependencies/
├── README.md
├── schema/
│   └── dependency-artifacts.schema.json
├── reviewed/
│   ├── source-baselines.yaml
│   └── claims.yaml
├── generated/
│   ├── code-graph.yaml
│   ├── source-selection.yaml
│   ├── source-selection.md
│   └── merge-attention/
│       └── <old-release>--<new-release>.{yaml,md}
├── scripts/
└── tests/
```

- `code-graph.yaml` is the canonical generated graph.
- Reviewed claims contain only evidenced semantic interpretation and decision
  references; they do not restate the task or ADR text.
- `source-selection.yaml` is a complete digest-bound projection optimized for
  file/profile queries. Its Markdown companion is the compact human guide.
- Merge-attention YAML is the authoritative projection for one comparison;
  Markdown is its deterministic review view.
- Task-specific proposals and acceptance history remain under `docs/tasks/`.
- No task-local analysis script moves into the top-level routine `scripts/`
  directory.

This promotion follows the accepted project-development lifecycle: exploratory
tasks keep their implementation, evidence, and review boundaries siloed while
scope is still emerging; once multiple tasks establish a stable shared model,
the reusable result is synthesized into a durable subject-oriented structure.
Task records preserve how the parts were established without forcing production
users or agents to navigate historical task boundaries for routine work.

Local source roots remain command arguments represented by placeholders in
tracked output. Once sources are imported, the same manifest logic verifies the
repository copies and records any compatibility delta; the model must not call
an external reference tree “vendored.”

## Query contract

The continuing query tool must accept any combination of:

- upstream owner and file or region;
- build profile and selection status/cause;
- subsystem, command, packet, or EDU-visible behavior;
- SETUP-004 disposition or ADR/task reference; and
- changed tagged release.

Canonical query output is bounded YAML with source-graph identity, applied
filters, complete matching records, and explicit continuation boundaries.
Markdown and diagrams are optional projections. Whole-graph grep remains a
fallback, not the normal agent workflow.

## Tagged-release merge-attention rules

Build each release graph independently from immutable tagged inputs, validate
both, then compare normalized identities, file hashes, graph relationships,
selection records, reviewed evidence, and build rules. Every changed, added,
deleted, or renamed file appears in exactly one highest-applicable tier with all
matching reason codes.

### Upstream watch cadence

Do not wait for a tagged release to discover months of upstream activity.
Establish a frequent informational watch over the upstream development branch,
nightly build activity when published, release notes, issues/bug reports, and
material pull-request discussion. This watch has two purposes:

1. keep prospective source diffs small enough for focused porting and unit-test
   preparation; and
2. preserve the maintainers' natural-language problem statements, rationale,
   rejected approaches, and expected behavior as contextual evidence for later
   agents.

Moving branches and nightlies never become import, build, or qualification
baselines. ADR-0011's latest-official-tag rule remains authoritative. Watch
reports are advisory previews tied to exact observed commits and upstream issue
or pull-request identifiers. Human discussion may explain intent but does not
override source, official documentation, accepted project decisions, or test
evidence.

The expected routine is frequent small watch reviews followed by a bounded
tagged-release reconciliation. The four attention tiers remain necessary for
completeness and exceptional large releases, but they should not encourage
agents to postpone upstream review until a thousand-line porting event.

### Tier A — mandatory boundary review

- new or unresolved files;
- deleted or renamed selected files;
- build manifests, dependency metadata, source filters, umbrella/public
  headers, or generated-code rules;
- selected/excluded status changes or observed-versus-declared drift;
- project adapter or conditional source-region boundaries;
- stale reviewed evidence or source-span fingerprints; and
- licenses, notices, or other distribution obligations.

Tier A blocks accepting the new baseline until explicitly disposed.

### Tier B — selected closure

- changed files or regions selected by the Extender target;
- direct or transitive dependencies of selected code; and
- source implementing retained behavior, packets, state, callbacks, or platform
  seams.

### Tier C — unselected but connected

- deliberately excluded implementation;
- unselected code that includes, is included by, declares interfaces for, or
  otherwise reaches the selected closure;
- portability or hardware code adjacent to a selected adapter boundary; and
- files tied to a deferred or future disposition.

### Tier D — isolated unselected content

- changed upstream content with no evidenced selected-closure or boundary
  relationship.

Tier D remains visible. It is lower attention, never “ignore.” Security review
may promote any tier, but the generator must not infer security significance
from filenames alone.

Exact Git change status is evidence. Hash-equal moves may be suggested as rename
candidates, but tools must not invent identity continuity when Git/source
evidence does not establish it. The highest matching tier wins; all reason codes
remain attached and deterministically sorted.

## Initial proof set

Implementation must demonstrate the model against cases that exercise distinct
boundaries:

1. vdp-gl DS3231 — present in the complete release, selected by the upstream
   broad build, deliberately excluded from the P4 target;
2. `fabutils.cpp` — selected file with separately excluded FileBrowser and
   classic-storage regions;
3. concrete VGA controller source — upstream-selected but replaced by a
   project-owned P4 adapter/backend in the target;
4. an official VDP header-defined implementation — selected transitively and
   required for retained compatibility;
5. CRC or ESP32Time source — exact release dependency selected through the
   official VDP closure; and
6. a license or documentation file — retained and merge-visible but not a
   firmware build candidate.

The DS3231 case remains the minimum explicit acceptance fixture required by the
task. The broader set prevents a passing implementation from handling only easy
whole-translation-unit exclusions.

## Proposed implementation sequence after approval

1. establish `docs/dependencies/` from the accepted PORT-001 implementation;
2. implement schema `2.0.0`, migration, validation, and deterministic tests;
3. generate exhaustive source manifests and complete file nodes;
4. add observed and declared build profiles plus normalized selection records;
5. ingest accepted SETUP-004 dispositions and exact region refinements;
6. generate the source-selection YAML/Markdown projection and query tool;
7. implement tagged-release comparison and merge-attention projections;
8. run the six-case proof set and deterministic regeneration; and
9. stop for Review Gate 2 before treating the promoted system as routine
   upstream-integration infrastructure.

No firmware source selection, vendored-source import, or build configuration is
changed merely by implementing the documentation graph. Importing source into
the firmware tree remains an explicit reviewed operation using the accepted
ADR-0011/ADR-0012 locations and identities.

## Review decisions requested

1. **Accepted 2026-08-22.** Adopt schema `2.0.0` with normalized build profiles
   and per-profile selection records replacing the single selection scalar.
2. **Accepted 2026-08-22.** Use exact source-region refinement for fused
   selected files. File inclusion does not imply that every code region is
   compiled; observed exclusions require preprocessing/build evidence.
3. **Accepted 2026-08-22.** Use the closed cause vocabulary and validation
   rules. The normalized model applies relational-database discipline while
   retaining validated deterministic YAML as authority.
4. **Accepted 2026-08-22.** Promote the accepted task-local dependency work into
   the durable `docs/dependencies/` layout with the graph as sole canonical
   machine-readable integration. Preserve task evidence while making routine
   use independent of historical task boundaries.
5. **Accepted 2026-08-22 with cadence stipulations.** Use the four
   merge-attention tiers and “nothing disappears” rule, supported by frequent
   informational monitoring of upstream development/nightly activity and
   natural-language issue/PR discussion. Only official tags become import and
   qualification baselines.
6. **Accepted 2026-08-22.** Use the six-case implementation proof set and stop
   at Review Gate 2 before treating the promoted system as routine production
   infrastructure.
