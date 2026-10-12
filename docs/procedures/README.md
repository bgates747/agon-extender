# Operation protocols and procedure applicability

Use the [current handbook](../README.md) for routine operation. This directory
also retains revisioned qualification recipes: their passing status applies to
specified candidates and runs, not the current installation. A historical
procedure does not authorize a flash, reset, wiring change or new qualification.

## Required operation dispatch

Before acting, the agent reads the controlling document for the requested type
of work. For a composite operation, read all applicable rows. The Author's latest
instruction controls scope; this index does not grant hardware authorization.
Historical scripts and task recipes cannot override these protocols.

| ID | Requested operation | Controlling document |
|---|---|---|
| OP-01 | Stage, start, collect or restore a test | [Test execution](test-execution.md), plus [active bench constraints](../qualification/bench-constraints.md) |
| OP-02 | Reset Agon, reset P4 or recover input by paired resets | [Reset protocol](../bench-reset.md), including its pre-reset startup check |
| OP-03 | Deploy or flash firmware | [Installation](../installing.md), exact selected component manifest and current machine-local bench record |
| OP-04 | Roll back one or more components | [Rollback](rollback.md), plus OP-03 and OP-02 for actual flash/reset steps |
| OP-05 | Transfer, deploy, move or delete SD files | [Mainboard SD](../mainboard-sd.md) or [P4 SD](../p4-sd.md), and [SD layout](../sd-layout.md) |
| OP-06 | Observe running hardware or retrieve test results | [Test execution](test-execution.md), especially the no-monitoring boundary |
| OP-07 | Recover MOS that cannot boot or accept installation | [MOS recovery](../mos-recovery.md); ordinary input recovery starts with OP-02 |
| OP-08 | Promote accepted work or tag a release | [Production](../../production/README.md), [versioning](../versions/README.md) and AGENTS.md's acceptance/promotion rules |
| OP-09 | Build firmware or prepare a candidate | [Building](../building.md), component-owner instructions and active task contract |

## Execution and correction rules

1. Identify the operation, the controlling protocol, affected components, current
   bench/application/startup state, and the requested stopping point before a
   mutating call. State the intended action briefly; do not burden the Author
   with the internal checklist or ask again for authorization already given.
2. Inspect the actual helper before executing it. A function named `stage`,
   `reset` or `restore` may also start a game, replace firmware, collect results
   or retry. Split/adapt such a helper when its side effects exceed this request.
3. A correction that contradicts the plan invalidates dependent queued actions.
   Stop those actions, acknowledge the mismatch and revise the plan before
   continuing. If the correction leaves the next action unclear, ask and wait;
   do not ask a question and continue its dependent work unanswered.
4. An explicit stop means no further tool calls or hardware changes. Acknowledge
   and wait. Do not perform a final diagnostic poll, cleanup, reset or rollback
   after that instruction. Record state when work is subsequently authorized.
5. Finish exactly at the requested boundary. Starting a test is not permission
   to monitor it, collect it, recover it or rerun it. A timeout does not authorize
   reset/replay. Other work may continue only within its separate authorization
   and without accessing or disturbing a run marked unmonitored.
6. Keep evidence receipts and current handoff accurate. Distinguish requested,
   staged, invoked, observed running, completed, verified and accepted. If an
   instruction prevents verification, record that limit rather than implying
   success. Resume paused work only when the Author authorizes it.

## Current maintenance procedure

| Procedure | Applicability |
|---|---|
| [Numeric upstream import](numeric-upstream-import-r01.md) | Maintained import gate for approved numeric adaptations. Check its pinned source inputs, then review the actual target closure. Host checks do not qualify hardware or every future conversion. |

## Retained qualification recipes

| Recipe | Recorded result / scope | Before reuse |
|---|---|---|
| [P4 canary r02](p4-canary-r02.md) | Rejected 400-MHz bring-up candidate | Historical failure only; do not deploy as current firmware |
| [P4 canary r03](p4-canary-r03.md) | Passed bounded 360-MHz canary; no Extender GPIO | New reviewed candidate/procedure required for the connected installed system |
| [Frame service r01](p4-frame-service-qualification-r01.md) | Rejected D008 lifecycle candidate | Retain for comparison only |
| [Frame service r02](p4-frame-service-qualification-r02.md) | Deprecated before physical execution | Its bench preparation was superseded by r03 |
| [Frame service r03](p4-frame-service-qualification-r03.md) | Passed sink-independent August candidate with r01 harness and Agon disconnected | Not a recipe for the current r03-connected console; no browser/graphics/input qualification implied |
| [Browser video r01](p4-browser-video-qualification-r01.md) | Candidate for first EVF1 startup-frame service | Predates current console, codecs and input; refresh under PORT-003 before any new use |
| [PORT-008 forward r01](port-008-forward-qualification-r01.md) | Rejected and superseded transport composition | Do not execute; current transport authority remains with PORT-008 |
| [Mainboard SD r01](mainboard-sd-qualification-r01.md) | Retained candidate procedure associated with scoped September acceptance | Predates EMOSlet placement and maintained reset support; refresh under [REMOTE-005 R05-10](../tasks/REMOTE-005.md) before new qualification; old keyboard observer still requests ordinary-application RUN |

Preserve these identities and their evidence. Do not copy old fixed payloads,
startup files, no-backup assumptions or disconnected-board preconditions into a
new deployment. Current build reconstruction limits are in [Building](../building.md);
current fixture invocation, input and SD placement requirements are in
[bench constraints](../qualification/bench-constraints.md) and
[SD layout](../sd-layout.md). Installed identities and physical state belong in
the machine-local bench record.
