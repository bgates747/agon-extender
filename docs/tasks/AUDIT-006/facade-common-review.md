# AUDIT-006 W6 — Official facade and common renderer

Source review against Extender `047ffe8`, official VDP v2.16.0
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, and vdp-gl
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`. Proposed dispositions, not
implementation or hardware qualification. The linked source paths are bound
to these revisions by [video-source-baseline.json](video-source-baseline.json).

## Documentation and selected implementation

The official [VDU reference](../../../../../agon-docs/docs/vdp/VDU-Commands.md)
defines text/graphics cursors, viewport clear and scroll, paint modes, mode
selection and inclusive graphics clipping. The official
[screen-mode reference](../../../../../agon-docs/docs/vdp/Screen-Modes.md)
defines drawing/visible buffer semantics. These are the externally observable
contracts; source is needed to establish native storage and execution.

The current [console selection](../../../vdp/pio/p4-console-source-selection.json)
contains 21 project translation units and three vdp-gl translation units:
`canvas.cpp`, `codepages.cpp`, `displaycontroller.cpp`. Concrete depth sources
present in the vendor tree are **not selected**. The generated application
CMake list matches the manifest; `pio/select_sources.py` separately selects
the three vendored units using `BuildSources`. A CMake compilation database
alone is therefore insufficient to establish the whole closure.

`p4_console.cpp` defines console and processed-keyboard selection and includes
`p4_browser_vdp.cpp`; that bridge defines the P4 target and includes
`video.ino`. The actual path is `runConsole(processor)`, not the unmodified
stock `processLoop` body below its conditional early return. This distinction
matters for timing and keyboard ownership. Historical disconnected, keyboard
probe and browser-typing branches are not the selected console.

The read-only verifier checks 57 selected/interface files against the frozen
checkpoint, compares all 47 official video source/header files (32 exact,
15 differing), and compares 22 library files (all exact). A complete diff of
the 15 official differences was inspected. Most insert conditional includes;
the material selected replacements are screen/controller binding, boot and
stream ownership, input binding, disabled audio/maintenance/Terminal paths and
the explicit console control opcode. Byte identity establishes provenance,
not equivalence of the lower-level implementations supplied to those files.

## Coverage and dispositions

Source paths below are relative to `vdp/video` for VDP and
`vdp/vendor/vdp-gl/src` for GL. The upstream counterparts use the same relative
paths at the pinned commits. **Retain** means keep the exact upstream body;
**restore** means remove an unnecessary replacement; **adapt** is limited to
the named target/output dependency.

| Region / exact source anchors | Selected P4 implementation and difference | Dependency evidence and disposition |
| --- | --- | --- |
| Mode command: VDP `vdu.h:305`, `VDUStreamProcessor::vdu_mode`; screen table `agon_screen.h:284`, `changeMode` | Bodies retained: clear/wait, requested→previous→mode 1 fallback, context reset, double-buffer initialization, cursor restoration, mode callbacks. | No processor-specific algorithm here. **Retain**. Changed controller construction and failure handling underneath remain subject to review. |
| Mode reply: VDP `vdu_sys.h:565`, `sendModeInformation` | Exact eight-byte dimensions/viewport character dimensions/depth/mode payload and callback ordering; console transport supplies `send_packet`. | GPIO/UART ownership is a separate transport adaptation. **Retain** the reply body. No new mode-reply protocol is needed for restoration. |
| Concrete mode factory: stock `agon_screen.h:38`, `getVGAController`, and `:186`, `updateVGAController`; P4 `agon_screen.h:59`, `:201` | Five stock classes replaced by one stable `P4DisplayController`; colour-depth validation no longer selects a concrete renderer. | Stock GPIO binding cannot run on P4, but this does not require losing concrete render methods. **Restore** the depth-specific family through a narrowly adapted lifecycle. See storage review. |
| Resolution/timing: stock GL `vgabasecontroller.cpp:243`, `convertModelineToTimings`, `:376`, `setResolution`; P4 `screen_facade_adapter.cpp:12`, `parseOfficialModeline`, `:65`, `configure` | P4 reads logical width/height and integer refresh from the label, allocates new planes, stops/restarts a software frame service; it ignores physical timings/porches/scan multiplier and does local rollback. | No VGA signal requires no porch/DMA buffers. That justifies output adaptation, not redefining native storage. Nominal label cadence is not identical to stock pixel-clock-derived cadence (e.g. 25.175 MHz / 800 / 525 ≈59.94 Hz). Keep this difference explicit; no claim of exact physical VSYNC parity. Review original parser reuse and P4 clock policy in the output binding. |
| Screen dimensions/scaling: VDP `agon_screen.h:260–275`; `context/viewport.h`, `scale`, `toScreenCoordinates`, `setGraphicsViewport`, `setOrigin` | Official logical scaling, rectangular-pixel choice, viewport bounds and origins retained; context file changes only imports. | **Retain**. Stock allocation can reduce viewport height; P4 transactional allocation instead fails before committing, then official fallback runs. Preserve observable fallback while reviewing singleton/static row ownership. |
| Commands/state: VDP `vdu.h`, `vdu_context.h`, `vdu_buffered.h`, `vdu_fonts.h`, `vdu_layers.h`, `context.h`, `buffers.h` | VDU dispatch and graphics-context/buffer/font/layer algorithms retained; conditional imports connect selected target dependencies. | **Retain** algorithms and buffer callback order. No justification to replace these to repair pixel access. Audio, Terminal and maintenance exclusions are explicit incomplete features, not missing generic drawing primitives. |
| Text/glyphs: VDP `context/graphics.h:800`, `plotString`; `context/cursor.h`, `context/fonts.h`, `agon_fonts.h`; GL `canvas.cpp:442`, `drawGlyph`, `:497`, `drawChar` | Official cursor positioning, font selection, character-to-glyph submission and text scrolling retained. `agon_fonts.h` changes include placement; context changes include compatibility declarations. Lower raw glyph writes use the replacement controller. | **Retain** upstream text/cursor/font algorithms. Restore concrete raw glyph/paint implementations underneath; text latency is not proof the text parser needs rewriting. |
| Geometry/flood/path: GL `displaycontroller.cpp:792`, `execPrimitive`; `:1068`, `floodFillFromPos`; `:1247`, `fillEllipse`; `:1310/1321`, sheared ellipses; `:1449/1498`, draw/fill path | Exact common algorithms and dispatch remain linked. They call virtual row/pixel functions in P4 instead of the selected stock depth class. | **Retain** common algorithms. A matching primitive list cannot prove matching cost: row fill/copy/paint helpers differ. No geometry rewrite proposed. |
| Bitmaps/transforms: GL `displaycontroller.cpp:1616`, `drawBitmap`; `:1626`, `absDrawBitmap`; `:1749`, `drawBitmapWithTransform`; `:1827–1839`, format dispatch | Exact clipping and transformed inverse-matrix logic remain. Concrete callbacks for Mask/RGBA2222/RGBA8888/native access differ. Native transformed path is commented out upstream too. | **Retain** shared logic; restore concrete depth writers. Do not label an inherited absence a new P4 regression. One-scanline clipping is already computed before pixel iteration; verify edge behavior rather than inventing new clipping. |
| Teletext: VDP `agon_screen.h:325`, mode 7; entire `agon_ttxt.h` | File byte-identical: 40×25 character/attribute buffer, double-height/flash/mosaic interpretation, glyph output, viewport text-buffer shifts and repaint. Mode 7 still initializes the 16-colour 640×480 controller. | **Retain**. Teletext intentionally retains its own text buffer/repaint algorithm; do not replace it with the ordinary bitmap-scroll fast path. Its flashing ultimately depends on the changed frame service. |
| VSYNC/user callbacks: VDP `vdu_stream_processor.h:601`, `processNext`; `context.h:1316`, `checkForVSYNC`; buffers callback machinery | Official callback bodies retained; the counter they observe now comes from the serialized P4 frame worker. | **Restore** independent frame progression beneath retained code. Do not claim a stock buffer callback signals browser presentation or arbitrary completion. Frame review covers exact scheduling. |
| Utilities: GL `fabutils.cpp`, selected P4 `extender/port/fabutils_port.cpp` | `isqrt`, clip-line, rectangle helpers, quadrant tests and light memory pool extracted but reformatted/renamed; clip-line and pool branches restructured. Same algorithms by inspection, not byte-identical source. Full stock utility TU also imports classic peripheral code. | Excluding that broad TU is justified by physical dependencies. Rewriting portable bodies is not. **Restore** verbatim source spans in the narrow utility closure when touching this binding; retain provenance/licensing. No measured speed difference assigned to these cosmetic/control-flow changes. |
| Includes/platform glue: `extender/compat/p4_vdp_gl.hpp`, sketch bridge, target architecture headers | Narrow aggregate includes and generated Arduino prototypes avoid importing unavailable physical subsystems; Xtensa helpers need actual RISC-V treatment. | **Adapt** only missing compiler/SDK/peripheral interfaces. Do not move retained floating-point primitives into ISR code using no-op compatibility helpers. See frame review. |

## Additional findings

**FC-01 — The facade factory is broader than an output replacement.**
The old Phase E statement that a single narrow screen patch preserves the
screen facade is true at the command boundary, but does not justify replacing
all five concrete controllers. Its compatibility document is historical
evidence of the old design, not an exemption from the fidelity requirement.

**FC-02 — Nominal frame cadence and physical scan timing differ.**
Logical dimensions in the selected official mode table remain available, but
P4's label parser is not the stock full modeline parser. The output binding
must explicitly distinguish logical refresh, duplicated scanlines/blanking,
and the mainboard-generated interrupt still driving eZ80 timing. This review
does not attribute multi-second hangs to a small nominal refresh difference.

**FC-03 — Extracted portable utilities need accurate provenance language.**
Their current header says they preserve implementations; algorithmic retention
is not exact textual reuse. Restore exact portable spans instead of defending
unnecessary re-expression. No wholesale `fabutils.cpp` inclusion is proposed.

The preferred repair retains official mode/command/text/Teletext/common drawing
code and reconnects it to stock concrete depth implementations. It does not
replace already working upper layers or revive deferred audio/Terminal/input
features. The integrated audit owns stable finding IDs and implementation
priorities.
