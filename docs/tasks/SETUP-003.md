# SETUP-003 — Generate the official VDP structural inventory

## State

- Status: In progress — Work 1 and 2 complete; remaining work not started

## Intent

Create a reproducible, machine-generated structural inventory of the latest
tagged official VDP release. The outputs are primarily an agent cheat sheet and
evidence source. Prefer compiler/build evidence over filename inference and
avoid duplicating generated facts in explanatory prose.

This task describes only the official VDP and its declared dependencies. It
does not make Extender design, portability, or source-modification decisions.

## Inputs

- Official VDP source: [agon-vdp](https://github.com/AgonPlatform/agon-vdp)
- Official documentation: [agon-docs](https://github.com/AgonPlatform/agon-docs)
- Release baseline: `v2.16.0` at
  `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, verified against the official
  remote tags on 2026-08-20 and recorded in
  `docs/architecture/vdp-upstream-precis.md`
- Maintenance and structural conventions:
  [ADR-0011](../decisions/ADR-0011-upstream-vdp-integration-and-project-structure.md)
- Dependency acquisition and version policy:
  [ADR-0012](../decisions/ADR-0012-vendored-release-dependencies.md)

## Work

1. [x] Record the latest official release tag, its immutable commit, declared
   dependency identities, tool versions, generator versions, and exact
   regeneration command in every generated output or its common manifest.
2. [x] Generate the canonical tracked-file inventory with `git ls-files` and
   `rg --files`, grouped by directory, extension, size, and line count.
3. Attempt a pristine whole-project P4 build:
   - use official VDP release `v2.16.0` and its exact selected dependency
     releases;
   - add only a separate experimental PlatformIO environment needed to select
     the qualified P4 board profile and hybrid Arduino/ESP-IDF framework;
   - make no VDP or dependency source fixes before the first complete build
     attempt;
   - do not upload or otherwise mutate the physical board;
   - capture PlatformIO's machine-readable metadata, verbose compiler and
     linker invocations, flags, defines, include paths, selected sources,
     libraries, generated artifacts, and complete first error set;
   - distinguish configuration failures from source/compiler failures;
   - classify each failure by owning project, file, subsystem, platform
     assumption, and probable portability boundary; and
   - stop for review of the unmodified-build evidence before correcting the
     first source error or beginning iterative port work.
4. Generate `compile_commands.json` with PlatformIO's `compiledb` target. Use
   compiler dependency output or `clang-scan-deps` to record the actual include
   graph. Because upstream implementation is heavily header-defined, retain a
   controlled preprocessor/include-tree summary for `video.ino`.
5. Generate a machine-readable symbol index with Universal Ctags JSON or a
   Clang-based equivalent. At minimum enumerate functions, methods, classes,
   structs, enums, macros, global definitions, `extern` declarations, and their
   owning files.
6. Generate focused structural inventories for:
   - startup and task entry functions;
   - FreeRTOS task handles, task creation, mutexes, queues, callbacks, and
     interrupt handlers;
   - globals and static owning objects;
   - Arduino `Stream` users and implementations;
   - direct FabGL, Arduino, ESP32, and FreeRTOS dependencies;
   - PSRAM allocators and memory-capability calls;
   - conditional-compilation symbols and regions; and
   - VDP command, packet, audio, input, and feature constants.
7. From a successful ELF build, capture `size`, `nm`, `readelf`, and a linker
   map sufficient to associate significant code/data symbols with source files
   and libraries. Do not retain bulky disassembly or raw preprocessor output
   unless it provides unique durable evidence.
8. Generate compact dependency views from the structured data: file include
   fan-in/fan-out, strongly connected groups where practical, subsystem
   dependencies, and task/callback entry relationships. Use Graphviz only for
   diagrams that remain legible and materially improve navigation.
9. Store durable, deterministic outputs under
   `docs/architecture/generated/`, favoring YAML or JSON plus small Markdown
   indexes. Provide one regeneration script rather than undocumented ad hoc
   commands.
10. Keep `docs/architecture/vdp-upstream-precis.md` as the compact agent-facing
    index to generated evidence and the place for relationships or caveats that
    tools cannot establish reliably. Do not add Extender design or port
    recommendations.

## Proposed outputs

- `manifest.yaml` — source, dependency, tool, and generation provenance;
- `files.yaml` — canonical file inventory and source statistics;
- `build.yaml` — PlatformIO environment, flags, libraries, and outputs;
- `symbols.yaml` — indexed declarations and definitions;
- `includes.yaml` — compiler-derived include/dependency graph;
- `globals.yaml` — global/static state and ownership clues;
- `tasks.yaml` — task, queue, mutex, callback, and interrupt inventory;
- `protocols.yaml` — command/packet constants and handler cross-references;
- `memory.yaml` — ELF sections and significant symbol ownership; and
- compact SVG dependency diagrams only where useful.

## Tool gate

Start with tools already installed. Before adding packages, report which
optional tools are absent, what unique output each would provide, and whether a
small repository-local extractor can produce a narrower and more reproducible
result.

## Dependency baseline work

The official `v2.16.0` build declares vdp-gl by immutable tag `all-the-plots`
at `ac2dd5986daf496c43ae8e7fe41836274aec54a0`. ESP32Time and CRC remain version
ranges. Before build-derived inventories or source import:

1. Determine the exact dependency versions resolved by a clean official
   `v2.16.0` build.
2. Record the resulting immutable commits, versions, package hashes, and source
   licenses as evidence.
3. Compare that resolved set with any dependency metadata produced by the
   official release workflow.
4. Vendor the exact selected releases under `vdp/vendor/` according to
   ADR-0012, retaining upstream structure, licenses, and provenance.
5. Replace range- or network-based build inputs with the local vendored
   identities and verify that dependency resolution no longer changes the
   build.

## Review gate

Stop after auditing tool availability and refining the proposed outputs. Obtain
Author approval before installing optional tools or generating the complete
inventory.
