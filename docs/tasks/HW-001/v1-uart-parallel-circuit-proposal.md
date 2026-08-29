# HW-001 V1 UART and forward-parallel circuit proposal

## Status and authority

1. **Status:** Four-chip transport topology accepted on 2026-08-28 and frozen
   on 2026-08-29 as the controlled-beta `light2-harness-r02` candidate.
2. **Authority:** The placement-independent electrical authority is
   `hardware/designs/light2-harness-r02/connectivity.yaml`. This document
   explains that circuit but is not a construction drawing or qualification
   claim.
3. **Scope:** Agon Light 2 to Olimex ESP32-P4-DevKit Rev D1; one common
   four-signal UART used by Exclusive Compatible and Exclusive Extended, plus
   the one-way eight-bit Agon-to-Extender parallel transport used by Exclusive
   Extended.
4. **Physical work:** Controlled construction of
   `light2-extender-solderless-assembly-r02` is authorized under HW-001 and the
   applicable bench procedures. Powered testing is separately gated.

## Design result

The accepted transport core uses two `SN74LVC244AN` octal three-state
buffers and two `SN74LV125AN` quad three-state buffers. It preserves the proved
predecessor signal-to-P4 mapping, adds all four eZ80 UART1 signals, prevents any
interface output from being enabled merely by P4 reset or absence, keeps the
Agon and P4 positive rails separate, and supplies partial-power-down protection
at every cross-board output.

The fourth buffer, `U4`, is deliberately used as four low-only isolated control
sinks. Each `U4` data input is tied to ground. A P4 control GPIO drives that
channel's active-low output-enable input. The channel therefore either pulls
its output low or releases it to high impedance; it never drives an Agon-domain
control net high. Agon-domain pull-ups own the disabled state. This obtains the
required open-drain-like cross-power behavior from an active, through-hole,
partial-power-down-rated part already selected for Extender experiments.

```text
Agon PC0,PC2 ──> U1 bank 1 ──> 220 R ──> P4 RX/CTS or parallel D0/D2

Agon PC1,PC3 ──> U1 bank 2 ──> 220 R ──> P4 parallel D1/D3
Agon PD5,PD7 ──> U1 bank 2 ──> 220 R ──> P4 CLOCK/VALID_N
Agon PC4..PC7 ─> U2 bank 1 ──> 220 R ──> P4 parallel D4..D7

P4 TX,RTS ─────> U3 channels 1/2 ──> 220 R ──> Agon PC1/RXD1, PC3/CTS1

P4 mode controls ─> U4 low-only sinks ─> U1/U2/U3 OE_N and READY_N
```

The circuit does not introduce direct onboard-VDP/EDP communication, a reverse
parallel path, a second mode-specific UART, or positive-rail sharing.

## Electrical domains

| Domain | Source | Loads in this proposal | Rule |
|---|---|---|---|
| `AGON_3V3` | Agon header pin 34 | `U1`, `U2`, `U3`, their OE pull-ups, and Agon-side bias | Never join to `P4_3V3` |
| `P4_3V3` | P4 EXT1 pin 1 | `U4`, P4 control pull-ups, and P4 receive-side bias | Never join to `AGON_3V3` |
| `GND` | Agon pin 33 and P4 ground pins | Both domains and every signal return | One common signal ground is mandatory |

Use P4 EXT1 pin 2 and the conveniently routed EXT2 ground contacts where the
carrier permits. Multiple ground contacts are one electrical net, not separate
domains. P4 EXT2 pin 1 (`+5V`) remains unconnected to this interface.

Place one 100 nF ceramic bypass capacitor directly between VCC and GND at each
of `U1` through `U4`. Place one 1 uF local bulk capacitor on each 3.3 V domain.
The production layout must keep each bypass loop short; breadboard construction
must place each 100 nF part adjacent to its IC supply pins.

## Endpoint allocation

### Four-signal UART

The P4 endpoint uses Arduino/ESP-IDF UART2 (`Serial2` / `UART_NUM_2`) through
the GPIO matrix. Retaining `Serial2` preserves the official VDP source idiom,
while avoiding UART0, which Espressif reserves conventionally for download and
diagnostic output. GPIO-matrix delay is immaterial at 1.152 Mbaud; Espressif
only requires direct IO-MUX routing for UART rates above 40 MHz.

| Wire role | Agon/eZ80 endpoint | P4 endpoint | Direction | Active level |
|---|---|---|---|---|
| eZ80 transmit | pin 17, `PC0/TXD1` | EXT2-11, GPIO22, UART2 RX | Agon to P4 | UART data |
| eZ80 receive | pin 18, `PC1/RXD1` | EXT1-13, GPIO12, UART2 TX | P4 to Agon | UART data |
| eZ80 request-to-send | pin 19, `PC2/RTS1` | EXT2-10, GPIO23, UART2 CTS | Agon to P4 | Low = P4 may send |
| eZ80 clear-to-send | pin 20, `PC3/CTS1` | EXT1-12, GPIO11, UART2 RTS | P4 to Agon | Low = eZ80 may send |

The UART target is 1,152,000 baud, 8 data bits, no parity, one stop bit, and
active-low RTS/CTS flow control. Official MOS v3.0.2 configures UART1 TX/RX and
polls `PC3/CTS1`, but does not configure `PC2/RTS1` as UART1 RTS. EMOS must own
that missing eZ80-side configuration before the four-wire circuit can be
qualified; the hardware must not disguise this firmware dependency.

### Forward parallel transport

| Function | Agon/eZ80 endpoint | P4 endpoint | Direction |
|---|---|---|---|
| `D0` | pin 17, `PC0` | EXT2-11, GPIO22 | Agon to P4 |
| `D1` | pin 18, `PC1` | EXT1-13, GPIO12 | Agon to P4 |
| `D2` | pin 19, `PC2` | EXT2-10, GPIO23 | Agon to P4 |
| `D3` | pin 20, `PC3` | EXT1-12, GPIO11 | Agon to P4 |
| `D4` | pin 21, `PC4` | EXT2-9, GPIO32 | Agon to P4 |
| `D5` | pin 22, `PC5` | EXT1-11, GPIO10 | Agon to P4 |
| `D6` | pin 23, `PC6` | EXT2-8, GPIO33 | Agon to P4 |
| `D7` | pin 24, `PC7` | EXT1-10, GPIO9 | Agon to P4 |
| `CLOCK` | pin 14, `PD5` | EXT1-15, GPIO14 | Agon to P4 |
| `VALID_N` | pin 16, `PD7` | EXT1-14, GPIO13 | Agon to P4 |
| `READY_N` | pin 13, `PD4` | EXT2-13, GPIO20 control | P4 to Agon, low-only |

The mapping retains the predecessor's physically exercised PARLIO assignment.
GPIO23 remains usable because Olimex leaves the optional Rev D1 Ethernet-clock
link resistor `R31` unpopulated; the Author also verified the current specimen
has open pads at that position. No selected signal uses P4 strapping GPIO34
through GPIO38, USB GPIO24/GPIO25, the microSD interface, MIPI, Ethernet data
signals, or the accepted GPIO37/GPIO38 MOD-WIFI reservation.

## Buffer and pin assignment

### U1 — `SN74LVC244AN`, fixed and shared forward signals

`U1` is powered by `AGON_3V3`; pin 20 is VCC and pin 10 is GND.

| U1 input | Source | U1 output | Series part | Destination | Enable |
|---|---|---|---|---|---|
| pin 2, `1A1` | Agon `PC0` | pin 18, `1Y1` | 220 ohm | P4 GPIO22, `D0` / UART RX | pin 1, `UART_FWD_OE_N` |
| pin 4, `1A2` | Agon `PC2` | pin 16, `1Y2` | 220 ohm | P4 GPIO23, `D2` / UART CTS | pin 1, `UART_FWD_OE_N` |
| pin 6, `1A3` | GND | pin 14, `1Y3` | none | no-connect | pin 1, `UART_FWD_OE_N` |
| pin 8, `1A4` | GND | pin 12, `1Y4` | none | no-connect | pin 1, `UART_FWD_OE_N` |
| pin 17, `2A4` | Agon `PC1` | pin 3, `2Y4` | 220 ohm | P4 GPIO12, `D1` | pin 19, `PAR_FWD_OE_N` |
| pin 15, `2A3` | Agon `PC3` | pin 5, `2Y3` | 220 ohm | P4 GPIO11, `D3` | pin 19, `PAR_FWD_OE_N` |
| pin 13, `2A2` | Agon `PD5` | pin 7, `2Y2` | 220 ohm | P4 GPIO14, `CLOCK` | pin 19, `PAR_FWD_OE_N` |
| pin 11, `2A1` | Agon `PD7` | pin 9, `2Y1` | 220 ohm | P4 GPIO13, `VALID_N` | pin 19, `PAR_FWD_OE_N` |

### U2 — `SN74LVC244AN`, remaining parallel data

`U2` is powered by `AGON_3V3`; pin 20 is VCC and pin 10 is GND.

| U2 input | Source | U2 output | Series part | Destination | Enable |
|---|---|---|---|---|---|
| pin 2, `1A1` | Agon `PC4` | pin 18, `1Y1` | 220 ohm | P4 GPIO32, `D4` | pin 1, `PAR_FWD_OE_N` |
| pin 4, `1A2` | Agon `PC5` | pin 16, `1Y2` | 220 ohm | P4 GPIO10, `D5` | pin 1, `PAR_FWD_OE_N` |
| pin 6, `1A3` | Agon `PC6` | pin 14, `1Y3` | 220 ohm | P4 GPIO33, `D6` | pin 1, `PAR_FWD_OE_N` |
| pin 8, `1A4` | Agon `PC7` | pin 12, `1Y4` | 220 ohm | P4 GPIO9, `D7` | pin 1, `PAR_FWD_OE_N` |

Tie unused bank-2 enable pin 19 directly to `AGON_3V3`, tie inputs 17, 15,
13, and 11 to GND, and leave outputs 3, 5, 7, and 9 unconnected.

### U3 — `SN74LV125AN`, UART return drivers

`U3` is powered by `AGON_3V3`; pin 14 is VCC and pin 7 is GND.

| Channel | OE_N | Input | Output | Series part | Destination |
|---|---|---|---|---|---|
| 1 | pin 1, `UART_RETURN_OE_N` | pin 2, P4 GPIO12 UART2 TX | pin 3 | 220 ohm | Agon pin 18, `PC1/RXD1` |
| 2 | pin 4, `UART_RETURN_OE_N` | pin 5, P4 GPIO11 UART2 RTS | pin 6 | 220 ohm | Agon pin 20, `PC3/CTS1` |

Tie unused channel-3/channel-4 OE pins 10 and 13 directly to `AGON_3V3`, tie
their input pins 9 and 12 to GND, and leave output pins 8 and 11 unconnected.

### U4 — `SN74LV125AN`, cross-domain low-only controls

`U4` is powered by `P4_3V3`; pin 14 is VCC and pin 7 is GND. Tie all four data
inputs (pins 2, 5, 9, and 12) to GND. Each P4 control GPIO has a 10-kilohm
pull-up to `P4_3V3`; low requests the associated sink and high or high-impedance
releases it.

| U4 channel | P4 owner and OE_N input | Low-only output | Agon-domain disposition |
|---|---|---|---|
| 1 | GPIO15 / EXT1-16 to pin 1 | pin 3 | `UART_FWD_OE_N`, 10-kilohm pull-up to `AGON_3V3`, U1 pin 1 |
| 2 | GPIO17 / EXT1-18 to pin 4 | pin 6 | `PAR_FWD_OE_N`, 10-kilohm pull-up to `AGON_3V3`, U1 pin 19 and U2 pin 1 |
| 3 | GPIO21 / EXT2-12 to pin 10 | pin 8 | `UART_RETURN_OE_N`, 10-kilohm pull-up to `AGON_3V3`, U3 pins 1 and 4 |
| 4 | GPIO20 / EXT2-13 to pin 13 | pin 11 | through 220 ohm to Agon `PD4/READY_N`, with 10-kilohm receiver-side pull-up to `AGON_3V3` |

`U4` is not represented as a generic push-pull level shifter. Grounding each A
input and controlling OE_N is part of the electrical contract. Substituting an
`SN74HC125N` is prohibited for either-order-power work because the HC part does
not provide the selected `Ioff` contract.

## Bias and series population

Every actively driven cross-board transport output receives one 220-ohm series
part at its driving-buffer output: `D0..D7`, `CLOCK`, `VALID_N`, both P4 UART
return outputs, and the `READY_N` sink. This is the initial fitted value. Keep
the footprints individually replaceable because final values require scope and
logic-analyzer qualification on the actual carrier and harness.

P4-side receive defaults are:

| P4 input | Bias | Reason while forward buffers are disabled |
|---|---|---|
| GPIO22 / `D0` / UART RX | 47 kilohm to `P4_3V3` | UART idle high |
| GPIO12 / `D1` / UART TX pin | 47 kilohm to `P4_3V3` | UART TX idle high before P4 owns output |
| GPIO23 / `D2` / UART CTS | 47 kilohm to `P4_3V3` | active-low CTS safely deasserted |
| GPIO11 / `D3` / UART RTS pin | 47 kilohm to `P4_3V3` | active-low RTS safely deasserted before P4 owns output |
| GPIO32, GPIO10, GPIO33, GPIO9 / `D4..D7` | 47 kilohm each to GND | deterministic inactive data value |
| GPIO14 / `CLOCK` | 10 kilohm to GND | no false sampling edge |
| GPIO13 / `VALID_N` | 10 kilohm to `P4_3V3` | no record accepted |
| Agon `PD4` / `READY_N` | 10 kilohm to `AGON_3V3` | Extender not ready |

The P4 datasheet specifies about 50 nA maximum input leakage at 3.3 V, so a
47-kilohm bias has ample static margin. The UART-capable pins use safe UART
idle/deasserted levels rather than an arbitrary parallel data value; `VALID_N`
prevents those inactive values from becoming a record.

## Mode and ownership truth table

All four P4 control GPIOs are active low. EDP/P4 firmware drives them high or
leaves them as pulled-up inputs before any endpoint mux is changed. EMOS owns
the eZ80 Port C/Port D direction and alternate-function configuration. The
interface ICs execute only the electrical enable state; they do not authorize
a mode transition.

| State | GPIO15 UART forward | GPIO17 parallel-only | GPIO21 UART return | GPIO20 READY | Enabled electrical paths |
|---|---:|---:|---:|---:|---|
| Power-off, P4 reset, uncommitted, or Legacy | 1 | 1 | 1 | 1 | none; `READY_N` released high |
| Exclusive Compatible | 0 | 1 | 0 | 1 | full-duplex four-wire UART |
| Exclusive Extended, UART epoch | 0 | 1 | 0 | 1 | full-duplex four-wire UART |
| Exclusive Extended, parallel epoch not admitted | 0 | 0 | 1 | 1 | `D0..D7`, `CLOCK`, `VALID_N`; not ready |
| Exclusive Extended, admitted parallel epoch | 0 | 0 | 1 | 0 | forward parallel path plus asserted `READY_N` |
| Any direction or mux transition | 1 | 1 | 1 | 1 | all drivers released before reconfiguration |

`0` means the P4 GPIO enables a grounded `U4` channel and therefore pulls the
named Agon-domain active-low net low. `1` includes explicit high and reset/high-
impedance with the external pull-up in control.

The supported transition invariant is break-before-make:

1. EDP/P4 firmware releases `READY_N` and drives GPIO15, GPIO17, and GPIO21
   high.
2. The hardware pull-ups place all three transport-driver groups in high
   impedance.
3. EMOS/eZ80 firmware and EDP/P4 firmware complete their agreed quiescence and
   pin-mux changes.
4. EDP/P4 firmware enables only the destination state from the table.
5. For parallel operation, EDP/P4 firmware asserts `READY_N` only after its
   receiver is armed.

The exact EMOS/EDP transaction that proves both processors reached steps 2 and
3 remains PORT-008 work. Hardware qualification must measure the minimum
disable and settling interval; this proposal does not invent a timing number.

## Power and reset analysis

| Condition | Hardware result |
|---|---|
| Both boards off | No powered driver. Positive rails remain separate. |
| Agon on, P4 off | `U1`--`U3` are powered, but Agon-side OE pull-ups disable every output; powered-off `U4` is high impedance through `Ioff`. |
| P4 on, Agon off | `U1`--`U3` are powered down and their `Ioff` outputs isolate the P4 pins; `U4` controls default high and releases every output. |
| P4 reset or firmware not running | Four P4-domain control pull-ups disable all `U4` sinks, so all Agon-facing drivers remain disabled without software action. |
| Agon reset while P4 remains in an active mode | **Not solved by this topology alone.** A stale low P4 enable can persist while eZ80 pin ownership resets. PORT-008 and QUAL-002 must either prove a bounded safe recovery using an Agon-reset/host-arm indication or require a hardware gate/revision. |
| Legacy with arbitrary user GPIO configuration | Drivers are high impedance, but buffer input capacitance, leakage, and the `READY_N` pull-up remain physically attached. More importantly, powered `U1`/`U2` CMOS inputs can be left floating when a legacy application configures the associated eZ80 pins as undriven inputs; TI explicitly forbids undefined non-bus-hold inputs. This is not a claim of perfect electrical transparency or a final V1 disposition. |

The last two rows are deliberate limits on r02 qualification. Calling this a
complete V1 carrier while leaving them implicit would contradict the project's
Legacy-absence and reset obligations. The topology is frozen for a controlled
beta transport and remains the recommended V1 transport core; arbitrary Legacy
use must not be enabled until the floating-input issue is removed. Final V1
promotion depends on resolving whether hardware arming, switchable buffer
power or isolation, weak defined input bias, or transport-pin pass-through is
required.

## Timing and throughput basis

1. Official VDP v2.16.0 uses 1,152,000-baud `Serial2`, 8N1, hardware RTS/CTS,
   a 256-byte receive buffer, and a hardware-flow threshold of 64 in the called
   setup path.
2. `SN74LVC244A` specifies a maximum propagation delay of 5.9 ns at 3.3 V;
   `SN74LV125A` is a 5-to-10-ns-class device. These delays are small compared
   with an approximately 868 ns UART bit period.
3. The predecessor's physical PRX-06 sweep used 220-ohm series resistance and
   passed every P4-received byte at approximately 0.84 MiB/s useful endpoint
   payload, with an independently observed zero-delay wire rate of about
   0.856 MiB/s. That is Agon-specific evidence for the initial population, not
   qualification of this changed four-IC topology.
4. TI recommends source-series damping for longer CMOS interconnects and says
   the resistance must be selected against driver and transmission-line
   impedance. The inherited 220-ohm value is therefore retained as a measured
   candidate and must be checked for rise/fall time, threshold margin,
   overshoot, and setup/hold at the far endpoint.

## Prototype BOM basis

| Quantity | Candidate part/value | Role |
|---:|---|---|
| 2 | TI `SN74LVC244AN`, 20-pin PDIP | Two independently enabled four-bit forward banks per package |
| 2 | TI `SN74LV125AN`, 14-pin PDIP | UART return drivers and four low-only cross-domain controls |
| 13 | 220 ohm, 1% | Series protection/damping on every driven transport output |
| 8 | 47 kilohm, 1% | P4 data/UART inactive bias |
| 7 | 10 kilohm, 1% | Three Agon-domain OEs, four P4 control inputs |
| 3 | 10 kilohm, 1% | `CLOCK`, `VALID_N`, and `READY_N` idle bias |
| 4 | 100 nF ceramic | One local bypass per IC |
| 2 | 1 uF ceramic or low-ESR electrolytic | One local bulk part per positive domain |

The Author confirmed two `SN74LVC244AN` and two `SN74LV125AN` through-hole
parts physically in hand and reallocated to Extender on 2026-08-28. This
confirms availability for the controlled prototype. It does not substitute for
continuity checks or electrical qualification.

## Test-access contract

The controlled schematic and carrier layout shall expose test access without
making a probe part of the operating circuit:

1. provide one labeled point for `AGON_3V3`, one for `P4_3V3`, and at least
   three nearby ground-return points;
2. provide accessible points on both sides of every 220-ohm series part so a
   qualification run can distinguish source waveform, buffer behavior, series
   drop, and receiver waveform;
3. provide points for `UART_FWD_OE_N`, `PAR_FWD_OE_N`,
   `UART_RETURN_OE_N`, and the P4-side control of `READY_N`;
4. provide receiver-side points for `D0..D7`, `CLOCK`, `VALID_N`, and
   `READY_N`; and
5. place no mandatory test point or indicator load directly on a timing net
   unless that load is included in the electrical authority and qualification.

The breadboard prototype may satisfy these requirements with directly
accessible IC, resistor, and header rows. A PCB projection shall use stable
test-point component references and include their terminals in the canonical
connectivity model.

## Provenance and design influence

### Agon- and project-specific authorities

| ID | Source | Facts used |
|---|---|---|
| `A01` | [Official Agon GPIO documentation at commit `f9806bd`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/GPIO.md) | Light 2 has a 34-pin header; UEXT duplicates rather than adds eZ80 pins. |
| `A02` | [Olimex AgonLight2 source at commit `b7f2a21`](https://github.com/OLIMEX/AgonLight2/tree/b7f2a21c282813efd8cdf26573eb5126876432a8), Rev B schematic SHA-256 `5019caa700d034bd16b720184f291c9768be3dba62734f0569887ee19704953c` | Header identities, common 3.3 V logic rail, and eZ80 Port C/Port D exposure. |
| `A03` | [Zilog `PS0153`](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf), revision `PS015317-0120`, local SHA-256 `9d64cfd5e75e50b009028f75ec6a2377ee1cf3721443715d32a78a0d920a71ba` | `PC0/TXD1`, `PC1/RXD1`, active-low `PC2/RTS1`, active-low `PC3/CTS1`, UART and GPIO electrical roles. |
| `A04` | Official MOS v3.0.2 commit `8336409`: [`src/uart.c`](https://github.com/AgonPlatform/agon-mos/blob/v3.0.2/src/uart.c) and [`src/serial.asm`](https://github.com/AgonPlatform/agon-mos/blob/v3.0.2/src/serial.asm) | UART1 pin setup; software waits while `PC3/CTS1` is high; UART1 setup does not configure `PC2/RTS1`. |
| `A05` | Official VDP v2.16.0 commit `c7ac293`: [`video/agon.h`](https://github.com/AgonPlatform/agon-vdp/blob/v2.16.0/video/agon.h) and [`video/vdp_protocol.h`](https://github.com/AgonPlatform/agon-vdp/blob/v2.16.0/video/vdp_protocol.h) | `Serial2`, 1,152,000 baud, 8N1, RX/TX/CTS/RTS relation, hardware flow control, default setup behavior. |
| `A06` | [Olimex ESP32-P4-DevKit source at commit `4b45361`](https://github.com/OLIMEX/ESP32-P4-DevKit/tree/4b453612bd72e2b83b49cb1156de93f655b8aec4), Rev D1 schematic SHA-256 `addf0e18dd913b36a47864832adcb413eeeab68ebec0bb0fbe3b5c8b60bd930e` | Exact EXT1/EXT2 pin mapping and board-owned facilities. |
| `A07` | `hardware/designs/light2-harness-r01/profile.yaml` and `legacy-evidence/prx-06-results.md` | Physically exercised P4 mapping, 220-ohm predecessor population, control polarity, and measured parallel throughput. |
| `A08` | `SETUP-006-D004` through `D007` | Preserved P4 GPIOs, MOD-WIFI reservation, beta/V1 boundary, and inspected GPIO23/R31 state. |

### Primary vendor sources

| ID | Source | Facts used |
|---|---|---|
| `V01` | [ESP32-P4 hardware-design checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32p4/schematic-checklist-esp32p4.html) | Five HP UARTs with CTS/RTS; UART1--UART4 recommended for application serial; GPIO-matrix routing; GPIO34--GPIO38 strapping restrictions; external bias for high-impedance pins. |
| `V02` | [ESP-IDF 5.5 ESP32-P4 UART API](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/uart.html) | Arbitrary UART signal assignment with `uart_set_pin()`, hardware RTS/CTS, GPIO-matrix suitability below extreme rates, and contention warning. |
| `V03` | [ESP32-P4 Series Datasheet v0.7](https://documentation.espressif.com/esp32-p4_datasheet_en.html) | 3.3 V GPIO thresholds and currents, approximately 50 nA input leakage, approximately 45-kilohm internal weak pulls, and pin restrictions. |
| `V04` | [TI `SN74LVC244A` datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf) | Two four-bit active-low-OE banks, 1.65--3.6 V operation, 5.5 V-tolerant inputs, 5.9 ns maximum propagation at 3.3 V, `Ioff`, PDIP `SN74LVC244AN`. |
| `V05` | [TI `SN74LV125A` datasheet](https://www.ti.com/lit/ds/symlink/sn74lv125a.pdf) | Individually enabled non-inverting three-state channels, 2--5.5 V operation, mixed-voltage ports, `Ioff`, PDIP `SN74LV125AN`. |
| `V06` | [TI floating-CMOS-input guidance, SLVA746](https://www.ti.com/lit/an/slva746/slva746.pdf) | Non-bus-hold inputs must not float; unused inputs require a defined level; inactive I/O may require a pull. |
| `V07` | [TI logic design guide, SDYA002](https://www.ti.com/lit/an/sdya002/sdya002.pdf) | Source-series damping principle and the requirement to tune total source resistance to the physical interconnect. |
| `V08` | [TI standard-logic datasheet interpretation, SZZA036C](https://www.ti.com/lit/an/szza036c/szza036c.pdf) | Meaning and limits of `Ioff`, power-up three-state behavior, and OE-to-VCC pull-up practice. |

General internet examples were not used to select the topology. The design is
derived first from official Agon/Olimex hardware and firmware, then from the
exact TI and Espressif component contracts, with generic logic-design guidance
used only for bias, decoupling, and series-damping treatment.

## Review boundary

Review Gate 2 froze this topology and the 220-ohm R1--R13 population as
`light2-harness-r02`. The remaining numbered questions in
`docs/tasks/HW-001.md` concern the EMOS/EDP UART/parallel epoch contract and
the final V1 requirement for Legacy electrical absence. Construction and
qualification must preserve those as explicit limitations rather than treating
candidate identity as evidence that they have passed.
