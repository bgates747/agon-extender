# PORT-003 — Implement the P4 display backend and logical frame service

## State

- Status: In progress — Phases A–C complete; Phase D in progress
- Started: 2026-08-22 10:14 EDT
- Finished: --

## Intent

Implement the accepted Work 1.d display boundary: retain the official VDP
screen facade, FabGL Canvas, and common bitmapped rendering semantics while
replacing the classic-ESP32 concrete VGA physical-controller family with an
Extender-owned P4 concrete `BitmappedDisplayController`.

The backend produces framebuffer state and logical frame progression
independently of any one output sink. The guaranteed network/browser path and
later P4-native local-display paths consume that common rendering model rather
than defining separate VDP implementations.

## Authority and inputs

- [SETUP-004 Work 1.d](SETUP-004.md#work-1d-execution-record) and its generated
  display-driver inventory.
- [ADR-0013](../decisions/ADR-0013-vdp-survey-integration-boundaries.md),
  especially decisions 16–21.
- [Current architecture](../architecture.md).
- [PORT-001 dependency graph](PORT-001.md) and
  [PORT-002 source-selection work](PORT-002.md).

## Required outcomes

1. Preserve the official screen-facade names, placement, ownership, mode and
   fallback behavior, dimensions, scaling, palette/Copper state, logical frame
   counter, completion waits, and buffer swaps through narrow integration
   changes.
2. Preserve Canvas and common primitive, paint, clipping, geometry, glyph,
   bitmap, sprite, cursor, readback, completion, and buffering semantics.
3. Supply an Extender-owned concrete bitmapped controller and framebuffer/frame
   service without retaining the old GPIO-matrix, I2S1, DMA-chain, or VSync-ISR
   physical engine.
4. Preserve stock mode dimensions, palette quantization, Copper scanline
   effects, sprite composition, readback, double buffering, frame waits and
   counters, callbacks, and failure/fallback behavior as closely as practical.
5. Reuse separable upstream algorithms where useful, keep every unavoidable
   P4 substitution narrow and provenance-rich, and update the dependency graph
   and compatibility delta.
6. Feed the initial network/browser video sink from the common framebuffer
   service. Treat MIPI-DSI and other local display sinks as separately
   selectable output implementations over the same rendering model.
7. Add deterministic host-side tests where possible and qualified target tests
   for rendering fidelity, frame behavior, concurrency, memory limits, and
   output-sink integration.

## Dependencies and gates

- Complete SETUP-004 before implementation so audio, input, network, and
  storage boundaries cannot be mistaken for display-backend ownership.
- PORT-002 must represent old concrete controllers as vendored but excluded and
  identify the selected replacement closure.
- `SETUP-005-D002` governs operating-mode lifecycle and later qualifies which
  processor owns the facade during transitions.
- QUAL-001 Review Gate 1 must be accepted before Phase D implementation so
  palette, Copper, overlay, and later facade decisions update durable
  compatibility obligations as they are made.
- PORT-008 supplies the physical command/response transport and official
  General Poll canary after Phase E. PORT-008 Gate 2 and the applicable
  QUAL-002 assembled-system scope must pass before PORT-003 Gate G can claim
  end-to-end Agon compatibility.
- Define detailed implementation phases and acceptance fixtures with the
  Author before coding. Do not infer pixel-level fidelity merely from a
  successful build or visible image.

## Review Gate 1 work plan

This plan is the scope fence for the evidence-and-design pass approved by the
Author on 2026-08-22. Check it before beginning each numbered item and record
results against the same number. Do not begin production implementation during
this pass.

1. [x] Freeze scope, authoritative inputs, evidence requirements, deliverable
   structure, and stop conditions in this task and its task-local directory.
2. [x] Review official Agon documentation, official VDP `v2.16.0`, the pinned
   vdp-gl release, accepted ADRs, SETUP-004 Work 1.d, and PORT-002 selection
   evidence. Record exact source entry points rather than performing an
   unbounded firmware survey.
3. [x] Generate bounded, deterministic display dependency inventories and slices
   from the durable dependency graph. Keep generated evidence machine-readable
   and make every human projection reproducible.
4. [x] Trace retained behavior manually from the official screen facade through
   Canvas and the abstract bitmapped-controller contract. Separately inventory
   classic-ESP32 VGA assumptions and classify each as retained algorithm,
   replaceable platform seam, excluded physical engine, or unresolved risk.
5. [x] Inspect only pinned ESP32-P4 framework facilities relevant to memory,
   scheduling, synchronization, cache/DMA constraints, and potential frame
   consumers. Use disposable compile probes only when they answer a recorded
   feasibility question; do not alter upstream checkouts or claim hardware
   qualification.
6. [x] Propose the narrow P4 `BitmappedDisplayController`, logical frame lifecycle,
   memory/concurrency model, and sink-neutral consumer interface. Preserve the
   accepted upstream-shaped facade and explicitly leave SETUP-005 mode policy
   outside the backend.
7. [x] Define deterministic host fixtures, later target qualification cases,
   compatibility measurements, implementation risks, and small implementation
   phases with review and acceptance gates.
8. [x] Audit the package against this plan, validate generated artifacts, update
   the task and current development log, and stop at Review Gate 1 for Author
   review without committing.

### Explicit exclusions for this pass

- No production firmware or vendored upstream source is added or modified.
- No network/browser, MIPI-DSI, or other physical output sink is implemented.
- No EDU/VDU routing, MOS integration, or SETUP-005 operating-mode decision is
  selected or implemented.
- No audio, input, networking, storage, updater, or board-wiring scope is
  absorbed into PORT-003.
- No successful firmware build, hardware behavior, timing, throughput, or
  pixel-fidelity claim is made without the corresponding evidence.
- No new external protocol, artifact version, hardware revision, or qualified
  baseline is silently assigned.

## Review Gate 1 stop condition

This gate was satisfied and accepted on 2026-08-22. The Author delegated
technical review to the Agent, authorized the Agent to commit and push the
package without personal diff review, and authorized Phase A to proceed under
a detailed stepwise plan without another pre-start review.

## Review Gate 1 decision register

All entries were accepted by delegated approval on 2026-08-22. The reviewed
recommendations and alternatives are detailed in
[`PORT-003/PROPOSAL.md`](PORT-003/PROPOSAL.md#decisions-accepted-at-review-gate-1).

| ID | State | Decision requested |
|---|---|---|
| `PORT-003-D001` | Accepted | One project-owned generic bitmapped controller with configured native codecs. |
| `PORT-003-D002` | Accepted | Preserve upstream packed native formats for the initial compatible backend. |
| `PORT-003-D003` | Accepted | Advance logical frames from sink-independent `esp_timer` cadence. |
| `PORT-003-D004` | Accepted | Adopt the proposed tick, swap, completion, and overrun model, subject to fixtures. |
| `PORT-003-D005` | Accepted | Use one central Copper and hardware-overlay presentation compositor. |
| `PORT-003-D006` | Accepted | Use latest-generation non-blocking frame consumers; slow sinks may drop generations. |
| `PORT-003-D007` | Accepted | Adopt the phased implementation and qualification plan. |

## Review Gate 1 execution record

### 1–2. Scope and bounded authority

The task-local package structure and explicit exclusions were frozen before
analysis. Research remained bounded to official Agon display documentation,
official VDP tag `v2.16.0` at
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, its pinned vdp-gl
`all-the-plots`, accepted display decisions, the canonical dependency graph,
and the pinned P4 framework headers. No firmware, vendored source, output sink,
or operating-mode policy was changed.

### 3. Deterministic evidence

[`PORT-003/generated/display-evidence.yaml`](PORT-003/generated/display-evidence.yaml)
projects six reviewed Work 1.d candidates, 31 direct files, 1,990 symbols, 33
abstract controller declarations, 478 classified old-architecture hits, 164
bounded related files, and five fingerprinted P4 platform headers. Compact
mode and controller slices are generated from the canonical graph. Two complete
pipeline passes were byte-identical and all graph/evidence validators passed.

Gotchas found while constructing the generator:

- a selection record can legitimately belong to more than one survey
  candidate; treating candidate membership as one-to-one lost the shared
  `fabgl.h` role;
- the first controller slice omitted `defines` and `includes`, producing a
  technically valid but useless one-node view; the relation set now preserves
  the controller's actual consumers; and
- the first validator used shorthand candidate names instead of durable graph
  IDs and correctly stopped the pipeline until fixed.

### 4. Retained behavior and physical exclusions

[`PORT-003/display-behavior.md`](PORT-003/display-behavior.md) traces mode
fallback, Canvas/primitive execution, the abstract backend, native pixels,
palette/Copper, software versus hardware sprites, readback, frame counter, and
callbacks. It separately classifies the classic GPIO/I2S/DMA/VSYNC engine and
the narrower architecture adaptations. Notable hidden couplings are the
official context's direct read/write of the concrete controller frame counter,
palette helpers that downcast to `VGAPalettedController`, and the input path's
`VGABaseController *` mouse-positioner type.

### 5. P4 feasibility

[`PORT-003/platform-feasibility.md`](PORT-003/platform-feasibility.md) records
the pinned capability heap, cache synchronization, periodic timer, RGB panel,
and MIPI-DSI declarations. These facilities support the proposed boundary at
header level. No disposable compile probe was needed because Review Gate 1
does not yet contain a concrete API call whose signature or linker selection
needed proving. No compile, throughput, cadence, or hardware claim was made.

### 6–7. Proposal and qualification

[`PORT-003/PROPOSAL.md`](PORT-003/PROPOSAL.md) proposes one project-owned
generic bitmapped controller, preserved native codecs, a sink-independent
logical frame service, central presentation composition, and non-blocking
latest-generation consumers. The seven material choices were accepted by
delegated approval and are recorded in ADR-0015.

[`PORT-003/qualification-plan.md`](PORT-003/qualification-plan.md) defines
deterministic oracle provenance, host and target fixture families, seven
implementation phases with review gates, and explicit stop/rollback rules.
It keeps physical sink implementation in separately owned work while requiring
all sinks to prove they cannot redefine logical VDP behavior.

### 8. Audit and stop gate

The final task-local pipeline regenerated twice byte-for-byte, validated both
canonical graph slices, and passed all PORT-003 evidence invariants. The ten
permanent dependency-tool tests passed. New Python sources compiled from text,
all local Markdown links resolved, no absolute machine path entered the tracked
package, `git diff --check` passed, and both generated SVGs contain explicit
white backgrounds. The worktree contains only TODO/task/development records,
task-local analysis machinery, generated evidence, and Review Gate 1 design
documents. Production firmware and vendored upstream trees remain untouched.

### Author approval

On 2026-08-22 the Author explicitly approved this work without performing a
personal review, authorized the Agent to commit and push it, and authorized
continuation into the next implementation gate without another review. The
same scope-control stipulation applies to that continuation: write a detailed
task list first and refer to it step by step to prevent drift.

## Phase A — Contract canary

- Status: Complete — Gate A passed
- Started: 2026-08-22 11:54 EDT
- Finished: 2026-08-22 12:38 EDT

Phase A is the next gate authorized by the Author. Its sole purpose is to prove
that the retained vdp-gl Canvas/common-renderer contract and one project-owned
concrete P4 controller type can enter the pinned P4 build without linking the
excluded classic VGA physical engine. It is not a functional renderer.

### Detailed execution checklist

Check this list before each action. Record outcomes and deviations against the
same item; do not substitute later-phase work merely because a nearby source
file is visible.

1. [x] Freeze the exact import, build, evidence, and stop boundaries under
   `PORT-003/phase-a/`. Use only the accepted official VDP `v2.16.0`, vdp-gl
   `all-the-plots`, ESP32Time `2.0.6`, and CRC `1.0.4` baselines already
   fingerprinted by the canonical dependency graph.
2. [x] Implement and validate a deterministic initial source-import process.
   Import official `video/` files unchanged into the upstream-shaped firmware
   tree while preserving `video/extender/`; import complete vdp-gl, ESP32Time,
   and CRC release contents under `vdp/vendor/`; exclude VCS administration
   only; preserve licenses, paths, bytes, and executable modes; and verify file
   counts and tree hashes before accepting the import.
3. [x] Update durable dependency presence/provenance so the canonical graph
   distinguishes repository-vendored dependencies and the imported official
   firmware from external reference trees. Regenerate deterministically and
   require zero source-identity or selection drift caused merely by relocation.
4. [x] Define a dedicated `p4-display-contract-canary` build environment and
   machine-readable source list. Compile only the canary, project-owned display
   skeleton, and the smallest evidenced retained vdp-gl closure. Keep the
   ordinary P4 environment separate and prevent PlatformIO from auto-building
   the vendored library's broad classic-ESP32 source set.
5. [x] Add a prominently marked contract-only P4 controller derived from
   `fabgl::GenericBitmappedDisplayController`. Make every required virtual
   method concrete, preserve an official-facade-shaped ownership/factory seam,
   and add compile-time assertions for integer widths, RGB/pixel values,
   native-format enumerators, and base-class relationships. Unimplemented
   drawing methods must fail visibly if called; they must not masquerade as a
   functioning display.
6. [x] Run bounded diagnostic compile iterations with the pinned PlatformIO
   environment. For every failure, classify the responsible source and cause
   before changing anything. Permit only retained Canvas/common-renderer
   dependencies and narrow P4 architecture adaptations required by this
   contract canary; record gotchas and inherited upstream assumptions beside
   the affected code and in Phase A evidence.
7. [x] Prove the resulting ELF/build graph contains the canary controller,
   Canvas, and common bitmapped-controller implementation while excluding all
   classic VGA concrete, VGA text, CVBS, Scene, physical PS/2, audio-output,
   network, and storage translation units. Record compiled sources, unresolved
   or discarded symbols, map evidence, and the exact non-qualification build
   invocation.
8. [x] Update the dependency graph, source-selection projection,
   compatibility delta, task record, and development log with the implemented
   seam and observed build closure. Do not turn diagnostic compilation into a
   hardware, rendering, timing, or compatibility claim.
9. [x] Run deterministic regeneration, dependency tests, task-local tests,
   clean-room rebuild, source-import verification, link-exclusion checks,
   Markdown/link/whitespace checks, and `git diff --check`. Stop at Gate A only
   if all criteria below are satisfied; otherwise stop at the first declared
   blocker with the evidence preserved.

### Phase A execution record

#### 1–3. Boundary, import, and provenance

The task-local Phase A package froze the gate before import or compilation.
`import-baselines.py` copied only immutable reviewed release bytes and modes,
preserved the official `video/` layout around the existing `video/extender/`
namespace, and refuses unexplained dependency files. Its steady-state verifier
proves 5,164 files across the four accepted baselines, matching all file counts
and tree hashes with zero local vendored modifications.

Managed-import mappings now make `vendored` a mechanically verified repository
fact. Every canonical upstream file node carries its upstream-relative path and
repository-managed path. Regeneration changed presence from external reference
to vendored without changing any source identity, release, commit, tree hash,
manifest count, or declared selection.

#### 4–5. Exact build and type boundary

`p4-display-contract-canary` uses a tracked five-translation-unit allowlist:
three project units plus upstream `canvas.cpp` and `displaycontroller.cpp`.
Because the Arduino/ESP-IDF hybrid ignores PlatformIO `build_src_filter`, the
pre-build hook deterministically renders an ignored component `CMakeLists.txt`
from the same list and adds only the two reviewed vendored units.

`P4DisplayControllerContractCanary` is a concrete
`GenericBitmappedDisplayController` with an official-facade-shaped factory.
Static assertions cover integer widths, `RGB888`, native-format enumerators,
inheritance, and base-pointer ownership. Lifecycle setup is bounded to a 1×1
contract shape. Every drawing, readback, bitmap, glyph, scroll, and swap method
fails visibly. A volatile-false probe retains the common primitive executor for
ELF evidence without executing it.

#### 6. Bounded compile iterations and gotchas

Each failure was classified before correction:

- PlatformIO's global Arduino package name had been left at upstream control
  build version 2.0.14, while pioarduino 55.03.311 requires core 3.3.11. The P4
  environment now pins the constituent 3.3.11 package so whichever build ran
  last cannot silently break the other.
- The hybrid framework ignored `build_src_filter` and initially compiled
  official `video.ino`, reaching excluded sound code and the missing classic
  `soc/sens_struct.h`. The generated component source list is the required
  hybrid build boundary; no official source was patched.
- A force-included C++ compatibility header was also injected into framework C
  units. Architecture helpers are now guarded by both RISC-V and C++ so the
  canary does not impose C++ standard headers on C compilation.
- vdp-gl's common headers include the removed classic ESP32 FRC timer register
  header even though this closure does not use that timer. The project shim is
  parse-only and aborts if an accidental runtime access occurs.
- Common vdp-gl code assumes Xtensa coprocessor helpers. The RISC-V canary
  supplies compile-only no-ops, prominently marked for replacement or reviewed
  runtime policy before transformed bitmap qualification.
- Excluding broad `fabutils.cpp` exposed a narrow utility link closure. Exact
  upstream implementations for timeout conversion, line clipping, rectangle
  merge/intersection, and `LightMemoryPool` were copied into one provenance-rich
  project port unit. No vendored file was edited.
- The first evidence pass found `execPrimitive()` discarded by section garbage
  collection. The guarded project probe made the gate's requirement real rather
  than weakening the validator.
- Official VDP and dependency releases retain upstream CRLF/tab/trailing-
  whitespace bytes, so an unqualified whitespace check initially reported the
  immutable imports. A root `.gitattributes` disables only those inherited
  checks under official `video/` and `vdp/vendor/` paths while restoring Git's
  normal strict set under `video/extender/`; no imported byte was normalized.
- The standard `*.map` build-output ignore also matched legitimate vdp-gl
  Doxygen `.map` release files. A vendor-root exception now makes reviewed
  `vdp/vendor/` imports byte-complete, and the importer can require every mapped
  release path in the staged Git index at commit gates.
- PlatformIO prints the board metadata's generic `400MHz` banner. The accepted
  pre-v3 configuration remains explicitly 360 MHz in `sdkconfig.defaults`; the
  banner is not runtime or configuration evidence.

#### 7–8. Closure proof and durable model

The resulting diagnostic ELF is approximately 536 KiB and is not a versioned
or qualified firmware artifact. Machine evidence proves exactly five VDP
application objects, all six required project/common-renderer symbol claims,
and no unexpected application objects. It reports no classic VGA, CVBS, Scene,
physical PS/2, sound generator, file browser, or other excluded VDP symbols.
Only normal framework start symbols remain undefined in the final ELF view.

The canonical graph now records three observed Extender build units for the
canary, concrete controller skeleton, and narrow utility port, with confirmed
dependencies on the retained upstream files/types. The source-selection guide
lists these project boundaries separately so they cannot be confused with the
immutable upstream file-selection profile. The compatibility delta explicitly
limits this gate to type, compile, and link evidence.

#### 9. Gate A validation

The immutable import verifier passed at steady state with 5,164 matching files
and zero writes. A true clean removed the complete canary environment and the
pinned hybrid build recreated it successfully in 70 seconds. The final image
is 536,596 bytes; reported application usage is 30,780 of 512,000 RAM bytes and
535,808 of 7,340,032 flash bytes. These are diagnostic linker reports, not
runtime capacity or performance qualification.

The Phase A validator regenerated twice byte-identically and proved five
application objects, six required ELF symbol claims, and zero excluded VDP
source or symbol families. The complete dependency pipeline and PORT-003
evidence pipeline each regenerated twice byte-identically. Full graph schema,
referential, source-file, tree, and source-span verification passed. All six
PORT-002 boundary proofs passed, as did 12 dependency-tool tests, three Phase A
tests, and version-record validation. Changed Markdown local links, explicit
white SVG backgrounds, project-owned whitespace, and `git diff --check` passed.

No source-import bytes changed, no vendored source was edited, no firmware was
flashed, no hardware was exercised, and no artifact identity was assigned.
Gate A therefore satisfies all acceptance criteria without triggering a stop
condition.

### Phase A explicit exclusions

- No framebuffer allocation, pixel drawing, readback result, palette, Copper,
  sprite composition, frame clock, queue executor, buffer swap, or output
  consumer is implemented.
- No network/browser, RGB, MIPI-DSI, HDMI, audio, input, storage, update,
  transport, EDU/VDU routing, MOS, or operating-mode implementation is added.
- The complete official `video/` source may be imported unchanged, but the
  canary build does not attempt to compile or link the complete official
  firmware. Full facade integration remains Phase E.
- No classic VGA source is patched into compiling on P4, stubbed, or linked.
- No vendored upstream file is locally edited. A required upstream adaptation
  must be isolated in project-owned code or recorded as a stop condition.
- No firmware is flashed or deployed. This is a compile/link diagnostic, not a
  qualified artifact or test run; it may use the existing unidentified
  experimental developer-build identity and must not assign a new version or
  revision without Author approval.

### Gate A acceptance criteria

1. Imported files reproduce all four accepted source baselines exactly at the
   declared managed paths, with complete provenance and licenses.
2. A clean pinned P4 diagnostic build produces an ELF containing Canvas,
   common `BitmappedDisplayController`, and the concrete project canary type.
3. The source and link manifests prove that none of the excluded physical
   implementations entered the build.
4. The skeleton cannot be mistaken for working display firmware: drawing and
   readback entry points fail visibly, and no sink or frame service exists.
5. The dependency/source-selection model represents the imported, selected,
   excluded, and project-owned boundaries without unresolved records or
   unexplained observed-versus-declared drift.
6. All deterministic generators and tests pass from the frozen baseline, and
   all implementation gotchas and deviations are recorded with provenance.

### Phase A stop conditions

Stop without broadening scope if the gate requires editing a vendored file,
linking an excluded physical driver, implementing a real renderer or another
subsystem, selecting an output sink, assigning an unapproved artifact identity,
or making an unresolved SETUP-005 operating-mode choice. Also stop if imported
bytes do not match the accepted baselines or if the minimum retained closure
cannot be separated from an excluded subsystem without a new architectural
decision.

## Phase B — Native storage and synchronous renderer

- Status: Complete — Gate B passed
- Started: 2026-08-22 12:43 EDT
- Finished: 2026-08-22 13:47 EDT

The Author authorized continuation without an intermediate review after Phase
A passed and was pushed. This checklist is therefore the controlling review
surrogate: consult it before every action, update results against the same item,
and stop rather than silently expanding the gate.

Phase B implements authoritative logical pixel storage and the retained common
renderer in a deliberately synchronous, sink-free configuration. It does not
add logical frame time, background execution, palette/Copper composition,
official mode-facade integration, or output delivery.

### Detailed execution checklist

1. [x] Freeze the Phase B package structure, exact source/test/evidence
   boundaries, accepted inputs, oracle hierarchy, and stop rules under
   `PORT-003/phase-b/`. Define a machine-readable implementation manifest so
   project source, adapted upstream algorithms, host fixtures, and target build
   units cannot drift apart.
2. [x] Generate a bounded provenance inventory for native formats, storage,
   allocation, pixel access, raw bitmap operations, copies, scrolls, drawing
   primitives, and readback. Fingerprint the exact vdp-gl `all-the-plots`
   declarations and old concrete-controller spans; classify each algorithm as
   reusable unchanged, adapted with provenance, replaced by project logic, or
    deferred outside Phase B. Do not manually transcribe an untraceable list.
3. [x] Define project-owned contracts before implementing behavior:
   - one logical mode descriptor for explicit dimensions, native format, and
     single/double buffering, without importing the official mode table;
   - depth-specific native pixel codecs preserving `PALETTE2`, `PALETTE4`,
     `PALETTE8`, `PALETTE16`, and logical `SBGR2222` contracts;
   - transactional plane ownership with injected allocation/failure and
     deterministic zero initialization;
   - drawing versus visible plane selection and native-save/readback rules;
   - a synchronous controller lifecycle with background execution disabled;
     and
   - explicit result/error contracts that leave the old valid mode installed
     after any failed reconfiguration.
4. [x] Build independent deterministic test machinery before trusting the
   implementation:
   - pure host reference codecs and pixel matrices that do not call production
     codec methods;
   - canonical fixtures carrying source tag/profile, dimensions, depth,
     buffering, seeded command sequence, expected native bytes/readback/pixels,
     oracle class, generator identity, and content hash;
   - a host C++ harness for project codec/storage code and, if feasible without
     broad subsystem stubs, the actual retained Canvas/common renderer;
   - injected allocator failures at every allocation boundary; and
   - deterministic regeneration/validation that rejects implementation-derived
     goldens and stale provenance.
5. [x] Implement and qualify the five native codecs and transactional plane
   storage independently of Canvas. Exhaustively cover every legal pixel value,
   packed-byte boundary, odd width, row stride, clipping edge, clear pattern,
   single/double-plane identity, reconfiguration, release, and allocation
   failure. Preserve RGB222 logical bits; synthesize legacy native-save sync
   bits only where the proven upstream contract requires them.
6. [x] Replace the contract canary with a Phase B synchronous controller while
   preserving the accepted factory/base-pointer shape. Implement direct pixel,
   line, row, clear, scroll, copy, glyph, ellipse/arc/sector, flood-fill,
   bitmap, transformed-bitmap, native-save, and logical readback entry points
   through the retained common renderer and project codecs. Port only the
   smallest old-controller algorithms demonstrated useful by item 2, keep exact
   provenance inline, and make every still-deferred path fail visibly.
7. [x] Run the complete native/primitives fixture matrix for all five depths,
   relevant paint modes, clipping/origins, overlapping copies, edge
   coordinates, bitmap formats/transforms, and single/double storage. Separate
   independent host-model expectations, official captures, and reviewed
   source-derived expectations in the evidence. A compile or self-comparison is
   not a passing fixture.
8. [x] Define a dedicated Phase B P4 diagnostic environment from the same
   machine source manifest. Compile and link only the synchronous renderer,
   retained common closure, and narrow project adaptations. Prove classic VGA,
   CVBS, Scene, physical PS/2, audio, network, storage, official facade, frame
   service, and output-consumer units remain absent. Do not deploy this build.
9. [x] Update the canonical dependency graph, source-selection projection,
   compatibility delta, task execution record, and development log with the
   observed storage/renderer boundary and exact adapted-source provenance.
   Distinguish host qualification, target compile evidence, and behavior still
   awaiting physical P4 qualification.
10. [x] Run a clean Phase B host and P4 build; complete fixture and allocation-
    failure matrices; import/index verification; graph and task evidence
    regeneration twice byte-identically; schema/source-span validation; all
    permanent tests; local-link, absolute-path, SVG-background, whitespace, and
    `git diff --check` audits. Commit and push only if every Gate B criterion
    passes and no stop condition requires a new Author decision.

### Phase B execution record

1. Package and authority freeze — complete:
   - `phase-b/README.md` defines the bounded task-local layout and Gate B
     boundary;
   - `phase-b/implementation-manifest.yaml` fixes production, host-test,
     fixture, evidence, target-build, and excluded-unit roles before behavior
     implementation; and
   - independent expectations outrank implementation output, which is
     explicitly forbidden from generating its own goldens.
2. Algorithm provenance — complete:
   - the deterministic extractor consumed the pinned SETUP-003 Universal Ctags
     index and immutable vendored `vdp-gl` tree;
   - 863 definitions/declarations in 17 files carry exact file and inclusive
     source-span SHA-256 fingerprints, with anonymous lambdas covered by their
     owning callable rather than promoted to false API boundaries;
   - the inventory distinguishes 199 retained common records, 407 adapted
     depth/native records, 67 platform replacements, 35 Phase C deferrals, 90
     Phase D deferrals, and 65 classic-physical exclusions; and
   - thirteen permanent provenance tests verify lexical span handling, tuple uniqueness,
     all fingerprints, all five native algorithm families, critical boundary
     classifications, and byte-identical regeneration.

3–5. Contracts, independent oracles, codecs, and storage — complete:
   - `phase-b/contracts.md` freezes the five native formats, row/plane sizing,
     typed failures, transactional replacement, single/double identity,
     native-save rules, and synchronous lifecycle before implementation;
   - 139 generated codec cases cover every legal value, nine boundary widths,
     odd rows, all clear values, and all SBGR sync combinations;
   - pure codec/storage tests run under ASan/UBSan and explicit allocation
     accounting, including first- and second-plane failures, old-state
     preservation, successful replacement, move ownership, idempotent release,
     and validation/overflow failures; and
   - the independent oracle's first `PALETTE8` draft exposed that three-bit
     pixels cross arbitrary byte boundaries. It was corrected to a bit-by-bit
     MSB-first model before production output was accepted.

6–7. Synchronous retained renderer — complete:
   - the Phase A abort-only canary is replaced by `P4DisplayController`, backed
     by `NativePixelCodec` and `PlaneStorage`, with no frame service or sink;
   - a bounded host compatibility layer permits the actual unchanged Canvas
     and common controller units to execute without emulating an unrelated
     ESP32 subsystem;
   - 115 primitive fixtures—23 scenarios at each depth—cover paint modes,
     clipping/origin, lines/rows/rectangles, copies, scrolling, clear, glyph,
     flood fill, ellipse/arc/segment/sector, mask/native/RGBA bitmaps, identity
     transforms, readback, native-save output, and double-plane identity; and
   - all 254 codec/renderer fixtures pass with zero mismatch under ASan/UBSan.
     LeakSanitizer cannot inspect processes under the managed tracing boundary,
     so it is disabled while the storage harness independently rejects leaks,
     unknown frees, and double frees.

   The retained narrow-glyph fast path reads a four-byte window from each
   byte-stride row. The fixture supplies three safe trailing bytes and records
   this inherited data contract rather than patching vendored code. The host
   Xtensa wrappers are inert only around normally executed host floating-point
   transforms; target wrappers remain the reviewed RISC-V compatibility seam.

8. P4 diagnostic closure — complete:
   - `p4-display-renderer` compiles five project units plus unchanged vendored
     `canvas.cpp` and `displaycontroller.cpp`;
   - initial links exposed only four pure geometry/bit helpers from broad
     `fabutils.cpp`; those exact source-pinned routines were added to the
     existing narrow port and the next build linked successfully; and
   - the resulting ESP32-P4 image reports 586,082 bytes of flash use. Machine
     evidence proves all seven selected objects and six required ELF symbols,
     with zero classic VGA/CVBS/Scene/PS2/audio/network/storage units or symbol
     families. This remains compile/link evidence; nothing was deployed.

9. Durable integration records — complete:
   - the canonical dependency graph now represents the five current
     project-owned Phase B units and observed seven-unit closure rather than
     stale Phase A canary nodes;
   - source-selection projections and the VDU 22 proof slice regenerated twice
     byte-identically across all 5,164 vendored files; and
   - `phase-b/compatibility-delta.md` separates retained behavior, project
     adaptations, host-only harness seams, and later-phase work.

10. Gate B audit — complete:
    - a clean P4 diagnostic rebuild produced an ELF whose validator proved all
      seven selected units, six required symbols, and zero excluded source or
      symbol families; nothing was deployed;
    - the immutable import verifier matched all 5,164 baseline files and wrote
      zero files;
    - 139 codec and 115 renderer fixtures passed again, including every
      allocation-failure boundary, and all seven Phase B generated artifacts
      were byte-identical across independent output passes;
    - the final clean-build evidence was incorporated into two byte-identical
      canonical graph regenerations, after which full file/source-span
      validation passed; and
    - 17 Phase B, three Phase A, and 12 dependency-tool tests passed together
      with version-record, changed-link, absolute-path, Python syntax,
      SVG-background, whitespace, and `git diff --check` audits.

Gate B passed under the Author's explicit authorization to check in and push
this work without personal review. The next phase still requires its own
detailed written plan before implementation begins.

### Phase B explicit exclusions

- No periodic timer, frame-service task, background primitive queue execution,
  frame counter, background completion behavior, logical swap-at-frame-edge, or consumer
  notification. Those begin in Phase C.
- No palette mutation/quantization service, Copper signal-list compositor,
  hardware sprite/cursor presentation overlay, or sink output format. Those
  begin in Phase D or later.
- No edits to official `agon_screen.h`, official mode table/fallback, VDU
  dispatch, contexts, Teletext, callbacks, MOS, or EDU/VDU operating modes.
  Official integration remains Phase E.
- No network/browser, RGB, MIPI-DSI, HDMI, audio, input, storage, updater, or
  transport implementation; no classic physical driver or compatibility stub.
- No vendored source edit, physical deployment, runtime P4 qualification, or
  new firmware/version/build identity.

### Gate B acceptance criteria

1. Every codec round-trips all legal values and matches independent native-byte
   goldens across packed boundaries and odd dimensions.
2. Transactional single/double-plane allocation, initialization,
   reconfiguration, release, and every injected failure leave a valid,
   leak-free controller state in host evidence.
3. Retained common primitives and all Phase B raw/readback operations match
   independent deterministic goldens at every native depth; any intentionally
   deferred method remains visibly unavailable and is outside the claimed
   matrix.
4. The synchronous controller never depends on a frame clock, sink, classic
   VGA physical engine, or another excluded subsystem.
5. A clean pinned P4 diagnostic build proves the selected application/link
   closure without vendored edits, deployment, or runtime claims.
6. Provenance, dependency selection, compatibility delta, generators, and tests
   are deterministic, complete, and free of unexplained declared-versus-
   observed drift.

### Phase B stop conditions

Stop for review if faithful native storage or renderer behavior requires
changing an accepted pixel contract, retaining a classic physical controller,
editing vendored source, implementing a frame service/sink/official facade,
making a SETUP-005 mode decision, or inventing compatibility behavior without
an independent oracle. Also stop if the actual common renderer cannot be host-
tested without broad unrelated subsystem emulation, if target allocation
constraints invalidate the accepted storage architecture, or if a material
primitive/readback difference cannot be isolated and measured.

## Phase C — Logical frame service

- Status: Complete — Gate C passed
- Started: 2026-08-22 13:49 EDT
- Finished: 2026-08-22 21:17 EDT

The Author explicitly authorized this phase to proceed, including check-in,
without personal review after Gate B passed. This checklist is the controlling
review surrogate. Consult it before every action, record results against the
same item, and stop rather than expanding logical frame service into palette,
official-facade, sink, transport, or operating-mode work.

Phase C adds sink-independent logical time and bounded asynchronous work to the
qualified Phase B renderer. It owns timer notification, frame-service task
execution through unchanged common queue semantics, logical buffer swaps,
the writable compatibility frame counter, provisional latest-generation
publication, and null/slow mock consumers. It does not compose presentation
pixels or implement a physical consumer.

On 2026-08-22 the Author ordered the corrective action recorded by
`CA-2026-08-22-001`. The strict candidate must retain upstream queue-depth
waiting, swap notification, background draining, dynamic payload, and
one-tick/one-edge behavior. The rejected stronger completion candidate remains
in commit `8aecb0e` and is promoted to the independent `UPSTREAM-001` A/B task.

### Detailed execution checklist

1. [x] Freeze this detailed scope, package/evidence layout, authority, oracle
   order, physical-qualification preconditions, and stop rules before changing
   production code. Record the Author's no-review authorization and keep the
   accepted ADR-0015 lifecycle ordering normative.
2. [x] Generate a bounded, deterministic Phase C provenance inventory from the
   existing symbol/source graph. Fingerprint the exact upstream queue,
   background primitive, swap, frame-counter, wait, callback, and teardown
   spans. Classify behavior separately from the old VSYNC ISR, I2S/DMA engine,
   Xtensa synchronization, and physical timing source; do not compile or copy
   the latter merely because they share a file.
3. [x] Define contracts before implementation for:
   - unchanged upstream queue-depth waits, swap notification, background
     draining, dynamic payload lifetime, and mode teardown;
   - single-buffer frame waits and double-buffer drawing/visible-plane swaps;
   - writable modulo-2^32 compatibility frame count and independent monotonic
     publication generation;
   - one-logical-edge-per-recorded-tick accounting and backlog handling;
   - a short timer-notification boundary and one frame-service owner;
   - bounded latest-generation consumer notification, drop accounting, and
     lease/pointer lifetime; and
   - transactional startup/reconfiguration/stop around the retained upstream
     lifecycle and last valid renderer state.
4. [x] Build an independent deterministic host model and trace fixtures before
   trusting production scheduling code. Cover exact event order, upstream
   queue-depth wait behavior, dynamic payload lifetime, single-buffer
   next-edge waits, double-buffer swap visibility, frame-count writes and
   rollover, generation publication, null/slow/disconnecting consumers,
   accumulated ticks as distinct edges, teardown draining, and bounded memory.
   Expected traces must come from the written contract or reviewed upstream
   behavior, never production output.
5. [x] Extend Phase B storage/controller seams only as required by those
   contracts. Add transactional drawing/visible-plane exchange and explicit
   logical frame-counter access without importing palette/Copper/overlay or
   official `agon_screen.h` behavior. Preserve synchronous execution as a
   selectable test/lifecycle state and make invalid direct swap paths fail
   visibly.
6. [x] Implement a platform-neutral logical frame state machine plus the
   narrowest ESP32-P4 adapter: `esp_timer` callback records elapsed ticks and
   wakes one FreeRTOS frame-service task; only that task runs frame-boundary
   work. Timer and sink callbacks must never render, swap planes, or publish
   mutable storage.
7. [x] Integrate retained Canvas/common background primitive execution without
   modifying it. Preserve queue-depth waiting—including its already-dequeued
   behavior—ordinary single-buffer FIFO work, immediate double-buffer drawing,
   immediate post-swap submitter notification, upstream stop draining, dynamic
   payload cleanup, and trailing single-buffer `Refresh` behavior.
8. [x] Add a provisional sink-neutral publication contract and null, fast,
   slow, disconnecting, and reconnecting mock consumers. Notifications must be
   latest-state and bounded; consumers may record drops but cannot block the
   frame service, retain mutable logical storage indefinitely, alter frame
   count, or create an unbounded queue. Interface freeze remains Phase F.
9. [x] Run deterministic host concurrency/stress qualification under
   sanitizers and explicit allocation/thread accounting. Exercise adversarial
   interleavings, rollover, repeated start/stop/reconfigure, forced tick bursts,
   slow consumers, upstream lifecycle draining, and long bounded runs; reject
   deadlock, stale-plane access, leaks, or growth with elapsed
   frames.
10. [x] Add a dedicated Phase C P4 diagnostic/qualification environment and
    prove the exact compile/link closure without deployment. Update the
    dependency graph, source-selection projection, compatibility delta, task
    record, and development log. Once host and clean target gates pass, create
    and push a pre-qualification checkpoint and assign the human-readable
    firmware/build/test identities required by `docs/versions/README.md`.
11. [x] Before physical work, reread `HARDWARE.local.md`, verify the named Pi,
    P4 identity, connection, toolchain, and safety boundary, then deploy only
    the committed qualification artifact. No backup of the pre-existing P4
    firmware is required. Measure sink-free cadence, jitter, drift, rollover
    seam, accumulated-tick backlog, null/slow consumers, teardown,
    and memory bounds at the accepted 360 MHz configuration; preserve serial
    capture and structured run evidence. Stop on identity mismatch, unstable
    power/transport, unexplained reset, or a result requiring contract change.
12. [x] Regenerate all Phase C and canonical graph artifacts twice
    byte-identically; verify immutable imports and index, schemas/source spans,
    host and target evidence, all permanent tests, links, absolute paths, SVG
    backgrounds, whitespace, and staged diff. Mark Gate C complete and commit
    and push the final evidence only if every criterion below passes.

### Gate C closure record

Gate C passed on 2026-08-22. The Phase C lifecycle, independent traces, host
results, target closure, canonical dependency graph, and PORT-003 projections
all regenerated twice byte-identically. The exhaustive source validator
matched all 5,164 immutable imported files and every recorded source span;
index verification found no omitted import.

The final suites passed 13 dependency-tool, three Phase A, 17 Phase B, and 11
Phase C permanent tests, plus 12 ASan/UBSan logical-frame traces, five retained
controller cases, three stress cases, and the nine-unit/eight-symbol/zero-
exclusion P4 closure. Run `PORT-003-2026-08-22-23-58-56Z` supplies the passing
target evidence, and its generated index binds the authoritative manifest by
SHA-256.

The audit found and corrected one generator-order issue: regenerating target
closure after the canonical graph left the graph's input fingerprint stale.
The enforced closure order is now Phase C evidence, canonical dependencies,
then PORT-003 projections. Current Markdown links pass outside intentionally
verbatim legacy-evidence excerpts; local identity/path leakage, SVG white
backgrounds, evidence hashes/sizes, schemas, whitespace, and the complete diff
also pass.

### Phase C explicit exclusions

- No palette mutation, Copper lists, presentation composition, hardware
  sprites/cursors, or output pixel format; those remain Phase D.
- No official mode table/fallback, `agon_screen.h`, contexts, callbacks,
  Teletext, VDU dispatch, MOS, or EDU/VDU operating-mode integration; those
  remain Phase E or SETUP-005.
- No browser/network, RGB, MIPI-DSI, HDMI, audio, input, storage, updater, or
  transport implementation and no classic VGA/CVBS physical engine.
- No frame consumer API freeze, production sink, or claim that host scheduling
  proves target cadence. Phase F owns final consumer handoff.
- No vendored lifecycle source edit is permitted. No uncommitted or
  unidentified firmware may be used for a qualified physical run.

### Phase C decision register

| ID | State | Decision requested |
|---|---|---|
| `PORT-003-D008` | Superseded | The proposed vdp-gl lifecycle patch is excluded from the strict-compatible product baseline and preserved under `UPSTREAM-001`. |
| `PORT-003-D009` | Accepted | Retain upstream common queue, completion-wait, swap-notification, background-lifecycle, and payload behavior unchanged; replace only the unavailable physical executor. |

`PORT-003-D008` was accepted on 2026-08-22 because the retained common methods
are non-virtual and their queue state is private. Corrective review established
that the proposed hooks were being used to improve inherited completion and
notification semantics even though the P4 can execute the common queue code as
written. The Author therefore superseded D008 with D009 on 2026-08-22.

D009 uses no linker interposition, queue interception, copied common
translation unit, or vendored lifecycle patch. The P4 task replaces the
unavailable physical executor through existing protected common seams while
the inherited queue-depth wait and swap notification remain authoritative.
The former correction candidate is recoverable from commit `8aecb0e` and has a
separate A/B regression path in `UPSTREAM-001`; it is not discarded or silently
represented as product compatibility.

### Original Phase C candidate record — superseded by corrective action

The following record describes commit `8aecb0e` and is retained as the exact
input to `UPSTREAM-001`. Its D008 completion, notification, coalescing, and
cancellation claims are not current product architecture.

1. Scope and plan freeze — complete:
   - the 12-item checklist, package boundary, gate criteria, explicit
     exclusions, physical-run checkpoint, and stop conditions were written
     before production changes; and
   - the Author's explicit no-review authorization is recorded while material
     stop conditions remain binding.

2. Frame-lifecycle provenance — complete:
   - `phase-c/scripts/extract-frame-lifecycle.py` deterministically fingerprints
     33 callable/source-region records across 13 pinned official files;
   - the records distinguish six retained common contracts, six official
     facade contracts, ten common sequence adaptations, one logical swap,
     three platform-task replacements, and seven physical-trigger exclusions;
   - four permanent tests verify tuple uniqueness, every file/span hash,
     critical dispositions, and the queue-race/override findings, and a second
     generation was byte-identical; and
   - the trace proves old frame edges increment `frameCounter` before waking or
     executing bounded work, swaps change visible identity before notifying,
     and `primitivesExecutionWait()` observes only queued count. Because a
     dequeued primitive is absent while still executing, the latter is not a
     valid completion proof.

3. Contracts — complete:
   - `phase-c/contracts.md` freezes execution ownership, elapsed-tick and
     overrun accounting, 32-bit writable frame count, 64-bit publication
     generation, FIFO sequence completion, single/double-buffer behavior,
     transactional lifecycle, and bounded metadata-only mock consumers; and
   - the contract identifies the exact private/non-virtual common-code boundary
     that cannot be completed solely in the existing P4 subclass; and
   - the Author accepted `PORT-003-D008`: a minimal annotated common-code patch
     with default-no-op lifecycle hooks and virtual completion waiting, leaving
     stock behavior unchanged for every non-P4 controller.

4. Independent event traces — complete:
   - `phase-c/scripts/generate-frame-traces.py` is a pure written-contract model
     that imports no production frame-service code or output;
   - 12 fixtures cover sink-free and coalesced ticks, frame-counter writes and
     rollover, dequeued-but-incomplete work, FIFO budgets, single-buffer Flush,
     double-buffer immediate drawing/swap, latest-only slow consumers,
     disconnect/reconnect, later tick arrival, and teardown payload release;
   - expected ordering places swap visibility before publication and
     publication before completion, while a started primitive remains an
     unsatisfied wait target until execution returns; and
   - six fixture tests plus the four provenance tests pass, and independent
     regeneration is byte-identical.

5. Storage and controller seams — complete:
   - `PlaneStorage` now owns explicit drawing and visible identities and
     performs a constant-time logical exchange only in double-buffered modes;
   - `P4DisplayController` exposes the Phase C frame descriptor and writable
     compatibility counter while rejecting reconfiguration during an active
     frame lifecycle; and
   - the synchronous Phase B lifecycle remains available after stop. An
     inherited upstream disable-ordering quirk queues one trailing `Refresh`;
     the controller prominently drains/cancels it before establishing a clean
     lifecycle sequence baseline.

6. Logical service and P4 adapter — complete:
   - `LogicalFrameService` is platform-neutral, uses a bounded eight-slot
     consumer registry and 32-bit lock-free tick accumulator, and maintains a
     separate 64-bit publication generation;
   - one service pass advances elapsed logical time, executes bounded work,
     observes any swap, publishes immutable metadata, and only then completes
     the executed sequences; and
   - `P4FrameService` confines `esp_timer` to tick recording/task wakeup. Its
     sole FreeRTOS owner task is joined before stop cancels queued payloads.

7. Retained queue integration — complete:
   - accepted seam `PORT-003-D008` adds default-no-op reservation, enqueue,
     start, completion, cancellation, notification-deferral, and virtual-wait
     hooks to the two common vdp-gl controller files;
   - P4 accounting distinguishes pre-send reservation from successful queue
     acceptance, including the narrow worker/sender handoff race, and does not
     report a dequeued primitive complete until execution and publication
     finish; and
   - teardown releases copied path/matrix payloads without executing stale
     work and wakes cancelled completion/swap waiters.

8. Provisional consumers — complete:
   - publications contain metadata only and expose no mutable framebuffer
     lease; the service writes fixed-capacity mailboxes and never invokes sink
     code;
   - null, polled, unconsumed, slow, disconnected, and reconnecting cases
     retain bounded latest-state behavior and explicit per-consumer drops; and
   - the contract remains deliberately provisional until Phase F supplies a
     real sink and freezes the handoff API.

   Pre-candidate audit rejected the first implementation even though its host
   fixtures passed: it called a nominally non-blocking virtual consumer method
   directly from the service task, so a misbehaving or merely slow sink could
   stall logical time. The replacement contains no consumer callbacks. It uses
   fixed latest-notice mailboxes whose producer lock is attempted once; busy
   or unconsumed slots report drops while the service continues. The retained
   tests were adapted to observe those production mailboxes without changing
   the independently generated expected traces.

9. Host concurrency and stress qualification — complete:
   - all 12 independent oracle fixtures pass under ASan/UBSan;
   - five retained Canvas/controller cases prove dequeued completion, double
     swaps, single-buffer edges, suspension, cancellation, restart, and
     reconfiguration behavior; and
   - three adversarial cases prove a concurrent 200,000-tick burst, saturated
     accounting across 1,000 lifecycles, and bounded consumer registration.
     LeakSanitizer is unavailable under managed tracing; Phase B allocation
     accounting continues to cover owned framebuffer allocations.

10. Target compile/link closure — complete:
    - `p4-frame-service` selects nine application translation units and links
      the retained common Canvas/controller implementation without a physical
      output sink;
    - the clean pinned target build succeeds at the qualified 360 MHz board
      profile, and machine validation proves required service symbols plus
      exclusion of classic VGA/CVBS, physical input, audio, network, and
      storage families; and
    - the dependency graph now represents vdp-gl as `vendored-patched`, permits
      only the two D008 paths to differ, records both upstream and repository
      hashes, and regenerates byte-identically.
    - the Author approved candidate identities
      `port-003-frame-service-canary-r01` and
      `p4-frame-service-qualification-r01`; registry `r06` and the committed
      qualification procedure define their exact scope.

### Corrective execution record — current candidate

On 2026-08-22 the Author approved `CA-2026-08-22-001` and superseded D008 with
D009. The corrective implementation:

1. restored `vdp-gl` `displaycontroller.h` and `displaycontroller.cpp`
   byte-for-byte to pinned `all-the-plots` and returned the complete managed
   vdp-gl import to `vendored` status;
2. removed P4 reservation/submission/start/completion sequences, virtual
   completion waiting, deferred swap notification, queued-payload cancellation,
   and the extra trailing-`Refresh` drain;
3. retained the necessary P4 physical-executor replacement through upstream's
   existing protected task-context dequeue and primitive executor;
4. changed accumulated ticks to distinct logical edges, each advancing the
   compatibility counter once, receiving one bounded renderer opportunity, and
   publishing one generation;
5. retained the Extender-owned bounded mailbox strictly after common primitive
   execution, so it changes no queue wait or swap notification; and
6. registered `UPSTREAM-001` with exact commit provenance and stock/patched A/B
   regression gates for a possible upstream contribution.

Corrected host evidence passes all 12 upstream-constrained traces, five
retained-controller cases, three stress cases, and ten Phase C provenance and
fixture tests under ASan/UBSan where applicable. A P4 diagnostic build succeeds
with nine selected application units; closure evidence proves all eight
required symbols—including the unchanged upstream wait and task-context
dequeue—and zero excluded physical families. The complete dependency pipeline
regenerates byte-identically with 5,164 pristine managed files, and all 17
Phase B provenance tests pass against the restored source.

This build is diagnostic only. The old `port-003-frame-service-canary-r01` and
`p4-frame-service-qualification-r01` identities describe the superseded D008
candidate and are rejected. The Author approved corrected candidate identities
`port-003-frame-service-canary-r02` and
`p4-frame-service-qualification-r03` in registry r09. Procedure r03 preserves
r02's firmware contract while controlling the attached `light2-harness-r01`,
`la03-p4-probe-fixture-r01`, and disconnected-Agon boundary. The coherent
candidate was committed and pushed as `ca0538a`; run
`PORT-003-2026-08-22-23-58-56Z` subsequently passed physical qualification.

### Gate C acceptance criteria

1. Host traces prove one-edge-per-tick progression, retained upstream queue
   waits and swap notification, task-context work, and publication ordering
   without implementation-derived expectations.
2. Single-buffer FIFO work and double-buffer swaps execute at a logical edge;
   drawing/visible identities and upstream payload lifetimes remain valid under
   concurrency, draining, reconfiguration, and teardown.
3. Frame count accounts for every logical tick modulo 32 bits without
   coalescing edges; publication generations remain monotonic and report
   consumer drops explicitly.
4. Null, slow, disconnected, and reconnecting mock consumers cannot block
   logical progress, grow memory without bound, or retain mutable storage past
   the defined access lifetime.
5. A clean pinned P4 build proves the selected closure, and a committed,
   versioned bench run measures accepted cadence/backlog bounds at 360 MHz with
   no physical sink, deadlock, or unexplained reset.
6. Provenance, dependency selection, compatibility delta, generators, tests,
   host evidence, and target evidence are deterministic and contain no
   unexplained declared-versus-observed drift.

### Phase C stop conditions

Stop for Author review if the phase requires changing ADR-0015 ordering,
letting a sink or timer callback own logical progress, editing vendored source
for lifecycle behavior,
adding a presentation compositor or official facade, choosing SETUP-005 mode
policy, exposing an unbounded queue or mutable indefinite frame lease, or
claiming compatibility without an independent trace oracle. Also stop if
retained Canvas queue semantics cannot be separated from the classic physical
engine by a narrow evidenced seam, if clean target compilation invalidates the
host architecture, or if physical qualification reveals a material cadence,
completion, reset, memory, or concurrency failure that cannot be isolated
without changing the accepted contract.

## Phase D — Palette, Copper, and overlays

- Status: Complete — Gate D passed
- Started: 2026-08-24 05:44 EDT
- Finished: 2026-08-24 06:42 EDT

The Author authorized this phase to proceed unattended after the returned EMOS
implementation froze Extender commit `10f2eb2`. The maintained EMOS source
commit `a8dc891` and build/qualification commit `b12fcab` are provisional
downstream references, not Phase D implementation inputs. PORT-201 and
PORT-203 evidence is required only for later claims that depend on broad EMOS
parity or physical EMOS/EDP transport; this mode-neutral presentation phase
makes neither claim.

This checklist is the controlling review surrogate. Complete one numbered
item at a time, then reread `TODO.md`, this task state, and the Phase D gate
before beginning the next item. Stop rather than silently absorbing Phase E,
Phase F, transport, output-sink, or operating-mode work.

### Detailed execution checklist

1. [x] Freeze the Phase D task-local structure, exact scope, contracts, oracle
   order, planned production seams, evidence families, exclusions, stop rules,
   and commit boundary under `PORT-003/phase-d/` before changing production
   code. Record the Author's unattended authorization and required post-item
   TODO reread.
2. [x] Generate a bounded deterministic provenance inventory for palette
   allocation/mutation, RGB222 quantization, Copper signal-list resolution,
   logical readback, software sprites, hardware sprites, text cursor, and mouse
   cursor. Fingerprint exact official VDP/vdp-gl `v2.16.0`/`all-the-plots`
   source spans and separate retained observable behavior from excluded VGA
   signal tables, DMA scanout, and ISR mechanics.
3. [x] Generate independent palette, Copper, logical-readback, and overlay
   fixtures before trusting production output. Cover every native depth,
   single/double buffering, duplicate colors, index wrapping, implicit palette
   creation, allocation failure, all-delete, unknown/deleted signal-list IDs,
   short/long/zero-row lists, clipping, alpha, XOR, and overlay order. Golden
   results must come from the written contract or source-derived model, never
   from the implementation under test.
4. [x] Implement allocator-injected project-owned palette/Copper state. Preserve
   the stock 16-bit palette-ID domain, palette-0 protection, copy-on-create,
   RGB222 output quantization, explicit lookup rebuild, unknown/deleted-ID
   fallback, final-span extension, and mode-reset behavior. Keep palette 0's
   drawing LUT distinct from secondary presentation palettes.
5. [x] Implement one pure row/region presentation compositor over explicit
   logical-plane, mode, palette/Copper, and overlay inputs. Emit RGB888 without
   modifying logical storage. Keep the compositor independent of FabGL
   controller inheritance, frame timing, transport, network, panel, and sink
   ownership.
6. [x] Integrate palette and compositor seams narrowly into
   `P4DisplayController`. Preserve ordinary `readScreen()` and native-save
   behavior as palette-0 logical views. Preserve unchanged common software
   sprite drawing, and compose text cursor, ascending hardware sprites, and
   mouse cursor after Copper conversion using exact upstream clipping,
   transparency, overwrite, and RGBA2222-XOR rules.
7. [x] Define and test the Phase D quiescent composition boundary. Palette,
   Copper, and overlay inputs must be coherent for one composition call, but no
   sink may receive a mutable framebuffer pointer or enter the frame-service
   task. Do not freeze a consumer lease, callback, output format family, or
   long-lived storage contract; Phase F owns that handoff.
8. [x] Run the complete host matrix under ASan/UBSan and explicit allocation
   accounting. Prove palette/readback independence, Copper-only presentation
   changes, software-versus-hardware sprite placement, cursor ordering,
   clipping, single/double visible-plane selection, reset, repeated mutation,
   and all injected allocation failures without leaks or stale state.
9. [x] Add a dedicated `p4-presentation` diagnostic environment and exact
   machine-readable source selection. Compile the Phase C frame service plus
   Phase D state/compositor and unchanged retained Canvas/common controller;
   prove the build excludes classic VGA/CVBS/Scene/PS2, physical audio,
   network, storage, official facade, and every physical output sink. Do not
   deploy or assign a qualification identity.
10. [x] Update canonical dependency/provenance records, source-selection
    projections, compatibility delta, architecture-facing task evidence, and
    the dated development log. Record every unavoidable replacement and any
    inherited upstream defect or unsafe implementation detail beside the code
    and in task evidence without claiming a behavior improvement.
11. [x] Regenerate every Phase D and canonical artifact twice byte-identically;
    verify all immutable imports, source spans, schemas, permanent tests,
    changed links, machine-path absence, white SVG backgrounds, project-owned
    whitespace, and `git diff --check`.
12. [x] Audit the staged Phase D boundary against this checklist and Gate D.
    Commit and push one coherent Phase D result only when every criterion below
    passes. Then reread the authoritative TODO/task documents before planning
    Phase E.

### Phase D execution record

1. Scope and contract freeze — complete:
   - `phase-d/README.md`, `contracts.md`, and
     `implementation-manifest.yaml` define the bounded role-named package,
     planned production seams, independent-oracle rule, output-sink/lease
     deferrals, exact exclusions, and one coherent Phase D commit boundary;
   - the synchronous controller composition seam is explicitly quiescent
     qualification machinery, not the Phase F consumer API; and
   - the returned EMOS commits are recorded only as provisional downstream
     context, with no parity, transport, or hardware claim entering this phase.
2. Presentation provenance — complete:
   - `extract-presentation-provenance.py` deterministically fingerprints 47
     exact callable/source-region records across 11 official VDP/vdp-gl files
     plus the canonical Copper documentation hash;
   - records distinguish retained facade/common/readback behavior, adapted
     palette and overlay algorithms, project-owned allocation/composition
     replacements, and five excluded classic physical-engine regions;
   - four permanent tests verify tuple uniqueness, every file/span hash,
     critical retained/adapted/excluded records, and the logical-versus-
     presentation split; and
   - the first invocation used the system Python, which lacks the project's
     pinned YAML dependency. The accepted process uses `.venv/bin/python`.
     The generator derives the canonical `agon-docs` sibling location from the
     workspace root and records only repository-relative documentation paths,
     keeping machine topology out of generated evidence.
3. Independent presentation fixtures — complete:
   - the pure Python source-derived model generates nine palette-state cases,
     eight composition cases, and two allocation-failure cases across all five
     native depths and both buffering states;
   - fixtures cover copied/implicit palettes, wrapped entries, explicit LUT
     rebuild, unknown/deleted IDs, all-delete, empty/zero-row/short/extended
     Copper lists, direct RGB222, visible-plane selection, alpha, XOR, clipping,
     software exclusion, and text/hardware/mouse ordering;
   - five generator tests prove case/hash uniqueness, complete format and
     buffering coverage, required edge cases, overlay dimensions, and oracle
     independence; all nine Phase D tests pass and a second generation is
     byte-identical; and
   - the model records upstream's explicit integer-truncated HSV-distance LUT
     rule rather than retaining Phase B's temporary full-double helper. Exact
     default-palette arithmetic produces the same selected entries, but the
     integer boundary remains part of mutable-palette compatibility and is now
     tested as such.
4. Palette and Copper state — complete:
   - new project-owned `PaletteState` uses one embedded primary palette and
     reset span plus allocator-injected secondary nodes and multi-span lists;
     it preserves all 16-bit IDs without imposing a project capacity limit;
   - copy-on-create/recreate, wrapped writes, implicit creation, RGB222
     quantization, explicit integer-distance LUT rebuild, palette-0 protection,
     robust all-delete, unknown-ID resolution, delete fallback, zero-row/final
     span behavior, and allocation-preserving updates are implemented without
     classic signal maps;
   - fixed RGB222 modes reject palette/Copper mutation and convert drawing
     colors directly; successful controller reconfiguration can reset the
     complete palette state without another allocation boundary; and
   - the standalone ASan/UBSan C++ test passes exact defaults, the retained
     integer-HSV tie decision, lifecycle, signal, late-create, deletion,
     fixed-mode, and both injected allocation failures with zero live
     allocations at teardown.
5. Pure presentation compositor — complete:
   - new project-owned `PresentationCompositor` consumes only explicit native
     plane, mode, palette/Copper, region, overlay, and caller-owned RGB888
     views; it owns no framebuffer, task, timing, transport, controller, sink,
     or output-device lifetime;
   - base conversion leaves logical bytes untouched and applies Copper
     palettes by absolute display row, while independently ordered overlay
     calls preserve clipping, alpha, overwrite, and RGBA2222-XOR rules;
   - dimensions, arithmetic, enum values, source extents, destination extents,
     native stride, and native storage are checked before access, including
     adversarial coordinate and overflow paths; and
   - the standalone ASan/UBSan test passes Copper conversion, exact stock
     palette order, clipped transparency, XOR-after-Copper behavior, and
     invalid-region/invalid-format rejection. LeakSanitizer itself cannot run
     under the execution harness's ptrace boundary; project allocator leaks
     remain covered explicitly and the final host matrix will repeat that
     accounting.
6. Retained-controller integration — complete:
   - `P4DisplayController` now owns `PaletteState`, resets it only after a
     successful transactional mode allocation, and exposes the narrow palette,
     LUT, and Copper mutation seams required by the later official facade;
   - drawing conversion, `readScreen()`, and native-save conversion use only
     palette 0, while composed presentation borrows the visible plane and
     applies text cursor, ascending hardware sprites, and mouse cursor in exact
     retained order; unsupported hardware-overlay bitmap formats remain
     ignored as they are upstream;
   - common software-sprite save/draw/restore code remains unedited and outside
     the compositor; no classic controller, sink, frame callback, transport,
     or facade was introduced; and
   - ASan/UBSan retained-controller tests pass the complete Phase C queue/frame
     regression plus Copper/readback separation, secondary-palette
     independence, and text/hardware/mouse ordering through the integrated
     controller seam.
7. Quiescent composition boundary — complete:
   - the synchronous controller seam accepts composition only with the frame
     service stopped or controller background execution disabled/suspended;
     an active unsuspended service returns `NotQuiescent` before frame state is
     borrowed;
   - the actor contract requires the caller to retain that state and own all
     palette, bitmap, sprite, and cursor mutation until the call returns; only
     copied RGB888 values leave the boundary;
   - a sanitizer-backed integration test proves stopped, rejected-running, and
     explicitly suspended-running cases; and
   - this is intentionally a Phase D misuse detector, not a sink callback,
     mutable frame lease, long-lived pointer, output-format family, or Phase F
     consumer contract.
8. Complete host presentation matrix — complete:
   - `run-host-presentation-tests.py` generates a temporary C++ fixture driver,
     compiles production palette/codec/compositor code under ASan/UBSan, and
     compares all nine palette cases, eight composition cases, and two
     allocation-failure cases with the independent YAML oracle;
   - three fixed harnesses additionally prove controller integration,
     quiescence, exact overlay order, software-versus-hardware placement,
     drawing-versus-visible double-buffer selection, and explicit allocation
     teardown; Phase B's complete native/primitive suite and Phase C's 12
     logical-frame fixtures also pass after their retained-controller source
     closures were updated;
   - cross-phase regression caught an uncommitted P8/P16 default-palette error:
     the first Phase D implementation and oracle both packed red/blue in the
     wrong lanes. Official controller defaults and the independent Phase B
     suite identified the shared error; both Phase D sources were corrected
     before evidence was accepted; and
   - the same audit corrected two fixture-schema ambiguities: Copper row
     expectations now retain their queried rows, and double-buffer logical
     readback is explicitly generated from the drawing plane while composed
     presentation is generated from the visible plane. All project-managed
     allocations return to zero; LSAN remains unavailable under managed
     tracing and is not claimed.
9. P4 compile and link closure — complete:
   - the dedicated `p4-presentation` environment compiles and links the Phase C
     frame service, Phase D palette/compositor/controller seams, retained
     Canvas/common controller, and a compile-only presentation canary as 11
     exact machine-readable translation units;
   - deterministic ELF/map validation proves all nine required retained and
     project-owned seams are linked, while classic VGA/CVBS/Scene/PS2, physical
     audio, network, storage, official facade, and output-sink source/symbol
     families remain absent;
   - PlatformIO initially retained its globally installed Arduino 2.0.14
     framework package despite the project's Arduino 3.3.11 platform pin. A
     package URL install reported success without replacing the shared package;
     explicitly uninstalling that global package allowed the project build to
     install and use its pinned framework. This is a PlatformIO package-cache
     behavior, not a source workaround; and
   - the resulting binary is evidence from a sink-free compile/link diagnostic
     only. It was not assigned an artifact identity, deployed, or physically
     qualified.
10. Durable dependency and compatibility records — complete:
    - the canonical dependency graph now consumes the Phase D build closure,
      projects the presentation canary, palette state, compositor, controller,
      frame service, and unchanged retained/vendored units as explicit build
      units, and carries those relationships into the task-facing slices;
    - `phase-d/compatibility-delta.md` separates retained observable behavior
      from the unavoidable project-owned VGA-physical replacements and from
      Phase E/F, sink, transport, MOS/EMOS, and physical-qualification deferrals;
    - the completed implementation manifest, source selections, generated
      provenance, and dated development log record no vendored patch and make
      the diagnostic-only evidence boundary explicit; and
    - the current pioarduino package layout splits Arduino sources from the
      architecture libraries. The task evidence generator correctly requires
      `framework-arduinoespressif32-libs` as its P4 capability root; passing the
      similarly named Arduino source package fails immediately on the first
      missing ESP-IDF capability header and does not produce accepted evidence.
11. Deterministic final validation — complete:
    - Phase D provenance, independent fixtures, host results, and build/link
      evidence each regenerated twice with identical SHA-256 results; the
      canonical dependency and PORT-003 task projections each passed their
      built-in two-pass byte-identity checks;
    - all 53 permanent PORT-003 Phase A–D and dependency-tool Python tests pass;
      the Phase D host run passes 19 generated fixtures and three fixed C++
      harnesses under ASan/UBSan, including the complete Phase B native/render
      and Phase C logical-frame regressions;
    - because the shared controller now depends on Phase D palette/compositor
      units, the Phase B and C source selections, P4 builds, ELF/map validators,
      and tracked closure evidence were rebuilt rather than left describing
      stale pre-Phase-D link sets. They prove 9 and 11 exact application units,
      respectively, with all required symbols and zero excluded families;
    - all six Phase D YAML records parse, canonical graph schemas and source
      imports validate, all changed local Markdown targets exist, generated
      SVGs retain explicit white backgrounds, and no machine-local path or
      vendored-source edit entered the change; and
    - project whitespace and `git diff --check` pass. No target was deployed,
      no physical run was performed, and no Phase E/F or transport contract was
      selected.
12. Gate D audit — complete:
    - the final boundary contains only Phase D palette/Copper/composition code,
      its compile-only canary and exact source selections, deterministic
      fixtures/evidence/generators/tests, the required Phase B/C closure refresh,
      canonical dependency projections, task records, and the dated log;
    - all six Gate D criteria are independently evidenced: palette-0 logical
      fidelity, Copper presentation behavior, software/hardware overlay split,
      drawing/visible plane separation, bounded allocation failure, and clean
      pinned P4 compile/link closure;
    - every explicit exclusion and stop condition remains intact. In
      particular, no vendored byte, official facade/parser, transport, EMOS,
      operating-mode policy, physical sink, consumer lease, deployment, bench
      operation, artifact identity, or hardware claim entered the phase; and
    - Gate D passed at 2026-08-24 06:42 EDT under the Author's unattended
      authorization. Phase E remains a separate post-commit planning boundary.

### Phase D gate criteria

1. Palette-0 drawing quantization and logical readback match independent
   expectations at all five native depths; secondary palettes never rewrite
   logical bytes.
2. Copper composition matches documented row-count/palette-ID behavior,
   including fallback and reset, while fixed 64-color presentation remains
   direct RGB222.
3. Software sprites remain in unchanged common framebuffer handling, while
   hardware sprites and both cursors appear only in composed presentation in
   exact stock order and color-operation semantics.
4. Single- and double-buffer tests distinguish drawing and visible planes and
   prove composed output independently from logical readback.
5. Allocation failures and repeated palette/signal-list changes leave valid,
   bounded state with no vendored source edit or classic physical dependency.
6. A clean pinned P4 diagnostic build and deterministic host evidence prove
   the declared closure without deployment, output-sink, transport, EMOS
   parity, or hardware-qualification claims.

### Phase D explicit exclusions

- No edit to immutable official VDP or vendored dependency bytes.
- No `agon_screen.h` facade, official mode table/fallback, context, callback,
  Teletext, VDU parser, MOS, EMOS, or operating-mode integration; those remain
  Phase E, PORT-008, or SETUP-005 work.
- No network/browser, RGB, MIPI-DSI, HDMI, or other physical output consumer.
- No frame-consumer API freeze, long-lived framebuffer lease, sink-owned
  buffer, or assertion that a Phase D quiescent composition call is the Phase F
  production handoff.
- No classic GPIO/I2S/DMA/VSYNC code, physical deployment, bench operation,
  artifact identity, or target runtime qualification.

### Phase D stop conditions

Stop for Author review if preserving observable behavior requires editing
vendored source, linking a classic physical controller, changing native bytes
or logical readback, letting composition or a sink block logical frame time,
freezing the Phase F consumer contract, choosing a Phase E facade or SETUP-005
mode policy, or inventing an application-visible command/protocol. Also stop
if an independently demonstrated palette/Copper/overlay difference cannot be
isolated and measured, or if target compilation invalidates the accepted
project-owned seam.
