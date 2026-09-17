# SRLE2 P4 iteration — compile-only contract

## Executive summary

Author authorizes original-source szip on P4 plus EDP wrappers under P01h.
Bench belongs to another agent: no flash, serial/network bench access, resets,
emulators, codec execution or runtime tests until explicit release. Compile only.

1. [x] Pin original szip source and historical mainboard contracts/license notices.
2. [x] Port C codec through bounded memory I/O, checked PSRAM allocation, recoverable
   errors and serialized access; preserve order3, recordsize1 entropy format.
3. [x] Add SRLE2 encode/decode APIs and command65 single-layer CmpS decoding.
   Keep TVC and RLE2 paths. Two command65 calls decode SRLE2 then create bitmap.
4. [x] Compile an isolated P4 candidate; record hashes, compiler diagnostics,
   limitations and pending tests. No runtime or hardware validation claim.

Historical decoder/caller: personal agon-vdp c33b3c23397670e85c38c84941d592a3bbca801e,
AgonJukebox agz a8f1075c605a78e573d488dce46d1bfacee8d3a8. Header is uppercase
`CmpS` + LE32 decoded size + `SZ\x0a\x04\x01\x0c`. SRLE2 wraps a complete
RLE2 file, including its header. Command bytes:23,0,160,dstLE16,65,srcLE16.
Do not assign historical67 or alter official compression64 semantics.

Web EVR1 remains RLE2 only: sending SRLE2 there would break the browser contract.
This iteration compiles the reusable SRLE2 encoder/decoder and asset dispatcher;
a separately negotiated browser decoder/output integration follows validation.
Original codec globals require one nonblocking admission gate shared by all users.
Caller receives failure/busy, never an ESP32 abort. Malformed-stream testing and
memory/cycle qualification are mandatory before enabling untrusted inputs.

## Pending release-gated validation

1. Golden compatibility: original `szip -b41o3` → P4 decode, P4 encode → original
   decoder; then composed SRLE2 both directions, exact bytes after decode.
2. Mainboard wrapper fixture: segmented input, same source/destination, successive
   command65 calls, ordinary bitmap creation and exact pixel comparison.
3. Stored/tiny blocks, truncated range streams, bogus index/order/record length,
   output capacity, allocation exhaustion and concurrent busy response.
4. Measure PSRAM high-water and task stack; benchmark raw/RLE2/SRLE2 CPU time,
   bytes, and eventually browser throughput with its own negotiated decoder.
5. None of these tests is authorized to execute while the other agent owns bench;
   current instruction also excludes host runtime testing until the all-clear.

## Compile reproduction

Use project `.venv/bin/python prepare.py PARENT_RLE2_BUILD NEW_PRIVATE_DIRECTORY`,
then `.venv/bin/python build.py NEW_PRIVATE_DIRECTORY` (script paths relative to
this directory; run from repository root). Parent must be the retained r06 source
closure/configuration; source identity and private location are in build evidence.
The generated source-selection manifest explicitly includes original C modules;
qsort_u4.c is included by sz_srt.c, not compiled a second time. No upload target.

Compile-only phase complete; see [RESULTS.md](RESULTS.md). Runtime gates remain
closed pending Author release.

## Bench-independent browser follow-up

Author authorized and completed the [Linux replay/browser tasklet](web/README.md).
Its reusable decoder and replay suite passed native/browser qualification and are
ready for review; see [results](web/RESULTS.md). It did not access the occupied bench. Its scoped host execution supersedes the blanket host-test
restriction above when that tasklet proceeds; hardware remains reserved.

## Hardware release supersedes earlier bench restriction

Author released the bench and authorized the [physical qualification goal](hardware/README.md).
Restore saved EMOS unchanged; keep mainboard VDP stock. The hardware contract owns
current execution and review gates. Earlier compile-only limits are historical.
