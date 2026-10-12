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
