# Retained display behavior and replacement boundary

This is the manual source trace for PORT-003 Review Gate 1. It records facts
from official VDP tag `v2.16.0` at commit
`c7ac293d2aa81ddfa693390549bcd909069c8fc3` and its pinned vdp-gl release
`all-the-plots`. Proposals belong in `PROPOSAL.md`.

## Public mode behavior

Authoritative documentation:

- `agon-docs:docs/vdp/Screen-Modes.md`
- `agon-docs:docs/vdp/VDU-Commands.md`
- `agon-docs:docs/vdp/Copper-API.md`
- `agon-docs:docs/vdp/Context-Management-API.md`

`VDU 22, mode` selects a one-byte screen mode. Modes above 128 are the
supported double-buffered variants. In those modes drawing targets an
off-screen buffer and `VDU 23, 0, &C3` makes the drawn buffer visible at the
next vertical frame boundary. In a single-buffered mode the same command waits
for the next boundary without swapping.

A mode change resets the graphics contexts and context-stack selection. It
also resets the Copper signal list and deletes secondary Copper palettes. A
failed requested mode falls back first to the preceding current mode and then,
if that also fails, to mode 1.

The mode table fixes the following behavior, independent of the eventual
physical sink:

- supported mode numbers, including the legacy interpretation of modes 0–3;
- logical color counts of 2, 4, 8, 16, or 64;
- physical canvas dimensions and nominal 60, 70, or 75 Hz frame cadence;
- supported double-buffered combinations;
- logical-coordinate scaling to the Agon graphics coordinate space;
- rectangular-pixel detection; and
- mode 7 Teletext initialization over the ordinary bitmapped Canvas.

## Official facade trace

Source: `agon-vdp@v2.16.0:video/agon_screen.h`.

The header owns global `canvas`, `_VGAController`, color depth, palette,
dimensions, logical scale, rectangular-pixel flag, legacy-mode flag, and
current mode. Its factory currently chooses one of five classic VGA controller
classes by color count.

The facade has four distinct responsibilities:

1. It binds official VDP code to a concrete display controller and Canvas.
2. It owns the mode table and translates each mode into color depth,
   dimensions/modeline, and double-buffering state.
3. It exposes palette and Copper operations by downcasting the controller to
   the classic `VGAPalettedController` type.
4. It exposes completion, swap, cursor-position, dimensions, scale, and frame
   state used elsewhere in official VDP code.

`updateVGAController()` constructs a new color-depth-specific controller,
ends and destroys the old controller, stores the new controller, and begins
it. `changeResolution()` then destroys the old Canvas, asks the controller to
set its resolution, enables background primitive execution, creates a new
Canvas, derives dimensions and scaling, and diagnoses insufficient vertical
allocation by comparing screen and viewport heights.

`changeMode()` changes `videoMode` only after success. It restores the palette
for every recognized mode attempt, including a recognized mode that failed.

Source: `agon-vdp@v2.16.0:video/vdu.h:299`.

The `VDU 22` handler clears and waits for the old display, disables Teletext,
removes all VSYNC callbacks, and attempts the mode change. On failure it
attempts the old `videoMode`; on a second failure it selects mode 1. It then
resets all contexts, initializes both sides of a double buffer, restores a
visible cursor, resets mouse positioning, emits mode-change callbacks, and
sends the resulting mode information to MOS.

This behavior means allocation and controller-start failures are
application-visible even when no error packet is returned: the selected mode,
dimensions, context state, callback state, and mode-information packet reveal
the result.

## Canvas and primitive lifecycle

Sources:

- `vdp-gl@all-the-plots:src/displaycontroller.h`
- `vdp-gl@all-the-plots:src/displaycontroller.cpp`

Canvas converts drawing calls into `Primitive` records and passes them through
`BitmappedDisplayController::addPrimitive()`. Common code owns paint state,
origin and clipping, primitive dispatch, paths, glyphs, bitmaps, software
sprites, cursor objects, readback orchestration, and dynamic primitive-data
lifetimes.

The current scheduling semantics differ by buffering state:

- In single-buffered background mode, ordinary primitives enter the FreeRTOS
  execution queue and are processed by the display engine around frame
  boundaries.
- In double-buffered mode, ordinary drawing executes immediately against the
  drawing buffer. A `SwapBuffers` primitive enters the one-element execution
  queue and the caller waits for task notification from its executor.
- Disabling background execution drains pending work synchronously.
- `processPrimitives()` suspends background execution, drains the queue,
  refreshes sprites, resumes execution, and queues a refresh region.
- Canvas `waitCompletion(true)` waits for queued work with frame
  synchronization; `waitCompletion(false)` may force immediate processing.
- Canvas `swapBuffers()` submits the swap primitive. Canvas `noOp()` provides
  the single-buffered path used to wait for a frame boundary.

Queue emptiness alone is not a sufficient completion contract: the current
executor can have removed a primitive from the queue while still executing it.
The replacement must qualify completion and swap notification at the same
observable boundary, not merely reproduce the present busy-wait
implementation.

## Abstract backend contract

`BitmappedDisplayController` inherits the common `BaseDisplayController`
resolution, lifecycle, dimensions, type, and color-count contract. It adds
the following backend obligations:

- native pixel format and bitmap-save width;
- suspension and resumption of background primitive execution;
- full-color screen readback;
- pixel, line, row, ellipse, arc, segment, sector, clear, and scroll operations;
- glyph, invert, foreground/background swap, and rectangle copy operations;
- buffer swap;
- native, mask, RGBA2222, and RGBA8888 bitmap operations; and
- transformed bitmap operations.

`GenericBitmappedDisplayController` supplies reusable geometry algorithms as
templates over concrete pixel preparation and raw row/pixel operations. It is
part of the retained common renderer, not part of the excluded VGA physical
engine.

The generated exact declaration inventory is
`generated/display-evidence.yaml`; its Markdown projection is
`generated/display-evidence.md`.

## Palette and Copper semantics

Official VDP drawing in 2-, 4-, 8-, and 16-color modes records logical palette
indices in packed native framebuffers. The 64-color controller stores a fixed
six-bit RGB value in the low bits of an eight-bit physical pixel whose high
bits also carry VGA sync state. Its native background-save path forces those
high bits set. The replacement must preserve any internal save/restore
expectation while excluding physical sync bits from authoritative logical
storage. The concrete controllers quantize physical output to the stock
64-color RGB222 space.

Palette 0 is both the ordinary drawing palette and the default output palette.
Copper can create secondary palettes, alter their entries, and install a
signal list selecting palettes by output scanline. Drawing still records
indices using palette 0; Copper selects the output interpretation during
scanout. Copper is unavailable in fixed 64-color modes.

Consequences for the replacement:

- changing a Copper palette must not rewrite the logical framebuffer;
- screen readback and native bitmap copies operate on logical framebuffer
  state rather than a post-Copper RGB presentation;
- the presentation compositor must select the correct palette for each row;
- palette 0 mutation changes both future drawing-color lookup and output; and
- a mode change must reset the signal list and secondary palettes.

## Sprite and cursor semantics

Common display-controller code distinguishes software sprites from hardware
sprites. In a single-buffered mode, software sprites save the covered
background, draw into the framebuffer, and restore it around updates. In a
double-buffered mode their lifecycle follows the drawing buffer.

The classic paletted VGA controllers instead insert hardware sprites, the
mouse cursor, and the optional text cursor while converting each scanline for
physical output. These overlays therefore do not become ordinary framebuffer
pixels and do not belong in framebuffer readback. Copper affects software
sprites because they are stored as framebuffer indices; it does not recolor
hardware-sprite pixels produced as a separate scanout overlay.

The P4 replacement must preserve that distinction in its presentation
compositor even though no VGA scanline ISR remains.

## Frame counter and callbacks

The classic controllers increment public `VGABaseController::frameCounter`
from their physical frame interrupt. Official context code reads it to detect
frame progress, idle/paged-mode behavior, cursor timing, and waits. Context
variable writes can also replace its low and high halves directly.

This is an upstream coupling outside the abstract base-controller contract.
The replacement therefore needs an upstream-recognizable frame-counter seam;
changing only the abstract class is insufficient.

The logical frame event must continue even with no sink, a disconnected sink,
or a backpressured sink. A physical RGB/MIPI VSYNC callback may recycle a sink
buffer but cannot become the sole source of official VDP frame progression.

## Old physical assumptions and disposition

| Assumption or facility | Classification | PORT-003 treatment |
|---|---|---|
| Canvas, primitive dispatch, paint/clipping, generic geometry | Retained algorithm | Compile retained common code with narrow architecture fixes. |
| Packed native pixel encodings and per-depth raw operations | Retained behavior, implementation seam | Preserve formats initially; port useful algorithms behind one project-owned controller. |
| FreeRTOS primitive queue and task notifications | Retained contract, replaceable implementation | Preserve ordering/blocking behavior; qualify a P4-safe executor. |
| Modeline-to-mode dimensions and cadence | Retained logical data | Parse or replace with an explicit logical mode descriptor; do not retain VGA signal generation. |
| Public frame counter and frame waits | Retained application behavior | Advance from a sink-independent logical frame clock. |
| Palette lookup, quantization, Copper signal list | Retained behavior | Store as logical state and apply through the common compositor. |
| Software sprites | Retained algorithm | Keep common framebuffer save/draw/restore behavior. |
| Hardware sprites and cursors inserted during scanout | Retained presentation behavior | Compose as non-framebuffer overlays. |
| GPIO matrix, VGA pins, sync bits embedded in pixels | Excluded physical engine | No P4 equivalent in the logical backend. |
| I2S1 register programming and DMA descriptor chains | Excluded physical engine | Sink implementations use maintained P4 facilities independently. |
| Physical VSYNC ISR as renderer and frame clock | Excluded physical engine | Replace with a logical frame service; sink callbacks only report sink state. |
| DMA-capable framebuffer allocation | Excluded assumption | Allocate logical storage by its actual P4 consumer and cache constraints. |
| CPU-cycle budgets and a task pinned for a shared Xtensa cycle counter | Excluded assumption | Use time-based budgets only if qualification proves they are needed. |
| Xtensa coprocessor save/restore around transformed bitmaps in ISR | Narrow mandatory adaptation | Execute transforms in task context on P4; retain the algorithm without Xtensa register code. |
| Mouse-positioner parameter typed as `VGABaseController *` | Cross-task coupling | Input adaptation owns the type seam; PORT-003 preserves cursor positioning without retaining PS/2/VGA code. |

The machine inventory records 478 bounded architecture-pattern hits across 31
direct display files. Counts are navigation evidence, not 478 independent port
requirements.

## Compatibility risks requiring fixtures

- exact packed-pixel ordering for all five color depths;
- RGB-to-palette quantization and duplicate palette entries;
- readback before and after software sprites, hardware overlays, and Copper;
- queue completion versus primitive execution completion;
- swap notification and visibility at the logical frame boundary;
- frame-counter writes, rollover, missed service deadlines, and callback order;
- single-buffer tearing and mutation during presentation;
- transactional behavior when allocation or initialization fails mid-mode
  change; and
- Teletext, mouse-cursor, and context-reset interactions at mode change.
