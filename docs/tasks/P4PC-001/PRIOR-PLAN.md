# Historical plan — superseded as active scope on 2026-10-02

Retained for provenance only. The current task is [P4PC-001](../P4PC-001.md).
The earlier work plan below is not an active execution checklist. Relative links
in the preserved text were written relative to `docs/tasks/`.

# P4PC-001 — Olimex ESP32-P4-PC bring-up and Agon integration

## Executive summary

The Author confirmed receipt of an Olimex ESP32-P4-PC Rev C on 2026-10-02
and selected it to replace the DevKit as the project target. Evaluate it
as both an Extender target with onboard HDMI and a useful standalone platform.
Exact preservation of DevKit GPIO assignments is no longer the deciding purchase
criterion: total assembled cost, capabilities and practical harness adaptation
matter. This task captures the plan; implementation and bench work have not begun.

## Scope and current authorization

Current authorization includes documentation vendoring and cloning the official
upstream examples as read-only references. Preserve the working
DevKit evidence. No purchase, wiring change, firmware deployment, reset or emulator
launch is part of this documentation step. The Author reports that the physical
bench topology has changed: development and bench hosting now run on the
Raspberry Pi 5, with the P4-PC and USB logic sniffer attached. The former
development host is retired from this work; the Agon and DevKit are disconnected
and unpowered. Establish standalone P4-PC operation with independent tests before
the Author reconnects the Agon to the Pi 5. Verify migrated host tools for ARM
compatibility before use; exact local paths and device identities belong in
`HARDWARE.local.md`. The official reference
checkout has been refreshed to `04032d68e5c727870f9d40beb9e37b7ab3a66916`;
the hardware reference index distinguishes it from the retained Rev B snapshot.
Golem remains out of scope. Existing graphics qualification evidence
is a baseline, not validation of a new board or HDMI backend.

## Itemized work plan

1. [x] PC01 — Record purchase, accessory options, breadboard proposal and limits.
2. [ ] PC02 — Confirm received revision and inspect its official schematic,
   populated headers, power routing and shared peripheral assignments. Produce
   a complete signal allocation before wiring or ordering a bespoke harness.
3. [ ] PC03 — Design the breadboard breakout: Agon header pin/signal, P4 header
   pin/GPIO, direction, voltage, existing pulls, proposed pulls, boot state and
   conflicts. Include UART TX/RX/RTS/CTS, future parallel signals, sniffer access,
   and recovery connections. Check GPIO constraints for any selected peripheral.
4. [ ] PC04 — Define board-specific firmware configuration and rollback/build
   identities without changing the established DevKit target. Preserve onboard
   HDMI, Ethernet, USB and audio where feasible; explicitly document tradeoffs.
5. [ ] PC05 — After bench authorization, qualify independent power and basic
   programming, then UART/flow control, EMOS keyboard and SD service. Confirm
   recovery access before disruptive testing. Retain exact wiring and evidence.
6. [ ] PC06 — Implement/qualify direct HDMI output: bridge setup, supported
   timings, palette conversion, framebuffer ownership, rendering correctness
   and sustained presentation. Keep output and rendering timings separate.
7. [ ] PC07 — Human review with Rally and Nurples; compare against retained
   baselines. Record standalone application opportunities separately from Agon
   compatibility. Do not infer acceptance from successful boot alone.

## Decisions and boundaries

1. Author selected P4-PC; receipt of Rev C confirmed on 2026-10-02. Full schematic
   and as-built inspection under PC02 remains pending.
2. Author proposes both device headers terminate on breadboard breakouts with
   cross-connections and optional pull resistors. This is the preferred prototype
   approach, not an approved pin table.
3. Initial proposal: common ground, separately powered boards, UART plus flow
   control first. Do not join supply rails or assume a straight UEXT ribbon works.
4. Check existing pulls and voltage domains before selecting resistors. Keep
   wires short. Parallel-speed qualification may require a better interconnect.
   MIPI/HDMI high-speed routing remains onboard, not on the breadboard.
5. Mouser US is the preferred accessory supplier; DigiKey US is secondary.
6. Pico 2 plus existing Cowbell is a separate optional video experiment, not a
   dependency of P4-PC HDMI. No Pico-to-P4 protocol has been selected or proven.

## Task files and evidence

[Bucket index](P4PC-001/README.md), [purchase/accessory record](P4PC-001/PURCHASING.md).
Earlier sourcing and schematic findings remain in
[RESEARCH-004](RESEARCH-004/RESULTS.md); do not erase their uncertainty or dates.
Future pin tables, board configuration notes and qualification reports belong
in this bucket. Private bench details remain in HARDWARE.local.md.

Related proposed stereo-streaming study: [AUDIO-001](AUDIO-001.md), using the
existing bench and network output first; independent of P4-PC arrival.

## Deferred mouse follow-on — 2026-09-20

Author defers all current mouse-function work until this board is available
and P4 EDP can offer physical USB mouse input. At that point scope USB hub/HID
mouse acquisition, retained stock mouse commands/cursor behavior and mouse
packets to EMOS over the admitted UART path. Keep correct absent-device behavior
within that future scope. This is a follow-on to board bring-up, not permission
to implement or test now. Later Console8 testing should include the Author's
one available PS/2 mouse through mainboard VDP. PORT-003 retains the known
command/reply inventory until this deferred work resumes.

## Offline reference library

**P4PC-001-DOC01** [x] Vendor official board documentation with provenance and
install clean upstream example/source checkout. [Reference index](../hardware/esp32-p4-pc/README.md)
records commit, scope, licensing and searchable derivatives; machine-local links
are in the ignored reference record. No toolchain installation or bench change.

## HDMI reuse research

[Existing driver map](../hardware/esp32-p4-pc/HDMI-DRIVERS.md): Espressif LT8912B
driver and Olimex production-test integration already exist in the local clone.
Use as the starting point for PC06; no new signalling implementation or change
to EDP framebuffer semantics implied. Integration remains unstarted.

## Deferred aspect-ratio research

[RESEARCH-005](RESEARCH-005.md) retains supplied mainboard VGA pillarboxing
research and the separate question of aspect-preserving P4 HDMI/DSI output.
Its suggested 720p experiment is not an adopted output architecture.


Physical VGA on the current P4 is a separate deferred interim-output idea. The
[P4 VGA research lead](RESEARCH-005.md#deferred-p4-vga-output-lead--2026-09-21)
records P4VGA565, known limitations and the prospective FabGL scanline reuse seam.
It does not change the HDMI bring-up priority or authorize hardware work.

## Received LCD, independent DevKit exploration

The Author reports receipt of MIPI-LCD2.8-640X480. [LCD-001](LCD-001.md)
owns revision identification and direct LCD exploration on the current DevKit.
This does not establish receipt of the P4-PC or qualify its HDMI output.
