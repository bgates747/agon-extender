# Current Rally Legacy/ExCom diagnosis

## Executive summary

**The immediate numeric repair passes the unchanged hardware reproduction:
ExCom now matches stock at all 80 samples, eliminating the previous 14 pixel
differences.** The stock results remain unchanged. The P4-only checked signed
conversion therefore resolves this reproduced left-road defect. See
[RX06 evidence](rx06/README.md) for the controlled installed-parent build,
raw results, limits and exact hashes.

The Author has now accepted the unmuted Rally HUD/sky repair through the
[stock audio dispatcher/no-op backend](../../PORT-004/audio-framing/results/README.md).
The [RX07 numeric inventory](rx07/README.md) is complete and awaiting RX08
Author disposition before corrections. The broader unsupported-command audit
remains open. No measured hardware game FPS or performance improvement is
claimed. Historical sections below retain the original diagnostic progression.

The following table preserves the original diagnostic run before repair.

## Most informative results first

| Hardware test, same bytes on both routes | Legacy | ExCom | Paired difference |
|---|---:|---:|---:|
| r03: current buffered road section |80 samples|80 samples|14 different, 17.5%|
| r02: direct clipped bitmap and raw triangles |68 samples|68 samples|0|
| r01: protected scroll, pages, clipped horizontal span |64 samples|64 samples|0|

Percent here is mismatching samples / samples, **not performance difference**.
The 14 differences are 7 unique positions repeated on 2 pages. All lie at x0..30.
Examples (RGB values):

| Position | Legacy mainboard VDP | ExCom P4 EDP |
|---|---|---|
| x0,y180 |85,85,85 — road gray|0,170,0 — grass green|
| x20,y180 |85,85,85 — road gray|255,0,0 — kerb red|
| x10,y200 |85,85,85 — road gray|255,0,0 — kerb red|
| x0,y220 |85,85,85 — road gray|0,170,0 — grass green|

All local fixed expectations passed. The road probes deliberately use sentinel
999 expectations: their CSV terminal `failures=0` only means local controls passed,
**not** Legacy/ExCom parity. comparison.json lists the 14 actual disagreements.

## What the test isolates

1. Current game is AgonArcade main 9e75196, default grip 200, eZ80 lookup-based
   projection. Golem sources/builds are excluded. The accepted game still uses
   stock buffered matrix commands to expand each eZ80-computed road section.
2. r03 copies the exact startup array from current
   rally-production/include/section_protocol.hpp and sends its exact 25-byte
   section::draw packet. The legal test section spans y160..224, centre 160 at the
   top and 120 at the bottom; projected left endpoints become negative.
3. r01tests VDU24/MOVE clipping activation, graphics-viewport horizontal scroll,
   retained 24-row HUD area and buffer alternation. r02adds negative-position
   direct bitmap drawing and the raw paired triangle sequence. Their passing
   results narrow this road reproduction to buffered section processing rather
   than a general failure to clip raw triangles or retain pages.
4. Red HUD control pixels remain intact in these tests. Full custom-font HUD,
   scenery bitmap strip repairs, live traffic and full-game phase changes are
   not covered; do not claim the reported HUD disappearance is explained.
5. Both routes used mode 136 on the same mainboard/EMOS, with selected destination
   established in startup. No firmware was built or flashed. Native USB input
   and the normal SD service remain the control/retrieval paths.

## Conversion hypothesis and minimal next experiment

`video/types.h::convertFloatToValue` writes signed fixed-point data using direct
casts `(uint16_t)(rawValue / scale)` and `(uint32_t)(rawValue / scale)`.
Negative integral results outside the unsigned range are not a defined C++
conversion. `bufferTransformData` uses this function when writing transformed
road coordinates back to the VDU command buffer. The same function body is in
official agon-vdp v2.16.0 and the Extender tree; it has not been agent-redesigned.

A small compiler audit is retained in results/r03. The selected RISC-V compiler
emits `fcvt.wu.s ... rtz`; the installed Xtensa compilers emit `utrunc.s`.
A signed-intermediate illustration instead emits `fcvt.w.s`/`trunc.s`.
This establishes a concrete architecture-sensitive conversion boundary; the
isolated compiler outputs are **not** a disassembly of the currently installed
firmware and do not alone prove the cause of the pixel differences.

After review, the next experiment should preserve stock signed fixed-point
semantics with the smallest P4-specific conversion adaptation, then rerun this
unchanged r03 fixture first. Also cover representable negative/zero/positive values,
16/32-bit formats and shifts. Do not silently redefine overflow, NaN or infinity
behavior. Leave official upstream checkouts unchanged. If r03 does not converge,
withdraw this causal hypothesis and inspect intermediate transformed data.
Then resume full HUD diagnosis and the wider relevant/performance comparisons.

## Identities, timing and evidence

- results/identities.json records all fixture source commits, binary hashes and
  sizes. Raw paired CSVs are in results/r01, r02 and r03; no external art used.
- Mainboard VDP remains official 2.16.0; EMOS/P4 remain the restored pre-E09 images
  documented in the E09 restoration record. The UART-optimized E07P candidates
  were not installed for these tests. Do not compare these as optimized E09
  frame-rate results. Machine-specific manifests remain in ignored agents/.
- r01 fixture deployment completed in 27.058 s; r02 staging 29.977 s and r03 staging
  31.052 s include independent stage/active readbacks and startup preparation.
  These are small-fixture end-to-end job durations, not raw UART transfer rates.
- r02 collection observed 32.65 s and r03 collection 57.54 s, including waiting and SD
  retrieval. The first started after reset. Neither is an exact fixture duration
  or rendering time. Current probes do not yet record complete target runtime;
  add that to a future revision before using them for execution estimates.
- The first service check was premature; both runs completed. No hardware hang
  was established. A short browser status capture during r01 is retained locally
  and is not a benchmark. Subsequent probes required no browser output.

## Review boundary

No correction has been applied. Preserve this failing case and stop. Restore
original startup through a CLI-launched SD service before notification. Do not
replace an EXEC file while its batch still owns an open handle; subsequent
staging must explicitly exit that service and relaunch it directly first.
Earlier inter-probe staging did not explicitly close that handle; terminal CSVs
are retained, but this procedural oversight must not recur. The first final
restoration step closes the batch before modifying its file.

## Bench returned for review

Original load-only Nurples autoexec is independently restored, SHA256
38f0a73389c584b0884b5a718a20cb9c610bd4f249a3af447912c0415ec5678e.
The older pre-test activation backup is preserved as /extender/RXOLDBOOT.TXT;
the temporary test-startup fallback was removed. Firmware and production Rally
were unchanged. Legacy MOS prompt is available. The accepted British hardware
voice player replaced a fresh pending receipt with audio_commands=pass and
returned through a fresh SD service; the service was then exited. Human hearing
is not yet confirmed. No firmware correction or wider suite was started.


## Author visual review and HUD trace — 2026-09-15 UTC

The Author confirms the roadway looks correct after RX06. The Author reports
black sky on straights and sky repaint/sideways scrolling during turns; HUD
remains incorrect. This is visual acceptance of the road correction, not of the
whole game or P4 port.

Current Rally does not clear the entire HUD each frame. `rally-game/include/hud.hpp`
initializes rows 0–23 separately on each page, then emits changed text cells only.
`src/main.cpp::drawScenery` clips scrolling below row24 (below88 with a panel).
`rally-production/include/scenery.hpp` retains each page on unchanged heading;
turns scroll and repaint exposed strips. A bottom scenery strip is refreshed
regularly. An unexpected erase therefore leaves static HUD cells and most sky
absent, while changing values and exposed scenery strips reappear.

P4's selected `unavailable_audio_adapter.hpp::vdu_sys_audio` is empty and does
not consume channel, operation or operands. Rally's `Engine::update` emits
`23,0,0x85,0,3,freqLo,freqHi`. Those remaining bytes can become ordinary VDU
commands. For example speed94/95 produces268Hz, with low byte12 (`CLS`);
speed96/97 produces272Hz, low byte16 (`CLG`). Context::cls clears the text
viewport, independent of the road graphics clip. These are concrete unsafe
parser paths, not proof that those exact speeds caused the observed erasure;
other escaped bytes can also alter parser/display state.

The existing `mute` option prevents Engine::start, leaving active=false, so
update and stop emit no audio. The next discriminating physical comparison is
the unchanged game on ExCom with/without `mute`, with the existing Legacy
control (PORT-003 UC06). Do not compensate by repainting retained areas every
frame. No new hardware test or firmware/game source change was performed during
this code trace. Safe audio payload consumption remains the separate planned
no-op work, not completed audio synthesis.

The Author subsequently tested `mute` and reports that it eliminates the HUD/sky
problem. This strengthens the audio-framing diagnosis; a corrected unmuted
firmware test remains required before closing that defect.
