# INPUT-001 — Analog game controllers through Extender

Prepare a reusable Oryx-to-P4 controller bridge, an EMOS-owned application
interface, and a readable axis/button test appliance. Start with the attached
Logitech F310 in XInput mode. Preserve analog input and keep future direct P4
USB capture compatible with the same logical controller interface. The current
host reader, viewer and recording tranche has passed Author review. The Author
has selected UDP and delegated packet layout, cadence and timeout. Host sender
and P4 receiver implementation was released for offline validation/building.
The Author now selects the Agon viewer in mode20 with AgonDev C++ permitted;
matching app/P4/EMOS candidate source and software/build checks are complete.
The Author-approved identified installation and corrected P4 r11 source admission
are verified. The preloaded viewer remains stopped for controller/visual review.
The Author subsequently releases the bench for deployment, requesting that the
installed mainboard VDP be retained. This authorizes P4/EMOS installation and
app staging; the viewer remains stopped for the Author to invoke.

## State and authority

1. **Status:** First host-only tranche implemented 2026-10-24; Author approves host
   viewer appearance and authorizes commit/push followed by LAN contract work.
   Guide and physical reconnect are verified; rest calibration remains
   optional/unreviewed. The subsequent UDP tranche is authorized below.
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
   were proposals at that point. The Author subsequently selected UDP and
   delegated packet layout, cadence and timeout for tuning during development.
5. The Author subsequently selects the eZ80/Agon state viewer in mode20. The
   reviewed host viewer precedes it; delivery to P4 alone does not demonstrate
   Agon input. Candidate implementation is not hardware acceptance.

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
   the LAN codec now uses the exact observed eight-bit lattice when reversible,
   with native signed16 fallback. No EMOS API format is selected by this.
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
   connection health and coherent controller-state storage. UDP is accepted.
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

## LAN implementation — authorized offline tranche

The Author accepted UDP ("UDP it is. make it so.") and then delegated layout,
cadence and timeout: "do whatever you think best ... we'll tune as we go."
The [decision record](../decisions/ADR-2026-10-24-controller-udp.md) and
[maintained protocol](../protocols/controller-lan.md) supersede the numerical
draft in the [LAN proposal](INPUT-001/LAN-PROPOSAL.md). Defaults are120Hz/250ms,
exact raw8/native fallback and128 retained transitions per endpoint.

The host sender and portable P4 receiver are implemented. Twenty-five host/core
checks pass, including real loopback sockets with synthetic input and the same
C++ core compiled into P4. Recorded-input loss replay preserves all44+2 button
transitions in exact order. Physical LAN timing, worker lifecycle and coexistence
still require bench validation. The candidate EMOS consumer now acknowledges
after copying transitions to its caller. LAN ACK still proves P4 queue storage
only;128 unconsumed transitions exhaust its bounded queue. No physical game
input or end-to-end readiness is claimed.

## Decision register

Present unresolved architectural decisions one at a time when implementation
is released. LAN choices below are recorded in the accepted decision record;
EMOS application decisions remain here for later review.

| ID | Recommendation | Alternatives, prerequisites and effects |
|---|---|---|
| IN001-D01 | Accepted by Author: Agon/eZ80 viewer in mode20, AgonDev C++ permitted | Host viewer is reviewed; target UI is built for recorded-input visual review. Live delivery still requires EMOS service/API work |
| IN001-D02 | Selected under delegation: native capture; reversible raw8 on observed lattice, native fallback | Saves four LAN bytes without rounding; EMOS representation remains unresolved |
| IN001-D03 | Accepted by Author: UDP snapshots and retained transitions | TCP/WebSocket considered; UDP loss/ordering/expiry handling is explicit; no physical latency advantage measured |
| IN001-D04 | Revised after Author feedback: event-driven capture and120Hz paced publication, matching nominal MOS tick rate | Supersedes initial100Hz; independently paced, not phase-locked. Tune1–240Hz with no catch-up bursts; physical latency/load measurement remains |
| IN001-D05 | Selected for the LAN tranche: one controller, one HTTP-admitted IPv4/UDP source | Endpoint/session binding; no implicit takeover; keyboard remains separate; no authentication claim |
| IN001-D06 | Selected under delegation:250ms timeout, neutral invalid raw state, explicit restart | Tunable50–2000ms, at least two publication periods; consumer throttle/pause/rearm policy remains separate |
| IN001-D07 | Selected for LAN: latest snapshots plus128 retained ordered transitions, ACK of storage | EMOS consumption/acknowledgement is unresolved; queue overflow invalidates input; no end-to-end reliability claim |
| IN001-D08 | LAN carries raw values without dead zones/inversion; consumer calibration policy remains open | Host preview calibration does not alter transport; existing fsim response remains consumer-owned |
| IN001-D09 | Implemented candidate for review: resident `ext.controller` cached READ, separate bounded REQUEST and retained-edge consumption | Uses existing gateway/F7 control allocation and private CI namespace/8E reply; no app callback or raw UART. Blocking per-read RPC was avoided to keep response waits outside the UI read. Physical timing/reset/coexistence and final API acceptance remain open |
| IN001-D10 | Accepted by Author,2026-10-25: no CRCs in EMOS–Extender VDP communications unless specifically requested | Firmware space, communication bandwidth and processor time are scarce. Ordinary framing/transport error handling remains; another software checksum is not a substitute. Installed controller candidate is nonconforming; correction and newly identified builds remain outstanding |

## Stable implementation subtasks

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
4. [ ] **IN001-04 — Host sender and P4 receiver.** Offline implementation and
   target build pass; physical lifecycle/coexistence validation remains. Implement
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
7. [ ] **IN001-07 — EMOS delivery and reusable API.** Matching candidate source,
   full-ROM/linked checks and native pipeline pass; see the
   [EMOS-owned task](../../../agon-emos/docs/tasks/INPUT-001.md).
   Interface acceptance/physical costs remain. Define an atomic/coherent,
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
   review is accepted; UDP selection/delegation now releases offline paired
   implementation and target compilation. The subsequent Agon viewer request
   releases the app and matching EMOS/P4 candidate software path. Later gates
   include interface review/identified staging,
   explicit hardware staging/invocation, end-to-end Author acceptance, and
   versioned production closeout. Approval of one gate does not release all.
5. No automatic daemon, physical firmware deployment, persistent controller
   configuration write, fsim integration or bench reservation is authorized by
   this offline tranche. No end-to-end qualification is complete.


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
   was subsequently released; the later UDP authorization below releases
   IN001-04 offline work. IN001-07 and target viewer remain gated. No
   controller-loss game policy was accepted implicitly.


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

The Author then explicitly selected UDP and delegated the remaining LAN layout,
cadence and timeout choices. This supersedes the proposal-only boundary for
host/P4 offline implementation and compilation. It does not release physical
firmware deployment, EMOS ABI work or fsim integration.

## UDP implementation evidence — 2026-10-24

| Check | Result and scope |
|---|---|
| Reader/core/sender regressions |25 pass on Pi and Oryx, including actual loopback UDP/HTTP with synthetic controller reports |
| Recorded-input replay |44/44 and2/2 transitions in exact order; every seventh STATE and every fifth delivered-state ACK deliberately dropped |
| Native sanitizers |100,000 malformed packets plus queue saturation/overflow pass ASan/UBSan; corpus includes valid headers to reach body validation |
| Existing native-builder checks |18 pass |
| P4-PC console compilation |Pass with controller option; actual compile graph/header dependencies and16-socket effective ceiling verified |
| Physical P4/network/controller qualification |Not performed; no firmware installed |

The compiled exploratory app is1,615,952bytes, SHA256
`f8efce2bda9364959153ca303e96bf7b1cad76f52ac702cb3ad09071804e1bc6`.
It is explicitly `UNVERSIONED-DO-NOT-DEPLOY`, built from host-publication commit
`29c4a8810707ad1edafdada3e6901429c1fb1fa2` plus dirty implementation inputs.
ESP-IDF is pinned at
`b774170ff46c393eeb5e495ea37936038d3f4f4f`; the dependency lock retains the
selected Arduino/component identities. No qualified or production identity is
created by this build. The base browser-console build does not reproduce the
bench's separately composed HDMI firmware.

Ignored local evidence retains source hashes, build/validation manifests,
app/factory images, test logs, replay receipts and Oryx staging receipts. The
Oryx sender is left stopped; no network query or session was sent to physical
P4. Actual controller-worker stack/heap, scheduling, Ethernet restart, concurrent
keyboard/video/SD behavior and EMOS delivery remain unmeasured.

Implementation gotcha: Arduino3.3.11 declares `IPAddress INADDR_NONE`, while
ESP-IDF5.5.5/lwIP defines that name as a macro. Including controller socket
headers before the established Arduino network header fails compilation. The
network owner includes the adapter afterward, with an adjacent explanatory
comment. This preserves upstream dependencies without editing their sources.

The Author subsequently challenged100Hz against MOS's nominal120Hz cadence.
The host sender default and current instructions now use120Hz (8⅓ms), retaining
the250ms timeout. The existing100Hz replay and unversioned P4 build records are
unchanged; the P4 receiver has no fixed publication rate. This host-only tuning
requires no P4 rebuild, installation or EMOS change.

## Agon viewer instruction and UI tranche — 2026-10-24

The Author directs recreating the test application for Agon, permits AgonDev C++
and explicitly chooses mode20. This settles the first target processor/viewer
choice. It does not make the absent EMOS read service available. The maintained
application is `tests/fixtures/controller`, with explicit source/output bounds
in its README. It has no private UART/GPIO access or provisional API allocation.

The initial compiled UI is a clearly labelled recorded-input visual appliance:
two sticks with signed/native and eight-bit values, two analog triggers, eleven
buttons, D-pad and press totals. Mode20 is512×384/64colours; a12×16 font and
incremental nominal20Hz updates prioritize readability. Escape exits, R clears
displayed counts, and Alt-Tab does not request exit. Single-buffered entry mode
is queried/restored with required settling; double-buffered entry is refused.
The temporary VDP font buffer reservation64001 and release are documented.

The reviewed22.455s host recording converts to896 checked states including final
invalidation. Native layout preview is generated from the target's shared C++
renderer; it does not establish execution/font/mode restoration on Agon. The
build is exploratory/unversioned, not deployed or ready for live-controller use.
No EMOS/P4 firmware, startup, route or SD contents changed. The remaining live
integration gate is an EMOS-owned, bounded controller read and retained-edge
consumption contract; an application must never open the physical UART itself.

### Bounded viewer research

The read-only official references were checked clean at MOSv3.0.2
(`8336409351ee5314e02801a7b72a4f1bb5282519`) and VDPv2.16.0
(`c7ac293d2aa81ddfa693390549bcd909069c8fc3`); consulted Agon-docs commit
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.

1. [Screen modes](../../../../agon-docs/docs/vdp/Screen-Modes.md) specifies
   mode20 as512×384/64colours/60Hz and describes double-buffered CLI hazards.
2. [VDU commands](../../../../agon-docs/docs/vdp/VDU-Commands.md),
   [system commands](../../../../agon-docs/docs/vdp/System-Commands.md) and
   [PLOT commands](../../../../agon-docs/docs/vdp/PLOT-Commands.md) establish
   mode query22/86, pixel scalingC0, counted drawing, rectangles65 and circles95.
3. [Font API](../../../../agon-docs/docs/vdp/Font-API.md) defines byte-aligned,
   MSB-first monochrome glyphs, 256 characters and explicit font selection/
   deletion. The12×16 font uses8192bytes and selects the built-in font at cleanup.
4. [MOS API/sysvars](../../../../agon-docs/docs/mos/API.md) defines mode flags,
   screen data, keyboard-down state and clock increments. Escape checks key-down
   plus ASCII27, not an arbitrary-key return. Replay time remains nominal and
   uncalibrated; the repaint interval is conservative for60/70Hz clocks.
5. Maintained [EMOS service contract](../../../agon-emos/docs/emos-v1-contract.md)
   and `src/emos.c` at`76834b9eb58c7b105bbdb6b968c7b971ebd292d8` establish the
   existing resident gateway but contain no analog-controller service. No
   placeholder service identity or private packet is called by the viewer.

## Final live software candidate — 2026-10-24

Live default mode now uses the matching candidate EMOS service; explicit replay
remains available. The [development service contract](../protocols/controller-emos.md)
defines the existing gateway/F7 carrier and private CI/8E namespace. No new global
MOS/function allocation, application UART bypass or SD lease is used.

| Final exploratory component | Bytes | SHA256 |
|---|---:|---|
| AgonDev C++ mode20 app |28,514 |`059e6b818b44f4d90dc3fd1b93ef4d4d69626e9de0bbb3231f5f39cb0bb5efe7` |
| EMOS controller profile |130,972;100 ROM bytes free |`8feace3ad4a903e4d987933bad7824035b72994484ddb4e7f4b8e93ed5c8f6ee` |
| P4-PC browser-console app |1,618,032 |`3a0055e4d357ce36d71d55baf1a365615b45a2e61ba9c84d3ca8945a3baf8807` |

App/P4 compilation, EMOS full-ROM/mandatory linked guards, resident native tests,
shared-renderer bounds and the real P4→EMOS→Agon-client native pipeline pass.
The pipeline exercises65,004 queries through healthy lease renewal without
resetting counts. VBlank deadlines prevent delayed replies/low-byte clock wrap
from reviving expired input; source age includes conservative return transit.
Marker/bar redraws avoid full-panel clearing. Physical appearance/timing and
mode cleanup remain untested.

Native-width age arithmetic avoids AgonDev's unreviewed`__smulu` runtime helper;
the generic runtime/toolchain was unchanged. The final freshness checks reduce
free ROM from the preceding479-byte checkpoint to100; further growth needs a
separate size plan. All builds are explicitly unversioned/experimental dirty
source, with exact local source/tool/API/header/build receipts. The P4 browser
composition is a compile proof, not a replacement for the deployed indexed-HDMI
composition. No bench access, install/reset, SD/startup change, emulator or
application invocation occurred.

## Deployment preparation after bench release — 2026-10-24

The Author says: "ok bench is yours to deploy. if we can keep mainboard VDP as
is that would be grand." Preserve the mainboard ESP32 VDP and user startup.
The eZ80 EMOS and P4 require their matching controller-enabled builds. Leave
the viewer stopped at handback; no visual/smoke invocation is part of preparation.

1. Read-only preflight finds the expected P4-PC USB identity, available HDMI,
   admitted neutral keyboard and offline/idle SD listener. Oryx enumerates the
   F310 XInput event device; neither Agon SD card is mounted there. Latest peer
   handoff releases the bench with a newer composed-frame mainboard VDP; that
   supersedes the earlier diagnostic image and must remain installed.
2. The retained installed P4 build uses indexed HDMI, automatic carrier,
   rolling scanout, frame/visible snapshots, bitmap fast path, BGR overlay,
   graphics timing, FS/LS USB and the configured reset bridge. The browser-only
   controller compile proof is unsuitable for this installation. Prepare an
   explicit source comparison and matching composition before building/flashing;
   current maintained source has retired some historical diagnostic switches.
3. Existing controller builds/profile are explicitly unversioned and excluded
   from deployment. Obtain agreement on the new experimental component
   identities before changing that guard or creating identified builds. Older
   task-specific standing version approvals do not establish an explicit
   controller identity agreement. Production promotion/version/tag is separate.
4. After identity agreement, freeze the exact source, run the identified full
   builds and mandatory guards, retain independently verified incoming P4/EMOS
   rollback and startup, then install/read back only the changed components.
   Stage the viewer under `/extender/controller`, establish input/source
   readiness and stop before invocation. Never modify `/autoexec.txt`.

No reset, firmware write, SD transfer, controller session or viewer invocation
occurred during this read-only preflight. Local receipts retain the exact
observations; they do not establish installation readiness.


Author agrees experimental EMOS v0.1.25, indexed-hdmi-r10 and
controller-viewer-r01 identities and directs proceeding with deployment.
Preserve mainboard VDP/startup; leave the viewer stopped for Author invocation.
This supersedes the pending identity gate above, not physical acceptance.


## Identified deployment and admission correction — 2026-10-24

The Author approved EMOS v0.1.25, indexed-hdmi-r10 and controller-viewer-r01
and directed deployment. P4 and eZ80 installation/readback verification is
complete; the mainboard ESP32 VDP and99-byte startup remain unchanged. The
viewer is loaded at040000 but has never been invoked. The foreground listener
is closed and the Legacy CLI has admitted neutral Extender keyboard input.
Controller input is **not ready**: the first Oryx sender received HTTP400 on
admission and stopped without transmitting a UDP state.

| Component | Exact build | Source commit | Verification |
|---|---|---|---|
| P4 | `indexed-hdmi-r10-b2026-10-25-02-40-35Z` | `2ebf044f893be59e769e6e95ba9d6e1c84e44094` | Full incoming rollback, flash verification, independent16MiB readback and observed boot ID |
| EMOS | `agon-emos-v0.1.25-b2026-10-25-02-41-10Z` | `b783e17ba3f2ab199baf8ed969065803c7350c55` | Complete131072-byte ROM readback matches selected padded image; CLI identity observed |
| Mode20 viewer | `controller-viewer-r01-b2026-10-25-02-41-10Z` | `6861af2e836ddc68024a49a59e1fd67bdb588119` | Installed28,528-byte binary readback exact; loaded without RUN |

The P4 source freeze is the installed r09 source28514129 plus only the
optional controller integration. Every display source hash, timing/carrier,
scanout/storage setting and configured reset bridge matches r09. SDK differences
are source paths and the intentional socket ceiling10→16. EMOS occupies131010
ROM bytes, leaving62. These are experimental builds, not production promotion.
The initial post-boot maintenance batch did not reach its listener; a subsequently
verified CLI/status exchange and fresh readback batch completed without another
FLASH. Input-ready during startup does not establish that load-only startup has
finished; future deployment coordination needs actual CLI handback before dispatch.

### IN001-F01 — IPv4 controller refused by the dual-stack HTTP listener

1. Observed failure: Oryx sender admission returns HTTP400, `IPv4 required`,
   with zero sent/acknowledged UDP states and no admitted controller session.
2. ESP-IDF5.5.5 commitb774170ff46c393eeb5e495ea37936038d3f4f4f
   `components/esp_http_server/src/httpd_main.c:httpd_server_init` deliberately
   selects PF_INET6 when CONFIG_LWIP_IPV6 is enabled. Its IPv4 clients have mapped
   IPv6 peer addresses. This is intentional upstream behavior, not an SDK defect.
   The new local handler incorrectly allocated sockaddr_in and required AF_INET.
3. The prepared correction uses sockaddr_storage and extracts either ordinary
   IPv4 or mapped IPv4, retaining the network-order source address for UDP
   binding. Genuine IPv6 remains outside the IPv4 UDP contract. The adjacent
   `http_peer.hpp` explains the adaptation; remove/rework it only when listener
   or controller transport address-family ownership deliberately changes.
4. Twelve focused tests pass, including a real IPv4 loopback client accepted
   by an IPv6 socket, mapped/raw address equivalence, truncation and genuine
   IPv6 rejection. A fresh isolated object using the actual P4 SDK/compiler
   action also compiles. The frozen r10 build outputs were not changed.
5. Corrected source is prepared in maintained source and the isolated HDMI
   composition. A new P4 revision agreement, full identified build and verified
   installation remain before starting the sender again. Do not reflash EMOS
   or mainboard VDP, rerun uncertain commands, or launch the viewer as a check.

Machine-local receipts, rollback bytes and stopped Oryx sender evidence remain
under the ignored installation record. No controller handling, visual, latency,
mode-cleanup or coexistence acceptance is claimed.


Author approves indexed-hdmi-r11 and directs proceeding with the prepared
mapped-IPv4 admission correction. Full identified build and P4-only installation
are authorized. Preserve EMOSv0.1.25, mainboard VDP and startup; viewer remains
stopped. Source freeze14c7f7b6 derives from the retained r10 HDMI composition.


## r11 deployment handback — 2026-10-24

P4 `indexed-hdmi-r11-b2026-10-25-03-12-12Z`, source `14c7f7b6f7d395dc0dd1a9a0be44e1a66e9ab28e`, is installed. Canonical full
build/compile-graph checks, verified incoming rollback, flash verification,
independent16MiB readback and observed startup identity pass. Outside written
flash sectors is unchanged. HDMI/display/reset selection remains the r10/r09
composition. IN001-F01 is corrected: Oryx HTTP admission succeeds and real
F310 UDP snapshots arrive with valid current source state and acknowledgements
at the configured120Hz/250ms. This checks host-to-P4 readiness, not Agon
application consumption, visual timing or all fault cases.

EMOSv0.1.25 and the mainboard VDP were not flashed again. Startup matches its
retained99-byte original. A real CLI/status handback is observed after reboot
before dispatching the finite stopped-viewer LOAD helper. The SD listener exits
to a Legacy CLI, keyboard neutral; viewer-r01 is loaded at040000 but never RUN.
The Oryx source remains running for the Author. No test invocation, controller
handling/visual acceptance or production promotion is claimed.

Interactive review: `VDU 22 20`, wait at least one whole second, then
`RUN &040000`. Escape exits; R clears displayed counts. Source/flash/CLI receipts
and original rollback remain in the machine-local record.


Receive-cadence limit: the configured Oryx publisher is120Hz, but a short
2.014-second Pi-monotonic observation saw45 new P4 accepted states
(22.3/s) while the highest source sequence advanced236. Source/ACKs stayed
valid with no reported rejection or queued edges. This is a bounded counter
observation, not a calibrated latency/throughput qualification or proof of
where packets were lost. Retained transitions remain queued until consumption.
Receive cadence/load needs investigation in IN001-04/IN001-08 after the first
manual state/visual review; do not advertise120Hz P4 application delivery.

## IN001-F02 — First human viewer run loses EMOS link — 2026-10-24

The Author invoked viewer-r01 and reports no position markers or button
changes; the displayed status is `EMOS controller link lost`. Host/P4 status
remains active and valid, with44 retained transitions not consumed by Agon.
This bounds the observed failure to Agon-side service/delivery, rather than
controller detection. The exact failing operation/status is not yet known.
The running application and firmware have been left untouched during diagnosis.

1. Prepared viewer correction: perform the initial full screen draw before
   the first controller REQUEST. Previously that draw ran after REQUEST and
   could consume its30-unit deadline. This is a timing hazard, not yet a
   demonstrated physical cause of this failure.
2. Preserve and display the failed gateway operation and numeric status on the
   failure screen and after normal exit; do not automatically reopen a failed
   lease or replay the application.
3. Native cross-component regression passes, including an actual resident
   timeout returning READ/unavailable35 through the application client.
   The modified app cross-compiles as unversioned, nondeployable preparation.
4. Author approval of viewer-r02 is required before stamping/deploying the
   replacement. Keep EMOS, P4, mainboard VDP and startup unchanged for this
   diagnostic step. Actual cause, corrected physical input handling and visual
   acceptance remain open; preserve the original viewer-r01 failure.

Author approves viewer-r02 diagnostic replacement and deployment on2026-10-24.
Firmware and startup remain unchanged; leave the replacement stopped for Author
invocation. Keyboard admission/source have since expired; ordinary monitored
recovery is required before the SD transfer.


### Viewer-r02 diagnostic deployment handback — 2026-10-24

`controller-viewer-r02-b2026-10-25-03-51-23Z`, source
`2055b680f4e7fb2a28602e3d6bcd0b494018e9a3`, is deployed at
`/extender/controller/ctrlview.bin`:28,795bytes, SHA256
`deb715574983c8c4017dc960299d23cf80a12bb3b270884b41d48053ec6fc62f`. Independent full binary
readback matches. The prior viewer-r01 binary is retained locally and as the
listener sibling backup. The finite `/extender/install/cv-load02.txt` loads
this binary then starts the foreground listener; observed listener reentry
establishes LOAD completion. Listener EXIT closes that final batch command;
Legacy CLI has the viewer preloaded at040000, never RUN by the agent.

One ordinary Agon reset restored fresh input admission after the failed review;
no P4 reset or firmware flash was needed. Cleared/fresh ExCom CLI/status output
verified actual EMOS command execution before returning Legacy and transferring.
Startup was read back before and after deployment and matches its retained
99-byte load-only original. P4r11, EMOSv0.1.25 and mainboard VDP remain unchanged.
The timed-out Oryx source ended; its recording/logs are retained. An explicitly
restarted sender has fresh P4 active/valid snapshots, no fault and neutral
controls at handback. This is service preparation, not Agon consumption proof.

Author review: `VDU 22 20`, wait at least one whole second, then `RUN &040000`.
Report the full `EMOS link lost: ...` line if failure recurs. IN001-F02 remains
unresolved until that diagnostic or working physical input establishes cause.


### Viewer-r02 human result and linked-image diagnosis — 2026-10-25

The Author reports `EMOS link lost: request35` (reading tentative). The viewer
still fails after initial drawing was moved before REQUEST. Do not claim that
initial drawing caused or corrected IN001-F02. REQUEST/unavailable35 can follow
resident lease expiry or loss of healthy UART ownership/admission; the failing
operation alone does not distinguish those paths.

A bounded headless instruction experiment executes the exact installed
131,010-byte EMOS image, including the real public gateway, controller service,
assembly byte parser and complete98-byte response dispatch. Only the physical
UART send boundary is mocked; clock/IRQ arrivals are controlled. OPEN, READ busy,
REQUEST, framed8E response, READ of actual axes/triggers and next REQUEST pass.
This rules out a deterministic ABI/wire decoding failure in that controlled
sequence, not physical timing/IRQ/FIFO interaction. Response dispatch and READ
each execute roughly177,000 instructions in this model; those counts are not
physical cycles, calibrated latency or a demonstrated timeout cause.

The running viewer has not been stopped or reset during this diagnosis. P4
still reports keyboard admission, but that is not proof that eZ80 input works.
Author Escape/CLI observation is needed to distinguish controller-only expiry
from loss of the resident keyboard/UART path. The restarted Oryx source also
ended after82.9seconds with missing fresh ACKs; its log/capture are retained.
LAN cadence/timeout remains a separate unresolved failure, not an explanation
for why EMOS returns35 rather than a responsive invalid-source snapshot.


Author confirms Escape does not exit viewer-r02, and also failed in the prior
run. This supports investigating the shared resident input path, rather than
only controller lease freshness. Source inspection finds READ executes two
96-byte CRC calculations while keyboard interrupts are disabled, including when
a new P4 reply is outstanding. That is an unsafe receive-overlap window: UART1
can receive a100-byte response while EMOS cannot drain its16-byte FIFO and has
not asserted receive backpressure. Actual physical fault timing has not been
captured, and the running failed instance remains preserved.

The Author challenges why controller delivery uses checksums when ordinary MOS
packets do not. CRC was an agent-added private protocol choice, not an official
MOS requirement. Recommendation: remove the controller UART/application CRC
work and rely on bounded typed/length framing, caller/query correlation and the
existing UART error/fault handling. Do not treat this discussion as approval
of a new wire contract, firmware version or deployment. LAN checksum policy is
a separate transport decision. No correction has yet been built or flashed.


## IN001-F02 correction prepared — 2026-10-25

The Author directs continuing the bug fixes after accepting the no-CRC policy.
The old installed ROM is reproduced under a bounded instruction-arrival model:
a P4 reply overlaps a cached READ, UART1 FIFO overruns, the actual resident
fault handler disables keyboard input, and the next REQUEST returns35. This
matches the observed controller error plus dead Escape. It is controlled
instruction evidence, not a physical timing capture.

1. Prepared carrier2 removes every controller CRC calculation and the response
   trailer: result96bytes/`CIS2`. The existing fixed F7 envelope remains16bytes
   with its last two bytes reserved zero; this avoids changing the shared
   console recognizer. Old carrier1 and98-byte app buffers are refused. P4,
   EMOS and the Agon viewer must be updated as a matched combination.
2. EMOS returns busy31 for READ while a refresh is pending. With no outstanding
   request the cache cannot be republished; EMOS unlocks interrupts for copying,
   zeroing unused records and freshness calculations, then briefly locks to
   revalidate and commit post-copy acknowledgement. Tick/fault cleanup changes
   flags without modifying cache bytes. The request timestamp now precedes its
   waiting flag to avoid an ISR observing an old timestamp on a new request.
3. The linked correction rejects the controlled overlap without faulting,
   returns a coherent fresh sample afterward, and delivers an entire Escape
   record through the actual receive IRQ during a cached READ. Normal cached
   READ masking falls from176,936 to82 executed instructions in the tested
   path. These are instruction counts, not calibrated elapsed time/cycles.
4. All27 host/controller tests, the resident host harness, AgonDev viewer
   compilation and the full EMOS wrapper/mandatory linked checks pass. The
   unversioned ROM uses130,748bytes with324free; exact named-build size remains
   to be measured. Canonical P4/EMOS carrier copies match. Actual P4 target
   compilation passes for the network owner and console owner. Its isolated
   source starts from installed r11/source14c7f7b6 and adds only the two
   controller files (commit0b49540b); display code/configuration stays pinned.
5. Full P4 preparation is blocked specifically by the indexed-PPA builder's
   requirement for a clean, named indexed-hdmi revision. Proposed matched
   identities are EMOSv0.1.26, indexed-hdmi-r12 and controller-viewer-r03;
   Author naming agreement is still required before identified builds or
   deployment. Do not reuse a prior revision or weaken the builder gate.
6. No live input, reset, flash, SD transfer or test invocation was performed.
   The failed viewer instance and existing firmware/startup remain preserved.
   Oryx publication/receiver cadence and missing-ACK timeout are a separate
   unresolved gate, not claimed corrected by this UART change. Existing
   non-controller console/SD CRC dependencies are separate policy migration
   debt; this correction makes no platform-wide CRC-removal claim.

The maintained paired contract now describes the prepared checksum-free
format; the earlier carrier description is frozen under the task evidence.
Build/target-object/linked-test logs and hashes remain in the ignored local
INPUT-001 evidence record. Physical review and production promotion remain open.


Author approves EMOSv0.1.26, indexed-hdmi-r12 and controller-viewer-r03 on
2026-10-25 and directs continuing the matched correction. This settles naming
for the private experimental carrier/API change; it does not accept the feature
or promote production. Build/installation verification is authorized, with the
viewer left stopped for Author invocation. Preserve mainboard VDP/startup and
follow the no-CRC processor-communication policy for deployment.

### Approved named builds complete; deployment transport pending

All three named correction builds now pass their offline checks. They are
prepared candidates, not installed or physically accepted results.

| Component | Exact build | Bytes | SHA-256 |
|---|---|---:|---|
| P4 application | `indexed-hdmi-r12-b2026-10-25-04-32-32Z` | 1,769,984 | `3a362de507a0ed5b65a2e4454b209d4fdbf81bd5debe02465f8fe5f82cbf3e64` |
| EMOS raw ROM | `agon-emos-v0.1.26-b2026-10-25-04-24-35Z` | 130,786 | `b70043198a9c74625b6b49c80451d93188e5733df2a05650e4be69ea42ef4ebd` |
| Agon viewer | `controller-viewer-r03-b2026-10-25-04-24-35Z` | 28,795 | `5a1a4e79653f248bf2610f7ad748d7a964eb185620240106a232416e98002182` |

1. P4 native composition/action validation passes, and all21 declared artifact
   hashes were independently verified. Source0b49540b changes only the two
   controller files relative to the installed r11 source; HDMI, board and
   dependency inputs remain pinned. An interrupted earlier compile produced
   no validated image; its timestamp is not the final P4 build identity.
2. Named EMOS source11b7a5c1 passes the linked receive-overlap/Escape regression
   and leaves286 ROM bytes free. Its padded128KiB installation image has SHA-256
   `cc6d6d589a4c48b6713180f1d7bcb7966c735969c5fef349477c554fd8733a64`.
   This saves224bytes versus the installed named v0.1.25 ROM. Neither instruction
   testing nor compilation establishes physical controller delivery.
3. The SD overlay, finite SAVE/FLASH and SAVE/LOAD maintenance files, exact-file
   manifest and direct-card staging helper are prepared. No maintenance file
   invokes the viewer or changes startup. Oryx host-disk staging is separate
   from deployment onto the Agon SD card.
4. The existing P4–EMOS SD service still computes CRCs. The standing prohibition
   therefore prevents using that service without an explicit Author exception.
   The Extender card is not currently mounted on Oryx; leave other media alone.
   Resolve either direct access to that card or a one-installation exception
   before any dependent reset, SD transfer or firmware change.
5. The failed viewer instance, installed P4r11/EMOSv25, mainboard VDP and startup
   remain unchanged. No physical test was invoked. Installation verification
   and fresh source readiness still precede a handback for Author invocation;
   Oryx-to-P4 cadence/ACK limitations remain open.

The Author subsequently directs correcting fast-copy CRC cost under REMOTE-005
R05-11. The prepared P4r12 remains immutable evidence; it cannot receive the
new fast carrier. Use the new matched P4/listener only after naming and
bootstrap are resolved. Prepared EMOSv26 and viewer-r03 bytes remain unchanged.
The failed installed viewer is still preserved; no physical test was invoked.


Author approves indexed-hdmi-r13 and sdserve-v0.3.0 on2026-10-25, including
one final legacy CRC-bearing transfer session to bootstrap their installation.
This is a bounded exception, not general permission for checked traffic.
Matched installation/readback and source readiness are authorized; viewer
invocation remains with the Author. Preserve mainboard VDP and startup.
