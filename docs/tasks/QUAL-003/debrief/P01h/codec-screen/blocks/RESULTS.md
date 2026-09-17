# Order4 SRLE2 block-size assessment

## Executive summary

**Keep full-input blocks. Smaller blocks did not deliver a worthwhile speed/size
tradeoff in these Linux/browser tests: they generally cost more time and more
bytes. No smaller block size earns priority for P4 testing on this evidence.**
The sensible sweep was512 bytes through128KiB in powers of two, plus full input,
with order4/record1/no differencing fixed throughout. Raw/RLE2 remained controls.

Captured512×384 scene; its RLE2 input is7,038 bytes. Times are Linux paired medians,
not P4 measurements. Percentages compare each candidate with its adjacent
full-block measurement to reduce clock/load drift.

| Block cap | Encoded bytes | Size vs full | Linux encode ms | Time vs paired full |
|---|---:|---:|---:|---:|
| 512 B | 1,444 | +54.1% | 0.335 | +184.6% |
| 1 KiB | 1,207 | +28.8% | 0.216 | +87.2% |
| 2 KiB | 1,124 | +20.0% | 0.170 | +47.1% |
| 4 KiB | 996 | +6.3% | 0.134 | +16.9% |
| 8 KiB and larger | 937 | 0% | ~0.114–0.115 | Within1% |
| Full input | 937 | baseline | 0.114 | baseline |

The8KiB-and-larger settings all encode that image as **one identical block**.
Their tiny timing differences are measurement variation, not block-size gains.

The synthetic sprite case made the penalty stronger:512-byte blocks took about
five times as long and produced2,177 bytes versus510. For noise, full-block
encoding took10.888ms;512-byte blocks took17.277ms and increased size19.7%.
32KiB–128KiB blocks were approximately tied on noise encoding time, but still
produced slightly larger files. See [all tables](TABLES.md).

Browser results also favour leaving blocks whole. The30Hz-capped, pre-encoded
mixed replay submitted28.80fps with full blocks versus26.64fps at512 bytes.
Mean decode-wall time increased from4.789 to11.849ms. These are headless Chromium
loopback results, not P4 Ethernet throughput, game fps or physical monitor refresh.

## Why the hoped-for cache benefit did not materialize here

The order4 sorter has a fixed65,536-entry32-bit counter table:256KiB, regardless
of whether the input block holds512 bytes or several kilobytes. Smaller input
blocks do not make that table small. Each block repeats initialization, model
setup and sorting overhead, and loses compression context across boundaries.
The observed host penalties are consistent with that source structure. This
is not a measurement of P4 cache misses and cannot categorically rule out a
P4-specific benefit; it does remove the empirical case for prioritizing it.

## Adapter findings and boundaries

1. Initial tests exposed allocation status3 on small blocks. The adapter's12MiB
   guard counted cumulative allocation traffic, not currently live bytes. The
   isolated r02 build subtracted allocation sizes when freeing blocks.
2. That alone did not fix the failure. The inherited order4 implementation leaves
   scratch frees commented out; the prior task adapter safely swept those buffers
   only at end-of-call. Multi-block inputs accumulated a scratch set per block.
3. The isolated r03 build sweeps tracked scratch and resets sort-cache pointers
   after each fully encoded or decoded block. It retains the12MiB live allocation
   ceiling,4096 allocation slots and Worker timeout. Original sorting/model
   algorithms and stream format are unchanged. Every reported block comparison,
   including full input, uses this same r03 adapter.
4. **No production port or firmware was changed.** These are useful findings to
   review before adopting multi-block operation anywhere. They are not evidence
   that the currently installed single-block path leaks between calls. Initial
   allocation failures remain in evidence/initial-allocation-failures.json.
5. The first fixture revision accidentally submitted raw/RLE2 controls to the
   szip CLI; the harness was corrected to submit only SRLE2. Those control
   failures were test setup mistakes, not codec failures.

## Validation and measurement

1. All144 native combinations passed exact pixels. The original CLI independently
   decoded all120 SRLE2 streams, including sub-32KiB blocks that its command-line
   encoder cannot request. Its output was RLE2-decoded and compared to raw pixels.
2. All1,152 browser exact frames passed, plus24 mixed codec/raw fallback frames.
   All1,080 paced frames completed. Malformed-envelope/CmpS and intentional
   Worker timeout checks rejected invalid input and recovered to valid raw frames.
3. Paired native timing:36 case/settings groups,20 measured alternating candidate/
   full-block pairs after two warmups. Every encoded payload was rechecked against
   the native sweep. Full-control self-comparisons varied by less than1%; differences
   of that size should not be interpreted as optimization wins.
4. Same pinned12-image corpus as the preceding codec screen. One task-owned
   physical sprite capture and synthetic patterns/noise; no new hardware capture,
   no Nurples/Rally gameplay run. Browser phase took63.1 seconds. Native and paired
   phase durations are retained in their evidence JSON.
5. Ordinary Linux desktop; no CPU/frequency isolation. Chromium151.0.7922.34,
   headless WebGL2/SwiftShader. PNG code was not exercised in this SRLE2-only
   comparison. The native and browser implementations are both task-local.

## Decision for review

Retain full-input blocks for the next SRLE2 order3/order4 P4 comparison. Keep PNG
as the separately identified alternative. A small-block P4 experiment would now
need a specific memory/latency requirement or new hardware evidence, rather than
being the leading speed hypothesis. Nothing was flashed, pushed or promoted.

## Reproduction

Run from the repository root using `.venv/bin/python`. Reuse the parent screen's
pinned corpus and private Emscripten SDK; use new output directories:

```sh
.venv/bin/python docs/tasks/QUAL-003/debrief/P01h/codec-screen/blocks/build.py agents/blocks-build \
  --emcc agents/srle2-web/emsdk/upstream/emscripten/emcc
.venv/bin/python docs/tasks/QUAL-003/debrief/P01h/codec-screen/blocks/native.py \
  --build agents/blocks-build --corpus agents/srle2-web/qualification02/corpus --out agents/blocks-native
.venv/bin/python docs/tasks/QUAL-003/debrief/P01h/codec-screen/blocks/browser.py \
  --build agents/blocks-build --native agents/blocks-native --out agents/blocks-browser
.venv/bin/python docs/tasks/QUAL-003/debrief/P01h/codec-screen/blocks/repeat.py \
  --build agents/blocks-build --native agents/blocks-native \
  --selected agents/blocks-browser/selected.json --out agents/blocks-browser/paired.json
```

`report.py --native DIR --browser DIR` regenerates tracked tables/evidence; use
only when deliberately updating this task record. Build hashes and raw samples
are retained; the r03 build generator is frozen at74e1180. Its build manifest
records the preceding HEAD because the cleanup refinement had not yet been
committed when compilation began. No source changes in official reference repos.
