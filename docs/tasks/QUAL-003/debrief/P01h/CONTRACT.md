# RLE2 candidate contract — r01

## Executive summary

Clean-sheet, allocation-free codec with historical RLE2 v1.0 wire compatibility.
First candidate measures P4 codec costs and adds asset decoding through existing
buffered command65. Web transport integration remains a separate gate.

1. Historical handler recovered from personal agon-vdp `origin/compression`,
   commit c33b3c23397670e85c38c84941d592a3bbca801e (2025-03-11),
   `video/vdu_buffered.h` and `compression_rle2.h`: command65 dispatches `Cmp`
   header type `r` to RLE2, alongside TurboVega and szip. Reuse this structure;
   command67 is not reassigned. Upstream main/v2.16.0 currently points to
   c7ac293d2aa81ddfa693390549bcd909069c8fc3. Listed upstream branches are main
   and adjust-porch; no new opcode is allocated by this extension.
2. Asset bytes: `Cmpr`, unsigned32-bit little-endian decoded count, `RLE2`,
   major1/minor0, then tokens. Bit7 singleton: lower6 colour, bit6 expands to
   alpha00 or11. Other tokens0..127 repeat the following full byte3..130 times.
   Decode preserves run literals including partial alpha. Encode supports only
   alpha00/11; unsupported partial alpha fails rather than silently losing it.
3. Candidate command: `23,0,160,dstLo,dstHi,65,srcLo,srcHi`. For typeT leave
   stock decoder untouched. Type r validates full header/version, complete token
   stream and exact output size. Reject empty or output above1MiB for this
   candidate; malformed input leaves destination unchanged. No new reply packet:
   existing completion query provides ordering, and image/readback tests prove
   outcome. A later status capability must not be invented implicitly.
4. Source buffers may be fragmented. Copy RLE2 source into temporary contiguous
   storage without changing its published blocks; decode to another temporary
   buffer. Retain source until success, then replace destination using existing
   buffer lifecycle. Same source/destination allowed. Peak temporary storage is
   encoded plus decoded bytes; asset allocation is outside per-frame web work.
   Source/destination IDs and bitmap creation remain ordinary VDP contracts.
5. Diagnostic HTTP codec benchmark is task-local, no VDU ownership bypass. It
   generates deterministic opaque snapshots, encodes/decodes preallocated PSRAM
   arrays, verifies exact bytes and reports microseconds and sizes. It performs
   no drawing and its timings are not whole-game/network FPS. Bounded trials
   run at idle; production endpoint promotion is not authorized.
6. Host implementation uses no upstream codec code, allocations, Xtensa assembly,
   unaligned integer loads, or assumed RISC-V special instructions. Legacy source
   provides format evidence only. The old decoder's unchecked source/output
   bounds and ignored version are not preserved. Author's format attribution
   remains intact. agon-utils reference commit0470f6f2e9c2cd44398c65b7863c6747bf5fc670.
7. Initial web extension design: negotiated optional full RLE2 file payload inside
   a new explicit codec envelope, retaining the14-byte file header; old EVF1 raw
   path unchanged. Do not repurpose EVF1 flags without specifying/checking all
   consumers. Frame dimensions, decoded size and sequence must agree; compressed
   frame only when total message smaller than raw. No delta state. Exact envelope
   implementation and negotiation remain H03 work, not frozen bytes yet.

## Web candidate protocol — EVR1 v1 (iteration3)

An upgraded client requests `/video?rle2=1`; ordinary `/video` remains EVF1 raw.
For that connection, server may send raw EVF1 or compressed EVR1. EVR1 retains
EVF1's32-byte metadata layout/version1, but magic is EVR1 and payload is a full
RLE2 v1.0 file. Header payloadBytes continues to mean **decoded** stride×height;
compressed length is WebSocket message length minus32. Only RGB222 format2 is
eligible; at most196608 decoded bytes and tightly packed stride=width. Every
frame independent. Browser validates compressed header, dimensions, decoded
length and token bounds, strips opaque alpha, reconstructs EVF1 metadata/pixels,
and applies existing parser validation. Raw fallback if encoded file is not
smaller, mode is ineligible, or preallocation failed. Reconnect resets eligibility.

Allocate196622-byte PSRAM encoder output once at HTTP startup, reuse only on
serialized HTTP send task; immutable snapshot lease survives through synchronous
send. No graphics locks added. Existing dispatch lock remains unchanged. Browser
requests no faster than30Hz; late frames do not produce catch-up bursts. Candidate
web UI opts in for qualification only; not a production default promotion.

## Diagnostic iteration — stack correction

First P4 codec benchmark request caused a serial-confirmed HTTP-task stack
protection fault: the task-local3KiB JSON array plus call overhead exceeded the
4KiB stack. Move response storage to checked temporary internal heap; preserve
allocation outside codec timing. Do not increase production task stack or change
scheduler policy. Repeat correctness/timing only on the corrected diagnostic.

## Measured implementation selection

P4 iteration3 improves dense-frame encode from approximately14.3ms to8.5–8.8ms
and decode from13.2ms to7.7–7.9ms. Run-heavy frames favour the original simple
encoder (approximately4.8–5.7ms). Iteration4 therefore samples496 adjacent pairs
at evenly spaced positions to choose simple versus word-batched encode. Both
emit identical full RLE2 bytes; sampling changes speed, never visual content or
frame omission. Asset decode uses the bounds-checked word variant. Retain raw
fallback and measure again before considering promotion.
