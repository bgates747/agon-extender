# W09 — Six-bit final-frame packing and Nurples review

## Executive summary

Author authorizes lossless packing for all 64-colour modes, preserving the W08
candidate and evidence. Add direct RGB222 packing (four pixels in three bytes),
retain lower-depth packing and RLE2 selection, test only Nurples on hardware,
and finish with the accepted hardware voice cue and an interactive review game.
No mainboard firmware, production game, scheduler or pacing changes.

1. [ ] Preserve W08 artifacts; implement separately negotiated six-bit packing
   and browser decoding, including odd pixel counts and malformed input checks.
2. [ ] Build/deploy the P4 candidate with rollback intact. Run matched Nurples
   output trials, recording actual wire formats, bytes, fps and decoding costs.
   Host codec tests may cover every geometry; no new all-mode hardware sweep.
3. [ ] Record results and limits, restore startup, hardware voice notify and
   leave the existing test Nurples ready for subjective review. Commit only
   this task's work; no push or unrelated changes.

Use the same completed RGB222 snapshot; no transparency, sprite or Copper
reinterpretation. Official Screen-Modes.md reviewed; no VDU contract changes.
The experimental extension requires packed=2 so older packed=1 clients cannot
receive an unsupported six-bit packet. Automatic selection retains RLE2 where
smaller; packed-only is a diagnostic control, not a promised universal speedup.
