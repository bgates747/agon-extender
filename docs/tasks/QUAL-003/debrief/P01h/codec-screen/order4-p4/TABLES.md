# Matched P4 order4 results

## Fixed-mode Nurples, three trials each

Browser central15-second window per trial, excluding startup/completion. Bytes include frame/codec headers. Codec timing counters span the complete invocation, so their scope differs from the central output window. Baseline is RLE2.

| Codec | App cycles/s | Received fps | Trial range | vs RLE2 | Submitted fps | Bytes/frame | RLE2 stage ms | Extra szip ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RLE2 | 60.00 | 17.26 | 16.43–17.72 | +0.0% | 17.28 | 28459 | 6.194 | 0.000 |
| SRLE2 order3 | 60.00 | 12.40 | 12.33–12.50 | -28.2% | 12.40 | 5857 | 5.952 | 20.904 |
| SRLE2 order4 | 60.00 | 16.83 | 12.45–19.14 | -2.5% | 16.84 | 5595 | 6.024 | 18.525 |

## Exact device encoder RPC

Input is already RLE2 encoded; this table measures only the additional szip stage. One warmup plus three measured calls; no browser connected.

| Case | Order3 ms | Order4 ms | Time difference | Order3 bytes | Order4 bytes |
|---|---:|---:|---:|---:|---:|
| noise | 676.106 | 678.376 | +0.3% | 151696 | 151715 |
| scroll2 | 25.148 | 18.130 | -27.9% | 530 | 530 |
| scroll1 | 24.880 | 18.013 | -27.6% | 491 | 491 |
| scroll0 | 23.884 | 18.068 | -24.4% | 369 | 369 |
| stripes | 13.514 | 11.044 | -18.3% | 145 | 145 |
| sprites0 | 10.868 | 9.214 | -15.2% | 654 | 532 |
| sprites1 | 10.830 | 9.142 | -15.6% | 613 | 510 |
| sprites2 | 10.808 | 9.169 | -15.2% | 611 | 511 |
| retained-sprites | 9.036 | 8.284 | -8.3% | 919 | 937 |
| solid | 6.557 | 6.166 | -6.0% | 55 | 55 |
| colours | 5.791 | 5.672 | -2.0% | 111 | 111 |
| tiny | 5.503 | 5.480 | -0.4% | 46 | 46 |

## Static scenes, same512×384 mode

Twenty receipts per codec; one trial. Excludes first two intervals from receipt rate. Not a game or application-cycle measurement.

| Scene | Codec | Received fps | Bytes/frame | Extra szip ms |
|---|---|---:|---:|---:|
| bitmap_raw | rle2 | 29.23 | 3301 | 0.000 |
| bitmap_raw | srle2 | 12.13 | 232 | 8.789 |
| bitmap_raw | order4 | 12.29 | 232 | 8.176 |
| raw_sprites | rle2 | 28.23 | 7070 | 0.000 |
| raw_sprites | srle2 | 12.00 | 959 | 10.959 |
| raw_sprites | order4 | 12.00 | 977 | 9.845 |
| incompressible | rle2 | 7.92 | 196640 | 0.000 |
| incompressible | srle2 | 4.00 | 1152 | 174.939 |
| incompressible | order4 | 5.06 | 1153 | 98.307 |
