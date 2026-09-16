# P01h — AGM SRLE2 compression and contention experiment

## Executive summary

Author-requested second experiment, frozen on2026-09-16 and queued after review
of P01g. Do not implement or flash this during the ladder. Investigate the Author's
AGM SRLE2 combination of bounded RGB222 RLE and subsequent “szip” entropy coding.
Its exact format, implementation and cost must be established from agon-utils,
not inferred from names or confused with an unrelated SZIP library.

## Frozen sequence

1. [ ] H01: Locate and pin the AGM/SRLE2 encoder, decoder and container contracts
   in agon-utils and relevant Jukebox sources. Record authorship, licensing,
   format/version, supported palette, keyframe/delta rules, worst-case expansion,
   memory ownership and scratch requirements. Source review before code reuse.
2. [ ] H02: Reproduce lossless round trips on retained full-frame captures from
   representative Nurples/Rally scenes plus changing/noise and all-solid inputs.
   Compare raw, RLE-only, and exact SRLE2; report payload/header bytes and ratios.
   Keep reference/copyright material ignored; Golem remains excluded.
3. [ ] H03: Propose a bounded P4 timing experiment informed by G's threshold.
   Measure encode-only cost independently from send-only and combined paths,
   using preallocated bounded buffers and no graphics lock during encoding of
   already immutable snapshots. Pin frame inputs and decoder behavior.
4. [ ] H04: After review authorizes hardware execution, compare rendering cadence,
   encode CPU/wall cost, memory use, transmitted bytes, send time and receiver
   decode/presentation latency; include incompressible fallback and overload.
   Compression may trade network contention for CPU/cache contention; prove
   which changes, do not assume processor-heavy work is harmless.
5. [ ] H05: Document results, restore accepted firmware/startup, commit and notify.
   No promotion based solely on compressed size or favorable average throughput.

The longer-term goal remains performant full-frame one-byte-per-pixel transport
and 256-colour support. RGB222 spare-bit RLE is not silently compatible with a
256-colour alphabet. Palette/mode changes, reconnects and periodic recovery need
explicit full-frame handling if deltas are tested. Preserve Author's original
bounded-RLE attribution; distinguish zero-delta/no-change from palette index0.

This is the next experiment, not authorization to skip G review or broaden to
JPEG/H.264, sparse game-specific redraw, redesign or Golem.

## Accepted cadence amendment — 2026-09-16

Normal output controls in this experiment must now obey the30fps512×384 web
ceiling (ADR-0020). Compression is evaluated for headroom/cost within that
contract;60fps is not a required acceptance gate. Higher-rate stress work needs
explicit authorization. Native rendering timing remains independent.
