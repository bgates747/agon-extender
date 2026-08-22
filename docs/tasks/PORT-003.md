# PORT-003 — Implement the P4 display backend and logical frame service

## State

- Status: In progress — Review Gate 1 approved; Phase A complete
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
