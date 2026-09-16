# P01c/d measured comparisons

## Refresh completion pacing

Worst spacing p95 first. Mainboard historical baseline:59.927 completions/s,17.063ms p95. Baseline is retained evidence, not a fresh same-session mainboard run. Positive percentage means a longer p95 interval. These are explicit RefreshSprites completions, not browser presentation.

| Run | Refresh/s | Spacing p95 ms | vs mainboard p95 | Spacing max ms | Enqueue spacing p95 ms | Enqueue→completion p95 ms |
|---|---:|---:|---:|---:|---:|---:|
| p01cd-normal1-probe0 | 60.062 | 24.796 | +45.3% | 33.573 | 23.193 | 4.175 |
| p01cd-normal6-probe1 | 60.048 | 22.281 | +30.6% | 53.063 | 22.363 | 4.102 |
| p01cd-discard3-probe0 | 60.054 | 20.352 | +19.3% | 21.424 | 17.509 | 3.947 |
| p01cd-discard4-probe1 | 60.057 | 17.315 | +1.5% | 21.219 | 17.462 | 4.052 |
| p01cd-off5-probe1 | 60.055 | 17.213 | +0.9% | 21.405 | 17.341 | 3.993 |
| p01cd-off2-probe0 | 60.056 | 17.125 | +0.4% | 21.190 | 17.347 | 3.944 |

## Output operations

Marker-window full512×384 snapshots and196640byte sends (196608pixels plus32byte EVF header). All costs are elapsed wall time including preemption/waits. Different achieved work rates prohibit exclusive-cost subtraction. No equivalent mainboard Ethernet operation.

| Run | Compose calls | Compose mean ms | Compose/s | Send calls | Send mean ms | Sends/s |
|---|---:|---:|---:|---:|---:|---:|
| p01cd-off2-probe0 | 0 | — | 0.000 | 0 | — | 0.000 |
| p01cd-discard4-probe1 | 2397 | 7.188 | 59.986 | 0 | — | 0.000 |
| p01cd-discard3-probe0 | 2397 | 6.445 | 60.002 | 0 | — | 0.000 |
| p01cd-normal6-probe1 | 897 | 9.299 | 22.446 | 898 | 23.415 | 22.471 |
| p01cd-normal1-probe0 | 1017 | 7.273 | 25.453 | 1017 | 18.294 | 25.453 |
| p01cd-off5-probe1 | 0 | — | 0.000 | 0 | — | 0.000 |

## Instrumented owner distributions

Wait/hold are outermost native acquisitions; wake is coalesced notification age, not exclusively scheduler latency. Histogram p95 is a bucket upper bound. Values are milliseconds. Totals include warmup and admitted scopes through terminal drain; completion tables discard120warmup boundaries. Do not add concurrent-owner totals as CPU time.

| Run | Owner metric | Count | Sum ms | Mean ms | Max ms | p95 bucket upper ms |
|---|---|---:|---:|---:|---:|---:|
| p01cd-discard4-probe1 | parser_wait | 242625 | 1601.160 | 0.007 | 2.356 | 0.031 |
| p01cd-discard4-probe1 | parser_hold | 242625 | 1972.764 | 0.008 | 2.307 | 0.015 |
| p01cd-discard4-probe1 | draw_wait | 255953 | 2736.356 | 0.011 | 0.393 | 0.031 |
| p01cd-discard4-probe1 | draw_hold | 255953 | 5170.952 | 0.020 | 0.946 | 0.127 |
| p01cd-discard4-probe1 | output_wait | 460224 | 3867.733 | 0.008 | 0.867 | 0.031 |
| p01cd-discard4-probe1 | output_hold | 460224 | 5052.425 | 0.011 | 0.436 | 0.031 |
| p01cd-discard4-probe1 | draw_notification_age | 9589 | 177.233 | 0.018 | 0.364 | 0.031 |
| p01cd-discard4-probe1 | output_notification_age | 2397 | 28.473 | 0.012 | 0.338 | 0.031 |
| p01cd-normal6-probe1 | parser_wait | 242624 | 2426.316 | 0.010 | 22.477 | 0.031 |
| p01cd-normal6-probe1 | parser_hold | 242624 | 2502.152 | 0.010 | 16.884 | 0.015 |
| p01cd-normal6-probe1 | draw_wait | 255751 | 2081.411 | 0.008 | 22.340 | 0.031 |
| p01cd-normal6-probe1 | draw_hold | 255751 | 5914.288 | 0.023 | 9.848 | 0.127 |
| p01cd-normal6-probe1 | output_wait | 172224 | 1850.860 | 0.011 | 23.048 | 0.031 |
| p01cd-normal6-probe1 | output_hold | 172224 | 2392.092 | 0.014 | 22.336 | 0.031 |
| p01cd-normal6-probe1 | draw_notification_age | 9389 | 1525.014 | 0.162 | 22.478 | 0.511 |
| p01cd-normal6-probe1 | output_notification_age | 1813 | 16906.639 | 9.325 | 30.998 | 32.767 |
| p01cd-off5-probe1 | parser_wait | 242625 | 1044.341 | 0.004 | 2.252 | 0.007 |
| p01cd-off5-probe1 | parser_hold | 242625 | 1986.134 | 0.008 | 2.591 | 0.015 |
| p01cd-off5-probe1 | draw_wait | 255952 | 890.590 | 0.003 | 0.344 | 0.007 |
| p01cd-off5-probe1 | draw_hold | 255952 | 4390.332 | 0.017 | 1.065 | 0.063 |
| p01cd-off5-probe1 | output_wait | 0 | 0.000 | — | 0.000 | — |
| p01cd-off5-probe1 | output_hold | 0 | 0.000 | — | 0.000 | — |
| p01cd-off5-probe1 | draw_notification_age | 9587 | 140.691 | 0.015 | 0.066 | 0.031 |
| p01cd-off5-probe1 | output_notification_age | 2397 | 27.996 | 0.012 | 0.085 | 0.031 |
