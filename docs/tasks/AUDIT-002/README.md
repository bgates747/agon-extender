# AUDIT-002 working directory

This directory contains the bounded extractor, expected-circuit manifest,
generated connectivity evidence, and findings for AUDIT-002. These files audit
the task-local SETUP-006 wiring draft; they do not become a competing hardware
authority or qualify the physical bench.

## Files

1. `extract-fritzing-connectivity.py` deterministically resolves recorded
   sketch connectivity and bundled custom-part buses without inferring wires
   from graphical overlap.
2. `generated/connectivity.json` is the machine-readable extracted graph.
3. `generated/connectivity.md` is its compact human review rendering.
4. `expected-circuit.json` is the evidence-derived named-net, component-value,
   isolation, supply-separation, and structural contract used to judge the
   drawing. External source references identify the repository and relative
   path without embedding machine-local filesystem topology.
5. `compare-fritzing-connectivity.py` resolves the manifest's durable endpoint
   names against the extracted graph and emits a deterministic pass/fail
   comparison without depending on Fritzing's generated net labels.
6. `generated/comparison.json` and `generated/comparison.md` are the structured
   and compact rendered comparison.
7. `findings.md` records the initial defects, evidence-backed corrections,
   final validation, and the limits of the resulting claim.

## Regeneration and validation

Run from the repository root:

```sh
.venv/bin/python docs/tasks/SETUP-006/SETUP-006.4-wiring-design/make-draft-v1.py
.venv/bin/python docs/tasks/AUDIT-002/extract-fritzing-connectivity.py
.venv/bin/python docs/tasks/AUDIT-002/compare-fritzing-connectivity.py
```

Use each script's `--check` option to require current deterministic outputs;
the comparison checker also exits nonzero if any circuit-contract check fails.
