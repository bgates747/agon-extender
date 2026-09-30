# AUDIT-010 RP06 — P4 mode prepare, commit and rollback

## Executive summary

`A10-RP06-S01` [x] RP05 is accepted and RP06 is authorized. The selected P4
runtime must prepare a complete replacement controller, viewport, Canvas,
clock and both workers while the current mode remains live. A preparation
failure leaves the current runtime and published status unchanged. Commit has
no remaining fallible resource acquisition; it quiesces the old workers,
activates the prepared runtime, publishes the new facade state and only then
retires the old objects. Exact-candidate hardware work remains a later explicit
gate.

`A10-RP06-S02` [x] Candidate implementation and exact-commit source
qualification complete at Extender `fd0c1d36`. Hardware qualification remains
unexecuted and requires explicit authorization.

`A10-RP06-S03` [ ] Exact-candidate hardware qualification and Author acceptance
complete. RP07 remains unauthorized until this item is accepted.

## Authority and scope

`A10-RP06-C01` [x] Official Agon screen-mode documentation states that an
unavailable requested mode falls back first to the current mode and then to
mode 1. The selected reference is `agon-docs` `docs/vdp/Screen-Modes.md`; the
official implementation baseline remains `agon-vdp` tag `v2.16.0`, commit
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`. The reference VDP checkout's tracked
source remains clean; an unrelated untracked macOS metadata file is not source
evidence.

`A10-RP06-C02` [x] `VDUStreamProcessor::vdu_mode` remains the owner of requested,
old-mode and mode-1 fallback. The project-owned selected P4 integration owns
the native runtime transaction. RP06 may correct the fallback's premature
`videoMode = 1` assignment because a failed mode-1 attempt must not publish a
mode which never committed; it must not replace official modelines or move
fallback policy into the P4 service.

`A10-RP06-C03` [x] RP06 changes only the stock-shaped selected display family.
It does not copy the repair into the contained nonrelease display family and
does not change palette, renderer, browser allocation policy, LCD behavior or
mode tables. RP05's checked lower allocations remain the prerequisite.

## Implementation contract

`A10-RP06-I01` [x] The implemented ownership is two separate per-mode
`StockP4Service` instances over one persistent external snapshot pool, rather
than two slots inside one service object. This keeps browser leases valid while
making active/prepared ownership explicit. The prepared service owns its
candidate controller reference, periodic clock and drawing/output tasks, but
its atomic admission gate prevents execution and publication until activation.
The deviation avoids a more complex two-slot state machine without changing
the frozen prepare/commit boundary.

`A10-RP06-I02` [x] Preparation creates and checks every semaphore, timer and
worker needed by the candidate. Every injected preparation failure destroys
only candidate resources in reverse order and leaves the active slot admitted.

`A10-RP06-I03` [x] Commit performs no allocation or task/timer creation. It
quiesces and joins the active slot, starts accounting on the already-created
candidate periodic timer, admits the already-created workers, then permits the caller to replace the
global controller/Canvas aliases. The old controller remains owned until both
old native readers have joined.

`A10-RP06-I04` [x] `changeResolution` prepares a distinct controller at every
depth, checks modeline parsing, viewport allocation, exact geometry, Canvas
construction and service preparation before commit. It updates colour depth,
geometry, scaling and refresh data only from the committed candidate.

`A10-RP06-I05` [x] Failed requests preserve the current controller, Canvas,
workers, clock, geometry, colour depth and `modeStatus`. Successful
`changeMode` remains the sole publisher of the new logical mode/status. A
failed mode-1 fallback retains the previously committed logical identity.

## Validation contract

`A10-RP06-V01` [x] The maintained sanitizer-backed host transaction seam
injects failure at controller construction, viewport preparation, Canvas preparation, timer
creation, drawing-worker creation and output-worker creation. At every point,
assert that the old runtime and published mode remain unchanged and all
candidate resources are released.

`A10-RP06-V02` [x] The same host seam proves successful commit ordering:
candidate resources exist before old-reader retirement; old readers join before old destruction; the
candidate is activated before publication; no fallible acquisition occurs
after old retirement.

`A10-RP06-V03` [ ] Regress early and late transitions, same-depth transitions,
depth changes, double buffering, official fallback to the old mode and mode 1,
truthful `modeStatus`, RP05 allocation injection, retained mode lifecycle,
screen capture and native selected-profile compilation.

`A10-RP06-V04` [x] The complete clean-commit offline qualification suite passes
all 57 cases at exact Extender commit
`fd0c1d368574be57bd91bd136c6230d003c15de4` in 149.169474 monotonic seconds,
with zero test failure, infrastructure error, timeout or blocked case and an
unchanged source closure. The retained local summary under
`agents/qualification-rp06-fd0c1d36/summary.json` has SHA-256
`f18c43b55de9ce3831e5a3b799c5e4fce7735d052e5de8f386155cf2cab1dd54`.
The fresh 1,707,696-byte unversioned `p4-console` factory image has SHA-256
`5ba7921d7157d0084c289860d659d135094aaffc4068551044783deb4617a1fc`.
These are source/build evidence only and do not claim installed behavior.

`A10-RP06-V05` [x] The bounded automated portion of `A10-VP02` is registered as
the mandatory `a10-rp06-mode-transaction` installed-P4 case. It performs
mode8→20→8 first without a browser consumer and then with one retained
browser-video WebSocket, checking committed status and decoded frame geometry
at every edge before final startup recovery. The case depends on the integrated
P4 smoke; the later destructive EMOS case also depends on this case so a failed
display prerequisite blocks raw-media work. Flashing and physical execution
require the Author's explicit authorization. After that automated no-asset
case, the loaded-asset Nurples transition remains a distinct manual case.

## Acceptance boundary

`A10-RP06-A01` [ ] Present the candidate, exact source evidence, hardware
procedure and remaining limits to the Author. Stop before hardware deployment
unless it is explicitly authorized, and stop again for explicit RP06
acceptance before RP07.
