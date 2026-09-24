# REMOTE-003 — Browser-requested mainboard reset through P4

## Executive summary

The Pi-backed browser reset button is implemented and Author-accepted, including
its top-right header placement and silent success. Use the
[current reset guide](../bench-reset.md) for operation. P4 serves the page; the
browser calls the Pi bridge, and the Pi pulses the mainboard reset actuator.
This is not a P4-driven GPIO reset or a power cycle.

Direct P4 reset remains a deferred feasibility proposal. No P4 reset pin or
control-expansion circuit is selected. The original study below applies to that
possible replacement of the Pi dependency; it does not describe browser reset
as unavailable.

## State and scope

1. Author requested a feasibility study on 2026-09-19; study complete. The Author
   deferred direct-P4 implementation, which remains unstarted. Resume that work
   only on explicit Author request. The later Pi-backed button is implemented;
   its accepted scope is recorded below.
2. Desired action: the human requests an Agon reset from the browser; P4 executes
   one physical reset pulse without requiring Pi5 or responsive EMOS.
3. This is reset, not power cycling, flashing, ZDI recovery or an automatic
   response to a lost video/keyboard connection. P4 itself remains running.
4. Current hardware authority remains [Pi reset](../bench-reset.md). This proposal
   does not change the production contract in [remote keyboard](../remote-keyboard.md).

## Evidence and feasibility

| Route | Existing evidence | Assessment |
|---|---|---|
| Browser → Pi → transistor → Agon reset | Maintained `scripts/reset_agon.py`; accepted 100 ms pulse and observed boot | Implemented through the accepted Pi bridge; trusted-LAN controls are not client authentication. Preserves the Pi dependency the deferred direct-P4 proposal would remove. |
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

## Direct-P4 decision register and implementation prerequisites

| ID | State | Decision needed before implementation |
|---|---|---|
| D01 | Accepted | Study only; prefer P4 execution of human-requested physical Agon reset. |
| D02 | Open | Choose dedicated GPIO or shared control expansion, allocate the required signals, and inspect reset-net electrical/fanout requirements against the actual boards. |
| D03 | Open | Move the existing actuator control to P4, or retain independent Pi control with isolated actuators; decide release behaviour if P4 fails during a pulse. |
| D04 | Open | Select browser control access/confirmation policy and compact UI placement. Existing LAN keyboard access is not automatically authorization for a new reset endpoint. |
| D05 | Open | Agree pulse timing, duplicate handling, fresh-admission observation and active flash/SD-operation handling. The observed 100 ms Pi pulse is the starting candidate, not new qualification. |
| D06 | Accepted | Defer direct-P4 study/implementation. Physical and Pi-backed browser reset remain available; no expansion architecture is selected. |

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

## Ad hoc Pi-backed reset button — authorized 2026-09-21

Author requests the existing agent reset action in the browser. This resumes only
Pi-backed browser control; direct P4 GPIO/reset expansion remains deferred.
Browser calls a separately configured Pi HTTP bridge, which runs the established
100 ms GPIO pulse once. P4 serves the button but does not drive reset. No EMOS,
SD or wiring changes. UI confirms interruption, releases browser keyboard capture,
never retries an uncertain request, and distinguishes pulse receipt from boot.
Endpoint and allowed Origin are machine-local configuration, not tracked addresses.

P01 [x] Implement/test a fixed-action bridge: explicit POST, allowed Origin and
custom header, bounded request size, concurrent-request rejection and duplicate
request-ID suppression. No user-supplied shell command or automatic retry.
P02 [x] Add compact Reset Agon button to the existing fullscreen control strip;
disabled if endpoint unconfigured. Preserve video/input implementation otherwise.
P03 [x] Deploy Pi service and P4 assets, verify served bytes and one explicit
browser reset; verify fresh keyboard admission separately. Preserve rollback.

### Ad hoc result — 2026-09-21

P01–P03 completed. `browser-reset-r01-b2026-09-21-20-23-09Z` was built from the
isolated key-query September20 parent with only index/app browser changes,
flashed and independently verified; boot identity and USB startup passed.
Bridge unit test rejected GET, wrong Origin and missing header; duplicate UUID
executed the mocked pulse once. Existing browser keyboard regression test passed.
Chromium fetched matching deployed assets, cancelled one confirmation without a
request, then accepted one explicit button reset. Bridge returned pulse released;
P4 reported keyboard ready and no held keys after Agon boot. No page JS errors.
No Mac browser acceptance claimed yet. Local receipts: `agents/browser-reset/`.

Operational authority is now [bench reset](../bench-reset.md). Pi service is
boot-enabled; no direct P4 reset GPIO, EMOS change or SD modification. Hardware
reset equivalence was checked against AgonLight2 Rev B sheet 4: physical RESET1
and the established ZDI1 reset endpoint share RST/EN. Author accepted the deployed upgrade and authorized commit/push.

Registry validation is blocked by a pre-existing light2-harness-r02
connectivity.yaml integrity mismatch; this task did not edit that hardware
profile or repair its recorded digest. Firmware build and reset tests passed.

### Header placement revision — 2026-09-21

Author requested Reset Agon at the right end of the branding/FPS header, away
from normal controls, and removal of the pulse-sent message. r02 implements
that placement and silent success; errors retain a dialog. The header remains
outside video fullscreen. Mock-browser check covers header alignment and
success without layout text; reset actuator/bridge unchanged.

Author acceptance: 2026-09-21, including header placement and silent success.
