# W10 — Full suite passes its checks; gameplay regression remains

**AUDIT-005-F007 — Remaining stalls and Nurples regression after stock draining.**
Evidence: saved paired timings plus Author gameplay observations. Owner:
PORT-003, with measurement/attribution retained under AUDIT-005. Root cause
and the next repair are unresolved.

The returned [00000007.CSV](evidence/stock-drain-full-suite/00000007.CSV)
passes all **48** case, status, pixel, clock-arithmetic and Legacy-return
checks. The Author confirms responsive USB keyboard input in Legacy, then
reports **substantial hangs in Nurples running in ExCom**, worse than before.
The fixture's bounded functional PASS is not acceptance of r08 gameplay or
responsiveness. Review of these findings remains open.

## Evidence and conditions

The [collection record](evidence/stock-drain-full-suite/collection.json)
identifies the sole new result after six preserved CSVs. Executable, manifest,
boot smoke, startup and prior results retain their prepared hashes. P4 remains
`uart-excom-console-r08-b2026-09-10-21-23-43Z`; the collection binds its verified
deployment while explicitly overriding the unchanged CSV's compiled r07
annotation. EMOS remains v0.1.12. No firmware or SD changes occurred during
collection. Hardware start UTC was not observed and is not invented.

One connected, visible browser client was required. The Author resumed the
run after requesting the P4 address and discussed browser transmission while
it ran; continuous browser visibility/connection was not instrumented and
explicit confirmation was requested. Until answered, treat that condition
as prescribed rather than independently established. No analyzer capture was
made for this suite; the saved results do not prove every physical byte.

The previous premature card return yielded no new result. The Author clarified
the mix-up and subsequently ran the test; this return supplies the complete
CSV. There is no evidence here of a lost result or filesystem failure.

## Saved timing comparison

Values are medians of three repetitions in seconds, at 120 clock units/s and
16.67 ms resolution. The [full comparison](evidence/stock-drain-full-suite/comparison.json)
retains every send, tail, total and query-wait value/range for both routes and
both firmware sessions. Medians are computed independently. The reference is
the [original full suite](hardware-baseline.md), also requiring browser video.

| Entry / payload | ExCom send before | ExCom send now | ExCom total before | ExCom total now | Legacy total now |
| --- | ---: | ---: | ---: | ---: | ---: |
| byte / null | 3.650 | 3.200 | 4.183 | 3.483 | 1.250 |
| byte / points | 4.567 | 2.300 | 5.217 | 2.367 | 1.017 |
| count / null | 3.217 | 2.917 | 3.917 | 3.600 | 1.250 |
| count / points | 4.550 | 1.950 | 5.267 | 2.233 | 1.033 |
| delimiter / null | 3.800 | 3.083 | 4.333 | 3.617 | 1.250 |
| delimiter / points | 4.600 | 2.200 | 5.300 | 2.483 | 1.033 |
| cli-putch / null | 17.967 | 17.950 | 17.967 | 17.967 | 16.167 |
| cli-putch / points | 19.650 | 19.650 | 19.667 | 19.667 | 17.850 |

Direct point completion improves by roughly 2.1–2.4 times. Null completion
improves much less; CLI medians are effectively unchanged. Legacy medians
remain within one clock quantum of their previous values. The ordinary
counted-point total is still about 2.16 times its same-run Legacy median.
Its ExCom totals range from 1.633 to 2.317 s, and completion tails from
83 to 367 ms. Counted-null tails range from 417 to 717 ms.

W9's one browser-off counted-point row completed in 130 clock units (1.083 s)
and 1.097 s on the wire; this suite's median is 268 clock units (2.233 s).
That difference warrants investigating browser/frame-service interaction, but
it is not a matched capture: case ordering, preceding traffic and browser
condition differ. Do not label the difference pure browser/network CPU cost.

## Deadline and gameplay observations

1. Legacy still has zero setup or completion first-wait expirations.
2. ExCom still has **24/24 setup timeouts**. Setup replies eventually arrive
   in 64–98 clock units (533–817 ms), median 66 (550 ms).
3. ExCom completion timeouts fall from **18/24 to 12/24**: all nine direct-null
   rows, one counted-point row and two delimiter-point rows. Byte-point and
   CLI completion queries meet the first wait in all three repetitions.
4. All final replies satisfy the benchmark's extended five-second observation
   bound, which does not repair or waive the ordinary MOS wait contract.
5. The Author's post-suite Legacy typing/load succeeded. This establishes the
   W10 keyboard check; it does not retroactively observe the separate W9 check.
6. [Nurples regression](evidence/stock-drain-full-suite/gameplay-observation.json):
   the Author reports large ExCom hangs after loading the existing game from
   SD. The returned game binary hash is recorded. Hang durations, automatic
   recovery and Escape responsiveness were requested, not assumed. Neither
   a crash nor an eZ80 execution stall is established by this description;
   browser-only presentation stalls remain possible.

## Recommended next investigation

Investigate the P4 frame worker's drawing, sprite and snapshot interaction
under the reported hangs, with a concrete observation separating eZ80 progress
from browser presentation. This is a proposed bounded follow-up, not a new
flash or instrumentation contract.

A local source check identifies a specific place to start:
[`executeFrameWork`](../../../vdp/video/extender/display/p4_display_controller.cpp)
keeps `executing_frame_work_` set through queue draining, `showSprites` and
full-surface snapshot composition. `suspendBackgroundPrimitiveExecution`
waits for that flag to clear. Thus snapshot/sprite work can extend a wait seen
by a caller requesting suspension. The
[task loop](../../../vdp/video/extender/display/p4_frame_service.cpp) also
services pending logical ticks individually after a delay. These are source
relationships, not measured attribution of the Nurples hangs. Determine which
work is occupying the interval before selecting a correction.

Keep the selected stock queue-drain policy; a new drawing budget is not the
proposed remedy. Scanline/region transport, core affinity and game changes
remain unimplemented. W9's measured point-workload improvement remains valid,
but it does not establish a usable gameplay improvement on the current build.
Preserve r07 rollback and r08 evidence; do not promote r08 to qualified.
