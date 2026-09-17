# Order4 block-size measurements

All comparisons use the same isolated r03 adapter. Encode medians use20 alternating candidate/full-block pairs after two warmups. Native bytes include codec headers. Negative encode delta means faster; positive size delta means larger.

## retained-sprites — RLE2 input 7,038 bytes

| Block cap | Blocks | Bytes | Size vs full | Linux encode ms | Encode vs paired full |
|---|---:|---:|---:|---:|---:|
| 512 B | 14 | 1,444 | +54.1% | 0.335 | +184.6% |
| 1,024 B | 7 | 1,207 | +28.8% | 0.216 | +87.2% |
| 2,048 B | 4 | 1,124 | +20.0% | 0.170 | +47.1% |
| 4,096 B | 2 | 996 | +6.3% | 0.134 | +16.9% |
| 8,192 B | 1 | 937 | +0.0% | 0.115 | +0.1% |
| 16,384 B | 1 | 937 | +0.0% | 0.114 | +0.4% |
| 32,768 B | 1 | 937 | +0.0% | 0.114 | +0.3% |
| 65,536 B | 1 | 937 | +0.0% | 0.115 | +0.4% |
| 131,072 B | 1 | 937 | +0.0% | 0.114 | -0.6% |
| Full input | 1 | 937 | +0.0% | 0.114 | -0.9% |
## sprites1 — RLE2 input 15,022 bytes

| Block cap | Blocks | Bytes | Size vs full | Linux encode ms | Encode vs paired full |
|---|---:|---:|---:|---:|---:|
| 512 B | 30 | 2,177 | +326.9% | 0.612 | +402.4% |
| 1,024 B | 15 | 1,503 | +194.7% | 0.349 | +226.2% |
| 2,048 B | 8 | 1,098 | +115.3% | 0.230 | +116.0% |
| 4,096 B | 4 | 835 | +63.7% | 0.163 | +50.8% |
| 8,192 B | 2 | 673 | +32.0% | 0.127 | +18.8% |
| 16,384 B | 1 | 510 | +0.0% | 0.106 | -0.1% |
| 32,768 B | 1 | 510 | +0.0% | 0.107 | +0.0% |
| 65,536 B | 1 | 510 | +0.0% | 0.106 | -0.0% |
| 131,072 B | 1 | 510 | +0.0% | 0.107 | +0.8% |
| Full input | 1 | 510 | +0.0% | 0.107 | -0.5% |
## noise — RLE2 input 196,579 bytes

| Block cap | Blocks | Bytes | Size vs full | Linux encode ms | Encode vs paired full |
|---|---:|---:|---:|---:|---:|
| 512 B | 384 | 181,649 | +19.7% | 17.277 | +58.8% |
| 1,024 B | 192 | 171,399 | +13.0% | 14.018 | +29.7% |
| 2,048 B | 96 | 164,260 | +8.3% | 12.364 | +14.4% |
| 4,096 B | 48 | 159,352 | +5.0% | 11.686 | +6.1% |
| 8,192 B | 24 | 156,147 | +2.9% | 11.227 | +3.3% |
| 16,384 B | 12 | 154,069 | +1.6% | 10.992 | +0.9% |
| 32,768 B | 6 | 152,788 | +0.7% | 10.898 | +0.3% |
| 65,536 B | 3 | 152,174 | +0.3% | 10.830 | +0.0% |
| 131,072 B | 2 | 151,937 | +0.1% | 10.882 | +0.1% |
| Full input | 1 | 151,715 | +0.0% | 10.888 | +0.1% |

## Mixed full-size loopback replay

Pre-encoded frames,30Hz ceiling, headless Chromium/SwiftShader. These are CPU submission cadence and browser decode costs, not P4, Ethernet or physical display measurements.

| Block cap | Submitted fps | FPS vs full | Mean decode-wall ms |
|---|---:|---:|---:|
| raw | 27.47 | -4.6% | 1.244 |
| rle2 | 28.06 | -2.6% | 1.935 |
| 512 B | 26.64 | -7.5% | 11.849 |
| 1,024 B | 27.91 | -3.1% | 8.194 |
| 2,048 B | 27.82 | -3.4% | 7.959 |
| 4,096 B | 28.38 | -1.4% | 6.666 |
| 8,192 B | 28.60 | -0.7% | 5.823 |
| 16,384 B | 28.40 | -1.4% | 5.568 |
| 32,768 B | 28.47 | -1.1% | 5.389 |
| 65,536 B | 28.68 | -0.4% | 5.412 |
| 131,072 B | 28.60 | -0.7% | 5.456 |
| Full input | 28.80 | +0.0% | 4.789 |
