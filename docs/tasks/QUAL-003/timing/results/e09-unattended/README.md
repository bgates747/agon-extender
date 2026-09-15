# E09 completed unattended graphics run

## Executive summary

**The complete 39-case paired matrix passes its baseline comparison:** 624/624
intervals, all status zero, all 1,560 progress checkpoints in order, exactly the
eight existing probe differences, and zero P4 browser snapshots. P4 is faster
in all eight upload-containing stages. The largest bitmap stage is **866.038 ms
on P4 versus 883.707 ms on mainboard VDP**, compared with the previous P4
3,048.353 ms. The worst remaining elapsed excess is **0.632 ms / 3.86%** on a
short stage. This is useful evidence that the UART work holds up under rendering
load. It is not a production FPS, browser-output or scanout qualification.

The Author observed completion about 28m30s after starting a phone timer several
minutes after launch, supporting **somewhat over 30 minutes total**. The saved
MOS-clock checkpoint span converts nominally to **27m13.267s**, and is not a
reliable wall-time measurement of this run. The old 20-minute host deadline was
inadequate; this successful run does not prove what the earlier interrupted run
would have done, nor resolve the earlier intermittent mainboard BSP21_01 timeout.

Restoration and the review voice receipt are recorded below when complete.
E10 production qualification remains a separate next step; no new full-suite
rerun, renderer change, wiring change or production-performance claim occurred.

## Most useful comparisons

Medians of three instrumentation-enabled repeats. Mainboard VDP is the baseline;
negative percentages mean P4 took less time. Each row's scope is explicit.

| Work | Scope | Mainboard ms | P4 ms | P4 difference |
|---|---|---:|---:|---:|
| BSP22_03 | Resident-stage elapsed; largest P4 excess | 16.366 | 16.998 | +3.86% |
| BSP03_01 | Upload-containing stage elapsed | 883.707 | 866.038 | -2.00% |
| COMBINED | Resident scroll/clip/plot batch elapsed | 84.848 | 50.939 | -39.96% |
| BSP03_01 | Primitive work within the stage | 37.636 | 11.465 | -69.54% |
| BSP25_02 | Software-sprite work; matching call counts | 20.410 | 3.638 | -82.18% |

[Full tables](comparison.md) show all cases, ranges, prior P4 values and
count-matching exclusions. Raw data and analysis retain bytes, counts and all
output intervals. Stage elapsed includes incoming traffic and completion work;
it is not isolated upload throughput. Primitive and sprite scopes overlap and
must not be added. The 64-operation road batches are not single-plot timings.

## Validation and limits

1. The strict validator accepted 4,992 metric rows / 624 intervals, expected
   order, bytes/upload metadata, disabled-instrumentation controls and timer
   controls. All statuses are zero.
2. All eight mismatch records match the previous complete baseline exactly,
   including repeat, route, case, index and expected/actual colour values.
   These remain known differences, not full graphics API conformance.
3. The progress journal contains the expected five ordered checkpoints for
   every case/route/repeat. The terminal record reports status0, saved624,
   mismatches8. The autonomous voice player returned a success receipt, and the
   Author separately confirmed the test finished.
4. Mainboard VGA was active while P4 browser output was off. Unequal scanout
   work prevents an output-speed comparison. Zero snapshots before/after is
   recorded, and the host made no queries during execution.
5. The r02 fixture adds journal and mainboard status work between intervals.
   Payloads/order are byte-identical to the 39-case baseline. Additional
   between-interval work changes total runtime; it is not billed as primitive
   rendering. Three samples provide observed ranges, not a large statistical
   confidence study.
6. The earlier mainboard timeout and 550-interval collector interruption remain
   preserved. This run supplies the missing complete comparison, not a claimed
   fix for the intermittent failure.

## Duration and future estimates

| Observation | Duration / meaning |
|---|---|
| Author's phone timer | About 28m30s after the timer was started |
| Start offset | A few minutes earlier; not precisely measured |
| Author's total-runtime assessment | Somewhat more than 30 minutes |
| First preload to final pre-probe checkpoint | 195,992 raw MOS ticks |
| Nominal conversion at 120 ticks/s | 27m13.267s; excludes last probes/terminal/audio |
| Sum of renderer-local timed intervals | 344.230s; excludes much of the harness |

MOS's clock increments by two per VBLANK (`agon-mos/src/interrupts.asm`);
mode20 selects a nominal 60Hz mode (`agon-vdp/video/agon_screen.h`). The
conversion therefore uses nominal 120 ticks/s, not the API's historical
“centiseconds” name. It disagrees with the human observation; no exact wall
runtime or cause is established. Lost/coalesced interrupts are a possibility,
not a measured diagnosis. Do not use this conversion to overrule the stopwatch.
The different clocks/scopes also prohibit treating the difference between the
last two rows as an exact harness-overhead measurement.

For the same fully prepared suite, use **roughly 35 minutes as a provisional
planning estimate**, with a 30-minute human progress check and scheduling room
beyond that. This is a planning allowance based on one human observation, not a
measured distribution or an automatic timeout. Installation, retrieval and audio
latency are separate. The previous host deadline must not be reinstated blindly.
`analysis.json` retains nominal per-case durations for future comparable runs.

The separately built r03 fixture now records start/end/raw elapsed ticks before
its terminal record. Host complete/SD-error/VDP-error paths pass and the Agon
build succeeds; it was **not deployed or run on hardware**. Its explicit timing
still needs independent wall-clock calibration before precise duration estimates
are justified. A VDP RTC/monotonic reference is a suitable next investigation;
no new clock/firmware experiment was started during this result review.

## Reproduction and provenance

Run from the Extender repository root:

```sh
.venv/bin/python docs/tasks/QUAL-003/timing/results/e09-unattended/analyze.py
```

Run: INTEG-014-2026-09-14-23-20-09Z. Fixture:
`graphics-timing-probe-r02-unattended-b2026-09-14-22-25-41Z`, 15,687 bytes,
SHA256 `7958bd7dbe6633c39ea19a20ba42d428dbbf2709a7463463c60648e0f22a25e9`.
CSV SHA256 `46b84516a2414eb99d713551d634e15643f4742b8a458413a46fcbd7d1b8ab48`.

Pinned diagnostic images:

| Image | SHA256 |
|---|---|
| Ordinary E07P EMOS | `429f85ebb413bf3eed779307a71126b6cafb7bf884ad1824c6673e1814718b61` |
| Mainboard graphics probe | `529808bd1d3f0e9ea04cb13ca1142032da8431fe26605932ffc46738d2dd17cd` |
| P4 owner-loop candidate factory | `368ff0a00e798f598964471656608d8a944a24cc062434c918e71cda203f91c5` |

Installed EMOS ROM and both ESP writes were independently verified. Original
root startup remained unchanged. Machine-local deployment/recovery journals are
retained separately; no private bench topology is required to read these results.
