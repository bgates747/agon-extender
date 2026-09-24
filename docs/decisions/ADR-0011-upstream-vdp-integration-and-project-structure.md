# ADR-0011 — Maintain upstream VDP fidelity and separate project-owned structure

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-20
- Documentation reconciled: 2026-09-24
- Related task: SETUP-003

## Current applicability

The recorded import baseline is VDP `v2.16.0`; this is not a claim that it
remains the newest upstream release. New imports follow the tagged-release
policy below. The [build guide](../building.md#which-files-actually-get-compiled)
identifies the maintained console selection; the
[dependency graph](../dependencies/README.md#model-scope-versus-deployed-builds)
covers its recorded profiles, not every later deployed console overlay.
Neither a graph nor this decision proves a complete current compatibility delta.

The accepted [rendering fidelity rule](../architecture.md) also retains
reusable native framebuffer algorithms and, for the first faithful port,
upstream behavior including suspected bugs. This decision does not authorize
upstream bug fixes or renderer redesign as incidental cleanup.

## Context

Extender begins from the official Agon VDP and guarantees backward
compatibility. New official releases must be incorporated throughout the life
of the project. The upstream firmware is unusually coupled: almost all
implementation is defined in `.h` files and assembled through textual inclusion
into one effective translation unit. Its apparent file boundaries are not
independent C++ module boundaries.

Reorganizing that source into a locally preferred structure would create a
permanent private architectural fork. Every upstream update would then require
reconstructing upstream changes inside a differently named, formatted, and
partitioned codebase. The maintenance cost and merge risk outweigh the benefit
of cleaning up inherited structure.

At the same time, project-owned code does not need to reproduce upstream's
header-defined style. It can begin with conventional C++17 boundaries and remain
mechanically distinguishable from imported compatibility code.

SETUP-003 also established working conventions for official-source baselines,
generated architectural inventories, local generators, factual précis
documents, and task-document scope. These conventions support the same goal:
keep upstream facts reproducible and project decisions visible without
accumulating unnecessary planning or migration narrative.

## Decision

### Upstream release baseline

1. Source analysis and imports use the latest official tagged Agon VDP release,
   not the tip of `main` or an arbitrary recent commit.
2. Record both the release tag and its immutable commit. The present baseline
   is `v2.16.0` at
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`.

### Upstream source fidelity

1. Preserve upstream directory paths, filenames, extensions, formatting,
   include order, symbols, and header-defined implementation wherever the P4
   target permits.
2. Do not reorganize upstream `.h` implementation into `.hpp` and `.cpp` files
   for style, modularity, testability, or cleanup.
3. Do not perform gratuitous renaming, reformatting, abstraction, or source
   movement in the upstream-shaped tree.
4. Make only changes required to build or behave correctly on the P4, or to
   connect an accepted Extender feature through an explicit integration seam.
5. Keep every upstream-file modification minimal, prominent, attributable, and
   mechanically auditable against the recorded release.
6. For every imported release, retain a complete compatibility delta between
   the pristine tagged source and the project tree.

This is a permanent maintenance policy, not a temporary restriction for the
first port.

### Project-owned C++ structure

1. Project-owned firmware code is C++17 unless a specific external interface or
   accepted technical constraint requires otherwise.
2. Use `.hpp` files for declarations and interfaces and `.cpp` files for
   implementations.
3. Do not place project-owned implementation in headers merely to imitate the
   upstream VDP style.
4. Keep project-owned code visibly separate under `vdp/video/extender/` in
   accordance with ADR-0001.
5. Keep connections between project-owned modules and upstream-shaped code
   narrow, explicit, and reviewable.

### Official-source documentation and generated evidence

1. The official VDP précis describes only facts about the selected official
   firmware release and its declared dependencies. Extender recommendations,
   source disposition, and design proposals do not belong in that document.
2. Structural inventories are primarily concise agent references. Prefer
   deterministic YAML or JSON generated from Git, build, compiler, and binary
   evidence over tutorial prose or inferred file descriptions.
3. Handwritten architectural summaries record relationships, caveats, and
   limitations that generators cannot establish reliably; they do not duplicate
   machine-generated inventories.
4. Keep explanatory glossary material minimal and specific to terms needed to
   interpret the project or generated evidence.

### Tool and repository organization

1. Reserve top-level `scripts/` for recurring project operations such as
   building, deployment, qualification, and other ongoing workflows.
2. Place one-purpose documentation or analysis generators beside the artifacts
   they generate.
3. Every generated inventory records its generator path and version, input
   release identity, relevant tool versions, and a reproducible invocation.

### Task and planning documents

1. Tracked task documents emphasize current work, concrete requirements,
   accepted decisions, and durable evidence.
2. Do not preserve routine task rearrangement, outline migration, or “this used
   to live elsewhere” narration unless that history affects implementation or
   interpretation.
3. Speculative or cognitively premature planning may remain in ignored scratch
   notes until the Author chooses to promote it into active tracked work.
4. A body of work that cannot be reviewed and executed comfortably as a
   subtask receives its own stable task identifier.

## Rationale

1. Structural fidelity makes upstream changes recognizable and reduces every
   future release update to the smallest practical compatibility merge.
2. Separating project-owned C++ prevents inherited coupling from spreading into
   new code.
3. Tagged baselines and deterministic inventories let present and future agents
   distinguish source fact from memory, inference, or stale planning.
4. Localizing one-purpose generators keeps routine operational tooling easy to
   find.
5. Concise task documents retain actionable information without becoming a
   history of their own editing process.

## Consequences

1. The project accepts the upstream VDP's unconventional `.h`-only
   implementation structure and coupling for the duration of the port.
2. Some inherited code will remain difficult to compile, test, or reason about
   independently.
3. P4 integration may require carefully annotated edits inside coupled upstream
   files, but those edits must remain narrower than a structural rewrite.
4. Code review must enforce different conventions in the upstream-shaped and
   project-owned portions of the tree.
5. SETUP-003 inventories become the reference baseline for measuring later
   imports and compatibility deltas.
