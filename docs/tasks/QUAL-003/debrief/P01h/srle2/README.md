# SRLE2 P4 iteration — compile-only contract

## Executive summary

Author authorizes original-source szip on P4 plus EDP wrappers under P01h.
Bench belongs to another agent: no flash, serial/network bench access, resets,
emulators, codec execution or runtime tests until explicit release. Compile only.

1. [ ] Pin original szip source and historical mainboard contracts/license notices.
2. [ ] Port C codec through bounded memory I/O, checked PSRAM allocation, recoverable
   errors and serialized access; preserve order3, recordsize1 entropy format.
3. [ ] Add SRLE2 encode/decode APIs and command65 single-layer CmpS decoding.
   Keep TVC and RLE2 paths. Two command65 calls decode SRLE2 then create bitmap.
4. [ ] Compile an isolated P4 candidate; record hashes, compiler diagnostics,
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
