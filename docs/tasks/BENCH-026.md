# BENCH-026 — Eliminate redundant Olimex serial file transfers

Routine tests should spend their time running the fixture. The audit will show
which operations move whole files, why each needs the bytes, and where metadata
or an existing receipt can replace a transfer. It covers both the slow SD path
and the intermittent mainboard USB programmer path.

**Status:** audit and host implementation complete. The [findings](BENCH-026/FINDINGS.md)
preserve the original transfer costs. The replacement proofs await a physical
Olimex run before adoption in the shared checkout.

## Scope and review boundary

- Audit the commissioned Olimex guide, authoring and recovery procedures, the
  sparse checkout, linked maintained tools, and the scripts those entry points
  actually call. Include active job-local launchers and adapters discoverable
  from current bench packets. Record file-by-file coverage, including helpers
  that move no file, and identify older routes that still appear in instructions
  or can be selected. Retained historical logs and old scripts supply evidence
  where they explain a current route or documented fallback.
- Trace both directions over Pi5-to-mainboard and Pi5-to-P4 USB serial, the
  P4-to-eZ80 UART carrier, and the Agon eZ80-to-mainboard-VDP UART used by
  FLASH. Trace HTTP and other legs where they explain where a UART payload
  goes. Distinguish file bytes from keyboard commands, serial observations,
  reset control, and protocol metadata. Include firmware writes, programmer
  reads and backups, SD staging and collection, installed-tool checks, and
  verification, recovery and restore paths.
- For every file transfer, name the caller, source, destination, physical
  carrier, byte count or bound, frequency, expected cost, why it exists, and
  what fails if it is removed. Decide whether to keep, reuse, reduce to
  metadata, or require a documented diagnostic or qualification reason. Mark
  uncertain costs and undocumented custom callers explicitly.
- Preserve the Author's current rule. A standard SD image gets a one-time
  byte comparison upon initial deployment with a published receipt. Routine
  jobs reuse it. A test-image SD transfer uses FLASH's on-card CRC and may
  send metadata back. Assess after-write verification independently so the
  audit can identify a small reply that retains the actual write proof.
- Use source, package dependencies and retained evidence only. The audit
  changes no bench procedure, hardware, file on the card, runner, firmware,
  or custody. Return findings and proposed changes for Smith to review.

## Work

- BENCH-026-001 [x] Freeze the exact live and published references and enumerate
  entry points across maintained procedures and current commissioning packets.

- BENCH-026-002 [x] Trace and justify the SD, native UART and USB serial
  payloads. Verify representative sizes and costs with saved records.

- BENCH-026-003 [x] Cross-check every route against procedure, implementation,
  and evidence. Evaluate compact verification for USB and expose duplicates,
  hidden polling or downloads, and paths that cannot yet be justified.

- BENCH-026-004 [x] Publish the coverage and transfer ledger, list decisions
  and recommended order, and identify gaps without changing the bench.

## Results

The audit covered all 45 paths in the live commissioned sparse checkout,
the published observer correction, linked maintained and fallback procedures,
and discoverable current or recently executed job-local launchers.
The [coverage inventory](BENCH-026/COVERAGE.md) records exact revisions,
the sweep window and the limits on unauditable private or archived variants.

- [USB serial](BENCH-026/USB-SERIAL.md) covers both programmers, console/reset
  traffic, incident reads and available flash digest proof.
- [SD UART](BENCH-026/SD-UART.md) covers input/output files, repeated reads
  of resident tools, exceptions and measured carrier costs.
- [Onboard Agon UART](BENCH-026/ONBOARD-UART.md) covers FLASH's actual app
  stream, local verification and measured comparisons.

The findings recommend replacing the routine mainboard USB application dump
with an ESP32-computed digest, preserving image range, actual boot selection
and fresh MOS evidence. This saves the bulk transfer and retains the ROM SYNC
dependency. A stock-compatible in-service proof would be a separate change.
The initial audit ended at findings. See the authorized implementation below.
The task contract was published at
`9313e48c39cc057ed6825a34c7268ef61e8b2a76`.

## Authorized implementation — November 27, 2026

Smith directed removal of unnecessary whole-file transfers from the standard
runner and bench procedures, across every UART path and both USB programming
links. Keep small programmer transactions that establish identity, layout,
selection or an independently verified write. Keep transfers needed to put new
bytes on a device, retrieve original results, commission a standard SD copy
once, or preserve otherwise unavailable evidence with a stated purpose.

- BENCH-026-005 [x] Replace ordinary full mainboard USB application readback with
  an ESP32-computed digest of the exact selected application range. Keep small
  layout and selector reads, exact host source pin, and fresh MOS after restart.
  Preserve existing admitted receipts and verification-only recovery. Keep full
  byte reads for explicit diagnostics. Never fall back to a dump automatically.
- BENCH-026-006 [x] Reuse commissioned SD tool identities and existing standard
  image receipts. Use metadata during normal phases, retain the small startup
  check, and keep FLASH's on-card CRC for candidate transfer verification.
- BENCH-026-007 [x] Remove redundant EMOS and P4 full-image verification transfers
  where actual written bytes can be checked locally with equivalent scope.
  Keep necessary writes, bounded metadata and required result collection.
- BENCH-026-008 [x] Align current procedures, commissioning and host-only tests.
  Record the proof retained in each route, review compatibility with existing
  evidence, and verify that success, mismatch and failure paths avoid bulk
  read fallback. Hardware qualification and live checkout changes require a
  coordinated operator window and a separate test disposition.


### Implemented and checked offline

The implementation contract was published at
`29d6fc761731369ed1fe8cc331a8bc4f08eb9870`. The
[bench procedure](../operations/olimex-bench/README.md),
[authoring guide](../operations/olimex-bench/AUTHORING.md) and
[SD firmware and tool receipts](../../production/olimex-sd-firmware.json)
describe the resulting duties and evidence.

| Phase | Bytes or proof now used | Bulk transfer removed |
| --- | --- | --- |
| Mainboard FLASH verification | The USB programmer keeps the board/slot checks, 12,288 B of layout and selector data and the ESP32's 16-byte digest for the exact installed range. | Mainboard application-sized read after each FLASH. |
| SD staging and collection | The Pi checks resident tool metadata against published identity receipts, reads bounded startup bytes at the relevant boundaries, and uploads only new fixture and firmware inputs. FLASH compares the candidate input CRC on the Agon. | Repeated SD listener and updater binary downloads. Existing verified standards can serve as candidate or restore without upload. |
| Extender P4 app verification | esptool's ESP32-P4-computed write digest for the padded extent, retained with the writer log and fresh MOS. An admitted retry checks the entry application by digest. | Separate full P4-app read after writing or to establish a pinned retry entry. |
| EMOS ROM verification | File size and FLASH's input CRC before confirmation. FLASH checks the actual written 128 KiB locally, then the Pi proves fresh MOS. | Generated SAVE/EXEC upload and full installed-ROM download. |

A matched VDPL-054 install and restore avoid 2,235,680 application bytes over
the mainboard USB link. An ordinary one-arm run avoids another 135,756 B of
repeated resident tool downloads over SD UART, excluding any avoided standard
image upload. These are payload counts from retained evidence. The revised
elapsed time has yet to be measured.

Host checks included the standard Olimex and bench test suites, exact
VDPL-054 baseline and candidate manifest preflight, and the retained v0.1.4-alpha
promotion manifest preflight. The compact mainboard proof also passed against
the original saved app1 candidate and app0 restore bytes, table and selector,
using their archived bytes to supply the simulated device response. The
current P4 writer parser accepted the retained INTEG-019 P4 write logs.
Existing raw and padded receipts remain readable. Frozen job adapters that
explicitly consume a raw dump keep their original revision. Future adapters
consume the compact receipt via the maintained verifier.

The programmer's initial ROM sync remains required. Full original reports,
first-deployment SD comparison and explicitly scoped diagnostics, backups
and recovery reads remain available. No durable production EMOS ROM copy on
the Agon SD card is currently commissioned. EMOS jobs still stage their
required ROM inputs. No new firmware build is needed for these runner changes.

- BENCH-026-009 [ ] Under a fresh lease, qualify the compact proofs using
  approved jobs for each affected component. Capture actual ESP32 replies,
  the P4 writer log, the FLASH MOS transcript and verified handback. Measure
  staging and verification separately. Refresh the shared checkout between
  operators after qualification. No bench session was used for the offline
  work.

### Mainboard qualification — November 27, 2026

Runner `38c1c37c973dc758a6f864bb095f2cc749a42a09` passed a complete
mainboard-only cycle with the VDPL-054 scanline fixture in a fresh namespace.
Agon Flash installed 1,118,336 bytes on app1 and restored production
VDPlet v0.1.4-alpha, 1,117,392 bytes, on app0. Both USB verifications matched
the ESP32's digest using the retained table and selector metadata. Neither
downloaded the application. The fixture passed and returned its 63-byte
report over UART. Handback proved fresh MOS, idle transfers and closed
serial handles. Local evidence is under
`agents/bench-026/compact-vdp-r01/evidence/`. The scheduler and the waiting
operator received the exact qualified mainboard runner and procedure before
check-in. The shared checkout stays pinned while P4 and EMOS write
qualification remains pending.
