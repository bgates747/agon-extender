# Browser pacing escalation plan

## Executive summary

Author authorizes the first candidate: change only the installed RLE2 client's
request cap from 30 to 60 fps, retain credit/backpressure behavior, fully deploy
and verify it, then hardware voice notify for human testing. No push/worker
redesign now. This is an experimental override of ADR-0020, not a new sustained
512×384 throughput guarantee.

1. [ ] W01 — Preserve current fullscreen r02 baseline and freeze this contract.
   Build a candidate from that preserved implementation with only 1000/30 changed
   to 1000/60 in browser credit pacing (plus build identity). RLE2 stays default.
2. [ ] W02 — Flash P4 only, independently verify, check served web assets and
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

Stop at W02 for this authorization. Preserve rollback artifacts, keep experiment
in this task silo, and do not deploy later stages merely because they are listed.
