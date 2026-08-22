# SETUP-004 subsystem disposition workspace

The canonical task is [`../SETUP-004.md`](../SETUP-004.md). This directory
separates reviewed source evidence, deterministic agent-facing inventory, and
the compact human review projection.

## Layout

```text
SETUP-004/
├── README.md
├── ANALYSIS-PROCESS.md
├── VDU-inventory.md
├── disposition-matrix.md
├── scope/
│   └── work-<item>.yaml
├── evidence/
│   └── work-<item>-<subject>.yaml
├── generated/
│   ├── work-<item>/
│   │   ├── candidates.yaml
│   │   ├── mechanical-facts.yaml
│   │   └── coverage.yaml
│   └── subsystem-inventory.yaml
└── scripts/
    ├── extract-work-item.py
    ├── audit-work-item.py
    └── generate-subsystem-inventory.py
```

- `ANALYSIS-PROCESS.md` defines candidate discovery, mechanical extraction,
  semantic review, coverage auditing, disposition, and acceptance for every
  Work 1 item.
- `scope/` contains the reviewed inclusion rules, seed facilities, terminology,
  and explicit exclusions for one Work 1 item. It bounds extraction but does
  not contain conclusions.
- `evidence/` contains bounded, manually reviewed interpretations layered over
  mechanical output. Source claims cite validated PORT-001 evidence and graph
  identities rather than machine-local paths.
- `generated/work-<item>/` contains candidate discovery, mechanically derived
  facts, and residual-coverage results. These files are regenerated rather
  than edited.
- `generated/subsystem-inventory.yaml` is the normalized machine-readable
  inventory. It is the preferred agent index for finding relevant code and
  dependency-graph entry points. Do not hand-edit it.
- `disposition-matrix.md` is the generated compact review view. It summarizes
  the same records without replacing the evidence files or generated YAML.
- `scripts/` contains task-local deterministic generation and validation. It
  does not belong in the repository's top-level routine build/deployment
  scripts.

The official tagged source, PORT-001 graph, and existing project decisions
remain authoritative. This inventory narrows source review; it does not replace
source inspection when implementation details matter. The present Work 1.a
evidence and projections predate the complete extraction design and are
preliminary inputs, not proof that Work 1.a is complete.

## Record lifecycle

Every material candidate receives exactly one provisional disposition:
`retain`, `replace`, `stub`, `omit`, or `defer`. A record's scope must separate
the framework or physical implementation from any externally visible behavior
that must survive its removal.

1. Approve or revise the bounded `scope/work-<item>.yaml` input.
2. Generate candidates and mechanical facts from SETUP-003 and PORT-001.
3. Resolve or explicitly retain extraction gaps reported by the coverage audit.
4. Add bounded reviewed interpretations and provisional dispositions under
   `evidence/`.
5. Regenerate and inspect the aggregate inventory and review projection.
6. Present provisional dispositions to the Author by subsystem group.
7. After approval, update the task, applicable ADRs, architecture, and dated
   development log. Do not encode open decisions in an ADR.

## Regenerate

From the project root:

```sh
.venv/bin/python docs/tasks/SETUP-004/scripts/generate-subsystem-inventory.py
```

The currently implemented projection generator validates reviewed record
fields, unique candidate IDs, disposition vocabulary, Work 1 item IDs,
PORT-001 evidence and graph-node references, and source identities. It does not
perform the discovery or coverage-audit stages specified in
`ANALYSIS-PROCESS.md`; those scripts must exist before any Work 1 item can be
closed. Output ordering and input fingerprints are deterministic.

