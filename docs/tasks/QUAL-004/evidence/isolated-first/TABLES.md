# Whole-image comparison case table

## Executive summary

14 exact matches among 14 completed device comparisons. 1 other records have no valid paired comparison.

Every comparison includes all pixels; repeat captures validate stability. Elapsed seconds cover setup, loading, extraction and host control. They are **not** rendering-operation times or frame-rate measurements.

| Cohort | Case | Outcome | Different / total pixels | Procedure seconds |
|---|---|---|---:|---:|
| isolated02 | [BSP21_01](isolated02/BSP21_01/run.json) | pass | 0 / 196608 | 112.538 |
| isolated02 | [BSP21_02](isolated02/BSP21_02/run.json) | pass | 0 / 196608 | 112.638 |
| isolated02 | [BSP21_03](isolated02/BSP21_03/run.json) | pass | 0 / 196608 | 112.757 |
| isolated02 | [BSP21_04](isolated02/BSP21_04/run.json) | pass | 0 / 196608 | 112.759 |
| isolated02 | [BSP21_05](isolated02/BSP21_05/run.json) | pass | 0 / 196608 | 112.793 |
| isolated02 | [BSP21_06](isolated02/BSP21_06/run.json) | pass | 0 / 196608 | 112.419 |
| isolated02 | [BSP22_01](isolated02/BSP22_01/run.json) | pass | 0 / 196608 | 111.807 |
| isolated02 | [BSP22_02](isolated02/BSP22_02/run.json) | pass | 0 / 196608 | 111.747 |
| isolated02 | [BSP22_03](isolated02/BSP22_03/run.json) | pass | 0 / 196608 | 112.311 |
| isolated02 | [BSP22_04](isolated02/BSP22_04/run.json) | pass | 0 / 196608 | 112.285 |
| isolated02 | [BSP22_05](isolated02/BSP22_05/run.json) | pass | 0 / 196608 | 112.188 |
| isolated02 | [BSP25_01](isolated02/BSP25_01/run.json) | pass | 0 / 196608 | 111.942 |
| isolated02 | [BSP25_02](isolated02/BSP25_02/run.json) | pass | 0 / 196608 | 112.530 |
| isolated02 | [BSP25_03](isolated02/BSP25_03/run.json) | pass | 0 / 196608 | 112.785 |
| isolated02 | [BSP25_04](isolated02/BSP25_04/run.json) | invalid_mainboard_crash | Not comparable | 34.925 |

## Evidence interpretation

Mainboard `.serial.gz` contains checksummed composed scanout rows. P4 `.evf.gz` contains the last two fresh web snapshot generations. PNGs are lossless decoded views; magenta in a difference image marks every unequal pixel. `integrity.json` hashes all retained evidence. Fixture and firmware identities belong to the parent results document.
