# Browser output ideas and rejected approaches

## Executive summary

RLE2 remains the best demonstrated choice for the measured Nurples workload.
Pair-RLE did not improve it; preserve that experiment, but do not repeat it
without a materially different hypothesis. Frame differencing, mirrored scrolls
and browser-side sprite composition remain untested alternatives, not rejected
ones. The Author requested this discussion record only: no new implementation,
bench experiment or architectural replacement is authorized by this document.

## Evidence and dispositions

| ID | Approach | Disposition and reason |
|---|---|---|
| D01 | Current full-frame RLE2 | Retain. Matched Nurples comparison averaged 38,956 packet bytes and 21.07 browser submissions/s. These are not monitor scanout rates. |
| D02 | Six-bit packing alone | Not a replacement for RLE2 on this workload. Four pixels occupy three bytes: a 512×384 raster takes 147,456 payload bytes, versus about 39 KB with RLE2. Retain optional packing for appropriate content. |
| D03 | Pair-RLE, two six-bit colours plus four-bit count | Ruled out as the Nurples default by measurement: 52,357 packet bytes and 20.03 submissions/s. Automatic selection chose RLE2 throughout. Not a universal rejection for other imagery. |
| D04 | Separate literal flag in pair tokens | Discussed, then superseded by the Author's explicit “do your way.” Not hardware-tested; do not present this alternative as a measured failure. |
| D05 | Difference successive frames, then RLE2 | Untested in this comparison. Neither packed nor RLE2 comparison paths used temporal differencing. Stationary decorated regions could benefit; solid regions already compress well. |
| D06 | Browser rendering all VDP commands; small network bridge replacing much of P4 | Architectural possibility only. Broad compatibility and reply/timing responsibilities make this a larger undertaking than changing output encoding. No ESP8266 bridge design was verified. |
| D07 | Mirror scrolling and send corrective pixel patches | Promising untested hybrid; detailed below. Does not require reimplementing the whole VDP. |
| D08 | Pack a 16-colour background and send separate 64-colour sprites | Untested hybrid. Requires a clean background, sprite state/assets and exact palette/composition semantics. |
| D09 | Treat all software sprites as separate hardware-style sprites | Author suggestion, untested. Compatibility differences must be established before silently substituting this for existing software-sprite behavior. |

Measured evidence and limitations: [pair-RLE results](composed-packing/pair-rle/RESULTS.md),
[six-bit experiment](composed-packing/sixbit/PLAN.md), and
[composed packing](composed-packing/RESULTS.md). Existing pacing/push/worker
explorations remain in [the pacing plan](web-pacing/PLAN.md); this record does
not replace that plan or the authoritative task queue.

## Why pair packing did not help

1. Existing RLE2 handles runs up to 130 pixels. Pair-RLE repeats an ordered pair
   at most 16 times, covering 32 pixels per token. A 64-pixel solid span therefore
   requires two pair tokens but fits in one RLE2 run.
2. Pair-RLE's distinguishing opportunity is an alternating pattern such as ABABAB.
   Nurples did not supply enough useful pair repetitions to overcome its losses.
3. Differencing would create zero runs for unchanged regions, but ordinary RLE2
   benefits from those too. More unchanged pixels alone does not favour pair-RLE.
4. Six-bit pixels require four pixels/three bytes for exact byte packing. Two
   pixels in two bytes leave control bits but provide no literal-size saving
   versus the original one-byte-per-pixel representation.
5. The conversation's bezel arithmetic is not verified geometry: the Author
   recalls 16 tiles × 16 pixels = 256 pixels and a 384-pixel horizontal extent,
   giving two 64-pixel bezels. The assistant then inferred portrait orientation
   without checking the fixture. Do not propagate that inference as fact: verify
   mode, viewport, orientation and tile positions from Nurples source/captures
   before deriving region boundaries. Swapping axes does not change full-frame
   byte totals, but does change row runs and scroll rectangles.

## Temporal differences and recovery

The P4 could encode differences against the exact frame retained by the browser.
Zero means unchanged in that protocol; it must not mean “paint black.” Browser
reconstruction must use the agreed reversible operation, such as XOR or modular
subtraction/addition, rather than merely plotting nonzero delta values as colours.
No choice of difference operation is made here.

Frame identity, base-frame identity and recovery are necessary. Mode changes,
reconnection or loss of the expected base require a complete frame; periodic
complete frames are another option already raised by the Author. Dropping frames
must not break a delta dependency chain. Account for P4 reference storage,
comparison/encoding cost and browser reconstruction as well as wire bytes.

## Mirrored scrolling with patches

The P4 remains the authoritative renderer. It tells the browser to move an
existing rectangle, then supplies newly exposed pixels and corrective patches
for subsequent drawing. The browser retains unchanged bezels. A scrolling field
can therefore be represented by a movement command instead of a full set of
changed pixels, even when ordinary differencing would flag most of that field.

The browser must apply movement and patches in the correct order against a known
base, then present the completed update. Software sprites already in the scrolled
pixels, their restoration, overlapping drawing and clipped scrolling complicate
that ordering. Hardware sprites and Copper effects complicate treating the last
fully composited frame as a clean scrollable background. Keeping final composition
on the P4 initially is an option, but does not remove these correctness issues.
A complete-frame fallback is required. This is a proposal, not implemented work.

## Separate background and sprite planes

The Author proposes sending a 16-colour background as four-bit indices, and
keeping 64-colour sprite images in the browser. The P4 could send sprite assets
once, then positions, animation frame selections, visibility and ordering updates.
Palette entries may be any of the 64 colours; lossless four-bit background packing
requires at most 16 distinct background colours for the chosen representation.
Combining this with mirrored scrolling could reduce both pixel traffic and P4
composition work.

The Author's preferred simplification is to eliminate software sprites or treat
them all as hardware-style composited objects. Software-sprite drawing/restoration,
scroll interactions, plotting over sprites and pixel readbacks may differ from a
separate overlay. Determine actual upstream semantics before deciding what can be
converted transparently. An explicit new rendering mode is another possibility;
none is accepted here. Copper palette/row effects, sprite priority, transparency,
asset replacement and bitmap transforms must remain accounted for.

## Entire browser renderer / bridge alternative

A browser could receive VDP commands and assets instead of raster frames. The P4
could either retain rendering for local output/readback, or delegate rendering to
the browser. The latter could reduce the P4 to a bridge or permit different bridge
hardware, but moves reply availability and latency onto the browser/network path.
Startup, input, buffered commands and pixel queries remain responsibilities.
Reports of ESP8266 connections to Agon were conversational leads, not inspected
wiring or proof of a VDP replacement. Existing EMOS routing ownership remains the
project contract; these musings do not authorize a bypass.

## Reminder for future discussions

Check D01–D09 before reopening an idea. Distinguish “measured and not useful for
Nurples” from “not tested,” and distinguish application cycles, delivered frames
and displayed refreshes. Any future experiment should preserve the existing
RLE2 baseline and use identical source frames or matched deterministic runs.
No further experiments are started by this record.
