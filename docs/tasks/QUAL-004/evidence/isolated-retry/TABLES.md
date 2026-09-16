# Whole-image comparison case table

## Executive summary

2 exact matches among 2 completed device comparisons. 1 other records have no valid paired comparison.

Every comparison includes all pixels; repeat captures validate stability. Elapsed seconds cover setup, loading, extraction and host control. They are **not** rendering-operation times or frame-rate measurements.

| Cohort | Case | Outcome | Different / total pixels | Procedure seconds |
|---|---|---|---:|---:|
| isolated03 | [BSP25_04](isolated03/BSP25_04/run.json) | pass | 0 / 196608 | 111.603 |
| isolated03 | [BSP25_05](isolated03/BSP25_05/run.json) | pass | 0 / 196608 | 111.708 |
| isolated03 | [BSP26_01](isolated03/BSP26_01/run.json) | invalid_mainboard_crash | Not comparable | 173.281 |

## Evidence interpretation

Mainboard `.serial.gz` contains checksummed composed scanout rows. P4 `.evf.gz` contains the last two fresh web snapshot generations. PNGs are lossless decoded views; magenta in a difference image marks every unequal pixel. `integrity.json` hashes all retained evidence. Fixture and firmware identities belong to the parent results document.
