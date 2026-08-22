# PORT-002 — Integrate vendored-source selection and upstream merge guidance

## State

- Status: Not started — scope registered from SETUP-004 Work 1.b
- Started: --
- Finished: --

## Intent

Extend the dependency-graph infrastructure proved by PORT-001 so every
upstream source file is visibly distinguishable as:

- present because the complete tagged upstream release is vendored;
- selected into a named Extender build because a retained facility needs it;
- selected only because an inherited upstream build rule is over-broad; or
- deliberately excluded from an Extender build under a reviewed disposition.

Generate a reliable upstream-merge guide from that information. Agents
reviewing a new tagged release must be able to identify changes inside the
selected dependency closure, changes at selection and adapter boundaries, and
changes to presently unselected source without rediscovering the firmware-wide
graph or assuming that an uncompiled file is irrelevant.

This task extends the canonical graph and its deterministic projections; it
must not create a manually maintained second source of truth.

## Inputs

- [PORT-001 graph system](PORT-001.md), schema, generated graph, and upstream
  comparison workflow.
- [SETUP-003 structural and compiler inventory](SETUP-003.md).
- [SETUP-004 subsystem dispositions](SETUP-004.md) and generated inventory.
- [ADR-0011 upstream integration boundary](../decisions/ADR-0011-upstream-vdp-integration-and-project-structure.md).
- [ADR-0012 vendored release policy](../decisions/ADR-0012-vendored-release-dependencies.md).
- [ADR-0013 source-selection boundary](../decisions/ADR-0013-vdp-survey-integration-boundaries.md).

## Work

1. Extend the graph's source/build model so every file in each vendored tree
   records immutable upstream provenance, availability, selection separately
   for each named build profile, mechanically evidenced selection cause, and
   applicable task or ADR disposition.
2. Define a closed, validated selection-cause vocabulary that distinguishes at
   minimum direct build input, transitive/header-defined dependency, retained
   compatibility requirement, project adapter, inherited broad build
   selection, deliberate exclusion, and unresolved selection.
3. Derive the records from vendored-tree manifests, compilation databases,
   compiler include evidence, build filters/manifests, graph reachability, and
   accepted SETUP-004 dispositions. Reviewed annotations may explain intent but
   may not contradict mechanical build evidence.
4. Validate that every vendored file is classified, every selected file has an
   evidenced cause, every exclusion cites a disposition or explicit scope
   boundary, and every newly appearing upstream file is visible until reviewed.
5. Generate a compact human-readable source-selection guide alongside the
   canonical machine-readable data. It must show what is merely vendored, what
   is compiled, why it is compiled or excluded, which retained behavior reaches
   it, and the responsible task or ADR.
6. Generate a tagged-release comparison and merge-attention projection that
   prioritizes changed selected code and dependency boundaries while retaining
   visibility of unselected changes that could alter build rules, public
   headers, licenses, security, or future selection.
7. Provide deterministic queries by upstream file, subsystem, command or EDU
   behavior, build profile, disposition, and changed tagged release. Preserve
   exact evidence entry points for deeper review.
8. Seed and validate the system against the current official VDP `v2.16.0`
   dependency set and the accepted SETUP-004 dispositions. Demonstrate that the
   DS3231 omission is represented as vendored-but-excluded rather than absent.
9. Document regeneration, tagged-release comparison, review, and acceptance
   procedures for routine upstream integration work.

## Review gate

Stop after proposing the schema extension, selection-cause vocabulary,
generated artifact layout, and merge-attention rules. Obtain Author approval
before implementation.
