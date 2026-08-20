# ADR-0007 — Use two large OTA application slots

## Status

Accepted. Exact offsets remain subject to toolchain validation.

## Context

Extender has 16 MB of SPI flash. It must preserve the stock VDP's ability to
write firmware to the next OTA partition while adding safe network updates and
room for substantially larger P4 firmware. The eventual image may include the
stock-compatible VDP, Arduino and ESP-IDF facilities, Ethernet services, media
streaming, SD-card access, and hardware-expanded functions.

The stock ESP32 VDP image is currently about 1.03 MiB, but that does not provide
a meaningful upper bound for the P4 product. The legacy P4 project used a
single-application partition table, which cannot safely update a running image
and does not satisfy the stock updater's two-partition behavior.

A permanent factory application would consume flash and create a third firmware
variant that must be maintained and tested throughout the product's life.

## Decision

Divide application capacity into two equal 7 MiB OTA slots, `ota_0` and `ota_1`.
Do not create a permanent factory application partition.

Allocate the required leading data area for NVS configuration, OTA selection
metadata, and crash diagnostics. Reserve the approximately 1.9 MiB remainder as
a data partition without yet selecting a filesystem or application-level use.

Freeze exact offsets and the precise diagnostic/reserved split only after the
pinned hybrid toolchain generates a valid table and confirms its bootloader,
alignment, and metadata requirements.

## Update and recovery model

The running application writes a candidate image to the inactive OTA slot,
verifies it, selects it for the next boot, and restarts. The candidate marks
itself valid only after a meaningful post-boot health check. A failure before
validation causes bootloader rollback to the previous image.

The previous OTA image is the normal recovery firmware. If neither application
is usable, the immutable ESP32-P4 ROM download mode provides recovery over USB.
A later SD-card recovery mechanism may supplement these paths but is not part of
this decision.

## Health-validation requirements

Post-boot validation establishes at least the compatible runtime chip revision,
successful flash and PSRAM initialization, the expected tested PSRAM capacity,
essential firmware initialization, and enough VDP operation to distinguish a
working image from one that merely reached the Arduino entry point. The exact
timeout and VDP health criterion remain implementation decisions.

## Rationale

1. Seven-mebibyte slots leave substantial growth room for multimedia and
   network firmware while retaining safe replacement of the running image.
2. Equal slots simplify alternating updates and preserve the stock updater's
   next-partition model.
3. Rollback reuses the previous production image instead of requiring a third,
   easily neglected recovery firmware product.
4. USB ROM download mode remains available even when application flash contents
   are unusable.
5. Reserving the remaining capacity avoids prematurely selecting an internal
   filesystem when large persistent assets belong on the board's SD card.

## Consequences

1. Every production image must fit comfortably within 7 MiB, including any
   signing or image metadata required later.
2. The updater must integrate ESP-IDF's image-validity and rollback lifecycle;
   selecting the next partition alone is insufficient.
3. Partition-table changes after deployment require exceptional care and an
   explicit migration decision.
4. The reserved data partition cannot be consumed casually merely because it
   appears unused.
5. Images larger than 7 MiB would require reducing reserved space, redesigning
   recovery, or changing hardware.
