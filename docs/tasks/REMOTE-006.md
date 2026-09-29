# REMOTE-006 — Independent browser-requested Extender reset

## Executive summary

Add a distinct **Reset Extender** button beside the existing **Reset Agon**
button in the browser header. The two controls remain independent because the
Extender P4 and Agon mainboard/onboard VDP can fail independently and an
operator may deliberately reset only one side. No combined reset, automatic
fallback from one reset to the other, or reset-on-reconnect is permitted.

The task must distinguish two Extender failure classes before selecting the
reset executor. A native P4 `esp_restart` endpoint can restart responsive
firmware while its HTTP server still runs, but cannot recover a completely hung
P4. An external actor, presently the bench Pi through the P4's verified USB or
a separately qualified reset actuator, can recover a broader failure. The
browser action must state which class it supports; it must not present a
self-reset endpoint as recovery from an unavailable network processor.

Created: 2026-09-29. Owning queue: `TODO.md`. Related authorities:
[REMOTE-003](REMOTE-003.md), [REMOTE-001](REMOTE-001.md),
[bench reset](../bench-reset.md), [remote keyboard](../remote-keyboard.md),
[architecture](../architecture.md) and [AUDIT-010](AUDIT-010.md).

## State and authorization

R06-S01 — Task contract drafted at the Author's request. No UI, bridge,
firmware, wiring, production package or maintained operating guide has been
changed by this draft.

R06-S02 — The Author's separately requested one-time USB reset of the currently
unresponsive Extender is an operator recovery action, not implementation or
qualification of REMOTE-006. Record its exact target identity and result in the
development log without treating it as browser-button evidence.

R06-S03 — Implementation waits behind the active AUDIT-010 review/repair gate
unless the Author explicitly reprioritizes it. Contract review does not
authorize a firmware build, browser deployment, P4 reset, Agon reset, wiring
change or production promotion.

## Required behavior

R06-B01 [ ] Place **Reset Extender** immediately beside **Reset Agon** in the
browser header. Preserve two separately focusable buttons, explicit accessible
labels and independent enabled/disabled states. Do not add a combined “reset
all” action.

R06-B02 [ ] **Reset Agon** retains its accepted REMOTE-003 behavior: the browser
requests the Pi bridge's fixed mainboard reset action; the Pi pulses the
mainboard actuator; the P4 remains running. REMOTE-006 must not silently change
that endpoint, pulse, request header, confirmation, evidence or failure text.

R06-B03 [ ] **Reset Extender** resets only the P4 and does not pulse the Agon
RST/EN net, restart the eZ80, reset the onboard VDP or power-cycle either board.
The action invalidates P4 video, browser-input, agent-input, network-service and
file-service sessions. No pre-reset input or mutation request is replayed.

R06-B04 [ ] Use target-specific confirmation text. The Extender confirmation
must say that browser video/input and P4-hosted file/network work will be
interrupted while the Agon continues running. The Agon confirmation must retain
its existing running-program warning. Cancel performs no request.

R06-B05 [ ] The browser releases its P4 keyboard capture before requesting an
Extender reset, closes or abandons stale P4 sessions, and requires fresh
connection/capture after a new P4 boot epoch. It does not interpret a dropped
HTTP/WebSocket connection as successful reset and never retries an uncertain
request automatically.

R06-B06 [ ] Keep request identities and actions separate. An Agon reset UUID
cannot suppress, acknowledge or trigger an Extender reset, and vice versa.
Concurrent or duplicate requests receive target-specific results. A fixed
bridge command accepts no browser-supplied executable or arguments.

R06-B07 [ ] Report executor acceptance/release separately from observed P4
boot, Ethernet readiness, browser reconnection, EMOS rediscovery and display
recovery. Silent ordinary success may be retained only if the UI still makes
an uncertain or failed request explicit and the selected executor can truthfully
complete its response.

R06-B08 [ ] Preserve open-file and mutation uncertainty. If the responsive P4
can identify an active WebDAV, P4-SD, mainboard-SD or firmware operation, the
selected policy must either refuse reset or require a stronger explicit
confirmation. A hard external reset cannot promise orderly cleanup; maintained
guidance must tell the operator to reconcile journals/staged files afterward.

R06-B09 [ ] Define Legacy and ExCom outcomes independently. In Legacy, the Agon
and onboard VDP continue without an implied mainboard reset. In ExCom, P4 reset
can remove the selected display/input peer while EMOS remains alive; the task
must specify the visible failure, fresh peer epoch, route recovery and any
operator action. It must not restore service by secretly resetting Agon.

## Architecture boundary

| Route ID | Browser request → executor → target | Recoverable failure class | Boundary and current assessment |
|---|---|---|---|
| `R06-R01` | Browser → responsive P4 HTTP control → `esp_restart` → P4 | Application/service remains responsive enough to accept and schedule restart | Smallest firmware-only change, but cannot recover a hard hang or dead network. Response delivery and delayed restart ordering must be proven. Insufficient alone for the motivating worst case. |
| `R06-R02` | Browser → Pi fixed-action bridge → verified P4 USB reset operation → P4 | P4 application/network hung while Pi, USB and reset mechanism remain available | Recommended first recovery candidate because the executor is independent of P4 application state and the existing browser reset already uses the Pi trust boundary. Exact USB reset semantics, stable identity, no-flash command and boot result must be qualified. |
| `R06-R03` | Browser → Pi fixed-action bridge → dedicated isolated P4 reset actuator → P4 | P4 and USB control path unavailable while Pi and actuator remain available | Strong independent reset, but current Pi-to-P4 `ESP_EN` arrangement is legacy evidence rather than a qualified installed circuit. Requires electrical/as-built work under a separate approved hardware procedure. |
| `R06-R04` | Browser → another P4/mainboard command path → target | Depends on the actor being responsive | Reject as the sole recovery route when it depends on the crashed P4, responsive EMOS or a combined-board reset. |

The browser may ultimately expose one Reset Extender button backed by one
selected route. If both native graceful restart and external hard reset are
retained, their escalation policy must be explicit and must never retry or
escalate automatically after an uncertain result.

## Decision register

| Decision ID | State | Decision and consequence |
|---|---|---|
| `R06-D01` | Accepted by Author 2026-09-29 | Add Reset Extender beside Reset Agon. |
| `R06-D02` | Accepted by Author 2026-09-29 | Keep Agon reset and Extender reset as independent options; neither invokes the other. |
| `R06-D03` | Proposed | Use the independent Pi→verified-P4-USB route as the first implementation candidate. A native P4 self-restart may be supplementary but does not satisfy hard-hang recovery. |
| `R06-D04` | Open | Select and qualify the exact no-flash USB reset operation, or reject it and scope a dedicated isolated actuator. Opening a serial port is not automatically accepted reset semantics merely because prior observations coincided with reboot. |
| `R06-D05` | Proposed | Reuse the current trusted-LAN bridge policy—exact allowed Origin, explicit POST, target-specific header, bounded JSON UUID, concurrency rejection and bounded duplicate history—while assigning a distinct action and endpoint. |
| `R06-D06` | Open | Decide responsive-busy policy for active P4/mainboard storage operations and wording for hard-reset uncertainty. |
| `R06-D07` | Open | Define EMOS behavior after independent P4 reset in Legacy and ExCom, including fresh boot/admission identity and route recovery without an Agon reset. |
| `R06-D08` | Proposed | Keep both reset controls outside element fullscreen, adjacent in the header; do not place destructive actions in the bottom fullscreen interaction strip. |
| `R06-D09` | Open | Decide whether successful external reset remains visually silent like Reset Agon or shows transient “Extender restarting”; failures and uncertain outcomes must remain explicit either way. |

Present open decisions one at a time with a recommendation before freezing the
implementation contract.

## Work items

R06-01 [ ] Establish the reset contract and exact actors.

R06-01a [ ] Verify official ESP-IDF restart behavior and the Olimex P4 board's
USB/reset topology from current primary documentation. Distinguish software
restart, USB Serial/JTAG reset behavior, EN/reset assertion and power cycling.

R06-01b [ ] Inspect the maintained Pi/P4 tooling and current as-built bench
record. Select only a stable-identity, no-flash operation that cannot target a
first-match serial device. Keep all machine-specific endpoint, account and
device values in ignored local records.

R06-01c [ ] Trace P4-reset consequences through EMOS route/input ownership,
browser generations, HTTP/WebSocket sessions, P4/mainboard SD transactions and
the maintained boot epoch. Record what the mainboard observes in Legacy and
ExCom when P4 disappears and returns.

R06-02 [ ] Freeze the reviewed architecture decision.

R06-02a [ ] Resolve `R06-D03` through `R06-D09` one at a time with the Author.

R06-02b [ ] Update or create the applicable ADR and normative architecture only
after the Author accepts the executor, trust boundary, session invalidation and
recovery contract. Open questions remain here, not in the ADR.

R06-03 [ ] Implement the selected reset executor and fixed-action control.

R06-03a [ ] If the Pi bridge is selected, add a separately configured Extender
action without weakening or overloading the existing Agon action. Resolve the
P4 by its stable USB identity immediately before reset; reject absent, ambiguous
or wrong identity. Execute no erase, flash or arbitrary shell request.

R06-03b [ ] If native restart is retained, register a bounded authenticated-by-
policy control route, send/queue a truthful acceptance response, perform restart
outside the HTTP callback, and prove the action runs at most once. Do not claim
hard-hang recovery.

R06-03c [ ] Ensure every normal/error path leaves the Agon reset actuator and
mainboard state untouched. Preserve the independent physical Reset Agon button
and Pi bridge rollback.

R06-04 [ ] Add the independent browser control.

R06-04a [ ] Add a second deployment-owned endpoint marker/configuration without
putting private URLs in tracked assets. Each button is disabled only when its
own executor is unconfigured.

R06-04b [ ] Add Reset Extender adjacent to Reset Agon with target-specific
confirmation, keyboard/session release, UUID namespace, request header, timeout
and uncertain-result handling. Do not infer reset success from connection loss.

R06-04c [ ] Preserve current video, fullscreen, keyboard, accessibility and
Reset Agon behavior. A CSS/layout change must not move either destructive action
into ordinary connect/capture controls.

R06-05 [ ] Complete host and browser validation before hardware work.

R06-05a [ ] Bridge/unit tests cover wrong method/path/origin/header, malformed or
oversized body, duplicate UUID, concurrent request, command timeout, target
identity failure and exact once-only target action. An Extender request must not
increment the mocked Agon actuator and an Agon request must not invoke the P4
reset command.

R06-05b [ ] Browser tests cover adjacent controls, independent configuration,
cancel, separate confirmation text, per-target headers/UUIDs, input release,
timeout, uncertain response, no retry, accessibility and unchanged fullscreen
layout.

R06-05c [ ] Build/asset tests verify the tracked empty endpoint markers,
deployment substitution, linked bytes and absence of machine-private values.

R06-06 [ ] Prepare and obtain authorization for bounded physical qualification.

R06-06a [ ] Follow `HARDWARE.local.md` and bench constraints. Verify the P4's
stable USB identity before every mutation. Preserve exact firmware identity,
capture reset executor receipt and new boot identity, and do not flash merely to
test reset.

R06-06b [ ] Demonstrate Extender-only reset in Legacy: the P4 restarts; Agon/eZ80
and onboard VDP do not reboot; P4 network/video/input return under the accepted
fresh-session contract.

R06-06c [ ] Demonstrate the accepted ExCom failure/recovery contract without an
implicit Agon reset. Separately verify Reset Agon still leaves the P4 running.

R06-06d [ ] Exercise idle, active browser video/input and the accepted
storage-busy/refusal or uncertainty cases. Never reset during flash or ROM
recovery. Use durable unattended status and the accepted audible completion/
failure cue where automation is approved.

R06-07 [ ] Close out accepted behavior.

R06-07a [ ] Update the browser/reset/build/install/using guides so operators can
distinguish the two targets, executors, limitations and post-reset recovery.

R06-07b [ ] Preserve exact accepted bytes and evidence, then follow the normal
production bundle/version/tag policy. Agree the production version with the
Author before promotion.

## Validation gates

R06-G01 [ ] The browser visibly offers two adjacent, independently enabled reset
controls and no combined reset action.

R06-G02 [ ] Every request has one named browser, executor and reset target;
duplicate/uncertain requests never become automatic second resets.

R06-G03 [ ] Reset Extender demonstrably leaves the Agon/eZ80 and onboard VDP
running in the qualified Legacy case; Reset Agon demonstrably leaves P4 running.

R06-G04 [ ] The selected route's recovery claim matches evidence: responsive
self-restart is not called hard-hang recovery, and external reset is not called
successful merely because its command was accepted.

R06-G05 [ ] Legacy and ExCom post-P4-reset outcomes are documented and bounded;
no stale keyboard, video, storage or admission session is replayed.

R06-G06 [ ] Existing Reset Agon behavior, browser video/input, fullscreen and
maintained build/asset checks pass unchanged.

R06-G07 [ ] No tracked source, manifest, receipt or task record contains private
bench endpoints, credentials or unique machine configuration.

## Safety and non-goals

R06-N01 — This task does not add a combined-board reset, power-cycle control,
watchdog policy, firmware flashing endpoint, factory reset or automatic crash
detection/restart.

R06-N02 — Do not reuse the Agon reset endpoint/header for Extender reset, connect
Pi and P4 push-pull reset drivers together, or infer current P4 reset wiring from
legacy evidence.

R06-N03 — A browser page served only by the crashed P4 cannot originate a new
request after reload. External recovery assumes the already-loaded page or a
separately reachable control origin remains available; document this usability
limit rather than hiding it.

R06-N04 — Reset interrupts volatile work. No successful reset receipt proves
that in-flight SD/FatFS mutations are complete, that EMOS has rediscovered P4,
or that the browser has re-established a fresh session.
