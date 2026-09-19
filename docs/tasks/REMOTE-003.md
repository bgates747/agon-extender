# REMOTE-003 — Browser-requested mainboard reset through P4

P4-controlled mainboard reset appears feasible using a GPIO-driven transistor
connected to the Agon reset net. The existing Pi-controlled actuator demonstrates
that physical route, but the P4 is not wired to it. This study recommends reusing
the proven actuator principle, subject to pin selection and electrical review.
The Author has deferred this work and will use the physical reset button for now.
No reset firmware, endpoint, wiring change or physical test is authorized here.

## State and scope

1. Author requested a feasibility study on 2026-09-19; study complete. The Author
   deferred further work; implementation remains unstarted. Resume only on explicit
   Author request. The existing Pi helper remains available, unchanged.
2. Desired action: the human requests an Agon reset from the browser; P4 executes
   one physical reset pulse without requiring Pi5 or responsive EMOS.
3. This is reset, not power cycling, flashing, ZDI recovery or an automatic
   response to a lost video/keyboard connection. P4 itself remains running.
4. Current hardware authority remains [Pi reset](../bench-reset.md). This proposal
   does not change the production contract in [remote keyboard](../remote-keyboard.md).

## Evidence and feasibility

| Route | Existing evidence | Assessment |
|---|---|---|
| Browser → Pi → transistor → Agon reset | Maintained `scripts/reset_agon.py`; accepted 100 ms pulse and observed boot | Possible fallback, but needs a Pi service/authentication surface and preserves the dependency the Author wants to remove. |
| Browser → P4 → transistor → Agon reset | Existing transistor arrangement works under Pi GPIO control; P4 HTTP and keyboard services already exist | Recommended candidate; requires a suitable allocated P4 output, wiring and new bounded control handling. Not yet qualified. |
| Browser → P4 → UART → EMOS restart command | Requires responsive EMOS and UART | Cannot replace physical reset when EMOS hangs; not recommended for this request. |
| Existing P4 ZDI recovery leads | GPIO46/47 connect TCK/TDI, not reset | Not an existing physical-reset connection; do not repurpose recovery firmware for normal operation. |

The accepted actuator has a 10 kohm base resistor and 2N2222 transistor:
collector to Light2 ZDI1 pin2 RST/EN, emitter to common ground. GPIO high pulls
reset low; GPIO low/input with pull-down releases it. The existing helper requests
100 ms once, then releases even on command failure. This is functional evidence,
not a measured reset timing/electrical specification for a new P4 driver.

A P4 implementation could move the actuator's control lead from Pi to P4, or
provide separately isolated low-side control paths if retaining both controllers.
Never tie Pi and P4 push-pull outputs together. Do not connect a push-pull P4 pin
directly to the Agon reset net or join the boards' power rails. A hardware base
pull-down should establish release while P4 is booting or its GPIO is unconfigured;
software cleanup alone cannot guarantee release after a processor failure.

No P4 GPIO is selected. Selection must account for the actual devkit revision,
USB keyboard, Ethernet, UART/parallel harness, future SD use, boot straps and
reserved recovery pins. The actual reset-net fanout must be checked in the
Light2 schematic before claiming which mainboard processors reset together.

## Shared GPIO and 74-series control expansion — deferred alternative

The Author suggested retaining P4 GPIO capacity for other uses. A latched bank of
control outputs could serve reset and future low-rate controls without dedicating
one processor pin to each function. No part, bus or wiring is selected.

| Option | P4 operation | Tradeoff |
|---|---|---|
| Dedicated GPIO | P4 drives the reset transistor through its base resistor | Simplest for reset alone; consumes an output exclusively. |
| Serial register, such as a 74HC595-style device | P4 shifts a control byte, then latches it into stable outputs; one output drives the reset transistor | Expands a few signals into several controls. Sharing data/clock may save pins, but still requires an unambiguous latch/select mechanism and startup handling. |
| Parallel output latch | P4 places a control word on suitable shared parallel lines and explicitly clocks the latch | Can reuse a bus, but bus direction, ownership, electrical loading and strobe isolation must be proven. Existing Agon-driven lines are not automatically safe for P4 to drive. |

1. The [TI SN74HC595](https://www.ti.com/product/SN74HC595) has separate shift and
   output storage registers, allowing stored outputs to remain stable while P4
   shifts new data. Its output-enable input can place outputs in high impedance.
   This establishes a candidate mechanism, not a qualified part selection.
2. Ordinary UART or parallel traffic must never latch an unintended control word.
   P4 must own a distinct update operation. A shared bus that requires responsive
   EMOS to relinquish it cannot provide dependable recovery from hung EMOS.
3. Hardware must keep reset released during P4 and logic-chip startup. Do not
   assume stored outputs power up cleared; the shift-register clear is not itself
   an output-register reset. Output gating and the transistor pull-down require
   deliberate design. Logic voltage compatibility must be checked for the exact
   74-series family selected.
4. A latched asserted output could hold Agon in reset if P4 fails before clearing
   it. Compare that failure mode with the dedicated-GPIO option and any bounded
   pulse hardware before adopting expansion logic.
5. On resumption, compare serial expansion with a parallel latch against the
   actual pin inventory and credible future controls. Extra logic is difficult
   to justify for reset alone, but may be worthwhile for several controls.

## Proposed control behaviour — not yet accepted

1. The browser sends an explicit reset request to a P4 control endpoint independent
   of keyboard ownership, video streaming and EMOS admission. The human sees a
   distinct reset action, with confirmation appropriate to interruption of a running
   program or SD write. No reset is triggered by entering fullscreen or reconnecting.
2. P4 validates the request under the chosen control-access policy, rejects a
   concurrent request, and schedules one bounded pulse outside a blocking HTTP
   handler. P4 releases reset on the normal completion and error paths.
3. The browser does not automatically retry an uncertain request. A request ID and
   P4 result/status distinguish accepted, pulsing and released from observed boot.
   A socket disconnect must not cause a second pulse.
4. P4 cancels queued pre-reset keyboard/agent input and releases held-key state;
   resumed automation requires a fresh EMOS admission epoch. Old `ready=true` is
   not proof of reboot. No pre-reset command batch is replayed.
5. P4 reports pulse completion separately from EMOS boot/readmission. A hung or
   unpowered P4 cannot provide this recovery; retain an independent physical/Pi
   fallback if that recovery requirement is accepted.

## Decision register and implementation prerequisites

| ID | State | Decision needed before implementation |
|---|---|---|
| D01 | Accepted | Study only; prefer P4 execution of human-requested physical Agon reset. |
| D02 | Open | Choose dedicated GPIO or shared control expansion, allocate the required signals, and inspect reset-net electrical/fanout requirements against the actual boards. |
| D03 | Open | Move the existing actuator control to P4, or retain independent Pi control with isolated actuators; decide release behaviour if P4 fails during a pulse. |
| D04 | Open | Select browser control access/confirmation policy and compact UI placement. Existing LAN keyboard access is not automatically authorization for a new reset endpoint. |
| D05 | Open | Agree pulse timing, duplicate handling, fresh-admission observation and active flash/SD-operation handling. The observed 100 ms Pi pulse is the starting candidate, not new qualification. |
| D06 | Accepted | Defer further study and implementation; Author uses the physical reset button for now. No expansion architecture is selected. |

After approval, a separate implementation contract must cover GPIO startup and
release checks, a single explicit reset, unchanged P4 uptime, fresh Agon boot,
no stale keystroke replay, operation without keyboard capture/in Legacy, request
failure/duplicate cases, and coexistence with ordinary video/input load. Do not
run those checks or change the bench as part of this study.

## Research references and limits

1. [Maintained reset circuit and acceptance](../bench-reset.md) and
   `scripts/reset_agon.py`: actual actuator, pulse and functional observations.
2. [Recovery protocol](../mos-recovery.md): GPIO46/47 programming allocation and
   separate ZDI1 reset pin. ZDI programming is not ordinary reset.
3. [Remote keyboard contract](../remote-keyboard.md): reset epoch/readmission and
   no replay of cancelled batches.
4. Official documentation reviewed in the read-only `agon-docs` checkout:
   `docs/Updating-Firmware.md` and `docs/FAQ.md` discuss reset/update behaviour but
   do not establish a new P4 GPIO or electrical reset contract. Board schematic
   verification therefore remains a prerequisite rather than an inferred fact.
5. The older [order4 test reboot](QUAL-003/debrief/P01h/codec-screen/order4-p4/RESULTS.md)
   used reset-before-run controls and observed a P4 reboot; it is not evidence
   of an implemented P4-driven Agon reset circuit or a diagnosed reset-driver bug.
