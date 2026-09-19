# Longer packing confirmations

## Executive summary

The longer runs reproduce useful dense-scene gains: automatic mode improves640×480 two-colour output from6.77 to11.97fps (+76.9%), and320×240 sixteen-colour output from19.96 to28.93fps (+45.0%). Packed-only is faster still. Sparse output is essentially unchanged. This is a retained single eight-second trial per path/workload, not a statistical confidence interval.

| Mode | Scene | Raw fps | RLE2 fps | Packed fps | Auto fps | Auto vs RLE2 | Auto frames | Auto bytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | static | 6.48 | 30.00 | 9.39 | 30.00 | +0.0% | 240 | 5294 |
| 2 | dense | 6.55 | 6.77 | 14.91 | 11.97 | +77.0% | 96 | 76839 |
| 2 | moving | 6.54 | 30.00 | 14.94 | 30.00 | -0.0% | 240 | 7777 |
| 9 | static | 20.09 | 59.88 | 29.88 | 59.25 | -1.0% | 474 | 1890 |
| 9 | dense | 20.08 | 19.96 | 30.00 | 28.93 | +45.0% | 231 | 38452 |
| 9 | moving | 20.04 | 15.00 | 30.00 | 15.00 | +0.0% | 120 | 3920 |

Combined mode execution: 306.1 seconds (5.1 minutes), including preparation/reset/warmup and exit. Same firmware/fixture and host as the broad sweep; eight measured seconds per variant after one second warmup. All static/dense decoded outputs matched exactly, and both moving cases changed sampled content. No new transition retry occurred.

P4 phase counters and browser decode milliseconds are retained in CONFIRMATION.json. Their scope and limitations are the same as the main results. Four raw/RLE2/packed/automatic paths are measured sequentially. The 320×240 sparse moving scene still plateaus at15fps with RLE2 and automatic versus30fps packed-only; it remains an output/pacing investigation, not a solved issue.
