# Building Extender components

Compile entry points and the accepted combination are indexed by the
[production selection](../production/README.md). The r55 clean build passed bounded
physical and Author review. This is not a fresh-machine installation qualification
or permission to deploy. Read the
[provenance boundary](#deployed-candidates-versus-the-base-target) before selecting
a replacement for an installed image, and the [operation entry point](using-extender.md)
before using an existing bench.

## Building the P4 firmware

Native ESP-IDF/CMake is the sole maintained outer build authority. Arduino-ESP32
3.3.11 remains a pinned ESP-IDF component. The project-scoped ESP-IDF 5.5.5
source, Python environment and tools are provisioned under ignored
`agents/build001/native-tools/`; the exact ESP-IDF commit is enforced by the
wrapper. Use **`p4-console` explicitly** and a fresh output path:

```sh
.venv/bin/python scripts/build_p4.py \
  --profile p4-console \
  --output agents/builds/console-local \
  --build-id UNVERSIONED-DO-NOT-DEPLOY
```

`p4-console` is the minimal ordinary product-development profile. Its manifest
records required definitions separately from default-off historical diagnostics
and rejected experiments; the builder rejects overlap, and the action validator
rejects excluded definitions on compiled sources. Do not enable a diagnostic or
experiment by editing the ordinary profile. A recurring diagnostic requires an
explicitly named profile and owning task contract.

The same manifest declares the selected stock-shaped display family as the
single product display owner. `p4-port008-nonrelease-qualification` selects a
different, older family solely to close PORT-008's bounded provenance and
retained-parser work; it is not a product, deployment, fallback or repair
target. The builder rejects mixed display families, a second product owner, or
a non-release family without an explicit task owner and retirement contract.
Do not copy a product display fix into the non-release family.

An identified build uses a project-approved ID in place of the unversioned
sentinel and requires a clean committed checkout. The wrapper rejects an
existing output, a wrong ESP-IDF checkout, unsafe manifest paths, unsupported
profiles and dirty identified inputs. It generates disposable CMake component
files, invokes IDF/Ninja, validates declared/compiled/archived/linked agreement,
and writes a manifest, dependency lock, effective SDK configuration, build log,
section report, validation report, canonical compilation database, ELF, map,
individual flash segments and offset-zero factory image.

Use optional `--reset-url "$RESET_BRIDGE_URL"` to configure the browser reset
bridge. The default is unset, leaving the reset button disabled. The endpoint is
recorded only by hash in the local manifest and inserted into the generated
embedded page; never commit a private endpoint. Request pacing is unchanged; the browser requests
`?rle2=1&packed=2` for the retained lossless compression selection.

After building, with Playwright and Chromium installed in the local environment:

```sh
.venv/bin/python tests/browser_bundle_test.py \
  --build-output agents/builds/console-local
```

This checks actual embedded asset bytes, browser negotiation and paired codec
outputs without a board connection. It does not measure P4 performance.
[prepare_console.py](../scripts/prepare_console.py) is only a compatibility name
that delegates ordinary console builds to the native wrapper. The old
[PlatformIO wrapper](../scripts/vdp-pio.sh) is retained for accepted bounded
reproduction of identified hybrid evidence and fails unless its historical-use
acknowledgement is supplied.

### Board selection and compile-time pin mapping

The native builder selects hardware independently of the software profile:

```sh
.venv/bin/python scripts/build_p4.py \
  --profile p4-console --board p4-pc \
  --tools-path "$P4_IDF_TOOLS" --python-env "$P4_IDF_PYTHON_ENV" \
  --output agents/builds/pc-local \
  --build-id UNVERSIONED-DO-NOT-DEPLOY
```

Set the two tool variables to host-native installations. Migrated x86 compiler
executables cannot run on the Pi ARM64 host; the wrapper checks executability
before creating output. Neither option changes the pinned ESP-IDF checkout or
managed component versions. Machine-local tool locations belong in
`HARDWARE.local.md`, not board profiles.

Omitting `--board` retains `p4-devkit`. The revisioned configuration files under
[`vdp/build/boards`](../vdp/build/boards/README.md) are the native hardware-input
authority. `p4-pc` currently supports only `p4-console`; recovery and historical
buffered parallel qualification remain DevKit-only. The builder rejects unknown
boards, unsupported compositions and invalid/conflicting GPIO allocations.

Each output contains `board.json` and the generated
`project/components/agon_vdp/agon_extender_board_config.hpp`. Shared C++ code
uses that header for UART routing, its startup input fence and TX cancellation,
Ethernet, local SD and USB hub setup. The build manifest records board identity,
configuration/header hashes and compiler identity. Validation checks actual
compiler dependencies and the effective application/bootloader silicon range.

Both variants retain browser output. Selecting the PC board does not add HDMI,
select a new display family or change EMOS's ownership of transport admission.
The PC mapping is a candidate direct harness: eight shared UART/parallel lanes
plus READY_N, CLOCK and VALID_N. Its GPIO20/32 sensing options must remain
disconnected. See [BOARD-001](tasks/BOARD-001.md) for pending physical review and
bench gates; compile success does not qualify that wiring or authorize flashing.

The [current wiring drawing and mapping](../hardware/designs/light2-p4pc-harness-draft/README.md)
retain the original assignments. The Author arranged the bench to suit that
mapping and withdrew the reversed-PC proposal. The unchanged PC board JSON
and existing PC build outputs match this restored mapping; no firmware
remapping is needed for the orientation request.

For the pending P4-PC keyboard experiment, add `--usb-fsls-only` to the native
`p4-console --board p4-pc` command. IDF 5.5.5 lacks the public `fsls_only`
install option. The source-bound recipe in
[`usb_fsls_only.cmake`](../vdp/native/usb_fsls_only.cmake) generates a USB HCD
derivative that restricts the existing HS-capable controller to FS/LS before
each root-port reset. It keeps the onboard hub and pin mapping, with a
12 Mbit/s upstream link. Other board/profile combinations reject the flag;
omitting it retains the existing USB source. The SDK checkout remains unchanged.
The manifest records the option and recipe/derivative hashes; validation checks
the actual compile action and USB archive. The Author's keyboard tests fail;
passive serial confirms full-speed operation followed by failure of the initial
device-descriptor transfer. Physical keyboard operation remains unqualified;
see BOARD-001.

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
| Flash | 16 MiB, 80 MHz. Effective IDF flash settings and the first-stage image header are recorded by the selected native build |
| PSRAM | 32 MiB target, hex mode at 200 MHz, boot memory test; distinct from internal SRAM |
| Internal-memory budget | The historical board metadata's 512,000-byte figure is not physical SRAM capacity and does not include all PSRAM; use IDF map/size output and runtime heap evidence |
| Application partitions | Two 7 MiB OTA slots, plus NVS, OTA metadata, coredump and reserved data. Partition presence does not implement a network updater or qualify durable crash reporting |

The [recorded bring-up](tasks/SETUP-001.md) passed its bounded canary scope;
sustained production-load and later-board qualification are separate. SDK defaults
do not necessarily overwrite a previously generated configuration. Inspect the
selected build's effective SDK settings when defaults or targets change; retain
candidate provenance rather than treating an old generated file as authority.

Build products are under `<output>/build/`; `<output>/manifest.json` records
their hashes and identities. The wrapper never flashes a board. An ordinary
build should carry **`UNVERSIONED-DO-NOT-DEPLOY`**. A successful build alone
does not qualify its firmware for a particular assembly; consult the
[version/build conventions](versions/README.md) and the relevant physical
acceptance record before deployment.

### Which files actually get compiled?

The definitive source/profile authority is
[p4-profiles.json](../vdp/build/p4-profiles.json). It names compiled sources,
forbidden alternatives, embedded browser assets, dependencies, definitions and
profile-specific integration settings. Generated project/component CMake files
inside a fresh output are disposable and must not be edited. The validator
compares this declaration to the actual compile database and Ninja archive/link
edges. Start tracing execution at
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
that workflow also requires a configured Fab runtime and runs automated
runtime checks. Start with [emulator setup](emulator-setup.md) for profile
ownership, stock-versus-EMOS selection and validation limits.

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

## Private parallel payload compile probe

PORT-008's explicit `--parallel-boot-candidate` P4-PC build compiles the private
shared handover, UART drain/parking and native PARLIO RX/TX coordinator. It does
not activate ExExt or provision a payload buffer. Ordinary selections exclude
the native coordinator and payload leaves. Unprovisioned offers are rejected.

The companion EMOS `port/parallel-native-candidate.mk` includes the private
foreground coordinator and native assembly. The complete checked image uses
130473 ROM bytes, 599 free; ordinary EMOS uses 128739 bytes, 2333 free. These are
compile/link measurements with unchanged ROM and caller-inventory guards, not
deployed identities or production selections. The coordinator has no activation
caller, public API or CLI command. See the
[coordinator integration evidence and remaining gate](tasks/PORT-008/LIVE-COORDINATOR-LC02-RESULTS.md)
before selecting either private composition. A separately reviewed fixture and
physical qualification remain required.

EMOS excludes its C receive correctness reference from ordinary/native builds;
`port/parallel-reference-test.mk` retains it explicitly for tests. The RAM-only
instruction image is never firmware. Earlier
[ROM-fit](tasks/PORT-008/NATIVE-ROM-FIT-RESULTS.md),
[diagnostic extraction](tasks/PORT-008/DIAGNOSTIC-ROM-RECOVERY-RESULTS.md) and
[block-control refusal](tasks/PORT-008/BLOCK-CONTROL-RESULTS.md) retain their own
historical build sizes and validation limits.

The extracted diagnostics build in sibling `agon-emos/projects/uartprobe` with
`make NAME=uarttest` and `make NAME=vdppoll`, using the selected AgonDev toolchain.
During an authorized paired development deployment their binaries belong at
`/emos/uarttest.bin` and `/emos/vdppoll.bin`; they are not present on SD by
assumption. Commands keep their EMOS prefix, require an idle Legacy CLI and an
unclaimed UART1, and retain their distinct peer/baud requirements. See the
[component guide](../../agon-emos/projects/uartprobe/README.md). No build command
installs either file or authorizes bench use.

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

## P4-local SD HTTP candidate

The standard `p4-console` source selection includes
`video/extender/storage/local/http.cpp`. The selected console SDK configuration
uses heap-backed FatFS long filenames, required by upload staging names. Other
fixture targets do not acquire this service automatically.

Host-only filesystem checks:

```sh
g++ -std=c++17 -Wall -Wextra -Werror -I vdp/video \
  tests/storage/p4_local_files_test.cpp -o /tmp/p4-local-files-test
/tmp/p4-local-files-test
```

A low-level PlatformIO compile is not an identified release or evidence that the
physical SD card mounts. Follow the normal identified build/deployment workflow
before bench qualification. See [P4 SD operations](p4-sd.md).

Additional P4-local file management checks (Linux host):

```sh
g++ -std=c++17 -Wall -Wextra -Werror -I vdp/video \
  tests/storage/p4_local_replace_failure_test.cpp -Wl,--wrap=rename \
  -o /tmp/p4-local-replace-test
/tmp/p4-local-replace-test
.venv/bin/python -m unittest discover -s tests/storage -p 'test_*.py' -v
```

The replacement test injects an installation rename failure and verifies old-file
restoration. Python tests use a localhost HTTP peer to check client framing,
command dispatch and tree transfers; they do not execute ESP-IDF handlers or
qualify an SD card. The console HTTP URI limit is 2048 bytes to accommodate two
encoded paths; recursive filesystem traversal is bounded to 16 levels.

Detached consumers should start with [shared P4 service boundaries](shared-p4-services.md),
not the complete console translation-unit selection. The Ethernet header is
Arduino-backed but independent of VDP, EMOS and HTTP route composition.

The optional development `--lcd` build is described in [LCD output](lcd-output.md);
it is not enabled in ordinary builds or the selected production bundle.

## P4-PC HDMI development output

The native builder accepts `--display-output browser` (the default) or
`--display-output hdmi`. HDMI is restricted to `p4-console` on `p4-pc` and
uses the same stock-shaped renderer. The selected adapter supplies fixed
1280×720 RGB888 output by default, centered unscaled images and cropping, with logical-mode
buffering and hardware-paced frames. Browser video is omitted; browser keyboard,
HTTP and SD services remain. Native DevKit/browser selection is unchanged.

The experimental `--hdmi-timing auto` option requires
`--rolling-scanout --direct-rgb888 --render-benchmark-output normal` and an
explicit dirty-experiment build identity. It selects684×384 for logical images
that fit that carrier and848×480 otherwise. Thus512×384 is centered at(86,0),
while640×480 is centered at(104,0) with no clipped text rows. Smaller modes remain
centered and unscaled;320×240 has no new physical timing yet. Oversized modes
retain the crop fallback pending inventory. `/display/status` reports the active
carrier rather than the build's initial size.

The automatic build also exposes experimental single-buffer modes **96–99**:
848×480 at 64, 16, 4 and 2 colors respectively. These provisional IDs expose
the complete 848×480 carrier, without changing stock modes or adding DB aliases.
They use the existing native compositor; the direct RGB888 fast path remains
limited to its previously qualified geometries. Select them through ordinary
EMOS-routed `VDU 22 n`; stock mainboard VDP does not implement these IDs.
See [full-width qualification](tasks/HDMI-002.md) for current validation limits.

The behavior in this paragraph and the next describes the retained r06 build.
Unaccepted development source now also contains the r07/r08 experiment with
three 848-wide slots, selected task stacks in PSRAM, and direct RGB888 mode 96.
That experiment fails longer Nurples runs with stopped scanout and a recorded
DSI underrun. A fresh build of this working tree is **not** the proven r06
rollback. Use its exact retained artifacts/manifest, and consult the
[failed experiment record](tasks/HDMI-002/ROLLING480-RESULTS.md) before choosing
development firmware. Production selection is unchanged.

The subsequent r09 source adds a bounded one-request refill queue and preserves
the first scanout fault for diagnosis. It passes host checks and target compilation
only; it has not been deployed. See the [offline review](tasks/HDMI-002/OFFLINE480-REVIEW.md)
before choosing this experiment. The three-slot allocation,1,600µs limit and
physical timings are unchanged; waiting time counts toward that limit.

The following r10 experiment adds cancellation of submitted swap waiters and
fault-aware panel borrowing/recreation at joined mode boundaries. It retains
r09's refill remedy. Host lifecycle and failure-injection checks pass; this is
still unflashed development, not a repair verified on the physical monitor.
See the [mode-lifecycle review](tasks/HDMI-002/MODE-LIFECYCLE-REVIEW.md) for exact
build status and the distinction between reproduced host defects and the
unresolved physical mode96-to97 failure.

The automatic build reserves three32-row684 rolling SRAM slots at boot and
retains them across carrier changes, avoiding later fragmentation. The684 carrier
uses those slots and immutable hardware
sprite snapshots. The848 carrier reuses pinned IDF's full-frame DMA, avoiding
an additional47KiB of SRAM that three848-wide slots would require. This does
not qualify equivalent hardware-sprite performance in480-line modes. Sprites
remain enabled through the native compositor, with unchanged palette behavior;
bounded640×480 checks in16/4/2-color modes pass. Carrier
changes stop/join the former rendering owners and restart DSI/LT8912B on core1;
fixed selections remain available. See [runtime qualification](tasks/HDMI-002.md).

The explicit experimental `--hdmi-timing 848x480` option selects the
[HDMI-002](tasks/HDMI-002.md) custom 60.06944 Hz timing: PLL240/7 pixel clock,
two 480 Mbps DSI lanes and 1104×517 totals. It is not exact DMT 0Eh or a
native 512×384 signal. A 512×384 logical image is centered unscaled at (168,48).
Omitting the option retains 1280×720. The build manifest and embedded browser
status record the selected output; browser video remains absent in HDMI builds.
The accepted partial-scroll implementation can be selected with the existing
experimental `--direct-rgb888` option; this does not promote it to production.
The additional experimental `--hdmi-timing 512x384` selection uses a native
512×384 active area with the same clock and totals, larger blanking porches and
4:3 metadata. The standalone signal failed physical review and the Author now
targets a widescreen carrier with512×384 pillarboxed. This full512-wide selection
is retained experimental preparation, not a deployment recommendation.
With `--rolling-scanout --direct-rgb888 --render-benchmark-output normal`,
its twelve 32-row DMA blocks use three internal SRAM slots totaling 147456 bytes,
versus 244224 bytes for the 848-wide experiment. The rolling renderer and DMA
driver must use matching build definitions; validation checks both. Full-firmware
startup, mode transitions, sprites and gameplay for that512-wide build remain
unqualified; it is not the accepted standalone684-wide timing pattern.

The explicit `--hdmi-timing 684x384` selection uses the reviewed widescreen
carrier with512×384 centered at(86,0), preserving the clock and totals above.
Combined with the same rolling/direct/benchmark flags, twelve32-row blocks
reuse three SRAM slots totaling196992bytes. Build validation checks matching
684-wide C DMA and C++ definitions. The initial candidate exhausted internal
memory during hardware Nurples and crashed in buffer ownership cleanup. The
latest placement remedy completes the marked3600-update run at nominal60/s and
ordinary menu/mode-change/Escape exit, with about22KiB internal RAM free during
play. Author review and broader qualification remain pending; automatic Agon
SD admission after ordinary exit rejects in ExCom and recovers through
`EMOS LEGACY` without reset. Use
[the integration record](tasks/SPRITE-001/INTEGRATION.md) for current evidence.
The old full848 image remains usable for service recovery, but is not a
hardware-sprite Nurples playtest rollback. The current rolling candidate prefers
PSRAM for all ordinary malloc sizes (`CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL=0`),
while preserving the32768-byte internal reserve and explicitly internal RTOS/DMA
allocations. The physical rolling build also allocates the unchanged1024-entry
primitive queue payload in PSRAM, with its RTOS control in internal RAM. The
owned adapter uses pinned IDF static-queue construction and capability-aware
deletion; the stock queue capacity, order and drawing behavior are unchanged.
An optional `--abort-on-alloc-failure` is restricted to an explicit
experimental rolling build; it uses IDF's heap-abort diagnostic and must not be
confused with the memory remedy. Default builds are unaffected. See
[allocation diagnosis and current checks](tasks/HDMI-002/MEMORY-RESULTS.md).
For controlled comparisons, `--dependencies-lock PATH` seeds dependency
resolution from a retained build lock. Verify the resulting lock against the
intended baseline; the option does not itself prevent a resolver update.

HDMI is experimental, outside selected production. Its pre-v3 silicon callback
is DMA frame completion rather than a separate hardware-vsync interrupt; original
70/75Hz modes physically use the fixed ~60Hz HDMI cadence. See
[HDMI-001](tasks/HDMI-001.md) for scope, constraints and pre-flash evidence.

The explicit `--allow-dirty-experimental` exception is restricted to admitted
HDMI experimental build identities on P4-PC/console/HDMI. It archives exact Git-visible
VDP and build-tool source bytes before compiling, records their hashes, and
rejects changes during the build. It does not qualify dirty source or waive
the normal clean-input guard for other identified builds. Build outputs retain
`source.tar.gz`, `source-inputs.json`, `display.json`, board inputs, dependency
lock, compile/link validation, image hashes and normal manifests. No build command
flashes a board.

The 2026-10-09 diagnostic extraction ordinary candidate and its three MOSlets
have subsequently passed [bounded hardware qualification](tasks/PORT-008/DIAGNOSTIC-ROM-RECOVERY-HARDWARE.md).
This development installation does not replace the selected production bundle
or qualify the private parallel coordinator.
