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
    ├── analysis_model.py
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
source inspection when implementation details matter. Work 1.a has passed the
mechanical and reviewed-evidence audit, and all 13 candidate dispositions have
completed Author review. Named follow-on tasks retain deferred implementation,
qualification, and architectural work.

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
.venv/bin/python docs/tasks/SETUP-004/scripts/extract-work-item.py \
  --work-item SETUP-004.1.a
.venv/bin/python docs/tasks/SETUP-004/scripts/audit-work-item.py \
  --work-item SETUP-004.1.a
.venv/bin/python docs/tasks/SETUP-004/scripts/generate-subsystem-inventory.py
```

The extractor verifies immutable source identities and exact source-file
hashes, discovers and assigns scoped evidence, and emits exhaustive mechanical
facts. The audit validates residual coverage, reviewed-field completeness,
target-framework evidence, decision dependencies, and removal fallout. The
projection generator accepts only passing, current audits; it rejects stale
input hashes or mismatched mechanical/reviewed candidate sets and preserves the
two layers separately. Output ordering and input fingerprints are
deterministic.
