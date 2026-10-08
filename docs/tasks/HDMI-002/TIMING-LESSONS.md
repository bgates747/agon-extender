# HDMI timing lessons — 640×480 failures and native 512×384

## Executive summary

The earlier 640×480 attempts did **not all fail for a demonstrated common
reason**. The APLL attempt, r10, probably selected a DPI clock source that this
P4 silicon cannot use; it produced no frame-DMA completions. The later PLL
attempts, r11–r13, did scan frames but never produced an acceptable monitor
picture. Their remaining bridge/timing/monitor failure is unresolved.

The successful 848×480 experiment supplies a better starting point: a supported
PLL clock, deliberately matched P4/DSI/bridge timing, a simple static framebuffer
and an unchanged bridge driver. It proves that 480 active lines can work here;
it does not retrospectively identify why the 640-pixel-wide trials failed.

For a future **native 512×384 HDMI signal**, derive the timing from clocks this
silicon can actually generate, check bridge/monitor limits, and repeat the static
visual gate before adding the renderer. The present 512×384 rectangle inside an
848×480 signal is not native 512×384 output.

## Evidence map

1. [Original 640×480 comparison](../P4PC-001/SCANOUT-COMPARISON.md) retains
   r10–r13 observations, configurations and software measurements.
2. [HDMI-002 contract/results](../HDMI-002.md) identifies the successful static
   image, exact factory hash, deployment checks and Author visual confirmation.
3. [Standalone source](../../../vdp/hdmi-timing-test/README.md) contains the
   reproducible build and pattern. Frozen machine-local images/captures remain
   under `agents/hdmi002/`; older captures remain under the P4-PC experiment.
4. ESP-IDF 5.5.5 commit `b774170ff46c393eeb5e495ea37936038d3f4f4f` is the exact
   SDK used. Relevant source is `components/hal/mipi_dsi_hal.c`,
   `components/hal/esp32p4/include/hal/mipi_dsi_ll.h`,
   `components/esp_lcd/dsi/esp_lcd_panel_dpi.c` and
   `components/esp_hw_support/port/esp32p4/rtc_clk.c` in that pinned checkout.
5. The [vendored LT8912B component](../../../vdp/components/esp_lcd_lt8912b/UPSTREAM.json)
   pins Olimex commit `04032d68e5c727870f9d40beb9e37b7ab3a66916` and file hashes.
   Its bridge source is unchanged in the successful experiment.

## Separate the failures

| Trial | Clock and signal | What actually happened | Supported conclusion |
|---|---|---|---|
| 640 r10 | Requested APLL 25.2 MHz; total 800×525; two 720 Mbps lanes | Startup display locks timed out; finite 5.019917 s window had zero renders and zero DMA completions; USB uptime advanced | Display scanout failed to progress. The APLL DPI mux is now a strong causal suspect; not a renderer throughput result or demonstrated reset loop. |
| 640 r11 | PLL240/9≈26.667 MHz; total 847×525; two 720 Mbps lanes | Approximately 60 DMA completions/s; unusable picture, including a fresh static boot | P4 frame progression worked. HDMI acceptance did not. Nonstandard timing/bridge handling remained unresolved. |
| 640 r12 | PLL240/8=30 MHz; total 952×525; two 360 Mbps lanes; H 168/96/48, V 10/2/33; negative sync; 4:3 metadata | Approximately 60 completions/s; fresh paused bars still failed visual review | Integer lane/pixel timing and matched configured totals were **insufficient**. No evidence that LVGL load alone caused the missing picture. |
| 640 r13 | r12 timing plus receiver settle 0x04 and receiver/DDS relock after P4 scanout started | Fresh static bars still failed | These two bridge changes did not repair that configuration. Neither became a proven fix. |
| 848 r02 | PLL240/7≈34.286 MHz; total 1104×517; two 480 Mbps lanes; H 32/112/112, V 6/8/23; positive sync; VIC 0 | Approximately 60 completions/s, HDMI hot-plug detected, Author reports “that is a beautiful sight” | This complete configuration produces visible output on the connected monitor. It is custom timing near 60 Hz, not exact DMT 0Eh. |

H/V triplets above are front porch / sync width / back porch. DMA completions,
LVGL rendering and actual visible output are separate measurements.

### Why r10 probably stalled

The SDK accepts `MIPI_DSI_DPI_CLK_SRC_APLL`, and its APLL setup can report a
plausible calculated frequency without proving that APLL reaches the DPI block.
The old trial's 25,200,020 Hz report therefore did not establish a running pixel
clock. Source inspection found no missing acquire/set step: the SDK powers and
gates APLL, programs coefficients and waits for calibration.

Espressif introduced DPI selector 3/APLL in
[commit be2b6efa](https://github.com/espressif/esp-idf/commit/be2b6efadc559596c22071ffec90423ea962c6e1),
whose subject/body concerns changes for silicon 3.0. The DPI APLL case is not
guarded like the revised PHY clock path. The
[official TRM](https://documentation.espressif.com/esp32-p4_technical_reference_manual_en.html),
pre-release v0.7 dated 2026-08-20, page 1128/register 11.16, lists DPI clock
selector 3 as invalid; it lists XTAL, PLL240 and PLL160 for the other selectors.
The newer DSI diagram in the same preliminary manual includes APLL, so the
manual itself mixes revision coverage. Its SHA256 is recorded in the main task.

Together with r10's zero-DMA behavior on actual silicon 1.3, this is strong evidence
of an unsupported old-silicon mux selection. It is **not** an isolated reproduced
vendor-confirmed defect, and cannot explain r11–r13, which already used PLL.
The 848 experiment avoided the questionable source rather than retrying it.

### Why r11–r13 remain unresolved

Changing a framebuffer size does not define an HDMI mode. The P4's pixel
clock/blanking, DSI packet timing, LT8912B reconstruction and monitor expectations
all have to agree. These trials used custom signals, and later trials changed
several variables together. No single-variable comparison isolated the remaining
fault. Specific facts and unresolved possibilities are:

1. **Clock rounding is a real SDK behavior.** The DPI divider is integer. The
   HAL rounds the source/request ratio, then adjusts the P4 producer's horizontal
   front porch when realized and requested clocks differ. Its DSI host timing
   calculation uses the requested clock separately. Programming the external
   bridge from the original requested totals can therefore produce disagreement.
   This behavior matters to every new modeline; it is not proof that every old
   failed trial had this mismatch. r12 already used an exact integer clock.
2. **Clock alignment alone was not sufficient.** r12 had integer horizontal
   byte-clock timings and still failed. Its two 360 Mbps lanes equal the raw
   RGB888 demand at 30 MHz; the successful trial's two 480 Mbps lanes exceed its
   approximately 411.429 Mbps-per-lane active-pixel demand. That difference may
   matter to DSI packet/blanking/FIFO behavior, but no controlled test proves
   a lane-headroom cause. Do not turn a payload-rate equality into a complete
   DSI link budget: packet overhead and burst scheduling still matter.
3. **Custom timing and HDMI metadata were not equivalent.** The old 640 path
   used VIC 1 with custom clock/blanking, whereas the successful 848 path uses
   VIC 0. Monitor interpretation is a possible contributor; no metadata-only
   comparison was performed. A custom signal must not be advertised as a CTA
   mode merely because active width/height match.
4. **480 active lines are not categorically unsupported.** The working848
   signal also has 480 active lines. It uses the original settle 0x10 and original
   reset order. The earlier settle 0x04/post-start-relock changes are neither
   demonstrated requirements for 480 lines nor a proven repair for 640×480.
5. **The bridge's integer `pclk_mhz` was a misleading lead.** In this pinned
   driver it is consulted only by the disabled internal-pattern path. Ordinary
   output reconstructs timing from incoming DSI. Rounding that field alone did
   not establish a normal-output fault or a fix.
6. **Rendering speed was a different issue.** The earlier LVGL circle workload
   drew in roughly 22–25 ms, too slow for a new rendered frame every 16.67 ms.
   That explains its sub-60 animation throughput, not the unusable static picture.
   Removing LVGL now narrows the test; it does not prove LVGL caused the old
   bridge failure. Older direct/static controls had already failed too.

## Lessons for native 512×384

These are constraints for the next scoped experiment, not authorization to run it.

1. **Define the actual output.** A 512×384 active HDMI signal is different from
   a 512×384 image inside 848×480 or 1280×720. In a true 512×384 signal, the monitor
   must accept the timing and provide any desired pillarboxing/aspect treatment.
   Adding transmitted black columns changes the active signal size again.
2. **Start from supported clocks.** On this specimen use the verified legacy
   clock muxes and realizable integer divisors. Do not reuse APLL solely because
   a current SDK enum exposes it. Derive horizontal/vertical totals from the
   actual clock and desired approximately 60 Hz cadence; then calculate the
   resulting horizontal frequency and blanking durations explicitly.
3. **Check electrical/timing limits before selecting that clock.** Establish
   LT8912B input/output clock ranges, DSI lane constraints and monitor EDID/range
   limits. A smaller active image need not imply a proportionally smaller pixel
   clock: extra blanking may be needed. Present success at 848×480 does not prove
   that the monitor will accept 512×384, nor that a low pixel clock is supported.
4. **Keep all timing owners consistent.** Supply the same active dimensions,
   totals, porch widths and polarity to P4 DPI and LT8912B. Calculate the DSI
   host's byte-clock values using the realized lane rate. Prefer exact integer
   relationships, explicitly account for payload/packet headroom, and record
   any unavoidable HAL compensation. Check driver realizability rather than
   assuming requested lane rates are generated exactly.
5. **Use truthful HDMI metadata.** A custom 512×384 mode has no established
   standard VIC in this experiment. Use custom-mode signaling unless an actual
   standard mapping is verified; choose 4:3 treatment deliberately. An aspect
   hint is not a guarantee that a monitor will preserve shape or avoid overscan.
6. **Use the same minimal proof first.** Keep the proven bridge driver, board
   initialization, channel order and static pattern methodology. Change only
   the timing/geometry required for 512×384. Start with one framebuffer, paint
   before scanout, flush its cache, then leave it unchanged for a physical review.
   A 512-pixel RGB888 row is 1536 bytes and a 384-line frame is 589,824 bytes, both
   suitably aligned to the 64-byte boundary used in these tests.
7. **Verify the right things independently.** Check both bootloader/application
   silicon ranges before flash; read back exact bytes; log selected clock/divider,
   DMA progression and bridge detection. Judge visible edges, colors, one-pixel
   detail, shape/aspect and stability on the actual monitor. None of the software
   counters by itself closes the visual gate. Keep exact 848 and Nurples rollback.
8. **Measure product benefit later.** At equal 60 frames/s, reading a 512×384
   RGB888 framebuffer once per frame is 35.39 MB/s versus 73.27 MB/s for 848×480,
   approximately 51.7% fewer active framebuffer bytes. These are arithmetic
   payload estimates, excluding blanking/protocol traffic, rendering, cache and
   buffer copies; they are not measured contention relief or a gameplay result.
   A static timing pass must precede renderer integration, scrolling/sprites,
   double-buffer ownership and user-input regression tests.

## Stop state

Only the 848×480 static trial has been deployed in this task. The Author's request
for these notes does not authorize a native 512×384 flash or another 640×480 trial.
The existing pattern remains unchanged on the monitor.


Subsequent authorization: the Author later requested native512×384, wide, and
320×240 experiments after sprite integration. See HDMI-002 M01–M03 for current
authorization and selected tuples; the stop state above records the earlier
static-trial handback, not the current bench installation.
