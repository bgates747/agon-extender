# Codec settings and PNG — staged comparison

## Executive summary

Author authorizes the Linux-to-browser comparison now, followed by a review stop.
Determine which lossless codecs/settings merit later P4 measurement; do not infer
P4 speed from host timings. The physical bench is unavailable to this task.
No physical network, serial, SD, firmware or reset operations, including alerts.
Use the accepted spoken emulator notification when the report is ready.

## Frozen contract

1. [x] C01 — Pin existing task-owned captured framebuffer and synthetic corpus,
   original szip lineage and present RLE2 baseline. Record exact bytes, geometry,
   source hashes, tool versions and host conditions. No third-party artwork.
2. [x] C02 — Implement a bounded Linux screening matrix: direct szip and SRLE2,
   orders0/3/4/6, small/medium/full-frame blocks; selected record sizes and optional
   incremental differencing. Test fast indexed PNG (levels1/3, selected filters,
   default/RLE/Huffman strategies), plus raw and RLE2 controls. Use identical raw
   frames. Record exact output, host encode time and size. Extend only task-owned
   codec adapters; keep original sorting/model source and licenses intact.
   Verify against original CLI where supported; explicitly document exclusions.
3. [x] C03 — Reuse the browser Worker/decoder and existing presenter boundaries.
   Add direct szip/settings support and browser-native indexed PNG decoding in
   this silo. Freeze a test-only transport envelope; do not repurpose production
   EVF1/EVR1/EVS1 meanings. Fail closed on invalid lengths/settings, bound memory,
   preserve raw fallback and isolate decode timeouts in a Worker.
4. [ ] C04 — Linux-to-browser exact-pixel and measured runs. Screen all settings
   natively, then test a representative bounded shortlist in real Chromium over
   loopback, including every codec family and host speed/size Pareto candidates.
   Warm up and repeat; report encode, bytes, browser decode, presentation and
   paced delivery separately. Test malformed input/recovery and mixed frames.
   Keep any failures and the exact tested shortlist. No host-to-P4 extrapolation.
5. [ ] C05 — Evaluate and record a proposed hardware shortlist with tabular results,
   percentage differences against RLE2 and explicit limitations. Commit discrete
   work/evidence, document reproduction, then emulator voice alert and STOP for
   Author review. No experimental push or production promotion.
6. [ ] C06 — FUTURE, NOT AUTHORIZED TO EXECUTE THIS TURN: after shortlist review and
   explicit bench release, measure P4-local encode/decode costs, then best candidates
   with identical startup-owned512×384 Nurples load and RLE2 controls. Judge delivered
   cadence, not just size. Restore baseline and notify using the then-agreed channel.

## Matrix and selection policy

Initial szip grid uses recordsize1 without incremental differencing across four
orders and three block sizes. A separate structural grid uses orders0/4, records
1/2/3/4/8, differencing on/off, full-frame blocks, on both raw and RLE2 inputs.
Deduplicate overlaps. PNG uses8-bit palette indices, exact64-colour palette,
filters None/Sub/Up, zlib levels1/3 and default/RLE/Huffman-only strategies.
Native passes use one warmup and three measured invocations. Browser runs use
at least eight exact frames per selected variant/case, then30Hz-paced mixed
replays for finalists. Keep controls plus representation from direct szip, SRLE2
and PNG; a Linux speed loser may still deserve P4 investigation. Broadening the
matrix requires a prominently labelled agent-assigned amendment with evidence.

## Précis and boundaries

Prior physical assessment: ../srle2/hardware/RESULTS.md. Prior reusable browser
implementation: ../srle2/web/README.md and PROTOCOL.md. Historical comparisons:
agon-utils tests/szip_benchmarks.txt (2025-02-25) and tests/images/report_*.csv
(2025-02-26); extender-legacy agm/szip-results.md (2026-08-16). These measured
mainly sizes/decompression, not current P4 live encoding across settings.

Szip record reordering gathers bytes by position modulo recordsize; incremental
encoding differences the resulting byte sequence, not successive video frames.
RLE2 input is variable-length tokens rather than fixed pixel records. Direct
szip on raw pixels must therefore be evaluated independently. Order4 has a
specialized transform; do not assume lower order means faster. Original szip
CLI block sizing rounds100kB units to32KiB boundaries; record actual sizes.

PNG uses indexed pixels plus DEFLATE; fast settings and browser-native decoding
are hypotheses to measure. Official references: https://www.zlib.net/manual.html
and https://www.w3.org/TR/png/ . PNG palette conversion must be exact; no RGB
expansion on the encoding side and no lossy colour approximation. Browser canvas
readback belongs to correctness checking, not the ordinary presentation timing.

## Decisions

D01 — Author approved staged Linux/browser work with a review gate before P4.
D02 — Bench remains untouched; emulator spoken cue only.
D03 — Production codec negotiation remains unchanged. This is an experimental
comparison protocol and proposed shortlist, not an accepted product choice.

## Execution notes

C01 corpus integrity and build/source identities are in `evidence/`. Generated
code, Wasm, corpus payloads and verbose samples remain in ignored `agents/`;
tracked results retain hashes and compact tables. Native order0 encoding of a
solid full-size frame is unexpectedly expensive (seconds); retain the result
rather than excluding it as an outlier. This screen does not change that algorithm.

The browser checks palette indices exactly. PNG checks native decoded RGB against
the exact64-colour palette, with readback cost separated from decode and absent
from the paced replay. The PNG renderer uploads ImageBitmap to the retained
WebGL2 shader path. Its submission time is not completed GPU/monitor display time.

PNG implementation follows W3C PNG third edition IHDR/PLTE/IDAT/filter definitions.
Zlib manual `deflateInit2` defines selected strategies: default0, Huffman-only2,
RLE3. These are compression tradeoffs, not image-quality settings. No interframe
deltas are used in this screen; szip incremental mode differences bytes within
one input stream.

## Agent-assigned amendment A01 — pathological native runtime

Native order0 on the solid case measured7–9 seconds per encode for some
structural settings; stripes with128KiB blocks measured17.03 seconds. Continuing the full matrix without a bound would waste the screening
budget. Each remaining variant now runs in a disposable native process with
a5-second wall limit for its four encodes and verification combined. A timeout
is an unqualified/performance-screen exclusion, not evidence of wrong pixels.
Previously completed timings and correctness remain retained. Only variants
passing every corpus case enter the browser shortlist; excluded order0 evidence
remains in the full native results. This amendment is agent-assigned, not a
separately Author-approved change. The codec source/algorithm remains unchanged.

C03 preflight passed on colours, tiny and solid images across10 selected
variants, followed by paced replays. Invalid envelopes, unknown codec, corrupt
CmpS/PNG headers and an intentionally nonresponsive Worker were rejected;
valid raw frames decoded after each rejection. This is preflight evidence;
C04 owns the complete corpus and final measured shortlist. Python3.14 changed
the multiprocessing default; the host-only timeout harness explicitly selects
Linux fork so inherited ctypes state remains local to each disposable child.

C02 complete:960 combinations,924 exact passes,36 screening timeouts.
All completed captured-scene szip encodings matched the original CLI. No pixel
mismatch was observed. The resumed sweep took302.6 seconds, excluding its
earlier unbounded segment. Initial samples used screen.py at68f739e; resumed
samples used its explicit-fork revision atb70bb6c. The run manifest recorded
HEAD at completion, not execution start; those source revisions are the precise
identities. Future runs now capture source commit/hash at invocation.
