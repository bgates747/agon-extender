# BENCH-007 — Reusable paired game timing package

## Executive summary

The reusable paired timing package and its scoped hardware results are complete
and committed under PLAN-001-T01 closeout. Browser streaming was idle during
measurements; these results do not qualify browser delivery or physical scanout.
Original mainboard/P4 firmware restoration and usable CLI/input were recorded.
Artifact status remains experimental. The original execution goal is complete.
Aginvadors optimization is deferred; unresolved findings below remain explicit.

## Frozen work contract — 2026-09-20

1. Record exact game, compiler, EMOS, VDP and P4 source/build identities and
   preserve existing unrelated work. Official source references remain read-only;
   mainboard diagnostic builds use project-owned exported copies. Preserve actual
   installed firmware and startup before deployment. Existing recovery protocols,
   stable device identities and bench constraints apply. No experimental push.
2. Production Aginvadors: replace its two-clock-tick pacing with the ordinary
   one-vblank mechanism used by Nurples. Keep movement/timer constants unchanged;
   any actual cadence change requires measurement (see precision-timer correction
   below). Build and test production
   changes separately; do not put scripted controls, invulnerability, timers or
   telemetry into the default game. Preserve unrelated Pynvaders/Joust changes.
3. Promote reusable timing authority to role-named package locations independent
   of task IDs (documentation, common recorder/protocol, eZ80 client helpers,
   host collection/analyzer and tests). Keep this task as evidence/contract owner.
   Reuse the existing QUAL-003 GraphicsFence implementation and admission rules.
   The protocol is a project testing interface, not an upstream VDU allocation
   or a general production callback API. It must fail explicitly on unsupported
   diagnostic firmware, timeout, overflow or mismatched session/frame identity.
4. Mark one complete application's drawing submission per game update, not every
   primitive. Start/read-lap/stop records use ESP monotonic microseconds and
   ordered drawing completion. Define parser-observed versus worker-completed
   timestamps separately. A queued end marker must not claim completion merely
   when UART receives it or the queue becomes empty. Never force drawing from
   the parser, remove locks, change core affinity/priorities or add drawing budgets.
5. Renderer completion means preceding submitted primitive work and the retained
   software-sprite completion boundary, not physical VGA/HDMI scanout, browser
   presentation or all future scanline sprite decoration. Reuse original backend
   operations. Publish any unavoidable boundary limitations prominently.
6. Buffer a bounded set of records in RAM; no per-frame serial formatting or SD
   writes in timed sections. Export after capture, including a serial-readable
   report where the board's established programming/data interface supports it.
   Existing admitted diagnostic replies may support common retrieval through
   EMOS. Do not start competing UART readers or confuse P4 native USB with UART0.
7. eZ80 variants record game logic/input, VDU submission (including transport
   backpressure), explicit vblank/pacing wait, and overall update intervals.
   Preserve raw units and calibration. Do not subtract clocks across processors
   or add overlapping intervals as independent CPU costs. Include instrumentation
   overhead controls and disclose behavior altered by a completion fence.
8. Test-owned game copies live under /test on Agon and isolated project staging
   locally. Pin finite run length, seed and input; disable collision damage where
   needed for comparable runs while still polling keyboard. Preserve production
   files/high scores. Select fixture video modes through startup/CLI before entry;
   benchmark derivatives suppress internal mode switching. Nurples at512×384,
   Aginvadors at320×240; confirm Rally's actual configuration before naming it.
9. Qualify parser/recorder/fence bounds with host tests and simple empty/known-work
   hardware controls before running games. Execute all three on mainboard VDP and
   P4 EDP with browser streaming disabled for the primary rendering baseline.
   Browser 30/60 pacing comparisons remain a distinct subsequent experiment;
   no measured baseline is to be labelled browser throughput or monitor refresh.
10. Preserve supported USB keyboard input throughout installation/recovery. Bound
    each run from known duration plus justified preparation/exit margins; no
    reset loops. Stop and preserve informative failures rather than force a pass.
    Restore ordinary firmware/startup and a verified usable CLI after temporary
    diagnostics; retained diagnostic images remain reproducible for future tests.
11. Report worst cases first in side-by-side tables with explicit units, baseline,
    percent difference and exclusions. Save fixture start/end duration for future
    estimates. Human gameplay balance is not an automated timing acceptance claim.
    No hardware/emulator attention cue requested; desktop app notification suffices.

## Work items

1. [x] T01 — Source/ABI/baseline précis and exact implementation layout.
2. [x] T02 — Production Aginvadors vblank pacing, build and validation.
3. [x] T03 — Shared timing recorder, completion protocol and host tests.
4. [x] T04 — Bounded game variants and common acquisition/analysis tools.
5. [x] T05 — Paired diagnostic builds, rollback preservation and hardware controls.
6. [x] T06 — Three-game paired runs, durable comparison and restoration.
7. [x] T07 — Promote reusable documentation, evidence and review closeout.

## Initial research anchors

1. Official docs: vdp/Screen-Modes.md describes VDU23,0,C3 swap/vsync;
   MOS API/sysvars define eZ80 clock and output. Verify chosen toolchain's actual
   vblank implementation before production pacing changes.
2. Existing `docs/tasks/QUAL-003/timing/protocol.md` and
   `vdp/video/extender/diagnostics/{graphics_timing.hpp,graphics_command.inc}`:
   GraphicsFence126, normal worker completion after showSprites; private EF
   requests and8C replies with bounded token/source checks. Preserve existing
   clients or version a distinct testing operation rather than silently replace.
3. `docs/tasks/QUAL-003/mode-transition/AGENT-QUESTIONS.md` records previous
   instrumentation perturbation, rejected scheduling experiments and distinctions
   between application pace and output delivery. No repeated priority remedies.
4. `docs/tasks/QUAL-003/mode-transition/AGINVADORS.md` pins the current binary,
   mode8 and intended50-Hz loop. Current game source is read from its owning repo;
   do not substitute the unrelated original arcade Space Invaders disassembly.

## Authorization boundary

Author explicitly authorizes production Aginvadors timing change, test variants
of all three games, diagnostic mainboard/P4 firmware and physical bench tests.
Standing identity approval applies. Human emulator validation applies only if
an emulator artifact is changed; no emulator alteration is required by this
contract. Product feature additions, game balance retuning, upstream bug fixes,
new rendering algorithms and unrelated browser work remain outside scope.

## Author clarification — active loop versus pacing

Primary per-update eZ80 fields must include active_elapsed (loop entry through
all logic/input/drawing submission immediately before intentional pacing),
pacing_elapsed (entry to exit of that wait), and total_elapsed. Subintervals
for logic/input and submission are secondary explanations. Active elapsed is
wall time and can include UART backpressure, interrupts and synchronization;
it is not exclusive CPU execution. Clearly report its distribution and fraction
of total update time, including updates that miss their nominal60-Hz deadline.
Do not hide rendering-fence wait inside game logic or conflate it with the
application's ordinary pacing wait. This clarification is authorized by the
Author during preparation and governs all three fixtures.

## Implementation précis and limits

1. Official mainboard source is VDP2.16.0 at
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, with vdp-gl
   `ac2dd5986daf496c43ae8e7fe41836274aec54a0`. The diagnostic build exports
   those commits; official reference trees remain untouched. It retains the
   existing normal-worker GraphicsFence and software-sprite completion boundary.
2. AgonDev's `mos_waitvblank.src` waits for the MOS sysvar clock to change.
   Production Aginvadors now uses that operation once per update. Constants
   remain unchanged; its normal build and sanitizer-backed simulation test pass.
3. The batch extension uses private EF operations5–10, retaining1–4. Successful
   begin/end commands have no reverse-UART reply. ESP RAM holds240 records;
   initial game cohorts contain120 updates. Stop/read occurs after the hot loop.
   Mainboard diagnostic serial export uses the existing `force_debug_log` path;
   this avoids assuming ordinary C stdio has the same console binding.
4. Primary host phase timing is PRT1 elapsed counts. MOS raw-clock elapsed
   time, nominal120 ticks/s but published at vblank boundaries, cross-checks the
   total run only. ESP timestamps retain
   microseconds in their own clock domain. No cross-clock subtraction.
5. Nurples interleaves game logic and VDU output throughout `do_game`. Its test
   records the combined active duration and pacing separately. It does not
   manufacture a logic-versus-output split. The test retains MOS keyboard-map
   polling, substitutes a private neutral map, disables joystick and damage,
   suppresses confirmations and mode changes, and captures after initialization.
6. Rally retains its four-raw-tick pacing target (nominal30 updates/s), ordinary
   attract driver and full keyboard-map polling. Its test moves the existing
   deadline wait to the end of the measured iteration so active and pacing are
   contiguous; the same next-deadline rule is retained. Test save I/O is disabled.
7. Diagnostic fences can affect natural pipelining. Empty/drawing controls and
   a no-marker eZ80 pacing control are required before interpretation. Results and controls are now retained in [RESULTS.md](BENCH-007/RESULTS.md);
   their scopes do not establish browser performance or physical scanout timing.

## Precision timer refinement — Author requested during implementation

1. Primary eZ80 timing now uses PRT1, following the register definitions and
   low-level approach in the current Nurples `timer.inc`. The old helper's
   interrupt-driven centisecond counter is not precise enough for these phases;
   the fixture reads the downcounter directly. It neither replaces interrupt
   vectors nor adds a timer ISR. EMOS/I2C and AgonDev delay use PRT0, left intact.
2. AgonDev inspected at `b67ab2444a63267a42193f204889d466765d8dd2`:
   `src/lib/libtimer/timer.c` implements `delay(ms)` with repeated PRT0
   single-pass countdowns, /16, and a19-count software-loop compensation.
   `src/lib/libc/clock.src` jumps to `mos_getsysvar_time.src`, returning raw
   MOS ticks. Its header declares CLOCKS_PER_SEC100 without conversion here.
   Therefore the earlier claim that Aginvadors necessarily ran at50Hz, or that
   the pacing change necessarily gives20% speedup, is withdrawn pending physical
   comparison. One-vblank production pacing remains the Author's requested form.
3. PRT1 must be disabled and select the system clock before admission. The
   fixture does not change the shared timer source selector. It uses single-pass
   /16, reload65535: nominal1,152,000 counts/s (0.868us/count) at18.432MHz.
   One shot per update avoids undetected wrapping; exhausted65535-count records
   are explicitly marked, never interpreted as short frames. Maximum unsaturated
   interval is approximately56.89ms. Disable PRT1 at completion; no timer ISR.
4. Zilog eZ80F92 product specification PS0153, Programmable Reload Timers and
   Timer Data Registers, requires low-byte then latched high-byte reads:
   https://www.zilog.com/docs/ez80acclaim/ps0153.pdf . PRT control qualification
   compares120 vblank waits, immediate read overhead, AgonDev10/30ms delays and
   deliberate100ms saturation before any game result is accepted.
5. Keep MOS raw ticks as a coarse independent duration check. Primary exported
   fields are active_prt, logic_prt, submit_prt, pacing_prt, total_prt, overflow
   and mos_ticks. The earlier raw-MOS-only variants are superseded before runs.
   Nurples moves bookkeeping/keyboard checks ahead of its pacing wait in the
   isolated derivative so the active window includes the complete iteration.

## First physical control — PRT1

At divider16,120 consecutive vblank controls each produced approximately19,210
counts against nominal19,200 for60Hz. Immediate read returned2 counts. AgonDev
10ms and30ms delays returned11,379 and34,124 counts; these software-compensated
delays are cross-checks, not an independent calibrated timebase. A100ms delay
saturated at65,535 as required. Actual raw controls and validation receipt are
retained in the local BENCH-007 evidence bundle. No mainboard/P4 firmware flash
was necessary for this PRT check; normal keyboard and SD service still function.

## Diagnostic build guard

The first P4 capability control found that the preserved console configuration
omitted AGON_GRAPHICS_TIMING. No game was admitted. The P4 builder now enables
that existing flag explicitly and verifies the timing dump marker is present in
the linked image before deployment. The corrected image must repeat the same
protocol/empty controls; the omitted-flag attempt is not performance evidence.
Mainboard protocol controls passed all four checks, and its120 post-capture
serial records exactly match the SD reply records.

## Hardware continuation — range and transition findings

1. The /16 PRT control and all four protocol rejection checks passed on both
   processors; SD records exactly match post-run programming-console dumps.
   Known rectangle controls reach60 updates/s on both routes with video idle.
2. Rally exceeded the56.9ms range in81/120 P4 and120/120 mainboard unmarked rows.
   These elapsed aggregates are unavailable, not short or zero. Repeat Rally
   with /64 (288,000 counts/s,3.472us resolution,227.55ms range); retain /16
   evidence as an informative range-control result. No ISR or rendering change.
3. Mainboard marked Nurples run panicked with heap corruption and LoadProhibited
   in stock VGAPalettedController::drawSpriteScanLine, after prior game/mode
   transitions. Attribution to timing fences versus transition lifetime is open.
   Preserve the console trace and exclude this run from performance conclusions.
   One normal Agon reset recovered verified CLI/input; no upstream fix applied.
4. MOS SAVE refuses an existing raw output: use unique per-run output paths.
   The completed P4 unmarked Nurples RAM was saved at its verified final prompt;
   host runtime was not retained, but all120 raw rows remain valid.

5. Rally's retained production logic advances physics by elapsed MOS ticks before
   each rendered update. Its attract driver is deterministic for a given tick
   sequence, but the two processors do not necessarily see identical scenes at
   the same update number. Report the120-update live-game measurements as such;
   do not label their percentage difference a pixel-identical backend speedup.
   Aginvadors and Nurples use per-update progression. A fixed-physics-tick Rally
   replay would be a distinct workload, not an unreported tweak to this cohort.

## Review checkpoint

The implementation authority is [the reusable package](../testing/game-timing.md).
Paired raw records, clock controls, timing tables and limitations are in
[BENCH-007/RESULTS.md](BENCH-007/RESULTS.md). The original mainboard panic and
fresh-boot success are both retained. No upstream bug fix or scheduling change
was made. The stable qualified invocation for future mainboard sprite timing
starts from a fresh boot; sequential mode/sprite lifetime remains unresolved.

Remaining review items:

1. Author review of scoped timing results and production Aginvadors pacing.
2. Separate follow-up diagnosis of the mainboard sequential-run sprite panic;
   do not silently expand this measurement implementation into an upstream fix.
3. If pixel-identical Rally comparison is wanted, specify fixed physics ticks
   and exact replay inputs as a new cohort before interpreting backend ratios.

## Restoration complete

Original mainboard4MiB and original P4 prefix independently verified. The only
non-application mainboard difference was the diagnostic panic's core-dump
partition; it was preserved before restoring the saved bytes. EMOS and root
startup remain unchanged. Final admitted CLI marker, ExCom root prompt, neutral
ready input and exited SD service were verified. No serial readers or agent
video observer remain. Implementation is ready for Author review; no push.

## PLAN-001-T01 closeout — 2026-09-20

**BENCH-007-C01** [x] Rechecked four analyzer tests, ASan/UBSan recorder controls,
85 retained evidence hashes, 18 CSV validations and 12 exact serial comparisons.

**BENCH-007-C02** [x] Reviewed recorded restoration: mainboard full-flash hash,
P4 original image verification, unchanged startup/EMOS and final CLI/input state.
These are retained run receipts, not a new hardware test today.

**BENCH-007-C03** [x] Committed reusable package separately from evidence.
Extender package: `ba9dd47f`. Production Aginvadors one-vblank pacing and its
notes: Pynvaders `7321a0f`. Normal game build and sanitizer-backed host simulation
pass. No new production optimization, gameplay retuning, emulator change or push.
Unrelated browser/Joust work remains uncommitted; agon-emos has no local changes.

### Unresolved findings retained for queue disposition

**BENCH-007-F01** [ ] Diagnose the mainboard sequential-run sprite/heap panic
if separately authorized. Preserve `results/mainboard-panic.txt`; the fresh-boot
retry passing does not resolve the cause. No upstream fix is implied.

**BENCH-007-F02** [ ] Reconcile the Rally timing fixture with ordinary gameplay
before making general performance claims. The elapsed-time physics and different
scenes prevent treating the paired runs as an identical-work rendering comparison.
No new benchmark is authorized by this closeout.

PLAN-001-T02 will retain or rehome these follow-ups without losing their evidence.
Aginvadors performance work is deferred by PLAN-001 D01, not an unfinished step
of the now-complete measurement implementation.

## Firmware bug register cross-reference — 2026-09-20

[FWBUG-002](../firmware-bugs.md#fwbug-002). These stable bug identities supplement the original
finding IDs and evidence. Registration does not authorize repairs or turn
source-only findings into hardware reproductions. Use the same FWBUG ID for
any future dedicated disposal task; current dispositions remain in the register.
