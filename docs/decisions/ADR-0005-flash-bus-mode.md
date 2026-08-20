# ADR-0005 — Qualify QIO flash operation at 80 MHz

## Status

Accepted as a physical-board qualification candidate.

## Context

The Olimex ESP32-P4-DevKit provides 16 MB of SPI flash. The legacy custom board
definition deliberately specifies QIO at 80 MHz, while the generated SDK
configuration from the working legacy firmware selected DIO at 80 MHz. The
legacy result proves that DIO works but does not establish that QIO fails; the
generated DIO setting may simply reflect the SDK default.

Espressif documents QIO as the usual, higher-throughput mode for compatible P4
flash hardware. Correct operation still depends on the flash device and board
wiring, so configuration evidence alone is insufficient.

## Decision

Configure QIO at 80 MHz in the primary board environment and qualify it on the
physical board. Define DIO at 80 MHz as the fallback configuration if QIO is
unstable or unsupported.

QIO is not considered proven until the qualification gate passes.

## Rationale

1. QIO offers greater flash-read throughput than DIO and is therefore the
   appropriate performance candidate for video firmware.
2. The legacy board definition indicates that QIO was an intentional hardware
   assumption, although it was not carried into the generated SDK settings.
3. The known-working DIO configuration provides a low-risk diagnostic fallback
   without forcing the production baseline to inherit an unexplained default.
4. Physical testing resolves the conflicting configuration evidence directly.

## Qualification gate

The canary must:

1. report QIO mode, 80 MHz frequency, and 16 MB capacity at boot;
2. survive repeated power-on cold boots and software/hardware resets;
3. support repeated erase, flash, and verify cycles; and
4. pass representative flash read and integrity stress testing.

If any failure correlates with QIO, repeat the same test set using DIO at
80 MHz before attributing the fault elsewhere.

## Consequences

1. QIO appears in the primary board and SDK configuration but remains visibly
   provisional until hardware qualification is recorded.
2. A DIO comparison environment or documented override must remain easy to
   invoke during bring-up.
3. Qualification results determine whether this ADR remains accepted as-is or
   is superseded by a DIO decision.
