# Paired graphics and Nurples benchmark contract

Current execution amendment: [framebuffer-first hardware pass](timing/framebuffer-pass.md). The Author resumed hardware testing on 2026-09-13, with the failed sprite sequence excluded and no P4 video output during this pass.

Status: **finite graphics benchmark preparation reactivated by the Author,
2026-09-11**. Owning task: [QUAL-003](../QUAL-003.md). The stock-backend audit
and R1/R2 restoration are complete; r10 is deployed and qualitatively improved.
This is the next requested measurement tranche. Typing-latency instrumentation
is not the current increment. Automated Nurples gameplay is deferred until
the finite graphics results are reviewed, provisionally the following session.
No performance repair or upstream bug fix is included.

## Current tranche — supersedes the earlier full-suite/game execution order

1. Use the [curated case inventory](curated-timing-cases.json): Shapes pages
   20/23 and Bitmaps pages 3/7/21/22/25/26/27/29/30. Preserve every stage and
   prerequisite within each selected page. In particular, BSP-30 varies
   1/2/4/8/16 sprites, software/hardware ownership, RGBA2222/RGBA8888, scanline
   alignment and frame size. These target the remaining sprite-heavy slowdown.
2. Include the empty-marker control and finite scrolling, one-row clipped
   bitmap and combined cases already specified below. These are small graphics
   batches; do not modify or automate the Nurples game in this tranche.
3. Prepare equivalent bounded timing hooks in a project-owned copy of stock
   mainboard VDP and restored P4 EDP, with EMOS-owned event reception. The
   existing Pingo notification supplies the correlation/mailbox precedent,
   not a ready-made ordinary-2D completion hook. Exact diagnostic carrier, hook
   locations, image-space check and rollback inputs remain B1 implementation
   preparation; they are not yet built or hardware-qualified.
4. Time submission, renderer-local work/completion and result delivery as
   distinct intervals. Measure recurring sprite/output work separately from
   a finite drawing-queue drain; a quick drain does not prove cheap hardware
   sprites. Exclude setup/SD I/O/probes/deliberate settling from drawing
   intervals and report their failures. Retain controls for instrumentation
   overhead and coarse eZ80 clock resolution.
5. Run mainboard first and EDP second, repeat three paired passes, and persist
   per-case results on Agon SD. Local validation and the existing required
   Author emulator review precede physical firmware changes. Preserve and
   restore the actual ordinary mainboard/P4/EMOS images. No screenshots or
   per-stage keypresses should be required to collect physical results.
6. Use those findings to decide whether the deferred deterministic Nurples
   run is needed next. The retained game requirements and unresolved D004
   input-pattern choice below apply only to that later tranche. The broader
   production generalized-callback ABI under D003 also remains separate.

Current baseline: P4 `uart-excom-console-r10-b2026-09-11-03-37-54Z` from
`f0dc271`, EMOS `agon-emos-v0.1.12-b2026-09-10-03-50-35Z`, and the selected
stock VDP release below. The Author reports marked ExCom improvement but
residual jerkiness/sprite-heavy slowdown, smooth Legacy gameplay with the
**same already-loaded binary**, and improved typing with slight remaining
latency. These are qualitative observations, not measured attribution.

The remainder retains the broader benchmark design and deferred game scope.
Where its whole-tour/minute-game instructions conflict with this tranche,
this section governs. No firmware, emulator, SD or running-board changes were
made while reactivating and curating this contract.

## Question this experiment answers

Compare the same application workloads through EMOS to mainboard VDP in Legacy
and P4 EDP in ExCom. Distinguish time spent submitting commands, executing
drawing, waiting for completion, and publishing a visible frame. Measure the
real scrolling/clipped-bitmap workload as well as finite graphics cases; a
completion barrier between every game draw would alter the problem under test.

## Source selection and existing evidence

1. The Author identifies **nurples-repair** as the modern game checkout. It is
   currently on `dev`, commit `4a52199870f5177d8fd65622566725418364ef84`, including
   the accepted optional-joystick change. The older `nurples` checkout is not
   the benchmark source. Use a task-local source snapshot and explicit patch
   from the selected repair commit; preserve its unrelated ongoing work.
2. The game executable recorded for the AUDIT-006 hang capture exactly matches
   `nurples-repair`'s current `tgt/nurples.bin` and its committed binary:
   `63c89d2676f6645631b2240f23002b8b68d45069979a4804ca7d14f34e720088`.
   The recorded `game.agnb` and `ui.agnb` also match that commit, respectively
   `b5e27f3f36ee9f25fe69fb35b3294c1268af1610f53327386fac6ae0055af823` and
   `d16b74171130fd72eff4dffd8485408aee1a1d356ce6df6e00bd9bb5742a0780`.
   These hangs were therefore observed with the repaired game, not the older
   checkout's known non-working development state.
3. The repair worktree has uncommitted artwork, asset-generation and deployment
   changes. Its current containers differ from the installed containers, while
   its executable remains identical. For continuity, select the committed
   assets above for the first benchmark and use identical files on both routes.
   Do not rebuild or absorb ongoing artwork changes incidentally.
4. Shapes/Bitmaps use this task's existing vendored source and provenance:
   24 Shapes pages and 32 Bitmaps pages comprising 123 stages. Preserve their
   known reference disagreements and staged sprite/resource behavior.
5. Retain the selected official reference sources: MOS v3.0.2
   `8336409351ee5314e02801a7b72a4f1bb5282519`, VDP v2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, documentation
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, and retained vdp-gl
   `ac2dd5986daf496c43ae8e7fe41836274aec54a0`. Official checkouts stay read-only.

## Bounded Nurples code review

The following are source observations and hypotheses, **not measured rankings
of individual rendering costs**. Relative source links identify the repair
checkout; the selected commit above governs if that checkout later changes.

| Path | Source observation | Measurement consequence |
|---|---|---|
| [tiles.inc][tiles], `tiles_scroll_background` | Each playing iteration scrolls the 256×336 playing field down one pixel, then sets an inclusive one-pixel-high graphics viewport. | Measure scrolling separately from drawing the newly exposed line. |
| [tiles.inc][tiles], `tiles_plot` / `bg_plot` | Each iteration selects/draws one background bitmap and all 16 tile columns; tile Y advances from −15 through 0 before the next source row. Full bitmap commands rely on clipping to produce one scanline. | Check clipping, negative coordinates, origin and transparency, then time identical command batches. Do not replace this algorithm before measuring it. |
| Historical [P4 controller][p4], `VScroll` / `rawCopyRow` | Before restoration, P4 used generic per-pixel copy/fill. This controller is excluded from current r10. | Historical audit evidence only; do not attribute current slowdown to this removed path. |
| [Retained VGA64 controller][vga64], `VScroll` | Mainboard and restored r10 now both use the original row-pointer/row-swap implementation. P4 adds the reviewed execution/output binding. | Measure current behavior and binding costs; the earlier algorithm difference has been removed. |
| [Viewport context][viewport] and [bitmap clipping][bitmap] | The retained viewport validator permits equal Y endpoints. Bitmap clipping reduces the source/destination height before the native bitmap call. r10 now selects the original depth-class implementation. | No obvious single-scanline rejection found. A correctness test must establish actual behavior; a source scan is insufficient to dismiss the Author's hypothesis. |
| [Game loop][game], [playing state][playing] | `timestamp_tick`, game work, then a bounded wait for a mainboard sysvar-clock change. Scrolling and most movement advance per loop; game work includes tiles, player/weapons, enemies, explosions, active tiles and UI. | Record completed loops and clock time separately. A slow renderer can reduce game updates; a slow publisher can hide otherwise progressing updates. |
| [Laser][laser] and [sprite movement][sprites] | Laser spawning uses elapsed-clock deadlines, whereas bolt displacement and recharge use game iterations. | Closely spaced bolts are consistent with fewer movement updates between shots. That symptom alone does not locate UART, drawing or publication delay. |
| [Runtime initialization][runtime] and [telemetry ABI][telemetry] | Entry resets the RNG and process state; an existing versioned RAM record counts completed loops and faults. | Reuse those mechanisms rather than inventing another game state machine or callback-based frame counter. RAM telemetry is not remotely readable on physical Agon without an explicit export. |

Official [VDU documentation][vdu-doc] explicitly supports inclusive single-pixel
viewports and scrolling the graphics viewport. The historical single-pixel
viewport bug predates the selected VDP release. Add a diagnostic for the exact
Nurples sequence; do not presume the old bug explains current behavior.

## Proposed workloads

1. **Automated graphics tour.** Execute the whole Shapes suite, then the whole
   Bitmaps suite, on mainboard; repeat the same order on EDP. Use three paired
   repetitions from identical resource state. Remove keypress pauses and
   deliberate probe-settling delays from timed work. Keep loading, cleanup,
   route preparation and correctness queries outside the drawing interval;
   record their failures and distinct times rather than hiding them.
2. **Small Nurples rendering cases.** Compare fixed-count batches of:
   scrolling only; one-line background plus 16 tile draws without scrolling;
   and their original combined sequence. Preserve the 256×336 region at
   origin (128,48), one-pixel strip, and all 16 tile-Y phases. Preload identical
   assets. Outside timing, use known pixel sentinels/readback to verify the
   newly exposed line, unchanged bezel, unaffected lines during strip-only
   drawing, transparency and restoration of the full gameplay viewport.
   A whole-screen or full-tile rewrite is not an acceptable equivalent.
3. **Unattended Nurples gameplay.** Use a separately identified test executable
   derived from the repair source. Skip splash, joystick selection, countdowns,
   confirmation waits, game-over/restart prompts and farewell artwork. Load
   the same assets and initialize the normal scrolling world, enemies, active
   tiles, sprites and UI. Begin the one-minute measurement only after setup
   and its completion barrier finish.
4. Place the ship in the **centre of the visible playing field**, updating both
   the game record and displayed sprite. This draft interprets “centre of the
   map” as the visible field, not skipping to the middle of the level's 256
   source rows. Proposed first pass: stationary, firing off, normal keyboard
   polling retained. That input choice awaits the Author under D004.
5. Disable joystick through the existing `player_joystick_disable` routine.
   Make the player invulnerable at the damage/death boundary while retaining
   collision detection and the normal enemy/tile collision consequences.
   Preserve register/flag contracts of `update_shields`; do not remove entire
   collision loops to achieve invulnerability. Retain other ordinary world
   behavior and record any terminal/error condition instead of restarting.
6. Use the mainboard-driven MOS clock for **60 elapsed seconds**, not a fixed
   number of frames. In the selected 60 Hz mode its units advance by two per
   VBlank (120 units/second); reuse the validated clock handling from AUDIT-005
   and retain raw units/resolution. Stop producing gameplay commands when the
   loop observes the deadline, then time final drain and cleanup separately.
   Record deadline overshoot: an eZ80 blocked inside an output call cannot
   guarantee an exact sixty-second return. A host watchdog ends observation
   after 180 seconds per game pass and records incomplete output; it must not
   silently reset either processor or label a missing result a pass.
7. Keep a minute's game measurements in bounded RAM, then write through public
   MOS file APIs after timed gameplay. Record completed frames, frame-duration
   distribution/max, scroll/row progression, shots, keyboard observations,
   faults, requested/actual duration and drain time. Count gameplay work
   separately from initialization/exit. Reuse the existing telemetry fields
   where their meanings match. Persist a started record before the interval
   so a stalled run is distinguishable from one never launched.

The minute-long runs compare work completed in equal elapsed time. They need
not reach the same map row or emit equal command totals when one renderer is
slower; normalize by recorded work and do not mislabel them identical traces.
The finite batches provide the equal-work comparison.

For the proposed stationary pass, the operator leaves all keys released;
unexpected movement/fire input marks the run as an uncontrolled observation.
Polling the existing key map does not itself generate keyboard UART traffic.
This first pass therefore does not qualify performance under active input; a
later selected script must send real packets from P4 through the normal EMOS
receiver, without changing player variables or fabricating the key map.

## Completion callbacks and instrumentation

1. Prepare temporary mainboard VDP from the selected stock release plus only
   the diagnostic changes. Prepare P4 from the current measured implementation,
   preserving its scheduling and rendering behavior. Retain each original
   image/configuration and a concrete restoration procedure before flashing.
   Do not substitute the whole Pingo development fork for stock mainboard VDP.
2. Reuse the Pingo **pattern** of token/sequence correlation and a bounded
   application mailbox. The existing `P3DR` event is Pingo-specific, and its
   ten-byte keyboard-type carrier is rejected by current EMOS. This experiment
   therefore needs explicit, narrowly scoped **EMOS receive integration** as
   well as diagnostic changes on both VDPs. Prefer a distinct diagnostic event
   with negotiated capability and strict length/source/token validation; leave
   ordinary keyboard parsing intact. No direct UART/register bypass is allowed.
3. Under D003, the proposed experiment uses one outstanding completion request
   and a fixed event record, not arbitrary application code on either VDP.
   EMOS validates the active reply source and copies the event to its owned
   mailbox; an application callback, if used, only copies bounded data and
   preserves registers. No ISR logging, MOS calls or SD writes. Check unused
   wire identifiers and the remaining EMOS image space before coding; record
   the exact private diagnostic format in the implementation contract. This
   does not settle the eventual generalized production callback ABI.
4. A tagged completion means **all preceding drawing in that finite batch has
   finished**, not that the browser has presented it. The batch producer stops
   sending further drawing before requesting completion, so unrelated later
   commands cannot be included. Preserve deliberate deferred-sprite operations;
   a marker must not introduce a refresh that the workload never requested.
5. Use completion at Shapes-page/Bitmaps-stage and small-batch boundaries.
   For the sustained Nurples run, use setup and final completion only: **no
   per-draw or per-frame UART callbacks, waits or queries in the hot loop**.
   Frequent barriers could manufacture empty-queue opportunities and conceal
   the publication starvation found in AUDIT-006.
6. P4 and mainboard record bounded local count/time aggregates for scrolling,
   clipped bitmap work and relevant frame/queue activity. Retrieve these after
   the measured batch/run; do not stream per-primitive records over the UART.
   Separate nested durations rather than summing overlapping scopes. Include
   instrumentation-disabled comparison and an empty marker/round-trip control;
   disclose measured overhead instead of assuming local timestamps are free.
7. Record eZ80 submission time and callback arrival separately from each VDP's
   own monotonic elapsed execution time. Use equivalent endpoints and label
   quantization/preemption. Never subtract timestamps from different processors
   as if their clocks were synchronized. Browser delivery/publication remains
   separate; retain frame/snapshot progress observations without changing the
   video protocol, frame rate or core allocation during the baseline.

## Execution and acceptance boundaries

1. **B1 — Freeze inputs and diagnostic details.** After Author approval, vendor
   the selected repair source with provenance, settle the experimental carrier
   under the limits above, register identities, and preserve exact rollback
   images. Build from clean committed candidates for physical evidence.
2. **B2 — Implement and review offline.** Build the bounded applications and
   hooks. Verify no gameplay-mode packets in the new fixtures: autoexec selects
   mode 20 separately on both renderers before launch. Remove the game's
   inherited mode-8 splash and mode-restoring exit from this variant only.
   Route changes use `mos_oscli` and EMOS `--keep-display`; native USB input
   remains selected. Exercise headless determinism, clipping, mailbox rejection,
   repeat invocation, error exits and durable-file output, then launch the
   labelled emulator for Author validation. Existing game/suite builds remain
   intact for rollback and manual use.
3. **B3 — Controlled physical comparison.** With the reviewed firmware/media
   and exact restore paths ready, deploy the instrumented builds through the
   existing guarded procedures. Autoexec handles mode/input setup and gives a
   short readiness result; the benchmark can also be launched manually. Run
   the finite suite and minute-long game passes mainboard first, then EDP,
   three paired repetitions. Use the same browser connection state and assets;
   do not enable browser keyboard input. Let each fixture finish without
   requiring screenshots or a keypress to advance.
4. **B4 — Collect and stop.** Preserve raw SD results, partial runs, host logs,
   firmware/game/asset hashes and the instrumentation-overhead comparison.
   Report correctness independently from speed, per-case ratios and game
   progress independently from presentation. Restore the recorded ordinary
   firmware after the approved temporary experiment, verify USB/Legacy/ExCom
   operation, and pause for findings review before any optimization.

No drawing budget, queue scheduling change, core dedication, scrolling repair,
bitmap rewrite, MicroPython, parallel transport or ordinary Nurples redesign
is included. Any clipping failure gets its own evidence before a repair. A
clean exit or finite-suite pass does not close the sustained-publication defect.

[tiles]: ../../../../nurples-repair/src/asm/tiles.inc
[game]: ../../../../nurples-repair/src/asm/nurples.asm
[playing]: ../../../../nurples-repair/src/asm/state_game_playing.inc
[laser]: ../../../../nurples-repair/src/asm/player_laser.inc
[sprites]: ../../../../nurples-repair/src/asm/sprites.inc
[runtime]: ../../../../nurples-repair/src/asm/runtime_init.inc
[telemetry]: ../../../../nurples-repair/docs/runtime-telemetry.md
[p4]: ../../../vdp/video/extender/display/p4_display_controller.cpp
[vga64]: ../../../vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp
[viewport]: ../../../vdp/video/context/viewport.h
[bitmap]: ../../../vdp/vendor/vdp-gl/src/displaycontroller.cpp
[vdu-doc]: ../../../../../agon-docs/docs/vdp/VDU-Commands.md
