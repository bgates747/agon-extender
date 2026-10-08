# Full-width 480-line review pattern

This ordinary MOS program draws the full experimental848×480 mode96, including
outer edges, eight labeled color bars, a circle/square and guides marking the
centered640-pixel area. It reuses the LCD color-bars wrapper and drawing idioms.
It selects no mode, changes no files, and waits for Escape before returning.

Generate `pattern.vdu` with the project Python, supplying `--build-id` and
`--output`. Assemble a copied `pattern.asm` beside that payload using the pinned
ez80asm. Retain source/payload/binary hashes in the build manifest. The deployed
path belongs under `/extender`; test results and startup backups belong under
`/agents/extender`. Startup must enable admitted Extender input, select ExCom,
issue `VDU 22 96`, and only then load/run the program. Stock VDP does not support
this provisional mode ID. Original startup must be preserved and restored.

See [HDMI-002](../../../docs/tasks/HDMI-002.md), W01–W03, for the active contract.
The separate moving-sprite checks reuse the resident render-load-r04 executable
with parameterized848×480 data; this static pattern is not a throughput test.
