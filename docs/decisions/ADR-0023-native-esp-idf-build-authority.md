# ADR-0023 — Use native ESP-IDF/CMake with Arduino as a component

- Status: Accepted
- Completeness: Partial
- Date: 2026-09-28
- Related task: BUILD-001
- Open-decision tracker: BUILD-001

## Context

The P4 firmware began as a PlatformIO Arduino project and later combined
Arduino and ESP-IDF under PlatformIO/SCons. Project source selection, dependency
locks, embedded assets, native ESP-IDF components and build identities were
added incrementally through PlatformIO pre-scripts.

The resulting hybrid build now has two materially different graphs. Generated
ESP-IDF CMake/Ninja metadata describes `.obj` nodes, while SCons separately
compiles and links `.o` nodes. The generated compilation database therefore
cannot authoritatively describe the linked project closure for static analysis
or maintenance. Preserving both orchestration layers also duplicates source,
configuration and dependency reasoning.

The firmware still depends materially on Arduino lifecycle and APIs. Removing
Arduino would turn build consolidation into a broad runtime port without a
demonstrated product benefit.

## Decision

Native ESP-IDF/CMake becomes the sole top-level build authority for maintained
P4 firmware. Retain the exact compatible Arduino-ESP32 release as a pinned
ESP-IDF component and preserve the Arduino `setup()`/`loop()` lifecycle during
the initial migration.

Use one neutral checked-in manifest as the authority for buildable profiles,
selected sources, configuration inputs, embedded assets and relevant compile
options. A project-owned wrapper validates that manifest, selects pinned
project-scoped ESP-IDF source and tools, prepares fresh profile-specific output
and invokes native `idf.py`. Generated CMake fragments are disposable outputs,
not editable authorities.

Validate migration through declared/compiled/linked graph agreement, exact
dependency and configuration records, explained artifact differences, host
controls and later Author-approved hardware equivalence. Do not presume binary
identity. Retain rollback and the current hybrid build until the Author accepts
cutover.

BUILD-001 owns unresolved profile disposition, detailed native layout,
implementation, validation and cutover. Production remains unchanged until a
separate accepted promotion.

## Consequences

1. ESP-IDF CMake, Ninja and the component manager compile and link the final
   P4 image; PlatformIO/SCons will leave the maintained path after accepted
   migration.
2. Arduino APIs and upstream-compatible VDP source structure remain available
   without making Arduino or PlatformIO the outer build authority.
3. ESP-IDF, its tools, Arduino-ESP32 and managed dependencies require exact
   source/tool identities and checked-in solver locks.
4. The native compilation database becomes eligible for AUDIT-010 only after a
   validator proves correspondence with linked project objects.
5. Following accepted BUILD-001 equivalence, native ESP-IDF/CMake is the
   operational development-build authority. PlatformIO procedures remain only
   for explicit bounded reproduction of identified hybrid evidence.

## Superseded decisions

This decision supersedes ADR-0002's selection of PlatformIO as the outer hybrid
build, ADR-0008's generated-CMake boundary and ADR-0009's PlatformIO wrapper as
the long-term maintained interface. Their rationale and transition evidence
remain historical. ADR-0003's exact pioarduino pin remains applicable to the
rollback build until BUILD-001 cutover disposes it.
