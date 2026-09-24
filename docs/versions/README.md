# Versioning and Artifact Identity

This directory is the authoritative home for Agon Extender artifact identity,
versioning, revision, build, baseline, and test-run conventions.

## Vocabulary

- **Artifact:** A reusable item whose identity can affect a build, deployment,
  interface, or result.
- **Artifact ID:** The stable human name of one artifact lineage.
- **Version:** A compatibility-significant software or protocol state.
- **Revision:** A controlled physical, wiring, layout, profile, fixture,
  procedure, document, or experimental-artifact state.
- **Build:** One produced image or executable from specific source,
  configuration, and tools.
- **Variant:** A deliberate parallel form that is neither newer nor older than
  its siblings.
- **Profile:** A machine-readable hardware or interface description.
- **Fixture:** A reusable physical or software test arrangement.
- **Specimen:** One physical unit, identified by a bench alias when necessary.
- **Baseline:** A named, approved combination of artifacts and dependencies.
- **Status:** An independent lifecycle state: experimental, candidate,
  qualified, released, deprecated, or rejected.
- **Run:** One execution of a build, deployment, experiment, or qualification.
- **Manifest:** The machine-readable bill of materials for a build, baseline,
  or run.
- **Provenance:** Where an artifact came from and how it was produced.
- **Integrity hash:** A byte-level identity check, not a human-facing version.

Software and protocols have versions. Physical assemblies, wiring, profiles,
fixtures, procedures, documents, and experimental artifacts have revisions.
Produced outputs have builds. Purchased devices retain manufacturer identities
and may receive local specimen aliases. Tests have run IDs.

## Identifier grammar

| Kind | Form | Example |
|---|---|---|
| Software or protocol | `<artifact>-vMAJOR.MINOR.PATCH` | `extender-vdp-v0.1.0` |
| Revision-controlled artifact | `<artifact>-rNN` | `light2-harness-r01` |
| Build | `<identity>-bYYYY-MM-DD-HH-MM-SSZ` | `extender-vdp-v0.1.0-b2026-08-20-21-42-03Z` |
| Experimental build | `<artifact>-rNN-bTIMESTAMP` | `setup-001-canary-r02-b2026-08-20-21-42-03Z` |
| Baseline | `<name>-rNN` | `p4-bringup-r01` |
| Run | `<TASK-ID>-YYYY-MM-DD-HH-MM-SSZ` | `SETUP-001-2026-08-20-21-42-03Z` |

Rules:

1. Semantic versions have no leading zeroes. Major is a compatibility break,
   minor is a backward-compatible capability addition, and patch is a
   backward-compatible correction without intended interface expansion, subject
   to the explicit EMOS development convention below.
2. Revisions begin at `r01`, advance monotonically, and continue from `r99` to
   `r100` without wrapping.
3. Builds and runs use UTC creation/start timestamps. `Z` is mandatory.
4. Variants use short lowercase names and do not imply ordering.
5. Manufacturer revisions retain their native spelling, such as `Rev D1`.
6. Status is recorded separately and does not change version ordering.
7. Compatibility is explicit in manifests; matching numbers do not imply it.
8. Commits and hashes accompany human identities for provenance and integrity
   but do not replace them.

### Allowed characters and uniqueness

- Artifact IDs and variant names use lowercase ASCII letters, digits, and
  single hyphens. They begin with a letter and neither end in nor repeat a
  hyphen: `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`.
- Task IDs retain their uppercase TODO spelling. Run IDs copy the task ID
  exactly and append the UTC timestamp.
- Versions use `v0.0.0` or greater. Revisions use `r01` or greater; `r00` is
  invalid.
- Build and run timestamps have one-second resolution. Two identifiers for the
  same artifact or task may not share a timestamp; if that occurs, wait for the
  next second rather than inventing an unrecorded suffix.
- Identifiers are immutable and are never reused, even after rejection.

The artifact registry itself has a revision. Increment `registry_revision`
whenever an artifact lineage, latest identity, status, variant, or normative
note changes. Pure formatting corrections need not increment it while the
registry is still a draft; an accepted registry revision is immutable.

## Lifecycle status

Allowed status values are:

| Status | Meaning |
|---|---|
| `draft` | Defined or under construction; not yet exercised. |
| `experimental` | Exercised for investigation; no qualification claim. |
| `candidate` | Frozen for a stated qualification procedure. |
| `qualified` | Passed the recorded procedure for a declared compatibility scope. |
| `released` | Deliberately published for normal use. |
| `deprecated` | Still identifiable but discouraged or scheduled for removal. |
| `rejected` | Failed review or qualification and must not be selected. |

The normal progression is `draft` → `experimental` → `candidate` →
`qualified` → `released` → `deprecated`. A state may move to `rejected` when
appropriate. Status changes do not rename an artifact. “Incompatible” is a
compatibility finding, not a lifecycle status.

Qualification is contextual. A manifest must say what procedure, hardware,
dependencies, and compatibility scope were qualified; `qualified` never means
“works with everything.”

## Increment rules and authority

The Author approves new artifact IDs and every version or revision increment.
An agent may recommend the next identity and may stamp builds and runs from UTC
automatically, but must not silently advance a version or revision.

### Semantic versions

- Increment **major** when an existing external consumer may need modification:
  removed or reinterpreted commands, incompatible packet or file formats,
  changed electrical/protocol assumptions, or abandoned compatibility.
- Increment **minor** for backward-compatible commands, capabilities, optional
  fields, or performance features.
- Increment **patch** for corrections and internal changes that preserve all
  intended external contracts.
- Before `v1.0.0`, the interface is explicitly developmental. Increment minor
  for a developmental breaking change and patch for compatible corrections;
  manifests must not imply stability merely because versions are ordered.

### EMOS early-development convention

On 2026-09-08 the Author approved a one-time EMOS numbering reset: the next
source identity is `agon-emos-v0.1.7`, following the recorded `v0.7.0` builds.
This is a naming-policy transition, not a rollback or renaming of any binary.
Existing builds, rollback payloads, manifests and evidence retain their exact
original identities. Use exact identities across this transition; numeric
version ordering does not describe its chronology. Previously used identities
remain reserved, including the earlier v0.2.0 through v0.7.0 identities; a
future milestone must select an unused identity.

During this early EMOS development series, compatible small implementation
increments, including bounded diagnostic additions, advance `v0.1.x`'s patch
number. Minor increments are reserved for Author-agreed capability milestones
or developmental breaking changes. This project-specific pre-1.0 convention
overrides the general capability-addition rule above for EMOS. Patch numbers
have no two-digit limit. Test-article-only changes advance the fixture revision;
they do not by themselves advance EMOS. Changed executable bytes still receive
a new build timestamp, even when the firmware version stays the same.

### Revisions

Increment a revision whenever a controlled artifact changes in a way that may
affect construction, behavior, interpretation, reproduction, or test results.
Examples include moving a wire or probe, changing a pin assignment, component,
threshold, trigger, build option, procedural step, or expected result.

Editorial corrections that cannot change execution or interpretation do not
require a new revision. If there is reasonable doubt, increment it. Never edit
the definition of a qualified or released revision in place; create the next
revision and retain the old record.

### Builds and runs

A new executable byte sequence is a new build, even when its semantic version
or source revision is unchanged. Repeating a procedure is always a new run.
Build and run timestamps are assigned at artifact creation and run start,
respectively, and never rewritten to match a later publication time.

## Compatibility declarations

Compatibility is directional and explicit. A consumer declares what it
requires; a baseline or run records the exact identities selected. Never infer
compatibility from matching version or revision numbers.

Each requirement names an `artifact_id` and exactly one selector:

- `exact`: one accepted identity;
- `one_of`: an explicit list of accepted identities; or
- `version_range`: inclusive `minimum` and exclusive `before` semantic-version
  bounds.

Revision ranges are deliberately unsupported because physical changes are not
semantically ordered. List acceptable revisions with `one_of`. A requirement
may additionally constrain a `variant` and state a short `reason`.

Breaking compatibility requires a new major protocol/software version or a new
physical revision, as applicable. It does not permit rewriting an old
declaration. Unknown combinations are **unqualified**, not compatible or
incompatible by assumption.

## Identity placement

Every deployed or evidence-producing firmware/program build must expose its
full build ID and status through its normal diagnostic channel. Extender
firmware must provide the same identity in:

1. a generated compile-time source constant;
2. startup/boot diagnostics;
3. machine-readable VDP or Extender capability diagnostics when implemented;
4. network status diagnostics when implemented;
5. the binary filename and adjacent build manifest; and
6. release metadata for released builds.

The source version/revision is maintained in a small tracked identity file. The
build system generates the UTC build ID and provenance fields; generated files
must say that they are generated and must not be hand-edited. Reproducible
builds may deliberately reuse a recorded build timestamp only when recreating
that exact build and verifying the same output hash.

Hardware, wiring, fixtures, profiles, and procedures display their artifact ID
and revision in their defining document or machine-readable file. Physical
labels are strongly recommended once an assembly leaves a transient
breadboard state.

A hardware profile may freeze multiple tracked inputs with an `integrity`
mapping containing `algorithm: sha256` and a nonempty `files` mapping. File
names are relative to the profile directory, the declared authority must be
included, and every recorded digest is validated. This protects companion
inputs such as a controlled BOM without making them competing electrical
authorities.

## Manifest rules

Manifests use UTF-8 YAML, schema version `1`, two-space indentation, lowercase
field names with underscores, and UTC timestamps. Required unknown information
uses YAML `null`; it must not be omitted, guessed, or written as an ambiguous
empty string. Optional sections may be omitted when irrelevant.

Tracked manifests must not contain credentials, private network/filesystem
topology, account information, or private specimen identifiers. Use aliases
whose private mapping lives in the ignored bench record.

Artifact and baseline records are declarative and tracked. Run manifests are
append-only evidence: after a run finishes, only explicit corrections with a
dated correction note may alter its manifest.

Run `outcome` is one of `pass`, `fail`, `partial`, `aborted`, or `invalid`.
`Partial` means the procedure completed only some declared checks; `invalid`
means its evidence cannot support a conclusion. An outcome never substitutes
for artifact lifecycle status.

## Qualified-run commit procedure

A qualified run tests immutable, committed inputs from a clean working tree.
Commit the candidate source, configuration, identity, procedure, profiles, and
other controlled definitions before building. The build manifest records that
exact commit with `dirty: false`.

The run manifest and evidence necessarily follow the test, so qualification
uses this sequence:

1. commit all candidate inputs;
2. confirm the working tree is clean;
3. build and hash the candidate from that commit;
4. run the committed procedure without changing the candidate;
5. commit the completed run manifest and evidence; and
6. after a pass, commit qualification/baseline status and optionally add an
   annotated release tag.

Preserve informative failed-run evidence and unresolved failures. Under the
Author's standing bench-retention rule, once an ordinary setup/operator mistake
is understood and has no lasting diagnostic value, discard its capture bundle
and detailed failure narrative while retaining a brief corrective note. This
exception does not permit deleting an unexplained failure or rewriting a failed
result as a pass. No evidence is discarded merely by applying this policy text.

Any candidate change after a run begins, however
small, requires a new commit, build ID, and run ID. Uncommitted or dirty builds
may be used for exploration but cannot support a `qualified` or `released`
status.

## Pre-policy evidence

Do not fabricate compliant IDs for historical work whose exact UTC build or run
start was not recorded. Preserve its original evidence name, label it
`pre-policy`, and record every identity that can be verified. A later rerun gets
a normal ID; retrospective approximation is never substituted for provenance.

## Records

- [`artifacts.yaml`](artifacts.yaml) registers project artifact IDs and their
  current versions or revisions.
- [`build-manifest.template.yaml`](build-manifest.template.yaml) defines build
  provenance and output identity.
- [`baselines/TEMPLATE.yaml`](baselines/TEMPLATE.yaml) defines approved
  combinations of independently identified artifacts and dependencies.
- Run manifests belong beside their evidence at
  `tests/runs/<RUN-ID>/manifest.yaml`; see
  [`tests/runs/TEMPLATE/manifest.yaml`](../../tests/runs/TEMPLATE/manifest.yaml).
- [`EXAMPLES.md`](EXAMPLES.md) contains complete worked naming and increment
  examples.
- [`REVIEW.md`](REVIEW.md) is the SETUP-002 approval checklist.

## Validation

Install the pinned development dependency and validate the registry/templates
from the repository root:

```text
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate-version-records.py
```

The validator checks YAML structure plus project-specific identity and status
rules. Passing it does not qualify the artifacts described by a manifest.

Machine-local topology, credentials, account information, and private specimen
identifiers must not appear in tracked version records.
