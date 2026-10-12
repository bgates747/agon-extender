# Indexed/PPA integration — first candidate result

## Outcome

All four records are complete and decode successfully, with no abort or recorded
fault rows. Deterministic Nurples completed 3,600 measured updates in nominal
60 seconds: **60 application updates/s**, with median active submission work
using **44.7%** of a 60 Hz budget (55.3% remaining before pacing). P4 HDMI
background publication averaged **30.1/s**, while DMA scanout remained about
60 Hz. These are different measurements; this does not prove 60 distinct game
images/s, visible correctness or responsive human input.

The partial-scroll/32-software-sprite fixture is the worst isolated case: its
pixel-query-fenced completion exceeds the 60 Hz budget on 55% of updates.
No matched ordinary-RGB888 or mainboard run was acquired for this experiment;
**no improvement or regression percentage is established**.

## Identity and execution

1. P4 candidate: `indexed-hdmi-r04-b2026-10-12-01-53-19Z`, application SHA-256
   `4bbb33276dca90a806ad03cb605b2dde13012026fad5c503a2134ea85ec5398c`.
   Four flash segments were independently verified before this run.
2. EMOS retained: `agon-emos-v0.1.24-b2026-10-10-01-48-39Z`, image SHA-256
   `69d7b11ac1fa6fcd48cc3770356c3b8806d8f308c345bd670075a7eb21b613dd`.
   Mainboard fsim P1-count VDP remained installed; no firmware changed during
   collection. EMOS rollback has **not** been performed.
3. Frozen fixture: `scan-scroll-suite-r02-b2026-10-06-23-03-19Z`, repaired
   Nurples source `0c741d5e2021927adfa440f45b8e04b950114889`; mode20, ordinary
   UART ExCom, window tag1837734. T03/T07/T08 use120 measured/60 warm-up updates;
   T09 uses3600 measured/120 warm-up updates. Configuration identities and exact
   raw-file hashes are in the [machine-readable record](INTEGRATION-CANDIDATE-R01.json).
4. Initial Agon-only launch failed at autoexec line2, receiver-ready timeout.
   The Author-directed P4 reset, short initialization wait and Agon reset
   restored input admission; that boot produced these records. This is evidence
   of recovery, not a causal finding about EMOS or P4.
5. The old launcher incorrectly started tests through autoexec. The Author
   rejected that approach. The new [test-execution protocol](../../procedures/test-execution.md)
   requires explicit CLI invocation for future runs. Original38-byte autoexec
   was restored and fully read back during collection, without reset. The
   candidate run.cfg files remain selected; their originals are retained.

## Application work and pacing

A nominal60 Hz budget is16.667ms or1200 PRT counts. PRT conversion assumes
18.432MHz/256 =72000 counts/s; MOS window timing assumes120 nominal ticks/s,
observed in increments of2. These are calibration assumptions, not independent
oscilloscope measurements. The fixture calibration samples for T03/07/08/09
are35190/35687/35916/36027 PRT counts per60 MOS ticks; percentages below use the
same nominal1200-count budget rather than silently recalibrating each case.

Isolated cases are ranked worst first by p95 fenced completion time. Active
work includes eZ80 command submission and UART effects; fenced completion adds
pixel-query reply overhead and is not pure P4 rendering time.

| Case | Median active work, % budget | Median fenced completion, % budget | P95 fenced completion, % budget | Completions over budget | Nominal updates/s |
|---|---:|---:|---:|---:|---:|
| T07 — partial scroll, 32 software sprites | 33.9% | 109.0% | 145.5% | 55.0% | 55.38 |
| T03 — partial scroll, no sprites | 13.4% | 88.2% | 97.5% | 0.8% | 60.00 |
| T08 — static background, 32 software sprites | 19.4% | 44.5% | 95.0% | 0.0% | 60.00 |

Nurples is unfenced and therefore is not ranked against the pixel-query cases.

| Game | Median active work | P95 active work | Median remaining budget before pacing | Nominal updates/s | Total intervals over budget |
|---|---:|---:|---:|---:|---:|
| Nurples | 44.7% (7.444ms) | 55.6% | 55.3% | 60.00 | 2/3600 |

T07 records118 late-flagged rows and a longest over-budget streak of3 updates;
late flags and the PRT completion threshold are distinct tests. Nurples records
zero late-flagged rows and a longest over-budget streak of1. All four records
have zero fault rows (the decoder's fault mask excludes the late flag).

## P4 output measurements

Rates below use each P4-tagged window's own microsecond duration. Background
publications are not application updates or proven distinct visible frames.
No valid per-frame markers were recorded, so counters cannot establish a
one-to-one application-frame/display-frame mapping. Scanout is the DMA frame
completion proxy; it is not an independent monitor measurement.

| Case | P4 window, s | Background publications | Publications/s | DMA scanouts | DMA scanouts/s |
|---|---:|---:|---:|---:|---:|
| T03 — partial scroll, no sprites | 2.004117 | 107 | 53.39 | 121 | 60.38 |
| T07 — partial scroll, 32 software sprites | 2.169912 | 70 | 32.26 | 131 | 60.37 |
| T08 — static background, 32 software sprites | 2.001685 | 108 | 53.95 | 120 | 59.95 |
| T09 — deterministic Nurples | 60.058774 | 1807 | 30.09 | 3607 | 60.06 |

The retained phase counters have calls crossing measurement boundaries; raw
boundary-drop fields are preserved. Do not sum overlapping phase wall times
as CPU utilization or infer transport throughput from them. No browser video
subscriber state or visual pass was established by this retrieval.

## Retention and terminal state

Raw files, SD journals, tagged P4 windows, original startup/configurations and
collection handback are retained in ignored integration evidence under
`agents/research007/integration-r01/bench`. The tracked JSON retains summaries,
raw-file hashes and configuration identities without private network details.

The foreground listener exited successfully; keyboard was ready/neutral and SD
was offline with no pending request. Ordinary startup was verified restored;
no reset, reflash or replay followed collection. P4 candidate and current EMOS
remain installed. No production selection, release tag or visual acceptance
changed. R07-I04 remains incomplete: matched baseline and resident controls are
still unperformed. BENCH-010 investigation and requested EMOS-only rollback
remain pending; this record does not resume either operation.
