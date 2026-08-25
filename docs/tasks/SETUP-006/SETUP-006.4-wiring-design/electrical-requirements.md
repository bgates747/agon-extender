# SETUP-006.4 electrical requirements and candidate allocation

## Status and interpretation

- State: task-local review candidate
- Physical assembly: unchanged
- Author's completed Fritzing source draft: wiring and geometry preserved;
  embedded UART1 labels corrected by CA-2026-08-25-001
- Fritzing `draft_v1` derivative: generated for Author review
- Immediate target: Exclusive Extended beta transport
- Separate deferred target: Exclusive Compatible stock UART

This review turns current firmware and mode requirements into electrical design
inputs. It does not approve a harness revision, claim that the assembled bench
matches the candidate, or authorize a physical test.

The generated `draft_v1` has separately been corrected and machine-audited as
a complete drawing of the controlled-power predecessor circuit under
AUDIT-002. It is evidence and a construction reference for that circuit, not a
claim that the fresh-design allocation below has already been drawn or
accepted.

The current `light2-harness-r01` pin map and predecessor runs are strong
evidence for the enhanced forward bus. They are not proof of assembled-system
safety and are not a stock-VDP UART design. The latter requires a later design
review after EMOS and EDP freeze its physical requirements.

## Pinned sources

1. Official VDP tag `v2.16.0`, commit
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`: `video/agon.h`,
   `video/vdp_protocol.h`, `video/vdu_sys.h`, and
   `video/vdu_stream_processor.h`.
2. Official MOS commit `5f67b1ca77eb7a77d3b37cc7b029db51f0d1548e`:
   `main.c`, `src/uart.c`, and `src/serial.asm`.
3. Olimex ESP32-P4-DevKit commit
   `4b453612bd72e2b83b49cb1156de93f655b8aec4`, Rev D1 schematic
   `HARDWARE/ESP32-P4-DevKit-Rev.D1/ESP32-P4-DevKit_Rev_D1.kicad_sch`.
4. Current project authorities: PORT-008, QUAL-002, the operating-mode audit,
   and `hardware/designs/light2-harness-r01/`.
5. TI's current SN74LV125A documentation identifies over-voltage-tolerant
   inputs and `Ioff` partial-power-down support. TI's SN74HC125 documentation
   identifies input clamp diodes and does not specify `Ioff`. At least four
   exact TI `SN74LV125AN` 14-PDIP parts are operator-confirmed on order. Receipt,
   physical count, and allocation to Extender remain unconfirmed because the
   separately ordered parts may be committed elsewhere.

## Contract layers

The phrase "compatible transport" must not collapse three different contracts:

1. **Application bytes:** EDP consumes the same VDU command bytes and emits the
   same VDP protocol packets as official VDP for retained functionality.
2. **EMOS behavior:** EMOS owns routing, response parsing, completion flags,
   sysvar updates, activation, committed mode, and recovery.
3. **Physical transport:** Exclusive Extended uses an eight-bit forward bus and
   a one-way UART return. It need not copy the onboard VDP's four-wire UART0
   circuit, but it must prove equivalent application-visible behavior, pacing,
   and recovery within the accepted mode contract.

Official VDP uses 1,152,000-baud 8-N-1 UART, begins with RTS flow control, and
can enable CTS/RTS full duplex. Official MOS UART0 provides RX, TX, RTS, and CTS
on Port D bits 0 through 3. Current official MOS UART1 provides PC0 TX and PC1
RX, while its hardware-flow helper configures PC3 only as CTS input; it does
not currently provide a UART1 RTS output on PC2. Exclusive Extended therefore
cannot assume that stock UART0 electrical flow control exists on UART1.

## Immediate beta signal inventory

### Mandatory conductors and local controls

| ID | Logical role | Agon/eZ80 endpoint | P4 endpoint in predecessor map | Actor and direction | Required behavior |
|---|---|---|---|---|---|
| `EE-D0` | Forward data bit 0 | PC0, header 17 | GPIO22, EXT2-11 | EMOS/eZ80 to EDP/P4 | Sampled only inside an admitted valid epoch; application-byte bit order remains exact. |
| `EE-D1` | Forward data bit 1 | PC1, header 18 | GPIO12, EXT1-13 | EMOS/eZ80 to EDP/P4 | Forward data outside the UART-return ownership epoch; PC1 becomes eZ80 UART1 RX for return. |
| `EE-D2` | Forward data bit 2 | PC2, header 19 | GPIO23, EXT2-10 | EMOS/eZ80 to EDP/P4 | Same as `EE-D0`; exact Rev D1 board must have DNP link R31 absent. |
| `EE-D3` | Forward data bit 3 | PC3, header 20 | GPIO11, EXT1-12 | EMOS/eZ80 to EDP/P4 | Same as `EE-D0`; PC3's UART1-CTS role does not itself throttle P4 return traffic. |
| `EE-D4` | Forward data bit 4 | PC4, header 21 | GPIO32, EXT2-9 | EMOS/eZ80 to EDP/P4 | Same as `EE-D0`. |
| `EE-D5` | Forward data bit 5 | PC5, header 22 | GPIO10, EXT1-11 | EMOS/eZ80 to EDP/P4 | Same as `EE-D0`. |
| `EE-D6` | Forward data bit 6 | PC6, header 23 | GPIO33, EXT2-8 | EMOS/eZ80 to EDP/P4 | Same as `EE-D0`. |
| `EE-D7` | Forward data bit 7 | PC7, header 24 | GPIO9, EXT1-10 | EMOS/eZ80 to EDP/P4 | Same as `EE-D0`. |
| `EE-CLOCK` | Forward sampling clock | PD5, header 14 | GPIO14, EXT1-15 | EMOS/eZ80 to P4 PARLIO | P4 samples on the selected edge. Predecessor evidence used falling edges; PORT-008 must freeze timing bounds. Idle Low is the current evidence-backed target. |
| `EE-VALID-N` | Forward record delimiter | PD7, header 16 | GPIO13, EXT1-14 | EMOS/eZ80 to P4 PARLIO | Active Low only around a finite admitted record. Idle High. No command semantics are encoded by the wire itself. |
| `EE-READY-N` | Forward admission/backpressure | PD4, header 13 | GPIO20, EXT2-13 | EDP/P4 to EMOS/eZ80 | Open-drain active Low only after P4 has mounted capacity for the next record. It has no reverse-UART, abort, or presence-announcement meaning. |
| `EE-UART-TX` | VDP protocol-packet return | PC1/UART1 RX, header 18 | predecessor used GPIO12 | EDP/P4 to EMOS/eZ80 | 1,152,000 baud, 8-N-1 target. Carries exact official VDP response packet bytes and no diagnostics. Driver remains disabled until EMOS and EDP have committed return ownership. |
| `EE-FWD-OE-N` | Forward isolation enable | no Agon conductor | predecessor GPIO15, EXT1-16 | EDP/P4 to forward interface buffers | Hardware defaults High/off. Firmware may enable only for a committed Exclusive Extended receive state. It is interface control, not application protocol. |
| `EE-REV-ENABLE` | Return isolation request | no Agon conductor | predecessor GPIO21, EXT2-12 | EDP/P4 to isolated return-enable stage | P4-side request defaults inactive. The isolated stage drives the Agon-domain active-low output-enable net only after EMOS has made PC1 an input and both processors commit the return epoch. |
| `EE-GND` | Signal reference | header 33 | a DevKit GND pin | physical wiring | Grounds are common for the interface. This does not join either board's positive supply rail. |

The forward record length, lower-layer framing/integrity scheme, exact timing,
return scheduling, and complete recovery state machine are intentionally not
invented here. PORT-008 Review Gate 1 owns those decisions. The first bounded
canary is the official General Poll command and its three-byte packet response:
packet type `0x80`, payload length `0x01`, and the echoed byte.

### Conditional conductor

`EE-UART-ALLOW-N` is a provisional eZ80-to-P4 return-pacing conductor. A
one-way 1,152,000-baud P4 transmitter cannot rely on UART1's current PC3 CTS
input to learn whether the eZ80 receive path has room. PORT-008 must first
determine whether bounded EMOS buffering and scheduled packet sizes are
sufficient without a wire. If not, an explicit EMOS-generated clearance line
is preferable to pretending stock hardware flow control exists. PD6/header 15
and P4 GPIO17/EXT1-18 are a geometrically convenient uncommitted pair, not an
accepted assignment.

### Explicitly absent from the beta inventory

1. No high-speed reverse parallel bus.
2. No direct onboard-VDP-to-EDP connection.
3. No P4-to-Agon reset actuator requirement.
4. No physical keyboard or mouse connection to Extender.
5. No second discovery or test-only wire protocol.
6. No positive supply connection between independently powered Agon and P4
   rails.

## Rev D1 P4 fixed-function audit

The following results come from the official Rev D1 schematic connectivity,
not merely the GPIO alternate-function names printed beside the chip pins.

| Facility | Physical P4 resources on Rev D1 | Effect on current enhanced map |
|---|---|---|
| Ethernet | PHY uses GPIO28-GPIO31, GPIO34, GPIO35, and GPIO49-GPIO52 for its selected RMII data, control, clock, reset, MDC, and MDIO nets. GPIO23 can be connected to RMII clock only through DNP resistor R31. | No populated-net conflict with GPIO9-GPIO17, GPIO20-GPIO23, GPIO32, or GPIO33. Confirm R31 is absent on the exact DevKit before qualifying GPIO23. GPIO32/33's printed EMAC alternatives are not wired to the onboard PHY. |
| Onboard microSD | SD1 data/clock/command and power use GPIO39-45. Card detect reaches GPIO3. | No conflict. Preserve GPIO3 and the internal GPIO39-45 assignments for PORT-007. The header pins labeled SPI are not the onboard microSD bus. |
| MIPI DSI/CSI | Data and clock use dedicated MIPI pins. Both connectors share control I2C on GPIO7/GPIO8; CSI also has optional control nets. | No conflict. Preserve GPIO7/GPIO8 and the MIPI connectors for later local display/camera work. |
| pUEXT / MOD-WIFI | pUEXT exposes power, UART0 on GPIO37/GPIO38, I2C on GPIO7/GPIO8, and SPI on GPIO4/GPIO5/GPIO53/GPIO54. | No conflict. Preserve all eight pUEXT signal GPIOs so the planned MOD-WIFI-ESP8266 attachment remains possible without redesigning the enhanced bus. |
| USB Serial/JTAG | Connector uses GPIO24/GPIO25 for USB1P1 port 0. | No conflict and must remain accessible for flashing/debugging. |
| Exposed USB interfaces | EXT2 exposes USB1P1 port 1 on GPIO26/GPIO27 and dedicated USB `DP`/`DM`. | No conflict; do not appropriate these as casual GPIOs. |
| User LED and reset | User LED is on GPIO2. `ESP_EN` is on EXT2-14 and the reset button. | No conflict. Preserve them and do not confuse `ESP_EN` with an Agon reset requirement. |

### Candidate-pin result

1. The predecessor's D0-D7, CLOCK, VALID_N, READY_N, FWD_OE_N, and REV_OE_N
   P4 assignments have no identified populated peripheral collision on Rev D1.
2. GPIO23 remains conditional on physical confirmation that DNP option R31 is
   unpopulated.
3. A dedicated return-UART TX on GPIO16 would avoid changing GPIO12 between
   PARLIO input and UART output. This is the recommended fresh-design
   candidate and deliberately departs from the predecessor experiment.
4. GPIO17 is retained only as a provisional return-pacing candidate until
   PORT-008 decides whether a physical clearance signal is required.
5. GPIO18, GPIO19, GPIO46-GPIO48, and the exposed USB pins remain uncommitted;
   this review does not consume every spare header pin speculatively.

### Discovered diagram defect

The SETUP-006.4 audit found that P4 part `r04` listed GPIO17 at EXT1-17 and
GPIO16 at EXT1-18. The official Rev D1 schematic establishes the opposite:
EXT1-17 is GPIO16 and EXT1-18 is GPIO17. Connector geometry was unaffected.
The generator and canonical scaffold use corrected P4 part `r05`. The Author's
completed source draft retains embedded P4 `r04` as provenance. At the Author's
direction, generated `draft_v1` embeds `r05` and therefore prints the corrected
P4 names. CA-2026-08-25-001 separately corrected the source draft's embedded
Agon UART1 header and label-bank parts without changing its P4 part, wiring, or
geometry.

## Electrical ownership and conditioning candidate

### Power-domain rule

The Agon 3.3 V rail and P4 3.3 V rail remain separate. The wiring uses common
ground and may use each rail to power only the interface logic assigned to
that rail. It never ties the two positive rails together.

The nominal logic level is 3.3 V on both endpoints, so ordinary level
translation is not required. Partial-power-down isolation is required because
either board may be powered while the other is off. A series resistor alone is
not isolation and must not be cited as protection against back-powering.

### Forward bank: Agon to P4

1. Route D0-D7, CLOCK, and VALID_N through non-inverting three-state buffers
   powered from the P4 3.3 V rail.
2. Require the exact buffer device to specify `Ioff` partial-power-down
   behavior and tolerate a valid Agon-side High while buffer VCC is 0 V. The
   TI SN74LV125A family is the present through-hole candidate. The on-hand
   SN74HC125N lacks a specified `Ioff` contract and remains restricted to old
   controlled-power evidence.
3. Tie all used forward output enables to `EE-FWD-OE-N`. Pull that net High to
   P4 3.3 V so the buffers remain disabled through P4 power-up, reset, GPIO
   release, and firmware failure-to-initialize. P4 GPIO15 may pull it Low only
   after EDP has armed an admitted Exclusive Extended receive state.
4. Put the current evidence-backed 220-ohm series element in every signal path,
   pending signal-integrity qualification. Keep D0-D7 ordered and put CLOCK
   beside an accessible ground return rather than in a long parallel bundle.
5. Define P4-side idle state independently of a powered Agon: pull VALID_N High
   and CLOCK Low on the P4 side of the disabled buffers. Data bits need no
   semantic default while VALID_N is inactive.
6. If PORT-008 selects `EE-UART-ALLOW-N`, carry it through the same protected
   forward topology rather than adding an unbuffered exception.

This topology consumes ten channels now, or eleven with return pacing. Three
quad packages provide twelve channels and leave either two or one unused
channel. Every unused input and output-enable input must be terminated per the
selected device's data sheet; no CMOS input floats.

### Return bank: P4 to Agon

1. Route P4 return UART TX through a non-inverting three-state buffer powered
   from the Agon 3.3 V rail. The device must specify `Ioff` and an input range
   that safely accepts P4 High while the Agon-powered buffer is off.
2. Pull the return buffer's `EE-REV-OE-N` output enable High to Agon 3.3 V. Do not connect
   that pulled-up node directly to an unpowered P4 GPIO: use a transistor or
   another reviewed partial-power-down control stage so P4 GPIO21's
   `EE-REV-ENABLE` request can assert it without acquiring an Agon-to-P4
   phantom-power path.
3. Use P4 GPIO16/EXT1-17 as the fresh-design UART TX candidate. Keep the
   predecessor's GPIO12 as PARLIO D1 input. Separating these nodes removes P4
   GPIO12 direction and pin-mux switching and makes the physical ownership
   boundary easier to inspect and test.
4. Retain a candidate 220-ohm series element between the return buffer output
   and Agon PC1. Its target-speed edge quality and UART margin require scope
   and endpoint qualification.
5. EMOS changes PC1 from parallel output to UART1 RX before EDP/P4 enables the
   return driver. EDP/P4 disables the return driver after the bounded packet or
   timeout before EMOS restores PC1 as parallel output. Both processors own a
   side of this handshake; neither may infer completion from elapsed time
   alone in the production contract.

### READY_N

Implement READY_N as a physical open-collector or open-drain stage rather than
depending on a P4 push-pull pin configured in software to behave as open drain.
Pull the Agon-side net High to the Agon 3.3 V rail. The P4 control side must
default inactive when P4 power or firmware is absent and must not receive
Agon-side pull-up current when P4 is off. A small NPN or NMOS stage is the
present candidate; part, bias values, polarity, and transition margin remain a
schematic-level selection.

### Reset, power-order, and failure states

| State | Required physical result |
|---|---|
| Both boards off | No energized path. |
| Agon on, P4 off | Forward-buffer inputs and return-buffer output present only high-impedance loads; return and READY drivers are off; no current enters P4 GPIO or rail through interface pull-ups. |
| P4 on, Agon off | Forward buffers may power but can drive only P4-side pins; return buffer is unpowered and `Ioff`-isolated; READY output stage remains non-sourcing; no current enters eZ80 or Agon rail. |
| P4 boot/reset, Agon in Legacy | Every P4-to-Agon driver remains hardware-disabled and READY_N remains released. P4 emits no presence traffic. |
| Late P4 power-on | Hardware remains passive until EMOS explicitly initiates discovery and both processors commit activation. No Agon reset is required. |
| P4 reset/fault during Extended | Forward admission is withdrawn, return output converges disabled, and EMOS times out to the accepted visible failure/recovery path. |
| Agon reset/power loss during Extended | Agon-powered return buffer turns off on power loss. A powered reset leaves PC1 non-driving; bounded EDP response epochs and timeout must converge the P4 return driver off before a later EMOS activation. |

No P4-to-Agon reset actuator is selected. A future need for an Agon-reset
observation input must be justified by recovery testing; it must not be
confused with the separate Pi 5 unattended bench-reset fixture.

### Construction and measurement provisions

1. Put 100 nF local bypass capacitance at every buffer package and provide a
   reviewed bulk-capacitor position per power domain.
2. Label Agon-domain and P4-domain 3.3 V nodes distinctly. Provide separate
   test points and never use rail color alone as connectivity authority.
3. Provide accessible test points for D0-D7, CLOCK, VALID_N, READY_N, UART TX,
   every output-enable net, both 3.3 V domains, and several nearby grounds.
4. Keep test points independent of logic-analyzer channel assignments. The
   eight-channel analyzer will require multiple controlled captures or an
   endpoint integrity oracle for full-bus claims.
5. Use an oscilloscope for UART edge/margin, CLOCK integrity, pull-up fall/rise
   time, and suspected contention. Use a meter/current-limited source for
   powered-off leakage and phantom-power checks. A digital analyzer cannot
   qualify analog safety.
6. Preserve access to P4 USB Serial/JTAG, Ethernet, reset, boot, pUEXT,
   microSD, and MIPI connectors in the physical layout.

## Candidate allocation for diagram development

This table is a review proposal, not authority to wire the bench.

| Net | Agon pin | P4 pin | Interface stage | Candidate state |
|---|---|---|---|---|
| D0 | 17 / PC0 | EXT2-11 / GPIO22 | P4-powered `Ioff` buffer + 220 ohm | retain |
| D1 | 18 / PC1 | EXT1-13 / GPIO12 | P4-powered `Ioff` buffer + 220 ohm | retain |
| D2 | 19 / PC2 | EXT2-10 / GPIO23 | P4-powered `Ioff` buffer + 220 ohm | retain after R31 check |
| D3 | 20 / PC3 | EXT1-12 / GPIO11 | P4-powered `Ioff` buffer + 220 ohm | retain |
| D4 | 21 / PC4 | EXT2-9 / GPIO32 | P4-powered `Ioff` buffer + 220 ohm | retain |
| D5 | 22 / PC5 | EXT1-11 / GPIO10 | P4-powered `Ioff` buffer + 220 ohm | retain |
| D6 | 23 / PC6 | EXT2-8 / GPIO33 | P4-powered `Ioff` buffer + 220 ohm | retain |
| D7 | 24 / PC7 | EXT1-10 / GPIO9 | P4-powered `Ioff` buffer + 220 ohm | retain |
| CLOCK | 14 / PD5 | EXT1-15 / GPIO14 | P4-powered `Ioff` buffer + 220 ohm; P4-side pull-down | retain |
| VALID_N | 16 / PD7 | EXT1-14 / GPIO13 | P4-powered `Ioff` buffer + 220 ohm; P4-side pull-up | retain |
| READY_N | 13 / PD4 | EXT2-13 / GPIO20 | isolated open-collector/drain; Agon-side pull-up | replace direct GPIO path |
| UART return TX | 18 / PC1 | EXT1-17 / GPIO16 | Agon-powered `Ioff` buffer + 220 ohm; isolated OE | replace predecessor GPIO12 TX |
| FWD_OE_N | none | EXT1-16 / GPIO15 | P4-side pull-up; common forward-buffer enable | retain role, expand scope |
| REV_ENABLE | none | EXT2-12 / GPIO21 | isolated control into Agon-domain `REV_OE_N` pull-up | retain pin, replace direct control |
| UART_ALLOW_N | 15 / PD6 | EXT1-18 / GPIO17 | protected forward input if selected | reserve only |
| Signal ground | 33 / GND | one or more DevKit GND pins | direct common reference | retain |
| Agon logic rail | 34 / +3.3 V | no P4 rail connection | powers Agon-side return buffer and pull-ups | separate wire/domain |
| P4 logic rail | none | EXT1-1 / +3.3 V | powers P4-side forward buffers and pulls | separate wire/domain |

## Qualification dependencies

1. PORT-008 must freeze record delimitation, lengths, timing, return ownership,
   pacing, timeout, recovery, and the General Poll vertical-slice procedure.
2. A new harness revision must encode the accepted schematic and connectivity;
   `light2-harness-r01` must remain unchanged as predecessor evidence.
3. QUAL-002 must approve the power/reset state matrix and the instrumentation
   plan before either-order power or fault tests.
4. The candidate must pass continuity and passive resistance checks before
   either board is attached, then current-limited single-board power checks,
   then dual-board idle checks, before active transport traffic.
5. Target-speed UART and forward-bus qualification must identify exact buffer
   manufacturer/orderable part, resistor values, wire lengths, board specimen,
   firmware builds, EMOS build, procedure, fixture, and run IDs.

## Questions for Author disposition

Discussion of Q001 exposed a prerequisite GPIO-budget and compatibility issue.
The active reasoning and unresolved alternatives are preserved in
`gpio-ownership-and-passthrough-discussion.md`. Q001 is paused until that
discussion establishes an acceptable P4 user reserve and future-feature
budget; none of its provisional directions is an accepted allocation.

0. **Q000 — GPIO budget and passthrough boundary:** The first beta dedicates
   the eleven eZ80 extended-transport pins while that transport is active and
   omits passthrough switching and event virtualization. Establish the
   permanent P4 user-GPIO reserve, optional Wi-Fi and future-link reservations,
   exact beta direct-GPIO compatibility carve-out, and practical provisions
   that avoid needlessly foreclosing a possible v1 mode-switched replicated
   eZ80 header before consuming another convenience pin or fixing the carrier
   layout.

1. **Q001 — Dedicated P4 UART TX:** Accept GPIO16 as return TX, leaving GPIO12
   permanently as PARLIO D1 input? Recommendation: yes; this removes needless
   P4 pin-mux and electrical turnaround while preserving the Agon PC1 contract.
2. **Q002 — Return pacing wire:** For the first General Poll beta, omit
   `UART_ALLOW_N` but reserve PD6/GPIO17 and physical routing space until
   PORT-008 measures whether EMOS buffering is sufficient? Recommendation: yes;
   do not invent a flow-control wire before the receiver needs it.
3. **Q003 — Buffer architecture:** Accept separate P4-powered forward and
   Agon-powered return buffer banks with `Ioff`, replacing the one-package HC125
   experiment? Recommendation: yes; it is the cleanest either-order-power
   boundary identified in this review.
4. **Q004 — READY_N isolation:** Replace direct P4 open-drain GPIO wiring with
   a discrete isolated open-collector/drain stage? Recommendation: yes; safe
   release must not depend solely on P4 GPIO initialization.
5. **Q005 — Pin-map caveat:** Retain GPIO23 for D2 only after inspecting the
   exact Rev D1 board to confirm R31 is unpopulated? Recommendation: yes; the
   official schematic marks it DNP, but specimen verification is cheap.
6. **Q006 — Series resistance:** Carry 220 ohms as the beta candidate on each
   push-pull forward signal and UART return, subject to scope qualification at
   target speed? Recommendation: yes; existing forward evidence is favorable
   and the value remains explicitly provisional for UART. READY_N's open-
   collector stage requires its own edge and current analysis.
