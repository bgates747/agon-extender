# P01e — snapshot lock ownership and scheduler correlation

## Executive summary

Author authorizes the originally proposed narrower trace, not the new load ramp
or chunking proposals. Capture the task-switch sequence around a long snapshot
native-lock hold, with bounded RAM and paired overhead controls. Restore r43,
original startup and keyboard/SD service, then hardware voice plus visible cue.
No optimization or experimental push; Golem/MOS/mainboard VDP excluded.

## Frozen work contract

1. [x] E01: Check pinned SDK hook support; clear mainboard screen through admitted
   native CLI. Freeze task and implementation boundaries before coding.
2. [x] E02: Default-off probe: timestamp only snapshot outer native holds, record
   bounded per-core scheduler switch rings, freeze at first >=8ms hold. Record
   task names/identities/priorities, holder and interval; retain explicit ring
   coverage/loss limits. No allocation or serial output in switch callbacks;
   no live transport during observation. Use compile-time SDK trace hooks in an
   isolated build, never edit installed SDK or official reference checkouts.
   If support differs, document the adjustment before proceeding.
3. [x] E03: Host-check recorder bounds/trigger/disabled behavior, build isolated
   candidate with r43 rollback retained, verify installation/readback. Selected
   experimental revision r47 is an agent implementation choice under this
   authorization; do not silently label it production or change other flags.
4. [ ] E04: Same r05 deterministic SW2400 fixture and wired full-frame observer:
   normal probe-off, normal probe-on, output-disabled probe-on, normal probe-off
   repeat. At most one additional streamed trigger repeat if needed. Compare
   completion/output rates and probe coverage; whole-window averages alone do
   not establish overhead if recording freezes early. Expected collection about
   15–20minutes plus preparation; no blind timeout resets.
5. [ ] E05: Reconstruct captured owner descheduling/task intervals. Distinguish
   task residency from CPU-exclusive execution (ISR time is not measured), and
   switches from proof of runnable state. No claimed root cause without trace
   coverage. Stop at actionable diagnosis or documented measurement limit;
   further optimization requires review.
6. [ ] E06: Restore and verify r43/startup, retain sanitized evidence, commit
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
