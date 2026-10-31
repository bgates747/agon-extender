# RELEASE-001 — Reproducible approved installation bundle

## Executive summary

Make one clearly indexed bundle of the firmware, EMOSlets and host tools approved
for current use, backed by a reproducible build and bounded validation. First
preserve the exact working installation; then consolidate its source and build
process without losing deployed features. A successful base P4 build is not yet
an equivalent replacement for the deployed snapshot/overlay combination.

**State:** The earlier r02 DevKit release is complete/current. Native P4-PC
promotion targets the Author-approved combined v0.2.1. Exact accepted HDMI and
keyboard/controller r16 source integration is verified; canonical qualification
and final production selection/tag closeout remain pending.
[Production selection](../../production/README.md) is the routine entry point.
[R01-08 closeout](RELEASE-001/R01-08.md) records exact packaging and validation.
No new hardware work is started by promotion.
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
within its explicit scope. R01-07 later identified and fixed a bootloader
configuration mismatch, deployed r55 and obtained Author acceptance. R01-08
replaced the failed package and selected the accepted combination.

## Decision register

| ID | State | Recommendation, alternatives and downstream effect |
|---|---|---|
| R01-D01 | Accepted — 2026-09-24 | Author authorized restoring `?rle2=1&packed=2` during R01-04. Preserve a clean raw-request control first, then identify/test the correction separately. Verify negotiation in built browser assets and paired encoder/decoder behavior. Keep current request pacing unchanged; its policy question remains with QUAL-003/BENCH-005. No deployment or release promotion is implied. |
| R01-D02 | Accepted — 2026-10-30 | Author combines previously accepted native HDMI and keyboard/controller coexistence as production v0.2.1; use v0.2.2 only for a demonstrated integration problem. Offline source audit confirms the r16 build already includes the accepted HDMI import, so no new merge/build or fallback is required. Canonical qualification remains separate. |

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

R01-07 [x] **Validate on the bench and obtain acceptance.** Only after bench
availability and deployment authorization, the operator deploys the candidate
with the preserved rollback ready. Use the R01-02 matrix: boot/SD, USB and browser
input, Legacy/ExCom switching, browser video, reset bridge, screen-text access,
checked/fast transfer and EMOSlet exit/reentry as applicable. Include bounded
human gameplay/UI comparison against the preserved installation, not an open-ended
performance campaign. Preserve unrelated SD files and observe capture-interference
rules. A failure retains the old approved selection; restore it when required.
Record exact passes, failures and exclusions; obtain Author acceptance.

R01-08 [x] **Promote and close the reconstruction gap.** After acceptance, the
agent packages the exact accepted r55 combination as a new immutable bundle,
verifies its inventory and corrected bootloader configuration, then advances the single current selection, updates the handbook/build/tool/SD
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

R01-01–08 are complete. Preserve accepted artifacts and the failed historical
r01 bundle. Further changes require their own bounded task and validation; this
closeout does not start downstream development. New firmware
identities and registry changes follow the existing version authority; exact
historical binaries retain their identities. A packaging milestone does not
close electrical qualification, all-mode compatibility or the documentation audit.


## Native HDMI v0.2.0 authorization — consolidated into v0.2.1

Author accepts HDMI r10 gameplay and its correctly displayed outro screen and
explicitly selects v0.2.0 for production promotion. Preserve the tested bytes;
do not rebuild them merely to change their experimental embedded identity.
Current production v0.1.0 remains selected until the following gates pass.

R01-N01 [x] Record acceptance and version authorization. P4 candidate is
`rgb-001-r10-b2026-10-07-22-56-28Z`, factory SHA-256
`ef7e7bdae861119bcdc2fcda947631450f0890b6cefc8d4c23e2b6d8ead7498c`;
paired EMOS is `agon-emos-v0.1.24-b2026-10-07-23-11-33Z`, image SHA-256
`44d217b555f68a7d030bc0a89a2fa1d27f0fb537576f2925e90ef055b0a44d02`.
Evidence: [HDMI r10 physical results](HDMI-002/R10-PHYSICAL-RESULTS.md) and
[EMOS callback correction](../../../agon-emos/docs/tasks/INTEG-015.md).

R01-N02–R01-N04 are superseded by R01-U04/U05 for the combined v0.2.1 target,
under the Author's2026-10-30 instruction. The r10/EMOSv24 bytes, acceptance and
rollback remain frozen; no standalone v0.2.0 promotion or tag is now queued.
The native archive recipe is implemented for the accepted r16 application update;
the remaining complete-installation qualification/selection work belongs only
to the combined target below.


## Accepted native keyboard/controller combination — 2026-10-30

The Author explicitly accepts r16 direct-header keyboard/onboard-hub F310
coexistence and requests commit/push. INPUT-004/ACCEPTANCE.yaml freezes the
installed P4 source/build/hash, unchanged old-ABI EMOS and matched viewer.
The native application-update archive uses the existing P4 build ID as its
directory identity; no new component revision or production version is invented.
It preserves the tested application only, with native source/support and viewer
provenance. Untested replacement bootloader/factory bytes are excluded.
The separate native packager leaves the historical hybrid recipe untouched.

R01-U01 [x] Record explicit feature acceptance, exact component identities,
independent readback, rollback availability, preserved components and scope.

R01-U02 [x] Generate, extract and independently verify immutable runtime and
source/support archives, publish their portable bundle record and update current
guides. Preserve private-configured binaries locally; no public upload.

R01-U03 [x] Author selects v0.2.1 for the combined accepted HDMI and
keyboard/controller result. Source integration is already present in exact
r16/source5f8ef; no conflict justifies the conditional v0.2.2 fallback. Preserve
older evidence and the v0.1.0 tag; do not produce a separate v0.2.0 release.

R01-U04 [ ] Complete live preflight and the canonical installed-hardware suite
under separately authorized bench scope. Exact retained paired receipts and
startup/fast-transfer/HDMI-profile runner preparation now pass offline. EMOSv27
retains its archived-patch provenance, not a fabricated clean-input receipt.
Fresh physical identities, commissioned reset/cue support and fixture deployment
remain prerequisites. Feature acceptance and host checks do not replace this gate.

R01-U05 [ ] Once those concrete gates pass, select the verified native combination
in production/current.yaml, complete production docs, commit, create the agreed v0.2.1
annotated immutable version tag, and publish commit/tag. Until then current
qualified production remains v0.1.0; the accepted native update is unselected.
No hardware operation is authorized merely by this packaging closeout.


The accepted r16 application-update runtime/source-support archives are generated
from committed packager inputs and independently extracted/hash/inventory
verified. Their immutable production record is
`production/bundles/indexed-hdmi-r16-b2026-10-30-22-37-38Z/bundle.yaml`;
archive bytes remain locally in the matching dist/production directory. No
bootloader/factory/full-device-backup payload is distributed. Packaging and
acceptance are complete; R01-U03/U04/U05 remain explicit production gates.


## Combined v0.2.1 source reconciliation — 2026-10-30

The Author explicitly directs combining both accepted features into v0.2.1,
with v0.2.2 only if integration is problematic. This resolves the version gate;
the earlier record that version authority was missing is historical.

The accepted r10 build used a dirty source snapshot based on3303bab. Fifteen
retained HDMI/rolling files match committed import8800ca84577410d5b4a9d70fbd830c10624fc326
exactly. That import is an ancestor of tested clean r16/source5f8ef. Seven
mode-table, buffer ownership, primitive queue and rolling runtime/config files
remain byte-identical. Later rendering/geometry/DMA corrections are retained;
this audit is not a claim of identical implementation/performance or new hardware
coverage. [Source reconciliation](RELEASE-001/MERGED-SOURCE-V0.2.1.json) records
pins and limits. No source merge, rebuild, reflash or v0.2.2 fallback is needed.

The [combined release record](../../production/releases/v0.2.1.yaml) binds the
accepted immutable application update and preserved companions to v0.2.1.
The bundle itself is not rewritten merely to replace its creation-time null
version metadata. Canonical paired qualification, its receipt/provenance and
startup/no-CRC adapter prerequisites, complete production selection and the
annotated v0.2.1 tag remain R01-U04/U05. No bench work starts from this record.

## Next steps — combined v0.2.1 qualification

The accepted images and source integration are preserved. The remaining work
is to modernize the canonical runner, qualify that exact installed combination,
complete a bounded visual review and select/tag the release. The Author
authorizes offline preparation on 2026-10-30; the bench is occupied, only the
mainboard is active, and Extender is completely offline. Do not contact either
board, deploy fixtures, open serial, reset, flash or invoke hardware tests in
this tranche. Preparation is not a claim that the physical suite is ready.

1. [x] **Adapt the Pi runner and its manifest offline.** Remove all startup writes and
   reset-launched tests; use explicit CLI invocation and preserve startup as
   read-only evidence. Enforce checksum-free fast transfers, conditional mode
   selection, at least one-second settling and entry route/mode/CLI restoration.
   Declare output-profile-specific mandatory coverage: native HDMI intentionally
   has no browser-video route, so browser WebSocket frame checks cannot serve as
   its scanout oracle. Preserve browser-video coverage for builds that provide
   it. Bind reset commands to the commissioned actuator and require fresh boot
   plus actual command/service handback; do not infer execution from ready flags
   or an absent serial mirror. Verify these changes offline before any bench use.
2. [x] **Bind exact retained paired installation evidence.** Adapt qualification receipts
   for the accepted P4 r16 and unchanged EMOS v27 without rebuilding or flashing
   merely to fit an old receipt schema. Retain byte-level installation evidence,
   exact source closure and honest archived-patch provenance for EMOS. Resolve
   fixture-source compatibility separately from installed-firmware provenance.
   Missing evidence must block qualification rather than produce a fabricated
   clean-source receipt.
3. [ ] **Run the canonical physical suite when separately authorized.** Check
   bench ownership, actual foreground, attached devices, unchanged normal startup,
   installed identities and reset readiness first. Cover boot/reset, USB/browser
   input, Legacy/ExCom routing, HDMI display/mode behavior, SD round trips and
   independently verified cleanup. Retain the guarded raw-sector write/read/
   restore case, its preimage and uncertain-I/O stop boundary. The historical
   inventory is 25 checks across three cases; profile adaptation must explicitly
   account for coverage rather than quietly skip mandatory browser cases.
4. [ ] **Complete Author visual review.** On the exact combined build, review
   representative loaded graphics/gameplay, mode changes and visible clean exit
   with keyboard/controller attached. Credit the existing accepted controller
   review; do not require an unrelated full rendering/performance campaign.
5. [ ] **Promote after all gates pass.** Retain the complete paired report,
   identities, individual outcomes and durations with preparation, execution,
   retrieval and notification distinguished. Verify the complete native
   installation selection, update production/current.yaml and current guides,
   commit, then create/push the agreed annotated v0.2.1 tag. Preserve immutable
   accepted archives and rollback; no tag or production selection before these
   gates pass.

## Offline preparation result — 2026-10-30

The runner/receipt/fixture preparation is implemented and verified without
contacting either board. [Preparation research](RELEASE-001/QUALIFICATION-PREPARATION.md)
bounds the contracts; [offline results](RELEASE-001/OFFLINE-PREPARATION.json)
records exact hashes and validation scope. The [canonical guide](../../qualification/README.md)
is the current procedure. These results do not close R01-U04's physical gate.

The supported physical entry is an independently verified idle Legacy CLI with
single-buffered modes. QSTATE obtains fresh mainboard mode data, and the Pi
restores both display modes and the entry route. Native HDMI has an explicit
DMA/text/mode profile; browser-video keeps decoded-frame coverage. Startup is
read-only in both the coordinator and rebuilt raw-SD app. The EMOS fixture fix
is committed in its owner as 29434e3; no resident EMOS source/build changed.

Retained schema-2 receipts validate the exact accepted P4 app/full readback and
EMOS full ROM plus source closure (5,533 P4 files; 557 EMOS files and the
archived patch). They explicitly do not establish live identity now. The physical
run additionally compares the current complete EMOS ROM. The P4 current-identity
preflight must establish that its accepted installation evidence still applies;
no reflash is required merely to obtain a receipt.

When the bench is released, remaining preparation is actual paired identity/CLI
verification, reset-bridge actuator commissioning, accepted cue-file review
(fast listener; no mode/startup change), and fixture deployment/readback. Do not
use --bench-ready until those prerequisites are complete. Then stop and announce
readiness before the full suite's invocation, preserving the Author's reserved
invocation boundary. Current bench remains occupied with Extender fully offline.

The separate cadence runner is disabled pending its own lifecycle migration;
that migration and a new performance campaign are not this release's gates.
The existing host inventory is reconciled: 43 omitted no-argument host checks
are registered; one experimental linked-ELF harness is explicitly classified as
requiring separate probe/native/ordinary images and a toolchain. Prior evidence
is unchanged. Production selection/tag and the bounded Author visual review
remain pending.

## Physical preparation — 2026-10-30

The Author releases a ready bench and clarifies that “bench is yours” establishes
ready idle operation; duplicate foreground questions are unnecessary. Preparation
retains the stop before full-suite invocation. No smoke/rendering/raw-sector
workload has been invoked, and the accepted firmware is not replaced.

1. Actual CLI execution is verified by repeated fast listener/startup-read/EXIT
   exchanges. Startup remains the same 108 bytes; no startup write occurs.
2. The complete current EMOS ROM matches the accepted padded v27 SHA-256
   `84da2c5ac3cebb1c470bab201f797a936296a6bfc33b6ebdbcf5d1dd3a1d1d79`.
   Independent P4 prefix readback matches the exact r16 application SHA-256
   `594a15e73aa1480a59e2007de080de7fd7dcd96f8a0f04382037e740ff979a62`
   and the retained bootloader/partition range. No flash write or erase occurs.
3. The existing Agon USB RTS/Q4 circuit replaces the unproved GPIO pulse in the
   private reset bridge configuration. The maintained helper verifies exact
   adapter identity, uses exclusive ownership and releases both controls together.
   The bridge produces a fresh admitted boot and actual CLI handback. P4's
   separate reset command is preserved.
4. The exact offline-built QSTATE and raw-SD binaries are staged/readback under
   `/extender`, alongside the accepted speech player/WAV and a new command file
   using `EMOS sdserve --fast /`. The listener's 22,968 bytes match its accepted
   checksum-free v0.3.0 identity. The player is not invoked during preparation.
5. Ordinary host-driven file commands exposed an unresolved command-handback
   gap. Conservative keyboard pacing and synchronous MOS cleanup batches now
   replace assumptions that event acknowledgement proves filesystem completion.
   Temporary deletion remains restricted to verified session-owned names and
   independently checked absence. One Agon-only recovery failed admission;
   standing P4 clean-init then Agon reset restored actual CLI access. Preserve
   informative evidence; do not claim a diagnosed firmware cause or full pass.
6. Final setup-only mode/cleanup/CLI verification passes. Both displays retain
   single-buffered mode0 and Legacy routing; the foreground listener is stopped,
   input is admitted/neutral, no serial reader or reset hold remains, and all
   identified temporary setup files are removed with independent absence checks.
   The full 25-check suite, raw-sector workload, physical visual review,
   production selection and annotated v0.2.1 tag remain unperformed.

Machine-specific commands, readbacks, manifests and journals are retained in the
ignored release preparation directory and current local bench record. The
[portable preflight record](RELEASE-001/BENCH-PREPARATION-R01.json) records readiness
without a qualification pass. The ignored release directory contains the prepared
explicit Pi launch script; no invocation is queued or running.
