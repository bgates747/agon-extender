# P4 message accounting — source-only diagnostic tranche

Prepare optional local counters so a later matched case can distinguish gateway,
queue, socket and UART work from inclusive waiting. The installed P4 has no
supported CPU accounting product. This tranche supplies source, checks, fit and
a reader contract; it does not install firmware or interrupt the current async
consumer chain. MechAgon's eZ80 headroom and reliable async work stay first.

## Scope and authority

1. Smith's verified GOAL-001 delegation selects all-processor measurement and
   owner collaboration. MechAgon's substantive source assignment of
   2026-11-07 selects this narrow follow-up after owner isolation/install/handoff.
2. Extender owns the P4 source and scheduler. Work in an isolated branch based
   on installed-source commit `e14e0b8a5c3c52f87b34bbeb03f9aa463816c8c5`;
   preserve active candidate/consumer source and frozen inputs.
3. The option defaults OFF. Do not add an EMOS ABI, software checksum, wire
   field, per-byte logging, global FreeRTOS runtime accounting or claimed CPU
   percentage. No target, install, reset, replay or new benchmark is selected.

## Source findings and research boundary

1. Retained `network/messages/runtime.hpp` owns a priority-4, unpinned worker,
   fixed bounded mailboxes and nonblocking socket operations. It sleeps two
   FreeRTOS ticks per loop. Configured P4 clock is 360 MHz, dual core, tick 1 kHz;
   trace/runtime stats and frame-timing scopes are OFF. Mainboard clock is a
   separate 240 MHz setting.
2. `runtime.hpp`, `mailbox.hpp`, `peer.hpp`, `tcp_client.cpp`,
   `transport/console_hardware.inc` and `console_stream.hpp` retain their NM
   framing, byte and ownership contracts. Optional observation cannot change
   request acceptance, reply bytes, ordering, retries, pacing or cleanup.
3. The matched IDF `esp_timer_get_time` source/header provides local monotonic
   microseconds; use its full value for diagnostic intervals. Current protocol
   millisecond deadlines remain unchanged, including their 32-bit modulo
   semantics. No conversion of elapsed wall time to exclusive task CPU.
4. Existing local counters are instantaneous queue/progress state, not an export
   contract. Existing compile-away frame scopes are inspiration, not active
   measurements. Keep short exact source joins in retained local evidence.

## Implementation tranche

1. Add a bounded, dependency-light counter model with explicit schema/version,
   completed event counts, byte counts, errors/WouldBlock outcomes, inclusive
   elapsed sum/max and queue highwater. Saturate overflow and publish an invalid
   flag instead of silently wrapping. Separate console and NM-worker domains.
2. Add default-OFF observation points for NM submit/take/dequeue/complete,
   peer request/tick, nonblocking socket operations and UART enqueue/drain
   transitions. Never timestamp each UART byte. Use fixed-size state; allocate
   JSON only in the existing HTTP task reader, outside observation locks.
3. Keep recorder locking bounded and actor-explicit. Recorder code never calls
   the gateway, socket, driver or application under its lock. Snapshot copies
   are coherent within the recorder; overlapping scopes/producers remain
   explicitly non-additive and include preemption. No forced task affinity.
4. Provide a read-only diagnostic reader only when the option is enabled;
   no reset/start/clear operation over HTTP. Export clock/units, counter epoch,
   active scopes, validity/saturation, sampling boundaries and limitations.
   A final sample with active scopes is not silently called a stopped interval.
5. Check actual enabled/disabled source compositions using deterministic fake
   clocks, saturation/backwards-clock controls, nested/overlapping scopes,
   full NM byte/event equivalence and absence of recorder calls/state in the
   default-OFF object. Use normal Pi compiler FIFO for build groups.
6. Report exact source, symbols/text/data/BSS deltas and reader fields. A target
   build is a build result, not a runtime pass. Any future matched hardware case
   requires its own identified plan, installed-image/rollback binding and normal
   fresh reservation after current priorities.

## Validation gates and remaining decisions

1. Source and host model checks before native P4 link; retain informative failed
   controls. Reject mutations that conflate WouldBlock with failed bytes or
   combine inclusive overlapping spans into CPU use.
2. No global task-utilization instrumentation is selected. CPU time, physical
   CTS/STOP-tail timing and exclusive wait attribution remain unresolved.
3. Reader path and exact event schema are routine implementation choices within
   this source-only tranche. Any protocol/default behavior change is out of
   scope and must be returned to the owning task rather than hidden in tracing.

## Source checkpoint and native fit tranche

1. Isolated source `a66f0563` adds the option and coherent HTTP reader; it is
   based on installed UART source `e14e0b8a`, not the current development HEAD.
   Twenty actual-source host steps pass with address, undefined-behavior and
   leak sanitizers, enabled/OFF reply equality, 200 concurrent recorder events
   and default-OFF socket object equality at Os/O2. The initial sandbox run
   stopped on LeakSanitizer's ptrace limitation; native host execution passed
   without disabling the sanitizer. No hardware diagnostic is installed.
2. The next finite compiler tranche links two fresh native P4 images from that
   same committed source, OFF then ON, with one compiler child at a time.
   Preserve the UART carrier, PC board, current USB/controller selection and
   reciprocal boot fence. Use retained pinned native IDF/tools/dependency lock;
   private cache/tool pointers remain ignored local records. Do not install a
   toolchain, flash, access the target or restart another owner's work.
3. These are fit-only `UNVERSIONED-DO-NOT-DEPLOY` builds, no reset URL configured,
   with fresh separate output paths and retained manifests/source snapshots.
   An eventual deployable diagnostic requires an agreed artifact identity and
   its separate matched hardware plan. No installed component or production
   identity is inferred from these link outputs.
4. Expected pair 10–20 minutes, whole bound 30 minutes; each native build bound
   14 minutes. Record one-second thermal/memory/owned-process observations;
   stop at 80 C, unreadable sensors or below 512 MiB available memory. Stop and
   join only owned descendants, retain the first failure and release the Pi
   slot before correction or extended analysis. No automatic unchanged retry.
5. Native validation must join exact selected sources, compile definitions,
   archive/ELF linkage and effective configuration. Compare text/data/BSS and
   application size between these two builds only. Host evidence is not an
   executed P4 counter/HTTP/transport or useful-CPU result.

## Native build continuation after measured timeout

1. The first control build reached1924/1992 actions under one compiler worker
   but did not link before its840-second child limit. The original guard stopped
   and joined every descendant; compiler342 released at11:40:10UTC. No compiler
   source error, ON image, linked size or physical result was established.
2. Keep that attempt and its source/log/process evidence. A separately reserved
   fresh native pair uses the same immutable source and canonical builder, fresh
   OFF/ON outputs and exactly two compiler workers within one active Pi build
   reservation. This changes build scheduling only. Do not install a cache or
   toolchain, resume an uncertain target command, or edit generated products.
3. Expected pair15–20 minutes, each child840s/whole1800s, same80C/512MiB/sensor
   and owned-descendant cleanup guards. Both arms use the same two-worker policy.
   Stop at the first failure and release before correction. Mech-first physical
   handoffs remain independent and must not wait for diagnostic analysis.
