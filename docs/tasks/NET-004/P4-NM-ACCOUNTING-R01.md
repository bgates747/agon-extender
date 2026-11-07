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


## Native R02 result and format portability correction

1. Sourcea66f0563 control/OFF native build and validation passed534.805s;
   enabled/ON stopped after507.551s before link. On the target ABI, uint32_t is
   unsigned long, so two JSON fields used the wrong printf `%u` conversion.
   Host checks use an ABI where uint32_t is unsigned int and did not expose it.
   Preserve this first compiler diagnostic; no enabled fit/runtime pass exists.
2. Compiler345 released12:08:01.552229UTC after every owned child joined; actual
   automatic successor346 Wolf was notified by durable mail and steering.
3. Correct only those two uint32 fields using standard PRIu32 formatting. Before
   another native link, compile the actual recorder leaf with retained target
   command/flags and a preserved original-source negative control. Original must
   fail for the observed formatting reason; corrected leaf must pass. Re-run
   meaningful recorder/composition host checks through the normal compiler slot.
4. A fresh same-source OFF/ON native pair may follow those checks under a new
   normal compiler grant, fresh output paths and original thermal/memory/process
   limits. No prior failed output becomes a passed result; no cached/generated
   product edit, toolchain replacement or hardware operation is selected.

5. First narrow target-control checker correctly compiled the original negative
   control to the two expected errors, then its raw-string assertion failed on
   ANSI color escapes. It never compiled the corrected arm or ran host checks.
   Compiler347 released12:11:26UTC with no successor. Preserve the failed raw
   diagnostic; a fresh check strips ANSI only for classification and preserves
   raw logs. Compiler flags and product source stay unchanged by this checker
   correction; do not treat it as another product failure.

6. Corrected sourceae7504c0 passes actual target recorder compilation, with the
   original negative control failing precisely the two old format conversions.
   All20 existing actual model/recorder/socket/runtime/selector/OFF-equivalence
   sanitizer steps also pass; complete guarded group18.576s. Compiler349 released
   12:13:56.835815UTC/allchildrenjoined/nextnone. No enabled full-link claim yet.
7. Next fresh native R03 pair uses this committed source, canonical defaultOFF
   thenON, fresh separate outputs, same retained IDF/dependency/toolchain and
   two compiler workers within one normal FIFO job. Original840s per arm/1800s
   whole,80C/512MiB/sensors and owned descendant cleanup remain. Hardware recovery,
   rollback and consumer handoffs stay independent and first; do not access P4
   for this build. Preserve earlier failed pairs without rewriting their results.

## Native OFF/ON fit result, 2026-11-07

Exact committed sourceae7504c0 passed both canonical native P4 builds and all
profile validators under compiler350: OFF549.743s, ON542.799s, whole1092.583s.
All owned descendants joined; actual350 release12:40:26.562409UTC assigned351
to Mech, with immediate durable/steering notification. Completion was12:34:33;
the later release time is retained, not described as immediate. Neither arm
was installed or executed on P4.

| Scope, bytes | OFF baseline | ON accounting | ON minus OFF |
|---|---:|---:|---:|
| Application image | 1,760,288 | 1,764,320 | +4,032 |
| Flash text | 1,338,140 | 1,341,260 | +3,120 |
| Flash read-only data | 283,716 | 284,636 | +920 |
| DRAM0 BSS | 38,392 | 38,344 | -48 |
| DRAM1 BSS | 11,576 | 12,384 | +808 |
| Sum of those BSS sections | 49,968 | 50,728 | +760 |
| DRAM initialized data | 22,348 | 22,348 | 0 |
| IRAM text | 115,204 | 115,204 | 0 |

The smaller DRAM0 BSS is placement/link composition, not free runtime memory;
report both sections and their sum. Flash section sums and aligned application
image deltas have distinct scopes. Both retain UNVERSIONED-DO-NOT-DEPLOY.
Default OFF object-equivalence, twenty actual host sanitizer/composition checks
and target linked fit are source/build evidence only. Counters remain local
inclusive wall-time observations, not CPU time, CTS, wire occupancy or exclusive
NM cost. A later separately frozen matched diagnostic case is still required.


## Selected identified artifact preparation after native350

1. MechAgon's existing all-processor GOAL selects identification of the checked sourceae7504c0 for a later separate case. Reuse native350 OFF/ON fit and twenty host checks as existing evidence; no product source changes or duplicate pair are needed. Keep the installed P4/defaultOFF unchanged. This is source/build/package preparation only: no hardware reservation, read, install, reset or case is selected.
2. Build one accounting-ON identified image through the same native wrapper and pinned PC/UART/HDMI/USB/controller/reciprocal-boot composition. Use the existing approved `net-003-r02` build lineage with a fresh UTC build timestamp and explicit experimental accounting manifest; no new revision, default or identity policy is introduced. Match the installed build's private reset-bridge configuration by its retained local hash; do not publish its endpoint. Prior fit images deliberately lacked that configuration and remain UNVERSIONED-DO-NOT-DEPLOY.
3. Use normal Pi compiler FIFO, exactly two workers in the one build, fresh SSD output/TMPDIR,840s child and1200s whole bound,80C/512MiB/sensor limits, and joined owned descendants. Existing source/hook/schema checks remain valid while inputs are byte-identical. Run the canonical profile/action/archive/ELF/config validation for the new identity. Release immediately after joined completion/failure and notify the actual automatic successor before analysis. A failed build never becomes an installed candidate or triggers an unchanged retry.
4. Freeze the identified app/ELF/map/config/dependency lock/source archive, build and validation manifests, reader contract and independent inventory hashes. Explicitly preserve active-scope, saturation, invalid-clock/lifecycle, same-boot boundaries and inclusive/non-additive wall-time limits. The read-only local HTTP reader has no clear/start/reset and does not prove quiescence, wire occupancy, CTS or CPU percentage; no duplicate profiler or per-byte timestamp is added.
5. Rehash exact retained normald9b application/manifest and record app offset20000 plus candidate/rollback sector-aligned touched spans. Preserve bootloader, partition table, NVS and unrelated mutable storage. Locate existing provenance for bytes beyond the old app through the new touched-sector end; if unknown, name only that unresolved tail as a future pre-write preservation prerequisite, without reading hardware now or inventing erased bytes. No incoming full-device backup is required when the exact retained spans/provenance already cover it.
6. Return exact package and read-only reader boundaries for a future separately frozen matched diagnostic case. Current Wolf95 and the first-priority unchanged47dadc L0/L1 owner installation/handoff stay independent; no accounting deployment is attached to them. Processor-time attribution beyond these inclusive wall brackets requires separately selected scheduler-aware evidence; no CPU percentage follows from source size or a successful native link.

## Identified build result, 2026-11-07

The checked accounting source now has an identified experimental artifact for a
future matched diagnostic case. It has not been installed or executed on P4.
The ordinary installed P4 and production selection remain unchanged.

1. Source `ae7504c034ebba102b3a0b4bb2913230a190343c`, clean canonical native
   build `net-003-r02-b2026-11-07-17-20-06Z`, passes profile/action/archive/ELF
   validators. Compiler406 completed in556.217 seconds and released at
   17:29:23.123948UTC after all owned descendants joined; automatic successor407
   MechAgon received the immediate mailbox/steering handoff. Existing twenty host
   checks and matched350 OFF/ON fit remain the evidence; neither was duplicated.
2. App1,764,368 bytes, SHA256
   `7a219ac1679b70d8c38ecf553230d2017ab9d194a6a68677dd07ce4683570f1e`.
   Flash text1,341,260, read-only data284,684, initialized DRAM22,348,
   DRAM0/DRAM1 BSS38,344/12,384 bytes, IRAM text115,204. Compared with the prior
   unversioned ON fit, app and read-only data each grow48 bytes; identity and
   private reset configuration differ, so this is not another isolated recorder
   cost comparison. Effective SDK settings match the installed UART source;
   only two partition-table source pathname strings differ.
3. Owner-local package46,379,123 bytes, SHA256
   `3f06743ee8c9a48b96841a3782ea073dcc09fd3546cc6cc0a263caaf6f4edda2`.
   All22 members independently equal their retained originals: source archive
   and input inventory, app/ELF/map/compile actions, config/dependencies,
   manifests, reader contract and exact app-only candidate/rollback spans.
   This private package includes the installed private reset configuration;
   publication is not selected. Generated artifacts stay in the ignored owner
   record rather than Git.
4. Future app-only write offset0x20000 and sector-aligned span1,765,376 bytes
   are fully covered by the existing verified normal UART restoration artifact.
   Candidate span SHA256
   `fbedce5fbafc51e08ffde35d81fae6b0d9a02b5cfb0123032d44a82389d6b239`;
   exact rollback span
   `629aab118e03e7b42b3235d7eed633b6103931273d524f097ef446e92fc3d17f`.
   Normal application hash remains `d9bcb1a2...`, separately from its touched
   sectors. Existing incoming-tail provenance was rehashed locally; no unknown
   bytes, invented erased tail or new device backup is needed for this span.
   Bootloader, partition table, NVS and unrelated storage remain outside it.
5. Read-only `GET /diagnostics/nm-accounting` follows the source reader contract:
   same boot/build, valid unsaturated coherent snapshots, active-scope and
   crossing-scope limits, non-additive inclusive elapsed time. No start/clear/reset,
   CPU percentage, physical CTS, wire occupancy or proven quiescence. A future
   separately frozen matched workload, reader schedule, positive retirement and
   exact installation/rollback remain prerequisites to hardware measurement.
   This artifact adds no test or firmware substitution to L0/L1 headroom work.

## Connect-fault source finding and selected bounded extension

The installed UART source and identified accounting build do not export the
socket cause behind CONNECT_FAILED. The private TcpClient error member survives
close until a later valid start, but no supported reader consumes it. The wire
header's diagnostic comment is not an implemented errno export. Accounting can
count a correctly framed FAULT reply as a successful peer request; its socket
read/write rows do not cover connection establishment.

1. Exact installed source `e14e0b8a` and accounting source `ae7504c0` have identical
   peer/header/wire logic and unchanged TCP start/poll/close failure mapping.
   Initial link/port/channel/start rejection and asynchronous socket failures
   collapse to payload CONNECT_FAILED2. Local1500ms timeout is a separate3;
   link loss and idle expiry have separate5/6 codes. Explicit stop retires the
   owner without a cancellation payload. Actual96's accepted POLL/FAULT2 proves
   none of the underlying errno, endpoint or physical causes.
2. Existing GOAL owner delegation selects a source/build-only extension after
   this finding. Preserve identified7a219 and its package unchanged. Use a new
   isolated source branch from committed ae7504c0; do not edit frozen source,
   active Wolf inputs or current installed firmware. Wolf97 and first-priority
   Mech consumer admission/cleanup remain independent and take precedence.
3. Reuse the existing default-OFF recorder, lock, fixed coherent snapshot and
   read-only HTTP reader. Retain one first unsuccessful connect attempt for the
   boot, with attempt/token/query binding, admitted IPv4/port, origin, actual
   operation result, immediately saved errno or SO_ERROR with validity, local
   attempt/event timestamps and cancellation distinction. Preserve it through
   later attempts, owner cleanup and HTTP reads; no remote clear/reset operation.
4. Record at existing failure edges before close or subsequent calls can change
   errno. Separate start/socket/fcntl/immediate connect, poll/SO_ERROR, local
   deadline, admission and cancellation paths. An absent errno is explicitly
   invalid, never zero-as-success or a stale member. Consume no additional
   SO_ERROR, socket, UART or hardware observations. A cancellation record is not
   a new NM fault code or proof that a packet was lost.
5. Keep normal queue/lifecycle/framing/status/deadline/retry/ownership behavior
   and default-OFF socket code equivalent. No per-byte logging, ring, global
   CPU accounting, new EMOS ABI or protocol checksum. Report actual fixed state,
   symbols, image/section/map costs after linking, without a fit assumption.
6. Through normal finite compiler FIFO, exercise actual source start/poll and
   EINPROGRESS/SO_ERROR/error/timeout/cancel paths, first-record retention and
   OFF equivalence with an unchanged control. Reuse unaffected prior checks;
   retain informative negative controls. Then one fresh identified ON build
   with the same private reset configuration, current toolchain and previous
   two-worker/840s-child/1200s-whole/80C/512MiB/join-release guards. No native
   build may occupy or delay a required primary physical handoff.
7. Freeze the exact artifact, source/reader/config/map/validation and touched
   rollback spans for a later separately selected matched case. This selection
   authorizes no install, target read, benchmark, new reservation, replay,
   production change or attribution of actual96's cause. Existing counters stay
   inclusive non-additive wall time; the new record is a failure witness, not CPU
   utilization or complete wire timing.
