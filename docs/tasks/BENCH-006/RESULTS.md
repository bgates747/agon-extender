# BENCH-006 results

## Executive summary

Direct ExCom screen text works on hardware. A full 80×60-cell capture took
2.20 seconds and contained both an injected ECHO command and its executed output.
The helper uses HTTP only: no video viewer takeover, eZ80 helper load or SD service.
The bench is left at the ExCom MOS prompt for the Author and Alex.

## Evidence

- Firmware identity/hashes: BUILD.json; flash independently verified.
- Sanitized host capture tests passed: request/completion, changed dimensions,
  unsupported dimensions and maximum supported cell count.
- Physical output contained `Alex screen readback works` on its own line after
  the command line. Private capture/result: agents/screen-text/marker-0.txt and
  result.json. Timing is one observed capture, not a throughput benchmark.
- Existing app.js, frame_protocol.js, index.html and style.css match the prior
  installed candidate byte-for-byte. No WebSocket was opened by this test.
- Installation rebooted P4 and mainboard; the subsequent read itself performs
  neither action. Mainboard firmware and SD startup were not modified.
- Alex read-screen.md now invokes the direct helper. README/NOTES/gitignore
  were not touched. No Alex prompt was submitted.

## Limitations and corrections

Retained glyph recognition is font/colour dependent and excludes some edge cells.
Non-ASCII/unrecognised cells return `?`. Samples span time while ordinary processing
continues; they are not a coherent instantaneous screenshot. Context/dimension
change returns 409. One reader uses the shared pending capture at a time.
Legacy requires its own follow-up; this endpoint sees the P4 display only.

Two integration corrections preceded acceptance: the installed candidate already
had an extra codec route, requiring one more HTTP handler slot than the maintained
base; and ExCom dispatches through runConsole rather than the generic processLoop.
The first caused startup failure; the second produced a bounded capture timeout.
The accepted image has the correct slot count and console-owner capture hook.
Prior pair-RLE rollback artifacts remain preserved.
