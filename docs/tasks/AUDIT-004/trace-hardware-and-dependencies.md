# Stock communication traces — board and dependency evidence

[AUDIT-004](../AUDIT-004.md), W3, 2026-09-07. This supplements the
[fixed stock baseline](baseline-and-research-map.md) where firmware calls reach
library-owned behavior or physical wiring. It describes source and schematic
evidence, not the wiring, jumper population, or behavior of a bench specimen.
The hardware hold remains in effect.

## Additional authenticated references

| Source | Identity and authentication | Scope |
| --- | --- | --- |
| vdp-gl | [Commit `ac2dd5986daf496c43ae8e7fe41836274aec54a0`](https://github.com/AgonPlatform/vdp-gl/tree/ac2dd5986daf496c43ae8e7fe41836274aec54a0), already selected by the historical stock control build. W3 checked the inspected files against blob IDs in the official repository's commit tree. | PS/2 defaults, VGA generation, drawing completion, audio defaults, and terminal boundary. Project-modified vendor files were not assumed to be stock. |
| Arduino-ESP32 | Tag 2.0.14 resolves to [commit `44da992b774f76777bb2e931dd76cfcf12b9fe70`](https://github.com/espressif/arduino-esp32/tree/44da992b774f76777bb2e931dd76cfcf12b9fe70). W3 authenticated `HardwareSerial`, `Stream`, and `esp32-hal-uart` implementation/header files against official Git blobs. | UART wrapper configuration, return values, reads, and writes. This binds the inherited framework version to source; it does not authenticate a deployed binary or exhaustively trace ESP-IDF internals. |
| Olimex AgonLight2 Rev B | [Four-sheet schematic][B-SCH] at inherited commit `b7f2a21c282813efd8cdf26573eb5126876432a8`; title blocks show Rev B, 2022-12-15. Downloaded PDF matches official Git blob `903fe581c59f5d0111d7e03f702cf3315a95665b`; SHA-256 is `559861bf7d723d2ac0978fe95808a9b16415257271619ca4457ec400326d9ee6`. All four sheets were visually inspected. | Source-board routes below, conditional on Rev B wiring. No claim that a specific specimen is Rev B or has a particular jumper state. |
| Zilog eZ80F92/eZ80F93 | W4 retrieved the [manufacturer specification][Z-F92], `PS015317-0120`, SHA-256 `9d64cfd5e75e50b009028f75ec6a2377ee1cf3721443715d32a78a0d920a71ba`, matching the inherited F92 document hash. | Document identity, GPIO mode/data semantics and UART modem-register semantics used below. This is not a review of every peripheral/electrical requirement. |

The freshly authenticated schematic hash differs from the inherited
`5019caa700d034bd16b720184f291c9768be3dba62734f0569887ee19704953c`
recorded in the earlier circuit proposal. W3 uses the explicit repository path,
commit, Git blob, and fresh hash above. It does not relabel the unidentified
older bytes as this PDF or infer a circuit revision change from the mismatch.
The task evidence register retains that provenance discrepancy. Retrieval and
file-integrity records are kept in ignored local research storage.

## Wiring trace at the selected board source

The schematic's signal names sometimes describe the peer rather than the ESP32
peripheral's role. Pin identity and direction below take precedence over those
names. The [primary protocol trace](trace-primary-protocol.md) records the
firmware configuration; the [VDP interface trace](trace-vdp-interfaces.md)
records library defaults and operating modes.

| Audit reference | Schematic route and endpoint | Consequence / boundary |
| --- | --- | --- |
| AUDIT-004-T001, forward bytes | Sheet 1: eZ80 U1 PD0/TXD0, pin 68, through R8, BUF2 and R19; sheet 2: `ESP_RXD` reaches ESP32 U3 GPIO34, pin 10. | MOS UART0 TX reaches VDP UART2 RX through onboard components. BUF2 enable shares the `UART_DIS1`/BUF3 circuit; uninterrupted connection is conditional on that circuit's state. |
| AUDIT-004-T001, reverse bytes | Sheet 2: ESP32 GPIO2, pin 22, through R24, `ESP_TXD`; sheet 1: BUF1 and R18 to eZ80 PD1/RXD0, pin 69. | VDP UART2 TX reaches MOS UART0 RX through onboard components, with the same enable condition. These existing onboard buffers are distinct from the held Extender circuit. |
| AUDIT-004-T001, pacing | Sheets 1–2: eZ80 PD2/RTS0, pin 70, net `ESP32_RTS`, reaches ESP32 GPIO14, pin 17; eZ80 PD3/CTS0, pin 71, net `ESP32_CTS`, reaches ESP32 GPIO13, pin 20. | ESP32 source assigns GPIO14 as CTS input and GPIO13 as RTS output. This explains the apparent reversal between schematic net names and VDP macro names; it does not establish measured pacing margins. |
| AUDIT-004-T002 / AUDIT-004-P024 | Sheet 2: ESP32 GPIO15, pin 21, net `VS`, connects both VGA1 pin 14 and, on sheet 1, eZ80 PB1, pin 89. | This is the VSync route consumed by MOS's PORTB1 interrupt. ESP32 GPIO17, net `ITRP`, instead reaches eZ80 PB0, pin 88. The reference-only `GPIO_ITRP=17` declaration is not proof of the VBLANK producer. |
| AUDIT-004-T003 / AUDIT-004-P025 | Sheet 1: eZ80 TCK/TDI pins 63/65; sheet 3: ZDI1 pins 4/6. ESP32 GPIO26/27 instead reach GPIO1 header pins 9/8 and have R20/R21 pull-ups on sheet 2. | The selected board does **not** draw a GPIO26/27 connection to eZ80 TCK/TDI. The VDP debugger source requires additional physical wiring to use its declared pins as that controller. No such attachment is assumed or authorized here. |
| AUDIT-004-T004 | Sheet 2: ESP32 GPIO1/GPIO3, nets `ESP_CH340_TXD`/`ESP_CH340_RXD`; sheet 4: CH340T U9 and USB1 through the shown serial/USB interface circuitry. | External-host maintenance and debug traffic use a USB-to-UART bridge, not native ESP32 USB. CH340 control lines also reach reset/programming circuitry; an external host's port-open/control behavior is not established by stock MOS/VDP source. |
| AUDIT-004-T005 / AUDIT-004-X001 | Sheet 1: eZ80 PC0–PC3 pins 76–79; sheet 3: GPIO1 pins 17–20. PC0/PC1 also reach UEXT1 pins 3/4; PC2 reaches UEXT1 pin 10. | Header exposure is separate from MOS UART1 configuration. Source evidence for CTS-only handling does not establish a four-wire UART1 setup or arbitrary external peer protocol. |
| AUDIT-004-T006 / AUDIT-004-X002 | Sheet 1: eZ80 SDA/SCL pins 98/99; sheet 3: GPIO1 pins 29/30, UEXT1 pins 6/5, ACCESS_BUS1 pins 1/2, with the shown R39/R40 pull-ups. | One shared I2C bus has several connector appearances; these are not separate controllers. Device addressing, added loading, and a particular peripheral remain outside the selected pair. |
| AUDIT-004-T007 / AUDIT-004-X003 | Sheet 1: PB7 MOSI, PB6 MISO, PB3 SCK, PB4 card select; sheet 3: corresponding `MICROSD_*` nets at MICRO_SD1. SPI data/clock also appear on expansion connectors; UEXT chip select uses PC2, not the card's PB4. | Shared data/clock exposure does not mean identical device-select wiring. Card protocol and MOS storage behavior are in the MOS trace. |
| AUDIT-004-T008 / AUDIT-004-X004 | Sheets 2–3: GPIO32 `KDAT` and GPIO33 `KCLK` through the shown FET interface to USB_KEYBOARD1 D−/D+ pins. | The keyboard connector carries the library's PS/2 clock/data protocol despite its USB-A form. No USB-host enumeration is inferred. |
| AUDIT-004-T009 / AUDIT-004-X005 | Sheets 2–3: GPIO26/27 appear at GPIO1 pins 9/8; no dedicated mouse connector is drawn. | The second PS/2 port and VDP debugger declare overlapping ESP32 pins. Their external attachments and coexistence are configuration boundaries, not proof of two simultaneously available interfaces. |
| AUDIT-004-T010 / AUDIT-004-X006 | Sheet 2: GPIO22/21, 19/18, 5/4 through resistor networks to VGA red/green/blue; GPIO23/15 to horizontal/vertical sync. | Matches the authenticated library's default VGA pin set. Pixel conversion quality, timing margins, and monitor behavior are not measured here. |
| AUDIT-004-T011 / AUDIT-004-X007 | Sheet 2: GPIO25 `SOUND` through R25 and the coupling/filter network to AUDIO1; the buzzer branch includes the shown transistor and enable jumper. | Source DAC selection reaches the drawn audio circuitry. Audible output depends on connector/jumper/peripheral state; no amplitude or quality qualification is implied. |
| Reset context for AUDIT-004-A011 / AUDIT-004-P025 | Sheets 1, 2, 4: `RST\EN` reaches eZ80 reset and ESP32 EN, the reset switch/supervisor, and USB programming-control circuitry. | The board has a shared physical reset net. MOS software restart, ESP32 software restart, and ZDI CPU reset are distinct operations; none alone proves that this physical net was asserted. |

## Evidence limits

W3 authenticates the library files actually inspected and the board source
above. W4 resolves the processor-document identity: the official Agon docs'
`ps0130.pdf` link opens the **eZ80L92** specification `PS013015-0316`, whereas
`ps0153.pdf` opens the selected **eZ80F92/eZ80F93** specification. The old board
PDF byte-identity mismatch remains open. No voltage threshold, pull-resistor
adequacy, reset sequencing guarantee, or UART signal-integrity requirement is
derived here. External transfer-tool
implementations, terminal peers, peripheral devices, and ESP-IDF internals not
explicitly traced remain named boundaries in the associated trace files.

## W4 — Reached eZ80 peripheral semantics

1. **T001 pacing:** the F92/F93 specification, printed page 119, table 63
   (PDF page 127), defines RTS output as the inverse of modem-control bit 1.
   Printed page 122, table 65 (PDF page 130), defines status bit 4 as the
   inverted CTS input. MOS `open_UART0` selects those alternate pins and
   writes `UART0_MCTL=0x02`; `UART0_wait_CTS` polls status bit 4. These establish
   an asserted RTS output and a software transmit gate. The selected MOS source
   contains no receive-occupancy-driven RTS update. VDP's later CTS+RTS driver
   request does not make MOS's receive pacing automatic. [Z-F92], [M-UART],
   [M-SERIAL]
2. **T002/P024 interrupt:** MOS startup chooses `GPIOMODE_INTRE` (9) for mask
   `0x02`; `GPIOB_M9` sets PB1's data/direction/alternate bits for rising-edge
   interrupt input. The F92/F93 specification's table 6, printed page 40
   (PDF page 48), identifies that bit pattern. Printed page 43 (PDF page 51)
   defines writing 1 to an edge-triggered pin's data-register bit as clearing
   its interrupt request. That supplies the documented semantics for the
   handler's OR/write of `0x02`, while clock increment and physical arrival
   rate remain distinct. [Z-F92], [M-PB-INIT], [M-GPIO], [M-GPIO-CONST]

[B-SCH]: https://github.com/OLIMEX/AgonLight2/blob/b7f2a21c282813efd8cdf26573eb5126876432a8/HARDWARE/AgonLight2_Rev_B/AgonLight2_Rev_B.pdf
[Z-F92]: https://www.zilog.com/docs/ez80acclaim/ps0153.pdf
[M-UART]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/uart.c#L62-L95
[M-SERIAL]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm#L76-L112
[M-PB-INIT]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/init_params_f92.asm#L195-L199
[M-GPIO]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/gpio.asm#L104-L111
[M-GPIO-CONST]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/equs.inc#L53-L62
