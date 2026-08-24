# LINK-001 — Research a direct onboard-VDP/EDP high-speed link

## State

- Status: Not started — post-v1 aspiration; no product guarantee
- Started: --
- Finished: --

## Namespace

`LINK` identifies work whose primary subject is a direct communication link
between independently owned processors or subsystems, including its use cases,
protocol, firmware endpoints, physical signals, lifecycle, and qualification.
Scheduling and product-version scope remain separate from the namespace.

## Prompting discussion

This task was created from
[`REMED-001` Work 2.c, `W2C-Q04`](REMED-001/exclusive-routing-analysis.md#w2c-q04--controlled-onboard-vdp-side-channel).
That decision makes MOS/eZ80 the sole Rev 1 intermediary for messages between
the onboard VDP and EDP. Rev 1 contains no direct VDP-to-EDP communication link.

The Author identified a possible later bidirectional high-speed link—probably
SPI—as a v2 aspiration. Neither the feature nor SPI is presently selected or
guaranteed.

One explicit v2 aspirational use case is direct transfer of compatible display
state and buffers between onboard VDP and EDP during a state-preserving mode
transition. This transfer is not a v1 feature. If the post-v1 link proceeds,
such transfer is a minimum design goal. The exact transferable state,
representation, protocol, and continuity guarantee remain unselected and must
not be inferred from this aspiration.

## Intent

Determine whether a direct high-speed onboard-VDP/EDP link would provide enough
post-v1 value to justify custom firmware on both processors, additional pins and
circuitry, a new protocol, lifecycle coupling, failure modes, and qualification.
If justified, design it without weakening the MOS/eZ80 ownership contracts or
making the stock machine dependent on Extender.

## Research work

1. Inventory concrete use cases that cannot be handled adequately through the
   Rev 1 MOS/eZ80 relay, including input events, delegated audio, display
   coordination, state synchronization, firmware management, diagnostics, and
   bulk data.
   Treat direct transfer of compatible VDP/EDP state and buffers for
   state-preserving mode transitions as the minimum aspirational use case.
2. Measure or bound the latency, throughput, CPU cost, buffering, and failure
   behavior of the Rev 1 relay before assuming a direct link is necessary.
3. Determine what cooperating onboard-VDP firmware changes each use case would
   require and how a stock or failed onboard VDP behaves when the link is
   absent.
4. Compare SPI, I2C, UART, and any maintained ESP32 interprocessor alternatives
   for full-duplex needs, bandwidth, GPIO consumption, electrical complexity,
   peripheral availability, isolation, debugging, and recovery.
5. Treat SPI as the leading hypothesis only. Select no bus until pin budgets,
   board revisions, mode requirements, and measured use cases support it.
6. Review whether MOS Modules or another later cooperative MOS architecture
   removes, changes, or strengthens the need for direct processor communication.
7. Determine whether the link belongs on every carrier, an optional add-on, or
   no supported product at all.

## Architecture work if justified

1. Define processor roles, ownership, discovery, capability and version
   negotiation, framing, integrity, flow control, backpressure, and reset.
2. Keep direct-link messages in a distinct versioned protocol domain. Do not
   impersonate ordinary VDU, stock VDP packets, EDU results, or MOS sysvar
   writes.
3. Define which processor may initiate each operation and which component
   remains the canonical owner of every affected state item.
4. Define boot-order independence, missing/stock/failed firmware behavior,
   timeout, recovery, fallback, and safe disablement.
5. Define security and authorization for firmware-management or privileged
   operations.
6. Produce a new revisioned hardware design from firmware requirements; infer
   no pins, wires, or components from the Rev 1 harness.
7. Produce deterministic endpoint tests, protocol conformance tests, electrical
   safety qualification, logic-analyzer procedures, throughput/latency tests,
   fault injection, and complete mode interaction coverage.

## Rev 1 exclusion

- Rev 1 has no direct electrical or protocol connection between onboard VDP and
  EDP.
- MOS/eZ80 software relays every accepted message between them.
- No Rev 1 input, audio, RTC, mode, maintenance, update, or compatibility
  requirement may depend on a direct link.
- No current firmware or hardware task may reserve pins, add framing, or alter
  stock onboard-VDP firmware on the assumption that LINK-001 will be accepted.
- Absence of the future link is normal, not a degraded Rev 1 condition.

## Dependencies and gates

- Complete and qualify the Rev 1 MOS/eZ80 relay before evaluating its measured
  limitations.
- Revisit current upstream onboard-VDP firmware, P4 capabilities, carrier pin
  budget, MOS Modules status, and board revisions when this task starts.
- No protocol, onboard-VDP firmware fork, pin assignment, circuit, or product
  commitment begins without separate Author review.
- If research supports implementation, split firmware, hardware, and
  qualification into approved tasks before changing production artifacts.

## Completion criteria

1. Measured use cases and Rev 1 relay limitations justify or reject the link.
2. Candidate buses and physical costs are compared against current hardware.
3. Ownership, compatibility, lifecycle, fallback, and protocol boundaries are
   accepted if the feature proceeds.
4. The product/version commitment is explicit.
5. Any implementation is split into separately reviewed firmware, hardware,
   and qualification tasks.
