# Order4 SRLE2 block-size screen

## Executive summary

Author authorizes a bench-free block-size comparison and emulator spoken notice.
Keep order4, recordsize1, differencing off; vary only szip block size. No P4 access.
Sizes apply to the RLE2 stream, not raw framebuffer rows. Host results cannot
establish P4 cache behavior or a shipping choice.

## Frozen contract

1. [ ] B01 — Reuse pinned codec/corpus. Test512,1024,2048,4096,8192,16384,
   32768,65536,131072 bytes and full input, with raw/RLE2 controls. Powers of two
   span sub-kilobyte overhead through cache-sized working sets to existing limits.
   Use all12 previous cases. Native exact decode plus original CLI decode checks;
   original CLI cannot request these small blocks, but its decoder must accept them.
2. [ ] B02 — Measure20 paired encodes against full-block order4 on captured scene,
   synthetic sprites and noise; alternate order and discard warmups. Browser-test
   every block size:8 exact frames/case,90 mixed frames at30Hz ceiling, malformed
   input/recovery and raw fallback. Reuse existing isolated EVC1/Worker/presenter.
3. [ ] B03 — Report bytes and ms, percentage differences to full-block order4,
   exceptions and practical shortlist. Freeze results in commits, emulator voice
   notify, stop. No bench/firmware/production changes or push.

A tiny-block tail may use the original stored-block representation; preserve it.
Retain failures rather than silently excluding sizes. Five-second native worker
screening guard remains; classify timeouts separately from incorrect pixels.
