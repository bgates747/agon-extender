# A08 runtime foundations — local results

This foundation checkpoint is superseded for current completion state by
[connected runtime results](A08-INTEGRATION-RESULTS.md); retained below as bounded evidence.

2026-09-27. Development only; bench untouched and production selection unchanged.

| Component | Implemented and checked | Still required |
| --- | --- | --- |
| P4 card ownership | Nonblocking shared lease around every local-SD HTTP handler; mount/provision helper requires that lease | Worker must acquire the same lease; physical contention/mount tests |
| Private spool | Case-insensitive and decoded-path rejection, hidden recursive listings, ancestor mutation rejection | Hardware FatFS/native-client qualification |
| P4 admission peer | Bounded HELLO/POLL/OFFER/DECIDE/descriptor/READY state, single-flight file records, session binding, cancellation, terminal state and timeout checks | Actual console-queue attachment; immutable operation/subtree enforcement in finite utility |
| Resident EMOS handoff | Only the running claimed utility obtains binding/control sequence; explicit terminal report precedes resident CLOSE | Implement and integrate finite `sdjob`; actual paired lifecycle tests |
| Network worker | Existing raw adapter and real-engine tests retained | Dedicated socket worker and real Channel; no endpoint enabled |

The private card directory is `/tmp/extender/spool`. Local APIs cannot address it
(including percent-encoded/case variants), enumerate its children, or mutate its
ancestors. Other card paths remain available. A second media owner receives busy
rather than waiting behind an active transfer. This is development behavior, not
a claim about currently deployed production.

## Verification

V01 [x] Four WebDAV/runtime test groups passed: protocol/real spool, P4 adapter
object compilation, raw HTTP through real EMOS file engine, and admission/media
host checks. Host C/C++ checks use address/undefined-behavior sanitizers.

V02 [x] P4 admission test translation unit cross-compiled with warnings as errors.
The peer remains unconnected; object compilation is not a runtime integration test.

V03 [x] Full `p4-console` firmware build passed: 67,436 bytes static RAM and
1,569,002 bytes flash. These are build statistics, not runtime heap/stack measurements.

V04 [x] Resident admission and gateway host tests passed, including no false
success on ordinary utility return, terminal-report replay rejection, exact
output capacities, owner exclusion and control delivery to the finite utility.

V06 [x] Full EMOS repository suite passed: 129 tests.

V05 [x] Fresh EMOS preparation and firmware/ABI/VDU checks passed. Development
image is 128,280 bytes. No identity was promoted or firmware installed.

## Next executable work

Complete existing R02–R04: add the finite utility with path/operation enforcement,
connect its peer through the existing console owner, and connect Channel plus the
bounded socket worker. Then test those real endpoints together before any A09–A12
bench/native-client qualification. The current adapter tests deliberately substitute
the admission Channel; they must not be cited as paired admission success.

Local build/test logs are retained under the ignored agent evidence directory.
No hardware, card, emulator profile, published production bundle or release tag changed.
