# Whole-image comparison case table

## Executive summary

9 exact matches among 9 completed device comparisons. 1 other records have no valid paired comparison.

Every comparison includes all pixels; repeat captures validate stability. Elapsed seconds cover setup, loading, extraction and host control. They are **not** rendering-operation times or frame-rate measurements.

| Cohort | Case | Outcome | Different / total pixels | Procedure seconds |
|---|---|---|---:|---:|
| alpha-fenced01 | [BSP03_01](alpha-fenced01/BSP03_01/run.json) | pass | 0 / 196608 | 91.187 |
| full-fenced01 | [CAL](full-fenced01/CAL/run.json) | pass | 0 / 196608 | 88.720 |
| full-fenced01 | [EMPTY](full-fenced01/EMPTY/run.json) | pass | 0 / 196608 | 89.068 |
| full-fenced01 | [SHP20](full-fenced01/SHP20/run.json) | pass | 0 / 196608 | 88.794 |
| full-fenced01 | [SHP23](full-fenced01/SHP23/run.json) | pass | 0 / 196608 | 88.805 |
| full-fenced01 | [BSP03_01](full-fenced01/BSP03_01/run.json) | pass | 0 / 196608 | 91.328 |
| full-fenced01 | [BSP07_01](full-fenced01/BSP07_01/run.json) | pass | 0 / 196608 | 89.223 |
| full-fenced01 | [BSP07_02](full-fenced01/BSP07_02/run.json) | pass | 0 / 196608 | 89.286 |
| full-fenced01 | [BSP07_03](full-fenced01/BSP07_03/run.json) | pass | 0 / 196608 | 89.379 |
| full-fenced01 | [BSP21_01](full-fenced01/BSP21_01/run.json) | invalid_mainboard_crash | Not comparable | 152.172 |

## Evidence interpretation

Mainboard `.serial.gz` contains checksummed composed scanout rows. P4 `.evf.gz` contains the last two fresh web snapshot generations. PNGs are lossless decoded views; magenta in a difference image marks every unequal pixel. `integrity.json` hashes all retained evidence. Fixture and firmware identities belong to the parent results document.
