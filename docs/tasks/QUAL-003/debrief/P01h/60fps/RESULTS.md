# Nurples at 60 fps pacing with RLE2 streaming

## Executive summary

**RLE2 improved browser delivery from 8.25 to 24.55 fps—about 3×—while both
raw and RLE2 runs maintained 60 application cycles/s.** The no-streaming control
also held60fps. These matched-configuration single trials demonstrate a browser
output benefit, not an application-rate improvement at this pacing.

| Output | Application mean ms | Application fps | Application p95/max ms | Browser fps | Browser p95 ms |
|---|---:|---:|---:|---:|---:|
| Disabled | 16.667 | 60.00 | 16.667 / 16.667 | — | — |
| Raw, capped at 30Hz | 16.667 | 60.00 | 16.667 / 16.667 | 8.25 | 142.20 |
| RLE2, capped at 30Hz | 16.667 | 60.00 | 16.667 / 16.667 | 24.55 | 51.60 |

Against raw streaming, RLE2 increased browser receipt rate197.7%, reduced mean
receive interval66.4% (121.28 → 40.73ms), and reduced mean message size80.9%
(196640 → 37647 bytes). Application interval difference:0.0% at MOS resolution.
All three runs recorded1800 cycles; every one of1799 intervals was two MOS ticks.
No VDU faults or browser page errors were reported. Raw game messages were EVF1;
compressed game messages were EVR1. Longest retained browser intervals: raw176.6ms,
RLE268.5ms. Web output remained capped at30fps in both streaming conditions.

## Scope and comparison

One sequential trial per condition, physical P4 candidate r06, Linux Wi-Fi receiver and
headless Chromium. Application pacing changed from two vblanks to one; the
fixture patch preserves everything else from the retained repair-based cadence
fixture. Production applications and the ordinary 30fps test executable were
not overwritten. New executable: `/test/nurples/cadence60.bin`.

Earlier two-vblank r05 RLE2 trial received29.18fps. This run received24.55fps,
about15.9% lower, but that is a historical comparison, not a controlled isolation:
r06 also rounds browser credit delays upward, and network conditions may differ.
The current matched output-disabled control is the valid application baseline.

These timestamps measure application cycles, not pixel correctness, unique
browser frames or physical display scanout. The new run makes no claim to extend
the previous correctness coverage. Browser statistics exclude500ms at each edge
of the longest512×384 game-frame segment. Raw traces, telemetry and browser events
are retained under `evidence`; `analyze.py` reproduces the summary.

## Disposition

The controller restores the exact pre-test P4 prefix and checks original startup.
Final restoration and notification receipts are retained alongside the results.
No mainboard firmware changes or experimental push. Further output-rate changes
require a separate experiment; the existing web cap remains30fps.

## Raw-control amendment

Only the missing raw condition was run for this amendment. The existing cadence60
binary was read back byte-for-byte; firmware and browser implementation match the
prior r06 runs. The raw observer removes the RLE2 negotiation query, leaving the
same30Hz credit policy. Timing conditions were matched, but trials were sequential,
not simultaneous or randomized; Wi-Fi variability remains a limitation.

The older two-vblank r05 raw result (12.78 application fps) does not reproduce as
an application slowdown here. Do not extrapolate that historical result to this
single-vblank r06 test, or claim a cause without a separate investigation. No
extra control or diagnostic run was added to this raw-only request.
