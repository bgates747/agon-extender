# P4-PC display benchmark — 2026-10-04 UTC

## Executive summary

The current 1280×720, 24-circle demo renders approximately **12 frames/s** while
the P4 panel completes approximately **60 frames/s**. Most scanout frames repeat
an earlier render. Direct double buffering improved the result, but 60 animated
frames/s has not been achieved. These are on-device counters, not an HDMI
analyser or a stock Agon comparison.

## Tested configuration

1. Build `p4pc-playground-r09-b2026-10-04-00-08-52Z`, experimental; independently
   verified bootloader, partition table and app before explicit reset.
2. P4-PC Rev C, silicon v1.3; IDF 5.5.5 at
   `b774170ff46c393eeb5e495ea37936038d3f4f4f`, LVGL 9.6.0~1,
   CPU 360 MHz and PSRAM 200 MHz. Compiler remains the inherited debug `-Og`;
   LVGL uses its software renderer. No performance-optimized compiler or
   hardware drawing-backend result is claimed.
3. RGB888, 1280×720, matched 60 MHz DPI/LT8912B timing, two 720 Mbps DSI lanes,
   totals 1350×741; calculated 59.979 Hz. Two panel-owned framebuffers, direct
   dirty-area rendering, 16 ms update/refresh scheduling, 1 MiB dynamically
   allocated builtin LVGL pool. Orbit phase follows elapsed time.
4. Ethernet/SD initialization deferred, audio idle. The P4 serial owner executes
   a finite benchmark while the animation/LVGL tasks continue. Periodic status
   label updates from the serial owner's ordinary loop do not run during the
   benchmark command. This is an isolated demo benchmark, not combined-load
   qualification.

## Measured results

| Metric | Paused bars control | Orbital circles |
|---|---:|---:|
| Actual measurement window | 5.019977 s | 30.002633 s |
| Animation updates | 0 | 360 |
| Animation update rate | 0.000 updates/s | 11.999 updates/s |
| Completed LVGL render passes | 0 | 360 |
| LVGL render rate | 0.000 passes/s | 11.999 passes/s |
| Frame submissions | 0 | 360 |
| Submission rate | 0.000 frames/s | 11.999 frames/s |
| Panel framebuffer completions | 301 | 1800 |
| Panel completion rate | 59.960 frames/s | 59.995 frames/s |
| Mean LVGL render-pass duration | Not applicable | 78.380 ms |
| Maximum LVGL render-pass duration | Not applicable | 78.860 ms |

The paused control demonstrates that panel completions continue without new
updates, renders or submissions. The circle window contains five panel
completions for each render. A subsequent ten-second circle sample gave
11.900 render passes/s and 59.898 panel completions/s; boundary timing and
shorter windows limit precision.

For context, r06's ordinary USB samples gave 367 updates in 55.004 s,
approximately 6.67 updates/s. The newer timed sample is approximately 79.8%
higher in update rate. This is not a matched benchmark: buffering, pacing,
pool location and motion phase changed, and ordinary status updates differ.
The older sample has no valid render/submission/panel counters. Stock Agon's
512×384 has 4.6875 times fewer pixels than this 1280×720 scene; no stock Agon
run was performed here.

## Measurement semantics and limits

1. Animation updates count the prescribed 24-circle positions, with no n-body
   forces or interactions. Updates are not presented frames.
2. `LV_EVENT_RENDER_READY` counts completed render passes. Its interval from
   `LV_EVENT_RENDER_START` includes drawing, cache/transfer work and the port's
   frame-completion wait; it is not pure CPU drawing time. Buffer synchronization
   before the render-start event is outside that interval.
3. Frame submissions count the last LVGL flush in each pass. A boundary can
   include an in-flight submission. Panel completions count the existing
   driver callback and include repeated pixels; they do not independently prove
   unique frames accepted by the monitor.
4. Counts and window statistics use brief critical sections. Timing uses the
   P4's monotonic microsecond clock, which has not been externally calibrated.
   A one-event boundary difference is about 0.033 events/s over thirty seconds.
   Host command, retrieval and serial-output time are recorded separately and
   excluded from the reported measurement window. No per-frame serial logging.
5. r08's zero panel counter was invalid: its copied dependency lock selected
   the older r06 port source without the hook. r09 rebases only local copied
   component paths and audits compiled component directories. Exact actual
   r08 source-path evidence is retained; no general IDF callback defect is proven.
6. Startup can time out selecting scene 2 while the initial orbital objects
   and higher-priority renderer compete for the lock; direct startup bars still
   complete. Busy animation can also reject `demo widgets`. Retain these
   control-readiness defects; start widgets from paused startup bars for this
   bounded evaluation. Do not treat a busy rejection as a started demo or claim
   every `info` response contains renderer statistics.

## Reproduction and retained evidence

Read `HARDWARE.local.md` before bench use and select its exact stable endpoint.
The Pi invokes the maintained reset-safe client, for example:

```text
.venv/bin/python vdp/p4pc-demo/control.py --port PORT --timeout 45 "bench 30"
```

`bench` defaults to ten seconds and accepts 5–30 seconds. Select the desired
scene first and keep peripherals fixed. The firmware records its own start/end
markers and actual elapsed microseconds; the host should retain the reply with
`--log`. Command errors and absent completion are failures.

The ignored benchmark bundle contains raw command logs, UTC host start/end,
separate host duration and parsed device results. Installation artifacts,
compiled-path audit, full preflash rollback and original factory backup remain
machine-local; the task points to those records without duplicating endpoints.
No Agon operation, production promotion, commit or publication occurred.

## Widgets follow-up

After resetting to paused bars, widgets start acknowledged and a ten-second
window completed: 47 LVGL render passes in 10.013059 s (4.694 passes/s),
46 submissions (4.594/s) and 601 panel completions (60.022/s). Mean/max render
pass duration was 207.461/228.486 ms. The one-pass/submission difference is
consistent with a boundary crossing; neither is a unique HDMI frame count.
Subsequent USB info showed approximately 1,000,240 free pool bytes, largest
free block 999,552 bytes, and peak usage 61,708 bytes. Software runtime and
allocation headroom passed this bounded window; the Author confirms visibly changing widgets. These rates are a different workload and are not a performance ranking
against the 24-circle scene.
