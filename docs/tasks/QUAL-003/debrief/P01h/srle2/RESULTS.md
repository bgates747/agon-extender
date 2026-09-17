# SRLE2 compile-only result

## Executive summary

**Original-source szip and SRLE2 wrappers compile and link for ESP32-P4.**
No codec tests, firmware execution, flash, hardware access or performance runs
were performed. Candidate remains unqualified and uninstalled pending Author
bench release. This is implementation progress, not evidence of compression gains.

Build: `srle2-p4-r01-b2026-09-17-00-41-21Z`. GCC14.2 RISC-V, existing ESP-IDF/Arduino composition.
Application binary: 1474304 bytes; change versus
retained RLE2 r06 image: +16080 bytes. Linker reports71540 bytes static RAM;
this excludes runtime codec PSRAM allocation and is not a measured heap peak.
Factory image: 1605376 bytes.
Hashes and exact source identity are in BUILD.json and SOURCE.json.

The first compile exposed missing qsort_u4.c, an included original sorting helper;
that source was added without creating a duplicate translation unit. Final build
succeeded in100 seconds. No srle2-path compiler warnings were reported; existing
ESP-IDF/Arduino/FabGL warnings remain (deprecated ADC, unsupported peripheral
libraries, SPI volatile qualifier and inherited volatile increment).

## Implemented and deferred

1. Original C sorting, range coding and probability models; bounded P4 memory I/O,
   checked PSRAM allocations, serialized entry and recoverable error return.
2. SRLE2 composition APIs: RLE2 then szip for encode; reverse for decode.
3. Historical command65 CmpS single-layer dispatch, staged destination replacement,
   fragmented input gathering and source=destination lifecycle. A second command65
   decodes the resulting Cmpr layer; normal bitmap creation follows.
4. Existing TVC/RLE2 commands and EVR1 browser output remain unchanged. SRLE2 web
   encoding is **not enabled**: browser decoder/negotiation is a subsequent gate.
5. All runtime correctness, malformed-input safety and speed/memory claims await
   release-gated tests listed in README.md. The original algorithm is not assumed
   safe merely because the outer wrapper checks bounds. Order3/recordsize1 is the
   deliberately supported AGM subset; other compressed modes return failure.

Bench is owned by another agent. No hardware notification was attempted because
it would violate that explicit restriction. No remote push or production promotion.
