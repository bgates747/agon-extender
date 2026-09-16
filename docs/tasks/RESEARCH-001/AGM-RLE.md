# AGM RLE — source inspection and possible output experiment

## Executive summary

Found the Author's non-expanding 64-colour RLE family in agon-utils. The AGM
variant supports transparent runs of up to64 pixels in one byte and opaque
colour runs of2–64 pixels in two bytes. Single opaque pixels cost one byte.
This is more expressive than our conversational guess of two run-count bits
encoding1–4 pixels. Both exploit the spare bits; they are different formats.

This is a promising **transport-only** pressure-relief experiment. Keep full
VDP drawing semantics and the one-byte-per-pixel/256-colour performance goal.
No code was modified, built or tested, and no bench action was taken. Actual
encoding/decoding costs and contention savings remain unmeasured. P06 in the
[work plan](../QUAL-003/DEBRIEF-PLAN.md#p06--browser-delivery-audit-and-isolated-pattern-benchmark)
owns the optional experiment and review gate.

## Source and exact format

Read-only reference: `bgates747/agon-utils` at
`e2756ae1aa9367d26f4f6202ea4042d8ee146169`. The inspected files match HEAD;
unrelated dirty work elsewhere in that repository was left untouched.

1. [`src/rle.c`](https://github.com/bgates747/agon-utils/blob/e2756ae1aa9367d26f4f6202ea4042d8ee146169/src/rle.c):
   `_rle_encode_internal` and `_rle_decode_internal`.
2. [`src/agm.c`](https://github.com/bgates747/agon-utils/blob/e2756ae1aa9367d26f4f6202ea4042d8ee146169/src/agm.c):
   `compute_difference` and `_process_mp4`.
3. [`utils/rle/rle2.c`](https://github.com/bgates747/agon-utils/blob/e2756ae1aa9367d26f4f6202ea4042d8ee146169/utils/rle/rle2.c):
   a separate format with runs3–130 in two bytes, singles/pairs as literals,
   and a14-byte file header. Do not confuse it with AGM's codec.

For AGM, source pixels are RGBA2222: zero upper alpha bits mean transparent;
nonzero upper bits mean an opaque six-bit colour.

| Input group | Encoded bytes | Payload cost |
|---|---|---:|
| Transparent run, length n=1–64 | `0x40 \| (n-1)` | 1 byte |
| Opaque singleton, colour c=0–63 | `0x80 \| c` | 1 byte |
| Opaque repeated colour, n=2–64 | `0x80 \| (n-1)`, then `0xC0 \| c` | 2 bytes |

Decoder distinguishes an opaque singleton from a run by checking whether the
following byte has its upper bits set to11. Such a byte occurs as the second
byte of a run, never as the next standalone command. This lookahead is part
of the format and needs bounds checks in any network decoder.

Each group costs no more bytes than its consumed pixels; summing proves the
encoded **pixel payload** never exceeds the input pixel count. AGM adds a
four-byte length field per frame, and RLE2 adds its own header. Neither file
framing nor network headers are covered by the payload non-expansion guarantee.

Calculated payload examples at512×384 (not measured timings):

| Image/difference content | Encoded bytes | Raw pixel bytes |
|---|---:|---:|
| Every pixel is an opaque singleton | 196,608 | 196,608 |
| Entire frame unchanged, represented as transparent zero | 3,072 | 196,608 |
| Entire frame one opaque colour | 6,144 | 196,608 |

No four-pixel row-width restriction applies to this byte-token RLE. Define
whether runs cross row boundaries and how any source stride padding is handled.

## Integration details a direct copy would miss

1. `compute_difference` uses **replacement values**, not XOR: unchanged pixels
   become0; changed pixels retain the new RGBA2222 value. The inspected AGM
   writer does not call that helper; it currently RLE-encodes `finalDither`, a
   complete frame. Presence of the helper does not prove active delta playback.
2. Extender's current RGB222 transport uses `00BBGGRR`. Passing it directly to
   the AGM encoder would classify **every pixel as transparent**. A proposed
   encoder must tag changed/full-frame colours with opaque bits, reserving0
   for unchanged pixels. Changed black must remain distinguishable from skip.
   Reference: `vdp/video/extender/web/frame_protocol.js`, `PixelFormat.RGB222`.
3. The utility decoder expands transparent pixels to0; it does not itself
   preserve a previous frame. A browser delta decoder would advance over skip
   runs and overwrite only literal/repeated changed colours. XOR deltas are a
   different proposed format and must not be mixed with these semantics.
4. The utility encoder mallocs twice the input size and then reallocs. Its
   expansion comment is overly conservative: the group proof above bounds
   payload byN. A P4 candidate should use bounded preallocated storage and
   consider fusing comparison with encoding instead of allocating a temporary
   difference image. Reading the previous frame still costs memory bandwidth;
   fewer wire bytes do not prove less total contention.
5. EVF1 v1 currently requires full frames and `payloadBytes == stride*height`.
   An RLE/delta encoding requires an explicit reviewed protocol extension and
   matching browser decoder, not silently reinterpreting existing bytes.
6. AGM decoder sizes output from tokens. A network decoder must additionally
   enforce declared dimensions, compressed/input bounds, exact decoded pixel
   count and maximum run endpoints. RLE2's decoder writes runs without checking
   against its declared original-size allocation; do not reuse it unreviewed.
   Source inspection only; no malformed-input test was run or utility fix made.

## Proposed contract to review, not yet implementation authority

1. Distinguish raw full frame, RLE full frame and RLE replacement delta explicitly.
   Retain the raw eight-bit baseline, and never apply six-bit colour masking to
   future256-colour pixels. Compression of presentation data must not skip VDP
   commands or redefine rendering completion.
2. P4 and browser identify stream/mode generation, current frame and delta base.
   Use the exact baseline the browser retains. Dropping a captured/queued frame
   must not advance the producer's reference invisibly. Define client ACK and
   buffer ownership; a socket send return alone is not client application ACK.
3. Require an independent full frame on connect/reconnect, mode/dimension/format
   changes and lost/invalid reference. Consider a periodic full refresh as a
   recovery point; interval remains undecided. Choose raw full-frame fallback
   when total encoded cost is no better. Palette-generation updates must be
   explicit for future indexed modes; RGB222 presently transmits final colours.
4. Proposed host checks before hardware: all64 colours, changed black, unchanged
   runs, lengths1/2/63/64/65, incompressible data, malformed/truncated tokens,
   reconnect/mode changes and skipped-source-frame sequences. Compare every
   reconstructed frame byte-for-byte, and verify encoded payload<=N.
5. Proposed matched controls: raw, RLE full, and RLE delta with identical game
   workload and frame accounting. Measure P4 comparison/encoding, extra memory
   reads/storage, wire bytes, browser decoding/presentation and drawing tails
   separately. Include noisy worst-case frames and periodic keyframe bursts.
   Retain complete output delivery accounting; average bandwidth alone is not
   a60Hz pass. Bench implementation/tests remain pending review.
