# P01f S — snapshot row priority experiment

## Executive summary

**The priority19 treatment failed and is not suitable for adoption.** Control
passed at60.046refresh/s with21.345ms p95; treatment diagnostic timings fell to
39.971/s with53.909ms p95 and its terminal pixel query failed15. The harness
stopped before the remaining repeats. r43/startup restored and verified; standard
hardware voice and completion banner delivered. Next: focused ownership audit A,
not another unmeasured priority adjustment. See [results](TABLES.md).

The tested intervention raised only snapshot row-call priority from2 to19 and
restored2 after native exclusion, before normalization. Interrupts, renderer,
other task priorities/affinities and full-frame browser payload were unchanged.
Same binary selected control/treatment; this remains default-off experimental
code, not a production scheduling policy.

## S review stop — failed treatment

Control passed at60.046 refresh/s,21.345ms p95. First priority19 treatment
returned terminal query error15; diagnostic trace39.971refresh/s,53.909ms p95.
Both2400-state hashes and completion traces match, but the treatment is not a
passing benchmark. Stop gate fired; remaining two controls not run. No adoption.
[Comparative results and limitations](TABLES.md). Recommend focused ownership
and inheritance audit A before another scheduling intervention.

## Frozen execution contract

1. [x] S01: Freeze source précis/intervention and clear hardware screen; review
   RAII early-return/nesting restoration and default-off build boundary.
2. [x] S02: Implement default-off scope in project adapter, host-check, commit;
   archive r45 source and overlay only this change. Select experimental r48
   explicitly for this task, no production identity increment. Build once using
   pinned SDK/config and record hashes. No owner/lock-wake probe flags.
3. [x] S03: Verify current r43 and unchanged startup/fixture; deploy/readback
   candidate and check boot/input. Same wired-Pi observer and r05 fixture.
4. [ ] S04 (stopped at first treatment failure; repeats unexecuted): Run control/treatment/treatment/control, identical Agon-reset startup,
   warm P4 as in B, fresh nonces,180second observers. Require2400states/completions,
   state hash, terminal pixel query, no accounting failure, no browser decode
   error/overflow, keyboard/SD health. Stop at first failure; no automatic retry
   or timeout relaxation. Four collections ~14minutes plus build/staging/rollback.
5. [x] S05: Compare refresh spacing, output throughput and composition/send wall
   time; require both directions rather than select favorable average. Same
   image control must retain approximately60refresh/s with streaming tail;
   if not, stop as changed baseline. No root-cause/parity claim from average alone.
6. [x] S06: Restore/readback r43/startup, verify SD/input, leave Legacy MOS;
   commit results, standard hardware voice and visible banner. Stop before A.

## Source précis and exact scope

Pinned ESP-IDF5.5.5 FreeRTOS-Kernel/tasks.c::vTaskPrioritySet changes base priority;
when priority is inherited it deliberately does not directly replace effective
priority. pthread recursive mutex uses FreeRTOS recursive mutex. Therefore do
not raise/lower inside an already-held native mutex or save an inherited priority
as the task base. stock_p4_service.cpp calls prepareRows with no native or pool
mutex held. prepareRows releases its recursive guard before returning; internal
recursive calls have unwound. Place RAII outside that call and lower afterward.
At entry for the experimental operation require current priority2; during it
expect19; at exit restore2. Nested same-ceiling scope does not lower the outer
scope. The snapshot task's configured base and affinity remain2/core1. Parser,
drawing, lwIP and HTTP settings are unchanged. Waiting for native exclusion at19
can also cause normal mutex inheritance in its current holder; this is part of
the intervention and bars an overly narrow claim of snapshot-only CPU effects.

Use a small generic ceiling guard plus RTOS adapter. The experimental selector
is compile-time gated, arms only valid P02 normal nonce byte4=1. Default and
byte4=0 remain control. Post-window record reports selected priority; no per-row
clock reads, counters, allocation, locks, serial output or scheduler hooks.
Snapshots retain full byte-per-pixel payload, row order and normalization outside
native exclusion. No queue, renderer, affinity, IRQ or network policy change.

The P4 tasks source above is authoritative for installed behavior; official
Espressif overview explains priority/affinity scheduling, but stable online docs
currently describe newer6.1 and must not override pinned5.5.5 semantics:
https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/system/freertos_idf.html
Agon sprite/refresh API and retained fixture semantics are unchanged. Parent
P02 actor inventory and P01f B measurements provide baseline and constraints.

## Interpretation limits

Priority changes themselves have per-row overhead; same-image control holds
layout constant but cannot cancel the cost of RTOS priority calls. If an early
validity gate fails, save diagnostic records, stop and restore instead of
claiming improvement from surviving counters. No P01e heavy probes in this pass.
No full architecture audit, new game tests or production promotion in this chunk.

S01 source check: priority guard surrounds prepareRows, outside native locks;
recursive inner native calls unwind before restoration. Host tests cover disabled
path, nested ceiling, early return and exception unwinding (firmware does not
require exceptions). No per-row diagnostic counters/timestamps added. The
post-window NPPRIO record verifies selector; it is not a measured CPU trace.

Before-run control admission bound:58–62 completed refresh/s and streamed p95
spacing at least20ms. This encompasses retained approximately60/s controls with
22–29ms streaming tails; outside it is a changed baseline/review stop, not proof
of a defect. This guard is agent-selected and frozen before any S bench run.

S02 build succeeded using pinned tools and archived r45 plus only the three
P01f S source changes. Parent delta retained in archived-parent.patch; new header
is tracked in vdp/video/extender/diagnostics/row_priority.hpp. No owner/lock-wake
flags or scheduler hooks in candidate. One image serves all four controls;
manifest retains exact source, SDK tasks and runner hashes. No production build
flags or SDK installation were modified.

## Closeout

r43 flash readback/boot identity verified, original autoexec restored/read back,
SD and neutral keyboard checked and SD exited to Legacy MOS. Accepted British
voice produced fresh stage6/audio-pass receipt; visible failure/review banner
sent. Human hearing unconfirmed. No active capture/observer/controller. Evidence
hashes and both sanitized native traces independently rechecked. Granular local
commits; no push. S04 remains stopped, not falsely checked off. Audit A not begun.
