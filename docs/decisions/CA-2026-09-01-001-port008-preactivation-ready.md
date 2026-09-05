# CA-2026-09-01-001 — PORT-008 pre-activation READY_N containment

- Document type: Corrective action
- Status: Open — predecessor retired and replacement data plane integrated;
  production activation correction unresolved
- Date opened: 2026-09-01
- Affected task: PORT-008 prototype tranche
- Affected source baseline: `agon-extender` commit `45c45d5` plus tracked-dirty corrective work
- Authoritative work tracker: `docs/tasks/PORT-008.md`

## Trigger

The third physical PORT-008 attempt again failed while `/autoexec.txt` line 1
explicitly requested `EMOS MODE EXTENDED`. The Author observed that the browser
had not been connected and questioned whether EMOS or EDP firmware had changed
ordinary MOS startup in violation of the safe Legacy-mode contract.

The resulting source-and-capture audit separated three concerns that must not
be conflated: ordinary EMOS startup routing, browser-frame observation, and
P4-side electrical behavior before activation.

## Controlling requirements

ADR-0014 and `docs/architecture.md` require Legacy mode to leave Extender
logically and electrically indistinguishable from absence. Ordinary VDU must
remain routed to the onboard VDP. Project hardware must default every
P4-to-Agon driver disabled, and EDP may expose only a bounded EMOS activation
exchange before a mode commits.

PORT-008 additionally requires the official General Poll to be the first
end-to-end compatibility canary. It forbids a disposable application protocol,
automatic Extender activation at boot, or promotion of the r01 predecessor
wiring into a production safety claim.

## Established findings

### EMOS does not silently reroute ordinary startup

The failed-run EMOS candidate's main path initialized UART0, synchronized with
the onboard VDP, read display state, printed the MOS banner, mounted the SD
card, and set up MOS sysvars before calling `emos_init()`. That initializer
selected Legacy, onboard VDP route zero, and inactive EDU state. It did not call
the predecessor PORT-008 GPIO acquisition routine.

That candidate's semantic VDU dispatcher snapshot route zero and invoked the
retained UART0 path. Only the explicit `EMOS MODE EXTENDED` command reached
`emos_port008_prepare()`. On preparation failure, EMOS restored the saved Port
C and Port D registers and did not publish the new route. The observed line-1
failure was therefore an explicitly requested transition failure, not evidence
that EMOS redirected the preceding stock startup.

### Browser connection is an observation gate only

P4 starts the parallel receiver and retained VDU processor before starting the
wired browser service. The page's Connect action opens a WebSocket and supplies
frame credit. Its absence prevents browser delivery of a visible frame, but it
does not arm parallel ingress and cannot cause the EMOS line-1 transaction to
fail before the fixture executes.

### P4 violates strict pre-activation electrical absence

`ForwardParallelStream` enables the Agon-to-P4 buffer and arms PARLIO during P4
startup. Its receiver task then asserts open-drain `READY_N` immediately rather
than waiting for an EMOS-owned activation request. The third capture records
`READY_N` low for the complete 500 ms window, including time before the explicit
EMOS request.

The P4-to-Agon reverse data driver remained disabled and no direction-enable
overlap occurred. The evidence therefore does not show ordinary VDU hijacking
or push-pull contention. Nevertheless, proactively pulling an Agon-visible
GPIO low means Extender is not electrically indistinguishable from absence in
Legacy mode.

### Defect provenance

The pre-activation behavior was created by EDP/P4 integration; it is not
inherited from official MOS, official Agon VDP, `vdp-gl`, or ESP-IDF, and it is
not an EMOS routing defect.

PORT-008 commit `c03656c87ff10d39d52ba59a9fbbf914a0bb1d73` changed the P4
boot path to call `forwardVDPStream.begin()` unconditionally. The receiver arms
PARLIO and asserts `READY_N` without an EMOS activation request. The then-
uncommitted direction-control correction also selected the forward buffer in
that same boot call, so it did not repair the activation boundary.

Official Agon VDP starts the onboard UART for its one-VDP machine and has no
Extender Legacy-mode contract. The separate predecessor receiver configured
READY released and asserted it only after an operator-triggered diagnostic
command; that diagnostic lifecycle was not a product activation protocol.
Importing either startup assumption into EDP is a local context error.

By contrast, EMOS commit `0e1541c8c96fbd9822bc0866df38eca182fcdbe0`
initializes Legacy, the onboard VDP route, and inactive EDU state. EMOS commit
`08fec4851f8917215a83168ca4e73b54a7d3dcbd` reaches the PORT-008 sender only
through explicit Exclusive Extended preparation and restores the saved eZ80
GPIO state on failure. The verified EMOS Legacy path must remain unchanged
while PORT-008 corrects P4 readiness and direction ownership.

The failed-run `ForwardParallelStream` is bounded predecessor code, not
accepted permanent EDP transport infrastructure. Any promoted transport must put P4
readiness and driver selection behind an accepted EMOS-owned activation
transaction and fail back to electrically absent Legacy state.

### The exact linked sender contains the intended clock writes

The exact 114,085-byte EMOS image has SHA-256
`8f659845c24a9b328f6791a7ac75a2b820df254bc601517d1b2741ed7999987b`.
Its linked disassembly forces PD5/CLOCK high and low state bytes, configures PD5
as output, toggles those states in the READY admission loop, and emits one
falling/rising pair per data byte. The third capture nevertheless sampled no
clock edge.

This proves the instructions exist in the tested image, not that the eZ80 pad
or r01 conductor changed level. The next useful discriminator is physical
observation at both the eZ80 PD5 source and P4 GPIO14 destination during one
attempt.

## Why prior qualification did not prevent this result

Fab does not model the external Port C/Port D circuit, P4 PARLIO, open-drain
READY line, or direction-control hardware. The graphical runtime used the fake
adapter, so it could prove Legacy route selection and transactional mode state
without exercising the physical adapter.

Source and linked-image checks proved instruction shape, record bytes, storage
width, and clock-write order. They cannot prove an eZ80 pad, breadboard node,
series element, P4 header connection, or analyzer probe changed electrical
level. P4-side HTTP readiness likewise says nothing about those nets. Only a
controlled physical observation can close that gap.

The procedure treated HTTP 200 as network-service preflight but did not
separately require the browser WebSocket before visible-frame evidence. That
omission cannot cause the mode failure, but it would have made a successful
transport run visually unobservable.

## Immediate containment

1. Do not flash or perform another powered transfer retry with the predecessor
   proactive-READY behavior. D002 separately authorizes software-only
   replacement work, not deployment or a physical retry.
2. Do not commit or promote the tracked-dirty predecessor corrective
   candidates as a qualified transport implementation. The replacement source
   is now committed, but its recorded builds predate that freeze and it still
   has no release or qualification identity.
3. Treat the exact third-run capture, manifest, diagnostic summary, and linked
   disassembly as failed-run evidence only.
4. Keep ordinary Legacy VDU routing on the onboard UART path; do not undo that
   independently verified EMOS behavior while correcting P4 activation.
5. Keep all replacement-handshake choices and executable work in PORT-008.
   This corrective action records the defect and containment; it does not
   approve a new protocol.
6. Require an explicit browser WebSocket connection before any future run that
   expects visible browser output.

The READY-isolated two-point CLOCK diagnostic was attempted, but its intended
wiring precondition was not established. Its invalid outcome remains
historical evidence; it is not a pending current procedure or a prerequisite
for r02 stage work.

## Design-status update

PORT-008's 2026-09-01 design-only pass found that the accepted r02
Legacy/uncommitted truth-table row releases every Agon-to-P4 forward enable as
well as UART return and READY. EDP therefore has no path on which to hear the
explicit EMOS request required before a P4 response. Proactive READY is not a
solution because it reverses the accepted request ownership.

The Author rejected `PORT-008-D001` on 2026-09-01. EDP/P4 firmware will not
assert a receive-only common-UART forward enable in Legacy, and EMOS will not
gain the proposed dedicated no-CTS bootstrap sender. No ADR, architecture,
hardware-profile, or corrective-action condition is reconciled to that rejected
alternative. The current all-controls-released rule remains binding, and
production activation requires an intended-circuit request path.

The Author separately accepted `PORT-008-D002`'s current-circuit development
boundary. R01 may later exercise new production forward-parallel data-plane
objects through a separately identified fixed-backend qualification
composition. That composition supplies an already-active epoch as a test
precondition; it does not establish Legacy behavior or production activation
and does not close this corrective action. Its source work, artifact identities,
procedure, and physical operation require their own gates. The detailed
boundary is recorded in PORT-008's task-local production-equivalence audit.

## Production-replacement update

Later Author-authorized PORT-008 Work 2 retired the rejected
`extender-vdp-v0.2.0`/`p4-forward-vdp` composition and the predecessor EMOS
sender/profile from maintained selection; both remain historical evidence.
The replacement ordinary dispatcher now reaches a common production parallel
route, and the separately identified fixed composition supplies only the
procedural precondition that its operator or top level has already prepared an
active peer epoch. The replacement P4 data-plane owner asserts readiness only
inside that supplied epoch; neither side implements or claims the production
activation request.

This replacement removes the predecessor behavior from the software
composition under test but does not close this corrective action. The accepted
production activation carrier, fail-closed Legacy transition, response path,
controlled physical evidence, and General Poll completion required below all
remain open.

## Resolution conditions

**Stage boundary, 2026-09-05:** Accepted PORT-008-D003 makes r02's ordered
circuit subsets the current construction/test path. Power/bias checks and
reviewed component fixtures that do not exercise the retired proactive-READY
behavior may be prepared independently of production activation. Each physical
stage needs its applicable authorization under the
[staged process](../qualification/staged-circuit-validation.md). Such evidence
does not establish Legacy absence, authorize a supported EMOS bypass, or close
this corrective action. Its full resolution conditions below remain intact.

This corrective action may close only after the Author approves a bounded
activation design, deterministic checks prove its fail-closed Legacy and
transition behavior, a controlled physical run proves every P4-to-Agon signal
released before explicit activation, and the official General Poll completes
without an unexplained clock or READY gap. Commit approval remains a separate
Author gate.

“Every P4-to-Agon signal” includes all four P4/U4-originated Agon-domain control
sinks—`UART_FWD_OE_N`, `PAR_FWD_OE_N`, `UART_RETURN_OE_N`, and `READY_N`—plus
the P4 UART TX/RTS return drivers. Because D001 is rejected, no Dormant-listen
exception exists. A fixed-backend data-plane run may provide bounded component
evidence under a separately approved qualification claim, but cannot satisfy
or weaken this production-activation resolution condition.
