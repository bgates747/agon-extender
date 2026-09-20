# Aginvadors — added performance-suite workload

**2026-09-20 correction:** the50-Hz inference below was based on the C header,
but AgonDev `clock()` actually returns raw MOS sysvar time without100-Hz
conversion. That inference is withdrawn. BENCH-007 measures actual cadence and
changes production to explicit one-vblank pacing; no20% speedup is established.


## Executive summary

Author adds Aginvadors to the output-pacing test suite. It complements the
512×384 Nurples fixture with a smaller 320×240 workload. Source matching the
previously deployed artifact selects mode8, single-buffered, with an intended
50-update/s loop. Do not interpret near-60 browser presentations as 60 game
updates. No new game build, instrumentation, deployment or hardware test here.

## Baseline and source review — 2026-09-20

1. Game repository snapshot: 7d688252b549e619ea9ff6968f2d5d068f3bf1ef.
   `agon/src/main.cpp::main` calls `vdp_mode(8)`, uses pixel coordinates, then
   schedules `next += 2` C-clock ticks per update. The source comment explicitly
   targets 50 Hz; the selected Agon dev C library defines CLOCKS_PER_SEC=100.
   Actual loop cadence remains to be measured, not inferred from comments alone.
2. Compiled artifact SHA256:
   f8ec1eeee5968b5ea125a9d060bc87abbdfe081e6942e9f53e7a18fb3578e28a.
   Matches the earlier deployment receipt in ignored agents/aginvadors-play.
   Current physical game identity was not reread during the Author's playtest.
3. Official Screen-Modes.md: mode8 is 320×240, 64 colours, nominal60Hz;
   mode136 adds double buffering. Mode20 is 512×384, 64 colours, nominal60Hz;
   mode148 is its double-buffered counterpart. The game source selects8, not136.
4. Source includes a `demo` path with scripted movement/fire, but build argument
   processing and whether that path is usable must be checked before choosing it
   as an automated fixture. Do not assume a deterministic seed: initialization
   currently derives its seed from clock(). High-score writes are possible in
   ordinary play; isolate future fixtures under /test.

## Author observation

With browser video and keyboard in ExCom, Presented fps sometimes approached60,
usually a little below, with substantial jerkiness and brief dips near25fps.
With Legacy rendering and browser keyboard input only, gameplay was smooth.
These are human observations, not paired application timing or measured scanout.
Legacy changes the renderer as well as disabling Extender video use, so it does
not isolate video streaming alone. Host monitor refresh is unknown.

## Suite inclusion and resumption gates

1. Include Aginvadors alongside Nurples in the planned same-firmware 30/60/30
   browser request-cap comparisons. Preserve normal codec negotiation and record
   actual frame format/size and request/receipt/presentation intervals.
2. Measure game updates separately from browser delivery; mode nominal refresh
   and the game's intended simulation rate differ. Retain human gameplay review.
3. Before automation, freeze binary identity, finite repeatable input/seed/run
   length and durable application timing. Reuse existing test infrastructure;
   any game modifications belong in a test-owned copy, not the production game.
4. Do not promote a mode8/136 60-Hz exception on peak Presented fps alone. Confirm
   stable pacing and application progress under the selected workload first.
5. Mode changes in any new test derivative remain startup-owned per bench rules;
   invoking an unchanged game's original mode behavior must be explicitly scoped.

This document adds suite scope, not permission to interrupt current play or flash.
