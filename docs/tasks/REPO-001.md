# REPO-001 — Establish agon-emos and disentangle repository histories

## State

- Status: Awaiting Review Gate D — live migration, remote cleanup, and
  fresh-clone qualification complete; recovery bundles retained
- Priority: First in the project queue
- Started: 2026-08-24 17:11 EDT
- Finished: --

## Namespace

`REPO` covers repository ownership, project extraction, history reconstruction,
remote topology, and cross-repository migration. It does not authorize product
firmware changes merely because those changes must move between repositories.

## Intent

Create `agon-emos` under the Author's established project root and a matching
private repository in the Author's GitHub account as the single project home
for Extender MOS (EMOS) customizations and their implementation-specific
documentation, tasks, tests, and qualification evidence.

Restore `agon-mos` to its role as the Author's upstream-oriented official-MOS
fork. Restore `mos-agondev` to its role as reusable AgonDev translation, build,
runtime, emulator, and qualification infrastructure. Remove local and remote
development branches and reachable history from repositories where they do not
belong, while preserving every accepted EMOS result and every reusable generic
improvement in its proper owner.

The Author subsequently reviewed the plan and explicitly authorized repository
creation, content movement, branch and worktree cleanup, and history/remote
reconstruction. Firmware behavior remains outside this migration's authority.

## Execution record

1. Review Gates A and B were accepted when the Author directed execution after
   reviewing this task. Verified pre-migration bundles were created before any
   ref mutation and remain retained pending Review Gate D.
2. The accepted lineage keeps official MOS history through v3.0.2. The generic
   oversized-packet correction remains in both the upstream-oriented MOS line
   and the EMOS ancestry. EMOS source and product support were separated into
   clean commits in the new repository.
3. `mos-agondev` was reconstructed from `c4b1f7a` with independently useful
   generic qualification improvements and a product-neutral source-profile
   interface. EMOS product files and policy were excluded.
4. The committed reconstructed EMOS repository passed the complete generic and
   product qualification gates and reproduced the accepted 113,053-byte binary
   exactly at SHA-256
   `ae0432a84be4be2261095d449627af876c9662d40a08ac334981e12d6dda339f`.
5. `mos-agondev` `dev/sort` is unrelated, unfinished generic qsort/contract work
   and remains in place. `agon-mos` `spool` and `v233` predate EMOS and remain in
   place. No unrelated ref is authorized for deletion.
6. The detailed allocation and before/after refs are recorded under
   `docs/tasks/REPO-001/`.
7. During local cleanup, `make clean` emitted harmless `find` diagnostics after
   the stale generated source worktree had already been moved aside. Preparing
   the new worktree first would avoid the noise; no maintained file or build
   result was affected.
8. A standalone `agon-mos` regression was initially invoked with package-style
   `unittest` syntax even though `tests/` is not a Python package. Direct-file
   invocation passed all three cases. The failed command was an invocation
   error, not a source regression.

## Proposed ownership model

The Author has accepted creation of a private `agon-emos` project. The exact
file allocation remains subject to the inventory and Review Gate A, but the
working ownership model is:

1. `agon-emos` owns the maintained EMOS firmware lineage: the complete
   upstream-shaped MOS source needed to build EMOS, EMOS behavior and APIs,
   EMOS-specific module/service tooling, source tests, implementation
   contracts, project tasks, qualification procedures, evidence, and release
   records.
2. `agon-mos` owns the Author's upstream-oriented official-MOS fork and only
   independently justified stock-MOS work. It must not retain an EMOS product
   branch merely because EMOS is derived from MOS.
3. `mos-agondev` owns reusable machinery for preparing, translating, compiling,
   linking, running, inspecting, and qualifying ZDS-oriented MOS-family source
   with AgonDev. It may contain maintained executable portability and runtime
   support, but no second maintained copy of MOS or EMOS product behavior.
4. `agon-extender` owns cross-component product architecture, EDP/EMOS
   requirements, operating-mode contracts, hardware and transport integration,
   and tasks whose completion spans the complete Extender product. It should
   reference `agon-emos` rather than duplicate EMOS implementation authority.
5. Generated prepared source, translated assembly, object files, maps, and
   firmware images remain disposable outputs and are not imported as maintained
   source into any repository.

## Initial observed state

The execution audit must refresh these facts before acting. At task creation:

1. `agon-extender` is clean on `main` at `3878cc0`, tracking
   `origin/main`. It contains accepted product-level EMOS architecture and
   references to the returned provisional implementation.
2. `agon-mos` is clean on `dev/emos` at `a8dc891`, based directly on official
   MOS v3.0.2 commit `8336409`. The same commit is checked out by a local
   `dev/port-200` linked worktree outside the canonical checkout. Remote
   `origin/dev/emos` points to `a8dc891`; remote `origin/main` remains at
   `8336409`. Remote `spool` and `v233` also exist and predate this work.
3. The single `agon-mos` EMOS commit adds the EMOS Core and modifies MOS
   dispatch, vectors, serial handling, and VDP parsing. It also includes an
   oversized-VDP-packet regression fix that may be useful independently of
   EMOS and therefore must be classified separately rather than discarded with
   the product branch.
4. `mos-agondev` is clean on `dev/emos` at `a695599`. Remote `main`,
   `dev/emos`, and `dev/port-200` all point to that commit. A local
   `dev/port-200` linked worktree outside the canonical checkout points there
   as well. Local `main` remains at pre-EMOS commit `c4b1f7a`; local and remote
   `dev/sort` point to unrelated unfinished qsort work at `0797779`.
5. Seven `mos-agondev` commits after `c4b1f7a` mix EMOS contracts, module and
   provider tooling, tests, fixtures, emulator media, and research with generic
   port qualification, ABI probes, regression infrastructure, source auditing,
   emulator hardening, and hardware-evidence tooling. Those commits cannot be
   removed safely as one undifferentiated block.
6. Existing EMOS implementation documentation, research, tasks, and evidence
   are concentrated in `mos-agondev`; source behavior and one source-level
   regression test are in `agon-mos`; system architecture and downstream tasks
   are in `agon-extender`.

## Work 1 — Freeze and audit every affected repository and remote

1. Record clean/dirty status, current commit, branch upstream, remotes, default
   branch, tags, stashes, local branches, remote-tracking branches, linked
   worktrees, submodules, Git LFS state, and untracked files for
   `agon-extender`, `agon-mos`, and `mos-agondev`.
2. Query GitHub read-only for repository visibility, default branch, branch
   protection/rulesets, forks, pull requests, issues, releases, Actions
   artifacts, deployment environments, webhooks, Pages, and all remote refs
   that could retain or expose the histories being reorganized.
3. Find every other local clone, worktree, bundle, patch, archive, remote, and
   cross-agent workspace that may hold an affected branch or assume an old
   commit identity. Do not delete or alter any result during this inventory.
4. Produce a commit-and-path manifest for all changes after the selected clean
   baselines. Classify each path and each logically separable change as:
   `EMOS product`, `generic MOS`, `generic AgonDev port`, `Extender product`,
   `generated`, `historical evidence`, `superseded`, or `unresolved`.
5. Audit non-EMOS branches independently. In particular, do not infer that
   `agon-mos` `spool`/`v233` or `mos-agondev` `dev/sort` should be deleted merely
   because they are non-default branches. Record their provenance, purpose,
   remote relationship, and proposed disposition for Author review.
6. Record exact dependency edges: which `mos-agondev` tests and evidence require
   which `agon-mos` source changes, which Extender documents pin returned EMOS
   commits, and which future tasks currently assume the old repository names or
   branches.

### Work 1 output

Create a task-local, machine-readable inventory plus a concise human review
that accounts for every affected commit, ref, path, worktree, remote object
class, and cross-repository reference. No migration decision may rely solely on
directory names or the commit in which a change happened.

## Work 2 — Freeze the target repository and content allocation

1. Define the tracked top-level structure of `agon-emos`, including maintained
   MOS-derived source, EMOS-owned tools, contracts, tasks, research, evidence,
   tests, build entry points, and generated-output exclusions.
2. Decide whether `agon-emos` begins with the official MOS history through the
   selected tagged baseline and clean EMOS commits on top, or with an orphan
   snapshot. The default recommendation is to retain the official MOS lineage
   because recognizable upstream ancestry materially assists future tagged
   release integration; imported local commits must nevertheless be cleanly
   scoped and reviewed.
3. Define the durable interface by which `agon-emos` consumes generic
   `mos-agondev` tooling without copying that machinery or depending on an
   untracked moving checkout.
4. Allocate every mixed `mos-agondev` change individually. Move EMOS product
   contracts, module/container tooling, fake-provider fixtures, EMOS-specific
   tests, implementation logs, and qualification evidence to `agon-emos`.
   Retain generic translator, linker, runtime, ABI, emulator, inspection,
   regression, and hardware-evidence improvements in `mos-agondev` only when
   they are independently valid for ordinary MOS-family inputs.
5. Allocate the oversized VDP-packet correction independently: retain it in a
   clean stock-MOS lineage, move it solely to `agon-emos`, prepare it for an
   upstream contribution, or preserve it only as regression evidence. Do not
   let its accidental co-location in `a8dc891` decide its ownership.
6. Identify Extender documents that remain legitimate product authority,
   implementation-specific material that should move to `agon-emos`, and
   stale commit/branch/path references that must be updated. Historical logs
   may retain truthful provenance but must not masquerade as current ownership.
7. Define the task authority after migration: `agon-emos/TODO.md` owns EMOS
   implementation work, `mos-agondev/TODO.md` owns generic port infrastructure,
   and `agon-extender/TODO.md` owns system-level integration and product gates.

**Review Gate A:** The Author approves the complete path/change allocation,
target repository structure, history basis, source baseline, dependency model,
and task ownership before any repository is created or reconstructed.

## Work 3 — Prepare a reversible migration and purge procedure

1. Define exact preconditions and command sequences for creating the local
   repository and private GitHub remote, reconstructing each retained lineage,
   publishing it, changing default branches or protections, deleting unwanted
   refs, and updating local checkouts.
2. Use explicit commit IDs and `--force-with-lease` expectations. Never identify
   a destructive target through an unresolved glob, symbolic branch, moving
   remote-tracking name, or broad directory.
3. Define a temporary recovery artifact, such as reviewed Git bundles or
   read-only mirror clones outside the working repositories. Inventory its
   exact contents, location, retention period, and final destruction gate so a
   safety copy does not silently become permanent forbidden history.
4. Distinguish two meanings of remote erasure:
   1. **Ref-visible cleanup:** ordinary clones and GitHub branch/tag views no
      longer expose the unwanted lineage after branch deletion and history
      reconstruction.
   2. **Object-level purge:** unreachable Git objects and provider-maintained
      caches are also removed as far as GitHub can guarantee, which may require
      deleting/recreating a repository or GitHub Support rather than merely
      force-pushing refs.
5. Recommend the required erasure level for each repository. Do not claim that
   deleting branches or force-pushing Git immediately destroys unreachable
   objects on GitHub, in local reflogs, in Actions caches, or in unknown clones.
6. Define an abort and restoration procedure for every destructive phase. The
   new `agon-emos` remote and a verified recovery artifact must exist before the
   first source ref is removed.

**Review Gate B:** The Author approves the exact preservation method, erasure
standard, repositories and refs to rewrite/delete, force-push plan, GitHub
setting changes, and recovery/abort procedure. This is the explicit destructive
authorization gate; approval of Work 2 is not sufficient.

## Work 4 — Construct and qualify `agon-emos`

1. Create `agon-emos` under the Author's established project root with the
   accepted lineage and source baseline. Add project-local instructions, one
   authoritative TODO, ownership documentation, generated-file exclusions,
   and links to canonical Agon development policy.
2. Create the matching `agon-emos` repository in the Author's GitHub account as
   a private repository, configure the approved default branch and protections,
   set the local remote, and publish only the reviewed lineage.
3. Import each accepted EMOS source, tool, contract, task, research, evidence,
   fixture, and test according to the migration manifest. Preserve provenance
   without copying generated build trees or stale ownership claims.
4. Make the new repository independently understandable from a fresh clone.
   Document its dependency on a pinned `mos-agondev` interface and the process
   for incorporating later tagged official MOS releases.
5. Build and run the complete available EMOS qualification suite from the new
   topology. Compare firmware, maps, ABI evidence, module images, emulator
   behavior, and regression results with the accepted pre-migration candidate.
   Any intentional difference requires an explicit explanation and approval.
6. Update but do not yet publish dependent current documents in
   `agon-extender` and generic interfaces in `mos-agondev` so they refer to
   `agon-emos` as the product authority.

**Review Gate C:** The Author reviews the complete new repository, migrated
content, dependency interface, builds, tests, comparison evidence, and proposed
cross-repository edits before any old branch or reachable history is removed.

## Work 5 — Reconstruct the source repositories and remove misplaced history

1. Reconstruct `agon-mos` at the accepted upstream-oriented lineage. Preserve
   only independently accepted generic MOS changes. Remove local worktrees and
   local/remote EMOS refs using the exact targets approved at Review Gate B.
2. Reconstruct `mos-agondev` from the accepted pre-EMOS baseline plus cleanly
   reapplied generic improvements. Remove EMOS product files and documentation,
   update its tests and setup to consume selectable MOS-family source, and
   delete approved local/remote EMOS and temporary qualification refs.
3. Resolve `dev/sort`, `spool`, `v233`, tags, stashes, pull-request refs, and any
   other audited branch individually according to the accepted disposition.
   No unrelated branch is deleted by category or implication.
4. Publish reconstructed default branches and delete approved remote refs only
   after rechecking leases, repository protections, new-repository reachability,
   and recovery artifacts immediately before each operation.
5. Remove or replace stale worktrees and remote-tracking refs without deleting
   any working tree that contains uncommitted or unpreserved content.
6. Apply the accepted object-level purge procedure if Review Gate B requires
   more than ref-visible cleanup.

## Work 6 — Reconcile cross-project authority and verify the result

1. Publish the reviewed `agon-extender` reference and task updates,
   `mos-agondev` generic reconstruction, and `agon-mos` cleanup in dependency
   order. Record exact resulting commit and remote identities.
2. Verify from fresh temporary clones that:
   1. `agon-emos` contains all accepted EMOS source and durable support;
   2. `agon-mos` exposes no prohibited EMOS branch or reachable EMOS commit;
   3. `mos-agondev` exposes no prohibited EMOS product branch or reachable
      product history and still performs its generic port role;
   4. default branches, visibility, protections, tags, releases, and advertised
      clone instructions are correct; and
   5. cross-project documents and TODOs identify one authority for each current
      requirement, implementation, task, and qualification record.
3. Run the accepted stock-MOS, AgonDev-port, EMOS, and Extender regression gates
   at their new boundaries. Hardware and emulator claims remain subject to
   their existing human approval gates.
4. Produce a before/after ref and ownership report, including any unreachable
   objects GitHub may temporarily retain and any historical references
   deliberately preserved as truthful provenance.
5. After Author acceptance, remove temporary recovery artifacts under their
   approved destruction procedure, close REPO-001 in the development log, and
   remove it from the authoritative TODO.

**Review Gate D:** The Author accepts the fresh-clone evidence, repository
ownership report, build and test results, remote state, and recovery-artifact
disposition before the migration is declared complete.

## Non-goals

1. Do not redesign EMOS behavior, the module ABI, operating modes, EDP
   transports, or Extender hardware as part of repository disentanglement.
2. Do not opportunistically clean unrelated source, squash legitimate upstream
   history, rename product interfaces, or resolve unrelated TODO items.
3. Do not submit upstream issues, pull requests, or patches without separate
   explicit authorization.
4. Do not claim secure erasure from unknown clones, caches, backups, or hosting
   provider storage beyond the evidence and guarantees actually obtained.

## Completion criteria

1. The private `agon-emos` remote and its local checkout are the sole maintained
   authority for EMOS product source and implementation-specific support.
2. Every pre-migration EMOS artifact and reusable generic improvement has an
   accepted disposition and a verified destination or explicit rejection.
3. `agon-mos`, `mos-agondev`, and `agon-extender` have unambiguous, documented,
   non-duplicative ownership boundaries and authoritative TODOs.
4. All approved misplaced local and remote refs are removed, reconstructed
   histories expose only accepted content, and the achieved erasure level is
   stated accurately.
5. Fresh-clone builds and applicable regression checks pass from the new
   topology, subject to existing emulator and hardware human gates.
6. The Author accepts the final evidence and authorizes destruction of the
   temporary recovery artifacts.
