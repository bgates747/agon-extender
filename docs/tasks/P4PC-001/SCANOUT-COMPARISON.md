# 640×480 drawing and scanout comparison

## Executive summary

Native 640×480 r12 measures about 30 ordinary LVGL renders/s. Paired sequential
capacity windows average 31.77 renders/s with P4 scanout active and 34.02 with
DMA/DSI stopped: approximately 7.1% faster without scanout. Drawing still takes
22–25 ms, exceeding the 16.67 ms budget. This supports drawing as the main limit
for this software workload. Both r11 and r12 fail Author visual review, including
fresh paused bars; panel completion counters do not establish usable HDMI.
Preserve working 720p/factory rollback and informative native failures.

## Bounded experiment

1. Native RGB888 640×480; same 24 circles and sizes. r12 uses PLL 240 MHz / 8
   (30 MHz), totals 952×525 (calculated 60.0240 Hz), horizontal 168/96/48
   and vertical 10/2/33 blanking, negative sync polarity and 4:3 metadata.
   DSI uses two 360 Mbps lanes, matching RGB888 pixel demand; integer DSI
   byte-clock horizontal timings avoid rounding mismatches. This custom
   blanking needs physical monitor validation. The failed r10 APLL
   control requested 25.2 MHz with 800×525 totals. The LT8912B
   integer MHz field is used only by its disabled test-pattern routine; normal
   operation locks to incoming DSI. Keep its DDS initialization, SDK, CPU/PSRAM,
   renderer, compiler and two framebuffers fixed within each on/off pair.
2. The copied IDF 5.5.5 DPI component receives a task-local stop/resume hook.
   The P4 DMA completes its current frame, stops rearming, and disables DSI
   video output. It retains both framebuffers. Resume reinitializes the existing
   DMA descriptors/output, without flash/reset or framebuffer reallocation.
   Do not modify the reference IDF checkout or claim blanked HDMI alone removes
   scanout memory traffic. Confirm frame completions stop before the off window.
3. Run the ordinary visible demo as a practical reference. Then run paired
   drawing-capacity windows with presentation/wait bypassed in both: same LVGL
   drawing, buffer synchronization and cache writeback, first with scanout active,
   then with DMA/DSI output stopped. This isolates scanout contention while
   removing its frame-pacing ceiling. Headless renders are not presented FPS.
4. Diagnostic windows use the USB main task as one LVGL owner: one fixed
   1/60 s animation step followed by an explicit refresh, then a one-tick yield
   for idle/watchdog readiness. Hold the LVGL mutex for the finite window;
   its normal port and animation tasks cannot race or insert polling gaps.
   Ordinary animation keeps elapsed-time motion and its admitted scheduling.
   Restore ordinary settings after each window.
   Log actual duration, updates, renders, panel completions, drawing interval,
   cache/flush interval and full refresh interval. Do not label render duration
   including frame waits as pure drawing time.
5. Correct known pause/startup lock readiness before the new test: atomic pause
   flags take effect without waiting behind renderer work; initial bars precede
   animation-task creation. USB errors must remain failures.
6. The Pi builds and audits compiled component paths, preserves/device-verifies
   rollback, flashes/verifies exact bytes and captures boot. The Author observes
   native-resolution motion and resumed output. Retain paired raw measurements
   and informative failures; no production integration/promotion or Agon operation.

## Retained r10 failure

Native build/source audit and exact install verification passed. Explicit boot
reported silicon v1.3, IDF 5.5.5, CPU 360 MHz/PSRAM 200 MHz, configured APLL
25,200,020 Hz and native 640×480. Startup display locks timed out; no playground
objects were admitted. A finite 5.019917 s window reported zero renders and zero
framebuffer completions. USB uptime advanced, so this is a display path failure,
not an established reset loop or rendering-capacity result. The APLL frequency
report is calculated from configuration, not a probed clock. Cause remains
unproven. Normal LT8912B DDS initialization is retained; its integer pclk field
is only consulted by the disabled internal test-pattern branch.

Exact failed bytes, config, copied component and boot/USB captures are retained
in the ignored r10 installed bundle. r11 changes the clock/timing selection and
preserves those bytes rather than relabelling the failure as a performance run.

## r11 software comparison and failed visual gate

The native PLL candidate requests 26.666667 MHz, totals 847×525, two 720 Mbps
lanes and calculated 59.9689 Hz. Exact build/install/rollback verification and
source audit passed. Static control recorded zero rendering and 59.961 panel
completions/s. Thirty seconds of ordinary circles recorded 29.996 renders/s,
59.991 panel completions/s, mean drawing 25.149 ms, cache writeback 0.467 ms,
frame wait 2.932 ms and full refresh 30.814 ms. Boundary submissions differ by one.

Two drawing-only off windows each recorded zero DMA completions; scanout-on
windows recorded approximately 60/s. Drawing intervals remained approximately
24 ms without DMA. However, independent animation/port scheduling inserted
gaps and occasionally merged updates; drawing-only throughput (approximately
21/s on and 23/s off) is not a maximum rendering-capacity result. r12 therefore
uses a sequential owner; r11 remains useful scheduling and stop/resume evidence.

Author reports no usable picture after the comparison and after a fresh USB
reset into paused bars with no stop in that boot. Fresh USB capture shows
advancing uptime and render/scanout counters, not a reset loop. Native HDMI
acceptance fails; timing/bridge compatibility remains unproven. r12 matches
the lane rate to RGB888 demand and uses an integer pixel clock/custom total;
this is an experimental candidate, not an isolated causal diagnosis.

## r12 sequential comparison and failed visual gate

Installed build `r12-b2026-10-04-01-06-06Z`, ELF prefix `330101be5`, retains
IDF 5.5.5, LVGL 9.6.0~1, compiler `-Og`, CPU 360 MHz/PSRAM 200 MHz,
RGB888 and two framebuffers. Matched 30 MHz/two 360 Mbps lanes produce
approximately 60 P4 frame completions/s. Author reports no usable picture
from freshly booted paused bars. The following are software measurements.

Worst throughput first; each capacity row is a finite ~20 s window. DMA-on
capacity deliberately bypasses presentation/wait and can overwrite a scanned
buffer; these are rendering rates, not accepted displayed frames/s.

| Variant | Renders/s | Drawing mean (ms) | Cache mean (ms) | Full refresh mean (ms) | P4 completions/s |
|---|---:|---:|---:|---:|---:|
| Ordinary paced, 30 s | 29.992 | 25.025 | 0.461 | 30.499 | 60.018 |
| Capacity on, repeat | 31.005 | 25.327 | 0.447 | 29.701 | 60.013 |
| Capacity on, first | 32.545 | 23.907 | 0.453 | 28.272 | 60.041 |
| Capacity off, repeat | 33.128 | 23.499 | 0.385 | 27.613 | 0 |
| Capacity off, first | 34.919 | 22.017 | 0.389 | 26.189 | 0 |

Both off windows have zero framebuffer completions. Every capacity window
has equal update/render/measured counts and zero submission/wait time. Aggregate
rate is total frames divided by total elapsed time: 1272/40.031995 s on and
1362/40.030993 s off. Percentage improvement is `(off/on - 1) × 100`.
Repeated order shows variation; do not attribute the entire difference to one
stage or extrapolate a stock Agon comparison. Static control has zero rendering;
scanout restores to approximately 60 completions/s after the off windows.

r13 adds a separate packed-format reference and tests LT8912B low-resolution
settle `0x04` with receiver/DDS relock after live P4 scanout starts. Linux's
[LT8912B driver](https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/bridge/lontium-lt8912b.c)
selects this settle value for vertical active sizes at most 600. This is an
unproven native-output experiment, with two bridge changes; it cannot isolate
which change matters if visual output improves.

## r13 fresh static visual failure confirmed

The Author confirms no usable picture after the deliberate reboot into paused
native 640×480 direct bars, with no subsequent benchmark or display change.
This is a failed physical gate, independent of the earlier ambiguous observation
during live test transitions. The low-resolution settle/live-stream relock
experiment does not restore usable native HDMI on this monitor. Horizontal
input detection and advancing software counters are insufficient acceptance.
Preserve exact r13 bytes and the fresh boot capture. The board remains on paused
bars; the render-only packed-format results remain valid within their scope.

## Later clock review and working480-line control —2026-10-07

[HDMI-002 timing lessons](../HDMI-002/TIMING-LESSONS.md) record the subsequent
review. r10's APLL DPI mux is now a strong older-silicon failure suspect, supported
by SDK history, the TRM register table and the zero-DMA behavior. It is not a
vendor-confirmed isolated diagnosis. r11–r13's PLL picture failures remain
unresolved; do not attribute them to the APLL issue.

A separate static848×480 signal now works on this monitor with PLL240/7,
two480 Mbps lanes, matched1104×517 totals and unchanged Olimex bridge setup.
The Author confirms a good visible result. That excludes a categorical inability
to output480 active lines; it does not identify which difference repairs640×480.
The linked notes preserve the remaining hypotheses and native512×384 lessons.
The preceding records, measurements and historical stop state are unchanged.
