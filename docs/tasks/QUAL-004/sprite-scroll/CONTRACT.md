# Sprite motion and scrolling checkpoints

## Executive summary

Author approved deterministic moving-sprite/scroll qualification. Use mode20,
two explicit software sprites and four accumulated-history checkpoints. Compare
physical mainboard scanout with P4 snapshots; no game changes, performance work,
Copper, hardware-sprite stress or renderer fixes. New fixture identity
sprite-scroll-probe-r01 and registry r95 use standing identity approval.

**QUAL-004-SS01** [x] Freeze generator/inputs/oracle/contract before deployment.
Preserve actual mainboard flash/startup; verify player and deployed input hashes.
Reuse existing all-depth diagnostic; P4/EMOS remain unchanged.

**QUAL-004-SS02** [ ] Select mode20 only through startup. Capture INITIAL,
OVERLAP, EDGES and HIDDEN after replay of identical accumulated updates from
fresh starts. Two independent mainboard captures and two distinct matching P4
generations per checkpoint; compare every 512×384 pixel without masks/tolerance.
Updates cover transparent software sprites, movement/frame changes, overlap,
viewport scrolling and drawing an eight-row bitmap through a one-row viewport.
Mark unexpected reset, incomplete acquisition or repeat instability per case.
Recover verified readiness and continue independent cases under the
[capture failure protocol](../../../qualification/capture-failure-protocol.md);
after the suite, rerun failed endpoints without capture instrumentation.
No renderer/fixture repair to force agreement.

**QUAL-004-SS03** [x] Independently compare the entire final hidden-sprite image
with a simple striped-background/scroll/refill oracle. This catches both stale
sprite pixels and drawing outside the one-row viewport. Require visible sprite
content earlier so a disabled-sprite fixture cannot pass merely by agreeing.
Retain mismatches with scope limits; no assertion of tear-free live animation.

**QUAL-004-SS04** [x] Hide sprites and drain before mode teardown, restore exact
startup and overwritten mainboard sectors, independently verify, close readers,
release keyboard/SD/video observers and confirm MOS prompt. Publish evidence
and acquisition duration, not FPS. Existing crashes and Copper remain deferred.
No emulator/voice cue or push requested.

## Research and interpretation

Official docs at f9806bd3cbff6ed5d1c08bef1d51fed11764b86b:
`docs/vdp/Bitmaps-API.md` specifies RGBA8888 alpha as binary transparency,
software-sprite update command23,27,15, frame selection, hide and signed pixel
positions. `VDU-Commands.md` specifies VDU24 graphics viewport and
VDU23,7 extent2/direction3/movement1 for one-pixel upward viewport scroll.
Mode20 is 512×384×64. Stock v2.16.0 reference remains read-only. Existing capture
samples composed visible scanout after each static completion checkpoint.

Every checkpoint file replays the full preceding history independently, with
completion fences after scroll, clipped plotting and sprite refresh. These
fences make the acquired image stable and explicitly exclude command-throughput
or unfenced resource-lifetime conclusions. Bitmap resources are not mutated or
freed while their sprite frames remain referenced. The hidden-background oracle
models only rectangles and row shifts, not the stock renderer or sprite order.

## Execution disposition

Stopped at first mainboard replay before capture; SS02/SS03 remain unqualified.
SS04 restoration/evidence closeout completed. See [results](RESULTS.md).

## Author amendment — 2026-09-20

The original stopped run remains historical evidence. Future execution follows
the linked protocol, including separate mainboard stock and capture-free EDP
controls for their respective failed cases. This amendment changes orchestration,
not fixture bytes, rendering implementation or prior qualification status.

## Authorized mainboard-only continuation

Author requests OVERLAP, EDGES and HIDDEN, with Extender deferred. Replay each
from fresh mainboard mode20 startup; acquire two independent captures when the
first succeeds. Mark capture failure, recover and continue. After all three,
replay failed cases without the capture token on verified official stock VDP,
observing30seconds and checking Escape/CLI responsiveness. Stock controls cannot
supply missing visual evidence without Author observation. Preserve the incoming
load-only review startup and restore stock app; do not run any P4 scene. Record
all results, including image/oracle checks where available. No diagnostic repair.

### Mainboard continuation disposition

OVERLAP/EDGES/HIDDEN completed twice each; repeat captures match. HIDDEN has zero
oracle mismatches. See [results](mainboard-followup/RESULTS.md). Mainboard portion
complete within those limits; full paired SS02/SS03 remain incomplete pending
separately authorized Extender work. Earlier INITIAL capture failure retained.

## Authorized Extender continuation

Author now requests all four Extender checkpoints. Existing P4/EMOS firmware is
unchanged. Select mode20 through autoexec, replay each frozen scene, acquire at
least two distinct stable frame generations and compare OVERLAP/EDGES/HIDDEN
against retained repeatable mainboard captures. INITIAL has only a stock visual
control, so do not claim an exact paired comparison there. HIDDEN also requires
its full independent oracle. Mark failures and continue after verified recovery;
any failed case requires a separately identified matching capture-free EDP
control, not simply disconnection of the viewer. Restore incoming load-only
mainboard startup and normal input/service state. No upstream/diagnostic repair.

### Extender continuation disposition

All four P4 checkpoints passed stable capture; OVERLAP/EDGES/HIDDEN exact paired
parity and HIDDEN full independent oracle passed. [Evidence](extender-followup/RESULTS.md).
SS02 remains incomplete only for INITIAL's missing mainboard capture; its stock
visual/exit control and P4 capture pass do not erase the diagnostic failure.
SS03 is complete. No diagnostic repair or capture-free EDP control was needed.
