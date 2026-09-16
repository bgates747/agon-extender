## Comparative performance

Historical stock mainboard baseline:59.927 completions/s, mean16.687 ms, p9517.063 ms, max31.816 ms. Positive percentage means worse spacing tail; percentage =100×(P4 p95/17.063−1). Ranked worst p95 first.

| Control | Completion/s | Mean ms | p95 ms | Max ms | p95 vs mainboard | Enqueue p95 ms |
|---|---:|---:|---:|---:|---:|---:|
| p02-discard6 | 52.551 | 19.029 | 45.509 | 54.228 | +166.71% | 44.339 |
| p02-normal1 | 60.055 | 16.651 | 29.238 | 37.727 | +71.35% | 29.830 |
| p02-prebuilt5 | 60.057 | 16.651 | 25.026 | 33.624 | +46.67% | 23.503 |
| p02-prebuilt7 | 60.058 | 16.651 | 21.428 | 33.171 | +25.58% | 21.820 |
| p02-discard3 | 60.053 | 16.652 | 17.318 | 21.335 | +1.49% | 17.429 |
| p02-off2 | 60.053 | 16.652 | 17.049 | 21.072 | -0.08% | 17.326 |

Operation scopes below are per full512×384 frame, not per bitmap draw. Means are elapsed wall time, not exclusive CPU time. These are different achieved workloads, not a matched-rate efficiency contest.

| Control | Native compositions | Compose mean ms | Native compositions/s | Send calls | Send mean ms | Sends/s | EVF bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| p02-off2 | 0 | — | 0.000 | 0 | — | 0.000 | 0 |
| p02-discard3 | 2397 | 6.429 | 59.995 | 0 | — | 0.000 | 0 |
| p02-prebuilt5 | 0 | — | 0.000 | 1133 | 17.342 | 28.357 | 222793120 |
| p02-normal1 | 1093 | 13.623 | 27.360 | 1093 | 17.702 | 27.360 | 214927520 |
| p02-discard6 | 2472 | 13.537 | 53.913 | 0 | — | 0.000 | 0 |
| p02-prebuilt7 | 0 | — | 0.000 | 1166 | 17.082 | 29.184 | 229282240 |

Prebuilt counters measure slot preparation/cache reuse, not native composition; full-size bytes are still sent. Raw per-phase counts, units, means and duration are retained in `results/*-output.json`. All accepted operation blocks report zero failures, invalid state and pending operations.
