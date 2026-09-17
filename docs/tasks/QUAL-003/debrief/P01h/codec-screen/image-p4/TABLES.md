# Matched physical image-codec tables

## Game delivery

Central15-second browser receipt window, ending5 seconds before final receipt.
All runs use clean identical mode20 startup,512×384 source, application cadence60
and30Hz browser request cap. Counters cover whole invocation, a different scope.

| Phase / codec | Received fps mean (range) | Change vs paired RLE2 | Mean wire bytes/frame | Validate/expand ms | Encode ms | Browser decode/parse ms | Application cycles/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| jpeg / JPEG90 RGB888 444 | 6.26 (5.94–6.66) | -52.6% | 119,201 | 14.330 | 4.800 | 2.952 | 60.00 |
| jpeg / RLE2 | 13.22 (12.77–13.80) | +0.0% | 37,587 | 0.000 | 6.385 | 0.471 | 59.99 |
| png / PNG level1 | 6.71 (6.65–6.77) | -50.8% | 23,344 | 5.487 | 78.980 | 2.894 | 60.00 |
| png / PNG level3 | 6.37 (6.34–6.40) | -53.4% | 21,725 | 5.426 | 80.824 | 2.770 | 60.00 |
| png / RLE2 | 13.65 (13.19–13.93) | +0.0% | 37,702 | 0.000 | 6.338 | 0.492 | 60.00 |

## Static completed scenes

20 receipts per condition; discard first2; one run per condition. These are
snapshot delivery rates, not changing-game FPS. Encoder counters cover entire
condition; baseline is same-scene RLE2.

| Scene / codec | Receipt fps | vs RLE2 | Wire bytes/frame | Validate/expand ms | Encode ms |
|---|---:|---:|---:|---:|---:|
| bitmap_raw / rle2 | 25.88 | +0.0% | 3,301 | 0.000 | 4.937 |
| bitmap_raw / jpeg | 16.39 | -36.6% | 7,479 | 13.773 | 4.767 |
| bitmap_raw / png1 | 12.03 | -53.5% | 2,017 | 5.376 | 57.655 |
| bitmap_raw / png3 | 12.03 | -53.5% | 2,011 | 5.416 | 57.668 |
| raw_sprites / rle2 | 29.25 | +0.0% | 7,070 | 0.000 | 5.109 |
| raw_sprites / jpeg | 13.15 | -55.0% | 9,945 | 13.668 | 4.716 |
| raw_sprites / png1 | 12.01 | -59.0% | 2,945 | 5.323 | 58.980 |
| raw_sprites / png3 | 12.01 | -59.0% | 2,594 | 5.373 | 58.897 |
| incompressible / rle2 | 6.66 | +0.0% | 196,640 | 0.000 | 9.794 |
| incompressible / jpeg | 4.86 | -27.1% | 293,636 | 13.657 | 5.268 |
| incompressible / png1 | 9.51 | +42.7% | 4,043 | 5.286 | 62.860 |
| incompressible / png3 | 10.01 | +50.2% | 3,157 | 5.290 | 62.418 |
