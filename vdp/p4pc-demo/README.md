# P4-PC playground

## Executive summary

Standalone experimental ESP-IDF firmware for P4PC-001: native VGA/720p HDMI animation,
finite analog audio playback, persistent Ethernet and a USB serial command
prompt. This is not an Extender production profile. Agon is not connected.

## Controls

Use the board's USB Serial/JTAG endpoint, 115200 baud, without DTR/RTS reset. Use the supplied Linux client to avoid open-time
modem-line transitions; generic terminal programs may reset this board.
The prompt is `p4pc>`. `help` repeats the controls.
For a single command, use project Python to run
`vdp/p4pc-demo/control.py --port PORT "demo bounce"`; it leaves DTR/RTS
untouched and waits for a bounded command-completion prompt.

| Command | Behavior |
|---|---|
| `info` | Version, IP, heap, SD, scene; pool/render statistics when the display lock is available |
| `demo orbit` | Coloured circles in intersecting orbits |
| `demo bounce` | Bouncing coloured shapes |
| `demo bars` | Static eight-colour bars |
| `demo widgets` | Start the LVGL widgets slideshow once per boot, preferably from paused startup bars |
| `bench 30` | Finite 5–30 second paced benchmark; default 10 seconds; updates/renders/submissions/scanout and stage timings |
| `bench 20 draw` | Drawing capacity: sequential fixed motion steps/refresh, same cache writeback, no presentation/wait |
| `bench 20 rgb332` / `bench 20 rgb888` | Native 640×480 matched opaque-circle reference; direct packed writes/full clear, scanout stopped; restores GUI/prior scanout |
| `scanout off` / `scanout on` | Stop/resume P4 framebuffer DMA and DSI video; retained buffers; off blanks the monitor |
| `pause` / `resume` | Freeze/resume playground animation (does not pause the widgets slideshow) |
| `tone 440 3` | 440 Hz sine wave for 3 seconds; 50–4000 Hz, 1–10 seconds |
| `melody` | Short C-major phrase |
| `volume 65` | Set codec volume, 0–90; default 65 |
| `video` | Report framebuffer samples and LVGL flush count |
| `video raw` | Pause UI refresh and fill scanout memory with direct colour bars |
| `video pattern` | DSI host bars independent of framebuffer pixels |
| `video ui` | Restore UI rendering; resumes playground animation when widgets are inactive |
| `net start` | Start persistent Ethernet/DHCP (deferred during display diagnosis) |
| `sd mount` | Mount SD read-only test path without formatting or write test |
| `sd ls` | List the SD root, limited to 128 entries; no file writes |

The serial owner executes audio synchronously for its finite duration while
LVGL and networking run independently. Audio starts silent; output goes through
the analog headset jack at codec volume 65 with moderate signal amplitude and
short note envelopes. This is not HDMI audio or a stereo-separation test.

`prepare.py --resolution 640x480` selects native RGB888 VGA: PLL 240 MHz / 8,
30 MHz, totals 952×525 and calculated 60.0240 Hz, horizontal blanking 168/96/48,
vertical 10/2/33, VIC 1 and 4:3 metadata. The selected copied BSP slot is
repurposed, including LVGL and panel buffer geometry. It is not a small window
in a 720p framebuffer. Both DSI lanes use 360 Mbps, matching RGB888 pixel demand; peripherals remain idle. This is custom
blanking requiring monitor validation. `--vga-clock apll` retains the failed r10
25.2 MHz/800×525 control; it produced no framebuffer completions.

r11/r12 native output fails Author visual review despite advancing panel
counters. r13 tests LT8912B low-resolution settle and live-stream receiver/DDS
relock; this remains an experimental remedy. Render-only format results do not
require usable HDMI and do not establish a visual pass. The selected LVGL
software renderer has no direct RGB332 backend; the reference kernel excludes
antialiasing/labels and reports drawing, motion and cache times separately.
See the [packed-format method](../../docs/tasks/P4PC-001/RGB332-REFERENCE.md).

The default remains 1280x720, RGB888. r06 uses matched WLED-derived 60 MHz
DPI/bridge timing, two 720 Mbps DSI lanes and totals 1350 × 741, calculating
59.979 Hz. This custom blanking needs physical monitor acceptance; it is not
measured refresh or proof of universal monitor support. The ultimate target
is 60 Hz. The factory SDK's inherited configuration calculates approximately
75 Hz; the earlier unbuilt 80 MHz preparation remains historical evidence.
See the task's [timing research](../../docs/tasks/P4PC-001/DEMO-CANDIDATES.md).
r09 schedules animation and LVGL refresh at 16 ms, with orbit phase based on
elapsed time. This does not establish 60 rendered frames/s: the measured
24-circle 720p workload renders about 12 frames/s while the panel completes
about 60 frames/s. See the [benchmark](../../docs/tasks/P4PC-001/BENCHMARK.md).
Ethernet remains active after DHCP. The BOOT button is deliberately unused
because GPIO35 is shared with RMII TXD1. Do not use BOOT for scene selection.
SD mounting never formats; the upstream write-test function is not invoked.

## Build and provenance

Run `prepare.py` with the project `.venv/bin/python`, supplying `--upstream`
and a new `--output` directory, plus an Author-approved `--revision rNN`.
Optional `--resolution 640x480` selects the Author-requested native VGA
comparison; default is `1280x720`. It requires a clean Olimex checkout at
`04032d68e5c727870f9d40beb9e37b7ab3a66916`. The preparer copies the factory
project into an ignored build workspace, replaces its entry point, removes
unused test components and changes console/font/formatting configuration.
The timing adaptation changes DPI and LT8912B timing together, chooses an exact clock divider,
and disables low-power blanking. Provenance and the IDF divider/compensation
workaround are explained in `prepare.py` beside the edits. The widgets demo
is supplied by the pinned LVGL dependency; its slideshow uses no input device.
r09 uses direct double buffering and a 1 MiB builtin pool allocated through
IDF's fixed PSRAM malloc policy. The inherited compiler remains debug `-Og`;
no accelerated LVGL drawing backend is selected.
The upstream BSP retains its notices and board wiring. No upstream checkout
is edited. Main application code belongs to this project.

`build.py` uses project-owned ESP-IDF 5.5.5 at
`b774170ff46c393eeb5e495ea37936038d3f4f4f` and native host tools under the
ignored workspace. Its default workspace is `agents/p4pc-demo`, containing
`project`, `tools`, `python-env` and `build`. The toolchain is Espressif
`esp-14.2.0_20260121`; Python packages must satisfy IDF's v5.5 constraints.
`build.py` rebases copied local dependency paths into the selected prepared
project without changing registry pins, then checks the actual compiled
component directories. A stale copied lock previously selected an older port;
prepared source alone is insufficient evidence of compiled source.
Retain the generated component lock, SDK configuration, source manifest and
image hashes with each candidate. `version.txt` carries the short build suffix
because the IDF app-description field is limited in size.

Before replacement, preserve and device-verify the entire factory flash. Flash
only the generated segments at their recorded offsets, keeping header bytes,
and verify them before reset. Local endpoint, rollback and installation receipts
belong in `HARDWARE.local.md` and ignored evidence. The task record owns human
visual/audio acceptance and known limits.

The current main starts with paused direct framebuffer bars before creating the animation
task. Atomic pause controls stop incoming animation without waiting behind
rendering. `info` reads counters independently of the display lock; allocator
statistics can still be unavailable while rendering is busy. Ethernet/SD remain
deferred and audio idle. The original factory control and r06 bars/circles
passed physical review. The Author also confirmed changing r09 widgets.

`display_experiment.py` copies the pinned SDK's `esp_lcd` component into the
prepared project and adds a task-local stop/resume hook. Stop waits for a complete
DMA frame, skips rearming and disables DSI video/DPI demand. Resume rebuilds the
existing descriptors, retaining buffers. This is diagnostic source, not an SDK
patch or production display contract. The SDK reference remains unmodified.

Drawing-capacity mode holds the LVGL mutex for a finite window, executes one
fixed animation step and explicit refresh per iteration, and yields one tick
for idle/watchdog readiness. The ordinary tasks remain blocked or paused until
restoration. It bypasses the ordinary port flip/wait in both scanout
states and matches its full-frame cache writeback. LVGL keeps its two buffers
and synchronization. Active DMA repeats a buffer that the diagnostic may
overwrite; drawing-only counts are not safely presented FPS or visual quality.
The paired windows isolate DMA contention. Ordinary paced mode supplies the
practical visible reference; 60 scanout completions/s alone is insufficient.

For a benchmark, select the workload first and use the raw client with a timeout
longer than the finite command, for example `--timeout 45 "bench 30"`. Retain
its start/end markers, actual device microseconds and counter output with
`--log`. A panel completion can repeat pixels. The USB owner does not update
its ordinary periodic status label while the benchmark command runs.

Stage timings use complete intervals beginning inside the finite window.
`draw_mean_ms` is render duration minus wrapper flush time, including software
drawing/dispatch. `cache_mean_ms` measures writeback, `wait_mean_ms` the port's
frame-completion semaphore, and `refresh_mean_ms` includes layout and buffer
synchronization outside the render interval. Boundary counts may differ by one.
See the [native scanout comparison](../../docs/tasks/P4PC-001/SCANOUT-COMPARISON.md).
