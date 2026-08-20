# ADR-0003 — Pin pioarduino release 55.03.311

## Status

Accepted, subject to build and physical-board qualification.

## Context

The ESP32-P4 VDP port requires a PlatformIO platform that supports the accepted
hybrid Arduino and ESP-IDF framework model. The platform selection must also be
reproducible and must accommodate the silicon and peripheral configuration of
the Olimex ESP32-P4-DevKit Rev-D1.

The legacy Extender successfully exercised the board with a pinned pioarduino
development commit and ESP-IDF 5.5.5. That is useful hardware evidence, but its
Arduino framework dependency was not qualified and could resolve from a moving
upstream source. The pioarduino `stable` release URL is likewise a moving alias.

pioarduino release `55.03.311` supplies Arduino-ESP32 3.3.11 with ESP-IDF 5.5.5
and includes an ESP32-P4 revision fix.

## Decision

Pin the initial VDP PlatformIO environment to pioarduino release `55.03.311`.
Use an immutable, version-specific release reference rather than the `stable`
alias or a development branch.

Treat the legacy pioarduino commit and its configuration as a known hardware
reference and fallback, not as the production build baseline.

## Rationale

1. The numbered release gives developers and automated builds a reproducible
   platform identity.
2. Arduino-ESP32 3.3.11 supports the Arduino APIs needed by the upstream VDP
   source while ESP-IDF 5.5.5 supplies native P4 configuration and facilities.
3. ESP-IDF 5.5.5 matches the version already exercised on the physical board by
   the legacy project, reducing one source of bring-up uncertainty.
4. The included P4 revision fix is preferable to starting from an older
   development snapshot and carrying an unexplained platform delta.

## Consequences

1. The version-specific release reference becomes part of `vdp/platformio.ini`.
2. Platform upgrades require an explicit decision and renewed build and
   physical-board qualification; they do not happen through a moving alias.
3. The release must pass the minimal hybrid canary before official VDP source is
   imported.
4. Failure of the canary triggers comparison against the legacy pinned setup
   before changing firmware architecture or upstream-compatible source.
