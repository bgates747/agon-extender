# P4-PC demo candidates — 2026-10-03

## Executive summary

The strongest external lead is WLED-MM-P4: its author reports working HDMI on
the P4-PC after replacing the default Olimex timings. Its published 720p mode
calculates to 59.979 Hz. Recommend first evaluating that display configuration
in a small project-owned experiment, then Olimex's LVGL animation demo. The matched timing experiment has now built, flashed and booted as r06;
Author confirms steady bars and moving circles, but rejects animation rate. The Author requires an ultimate
60 Hz output target for Agon compatibility and monitor interoperability.

The received board reports silicon v1.3 in both factory and demo boot logs.
ESP-IDF supports that silicon, but selecting the correct silicon family and
pinning display dependencies matters. The earlier unbuilt r06 preparation requested 80 MHz. The Author subsequently
accepted the 59.979 Hz timing experiment; its distinct timestamp preserves that
preparation as history. See the task's current accepted-experiment record.

## Silicon and SDK findings

1. [Espressif's compatibility table](https://github.com/espressif/esp-idf/blob/master/COMPATIBILITY.md#esp32-p4)
   lists v1.0/v1.3 support from IDF 5.3. This does not qualify every peripheral,
   board BSP or dependency combination.
2. [IDF 5.5.5 configuration reference](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/kconfig-reference.html#config-esp32p4-selects-rev-less-v3)
   requires `CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y` for 0.x/1.x silicon; the
   default is disabled. Our retained r05 configuration already selects it,
   allows revisions 0.1–1.99 and runs CPU/PSRAM at 360/200 MHz. The observed
   failure is not a boot refusal caused by selecting only v3 silicon.
3. Espressif's [v1.3/v3.2 comparison](https://documentation.espressif.com/en/PCN202600801_ESP32-P4_Chip_Revision_v3.2_Upgrade_Chip_Revision_v1.3_Demand_Collection_and_EOL_Plan_Description.html)
   distinguishes stable v1.3 CPU/PSRAM clocks of 360/200 MHz from v3.2's
   400/250 MHz. Keep the existing v1.3 limits during comparisons.
4. The [v3.2 SDK advisory](https://documentation.espressif.com/AR2026-004_Compatibility_Advisory_for_ESP32-P4_Chip_Revision_v3.2_EN.html)
   discusses revision-specific flashing and watchdog behavior. Its conditional
   IDF 5.5.5 requirement for v3.2/external 32 kHz operation is not a requirement
   for our v1.3 specimen. Do not transfer later-silicon advice indiscriminately.
5. [Current official errata](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32p4/02-errata-summary/index.html)
   identifies affected revisions individually. Community warnings are leads;
   they do not prove an HDMI defect on this specimen or establish that all IDF
   6.x configurations fail on v1.3. For a control, prefer the exact factory SDK
   commit or a demo's declared tested SDK rather than changing several layers.

## Candidate ranking

Ranking favors evidence on the P4-PC/LT8912B path, credible near-60 Hz output,
then adaptation effort. Source-author reports are not local qualification.

| Rank | Candidate | Demonstration and board evidence | SDK/dependencies | Adaptation and limits |
|---|---|---|---|---|
| 1 | [WLED-MM-P4 HDMI branch](https://github.com/troyhacks/WLED/tree/Olimex_HDMI_Output) | Animated effects; author reports P4-PC HDMI and corrected 720p timings in [Olimex issue 1](https://github.com/OLIMEX/ESP32-P4-PC/issues/1) | PioArduino platform `55.03.31-2`; custom Arduino/core-library branches, not a reproducibly pinned SDK set yet | Best display configuration donor. Full application uses a personal EV-board profile, LED GPIOs and its own partition table; review those before any build intended for deployment. |
| 2 | [Olimex display_lvgl_demos](https://github.com/OLIMEX/ESP32-P4-DevKit/tree/main/SOFTWARE/Demo_Examples/display_lvgl_demos) | LVGL demo player; Olimex explicitly reports DevKit + MIPI-HDMI operation | Manifest selects `esp32_p4_function_ev_board: '*'`; exact IDF/LVGL not established by README | Small animation control; adapt to PC Rev C and pin dependencies. README's sample boot log is for an S3 board and does not identify the tested P4 SDK. No audio demo. |
| 3 | [Vectrex Mini](https://github.com/malbanGit/ESP32_P4_Vectrex) | Vector animation, LT8912B HDMI, audio, USB input; targets non-X P4 at 360 MHz/200 MHz PSRAM | Author reports IDF 5.5.1; LT8912B component pinned to 0.2.0 | Promising alternative framebuffer/scanout implementation. P4-PC wiring is unverified. Uses YUV422 memory converted to RGB888 output; review its HDMI/audio and peripheral setup. |
| 4 | [RetroESP32-P4](https://github.com/giltal/RetroESP32-P4) | Emulator launcher, games, audio and HDMI; targets Guition + Olimex LT8912 bridge | Exact SDK/silicon build selection needs inspection | Larger port, own partition layout and SD content. Prebuilt HDMI image is not a PC Rev C image; do not select it by filename alone. |
| 5 | [OpenLara](https://github.com/alexkid77/openlara_esp32p4) / [Quake II](https://github.com/alexkid77/ESP32_QUAKE2) | Moving 3D graphics and audio; EV-board DSI display, not PC HDMI | OpenLara reports 5.4.4/5.5.5/6.1; Quake II requires 5.5.5 | Later showcase candidates. Need PC HDMI/RGB888, codec, SD and USB adaptation and game assets. OpenLara writes saves/cache; these exceed the current read-only SD experiment. |

The official PC [Arduino example](https://github.com/OLIMEX/ESP32-P4-PC/tree/04032d68e5c727870f9d40beb9e37b7ab3a66916/SOFTWARE/Arduino/ESP32-P4-PC-MIPI-LCD-Arduino)
animates a progress bar on the separate ST7701 MIPI LCD, using Arduino 3.3.8
and LVGL 8.4.0. It specifies the before-v3 chip variant for silicon v1.3.
It is not an HDMI candidate for the connected monitor.

## Most useful external timing evidence

WLED's [display implementation](https://github.com/troyhacks/WLED/blob/4d27fd45946a4cf101f67dda4c827bba9b440bc5/wled00/wled_hdmi.cpp)
contains a custom mode with the following values. These are extracted source
configuration and calculated rates, not measurements on our monitor.

| Parameter | Published WLED 720p mode | Earlier unbuilt r06 factory comparison |
|---|---:|---:|
| Active pixels | 1280 × 720 | 1280 × 720 |
| DPI clock | 60 MHz | 80 MHz |
| PLL_F240M divider | 4 | 3 |
| DSI lane rate | 720 Mbps per lane, 2 lanes | Inherited Olimex configuration |
| Horizontal front/sync/back | 10 / 32 / 28 pixels | 48 / 32 / 80 pixels |
| Horizontal total | 1350 pixels | 1440 pixels |
| Vertical front/sync/back | 3 / 5 / 13 lines | 3 / 5 / 13 lines |
| Vertical total | 741 lines | 741 lines |
| Calculated refresh | 59.979 Hz | 74.974 Hz |

Refresh is pixel clock / horizontal total / vertical total. WLED sets both P4
DPI timing and LT8912B timing from the same mode, including bridge clock and
HDMI metadata. It disables low-power blanking and selects an exact divider.
Its custom blanking differs from standard CEA 720p timing: a 60 Hz label or
VIC does not establish acceptance by every monitor. Confirm the monitor's
reported mode and retain physical review independently of software timing.

Vectrex's pinned `main/hdmi.c` independently changes blanking for an 80 MHz
clock: total 1440 × 926, calculated 59.995 Hz. Its comments acknowledge that
the inherited 720p configuration runs at approximately 75 Hz. This provides
a second near-60 Hz strategy, with different memory/transport work.

## Local IDF comparison and earlier preparation boundary

1. Olimex's staged LT8912B C driver and timing header are byte-identical to
   the official PC reference. The BSP differs only by the task-local panel
   accessor before the prepared r06 edit. Selected HDMI, RGB888, one-framebuffer,
   DMA2D and cache settings match the checked-in vendor configuration.
   The checked-in project is a reference, not proof of the factory binary's
   complete dependency graph.
2. Exact factory-IDF source at `e0577ae677` uses floor division for the
   240 MHz / requested 64 MHz pixel clock: divider 3, actual 80 MHz. Its HAL
   uses that actual clock for DSI timing conversion.
3. Pinned IDF 5.5.5 at `b774170ff46c393eeb5e495ea37936038d3f4f4f`
   rounds to divider 4, actual 60 MHz. Its horizontal compensation yields
   total 1350 for the inherited 1440-pixel line, implying front porch -42
   after 1280 active + 32 sync + 80 back porch. This is an invalid geometry
   and a strong failure hypothesis. Visual causality remains unproven.
4. The Author approved r06. Its prepared source requests actual 80 MHz
   explicitly and adds `video pattern` to bypass framebuffer data through the
   IDF DSI host pattern generator. It preserves external bridge settings to
   isolate the comparison. It is not a 60 Hz solution.
5. The earlier 80 MHz r06 preparation succeeded; compilation stopped at registry connectivity
   during CMake configuration. It is unbuilt and unflashed. Fresh project-owned
   output preserves the original r05 build tree and images. Source/configuration,
   upstream diffs and retrieval hashes are retained under the ignored workspace.
6. Two clean r05 USB samples reported uptime 24107 then 188328 ms, scene 2,
   zero animation updates, no IP and no mounted SD. A `video` reply reported
   framebuffer data and 104 LVGL flushes. These bounded replies are not visual
   acceptance or proof of continuous stability. An earlier sample encountered
   a partial command and returned an error; it is not a successful info check.

## Source snapshots and next evaluation

| Reference | Selected research commit |
|---|---|
| Official PC reference | `04032d68e5c727870f9d40beb9e37b7ab3a66916` |
| WLED HDMI branch | `4d27fd45946a4cf101f67dda4c827bba9b440bc5` |
| Olimex DevKit/LVGL repository | `26705d36407a07324348927dfd30fbf4ffc1d94c` |
| Vectrex repository | `caf2d9b77e1c9eaa5b7f8805fc0172650dbea051` |
| RetroESP32-P4 repository | `339f17ff74eea4fe250d749fdcf0b5e544519c2a` |

These pin research, not approved installations. Machine-local downloaded
snippets, retrieval metadata and logs remain in `agents/p4pc-demo/`.

1. Recommend a project-owned minimal static/animated display comparison using
   WLED's 59.979 Hz geometry, with its matched DPI/bridge settings. The Pi builds
   and independently verifies each admitted image; the P4 transmits through its
   DSI host and onboard LT8912B to the existing HDMI monitor; the Author observes
   stability and checks the monitor's timing report.
2. Then adapt the Olimex LVGL demo player to the same validated display path,
   using pinned SDK/dependency versions. Establish animation separately from
   audio and peripheral load. Preserve the factory control and r05 evidence.
3. Keep silicon family, CPU/PSRAM clocks and USB client fixed while comparing
   display timing. A later SDK comparison should change the SDK independently.
   Determine whether 59.979 Hz/custom blanking meets the Author's eventual
   compatibility requirement before adopting it beyond this experiment.
4. Candidate selection does not authorize game SD writes, imported board GPIO
   profiles, an Agon connection, production promotion or publication. Further
   experimental identities follow the project's Author-approved revision policy.

## Evaluation admitted after research

The Author accepted the timing-first, LVGL-second recommendation. The
project-owned r06 build uses only WLED's numeric mode configuration, with
upstream driver notices retained. IDF/LVGL and silicon/CPU/PSRAM selection
remain fixed. LVGL widgets and its automatic slideshow are compiled in for
animation after static review. Build and exact-byte deployment passed; physical
review confirms static bars; orbit is slow and widgets exposed pool exhaustion. See [current task state](../P4PC-001.md).

Local evaluation now confirms the matched configuration produces steady bars
and orbital motion. The low animation rate and widgets allocation assertion
are separate open rendering issues. Exact SDK-version causality for the earlier
dark screen remains unproven: the accepted experiment changed clock, geometry,
lane rate and low-power behavior together.

## Bounded rendering research after physical output

[LVGL display setup](https://lvgl.io/docs/open/9.5/main-modules/display/setup)
describes direct rendering into display-sized buffers with only dirty regions
redrawn, and two buffers synchronized by LVGL. The locally pinned 9.6.0~1
implementation and copied Olimex port were reviewed before preparing r08.
[Espressif's DSI API](https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32p4/api-reference/peripherals/lcd/dsi_lcd.html)
provides panel framebuffer access and refresh-completion events. The local 5.5.5
driver source determines the exact behavior used here. r08 preserves the port's
existing refresh semaphore/callback, adding only a lightweight frame counter.

The inherited LVGL pool is 64 KiB. r06 widgets stopped at the image-transform
allocation assertion; r07 safely rejected a runtime 1 MiB pool because TLSF's
maximum pool size is compiled from `LV_MEM_SIZE`. r08 therefore configures a
1 MiB dynamically allocated builtin pool, retaining assertions, watchdog and
pool-usage diagnostics. r08 also tests direct double buffering and 16 ms pacing;
HDMI timing and SDK remain fixed. These are prepared experiments, not measured
performance results or a qualified general rendering design.
