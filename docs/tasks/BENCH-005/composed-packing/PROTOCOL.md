# EVP1 experimental composed-frame packing

Recurring complete-frame wire details are now consolidated in the
[maintained browser-video contract](../../../protocols/browser-video.md#negotiated-complete-frame-encodings).
This record retains the experiment's original selection, limits and evidence;
it is not an assertion that its exact candidate is currently installed.

## Executive summary

EVP1 preserves the already-composited RGB222 image exactly using a frame-local
palette and MSB-first indices. It changes only network representation; no sprite,
Copper or native framebuffer interpretation occurs in the browser. It is opt-in
via `packed=1`; browser candidate requests `rle2=1&packed=1`.

## Wire structure

Retain EVF1's 32-byte header, changing its magic to EVP1. Version1, pixel format2,
width, height, sequence, flags and present period retain their meanings. Header
stride and payload length describe the **decoded RGB222 image**, as for EVR1.
Dimensions are bounded to1024×768. Payload after header:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 1 | Bits/index:1,2,4 |
| 1 | 1 | Palette entries:1..2^bits |
| 2 | 2 | Reserved zero |
| 4 | entries | Unique RGB222 values0..63 |
| 4+entries | ceil(width×height×bits/8) | MSB-first indices, contiguous raster |

Unused final low bits are zero. Invalid indices, duplicate/out-of-range palette
entries, reserved bits, malformed lengths or dimensions reject the entire frame.
Each frame is independent: reconnect, mode changes and palette changes require
no previous-frame state. The browser reconstructs standard EVF1 before existing
validation and WebGL presentation. Existing clients never receive EVP1 unless
requested. No modification to AGM or RLE2 asset contracts.

## Selection and storage

The P4 sends raw when no codec is requested. RLE2-only uses the existing encoder
with its old512×384 cap expanded to1024×768. Packed-only scans final colours and
packs up to16, otherwise raw. Automatic encodes RLE2 then attempts packing only
when the predicted packed size is smaller. Header/palette overhead is included.
This initial policy optimizes transmitted bytes; it does not claim minimum total
CPU time. Benchmark that tradeoff before considering a classifier or heuristic.
Two startup allocations:786446 bytes RLE2 scratch and393252 bytes packing scratch,
both PSRAM. Allocation failure falls back safely. Encoder hot path allocates no
heap storage and never acquires the graphics lock. The existing snapshot lease
remains held until transmission completes.

## Limits

Compositing cost remains. Copper/sprites can exceed16 final colours even in a
2-colour drawing mode, and then packing falls back. No colour is quantized away.
Frame coherence retains the existing snapshot semantics; this experiment does
not claim to repair concurrent-scene consistency or old Copper transition bugs.
Future256-colour support requires another wire contract; this one accepts only
RGB222. Native mode buffer depth does not appear in this format intentionally.
