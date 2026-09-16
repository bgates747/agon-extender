# QUAL-004 graphics correctness results — in progress

## Executive summary

The first four scenes (calibration, empty/reset, viewport/clear, and bitmap/graphics
text) match across all196608 pixels per scene on physical mainboard and P4.
The alpha/cutout scene is **not yet a valid parity comparison**: two mainboard
replays differed at11600 pixels in one reused checkerboard bitmap. Both captures
passed their row-integrity checks. A test-only resource-barrier variant is being
prepared; no VDP rendering implementation is changed.

| Scene | Mainboard repeat | Mainboard versus P4 | Differing pixels |
|---|---|---|---:|
| BSP03_01, original unfenced | Failed stability | Not run |11600 between mainboard replays|
| CAL | Exact | Exact |0|
| EMPTY | Exact | Exact |0|
| SHP20 | Exact | Exact |0|
| SHP23 | Exact | Exact |0|

The calibration cohort took88.374 seconds including loading, two serial dumps,
keyboard orchestration and P4 snapshots. This is procedure duration, not a GPU
rendering time or frame rate. Native rendered-operation timing is not inferred.

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
