# Agon Extender Architecture

This document describes the current accepted architecture. Open questions and
implementation work belong in `TODO.md` and the corresponding tracked files
under `docs/tasks/` rather than here.

## VDP firmware lineage

Agon Extender's VDP firmware begins as a faithful port of the official Agon VDP
to the ESP32-P4. Full backward compatibility with existing Agon software is a
product requirement.

The port preserves official directory names, filenames, relative source
locations, and recognizable code wherever the target permits. P4-specific
changes should be narrow and explicit so maintainers can compare the port with
upstream and incorporate future official changes without reconstructing
equivalent modules under unrelated names.

## Repository layout

The complete PlatformIO project and VDP firmware live under the repository's
top-level `vdp/` directory. Within that project, `vdp/video/` mirrors the
official VDP source directory.

New Extender capabilities and extended functions live under:

```text
vdp/video/extender/
```

This location is inside the firmware source directory selected by the official
PlatformIO project while retaining a clear ownership boundary. Existing
upstream files remain at their official relative paths. Calls between the
upstream-shaped compatibility port and Extender-owned modules must use narrow,
documented integration points.

The rationale and consequences of this placement are recorded in
[ADR-0001](decisions/ADR-0001-vdp-source-layout.md).

## Change boundaries

The upstream-shaped compatibility port owns stock VDP behavior. The
`video/extender/` subtree owns capabilities that do not exist in the official
firmware.

Target adaptation should follow this preference order:

1. retain upstream code unchanged;
2. isolate board or architecture differences in target-specific support code;
3. use a small conditional or insertion point in an upstream-shaped file when
   isolation is impractical; and
4. replace an upstream implementation only when the P4 target makes the
   original mechanism unavailable.

Every deviation from upstream should remain attributable to a verified target
requirement or an accepted Extender feature.

## Firmware build model

PlatformIO remains the outer project, dependency, build, upload, and monitoring
workflow, preserving the official VDP project's familiar development idioms.
The ESP32-P4 environment combines the Arduino and ESP-IDF frameworks.

Arduino preserves the application-level structure expected by official
`agon-vdp`, including its sketch entry point and Arduino-oriented APIs and
libraries. ESP-IDF supplies the lower-level target configuration and native P4
facilities needed for silicon revision handling, memory, partitions, USB,
Ethernet, multimedia peripherals, and future Extender functions.

The hybrid framework choice must pass a minimal build and physical-board canary
before it becomes the foundation for source adaptation. See
[ADR-0002](decisions/ADR-0002-hybrid-firmware-framework.md).

The initial build pins pioarduino platform release `55.03.311`, which combines
Arduino-ESP32 3.3.11 with ESP-IDF 5.5.5. A moving release alias or development
branch is not an acceptable reproducible baseline. See
[ADR-0003](decisions/ADR-0003-pioarduino-platform-baseline.md).

The Rev-D1 development board's v1.3 ESP32-P4 is represented as the pre-v3
`esp32p4_es` platform variant. SDK configuration explicitly limits compatible
full revisions to 100 through 199, and board qualification reports and checks
the runtime revision. See
[ADR-0004](decisions/ADR-0004-p4-silicon-identity.md).

The primary board environment configures the 16 MB SPI flash for QIO at
80 MHz. This is a qualification candidate until cold-boot, reset, reflash, and
flash-integrity tests pass on the physical board. DIO at 80 MHz is the defined
fallback if QIO proves unreliable. See
[ADR-0005](decisions/ADR-0005-flash-bus-mode.md).

The board definition uses a conservative 512,000-byte internal-RAM link budget
and declares external PSRAM separately. The 32 MB PSRAM operates in hexadecimal
mode at 200 MHz and is intended for explicit bulk allocation; it is not treated
as interchangeable with internal SRAM. Bring-up verifies its capacity and runs
a memory test. See [ADR-0006](decisions/ADR-0006-board-memory-model.md).

The 16 MB flash contains two equal 7 MiB OTA application slots. A candidate
image is written to the inactive slot and must pass an explicit post-boot health
check before it is marked valid; otherwise the bootloader rolls back. There is
no separately maintained factory application. Required NVS, OTA metadata, and
crash diagnostics use the leading data area, and the approximately 1.9 MiB
remainder stays reserved until a durable use is approved. See
[ADR-0007](decisions/ADR-0007-flash-partition-strategy.md).

PlatformIO owns hybrid project orchestration. The project begins without
project-authored CMake files; a tracked `CMakeLists.txt` is added only when a
specific build requirement demonstrates that PlatformIO's generated hybrid
structure is insufficient. Any such file must be the smallest boundary needed
and must not reorganize the upstream-compatible `video/` tree. See
[ADR-0008](decisions/ADR-0008-minimal-cmake-boundary.md).

The tracked `scripts/vdp-pio.sh` wrapper locates the repository root, requires
the root `.venv/bin/pio`, selects `vdp/` as the PlatformIO project directory,
and forwards PlatformIO arguments unchanged. It performs no implicit build,
upload, installation, port selection, or environment activation. Direct
PlatformIO invocation remains supported. See
[ADR-0009](decisions/ADR-0009-platformio-wrapper.md).

The primary board environment configures the CPU at the vendor-rated 400 MHz.
This remains subject to sustained CPU, flash, PSRAM, and mixed-load physical
qualification. A 360 MHz environment or override is retained solely as a
controlled diagnostic fallback for frequency-correlated failures. See
[ADR-0010](decisions/ADR-0010-cpu-frequency.md).
