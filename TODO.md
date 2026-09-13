# Agon Extender TODO

This is the project's single authoritative list of unfinished work. Stable item
IDs are retained until an item is accepted, rejected, or superseded; its result
and rationale are then recorded in the current dated development log before the
item is removed.

## Current goal — Host-controlled typing

- [ ] **REMOTE-002 — Type commands through the existing Extender keyboard path**
  - Started: 2026-09-13 UTC
  - Status: Contract frozen before implementation; autonomous firmware/SD/reset
    qualification authorized. Bespoke spoken hardware cue, then await chat reply
    before the live typing demonstration. DEMO-001 is accepted and closed.
  - Details: [REMOTE-002](docs/tasks/REMOTE-002.md)

## Remaining queue — Exclusive Compatible console and EDP

PORT-017 was accepted on 2026-09-13 UTC and removed from the unfinished list.
See [the dated log](docs/development/2026-09-13.md) and
[SD operating guide](docs/mainboard-sd.md). The following order is retained;
no downstream implementation was started as part of SD delivery.

Native USB keyboard bring-up is complete: ordinary MOS commands and gameplay
work in Legacy. On 2026-09-09 the Author deferred further keyboard refinements
and selected actual ExCom operation and the retained VDP-to-EDP port as the
next priority. The first ordinary ExCom console is now accepted, including
observed Legacy return and re-entry. Build on that working UART console. Use the existing UART-only r03 path; parallel
transport stays on hold. Browser input remains deferred; browser video is the
initial Extender display. The USB schematic waits until 2026-09-10.

The previous first priority was a faithful stock video backend.
AUDIT-006 is accepted and closed with implementation assigned to PORT-003.
The original-controller R1/R2 implementation is accepted. R3 starts with
the completed P4-only deployment and qualitative repaired-Nurples review.
That prior sequence selected QUAL-003's curated finite graphics timing tranche;
deterministic Nurples and separate typing measurements are deferred.

- [ ] **QUAL-003 — Compare mainboard VDP and Extender EDP graphics**
  - Started: 2026-09-09
  - Status: EDP visual PASS retained. Curated finite graphics timing tranche reactivated after restored-backend playtest. Prepare temporary mainboard/P4 hooks, bounded EMOS reception and automated SD results. Deterministic Nurples and its input-pattern question remain deferred. Wolf3D/audio remains deferred.
  - Details: [QUAL-003](docs/tasks/QUAL-003.md)


- [ ] **PORT-003 — Implement the P4 display backend and logical frame service**
  - Started: 2026-08-22 10:14 EDT
  - Finished: --
  - Status: Queued after QUAL-003. R1 accepted and frozen. R2 accepted: 70 runtime checks, 42 stock scanline checks and P4 console/display compile/link pass; the two inherited native-scroll discrepancies remain. R3 candidate r10 deployed and startup verified; qualitative repaired-Nurples playtest reports marked improvement, with residual jerkiness and sprite-heavy slowdown. No upstream fixes; full hardware qualification remains open.
  - Details: [PORT-003](docs/tasks/PORT-003.md)

- [ ] **REMED-003 — Reproduce Fab filesystem create-new and sync failures**
  - Started: 2026-09-10
  - Finished: --
  - Status: Hardware and raw-image PASS; upstream directory backend reproduces both failures. Report and reproducible attachment ready for Author review; unsubmitted.
  - Details: [REMED-003](docs/tasks/REMED-003.md)

- [ ] **AUDIT-005 — Review stock MOS reuse and EMOS UART execution costs**
  - Started: 2026-09-10
  - Finished: --
  - Status: W9/W10 measurements frozen for follow-up: point output improves but ordinary-query stalls remain and Nurples has large ExCom hangs. Further attribution moves to AUDIT-006; stock-reuse audit closure remains open.
  - Details: [AUDIT-005](docs/tasks/AUDIT-005.md)


- [ ] **PORT-008 — Implement and qualify the compatibility transport**
  - Started: 2026-08-29 19:12 EDT
  - Finished: --
  - Status: First ExCom hardware console and Nurples gameplay accepted as a major milestone; native USB input and retained browser graphics work over UART. Entry/return/re-entry logs show no prior crash; N002 closed. Wider qualification remains open; r02 hardware/parallel work stays on hold.
  - Details: [PORT-008](docs/tasks/PORT-008.md)


## Scheduled hardware documentation

- [ ] **HW-002 — Review simplified wiring for Exclusive Compatible**
  - Started: 2026-09-07 17:36 EDT
  - Finished: --
  - Status: USB keyboard addition specified; schematic/model update deferred until 2026-09-10. Existing endpoint review remains open.
  - Details: [HW-002](docs/tasks/HW-002.md)

## Other active work

- [ ] **PORT-006 — Implement the Extender network foundation and update service**
  - Started: 2026-08-27 19:13 EDT
  - Finished: --
  - Status: Video-only service restored; supports PORT-003 RGB222 delivery. Browser input remains retired; network resilience work remains open.
  - Details: [PORT-006](docs/tasks/PORT-006.md)

## Deferred keyboard refinements

- [ ] **PORT-005 — Implement the processed-keyboard input adapter**
  - Started: 2026-09-08 (P4 controlled-key sender).
  - Finished: --
  - Status: Further keyboard refinements, including the proposed Caps Lock LED increment, deferred by Author on 2026-09-09. Preserve working USB input; repair only keyboard regressions that block the ExCom increment.
  - Details: [PORT-005](docs/tasks/PORT-005.md)

## Deferred browser input

- [ ] **REMOTE-001 — Develop browser keyboard and remote EMOS control**
  - Started: 2026-09-08
  - Finished: --
  - Status: Deferred by Author, 2026-09-09; retain implementation, measurements and unresolved defects. Resume only on explicit reprioritization.
  - Details: [REMOTE-001](docs/tasks/REMOTE-001.md)

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

- [ ] **HW-001 — Design and qualify the V1 UART and forward-parallel interface**
  - Started: 2026-08-28 13:06 EDT
  - Finished: --
  - Status: Design, wiring, and testing on hold; incomplete and full circuit untested.
  - Details: [HW-001](docs/tasks/HW-001.md)

## Porting

- [ ] **PORT-004 — Implement the P4 PCM scheduler and network audio sink**
  - Started: --
  - Finished: --
  - Status: Deferred by the Author until audio implementation is requested; includes audio-command framing defect and Wolf3D retest.
  - Details: [PORT-004](docs/tasks/PORT-004.md)

- [ ] **PORT-007 — Implement the P4 DevKit microSD storage service**
  - Started: --
  - Finished: --
  - Status: Required v1 capability, scheduled after the first beta; EMOS must be able to read the P4 card. Future MicroPython is a storage consumer, not a prerequisite.
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

## Future software capabilities

- [ ] **PORT-016 — Add MicroPython scripting to EDP**
  - Started: --
  - Finished: --
  - Status: Long-term capability requested by Author, 2026-09-10. Implementation deferred; inclusion in v1 remains undecided. Not a dependency of the current performance investigation.
  - Details: [PORT-016](docs/tasks/PORT-016.md)
