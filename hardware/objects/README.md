# Hardware object authority

This directory is the durable project authority for role-descriptive hardware
object names, classifications, aliases, and containment. It answers **what an
object is** independently of a particular wiring revision, physical specimen,
bench location, test run, or ERP record.

The machine-readable authority is [`objects.yaml`](objects.yaml). Its structural
contract is [`schema.json`](schema.json), and the project validator adds
collection-wide checks that JSON Schema cannot express.

The current authority identity is `hardware-object-registry-r01`, with `draft`
status. Its lineage and latest identity are registered in
`docs/versions/artifacts.yaml`; status and identity in that registry and the
machine-readable authority must agree.

The initial 41-object vocabulary was synthesized from the accepted SETUP-006.1
discovery inventory and naming review. Those task files remain provenance, not
a second maintained object list.

## Authority boundary

The object authority owns:

1. one unique lowercase `object_id` for each durable role;
2. one human-readable label and description;
3. product, prototype, bench, measurement, proposed-product, and context
   domains;
4. reusable object classes and containment relationships;
5. searchable legacy aliases; and
6. links to related project artifact lineages where they already exist.

It does **not** own:

1. pins, nets, wire colors, connector terminals, component values, or
   electrical connectivity;
2. artifact versions or revisions, lifecycle status, physical specimen IDs,
   build IDs, baselines, or test runs;
3. current machine-local bench attachment or power state;
4. Odoo Product, Internal Reference, External ID, lot, serial, BoM, or ECO
   identities; or
5. unresolved protocol, operating-mode, or firmware behavior.

Electrical connectivity remains part of a controlled design revision under
`hardware/designs/<identity>/`. Measurement attachment remains part of a
controlled fixture revision under `hardware/fixtures/<identity>/`. This split
prevents a global vocabulary edit from silently changing the meaning of a
historical harness, fixture, baseline, or qualification run.

Machine-local specimen identity and current bench state remain in ignored local
records as required by the project handoff. ERP exports, when introduced, must
derive stable mappings from this authority and the applicable revisioned design;
they must not become a competing source of electrical truth.

## Change control

Adding, removing, merging, splitting, or redefining an object is a reviewed
semantic change to this authority. Changing only a legacy alias or correcting
wording without changing object meaning is editorial. Neither operation
silently increments a hardware design or fixture revision; any affected
revisioned artifact must be reviewed independently under
`docs/versions/README.md`.

Objects are sorted lexicographically by `object_id`. A `parent_object_id` is a
containment relationship, not an electrical connection. `related_artifact_ids`
are cross-references to the version registry, not assertions that the object is
identical to, wholly governed by, or qualified with that artifact.

## Validation

From the repository root, using the project virtual environment:

```text
.venv/bin/python scripts/validate-hardware-objects.py
```

Validation checks the JSON Schema, identifier and alias uniqueness, deterministic
ordering, parent existence and acyclicity, and references to registered artifact
IDs.
