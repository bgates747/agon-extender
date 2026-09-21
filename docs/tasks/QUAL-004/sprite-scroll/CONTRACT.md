# Sprite motion and scrolling checkpoints

## Executive summary

Author approved deterministic moving-sprite/scroll qualification. Use mode20,
two explicit software sprites and four accumulated-history checkpoints. Compare
physical mainboard scanout with P4 snapshots; no game changes, performance work,
Copper, hardware-sprite stress or renderer fixes. New fixture identity
sprite-scroll-probe-r01 and registry r95 use standing identity approval.

**QUAL-004-SS01** [ ] Freeze generator/inputs/oracle/contract before deployment.
Preserve actual mainboard flash/startup; verify player and deployed input hashes.
Reuse existing all-depth diagnostic; P4/EMOS remain unchanged.

**QUAL-004-SS02** [ ] Select mode20 only through startup. Capture INITIAL,
OVERLAP, EDGES and HIDDEN after replay of identical accumulated updates from
fresh starts. Two independent mainboard captures and two distinct matching P4
generations per checkpoint; compare every 512×384 pixel without masks/tolerance.
Updates cover transparent software sprites, movement/frame changes, overlap,
viewport scrolling and drawing an eight-row bitmap through a one-row viewport.
Stop/restore on unexpected reset, incomplete acquisition or repeat instability.
No renderer/fixture repair to force agreement.

**QUAL-004-SS03** [ ] Independently compare the entire final hidden-sprite image
with a simple striped-background/scroll/refill oracle. This catches both stale
sprite pixels and drawing outside the one-row viewport. Require visible sprite
content earlier so a disabled-sprite fixture cannot pass merely by agreeing.
Retain mismatches with scope limits; no assertion of tear-free live animation.

**QUAL-004-SS04** [ ] Hide sprites and drain before mode teardown, restore exact
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
