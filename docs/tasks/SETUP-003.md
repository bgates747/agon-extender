# SETUP-003 — Generate the official VDP structural inventory

## State

- Status: Proposed — Author review required before execution

## Intent

Create a reproducible, machine-generated structural inventory of the pinned
official VDP baseline. The outputs are primarily an agent cheat sheet and
evidence source. Prefer compiler/build evidence over filename inference and
avoid duplicating generated facts in explanatory prose.

This task describes only the official VDP and its declared dependencies. It
does not make Extender design, portability, or source-modification decisions.

## Inputs

- Official VDP source: [agon-vdp](https://github.com/AgonPlatform/agon-vdp)
- Official documentation: [agon-docs](https://github.com/AgonPlatform/agon-docs)
- Pinned VDP baseline recorded in
  `docs/architecture/vdp-upstream-precis.md`

## Work

1. Record the immutable upstream VDP commit, declared dependency identities,
   tool versions, generator versions, and exact regeneration command in every
   generated output or its common manifest.
2. Generate the canonical tracked-file inventory with `git ls-files` and
   `rg --files`, grouped by directory, extension, size, and line count.
3. Capture PlatformIO's machine-readable project metadata and verbose build
   configuration, including environment, framework, compiler flags, defines,
   include paths, libraries, source selection, and generated artifacts.
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

## Review gate

Stop after auditing tool availability and refining the proposed outputs. Obtain
Author approval before installing optional tools or generating the complete
inventory.
