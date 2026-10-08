# Light 2 to P4-PC wiring review draft

This [wiring diagram](wiring-diagram.svg) shows the proposed direct Agon Light 2
to Olimex ESP32-P4-PC Rev C harness, with every contact of both headers and
explicit resistor-to-rail connections. It is an unversioned review drawing;
physical construction and electrical qualification remain under
[BOARD-001](../../../docs/tasks/BOARD-001.md). The historical drawings are unchanged.
The Author arranged the bench to suit the original mapping and requested its
restoration. The diagram, native board profile and prepared P4-PC builds now
share the same assignments; no firmware remapping is required. This report
confirms the chosen arrangement, not powered transport qualification.

## Author construction clarification — 2026-10-08

The Author confirms that the P4-PC migration was wired according to the supplied
specification. Treat the complete restored mapping below, including PD4 READY_N,
PD5 CLOCK and PD7 VALID_N, as the reported connected arrangement. The older
DevKit r03 record of disconnected handshake lines does not describe this PC
migration. This is an Author construction report, not a new continuity or
powered parallel test; electrical qualification remains open.

The current EXT1 allocation has13 available transport/recovery GPIOs after
excluding GPIO2 (LED) and GPIO26/27 (USB): eight data/UART lanes plus three
handshake/clock lines are allocated, leaving GPIO47/48 at contacts19/20 spare.
Those two spare contacts are proposed for the deferred ZDI recovery connection;
they are not already connected or freely reassigned by this clarification.

## Reading the drawing

1. The upper view shows the complete 34-contact Agon and 20-contact P4-PC EXT1
   headers, viewed from the board/component side. Pin 1 is outlined. EXT1's
   pin 1/2 end is toward LAN/HDMI; its pin 19/20 end is toward USB-A.
2. The lower views separate each header's odd/even banks, with high-numbered
   contacts at the top, following the original drawing. The eight data wires
   run straight across. READY_N has one jog past unused Agon pin 15.
3. Eight 15 kΩ resistors pull PC0–PC7 up to **Agon pin 34, +3.3 V**.
   READY_N (Agon 13) and VALID_N (Agon 16) each have a 10 kΩ pull-up to that
   same rail. CLOCK (Agon 14) has a 10 kΩ pull-down to common ground.
   The data values follow the later r03 harness/Author report; the handshake
   values are inherited from the supplied legacy SVG. The r03 assembly did
   not retain those three handshake resistors; this drawing proposes their
   reinstatement for the shared UART/parallel mapping.
4. Agon pin 33 connects to P4-PC EXT1 pin 3 as common ground. The two boards'
   positive supply rails are separate. Neither PC EXT1 pin 1 nor pin 2 feeds
   the Agon pull-ups. No series resistors or sniffer markers are present.
5. PC GPIO20/32 are allocated to transport only with their optional board
   sensing links disconnected. GPIO47/48 at EXT1 pins 19/20 remain spare.
   UART and parallel roles share lanes; EMOS owns transport selection.

## Original mapping — restored

The native [P4-PC board profile](../../../vdp/build/boards/p4-pc.json) owns the
assignments. UART roles are named from the P4 side: P4 RX receives EMOS TX;
P4 TX sends to EMOS RX; P4 CTS receives EMOS RTS; P4 RTS sends to EMOS CTS.

| Agon pin | Signal / P4 UART role | PC EXT1 pin | PC GPIO |
|---:|---|---:|---:|
| 13 | PD4 / READY_N | 9 | 15 |
| 17 | PC0 / D0 / RX | 11 | 17 |
| 19 | PC2 / D2 / CTS | 13 | 19 |
| 21 | PC4 / D4 | 15 | 32 |
| 23 | PC6 / D6 | 17 | 36 |
| 14 | PD5 / CLOCK | 8 | 14 |
| 16 | PD7 / VALID_N | 10 | 16 |
| 18 | PC1 / D1 / TX | 12 | 18 |
| 20 | PC3 / D3 / RTS | 14 | 20 |
| 22 | PC5 / D5 | 16 | 33 |
| 24 | PC7 / D7 | 18 | 46 |
| 33 | Common ground | 3 | — |

D0–D7 GPIO order is **17, 18, 19, 20, 32, 33, 36, 46**;
READY_N/CLOCK/VALID_N are **15 / 14 / 16**. P4 UART TX/RX/RTS/CTS are
**18 / 17 / 20 / 19**, matching the existing native configuration and prepared
builds. The ascending-PC alternate proposal was withdrawn before any firmware
changes or rebuilds; its temporary CSV is no longer an active mapping authority.

## Sources and regeneration

The native P4-PC board profile supplies the signal allocation and physical
GPIO-to-header metadata. The generator derives Agon labels and layout style
from the preserved [legacy SVG](../light2-harness-r01/legacy-evidence/wiring-diagram.svg).
Complete PC labels and orientation follow the Olimex Rev C schematic and top
silkscreen indexed in the [manufacturer reference record](../../../docs/hardware/esp32-p4-pc/README.md).
The resistor values and power wiring are defined explicitly in
[`export_diagram.py`](export_diagram.py); no second independent pin map is created.

From the repository root:

```text
.venv/bin/python hardware/designs/light2-p4pc-harness-draft/export_diagram.py
```

Regeneration does not access either board. This drawing does not authorize
construction, flashing or powered testing, and it does not qualify unequal-power
behavior or GPIO contention. The selected native P4-PC build remains browser-only.
