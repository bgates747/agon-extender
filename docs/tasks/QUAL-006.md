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

The same facility supports routine production bug-report reproduction and bounded
feature proofs against exact firmware and diagnostic payload identities. It is
product infrastructure, not a diagnostic-build-only qualification runner.
Enablement, supported jobs and collected evidence are part of its product contract.

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
missing capabilities, and a proposed target architecture. The Author accepted
the architectural decisions and staged migration policy below; concrete transport,
resource bounds and wire/scheduling details remain before contract freeze.

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
existing UART carrier and post-admission availability boundary are accepted
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

Q06-07a [ ] Prove the accepted supervisor subset: bind each fixture manifest to
its code/data/heap/stack bounds and no-nested-MOSlet contract; reject missing or
incompatible declarations before load. Verify the supervisor slot, application
return path and existing busy/Core guards before admitting the first fixture.

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

## Offline contract review — 2026-10-13

The existing audit and work items cover the proposed control plane; a second
implementation task is unnecessary. The immediate deliverable is a bounded
accepted protocol contract, beginning with Q06-D06. No implementation decision
was accepted during this review, and no running qualification input was changed.

| Review item | Existing owner | Concrete gap before implementation |
|---|---|---|
| R01 — Wire and admission boundary | Q06-D06, Q06-04 | State whether observation begins only after EMOS admits the existing UART epoch. Do not promise pre-admission answers on an inactive link. |
| R02 — Response timing and execution context | Q06-04/05/06, Q06-G04/05 | Define which EMOS execution contexts can service queries, where a coherent snapshot is copied, which foreground serializer emits it, and how P4 reports unavailable/stale state. Existing storage receive code copies in interrupt context and makes decisions/sends in foreground; that alone does not prove timely answers during arbitrary applications. |
| R03 — Supervisor memory and launch | Q06-D02, Q06-07/08 | Prove the MOSlet/application memory and return contract before choosing the supervisor. Define load failure and return without a valid fixture terminal record. |
| R04 — Restart and event loss | Q06-04/06, Q06-D04 | Specify epoch binding, event retention bounds, gap disposition and reconnect reconciliation. A reconnect must not resubmit an uncertain job. |
| R05 — Scope and migration | Q06-02/10/11/13 | Freeze one observation-only tranche before adding remote launch. Keep current suites authoritative and leave their pinned inputs unchanged during an active run. |

The current multimode host now supports initial listener admission and staged
startup replacement. Those are bounded runner repairs, not an EMOS lifecycle
service: host keyboard delivery still does not identify the eZ80 foreground.
The September audit remains a dated baseline, not a statement that every old
launch pattern persists unchanged in October. Its historical observations should
not be rewritten as fresh hardware evidence.

The first proposed tranche is observation only: resident EMOS retains lifecycle
state, answers bounded read-only queries over the admitted UART epoch, and P4
reports the response's epoch and freshness. No job launch, cancellation, reset,
mode selection, event-feed technology or fixture ABI is selected by accepting
that carrier. Existing UART ownership and whole-record serialization must be
proved against a refreshed implementation baseline before source changes.

For Q06-D06, recommend existing UART after explicit Extender admission. The
alternative is a requirement for pre-admission observation, which needs separate
bootstrap/transport analysis and may require hardware changes. Do not select a
new conductor without establishing that earlier observation is needed. Rejected
or unanswered queries grant no authority to recover or reset the Agon.

### Supervisor memory review — 2026-10-13

Official `agon-docs/docs/mos/Executables.md` distinguishes the conventional
application address 0x040000 from the MOSlet slot at 0x0B0000 (under 32 KiB),
but a simple MOS header does not declare a program's complete memory footprint.
The project-owned `agon-emos/src/emos.c::emos_run_utility` explicitly loads
utilities into that slot and rejects busy/non-Core entry and oversized files.
Its adjacent admission path explicitly forbids loading another utility into a
running application. These existing guards must survive a test supervisor.

Separate load addresses alone do not prove that an arbitrary fixture's code,
data, heap, stack or nested utility calls leave the supervisor slot untouched.
Q06-D02 therefore needs either a manifest-bound, independently checked
memory-safe fixture subset with no nested MOSlet load, or a different execution
split. Do not authorize arbitrary games/applications on the strength of a MOS
header or current executable size. No generic supervisor launch compatibility
has been proved by this bounded source/document review.

## Decision register

Q06-D00 — **Accepted 2026-09-30.** Resident EMOS owns and retains the
authoritative startup, foreground, mode/route and test-job lifecycle state. The
P4 may request a versioned snapshot and EMOS reports its own state; the P4 must
not synthesize EMOS state from keyboard delivery, pixels, elapsed time, or local
P4 service state. The request is read-only and conveys no control authority.

Q06-D06 — **Accepted 2026-10-13.** Read-only lifecycle queries use the
existing full-duplex r03 UART1 transport after explicit EMOS Extender admission.
P4 sends the private request on its existing transmit direction; EMOS emits one
whole framed response through its sole output serializer between complete
VDU/service records. RTS/CTS retain flow control. No second UART owner, ISR
transmission, additional conductor or pre-admission response is selected.
Before admission, P4 reports EMOS state unavailable; silence grants no control
or reset authority. Query scheduling, coherent snapshots, framing and freshness
remain protocol prerequisites under Q06-04/05/06 and review item R02.

Q06-D01 — **Accepted 2026-10-13.** Include the dormant, versioned bounded
test-control capability in ordinary EMOS/P4 firmware so qualification exercises
the exact candidate bytes proposed for release. Every test job requires a
host-held P4 resource lease and fresh EMOS safe-point authorization; P4 never
acquires unilateral launch authority. Inclusion is not enablement or deployment.
Network trust/enablement policy, resource budgets and regression qualification
remain implementation prerequisites under Q06-04/06/13.

Q06-D02 — **Accepted 2026-10-13.** Keep lifecycle and admission state
resident in EMOS and use a finite SD-loaded `/emos/testjob.bin` supervisor in
the existing MOSlet slot. Initially support only manifest-bound fixtures whose
code, data, heap and stack are independently proved not to overlap that slot
and which never load another MOSlet. Preserve existing busy/Core, size and
nested-load guards. EMOS rejects unsupported or unproved fixtures before launch;
a MOS header or executable size alone is insufficient. Broader application
support requires a separately proved memory/return contract or a different
execution split. No generic application compatibility is accepted by this choice.

Q06-D03 — **Accepted 2026-10-13.** Fixtures use a small linked
source-level helper to submit typed binary start, progress, assertion and
completion records through resident EMOS over the existing private transport
to P4. EMOS validates each record against the active job grant; every record is
bound to peer epochs, foreground generation, job identity, exact fixture hash
and result schema. Fixtures do not acquire a private UART writer or bypass EMOS.
The supervisor supplies the launch/return envelope and reports load/launch
failure, invalid records and return without valid completion as non-pass
outcomes. Large evidence remains separately referenced artifacts. Exact layouts,
size/rate bounds and backpressure are protocol work under Q06-04/08.

Q06-D04 — **Accepted 2026-10-13; selected transport under Q06-D04-T01.**
Provide one current-state snapshot endpoint plus an ordered event feed that
resumes after the host's last received event sequence. Bind events to peer
boot/link identities and foreground/job generations. On peer restart or a
retention gap, the host obtains a fresh snapshot and explicitly reconciles
state; reconnect never automatically relaunches or resubmits uncertain work.
This accepts the interface semantics, not an HTTP transport or retention size.

Q06-D04-T01 — **Accepted 2026-10-13; hardware qualification pending.**
Use asynchronous bounded long-poll with one outstanding reader request, one
bounded worker and explicit SDK request completion on every success/error exit.
The shared HTTP handler returns immediately; event waits and slow sends must not
run on that task. The host receives bounded batches and reconnects using its
validated cursor. Qualify stack/heap, shared-service latency, exhaustion,
disconnect cleanup and reconnect gaps on both DevKit and PC before promotion.
Source inspection establishes implementation feasibility, not measured capacity.
No resource measurements are authorized on the active benchmark bench.

Q06-D05 — **Accepted 2026-10-13.** Keep QUAL-005 authoritative while
migrating one physical case at a time. Each migrated case must preserve or
strengthen its oracles and retain old/new equivalence evidence. Switch authority
and retire only replaced maintained paths after a complete old/new comparison
passes against the same independently verified firmware pair and the Author
accepts the migration. Retirement is evidence-gated, not calendar-driven.
Historical evidence remains preserved. This does not authorize interrupting,
modifying or replacing an active qualification campaign.

Q06-D07 — **Accepted 2026-10-13.** Ordinary production firmware starts
with diagnostic job execution disabled. An explicit operator command in EMOS
enables it only for the current EMOS boot; reboot restores disabled state.
Host-controlled execution additionally requires a P4 host lease and a fresh
EMOS safe-point grant for each supported job. Read-only lifecycle status remains
available after ordinary Extender admission without enabling diagnostic execution.
This supports production bug reports and bounded feature proofs, not unattended
remote activation of diagnostics. Command syntax, disable-during-job behavior,
network access policy and evidence export details remain contract work.

Q06-D08 — **Accepted 2026-10-13, both supported boards.** P4 retains a
bounded durable terminal journal on its own SD card; the host exports the full
evidence bundle. P4 retains uncollected terminal records until the host verifies
and acknowledges required evidence. Unavailable/full journal storage rejects new
diagnostic jobs; it does not disable ordinary EMOS/P4 use or read-only status.
Use board-profile-selected storage for P4-DevKit and P4-PC, not a PC-only path.
Exact persistence/recovery format, storage lease integration and resource bounds
require qualification on each board. The Author explicitly reaffirmed DevKit
coverage and recalled its SD slot; no board is dropped from scope.

## Next contract tranche — offline only

The main architectural choices are accepted. Q06-02 remains incomplete until
transport implementation proof, network access/enablement details, scheduling and protocol bounds are
resolved and the accepted implementation contract is frozen. Drafting and source
review do not grant firmware implementation or deployment authority.

### Board and journal scope

The [P4 SD guide](../p4-sd.md) records bounded DevKit local-card checks and
separate board power lifecycles. Both maintained board profiles declare SDMMC
configuration. Those facts support a common storage abstraction, not a claim
that the new journal is qualified. Q06-06/13 must cover missing/full media,
interrupted journal writes, restart recovery, acknowledgement/reclamation and
storage-owner contention on both DevKit and PC. DevKit browser video/input
resource use must be included; HDMI-only measurements cannot substitute for it.

### HTTP resource review — 2026-10-13

| Source observation | Evidence | Design consequence to verify |
|---|---|---|
| Shared HTTP configuration defaults to seven sockets and 4096-byte task stack | `vdp/video/extender/network/http_video_service.hpp::HttpVideoConfig` | Account for event clients together with existing browser and HTTP clients; do not assume a spare unlimited connection pool. |
| HTTP startup disables LRU socket purging and installs explicit open/close hooks | `http_video_service.cpp::startServer` | Specify event-client admission, disconnect cleanup and bounded lifetime rather than relying on eviction. |
| Browser keyboard is already a WebSocket route on the shared server | `wired_network_service.cpp::startHttp` | WebSocket support exists, but that alone does not prove sufficient resources or correct event reconnect semantics. |
| P4 telemetry already copies a latest snapshot under a short critical section | `vdp/video/extender/telemetry/target.hpp` | Review reuse for coherent copy mechanics; application-published telemetry is not automatically authoritative EMOS lifecycle state. |

These are source/configuration observations, not measured installed runtime
limits. A synchronous event wait or long-lived response on the shared request
task risks delaying unrelated handlers; the selected implementation must prove
bounded/asynchronous dispatch and client cleanup. Asynchronous bounded long-poll is selected under Q06-D04-T01; its resource
and cleanup qualification still requires separately authorized physical work.

### Working protocol draft

[Protocol draft](QUAL-006/PROTOCOL-DRAFT.md) now specifies transport-independent
snapshot/event fields, authority and freshness, query scheduling, job states,
duplicate/restart handling, deferred artifacts and offline fault cases. Its
queue/client/enablement proposals are unaccepted review targets. The transport
comparison records existing source constraints without selecting a winner or
claiming measured P4 capacity. The concrete-proposal section adds operator
command syntax, disable-pending behavior, candidate private framing and fragment
bounds, a 208-byte bound fixture envelope, queue/client/watchdog targets and
explicit evidence-export/acknowledgement semantics. Arithmetic/link checks pass;
wire assignments and capacity remain unaccepted proposals. Host transport and terminal persistence are now selected; concrete wire and
journal proposals remain subject to parser, memory and recovery proof. Q06-02/Q06-04 remain incomplete; the draft is not
a frozen implementation contract and changes no running-suite input.

### Feasibility disposition — 2026-10-13

[Offline feasibility review](QUAL-006/PROTOCOL-FEASIBILITY.md) completes the
parser, supervisor, retained ROM and P4-map pass. Accepted architecture remains
viable as a staged target, but full implementation fit is unproved. Early QC
routing must precede SD mailboxes; supervisor context must survive application
entry/return; the existing IRQ telemetry transmitter cannot be reused under the
no-ISR-transmission contract. Retained ordinary ROM headroom is only a few KiB,
with substantially less in distinct experimental compositions. P4 map spans are
not runtime allocation proof and PC HDMI evidence cannot replace DevKit evidence.

Next prepare a selected observation-only baseline and ROM/RAM cost study through
owner wrappers, plus parser regression cases and a later supervisor lifecycle
plan. Do not freeze or deploy the full contract based on arithmetic or old map
capacity. No implementation/build/bench work occurred in the feasibility review.

### Protocol drafting checklist

1. Define snapshot/event logical fields and unknown/stale reasons independently
   of SSE, WebSocket or long-poll framing.
2. Bind the snapshot to both peer identities, link and foreground generations;
   bind fixture records to the granted job, fixture hash and result schema.
3. Define query coalescing, coherent state copying and a single EMOS reply owner
   without ISR transmission or VDU-record interleaving.
4. Specify fixed event retention, event/client limits, wrap/restart behavior and
   explicit gap reconciliation. No reconnect-triggered job replay.
5. Specify job offer/grant/launch/return/cleanup transitions and distinct failures,
   including unproved fixture memory, missing terminal record and storage errors.
6. Define the host lease's enablement/trust boundary and ownership conflicts;
   inclusion in ordinary firmware must not silently activate remote job control.
7. Build offline state-machine and reconnect fault cases before scheduling a
   hardware resource comparison or the first observation-only firmware tranche.

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
