# SRLE2 browser tasklet — unexpected stop

## Executive summary

**Stopped on the first golden round-trip mismatch, as directed.** A64-colour
fixture contains78 RLE2 bytes; the Linux szip decoder produced156 bytes. The first
78 match the expected data, but trailing bytes make the decode invalid. No browser
implementation or performance test has run. The occupied bench was untouched.

## Finding

The original sz_unsrt function explicitly writes output with `putc(..., stdout)`
when its output pointer is NULL. The commented `fwrite` in the caller was therefore
intentional for that path, not an omitted output operation. Our earlier port and
this corpus generator incorrectly reinstated it. The original unsorter outputs
correct bytes first; the extra write appends its working buffer.

The P4 shim has a second aspect of the same incomplete I/O adaptation: io.h
redirects putchar/fwrite but not putc. Thus its native C output path is not fully
redirected to bounded memory. The exact P4 symptom is untested; do not infer that
it will reproduce the Linux156-byte result. The compiled candidate must not be
flashed until this is corrected and independently validated.

## Next decision

Resume with a bounded correction: remove the added write, route every original
codec I/O primitive (including putc) into the memory shim, inventory remaining
stdio uses, then repeat the independent golden controls before WebAssembly work.
No correction was made after this unexpected stop; evidence and the failing
reproducer are retained. W01 remains incomplete; W02–W08 are not completed.

Official Emscripten SDK4.0.23 was installed in ignored task-local storage using
the official emsdk workflow (https://emscripten.org/docs/getting_started/downloads.html).
No shell startup files or system packages were changed. Installation is preparation,
not browser validation. SDK commit is recorded in TOOLING.json.
