# TEXT-001 — Transparent text backgrounds at the text cursor

## Executive summary

Feasible without a new glyph renderer. Stock VDP already controls glyph background
painting with `GlyphOptions::FillBackground`; cursor selection forces it on for
text and off for graphics. EDP retains that path. Recommend an explicit per-context
text-transparency flag, leaving colour numbers and ordinary PRINT byte streams
unchanged. Investigation complete; command allocation and behaviour approval are
required before implementation. No firmware or bench changes in this task pass.

## Contract and bounded checklist

Author requested investigation and scoping, not firmware implementation.

T01-01 [x] Read official text/colour/cursor contracts and identify stock draw path.
T01-02 [x] Compare EDP path; identify reset/context/font, erase, scrolling, cursor
and readback implications. Distinguish source findings from runtime proof.
T01-03 [x] Recommend a minimal interface and enumerate approval choices and tests.
T01-04 [ ] Author reviews scope and selects behaviour; allocate command only after
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

D01 — Recommendation awaiting Author approval: add an explicit text-background
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

D03 — Recommendation awaiting approval: preserve existing destructive operations.
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
