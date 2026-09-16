# QUAL-004 acquisition research

## Executive summary

Stock pixel queries wait for drawing then read the drawing framebuffer. That is
not sufficient for hardware sprites or displayed-page qualification. Stock VGA64
ISR prepares actual visible rows, then decorates them with hardware sprites.
A diagnostic tap immediately after decoration can observe these exact bytes.
This adds capture only, not a replacement renderer.

## Pinned references and capture contract

1. Official read-only VDP v2.16.0, c7ac293d2aa81ddfa693390549bcd909069c8fc3;
   vdp-gl ac2dd5986daf496c43ae8e7fe41836274aec54a0. Official documentation:
   VDU-Commands.md, Screen-Modes.md, Bitmaps-API.md, Copper-API.md in agon-docs.
2. video/vdu_sys.h sendScreenPixel calls waitPlotCompletion then Context::getPixel.
   canvas.cpp getPixel delegates to controller readScreen. VGA64 readScreen reads
   m_viewPort (drawing page); this is not the displayed-page oracle.
3. vga64controller.cpp ISRHandler copies s_viewPortVisible rows, invokes
   decorateScanLinePixels, then advances. vgabasecontroller.h defines physical
   byte addressing as x XOR 2. Low six bits are BBGGRR. Decode to RGB888 using85.
4. Initial self-assigned acquisition design: one requested scanout row copied
   into bounded internal RAM after decoration, then emitted from task context
   over debug serial. No serial writes or PSRAM allocation in the ISR. Capture
   spans multiple refreshes: fixtures must be static, parser held at checkpoint,
   and two complete captures must match before static-image parity is admitted.
   Animated Copper/palette changes require a different coherent-frame method;
   mark that coverage deferred, never claim a static stitched image proves it.
5. P4 existing web snapshots provide complete immutable composed images. Use a
   single requested snapshot at a stable checkpoint, not a performance stream.
   Validate canonical colour ordering with known colour blocks first.
6. First capture implementation targets64-colour modes. Lower-depth modes need
   taps after their palette expansion; defer if time reserve is reached. Missing
   graphics APIs are recorded not implemented; this task must not add them.
