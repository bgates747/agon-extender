# Original controller binding proof — stock-backend-binding-r01

R1 was accepted for freezing on 2026-09-10 under the accepted
[restoration contract](../stock-backend-restoration.md). The five original
VGA2/4/8/16/64 classes compile and link with their common renderer and stock
utilities for ESP32-P4. The host comparison has **180 passing checks and two
failed logical expectations in unchanged upstream code**. Those failures are
preserved, not repaired or relabelled as passes.

This is an experimental, synchronous source-binding proof. It produces a host
executable and a P4 **relocatable object**, not a bootable firmware image. It
does not select the new classes in the ordinary console, start a drawing/output
worker, access hardware or qualify performance. R2 owns independent drawing and
output integration; R3 owns target execution/qualification.

## Evidence and reproduction

The [result manifest](results.json) records the build/run identity, compiler
versions, dependency hashes, source-preservation checks and link boundary.
[Native comparison output](native-rows.txt) records every check, including the
first differing row bytes in the two failures. Local commands, compiler logs,
objects, DSP archive binding and full disassembly are retained under the
ignored `agents/stock-backend-r1/` build directory named in the manifest.

From the repository root:

```sh
.venv/bin/python -B docs/tasks/PORT-003/stock-backend-r1/run.py
```

The runner uses the installed P4 SDK/toolchain and the existing PlatformIO
compile database to reproduce actual target flags. It does **not** invoke
PlatformIO or CMake, install packages, modify their build directories, launch
the emulator or touch either board. It creates a newly stamped evidence
directory. The host executable exits 1 for the two failed logical expectations;
the runner reports their exact known upstream disposition and rejects any
additional, missing or altered failure. It does not print an all-tests-pass
claim. The remaining unresolved target symbols belong to the real SDK/C/C++
runtime; no FabGL/controller or DSP matrix symbol remains unresolved.

## Source binding and precise changes

Upstream is vdp-gl `all-the-plots`,
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`, as used by official VDP v2.16.0.
The project snapshot `a773b19` preserves those original controller bytes and
the accepted first-pass no-fix contract. All edits are gated by
`AGON_EXTENDER_STOCK_ROWS_PROOF`; it is absent from production source selection.

| Source/symbol | R1 selection | Why the binding exists |
|---|---|---|
| All seven controller headers | Entire files unchanged | The installed P4 SDK accepts the original declarations, including descriptor types |
| VGA2/4/8/16/64 constructors | Pass `nullptr` instead of each `ISRHandler` address in the proof only; bodies unchanged | R1 does not attach a physical output interrupt |
| Five `ISRHandler` definitions | Original bodies retained in source, excluded from proof | Classic I2S end-of-frame/cache operations do not compile for P4 |
| All concrete pixel accessors, row paint/fill/copy/swap/scroll, glyph, bitmap, transformed-bitmap, palette and signal-table methods | Original implementations selected unchanged | Native representation and algorithms are the object of this restoration |
| `VGABaseController::init` | Original state initialization; omit `GPIOStream::begin` | No classic physical output engine |
| `VGABaseController::begin()` | Initialize state, retain 2-bit/channel interpretation; omit the GPIO-argument call | Do not bind classic default pins to P4 |
| GPIO-argument `begin`, `setupGPIO`, `freeBuffers`, `setDMABuffersCount`, `startGPIOStream`, `calcRequiredDMABuffersCount`, `fillVertBuffers`, `fillHorizBuffers`, `setDMABufferBlank`, `isMultiScanBlackLine`, `setDMABufferView`, `getDMABuffer`, `fill`, `moveScreen` | Original definitions retained, excluded from proof | Physical GPIO/I2S/DMA/output positioning closure; includes both `setDMABufferView` overloads |
| `VGABaseController::end` | Proof retires only its native allocations | No task or DMA reader exists to stop/join in R1 |
| `VGABaseController::setResolution(VGATimings...)` | Preserve geometry, quanta, sync values, row allocation, paint reset; exclude blank output rows, descriptor setup and task startup | Keep native lifecycle while isolating absent physical output |
| `VGABaseController::swapBuffers` | Preserve native row-table exchange; omit physical descriptor exchange | Prove drawing/visible plane identities independently of DMA |
| `primitiveExecTask`, `calculateAvailableCyclesForDrawings` | Original definitions retained, excluded from proof | R1 uses existing synchronous task-context execution; R2 must bind the real worker/clock, with timeout disabled |
| `VGAPalettedController::setResolution` | Keep native rows, palettes, signals and suspend/resume; exclude physical interrupt/stream tail | Preserve stock setup without a physical ISR |
| `VGAPalettedController::allocateViewPort`, `freeViewPort`, `onSetupDMABuffer`, `swapBuffers` | Original bodies unchanged | Actual SDK descriptor declarations compile; the descriptor callback is not invoked in R1 |
| Canvas, common display controller, codepages, fonts, utilities' original source/header | Unchanged | No new parser, renderer or public capture contract |
| `stock_render_utils.cpp` | Nine verbatim source groups replace the earlier re-expressed utility subset **only in the proof** | Whole upstream `fabutils.cpp` also owns classic peripheral/storage code; extraction avoids selecting that unrelated closure |

The utility groups retain original `isqrt`, `msToTicks`, `clipLine_code`,
`clipLine`, `Rect::merge/intersection`, `getBit`, `getCircleQuadrant`,
`quadrantContainsArcPixel`, `rgb222_to_hsv`, every `LightMemoryPool` method,
`CoreUsage::s_busiestCore` and `CurrentVideoMode::s_videoMode`. Licenses and
[exact source spans/hashes](utility-spans.json) accompany the selection.

`verify_source.py` checks all seven headers and nine shared files byte-for-byte.
It reconstructs each original controller branch and compares its code tokens,
including literals. It also verifies the utility bodies and eight independently
compiled original pixel accessors in `oracle.hpp`. No upstream algorithm has
been renamed, rewritten or fixed to obtain these results.

## Actual target dependencies and memory choices

The first unmodified VGA64 translation-unit compile failed specifically on
`I2S1.int_st.out_eof`, `I2S1.out_eof_des_addr`, and
`spi_flash_cache_enabled()` in its physical ISR. The local
`unmodified-target.log` records that compiler output. With that physical engine
excluded, the original drawing code compiles. Other original headers were
initially investigated but ultimately left unchanged because they compile.

Native allocation is **still upstream's allocation**: capability-selected
internal pools, indirect row tables, original row size and width/height quanta.
PAL2/4/8/16 use 1/2/3/4 bits per pixel; 64-colour rows retain native sync bits
and `x ^ 2` byte lanes. Stock palette output-line allocations retain
`MALLOC_CAP_DMA`. R1 introduces neither PSRAM selection nor a flat-row invariant,
extra padding, an alternative cache policy or a scalar replacement codec.

The P4 disassembly of the original PAL8 accessor retains `lw`/`sw` over
three-byte groups. Thus group addresses can be unaligned and its final
32-bit access extends one byte beyond the final three-byte group. R1 records
this unchanged access pattern; host execution and target compilation do not
qualify target misaligned access, allocator boundaries, cache behavior or
large-mode capacity. Native target execution must check those before ordinary
console qualification. If a processor-specific access binding becomes necessary,
it requires actual target evidence and byte-preserving changes under the
contract; an upstream cleanup is not authorized.

The host allocator models only allocation, not ESP-IDF capabilities. Host DMA
declarations are parse-only and never used for physical output. Target builds
use the real SDK types. `task_context.hpp` **aborts** if the unchanged common
renderer unexpectedly enters its Xtensa ISR/FPU branch; it provides no no-op
FPU implementation. Transformed bitmaps pass through the original ordinary
task branch. This does not qualify transformed drawing in an ISR.

## Native-row checks and retained observations

The actual side uses the original Canvas and concrete controllers. The
reference side applies unchanged upstream pixel accessors to an independently
calculated logical image. Explicit byte witnesses additionally distinguish
stock PAL8 `0,1,2,3,4,5,6,7` packing (`77 39 05`) and VGA64 sync/lane bytes
(`c2 c3 c0 c1`) from the former project codecs.

Each depth exercises clear/nonzero fill, all eight row-paint modes, full-width
VScroll with pointer identity, aligned/unaligned partial H/V scroll in both
directions, overlapping copy in both directions, a 96×32 bitmap clipped to a
46×1 inclusive viewport, public RGBA2222 capture, glyphs, a transformed bitmap,
software-sprite native background save/restore, single/double-buffer aliases,
direct original plane swaps and original dimension rounding.

**R1-O001 — preserved upstream two-colour scroll behavior.** In a 64×16 image,
scrolling viewport `(3,2)..(58,13)` vertically by −3 or +3 fails the independent
outside-preservation expectation. The original `genericVScroll` swaps the rows
and calls `VGA2Controller::swapRows` on the outside span `(59..63)`. Its leading
loop swaps that narrow span, then the trailing loop restarts at 56 and swaps
through 63. Pixels 59..63 are swapped twice; pixels 56..58 are also affected.
The exact portable bodies are unchanged and source-verified. This makes the
audit's SR-08/F009 concern reproducible on the host; it is not a newly measured
mainboard defect or an explanation proven for the P4 hang. No fix is included.

Broader shape/flood/path correctness, composition/Copper/cursor/hardware-sprite
interaction, worker/concurrency/output lifetime and target execution remain in
the integration/qualification contract. These 182 bounded checks do not replace
that work or establish improved gameplay/frame rate.

Repository checks: the artifact registry, manifest templates, VDP source
identity, R1 source/dependency hashes, document links and whitespace checks pass.
The combined version-validation command also checks the held r02 hardware
profile and stops on its existing `connectivity.yaml` digest mismatch. Both
hardware files are byte-identical to checkpoint `a773b19`; R1 does not change
that unrelated hardware record or claim the combined check passes.
