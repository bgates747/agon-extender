# QUAL-006 — Modern automated hardware-test control plane

## Executive summary

Replace routine qualification's inferred, boot-script-driven control with an
explicit EMOS↔P4 test-control plane. EMOS must publish its real foreground and
startup state, authorize finite jobs only at a safe top-level CLI boundary,
launch fixtures under a structured contract, and report correlated progress and
completion. The P4 must expose that state and those events to the host runner,
arbitrate incompatible browser/input/storage users, and retain a durable job
journal. The host runner must wait for declared state transitions rather than
infer execution from delivered keystrokes, old framebuffer pixels, a file
listener appearing, or a fixed delay.

This task preserves `/autoexec.txt` and a cold boot where startup behavior,
first input admission, recovery, or reset is itself under test. It removes them
from ordinary fixture launch and result collection. The accepted
[QUAL-005](QUAL-005.md) suite remains the firmware-acceptance authority until a
replacement run has passed on installed hardware and the Author accepts the
migration.

Created: 2026-09-30. Owning queue: `TODO.md`. Audit artifact:
[AUDIT.md](QUAL-006/AUDIT.md). Related work:
[REMOTE-005](REMOTE-005.md), [DIAG-002](DIAG-002.md),
[AUDIT-010](AUDIT-010.md), and
[bench constraints](../qualification/bench-constraints.md).

## State

Q06-S01 — **Audit and initial proposal complete; implementation contract not
frozen.** The audit establishes current failure modes, retained strengths, the
missing capabilities, and a proposed target architecture. The Author has not
yet accepted its protocol decisions or implementation order.

Q06-S02 — No EMOS, P4, runner, fixture, startup, flash, deployment, bench, or
production change is authorized merely by filing this task. Existing tests
retain their current contract until individually migrated and requalified.

Q06-S03 — The implementation must not silently preempt AUDIT-010, REMOTE-005,
DIAG-002, or the planned workspace reduction. The Author selects scheduling
after reviewing this contract. Reuse of REMOTE-005's admission machinery is a
coordination requirement, not permission to reopen accepted storage behavior.

Q06-S04 — On 2026-09-30 the Author accepted the architectural requirement that
resident EMOS keep the authoritative lifecycle state and report it to the P4
EDP on demand. A P4 query is observation only: it grants the P4 no authority to
launch, cancel, reset, select a mode, commit a route, or alter EMOS state. The
wire carrier and earliest boot phase at which queries are available remain open
under Q06-D06.

## Source and evidence baselines

| Role | Exact review baseline | Use in this task |
|---|---|---|
| Extender/P4 development source | `abb8ea995d7ebaff06db687d0cdff7e9a60967d3` | Current runner, HTTP endpoints, keyboard input, display observation, storage admission |
| EMOS development source | `9b67182cca4cb51f9fee0473ab32dda1e766e3db` | Current CLI lifecycle, input admission, finite `sdjob` dispatch |
| Official Agon documentation | `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` | MOS CLI, executable, API and VDU contracts |
| Official MOS reference | v3.0.2, `8336409351ee5314e02801a7b72a4f1bb5282519` | Read-only CLI/editor/loader reference |
| Official VDP reference | v2.16.0, `c7ac293d2aa81ddfa693390549bcd909069c8fc3` | Read-only VDU and display reference |

These source revisions are research baselines, not claims about the selected
production bundle or bytes installed on the bench. A future implementation
baseline must re-read `production/current.yaml`, bind exact component receipts,
and refresh this research if any authority has changed.

## Scope

Q06-C01 — Cover every maintained automated hardware path in `qualification/`,
including the integrated smoke, mode transaction, raw-SD repair case, performance
runner, shared keyboard/reset/SD helpers, manifests, notification, evidence, and
failure recovery.

Q06-C02 — Cover the EMOS CLI/editor safe point, startup execution, program and
MOSlet lifecycle, mode/routing ownership, Extender admission, result reporting,
and recovery behavior needed by those runners.

Q06-C03 — Cover P4 keyboard, screen, display, video, storage, browser-session,
admission, event-journal, and reset services where they participate in test
control or observation.

Q06-C04 — Inventory historical launch scripts only far enough to classify them
as maintained, compatibility-only, or frozen evidence. This task does not
rewrite every historical script.

Q06-C05 — Preserve the separation between source/build regression, flashing,
installed-hardware qualification, performance measurement, and human visual or
gameplay acceptance. A modern control plane does not make these evidence classes
interchangeable.

## Work items

Q06-01 [x] Audit the complete maintained hardware-test flow and record its
actors, synchronization mechanisms, state assumptions, failure behavior,
startup mutation, reset use, path assumptions, evidence channels, and retained
strengths in [AUDIT.md](QUAL-006/AUDIT.md).

Q06-02 [ ] Review this task and the audit with the Author. Resolve the decision
register one item at a time, update the proposal, and freeze the accepted
implementation contract in its own commit before source changes.

Q06-03 [ ] Amend the active bench constraint after contract acceptance. Keep
prepared `/autoexec.txt` for first admission, recovery and deliberate cold-boot
tests; permit the admitted EMOS test supervisor to select a fixture's mode before
launch during ordinary tests. Do not weaken the mainboard-keyboard recovery
boundary.

Q06-04 [ ] Specify one versioned EMOS↔P4 control protocol. Define peer and boot
identities, monotonic event sequences, foreground generations, state vocabulary,
job identity and grant, capabilities, resource leases, cancellation, terminal
results, reconnect behavior, timeouts as watchdogs, and old-peer failure modes.

Q06-05 [ ] Extend resident EMOS with a truthful lifecycle publisher. It must
distinguish boot/startup phases, startup failure, empty idle CLI, edited CLI,
command execution, utility execution, application execution, recovery-required
state, current input owner/health, EMOS-owned route/mode intent, and whether a
cooperative job may be cancelled or reset safely.

Q06-06 [ ] Extend the P4 EDP firmware to cache only current-epoch EMOS state,
correlate it with P4 display/output and client-resource state, expose a
machine-readable snapshot plus ordered event stream, journal jobs durably for
the host, and invalidate stale EMOS state after either peer restarts.

Q06-07 [ ] Generalize REMOTE-005's finite idle-CLI admission into a bounded test
job without creating another authorization path. The P4 may offer a job; EMOS
alone authorizes it at the empty top-level CLI safe point and launches the
accepted supervisor or application contract.

Q06-08 [ ] Define and implement a fixture ABI for identity, start, progress,
assertion, completion, failure, and optional cooperative cancellation. Bind
every record to the peer epochs, foreground generation, job ID, exact fixture
hash, and result schema. An application return without a valid terminal record
must not be promoted to a pass.

Q06-09 [ ] Replace routine typed CLI setup, manual `sdserve` startup, framebuffer
prompt inference, result-listener appearance, and per-case reboot with a runner
state machine driven by Q06-04 events. Perform all capability, receipt, path,
artifact, resource, and cleanup preflight before the first mutation.

Q06-10 [ ] Migrate QUAL-005 cases individually. Add focused host tests and one
physical diagnostic for each migration, retain the old case until the new case
has equivalent or stronger oracles, and pause for Author acceptance before the
next case.

Q06-11 [ ] Migrate the performance runner after functional cases. Keep loading
outside the measurement window, preserve 30 seconds of wall time, declare video
observers and browser clients as resources, and report application, rendering,
transport and presentation rates separately.

Q06-12 [ ] Isolate the residual boot-script suite. Cold-boot, startup-file,
first-admission, reset-order, missing-P4, and recovery tests may still stage
`/autoexec.txt`, but must use a transaction with exact preservation, independent
readback, a recovery artifact, and an explicit reason that live control cannot
exercise the behavior.

Q06-13 [ ] Run the complete old and new installed-system suites against the
same verified component pair where safe. Demonstrate exact startup restoration,
no routine autoexec mutation, no routine reset, truthful progress, bounded
failure, peer-restart invalidation, resource-conflict rejection, and retained
manual loaded-asset coverage.

Q06-14 [ ] After Author acceptance, promote the new control and qualification
interfaces into role-named maintained documentation and tooling, retire only
superseded compatibility paths, update production policy, agree the release
version, package exact tested bytes, commit, tag, and publish under the normal
production procedure.

## Decision register

Q06-D00 — **Accepted 2026-09-30.** Resident EMOS owns and retains the
authoritative startup, foreground, mode/route and test-job lifecycle state. The
P4 may request a versioned snapshot and EMOS reports its own state; the P4 must
not synthesize EMOS state from keyboard delivery, pixels, elapsed time, or local
P4 service state. The request is read-only and conveys no control authority.

Q06-D06 — **Open; present first.** Select the physical/wire carrier for the
read-only state request. Recommendation: use the existing full-duplex r03 UART1
epoch. P4 GPIO12 is the sole driver toward Agon PC1/RXD1; Agon PC0/TXD1 is the
sole driver toward P4 GPIO22. Carry a private request in the P4→EMOS packet
stream and one whole framed response through EMOS's existing output serializer.
Do not repurpose RTS/CTS, transmit from an ISR, add a second UART owner, or permit
both processors to drive one conductor. If state must be queryable before EMOS
has admitted that UART epoch, define that requirement before deciding whether a
new wire is necessary.

Q06-D01 — **Open; wait for Q06-D06.** Should the bounded test-control capability be
present in the exact ordinary EMOS/P4 firmware submitted for acceptance, or only
in diagnostic builds? Recommendation: include the dormant, versioned capability
in ordinary firmware because qualification must exercise the exact candidate
bytes. Require a host-held P4 resource lease plus fresh EMOS safe-point
authorization for every job; do not give the P4 unilateral launch authority.
Record the network trust and enablement policy before implementation.

Q06-D02 — **Open; wait for Q06-D01.** Select the EMOS execution split.
Recommendation: keep lifecycle/admission state resident and launch a finite
`/emos/testjob.bin` supervisor in the existing MOSlet region. The contract must
prove that the supervisor can launch or supervise the required application
without overlapping a loaded program or nested MOSlet. If that memory contract
cannot be proven, return for a different design rather than deleting the guard.

Q06-D03 — **Open; wait for Q06-D02.** Select the result/progress ABI and the
minimum linked fixture helper. Recommendation: typed binary records over the
existing EMOS↔P4 private transport, with a tiny source-level helper for fixtures
and a supervisor-generated launch/return envelope.

Q06-D04 — **Open; wait for Q06-D03.** Select the host event interface.
Recommendation: one snapshot endpoint plus a resumable ordered event feed;
choose SSE, WebSocket, or bounded long-poll only after measuring the P4 HTTP
server's resource and reconnect behavior.

Q06-D05 — **Open; wait for Q06-D04.** Select migration and retirement dates.
Recommendation: keep QUAL-005 authoritative, migrate one physical case at a
time with old/new equivalence evidence, and switch authority only after one
complete accepted paired run.

## Validation gates

Q06-G01 [ ] A host can identify the exact live P4 and EMOS epochs/builds and
wait for a declared empty-CLI safe point without reading pixels or injecting a
probe command.

Q06-G02 [ ] A host can stage a content-addressed fixture, request its launch,
observe authorization, mode preparation, start, progress and terminal result,
and collect evidence without editing `/autoexec.txt` or resetting the Agon.

Q06-G03 [ ] The P4 rejects or explicitly resolves incompatible browser,
keyboard, video, storage and test-job ownership before launch. The runner never
asks the operator to perform hidden manual state cleanup.

Q06-G04 [ ] Lost events, peer restart, stale identity, foreground change,
application crash, missing fixture result, storage failure and cleanup failure
end in distinct typed dispositions with the last known authoritative state.

Q06-G05 [ ] Watchdog deadlines bound loss of communication but never serve as
evidence that EMOS is idle, a command ran, a fixture completed, or reset is safe.

Q06-G06 [ ] Every ordinary migrated case leaves the original startup bytes and
boot policy untouched. Every residual cold-boot case restores the exact prior
bytes on success and makes a bounded best-effort recovery with a retained
artifact on failure.

Q06-G07 [ ] Existing input, Legacy/ExCom, SD, video, loaded-asset, reset,
recovery, notification, and production-acceptance requirements remain passing.

## Non-goals

Q06-N01 — This task does not replace the MOS CLI, turn keyboard injection into
a command-completion API, expose unbounded remote memory/register access, or
let the P4 bypass EMOS ownership of mode, routing, activation, and launch.

Q06-N02 — This task does not eliminate every reset. Firmware flashing,
reset/recovery qualification, startup qualification, and unrecoverable fault
recovery retain explicit reset contracts.

Q06-N03 — This task does not infer production identity from Git HEAD, rebuild
installed firmware during qualification, or merge offline source regression
with installed-hardware acceptance.

Q06-N04 — This task does not repair unrelated P4/EMOS product defects merely
because the stronger state channel exposes them. File a bounded owner-specific
defect and preserve the control-plane evidence.
