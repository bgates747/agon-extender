# ADMIN-001 findings — centralized task dependency metadata

## Review status

- Inspection complete: 2026-08-24
- Task disposition: closed without prejudice 2026-08-24
- Source snapshot: `agon-fsim` tracked commit
  `dc9552d31f57f8926c4f8b0bd3f4ff165fd7f4c5`
- Recommendation: adapt the authority split and graph semantics; do not copy
  the hand-maintained Markdown representation unchanged
- Project changes authorized by this report: none

The Author retained Extender's present task system pending a concrete
cross-project implementation target. The recommendations below remain durable
research rather than accepted policy, rejected policy, or authorized work.

## Executive finding

`agon-fsim` does not store all task metadata in one file. It centralizes one
specific class of metadata—direct dependencies, entry predicates, accepted
evidence roots, milestone gates, dynamic planning nodes, and successor
effects—in `docs/task-dependency-gates.md`.

Three authorities remain separate:

1. `TODO.md` alone decides which unfinished work is actionable and in what
   order.
2. `docs/task-dependency-gates.md` alone states prerequisite and gate truth.
3. `docs/tasks/<TASK-ID>.md` retains each task's detailed execution contract,
   local dependencies, decisions, evidence, and results.

This separation is useful precedent for Extender. The present implementation
is nevertheless a manually maintained Markdown graph with no parser,
validator, schema, generator, or CI consumer. Its guarantees are procedural,
not mechanically enforced.

## Observed agon-fsim authorities

| Record | Observed authority |
|---|---|
| `TODO.md` | Sole unfinished-work register; immediate section is ordered and actionable, eventual section is retained but non-actionable. |
| `docs/task-dependency-gates.md` | Canonical graph of direct prerequisites, predicates, accepted roots, gates, and successor effects; explicitly not a queue. |
| `docs/tasks/<TASK-ID>.md` | Scope, execution instructions, entry predicate, references, decisions, evidence, affected surfaces, and validation gates. |
| `docs/project-management.md` | Normative lifecycle, task-boundary test, promotion rules, atomic reconciliation requirements, and completion behavior. |
| `AGENTS.md` | Requires an agent to consult the graph before and reconcile it after every task lifecycle event. |
| `docs/development/<date>.md` | Narrative receipt for lifecycle changes, accepted evidence, and completed-task removal. |
| `docs/tasks/AUDIT-010.md` | Historical implementation and conformance evidence for the current task-governance model. |

## Central graph data model

The graph is a set of Markdown tables grouped by milestone or work horizon.
Its row types are:

1. **Satisfied root:** a completed task, ADR, audit, or accepted durable
   evidence still consumed by open work.
2. **Task node:** a stable task ID with direct prerequisites or an entry
   predicate and a completion gate or successor effect.
3. **Dynamic node:** a placeholder such as `PINGO-PORT-*` that a planning task
   must replace with stable IDs.
4. **Milestone gate:** a named predicate such as `G-PINGO2`; it is not a task
   and never becomes actionable independently.

Each ordinary graph row has three conceptual fields:

1. node or gate identity;
2. direct prerequisites or entry predicate; and
3. completion gate or successor effect.

Free-form notation supplies conjunction (`+`), Author-accepted alternative
disposition (`or disposition`), evidence conditions, and qualification
language. This is expressive for humans and agents but has no formal grammar.

Task lifecycle state, title, dates, TODO horizon, and queue position do not
live in the graph. State and dates are duplicated between TODO and the task
record; task records repeat their direct entry dependencies for local context.

## Lifecycle and consumption

The documented process is:

1. The maintainer registers accepted future intent in TODO's eventual section
   and creates a matching task record.
2. The maintainer promotes an existing stable ID into TODO's immediate queue
   only after its predicates and execution contract are ready and the Author
   accepts promotion.
3. Before any create, modify, promote, start, complete, split, supersede, or
   remove operation, the maintainer reads the affected graph node and its
   direct neighbors.
4. The maintainer updates the task, TODO, graph, decisions, and development
   receipt atomically wherever the lifecycle event affects them.
5. On completion, the maintainer records the accepted result, removes the task
   from TODO, and retains its task record. The graph retains a satisfied root
   only while an open successor still consumes that evidence.
6. Planning tasks replace dynamic graph nodes with stable tasks when their
   exact tranches become known.

Humans and agents consume the Markdown directly. Repository-wide inspection
found no non-Markdown consumer and no task-specific schema, parser, generator,
validator, make target, or CI workflow. The conformance evidence was produced
by bounded audit-time searches and scripts or commands rather than retained
task-graph tooling.

## Current mechanical evidence

At the inspected state:

1. TODO contained 66 unique open task IDs.
2. Every open TODO ID had a matching task file and first-column graph node.
3. The graph contained 73 unique task-shaped nodes: the 66 open tasks plus
   seven completed evidence roots still consumed by open work.
4. The graph additionally contained nine named `G-*` milestone gates and one
   dynamic `PINGO-PORT-*` node.
5. `docs/tasks/` contained 84 stable-ID task files because completed records
   remain durable even when they no longer need graph roots.
6. The central graph entered the repository in commit `5dac496` as part of a
   73-file governance reconciliation. Four later commits updated it as tasks
   were planned, completed, or deferred, demonstrating active maintenance.
7. The current task-start example duplicated its timestamp/status change in
   TODO and its task record; no graph edit was needed because no predecessor or
   successor relationship changed.

## Guarantees when the policy is followed

1. Queue authority and dependency truth cannot be confused merely because two
   tasks appear near each other in TODO.
2. Cross-milestone and non-linear prerequisites remain visible in one bounded
   review surface.
3. Completed evidence can remain pinned without keeping completed work in the
   actionable queue.
4. A planning task can expose unknown future topology without inventing stable
   task IDs prematurely.
5. The task-boundary test uses dependency topology and independently consumable
   gates instead of document size or elapsed-time guesses.
6. The required before/after reconciliation encourages lifecycle changes to
   update queue, detail, dependency, decision, and receipt records together.

These are governance guarantees only. The repository currently cannot reject
a missing node, duplicate node, dangling edge, cycle, stale satisfied root, or
TODO/task lifecycle mismatch automatically.

## Costs and failure modes

1. Direct dependency facts are intentionally duplicated in task files and the
   central graph, creating a drift surface.
2. Free-form Markdown predicates cannot be reliably evaluated, normalized, or
   compared by generic tooling.
3. A graph-wide edit is a merge hotspot even when two agents own unrelated
   task silos.
4. TODO ordering, horizon membership, task state, and graph predicates can
   contradict one another because no retained validator joins them.
5. Satisfied-root retention and collapse depend on human review of all open
   consumers.
6. Dynamic wildcard nodes are useful prose but cannot enforce the identities
   or ordering of the tasks that eventually replace them.
7. The initial reconciliation was broad and expensive because dependency
   meaning had to be inferred and copied across many existing records.
8. Periodic manual audits can prove a snapshot but do not prevent drift in the
   next edit.

## Comparison with Agon Extender

Extender currently has 17 open TODO tasks and 24 retained stable-ID task files.
It already preserves one TODO authority and per-task detail records, but it has
no central dependency graph or explicit immediate/eventual horizon contract.
Dependencies are distributed across task sections, decision gates, the bench
audit matrix, and REMED-001's reconciliation plan.

This makes a bounded central relationship model valuable: current dependencies
include decisions gating several implementation tasks, implementation tasks
gating physical qualification, and accepted evidence that must survive task
closure. The active remediation effort also means topology is still changing,
so a wholesale hand transcription now would invite churn.

Extender already uses reviewed YAML, JSON Schema, deterministic generated
Markdown, and validation tests for compatibility qualification. That precedent
makes a structured dependency source and generated human view a better local
fit than a second large hand-maintained Markdown authority.

## Recommendation: adapt, do not copy

Retain these `agon-fsim` principles:

1. TODO remains the sole authority for actionability and execution order.
2. Task files remain the authority for detailed execution contracts and
   evidence.
3. One bounded construct becomes authoritative for direct dependency and gate
   topology.
4. Completed evidence roots remain visible only while open successors consume
   them.
5. Every lifecycle mutation performs before/after topology reconciliation.
6. Task splitting follows independently consumable dependency and review gates.

Implement the central construct differently if the Author accepts it:

1. Use reviewed `docs/tasks/task-metadata.yaml` as the canonical relationship
   source, not as a replacement for TODO or task files.
2. Store typed task nodes, direct dependency IDs, named predicate/gate IDs,
   accepted evidence roots, dynamic-node ownership, and successor effects.
3. Generate a compact `docs/tasks/task-dependency-gates.md` view for humans and
   agents; never edit the generated view directly.
4. Validate exact open-TODO coverage, matching task files and detail links,
   unique identities, known references, acyclicity, consumed completed roots,
   dynamic-node ownership, and lifecycle timestamp/status agreement.
5. Keep descriptive scope, instructions, decisions, evidence narratives, and
   result prose out of the centralized file.
6. Initially encode only current open tasks and completed roots they consume;
   do not reconstruct every historical task into the graph.
7. Introduce the model after REMED-001 establishes the accepted near-term task
   topology, or migrate in small reviewed tranches rather than one broad
   inference pass.

The immediate/eventual two-horizon queue is useful but separable. It should not
be imported implicitly with the dependency graph. Extender can decide later
whether its unfinished portfolio needs that distinction.

## Author review questions

### ADMIN-001-D1 — Central relationship authority

- **Status:** Deferred without prejudice
- **Recommendation:** Accept one canonical dependency/gate construct while
  retaining TODO as the only action queue and task files as execution records.
- **Alternative:** Continue with distributed prose dependencies and periodic
  audits.
- **Downstream effect:** Acceptance authorizes a separately bounded design and
  migration task; it does not authorize migration inside ADMIN-001.

### ADMIN-001-D2 — Canonical representation

- **Status:** Deferred without prejudice
- **Recommendation:** Use reviewed YAML plus schema/validator/generator rather
  than hand-maintained Markdown.
- **Alternative:** Copy `agon-fsim`'s Markdown table model for lower initial
  implementation cost but retain manual drift risk.
- **Downstream effect:** Determines whether tuple uniqueness, reference
  integrity, acyclicity, and coverage can become commit-time checks.

### ADMIN-001-D3 — Queue horizons

- **Status:** Deferred without prejudice
- **Recommendation:** Defer immediate/eventual adoption to a separate decision;
  it is independent of dependency centralization.
- **Alternative:** Adopt both horizons during the metadata migration.
- **Downstream effect:** Affects TODO semantics and promotion policy, not graph
  correctness.

### ADMIN-001-D4 — Follow-on boundary

- **Status:** Deferred without prejudice
- **Recommendation:** If D1 and D2 are accepted, create `ADMIN-002` to design,
  prototype, validate, review, and migrate the relationship model. Do not make
  ADMIN-001 itself an implementation task.
- **Alternative:** Reject or defer with no follow-on task.
- **Downstream effect:** Preserves this inspection as evidence while making the
  infrastructure change independently reviewable and reversible.
