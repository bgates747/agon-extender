# Repeated Linux/browser comparisons

Exact pixels passed on 12 fixtures × 3 formats × 2 repetitions. First two frames per run are excluded from steady means. Ranked by worst SRLE2 decode cost.

| Fixture | Raw bytes | RLE2 bytes | SRLE2 bytes | SRLE2 vs RLE2 bytes | Raw decode/parse ms | RLE2 decode/parse ms | SRLE2 decode/parse ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| noise | 196640 | 196611 | 151736 | -22.8% | 0.014 | 0.531 | 18.808 |
| scroll2 | 196640 | 49294 | 570 | -98.8% | 0.025 | 0.736 | 1.611 |
| scroll0 | 196640 | 49198 | 409 | -99.2% | 0.022 | 0.836 | 1.403 |
| scroll1 | 196640 | 49246 | 531 | -98.9% | 0.019 | 0.811 | 1.383 |
| stripes | 196640 | 24622 | 185 | -99.2% | 0.017 | 0.572 | 0.956 |
| sprites1 | 196640 | 15054 | 653 | -95.7% | 0.017 | 0.322 | 0.939 |
| sprites2 | 196640 | 15054 | 651 | -95.7% | 0.019 | 0.364 | 0.925 |
| sprites0 | 196640 | 15063 | 694 | -95.4% | 0.025 | 0.356 | 0.856 |
| retained-sprites | 196640 | 7070 | 959 | -86.4% | 0.019 | 0.219 | 0.772 |
| solid | 196640 | 3072 | 95 | -96.9% | 0.019 | 0.183 | 0.561 |
| tiny | 33 | 47 | 86 | +83.0% | 0.011 | 0.031 | 0.408 |
| colours | 96 | 110 | 151 | +37.3% | 0.028 | 0.036 | 0.389 |

## SRLE2 stage detail

| Fixture | Szip ms | RLE2 expansion ms | Final parse ms | Presenter submission ms | Receive interval ms |
|---|---:|---:|---:|---:|---:|
| noise | 18.214 | 0.394 | 0.031 | 0.144 | 39.74 |
| scroll2 | 0.836 | 0.686 | 0.006 | 0.122 | 34.19 |
| scroll0 | 0.831 | 0.444 | 0.022 | 0.186 | 34.24 |
| scroll1 | 0.767 | 0.492 | 0.019 | 0.181 | 34.26 |
| stripes | 0.467 | 0.353 | 0.017 | 0.194 | 34.39 |
| sprites1 | 0.539 | 0.300 | 0.014 | 0.164 | 34.24 |
| sprites2 | 0.567 | 0.283 | 0.017 | 0.133 | 34.25 |
| sprites0 | 0.478 | 0.267 | 0.014 | 0.153 | 34.25 |
| retained-sprites | 0.506 | 0.161 | 0.014 | 0.158 | 34.26 |
| solid | 0.319 | 0.169 | 0.014 | 0.158 | 34.30 |
| tiny | 0.297 | 0.025 | 0.033 | 0.100 | 34.39 |
| colours | 0.292 | 0.017 | 0.017 | 0.103 | 34.27 |

All timing is headless Chromium on Linux over localhost. It measures neither P4 encode/render/transport cost nor physical display refresh. Frames are credit paced at at most30Hz. GPU palette conversion is part of presenter submission; submission does not wait for GPU completion. Fixed WebAssembly memory reservation is64MiB, not measured live allocation high-water. Original codec invocation allocation budget is12MiB cumulative. First-frame module initialization costs are retained in comparison.json, separately from steady means. Raw and RLE2 use the existing main-thread parser; SRLE2 decoding/expansion runs in a Worker, so scheduler/IPC overhead is not isolated by these inner-operation timings.
