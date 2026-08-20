# P4 Canary Qualification — r02

Status: Rejected by run `SETUP-001-2026-08-20-22-18-02Z`

## Purpose

Qualify SETUP-001 canary r02 on the Olimex ESP32-P4-DevKit Rev D1 without any
Extender GPIO connection or configuration.

## Controlled inputs

- `setup-001-canary-r02`
- `olimex-p4-devkit-profile-r02`
- `p4-ota-partition-layout-r01`
- `p4-bringup-procedure-r02`
- Pinned pioarduino `55.03.311`

The candidate source, this procedure, and all configuration must be committed,
and the candidate tree must be clean before the qualification build.

## Deliberate no-backup rule

Do not read or back up the P4's existing flash. Its pre-test firmware is a known
legacy-project artifact and can be rebuilt or restored from that separate
repository. This exception removes the r01 backup step; it does not weaken
device-identity checks, write verification, evidence capture, or recovery
assessment.

## Procedure

1. Resolve the board through the ignored bench record's stable USB identity;
   reject zero, multiple, or mismatched devices.
2. Record the candidate commit and confirm `git status --porcelain` is empty.
3. Allocate the UTC build ID, build with
   `AGON_EXTENDER_QUALIFICATION_BUILD=1`, and inject the full build ID.
4. Record the binary size and SHA-256 in a build manifest. Verify the combined
   factory image's bootloader, partition, and application offsets.
5. Allocate the run ID immediately before the physical run.
6. Stage the exact factory image and verify its remote SHA-256.
7. Erase flash, write the combined image at `0x0`, and run esptool verification.
8. Reset through USB Serial/JTAG and capture at least 12 seconds of boot output.
9. Verify the required observations below.
10. Perform three additional USB resets with captured output. Every boot must
    reach the canary report without panic, reset loop, memory-test failure, or
    identity/configuration drift.
11. Record outcome and evidence. Do not modify the candidate during the run.

## Required observations

- ESP32-P4 revision 1.3 within the configured 1.0–1.99 range.
- Second-stage QIO enabled at 80 MHz with 16 MiB flash.
- CPU frequency exactly 400 MHz.
- 32 MiB hexadecimal PSRAM at 200 MHz and passing startup memory test.
- Intended partition table and application load from `ota_0` at `0x20000`.
- Exact source identity and build ID through USB Serial/JTAG diagnostics.
- Explicit confirmation that no Extender GPIO is configured.

## Outcome

Pass only if the initial boot and all three reset repetitions satisfy every
required observation. Preserve failed evidence. Restore legacy firmware only
if needed to return the board to a usable state; restoration is recovery, not
part of a passing run.

The run failed reproducibly: all four captures reached the PSRAM memory-test
success message and then repeatedly asserted in `esp_clk_init` at `clk.c:142`.
The application canary was never reached. The prior 360 MHz r01 canary was
restored and independently verified to leave the board usable.
