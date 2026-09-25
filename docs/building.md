# Building Extender components

Compile entry points and the accepted combination are indexed by the
[production selection](../production/README.md). The r55 clean build passed bounded
physical and Author review. This is not a fresh-machine installation qualification
or permission to deploy. Read the
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
.venv/bin/python scripts/prepare_console.py --output agents/release-build
```

[prepare_console.py](../scripts/prepare_console.py) requires a clean committed
checkout, exports `vdp/` into a fresh output directory, and invokes the selected
target there. It records identity, output/asset hashes, managed-component hashes,
effective SDK configuration and verbose compiler/tool logs. Downloaded tool
packages may be reused, but previous build objects and agent snapshots are not.
The output directory must not exist. Do not modify tracked inputs during a build.

Use optional `--reset-url "$RESET_BRIDGE_URL"` to configure the browser reset
bridge. The default is unset, leaving the reset button disabled. The endpoint is
recorded only in the local build manifest and generated page; never commit a
private endpoint. Request pacing is unchanged; the browser requests
`?rle2=1&packed=2` for the retained lossless compression selection.

After building, with Playwright and Chromium installed in the local environment:

```sh
.venv/bin/python tests/browser_bundle_test.py --bundle agents/release-build
```

This checks actual embedded asset bytes, browser negotiation and paired codec
outputs without a board connection. It does not measure P4 performance. The
[wrapper](../scripts/vdp-pio.sh) remains a low-level in-place compile convenience,
not the clean identified-bundle entry point. PlatformIO downloads pinned tools;
fresh-machine setup and packaging remain separate validation gates.

### Selected DevKit configuration

The maintained [board definition](../vdp/boards/olimex_esp32_p4_devkit.json),
[console SDK configuration](../vdp/pio/p4-console.sdkconfig),
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

### Upstream source and library pins

The [reviewed import identities](dependencies/reviewed/source-baselines.yaml)
record VDP `v2.16.0`, vdp-gl `all-the-plots`, ESP32Time `2.0.6` and CRC `1.0.4`.
The first two have pinned Git commits; the latter two use registry-package
path/content evidence. These are recorded imports, not a fresh upstream release
survey. The three libraries are vendored under `vdp/vendor/`; compiled subsets
come from the target selection above, not directory presence.

The [vendoring decision](decisions/ADR-0012-vendored-release-dependencies.md)
does not cover the entire toolchain: platform/framework packages and the console's
pinned managed components still have their own acquisition and lock records.
The [dependency graph's scope](dependencies/README.md#model-scope-versus-deployed-builds)
is narrower than all later console overlays; its historical verification is not
a complete compatibility-delta audit of the currently deployed firmware.

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

The maintained `p4-console` target includes the selected codecs, browser decoders,
build flags and hash-guarded DSP derivative. It no longer requires hidden task
snapshot overlays. The accepted r55 build additionally fixes the separate
bootloader configuration path and checks both silicon ranges before freezing an
image. See the [current bundle](../production/README.md) for exact binaries and
[physical acceptance](tasks/RELEASE-001/R01-07.md) for the bounded scope.

EMOS and the listener reproduce historical bytes exactly. P4 r55 is a separately
identified clean reconstruction, not byte-identical to the old installed reset
build. Compression negotiation and reset configuration are explicit in its
manifest. No new FPS guarantee or change to request pacing is implied.

### Exact EMOS and MOSlet reproduction

[reproduce_sd_components.py](../scripts/reproduce_sd_components.py) clones clean
owning repositories into a fresh directory, uses the existing MOS builder and
AgonDev toolchain, and requires expected historical hashes. For the selected
recorded installation (substitute local checkout/tool paths):

```sh
.venv/bin/python scripts/reproduce_sd_components.py \
  --emos-source ../agon-emos --builder-source ../mos-agondev \
  --toolchain ../mos-agondev/toolchains/agondev \
  --builder-python ../mos-agondev/.venv/bin/python \
  --output agents/sd-reproduction \
  --emos-build-id agon-emos-v0.1.19-b2026-09-24-02-02-56Z \
  --listener-build-id sdserve-v0.2.0-b2026-09-24-02-21-03Z \
  --emos-sha256 817deb27aa6139dcfbf616f10f799f90d2eed08c17e87883f57d6cc8583195d7 \
  --listener-sha256 bd7dc38aeac564d2df3da5a7c2dc1cd902ebf1973ef96140307649023f3dbb11
```

The exact commits and compiler hash are in the
[reproduction record](tasks/RELEASE-001/BUILD-RESULTS.json). Select those commits
in clean local checkouts if current source has advanced. Reused timestamps are
permitted solely for exact hash reproduction; differing outputs fail and must
not be deployed with a historical identity. A genuinely changed build needs a
new timestamp through the owning project's identified build procedure.
The helper builds the **MOSlet**, not an ordinary LOAD/RUN application, and does
not modify an emulator, SD card or board.

## Local installation packaging

The [production entry point](../production/README.md) and `production/current.yaml`
select the accepted immutable bundle. r02 packages the exact physically tested
r55 outputs; it does not rebuild or flash them. A clean source export must pass
both application and bootloader silicon-configuration checks. The maintained
pre-build hook resolves the configuration path absolutely for both CMake builds.

The selected inputs are in
[the packaging selection](../production/bundles/extender-installation-r02/selection.json).
Local generated build directories are inputs, not runtime dependencies:

```sh
.venv/bin/python scripts/package_installation.py \
  --selection production/bundles/extender-installation-r02/selection.json \
  --p4-build agents/release001/builds/reset-corrected \
  --sd-build agents/release001/builds/sd-components \
  --emos-source ../agon-emos --builder-source ../mos-agondev
.venv/bin/python scripts/verify_installation.py \
  dist/production/extender-installation-r02/extender-installation-r02
```

The builder requires a clean packaging checkout and refuses an existing output
directory. Use the immutable bundle's recorded packaging commit to reconstruct
its recipe; do not reuse the identity for changed inputs. Archive timestamps are
not claimed reproducible: select retained archives by recorded SHA-256.
Neither command deploys or creates the current selection. The configured local
firmware contains a private reset endpoint. Its build-owner configuration remains
local; changing it requires a newly identified build. Public source/license
limits remain in [NOTICES](../production/NOTICES.md). The failed r01 archive is
historical evidence and must not be deployed.
