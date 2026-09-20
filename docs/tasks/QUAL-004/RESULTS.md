# QUAL-004 graphics correctness results — first pass

## Executive summary

**2026-09-20 follow-ups:** [two displayed-page controls](page-controls/RESULTS.md)
and [two plain low-depth controls](low-depth/RESULTS.md) also passed. Cumulative
retained coverage is now **70 scenes / 12,923,904 pixels**; four prepared Copper
controls remain. The first-pass results and firmware identities below are
preserved as originally measured.

**66 distinct static scenes matched pixel for pixel on physical mainboard VDP
and P4: 12,616,704 compared pixels, zero differences.** This establishes parity
for the captured scenes, not every graphics API, mode, animation or transition.
Mainboard repeat captures and two fresh P4 snapshots agreed for each valid pair.
Six independent literal-oracle checks (three scenes on both devices) and ten
ordinary MOS pixel-query replies also passed.

| Scope | Mainboard | P4 | Complete-image differences |
|---|---:|---:|---:|
| Mode20, 512×384×64 |63 valid scenes|63 valid scenes|0 /12,386,304 pixels|
| Mode9, 320×240×16 |3 valid scenes|3 valid scenes|0 /230,400 pixels|
| Remaining prepared mode controls |Not qualified|Not qualified|8 scenes deferred|

**Reliability findings remain open:** three mainboard diagnostic-build attempts
crashed in stock sprite scanout; two P4 restarts occurred during subsequent mode
setup after Copper scenes. Fresh retries passed the affected mainboard static
scenes. P4's second restart ended additional coverage as required by the contract.
These failures are retained, not converted into passes by successful retries.
The initial unfenced alpha scene also differed between mainboard repeats;
explicit completion barriers before resource clears produced stable matching images.
No renderer or missing API functionality was implemented or repaired.

The next investigation should capture the P4 restart cause during the Copper/mode
transition, then reproduce the mainboard sprite failure without the capture tap.
These are **second-pass candidates, not started or automatically approved**.
Remaining low-depth/page controls and uncovered API families follow those checks.

This pass measured acquisition procedure durations, **not isolated rendering
milliseconds or realised FPS**. Resets, loading, serial extraction and host control
are included; those durations cannot support a mainboard/P4 speed claim. The
initial calibration procedure took88.374 seconds. Each cohort table retains
individual procedure seconds for future acquisition estimates.

Evidence tables: [first fenced cohort](evidence/fenced-first/TABLES.md),
[isolated cohort](evidence/isolated-first/TABLES.md),
[isolated retry](evidence/isolated-retry/TABLES.md),
[remaining mode20 corpus](evidence/bounded-corpus/TABLES.md), and
[mode9 controls](evidence/mode-controls/TABLES.md). Duplicate calibration/alpha
controls are excluded from the66-scene count. Exact identities and prepared inputs
are in [ARTIFACTS.json](ARTIFACTS.json) and [fixtures](fixtures/README.md).
Known missing functionality and untested coverage are separated in
[COVERAGE.md](COVERAGE.md).

## Unfenced alpha finding

[First mainboard replay](evidence/unfenced-alpha/mainboard-repeat-0.png),
[second replay](evidence/unfenced-alpha/mainboard-repeat-1.png), and
[difference](evidence/unfenced-alpha/repeat-difference.png) show one checkerboard
background missing in the first replay. Bounds are x200..327/y112..207.
The checker bitmap uses a repeatedly cleared/reloaded temporary buffer. A resource
lifetime/ordering issue is a hypothesis; the initial observation does not prove
a P4 defect, a shared defect, or a capture-method defect. Raw serial evidence is
retained beside the images. The test-only next variant places stock completion
commands before top-level buffer clears, with opaque pixel payloads untouched.

## Resource-barrier control

BSP03_01 with stock completion commands before buffer clears now has identical
mainboard repeats and zero differing P4 pixels. Its image hash is
`d632b08298934359a5dd793d1e8ce1e73b25921b7f5ad4c43b0582b00f60665e`, matching
the complete checkerboard from the original second replay. This supports a
mutable-resource ordering explanation; it does not establish which upstream
contract, if any, the unfenced case violates. No renderer code was repaired.
Proceed with the explicitly serialised63-scene correctness cohort; preserve the
unfenced result rather than silently relabelling it a pass.

## Mainboard sprite-replay acquisition failure

The fenced cohort passed CAL, EMPTY, SHP20, SHP23, BSP03_01 and BSP07_01–03
before stopping at BSP21_01. Its first mainboard capture completed; the second
replay crashed mainboard VDP before any capture-begin marker for token2017.
The ESP32 exception was `LoadProhibited`, address0x1c. The exact diagnostic ELF
maps PC0x40083247 to stock `VGAPalettedController::drawSpriteScanLine`, line490,
where the loop dereferences `sprite->hardware`; `getSprite(i)` appears null.
The backtrace itself is marked corrupted, so deeper call-stack claims are withheld.

Stock `setSprites` sets count0 before replacing its pointer, but a scanout loop
may already have entered an iteration. This is a source-supported lifetime/race
hypothesis, not a proven root cause. Capture instrumentation may affect timing.
The crash occurred outside the capture command, and before the added row tap in
that ISR path. No stock or port implementation is changed.

Self-assigned isolation control: rerun the remaining cohort with a normal
mainboard reset into the verified test startup before each mainboard replay.
This avoids resetting a live sprite collection from the preceding replay.
Record it as a distinct cohort; it cannot qualify live sprite teardown, and a
repeat failure must remain a failure. Preserve the original crash evidence.

The first restart-isolated BSP21_01 comparison passed: mainboard repeats were
identical and all196608 pixels matched P4. This is evidence for static sprite
composition under fresh setup, not clearance of the live-replay crash. The
remaining55-scene cohort is proceeding with actual SD-startup readiness checked
after each reset rather than a fixed boot-delay assumption.

## Unexpected mode during acquisition

The isolated cohort passed14 further scenes through BSP25_03. BSP25_04 then
reported640×480 rather than the startup's expected512×384; its capture ended
unsuccessfully without a row. The r01 tap covers64-colour scanout only, so this
is invalid acquisition, not a valid pixel mismatch. The frozen input contains
no top-level mode command. Startup bytes had been verified, but that does not
prove the display reached its requested mode. Cause remains unresolved; one
fresh-start retry of the case is permitted before proceeding with the remainder.
No mode-selection command is added to the fixture and no renderer is repaired.

Correction after examining serial bytes **before** Q4BEGIN4028: the VDP did not
merely remain in the wrong startup mode. It crashed/rebooted during scene
execution at the same stock sprite-scanout PC0x40083247/address0x1c, then consumed
the trailing capture command in default640×480 mode. The dated run correction
and full preceding crash text are retained. Restart isolation therefore reduces
live-replay exposure but does not eliminate this failure. Its timing relationship
to the diagnostic build remains unqualified; no renderer fix is attempted.

## P4 restart between Copper scenes

PAL16 and COP16_SETUP completed with exact full-image parity. During the next
mainboard startup (which re-selects mode9 on P4), HTTP timed out; P4's keyboard
boot identity changed and counters returned to zero. COP16_EDIT had not sent its
scene commands. This proves a P4 restart in that interval, not its root cause.
The prior Copper scene contained active software/hardware sprites and row palettes.
No serial panic trace was acquired, and no P4 firmware change is made.

Retain the failure as an unqualified mode-transition path. The next bounded
static-scene control explicitly resets Copper and sprites after capture before
re-selecting a mode. Such cleanup must not be described as fixing the P4 restart.

## Second Copper transition failure and stop

COP16_EDIT passed after the first recovery: both complete images matched, and
both devices passed its independent literal oracle. The fixture then sent ordinary
Copper reset and sprite cleanup before the next startup. During that startup,
HTTP timed out again and P4's boot identity changed. No COP16_REPLACE image was
acquired. Cleanup therefore did not establish reliable mode-transition behaviour.
No panic trace was collected; the source of the restart remains unresolved.
The remaining eight prepared mode controls were left unqualified, not failed pixel
comparisons. See the retained second-restart observation and mode-control table.

## What the images establish

The temporary mainboard diagnostic samples composed scanout rows after palette
expansion and sprite decoration; row transfer uses USB serial outside rendering.
Canonical pixels are logical RGB222 colours, including hardware-sprite composition.
Static rows are stitched across refreshes, so repeated identical captures are a
required stability check. P4 images are lossless immutable web snapshots from the
unchanged r43 firmware. Every pixel is compared; no cropping, resizing or tolerance.
This is visible-image equality, not identity of internal framebuffer memory layout,
electrical VGA timing, browser presentation cadence or tear-free animation.
Capture instrumentation can change mainboard timing and memory layout; the crashes
are not proven reproducible on uninstrumented stock firmware.

## Independent controls and remaining boundaries

The host decoder's nine negative-control tests reject malformed/corrupt captures
and detect pixel differences. Ten public pixel-query replies validate colour
interpretation on both devices. PAL16, COP16_SETUP and COP16_EDIT pass the retained
literal pixel/halo oracle independently on each device (six checks). The other
16 device-oracle checks have no image because eight scenes were deferred.
No ideal-oracle mismatch was observed in those completed checks.

Known absent mouse-cursor, audio and selected native-display backends remain
untouched. Feature-gated tile/layer APIs, teletext, dynamic Copper, live sprite
mutation, population stress and exhaustive mode/format combinations are not fully
qualified. A prepared fixture is not evidence of a passing implementation.

## Restoration and elapsed time

The exact incoming mainboard app erase sectors were restored from the freshly
verified full-flash backup and independently read back. The original89-byte
`autoexec.txt` was restored and read back through SD service. P4 firmware r43 and
MOS were not changed. Final normal mainboard reset completed; Extender keyboard
was ready and neutral, SD service verification succeeded and exited to Legacy
MOS. Serial capture closed. No notification was sent. The original startup loads
Nurples without running it. Test-only files remain under `/test/qual004`; production
applications were untouched. See [restoration receipt](evidence/restoration.json).

Goal began12:11:20 UTC; hardware restoration verified16:09:31 UTC on2026-09-16
(3h58m11s including preparation, testing and recovery). Reporting finished shortly
afterward, comfortably before the eight-hour ceiling. This is elapsed project
work, not graphics execution time.
