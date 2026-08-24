# PORT-003 Phase D — Palette, Copper, and overlays

[`../../PORT-003.md`](../../PORT-003.md#phase-d--palette-copper-and-overlays)
is the authoritative checklist and scope fence. This directory owns Phase D's
bounded source provenance, independent presentation fixtures, host harnesses,
diagnostic target-closure evidence, and gate validators. Production code stays
under `vdp/video/extender/display/`; recurring P4 build selection stays under
`vdp/pio/`.

## Structure

```text
phase-d/
├── README.md
├── contracts.md
├── compatibility-delta.md       # reviewed result, added during implementation
├── implementation-manifest.yaml
├── evidence/                    # generated provenance, host, and build records
├── fixtures/                    # independent palette/composition expectations
├── scripts/                     # deterministic extractors, models, runners
└── tests/                       # host harnesses and permanent generator tests
```

Generated files identify their generator, frozen inputs, and content hashes.
The fixture generator models the written/source-derived contract and must not
import production headers, invoke production binaries, or parse production
output. Production output is compared with the fixtures only by the host
runner.

Phase D owns palette/Copper state and one sink-neutral composition algorithm.
It may offer a synchronous quiescent controller seam for qualification, but it
does not expose a mutable frame pointer or freeze a sink/lease contract. Phase
F owns bounded generation access and consumer handoff; physical sinks remain
separate tasks.

After every completed numbered checklist item, reread `TODO.md`, the Phase D
section of `PORT-003.md`, and the implementation/gate section of
`qualification-plan.md` before beginning the next item.

## Commit boundary

Phase D ends in one coherent commit containing production palette/compositor
code, host fixtures and evidence, diagnostic target selection/closure,
dependency/provenance updates, the compatibility delta, task completion, and
the development-log record. No unqualified binary, physical run, or Phase E
facade work belongs in that commit.
