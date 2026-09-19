# W08 — Pack completed browser frames, all-mode qualification

## Executive summary

Author authorizes implementation and hardware benchmarking after full P4 composition.
Preserve software sprites, hardware sprites and Copper by encoding the completed
RGB222 snapshot; do not bypass composition or move sprites into the browser.
Compare exact reconstructed pixels and delivered cadence against working RLE2,
with raw controls. No Golem. Production games and mainboard firmware remain unchanged.
Hardware voice notification concludes the run. Experimental work remains unpublished.

## Contract and bounded précis

Official Screen-Modes.md and Copper-API.md in the read-only agon-docs checkout
establish explicit modes, double-buffer swaps, and scanline palettes. Copper and
hardware sprites can produce up to 64 final colours in a nominal 2-colour mode.
Consequently packing uses the actual completed image's distinct RGB222 colours,
not the drawing framebuffer's nominal palette. A small frame-local palette plus
1/2/4-bit indices preserves up to 2/4/16 colours exactly. More colours retain
RLE2/raw; no quantization. Packing across the whole raster with defined padding
avoids row-alignment ambiguity. Old clients retain existing wire formats.

The installed lineage is agents/web60/manifest.json, sourced from the preserved
candidate02 tree. Main-tree equivalence is not assumed. Existing RLE2 excludes
images over 196608 pixels; extend encoder and decoder bounds to 1024x768 for
matched controls. Preallocate scratch outside the frame hot path, preserve
immutable snapshot leases and compression outside drawing locks. New format is
explicitly negotiated and includes its palette in each complete frame.

## Ordered work

1. [x] P01 — Freeze this contract; capture source/firmware identities, inventory
   every explicit non-50-Hz mode and buffering variant; clear previous bench cue
   at a verified prompt, save startup and preserve rollback artifacts.
2. [x] P02 — Implement bounded lossless final-frame palette packing and browser
   decoding; retain RLE2/raw controls and choose the smaller eligible payload.
   Test exact round trips, palette overflow, malformed lengths/indices, all mode
   dimensions, and frames containing colours beyond the nominal mode depth.
3. [ ] P03 — Build and deploy P4 candidate with verified identity and assets.
   Reuse deterministic graphics fixtures, adapting geometry/depth and swaps as
   necessary; modes selected in temporary autoexec only. Record exceptions for
   unsupported modes/features rather than silently substitute.
4. [ ] P04 — Benchmark all supported non-50-Hz modes with matched deterministic
   workloads and encoding selections. Include static/text, moving rendering,
   software/hardware sprite and Copper correctness cases where supported. Reuse
   existing scene commands. Separate rendering from capture/encode/send/decode/
   presentation timings wherever instrumentation permits; report unavailable
   metrics honestly. 60 Hz request ceiling is not a claim of 60 delivered fps.
   Include 70 Hz modes and document legacy-numbering aliases separately.
5. [ ] P05 — Review results; make bounded corrections if evidence warrants them,
   rerun affected cases. Tables give bytes, milliseconds, fps, baseline-relative
   differences and sample counts. Record elapsed execution for future estimates.
6. [ ] P06 — Restore startup, close observers, release keys, preserve a working
   candidate or restore rollback on failure; record bench state and limitations,
   commit discrete work, and notify on hardware for Author review.

## Boundaries and decisions

No new sprite architecture, RLE2 asset-contract change, lossy conversion, push
transport, scheduler redesign, EMOS change or mainboard VDP flash. Existing
QUAL-004 Copper transition failures remain exceptions; do not hide or relabel them.
Use test-only files under /test. Preserve unrelated repository dirt. Missing
observability or allocation/mode failures are reported, not inferred successes.
Self-assigned changes to this plan must be explicitly labelled and justified.
