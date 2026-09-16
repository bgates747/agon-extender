# C1 follow-up — allocation, cache and ownership

## Executive summary

**The focused second pass was worthwhile, but establishes no malloc defect or
missing snapshot cache flush.** Extender preallocates its PSRAM snapshot slots.
Its selected WebSocket send helper does not allocate a full-frame staging copy.
Below that, TCP uses copying writes and dynamically allocated packet storage;
the Ethernet driver copies into reusable internal DMA buffers and performs its
own cache synchronization. This is real memory traffic even with a preallocated
application pool. Its cost has not been isolated by measurement.

The adapter's useful lessons are explicit memory capabilities, ownership-aware
cleanup, and synchronization at the actual CPU/DMA boundary. Its LCD cache
helpers are not a universal performance treatment. In particular, rounding an
invalidation range to cache lines requires ownership of those whole lines.

**Next avenues, in order:** retain P01c/d wait attribution; add bounded packet
allocation/copy and memory-placement accounting if needed; investigate heap
fragmentation only if largest-block/free-memory evidence warrants it. Do not
add blanket flushes, replace malloc, or import LVGL. No new timing result,
firmware change, build, flash or test. Stop for review before C2.

## Scope and evidence

Contract frozen at `1678332`. Same pinned adapter as the parent C1 report:
`6958385313b0e4fc1f3de259b1d677fca7d7d236`. Selected LVGL9 full/direct paths,
allocation setup/teardown and adjacent partial/rotation cache calls were read.
This is not exhaustive LVGL, PPA, DMA2D, encryption or cancellation certification.
Installed IDF5.5.5 sources establish our SDK behavior; hashes in
[memory-provenance.json](memory-provenance.json). Runtime allocation placement,
counts, failures and cache misses were not measured.

## Allocation comparison

| Area | Source finding | Practical consequence |
|---|---|---|
| Adapter full/direct frame storage | Display manager borrows panel framebuffers; pipeline allocates metadata at initialization | No reason to allocate an application frame every refresh |
| Adapter owned buffers | Explicit internal/PSRAM capabilities; aligned allocation attempted; null returns propagated | Capability selection and failure handling matter separately from speed |
| Adapter fallback | Non-encrypted path can fall back from aligned allocation to ordinary capability allocation; encrypted PSRAM path refuses that fallback | Do not assume every returned buffer has requested cache alignment; check consumer requirements |
| Adapter teardown | Distinguishes borrowed panel buffers from owned draw/dummy buffers; failed node initialization invokes destruction | Borrowing a buffer must not transfer responsibility for freeing it |
| Adapter worker | Stack defaults internal; optional PSRAM stack allocation retries internally if creation fails | Record actual successful placement, not merely requested placement |
| Extender snapshots | Pool constructor allocates all slots; partial failure frees prior slots; service persists across native mode updates | Steady-state snapshot publication is not a malloc/free loop |
| Extender network | WebSocket header is stack storage; application sends leased pixel segment; socket/TCP path copies data and allocates packet storage | Preallocation at the application level does not eliminate lower-stack allocation or copying |
| Ethernet DMA | Driver allocates reusable internal DMA buffers, copies packet bytes, writes back buffers/descriptors before DMA ownership | Our PSRAM snapshot is not the DMA buffer in this path |

Adapter source navigation, relative to its pinned component: 
`src/display/display_manager.c`: registration230–241, owned/borrowed free483–504,
teardown677–732, allocator1159–1204, full/direct panel selection1332–1380,
LVGL9 setup1407–1493. `src/adapter/esp_lv_adapter.c`: worker creation679–726.
`src/display/bridge/common/display_bridge_common.c`: pipeline setup1238–1322.
LVGL9 bridge creates metadata and synchronization objects during creation,
rebuilds pipeline state on reconfiguration, and releases these on teardown.
Dummy draw can lazily allocate its private buffer; partial modes allocate
separate drawing storage. These lifecycle operations must not be confused with
steady-state full-frame flushes. LVGL's own renderer allocations remain outside
this bounded review. No claim that all of LVGL is allocation-free.

Ordinary allocation fallback is a portability consideration, not a demonstrated
upstream bug. Likewise, this review does not certify every allocation-size
overflow, arbitrary invalid configuration, concurrent teardown or error branch.
No upstream fix is proposed.

## Cache operations belong to specific ownership boundaries

Adapter common bridge491–576 determines alignment by address/memory class,
writes back CPU-written regions with C2M, and invalidates with M2C. Its range
helper rounds outward; its framebuffer writeback permits unaligned ranges.
These helpers discard the synchronization return value. That deserves explicit
error/ownership qualification if reused, not a speculative upstream patch.
Adjacent LVGL9 partial/rotation paths2786,2893–2894,3025,3051–3053 combine
source synchronization, CPU/accelerated copies and framebuffer synchronization.
Those operations cannot be lifted out of their buffer ownership and completion
contracts and applied to a CPU-only snapshot producer.

Espressif's [memory synchronization guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/system/mm_sync.html)
distinguishes CPU/DMA visibility and warns about invalidation of neighboring
dirty bytes when ranges are not cache-line owned. The stable page resolved to
**6.1**, not our SDK. Requested5.5.5 HTML was unavailable; installed5.5.5
`components/esp_mm/include/esp_cache.h` and implementation supply the local
direction/flag contract. Do not infer that internal RAM is always uncached: P4's
`SOC_CACHE_INTERNAL_MEM_VIA_L1CACHE` is enabled in the inspected SoC header.

For our network path, the important source chain is:

1. `wired_network_service.cpp::completeSend` calls socket `send`; the selected
   HTTP `httpd_ws_send_frame_async` uses a stack header and invokes the configured
   send function. Other similarly named SDK helpers allocate request records;
   those are not evidence that this particular helper does so.
2. lwIP `sockets.c::lwip_send` sets `NETCONN_COPY`; `tcp_out.c` allocates TCP
   segment/pbuf storage and `pbuf.c` allocates PBUF_RAM via `mem_malloc`. Exact
   allocation counts, pooling behavior and actual memory placement need the
   selected configuration plus measurements, not a count of source call sites.
3. `esp_eth_mac_esp.c` delegates to `esp_eth_mac_esp_dma.c`. Its transmit paths
   copy payload into reusable DMA buffers; the normal path writes back payload
   and descriptors before giving descriptors to DMA. Its P4 cache macros use
   C2M/M2C. Allocation requests internal, DMA-capable storage.

Thus no missing application-level cache flush was identified. Extra snapshot
flushes could increase shared-memory work. Cache correctness and cache/memory
bandwidth contention are different questions.

## Diagnostic considerations — owned by P01c/d, not executed

| Priority | Question | Bounded evidence to collect if authorized |
|---|---|---|
| 1 | Lock/runnable delay versus actual copy work? | Existing wait/hold/wake attribution; output composition and send scopes kept separate |
| 2 | Runtime packet allocations/copies material? | Counts/bytes and time by selected caller/task; failures; distinguish CPU work from blocked send time |
| 3 | Placement or allocation order changes cache pressure? | Actual slot/task/packet memory capabilities and addresses; alignment; controlled startup/repeat ordering |
| 4 | Heap pressure or fragmentation? | Internal and PSRAM free totals, minima, largest free block over the same run |

Largest-free-block divergence from free total can motivate fragmentation checks;
free space alone cannot establish a leak or fragmentation cause. Hooks must not
allocate, block or print. Store bounded aggregates, retrieve after the measured
window, and compare instrumentation overhead to an unchanged control. Heavy
heap poisoning/tracing is not a neutral baseline. Full cache-line isolation is
a prerequisite for any proposed DMA invalidation experiment, not proof such an
experiment is needed here.

**Disposition:** retain these distinctions in the common considerations. This
second pass narrows the proposed measurement, not the performance verdict.
Neither fragmentation nor cache contention is proven; C1 supplies no new FPS
or milliseconds, and does not change the existing P02 results.
