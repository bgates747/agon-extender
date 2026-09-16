# Agon Extender TODO

This is the project's single authoritative list of unfinished work. Stable item
IDs are retained until an item is accepted, rejected, or superseded; its result
and rationale are then recorded in the current dated development log before the
item is removed.

## Current Author-directed research

- [ ] **RESEARCH-001 — P4 rendering/network pacing literature search**
  - Status: C1 source investigation complete; report in RESEARCH-001/C1/README.md. No drop-in fix or new benchmark. Await Author review before C2; RLE deferred until C1–C5 dispositions.
  - Details: [RESEARCH-001](docs/tasks/RESEARCH-001.md)
  - Boundary: Research only; hardware voice at review, no firmware changes.

## Current Author-directed review — Overnight debrief

QUAL-003 owns the [performance debrief and review contract](docs/tasks/QUAL-003/DEBRIEF-PLAN.md).
P00 and P01a/b are complete; [P02 SW isolation controls](docs/tasks/QUAL-003/debrief/P02/README.md)
are collected for review. Prebuilt transmission retains a timing tail, but a
contradictory composition-only repeat prevents network-only attribution.
Recommend resolving boot/order/pool-placement and scheduling variance before
an affinity change. No performance fix or parity pass claimed. Golem remains
on hold. Verified r43/startup restored, hardware voice delivered, paused for review.

## Current Author-directed sequence — Audits before game benchmarks

Complete the numeric-conversion audit and unsupported-command audit before
benchmarking games. RX07 enumerates only; RX08 retains mandatory Author review
before RX09 corrections, RX10 deterministic stock comparisons and RX11 reusable
gates. PORT-003 UC01–UC07 covers the wider command-consumption audit; its audio
slice now has Author visual acceptance. Then QUAL-003 owns matched current Rally
and a bespoke deterministic Nurples fixture on mainboard VDP and P4 EDP.
See [the sequencing contract](docs/tasks/QUAL-003/rally-excom/PLAN.md#audit-first-game-benchmark-sequence).
Earlier priority headings below preserve historical context and do not override
this sequence. Golem and actual P4 audio synthesis remain excluded.

## First priority — Stock UART alignment

- [ ] **PORT-008 — Stock-compatible UART performance and correctness**
  - Status: E07P bulk parity qualified in ordinary and bench EMOS: each passes384 exact controls, three captures and strict symmetric return timing. Exact original bench firmware/startup restored; CLI/SD/input verified and hardware voice acknowledged. Graphics and short-command latency are not included in that parity claim. No experimental push.
  - Details: [PORT-008](docs/tasks/PORT-008.md), [bounded plan](docs/tasks/PORT-008/uart-alignment/PLAN.md)
  - Companion: [E07P owner scheduling](docs/tasks/PORT-008/uart-alignment/E07P-owner.md) is complete; minimal stock-loop alignment retained. [Current findings](docs/tasks/PORT-008/uart-alignment/FINDINGS.md) link qualification/restoration evidence.
  - Next: Author review of completed E08 correctness and E09 rendering evidence, then explicit EMOS INTEG-014 E10 authorization. No automatic follow-up or experimental push.

## Previous goal — Resident Rally telemetry and driving

- [ ] **BENCH-001 — Initial experiments**
  - Started: 2026-09-13 UTC
  - Status: Local work frozen in commits by explicit Author instruction. No new
    experiments until the next graphics-suite contract is agreed. Resident telemetry/driving and bounded physical practice are
    machine-complete; the hour is exhausted. Final native v2 integration passes
    with the explicit TEST-002 UART1 model correction; original failures remain
    preserved. Human review is open. Unattended full-game continuation is
    sequenced in AgonArcade RALLY-22, then video speed and faithful VDP coverage.
    No overnight progress alerts; human review/commit approval remain separate.
  - Details: [BENCH-001](docs/tasks/BENCH-001.md)

## Host-controlled typing — Implementation review

- [ ] **REMOTE-002 — Type commands through the existing Extender keyboard path**
  - Started: 2026-09-13 UTC
  - Status: Contract committed; host/headless and physical input/CLI/SD checks pass.
    First attended typing received positive feedback, but exposed a stale-clock
    lease bug. r15 clock/pacing fixes and extended physical cursor/CLI/SD retest
    pass. Author returned and is convinced typing works; requested practical
    CLI experiments under BENCH-001 instead of another typing demonstration.
    Uncommitted; remaining review disposition and commit approval not recorded.
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
  - Status: Overnight debrief ready for review. Complete E09 framebuffer-only evidence shows faster P4 execution scopes; streamed Nurples averages about60 refresh completions/s but fails repeated spacing parity. Current Rally hardware FPS unmeasured. P00/P01 complete; approved P02 SW controls reveal transmission-associated tails and contradictory discard-repeat variance. Review P02 before further experiments; Golem on hold, no experimental push.
  - Details: [QUAL-003](docs/tasks/QUAL-003.md)
  - Current priority: [Rally Legacy/ExCom diagnosis](docs/tasks/QUAL-003/rally-excom/PLAN.md), Review stop: RX06 repair eliminates all 14 road-section differences; 80/80 samples now match stock. [Findings](docs/tasks/QUAL-003/rally-excom/FINDINGS.md). RX07 enumeration complete: [inventory](docs/tasks/QUAL-003/rally-excom/rx07/README.md). RX08 approved N02–N06; [RX09/RX10 guards and stock comparisons](docs/tasks/QUAL-003/rally-excom/rx09/PLAN.md) pass machine checks; human review pending. RX11 reusable import protection complete; [results](docs/tasks/QUAL-003/rally-excom/rx11/README.md). Golem excluded.


- [ ] **PORT-003 — Implement the P4 display backend and logical frame service**
  - Started: 2026-08-22 10:14 EDT
  - Finished: --
  - Status: Paused for Author catch-up, prior P4 image restored and Legacy keyboard/SD recovery verified. Large-surface probe separates snapshot cost (640×480 mean16.660ms) but rejects incomplete socket-send accounting at observer teardown; L04 remains open in video-throughput/LARGE-SURFACE.md. Earlier video increment remains scoped machine evidence. No optimization/publication claim; QUAL-003 now owns the separately authorized framebuffer-first rerun.
  - Details: [PORT-003](docs/tasks/PORT-003.md)
  - Active separate tranche: [UC01–UC07 safe no-op command consumption](docs/tasks/PORT-003.md#unimplemented-command-consumption-tranche), UC01 inventory complete ([findings](docs/tasks/PORT-003/command-consumption/README.md)); UC02/UC03 contracts next, then deterministic sentinels and hardware review. Audio-first repair passes hardware checks; [results and review](docs/tasks/PORT-004/audio-framing/results/README.md).

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


**PORT-008 retained compatibility context (active priority above)**
  - Started: 2026-08-29 19:12 EDT
  - Finished: --
  - Status: First ExCom hardware console and Nurples gameplay accepted; native USB input and browser graphics work over UART. Selected font, bitmap/affine, context, palette/depth, staged sprite and Copper cases preserve stock native pixels on physical P4, with Legacy/SD recovery. Inherited reflected-edge and active sprite-kind conversion failures remain explicit; guarded conversion passes. Copper reconnect snapshots retain the preceding state before fresh output. Local review pending. N002 remains closed. Wider command qualification is open; r02 hardware/parallel work stays on hold.
  - Details: [PORT-008](docs/tasks/PORT-008.md)


## TRS-80 integration

- [ ] **TRS-80-001 — Design TRS-OS integration and reusable network storage for Extender**
  - Started: 2026-09-13 (ecosystem survey and task definition).
  - Status: Initial survey and Linux reference acquisition complete (14 repos, two archives); architecture and protocol selection open. Future owned TRS-80 project should prefer selected vendoring. Coordinate with current EMOS/Extender work before implementation; existing console/graphics queue remains in place.
  - Details: [TRS-80-001](docs/tasks/TRS-80-001.md)

## Scheduled hardware documentation

- [ ] **HW-003 — Assess alternate ESP32-P4 development board**
  - Started: 2026-09-13
  - Finished: --
  - Status: Desk assessment ready; promising full Waveshare kit, requires pin remapping and specimen qualification. Electrotux in Chile has decided to purchase a test unit; exact variant/revision and adaptation scope remain pending.
  - Details: [HW-003](docs/tasks/HW-003.md)

- [ ] **HW-002 — Review simplified wiring for Exclusive Compatible**
  - Started: 2026-09-07 17:36 EDT
  - Finished: --
  - Status: USB keyboard addition specified; schematic/model update deferred until 2026-09-10. Existing endpoint review remains open.
  - Details: [HW-002](docs/tasks/HW-002.md)

## Required audits — currently unscheduled

- [ ] **AUDIT-007 — Exhaustive Agon FabGL port completeness audit**
  - Status: Author-required, unscheduled pending QUAL-003 P00 immediate timing
    research. Required regardless of whether that research produces a fix;
    the dependency controls sequencing, not scope or commitment. Not started.
  - Details: [AUDIT-007](docs/tasks/AUDIT-007.md)

## Other active work

- [ ] **NET-001 — Replace the active video viewer on a new connection**
  - Implemented on r20; six hardware connections/five takeovers passed. Hardware voice sent; awaiting Author browser acceptance.
  - Details: [NET-001](docs/tasks/NET-001.md); preserve one-client bounded delivery and RX06 repair.


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
  - Status: Audio synthesis/output deferred. Interim command framing/no-op work reprioritized under PORT-003 UC01–UC07; retains audio reply and Wolf3D regression obligations. Audio-first repair passes hardware checks; [results and review](docs/tasks/PORT-004/audio-framing/results/README.md).
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

Current Author goal: [Nurples hardware parity with active web streaming](docs/tasks/QUAL-003/nurples-parity/PLAN.md). This takes priority over unrelated audit continuations; existing gates remain recorded.
