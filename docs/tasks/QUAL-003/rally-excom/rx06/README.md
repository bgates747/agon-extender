# RX06 — immediate signed fixed-point repair

## Executive summary

Candidate adds a narrow P4-only checked conversion at buffered command41's
fixed-point result boundary. All65,764 host checks pass with undefined-behavior
and float-cast-overflow sanitizers. Physical r03 comparison remains pending.
The wider enumeration and no-op audio work have not started.

## Selected semantics and scope

1. Fixed formats are signed16/32 values stored as bits. Scale by the selected
   power of two, truncate toward zero, check the signed result domain before
   casting, then encode using defined integer-to-unsigned conversion. Exclusive
   upper bounds avoid INT32_MAX rounding to an invalid float boundary.
2. NaN, infinity, scaling overflow and an out-of-format truncated value reject
   the entire transform before replacing the destination buffer. Temporary
   streams are discarded. This is explicit handling of inputs with no portable
   stock conversion oracle; it is not claimed as stock overflow parity, and no
   clamping coordinate is synthesized. Valid fractional values truncate toward
   zero. Floating output formats retain their existing path.
3. Current conversion edits are only the new port helper and one fixed-result
   call site in vdu_buffered.h. Official references stay unchanged. Remaining
   conversion sites are intentionally not audited or repaired in this step.
4. Build the physical candidate from the preserved installed r17 source archive,
   adding only this patch/helper and the r18 identity. Preserve original poll1,
   TCP32k and DSP lifetime settings, dependencies and EMOS/mainboard firmware.
   This avoids attributing unrelated newer UART changes to the numeric repair.
   The historical parent was a dirty exploratory build: preserve that fact;
   the candidate's controlled patch is committed, but do not relabel the parent
   or this composite as a qualified release.
5. Reuse unchanged r03 fixture and sample positions on both routes. Require
   the same stock reference values and zero paired differences. Recheck r01/r02
   only if this repair or results raise a relevant concern. Restore original
   startup/usable bench, keep known-good firmware rollback, then hardware voice.
   No unreviewed firmware push; stop before the wider enumeration.

## Host verification

`c++ -std=c++17 -O2 -Wall -Wextra -Werror
-fsanitize=undefined,float-cast-overflow -fno-sanitize-recover=all -Ivdp/video
tests/fixed_conversion_test.cpp -o <ignored-output>` followed by that executable.

Tests cover every signed16 integer, fractional sign/truncation, both widths,
all encoded shifts -32..31, adjacent signed limits, nonfinite values, scale
failure and unchanged output on rejection. Host results do not establish P4
execution or buffer publication behavior; unchanged physical r03 is required.

Global version validation remains blocked by the pre-existing light2-harness-r02
connectivity hash mismatch (hardware files unchanged since4cd4ae3). Registry,
templates and VDP identity checks pass separately. No hardware record is repaired
as part of this numeric work; no claim of full qualification.
