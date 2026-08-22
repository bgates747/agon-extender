# P4 Frame-Service Qualification — r01

Status: Candidate

Identity: `p4-frame-service-qualification-r01`

## Purpose

Qualify `port-003-frame-service-canary-r01` on the Olimex ESP32-P4-DevKit Rev
D1 at the accepted 360 MHz configuration. This procedure measures the
sink-independent logical frame service only. It neither installs nor qualifies
a physical display sink, official VDP facade, VDU path, network transport,
palette/Copper compositor, audio, input, or storage behavior.

## Controlled inputs

- `port-003-frame-service-canary-r01`
- `olimex-p4-devkit-profile-r03`
- `p4-ota-partition-layout-r01`
- `p4-frame-service-qualification-r01`
- pioarduino `55.03.311`, Arduino `3.3.11`, and ESP-IDF `5.5.5`
- the exact clean candidate commit recorded in the run manifest

The candidate source, identity, procedure, board profile, and partition layout
must be committed and pushed before the qualification build. Read the ignored
`HARDWARE.local.md`, resolve the stable USB device exactly as specified there,
and stop on any identity mismatch. Do not place machine-local hostnames,
addresses, keys, USB identifiers, or specimen mappings in tracked evidence.

No backup of the installed P4 firmware is required; its prior state is
reproducible from the retained legacy project.

## Build and identity

1. Confirm the candidate worktree is clean and record its full commit.
2. Remove only the ignored generated `vdp/sdkconfig.p4-frame-service`, if
   present, so a stale Kconfig cannot survive PlatformIO's clean target.
3. Assign a unique UTC build ID of the form
   `port-003-frame-service-canary-r01-bYYYY-MM-DD-HH-MM-SSZ`.
4. Clean and build environment `p4-frame-service` with
   the assigned `AGON_EXTENDER_BUILD_ID` in the environment. The build must
   obtain `AGON_EXTENDER_SOURCE_IDENTITY=port-003-frame-service-canary-r01`
   and status `candidate` from committed
   `vdp/pio/p4-frame-service-identity.json`; an optional matching environment
   value may be supplied as an additional guard, but a mismatch must fail.
5. Run the committed Phase C closure validator. Require nine selected
   application translation units, all required symbols, and zero excluded
   application source/symbol families.
6. Record hashes and sizes for the factory image, application image,
   bootloader, partition table, generated SDK configuration, ELF, and map.
7. Verify both exact identities are embedded in the ELF and factory image.
   Reject the `UNVERSIONED-DO-NOT-DEPLOY` marker.

## Deployment

1. Verify the disposable Pi host, stable board USB identity, expected ESP32-P4
   chip, serial endpoint, and flash tool before mutation.
2. Stage only the exact committed factory image and verify its remote SHA-256
   against the local build manifest.
3. Confirm the combined image offsets are bootloader `0x2000`, partition table
   `0x8000`, OTA data `0xf000`, and application `0x20000`.
4. Erase flash, write the factory image at `0x0`, and independently verify the
   written bytes. Stop on any command or hash failure.
5. Capture the complete initial boot through the stable USB Serial/JTAG path.
   Do not change source, configuration, or binaries during the run.

## Required observations

Require all of the following from the captured boot and canary result:

- exact source and build identities plus artifact status `candidate`;
- ESP32-P4 revision 1.3;
- QIO at 80 MHz with 16 MiB flash;
- CPU frequency exactly 360 MHz;
- no assertion, panic, Guru Meditation, watchdog reset, or reset loop;
- normal ten-second cadence records 550–650 elapsed ticks and at least 500
  independently polled notices, with maximum observed polling interval below
  100 ms;
- the injected five-tick burst is accepted and records at least four
  coalesced ticks;
- the compatibility frame counter crosses modulo-2^32 rollover and finishes
  below 1,000;
- the deliberately unconsumed mailbox records nonzero bounded drops without
  stalling logical progress;
- all 20 stop/start cycles succeed; and
- final free 8-bit heap is no more than 4,096 bytes below its initial value.

The firmware must emit `PORT003_PHASE_C_RESULT pass=1`. Preserve the raw boot
capture; derive a compact machine-readable observation record without editing
the raw evidence.

## Run record and outcome

Assign the run ID at start as `PORT-003-YYYY-MM-DD-HH-MM-SSZ`. Record exact UTC
times, clean commit, build ID, hashes, tool versions, controlled artifact
identities, generic bench aliases, deployment checks, observations, and all
evidence hashes under `tests/runs/<RUN-ID>/`.

Pass only if every required observation succeeds with no procedural deviation
that weakens the claim. Preserve failed, partial, aborted, or invalid runs and
assign a new build/run identity after any candidate change.
