# QUAL-004 graphics correctness results — in progress

## Executive summary

Twenty-four distinct mode20 scenes now have valid mainboard/P4 comparisons,
with zero differing pixels across each complete512×384 image. Three mainboard
attempts have also crashed in stock sprite scanout, outside the capture command;
they remain invalid attempts even where a fresh retry later passes. The original
unfenced alpha replay was unstable; an explicitly fenced control matched.

The remaining cases and lower-depth/page controls are still running. This is
not yet a blanket API-parity conclusion. Missing functionality is recorded in
[COVERAGE.md](COVERAGE.md) and will not be implemented in this pass. Exact
artifact identities are in [ARTIFACTS.json](ARTIFACTS.json).

The table below is the early control history; the retained cohort tables contain
subsequent full-image comparisons.

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
