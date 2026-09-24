# Architecture decision records

Architecture decision records (ADRs) preserve accepted project architecture
and its rationale. Open questions and actionable work remain in the
authoritative `TODO.md` and corresponding files under `docs/tasks/`.

## Decision index

For implemented behavior begin with the [current architecture boundary](../architecture.md#implementation-boundary)
and [handbook](../README.md). This index reports decision metadata, not whether
an implementation or particular board has passed qualification. Later amendments
and linked current contracts govern over superseded details; historical run or
attention instructions are not continuing execution authorization.

| Decision | Recorded authority / completeness |
|---|---|
| [ADR-0001 — Place Extender code under `vdp/video/extender/`](ADR-0001-vdp-source-layout.md) | Accepted / Complete |
| [ADR-0002 — Use PlatformIO with Arduino and ESP-IDF together](ADR-0002-hybrid-firmware-framework.md) | Accepted / Complete |
| [ADR-0003 — Pin pioarduino release 55.03.311](ADR-0003-pioarduino-platform-baseline.md) | Accepted / Complete |
| [ADR-0004 — Identify the board as a pre-v3 ESP32-P4](ADR-0004-p4-silicon-identity.md) | Accepted / Complete |
| [ADR-0005 — Qualify QIO flash operation at 80 MHz](ADR-0005-flash-bus-mode.md) | Accepted / Complete |
| [ADR-0006 — Represent internal SRAM and external PSRAM separately](ADR-0006-board-memory-model.md) | Accepted / Complete |
| [ADR-0007 — Use two large OTA application slots](ADR-0007-flash-partition-strategy.md) | Accepted / Complete |
| [ADR-0008 — Add CMake only when the hybrid build proves it necessary](ADR-0008-minimal-cmake-boundary.md) | Accepted / Complete |
| [ADR-0009 — Provide a transparent PlatformIO wrapper](ADR-0009-platformio-wrapper.md) | Accepted / Complete |
| [ADR-0010 — Use 360 MHz on the current pre-v3 P4](ADR-0010-cpu-frequency.md) | Accepted / Complete |
| [ADR-0011 — Maintain upstream VDP fidelity and separate project-owned structure](ADR-0011-upstream-vdp-integration-and-project-structure.md) | Accepted / Complete |
| [ADR-0012 — Vendor exact release dependencies for the VDP firmware](ADR-0012-vendored-release-dependencies.md) | Accepted / Complete |
| [ADR-0013 — VDP survey findings and integration boundaries](ADR-0013-vdp-survey-integration-boundaries.md) | Accepted / Complete |
| [ADR-0014 — EDU operating modes, state ownership, and service architecture](ADR-0014-edu-operating-modes-and-service-architecture.md) | Accepted / Partial |
| [ADR-0015 — P4 display backend and logical frame service](ADR-0015-p4-display-backend-and-frame-service.md) | Accepted / Complete |
| [ADR-0016 — V1 transport electrical core](ADR-0016-v1-transport-electrical-core.md) | Accepted / Partial |
| [ADR-0017 — Generalized EDP callbacks](ADR-0017-generalized-edp-callbacks.md) | Accepted / Partial |
| [ADR-0018 — RGB222 browser video and bounded frame pacing](ADR-0018-rgb222-browser-video.md) | Accepted / Complete |
| [ADR-0019 — Host keyboard input and independent bench reset](ADR-0019-host-keyboard-and-bench-reset-control.md) | Accepted / Complete |
| [ADR-0020 — 30 fps web output at512×384](ADR-0020-web-output-30fps.md) | Accepted / Complete |
| [ADR-0021 — RLE2 as the browser-video default](ADR-0021-rle2-browser-default.md) | Accepted / Complete |
| [ADR-0022 — Explicit browser keyboard capture](ADR-0022-browser-keyboard-capture.md) | Accepted / Complete |
| [SD separation of support files, evidence and transactions](ADR-2026-09-21-sd-layout.md) | Accepted / Complete |

When changing an ADR's identity, title, status or completeness, update this index.
Do not infer a new decision or change qualification status merely to make the
index look complete.

## Required metadata

Every ADR begins with these fields immediately below its title:

```markdown
- Status: Accepted
- Completeness: Complete
- Date: YYYY-MM-DD
```

Add `Related task` when a task owns the decision. An ADR with partial
completeness must also name its authoritative tracker:

```markdown
- Open-decision tracker: SETUP-NNN
```

## Status

- **Proposed:** presented for review but not authoritative.
- **Accepted:** authoritative current architecture.
- **Rejected:** considered and explicitly declined.
- **Superseded:** no longer authoritative; the ADR identifies its replacement.

Status describes the authority of decisions already recorded. Qualification,
implementation, and testing state do not change an accepted decision's status;
record those separately in its task and evidence.

## Completeness

- **Partial:** accepted decisions exist, but known architectural decisions
  remain unresolved inside the ADR's declared scope.
- **Complete:** no known architectural decisions remain unresolved inside the
  declared scope.

Complete does not mean immutable, implemented, tested, or eternally final. New
evidence may amend or supersede any ADR. Partial ADRs contain only accepted
decisions and link to a task that owns the unresolved questions; they do not
duplicate open questions or actionable checklists.

When the final tracked question is resolved, incorporate the accepted result,
change completeness to `Complete`, and update the task and development log.

## Design audit records

Files named `AUDIT-YYYY-MM-DD-NNN-<subject>.md` record a bounded review of
current architecture, tasks, implementation, generated data, and evidence.
They identify contradictions, omissions, stale assumptions, and affected
authorities without making new architecture authoritative merely by finding a
problem.

Every audit begins with `Status`, `Date`, `Trigger`, `Scope`, and `Owning task`.
Findings use stable IDs and record severity, observed state, required
disposition, and affected artifacts. Status is `In progress` while coverage is
being gathered and `Complete` when the declared scope has been reviewed and
every finding has an owner or explicit deferral.

Accepted architectural corrections are promoted into the applicable ADR and
normative architecture document. Actionable work remains in the owning tracked
task and `TODO.md`; generated outputs are regenerated from their corrected
authorities. An audit is evidence and a correction map, never a competing
architecture specification or task list.
