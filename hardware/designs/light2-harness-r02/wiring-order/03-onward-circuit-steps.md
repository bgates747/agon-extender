# 03 onward — Small powered circuit steps

**Superseded draft; hardware work on hold as of 2026-09-07.** Retained for
review only. The Author rejected R32–R41 additions solely for intermediate
powered tests. This document is not an executable construction/test procedure.

Status: draft sequence, conditional on the permanent-input-bias circuit change
in step 02. All prior wiring and approved permanent resistors remain installed.
The [sequence manifest](sequence.yaml) lists cumulative additions; the r02
model defines the existing endpoints. The source drawings below help locate
the wires, but often show more wiring than the particular step adds.

Use the common entry/exit rules and named methods in
[test methods](test-methods.md). Each step requires its identified caller to be
prepared and reviewed before power-on. The [result template](tests/RESULT-TEMPLATE.md)
records the actual wiring, held levels, waveform and outcome. Failed or partial
checks remain evidence; do not mark a lane accepted from continuity alone.

## 03 — Enable-bank checkpoint

Add no permanent wire: step 02 already wired all three OE nets and their P4
controls. Use the Control method, with all ten added input biases fitted and
all transport output connections still absent. Starting with all controls
released, the P4 diagnostic asserts and releases GPIO15, then GPIO17, then
GPIO21 individually. Each selected OE must follow low/high; the other two
remain high. Check both `U1.19` and `U2.1` on the shared parallel enable and
both `U3.1` and `U3.4` on the return enable. Keep GPIO20 released.

Capture the enable map and measure the low/high held voltages. This tests the
control sinks and enable wiring before any output can drive a processor lane.
It does not prove output high impedance by itself. U4's READY output is tested
after its receiver-side pull path is complete at step 08.

## 04 — D0 / UART forward data

Add `J1.17`–`U1.2` and `U1.18`–`R1.1`; R1's other end already reaches
`J3.11`/GPIO22. Trace with [view 04](../signal-views/generated/04_schematic_d0-uart-rx-lane.kicad_sch).

Use the Lane method: EMOS owns and toggles PC0, P4 holds GPIO22 as input and
enables UART-forward only. Observe source `J1.17`, destination `J3.11`, and
OE `U1.1`. U1's other used channel input, `U1.4`, remains permanently biased;
its output is still unconnected. Enabled GPIO22 follows PC0; released GPIO22
returns high through R14. Check a driven low as well as the idle high so a
disconnected wire cannot appear to pass. This is a lane test, not yet a
four-wire UART exchange.

## 05 — D2 / UART forward flow control

Add `J1.19`–`U1.4` and `U1.16`–`R3.1`; the destination is already
`J3.10`/GPIO23. Trace with [view 05](../signal-views/generated/05_schematic_d2-uart-cts-lane.kicad_sch).

Use the Lane method with EMOS-owned PC2. Observe `J1.19` → `J3.10`, OE
`U1.1`, and D0 as the other channel in that bank. Enabled low/high levels must
arrive at GPIO23; released GPIO23 returns high through R16. This establishes
the electrical RTS-to-CTS path. Actual UART flow control waits for step 07.

## 06 — UART return data

Add the complete net `J1.18`–`R11.2`–`U1.17`, plus `U3.3`–`R11.1`.
R11 is 220 ohms. The P4 source path GPIO12/`J2.13` → `U3.2` already exists.
Use [view 07](../signal-views/generated/07_schematic_d1-uart-tx-lane.kicad_sch)
for tracing, but **leave `U1.3`–`R2.1` absent** until step 09.

The P4 UART/electrical caller sets GPIO12 and GPIO11 to their reviewed output
idle states before enabling U3. EMOS keeps PC1 an input. Keep parallel-forward
released throughout. Observe `J2.13` → `J1.18`, OE `U3.1`; check both driven
levels, then released Agon RX high through the new permanent input pull-up.
U3's second output `U3.6` remains unconnected, but its input GPIO11 must still
be controlled. This is the return-data electrical test; complete UART setup
and candidate binding remain prerequisites for the later byte exchange.

## 07 — UART return flow control and four-wire UART

Add `J1.20`–`R12.2`–`U1.15`, plus `U3.6`–`R12.1`; R12 is 220 ohms.
GPIO11/`J2.12` → `U3.5` already exists. Trace with
[view 08](../signal-views/generated/08_schematic_d3-uart-rts-lane.kicad_sch),
leaving `U1.5`–`R4.1` absent until step 10.

First observe `J2.12` → `J1.20`, OE `U3.4`, with EMOS PC3 input and
parallel-forward released. Check low/high and released high. All four UART
signal paths now exist. With the reviewed UART method, exchange a bounded
known pattern (proposed: repeated `00 FF 55 AA` with byte counts) in both
directions. Begin at a reviewed diagnostic rate, then test the required
1,152,000 baud, 8N1. Each result names its actual rate.

Exercise RTS/CTS blocking and resumption in both directions through the
owning UART implementation; verify no missing/extra/reordered bytes and no
transmission while flow is blocked, within the agreed in-flight-byte limit.
That limit and the exact MOS/P4 configuration must be supplied by the caller
procedure, not guessed from this electrical plan. General Poll, mode
activation and full compatibility are separate later claims.

## 08 — READY return

Add `U4.11`–`R13.2`; R13's Agon end already reaches `J1.13` and R24.
Trace with [view 17](../signal-views/generated/17_schematic_ready-n.kicad_sch).

Use the Control method with all transport banks released and EMOS PD4 input.
Observe GPIO20/`J3.13` → READY_N/`J1.13`: a low control lets U4 sink READY_N
low; released control lets R24 pull READY_N high. EMOS readback should agree
with the sniffer and held-voltage measurements. The existing P4
`assertReady()`/`releaseReady()` component can be used by an identified caller
after its GPIO configuration preconditions are met. This electrical stimulus
does not assert that a production receiver has armed a record.

## 09 — Parallel D1 output

Add `U1.3`–`R2.1`. The source net PC1/`J1.18` → `U1.17` was installed in
step 06; R2's destination GPIO12/`J2.13` was installed in step 02.
Trace with [view 07](../signal-views/generated/07_schematic_d1-uart-tx-lane.kicad_sch).

Use the Lane method after releasing U3 and P4 UART outputs, configuring GPIO12
and GPIO11 as inputs, and giving EMOS the selected output direction. Observe
`J1.18` → `J2.13`, OE `U1.19`. The whole U1 second bank and U2 first bank
enable together; all other inputs retain their defined states. Check both
driven levels and return to the P4-side high bias after release.

## 10 — Parallel D3 output

Add `U1.5`–`R4.1`. Source PC3/`J1.20` → `U1.15` already exists from step
07; destination GPIO11/`J2.12` already exists from step 02. Trace with
[view 08](../signal-views/generated/08_schematic_d3-uart-rts-lane.kicad_sch).

Use the same shared-pin preparation as step 09. Observe `J1.20` → `J2.12`,
OE `U1.19`, and already installed D1. Check driven low/high and released high.
UART return remains disabled for the whole parallel-lane test.

## 11 — Parallel D4

Add `J1.21`–`U2.2` and `U2.18`–`R5.1`. Observe PC4/`J1.21` →
GPIO32/`J3.9`, OE `U2.1`, using the Lane method. Trace with
[view 10](../signal-views/generated/10_schematic_d4-lane.kicad_sch).
The enabled destination follows both source levels; release returns it low
through R18. Check a driven high so a missing wire cannot pass as idle low.

## 12 — Parallel D5

Add `J1.22`–`U2.4` and `U2.16`–`R6.1`. Observe PC5/`J1.22` →
GPIO10/`J2.11`, OE `U2.1`, using the Lane method. Trace with
[view 11](../signal-views/generated/11_schematic_d5-lane.kicad_sch).
Check driven low/high and released low through R19, plus the previously
installed D4 lane while their shared bank is enabled.

## 13 — Parallel D6

Add `J1.23`–`U2.6` and `U2.14`–`R7.1`. Observe PC6/`J1.23` →
GPIO33/`J3.8`, OE `U2.1`, using the Lane method. Trace with
[view 12](../signal-views/generated/12_schematic_d6-lane.kicad_sch).
Check driven low/high and released low through R20; other bank inputs stay
at their declared idle or deliberately exercised state.

## 14 — Parallel D7

Add `J1.24`–`U2.8` and `U2.12`–`R8.1`. Observe PC7/`J1.24` →
GPIO9/`J2.10`, OE `U2.1`, using the Lane method. Trace with
[view 13](../signal-views/generated/13_schematic_d7-lane.kicad_sch).
Check driven low/high and released low through R21. All eight data lanes now
exist, but CLOCK and VALID_N are still missing: do not claim a parallel record.

## 15 — CLOCK

Add `J1.14`–`U1.13` and `U1.7`–`R9.1`. Observe PD5/`J1.14` →
GPIO14/`J2.15`, OE `U1.19`, using the Lane method. Trace with
[view 14](../signal-views/generated/14_schematic_clock.kicad_sch).
Check low/high holds, the slow pulse train and released low through R22.
Keep VALID_N inactive. The low-rate capture establishes connectivity and
polarity, not maximum clock rate or setup/hold margin.

## 16 — VALID_N

Add `J1.16`–`U1.11` and `U1.9`–`R10.1`. Observe PD7/`J1.16` →
GPIO13/`J2.14`, OE `U1.19`, using the Lane method. Trace with
[view 15](../signal-views/generated/15_schematic_valid-n.kicad_sch).
Check high idle, deliberate low assertion, and released high through R23.
Do this diagnostic with PARLIO record reception inactive.

The accumulated permanent connections now include every connected terminal
of the r02 basis plus the approved input-bias additions. Inspect the complete
assembly and intentional no-connects against the accepted successor model
before selecting step 17's candidate build.

## 17 — Complete candidate parallel records

Add no wire. Use the Parallel method with real sender, receiver, all eight
data lanes, CLOCK, VALID_N and READY_N. P4 UART outputs and the U3 return bank
must be released before EMOS drives shared data pins and the P4 enables the
forward banks. Candidate ingress asserts READY only after it is prepared to
accept a record; EMOS observes the real signal.

Use a reviewed fixed qualification composition to exercise retained
production sender, epoch owner, PARLIO and queue components. Begin with a small
known payload, then walking-bit patterns and record-boundary sizes selected
from the actual component limits. Compare exact transmitted and received
bytes/counts. Include bounded stop/cancellation and READY backpressure through
their real APIs. Each new fault or reset scenario needs its own applicable
review; this plan does not authorize physical fault injection.

Use the bounded captures described in test methods and state which signals
each pass observed. Record the exact candidate objects and link provenance
under PORT-008 Work 2.e. Product activation, mode commitment, General Poll and
broader power/reset qualification retain their task gates. Passing this step
does not promote a diagnostic caller into the product or establish release
composition equivalence.
