# SETUP-004 Work 1 analysis process

## Purpose

This process is applied independently and consistently to Work 1.a through
Work 1.h. It discovers material candidates, gathers the evidence required by
SETUP-004, exposes incomplete analysis, and only then supports provisional
retain/replace/stub/omit/defer recommendations.

The process must distinguish facts mechanically recoverable from the pinned
source and build from interpretations requiring source review or product
judgment. A generated record may never silently convert an unresolved
relationship into an absent dependency.

## Immutable inputs

Each run is tied to the source identities already recorded by PORT-001:

- official `agon-vdp` release `v2.16.0`;
- vdp-gl tag `all-the-plots`;
- ESP32Time release `2.0.6`; and
- CRC release `1.0.4`.

The extraction scripts consume these tracked artifacts:

- `SETUP-003/generated/compile-commands.json` for selected translation units;
- `SETUP-003/generated/includes.yaml` for direct and transitive preprocessing;
- `SETUP-003/generated/symbols.yaml` for definitions and declarations;
- `SETUP-003/generated/portability.yaml` for platform occurrences and reviewed
  runtime facts;
- `SETUP-003/generated/dependency-views.yaml` for file-level coupling;
- `docs/dependencies/generated/code-graph.yaml` for typed source, call, state, task,
  callback, packet, platform, and physical-facility relationships;
- `SETUP-004/VDU-inventory.md` for the accepted compatibility surface; and
- accepted ADRs and open task decisions for project ownership and architecture.

Exact tagged source is consulted read-only for targeted review when generated
evidence is ambiguous or incomplete. Machine-local source paths never enter
tracked output.

## Artifact layers

### Scope input

`scope/work-<item>.yaml` is a small reviewed input containing:

- Work item ID and title;
- platform APIs, headers, source areas, graph node kinds, and search terms that
  seed discovery;
- candidate-grouping rules;
- explicit out-of-scope boundaries and the Work item that owns each boundary;
- source identities; and
- any accepted architecture that constrains ownership without deciding the
  candidate disposition automatically.

Scope rules select evidence for inspection. They are not evidence that a
candidate is runtime-reachable and do not imply a disposition.

### Mechanical output

`generated/work-<item>/candidates.yaml` records every discovered candidate and
why it entered the candidate universe. `mechanical-facts.yaml` records facts
that can be reproduced without judgment. `coverage.yaml` reports every scoped
source occurrence or graph node that was assigned, excluded with a reason, or
left unresolved.

### Reviewed evidence

`evidence/work-<item>-<subject>.yaml` adds only conclusions requiring semantic
review or product knowledge. Each conclusion cites exact source evidence,
generated record IDs, or accepted project decisions. Unknowns remain explicit.

### Aggregate output

`generated/subsystem-inventory.yaml` merges validated mechanical facts and
reviewed interpretations. `disposition-matrix.md` is its compact human review
projection. Neither file introduces new conclusions.

## Script design

### `extract-work-item.py`

Command:

```sh
.venv/bin/python docs/tasks/SETUP-004/scripts/extract-work-item.py \
  --work-item SETUP-004.1.a
```

Responsibilities:

1. Validate the scope file and every immutable source identity.
2. Discover platform APIs, physical facilities, source files, symbols,
   includes, and unresolved graph records matching the scope seeds.
3. Group related low-level occurrences into stable material candidates while
   retaining every constituent graph and evidence ID.
4. Classify source participation as:
   - selected translation unit;
   - header-defined implementation reached by a selected translation unit;
   - declaration-only/header coupling;
   - compiled but not proven runtime-reachable; or
   - available upstream but not selected.
5. Traverse matched graph facilities backward to their consumers and inspect
   their outgoing relationships to gather direct hardware, architecture,
   startup, task, interrupt, callback, state, command, packet, and
   visible-behavior relationships.
6. Stop traversal at explicit subsystem boundaries and record every excluded
   continuation in the candidate rather than silently truncating it.
7. Emit deterministic candidate and mechanical-fact files with input hashes,
   generator version, exact regeneration command, and no machine-local paths.

The extractor proposes no physical owner and no disposition.

### `audit-work-item.py`

Command:

```sh
.venv/bin/python docs/tasks/SETUP-004/scripts/audit-work-item.py \
  --work-item SETUP-004.1.a
```

Responsibilities:

1. Verify that every scoped platform occurrence, include, selected source
   unit, graph node, and relevant unresolved record is assigned to exactly one
   candidate or has one explicit exclusion.
2. Reject duplicate candidate membership unless an intentional cross-cutting
   relationship names one primary owner and the dependent candidates.
3. Reject unknown graph/evidence IDs and stale source spans.
4. Require every candidate to contain all mechanically answerable SETUP-004
   fields.
5. Require an explicit review gap for every field automation cannot establish.
6. For proposed omissions, require compile/link fallout evidence covering
   selected translation units, reverse includes, inbound symbol references,
   calls, and state edges.
7. Emit `coverage.yaml` with assigned, excluded, unresolved, and unreviewed
   counts. A Work item cannot close while any unclassified residual remains.

### `generate-subsystem-inventory.py`

The projection layer:

1. consume validated mechanical outputs as well as reviewed evidence;
2. requires reviewed source and implementation highlights to have mechanical
   provenance, while retaining the complete mechanical and reviewed layers
   separately;
3. require every final candidate to pass the field-completeness rules below;
4. retain provenance separately for mechanical facts, reviewed source
   conclusions, accepted product decisions, and provisional recommendations;
5. generate the aggregate YAML and Markdown matrix deterministically; and
6. refuses projection unless the coverage audit passes and every audited input
   hash remains current, and labels projected Work items as awaiting Author
   review rather than complete.

## Required-field evidence plan

Every candidate must answer all eight SETUP-004 questions as follows.

### 1. Owning project and source files

Mechanical sources:

- PORT-001 source and file nodes;
- SETUP-003 file and symbol inventories; and
- immutable dependency identities.

Completion test: every implementation, declaration, and reviewed evidence span
names an owner and repository-relative path. No basename-only references or
machine-local paths are permitted.

### 2. Selected translation units and header-defined implementation

Mechanical sources:

- normalized compilation database;
- direct/transitive include graph;
- symbol definitions; and
- PlatformIO dependency selection.

Completion test: every source file is classified by build participation. A
header-only implementation names the selected translation unit or include
chain that brings it into the effective build.

### 3. Direct hardware and architecture dependencies

Mechanical sources:

- platform-API and physical-facility graph nodes;
- portability occurrences and conditional compilation;
- direct includes of ESP-IDF, Arduino, FreeRTOS, SoC, register, and architecture
  headers; and
- unresolved platform calls retained as review gaps.

Reviewed additions identify register assumptions, chip-generation constraints,
or hardware ownership that syntax cannot prove.

Completion test: every platform-facing edge is classified as portable API,
chip-specific API, peripheral-specific implementation, architecture-specific
code, or unresolved.

### 4. Startup, task, interrupt, callback, and global-state connections

Mechanical sources:

- PORT-001 typed graph and bounded slices;
- SETUP-003 reviewed runtime map; and
- call, read, write, task, timer, interrupt, and callback relationships.

Completion test: each connection class is present, even when empty. Empty means
the audit found no evidenced connection; unresolved evidence is listed
separately and never represented as empty.

### 5. VDP commands, responses, status packets, or visible behavior

Mechanical sources:

- reverse graph traversal from the candidate to command dispatches, packet
  sends, persistent state, and callbacks;
- VDU compatibility inventory; and
- PORT-001 command slices.

Reviewed source analysis supplies behavioral relationships absent from syntax,
including timing, ordering, resource limits, and indirect callback effects.

Completion test: each candidate lists direct, indirect, and absent visible
surfaces separately. Claims of no visible behavior require a completed reverse
reachability audit and targeted source search.

### 6. Present physical owner

This is reviewed product information, not a mechanical source conclusion. The
allowed owner vocabulary is:

- Agon main board;
- onboard VDP;
- Extender;
- shared, with named participants; or
- none.

Completion test: every candidate has one owner value and cites the accepted
architecture, hardware description, or Author decision supporting it.

### 7. Proposed disposition and rationale

Disposition is added only after Fields 1–6 and omission fallout are complete.
The value is exactly one of retain, replace, stub, omit, or defer. Rationale
must identify the compatibility obligation, physical owner, implementation
cost or constraint, and why the other plausible dispositions were rejected.

Completion test: `defer` names the exact missing evidence or open decision;
`omit` proves no required surface or names its surviving boundary; `stub` names
the interface and inert behavior; `replace` names the required behavior and
new owner; `retain` names any P4 adaptation still required.

### 8. Dependencies on other disposition decisions

Mechanical graph relationships provide candidate-to-candidate dependencies.
Reviewed records map those relationships to stable Work item, task-decision, or
ADR IDs.

Completion test: every dependency names a stable ID and states whether it
blocks disposition, blocks implementation only, or merely requires later
qualification. An empty dependency list is an affirmative reviewed result.

## Omission and replacement fallout

Every omit, stub, or replace proposal receives a dedicated fallout analysis:

1. Determine whether the candidate is an independently selected translation
   unit, header-defined implementation, declaration/API, global object, or
   runtime-only activation path.
2. Follow reverse include, symbol, call, state, task, interrupt, and callback
   edges to all selected consumers.
3. Record the first compile, link, startup, or runtime failure expected from
   direct removal.
4. Identify the narrow adapter, source filter, stub, ownership change, or
   retained interface required to sever the dependency.
5. Keep unproven fallout explicit. A future experimental build may validate the
   prediction, but SETUP-004 itself does not modify source selection or code.

## Per-item execution sequence

1. Write and review the Work item scope manifest.
2. Run mechanical candidate discovery and fact extraction.
3. Run the residual coverage audit.
4. Inspect unresolved records and perform bounded targeted source review.
5. Add reviewed physical ownership, visible behavior, fallout, dependencies,
   and provisional dispositions.
6. Regenerate and rerun the coverage audit.
7. Present the candidate group and matrix to the Author.
8. Record accepted dispositions and architectural consequences.
9. Mark the Work 1 subitem complete only when the Author accepts it and the
   coverage audit has no unclassified residuals.

## Current implementation status

The extractor, coverage audit, and projection generator are implemented for
the common Work 1 process. Work 1.a has 13 reviewed candidate records and a
passing coverage audit with no ambiguous or unclassified scoped evidence. The
Author accepted all 13 dispositions; named follow-on work preserves deferred
implementation, qualification, and architecture details.

Work 1.b has four reviewed candidate records and a passing coverage audit: 145
scoped items, 141 assigned and four explicitly delegated to Work 1.c, with no
ambiguous or unclassified evidence. The Author accepted both retained RTC
candidates and both device-driver omissions; the separate clock-policy question
was explicitly deferred to `SETUP-005-D008`.

Work 1.c has ten reviewed candidate records and a passing coverage audit: 703
scoped items, 507 assigned and 196 explicitly delegated to later subsystem
owners, with no ambiguous or unclassified evidence. All ten dispositions have
completed Author review, including the narrow P4-native replacement of
ESP32/Xtensa clock and cycle-counter internals.

The PORT-001 graph deliberately preserves unresolved lexical relationships.
Those IDs may appear in mechanically complete candidates without becoming
unclassified scope residuals: the extractor retains them as uncertainty, and
the reviewed layer may make only bounded conclusions supported by targeted
source inspection. Later Work 1 items reuse this distinction rather than
silently treating unresolved graph edges as absent behavior.
