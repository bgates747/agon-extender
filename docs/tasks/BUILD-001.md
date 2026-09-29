# BUILD-001 — Native ESP-IDF/CMake P4 build authority

## Executive summary

**Accepted by the Author on 2026-09-28; frozen by the commit containing this
contract.** Replace
the P4 firmware's PlatformIO/SCons outer build with native ESP-IDF/CMake while
retaining Arduino-ESP32 as a pinned ESP-IDF component. The migration establishes
one authoritative build graph for source selection, compiler options,
dependencies, generated assets, partitions and linked objects. Under the
Author's 2026-09-28 sequencing amendment, it must first reproduce the latest
working pre-LCD ExCom product and provide that closure to AUDIT-010. LCD support
is redeployed only after the audit, review and accepted fixes; it is no longer
part of BUILD-001's initial equivalence baseline.

BUILD-001 is the prerequisite to AUDIT-010's baseline freeze. The
migration must finish, be reviewed and have its resulting source/build identity
recorded before AUDIT-010 A10-02 begins. Until the Author accepts this contract,
no implementation, dependency installation, firmware build, flash, reset, SD
mutation, production selection or audit-baseline change was authorized before
the Author accepted this document.

Created: 2026-09-28. Owning queue: `TODO.md`. Related owners:
[AUDIT-010](AUDIT-010.md), [LCD-001](LCD-001.md), [PORT-003](PORT-003.md),
[PORT-006](PORT-006.md) and [QUAL-001](QUAL-001.md).

## Purpose

Make ESP-IDF/CMake the sole top-level build authority for maintained ESP32-P4
firmware. Arduino-ESP32 remains available as an ESP-IDF component for the
Arduino APIs and upstream-derived code that currently depend on it. Native
ESP-IDF facilities remain native components. The resulting build must expose
the real linked translation-unit closure to CMake and emit a trustworthy
compilation database suitable for AUDIT-010's analysis tools.

The migration must answer these immutable questions:

B01-Q01 [x] Which checked-in artifact is the single authority for selected source
files, and how does CMake consume it without a competing PlatformIO selection?

B01-Q02 [x] How are the ESP-IDF release, tools, Arduino-ESP32 component, managed
components and non-managed third-party sources pinned and reproduced without
depending on unrecorded global developer state?

B01-Q03 [x] How does each maintained P4 build profile express configuration,
feature flags, dependencies, embedded files, partitions and output identity?

B01-Q04 [x] Which current PlatformIO environments are maintained product or
diagnostic profiles that must migrate, and which are obsolete or frozen evidence
that must be disposed explicitly rather than copied forward?

B01-Q05 [x] What evidence demonstrates build equivalence and explains every
material ELF, map, image-size, dependency or runtime difference introduced by
the build migration? Hardware functional equivalence remains B01-06.

B01-Q06 [ ] When can PlatformIO/SCons source selection and its generated CMake
facade be removed from the maintained P4 path without losing rollback,
provenance or a still-used profile?

## Scope and boundaries

The implementation scope is the maintained ESP32-P4 firmware build under
`vdp/`, its project-owned build helpers, configuration, source-selection data,
dependencies, generated assets, tests and current build documentation. Inspect
`../agon-emos` and `../mos-agondev` only where their tools or artifacts consume a
P4 build identity. Official `../../agon-docs`, `../../agon-vdp` and
`../../agon-mos` remain read-only references.

Preserve the selected pre-LCD application behavior and source closure unless a
change is strictly necessary to express the same program under ESP-IDF. Small
compatibility adapters are permitted only when identified individually and
covered by targeted tests. Porting Arduino-dependent application code to pure
ESP-IDF is outside scope. LCD code and its post-r61 source changes are outside
the initial native-equivalence and audit baseline; retain them for LCD-001's
later delta. Repairing LCD behavior, the late-mode20 allocation failure, browser
resource exhaustion, rendering semantics or unrelated defects is outside scope;
record newly exposed defects for their owning tasks.

Production firmware and `production/current.yaml` remain unchanged throughout
the migration. A successful development migration does not authorize production
promotion, a version number, a tag or publication. Do not remove the existing
working build path until the replacement has passed this contract and the Author
accepts the cutover.

Git history and superseded implementations are outside routine discovery. If
current authorities and artifacts cannot resolve a material build contract,
pause before historical review and present the exact question, proposed commits
or date range and stopping condition for Author acceptance.

## Decision register

The Author accepted these decisions with the contract on 2026-09-28.

| ID | State | Recommended decision | Consequence |
|---|---|---|---|
| B01-D01 | [x] Accepted | Native ESP-IDF/CMake becomes the sole top-level authority for maintained P4 builds. | The outer PlatformIO/SCons graph no longer decides which P4 objects are linked. |
| B01-D02 | [x] Accepted | Retain the exact compatible Arduino-ESP32 release as a pinned ESP-IDF component. | Existing Arduino APIs can remain while new native ESP-IDF code does not pass through an Arduino build authority. |
| B01-D03 | [x] Accepted | Retain one neutral, checked-in P4 source/profile manifest and generate or validate CMake inputs deterministically from it. | Source provenance remains machine-readable while CMake compiles the same declared closure; generated files are never a second editable authority. |
| B01-D04 | [x] Accepted | Provide one project-owned wrapper around the pinned native ESP-IDF tools and isolated tool state. | Operators receive repeatable profile selection and identity capture without relying on an ambient `idf.py` installation. |
| B01-D05 | [x] Accepted | Migrate every maintained current or diagnostic P4 profile; explicitly classify obsolete profiles instead of preserving them by default. | Cutover cannot silently strand a qualification or recovery build, while historical experiments do not become permanent maintenance obligations. |
| B01-D06 | [x] Accepted | Judge migration by source/configuration equivalence, explained binary differences and runtime qualification, not presumed byte identity. | Link ordering and native build metadata may change, but unexplained behavioral or material image differences block acceptance. |
| B01-D07 | [x] Accepted | Freeze AUDIT-010's source baseline only after BUILD-001 acceptance. | Static analysis observes the actual native CMake build graph rather than the current hybrid graph's unused object descriptions. |
| B01-D08 | [x] Accepted | Retire the maintained PlatformIO/SCons path only after rollback and clean-build evidence are retained. | The migration remains reversible until the replacement is accepted; frozen historical evidence is not rewritten. |
| B01-D09 | [x] Accepted 2026-09-28 | Rebase BUILD-001 equivalence on the last working pre-LCD Extender commit `6c6bea3beb2f8abc89c5b1f40a0e7dd0890a084d`, paired with EMOS v0.1.23 source `21a9ba27f1f346473d767c2c3053ee18e8911335`. | The combined LCD candidate and its startup failure remain evidence, but AUDIT-010 receives a proven pre-LCD closure; LCD-001 redeploys LCD only after audit fixes. |

## Work contract

### B01-01 [x] Research official integration contracts

The bounded conclusions and exact official sources are recorded in
[RESEARCH.md](BUILD-001/RESEARCH.md).

Read current official ESP-IDF build-system, component-manager, configuration,
tool-installation and compilation-database documentation. Read official
Arduino-ESP32 documentation for use as an ESP-IDF component and establish the
exact Arduino/ESP-IDF compatibility contract for the versions currently pinned
by the project. Consult source only where the official documentation is
insufficient. Record exact documentation, releases, commits and conclusions in
a bounded précis under `docs/tasks/BUILD-001/` before implementation.

B01-01a [x] Determine whether Arduino-ESP32 can be acquired reproducibly as a
managed component at the required version or must be supplied through a pinned
project-owned component source; record integrity and offline-build implications.

B01-01b [x] Establish the native ESP-IDF mechanism for per-profile `sdkconfig`
defaults, partition tables, embedded files, component dependencies and C/C++
compile options used by this project.

B01-01c [x] Establish how the native build emits `compile_commands.json`, map
files, size reports, flash images and dependency locks, and how each artifact is
bound to the selected profile and source revision.

### B01-02 [x] Inventory and preserve the current build contract

Inventory and controls are recorded in [INVENTORY.md](BUILD-001/INVENTORY.md).
The Author accepted the profile dispositions on 2026-09-28: migrate the console,
maintained MOS recovery and active PORT-008 non-release qualification profiles;
freeze superseded diagnostics; preserve rejected profiles as tombstones.

Before changing build files, record the exact repositories, production
selection, development source, PlatformIO platform/framework packages,
toolchains, generated component files and dependency locks. Inventory every
`platformio.ini` environment and classify it as maintained product, maintained
diagnostic, obsolete experiment or frozen evidence. Pause for Author review of
the classification before excluding a profile from migration.

B01-02a [x] Capture the current actual SCons compile and link actions for the
combined ExCom+LCD target, its selected translation units, definitions, include
paths, language standards, component dependencies, embedded assets, partition
table, `sdkconfig`, ELF/map/image sizes and immutable output hashes.

B01-02b [x] Run the currently applicable host-side checks and retain their exact
commands and results as pre-migration controls. Do not initiate a hardware run
without a separately reviewed procedure and explicit Author authorization.

B01-02c [x] Identify every script, document, CI action, qualification profile,
packaging step or operator procedure that invokes PlatformIO or consumes its
output layout.

### B01-03 [x] Review the native-build design

The proposal is recorded in [DESIGN.md](BUILD-001/DESIGN.md) and now pauses for
Author acceptance before any maintained build-path change. The Author accepted
the source/profile authority, wrapper and graph-validator design on 2026-09-28;
the Author then accepted managed Arduino-ESP32 3.3.11 and project-scoped
official ESP-IDF 5.5.5 source/tools. The additive implementation boundary
was accepted on 2026-09-28 through host equivalence only; hardware remains a
separate review gate.

Produce the proposed directory/component graph, source/profile authority,
dependency acquisition and lock strategy, isolated tool environment, output
layout, build-identity format and operator commands. Show how each maintained
profile maps to native ESP-IDF configuration and how the wrapper prevents stale
generated inputs. Pause for Author acceptance of the design before changing the
maintained build path.

B01-03a [x] Name the owner and lifecycle of every generated file. A generator
must fail on stale or inconsistent inputs and must not make generated CMake a
second hand-edited source of truth.

B01-03b [x] Define a build-graph validator that compares declared sources,
compiled objects, linked objects and compilation-database entries, with explicit
handling for framework and third-party component internals.

B01-03c [x] Define rollback so an unsuccessful native migration can restore the
preserved hybrid build without altering production or discarding evidence.

### B01-04 [x] Implement the native ESP-IDF/CMake build

Introduce the minimum checked-in CMake components, profile data and project-owned
wrapper needed to build the preserved P4 source closure with native ESP-IDF.
Retain Arduino-ESP32 as the pinned component selected in B01-01. Keep product
source edits separate from build changes and itemize any unavoidable adapter by
symbol, reason, test and removal condition.

B01-04a [x] Reproduce source selection, language standards, definitions, include
paths, link inputs, embedded assets, partitions, `sdkconfig` values and managed
dependencies for the combined ExCom+LCD target.

B01-04b [x] Map each accepted maintained diagnostic profile without reintroducing
an outer build graph or profile-specific hand-edited source list.

B01-04c [x] Emit immutable build identity, dependency lock, ELF, map, flash
images, size reports and canonical compilation database into a profile-specific
output directory.

B01-04d [x] Ensure a clean checkout can provision or locate the pinned tools and
components through documented, project-scoped commands. Do not modify global
developer packages or hide machine-specific paths in tracked files.

B01-04e [x] Apply the accepted native build authority to the bounded pre-LCD
Extender source `6c6bea3beb2f8abc89c5b1f40a0e7dd0890a084d` without importing
later LCD implementation. Preserve the existing native infrastructure changes
as a reviewable build-only delta and prove that selected project sources match
the retained r61 closure.

The resulting clean branch is `codex/build001-prelcd`. Corrected candidate
`build001-e7b35fd5-console-prelcd`, built at
`e7b35fd5bb5ab88b619a9a433a78ffa132119d19`, selects exactly the retained r61
product closure's 22 project and 11 vendored translation units and no LCD source
or dependency. It explicitly retains r61's staged-WebDAV profile setting and
accepts the private browser-reset endpoint only as a machine-local build input.
The initial boot-only procedure is
[PRELCD-BOOT-PROCEDURE.md](BUILD-001/PRELCD-BOOT-PROCEDURE.md).

### B01-05 [x] Validate build-graph and artifact equivalence

Host evidence and the one remaining static-analysis smoke are recorded in
[VALIDATION.md](BUILD-001/VALIDATION.md).

Run clean native builds and compare them with the B01-02 controls. Triage every
difference before hardware use; do not treat a successful link as equivalence.

B01-05a [x] Prove that every intended project translation unit is compiled once,
every linked project object is represented by the selected source authority, and
the canonical compilation database covers the real linked project closure.

B01-05b [x] Compare configuration, partition layout, embedded assets, symbols,
sections, map ownership, IRAM/DRAM/PSRAM/flash use and image sizes. Explain and
dispose every material difference.

B01-05c [x] Repeat clean builds in fresh output directories and compare outputs.
Record deterministic hashes where achieved; identify and bound any intentional
timestamp, path or tool metadata that prevents byte-for-byte reproducibility.

B01-05d [x] Run applicable host tests, build-graph validation and AUDIT-010's
accepted compiler/static-analysis smoke checks against the canonical database.
Tool findings remain audit inputs and are not repaired inside this migration
unless they prove a migration error.

B01-05e [x] Repeat B01-05a through B01-05d for the pre-LCD native closure and
compare it with retained hardware-tested r61 build
`uart-excom-console-r61-b2026-09-28-03-12-48Z`, factory SHA-256
`f794a8bba96f9afbfc1dae6eaa4554eb676880d76ffe74bda97bbebc7e160fea`.
The completed combined-LCD comparison remains failed/deferred evidence and does
not satisfy this replacement baseline.

### B01-06 [x] Perform bounded hardware equivalence qualification

After B01-05 passes, prepare a run sheet that names the exact firmware, bench
state, expected observations, rollback image, evidence paths and stopping
conditions. Read `HARDWARE.local.md` and current bench constraints, then obtain
explicit Author authorization before flashing or resetting the P4 or deploying
fixtures.

The first authorized attempt failed during ESP-IDF startup and rolled back
safely; see [HARDWARE-RESULTS.md](BUILD-001/HARDWARE-RESULTS.md). No functional
equivalence subitem passed. A corrected immutable candidate and reviewed
procedure dependency are required before B01-06 resumes.

The subsequent native pre-LCD boot canary failed at the identical
`sdio_mempool_create` assertion. Because that candidate selected no LCD source
or dependency, LCD is no longer a candidate cause of this boot loop. B01-HR07
owns diagnosis of the native `esp_hosted`/SDIO build boundary before another
hardware candidate.

B01-HR07 and B01-HR08 subsequently resolved that gate. Native CMake had honored
ESP-Hosted's whole-archive constructor while the working hybrid link omitted
it. Extender uses wired Ethernet, so commit `eadc2925` explicitly disables the
unused remote-Wi-Fi/ESP-Hosted configuration. The exact corrected candidate
booted twice without assertion, initialized USB input and wired Ethernet, and
served HTTP successfully. This is a boot-canary pass, not completion of the
functional-equivalence items below.

The first functional pass then exposed B01-HR09: candidate `d17cae79` booted and
passed Legacy, ExCom, keyboard and HTTP checks, but did not listen on staged
WebDAV port 8081. The migration had reproduced the source closure while omitting
r61's explicit `--staged-webdav` build variant. The corrected native profile now
defines that behavior directly and preserves the private reset endpoint through
a non-tracked wrapper argument. The amended exact-candidate procedure requires
renewed Author acceptance before another flash.

B01-06a [x] Verify flash, boot, EMOS transport, Legacy and ExCom output,
keyboard/input, SD service, browser service and clean recovery using targeted
tests chosen to detect build-migration regressions. Do not enable or test LCD in
this baseline qualification.

B01-06b [x] Run the mode20 static-grid control as an automated fixture with its
mode selected only in `/autoexec.txt`. After all automated passes finish, the
Author manually runs Nurples and other real applications that switch modes
after loading significant VDP-buffer assets. Record the pre-LCD mode-switch,
browser and gameplay result as an equivalence baseline. Do not grant automated
fixtures a mode-switch exception or infer anything about the later LCD resource
failure from a pre-LCD pass.

The controls and human runs are recorded in the accepted procedure and hardware
results. Static mode20 and the asset-heavy transition pass in Legacy; the same
Nurples executable retains 320-by-240 geometry after its late mode20 request in
native pre-LCD ExCom. B01-HR11 must compare the exact hybrid r61 image before
this can be classified as inherited behavior or a migration regression.

B01-06c [x] Keep runtime monitoring bounded. Reusable unattended tests must print
progress on the legacy mainboard display where practical and invoke the existing
audible success/failure notification without overwriting a retained failure
message.

The accepted detached `bench_job.py` terminal-hook contract, focused host tests
and retained hardware result demonstrate this behavior. The failure path plays
its cue before restoring the durable Legacy failure message; the success path
leaves its terminal result visible.

### B01-07 [x] Cut over maintained build consumers

After the Author accepts B01-05 and B01-06 evidence, update maintained build,
test, package and operator entry points to use native ESP-IDF/CMake. Update the
handbook and `docs/building.md`; preserve machine-local details only in ignored
records. Remove or quarantine PlatformIO/SCons generation only after every
B01-02 consumer has migrated or received an explicit disposition.

B01-07a [x] Retain enough identified hybrid-build material and instructions to
reproduce the pre-migration baseline during the agreed rollback interval without
presenting it as the current build authority.

B01-07b [x] Verify that maintained documentation contains one canonical P4 build
procedure and does not direct operators to stale PlatformIO output paths.

B01-07c [x] Present production impact separately. Do not promote, version, tag or
publish a native-built firmware until the Author accepts a production proposal
under the repository's normal promotion rules.

### B01-08 [x] Hand the canonical baseline to AUDIT-010

Record the accepted native-build commit, exact tool/component locks, selected
profile, build identity, artifact hashes and canonical compilation database in
AUDIT-010's baseline ledger. Implement its accepted A10-P02 pre-LCD baseline
amendment while preserving the original frozen A10-P01 combined-LCD direction
as superseded decision history.

B01-08a [x] Demonstrate that AUDIT-010 analysis commands consume actual linked
project actions rather than unused CMake object descriptions.

B01-08b [x] Preserve known LCD/mode20/browser behavior as deferred LCD-001
integration evidence. Do not include LCD code in the exhaustive audit baseline;
after AUDIT-010 review and fixes, require it as a redeployment regression.

## Gates and success criteria

B01-G01 [x] The Author accepted and froze this contract before B01-01 began.

B01-G02 [x] Official integration research and current-profile inventory are
complete before the native design is accepted.

B01-G03 [x] One checked-in authority selects sources and profiles; CMake's actual
compiled and linked graph agrees with it.

B01-G04 [x] The pinned native toolchain and Arduino component build every accepted
maintained P4 profile from clean project-scoped state.

B01-G05 [x] Material configuration, dependency, section, size and binary
differences are explained, and targeted host tests pass.

B01-G06 [x] Author-approved hardware equivalence checks pass with rollback
available and without changing production selection.

B01-G07 [x] Maintained consumers and documentation use the native path; obsolete
PlatformIO profiles and helpers have explicit dispositions.

B01-G08 [x] AUDIT-010 receives a trustworthy canonical compilation database and
an immutable accepted baseline before its exhaustive review begins.

BUILD-001 is complete only when B01-G01 through B01-G08 are satisfied and the
Author accepts the migration result. Completion does not by itself constitute
production promotion.

The native authority was cut over at `755d6f37`; the exact accepted audit
handoff is recorded in [AUDIT-010/BASELINE.md](AUDIT-010/BASELINE.md). Hybrid
r61 material remains explicitly gated rollback evidence. Selected production
v0.1.0/r02 is unchanged. The Author accepted the completed migration result on
2026-09-29; BUILD-001 is closed and removed from the active queue.

## Evidence and change discipline

Store research, inventories, comparison tables, raw build-graph reports and
reviewed result summaries under `docs/tasks/BUILD-001/`; keep bulky generated
build trees and machine-local paths out of Git. Every retained run names its
source commit, profile, tool/component identities, command, output hashes and
result. Use stable `B01-*` identifiers in findings and review discussion.

Commit the accepted contract separately before research or implementation.
Thereafter keep research/design, implementation, validation and cutover changes
reviewable; do not combine unrelated product fixes with build migration. Preserve
dirty work in all participating repositories and never rewrite frozen task
evidence.
