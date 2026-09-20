# Static Mode7 teletext qualification

## Executive summary

Author authorized Mode7 comparison. Reuse the existing mainboard all-depth
capture diagnostic and scene player; add teletext-static-probe-r01 under standing
identity approval (registry r94). No product firmware changes. One static page
covers text/colours, contiguous/separated mosaics, held graphics, backgrounds,
double height and conceal. Flash timing, scrolling and exhaustive teletext parity
remain outside this bounded run.

**QUAL-004-TT01** [x] Freeze generator, scene, manifest and this contract before
bench mutation. Preserve actual mainboard flash/startup, verify retained player
and deployed scene/sidecar hashes. P4/EMOS remain unchanged.

**QUAL-004-TT02** [x] Temporarily install/verify existing diagnostic. Startup alone
selects mode7 on both routes. Two fresh-reset mainboard captures and two distinct
matching P4 generations; compare all 640×480 pixels without tolerance or cropping.
Independently check a fully filled contiguous white mosaic cell, separation gaps
in the adjacent separated example, nonempty coloured text and both double-height
halves. Record actual dimensions. Stop/restore on unexpected reset or incomplete
capture; no renderer repairs or fixture changes to manufacture a pass.

**QUAL-004-TT03** [x] Restore exact original startup/mainboard overwritten sectors,
verify, close serial/video observers, release keyboard and SD service, verify MOS
prompt. Retain evidence and acquisition duration separately from rendering time.
Report mismatches and coverage limits. No emulator/voice cue or push requested.

## Bounded source research

Official docs at `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` identify mode7 as
BBC-style teletext with 16 colours. Stock v2.16.0 at
`c7ac293d2aa81ddfa693390549bcd909069c8fc3` is clean/read-only.
[Screen modes](https://github.com/AgonConsole8/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Screen-Modes.md)
provide mode semantics; implementation detail comes from stock `video/agon_screen.h`
(case7: VGA16, 640×480), `video/agon_ttxt.h` (40×25 cells, 16×19 at this height,
high-bit control aliases, mosaic and double-height fonts), and
`video/context/graphics.h` (text dispatch to draw_char). Retained P4 sources use
that teletext path. Existing VGA16 capture taps expanded composed visible rows.
The five unused bottom raster rows remain part of full-image comparison.

Flashing is excluded because serial acquisition samples rows over time. Text
controls are emitted with bit7 set so they reach teletext processing rather
than execute as ordinary VDU controls. Double-height text is supplied on both
rows, as stock retains a separate character buffer for each row. These are
fixture choices, not changes to upstream semantics.
