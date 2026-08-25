# SETUP-006 working directory

This directory is the bounded working area for SETUP-006 inventories, source
extracts, provisional structured data, diagram generators, draft diagrams, and
review evidence. It is not a permanent hardware authority.

Accepted recurring definitions will be promoted or synthesized into a
role-named location under `hardware/`. Historical evidence and task-specific
review records may remain here after promotion.

## Current contents

1. [`SETUP-006.1.1-object-inventory.md`](SETUP-006.1.1-object-inventory.md) —
   bounded discovery inventory using temporary row keys, before durable object
   names or a permanent schema are selected.
2. [`SETUP-006.1.1-reset-breakout-observation.md`](SETUP-006.1.1-reset-breakout-observation.md)
   — exact operator-reported placement, geometry, colors, and suspected wiring
   problem, recovered alternate configurations, and bounded visual trace.
3. [`SETUP-006.1.2-naming-register.md`](SETUP-006.1.2-naming-register.md) —
   accepted naming review provenance, legacy aliases, ownership domains,
   containment, and logical-versus-physical boundaries. The maintained names
   have been promoted to `hardware/objects/objects.yaml`.
4. [`SETUP-006.3-fritzing/`](SETUP-006.3-fritzing/) — accepted canonical
   mechanical and diagrammatic breadboard scaffold for subsequent wiring
   design. It is intentionally unwired and remains task-local until the
   electrical design establishes its permanent artifact boundary.

## Promoted output

The maintained hardware role vocabulary, schema, and authority boundary now
live under `hardware/objects/`. Its routine validator is
`scripts/validate-hardware-objects.py`. SETUP-006 task files remain discovery
and review provenance and must not become a competing maintained authority.
