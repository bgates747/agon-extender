# PORT-007 — Implement the P4 DevKit microSD storage service

## State

- Status: Not started — registered from SETUP-004 Work 1.h
- Started: --
- Finished: --

## Intent

Implement the project-owned storage service for the Olimex ESP32-P4-DevKit's
onboard microSD card. This is a required v1 capability deferred until after the
first beta. It does not require or imply a file browser.

Begin from Olimex's board-specific ESP-IDF SDMMC demo and Espressif's maintained
P4 SDMMC implementation rather than adapting vdp-gl's dormant FileBrowser or
classic-ESP32 SDSPI/SPIFFS backend.

## Authority and inputs

- [SETUP-004 Work 1.h](SETUP-004.md#work-1h-execution-record) and its generated
  storage inventory.
- [ADR-0013](../decisions/ADR-0013-vdp-survey-integration-boundaries.md),
  especially decisions 30–31.
- [Current architecture](../architecture.md).
- [PORT-002 source-selection work](PORT-002.md).
- [Olimex ESP32-P4-DevKit SDMMC demo](https://github.com/OLIMEX/ESP32-P4-DevKit/tree/main/SOFTWARE/Demo_Examples/sdmmc).
- [Espressif ESP-IDF SDMMC example](https://github.com/espressif/esp-idf/tree/master/examples/storage/sd_card/sdmmc).
- Olimex schematic and tracked target hardware profile for the exact board
  revision selected during implementation.

## Required outcomes

1. Pin or vendor the exact tagged or immutable Olimex/Espressif reference
   versions used as the implementation baseline and record them in project
   version metadata.
2. Verify the selected DevKit revision's SDMMC pins, bus width, pull-ups, power
   source, internal-LDO channel, card-detect/write-protect availability, and
   conflicts with all other selected P4 functions.
3. Implement a project-owned mount and lifecycle service using current P4
   SDMMC, FATFS, and VFS APIs. Keep physical-card ownership separate from
   installed-application, media, network-file, and future EDU-facing services.
4. Define explicit error, retry, mount/unmount, card-removal/reinsertion,
   startup, shutdown, and recovery behavior. Do not inherit global mutable
   mount state from vdp-gl.
5. Define namespaces and safe concurrent access for firmware assets, installed
   applications, media, network services, and later MOS-facing RPC consumers.
6. Define write durability, flushing, power-loss behavior, capacity reporting,
   supported card/filesystem limits, and performance targets.
7. Make destructive formatting an explicit authorized operation. Never format
   automatically merely because mounting failed.
8. Leave internal-flash filesystem support unselected until a concrete feature
   requires it; do not couple SPIFFS adoption to microSD implementation.
9. Add deterministic host tests where practical and qualified target tests for
   supported cards, throughput, concurrency, removal, reinsertion, malformed
   filesystems, full media, interrupted writes, and recovery.

## Dependencies and gates

- This task is a v1 requirement but is deliberately scheduled after the first
  beta.
- PORT-002 must represent both omitted vdp-gl storage regions as vendored but
  excluded without removing unrelated retained `fabutils.cpp` services.
- QUAL-001 must retain microSD qualification as a secondary product capability,
  separate from stock VDP compatibility evidence.
- Read `HARDWARE.local.md` before any target build, deployment, power, serial,
  or physical qualification operation.
- Freeze the exact board, firmware, wiring/profile, fixture, procedure, and test
  identities under `docs/versions/README.md` before qualified hardware runs.
- Review the mounted-card format and destructive-operation policy with the
  Author before implementing formatting or recovery that can alter media.
