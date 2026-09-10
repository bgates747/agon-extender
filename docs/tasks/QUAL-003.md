# QUAL-003 — Compare mainboard VDP and Extender EDP graphics

## State and scope

Status: EDP graphics-suite hardware visual review PASS, accepted for freezing.
Mainboard BSP-28–30 artifacts are reference-display observations. A separate
Wolf3D failure with EDP is deferred to PORT-004 at the Author's request.
Startup follow-up and callback/benchmark design remain open. Author requested paired graphics fixtures after accepted
ExCom console/Nurples gameplay. Vendor agon-utils Shapes and Bitmaps in this
task silo, then render each page/stage on mainboard VDP first and EDP second,
with one keypress pause after the pair. Native P4 USB remains the input source.
The source checkout contains other active work and remains untouched.

## Work items

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
