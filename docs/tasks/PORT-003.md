# PORT-003 — Implement the P4 display backend and logical frame service

Current planned addition: [unimplemented-command consumption](#unimplemented-command-consumption-tranche). Task documents only in the current turn; no implementation started.

## Governing priority — faithful upstream backend, 2026-09-10

The Author has made [AUDIT-006](AUDIT-006.md) the first priority and expanded it
to compare the entire stock video-generation backend with the selected P4
implementation. The source audit and R1 proof are accepted; execute the restoration contract before another
local optimization or QUAL-003's benchmark. This task implements the
subsequently accepted repair contract; it must not use the previous generic
controller, flat planes or project pixel codecs as constraints on that review.

Reuse upstream code exactly wherever processor facilities and video-output
interfaces permit it. Portable algorithms within a VGA controller remain
reuse candidates even when the physical engine cannot run on P4. Native memory
layout, row operations and efficient execution are part of fidelity, beyond
matching final pixels. ADR-0013/ADR-0015 and the architecture now make this
explicit. Existing phase definitions/evidence describe their identified builds;
their broader replacement choices are reopened under AUDIT-006-D001/D002.

AUDIT-006 W6/W7 now provide the completed
[source comparison](AUDIT-006/video-backend-audit.md) and
[accepted restoration contract](PORT-003/stock-backend-restoration.md).
The authorized first coding increment binds the original five depth classes,
preserves their native row layout and compares their operations with stock.
Independent output/clock integration follows with explicit shared-state
ownership; no new drawing budget is proposed. The Author accepted W8/D002 and authorized R1 after freezing the contract.
No upstream bug fixes belong in this first pass: use otherwise compilable
upstream code unchanged. R1 is a build/comparison proof; no flash is authorized.

**R1 accepted; R2 authorized:** the original five classes and shared renderer
compile/link as a nondeployable P4 closure. The
[native-row evidence](PORT-003/stock-backend-r1/README.md) records 180 passing
checks and two preserved upstream two-colour scroll discrepancies. Original
headers/common files and utility bodies are source-verified. R2's independent
worker/output integration is prepared below; the ordinary console still selects its
existing backend, and no performance improvement is claimed yet.

**R2 accepted; [R3 deployment authorized](PORT-003/stock-backend-r3/README.md):** the [runtime binding and evidence](PORT-003/stock-backend-r2/README.md)
records 70 passing concurrency/lifetime checks, 42 passing stock scanline
checks, and 180 native comparisons with the same two inherited discrepancies.
The 20-unit P4 display closure and ordinary console integration compile/link
as nonbootable objects. Original bodies remain beneath narrow entry/lifetime
bindings; RGB222 output uses original packed scanline code directly.
PORT-003-R2-D001 preserves the independent clock and the Author's reservation
about stock's reliable 60 Hz cadence. R3 owns deployment selection, complete
candidate build and physical qualification. The Author requests repaired Nurples as the first qualitative hardware check; full qualification remains separate. Candidate `uart-excom-console-r10-b2026-09-11-03-37-54Z` from `f0dc271` is now deployed with independent flash verification, USB keyboard enumeration and HTTP startup; the Author reports marked gameplay improvement, residual jerkiness and noticeable slowdown as more sprites appear. Measured attribution and full qualification remain open.

## Active correction — stock queue draining, 2026-09-10

**PORT-003-D013 — Accepted:** remove the P4 primitive-count limit. On each
service opportunity, drain FIFO work until empty or suspended, matching the
selected stock worker with its timeout disabled. Preserve independent tick
accounting, immediate flush, double-buffer drawing/swap and existing P4
suspension handling. Core assignments and UART/parser budgets stay unchanged.
ADR-0015 and the normative architecture/frame contract are amended accordingly.

1. [x] Implement the drain policy and remove the production budget interface.
2. [x] Validate backlog draining, suspension/resume, completion, swaps and
   lifecycle; prepare the P4 build and concrete deployment for review.
3. [x] Author accepted the measured point comparison. W10 now validates all
   48 cases and post-run Legacy keyboard input; W9's separate keyboard
   observation remains unconfirmed. Broader responsiveness is still failing.

The [W9 work contract](AUDIT-005/stock-queue-drain.md) owns exact inputs,
identity, measurement boundaries and stopping rule. Earlier Phase C target
qualification remains evidence of its original candidate, not this correction.
The [local preparation record](AUDIT-005/stock-drain-preparation.md) records
passing frame/render/mode checks and the clean r08 candidate build from
`b9d4ff6`. The Author-authorized P4 deployment passed independent readback
and startup checks. The [single comparison](AUDIT-005/stock-drain-findings.md)
reduces counted-point completion from 5.075 s to 1.097 s, removing the
approximately 60 Hz UART pauses. Broader workload and browser/gameplay
validation remain open; the existing setup-query timeout persists.
The [full-suite result](AUDIT-005/stock-drain-suite-findings.md) shows uneven
improvement and persistent setup/null-path stalls. The Author then playtested
Nurples and reports a regression with substantial ExCom hangs. Retain r08 as
a candidate under investigation, not qualified gameplay. Review frame-worker
drawing/sprite/snapshot waits before proposing a new repair; no scanline,
core-affinity or drawing-budget change is authorized by these observations.
The Author subsequently authorized [AUDIT-006](AUDIT-006.md) to instrument
those intervals and reproduce the hang. It owns diagnostic deployment and
evidence; this display task still owns the eventual reviewed correction.

[AUDIT-006-F001](AUDIT-006/findings.md) now attributes the demonstrated freezes:
one drawing-drain invocation lasted 41.758495 seconds while Agon UART traffic
continued and no new snapshot completed. P4 ties publication and subsequent
logical-frame service to emptying a continuously replenished drawing queue.
The proposed correction is to separate periodic frame/output servicing from
that condition, preserving FIFO, explicit completion/swap and snapshot ownership.
This is a proposal for review, not an amendment of D013 or a selected budget/core
change. The Author proposes deterministic callback-timed graphics comparisons
under QUAL-003 as a measurement direction. The later fidelity-audit instruction
above now takes precedence; the benchmark remains a draft on hold.

## Current increment — RGB222 browser video, 2026-09-10

The Author selected this as the next display increment, ahead of broader
compatibility work. PORT-003 owns packed-pixel publication, EVF1 encoding,
browser decoding and presentation pacing; PORT-006 retains opaque network
transport and connection/backpressure ownership. Audio/Wolf3D repair remains
deferred to PORT-004.

1. [x] **RGB-1** Publish the P4-composed final image as one-byte RGB222 and
   decode it in browser WebGL. Preserve palette, Copper, sprites and cursor
   composition on P4; retain RGB888 browser decoding for existing streams.
2. [x] **RGB-2** Remove the 200 ms snapshot throttle; retain bounded snapshots,
   latest-frame selection and one-credit-per-present browser backpressure.
   Report measured browser presentation rate separately from logical VDP time.
3. [x] **RGB-3** Verify all 64 colours, format/dimension changes, malformed
   frames, immutability and backpressure locally; build the P4 draft and prepare
   an isolated browser review. Launch an explicitly labelled emulator attention
   cue only after the review is ready.
4. [ ] **RGB-4** After Author review and later deployment authorization, retest
   slideshow/gameplay colour, responsiveness, achieved frame rate and uptime.

The Author requires the currently running Agon/P4 slideshow to remain
undisturbed: no device access, deployment, reset, network probe or SD edits
during that completed preparation. The subsequent deployment authorization
below supersedes this temporary hold for P4 flashing and the requested SD edit.
The reported ten-minute slideshow run had no browser
disconnects or visible faults; this is an observation of the existing build.
Use standing identity preapproval for draft uart-excom-console-r05 and registry
r54; EMOS and paired graphics fixtures remain unchanged.

### Decision and local review record

**PORT-003-RGB-D001 — accepted:** the Author selected RGB222 browser decoding
and removal of the 5 fps throttle. [ADR-0018](../decisions/ADR-0018-rgb222-browser-video.md)
records the boundary; [browser video](../protocols/browser-video.md) is the
current encoding/pacing authority.

Local preparation and Author visual review are complete. The Author accepted
the preview and authorized P4 flashing; physical qualification remains pending. Draft P4 build:
`uart-excom-console-r05-b2026-09-10-05-47-38Z`.
The bundle and browser evidence are in the ignored `agents/rgb222-review/`.
No EMOS build, physical flash, serial open, bench network request or SD edit
was performed.

Validation: C++ address/undefined-behavior sanitizer checks passed for all 64
packed colours and exact header bytes, 120 successive 60 Hz publication
boundaries, immutable slow-client leases and latest selection; existing pool,
controller and network regressions passed. Actual Chromium WebGL readback
passed all colours, RGB888/RGB222 format switches, padded rows, minimum/maximum
surfaces, orientation, malformed frames and credit. The production page's
reconnect/video-only and network containment tests passed. The local demo
measured about 60 fps; this does not measure P4/Ethernet throughput.

Registry and VDP source identity validation passed. The whole-repository
version validator still fails on an unchanged r02 hardware connectivity hash
mismatch; this predates the increment and is outside its scope. Diff checks
pass. Author review is now accepted; source is being frozen for a clean candidate build.

### Accepted review and deployment authorization — 2026-09-10

The Author reports the local preview looked good and requests P4 flashing.
Standing identity preapproval advances registry r55 and the existing console
r05 to candidate. EMOS remains unchanged. The Author separately requests that
SD autoexec select `EMOS KEYINPUT extender` and then `CD /mystuff/slideshow/64`;
`app.bin` is directly in that directory. The Author clarified that keyboard
selection must remain automatic. Mode selection and application launch remain
operator actions. No Agon reset is authorized here.

### Deployment startup correction

The r05 candidate flashed and independently verified, and native USB input
enumerated. However, the HTTP endpoint refused connections after DHCP. Source
inspection identified unrequested full-frame composition on every tick in the
high-priority frame task as a starvation risk exposed by removing the throttle.
The r06 correction admits snapshots only when a consumer needs a fresh frame;
logical VDP work continues independently and no fixed fps cap returns.
Browser decoder/UI bytes remain exactly those accepted by the Author. Added
regressions for 120 idle ticks with no composition and 120 successive 60 Hz
consumer requests. The deployment is not a physical graphics/performance PASS.
The Author's flashing and standing identity authorization cover this P4-only
startup correction, selected as candidate r06 with registry r56.

### RGB222 deployment handover

Candidate `uart-excom-console-r06-b2026-09-10-06-01-48Z` from clean source
`3c2daa8` is installed. [PORT-003-2026-09-10-06-03-17Z](../../hardware/designs/light2-harness-r03/tests/PORT-003-2026-09-10-06-03-17Z/README.md)
records independent flash verification, USB keyboard enumeration, HTTP startup,
matching browser assets and five real RGB222 frames presented by an isolated
Chromium client. The client closed and HTTP remained responsive. This confirms
the startup correction; slideshow performance and sustained stability remain
for the Author's next test. The SD is safely unmounted with Extender keyboard
selection followed by the slideshow directory change. No Agon reset occurred.

### Admission regression and r07 functional recovery

The Author's first Agon test after the r06 deployment reports `KEYINPUT FAIL:
receiver readiness timeout`, mainboard input retained, and autoexec stopped at
line 1 with MOS's `Volume timeout` error. This is not a keyboard-admission PASS
or evidence of an SD fault. EMOS and the UART protocol were unchanged. The new
autoexec omits the previous `SET KEYBOARD 1`; default layout 0 (UK) and layout 1
(US) are both accepted by the P4 console, so this difference alone does not
explain a missing General Poll reply.

P4 HTTP remained responsive. A bounded serial recording of the installed r06
candidate collected an Agon-only reset attempt with browser video
disconnected, to distinguish admission failure from browser-dependent load.
Opening the recording restarted P4; no firmware or SD changes accompanied it.
At that point the cause and hardware result remained unresolved; the r07
follow-up below records functional recovery. Private capture details and
current bench state are in `HARDWARE.local.md`.

The Author confirms keyboard input works after the recorded P4 restart with
browser video disconnected, and manually launched slideshow on mainboard VDP.
The serial record confirms native keyboard admission with no connected video
client or reported fault. This establishes recovery, not the original failure
cause: both P4 state and browser connection state changed. The next comparison
kept browser video connected during Agon keyboard admission.


The connected-browser repeat also admitted the keyboard. The Author then typed
`emos excom` manually and received display-switch failure with Legacy retained;
keyboard and mainboard slideshow remained usable. The captured P4 received
PREPARE and later ABORT, with no COMMIT accepted, panic or UART fault. Browser
frames continued; gaps appeared in lower-priority diagnostic reporting. The
recording is stopped and retained as informative failure evidence under
`PORT-003-2026-09-10-06-13-32Z` beside the design tests.

Source review and a failing host regression identify duplicate snapshot demand:
network polls while the producer is still composing set the request flag again.
With continuous browser credit, the high-priority frame task can compose again
on each catch-up tick. The r07 correction makes those polls await the existing
Producer slot, including deferred publication; after cancellation a later poll
can request another attempt. It retains logical tick semantics, the single
renderer owner, immutable leases and no fixed frame-rate limit. The test
interleaves twelve network retries per composition over 120 frames and checks
that no unrequested extra composition begins, plus cancellation recovery.
The subsequent hardware retest below confirms successful admission and ExCom
entry, while typing latency remains open. EMOS and browser assets are unchanged. Standing
identity/deployment authorization selects candidate r07 and registry r57.

The Author raised dedicating a P4 core to critical UART/USB/command work. This
remains an architectural option, not an accepted assignment: first complete the
bounded request correction, then use task-runtime and latency measurements to
judge core placement and rendering cost. Core assignment cannot by itself fix
duplicate work or cross-task waits.


Candidate `uart-excom-console-r07-b2026-09-10-06-31-58Z` from clean `52479f0`
is now installed and independently verified. Deployment evidence is
[PORT-003-2026-09-10-06-32-58Z](../../hardware/designs/light2-harness-r03/tests/PORT-003-2026-09-10-06-32-58Z/README.md).
USB/HTTP startup and 104 real RGB222 browser presentations including a continuous
20-second credit interval pass. Periodic diagnostic output retained its normal
cadence in that bounded check. The agent browser closed before the Author-operated keyboard admission and
manual ExCom retest with browser video connected, recorded below.


**Functional recovery confirmed; typing latency open:** the Author reports
successful manual ExCom entry and slideshow on Extender. The completed
[PORT-003-2026-09-10-06-33-58Z](../../hardware/designs/light2-harness-r03/tests/PORT-003-2026-09-10-06-33-58Z/README.md)
record shows keyboard admission, accepted PREPARE/COMMIT/LEAVE, one P4 startup
and no panic, UART blockage or USB fault. Periodic diagnostics retained their
normal cadence. One socket-send failure occurred at the agent's deliberate
browser closure before the operator's test; no further failure was recorded.
Capture is stopped and preserved. No further firmware/SD/reset operation.

The Author also reports very laggy refresh while typing. This functional PASS
does not close responsiveness or RGB-4's remaining performance/uptime checks.
The next proposed bounded investigation measures USB reception, UART delivery
to EMOS, returned VDU bytes, P4 rendering/snapshot readiness and browser
presentation. Use correlated intervals to distinguish input and output delay
before changing task priority/core assignments. No new instrumentation or
core-assignment implementation is authorized by recording that proposal alone.

### Deferred core-affinity review

Author-directed on 2026-09-10; follow-up owned by PORT-003, not an active
implementation increment. The P4 frame-service task currently uses unpinned
`xTaskCreate`, while the command-processing task is pinned to core 0. The
[original proposal](PORT-003/PROPOSAL.md#concurrency-ownership) deferred exact
affinity to measurement; no subsequent pinned-versus-unpinned comparison was
found in this review. Stock VGA/core-local timing assumptions explain why core
numbers were not copied automatically, but do not establish that leaving P4
frame service unpinned is preferable. Pinning a task does not reserve a core.

1. [ ] Revisit this decision when the current AUDIT-005 investigations are
   exhausted or the reported slowdown is resolved. If material slowdown
   remains, consider a bounded affinity comparison as a diagnostic follow-up;
   do not combine it with the current stock-drain correction.
2. [ ] If the current work resolves the slowdown, retain the review as a
   further optimization deferred until implementation is substantially
   complete. At that point compare measured P4 task placement, contention and
   responsiveness with stock's division of work before proposing any change.

These are conditional dispositions of one review, not authorization to change
affinity, priority or scheduling now. Record which branch applies when the
current performance investigation closes.

### Partially working checkpoint — 2026-09-10

The Author requests preserving the current state, with the functional recovery
above accepted only within its stated scope. The later Nurples run was very
laggy on EDP, with rapid-fire laser bolts closer together than on mainboard
VDP. This is a subsequent operator observation, not part of the earlier serial
capture or a measured throughput result. Typing responsiveness and gameplay
performance remain unresolved; the earlier successful Nurples milestone does
not qualify this newer P4 candidate's performance.

A read-only scan of the deployed Nurples repair lineage (`4a52199`, no assembly
source differences in the inspected checkout) found that `player_laser.inc`
uses a MOS-clock cooldown of 12 clock units, fixed movement of four pixels per
game update, and one recharge unit per six updates. `timer.inc` samples MOS
time; `vdu.inc` waits for that clock to change rather than requesting EDP
render completion. Fewer game updates between elapsed-time shot deadlines
could therefore explain compressed bolt spacing. This is a timing clue, not
proof of the bottleneck. Continuous fire reads the held-key map.

The EMOS source scan found synchronous byte transmission, per-byte deadline
and interrupt bookkeeping, and waits when P4 pauses reception through CTS.
P4 backpressure and EMOS execution overhead remain alternative or contributing
causes; no trace measures their cost yet. No Nurples or firmware source,
hardware state, or SD contents changed during this investigation.

The Author places a stock-MOS reuse audit before further instrumentation or
core assignment. Review the smallest EMOS routing/ownership changes that can
retain proven stock implementation; do not assume C itself proves a defect or
remove necessary compatibility, flow-control, lifecycle or recovery behavior.
The [AUDIT-005 review](AUDIT-005.md) takes priority over the earlier
instrumentation proposal. W1–W6 measurements are complete; the
[paired hardware baseline](AUDIT-005/hardware-baseline.md) validates all 48
rows and measures direct ExCom send times 2.61–4.52× Legacy medians. The
[completed UART/CTS trace](AUDIT-005/uart-cts-findings.md) now locates 3.407
of 4.456 payload-wire seconds in idle while P4 withholds permission. The
returned CSV agrees within clock resolution and confirms Legacy return.
P4 receive/parser/display service is the immediate performance target. The
[W7 browser-disconnected control](AUDIT-005/browser-disconnected-findings.md)
now measures 5.075 s total versus 5.081 s connected, with P4 still withholding
permission during 3.344 s of idle. Long individual gaps shrink, but the main
throughput problem persists. The Author accepted these findings; the
[W8 internal wait-attribution contract](AUDIT-005/p4-wait-attribution.md)
was frozen in `71f082e`. The completed
[W8 source accounting](AUDIT-005/p4-queue-accounting.md) finds five queued
primitives per point. EDP's 64-per-frame limit predicts 5.067 s versus 5.075 s
measured; RX buffering and approximately 60 Hz wire bursts corroborate the
mechanism. Stock's background drain has no such fixed count limit. W8 required
no instrumentation and is accepted. The Author rejected the 128-budget
experiment and authorized [stock queue draining](AUDIT-005/stock-queue-drain.md)
under PORT-003-D013, followed by one unchanged browser-off comparison. Its
physical deployment gate remains explicit.
The Author selected paired
Legacy/ExCom pathway benchmarks before choosing repairs, followed by repeated
measurements and personal Nurples playtesting; automated game input is
deferred. The findings distinguish definite EMOS byte-path overhead from
measured P4 backpressure; the internal P4 cause remains unisolated. This task
retains the unresolved display/performance work. The physical CSV supplies
the timing result; emulator checks establish fixture behavior. No performance
repair or new core assignment has been made.

## State

- Status: In progress — Gate F accepted; Work 2.a source findings are recorded
  and broad D011 hardening is rejected; Phase G awaits applicable REMED-002
  gates, Work 4.d's Gate G definition, PORT-008 Gate 2, and applicable QUAL-002
  qualification
- Started: 2026-08-22 10:14 EDT
- Finished: --

## Current integration priority — 2026-09-09

The Author selected actual ExCom console operation and continued VDP-to-EDP
porting after native USB CLI/gameplay passed. PORT-008's next bounded increment
pairs EMOS-owned ordinary VDU routing with the retained P4 parser/rendering and
browser display, while preserving USB input. Reuse the existing display work;
this is not a restart of the upstream inventory or a claim of complete Gate G
compatibility. Browser keyboard input and further keyboard polish are deferred.
PORT-006 retains network ownership; browser video remains the initial output.
A video defect that blocks this proof remains relevant even though browser
input repairs are deferred. Historical r02/parallel prerequisites below do not
resume held construction or gate this UART-only console proof.

The paired `p4-console` composition is now a compiled draft under PORT-008;
it feeds this retained parser and display path from EMOS ordinary UART VDU.
Native-reference emulator checks do not exercise the P4 concrete controller or
browser video. Those results await the bounded r03 console hardware sheet;
Gate G and wider rendering qualification remain open.

## Intent

Implement the accepted Work 1.d display boundary: retain the official VDP
screen facade, FabGL Canvas, and common bitmapped rendering semantics while
replacing the classic-ESP32 concrete VGA physical-controller family with an
Extender-owned P4 concrete `BitmappedDisplayController`.

The backend produces framebuffer state and logical frame progression
independently of any one output sink. The guaranteed network/browser path and
later P4-native local-display paths consume that common rendering model rather
than defining separate VDP implementations.

## Authority and inputs

- [SETUP-004 Work 1.d](SETUP-004.md#work-1d-execution-record) and its generated
  display-driver inventory.
- [ADR-0013](../decisions/ADR-0013-vdp-survey-integration-boundaries.md),
  especially decisions 16–21.
- [Current architecture](../architecture.md).
- [PORT-001 dependency graph](PORT-001.md) and
  [PORT-002 source-selection work](PORT-002.md).

## Required outcomes

1. Preserve the official screen-facade names, placement, ownership, mode and
   fallback behavior, dimensions, scaling, palette/Copper state, logical frame
   counter, completion waits, and buffer swaps through narrow integration
   changes.
2. Preserve Canvas and common primitive, paint, clipping, geometry, glyph,
   bitmap, sprite, cursor, readback, completion, and buffering semantics.
3. Supply an Extender-owned concrete bitmapped controller and framebuffer/frame
   service without retaining the old GPIO-matrix, I2S1, DMA-chain, or VSync-ISR
   physical engine.
4. Preserve stock mode dimensions, palette quantization, Copper scanline
   effects, sprite composition, readback, double buffering, frame waits and
   counters, callbacks, and failure/fallback behavior as closely as practical.
5. Reuse separable upstream algorithms where useful, keep every unavoidable
   P4 substitution narrow and provenance-rich, and update the dependency graph
   and compatibility delta.
6. Feed the initial network/browser video sink from the common framebuffer
   service. Treat MIPI-DSI and other local display sinks as separately
   selectable output implementations over the same rendering model.
7. Add deterministic host-side tests where possible and qualified target tests
   for rendering fidelity, frame behavior, concurrency, memory limits, and
   output-sink integration.

## Dependencies and gates

- PORT-008-D003 now establishes the circuit incrementally on r02. This task's
  parser/display/browser components become dependencies only when the selected
  stage exercises or observes them. Power, bias, and isolated transport checks
  follow the [staged process](../qualification/staged-circuit-validation.md)
  without requiring Gate G or a complete release composition. Gate G's
  end-to-end compatibility prerequisites remain unchanged.
- Complete SETUP-004 before implementation so audio, input, network, and
  storage boundaries cannot be mistaken for display-backend ownership.
- PORT-002 must represent old concrete controllers as vendored but excluded and
  identify the selected replacement closure.
- `SETUP-005-D002` governs operating-mode lifecycle and later qualifies which
  processor owns the facade during transitions.
- QUAL-001 Review Gate 1 must be accepted before Phase D implementation so
  palette, Copper, overlay, and later facade decisions update durable
  compatibility obligations as they are made.
- PORT-008 supplies the physical command/response transport and official
  General Poll canary after Phase E. PORT-008 Gate 2 and the applicable
  QUAL-002 assembled-system scope must pass before PORT-003 Gate G can claim
  end-to-end Agon compatibility.
- Define detailed implementation phases and acceptance fixtures with the
  Author before coding. Do not infer pixel-level fidelity merely from a
  successful build or visible image.

## Review Gate 1 work plan

This plan is the scope fence for the evidence-and-design pass approved by the
Author on 2026-08-22. Check it before beginning each numbered item and record
results against the same number. Do not begin production implementation during
this pass.

1. [x] Freeze scope, authoritative inputs, evidence requirements, deliverable
   structure, and stop conditions in this task and its task-local directory.
2. [x] Review official Agon documentation, official VDP `v2.16.0`, the pinned
   vdp-gl release, accepted ADRs, SETUP-004 Work 1.d, and PORT-002 selection
   evidence. Record exact source entry points rather than performing an
   unbounded firmware survey.
3. [x] Generate bounded, deterministic display dependency inventories and slices
   from the durable dependency graph. Keep generated evidence machine-readable
   and make every human projection reproducible.
4. [x] Trace retained behavior manually from the official screen facade through
   Canvas and the abstract bitmapped-controller contract. Separately inventory
   classic-ESP32 VGA assumptions and classify each as retained algorithm,
   replaceable platform seam, excluded physical engine, or unresolved risk.
5. [x] Inspect only pinned ESP32-P4 framework facilities relevant to memory,
   scheduling, synchronization, cache/DMA constraints, and potential frame
   consumers. Use disposable compile probes only when they answer a recorded
   feasibility question; do not alter upstream checkouts or claim hardware
   qualification.
6. [x] Propose the narrow P4 `BitmappedDisplayController`, logical frame lifecycle,
   memory/concurrency model, and sink-neutral consumer interface. Preserve the
   accepted upstream-shaped facade and explicitly leave SETUP-005 mode policy
   outside the backend.
7. [x] Define deterministic host fixtures, later target qualification cases,
   compatibility measurements, implementation risks, and small implementation
   phases with review and acceptance gates.
8. [x] Audit the package against this plan, validate generated artifacts, update
   the task and current development log, and stop at Review Gate 1 for Author
   review without committing.

### Explicit exclusions for this pass

- No production firmware or vendored upstream source is added or modified.
- No network/browser, MIPI-DSI, or other physical output sink is implemented.
- No EDU/VDU routing, MOS integration, or SETUP-005 operating-mode decision is
  selected or implemented.
- No audio, input, networking, storage, updater, or board-wiring scope is
  absorbed into PORT-003.
- No successful firmware build, hardware behavior, timing, throughput, or
  pixel-fidelity claim is made without the corresponding evidence.
- No new external protocol, artifact version, hardware revision, or qualified
  baseline is silently assigned.

## Review Gate 1 stop condition

This gate was satisfied and accepted on 2026-08-22. The Author delegated
technical review to the Agent, authorized the Agent to commit and push the
package without personal diff review, and authorized Phase A to proceed under
a detailed stepwise plan without another pre-start review.

## Review Gate 1 decision register

All entries were accepted by delegated approval on 2026-08-22. The reviewed
recommendations and alternatives are detailed in
[`PORT-003/PROPOSAL.md`](PORT-003/PROPOSAL.md#decisions-accepted-at-review-gate-1).

| ID | State | Decision requested |
|---|---|---|
| `PORT-003-D001` | Accepted | One project-owned generic bitmapped controller with configured native codecs. |
| `PORT-003-D002` | Accepted | Preserve upstream packed native formats for the initial compatible backend. |
| `PORT-003-D003` | Accepted | Advance logical frames from sink-independent `esp_timer` cadence. |
| `PORT-003-D004` | Accepted | Adopt the proposed tick, swap, completion, and overrun model, subject to fixtures. |
| `PORT-003-D005` | Accepted | Use one central Copper and hardware-overlay presentation compositor. |
| `PORT-003-D006` | Accepted | Use latest-generation non-blocking frame consumers; slow sinks may drop generations. |
| `PORT-003-D007` | Accepted | Adopt the phased implementation and qualification plan. |

## Review Gate 1 execution record

### 1–2. Scope and bounded authority

The task-local package structure and explicit exclusions were frozen before
analysis. Research remained bounded to official Agon display documentation,
official VDP tag `v2.16.0` at
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, its pinned vdp-gl
`all-the-plots`, accepted display decisions, the canonical dependency graph,
and the pinned P4 framework headers. No firmware, vendored source, output sink,
or operating-mode policy was changed.

### 3. Deterministic evidence

[`PORT-003/generated/display-evidence.yaml`](PORT-003/generated/display-evidence.yaml)
projects six reviewed Work 1.d candidates, 31 direct files, 1,990 symbols, 33
abstract controller declarations, 478 classified old-architecture hits, 164
bounded related files, and five fingerprinted P4 platform headers. Compact
mode and controller slices are generated from the canonical graph. Two complete
pipeline passes were byte-identical and all graph/evidence validators passed.

Gotchas found while constructing the generator:

- a selection record can legitimately belong to more than one survey
  candidate; treating candidate membership as one-to-one lost the shared
  `fabgl.h` role;
- the first controller slice omitted `defines` and `includes`, producing a
  technically valid but useless one-node view; the relation set now preserves
  the controller's actual consumers; and
- the first validator used shorthand candidate names instead of durable graph
  IDs and correctly stopped the pipeline until fixed.

### 4. Retained behavior and physical exclusions

[`PORT-003/display-behavior.md`](PORT-003/display-behavior.md) traces mode
fallback, Canvas/primitive execution, the abstract backend, native pixels,
palette/Copper, software versus hardware sprites, readback, frame counter, and
callbacks. It separately classifies the classic GPIO/I2S/DMA/VSYNC engine and
the narrower architecture adaptations. Notable hidden couplings are the
official context's direct read/write of the concrete controller frame counter,
palette helpers that downcast to `VGAPalettedController`, and the input path's
`VGABaseController *` mouse-positioner type.

### 5. P4 feasibility

[`PORT-003/platform-feasibility.md`](PORT-003/platform-feasibility.md) records
the pinned capability heap, cache synchronization, periodic timer, RGB panel,
and MIPI-DSI declarations. These facilities support the proposed boundary at
header level. No disposable compile probe was needed because Review Gate 1
does not yet contain a concrete API call whose signature or linker selection
needed proving. No compile, throughput, cadence, or hardware claim was made.

### 6–7. Proposal and qualification

[`PORT-003/PROPOSAL.md`](PORT-003/PROPOSAL.md) proposes one project-owned
generic bitmapped controller, preserved native codecs, a sink-independent
logical frame service, central presentation composition, and non-blocking
latest-generation consumers. The seven material choices were accepted by
delegated approval and are recorded in ADR-0015.

[`PORT-003/qualification-plan.md`](PORT-003/qualification-plan.md) defines
deterministic oracle provenance, host and target fixture families, seven
implementation phases with review gates, and explicit stop/rollback rules.
It keeps physical sink implementation in separately owned work while requiring
all sinks to prove they cannot redefine logical VDP behavior.

### 8. Audit and stop gate

The final task-local pipeline regenerated twice byte-for-byte, validated both
canonical graph slices, and passed all PORT-003 evidence invariants. The ten
permanent dependency-tool tests passed. New Python sources compiled from text,
all local Markdown links resolved, no absolute machine path entered the tracked
package, `git diff --check` passed, and both generated SVGs contain explicit
white backgrounds. The worktree contains only TODO/task/development records,
task-local analysis machinery, generated evidence, and Review Gate 1 design
documents. Production firmware and vendored upstream trees remain untouched.

### Author approval

On 2026-08-22 the Author explicitly approved this work without performing a
personal review, authorized the Agent to commit and push it, and authorized
continuation into the next implementation gate without another review. The
same scope-control stipulation applies to that continuation: write a detailed
task list first and refer to it step by step to prevent drift.

## Phase A — Contract canary

- Status: Complete — Gate A passed
- Started: 2026-08-22 11:54 EDT
- Finished: 2026-08-22 12:38 EDT

Phase A is the next gate authorized by the Author. Its sole purpose is to prove
that the retained vdp-gl Canvas/common-renderer contract and one project-owned
concrete P4 controller type can enter the pinned P4 build without linking the
excluded classic VGA physical engine. It is not a functional renderer.

### Detailed execution checklist

Check this list before each action. Record outcomes and deviations against the
same item; do not substitute later-phase work merely because a nearby source
file is visible.

1. [x] Freeze the exact import, build, evidence, and stop boundaries under
   `PORT-003/phase-a/`. Use only the accepted official VDP `v2.16.0`, vdp-gl
   `all-the-plots`, ESP32Time `2.0.6`, and CRC `1.0.4` baselines already
   fingerprinted by the canonical dependency graph.
2. [x] Implement and validate a deterministic initial source-import process.
   Import official `video/` files unchanged into the upstream-shaped firmware
   tree while preserving `video/extender/`; import complete vdp-gl, ESP32Time,
   and CRC release contents under `vdp/vendor/`; exclude VCS administration
   only; preserve licenses, paths, bytes, and executable modes; and verify file
   counts and tree hashes before accepting the import.
3. [x] Update durable dependency presence/provenance so the canonical graph
   distinguishes repository-vendored dependencies and the imported official
   firmware from external reference trees. Regenerate deterministically and
   require zero source-identity or selection drift caused merely by relocation.
4. [x] Define a dedicated `p4-display-contract-canary` build environment and
   machine-readable source list. Compile only the canary, project-owned display
   skeleton, and the smallest evidenced retained vdp-gl closure. Keep the
   ordinary P4 environment separate and prevent PlatformIO from auto-building
   the vendored library's broad classic-ESP32 source set.
5. [x] Add a prominently marked contract-only P4 controller derived from
   `fabgl::GenericBitmappedDisplayController`. Make every required virtual
   method concrete, preserve an official-facade-shaped ownership/factory seam,
   and add compile-time assertions for integer widths, RGB/pixel values,
   native-format enumerators, and base-class relationships. Unimplemented
   drawing methods must fail visibly if called; they must not masquerade as a
   functioning display.
6. [x] Run bounded diagnostic compile iterations with the pinned PlatformIO
   environment. For every failure, classify the responsible source and cause
   before changing anything. Permit only retained Canvas/common-renderer
   dependencies and narrow P4 architecture adaptations required by this
   contract canary; record gotchas and inherited upstream assumptions beside
   the affected code and in Phase A evidence.
7. [x] Prove the resulting ELF/build graph contains the canary controller,
   Canvas, and common bitmapped-controller implementation while excluding all
   classic VGA concrete, VGA text, CVBS, Scene, physical PS/2, audio-output,
   network, and storage translation units. Record compiled sources, unresolved
   or discarded symbols, map evidence, and the exact non-qualification build
   invocation.
8. [x] Update the dependency graph, source-selection projection,
   compatibility delta, task record, and development log with the implemented
   seam and observed build closure. Do not turn diagnostic compilation into a
   hardware, rendering, timing, or compatibility claim.
9. [x] Run deterministic regeneration, dependency tests, task-local tests,
   clean-room rebuild, source-import verification, link-exclusion checks,
   Markdown/link/whitespace checks, and `git diff --check`. Stop at Gate A only
   if all criteria below are satisfied; otherwise stop at the first declared
   blocker with the evidence preserved.

### Phase A execution record

#### 1–3. Boundary, import, and provenance

The task-local Phase A package froze the gate before import or compilation.
`import-baselines.py` copied only immutable reviewed release bytes and modes,
preserved the official `video/` layout around the existing `video/extender/`
namespace, and refuses unexplained dependency files. Its steady-state verifier
proves 5,164 files across the four accepted baselines, matching all file counts
and tree hashes with zero local vendored modifications.

Managed-import mappings now make `vendored` a mechanically verified repository
fact. Every canonical upstream file node carries its upstream-relative path and
repository-managed path. Regeneration changed presence from external reference
to vendored without changing any source identity, release, commit, tree hash,
manifest count, or declared selection.

#### 4–5. Exact build and type boundary

`p4-display-contract-canary` uses a tracked five-translation-unit allowlist:
three project units plus upstream `canvas.cpp` and `displaycontroller.cpp`.
Because the Arduino/ESP-IDF hybrid ignores PlatformIO `build_src_filter`, the
pre-build hook deterministically renders an ignored component `CMakeLists.txt`
from the same list and adds only the two reviewed vendored units.

`P4DisplayControllerContractCanary` is a concrete
`GenericBitmappedDisplayController` with an official-facade-shaped factory.
Static assertions cover integer widths, `RGB888`, native-format enumerators,
inheritance, and base-pointer ownership. Lifecycle setup is bounded to a 1×1
contract shape. Every drawing, readback, bitmap, glyph, scroll, and swap method
fails visibly. A volatile-false probe retains the common primitive executor for
ELF evidence without executing it.

#### 6. Bounded compile iterations and gotchas

Each failure was classified before correction:

- PlatformIO's global Arduino package name had been left at upstream control
  build version 2.0.14, while pioarduino 55.03.311 requires core 3.3.11. The P4
  environment now pins the constituent 3.3.11 package so whichever build ran
  last cannot silently break the other.
- The hybrid framework ignored `build_src_filter` and initially compiled
  official `video.ino`, reaching excluded sound code and the missing classic
  `soc/sens_struct.h`. The generated component source list is the required
  hybrid build boundary; no official source was patched.
- A force-included C++ compatibility header was also injected into framework C
  units. Architecture helpers are now guarded by both RISC-V and C++ so the
  canary does not impose C++ standard headers on C compilation.
- vdp-gl's common headers include the removed classic ESP32 FRC timer register
  header even though this closure does not use that timer. The project shim is
  parse-only and aborts if an accidental runtime access occurs.
- Common vdp-gl code assumes Xtensa coprocessor helpers. The RISC-V canary
  supplies compile-only no-ops, prominently marked for replacement or reviewed
  runtime policy before transformed bitmap qualification.
- Excluding broad `fabutils.cpp` exposed a narrow utility link closure. Exact
  upstream implementations for timeout conversion, line clipping, rectangle
  merge/intersection, and `LightMemoryPool` were copied into one provenance-rich
  project port unit. No vendored file was edited.
- The first evidence pass found `execPrimitive()` discarded by section garbage
  collection. The guarded project probe made the gate's requirement real rather
  than weakening the validator.
- Official VDP and dependency releases retain upstream CRLF/tab/trailing-
  whitespace bytes, so an unqualified whitespace check initially reported the
  immutable imports. A root `.gitattributes` disables only those inherited
  checks under official `video/` and `vdp/vendor/` paths while restoring Git's
  normal strict set under `video/extender/`; no imported byte was normalized.
- The standard `*.map` build-output ignore also matched legitimate vdp-gl
  Doxygen `.map` release files. A vendor-root exception now makes reviewed
  `vdp/vendor/` imports byte-complete, and the importer can require every mapped
  release path in the staged Git index at commit gates.
- PlatformIO prints the board metadata's generic `400MHz` banner. The accepted
  pre-v3 configuration remains explicitly 360 MHz in `sdkconfig.defaults`; the
  banner is not runtime or configuration evidence.

#### 7–8. Closure proof and durable model

The resulting diagnostic ELF is approximately 536 KiB and is not a versioned
or qualified firmware artifact. Machine evidence proves exactly five VDP
application objects, all six required project/common-renderer symbol claims,
and no unexpected application objects. It reports no classic VGA, CVBS, Scene,
physical PS/2, sound generator, file browser, or other excluded VDP symbols.
Only normal framework start symbols remain undefined in the final ELF view.

The canonical graph now records three observed Extender build units for the
canary, concrete controller skeleton, and narrow utility port, with confirmed
dependencies on the retained upstream files/types. The source-selection guide
lists these project boundaries separately so they cannot be confused with the
immutable upstream file-selection profile. The compatibility delta explicitly
limits this gate to type, compile, and link evidence.

#### 9. Gate A validation

The immutable import verifier passed at steady state with 5,164 matching files
and zero writes. A true clean removed the complete canary environment and the
pinned hybrid build recreated it successfully in 70 seconds. The final image
is 536,596 bytes; reported application usage is 30,780 of 512,000 RAM bytes and
535,808 of 7,340,032 flash bytes. These are diagnostic linker reports, not
runtime capacity or performance qualification.

The Phase A validator regenerated twice byte-identically and proved five
application objects, six required ELF symbol claims, and zero excluded VDP
source or symbol families. The complete dependency pipeline and PORT-003
evidence pipeline each regenerated twice byte-identically. Full graph schema,
referential, source-file, tree, and source-span verification passed. All six
PORT-002 boundary proofs passed, as did 12 dependency-tool tests, three Phase A
tests, and version-record validation. Changed Markdown local links, explicit
white SVG backgrounds, project-owned whitespace, and `git diff --check` passed.

No source-import bytes changed, no vendored source was edited, no firmware was
flashed, no hardware was exercised, and no artifact identity was assigned.
Gate A therefore satisfies all acceptance criteria without triggering a stop
condition.

### Phase A explicit exclusions

- No framebuffer allocation, pixel drawing, readback result, palette, Copper,
  sprite composition, frame clock, queue executor, buffer swap, or output
  consumer is implemented.
- No network/browser, RGB, MIPI-DSI, HDMI, audio, input, storage, update,
  transport, EDU/VDU routing, MOS, or operating-mode implementation is added.
- The complete official `video/` source may be imported unchanged, but the
  canary build does not attempt to compile or link the complete official
  firmware. Full facade integration remains Phase E.
- No classic VGA source is patched into compiling on P4, stubbed, or linked.
- No vendored upstream file is locally edited. A required upstream adaptation
  must be isolated in project-owned code or recorded as a stop condition.
- No firmware is flashed or deployed. This is a compile/link diagnostic, not a
  qualified artifact or test run; it may use the existing unidentified
  experimental developer-build identity and must not assign a new version or
  revision without Author approval.

### Gate A acceptance criteria

1. Imported files reproduce all four accepted source baselines exactly at the
   declared managed paths, with complete provenance and licenses.
2. A clean pinned P4 diagnostic build produces an ELF containing Canvas,
   common `BitmappedDisplayController`, and the concrete project canary type.
3. The source and link manifests prove that none of the excluded physical
   implementations entered the build.
4. The skeleton cannot be mistaken for working display firmware: drawing and
   readback entry points fail visibly, and no sink or frame service exists.
5. The dependency/source-selection model represents the imported, selected,
   excluded, and project-owned boundaries without unresolved records or
   unexplained observed-versus-declared drift.
6. All deterministic generators and tests pass from the frozen baseline, and
   all implementation gotchas and deviations are recorded with provenance.

### Phase A stop conditions

Stop without broadening scope if the gate requires editing a vendored file,
linking an excluded physical driver, implementing a real renderer or another
subsystem, selecting an output sink, assigning an unapproved artifact identity,
or making an unresolved SETUP-005 operating-mode choice. Also stop if imported
bytes do not match the accepted baselines or if the minimum retained closure
cannot be separated from an excluded subsystem without a new architectural
decision.

## Phase B — Native storage and synchronous renderer

- Status: Complete — Gate B passed
- Started: 2026-08-22 12:43 EDT
- Finished: 2026-08-22 13:47 EDT

The Author authorized continuation without an intermediate review after Phase
A passed and was pushed. This checklist is therefore the controlling review
surrogate: consult it before every action, update results against the same item,
and stop rather than silently expanding the gate.

Phase B implements authoritative logical pixel storage and the retained common
renderer in a deliberately synchronous, sink-free configuration. It does not
add logical frame time, background execution, palette/Copper composition,
official mode-facade integration, or output delivery.

### Detailed execution checklist

1. [x] Freeze the Phase B package structure, exact source/test/evidence
   boundaries, accepted inputs, oracle hierarchy, and stop rules under
   `PORT-003/phase-b/`. Define a machine-readable implementation manifest so
   project source, adapted upstream algorithms, host fixtures, and target build
   units cannot drift apart.
2. [x] Generate a bounded provenance inventory for native formats, storage,
   allocation, pixel access, raw bitmap operations, copies, scrolls, drawing
   primitives, and readback. Fingerprint the exact vdp-gl `all-the-plots`
   declarations and old concrete-controller spans; classify each algorithm as
   reusable unchanged, adapted with provenance, replaced by project logic, or
    deferred outside Phase B. Do not manually transcribe an untraceable list.
3. [x] Define project-owned contracts before implementing behavior:
   - one logical mode descriptor for explicit dimensions, native format, and
     single/double buffering, without importing the official mode table;
   - depth-specific native pixel codecs preserving `PALETTE2`, `PALETTE4`,
     `PALETTE8`, `PALETTE16`, and logical `SBGR2222` contracts;
   - transactional plane ownership with injected allocation/failure and
     deterministic zero initialization;
   - drawing versus visible plane selection and native-save/readback rules;
   - a synchronous controller lifecycle with background execution disabled;
     and
   - explicit result/error contracts that leave the old valid mode installed
     after any failed reconfiguration.
4. [x] Build independent deterministic test machinery before trusting the
   implementation:
   - pure host reference codecs and pixel matrices that do not call production
     codec methods;
   - canonical fixtures carrying source tag/profile, dimensions, depth,
     buffering, seeded command sequence, expected native bytes/readback/pixels,
     oracle class, generator identity, and content hash;
   - a host C++ harness for project codec/storage code and, if feasible without
     broad subsystem stubs, the actual retained Canvas/common renderer;
   - injected allocator failures at every allocation boundary; and
   - deterministic regeneration/validation that rejects implementation-derived
     goldens and stale provenance.
5. [x] Implement and qualify the five native codecs and transactional plane
   storage independently of Canvas. Exhaustively cover every legal pixel value,
   packed-byte boundary, odd width, row stride, clipping edge, clear pattern,
   single/double-plane identity, reconfiguration, release, and allocation
   failure. Preserve RGB222 logical bits; synthesize legacy native-save sync
   bits only where the proven upstream contract requires them.
6. [x] Replace the contract canary with a Phase B synchronous controller while
   preserving the accepted factory/base-pointer shape. Implement direct pixel,
   line, row, clear, scroll, copy, glyph, ellipse/arc/sector, flood-fill,
   bitmap, transformed-bitmap, native-save, and logical readback entry points
   through the retained common renderer and project codecs. Port only the
   smallest old-controller algorithms demonstrated useful by item 2, keep exact
   provenance inline, and make every still-deferred path fail visibly.
7. [x] Run the complete native/primitives fixture matrix for all five depths,
   relevant paint modes, clipping/origins, overlapping copies, edge
   coordinates, bitmap formats/transforms, and single/double storage. Separate
   independent host-model expectations, official captures, and reviewed
   source-derived expectations in the evidence. A compile or self-comparison is
   not a passing fixture.
8. [x] Define a dedicated Phase B P4 diagnostic environment from the same
   machine source manifest. Compile and link only the synchronous renderer,
   retained common closure, and narrow project adaptations. Prove classic VGA,
   CVBS, Scene, physical PS/2, audio, network, storage, official facade, frame
   service, and output-consumer units remain absent. Do not deploy this build.
9. [x] Update the canonical dependency graph, source-selection projection,
   compatibility delta, task execution record, and development log with the
   observed storage/renderer boundary and exact adapted-source provenance.
   Distinguish host qualification, target compile evidence, and behavior still
   awaiting physical P4 qualification.
10. [x] Run a clean Phase B host and P4 build; complete fixture and allocation-
    failure matrices; import/index verification; graph and task evidence
    regeneration twice byte-identically; schema/source-span validation; all
    permanent tests; local-link, absolute-path, SVG-background, whitespace, and
    `git diff --check` audits. Commit and push only if every Gate B criterion
    passes and no stop condition requires a new Author decision.

### Phase B execution record

1. Package and authority freeze — complete:
   - `phase-b/README.md` defines the bounded task-local layout and Gate B
     boundary;
   - `phase-b/implementation-manifest.yaml` fixes production, host-test,
     fixture, evidence, target-build, and excluded-unit roles before behavior
     implementation; and
   - independent expectations outrank implementation output, which is
     explicitly forbidden from generating its own goldens.
2. Algorithm provenance — complete:
   - the deterministic extractor consumed the pinned SETUP-003 Universal Ctags
     index and immutable vendored `vdp-gl` tree;
   - 863 definitions/declarations in 17 files carry exact file and inclusive
     source-span SHA-256 fingerprints, with anonymous lambdas covered by their
     owning callable rather than promoted to false API boundaries;
   - the inventory distinguishes 199 retained common records, 407 adapted
     depth/native records, 67 platform replacements, 35 Phase C deferrals, 90
     Phase D deferrals, and 65 classic-physical exclusions; and
   - thirteen permanent provenance tests verify lexical span handling, tuple uniqueness,
     all fingerprints, all five native algorithm families, critical boundary
     classifications, and byte-identical regeneration.

3–5. Contracts, independent oracles, codecs, and storage — complete:
   - `phase-b/contracts.md` freezes the five native formats, row/plane sizing,
     typed failures, transactional replacement, single/double identity,
     native-save rules, and synchronous lifecycle before implementation;
   - 139 generated codec cases cover every legal value, nine boundary widths,
     odd rows, all clear values, and all SBGR sync combinations;
   - pure codec/storage tests run under ASan/UBSan and explicit allocation
     accounting, including first- and second-plane failures, old-state
     preservation, successful replacement, move ownership, idempotent release,
     and validation/overflow failures; and
   - the independent oracle's first `PALETTE8` draft exposed that three-bit
     pixels cross arbitrary byte boundaries. It was corrected to a bit-by-bit
     MSB-first model before production output was accepted.

6–7. Synchronous retained renderer — complete:
   - the Phase A abort-only canary is replaced by `P4DisplayController`, backed
     by `NativePixelCodec` and `PlaneStorage`, with no frame service or sink;
   - a bounded host compatibility layer permits the actual unchanged Canvas
     and common controller units to execute without emulating an unrelated
     ESP32 subsystem;
   - 115 primitive fixtures—23 scenarios at each depth—cover paint modes,
     clipping/origin, lines/rows/rectangles, copies, scrolling, clear, glyph,
     flood fill, ellipse/arc/segment/sector, mask/native/RGBA bitmaps, identity
     transforms, readback, native-save output, and double-plane identity; and
   - all 254 codec/renderer fixtures pass with zero mismatch under ASan/UBSan.
     LeakSanitizer cannot inspect processes under the managed tracing boundary,
     so it is disabled while the storage harness independently rejects leaks,
     unknown frees, and double frees.

   The retained narrow-glyph fast path reads a four-byte window from each
   byte-stride row. The fixture supplies three safe trailing bytes and records
   this inherited data contract rather than patching vendored code. The host
   Xtensa wrappers are inert only around normally executed host floating-point
   transforms; target wrappers remain the reviewed RISC-V compatibility seam.

8. P4 diagnostic closure — complete:
   - `p4-display-renderer` compiles five project units plus unchanged vendored
     `canvas.cpp` and `displaycontroller.cpp`;
   - initial links exposed only four pure geometry/bit helpers from broad
     `fabutils.cpp`; those exact source-pinned routines were added to the
     existing narrow port and the next build linked successfully; and
   - the resulting ESP32-P4 image reports 586,082 bytes of flash use. Machine
     evidence proves all seven selected objects and six required ELF symbols,
     with zero classic VGA/CVBS/Scene/PS2/audio/network/storage units or symbol
     families. This remains compile/link evidence; nothing was deployed.

9. Durable integration records — complete:
   - the canonical dependency graph now represents the five current
     project-owned Phase B units and observed seven-unit closure rather than
     stale Phase A canary nodes;
   - source-selection projections and the VDU 22 proof slice regenerated twice
     byte-identically across all 5,164 vendored files; and
   - `phase-b/compatibility-delta.md` separates retained behavior, project
     adaptations, host-only harness seams, and later-phase work.

10. Gate B audit — complete:
    - a clean P4 diagnostic rebuild produced an ELF whose validator proved all
      seven selected units, six required symbols, and zero excluded source or
      symbol families; nothing was deployed;
    - the immutable import verifier matched all 5,164 baseline files and wrote
      zero files;
    - 139 codec and 115 renderer fixtures passed again, including every
      allocation-failure boundary, and all seven Phase B generated artifacts
      were byte-identical across independent output passes;
    - the final clean-build evidence was incorporated into two byte-identical
      canonical graph regenerations, after which full file/source-span
      validation passed; and
    - 17 Phase B, three Phase A, and 12 dependency-tool tests passed together
      with version-record, changed-link, absolute-path, Python syntax,
      SVG-background, whitespace, and `git diff --check` audits.

Gate B passed under the Author's explicit authorization to check in and push
this work without personal review. The next phase still requires its own
detailed written plan before implementation begins.

### Phase B explicit exclusions

- No periodic timer, frame-service task, background primitive queue execution,
  frame counter, background completion behavior, logical swap-at-frame-edge, or consumer
  notification. Those begin in Phase C.
- No palette mutation/quantization service, Copper signal-list compositor,
  hardware sprite/cursor presentation overlay, or sink output format. Those
  begin in Phase D or later.
- No edits to official `agon_screen.h`, official mode table/fallback, VDU
  dispatch, contexts, Teletext, callbacks, MOS, or EDU/VDU operating modes.
  Official integration remains Phase E.
- No network/browser, RGB, MIPI-DSI, HDMI, audio, input, storage, updater, or
  transport implementation; no classic physical driver or compatibility stub.
- No vendored source edit, physical deployment, runtime P4 qualification, or
  new firmware/version/build identity.

### Gate B acceptance criteria

1. Every codec round-trips all legal values and matches independent native-byte
   goldens across packed boundaries and odd dimensions.
2. Transactional single/double-plane allocation, initialization,
   reconfiguration, release, and every injected failure leave a valid,
   leak-free controller state in host evidence.
3. Retained common primitives and all Phase B raw/readback operations match
   independent deterministic goldens at every native depth; any intentionally
   deferred method remains visibly unavailable and is outside the claimed
   matrix.
4. The synchronous controller never depends on a frame clock, sink, classic
   VGA physical engine, or another excluded subsystem.
5. A clean pinned P4 diagnostic build proves the selected application/link
   closure without vendored edits, deployment, or runtime claims.
6. Provenance, dependency selection, compatibility delta, generators, and tests
   are deterministic, complete, and free of unexplained declared-versus-
   observed drift.

### Phase B stop conditions

Stop for review if faithful native storage or renderer behavior requires
changing an accepted pixel contract, retaining a classic physical controller,
editing vendored source, implementing a frame service/sink/official facade,
making a SETUP-005 mode decision, or inventing compatibility behavior without
an independent oracle. Also stop if the actual common renderer cannot be host-
tested without broad unrelated subsystem emulation, if target allocation
constraints invalidate the accepted storage architecture, or if a material
primitive/readback difference cannot be isolated and measured.

## Phase C — Logical frame service

- Status: Complete — Gate C passed
- Started: 2026-08-22 13:49 EDT
- Finished: 2026-08-22 21:17 EDT

The Author explicitly authorized this phase to proceed, including check-in,
without personal review after Gate B passed. This checklist is the controlling
review surrogate. Consult it before every action, record results against the
same item, and stop rather than expanding logical frame service into palette,
official-facade, sink, transport, or operating-mode work.

Phase C adds sink-independent logical time and bounded asynchronous work to the
qualified Phase B renderer. It owns timer notification, frame-service task
execution through unchanged common queue semantics, logical buffer swaps,
the writable compatibility frame counter, provisional latest-generation
publication, and null/slow mock consumers. It does not compose presentation
pixels or implement a physical consumer.

On 2026-08-22 the Author ordered the corrective action recorded by
`CA-2026-08-22-001`. The strict candidate must retain upstream queue-depth
waiting, swap notification, background draining, dynamic payload, and
one-tick/one-edge behavior. The rejected stronger completion candidate remains
in commit `8aecb0e` and is promoted to the independent `UPSTREAM-001` A/B task.

### Detailed execution checklist

1. [x] Freeze this detailed scope, package/evidence layout, authority, oracle
   order, physical-qualification preconditions, and stop rules before changing
   production code. Record the Author's no-review authorization and keep the
   accepted ADR-0015 lifecycle ordering normative.
2. [x] Generate a bounded, deterministic Phase C provenance inventory from the
   existing symbol/source graph. Fingerprint the exact upstream queue,
   background primitive, swap, frame-counter, wait, callback, and teardown
   spans. Classify behavior separately from the old VSYNC ISR, I2S/DMA engine,
   Xtensa synchronization, and physical timing source; do not compile or copy
   the latter merely because they share a file.
3. [x] Define contracts before implementation for:
   - unchanged upstream queue-depth waits, swap notification, background
     draining, dynamic payload lifetime, and mode teardown;
   - single-buffer frame waits and double-buffer drawing/visible-plane swaps;
   - writable modulo-2^32 compatibility frame count and independent monotonic
     publication generation;
   - one-logical-edge-per-recorded-tick accounting and backlog handling;
   - a short timer-notification boundary and one frame-service owner;
   - bounded latest-generation consumer notification, drop accounting, and
     lease/pointer lifetime; and
   - transactional startup/reconfiguration/stop around the retained upstream
     lifecycle and last valid renderer state.
4. [x] Build an independent deterministic host model and trace fixtures before
   trusting production scheduling code. Cover exact event order, upstream
   queue-depth wait behavior, dynamic payload lifetime, single-buffer
   next-edge waits, double-buffer swap visibility, frame-count writes and
   rollover, generation publication, null/slow/disconnecting consumers,
   accumulated ticks as distinct edges, teardown draining, and bounded memory.
   Expected traces must come from the written contract or reviewed upstream
   behavior, never production output.
5. [x] Extend Phase B storage/controller seams only as required by those
   contracts. Add transactional drawing/visible-plane exchange and explicit
   logical frame-counter access without importing palette/Copper/overlay or
   official `agon_screen.h` behavior. Preserve synchronous execution as a
   selectable test/lifecycle state and make invalid direct swap paths fail
   visibly.
6. [x] Implement a platform-neutral logical frame state machine plus the
   narrowest ESP32-P4 adapter: `esp_timer` callback records elapsed ticks and
   wakes one FreeRTOS frame-service task; only that task runs frame-boundary
   work. Timer and sink callbacks must never render, swap planes, or publish
   mutable storage.
7. [x] Integrate retained Canvas/common background primitive execution without
   modifying it. Preserve queue-depth waiting—including its already-dequeued
   behavior—ordinary single-buffer FIFO work, immediate double-buffer drawing,
   immediate post-swap submitter notification, upstream stop draining, dynamic
   payload cleanup, and trailing single-buffer `Refresh` behavior.
8. [x] Add a provisional sink-neutral publication contract and null, fast,
   slow, disconnecting, and reconnecting mock consumers. Notifications must be
   latest-state and bounded; consumers may record drops but cannot block the
   frame service, retain mutable logical storage indefinitely, alter frame
   count, or create an unbounded queue. Interface freeze remains Phase F.
9. [x] Run deterministic host concurrency/stress qualification under
   sanitizers and explicit allocation/thread accounting. Exercise adversarial
   interleavings, rollover, repeated start/stop/reconfigure, forced tick bursts,
   slow consumers, upstream lifecycle draining, and long bounded runs; reject
   deadlock, stale-plane access, leaks, or growth with elapsed
   frames.
10. [x] Add a dedicated Phase C P4 diagnostic/qualification environment and
    prove the exact compile/link closure without deployment. Update the
    dependency graph, source-selection projection, compatibility delta, task
    record, and development log. Once host and clean target gates pass, create
    and push a pre-qualification checkpoint and assign the human-readable
    firmware/build/test identities required by `docs/versions/README.md`.
11. [x] Before physical work, reread `HARDWARE.local.md`, verify the named Pi,
    P4 identity, connection, toolchain, and safety boundary, then deploy only
    the committed qualification artifact. No backup of the pre-existing P4
    firmware is required. Measure sink-free cadence, jitter, drift, rollover
    seam, accumulated-tick backlog, null/slow consumers, teardown,
    and memory bounds at the accepted 360 MHz configuration; preserve serial
    capture and structured run evidence. Stop on identity mismatch, unstable
    power/transport, unexplained reset, or a result requiring contract change.
12. [x] Regenerate all Phase C and canonical graph artifacts twice
    byte-identically; verify immutable imports and index, schemas/source spans,
    host and target evidence, all permanent tests, links, absolute paths, SVG
    backgrounds, whitespace, and staged diff. Mark Gate C complete and commit
    and push the final evidence only if every criterion below passes.

### Gate C closure record

Gate C passed on 2026-08-22. The Phase C lifecycle, independent traces, host
results, target closure, canonical dependency graph, and PORT-003 projections
all regenerated twice byte-identically. The exhaustive source validator
matched all 5,164 immutable imported files and every recorded source span;
index verification found no omitted import.

The final suites passed 13 dependency-tool, three Phase A, 17 Phase B, and 11
Phase C permanent tests, plus 12 ASan/UBSan logical-frame traces, five retained
controller cases, three stress cases, and the nine-unit/eight-symbol/zero-
exclusion P4 closure. Run `PORT-003-2026-08-22-23-58-56Z` supplies the passing
target evidence, and its generated index binds the authoritative manifest by
SHA-256.

The audit found and corrected one generator-order issue: regenerating target
closure after the canonical graph left the graph's input fingerprint stale.
The enforced closure order is now Phase C evidence, canonical dependencies,
then PORT-003 projections. Current Markdown links pass outside intentionally
verbatim legacy-evidence excerpts; local identity/path leakage, SVG white
backgrounds, evidence hashes/sizes, schemas, whitespace, and the complete diff
also pass.

### Phase C explicit exclusions

- No palette mutation, Copper lists, presentation composition, hardware
  sprites/cursors, or output pixel format; those remain Phase D.
- No official mode table/fallback, `agon_screen.h`, contexts, callbacks,
  Teletext, VDU dispatch, MOS, or EDU/VDU operating-mode integration; those
  remain Phase E or SETUP-005.
- No browser/network, RGB, MIPI-DSI, HDMI, audio, input, storage, updater, or
  transport implementation and no classic VGA/CVBS physical engine.
- No frame consumer API freeze, production sink, or claim that host scheduling
  proves target cadence. Phase F owns final consumer handoff.
- No vendored lifecycle source edit is permitted. No uncommitted or
  unidentified firmware may be used for a qualified physical run.

### Phase C decision register

| ID | State | Decision requested |
|---|---|---|
| `PORT-003-D008` | Superseded | The proposed vdp-gl lifecycle patch is excluded from the strict-compatible product baseline and preserved under `UPSTREAM-001`. |
| `PORT-003-D009` | Accepted | Retain upstream common queue, completion-wait, swap-notification, background-lifecycle, and payload behavior unchanged; replace only the unavailable physical executor. |

`PORT-003-D008` was accepted on 2026-08-22 because the retained common methods
are non-virtual and their queue state is private. Corrective review established
that the proposed hooks were being used to improve inherited completion and
notification semantics even though the P4 can execute the common queue code as
written. The Author therefore superseded D008 with D009 on 2026-08-22.

D009 uses no linker interposition, queue interception, copied common
translation unit, or vendored lifecycle patch. The P4 task replaces the
unavailable physical executor through existing protected common seams while
the inherited queue-depth wait and swap notification remain authoritative.
The former correction candidate is recoverable from commit `8aecb0e` and has a
separate A/B regression path in `UPSTREAM-001`; it is not discarded or silently
represented as product compatibility.

### Original Phase C candidate record — superseded by corrective action

The following record describes commit `8aecb0e` and is retained as the exact
input to `UPSTREAM-001`. Its D008 completion, notification, coalescing, and
cancellation claims are not current product architecture.

1. Scope and plan freeze — complete:
   - the 12-item checklist, package boundary, gate criteria, explicit
     exclusions, physical-run checkpoint, and stop conditions were written
     before production changes; and
   - the Author's explicit no-review authorization is recorded while material
     stop conditions remain binding.

2. Frame-lifecycle provenance — complete:
   - `phase-c/scripts/extract-frame-lifecycle.py` deterministically fingerprints
     33 callable/source-region records across 13 pinned official files;
   - the records distinguish six retained common contracts, six official
     facade contracts, ten common sequence adaptations, one logical swap,
     three platform-task replacements, and seven physical-trigger exclusions;
   - four permanent tests verify tuple uniqueness, every file/span hash,
     critical dispositions, and the queue-race/override findings, and a second
     generation was byte-identical; and
   - the trace proves old frame edges increment `frameCounter` before waking or
     executing bounded work, swaps change visible identity before notifying,
     and `primitivesExecutionWait()` observes only queued count. Because a
     dequeued primitive is absent while still executing, the latter is not a
     valid completion proof.

3. Contracts — complete:
   - `phase-c/contracts.md` freezes execution ownership, elapsed-tick and
     overrun accounting, 32-bit writable frame count, 64-bit publication
     generation, FIFO sequence completion, single/double-buffer behavior,
     transactional lifecycle, and bounded metadata-only mock consumers; and
   - the contract identifies the exact private/non-virtual common-code boundary
     that cannot be completed solely in the existing P4 subclass; and
   - the Author accepted `PORT-003-D008`: a minimal annotated common-code patch
     with default-no-op lifecycle hooks and virtual completion waiting, leaving
     stock behavior unchanged for every non-P4 controller.

4. Independent event traces — complete:
   - `phase-c/scripts/generate-frame-traces.py` is a pure written-contract model
     that imports no production frame-service code or output;
   - 12 fixtures cover sink-free and coalesced ticks, frame-counter writes and
     rollover, dequeued-but-incomplete work, FIFO budgets, single-buffer Flush,
     double-buffer immediate drawing/swap, latest-only slow consumers,
     disconnect/reconnect, later tick arrival, and teardown payload release;
   - expected ordering places swap visibility before publication and
     publication before completion, while a started primitive remains an
     unsatisfied wait target until execution returns; and
   - six fixture tests plus the four provenance tests pass, and independent
     regeneration is byte-identical.

5. Storage and controller seams — complete:
   - `PlaneStorage` now owns explicit drawing and visible identities and
     performs a constant-time logical exchange only in double-buffered modes;
   - `P4DisplayController` exposes the Phase C frame descriptor and writable
     compatibility counter while rejecting reconfiguration during an active
     frame lifecycle; and
   - the synchronous Phase B lifecycle remains available after stop. An
     inherited upstream disable-ordering quirk queues one trailing `Refresh`;
     the controller prominently drains/cancels it before establishing a clean
     lifecycle sequence baseline.

6. Logical service and P4 adapter — complete:
   - `LogicalFrameService` is platform-neutral, uses a bounded eight-slot
     consumer registry and 32-bit lock-free tick accumulator, and maintains a
     separate 64-bit publication generation;
   - one service pass advances elapsed logical time, executes bounded work,
     observes any swap, publishes immutable metadata, and only then completes
     the executed sequences; and
   - `P4FrameService` confines `esp_timer` to tick recording/task wakeup. Its
     sole FreeRTOS owner task is joined before stop cancels queued payloads.

7. Retained queue integration — complete:
   - accepted seam `PORT-003-D008` adds default-no-op reservation, enqueue,
     start, completion, cancellation, notification-deferral, and virtual-wait
     hooks to the two common vdp-gl controller files;
   - P4 accounting distinguishes pre-send reservation from successful queue
     acceptance, including the narrow worker/sender handoff race, and does not
     report a dequeued primitive complete until execution and publication
     finish; and
   - teardown releases copied path/matrix payloads without executing stale
     work and wakes cancelled completion/swap waiters.

8. Provisional consumers — complete:
   - publications contain metadata only and expose no mutable framebuffer
     lease; the service writes fixed-capacity mailboxes and never invokes sink
     code;
   - null, polled, unconsumed, slow, disconnected, and reconnecting cases
     retain bounded latest-state behavior and explicit per-consumer drops; and
   - the contract remains deliberately provisional until Phase F supplies a
     real sink and freezes the handoff API.

   Pre-candidate audit rejected the first implementation even though its host
   fixtures passed: it called a nominally non-blocking virtual consumer method
   directly from the service task, so a misbehaving or merely slow sink could
   stall logical time. The replacement contains no consumer callbacks. It uses
   fixed latest-notice mailboxes whose producer lock is attempted once; busy
   or unconsumed slots report drops while the service continues. The retained
   tests were adapted to observe those production mailboxes without changing
   the independently generated expected traces.

9. Host concurrency and stress qualification — complete:
   - all 12 independent oracle fixtures pass under ASan/UBSan;
   - five retained Canvas/controller cases prove dequeued completion, double
     swaps, single-buffer edges, suspension, cancellation, restart, and
     reconfiguration behavior; and
   - three adversarial cases prove a concurrent 200,000-tick burst, saturated
     accounting across 1,000 lifecycles, and bounded consumer registration.
     LeakSanitizer is unavailable under managed tracing; Phase B allocation
     accounting continues to cover owned framebuffer allocations.

10. Target compile/link closure — complete:
    - `p4-frame-service` selects nine application translation units and links
      the retained common Canvas/controller implementation without a physical
      output sink;
    - the clean pinned target build succeeds at the qualified 360 MHz board
      profile, and machine validation proves required service symbols plus
      exclusion of classic VGA/CVBS, physical input, audio, network, and
      storage families; and
    - the dependency graph now represents vdp-gl as `vendored-patched`, permits
      only the two D008 paths to differ, records both upstream and repository
      hashes, and regenerates byte-identically.
    - the Author approved candidate identities
      `port-003-frame-service-canary-r01` and
      `p4-frame-service-qualification-r01`; registry `r06` and the committed
      qualification procedure define their exact scope.

### Corrective execution record — maintained corrected candidate

On 2026-08-22 the Author approved `CA-2026-08-22-001` and superseded D008 with
D009. The corrective implementation:

1. restored `vdp-gl` `displaycontroller.h` and `displaycontroller.cpp`
   byte-for-byte to pinned `all-the-plots` and returned the complete managed
   vdp-gl import to `vendored` status;
2. removed P4 reservation/submission/start/completion sequences, virtual
   completion waiting, deferred swap notification, queued-payload cancellation,
   and the extra trailing-`Refresh` drain;
3. retained the necessary P4 physical-executor replacement through upstream's
   existing protected task-context dequeue and primitive executor;
4. changed accumulated ticks to distinct logical edges, each advancing the
   compatibility counter once, receiving one bounded renderer opportunity, and
   publishing one generation;
5. retained the Extender-owned bounded mailbox strictly after common primitive
   execution, so it changes no queue wait or swap notification; and
6. registered `UPSTREAM-001` with exact commit provenance and stock/patched A/B
   regression gates for a possible upstream contribution.

Corrected host evidence passes all 12 upstream-constrained traces, five
retained-controller cases, three stress cases, and ten Phase C provenance and
fixture tests under ASan/UBSan where applicable. A P4 diagnostic build succeeds
with nine selected application units; closure evidence proves all eight
required symbols—including the unchanged upstream wait and task-context
dequeue—and zero excluded physical families. The complete dependency pipeline
regenerates byte-identically with 5,164 pristine managed files, and all 17
Phase B provenance tests pass against the restored source.

This build is diagnostic only. The old `port-003-frame-service-canary-r01` and
`p4-frame-service-qualification-r01` identities describe the superseded D008
candidate and are rejected. The Author approved corrected candidate identities
`port-003-frame-service-canary-r02` and
`p4-frame-service-qualification-r03` in registry r09. Procedure r03 preserves
r02's firmware contract while controlling the attached `light2-harness-r01`,
`la03-p4-probe-fixture-r01`, and disconnected-Agon boundary. The coherent
candidate was committed and pushed as `ca0538a`; run
`PORT-003-2026-08-22-23-58-56Z` subsequently passed physical qualification.

### Gate C acceptance criteria

1. Host traces prove one-edge-per-tick progression, retained upstream queue
   waits and swap notification, task-context work, and publication ordering
   without implementation-derived expectations.
2. Single-buffer FIFO work and double-buffer swaps execute at a logical edge;
   drawing/visible identities and upstream payload lifetimes remain valid under
   concurrency, draining, reconfiguration, and teardown.
3. Frame count accounts for every logical tick modulo 32 bits without
   coalescing edges; publication generations remain monotonic and report
   consumer drops explicitly.
4. Null, slow, disconnected, and reconnecting mock consumers cannot block
   logical progress, grow memory without bound, or retain mutable storage past
   the defined access lifetime.
5. A clean pinned P4 build proves the selected closure, and a committed,
   versioned bench run measures accepted cadence/backlog bounds at 360 MHz with
   no physical sink, deadlock, or unexplained reset.
6. Provenance, dependency selection, compatibility delta, generators, tests,
   host evidence, and target evidence are deterministic and contain no
   unexplained declared-versus-observed drift.

### Phase C stop conditions

Stop for Author review if the phase requires changing ADR-0015 ordering,
letting a sink or timer callback own logical progress, editing vendored source
for lifecycle behavior,
adding a presentation compositor or official facade, choosing SETUP-005 mode
policy, exposing an unbounded queue or mutable indefinite frame lease, or
claiming compatibility without an independent trace oracle. Also stop if
retained Canvas queue semantics cannot be separated from the classic physical
engine by a narrow evidenced seam, if clean target compilation invalidates the
host architecture, or if physical qualification reveals a material cadence,
completion, reset, memory, or concurrency failure that cannot be isolated
without changing the accepted contract.

## Phase D — Palette, Copper, and overlays

- Status: Complete — Gate D passed
- Started: 2026-08-24 05:44 EDT
- Finished: 2026-08-24 06:42 EDT

The Author authorized this phase to proceed unattended after the returned EMOS
implementation froze Extender commit `10f2eb2`. The maintained EMOS source
commit `a8dc891` and build/qualification commit `b12fcab` are provisional
downstream references, not Phase D implementation inputs. PORT-201 and
PORT-203 evidence is required only for later claims that depend on broad EMOS
parity or physical EMOS/EDP transport; this mode-neutral presentation phase
makes neither claim.

This checklist is the controlling review surrogate. Complete one numbered
item at a time, then reread `TODO.md`, this task state, and the Phase D gate
before beginning the next item. Stop rather than silently absorbing Phase E,
Phase F, transport, output-sink, or operating-mode work.

### Detailed execution checklist

1. [x] Freeze the Phase D task-local structure, exact scope, contracts, oracle
   order, planned production seams, evidence families, exclusions, stop rules,
   and commit boundary under `PORT-003/phase-d/` before changing production
   code. Record the Author's unattended authorization and required post-item
   TODO reread.
2. [x] Generate a bounded deterministic provenance inventory for palette
   allocation/mutation, RGB222 quantization, Copper signal-list resolution,
   logical readback, software sprites, hardware sprites, text cursor, and mouse
   cursor. Fingerprint exact official VDP/vdp-gl `v2.16.0`/`all-the-plots`
   source spans and separate retained observable behavior from excluded VGA
   signal tables, DMA scanout, and ISR mechanics.
3. [x] Generate independent palette, Copper, logical-readback, and overlay
   fixtures before trusting production output. Cover every native depth,
   single/double buffering, duplicate colors, index wrapping, implicit palette
   creation, allocation failure, all-delete, unknown/deleted signal-list IDs,
   short/long/zero-row lists, clipping, alpha, XOR, and overlay order. Golden
   results must come from the written contract or source-derived model, never
   from the implementation under test.
4. [x] Implement allocator-injected project-owned palette/Copper state. Preserve
   the stock 16-bit palette-ID domain, palette-0 protection, copy-on-create,
   RGB222 output quantization, explicit lookup rebuild, unknown/deleted-ID
   fallback, final-span extension, and mode-reset behavior. Keep palette 0's
   drawing LUT distinct from secondary presentation palettes.
5. [x] Implement one pure row/region presentation compositor over explicit
   logical-plane, mode, palette/Copper, and overlay inputs. Emit RGB888 without
   modifying logical storage. Keep the compositor independent of FabGL
   controller inheritance, frame timing, transport, network, panel, and sink
   ownership.
6. [x] Integrate palette and compositor seams narrowly into
   `P4DisplayController`. Preserve ordinary `readScreen()` and native-save
   behavior as palette-0 logical views. Preserve unchanged common software
   sprite drawing, and compose text cursor, ascending hardware sprites, and
   mouse cursor after Copper conversion using exact upstream clipping,
   transparency, overwrite, and RGBA2222-XOR rules.
7. [x] Define and test the Phase D quiescent composition boundary. Palette,
   Copper, and overlay inputs must be coherent for one composition call, but no
   sink may receive a mutable framebuffer pointer or enter the frame-service
   task. Do not freeze a consumer lease, callback, output format family, or
   long-lived storage contract; Phase F owns that handoff.
8. [x] Run the complete host matrix under ASan/UBSan and explicit allocation
   accounting. Prove palette/readback independence, Copper-only presentation
   changes, software-versus-hardware sprite placement, cursor ordering,
   clipping, single/double visible-plane selection, reset, repeated mutation,
   and all injected allocation failures without leaks or stale state.
9. [x] Add a dedicated `p4-presentation` diagnostic environment and exact
   machine-readable source selection. Compile the Phase C frame service plus
   Phase D state/compositor and unchanged retained Canvas/common controller;
   prove the build excludes classic VGA/CVBS/Scene/PS2, physical audio,
   network, storage, official facade, and every physical output sink. Do not
   deploy or assign a qualification identity.
10. [x] Update canonical dependency/provenance records, source-selection
    projections, compatibility delta, architecture-facing task evidence, and
    the dated development log. Record every unavoidable replacement and any
    inherited upstream defect or unsafe implementation detail beside the code
    and in task evidence without claiming a behavior improvement.
11. [x] Regenerate every Phase D and canonical artifact twice byte-identically;
    verify all immutable imports, source spans, schemas, permanent tests,
    changed links, machine-path absence, white SVG backgrounds, project-owned
    whitespace, and `git diff --check`.
12. [x] Audit the staged Phase D boundary against this checklist and Gate D.
    Commit and push one coherent Phase D result only when every criterion below
    passes. Then reread the authoritative TODO/task documents before planning
    Phase E.

### Phase D execution record

1. Scope and contract freeze — complete:
   - `phase-d/README.md`, `contracts.md`, and
     `implementation-manifest.yaml` define the bounded role-named package,
     planned production seams, independent-oracle rule, output-sink/lease
     deferrals, exact exclusions, and one coherent Phase D commit boundary;
   - the synchronous controller composition seam is explicitly quiescent
     qualification machinery, not the Phase F consumer API; and
   - the returned EMOS commits are recorded only as provisional downstream
     context, with no parity, transport, or hardware claim entering this phase.
2. Presentation provenance — complete:
   - `extract-presentation-provenance.py` deterministically fingerprints 47
     exact callable/source-region records across 11 official VDP/vdp-gl files
     plus the canonical Copper documentation hash;
   - records distinguish retained facade/common/readback behavior, adapted
     palette and overlay algorithms, project-owned allocation/composition
     replacements, and five excluded classic physical-engine regions;
   - four permanent tests verify tuple uniqueness, every file/span hash,
     critical retained/adapted/excluded records, and the logical-versus-
     presentation split; and
   - the first invocation used the system Python, which lacks the project's
     pinned YAML dependency. The accepted process uses `.venv/bin/python`.
     The generator derives the canonical `agon-docs` sibling location from the
     workspace root and records only repository-relative documentation paths,
     keeping machine topology out of generated evidence.
3. Independent presentation fixtures — complete:
   - the pure Python source-derived model generates nine palette-state cases,
     eight composition cases, and two allocation-failure cases across all five
     native depths and both buffering states;
   - fixtures cover copied/implicit palettes, wrapped entries, explicit LUT
     rebuild, unknown/deleted IDs, all-delete, empty/zero-row/short/extended
     Copper lists, direct RGB222, visible-plane selection, alpha, XOR, clipping,
     software exclusion, and text/hardware/mouse ordering;
   - five generator tests prove case/hash uniqueness, complete format and
     buffering coverage, required edge cases, overlay dimensions, and oracle
     independence; all nine Phase D tests pass and a second generation is
     byte-identical; and
   - the model records upstream's explicit integer-truncated HSV-distance LUT
     rule rather than retaining Phase B's temporary full-double helper. Exact
     default-palette arithmetic produces the same selected entries, but the
     integer boundary remains part of mutable-palette compatibility and is now
     tested as such.
4. Palette and Copper state — complete:
   - new project-owned `PaletteState` uses one embedded primary palette and
     reset span plus allocator-injected secondary nodes and multi-span lists;
     it preserves all 16-bit IDs without imposing a project capacity limit;
   - copy-on-create/recreate, wrapped writes, implicit creation, RGB222
     quantization, explicit integer-distance LUT rebuild, palette-0 protection,
     robust all-delete, unknown-ID resolution, delete fallback, zero-row/final
     span behavior, and allocation-preserving updates are implemented without
     classic signal maps;
   - fixed RGB222 modes reject palette/Copper mutation and convert drawing
     colors directly; successful controller reconfiguration can reset the
     complete palette state without another allocation boundary; and
   - the standalone ASan/UBSan C++ test passes exact defaults, the retained
     integer-HSV tie decision, lifecycle, signal, late-create, deletion,
     fixed-mode, and both injected allocation failures with zero live
     allocations at teardown.
5. Pure presentation compositor — complete:
   - new project-owned `PresentationCompositor` consumes only explicit native
     plane, mode, palette/Copper, region, overlay, and caller-owned RGB888
     views; it owns no framebuffer, task, timing, transport, controller, sink,
     or output-device lifetime;
   - base conversion leaves logical bytes untouched and applies Copper
     palettes by absolute display row, while independently ordered overlay
     calls preserve clipping, alpha, overwrite, and RGBA2222-XOR rules;
   - dimensions, arithmetic, enum values, source extents, destination extents,
     native stride, and native storage are checked before access, including
     adversarial coordinate and overflow paths; and
   - the standalone ASan/UBSan test passes Copper conversion, exact stock
     palette order, clipped transparency, XOR-after-Copper behavior, and
     invalid-region/invalid-format rejection. LeakSanitizer itself cannot run
     under the execution harness's ptrace boundary; project allocator leaks
     remain covered explicitly and the final host matrix will repeat that
     accounting.
6. Retained-controller integration — complete:
   - `P4DisplayController` now owns `PaletteState`, resets it only after a
     successful transactional mode allocation, and exposes the narrow palette,
     LUT, and Copper mutation seams required by the later official facade;
   - drawing conversion, `readScreen()`, and native-save conversion use only
     palette 0, while composed presentation borrows the visible plane and
     applies text cursor, ascending hardware sprites, and mouse cursor in exact
     retained order; unsupported hardware-overlay bitmap formats remain
     ignored as they are upstream;
   - common software-sprite save/draw/restore code remains unedited and outside
     the compositor; no classic controller, sink, frame callback, transport,
     or facade was introduced; and
   - ASan/UBSan retained-controller tests pass the complete Phase C queue/frame
     regression plus Copper/readback separation, secondary-palette
     independence, and text/hardware/mouse ordering through the integrated
     controller seam.
7. Quiescent composition boundary — complete:
   - the synchronous controller seam accepts composition only with the frame
     service stopped or controller background execution disabled/suspended;
     an active unsuspended service returns `NotQuiescent` before frame state is
     borrowed;
   - the actor contract requires the caller to retain that state and own all
     palette, bitmap, sprite, and cursor mutation until the call returns; only
     copied RGB888 values leave the boundary;
   - a sanitizer-backed integration test proves stopped, rejected-running, and
     explicitly suspended-running cases; and
   - this is intentionally a Phase D misuse detector, not a sink callback,
     mutable frame lease, long-lived pointer, output-format family, or Phase F
     consumer contract.
8. Complete host presentation matrix — complete:
   - `run-host-presentation-tests.py` generates a temporary C++ fixture driver,
     compiles production palette/codec/compositor code under ASan/UBSan, and
     compares all nine palette cases, eight composition cases, and two
     allocation-failure cases with the independent YAML oracle;
   - three fixed harnesses additionally prove controller integration,
     quiescence, exact overlay order, software-versus-hardware placement,
     drawing-versus-visible double-buffer selection, and explicit allocation
     teardown; Phase B's complete native/primitive suite and Phase C's 12
     logical-frame fixtures also pass after their retained-controller source
     closures were updated;
   - cross-phase regression caught an uncommitted P8/P16 default-palette error:
     the first Phase D implementation and oracle both packed red/blue in the
     wrong lanes. Official controller defaults and the independent Phase B
     suite identified the shared error; both Phase D sources were corrected
     before evidence was accepted; and
   - the same audit corrected two fixture-schema ambiguities: Copper row
     expectations now retain their queried rows, and double-buffer logical
     readback is explicitly generated from the drawing plane while composed
     presentation is generated from the visible plane. All project-managed
     allocations return to zero; LSAN remains unavailable under managed
     tracing and is not claimed.
9. P4 compile and link closure — complete:
   - the dedicated `p4-presentation` environment compiles and links the Phase C
     frame service, Phase D palette/compositor/controller seams, retained
     Canvas/common controller, and a compile-only presentation canary as 11
     exact machine-readable translation units;
   - deterministic ELF/map validation proves all nine required retained and
     project-owned seams are linked, while classic VGA/CVBS/Scene/PS2, physical
     audio, network, storage, official facade, and output-sink source/symbol
     families remain absent;
   - PlatformIO initially retained its globally installed Arduino 2.0.14
     framework package despite the project's Arduino 3.3.11 platform pin. A
     package URL install reported success without replacing the shared package;
     explicitly uninstalling that global package allowed the project build to
     install and use its pinned framework. This is a PlatformIO package-cache
     behavior, not a source workaround; and
   - the resulting binary is evidence from a sink-free compile/link diagnostic
     only. It was not assigned an artifact identity, deployed, or physically
     qualified.
10. Durable dependency and compatibility records — complete:
    - the canonical dependency graph now consumes the Phase D build closure,
      projects the presentation canary, palette state, compositor, controller,
      frame service, and unchanged retained/vendored units as explicit build
      units, and carries those relationships into the task-facing slices;
    - `phase-d/compatibility-delta.md` separates retained observable behavior
      from the unavoidable project-owned VGA-physical replacements and from
      Phase E/F, sink, transport, MOS/EMOS, and physical-qualification deferrals;
    - the completed implementation manifest, source selections, generated
      provenance, and dated development log record no vendored patch and make
      the diagnostic-only evidence boundary explicit; and
    - the current pioarduino package layout splits Arduino sources from the
      architecture libraries. The task evidence generator correctly requires
      `framework-arduinoespressif32-libs` as its P4 capability root; passing the
      similarly named Arduino source package fails immediately on the first
      missing ESP-IDF capability header and does not produce accepted evidence.
11. Deterministic final validation — complete:
    - Phase D provenance, independent fixtures, host results, and build/link
      evidence each regenerated twice with identical SHA-256 results; the
      canonical dependency and PORT-003 task projections each passed their
      built-in two-pass byte-identity checks;
    - all 53 permanent PORT-003 Phase A–D and dependency-tool Python tests pass;
      the Phase D host run passes 19 generated fixtures and three fixed C++
      harnesses under ASan/UBSan, including the complete Phase B native/render
      and Phase C logical-frame regressions;
    - because the shared controller now depends on Phase D palette/compositor
      units, the Phase B and C source selections, P4 builds, ELF/map validators,
      and tracked closure evidence were rebuilt rather than left describing
      stale pre-Phase-D link sets. They prove 9 and 11 exact application units,
      respectively, with all required symbols and zero excluded families;
    - all six Phase D YAML records parse, canonical graph schemas and source
      imports validate, all changed local Markdown targets exist, generated
      SVGs retain explicit white backgrounds, and no machine-local path or
      vendored-source edit entered the change; and
    - project whitespace and `git diff --check` pass. No target was deployed,
      no physical run was performed, and no Phase E/F or transport contract was
      selected.
12. Gate D audit — complete:
    - the final boundary contains only Phase D palette/Copper/composition code,
      its compile-only canary and exact source selections, deterministic
      fixtures/evidence/generators/tests, the required Phase B/C closure refresh,
      canonical dependency projections, task records, and the dated log;
    - all six Gate D criteria are independently evidenced: palette-0 logical
      fidelity, Copper presentation behavior, software/hardware overlay split,
      drawing/visible plane separation, bounded allocation failure, and clean
      pinned P4 compile/link closure;
    - every explicit exclusion and stop condition remains intact. In
      particular, no vendored byte, official facade/parser, transport, EMOS,
      operating-mode policy, physical sink, consumer lease, deployment, bench
      operation, artifact identity, or hardware claim entered the phase; and
    - Gate D passed at 2026-08-24 06:42 EDT under the Author's unattended
      authorization. Phase E remains a separate post-commit planning boundary.

### Phase D gate criteria

1. Palette-0 drawing quantization and logical readback match independent
   expectations at all five native depths; secondary palettes never rewrite
   logical bytes.
2. Copper composition matches documented row-count/palette-ID behavior,
   including fallback and reset, while fixed 64-color presentation remains
   direct RGB222.
3. Software sprites remain in unchanged common framebuffer handling, while
   hardware sprites and both cursors appear only in composed presentation in
   exact stock order and color-operation semantics.
4. Single- and double-buffer tests distinguish drawing and visible planes and
   prove composed output independently from logical readback.
5. Allocation failures and repeated palette/signal-list changes leave valid,
   bounded state with no vendored source edit or classic physical dependency.
6. A clean pinned P4 diagnostic build and deterministic host evidence prove
   the declared closure without deployment, output-sink, transport, EMOS
   parity, or hardware-qualification claims.

### Phase D explicit exclusions

- No edit to immutable official VDP or vendored dependency bytes.
- No `agon_screen.h` facade, official mode table/fallback, context, callback,
  Teletext, VDU parser, MOS, EMOS, or operating-mode integration; those remain
  Phase E, PORT-008, or SETUP-005 work.
- No network/browser, RGB, MIPI-DSI, HDMI, or other physical output consumer.
- No frame-consumer API freeze, long-lived framebuffer lease, sink-owned
  buffer, or assertion that a Phase D quiescent composition call is the Phase F
  production handoff.
- No classic GPIO/I2S/DMA/VSYNC code, physical deployment, bench operation,
  artifact identity, or target runtime qualification.

### Phase D stop conditions

Stop for Author review if preserving observable behavior requires editing
vendored source, linking a classic physical controller, changing native bytes
or logical readback, letting composition or a sink block logical frame time,
freezing the Phase F consumer contract, choosing a Phase E facade or SETUP-005
mode policy, or inventing an application-visible command/protocol. Also stop
if an independently demonstrated palette/Copper/overlay difference cannot be
isolated and measured, or if target compilation invalidates the accepted
project-owned seam.

## Phase E — Official mode integration

- Status: Complete — Gate E passed
- Started: 2026-08-24 06:47 EDT
- Finished: 2026-08-24 07:46 EDT

The Author authorized this phase to proceed unattended after Phase D was
committed and pushed at `3599532`. The maintained EMOS source remains
`a8dc891`, its original returned build milestone is `b12fcab`, and the completed
PORT-200 qualification tip is `a695599`; all remain downstream context only.
This phase may prove the official display-facing command lifecycle without
claiming EMOS parity, a physical transport, or an assembled-system result.

This checklist is the controlling review surrogate. Complete one numbered
item at a time, then reread `TODO.md`, this task state, and the Phase E gate in
`qualification-plan.md` before beginning the next item. Stop rather than
silently absorbing Phase F, PORT-008, PORT-005, a physical output sink, or
operating-mode policy.

### Detailed execution checklist

1. [x] Freeze the Phase E task-local structure, exact official documentation
   and source inputs, actor-explicit contracts, oracle order, planned patched
   paths, exact exclusions, stop rules, and one coherent commit boundary under
   `PORT-003/phase-e/` before changing production code.
2. [x] Generate bounded deterministic provenance for the complete official
   mode table, modeline dimensions/cadence, `agon_screen.h` facade, `VDU 22`
   fallback sequence, context reset, callback removal/invocation, mode packet,
   Teletext initialization, cursor visibility, and input-owned cursor-position
   seam. Fingerprint exact `v2.16.0` source and documentation spans.
3. [x] Generate independent official-mode and lifecycle fixtures before
   trusting production output. Cover every documented current, legacy, and
   double-buffered mode; invalid modes; requested/old/default fallback paths;
   allocation/service-start failures; scales and rectangular pixels; Teletext;
   context and callback order; both double-buffer planes; cursor handling; and
   the exact eight-byte mode-information payload.
4. [x] Add the narrow project-owned screen-facade adapter. Parse only the
   dimensions and cadence encoded by the official retained modelines, map the
   five stock color depths to the retained native formats, configure one stable
   P4 controller transactionally, and start/restart the P4 logical frame
   service at the selected cadence. Return explicit facade errors without
   importing any classic VGA physical controller.
5. [x] Preserve the official writable 32-bit `frameCounter` source seam without
   modifying official context code. The P4 frame service and official direct
   low/high writes must observe one modulo-2^32 value, with deterministic host
   coverage for writes, reads, advancement, and rollover.
6. [x] Add only the display-facing processed cursor-position seam required by
   the official facade and mode lifecycle. It may bind, bound, and reposition
   the P4 display cursor, but must not add physical PS/2 acquisition, event
   routing, keyboard behavior, mouse packet generation, or PORT-005 policy.
7. [x] Apply the accepted narrow `agon_screen.h` patch with a prominent
   provenance header. Preserve official global names, factory/facade names,
   complete mode switch, palette/Copper helpers, Canvas ownership, dimensions,
   scaling, Teletext, waits, swaps, and error codes; change only the concrete
   controller, configuration, frame-service, and cursor bindings authorized by
   ADR-0013 and ADR-0015.
8. [x] Exercise the exact official `VDUStreamProcessor::vdu_mode` implementation
   and `sendModeInformation` packet construction against controlled host
   collaborators. Extract the pinned function bodies deterministically for the
   harness rather than copying or rewriting their behavior into production.
   Prove clear/wait, Teletext disable, VSYNC-callback removal, fallback,
   context reset, double-buffer initialization, cursor restoration/reset,
   mode-change callback, and packet order.
9. [x] Exercise Teletext mode 7 through the adapted official facade and
   ordinary retained Canvas path. Prove successful initialization, expected
   640x480/16-color mode metadata, transition out of Teletext, and controlled
   initialization failure without adding a text-mode physical driver.
10. [x] Run the complete Phase E host matrix under ASan/UBSan and explicit
    allocation accounting. Re-run Phases B–D regressions and prove repeated
    mode changes, all injected failures, frame-service restarts, fallback,
    context/callback/packet traces, cursor binding, and teardown leave valid
    bounded state.
11. [x] Add a dedicated `p4-official-display` diagnostic environment and exact
    machine-readable source selection. Compile the adapted official facade,
    Teletext implementation, P4 controller/frame service, and unchanged
    retained Canvas/common controller; prove old VGA/CVBS/Scene/PS2, audio,
    network, storage, updater, output sinks, and physical transport remain
    excluded. Do not deploy or assign a qualification identity.
12. [x] Update managed-import patch provenance, canonical dependency/source
    selection, compatibility delta, implementation manifest, task record, and
    dated development log. Every patched official byte must name its accepted
    decision and remain distinguishable from pristine vendored source.
13. [x] Regenerate Phase E and canonical artifacts twice byte-identically;
    verify immutable source spans, managed imports, schemas, all permanent and
    cross-phase tests, changed links, machine-path absence, generated SVG
    backgrounds, project whitespace, and `git diff --check`.
14. [x] Audit the staged Phase E boundary against this checklist and Gate E.
    Commit and push one coherent Phase E result only when every criterion below
    passes, then stop before PORT-008 as directed by the Author.

### Phase E execution record

1. Scope and contract freeze — complete:
   - `phase-e/README.md`, `contracts.md`, and the planned implementation
     manifest freeze the exact upstream identities, official document/source
     inputs, actor ownership, oracle order, one permitted patched path,
     exclusions, stop rules, and coherent commit boundary before production
     code changes;
   - exact official handler bodies may be extracted only into a temporary host
     harness, while fixtures remain independently generated and production
     continues to use the retained upstream files; and
   - no transport, EMOS parity, input-event implementation, consumer contract,
     physical sink, deployment, or hardware claim entered the phase.
2. Official mode and lifecycle provenance — complete:
   - `extract-mode-provenance.py` fingerprints 15 exact official source
     functions and five documentation regions covering the facade, complete
     mode switch, VDU lifecycle, packet, context, frame, Teletext, and cursor
     seams;
   - the extractor resolves all retained vdp-gl modelines into 58 current,
     legacy, and buffered variants spanning the complete 54-mode ID set, with
     explicit dimensions, depth, cadence, and buffering metadata;
   - four permanent tests prove mode-set completeness, variant counts, record
     uniqueness, critical lifecycle coverage, and parser reproduction; and
   - two complete generations produced byte-identical
     `mode-provenance.yaml` at SHA-256 `913bcf126cea1454c3576d59f739e154bd867cc2fdf3a7dd91bf09e77a1c3ace`.
3. Independent mode and lifecycle fixtures — complete:
   - `generate-mode-fixtures.py` independently transcribes the documented and
     frozen contract into all 58 mode variants plus seven VDU lifecycle cases;
   - coverage includes current/legacy modes, every supported buffered mode,
     60/70/75 Hz cadence, scales, rectangular pixels, Teletext, invalid mode,
     requested/old/default fallback, allocation/service failure, visible
     cursor, double-buffer initialization, and exact mode-packet bytes;
   - the independent table agrees exactly with the separately parsed official
     source table, while four permanent fixture tests enforce coverage, event
     order, packet shape, uniqueness, and generator reproduction; and
   - the first generator draft requested a nonexistent `canonical_json` helper
     from the dependency library. It now uses explicit sorted compact JSON only
     for the fixture-set digest and the established canonical YAML writer for
     output. Two generations produced byte-identical fixtures at SHA-256
     `d4fd0f87e76477b020d3940a8cf070b1012535d421cb68e42d18cd82542ffce9`.
4. P4 screen-facade adapter — complete:
   - `ScreenFacadeAdapter` parses only the quoted width, height, and refresh
     metadata retained in official modelines, maps all five stock color depths,
     and configures one stable `P4DisplayController` without selecting VGA
     electrical timing or a physical sink;
   - a callback binding names the P4 frame service as cadence owner, stops it
     before storage replacement, restarts it at the nearest integer-microsecond
     60/70/75 Hz period, and preserves/restarts the prior valid mode after
     injected storage or service-start failure whenever one exists;
   - target-only `screen_facade_p4_binding.cpp` isolates ESP-IDF dependencies
     from the host-qualifiable state machine, and typed results distinguish
     invalid depth/modeline, storage, service, and rollback failure; and
   - the sanitizer-backed fixed harness passes modeline/depth/period parsing,
     initial and replacement configuration, allocation preservation, service
     rollback, cadence, buffering, and zero-allocation teardown. The retained
     vdp-gl headers emit their known host portability warnings; no new warning
     or classic physical source is required by the adapter.
5. Writable official frame counter — complete:
   - public `FrameCounterRegister frameCounter` preserves the exact official
     `_VGAController->frameCounter` read and assignment expressions without an
     edit to `context.h`;
   - the register's atomic load, assignment, and fetch-add all address one
     unsigned 32-bit value, while the project-owned executor accessor was
     renamed `readFrameCounter()` to avoid shadowing that upstream field;
   - the sanitizer harness passes official-style direct assignment/read,
     low-word replacement, frame-service advancement, and modulo-2^32
     rollover; and
   - all 12 Phase C trace fixtures plus its retained-controller and stress
     regressions pass after the interface rename.
6. Display cursor-position endpoint — complete:
   - `CursorPositionAdapter` binds only the active P4 controller and mode
     bounds, clamps forwarded processed coordinates, and moves the EDP-local
     retained cursor overlay; it owns no device, events, packets, variables,
     callbacks, keyboard, transport, or routing;
   - upstream-shaped `resetMousePositioner()` and the separate position helper
     let unchanged official lifecycle callers reach this endpoint after the
     physical `agon_ps2.h` include is removed;
   - the first implementation attempted to inspect vdp-gl's private cursor
     member directly. The corrected controller uses its protected retained
     `mouseCursor()` accessor, preserving the intended inheritance boundary;
     and
   - the sanitizer harness passes unbound, bind, position, clamp, mode-resize,
     invalid-bounds, and teardown cases. PORT-005 remains the sole owner of
     processed event injection and broader input compatibility.
7. Narrow official screen-facade patch — complete:
   - the sole modified official file is `vdp/video/agon_screen.h`, whose header
     names the pinned upstream source, accepted decisions, exact local patch
     boundary, retained behavior, and removal condition;
   - the patch preserves the official globals and entry-point names, complete
     mode table, `changeMode()`, Canvas construction and scaling, Teletext,
     waits, swaps, palette restoration, and return-code surface while replacing
     only the classic controller factory/downcasts, configuration, frame clock,
     and processed cursor-position binding;
   - `changeResolution()` commits the public color depth and constructs Canvas
     only after the transactional P4 facade reports success, leaving the
     official VDU-owned requested/old/default fallback sequence intact; and
   - a bounded diff audit found no edit to any other official VDP file. Target
     compile/link closure remains deliberately unclaimed until checklist item
     11; this item certifies the authorized source boundary only.

Returned EMOS review checkpoint:

- `mos-agondev` `dev/emos`, `origin/dev/emos`, `origin/main`, and
  `origin/dev/port-200` all resolve to completed qualification commit
  `a695599`; its authoritative TODO is clear;
- PORT-200 adds emulator/ABI qualification, a later physical gate, and
  prior-art evidence but no maintained EMOS source change after `a8dc891`;
- EMOS still names physical EDP discovery, transport, wiring, and timing as
  unresolved and labels `edu.probe` as fake qualification scaffolding, so none
  may be used as Phase E evidence; and
- its fixed VDU dispatcher and exclusive-mode route contract are compatible
  downstream consumers of this EDP-side official display lifecycle. They do
  not alter the Phase E source boundary, fixtures, gate, or stop conditions.

Repository migration note (2026-08-24): the commit identities above remain the
frozen inputs and evidence reviewed for this completed phase. Current EMOS
source, product support, tasks, and qualification authority is `agon-emos`
`main`, reconstructed at `b2a6d81`; current generic port authority is the
reconstructed `mos-agondev` `main` at `2cd4128`. The former branch names are no
longer operational dependencies.
8. Exact official VDU mode lifecycle — complete:
   - `run-official-mode-lifecycle.py` verifies the immutable `v2.16.0` commit
     and recorded function/file hashes, extracts the exact
     `VDUStreamProcessor::vdu_mode()` and `sendModeInformation()` bodies into a
     temporary C++17 harness, and compiles them under ASan/UBSan without copying
     either function into production;
   - controlled collaborators expose clear/wait, Teletext disable, callback
     removal/invocation, requested/old/default attempts, full context reset,
     double-buffer swap/clear, cursor restoration/position reset, mouse-variable
     update, exact packet bytes, and final state in actor order;
   - all seven independent lifecycle cases pass, including invalid mode,
     allocation/service failure represented at the facade return seam,
     three-stage fallback, Teletext failure, and visible double-buffer cursor;
     the generated result is bound to the independent fixture hash; and
   - comparison against the exact packet function exposed one omitted oracle
     event: stock invokes `CALLBACK_SENDING_VDPP | PACKET_MODE` immediately
     before `send_packet()`. The independent generator and permanent tests now
     record that callback explicitly rather than hiding the correction in the
     harness. The result artifact SHA-256 is
     `d4daae5338d915b24a472e56e4220701dd2990870fe71ffef4a65c481e959ac7`.
9. Retained Teletext and Canvas integration — complete:
   - `run-teletext-integration.py` compiles the patched official screen facade,
     real retained `agon_ttxt` implementation/font data, ordinary retained
     Canvas/common controller, P4 controller/facade, and project display seams
     into a sanitizer-backed host executable; no classic display, text-driver,
     PS/2, Scene, audio, network, transport, or sink source is in the closure;
   - successful mode 7 configures the stable P4 controller and Canvas at
     640x480 in 16 colors, allocates the official four Teletext work areas,
     selects the retained font, clears the page, and sets official mode state;
     the independently proven VDU lifecycle clears Teletext before the same
     facade transitions to ordinary mode 8 at 320x240 in 64 colors;
   - a separate fresh process injects failure at the first official Teletext
     PSRAM request after successful P4/Canvas configuration and observes the
     retained `-1` result with Teletext inactive. Retained Teletext has no
     teardown API and owns four process-lifetime global buffers, so LSAN is
     explicitly unclaimed while ASan/UBSan remain active; and
   - the inherited `fabgl.h` aggregate had supplied global `RGB888` and
     `GlyphOptions` aliases while also importing every classic subsystem
     declaration. The facade now includes only `canvas.h` and names those two
     required aliases explicitly, making the intended source boundary real.
     The hash-bound result artifact SHA-256 is
     `c94c6c9a8fd2a7322ad28e0325fee22b6292077eca8332baea82084d024d7495`.
10. Complete host mode and regression matrix — complete:
    - one stable `ScreenFacadeAdapter` and `P4DisplayController` accepts all 58
      independent current, legacy, and buffered variants in sequence, with
      exact dimensions, native depth, cadence, buffering, full viewport, 58
      starts, 57 replacement stops, and zero live allocations at teardown;
    - the fixed sanitizer harness separately passes modeline/depth rejection,
      transactional initial/replacement configuration, injected allocation and
      frame-service failures with prior-mode recovery, frame-counter expressions
      and rollover, cursor bind/clamp/resize, and allocator teardown;
    - the exact VDU lifecycle, retained Teletext, all Phase E permanent tests,
      Phase B native renderer/allocation suite, Phase C 12-trace/controller/stress
      suite, and Phase D palette/compositor/controller suite all pass under the
      consolidated runner. Refreshed cross-phase evidence records the expected
      Phase E interface/header hashes rather than leaving stale evidence; and
    - `mode-facade-matrix-results.yaml` has SHA-256
      `f8f590bbaf6eed1bf6519e35ced2f8b5990b9a67479529faccba3ad99506e779`;
      the eight-gate aggregate `host-mode-results.yaml` has SHA-256
      `39c39bc9f9c38712abc49991e0a749de2f8b0acdd4f71d08c44ca26f160d9799`.
11. P4 official-display compile and link closure — complete:
    - the dedicated `p4-official-display` environment compiles the adapted
      header-defined official facade and Teletext implementation, 12 exact
      project translation units, and unchanged retained `canvas.cpp` and
      `displaycontroller.cpp`; the build succeeds for the pinned ESP32-P4
      target and produces a diagnostic-only 609,328-byte binary;
    - deterministic compile-command, linker-map, and ELF validation proves all
      14 selected units and eight required official/project seams are linked,
      with no missing or unexpected application objects or compile records;
    - classic VGA/CVBS/Scene/PS2, physical audio, network, storage, updater,
      broad `fabutils.cpp`, output-sink, and physical-transport source/symbol
      families remain absent. The final clean-build closure and exclusion
      records have SHA-256
      `8ddc9995ce10bb4ee4f4a7276d3943e560e94332f36995728aa8ac88d3f225a0`
      and `35fe007959aae88c2dac6182745972d43a112f7306bfa17b49ee82ccb10dee99`;
      and
    - the first post-link check incorrectly required an emitted symbol for the
      intentionally inline cursor wrapper. The linked concrete P4 cursor
      endpoint was present; the validator now checks that surviving method.
      The only compile diagnostics are inherited vdp-gl deprecated-ADC
      warnings. Nothing was assigned an artifact identity, deployed, or
      physically qualified.
12. Durable provenance, dependency, and compatibility records — complete:
    - the reviewed `agon-vdp@v2.16.0` managed import is now classified
      `vendored-patched`; `video/agon_screen.h` is its only declared differing
      path and names ADR-0015, the immutable/repository hashes, and the exact
      repository location. Regeneration rejects an undeclared difference, a
      missing patch, or a stale byte-identical patch declaration;
    - the canonical dependency graph now consumes the Phase E build closure
      and projects the official-display canary, cursor adapter, screen facade,
      P4 binding, retained controller/frame/presentation seams, official
      header-defined facade/Teletext, and unchanged Canvas/common units rather
      than presenting Phase D as the current integration boundary;
    - `phase-e/compatibility-delta.md` distinguishes the retained VDU-visible
      mode lifecycle from the unavoidable P4 physical-controller adaptation
      and from Phase F, PORT-008, EMOS, sink, and hardware deferrals; and
    - the completed implementation manifest binds production files,
      generators, evidence, target selection, source hashes, patch decision,
      returned EMOS context, exclusions, and deferrals. The dated development
      log records the same factual boundary without promoting compile evidence
      into a physical claim.
13. Deterministic final validation — complete:
    - after a clean `p4-official-display` rebuild, all 20 tracked Phase E,
      cross-phase, and canonical projection artifacts regenerated twice with
      byte-identical SHA-256 results. The independent dependency orchestrator
      also regenerated and validated its complete output pipeline twice
      byte-identically across all 5,164 managed source files;
    - the clean P4 build succeeds against pioarduino `55.03.311`, Arduino
      `3.3.11`, and ESP-IDF `5.5.5`; post-link validation again proves 14 exact
      application units, eight required symbols, and zero excluded families.
      The raw unidentified firmware hash changes across clean builds because
      ESP-IDF embeds build metadata, while its size, compile-command hash,
      linker-map hash, and normalized symbol hash remain stable. Reproducible
      release-image identity is not claimed by this diagnostic phase;
    - all 71 permanent dependency and PORT-003 Phase A–E Python tests pass,
      along with the eight-gate sanitizer-backed host matrix. The first full
      pass exposed stale Phase C/D tests that compared immutable provenance to
      the now-patched repository import; they now read official VDP bytes from
      the pinned source checkout while the managed-import validator separately
      proves and authorizes the repository difference; and
    - schemas and all 17 changed YAML/JSON files parse, exhaustive source and
      span verification passes, all changed local Markdown links resolve, all
      generated SVGs retain explicit white backgrounds, and the 62-file change
      set contains no machine-local paths or trailing whitespace. Project
      whitespace and `git diff --check` pass.
14. Gate E boundary audit — complete:
    - the staged boundary contains only the narrow official-facade patch,
      project-owned mode/frame/cursor adapters, diagnostic target selection,
      independent fixtures and evidence, cross-phase interface refreshes,
      managed patch provenance, canonical dependency projections, and the
      required task/development records;
    - each Gate E criterion is independently covered: all mode variants and
      metadata, requested/old/default fallback and injected failures, exact VDU
      lifecycle and packet order, retained Teletext, writable frame counter,
      display-only cursor endpoint, host sanitizers, and clean target closure;
    - no physical transport, input acquisition or routing, EMOS parity claim,
      consumer API, output sink, operating-mode policy, firmware identity,
      deployment, bench action, or hardware result entered the phase; and
    - Gate E passed at 2026-08-24 07:46 EDT under the Author's unattended
      authorization. The next boundary is Phase F planning; PORT-008 remains
      untouched as explicitly directed.

### Phase E gate criteria

1. Every official current, legacy, and supported double-buffered mode produces
   the documented dimensions, depth, cadence, scaling, rectangular-pixel flag,
   buffering state, and mode identity through the adapted official facade.
2. Injected requested-mode, old-mode, default-mode, allocation, and service
   failures follow the recorded official fallback contract and never leave the
   facade without a valid explicitly reported state.
3. The exact official `VDU 22` implementation produces the required context,
   callback, cursor, double-buffer, and eight-byte mode-packet event order
   against independent fixtures.
4. Teletext mode 7 initializes and exits through retained official code over
   ordinary Canvas, with no physical text controller or PS/2 dependency.
5. The official direct frame-counter seam and the P4 logical frame service
   share one writable wrapping value; the cursor seam owns display positioning
   only and does not absorb PORT-005 behavior.
6. Host sanitizers, cross-phase regressions, deterministic evidence, managed
   patch provenance, and clean pinned P4 compile/link closure all pass without
   deployment, transport, EMOS parity, output-sink, or hardware claims.

### Phase E explicit exclusions

- No edit to official VDU command semantics beyond the accepted concrete
  display binding; `vdu.h`, context code, callback code, and packet code remain
  byte-identical to `v2.16.0`.
- No physical PS/2 keyboard or mouse driver, processed event injection, input
  packet routing, control-key policy, or PORT-005 implementation.
- No network/browser, RGB, MIPI-DSI, HDMI, or other physical output consumer,
  and no Phase F consumer lease/API freeze.
- No MOS/EMOS parity claim, VDU/EDU routing, UART/parallel transport, General
  Poll, mode-policy selection, or PORT-008 work.
- No classic GPIO/I2S/DMA/VSYNC engine, target deployment, bench operation,
  artifact identity, or hardware qualification.

### Phase E stop conditions

Stop for Author review if the official display lifecycle cannot be retained
without broad edits outside `agon_screen.h`, if selected code requires a
classic physical controller or physical input driver, if an application-
visible command/packet must change, if the frame/sink contract must change, or
if PORT-005, PORT-008, SETUP-005, MOS/EMOS, or physical-output policy is needed
to make the gate pass. Also stop if independent fixtures expose a behavior
difference that cannot be narrowly isolated and recorded, or if target
compilation invalidates the accepted one-controller facade.

## Phase F — Browser video handoff and bootable port

The first-bench/first-fixture selections in this accepted phase record describe
the earlier bring-up sequence. PORT-008-D003 now owns the current r02 stage
order. Gate F's retained display/browser result remains available to later
stages; it does not force power, bias, or isolated UART checks to initialize
the parser or browser, or to repeat the former forward-only fixture.

### Accepted direction

1. Ethernet/browser presentation is the sole planned video-output path for the
   foreseeable future and is the primary product sink, not a diagnostic
   substitute for another display.
2. Reuse the look and feel of the most recent legacy presentation interface at
   `agon-extender-legacy@f33b9dd:web/presentation/`: its dark centered shell,
   pixel-sharp 4:3 canvas, compact connection controls, and frame-statistics
   grid are the visual reference.
3. Do not import stale legacy architecture by implication. Reconcile its
   physical-scanout terminology, frame protocol, WebGL presenter, buffering
   behavior, and server implementation with the current retained VDP port,
   logical framebuffer, and bounded latest-state consumer contract before
   selecting or reusing code.
4. Phase F must produce part of the actual retained VDP port. It may not use a
   throwaway renderer, invented VDU vocabulary, or disposable transport merely
   to obtain visible output.
5. EDP firmware on the P4 serves the browser assets and video endpoint directly
   over the DevKit's onboard Ethernet. A Pi or other external web server is not
   part of the product runtime. Bench hosts may deploy, observe, and qualify
   the firmware without becoming a required media relay.

The accepted direction, ownership split, first frame delivery, network
bootstrap, command fixture, actor path, and activation rules are recorded
below. The detailed checklist and proposed contracts still require one complete
Author review before coding.

### Accepted ownership boundary

1. PORT-006 owns P4 Ethernet initialization and link state, IP configuration,
   HTTP serving, browser connection lifecycle, and generic bounded network
   buffering and backpressure.
2. PORT-003 owns framebuffer snapshot and consumer handoff, browser-video frame
   semantics and encoding, HTML/CSS/JavaScript presentation assets, WebGL or
   Canvas presentation, and video-specific counters and diagnostics.
3. PORT-006 transports opaque bytes without interpreting pixels. PORT-003 does
   not initialize or control Ethernet hardware.
4. The first supporting PORT-006 tranche is limited to the browser-video
   foundation. OTA, optional Wi-Fi, management, and unrelated network services
   remain outside Phase F.

### Accepted initial frame-delivery contract

1. Deliver full, uncompressed, presentation-ready RGB888 frames over a
   WebSocket for the first port. Screen dimensions and stride are runtime frame
   metadata rather than a hard-coded 320-by-240 assumption.
2. Derive the versioned frame header from the legacy `EVF1` contract, subject
   to exact validation against current types and byte-order requirements. Do
   not inherit the legacy server's fixed dimensions or one-frame-only behavior.
3. Use explicit browser demand and bounded latest-frame semantics. A browser
   that is slow, disconnected, or not requesting another frame cannot queue
   unbounded surfaces, retain mutable logical storage, or delay VDP execution
   and logical frame progression.
4. The P4 composes final presentation pixels. Browser code must not reimplement
   logical palette expansion, Copper effects, sprites, cursor composition, or
   other VDP semantics.
5. Pixel-exact full frames and deliberately bounded cadence are sufficient for
   the first visible forward-command test. Compression, dirty rectangles,
   codecs, and production-rate optimization follow measured evidence and are
   not Phase F prerequisites.

### Accepted first-bench network bootstrap

1. EDP/P4 firmware uses ordinary DHCP over the DevKit's onboard Ethernet.
2. The bench router's existing reservation for the DevKit MAC is expected to
   return the stable bench address; firmware does not hard-code that address.
3. EDP/P4 firmware reports link and acquired-lease information through its USB
   serial diagnostics so reservation or network failures remain observable.
4. Friendly-name discovery, persistent user network settings, and multi-device
   naming are deferred beyond the first forward test.

### Accepted first visible-command fixture

1. Use only official retained VDP commands and ordinary printable bytes.
2. Select a conventional bitmap mode, clear the screen, set text color, print
   a recognizable banner, reposition the text cursor, and print a second
   string.
3. Set graphics color, draw several lines and a filled rectangle, then change
   and visibly use one palette entry.
4. Derive exact command bytes from official documentation and freeze both
   expected pixels and a human-recognizable expected image before bench use.
5. Treat this as a representative first fixture, not a claim that unexercised
   retained VDP commands are qualified.

### Accepted first-fixture actor path

1. An ordinary eZ80 test application emits the fixture through the standard
   MOS/VDU call surface.
2. A fixed-purpose EMOS development build owns the routing decision and sends
   the unchanged official byte stream over the parallel wiring.
3. The eZ80 application does not manipulate transport GPIO or depend on a new
   application-visible protocol.
4. EDP/P4 firmware admits the bytes into the retained VDP parser, updates the
   logical framebuffer, and makes the presentation surface available to the
   P4-owned browser endpoint.
5. This fixed routing proves a vertical slice; it does not implement or qualify
   the eventual runtime operating-mode transition machinery.

### Accepted first-run activation

1. Agon and EMOS boot normally in Legacy mode; no test build may force the
   parallel route during startup.
2. EDP/P4 boots independently, acquires its DHCP lease, and serves the browser
   endpoint. The operator confirms that readiness before requesting a route.
3. The operator explicitly requests Exclusive Extended through the existing
   EMOS mode-command framework.
4. A qualification-only EMOS forward adapter prepares the eZ80 GPIO and
   transport route and commits it only under this controlled operator action.
5. Reverse UART remains disabled, so this adapter cannot prove the eventual
   EDP handshake or qualify the complete runtime transition. Its diagnostics
   and evidence must describe that limitation explicitly.

### Detailed Phase F execution checklist

This checklist is the accepted scope fence. After every completed item, reread
`TODO.md`, this Phase F section, the Phase F contracts, and the active item
before proceeding.

1. [x] Freeze the accepted scope, exact authorities, legacy evidence commit,
   ownership boundaries, exclusions, proposed contracts, fixture rules,
   implementation order, and stop conditions. Create the task-local Phase F
   package and do not edit product code during this item.
2. [x] Generate a bounded source/provenance inventory for the official parser
   and sketch lifecycle, current P4 display/frame APIs, legacy browser assets
   and `EVF1` protocol, pinned ESP-IDF Ethernet/HTTP facilities, and the current
   EMOS mode/adapter seams. Fingerprint exact inputs; do not perform another
   whole-firmware survey.
3. [x] Define the bootable retained-port closure. Preserve the official
   `VDUStreamProcessor`, VDU handlers, contexts, buffers, screen facade,
   Teletext, and Arduino/FreeRTOS lifecycle while replacing only already
   accepted P4-inapplicable bindings. Keep audio, physical input, updater,
   terminal/ZDI hardware, and return packets explicit rather than allowing
   missing symbols to choose behavior accidentally.
4. [x] Freeze and independently model a fixed-capacity immutable presentation
   snapshot pool. The proposed first contract uses three PSRAM-backed slots
   sized for the largest retained 1024-by-768 RGB888 surface: at most one
   producer slot, one latest published slot, and one leased network slot. The
   producer never waits for a slot; pressure records a dropped presentation.
   No consumer receives a mutable logical-plane pointer.
5. [x] Freeze the `EVF1` wire contract and browser credit state machine before
   implementation. Validate every field and arithmetic bound, support all
   retained dimensions and packed RGB888 stride, allow one outstanding browser
   frame request, send only an immutable complete snapshot, and release its
   lease after the network send completes or the client disconnects.
6. [x] Freeze the narrow PORT-006 service contract: DHCP with observed lease,
   onboard Ethernet link lifecycle, embedded static assets, HTTP routes, one
   first-tranche video WebSocket client, opaque bounded sends, disconnect
   cleanup, and USB serial diagnostics. No Pi relay, Wi-Fi, OTA, management,
   authentication claim, internet exposure, or unrelated service enters this
   bench tranche.
7. [x] Build independent fixtures before production code: snapshot-pool state
   traces, mode/reconfigure/failure cases through 1024-by-768, exact `EVF1`
   byte vectors, malformed-frame rejection, browser credit/reconnect traces,
   deterministic presentation hashes, and the accepted visible VDU-command
   fixture. Expected values come from written contracts, official docs/source,
   or separately reviewed legacy bytes—not the implementation under test.
8. [x] Implement the project-owned immutable snapshot publisher and lease API.
   Composition occurs only at a controller-owned quiescent frame boundary and
   never calls network code. Limit first-bench snapshot production to a
   documented conservative cadence; logical frame time continues independently
   when no slot or browser is available.
9. [x] Adapt the legacy browser presentation into current project-owned assets.
   Preserve its accepted visual language, strict frame parser, pixelated 4:3
   presentation, local browser test pattern, connection state, and statistics.
   Replace stale physical-scanout wording, fixed dimensions, and one-frame
   behavior; issue the next credit only after the prior frame is accepted for
   browser presentation.
10. [x] Implement the narrow PORT-006 wired service and bind its opaque send
    interface to PORT-003's leased snapshots. Keep Ethernet/HTTP code under the
    network owner and pixel/frame semantics under the display owner. A slow or
    failed send may consume its one lease and cause later presentation drops,
    but it cannot block the frame service or VDU command path.
11. [x] Assemble a bootable P4 target from the retained official VDP lifecycle,
    completed P4 display facade, snapshot publisher, browser sink, and a
    disconnected project transport ingress implementing the required Arduino
    `Stream` contract. PORT-008 later supplies the parallel ingress. Preserve
    upstream startup and General Poll behavior; do not invent startup bytes or
    mark a missing return transport as qualified.
12. [x] Run deterministic host tests under sanitizers plus browser-side parser
    and state-machine tests. Exercise null, fast, slow, disconnecting, and
    reconnecting consumers; slot exhaustion; mode changes; allocation failure;
    malformed frames; sequence rollover; repeated start/stop; and sustained
    bounded operation. Re-run all Phase A--E and dependency regressions.
13. [x] Add and validate the exact P4 build closure. Prove the retained parser,
    official facade, P4 controller/frame/snapshot code, browser assets, and
    narrow wired service are linked, while classic VGA/CVBS, PS/2 acquisition,
    physical audio, updater, Wi-Fi, storage, and the parallel/return transports
    remain absent until their owning tasks select them.
14. [x] Regenerate provenance, dependency, source-selection, compatibility,
    and qualification artifacts twice byte-identically. Audit all changed
    source, generated evidence, links, schemas, paths, comments, and exclusions.
    Present the committed-artifact identities and exact P4-only deployment
    procedure for separate Author approval.
15. [x] Only after that approval, deploy the identified P4-only build and prove
    DHCP, direct asset serving, browser self-test, startup framebuffer delivery,
    disconnect/reconnect, bounded drops, memory bounds, and serial diagnostics.
    This does not connect the Agon or claim VDU transport.
16. [x] Stop for Author review of Gate F. If accepted, hand the same bootable
    firmware target to PORT-008, which adds the parallel `Stream` ingress and
    runs the explicit-EMOS official-command fixture. Do not begin return UART,
    production electrical tuning, or broad compatibility qualification.

### Phase F execution record

1. Item 2 generated a bounded inventory at
   `docs/tasks/PORT-003/phase-f/evidence/source-provenance.yaml` with a matching
   Markdown review rendering. It fingerprints the exact retained VDP, P4
   display, legacy browser, ESP-IDF/Arduino networking, official-documentation,
   build-boundary, and EMOS seam inputs without recording machine-local paths.
   Final item-14 regeneration contains 103 records and matched both tracked
   outputs byte-for-byte. The inventory
   confirms that immutable presentation leases are new PORT-003 work, while the
   physical EMOS forward adapter remains PORT-008 work.
2. Item 3 froze `phase-f/boot-closure.yaml` and its deterministic Markdown
   rendering. The closure retains the official parser, setup/loop shape,
   process task, General Poll startup gate, screen/context/buffer state,
   Teletext, RTC surface, and official boot banner. It names each unavoidable
   P4 binding explicitly: disconnected `Stream`, USB diagnostics, no-device
   processed-input seam, deferred PORT-004 audio binding, accepted maintenance
   exclusions, and post-boot PORT-006 startup. Missing physical subsystems are
   nonclaims rather than linker-selected behavior. The renderer validates
   tuple-unique IDs and the presence of every retained or vendored input and
   reproduced its output byte-identically.
3. Item 4 froze `phase-f/fixtures/snapshot-pool-model.yaml`: three fixed
   2,359,296-byte PSRAM slots, 7,077,888 pixel bytes total, tightly packed
   RGB888, 64-bit internal generations, explicit free/producer/latest/leased
   transitions, reconnect-safe release behavior, and a 200,000-microsecond
   first-bench production interval. The independent Python oracle imports no
   production code; its four named scenarios and depth-12 exploration of 71
   normalized states and 217 valid transitions pass byte-deterministically.
4. Item 5 froze `phase-f/fixtures/evf1-contract.yaml`. EVF1 v1 is an exact
   32-byte little-endian header plus a bounded complete RGB888 payload; current
   producers emit packed stride, both known flags, and the low 32 bits of the
   snapshot generation. The exact text `frame` grants one credit. Server and
   browser transition tables prohibit a second outstanding credit, hold only
   one immutable lease/frame, release on send failure or disconnect, and issue
   the next credit only after browser animation presentation. The independent
   checker covers every header byte and passes four lifecycle scenarios without
   importing production C++ or JavaScript.
5. Item 6 froze `phase-f/network-service-contract.yaml`. Arduino-ESP32 3.3.11
   owns explicit IP101/RMII initialization and DHCP events; ESP-IDF 5.5.5 owns
   HTTP/WebSocket tasks and socket writes. The contract records all ten onboard
   Ethernet GPIO roles, a six-route embedded-asset surface, idempotent
   link/lease/server transitions, USB diagnostics, private-LAN-only exposure,
   and a two-segment 2,359,328-byte maximum opaque lease. PORT-006 holds one
   credit, one lease, and one queued send without parsing EVF1 or calling
   PORT-003 under network locks. Its deterministic checker passes all unique
   pin, transition, route, size, and exposure constraints.
6. Item 7 generated `phase-f/fixtures/independent-fixtures.yaml` and the
   human-reviewable `visible-vdu-command-expected.svg` without importing
   production C++ or browser JavaScript. Seven exact authority fingerprints
   support 53 documented mode profiles through 1024 by 768, four all-or-nothing
   allocation outcomes, three no-reallocation mode changes, four valid EVF1
   vectors, 18 malformed-frame rejections, and six browser credit/reconnect
   traces. The accepted 106-byte official VDU stream selects mode 9, disables
   the cursor, draws two colored text strings, three axial lines, two filled
   rectangles, and visibly remaps one palette entry. Its independently rendered
   230,400-byte RGB888 expectation hashes to
   `d368967667b3eee2315e2bb86129e7f423d904abd203c93dd0810906d08783d8`.
   Independent regeneration was byte-identical, and the separate consistency
   checker passes every vector and fixture family.
7. Item 8 added `presentation_snapshot_pool.hpp/.cpp` and bound it to the end
   of `P4DisplayController::executeFrameWork()`, after retained primitive and
   sprite work but before the controller releases its frame-boundary ownership.
   Three PSRAM-only maximum-size slots are allocated all-or-nothing on P4; an
   allocation failure leaves the display controller available and publication
   disabled. The frame-task producer tries the short transition guard once,
   composes into one private mutable slot, and publishes an immutable complete
   generation or defers one bounded transition without waiting. The network
   side receives a move-only immutable lease and never holds the transition
   guard while using bytes. A retained latest generation survives disconnect
   and may be acquired by a new connection.

   Standalone and controller-integrated sanitizer checks pass allocation
   failure at slots one through three, cancellation, cadence, held-lease/new-
   latest behavior, reconnect, 1024-by-768 mode change, packed metadata, and
   palette-expanded bytes. Existing controller presentation checks also pass.
   A compile-only `p4-official-display` attempt stopped before compiling source:
   PlatformIO rebuilt its private Python environment after a 3.12/3.14 mismatch
   and then reported a missing Arduino framework directory. This is recorded as
   a local build-tool regression for the item 13 build gate; no firmware change
   was made around it.
8. Item 9 added the project-owned browser assets under
   `vdp/video/extender/web/`. They preserve the accepted legacy dark shell,
   pixelated 4:3 canvas, compact controls, statistics, WebGL2 upload path, and
   local test-pattern facility while replacing physical-scanout terminology,
   fixed dimensions, permissive parsing, and one-frame-only flow. The browser
   validates every frozen EVF1 field and bound, holds one pending complete
   frame, and emits the next exact `frame` credit only after its animation loop
   invokes the presenter. Mode changes recreate the immutable WebGL texture;
   padded rows use one reusable staging buffer.

   A framework-free browser-native test imports the production parser, credit
   state, and WebGL presenter. Firefox headless passed 25 checks covering the
   independent compact vector, demo formula, representative malformed input,
   initial/presentation/reconnect credit, duplicate-frame rejection, and actual
   WebGL pixel readback. The local test pattern also traversed parser and
   presenter and reported a 320-by-240 surface, one received frame, and one
   presented frame. Node.js is absent from this host; the broader item 12
   browser runner must remain browser-native or explicitly provision its own
   declared runtime.
9. Item 10 implemented the narrow PORT-006 service in
   `video/extender/network/` and the sole EVF1/snapshot bridge in
   `video/extender/web/browser_video_provider.hpp/.cpp`. The network owner uses
   explicit IP101/RMII startup, ordinary DHCP, coalesced link/lease events, a
   dedicated worker, direct ESP-IDF HTTP/WebSocket service, six embedded
   routes, one post-handshake client, one exact credit, one opaque two-segment
   lease, and one queued HTTP-task send. Provider acquisition, send, and
   release happen outside short network state locks; Ethernet callbacks only
   record events and wake the worker. Disconnect and failed sends release the
   immutable snapshot without blocking the frame producer.

   The bridge validates packed RGB888 snapshot metadata and constructs the
   exact EVF1 header while holding one move-only immutable snapshot lease.
   Sanitized host tests pass all bounded credit, generation, completion,
   failure, disconnect, reconnect, and payload cases. The
   `p4-network-service` diagnostic compiles and links at the pinned 360 MHz P4
   profile with Arduino-ESP32 3.3.11 and ESP-IDF 5.5.5; its ELF contains the
   network/provider symbols and all five embedded browser assets. It publishes
   no frame and makes no boot, DHCP, or hardware claim.

   The target build found and documented two environment/build-boundary
   problems rather than hiding them in firmware. A stale Arduino 2.0.14 package
   left by PlatformIO's Python-environment rebuild was replaced through the
   pinned package install. PlatformIO's generic text-embedding hook generated
   assembly but omitted its objects from this hybrid application's final link,
   so the source-selection manifest now owns `embedded_text_files` and the
   generator emits ESP-IDF-native application-component `EMBED_TXTFILES`.
10. Item 11 assembled `p4-browser-vdp`, the first bootable retained-VDP P4
    target. A deliberately exceptional Arduino/ESP-IDF bridge compiles the
    retained `video.ino` setup, loop, process task, parser, contexts, buffers,
    Teletext, RTC surface, boot banner, and General Poll gate without copying
    their ownership into a second lifecycle. The target binds the P4 display,
    immutable snapshot publisher, browser-video provider, and wired service
    after the retained boot screen.

    Every unavailable binding is explicit. A disconnected Arduino `Stream`
    preserves parser construction while supplying no VDU bytes or qualified
    return path; no-device input, deferred audio, and unavailable-maintenance
    adapters close only the already accepted Phase F exclusions. A narrow
    vdp-gl compatibility include retains Canvas, codepage, font, and common
    display facilities without pulling classic Terminal, PS/2, or sound
    hardware into the P4 image. USB Serial/JTAG diagnostics replace the
    inapplicable stock UART0 debug-pin binding. The unchanged General Poll wait
    remains blocked until PORT-008 supplies real ingress.

    The pinned `p4-browser-vdp` environment compiled and linked successfully at
    360 MHz and produced an ESP32-P4 application image plus a combined factory
    image. PlatformIO reported 46,084 of 512,000 bytes RAM, 1,217,592 of
    7,340,032 bytes application flash, and a 1,218,439-byte total image before
    binary padding. This is predeployment build evidence only: item 13 still
    owns exact linked-symbol/exclusion proof, and no boot, Ethernet, browser,
    transport, or hardware claim has yet been made.
11. Item 12 added one reproducible nonphysical regression orchestrator and
    passed all 16 of its gates. ASan/UBSan harnesses exercised allocation
    failure, bounds, cancellation, mode changes through 1024 by 768, null and
    disconnected consumers, a held slow lease, slot pressure, 4,096 sustained
    snapshot publications, immutable held bytes, latest-state collapse, and
    exact three-allocation teardown. The network/provider harness exercised
    exact EVF1 bytes, fast sends, failed sends, disconnect during send,
    reconnect, duplicate credit, 256 repeated client start/stop cycles, 2,048
    fast frame transactions, and 1,023 publications behind one held send.

    A real Firefox 154.0.1 run imported the production parser, credit state,
    and WebGL presenter and passed 78 checks. It consumed all four independent
    valid vectors and all 18 malformed vectors, including sequence
    `0xffffffff` followed by zero, maximum retained dimensions, WebGL pixel
    readback, presentation-gated credit, duplicate-frame rejection, and
    reconnect. Four independent Phase F contract/fixture oracles, the eight-
    gate Phase A--E host matrix, 13 dependency-tool tests, and all 58 permanent
    Phase A--E tests also passed.

    The complete orchestrator, browser evidence, and refreshed Phase E host
    evidence reproduced byte-for-byte on a second run. A hermetic localhost
    fixture additionally proves that the hardware qualification client checks
    exact embedded assets, reassembles fragmented EVF1, detects a no-credit
    quiet interval, and reconnects without recording its endpoint. Temporary
    compiler paths are normalized out of tracked evidence, and the coverage map names
    which gate proves each item-12 stress family. These remain host claims;
    target closure and runtime behavior belong to items 13 and 15.
12. Item 13 added a fail-closed post-link closure validator and passed it twice
    byte-identically. The final map proves all 23 selected application units,
    all five embedded browser objects, the retained Arduino lifecycle and VDU
    parser, General Poll, complete mode switch, Teletext, P4 facade/controller/
    frame/snapshot owners, EVF1 provider, wired service, and deliberately
    disconnected ingress. Every project-owned hybrid-CMake compile record ends
    in `-std=gnu++17`; the generated component pins that effective standard;
    and the ELF identifies Arduino 3.3.11 and ESP-IDF 5.5.5.

    The paired exclusion artifact proves no selected or linked classic
    VGA/CVBS, Scene, PS/2, physical audio, Terminal/FileBrowser, updater,
    storage API, parallel ingress, or return-UART implementation. Arduino's
    Ethernet dependency causes its archive build to compile broad framework
    code and leaves only the known global Wi-Fi constructor/destructor residue
    in the final image; no selected project source references Wi-Fi and no
    operational Wi-Fi API is linked. Framework archive breadth is therefore
    recorded separately from the exact Extender application closure.

    Exact-package qualification uncovered two build-tool hazards. PlatformIO's
    global package store alternated this P4 target's Arduino 3.3.11 archive
    with another checkout's Arduino 2.x package, so the tracked project now
    isolates tool packages under ignored `vdp/.pio/packages`. Also, running
    PlatformIO's `compiledb` target cleared the linker map while retaining a
    stale ELF/bin; the validator rejected that incoherent state. Closure proof
    therefore follows one complete build and never an intervening `compiledb`
    invocation. The final predeployment rebuild uses 46,500 bytes RAM and
    1,222,912 bytes application flash. Its application image is 1,223,776
    bytes with SHA-256
    `4b066beb87a8b0c0b8c5ff242f29fcdb5b18b10c014a550dc3a75332cb809b3e`;
    this remains predeployment evidence and not yet an approved identity.
13. Item 14 regenerated every Phase F fixture, model result, browser result,
    host result, build closure, source-provenance record, global dependency
    graph, source-selection view, and implementation manifest twice
    byte-identically. The final nonphysical gate passes 16 host suites, the
    linked target proves 23 selected units, five embedded assets, 15 required
    symbols and all declared exclusions, and the dependency system reproduces
    12,115 nodes, 11,875 edges, 10,375 selection records, and 5,164 manifest
    files.

    The fail-closed predeployment audit parses every changed YAML and JSON
    document, resolves local links, compiles changed Python, checks the shell
    wrapper, rejects machine-private values, verifies 23 manifest fingerprints
    and 69 current-project provenance fingerprints, reconciles source selection
    to the linked closure, and compares all 15 declared upstream-shaped patches
    with official VDP v2.16.0. It records 122 candidate files and passes
    `git diff --check`. Source review found no new VDU byte or command
    reinterpretation; the only new external protocol is the accepted EVF1
    browser-output contract.

    The reviewed image deliberately contains `UNVERSIONED-DO-NOT-DEPLOY` and
    proves no deployable identity. On 2026-08-27 the Author approved firmware
    `extender-vdp-v0.1.0` (`candidate`, `olimex-p4-devkit`), procedure
    `p4-browser-video-qualification-r01`, and artifact-registry revision
    `r12`. These controls are frozen and committed before a new exact UTC build
    identity is generated from the clean commit. The reviewed unversioned image
    is never flashed. Item 15 remains separately authorization-gated and keeps
    the Agon physically disconnected.
14. The Author approved exact candidate commit
    `39b45df18622d872eb729644a56b2f92297da6cf`, build
    `extender-vdp-v0.1.0-b2026-08-28-01-57-52Z`, and Phase F item 15. Run
    `PORT-003-2026-08-28-14-46-06Z` used the required disconnected-Agon state,
    inactive reset breakout, passive analyzer load, and verified GPIO32 green
    probe. Read-only preflight identified ESP32-P4 revision 1.3 and 16 MiB
    flash. Remote staging matched the approved factory-image hash; erase,
    write verification, and independent flash verification all passed.

    The first passive runtime capture then failed the procedure's clean-runtime
    requirement. It contained 7,780 exact
    `esp_task_wdt_reset(707): task not found` errors in 7,784 lines, at roughly
    one error per millisecond. Required runtime checks 2 through 10 were not
    attempted because the flood could distort timing, network, reconnect, and
    memory evidence. The failed run, complete remote-log hashes, compact
    tracked evidence, and a bounded source diagnosis are preserved under
    `tests/runs/PORT-003-2026-08-28-14-46-06Z/`.

    Linked-code inspection proves that the retained parser task does not call
    `esp_task_wdt_reset()`: `VDP_USE_WDT` is absent. The caller producing the
    flood is ESP-IDF 5.5.5's still-registered per-core IDLE hook. Official VDP
    v2.16.0's retained startup calls `disableCore0WDT()` and
    `disableCore1WDT()`; Arduino-ESP32 3.3.11 implements those APIs by removing
    the IDLE tasks from the watchdog without deregistering ESP-IDF's IDLE
    hooks. Each hook subsequently feeds from an unregistered task. ESP-IDF's
    own reconfiguration path removes both subscription and hook.

    This is a P4 framework-binding incompatibility in retained startup intent,
    not an EVF1, browser, network-service, or new VDP-wire-contract defect. No
    correction was made. A reviewed P4-only binding correction, new immutable
    candidate commit and build identity, and a new item-15 run are required
    before Gate F can be reviewed.

### Item-15 corrective decision and implementation

| ID | State | Decision requested |
|---|---|---|
| `PORT-003-D010` | Accepted | Preserve the retained no-watchdog startup intent on P4 through ESP-IDF's supported task-watchdog reconfiguration path. |

Accepted implementation direction for `PORT-003-D010`:

1. The P4 boot adapter, running in the Arduino `loopTask` during `setup()`,
   calls `esp_task_wdt_reconfigure()` once with the pinned five-second timeout,
   current non-panic policy, and an empty IDLE-core mask. ESP-IDF then removes
   both IDLE-task subscriptions and both IDLE hooks atomically through its own
   supported path while leaving the task-watchdog service available for a
   future explicit subscriber.
2. A narrow `AGON_EXTENDER_P4_BOOT` branch in retained `video.ino` selects that
   adapter and preserves the two existing 200-millisecond startup delays. The
   stock build continues calling `disableCore0WDT()` and
   `disableCore1WDT()` exactly as official VDP v2.16.0 does. The exceptional
   branch receives an inline provenance comment and enters the upstream-patch
   manifest.
3. Any unexpected reconfiguration result is a P4 startup failure reported by
   USB Serial/JTAG diagnostics; the P4 firmware must not continue into a known
   error-flooding state.
4. Deterministic checks prove the stock branch is unchanged, the P4 link calls
   `esp_task_wdt_reconfigure()`, neither Arduino `disableCore*WDT()` function is
   called from the linked P4 `setup()`, and no VDU, EVF1, network, transport,
   or framebuffer contract changes.
5. Mark failed `extender-vdp-v0.1.0` rejected, advance the artifact registry
   to `r13`, assign corrected patch identity
   `extender-vdp-v0.1.1` as a candidate, implement and commit the correction,
   generate a new exact build ID, and repeat
   `p4-browser-video-qualification-r01` from the beginning under a new run ID.

Rejected alternatives:

1. Calling `esp_task_wdt_deinit()` would also remove the hooks but unnecessarily
   removes the complete watchdog service, making later explicit task
   subscription require reinitialization.
2. Disabling task-watchdog initialization in `sdkconfig.defaults` changes the
   whole target's startup policy and makes retained or future calls fail because
   no service exists.
3. Directly calling `esp_task_wdt_delete()` or suppressing the error log repeats
   the failed Arduino binding or hides its symptom without removing the stale
   hooks.
4. Patching the pinned Arduino or ESP-IDF package creates a project-local
   framework fork for a correction that can remain at the existing P4 port
   seam.

The Author accepted `PORT-003-D010` and authorized continued implementation on
2026-08-28.

The correction adds one P4-owned adapter at
`video/extender/port/p4_task_watchdog.hpp/.cpp` and one narrow conditional in
the retained `video.ino`. The adapter reconfigures the initialized ESP-IDF task
watchdog with its pinned five-second timeout, current non-panic policy, and no
IDLE-core subscriptions. Failure is reported and returns from P4 setup; the
non-P4 branch remains byte-for-byte equivalent to the two official Arduino
calls and delays.

The corrected unversioned P4 build passes 17 host gates and proves 24 selected
translation units, five embedded assets, 16 required symbols, C++17, and every
declared exclusion. The bounded provenance now contains 109 records, including
the exact Arduino helper and ESP-IDF reconfiguration implementation. Phase F
and global dependency regeneration were byte-identical on repeat. Artifact
registry `r13` rejects v0.1.0 and selects approved v0.1.1 as the candidate.
These remain predeployment findings until the correction is committed, rebuilt
with an exact build ID, and rerun under item 15.

Run `PORT-003-2026-08-28-15-28-59Z` exercised corrected candidate commit
`43cffd181058fa264cb9f9f78bc36eee17773746` as identified build
`extender-vdp-v0.1.1-b2026-08-28-15-26-31Z`. Stable-device preflight, exact
remote staging, flash erase/write verification, and independent flash
verification passed with the Agon and reset breakout disconnected.

The application-startup capture proves ESP32-P4 revision 1.3, QIO, 360 MHz CPU,
32 MiB PSRAM, the exact identity, the corrected hook-aware watchdog binding,
retained VDP setup, DHCP, and direct HTTP readiness. No watchdog flood, panic,
assertion, Guru Meditation, or reset loop occurred. All five served assets,
EVF1 delivery, no-credit quiet behavior, reconnect, Firefox/WebGL2 demo, and
the P4-composed retained startup banner passed.

One warm-up and five additional reconnect cycles produced 10 complete
snapshot and 11 complete network/provider/heap intervals. Seven observed
connections all disconnected, counters remained monotonic, all allocation,
composition, protocol, send, queue, and socket failure counts remained zero,
free 8-bit heap ended 232 bytes above its post-warm-up baseline, and free PSRAM
was unchanged. Continued frame and asset service passed. Raw bench-sensitive
evidence and screenshots are preserved under hashes in the tracked run
manifest. Item 15 passes within its explicit P4-only claim boundary.

The Author accepted Gate F on 2026-08-28, completing Phase F. The exact
qualified P4-only target is handed to PORT-008 as its retained parser, display,
frame-service, and browser-output starting point. PORT-008 remains not started;
the handoff does not authorize transport implementation or enlarge this run's
claim boundary. PORT-003 remains open for Phase G after PORT-008 Gate 2 and the
applicable QUAL-002 assembled-system qualification pass.

### Phase F gate

Gate F passes only when the retained VDP target boots on P4, the P4 directly
serves the accepted browser interface, immutable RGB888 snapshots cover every
retained mode size, and null/slow/disconnected network behavior cannot change
official logical frame progress, command responsiveness, queue completion, or
bounded memory. Gate F alone makes no Agon transport, return-packet, mode-
transition, production-throughput, internet-security, or electrical claim.

### Phase F stop conditions

Stop for Author review if implementation requires changing official VDU bytes
or semantics, patching retained lifecycle merely for robustness, handing a
mutable logical buffer to network code, waiting for a slow consumer on the VDU
or frame-service path, retaining a classic physical driver, expanding the
narrow PORT-006 tranche, inventing a transport command, exceeding bounded
memory, or weakening Legacy-at-boot and explicit EMOS activation rules.

## REMED-002 findings and current dispositions

The Author accepted the initial dispositions in
[REMED-002](REMED-002.md). The audit record
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md)
owns the evidence and provenance for these stable findings. The initial D001
register was later narrowed for upstream-origin findings by REMED-002-D004 and
PORT-003-D012. PORT-003 owns the following current actions and records; this
intake authorizes neither source changes nor Gate G.

1. [x] **F001 disposition:** Preserve the upstream/local source analysis.
   Correction and isolating regression design are deferred until deterministic
   evidence shows distinct Extender activation or obstruction of a selected
   Extender function.
2. [x] **F002 disposition:** Preserve the palette/Copper/buffer-mutation and
   P4-reader analysis. Correction and isolating regression design are deferred
   under the same D012 trigger threshold.
3. [ ] **F003 coverage split:** Add browser-frame regression coverage for the
   PORT-006 short-write remedy, including immutable snapshot ownership through
   complete send, congestion failure, disconnect, and retry. PORT-006 owns the
   ESP-IDF transport correction.
4. [ ] **F004 split:** Define and test a reachable parser binding in which
   every unsupported audio or updater command consumes or safely rejects its
   complete official grammar before top-level VDU parsing resumes. PORT-004
   owns retained audio semantics; PORT-008 and SETUP-005 own reachability and
   mode-policy integration.
5. [ ] **F007 durable owner:** Replace staging-time clean-HEAD inference with a
   cryptographic build-to-source binding that rejects objects or firmware
   produced from another commit. PORT-008 must consume this corrected staging
   authority rather than implement a divergent weaker copy.
6. [ ] **F011:** Make every Phase B, C, and D sanitizer runner fail on UBSan
   diagnostics, select an explicit non-recovering policy where appropriate,
   and include a negative fixture that would previously have exited zero.
7. [ ] **F017:** Define Phase G scope, fixtures, prerequisites, stop
   conditions, and acceptance criteria for Author review before any Gate G
   implementation or qualification begins.

These actions reopen no accepted Phase A--F claim by themselves. Evidence that
depends on a defective sanitizer or staging path must be explicitly retained,
rerun, superseded, or withdrawn before it supports later promotion.

## REMED-002 Work 2.a design gate

The design-only pass is recorded in
[`PORT-003/concurrency/README.md`](PORT-003/concurrency/README.md). It records
F001 and F002 source analysis through official VDP `v2.16.0`, pinned vdp-gl
`all-the-plots`, and the current P4 implementation, plus the F022 and H001
upstream observations. No production source, fixture identity, procedure,
firmware, qualification claim, or physical state changed in that pass.

The analysis remains useful, but its proposed D011 correction package is not
the current product direction. The Author rejected broad retained-renderer
hardening on 2026-09-01. ADR-0015's strict-compatible baseline and minimal-
upstream-delta rule remain authoritative, and ADR-0015 is again complete.

The retained observations are:

1. `PORT-003-W2A-H001`: retained `LightMemoryPool` allocation and frame-side
   release share unsynchronized metadata.
2. `PORT-003-W2A-H002`, promoted to `INTEGRITY-AUDIT-F022`: retained primitives
   queue raw bitmap/tile/copy-destination pointers and oversized official
   Context paths, while official code can later invalidate or reuse the owner.
   Generic direct glyph, glyph-buffer, and Canvas path APIs retain their
   upstream caller-lifetime obligation.

These observations are recorded, not selected for correction. They do not
block the current work to establish EMOS-to-EDP forward transport over the
parallel GPIO interface. A later task pass may design isolating regression
tests, but no such fixture work is active now.

### Work 2.a decision register

| ID | State | Decision |
|---|---|---|
| `PORT-003-D011` | Rejected by the Author, 2026-09-01 | Do not adopt the proposed comprehensive frame-state/lifetime hardening package; it changes too much retained behavior without evidence that selected Extender functionality manifests the upstream failures differently from regular VDP operation. Preserve the design as research only. |
| `PORT-003-D012` | Accepted by the Author, 2026-09-01 | Record upstream defects, but make a local correction only after deterministic evidence shows that a project-owned Extender transport, scheduler, presentation reader, or other selected function reproducibly triggers the failure in a way regular official VDP operation does not, or that the defect blocks the selected Extender function. Prefer a project-owned boundary and require separate approval before editing retained common code. Current priority is the bounded forward-parallel transport, not general firmware hardening. |

D012 resolves ADR-0015's open completeness question. F001, F002, F022, and
H001 remain recorded follow-up observations. If a future isolating regression
meets D012's trigger threshold, PORT-003 must return with the smallest proposed
containment and exact upstream-delta impact before source changes.

## Unattended continuation after Rally — 2026-09-13

The Author now prioritizes measured video speed, then faithful command coverage,
after RALLY-22's machine-complete game candidate. The bounded execution/précis is
in [video-throughput/README.md](PORT-003/video-throughput/README.md). Existing
R1/R2/R3 evidence and the held QUAL-003 failure remain scoped historical records.
Experiments stay local; the live project's remote must not receive experimental
code before explicit Author review. Preserve concurrent keyboard/SD/remote work.

## Unimplemented-command consumption tranche

### Executive summary

The Author requests safe no-op treatment for unimplemented VDP functions:
P4 EDP must consume each complete command payload without allowing argument
bytes to become subsequent VDU commands. This is protocol compatibility work,
not implementation of audio synthesis, a new sink, or an upstream redesign.
This turn is planning-only, followed by hardware voice and stop. The earlier
PORT-004 deferral is lifted only for this framing/no-op tranche when execution
resumes; synthesis and output remain deferred.

1. [ ] UC01: Inventory every unimplemented function reachable through the
   selected P4 VDU parser, including audio, updater and other selected adapters.
   Reuse PORT-008 F004 reachability and PORT-004's existing audio grammar work.
   For each command/subcommand record selected official version, exact grammar,
   optional/variable lengths, terminators, command-dependent fields, required
   response packets and parser ownership. Do not assume fixed lengths or infer
   boundaries from whether a byte looks like another command.
2. [ ] UC02: Freeze the no-op contract before coding. Preserve the official
   parser wherever it compiles; replace only unavailable execution/backend
   effects with a bounded discard sink. Consume streaming payloads without
   allocating the full payload merely to discard it. Complete legitimate
   command framing before resuming top-level parsing. Preserve already
   implemented behavior; stubs must not disable functional commands.
3. [ ] UC03: Specify replies/status and malformed/truncated behavior per command.
   No rendering/audio side effect does not necessarily mean no reply: preserve
   required protocol replies through EMOS so applications do not hang, using
   documented unsupported/failure behavior rather than claiming successful
   playback. Record gaps for review. With an unframed byte stream, do not claim
   arbitrary truncation/unknown commands can be resynchronized by guessing or
   swallowing the next valid command. Match stock grammar/timeouts where
   applicable and explicitly disposition unsupported recovery cases.
4. [ ] UC04: Implement reviewed handlers with narrowly scoped commits. P4
   consumes/discards the payload; EMOS remains route/reply authority. No
   unsolicited audio forwarding to mainboard and no new sink architecture.
   Keep numeric-conversion fixes in separate candidates for attribution.
5. [ ] UC05: Deterministic parser tests: every command followed immediately by
   a known graphics/text/query sentinel; back-to-back commands, payload bytes
   that resemble VDU controls, optional fields, zero/boundary lengths and
   split transport chunks. Exercise malformed/truncated input under UC03's
   explicit contract. Verify exact consumed byte counts, sentinel recognition,
   required responses, bounded memory and absence of unavailable side effects.
   Compare parsing/reply obligations against pinned stock, not missing output.
6. [ ] UC06: Verify whether current Rally mute suppresses all initialization,
   gameplay and shutdown audio commands. Run the same identified binary with
   audio enabled and muted on ExCom, with matching Legacy controls. Then test
   the corrected stub using the enabled stream and deterministic sentinels.
   The Author's HUD/audio hypothesis is plausible; the empty audio handler is
   already documented in PORT-004, but causation for Rally HUD loss remains
   unproved. Preserve measurements and snapshots without calling browser FPS
   renderer FPS. Include the retained Wolf3D framing regression when applicable.
7. [ ] UC07: Hardware voice and review stop with exact candidates/results and
   a usable restored bench. Human Rally/Nurples validation remains required.
   Promote accepted grammar/stub obligations into existing compatibility and
   upstream-update checks so future imports cannot silently restore empty
   handlers. Do not mark full audio support complete or push experimental
   firmware before review.

PORT-004 retains audio-specific obligations; PORT-008 retains transport/reply
reachability. This task owns the executable parser binding and generic discard
behavior. TODO.md remains the single authoritative work index.


## Audio-first execution resumed

The Author authorizes the [audio framing execution contract](PORT-004/audio-framing/PLAN.md), implementation and hardware tests with spoken notification. Broader unimplemented-command inventory and audio synthesis remain separate.


Audio-first slice complete for review: [PORT-004 results](PORT-004/audio-framing/results/README.md).
144paired pixels and48audio replies pass per route; unmuted Rally capture shows
intact HUD/sky. This does not check off the full UC01 inventory, all unsupported
functions, full Wolf3D acceptance or synthesis. Hardware voice sent.
