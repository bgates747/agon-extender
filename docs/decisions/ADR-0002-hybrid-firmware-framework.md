# ADR-0002 — Use PlatformIO with Arduino and ESP-IDF together

- Status: Accepted
- Date: 2026-08-20

## Context

Official `agon-vdp` is a PlatformIO Arduino project. Its source depends on the
Arduino sketch lifecycle, `Stream`, `HardwareSerial`, and Arduino-oriented
libraries including vdp-gl. Preserving those idioms and source locations is
important for upstream maintainability.

The ESP32-P4 target also needs lower-level configuration and facilities exposed
through ESP-IDF. These include control over the physical chip revision, PSRAM,
partitioning, USB Serial/JTAG, Ethernet, MIPI, PARLIO, and other P4-specific
peripherals. The legacy project qualified the Olimex board using pure ESP-IDF,
but adopting its `app_main` and component architecture would create a large
structural delta from official `agon-vdp`.

Three approaches were considered:

1. Arduino-only, which most closely resembles upstream but may limit target
   configuration or rely on fixed precompiled framework choices;
2. pure ESP-IDF, which provides maximum target control but would require the
   largest rewrite; and
3. hybrid Arduino and ESP-IDF, preserving Arduino application interfaces while
   building them within an ESP-IDF-controlled project.

## Decision

Retain PlatformIO as the outer project and development workflow. Configure the
initial ESP32-P4 environment with both frameworks:

```ini
framework = arduino, espidf
```

Treat this as the accepted candidate architecture subject to a minimal hybrid
build and physical-board qualification gate before importing or adapting the
official VDP source.

## Reasons

1. PlatformIO preserves the upstream project's familiar build and dependency
   idioms.
2. Arduino preserves the stock VDP's application-facing source structure and
   APIs.
3. ESP-IDF provides the P4-specific build and hardware controls required by the
   product.
4. The locally inspected pioarduino platform supports hybrid projects and
   provides worked examples.
5. The approach minimizes the risk of beginning with an ESP-IDF rewrite that is
   difficult to compare with or update from upstream.

## Consequences

1. The project gains CMake and ESP-IDF component concepts in addition to
   PlatformIO and Arduino concepts.
2. Framework and package versions must be pinned and qualified as one coherent
   toolchain.
3. Arduino `setup()` and `loop()` behavior must be verified on the physical
   Olimex Rev-D1 board under hybrid startup.
4. P4 revision selection, PSRAM, console, flash, and reset behavior must be
   tested before importing the VDP source.
5. If hybrid qualification fails, Arduino-only is the next fallback. Pure
   ESP-IDF remains the last option because it creates the greatest upstream
   divergence.
