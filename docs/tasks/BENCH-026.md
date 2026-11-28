# BENCH-026 — Audit every Olimex serial file transfer

Routine tests should spend their time running the fixture. The audit will show
which operations move whole files, why each needs the bytes, and where metadata
or an existing receipt can replace a transfer. It covers both the slow SD path
and the intermittent mainboard USB programmer path.

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

- BENCH-026-001 [ ] Freeze the exact live and published references and enumerate
  entry points across maintained procedures and current commissioning packets.

- BENCH-026-002 [ ] Trace and justify the SD, native UART and USB serial
  payloads. Verify representative sizes and costs with saved records.

- BENCH-026-003 [ ] Cross-check every route against procedure, implementation,
  and evidence. Evaluate compact verification for USB and expose duplicates,
  hidden polling or downloads, and paths that cannot yet be justified.

- BENCH-026-004 [ ] Publish the coverage and transfer ledger, list decisions
  and recommended order, and identify gaps without changing the bench.
