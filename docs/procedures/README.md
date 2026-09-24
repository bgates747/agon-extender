# Procedure applicability

Use the [current handbook](../README.md) for routine operation. This directory
also retains revisioned qualification recipes: their passing status applies to
specified candidates and runs, not the current installation. A historical
procedure does not authorize a flash, reset, wiring change or new qualification.

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
| [Mainboard SD r01](mainboard-sd-qualification-r01.md) | Retained candidate procedure associated with scoped September acceptance | Predates EMOSlet placement and maintained reset support; refresh under REMOTE-005 before new qualification |

Preserve these identities and their evidence. Do not copy old fixed payloads,
startup files, no-backup assumptions or disconnected-board preconditions into a
new deployment. Current build reconstruction limits are in [Building](../building.md);
current fixture invocation, input and SD placement requirements are in
[bench constraints](../qualification/bench-constraints.md) and
[SD layout](../sd-layout.md). Installed identities and physical state belong in
the machine-local bench record.
