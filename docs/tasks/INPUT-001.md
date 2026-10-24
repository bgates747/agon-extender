# INPUT-001 — Analog game controllers through Extender

Prepare a reusable Oryx-to-P4 controller bridge, an EMOS-owned application
interface, and a readable axis/button test appliance. Start with the attached
Logitech F310 in XInput mode. Preserve analog input and keep future direct P4
USB capture compatible with the same logical controller interface. The current
host reader, viewer and recording tranche has passed Author review. LAN
transport contract preparation is now released; P4/EMOS and transport
implementation remain behind their separate review gates.

## State and authority

1. **Status:** First host-only tranche implemented 2026-10-24; Author approves host
   viewer appearance and authorizes commit/push followed by LAN contract work.
   Guide and physical reconnect are verified; rest calibration remains
   optional/unreviewed. No network/target implementation is released.
2. The Author transferred the generic controller task from fsim on 2026-10-14.
   On 2026-10-24 the Author selected host capture before direct P4 USB work,
   requested sampling/wire design and an axis/button display program, and
   instructed Extender to write the task and pause.
3. After reviewing the task, the Author released the four-part host tranche:
   Linux capture/reconnect, large readable viewer, native/eight-bit observation,
   and timestamped recording. No LAN bridge, P4 receiver, EMOS API, firmware
   change or target appliance is authorized by this tranche.
4. The older task's HTTP path and 30 Hz fsim examples were proposals, not
   approved transport or sampling contracts. UDP and 100 Hz discussed in chat
   are likewise proposals. Do not silently select either.
5. The first consumer processor remains unresolved. Recommend an eZ80 state
   viewer as the first end-to-end consumer, since delivery to P4 alone does not
   demonstrate Agon input. A host viewer should precede target deployment.

## Confirmed controller and bounded research précis

| F310 mode | USB vendor/product | Linux name | Exposed analog inputs |
|---|---|---|---|
| DirectInput, initially observed | 046d:c216 | Logitech Logitech Dual Action | Four stick axes 0–255; no analog trigger axes |
| XInput, selected by Author and replugged | 046d:c21d | Logitech Gamepad F310 | Four stick axes −32768…32767; two separate triggers 0–255 |

1. XInput also exposes a two-axis digital hat (−1/0/+1) and eleven button
   codes: face buttons, shoulders, select/start/guide and two stick clicks.
   Triggers are axes rather than additional digital button codes in this mode.
   DirectInput exposes twelve button codes. These are enumerated capabilities,
   not a completed physical control-to-code mapping or measured sensor precision.
2. XInput stick centres observed about +128/−129, not exactly zero. Linux
   reports stick fuzz 16 and flat 128. These driver metadata do not establish
   ideal dead zones, centring accuracy, physical resolution or usable extremes.
3. Linux's advertised signed 16-bit range does not prove 16-bit hardware
   precision. Measure actual steps before promising precision or discarding
   information. User interest in efficient eight-bit eZ80 values is recorded;
   eight-bit quantization has not been selected as the mandatory wire/API format.
4. Logitech's [F310 guide](https://www.logitech.com/assets/47879/f310-gamepad-quick-start-guide.pdf)
   distinguishes analog triggers in XInput from digital triggers in DirectInput.
5. Existing fsim handling is documented in
   [RC-001](../../../agon-fsim/docs/tasks/RC-001.md) and
   [FLIGHT-041](../../../agon-fsim/docs/tasks/FLIGHT-041.md): SDL mapping,
   proportional surfaces, incremental throttle and configurable response.
   Reuse researched mechanisms; flight mappings/response remain consumer-owned.
6. Official [MOS module documentation](../../../../agon-docs/docs/mos/Modules.md)
   discusses joystick drivers as a future possibility, not a supplied analog
   API. Before coding an API, inspect current official MOS/VDP documentation
   first, then relevant source when necessary; record exact baseline commits
   and contracts. Coordinate existing shared interface-allocation policy before
   reserving any MOS call, getfunction entry, packet type or VDU command.
7. Current Extender [keyboard input](../remote-keyboard.md),
   [console routing](../protocols/excom-console.md) and
   [architecture](../architecture.md) supply admission/ownership constraints.
   They do not already transport analog controllers. No axis encoding through
   synthetic keycodes or direct register/transport bypass of EMOS is supported.

Stable device paths, host access, unique device identifiers and raw capability
receipts belong in ignored local evidence, not tracked deployment recipes.

## Ownership and proposed path

1. Oryx's Linux input stack reads the USB controller. An Extender-owned host
   bridge selects the device and maps physical events to logical controls.
2. The Oryx bridge sends versioned messages across the LAN to a P4 service.
   Extender owns admission, bounded queues, sequencing, receiver timestamps,
   connection health and coherent controller-state storage. Transport is open.
3. EMOS owns the P4-to-eZ80 transport and application-facing controller contract.
   Implementation belongs in agon-emos; assembled-product requirements and P4
   services belong here. Existing UART1 wiring is the candidate physical path;
   framing, delivery mode, scheduling and route compatibility require review.
4. The game/application polls or receives input through that EMOS contract.
   An application owns flight/game mappings, throttle/brake semantics, response
   curves and whether a lost controller pauses its simulation.
5. Fsim integration and changes to its accepted host controls remain fsim-owned.
   Extender supplies generic state viewers, not a replacement flight-control loop.
6. Future direct P4 USB capture should feed the same logical state owner. Direct
   USB enumeration/keyboard/hub repairs, rumble and game integration are outside
   the first implementation tranche. Do not claim USB compatibility now.

## Decision register — proposals pending Author review

Present unresolved architectural decisions one at a time when implementation
is released. Each accepted material decision requires the project ADR,
architecture, task and dated-log updates; this draft accepts none of them.

| ID | Recommendation | Alternatives, prerequisites and effects |
|---|---|---|
| IN001-D01 | First target viewer runs on eZ80 through EMOS; host viewer first | P4-only first is simpler but leaves Agon delivery/cost unproved; confirm first consumer before API work |
| IN001-D02 | Keep native values in capture; offer explicit eight-bit quantization at a documented boundary | Fixed native-width wire/API preserves data; fixed eight-bit saves bytes. Measure actual stick steps and consumer needs before choosing; reserve versioned layout/capabilities |
| IN001-D03 | Compare UDP state snapshots with persistent HTTP/binary delivery; prefer UDP if measured simplicity/latency justify it | UDP needs loss/reorder/session/edge handling; HTTP reuses services but may add serialization, acknowledgement and scheduling costs. Verify present P4 networking limits and firmware ownership first |
| IN001-D04 | Event-driven capture plus paced latest-state sends; evaluate 60/100/120 Hz | Choose cadence using latency, jitter, traffic and P4/eZ80 CPU measurements, not fsim frame rate alone; bound overload and heartbeat behavior |
| IN001-D05 | One deliberately selected controller and one admitted sender initially | Multi-controller/source takeover needs larger API and arbitration; reserve extensibility without implementing it. Keyboard remains separate |
| IN001-D06 | Explicit freshness/connected status; neutralize sticks/buttons on loss and require deliberate rearming | Timeout must be selected and measured. Trigger raw neutral is released, but game throttle state/hold/pause is consumer policy; never promise a silent generic engine cutoff |
| IN001-D07 | Coherent snapshots plus bounded retained button transitions with acknowledgement/overflow reporting | Per-button counters are an alternative if ordering is unnecessary; snapshots alone lose short taps. Bound retention/retries and distinguish delivery from game consumption |
| IN001-D08 | Device normalization in bridge; game dead zones/expo remain configurable above transport | Define calibration/inversion ownership explicitly to prevent double dead zones. Existing fsim settings are prior art, not a universal default |

## Stable implementation subtasks — host tranche only released

1. [ ] **IN001-01 — Contract and prior art.** Review official API documentation,
   Extender production/network/runtime boundaries, current EMOS owner guidance,
   fsim input handling and Nurples/Console8 digital joystick conventions.
   Pin consulted revisions and distinguish compatibility adapters from the new
   analog API. Resolve decisions and source-owner fences before implementation.
2. [x] **IN001-02 — Capture and local viewer.** Enumerate/select the F310 by
   stable capabilities/identity without fixed event numbers; handle unplug,
   replug, mode changes and changed paths. Compare Linux evdev with existing
   SDL mappings before selecting a maintained dependency. Avoid exclusive
   grabbing by default or disrupting fsim. Measure axis steps, drift, extremes,
   inversion, hat/button mapping and trigger independence. Preserve full raw
   values alongside calibrated/logical values in the viewer.
3. [ ] **IN001-03 — Sampling and both wire contracts.** Specify Oryx→P4 and
   P4↔EMOS separately: version/capabilities, length/bounds, byte order, axis
   signedness/centres, trigger range, hat/buttons, session/controller identity,
   sequence wrap, freshness, coherent snapshots and transition retention.
   Include malformed/unknown packets, reordered/duplicate input, bounded
   overflow, reconnect/rearm, restart and explicit disconnect semantics.
   Use monotonic receiver clocks for expiry; do not infer one-way LAN latency
   from unsynchronized host/P4 timestamps. Select ports through current service
   ownership, not hard-coded historical addresses or accidental collisions.
4. [ ] **IN001-04 — Host sender and P4 receiver.** After approval, implement
   paced coalesced axis snapshots and required transition/heartbeat delivery.
   Bound message size, queue depth, work per iteration and retries; don't block
   Linux event capture, P4 render ownership or keyboard/SD services. Reject
   stale sessions/displaced owners. Keep networking admission separate from
   controller state being accepted/applied by an application.
5. [ ] **IN001-05 — Loss, calibration and arbitration.** Exercise unplug, bridge
   crash, LAN outage, late packets, host/P4/Agon restart, source displacement,
   stuck buttons, retained-state expiry and event overflow. Make lost input
   visible; don't resurrect held controls on reconnect. Review held-controls
   rearm behavior and keyboard coexistence. Fsim decides its own pause/throttle
   semantics later, without changing generic raw control definitions.
6. [ ] **IN001-06 — State-display test appliance.** Provide a generic readable
   host view and an independently callable Agon viewer: two stick crosshairs,
   separate trigger bars, labelled D-pad/button indicators, numeric raw/logical
   values, neutral/dead-zone markers and short-press counters/history. Show
   connected/source/mode status, sample age, delivered rate, drops/duplicates,
   edge overflow and protocol identity. Large text and high contrast matter
   for Author review. Label measurement clocks and distinguish source, P4 and
   application-observed states; do not paint host-only values as end-to-end proof.
7. [ ] **IN001-07 — EMOS delivery and reusable API.** Define an atomic/coherent,
   bounded nonblocking application read with validity/freshness and transition
   semantics. Choose pull/push/cache policy and measure full packet/poll cost,
   stale-read behavior and eZ80 ROM/RAM/CPU use. Preserve ordinary VDU routing,
   keyboard input, callbacks, SD ownership and running-application boundaries.
   Assess Legacy and ExCom separately; do not depend on experimental ExExt or
   a finished native-EMOS migration without an explicit dependency decision.
   Reserve interfaces jointly with the owning API registries, not private numbers.
8. [ ] **IN001-08 — Qualification and handoff.** Use deterministic recorded input
   streams and fault injection before physical work. Verify coherent axes,
   trigger independence, tap/hold/release ordering, normalization endpoints,
   timeout/rearm and invalid packets. Measure sustained traffic, accepted rate,
   age/jitter, CPU/memory and button loss under representative graphics and SD
   loads; give same-build keyboard/no-controller baselines. Physical runs need
   fresh reservation and explicit Author scope. Stop for Author visual/handling
   review; separately authorize fsim adoption and agreed production promotion.

## Viewer lifecycle and review gates

1. Follow [test appliance lifecycle](../procedures/test-appliances.md),
   [test execution](../procedures/test-execution.md),
   [bench constraints](../qualification/bench-constraints.md) and
   [SD layout](../sd-layout.md). Save entry mode, switch only if needed, verify
   and settle for at least one second, and restore visible responsive CLI.
   Exclude unqualified double-buffered entry cleanup rather than claim success.
2. Display route belongs to EMOS. Report selected route and controller source
   visibly. Provide explicit interactive CLI commands with separately paced
   mode preselection. Escape exits; gamepad buttons are observations, not hidden
   exit/reset/menu commands. Release viewer-owned input/session state on return
   without terminating unrelated host/controller consumers.
3. Keep the host viewer usable before new P4/EMOS installation. Retain working
   keyboard/agent recovery independent of the controller under test. No runner,
   appliance or staging helper may change /autoexec.txt, including load-only
   startup left by another project. No reset-start or automatic test replay.
4. Gate 0 task review released host-only capture/view/recording. Host viewer
   review is accepted; the Author now releases LAN contract preparation.
   Later gates are approved API/protocol/ownership, offline paired implementation,
   explicit hardware staging/invocation, end-to-end Author acceptance, and
   versioned production closeout. Approval of one gate does not release all.
5. No daemon/service, LAN receiver, firmware build/deployment, persistent
   controller configuration write, fsim integration or bench reservation is
   authorized by this host tranche. No end-to-end qualification is complete.


## Host tranche evidence — 2026-10-24

1. Maintained implementation: scripts/controller_input.py and
   scripts/controller_view.py; [usage/review guide](../testing/controller-viewer.md).
   Linux evdev exposes raw ranges, report boundaries, overflow and timestamps
   without adding packages; existing fsim SDL remains unchanged. The GUI uses
   Tkinter. No network server, sender or background service is created.
2. Fourteen synthetic semantic tests pass on both Pi and Oryx: report coherence,
   trigger separation, quick taps/repeats, overflow resync, initial held keys,
   observed steps, preview endpoints, rest measurement/rejection, disconnect/
   reconnect sessions, ambiguous selection, recording/replay/corruption, partial
   report recording start, exclusive capture creation and failed-open cleanup.
3. Three-second read-only observation attaches to the real XInput F310, records
   a clean stationary session and passes replay checking. Zero movement events
   were received: physical travel/steps/button mapping are not yet validated.
4. A three-second virtual-display run on Oryx paints the live connected viewer,
   produces a review screenshot and closes normally with no Tk callback errors.
   No human-visible window is left running. Actual unplug/replug remains an
   Author review item; only simulated fault paths have been qualified so far.
5. IN001-02 and host portion of IN001-06 are prepared for review, not closed.
   Host implementation is subsequently accepted below. IN001-03 contract work
   is now released; IN001-04/07 implementation and target viewer remain gated. No architectural transport,
   wire quantization or controller-loss game policy was accepted implicitly.


## Author host review — 2026-10-24

The Author reports the viewer looks good and supplied exercised controls.
[Recording analysis](INPUT-001/HOST-REVIEW-2026-10-24.md) validates all894frames
against1848raw events over22.455s, with no input gaps, full six-axis travel,
D-pad directions and ten matched button channels. Guide, rest calibration and
physical reconnect were not recorded. All observed stick values lie on an
eight-bit lattice (step257); triggers have one-unit steps. This informs D02 but
does not select a wire format. Viewer appearance is accepted; target work and
production version/publication remain separately gated.

Second Author capture validates Guide down/up, physical disconnect/reconnect
with a new session/cleared counters and resumed axis reports. All242frames
replay from535events, no gaps. All eleven button channels now have recorded
coverage across both captures. See the host-review follow-up for exact hashes
and limits; rest calibration and held-button unplug were not exercised.


## Host publication and next tranche — 2026-10-24

The Author explicitly directs commit and push, then proceeding to the LAN
transport contract. Publish the reviewed host utility and its current usage/
evidence records; do not alter the selected firmware production bundle or
invent a release version/tag. Separate production packaging/version agreement
remains a closeout boundary. Prepare a concrete bounded LAN proposal, present
architectural decisions one at a time, and obtain their acceptance before
implementing P4 service or EMOS counterparts. No bench use is needed.
