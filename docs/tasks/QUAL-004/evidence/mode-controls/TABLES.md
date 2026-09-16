# Whole-image comparison case table

## Executive summary

3 exact matches among 3 completed device comparisons. 2 other records have no valid paired comparison.

Every comparison includes all pixels; repeat captures validate stability. Elapsed seconds cover setup, loading, extraction and host control. They are **not** rendering-operation times or frame-rate measurements.

| Cohort | Case | Outcome | Different / total pixels | Procedure seconds |
|---|---|---|---:|---:|
| mode9-run01 | [PAL16](mode9-run01/PAL16/run.json) | pass | 0 / 76800 | 88.320 |
| mode9-run01 | [COP16_SETUP](mode9-run01/COP16_SETUP/run.json) | pass | 0 / 76800 | 89.320 |
| mode9-run02 | [COP16_EDIT](mode9-run02/COP16_EDIT/run.json) | pass | 0 / 76800 | 89.229 |
| mode9-run01 | [COP16_EDIT](mode9-run01/COP16_EDIT/run.json) | invalid_p4_restart | Not comparable | 13.363 |
| mode9-run02 | [COP16_REPLACE](mode9-run02/COP16_REPLACE/run.json) | invalid_p4_restart_during_setup | Not comparable | 283.841 |

## Evidence interpretation

Mainboard `.serial.gz` contains checksummed composed scanout rows. P4 `.evf.gz` contains the last two fresh web snapshot generations. PNGs are lossless decoded views; magenta in a difference image marks every unequal pixel. `integrity.json` hashes all retained evidence. Fixture and firmware identities belong to the parent results document.
