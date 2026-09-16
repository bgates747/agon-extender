# P01e captured timeline

## Executive summary

One complete long native hold is captured in a failed diagnostic run. Task residency includes interrupts. Ring coverage passes; benchmark terminal-query acceptance fails.

## Core1 timeline relative to hold acquisition

| Start ms | End ms | Task | Priority at entry |
|---:|---:|---|---:|
| 0.000 | 0.021 | stock-output | 2 |
| 0.024 | 0.087 | emac_rx | 15 |
| 0.089 | 0.572 | tiT | 18 |
| 0.574 | 0.632 | emac_rx | 15 |
| 0.634 | 0.885 | tiT | 18 |
| 0.887 | 0.947 | emac_rx | 15 |
| 0.949 | 10.869 | tiT | 18 |
| 10.871 | 13.888 | tiT | 18 |
| 13.890 | 14.131 | tiT | 18 |
| 14.133 | 14.379 | tiT | 18 |
| 14.381 | 21.966 | tiT | 18 |
| 21.968 | 22.707 | tiT | 18 |
| 22.709 | 22.940 | tiT | 18 |
| 22.942 | 23.187 | tiT | 18 |
| 23.189 | 23.676 | tiT | 18 |
| 23.678 | 24.381 | tiT | 18 |
| 24.384 | 24.491 | tiT | 18 |
| 24.493 | 24.531 | tiT | 18 |
| 24.533 | 24.643 | tiT | 18 |
| 24.644 | 24.676 | tiT | 18 |
| 24.678 | 24.785 | tiT | 18 |
| 24.787 | 24.821 | tiT | 18 |
| 24.823 | 24.944 | tiT | 18 |
| 24.946 | 24.986 | tiT | 18 |
| 24.989 | 25.210 | stock-output | 5 |

## Both-core residency totals

Totals are per core; do not sum cores as wall time or exclusive CPU usage.

| Core | Task | Residency ms |
|---:|---|---:|
| 1 | tiT | 24.737 |
| 0 | IDLE0 | 19.393 |
| 0 | emac_rx | 3.991 |
| 0 | httpd | 1.097 |
| 1 | stock-output | 0.242 |
| 1 | emac_rx | 0.181 |
| 0 | esp_timer | 0.124 |
| 0 | extender-net | 0.027 |
| 0 | stock-draw | 0.022 |
| 0 | processLoop | 0.007 |

## Comparison status

Current probe-on data is diagnostic-only because the fixture failed. Percentages below describe the observed values, not a valid performance improvement/degradation attribution.

| Measure | Current off | Current on, failed | Observed change vs off |
|---|---:|---:|---:|
| Refresh completions/s | 50.138 | 34.661 | -30.9% |
| Spacing p95 ms | 33.297 | 46.145 | +38.6% |
| Spacing max ms | 158.895 | 86.995 | -45.3% |
| Enqueue spacing p95 ms | 32.884 | 45.787 | +39.2% |
