# SETUP-001.1 — Proposed VDP setup and layout manifest

Status: DRAFT — Author review required before creating `vdp/`

## 1. Audit identity and boundaries

This manifest compares:

1. Official [Agon VDP](https://github.com/AgonPlatform/agon-vdp) checkout
   - Branch: `main`
   - Commit: `c7ac293d2aa81ddfa693390549bcd909069c8fc3`
   - Working tree: clean at inspection
2. Private legacy Agon Extender checkout
   - Branch: `main`
   - Commit: `df54cf6a7a23cd40e98076856f68cff0559d1c77`
   - Working tree: clean at inspection

The official VDP is authoritative for source shape and compatibility behavior.
The legacy project is evidence for the physical Olimex P4 board and its build
toolchain, not an architectural template for the new firmware.

## 2. Official `agon-vdp` inventory

### 2.1 Root and build files

| Path | Role |
|---|---|
| `platformio.ini` | Complete PlatformIO definition; sets `src_dir = video` and the `esp32dev` Arduino environment. |
| `README.md` | Project purpose, VDP summary, official documentation link, and PlatformIO build guidance. |
| `LICENSE` | Upstream MIT license. |
| `.gitignore` | Ignores editor state and `video/build`. |
| `.github/workflows/build.yml` | Runs `pio run` on Linux, Windows, and macOS. |
| `.github/FUNDING.yml` | Upstream project metadata; not firmware input. |

The official PlatformIO environment is deliberately small:

- source directory: `video`;
- framework: Arduino;
- board: generic `esp32dev`;
- platform: `espressif32@6.6.0`;
- CPU: 240 MHz;
- flash: 80 MHz, QIO;
- C++: GNU++17;
- optimization: `-O2`;
- dependencies: `AgonPlatform/vdp-gl#all-the-plots`, ESP32Time, and CRC;
- monitor: 115200 baud; and
- upload: 600000 baud.

### 2.2 Firmware source shape

The tracked firmware is one Arduino sketch plus headers under `video/`.
`video/video.ino` owns `setup()`, `loop()`, global subsystem instances, and the
main processing task. The headers contain most subsystem implementations, so
preserving filenames and relative includes is especially important.

The complete upstream directory grouping is:

```text
video/
  video.ino
  OneWire_direct_gpio.h
  agon.h
  agon_audio.h
  agon_fonts.h
  agon_palette.h
  agon_ps2.h
  agon_screen.h
  agon_ttxt.h
  audio_channel.h
  audio_sample.h
  buffer_stream.h
  buffers.h
  compression.h
  context.h
  enhanced_samples_generator.h
  hexload.h
  mem_helpers.h
  multi_buffer_stream.h
  span.h
  sprites.h
  ttxtfont.h
  types.h
  updater.h
  vdp_protocol.h
  vdp_variables.h
  vdu.h
  vdu_audio.h
  vdu_buffered.h
  vdu_context.h
  vdu_fonts.h
  vdu_layers.h
  vdu_sprites.h
  vdu_stream_processor.h
  vdu_sys.h
  version.h
  ymodem.h
  zdi.h
  context/
    cursor.h
    fonts.h
    graphics.h
    viewport.h
  envelopes/
    adsr.h
    frequency.h
    multiphase_adsr.h
    types.h
  utils/
    thread_safe_variant_deque.h
```

## 3. Reusable legacy P4 setup evidence

### 3.1 Qualified or strongly evidenced facts

| Concern | Legacy evidence | Disposition |
|---|---|---|
| Physical board | Olimex ESP32-P4-DevKit Rev D1 with ESP32-P4NRW32 | Retain as target identity. |
| P4 platform | pioarduino platform commit `9905818f69da26fffb7b6871b5b99523eba91890` | Reuse initially as a reproducible known package set; reassess before long-term pinning. |
| ESP-IDF | v5.5.5, commit `b774170ff46c393eeb5e495ea37936038d3f4f4f` | Known hardware-qualified IDF baseline. |
| PlatformIO Core | 6.1.19 | Reuse as the initial pinned project tool version. |
| Board definition | `boards/olimex_esp32_p4_devkit.json` | Adapt rather than copy blindly; add Arduino support and review RAM semantics. |
| CPU/flash/PSRAM | 400 MHz CPU, 80 MHz flash, 200 MHz 32 MB hex-mode PSRAM | Retain as target configuration, subject to first-build and hardware checks. |
| Flash capacity | 16 MB | Retain. |
| Silicon family | Physical chip reports v1.3 and requires the pre-v3 family selection | Retain `CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y` and minimum revision v1.0 until hardware evidence supersedes it. |
| Programming console | USB Serial/JTAG | Retain for development console and upload/monitor qualification. |
| Ethernet PHY | IP101GRR, address 1, MDC GPIO31, MDIO GPIO52, reset GPIO51 | Proven by NET-00/NET-01; keep for later `extender/` networking, not initial compatibility-port setup. |
| PlatformIO isolation | Wrapper sets a project-local `PLATFORMIO_CORE_DIR` | Reuse concept, adjusted to the new repository and existing root `.venv`. |
| Native reference build | ESP-IDF v5.5.5 used as authority when PlatformIO differed | Preserve as a diagnostic fallback, not as a second production source tree. |

### 3.2 Legacy material not adopted as the new baseline

1. Root `src/`, `src/modules/`, `app_main`, and `P4_APP_FEATURE` selection:
   these belong to the aborted feature-bundle architecture and would destroy
   the official VDP source shape.
2. Legacy `vdp/agon`, `vdp/common`, `vdp/p4`, parser skeletons, compatibility
   copies, and portable replacement layers: these are useful historical
   evidence but are not a faithful upstream port.
3. AGM, web presentation, transport diagnostics, fixtures, and benchmark trees:
   do not import them during baseline setup. Reconsider individual proven
   implementations later under `vdp/video/extender/`.
4. Generated `sdkconfig` and `sdkconfig.p4`: generated outputs are not source
   configuration and contain broad incidental defaults.
5. Single-app partition selection from the legacy generated configuration: the
   official VDP contains OTA update behavior and expects a safe update model.
   Partitioning requires its own explicit decision and cannot be inherited from
   an experimental single-app image.
6. `CONFIG_COMPILER_OPTIMIZATION_DEBUG=y`: useful during bring-up but not yet
   accepted as the port baseline; upstream uses `-O2`.
7. Ethernet and HTTP options in legacy `sdkconfig.defaults`: proven, but they
   belong to Extender networking and should not contaminate the first stock-VDP
   compatibility build.

## 4. Framework decision

### 4.1 Verified facts

1. Official `agon-vdp` is an Arduino project and directly uses Arduino APIs,
   Arduino `Stream`, `HardwareSerial`, ESP32Time, and Arduino-oriented vdp-gl.
2. Espressif currently lists ESP32-P4 as supported by Arduino-ESP32.
3. The locally installed pioarduino platform advertises both `arduino` and
   `espidf` and contains supported hybrid `framework = arduino, espidf`
   examples.
4. The legacy Olimex board JSON artificially restricts its frameworks list to
   `espidf`; the same local platform's P4 board definitions permit both.
5. Pure ESP-IDF was hardware-qualified in the legacy project. Arduino or hybrid
   operation on this exact Olimex Rev-D1 board has not yet been qualified here.

### 4.2 Accepted direction

Use a hybrid `arduino, espidf` environment as the first candidate. In database
terms, Arduino preserves the application-facing schema expected by the
upstream source, while ESP-IDF exposes the lower-level board and build controls
needed for P4 hardware. This is the narrowest plausible route to both source
fidelity and P4 configuration control.

The Author accepted this direction as `SETUP-D002`. PlatformIO remains the
familiar outer project and command workflow used by upstream; the selected
frameworks operate beneath it. The first implementation gate must be a
minimal hybrid canary on the physical Rev-D1 board proving:

1. correct pre-v3 silicon image selection;
2. boot through USB Serial/JTAG;
3. Arduino `setup()` and `loop()` execution;
4. correct 32 MB PSRAM discovery and allocation;
5. expected CPU and flash frequencies; and
6. a clean reset/reflash cycle.

If hybrid mode cannot satisfy those gates, evaluate Arduino-only next. A pure
ESP-IDF rewrite is the last choice because it creates the largest and least
maintainable delta from official `agon-vdp`.

## 5. Comparison matrix

| Concern | Official VDP | Legacy P4 | Proposed Extender |
|---|---|---|---|
| Project root | Repository root | Repository root | `vdp/` subproject |
| PlatformIO config | Root `platformio.ini` | Root `platformio.ini` | `vdp/platformio.ini`, preserving upstream filename |
| Source directory | `video/` | `src/` | `vdp/video/`, exact upstream relative shape |
| Entry point | `video/video.ino`, Arduino `setup/loop` | `src/app_module.c`, IDF `app_main` | Preserve `video/video.ino` and qualify Arduino/hybrid startup |
| Framework | Arduino | ESP-IDF | Candidate: Arduino + ESP-IDF hybrid |
| Platform package | `espressif32@6.6.0` | Pinned pioarduino commit | Pin pioarduino release `55.03.311`; retain the legacy commit as a hardware-reference fallback |
| Target board | `esp32dev` | Custom Olimex P4 JSON | Adapted custom Olimex P4 JSON with Arduino and ESP-IDF permitted |
| CPU architecture | Xtensa ESP32, 240 MHz | RISC-V P4, 400 MHz | RISC-V P4, 400 MHz; isolate architecture-specific source deltas |
| Flash | QIO, 80 MHz; board defaults | 16 MB, generated config used DIO | Qualify QIO at 80 MHz; retain DIO at 80 MHz as fallback |
| Memory | Original board assumptions | Legacy board JSON conflated 32 MB PSRAM with ordinary RAM | 512,000-byte internal link budget; separate 32 MB hex PSRAM at 200 MHz; verify and test at boot |
| Silicon revision | Not applicable | Rev v1.3/pre-v3 family required | `esp32p4_es`; explicit full revision range 100–199; verify at runtime |
| C++ version | GNU++17 | C plus selected GNU++17 files | Preserve GNU++17 globally as upstream does |
| Optimization | `-O2` | IDF debug optimization | Begin with upstream `-O2` unless bring-up diagnostics require a named temporary environment |
| VDP library | `vdp-gl#all-the-plots` | Portable compatibility experiments | Start with same dependency and determine P4 compile/runtime deltas |
| Additional features | Mixed into stock firmware history | Feature modules throughout tree | New work only under `vdp/video/extender/`, with narrow calls from upstream-shaped code |
| Configuration | PlatformIO flags | `sdkconfig.defaults` plus generated configs | Minimal tracked `sdkconfig.defaults`; no generated sdkconfig committed initially |
| Partitions | Arduino board default, updater present | Generated single-app layout | Explicit OTA/update-compatible design required; do not inherit single-app layout |
| Unit tests | CI build only | Native Unity and Python suites | Add tests later without moving upstream firmware files |
| Build wrapper | Direct `pio run` | `tools/pio` with isolated core | Project-local wrapper or documented root-venv command; exact placement pending review |
| Emulator | Upstream supports `USERSPACE` conditionals | Bespoke experimental profile | Separate later task and mandatory Author validation gate |

## 6. Proposed exact initial tree

Classification tags:

- `[U]` upstream-shaped file retained at the same path relative to the VDP
  project;
- `[P]` P4/board/build adaptation;
- `[E]` Extender-owned code;
- `[S]` project support; and
- `[O]` intentionally omitted from initial setup.

```text
vdp/
  platformio.ini                         [U/P]
  CMakeLists.txt                         [P] candidate hybrid-build support
  sdkconfig.defaults                     [P] minimal hardware defaults only
  boards/
    olimex_esp32_p4_devkit.json          [P]
  video/                                 [U]
    video.ino                            [U]
    OneWire_direct_gpio.h                [U]
    agon.h                               [U]
    agon_audio.h                         [U]
    agon_fonts.h                         [U]
    agon_palette.h                       [U]
    agon_ps2.h                           [U]
    agon_screen.h                        [U]
    agon_ttxt.h                          [U]
    audio_channel.h                      [U]
    audio_sample.h                       [U]
    buffer_stream.h                      [U]
    buffers.h                            [U]
    compression.h                        [U]
    context.h                            [U]
    enhanced_samples_generator.h         [U]
    hexload.h                            [U]
    mem_helpers.h                        [U; expected narrow RISC-V delta]
    multi_buffer_stream.h                [U]
    span.h                               [U]
    sprites.h                            [U]
    ttxtfont.h                           [U]
    types.h                              [U]
    updater.h                            [U; partition contract unresolved]
    vdp_protocol.h                       [U; board UART pins unresolved]
    vdp_variables.h                      [U]
    vdu.h                                [U]
    vdu_audio.h                          [U]
    vdu_buffered.h                       [U]
    vdu_context.h                        [U]
    vdu_fonts.h                          [U]
    vdu_layers.h                         [U]
    vdu_sprites.h                        [U]
    vdu_stream_processor.h               [U]
    vdu_sys.h                            [U]
    version.h                            [U]
    ymodem.h                             [U]
    zdi.h                                [U; hardware support unresolved]
    context/                             [U]
      cursor.h                           [U]
      fonts.h                            [U]
      graphics.h                         [U]
      viewport.h                         [U]
    envelopes/                           [U]
      adsr.h                             [U]
      frequency.h                        [U]
      multiphase_adsr.h                  [U]
      types.h                            [U]
    utils/                               [U]
      thread_safe_variant_deque.h        [U]
    extender/                            [E]
      README.md                          [E] ownership boundary only initially
```

Support files outside `vdp/` are not part of this manifest. The repository
already owns its root `.venv`, ignored `agents/`, TODO, README, and licensing.

## 7. Proposed deviations from official `agon-vdp`

| Deviation | Reason | Containment boundary |
|---|---|---|
| Entire PlatformIO project nested under repository `vdp/` | Product repository will contain more than firmware | One directory prefix only; all upstream-relative paths beneath it remain stable |
| Custom Olimex board JSON | Official environment targets generic original ESP32 | `vdp/boards/olimex_esp32_p4_devkit.json` |
| pioarduino platform instead of official PlatformIO `espressif32@6.6.0` | Mainline PlatformIO still does not provide practical P4 Arduino support | `vdp/platformio.ini` pin |
| Candidate hybrid Arduino/ESP-IDF framework | Preserve upstream Arduino source while controlling P4 IDF configuration | Build files only unless qualification proves source changes necessary |
| Root CMake file under `vdp/` | Hybrid builds may require ESP-IDF project metadata | `vdp/CMakeLists.txt`; avoid adding CMake structure inside upstream `video/` if PlatformIO can generate it |
| Minimal `sdkconfig.defaults` | Rev-D1 silicon, PSRAM, flash, and USB console need explicit settings | `vdp/sdkconfig.defaults` |
| `video/extender/` subtree | Required ownership boundary for new product features | PlatformIO discovers it beneath `src_dir = video`; existing upstream files remain in place and integration calls must be explicit |
| Architecture and pin conditionals | P4 is RISC-V and uses different peripherals/pins | Prefer target headers or minimal `#if` blocks; enumerate every changed upstream file during implementation |

## 8. Intentional initial omissions

1. Legacy root `src/`, modules, common protocols, web UI, AGM, transport, tests,
   and tools.
2. Legacy generated `sdkconfig` and `sdkconfig.p4`.
3. Legacy single-app partition selection.
4. Ethernet/HTTP configuration and implementation; qualified evidence is
   retained for later Extender networking tasks.
5. Parallel transport implementation; qualified evidence is retained for a
   later transport task.
6. MIPI display, HDMI, SD-card application storage, wireless module, firmware
   flashing, FTP, Gopher, and installed-application features.
7. Emulator adaptation or custom VDP module.
8. Copies of upstream README, workflow, funding metadata, or root license inside
   `vdp/`; licensing/provenance treatment needs a separate explicit review.

## 9. Unresolved decisions before scaffolding

1. Approve reuse of the exact legacy pioarduino commit for reproducibility, or
   qualify and pin a current stable pioarduino release first.
2. Determine the correct custom-board `chip_variant` for physical v1.3 silicon
   under the selected Arduino package (`esp32p4_es` versus current naming).
3. Reconcile board JSON `flash_mode = qio` with the legacy generated IDF result
   of DIO and the Olimex/vendor hardware guidance.
4. Correctly represent internal RAM versus 32 MB external PSRAM in the board
   JSON; the legacy `maximum_ram_size = 33554432` should not be accepted merely
   because builds succeeded.
5. Implement the accepted two-slot OTA strategy: two 7 MiB application slots,
   rollback validation, no factory application, and reserved remainder. Freeze
   exact offsets only after validating the hybrid toolchain's requirements.
6. Begin without project-authored CMake. Add a `vdp/CMakeLists.txt` or component
   file only if the minimal hybrid canary demonstrates that PlatformIO cannot
   establish the required component boundary itself.
7. Add transparent `scripts/vdp-pio.sh` pass-through using the repository root
   `.venv`, while keeping `vdp/` a normal standalone PlatformIO project.
8. Qualify Olimex's vendor-rated 400 MHz CPU configuration under sustained and
   mixed load; retain 360 MHz as the controlled diagnostic fallback.

## 10. Recommended first implementation slice after approval

Do not import the VDP source first. Build and physically qualify a minimal
hybrid P4 canary using only the proposed board definition and hardware defaults.
After it passes, copy the exact tracked upstream `video/` tree without edits and
attempt a compile. That failure inventory becomes the evidence-based porting
plan; it is preferable to predicting and pre-editing every incompatibility.

The ordered gates should be:

1. minimal hybrid build;
2. inspect image target/revision metadata;
3. physical flash and USB-console boot;
4. CPU/flash/PSRAM identity checks;
5. clean reset and reflash;
6. exact upstream tree import;
7. unmodified compile attempt;
8. classified failure inventory; and
9. Author review before source adaptation.

## 11. Evidence consulted

Official VDP checkout:

- `platformio.ini`
- `video/video.ino`
- `video/agon.h`
- `video/vdp_protocol.h`
- `video/updater.h`
- `.github/workflows/build.yml`
- `README.md`

Local legacy evidence:

- `platformio.ini`
- `boards/olimex_esp32_p4_devkit.json`
- `sdkconfig.defaults`
- `docs/development.md`
- `docs/provenance.md`
- `docs/net-00-results.md`
- `docs/net-01-results.md`
- `src/CMakeLists.txt`
- `tools/pio`
- `requirements-dev.txt`

Current external primary references:

- https://github.com/espressif/arduino-esp32/blob/master/docs/en/getting_started.rst
- https://docs.espressif.com/projects/arduino-esp32/en/latest/libraries.html
- https://github.com/pioarduino/platform-espressif32
