# Sprite/scroll checkpoint attempt — stopped

## Executive summary

The mainboard VDP crashed during the first fixture replay, before any capture
began. **No image comparison or sprite checkpoint passed.** P4 did not execute
any of these scenes. The contract's stop condition was applied; no retry or
renderer repair was attempted. Existing static coverage remains 71 scenes.

This reproduces the signature of [FWBUG-002](../../../firmware-bugs.md#fwbug-002),
the retained mainboard sprite-scanout failure. It does not establish an Extender
defect or prove the diagnostic instrumentation irrelevant.

## Captured evidence

1. [Run status](evidence/result.json): SS_INITIAL, token5400; no Q4BEGIN or image.
2. [Panic trace](evidence/panic.txt) and [exact-ELF decode](evidence/decode.txt).
3. [Retained complete serial stream](evidence/mainboard.serial.gz).
4. [Fixture command bytes and hashes](manifest.json); [generator](prepare.py).
5. [Restoration receipt](evidence/receipt.json) and [hash inventory](evidence/SHA256.json).

`LoadProhibited`, EXCVADDR `0x0000001c`, PC `0x4008332f`, maps to stock
`VGAPalettedController::drawSpriteScanLine`, line490: dereferencing
`sprite->hardware` after `getSprite(i)`. The backtrace is marked corrupted;
no deeper stack narrative is inferred. Diagnostic ELF SHA256 is
`cac2c919b5154ccd9f1ae57353f6d67e54c3e8b964b057280557db3b4d3de938`.
The same function/address signature was retained in the earlier
[mainboard sprite-replay failures](../RESULTS.md#mainboard-sprite-replay-acquisition-failure).

The exact VDU command at the point of failure was not instrumented. SS_INITIAL
sets up two software sprites, but this trace does not prove whether activation,
reset, frame setup or another setup action triggered the fault. A software-only
fixture still traverses the stock scanout sprite list. Count/pointer lifetime
remains a hypothesis, not a confirmed mechanism. No source fix was made.

## Procedure disposition

The frozen contract is `f7b8f0f4`; sprite-scroll-probe-r01/registry r95. All four
fixtures and sidecars were deployed and read back, and the retained player
matched. Mode20 selection occurred only in startup. The mainboard diagnostic
was independently verified before execution. P4 and EMOS firmware were unchanged.
The existing decoder/comparator tests passed (five plus four tests).

SS_OVERLAP, SS_EDGES and SS_HIDDEN were not executed. Independent background
comparison therefore remains unperformed. Acquisition was interrupted on panic;
there is no completed suite duration or rendering-time measurement to report.

The Author may choose a separate bounded investigation to isolate the mainboard
sprite-list failure, including a diagnostic-free control. That follow-up is not
automatically started by this result. Existing bug deferrals remain authoritative.

## Restoration

Recovery used the ordinary Agon reset and prepared SD service. Original startup
was restored/read back, and original mainboard application sectors restored and
independently verified. The final MOS prompt/input and closed serial/SD/video
state are recorded in the receipt. No P4 scene, product firmware change, emulator
notification or push occurred.

## Subsequent official stock control

The Author-authorized [diagnostic-free control](stock-control/RESULTS.md) did not
crash during one30-second observation and returned to CLI service after Escape.
This leaves diagnostic influence/intermittency unresolved; no stock-independent
crash claim or new image qualification is justified.

## Subsequent mainboard-only continuation

[OVERLAP, EDGES and HIDDEN](mainboard-followup/RESULTS.md) each completed two
matching captures, with zero full-background oracle mismatches for HIDDEN.
No new failures. This does not erase the INITIAL failure or add P4 coverage.
