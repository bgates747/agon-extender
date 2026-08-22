# PORT-003 — Implement the P4 display backend and logical frame service

## State

- Status: In progress — Review Gate 1 approved; Phases A–B complete
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
  frame counter, completion sequence, logical swap-at-frame-edge, or consumer
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
