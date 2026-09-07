# Stage 02 — Startup and fail-safe bias test sheet

**Superseded draft; hardware work on hold as of 2026-09-07.** Retained for
review only. The Author rejected R32–R41 additions solely for intermediate
powered tests. This document is not an executable construction/test procedure.

**DRAFT — no measurements recorded.** This is the worksheet for the expanded
[wiring-order step 02](../02-startup-and-fail-safe-bias-network.md), covering
resistor installation, continuity and settled idle voltages. Its powered scope
requires the proposed permanent input-bias additions to be accepted into a
successor circuit. Frozen r02 alone does not meet that prerequisite.
Procedure artifact ID/revision: not yet assigned or approved. The stage number
comes from the wiring order; it is not a procedure revision or a run ID.

Existing circuit basis: [r02 connectivity](../../connectivity.yaml).
Tested successor circuit identity/model/commit: unassigned pending HW-001-Q011;
record the accepted successor authority in the result before execution.
Construction view: [02 KiCad schematic](../../signal-views/generated/02_schematic_startup-and-fail-safe-bias-network.kicad_sch)
and [SVG](../../signal-views/generated/02_schematic_startup-and-fail-safe-bias-network.svg).
Retain stage 01 power, ground, and bypass wiring. Its
[previous observations](01-power-domains-results-2026-09-04.md) are preliminary;
repeat the rail checks after adding this wiring.

## 1. Record the actual bench state

Fill this section in the result copy before measurements. Keep private board,
host, and USB identities in the ignored root `HARDWARE.local.md`; use aliases
here. A blank field means unrecorded, not passed.

| Item | Record |
| --- | --- |
| Operator; local date/time and UTC start | — |
| Result/run ID; procedure identity and source commit | — |
| Hardware and assembly identities; as-built photo/map reference | — |
| Installed wiring-order steps, permanent added parts and omitted endpoints | — |
| Meter model, DC input impedance, range, accuracy; lead resistance | — |
| Agon power source; P4 power source; attached USB/display/probe cables | — |
| Agon MOS/EMOS image and startup behavior; SD autoexec contents | — |
| P4 image/build/hash and how its installed identity was confirmed | — |
| Stage review / Author's execution authorization reference | — |
| Frozen-input profile check, if claiming qualification | — |

Use the [passive P4 diagnostic](../../../../../docs/tasks/QUAL-002/p4-passive-r01/README.md)
for the proposed idle measurements: GPIO 9–15, 17, 20–23, 32, and 33 are
input-only with internal pulls disabled after application setup. Confirm the
installed image; the September 4 deployment is historical evidence. Flashing
is a separate operation, not a step in this sheet. This diagnostic exercises
external bias, not production transport code.

The Agon must not launch an Extender transfer fixture or drive a net being
measured as passive. Record its actual GPIO state rather than assuming that
a visible MOS prompt proves it. No keyboard interaction is required; the
[active bench constraint](../../../../../docs/qualification/bench-constraints.md)
still applies. Keep P4 Ethernet disconnected for this scope and record every
other cable; an unexpected alternate power feed invalidates a single-domain
measurement.

## 2. Confirm powered inputs before applying power

The Author confirmed the ten U1/U2 input pins are presently unwired and
requires permanent parts only. The expanded step 02 proposes R32–R41 to hold
those inputs at defined levels before their Agon source wires are installed.
The [step-02 connection table](../02-startup-and-fail-safe-bias-network.md)
names each endpoint, bias direction, and later source connection.

These are proposed permanent additions, absent from r02. Record approval of
the successor circuit, its exact added parts and their unpowered checks before
using this powered section. Do not substitute temporary resistors or direct
rail jumpers. Keep the ten Agon source wires absent at this checkpoint.

| Proposed part / input | Value | Bias end | Fitted value / continuity |
| --- | --- | --- | --- |
| R32 / `U1.2` — D0 | 10 kohm | Agon rail | — |
| R33 / `U1.17` — D1 | 10 kohm | Agon rail | — |
| R34 / `U1.4` — D2 | 10 kohm | Agon rail | — |
| R35 / `U1.15` — D3 | 10 kohm | Agon rail | — |
| R36 / `U2.2` — D4 | 10 kohm | Ground | — |
| R37 / `U2.4` — D5 | 10 kohm | Ground | — |
| R38 / `U2.6` — D6 | 10 kohm | Ground | — |
| R39 / `U2.8` — D7 | 10 kohm | Ground | — |
| R40 / `U1.13` — CLOCK | 10 kohm | Ground | — |
| R41 / `U1.11` — VALID_N | 10 kohm | Agon rail | — |

The [TI input requirement](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf)
applies with output banks disabled as well as enabled. All ten resistors
remain fitted in subsequent stages and the finished proposed circuit.

Also verify the connections already selected by the two views:

1. Ground: `U1.6`, `U1.8`, `U1.10`; `U2.10`, `U2.11`, `U2.13`, `U2.15`,
   `U2.17`; `U3.7`, `U3.9`, `U3.12`; `U4.2`, `U4.5`, `U4.7`, `U4.9`,
   `U4.12`.
2. Agon rail: `U1.20`, `U2.20`, `U3.14`; permanently disabled spare banks at
   `U2.19`, `U3.10`, `U3.13`.
3. P4 rail: `U4.14`. U3's used data inputs, `U3.2` and `U3.5`, connect to
   the R15 and R17 bias nets in the table below.

## 3. Unpowered resistor and continuity checks

The operator removes all board power and alternate power feeds, confirms both
rails have discharged in DC-voltage mode, and only then selects resistance or
continuity mode. Confirm IC orientation against the physical DIP drawing.

For each row, check the fitted resistor's value and both endpoint nets. The
listed IC/header terminals must have direct continuity to the specified signal
end; a connection through a resistor is not direct continuity. Compare wire
resistance with the shorted-lead reading and check for unintended bridges to
adjacent pins. Use markings or an isolated component measurement to establish
resistor value: connected boards and ICs can create parallel meter paths.

`J1.34` is `AGON_3V3`; `J2.1` is `P4_3V3`; `J1.33` and `J2.2` are common
ground. Connector pin numbers are the design's logical header terminals.

| Resistor | Value | Rail/ground end | Signal end and same-net terminals to check | Value / continuity result |
| --- | --- | --- | --- | --- |
| R14 | 47 kohm | `R14.1` → P4 rail | `R14.2`, `J3.11`, `R1.2` — GPIO22 / D0 / RX | — |
| R15 | 47 kohm | `R15.1` → P4 rail | `R15.2`, `J2.13`, `R2.2`, `U3.2` — GPIO12 / D1 / TX | — |
| R16 | 47 kohm | `R16.1` → P4 rail | `R16.2`, `J3.10`, `R3.2` — GPIO23 / D2 / CTS | — |
| R17 | 47 kohm | `R17.1` → P4 rail | `R17.2`, `J2.12`, `R4.2`, `U3.5` — GPIO11 / D3 / RTS | — |
| R18 | 47 kohm | `R18.2` → ground | `R18.1`, `J3.9`, `R5.2` — GPIO32 / D4 | — |
| R19 | 47 kohm | `R19.2` → ground | `R19.1`, `J2.11`, `R6.2` — GPIO10 / D5 | — |
| R20 | 47 kohm | `R20.2` → ground | `R20.1`, `J3.8`, `R7.2` — GPIO33 / D6 | — |
| R21 | 47 kohm | `R21.2` → ground | `R21.1`, `J2.10`, `R8.2` — GPIO9 / D7 | — |
| R22 | 10 kohm | `R22.2` → ground | `R22.1`, `J2.15`, `R9.2` — GPIO14 / CLOCK | — |
| R23 | 10 kohm | `R23.1` → P4 rail | `R23.2`, `J2.14`, `R10.2` — GPIO13 / VALID_N | — |
| R24 | 10 kohm | `R24.1` → Agon rail | `R24.2`, `J1.13`, `R13.1` — Agon PD4 / READY_N | — |
| R25 | 10 kohm | `R25.1` → Agon rail | `R25.2`, `U1.1`, `U4.3` — UART forward OE_N | — |
| R26 | 10 kohm | `R26.1` → Agon rail | `R26.2`, `U1.19`, `U2.1`, `U4.6` — parallel forward OE_N | — |
| R27 | 10 kohm | `R27.1` → Agon rail | `R27.2`, `U3.1`, `U3.4`, `U4.8` — UART return OE_N | — |
| R28 | 10 kohm | `R28.1` → P4 rail | `R28.2`, `J2.16`, `U4.1` — GPIO15 control | — |
| R29 | 10 kohm | `R29.1` → P4 rail | `R29.2`, `J2.18`, `U4.4` — GPIO17 control | — |
| R30 | 10 kohm | `R30.1` → P4 rail | `R30.2`, `J3.12`, `U4.10` — GPIO21 control | — |
| R31 | 10 kohm | `R31.1` → P4 rail | `R31.2`, `J3.13`, `U4.13` — GPIO20 control | — |

The view selects complete nets touching R14–R31, including the signal-side
ends of R1–R10 and R13. It does not select the opposite ends of those series
resistors or complete their transport lanes. In particular, `U4.11` to
`R13.2` is outside this view: a high reading at READY_N tests R24's bias,
not the complete READY sink path. Record any such wiring already fitted.

| Additional unpowered check | Reading / observation |
| --- | --- |
| Common-ground continuity across both boards and all IC grounds | — |
| Each positive rail reaches only its assigned IC supply and pull ends | — |
| P4 rail to ground; Agon rail to ground; rail to rail (record probe polarity and settling) | — |
| No unintended direct rail/ground or rail/rail bridge | — |
| Section 2 input-state record and all deviations attached | — |

## 4. Settled voltage measurements

After the stage's preparation and authorization are recorded, use DC-voltage
mode with the black lead at common ground and a meter input impedance of at
least 10 Mohm. Measure at the actual IC/header terminals as well as the
resistor ends; record separate readings where continuity or voltage differs.

Run each selected state from both boards off. Restore both boards to off
between states; wait for rails to discharge before a connection change. Allow
the powered board to reach its documented idle state before recording values.
Record the actual settling time. Do not toggle a control GPIO or bridge an OE
pin to ground during this test.

1. **P4 only:** Agon supply off; P4 passive application idle.
2. **Agon only:** P4 supply off; Agon input-state preparation from section 2
   in place. Check U3's R15/R17-biased inputs as well as U1/U2.
3. **Both:** both domains powered, Agon preparation retained and P4 passive.
   Record which board was powered first. This observes one settled endpoint;
   it does not qualify both power-up sequences or their transitions.

### Rail readings first

Provisional construction screening bands: a powered nominal 3.3 V rail is
3.135–3.465 V (3.3 V ±5%); an unpowered rail has absolute voltage below
0.20 V. These continue the stage-01 diagnostic expectations, not manufacturer
back-power-current limits or an accepted whole-product qualification limit.
Stop before signal measurements if a rail is outside the agreed band.

| Probe to common ground | P4 only (V) | Agon only (V) | Both (V) |
| --- | --- | --- | --- |
| `J2.1` P4 rail; each physical rail section | — | — | — |
| `U4.14` P4-domain VCC | — | — | — |
| `J1.34` Agon rail | — | — | — |
| `U1.20` VCC | — | — | — |
| `U2.20` VCC | — | — | — |
| `U3.14` VCC | — | — | — |
| Idle/settling time; board powered first | — | — | — |

### Bias readings

In the table, **P** means approximately the measured P4 rail, **A** the
measured Agon rail, and **0** common ground. Record volts alongside the printed
expectation. Proposed screening bands: within 0.20 V of the named powered
rail for P/A; absolute voltage below 0.20 V for 0. A deviation requires
investigation of loading, input state, wiring, and measurement uncertainty;
these bands are not a characterization of worst-case component leakage.

| Signal probe | P4 only: expected / V | Agon only: expected / V | Both: expected / V |
| --- | --- | --- | --- |
| `R14.2` — D0 / GPIO22 | P / — | 0 / — | P / — |
| `R15.2` — D1 / GPIO12; `U3.2` | P / — | 0 / — | P / — |
| `R16.2` — D2 / GPIO23 | P / — | 0 / — | P / — |
| `R17.2` — D3 / GPIO11; `U3.5` | P / — | 0 / — | P / — |
| `R18.1` — D4 / GPIO32 | 0 / — | 0 / — | 0 / — |
| `R19.1` — D5 / GPIO10 | 0 / — | 0 / — | 0 / — |
| `R20.1` — D6 / GPIO33 | 0 / — | 0 / — | 0 / — |
| `R21.1` — D7 / GPIO9 | 0 / — | 0 / — | 0 / — |
| `R22.1` — CLOCK / GPIO14 | 0 / — | 0 / — | 0 / — |
| `R23.2` — VALID_N / GPIO13 | P / — | 0 / — | P / — |
| `R24.2` — READY_N / Agon PD4 | 0 / — | A / — | A / — |
| `R25.2`; `U1.1`, `U4.3` — UART forward OE_N | 0 / — | A / — | A / — |
| `R26.2`; `U1.19`, `U2.1`, `U4.6` — parallel forward OE_N | 0 / — | A / — | A / — |
| `R27.2`; `U3.1`, `U3.4`, `U4.8` — UART return OE_N | 0 / — | A / — | A / — |
| `R28.2`; `U4.1` — GPIO15 control | P / — | 0 / — | P / — |
| `R29.2`; `U4.4` — GPIO17 control | P / — | 0 / — | P / — |
| `R30.2`; `U4.10` — GPIO21 control | P / — | 0 / — | P / — |
| `R31.2`; `U4.13` — GPIO20 control | P / — | 0 / — | P / — |
| `U2.19`, `U3.10`, `U3.13` — spare-bank enables | 0 / — | A / — | A / — |
| `U4.2`, `U4.5`, `U4.9`, `U4.12` — sink inputs | 0 / — | 0 / — | 0 / — |
| `U1.2` — R32 / D0 input | 0 / — | A / — | A / — |
| `U1.17` — R33 / D1 input | 0 / — | A / — | A / — |
| `U1.4` — R34 / D2 input | 0 / — | A / — | A / — |
| `U1.15` — R35 / D3 input | 0 / — | A / — | A / — |
| `U2.2` — R36 / D4 input | 0 / — | 0 / — | 0 / — |
| `U2.4` — R37 / D5 input | 0 / — | 0 / — | 0 / — |
| `U2.6` — R38 / D6 input | 0 / — | 0 / — | 0 / — |
| `U2.8` — R39 / D7 input | 0 / — | 0 / — | 0 / — |
| `U1.13` — R40 / CLOCK input | 0 / — | 0 / — | 0 / — |
| `U1.11` — R41 / VALID_N input | 0 / — | A / — | A / — |

When the Agon domain is powered, high R25/R26/R27 nets request disabled U1/U2/U3
outputs. When the P4 domain is powered, high R28–R31 nets request released U4
sink outputs. With a chip unpowered, do not interpret its OE voltage as an
operating logic state. These meter readings establish settled bias only;
they do not measure output leakage or prove high impedance through a load test.

### Optional digital startup capture

Use the explicit eight-channel bias/startup map in
[test methods](../test-methods.md#logic-sniffer-maps), with its reviewed probe
configuration. Record the actual channel endpoints, sample rate, threshold,
trigger and pretrigger interval. Arm before the specifically authorized event.
Observe the four control requests, three bank enables and READY_N bias; no
transport stimulus is part of this sheet. Record any digital pulse, but do
not claim the sniffer measures rail voltage or excludes pulses below its
sampling/threshold capability.

| Capture record | Observation / evidence |
| --- | --- |
| Event, initial/final power state, sample/trigger settings | — |
| Actual eight-channel map and capture file | — |
| Control or enable pulses; steady-state observations | — |
| Timing/analog limitations and exact accepted claim | — |

## 5. Stop conditions and result

The operator removes both board power sources if there is an unexpected rail
or enable voltage, unstable readings, heating, odor, smoke, or repeated resets.
Record the state, probe location, reading, and symptom before investigating
unpowered. Do not repair or move wiring while powered, or silently treat a
corrected assembly as the original test article.

| Result field | Record |
| --- | --- |
| Checks completed; skipped checks and reasons | — |
| Deviations, first unexpected reading, and disposition | — |
| Agon display/boot observation; P4 idle evidence and its limits | — |
| Evidence links; end time; final power/cable state | — |
| Outcome and exact scope accepted by Author | — |

The default final state is both boards off; record any separately authorized
alternative. Put the completed result beside this sheet and link its
disposition from [QUAL-002](../../../../../docs/tasks/QUAL-002.md).

A satisfactory record supports the installed resistor/connection checks and
the measured steady-state bias in the listed power states. The optional
startup capture has only its declared digital coverage. General boot/reset
transient qualification, brownout, active enable behavior, complete READY
operation, transport, production-code execution, and Legacy electrical absence need their
own applicable tests. The existing r02 connectivity/profile digest discrepancy
remains under [HW-001](../../../../../docs/tasks/HW-001.md) S3 before any clean
frozen-input qualification claim.
