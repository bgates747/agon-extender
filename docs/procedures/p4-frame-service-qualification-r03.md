# P4 Frame-Service Qualification — r03

Status: Qualified

Identity: `p4-frame-service-qualification-r03`

Qualified by `PORT-003-2026-08-22-23-58-56Z`.

## Purpose

Qualify `port-003-frame-service-canary-r02` on the Olimex ESP32-P4-DevKit Rev
D1 at 360 MHz using the D009 faithful-port lifecycle. This revision supersedes
r02 solely to control the live breadboard harness, attached logic-analyzer
fixture, disconnected-Agon boundary, and pre-flash probe checks. It does not
change the firmware or logical frame-service acceptance contract.

This is a sink-independent test. It does not qualify a physical display sink,
official VDP facade, VDU path, network transport, palette/Copper compositor,
audio, input, storage, or analyzer timing.

## Controlled inputs

- `port-003-frame-service-canary-r02`
- `olimex-p4-devkit-profile-r03`
- `p4-ota-partition-layout-r01`
- `light2-harness-r01`
- `la03-p4-probe-fixture-r01`
- `p4-frame-service-qualification-r03`
- pioarduino `55.03.311`, Arduino `3.3.11`, and ESP-IDF `5.5.5`
- the exact clean candidate commit recorded in the run manifest

The candidate source and all controlled identities must be committed and
pushed before the qualification build. Read ignored `HARDWARE.local.md` and
resolve the bench host and stable P4 identity exactly as specified there. Stop
on any identity or physical-state mismatch. Do not place machine-local or
unique-device details in tracked evidence. No backup of the installed P4
firmware is required; it is reproducible from the retained legacy project.

## Required initial bench state

- The P4 is powered on the breadboard with `light2-harness-r01` attached.
- The USB logic analyzer is powered and attached as
  `la03-p4-probe-fixture-r01`.
- The Agon is physically disconnected from the harness.
- Analyzer attachment is controlled loading and observation infrastructure;
  this run does not claim analyzer timing qualification unless separately
  specified and captured.

## Build and identity

1. Confirm a clean worktree and record the full pushed commit.
2. Remove only ignored generated `vdp/sdkconfig.p4-frame-service`, if present.
3. Assign `port-003-frame-service-canary-r02-bYYYY-MM-DD-HH-MM-SSZ` as the UTC
   build ID.
4. Clean and build environment `p4-frame-service` with that
   `AGON_EXTENDER_BUILD_ID`. Require committed source identity
   `port-003-frame-service-canary-r02` and status `candidate`; reject any
   mismatch.
5. Run the committed Phase C closure validator. Require nine selected
   application translation units, every required symbol, and no excluded
   application source or symbol family.
6. Record hashes and sizes for the factory and application images, bootloader,
   partition table, SDK configuration, ELF, and map.
7. Verify exact source/build identities in the ELF and factory image. Reject
   `UNVERSIONED-DO-NOT-DEPLOY` and every r01 identity.

## Physical preflight and deployment

Complete every read-only check before erasing or writing flash:

1. Verify the disposable Pi host, stable board USB identity, ESP32-P4 chip,
   serial endpoint, and flash tool.
2. Compare the attached breadboard wiring with `light2-harness-r01`; confirm
   and record that the Agon remains disconnected.
3. Compare every attached analyzer lead with `la03-p4-probe-fixture-r01`.
   Physically verify that green D0 is firmly seated on P4 GPIO32, Rev D1 EXT2
   pin 9. Stop for any loose, displaced, or contradictory probe.
4. Confirm the analyzer is visible to the bench host without changing its
   configuration. No analyzer capture is required by this procedure.
5. Stage only the exact committed factory image and verify its remote SHA-256.
6. Confirm offsets: bootloader `0x2000`, partition table `0x8000`, OTA data
   `0xf000`, and application `0x20000`.
7. Erase flash, write the factory image at `0x0`, and independently verify the
   written bytes. Stop on any command or hash failure.
8. Capture the complete initial boot over stable USB Serial/JTAG without
   changing source, configuration, binaries, harness, or probes during the
   run.

## Required observations

Require all of the following:

- exact r02 source/build identities and artifact status `candidate`;
- ESP32-P4 revision 1.3, QIO 80 MHz, 16 MiB flash, and CPU at 360 MHz;
- no assertion, panic, Guru Meditation, watchdog reset, or reset loop;
- ten-second cadence records 550–650 elapsed ticks and at least 500
  independently polled notices, with maximum polling interval below 100 ms;
- the five-tick burst yields at least five distinct serviced edges;
- the compatibility counter crosses modulo-2^32 rollover and ends below 1,000;
- the unconsumed mailbox reports nonzero bounded drops without stalling;
- all 20 stop/start cycles succeed with unchanged upstream draining;
- final free 8-bit heap is at most 4,096 bytes below initial free heap; and
- `PORT003_PHASE_C_RESULT pass=1` is emitted.

Preserve the raw boot capture and derive the machine-readable observations
without editing that raw evidence.

## Run record and outcome

Assign `PORT-003-YYYY-MM-DD-HH-MM-SSZ` at run start. Record exact UTC times,
commit, build ID, hashes, tools, all controlled identities, generic bench
aliases, observed harness/probe state, disconnected-Agon confirmation,
deployment checks, observations, and evidence hashes under
`tests/runs/<RUN-ID>/`.

Pass only when every required observation succeeds without a deviation that
weakens the claim. Preserve failed, partial, aborted, and invalid runs. Assign
a new build/run identity after any candidate change.
