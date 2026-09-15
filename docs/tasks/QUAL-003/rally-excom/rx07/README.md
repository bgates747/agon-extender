# RX07 — Numeric conversion inventory

## Executive summary

The remaining conversions are **not another demonstrated ordinary Rally bug**.
The repaired negative fixed-point path is protected on P4. The audit finds five
additional exposed conversion families without complete range/nonfinite guards:
logical affine translation, transformed-bitmap bounds in two paths, transformed
pixel sampling, and bitmap byte-count calculation. These need Author disposition
before edits. Several compiler warnings are safe stock conversions and should
stay unchanged. Circle arithmetic and custom modeline parsing are separate
candidates, not proven P4 regressions.

RX07 is enumeration only. No firmware/game source was changed, built for
installation, flashed or benchmarked. RX08 is the required review stop. Recommended
scope: review N02–N06 for minimal P4 conversion guards, preserve ordinary stock
rounding/truncation, leave N07/N08 and dormant backend cases as separately
recorded follow-ups unless explicitly approved. Do not silently “improve” stock.

## Baseline and coverage

1. Source-selection authority: `docs/dependencies/generated/code-graph.yaml`
   and its `source-selection.yaml` projection, plus the narrower current
   `vdp/pio/p4-console-source-selection.json` and `vdp/pio/select_sources.py`.
   The declared profile selects 129 subjects. `declared-closure.json` records
   their current paths/hashes and lexical candidates. It is a search manifest,
   not a claim that all 129 files execute in the present image.
2. Actual installed-source baseline: audio-framing r21 candidate, app SHA256
   `394dceb0f40eb3f570f34624921c9f5cad731f4e24b3fbd2b17847d963c83f40`.
   Its 17 project translation units and 11 retained render-library units were
   syntax-checked with the P4 compiler. All 28 pass. All 16 focused source files
   in `source-identities.json` are byte-identical between installed source and
   current worktree. No assumption that the entire worktree equals that build.
3. Official reference: agon-vdp v2.16.0,
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, verified tagged/clean.
   Retained vdp-gl source lineage: all-the-plots,
   `ac2dd5986daf496c43ae8e7fe41836274aec54a0` (local port changes remain explicit).
   Official documentation checkout `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`:
   `docs/vdp/Buffered-Commands-API.md`, especially numeric formats, affine
   translation and commands 40/41. IEEE values are allowed; the documentation
   does not define a portable result for converting NaN/overflow to integers.
4. Methods: lexical scan of declared selected sources and project adapters;
   call/range inspection; `-Wfloat-conversion`; GCC original-tree
   `FIX_TRUNC_EXPR` enumeration, which also finds explicit casts and instantiated
   generic pixel code that warnings miss. `typed-conversions.json` retains
   function identities/counts and standard-library exclusions. Compiler node
   counts are not source-site counts. The 29 non-stdlib function identities
   include 15 instantiations of three pixel templates across five depths.
5. The syntax probe derives target definitions from the installed CMake
   compilation database, supplementing missing Arduino/vendor include paths,
   Arduino macros and the existing architecture header from the PIO setup.
   It is an analysis compile, not an exact production rebuild or a timing test.
   Earlier incomplete include setups were corrected before collecting results.
   Compiler commands, raw dumps and diagnostic logs remain ignored in
   `agents/rx07/`; compact normalized evidence is retained here.
6. Eight additional DSP matrix translation units pass the same warning/raw-tree
   inspection using their own CMake commands, including the installed `mat.cpp`
   lifetime derivative. Its one warning is double-to-float constant rounding,
   not float-to-integer conversion. The used matrix arithmetic produces floats;
   narrowing occurs at the inventoried VDP/renderer consumers.
7. This is a bounded port audit, not an audit of all ESP-IDF, Arduino, libc,
   libstdc++, networking libraries or every unlinked DSP/ML component. C++
   library conversion nodes are retained separately, not mislabelled as port
   defects. Classic peripheral backends excluded by the current profile are
   reviewed as dormant where the older declared profile selects them. No
   claim that text search or compiler warnings alone prove exhaustiveness.

## Findings requiring disposition

All locations below are relative to the repository; exact whole-file hashes
are in `source-identities.json`. N02–N06 are confirmed missing guards by source
inspection, **not measured stock/P4 pixel disagreements**. “Undefined” refers
to the C++ conversion domain, not a promised crash or a chosen device result.

| ID | Location / source lineage | Conversion and evidence | Proposed verification / disposition |
|---|---|---|---|
| N01 | `vdp/video/types.h:283` `convertFloatToValue`; stock v2.16.0 | Two explicit float→uint16/uint32 fixed encodings. Negative integral values outside the unsigned domain are unsafe. P4 command41 now routes fixed values through `encodeFixed`; its only remaining helper call is the nonfixed branch. | **Already remediated on active P4 path.** Retain regression/import gate; do not refactor the stock helper just because it remains present. High confidence, RX06 hardware evidence. |
| N02 | `vdp/video/vdu_buffered.h:1755` `bufferAffineTransform`, logical translation; stock | Two implicit float→int16 conversions entering `Context::scale`, before logical scaling. `readFloatArguments` rejects positive infinity as timeout but does not reject NaN, negative infinity or finite out-of-int16 inputs. Ordinary negative representable inputs are valid. | Test fractional truncation, ±32768 boundaries, NaN/±infinity and large finite values. Proposed P4 guard before the call, preserving truncation before scaling. High confidence. |
| N03 | `vdp/video/vdu_buffered.h:2132–2156` `bufferTransformBitmap`; stock | Sixteen float→int corner casts in resize/auto-translate path; a matrix buffer can contain arbitrary IEEE values. No finite/int32-range test before forming bounds. Negative in-range corners are not themselves wrong. | Test four corners, singular/nonfinite and huge transforms, resize/translation options. Proposed validate all results before allocation/destination publication. Do not assert stock output for undefined inputs. High confidence. |
| N04 | `vdp/vendor/vdp-gl/src/displaycontroller.cpp:1803–1828` `drawBitmapWithTransform`; all-the-plots | Same sixteen unguarded float→int corner casts in direct transformed plotting, before clipping. A screen clip does not make a preceding conversion valid. | All depths; identity/mirror/negative legal corners versus stock, invalid matrix must not modify framebuffer or strand matrix ownership. Proposed bounded P4 seam preserving valid stock output. High confidence. |
| N05 | `vdp/vendor/vdp-gl/src/displaycontroller.h:2822–2826,2859–2862,2895–2898` three `genericRawDrawTransformedBitmap_*` templates; all-the-plots | Six source-coordinate float→int casts (two per template). Negative/upper-bound rejection excludes infinities but **NaN passes every comparison** and reaches cast/pixel-address arithmetic. Instantiated for 2/4/8/16/64 colours. Output-loop x/y conversions are separately bounded. | Host sentinel buffers first; NaN in inverse matrix, infinities, valid clipped transforms and all three pixel formats/depths. Proposed finite/positive-range acceptance before sampling; no hardware malformed-pointer test before guard. High confidence. |
| N06 | `vdp/video/vdu_sprites.h:341` `createBitmapFromBuffer`; stock | Implicit double→uint32 for `ceil(width*bytesPerPixel)*height`. Unsigned16 dimensions with RGBA8888 can exceed UINT32_MAX (65535×65535×4 = 17179344900). Conversion occurs before stream-length mismatch rejection. | Boundary byte counts, zero/max dimensions, each format and short existing buffer; proposed checked count before narrowing. Distinguish this conversion from later allocation/size issues. High confidence. |
| N07 | `vdp/video/context/graphics.h:230–234` `plotCircle`; stock | sqrt result implicitly becomes int ellipse dimensions. Earlier signed integer squares/sum can overflow, yielding an invalid sqrt input before conversion. Ordinary bounded circles are fine; this is an inherited integer-arithmetic concern feeding a float cast. | Candidate: extreme signed coordinates and rectangular pixels in host analysis, safe circles against stock. **Record, do not fix opportunistically.** High confidence in source risk; no new device reproduction. |
| N08 | `vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp:289` `convertModelineToTimings`; all-the-plots | Parsed MHz float×1e6 implicitly becomes signed int frequency. A custom textual modeline can supply nonfinite/too-large values. Current mode tables use ordinary finite clocks; no current VDU custom-string path was established. | Candidate dormant/API-boundary risk, not evidence of a shipped mode failure. Review modeline caller admission before proposing change; table clocks should stay unchanged. Medium confidence in runtime relevance. |

## Reviewed conversions to preserve

| ID | Location / family | Range and conclusion | Suggested regression coverage |
|---|---|---|---|
| N09 | `context/viewport.h:42,170,171,174,184,194`, invScale/setLogicalCoords/scale/toCurrentCoordinates | Twelve implicit double→int argument conversions. With positive supported canvas dimensions and signed16 points, logical scale factors keep results inside int32. Subsequent Point int→int16 narrowing is a different operation. No new float-domain defect established. | Both coordinate modes, signed endpoints, smallest/largest supported resolution. Preserve existing truncation. |
| N10 | `displaycontroller.cpp:1388–1389`, fillEllipseSheared roundToInt | Signed16 size/shear bound normal results far inside int32; zero half-height exits first. Binary32 endpoint check over all 16383 positive representable half-heights found no reciprocal-multiply overshoot above1. This is not a full raster proof. | Degenerate/small/maximum legal ellipses, both shear signs. No rewrite proposed. |
| N11 | `displaycontroller.cpp:1621–1624`, pen offsets via lround | Four float-library→integer operations outside FIX_TRUNC_EXPR inventory. Sine/cosine bounded; pen width is bounded by API data. Preserve rounding, which differs intentionally from truncation. | Pen width extremes and all quadrants. |
| N12 | `dispdrivers/vgapalettedcontroller.cpp:269`, palette distance | double→int of squared RGB222 HSV differences: hue under360 and saturation/value within0..100; nonnegative total <149600, fits int32. Keep stock quantization/tie rules. | Enumerate palette colours/ties; no semantic improvement. Older excluded `palette_state.cpp:194` has the equivalent bounded conversion. |
| N13 | `vdu_buffered.h:2196`, bufferTransformBitmap sample lookup | Two float→int source coordinates are inside a **positive conjunction**: >=0 and <bitmap dimensions. Unlike N05, NaN fails admission. Safe for positive valid bitmap sizes. | NaN must leave transparent pixel, valid edge sampling unchanged. |
| N14 | `displaycontroller.h` transformed template output x/y | Float loop variables originate from signed16 Rect bounds and stay there; conversion before adding destination position is representable. Retain; distinguish from unsafe inverse-matrix source coordinates N05. | Clipped signed-coordinate rectangles. |
| N15 | `extender/port/fixed_conversion.hpp:22`, encodeFixed | Finite check, truncation, exclusive signed upper bound, then signed→unsigned integer encoding. Existing accepted repair is the intended pattern. | Existing 65,764-check suite and RX06 physical regression. |
| N16 | types.h half/single conversion and bit reinterpretation; DSP matrix arithmetic | Float bit storage/reinterpretation and integer exponent operations are not numeric float→integer casts. Matrix operations retain floating values; double→float constants are not this defect class. | Keep separately scoped aliasing/DSP lifetime issues out of this audit. |

## Declared but currently dormant source

| ID | Family | Enumeration / current disposition |
|---|---|---|
| N17 | `video/enhanced_samples_generator.h:73,86`, sample interpolation/duration | Two implicit double→int conversions. Interpolation is bounded if finite fraction remains0..1 and samples remain bounded. Duration division can exceed int range or encounter invalid rate state. Audio backend is excluded from r21; its no-op adapter contains no floating conversions. Review rate/duration admission before eventual synthesis port; no present renderer fix. |
| N18 | `vendor/vdp-gl/src/fabutils.cpp:1584,1739,1751,1814,1819,1843` | floatToFraction double→int64; APLL startSDM1/sdm0 double→int; I2S N/b/return double→int. Caller/rate bounds and zero rates matter. Classic APLL/I2S helpers are not in extracted `stock_render_utils.cpp`; do not restore these backends just to audit them. Record candidates for any future port. |
| N19 | `vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp:870,873` | Classic timeout double ceil→integer conversions occur in the classic primitive-budget calculation block excluded from P4 stock-runtime compilation. Rate/divisor assumptions need review if ever selected. No P4 game impact established. |

The declared profile's CRC version strings/format text triggered lexical search
but no numeric cast; ESP32Time and selected CRC arithmetic do not add this
hazard. Terminal serial stop-bit handling compares floats, not numeric casts.
Dormant sound-generator/stream files pass rates into the separately listed
clock helpers. Old custom display backend and palette implementation remain
explicitly excluded by the current source selection; do not treat their presence
as proof that they execute. Firmware-support libraries outside the port closure
are a stated boundary, not certified bug-free.

## Source-selection bookkeeping finding

The graph's declared P4 profile describes an earlier Phase F selection, while
current console uses retained stock depth controllers. The current selection
JSON still lists `video/vdu_audio.h` among exclusions although r21 deliberately
includes its stock dispatcher through `vdu.h`. The compiler walk observes the
actual selected body. Record this drift for RX11/command-audit reconciliation;
do not silently regenerate or change source-selection contracts during RX07.

## Review decision and next work

1. Author disposition of N02–N06 is required before RX09 changes. Proposed
   approach is minimal P4 conversion guards, retaining stock results for valid
   representable inputs and rejecting/skipping unsupported invalid data before
   framebuffer writes or destination replacement. Exact failure/consumption and
   resource-ownership behavior must be frozen per command before implementation.
2. Keep N07/N08/N17–N19 documented as inherited or dormant candidates, unless
   explicitly added to the approved scope. Ordinary signed truncation, palette
   ties, lround and the safe positive bounds checks must remain unchanged.
3. Then deterministic comparisons against stock for defined valid inputs, plus
   host safety/sentinel checks for invalid inputs with no portable stock oracle.
   Preserve official source checkouts; no broad upstream bug-fix campaign.
4. Unsupported-command UC01–UC07 remains next; audio-first acceptance does not
   close that inventory. Game benchmarking stays behind both audit phases.


## Reproduction

`replay_syntax.py` accepts an ignored local target-command JSON, the identified
source root and build working directory. It refuses object/dependency-output
flags and writes only into a newly created output directory. Example:

```sh
.venv/bin/python docs/tasks/QUAL-003/rally-excom/rx07/replay_syntax.py \
  --source-root "$AUDIT_SOURCE_ROOT" --command-json "$AUDIT_COMMAND_JSON" \
  --cwd "$AUDIT_BUILD_ROOT" --output "$AUDIT_OUTPUT"
```

The current local seed is `agents/rx07/parser-command.json`; remove any existing
`-fdump-*` option before replay. Raw compiler trees are deliberately ignored:
they contain system paths, expanded library code and redundant template nodes.
The checked-in summary, input hashes, source locations and methods are the
review record. This tool supplements manual range/call inspection; it does not
automatically classify hazards or replace the reusable RX11 import gate.


## Hardware notification and stop

The established hardware voice player replaced a fresh pending receipt with
`audio_commands=pass`; original autoexec was read back unchanged. Rally was
exited for the spoken cue and the bench is at the Legacy MOS prompt. No
firmware changed. Human hearing and RX08 finding dispositions remain pending.
See notification.json. Stop here; do not start RX09 or game benchmarks.
