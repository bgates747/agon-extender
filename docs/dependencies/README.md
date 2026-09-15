# Dependency and source-selection workflow

This is the durable project boundary promoted from PORT-001 and extended by
PORT-002. [`generated/code-graph.yaml`](generated/code-graph.yaml) is the sole
canonical machine-readable model. Reviewed source claims and accepted
SETUP-004 dispositions feed deterministic generators; generated guides,
queries, diagrams, and merge-attention reports are digest-bound projections.

The model distinguishes source presence, observed upstream build selection,
declared P4 target selection, narrower source-region seams, architectural
rationale, and upstream merge attention. Reviewed managed-import mappings in
`source-baselines.yaml` classify release trees as `vendored` only after the
generator verifies every repository copy byte-for-byte against its immutable
source root. `vendored-patched` additionally requires every differing path to
name its accepted decision; undeclared differences and stale byte-identical
patch declarations both fail regeneration. Canonical file nodes retain the
upstream and repository hashes plus paths so merge work can find either
representation.
Observed project-owned port seams are represented as Extender build units with
machine-evidenced dependencies. The compact source-selection projection lists
those units separately from immutable upstream file selections so a diagnostic
canary cannot be mistaken for an exhaustive production source profile.

## Inputs

Install `requirements-dev.txt` in `.venv`, then provide immutable roots matching
[`reviewed/source-baselines.yaml`](reviewed/source-baselines.yaml):

```text
AGON_VDP_SOURCE
VDP_GL_SOURCE
ESP32TIME_SOURCE
CRC_SOURCE
```

Git-backed roots must be at their recorded commits. Registry-package roots are
verified by exhaustive path/content manifests. Local paths appear only as
command arguments; tracked artifacts use placeholders.

## Regenerate

Use the orchestrator so the base graph, schema-2 enrichment, projections,
proof, VDU 22 slice, diagrams, and validators run in their defined order:

```sh
.venv/bin/python docs/dependencies/scripts/regenerate-dependencies.py \
  --source-root "agon-vdp=${AGON_VDP_SOURCE}" \
  --source-root "vdp-gl=${VDP_GL_SOURCE}" \
  --source-root "ESP32Time=${ESP32TIME_SOURCE}" \
  --source-root "CRC=${CRC_SOURCE}" \
  --check-deterministic
```

`mechanical-graph.yaml` and `base-code-graph.yaml` are ignored reproducible
intermediates. The tracked outputs are:

- `code-graph.yaml` — canonical graph, exhaustive manifests, profiles, regions,
  and normalized selection records;
- `source-selection.yaml` — complete query-oriented projection;
- `source-selection.md` — compact target-closure guide;
- `port-002-proof.yaml` — six accepted boundary cases;
- `commands/vdu-22.{yaml,md}` and `diagrams/vdu-22.{dot,svg}` — retained
  PORT-001 proof views; and
- `merge-attention/<old>--<new>.{yaml,md}` — created only when two independently
  validated official-tag graphs exist.

## Validate and test

```sh
.venv/bin/python -m unittest discover -s docs/dependencies/tests -v

.venv/bin/python docs/dependencies/scripts/validate-dependency-artifact.py \
  docs/dependencies/generated/code-graph.yaml --canonical
```

For full source verification, add `--verify-files` and one
`--source-root SOURCE-ID=PATH` per source. This checks tracked input digests,
exhaustive manifest counts and hashes, and every source-region span.

Project validation extends JSON Schema with tuple uniqueness, referential
integrity, complete per-profile file coverage, cause/evidence compatibility,
accepted exclusion references, explicit observed/declared drift, selected
region parents, and deterministic ordering. An `unresolved` selection is valid
analysis output but fails release qualification.

## Query and slice

`query-dependencies.py` filters by owner/path, profile, status, cause,
disposition, or graph proximity to any typed command, subsystem, packet, or
behavior node. It emits bounded canonical YAML and reports omitted results.

```sh
.venv/bin/python docs/dependencies/scripts/query-dependencies.py \
  docs/dependencies/generated/code-graph.yaml \
  --profile build-profile:extender:p4-default \
  --status excluded --path-contains DS3231 \
  --output /tmp/ds3231-selection.yaml
```

`slice-dependency-graph.py` remains seed-agnostic. Every continuation removed
by its depth, relation, node-kind, or explicit stop policy becomes a boundary;
YAML is authoritative over Markdown and Graphviz views.

## Review and extend

1. Change reviewed semantic claims only in `reviewed/claims.yaml`; never edit a
   generated graph.
2. Change dispositions in their authoritative task/ADR records. The selection
   generator consumes accepted SETUP-004 records directly rather than copying
   their prose into a second policy file.
3. Add a source-region only when a materially narrower reviewed boundary is
   needed. Record exact fingerprints and whether it is an exact boundary or a
   seam anchor; do not imply an upstream conditional already exists.
4. Regenerate, validate source identities and spans, inspect relevant bounded
   queries/slices, run tests, and require byte-identical regeneration.
5. Add a selection cause only by updating the closed schema vocabulary and its
   validator rules.

## Tagged upstream releases

Follow [`UPSTREAM-WATCH.md`](UPSTREAM-WATCH.md). Generate old and new graphs
independently from official tags. Pass the old graph to the new graph's
regeneration as `--prior-graph <old-code-graph.yaml>`; files absent from that
baseline default to `unresolved` until an accepted disposition classifies them.
Then run:

```sh
.venv/bin/python docs/dependencies/scripts/compare-tagged-releases.py \
  <old-code-graph.yaml> <new-code-graph.yaml> \
  --yaml docs/dependencies/generated/merge-attention/<old>--<new>.yaml \
  --markdown docs/dependencies/generated/merge-attention/<old>--<new>.md
```

Every changed file appears once in Tier A–D with all applicable reasons. New
files, selection drift, boundaries, public headers, build metadata, and
licenses receive mandatory Tier A review. Hash-equal moves are suggestions,
not invented rename identity.

## Numeric adaptation gate

Every VDP import must follow [numeric-upstream-import-r01](../procedures/numeric-upstream-import-r01.md).
Run the numeric regression entry point and reconcile its bounded review
fingerprints, then perform fresh compiler-backed conversion enumeration and
target/hardware validation. Hash updates alone do not satisfy review.
