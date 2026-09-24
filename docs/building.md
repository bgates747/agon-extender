# Building Extender components

Compile entry points, checked against source on 2026-09-24. This is not a
fresh-machine installation qualification or permission to deploy. **The base
P4 build does not reconstruct every deployed candidate overlay.** Read the
[provenance boundary](#deployed-candidates-versus-the-base-target) before selecting
a replacement for an installed image, and the [operation entry point](using-extender.md)
before using an existing bench.

## Building the P4 firmware

Use **`p4-console` explicitly**. The default environment in `platformio.ini`
is still `p4-canary`, an earlier bring-up target. Many other named environments
are isolated diagnostics or historical experiments; their presence does not
make them alternative supported firmware configurations.

The current build uses PlatformIO with the Arduino/ESP-IDF hybrid framework.
The repository pins pioarduino `55.03.311` and Arduino-ESP32 `3.3.11`. The
maintainer's Linux build environment uses PlatformIO Core `6.1.19`. From a
POSIX shell with Git and Python 3 available:

```sh
git clone https://github.com/bgates747/agon-extender.git
cd agon-extender
python3 -m venv .venv
.venv/bin/python -m pip install platformio==6.1.19 PyYAML==6.0.3
./scripts/vdp-pio.sh run -e p4-console
```

The [wrapper](../scripts/vdp-pio.sh) selects the root `.venv/bin/pio` and runs it
inside `vdp/`. PlatformIO downloads the selected compiler/framework packages;
allow space and time for the first build. Additional documentation/validation
tools have dependencies in [requirements-dev.txt](../requirements-dev.txt).
Fresh-machine setup is still rough, and the commands above are the current
compile entry point rather than a complete installation procedure.

### Selected DevKit configuration

The maintained [board definition](../vdp/boards/olimex_esp32_p4_devkit.json),
[SDK defaults](../vdp/sdkconfig.defaults) and
[partition table](../vdp/partitions.csv) select the following baseline. These
are build inputs, not a fresh measurement of the installed firmware or a P4-PC
profile.

| Item | Selected configuration / interpretation |
|---|---|
| Silicon | Pre-v3 P4 (`esp32p4_es`); generated revision bounds must be checked for the selected build |
| CPU | SDK selects 360 MHz. The board JSON's descriptive 400 MHz field is not runtime proof; [ADR-0010](decisions/ADR-0010-cpu-frequency.md) records why forced 400 MHz was rejected |
| Flash | 16 MiB, QIO at 80 MHz. A DIO first-stage image header is expected for this toolchain; verify the second-stage handoff rather than patching that header |
| PSRAM | 32 MiB target, hex mode at 200 MHz, boot memory test; distinct from internal SRAM |
| Internal-memory budget | PlatformIO reports 512,000 bytes; this is not physical SRAM capacity and does not include all PSRAM |
| Application partitions | Two 7 MiB OTA slots, plus NVS, OTA metadata, coredump and reserved data. Partition presence does not implement a network updater or qualify durable crash reporting |

The [recorded bring-up](tasks/SETUP-001.md) passed its bounded canary scope;
sustained production-load and later-board qualification are separate. SDK defaults
do not necessarily overwrite a previously generated configuration. Inspect the
selected build's effective SDK settings when defaults or targets change; retain
candidate provenance rather than treating an old generated file as authority.

Build outputs are under `vdp/.pio/build/p4-console/`, including `firmware.bin`,
`firmware.elf` and `firmware.factory.bin`. An ordinary build without an explicit
build identity carries **`UNVERSIONED-DO-NOT-DEPLOY`**. For an identified bundle
from clean, committed source, use the existing builder with a new output path:

```sh
.venv/bin/python scripts/prepare_console.py --output agents/builds/console-local
```

[prepare_console.py](../scripts/prepare_console.py) builds and records binary,
source and dependency identities. It does not flash a board. A successful build
alone does not qualify its firmware for a particular assembly; consult the
[version/build conventions](versions/README.md) and the relevant physical
acceptance record before deployment.

### Which files actually get compiled?

The definitive list for this target is
[p4-console-source-selection.json](../vdp/pio/p4-console-source-selection.json).
It names the compiled project/library files, embedded browser assets and
excluded implementations. This matters: several generations of renderer and
transport code coexist in the tree.

[select_sources.py](../vdp/pio/select_sources.py) turns that list into the hybrid
build's generated CMake inputs. Edit the maintained source and selection files;
generated `vdp/CMakeLists.txt`, `vdp/video/CMakeLists.txt`, component manifests
and `.pio/` outputs are disposable. Start tracing execution at
[p4_console.cpp](../vdp/video/extender/boot/p4_console.cpp), which includes the
retained browser-VDP boot code and
[console transport](../vdp/video/extender/transport/console_hardware.inc).

## Building EMOS and the SD application

EMOS is built separately from the P4 firmware. Its current AgonDev build uses
[mos-agondev](https://github.com/bgates747/mos-agondev) for source preparation,
assembly translation and linking, and the
[AgonDev toolchain](https://github.com/AgonPlatform/agondev). The maintained
EMOS source remains in `agon-emos`; generated builder worktrees are disposable.

Start with [mos-agondev/STARTHERE.md](https://github.com/bgates747/mos-agondev/blob/main/STARTHERE.md)
for the toolchain and builder setup, supplying the EMOS checkout to its
`--agon-mos` source option. That builder currently requires Python 3.14 or newer.
EMOS's own Python dependencies are listed in its
[requirements-dev.txt](https://github.com/bgates747/agon-emos/blob/main/requirements-dev.txt).
Once the local paths and Python environments are configured, the EMOS
checkout's own Makefile provides the product build:

```sh
# Run from the agon-emos repository root.
make PYTHON=.venv/bin/python firmware-check
```

The [EMOS Makefile](https://github.com/bgates747/agon-emos/blob/main/Makefile)
defines `MOS_AGONDEV_ROOT`, `MOS_WORKTREE` and `AGONDEV_TOOLCHAIN` overrides.
With its default layout, firmware outputs are in
`../mos-agondev/projects/mos-port/bin/`. For identified builds and automated
qualification, see
[prepare_boot_review.py](https://github.com/bgates747/agon-emos/blob/main/scripts/prepare_boot_review.py);
that workflow also requires a configured Fab emulator.

The maintained `agon-emos` repository contains the resident SD gateway and
`projects/sdserve/`. The listener is built separately from resident EMOS. Its
ordinary application build, with AgonDev on `PATH`, is:

```sh
# Run from the agon-emos repository root.
make -C projects/sdserve
```

This produces the ordinary application `projects/sdserve/bin/sdserve.bin`. In that checkout,
`projects/sdserve/README.md` covers explicit toolchain paths, identified builds
and its EMOS requirements; `scripts/prepare_sdserve.py` creates identified
application bundles.
Use the [mainboard SD operating guide](mainboard-sd.md) for the host client
and service lifecycle. Compiling this application alone does not install the
EMOS gateway or matching P4 firmware it needs.

The installed EMOSlet instead occupies the 32 KiB MOSlet region. From the
`agon-emos` repository, a compile-only build is:

```sh
make -C projects/sdserve clean
make -C projects/sdserve RAM_START=0xB0000 RAM_SIZE=0x8000
```

The clean step prevents reuse of objects from the other memory layout. Both
layouts produce the same output filename: do not interchange their payloads.
The MOSlet installs as `/emos/sdserve.bin` and is invoked through `EMOS sdserve`;
the ordinary application fallback uses LOAD/RUN. `prepare_sdserve.py` prepares
ordinary application bundles; it does not by itself select the MOSlet layout.
Identified MOSlet builds and their validation are recorded in the
[fast-transfer tasklet](tasks/REMOTE-005/FAST-TRANSFER.md). Consult the
[EMOS utility contract](https://github.com/bgates747/agon-emos/blob/main/docs/emos-utilities.md)
for dispatch and memory limits. No build command in this guide deploys firmware.

## Deployed candidates versus the base target

The commands above compile the repository's base `p4-console` target. They do
**not** establish byte-for-byte or feature-for-feature reproduction of the
installed September candidates. Several deployed codec, renderer and browser
increments were built from isolated source snapshots with retained task-local
transformations. `scripts/prepare_console.py` invokes the base target directly;
it is not a reconstruction of that chain.

Trace the exact candidate from its deployment receipt and parent build before
preparing a replacement. Useful provenance entry points are
[BENCH-005 pacing/packing](tasks/BENCH-005.md),
[REMOTE-001 browser implementation](tasks/REMOTE-001/B04-implementation.md) and
[REMOTE-003 reset deployment](tasks/REMOTE-003.md#ad-hoc-result--2026-09-21).
Some snapshot inputs are ignored local artifacts; a clean public checkout is
not yet proven sufficient to reconstruct the latest installed P4 combination.
Do not deploy a base build as an equivalent replacement merely because it
compiles. The documentation audit records this gap as
[A09-F009](tasks/AUDIT-009/FINDINGS.md); consolidating source/build overlays
requires a separate implementation contract, not a documentation-only fix.
