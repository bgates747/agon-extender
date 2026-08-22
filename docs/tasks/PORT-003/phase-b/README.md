# PORT-003 Phase B — Native storage and synchronous renderer

[`../../PORT-003.md`](../../PORT-003.md#phase-b--native-storage-and-synchronous-renderer)
is the authoritative checklist and scope fence. This directory owns Phase B's
bounded provenance extraction, independent fixtures, generated evidence, and
gate validators. Production display code remains under
`vdp/video/extender/display/`; recurring VDP build selection remains under
`vdp/pio/`.

## Structure

```text
phase-b/
├── README.md
├── compatibility-delta.md
├── implementation-manifest.yaml
├── evidence/
│   ├── algorithm-provenance.yaml
│   ├── host-fixture-results.yaml
│   ├── allocation-failure-results.yaml
│   ├── build-closure.yaml
│   └── link-exclusions.yaml
├── fixtures/
│   ├── native-codecs.yaml
│   └── primitives.yaml
├── scripts/
│   ├── extract-algorithm-provenance.py
│   ├── generate-fixtures.py
│   ├── run-host-fixtures.py
│   └── validate-phase-b.py
└── tests/
    ├── compat/
    └── renderer_fixture_tests.cpp
```

The exact file set may contract after item 2 reveals the natural durable
boundaries, but generators, independent oracles, results, and compatibility
claims must remain distinguishable. Generated files name their generator and
input hashes and are never edited manually.

## Gate boundary

Phase B is synchronous and sink-free. It may own logical pixel storage,
depth-specific codecs, direct/raw drawing, common primitive execution, and
logical readback. It must not own logical frame time, background service,
palette/Copper presentation, hardware overlays, official mode-facade
integration, or any output sink.

`tests/compat/` is a host-only boundary for executing the actual retained
Canvas/common renderer. Its README defines the permitted synchronous queue,
allocator, task, and matrix surface. It must never enter a target build.
