# SETUP-001 — Initial PlatformIO project

## State

- Status: In progress — subtask review

## Scope

Establish the development environment for the VDP portion of the ESP32-P4
firmware. Begin with a faithful port of the official stock Agon VDP to the
Olimex ESP32-P4-DevKit while guaranteeing full backward compatibility with
existing Agon software.

Mirror the stock VDP project's directory structure, filenames, and source
organization as closely as the target permits. Names and locations should be
virtually identical so upstream changes remain recognizable, comparable, and
practical to incorporate over the life of the project.

The repository will contain a top-level `vdp/` directory. That directory will
own the PlatformIO project, the ported VDP firmware, and the dedicated
`vdp/video/extender/` subtree for new Extender capabilities and extended
functions.

## Implementation gate

Review and agree upon the implementation subtasks individually with the Author
before creating or changing the PlatformIO project structure.

Initial build inspection and explicitly approved canary flashing may proceed
without the final project versioning scheme. Before serious firmware iteration,
compatibility integration, repeated deployment, or wiring/protocol
qualification begins, complete SETUP-002 and apply its human-readable
identities to the affected artifacts and evidence.

## Instructions

1. Treat the official Agon VDP project as the structural and behavioral
   baseline for the VDP portion of Extender firmware.
2. Preserve upstream directory names, filenames, and relative source locations
   wherever technically possible.
3. Keep upstream-derived code recognizable as a port. Avoid gratuitous
   renaming, relocation, reformatting, abstraction, or cleanup that would make
   source comparison and upstream integration harder.
4. Isolate unavoidable ESP32-P4, ESP-IDF, board, build-system, and Extender
   differences behind the narrowest practical target-specific files or
   conditional boundaries.
5. Do not place new Extender capabilities into the upstream-shaped baseline
   merely for convenience. New capabilities and extended functions belong in
   the dedicated `video/extender/` subfolder. Keep their integration points
   with the upstream-shaped baseline explicit and narrow so the compatibility
   port remains auditable.
6. Place the complete VDP PlatformIO project and firmware under the repository's
   top-level `vdp/` directory.
7. Develop the remaining implementation subtasks here and review them
   individually with the Author before changing the PlatformIO project
   structure.
8. Treat technical explanation and Author review as required engineering
   outputs. Do not assume prior fluency in Python, C, C++, PlatformIO, ESP-IDF,
   object-oriented design, build systems, or embedded-software architecture.
9. Explain unfamiliar concepts using plain language and, where useful,
   analogies to SQL data flow, schemas, stored procedures, eZ80 assembly,
   calling conventions, memory layout, interrupts, and hardware interfaces.
10. Present architecture as small, reviewable decisions. Define terminology,
    show how control and data move through the system, identify tradeoffs, and
    obtain Author understanding before relying on a major design conclusion.

## Subtasks

### SETUP-001.1 — Inspect and reconcile project setup

- Status: Initial physical canary completed with partial pass; pre-canary
  firmware restored; CPU and Arduino USB-serial corrections required
- Deliverable:
  [`SETUP-001.1 layout manifest`](SETUP-001.1-layout-manifest.md)
- Inspect the official [Agon VDP](https://github.com/AgonPlatform/agon-vdp)
  project as the authority for
  VDP structure, filenames, build organization, source layout, and compatibility
  baseline.
- Inspect the private legacy Agon Extender repository for previously proven
  ESP32-P4 DevKit, PlatformIO, ESP-IDF, board-definition, build, upload, and
  development-environment setup.
- Distinguish reusable setup evidence from obsolete or experiment-specific
  legacy architecture. Do not copy the legacy project wholesale.
- Produce a proposed `vdp/` setup and layout manifest that blends the official
  VDP structure with only the necessary, verified P4-specific setup from the
  legacy project.
- Identify every proposed deviation from official `agon-vdp`, its reason, and
  the narrow boundary that will contain it.
- Stop for Author review of the manifest before creating the top-level `vdp/`
  directory or any PlatformIO project files.

#### Execution sequence

1. Inventory official `agon-vdp`: record every important directory and root
   file, especially `platformio.ini`, firmware entry points, source directories,
   libraries, configuration files, and build scripts.
2. Inventory the legacy Extender setup: extract only proven P4 infrastructure,
   including its board definition, PlatformIO environment, ESP-IDF version,
   compiler flags, partitioning, upload configuration, pin configuration, and
   useful development scripts.
3. Build a comparison table showing the official VDP, legacy P4, and proposed
   Extender choice for each setup concern.
4. Draft the exact proposed `vdp/` tree. Classify every proposed file as an
   upstream-shaped port, P4-specific replacement, build/configuration support,
   new `vdp/video/extender/` code, or an intentional omission.
5. Review every proposed deviation from upstream with the Author. Default to
   retaining the upstream name and relative location unless a verified P4
   requirement prevents it.
6. Create the `vdp/` project only after the Author approves the manifest.

#### Canary implementation result

- Created the approved hybrid Arduino/ESP-IDF PlatformIO scaffold beneath
  `vdp/`, preserving `video/` as the upstream-shaped source root.
- Pinned pioarduino `55.03.311` and recorded resolved ESP-IDF component
  dependencies in `vdp/dependencies.lock`.
- Built the temporary, GPIO-inert `video/video.ino` canary successfully with
  Arduino-ESP32 3.3.11, ESP-IDF 5.5.5, and the RISC-V 14.2.0 toolchain.
- Verified the generated partition table, application offset, OTA layout,
  silicon revision constraints, PSRAM configuration, 400 MHz CPU target,
  80 MHz flash target, rollback, core-dump, and USB Serial/JTAG settings.
- Confirmed that pioarduino deliberately leaves the ROM-compatible image
  header in DIO mode while the second-stage bootloader enables configured QIO.
  Runtime QIO remains a physical-board qualification requirement.
- Confirmed read-only that the bench Pi sees the attached board under its
  expected stable USB identity. No firmware was flashed and no reset, power,
  GPIO, or other physical state was changed.

#### Execution record, gotchas, and workarounds

1. **The wrapper could not use project selection as a global option.** The
   first wrapper form attempted to give PlatformIO a project-directory option
   before the subcommand. PlatformIO rejected that command shape because such
   options belong to individual subcommands. The wrapper now changes its
   working directory to `vdp/` and forwards every argument unchanged. This is
   documented at the top of `scripts/vdp-pio.sh` and in ADR-0009.
2. **The hybrid framework has two mandatory Arduino settings that were not
   supplied implicitly.** Initial CMake configuration stopped because
   Arduino-ESP32 requires `CONFIG_FREERTOS_HZ=1000`. After that was supplied,
   linking failed with an undefined `app_main`; enabling
   `CONFIG_AUTOSTART_ARDUINO` makes Arduino-ESP32 provide `app_main` and invoke
   `setup()` and `loop()`. Provenance is the pinned Arduino-ESP32
   `CMakeLists.txt` tick check and `Kconfig.projbuild` AUTOSTART definition.
   Both settings and their reason are inline in `sdkconfig.defaults`.
3. **One partition-table choice feeds two build paths.** Setting
   `board_build.partitions` made PlatformIO's packaged factory image correct,
   but ESP-IDF's auxiliary `flash_args` retained its default `0x10000`
   application offset while this table starts applications at `0x20000`.
   Explicit ESP-IDF custom-table settings in `sdkconfig.defaults` brought both
   manifests into agreement. The synchronization requirement is noted in all
   three participating files.
4. **A QIO build intentionally reports DIO in the initial image header.** This
   looked contradictory during artifact inspection, but pinned pioarduino's
   `builder/main.py::_get_board_flash_mode` explicitly maps QIO/QOUT to a
   ROM-compatible DIO header. The compiled second-stage bootloader contains the
   configured QIO path. This is upstream behavior, not presently classified as
   an upstream bug or a local workaround; physical boot logs still have to
   prove QIO was actually enabled.
5. **PlatformIO generated CMake files despite the no-project-CMake decision.**
   This does not violate ADR-0008: `vdp/CMakeLists.txt` and
   `vdp/video/CMakeLists.txt` are tool-generated adapters, not maintained
   project build logic. Exact ignore rules and explanatory comments preserve
   that boundary.
6. **The initial SDK ignore rule also hid its own tracked input.** The pattern
   `/vdp/sdkconfig.*` correctly ignored the generated environment config but
   also matched `sdkconfig.defaults`. An explicit negated rule now retains the
   defaults file. The warning lives beside the rule because that is where a
   future editor is most likely to need it.
7. **ESP-IDF generated a dependency lock and managed component tree.** The
   managed component sources are reproducible generated material and remain
   ignored. `vdp/dependencies.lock` is retained as a build input because it
   freezes resolved component versions and hashes. It is generated and should
   be refreshed through the package tooling, not hand-edited.
8. **The repeated build initially failed only under the agent filesystem
   sandbox.** PlatformIO needed to update its existing user package locks and
   telemetry cache beneath `~/.platformio`; rerunning with the already approved
   package-cache access succeeded. This was an execution-environment
   restriction, not a repository, toolchain, or firmware defect, and no source
   workaround was introduced for it.
9. **Esptool 4.12 uses underscore operation names.** The first read-only flash
   query used `flash-id`, which this installed version rejected before touching
   flash. The accepted command is `flash_id`. Record exact bench-tool versions
   with commands instead of assuming syntax from another esptool generation.

#### Physical canary run — 2026-08-20

The Author explicitly approved the initial board-mutating qualification. The
stable USB identity was resolved before every operation; commands targeted the
resolved device only after its identity matched.

- Esptool independently reported ESP32-P4 revision 1.3, the expected board
  identity, Winbond-compatible flash ID `ef:4018`, and 16 MiB flash.
- The complete pre-canary 16 MiB flash was saved on the bench Pi as
  `captures/setup-001-20260820/pre-canary-full-flash.bin`; SHA-256 is
  `4e54fe656cef8e048f0d7acf333cb0f21006b16ea431cc9811864f85cab9e604`.
- The staged factory image hash matched the local image:
  `d36d016cd04ba26fd7dd8238add6496608ebfbe366be8fb45c754e5d43e455a7`.
  Its embedded bootloader, partition table, and application had already been
  byte-compared at offsets `0x2000`, `0x8000`, and `0x20000`.
- Flash was erased, the combined canary image was written at `0x0`, and
  esptool's independent `verify_flash` digest comparison passed.
- Reset boot output was preserved on the Pi as
  `captures/setup-001-20260820/canary-reset-boot.log`.

Physical results:

1. **PASS — silicon:** boot and esptool both reported revision 1.3 within the
   configured 1.0–1.99 range.
2. **PASS — flash:** the second-stage bootloader explicitly enabled Winbond
   QIO, then reported QIO at 80 MHz and 16 MiB. The initial ROM line still
   reported DIO as predicted by the compatibility-header investigation.
3. **PASS — partitioning:** boot enumerated the intended NVS, OTA metadata,
   core-dump, two 7 MiB OTA slots, and reserved region, then loaded `ota_0` at
   `0x20000`.
4. **PASS — PSRAM:** boot detected 32 MiB hexadecimal PSRAM at 200 MHz and its
   startup memory test passed.
5. **FAIL — CPU target:** boot reported 360 MHz rather than the accepted
   400 MHz. The generated SDK config confirms
   `CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_360=y`; PlatformIO's board-level `f_cpu`
   declaration did not select ESP-IDF's corresponding Kconfig choice. The next
   canary must set and statically verify the 400 MHz SDK option explicitly.
6. **FAIL — canary report transport:** ESP-IDF console logs appeared through
   USB Serial/JTAG, but the sketch's `Serial` report did not. Pinned
   Arduino-ESP32's `HardwareSerial.h` shows that `Serial` remains UART0 unless
   its USB CDC macros select hardware CDC/JTAG. The next canary must either
   configure Arduino `Serial` for hardware USB CDC deliberately or emit
   qualification evidence through ESP-IDF logging. This was a test-observability
   failure, not evidence that `setup()` failed or that UART0 is defective.

Because an essential target failed, the complete pre-canary backup was restored
at `0x0` after a clean erase. The full 16 MiB restore passed independent
`verify_flash`, and `restored-reset-boot.log` confirms that the prior
`agon_extender` firmware boots from its original factory partition at
`0x10000`. The board is therefore back at its pre-test firmware state.

Do not repeat the physical canary until the two failed assumptions are corrected
and the resulting generated configuration and output path are reviewed. The
SETUP-002 gate still applies before broader or repeated firmware work.

#### Canary r02 qualification candidate

SETUP-002 is complete and its accepted identity policy now governs this work.
The Author also directed that r02 must not back up the board's existing flash:
the current firmware is reproducible from the retained legacy repository.

Candidate identities:

- `setup-001-canary-r02`
- `olimex-p4-devkit-profile-r02`
- `p4-ota-partition-layout-r01`
- `p4-bringup-procedure-r02`

Corrections and findings:

1. The r01 CPU result was not merely a failed PlatformIO board-JSON
   propagation. Pinned ESP-IDF 5.5.5 deliberately defaults pre-v3 P4 silicon
   to 360 MHz and hides its 400 MHz choice behind
   `ESP_FORCE_400MHZ_ON_REV_LESS_V3`. Its Kconfig warns that 400 MHz requires
   additionally qualified chips. R02 enables that gate under the already
   accepted Olimex vendor-rating decision in ADR-0010. The exception and its
   provenance are prominent in `sdkconfig.defaults`.
2. R02 uses ESP-IDF logging for its complete identity and hardware report. This
   preserves Arduino's upstream `Serial`→UART0 mapping and uses the USB
   Serial/JTAG log path proven during r01 rather than introducing an unrelated
   USB-CDC remapping solely for a temporary canary.
3. The tracked source identity is in `vdp/version.yaml` and
   `video/extender/version.h`. Qualification compilation requires an injected
   UTC build ID; ordinary builds visibly report themselves as unidentified and
   experimental.
4. `docs/procedures/p4-canary-r02.md` is the controlled no-backup procedure. It
   requires a clean candidate commit, exact build/run evidence, write
   verification, an initial boot, and three repeat reset boots.
5. An exploratory pre-commit build passed. Generated SDK configuration now
   explicitly selects the pre-v3 force gate and 400 MHz choice. The resulting
   binary contains the source identity and temporary unqualified-build marker;
   it is not the qualification binary.

No inherited upstream defect has yet required a local patch. If one does, its
inline marker must identify the upstream project and pinned version or commit,
the observed failure, any upstream issue or source location, the local remedy,
and the condition under which the remedy may be removed.

### SETUP-001.2 — Build the VDP architecture précis

- Status: Approved for planning; not started
- Create a reusable VDP architecture subject précis. Its durable location will
  be selected when that documentation work begins. It should
  describe the official VDP project rather than prescribe Extender-specific
  implementation work.

#### Pass A — Project and coding structure

1. Map the official VDP directory and filename structure, including the purpose
   and ownership of each major directory and important root file.
2. Explain how PlatformIO discovers, configures, compiles, links, and packages
   the firmware, and identify the roles of `platformio.ini`, environments,
   framework configuration, libraries, source filters, and generated outputs.
3. Describe the project's coding structure: entry points, translation units,
   headers, global/shared state, classes, modules, libraries, configuration,
   and conditional compilation.
4. Distinguish upstream Agon-owned code, third-party code such as FabGL/vdp-gl,
   generated material, and target- or board-specific code.
5. Explain the C/C++ and embedded-development concepts in plain language, with
   concrete file examples and SQL/eZ80 analogies where helpful.
6. Record exact links to the official documentation and source files supporting
   each major conclusion. Include only short excerpts needed to remove
   ambiguity.

#### Pass B — Runtime architecture and integration surfaces

1. Trace startup from reset/framework entry through VDP initialization and the
   steady-state main loop or task structure.
2. Identify external interfaces and contracts, including communication with
   MOS/eZ80, serial protocols, keyboard and mouse input, video output, audio
   output, storage or filesystem use, debug/programming interfaces, and any
   network-related facilities already present.
3. Trace the major input paths: where bytes, commands, events, and assets enter;
   how they are parsed or dispatched; and which state or subsystem consumes
   them.
4. Trace the major output paths: framebuffer/video generation, audio samples,
   keyboard or mouse responses, protocol replies, diagnostics, and firmware
   update behavior.
5. Identify major insertion points for ESP32-P4 portability, board adaptation,
   Extender transports, Ethernet/browser presentation, P4-local storage, and
   future extended functions.
6. Classify each insertion point as an existing abstraction, a narrow patch, a
   target-specific replacement, or a likely upstream conflict. Explain why.
7. Identify global state, timing assumptions, concurrency/tasks, interrupts,
   buffering, ownership, memory constraints, and hardware dependencies that
   could make a superficially simple port unsafe.
8. Produce small control-flow and data-flow diagrams only where they make the
   architecture materially easier to understand.

#### Teaching and review deliverables

1. Maintain a glossary of C/C++, PlatformIO, ESP-IDF, and software-architecture
   terms encountered during the analysis.
2. For every major subsystem, answer: what it does, where it starts, what data
   enters, what data leaves, what state it owns, what calls it, and what it
   calls.
3. Separate verified facts from interpretation, recommendations, and unresolved
   questions.
4. Summarize findings with the Author in manageable sections and invite
   questions before using them to make Extender architecture decisions.
5. Stop for Author review of the completed précis before translating its
   findings into a porting or modification plan.

## Dependencies and references

- Official documentation: [agon-docs](https://github.com/AgonPlatform/agon-docs)
- Official VDP source: [agon-vdp](https://github.com/AgonPlatform/agon-vdp)
- Official MOS source: [agon-mos](https://github.com/AgonPlatform/agon-mos)

## Task précis

SETUP-001.2 will create the reusable VDP architecture précis. Task-specific
setup findings and instructions remain in this file.

## Decisions and assumptions

1. Full stock-VDP backward compatibility is a product guarantee and therefore
   an architectural requirement, not a later enhancement.
2. Extender's VDP begins as a port of the stock firmware rather than a rewrite
   or a merely behavior-compatible independent implementation.
3. Near-identical source names and locations are required to make continuing
   upstream support tractable.
4. Structural fidelity takes precedence over local aesthetic preferences unless
   the P4 target makes an upstream structure technically impossible.
5. The `extender/` subfolder owns new Extender capabilities and extended
   functions and will be located at `vdp/video/extender/`. See tracked
   [ADR-0001](../decisions/ADR-0001-vdp-source-layout.md).
6. The complete PlatformIO project and VDP firmware will live under the
   repository's top-level `vdp/` directory.

## Decision register

| ID | Decision | Status | Choice or next question | Durable record |
|---|---|---|---|---|
| SETUP-D001 | Extender source location | Accepted | `vdp/video/extender/` | `docs/decisions/ADR-0001-vdp-source-layout.md` |
| SETUP-D002 | Initial firmware framework | Accepted | Hybrid Arduino/ESP-IDF, subject to canary qualification | `docs/decisions/ADR-0002-hybrid-firmware-framework.md` |
| SETUP-D003 | Platform package baseline | Accepted | Pin pioarduino `55.03.311`, subject to canary qualification | `docs/decisions/ADR-0003-pioarduino-platform-baseline.md` |
| SETUP-D004 | P4 chip-variant identity | Accepted | `esp32p4_es` with explicit full revision range 100–199 | `docs/decisions/ADR-0004-p4-silicon-identity.md` |
| SETUP-D005 | Flash bus mode | Accepted | Qualify QIO at 80 MHz; retain DIO at 80 MHz as fallback | `docs/decisions/ADR-0005-flash-bus-mode.md` |
| SETUP-D006 | Board memory declaration | Accepted | 512,000-byte internal link budget; separate 32 MB hex PSRAM at 200 MHz | `docs/decisions/ADR-0006-board-memory-model.md` |
| SETUP-D007 | Firmware partition layout | Accepted | Two 7 MiB OTA slots, rollback, no factory app, remaining space reserved | `docs/decisions/ADR-0007-flash-partition-strategy.md` |
| SETUP-D008 | Hybrid CMake boundary | Accepted | Start without project-authored CMake; add only the minimum proven necessary | `docs/decisions/ADR-0008-minimal-cmake-boundary.md` |
| SETUP-D009 | PlatformIO command wrapper | Accepted | Transparent `scripts/vdp-pio.sh` pass-through using root `.venv` | `docs/decisions/ADR-0009-platformio-wrapper.md` |
| SETUP-D010 | CPU frequency | Accepted | Qualify vendor-rated 400 MHz; retain 360 MHz as diagnostic fallback | `docs/decisions/ADR-0010-cpu-frequency.md` |

## Unresolved questions

1. Additional implementation subtasks remain to be developed and reviewed.
2. The depth and boundaries of the VDP architecture précis will be refined as
   Pass A reveals the actual upstream structure.

## Affected implementation

To be determined during subtask review.

## Validation gates

To be determined during subtask review.
