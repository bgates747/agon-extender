# P4 RLE2 benchmark table

## Executive summary

Final r05 build, median of three request medians, nine timed trials each.
Encode baseline is the first clean-sheet scalar encoder; percentage is change
in elapsed encode time (negative is faster). Decode compares scalar versus words.
No mainboard RLE2 timing baseline exists in this run.

| Pattern | File bytes | Scalar encode ms | Selected encode ms | Change | Scalar decode ms | Word decode ms |
|---|---:|---:|---:|---:|---:|---:|
| Noise | 196564 | 14.274 | 10.472 | -26.6% | 13.245 | 7.868 |
| Diagonal | 196622 | 14.234 | 9.974 | -29.9% | 13.189 | 7.673 |
| Tiles | 24590 | 5.601 | 5.610 | +0.2% | 3.588 | 4.107 |
| Solid | 3040 | 4.769 | 4.792 | +0.5% | 2.211 | 2.285 |

Earlier r04 word timings were lower for dense input (8.5–8.8ms). The final
r05 binary measures10.0–10.5ms for the same family; code layout/compiler
inlining is a possible explanation, not established. Report final-build numbers
rather than selecting the fastest measurement across binaries.

## Matched Nurples trial — r05, Wi-Fi receiver

| Output | Application mean interval ms | Application fps | Browser receive fps | Mean message bytes | Browser p95 interval ms |
|---|---:|---:|---:|---:|---:|
| off | 33.333 | 30.00 | — | — | — |
| raw | 78.266 | 12.78 | 4.73 | 196640 | 297.60 |
| rle | 33.333 | 30.00 | 29.18 | 37675 | 42.60 |

All three record1800 application cycles. RLE2 matched output-disabled pacing at
the MOS clock's8.333ms granularity. Raw versus RLE2 shares the same candidate and
client cap; one trial each is promising evidence, not broad performance acceptance.
The host receiver used Wi-Fi; do not present this as a wired receiver throughput
ceiling. Application cycle rate and browser snapshot receipt are separate metrics.
Initial no-output SAVE syntax was corrected after the game ended; its intact RAM
trace was recovered before loading another program. Later batches use explicit
hex prefixes. r06 only rounds browser credit delay upward; the game timings here
belong to r05, whose shortest observed request interval was32.9ms.
