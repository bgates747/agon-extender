# ADR-0004 — Identify the board as a pre-v3 ESP32-P4

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-20
- Qualification: Generated-configuration and physical-board verification required

## Context

The Olimex ESP32-P4-DevKit Rev-D1 used for development reports ESP32-P4 chip
revision v1.3. ESP-IDF separates pre-v3 P4 silicon from revision 3 and later,
and pioarduino represents that distinction with the `esp32p4_es` and
`esp32p4` chip variants.

The legacy project's board file names the generic `esp32p4` variant, but its
working SDK configuration explicitly selects the pre-v3 family and permits
full revisions 100 through 199. The explicit SDK settings are stronger
evidence than the ambiguous board-file label.

## Decision

Declare the custom board's PlatformIO `chip_variant` as `esp32p4_es`.

Retain these constraints explicitly in the project's SDK defaults:

- select the ESP32-P4 revision-less-than-v3 family;
- set the minimum full revision to 100; and
- set the maximum full revision to 199.

The qualification firmware reports the runtime chip revision and treats a
build/runtime revision mismatch as a failed canary.

## Rationale

1. The setting matches the physical v1.3 silicon rather than the board's
   unrelated Rev-D1 printed-circuit-board revision.
2. It preserves the revision range used successfully by the legacy firmware.
3. It prevents pioarduino's revision-3-or-later linker and memory assumptions
   from being selected silently for pre-v3 silicon.
4. Explicit bounds make the intended target reviewable in source and in the
   generated SDK configuration.

## Consequences

1. The custom board definition uses `esp32p4_es` even though the legacy board
   definition used `esp32p4`.
2. `sdkconfig.defaults` owns the 100–199 bounds; generated `sdkconfig` output
   must be inspected during qualification.
3. Runtime chip-revision reporting is a required canary result.
4. Supporting revision-3-or-later boards will require a separately qualified
   environment or a later decision; it must not silently broaden this target.
