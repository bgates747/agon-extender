# QUAL-006 automated hardware-test audit

## Audit result

The maintained qualification process has strong artifact identity, destructive-
test caution, exact startup preservation, durable summaries, and real hardware
oracles. Its control model is nevertheless fragile because the host can observe
P4-side transport and rendering state but cannot observe EMOS's authoritative
foreground lifecycle. The host therefore converts weak observations into
execution claims:

- P4 keyboard acceptance is treated as a proxy for EMOS command execution;
- sampled screen text is used as a parser and prompt-progress barrier;
- appearance of the foreground SD listener is used as a command-completion cue;
- `/autoexec.txt` plus reset is used to obtain deterministic fixture launch;
- result files and a second listener session are used to learn that a fixture
  returned; and
- fixed deadlines bound waits whose expected state is otherwise unknown.

Those are not merely untidy scripts. They are compensations for missing product
capabilities: no EMOS lifecycle/state service, no correlated remote command or
job completion, no generic finite fixture admission, no standard test-result
channel, no cross-service resource lease, and no resumable state/event feed.
The clean repair is to add those capabilities, then simplify the runners. More
screen scraping, longer sleeps, and increasingly defensive startup rewrites
would preserve the underlying ambiguity.

The current development source already supplies a valuable architectural seed.
REMOTE-005 lets the P4 offer a finite storage job while resident EMOS authorizes
it only at an empty top-level CLI safe point and launches `/emos/sdjob.bin`.
QUAL-006 should generalize that admission and identity machinery; it should not
create a competing remote-launch owner.

On 2026-09-30 the Author settled the state owner: resident EMOS must retain the
authoritative lifecycle state and answer an on-demand P4 query. The query is not
a command grant. Its carrier remains an explicit task decision; the existing
r03 UART1 data lanes are the recommended no-rewire path because each direction
has exactly one electrical driver during a committed UART epoch.

## Scope and method

Q06-A01 — The audit traced `qualification/run.py`,
`qualification/performance.py`, `qualification/manifests/`, shared helpers under
`scripts/`, the current reset/keyboard/SD HTTP clients, P4 HTTP and display
endpoints, P4 storage admission, EMOS CLI/editor and program lifecycle, EMOS
finite admission, the accepted QUAL-005 contract, active bench constraints, and
relevant REMOTE-005 research.

Q06-A02 — The audit read official Agon `MOS.md`, MOS API, star-command and
executable documentation at official-docs commit
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, then used official MOS v3.0.2 and
official VDP v2.16.0 source only where implementation detail was material. The
official projects provide CLI, executable, API and VDU contracts; they do not
provide a stock remote supervisor or fixture-result protocol.

Q06-A03 — The audit did not execute hardware, edit startup, flash firmware, or
change any control path. It reviewed current source and retained evidence. The
baseline identities are recorded in the parent task.

## Research and source map

Q06-A04 — Official contracts reviewed first:

- [MOS overview](../../../../../agon-docs/docs/MOS.md) for startup and CLI
  ownership;
- [MOS API](../../../../../agon-docs/docs/mos/API.md) for OSCLI/editor and
  application-visible services;
- [MOS star commands](../../../../../agon-docs/docs/mos/Star-Commands.md) and
  [executable format](../../../../../agon-docs/docs/mos/Executables.md) for
  command and launch behavior; and
- [VDU commands](../../../../../agon-docs/docs/vdp/VDU-Commands.md) and
  [screen modes](../../../../../agon-docs/docs/vdp/Screen-Modes.md) for mode
  selection and display ownership.

Q06-A05 — Maintained implementation and operating authorities traced:

- [canonical qualification policy](../../../qualification/README.md),
  [installed runner](../../../qualification/run.py),
  [performance runner](../../../qualification/performance.py), and
  [hardware manifest](../../../qualification/manifests/hardware.json);
- [shared hardware helpers](../../../scripts/hardware_validation.py),
  [keyboard client](../../../scripts/keyboard.py),
  [reset helper](../../../scripts/reset_agon.py), and
  [SD client](../../../scripts/sdcard.py);
- [P4 network endpoints](../../../vdp/video/extender/network/wired_network_service.cpp),
  [sampled text endpoint](../../../vdp/video/extender/network/screen_text.hpp),
  [display status](../../../vdp/video/extender/network/display_status.hpp), and
  [storage admission](../../../vdp/video/extender/storage/admission/peer.hpp);
- [EMOS admission](../../../../agon-emos/src/emos_admission.c),
  [EMOS lifecycle/utility loader](../../../../agon-emos/src/emos.c), and
  [EMOS contract](../../../../agon-emos/docs/emos-v1-contract.md); and
- [REMOTE-005 admission contract](../REMOTE-005/ADMISSION-CONTRACT.md) and
  [source review](../REMOTE-005/ADMISSION-REVIEW.md).

The relative links to sibling owner/reference checkouts are development-workspace
links; the exact revisions in the parent task remain the identity authority.

## Current maintained process map

| Phase | Requesting actor | Executing actor | Present synchronization/evidence | Principal weakness |
|---|---|---|---|---|
| Verify installed inputs | Host runner | Host receipt parser | Verified P4/EMOS flash receipts | Strong identity evidence, but live peer identity is not one unified runtime snapshot |
| Reset/readmit | Host runner through the bench Pi reset circuit | Agon mainboard and EMOS; P4 observes keyboard admission | Fresh `/keyboard/status` boot epoch, ready and neutral flags | Proves P4 input admission, not EMOS startup completion, prompt state, route, or foreground |
| Routine CLI setup | Host runner through P4 key injection | EMOS editor/parser | P4 event drain; sometimes fresh `/screen/text` | Drain proves delivery only; screen text is sampled framebuffer content, not command acknowledgement |
| Stage files | Host runner | Foreground `EMOS sdserve`, EMOS SD gateway, P4 HTTP SD endpoint | Poll `/sd/status`; transfer IDs, hashes and readback | Listener must first be launched through the ambiguous CLI path and monopolizes the foreground |
| Launch integrated smoke actions | Host runner | EMOS CLI and P4 display services | Text markers, display status, WebSocket frames, SD round trip | Useful bounded oracles, but command ordering still depends on screen/prompt heuristics |
| Launch raw-SD fixture | Host runner modifies SD startup, then bench Pi pulses reset | EMOS startup and fixture application | One-shot `/autoexec.txt`, ExCom marker, reset | Mutates persistent boot state and needs a reboot only to obtain deterministic execution |
| Detect raw-SD completion | Fixture, then host runner | Fixture returns to MOS; host types listener command | Result token and later prompt pixels, then `/sd/status` | Stale pixels can masquerade as a current prompt; no authoritative foreground generation or terminal event |
| Launch performance cases | Host runner modifies SD startup for each case, then resets | EMOS startup and fixture | One-shot `/autoexec.txt`, result listener, video observation | Repeated startup mutation/reset magnifies recovery cost and contaminates performance setup |
| Restore startup | Host runner through foreground listener | EMOS/P4 SD service | Exact bytes, readback, backup resolution | Strong transaction once the listener is available; failure can remove the very channel needed for recovery |
| Notify | Host runner | Terminal and admitted MOS CLI | Durable summary, visible/spoken cue | Correctly suppressed in unknown destructive foreground, but that unknown state is common because no lifecycle service exists |

The source-build/offline suite is separate and does not use this hardware
control path. Firmware flashing is also separate: it builds and verifies exact
bytes, resets where installation requires it, and produces receipts. Neither is
the cause of the routine fixture-launch problem.

## Findings

| ID | Severity | Finding | Consequence |
|---|---:|---|---|
| Q06-F01 | Critical | No actor exposes authoritative EMOS startup/foreground state | The host cannot distinguish idle CLI, edited line, command, MOSlet, application, failed startup, or unknown foreground |
| Q06-F02 | Critical | Key injection has delivery acknowledgement but no command lifecycle | Accepted keystrokes can be lost to timing, consumed by another foreground, rejected, or still pending when the next action starts |
| Q06-F03 | High | Routine fixtures use persistent startup mutation plus reset as a launcher | A functional test can alter boot policy, require minutes of recovery, or strand the bench when cleanup cannot start |
| Q06-F04 | High | Completion/result collection depends on returning to a guessed prompt and launching another foreground listener | The runner cannot safely tell crash, slow execution, returned application, stale framebuffer, or listener-start failure apart |
| Q06-F05 | High | Browser, video observer, remote keyboard, manual SD service, admitted job and test runner have no common resource lease | A disconnected-looking page, retained socket, or competing owner can change timing or block a service without an atomic preflight |
| Q06-F06 | High | Polling deadlines and screen heuristics substitute for state transitions | Longer waits hide protocol defects; shorter waits create nondeterministic infrastructure failures; neither proves safety |
| Q06-F07 | Medium | Path and artifact assumptions are validated incrementally after mutation begins | Missing repositories, fixtures, optional endpoints, SD directories, or capabilities can leave startup altered before a run rejects them |
| Q06-F08 | Medium | Failure handling is script-specific and sometimes ends as a traceback or broad infrastructure error | The operator receives poor state diagnosis and recovery ownership varies by path |
| Q06-F09 | Medium | The active fixture constraint conflates recovery/cold-boot setup with every fixture | Even trusted admitted P4 control is forbidden from selecting mode immediately before an ordinary launch, preserving unnecessary reboots |
| Q06-F10 | Medium | Fixtures have no standard progress/result/cancellation ABI | Each test invents markers, result files, magic colours, listener handoffs and timeout interpretation |
| Q06-F11 | Medium | Reset is used as state normalization rather than only as an operation under test or recovery boundary | Resets consume time, disturb peer epochs and connections, and can mask lifecycle cleanup defects |
| Q06-F12 | Medium | P4 and EMOS live identities, epochs, route/mode, foreground and clients are not one coherent snapshot | A receipt can identify installed bytes while the runner still acts on stale or partial runtime relationships |
| Q06-F13 | Low | Historical task launchers coexist with the canonical `qualification/` authority | Discovery can select frozen or compatibility code unless the operator begins from current documentation |

### Q06-F01 — missing EMOS lifecycle authority

`/keyboard/status` reports the P4 remote-input session, delivery counters,
neutrality and admission readiness. `/display/status` reports P4 output geometry,
colour depth, refresh and buffering. `/sd/status` reports the foreground SD
service's availability. `/screen/text` samples rendered text and can explicitly
return changing/incomplete content. None identifies what the eZ80 is executing.

This distinction explains several retained failures: input batches were accepted
before prior commands completed; the SD listener did not start while ExCom owned
the foreground; old prompt pixels survived after the true foreground changed;
and an Agon reset advanced a P4 epoch without restoring ready admission. Each
observation was real, but no endpoint could state the EMOS lifecycle fact the
runner needed.

### Q06-F02 — delivery is not execution

`scripts/hardware_validation.py::type_line` waits for a ready/neutral P4 input
session, sends key events and closes the session. The P4 can truthfully report
emitted, accepted, discarded and pending events. EMOS does not attach a command
ID, accepted/executing/completed state, return code, or output boundary to those
events. Fresh screen capture has been used as a practical parser-progress
barrier, but it is not an execution protocol.

Keyboard injection remains valuable for human control, recovery, and tests of
interactive input. Automated setup should use structured jobs or commands with
EMOS-generated lifecycle events.

### Q06-F03 — startup mutation is a compensation, not a requirement

The destructive RP04 and every performance case download the original startup,
write a one-shot `/autoexec.txt`, verify it, stop the listener, and reset the
Agon. This guarantees ordering before an application receives control and
worked when startup was the only noninteractive input. With admitted P4 input it
is no longer the clean default, but key injection alone still cannot safely
replace it because Q06-F01 and Q06-F02 remain.

Exact preservation/readback and conservative refusal to reset an unknown raw-I/O
foreground are good controls. They reduce harm; they do not make persistent boot
mutation an appropriate ordinary launcher.

### Q06-F04 — circular completion and recovery

The fixture writes a result file, returns, and the host tries to prove that
return from framebuffer markers before typing a command that opens the SD
listener needed to retrieve the result and restore startup. If any link fails,
the runner may lack the service required to restore the bytes it changed.

A modern fixture must emit a bound terminal record over the already admitted
control transport. Storage may retain large evidence, but it must not be the
sole source of truth that execution ended safely.

### Q06-F05 — no cross-service resource lease

The current endpoints each know part of their own state. The runner cannot
atomically claim “qualification owns keyboard commands, one declared video
observer, no browser keyboard owner, no manual SD listener, and one finite EMOS
job.” Operator instructions to disconnect a browser and P4 resets that close
sessions are workarounds for missing arbitration.

The P4 should own the network-side lease and report conflicts. EMOS must still
own launch authorization and foreground safety; a P4 lease cannot override a
busy or incompatible EMOS state.

### Q06-F06 — deadlines are watchdogs, not facts

Polling is not inherently wrong. A monotonic deadline is still required to
bound a dead peer or lost event. The error is using elapsed time or the absence
of an endpoint as evidence of what the eZ80 is doing. A state-driven runner
waits for a correlated transition and uses the deadline only to report that the
transition did not arrive, including the last authoritative state.

### Q06-F07 — incomplete preflight

The runners correctly bind commits and receipts, but some repository siblings,
fixture builders, SD destinations, optional P4 endpoints and runtime
capabilities are discovered only as a case proceeds. A performance attempt, for
example, changed startup before discovering an optional diagnostics route was
absent. All immutable dependencies and capabilities must be resolved before
staging; staged fixtures should carry content hashes rather than depend on an
implicit checkout location.

Machine-specific paths belong in the ignored bench configuration. Maintained
code should accept configured component repositories and reject missing/wrong
revisions in a single preflight report rather than infer sibling layout.

The material current assumptions are:

| Assumption | Current location | Disposition |
|---|---|---|
| P4 URL, reset URL, EMOS repository, MOS builder/toolchain, FabGL tree and exact P4 device access exist | Ignored qualification configuration | Keep machine-local configuration, but validate every field and capability in one read-only preflight |
| Nurples source is the sibling `../nurples-repair` unless overridden | `qualification/performance.py` | Remove the positional default from unattended acceptance; require a manifest/configured repository and exact commit |
| Qualification fixture and result directories already exist at fixed SD paths | `qualification/run.py`, `qualification/performance.py` | Keep the approved SD-layout namespaces, but query/create them through an admitted storage transaction before changing startup or launching work |
| RP04 source is recoverable from the EMOS flash receipt's component snapshot | `qualification/run.py` | Keep receipt binding; preflight the snapshot, fixture source, toolchain and output hash before touching the bench |
| Optional P4 diagnostic routes can be discovered during a case | `qualification/performance.py` retained failure/correction | Probe every optional capability before staging; record a supported fallback or reject before mutation |
| Foreground `sdserve` can be started after typed setup | shared runner flow | Replace with finite safe-point storage admission; never infer CLI availability from keyboard readiness |
| Browser disconnection is operator-maintained when video diagnostics are absent | performance runner | Replace with P4 client/resource inventory and an explicit lease/conflict result |

### Q06-F08 — inconsistent failure semantics

The canonical runner has meaningful categories—test failure, infrastructure
error, timeout, blocked, and unsafe mainboard state—and preserves detailed
evidence. Lower-level helpers still raise raw exceptions, and recovery ownership
is distributed among callers. The modern runner needs typed phase/state/job
errors, one terminal cleanup path, and a durable final snapshot even when cleanup
fails. A traceback may be retained as diagnostic detail, not used as the only
operator report.

### Q06-F09 — overbroad fixture-mode rule

The active bench constraint rightly forbids a fixture from changing its own mode
and rightly requires a noninteractive path when input admission itself is under
test. Its present wording requires every fixture mode to be selected only from
`/autoexec.txt`. After a trusted EMOS supervisor exists, EMOS can select the
declared mode immediately before transferring control to an ordinary fixture
without weakening either principle. Cold-boot and input-candidate tests retain
the existing rule.

### Q06-F10 — bespoke fixture protocols

The current fixtures use different combinations of screen markers, colour
frames, result files, ticks, row limits, prompt return, and listener appearance.
The result is difficult to compose and diagnose. A small common ABI should bind
begin/progress/assert/end records to a granted job. Large files, screenshots,
and performance samples can remain separate artifacts referenced by hashes.

### Q06-F11 — reset overuse

Reset is appropriate after flash, when reset behavior is being qualified, for
first admission/recovery, and when an accepted recovery policy declares the
foreground disposable. It should not be the ordinary transition between two
well-behaved fixtures. A supervisor should return EMOS to a declared idle state
and expose cleanup failure instead of hiding it with a reboot.

### Q06-F12 — fragmented identity and state

The flash receipts are strong immutable evidence. Runtime endpoints separately
report P4 boot or service state, but the host lacks a single snapshot binding
P4 boot/build, EMOS boot/build, transport generation, EMOS foreground generation,
route/mode, P4 committed display generation, resource owners and current job.
Without it, stale state across one-sided resets is difficult to reject.

### Q06-F13 — historical discovery noise

Current documentation clearly makes `qualification/` authoritative, yet frozen
task scripts and compatibility launchers still contain executable-looking
startup patterns. They should remain evidence, not be bulk rewritten. Maintained
entry points should declare themselves and historical scripts should carry
machine-readable or prominent archival status where ambiguity remains.

## Retained strengths

Q06-R01 — Verified flash receipts bind installed artifacts to exact commits and
independent readback. The new control plane should consume, not replace, them.

Q06-R02 — QUAL-005 refuses a zero-case or offline-only hardware acceptance and
separates build, flash, installed behavior, performance and human evidence.

Q06-R03 — Startup preservation uses exact bytes, independent readback and
retained sibling-backup cleanup. Residual cold-boot cases should retain this
transaction.

Q06-R04 — Destructive RP04 refuses input/reset when raw-media restoration is
unknown. A future “safe to reset” bit must be supplied by the owning EMOS job;
the host must not infer it.

Q06-R05 — The runner records case/check durations, typed dispositions, summaries
and terminal notification. Event-driven control should improve these records,
not discard them.

Q06-R06 — Keyboard, SD and display endpoints already expose useful bounded
transport/output state. They remain observers and data paths under the new
lifecycle authority.

Q06-R07 — REMOTE-005 already implements job identities, generations, grants,
finite completion and EMOS safe-point authorization for storage work. This is
the preferred seed for generic test jobs.

## Missing capabilities

| Capability | Current closest mechanism | Gap to close | Proposed owner |
|---|---|---|---|
| Live component identity | Flash receipts; P4 build logs | No bound live P4+EMOS snapshot | EMOS publishes its build/boot; P4 publishes both with peer generations |
| Authoritative foreground state | Keyboard, display, screen and SD status | None describes eZ80 execution | Resident EMOS state machine |
| Correlated command/job completion | P4 key-event counters | No EMOS acceptance, start, return or status | EMOS job supervisor and result ABI |
| Safe remote launch | One-shot startup; storage-only `sdjob` admission | Generic finite fixture launch absent | Generalized EMOS admission, offered by P4 |
| Structured progress/results | Files, pixels and prompt markers | No shared schema or job binding | Fixture helper → EMOS → P4 journal |
| Resource arbitration | Per-endpoint busy/offline state | No atomic multi-service claim | P4 resource lease plus EMOS launch decision |
| Resumable state events | Repeated HTTP polling | No ordered event cursor after reconnect | P4 snapshot and event feed |
| Cooperative cancellation | Escape in selected foreground utilities | No declared fixture capability/safe point | Fixture/supervisor contract, EMOS reports capability |
| Preflight | Manifests and per-step validation | Some dependencies discovered after mutation | Host runner with P4/EMOS capability snapshot |
| Recovery truth | Conservative host heuristics | No owner-declared reset/cleanup safety | EMOS job state and terminal disposition |

## Proposed architecture

### Q06-P01 — one control plane, three authorities

The host runner requests and records work. The P4 owns network sessions,
resource leases, job offers, event retention, and transport to EMOS. EMOS owns
whether the eZ80 is at a safe CLI boundary, mode/routing preparation, fixture
launch, foreground lifecycle, and whether cancellation/reset is safe. The
fixture owns its functional assertions and cooperative progress.

No actor may promote another actor's observation into authority. In particular,
the P4 may not launch merely because its keyboard session is ready; the host may
not declare completion merely because pixels resemble a prompt; and a fixture
may not bypass EMOS to commit an ordinary mode.

The read-only state request does not weaken this ownership. P4 requests a
snapshot; resident EMOS creates the report from its own lifecycle state. A
request never means “enter a state,” and the absence of a reply leaves state
unknown rather than authorizing recovery or control.

### Q06-P01a — recommended no-rewire request path

The active r03 UART wiring already provides separate, single-driver conductors:
P4 GPIO12 transmits to Agon PC1/RXD1, while Agon PC0/TXD1 transmits to P4
GPIO22. The P4 can therefore send a private state-query packet on its existing
transmit direction and EMOS can queue a framed reply on its existing transmit
direction. Neither processor electrically drives the other's transmit wire.

RTS and CTS must retain flow-control meaning; neither is a state-request strobe.
The EMOS receive ISR may validate and record a bounded query but must not emit a
reply itself. The existing EMOS foreground/serializer owner must insert one
complete private response between complete VDU/service records so state traffic
cannot interleave with application output.

This recommendation is conditional on an admitted UART epoch. Cold Legacy boot
currently starts with mainboard input and does not promise that the Extender
UART service is already active. QUAL-006 must decide whether “on demand” begins
after explicit Extender admission—which is sufficient for ordinary automated
tests—or is required before that point. Only the latter would justify examining
an additional wake/request conductor.

### Q06-P02 — runtime snapshot

The P4 should expose one versioned snapshot containing at least:

| Group | Required fields |
|---|---|
| P4 identity | Build ID, immutable source/artifact identity, P4 boot epoch, protocol versions |
| EMOS identity | Build ID, EMOS boot epoch, negotiated link generation, last-seen age |
| EMOS lifecycle | Startup phase/result, foreground phase/generation, command or job ID, program identity when known, safe-to-cancel/reset flags |
| Input | Selected EMOS source, admission state/reason, P4 keyboard owner, pending/held/neutral counters |
| Display | EMOS route/mode intent and generation; P4 committed mode/geometry/depth/generation |
| Storage | Manual listener state, admitted finite job state, media owner, recovery-required state |
| Clients/resources | Browser video clients, browser keyboard owner, diagnostic observer, host test lease, conflicts |
| Terminal history | Last terminal job ID/result and ordered event sequence retained for reconnect |

Unknown must be a first-class value with a reason and age. The P4 must clear or
mark stale all EMOS-owned fields when the EMOS link generation changes.

### Q06-P03 — lifecycle vocabulary

EMOS should publish a small mutually exclusive foreground phase rather than a
large collection of inferred booleans:

| Phase | Meaning | Ordinary host action |
|---|---|---|
| `booting` | EMOS has not completed core initialization | Observe only; watchdog may report lost boot |
| `startup-running` | Startup file is executing | Observe; do not offer routine jobs |
| `startup-error` | Startup stopped with line/status evidence | Report; recovery policy decides next action |
| `cli-idle` | Empty top-level EMOS CLI is eligible for an admitted job | P4 may present one pending job offer |
| `cli-editing` | User has a nonempty line or editor activity | User wins; reject/defer job without replay ambiguity |
| `command-running` | CLI command owns the foreground | Observe correlated command if structured; no new job |
| `utility-running` | MOSlet/service owns the foreground | Report utility/job identity and cancellation capability |
| `application-running` | Application owns the foreground | Report identity when launched by supervisor; otherwise explicit unknown application |
| `recovery-required` | EMOS knows ordinary continuation is unsafe | Preserve evidence; permit only accepted recovery operations |

Transport unavailable is a relationship state, not a fabricated foreground
phase. EMOS must remain usable in Legacy without the P4.

### Q06-P04 — finite job flow

Q06-P04a — The host preflights receipts, live identities, capabilities,
artifacts, paths, cleanup policy and resource conflicts before mutation.

Q06-P04b — The host uploads or identifies a content-addressed fixture and posts
a bounded job descriptor to the P4. The descriptor declares fixture hash/path,
working directory, arguments, required mode/route, result ABI, resource needs,
timeout/watchdog policy, destructive scope, cancellation capability and cleanup.

Q06-P04c — The P4 acquires a network-side test lease and offers the job through
the generalized REMOTE-005 channel. The P4 does not self-authorize it.

Q06-P04d — At `cli-idle`, EMOS validates capabilities, atomically grants the
exact job, publishes the new foreground generation, selects the declared mode,
and launches the supervisor/fixture. A pending key or foreground change wins and
retires the offer.

Q06-P04e — The fixture helper reports begin, progress, assertion and terminal
records. EMOS validates the active binding; the P4 journals records and exposes
them to the host event feed. The supervisor reports launch failure or an
application return that lacks a terminal record as distinct non-pass results.

Q06-P04f — EMOS performs the accepted cleanup, returns to `cli-idle`, and emits
the terminal state. The P4 releases resources. The host stores the event journal
and referenced artifacts. No reset or startup rewrite occurs on the ordinary
path.

### Q06-P05 — event-driven waits

The host should first read a snapshot, then subscribe with the current event
sequence. Each event must carry P4 boot epoch, EMOS boot/link generation,
foreground generation and job ID where applicable. Reconnect resumes after the
last sequence when retained; otherwise the host reads a fresh snapshot and
explicitly reconciles a gap.

Every wait retains a monotonic watchdog. On expiry the runner reports “expected
event X did not arrive; last authoritative phase was Y at generation Z,” not
“the application must still be running” or “reset is probably safe.”

### Q06-P06 — files and paths

The finite storage-admission path should stage fixtures while EMOS is idle,
without typing `EMOS sdserve`. The runner should address an approved qualification
namespace using a manifest and hashes. Machine-local repositories and toolchains
remain configured inputs; the runner validates their exact revisions and all
fixture dependencies before acquiring a test lease.

The job descriptor carries target paths explicitly. No maintained case should
derive a target from the operator's current directory, a historical task tree,
or an assumed sibling checkout.

### Q06-P07 — cancellation and destructive tests

Cancellation is a declared capability, not a universal Escape keystroke. A
cooperative fixture checks the supervisor at defined safe points and reports
whether cleanup completed. A raw-media operation may declare a noninterruptible
interval and publish `safe_to_reset=false` until independent restoration passes.
The host preserves this state and cannot override it with a timeout.

An uninstrumented application can be observed but cannot promise cooperative
cancel or structured recovery. Tests of such applications remain manual or use
an explicitly destructive reset policy accepted for that fixture.

### Q06-P08 — residual `autoexec.txt` use

Keep startup mutation only when the test subject requires execution before the
normal admitted control plane exists:

| Retained case | Why live control is insufficient |
|---|---|
| First Extender input admission | The P4 input path cannot type the command that first enables itself |
| Missing/incompatible P4 recovery | The control peer is absent or is the failed subject |
| EMOS startup and startup-file semantics | The test specifically observes boot execution |
| Agon/P4 reset-order and cold-boot behavior | Reset and early handshake are the behavior under test |
| Bare-metal or bricked-firmware recovery | Normal EMOS/P4 services are unavailable |

Each retained case must say which row applies. Ordinary mode selection, fixture
launch, progress, completion, result collection and cleanup are not sufficient
reasons after the new control plane is qualified.

### Q06-P09 — command execution

Routine qualification should prefer typed structured actions—select route,
select mode, stage artifact, launch fixture, collect result—over arbitrary CLI
text. A bounded correlated `cli.exec` facility may remain useful for testing the
CLI itself and for recovery, but it must execute only from `cli-idle`, attach a
command ID, publish start/return, and state its network authorization policy.
P4 keyboard injection remains a human-input facility and an input test oracle;
it does not become the automation command channel.

### Q06-P10 — security and production identity

The present LAN keyboard API can already cause arbitrary CLI input after EMOS
admits Extender input. A structured job API therefore formalizes rather than
creates much of the operational power, but it increases reliability and must
not silently widen exposure. The accepted design must define endpoint binding,
session ownership, enablement, path allowlists, job classes, destructive-job
authorization, logging and browser access.

Qualification must exercise the exact firmware proposed for production.
Building a special diagnostic image and accepting ordinary bytes by analogy
would defeat the installed-firmware gate. The recommended direction is a
dormant bounded capability in ordinary firmware, activated by an explicit host
lease and every-job EMOS safe-point grant, subject to Author decision Q06-D01.

## Migration plan

Q06-M01 — Freeze protocol and ownership before code. Resolve Q06-D01 through
Q06-D05 one at a time and update REMOTE-005/DIAG-002 coordination boundaries.

Q06-M02 — Add state publication only. Verify lifecycle transitions in emulator
and on hardware while the old QUAL-005 suite remains unchanged. State reporting
must not alter CLI, application, mode or reset behavior.

Q06-M03 — Add P4 snapshot/events and resource inventory. Test peer restart,
lost events, reconnect, stale-state invalidation and client conflicts without
launching fixtures.

Q06-M04 — Generalize finite admission and add one harmless static fixture.
Prove launch, progress, result, cancellation and return without startup mutation
or reset.

Q06-M05 — Migrate integrated smoke actions. Keep keyboard-specific checks as
keyboard checks; move non-input setup to structured control.

Q06-M06 — Migrate RP06 mode transactions. Use EMOS-declared mode requests and
P4 committed-display generations; retain zero/one video-consumer coverage.

Q06-M07 — Migrate RP04 last among functional cases. Its job owns raw-media
restoration state and must publish `safe_to_reset=false` during the destructive
interval. Preserve the old conservative case until equivalent evidence passes.

Q06-M08 — Migrate performance after functional control is stable. Compare
against retained runs because removing reboot/listener/browser artifacts changes
setup overhead and may expose different timing.

Q06-M09 — Run old/new equivalence, obtain Author acceptance, then update the
canonical authority and current operating documentation. Preserve frozen
failure evidence; retire only maintained duplicate launch logic.

## Coordination boundaries

Q06-X01 — REMOTE-005 owns finite storage admission and WebDAV/storage behavior.
QUAL-006 reuses its safe-point identity/grant machinery but does not redefine
file semantics or create a second P4-to-EMOS launcher.

Q06-X02 — DIAG-002 owns human-visible startup connection and P4 identity.
QUAL-006 owns the machine-readable lifecycle/identity state required by tests.
DIAG-002 should render the same truth rather than negotiate a parallel identity.

Q06-X03 — QUAL-005 remains the accepted qualification policy and runner until
the new suite passes and is explicitly promoted. QUAL-006 is not evidence that
current firmware passed.

Q06-X04 — AUDIT-010 controls the active implementation audit/repair sequence.
Filing QUAL-006 records a cross-cutting test-infrastructure defect; it does not
change AUDIT-010's repair order without Author reprioritization.

## Conclusion

The fragile behavior is not caused simply by bad timeout values or careless
Python. The runners are trying to supervise an eZ80 foreground through interfaces
that expose only keystroke delivery, rendered output, and one foreground file
service. Their elaborate recovery is rational under those limits, but it cannot
be made fully reliable without authoritative EMOS state and a correlated job
protocol.

The smallest principled path is to generalize the finite REMOTE-005 admission
already present in development source, add resident EMOS lifecycle reporting,
make the P4 a state/event/resource broker, and give fixtures a small bound result
ABI. Then routine tests can behave like modern remote jobs: preflight, stage,
launch, observe, collect, clean up, and return to idle—without rewriting the
machine's boot file or rebooting merely to run the next test.
