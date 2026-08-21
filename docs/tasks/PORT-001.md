# PORT-001 — Build the VDU-to-EDU dependency graph system

## State

- Status: Complete
- Started: 2026-08-21 01:03 EDT
- Finished: 2026-08-21 02:07 EDT

## Intent

Build a reusable, deterministic dependency-graph system that supports the port
of retained official VDU behavior into the EDP and EDU architecture. The system
must answer what each command depends upon, what state and externally visible
behavior it affects, what platform facilities it reaches, and what must be
retained, replaced, adapted, stubbed, or qualified.

The graph is continuing engineering infrastructure, not a one-time survey
artifact. It must remain useful for implementation, upstream release updates,
impact analysis, testing, debugging, review, and production qualification. No
command is predetermined as the first proof slice; select a representative seed
after reviewing the schema and available evidence.

## Inputs

- [SETUP-003 structural inventory](SETUP-003.md) and its deterministic outputs
  under `SETUP-003/generated/`.
- [SETUP-004 VDU compatibility inventory](SETUP-004/VDU-inventory.md).
- Official VDP release `v2.16.0` at
  `c7ac293d2aa81ddfa693390549bcd909069c8fc3`.
- vdp-gl tag `all-the-plots` at
  `ac2dd5986daf496c43ae8e7fe41836274aec54a0`.
- The selected compilation database, compiler dependency evidence, symbol
  index, portability inventory, and reviewed semantic relationships.

## Work

1. [x] Define a versioned canonical graph schema with stable typed node IDs, typed
   edges, source ownership, exact evidence locations, source identities,
   confidence, and mechanical-versus-reviewed provenance.
2. [x] Implement a deterministic graph builder that combines actual build
   selection, compiler-derived include data, indexed symbols, token-aware call
   and state-reference extraction, and a small explicit layer of reviewed
   semantic edges.
3. [x] Model at least commands, parser dispatches, functions and methods, files,
   types, globals and persistent state, callbacks, tasks, protocol packets,
   subsystems, platform APIs, and physical facilities. Use relationships such
   as `dispatches-to`, `calls`, `reads`, `writes`, `owns`, `resets`,
   `invokes-callback`, `sends-packet`, `depends-on`, and `requires-hardware`.
4. [x] Implement a general command/symbol slicer that emits bounded direct and
   transitive dependency views. Record explicit traversal boundaries rather
   than silently truncating large dependency chains.
5. [x] Implement deterministic renderers for compact Markdown review tables and
   Graphviz views. The canonical machine-readable graph remains authoritative;
   diagrams are generated projections.
6. [x] Implement validation for schema consistency, dangling edges, duplicate IDs,
   stale source evidence, unresolved symbols, source-identity mismatch, and
   deterministic regeneration.
7. [x] Select, generate, and manually validate a representative first command slice.
   Choose a seed that exercises the graph usefully without requiring unresolved
   architecture to be invented. Report dispatch, execution, state mutation,
   callbacks, packets, resources, platform and hardware dependencies, and
   port-disposition impact separately.
8. [x] Document regeneration, query, review, and upstream-version comparison
   workflows. Define how later test, build, and qualified-release relationships
   can be added without prematurely encoding systems that do not yet exist.

## Durable layout

Task-local implementation and initial outputs live under:

```text
docs/tasks/PORT-001/
├── scripts/
├── schema/
├── reviewed/
└── generated/
    ├── code-graph.yaml
    ├── commands/
    └── diagrams/
```

If the system is accepted for continuing production use, promote its scripts,
schema, and maintenance documentation to an appropriately named durable project
tool boundary. Do not place one-off extraction scripts in the repository's
top-level `scripts/` directory.

## Requirements

- Use only selected tagged upstream source and its exact dependency identities.
- Record tool versions, generator version, input identities, and exact
  regeneration commands.
- Keep machine-local paths and transient build locations out of tracked output.
- Prefer mechanically regenerated structural relationships; keep reviewed
  semantic edges few, explicit, evidenced, and independently auditable.
- Never treat filename proximity or textual name similarity as proof of a
  dependency.
- Distinguish code available in vendored source from code selected into the EDP
  build.
- Preserve upstream source unchanged while extracting and validating evidence.
- Keep generated views compact enough to answer a specific engineering question
  without requiring interpretation of one firmware-wide diagram.

## Review Gate 1

- [Graph and slice proposal](PORT-001/schema/PROPOSAL.md)
- [Schema contract and conventions](PORT-001/schema/README.md)
- [Formal JSON Schema](PORT-001/schema/dependency-artifacts.schema.json)
- [Illustrative dependency slice](PORT-001/schema/examples/representative-slice.yaml)

Status: approved by the Author on 2026-08-21. YAML remains authoritative;
project validation enforces graph-wide constraints; SQLite may later be a
disposable generated query index but not a second source of truth.

## Review Gate 2

- [Implementation and maintenance workflow](PORT-001/README.md)
- [First proof review](PORT-001/proof-vdu-22.md)
- [Authoritative VDU 22 proof slice](PORT-001/generated/commands/vdu-22.yaml)
- [Compact Markdown projection](PORT-001/generated/commands/vdu-22.md)
- [SVG projection](PORT-001/generated/diagrams/vdu-22.svg)

Status: approved by the Author on 2026-08-21. The validated task-local system
and first proof complete PORT-001. Promotion into a continuing project tool
boundary and future test/build/release relationships remain separate follow-on
work.

## Review gates

1. Stop after proposing the graph schema, evidence model, and representative
   command-slice output shape. Obtain Author approval before implementing the
   full builder.
2. Stop after generating and explaining the validated first proof slice.
   Obtain Author approval before promoting the system into continuing project
   infrastructure or adding test/build/release relationships.
