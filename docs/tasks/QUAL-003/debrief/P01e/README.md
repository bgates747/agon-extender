# P01e — snapshot lock ownership and scheduler correlation

## Executive summary

**Captured: the snapshot task was descheduled while holding the graphics lock,
and lwIP's higher-priority TCP/IP task occupied the same core.** In the selected
25.210ms pre-unlock hold, the snapshot owner was scheduled for only0.242ms;
TCP/IP `tiT` occupied24.737ms. This identifies a concrete lock-holder preemption
mechanism in the diagnostic candidate, not a pixel loop executing for25ms.
Interrupt time remains included in task-residency intervals.

**Qualification failed, and the sequence stopped.** The probe-off candidate was
already much slower than the previous image, and the instrumented run returned
terminal pixel-query timeout15. Its complete2,400 refresh records and matching
game-state hash are retained as diagnostic evidence, never relabeled a passing
benchmark. The planned output-off and final repeat were not run. No optimization
was made. Restore/notification receipts are recorded at closeout.

| Scope | Refresh completions/s | Spacing p95 ms | Mean full snapshot ms | Game-window sends/s | Verdict |
|---|---:|---:|---:|---:|---|
| Current probe-on | 34.661 | 46.145 | 182.723 | 4.702 | Terminal query failed; diagnostic only |
| Current probe-off | 50.138 | 33.297 | 54.940 | 7.368 | Fixture passes; baseline materially changed |
| Previous P01c/d probe-off | 60.062 | 24.796 | 7.273 | 25.453 | Historical different image |
| Mainboard historical | 59.927 | 17.063 | — | — | Historical; no equivalent web operation |

Current probe-off p95 is95.1% longer than historical mainboard; probe-on is170.4%
longer, but its failed validity gate bars a parity claim. These are refresh
completion boundaries, not browser presentation. New28KiB static trace storage,
code/layout and run-order/allocation effects are possible confounders even when
recording is off. No clean instrumentation-overhead estimate is available.

| Within the captured25.210ms hold, core1 | Scheduled residency ms | Share of hold |
|---|---:|---:|
| lwIP TCP/IP task `tiT`, priority18 | 24.737 | 98.12% |
| Lock owner `stock-output` | 0.242 | 0.96% |
| Ethernet receive `emac_rx`, priority15 | 0.181 | 0.72% |
| Between recorded switch boundaries | 0.050 | 0.20% |

The owner entered at priority2, switched out at3 and returned at5, consistent
with recursive-mutex priority inheritance; all remain below TCP/IP priority18.
Core0 recorded19.393ms of IDLE0 residency during the same interval. Task-level
preemption is observed; CPU-exclusive work, interrupt residency, every waiter's
identity and the reason for TCP/IP's long residency are not yet established.
This is not evidence of a data race, broken lwIP, or a need for assembly.

**Next avenue for review:** establish a less intrusive/representative baseline,
then test one bounded remedy for network tasks preempting the snapshot lock
owner. Evaluate priority relationships and core placement together with actual
lock scope; do not blindly move TCP/IP onto the parser/drawing core or disable
interrupts around frame copying. The current trace justifies a scheduling/exclusion
experiment, but not shipping a priority change. Preserve the lower-memory r43
control and account for allocations before drawing broad conclusions. Load ramp
remains deferred; chunking remains the Author's fallback. Golem stays excluded.

[Timeline and measurements](TABLES.md), [raw evidence manifest](evidence/manifest.json),
and [failed-run status](evidence/failed-run-status.json) retain the distinction
between a valid captured event and an invalid benchmark run.

## Frozen work contract

1. [x] E01: Check pinned SDK hook support; clear mainboard screen through admitted
   native CLI. Freeze task and implementation boundaries before coding.
2. [x] E02: Default-off probe: timestamp only snapshot outer native holds, record
   bounded per-core scheduler switch rings, freeze at first >=8ms hold. Record
   task names/identities/priorities, holder and interval; retain explicit ring
   coverage/loss limits. No allocation or serial output in switch callbacks;
   no added trace transport during observation. Use compile-time SDK trace hooks in an
   isolated build, never edit installed SDK or official reference checkouts.
   If support differs, document the adjustment before proceeding.
3. [x] E03: Host-check recorder bounds/trigger/disabled behavior, build isolated
   candidate with r43 rollback retained, verify installation/readback. Selected
   experimental revision r47 is an agent implementation choice under this
   authorization; do not silently label it production or change other flags.
4. [ ] E04 (stopped after second run failed; remaining controls not executed): Same r05 deterministic SW2400 fixture and wired full-frame observer:
   normal probe-off, normal probe-on, output-disabled probe-on, normal probe-off
   repeat. At most one additional streamed trigger repeat if needed. Compare
   completion/output rates and probe coverage; whole-window averages alone do
   not establish overhead if recording freezes early. Expected collection about
   15–20minutes plus preparation; no blind timeout resets.
5. [x] E05: Reconstruct captured owner descheduling/task intervals. Distinguish
   task residency from CPU-exclusive execution (ISR time is not measured), and
   switches from proof of runnable state. No claimed root cause without trace
   coverage. Stop at actionable diagnosis or documented measurement limit;
   further optimization requires review.
6. [x] E06: Restore and verify r43/startup, retain sanitized evidence, commit
   stages, hardware voice and visible completion banner. No experimental push.

## Source précis and constraints

Retained P01c/d streaming output hold maximum22.336ms versus composition-only
0.436ms; broad instrumentation changes snapshot/send cost and delivered rate.
This probe therefore avoids parser/draw per-acquisition histograms and global
aggregate spinlocks. A task-switch recorder still needs measured overhead.

Pinned ESP-IDF5.5.5 FreeRTOS-Kernel/tasks.c invokes traceTASK_SWITCHED_OUT/IN
inside vTaskSwitchContext around task selection, with the current-core TCB
available. FreeRTOS.h provides empty defaults. Project-scoped build injection
of these macros can observe switches without rewriting the scheduler. Consult
exact pinned source and preserve its hash in build evidence. Do not assume
latest SystemView APIs match this older SDK or claim custom events are SystemView.
Official overview: https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-guides/app_trace.html

Use internal fixed-size ring storage. Task/core identity is observed at switch
boundaries; interrupts may run within a recorded residency. Recursion must not
reset the snapshot outer hold. Record pre-unlock endpoint, unlike the earlier
post-unlock aggregate, so preemption after unlock cannot inflate this hold.
A rolling ring overwrites old history by design; reject causal interpretation
if its retained interval does not cover the entire selected lock hold. Freeze
at first long hold and stop collection safely before post-test dumping.

## Implemented probe boundaries

Snapshot-only outer hold timestamps end before unlock. Parser/draw acquisition
histograms and the shared aggregate spinlock are absent. Hold count/sum/max
continue through the whole marker window; scheduler rings freeze on the first
hold>=8ms. Each core retains512switch-in/out records including copied16byte task
names and effective priority. Static rings total28KiB; on/off controls reserve
the same RAM. No allocation/logging/locks in the scheduler callbacks. Recording
stops and in-flight callbacks drain before dumping. Refresh submission sequence
is sampled at hold acquisition; it identifies pipeline progress, not a direct
one-to-one association between snapshot and game frame. Host tests cover disabled
recording, ring wrap, recursive holds, trigger freeze and rearm.

## Build validation

Scheduler compile command includes owner_trace_hooks.h; its tasks.c object has
an unresolved call to agon_owner_switch, resolved by the final application.
ELF places callback at0x4ff058b6 and28,680byte rings at0x4ff21b84 (internal
memory). Generator opt-in is AGON_EXTENDER_OWNER_TRACE=1 plus application build
flag; ordinary builds are unchanged. The first isolated packaging attempt missed
an inherited header and generated CMake discarded the initial injection; these
were corrected before deployment and object-level checks added. No installed
SDK source was edited. Host synthetic switched-out/resumed timeline checks pass.

## First control observation

Probe-off first streaming control is substantially slower than P01c/d:50.138
refreshes/s,33.297ms spacing p95,54.940ms mean composition,7.368sends/s. Treat
this as a changed/variable comparison baseline, not representative production
performance. Retained boot/mode log still selects internal512×384 framebuffer;
no framebuffer fallback is established. New static recorder reservation/layout
is a possible confounder even with hooks inactive. Four controls will determine
repeatability; attribution must retain this limitation. Inherited periodic USB
status logs remain as in the parent; no new trace logging occurs in-window.

## Findings and disposition

1. First long hold begins19.344698seconds into the marker window, ends19.369908,
   and samples refresh-submitted sequence858: beyond the120-boundary warmup.
   Both core rings cover the complete selected interval; old ring history was
   overwritten by design but the selected hold is intact. No in-flight scope or
   callback remained when the dump was read. This event ends before mutex unlock,
   excluding the earlier probe's possible post-unlock preemption inflation.
2. Pinned lwIP `port/include/lwipopts.h` defines TCPIP_THREAD_NAME as `tiT`.
   sdkconfig selects priority18 and no affinity; the trace observes it on core1
   during this event. The EtherMAC receive task also executes on both cores in
   the retained interval. A configured affinity alone is not our evidence.
3. The callback retains switch-in/out timestamps, task address, copied name and
   effective priority. On core1, the owner switches out21microseconds after hold
   acquisition and returns near its end. TCP/IP repeatedly switches back to
   itself in the intervening period. Core0 performs small amounts of receive,
   HTTP, timer, drawing and parser activity amid substantial idle residency.
   The trace does not directly report the blocked reason of each other task.
4. sdk pthread recursive mutex uses xSemaphoreCreateRecursiveMutex and
   xSemaphoreTakeRecursive/GiveRecursive. The observed owner priority changes
   are consistent with inheritance, not proof that inheritance can outrank
   unrelated higher-priority networking. Higher numbers mean higher priority.
5. Fixture `bench_finish` waits for the terminal pixel reply through MOS API0x41
   before sending the stop marker. EMOS mos_api.asm documents15 as FR_TIMEOUT.
   Therefore the failure precedes our post-stop trace dump; do not blame the
   additional dump bytes for that earlier query timeout. No retry or timeout
   relaxation was performed. Both native traces have2,400 completions and the
   failed run's state hash still matches the retained deterministic reference.
6. First control already degraded substantially with recording off. The second
   run degrades further and fails its fence. This is a failed diagnostic overhead
   qualification. Do not compare its snapshot182.723ms mean to mainboard primitive
   execution or call it production speed. The additional ring storage is a
   plausible memory-layout/pressure confounder, not a demonstrated allocation bug.
7. The harness stopped at the first failed validity gate. Agent closeout restores
   original autoexec through the still-working SD service, then restores r43.
   No MOS/mainboard VDP experiment, speculative fix, load ramp or chunking test
   was started. Two remaining planned controls are explicitly unexecuted.
8. Raw failed NP04 bytes are preserved, not patched to make the ordinary analyzer
   accept them. Separately parsed refresh and owner records carry the failure
   context in failed-run-status.json. Full private logs, fixtures, observers and
   deployment/rollback evidence remain under ignored agents/p01e/.

## Reproduction

Host recorder: `g++ -std=c++17 -Wall -Wextra -Werror -pthread -I vdp/video docs/tasks/QUAL-003/debrief/P01e/recorder_test.cpp -o /tmp/p01e-recorder-test`.
Run the executable. Decode retained trace.log.gz, then use
`.venv/bin/python docs/tasks/QUAL-003/debrief/P01e/analyze_owner.py TRACE --nonce HEX --output RESULT.json`.
Existing refresh/output analyzers remain unchanged. Do not remove the fixture
failure check to obtain a passing result. SDK source identity and application
hashes are in candidate-build.json; source hook injection is target-only and
requires the explicit diagnostic environment/compile flag.

Official tracing context: [Espressif5.5.5 application tracing](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-guides/app_trace.html).
This recorder uses retained FreeRTOS task-switch macros, not the SystemView
wire format or live host streaming. SDK tasks.c hash is retained. The benchmark
still emits inherited periodic service logs; no added in-window trace dump.

## Closeout

r43 firmware readback/startup identity verified, original autoexec restored and
read back, keyboard neutral and SD service checked then exited. Accepted British
voice cue produced a fresh stage6/audio-pass receipt; visible mainboard banner
states P01 owner trace is ready for review. Human hearing unconfirmed. No active
capture/controller. Local contract/code/evidence/closeout commits; nothing pushed.
E04 remains explicitly incomplete after the failed gate; this tranche ends at
its authorized actionable-diagnosis/measurement-limit review stop.

Marker windows measured47.499933seconds probe-off and68.481027seconds probe-on;
fixed host observer windows were180seconds each. These are not total preparation,
collection, rollback or task durations. Failed-run host collection duration was
not emitted because the harness rejected the fixture before that summary step.
