# ADR-0010 — Use 360 MHz on the current pre-v3 P4

## Status

Amended after failed physical qualification on 2026-08-20.

## Context

Olimex specifies the ESP32-P4NRW32 on its ESP32-P4-DevKit as a dual-core
400 MHz processor. The legacy project configured and exercised the same board
at 400 MHz. In contrast, pioarduino's generic pre-v3 ESP32-P4 board definition
uses 360 MHz, while its revision-3-or-later generic definition uses 400 MHz.

Extender's intended graphics, media, transport, and network workloads benefit
from the board's full rated processing capability, but a successful boot alone
does not establish sustained stability.

Pinned ESP-IDF 5.5.5 also warns that forcing 400 MHz on pre-v3 silicon requires
an additionally qualified chip and otherwise defaults this silicon to 360 MHz.

Qualification run `SETUP-001-2026-08-20-22-18-02Z` forced 400 MHz on the
attached rev 1.3 chip. All four captures passed flash and PSRAM initialization,
then asserted in `esp_clk_init` before the application started and entered a
reboot loop. Restoring the 360 MHz r01 canary restored stable operation.

## Decision

Configure this pre-v3 board environment explicitly for 360 MHz. Do not enable
ESP-IDF's pre-v3 400 MHz force gate for this physical board. A future silicon
revision or separately proven hardware variant may receive its own 400 MHz
profile and qualification decision.

## Qualification gate

The 360 MHz canary must report runtime CPU frequency and exercise:

- sustained computation on both high-performance cores where practical;
- flash-intensive operation;
- PSRAM allocation, access, and integrity testing; and
- representative mixed CPU, flash, and PSRAM load.

The 400 MHz setting is already rejected as non-bootable on this rev 1.3 board.
It must not be reintroduced merely because a later workload appears stable at
360 MHz.

## Rationale

1. Repeated direct evidence outweighs the nominal vendor frequency and legacy
   configuration assumption for this exact silicon revision.
2. 360 MHz follows ESP-IDF's pre-v3 safety default and boots reliably.
3. Separate profiles preserve a path to 400 MHz on later or qualified silicon
   without weakening this board's baseline.

## Consequences

1. The generated ESP-IDF configuration must select 360 MHz explicitly.
2. The custom board's PlatformIO declaration may remain a descriptive upstream
   compatibility field, but it is not accepted as proof of runtime frequency;
   generated Kconfig and boot evidence govern.
3. Performance estimates for this hardware variant must assume 360 MHz.
