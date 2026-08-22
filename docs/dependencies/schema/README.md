# Dependency artifact schema

Schema `2.0.0` formalizes the durable `code_graph` and bounded
`dependency_slice` artifacts. YAML is tracked for review; JSON Schema defines
shape, and `validate-dependency-artifact.py` enforces graph-wide invariants that
JSON Schema cannot express.

## Canonical graph model

The graph contains stable typed nodes, evidenced edges, unresolved lexical
relationships, immutable source identities, and two normalized source-selection
collections:

- `build_profiles` describe an observed build or declared compile-time target;
- `selection_records` use unique `(build_profile_id, subject_id)` tuples for
  files and source regions.

Runtime EDU modes are not build profiles unless they later produce separate
firmware images. The obsolete per-node `build_selection` scalar is forbidden;
all profile-specific status comes from normalized records.

Every immutable release file has one file node carrying owner, source-relative
path, content hash, role, exact release identity, and presence class. Presence
is independent of compilation. `source-region` nodes refine selected files
when a disposition applies to a materially narrower fingerprinted span.

Statuses are `selected`, `excluded`, `available-not-selected`,
`not-applicable`, and `unresolved`. Causes use the closed versioned vocabulary
declared in the schema. Mechanical mechanism and reviewed architectural reason
remain separate cause records even when they support the same selection.

## Stable identity and evidence

IDs are typed, owner-qualified, and independent of line numbers. Examples:

```text
file:vdp-gl:src/fabutils.cpp
source-region:vdp-gl:src/fabutils.cpp:storage-vdp-gl-filebrowser-api
command:agon-vdp:vdu-22
build-profile:extender:p4-default
```

Line numbers belong to evidence. Source spans include file and span hashes so
upstream movement or edits invalidate stale review. Edge IDs derive
deterministically from `(from, relation, to)`; selection identity derives from
`(profile, subject)`.

`confirmed`, `strong`, `provisional`, and `unresolved` describe relationship
confidence. Reviewed evidence records their acceptance basis; reviewed intent
cannot contradict compiler or source evidence.

## Determinism and validation

Canonical YAML excludes timestamps and sorts every identity-bearing
collection. Generator path/version, exact argument vectors, source identities,
tool versions, and input hashes establish provenance.

Project validation requires, among other checks:

- exhaustive manifest/file-node equality and one file record per profile;
- globally unique IDs, edge tuples, and profile/subject tuples;
- mechanical causes for observed selections and accepted causes for target
  selections;
- accepted task/ADR references for exclusions;
- explicit observed-versus-declared drift;
- selected parents for source-region records;
- resolved evidence, graph, profile, subject, and replacement references; and
- matching input, source-tree, file, and span fingerprints.

Unresolved graph relationships remain ordinary visible analysis debt.
Unresolved source selection is stronger: it must remain visible and blocks
release or qualification until disposed.

## Slices and projections

A dependency slice copies a bounded set of graph nodes/edges and names the
canonical graph digest. Every omitted continuation encountered during traversal
is recorded as a boundary. Source-selection guides, query results, Markdown,
DOT, SVG, and merge-attention reports are deterministic projections, not
independent authorities.

The current generated VDU 22 slice under `../generated/commands/` is the schema
example exercised by the regression suite.
