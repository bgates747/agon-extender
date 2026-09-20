# First graphics-backend source pass — 2026-09-20

## Result and limits

EDP selects the restored stock depth controllers and native row storage, not the
retired generic flat-framebuffer renderer. This pass found no newly demonstrated,
non-deferred missing drawing command. It does not establish exhaustive parity or
identify the installed firmware. The full audit remains open.

[Baseline](baseline.json) records commits, file hashes, build selection and the
pre-existing dirty working tree. Stock VDP was clean at v2.16.0
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`; its vdp-gl dependency was clean at
`ac2dd5986daf496c43ae8e7fe41836274aec54a0`. Official docs were read at
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` (VDU Commands, Screen Modes and
Bitmaps API). The tag is the newest locally available tag, not a remote-release
verification. EDP source baseline is `db314dd6` plus the recorded working tree.

[File census](SOURCE-CENSUS.md): 106 upstream vdp-gl source files retained,
94 identical and 12 modified; 47 upstream VDP video files retained, 28 identical
and 19 modified. No upstream file is absent from these compared trees. Inclusion
in the tree does not mean inclusion in the executable or identical conditional
compilation. These are source comparisons, not new performance measurements.

## Source-backed findings

Paths below are repository-relative; symbols identify the reviewed boundaries.

| Area | Finding | Source and limits |
|---|---|---|
| Controller selection | Retained: original 2/4/8/16/64-colour controllers. Retired generic rendering units explicitly forbidden by source selection. | [factory](../../../vdp/video/extender/display/stock_runtime_controller.cpp), `makeStockRuntimeController`; [selection](../../../vdp/pio/p4-console-source-selection.json). |
| Native storage | Retained native row-pointer layouts. Allocation capabilities adapted for P4 PSRAM; optional internal-memory experiments must not be assumed enabled. | [paletted controller](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp), `allocateViewPort`; [base](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp). |
| Viewport scrolling | VGA64 keeps stock `genericVScroll` and `HScroll`, including word-aligned fast paths and inherited slow unaligned fallback. The fallback is not a newly invented P4 algorithm. | [VGA64](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp), `VScroll`, `HScroll`; prior static clipping/scroll evidence remains scoped. |
| Bitmap clipping and sprites | Shared stock primitive dispatch, clipping state and sprite composition remain. P4 adds native-access guards and diagnostic hooks. Static parity is established for selected scenes, not every dynamic interaction. | [display controller](../../../vdp/vendor/vdp-gl/src/displaycontroller.cpp), `execPrimitive`, `showSprites`, clipping helpers; [coverage](../QUAL-004/COVERAGE.md). |
| Command execution | P4 gate wraps stock queue consumption and sprite refresh. Drain has no timeout budget. Task admission/suspension are P4-specific. | [binding](../../../vdp/video/extender/display/stock_runtime_controller.hpp), `drain`; this pass proposes no new drawing budget. |
| Swap and lifecycle | Native displayed/drawing row-pointer swap retained; physical DMA descriptor handling excluded. Binding teardown assumes both worker tasks have already joined. Correctness of all transitions remains unresolved. | [base](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp), swap path; [binding](../../../vdp/video/extender/display/stock_runtime_controller.hpp), `end`. |
| Output | Classic ESP32 VGA hardware execution replaced by P4 task/timer service and snapshots. Portable stock scanline composition is retained; output normalization is a boundary conversion. Per-row guards alone do not establish an atomic full-frame snapshot. | [service](../../../vdp/video/extender/display/stock_p4_service.cpp); [scanline](../../../vdp/video/extender/display/stock_scanline.cpp); binding `prepareRow`. Scheduling and output remain material adaptations, not proof of a defect. |
| Intentional omissions | Physical mouse cursor, audio synthesis and native HDMI/LCD output remain deferred. Updater/printer/terminal decisions are unchanged. | Existing task decisions remain authoritative; no new implementation tranche for these features is proposed. |
| False missing-feature candidates | Empty VGA64 palette setter is inherited stock behavior. Unselected text-only VGA hardware controller does not prove absent teletext: retained `agon_ttxt.h` is included by the screen layer. | These must not become speculative fixes. Mode 7 remains unqualified in the scoped image campaign. |

Previously accepted numeric safety changes in transform/sample bounds remain
local deviations; this audit neither introduces nor expands upstream fixes.
File-wide equality of `canvas.cpp` also does not prove equivalence of the
controller and output implementations that it calls.

## Recommended next tranche — review proposal, not authorization

**AUDIT-007-N01** [ ] PORT-003 owns a bounded investigation of P4 graphics
mode-transition teardown and resource lifetime, with qualification tracked in
QUAL-004. Start with the retained two restart observations and trace the EDP
mode-change caller through worker shutdown, queued primitives, sprite/Copper
references and controller destruction. Compare stock ownership and ordering;
identify necessary P4 adaptations explicitly. Do not assume a stale pointer,
watchdog or memory exhaustion before capturing evidence.

Reason: [retained results](../QUAL-004/RESULTS.md) show two actual P4 restarts
during mode startup, including one after explicit sprite/Copper cleanup. No
panic trace was obtained. Eight prepared mode controls, including mode136
PAGE_FRONT/PAGE_SWAP, therefore remain unqualified. This is a stronger basis
for work than inventing another missing drawing API.

Proposed acceptance: preserve the failing sequence and collect reset/panic cause;
if a defect is established, make the smallest source-backed correction, repeat
the transition sequence with retained serial evidence, and complete the prepared
page-front/page-swap controls against mainboard reference images. State exact
repetition count, firmware identities and restoration procedure in the separate
implementation/bench contract before execution. A pass must not silently close
all mode transitions or the exhaustive audit. No browser throughput work, game
optimization, drawing budgets or opportunistic upstream fixes.

Stop here for Author review. No source code, firmware, hardware or official
reference checkout was changed by this audit.
