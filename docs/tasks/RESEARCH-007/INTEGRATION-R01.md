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

### R07-I01 [ ] Freeze layout/lifetime contract and source dependency map

Record the affected pixel-access, row allocation, copy/scroll, Native bitmap,
readback and output consumers. Commit/push this contract before implementation.
Record the accepted experimental layout decision in an ADR and architecture.

### R07-I02 [ ] Implement linear controller and PPA output integration

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
