# Manifest Field Guide

All version records use YAML schema version `1`. Templates are authoritative
for structure; this guide states the meaning of fields shared across records.

## Common identity fields

- `artifact_id`: Stable lineage name registered in `artifacts.yaml`.
- `identity`: Full artifact ID plus semantic version or revision.
- `source_identity`: Version/revision from which a build was produced.
- `build_id`: Source identity plus UTC build timestamp.
- `variant`: Parallel form selected for this record, or `null`.
- `status`: Lifecycle state defined by the versioning policy.
- `sha256`: Full lowercase 64-digit digest of the exact file bytes.

## Compatibility requirement

Each entry under `requires` has `artifact_id`, optional `variant` and `reason`,
and exactly one of:

```yaml
exact: artifact-r01
```

```yaml
one_of:
  - artifact-r01
  - artifact-r03
```

```yaml
version_range:
  minimum: v1.2.0
  before: v2.0.0
```

`minimum` is inclusive and `before` is exclusive. Revision ranges are invalid;
list physical revisions explicitly.

## Build manifest

`provenance` identifies the repository, complete commit ID, dirty state,
optional reproducible-build epoch, toolchain versions, and exact configuration
artifacts. Each output records filename, media type, byte size, and SHA-256.

## Baseline manifest

`compatibility_scope` says what the combination is approved to do. `artifacts`
selects exact identities/builds. `external_dependencies` records upstream or
purchased identities. `qualification.run_ids` supplies evidence.

## Run manifest

`outcome` records execution result independently of artifact status. A run
selects the exact procedure, artifacts, base hardware profiles, reusable
connections, instrumentation, external dependencies, observations, and
evidence. Irrelevant optional sections may be removed; relevant unknown fields
remain explicit `null` until resolved.

Private specimen details are never copied into tracked manifests. A
`specimen_alias` or `equipment_alias` is meaningful through the ignored local
bench inventory.
