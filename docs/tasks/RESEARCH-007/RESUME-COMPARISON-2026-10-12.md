# Matched RGB888 and indexed/PPA comparison — 2026-10-12

## Executive summary

All four paired result files validate and have identical deterministic game-state trajectories. The Author reports substantial sprite flicker in the indexed candidate and recalls an earlier version looked perfect: **candidate fails visual acceptance**, regardless of its timing results. Nurples background publication falls from60.07/s to30.14/s (49.8% lower), while application updates stay60/s. The scrolling/32-sprite fixture falls from60 to53.33updates/s; its p95 fenced cost rises74.1%. No cause or repair is established. The earlier intermittent HDMI dropout also remains unresolved.

## Application work and completion

A 60 Hz budget is 16.667 ms, or 1,200 nominal PRT counts. Percentages use 72,000 counts/s (18.432 MHz / 256); nominal application rate uses MOS120 ticks/s, observed in steps of two. These are calibration assumptions, not independent hardware clock measurements. Active work includes eZ80 command submission and transport/backpressure. Fenced completion includes pixel-query reply overhead.

Isolated cases ranked worst first by RGB888 p95 fenced completion. Lower-is-better reduction = 100 × (RGB888 − indexed) / RGB888; negative values mean regression.

| Workload | RGB888 median active, % budget | Indexed median active, % budget | RGB888 p95 fenced, % budget | Indexed p95 fenced, % budget | P95 fenced cost reduction | RGB888 updates/s | Indexed updates/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| T07 — Partial scroll + 32 software sprites | 33.75 | 33.71 | 98.75 | 171.92 | -74.09% | 60.00 | 53.33 |
| T03 — Partial vertical scroll, no sprites | 13.92 | 13.83 | 56.00 | 99.33 | -77.38% | 60.00 | 60.00 |
| T08 — Static background + 32 software sprites | 19.33 | 19.33 | 43.92 | 86.00 | -95.83% | 60.00 | 60.00 |

Nurples is unfenced: its active work is not a measurement of completed rendering or distinct displayed frames.

| Nurples metric | RGB888 | Indexed/PPA |
|---|---:|---:|
| Median active work, % budget | 42.67 | 42.42 |
| P95 active work, % budget | 52.92 | 53.00 |
| Median remaining budget before pacing, % | 57.33 | 57.58 |
| Nominal application updates/s | 60.00 | 60.00 |
| Longest over-budget streak, updates | 0.00 | 0.00 |

## P4 rendering and output

Background publications and DMA completions are separate from application updates. DMA cadence does not establish monitor lock, visible correctness or sprite stability. Phase counters measure nested/concurrent wall scopes; do not sum them as CPU utilization. Expansion includes driver overhead/cache handling and is not isolated PPA kernel time. The conversion scopes are **not equivalent work**: RGB888 stages an already rendered panel image; indexed includes waiting for the prior submitted buffer, row snapshots and PPA expansion. Their difference cannot be called a CLUT-kernel slowdown or used as proof of the flicker cause. The measured publication rate is the comparable end-to-end output result.

| Case | RGB888 publications/s | Indexed publications/s | RGB888 DMA/s | Indexed DMA/s |
|---|---:|---:|---:|---:|
| T07 | 59.94 | 32.70 | 59.94 | 60.10 |
| T03 | 59.94 | 41.92 | 59.94 | 60.38 |
| T08 | 60.44 | 54.95 | 60.44 | 59.95 |
| T09 | 60.07 | 30.14 | 60.07 | 60.07 |

| Case / phase | RGB888 mean, µs/call | Indexed mean, µs/call | RGB888 maximum, µs | Indexed maximum, µs |
|---|---:|---:|---:|---:|
| T07 / row_compose | — | 12.16 | 0 | 233 |
| T07 / expand | — | 3945.45 | 0 | 4215 |
| T07 / cache | 287.21 | 45.23 | 430 | 78 |
| T07 / conversion | 580.52 | 28953.07 | 3624 | 34277 |
| T03 / row_compose | — | 12.28 | 0 | 689 |
| T03 / expand | — | 4134.41 | 0 | 4729 |
| T03 / cache | 166.27 | 72.48 | 322 | 272 |
| T03 / conversion | 98.61 | 22291.76 | 603 | 35282 |
| T08 / row_compose | — | 11.47 | 0 | 389 |
| T08 / expand | — | 3911.85 | 0 | 4175 |
| T08 / cache | 26.26 | 41.97 | 95 | 99 |
| T08 / conversion | 37.91 | 16900.86 | 62 | 32555 |
| T09 / row_compose | — | 12.29 | 0 | 1352 |
| T09 / expand | — | 4051.40 | 0 | 5584 |
| T09 / cache | 509.04 | 51.32 | 1351 | 369 |
| T09 / conversion | 119.25 | 32045.47 | 822 | 38153 |

## Identity, evidence and limits

1. RGB888 control: `rgb-001-r12-b2026-10-12-10-15-57Z`, app SHA256 `abf8bb9b013b9a2f65e6790230e9a4ff5b6f48936fda000ad192a1ddcd35a284`.
2. Indexed candidate: `indexed-hdmi-r05-b2026-10-12-10-15-57Z`, app SHA256 `636bcfc6c7f6424d72ce6c3ed17cfc46d682619c534d79f101aea2cf3b6fc40c`. Both are clean same-source `26660db54ca0ff0621cc7822b985092933a636e5`; four flash segments independently verified, NVS preserved. Neither selects parallel handling or the HDMI link observer.
3. EMOS unchanged: `agon-emos-v0.1.24-b2026-10-07-23-11-33Z`; mainboard fsim P2 ordinary timing VDP unchanged, app SHA256 `06dcfc3e0d7ddb8bc54eedf45a941330876ac07a74141e105c3dfeba6ba94a18`.
4. Frozen fixture `scan-scroll-suite-r02-b2026-10-06-23-03-19Z`; repaired Nurples source `0c741d5e2021927adfa440f45b8e04b950114889`. T03/07/08 each120 measured and60 warm-up updates; Nurples3600 measured and120 warm-up. All records complete, no abort/fault rows; P4 windows closed/non-overflowed, and per-update state/phase/actors/projectiles/map/RNG trajectories match.
5. Mode20, ordinary UART ExCom, HDMI684×384 carrier. No browser video endpoint/subscriber. Setup-only startup; each suite launched once by explicit CLI EXEC. No tests launched by autoexec.
6. Baseline invocation-to-listener100.809s; retrieval59.128s. Candidate collection was interrupted during T09 download, then its exact pending READ was resolved through the same session and the file retrieved. Candidate precise invocation-to-return duration was not persisted; elapsed time including the human pause must not be reported as fixture runtime. No rerun, reset or flash during recovery.
7. Machine-readable paired summaries and raw hashes: [comparison](RESUME-COMPARISON-2026-10-12.json). Local raw binaries, windows, install receipts, session journals and passive captures remain in the ignored campaign evidence. The tracked JSON omits private endpoints.
8. This is not a mainboard-versus-P4 comparison, visual pass, input responsiveness qualification or production promotion. Overlay/mode136/outro controls remain unperformed in this tranche.
9. Terminal state: candidate stays installed; foreground listener remains online in Legacy, with temporary setup-only63B startup and r03 candidate fixture configs unchanged. No restoration or additional launch was performed under this collection-only authorization.

[Resumption contract](RESUME-R01.md) owns remaining work.
