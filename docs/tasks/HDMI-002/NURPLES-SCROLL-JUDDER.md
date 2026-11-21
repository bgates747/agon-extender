# HDMI02-SIZE01e — Nurples scrolling judder on the Olimex P4

**Draft for Smith’s review.** Determine where the uneven vertical motion first appears during Nurples playfield scrolling. Smith saw it on the full-frame HDMI candidate while gameplay otherwise appeared to run at normal speed. The cause is open. Investigation, instrumentation and another bench reservation await Smith’s review.

## What was observed

Smith described vertical judder that appeared to span multiple scanlines. Different parts of the playfield seemed to move unevenly. He saw no alternating blank and drawn scanlines. He raised scanout errors as a possibility. The trial provided a visual observation only. There is no game-time frame trace, video recording or matched release playthrough in this record. The earlier static pattern verdict and scanout samples belong to a separate run. [Bench observations](SIZE01-BENCH.md)

The Olimex ran Nurples from `/mystuff/nurples`, using the four-file physical runtime bundle from Nurples dev commit `7acfbfa3f27c0100afbedc9d40d75a98a4d1e846`. The executable SHA-256 was `b596aec8592dfc295bd379d6812cfeca96e725b59bd6676c77afaf96460c8ff9`. The P4 ran `hdmi-coverage-r01-b2026-11-21-16-58-59Z`. Its build uses full-frame DMA. Capture the game's actual mode, buffering and HDMI carrier during reproduction. [P4 build and release identities](SIZE01-RESULT.json)

## Proposed investigation after approval

1. The Extender owner and Smith identify a repeatable level segment, camera direction and input sequence with a visible landmark at several screen heights. Record a stationary interval and a scrolling interval. Use the same Nurples bytes, EMOS route, input, cable, monitor and monitor settings on both P4 builds.
2. In a separately authorized Olimex slot, the operator compares released v0.3.0 with the exact candidate and records mode, carrier and buffering for each. Smith reports whether motion is uneven across **part** of the playfield or moves the whole image together, and whether any rows go blank. If filming is available, retain several successive frames with the full playfield in view and compare landmark displacement near the top, middle and bottom. Check any bands against the direct visual observation because camera readout can introduce bands of its own.
3. The operator correlates affected intervals with available P4 frame-completion, submission and error reports. A mean near 60 Hz cannot resolve differences between rows within one frame. If these observations leave the source ambiguous, the Extender owner proposes the smallest follow-up measurement that can distinguish game scroll updates, P4 composition into the framebuffer, buffer publication and HDMI scanout. Any Nurples instrumentation belongs to its game owner. Smith reviews that proposal before a diagnostic build or further run.
4. Return a side-by-side result with the scene, reproduction frequency, affected rows, and the earliest stage supported by evidence. If the symptom cannot be reproduced or localized, record that outcome and the missing discriminator. Keep a proposed fix and any production decision separate from this investigation.
