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
