# ADR-0010 — Qualify the vendor-rated 400 MHz CPU frequency

## Status

Accepted as a physical-board qualification candidate.

## Context

Olimex specifies the ESP32-P4NRW32 on its ESP32-P4-DevKit as a dual-core
400 MHz processor. The legacy project configured and exercised the same board
at 400 MHz. In contrast, pioarduino's generic pre-v3 ESP32-P4 board definition
uses 360 MHz, while its revision-3-or-later generic definition uses 400 MHz.

Extender's intended graphics, media, transport, and network workloads benefit
from the board's full rated processing capability, but a successful boot alone
does not establish sustained stability.

## Decision

Configure the primary board environment for 400 MHz and qualify it under
sustained physical-board load. Retain 360 MHz as a controlled diagnostic
fallback, not as the production default.

## Qualification gate

The canary must report the runtime CPU frequency and exercise:

- sustained computation on both high-performance cores where practical;
- flash-intensive operation;
- PSRAM allocation, access, and integrity testing; and
- representative mixed CPU, flash, and PSRAM load.

Any instability observed at 400 MHz must be reproduced with the same test at
360 MHz before it is classified as frequency-related or attributed elsewhere.

## Rationale

1. 400 MHz is the board vendor's published operating frequency rather than an
   experimental overclock.
2. The legacy project provides prior evidence of operation at that frequency on
   the physical board.
3. Multimedia and transport workloads can use the additional performance.
4. A defined 360 MHz comparison prevents frequency assumptions from obscuring
   diagnosis during bring-up.

## Consequences

1. The custom board definition uses `f_cpu = 400000000L`.
2. Production qualification requires stress evidence, not merely a boot log.
3. A frequency-correlated failure may supersede this decision with a lower
   production setting without changing the broader firmware architecture.
