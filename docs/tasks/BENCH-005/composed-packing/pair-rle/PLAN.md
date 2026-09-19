# W10 — Pair-RLE experiment

## Executive summary

Author authorizes a goal task implementing two six-bit colours plus a literal flag and three-bit
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
uses bit15=1 for one literal pair (bits14:12 reserved zero), or bit15=0
with count-minus-two in bits14:12 for2–9 repetitions. First RGB222 pixel is
in11:6, second in5:0. Pair boundaries begin at raster offset0 and cross rows.
An odd final pixel is a single RGB222 byte after all pair tokens. Payload never
exceeds the original one-byte-per-pixel size; frame headers are unchanged.
Decoder rejects overrun, truncation, excess bytes and invalid odd-tail colour.
No transparency semantics. Explicit pair=1 negotiation protects older clients.

Author amendment before building: highest bit explicitly marks a literal pair.
The three remaining control bits encode runs2–9; no one-pair run token is needed.
No earlier pair-RLE firmware has been built or flashed.
