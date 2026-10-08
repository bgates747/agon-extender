# SPRITE-001 — Ordinary Nurples hardware-sprite trial

## Executive summary

Build a separately named Nurples executable using hardware sprites for every
sprite, then let the Author compare Legacy and ExCom gameplay. This follows
[HDMI-002](HDMI-002.md): much improved busy scenes, residual death-animation
flicker and upper-screen sprite visibility concerns. The agent builds/deploys;
the Author tests. The first review passes on mainboard but fails badly on
Extender: stalled gameplay and slowly appearing/disappearing sprite rows.
Small bench diagnostics identify expensive overlay preparation. The subsequent
authorized one-hour rolling-scanout prototype produces clean32-sprite output in
isolation, but fails refill timing under concurrent scrolling-memory traffic.
The follow-up DMA-assisted three-buffer test passes that loaded scene at about60Hz,
with Author-confirmed stable output and a verified late-refill abort. Full firmware
is restored; no integrated remedy or promotion is accepted. See the
[latest DMA-refill results](SPRITE-001/DMA-REFILL.md) and the retained
[rolling-scanout findings](SPRITE-001/ROLLING-SCANOUT.md).

Current full684-wide integration passes small fixtures and, after a bounded
memory-placement remedy, marked3600-update hardware Nurples at nominal60/s with
57% median active-work headroom. Loaded internal free RAM rises from83bytes to
22691bytes. Ordinary menu/mode changes, Escape cleanup and CLI commands pass.
The Author reports that the slight tear disappears when the game is paused;
hardware Nurples on mainboard has no observed tear. The successful candidate
remains installed; update/scanout synchronization and broader qualification
remain open. Automatic SD admission after ordinary
exit rejects in ExCom but recovers through EMOS Legacy without reset. See
[current memory results](HDMI-002/MEMORY-RESULTS.md); the previous848 image is
service recovery only, not a working hardware-Nurples handback.

The subsequent [automatic-carrier remedy](HDMI-002/RUNTIME-RESULTS.md) retains
the684 rolling game path and selects848×480 on mode0 exit. Ordinary software
and hardware Nurples round trips and bounded640×480 sprite checks in16/4/2
colors pass; the Author confirms the formerly missing upper text is visible.
This replaces the fixed684 installed selection without closing the thin-tear
or broader performance questions.

## Scope and ownership

Preserve all existing `nurples-repair` dirt on `dev`, then create the explicitly
authorized `hardware-sprites` branch. Game code stays in that repository.
Ordinary VDU commands travel through EMOS's existing Legacy/ExCom routing to the
selected VDP. The initial game-only trial changes no firmware and introduces no
direct GPIO/UART bypass. The later explicitly authorized standalone scanout
tranche below has its own temporary P4 firmware and restoration boundary.

Deploy only `/mystuff/arcade/nurples-hardware.bin`, beside ordinary `nurples.bin`.
Preserve ordinary executable, both AGNB containers, font and startup. Keep
game logic, population, art, geometry, scrolling and pacing unchanged. Do not
rebuild artwork. The original deployment did not start the game or benchmark;
the separately authorized diagnostic tranche below may run bounded tests.
No emulator change or push is required.

## API précis

Official documentation: `agon-docs` commit
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
[sprite API](../../../../agon-docs/docs/vdp/Bitmaps-API.md) and
[VDP variables](../../../../agon-docs/docs/vdp/VDP-Variables.md).
The read-only VDP reference is clean at tagged `v2.16.0`, commit
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`;
[sprite implementation](../../../../agon-vdp/video/sprites.h) and
[command dispatch](../../../../agon-vdp/video/vdu_sprites.h) confirm:

1. `VDU 23,0,&F8,2;0;` enables test flag2; presence enables hardware sprites.
2. `VDU 23,27,19` marks the selected sprite hardware. Apply it to every
   initialized slot before activation, after each game/level sprite reset.
3. Resetting sprites clears this selection unless the separate global
   prefer-hardware variable is also present. Clearing/reloading RGBA2222 frames
   preserves it. Mask frames and sprite GCOL can revert a sprite to software;
   this game uses RGBA2222 and does not call sprite GCOL.
4. Do not set the global prefer-hardware variable. Selection affects only the
   game's slots; ordinary exit already resets them. The feature-enable flag
   remains set, but does not itself make future sprites hardware.
5. Mainboard draws hardware sprites during VGA scanout. Extender CPU-composes
   overlays into output rows, without a P4 sprite plane. Common API terminology
   does not establish equal cost or behavior. Hardware sprites appear over
   background graphics and follow sprite-ID overlap order.

## Ordered work contract

SPR01-01 [x] Preserve existing Nurples work on `dev`, then branch.
Snapshot commit: `a2fd5d7`; branch: `hardware-sprites`. Author's explicit commit
instruction overrides earlier pending-artwork commit gates, without claiming
retrospective visual acceptance.

SPR01-02 [x] Enable hardware sprites and mark all20 initialized slots. Audit
player, weapons, enemies, explosions, respawn/frame changes and exit. Build with
the retained native assembler; record source/tool/binary identities and check
the command stream. Compile/content checks are not physical acceptance.

SPR01-03 [x] Establish idle EMOS SD-service readiness, deploy the distinct
executable and verify whole-file readback. Preserve user files and record hashes.
Leave the Agon at its prompt for the Author; do not launch the trial.

SPR01-04 [x] Author tests the same executable in Legacy and ExCom: upper-screen
visibility, busy enemies, player death/respawn, input and clean Escape exit.
Record endpoint-specific failures. No automatic promotion or follow-on remedy.

SPR01-05 [x] Diagnose the reported Extender failure with small tests. Retain a
short passive serial sample, inspect the overlay implementation and run the
existing unchanged render-load-r04 fixture in mode20: paced16 software sprites
(case46), then paced16 hardware sprites (case54), one approximately five-second
measurement each. These small16×16 test sprites are an isolation control, not a
substitute for Nurples's larger art, scrolling or gameplay acceptance. Record
application timing, output preparation and DMA separately. Reuse the installed
firmware and existing SD assets; preserve/restore startup; no firmware rebuild
or flash. If readiness fails, retain the failure and use deliberate normal
Agon reset recovery before another operation. Do not replay uncertain writes or
expand into the full benchmark campaign. Stop with findings before a remedy.
Completed with the timing and recovery qualifications below. The small cases
did not reproduce the game's severe stall; the full root cause remains open.

## Rolling scanout experiment — frozen 2026-10-07

SPR01-06 [x] Within the Author's one-hour authorization, prove a project-owned
ESP-IDF DPI derivative in a standalone848x480 pattern. First split the existing
unchanged picture into eight60-row DMA blocks; verify block/frame progress,
invalid-descriptor and underrun counters. Preserve the pinned SDK unchanged.
Then reuse two fixed-address strip buffers, refilling each only after its block
retires. Exercise a moving synthetic sprite over the retained background; record
refill deadlines and frame/block consistency. No live descriptor address edits.
Completed as a bounded investigation: static blocks and unloaded rolling output
pass, but concurrent-memory-load timing fails. This checkmark does not declare
the prototype ready for full integration.

SPR01-07 [ ] Only if the strip handoff passes and time permits, connect the
existing native scanline decorator without background save/restore. Start with
small sprite cases; a deterministic hardware-sprite Nurples run is authorized
but conditional on the simpler gates. Do not infer gameplay acceptance from a
standalone DMA counter. If the dependency is not proved, record the concrete
blocker rather than replacing more of the renderer speculatively.
Partially explored: the unchanged stock scanline function paints immutable
fixture art correctly in isolation and full684-wide small fixtures pass.
The marked game test fails around the warm-up/measurement boundary; the retained core and marker-disabled
control belong to HDMI02-M02c. SPR01-07A's standalone loaded pass does not qualify
the full application's allocation/lifetime behavior or ordinary gameplay.

SPR01-08 [x] End this tranche by restoring the exact previous full848x480 image,
verifying normal P4 services and admitted Agon input, and retaining source,
binary/flash identities, measurements and limitations. The deadline is one hour
from goal start; reserve restoration time. Agon startup/assets remain unchanged
unless a separately recorded fixture run requires temporary preparation. No
production promotion or broad SCAN-001 campaign is implied.
Restored `rgb-001-r03-b2026-10-07-02-45-45Z` with fresh segment readback, then
reset Agon normally after P4 services initialized. Input is ready/neutral with
no held/pending keys, SD listener is offline with no job, and diagnostic windows
are closed/nonoverflowed. SD files and38-byte startup were untouched throughout.
The experimental source, results and prior work remain uncommitted for review.

The Pi host builds and flashes only the identified P4. P4 DMA sends completed
RGB888 strips to its DSI bridge and LT8912B; the P4 CPU replenishes retired
strips. Agon remains idle during standalone tests, whose image deliberately has
no keyboard/network/SD services. Existing working firmware is the rollback.
This is an experiment in output scheduling, not an upstream defect correction.

### Completed follow-up — DMA-assisted refills

SPR01-07A [x] Reuse Espressif's pinned asynchronous framebuffer copier in the
standalone12-strip prototype. The P4 DMA2D engine copies the centered background
from PSRAM into a retired SRAM strip; the CPU retains the unchanged stock sprite
scanline body and cache handoffs. Keep one framebuffer-copy handle and at most
one outstanding transaction: the pinned helper has a shared static transaction
configuration and must not be treated as a concurrent multi-handle queue.
Initialize resources in task context. No allocations or task mutex waits in
refill/completion callbacks. Keep the SDK unchanged.

Before panel start, compare all12 DMA-prepared strips against CPU-prepared
background/sprite pixels. During scanout track copy, composition and total refill
latency, expected strip generation, outstanding-copy overlap and late readiness.
On a detected late/invalid handoff, latch failure and stop the experimental DMA
output instead of continuing indefinitely with corrupt buffers. Detection at an
ISR boundary cannot promise that no pixels were already read; it is a test abort,
not a production recovery design. Do not rely on frame counters as correctness.

Reuse the same1/8/16/32-sprite progression, fixed848×480 timing and separate-core
scroll workload, with at least30 seconds of the loaded32-sprite case. Preserve
exact binaries and bounded timing evidence, compare with the retained CPU-copy
control, then restore the previous full firmware and admitted input. If an
ordinary build/setup correction is needed, retain the corrected distinct build;
do not expand into real renderer integration or Nurples until this step has been
reviewed. No SD/EMOS/game changes or production promotion in this step.

Bounded comparison refinement: the two-buffer DMA control improves timings but
still exceeds one strip interval, and delayed ISR handling can conceal that
from a generation check. Compare three40-row buffers with the same12-block
output and workload (305,280 SRAM bytes, equal to the earlier two60-row buffers).
Refill the retired slot three blocks ahead. Also abort when measured refill
duration exceeds the conservative available-window threshold, independently of
generation checks. A deliberately delayed refill may be used as one negative
control to verify that output stops and no further frame rearming occurs.

Completed: the three-buffer run holds about60 DMA frames/s with32 sprites and
over60 seconds of concurrent memory load; maximum refill1,524µs, zero faults,
minimum observed ready lead1,012µs. The Author confirms stable/no flicker.
The delayed-refill control trips once and stops at frame41, with no further
frame rearming. Exact previous full firmware restored/readback verified;
normal Agon reset restores ready/neutral keyboard admission. SD/startup/EMOS
and game files untouched. [Results](SPRITE-001/DMA-REFILL.md) distinguish this
standalone pass from native integration and actual gameplay, which remain open
under SPR01-07 and require the next review.

### Authorized integration — SPR01-07, 2026-10-07

The Author approves proceeding after SPR01-07A. Keep this one bounded tranche:
reuse its twelve-block/three-buffer DMA2D pipeline in an explicitly selected
experimental full build. Preserve the existing848 timing and scrolling renderer.
The normal build and exact previous firmware remain rollback; no promotion.

Authorization extension: the Author retires for the night and explicitly asks
for unattended iterations/testing as needed, tracked as a goal. No new one-hour
deadline is imposed. Continue within this integration objective; preserve safe
rollback and exact evidence. Manual gameplay/visual acceptance can remain for
the Author after waking. Earlier pause-between-subtasks language does not require
waking them for routine implementation or recovery within this authorization.

1. The output task snapshots visible hardware sprites and cursors under the
   existing native exclusion, preserving stock order, visibility, RGBA formats
   and paint mode. Copy bitmap bytes into task-owned snapshot storage rather
   than retaining pointers to mutable/freed native objects. A three-slot mailbox
   separates the published scene, ISR-leased scene and next writer. No allocation,
   native/task mutex or object destruction in the ISR. The retained stock sprite
   scanline body paints the copied scene; the source framebuffer stays unmodified.
2. P4 DMA latches one scene and background selection for each prepared frame.
   Strip lookahead must not acknowledge a double-buffer swap before the selected
   frame actually starts. Old controller teardown cannot invalidate retained
   panel allocations or copied sprite bytes. Indexed modes retain their ordinary
   task-composed pixels; direct RGB888 modes use scanout sprites. Mode changes
   and empty scenes must retire overlays without leaving a native pointer alive.
3. Compile and exercise snapshot ownership, overlap/clipping, cursor/XOR and
   unchanged stock painting with focused host checks. Preserve exact experimental
   source closure and derivative-driver provenance; keep the SDK unchanged.
4. Flash/read back the identified P4; first establish startup/input and small
   existing hardware-sprite fixtures. Check timing/abort counters and ordinary
   mode/route transitions. Only if those gates pass, adapt the existing deterministic
   repaired-Nurples fixture to mark its sprites hardware, then run3,600 updates
   and collect the same timing/state evidence. Do not modify ordinary game/assets.
5. Preserve/restore startup and any temporary fixture configuration. On a failed
   gate restore the exact prior full firmware and admitted input; do not push
   through a failed scene into the game. On success retain a clearly identified
   review candidate and give the Author the manual game smoke boundary. Stop for
   review with actual results and remaining limitations.

Research boundary: pinned IDF commit
`b774170ff46c393eeb5e495ea37936038d3f4f4f`, documentation
`docs/en/api-reference/peripherals/lcd/dsi_lcd.rst` and
`docs/en/api-reference/system/mm_sync.rst`; source
`components/esp_lcd/src/esp_async_fbcpy.c`, its private header, and
`components/esp_hw_support/dma/dma2d.c`. The existing DSI draw path already uses
this helper. `dma2d_enqueue` uses ISR-aware critical sections, while callers own
transaction lifetime. CPU writes must be cleaned before DMA reads; DMA-written
scratch pixels must be invalidated before CPU composition; composed pixels must
be cleaned before scanout. All ranges are cache-line aligned and exclusively
owned during these transitions. This is a standalone timing/lifetime experiment,
not a claim that the private helper is a general concurrent application API.

## Author result — hardware-sprite game

| Endpoint | Author observation | Disposition |
|---|---|---|
| Mainboard / Legacy | Works splendidly | Qualitative gameplay pass |
| Extender / ExCom | Game nearly halts; visible sprites blink slowly and appear to be drawn/erased a scanline at a time | Failure; retain ordinary software-sprite game as control |

No measured mainboard performance or complete sprite/API qualification is
implied. The HDMI firmware was unchanged between these user trials.

## Small-test findings — 2026-10-07

**Both small cases sustain60 application updates/s, but hardware sprites cost
8.64 times as much HDMI preparation and nearly double p95 command completion.**
This supports investigating the P4 overlay implementation before changing the
game again. It does not establish the complete cause of the severe Nurples
failure or measure physical monitor delivery.

[Portable results and provenance](SPRITE-001/SMALL-TEST-RESULTS.json) retain
exact identities and raw evidence hashes. The existing render-load-r04 case46
and case54 use16 moving16×16 RGBA2222 sprites, the same trajectories, mode20,
the same P4 image and no browser streaming. They omit Nurples's scrolling and
larger/spread-out actors. The command fence excludes recurring overlay work;
that work is measured separately in HDMI preparation.

| Metric | Software sprites, baseline | Hardware sprites | Hardware change from baseline |
|---|---:|---:|---:|
| HDMI preparation, mean ms/pass | 0.458 | 3.953 | +764% |
| Application command completion, p95 ms | 5.472 | 10.514 | +92% |
| p95 completion as share of16.67ms budget | 32.8% | 63.1% | +30.3 percentage points |
| Application command completion, mean ms | 5.016 | 5.756 | +14.8% |
| Command submission, mean ms | 1.711 | 1.713 | +0.1% |
| Application updates/s, MOS-clock derived | 60.0 | 60.0 | 0% |
| P4 HDMI submissions/s | 60.031 | 59.990 | -0.07% |
| DMA frame completions/s | 60.031 | 59.990 | -0.07% |
| Completion samples over nominal16.67ms budget | 0/842 | 0/402 | None in these small cases |
| Actual measured application interval, s | 14.033 | 6.700 | Unequal diagnostic windows |

Rows place the largest relative cost increase first. Percentage changes are
`(hardware/software−1)×100`; frame-budget percentages use the nominal60Hz
budget. PRT values use72,000counts/s, with raw MOS120units/s and16.67ms clock
granularity. Half-second calibration returned35,237 and35,023 PRT counts;
these are nominal timings, not external clock calibration. Both results have
valid, untruncated records, no sample faults and matching closed P4 windows.
Preparation is wall time including native-mutex waiting and overlay work;
it is **not** exclusive overlay CPU time. P4 phases may overlap other work and
must not be added to application completion. One pass is diagnostic evidence,
not a stable long-run percentile estimate or complete acceptance.

### Implementation findings

1. `P4Rgb888Controller::composePanelOverlays` in
   [p4_rgb888_controller.cpp](../../vdp/video/extender/display/p4_rgb888_controller.cpp)
   saves and converts the full512-pixel width of every row intersecting a
   visible hardware sprite, even when the sprite occupies only a small span.
   The installed path converts RGB888 background to RGB222, invokes the stock
   scanline decorator, then expands the resulting row to RGB888.
2. `restorePanelOverlays` expands saved RGB222 backgrounds pixel by pixel.
   `prepareForDrawing`, called by primitive execution and sprite show/hide,
   restores those rows before drawing. These operations affect the live
   single-buffer HDMI memory. Erase/repaint visibility is therefore plausible;
   the tests did not independently capture or time the reported row-wise effect.
3. [HdmiOutput::publish](../../vdp/video/extender/display/hdmi_output.cpp)
   holds native drawing exclusion during overlay composition and panel/cache
   submission. The serial preparation timer starts **before** mutex acquisition.
   The P4 reuses the stock sprite scanline algorithm, but this surrounding
   full-row save/restore/output mechanism is Extender-specific. Mainboard's
   scanout overlay does not require this P4 panel-background round trip.
4. Horizontal offscreen rejection exists in the stock sprite row painter but
   not in `overlayIntersectsRow`; a sprite can therefore cause row conversion
   even when it contributes no visible pixels. This is an additional source
   observation, not a demonstrated cause of the Nurples failure.

The original proposed remedy was to investigate sprite-bounded RGB888 background
preservation/restoration and bounded use of the retained stock decorator, while
preserving the accepted scrolling path. Coherent presentation and input must
be tested; reduced byte traffic alone does not prove flicker fixed. This is a
historical recommendation. The Author subsequently authorized the bounded
rolling-scanout experiment above instead; it does not authorize an unbounded
renderer replacement.

### Recovery, evidence and handback

The initial passive serial sample reported15.593ms mean preparation and60.091Hz
DMA. Its scene was not verified: a text response showed a post-game prompt and
fresh screen requests did not complete. Do not label it a measured failing
Nurples interval. Injected input did not drain; restarting the P4 with unchanged
firmware and resetting Agon recovered admission.

The first controlled startup then timed out connecting mainboard to Extender,
as confirmed by the Author; no measurement window opened. After both endpoints
were ready, a deliberate mainboard reset started the software control. Manual
Space ended it, giving14.033s rather than the planned five-second interval.
The normal runner completed the hardware case; its recorded interval is6.7s
including bounded host control latency. Failed startup is not a rendering
failure or a missing timing sample, and was not blended into the results.

Original38-byte startup was restored with complete byte readback. Final checks
show admitted input, no held/pending keys, listener offline, no SD job and closed
measurement windows. Firmware, game executables and assets were unchanged.
The card stays in Agon at the normal Legacy prompt. Results/startup history are
under SD `/agents/extender/results/sprite001-small`; local raw evidence and
restoration receipt are under ignored `agents/sprite001/diagnostic`.
No commit, push, promotion or firmware remedy was performed in this tranche.

## Evidence

Local bench identity/service address remain in ignored `HARDWARE.local.md`.
Build/deployment evidence belongs under ignored `agents/sprite001/`, with a
concise cross-project note in Nurples's dated development log. Experimental
artifact lineage: `nurples-hardware-r01`; exact build timestamp and hashes belong
in its manifest. Existing game and firmware remain available for comparison.

## Build and deployment result — 2026-10-06 local

[Deployment receipt](SPRITE-001/DEPLOYMENT.json) records the byte identities.

The unchanged ordinary source first rebuilt byte-for-byte using the retained
ARM assembler (SHA256
`0e4ea930cee1f1278ba88ef2454ff250031db9e160afdacf80ebd8e867e7ba51`).
The branch then adds54 bytes: the test-flag command, selected-sprite command
and20-slot initialization loop. Assembled listing inspection confirms IDs0–19
are marked before activation. All350 image records in the existing game
container use supported RGBA2222. No live sprite-GCOL calls revert the flag;
frame clearing/reloading preserves it; ordinary exit resets sprites.

| Item | Recorded value |
|---|---|
| Preserved `dev` commit / branch point | `a2fd5d773860ef30a359c20566f9d83981056b0a` |
| Experiment branch | `hardware-sprites` |
| Build | `nurples-hardware-r01-b2026-10-07-03-35-10Z` |
| Executable bytes | 36,493 |
| Executable SHA256 | `3ba82ef604cb75fdd35b42ff5890504a3c4e74c28bfc7f83b7208130276cfcd1` |
| SD destination | `/mystuff/arcade/nurples-hardware.bin` |
| Independent readback | Complete byte equality |
| Ordinary binary, startup | Read before/after; byte-identical |
| Assets, EMOS, P4 firmware | Unchanged |
| Runtime testing | Reserved for Author; trial not launched by agent |

Escape did not establish SD-service eligibility from the prior foreground state.
The agent used the normal Agon reset/startup once, verified CLI admission, then
used the existing foreground fast listener for upload followed by independent
full readback. Listener exited normally. The MOS prompt is left in Legacy routing;
the agent changes the working directory to `/mystuff/arcade` for manual testing.
The experimental code/build files remain uncommitted pending review; only the
pre-existing dirt was committed. No push occurred.

At the prompt, `LOAD nurples-hardware.bin` then `RUN`. Choose no joystick.
Exit normally before switching display route. Repeat with `EMOS EXCOM` (or
`EMOS LEGACY`) and the same executable. Retain the ordinary `nurples.bin` as
the control. Report upper-screen sprites, busy scenes and death/respawn separately.

Live integration build/host checks and the SRAM failure/remedy are tracked in [INTEGRATION](SPRITE-001/INTEGRATION.md).

## Temporary pause control — 2026-10-07

Author review of the installed684 memory remedy is positive: beautiful output,
with a thin horizontal tear about one-fifth down. Preserve that bounded acceptance;
broader qualification and a production-version decision remain outstanding.
The Author requests a temporary P pause/resume control to inspect the same image
under reduced rendering load. P4/EMOS firmware and HDMI timing stay unchanged.

SPR01-P01 [x] Build a separately named `nurples-hardware-pause.bin` from the
current hardware-sprites branch. Keep game-owned diagnostic source/builder in
nurples-repair. Reproduce the retained hardware binary before modifying a copied
entry point. Poll MOS's existing key map: P is byte6 bit7; use a rising edge so
holding P toggles only once. Paused iterations keep the stock clock wait and
Escape polling but skip game logic, timestamp advancement, drawing and telemetry
updates. Exclude accumulated pause duration from the game's virtual timestamps
on resume. Reset pause state on every MOS RUN. No pause overlay redraws the image.

SPR01-P02 [x] Compile/check the exact derivative, deploy only the new executable
beside its assets using the admitted foreground listener, and verify full
readback. Preserve both normal binaries and startup. A bounded pause/resume/
Escape smoke precedes Author review; no automatic benchmark or firmware flash.
Retain enough evidence to distinguish stopped game drawing from continuing P4
HDMI scanout/sprite composition. Persistent tearing is for the Author to judge.

Official reference: agon-docs `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
[keyboard bitmap](../../../../agon-docs/docs/mos/Keyboard.md) and
[`mos_getkbmap`](../../../../agon-docs/docs/mos/API.md). Reuse the game's
`vdu_vblank`, ordinary Escape/cleanup and timestamp-based timers; do not install
a new interrupt handler or change EMOS input routing.

### Pause-build result and handback

Build `nurples-hardware-pause-r01-b2026-10-07-17-06-35Z` is36677bytes,
SHA256 `4c842f8dfe6cf12a627a4b764b08bf631bce8476d3f1535548f3eb4549bfd909`.
Assembler SHA256 remains
`0e4ea930cee1f1278ba88ef2454ff250031db9e160afdacf80ebd8e867e7ba51`.
Control reproduction matches the existing36493-byte hardware game exactly.
The new executable is independently read back in full; both original games
and38-byte startup are unchanged. The copied entry-point diff, matched symbols,
source hashes and deployment receipt are retained under `agents/sprite001/pause`.
Maintained diagnostic source and builder live only in nurples-repair.

Startup, ordinary entry, two two-second P holds separated by releases, another
P tap, Escape, clean farewell and a second MOS RUN complete without reset.
The keyboard returns neutral; the restarted diagnostic is left at its joystick
prompt in ExCom. No new firmware or assets are installed. The attempt to compare
paused browser pixels could not start: this HDMI image rejects the video
WebSocket connection. No pixel-equivalence or visual pause pass is claimed.
The Author must confirm that P freezes/resumes the picture and inspect the thin
line. This temporary diagnostic is not a performance-baseline replacement.

Choose N for joystick, then any key to start. P pauses/resumes; Escape exits
while paused or playing. There is no on-screen pause banner, so the inspected
image is undisturbed. Pausing stops game-issued rendering, while P4 HDMI scanout
and hardware-sprite composition continue. Later invocation from the game
directory is `LOAD nurples-hardware-pause.bin`, then `RUN`.

### Author pause/control observations and sprite-path review

Follow-up on 2026-10-07, with the same installed P4 memory-remedy build:

| Application and route | Author observation | Evidence limit |
| --- | --- | --- |
| Hardware Nurples, ExCom, moving scene | Thin horizontal tear, approximately one-fifth down | Visual observation; no captured scanline timing |
| Hardware pause diagnostic, ExCom, paused scene | Tearing disappears | P4 continues scanout/composition while game drawing and sprite-position updates stop |
| Hardware Nurples, Legacy/mainboard VDP | No tearing observed | Visual control, not a synchronized capture of identical game frames |
| Ordinary Nurples, ExCom | Laser bolts now remain visible to the top of the playfield; Author suspects hardware sprites | Visibility alone does not identify the sprite implementation |

Pausing removes the observed artifact without changing HDMI timing. This points
toward an interaction between scene updates and scanout, rather than a permanent
bad row or fixed geometry error. It does not isolate background scrolling from
sprite-position publication, cache visibility, or workload-dependent refill
timing: the pause stops several activities together. In particular, immutable
hardware-sprite snapshots do not make the single-buffered background immutable.
The rolling DMA copy still reads live background pixels strip by strip.

The source review finds no automatic conversion of ordinary software sprites:

1. The deployment receipt verified that ordinary `nurples.bin` remained byte-for-
   byte unchanged (SHA256
   `63c89d2676f6645631b2240f23002b8b68d45069979a4804ca7d14f34e720088`).
   The separately named hardware game enables variable2 and explicitly marks
   each sprite with `VDU 23,27,19`; it does not set prefer-hardware variable
   `0x0400`. Ordinary game initialization issues the sprite reset command.
2. [resetSprites](../../vdp/video/sprites.h) assigns the hardware bit afresh:
   only the combination of feature flag2 and prefer-hardware variable `0x0400`
   makes reset sprites hardware. The
   [variable map](../../vdp/video/vdp_variables.h) starts empty; the hardware
   enable flag surviving a game exit is insufficient by itself.
3. The [software painter](../../vdp/vendor/vdp-gl/src/displaycontroller.cpp)
   still saves/restores sprite backgrounds and paints sprites whose hardware
   bit is clear. The [rolling scene capture](../../vdp/video/extender/display/rolling/scene.cpp)
   includes only visible game sprites marked hardware and allowed to draw.
   [Strip refill](../../vdp/video/extender/display/rolling/strip_runtime.inc)
   copies the selected live background, then composes the captured hardware
   sprites. It does not reclassify software sprites.
4. All five reviewed P4 source files match the installed build's retained source
   archive byte for byte. No live sprite flags or variable `0x0400` were queried
   during this review, so another program having set that global preference is
   not excluded. Better upper-playfield visibility may instead reflect the new
   scanout timing; that explanation remains an inference.

The Author's paused-scene observation completes the requested visual comparison,
not the tearing remedy. If sprite type needs definitive confirmation, observe
the actual per-sprite hardware flags and prefer-hardware variable during an
ordinary-game run before changing renderer behavior. No reset, key injection,
firmware/game change or additional bench test was performed for this review.

### Author-requested earlier-firmware comparison

On 2026-10-07 the Author requests restoring the exact firmware used when
ordinary Nurples ran well but upper-playfield sprite visibility was limited.
Select `rgb-001-r03-b2026-10-07-02-45-45Z`, the full848×480 build preceding the
hardware-sprite experiment, factory SHA256
`c41d7974f9d734a1464155f02fec3ed3bf122e3e26b21e52306e9b6bf95bacad`.
This is a deliberate ordinary-software-sprite comparison, not a claim that this
older image supports the hardware game well. Preserve the current full684 image
`rgb-001-r04-b2026-10-07-15-27-40Z` and its verified artifacts for return.

SPR01-C01 [x] Verify both retained builds, restore/readback the earlier P4
firmware, and establish fresh EMOS keyboard admission after normal Agon reset.
Leave ordinary game binaries, assets, startup, EMOS and source work unchanged.
The Author runs `/mystuff/arcade/nurples.bin`; do not substitute the hardware or
pause derivative. Record visual results separately. A returning symptom proves
a firmware-version difference, not hardware-sprite selection or a particular
fix: scanout method and physical carrier geometry also differ.

Both complete build artifact sets verify. The earlier848 image is installed
with independent verification of all four flash segments. One normal Agon
reset establishes fresh, neutral Extender keyboard admission. Full SD readback
confirms unchanged startup, ordinary Nurples and hardware Nurples. The agent
exits the foreground listener, selects ExCom through EMOS, changes to the
game directory and loads ordinary `nurples.bin`. Rendered CLI text confirms
the final readiness message, with no load or route-switch error. The game has
not started: the Author types `RUN` to begin the comparison. No active automated
input, transfer or test remains. Visual comparison is pending. Local deployment,
prior installed records and handback evidence are retained under
`agents/sprite001/comparison-rollback/2026-10-07-17-50-36Z`.

Author result: the earlier firmware reproduces the same upper-playfield laser
visibility symptom. With the ordinary game binary unchanged, the comparison
confirms a visible improvement in the newer full684 firmware combination. The
Author regards this as a welcome incidental remedy. The specific contributing
change is not isolated, and this comparison does not establish a conversion to
hardware sprites. No new flash follows this report: the earlier848 comparison
image remains installed, with current game/CLI state under Author control.

### Post-exit text cropping diagnostic

The Author reports approximately eight top text rows missing after either game
exits on full684 firmware, but not on the earlier full848 image. Restore the
exact latest tested full684 memory-remedy build, run one short ordinary Nurples
entry/exit, and retain before/after logical-mode and output dimensions plus
available screen readback. Do not rebuild firmware or change game/startup files.
The HDMI build has no browser video snapshots; text readback is logical
framebuffer evidence, not an HDMI screenshot. Check centering/cropping in the
installed source before interpreting this as lost text or a sprite defect.

SPR01-C02 [x] Restore/verify the full684 build; confirm fresh EMOS input, run the
ordinary game briefly, exit normally, inspect the resulting text geometry and
record the finding. Preserve the full848 comparison and full684 tested bytes.
An output-mode policy remedy is outside this diagnostic.

Result: restored the exact15:27:40Z full684 image and verified all four flash
segments, then reset Agon once and verified fresh neutral keyboard admission.
Ordinary Nurples enters mode8 title, then mode20 gameplay, runs five seconds,
and exits normally to mode0. The pixel-derived logical text readback contains
the complete farewell beginning at row0. The initial title read encountered a
mode/font transition (HTTP409); only the capture was retried, not RUN or reset.

| Post-exit property | Earlier848 build | Latest684 build |
| --- | --- | --- |
| Logical mode0 dimensions | 640×480 | 640×480 |
| HDMI active dimensions | 848×480 | 684×384 |
| Source pixels omitted at top / bottom | 0 / 0 | 48 / 48 |
| Logical text grid / cell size | Same mode; no separate font measurement in this control | 80×60 / 8×8 pixels |
| Source rows sent to HDMI, inclusive | 0–479 | 48–431 |

The [centering helper](../../vdp/video/extender/display/hdmi_geometry.hpp) and
[fallback row publication](../../vdp/video/extender/display/hdmi_output.cpp)
therefore account for **six complete text rows cropped at each vertical edge**.
The current image's mode0 uses native rendering/fallback publication, unlike
mode20 panel-direct gameplay. This is output geometry, not evidence of text
loss or a game-specific cleanup defect. All five source files reviewed for
placement, strip staging, text readback and disabled browser video match the
installed source archive. No actual HDMI screenshot was available; the retained
capture is explicitly logical text readback, not proof of physical pixel output.
It corroborates the Author's visible clipping report and the geometry calculation.

The Author then visually confirms the reproduced bug and agrees that six
8-pixel rows matches the estimated missing text. This closes the diagnostic's
physical-observation gate; output cropping remains unfixed.

Full684 remains installed at the ExCom post-game mode0 prompt, input neutral,
listener offline/no pending job. SD files, game binaries, EMOS and source code
unchanged. Local evidence is `agents/sprite001/exit-crop/2026-10-07-18-09-49Z`.
The next output-policy work must accommodate480-line logical modes through a
suitable carrier or an explicitly chosen scaling policy; top alignment alone
would only move all96 clipped pixels to the bottom. No such remedy is implemented
or newly authorized by this diagnostic.
