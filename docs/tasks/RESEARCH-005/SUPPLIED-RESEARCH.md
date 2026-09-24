I have now actually crawled through the FabGL entrails. The good news is that there is a **very definite place to do this hack**. The bad news is that my earlier idea that `setResolution()` could nearly do it for us was too optimistic.

### What the VDP actually does

Agon's `changeResolution()` in `video/agon_screen.h` does this:

```cpp
_VGAController->setResolution(modeLine, -1, -1, doubleBuffered);
```

So currently the **logical framebuffer dimensions and physical visible raster dimensions are deliberately identical**. Mode 8, for example, selects `QVGA_320x240_60Hz`; modes 8–11 differ only in which VGA controller/color depth they instantiate. ([GitHub][1])

Down inside `VGABaseController::setResolution()` we get:

```cpp
setScreenSize(m_timings.HVisibleArea, m_timings.VVisibleArea);

m_viewPortWidth =
    viewPortWidth <= 0 ? m_timings.HVisibleArea : viewPortWidth;

m_viewPortHeight =
    viewPortHeight <= 0 ? m_timings.VVisibleArea : viewPortHeight;

m_viewPortCol =
    (m_timings.HVisibleArea - m_viewPortWidth) / 2;

m_viewPortRow =
    (m_timings.VVisibleArea - m_viewPortHeight) / 2;
```

So FabGL **already has pillarboxing machinery**. If the physical raster is 1280 wide and the viewport is 960, it automatically centers it and produces 160 pixels of blank on either side. That's real existing functionality, not something we'd need to invent. FabGL documents viewport sizing as part of `setResolution()` as well. ([GitHub][2])

### Where things get interesting

`fillVertBuffers()` constructs the DMA chain. For each visible scanline it essentially constructs:

```text
[horizontal blank/sync + left pad]
[viewport DMA buffer]
[right pad]
```

So **this is exactly where the pillars already happen**.

More importantly, vertical multiscan is already implemented structurally. Every physical line gets emitted:

```cpp
for (int scan = 0; scan < m_timings.scanCount; ++scan)
```

and `DoubleScan` makes `scanCount == 2`; `QuadScan` makes it 4.

That's why current 320×240 doesn't require a 480-line framebuffer. FabGL just points multiple DMA scanlines at the same logical row.

So vertical **3×** scaling is actually quite close to existing machinery: extend the modeline parser/timing representation to support a scan count of 3, or otherwise set `scanCount = 3`.

That part is pleasantly mundane.

### Horizontal 3× is the actual hack

Here's the crucial discovery.

For Agon's paletted modes—2, 4, 8 and 16 colours—the framebuffer **is not what DMA ultimately sends to VGA**.

For example, `VGA8Controller` keeps the compact logical framebuffer, then its interrupt routine converts framebuffer palette indexes into physical RGB222 VGA scanline buffers:

```cpp
auto src  = (uint8_t const *) s_viewPortVisible[scanLine];
auto dest = (uint16_t*) lines[lineIndex];

for (int col = 0; col < width; col += 16) {
    ...
    auto v1 = packedPaletteIndexPair_to_signals[...];
    ...
    *(dest + 2) = v1;
    ...
}
```

**That is our insertion point.**

Currently:

```text
logical framebuffer

320 palette pixels
       │
       ▼
VGA8 ISR palette expansion
       │
       ▼
320 RGB222 samples
       │
       ▼
DMA → VGA
```

We change that to:

```text
320 palette pixels
       │
       ▼
VGA8 ISR palette expansion + 3× replication
       │
       ▼
960 RGB222 samples
       │
       ▼
DMA → VGA
```

Each logical pixel gets written three times to the temporary DMA scanline.

So this is **not a renderer modification at all**. Sprites, bitmaps, fonts, plotting, scrolling, Canvas, BASIC coordinates, etc. remain completely unaware that anything happened.

That's exactly what we wanted.

### The architectural wrinkle

FabGL currently assumes:

```cpp
m_viewPortWidth == physical DMA viewport width
```

The temporary `m_lines[]` buffers are allocated as:

```cpp
heap_caps_malloc(m_viewPortWidth, MALLOC_CAP_DMA);
```

and the DMA descriptor length is also:

```cpp
DMABuffers[index].length = m_viewPortWidth;
```

We need to break that assumption.

I'd introduce something like:

```cpp
m_hScanScale = 3;
m_vScanScale = 3;
```

and distinguish:

```text
logical viewport width  = 320
physical viewport width = 960
```

Then `VGAPalettedController::allocateViewPort()` keeps allocating the logical framebuffer for **320 pixels**, but allocates `m_lines[]` for **960 output samples**.

`fillVertBuffers()` uses **960** when calculating:

```cpp
m_viewPortCol = (1280 - 960) / 2;
```

giving our desired:

```text
160 |       960       | 160
    | 320 pixels × 3 |
```

### And 720p is already in FabGL

We don't even need to invent the modeline.

FabGL already contains:

```cpp
#define SVGA_1280x720_60Hz \
"\"1280x720@60Hz\" 74.48 1280 1468 1604 1664 \
720 721 724 746 +hsync +vsync"
```

So FabGL was explicitly designed to generate 1280×720 VGA timing. ([GitHub][3])

That removes another substantial unknown.

### One complication: 64-colour modes

Modes using `VGA2Controller`, `VGA4Controller`, `VGA8Controller` and `VGA16Controller` all have the ISR conversion stage where this is fairly natural.

**VGA64Controller is different.**

That's essentially FabGL's direct RGB222 framebuffer controller. DMA can consume framebuffer pixels directly, so there isn't already a palette-expansion scanline stage in which to sneak our 3× replication.

Thus I would **prototype this with mode 9/10/11 rather than mode 8**—one of the ≤16-colour 320×240 modes.

If that works, 64 colours requires either adding an intermediate scanline expander analogous to the paletted controllers, or devising another DMA trick.

### So the first experimental patch is surprisingly well bounded

I would *not* attempt to make this generic initially. Hard-code one experimental mode:

```text
logical:   320 × 240
physical: 1280 × 720 @ 60

horizontal:
    each pixel ×3
    320 → 960
    160 black pixels each side

vertical:
    each row ×3
    240 → 720
```

Touch primarily:

```text
agon-vdp/video/agon_screen.h
        ↓
vdp-gl/dispdrivers/vgabasecontroller.*
        ↓
vdp-gl/dispdrivers/vgapalettedcontroller.*
        ↓
vga16controller.cpp (or whichever depth we prototype)
```

The **heart of the horizontal hack is the individual `VGA{2,4,8,16}Controller::ISRHandler()`**, not the Agon renderer and not really `setResolution()`.

And I like this considerably more after tracing it. FabGL's architecture is bizarre, but the paletted controllers have accidentally given us almost exactly the abstraction we need: **logical framebuffer → continuously generated physical scanlines**. We're just asking that conversion to generate three physical samples per logical pixel instead of one.

The main thing I'd investigate before writing code is whether that ISR has enough CPU budget at a **74.48 MHz pixel stream** to generate 960 output pixels per line. That is now the obvious potential showstopper—not the framebuffer, DMA architecture, modeline, pillarboxing, or vertical scaling.

[1]: https://github.com/AgonPlatform/agon-vdp?utm_source=chatgpt.com "GitHub - AgonPlatform/agon-vdp: Official Agon Platform Firmware for all Agon models: ESP32 VDP · GitHub"
[2]: https://github.com/fdivitto/FabGL/blob/master/src/dispdrivers/vgabasecontroller.h?utm_source=chatgpt.com "FabGL/src/dispdrivers/vgabasecontroller.h at master · fdivitto/FabGL · GitHub"
[3]: https://github.com/fdivitto/FabGL/blob/master/src/fabglconf.h?utm_source=chatgpt.com "FabGL/src/fabglconf.h at master · fdivitto/FabGL · GitHub"
