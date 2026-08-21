# ADR-0013 — VDP survey findings and integration boundaries

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-20
- Related task: SETUP-003

## Context

The SETUP-003 source and build surveys show that the official VDP firmware
owns peripheral facilities needed by the stock Agon VDP. These include FabGL's
PS/2 controller and keyboard/mouse paths, low-level ESP32 ULP support, and
other hardware-facing I/O code.

Extender supplements an Agon whose main board and onboard VDP continue to own
their existing physical input and peripheral responsibilities. Backward
compatibility with the official VDP does not require duplicating every stock
VDP hardware implementation on the P4. Blindly compiling all such facilities
would increase the P4 porting surface and preserve dependencies on ESP32-only
hardware that Extender does not use. The first survey build exposed one such
case when `vdp-gl/src/comdrivers/ps2controller.cpp` included the unavailable
ESP32-specific `esp32/ulp.h`.

## Decision

1. Treat the official VDP source survey as both a compatibility inventory and
   a scope-selection exercise. Inclusion in upstream source does not by itself
   require inclusion in Extender firmware.
2. Do not port or build FabGL's PS/2 controller or its physical keyboard and
   mouse implementation for Extender.
3. More generally, exclude upstream hardware-facing I/O facilities when the
   Agon main board or onboard VDP remains responsible for that hardware and
   Extender has no defined use for the implementation.
4. Preserve externally observable VDP protocol and application behavior where
   backward compatibility requires it. Separate that compatibility obligation
   from reuse of the upstream physical driver that originally supplied the
   behavior.
5. Extender-specific input facilities, if introduced, are project-owned. Put
   their interfaces and implementations in the Extender-owned source boundary;
   do not force them through unused FabGL PS/2 or stock peripheral machinery.
6. Use explicit build selection, adapters, or narrow compatibility boundaries
   to omit unused upstream facilities. Do not perform broad source cleanup or
   restructure vendored upstream code merely because part of it is excluded.
7. Record each material omission discovered during SETUP-003 with the upstream
   subsystem, the retained compatibility surface, and the replacement owner or
   reason no replacement is required.

## Rationale

1. The stock main board remains the authority for hardware it already serves;
   duplicating those drivers on Extender adds no useful compatibility.
2. Removing unused hardware implementations reduces architecture-specific
   porting work without weakening the promise to preserve relevant VDP-visible
   behavior.
3. Project ownership of new input paths allows a deliberate P4-native design
   instead of inheriting ESP32 and PS/2 constraints accidentally.
4. Explicitly recording exclusions prevents an omitted source file from being
   mistaken for an incomplete or forgotten port.

## Consequences

1. A successful Extender build will not necessarily compile every translation
   unit supplied by vdp-gl or the official VDP dependency graph.
2. Build manifests and structural inventories must distinguish code available
   in vendored source from code selected into Extender firmware.
3. Compatibility analysis must identify any VDP commands or responses coupled
   to excluded input drivers and decide whether they remain onboard-VDP-only,
   require a stub, or require a project-owned adapter.
4. Future Extender input hardware or network input features require their own
   architecture and qualification decisions.
