# Stock MOS and VDP communications — review overview

[AUDIT-004](../AUDIT-004.md), W5 presentation, 2026-09-07. The inventory and
source review were accepted by the Author on 2026-09-07 for their declared
scope and frozen as an audit checkpoint. This overview is the reading entry
point, not a second inventory or
an Extender design specification.

The selected sources are **MOS v3.0.2** and **VDP v2.16.0**, with Agon Light 2
Rev B schematic context. Exact commits, documentation and dependency identities
remain in the [baseline record](baseline-and-research-map.md) and
[board/dependency evidence](trace-hardware-and-dependencies.md).

## What communicates with what

The ordinary onboard connection is **eZ80 UART0 (Port D) ↔ onboard VDP UART2**. MOS
sends command and resource bytes; VDP sends typed replies and input events.
The two directions use different message formats. Terminal and maintenance
sessions can change the stream's processing owner and interpretation.

VDP also supplies display VSync to an eZ80 interrupt input. The exposed
**Port C UART1 is a separate eZ80 interface for external devices**. Software
APIs, shared MOS state and callbacks add ways to initiate or observe these
exchanges; they do not add wires.

The [full inventory](communication-inventory.md) contains **46 path families
and 11 transport references**. The family groups are:

| IDs | Participants and communication |
| --- | --- |
| P001–P005 | MOS/application → VDP: text/drawing, bitmap/sprite/font resources, advanced rendering state, stored data/programs, and completion/swap requests. |
| P006–P015 | MOS ↔ VDP: startup polling; cursor, character, colour and mode queries; audio control/status; clock access; keyboard configuration/events; mouse controls/events. Some VDP messages are unsolicited or automatic. |
| P016–P018 | MOS or stored VDP commands change VDP variables, packet destinations, suppression, callbacks and echo. Stock MOS has no handler for the VDP echo packet types. |
| P019–P023 | Alternate eZ80 software and external tools use VDP terminal, HEX, YMODEM and firmware-update services. Their stock-side behavior is traced; external tool implementations are not selected baselines. |
| P024 | VDP display timing → eZ80 PB1 interrupt → MOS timing state, using the separate VSync route. |
| P025 | External console → VDP debugger → eZ80 hardware debug/reset interface, conditional on added attachment. Selected auxiliary debugger traffic also uses the onboard UART. |
| A001–A011 | Application/operator ↔ MOS: API calls, VDU output, shared state, keyboard/editor, callbacks/vectors, RTC helpers, CLI/scripts, named variables, executable launch/return and reset/crash entry. |
| X001–X003 | MOS/application ↔ external UART1 device, I2C device or SD card. Storage can also trigger VDP clock requests. |
| X004–X007 | VDP ↔ PS/2 keyboard/mouse; VDP → VGA display and audio outputs. |
| X008–X010 | VDP ↔ external serial host: diagnostics, printer forwarding and console reflection/input. These share the debug UART and USB-to-serial bridge used by maintenance services. |

IDs here retain the `AUDIT-004-` prefix by reference. The 11 transport entries
are the onboard UART, VSync, conditional ZDI attachment, VDP debug UART, eZ80
UART1, I2C, SD/SPI, keyboard PS/2, mouse PS/2, VGA and audio. Multiple connector
appearances or logical services can share one route.

## Findings that matter when reading the inventory

1. **Flow control depends on the endpoint and operating state.** VDP starts
   with RTS-only enabled, then MOS startup requests CTS+RTS. MOS's UART0 code
   polls CTS before transmitting and holds RTS asserted after setup; it does
   not adjust RTS with receive-buffer occupancy. Separately, the stock UART1
   API uses PC0/TX and PC1/RX, with optional PC3/CTS polling, and does not
   configure PC2/RTS. These are source behaviors, not measured throughput or
   loss guarantees. [Primary trace](trace-primary-protocol.md),
   [MOS interfaces](trace-mos-interfaces.md).
2. **Sending bytes, executing a command and receiving a result are different
   events.** MOS result flags generally identify the latest result family,
   not a particular request. Input state can be coalesced or overwritten;
   callbacks can alter packet contents or destinations. VDP's after-send
   callback means output was attempted, not that MOS received it. Callback
   storage also supplies no registration-order guarantee.
   [Primary trace](trace-primary-protocol.md).
3. **Apparently local operations can communicate.** MOS named-variable getters,
   pathname expansion and filesystem timestamps can request the clock from
   VDP. Stored VDP programs and callbacks can themselves produce traffic.
   An inventory limited to explicit drawing commands would miss these routes.
   [MOS interfaces](trace-mos-interfaces.md),
   [stored execution](trace-command-stream.md).
4. **The board drawing resolves misleading pin-name assumptions.** VSync runs
   from VDP GPIO15 to eZ80 PB1; GPIO17/ITRP is a different route. The selected
   board does not connect VDP GPIO26/27 to eZ80 ZDI. Those VDP pins also serve
   the default mouse interface, making attachments and coexistence explicit
   configuration limits. Shared physical reset wiring is distinct from each
   processor's software restart. [Board evidence](trace-hardware-and-dependencies.md).
5. **Documented behavior and selected implementation sometimes disagree.**
   Findings include keyboard-variable address/unit errors, callback lifetime
   differences and mouse reply promises. Source defects include incomplete
   packet validation/recovery, a raw-write API dispatched to the read wrapper,
   and a volume-label call that can act before returning an error. The evidence
   register distinguishes these from inherited fork fixes and physical test
   results. [Coverage corrections](coverage-review.md#corrections-incorporated-into-the-traces),
   [task evidence register](../AUDIT-004.md#w3-source-findings-and-remaining-interpretation).

## Coverage and remaining uncertainty

Every inventoried family has a trace through the selected endpoints or an
explicit external boundary. W4 reconciled MOS API/CLI/vector tables, VDP
documentation and dispatchers, reverse-packet producers, peripheral services
and configuration branches. No additional family was identified in those
reviewed surfaces. The [coverage review](coverage-review.md) states the exact
source-entry coverage; it does not prove every program path or opcode correct.

The remaining uncertainties are external tool/device implementations, deeper
driver/RTC/debug-hardware behavior, alternate builds and runtime combinations,
and actual timing, loss, recovery and electrical behavior. One older schematic
hash still lacks identifiable source bytes; the selected Rev B PDF itself is
authenticated. These limits remain under task evidence entries E03, E04, E11
and E19. The [Author review section](../AUDIT-004.md#w5-presentation-and-author-review)
owns their disposition and any later scope choice.

The delivered record supports review of **stock communication behavior within
this evidence boundary**. It does not establish Extender compatibility
requirements, buffer necessity, pull-up sufficiency or a revised circuit.
No builds or hardware tests were performed. The held r02 design remains
incomplete, its full wiring incomplete and its complete circuit untested.

For detail, use the [inventory](communication-inventory.md),
[trace index](communication-traces.md), [coverage review](coverage-review.md)
and [task register](../AUDIT-004.md). The audit is accepted and closed; any
later comparison or investigation requires separate authorization.
