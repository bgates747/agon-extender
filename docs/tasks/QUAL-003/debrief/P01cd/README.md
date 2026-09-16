# P01c/d — bounded native lock and wake attribution

## Executive summary

**The probes found long native-lock stalls specifically during streaming, but
also materially disturbed output performance.** This is an actionable diagnostic
lead, not a fix or proof that a particular network task caused every missed beat.
All six controls passed the same 2,400-state workload and complete refresh trace.
No renderer, MOS, priority, affinity or web-protocol optimization was made.

| Condition | Probes off refresh/s | Off spacing p95 ms | Probes on refresh/s | On spacing p95 ms |
|---|---:|---:|---:|---:|
| Normal streaming | 60.062 | 24.796 | 60.048 | 22.281 |
| Composition only | 60.054 | 20.352 | 60.057 | 17.315 |
| Output disabled | 60.056 | 17.125 | 60.055 | 17.213 |
| Mainboard historical reference | 59.927 | 17.063 | — | — |

Normal uninstrumented P4 p95 spacing is **45.3% longer** than the retained
mainboard reference. The mainboard was not rerun in this tranche. Near60 average
refresh completions/s still conceals irregular spacing and does not mean60
browser frames/s. This tests Nurples software-sprite loading, not Rally, hardware
sprites, individual bitmap-plot latency or Golem.

| Instrumented elapsed maximum | Output disabled ms | Composition only ms | Streaming ms |
|---|---:|---:|---:|
| Output notification age | 0.085 | 0.338 | 30.998 |
| Output native-lock wait | — | 0.867 | 23.048 |
| Drawing notification age | 0.066 | 0.364 | 22.478 |
| Parser native-lock wait | 2.252 | 2.356 | 22.477 |
| Drawing native-lock wait | 0.344 | 0.393 | 22.340 |
| Output native-lock hold | — | 0.436 | 22.336 |
| Parser native-lock hold | 2.591 | 2.307 | 16.884 |
| Drawing native-lock hold | 1.065 | 0.946 | 9.848 |

These are wall-time maxima, including preemption; notification age includes
coalescing and previous work, **not pure scheduler latency**. In the streaming
probe run14 output holds exceeded16.384ms out of172,224 acquisitions. This is a
rare long-hold mechanism worth investigating, not enough by itself to explain
the whole p95 distribution. Aggregate records cannot match individual lock
owners/waiters or align a stall with a particular refresh.

**Instrumentation sensitivity:** streamed snapshot mean rose7.273→9.299ms
(+27.9%), send mean18.294→23.415ms (+28.0%), and sends fell25.453→22.471/s
(−11.7%). Maximum refresh spacing worsened33.573→53.063ms even while p95 improved.
Composition-only snapshot mean rose6.445→7.188ms (+11.5%), while p95 spacing
improved. These single ordered pairs cannot separate probe overhead from
boot/order/scheduling variability. Therefore do not use this image to certify
performance or infer that reducing average lock duration will fix the problem.

**First avenue for review:** use a narrower, threshold-triggered event record
around native ownership plus scheduler transitions to determine which task is
running when a snapshot owner retains the lock across a long interval. Correlate
with refresh sequence/phase; quantify its overhead first. Inspect HTTP send,
lwIP/Ethernet and interrupt/core placement together, using the existing P02c
inventory. The priority5 HTTP task executes sends; moving only the priority3
network worker would miss it. No affinity change is yet selected. Ordinary
preemption, lock-holder descheduling and shared-memory contention remain
hypotheses, not proven root causes. Compression remains downstream.

Detailed [tables](TABLES.md) include means, counts, totals, histogram bounds,
completion/enqueue timings and output rates. [Raw evidence](evidence/manifest.json)
contains all six nonce-bound results and compressed trace records. Private full
captures and build/rollback scripts remain in `agents/p01cd/`.

## Frozen contract

1. [x] D01: Add default-off diagnostic hooks for native lock wait/outermost hold
   by parser/drawing/output owner and notification-to-worker-entry intervals.
   Bounded in-memory aggregates only, no timed-window prints, SD or polling.
   Distinguish coalesced notification age from scheduler runnable delay: these
   hooks alone cannot measure the latter exclusively. Retain baseline semantics.
2. [x] D02: Host-check recorder/lifecycle, build isolated candidate from retained
   P02 configuration, verify hashes/rollback/readback. Retain r43 restored firmware
   as rollback. Agent-selected candidate revision r46 within this approved
   diagnostic work; identity is experimental, never a production parity pass.
3. [x] D03: Run unchanged r05 SW2400-state fixture on output-off, composition-only
   and normal web streaming, with probe-on/off controls in the same image. Use
   existing180second wired observer for streamed cases; approximately40seconds
   game window per successful run. Six controls plus one informative repeat if
   needed, roughly20–30minutes collection excluding setup/build. Estimates are
   not automatic reset deadlines. Record raw trace, counts, work and state hash.
4. [x] D04: Compare probe overhead and owner wait/hold distributions; elapsed
   scopes include preemption. If instrumentation materially alters the contrast,
   mark attribution limited and narrow probes rather than claim causality. Stop
   before speculative priority, cache, codec or rendering changes.
5. [x] D05: Restore r43 and original startup; verify input/SD, commit evidence,
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

## Probe interpretation

1. Parser, drawing and output task owners are registered explicitly. Native
   recursive mutex semantics are retained. Only outermost acquisitions contribute
   wait/hold samples; nested work belongs to that outer hold. Foreground admission
   and execution-gate waits are not instrumented in this first bounded tranche.
2. Wait starts just before native mutex acquisition; hold starts after acquisition
   and ends just after release. These elapsed scopes include preemption. Aggregate
   bookkeeping uses a short internal spinlock outside the native lock after release.
   Instrumentation can itself create contention; on/off pairs are mandatory.
3. Wake age begins at the earliest recorded timer notification and ends after
   the worker takes a notification. Coalesced wakes and previously running work
   contribute; it is not exclusively runnable-to-scheduled latency.
4. Eight fixed aggregates include count, sum, maximum and logarithmic histograms.
   Histogram percentiles are bucket upper bounds, not exact percentiles. Raw
   microseconds are reported as milliseconds. No per-operation event list exists.
5. Counts/summed durations span the marker window and admitted scope drain;
   completion-spacing summaries retain the established warmup convention. Do
   not equate their populations or sum concurrent owner times into CPU usage.
6. Six controls execute in order normal-off, disabled-off, compose-off,
   compose-on, disabled-on, normal-on. Here the final suffix denotes probes,
   not output. Single samples and ordered runs cannot establish an exclusive
   causal explanation or rule out boot/allocation variability.

## Reproduction and retained controls

1. Host check: `g++ -std=c++17 -Wall -Wextra -Werror -pthread -I vdp/video docs/tasks/QUAL-003/debrief/P01cd/recorder_test.cpp -o /tmp/p01cd-recorder-test`, then run the binary.
2. Recorder parser: `.venv/bin/python docs/tasks/QUAL-003/debrief/P01cd/analyze_lock_wake.py CAPTURE --nonce HEX --output RESULT.json`. It rejects unfinished scopes, invalid records, duplicate markers and histogram/count disagreement.
3. Game and completion analyzers are retained in `../P02/README.md` and
   `../../nurples-parity/`; fixture binary SHA256 is
   `8e81bfeb7ca01cf6ad9f68c502a42969c5763c45033dc80f55d1a97d7880d13b`.
   Expected 2,400-state SHA256 is
   `f43eaa27074aaf6916eded49e5f97bb7eb64a79fd0ccc060f1923a9eb3ea3948`.
4. Private automated installation/run/rollback scripts and full build source are
   retained under ignored `agents/p01cd/`. Installation verifies stable device
   identity, saves the prior flash prefix, checks the installed baseline and
   partition table, then verifies the written candidate and boot identity.
5. Candidate keeps retained P02 configuration: four drawing opportunities per
   logical frame; parser core0 priority3; drawing core0 priority5; output core1
   priority2; paired native output rows; internal framebuffer and snapshot pools.
   ESP-IDF5.5.5/Arduino3.3.11, CPU360MHz, PSRAM200MHz. Ordinary browser credit and
   full512×384 one-byte pixel output remain unchanged. No core-isolation changes.

## Findings and limits

1. All14,400 submitted refreshes completed, all six game-state hashes match the
   retained reference, all output accounting is complete, and all lock records
   have zero unfinished scopes/invalid flags. Probe-off lock counts are zero.
   Composition-only output acquisition counts equal192row pairs per full frame.
2. Enabled probes observed242,624–242,625 parser and255,751–255,953 drawing
   outer acquisitions per run. Thus the default-off design is bounded in RAM,
   but still intrusive in execution frequency. Future probes should be batch-
   or threshold-focused rather than repeating this broad per-acquisition design.
3. Composition-only prepared2,397 frames in both runs, about60/s; normal runs
   sent1,017 and898 full frames, about25.45 and22.47/s. These differ in work,
   so subtracting composition-only from streamed means would not isolate network
   CPU cost. Snapshot production does not equal browser presentation.
4. Streaming output wake age has613 samples≥16.384ms out of1,813. Drawing has14
   out of9,389. Output is low priority and may already be working when notified;
   the counter measures that accumulated age as well as dispatch delay. No
   claim of915 or613 scheduler deadline misses is justified.
5. Streaming long native intervals are rare: parser wait20, drawing wait16,
   output wait11 and output hold14 samples≥16.384ms. The parser hold has one;
   drawing hold has none at that threshold. Samples overlap across owners and
   are not additive lost time. They direct investigation toward lock ownership
   during competing activity but do not identify its cause.
6. The existing enqueue-to-completion p95 remains near4ms in all six controls,
   while streamed enqueue spacing is already irregular. Continue to include
   parser admission/foreground gating in the narrowed investigation, rather
   than assuming every long completion interval originates in the renderer.
7. Host nesting, disabled-state and rearm checks passed. Parser checks rejected
   unfinished/duplicate/incomplete traces and verified histogram bounds. The
   firmware built successfully in98.72seconds. Installation retained the prior
   flash prefix and verified complete candidate bytes and startup identity.
8. Six reset-to-collection intervals total1,195.33seconds (19.92minutes), including
   fixed180second observation windows and retrieval. Each actual game marker
   window is about40seconds. Staging, building, flashing, rollback and reporting
   are separate; these totals are not a pure game or complete-task duration.
9. No seventh run: the six controls already expose the actionable lock/wake
   distinction and measurement limitation. Narrow instrumentation before more
   repetitions or any speculative optimization. This is the bounded review stop.

## Next proposed experiment — not executed

1. Reuse the same full-size streaming/reference fixture and rollback. Select a
   low-overhead bounded event design that preserves task ownership and timestamps
   around outlier intervals; count overwritten/missing events and reject overflow.
2. Correlate the native lock holder, blocked waiter, current executing task/core,
   parser admission and explicit refresh sequence. Assess supported IDF task-
   switch tracing and its overhead before enabling it; notification age alone
   does not answer who displaced a worker.
3. Use a matched probe-off control and an informative repeat/reversed order.
   Stop if probes materially change the distribution; report a limit rather than
   turning a perturbed result into a performance claim.
4. Only after ownership is attributed, propose one actor-specific scheduling or
   snapshot-lock change for review. Retain stock rendering logic. No Golem,
   MOS, compression, game-specific bezel shortcut or task-priority guess.

## Closeout

r43 flash bytes and identity restored/verified; original autoexec verified;
keyboard neutral and SD service exited to Legacy MOS. Accepted British voice
command completed with a fresh stage6/audio-pass receipt; visible completion
banner emitted. Human hearing remains unconfirmed. Start-screen clear was sent
before work. No active collector/controller; no MOS/mainboard VDP changes.
Local commits preserve contract, implementation, evidence and closeout; no push.
