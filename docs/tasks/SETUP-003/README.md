# SETUP-003 supporting workspace

The canonical task record is [`../SETUP-003.md`](../SETUP-003.md). This
directory keeps task-specific tooling and evidence together without hiding the
task itself from scans of `docs/tasks/`.

- `scripts/` contains reproducible extractors used only by SETUP-003.
- `evidence/` contains compact, selected source or build evidence that is not
  reproducibly generated.
- `generated/` contains deterministic machine-generated inventories.

Generated files must identify their inputs, generator, tool versions, and
exact regeneration command. Avoid retaining bulky raw logs when a compact
lossless extract records the relevant evidence.

## Work 3 upstream control build

Create a fresh temporary checkout at tag `v2.16.0`, then build and generate its
compilation database with an isolated temporary PlatformIO core/package store:

```sh
PLATFORMIO_CORE_DIR=<isolated-temporary-platformio-core> \
  PLATFORMIO_SETTING_ENABLE_TELEMETRY=no \
  <project-venv>/bin/pio run -d <temporary-v2.16.0-checkout> -e esp32dev
PLATFORMIO_CORE_DIR=<isolated-temporary-platformio-core> \
  PLATFORMIO_SETTING_ENABLE_TELEMETRY=no \
  <project-venv>/bin/pio run -d <temporary-v2.16.0-checkout> -e esp32dev -t compiledb
.venv/bin/python docs/tasks/SETUP-003/scripts/generate-control-build-evidence.py \
  --source <temporary-v2.16.0-checkout> \
  --platformio-core <isolated-temporary-platformio-core>
```

The isolated PlatformIO store is mandatory. A temporary source checkout alone
does not prevent an incompatible package with the same PlatformIO package name
from being reused from the normal global store.

## Work 4 regeneration

Against an isolated official `v2.16.0` checkout configured with the qualified
P4 experimental environment:

```sh
.venv/bin/pio run -d <official-agon-vdp-checkout> -e p4-work3 -t compiledb
.venv/bin/python docs/tasks/SETUP-003/scripts/generate-compile-evidence.py \
  --source <official-agon-vdp-checkout>
```

PlatformIO's complete `compile_commands.json` contains ESP-IDF implementation
units and host-specific paths. `generated/compile-commands.json` is the
normalized subset for the VDP sketch and its declared dependencies.

PlatformIO records but does not retain its transient `video/video.ino.cpp`.
The extractor therefore applies that recorded command to `video/video.ino` in
preprocessor-only mode. This is sufficient for include analysis and does not
attempt to reproduce Arduino's generated function prototypes.

## Work 5 regeneration

```sh
.venv/bin/python docs/tasks/SETUP-003/scripts/generate-symbol-index.py \
  --source <official-agon-vdp-checkout> \
  --ctags <universal-ctags>
```

The generator requires Universal Ctags with JSON output. It maps Arduino
`.ino` files explicitly to C++, enables prototype and external-variable kinds,
and indexes only the official VDP and declared-library source trees. Examples
and tests bundled with dependencies are outside the index.

## Work 6 portability and ownership regeneration

```sh
.venv/bin/python docs/tasks/SETUP-003/scripts/generate-portability-inventory.py \
  --source <official-agon-vdp-checkout>
```

`generated/portability.yaml` combines the symbol index with exact source-line
evidence for lifecycle APIs, platform/framework facilities, memory use,
includes, conditional compilation, global/static candidates, and
protocol-related names. It also merges the bounded semantic review in
`evidence/work-6-reviewed-subsystems.yaml` after validating every referenced
source line and declared source-wide search. The resulting subsystem records
describe ownership, runtime activation, platform coupling, externally visible
behavior, and portability boundaries. They deliberately make no
retain/replace/stub/omit/defer disposition.

The compact human index and conclusions are in `portability-review.md`.

## Work 7 dependency-view regeneration

```sh
.venv/bin/python docs/tasks/SETUP-003/scripts/generate-dependency-views.py
```

The generator resolves the Work 6 direct-source include records against the
indexed source set, computes distinct-file fan-in and fan-out, finds strongly
connected components, and emits the complete graph as
`generated/dependency-views.yaml`. It validates and merges the bounded,
source-cited semantic relationships in `evidence/work-7-graph-model.yaml`.

The `.dot` and `.svg` files are deterministic projections of that data. The
cycle diagram intentionally omits edges between different strongly connected
components to preserve legibility; those edges remain in the YAML. Graphviz
layout may be adjusted through the model's presentation settings without
changing semantic nodes or edges.
