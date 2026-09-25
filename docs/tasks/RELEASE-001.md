# RELEASE-001 — Reproducible approved installation bundle

## Executive summary

Make one clearly indexed bundle of the firmware, EMOSlets and host tools approved
for current use, backed by a reproducible build and bounded validation. First
preserve the exact working installation; then consolidate its source and build
process without losing deployed features. A successful base P4 build is not yet
an equivalent replacement for the deployed snapshot/overlay combination.

**State: R01-06 complete locally; configured reset and live identity gates remain before bench deployment.**
Consolidate the mapped P4 composition, produce clean identified control/corrected
builds and verify the actual embedded browser assets. Rebuild/pin EMOS, listener
and host inputs within their existing ownership. No physical deployment or
emulator modification is authorized by this tranche.
“Approved for current use” does not silently confer formal `qualified` or
`released` status. TODO.md owns priority; this file owns the discrete work.

## Scope and ownership

The reviewing agent inventories and preserves exact artifacts. The P4 build
owner consolidates EDP source and embedded browser assets in agon-extender. The
EMOS build owner retains resident firmware and EMOSlet source in agon-emos,
using mos-agondev as its builder where applicable. Host clients remain maintained
in their owning repository; packaging does not create separately edited copies.
The Author reviews behavior and approves the selected installation combination.

Include P4 firmware and required flash companions, EMOS firmware, the installed
sdserve EMOSlet, compatible host clients and their runtime requirements, browser
assets embedded in P4, and required reset-bridge support. Identify onboard VDP
compatibility explicitly; do not assume its image must be redistributed or
changed. Distinguish required components from optional operational tools.

Do not optimize rendering, alter browser pacing, revive delta experiments, add
features, upgrade upstream dependencies or repair unrelated defects. Do not
clean up historical artifacts until the preserved bundle and rollback path are
verified. Do not change ordinary VDU/input ownership or bootstrap prerequisites.

## Evidence and existing owners

1. [Build guide](../building.md): base target versus deployed overlay gap.
2. [AUDIT-009 findings](AUDIT-009/FINDINGS.md): A09-F009 reconstruction gap,
   A09-F040 status ambiguity and A09-F060 emulator setup gap.
3. [PORT-003](PORT-003.md): display implementation owner. This task owns the
   cross-component packaging/reproduction work, not a competing renderer plan.
4. [Current SD guide](../mainboard-sd.md), [AUDIT-008 deployment](AUDIT-008/HARDWARE.md)
   and [fast-transfer record](REMOTE-005/FAST-TRANSFER.md): recorded EMOS/EMOSlet
   installation and bounded validation; verify actual state before selecting it.
5. [Host tool index](../../scripts/README.md), [version policy](../versions/README.md),
   [SD layout](../sd-layout.md) and [recovery](../mos-recovery.md): existing authorities.

Machine-specific access and installed-state receipts remain in ignored local
records. Before any physical inspection or operation, the agent must read
HARDWARE.local.md and confirm bench ownership. Before an eZ80 fixture, also read
[bench constraints](../qualification/bench-constraints.md). Current live contents
are not established by this task proposal.

## R01-01 checkpoint

[Preservation result](RELEASE-001/R01-01.md) records the component table, exact
hashes, rollback material and unresolved live-identity limits. R01-01 is complete
within that stated scope. [Bundle specification and validation matrix](RELEASE-001/R01-02.md)
complete R01-02. [Source composition](RELEASE-001/R01-03.md) completes R01-03;
[R01-04 build results](RELEASE-001/R01-04.md) complete local reconstruction and
compression checks. [R01-05 packaging](RELEASE-001/R01-05.md) supplies the
unselected local bundle. [R01-06 local validation](RELEASE-001/R01-06.md) passes
within its explicit scope. No installed firmware changed.

## Decision register

| ID | State | Recommendation, alternatives and downstream effect |
|---|---|---|
| R01-D01 | Accepted — 2026-09-24 | Author authorized restoring `?rle2=1&packed=2` during R01-04. Preserve a clean raw-request control first, then identify/test the correction separately. Verify negotiation in built browser assets and paired encoder/decoder behavior. Keep current request pacing unchanged; its policy question remains with QUAL-003/BENCH-005. No deployment or release promotion is implied. |

This is an implementation discrepancy, not a new architectural decision. The
accepted compression requirement remains unchanged; source review does not
establish the performance effect. The raw control and corrected draft were built separately; promotion still
requires the later hardware/acceptance gate.

## Proposed durable layout

Use a role-named `production/README.md` as the single selection entry point,
with a machine-readable current selection referring to immutable bundle
manifests. Each bundle identifies exact component builds, hashes, source commits,
toolchain/configuration inputs, compatibility limits and acceptance evidence.
Reuse the existing version/baseline schema rather than invent a second status
registry. Retained task receipts remain evidence, not installation instructions.

Generated binary bundles should be stored separately from editable source;
choose local retention and eventual publication storage in R01-02. Do not commit
large binaries, private topology or credentials by default. Routine users must
be able to obtain and verify the selected bundle without reconstructing task
history. An unapproved reconstruction must never replace the current selection.

## Discrete work chunks

R01-01 [x] **Preserve and identify the working installation.** The agent inspects
retained deployment receipts and, when bench access is authorized, verifies live
identities/readbacks through existing tools without changing firmware. Preserve
P4 images/flash companions, EMOS, EMOSlet, compatible host/browser sources and
any necessary snapshot transformations. Record hashes, exact paths in local
records, provenance and a rollback recipe. Distinguish installed, available and
Author-accepted artifacts. Unknown identity is a stop condition for replacement,
not permission to choose the newest timestamp. Deliver a component/evidence table.

R01-02 [x] **Define the bundle and acceptance boundary.** From R01-01, the agent
specifies required/optional components, storage, manifest reuse, the current
selection mechanism, licenses and installation order. Record the exact feature
set to preserve and known failures. Resolve lifecycle labels without rewriting
frozen evidence. Present material identity/publication/policy decisions to the
Author before acting; do not create a release merely by naming a directory
production. Deliver the concrete packaging specification and validation matrix.

R01-03 [x] **Recover the P4 source composition.** The P4 build owner maps each
selected deployed change to maintained source or a retained transformation,
including renderer, codec, browser input/UI, reset integration and SD gateway.
Record included/excluded changes and parent provenance; do not apply every old
experimental patch. Identify missing source inputs explicitly. Deliver a bounded
composition map before editing the production build.

R01-04 [x] **Consolidate and reproduce builds.** The build owners integrate only
R01-03's selected composition into maintained source and one documented P4 build
entry point. Pin EMOS, EMOSlet and host-client inputs without migrating ownership.
Build from clean recorded commits into fresh output directories, with no hidden
agent snapshots or prior generated objects. Compare outputs with preserved
images; report nondeterministic metadata separately. If bytes differ, document
why and require equivalence validation rather than claiming exact reproduction.
Deliver build commands, manifests and automated integrity/input checks.

R01-05 [x] **Assemble the installation candidate.** The agent packages identified
outputs, pinned host tools/dependencies, checksums and operator instructions.
Clearly distinguish EMOSlet from ordinary application payloads. Document initial
input admission, SD placement, flash order/offsets where applicable, verification,
service startup/stop and rollback. Retain configurable local endpoints outside
the bundle. Generate packages from canonical sources; never maintain a second
editable script/browser tree. Candidate packaging does not advance current.

R01-06 [x] **Validate locally.** The agent exercises manifest/hash checks,
component selection, clean builds and applicable host tests. Use emulator checks
only where they provide meaningful evidence; honor the explicit human approval
gate for any emulator-related changes. Record untested hardware behavior as
such. Test the documented installation path by desk walkthrough and verify that
another agent does not need historical task knowledge to select its inputs.

R01-07 [ ] **Validate on the bench and obtain acceptance.** Only after bench
availability and deployment authorization, the operator deploys the candidate
with the preserved rollback ready. Use the R01-02 matrix: boot/SD, USB and browser
input, Legacy/ExCom switching, browser video, reset bridge, screen-text access,
checked/fast transfer and EMOSlet exit/reentry as applicable. Include bounded
human gameplay/UI comparison against the preserved installation, not an open-ended
performance campaign. Preserve unrelated SD files and observe capture-interference
rules. A failure retains the old approved selection; restore it when required.
Record exact passes, failures and exclusions; obtain Author acceptance.

R01-08 [ ] **Promote and close the reconstruction gap.** After acceptance, the
agent advances the single current selection, updates the handbook/build/tool/SD
instructions and records compatibility and rollback. Update A09-F009 only to the
extent reproduction was proved; broader qualification remains with its owners.
Commit logically by owning repository. Publication/push follows the applicable
Author authorization, with no private files or unrelated work included. Deliver
one starting path, the selected manifest and a concise remaining-limit list.

## Gates and stopping rules

Each chunk ends with its evidence, checklist state and a bounded next step.
Missing source, incompatible components or an unexplained behavior change must
be reported before promotion; they do not authorize a redesign. No modernizing
or incidental cleanup is hidden in reconstruction. Preserve existing work in all
repositories and use isolated worktrees when needed.

The present execution boundary is **R01-06**. Check retained clean-build evidence,
extract and validate the frozen archives, exercise the packaged host clients and
browser through local fixtures, and walk installation/rollback as a new reader.
Do not modify the immutable r01 bundle. Record blockers rather than silently
repackaging or advancing current. No bench, SD, reset or emulator changes.
R01-07 and promotion require continuation authorization. New firmware
identities and registry changes follow the existing version authority; exact
historical binaries retain their identities. A packaging milestone does not
close electrical qualification, all-mode compatibility or the documentation audit.
