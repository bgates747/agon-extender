# Vendored Nurples assembly APIs

These 14 `.inc` files are unchanged copies from `src/asm/` in
`https://github.com/bgates747/nurples.git`, commit
`1b2b488046eff27aabfc41c55d4276a509ecd602` on `dev`, imported on 2026-09-08.
Every imported file matched that commit even though the source checkout had
unrelated local changes. `manifest.json` records the source path and SHA-256
of each include and the copied root `LICENSE`. Original attribution and
source-reference comments are preserved.

The imported set contains MOS definitions, macros, text and number output,
arithmetic and fixed-point helpers, file-buffer storage, timers, and the VDU
text/bitmap, buffered-command, font, PLOT, sprite, and sound APIs.

The reusable bitmap path is `vdu_load_img` / `vdu_load_buffer_from_file` in
`vdu.inc`, with bitmap selection and `vdu_plot_bmp` for display. The sample
path is `vdu_load_sfx` / `vdu_play_sample` in `vdu_sound.inc`. File loading
uses the inherited 8 KiB scratch region at `0xB7E000`, defined in `files.inc`.

Nurples' `images.inc` and `vdu_sfx.inc` contain application loading screens
and game dependencies. `fonts.inc` loads its generated application font
table. Those application wrappers and their asset lists are excluded; the
underlying VDU loading, drawing, font, and sound routines are included.

This is a source snapshot, not a claim of runtime qualification. The imported
code retains packed ADL stores, incomplete buffered-command wrappers, and
direct timer/interrupt setup helpers. See the project development log for
the bounded review. Hello World calls only the imported string-output path.
