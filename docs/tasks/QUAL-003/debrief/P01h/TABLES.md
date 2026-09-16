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
