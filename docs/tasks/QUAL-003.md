# QUAL-003 — Compare mainboard VDP and Extender EDP graphics

## Executive summary — current continuation, 2026-09-16

[P01g](QUAL-003/debrief/P01g/README.md) is the Author-authorized fixed-rendering
network payload ladder. Freeze contracts, execute G, restore and voice notify.
[P01h](QUAL-003/debrief/P01h/README.md) owns subsequent AGM/SRLE2 review; no
compression implementation now. Prior W failure remains preserved, not retried.

## Prior diagnostic finding

[P01e owner/scheduler trace](QUAL-003/debrief/P01e/README.md) captured a25.210ms
snapshot lock hold during which TCP/IP `tiT` occupied the same core for24.737ms.
This is observed lock-holder preemption, not25ms of pixel computation. The
candidate's probe-off baseline degraded; the probe-on run failed its terminal
pixel query. Thus the captured event is diagnostic evidence, not a passing
performance result. Remaining controls were stopped. Original r43/startup and
keyboard/SD verified restored; hardware voice receipt and visible review banner delivered. No push.

The [itemized plan](QUAL-003/DEBRIEF-PLAN.md),
[overnight debrief](QUAL-003/OVERNIGHT-DEBRIEF.md) and
[source research](QUAL-003/debrief/OFFICIAL-RESEARCH.md) preserve context.
Review a representative lower-overhead control and bounded scheduling/exclusion
experiment. Load ramp is now authorized in P01g, chunking fallback only; Golem excluded.

## Earlier execution amendments and scope records

The sections below preserve earlier contracts and checkpoints. Their older
"current"/"deferred" wording does not supersede the dated review above or the
nonce-validated Nurples evidence.


Current application continuation: [Rally Legacy/ExCom r01](QUAL-003/rally-excom/PLAN.md), authorized after E09 review. Targeted diagnosis precedes broad reruns; first clear defect is a review stop.

Current execution amendment: [framebuffer-first hardware pass](QUAL-003/timing/framebuffer-pass.md). The 2026-09-13 exploratory pass is complete and awaiting Author review: 624/624 intervals in the stable 39-case selection, no P4 video snapshots, and ordinary mainboard firmware/keyboard/SD restored. Two earlier population-stress failures remain preserved; see the amendment for exact scope and limits.

The later [UART-aligned rerun](PORT-008/uart-alignment/FINDINGS.md) first timed
out on mainboard BSP21_01 after 483 intervals. One identical retry completed
624 intervals with the same 8 probe differences and zero P4 snapshots. Keep
this intermittent diagnostic/stock-path timeout open alongside the earlier
population-stress failures; do not treat a successful retry as its resolution.
Current loading/rendering comparisons are linked from those findings. No
renderer or test-case exclusion was introduced for the UART-aligned retry.

## State and scope

Status: EDP graphics-suite hardware visual review PASS, accepted for freezing.
Mainboard BSP-28–30 artifacts are reference-display observations. A separate
Wolf3D failure with EDP is deferred to PORT-004 at the Author's request.
Startup follow-up and production callback design remain open. The
[benchmark contract](QUAL-003/benchmark-contract.md) is **reactivated for the
Author's finite graphics timing tranche**, following the accepted backend
audit/restoration and qualitative r10 playtest. Its
[curated inventory](QUAL-003/curated-timing-cases.json) targets sprites, clipping
and finite scrolling; the whole tour and deterministic Nurples are deferred
until these results are reviewed. Temporary mainboard/P4 hooks, bounded EMOS
receive integration and the automated durable-result runner now have exploratory
hardware evidence in the linked framebuffer-first amendment; broader
qualification and the omitted population-stress investigation remain open. This is the current measurement work; no separate
typing-timing increment is underway.
Author requested paired graphics fixtures after accepted
ExCom console/Nurples gameplay. Vendor agon-utils Shapes and Bitmaps in this
task silo, then render each page/stage on mainboard VDP first and EDP second,
with one keypress pause after the pair. Native P4 USB remains the input source.
The source checkout contains other active work and remains untouched.

## Visual-comparison work items (accepted increment)

1. Vendor exact source inputs with per-file provenance and preserve documented
   reference mismatches. Keep generated binaries/assets and review media local.
2. Use the existing public `mos_oscli` API for EMOS-owned display switching.
   The Author accepted the display-preservation option below.
   No fixture may write transport registers or activate EDP independently.
3. Adapt both Shapes (24 pages) and Bitmaps (32 pages, 123 stages). Maintain
   independent per-display probe results and state; preserve staged sprite,
   deferred-refresh and resource-lifetime semantics across the comparison.
   Check route-command failures before sending drawing bytes. Escape and normal
   completion return to a usable ExCom MOS prompt with USB input selected.
4. Prepare startup that selects Extender keyboard and ExCom, and configures
   mode 20 (512×384, 64 colours) on both destinations before fixture execution.
   Only autoexec selects video modes. Build and validate generated packets,
   assets and route ordering; perform controlled emulator review before commits
   or hardware deployment. Launch the prepared review when ready for the Author.
5. After review, prepare the SD and any required firmware through the existing
   guarded workflow, then retain side-by-side hardware observations adjacent to
   the r03 design. Do not claim full graphics fidelity from compilation alone.

## Bounded research and implementation contracts

Official `agon-docs/docs/mos/API.md`, section 0x10, defines `mos_oscli`: HL points
to a mutable command string; A returns status; HL is preserved. EMOS already
recognizes EXCOM/LEGACY through this command route and owns its coordinator.
No new RST ABI is necessary merely to request a mode from an application.
The exact source references are recorded in the ignored local précis.

Current console switching is intentionally disruptive: P4 preparation invokes
retained vdu_mode(0), EMOS initializes/clears the destination, and EMOS replaces
the mainboard image with a status banner. Therefore unmodified commands cannot
preserve two matching images or a multistage bitmap scene. The existing
idle-console scope does not establish application display-state preservation.
The Author's requested comparison requires an explicit bounded extension if
both images are to remain visible.

Startup must select mode 20 separately for each destination. The fixture must
not smuggle a VDU22 packet into generated stage data or switch mode itself.
The current ExCom code resets P4 to mode 0 on ordinary entry, so the startup
and any retaining switch must be qualified together.

## Decision register

QUAL-003-D001 — accepted by the Author: retain both rendered images at the pause. The Author selected a display-preserving EMOS command option,
requested through mos_oscli, retaining each processor's own scene and switching
only the committed route/reply authority. This keeps the comparison meaningful
and preserves staged bitmap state; it requires a bounded EMOS/P4 extension.
Alternative: current disruptive switches and rebuilding every previous stage
on each transition; the mainboard image would not remain for comparison.

QUAL-003-D002 — accepted and clarified by the Author on 2026-09-10: generalized
callbacks are a supported production EDP capability, enabling applications to
receive useful feedback about EDP work and state. Render completion is one use
case; the graphics benchmark is an initial intended consumer. The Pingo
mainboard callback is a precedent, not the scope limit or automatically selected
mechanism. Recorded in
[ADR-0017](../decisions/ADR-0017-generalized-edp-callbacks.md).

QUAL-003-D003 — open: discuss the general callback model with the Author before
implementation. Establish callback execution ownership, registration, event and
state/result access, then the request/correlation and delivery contract under
EMOS. For the rendering use case, specify covered work, hardware-sprite
composition, deferred operations and the distinction from sink presentation.
Capability discovery, cancellation/reset and stale-event behavior also require
a contract. The Author explicitly requests further discussion; do not infer an
event catalogue, arbitrary memory access, uploaded-code execution or a public
ABI from the Pingo-specific carrier.

The benchmark contract now proposes a bounded, experimental completion event
and EMOS-owned mailbox as the initial measurement mechanism. This proposal
requires review and does not settle the production callback model. The current
EMOS rejection of the original Pingo keyboard carrier is documented below.

QUAL-003-D004 — open, parked behind AUDIT-006: first unattended Nurples input pattern.
Recommendation: ship centred in the visible playing field, stationary and
firing off, with ordinary keyboard polling, scrolling, enemies and collision
processing retained. This gives a repeatable first comparison without adding an
input sequencer. Alternative: a fixed movement/fire script, which also exercises
return UART traffic but adds sequencing and changes the workload. If selected,
P4 must send ordinary keyboard packets through EMOS; the test must not write
the game's key map or player controls directly. Revisit this after the audit;
do not implement an assumed answer. The requested collision invulnerability,
one-minute duration, automatic start/exit and disabled joystick are already
part of the draft scope.

## Evidence and limits

Original suite reference checks report Shapes 237/244 pixel checks with seven
known documentation/reference disagreements and no query timeout. Keep those
observations distinct from any new EDP differences. Vendor snapshot provenance
is a worktree file-hash manifest because the source suite is not committed in
agon-utils. No source ownership transfer or completed hardware test is implied.

### Accepted implementation contract

`EMOS EXCOM --keep-display` and `EMOS LEGACY --keep-display` use the existing
public mos_oscli path. Ordinary commands without the option remain disruptive
console switches. Applications finish their current VDU command/query before
switching; each renderer keeps its own mode, framebuffer, contexts and assets.
EMOS retains route/activation/reply authority and USB source selection. The
paired P4 prepare-keep opcode is 5 under existing wire version/contract 1;
old peers reject it. Its fresh challenge and post-COMMIT query barrier remain
mandatory. No screen migration or arbitrary concurrent application switching
is implied. Standing version preapproval supplies EMOS v0.1.12 and console r04
as drafts, with registry r52 and paired-graphics-probe-r01.

## Implementation findings

1. Existing `mos_oscli` reached EMOS, but the mode coordinator rejected every
   live application as busy. EMOS INTEG-011 explicitly permits Legacy/ExCom
   requests carrying `--keep-display`; other application mode changes and
   overlapping resident dispatch remain rejected. Tests cover case-insensitive
   options, unknown options, failed entry and per-request option reset.
2. The old text-only emulator peer scanned for the private control prefix and
   could misread binary graphics payloads. This task uses a bounded command
   length framer checked against every generated packet and adversarial payload
   splits. It sends complete ordinary commands to native VDP. This is review
   infrastructure, not another production VDU implementation.
3. Both fixtures expose their full build identity, preserve the upstream
   generators and maintain independent probe/result banks. The task disables
   upstream single-display deployment recipes. Only its paired startup selects
   modes and routes. Mainboard clock and Extender USB keyboard remain selected.

## Draft validation checkpoint — 2026-09-09

1. Guarded EMOS build/link/runtime checks passed at 130215 bytes, 857 bytes
   under 128 KiB. Host coordinator checks cover the application gate, explicit
   option, default rejection, busy rejection, failed activation, reset of
   request options and unchanged transaction/recovery cases. The real console
   adapter checks kept/fresh initialization and unsupported-peer rejection.
2. Both fixture generators and independent binary/packet/asset validators
   passed. The bounded graphics framer passed full-corpus, arbitrary chunking,
   opaque control-like payload and unknown-command rejection checks.
3. Real EMOS with two native stock VDP instances completed all 24 Shapes pages
   and all 123 Bitmaps stages. Both renderer probe banks matched with zero
   timeouts. Shapes retained its seven known reference mismatches; they are
   not classified as new EDP failures or silently suppressed.
4. Actual presentation captures passed all 41 independent bitmap/sprite image
   checks on each native renderer. Page-29 early Escape and a page-1 truncated
   asset returned expected status and a usable ExCom MOS prompt. Separate
   production P4 control/lifecycle tests passed, including complete fresh-mode
   reset and absence of that reset for prepare-keep.
5. These are draft emulator/host results. Native VDP substitutes for P4 here;
   no physical P4 pixel, browser or UART qualification is claimed. The Author's
   visual review, candidate freeze and paired hardware comparison remain open.
   Exact local build/run manifests, transcripts and images are in the ignored
   paired-graphics emulator profiles and agent preparation records.

Official references used for this increment: MOS v3.0.2 at
`8336409351ee5314e02801a7b72a4f1bb5282519`; VDP v2.16.0 at
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`; agon-docs at
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` (mos/API.md 0x10, graphics/bitmap
contracts cited by the vendored reference notes). MOS and VDP references remain
clean and on their selected release tags.


The identified P4 console r04 draft build also passed with locked dependencies.
Its prepare-keep handler preserves the retained VDP context; the existing
fresh-entry context reset remains intact. Local build manifests hold the exact
EMOS/P4/fixture build identities and hashes for the pending review. No firmware
has been flashed and no bench SD card has been written for this increment.


The first desktop review exposed a capture-only scaling defect: the inherited
SDL helper cropped a fixed 512×384 rectangle inside the enlarged window. The
helper now captures the complete centred integer-scaled display and normalizes
it to mode-20 dimensions. A dummy-driver 3× window test reproduced the desktop
size and matched all four page-29 frames pixel-for-pixel against the original
1× captures. This does not change either fixture or firmware binary.


## Candidate handover — 2026-09-09

The Author reports both emulator images looked correct and explicitly requests
flashing and hardware testing. This accepts the visual review without a saved
Author screenshot; the generated images and automated evidence remain local.
Freeze EMOS v0.1.12, P4 uart-excom-console-r04 and paired-graphics-probe-r01 as
candidates under registry r53. This acceptance authorizes the required source
commits and paired deployment; it does not establish a physical test pass.
The [hardware test sheet](../../hardware/designs/light2-harness-r03/tests/paired-graphics-probe-r01.md)
owns the operator sequence and subsequent physical observations. Preserve the
working EMOS v0.1.11 rollback and retain the seated, powered UART/USB wiring.


Registry, identity and template validation pass. The aggregate version validator
still reports the pre-existing r02 connectivity hash mismatch; both affected
r02 files are byte-identical to HEAD and that held design is not used by this
r03 UART comparison. No r02 evidence or hardware definition was changed to
satisfy an unrelated gate.

## Physical deployment handover — 2026-09-09

Clean candidate builds passed from EMOS `82929c4` and Extender `7943789`.
EMOS v0.1.12 is 130219 bytes (853 bytes below 128 KiB). P4 console r04 passed
flash/readback verification, exact candidate identity, USB keyboard enumeration
and browser-service startup. The [deployment record](../../hardware/designs/light2-harness-r03/tests/QUAL-003-2026-09-10-03-52-11Z/README.md)
contains the observed result and artifact hashes.

The SD contains both candidate graphics programs, their runtime assets and the
matching boot smoke. Its active autoexec remains the one-shot MOS installer;
the working v0.1.11 image is preserved as rollback. The card was safely
unmounted. Next the Author inserts it, resets Agon, confirms the flash and
remounts it locally; replace the installer with the test-sheet startup then.
Physical paired rendering, CLI return and repeat checks remain pending.

## Installation confirmed — 2026-09-10

The Author reports good EMOS flashing. Returned SD payload integrity matches
the frozen v0.1.12 candidate, and all 29 runtime files and retained rollback
images verify. The installer was replaced with the committed graphics startup;
the card is safely unmounted. The [installation and startup receipt](../../hardware/designs/light2-harness-r03/tests/QUAL-003-2026-09-10-04-02-44Z/README.md)
distinguishes the Author's flash report from SD checks. P4 r04 is unchanged.
The next Agon reset starts Shapes; physical comparison remains pending.

## Initial hardware feedback — 2026-09-10

The Author reports the graphics look good so far and that manually loading and
running the programs works better than automatic launch. The browser showed an
SD-related complaint during the automatic path, although EMOS could load the
programs manually. Exact message, failing autoexec line, timing and observed
page/stage coverage are not yet recorded. This is partial positive visual
feedback, not a complete Shapes/Bitmaps pass. See the design-adjacent
[observation notes](../../hardware/designs/light2-harness-r03/tests/paired-graphics-observations.md).

QUAL-003-I001 — open: identify the automatic-start failure. First recover the
exact message and whether it precedes the first page or follows program exit.
EMOS's inherited `src/mos.c` maps return code 1 to `Error accessing SD card`;
`mos_EXEC` propagates command/program failure to the normal error printer.
The paired fixtures also return 1 for mode/route failures (`paired.inc` and
Shapes' initial mode check). Therefore the generic SD wording cannot by itself
identify the failed subsystem. A mode-readiness race is a hypothesis only;
neither SD failure nor that race has been reproduced or established.

For the next media handover, follow the Author's manual-launch preference:
retain boot smoke, native USB input, both mode-20 selections, ExCom and the
`/extender` working directory, then stop at the prompt. Omit only the final
`LOAD shapes.bin` / `RUN` pair. Record the changed startup as a procedure
deviation or revision when deployed; do not rewrite the frozen r01 startup or
earlier evidence. The card is not mounted locally at this observation, so no
media or running-board change accompanied it. Leave the automatic-start defect
open even if manual loading continues to work.

QUAL-003-I002 — recorded mainboard reference anomaly; non-blocking for the
accepted EDP suite pass: sprite-display anomalies on pages 28–30.
The Author reports mainboard VDP shaking/tearing while EDP appears steady and
continues the review. Page 28 exercises hardware paint-mode transitions;
page 29 exercises transformed frame lists on both sprite backends. Preserve
this observation without changing the fixture mid-review or attributing the
cause to stock VDP, wiring, mode switching or EDP. After the review, narrow
the affected sub-stages and whether the effect continues while paused; account
for mainboard VGA versus EDP's five-fps browser presentation. Exact footage,
sub-stages and repeat evidence remain unavailable.

The Author additionally reports abnormal mainboard output on BSP-30, bounded
sprite population. Its exact artifact and EDP comparison are not yet reported.
The page varies count (1/2/4/8/16), backend, pixel format, scanline alignment
and frame size; do not assume a population threshold or shared cause before
the affected sub-stage is identified.

QUAL-003-I003 — deferred to PORT-004 by the Author on 2026-09-10 until audio
implementation resumes: Wolf3D compatibility failure with EDP. The Author reports
misplaced text and apparently unplayable behavior; Nurples appeared fine. The
Author corrected the initial crash description: Escape/quit worked, the game
exited cleanly to EMOS and operation was normal afterward. No crash is confirmed.
The Author confirms the same game build works properly on mainboard VDP;
treat this as an EDP-path compatibility difference, not a general game defect.
The quick source audit confirms that EDP's empty audio handler leaves command
parameters in the VDU stream, where they can be interpreted as text or controls.
Wolf3D sends these commands. This is a strong candidate explanation, not a
hardware-confirmed complete diagnosis. [PORT-004](PORT-004.md) owns the recorded
source evidence, framing repair and subsequent same-binary Wolf3D retest.
Investigation and repair are deferred, not current graphics-suite work. Preserve
this separate limitation; do not fold it into mainboard-only BSP-28–30 artifacts
or the passing suite result.

## Completed visual review and performance request — 2026-09-10

The Author reports everything else passes and EDP is steady throughout,
including BSP-30. This accepts the visual tour with the previously recorded
mainboard and startup exceptions; precise automated pixel/timing evidence is
not inferred. EDP appeared slower on some tests, but rendering time and browser
presentation delay have not been separated. The Author requests an automated
whole-suite mainboard-first/EDP-second benchmark proposal with durable file
output; benchmark implementation and deployment have not begun.

The Author suggests reusing the existing Pingo VDP render-completion callback,
which was developed and physically tested on the mainboard ESP32. Its `P3DR`
notification is a token/sequence-tagged ten-byte event, emitted after a Pingo
scene render has finished writing its destination, and consumed through the
MOS keyboard callback. That specific hook is scoped to Pingo 3D completion;
ordinary 2D VDU queue completion requires its own verified boundary.

The stock VDP and retained EDP `sendScreenPixel` handlers already call
`waitPlotCompletion()` before returning the pixel packet, and the documented
VDU 23,0,&CA command explicitly drains the drawing queue. These provide a
stock-compatible completion/reply path to assess for this benchmark. A hardware
sprite's recurring VGA scanout or EDP presentation composition is not completed
by a framebuffer read; label command/framebuffer timing separately from actual
display presentation. Exact local Pingo references are in the paired-graphics
précis. No mainboard firmware replacement is implied by this discussion.

The Author subsequently clarified the broader product goal: generalized EDP
callbacks (D002), with render completion as an example. The earlier
stock-compatible query proposal remains relevant to timing the stock mainboard
reference; it does not replace the general EDP facility. The callback model
requires further discussion. Benchmark and service implementation have not begun.

### Measurement ordering amendment — 2026-09-10

The Author subsequently selected the smaller paired Legacy/ExCom pathway
benchmark in [AUDIT-005](AUDIT-005.md#accepted-measurement-sequence--2026-09-10)
before performance repairs, followed by repeat measurements and personal
Nurples playtesting. This task's completion-boundary research supports that
increment; the full graphics-suite benchmark and generalized callback service
remain later work. Automated Nurples control is also deferred; its eventual
EDP-generated keyboard packets must traverse the normal UART/EMOS receiver.
The [pathway benchmark](AUDIT-005/README.md) uses the existing pixel-query
completion reply for its initial two workloads. Its SD application passes
functional emulator checks and now has a complete 48-row
[physical pathway baseline](AUDIT-005/hardware-baseline.md). It does not
require a new callback implementation or benchmark the whole graphics suite.

## Graphics-suite milestone frozen — 2026-09-10

The Author explicitly accepts the graphics suite as a pass and requests a
commit, emphasizing that the notable suite artifacts are on mainboard VDP,
not Extender. Record the bounded EDP visual PASS beside the design. The later
Wolf3D text/playability report is a separate unresolved EDP compatibility issue;
Nurples is reported visually fine. The suite comparison work is accepted,
while the task retains the named follow-ups. Firmware identities remain
candidates; no measured performance result or broad game qualification is
claimed. The generalized-callback direction is included in this checkpoint,
with its interface still open for discussion.


## Deterministic graphics timing revisited — 2026-09-10

After the AUDIT-006 Nurples capture, the Author reports that delays were also
visible in these graphics fixtures and proposes automating the deterministic
suite and comparing completion times. The Author specifically proposes the
Pingo-style callback mechanism on both renderers and recognizes that this
requires temporary custom firmware on mainboard VDP and P4. This revisits the
earlier deferred benchmark; the earlier statement that no mainboard replacement
was implied describes that prior discussion, not a prohibition on this proposal.
No benchmark implementation, mainboard build or flash has occurred here.

The bounded proposal is to automate the vendored 24 Shapes pages and 123
Bitmaps stages, execute the whole ordered suite on mainboard and then EDP,
repeat from known per-renderer state, correlate each completion with its case,
and save each result durably on the Agon SD. Remove interactive pauses and
exclude deliberate settling, setup/asset I/O and file writes from the drawing
interval while reporting their distinct costs where relevant. Preserve staged
sprite/deferred-refresh/resource semantics. Time command submission separately
from completion notification; renderer-local intervals need equivalent start/end
boundaries and monotonic-clock conversion on each processor. Browser display
arrival remains a different measurement. Small finite cases alone cannot prove
that publication progresses under Nurples' sustained input.

The [existing Pingo notification contract][pingo-notify] and its source emit a
10-byte `P3DR` payload inside packet `0x81`, after a Pingo 3D render/output
finishes. Its request token, sequence and application mailbox are useful
precedent. Applying it to ordinary 2D drawing requires a verified queued-work
completion boundary; simply invoking the existing Pingo render callback does
not cover these fixtures or hardware-sprite scanout.

One material integration constraint was verified against the installed EMOS
v0.1.12 manifest: [emos_keyboard.c][emos-keyboard] validates mainboard key data
before invoking the user callback, so the `P3DR` down byte is rejected. Its
P4 receiver also faults a `0x81` packet whose length is not four. Consequently,
reusing the Pingo carrier verbatim requires an EMOS receive change as well as
mainboard/P4 instrumentation. Select an explicit completion-event carrier and
EMOS dispatch under D003; do not weaken ordinary keyboard validation or invent
a bypass to EMOS routing. The generalized callback product ABI remains open.

Prepare the mainboard reference from its selected stock source with only the
reviewed diagnostic changes, retain the current P4 behavior for the initial
comparison, and preserve exact original images/configuration for restoration.
Label both as instrumented builds. Do not replace the stock reference with a
broad unrelated Pingo development branch merely to obtain its hook. The exact
firmware changes, completion/clock semantics, EMOS integration and rollback
sequence belong in the next reviewed work contract before deployment.

### Nurples benchmark added; approval pending

The Author requested adding the repaired game to the suite: centred ship,
collision invulnerability, one minute of gameplay and automatic exit, no
confirmation/joystick steps, keyboard polling retained. The
[draft work contract](QUAL-003/benchmark-contract.md) records the bounded source
review, finite scroll/clipping cases, low-traffic completion strategy, source
and asset provenance, timing/output requirements and B1–B4 execution gates.
It supersedes the earlier deferral of this benchmark variant, but authorizes
only planning until the Author reviews the contract and D004.

The Author clarified that the modern source is `nurples-repair`. Read-only
verification confirms the installed game binary and containers used in the
hang capture match its committed `dev` state, including the joystick fix.
Newer uncommitted artwork remains outside this first comparison. P4's
per-pixel scrolling differs from mainboard's row-swapping path; the retained
viewport and bitmap paths appear to admit one-scanline clipping. Both require
measured comparison, not a speculative repair. No game or firmware source,
build, hardware state or removable media was changed during this review.

### Superseding priority — stock backend fidelity

The Author subsequently directed the whole stock/P4 video-generation comparison
to become priority one within AUDIT-006. This benchmark draft is retained for
later targeted verification; its earlier requests do not authorize implementation
while that source audit is the current task. No input-pattern answer is needed
to start the audit, and no temporary mainboard/P4 callback firmware is being
prepared. Revise the benchmark after the audit identifies the actual reuse and
adaptation boundaries.

[pingo-notify]: ../../../agon-vdp-pingo-v216-promotion/docs/pingo-render-completion.md
[emos-keyboard]: ../../../agon-emos/src/emos_keyboard.c


## Finite timing tranche reactivated — 2026-09-11

The Author explicitly redirects the next tranche from typing latency to the
already-proposed graphics torture tests, with temporary timing hooks in EMOS,
mainboard VDP and P4 EDP and automated durable results. Curate the existing
suite rather than start another audit. The current benchmark-contract section
and machine-readable case inventory govern the first run; preserve complete
page prerequisites and deliberately deferred sprite semantics. The restored
r10 backend replaces the historical flat-framebuffer baseline. Mainboard's
near-infallible 60 Hz operation remains the reference.

The Author reports smooth Legacy Nurples without reloading the binary and
improved ExCom typing with some residual latency, in addition to the marked
gameplay improvement and sprite-heavy slowdown. None of those observations
is a numerical benchmark. Deterministic Nurples stays deferred until this
finite suite indicates whether it is needed; D004 does not block this tranche.
D003's production callback model remains open; the bounded experimental
completion-event details belong in B1 before implementation. The existing
local validation/emulator review and rollback gates still apply.

## Finite timing implementation — 2026-09-11

Contract frozen in fc14f02. B1/B2 implementation now uses the bounded
[timing protocol](QUAL-003/timing/protocol.md): 64 cases, a normal-worker FIFO
fence, separate primitive/software-sprite/scanline counters, raw FAT result
files, and EMOS v0.1.13 source-owned reception. Mainboard and P4 diagnostic
images and SD application compile; paired emulator validation is in progress.
No physical firmware, SD card, reset or running-board state changed. Actual
mainboard backup and Author emulator approval remain deployment gates.

Offline validation now includes a complete 256-interval paired native result,
five malformed/stale reply cases, 17/17 sprite presentation checks, source
fidelity and all three firmware builds. See the bounded
[validation record](QUAL-003/timing/validation.md). The project UART emulator
helper needed a host-socket backpressure correction; it did not require a
production UART change. A separate native COMBINED timeout is retained as an
unresolved preparation observation, despite subsequent ordinary/traced passes.
Review that partial result if recurrence appears during the next gate; do not
discard or retry away a physical failure. Author visual validation is next.

## Visual review accepted — 2026-09-11

The Author supplied the completed 256-interval screen and MOS prompt and
authorized deployment. Promote the same reviewed EMOS v0.1.13, console r11
and graphics fixture r01 inputs to candidates under registry r70, then build
from clean commits. Preserve the mainboard's actual flash before replacing it.
Physical timing and restoration remain pending; the known native timeout and
two inherited pixel-probe disagreements retain their recorded limits.

## Timing candidates deployed — 2026-09-11

Clean candidate builds and deployment hashes are in
[timing/candidate-deployment.json](QUAL-003/timing/candidate-deployment.json).
P4 and the mainboard timing application were written and independently verified.
The complete installed mainboard flash was first read and independently verified;
the application update preserved its bootloader, partitions and persistent state.
EMOS v0.1.13 and all benchmark files are staged on SD; the one-time installer
runs first. Author confirmation of that flash and the later benchmark handoff
remain pending. No hardware timing result exists yet.

## EMOS installation accepted; benchmark armed — 2026-09-11

The Author reports a successful EMOS flash. The returned SD contains the
expected v0.1.13 payload in EMDONE.BIN and no unconsumed EMNEW.BIN. Replace
the one-time installer startup with the reviewed eight-command benchmark
startup. Preserve all existing results and rollback images. The physical run
now awaits the Author’s reset with one browser video client connected; collect
the closed CSV after MOS returns, including an incomplete result if it fails.

## QUAL-003-I004 — Mainboard population-stage stall observation

Status: open; physical result collection pending. On 2026-09-11 the Author
reports that the mainboard appears stuck at BSP-30, caption “8 active; two
aligned scanline groups,” with stationary sprites and scanout corruption.
The SD is not mounted on the workstation at this observation. No running-board
reset, flash or serial open was performed in response. Whether the browser
continues the paired workload is not yet confirmed.

1. The population stages intentionally contain no animation. The same caption
   occurs at BSP30_04/_10/_16/_22 (software/hardware, RGBA2222/RGBA8888).
   The photograph cannot identify which variant or repetition stopped. Recover
   the closed CSV before assigning an exact failing interval.
2. The selected official Bitmaps API’s “Hardware sprite limitations” section
   explains that too many sprite pixels on one scanline can overrun VGA
   generation. I002 already records abnormal mainboard BSP-30 output before
   this timing firmware existed. This is relevant precedent, not proof of the
   present cause or a reason to suppress this failure.
3. The added Scope constructor acquires the shared portMUX on every
   drawSpriteScanLine entry even with detail=0. Enabled timing also reads the
   timer and updates counters. Off therefore retains scanline overhead and
   cannot isolate untouched-stock behavior near its VGA timing limit. Review
   instrumentation interference before trusting this stage’s performance.
4. The diagnostic’s ten-second bounds apply to its explicit completion/reply
   waits. They do not bound the reused stock UART0 blocking output path:
   serial.asm UART0_wait_CTS loops until ready. If mainboard stops consuming,
   the SD app may remain inside an ordinary MOS output call and never reach
   its own timeout or final message. This is a possible mechanism, not a
   measured diagnosis; do not silently change stock MOS to address it.
5. Preserve the partial CSV and exact deployed images. Distinguish a display
   left unchanged after a route switch from a stalled application. The next
   repair/retest decision follows that evidence. No rerun or replacement
   firmware has been deployed in response to this observation.

### I004 result recovered — first physical timing attempt

[Preserved CSV and analysis](QUAL-003/timing/results/first-hardware-attempt/partial-analysis.json)
identify BSP30_22: **eight 34×34 RGBA8888 hardware sprites sharing a scanline
band**, after BSP30_21 (four sprites) completes. The file contains the exact
expected prefix: 114 successful intervals, one failed interval, 920 metric
rows, and a terminal FR_TIMEOUT (15) record. EMOS waited 1200 raw ticks
(nominal ten seconds) for completion after submitting the 260-byte stage.
The successful submission is below tick resolution, not literally zero-time.

All records belong to repeat 0, mainboard, detail=0. No EDP workload case or
enabled-duration pass was reached. The preceding software populations and
RGBA2222 hardware populations completed; the one pixel mismatch is the known
SHP23 expectation. This is an informative failed comparison, not a performance
pass or evidence that EDP stalled. The earlier possible unbounded UART wait
is not established as the cause: the CSV proves the application reached its
own timeout and persisted the terminal result. Its final screen message may
have been blocked or obscured by mainboard output failure.

Off still retains scanline hook locking and completion fences. The leading
hypothesis is mainboard scanout overload at this aligned RGBA8888 population,
potentially aggravated by instrumentation; it is not yet a measured causal
conclusion. The next proposed isolation is this exact population sequence in
mode 20 with the preserved original mainboard image and ordinary VDU traffic,
without private timing requests. Use that control to decide the safe workload
bound and required instrumentation correction before repeating the paired run.
Do not repair upstream rendering or silently omit the failed stage.

The original CSV remains on SD and is copied into tracked evidence. Autoexec
now retains mode/input setup and the benchmark working directory, but omits
LOAD/RUN to avoid unattended repeats. No processor was reset or reflashed.

## Author diversion: PingoWolf with Extender keyboard — 2026-09-11

The Author pauses the benchmark and requests the latest PingoWolf mainboard
VDP. The initial stock MOS 3.0.2 request was superseded by the explicit need
to retain Extender keyboard input. EMOS v0.1.13 and P4 console r11 therefore
remain installed. No stock MOS installer was staged.

The mainboard now runs `pingowolf-v0.1.0-alpha.1-b2026-09-11-09-40-21Z`, built from
the latest local committed pingowolf branch `1a78d9886005b7bdc5eee759d24150a16a22a321`
with vdp-gl ac2dd598 (the upstream dependency at that branch’s date).
Later audio_fix work was excluded and left untouched. Only the build stamp
and local dependency resolution differ from that committed source. Its
application SHA-256 is `8128cbebecef6393d32767480a8632101e8ae6002331e8e89df8a997afba7c40`.
The previous diagnostic application and partition/OTA layout were checked
before writing; the new application was independently flash-verified.

The Author’s current autoexec had Extender input commented out. Re-enable
`EMOS KEYINPUT extender` after `SET KEYBOARD 1`, preserving the chosen
Aginvadors directory and LOAD without adding RUN. Leave the SD mounted per
the Author. The timing suite remains disabled: PingoWolf has no private
graphics timing command, so the paired timing procedure requires its recorded
diagnostic mainboard image restored before a future authorized run.

## QUAL-003-I005 — Visible completion summary requested — 2026-09-13

Status: open, deferred until after the current framebuffer-first run. The
Author requests a clear on-screen message when tests end, with compact
pass/fail totals. Do not show a detailed test-by-test list: it will not fit.
The summary should identify completion versus an incomplete/failed run and
point to the detailed saved results. Display it outside measured intervals,
and ensure it remains visible after route changes and recovery. This is a
future fixture change, explicitly not part of the run already in progress.

- [ ] Add and validate the compact completion summary in a subsequent fixture revision.


The Author has video evidence of the second framebuffer-pass BSP30 stage 17
scanout failure and intends to provide it. The [video findings](QUAL-003/timing/results/framebuffer-first/author-video.md)
now record the received clip; it complements the preserved callback timeout and the report of
stage16 scanout errors. Receipt of the video does not block the independently
scoped 39-case baseline run with the full population-stress page excluded.
