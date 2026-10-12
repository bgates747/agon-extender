# RESEARCH-007 — Linear one-byte/PPA HDMI integration

## Executive summary

Author authorizes implementation, deployment and bounded testing after committing
and pushing existing work. P4 drawing will use linear one-byte physical RGB222
pixels, and the PPA will expand a private L8 snapshot into the existing RGB888
HDMI background. No full-frame VGA byte-lane reorder belongs in this path.
Stock-visible colours, drawing, readback, sprite backgrounds and EMOS routing
remain unchanged. This experimental selection does not replace production.

## Frozen scope — 2026-10-11

1. Reuse common stock rasterizers and the project-owned 64-colour controller;
   select a linear byte storage policy explicitly at build time. Adapt physical
   pixel access, allocation, fill/copy/scroll operations to one-byte pixels.
   Preserve logical stock64 physical colours, including high sync-bit aliases
   in the fixed256-entry CLUT. Custom256 palette/API work remains out of scope.
2. The core1 HDMI output task snapshots visible linear rows under native
   exclusion, then releases exclusion before a blocking public PPA BLEND call.
   No live logical row pointer survives into DMA. The task owns the only CLUT
   BLEND client and initializes its fixed palette before transactions begin.
   Retain the benchmarked transparent A8 second input required by BLEND.
3. Use independent HDMI front/back backgrounds even for logical single-buffer
   modes; never let PPA overwrite a scanned front. Keep existing rolling-strip
   DMA and immutable hardware-sprite/cursor scenes. Discard snapshots crossing
   a logical double-buffer swap. Keep stock application swap/frame semantics.
4. Keep packed-depth controllers and cropped/unselected geometries on their
   existing paths. Keep automatic384/480-line carriers and320 scaling;320
   requires expansion followed by existing SRM scaling, not a nonexistent
   combined L8/SRM operation. Preserve ordinary mode0 outro visibility.
5. Promote the exact six-file, hash-pinned CLUT backport into a reusable build
   compatibility location. Generate component overrides per build; never
   modify the selected SDK or official upstream reference checkouts.
6. Preserve ordinary UART behavior and installed EMOS/mainboard VDP. Do not
   optimize ExExt, add CRC, change wiring, modify game logic or start AUDIT-011.
   Preserve retained ordinary P4 rollback and original SD startup bytes.

## Bounded research and contracts

The [pipeline inventory](PIPELINE-INVENTORY.md), [capability report](CAPABILITY-REPORT.md)
and [physical results](PHYSICAL-RESULTS.md) provide pinned source/SDK evidence.
Official contracts: `agon-docs/docs/vdp/Bitmaps-API.md` (physical colour
quantization, Native captures and software/hardware sprites), `VDU-Commands.md`
(colours/scrolling) and `Screen-Modes.md` (logical buffering). Read-only VDP
reference remains v2.16.0. Source identities are recorded before candidate builds.

Local controller generic bitmap/glyph/readback helpers already isolate physical
pixel access. RGB888-specific raw spans, allocation size and borrowed panel
ownership require adaptation. The immutable rolling scene owns overlay assets;
its CPU ISR must not submit PPA operations. Small overlay row adapters may still
use stock VGA signal order locally; background storage and PPA input stay linear.

## Subtasks

### R07-I01 [x] Freeze layout/lifetime contract and source dependency map

Record the affected pixel-access, row allocation, copy/scroll, Native bitmap,
readback and output consumers. Commit/push this contract before implementation.
Record the accepted experimental layout decision in an ADR and architecture.

### R07-I02 [x] Implement linear controller and PPA output integration

Add explicit build selection, preserve old selection, reuse proven driver and
renderer operations, and document every hardware-specific departure beside
code. Record fixed-CLUT ownership, cache, snapshot and DMA lifetimes. No claim of
whole-renderer improvement follows the standalone benchmark alone.

### R07-I03 [ ] Verify offline correctness and complete target build

Reuse controller golden tests with the new storage selection, checking clipping,
scrolling, bitmap formats/alpha, painting and saved backgrounds. Verify build
selectors fail closed and the actual target links the CLUT backport. Build from
committed inputs, record identity/configuration/hashes and retain exact rollback.

### R07-I04 [ ] Deploy and run bounded existing fixtures

After fresh bench ownership/readiness checks, flash/verify the candidate while
Agon is held reset. Reuse existing colour, scroll/software-sprite, hardware-sprite
and320 double-buffer fixtures plus a finite deterministic Nurples run. Select
fixture modes only in autoexec; restore original startup afterward. Capture
ordinary HDMI timing/fault logs and retained game timing data. Check keyboard
readiness and mode0 outro. Do not infer visual acceptance from counters.

### R07-I05 [ ] Leave a concrete Nurples review and report

Leave the verified full firmware, ordinary input and actual Nurples application
ready for Author playtest if bounded checks pass. On regression restore exact
ordinary P4 and explain evidence. Update current build/use limits, task and log;
commit/push owned results. Production promotion remains separately gated by
Author acceptance, agreed version and required release checks.

## Implemented dependency seam (validation pending)

| Consumer | Linear-byte accommodation | Unchanged contract |
|---|---|---|
| P4-owned64-colour controller pixel lambdas | Compile-time1-byte/3-byte pixel policy; linear x addressing | Stock common rasterizers and paint operations |
| Allocator/initial clear | Logical width bytes per row, independent of HDMI stride | Native row tables, single/double image ownership |
| Raw fill/copy/HScroll | Byte-sized memset/memcpy/memmove spans | Clipping and scroll direction |
| Partial VScroll | Existing field-only copy remedy with1-byte spans | Incoming row/background restore order |
| Native bitmap/software-sprite save | Shared generic byte get/set operations | One-byte Native saves and opacity semantics |
| Readback/capture | Physical byte decoded using existing RGB222 semantics | Visible colours, public bitmap formats |
| Output snapshot | Private linear row copies, generation check across double swap | No live row reaches DMA |
| PPA BLEND | Fixed256-entry table repeats physical64 colours | Logical palette remapping does not recolour existing pixels |
| Rolling hardware overlays | Existing deep-copied immutable scene | Same sprite order, XOR and cursor composition |
| Scaled320 | Decorated byte snapshot, BLEND expansion, existing SRM | Logical buffering and bilinear2x presentation |
| Mode0/packed depths | Existing controller/output path | Copper/packed palette and outro visibility |

P4Color64Controller is the common implementation; the P4Rgb888Controller alias
retains existing test/caller compatibility. The explicit indexed build selects
linear storage; ordinary selection still uses three-byte storage. Historical
filenames remain so this change does not manufacture a second copied renderer.

## Offline checkpoint

Indexed and retainedRGB888 controller golden runs pass;14 HDMI build-selection
tests pass. The full version-record validator is blocked by a pre-existing
light2-harness-r02 connectivity hash mismatch (expected560ab589…, actual
c68e4d4f…); this tranche does not edit that unrelated electrical record. Target
compile/link, actual component binding, concurrent scanout and bench tests remain.

The first full build exposed an esp-dl dependency on stock HAL headers preceding
the PPA include overlay. The reusable generator now overrides both owning
components locally, replacing only the six pinned files, and validation checks
all compile actions for unwanted SDK HAL paths. Candidate r02 supersedes the
unlinked r01 build. The selected SDK remains unchanged. r02 compiles, links and
passes actual-source/component validation. r03 additionally labels linear
storage correctly in read-only status, retains separate preparation/expansion/
cache phase boundaries and rejects a single-HDMI-buffer allocation. Expansion
wall time includes driver cache handling and the320 SRM pass when selected;
it is neither isolated CLUT kernel time nor CPU occupancy. r04 completes the
existing diagnostic enum/counter bindings; its actual HDMI target syntax check
passes before the final full build. r03 was stopped before link, not deployed.

The bench has a newer fsim reservation. Finish compilation and concrete offline
test preparation before deployment; do not interrupt the reserved manual tests.
