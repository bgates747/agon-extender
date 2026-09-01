# REMOTE-001 — Develop browser keyboard and remote EMOS control

## State

- Status: Not started — registered from the 2026-08-28 bench-input failure and
  existing remote-access plans
- Started: --
- Finished: --

## Namespace

`REMOTE` identifies remotely originated human or agent interaction with the
Agon, EMOS, onboard VDP, or EDP. It covers user-facing browser input, remote
terminal sessions, privileged command services, authorization, observability,
and the endpoint integrations they require. Physical interprocessor-link
research remains in the `LINK` namespace.

## Prompting need

The current bench Agon's hardware keyboard path is inoperative. BC-001 therefore
requires cold-boot `/autoexec.txt` execution for eZ80 text fixtures until the
Author clears that constraint. Browser keyboard input is a desired product
capability regardless of whether the stock hardware is repaired, but it may
also become the practical fallback for this bench machine.

The broader planned facility should let an explicitly authorized human or
agent interact with EMOS remotely and support a remote-terminal experience.
That work creates a concrete use case for the previously aspirational
bidirectional EDP/onboard-VDP link. SPI is the leading hypothesis, not an
accepted bus or wiring design.

## Actor and ownership boundaries

1. Browser code captures focused keyboard events and presents explicit remote
   session state. It does not invent VDP packets, write MOS state, or execute
   eZ80 commands.
2. EDP/P4 firmware authenticates and bounds the browser session, translates
   browser events into a separately versioned remote-input protocol, and owns
   the EDP endpoint of any selected direct link.
3. Custom onboard-VDP firmware owns the other direct-link endpoint and any
   accepted injection into its existing processed-keyboard/packet path. It
   must distinguish physical-device handling from remote injection internally,
   even if compatibility requires ordinary stock packets toward MOS/EMOS.
4. EMOS remains the sole eZ80 authority for VDU routing, Extender activation,
   canonical MOS state, and privileged remote-command authorization and
   execution. No browser, EDP firmware, onboard-VDP firmware, application, or
   agent receives a supported bypass around EMOS.
5. A remote human or agent requests operations through an explicit opt-in
   service. Possession of network reachability alone must not grant command
   execution authority.
6. PORT-006 owns the network listener, connection lifecycle, generic bounded
   transport, authentication substrate, and exposure policy. REMOTE-001 owns
   keyboard/session semantics and remote-control behavior.
7. PORT-005 owns EDP-local processed-input injection and its effects on EDP
   state. LINK-001 owns research and selection of the physical/protocol
   EDP/onboard-VDP channel. PORT-008's Agon/EDP transport remains a separate
   link and must not be conflated with either one.

## Required outcomes

1. Define browser key-down, key-up, modifier, repeat, focus-loss, layout, and
   disconnect behavior with deterministic mapping to the accepted Agon input
   domain.
2. Deliver remotely injected keyboard events through a bounded path that can
   produce ordinary MOS/EMOS-visible keyboard behavior without competing
   sysvar writers, duplicate packets, stuck keys, or silent unbounded queues.
3. Research and, if accepted, implement a versioned bidirectional
   EDP/onboard-VDP channel. Compare SPI, I2C, UART, and maintained alternatives;
   select no bus before firmware requirements, exposed onboard-VDP pins, P4
   GPIO budget, wiring safety, boot order, reset, and failure behavior are
   reviewed.
4. Preserve normal operation when EDP, the direct link, browser service, custom
   onboard-VDP firmware, or EMOS support is absent, incompatible, starting,
   disconnected, or failed. A stock Agon must not become dependent on Extender
   merely because compatible custom firmware is installed.
5. Define an opt-in EMOS remote-command service with explicit request,
   authorization, execution, result, timeout, cancellation, and audit actors.
   Decide separately whether terminal keystrokes and structured agent commands
   share only transport/session infrastructure or also an application protocol.
6. Provide a human remote-terminal path using the browser's existing video
   presentation plus accepted keyboard input. Define what terminal output is
   framebuffer-only and what, if anything, is exposed as structured text.
7. Provide a bounded automation interface suitable for authorized agents
   without treating arbitrary generated text as trusted operator intent.
   Destructive commands, firmware changes, resets, and mode changes retain
   their existing approval and safety policies.
8. Add deterministic host/emulator tests, endpoint protocol tests, browser
   event tests, malformed/authentication tests, disconnect and stuck-key
   recovery, boot-order tests, and separately approved physical/electrical
   qualification for any new wiring.

## Work

1. Diagnose or bound the current hardware keyboard failure and record whether
   repair, replacement, or browser fallback is the bench strategy. Keep
   BC-001 active until its independent removal condition is met.
2. Freeze separate use cases and actor paths for browser keyboard emulation,
   EDP-local input effects, remote human terminal access, structured agent
   control, diagnostics, and any later bulk or display-state transfer.
3. Execute LINK-001's direct-link research against these concrete use cases.
   If the link is advanced into beta or v1, obtain an explicit architecture
   amendment to the current no-direct-link Rev 1 boundary before reserving
   pins, changing firmware, or designing circuitry.
4. Freeze versioned keyboard-event, direct-link, remote-session, and EMOS
   command/result contracts. Keep those protocol domains distinct even when
   they share a physical link or WebSocket.
5. Implement and qualify the selected EDP and onboard-VDP endpoints in their
   owning repositories, with exact upstream-version provenance and safe
   stock/absent-peer behavior.
6. Implement browser keyboard capture and visible session controls through the
   PORT-006 network boundary. The current HTTP-only trusted-bench service is
   not sufficient authority for unattended or broader remote command access.
7. Implement the EMOS-owned command/terminal service and emulator fixtures
   before granting a network client authority over physical hardware.
8. Produce a new revisioned wiring design from accepted firmware requirements,
   then run approved electrical, protocol, lifecycle, security, and integrated
   qualification. Do not retrofit an undocumented link into the current
   harness.

## Open decisions

1. Is the current keyboard failure repairable, and does browser input remain
   optional or become required for the affected bench machine?
2. Is remote keyboard input a beta requirement, v1 requirement, or later
   capability independent of the bench workaround?
3. Does the direct EDP/onboard-VDP link move into beta or v1, or remain a later
   prerequisite for the remote feature?
4. Which bus, processor roles, pins, voltage-domain protection, connector, and
   flow-control/integrity contract are selected?
5. Does onboard-VDP firmware inject remote keys into the stock processed input
   path, or does EMOS receive a distinct authenticated remote-input service?
6. Are remote terminal keystrokes sufficient for agents, or is a structured
   EMOS command/result API required from the first implementation?
7. What authentication, authorization, session-presence, network-exposure, and
   audit policy is required for humans and agents?
8. Which operations may an unattended agent request, and which still require
   contemporaneous operator approval or physical presence?
9. Does remote terminal output remain video-only, or does EMOS additionally
   expose a structured text stream?

## Dependencies and gates

1. Read the official VDP and MOS input/packet documentation and source before
   freezing event semantics or endpoint insertion points.
2. Reconcile SETUP-005-D007, ADR-0014, REMED-001 input ownership, PORT-005, and
   QUAL-001 before changing the accepted canonical-writer model.
3. LINK-001 must complete the applicable link research before a bus or wiring
   revision is selected.
4. PORT-006 must define authentication and privileged-service exposure before
   browser clients can send EMOS commands outside a tightly controlled bench
   fixture.
5. EMOS source and emulator qualification live in the agon-emos project. This
   task records Extender integration requirements and cross-project evidence;
   it does not move EMOS implementation into this repository.
6. Each firmware, wiring, and physical-run tranche requires its own reviewed
   source boundary, versioned identities, deterministic fixtures, and explicit
   authorization.

## Immediate non-decisions

1. No bus, GPIO assignment, connector, wire protocol, browser command format,
   authentication method, or product-version commitment is selected here.
2. No direct-link or remote-control code is authorized by creating this task.
3. The present workaround remains cold-boot `/autoexec.txt`; REMOTE-001 does
   not gate PORT-008's forward-only visible-command prototype.

## Accepted REMED-002 findings and retained risk

[REMED-002](REMED-002.md) assigns REMOTE-001 the product-semantics portions of
F010 and F019 and retains R003 in this task. Detailed evidence and provenance
remain in
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md).

1. [ ] **F010:** Keep remote use cases, session semantics, authorization, and
   product requirements here. LINK-001 may research candidate direct links but
   owns no firmware, protocol, pins, circuit, or product commitment. If the
   Author accepts implementation, create separately approved endpoint,
   hardware, and qualification tasks before changing artifacts.
2. [ ] **F019:** Preserve authenticated remote-origin provenance until EMOS
   authorizes the requested operation. Do not convert privileged remote intent
   into an indistinguishable ordinary keyboard packet unless the Author first
   accepts a narrowly constrained terminal authority that cannot escape its
   session policy.
3. [ ] Define whether remote terminal input or a structured EMOS operation API
   owns shell commands, reset, flash/update, mode transition, filesystem, and
   other privileged requests; name the authenticating, authorizing, executing,
   observing, and revoking actor for each class.
4. [ ] **R003:** Before enabling browser input or commands beyond the accepted
   trusted bench LAN, consume PORT-006's authentication, Origin, cross-site
   WebSocket, exposure, session-presence, and revocation contract and add
   negative security fixtures.

No link, browser-input path, EMOS service, or network exposure is authorized by
this intake.
