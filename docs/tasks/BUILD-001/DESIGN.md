# BUILD-001 B01-03 — Proposed native-build design

Status: source/profile authority, wrapper and validator design accepted by the
Author on 2026-09-28. Dependency/tool acquisition and implementation-boundary
decisions remain under review. No maintained build files have been changed.

## Design outcome

One project-owned Python entry point prepares a profile-specific native
ESP-IDF/CMake build from one neutral checked-in manifest. CMake, Ninja and the
ESP-IDF component system compile and link every object. PlatformIO and SCons
have no role in the resulting graph.

The first implementation preserves ESP-IDF 5.5.5, Arduino-ESP32 3.3.11,
Arduino `setup()`/`loop()` autostart, all current console sources and flags, the
existing partition table, selected managed component versions, embedded browser
assets and the optional LCD configuration. It does not restructure runtime code.

## Proposed checked-in structure

| Path | Owner and purpose |
|---|---|
| `vdp/CMakeLists.txt` | Minimal native ESP-IDF project; validates the wrapper-provided profile input, sets target/configuration/lock properties and invokes `project()`. |
| `vdp/build/p4-profiles.json` | Sole neutral authority for buildable profiles, source lists, forbidden sources, flags, include paths, assets, SDK defaults, partition table and dependency-lock identity. |
| `vdp/components/agon_vdp/CMakeLists.txt` | Stable application-component registration; includes only the generated profile fragment from the selected build directory. |
| `vdp/components/agon_vdp/idf_component.yml` | Exact managed dependency constraints, including `espressif/arduino-esp32==3.3.11`. |
| `vdp/build/locks/<profile>.lock` | Solver-generated, reviewed exact dependency closure for each migrated profile. |
| `vdp/build/sdkconfig/<profile>.defaults` | Maintained profile deltas layered after common defaults; generated effective `sdkconfig` stays in the output directory. |
| `scripts/build_p4.py` | Sole supported operator wrapper for provision, configure, build, clean, graph validation and identified bundle preparation. It never flashes. |
| `scripts/validate_p4_build.py` | Compares the manifest, compilation database, Ninja graph, linker map, ELF and emitted artifacts; produces a machine-readable report. |

The existing per-profile source-selection JSON files remain frozen inputs during
transition. Implementation first imports their accepted facts into
`p4-profiles.json` and runs a mechanical equivalence check. After cutover they
are retained as historical evidence or removed only where their owning task
permits; they do not remain competing current authorities.

## Configure and build flow

B01-F01 [ ] The operator invokes `scripts/build_p4.py build --profile
p4-console --output <fresh-directory>` and optional reviewed feature switches
such as `--lcd`. The wrapper rejects unknown profiles, a dirty source for an
identified bundle, an existing output directory and unpinned tool identities.

B01-F02 [ ] The wrapper locates or provisions the exact ESP-IDF 5.5.5 checkout,
submodules and release tools in ignored project-scoped storage. It sets
`IDF_PATH`, `IDF_TOOLS_PATH` and `IDF_PYTHON_ENV_PATH` explicitly for child
processes and removes ambient compiler-injection variables.

B01-F03 [ ] The wrapper validates `p4-profiles.json`, resolves every path below
the repository root, checks duplicate/forbidden selections, hashes all inputs
and writes a generated `profile.cmake` plus build identity header into the fresh
output tree. Generated files include the manifest hash and reject reuse with a
different profile or source commit.

B01-F04 [ ] The wrapper invokes the pinned `idf.py -B <profile-build-directory>
build`. The checked-in top-level CMake file refuses configuration unless the
generated profile path, hash, target and output directory agree. The application
component registers the exact generated `SRCS`, assets, includes, definitions
and compile options. No source-tree CMake file is rewritten.

B01-F05 [ ] ESP-IDF's component manager resolves Arduino and the existing
managed dependencies against the selected checked-in lock. The build fails on
lock drift; dependency updates require a separate explicit wrapper action and a
reviewed lock diff.

B01-F06 [ ] The wrapper runs the graph validator and only then packages the ELF,
application/bootloader/partition images, factory image, map, effective
configuration, compilation database, dependency lock, input hashes, tool
identities, graph report and build log into the identified output directory.

## Component and lifecycle mapping

`agon_vdp` is one project component for the initial migration. It owns the
selected project translation units, selected vendored vdp-gl and ESP32Time
translation units, browser assets and current component-specific C++17/options.
Keeping one component initially reproduces current include visibility and avoids
turning a build migration into an architectural source split. AUDIT-010 may
later recommend component boundaries as an itemized fix.

Arduino-ESP32 is a managed component. Its own component supplies `app_main()`,
initializes Arduino and invokes the retained `setup()` and `loop()`. The
application component declares its Arduino and ESP-IDF requirements explicitly.
The first native profile preserves `CONFIG_AUTOSTART_ARDUINO=y`, core 1 and
`CONFIG_FREERTOS_HZ=1000`.

The profile manifest separately records C and C++ sources so `panel.c` remains
C while the current C++ units retain C++17. Header-defined VDP implementation
remains reached through `p4_console.cpp`; it is recorded as a header-owned
implementation set but is not falsely registered as independent translation
units.

## Configuration, dependencies and assets

Common hardware values move from PlatformIO board metadata into checked-in
native defaults or explicit wrapper/CMake arguments: ESP32-P4 target, flash
size/mode/frequency, PSRAM, silicon bounds, partition table and upload-independent
image offsets. `p4-console.sdkconfig` is used as the initial equivalence oracle;
the maintained native form becomes common defaults plus a small profile delta,
while the generated effective configuration is compared key-for-key during
migration.

The console manifest pins direct dependencies currently selected by the console
source manifest and adds Arduino-ESP32 3.3.11. The first solve must explain any
transitive additions, removals or version changes against
`p4-console-dependencies.lock`; an unexplained difference blocks B01-05.

Browser files use ESP-IDF's component embedding facility and preserve the
current terminating-NUL contract. The validator hashes source assets and checks
the emitted application bytes as the existing clean builder does.

## Canonical graph validation

The validator produces `build-graph.json` with these fail-closed comparisons:

B01-V01 [ ] Every manifest project/vendor source appears exactly once in
`compile_commands.json`, after canonical path resolution.

B01-V02 [ ] No forbidden or unselected project/vendor source appears in the
database, Ninja compilation edges or linker map.

B01-V03 [ ] Every project object recorded by the compilation database is an
input, directly or through its component archive, to the final ELF according to
the Ninja graph and linker map; every linked project object has a database
entry.

B01-V04 [ ] Compile definitions, include ordering, forced includes, language
standard and relevant optimization/debug flags match the profile declaration.

B01-V05 [ ] Embedded assets, partition input, effective SDK configuration,
managed dependency lock and build identity match their recorded hashes.

B01-V06 [ ] The report distinguishes project, vendored, Arduino, managed and
ESP-IDF framework units so AUDIT-010 can select project coverage without
mistaking framework internals for unreviewed application code.

## Migrated profiles

Under the Author-accepted inventory classification, the initial manifest
contains three buildable profiles:

| Profile | Native purpose |
|---|---|
| `p4-console` | Maintained ExCom/browser/USB/SD product-development firmware, with LCD as an explicit recorded feature switch. |
| `p4-mos-recovery` | Maintained operator-armed external MOS recovery programmer. |
| `p4-port008-nonrelease-qualification` | Non-release diagnostic retained until PORT-008 disposes its unfinished qualification and actual-action evidence needs. |

Common configuration is data inherited by these profiles, not a separately
buildable `p4-canary` default. The wrapper requires an explicit profile and has
no default that could accidentally produce older bring-up firmware.

## Build identity and output layout

Each fresh output contains `manifest.yaml`, `build-graph.json`, `inputs.json`,
`tools.json`, `dependencies.lock`, effective `sdkconfig`, build log,
`compile_commands.json`, ELF, map and flash images. The identity includes source
commit/tree state, profile manifest hash, profile name, feature switches,
ESP-IDF tag/commit/submodules, Arduino component version/hash, dependency-lock
hash, tool identities and output hashes.

Machine-local absolute paths may appear in ignored raw logs and compilation
databases. Tracked result summaries use repository-relative paths and hashes.
The wrapper normalizes or maps paths only for comparison; it does not rewrite
compiler commands and claim byte reproducibility that has not been demonstrated.

## Rollback and cutover

Implementation is additive through B01-06. Existing `platformio.ini`, hooks,
per-profile selection files and preparation scripts remain capable of building
the retained hybrid control. Native output uses a separate ignored directory
and cannot overwrite `.pio` products.

After native host and hardware equivalence acceptance, B01-07 changes maintained
entry points and documentation in one reviewable cutover. The hybrid files are
then moved to a clearly historical/rollback location or removed only after all
accepted consumers have migrated. The clean baseline bundle and its hashes
remain retained. Production selection does not change.

If native validation fails, the operator discards only the fresh native output
directory and continues using the unchanged hybrid path. No source reset,
firmware flash or production rollback is required because implementation before
cutover does not alter those authorities.

## Review decisions requested

B01-DR01 [x] The Author accepted the profile classification in `INVENTORY.md`
on 2026-09-28.

B01-DR02 [x] The Author accepted this source/profile authority, wrapper and
validator design on 2026-09-28.

B01-DR03 [ ] Accept or amend managed Arduino-ESP32 3.3.11 plus project-scoped
official ESP-IDF 5.5.5 source/tools as the acquisition strategy.

B01-DR04 [ ] Accept additive implementation through host equivalence only;
hardware procedure and flash authorization remain a later review.
