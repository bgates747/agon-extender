# Plain low-depth graphics controls

## Executive summary

Author selected this bounded qualification on 2026-09-20. Compare existing PAL4
(mode10) and PAL2 (mode11) fixtures on physical mainboard VDP and P4 EDP, with
no Copper execution, product-code changes or new fixtures. Reuse the verified
all-depth mainboard capture diagnostic and retained player/scene identities.

**QUAL-004-LD01** [ ] Preserve actual mainboard flash and incoming startup;
verify fixture hashes against frozen SCENES.json and retain literal palette
oracles. Keep P4/EMOS unchanged. Freeze this contract before bench mutation.

**QUAL-004-LD02** [ ] Install/independently verify existing mainboard diagnostic.
Select each mode on both endpoints only through temporary autoexec. Take two
fresh-reset mainboard captures and two distinct matching P4 generations for
each case. Plain VDU19 palette remapping is included; custom Copper palette
objects and Copper commands are excluded. Stop and restore on unexpected
reset or incomplete acquisition; do not repair firmware to obtain a pass.

**QUAL-004-LD03** [ ] Compare every pixel with zero tolerance, and compare each
device independently with the retained literal tile oracle. Verify 320×240
geometry. Retain failures as well as passes. Record acquisition duration, not
mislabel it rendering time or FPS.

**QUAL-004-LD04** [ ] Restore exact startup and overwritten mainboard flash
sectors, independently verify, close serial/video observers, release keyboard
and SD service, confirm the MOS prompt. Publish results and update coverage.
Four remaining Copper controls and previously reported defects remain deferred.

References: [existing scene generator](../prepare_modes.py),
[frozen inputs](../fixtures/SCENES.json), [oracle checker](../check_oracles.py),
[previous acquisition/restoration](../page-controls/RESULTS.md).
Existing firmware/fixture identities are unchanged; new run IDs use QUAL-004
plus UTC start time. No emulator/voice alert or push requested.
