# SCROLL-001 — Pattern-based scrolling qualification

Measure actual completed scrolling on mainboard VDP and Extender while using the
approved mode-specific pattern as the moving image. Begin with single-buffered,
240-line, 4:3 modes. Full-screen means every pixel moves, preserving stock's
full-width/full-screen optimized paths. Timing must describe VDP execution, not
merely eZ80 command transmission. This records the Author's evolving design;
implementation and hardware execution are not started.

## Agreed scope

1. One eZ80 program contains eight cases: full-screen up/down/left/right and
   partial-region up/down/left/right. Advance one logical pixel per vblank.
2. Begin with 4:3 modes; wide Extender variants follow later. Initial 320×240
   geometry: vertical partial region256×240, centered with32pixel sidebars;
   horizontal partial region320×176, centered with32pixel top/bottom margins.
   Larger-mode geometry is not yet selected; do not extrapolate silently.
3. Wrap at the tested region's own opposing boundary. Partial cases leave the
   surrounding image unchanged. Full-screen cases move the entire image,
   including identification embedded in the pattern; no reserved fixed banner.
4. Use each mode's approved palette-quantized pattern. Preserve original image
   identity/phase and clear case announcements between measured runs.
5. Vblank paces drawing updates. Exclude intentional vblank waiting from rendering
   timing. Record overload/backlog rather than disguise missed pacing slots.
6. The Author requests time spent by the VDP executing the full rendering work.
   Distinguish scroll primitive execution, exposed-edge wrap restoration and
   completed scroll-plus-wrap rendering. eZ80 submission/return latency is not
   an acceptable substitute for actual VDP rendering time.
7. Compare mainboard versus Extender at equal mode/geometry/work, and compare
   directions/full versus partial within each processor. State dimensions and
   scope; do not normalize away the differing region areas.
8. Double-buffered tile-scroller game mechanics remain deferred in DBUF-001;
   they are not an added case or dependency here. Frozen prior suites/results
   remain historical evidence, not editable test definitions.

## Source review and timing investigation

1. Official VDP v2.16.0 Context::scrollRegion in
   ../../../../agon-vdp/video/context/graphics.h routes public VDU23,7 to Canvas
   scrolling. Official command contract:
   ../../../../agon-docs/docs/vdp/VDU-Commands.md section VDU23,7.
2. Project-retained upstream-shaped VGA64Controller::VScroll uses generic
   row-pointer swapping with sidebar copying when the region is narrower than
   the viewport. Full-width scrolling avoids sidebar copies. HScroll contains
   specialized aligned packed-byte/word shift paths for one-pixel scrolling.
   Locations: vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp and
   vdp/vendor/vdp-gl/src/displaycontroller.h. Establish the immutable upstream
   library revision before treating a full audit as complete.
3. P4 alternative controller: vdp/video/extender/display/p4_rgb888_controller.cpp.
   Full-width vertical row-pointer rotation is retained for owned rows. Borrowed
   panel storage uses stock's copy/fill overload because DMA row addresses cannot
   rotate. Narrow linear-byte vertical regions also select that copy/fill path.
   Horizontal scrolling is rewritten as row-wise memmove plus exposed fill;
   upstream's packed VGA lane-shift specialization is not retained there.
4. Audit the exact selected source/controller/format in each mode before building
   the fixture. Root working tree and retained experimental source can differ;
   no source selection or firmware repair is implied by these initial findings.
5. Canvas.waitCompletion exists internally, but waitCompletion(false) actively
   processes primitives immediately and therefore changes normal scheduling;
   Canvas.getPixel itself is not a universal completion barrier. Do not time
   either wrapper and call that normal-worker scroll execution.
6. Inspect/reuse retained operation timing at the actual normal primitive
   execution boundary, with matched mainboard/P4 scope and monotonic clocks.
   Include wrap drawing and final render housekeeping in a separate complete
   update measure. Retain queue wait separately, no forced synchronous execution
   merely to simplify timing. See docs/testing/game-timing.md and existing
   render operation instrumentation in displaycontroller.cpp.
7. Establish a bounded diagnostic record/terminal protocol compatible with EMOS;
   no private keyboard completion carrier or unproved stock-poll fence. Prove
   operation ordering, measurement overhead, missing records and timeout behavior
   before claiming actual completed rendering measurements.

## Remaining gates

1. Finish the stock-versus-port path audit, including actual linked upstream
   revision, selected controller, full-width optimizers and partial-region
   algorithms. Record retained versus rewritten behavior without assuming a
   rewrite is beneficial.
2. Agree the precise primary timing interval and normal-worker instrumentation,
   clock calibration, controls and record retrieval before implementation.
3. Select initial mode/colour matrix, per-case duration/repeats, overload policy
   and how current case identity stays accessible without changing full-screen
   scroll semantics. Do not assume additional resolved choices.
4. Build a new revision, validate region/wrap correctness and timing independently,
   then stage under the normal readiness protocol. No flash/reset/run authorization
   comes from this planning record.
