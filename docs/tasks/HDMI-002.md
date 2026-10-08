# HDMI-002 — 848×480 HDMI timing and centered 512×384 image

## Accepted r10 and next tranche — 2026-10-07

The Author reports beautiful gameplay and a correctly displayed **outro screen**
after exit, accepting the bounded r10 result. Preserve its exact tested bytes,
commit the source/evidence, and keep its rollback available. The Author approves
production version **v0.2.0**; native-bundle packaging and canonical paired
qualification are tracked in [RELEASE-001](RELEASE-001.md) before selection/tag changes.
This does not qualify untested fault recovery or all video modes.

The Author authorizes HDMI02-M03's next progression. Start with the existing
428×240 widescreen timing/pattern implementation and center 320×240 inside it.
Reuse the accepted clock/line totals and corrected r04 pattern; do not assume
that the monitor accepts this 240-line active signal. Stop for visual geometry
and stability review before integrating it into ordinary firmware. After that
gate, reuse the resident small-sprite fixture and a suitable existing game;
keep each stage's observations separate. No 320-wide native 4:3 signal is needed.


## Offline mode-transition investigation — authorized 2026-10-07

The Author selects the mode-switch investigation next. Reuse the retained
mode96-to97 failure and current r09 source; the bench remains assigned to another
project. Source review, host failure-injection tests and target compilation only.
No device access, flash, reset, SD operation or emulator cue. Preserve earlier
uncommitted work and immutable builds. No new timing/mode/scaling implementation.

HDMI02-L01 [x] Trace P4 renderer detach, swap cancellation, panel borrowing,
driver teardown and requested/old/default-mode fallback against the pinned
official mode contract and IDF5.5.5. Separate demonstrated defects from possible
causes of the recorded physical transition failure; retain a bounded précis.

HDMI02-L02 [x] Reproduce concrete lifetime/wait defects with maintained code
under host-controlled DMA completion, cancellation and initialization failure.
Apply minimal fixes that preserve DMA ownership and joined resource teardown;
do not add guessed buffer-reuse timeouts or bypass EMOS routing. Cover recovery
and repeated carrier changes, including resource cleanup after partial startup.

HDMI02-L03 [x] Run relevant existing regression checks and compile any changed
P4 code. Record exact results and remaining physical gates in HDMI02-O04, leave
all experimental images unflashed, then pause for Author review. A local pass
does not resolve the physical hang or authorize production promotion.

The [mode-lifecycle review](HDMI-002/MODE-LIFECYCLE-REVIEW.md) records two
reproduced waits and their bounded remedy. Actual-sink host tests cover driver-call
cancellation, preserved DMA ownership, same-carrier fault recovery, partial
startup failure and repeated carrier reconstruction. Experimental r10 compiles with verified source closure and archive hashes;
The later authorized physical tranche passes both Nurples runs and small sprite
checks; [r10 results](HDMI-002/R10-PHYSICAL-RESULTS.md) record its exact scope.
Physical mode96-to97 causality remains unresolved despite the passing retest.

## Offline wider-scanout investigation — authorized 2026-10-07

The bench belongs to another project. This tranche uses retained evidence,
source review, host tests and compilation only: no device access, flashing,
resets, network status reads, SD deployment or emulator attention cue. Preserve
the exact r06 rollback and all existing work. Do not claim a hardware fix from
an offline result, or start unrelated modes/performance work.

HDMI02-O01 [x] Compare 684×384 and 848×480 descriptor layouts, block ownership,
interrupt ordering, refill timing and joined teardown against pinned IDF5.5.5.
Separate concrete code defects from hypotheses about the recorded underrun.
Record a bounded source/evidence précis, including what the present counters
cannot establish.

HDMI02-O02 [x] Fix concrete defects within that path and add host regression
coverage exercising the maintained implementation with delayed/completing DMA,
faults and mode teardown. Keep timing, slot count, color precision and existing
safety limits unchanged unless a separately documented concrete defect requires
otherwise. Retain first-fault evidence so a later underrun cannot obscure the
initiating failure. Do not redesign the renderer or modify official references.

HDMI02-O03 [x] Compile the affected target firmware, run relevant existing host
checks, document results and pending physical validation. Leave the bench and
production selection untouched. No hardware claim, promotion or publication is
implied; pause for review after this bounded tranche.

Research baseline: official Agon mode/swap contract at agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`; pinned ESP-IDF
`b774170ff46c393eeb5e495ea37936038d3f4f4f` supplies DPI, DW-GDMA,
DMA2D and cache semantics. Preserve these versions rather than treating newer
online documentation as the installed implementation.

Findings and implementation are in the
[offline review](HDMI-002/OFFLINE480-REVIEW.md). The old runtime demonstrably
aborts a safe delayed-copy schedule before its 1,600-µs limit. A one-request
waiting queue reuses the pinned DMA2D EOF contract; no additional DMA transaction
may overlap. Host tests cover both geometries, true deadlines, unsafe reuse,
fault ordering and cancellation. This is a plausible remedy awaiting hardware
validation, not a retrospective determination of the blue screen's cause.

O03 outcome: experimental `rgb-001-r09-b2026-10-07-22-25-41Z` compiles and passes
target source/link/configuration validation. Runtime ASAN/UBSAN, existing scene,
HDMI scheduling and all12 build-selection checks pass. No hardware access,
flash, reset, SD change or production promotion occurred. The actual r06
rollback remains retained; the other project's bench state is not rechecked.
The next physical gate reuses the small sprite fixture, wide3600-update Nurples,
mode20 regression control and native-depth carrier transition. Capture first-fault
detail before recovery if anything fails; execution awaits bench release and
Author review rather than starting automatically.

HDMI02-O04 [ ] **Bounded physical run passed; Author review and physical
fault-recovery coverage remain, 2026-10-07.**
The Author has restored stock mainboard VDP, released the bench and authorized
the bounded r10 physical tranche below. Reuse the prepared tests; if a new
failure requires substantial investigation, preserve evidence, recover and pause.
The Author previously reconfirmed the hold after the offline report. Once the Author
returns the bench, re-read its current owner/handoff before preparing deployment;
do not assume another project's installed firmware is still r06. Verify the
retained candidate and rollback bytes, then reuse the small sprite fixture,
mode96 3,600-update hardware Nurples, mode20 control and lower-color/native
carrier-transition check. Capture first-fault reason/detail and queue counters
before recovery. Verify complete game records, input/exit and restored startup.
Report the physical outcome separately from the passing host tests; this entry
did not authorize automatic execution on availability; the later explicit
authorization above covers the completed bounded tranche.
The subsequent L tranche prepares r10 with both the r09 refill change and the
mode-lifecycle remedy. Preserve r09 as a separately identifiable control rather
than silently replacing its evidence. Include cancellation/fault recovery and
same-carrier96-to97 changes as well as the two physical carrier sizes; no host
pass establishes those physical outcomes.

O04 result: r10 is installed/verified; mode96 and mode20 each complete3,600
Nurples updates at nominal60/s, with57.125%/57.25% median headroom and matching
game-state trajectories. Both small sprite checks, including96→97 in autoexec,
pass. Startup/configuration are restored and normal input re-admitted. No
physical fault was induced; recovery after one remains unqualified on hardware.
See [r10 physical results](HDMI-002/R10-PHYSICAL-RESULTS.md). Pause for playtest;
do not start240-line modes or new fault-injection work automatically.

## Faster 480-line output — authorized 2026-10-07

The Author accepts the full-width pattern and authorizes adapting the faster
rolling path to 848×480. Keep the physical timings and EMOS-routed VDU API.
Nurples is the performance target: use the existing deterministic hardware
fixture in mode96, retaining its 512×384 game coordinates inside the larger
logical canvas. Do not rewrite gameplay or claim that an ordinary executable
which selects mode20 is exercising mode96. Compare retained mode20 trajectory
and PRT headroom; distinguish application, presentation and DMA rates.

HDMI02-F01 [x] Extend the existing three-slot, 32-row DMA scanout to both proven
carriers at joined mode boundaries; preserve immutable sprite snapshots, exact
pixel semantics, late-refill containment and the 684 path. Max-size848 slots
need47,232 extra internal bytes. Use IDF's existing external-stack APIs for
bounded task-only drawing/output/network/SD workers, preserving sizes, priorities,
affinities and matched deletion; keep IRQ stacks, RTOS controls and DMA internal.
Review those paths for cache-disabled/flash operations first. No two-slot timing
shortcut, reduced color precision, or clock change. Enable panel-direct RGB888
only for the added64-color848×480 geometry; native lower depths remain supported
without a new performance promise. Record actual memory headroom.

HDMI02-F02 [x] Reuse host pixel/sprite/ownership checks, adding full-width edge
and runtime-carrier cases. Build/validate a source-identified candidate with exact
r06 rollback. Reuse small resident sprite cases first, including mode96 then a
lower-color/native mode. Retain errors instead of treating scanout60Hz alone as
successful rendering. No standalone SDK edits or upstream-reference changes.

HDMI02-F03 [x] Flash/readback, run the3600-update hardware Nurples
fixture with mode96 selected only in startup. The retained r03 fixture explicitly
rejects every mode except20; reproduce it exactly, then build an identified r04
companion changing only that admission check, its error text and build identity.
Keep r03 for the mode20 control. No gameplay, asset, input or timing changes.
Verify complete PRT records and
state trajectory, input/exit, scanout counters and loaded internal memory.
Exercise return to the684 carrier and back to480. Restore/read back original
startup and fixture configuration, preserve ordinary game files, then leave a
working candidate for Author review; fall back to r06 if the experiment fails.
Document performance and limits. Stop before240-line work or broad qualification.

F01–F02 implementation/checks are complete as an experiment, **not accepted
firmware**. Small mode-96 sprite output reaches approximately 60 images/s, but
two longer Nurples runs stop presenting. The diagnostic run records a DSI
underrun after 730 presentations; the Author confirms the blue-screen failure.
The bounded investigation and rollback are recorded in
[rolling 480-line results](HDMI-002/ROLLING480-RESULTS.md). Do not use the failed
r07/r08 images as the new gameplay baseline or infer success from a full-sized
SD result file with its abort flag set.

F03 closes as a **failed wider-path experiment with successful recovery**.
The unchanged mode20 control passes3600 updates at60/s, with the same recorded
game trajectory and about57% median active-work headroom. Original startup,
fixture config and both ordinary games pass full readback. Exact r06 is restored,
all four flash segments verified, and a fresh Agon boot has admitted neutral
Extender input and a verified Legacy CLI. The foreground listener is stopped;
no test/capture/input automation remains. Preserve r07/r08 source and evidence,
but do not deploy them as an accepted upgrade. Further remedy selection is a
discussion boundary; no240-line work or broader qualification has begun.

Research boundary: retain the official VDU22/sprite contracts and commits below.
Pinned IDF5.5.5 supports `xTaskCreatePinnedToCoreWithCaps`,
`vTaskDeleteWithCaps`, and HTTP server `task_caps`; their task stack placement
must not be mistaken for moving task controls or interrupt stacks to PSRAM.
The selected drawing, output and socket/FAT handlers perform no flash/NVS/cache-off
operations. Re-review this boundary if such operations are later added.

## Full-width 480-line drawing — authorized 2026-10-07

The Author selects widescreen480p next. Reuse the proven848×480 signal
(0.625% narrower than exact16:9), exposing its whole drawable area without
altering stock mode IDs or the accepted384-line Nurples path. This first pass
uses the existing native compositor; it does not promise60 newly rendered fps.

HDMI02-W01 [x] Add experimental single-buffer modes96/97/98/99 for848×480
at64/16/4/2 colors, restricted to the automatic-HDMI build. These IDs are unused
in the reviewed stock table and provisional, not a released API allocation.
Retain EMOS-routed VDU22 selection, stock drawing/palette/sprite behavior,
fallback and metadata. No DB variants, new scaling, clock changes or rolling848
optimization in this first pass. Record full-width architecture and build scope.

HDMI02-W02 [x] Compile/validate a source-identified rgb-001-r06 candidate;
reuse the existing renderer checks and render-load-r04 sprite fixture with new
parameter data. Prepare a simple full-width edge/color/aspect pattern reusing
the existing VDU fixture wrapper. Select all fixture modes only in startup.
Preserve exact r05 rollback and original startup/game files.

HDMI02-W03 [x] Flash/independently verify, check input readiness and run bounded
sprite cases in all four depths. Restore/read back original startup; show the
full-width64-color pattern for Author visual review with no unattended input
left running. Retain failures and results, then stop. Do not start240-line work.
Implementation/bench portion complete: all four checks pass; original startup
is restored/read back and the full-width pattern is running. Author confirms the pattern looks good. No host automation remains.
This accepts the bounded geometry test; canonical qualification and an agreed
release version remain prerequisites for production promotion.

Progress and retained identities: [full-width results](HDMI-002/WIDE480-RESULTS.md).

## Mode inventory and discussion gate — 2026-10-07

HDMI02-I01 [x] Inventory stock mode IDs, geometries, depths, double buffering,
legacy remapping and refresh rates against the installed carrier selector and
retained evidence. Record cropping, renderer differences and untested cases in
the [mode inventory](HDMI-002/MODE-INVENTORY.md). Documentation/source review
only: no build, flash, input, SD operation or hardware test in this tranche.

HDMI02-I02 [x] Discuss the inventory with the Author before implementing anything
else. Open decision HDMI02-D240: prefer a new small widescreen carrier for
320×240, 2× enlargement into848×480, or retain current unscaled684 presentation?
Recommendation and tradeoffs are in the inventory. A new carrier first requires
a static physical timing test and strip-layout review. Integer enlargement would
require an explicit amendment to ADR-0024's unscaled policy. Neither route nor
any new full-width logical mode is authorized by this inventory.
Disposition: Author chooses full-width480p first, under W01–W03 above. The240-line
alternatives remain deferred; the inventory itself authorized no implementation.

## Runtime carrier selection — authorized 2026-10-07

The Author directs HDMI timings to follow Agon mode changes using the proven
684×384 and848×480 carriers, then inventory remaining modes. Preserve512×384
games centered in684×384 and640×480 text centered in848×480; no scaling or new
320×240 physical timing in this tranche. For now smaller logical images use
the smallest proven carrier that fits; oversized images retain explicit
center-cropping on848×480 pending the separate inventory.

HDMI02-R01 [x] Implement explicit runtime carrier selection in an experimental
build, retaining fixed-build options and exact rollback images. P4 handles the
ordinary EMOS-routed VDU22 mode change: detach/join native drawing and output,
retire borrowed panel references, stop scanout/DMA, release driver resources,
then initialize the selected proven timing and publish the replacement mode.
Use core1 for DSI/bridge lifetime. No live descriptor or clock edits, no upstream
reference changes, and no bypass of EMOS routing. Same-carrier mode changes keep
the existing candidate lifecycle. Physical carrier changes necessarily retire
old panel storage; failures return to stock requested/old/default-mode fallback.

HDMI02-R02 [x] Test selection, centering, repeated driver lifecycle and unchanged
Nurples sprite/scroll composition. Keep684 rolling scanout and its memory remedy;
reuse ordinary full-frame scanout for848 (three848 rolling strips need47KiB more
internal RAM than684, exceeding the measured loaded reserve). Sprites remain supported in every mode through the existing compositor; speed
is a separate qualification. Reuse the resident render-load-r04 executable for
a bounded16-sprite check in640×480 modes0/1/2 (16/4/2colors), with tiny
parameterized data and mode selection only in temporary restored startup.
Do not add64-color sprites over indexed backgrounds in this tranche. Build/validate a source-identified
candidate; exercise compile-time guards and truthful runtime output metadata.

HDMI02-R03 [x] Flash/readback verify, then use existing fixtures/ordinary games
for bounded transitions:480-line prompt,384-line game, title and low-resolution
fallback, return to480-line prompt, and repeated transitions. Verify input,
complete upper text, continuing DMA, resource recovery and absence of faults.
Retain exact firmware, status, text/serial and Author visual evidence. Preserve
SD startup and games; leave working input and the successful candidate for review.
Use the existing short/marked Nurples fixtures when needed, not a new benchmark
campaign. Do not start unproven240-line or full-width mode work automatically.

R03 status: build, flash/readback, three ordinary-game round trips and the
16/4/2-color sprite checks pass. After startup restoration and one short
handback run, the Author confirms “Yes, upper text is visible” on the actual
monitor. This closes the missing-row remedy's visual gate.
See [runtime results](HDMI-002/RUNTIME-RESULTS.md) for the rejected first image,
SRAM reservation remedy, installed identity and bounded validation.

Research: official agon-docs `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
[screen modes](../../../../agon-docs/docs/vdp/Screen-Modes.md), VDU22 logical
mode and old/default fallback contract. Pinned IDF5.5.5 DPI create/delete and
unmodified Olimex bridge init/delete are the hardware lifecycle authority;
retain the existing generated DPI derivative's exact upstream hash guard.
The reference VDP and SDK remain read-only. ADR-0024 now permits selecting a
proven carrier at a logical-mode boundary rather than one fixed carrier per build.

## Executive summary

Current development state: automatic carrier selection is installed and passes
the bounded hardware checks above. The Author visually confirms that the former
fixed684 mode0 crop is gone. The following
paragraphs retain earlier milestone evidence, not the current installed selection.

The visually accepted848×480 timing is now integrated with the accepted Nurples
scroll renderer. One3600-update deterministic run passes at nominal60 updates/s,
with zero faults and53% of the frame budget used at the active-work95th percentile.
The ordinary repaired game subsequently passed bounded Author review. Its512×384 image is
unscaled at(168,48):168-pixel side margins and48-line top/bottom margins.
This is custom PLL timing at calculated60.069440Hz, not exact DMT0Eh.
EMOS, ordinary game bytes and production selection are unchanged; temporary SD
startup/config edits were restored and independently read back before handover.

[Detailed timing lessons](HDMI-002/TIMING-LESSONS.md) distinguish the probable
r10 clock fault from unresolved later 640×480 failures and record requirements
for lower active-height signals. The first standalone512×384 signal fails Author
review: flicker and repeated picture loss despite approximately60Hz DMA progress.
The Author clarifies that512×384 is the logical game image, always centered in
a widescreen HDMI carrier. The684×384 standalone trial is now flashed and
readback-verified, with approximately60Hz DMA. The Author confirms stable output,
correct circle/square proportions and a complete outer border; the reported
geometry concern was misplaced fixture labels. The centered512×384 pattern
follow-up corrects those labels and adds86-pixel sidebars; the Author confirms
that layout correct and steady. Initial full684-wide runs exposed internal-memory
exhaustion and a buffer-cleanup crash, despite promising flicker-free output.
The latest bounded placement remedy completes marked3600-update hardware Nurples
at nominal60/s with57% median active-work headroom and about22KiB internal RAM
free. Ordinary menu/mode changes, Escape cleanup and CLI commands also pass.
This actual684 candidate remains installed for Author play review. Automatic SD
admission after ordinary exit rejects in ExCom but recovers through EMOS Legacy
without reset; that service issue and slight tearing remain open. See
[memory remedy results](HDMI-002/MEMORY-RESULTS.md) and the retained
[initial integration failures](HDMI-002/FULL-WIDE-RESULTS.md).
The848×480 image is service recovery only for hardware Nurples, not a working
playtest rollback. See [native timing results](HDMI-002/NATIVE-TIMINGS.md).

## Contract and ownership

The P4 generates RGB888 pixels, supplies DSI timing and configures its onboard
LT8912B over I2C. The bridge transmits HDMI to the connected monitor. The Pi
builds, flashes, verifies and captures USB serial diagnostics. The Author judges
the actual monitor image. Local wiring, device identities, paths and rollback
receipts remain in `HARDWARE.local.md` and ignored `agents/hdmi002/` records.

Use artifact `hdmi-timing-r02`, experimental status, under the Author's standing
identity preapproval. Preserve the exact accepted `rgb-001-r02` Nurples image
for rollback. Temporarily replacing P4 firmware stops Extender input/network
services; the standalone image must not communicate with or reset the Agon,
mount either SD card, or configure the Agon UART/parallel harness pins.

### Bounded steps

HDMI02-01 [x] Review prior 640×480/720p experiments and pinned clock/bridge code;
freeze this bounded contract before building or deploying.

HDMI02-02 [x] Implement the smallest standalone test using the existing bridge
component and proven board initialization. Paint color bars, labelled corners,
continuous outer edges, pixel checks and aspect shapes around/inside the centered
512×384 region. Check native pattern memory bounds and channel order; compile
with the pinned native P4 toolchain and record exact inputs and output hashes.

HDMI02-03 [x] Revalidate rollback, USB identity and silicon compatibility;
flash and readback-verify this standalone image. Record startup, actual configured
clock and DMA frame completion progress independently of picture correctness.
If necessary, make only bounded changes required to get this timing/pattern
running; retain each meaningful failed configuration and its evidence.

HDMI02-04 [x] Leave the static pattern running with a sentence-case visual
validation cue. Ask the Author to check visibility, all four edges, colors,
centering and aspect. Stop for review. Counters do not substitute for this gate.

No games, renderer integration, scaling implementation, benchmarks, release
promotion, new video modes or downstream work are authorized by this contract.

## Research and reuse

| Property | First candidate |
|---|---|
| Active image | 848×480 RGB888, 2544-byte stride |
| DMT identifier | 0Eh; not a CTA VIC |
| Pixel clock | APLL 33,750,000 Hz, DPI divider 1 |
| Horizontal front/sync/back | 16/112/112 pixels; 1088 total |
| Vertical front/sync/back | 6/8/23 lines; 517 total |
| Sync | Positive H and V |
| Calculated refresh | 60.0004267 Hz, not a measured frequency |
| DSI | Two 540 Mbps lanes; default legacy 20 MHz PHY reference |
| HDMI metadata | VIC 0; 16:9 aspect hint |
| Centered image | 512×384 at 168,48; no resampling |

848/480 is approximately 16:9, not exactly. Monitor handling and EDID support
remain physical review questions. The centered image itself is 4:3.

1. [VESA DMT 1.13](https://glenwing.github.io/docs/VESA-DMT-1.13.pdf),
   DMT 0Eh timing table; independently present in the
   [Linux DMT table](https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/drm_edid.c).
2. [Prior scanout comparison](P4PC-001/SCANOUT-COMPARISON.md): 640 r10 used
   APLL 25.2 MHz but produced zero DMA completions; r11–r13 produced roughly 60
   completions/s without an acceptable picture. r12 aligned lane/pixel clocks;
   r13 changed receiver settle and post-start relock without solving the picture.
   Do not carry those unproven changes into the first candidate.
3. Reuse initialization and RGB888 byte order from
   [`hdmi_output.cpp`](../../vdp/video/extender/display/hdmi_output.cpp), plus
   the static-pattern and evidence lessons from
   [`p4pc-demo`](../../vdp/p4pc-demo/README.md). Omit its unrelated LVGL,
   SD/audio/network/peripheral startup, because the Agon is connected now.
4. Retain the unmodified Olimex LT8912B component at source commit
   `04032d68e5c727870f9d40beb9e37b7ab3a66916`; provenance is
   [`UPSTREAM.json`](../../vdp/components/esp_lcd_lt8912b/UPSTREAM.json).
   Its integer `pclk_mhz` affects only its disabled internal test-pattern path.
5. ESP-IDF 5.5.5 commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`:
   `components/hal/mipi_dsi_hal.c` rounds PLL240/7 to 34.285714 MHz and adjusts
   the DPI horizontal porch. That is unsuitable for an unchanged 33.75 MHz DMT
   bridge configuration. APLL 33.75 MHz is exactly representable with 40 MHz
   XTAL (`o_div=4,sdm2=6,sdm1=32,sdm0=0`); runtime operation needs proving.
   The silicon 1.3 legacy PHY supports exact 540 Mbps (M54/N2), giving a 2:1
   byte-clock/pixel-clock ratio and integer horizontal byte-clock intervals.
   A requested 405 Mbps instead becomes 400 Mbps. Do not assume requested clocks
   equal realized clocks or modify the pinned SDK reference.

## Results and next gate

### Pre-deployment correction: supported clock on silicon 1.3

The first contract is retained locally with SHA256
`8cb00e92c50919be7314383f64519fcf86ffe02032b174133f866817cc3c7a5a`.
The exact-DMT/APLL design was **not deployed**. Deeper review found that
Espressif introduced DPI selector 3/APLL in
[commit be2b6efa](https://github.com/espressif/esp-idf/commit/be2b6efadc559596c22071ffec90423ea962c6e1),
associated with silicon 3.0. The
[official TRM](https://documentation.espressif.com/esp32-p4_technical_reference_manual_en.html)
pre-release v0.7, 2026-08-20, page 1128/register 11.16 lists:

> 0: XTAL_CLK 1: PLL_F240M_CLK 2: PLL_F160M_CLK 3: Invalid

Its newer DSI diagram also includes APLL: preliminary documentation has mixed
revision coverage. Alongside earlier r10's zero-DMA result, this is strong reason
to avoid APLL on this 1.3 specimen, not a vendor-confirmed defect. PDF SHA256:
`622fe9625d19cf00bd7aa49e65f0b5dd6ef2197f83cb7a88b4405078d6a957d4`.

The deployed candidate therefore uses the supported PLL240/7 source, requested
as `240.0f/7.0f`, and two 480 Mbps lanes. Horizontal front/sync/back becomes
32/112/112, total 1104; vertical total remains 517. Calculated refresh is
**60.069440273 Hz**. The byte/pixel ratio is exactly 1.75, all horizontal fields
map to integer byte clocks and the SDK's compensation is zero. This is explicitly
**custom 848×480 near 60 Hz**, not exact DMT 0Eh. Image size/centering and the
visual gate remain unchanged. No unsupported register setting is used.

### Bounded physical result —2026-10-07 UTC

**The Author confirms a visible, pleasing picture: “that is a beautiful sight.”**
The static pattern remains running. No further experiment, game or product
integration follows automatically. This establishes useful output on the connected
monitor; no photo or separate edge/color/aspect verdict has been supplied.

| Check | Result |
|---|---|
| Installed build | `hdmi-timing-r02-b2026-10-07-02-26-42Z` |
| Factory SHA256 | `16e41d49d07595f3dc7ee4d3f06cb9d7d7f9e23e3d5c2bbc3321c36a68a978e9` |
| Build | Native ARM, pinned IDF5.5.5; source closure and merged segments verified |
| Pattern host checks | ASan/UBSan: bounds, stride padding, colors, edges and centered image pass |
| Flash | Bootloader, partition table and application independently readback-verified |
| Silicon | Both image headers admit actual P4 revision 1.3; no header patching |
| Clock readback | DPI selector 1 (PLL240), divider 7 |
| Frame DMA | Four approximately 5-second intervals: 59.998,60.176,59.976,59.976 completions/s |
| HDMI hot-plug | Detected throughout retained capture |
| User review | Visible picture confirmed positively; detailed geometry/color verdict not separately recorded |
| Other devices | No Agon reset/communication, firmware change or SD write |
| Stop state | Standalone pattern held; normal P4 network/input/SD services intentionally absent |

The short DMA count is a progression check, not a calibrated pixel-clock or
monitor-refresh measurement. Calculated60.069440 Hz and observed completion
counts have different scopes. Production and the accepted Nurples renderer are
unchanged; the exact prior image remains available for rollback.

Build configuration must explicitly set `CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y`
as well as the minimum revision. IDF otherwise silently selects 3.1 despite the
old minimum-revision option. The deployment guard caught that before flashing;
the builder now validates both image headers too. No incompatible image reached
the board. Source is [`vdp/hdmi-timing-test`](../../vdp/hdmi-timing-test/README.md).

Registry validation passes independently. The broader existing version-record
validator stops on the pre-existing `light2-harness-r02/connectivity.yaml` hash
mismatch; this experiment did not change that frozen hardware profile.

Exact source snapshots, manifests, build logs, flash/readback receipts, USB
capture and result summary are retained under ignored `agents/hdmi002/`.
Future work requires Author selection; this experiment is not production
qualification or authorization to replace the normal Extender image permanently.

## G tranche — centered Nurples integration, authorized2026-10-06 local

The Author now requests the next step: run Nurples centered at512×384 inside
the proven848×480 output. This supersedes the previous static-only stop for this
bounded tranche. Preserve both the static pattern and accepted720p Nurples image
as exact rollback artifacts. The P4 continues using EMOS-owned UART routing;
EMOS firmware and the ordinary game binary/assets are unchanged.

HDMI02-G01 [x] Add explicit848×480 timing selection to the maintained P4 build,
using the exact visually accepted clock/DSI/bridge tuple. Reuse existing centered
panel geometry and accepted partial-scroll copy implementation. Preserve720p
as the default build option; expose truthful output geometry in diagnostics/UI.
Freeze an experimental `rgb-001-r03` image and verify geometry, renderer/scroll
regressions, compiled source selection and silicon compatibility.

HDMI02-G02 [x] Flash/readback-verify the P4 image; recover EMOS input admission
through the existing startup/reset path if required. Reuse one finite3600-update
deterministic repaired-Nurples run, retaining its timing and correctness data.
Use the existing SD fixtures and new task-local evidence paths. Preserve/restore
startup and any edited fixture configuration byte-for-byte. No full benchmark
suite or unrelated game test is implied.

HDMI02-G03 [x] Stage the current ordinary nurples-repair build on the HDMI output
for the Author's playtest with working input. Record installed state, timing
limits and observations, then stop. Do not infer acceptance of all video modes,
permanent product selection or further optimizations from a successful smoke.

### G01 implementation and deployment

The full image `rgb-001-r03-b2026-10-07-02-45-45Z` compiled and passed source,
profile/link, dependency-lock and silicon-header checks. Its dependency lock and
partial-scroll renderer bytes match the accepted720p candidate exactly. Factory
SHA256: `c41d7974f9d734a1464155f02fec3ed3bf122e3e26b21e52306e9b6bf95bacad`.
The agent flashed and independently verified every segment. HTTP reports848×480
HDMI and admitted, neutral keyboard input after the normal Agon reset/startup.

Host checks passed for both output geometries, the848-stride real renderer
(scrolling, clipping, sprites, overlays and swaps), eight build-selection checks
and the headless browser's truthful HDMI status/keyboard path. No game source,
EMOS image, bridge-driver source or production selection changed. The retained
one-case run and ordinary-game review remain separate gates below.

### G02–G03 result and stop state

The same retained `scan-scroll-suite-r02-b2026-10-06-23-03-19Z` T09 fixture ran
120 warmup updates followed by3600 measured updates. Every retained simulation
checkpoint, phase, actor/projectile count, map row and RNG matches the earlier
mainboard run. Peak population is five enemy-table actors and four player
projectiles. This is the existing deterministic scene, not a maximum-sprite test.
[Machine-readable result](HDMI-002/NURPLES-RESULT.json) retains counts and hashes.

| Measurement | Newly tested848×480 HDMI |
|---|---:|
| Recorded game updates / faults / late updates | 3600 / 0 / 0 |
| Nominal application updates/s | 60.00 |
| Active-work frame budget: median /95th percentile / maximum | 42.7% /53.0% /70.1% |
| Remaining active-work headroom at95th percentile | 47.0% |
| Final completion drain | 3.49ms |
| P4 correlated window duration | 60.062344s |
| P4 submissions/s / DMA frame completions/s | 60.071 /60.071 |

Retained mainboard comparison below uses the identical deterministic trajectory;
it was not rerun. Busy intervals first, ranked by the new candidate's95th-percentile
active work. Relative change =100×(new P4 active time/mainboard active time−1).
These percentages describe the nominal16.667ms game-loop budget, not CPU use.

| Live enemy-table actors | Updates | Mainboard median /p95 budget | New P4 median /p95 budget | P4 p95 change vs mainboard |
|---|---:|---:|---:|---:|
| 3–5 | 995 | 49.6% /70.4% | 47.7% /55.3% | −21.5% |
| 1–2 | 1921 | 34.2% /64.4% | 42.3% /52.3% | −18.8% |
| 0 | 684 | 19.7% /43.0% | 30.1% /38.8% | −9.7% |

PRT uses nominal72kHz and raw MOS time nominal120 units/s; these are not external
clock calibrations. Active work includes eZ80 execution, MOS output and blocking
before pacing. The game runs naturally pipelined, without per-update completion
queries; its final drain is separate. HDMI DMA completion/submission counts do
not establish optical coherence or input latency. The fixture has no visual frame
marker, so the diagnostic's marker-invalid count is expected and is not a fault.
A short USB log and sparse HTTP status reads occurred during this smoke; unlike
the earlier quiet comparison it is not a tightly controlled timing repeat.

Setup took approximately70s, the P4 measurement window60.06s, and host reset to
observed foreground-listener return approximately110s including startup, loading,
result writing and observation delay. Retrieval took approximately36s. These
scopes are separate; no completion estimate became an automatic reset deadline.
No streaming browser or image capture operated during the timed run.

Original38-byte startup and original fixture configuration were restored, then
independently read back through the ordinary SD service. Agent launched the
unchanged current repaired `/mystuff/arcade/nurples.bin`; SHA256
`63c89d2676f6645631b2240f23002b8b68d45069979a4804ca7d14f34e720088` matches
the repair checkout's built artifact. Live status reports mode20,512×384,64colors,
single-buffered RGB888 panel-direct inside848×480, with keyboard ready, neutral
and no held/queued keys. No test window remains open and no counter overflowed.
The ordinary game remains for Author review; the agent schedules no more input
or reset. Detailed flicker, geometry and physical-input acceptance remain pending.

Evidence is under ignored `agents/hdmi002/nurples`; the SD result and preserved
test inputs are under `/agents/extender/results/hdmi002-g01`. Both rollback images
remain retained. No commit, push, promotion, new logical widescreen game mode or
native512×384 signal experiment was performed in this tranche.

### Author gameplay observation — 2026-10-06

The Author's next selected experiment is the separately scoped
[SPRITE-001 hardware-sprite Nurples trial](SPRITE-001.md). It changes the game
branch and deploys a distinct executable; this HDMI image is held unchanged.
Its first Author review passes on mainboard but fails badly on Extender with
near-stalled gameplay and slowly appearing/disappearing sprite rows. Small
diagnostics are recorded in that task; the earlier software-sprite improvement
does not qualify this hardware-sprite path.

Author reports a major improvement: no bad flickering noticed in very busy
scenes. Bad flicker was noticed during the player-death animation, which the
Author intends to retry. Possible slight tearing remains an uncertain observation,
not a diagnosed monitor timing fault. Current custom signal is calculated
60.069440Hz. Mode20 remains single-buffered; CPU drawing into memory being
scanned is a plausible source-side tearing mechanism even with stable sync.
Monitor internal panel synchronization/rate conversion has not been measured.
No new test, firmware change, death-animation remedy or production promotion
is implied by recording this report.

## Authorized return to video modes — 2026-10-07

The Author directs the agent to resume video modes, unattended. The initial
request makes this conditional on SPRITE-001 integration, then explicitly
reiterates “get back to working on video modes.” Native standalone pattern work
therefore proceeds while the independent full-application SRAM integration
constraint remains recorded; no sprite/game qualification is implied. The existing carrier is848×480, with
512×384 centered in it. Keep that known working timing as rollback.

HDMI02-M01 [x] Investigate and test a roughly60Hz widescreen HDMI signal with
384 active lines, starting at684×384. The Author's2026-10-07 clarification
supersedes a standalone4:3 signal as the target: logical512×384 remains centered
unscaled with black sidebars,86 pixels each at684-wide. Retain the failed512-wide
experiment as evidence, not an integration prerequisite. Reuse the supported PLL/divider and retained LT8912B/DSI timing lessons;
calculate blanking, lane bandwidth, legal DMA block geometry and monitor
acceptance independently. Start with an edge/grid/color pattern before game
content. Record calculated versus observed timing; HPD and a60Hz DMA counter
alone do not prove the monitor accepts the picture. If no operator is present,
leave physical picture acceptance explicitly pending.

HDMI02-M02 [ ] The widescreen signal and centered test image pass physical
review. Next integrate
centered512×384 output and explore applications using the full widescreen logical
geometry. Record integer dimensions and aspect rounding; do not stretch a4:3
framebuffer or change legacy mode IDs. Select a trial logical widescreen mode
only after checking the stock mode table and supported geometry alignment.

HDMI02-M02a [x] Build the full P4 rolling image for the exact reviewed684×384
signal, keeping512×384 centered at(86,0). Retain stock sprite painting,12blocks,
three32-row SRAM slots and1600µs refill abort. Check geometry agreement between
the C DMA derivative and C++ output, renderer offsets, and source provenance.

HDMI02-M02b [x] Pi flashes and verifies the image; P4 must establish normal
Ethernet, local SD, USB and EMOS input before draw fixtures. Run existing mode20
one-hardware-sprite and16-hardware-sprite cases with fresh result paths. Observe
refill/underrun and service state separately from application timings. Preserve
exact original Agon startup and verify restoration. Ordinary848 firmware and
the accepted standalone684 pattern remain rollback options.
Completed with bounded service/agent-input checks and clean cases50/54; physical
USB keystrokes were not separately exercised. Detailed results are linked above.

HDMI02-M02c [ ] Only after those checks, run the existing3600-update repaired
Nurples hardware-sprite companion, preserving game/config bytes and retaining
durable timing and correctness results. Restore temporary startup/configuration,
then hand over ordinary hardware-sprite Nurples for visual/play review if ready.
Do not claim a DMA counter alone proves flicker-free gameplay. No full campaign,
logical widescreen mode allocation or production promotion in this tranche.
Current gate: the allocation failure is proven, bounded placement remedy built
and flashed, marked3600-update records pass, and ordinary game entry/mode
changes/Escape/CLI work without reset. Original startup/configuration are
restored and the exact successful684 candidate remains installed. Author manual
review of this candidate is pending. Retain the separate ExCom SD-admission503
after exit: Legacy restores access without reset; establish whether that behavior
predates the memory change before proposing an EMOS/transport remedy. No upstream
lock workaround or broader mode work in this continuation.

HDMI02-M02c continuation,2026-10-07: Author reports the restored848 image is
not working for hardware-sprite Nurples. It is a service-recovery image, not a
gameplay-ready rollback. Continue the684 renderer remedy without offering that
old image as a playtest. First use IDF's explicit allocation-failure abort in a
separately identified diagnostic build to capture the first failed allocation;
preserve its core before recovery. Then make a bounded memory-placement change
supported by that evidence, retaining sprite/scroll semantics, queue capacity,
three scanout slots and HDMI timing. Re-run the deterministic3600-update fixture,
service checks and clean exit; restore original SD files and leave the actual
successful candidate installed before announcing manual Nurples readiness.
[Memory results](HDMI-002/MEMORY-RESULTS.md) records the first failed84-byte mutex
allocation and the bounded PSRAM-placement candidate.

HDMI02-M03 [ ] Repeat the same focused progression for320×240 logical images
centered in a widescreen carrier, and applications using its full width.
Distinguish low-resolution logical pixels, pixel/line repetition,
and actual HDMI active timing; do not claim a native signal when using a larger
carrier. Reuse prior fixtures where applicable, preserve safe recovery, and
record any bridge/monitor restriction before broadening supported modes.

These are follow-ons to the current sprite integration, not prerequisites for
its completion or production promotion. The Author explicitly reiterates that
the next priority is returning to video-mode work.

### M01 experimental timing selection

The first native-active candidates keep the accepted PLL240/7 clock, two480Mbps
DSI lanes,1104×517 totals,+H/+V and VIC0. Only active dimensions and front porches
change. This preserves calculated60.069440Hz frame cadence and31.055901kHz line
cadence while separating native-active geometry from clock selection. A larger
front porch is blanking, not framebuffer pixels; these candidates do not send a
small picture inside an848-pixel black canvas.

| Active pixels | H front/sync/back | V front/sync/back | Aspect hint | Active framebuffer bytes |
|---|---|---|---|---:|
| 512×384 | 368/112/112 | 102/8/23 | 4:3 | 589824 |
| 684×384 | 196/112/112 | 102/8/23 | 16:9; width rounded to a multiple of4 | 787968 |
| 320×240 | 560/112/112 | 246/8/23 | 4:3 | 230400 |
| 428×240 | 452/112/112 | 246/8/23 | 16:9; width rounded to a multiple of4 | 308160 |

684×384 is0.1953% wider than exact16:9;428×240 is0.3125% wider. These are
standalone pattern candidates, not new VDU mode allocations or supported product
modes. The first512×384 physical trial failed. Author clarification now selects
the prepared684×384 standalone pattern next, before any full-firmware integration
or240-line test. Its pattern covers the carrier for sync/edge/aspect inspection;
it is not yet the centered game renderer. Do not infer picture acceptance from
DMA progress. Keep the unchanged LT8912B driver for this comparison.

The [Lontium LT8912B brief, revision1.5](https://www.lontiumsemi.com/uploadfile/202410/4b78333c11fcc16.pdf)
confirms continuous-clock input and80Mbps–1.5Gbps per lane. Its25–154MHz statement
specifically describes LVDS output and is not evidence of an HDMI minimum clock.
The brief also states no DDC support; this experiment does not claim to read the
monitor's EDID through the bridge. Retaining the working clock avoids guessing
at a low-clock limit, but does not establish monitor support for unusual active
sizes or long blanking. Actual visible picture review remains necessary.

### M01 full-firmware preparation while picture review is pending

Continue compile/host preparation within the authorized native-mode and live
scanout work; leave the installed standalone pattern untouched. The experimental
full P4 build may explicitly select the same 512×384 timing, twelve 32-row
blocks and three SRAM slots, retaining the existing 848×480/default output
paths. Preserve the 1600µs refill abort because line cadence is unchanged.
Validate C DMA and C++ renderer geometry agreement, stock sprite pixels, clipping
and build inputs. No new logical mode ID, scaling, upstream queue fix or reduced
queue capacity. Only after Author picture acceptance may this candidate replace
the pattern and attempt normal services, mode changes and the small sprite
fixtures; hardware Nurples remains conditional on those gates.

**Superseded deployment target,2026-10-07:** the512-wide full image above remains
unflashed preparation. The Author rejects512-wide HDMI as the desired output;
successful684-wide timing would require a matching full build and renewed SRAM
and service checks. Three32-row RGB888 slots at684-wide need196992 bytes, not
the147456-byte512-wide allocation. Do not deploy the old full candidate or claim
its memory-saving figure for the widescreen output.

### Accepted presentation decision —2026-10-07

HDMI02-D01 [x] The P4 output adapter centers the unchanged512×384 game canvas in
a widescreen HDMI active area and supplies black sidebars. The monitor receives
the wide signal; the P4 does not stretch the game.684×384 is the first384-line
candidate,0.1953% wider than exact16:9, pending physical qualification. This
amends [ADR-0024](../decisions/ADR-0024-centered-unscaled-hdmi.md); it does not
allocate a logical VDU mode or qualify this candidate.

### M02 loaded failure and bounded diagnostic repeat

The full684 candidate passes host/build validation and both small sprite cases,
but hardware Nurples fails around the warm-up/measurement boundary: Author reports blue then black output
a few seconds after the first enemy fireball. P4 restarts and loses its in-memory
window records. Agon retains an aborted header with zero measured rows and a
saturated final fence timer. This is not a performance pass. The initial serial
capture began too late to retain the panic; full-image rollback also replaces
the core-dump partition, so that original dump is unavailable.

Restore exact startup/configuration through the known working848 image first.
Then perform one deliberate repeat of the same fixture/candidate using a new
result path, with USB logging already active before Agon reset. Preserve any
panic and core dump before another flash, identify the failing source path,
and restore normal operation. This is a bounded failure diagnosis within M02c,
not a new measurement campaign or permission to count recovery runs as passes.

The repeat's retained core dump resolves the crash to processLoop destroying the
shared-pointer control block for a BufferStream in bufferWrite(ID65535). That is
the benchmark marker carrier, not proof of a scanout-ISR or ordinary-game crash.
Under the standing diagnostic-failure protocol, run one otherwise identical
3600-update control with aggregate B009 markers disabled (config extra_flags=0,
window tag0). Preserve eZ80 PRT/result records, but do not invent missing P4 phase
measurements or count it as a complete matched pass. Capture serial through a
parent process that waits for the capture child; preserve any core before flash.
Restore exact originals afterward. This control must precede a speculative
renderer or upstream-library fix.

M02c memory continuation: the ordinary-malloc PSRAM preference completes the
marked3600 run and normal exit, but leaves only3835 internal bytes. The fixed-mode
fixture does not exercise the ordinary game's loaded8→20 transition. The next
bounded remedy keeps the1024-entry primitive queue unchanged while moving its
18432-byte payload to PSRAM and retaining its RTOS control in internal RAM.
P4 drawing consumes this queue in task context; classic VGA ISR consumption is
excluded from this composition. Retain every original queue operation and paired
allocation/free ownership. Repeat the same game and verify ordinary interactive
entry/mode changes/exit before offering the installed image for play review.


Runtime implementation evidence: the first848→684 test exposed internal SRAM
fragmentation (131735bytes free, largest59392, required65664 for the third slot).
The revised automatic build reserves all three684 rolling slots before network
and task initialization and retains them across carrier changes. DMA and
framebuffer ownership still stop/join/restart; reservation is not live DMA reuse.
A palette-access guard at the owned mode seam lets the stock fallback run after
a destructive carrier failure instead of dereferencing the retired controller.
The hardware failure is retained; no SD contents changed in that first attempt.

The Author mentions64-color sprites over a lower-color background as a possible
future feature. Keep current upstream behavior: `VGAPalettedController::
rawDrawSpriteScanline` writes a sprite's6-bitRGB directly into the decorated
scanline, after background palette expansion. Source therefore suggests hardware
sprites may already provide that distinction. This is a research observation,
not a newly implemented feature or a complete physical color qualification.
Software sprites still paint into the background representation.
