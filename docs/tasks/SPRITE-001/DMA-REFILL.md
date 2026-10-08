# DMA-assisted strip refills — 2026-10-07

**The standalone loaded test now passes: 32 sprites, about60 DMA frames/s,
no recorded refill faults, and an Author-confirmed flicker-free picture.**
Espressif's existing DMA2D copier reduces background-copy cost; three rotating
SRAM buffers give the unchanged stock sprite painter enough preparation time
in this test. The deliberately late-refill control also stops output as intended.
This is not yet connected to the live VDP or Nurples. The next gate is safe scene
and bitmap ownership during scanout, followed by small integrated tests.

This completes SPR01-07A in [the work contract](../SPRITE-001.md).
[Portable evidence](DMA-REFILL.json) records exact source/build identities,
capture hashes, sampled counters and checks. Ignored raw evidence is retained
under `agents/sprite001/dma-refill/`. The [earlier CPU-copy experiment](ROLLING-SCANOUT.md)
remains an unchanged historical control.

## Comparison

All rows use848×480 output, a centered512×384 logical image, twelve40-row
strips, the same1/8/16/32 sprite progression, and separate-core256×336 PSRAM
scrolling traffic starting at frame3600. The displayed background stays static.
Ranked by worst observed refill duration, slowest first:

| Measurement | CPU copy, two buffers (baseline) | DMA copy, two buffers | DMA copy, three buffers |
|---|---:|---:|---:|
| Maximum refill, µs |2,195 |1,539 |1,524 |
| Maximum versus baseline |— |29.9% lower |30.6% lower |
| Nominal preparation window, µs |1,288 |1,288 |2,576 |
| Maximum as share of nominal window |170.4% |119.5% |59.2% |
| Conservative instrumentation threshold, µs |1,000 |1,000 |2,000 |
| Threshold exceedances in retained final sample |8,820 |5,588 |0 |
| Minimum observed ready lead at block callback, µs |Not instrumented |2 |1,012 |
| Scratch SRAM, bytes |203,520 |203,520 |305,280 |
| DMA cadence |About60/s |60.040/s |60.053/s |
| Conclusion |Too slow under load |Improved, still too late |Bounded loaded test passes |

Maxima and exceedance counts are cumulative since boot; they are observations,
not latency bounds or an equal-duration statistical benchmark. The earlier CPU
control has roughly60s loaded observation, the two-buffer DMA control55s, and
the three-buffer DMA capture60s. The last positive sample follows86,636 runtime
refills and3,616 scrolling iterations. Frame rates are approximately five-second
counter deltas, not independently measured HDMI monitor refresh.

The three-buffer sample reports maximum copy latency729µs and maximum sprite
composition864µs. These maxima need not coincide; do not sum them as a measured
refill. Copy latency includes submission/cache preparation and completion ISR
delay. Total refill includes both stages and cache handoffs. Cumulative means
include earlier lighter scenes and are retained in JSON, not presented as busy
scene averages. Timers use P4 `esp_timer` microseconds without external calibration.

The extra buffer increases available time rather than making composition faster.
Its305,280-byte allocation equals the earlier experiment's two60-row buffers.
The loaded sample retains273,383 free internal bytes in this standalone image;
that does not establish memory availability in full Extender firmware.

## Correctness and abort checks

1. Before scanout, the P4 compares all12 DMA-prepared strips with CPU-prepared
   background and sprite pixels: all pass. The unchanged stock sprite body and
   retained Nurples art also pass16 independent whole-frame host comparisons.
2. The positive loaded run records zero invalid blocks, underruns, callback
   sequence errors, cache errors, late generations, overlapping copy jobs or
   abort faults. The Author separately confirms: **“Stable, no flicker”**, in
   response to checking the left gray/checker boxes and moving sprites under load.
3. The two-buffer experiment shows why generation checks alone are inadequate:
   a slow completion ISR can delay the block ISR itself. Generation may appear
   ready while actual refill duration exceeds the nominal available interval.
   The final variant also checks elapsed refill duration independently.
4. The negative control injects a4,000µs hold at absolute strip tag500, after
   composition. Refill reaches4,288µs; the2,000µs guard latches exactly one fault.
   Frame count stops at41, block/refill count at498, and subsequent five-second
   samples report0 frames/s through21.392s. One underrun is recorded after output
   is disabled. This is the expected abort, not a positive timing result.
5. The abort can occur after the reader has begun using a late strip. It proves
   bounded experimental shutdown and no continuing frame rearm, not a guarantee
   of no transient bad pixels or a finished production recovery mechanism.

## Implementation and limits

The pinned ESP-IDF5.5.5 asynchronous framebuffer-copy helper is reused unchanged,
with one handle and one outstanding transaction because its transaction setup
uses shared static state. Allocation remains in task context. CPU/DMA cache
ownership is explicitly handed over before copying, sprite composition and
scanout. Fixed descriptor addresses rotate through three buffers; the final
refill occurs after DMA rearm. The SDK and official Agon references are unchanged.
The stock sprite scanline body is unchanged; no upstream bug fix is introduced.

Three ordinary setup corrections preceded the measured runs: an unflashed union
initializer correction, moving preflight after buffer allocation, and passing
the complete RGB color-space identifier to the copier. These were local fixture
errors, not hardware faults or memory exhaustion. Their build identities and
brief corrective notes remain local; repetitive panic captures were discarded.

No live graphics mutate the displayed background in this test. The P4 still
needs an ISR-safe scene snapshot, bitmap/list lifetime protection, sufficient
full-firmware SRAM, and mode/double-buffer retirement handling before integration.
Larger Nurples sprites, actual scrolling, input response and game-loop timing
remain untested on this path. The four-bit hardware block-count limit remains.
No application drawing budget or command dropping is added.

## Handback

Restoration verification is recorded in the portable evidence. The exact prior
full848 firmware, `rgb-001-r03-b2026-10-07-02-45-45Z`, was restored with segment
readback, then Agon reset after P4 services initialized. Input is ready/neutral
with no pending/held keys, SD service offline/idle and diagnostic windows closed.
No SD, startup, EMOS, game, asset or production selection changed. Native integration and a deterministic
hardware-sprite Nurples run remain the next separately reviewed step.
