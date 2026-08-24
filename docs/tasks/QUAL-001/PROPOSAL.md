# QUAL-001 Review Gate 1 proposal

Status: Review Gate 1 accepted by the Author on 2026-08-22. The proposal is the
approved boundary for QUAL-001 Work 2; Gate 2 still controls authority
promotion and complete-matrix acceptance.

## 1. Resulting durable role

After Review Gates 1 and 2, `docs/qualification/` will be the maintained home
for compatibility and product-capability qualification traceability. It will
answer:

> For every accepted behavior or capability, what implements it, what blocks
> it, and what evidence supports the exact claim?

The construct will not redefine VDU/EDU syntax, operating modes, hardware,
task scope, procedures, run outcomes, or source selection. It will reference
their authorities and expose missing joins.

The proposed durable layout is:

```text
docs/qualification/
├── README.md
├── reviewed/
│   ├── sources.yaml
│   ├── modes.yaml
│   ├── interfaces.yaml
│   ├── capabilities.yaml
│   ├── qualification-domains.yaml
│   ├── mode-expectations.yaml
│   ├── obligations.yaml
│   ├── evidence.yaml
│   └── evidence-links.yaml
├── schema/
│   ├── README.md
│   └── compatibility-matrix.schema.json
├── scripts/
│   ├── build-compatibility-matrix.py
│   ├── render-compatibility-views.py
│   └── validate-compatibility-matrix.py
├── generated/
│   ├── compatibility-matrix.yaml
│   ├── compatibility-matrix.md
│   ├── vdu-inventory.md
│   ├── secondary-capabilities.md
│   └── views/
└── tests/
```

Names may receive small editorial corrections during implementation. Changing
collection roles, authority, or identity rules requires another Author review.

### Authority boundary

The reviewed YAML collections are the human-maintained semantic inputs. The
generated canonical YAML is the deterministic normalized join used by agents,
validators, release gates, and bounded queries. Markdown and any diagrams are
generated projections only.

This mirrors the established dependency workflow: reviewed semantic claims
and external authorities feed one canonical machine model, and all convenient
views are projections.

## 2. Promotion of the current VDU inventory

The accepted
[`SETUP-004/VDU-inventory.md`](../SETUP-004/VDU-inventory.md) remains
authoritative throughout QUAL-001 Work 2 and the initial import. Work 3 will:

1. import every inventory entry into `reviewed/interfaces.yaml` without
   changing selector, title, category, or disposition;
2. assign and validate one stable interface ID per entry;
3. generate a replacement inventory view from those records;
4. compare the generated view against the accepted source and expose every
   difference; and
5. stop at Review Gate 2 before changing authority.

If Gate 2 is accepted, the reviewed YAML becomes the interface authority and
the old task-local Markdown becomes either a generated view or a short link to
the durable view. It will not remain an independently edited command list.

This is a one-time role promotion, not an attempt to infer new dispositions
from symbols or source code.

## 3. Stable identity

Every internal identity is typed and owner-qualified:

```text
interface:agon-vdp:vdu-22
interface:agon-vdp:vdu-23-0-x80
interface:agon-vdp:vdu-23-0-x87
capability:extender:wired-ethernet
mode:extender:legacy
mode:extender:edp-exclusive
mode:extender:cooperative
obligation:extender:vdu-23-0-x80-startup-roundtrip
evidence:run:PORT-003-2026-08-22-23-58-56Z
```

Identity rules are:

1. IDs never contain line numbers, task-local item numbers, titles, status, or
   implementation owners.
2. VDU selector segments use decimal where the accepted syntax is decimal and
   lowercase `xNN` where it uses `&NN`. Parameters do not enter the ID.
3. Two semantic branches sharing a selector receive a short reviewed suffix,
   such as `-load-bitmap` and `-capture-screen`; they are never disambiguated by
   array order.
4. Child commands preserve the complete selector path when it is known.
5. Titles may change editorially without rekeying the ID.
6. An accepted ID is immutable. A truly different contract receives a new ID
   and an explicit supersession relation.
7. Task IDs, source files, code symbols, procedures, and run IDs are references,
   not components of interface or obligation identity.

The schema checks ID shape. The semantic validator enforces global uniqueness,
subject references, and non-reuse.

## 4. Normalized data model

A displayed matrix row is a join, not the primary storage shape. The model has
seven principal collections.

### 4.1 Interfaces

One record per accepted VDU inventory item:

- stable ID;
- exact selector text;
- titular description;
- command category, category-relative display order, and optional parent;
- accepted disposition: `supported`, `accepted-noop`, `mode-dependent`,
  `unsupported`, or `unresolved`; and
- source references.

Interfaces say what the accepted surface contains. They do not claim that an
implementation or test exists.

### 4.2 Secondary capabilities

One record per non-compatibility product capability, such as wired Ethernet or
microSD. These records are always marked `secondary-capability`; their evidence
cannot satisfy compatibility-critical obligations.

### 4.3 Qualification domains

Some compatibility obligations span several commands or have no command
selector at all. Shared compatibility transport, operating-mode lifecycle, and
assembled-system electrical behavior are examples. A qualification domain is a
stable, compatibility-critical grouping subject for those claims.

Domains do not define commands, protocols, wiring, capabilities, or decisions.
They only prevent a cross-cutting obligation from being assigned to an
arbitrary interface or mislabeled as a secondary product capability. Initial
domain IDs are:

```text
domain:extender:compatibility-transport
domain:extender:operating-mode-lifecycle
domain:extender:assembled-system
```

### 4.4 Modes and mode expectations

Modes are stable vocabulary records. A normalized mode-expectation tuple links
one interface and one mode with one of:

- `stock-vdp` — behavior belongs to the onboard VDP in that mode;
- `extender-required` — EDP must provide the accepted behavior;
- `accepted-noop` — command is consumed with the accepted no-op behavior;
- `unsupported` — accepted carve-out;
- `not-applicable`; or
- `unresolved`.

Blockers name exact SETUP-005 decision IDs. Missing mode knowledge remains
explicit rather than being inferred from the interface-wide disposition.

### 4.5 Qualification obligations

A subject can have several independently provable obligations. General Poll,
for example, has command-ingress, response-packet, MOS-state, and physical
round-trip concerns. Each obligation records:

- stable ID and subject;
- compatibility-critical or secondary scope;
- claim and obligation kind;
- applicable modes;
- owning tasks;
- requirement and blocker references;
- implementation state; and
- qualification state.

This is the row granularity used by detailed generated views. It prevents one
successful test from silently qualifying every aspect of a command.

### 4.6 Evidence

Evidence records point to existing authoritative source analysis, decisions,
host tests, target tests, procedures, bench runs, and visual/audio observations.
They carry their own lifecycle state. They do not repeat raw logs or procedure
contents.

### 4.7 Evidence links

Evidence links form unique `(obligation, evidence)` tuples and state whether an
item `supports`, `partially-supports`, `contradicts`, or `supersedes` the exact
claim. Evidence availability never changes an obligation to `qualified`
automatically.

## 5. Independent state axes

The proposal separates concepts that would be misleading as one status field.

### Interface disposition

```text
supported
accepted-noop
mode-dependent
unsupported
unresolved
```

### Implementation state

```text
unassigned
not-started
in-progress
implemented
excluded
not-applicable
```

### Qualification state

```text
unknown
not-required
blocked
planned
candidate
qualified
rejected
```

### Evidence lifecycle

```text
candidate
accepted
rejected
superseded
```

Rules enforced beyond JSON Schema will include:

1. `qualified` requires at least one accepted supporting evidence link and a
   qualification basis naming the applicable procedure/run or accepted
   non-run method.
2. `blocked` requires one or more blocker references.
3. `not-required` requires an accepted decision or carve-out reference.
4. `unsupported` does not erase obligations to prove selected parser/failure
   behavior.
5. Secondary evidence cannot qualify a compatibility-critical obligation.
6. Rejected or superseded evidence remains traceable but cannot support a
   current qualified state.
7. An implemented behavior may remain unqualified, and a partial test may be
   linked without elevating qualification state.

## 6. References and integration

References are stable repository-relative paths, task/decision IDs, dependency
node IDs, artifact IDs, procedure IDs, and run IDs. Validators will distinguish
reference classes and reject dangling local references where the target is
tracked in this repository.

The dependency graph remains authoritative for code/source relationships. The
qualification model stores only the dependency node IDs needed to connect a
behavior or obligation to relevant source; it does not reproduce graph edges.

Likewise, run manifests remain authoritative for physical observations and
hashes. The matrix records the exact claim supported by a run, not a summary
that could silently broaden the run's scope.

## 7. Determinism and validation

Work 2 will provide one orchestrated regeneration command. The permanent
validator will enforce:

- schema validity and closed vocabularies;
- globally unique IDs and normalized tuple uniqueness;
- complete interface coverage after the Gate 2 migration;
- referential integrity across subjects, parents, modes, tasks, decisions,
  dependency nodes, evidence, and evidence links;
- status/blocker/evidence invariants;
- deterministic sort order;
- input digests and generator identity;
- byte-identical repeated generation; and
- no private paths, network topology, credentials, or specimen identities.

The repository-local `.venv` and pinned development requirements remain the
only Python environment. No database server or runtime application dependency
is introduced.

## 8. Human and agent views

The primary generated Markdown will remain compact. It will show one summary
row per interface with counts and worst-state indicators, while detailed views
show obligations by:

- interface or command family;
- operating mode;
- owning task;
- implementation subsystem;
- blocker/open decision;
- evidence type;
- release/qualification readiness; and
- secondary capability.

Agents should query or generate a bounded view before broad source searching.
Human summaries link to the exact obligation and its authorities rather than
embedding large excerpts.

## 9. Lifecycle

1. An accepted interface or disposition change begins in its owning decision or
   task, then updates reviewed YAML and regenerated views.
2. Implementation tasks add or update obligation ownership and implementation
   state while preserving unresolved blockers.
3. Procedures define qualification claims before runs.
4. Completed run manifests are linked as evidence after execution.
5. Qualification state advances only through an explicit reviewed disposition.
6. Upstream tagged-release review uses dependency merge-attention results to
   identify affected interfaces and obligations.
7. Task closure and releases reject unexplained required rows but permit
   explicit accepted carve-outs and deferrals.
8. Superseded/rejected records remain queryable and cannot be silently reused.

## 10. Representative fixture

[`fixtures/review-gate-1.yaml`](fixtures/review-gate-1.yaml) exercises:

- supported VDU mode selection with partial frame-service evidence;
- the supported General Poll command blocked on transport/MOS integration;
- a cross-cutting compatibility-transport domain obligation;
- unresolved RTC authority linked to SETUP-005-D008;
- an unsupported printer command whose selected failure behavior remains
  blocked on SETUP-005-D006; and
- wired Ethernet as a secondary capability whose evidence cannot qualify VDU
  behavior.

The fixture is schema-valid proposal evidence, not project qualification data.
It intentionally contains accepted partial evidence without a `qualified`
obligation, demonstrating the separation between “we observed something” and
“we qualified the complete claim.”

## Review Gate 1 decisions requested

1. Accept the normalized YAML collections and generated canonical join rather
   than one hand-maintained flat matrix.
2. Accept the one-time Gate 2 promotion of the current VDU inventory into YAML
   authority, after exact import/diff review.
3. Accept typed selector-derived interface IDs and separately stable obligation
   IDs.
4. Accept the independent disposition, mode-expectation, implementation,
   qualification, and evidence axes.
5. Accept strict separation of compatibility-critical and secondary capability
   qualification.
6. Accept repository-native YAML, JSON Schema, semantic validation, and no
   relational/database service.
7. Accept the proposed durable layout and lifecycle as the Work 2 boundary.
8. Accept normalized qualification domains as subjects for cross-cutting
   compatibility obligations.

The Author accepted all eight Review Gate 1 decisions on 2026-08-22. Work 2
implemented this boundary; Review Gate 2 still controls authority promotion.
