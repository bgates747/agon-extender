# Focused multimode rendering results — 2026-10-13

## Executive summary

All 240 runs validate: five modes, eight workloads, two renderers and three
repeats, with all 120 same-repeat RGB/indexed trajectories matched. Mode 20
software Nurples uses **52.91% less queued-render time** and hardware Nurples
**40.46% less**, against the same-source optimized RGB888 control. Both measure
60 application updates/s in these mode 20 fixtures. This is a queued-render
cost reduction, not a game-FPS or input-latency improvement claim.

Indexed rendering is not uniformly faster. Mode 20 heavy bitmap updates fall
from 57.60 to 44.35/s despite lower queued-render cost. Modes 0/3 use native storage
for both selected builds and show mostly small differences. Mode 136 queued
rendering is unmeasured; its immediate double-buffer work must be compared using
eZ80 pacing/active/completion evidence instead.

Execution finished and ordinary startup was restored. Raw collection and offline
validation now pass, but the final physical success cue remains unissued. The
runner deliberately withheld success pending collection and incorrectly omitted
a clear execution-finished/awaiting-card-collection cue. No production promotion
or broader Author visual/gameplay acceptance follows from this report.

## Evidence and validation

1. 237,600 measured updates; all results have expected build, workload,
   counts, tags, calibration and trajectory bindings. All mapped P4 windows and
   required finite fences validate. Zero recorded abort/timer/fence faults and
   zero deltas in the eight checked HDMI output-error counters.
2. 8,016 rows exceed the measured completion/pacing budget. These are retained
   performance outcomes, not corruption or HDMI output faults. A valid run need
   not reach 60 updates/s.
3. Copied 240 raw files plus ordinary startup: 5,733,158 bytes,
   all 241 source SHA-256 checks verified. Copy/checksum/extraction/verification
   took 1.902 host seconds, excluding operator handling.
   The correct card was selected by filesystem identity plus startup/retained
   result hashes; it was safely unmounted and other media were untouched.
4. Both installed renderers bind independent flash/CLI receipts to clean common
   source `c788b668d64f61431b8de34b72262556d9e4e7b0`.

| Variant | Firmware build | Application SHA-256 |
|---|---|---|
| rgb888 | `rgb-001-r13-b2026-10-13-17-52-17Z` | `76d8c70254a32ce18af922663bee504a7c32e1a7709dc5e176b3d0e37715fc1f` |
| indexed | `indexed-hdmi-r07-b2026-10-13-18-01-06Z` | `1f0896bb4b455f6fde34b7dadddf3e4fc6d7cfc0f8bae3d1eda1ac9b33ed70d8` |

Raw results, the frozen invocation plan, sidecars, source-card checksum manifest,
installation receipts and CSV/JSON comparisons remain in ignored local evidence.
The maintained offline collector and analyzer produced this tally without bench
access. Original execution receipts remain retained alongside collected receipts.

## Scope and calculation

Each cell averages three per-run means for the same mode/workload/renderer.
Queued reduction =100×(RGB cost−indexed cost)/RGB cost; positive means indexed
uses less queued-render time, negative means more. Tables rank the worst
percentage reductions first. Small absolute costs can produce large percentages.
No significance or confidence interval is claimed from three windows.

Queued rendering excludes UART/parser, eZ80 pacing, native wait and asynchronous
HDMI output/composition. Reported update rates use raw MOS nominal 120 ticks/s,
observed in steps of 2; PRT is nominal 72k counts/s. These are fixture application
update rates, not display FPS. Rendering and completion/pacing have different
scopes and may move in opposite directions.

Modes 0/3 both use native storage; modes 8/20/136 use RGB888 versus linear RGB222.
Nurples derivatives outside mode 20 alter viewport/clipping; mode 136 is a bank-
stress derivative. Compare renderers within a mode, never equate work across modes.
Functional/timing passes do not replace visual fidelity, production gameplay,
input-latency or release qualification.

## Queued rendering — all instrumented comparisons

| Mode | Workload | RGB µs/update | Indexed µs/update | Reduction % | RGB updates/s | Indexed updates/s |
|---:|---|---:|---:|---:|---:|---:|
| 20 | hardware-static | 19.33 | 34.60 | -79.03 | 60.00 | 60.00 |
| 3 | hardware-static | 26.46 | 39.34 | -48.68 | 60.00 | 60.00 |
| 8 | hardware-static | 23.23 | 32.53 | -40.06 | 60.00 | 60.00 |
| 20 | bitmap-light | 547.24 | 575.59 | -5.18 | 60.00 | 60.00 |
| 3 | partial-scroll | 1849.94 | 1910.23 | -3.26 | 60.00 | 60.00 |
| 3 | software-scroll | 3705.02 | 3817.56 | -3.04 | 55.39 | 55.10 |
| 3 | software-static | 1352.51 | 1383.71 | -2.31 | 60.00 | 60.00 |
| 3 | nurples-hardware | 1917.03 | 1954.67 | -1.96 | 60.00 | 60.00 |
| 3 | nurples-software | 2111.51 | 2148.95 | -1.77 | 60.00 | 60.00 |
| 3 | bitmap-light | 833.47 | 844.79 | -1.36 | 60.00 | 60.00 |
| 3 | bitmap-heavy | 3190.50 | 3227.30 | -1.15 | 40.99 | 40.83 |
| 0 | nurples-hardware | 2881.12 | 2902.87 | -0.75 | 60.00 | 60.00 |
| 0 | partial-scroll | 2688.77 | 2708.20 | -0.72 | 60.00 | 60.00 |
| 0 | software-scroll | 4869.61 | 4893.30 | -0.49 | 55.10 | 55.10 |
| 0 | nurples-software | 3231.39 | 3238.57 | -0.22 | 60.00 | 60.00 |
| 0 | software-static | 1682.74 | 1685.47 | -0.16 | 60.00 | 60.00 |
| 0 | bitmap-light | 839.44 | 839.23 | +0.03 | 60.00 | 60.00 |
| 0 | bitmap-heavy | 3166.31 | 3147.66 | +0.59 | 43.99 | 43.90 |
| 0 | hardware-static | 32.88 | 30.51 | +7.21 | 60.00 | 60.00 |
| 20 | bitmap-heavy | 2430.34 | 2191.63 | +9.82 | 57.60 | 44.35 |
| 8 | bitmap-light | 753.89 | 568.04 | +24.65 | 60.00 | 60.00 |
| 8 | bitmap-heavy | 2880.80 | 2157.30 | +25.11 | 40.30 | 51.92 |
| 20 | nurples-hardware | 3669.56 | 2184.92 | +40.46 | 60.00 | 60.00 |
| 8 | partial-scroll | 1595.33 | 928.28 | +41.81 | 60.00 | 60.00 |
| 8 | nurples-hardware | 1772.91 | 971.83 | +45.18 | 59.99 | 60.00 |
| 20 | software-static | 1814.98 | 954.44 | +47.41 | 60.00 | 60.00 |
| 8 | nurples-software | 1887.30 | 920.34 | +51.23 | 60.00 | 60.00 |
| 20 | nurples-software | 3923.63 | 1847.68 | +52.91 | 60.00 | 60.00 |
| 20 | software-scroll | 6135.51 | 2735.85 | +55.41 | 59.02 | 56.99 |
| 8 | software-static | 2184.45 | 954.90 | +56.29 | 60.00 | 60.00 |
| 20 | partial-scroll | 3982.14 | 1644.06 | +58.71 | 60.00 | 60.00 |
| 8 | software-scroll | 5281.57 | 1961.49 | +62.86 | 44.91 | 60.00 |

The worst percentage regression is mode 20 isolated hardware sprites, but the
absolute difference is only 15.28 µs/update (19.33→34.60). Mode 20 light bitmap
queued cost rises 5.18%. Mode3 differences do not establish a useful indexed
benefit because both builds use the native backend there.

Mode 20 heavy bitmap throughput falls 23.00% while queued cost falls 9.82%.
Mode 20 scrolling software sprites also slow 59.02→56.99 updates/s despite 55.41%
lower queued-render cost. These discrepancies need a bounded completion/output/
contention investigation before a blanket performance claim; this run does not
isolate their mechanism.

## Mode 136 — application pacing, queued rendering unmeasured

Update-rate change =100×(indexed−RGB)/RGB. Worst changes first. These measurements
include immediate double-buffer behavior, without claiming queue-cost reduction.

| Workload | RGB updates/s | Indexed updates/s | Update-rate change % |
|---|---:|---:|---:|
| bitmap-heavy | 30.08 | 30.08 | +0.00 |
| bitmap-light | 59.02 | 60.00 | +1.67 |
| hardware-static | 58.70 | 60.00 | +2.22 |
| software-static | 41.97 | 60.00 | +42.96 |
| partial-scroll | 30.13 | 57.45 | +90.71 |
| nurples-software | 30.43 | 59.99 | +97.17 |
| nurples-hardware | 30.17 | 59.86 | +98.41 |
| software-scroll | 14.27 | 28.31 | +98.43 |

## Duration and terminal state

Host campaign elapsed: 8768.544 seconds
(146.14 minutes), from 18:20:46 to 20:46:55 EDT on
2026-10-13. Summed invocation/asset-load/work/listener-handback intervals:
8013.487 seconds. Remaining host preparation/transitions/collection-handback
overhead: 755.057 seconds. These are host
monotonic durations, not isolated CPU or fixture timing. Raw retrieval was
physical-card collection afterward; no bulk serial retrieval occurred.

Final indexed candidate remains the last installed image. Ordinary 38-byte
keyboard-only startup was restored and the listener positively exited before
collection. Current offline state is `validated_awaiting_notification`.
The card is safely unmounted on Oryx, ready for return to Agon. No reset, flash,
input injection or final success display occurred during results processing.

## Author visual observations after review

The Author reports that all mode20 Nurples runs they saw looked pretty good.
The indexed/software configuration remains the queued-render timing winner,
conditional on checking software-sprite flicker near the top screen edge. The
Author recalls hardware sprites removed that issue in the earlier inspection;
this is retained historical visual evidence, not a fresh controlled A/B result.

The Author reports severe background and sprite flicker in the16-colour
versions. The selected suite's16-colour modes are0 and136, but individual
observed run identities and per-mode flicker attribution were not supplied.
Do not infer that both renderers or every repeat had an independently observed
identical defect. Data-valid runs do not establish visual fidelity; these
observations block a blanket visual pass for the16-colour derivatives.

No new fixture, reset or rerun follows from these observations. A bounded
mode20 top-edge comparison and separate16-colour flicker diagnosis remain in
the owning task, with exact renderer/mode/run identity required for new evidence.

## Remaining work

The [owning qualification task](MULTIMODE-QUALIFICATION-R01.md) retains remaining
work: completion/collection-phase cues, any requested bounded regression analysis,
and separately admitted final notification after card return. The newer
[control-plane task](../QUAL-006.md) retains the general production-support
redesign. Do not rerun measurements or promote firmware from this report alone.
