# HDMI r10 — bounded physical results, 2026-10-07

The prepared r10 candidate passes both 3,600-update Nurples runs and the two
small sprite checks. Widescreen mode96 no longer reproduces the earlier stop
during this one-minute workload. Mode20 retains its previous game-loop headroom;
the 96-to97 same-carrier switch also completes. The candidate remains installed
for Author playtesting. This is bounded evidence, not production acceptance or
proof of recovery from a deliberately induced physical DMA fault.

## Combination and procedure

1. P4: `rgb-001-r10-b2026-10-07-22-56-28Z`, factory SHA-256
   `ef7e7bdae861119bcdc2fcda947631450f0890b6cefc8d4c23e2b6d8ead7498c`.
   All build artifacts and the retained r06 rollback were rehashed before
   installation. All four installed flash segments independently verified.
2. EMOS: previously verified `agon-emos-v0.1.24-b2026-10-07-23-11-33Z`.
   Author restored stock mainboard VDP using the verified pre-Pingo backup.
   Neither component was reflashed in this tranche. The older timing control
   predates the EMOS correction, so it is a regression reference, not a perfectly
   identical firmware combination.
3. Reused unchanged resident `render-load-r04-b2026-10-05-05-58-59Z`, case54,
   sixteen hardware sprites, in modes96 and97. The latter startup explicitly
   selects96 then97 before loading the fixture. Mode selection stays in autoexec.
4. Reused repaired-Nurples deterministic hardware-sprite fixtures r04 for mode96
   and r03 for mode20: 120 warmup updates followed by 3,600 recorded updates.
   No ordinary game binary or asset was modified. The wider fixture retains
   512×384 game coordinates inside the 848×480 logical mode.
5. No browser video streaming. Passive P4 serial capture and existing diagnostic
   windows observe rendering/output; SD retrieval occurs after application exit.

## Results

Game rows are ordered by median active-work cost, highest first. Baseline is
the retained successful r08 mode20 control. Work change is
`100 × (candidate median PRT counts / baseline median PRT counts − 1)`.

| Game run | Updates | Nominal game updates/s | Median active budget | Median spare budget | Work change vs baseline | Fault / late rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| r10, mode96, 848×480 | 3,600 | 60.00 | 42.875% | 57.125% | +0.292% | 0 / 0 |
| r10, mode20, 512×384 | 3,600 | 60.00 | 42.750% | 57.250% | 0.000% | 0 / 0 |
| r08 mode20 baseline | 3,600 | 60.00 | 42.750% | 57.250% | baseline | 0 / 0 |

Both new runs have no abort and exactly match the retained game-state trajectory
for all 3,600 rows: update, state, phase, actor/projectile counts, map row and RNG.
The nominal frame budget is 1/60 s, with PRT counts interpreted at 72 kHz and
MOS raw ticks at 120 Hz. Retained calibration observations remain in each record;
these are not an external oscillator calibration. Do not infer a material
performance change from the small median difference.

| Separate P4 output observation | Mode96 | Mode20 |
| --- | ---: | ---: |
| Presentations per second within game window | 60.062 | 60.069 |
| DMA scanouts per second within game window | 60.062 | 60.069 |
| Recorded scanout faults / underruns / late refills | 0 / 0 / 0 | 0 / 0 / 0 |

The small mode96 and mode97 case54 checks both pass complete-record validation,
with no bad or truncated frames. Keyboard Space advances them and each returns
normally. The observed mode97 surface is 848×480, 16 colors, on the same
848×480 carrier. The tests also traverse the two carrier sizes, 848×480 and
684×384. Queued refills are observed in the wide run, reaching six with maximum
waiting time225µs and no recorded fault. This exercises the new queue physically
but does not prove that premature overlap rejection caused every earlier failure.
Periodic serial lines can span setup, game and exit; their maxima must not be
misrepresented as exclusively hot-loop samples.

## Evidence, restoration and remaining gate

Exact build/flash receipts, startup/configuration preservation, host commands,
SD records, decoded summaries, comparison JSON and passive serial captures live
in the ignored `agents/hdmi002/mode-lifecycle/physical` silo. Test SD outputs use
`/agents/extender/results/hdmi02-r10-sprites` and `hdmi02-r10-game20`/`game96`.
Host readback/preparation durations are separate from measured game windows.

Original38-byte startup and Nurples run configuration were restored and read back
after each owner finished. Final normal reset establishes fresh, neutral Extender
input at the Legacy prompt; listener idle, no pending SD job, all measurement
windows closed and no active capture. Installed r10 remains selected locally;
production selection is unchanged, and exact r06 rollback remains available.

At the initial handback, Author visual/gameplay review remained pending. No physical fault was deliberately injected, so
post-fault cancellation/recovery remains supported by host tests rather than a
new physical pass. No additional video modes, diagnosis or firmware changes
were started during this tranche.


Subsequent Author review: gameplay is beautiful and exit restores the correctly
displayed **outro screen**. Accepted on 2026-10-07; production version v0.2.0
authorized. Preserve these exact bytes for release preparation. Physical
post-fault recovery and broader qualification are still separate gates.
