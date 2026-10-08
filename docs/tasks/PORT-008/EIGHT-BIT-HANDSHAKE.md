# PORT-008 — Corrected eight-bit payload scope

## Executive summary

The Author intends bidirectional eight-bit payload on PC0–PC7, using the existing
dedicated READY/CLOCK/VALID connections on P4-PC.
The initial four-lane SPI payload recommendation answered a different question
and is withdrawn. The subsequent [prototype review](FORWARD-PROTOTYPE-REUSE.md) confirms that
forward byte sampling is already proved using a separate PD5 clock wire.
The P4-PC specification includes CLOCK, READY and VALID; the Author confirms
following that specification. No extra handshake wiring or pseudo-SPI is required
to recover these signals. The [development contract](BIDIRECTIONAL-DEVELOPMENT.md)
now owns implementation work and the remaining qualification boundaries.

## Required phase distinction

| Phase | PC0–PC3 | PC4–PC7 | Endpoint responsibility |
|---|---|---|---|
| Prepare | UART TX/RX/RTS/CTS | Inputs; unused for setup | EMOS initiates; P4 prepares; both agree direction and bounded length |
| Handover | Transition from UART to payload | Remain inputs until admitted | Both stop old drivers before enabling new ownership; no fixed delay alone proves peer readiness |
| Payload | Data bits | Data bits | One processor drives all eight bits; the other samples; Proved forward PD5 clock; reverse alignment remains open |
| Return | Transition back to UART | Return to inputs | Both release payload ownership and establish UART readiness before resuming input/control |

RAM flags retain local negotiated state. They are neither shared memory nor a
clock. The already-specified PD4/PD5/PD7 connections provide READY/CLOCK/VALID
without consuming payload bits. A pseudo-SPI exchange is no longer the recommended
way to recover missing signals: the signals are already in the PC specification.
eZ80 hardware SPI and the SD reader remain outside this proposal.

## Reconciled design boundaries

1. Use the complete P4-PC mapping, including PD5 clock and PD4/PD7 handshake
   lines. Review their forward/reverse roles before changing the known protocol;
   no reconnect decision is needed from the Author's construction report.
2. How do EMOS and P4 confirm phase transitions using the dedicated control lines
   whose drivers remain unchanged? Define release ordering and observable acknowledgements without
   relying only on simultaneous execution or timed delays.
3. How are UART FIFOs drained, unsolicited P4 keyboard packets queued, and input
   service resumed between bounded blocks? Neither endpoint may keep its UART
   transmitter or RTS driver enabled on a payload lane.
4. How does either processor stop/recover after a reset, timeout or partial block
   while UART is unavailable? Driver release and fresh-session admission must
   prevent stale RAM state from granting ownership.
5. What do the retained early SPI and eight-bit experiments establish about
   timing and speed, and which required signals were physically connected then?
   Preserve their limits; do not infer current compatibility from old captures.

F01 source/wiring reconciliation is complete. Remaining design boundaries
belong to F02c/d, not additional independent tasks.
If no credible no-extra-wire eight-bit scheme emerges, report the precise
constraint and ask the Author to choose a tradeoff; do not substitute a narrower
payload design without agreement.
