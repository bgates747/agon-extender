# Composed packing — findings and review

## Executive summary

Keep the lossless packing implementation. Across the 54-mode screen, automatic
selection improved median dense-scene throughput by 42.7% over matched RLE2-only,
with exact reconstruction of 107 static/dense scenes. It is not a universal
60 fps solution: large rasters remain slow and selecting the smallest payload can
cost more CPU than it saves. Human acceptance and production promotion remain
pending. The installed candidate is available for review; no remote publication
is part of this task.

## What changed

1. P4 composes the entire output first, including its existing software sprites,
   hardware sprite overlays and Copper processing. A frame-local palette then
   represents up to 2/4/16 actual final colours using 1/2/4 bits per pixel. More than
   16 final colours retain RLE2/raw. No colour approximation or transparency
   semantics are introduced into the completed image.
2. Nominal mode depth is insufficient to choose packing. The inherited sprite
   and Copper scenes can add colours beyond the drawing palette. For example,
   a nominal two-colour dense scene with a coloured hardware sprite needs more
   than one bit per pixel. Packing the final palette preserves it correctly.
3. EVP1 is explicitly negotiated. Existing raw and RLE2 clients remain supported.
   The installed browser requests both RLE2 and packed output; P4 chooses the
   smaller eligible payload. Decoder validates dimensions, indices, palette and
   padding before reconstructing the canonical one-byte-per-pixel image.
4. The old 196608-pixel RLE2 limit is raised to 786432 pixels on both endpoints.
   This independently fixes high-resolution exclusion; it must not be credited
   to packing when comparing against older deployed builds. Every measurement
   here uses the same expanded-bound candidate, including the RLE2 baseline.
5. Candidate 02 skips the palette scan whenever RLE2 already beats the theoretical
   smallest packed payload. Encoder scratch is preallocated outside the frame
   path. Snapshot ownership, drawing locks and scheduler policy are unchanged.

## Measurement scope

1. All 54 explicit modes in MODES.md completed:31 ordinary modes including
   teletext, plus 23 double-buffered variants. No 50 Hz mode is included. 70 Hz modes
   are included but browser requests remain capped at 60. Historical legacy
   numbering aliases were inventoried, not independently exercised; their 75 Hz
   alias is not a claim of 75 Hz output.
2. The suite has 160 mode/workload groups × 4 paths= 640 short trials. Static and
   dense images are byte-identical after decoding across all four paths in 107
   groups. 53 moving groups require changing sampled content and correct geometry;
   sequential moving captures cannot be compared bytewise. No browser page errors
   occurred in retained passing trials.
3. These checks establish preservation of the P4 compositor's output through the
   codecs. They do not reopen or close the mainboard pixel-parity exceptions in
   QUAL-004, nor certify every possible Copper/sprite programme.
4. The deterministic fixture reuses existing Copper/software/hardware sprite
   commands, then dense seeded bitmap tiles, then full-surface moving rectangles.
   Teletext gets its applicable static scene only. These are synthetic output
   workloads, not measured game simulation rates or physical monitor refresh.
5. FPS counts headless Chromium presentation submissions. Wire sizes include the
   frame protocol header but exclude TCP/Ethernet overhead. P4 snapshot and
   socket/encode timings, browser decode and presentation intervals remain
   separate; socket API completion is not physical wire delivery. Timing windows
   include warmup, whereas FPS windows exclude it. Ten trial timing windows with
   recorder loss are withheld; their independent pixel/FPS observations remain.
6. Short trials measure two seconds after one second of warmup, in a fixed path
   order. Small differences are not statistically established improvements.
   CONFIRMATION.md retains longer eight-second trials for modes 2 and 9 separately.
   No stock-mainboard performance comparison was run in this task.

## Remaining issues and first avenues

1. **Encoder selection overhead:** dense frames often run faster with packed-only
   than automatic, despite identical transmitted sizes. For mode 143's dense
   screening, packed-only delivered 53.95 fps versus 30.00 automatic; socket/encode
   means were 4.65 ms and 8.60 ms respectively. A future selector should avoid
   computing both complete encodings unnecessarily, while preserving exact
   pixels and efficient RLE2 for sparse frames. This is a recommendation, not an
   additional implementation authorized or performed in this run.
2. **Small-payload pacing:** some sparse scenes plateau around 15 fps while others
   with small payloads approach 60. Composition/encoding alone does not account
   for every interval. Measure request, TCP delivery and browser presentation
   together before diagnosing the cause. ACK/Nagle behaviour is an untested
   hypothesis; no transport redesign or clock synchronization was performed.
3. **Mode-transition reliability:** ten accepted mode runs needed the bounded
   extra reset after keyboard admission failed following active Copper/sprites.
   This reproduces the known transition issue; passing after recovery does not
   qualify the transition itself. Exact modes are in RESULTS.md.
4. **Collection interruptions:** staging modes 12 and 27 hit keyboard HTTP timeouts;
   mode 142 hit a diagnostic HTTP timeout, then a page-load timeout on its moving
   trial. Completed cases were preserved and only missing work resumed. The
   unchanged direct moving retry passed. These interruptions are not hidden
   behind the overall pixel-pass count.
5. **Resource/cost limits:** large rasters still cost full composition and a
   complete snapshot. Packing reduces network payload, not the initial raster
   work. Scratch reservations are 786446 bytes for RLE2 and 393252 for packing,
   in PSRAM. This is a retained experimental source-tree overlay, not a clean
   production release.

## Reproduction and evidence

PLAN.md records the frozen scope and self-assigned bounded corrections.
BUILD-R02.json pins firmware and fixture hashes. PROTOCOL.md specifies EVP1;
packed.hpp and decoder.js are the retained implementation. prepare.py/build.py
recreate the overlay; test.py holds 70 host round trips and 8 malformed rejections.
run.py/observe.py reproduce hardware collection and report.py produces the tables.
Private raw samples and decoded images remain under agents/composed-packing,
with valid sweep02–sweep06 and confirmation01 directories. Earlier provisional
sweeps are not counted. Firmware artifacts and rollback images remain there too.
Production games, mainboard VDP and EMOS firmware were not changed.
