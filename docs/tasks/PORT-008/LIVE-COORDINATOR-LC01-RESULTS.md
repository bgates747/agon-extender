# Shared P4 coordinator owner — LC01 results

## Executive summary

The private P4 console now gives boot recovery and block control the same
handover object. Boot completion can therefore authorize actual control-owner
admission; the reset monitor no longer treats legitimate block controls as a
reset. Focused software checks and complete ordinary/private P4 builds pass.
No bench firmware, EMOS source, wire format or production selection changed.

## Implementation and evidence

`ConsoleStream::parallel.handover` owns the physical phase for the lifetime of
the UART process task. `P4BootStartup` requires that object by reference instead
of constructing a second handover. Its private delegation flag remembers that
normal block return also traverses recovery phases. While delegated, startup
polling permits no ordinary UART work and performs no GPIO operations, boot
recovery deadline, restoration callback or transport cancellation. Actual block
progress and deadlines remain the next coordinator's responsibility.

After the shared handover reports UART restored, normal boot monitoring resumes.
Explicit block cancellation marks the handover failed and requests recovery;
startup then performs a fresh physical fence before invalidating old transport
state. Wrong-core calls still perform no hardware operation. Failed pad release
and cleanup retain the existing refusal behavior. No fabricated completion bits
or direct assignments to UART phase were added to product code.

| Retained validation | Result |
|---|---|
| Actual boot/runtime pad adapters and shared control owner | 722 cases pass, including four added shared-owner scenarios |
| Real EMOS/P4 block-control owners | 689 cases pass |
| Session negotiation/admission | 1149 checks pass |
| Paired handover/reset progression | 5208 cases pass |
| Native UART parking adapter | 196 cases pass |
| Console UART ownership | 2 tests pass |
| Transport/parser cancellation | 4 tests pass |
| Remove block delegation / remove return delegation | Both mutations rejected by assertions |

The added scenarios negotiate a real private session after actual boot-adapter
recovery, admit a block, hold all four CLOCK/VALID combinations during each
entry/block/return phase and check that boot polling makes no SDK call. They
exercise return to UART and completion receipt, explicit cancellation, failed
fencing and wrong-core calls. Physical block completion inputs remain modeled;
these checks do not establish actual UART drain, DMA lifetime, electrical timing
or data throughput. The ordinary console path does not instantiate this adapter.

LeakSanitizer cannot run under this session's sandbox tracing. The sanitizer
suite was rerun outside that tracing with its checks intact; no sanitizer was
disabled. One early test used a reset-indicating C=0,V=1 completion sample;
correcting that modeled sample preserved the existing reset contract.

## Remaining boundary

LC02 must bind the actual P4 UART drain/parking, native payload and reciprocal
restore/status owner, alongside the EMOS foreground coordinator and boot-monitor
exclusion. The installed ordinary pair remains unchanged. These compile-only
candidates must not be flashed as a complete live transport. No performance or
production acceptance is claimed. The Author requested discussion between
subtasks; LC01 closes only its declared owner-sharing increment.

## Build closure

Both complete P4-PC/browser compositions compile through the maintained native
wrapper and pass its unchanged validator. The private composition includes the
native payload leaves. Both are `UNVERSIONED-DO-NOT-DEPLOY` compile checks; no
installation or hardware qualification is implied. Exact source inputs match
before/after both builds and their retained archives.

[Machine-readable results](LIVE-COORDINATOR-LC01-RESULT.json) retain complete
image/ELF/map/manifest/source/archive hashes, test evidence and host durations.
Build/host durations are monotonic seconds, not transport performance. All
existing open work is preserved; no commit or push occurred in this subtask.
