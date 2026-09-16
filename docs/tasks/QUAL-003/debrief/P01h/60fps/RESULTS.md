# Nurples at 60 fps pacing with RLE2 streaming

## Executive summary

**Nurples maintained 60 application cycles/s with RLE2 streaming enabled, matching
the no-streaming control.** Browser receipts averaged **24.55 fps** against the
unchanged 30fps output cap. RLE2 therefore preserved full-speed game execution in
this trial; it did not deliver 60fps video or consistently achieve 30fps video.

| Output | Application mean ms | Application fps | Application p95/max ms | Browser fps | Browser p95 ms |
|---|---:|---:|---:|---:|---:|
| Disabled | 16.667 | 60.00 | 16.667 / 16.667 | — | — |
| RLE2, capped at 30Hz | 16.667 | 60.00 | 16.667 / 16.667 | 24.55 | 51.60 |

Application elapsed interval difference versus disabled baseline: **0.0%** at
MOS clock resolution. Each run recorded 1800 cycles, with all 1799 intervals two
MOS ticks (nominal120Hz clock). Neither recorded a VDU fault; browser reported
no page errors. Mean compressed message:37647 bytes. The browser's longest
retained receive interval was68.5ms. All retained game-window messages used EVR1.

## Scope and comparison

One trial per condition, physical P4 candidate r06, Linux Wi-Fi receiver and
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
