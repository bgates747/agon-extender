# P01c/d — bounded native lock and wake attribution

## Executive summary

Author authorized immediate implementation and hardware execution without
intermediate plan review. Diagnose rendering tails before compression; stop
when evidence identifies an actionable next change. No claim of CPU-exclusive
time from elapsed scopes. Golem excluded; no MOS/mainboard VDP modifications.

## Frozen contract

1. [x] D01: Add default-off diagnostic hooks for native lock wait/outermost hold
   by parser/drawing/output owner and notification-to-worker-entry intervals.
   Bounded in-memory aggregates only, no timed-window prints, SD or polling.
   Distinguish coalesced notification age from scheduler runnable delay: these
   hooks alone cannot measure the latter exclusively. Retain baseline semantics.
2. [ ] D02: Host-check recorder/lifecycle, build isolated candidate from retained
   P02 configuration, verify hashes/rollback/readback. Retain r43 restored firmware
   as rollback. Agent-selected candidate revision r46 within this approved
   diagnostic work; identity is experimental, never a production parity pass.
3. [ ] D03: Run unchanged r05 SW2400-state fixture on output-off, composition-only
   and normal web streaming, with probe-on/off controls in the same image. Use
   existing180second wired observer for streamed cases; approximately40seconds
   game window per successful run. Six controls plus one informative repeat if
   needed, roughly20–30minutes collection excluding setup/build. Estimates are
   not automatic reset deadlines. Record raw trace, counts, work and state hash.
4. [ ] D04: Compare probe overhead and owner wait/hold distributions; elapsed
   scopes include preemption. If instrumentation materially alters the contrast,
   mark attribution limited and narrow probes rather than claim causality. Stop
   before speculative priority, cache, codec or rendering changes.
5. [ ] D05: Restore r43 and original startup; verify input/SD, commit evidence,
   hardware voice and visible completion cue. No experimental push.

Use existing P02 nonce mode selector; reserve nonce byte4 as explicit probe
enable only in this candidate. Same code/image and reserved RAM for on/off;
compare retained r45 where informative but not as a same-boot control. Recording
is admitted only inside the deterministic marker window; drain active scopes
before retrieval. Missing/overflowed or unfinished records invalidate attribution.
No hooks inside per-pixel or per-byte loops. Per-native-acquisition instrumentation
is deliberately intrusive enough to require the paired overhead controls.

Application output capture must remain full-size with normal browser credit.
Composition-only may do more work: compare rates/counts, never subtract unrelated
means as exclusive costs. Current source/hardware baseline inspected before
execution. Firmware installation preserves rollback and startup before writing.
