# RX09/RX10 — Approved numeric guards

## Executive summary

The Author approved the recommended N02–N06 scope and instructed execution
with a hardware spoken alert when finished. Apply minimal P4-only checks,
retain stock valid-input conversion/order, then compare deterministic valid
streams on stock mainboard VDP and P4. No Golem, N07/N08/dormant fixes, audio
synthesis, unrelated optimizations or experimental push.

## Frozen behavior

1. N02: After all logical-translation arguments are consumed, verify both X/Y
   can truncate into int16 before Context::scale. Invalid input returns before
   destination matrix publication. Keep Z semantics and truncation-before-scale.
   Existing parser timeout behavior is unchanged; no new reply is invented.
2. N03: Check each transformed corner fits signed32 before its existing cast.
   Invalid corner returns before allocation/destination replacement. Do not
   change existing signed-integer geometry semantics in this bounded fix.
3. N04: Same signed32 check for direct plotted bitmap corners. Invalid corner
   skips drawing and releases both dynamically owned matrices exactly once,
   just as the existing clipped-empty path does. Borrowed matrices remain owned
   by the caller. No framebuffer/updateRect mutation on rejection.
4. N05: For all three generic transformed pixel templates, use a positive
   in-bounds conjunction on P4; NaN must fail before integer conversion or
   pointer arithmetic. Valid pixels retain stock sampling and rounding.
5. N06: Check the existing double byte-count expression lies in uint32 domain
   before its existing cast. Reject before bitmap publication; no large
   allocation or attempted payload discard is introduced (data is already in
   a buffer). Preserve zero-size and supported-format behavior.
6. Checks use ordered range comparisons, which reject NaN/infinity and avoid
   new per-pixel transcendental calls. Float32→int32 lower bound is inclusive;
   int16 accepts negative fractional inputs whose truncation is representable.
7. Host tests execute the actual guarded source bodies, not merely replicas
   of helpers. Cover boundaries, fractional negatives, NaN/infinities, ownership,
   unchanged destination/sentinels and valid-path equivalence. Stock hardware
   only receives defined valid cases; malformed/undefined behavior has no
   portable stock oracle and must not be tested through unsafe stock pointers.

## Checklist

1. [x] G01: Record approval and freeze this behavior before implementation.
2. [x] G02: Implement N02/N03/N06 parser guards and focused host tests; commit.
3. [ ] G03: Implement N04/N05 renderer guards and focused host tests; commit.
4. [ ] G04: Run target compile/source checks and existing relevant regressions;
   prepare deterministic eZ80 fixture and controlled installed-parent candidate.
5. [ ] G05: Build/identify, flash/verify P4, deploy/read back fixture and startup;
   run paired valid cases and P4 rejection cases with durable results. Keep
   mode selection in autoexec. Record fixture/runtime and preparation durations.
6. [ ] G06: Restore startup, verify CLI/SD and unmuted Rally rendering; record
   results/limits, commit and send hardware voice. Human review is separate.

The earlier RX07 baseline and source inventory are authoritative inputs. Use
unchanged official v2.16.0 and current EMOS; no mainboard flash is planned.
Future RX11 reusable import gates and UC01–UC07 inventory remain sequenced
before game benchmarks. If validation exposes an unrelated defect, preserve
it and stop rather than broaden this approved work silently.


G02: Parser guards added; retained logical-translation case, full bitmap
transform body and full bitmap-creation body pass65,931 host cases with
undefined/float-cast-overflow sanitizers. The bitmap-creation API already clears
its previous bitmap at entry; N06 preserves that stock behavior rather than
promising destination preservation the original command does not provide.
Numeric source dependencies stay P4-only. Target/hardware validation is pending.
