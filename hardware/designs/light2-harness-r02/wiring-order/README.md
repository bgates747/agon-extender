# Light 2 harness r02 powered construction order

**On hold — incomplete (Author direction, 2026-09-07).** The present
hardware design, construction, and testing are paused pending review of stock
MOS/VDP communications and interface requirements. Full wiring of the r02
circuit as drawn is incomplete, and the complete circuit has not been tested.
The September 4 power-domain observations retain only their recorded scope.
The frozen candidate identity preserves the design checkpoint; it does not
claim design completion, complete assembly, or qualification. Earlier stage
instructions below are retained references and do not authorize further work.

**Current scope (2026-09-07): connection identification only.** The
[connection ledger](connections.md) assigns stable IDs to the unchanged r02
circuit; [connections.csv](connections.csv) provides the same inventory for
machine use. The Author will discuss discrete wiring steps separately.
The earlier draft below is superseded as construction guidance: the Author
rejected adding resistors solely to enable intermediate powered tests.
Its proposed R32–R41 additions and stage assignments are not adopted by the
ledger. No replacement sequence is defined in this change.

This directory plans the smallest useful additions to a partially built
assembly based on r02 that can each be followed by a powered check. It owns construction
sequencing and the associated [test sheets and results](tests/README.md).
The Author requested this separation on 2026-09-05 under PORT-008-D004.

**Plan status: DRAFT.** The process and document location are accepted; the
proposed permanent input bias, new test callers, probe configurations, and
individual physical procedures still need their applicable review. Stage
numbers are document positions, not approved artifact revisions or run IDs.
No new hardware or procedure identity is assigned here.

## Three different views of the same circuit

1. [`connectivity.yaml`](../connectivity.yaml) defines the r02 circuit.
2. [`signal-views/`](../signal-views/README.md) isolates functions for tracing
   and debugging. Its existing numbers and drawings remain stable reference
   names; their order is not a powered construction procedure.
3. This directory defines cumulative construction checkpoints, including
   supporting connections outside the function being tested, safe input and
   enable states, the actual stimulus owner, and measurement points. The
   [sequence manifest](sequence.yaml) lists each permanent electrical addition
   and the proposed permanent bias additions. It does not redefine r02 nets.

The drawing geometry remains in the maintained schematic and function views.
The numbered documents here add explicit endpoint instructions and test
boundaries; they are not newly generated KiCad drawings. Use both the cited
function drawing and the step's additional-connection table when wiring.

## Construction sequence

| Step | Smallest new addition or test checkpoint | Powered observation |
| --- | --- | --- |
| [01](01-power-foundation.md) | Rails, common ground, bypass and bulk capacitors; ICs absent for a fresh build | Both rails and either-domain isolation |
| [02](02-startup-and-fail-safe-bias-network.md) | Existing bias view plus defined levels at all ten U1/U2 data inputs; populate all four ICs | Settled rails, all bias nodes and released enables; optional digital startup capture |
| [03](03-onward-circuit-steps.md#03--enable-bank-checkpoint) | Test the already wired enable banks before attaching transport outputs | Control/OE correspondence and exclusion; no permanent wire added |
| [04](03-onward-circuit-steps.md#04--d0--uart-forward-data) | D0 source and buffered output | eZ80 source versus P4 GPIO22 |
| [05](03-onward-circuit-steps.md#05--d2--uart-forward-flow-control) | D2 source and buffered output | eZ80 RTS source versus P4 GPIO23 |
| [06](03-onward-circuit-steps.md#06--uart-return-data) | P4 TX through U3/R11 to Agon PC1 and U1's input tap | GPIO12 versus Agon RX; parallel output remains absent |
| [07](03-onward-circuit-steps.md#07--uart-return-flow-control-and-four-wire-uart) | P4 RTS through U3/R12 to Agon PC3 and U1's input tap | GPIO11 versus Agon CTS; first complete four-wire UART test |
| [08](03-onward-circuit-steps.md#08--ready-return) | Complete U4/R13 READY sink path | P4 ready control versus Agon PD4; release/assert/readback |
| [09](03-onward-circuit-steps.md#09--parallel-d1-output) | U1/R2 parallel D1 output | Agon PC1 versus GPIO12 after UART outputs are released |
| [10](03-onward-circuit-steps.md#10--parallel-d3-output) | U1/R4 parallel D3 output | Agon PC3 versus GPIO11 after UART outputs are released |
| [11](03-onward-circuit-steps.md#11--parallel-d4) | D4 source and buffered output | Agon PC4 versus GPIO32 |
| [12](03-onward-circuit-steps.md#12--parallel-d5) | D5 source and buffered output | Agon PC5 versus GPIO10 |
| [13](03-onward-circuit-steps.md#13--parallel-d6) | D6 source and buffered output | Agon PC6 versus GPIO33 |
| [14](03-onward-circuit-steps.md#14--parallel-d7) | D7 source and buffered output | Agon PC7 versus GPIO9 |
| [15](03-onward-circuit-steps.md#15--clock) | CLOCK source and buffered output | Agon PD5 versus GPIO14 |
| [16](03-onward-circuit-steps.md#16--valid_n) | VALID_N source and buffered output | Agon PD7 versus GPIO13; completes permanent transport wiring |
| [17](03-onward-circuit-steps.md#17--complete-candidate-parallel-records) | Integrate the complete candidate parallel engine on the checked wiring | Actual READY-paced records, byte comparison, bounded stop/recovery |

Every wire is added unpowered. Each row starts from the previous accepted
cumulative assembly. A new transport lane normally needs its source connection
and its buffered output connection together; splitting that pair would yield
an incomplete path rather than an additional source-to-destination test.
Steps 03 and 17 are explicit test checkpoints with no new permanent wire.

The principal change from the function-view order is that input preparation
comes before powered IC testing, UART-return and parallel-output halves of D1
and D3 are separated, and READY is completed before parallel-record testing.
All spare inputs and both channels of a shared enable group remain controlled
while a single lane is exercised.

## Starting from the current breadboard

The Author reports all ten listed U1/U2 input pins are presently unwired.
The four ICs were already present during the earlier power-domain observations.
Continue unpowered into step 02's preparation; do not remove working wiring
just to replay the fresh-build step 01. Repeat the rail measurements at the
end of step 02. The September 4 results retain their actual older boundary.

The Author requires permanent circuit parts only. Step 02 therefore proposes
ten permanent 10 kohm Agon-side bias resistors. They are **not in frozen r02**;
HW-001-Q011 owns approval of the addition and successor revision. Until that
circuit change is accepted and its authorities updated, the powered sequence
from step 02 onward is a conditional plan, not an executable r02 procedure.
The folder remains under r02 to keep this review beside its design basis.

Adding the ten eZ80 wires early would not by itself define undriven inputs.
The proposed resistors remain in the finished circuit; there are no temporary
parts or cleanup/removal stage. Their loading must be reviewed and tested.
Defined idle bias addresses this input-state gap, but does not settle the
broader Legacy electrical-absence or activation-path decisions.

## Firmware and evidence

[Test methods](test-methods.md) define stimulus ownership, shared-pin states,
candidate-code availability, and bounded logic-analyzer maps. Each later step
names the method it needs. A planned method is not a built or deployed image.
Prepare only the next needed caller under PORT-008; do not resume the deferred
release-comparison tooling as a prerequisite for these circuit checks.

Keep human results under [tests/](tests/README.md), with exact cumulative
wiring, approved circuit revision, firmware and probes. Controlled raw evidence
and run manifests retain the repository-root `tests/runs/<RUN-ID>/` location.
The [staged process](../../../../docs/qualification/staged-circuit-validation.md),
[version policy](../../../../docs/versions/README.md), and ignored root
`HARDWARE.local.md` govern review, identities and physical execution.
