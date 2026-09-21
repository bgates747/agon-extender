# Mainboard sprite/scroll follow-up

## Executive summary

All three mainboard-only checkpoints completed twice with pixel-identical
captures and successful Escape/CLI recovery. The final hidden-sprite background
matched its independent reference at every pixel. No crash or incomplete capture
occurred in this batch, so no failure-triggered stock replay was required.
P4 scenes remain unexecuted; this does not add paired qualification coverage.

| Check | Mainboard capture result | Additional evidence |
|---|---|---|
| OVERLAP: movement/frame changes ending in overlap | Two identical complete images | Red/cyan transparent patterns visible in expected overlapping region; visually reviewed captured image |
| EDGES: opposite screen-edge clipping | Two identical complete images | Red sprite clipped at left, cyan at bottom-right; visually reviewed captured image |
| HIDDEN: hide both sprites after scrolling/refill | Two identical complete images | Independent full-background oracle: zero mismatches out of196608pixels |

## Scope and reproducibility

The existing sprite-scroll-probe-r01 bytes/player were read back from SD before
execution. Mainboard-image-capture-r02 was installed and independently verified,
with actual incoming stock flash retained. Mainboard mode20 was selected only
through startup. Each capture had fresh reset/startup isolation, including all
prior updates encoded in that checkpoint. Successful attempts exited with Escape
and demonstrated CLI response by starting/exiting the SD service.

[Results](evidence/results.json), [duration](evidence/duration.json),
[input hashes](evidence/staged.json) and [deployment](evidence/deploy.json).
Six checksummed serial images and decoded pixel payloads are retained in evidence;
PNG previews accompany them. Host duration includes reset, commands, serial image
transfer and recovery, and is not a rendering-performance measurement.

OVERLAP/EDGES are repeatability and visual capture checks, not independent
whole-image oracle proofs. HIDDEN has the complete independent oracle. These are
static checkpoints after successive updates, not proof of tear-free animation.
The earlier INITIAL diagnostic panic remains unresolved: this successful batch
neither erases it nor proves diagnostic instrumentation innocent. Its stock
control and Author visual pass remain separately recorded.

## Restoration

Stock mainboard application and incoming load-only visual-review startup are
restored and verified in the final receipt. P4/EMOS unchanged; no Extender scene
executed. Mainboard remains ready for the Author; no automatic fixture RUN.
