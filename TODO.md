# Agon Extender TODO

This is the project's single authoritative list of unfinished work. Stable item
IDs are retained until an item is accepted, rejected, or superseded; its result
and rationale are then recorded in the current dated development log before the
item is removed.

## Current priority — direct USB keyboard input

The order below applies to the keyboard slice in each detail file, not to
completion of the whole task. Documentation was accepted for freeze on
2026-09-08. The resident EMOS receiver, API proof and bounded recovery emulator
checkpoints are accepted and frozen. Controlled P4 keyboard sending and EMOS
API effects pass on hardware. Physical browser typing, Enter and Backspace
now work. Paired timing measurements identify a reproducible keyboard lease
defect and P4 video send-budget closures. The Author reviewed those findings
and selected direct USB keyboard input before browser repairs on 2026-09-09,
to restore a keyboard for the ordinary EMOS CLI on mainboard VGA.
Broader physical/session qualification remains open. The selected Agon/P4 path uses
only r03 UART1; module loading, runtime relocation and moslet-space residency
are not prerequisites.

- [ ] **PORT-015 — Bring up a directly connected USB keyboard**
  - Started: 2026-09-09 (connector verification, then native P4 HID input).
  - Finished: --
  - Status: Native USB acquisition passes; ordinary EMOS CLI integration is drafted with host/emulator checks passing, awaiting Author review and hardware proof. Power particulars remain open.
  - Details: [PORT-015](docs/tasks/PORT-015.md)

- [ ] **REMOTE-001 — Develop browser keyboard and remote EMOS control**
  - Started: 2026-09-08 (physical typing/editing works; reviewed findings retained; repairs follow PORT-015).
  - Finished: --
  - Details: [REMOTE-001](docs/tasks/REMOTE-001.md)

- [ ] **PORT-006 — Implement the Extender network foundation and update service**
  - Started: 2026-08-27 19:13 EDT
  - Finished: --
  - Details: [PORT-006](docs/tasks/PORT-006.md)

- [ ] **PORT-005 — Implement the processed-keyboard input adapter**
  - Started: 2026-09-08 (controlled P4 sender).
  - Finished: --
  - Status: Controlled sender and browser typing work on hardware; PORT-015 reuses the processed-input path for USB; wider input parity remains open.
  - Details: [PORT-005](docs/tasks/PORT-005.md)

- [ ] **PORT-008 — Implement and qualify the compatibility transport**
  - Started: 2026-08-29 19:12 EDT
  - Finished: --
  - Status: Controlled P4-to-EMOS keyboard UART proof passes; browser/session and wider integration remain; r02/parallel work stays on hold.
  - Details: [PORT-008](docs/tasks/PORT-008.md)

## Other active work

- [ ] **PORT-003 — Implement the P4 display backend and logical frame service**
  - Started: 2026-08-22 10:14 EDT
  - Finished: --
  - Details: [PORT-003](docs/tasks/PORT-003.md)

## Qualification infrastructure

- [ ] **QUAL-001 — Establish the durable compatibility qualification matrix**
  - Started: 2026-08-22 22:59 EDT
  - Finished: --
  - Details: [QUAL-001](docs/tasks/QUAL-001.md)

## Audit remediation

- [ ] **REMED-001 — Reconcile the repository with the four-mode operating architecture**
  - Started: 2026-08-23 17:02 EDT
  - Finished: --
  - Details: [REMED-001](docs/tasks/REMED-001.md)

- [ ] **REMED-002 — Remediate open-task implementation and evidence-integrity findings**
  - Started: 2026-09-01 12:52 EDT
  - Finished: --
  - Details: [REMED-002](docs/tasks/REMED-002.md)

## Setup

- [ ] **SETUP-005 — Resolve remaining operating-mode integration decisions**
  - Started: 2026-08-21 00:49 EDT
  - Finished: --
  - Status: Immediate keyboard decisions accepted; broader integration remains open.
  - Details: [SETUP-005](docs/tasks/SETUP-005.md)

- [ ] **SETUP-006 — Establish the Light 2 Extender wiring target**
  - Started: 2026-08-24 19:09 EDT
  - Finished: --
  - Status: On hold; physical wiring and as-built record incomplete.
  - Details: [SETUP-006](docs/tasks/SETUP-006.md)

## Hardware design

- [ ] **HW-002 — Review simplified wiring for Exclusive Compatible**
  - Started: 2026-09-07 17:36 EDT
  - Finished: --
  - Status: R03 schematic checkpoint and eight-line pinwalk accepted; endpoint review remains open.
  - Details: [HW-002](docs/tasks/HW-002.md)

- [ ] **HW-001 — Design and qualify the V1 UART and forward-parallel interface**
  - Started: 2026-08-28 13:06 EDT
  - Finished: --
  - Status: Design, wiring, and testing on hold; incomplete and full circuit untested.
  - Details: [HW-001](docs/tasks/HW-001.md)

## Porting

- [ ] **PORT-004 — Implement the P4 PCM scheduler and network audio sink**
  - Started: --
  - Finished: --
  - Details: [PORT-004](docs/tasks/PORT-004.md)

- [ ] **PORT-007 — Implement the P4 DevKit microSD storage service**
  - Started: --
  - Finished: --
  - Details: [PORT-007](docs/tasks/PORT-007.md)

## System qualification

- [ ] **QUAL-002 — Qualify assembled-system electrical absence, power, and reset behavior**
  - Started: 2026-09-04 18:32 EDT
  - Finished: --
  - Status: Present-hardware qualification on hold; full circuit untested.
  - Details: [QUAL-002](docs/tasks/QUAL-002.md)

## Upstream research

- [ ] **UPSTREAM-001 — A/B test vdp-gl lifecycle corrections for a possible upstream PR**
  - Started: --
  - Finished: --
  - Details: [UPSTREAM-001](docs/tasks/UPSTREAM-001.md)

## Operating-mode lifecycle

- [ ] **MODE-001 — Develop state-preserving operating-mode transitions**
  - Started: --
  - Finished: --
  - Details: [MODE-001](docs/tasks/MODE-001.md)

- [ ] **MODE-002 — Evaluate automatic mode-request retry protection**
  - Started: --
  - Finished: --
  - Details: [MODE-002](docs/tasks/MODE-002.md)

## Failure diagnostics

- [ ] **DIAG-001 — Implement recoverable failure reporting and crash records**
  - Started: --
  - Finished: --
  - Details: [DIAG-001](docs/tasks/DIAG-001.md)

## Interprocessor links

- [ ] **LINK-001 — Research a direct onboard-VDP/EDP high-speed link**
  - Started: --
  - Finished: --
  - Details: [LINK-001](docs/tasks/LINK-001.md)
