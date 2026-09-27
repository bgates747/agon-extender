# R05-A08 runtime integration work contract

Connect the locally tested WebDAV adapter to the owned runtime interfaces, while
keeping deployment disabled and the occupied bench untouched. Local engine tests
are not substitutes for physical UART/card or native-file-manager qualification.
This completes existing A08 integration work; A09–A12 retain their original gates.

A08-R01 [x] Serialize P4 local-card operations and staging ownership. Reserve the
private spool namespace against reads, writes and ancestor/tree operations. Mount
once under the same guard; do not format or delete retained evidence.

A08-R02 [x] Implement the bounded external admission peer on the existing console
queue: fresh HELLO incarnation, current idle POLL, immutable OFFER/descriptor,
DECIDE/READY grant, one file request/reply, cancellation and terminal closure.
Busy requests are rejected, not deferred. Retire stale generations/reset identities.

A08-R03 [x] Implement the finite EMOS-owned sdjob utility and only the resident
handoff needed to expose its already claimed binding. Reuse the existing file
engine. Interrupt handlers copy packets only. Missing/wrong utility and errors
restore CLI; no second application load or grant to ordinary foreground callers.

A08-R04 [x] Connect Channel to that peer and add the dedicated bounded-socket
worker, independently of video/input HTTP. Use explicit port, quota and stack
configuration; keep startup/capability enablement gated until integration checks.

A08-R05 [x] Run host lifecycle/interleaving and real-engine integration checks,
P4 compilation and EMOS/utility build gates. Preserve existing manual listener
and application-origin behavior. No physical access or emulator profile changes.

A08-R06 [x] Record exact results, residual limitations and the eventual deployment
recipe without performing it. Commit cohesive local work; production is unchanged.

Frozen 2026-09-27 under the Author's no-hardware development authorization.
Ordinary MOS filesystem contracts remain the official documented APIs; no new
hardware/VDU protocol is introduced. Private control refinements must be recorded
in ADMISSION-CONTRACT.md beside the implementation. Initial runtime must not
advertise ExCom or application staging capabilities that it does not implement.

## Local completion boundary

R01–R06 are implemented and locally checked. The finite utility and real Channel
are now tested together with the existing checked engine; both P4 gate branches
and the EMOS/MOSlet targets compile. See [connected runtime results](A08-INTEGRATION-RESULTS.md)
for exact scope, resource figures and the unexecuted deployment recipe. The
ordinary build gate stays disabled. A09–A12 still own physical and native-client
qualification; production is unchanged.
