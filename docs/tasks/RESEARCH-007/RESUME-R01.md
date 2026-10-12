# Indexed/PPA rendering comparison — resumption

## Executive summary

Prepare the remaining R07-I04 comparison while fsim owns the bench. Compile a
same-source ordinary-UART RGB888 control and linear-byte/PPA candidate, retain
the accepted pre-parallel r11 rollback, and reuse the existing four finite SCAN
fixtures and resident controls. Tests start only through explicit MOS CLI EXEC.
No board access, deployment, reset, serial opening, SD transfer or invocation is
part of this preparation. Production selection is unchanged.

The earlier r04-only evidence remains valid for its recorded composition but
cannot establish a speedup. It used different EMOS and parallel boot handling;
it must not be the timing baseline for this resumed comparison.

## Fixed experiment

1. The Pi builds both variants from the same committed Extender source and
   dependency lock. Both select P4-PC, automatic HDMI carriers, rolling scanout,
   320 PPA scaling and normal timing hooks. Neither selects parallel boot,
   probe, data-check or ExExt handling. Only the indexed variant selects the
   CLUT backport and linear-byte/PPA renderer. No renderer algorithm changes.
2. The Pi preserves the installed pre-parallel EMOS and whichever mainboard VDP
   fsim hands back. Record exact identities after handover and keep them fixed
   across the two variants. No new EMOS flash or mainboard VDP is required.
3. The P4 renders through HDMI without a browser video subscriber. Browser or
   agent keyboard control remains usable for explicit CLI commands. Record the
   actual subscriber condition; do not infer it from HDMI being selected.
4. The agent preserves current startup and the four active run.cfg files on
   admission. Install only the selected setup-only startup, then boot to CLI.
   The agent verifies actual CLI execution using acknowledged listener
   start/read/EXIT before invoking a test. A ready flag alone is insufficient.
5. Use a new campaign directory under /agents/extender/results. Existing
   executables, assets, unrelated SD content and old results remain intact.
   Verify binaries and resident data against the retained hashes before use.

## Remaining R07-I04 execution order

### R07-I04-A [x] Prepare offline

Compile/validate both full targets; check actual compile definitions, selected
sources and ELF for excluded parallel startup/native coordinator handling.
Verify same-source closure and package four segments per variant plus exact r11
rollback, checking archived bytes. Prepare fresh configs, setup-only startup and
explicit command files. Re-run existing controller/build/timing-unit checks.
Completed: [preparation results](RESUME-PREPARATION-R01.md). Fsim retains the bench.

### R07-I04-B [ ] Establish fresh hardware handover and RGB888 control

After Author bench authorization and fsim handback, read the current local
reservation and installed identities. Preserve startup/config files; verify
actual CLI and foreground listener operation. Flash/independently verify only
four RGB888 control segments with Agon held reset; preserve NVS. Use the safe
joined-control USB opener if capture is needed, before any measured fixture.
Require real keyboard/listener/read/EXIT operation after release. First check a
resident mode20 chart for intact geometry/colours. Stop on unexpected failure;
restore exact r11 if the new control cannot establish a sound baseline.

### R07-I04-C [ ] Collect the mode20 RGB888 baseline

Install mode20 setup-only startup before the separate reset. At the verified
prompt, explicitly EXEC the generated suite20.txt. It runs frozen T03 partial
scroll/no sprites, T07 partial scroll/32 software sprites, T08 static background/
32 software sprites, then T09 deterministic Nurples for3,600 measured updates
with120 warm-up updates. It returns to Legacy and the foreground listener.

Keep raw records and correlated P4 windows. Require exact fixture/config/tag,
complete counts, no abort/fault rows, closed non-overflowed windows and measured
scanout/publication activity. Do not reset or replay on missing progress. Record
preparation, invocation-to-return, collection and restoration durations separately.
The prior candidate windows total about66.2seconds; nominal warm-up adds about
5seconds, excluding asset/SD setup. This is an estimate, not a reset deadline.

### R07-I04-D [ ] Collect the indexed/PPA comparison

With the baseline safely collected and CLI established, flash/verify the indexed
variant with the same reset/NVS policy; keep EMOS/mainboard VDP/wiring fixed.
Repeat actual input/listener admission and mode20 chart. Execute the identical
finite suite with the candidate configs. Require identical per-update state,
phase, actor/projectile counts, map row and RNG trajectory before computing
percentage changes. Preserve any visible flicker/tearing as a failure observation
regardless of valid timing counters. No automatic reset or retries.

### R07-I04-E [ ] Run existing overlay and 320 double-buffer controls

For each variant, invoke the existing16-hardware-sprite case54 in mode20 and
mode136. Its generated plan selects only case54. Use one Space after5seconds
from the positively correlated open window, while the fixture is still active;
missing progress means stop, never send a stray key to a CLI. Save the complete
record and P4 windows. Use the existing colour chart in both modes, retaining
its three10-second windows and an explicit Escape only after confirming the
chart remains active. No frozen executable changes or mode switches in fixtures.
Mode136 is320x240 logical double buffering on the existing scaled480-line carrier.

These controls need separate explicit EXEC commands. Startup selects the mode
before reset; no test command is ever installed in /autoexec.txt. The maintained
static-conversion analysis can decode collected windows offline; do not invoke
its old live autoexec/reset runner. Likewise do not call the old finite_suite.py
stage, controls.py hardware/chart, or qualification Bench.run/startup launch
paths. Their --check modes are offline hashes only; historical launchers remain
frozen evidence, not this experiment's entry points.

### R07-I04-F [ ] Report matched results and stage Author Nurples review

Show worst isolated case first by p95 fenced completion. Show both variants
side by side, milliseconds and percentage of the16.667ms/1,200-count60Hz budget,
and percentage reduction100*(RGB888-indexed)/RGB888 for lower-is-better costs.
Report active work/headroom, late streaks and game-loop rate separately from
P4 row/snapshot work, whole-image PPA expansion, cache handoff, background
publications and DMA cadence. For higher-is-better rates explicitly use
100*(indexed-RGB888)/RGB888. Do not add overlapping wall scopes as CPU load.

Verify mode0 upper text/outro and ordinary CLI/input after the comparison.
Restore saved startup/config bytes and verify readbacks. On regression restore
r11 and leave a working CLI. If bounded checks pass, leave the indexed image
and current regular Nurples ready for Author input/flicker review under R07-I05.
Counters and synthetic key polling do not establish human responsiveness or
visual acceptance. No production promotion/tag is implied by preparation.

## Retained evidence and operational limits

Local commands, build logs, manifests, deployment archives and package index
belong in the ignored task workspace. Tracked preparation results contain exact
public build/source/artifact hashes and outcomes, without private endpoints.
Future physical results must identify actual installed bytes and the startup/
fixture configuration used. The canonical CLI test-execution, rollback, serial
capture, bench constraints and SD layout procedures control execution.

## Execution correction — mode ownership

The first RGB888 chart invocation stopped before any measurement: startup had
selected mode20 on mainboard in Legacy, and ordinary EMOS EXCOM then reset P4
to mode0. The frozen chart correctly rejected the wrong mode with return1,
which MOS displayed as “Error accessing SD card”; the chart performs no SD I/O.
This was a host setup error, not evidence of a renderer or SD defect.

Corrected setup-only startup selects EMOS EXCOM before VDU22 on P4. Every
separate test batch enters with `EMOS EXCOM --keep-display`, preserving that
mode after the foreground listener's Legacy exchange. No executable fixture or
firmware changes. The corrected campaign uses fresh result paths/tags; retain
the original startup/config bytes and stop on any new unexpected result.

## Initial r12 physical stop — intermittent RGB888 display loss

Corrected mode20 chart completed three windows. P4 counters reported roughly
60.07 DMA completions/s, with zero recorded rolling faults/underruns. Author
initially reported correct appearance, then withdrew that visual pass after
repeated off/on display loss. These counters do not measure monitor lock or
prove continuously visible HDMI output. Candidate indexed/PPA is not installed.

The agent had already submitted the finite baseline-suite EXEC immediately
before the visual correction arrived. Its keyboard journal completed; the host
monitor was stopped without further device input, reset, retrieval or retry.
A subsequent read-only SD status confirms that the foreground listener returned. The complete finite-suite records still need retrieval and validation; listener return alone does not establish their contents.
EMOS and handed-back mainboard VDP remain unchanged. Preserve the installed
RGB888 r12/control configuration pending diagnosis or Author-directed recovery.
R07-I04-B visual stability is failed; remaining comparison stages are blocked.


## R07-I04-B transient display-loss investigation — authorized 2026-10-12

B01 [x] Preserve the installed r12 control and obtain bounded passive P4 serial
and read-only status evidence before changing anything. No reset, panic,
rolling fault, underrun or missed sequence appears in the retained50-second
capture. This does not prove continuous HDMI/monitor lock; the available
counters observe P4 DMA, not the receiver's displayed image.

B02 [x] Retrieve and validate the completed finite r12 suite through its
positively observed foreground listener. Preserve the Author's observations:
Nurples looked good while running, but the HDMI picture briefly disappeared
and returned. Timing records cannot overrule that visual failure.

B03 [x] Install the exact retained working r11 P4 as a one-component control,
with independent segment verification, NVS retained and setup-only startup.
Preserve EMOS, mainboard VDP, monitor, wiring and chart executable. Verify actual
CLI/listener/read/EXIT, then explicitly launch the same mode20 static chart.
Collect its bounded output logs and leave the picture steady for Author review.
No indexed candidate, new timing tuple or speculative bridge register change.

B04 [x] Stop for the Author's observation of whether the brief dropout also
occurs on r11. The Author initially saw no blink, then reported one brief off/on
event; the older control therefore fails visual stability too. The failure
exists without the r12 renderer changes.
Absence of a transient in one short run is not proof of repair. If necessary,
next instrumentation should distinguish P4 progress, bridge MIPI/clock state
and hot-plug status; it must not reset/relock the bridge and mask the symptom.

Source comparison: r11 source8800ca84577410d5b4a9d70fbd830c10624fc326 plus
its retained dirty-source archive versus clean r12
source26660db54ca0ff0621cc7822b985092933a636e5. The r11 archive and input hashes,
not its Git commit alone, identify its actual PPA320 code. HDMI timing tuples and vendored
LT8912B driver are unchanged. DDS thresholds or receiver-settle changes from
unrelated vendor examples are hypotheses, not established corrections. The
Linux [LT8912B driver](https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/bridge/lontium-lt8912b.c)
and the pinned vendor driver both interpret main-bank0xc1 bit7 as hot-plug;
neither makes this a monitor-lock indicator. Preserve that distinction in any
subsequent diagnostic. Existing rolling timing does not report HDMI-side lock.

[Transient display-loss findings](HDMI-DROPOUT-R01.md) retain the code comparison, validated r12 records and limits.

Exact r11 control installation and actual CLI/listener/read/EXIT pass. Its mode20
static chart completed three windows at60.074Hz DMA cadence with no recorded
rolling faults. The Author subsequently observed one transient off/on event,
so r11 also fails the visual stability gate. That control's passive capture is
closed; B07 below supersedes its installed state. No correction is established.

B05 [x] Confirm the physical display connections before changing software.
The Author confirms the external MIPI LCD ribbon is removed. Exclude loading
from an attached second DSI receiver. The Author has seen no further blink
since the previous notification; preserve the one earlier r11 dropout without
claiming a formal rate comparison or repair. Bench remains unchanged.

B06 [x] Prepare a default-off HDMI link observer in the full RGB888 control.
The P4 records maximum DMA frame-callback gaps and gaps over25ms. In the
existing joined output task, at most ten times per second, read only the
LT8912B's existing HPD, MIPI-input and DDS diagnostic registers. Log raw values,
sample duration, output epoch and scanout progress; HPD is not image lock.
Use bounded I2C transactions and disable observation after a read failure;
never reset/relock the bridge or change its registers to hide a failure.
The observer does not alter timing, transport, drawing, EMOS or mainboard VDP.
Build selection and validation must reject accidental observer inclusion in
ordinary builds. Preserve exact uninstrumented r11/r12 artifacts. Compile/link
and verify the observer's full image before selecting it for a physical run;
instrumented measurements are not a renderer performance comparison.

The full observer build `rgb-001-r12-b2026-10-12-12-00-47Z` compiles, links,
passes native action validation and verifies its frozen source closure. Its
manifest explicitly records `hdmi_link_watch=true` and all indexed/parallel
selections false. App SHA256
`0452b9680090f6cba60f1a03fc431b983109bca25c1197aaf19d71ce6e2f2396`;
1,738,864bytes. Fifteen HDMI build-selection tests pass. This is an explicitly
instrumented new r12 build, not the earlier uninstrumented control's bytes.

B07 [x] After B06's full build validates, install only the observer P4 image,
independently verify its four immutable flash segments and preserve NVS. Retain
EMOS, mainboard VDP, setup-only startup, chart, monitor and wiring. Escape the
known held chart once, require its foreground listener return, verify startup,
then install with Agon held reset until P4 initialization completes. Verify an
actual CLI/listener/read/EXIT exchange before explicitly invoking the same
mode20 chart. Save bounded passive P4 serial history and correlate its output
epoch, callback gaps and raw bridge readings for subsequent visual correlation.
Stop on unexpected admission, read or output failure; no automatic recovery,
relock, indexed comparison or performance claim.

Four segments independently verify; NVS, startup and the other processors are
preserved. Actual CLI/listener/read/EXIT passes. Explicit CLI EXEC starts the
same mode20 chart and its three windows close normally. The120-second passive
trace contains1,031 bridge samples,60.069Hz DMA cadence, maximum callback gap
16,781us, no gaps over25ms, no HPD changes and no captured errors. Raw bridge
values are retained without claiming image lock. Capture closed; chart remains
running on the observer image.

B08 [x] Obtain the Author's observation of any off/on since the observer chart
returned. Correlate reported events with retained trace time where possible;
do not claim a repair from a quiet interval. Pause after asking, before further
hardware operations or selecting a new investigation branch.

The Author reports no observed blink on the observer image. No repair is
claimed; the diagnostic reads add workload and the older control also had
quiet intervals. The subsequent explicit authorization below permits timing
collection with the fault still unresolved.

## Author-directed performance tranche — 2026-10-12

The Author reports no observed blink on the read-only observer and authorizes
the four-workload RGB888/indexed comparison now, leaving intermittent HDMI loss
unresolved. This explicitly releases the prior visual-stability stop for timing
collection only; it does not accept either control as repaired. Use the exact
uninstrumented same-source builds already prepared, fresh result paths and
the frozen T03/T07/T08/T09 executables. Remove the observer by installing the
verified RGB888 control first. Preserve EMOS/mainboard VDP and setup-only mode
selection. No additional overlay/mode controls in this tranche. Collect both
variants, verify deterministic equality and report separated timing scopes.
On an unexpected failure stop and request a higher thinking level; do not
investigate, replay or add a speculative correction in this light-thinking run.


### Performance tranche checkpoint — paused on host harness ownership

Fresh campaign r07-20261012-uart-r03 RGB888 control has four complete validated
records and closed P4 windows. All four application rates are60updates/s;
Nurples median active work is42.67% of the60Hz budget, p95 52.92%. Invocation
to returned listener100.809s; collection59.128s. Passive capture is closed.

The indexed candidate independently verifies four segments and passes actual
CLI/listener/read/EXIT. A pre-chart host helper then retained one foreground
client while constructing a second client on its locked state file. The host
rejected that duplicate before any chart or finite-suite invocation. No candidate
performance result or firmware defect is established. Last observed state is
the foreground listener, with candidate installed and setup-only startup retained.
No retry, reset or additional investigation: pause for a thinking-level change
as agreed with the Author. This ordinary harness mistake needs only this brief
corrective note, not a firmware bug entry or large failure capture.

## Indexed candidate visual stop — 2026-10-12

Author reports substantial Nurples flicker on indexed/PPA r05, and recalls an earlier version looked perfect. Treat candidate as visual regression, not accepted sprite limitation. No root cause established. Direct single-client chart invocation succeeded; all three chart windows closed and explicit Escape returned listener. Candidate suite completed enough to return listener; T03/T07/T08 downloaded and validated. Host collection interrupted on visual failure while downloading T09; its session journal may retain a pending read. Passive collector closed, no test/reset/flash/restore/retry afterward. Last observed application state foreground listener online in Legacy. Candidate remains installed, temporary63B startup and r03 candidate configs remain. Baseline complete. Do not claim complete paired comparison or visual pass. Resume must resolve the existing SD session journal before another client operation; do not create a new session or restart listener blindly.

## Matched data recovery complete — 2026-10-12

All four candidate records recovered through the existing foreground SD session. Exact pending READ resolved first; no new listener/session, firmware, reset, rerun or configuration change. Complete120/120/120/3600 records and tagged closed/nonoverflowed P4 windows validate; trajectories match RGB888. Nurples application60updates/s both, background publication60.07/s RGB888 versus30.14/s indexed (49.8% lower); scrolling/32-sprite fixture60 versus53.33updates/s and74.1% higher p95 fenced cost. Author-observed substantial sprite flicker means candidate fails visual acceptance. No root cause/fix established. RGB888 baseline valid; intermittent common HDMI dropout remains open. Foreground listener remains online in Legacy, candidate r05 installed, temporary63B setup-only startup and r03 candidate configs unchanged; no pending session read, collectors closed. Paired report [paired results](RESUME-COMPARISON-2026-10-12.md). No promotion, commit or further tests.
