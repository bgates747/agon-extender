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
