# SETUP-004 — Determine upstream I/O driver disposition

## State

- Status: In progress — VDU compatibility inventory complete; subsystem
  disposition survey pending
- Started: 2026-08-20 20:52 EDT
- Finished: --

## Intent

Review the official VDP and vdp-gl hardware-facing I/O facilities and decide
which Extender must retain, replace, stub, omit, or defer. Reduce unnecessary
ESP32-PICO-to-P4 porting while preserving the externally observable behavior
required for VDP backward compatibility.

Begin from the documented VDU interface rather than implementation internals.
The Author will review each command or command family in
[`SETUP-004/VDU-inventory.md`](SETUP-004/VDU-inventory.md) and state which
observable behavior Extender promises to preserve. Driver disposition follows
from that product-level compatibility boundary.

This is a survey and disposition task. It does not implement driver removals,
replacement drivers, compatibility adapters, or build-selection changes.

## Authority and inputs

- [ADR-0013 — VDP survey findings and integration boundaries](../decisions/ADR-0013-vdp-survey-integration-boundaries.md)
- [SETUP-003 — official VDP structural inventory](SETUP-003.md)
- [SETUP-003 generated compiler and include evidence](SETUP-003/generated/)
- Official VDP release `v2.16.0` at
  `c7ac293d2aa81ddfa693390549bcd909069c8fc3`
- vdp-gl tag `all-the-plots` at
  `ac2dd5986daf496c43ae8e7fe41836274aec54a0`

## Required dispositions

Assign exactly one provisional disposition to every material hardware-facing
subsystem:

- **Retain:** required substantially as implemented, subject to P4 adaptation.
- **Replace:** behavior is required but implementation becomes project-owned.
- **Stub:** an interface must remain, but no physical implementation is needed.
- **Omit:** neither implementation nor compatibility surface is required in the
  Extender image.
- **Defer:** evidence is insufficient; record the exact unresolved dependency
  or product decision.

Provisional dispositions become accepted architecture only after Author
review. Any accepted decision with broad or durable consequences receives an
ADR or an amendment to ADR-0013.

## Work

1. Derive a candidate inventory from compiler evidence, source includes,
   PlatformIO library selection, and targeted source searches. At minimum
   review:
   - PS/2 keyboard and mouse controllers;
   - FabGL VGA, composite-video, display-controller, and canvas drivers;
   - sound generators and physical audio output;
   - UART, GPIO, ADC, I2C, SPI, timers, interrupts, and ULP facilities;
   - RTC and peripheral-device drivers;
   - network, updater, and transfer facilities;
   - storage and filesystem interfaces; and
   - Arduino, ESP-IDF, and FreeRTOS hardware abstractions used by those areas.
2. For each candidate, record:
   - owning project and source files;
   - selected translation units and header-defined implementation;
   - direct hardware and architecture dependencies;
   - startup, task, interrupt, callback, and global-state connections;
   - VDP commands, responses, status packets, or application-visible behavior;
   - present physical owner: main board, onboard VDP, Extender, or none;
   - proposed disposition and rationale; and
   - dependencies on other disposition decisions.
3. Trace each proposed omission far enough to identify compile/link fallout.
   Distinguish removing an independently selected translation unit from
   severing a header-defined or global-state dependency inside the effective
   VDP translation unit.
4. Identify facilities that are not needed physically but whose protocol
   surface must remain for backward compatibility. Recommend a project-owned
   adapter, inert stub, explicit unsupported response, or continued delegation
   to the onboard VDP as appropriate.
5. Produce a compact review matrix grouped by subsystem. Keep unresolved
   decisions here rather than in an ADR.
6. Present the matrix to the Author in manageable groups and record accepted
   dispositions. Create follow-on implementation tasks only after review.

## Initial accepted boundary

Per ADR-0013, FabGL PS/2 controller and physical keyboard/mouse support will
not be ported or built for Extender. Existing input responsibilities remain
with the Agon main board and onboard VDP. Any future Extender input facility is
project-owned. The survey must still trace protocol and compile-time coupling
before assigning the precise **Omit**, **Stub**, or **Replace** mechanics.

Retain keyboard and mouse command parsing and externally visible protocol state
needed by exclusive compatibility mode, while leaving cooperative-mode routing
unresolved. This retained surface does not reverse the physical-driver boundary:
upstream PS/2 acquisition remains excluded, and couplings such as sprite command
`&40` calling mouse-owned cursor code require a project-owned adapter or
delegation boundary.

Retain the complete buffered-callback facility unconditionally. Commands 80 and
81 modify EDP-local registration state, while callback execution can alter or
suppress later protocol packets. Exclusive compatibility mode requires those
indirect MOS-visible effects to match the official VDP behavior.

The Extender application interface is a stable, explicit EDU API with both
directly linked and optional resident-service implementations. The resident
service does not intercept stock VDU restart paths. See
[ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md).

### Known diagnostic-output constraint

Official VDP `v2.16.0` implements buffered command 128 with
`force_debug_log()` through `DBGSerial`, which is stock UART0 on ESP32 pins 3
and 1. It reports the stream count, prints transform matrices in readable form,
or emits the entire first buffer stream as hexadecimal. It sends no VDP protocol
packet and modifies no MOS sysvar.

The P4 port must bind this command to an explicit EDP diagnostic console or log
sink rather than inherit the upstream UART mapping. Because output is
synchronous and unbounded by command semantics, large buffers can stall VDU
processing and may expose task-latency or watchdog problems. Preserve that
behavioral warning during implementation and qualification.

## Outputs

- A machine-readable driver/subsystem inventory under
  `docs/tasks/SETUP-004/generated/`.
- A concise review matrix under `docs/tasks/SETUP-004/`.
- Task-local reproducible extractors under `docs/tasks/SETUP-004/scripts/` if
  SETUP-003 evidence is insufficient.
- Follow-on implementation tasks and accepted ADR updates after review.

## Review gate

Stop after producing and explaining the provisional disposition matrix. Do not
alter source selection, add stubs, or modify VDP/vdp-gl code until the Author
has reviewed the affected subsystem group.
