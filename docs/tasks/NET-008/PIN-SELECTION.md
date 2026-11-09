# Temporary ESP8266 branch — task-only wiring record

Use P4-PC EXT1 contacts19/20 for the modem's two UART signals. They are the
last pair at the USB-A end, immediately beyond the existing brown D6 and green
D7 connections. The [full drawing](ESP8266-WIRING.svg) retains all existing
Agon/P4 harness wiring and adds the modem branch; [PNG preview](ESP8266-WIRING.png).
Smith reports the wiring complete on2026-11-09 and corrects the P4 RX wire colour to orange, matching Console8. This records his construction report. The swapped firmware now passes byte exchange; independent continuity and power-margin checks remain unperformed.

## Current functional connections — swapped firmware passes AT

| P4-PC EXT1 contact | P4 function | Modem terminal | Drawing colour |
|---|---|---|---|
| 19 / GPIO47 | UART2 RX, P4 receives | TXD | Teal |
| 20 / GPIO48 | UART2 TX, P4 transmits | RXD | Orange (wire retained) |
| 3 / GND | Existing common ground, add a branch | GND | Black |
| 1 / +3.3V | Candidate modem supply; power margin still to establish | VCC / 3.3V | Dashed red |

Use the modem's terminal labels, not the order drawn in the logical block.
The existing four-wire modem has no RTS/CTS terminals. UART2 is proposed at
1152008N1; maintained console code currently uses UART1, and normal console
logging uses USB serial/JTAG. The TX48/RX47 development diagnostic passes actual AT/GMR and three repeated AT exchanges. This establishes functional byte exchange; the modem connector orientation and power margin have not been independently surveyed.

## Orient against the existing wires

1. View the P4-PC EXT1 header from the board/component side, as in the base
   drawing. Pins1/2 are at the LAN/HDMI end; pins19/20 are at the USB-A end.
   A wiring-side socket view is mirrored.
2. The existing brown wire is EXT1-17/GPIO36/D6. Move one header row toward
   USB-A to EXT1-19/GPIO47 for the current modem RX.
3. The existing green wire is EXT1-18/GPIO46/D7. Move one header row toward
   USB-A to EXT1-20/GPIO48 for the current modem TX.
4. In the lower separated-bank views, pins19/20 are immediately above those
   brown/green wires. Actual breadboard row numbers have not been recorded;
   this proposal does not invent hole coordinates.
5. EXT1-3 already connects to Agon pin33/common ground. The new modem ground
   is another branch of that same ground. EXT1-1 is P4 +3.3V, distinct from
   Agon pin34/+3.3V, which continues to feed the existing pull-ups.

The complete eight data wires, three handshake/clock wires, common ground,
pull resistors and power rails remain visible. Existing colours and resistor
values follow the base drawing. The base's handshake resistor provenance and
electrical-qualification limits remain; this copy is not a new as-built survey.

## Allocation and power limits

1. The maintained P4-PC profile maps GPIO47/48 to contacts19/20 and assigns
   neither to transport nor its reserved GPIO list. The base drawing reports
   both contacts spare. Their earlier proposed ZDI assignment was deferred,
   not installed by that record; the reported temporary modem wiring occupies
   both. It does not silently modify a recovery profile or create simultaneous
   modem/ZDI use.
2. GPIO47/48 share VDDPST_5/LDO4 with the already-connected GPIO46/D7. Existing
   P4-PC builds must keep this bank at3.3V. A separate UART signal pair does
   not authorize disabling this existing supply requirement.
3. The Rev C PCB confirms EXT1-1 is +3.3V and EXT1-3 is GND. Modem peak demand,
   local decoupling and spare P4 supply current have not been established for
   this physical assembly. The red supply connection remains conditional;
   do not treat the diagram as power-on readiness. Do not use EXT1-2/+5V for
   the selected3.3V modem or join the two computers' positive supply rails.
4. Smith reports completing the physical wiring. The agent performed no physical
   inspection, firmware build, pin drive, power operation or hardware test. Hardware remains
   under the dedicated scheduler. Existing pin profiles and harness authorities
   are unchanged.

## Source and retention

Smith selected the pin drawing on2026-11-09 and explicitly required it to remain
siloed in this task. All derived files and their generator are here; the base
diagram is untouched. Existing NET-008/FREEZE-R01.json and its historical
priority/topology record remain unchanged. Smith's current ESP8266 priority
supersedes the older secondary-priority wording for this selected work.

1. Base: [complete P4-PC harness](../../../hardware/designs/light2-p4pc-harness-draft/wiring-diagram.svg),
   SHA256 `b32749d5e62c1ba32dca68840b7907d5683c02676096ae9c35325732e0c73746`.
   Its [construction/orientation record](../../../hardware/designs/light2-p4pc-harness-draft/README.md)
   records the Author's2026-10-08 migration wiring report.
2. Pin authority: [P4-PC board profile](../../../vdp/build/boards/p4-pc.json),
   SHA256 `726faa5ae9b6cdcdb2c8a7c6ae8b6276bdb68460cfab5361d43e2c4c159686d7`.
3. Manufacturer reference: Olimex ESP32-P4-PC Rev C, commit
   `04032d68e5c727870f9d40beb9e37b7ab3a66916`.
   [Schematic](https://github.com/OLIMEX/ESP32-P4-PC/blob/04032d68e5c727870f9d40beb9e37b7ab3a66916/HARDWARE/ESP32-P4-PC-Rev.C/ESP32-P4-PC_Rev_C.pdf)
   and matching PCB source were inspected read-only. EXT1 footprint pads1/3/19/20
   carry +3.3V/GND/GPIO47/GPIO48 respectively. Local checkout remains clean.
   [Reference index](../../hardware/esp32-p4-pc/README.md) records the source location.
4. The generator preserves all42 existing SVG path elements exactly and checks
   the proposed GPIOs against the maintained transport/reserved allocation.
   Native librsvg/Cairo exports a PNG that was visually inspected. ImageMagick's
   internal renderer omitted existing wire paths; that failed preview is not
   the delivered drawing.

Regenerate from the repository root:

```text
.venv/bin/python docs/tasks/NET-008/draw_wiring.py
```

Pin/supply labels in this proposal are supported by the current schematic and
profile. Construction is Author-reported; independent electrical checks and
modem power margin remain to be established. No generic protocol or product pin-map change is
selected by creating this task-local drawing.

## Actual swapped-pins result

Smith selects software reversal before checking the ESP8266 end. With wiring
unchanged, actual164-r02 TX48/RX47 passes all five exchanges at1152008N1; modem
reports AT1.3.0.0/SDK2.0.0. The drawing now shows that functional direction while
retaining the teal GPIO47 and orange GPIO48 physical leads. The original TX47/
RX48 attempt remains a zero-byte failure in the historical test record.
Development firmware remains installed by explicit Author instruction; UART
pins retire to inputs after the finite test. No bandwidth qualification yet.
