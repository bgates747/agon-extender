# SCAN01-S03 — Segmented DMA feasibility

## Executive summary

**Source study complete; the full Nurples segmentation gate is not cleared.**
ESP-IDF 5.5.5 already drives HDMI through a linked-list-capable DMA controller.
However, its DSI bridge has a **four-bit block-count field**, and the current
driver configures exactly one block per frame. A straightforward mapping of
Nurples' independently scrolling field requires **1,010 blocks**. Passing that
count to the existing helper silently truncates it. Neither the pinned SDK nor
the chip-revision-specific manual establishes a supported way around this.

Nurples' coordinates and RGB888 row lengths satisfy conservative DMA alignment
requirements. Moving its scroll mapping instead of its pixels remains promising,
but it is not yet a justified renderer architecture. S07 can start with a
**14-block, four-row specimen** to prove small-list DSI operation and retirement.
Success there would not prove a 336-row playing field. Longer-list operation needs
its own demonstrated bridge handshake/frame-end rule before integration.

Descriptor ownership and pixel ownership are separate. Even working scatter/gather
DMA would not by itself prevent the renderer's software-sprite erase/redraw cycle
from appearing on HDMI. No new drawing budget, implicit double buffering or
application-specific VDU command is proposed.

This step changes research/task records only. No renderer/SDK edit, build,
firmware test, card access, board operation, commit or push occurred. Next is
S04, subject to the Author's one-subtask approval rule.

## References and scope

The [S01 baseline](S01-BASELINE.md) and [S02 audit](S02-AUDIT.md) retain the exact
game, renderer and firmware identities. SDK references below are pinned to
`b774170ff46c393eeb5e495ea37936038d3f4f4f` (IDF 5.5.5), not current upstream HEAD.
`DW_GDMA` in this SDK means the **VDMA controller** in the technical manual;
the manual's ordinary GDMA-AXI descriptor rules are not interchangeable.

| ID | Authority / inspected detail |
|---|---|
| R01 | [P4 chip revision v1.3 TRM](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_technical_reference_manual_en.pdf), pre-release v0.4, dated 2026-06-11; chapter 5, especially §§5.4, 5.5.1–5.5.4, 5.7.3 and registers 5.10–5.11. Its release table still marks **MIPI DSI “to be added later”**. Retrieved 2026-10-06, SHA-256 `ae1fa2a411776760e03329adc3f9a7c13e98c440168cab208f06e3b2d5818830`. |
| R02 | [Pinned DPI driver](../../../agents/build001/native-tools/esp-idf/components/esp_lcd/dsi/esp_lcd_panel_dpi.c): `dpi_panel_create_dma_link`, `dpi_panel_init`, `mipi_dsi_dma_trans_done_cb`, bridge setup and underrun ISR. File SHA-256 `a0b13536fec34d3cc4a6324ab64bc9bb62fee4db39dec24133681bc3c17b8373`. |
| R03 | [DW-GDMA API](../../../agents/build001/native-tools/esp-idf/components/esp_hw_support/dma/include/esp_private/dw_gdma.h) and [implementation](../../../agents/build001/native-tools/esp-idf/components/esp_hw_support/dma/dw_gdma.c): list allocation, transfer configuration, noncached descriptor handles, ISR and callback registration. |
| R04 | [P4 DMA LL](../../../agents/build001/native-tools/esp-idf/components/hal/esp32p4/include/hal/dw_gdma_ll.h): 64-byte descriptor structure, item counts, markers, master ports and flow-control selection. |
| R05 | [P4 DSI bridge LL](../../../agents/build001/native-tools/esp-idf/components/hal/esp32p4/include/hal/mipi_dsi_brg_ll.h) and [pre-v3 bridge register layout](../../../agents/build001/native-tools/esp-idf/components/soc/esp32p4/register/hw_ver1/soc/mipi_dsi_bridge_struct.h): `dma_flow_multiblk_num`, `dma_multiblk_en`, FIFO/flow settings and available interrupts. |
| R06 | [DMA types](../../../agents/build001/native-tools/esp-idf/components/hal/include/hal/dw_gdma_types.h), [SDK tests](../../../agents/build001/native-tools/esp-idf/components/esp_hw_support/test_apps/dma/main/test_dw_gdma.c), [cache synchronization](../../../agents/build001/native-tools/esp-idf/components/esp_mm/esp_cache_msync.c). The SDK's two-item memory-to-memory test is not a DSI segmentation test. |
| R07 | [Current HDMI adapter](../../../vdp/video/extender/display/hdmi_output.cpp), [ownership helper](../../../vdp/video/extender/display/hdmi_buffer_ownership.hpp), [direct renderer](../../../vdp/video/extender/display/p4_rgb888_controller.cpp), and [existing source-replacement build seam](../../../vdp/native/usb_fsls_only.cmake). |
| R08 | [Espressif errata summary](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32p4/02-errata-summary/index.html), reviewed 2026-10-06. The listed PSRAM unaligned-DMA stale-data issue MSPI-750 affects v3.0, not this v1.3 baseline. That does not establish arbitrary unaligned DSI transfers as supported. |

The downloaded manual, local arithmetic receipt and source verification are
retained under ignored `agents/scan001/s03/`. Hardware conclusions below separate
explicit register/API facts from conservative restrictions and unproved options.

## Findings and implementation constraints

| ID | Finding | Consequence |
|---|---|---|
| F01 | VDMA supports linked blocks with independent source addresses. The DPI driver already selects LIST for both ends, memory as source, DSI as destination, hardware handshake and DMA-controlled flow. | Source row order need not be physically linear **at the DMA engine**. This alone does not establish the bridge's handling of a long list. |
| F02 | The pre-v3 DSI bridge stores `dma_flow_multiblk_num` in four bits. The LL helper assigns the supplied count without range validation and enables multiblock when count > 1. Current DPI supplies 1. | Positive counts 1–15 are representable. No inspected contract gives 0 a meaning of 16, infinity or count-ignore. A count of 1,010 becomes 2; do not use it. Treat >15 as a source gate, not a proven universal silicon limit. |
| F03 | VDMA's `BLOCK_TS` is 22 bits and stores **source items minus one**. The SDK `.size` is an item count despite its vague header comment. DPI uses 64-bit source and destination widths. | Accept 1…4,194,304 items; bytes/8 for the initial candidate. A full RGB888 720p frame is only 345,600 items. No zero-length descriptor; validate before SDK calls, which do not enforce these bounds. |
| F04 | The v1.3 manual enumerates 8/16/32/64-bit transfer widths. The generic SDK enum also names larger widths. | Do not assume the generic enum establishes 128/256/512-bit support on this silicon. Preserve the working 64-bit DSI path. |
| F05 | The inspected SAR description does not settle arbitrary unaligned source reads. Existing DPI supplies aligned allocations and a byte length divisible by eight. | Initially require each source address and block length to be 8-byte aligned. This is a conservative proof boundary, not a discovered statement that all unaligned accesses are impossible. Cache ownership adds a separate 64-byte boundary. |
| F06 | A VDMA block can end with shorter transactions than its configured burst. Current DPI uses source MSIZE 512, destination MSIZE 256, AXI burst length 16. Bridge burst/empty-threshold helper comments apply to bridge-controlled flow. | A 768-byte block is not ruled out merely because it is shorter than MSIZE. But memory-to-memory success does not prove DSI tail handshakes; exercise these exact lengths. Do not switch flow controller or lower all burst settings as an unexplained fix. |
| F07 | A descriptor is exactly 64 bytes, aligned to 64. IDF allocates the list in internal DMA-capable RAM, synchronizes once and exposes noncached aliases for CPU writes. | Keep descriptors internal in the first proof. Two large lists consume meaningful internal SRAM; PSRAM list relocation is not an automatic escape. R01 warns about PSRAM LLIs when peripheral status writeback is disabled. |
| F08 | VDMA can prefetch LLIs and clears VALID during descriptor writeback. The DPI restart callback rearms only item 0 and marks it LAST. | For a segmented frame, every consumed entry needs rearming, and only the actual final entry may be LAST. Never modify a live or prefetched list. Merely increasing allocation size cannot work. |
| F09 | On this pre-v3 configuration `MIPI_DSI_BRG_LL_EVENT_VSYNC` is 0. DPI restarts DMA before invoking the application's framebuffer-complete callback. | Use full-list DMA completion as the source-memory retirement event, not as proof that the last pixel has reached HDMI. Block completion is not frame completion. Carry explicit old/new generation identity through restart. |
| F10 | The bridge underrun ISR logs an error but does not recover the picture. The DW-GDMA public callback group covers block/full completion and invalid LLIs, not all AXI/slave errors. | The specimen needs durable underrun/invalid/error evidence and an explicit safe stop/recovery path. A rising frame counter alone is insufficient. |
| F11 | The current descriptor has incrementing source address, fixed DSI FIFO destination and item count; it has no row-pitch or scatter pattern field. | A narrow rectangle in rows separated by a 3,840-byte stride needs separate blocks. Increasing block size would transmit unwanted sidebar bytes; fewer blocks cannot describe arbitrary per-row partial scrolling without another mechanism or copies. |

The general VDMA alternate flow-controller options do not resolve F02 by
themselves. Bridge-controlled flow, suppressing the bridge's multiblock/frame
interval mechanism, or using different source/destination block types each
requires evidence that row payloads, final-byte detection and continuous frame
restart still agree. The absent DSI chapter prevents choosing one from source
alone. None is selected here. There is no reviewed long-list DSI example in the
pinned SDK; its basic linked-list test moves memory to memory.

## Actual Nurples geometry and costs

The accepted output remains 1280×720 RGB888 with a 3,840-byte stride. Mode 20's
512×384 image is centered at panel (384,168). Its 256×336 field at logical
(128,48) therefore occupies panel **X512…767, Y216…551**.

For one field row, DMA would read 1,536 bytes of stationary left content,
768 bytes from the mapped field row, then 1,536 bytes of stationary right
content. These boundaries and the row stride are even multiples of 64. The
216 rows above the field and 168 below it can each remain one contiguous block
if their ordinary panel storage remains allocated. Thus the straightforward
layout is `1 + 336×3 + 1 = 1,010` descriptors. The stream still contains exactly
2,764,800 bytes; neither padding bytes nor extra pixels may appear at a join.

Costs below are arithmetic, **not measured throughput or allocation success**.
The table is ordered by descriptor memory, worst first. It assumes independent
active and prepared descriptor banks; object/heap metadata and renderer state
are additional.

| Layout | Blocks/frame | One descriptor bank | Two banks | Status |
|---|---:|---:|---:|---|
| Naive three segments on every 720p row | 2,160 | 138,240 B | 276,480 B (270 KiB) | Unnecessary overhead; exceeds representable bridge count |
| Nurples-sized field with up to two unaligned edge cells/row | ≤1,682 | ≤107,648 B | ≤215,296 B (210.25 KiB) | Arithmetic upper bound; bridge gate unresolved |
| Aligned Nurples field, coalesced stationary top/bottom | 1,010 | 64,640 B | 129,280 B (126.25 KiB) | Target layout; bridge gate unresolved |
| Four-row aligned specimen, same field X/width | 14 | 896 B | 1,792 B | Count fits; DSI behavior untested |
| Existing contiguous frame | 1 | 64 B | 128 B | Working driver baseline |

With a simple fixed descriptor topology, one downward scroll changes 336 field
source addresses, while only the new 768-byte field row needs clearing/drawing.
The CPU must still rearm **all 1,010 descriptors for each repeated DMA frame**;
unchanged pixels do not eliminate this work. The existing marker helper performs
several bitfield stores, so a count of one four-byte write per descriptor is only
a lower bound. Rebuilding every complete node would write 64,640 bytes per
publication (3.88 MB/s at nominal 60 Hz), not a measured instruction or bus cost.
Descriptor fetch/writeback also consumes bandwidth, separately from PSRAM pixels.

The field's tightly packed RGB888 storage is 258,048 bytes (252 KiB). One spare
field row costs 768 bytes. A simple proof retaining the current two panel buffers
(5,529,600 bytes) and adding one separate field plane plus a spare totals
**5,788,416 bytes**, before other renderer allocations. Two such field generations
plus two spares total 6,047,232 bytes. These are deliberately explicit incremental
budgets, not permission to silently allocate another full image or claims that
the running firmware has sufficient free/contiguous heap. Reusing suitably
retired panel slices could avoid the extra plane; validate their lifetime first.

Nominal 60-Hz scanout still reads 165.888 MB/s of active RGB888 pixel payload. The
current 60-MHz/1350×741 timing calculates to 59.979 Hz. Segmentation removes CPU
movement of existing scroll pixels; it does **not** reduce the HDMI frame's pixel
payload or promise sprite/input headroom. Compare eventual measured results with
the explicit rectangle-copy control: 257,280 copied destination bytes per scroll,
plus reads, clearing and cache work; see S02.

## Odd coordinates, narrow strips and cache boundaries

**E01 — RGB byte phase.** For an aligned source row, an RGB888 pixel boundary
is also an eight-byte boundary only every eight pixels. One pixel is three
bytes; source 8-bit transfers do not establish that the fixed DSI FIFO accepts
three-byte blocks without packing/tail effects. Keep the established B,G,R byte
stream intact across descriptors, including splits inside a pixel. Do not add
padding to an output block merely to satisfy alignment.

**E02 — Costed boundary-cell alternative.** For vertical-only row remapping,
keep source-byte addresses congruent modulo 8 with their intended output-byte
positions. Existing full-width row slices naturally preserve this; a compact
region plane may need a prefix of `(3×panelX) mod 8` bytes and padded row stride.
At each unaligned left/right boundary, construct the affected eight-byte output
cell in aligned scratch from both neighboring regions. Direct descriptors cover
the aligned interiors. Two boundaries require at most 16 copied bytes per row;
when they fall in the same cell, merge them. A one-pixel strip therefore needs
one or two cells, not a fabricated three-byte DSI transaction.

For 336 rows this is at most 5,376 copied bytes/update. Packing both edge cells in
one independently owned 64-byte slot per row costs 21,504 bytes per scratch bank,
43,008 bytes for two; cleaning those whole slots covers 21 KiB/update. The worst
simple topology has five segments/row plus the two outer bands (1,682 nodes).
That is a bounded edge copy, not a hidden full-frame copy, but it **worsens the
block-count obstacle**. Nurples' aligned field needs none of it.

If source/output alignment phases differ, the aligned interior may itself be
unaligned in source memory. E02 then does not suffice: correct the allocation
layout, prove a different supported source-width strategy, or disclose the
required larger copy. New arbitrary viewport partitions cannot assume the
compact plane has the right phase. Cache isolation padding changes allocation
size, never the number of transmitted image bytes.

**E03 — Cache publication.** Pixel writes use CPU cache; VDMA reads memory.
Clean modified physical storage before publishing its descriptor generation.
Rotating already-clean row addresses does not require cleaning unchanged field
pixels, but software sprites, bitmap writes, overlays and newly reused rows do.
The current full-frame `draw_bitmap` cache clean is not a dirty-region tracker.
For a simple scroll-only proof, the newly written 768-byte aligned row needs
12 cache lines. General full-field changes cover 4,032 lines; a whole panel covers
43,200, with the pinned 64-byte cache-line configuration. API range length is not
a measurement of actual writebacks. CPU/cache exclusion must cover neighboring
pixels sharing a cleaned line; cache synchronization is not a mutex against DMA
or the other CPU core.

## Safe reuse and publication requirements

**L01 — Descriptor banks.** The CPU prepares only an inactive bank through IDF's
noncached descriptor handles. Validate addresses/counts/stream size, clean pixel
storage, and publish ownership with appropriate memory ordering before DMA start.
Preserve IDF's cached physical addresses in links, not its CPU noncached aliases.
Only the final node has LAST; every node is valid before traversal. Reusing the
same bank requires all consumed VALID bits to be reset after retirement.

**L02 — Pixel rows.** A new list can refer to many of the same rows as the old
list. Switching lists does not free those rows. For scroll-only operation with
one pending update, an H+1-row pool can provide a fresh incoming row; reuse the
dropped row only after the old list completes and no active/prepared list still
references it. More pending updates need more retained rows or explicit producer
backpressure. One spare is not sufficient for unrestricted drawing to shared
rows. Software-sprite restoration/redraw and hardware-overlay restoration remain
separate hazards; worst-case copy-on-write can approach another whole field or
image. S08 must choose and cost that policy without secretly changing VDU mode
buffering semantics.

**L03 — Continuous output.** The current one-node callback cheaply rearms and
restarts the frame. Doing 1,010 node rearms in the ISR is new work with an unmeasured
restart delay. Preparing/rearming a retired bank in task context reduces ISR work
but needs a fully ready replacement even when the picture is unchanged. Define
what happens if none is ready; do not busy-wait in the ISR, edit the active list,
or submit consumed invalid nodes. A 14-node specimen can measure bounded ISR
rearming first. This is a scanout deadline, not a budget limiting VDU drawing.

**L04 — Generation retirement.** On full-list completion the driver identifies
the retiring generation, selects a completely prepared successor with the same
proven bridge block configuration, restarts DMA, then releases
only storage no successor retains. The current framebuffer-index callback is
insufficient for independently owned region rows. Keep memory-readable lifetime
through peripheral consumption; DMA completion does not mean HDMI display time.
Mode teardown must stop/retire DMA before freeing rows, scratch or LLIs, and
leave a valid output/rollback path. CPU locks alone do not provide this guarantee.
Initially change the block count only through output reinitialization between
specimen stages; live changes to bridge framing are not established here.

## Project-owned driver seam

Use a narrow project-owned derivative of the pinned DPI translation unit when
S07 is authorized, following the existing hash-checked CMake replacement pattern
in R07. Keep the SDK tree untouched. Preserve Apache-2.0 provenance and an exact
diff; pin R02's input hash and fail the build if the expected source or unique
translation-unit replacement changes. Keep the existing `esp_lcd` target's
include paths/private DSI bus definition rather than casting its private object
layout from unrelated application code. The LT8912B driver and other panel
paths stay stock; enable the experimental path explicitly for the specimen.
The generated source also needs an explicit private include path to the pinned
SDK's `dsi/` directory: moving the translation unit otherwise loses its relative
access to `mipi_dsi_priv.h`.

The derivative needs project-owned entry points for validated segment-list
submission and retirement/diagnostic snapshots. It must own list allocation,
per-node configuration/rearming, bridge block count, restart/cancellation and
frame-generation identity. Reject unrepresentable counts initially. Do not
replace Espressif's whole DSI host/PHY implementation, duplicate the bus owner,
steal an in-use DMA channel or edit the cached SDK in place. The existing public
`draw_bitmap` API does not expose a descriptor list; this is a pinned private
driver adaptation with maintenance cost, not a public API already supported
by Espressif.

## Standalone specimen design for existing S07

These are design stages inside S07, not work executed by S03 and not new top-level
subtasks. Preserve ordinary output timing, color order and reversible rollback.
They need no Agon game or SD card: the P4 draws the test image itself.

| Stage | Smallest useful experiment | Required evidence / stop condition |
|---|---|---|
| P01 | Same picture through one ordinary descriptor, then 3 full-width horizontal bands, then 15 bands. Keep DMA-controlled flow and set the actual bridge block count. | Exact bytes/frame, LAST only at final node, every block consumed, full-list completion rate and zero bridge underruns. This establishes small multiblock handling only. |
| P02 | A four-row 256-pixel-wide middle at panel X512, with stationary left/right and coalesced top/bottom: 14 blocks. Give rows unique colors/numbers; rotate them through a five-row pool. | Sidebars remain fixed; one-row scroll/wrap is visible; retired row is reused only after the old generation releases it. Hold visual proof for the Author. |
| P03 | A two-row odd-X/odd-width field, maximum 12 blocks with E02 edge scratch; include a one-pixel-wide strip and a one-scanline-high case. | Byte-for-byte software stream reconstruction plus photographed edge/color correctness; allocation guards unchanged, no out-of-bounds clean/read or leaked padding. A host reconstruction is not proof of hardware scanout. |
| P04 | Alternate prepared banks; deliberately delay preparation, exercise safe repeat/rearm, then terminate/reinitialize the output owner. | Retained generation IDs, missing-bank/error counters, restart duration and ownership assertions; no continuing after underrun/invalid-list failure merely because counters advance. |
| P05 | Only after establishing a justified bridge-control method, exceed 15 blocks and work up to the 1,010-block geometry under load. | Separate evidence for long-list framing/handshake, total byte count, descriptor heap, frame rate and safe retirement. Never test 1010 by silently truncating the field. If no justified method exists, stop and present alternatives at S08. |

Record underruns before the ISR clears status, invalid-list callbacks, relevant
DMA error/status registers, completed/published generation counts, per-stage wall
duration and CPU publication/rearm time. Keep capture diagnostics optional;
they must not become a condition for correct live output. Do not alter the
LT8912B's accepted timing to conceal a segmentation failure. There is no claimed
minimum sustained frame rate from this unexecuted design.

## Disposition

**S03 complete as a feasibility investigation, not a positive hardware proof.**
Small aligned lists have a source-supported design worth testing. Full-field
scatter/gather remains conditional on the four-bit bridge-count issue, memory
budget and safe pixel lifetime. Aligned edge copying addresses byte boundaries,
not the bridge-count issue. A narrow rectangle-copy fallback remains a much
smaller renderer change if long-list DSI proves unsuitable; it still requires
measured Nurples/sprite/input acceptance and Author architecture approval.

Offline arithmetic verifies the 1,010-node layout's total bytes, item bounds and
alignment, and 7,150 edge-boundary combinations satisfy the stated two-cell bound
under E02's source-phase prerequisite. These are calculations, not firmware or
emulator tests. S01 Extender/game inputs and the pinned SDK remain unchanged.
Proceed no further than this source study without the next subtask authorization.
