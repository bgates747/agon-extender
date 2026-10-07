# Packed RGB332 render-only reference

## Executive summary

The Author requests a 640×480 one-byte-per-pixel comparison with stock Agon
storage. The selected LVGL 9.6.0~1 software renderer has no direct RGB332 output
path. A small reference rasterizer therefore writes RGB332 directly to PSRAM,
and also writes RGB888 with identical opaque-circle geometry and pixel work.
Host tests pass canonical packing, per-pixel format equivalence and clipping
bounds. Four clean device windows measure RGB332 drawing at 3.786 ms/frame
and RGB888 at 13.758 ms/frame, with zero DMA completions. Total throughput is
approximately 200 versus 66.7 frames/s including motion/cache/yield. This does
not fix native HDMI output
or establish an Agon performance comparison on the disconnected hardware.

## Method and comparability

1. Native logical dimensions 640×480: 307,200 bytes/frame for packed RGB332,
   921,600 for RGB888. Two retained panel-owned PSRAM buffers alternate; their
   larger allocation is retained, but only each format's logical bytes are
   written and cache-synchronized. P4 framebuffer DMA/DSI output is stopped
   and its completion counter must remain unchanged throughout each window.
2. Both formats use the same 24 circles, sizes 14/24/34/44 and prescribed orbital
   paths. The rasterizer clears the whole frame and writes identical clipped
   opaque spans. No antialiasing, GUI labels, dirty-area synchronization or
   intermediate RGB888-to-RGB332 conversion. Report this separately from LVGL's
   antialiased GUI; its workload and renderer differ.
3. RGB332 packs `RRRGGGBB`. Quantization occurs while writing the destination,
   not in a subsequent image-conversion pass. The RGB888 kernel stores B,G,R,
   matching the current panel memory representation. Optimized span kernels
   are format-specific, with identical geometry and full-clear work.
4. Separate motion calculation, drawing and cache writeback timings, plus actual
   elapsed device microseconds and frame count. Yield one FreeRTOS tick between
   frames for idle/watchdog readiness. Total throughput includes this yield;
   inverse mean drawing duration alone is not presented FPS. No HDMI transport
   is included, and no physical display acceptance is inferred from a checksum.
5. The P4 serial owner runs finite `bench 20 rgb888` / `bench 20 rgb332` commands.
   Restore RGB888 GUI state and prior DMA state after sampling. Preserve raw
   logs, exact firmware/source identities, comparator configuration and rollback.
   Use repeated reversed order to disclose cache/order variation.

## Official Agon contract consulted

Read-only official documentation: `agon-docs/docs/vdp/Bitmaps-API.md` describes
RGBA2222 as one byte per pixel; `Tile-Engine.md` specifies AABBGGRR ordering and
64 visible colours. Captured/native framebuffer data and bitmap API formats are
not interchangeable contracts: the documentation distinguishes native RGB222
or palette-indexed bytes from RGBA2222 bitmap storage. RGB332 matches the one-byte
storage cost, not alpha semantics, channel packing or the exact Agon renderer.
No MOS/VDP API or wiring is changed by this reference test.

## Implementation boundaries

The portable reference is maintained in `vdp/p4pc-demo/main/render_reference.c`.
Its host test compares every RGB332 pixel against quantized RGB888 output across
moving, overlapping and edge-clipped circles, and checks sentinel guards around
both buffers. This validates actual packed colour writes rather than substituting
LVGL's 8-bit grayscale output. ESP-IDF 5.5.5's current RGB definitions and DPI
panel path also do not expose a direct RGB332 scanout choice; this test uses CPU
writes only and does not claim hardware acceleration or native HDMI support.

Espressif's [P4 datasheet](https://documentation.espressif.com/esp32-p4_datasheet_en.html)
lists MIPI DSI colour formats RGB888/RGB666/RGB565, plus YUV/gray inputs; it
does not list RGB332. The pinned IDF colour definitions and LVGL software
format definitions likewise do not expose direct packed RGB332 rendering here.
This establishes the selected-path boundary, not a claim about every possible
P4 peripheral or future SDK.

The ordinary LVGL on/off comparison remains documented separately in
[the scanout comparison](SCANOUT-COMPARISON.md).

## Device results — r13

Exact build `r13-b2026-10-04-01-20-08Z`, ELF prefix `2bbe38cd7`; independently
verified flash segments and complete preflash rollback. IDF 5.5.5, LVGL
9.6.0~1, `-Og`, CPU 360 MHz, PSRAM 200 MHz and 1 ms FreeRTOS ticks. Animation
is paused before starting the reference, which owns the LVGL mutex and stops
DMA. The benchmark's own prescribed-motion loop remains active. Every command
has a complete echo, result and prompt. Order: RGB888, RGB332, RGB332, RGB888;
20 seconds each, measured with the P4 microsecond timer. Host elapsed time and
raw captures are retained separately in the ignored r13 reference bundle.

Worst aggregate drawing duration first. Means are weighted by measured frame
counts; throughput is total frames divided by total device elapsed seconds.

| Format | Bytes/frame | Drawing mean (ms) | Drawing max (ms) | Cache mean (ms) | Motion mean (ms) | Total throughput (frames/s) |
|---|---:|---:|---:|---:|---:|---:|
| RGB888 baseline | 921,600 | 13.758 | 13.913 | 0.485 | 0.128 | 66.667 |
| RGB332 | 307,200 | 3.786 | 3.945 | 0.456 | 0.127 | 200.000 |

1. RGB888 repeats: 1334 frames/20.009920 s and 1334/20.009889 s.
   RGB332 repeats: 4000/20.000068 s and 4001/20.004873 s. All four windows
   have zero DMA completions and nonzero output checksums. Geometry follows
   fixed logical steps; faster variants cover more logical steps per window.
2. RGB332 reduces drawing duration **72.48%** relative to RGB888,
   `(1 - 3.786/13.7575) × 100`. Total throughput improves **200.00%**,
   `(200.000295/66.666985 - 1) × 100`. Storage falls **66.67%**. Format-specific
   span/clear kernels also differ (`memset` for one-byte colour); this is not
   a measurement attributing every difference solely to byte count.
3. The watchdog-friendly one-tick yield contributes to approximately 5 ms
   total RGB332 frame periods. Drawing plus cache/motion is approximately
   4.37 ms; do not describe inverse drawing time as displayed FPS or project
   the 200/s figure into an accepted HDMI renderer. No scanout/conversion cost
   or antialiasing/GUI overhead is included.
4. Recovery restores RGB888 GUI/scanout. A five-second ordinary software
   check records 29.120 renders/s and 60.035 panel completions/s. The Author
   subsequently reports no usable picture, while objecting that visual states
   were changed before observation. Therefore native HDMI remains unaccepted;
   the Author also confirms no usable picture after bars are restaged by a fresh
   reboot and left unchanged until their reply. The board remains on paused bars.
5. An earlier RGB888 sample completed but its incomplete USB echo failed the
   host command gate; it is retained separately and excluded from aggregates.
   Pausing ordinary animation produced complete repeated captures. No cause
   for the lost echo is claimed. Factory/prior-image rollback remains intact.
