# PORT-008 Work 2.e production-object provenance gate

- Status: product policy, raw-record adapters, validator/comparator, and
  adversarial host tests implemented; intended-command fingerprints await a
  clean rehearsal, no target evidence has been accepted, and no equivalence
  claim is available
- Owner: PORT-008 under accepted `PORT-008-D002`
- Policy: `production-object-policy.json`
- Build-record skeleton: `BUILD-RECORD.template.json`
- Gate: `../scripts/validate-production-object-provenance.py`
- Tests: `../tests/test_production_object_provenance.py`

## Outcome and claim boundary

This is the Work 2.e product gate. It supersedes the retained schema-v1
similarity checker only for Work 2.e production-object claims. The preliminary
checker remains intact for interpreting its earlier reports; it cannot close
`PORT-008-D002`.

The gate consumes the recorders' raw actual-step evidence rather than a
manifest-selected compiler replay. The tracked policy, not the evidence, owns
the complete target, role, unit, symbol, tool, environment, and identity sets.
For every policy-required production unit, validation establishes all of the
following before comparison:

1. The maintained product source, task policy, version registry, recorder, and
   named build-boundary files are clean files at exact Git commits. For P4,
   this does not turn every PlatformIO platform/framework builder or package
   script into tracked product authority; those remain in the trusted-host
   boundary described below.
2. The selected target compiler/assembler/linker and inspection executables
   match policy-pinned bytes and reproducible identity probes. P4 additionally
   proves the compiler-selected `cc1plus`, assembler dispatcher and exact
   xespv2p1 backend, `collect2`, and linker. Its capture record binds the
   resolved Python executable, PlatformIO/SCons package trees, and PlatformIO
   launcher file. This is not complete dynamic-loader, shared-library, Python
   standard-library, dependency-package, or host execution closure.
3. Every role-required unit command and the final-link command must match a
   tracked normalized fingerprint. The fingerprint covers actual argv,
   response-file bytes and boundaries, expanded argv, and effective selected-
   tool/probe material. Normalization replaces only declared root paths and
   exact per-build identity-definition values; it does not ignore flags,
   ordering, forced includes, plugins, specs, scripts, libraries, or wrappers.
4. A fresh recorder session observed the actual producer, hashes every
   declared response/dependency before and after use, and binds the producer's
   exact output into the actual final link.
5. The final link map has one direct `LOAD`, a nonzero allocated contribution,
   and one unambiguous owned-symbol origin for each policy unit. Object and
   linked-image symbol/disassembly records are derived with policy-pinned
   target tools.
6. The produced image contains the firmware source identity, immutable build
   ID, and lifecycle status from the build record. A qualification image must
   also contain the separately revisioned
   `port-008-forward-qualification` composition identity. These values may be
   local only to the composition/boot owner; common units must remain neutral.
7. Qualification and release captures have distinct recorder sessions,
   evidence instances, build records, images, and immutable build IDs.
   Equality units must then have identical source/dependency/declaration sets,
   target executable identities, child environments, response files, compile
   commands, object bytes, object symbols, object disassembly, and the policy-
   selected owned-symbol contracts plus those symbols' normalized linked
   instructions.

The gate deliberately scopes final-link claims to the policy-required objects.
It does not claim that P4 evidence enumerates every implicit driver runtime,
`-l` resolution, default linker script, framework archive, or whole-image link
input. Each required unit must nevertheless be an exact actual-link input and
must contribute owned code. Linked disassembly is symbol-relative and limited
to the policy-selected owned symbols: the gate removes each selected symbol's
absolute start address, records instruction offsets from that start, and
replaces rendered absolute symbol targets with their symbol names.
Qualification and release records for those selected symbols must still match.
A different relaxation/opcode/immediate within that selected set therefore
fails even when object bytes match, while a harmless whole-image address/layout
shift does not. Exact pre-link object bytes remain the complete byte-level
equality authority for each required object; the linked-disassembly result is
not a whole-object or whole-image instruction-coverage claim.

EMOS linker `--trace` output is required, nonempty, and hash-bound. It is a
diagnostic only: the gate does not parse it into a broader link-closure claim.
EMOS product evidence currently admits no response files at all. Its recorder
file and selected target commands are authenticated, but the Python runtime
which launched the recorder, GNU Make/shell, dynamic loader, shared libraries,
and compiler-internal runtime/config closure are not recorded. The validation
report therefore says `capture_runtime_authority_proved: false` for EMOS and
keeps the host-runtime boundary explicit.

No validation or comparison establishes runtime behavior, activation,
return-transport behavior, deployment authority, electrical safety, wiring,
or physical qualification.

## Current honest result

Work 2.e cannot currently produce an eligible comparison:

1. Every per-role unit and final-link command-fingerprint slot in the tracked
   policy is intentionally null and the target policies remain
   `awaiting-clean-rehearsal`. Validation emits candidates but cannot mark
   `intended_command_policy_proved` or `equivalence_eligible` until reviewed
   hashes are committed and both roles are recaptured under that policy.
2. The version registry has no approved successor identity for either
   `agon-emos` or `extender-vdp`. Their latest recorded firmware identities are
   rejected predecessor identities.
3. The only registered `port-008-forward-qualification` revision is rejected.
4. No production P4 release composition consumes the P4 production units.
   `p4-browser-vdp` uses `DisconnectedStream` and is not a release surrogate.
5. No real P4 target capture has integrated the final actual-step recorder
   shape, and no Work 2.e EMOS ordinary/fixed pair has been captured.
6. `PORT008-PROV-P023` through `PORT008-PROV-P031` are corrected in source or
   pre-baseline evidence tooling but lack fresh target evidence. P024/P025
   specifically require equality of
   common compile commands and dependencies after role/identity flags became
   translation-unit-local; no waiver is allowed for coincidentally equal
   object bytes.

An unversioned mechanical rehearsal may use explicit, distinct
`UNVERSIONED-...-DO-NOT-DEPLOY` build markers for the two roles and the
unversioned qualification-composition marker. That permits the mechanics to be
exercised without inventing identities. The gate will report the registry and
embedded-marker blockers, will not set `equivalence_eligible`, and will not set
`equivalence_proved`.

## Evidence layout

Raw evidence directories are machine-local and remain untracked. The records
contain absolute build topology, live inode/time snapshots, package-tree
inventories, and per-run nonces. Moving, editing, normalizing, or committing a
raw directory invalidates evidence. A durable qualification record may later
record the gate report, hashes, approved identities, and custody location; it
must not replace the raw directory while validation is pending.

Each build uses a different fresh evidence directory:

```text
<evidence-root>/
  BUILD-RECORD.json
  ... recorder-owned raw records ...
```

For EMOS, the recorder owns `.mos-agondev-provenance-session.json`,
`compile/`, `assemble/`, and `link/firmware.json`. The build record names one
unit record for every role-required policy unit and names
`link/firmware.json` as `capture.link_record`.

For P4, the recorder owns `session.json`, `events.jsonl`,
`provenance.json`, response blobs, and dependency-scan records. The build
record names `provenance.json` as `capture.record`; P4 `unit_records` stays
empty and `link_record` stays null because the adapter rederives both from the
raw JSONL/report/session chain.

## Creating a build record

Do not edit the template into a pretend passing example. For each actual
capture, copy `BUILD-RECORD.template.json` to the fresh evidence root as
`BUILD-RECORD.json`, then populate these fields from the same capture:

1. Set `policy_sha256` to the lowercase SHA-256 of the committed
   `production-object-policy.json` bytes.
2. Set `target` to `emos` or `p4`, and `role` to `qualification` or `release`.
3. Populate `identity` before interpreting the capture. `artifact_id`,
   `variant`, source identity, lifecycle status, and qualification composition
   artifact must match policy and the authoritative version registry.
   `build_id` uses
   `<source-identity>-bYYYY-MM-DD-HH-MM-SSZ`; qualification and release need
   different build IDs even when their source identity and lifecycle lineage
   are the same. Release composition fields are null. Qualification uses exact
   artifact ID `port-008-forward-qualification` plus its approved revision.
4. Populate `repositories` in policy order. Each row contains the policy ID and
   root name, exact `git rev-parse --verify HEAD^{commit}` result, and
   `dirty: false`. Do not set false unless
   `git status --porcelain=v1 --untracked-files=all --ignore-submodules=none`
   is empty. The gate independently repeats both checks and compares every
   authority file with its committed blob.
5. Populate capture references with paths relative to the evidence root and
   lowercase SHA-256 digests of the referenced raw JSON files. Do not use
   absolute paths in build-record references. The adapters independently
   rehash the raw files and every raw-record artifact.

For EMOS, set `capture.format` to the policy value, set `capture.record` null,
set `capture.link_record` to `{"path":"link/firmware.json","sha256":"..."}`,
and create one same-shaped `capture.unit_records[<policy-unit-id>]` reference
for every role-required unit. For P4, set `capture.format` to the policy value,
leave `unit_records` empty and `link_record` null, and set `capture.record` to
`{"path":"provenance.json","sha256":"..."}`. The gate rejects an omitted,
extra, or evidence-selected unit key.

Useful read-only commands are:

```text
sha256sum \
  docs/tasks/PORT-008/production-equivalence/object-equivalence/production-object-policy.json

git -C <repository-root> rev-parse --verify 'HEAD^{commit}'
git -C <repository-root> status --porcelain=v1 \
  --untracked-files=all --ignore-submodules=none

sha256sum <evidence-root>/<raw-record-relative-path>
```

The template's nulls are intentionally invalid. A missing field, reordered or
wrong repository set, dirty repository, stale digest, unsupported extra field,
or evidence-selected unit causes a fail-closed structural error.

## Root bindings

Every CLI root is explicit `NAME=/absolute/path`; the supplied set must match
policy exactly. Roots may be nested where policy requires it, but may not
alias one another. Every strict root is checked from the filesystem anchor
through the root itself; a symlinked ancestor fails. A root policy may allow
only that root's leaf to resolve through a symlink. The separately recorded P4
virtual-environment Python launcher symlink must still resolve exactly to the
policy-pinned interpreter bytes.

EMOS bindings:

1. `AUTHORITY`: this clean `agon-extender` repository.
2. `SOURCE`: the clean `agon-emos` repository.
3. `BUILD_TOOL`: the clean `mos-agondev` repository.
4. `PYTHON_ENV`: the selected Python environment whose interpreter the policy
   pins.
5. `PREPARED`: the exact generated MOS prepared worktree and metadata.
6. `BUILD`: exactly `BUILD_TOOL/projects/mos-port`; every claimed product step
   runs there, objects/maps/ELF remain under it, and the final link consumes
   exact `BUILD/ld/mos.ld`.
7. `TOOLCHAIN`: the selected AgonDev release root.
8. `PROVENANCE`: the fresh EMOS evidence root.

P4 bindings:

1. `AUTHORITY` and `SOURCE`: two separate clean `agon-extender` worktrees at
   the same exact commit. `AUTHORITY` owns policy/registry files and `SOURCE`
   owns the product build. Neither may be the ordinary dirty working checkout.
2. `PROJECT`: the product worktree's nested `vdp` directory. The gate requires
   it to resolve exactly to `SOURCE/vdp`; using the Git top level as PROJECT or
   using `vdp` as SOURCE fails.
3. `BUILD`: the environment build directory
   `PROJECT/.pio/build/p4-port008-nonrelease-qualification` for the captured
   qualification role.
4. `PIO_PACKAGES`: exactly `PROJECT/.pio/packages`, the captured project's
   package store. A global PlatformIO home is not an accepted surrogate.
5. `TOOLCHAIN`: exactly
   `PIO_PACKAGES/toolchain-riscv32-esp`, the local RISC-V package used by the
   captured project.
6. `VENV_RUNTIME`: exactly `SOURCE/.venv`, containing the canonical local
   PlatformIO installation used to launch the build. The recorded PlatformIO
   tree and executed `platformio/__main__.py` launcher must be under this root;
   the imported SCons tree remains under `PIO_PACKAGES`.
7. `PYTHON_RUNTIME`: the resolved CPython installation root named by the
   capture-runtime policy.
8. `PROVENANCE`: the fresh P4 evidence root.

The P4 `AUTHORITY` and `SOURCE` roots cannot be the same resolved directory
because aliasing is rejected. Create two separate clean worktrees at the same
committed extender head: one policy/registry authority worktree and one product
worktree. The gate requires their commits to be equal within each build and
requires the qualification and release captures to use that same commit. Do
not use a dirty working checkout as either root.

## Capture and command-policy rehearsal

The P4 qualification capture is explicitly opt-in. Start from the clean
product worktree and use its copied virtual environment's interpreter, not the
`pio` script whose shebang may name a different worktree:

```text
unset AGON_EXTENDER_P4_PROVENANCE_DIR
<SOURCE>/.venv/bin/python -m platformio run \
  --project-dir <PROJECT> \
  --environment p4-port008-nonrelease-qualification \
  --target clean

AGON_EXTENDER_P4_PROVENANCE_DIR=<fresh-absolute-evidence-root> \
<SOURCE>/.venv/bin/python -m platformio run \
  --project-dir <PROJECT> \
  --environment p4-port008-nonrelease-qualification
```

The evidence directory must not already exist. The clean invocation must not
carry the capture variable. Raw P4 evidence binds the PlatformIO `__main__.py`
launcher under `VENV_RUNTIME`; imported SCons remains under
`PIO_PACKAGES/tool-scons`. Legitimate non-product framework compiles are only
classified under policy-owned prefixes and are reported as unclaimed external
steps; they do not acquire product-source or whole-link authority.

The first clean role pair is a fingerprint rehearsal, not final evidence:

1. Commit the policy with all `unit_command_sha256` and
   `final_link_command_sha256` entries null and status
   `awaiting-clean-rehearsal`.
2. Capture both roles in distinct fresh evidence roots and create their build
   records. Explicit distinct unversioned build markers are permitted for this
   mechanical pass.
3. Run `validate --report <new-report>` for each role. Exit 1 is expected. The
   report contains the exact review material and hashes at
   `capture.command_policy.candidates.unit_commands`,
   `unit_command_sha256`, `final_link_command`, and
   `final_link_command_sha256`.
4. Review the normalized argv, response records, effective subtool selection,
   forced includes/defines, plugins/specs, link scripts/libraries, and input
   order. Copy only reviewed hashes into the matching target/role policy maps.
   Populate every role slot, set `command_policy_status` to `frozen`, and
   commit the policy. Do not derive a waiver from matching object bytes.
5. Discard the rehearsal as eligibility evidence and recapture both roles.
   Changing the committed policy changes `policy_sha256`, so old build records
   cannot pass under the frozen policy.

P4 cannot complete step 2 for a release role until a real release consumer
exists. Its command policy therefore remains awaiting rehearsal. Do not fill
that role from the browser build or fabricate a hash.

## Validation commands

Validate one raw build without writing a report:

```text
.venv/bin/python -B \
  docs/tasks/PORT-008/production-equivalence/scripts/validate-production-object-provenance.py \
  validate \
  --policy docs/tasks/PORT-008/production-equivalence/object-equivalence/production-object-policy.json \
  --build-record <evidence-root>/BUILD-RECORD.json \
  --evidence-root <evidence-root> \
  --root NAME=/absolute/path \
  ...one --root for every target-policy root...
```

Add `--report <new-path>` only for a new nonexisting output. The gate refuses
to overwrite. Exit status is 0 only when that build is eligible for comparison,
1 when validation is sound but policy/identity/release prerequisites make it
ineligible, and 2 for malformed, stale, contradictory, or unauthenticated
evidence.

Compare independently captured roles:

```text
.venv/bin/python -B \
  docs/tasks/PORT-008/production-equivalence/scripts/validate-production-object-provenance.py \
  compare \
  --policy docs/tasks/PORT-008/production-equivalence/object-equivalence/production-object-policy.json \
  --qualification-build-record <qualification-evidence>/BUILD-RECORD.json \
  --qualification-evidence-root <qualification-evidence> \
  --qualification-root NAME=/absolute/path \
  ...all qualification roots... \
  --release-build-record <release-evidence>/BUILD-RECORD.json \
  --release-evidence-root <release-evidence> \
  --release-root NAME=/absolute/path \
  ...all release roots... \
  --report <new-comparison-report.json>
```

The comparator revalidates both raw captures from scratch. It never accepts
previous validation JSON as input.

## False-green cases explicitly rejected

The adversarial boundary includes, at minimum:

1. evidence omits a policy unit/symbol or adds an unselected project unit;
2. qualification and release reuse a session, build record, evidence instance,
   final composition, or immutable build ID;
3. a build record is relabeled onto unchanged raw evidence;
4. role/identity flags leak into a common unit even when object bytes match;
5. an EMOS command uses any response indirection, or a P4 response is absent,
   changed, ambiguously reused, nested, not byte-round-trippable through the
   pinned SCons encoding, or expands differently from recorded argv;
6. dependency, generated-source, selector, manifest, recorder, source, selected
   tool, recorded P4 capture-runtime, object, map, or final image bytes change
   after capture;
7. a declared nested compiler/linker tool was not proven as the selected
   executable, or an option can redirect to a plugin/spec/wrapper/tool path;
8. a linker command mentions an object but the actual producer chain, direct
   map `LOAD`, nonzero contribution, exact symbol owner, or disassembly origin
   is absent;
9. a P4 generated `video/CMakeLists.txt` differs from the canonical bytes
   rederived from the committed selector and source-selection manifest;
10. Git is dirty, the P4 authority/product commits differ, the two roles use
    different source/registry lineage, a policy/selector/recorder file differs
    from its committed blob, a path escapes its declared root, or a symlinked
    ancestor crosses a strict authority boundary;
11. a command fingerprint is unset/unfrozen, or an extra/reordered flag,
    define/undefine, forced include, plugin, spec, wrapper, link script,
    library, response blob, effective Clang invocation, or link input changes.

## Host validation

Run the focused gate tests from the repository root:

```text
.venv/bin/python -B -m unittest -v \
  docs/tasks/PORT-008/production-equivalence/tests/test_production_object_provenance.py
```

Run the complete task-local host suite with:

```text
.venv/bin/python -B -m unittest discover \
  -s docs/tasks/PORT-008/production-equivalence/tests -v
```

These tests create temporary synthetic records/files only. They do not build,
deploy, reset, power, or communicate with target hardware.

## Retained preliminary checker

The historical `validate-target-object-equivalence.py` and
`target-object-equivalence-v1.schema.json` remain available. They compare
supplied compiler outputs and selected final symbol/disassembly records, and
they can replay supported compiler-driver commands. They do not authenticate
Git claims or evidence-selected tools, do not prove actual final-link
consumption or nonzero contribution, and cannot represent the wrapped/direct
assembly boundary used by EMOS. Every successful preliminary report therefore
sets `equivalence_proved: false`.

Do not convert a preliminary manifest/report into a Work 2.e build record. Raw
actual-step evidence must be captured anew under this policy.
