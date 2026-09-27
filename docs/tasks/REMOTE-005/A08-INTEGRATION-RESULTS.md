# A08 connected runtime — local qualification

The finite EMOS utility, P4 admission queue, checked WebDAV backend and dedicated
network worker are now connected in development source. Actual cross-component
host tests pass and both target builds compile. The endpoint remains disabled in
ordinary builds; no devices, physical cards or emulator profiles were touched.
Physical UART/card timing and native file-manager qualification remain A09–A12.

## What executes where

I01 [x] P4's existing console owner transmits all control/file packets through its
existing queue. The HTTP task never calls UART. Manual SD service and an external
job cannot own that queue together. An expired manual presence does not permanently
block a fresh CLI job through a stale pending request.

I02 [x] P4 Channel constructs a bounded immutable descriptor, reserves only a
fresh idle POLL, awaits matching READY, checks the full grant on every exchange,
and awaits FINISH plus resident CLOSE before reporting completion. Cancellation
poisons further submissions; uncertain jobs are not resubmitted automatically.

I03 [x] Resident EMOS launches the fixed finite `/emos/sdjob.bin` at the existing
claimed-CLI boundary. This MOSlet obtains the private binding, validates descriptor
fragments/CRC/paths, and services only the declared operation/subtree through the
existing checked `sdserve` engine. It does not switch display mode or load another
application. Filesystem work never runs in interrupts. Ordinary direct invocation
cannot acquire its resident binding.

I04 [x] The utility uses cooperative STATUS checks, including within engine digest
loops. Escape, cancellation, lost replies and an unfinished upload cannot report
success. Cancellation lets an already executing filesystem operation reach its
recoverable boundary. Recovery siblings remain available for deliberate recovery;
the finite utility does not perform automatic recovery or enable fast transfers.
The running `/emos/sdjob.bin` cannot be overwritten, moved or deleted by its own job.

I05 [x] Finite utility reception has two bounded packet slots. READY's control ACK
and the first file request can arrive back-to-back before the foreground drains
the first slot. A single slot loses that valid pair. Manual/application owners
retain their prior one-slot behavior. A third finite packet cannot overwrite either
slot; interruption code still only copies. This adds 240 payload bytes plus one
count byte of resident RAM, not another filesystem implementation in ROM.

I06 [x] A separate acceptor/worker serves one request per connection on development
port 8081. P4-local SD management remains on its existing port. Concurrent worker
requests receive 503; the card lease also excludes local-SD handlers. The private
spool is provisioned without formatting under that lease. A failed worker creation
closes the accepted socket. Metadata/video HTTP uses neither this worker nor socket.

## Explicit development limits

| Setting | Value / meaning |
| --- | --- |
| Compile gate | `AGON_EXTENDER_STAGED_WEBDAV=0` by default; enabled branch compiled separately |
| Negotiated capability | Admission + finite external jobs only; Legacy only |
| Port / origin | HTTP 8081, numeric local IPv4 origin for absolute Destination URLs |
| Staging quota | 32 MiB per staged payload; no claim of unlimited directory transaction size |
| Worker stack | 32 KiB, dedicated low-priority task; hardware high-water unmeasured |
| Socket waits | 5 seconds per blocking read/write; 10-minute connection deadline |
| Admission / file / close waits | 1.5 seconds / 60 seconds / 5.5 seconds, bounded polling |
| Utility clock | Existing MOS time at 120 units/s; 24-unit control wait, 12-unit STATUS cadence, 72,000-unit total job cap; stalled-clock spin bound |
| Recovery | Retain uncertain spool/Agon siblings; no retry as a fresh mutation |

Timeouts are development bounds, not measured throughput guarantees. Socket
bounds do not make physical SD driver operations interruptible. A cancellation
that has not reached terminal closure keeps the peer unavailable rather than
handing its still-active grant to another job. ExCom framing and application-origin
P4 staging are still disabled. Existing WebDAV subset limits (including no directory
replacement) remain in [adapter results](A08-RESULTS.md).

## Verification

| Check | Result |
| --- | --- |
| Raw HTTP → real Channel → real P4 Peer → real finite MOSlet → existing checked engine | PASS: PUT, byte-identical GET, MKCOL, COPY, PROPFIND, MOVE, recursive DELETE |
| Finite utility fault/scope checks | PASS: cancellation after BEGIN; unfinished stage; lost READY ACK; wrong operation/path; traversal; overwrite refusal; live utility protection |
| Peer/Channel/media tests | PASS: stale identity/reply, timeout, duplicate conflict, busy manual owner, missing claim, hidden/encoded spool paths and card lease exclusion |
| Existing adapter, real-engine and target-object groups | All four groups pass with host address/undefined-behavior sanitizers |
| EMOS repository suite | All 129 tests pass, including two-slot finite reception and unchanged manual behavior |
| EMOS firmware/linked guards | PASS; 128,369-byte image, 2,703 bytes below 128 KiB |
| Finite sdjob MOSlet | PASS; 23,067-byte binary at B0000; 5,760 bytes remaining heap/stack region, not a measured stack margin |
| Enabled P4 firmware | PASS; static RAM 68,996 bytes, flash 1,663,292 bytes |
| Ordinary disabled P4 firmware | PASS; endpoint startup/negotiation disabled |

The host substitutions are FatFS-to-POSIX calls, gateway transport, clock and task
scheduling. The admission, utility, wire protocol and file engine are real source.
These tests cannot establish physical UART burst delivery, FAT power-loss behavior,
FreeRTOS stack high-water, native-client concurrency behavior or ExCom correctness.
Logs/build details are retained in the ignored `agents/remote005-webdav-runtime`.

## Later deployment recipe — not executed

1. After bench release, re-read local bench/qualification constraints and
follow existing A09–A10 identity, preparation, rollback and deployment gates. Use
fresh paired identified builds; do not install these unversioned compile outputs.

2. Prepare EMOS through its wrapper/profile and build `projects/sdjob` as a
B0000/8000 MOSlet. Install the identified utility at `/emos/sdjob.bin` without
changing unrelated card files. Keep the checked manual listener available.

3. Explicitly enable the staged WebDAV composition for its identified P4
candidate. Startup must establish Legacy mode and Extender keyboard input before
idle admission. Neither missing utility nor unsupported ExCom may silently change
the display route or fall back to manual service.

4. Exercise A09–A12: real control/data interleavings, card faults and removal,
client disconnect, keyboard/CLI races, stack high-water and native clients. Verify
ordinary manual service and rollback. Only then consider enabling/promotion under
the Author's acceptance and version policy.

## A09 deployment preparation

Author released the bench and authorized the largest independently executable
tranche. Registry r118 allocates EMOS v0.1.22, P4 console r60 and sdjob v0.1.0
under standing version preapproval. These are experimental deployment candidates,
not production selection. `prepare_console.py --staged-webdav` enables the runtime
only in the exported build. The utility builder accepts `--utility sdjob`.

The actual eZ80 finite utility passes HELLO/STAT/READ, FINISH/CLOSE and MOS prompt
return with the real P4 admission peer in the retained UART emulator harness.
This exposed a scheduling race: resident EMOS sends HELLO immediately after CLOSE,
so the P4 must retain its terminal receipt until the HTTP worker consumes it.
A regression now covers HELLO and POLL before terminal retirement. This is local
functional evidence, not physical timing or FAT durability evidence.
