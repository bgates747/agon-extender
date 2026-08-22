# PORT-003 Phase A — Contract canary

[`../../PORT-003.md`](../../PORT-003.md#phase-a--contract-canary) is the
authoritative checklist and scope fence. This directory contains only Phase A
source-import machinery, generated evidence, diagnostic build records, and
validation helpers. Production display code remains under
`vdp/video/extender/display/`; recurring build-selection machinery belongs
with the VDP project after the canary proves its shape.

## Structure

```text
phase-a/
├── README.md
├── compatibility-delta.md
├── evidence/
│   ├── import-manifest.yaml
│   ├── build-closure.yaml
│   └── link-exclusions.yaml
└── scripts/
    ├── import-baselines.py
    └── validate-phase-a.py
```

Generated evidence must name its generator, source identities, input hashes,
and diagnostic status. Build logs are summarized into structured evidence;
environment-specific raw logs and PlatformIO products remain ignored.

`vdp/pio/source-selection.json` is the recurring machine source list.
`vdp/pio/select_sources.py` renders the ignored hybrid-component CMake boundary
and selects the two approved vdp-gl translation units. The tracked application
sources remain under `vdp/video/extender/`; they are not duplicated here.

## Regeneration and validation

Verify the immutable import without modifying it:

```sh
.venv/bin/python docs/tasks/PORT-003/phase-a/scripts/import-baselines.py \
  --source-root agon-vdp=<official-v2.16.0-checkout> \
  --source-root vdp-gl=<official-vdp-libdeps>/vdp-gl \
  --source-root ESP32Time=<official-vdp-libdeps>/ESP32Time \
  --source-root CRC=<official-vdp-libdeps>/CRC
```

At commit gates, add `--verify-index` after staging. This catches generic
ignore rules that would otherwise omit legitimate release files.

Build and prove the application closure:

```sh
.venv/bin/pio run --project-dir vdp -e p4-display-contract-canary

.venv/bin/python docs/tasks/PORT-003/phase-a/scripts/validate-phase-a.py \
  --nm <pinned-riscv32-esp-elf-nm>
```

The validator proves exactly three project and two vendored application
translation units, required ELF symbols, and excluded VDP implementation
families. ESP-IDF and Arduino platform components are intentionally outside
that application-level exclusion claim.

## Gate boundary

Phase A proves type, compile, and link boundaries only. It intentionally has no
framebuffer, rendering, logical frame service, or output sink and makes no
runtime or hardware claim.
