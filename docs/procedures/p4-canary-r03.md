# P4 Canary Qualification — r03

Status: Candidate

## Purpose

Qualify the safe 360 MHz SETUP-001 canary on the Olimex ESP32-P4-DevKit Rev D1
after r02 proved that forcing 400 MHz on its rev 1.3 silicon is not bootable.

## Controlled inputs

- `setup-001-canary-r03`
- `olimex-p4-devkit-profile-r03`
- `p4-ota-partition-layout-r01`
- `p4-bringup-procedure-r03`
- Pinned pioarduino `55.03.311`

The candidate source and procedure must be committed before the qualification
build. Inject a unique UTC build ID and preserve the exact commit, binary hash,
size, generated SDK configuration, and workspace status.

Do not back up existing P4 flash. The prior firmware is reproducible from the
retained legacy project. This does not weaken identity checks, write
verification, evidence capture, or recovery assessment.

## Procedure and required observations

Follow r02's identity resolution, clean build, offset checks, remote hash
check, erase/write/verify, initial capture, and three-reset repetition. Require:

- ESP32-P4 revision 1.3;
- QIO at 80 MHz with 16 MiB flash;
- CPU frequency exactly 360 MHz;
- 32 MiB hexadecimal PSRAM at 200 MHz with successful memory test;
- the intended partition table and `ota_0` application at `0x20000`;
- exact source and build identities on USB Serial/JTAG;
- explicit confirmation that no Extender GPIO is configured; and
- no assertion, panic, memory-test failure, or reset loop in any capture.

Pass only if all four boots satisfy every observation.
