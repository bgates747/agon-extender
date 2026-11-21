# Matched Olimex screen coverage comparison

Smith reviews this packet before scheduling. The two arms change only the P4 application. Smith operates the same preview on the same HDMI monitor with the same cable, input, aspect/zoom/overscan setting and viewing position. Pi5 stages identical preview and pattern bytes through the production PARLIO listener. Production EMOS and the mainboard VDP remain installed.

## Preparation and invocation

Use the commissioned runner revision, local job SHA-256 values, config pin, exact phase commands and evidence roots in the operator binding alongside the two generated job manifests. A and B have fresh, separate SD directories under /test. Each uses schema 3 human preload. The launcher reads the four existing packed mode-preview-r02 files by relative name because the standard preview executable hardcodes /extender paths. It consumes each file's initial VDU 22 as a conditional mode change through EMOS, confirms the active mode and allows at least one second to settle after an actual switch. It sends the remaining original bytes through MOS without changing the label, raster, palette, compression or drawing commands.

1. After approval and ordinary checkout, establish a visible, working Legacy mode-0 CLI. Record the monitor settings once, ensure that the Extender's entry mode is 0 and retain the prior working directory. Use the bench procedure's stop rule for unexpected entry or loss of input.
2. **A, released v0.3.0.** Stage and preload the baseline job. Smith types `RUN &040000` at the verified job prompt. The operator observes the P4's read-only /display/status and captures the passive P4 serial log with the admitted no-reset method. Confirm the released raw application hash against the installed inventory and capture the P4 build identity where available. Use the Extender build ID and raw app hash for image identity. The generic ESP-IDF app-version label reflects the build directory. Record callback progress or the available scanout report, any panel errors or underrun, and the CLI/input result. Do not count the static status dimensions as a frame-progress observation.
3. Smith selects **0, 8, 20 and 3** in that order. Type the mode number and Enter at the menu. After the artwork has completely appeared and the monitor has settled for at least one second, capture the entire monitor frame straight on. Note the pattern label; top, bottom, left and right edges; black margins; and horizontal and vertical diameter of the same circle (or side lengths of the same marked square). Keep the camera location and zoom fixed. Press **Escape** to return to the mode-0 menu between patterns. Explicitly record mode and carrier before mode 20, during mode 20 and after Escape. Confirm that the mode-0 menu redraws and accepts mode 3.
4. Escape from the final preview and again from the menu. The operator verifies a visible responsive Legacy prompt, restores the entry directory and completes A handback. Preserve the original symptom and its evidence even if the monitor scales the two signals differently from the expected HDMI margins. A monitor setting change invalidates the matched comparison.
5. **B, candidate.** Follow the second manifest through stage, P4 app-only install, independent complete write verification and preload. Smith repeats the same RUN, mode order, measurements, photos and exit. Use identical capture settings. The operator then restores the pinned v0.3.0 P4 bytes over the same extent, verifies readback, CLI, idle services and process cleanup before check-in. Neither preload nor reset starts either preview. Follow the [Olimex stop rule](../../operations/olimex-bench/README.md) on an unexpected fault and retain the first failure.

| Case | Release P4 carrier and image | Candidate P4 carrier and image | Monitor observation on B |
|---|---|---|---|
| 8 | 1280×720 / 320×240 | 848×480 / 640×480 | Full height, both sidebars, round circle at 2× |
| 20 | 1280×720 / 512×384 | 684×384 / 512×384 | Full height, complete top and bottom, equal sidebars |
| 0 | 1280×720 / 640×480 | 848×480 / 640×480 | Full height, all four edges, legible label |
| 3 | 1280×720 / 640×480 | 848×480 / 640×480 | Full height, correct proportions with doubled rows |
| 0→20→0 | 720-line carrier throughout | 848×480 → 684×384 → 848×480 | Both relocks, responsive redrawn menu and advancing output |

For each arm and mode, retain one photo showing the bezel, the raw status response, circle diameters in the same photo units and the matching serial timestamps. Hold each picture through a fresh positive scanout report where available. The P4 computes Hz over at least ten seconds when updates occur. A missing sample leaves frame progress inconclusive. Close the passive serial monitor before programming or handback.

The P4 status must report logical mode and dimensions as well as the expected output dimensions. The expected left/right margins in the candidate signal are 104/104 pixels for 0, 8 and 3 and 86/86 for 20. All four should have zero black rows above and below the artwork. Judge physical geometry using the pattern and the monitor frame; monitor pixels need not correspond one for one to HDMI pixels. Record raw measurements and Smith's verdict for each mode. A clipped edge, distorted shape, underrun, stopped frame progression, failed mode selection or unresponsive return is a failed observation. The full-frame builds have no rolling refill counter. Record unavailable telemetry as such. Gameplay throughput and other modes are outside this comparison.


## Review and operator records

The [offline receipt](SIZE01-RESULT.json) pins both jobs, the matched launcher and all four patterns. The packet-local operator binding gives the commissioned checkout and phase commands. After Smith releases this review gate, the operator follows the commissioned readiness and reservation procedure. Each job's preload leaves the CLI waiting for Smith. Keep one observation row per mode and an additional row for the round trip in each arm.

| Arm and mode | Logical mode and carrier from P4 | Photo and status file | Top / bottom / left / right margins | Circle width / height | Scanout Hz and serial interval | Lock, return and Smith's verdict |
|---|---|---|---|---|---|---|
| A or B, 0 / 8 / 20 / 3 / round trip | | | | | | |

The candidate and restore writes both start at app0 offset `0x20000` and cover 1,794,048 bytes. The restore writes the released application followed by erased padding through the end of that extent. Retain independent readbacks for both writes. Use the job’s pinned component identities and verify the baseline inventory at entry before running A. If a different build is present, stop the comparison for review.
