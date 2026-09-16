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
