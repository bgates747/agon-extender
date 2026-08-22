# PORT-003 Phase C — Logical frame service

[`../../PORT-003.md`](../../PORT-003.md#phase-c--logical-frame-service) is the
authoritative checklist and scope fence. This directory owns Phase C's bounded
provenance, independent event-trace fixtures, host concurrency harnesses,
target qualification procedure, generated evidence, and gate validators.
Production frame-service code remains under `vdp/video/extender/display/`;
recurring P4 build selection remains under `vdp/pio/`.

## Structure

```text
phase-c/
├── README.md
├── contracts.md
├── compatibility-delta.md
├── implementation-manifest.yaml
├── evidence/                 # generated host and target closure records
├── fixtures/                 # independent written-contract traces
├── scripts/                  # deterministic extractors, runners, validators
└── tests/                    # host harnesses and permanent generator tests
```

Generated evidence must identify its generator, frozen inputs, and content
hashes. Host traces use a deterministic injected clock/scheduler; target
cadence evidence uses only a committed and versioned firmware artifact. The
host model and production state machine must not generate each other's
expected results.

`compatibility-delta.md` is the human review surface for retained behavior,
project-owned implementation, the accepted patched-vendor seam, and deferred
or excluded behavior. `implementation-manifest.yaml` is the machine-readable
scope authority consumed by Phase C validation and later source-selection
work. Generated files are never hand-edited.

Physical qualification follows the controlled
[`p4-frame-service-qualification-r01`](../../../procedures/p4-frame-service-qualification-r01.md)
procedure after all candidate inputs are committed and the worktree is clean.

## Gate boundary

Phase C owns logical ticks, task-context frame work, primitive/swap completion,
frame count, publication generation, and bounded mock-consumer notification.
It does not own presentation composition, palette/Copper/overlays, an official
mode facade, an output sink, or EDU/VDU routing.
