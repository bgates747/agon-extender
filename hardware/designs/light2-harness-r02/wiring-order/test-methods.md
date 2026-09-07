# Powered construction test methods

**Superseded draft; hardware work on hold as of 2026-09-07.** Retained for
review only. The Author rejected R32–R41 additions solely for intermediate
powered tests. This document is not an executable construction/test procedure.

Status: draft requirements for the callers and captures used by the
[wiring sequence](README.md). These method labels are not firmware identities,
approved procedures, or evidence that executable fixtures exist. All steps
after 01 depend on approval and implementation of the permanent input bias
proposed in [step 02](02-startup-and-fail-safe-bias-network.md).

## Common starting and finishing state

1. The operator changes wiring and probes with both boards unpowered. Record
   the cumulative step, circuit revision, source/image identities, actual
   source/destination terminals, instrument settings and cable/power state.
2. At settled idle, P4 GPIO15/17/21/20 release their controls; R28–R31 and
   R25–R27 provide the respective high states. P4 transport pads start as
   inputs with internal pulls disabled. Permanent input bias defines the
   Agon-side buffer inputs before EMOS owns the associated signals.
3. Before enabling a bank, the caller configures every input and output in
   that bank, including channels whose output wires are absent. U3's used
   inputs are GPIO12 and GPIO11 even when only one return lane is installed.
4. EMOS owns all eZ80 pin direction/mux changes and stimuli. A cold-boot
   application may call an approved EMOS-owned diagnostic entry point; it may
   not write registers itself. Its exact `/autoexec.txt` invocation and terminal
   state must be supplied before use under the
   [bench constraint](../../../../docs/qualification/bench-constraints.md).
5. For each lane, start with a slow bounded low/high pattern, proposed at 10 Hz
   for ten cycles, so a DMM can check held levels and the sniffer can compare
   edges. Record low/high holds separately from the pulse capture. Expected:
   the enabled destination follows its source; after release it returns to
   its local bias. The preliminary voltage bands are in the step-02 sheet.
6. On completion or error, the caller releases READY and all transport
   enables, releases P4 shared outputs, and restores the declared EMOS idle
   state. The operator records the result and returns both boards to off.
   Unexpected voltage, contention, reset, heat, or a failed release ends the
   test; wiring is investigated only unpowered.

## Methods and actual code availability

| Method | Owner and intended stimulus | Current implementation boundary |
| --- | --- | --- |
| Passive | P4 leaves all fourteen harness pads input-only; EMOS/stock MOS launches no transport stimulus | The [P4 passive fixture](../../../../docs/tasks/QUAL-002/p4-passive-r01/README.md) exists. Confirm its installed build. No transport component is exercised. |
| Control | P4 caller releases all controls, then asserts/releases only the reviewed bank; logs requested states | [EspP4EpochHardware](../../../../vdp/video/extender/transport/p4_parallel_target.hpp) has production release, parallel-enable and READY operations. Its `enableParallelForwardBanks()` controls GPIO15 **and** GPIO17 together. It has no isolated UART-forward or UART-return assertion API. A separately identified diagnostic caller is needed for isolated bank tests; do not describe copied GPIO code as the production component. |
| Lane | EMOS-owned bench routine holds/toggles the selected Agon signal; P4 caller establishes the selected receive-bank state and samples its input | No deployable per-lane EMOS/P4 composition has been selected. PORT-008 prepares the next needed caller. Reuse the existing product ownership/pad helpers only where their actual preconditions hold; a bounded electrical diagnostic covers the remaining stimulus and makes no complete transport claim. |
| UART | EMOS UART1 and P4 UART2 exchange a bounded known byte pattern, then apply RTS/CTS backpressure in both directions | r02 UART binding, four-wire setup and its stage caller need preparation/review. The existing parallel qualification composition explicitly owns no UART return path. Do not enable its parallel epoch to stand in for a UART test. |
| Parallel | EMOS production binding/engine transmits real records; P4 production epoch owner and PARLIO ingress receive them and report exact byte comparison | Production sources exist: P4 [data plane](../../../../vdp/video/extender/transport/p4_parallel_data_plane.hpp) and [target](../../../../vdp/video/extender/transport/p4_parallel_target.cpp); EMOS owns `src/emos_parallel.c`, `emos_parallel_engine.c`, `emos_parallel_io.asm` and the fixed qualification backend in its sibling repository. A clean identified composition and authorized peer/epoch preconditions remain due. |

The EMOS fixed backend supplies a reviewed qualification precondition; it is
not a discovery protocol. A partial bus has no complete record test: do not
force READY, invent an acknowledgement, discard absent bits, or edit the
production protocol to make one pass. Step 17 is the first full parallel
record checkpoint. General Poll and ordinary VDU integration follow under
their existing task gates.

The passive and individual-control methods can test the early populated
circuit without a full EMOS/P4 transport build. PORT-008's current queue owns
only the next needed caller; the implementation work stays out of these
procedure documents.

## Shared-pin states

| Test state | GPIO15 / UART-forward control | GPIO17 / parallel-forward control | GPIO21 / UART-return control | GPIO12 and GPIO11 on P4 | Agon PC1 and PC3 |
| --- | --- | --- | --- | --- | --- |
| Passive | Released | Released | Released | Inputs | Undriven, permanent high bias |
| Individual forward lane 04/05 | Low when measuring | Released | Released | Inputs | Undriven, permanent high bias |
| UART return 06/07 | Released, or low only when the forward pair is deliberately in use | Released | Low when measuring | Outputs, both initialized to UART idle/released-flow state before U3 enable | Inputs |
| Parallel lane 09–16 | Low for D0/D2 observation if selected | Low when measuring a parallel-bank lane | Released | Inputs before the forward bank is enabled | EMOS-owned outputs when exercised |

GPIO20 stays released except for the step-08 READY test and a real armed
parallel receiver. The step-08 diagnostic claims only control-to-PD4 behavior;
asserting it is not a production receiver-readiness claim.

Whenever a shared-pin role changes, release the return and forward banks,
stop the old UART/PARLIO owner, prepare the receiving pads, establish the EMOS
direction, then enable only the selected new path. Observe enable exclusion.
A static bench setup does not qualify the full production epoch transition.

## Logic-sniffer maps

Use the known eight physical lead colors from the
[analyzer reference](../../../../hardware/fixtures/la03-p4-probe-fixture-r01/README.md),
but record the actual stage endpoints below as a newly reviewed probe map.
These maps are **not** the old LA-03 r01 placement. GPIO20 is the READY
**control** on r02; Agon READY_N is at J1.13. Probe the intended one explicitly.
Connect analyzer ground to common ground. Confirm the analyzer's electrical
limits and input loading before attachment; its digital readings cannot prove
analog safety. Do not attach an unpowered analyzer if it would load a powered
signal through its input protection.

| Channel / physical color | Bias/startup map, step 02 | Enable map, step 03 | Single-lane map, steps 04–16 |
| --- | --- | --- | --- |
| D0 / green | GPIO15, `J2.16` | GPIO15, `J2.16` | Source terminal named in the step |
| D1 / yellow | UART-forward OE, `U1.1` | UART-forward OE, `U1.1` | Destination terminal named in the step |
| D2 / blue | GPIO17, `J2.18` | GPIO17, `J2.18` | Selected bank OE at its actual IC pin |
| D3 / orange | Parallel-forward OE, `U1.19` | Parallel-forward OE, `U1.19` | GPIO15 control |
| D4 / purple | GPIO21, `J3.12` | GPIO21, `J3.12` | GPIO17 control |
| D5 / red | UART-return OE, `U3.1` | UART-return OE, `U3.1` | GPIO21 control |
| D6 / gray | GPIO20, `J3.13` | GPIO20, `J3.13` | GPIO20 control |
| D7 / brown | READY_N, `J1.13` | READY_N, `J1.13` | Other lane in the enabled bank, or READY_N; identify it explicitly |

Duplicate endpoints in a step's map may leave a channel unused; label it so.
For the step-08 READY test, source = `J3.13`, destination = `J1.13`, and the
selected OE is `U4.13`. Check `U4.11`/R13's sink end in a separate recording
if localizing a failure. Do not claim observation of an unprobed point.

Record sample rate, sample count/duration, trigger edge and threshold, and
pretrigger coverage. Use at least ten samples per shortest intended pulse for
the slow diagnostic; at 1.152 Mbaud, 24 MS/s yields about 20.8 samples per bit
if the actual analyzer configuration supports that rate. Trigger at the source
edge for lane tests and retain an idle interval on each side. Digital equality
within a sample bin is not a propagation-delay or analog-edge measurement.

Step 07 uses one eight-channel pass for both ends of all four UART signals:
PC0/GPIO22, PC2/GPIO23, GPIO12/PC1, GPIO11/PC3. A separate pass observes the
enable state. Step 17 uses one data-bus pass and additional CLOCK/VALID/READY/
enable passes, plus receiver byte comparison. Eight channels cannot observe
the full bus and all controls simultaneously; conclusions must name each
capture's boundary. Use an oscilloscope when an analog or sub-sample timing
claim is needed.
