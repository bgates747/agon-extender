# W10 — Pair-RLE experiment

## Executive summary

Author authorizes a goal task implementing two six-bit colours plus a four-bit
repeat count in each 16-bit word. Preserve previous candidates and compare only
Nurples on hardware, then send a hardware voice notification. No game, mainboard
firmware, compositor, scheduler or sprite changes.

1. [ ] Freeze wire layout, preserve rollback, implement bounded C++ encoder and
   browser decoder. Test exact round trips, run boundaries, odd tails, invalid
   tokens and worst-case size. Existing formats remain negotiated independently.
2. [ ] Build/deploy experimental P4 firmware and run matched deterministic
   Nurples trials: prior selection, pair-only and automatic selection. Record
   wire sizes/formats, application cycles and browser submissions separately.
3. [ ] Evaluate whether the new path merits default selection; retain useful
   code/evidence even if slower. Restore startup, hardware notify, leave Nurples
   available for subjective review, commit discrete work without unrelated dirt.

EVQ1 retains the existing32-byte frame header. Each little-endian16-bit token
contains count-minus-one in bits15:12, first RGB222 pixel in11:6, second in5:0.
Repeat the pair1–16 times. Pair boundaries begin at raster offset0 and cross rows.
An odd final pixel is a single RGB222 byte after all pair tokens. Payload never
exceeds the original one-byte-per-pixel size; frame headers are unchanged.
Decoder rejects overrun, truncation, excess bytes and invalid odd-tail colour.
No transparency semantics. Explicit pair=1 negotiation protects older clients.
