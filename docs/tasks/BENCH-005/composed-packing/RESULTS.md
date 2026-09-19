# Composed packing — hardware results

## Executive summary

Results are provisional until all requested modes and exceptions are reviewed. Final-colour packing preserves composition; measured performance depends on image entropy. RLE2 is the baseline below, with its size limit corrected for all supported resolutions.

## Matched browser presentation submissions

Each trial uses the same candidate, compositor, host and60Hz request cap. These are headless Chromium presentation submissions, not physical display refresh or game simulation fps. Static and dense cases compare decoded images exactly against the same P4 compositor without compression. This qualifies wire preservation, not new stock-mainboard pixel parity. Moving cases measure output during deterministic drawing; images differ in time and are not compared bytewise.

| Mode | Scene | RLE2 fps | Packed fps | Auto fps | Auto vs RLE2 | RLE2 bytes | Packed bytes | Auto bytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | dense | 5.36 | 8.64 | 7.37 | +37.6% | 287805 | 153641 | 153641 |
| 0 | dense | 5.36 | 8.79 | 7.51 | +40.2% | 304835 | 153652 | 153652 |
| 3 | dense | 10.59 | 11.29 | 9.47 | -10.6% | 153632 | 153632 | 153632 |
| 2 | dense | 6.72 | 14.73 | 11.89 | +76.9% | 244381 | 76839 | 76839 |
| 6 | static | 14.99 | 15.51 | 14.74 | -1.7% | 2930 | 76842 | 2930 |
| 6 | moving | 15.00 | 23.71 | 14.88 | -0.8% | 3957 | 38439 | 3957 |
| 8 | static | 15.00 | 19.66 | 14.88 | -0.8% | 3444 | 76832 | 3444 |
| 5 | dense | 10.08 | 15.52 | 14.88 | +47.5% | 143925 | 76841 | 76841 |
| 8 | moving | 15.00 | 29.74 | 14.99 | -0.1% | 3829 | 38450 | 3835 |
| 5 | static | 15.00 | 15.89 | 14.99 | -0.1% | 2930 | 76842 | 2930 |
| 10 | moving | 15.00 | 29.49 | 15.00 | -0.1% | 3923 | 38441 | 3911 |
| 7 | static | 19.99 | 20.00 | 15.00 | -25.0% | 48354 | 38438 | 38438 |
| 3 | moving | 15.00 | 15.52 | 15.00 | -0.0% | 3886 | 76850 | 3886 |
| 4 | dense | 9.48 | 15.25 | 15.00 | +58.3% | 152435 | 76852 | 76852 |
| 4 | moving | 15.00 | 15.26 | 15.00 | +0.0% | 3981 | 76850 | 3982 |
| 11 | moving | 15.00 | 31.31 | 15.01 | +0.0% | 3865 | 19239 | 3862 |
| 4 | static | 15.00 | 16.18 | 15.01 | +0.1% | 2930 | 76842 | 2930 |
| 9 | moving | 15.00 | 29.99 | 15.01 | +0.1% | 3913 | 38451 | 3922 |
| 5 | moving | 15.00 | 16.13 | 15.01 | +0.1% | 3977 | 76841 | 3975 |
| 8 | dense | 17.36 | 20.00 | 16.64 | -4.1% | 76832 | 76832 | 76832 |
| 6 | dense | 11.70 | 28.75 | 20.00 | +71.0% | 122221 | 38439 | 38439 |
| 9 | dense | 18.30 | 29.78 | 23.40 | +27.8% | 76235 | 38452 | 38452 |
| 10 | dense | 19.66 | 29.73 | 25.22 | +28.3% | 71925 | 38441 | 38441 |
| 0 | moving | 29.99 | 8.34 | 29.99 | +0.0% | 7822 | 153651 | 7821 |
| 11 | dense | 20.34 | 31.00 | 29.99 | +47.5% | 61021 | 19239 | 19239 |
| 2 | moving | 30.00 | 14.75 | 30.00 | +0.0% | 7784 | 76839 | 7788 |
| 2 | static | 29.99 | 8.80 | 30.00 | +0.0% | 5294 | 153642 | 5294 |
| 1 | moving | 29.99 | 8.04 | 30.01 | +0.1% | 7816 | 153641 | 7816 |
| 0 | static | 30.00 | 8.72 | 30.02 | +0.1% | 5294 | 153642 | 5294 |
| 1 | static | 29.99 | 8.41 | 30.24 | +0.8% | 5294 | 153642 | 5294 |
| 3 | static | 41.87 | 11.80 | 36.63 | -12.5% | 4792 | 153632 | 4792 |
| 9 | static | 60.01 | 30.01 | 59.97 | -0.1% | 1890 | 38442 | 1890 |
| 10 | static | 59.99 | 29.99 | 59.99 | +0.0% | 1890 | 38442 | 1890 |
| 11 | static | 59.45 | 30.00 | 60.00 | +0.9% | 1890 | 38442 | 1890 |

Ranked slowest automatic output first. Percentage is throughput change relative to RLE2-only; positive is faster. Payload bytes include transport frame headers, not TCP/Ethernet overhead. See SUMMARY.json for sample counts, p95 intervals, decoder milliseconds, and snapshot/socket phase milliseconds. Socket phase includes encoding: it is not pure wire time. The timing counter windows include warmup, whereas fps excludes it.

## Exceptions

1. Mode 1: P4 restart on transition; one reset retry.
1. Mode 10: P4 restart on transition; one reset retry.
1. Mode 5: P4 restart on transition; one reset retry.
