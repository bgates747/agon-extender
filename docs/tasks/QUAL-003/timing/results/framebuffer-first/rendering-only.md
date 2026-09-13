# Rendering-only comparison — 2026-09-13

The Author requested that graphics API port performance be separated from
transport and upload performance. This report derives rendering-scope times
from the completed 39-case physical baseline, `baseline39.csv`, using the
existing metric definitions in [the protocol](../../protocol.md).

Both devices used mode 20: 512×384, 64 colours, single-buffered. Values are
medians of three instrumentation-enabled draw intervals. Percentage change is
`100 × (EDP time / mainboard VDP time − 1)`; negative means less time on EDP.
Each table starts with the largest EDP duration, not the smallest percentage
improvement. These are measured rendering scopes, excluding transport waits
and bitmap-upload time, not complete API-call latency or exclusive CPU cycles.

## Drawing primitives — metric 2

These are complete native primitive batches, including text, rectangles and
state operations where present. Both devices executed matching primitive counts.
The first row includes the drawing portions of a stage that also uploads assets;
its upload time is excluded from this metric. SHP23 retains the known colour
probe disagreement on both devices. Do not describe these scene totals as the
cost of a single bitmap PLOT.

| Rendering workload | Case | Mainboard VDP ms | EDP ms | Time change |
| --- | --- | ---: | ---: | ---: |
| Opaque, cutout and alpha-band bitmap scene | BSP03_01 | 37.607 | 11.518 | -69.4% |
| Direct drawing versus transformed/XOR bitmap plotting | BSP07_02 | 15.453 | 9.798 | -36.6% |
| Bitmap plots and graphics text with clipping | SHP23 | 10.511 | 6.885 | -34.5% |
| Graphics viewports, including one-pixel viewports | SHP20 | 7.823 | 6.041 | -22.8% |
| Direct bitmap drawing across four screen edges | BSP07_03 | 7.566 | 4.901 | -35.2% |
| 64 scroll-and-clipped-bitmap operations | COMBINED | 7.102 | 2.660 | -62.5% |
| 64 partial-viewport scrolls | SCROLL | 9.362 | 2.078 | -77.8% |
| 64 bitmap plots clipped to one row | CLIPROW | 6.334 | 1.951 | -69.2% |

## Repeated operations with assets already resident

The following batches prepare assets before timing and contain no scene captions
inside the measured interval. Divide each 64-operation aggregate by 64 to obtain
these amortized rendering costs. State-setting primitives and the shared timing
marker remain included; these are not individually instrumented bitmap blits.

| Rendering workload | Case | Mainboard VDP ms | EDP ms | Time change |
| --- | --- | ---: | ---: | ---: |
| One scroll plus clipped bitmap plot | COMBINED | 0.1110 | 0.0416 | -62.5% |
| Scroll 256×336 viewport downward one pixel | SCROLL | 0.1463 | 0.0325 | -77.8% |
| Plot resident 256×16 bitmap through 256×1 viewport | CLIPROW | 0.0990 | 0.0305 | -69.2% |

The combined sequence costs less than adding the separate tests. These are
workload-dependent observations, not interchangeable operation constants.

## Software sprites — metric 4

This scope covers `showSprites`: redrawing software sprites and saving their
backgrounds. These stages reuse loaded assets. The two devices recorded matching
numbers of calls for each listed stage. Caption drawing can trigger extra sprite
redraws; totals are stage aggregates, not the cost of one move/hide command.

| Rendering workload | Case | Mainboard VDP ms | EDP ms | Time change |
| --- | --- | ---: | ---: | ---: |
| Reduce overlapping group from four active sprites to two | BSP25_02 | 20.466 | 3.572 | -82.5% |
| Reactivate four; hide one within the group | BSP25_03 | 17.568 | 3.242 | -81.5% |
| Show/move overlapping sprites and draw background stripe | BSP25_04 | 7.752 | 1.460 | -81.2% |
| Deactivate overlapping group; includes preceding redraws | BSP25_05 | 7.915 | 1.403 | -82.3% |
| Three sprites: movement step 1 | BSP21_02 | 1.672 | 0.338 | -79.8% |
| Three sprites: movement step 2 | BSP21_03 | 1.603 | 0.325 | -79.7% |
| Three sprites: movement step 4 | BSP21_05 | 1.615 | 0.317 | -80.4% |
| Three sprites: zero-distance movement | BSP21_04 | 1.504 | 0.307 | -79.6% |
| Three sprites: positioning across screen edges | BSP21_06 | 0.900 | 0.187 | -79.2% |
| One sprite: line drawing triggers pending move | BSP22_04 | 0.460 | 0.093 | -79.8% |
| One sprite: explicit refresh after pending move | BSP22_03 | 0.465 | 0.090 | -80.6% |

The scope does not include every part of restoring old backgrounds or updating
sprite state. In particular, the deactivate-group stage includes redraws caused
by the caption before deactivation. Primitive and software-sprite scopes overlap;
do not add the tables or claim either scope is the full API latency.

## Hardware sprites and remaining measurement limits

Mainboard VDP composited hardware sprites during VGA scanout. EDP performed zero
scanline-composition calls because no output was requested in this pass. There
is therefore no valid hardware-sprite rendering percentage comparison yet.
Zero EDP time means no measured composition work, not infinitely fast rendering.
Mixed hardware/software stage totals are not presented as equivalent full-scene
composition. The failed population-stress cases remain excluded and unresolved.

The comparable measurements support faster EDP primitive drawing and software
sprite redrawing, while exact standalone bitmap-blit costs and equivalent
hardware-sprite composition remain unmeasured. Timing scopes use wall-clock
microseconds and can include preemption. Mainboard scanout stayed active while
EDP output was absent; timer hooks also have overhead. These results neither
qualify the full graphics API port nor establish gameplay FPS.

No new hardware experiment or optimization was performed for this breakdown.
Raw CSV, source corpus, image identities and prior failures remain in this folder
and the [owning findings](../../framebuffer-pass.md).

Loading and submission are reported separately in the [upload-stage tables](upload-stages.md).
