# W07a — Packed framebuffer path audit

## Executive summary

**The installed RLE2 path excludes mode 0 entirely. Its encoder and browser decoder
limit a frame to 196,608 pixels (512×384); 640×480 exceeds that limit and the server
sends raw RGB222.** Requesting `?rle2=1` does not guarantee compression. This is a
concrete confound in our mode-0 versus mode-20 discussion, not a measured attribution
of all lag. Correct the earlier blanket statement that browser video is always
RLE2-compressed. RLE2 remains the accepted default negotiation policy.

**Native 16/2-colour buffers are already packed, and preserving them can avoid
expansion—but cannot blindly replace the composed output.** The installed path
expands palette indices, applies per-scanline palette/Copper state and overlays
hardware sprites before producing RGB222. Sprites can introduce colours outside
the native mode palette. Plain text is a promising restricted experiment, not a
license to discard composition for all programs.

Recommended order for review: first remove the resolution confound in a bounded
RLE2 eligibility experiment (server scratch limit **and** client decoder limit),
then compare native packed output against that corrected baseline. Do not compare
packing only against an accidentally raw mode-0 baseline and call the difference
an advantage over RLE2. Neither change is implemented by this audit.

## Installed lineage and scope

Installed candidate: `browser-credit60-r01`, exact build/hash in
[web-pacing/build.json](../web-pacing/build.json), derived from preserved fullscreen
r02. Its build uses the retained `agents/rle2-execution/candidate02/source` tree,
not the current main-tree generic compositor. The build script temporarily
substitutes web assets, then restores source assets; served client was inspected
separately. Current live decoder contains the same `n>196608` guard. See
[source evidence](source-evidence.json) for hashes, paths and excerpts.

No new firmware, output code, benchmark or wiring changes. Source reasoning only;
no assertion of CPU milliseconds saved. Mainboard stock references remain untouched.

## Actual path

1. `vdp/vendor/vdp-gl/src/dispdrivers/vga16controller.cpp` stores two indices per
   byte, high nibble first; `vga2controller.cpp` stores eight one-bit indices per
   byte. This is native drawing storage, not the final browser pixel format.
2. `extender/display/stock_p4_service.cpp::publish` obtains a snapshot slot,
   calls `prepareRows` in two-row batches in this configuration, and normalizes
   each row into one-byte RGB222 snapshot storage. `packed_pixels` means packed
   RGB channels within each byte here, **not** packed 4-bit/1-bit indices.
3. `stock_runtime_controller.hpp::prepareRows/prepareRowLocked` holds native
   exclusion per batch, preserves palette revision/Copper cursor rules, and
   invokes retained row preparation. A whole frame is not atomically locked.
4. `stock_scanline.cpp` expands native index pairs/octets through
   `getSignalsForScanline` lookup tables, then `decorateScanLinePixels`.
   VGA16 writes lane-ordered signal bytes. This is not an intermediate RGB888
   expansion in the active stock-runtime path.
5. `vgapalettedcontroller.cpp::decorateScanLinePixels` draws hardware sprites.
   RGBA8888/RGBA2222 sprite branches write or XOR final RGB222 signals; they need
   not be limited to the base framebuffer palette. Native-copy-only output would
   omit these overlays. Cursor representation must be traced/tested for each
   supported cursor type rather than assumed to be in the base pixels.
6. `stock_scanline.hpp::normalizeRow` removes signal bits and normalizes lane
   order (`x ^ 2`, or its selected helper), writing contiguous RGB222 bytes.
7. Immutable leased snapshot segments reach
   `network/wired_network_service.cpp` WebSocket send path. It compresses only
   RGB222, tightly packed rows, `n == width*height`, **n <= 196608**, valid scratch,
   and requested RLE2. Scratch capacity is 196622 bytes. It sends EVR1 only if
   encoded size is smaller; otherwise retains raw EVF1. Compression occurs
   outside the graphics lock. Do not remove that lifetime/ownership separation.
8. Served `frame_protocol.js` recognizes EVR1, enforces the same pixel limit,
   expands RLE2 to ordinary EVF1 RGB222. `webgl2_presenter.js` uploads R8 pixels
   and expands RGB222 in its shader. There is no indexed 4-bit/1-bit wire format.
   Browser credit delay is now 1000/60, unchanged by this audit.

## Payload budgets (not measured compression)

| Surface | Raw RGB222 bytes | Native packed bytes | Consequence |
|---|---:|---:|---|
| 640×480, 16 colours / mode 0 | 307,200 | 153,600 | RLE2 ineligible in installed implementation |
| 640×480, 2 colours / mode 2 | 307,200 | 38,400 | Same RLE2 resolution exclusion |
| 512×384, 64 colours / mode 20 | 196,608 | 196,608 native bytes | Eligible for RLE2; compression still conditional |

Headers/palette data excluded. At 60 complete frames/s, mode-0 raw RGB222 payload
alone is 18.432 MB/s, or 147.456 Mbit/s. Native 4-bit payload is 73.728 Mbit/s;
1-bit payload is 18.432 Mbit/s. These are arithmetic loads, not throughput claims.
Text RLE2 may be much smaller than either packed-raw alternative. Actual frame
sizes are needed for the final choice.

## Packed-output correctness requirements

1. Capture native pixels plus the corresponding palette/mode generation into
   owned immutable storage. Never transmit directly from a mutable live plane.
   Respect per-row pointers, native stride/bit order and scrolling layout.
2. A single palette is insufficient if Copper changes interpretation by scanline.
   First experiment should explicitly disallow Copper/active hardware sprites and
   unverified cursor effects, or take a conservative composed-output fallback.
3. Default/fallback must preserve the current final pixels; unsupported scenes
   must not silently lose sprite, cursor, XOR or palette effects.
4. Mode/palette changes while capturing require explicit snapshot consistency
   rules and rejection/retry, not an index plane paired with an unrelated palette.
   Avoid long frame-wide locks as an unmeasured shortcut.
5. Browser decoder/shader needs a separate negotiated format with dimensions,
   stride, bit order, palette and sequence identity; no silent reinterpretation
   of existing EVF1/EVR1. Old clients retain current supported output.
6. 64-colour and future 256-colour behavior remains unchanged. Do not abandon
   RLE2 as default because a restricted packed experiment is promising.

## Bounded proposed experiments — await Author choice

1. **Eligibility control:** same mode-0 text fixture, existing 60 fps credit flow;
   raise only the encoder scratch/eligibility and decoder bounds to cover the
   selected mode. Validate malformed-size bounds, allocation failure/raw fallback,
   exact decoded pixels and measured compressed sizes. Compare to preserved raw
   fallback baseline. This isolates compression availability without a new format.
2. **Native packed prototype:** task-local negotiated 4-bit/1-bit snapshots for
   controlled eligible text scenes, copied directly from native rows plus palette.
   Retain the existing composed path as oracle/fallback. Begin static text, then
   typing and scrolling. Explicitly exercise palette changes and fallback for
   sprites/Copper/cursor configurations. No general compositor rewrite.
3. **Matched measurements:** same scene, resolution, firmware except selected
   path, host/browser, and request cap. Record snapshot lock wait/hold, expansion
   or copy time, encode time, payload bytes, socket send time, decode/presentation
   cadence and injected-key latency distributions. Keep correctness captures
   separate from timing overhead. Compare packed raw to *working* RLE2 and raw.

## Audit limits

The hard limit and conversion path are source-confirmed. The installed decoder
was fetched read-only; this run did not attach a frame observer to count mode-0
EVF1 traffic. No performance attribution beyond arithmetic follows. Retained
build/source provenance is used; no claim that every line of the current main
checkout matches the installed candidate. Hardware voice is the only requested
completion action beyond documentation and ordinary bench CLI access.
