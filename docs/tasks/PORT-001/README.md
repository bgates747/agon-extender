# PORT-001 dependency graph workflow

This directory contains the task-local implementation approved at Review Gate
1. The tracked canonical artifact is `generated/code-graph.yaml`. Reviewed
semantic claims remain separately auditable in `reviewed/`, and bounded YAML
slices are authoritative over their Markdown and Graphviz projections.

## Prerequisites

Install the pinned development dependencies into the project virtual
environment:

```sh
.venv/bin/pip install -r requirements-dev.txt
```

Provide immutable source roots matching
[`reviewed/source-baseline.yaml`](reviewed/source-baseline.yaml). The commands
below assume these shell variables have already been assigned outside tracked
project files:

```text
AGON_VDP_SOURCE
VDP_GL_SOURCE
ESP32TIME_SOURCE
CRC_SOURCE
```

The builder rejects Git-backed source roots whose current commits do not match
the reviewed baseline. Registry packages are verified by deterministic source
tree fingerprints.

## Regenerate the graph

```sh
.venv/bin/python docs/tasks/PORT-001/scripts/build-code-graph.py \
  --setup-root docs/tasks/SETUP-003 \
  --baseline docs/tasks/PORT-001/reviewed/source-baseline.yaml \
  --source-root "agon-vdp=${AGON_VDP_SOURCE}" \
  --source-root "vdp-gl=${VDP_GL_SOURCE}" \
  --source-root "ESP32Time=${ESP32TIME_SOURCE}" \
  --source-root "CRC=${CRC_SOURCE}" \
  --reviewed-claims docs/tasks/PORT-001/reviewed/claims.yaml \
  --output-dir docs/tasks/PORT-001/generated
```

The builder produces:

- `mechanical-graph.yaml` — ignored full intermediate rebuilt on demand;
- `reviewed-overlay.yaml` — normalized reviewed claims and annotations; and
- `code-graph.yaml` — authoritative merged graph.

The mechanical intermediate is deliberately ignored because retaining it would
duplicate nearly the entire merged graph. Its digest remains in the overlay and
merged graph and is reproducible from the recorded inputs.

## Validate

Run the task tests:

```sh
.venv/bin/python -m unittest discover -s docs/tasks/PORT-001/tests -v
```

Validate structure and canonical form:

```sh
.venv/bin/python docs/tasks/PORT-001/scripts/validate-dependency-artifact.py \
  docs/tasks/PORT-001/generated/code-graph.yaml --canonical
```

For qualification, add `--verify-files` and one `--source-root
SOURCE-ID=PATH` argument for each source ID. This verifies input and graph
digests, every source span, and the reconstructed source-tree fingerprints.
Overlay validation additionally names the regenerated mechanical graph through
`--base-graph`.

## Query and slice

The slicer accepts any node ID; it is not limited to VDU commands. Select seeds,
directions, relationship kinds, node kinds, maximum depth, and explicit stop
rules. Every encountered continuation excluded by those rules becomes a
boundary record.

The first proof invocation is recorded exactly in
[`generated/commands/vdu-22.yaml`](generated/commands/vdu-22.yaml) under
`generator.argv`. Use that vector as the reproducible example rather than
copying it into another independently maintained command block.

Render any slice with:

```sh
.venv/bin/python docs/tasks/PORT-001/scripts/render-dependency-slice.py \
  <slice.yaml> --markdown <review.md> --dot <view.dot> --svg <view.svg>
```

YAML remains authoritative. Markdown and diagrams are disposable deterministic
projections.

## Review and extend

1. Inspect mechanically confirmed and strong relationships separately.
2. Treat every `unresolved` record and explicit boundary as visible analysis
   debt, not as an absent dependency.
3. Add semantic conclusions to `reviewed/claims.yaml` with exact source
   evidence; do not edit generated graphs.
4. Regenerate, validate all fingerprints, inspect the bounded slice, and run
   deterministic regeneration before accepting the claim.
5. Put project decisions in namespaced annotations with a task or ADR
   reference. Do not convert source facts into port dispositions implicitly.

## Upstream comparison

For a new tagged VDP release, first produce the corresponding SETUP structural
evidence and a new reviewed immutable source baseline. Generate the new graph
under a separate output directory and compare normalized node IDs, edge tuples,
unresolved records, reviewed evidence validity, and selected-build status. IDs
that survive source movement remain comparable because line numbers are
evidence rather than identity. Review changed or stale overlay claims before
making the new graph authoritative.

The present baseline is intentionally immutable. The builder must never be
temporarily pointed at a moving branch to perform an upstream comparison.

## Future metadata

Tests, builds, qualification runs, and releases may be represented later as
typed nodes and namespaced annotations. Do not add those relationships until
their authoritative project records exist. A generated SQLite index may be
added for large queries, but it must remain disposable and reproducible from
validated YAML.

