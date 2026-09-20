# BENCH-007 — Reusable paired game timing package

## Executive summary

Author authorizes contract freeze, implementation and physical qualification of
an official reusable test package for mainboard ESP32 VDP and P4 EDP, including
firmware deployment and bench control. First change production Aginvadors to
one-vblank 60-Hz pacing without gameplay retuning. Then create isolated timing
variants of Aginvadors, current repair-based Nurples and current Rally. Measure
both eZ80 work/wait and renderer completion; retain clocks/scopes separately.
No further user question is presently required. Goal tracking is active.

## Frozen work contract — 2026-09-20

1. Record exact game, compiler, EMOS, VDP and P4 source/build identities and
   preserve existing unrelated work. Official source references remain read-only;
   mainboard diagnostic builds use project-owned exported copies. Preserve actual
   installed firmware and startup before deployment. Existing recovery protocols,
   stable device identities and bench constraints apply. No experimental push.
2. Production Aginvadors: replace its centisecond 50-Hz pacing with the ordinary
   one-vblank mechanism used by Nurples. Keep movement/timer constants unchanged;
   the expected nominal 20% speedup is intentional. Build and test production
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

1. [ ] T01 — Source/ABI/baseline précis and exact implementation layout.
2. [ ] T02 — Production Aginvadors vblank pacing, build and validation.
3. [ ] T03 — Shared timing recorder, completion protocol and host tests.
4. [ ] T04 — Bounded game variants and common acquisition/analysis tools.
5. [ ] T05 — Paired diagnostic builds, rollback preservation and hardware controls.
6. [ ] T06 — Three-game paired runs, durable comparison and restoration.
7. [ ] T07 — Promote reusable documentation, evidence and review closeout.

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
