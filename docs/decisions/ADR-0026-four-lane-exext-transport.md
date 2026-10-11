# ADR-0026 — Eight-bit ExExt payload with existing-wire handshaking

- Status: Accepted
- Completeness: Partial
- Date: 2026-10-08
- Related task: PORT-008
- Open-decision tracker: PORT-008

## Decision

The Author's target is bidirectional eight-bit parallel payload using PC0–PC7
in ExExt. The existing P4-PC READY/CLOCK/VALID connections carry control;
PC4–PC7 remain data lanes. Local RAM records each processor's state; the
agreed state must be communicated over actual wires. No additional wiring
is selected; electrical feasibility remains unqualified.

EMOS owns admission, initiation, eZ80 GPIO/flow control and UART handover. P4
firmware owns its peripheral, buffers and counterpart handshake. UART is
unavailable on the shared pins during the eight-bit payload phase and resumes
after coordinated handback. Legacy and ExCom gain no parallel traffic.

This record corrects the agent's initial interpretation that the four spare
lanes would carry payload while UART remained permanently active. That narrower
SPI payload proposal was not the Author's intent. The filename is retained for
link continuity. Eight-bit byte timing and recovery remain under PORT-008;
accepting the goal does not establish that it works without further signals.

## Wiring clarification

The Author confirms following the P4-PC migration specification. That drawing
already allocates PD4 READY_N, PD5 CLOCK and PD7 VALID_N alongside PC0–PC7.
The historical DevKit r03 disconnected-line state is not the PC arrangement.
The spare-lane handshake idea is therefore an investigated option, not a
requirement to replace existing dedicated signals with pseudo-SPI. PORT-008
uses the complete mapping for authorized bench-free development. EMOS owns
CLOCK and VALID in both directions; P4 owns READY. PC4–PC7 need not carry a
separate setup protocol. The eight-bit payload target remains; no physical
qualification is implied by selecting these existing conductors.

## Rationale and consequences

Handshake overhead can be amortized across a bounded block. Preserving payload
width is the objective; reusing existing wires for handshake is the proposed
way to avoid additional construction. A pre-transfer handshake does not itself
provide per-byte timing. Both transfer directions, sampling and UART/input
recovery require a concrete design and measurement before implementation.

[PORT-008](../tasks/PORT-008.md) owns that work. The old forward-only buffered
circuit remains held evidence, not a qualified implementation of this design.

## Reset and absent-peer policy

For the future parallel-capable pair, EMOS must keep PC0–PC7 released after
reset until P4 explicitly acknowledges release using READY/CLOCK/VALID. A timer
cannot establish that P4 stopped driving. If P4 is absent or runs older firmware
without this handshake, Extender input/output remains unavailable; MOS and the
mainboard keyboard remain usable. There is no timed UART ownership fallback.
Each reset invalidates the prior block admission. This accepted policy governs
the candidate implementation, not the current UART-only production image.

## ExExt CRC policy — 2026-10-11 amendment

EMOS and P4 EDP must not compute or require CRC for the ExExt transport,
including its control exchanges. The Author rejects accelerating the candidate's
repeated CRC checks and requires removing that work instead. No alternative
per-block checksum is selected. Physical direction ownership and reciprocal
handshakes remain required; transport CRC is not their substitute.

The CRC-bearing candidate measured by PORT-008 remains historical evidence,
not this accepted final design. Qualification may independently compare payload
bytes outside measured intervals. This amendment changes no deployed image or
unrelated SD verification contract. PORT-008 P08-D02 owns the remaining paired
wire-format/version decision and implementation boundary.

## Stock behavior; transport-only first pass — 2026-10-11 amendment

The Author requires EMOS and P4 EDP to preserve stock MOS/VDP behavior above
the byte-transport boundary. The first pass changes which wires carry the
ordered command and return streams. Application APIs, VDU bytes and reply
formats, parsing, callbacks, sysvars and interrupt semantics remain stock;
reuse upstream code wherever processor differences permit. Physical transfer
timing can differ without authorizing higher-level behavioral changes.

EMOS and EDP may add only the operations necessary for physical ownership,
byte delivery and the replacement peripheral. Reciprocal release/direction
and byte-sampling handshakes are required by the shared wiring. Each further
addition must have a specific physical-link justification. Existing block
offers, completion messages, return polls, sessions and buffering are candidate
implementation choices, not accepted requirements merely because code exists.
The no-CRC decision above remains binding. This amendment concerns the ExExt
transport pass; it does not reopen rendering, output-device or unrelated service
design. PORT-008 P08-P05/D02/D03 own the bounded implementation review; deployed
behavior and qualification remain unchanged.

## First CRC-removal implementation cut — 2026-10-11 amendment

Under the Author-authorized first code cut, EMOS and P4 use the existing parallel
wire discriminator value3 for the CRC-free experimental pair. They retain the
sixteen-byte carrier initially; bytes14–15 are transmitted zero and ignored on
receipt. Format2 cannot grant parallel admission. Ordinary version1 console
activation remains unchanged. This is a bounded implementation transition, not
a permanent requirement for the final minimum control carrier. It changes no
installed image or production selection. The linked PORT-008 task retains the
remaining design questions and deployment gates.
