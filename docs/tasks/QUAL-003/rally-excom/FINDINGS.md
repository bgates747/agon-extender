# Current Rally Legacy/ExCom diagnosis

## Executive summary

**A small hardware test reproduces the left-road defect: ExCom differs from
Legacy at14of80sampled pixels using current Rally's exact buffered road-section
program.** The same seven left-side locations disagree on both pages. Simpler
scroll, page-retention, raw triangle and direct bitmap tests match. Stop here for
Author review, before changing firmware or running a larger suite.

The leading cause is an inherited float-to-unsigned conversion whose behavior
is not portable between Xtensa and RISC-V. That source is identical to stock;
this is a compatibility adaptation candidate, not permission to improve stock
VDP. A controlled correction/rerun is still needed to establish causation.
The full HUD flicker remains unresolved. These are pixel-correctness results,
not frame-rate or throughput measurements.

## Most informative results first

| Hardware test, same bytes on both routes | Legacy | ExCom | Paired difference |
|---|---:|---:|---:|
| r03: current buffered road section |80samples|80samples|14different,17.5%|
| r02: direct clipped bitmap and raw triangles |68samples|68samples|0|
| r01: protected scroll, pages, clipped horizontal span |64samples|64samples|0|

Percent here is mismatching samples / samples, **not performance difference**.
The14differences are7unique positions repeated on2pages. All lie at x0..30.
Examples (RGB values):

| Position | Legacy mainboard VDP | ExCom P4 EDP |
|---|---|---|
| x0,y180 |85,85,85 — road gray|0,170,0 — grass green|
| x20,y180 |85,85,85 — road gray|255,0,0 — kerb red|
| x10,y200 |85,85,85 — road gray|255,0,0 — kerb red|
| x0,y220 |85,85,85 — road gray|0,170,0 — grass green|

All local fixed expectations passed. The road probes deliberately use sentinel
999expectations: their CSV terminal `failures=0` only means local controls passed,
**not** Legacy/ExCom parity. comparison.json lists the14actual disagreements.

## What the test isolates

1. Current game is AgonArcade main9e75196, default grip200, eZ80 lookup-based
   projection. Golem sources/builds are excluded. The accepted game still uses
   stock buffered matrix commands to expand each eZ80-computed road section.
2. r03copies the exact startup array from current
   rally-production/include/section_protocol.hpp and sends its exact25-byte
   section::draw packet. The legal test section spans y160..224, centre160at the
   top and120at the bottom; projected left endpoints become negative.
3. r01tests VDU24/MOVE clipping activation, graphics-viewport horizontal scroll,
   retained24-row HUD area and buffer alternation. r02adds negative-position
   direct bitmap drawing and the raw paired triangle sequence. Their passing
   results narrow this road reproduction to buffered section processing rather
   than a general failure to clip raw triangles or retain pages.
4. Red HUD control pixels remain intact in these tests. Full custom-font HUD,
   scenery bitmap strip repairs, live traffic and full-game phase changes are
   not covered; do not claim the reported HUD disappearance is explained.
5. Both routes used mode136on the same mainboard/EMOS, with selected destination
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
unchanged r03fixture first. Also cover representable negative/zero/positive values,
16/32-bit formats and shifts. Do not silently redefine overflow, NaN or infinity
behavior. Leave official upstream checkouts unchanged. If r03does not converge,
withdraw this causal hypothesis and inspect intermediate transformed data.
Then resume full HUD diagnosis and the wider relevant/performance comparisons.

## Identities, timing and evidence

- results/identities.json records all fixture source commits, binary hashes and
  sizes. Raw paired CSVs are in results/r01, r02and r03; no external art used.
- Mainboard VDP remains official2.16.0; EMOS/P4 remain the restored pre-E09 images
  documented in the E09 restoration record. The UART-optimized E07P candidates
  were not installed for these tests. Do not compare these as optimized E09
  frame-rate results. Machine-specific manifests remain in ignored agents/.
- r01fixture deployment completed in27.058s; r02staging29.977s and r03staging
  31.052s include independent stage/active readbacks and startup preparation.
  These are small-fixture end-to-end job durations, not raw UART transfer rates.
- r02collection observed32.65s and r03collection57.54s, including waiting and SD
  retrieval. The first started after reset. Neither is an exact fixture duration
  or rendering time. Current probes do not yet record complete target runtime;
  add that to a future revision before using them for execution estimates.
- The first service check was premature; both runs completed. No hardware hang
  was established. A short browser status capture during r01is retained locally
  and is not a benchmark. Subsequent probes required no browser output.

## Review boundary

No correction has been applied. Preserve this failing case and stop. Restore
original startup through a CLI-launched SD service before notification. Do not
replace an EXEC file while its batch still owns an open handle; subsequent
staging must explicitly exit that service and relaunch it directly first.
Earlier inter-probe staging did not explicitly close that handle; terminal CSVs
are retained, but this procedural oversight must not recur. The first final
restoration step closes the batch before modifying its file.
