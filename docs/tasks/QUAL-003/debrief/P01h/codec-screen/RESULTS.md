# Codec settings and indexed PNG — Linux/browser assessment

## Executive summary

**The current SRLE2 settings remain a strong choice; this screen found worthwhile
P4 candidates, not a proven replacement. Test SRLE2 order4 and fast indexed PNG
next, against the existing RLE2 and SRLE2 order3 controls.** Record reordering and
incremental differencing did not produce a consistent win worth prioritizing.
Direct szip was generally a worse tradeoff than compressing the RLE2 stream.

The captured512×384 sprite scene gives this comparison. Encode times are Linux
medians from20 paired samples; bytes include codec headers, exclude the common
32-byte test envelope. RLE2 is the size baseline. These are **not P4 timings**.

| Codec/settings | Bytes | Size vs RLE2 | Linux encode ms | Encode vs paired RLE2 |
|---|---:|---:|---:|---:|
| RLE2 control | 7,038 | 0% | 0.086 | 0% |
| PNG level1/default/None | 2,553 | −63.7% | 0.307 | +254.4% |
| PNG level3/default/None | 2,423 | −65.6% | 0.337 | +292.6% |
| Direct szip order4/record1 | 1,310 | −81.4% | 0.581 | +566.7% |
| SRLE2 order4/record1 | 937 | −86.7% | 0.156 | +83.9% |
| SRLE2 order3/record1 control | 919 | −86.9% | 0.164 | +91.0% |

Order4 encoded this scene about5% faster than order3 with2% more bytes. On the
synthetic sprite case it was about10% faster and17% smaller. These small host
advantages justify an embedded comparison, not a firmware promotion.

PNG has a different strength: browser-native decoding and lower cost on noisy
input. On deterministic noise, Linux PNG level3 took2.849ms against SRLE2 order3's
10.772ms, with152,475 versus151,696 bytes. On the mixed full-size browser replay,
PNG level3's mean decode-wall cost was1.726ms versus5.474ms for SRLE2 order3.
That includes the different native/Worker boundaries; it does not measure P4
encoding or prove an Ethernet/frame-rate gain.

The30Hz-capped loopback replays delivered27.41–28.52 submitted frames/s across all
14 variants; RLE2 delivered27.92. The small differences around this imposed cap
are not evidence of a useful throughput winner. **Do not raise the existing web
frame-rate guarantee on this evidence.** The producer sent pre-encoded bytes;
there was no game, embedded renderer or physical network in these measurements.

## Qualification result and scope

1. Native matrix:80 settings ×12 images =960 combinations.924 completed exact
   checks;36 exceeded the documented screening wall limit. No completed case
   had a pixel mismatch. Timeouts are unqualified cases, not codec-corruption
   findings. See the full [native evidence](evidence/native.csv).
2. Every completed szip setting on the captured scene matched the original
   unmodified CLI encoder byte for byte. This checks the generalized adapter
   against original source, not merely its own inverse.
3. Browser shortlist:14 variants,1,344 exact frame checks,1,260 paced frames,
   and24 mixed codec/raw-fallback exact frames all passed. The native PNG path
   preserved every RGB palette value; other paths preserved every pixel index.
4. Short/truncated envelopes, unsupported codec, corrupt CmpS and PNG headers,
   plus an intentionally nonresponsive Worker were rejected. Valid raw frames
   recovered afterward. Header bounds limit geometry/payload before admission;
   PNG IHDR geometry is checked before native image allocation.
5. Corpus:11 deterministic synthetic cases plus one retained task-owned physical
   sprite/bitmap capture. It includes scrolling patterns, sprite patterns, all
   colours, tiny/stored data and noise. **This is not a Nurples or Rally gameplay
   benchmark.** No new hardware pixels were captured in this phase.
6. Physical bench untouched: no network/serial/SD access, flash or reset. No
   mainboard VDP, EMOS, P4 firmware or production browser code changed. All new
   code is in this task silo; production negotiation is unchanged.

## What the settings actually did

1. **Order0 is not automatically fast.** Some solid/patterned inputs took seconds
   per encode: the initial128KiB-block stripes result was17.03 seconds. The
   specialized order4 transform avoids that particular observed cost. This is
   empirical screening evidence, not a diagnosis or modification of upstream
   szip's algorithms. Remaining expensive cases were bounded by amendment A01.
2. **Record size is byte reordering, not pixel depth.** The original reorder
   routine gathers positions modulo record size. Incremental mode differences
   that reordered byte stream within one frame; it is not temporal frame delta.
   RLE2 tokens have variable lengths, so assumed multi-byte records are not
   naturally aligned to its pixels. Some combinations helped individual cases,
   but none displaced order3/4 record1 in the proposed first hardware shortlist.
3. **Block sizing needs context.** The captured RLE2 file is7,038 bytes, so both
   32KiB and full-frame block settings form one identical szip block. Their919-byte
   outputs are identical; initial timing differences were noise. Larger/noisier
   inputs exercise actual multiple blocks. The CLI rounds its100kB option units
   to32KiB boundaries; the matrix records actual32768/131072/4259840-byte limits.
4. **PNG is not automatically the smallest or fastest encoder.** Level3/default/
   None was a useful size/speed compromise here. Level1 is retained as an embedded
   speed control. The RLE/Huffman strategies and fixed Sub/Up filters had some
   case-specific wins, but no compelling broad advantage for the first P4 pass.
   This is an8-bit indexed PNG with a64-entry exact palette, not RGB expansion
   on the encoder and not lossy image conversion.
5. **Keep raw fallback.** Codec/header overhead can exceed raw size, especially
   on tiny frames. The replay switches to raw when the candidate message would
   not be smaller, and verifies that mixed stream. Worst-case CPU remains an
   independent problem: discovering poor compression after encoding does not
   recover the time already spent. Adaptive encoding admission needs its own
   measured decision later, not a speculative change in this screen.

## Measurement review and limitations

1. The initial three-sample native sweep is suitable for broad screening, but
   some sub-millisecond rankings moved substantially. A subsequent confirmation
   alternated candidate/RLE2 order, discarded two warmup pairs and took medians
   of20 pairs across42 selected case/settings groups. Every candidate payload
   still matched the original sweep. The executive table and main table use
   those paired results; original samples remain retained rather than rewritten.
2. Ordinary Linux desktop, no CPU/frequency isolation. Browser preflight overlapped
   part of the initial native sweep; the final browser run and paired timing
   confirmation were sequential. Reported decimal places are units, not precision
   guarantees. No conversion factor from x86 timing to RISC-V/P4 is justified.
3. Chromium151.0.7922.34 runs headlessly with WebGL2/SwiftShader. PNG decode uses
   createImageBitmap in a Worker; ordinary presentation uploads its ImageBitmap
   without verification readback. Exact checks use separate RGBA readback and
   palette comparison. CPU WebGL submission does not prove GPU completion or
   physical monitor presentation. No video-refresh/interpolation claim follows.
4. The server has one outstanding frame credit and a30Hz ceiling, and the client
   schedules drawing through requestAnimationFrame. Both browser scheduling and
   software rendering contribute to the observed roughly28fps cadence. This is
   an apples-to-apples host pipeline comparison, not a link saturation test.
5. Wasm has a fixed64MiB heap and2MiB stack for this host experiment. Those are not
   approved P4 allocations. Future embedded measurements must include stack,
   internal RAM/PSRAM high-water, allocation failures and simultaneous rendering.
6. Native resume phase:302.6 seconds; final browser:71.7 seconds. Paired confirmation
   duration is recorded in evidence/paired.json. The initial unbounded native
   portion and build/preparation are additional;302.6 seconds is not total task
   elapsed time. This guard and measured durations guide future run estimates.
7. Full private payloads/Wasm/logs/browser samples remain in ignored agent output;
   compact native/browser evidence, source hashes, corpus identities and paired
   samples are tracked. Reproduction is in [REPRODUCE.md](REPRODUCE.md).

## Proposed P4 shortlist — review gate, not authorization to run

| Priority | P4 experiment | Why |
|---|---|---|
| Controls | Existing RLE2 and SRLE2 order3/record1/full block | Re-establish matched embedded costs and output cadence |
| First | SRLE2 order4/record1/no incremental/full block | Small source-setting change with promising host improvements |
| Second | Indexed PNG level3/default/None | Native browser decoder; competitive noise encoding; different cost distribution |
| Optional paired control | Indexed PNG level1/default/None | Determine whether reduced search helps the embedded encoder |

After Author review and bench release: measure P4-local encode/decode/memory first,
then compare only promising variants under identical fixed-mode live rendering
and browser output, retaining RLE2 controls. Do not change mainboard VDP or EMOS
for this experiment. Preserve exact pixels and raw fallback. Embedded results,
not this host shortlist, decide whether a codec should ship.

See [TABLES.md](TABLES.md) for all14 variants and explicit percentage comparisons.
C06 remains pending. No production promotion or experimental push occurred.
