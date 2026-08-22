# PORT-003 Review Gate 1 package

This directory contains bounded evidence and design material for the P4 display
backend. [`../PORT-003.md`](../PORT-003.md) is the authoritative task and scope
fence. Nothing here authorizes production implementation.

## Structure

- `PROPOSAL.md` — integrated Review Gate 1 design, alternatives, decisions
  requested, implementation phases, and stop gate.
- `display-behavior.md` — source-grounded retained behavior and lifecycle trace.
- `platform-feasibility.md` — pinned P4 framework facilities, constraints, and
  unqualified assumptions relevant to the accepted boundary.
- `qualification-plan.md` — deterministic host fixtures and later target tests.
- `scripts/` — task-local deterministic evidence generators.
- `generated/` — machine-readable evidence plus reproducible compact views and
  diagrams. Generated files identify their generator and must not be edited by
  hand.

## Authority

The canonical dependency graph remains `docs/dependencies/generated/code-graph.yaml`.
Generated task evidence is a digest-bound projection, not another dependency
authority. Source facts cite immutable official VDP `v2.16.0` or pinned
dependency paths. Proposals remain non-normative until the Author accepts them
and the accepted result is promoted through the project's decision process.

## Regeneration and validation

One task-local command regenerates all machine evidence and validates graph
provenance, tuple uniqueness, source locations, deterministic ordering, and
required display-boundary coverage:

```sh
.venv/bin/python docs/tasks/PORT-003/scripts/regenerate.py \
  --agon-vdp-root <official-v2.16.0-checkout> \
  --vdp-gl-root <that-checkout>/.pio/libdeps/esp32dev/vdp-gl \
  --p4-framework-root <pioarduino-architecture-libs-package> \
  --check-deterministic
```

Host-side design fixtures and target qualification procedures remain separate:
an analysis artifact cannot establish runtime correctness.
