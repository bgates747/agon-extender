# CPU versus indexed PPA expansion

Build `ppa-clut-benchmark-r01-b2026-10-12-00-21-22Z`; run 1 (fresh).
Firmware workload/check duration: 14.439 s; excludes result storage and serial emission.

32 samples per method/case. Values are total elapsed microseconds, shown as median / p95 / worst. Worst complete-path PPA-to-CPU p95 ratio first.

| Workload / destination | Old CPU signal | Linear CPU control | Linear PPA | Reorder + PPA | PPA p95 improvement | Complete-path p95 improvement |
|---|---:|---:|---:|---:|---:|---:|
| 320×32 / SRAM | 1008.5 / 1009 / 1009 | 950.0 / 951 / 951 | 277.0 / 278 / 278 | 470.0 / 473 / 475 | +72.4% | +53.1% |
| 320×240 / PSRAM | 9890.0 / 9897 / 9898 | 9462.0 / 9464 / 9464 | 1770.5 / 1784 / 1785 | 4430.0 / 4444 / 4455 | +82.0% | +55.1% |
| 512×32 / SRAM | 1616.0 / 1623 / 1623 | 1525.0 / 1532 / 1532 | 395.0 / 395 / 395 | 721.0 / 722 / 722 | +75.7% | +55.5% |
| 320×32 / PSRAM | 1099.0 / 1104 / 1104 | 1041.5 / 1047 / 1047 | 282.0 / 283 / 283 | 474.0 / 475 / 475 | +74.4% | +57.0% |
| 512×32 / PSRAM | 1755.0 / 1761 / 1761 | 1662.0 / 1662 / 1662 | 414.0 / 422 / 422 | 729.0 / 733 / 737 | +76.0% | +58.4% |
| 512×384 / PSRAM | 24775.0 / 24783 / 24783 | 23696.0 / 23702 / 23704 | 3770.5 / 3779 / 3785 | 10230.5 / 10251 / 10251 | +84.8% | +58.6% |

Improvement = 100 × (old CPU p95 − candidate p95) / old CPU p95; positive means faster. Linear PPA assumes a changed framebuffer layout. Reorder + PPA includes adapting the old signal layout.

Source is PSRAM; CPU conversion includes output publication and PPA includes driver cache work plus blocking completion. No HDMI scanout, sprites, game, browser or other concurrent workload runs. Elapsed cycle counts include waiting/preemption and are not CPU-busy measurements.

| Workload / destination | Old CPU worst / budget | Reorder + PPA worst / budget | Budget context |
|---|---:|---:|---|
| 320×32 / SRAM | 63.1% | 29.7% | 1600.0 µs strip guard |
| 320×240 / PSRAM | 59.4% | 26.7% | 16666.7 µs 60 Hz frame |
| 512×32 / SRAM | 101.4% | 45.1% | 1600.0 µs strip guard |
| 320×32 / PSRAM | 69.0% | 29.7% | 1600.0 µs strip guard |
| 512×32 / PSRAM | 110.1% | 46.1% | 1600.0 µs strip guard |
| 512×384 / PSRAM | 148.7% | 61.5% | 16666.7 µs 60 Hz frame |

Budget percentages are context only, not output/gameplay qualification. Timer resolution is one microsecond; CPU configured at 360 MHz, PSRAM at 200 MHz, dynamic power management disabled. Detailed phase distributions and raw cycles are in results.json and samples.csv.

## Execution and restoration

RESEARCH-007 R07-B05 completed under the Author's bench handover. The host
validated all768 measured rows from one fresh run. The P4 verified every output
pixel, source integrity and guard after every warmup and timed conversion, then
acknowledged its NVS commit before printing the complete batch. NVS replay or
power-loss resilience was not separately tested. Timing comparisons above use
p95 total elapsed time; percentages denote reduced time, not higher game FPS.

The host held Agon reset throughout the standalone installation, run and ordinary
P4 restoration. Benchmark three-segment write/readback passed; restoration of the
exact preceding data-r20 P4 passed all four segment verifications. EMOS, mainboard
VDP, wiring, SD files and startup were unchanged. Ordinary P4 initialization was
observed; Agon reset was released and fresh admitted CLI input plus five seconds
of ready/neutral keyboard and idle SD status passed. No active fixture, collector
or reset hold remains. The bench is released, production unchanged.

A restoration helper initially waited for a boot text marker absent from the
frozen older data-r20 source. This was a helper assumption, not a benchmark or
firmware failure. Verified ordinary initialization and fresh input/readiness
provided restoration proof; no deeper firmware debugging or repeated benchmark
was needed.

[Normalized physical evidence](PHYSICAL-EVIDENCE.json) pins retained raw
serial/CSV/JSON, timing distributions and restoration receipts. Local journal:
`agents/research007/benchmark-r01/bench`. Full workload/check time14.439231s excludes
NVS storage and serial printing. This one unloaded run does not establish
behaviour under scanout traffic, sprite/Copper workloads or the current direct
RGB888 renderer, which avoids the old conversion entirely. Stop for review
before integration or another benchmark campaign.
