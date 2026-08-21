# SETUP-003 Work 3 upstream control build

Validation date: 2026-08-20

## Result

Official Agon VDP tag `v2.16.0` built and linked successfully from a fresh
temporary detached checkout at
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`. The release's `platformio.ini`,
source, dependencies, and build configuration were not modified. Nothing was
uploaded and no physical board operation occurred.

The authoritative machine-readable record is
[`../generated/control-build.yaml`](../generated/control-build.yaml).

The accepted isolated build resolved:

- PlatformIO Core 6.1.19;
- Espressif32 platform 6.6.0;
- Arduino-ESP32 framework 2.0.14
  (`framework-arduinoespressif32` 3.20014.231204);
- Xtensa ESP32 GCC 8.4.0 (`8.4.0+2021r2-patch5`);
- esptool.py 4.5.1 (`tool-esptoolpy` 1.40501.0);
- vdp-gl 1.0.5 at
  `ac2dd5986daf496c43ae8e7fe41836274aec54a0`;
- ESP32Time 2.0.6; and
- CRC 1.0.4.

PlatformIO reported 44,688 of 327,680 RAM bytes and 1,077,253 of 1,310,720
application-partition bytes used. The generated ELF, binary, and map identities
are recorded by size and SHA-256 without retaining those bulky artifacts.

## Control method and gotchas

The first build used the normal shared PlatformIO package directory. PlatformIO
reported that the selected platform required Xtensa toolchain
`8.4.0+2021r2-patch5`, but the package actually installed under that shared
name was GCC 12.2.0 from later P4 work. That build succeeded, but it was rejected
as the control because the globally reused package did not match the resolved
identity.

The accepted build set `PLATFORMIO_CORE_DIR` to a dedicated temporary directory.
PlatformIO then downloaded Espressif32 6.6.0 and the actual 8.4.0 toolchain into
that isolated store. Future qualified control builds must isolate the complete
PlatformIO core/package directory; isolating only the source checkout is
insufficient.

Other observed upstream/tool behavior:

- `platformio.ini` configures QIO, but the generated application image header
  encodes DIO. This is recorded as observed behavior and was not corrected.
- Arduino-ESP32 2.0.14 emits a warning in `esp32-hal-uart.c` where
  `uartSetPins` returns without a value. It does not fail the build.
- esptool.py 4.5.1 emits a Python 3.14 `SyntaxWarning` concerning a `return` in
  a `finally` block. It does not fail image generation.
- Running from `/tmp` requires the project-local PlatformIO executable to be
  addressed by its absolute path.

## Stock-to-P4 compilation comparison

The stock compilation database contains 96 total entries: the VDP sketch, 40
declared-dependency translation units, and framework implementation units. The
normalized P4 database intentionally retains the 40 dependency units but not
the transient generated sketch unit.

After normalizing environment-directory names, both experiments select exactly
the same dependency sources:

- 31 vdp-gl translation units;
- one ESP32Time translation unit; and
- eight CRC translation units.

No stock-only or P4-only dependency translation unit was found. Work 4's source
selection finding therefore requires no correction.

The expected material command differences are:

- stock uses `xtensa-esp32-elf-g++`; P4 uses `riscv32-esp-elf-g++`;
- stock uses the Xtensa PSRAM-cache workaround and `-mlongcalls`; P4 uses the
  ESP32-P4 RISC-V `-march` setting;
- stock exposes Arduino-ESP32 2.0.14 / IDF 4.4.6 target definitions; P4 exposes
  Arduino/IDF 5.5.5 and ESP32-P4 definitions; and
- the representative vdp-gl compile command has 192 stock include paths versus
  294 in the hybrid P4 environment.

Both commands retain `-O2`, `c++17`, `gnu++17`, `BOARD_HAS_PSRAM`,
`ARDUINO_ARCH_ESP32`, and `ESP_PLATFORM`. The hybrid P4 command additionally
contains `gnu++2b` from its framework layer; this does not alter the conclusion
that upstream dependency source selection itself was unchanged.
