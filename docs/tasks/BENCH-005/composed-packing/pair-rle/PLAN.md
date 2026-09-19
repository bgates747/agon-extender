# W10 — Pair-RLE experiment

## Executive summary

Author authorizes a goal task implementing two six-bit colours plus a four-bit
repeat count in each 16-bit word. Preserve previous candidates and compare only
Nurples on hardware, then send a hardware voice notification. No game, mainboard
firmware, compositor, scheduler or sprite changes.

1. [x] Freeze wire layout, preserve rollback, implement bounded C++ encoder and
   browser decoder. Test exact round trips, run boundaries, odd tails, invalid
   tokens and worst-case size. Existing formats remain negotiated independently.
2. [x] Build/deploy experimental P4 firmware and run matched deterministic
   Nurples trials: prior selection, pair-only and automatic selection. Record
   wire sizes/formats, application cycles and browser submissions separately.
3. [ ] Evaluate whether the new path merits default selection; retain useful
   code/evidence even if slower. Restore startup, hardware notify, leave Nurples
   available for subjective review, commit discrete work without unrelated dirt.

EVQ1 retains the existing32-byte frame header. Each little-endian16-bit token
contains count-minus-one in bits15:12, first RGB222 pixel in11:6, second
in5:0. Repeat the pair1–16 times. Pair boundaries begin at raster offset0 and cross rows.
An odd final pixel is a single RGB222 byte after all pair tokens. Payload never
exceeds the original one-byte-per-pixel size; frame headers are unchanged.
Decoder rejects overrun, truncation, excess bytes and invalid odd-tail colour.
No transparency semantics. Explicit pair=1 negotiation protects older clients.

Author amendment before building: highest bit explicitly marks a literal pair.
The three remaining control bits encode runs2–9; no one-pair run token is needed.
No earlier pair-RLE firmware has been built or flashed.

Author subsequently accepted returning to the original four-bit count ("as you
were"). The literal-flag variation was host-tested only, never built/flashed.
Current EVQ1 uses count-minus-one; zero therefore means one literal pair.

Final clarification was explicit: "do your way"; proceed with the four-bit count.
64 host round trips and8 malformed cases passed, including maximum runs, odd
tails and exact worst-case size. First Escape did not reach MOS; a normal reset
returned keyboard readiness, but the following SD admission still failed.
The requested screen clear was emitted, not independently confirmed. No SD
mutation occurred. Recheck admission after the P4 deployment before trials.

After verified P4 deployment, SD admission succeeded and the unchanged Nurples
fixture transfer began. The earlier admission failure did not recur at this gate.

Measured decision: pair-only packets averaged52KB vs39KB RLE2; automatic
selected RLE2 throughout the measured Nurples window. Retain pair=1 support
but restore the prior browser default without pair selection. Preserve the
experimental image and results, rebuild only this default change, verify served
assets and run a short Nurples default-client smoke before review.
