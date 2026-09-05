# Compatibility qualification infrastructure

This directory is the durable traceability boundary promoted by QUAL-001. It
answers, for each accepted stock behavior or secondary Extender capability,
what owns it, where it applies, what blocks it, and what evidence supports the
exact claim.

The matrix does not define VDU/EDU syntax, protocols, wiring, operating modes,
procedures, or run outcomes. Those remain authoritative in their owning
documents. Qualification records link them without copying their contents.

[Staged circuit validation](staged-circuit-validation.md) owns the recurring
construction/test process accepted under PORT-008-D003. HW-001, QUAL-002, and
PORT-008 record bounded stage evidence before the complete release or mode
matrix exists. This does not promote the superseded matrix below or confer
untested compatibility; accepted stage evidence can later be linked to its
exact obligations.

## Authority and layout

`reviewed/` contains the human-reviewed semantic inputs:

- `sources.yaml` — referenced authorities and supporting records;
- `modes.yaml` — reviewed operating-mode vocabulary candidate;
- `interfaces.yaml` — one record for every accepted VDU inventory entry;
- `capabilities.yaml` — secondary Extender product capabilities;
- `qualification-domains.yaml` — compatibility-critical cross-cutting subjects;
- `mode-expectations.yaml` — one interface/mode expectation tuple;
- `obligations.yaml` — independently provable claims;
- `evidence.yaml` — evidence identities and lifecycle; and
- `evidence-links.yaml` — bounded relationships between evidence and claims.

The current mode records and their three-way expectation cross product are a
superseded Review Gate 2 candidate, not accepted vocabulary. ADR-0014 and
SETUP-005 now define Legacy, Exclusive Compatible, Exclusive Extended, and Dual
modes. QUAL-001-RG2-02R must correct and regenerate this data before mode
promotion; do not consume the old mode IDs as current architecture.

`generated/compatibility-matrix.yaml` is the sole canonical machine-readable
join. Every Markdown file under `generated/` is a deterministic projection and
must not be edited. `schema/` and `scripts/` define validation and generation;
`tests/` exercises structural, semantic, coverage, contradiction, and
determinism rules.

`generated/vdu-inventory.md` is the compact category-ordered replacement view
for the current task-local command list. It is not authoritative before Review
Gate 2.

Until QUAL-001 Review Gate 2 is accepted,
`docs/tasks/SETUP-004/VDU-inventory.md` remains the disposition authority and
`reviewed/interfaces.yaml` is an exact candidate import. The validator rejects
drift between them. Gate 2 may promote the YAML and replace the task-local list
with a generated view; that authority change is not implicit in generation.

## Regenerate and validate

Use the repository virtual environment:

```sh
.venv/bin/python docs/qualification/scripts/regenerate-qualification.py
.venv/bin/python docs/qualification/scripts/regenerate-qualification.py --check
.venv/bin/python -m unittest discover -s docs/qualification/tests -v
```

`--check` builds in a temporary directory and rejects any byte difference from
tracked generated files. It also verifies the exact pre-Gate-2 VDU import.

## Maintenance contract

1. Change accepted behavior first in its owning task or ADR.
2. Update reviewed YAML; never edit generated output.
3. Keep interface disposition, mode expectation, implementation state,
   qualification state, and evidence lifecycle independent.
4. Link evidence to the narrow claim it supports. Evidence never advances a
   row to `qualified` automatically.
5. Keep compatibility-critical and secondary-capability evidence separate.
6. Preserve rejected and superseded evidence as traceable records.
7. Regenerate, validate, inspect bounded views, and require deterministic
   output before review or commit.

Stable IDs must not contain line numbers, mutable titles, implementation owners,
or status. Accepted IDs are immutable; a materially different contract receives
a new ID and an explicit supersession record.
