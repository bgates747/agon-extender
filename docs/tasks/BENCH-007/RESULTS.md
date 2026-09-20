# Paired game timing — 2026-09-20

## Executive summary

The reusable PRT and renderer recorder passed scoped hardware checks on both processors. Browser streaming was idle. Nurples sustained approximately60 application updates/s; Aginvadors averaged51; Rally missed its30-update/s target on both routes. Mainboard had one sprite/heap panic after sequential game/mode transitions; a fresh-boot Nurples retry passed. Preserve that failure as unresolved, not a failed P4 result.

## Plain-English view: work versus breathing room

**Nurples has substantial breathing room on both boards. Aginvadors has less,
and occasional heavy updates miss its pacing deadline. Rally has effectively
no breathing room in this fixture.** Browser video was off for these measurements.

These percentages divide each game's measured loop time into active work and
intentional pacing wait. Waiting is the breathing room available in those
iterations. Rows are ranked by Extender work share, busiest first; mainboard is
the comparison baseline. Values are rounded to whole percentages.

| Game | Mainboard working | Mainboard waiting | Extender working | Extender waiting |
|---|---:|---:|---:|---:|
| Rally | ~100% | ~0% | ~100% | ~0% |
| Aginvadors | 71% | 29% | 75% | 25% |
| Nurples | **31%** | **69%** | **37%** | **63%** |

1. **Nurples:** about two-thirds of the measured loop time is available for
   pacing. None of its 120 measured active intervals exceeded the time available
   for one 60-Hz refresh on either board. The small overall cadence difference
   does not by itself prove frame skips.
2. **Aginvadors:** the averages conceal heavier updates. On each board, 20 of
   120 active intervals (about 17%) exceeded one 60-Hz refresh interval. The
   separate coarse loop records show 21 two-refresh iterations. It therefore
   cannot yet serve as a dependable 60-Hz pacing reference, despite having spare
   time on lighter updates. The measured build uses one-vblank pacing, not the
   former two-tick scheduler; its roughly 51 updates/s is not a retained 50-Hz cap.
3. **Rally:** almost all measured time is active work. These unexpectedly slow
   fixture results need comparison with ordinary gameplay before generalizing
   them to the Author's smoother Legacy experience. Its elapsed-time physics
   also means the two boards need not render identical scenes at the same update.

Work share = active PRT counts / total PRT counts; waiting share = pacing PRT
counts / total PRT counts. These are aggregate elapsed-time shares, **not CPU
utilization, a percentage of a fixed 60-Hz budget, or pure instrumentation
overhead**. Active work includes game logic, keyboard polling, drawing submission,
interrupts and UART stalls. Averages do not guarantee that every update meets its
deadline. The detailed milliseconds and renderer measurements remain below.

## Natural-pipeline controls (no renderer markers)

These120-update runs retain PRT reads but omit renderer begin/end commands. Work is elapsed eZ80 time before deliberate pacing, including interrupts and UART backpressure. It is not exclusive CPU time. Rows ranked by P4 work-time increase versus mainboard; percentage = (P4/mainboard−1)×100.

| Game / mode | Mainboard work ms | P4 work ms | Work difference | Mainboard wait ms | P4 wait ms | Mainboard updates/s | P4 updates/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| Nurples /20 | 5.207 | 6.091 | +17.0% | 11.401 | 10.596 | 60.00 | 59.50 |
| Aginvadors /8 | 13.766 | 14.499 | +5.3% | 5.673 | 4.936 | 51.06 | 51.06 |
| Rally /136 | 107.450 | 64.030 | -40.4% | 0.025 | 0.024 | 9.28 | 15.58 |

Rally retains elapsed-tick physics:120 updates need not traverse identical scenes on the two routes. Its percentage describes these live-game runs, not a pixel-identical rendering speedup. Nurples logic/output are interleaved; only combined active time is claimed. Aginvadors/Rally also retain their ordinary audio commands, so transport cost is not pure graphics.

## Renderer-marked runs

ESP-local elapsed time from parsed begin to normal-worker fence completion. Includes UART arrival/submission and queue/drain time; excludes physical scanout and browser presentation. Extra fences can alter pipelining. Rank by P4 mean completion, largest first.

| Game | Mainboard completion ms | P4 completion ms | Mainboard p95 ms | P4 p95 ms | Mainboard updates/s | P4 updates/s |
|---|---:|---:|---:|---:|---:|---:|
| Rally | 79.269 | 67.216 | 100.454 | 87.418 | 9.27 | 15.45 |
| Aginvadors | 16.515 | 12.452 | 26.845 | 14.286 | 51.43 | 51.06 |
| Nurples | 16.505 | 8.116 | 16.774 | 8.943 | 59.02 | 60.00 |

All accepted marked records match their programming-console dumps exactly. Raw CSV retains submission and drain separately; neither should be added to eZ80 work as independent CPU costs. All final selected runs contain120 records and no PRT saturation.

## Precision, controls and limits

1. /16:1,152,000 nominal counts/s,0.868µs/count,56.89ms range.120 vblank controls averaged19,210.61 counts; immediate read2 counts.100ms delay saturated correctly.
2. Rally /64:288,000 nominal counts/s,3.472µs/count,227.55ms range. The wider precision control passed. Initial /16 Rally rows that saturated are retained and excluded from elapsed averages.
3. MOS raw ticks (nominal120/s, published at vblank boundaries) cross-check whole-run cadence. Two-second captures have coarse endpoint quantization;59.5 is not proof of a persistent half-frame loss.
4. Empty and rectangle controls run at approximately60 updates/s. Capability, wrong-session, empty-read and out-of-order protocol checks passed on both processors. Host recorder ASan/UBSan and analyzer tests pass.
5. These are short, single-cohort baselines, not repeated statistical trials, gameplay balance acceptance or a browser-output benchmark. Native monitor refresh is not measured.
6. A mainboard heap-corruption/LoadProhibited panic in drawSpriteScanLine occurred during sequential use. Fresh-boot marked Nurples passed. This does not establish its cause or justify an upstream fix.
7. P4 unmarked Nurples required manual recovery of its completed RAM after MOS SAVE refused an existing filename. All120 records validated; host invocation-to-service time is unavailable for that run. Unique run names now prevent this collision.
8. Per-run summary.json distinguishes fixture-to-service duration from retrieval completion. Initial binary transfer and verification, especially Rally, is separate preparation time.
