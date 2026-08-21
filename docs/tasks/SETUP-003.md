# SETUP-003 — Generate the official VDP structural inventory

## State

- Status: In progress — Work 1, 2, 4, 5, and 6 complete; Work 3 paused at its
  unmodified-build review gate

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
4. [x] Generate `compile_commands.json` with PlatformIO's `compiledb` target. Use
   compiler dependency output or `clang-scan-deps` to record the actual include
   graph. Because upstream implementation is heavily header-defined, retain a
   controlled preprocessor/include-tree summary for `video.ino`.
5. [x] Generate a machine-readable symbol index with Universal Ctags JSON or a
   Clang-based equivalent. At minimum enumerate functions, methods, classes,
   structs, enums, macros, global definitions, `extern` declarations, and their
   owning files.
6. [x] Generate a focused **portability and ownership inventory**. Its purpose is
   to support P4 port planning and SETUP-004 disposition decisions, not to
   catalog every construct in the codebase.

   Mechanical extraction and source-validated semantic relationship review are
   complete. The combined machine-readable inventory is
   [`SETUP-003/generated/portability.yaml`](SETUP-003/generated/portability.yaml),
   with a compact review at
   [`SETUP-003/portability-review.md`](SETUP-003/portability-review.md).

   For each material runtime subsystem, record relationships sufficient to
   answer:
   - what physical hardware or platform facility the code owns;
   - what startup path, task, callback, interrupt, or command handler activates
     it;
   - which global/static owning objects and shared state keep it alive;
   - which FabGL, Arduino, ESP32, FreeRTOS, PSRAM, or memory-capability
     facilities it uses directly;
   - which conditional-compilation regions select or exclude it;
   - which VDP commands, packets, audio/input behavior, or other externally
     visible features depend on it; and
   - whether the evidence suggests it can be omitted cleanly or requires a
     retained interface or replacement boundary.

   Prioritize:
   - startup and task entry functions, task creation, callbacks, and interrupt
     handlers;
   - global/static subsystem owners;
   - direct architecture and framework dependencies;
   - PSRAM and capability-specific allocation; and
   - compile-time switches and protocol constants tied to hardware behavior.

   Do not exhaustively enumerate mutexes, queues, `Stream` uses, constants, or
   other constructs that have no demonstrated bearing on ownership,
   portability, lifecycle, externally visible behavior, or omission fallout.
   Use targeted machine extraction plus source validation; preserve useful
   relationships rather than raw search matches. Stop for Author review of the
   proposed extraction and output shape before starting this work.
7. From a successful ELF build, capture `size`, `nm`, `readelf`, and a linker
   map sufficient to associate significant code/data symbols with source files
   and libraries. Do not retain bulky disassembly or raw preprocessor output
   unless it provides unique durable evidence.
8. Generate compact dependency views from the structured data: file include
   fan-in/fan-out, strongly connected groups where practical, subsystem
   dependencies, and task/callback entry relationships. Use Graphviz only for
   diagrams that remain legible and materially improve navigation.
9. Store task scripts, evidence, and deterministic outputs under
   `docs/tasks/SETUP-003/`, favoring YAML or JSON plus small Markdown indexes.
   Provide reproducible task-local scripts rather than undocumented ad hoc
   commands. Promote an output into architecture documentation only when it
   becomes a durable reference beyond this task.
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
- `portability.yaml` — mechanical candidates plus reviewed subsystem ownership,
  lifecycle, coupling, externally visible behavior, and portability boundaries;
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
