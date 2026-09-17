# SRLE2 original-source port notes

## Executive summary

This is a P4 C port of pinned szip1.12, with subsequent exact native/browser
validation of its generated codec. P4 runtime remains untested and the earlier
compiled image is obsolete. See [browser results](web/RESULTS.md). Original vendor
files remain byte-for-byte intact; port.py generates modifications.

1. Historical Agon sources prepend uppercase CmpS/LE32 length to SZ 0A 04 01 0C.
   The mainboard decoder requires exactly1.12. Command65 decodes a single layer;
   use two calls for SRLE2. No command67 alias or new opcode is introduced.
2. Host testing corrected the output path: sz_unsrt(NULL) already emits through
   putc, so the caller must not append its work buffer. io.h redirects putc/getc
   as well as getchar/putchar/fread/fwrite/ungetc into bounded memory. fprintf
   diagnostics are suppressed; exit/abort return through the C error boundary.
   Invocation cleanup also requires removing retained function-local static sort
   pointers; they are now local, and the remaining global sort cache is reset.
   Native golden encode/decode and repeated browser fixtures pass. Original GPL
   notices remain with the pinned range/model modules and staged web assets.
3. Original model/sort/range arithmetic stays in C compiled for RISC-V. Fixed
   uint16_t/uint32_t replace host-specific u_int types. CMake applies C++17 only
   to C++ translation units. No Xtensa assembly or speculative P4 SIMD used.
4. Stdio and fatal exit/abort become bounded memory I/O and C-only setjmp/longjmp
   error return. No jump crosses C++ destructors. Caller stages output and only
   publishes on success. All codec allocations use checked PSRAM, with an
   invocation allocation budget. Original global sort cache is reset each call.
5. One atomic nonblocking admission flag protects original global state. Busy
   callers fail without spinning or blocking rendering. No graphics lock or
   scheduler changes. Firmware task stack still needs measurement; models move
   from stack to checked heap, but not every local array has been profiled.
6. Candidate accepts order3/recordsize1 compressed blocks (the AGM -b41o3 subset)
   and stored blocks. Other order/record transforms are rejected deliberately.
   Generic codec does not silently identify itself as full szip format support.
7. Header/size/output/token-read/run checks are added, but those checks do not
   establish that all original internal sort/model table indexes are safe on
   malicious data. Malformed corpus, sanitizers, watchdog/heap stress, byte-golden
   round trips and mainboard fixture compatibility are mandatory pending tests.
8. Web EVR1 is unchanged. Full SRLE2 browser output requires a separately versioned
   negotiation/decoder, not a silent change in EVR1 payload semantics. Firmware
   reusable encode/decode APIs are the prerequisite, not evidence of web gains.

Vendor whitespace is intentionally preserved to keep SOURCE.json hashes exact;
diff whitespace checks apply to task-owned adapters separately.
