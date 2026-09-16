# P01f — baseline, scheduling causality and ownership audit

## Executive summary

Author authorized this continuation on 2026-09-16: freeze the contract, then
execute in discrete chunks with hardware voice notification at each review stop.
First recover a representative lower-overhead baseline; then test one bounded
scheduling change; use the evidence to audit the port's ownership and handoffs
against FabGL. This is experimental investigation, not authorization to rewrite
upstream rendering, remove FreeRTOS or promote a firmware release.

## B findings — 2026-09-16

**Representative lower-overhead baseline recovered; streamed pacing tail remains.**
All three controls passed. Streaming: 60.056/60.053 refresh completions/s,
p95 spacing 24.990/29.291ms. Output disabled: 60.053/s, p95 17.052ms;
historical mainboard p95 17.063ms. Web sends during game: 28.226/27.232 per second.
No priority change or new firmware build was made.

Mean snapshot wall time changed from 6.596 to 13.424ms across the two streaming
runs while sending stayed 17.753/17.760ms. Baseline is representative, not
variance-free. Next S should use repeated matched controls to test one priority
intervention; no conclusion from one favorable average. P01e's slow diagnostic
candidate is not the performance baseline. Original r43/startup restored and verified; hardware voice receipt and
completion banner delivered. Chunk B is complete; S/A remain unexecuted. [Detailed tables and limits](TABLES.md).

## Evidence and source précis

P01e captured a snapshot native mutex held for 25.210ms while TCP/IP task tiT
occupied the owner's core for 24.737ms. Task residency includes ISR time. The
probe candidate was slow even with recording disabled and its instrumented
fixture failed a terminal pixel query. It is diagnostic evidence, not a valid
performance baseline. See ../P01e/README.md and ../P02/README.md.

Retained P02 r45 has bounded refresh/output counters but neither P01c/d broad
lock probes nor P01e's scheduler hooks and 28KiB rings. Reuse its exact archived
binary, manifest and source. Do not rebuild it or claim zero instrumentation.
Retained FabGL vga64controller.cpp::ISRHandler notifies drawing at vertical sync;
P4 display/stock_p4_service.cpp uses timer notifications and scheduled snapshot
work. The focused audit must distinguish inherited behavior from project-added
locks/tasks and identify the original timing/ownership guarantee for each.

## Frozen boundaries and decisions

1. Author-approved sequence: baseline, bounded priority causality experiment,
   focused upstream/port scheduling and ownership audit. Agent selects chunk
   size; stop and notify after each completed discrete chunk.
2. B below is the current execution chunk. S and A are authorized scope but
   will not run in the same chunk. Later candidate details must be recorded
   and frozen before execution; no silent product/revision changes.
3. No disabling interrupts, blanket priority/affinity changes, assembly rewrite,
   allocator changes, changed game behavior, output pacing/chunking, RLE or
   reduced frame payload. Golem, MOS flashing and mainboard VDP flashing excluded.
4. Preserve stock VDP rendering semantics. An architecture hypothesis does not
   authorize simplification without evidence. Identify waits, locks, execution
   and interrupts separately; never equate task residency with exclusive CPU.
5. Reuse wired-Pi full-frame browser observer and r05 SW2400 fixture unchanged.
   Hardware sprites and current Rally are not measured in this bounded chunk.
6. Every bench change requires verified rollback, original autoexec backup,
   fixture readback, exact image/hash identity and default fail-closed tools.
   Mode is selected by autoexec, never by editing the fixture. No experimental push.
7. Stop on fixture/trace failure, unexpected image, resets, malformed output or
   pending accounting. Retain failure and recover; no relaxed gates or automatic
   retry. A non-representative baseline is itself a review stop.

## B — unchanged lower-overhead baseline (current chunk)

1. [x] B01: Freeze contract and runners; clear mainboard through admitted CLI.
   Verify r45 and r43 archive hashes and inherited fixture/startup; record provenance.
2. [x] B02: Preserve/verify installed r43, deploy/readback exact archived r45,
   observe boot identity and input readiness. No compilation or source change.
3. [x] B03: Run normal streaming, output disabled, normal streaming on the same
   image with identical Agon reset procedure and fresh nonces. Each normal run
   has the retained 180s wired observer. Do not reset P4 between these controls;
   this reproduces historical warm-P4 ordering rather than claiming cold-boot
   equivalence. No browser observer in the disabled control. Record actual
   runtime and reset-to-collection duration. Approximately 10 minutes collection
   plus preparation/rollback; estimate is not a timeout-based reset policy.
4. [x] B04: Require fixture count 2400, matching deterministic state hash,
   terminal query success, 2400 native completions and valid output accounting.
   Tabulate refresh/s, spacing p50/p95/p99/max in ms, composition/send ms and
   game-window sends/s. Compare r45 historical and historical mainboard scopes
   honestly. Mainboard is not rerun; browser throughput is not render FPS.
   Treat normal near-60 average with wider spacing than output-off as recurrence,
   not parity. Report repeat variability rather than pick the favorable run.
5. [x] B05: Restore/readback original autoexec and r43; verify keyboard/SD,
   exit to Legacy MOS, record results and commits, hardware voice plus visible
   completion banner. Stop for review before S.

## S — one bounded scheduling experiment (current chunk)

Author authorized proceeding after B. [Frozen S details](S/README.md) govern this chunk.

1. [x] S01: Using B, freeze a single priority intervention and comparable control.
   Inspect ESP-IDF priority inheritance and core placement before choosing scope;
   priority restoration must remain correct across nested locks and all exits.
   Do not wait on locks with interrupts disabled. Avoid broad network starvation.
2. [ ] S02 (built/tested; paired sequence stopped at failed treatment): Build/hash/test control and intervention with minimal equal overhead;
   run deterministic paired/repeated controls, verify pixels, transfer integrity,
   refresh/output timing and keyboard/SD. Stop at failure; restore and notify.
3. [x] S03: Decide whether the intervention supports causality, including adverse
   network effects. No adoption based only on a faster favorable average.

## A — focused FabGL/port architecture audit (subsequent chunk)

1. [ ] A01: Map parser, primitive execution, snapshot producer, HTTP sender and
   network stack ownership; every queue, mutex and notification on that path.
2. [ ] A02: For each handoff document original upstream reason, current P4
   reason, timing guarantee lost/preserved and evidence. Separate observed
   defects from suspected unnecessary layers; consult pinned official SDK sources.
3. [ ] A03: Recommend the smallest evidence-supported remedy; report prerequisites
   for any structural change. Link the already required exhaustive FabGL audit
   rather than duplicating it. Commit, notify and stop; no redesign by implication.

## B closeout

Baseline image r43 was independently flash-readback verified and its boot/native
USB identity observed. Original autoexec was restored/read back, SD and neutral
keyboard checked, and SD exited to Legacy MOS. Standard British voice produced
a fresh stage6/audio-pass receipt; completion banner issued without clearing it.
No capture, browser observer or controller remains active. Human hearing not
assumed. No experimental push; granular local commits retain contract and evidence.

Sanitized native traces were independently re-parsed and match all three retained
summary results; framebuffer allocation excerpts and SHA256 manifest are retained.
Next chunk S is the authorized bounded priority causality experiment, with its
precise intervention/control frozen before any build. Warm-run variability means
it needs repeated controls. This notification is the discrete-work review stop
requested by the Author; no priority/affinity change has yet occurred.

## S outcome

The first priority19 treatment failed its terminal pixel query and worsened
refresh timing (39.971/s,53.909ms p95 versus control60.046/s,21.345ms). Two
remaining runs were stopped. This is a rejected intervention, not a passing
benchmark or replicated causal estimate. See S/TABLES.md. Chunk A ownership/
inheritance audit is the recommended next work; no further scheduling guesses.
