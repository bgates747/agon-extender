# RX06 — immediate signed fixed-point repair

## Executive summary

Candidate adds a narrow P4-only checked conversion at buffered command41's
fixed-point result boundary. All65,764 host checks pass with undefined-behavior
and float-cast-overflow sanitizers. Physical unchanged r03 now matches stock at all 80 samples (previously 14 differed); the stock results remain identical to the prior baseline.
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

## Physical result — 2026-09-15 UTC

| Same r03 fixture, mode 136 | Stock mainboard VDP | P4 ExCom | Differences |
|---|---:|---:|---:|
| Original r17 | 80 samples | 80 samples | 14 (17.5%) |
| Controlled numeric repair r18 | 80 samples | 80 samples | 0 (0%) |

Both pages are included. Stock values are unchanged from the earlier run.
The controlled repair eliminates the reproduced left-road discrepancy; it does
not establish full Rally visual acceptance, HUD correctness or performance.
No audio handler was changed. Wider conversion enumeration has not started.

The deployed build is `uart-excom-console-r18-b2026-09-15-02-58-20Z`.
See manifest.json for exact input/output identities and raw CSV/comparison files
beside this document. The same r03 binary was read back before invocation.
Factory flash was independently verified; matching startup and USB host readiness
were observed. Original mainboard VDP and EMOS were not flashed.

The isolated build took 113.4 seconds; deployment/verification took 47.70 seconds.
The collection job took 58.46 seconds from immediately after reset through
retrieval, including boot, both probes and downloads. This is an operational
estimate for repeating this small probe, **not renderer timing or FPS**.
Host checks validate the helper; physical samples validate the normal road path.
Invalid-transform destination preservation is established by code inspection,
not a dedicated physical malformed-input probe.

The installed-source archive was a historical dirty build. The candidate keeps
its dependency lock and DSP derivative unchanged and adds the committed numeric
patch and identity only. This is controlled exploratory evidence, not a clean
release qualification. The affected translation unit has no unsafe math flags.

## Review state

Original load-only Nurples autoexec was restored and independently read back;
the historical backup was preserved. The P4 numeric candidate remains installed
for review. Mainboard VDP and EMOS remain unchanged. The British hardware voice
player replaced a fresh pending marker with `audio_commands=pass`; hearing is
not yet human-confirmed. The bench returned to the Legacy MOS prompt.
No experimental changes were pushed. RX06 is complete for this bounded defect;
stop before RX07. Full-game visual acceptance remains pending.
