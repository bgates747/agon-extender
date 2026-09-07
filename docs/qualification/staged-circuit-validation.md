# Staged circuit validation

Present-hardware execution is on hold by Author direction as of 2026-09-07.
The r02 design work and full wiring remain incomplete; the complete circuit
is untested. This reusable process does not lift that task hold.

This document owns the recurring process for constructing and validating the
current Agon Extender circuit incrementally. The Author accepted this process
on 2026-09-05 under PORT-008-D003, refined by PORT-008-D004 to require
checkpoints suitable for powered testing. It governs test scope and evidence; it does
not change electrical connectivity, operating modes, artifact identities, or
the machine-local bench authorization boundary.

## Circuit and construction authority

The current circuit is
[`light2-harness-r02`](../../hardware/designs/light2-harness-r02/README.md).
Its `connectivity.yaml` owns electrical topology; its maintained complete
schematic is the checked human construction drawing. The
[`signal-views/views.yaml`](../../hardware/designs/light2-harness-r02/signal-views/views.yaml)
selects functions for tracing/debugging; its numbered drawings do not define
powerable intermediate assemblies. The separate
[wiring order](../../hardware/designs/light2-harness-r02/wiring-order/README.md)
owns the cumulative construction checkpoints and their test dependencies.
Gray context in a function view is not an instruction to connect a wire.

The operator adds and checks functions in the reviewed wiring order. Each stage retains the
previously installed circuitry unless its approved instructions explicitly
change it. A focused drawing alone does not describe the cumulative as-built
state, prove that a prerequisite is installed, or constitute a test procedure.
The stage record identifies the actual connected terminals, populated parts,
omissions, relevant breadboard/contact mapping, and probes. HW-001 owns that
construction mapping; QUAL-002 owns its electrical evidence. A complete future
assembly drawing is not a prerequisite for a bounded stage whose actual
construction and measurement boundary are recorded adequately.

Each powered checkpoint must account for every powered IC input, shared enable
bank, attached processor pad, omitted lane and reset/idle interval. A source
wire alone does not define a level if its driving pad is undriven. The Author
requires permanent circuit parts only for this sequence. When a missing
prerequisite requires a circuit addition, prepare the exact change and obtain
its approved successor revision before using it; do not disguise it as a
temporary fixture or edit a frozen circuit in place. The ten-input
resistor proposal was rejected by the Author; HW-001-Q011 retains the input-state
question on hold. Reordering drawings alone cannot
resolve that electrical gap.

Predecessor r01 drawings, failures, and fixed-forward procedures remain
historical evidence. Repeating an r01 experiment is not a prerequisite for r02
construction or validation and requires a separately justified task decision.
No result transfers between circuit revisions merely because endpoint pins
match.

## Firmware selected for the measurement

1. Power and passive-bias checks may use a small diagnostic P4 firmware that
   leaves the relevant GPIOs input-only with internal pulls disabled and starts
   no connection-seeking service. Its evidence concerns the measured circuit
   and application behavior only; external circuitry owns safe defaults before
   the application executes. No production transport code is required for a
   measurement that does not exercise transport.
2. Active circuit stages use the applicable production-candidate P4 and EMOS
   components wherever implemented and compatible with the installed subset.
   A small, explicitly identified test caller may supply a documented component
   precondition and observe its result. The record distinguishes the retained
   component from the test caller and lists every omitted product service.
3. If an applicable component is missing or cannot execute on the installed
   subset, the owner task records why a bounded diagnostic stimulus is needed,
   what it proves, and which production-code test remains due. Such a fixture
   may establish circuit behavior but cannot qualify unexecuted product code.
   It must not turn a temporary test wire format into a supported protocol.
4. P4 test firmware initializes only the selected functions and holds all
   other relevant outputs in their reviewed safe state. The stage review
   covers the whole enabled buffer bank and powered IC, including inputs and
   outputs outside the focused view; partial wiring is not permission to leave
   unsafe states uncontrolled or to drive into an unprepared peer.
5. EMOS retains ownership of every eZ80 transport operation. eZ80 applications
   and test clients use EMOS-owned entry points rather than claiming GPIO,
   UART, vectors, routing, or activation independently. Ordinary VDU tests use
   its ordinary dispatcher. A P4 electrical fixture or fixed component caller
   does not establish production activation or a committed operating mode.

## Evidence and release sequencing

Stage evidence and release equivalence are different claims. A stage can prove
a measured circuit function and the behavior of identified candidate code
without a complete production firmware image existing yet.

For each stage, its owner records the selected view and cumulative wiring,
sender and receiver, transport or diagnostic stimulus, safe starting state,
observable expected result, measurement limits, stop/recovery behavior, exact
firmware and procedure identities, and evidence disposition. Before using
candidate-code results, the build record binds the tested image to committed
source, selected configuration and generated inputs, tool versions, actual
build commands, output hashes, and the candidate objects and link contributions
being claimed. Record the evidence method and limits explicitly; a plausible
filename, an unused compilation database, or matching source alone does not
prove which code ran. A bounded review may establish these facts without
completing a general release-pair validator.

Human construction test sheets and their completed results live beside the
owning design, currently in the [r02 test directory](../../hardware/designs/light2-harness-r02/wiring-order/tests/README.md).
Keep the reusable sheet separate from each result. Task documents link to
these records and retain sequencing, unresolved findings, review decisions,
and acceptance. Controlled run manifests and their raw evidence retain the
version policy's repository-root `tests/runs/<RUN-ID>/` location; the
design-side result links to them. Preserve historical observations and their
limitations when relocating them instead of copying a second authority into
the task document.

The existing [versioning policy](../versions/README.md) still governs controlled
artifacts and qualified runs. Exploratory or incomplete records remain
diagnostic evidence. Clean candidate inputs, approved identities, and the
selected procedure are required before a qualified claim. Existing invalid
captures remain invalid; a new process does not repair their provenance.

The exact tested candidate objects are retained for later integration. When
the production release composition exists, its owner verifies consumption of
those objects and the applicable linked-code contract. A changed object,
configuration, or integration context receives an explicit impact assessment
and the relevant repeat tests; it is never silently called identical. Byte
identity supports reuse of component evidence but does not prove that a new
caller, activation path, or complete system behaves correctly.

The task-local release-pair comparator, developed under the former Work 2.e
and now deferred to PORT-008 Work 2.g, remains available for that later claim.
Its unfilled release fingerprints, missing release consumer, and
recorder-specific environment restrictions do not themselves block an earlier
stage using an adequate reviewed evidence method. Its unresolved defects still
block relying on affected reports. No passing equivalence result is fabricated
or required from an incomplete release composition.

## Gates and ownership

HW-001 owns circuit and construction sufficiency; QUAL-002 owns electrical,
power, bias, isolation, and reset observations; PORT-008 owns active transport
components and their eZ80/P4 integration. PORT-003 and PORT-006 become test
dependencies when a stage actually uses the retained parser/display or browser
service. QUAL-001 consumes the exact accepted claims; its unfinished four-mode
matrix does not prevent mode-neutral construction evidence being recorded
beside the design and linked from the owner task.

Each physical step still requires its applicable reviewed procedure and
explicit authorization under `HARDWARE.local.md`. The operator confirms the
installed subset, power sources, attached cables, and final safe state.
The [bench constraints](bench-constraints.md) govern noninteractive eZ80
fixtures. A process amendment does not authorize flashing, wiring, power,
reset, or a new run.

Mode-neutral circuit tests require only their relevant prerequisites. Tests
that exercise or claim activation, mode transitions, Legacy absence, response
ownership, or assembled-system recovery retain the corresponding architecture,
corrective-action, and remediation gates. General Poll remains the first
bidirectional compatibility canary when those paths are ready; it is not a
prerequisite for power, bias, or isolated circuit measurements.
