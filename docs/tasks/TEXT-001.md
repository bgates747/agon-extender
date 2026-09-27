# TEXT-001 — Transparent text backgrounds at the text cursor

## Executive summary

Feasible without a new glyph renderer. Stock VDP already controls glyph background
painting with `GlyphOptions::FillBackground`; cursor selection forces it on for
text and off for graphics. EDP retains that path. Recommend an explicit per-context
text-transparency flag, leaving colour numbers and ordinary PRINT byte streams
unchanged. Investigation complete; the Author approved the first-pass separate flag with
normal destructive erase/scroll behaviour. Command allocation and the detailed
implementation contract remain before implementation. No firmware or bench changes in this task pass.

## Contract and bounded checklist

Author requested investigation and scoping, not firmware implementation.

T01-01 [x] Read official text/colour/cursor contracts and identify stock draw path.
T01-02 [x] Compare EDP path; identify reset/context/font, erase, scrolling, cursor
and readback implications. Distinguish source findings from runtime proof.
T01-03 [x] Recommend a minimal interface and enumerate approval choices and tests.
T01-04 [x] Author reviews scope and selects behaviour; allocate command only after
checking the applicable command namespace. Implementation needs its own frozen
contract, version identities and qualification. No numeric opcode reserved here.

## Source basis and provenance

Read-only official VDP checkout is clean at its newest locally available tag
v2.16.0, commit `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. This is the retained
reference, not a claim of a fresh remote-release check. Official docs inspected
at `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`; no upstream checkout changed.

| Evidence | Relevant contract/finding |
|---|---|
| [Official VDU documentation](https://github.com/AgonConsole8/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDU-Commands.md) | VDU 4 uses text foreground/background; VDU 5 is transparent except destructive VDU 127. VDU 17 assigns all byte values to foreground/background palette selection, wrapping colours. |
| Official `video/context/cursor.h`, `Context::setActiveCursor` | Text selects `setCharacterOverwrite(true)`; graphics selects false. Cursor flash changes cursor sprite visibility. |
| Official `video/context/fonts.h` | Overwrite sets `GlyphOptions().FillBackground(overwrite)`; `resetFonts` restores true. `getScreenChar` classifies pixels against tbg and matches glyph bitmaps. |
| Official `video/context/graphics.h` | `plotString` uses text viewport/tfg/tbg/tpo or graphics viewport/gfg/gpofg; draws glyphs or mapped bitmap characters. Backspace erasure explicitly fills a rectangle. Scrolling moves the viewport pixels using tbg for fill. |
| Official `video/context.h` | Context copying includes colour/paint state; any new flag needs explicit copy/reset semantics. |
| Maintained EDP `vdp/video/context/{cursor,fonts,graphics}.h` | Same relevant glyph-background mechanism; existing project differences must be preserved. |
| EDP `vdp/video/extender/display/p4_display_controller.cpp`, `drawGlyph` | Passes options through to inherited `genericDrawGlyph`. |
| Vendored `vdp/vendor/vdp-gl/src/displaycontroller.h`, `genericDrawGlyph` | Background pixels painted conditionally on `fillBackground`. No new pixel format/alpha plane required. |

Official source paths above are relative to the pinned VDP repository
[tree](https://github.com/AgonConsole8/agon-vdp/tree/c7ac293d2aa81ddfa693390549bcd909069c8fc3).
Local maintained paths are relative to this repository. Source inspection only;
no runtime transparency experiment performed.

## Proposed first implementation scope

D01 — First-pass direction approved by the Author: add an explicit text-background
painting option, separate from VDU 17 colour selection. Do not reinterpret a
palette alias as transparent; that would change valid existing programs. A
VDU extension controls the option; ordinary MOS output, BASIC PRINT and C printf
continue sending the same characters. No EMOS parser/output rewrite is needed.
VDU transport remains owned by EMOS. Legacy requires matching mainboard VDP
support; implementing it only in EDP would not add the feature to stock mainboard.

D02 — Recommendation awaiting approval: ordinary glyph plotting only. Default
opaque; selecting text cursor respects the flag, graphics cursor stays transparent.
Mode/context reset restores opaque; context save/copy/restore preserves the flag
until reset. Font changes must not accidentally re-enable fill. VDU 17 continues
to set the stored colour used by explicit clears and erases regardless of flag.

D03 — Approved by the Author for the first pass: preserve existing destructive operations.
VDU 8 moves the cursor; VDU 127 deletes with background fill; CLS fills the text
viewport; scrolling moves all its pixels and fills exposed space. Printing a
space in transparent mode paints nothing; overprinting does not remove old ink.
This is transparent glyph plotting, not a separately composited text layer or
restoration of graphics hidden under old letters. Applications wanting stable
backgrounds should avoid scroll or redraw their own backgrounds.

D04 — Recommendation awaiting approval: exclude teletext from the first extension
(document an ignored option there); preserve mapped bitmap characters' existing
pixel transparency rather than inventing glyph-fill semantics for them. Text
cursor remains the existing sprite. Verify flashing over graphics but do not
introduce a cursor backing-store design absent a demonstrated need.

## Implementation touch points and risks

1. VDP owns command parsing, per-context flag, copy/reset and canvas activation.
   Apply the flag through the existing overwrite helper whenever text state is
   activated; inspect global canvas state when switching contexts and VDU 4/5.
2. EDP uses the corresponding maintained context code and the existing generic
   glyph renderer. Keep a minimal mainboard-compatible patch, not a new renderer.
3. Screen-character recognition is not guaranteed over arbitrary graphics:
   stock readback compares pixels against tbg. Transparency can defeat matching.
   Do not claim a text-buffer/readback guarantee or add a shadow buffer in scope.
   Review Extender screen-text endpoint behaviour separately in implementation.
4. A clean no-background glyph may do fewer writes, but no speed claim follows
   without measurement. Rendering remains destructive foreground painting, with
   no extra frame history, alpha framebuffer or double buffering introduced.
5. Existing text paint modes, clipping, custom fonts and bitmap-character mappings
   need tests; the one-line helper change alone is not a complete feature.

## Proposed qualification (not executed)

| Case | Expected result under recommended scope |
|---|---|
| Default PRINT and all VDU 17 colour aliases | Existing opaque behaviour unchanged |
| Pattern background, transparent letters and spaces | Only glyph foreground pixels change |
| Repeated different letters in same cell | Old ink persists where not overwritten |
| VDU 8 / VDU 127 / CLS | Move / background erase / background clear respectively |
| Wrap and scroll inside text viewport | Stock scrolling and exposed-area fill retained |
| VDU 4/5 transitions, fonts, context copy/activation, mode reset | Flag preserved/reset as specified, no canvas-state leakage |
| Cursor flash, single/double buffering, supported palette depths | Underlying pixels stable when cursor hides; matching semantics |
| Mapped bitmap characters and teletext | Existing behaviour; exclusions explicit |
| Screen-character query over graphics | Limitation documented, no fabricated recognition guarantee |

Compare mainboard and EDP against a deterministic patterned background and pixel
expectations; retain human visual review where capture changes behaviour. Fixtures
select mode in autoexec before invocation. Source implementation and testing await
scope approval; no upstream publication is authorized by this research task.

## Author review

The Author approved transparent printing with normal destructive erase and
scrolling for a first pass. This accepts D01/D03 direction; detailed reset,
context and special-mode semantics remain recommendations to settle in the
implementation contract. No command number or firmware identity assigned.

## Implementation contract — Author authorized

T01-05 [x] Implement per-context transparent text flag in maintained EDP context
code and apply the same bounded patch to an isolated Fab native VDP source copy.
Use experimental VDP variable 0x10F1 (unassigned in the inspected reference),
value 0 opaque / 1 transparent, other values ignored. This is a private prototype
allocation, not an upstream assignment. Use the existing VDU 23,0,F8 word/word
parser and read-variable path. Teletext ignores writes. Preserve colour/erase/
scroll semantics; copy flag with context, clear on context/mode reset, restore
on context activation and VDU 4. No EMOS change or physical firmware deployment.

T01-06 [x] Build bespoke native VDP on Linux using existing emulator build inputs;
reuse the unchanged emulator executable on Lenovo. Verify actual pixel differences
against opaque glyph output and a patterned background, plus toggle/reset cases.
Compile maintained P4 code. Keep all emulator-coupled changes uncommitted until
Author visual acceptance.

T01-07 [x] Install isolated project `.emulator/text-001` profile on Lenovo with
verified stock MOS and bespoke VDP; demo executable uses ordinary text cursor
printing over rainbow stripes. Video mode selected by autoexec before running.
Leave the everyday profile unchanged. Launch only when ready for visual review.


## Prototype result — visual acceptance pending

Native pixel checks pass: opaque-derived glyph mask over a coloured background,
transparent spaces, opaque restoration, VDU 4/5 and saved-context restoration,
destructive delete and full context reset. P4 console compile/link passes in
29.37 seconds; no P4 deployment performed. The native module uses Fab's retained
2.16.0 userspace-adapted source, commit
`1056ee38ec1cc68ed327bd32ee47d04b1c30597c`, not a claim of stock physical VDP proof.
The same bounded modifications are in maintained EDP context sources.

Reproduction helpers live alongside this document: `build_native.py`,
`apply-native-prototype.py`, `make_demo.py`, `check_pixels.py`. Build receipt,
module, native pixel result and screenshots are retained in ignored local task
evidence. The Lenovo profile uses stock MOS 3.0.2, the unchanged installed Fab
executable, and this bespoke VDP; everyday emulator untouched. Local deployment
paths are recorded in the ignored receipt. Mode 0 is selected by autoexec.

The visual fixture uses the stock buffered-command API to submit its VDU 4 text
and graphics together: the retained native emulator loses some glyph rendering
when its UART delivers separate text fragments (also observed by the prior console
review harness). A paced direct stream did not remedy it. This is a demo delivery
workaround, not a P4 fix or a throughput claim. Native pixel tests separately
exercise the direct text stream and feature state.

Set transparency: byte sequence `23,0,248,241,16,1,0`; disable with final word
`0,0`. These use the existing set-variable protocol and private variable 0x10F1.
Full reset clears it; font-only reset preserves it. Partial text-colour reset
retains the flag in this prototype. Teletext ignores writes. Clear-variable does
not clear VDU state: explicitly set zero, as with other VDU variables.
Changes remain uncommitted pending Author emulator validation.


Final Lenovo window capture verifies the full labelled rainbow demonstration,
including opaque and transparent ordinary text, visible spaces and exit guidance.
Author clarified that earlier window exits were manual, not emulator crashes.
The final buffered workload renders all labels; direct native pixel validation
remains separately retained. Visual acceptance still belongs to the Author.

## Author-requested sharing package

Built a flashable classic ESP32 mainboard VDP application image from a separate
copy of official v2.16.0 plus the same context patch and a TEXT001 prototype build
label. PlatformIO espressif32 6.6.0 build passes (13.16 seconds); no flashing done.
Retained stock dependency vdp-gl commit ac2dd5986daf496c43ae8e7fe41836274aec54a0.
Discord sharing archive contains application firmware (not an emulator module),
stock-relative patch, Agon demo source/binary, exact build sources/dependencies,
licenses, README and checksums. Dependency examples/generated docs omitted; build
sources retained. Archive copied to the Author's Lenovo desktop and SHA verified.
Private location and package bytes remain in local task evidence. Mainboard
physical qualification and Author emulator acceptance remain separate gates.
