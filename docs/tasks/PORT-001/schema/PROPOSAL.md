# PORT-001 Review Gate 1 — Graph and slice proposal

Status: Approved by the Author on 2026-08-21.

## Outcome

Use a versioned property graph as the durable project model. Store canonical
instances as deterministic YAML, validate them with a formal JSON Schema and
project-specific referential checks, and generate bounded self-contained slices
for engineering review. Do not make diagrams or Markdown tables authoritative.

## Why this shape

SETUP-003 already provides trustworthy but separate evidence classes:

- build-selected translation units and compiler dependency closure;
- direct include records and unresolved external includes;
- Ctags symbols;
- mechanically extracted platform, protocol, global, and conditional records;
- manually reviewed subsystem ownership and semantic edges; and
- source-validated runtime entry relationships.

A single syntax-derived call graph would discard important ownership and
hardware meaning. A manually maintained graph would rot. The proposed model
therefore merges mechanical and reviewed relationships while preserving the
method, evidence, confidence, and source identity of every claim.

## Expected review burden

The builder should eliminate repeated mechanical source reading, not pretend
that syntax proves behavior. It can generate broad candidate relationships from
the selected build, compiler dependencies, symbols, source tokens, and explicit
dispatch tables. Agent review remains necessary for indirect dispatch,
macro-mediated behavior, state ownership, callbacks, platform consequences,
and other semantic claims the evidence cannot establish unambiguously.

Those conclusions are recorded once in reviewed overlays. Subsequent slices
reuse them and should require focused review only for unresolved relationships,
changed source evidence, or newly reached graph regions. A usable Clang AST and
compilation database may reduce this review burden, but cannot remove it.

## Artifact boundaries

### Canonical graph

`code_graph` contains the complete normalized node and edge set for one selected
source/build identity. It is regenerated, never hand-edited.

### Reviewed overlay

`graph_overlay` contains semantic nodes, semantic edges, and namespaced
annotations that tools cannot safely infer. The builder validates each source
span and referenced graph identity before merging it. Port dispositions belong
here under keys such as `port.disposition` and retain their task or ADR decision
reference.

### Dependency slice

`dependency_slice` is a self-contained subset selected from a canonical graph.
It records its seed, traversal policy, grouping, explicit truncation boundaries,
unresolved relationships, source graph digest, and copied evidence. This makes
the slice independently reviewable while remaining reproducible from the graph.

## Important design choices

1. **Human-readable stable IDs:** IDs use type, owner, and engineering identity;
   source lines are evidence, never identity.
2. **Typed vocabulary:** Node kinds and edge relations are closed and versioned.
   New vocabulary requires a reviewed schema change rather than ad hoc strings.
3. **Evidence as data:** Multiple nodes and edges may cite one evidence record.
   Exact source spans carry file and span SHA-256 fingerprints to detect stale
   references even when a path and line number still exist.
4. **Confidence is independent of method:** Mechanical results can be ambiguous;
   reviewed conclusions can remain tentative. Non-confirmed edges explain why.
5. **Build selection is explicit:** Available vendored code is distinguishable
   from selected build input and external facilities.
6. **Semantic overlays remain separate:** Regeneration cannot erase reviewed
   conclusions or quietly turn judgment into mechanical fact.
7. **Every truncation is visible:** A slice boundary names the omitted target,
   triggering relation, stop rule, and optional continuation slice.
8. **No generation timestamp in canonical data:** Identical inputs produce
   byte-identical output. Qualified run records provide chronology separately.
9. **Self-contained slices:** Review does not require loading the full graph,
   but the source graph identity prevents slices from becoming orphan facts.
10. **Extensible without schema pollution:** Test, port, and qualification data
    use namespaced properties or reviewed annotations; they do not acquire
    arbitrary top-level fields.

## Required validation beyond JSON Schema

The eventual validator must enforce rules JSON Schema cannot express compactly:

- unique IDs in every collection;
- unique `(from, relation, to)` edge tuples;
- all edge endpoints, evidence IDs, seed IDs, group IDs, and annotation targets
  resolve;
- all source IDs and input artifact IDs resolve;
- source spans have `start_line <= end_line` and match file/span fingerprints;
- arrays obey canonical sort order;
- node ID type prefixes agree with `kind`;
- declared vocabulary equals the schema vocabulary used by the generator;
- selected-build claims agree with compilation evidence;
- overlay source and target-graph identities match exactly;
- slice contents are a faithful subset of the named graph plus visible boundary
  records; and
- regeneration produces byte-identical canonical YAML.

The current project virtual environment includes PyYAML but not a JSON Schema
validator. After this proposal is accepted, the recommended implementation is
to pin Python's `jsonschema` package for standards-compliant schema checks and
retain a small project validator for the graph-specific rules above. Rewriting
JSON Schema semantics locally would add risk without adding project value.

## Proposed initial implementation sequence

After approval of this gate:

1. implement schema and referential validation without graph extraction;
2. normalize SETUP-003 files, symbols, includes, and reviewed subsystem edges
   into the graph;
3. add token-aware direct call and state-reference extraction with unresolved
   candidates retained rather than guessed;
4. implement deterministic overlay merge;
5. implement general slicing and boundary capture;
6. choose a representative proof seed from SETUP-004's pending disposition
   questions;
7. validate the proof slice manually; and
8. add Markdown and Graphviz renderers only after the graph and slice are
   trusted.

## Approved Review Gate 1 questions

1. Approve YAML as canonical tracked form with JSON Schema plus stronger local
   validation?
2. Approve the three-artifact boundary: graph, reviewed overlay, and slice?
3. Approve human-readable typed IDs and closed versioned vocabularies?
4. Approve source/file/span fingerprints and omission of generation timestamps
   from canonical output?
5. Approve explicit slice stop rules and boundary records as mandatory?
6. Approve choosing the first proof seed only after the builder exposes which
   SETUP-004 boundary will test the model most usefully?
7. Approve pinning `jsonschema` as a development dependency while keeping
   graph-specific referential checks in project code?
