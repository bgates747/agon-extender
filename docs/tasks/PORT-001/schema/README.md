# PORT-001 dependency artifact schema

Status: Accepted at Review Gate 1 on 2026-08-21; implemented for Review Gate 2.

The proposed system has three machine-readable artifact kinds:

1. `code_graph` — canonical merged structural and semantic graph;
2. `graph_overlay` — separately reviewed semantic edges and annotations; and
3. `dependency_slice` — self-contained bounded projection for one engineering
   question.

All are YAML documents validated against
[`dependency-artifacts.schema.json`](dependency-artifacts.schema.json). JSON
Schema is used only as the formal contract; canonical tracked instances remain
YAML for readable review and compact diffs.

## Authority

- The canonical graph is authoritative for graph structure.
- Reviewed overlays are authoritative for the explicit semantic claims they
  contain and retain their own evidence.
- Slices copy the selected nodes and edges from a named graph identity. They are
  reproducible review artifacts, not an independent source of graph facts.
- DOT, SVG, and Markdown views are disposable generated projections.

## Stable identity

Node IDs are human-readable, typed, and owner-qualified:

```text
command:agon-vdp:vdu-22
method:agon-vdp:VDUStreamProcessor::vdu_mode(uint8_t)
state:agon-vdp:screen-mode
protocol-packet:agon-vdp:mode-information
subsystem:agon-vdp:graphics-display
platform-api:arduino:Stream
physical-facility:esp32-pico:uart2
```

An ID changes when the represented engineering identity changes. Source line
numbers never form part of an ID. Overload signatures disambiguate symbols.
Edge IDs are deterministic readable slugs derived from source, relation, and
target; the validator also enforces uniqueness of that tuple.

## Determinism

Canonical output uses UTF-8, LF endings, two-space YAML indentation, quoted
ambiguous scalars, and these sort keys:

- sources, inputs, tools, evidence, nodes, and edges by `id`;
- annotations by target, namespace, and key;
- slice boundaries by source node, relation, and omitted target; and
- object keys in the order documented by the schema and emitter.

Generation time is deliberately excluded because it would make identical input
produce different output. Source commits, file and span fingerprints, generator
version, tool versions, input hashes, and exact argument vectors provide
reproducibility. A qualified run record may separately timestamp generation.

## Evidence and confidence

Evidence records are reusable first-class objects. Mechanical and reviewed
methods remain explicit. A graph edge cites one or more evidence IDs and assigns
one of three confidence levels:

- `confirmed` — directly established by compiler output, exact source, or
  reviewed control flow;
- `strong` — supported by evidence but contains bounded dispatch or semantic
  inference; and
- `tentative` — useful candidate requiring further review.

`strong` and `tentative` claims require a rationale. Mechanical extraction is
not automatically confirmed, and manual review is not automatically correct.

## Reviewed overlays

Mechanically generated graph data is never hand-edited. Reviewed overlays may:

- add semantic nodes absent from syntax-oriented indexes;
- add evidenced semantic edges;
- annotate existing nodes or edges under a namespaced key; and
- record a proposed or accepted port disposition with its decision reference.

The builder validates overlays against the selected source identities before
merging them. Namespaced annotations prevent port decisions, testing metadata,
and future qualification data from becoming unstructured top-level fields.

## Slices and boundaries

A dependency slice is self-contained but names its canonical source graph. Its
policy records traversal direction, admitted relations and node kinds, depth,
and explicit stop rules. Every omitted continuation encountered during traversal
becomes a boundary record. This prevents a small diagram from silently
misrepresenting a truncated dependency chain as complete.

See [`examples/representative-slice.yaml`](examples/representative-slice.yaml)
for an illustrative, non-source-derived output shape.
