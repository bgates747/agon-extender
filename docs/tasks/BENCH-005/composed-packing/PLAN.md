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
3. [x] P03 — Build and deploy P4 candidate with verified identity and assets.
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

## Execution notes / self-assigned fixture adaptation

Official references inspected: VDP v2.16.0, MOS v3.0.2, agon-docs
f9806bd3cbff6ed5d1c08bef1d51fed11764b86b. All are read-only.
The deterministic fixture reuses QUAL-004 Copper setup (including software and
hardware sprites), plus BENCH-005's animated rectangle approach scaled to each
surface. This avoids assuming game binaries support arbitrary mode geometries.
Raw/RLE2/packed/automatic selection share the exact installed compositor and
request cap. Host codec tests cover extra colours and fallback. Browser timings
are headless Chromium presentation submissions, not physical display refresh.
The preserved source-tree overlay is experimental (not a clean-tree release).
SD uploads explicitly preserve startup then clean its known previous-transfer
backup before replacing it. Initial staging API/state mistakes were corrected
before executing a scene; they are not graphics failures.

The first silicon smoke (mode9) reconstructed all four paths identically. Sparse
Copper scene strongly favours RLE2, so a self-assigned dense deterministic bitmap
tile stage was added before animated tiles. It resets the row palette list to
exercise nominal palette packing, while the preceding static stage retains Copper.
This makes the workload comparison cover both long runs and short-run imagery.

A second startup after live Copper/sprites reproduced the known P4 reset: boot
banner at640×480, keyboard admission false. One subsequent mainboard reset from
the now-clean P4 state restored mode9 and exact pixels. Self-assigned isolation:
record this exception, permit one bounded startup retry only when admission is
false, then stop if still unavailable. Such a retry is not a pass for transitions.
Do not count boot-screen samples. Fixture geometry is checked for every path.

## Self-assigned bounded optimisation to evaluate after the first sweep

Automatic selection currently scans the entire frame for palette eligibility even
when RLE2 is already smaller than the theoretical minimum packed image. A safe
lower-bound check (one palette entry plus ceil(pixels/8) plus header) can skip that
scan without changing transmitted bytes. Preserve the initial candidate/results;
implement and compare selected sparse/dense cases after the baseline sweep, not
mid-run. No change to rendering or locking is needed.

Initial sweep screening exposed a fixture-control flaw: immediate down/up pairs
can be missed by foreground keycount polling. The first sweep is provisional;
its mode3 dense image remained unchanged. Hold injected keys200ms, verify dense
far-corner pixels and moving content markers, and restart the sweep with this
stronger acceptance gate. Do not publish those earlier missing-workload samples
as dense/animated performance. This corrects the test, not P4 rendering.

Sequencing amendment (self-assigned): because the initial all-mode sweep must be
restarted for reliable workload control anyway, apply the already-described
minimum-size short circuit before the replacement sweep. Preserve candidate01
and its valid preliminary controls. Repeat host tests and selected silicon
controls, then use one immutable candidate02 for the full replacement sweep.

Dense mode2 now passes the far-corner black/white check after clearing its buffer
and flushing creation, with candidate02 installed. Preserve this corrected
control; it supersedes the missing-tile attempts. The final sweep uses200ms taps,
explicit buffer replacement, palette setup, far-corner checks and moving markers.

Observed timing follow-up, not assigned implementation: some small RLE2 payloads
settle near15fps despite mean P4 snapshot+socket phases below11ms; larger images
sometimes reach30fps. The socket phase measures API send time, not TCP delivery.
Record browser/request/network waits separately before attributing these plateaus
to rendering. TCP packet/ACK behaviour is a hypothesis only, not a diagnosed cause.
No networking/scheduler redesign is authorized by this packing experiment.

Corrected sweep02 completed modes0–11 (34 workload groups). Preparing mode12
encountered one keyboard HTTP timeout after route switching, before its startup
was uploaded or measured. Keyboard status subsequently returned ready/neutral.
A bounded ordinary reset restores known startup before continuing unchanged
firmware/fixture as sweep03 from mode12; completed measurements are preserved.
