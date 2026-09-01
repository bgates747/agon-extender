# CA-2026-09-01-001 — PORT-008 pre-activation READY_N containment

- Document type: Corrective action
- Status: Open — defect contained; correction not yet authorized
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

The current EMOS main path initializes UART0, synchronizes with the onboard
VDP, reads display state, prints the MOS banner, mounts the SD card, and sets up
MOS sysvars before calling `emos_init()`. That initializer selects Legacy,
onboard VDP route zero, and inactive EDU state. It does not call the PORT-008
GPIO acquisition routine.

The semantic VDU dispatcher snapshots route zero and invokes the retained
UART0 path. Only the explicit `EMOS MODE EXTENDED` command reaches
`emos_port008_prepare()`. If preparation fails, EMOS restores the saved Port C
and Port D registers and does not publish the new route. The observed line-1
failure is therefore an explicitly requested transition failure, not evidence
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
PARLIO and asserts `READY_N` without an EMOS activation request. The current
uncommitted direction-control correction also selects the forward buffer in
that same boot call, so it does not repair the activation boundary.

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

The current `ForwardParallelStream` is bounded prototype code, not accepted
permanent EDP transport infrastructure. Any promoted transport must put P4
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

1. Do not perform another PORT-008 firmware change, flash, or powered transfer
   retry under the current proactive-READY behavior.
2. Do not commit or promote the tracked-dirty corrective candidates as a
   qualified transport implementation.
3. Treat the exact third-run capture, manifest, diagnostic summary, and linked
   disassembly as failed-run evidence only.
4. Keep ordinary Legacy VDU routing on the onboard UART path; do not undo that
   independently verified EMOS behavior while correcting P4 activation.
5. Keep all replacement-handshake choices and executable work in PORT-008.
   This corrective action records the defect and containment; it does not
   approve a new protocol.
6. Require an explicit browser WebSocket connection before any future run that
   expects visible browser output.

The task now contains a proposed READY-isolated, two-point CLOCK diagnostic.
It is review material only and does not relax containment or authorize a
physical change.

## Resolution conditions

This corrective action may close only after the Author approves a bounded
activation design, deterministic checks prove its fail-closed Legacy and
transition behavior, a controlled physical run proves every P4-to-Agon signal
released before explicit activation, and the official General Poll completes
without an unexplained clock or READY gap. Commit approval remains a separate
Author gate.
