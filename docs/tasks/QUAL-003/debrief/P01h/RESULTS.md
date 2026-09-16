# RLE2 clean-sheet P4 development — bounded run

## Executive summary

**RLE2 delivers an improvement worth keeping: retain this implementation.**
In the matched Nurples trial, it restored application performance from **12.8 to
30 fps** and increased browser receipt from **4.7 to 29.2 fps**, while completed
image comparisons remained pixel-exact. Repeat the measurements and finish the
remaining compatibility checks before making it the production default.

The output-disabled control also ran at 30 fps. These figures represent one run
per condition with a Wi-Fi receiver, not full performance qualification; see
[tables](TABLES.md) for scope and uncertainty.

Candidate implements **both** P4 RLE2 asset decompression and negotiated web-frame
compression. Historical generic command65/header dispatch is retained; codec code
is new. Host golden/malformed tests, physical asset-image controls, negotiated
raw/compressed static frames and headless browser presentation have passed.
Production promotion remains gated on the remaining recovery/game evidence and
Author review. QUAL-004 remains separately open for its exceptions.

The measured P4 codec benefits from iteration; the data do not justify declaring
all patterns faster with one implementation. Simple scanning wins long runs;
word batching wins literal-heavy streams. The selected encoder samples a bounded
set of adjacent pixels to select the implementation, without changing encoded
bytes. No Xtensa code, custom assembly or new scheduler policy was adopted.

## Codec benchmark scope

Physical P4 at360MHz, PSRAM200MHz, GCC14.2 `-O2`,512×384 opaque RGB222 inputs.
One warm-up plus nine measured trials per pattern/variant, three requests per
candidate. Table generation uses median of request medians. Allocation, input
creation, result verification, JSON and network transfer are excluded from the
codec timers. They are **codec costs**, not rendering milliseconds or frame rates.
Synthetic patterns are constant, fixed-seed random, diagonal changing colours,
and16-pixel tiles. RLE file sizes include14-byte wrapper; WebSocket overhead is
separate. Raw full frame is196608 bytes.

## Correctness evidence

1. Host:1688 golden/random boundary checks per iteration,10000 malformed inputs,
   69 retained-image/synthetic inputs, plus100000 ASan/UBSan trials on each of
   initial and word-batched implementations. All completed checks passed.
2. P4 r03 asset command65: seven cases, each full196608-pixel image identical to
   the raw reference. Reference also matched a literal pixel oracle. Cases:
   ordinary compressed upload, header/token fragmentation, source=destination,
   invalid version, truncation and decoded-length overflow. Rejected inputs left
   the previous destination bitmap usable and preserved command alignment.
3. P4 r03 web negotiation: raw→RLE2→raw reconnection yielded identical static
   pixels. Full message196640 bytes became4368 bytes for this scene (97.78% less).
   First cached pre-scene snapshot is not treated as a current-scene frame;
   two warm-up credits precede comparison on each connection.
4. Headless Chromium on the Linux host presented150 frames in the five-second
   static observation, without page errors. This is a presentation count, not
   proof of150 distinct rendered game frames or physical panel scanout.
5. Browser decoder tests cover all64 colours, malformed runs, transparency
   rejection for composed frames, truncations and retained physical EVR1 frames.

## Failures and changes retained

The first task-local benchmark used a3KiB stack response array; the P4 HTTP task
raised a serial-confirmed stack-protection fault. Response allocation now uses
checked heap storage outside timed loops. Do not attribute this diagnostic bug
to stock VDP, RLE2 parsing or the existing web renderer. Subsequent codec benchmark
requests completed with exact decode verification. Mainboard startup readiness
also needed actual polling after its two-mode test startup, rather than a fixed
15-second assumption.

The historical decoder lacked source/output bounds checks and version validation;
those behaviours were not reproduced. New encoding rejects partial alpha instead
of silently losing it; decoding preserves literal run bytes. Encodable asset
alpha is00/11. This is not an arbitrary RGBA2222 four-alpha-level round-trip claim.

## Remaining qualification boundaries

No default production enablement or remote push. Delta compression and szip/SRLE2
remain deferred. Allocation-failure
injection, broad mode/palette and slow-client stress, exact transfer/decode/bitmap
creation timing separation, and full repeated game cadence qualification are not
covered merely by the passing static controls. Raw fallback preserves unsupported
formats/modes. Incompressible input still costs an attempted encode; tiny savings
can be insufficient to repay that CPU cost. A cost-aware bypass is future work,
not an unmeasured performance claim.

## Final candidate checks and next review

Candidate r06 repeated all seven asset controls successfully. The retained bitmap
fixture additionally produced exact raw/RLE image pairs for clipping, bitmap copy,
reflection/scaling and the software/hardware-sprite scene. Each comparison covers
all 196608 pixels. These are same-P4 raw-versus-compressed controls, not a new
mainboard-versus-P4 rendering qualification. QUAL-004 remains open independently.

An incompressible full-screen pattern negotiated with `?rle2=1` correctly fell back
to raw EVF1. Raw → opted-in → raw connections returned identical pixels. Retained
PNGs, compressed EVF captures and SHA256 results are in `evidence/`.

The matched game measurements belong to r05. r06 only rounds the browser request
delay upward to avoid fractional-millisecond timer truncation below the nominal
30 Hz interval; its asset/fallback checks passed, but its game cadence has not
been remeasured. Do not relabel the r05 numbers as r06 measurements.

First follow-up: Author visual review, then repeated matched Nurples runs with a
wired receiver and the final candidate; Rally remains untested in this chunk.
Next qualify allocation failures, slow consumers, broader mode/palette transitions
and transport/decode/bitmap-create timing separately. All experimental sources
remain in this task silo. No production defaults changed and no remote push.

## Bench disposition

Exact pre-task r43 P4 flash prefix restored and verified; original 89-byte startup
read back after normal reset. Mainboard VDP and EMOS were not flashed. Production
applications were not replaced. Test fixtures remain under `/test/rle2`. Candidate
r06 is retained for review, not installed. The one-hour budget includes restoration
and reporting; development stopped early enough to leave recovery margin.

Standard British hardware voice cue completed; fresh service receipt confirmed
audio commands and unchanged startup. Human hearing/visual acceptance remains
pending. Run completed in approximately 45 minutes, within the one-hour limit.
