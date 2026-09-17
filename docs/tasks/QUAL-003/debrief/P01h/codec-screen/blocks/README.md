# Order4 SRLE2 block-size screen

## Executive summary

Complete: keep full-input blocks. Smaller blocks generally made encoding slower
and output larger. All native/browser exact checks passed after isolating
multi-block scratch reclamation in the test adapter. See [RESULTS.md](RESULTS.md)
and [TABLES.md](TABLES.md). Bench untouched; no production changes.

## Frozen contract

1. [x] B01 — Reuse pinned codec/corpus. Test512,1024,2048,4096,8192,16384,
   32768,65536,131072 bytes and full input, with raw/RLE2 controls. Powers of two
   span sub-kilobyte overhead through cache-sized working sets to existing limits.
   Use all12 previous cases. Native exact decode plus original CLI decode checks;
   original CLI cannot request these small blocks, but its decoder must accept them.
2. [x] B02 — Measure20 paired encodes against full-block order4 on captured scene,
   synthetic sprites and noise; alternate order and discard warmups. Browser-test
   every block size:8 exact frames/case,90 mixed frames at30Hz ceiling, malformed
   input/recovery and raw fallback. Reuse existing isolated EVC1/Worker/presenter.
3. [ ] B03 — Report bytes and ms, percentage differences to full-block order4,
   exceptions and practical shortlist. Freeze results in commits, emulator voice
   notify, stop. No bench/firmware/production changes or push.

A tiny-block tail may use the original stored-block representation; preserve it.
Retain failures rather than silently excluding sizes. Five-second native worker
screening guard remains; classify timeouts separately from incorrect pixels.

## Agent-assigned adaptation A01

Initial small-block tests hit adapter allocation status3: the12MiB guard counted
lifetime allocation traffic, although each block's model had already been freed.
The isolated r02 build tracks each slot's size and subtracts it on free, keeping
the12MiB live-allocation ceiling,4096 live-slot ceiling and existing decode
timeouts. Original sorting/model algorithms remain unchanged. This is test-only;
production port still needs review before adopting multi-block settings. Retain
the initial status3 evidence. A fixture mistake also tried feeding raw/RLE2
controls to the szip CLI; corrected to check only SRLE2 streams.

A01 refinement: live accounting alone did not resolve status3. The inherited
order4 sorter has commented-out frees; its task port intentionally sweeps those
allocations at end-of-call. Multiple small blocks retain one scratch set per
block until then. Isolated r03 now sweeps tracked scratch and resets sort-cache
pointers at each complete block, for encode and decode. No algorithm or wire
format changes. Both r01/r02 failures remain evidence; r03 must pass original
CLI decoding and browser checks before timings are interpreted.

B01 complete:144/144 native combinations passed, including original CLI decode
of all120 SRLE2 streams. The r03 build retains the same codec algorithms while
reclaiming block-local scratch. All full-block comparisons below use r03 as well.

B02 complete:1,152 browser exact frames,1,080 paced frames and24 mixed
codec/raw exact fallback frames passed, as did invalid-input/timeout recovery.
Paired timing confirmed36 case/settings groups with20 measured pairs each.
No physical bench access occurred. See TABLES.md and evidence/.
