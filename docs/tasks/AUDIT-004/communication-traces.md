# Stock MOS/VDP communication traces — W3

[AUDIT-004](../AUDIT-004.md), recorded 2026-09-07. W3 follows the W2 inventory's
46 path families through their selected source endpoints or explicit external
boundary. The [baseline](baseline-and-research-map.md) remains stock MOS v3.0.2
and VDP v2.16.0. This is source evidence, not a test result or an accepted
Extender compatibility requirement. [W4 coverage reconciliation](coverage-review.md)
is complete and its corrections are incorporated here. The [W5 overview](README.md)
presents the result, accepted by the Author on 2026-09-07 within its stated limits.

## Trace map

| Inventory references | Trace and responsibility |
| --- | --- |
| AUDIT-004-P001–P005 | [Forward command stream](trace-command-stream.md): MOS byte output, VDP command consumption, resources and stored execution, display effects and completion. |
| AUDIT-004-T001; AUDIT-004-P006–P018 | [Primary UART and reverse protocol](trace-primary-protocol.md): startup, flow control, every ordinary reverse payload and MOS consumer, result/event coordination, redirection, echo, and parser failure limits. |
| AUDIT-004-A001–A011; AUDIT-004-X001–X003; AUDIT-004-T005–T007 | [MOS interfaces](trace-mos-interfaces.md): application/operator calls, shared state, callbacks, lifecycle, UART1, I2C, and storage. |
| AUDIT-004-P019–P025; AUDIT-004-X004–X010; AUDIT-004-T002–T004 and T008–T011 | [VDP interfaces](trace-vdp-interfaces.md): alternate sessions, transfers, updater/debugger, VSync, keyboard/mouse, display/audio and external console. |
| Physical routes and reached libraries | [Board and dependency evidence](trace-hardware-and-dependencies.md): authenticated source identities and conditional Light 2 Rev B wiring. Transport appearances at multiple connectors remain one shared route. |

The [inventory](communication-inventory.md) retains stable IDs and its compact
entry map. These traces supply the detailed W3 evidence; the task file owns
evidence dispositions and future work.

## Findings that affect interpretation

1. **One UART supports several different contracts.** Ordinary VDU output is
   a command byte stream; reverse traffic uses typed length/payload packets.
   Terminal and transfer sessions change the processing owner or grammar.
   VDP starts with RTS-only pacing; selected MOS startup then requests CTS+RTS.
   MOS itself statically asserts RTS and polls CTS before transmission; the VDP
   setting does not establish occupancy-driven MOS receive backpressure.
   Flow-control setup, byte acceptance, command execution, and result receipt
   are separate events. [Primary trace](trace-primary-protocol.md),
   [alternate sessions](trace-vdp-interfaces.md).
2. **MOS generally publishes latest state.** Result flags identify families,
   not request instances. Keyboard/mouse state can be coalesced or overwritten;
   callbacks and automatic notifications matter. A flag or completed output
   call alone is not proof of a fresh, valid, fully rendered transaction.
   [Primary trace](trace-primary-protocol.md),
   [MOS state and callbacks](trace-mos-interfaces.md).
3. **Communication can be indirect.** Buffered VDP programs and callbacks can
   generate responses; MOS named-variable/pathname operations and FatFS timestamps can
   emit VDP requests. Inventorying only explicit display commands would miss
   these dependencies. [Stored execution](trace-command-stream.md),
   [MOS variables and storage](trace-mos-interfaces.md).
4. **Stock UART1 is distinct from the onboard UART.** Its flow-control option
   polls PC3/CTS and does not configure PC2/RTS. This establishes what the stock
   MOS API does, not what another program or the eZ80 peripheral could support.
   [UART1 trace](trace-mos-interfaces.md).
5. **Board wiring resolves two misleading source leads.** Display VSync comes
   from ESP32 GPIO15 to eZ80 PB1; GPIO17/ITRP is another route. The selected
   Light 2 schematic does not connect the debugger's GPIO26/27 declarations to
   eZ80 ZDI. Additional attachment would be required for that source facility.
   [Board evidence](trace-hardware-and-dependencies.md).
6. **Documentation and implementation differ in material places.** The traces
   resolve mode-info length, echo peer support, callback ownership, function
   lookup status and sector-count units. They also identify stock parser
   recovery defects, the raw-write API's incorrect read dispatch, and RTC
   waiting behavior. W4 adds variable-address/unit corrections, callback
   ordering/lifetime qualifications, and a volume-label status defect. These
   observations are recorded in the task register;
   this audit applies no firmware fixes or circuit conclusions.

## Remaining evidence boundaries

Every inventory family has a trace location. W4 reconciled the selected
documentation and source entries without identifying another family; its
coverage review states the precise boundary. External terminal/transfer
tools and device firmware are not selected audit baselines; their peers are
traced from the stock side only. The ZDI controller's declared hardware endpoint
is identified, while its additional attachment and processor debug-register
contract remain unverified. Reached vdp-gl and Arduino UART source was
authenticated; deeper framework, RTC-library, and device-specific behavior is
bounded where the corresponding trace stops.

The board record authenticates an explicit Rev B schematic, whose fresh hash
differs from the inherited unnamed-byte record. It establishes source wiring,
not specimen identity. W4 authenticated the F92/F93 manual and reached
GPIO/UART semantics; physical timing, electrical margins, and reset/power
behavior requiring measurement remain unresolved. No build, emulator run, deployment, wiring operation, or hardware
test was performed. The existing hardware hold remains in effect.
