# Standalone HDMI timing pattern

Experimental P4-PC fixture for [HDMI-002](../../docs/tasks/HDMI-002.md).
It replaces the complete P4 application temporarily. No Agon routing, keyboard,
Ethernet, SD, LVGL or game services are started. Product renderer code is unchanged.

The current r02 trial generates custom 848×480 near 60 Hz with supported PLL240/7,
two 480 Mbps DSI lanes and matched 1104×517 totals. The exact 33.75 MHz DMT/APLL
proposal was not deployed; the task explains the silicon-revision concern.

`pattern.c` writes BGR888 directly into the panel-owned framebuffer before DSI
starts. It is never repainted: subsequent USB logs record only frame-DMA progress
and HDMI hot-plug detection. These do not establish picture correctness. The
Author must inspect the outer border, all four corner labels, channel bars and
centered unscaled 512×384 field. Circle/square shapes help reveal stretching.

Use the repository Python environment:

```sh
.venv/bin/python tests/display/hdmi_timing_pattern_test.py
.venv/bin/python vdp/hdmi-timing-test/build.py --output agents/hdmi002/new-build
```

The builder requires the existing native ARM tools from the P4-PC demonstration
and ESP-IDF 5.5.5 at the pinned revision. It refuses an existing output directory,
freezes source/hash provenance, builds and merges the image, then checks compiled
source closure and factory segment contents. `manifest.json` and `build.log`
remain with the generated image. It does not flash.

Deployment requires the current machine-local bench identity, checked silicon
image headers, retained exact rollback and flash/readback evidence. Consult the
task and `HARDWARE.local.md`; do not reuse old private bench addresses or select
production from the newest generated file.

r03 adds `--timing 512x384`, `684x384`, `320x240` and `428x240` for isolated
native-active experiments. The default remains848×480. All retain the accepted
PLL240/7,1104×517 totals and480Mbps lanes; front porches absorb the change in
active dimensions. No resampling or black active border substitutes for native
pixels. `timings.py` owns the explicit experimental tuples; generated
`timing_config.h` and the manifest preserve the selection in each fresh build.
The two wide candidates round width to a multiple of4; aspect rounding is in the
manifest. These are not supported VDU modes. The512×384 physical trial fails
visual review despite continuous DMA progress. The Author now selects widescreen
HDMI with a centered512×384 game canvas;684×384 is the next standalone signal
trial. Its edge/color pattern covers the carrier, before centered-game integration.
Picture acceptance is separate from a successful build or frame-DMA counter.

r04 centers a512×384 image inside684×384, and320×240 inside428×240, with black
sidebars. The outer white border marks the complete carrier; the inner border
marks the logical image. Each color label is centered over its bar. This fixes
the r03 pattern's constant-spacing labels without changing timing or bridge
initialization. The Author confirms the r03 684×384 signal steady with correct
circle/square aspect and all outer edges visible. The r04 centered layout also
passes Author review as correct and steady. These are bounded pattern results,
not qualification of full Extender services or games at this timing.
