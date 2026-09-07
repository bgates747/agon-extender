# 02 — Startup and fail-safe bias, with powered-test prerequisites

**Superseded draft; hardware work on hold as of 2026-09-07.** Retained for
review only. The Author rejected R32–R41 additions solely for intermediate
powered tests. This document is not an executable construction/test procedure.

**DRAFT.** Preserve the wiring in
[function view 02](../signal-views/generated/02_schematic_startup-and-fail-safe-bias-network.kicad_sch),
including R14–R31, while retaining the power/ground/bypass connections from
view 01. Add the ten defined-input connections below before powering the
populated ICs. They are the extra preparation missing from the function view.

## Permanent circuit change proposed for this stage

The Author requires permanent circuit parts only. Add ten separate
**10 kohm, 1%, at least 0.125 W** resistors in the proposed successor circuit.
R32–R41 below are proposed references, not parts present in frozen r02.
HW-001-Q011 owns approval of this circuit change and the successor harness
identity; the suggested next revision is `light2-harness-r03`, not yet approved.
The r02 connectivity model, BOM and generated drawings have not been revised.
This document is the reviewable addition proposal; do not build it as r02.

| Proposed resistor | Signal-side endpoint | Other end | Settled input with Agon powered | Later permanent source connection |
| --- | --- | --- | --- | --- |
| R32 | `U1.2` | `AGON_3V3` | High | `J1.17` / PC0, step 04 |
| R33 | `U1.17` | `AGON_3V3` | High | `J1.18` / PC1, step 06 |
| R34 | `U1.4` | `AGON_3V3` | High | `J1.19` / PC2, step 05 |
| R35 | `U1.15` | `AGON_3V3` | High | `J1.20` / PC3, step 07 |
| R36 | `U2.2` | common ground | Low | `J1.21` / PC4, step 11 |
| R37 | `U2.4` | common ground | Low | `J1.22` / PC5, step 12 |
| R38 | `U2.6` | common ground | Low | `J1.23` / PC6, step 13 |
| R39 | `U2.8` | common ground | Low | `J1.24` / PC7, step 14 |
| R40 | `U1.13` | common ground | Low | `J1.14` / PD5, step 15 |
| R41 | `U1.11` | `AGON_3V3` | High | `J1.16` / PD7, step 16 |

Use the local Agon-domain rail for every high bias. Do not use `P4_3V3` and
do not install direct input-to-rail jumpers: later eZ80/U3 outputs must be able
to drive the opposite level through the resistor's limited load. At 3.3 V,
one 10 kohm resistor draws approximately 0.33 mA when driven against its bias;
measure actual driven levels and include this added load in later results.

TI requires defined CMOS inputs even with outputs disabled; the
[SN74LVC244A datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf)
sections 5.3 and 7.3.3 explain that requirement and input termination.
The choice is a circuit proposal, not electrical qualification. At a 3.6 V
supply and 9.9 kohm minimum resistance, the added opposing load is at most
about 0.364 mA per line and 1.31 mW per resistor. Port C can see up to eight
such loads (2.91 mA total); CLOCK and VALID add two separately.
[Zilog PS015317-0120 table 163](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf)
specifies eZ80 output low/high levels at a 1 mA load, so each added resistor's
load alone is below that characterization point. The table also allows
temperature-dependent input/tristate leakage; the complete loading budget
must include the buffer, attached probes, other pin uses and internal pulls.
The [SN74LV125A electrical table](https://www.ti.com/lit/ds/symlink/sn74lv125a.pdf)
likewise supplies U3's output limits. Review the total source/sink and leakage
budgets, UART low-level margin through R11/R12, and transitions before accepting
the circuit. The later lane tests measure the resulting driven levels; a logic
trace alone cannot do so.

All ten resistors stay installed when their later signal wires are added.
Their purpose includes the interval before EMOS acquires the eZ80 pins, not
just the currently unwired stage. Once approved, they remain in the final
assembly and every tested stage.
There is no temporary termination or resistor-removal phase.

## Complete powered-input coverage

1. U1's ten signal/control inputs: six data inputs have the permanent bias
   above; `U1.6` and `U1.8` are grounded; OE pins `U1.1` and `U1.19` have
   R25/R26 Agon-domain pull-ups.
2. U2: four used data inputs have permanent bias; `U2.11`, `U2.13`, `U2.15`,
   `U2.17` are grounded; `U2.1` has R26 and `U2.19` is tied to `AGON_3V3`.
3. U3: `U3.2` and `U3.5` already connect to the R15/R17 P4-side bias nets;
   `U3.9` and `U3.12` are grounded. OE pins 1/4 have R27; pins 10/13 are tied
   to `AGON_3V3`.
4. U4: inputs 2/5/9/12 are grounded; OE pins 1/4/10/13 have R28/R29/R30/R31
   P4-domain pull-ups. All package grounds, supplies and bypasses remain fitted.

The ten Agon source wires in the table remain absent until their listed
steps. Transport buffer output connections remain absent. View 02 already
connects `J1.13`/READY_N through R24 and R13's Agon end; keep eZ80 PD4 an input.
The U4 output-to-R13 connection is added at step 08.

## Powered test

Use the [revised step-02 worksheet](tests/02-startup-and-fail-safe-bias-network.md).
It retains the previous rail and R14–R31 tables and adds readings at all ten
additional biased inputs. Confirm the P4 passive diagnostic identity, all four
control pull-ups and the absence of an Agon transport stimulus. Run the
authorized single-domain and dual-domain settled checks. All populated CMOS
inputs now have an explicit intended level in those states.

The optional eight-channel startup map in [test methods](test-methods.md#logic-sniffer-maps)
observes the four P4 control requests, three Agon enable nets and READY_N bias.
Arm before the specifically authorized power/reset event and retain the
pretrigger interval. Digital capture can reveal an unexpected enable pulse;
it does not prove analog voltage, leakage, or absence of shorter pulses.

This checkpoint establishes bias and released-state observations with the
approved permanent additions fitted. Active bank checks follow at step 03;
a complete transport and its production data plane are not needed for step 02.
