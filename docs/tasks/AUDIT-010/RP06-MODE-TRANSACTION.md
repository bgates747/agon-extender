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

`A10-RP06-S02` [ ] Candidate implementation and source qualification complete.

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

`A10-RP06-I01` [ ] Give `StockP4Service` separate active and prepared runtime
slots over its one persistent snapshot pool. A prepared slot owns its candidate
controller reference, periodic clock and drawing/output tasks, but cannot
execute or publish until activation.

`A10-RP06-I02` [ ] Preparation creates and checks every semaphore, timer and
worker needed by the candidate. Every injected preparation failure destroys
only candidate resources in reverse order and leaves the active slot admitted.

`A10-RP06-I03` [ ] Commit performs no allocation or task/timer creation. It
quiesces and joins the active slot, activates the already-running candidate
clock and already-created workers, then permits the caller to replace the
global controller/Canvas aliases. The old controller remains owned until both
old native readers have joined.

`A10-RP06-I04` [ ] `changeResolution` prepares a distinct controller at every
depth, checks modeline parsing, viewport allocation, exact geometry, Canvas
construction and service preparation before commit. It updates colour depth,
geometry, scaling and refresh data only from the committed candidate.

`A10-RP06-I05` [ ] Failed requests preserve the current controller, Canvas,
workers, clock, geometry, colour depth and `modeStatus`. Successful
`changeMode` remains the sole publisher of the new logical mode/status. A
failed mode-1 fallback retains the previously committed logical identity.

## Validation contract

`A10-RP06-V01` [ ] Add a host transaction seam which injects failure at
controller construction, viewport preparation, Canvas preparation, timer
creation, drawing-worker creation and output-worker creation. At every point,
assert that the old runtime and published mode remain unchanged and all
candidate resources are released.

`A10-RP06-V02` [ ] Prove successful commit ordering: candidate resources exist
before old-reader retirement; old readers join before old destruction; the
candidate is activated before publication; no fallible acquisition occurs
after old retirement.

`A10-RP06-V03` [ ] Regress early and late transitions, same-depth transitions,
depth changes, double buffering, official fallback to the old mode and mode 1,
truthful `modeStatus`, RP05 allocation injection, retained mode lifecycle,
screen capture and native selected-profile compilation.

`A10-RP06-V04` [ ] Run the complete clean-commit offline qualification suite.
Record exact commit, counts, duration and artifact identity without claiming
hardware behavior.

`A10-RP06-V05` [x] The bounded automated portion of `A10-VP02` is registered as
the mandatory `a10-rp06-mode-transaction` installed-P4 case. It performs
mode8→20→8 first without a browser consumer and then with one retained
browser-video WebSocket, checking committed status and decoded frame geometry
at every edge before final startup recovery. The case depends on the integrated
P4 smoke; the later destructive EMOS case also depends on this case so a failed
display prerequisite blocks raw-media work. The loaded-asset Nurples transition
remains manual. After source review, execute the bounded `A10-VP02`
mode8↔20 hardware procedure with browser absent/present and assets
absent/loaded. Flashing and physical execution require the Author's explicit
authorization; the automated suite and manual Nurples case remain distinct.

## Acceptance boundary

`A10-RP06-A01` [ ] Present the candidate, exact source evidence, hardware
procedure and remaining limits to the Author. Stop before hardware deployment
unless it is explicitly authorized, and stop again for explicit RP06
acceptance before RP07.
