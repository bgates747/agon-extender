# ADR-0008 — Add CMake only when the hybrid build proves it necessary

## Status

Accepted.

## Context

The accepted firmware model uses PlatformIO as the familiar outer workflow and
combines Arduino with ESP-IDF underneath it. ESP-IDF is CMake-based, and
pioarduino can generate the required hybrid project and component structure.
Adding project-authored CMake prematurely would create another build interface
to understand and maintain before its purpose is known.

The port also depends on preserving official `agon-vdp` names and relative
source locations. Unnecessary component restructuring would make upstream
comparison and future synchronization harder.

## Decision

Begin the minimal hybrid canary without project-authored `CMakeLists.txt` files.
Let PlatformIO generate and orchestrate the underlying hybrid build.

Add tracked CMake only when build evidence identifies a requirement that cannot
be represented adequately through `platformio.ini`, the custom board
definition, SDK defaults, normal source placement, or PlatformIO scripting.

If required, introduce the smallest CMake boundary that solves the demonstrated
problem without moving or renaming upstream-compatible VDP files.

## Evidence that may justify CMake

A later CMake file may be justified by a concrete need to register a native IDF
component, declare component dependencies, expose generated headers, control
source discovery that PlatformIO cannot express, or integrate an IDF facility
whose supported interface requires component metadata.

Preference alone, anticipation of possible future complexity, or a desire to
make the project resemble a pure ESP-IDF application is not sufficient.

## Rationale

1. PlatformIO remains the single visible build workflow familiar from official
   `agon-vdp`.
2. Delaying CMake keeps the initial canary focused on framework and hardware
   qualification.
3. Evidence-driven scaffolding avoids committing to an incorrect component
   model before the first build exposes the real boundary.
4. Minimal build metadata reduces divergence from the upstream source layout.

## Consequences

1. The initial tree may contain no `CMakeLists.txt` even though ESP-IDF is one of
   the selected frameworks.
2. Generated CMake files are build artifacts and are not tracked.
3. A later CMake addition requires documentation of the exact build failure or
   integration requirement it resolves.
4. If CMake becomes necessary, this ADR permits it without requiring a new
   architecture decision, provided the addition follows the stated boundary.
