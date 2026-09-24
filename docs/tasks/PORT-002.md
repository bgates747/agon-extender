# PORT-002 — Integrate vendored-source selection and upstream merge guidance

## Current applicability

The infrastructure was accepted and promoted to the
[dependency workflow](../dependencies/README.md). Its fingerprinted profile scope
is distinct from [current console selection](../building.md); graph acceptance
is neither a P4 build nor qualification of later deployed overlays.

The implementation record describes August acceptance. Later managed imports
are recorded in [source-baselines.yaml](../dependencies/reviewed/source-baselines.yaml);
original external-reference classifications do not mean sources are still absent
from this repository. Refresh generated data through reviewed inputs, never by
hand-editing it to match a prose summary.

## State

- Status: Complete — Review Gate 2 approved
- Started: 2026-08-22 07:03 EDT
- Finished: 2026-08-22 10:08 EDT

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

The [Review Gate 1 proposal](PORT-002/PROPOSAL.md) defines the schema extension,
selection-cause vocabulary, durable artifact layout, validation contract,
merge-attention rules, and implementation proof set.

Status: closed and approved by the Author on 2026-08-22. The accepted decisions
were frozen before implementation. Schema 2.0, durable tooling, complete source
manifests, normalized profile selections, source-region seams, projections,
queries, merge-attention comparison, documentation, and the six-case proof are
implemented. Review Gate 2 subsequently accepted promotion, as recorded below.

## Review Gate 2

- [Durable workflow](../dependencies/README.md)
- [Schema contract](../dependencies/schema/README.md)
- [Canonical graph](../dependencies/generated/code-graph.yaml)
- [Complete source-selection projection](../dependencies/generated/source-selection.yaml)
- [Compact source-selection guide](../dependencies/generated/source-selection.md)
- [Six-case proof report](../dependencies/generated/port-002-proof.yaml)
- [Upstream watch and tagged-release procedure](../dependencies/UPSTREAM-WATCH.md)

Status: approved by the Author on 2026-08-22. The infrastructure is accepted
as the routine production baseline, subject to the explicit distinction
between declared source selection and a successfully compiled P4 firmware.

### Author review questions

- **RG2-1 — Declared P4 profile (accepted by delegation, 2026-08-22):** The
  Author accepts the generated P4 source-selection profile as the planning
  baseline without representing that he performed a record-by-record review.
  Acceptance delegates technical judgment to the Agent and rests on the
  Author's detailed SETUP-004 disposition decisions, the approved PORT-002
  proposal, the six-case proof, and completed automated validation. The profile
  records intended selection and has not yet been demonstrated by a successful
  P4 firmware build.
- **RG2-2 — Mixed-file seams (accepted, 2026-08-22):** Two exact `fabutils`
  source-region boundaries and the remaining reviewed seam anchors are
  accepted as the honest interim representation. Exact conditional or
  extracted-code boundaries remain deferred until the affected port work is
  implemented and supplies sufficient evidence.
- **RG2-3 — Infrastructure promotion (accepted by delegation, 2026-08-22):**
  The Author delegates the detailed technical judgment to the Agent and
  approves the schema, generators, validators, queries, generated artifacts,
  and upstream-watch procedure as routine project infrastructure. PORT-002 is
  authorized to close. This approval rests on the accepted preparatory
  decisions, proof cases, deterministic regeneration, source verification, and
  regression tests rather than a personal line-by-line audit by the Author.

## Implementation record

All nine work items were implemented for the accepted August review:

1. schema 2.0 models exhaustive files, source regions, observed/declared build
   profiles, and normalized profile/subject selections;
2. the closed cause vocabulary is schema- and validator-enforced;
3. selection derives from immutable manifests, the control compilation/include
   closure, accepted SETUP-004 records, and graph entry points;
4. validation enforces manifest completeness, tuple uniqueness, cause/evidence
   compatibility, accepted exclusions, explicit drift, and region parents;
5. complete YAML and compact Markdown source-selection guides are generated;
6. tagged-release comparison emits complete Tier A–D merge attention and
   conservative hash-equal rename candidates;
7. bounded queries cover source, profile, status, cause, disposition, graph
   proximity, and optional tagged-release change/tier filters;
8. the six required v2.16.0 cases pass; and
9. regeneration, informational upstream watch, tagged reconciliation, review,
   and acceptance procedures are documented.

Implementation facts and gotchas:

- PORT-001's relationship graph remains a reproducible ignored schema-1
  intermediate. The enrichment pass removes its obsolete node scalar and emits
  the sole canonical schema-2 graph; the reviewed overlay is likewise ignored
  rather than tracked as a second large authority.
- At this original checkpoint inputs were external `upstream-reference`
  trees and PORT-002 imported no firmware. Current managed-import declarations
  are linked above.
- The four exact source manifests contain 5,164 files; vdp-gl's documentation,
  examples, images, and generated documentation account for most of them. They
  remain visible as non-runtime or available content instead of being silently
  discarded.
- The two profiles yield 10,375 file/region selection records. The declared P4
  profile has 129 selected files, 42 excluded files, 882 available but not
  selected, and 4,111 non-runtime files, plus 47 excluded source-region seams.
- Mixed accepted dispositions cannot be represented honestly at file level.
  Exact reviewed spans are used for the two `fabutils` storage boundaries;
  other mixed seams are explicitly labeled as reviewed anchors until port work
  establishes precise conditional boundaries. No anchor claims that a source
  guard already exists.
- Replace dispositions resolve to a planned project-owned adapter build-unit.
  No adapter source is marked selected before PORT-003 implements it.
- No real merge-attention report is generated because only one official-tag
  graph exists. The comparator is regression-tested with deterministic
  fixtures; the first tracked report requires an independently generated later
  official tag.
- The canonical graph is approximately 30 MiB and the exhaustive selection
  projection approximately 8 MiB. Ignored base/mechanical/overlay intermediates
  prevent another copy of those large relationships from entering history.

Validation completed on 2026-08-22:

- JSON Schema and project invariant validation of the graph and VDU 22 slice;
- full input, source-tree, file, and source-span fingerprint verification for
  all four immutable source roots;
- ten regression tests, including new-file fail-visible behavior, the six-case
  proof, and Tier D visibility;
- a live bounded DS3231 query; and
- two complete pipeline passes with byte-identical tracked outputs.
