# PORT-003 — Implement the P4 display backend and logical frame service

## State

- Status: In progress — Review Gate 1 approved; Phase A authorized
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
