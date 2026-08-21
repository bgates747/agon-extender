# ADR-0006 — Represent internal SRAM and external PSRAM separately

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-20
- Qualification: Physical-board qualification required

## Context

The ESP32-P4 has 768 KB of physical internal SRAM, not all of which is
available to the application linker and general-purpose allocation. The Olimex
board also provides 32 MB of external PSRAM. Internal SRAM and PSRAM have
different latency, allocation, execution, DMA, interrupt, and peripheral-access
properties and therefore are not interchangeable resources.

The legacy custom board definition sets PlatformIO's `maximum_ram_size` to
33,554,432 bytes, conflating the external PSRAM capacity with ordinary internal
RAM. pioarduino's pre-v3 P4 evaluation-board definition instead uses a
512,000-byte internal-RAM budget and declares PSRAM independently.

The legacy firmware successfully configured the PSRAM in hexadecimal mode at
200 MHz.

## Decision

Set the custom board's PlatformIO `maximum_ram_size` to 512,000 bytes. Treat
this as a conservative link-time internal-memory budget, not a statement of the
chip's total physical SRAM.

Declare PSRAM separately with `BOARD_HAS_PSRAM` and SDK configuration for:

- PSRAM enabled and initialized during boot;
- hexadecimal mode;
- 200 MHz operation;
- allocation through the capability-aware allocator and `malloc` integration;
  and
- boot-time memory testing.

The canary must report and verify the full 32 MB PSRAM capacity.

## Allocation policy

Use PSRAM deliberately for large framebuffers, media buffers, caches, and other
bulk data. Prefer internal SRAM for stacks, interrupt-accessed data,
latency-sensitive state, and buffers whose DMA or peripheral requirements have
not yet been verified as PSRAM-capable.

## Rationale

1. The model accurately distinguishes the processor's scarce low-latency memory
   from its large external working store.
2. The 512,000-byte budget follows a maintained pre-v3 P4 board baseline rather
   than inventing a new linker estimate.
3. The PSRAM mode and frequency preserve settings already exercised by the
   legacy firmware.
4. Explicit allocation makes performance and peripheral compatibility easier
   to reason about and diagnose.

## Consequences

1. PlatformIO's memory summary will not count all 32 MB of PSRAM as ordinary
   linkable RAM.
2. Large allocations must be designed and reviewed with their memory capability
   requirements in mind.
3. Bring-up fails if PSRAM initialization, capacity detection, or its memory
   test fails.
4. The internal-RAM budget may be refined later from linker evidence without
   changing the architectural distinction between internal SRAM and PSRAM.
