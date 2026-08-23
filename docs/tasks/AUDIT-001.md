# AUDIT-001 — Audit physical bench-test and compatibility wiring coverage

## State

- Status: Complete — accepted findings assigned or explicitly deferred
- Started: 2026-08-22 21:41 EDT
- Finished: 2026-08-22 22:53 EDT

## Intent

Establish one reviewable inventory of physical bench tests already executed or
proposed for Agon Extender, expose capabilities that need physical
qualification but presently lack a test, and identify missing or unresolved
wiring needed to reproduce the accepted stock VDP application-facing behavior.

This is an audit and planning task. It does not authorize firmware, MOS, test
fixture, protocol, pin-assignment, wiring, or procedure changes. A gap may say
that new wiring could be required, but resolving it requires the normal design,
versioning, and Author-approval process.

## Scope and compatibility boundary

Primary scope is physical behavior required by the accepted compatibility
surface in [SETUP-004's VDU inventory](SETUP-004/VDU-inventory.md), interpreted
through the operating modes and carve-outs in
[ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md)
and [SETUP-005](SETUP-005.md). This includes the command path, response path,
startup synchronization, MOS-visible results, display and audio output,
input-dependent behavior, timing, reset, failure, and mode transitions.

The audit accepts the pinned v1 carve-outs rather than silently restoring them:
printer/local USB serial, console and terminal modes, ZDI, Intel HEX/YMODEM,
the stock serial updater, and other explicitly excluded maintenance/operator
facilities are not required as working Extender services. Their selected
mode-specific failure, no-op, or stock-fidelity behavior may still require
physical qualification after `SETUP-005-D006` is resolved.

Secondary scope records already-proposed physical qualification for Extender's
network, browser, optional wireless, and local-storage capabilities. It does
not attempt to invent tests for extended capabilities whose contracts do not
yet exist.

## Authority and evidence classes

- [Hardware design target](../../hardware/designs/light2-harness-r01/README.md)
  and its authoritative
  [profile](../../hardware/designs/light2-harness-r01/profile.yaml).
- [Logic-analyzer fixture](../../hardware/fixtures/la03-p4-probe-fixture-r01/README.md)
  and its authoritative
  [profile](../../hardware/fixtures/la03-p4-probe-fixture-r01/profile.yaml).
- [PORT-003 qualification plan](PORT-003/qualification-plan.md) and current
  qualified [frame-service procedure](../procedures/p4-frame-service-qualification-r03.md).
- Open implementation tasks [PORT-003](PORT-003.md),
  [PORT-004](PORT-004.md), [PORT-005](PORT-005.md),
  [PORT-006](PORT-006.md), and [PORT-007](PORT-007.md).
- Official VDP v2.16.0 and MOS behavior recorded by SETUP-003 and SETUP-004,
  including the stock General Poll startup synchronization.

The tables use these evidence classes:

- **Current-project pass:** qualified by a tracked clean-project procedure and
  run.
- **Inherited evidence:** physically exercised in the legacy project and
  retained as evidence, but not qualification of the current project.
- **Explicitly planned:** a current task or qualification plan requires the
  bench result, though a complete procedure may not yet exist.
- **Implied requirement:** compatibility or a required outcome cannot be
  credibly claimed without the result, but no task presently states the
  physical test clearly enough.
- **Blocked by decision/design:** the expected behavior or physical path is not
  sufficiently settled to write a valid procedure.

## Existing physical evidence

| ID | Bench evidence | Status and present claim | Authority |
|---|---|---|---|
| `AUDIT-001-E01` | P4 silicon, flash, PSRAM, 360 MHz CPU, partition layout, repeated reset, and USB diagnostic identity | **Current-project pass.** Four boots passed without panic, memory failure, or reset loop. This proves board bring-up, not VDU compatibility. | `p4-canary-r03`; run `SETUP-001-2026-08-20-22-31-26Z` |
| `AUDIT-001-E02` | Sink-independent logical frame cadence, rollover, counted edges, bounded mailbox drops, repeated service restart, and heap stability | **Current-project pass.** The Agon was disconnected; no command transport, VDU facade, physical sink, analyzer timing, or MOS behavior was qualified. | `p4-frame-service-qualification-r03`; run `PORT-003-2026-08-22-23-58-56Z` |
| `AUDIT-001-E03` | Eight-bit forward bus pin map, PARLIO reception, control timing, record integrity, and throughput through approximately 0.84 MiB/s | **Inherited evidence.** It supports `light2-harness-r01` as the first target but must be repeated against committed current-project firmware, MOS/eZ80 code, and procedure before qualification. | `light2-harness-r01` legacy PRX-06 evidence |
| `AUDIT-001-E04` | Shared-PC0/PC1 UART direction switching, transceiver break-before-make, fixed-frame exchange, and following parallel record at 115,200 baud | **Inherited evidence only.** The experimental fixed-frame protocol is not selected product architecture, and the reduced speed does not qualify the stock 1,152,000-baud contract. Electrical ownership results remain useful. | `light2-harness-r01` legacy REV-02 evidence |
| `AUDIT-001-E05` | Live breadboard and analyzer attachment preflight with the Agon disconnected | **Current-project observed fixture state.** It controlled the PORT-003 run but made no electrical timing claim. Only the green analyzer lead was newly physically confirmed; other fixture assignments retain their stated evidence status. | `light2-harness-r01`, `la03-p4-probe-fixture-r01`, PORT-003 run |

## Compatibility-critical bench-test inventory

These are test requirements, not test procedures. They deliberately avoid
choosing packet formats, timing thresholds, wiring changes, or implementation
mechanisms that have not been accepted elsewhere.

| ID | Physical bench result | Planning status | Dependency or current gap |
|---|---|---|---|
| `AUDIT-001-C01` | Requalify the complete eight-bit forward path on the current clean project: all data lines, `CLOCK`, `VALID_N`, `READY_N`, record integrity, backpressure, sustained transfer, and recovery. | **Explicitly planned** by SETUP-004 Work 1.c; no current-project procedure. | Requires a selected transport implementation, committed eZ80 fixture, complete probe coverage or another defensible integrity oracle, and accepted performance bounds. |
| `AUDIT-001-C02` | Qualify the P4-to-eZ80 UART1 return path at 1,152,000 baud with the selected framing, buffering, error handling, and whatever flow-control behavior the compatibility design requires. | **Explicitly planned** by SETUP-004 Work 1.c; no procedure. | Present wiring has only 115,200-baud inherited evidence. Complete target-speed and flow-control behavior is unqualified; added or revised wiring may be required. |
| `AUDIT-001-C03` | Qualify safe coexistence and every selected transition between parallel use of PC0/PC1 and UART1 use of the same nets, including no bus contention, released-idle states, timeout recovery, reset, and either endpoint changing modes first. | **Explicitly planned** in the accepted harness/Work 1.c boundary; no current procedure. | The shared-net mux/ownership design is candidate-only. Any changed enable logic, pin ownership, or timing requires a new harness revision. |
| `AUDIT-001-C04` | Run the official MOS/VDP startup synchronization end to end: MOS issues `VDU 23,0,&80,1`, Extender consumes it through the selected command path, returns the unchanged General Poll response, and the MOS-owned parser observes readiness. | **Implied requirement with an existing official protocol**; PORT-008 owns its procedure and execution. | Becomes meaningful after PORT-003 Phase E, PORT-008's transport candidate, and the selected MOS UART1 response route. No new handshake protocol is needed. |
| `AUDIT-001-C05` | Exercise representative and boundary-length stock VDU byte streams from MOS/application code through Extender, including fragmented commands, back-to-back commands, buffering, timeout, flow control, and parser resynchronization. | **Implied requirement**; host fixtures are planned, physical coverage is not explicit. | Depends on transport implementation and strict-mode malformed-stream policy. Must compare application-visible behavior with official VDP v2.16.0 rather than define cleaner behavior by accident. |
| `AUDIT-001-C06` | Verify every retained VDP response class reaches the correct MOS-owned parser/domain with exact packet bytes, completion flags, and sysvar effects where applicable. | **Implied requirement**; no comprehensive physical matrix or procedure exists. | Blocked by `SETUP-005-D003`; stock MOS does not parse the adopted UART1 return path. Requires an accepted MOS-owned route, not direct P4 writes to MOS memory. |
| `AUDIT-001-C07` | Physically validate documented screen modes, fallback behavior, context reset, buffer swap/wait, frame count, mode information, and representative visible VDU output through the selected Rev 1 presentation sink. | **Explicitly planned** by PORT-003 Phases E and G, but the current plan does not yet define the complete physical visual oracle. | Phase D/E implementation and a selected sink are prerequisites. Network/browser output location differs from stock analog video, so logical/pixel fidelity and delivery behavior must be stated separately. |
| `AUDIT-001-C08` | Validate palette quantization, Copper scanline changes, software and hardware sprites, cursors, readback, and composed presentation against independently known images/results on target hardware. | **Explicitly planned** by PORT-003 Gate D/G; Gate D currently emphasizes deterministic fixtures rather than a physical sink. | Requires Phase D and a capture/comparison method. Readback must remain logical while physical presentation includes Copper and overlays. |
| `AUDIT-001-C09` | Validate frame timing, VSYNC-equivalent waits, queued drawing completion, callbacks, and command responsiveness while the real presentation sink is normal, slow, disconnected, and reconnecting. | **Partly planned.** Logical sink independence passed in Phase C; real-sink physical qualification is deferred to PORT-003 F/G and network work. | Requires the browser/video consumer and accepted timing/latency limits. Current run had no physical sink or Agon command source. |
| `AUDIT-001-C10` | Exercise all retained audio commands from an Agon program, verify exact acknowledgements/channel status/logical timing, and separately measure delivered browser audio, latency, jitter, drift, reconnect, and concurrent video. | **Explicitly planned** by PORT-004; no procedure. | Requires PORT-004 and PORT-006. Rev 1 does not promise the stock analog output location or characteristics. Optional onboard-VDP playback remains blocked by `SETUP-005-D005`. |
| `AUDIT-001-C11` | Verify onboard-VDP keyboard/mouse packets still reach MOS unchanged in legacy/cooperative operation and that explicitly forwarded processed events produce the selected EDP-local behavior without duplicate packets or competing sysvar writers. | **Host testing is planned** by PORT-005; the corresponding integrated physical bench test is only implied. | Requires PORT-005 and the accepted portion of `SETUP-005-D007`. Transparent exclusive-mode input remains unresolved; new wiring is not presently selected. |
| `AUDIT-001-C12` | Verify retained keyboard/mouse-dependent display behavior in EDP-exclusive mode: paged-mode control, control keys, mouse state/cursor operations, variables, and callbacks. | **Blocked by decision/design.** | `SETUP-005-D007` must select the routing mechanism. The current proof-of-concept application relay cannot establish untouched-application compatibility. A software/MOS route is preferred, but the audit cannot rule out a wiring consequence before that decision. |
| `AUDIT-001-C13` | Verify RTC read/set commands, response packets, MOS sysvars, reset persistence, and any network synchronization without competing clock writers. | **Blocked by decision/design.** | `SETUP-005-D008` must select authority and routing before a valid physical test can be written. No additional signal wiring is presently indicated. |
| `AUDIT-001-C14` | Qualify legacy, EDP-exclusive, and cooperative mode selection, discovery, entry/exit, reset, failure, recovery, and deterministic fallback with aware and unaware programs. | **Blocked by decision/design.** | `SETUP-005-D001` through `D004` own routing and lifecycle. Selection may be software-only, but no physical selector or extra wiring has been accepted. |
| `AUDIT-001-C15` | Demonstrate that legacy mode makes a powered or unpowered Extender electrically and logically absent: onboard VDP operation remains normal, no shared line is driven improperly, and either-order power/reset cannot back-power or wedge either board. | **Implied compatibility and safety requirement**; QUAL-002 owns procedure design and execution. | `light2-harness-r01` explicitly leaves production isolation and either-order power behavior unqualified. Revised isolation, switching, or power-boundary wiring may be required. |
| `AUDIT-001-C16` | Test independent Agon, onboard-VDP, and P4 reset/power sequences during idle, command transfer, response transfer, and rendering; prove bounded recovery or the selected visible failure. | **Implied requirement** assigned to QUAL-002; current P4-only reset tests do not cover the assembled system. | Reset coordination is not wired or specified. The eventual mode lifecycle may avoid a reset conductor, but that conclusion has not been qualified. |
| `AUDIT-001-C17` | Exercise malformed, truncated, stalled, and overrun command/response streams in each strict and non-strict mode and record parser recovery, timeout, reset, crash, or diagnostic behavior against the accepted policy. | **Blocked in part by `SETUP-005-D006`;** no physical procedure exists. | Strict modes may intentionally reproduce stock failure behavior. Safer modes may improve it. The procedure cannot assume one policy for all modes. |
| `AUDIT-001-C18` | Exercise every scoped maintenance/operator carve-out sufficiently to prove its selected mode-specific no-op, rejection, fallback, or stock-observable failure without corrupting later normal VDU traffic beyond the accepted behavior. | **Blocked by `SETUP-005-D006`.** | Working printer, console/terminal, ZDI, transfer-mode, and stock updater services are not v1 compatibility requirements; graceful or faithful disposition still needs evidence after selection. |
| `AUDIT-001-C19` | Repeat the accepted compatibility matrix on Console8 with its different host GPIO/header arrangement. | **Known future requirement; no wiring design or procedure.** | Requires a separately versioned Console8 harness. `light2-harness-r01` is not authority for Console8. New wiring is definitely required, but no pins should be inferred in this audit. |

## Secondary already-proposed bench tests

These are real project requirements but do not establish stock VDP
compatibility by themselves.

| ID | Physical bench result | Planning status | Authority/gap |
|---|---|---|---|
| `AUDIT-001-X01` | Wired-Ethernet link, addressing, DNS, throughput, reconnect, congestion, concurrent media, and failure behavior. | **Explicitly planned**; no procedure. | PORT-006 |
| `AUDIT-001-X02` | Browser video transport under normal, slow, disconnected, reconnecting, and concurrent-audio conditions without changing logical VDP progress. | **Explicitly planned**; no procedure. | PORT-003 F/G and PORT-006 |
| `AUDIT-001-X03` | Network update authentication/integrity, interruption, power loss, rollback, restart, and recovery. | **Explicitly planned**; no procedure. | PORT-006; requires controlled recoverable update fixtures. |
| `AUDIT-001-X04` | Optional MOD-WIFI-ESP8266 backend, dedicated-header electrical behavior, selected module firmware/protocol, reconnect, throughput, and coexistence. | **Explicitly planned at capability level**; no accepted header profile, module protocol, or procedure. | PORT-006. New carrier/header wiring is expected but not defined. |
| `AUDIT-001-X05` | DevKit microSD supported cards, mount lifecycle, throughput, concurrency, removal/reinsertion, full media, malformed filesystem, interrupted writes, and recovery. | **Explicitly planned**; no procedure. | PORT-007; board-native SD wiring must first be verified against the exact DevKit revision and all selected pin uses. |
| `AUDIT-001-X06` | MIPI-DSI LCD and MIPI-HDMI output behavior. | **Capability discussed but not represented by a current TODO implementation/qualification task.** | Outside the primary compatibility audit. Connector/board support must be defined before testing; no new carrier wiring is assumed here. |

## Wiring and fixture coverage findings

### `AUDIT-001-W01` — Forward bus is defined but not currently qualified

The complete Light 2 forward pin assignment and conditioning are authoritative
as `light2-harness-r01`, and inherited evidence is strong. The clean project
has not yet qualified that harness with its own firmware, eZ80 sender, run
manifest, and complete integrity/timing evidence.

### `AUDIT-001-W02` — Stock-compatible return transport is incomplete

The candidate buffered PC0/PC1 circuit defines P4 RX, P4 TX, and two buffer
enable controls and has bounded 115,200-baud evidence. The accepted target is
1,152,000 baud. Complete flow-control behavior, buffering, routing into MOS,
and coexistence with parallel D0/D1 remain unqualified. The official VDP uses a
duplex UART with RTS flow control by default and supports CTS/RTS duplex
operation. The split Extender transport may not need an electrical copy of
every stock wire, but it must preserve the application-visible contract and
prove equivalent pacing and recovery. Whether that requires additional
conductors or revised switching is an open hardware/transport design question.

### `AUDIT-001-W03` — Shared PC0/PC1 ownership remains candidate-only

PC0 and PC1 are parallel D0/D1 in the forward bus and UART1 TX/RX in the
candidate return circuit. Inherited evidence proves bounded break-before-make
behavior for a legacy experiment, not the selected production lifecycle.
Target-speed transitions, resets, failures, both endpoints changing ownership,
and operation with the complete bus must be qualified. Any revised ownership
circuit is a new harness revision.

### `AUDIT-001-W04` — Legacy electrical absence and power safety are open

The current harness forbids joining independently powered rails and defines a
common signal ground, but production isolation, either-order power behavior,
and the electrically absent legacy mode are explicitly unqualified. The
breadboard must not be promoted into a compatibility claim until powered,
unpowered, reset, and fault states prove that Extender cannot disturb the
onboard VDP or back-power either board. Additional isolation or switching may
be required.

### `AUDIT-001-W05` — Analyzer coverage is useful but incomplete

`la03-p4-probe-fixture-r01` observes selected data/control/ownership signals.
Only some assignments have direct run or Author verification, and eight
channels cannot simultaneously establish every bus bit, all control signals,
UART data, possible flow-control lines, and power/reset behavior. Each future
procedure must define the exact probe map and claim boundary. A revised probe
fixture, multiple captures, oscilloscope measurements, or endpoint integrity
oracles may be required; this audit selects none of them.

### `AUDIT-001-W06` — Exclusive input compatibility has no selected physical path

Legacy and cooperative modes can leave keyboard/mouse hardware on the onboard
VDP and preserve its UART0 packets to MOS. The proof-of-concept forwards
processed events in software. Untouched applications in EDP-exclusive mode
need a selected relay/routing design before their input-dependent behavior can
be qualified. No direct P4 peripheral wiring is planned for v1, and this audit
does not add any.

### `AUDIT-001-W07` — Console8 requires its own harness

The current authority is only for Agon Light 2. Console8 has a different GPIO
pinout and needs a separately reviewed, versioned, and qualified harness before
compatibility claims can extend to it.

## Plan gaps and required follow-on disposition

1. **Transport implementation lacked a TODO item.** PORT-008 now owns the
   parallel-forward/UART1-return adapter, `C01`–`C06`, and the existing General
   Poll as its first end-to-end compatibility canary.
2. **No central compatibility qualification matrix exists.** QUAL-001
   now owns promotion of the permanent matrix. PORT-003,
   PORT-004, PORT-005, and SETUP-005 each own pieces, but no accepted plan maps
   every retained VDU command/response class to host evidence, target evidence,
   physical sink observation, MOS sysvar observation, operating mode, and
   carve-out. Such a matrix should be generated from the accepted VDU inventory
   rather than maintained as an unrelated competing command list.
3. **System power/reset qualification was unassigned.** QUAL-002 now owns
   assembled-system isolation, either-order power, independent reset, and
   legacy-absence qualification.
4. **Full Light 2 fixture coverage is not defined.** QUAL-002 and each affected
   transport procedure must define a
   controlled way to observe or independently validate all claimed lines and
   relevant analog/electrical properties without pretending the current
   eight-channel attachment proves more than it sees.
5. **Mode-dependent tests cannot be finalized yet.** SETUP-005 must settle
   routing, response ownership, input, RTC, maintenance behavior, and lifecycle
   before `C06`, `C12`–`C14`, `C17`, and `C18` can become procedures.
6. **Extended hardware remains deliberately incomplete.** Optional Wi-Fi,
   MIPI outputs, future audio hardware, and post-v1 user GPIO expansion should
   receive tests only after their capability and hardware contracts mature.

## Accepted follow-on ownership register

| Audit scope | Owner | Sequencing disposition |
|---|---|---|
| Permanent compatibility and qualification matrix | `QUAL-001` | First follow-on task; Review Gate 1 precedes PORT-003 Phase D implementation. |
| `C01`–`C06`, `W01`–`W03`, and transport portions of `W05` | `PORT-008` | Physical analysis may begin after QUAL-001 Gate 1; official General Poll waits for PORT-003 Phase E and SETUP-005 D001–D003. |
| `C15`, `C16`, `W04`, and system-level portions of `W05` | `QUAL-002` | Begins after PORT-008 defines a controlled candidate; gates final assembled-system compatibility claims. |
| `C07`–`C09` | `PORT-003` | Existing Phases D–G, now gated through QUAL-001, PORT-008, and QUAL-002 where applicable. |
| `C10` | `PORT-004` | Logical audio work may precede transport; Agon-fed bench evidence waits for PORT-008. |
| `C11`–`C12` | `PORT-005` and `SETUP-005-D007` | Proof-of-concept host work may proceed; transparent exclusive behavior remains blocked. |
| `C13`–`C14`, `C17`–`C18` | `SETUP-005`, then affected implementation tasks | Remain explicitly blocked until their mode decisions are accepted. |
| `C19` | Deferred Console8 harness task | Do not create until the Light 2 transport and compatibility baseline is stable enough to adapt. |
| `X01`–`X04` | `PORT-006` | Secondary capability evidence; optional Wi-Fi hardware/protocol remains a task-local gate. |
| `X05` | `PORT-007` | Secondary v1 capability after first beta. |
| `X06` | Deferred local-display task | Do not create until MIPI capability and hardware contracts are mature. |

## Review register

### `AUDIT-001-R01` — Qualification-scope separation

- **Status:** Accepted by the Author on 2026-08-22.
- **Decision:** Keep compatibility-critical bench obligations separate from
  secondary Extender product-capability tests. The former governs the claimed
  stock application-facing compatibility surface; the latter qualifies added
  network, browser, wireless, storage, and local-output capabilities without
  obscuring compatibility gates.

### `AUDIT-001-R02` — Missing task ownership

- **Status:** Accepted by the Author on 2026-08-22.
- **Decision:** Transport implementation and assembled-system power/reset
  qualification require explicit TODO task owners; they are not merely missing
  test procedures.
- **Required follow-up:** After AUDIT-001 is accepted, first create those
  follow-on tasks and sequence them in the authoritative TODO where they impose
  the appropriate implementation and qualification gates. QUAL-001, PORT-008,
  and QUAL-002 now provide those accepted owners.

### `AUDIT-001-R03` — Durable disposition of the compatibility matrix

- **Status:** Accepted by the Author on 2026-08-22.
- **Decision:** Promote the compatibility matrix now into permanent,
  role-named infrastructure under `docs/qualification/`. Use authoritative
  machine-readable data derived from the accepted VDU inventory and generate
  human-readable views from it. Do not create a competing hand-maintained
  command list.
- **Purpose:** Let every porting task identify the compatibility obligations it
  satisfies, affects, or leaves blocked, and keep host, target, physical-sink,
  MOS/sysvar, operating-mode, carve-out, and qualification evidence visibly
  connected throughout development and production maintenance.
- **Boundary:** Populate only established facts and accepted decisions. Keep
  unresolved behavior explicitly linked to its owning task rather than
  resolving it speculatively inside the matrix.
- **Owner:** QUAL-001; its formal task plan was accepted on 2026-08-22.

## Completion gate

AUDIT-001 may close when the Author has reviewed the inventory, corrected its
scope, and every accepted gap has either:

1. an owning TODO task and explicit dependency;
2. a recorded deferral with scope and rationale; or
3. an accepted determination that no physical bench test is required.

Closing this audit does not mean the tests have passed. It means every accepted
physical qualification obligation has a visible disposition and owner.

## Completion record

On 2026-08-22 the Author accepted the complete inventory, the separation of
compatibility-critical and secondary qualification, the three-task follow-on
tranche, its sequencing gates, and the explicit Console8 and MIPI deferrals.
QUAL-001 owns the durable matrix, PORT-008 owns both P4 and eZ80/MOS transport
integration, and QUAL-002 owns assembled-system electrical/power/reset
qualification. Existing tasks own their accepted rows as recorded above.

AUDIT-001 is complete because every finding now has an accepted owner, blocker,
or deferral. Completion makes no implementation or qualification claim.
