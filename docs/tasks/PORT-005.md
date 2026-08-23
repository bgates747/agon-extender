# PORT-005 — Implement the EDU processed-input injection adapter

## State

- Status: Not started — registered from SETUP-004 Work 1.f
- Started: --
- Finished: --

## Intent

Implement the accepted Work 1.f proof-of-concept boundary. Replace official
VDP input integration's direct FabGL keyboard, mouse, and PS/2-controller
bindings with a narrow EDU input-injection adapter. An EDU-aware eZ80
application reads processed input through the stock onboard-VDP path and
forwards selected events explicitly to Extender.

## Authority and inputs

- [SETUP-004 Work 1.f](SETUP-004.md#work-1f-execution-record) and its generated
  input inventory.
- [ADR-0013](../decisions/ADR-0013-vdp-survey-integration-boundaries.md),
  especially decisions 26–28.
- [ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md),
  especially decisions 23–24.
- [Current architecture](../architecture.md).
- [PORT-002 source-selection work](PORT-002.md).

## Required outcomes

1. Define versioned EDU operations for injecting processed keyboard and mouse
   events without exposing FabGL physical-device objects.
2. Update EDP-local input variables, buffered callbacks, control-key and
   paged-mode logic, logical mouse state, and cursor effects from injected
   events where the selected proof-of-concept profile requires them.
3. Do not automatically emit `PACKET_KEYCODE` or `PACKET_MOUSE` back to the
   eZ80 application that forwarded an event. Keep packet emission as an
   explicit later routing-policy capability.
4. Preserve stable official event, packet, modifier, virtual-key, mouse-field,
   callback, and state semantics needed by later compatibility profiles.
5. Exclude vdp-gl PS/2 controller, physical keyboard and layout engine, and
   physical mouse engine translation units from the P4 build while retaining
   their complete source in the vendor tree.
6. Retain only shared virtual-key, keyboard-event, mouse-event, status, cursor,
   and other type vocabulary actually required by selected code.
7. Add deterministic host-side tests for event injection, state updates,
   callbacks, control-key/paged-mode effects, cursor behavior, ordering,
   duplicate suppression, and non-echo behavior.

## Dependencies and gates

- Complete SETUP-004 before implementation.
- PORT-002 must represent the omitted physical input sources as vendored but
  excluded without losing required shared declarations.
- The proof of concept does not depend on transparent routing or modified MOS.
- `SETUP-005-D007` governs any more automatic v1 route and must not be presumed
  by this task.
- QUAL-001 must identify the mode-specific input, state, callback, cursor,
  packet, and sysvar obligations before the injection contract is frozen.
- PORT-008 is required before an EDU-aware Agon application can physically
  inject events through the selected Extender transport; deterministic host
  adapter work may precede it.
- Define the EDU injection command format and acceptance fixtures with the
  Author before coding.
