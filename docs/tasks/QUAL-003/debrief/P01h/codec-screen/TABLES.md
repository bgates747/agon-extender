# Codec screening tables

## Captured 512×384 sprite scene

Sorted by encoded size, largest first. Byte counts include codec headers but exclude the common32-byte EVC1 envelope. RLE2 is the baseline. Encode is native Linux median of20 paired samples (alternating candidate/RLE2 order); decode is browser processing excluding PNG verification/readback. Submission is CPU time issuing WebGL commands, not completed display.

| Variant | Bytes | Size vs RLE2 | Linux encode ms | Encode vs paired RLE2 | Browser decode ms | Submit ms |
|---|---:|---:|---:|---:|---:|---:|
| raw | 196608 | +2693.5% | 0.005 | -92.0% | 1.183 | 0.067 |
| rle2 | 7038 | +0.0% | 0.086 | +0.0% | 1.467 | 0.133 |
| png-l1-s0-f0 | 2553 | -63.7% | 0.307 | +254.4% | 1.850 | 0.733 |
| png-l3-s3-f2 | 2542 | -63.9% | 0.357 | +308.0% | 1.950 | 0.683 |
| png-l3-s0-f0 | 2423 | -65.6% | 0.337 | +292.6% | 0.933 | 0.383 |
| szip-o4-b4259840-r8-i0 | 1509 | -78.6% | 0.662 | +675.3% | 2.283 | 0.100 |
| srle2-o4-b4259840-r3-i0 | 1437 | -79.6% | 0.176 | +103.4% | 1.283 | 0.117 |
| szip-o4-b4259840-r1-i0 | 1310 | -81.4% | 0.581 | +566.7% | 2.133 | 0.183 |
| szip-o4-b4259840-r8-i1 | 1247 | -82.3% | 0.711 | +734.1% | 1.867 | 0.100 |
| srle2-o4-b4259840-r2-i1 | 1226 | -82.6% | 0.171 | +99.3% | 1.833 | 0.083 |
| srle2-o4-b4259840-r1-i0 | 937 | -86.7% | 0.156 | +83.9% | 1.183 | 0.183 |
| srle2-o0-b4259840-r2-i0 | 927 | -86.8% | 2.337 | +2441.0% | 2.033 | 0.133 |
| srle2-o3-b32768-r1-i0 | 919 | -86.9% | 0.163 | +92.2% | 1.083 | 0.133 |
| srle2-o3-b4259840-r1-i0 | 919 | -86.9% | 0.164 | +91.0% | 1.317 | 0.167 |

## 30 Hz mixed full-size replay

These are pre-encoded loopback frames, not P4/network/application fps. First two samples excluded. Includes synthetic noise and the captured scene. No correctness readback in this pass.

| Variant | Submitted fps | FPS vs RLE2 | Decode wall ms | Submit ms |
|---|---:|---:|---:|---:|
| raw | 27.41 | -1.8% | 1.315 | 0.111 |
| rle2 | 27.92 | +0.0% | 2.059 | 0.120 |
| srle2-o4-b4259840-r2-i1 | 28.14 | +0.8% | 5.570 | 0.123 |
| png-l1-s0-f0 | 28.28 | +1.3% | 1.634 | 0.218 |
| szip-o4-b4259840-r8-i0 | 28.30 | +1.4% | 6.718 | 0.116 |
| szip-o4-b4259840-r1-i0 | 28.31 | +1.4% | 7.522 | 0.119 |
| szip-o4-b4259840-r8-i1 | 28.31 | +1.4% | 6.898 | 0.126 |
| srle2-o3-b4259840-r1-i0 | 28.36 | +1.6% | 5.474 | 0.134 |
| srle2-o0-b4259840-r2-i0 | 28.39 | +1.7% | 5.075 | 0.125 |
| srle2-o3-b32768-r1-i0 | 28.40 | +1.7% | 5.400 | 0.150 |
| srle2-o4-b4259840-r1-i0 | 28.41 | +1.7% | 5.208 | 0.111 |
| png-l3-s0-f0 | 28.49 | +2.0% | 1.726 | 0.183 |
| png-l3-s3-f2 | 28.49 | +2.1% | 1.744 | 0.152 |
| srle2-o4-b4259840-r3-i0 | 28.52 | +2.2% | 5.233 | 0.117 |

## Native exclusions

| Reason | Cases/settings |
|---|---:|
| screening timeout: four encodes plus verification exceeded 5 seconds | 36 |

## Slowest completed native encodes

| Case | Variant | Encode ms |
|---|---|---:|
| stripes | szip-o0-b131072-r1-i0 | 17030.228 |
| solid | szip-o0-b4259840-r2-i1 | 10105.340 |
| solid | szip-o0-b4259840-r3-i0 | 8901.465 |
| solid | szip-o0-b4259840-r8-i1 | 8393.986 |
| solid | szip-o0-b4259840-r8-i0 | 8347.702 |
| solid | szip-o0-b4259840-r4-i0 | 8139.952 |
| solid | szip-o0-b4259840-r1-i1 | 8077.284 |
| solid | szip-o0-b4259840-r1-i0 | 8007.708 |
| solid | szip-o0-b4259840-r4-i1 | 7439.600 |
| solid | szip-o0-b4259840-r3-i1 | 7151.106 |
| solid | szip-o0-b4259840-r2-i0 | 6604.275 |
| solid | szip-o0-b131072-r1-i0 | 4823.966 |
