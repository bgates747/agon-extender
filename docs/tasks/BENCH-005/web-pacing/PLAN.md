# Browser pacing escalation plan

## Executive summary

Author authorizes the first candidate: change only the installed RLE2 client's
request cap from 30 to 60 fps, retain credit/backpressure behavior, fully deploy
and verify it, then hardware voice notify for human testing. No push/worker
redesign now. This is an experimental override of ADR-0020, not a new sustained
512×384 throughput guarantee.

1. [x] W01 — Preserve current fullscreen r02 baseline and freeze this contract.
   Build a candidate from that preserved implementation with only 1000/30 changed
   to 1000/60 in browser credit pacing (plus build identity). RLE2 stays default.
2. [x] W02 — Flash P4 only, independently verify, check served web assets and
   keyboard admission; preserve startup and mainboard firmware. Leave a usable
   ExCom console for human typing at modes 20 and 0. Voice notify on hardware.
3. [ ] W03 — Author review: typing, cursor movement, scrolling, both resolutions,
   then games. Record acceptance or regression before production promotion.
4. [ ] W04 — If needed, matched quantitative tests at 30/60 requests per second
   for modes 20 and 0; separate rendering, encoding, delivery and presentation.
5. [ ] W05 — Only if evidence warrants and separately authorized: push-only P4
   output with bounded sends, newest pending frame selection, no custom browser
   frame acknowledgements. TCP still acknowledges/orders data; bound queued data.
6. [ ] W06 — Only if browser processing is shown material: persistent worker(s)
   for receive/decode, transferable buffers, newest completed frame presentation.
   No per-frame thread creation. Compare against the simpler configuration.
7. [ ] W07 — Explore pixel packing for low-colour modes. Compare packed raw
   4-bit indices (16 colours) and 1-bit indices (2 colours) against current
   full-frame RLE2 on identical text, scrolling and graphical scenes. At
   640×480 the packed pixel payloads are 153,600 and 38,400 bytes respectively,
   before headers/palette data. Packing consumes the spare bits used by RLE2
   tokens, so do not assume the existing codec applies unchanged. Evaluate any
   combined encoding separately. Verify whether final composed pixels remain
   representable by the mode palette, including sprites, palette changes and
   effects; define explicit fallback when they do not. Measure capture,
   packing/encoding, wire size, browser decode and presentation separately.
   Smaller payload alone does not establish lower capture cost or latency.
   Exploration only; implementation and experiment ordering await discussion.

Stop at W02 for this authorization. Preserve rollback artifacts, keep experiment
in this task silo, and do not deploy later stages merely because they are listed.

Candidate deployed and served assets verified. Hardware voice receipt passed;
ExCom console set to mode 20. Refresh browser before review. W03 remains pending.

Author subsequently reports mode 20 feels good and mode 0 remains choppy;
mode 8 was not retested. This is qualitative evidence, not full W03 acceptance.
At the Author's latest instruction, pause execution after recording W07: discuss
which exploration to try next before any further tests or implementation.

W07a read-only audit authorized and executed: [findings](../packed-output/RESULTS.md).
Installed RLE2 excludes mode 0 by pixel-count limit; reassess experiment order
before implementing native packed output. W07 implementation remains pending.
