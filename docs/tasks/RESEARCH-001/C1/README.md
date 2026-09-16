# C1 — esp_lvgl_adapter source investigation

## Executive summary

**Useful architectural reference; no demonstrated immediate throughput fix.**
Extender already has immutable snapshot leases, short pool-state transitions,
producer backpressure and transmission outside the pool lock. Copying those
features from LVGL would duplicate existing mechanisms. The most useful lesson
is to distinguish buffer reuse, transfer completion and presentation, then
measure each owner's wait separately.

The remaining concrete suspect is the interaction between Extender's row
preparation and native drawing, plus shared-memory/scheduler interference outside
that lock. LVGL does not eliminate this class of contention: its worker holds
its broader recursive LVGL mutex across `lv_timer_handler`, whose flush path can
wait for display buffers. “Short state locks” does not mean every lock is short.
No observed Extender bug is established by this comparison.

**Disposition:** finish C1's source-only investigation here, retain it for future
MIPI LCD work, and propose a bounded wait/hold diagnostic under existing P01c/d.
Do not import LVGL, change scheduling or add cache flushes on this evidence.
Author review is next; C2 has not started. C1 is not a performance pass, and its
proposed measurements remain open. RLE stays deferred until all five candidate
avenues have recorded dispositions.

No build, sample execution, flash, reset, benchmark or firmware change occurred.
The sole hardware action at closeout is the requested accepted voice cue.

Focused second pass: [allocation/cache findings](MEMORY.md). It confirms SDK-owned
Ethernet cache synchronization and lower-stack allocation/copy work, without
establishing their runtime cost or an allocator defect.

## 1. Question and evidence scope

Can the adapter reveal an omitted ownership, completion or scheduling mechanism
that explains Extender's increased rendering tails during output, without
changing stock VDP drawing semantics? Focus: LVGL9 double-direct/full and
unrotated triple-full paths, their shared pipeline, worker and MIPI callbacks.
Other display modes, LVGL internals and all cancellation races are not certified.

Upstream: esp-iot-solution commit
`6958385313b0e4fc1f3de259b1d677fca7d7d236`, adapter0.7.0, IDF>=5.5.
Local review starts at Extender commit `9646e9a` (documentation-only scope freeze).
The four key local files below match the retained P02 r45 source byte-for-byte.
P02's selected build is IDF5.5.5/Arduino3.3.11; r43 was restored afterward.
Neither current default macros nor old source comments establish deployed flags.
P02 manifest selects output core1/priority2, drawing-twice, lookahead, direct
packed rows and internal game framebuffer. Snapshot allocation remains PSRAM.
See [source/config provenance](provenance.json) and [P02 results](../../QUAL-003/debrief/P02/README.md).

## 2. Mechanism comparison

| Mechanism | Inspected adapter behavior | Extender comparison and implication |
|---|---|---|
| Worker wake | `lvgl_worker`: run LVGL timers under recursive mutex, release it, then bounded notification wait | Stock timer notifies draw/output tasks; notifications coalesce. Timer phase and runnable delay remain measurable; LVGL's timer policy is not an Agon refresh contract |
| Ownership | Free/busy lists under `pipeline.lock`; ISR releases retired buffers | Pool uses Free/Producer/Latest/Leased states and generation-tagged leases; copies/sends occur outside transition lock. Principle already present |
| Completion wait | Double-buffer path saves switch sequence, submits, checks whether switch already occurred, then waits on semaphore; free-list path clears stale notification before checking authoritative list | Extender pool producer tries once and can defer publication; browser consumer polls for a new generation. No corresponding LCD ISR wait to transplant |
| Triple buffering | One pending DPI switch; old front remains busy until completion callback; producer waits for reusable buffer | Lookahead can overlap snapshot production and send. Adding buffers does not remove composition cost or shared PSRAM bandwidth |
| Broad lock | Worker holds LVGL lock across timer/render/flush processing; flush may block for buffer completion | Native guard covers each row batch and each retained drawing operation, not the full snapshot or queue drain. Measure wait and hold independently |
| Memory | Stack capabilities/affinity configurable; default stack is internal. Panel buffers are supplied via esp_lcd; cache helpers account for address/alignment | Snapshot slots explicitly PSRAM; selected game framebuffer internal. CPU cores still share memory resources; core assignment alone cannot prove isolation |
| DMA coherency | C2M synchronization before DMA-visible output; separate invalidation helper for memory-to-cache direction | No evidence of a missing CPU snapshot cache flush. Driver-managed Ethernet DMA must be traced in its own contract; LCD helpers are not a general network optimization |
| Overload | Display paths block for buffers rather than guaranteeing all render calls fit a refresh interval | On-demand snapshots/Latest replacement limit work; leased bytes remain stable. Presentation counts must remain distinct from VDP completion |

Local paths:
`vdp/video/extender/display/{stock_p4_service.cpp,stock_runtime_controller.hpp,presentation_snapshot_pool.cpp}`,
`vdp/video/extender/web/browser_video_provider.cpp`, and `vdp/video/agon_screen.h`.

## 3. Relevant call paths and subtleties

1. **Double-buffer reuse:** `display_bridge_v9_submit_double_buffer` calls
   prepare-wait, full-frame blit, arm-after-submit and wait-ready. Sequence/predicate
   checks are intended to cover a completion arriving before the task sleeps.
   The shared completion ISR updates the sequence and gives the semaphore.
   This is a useful pattern, not a formal concurrency proof: sequence updates,
   submission gating and all callback interleavings still require qualification
   before reuse. No upstream bug fix is proposed.
2. **Triple-full:** wait for previous switch → submit → mark old front busy →
   publish pending pointer → wait for free buffer → flush-ready. Completion ISR
   promotes pending to display and recycles the retired buffer. The common
   free-list wait checks state again after wakeup; notifications are hints,
   not a count of frames that must be drawn. Do not equate triple buffering with
   unlimited queuing or a throughput multiplier.
3. **MIPI API distinctions:** IDF5.5.5 documents colour-transfer completion as
   permission to recycle a copied source, explicitly not proof of screen refresh.
   Frame-buffer completion allows reuse of the display buffer; VSYNC is another
   callback. The adapter chooses callback paths by mode and has CMake feature
   detection for `on_frame_buf_complete`, with a legacy-name fallback. This is
   valuable for our eventual LCD backend. An Ethernet send returning and a
   browser displaying a frame likewise establish different things.
4. **Native output:** `StockP4Service::publish` reserves a producer slot, obtains
   native row data through `prepareRow/prepareRows`, normalizes it into packed
   PSRAM outside native exclusion, then publishes. A small ownership lock does
   not protect us from hundreds of native-lock acquisitions, long drawing
   operations, runnable delay or cache traffic. Do not report the aggregate
   composition interval as exclusive CPU execution time.
5. **No magic jitter cure:** common bridge has a VSYNC “jitter shield” threshold
   relative to submission. It filters a physical display event path, not CPU
   contention or Ethernet latency. Copying that delay/filter into web output
   would have no demonstrated justification.
6. **Configuration tradeoffs:** adapter guidance suggests larger L2/cache lines
   and PSRAM XIP. Those differ from our retained128KiB/64-byte/no-XIP settings.
   Larger cache consumes internal memory; moving instructions into PSRAM changes
   traffic. These are conditional experiments, not a configuration patch to copy.

## 4. Timing evidence and limits

No new C1 timing data. Relevant historical P02 controls, same SW fixture:

| Condition | Composition mean (ms) | Rendering completion interval p95 (ms) |
|---|---:|---:|
| Discard repeat6 | 13.537 | 45.509 |
| Normal streaming1 | 13.623 | 29.238 |
| Discard3 | 6.429 | 17.318 |
| Output off2 | Not performed | 17.049 |

Worst p95 first. These are separate scopes, not additive/subtractable costs.
The two discard runs undermine a network-only explanation. C1 has no matched
LVGL workload, so a vendor-versus-Agon speedup percentage would be invented.

## 5. Smallest useful proposed check — not executed

Use existing P01c/d ownership rather than create a new suite. Retain the exact
reference fixture and output-isolation controls; first freeze a separately
reviewed diagnostic build and rollback. Measure timer opportunity-to-task-entry,
native-lock wait/hold for output row batches and drawing operations, pool
admission/deferred-publication counts, and normalization outside the native lock.
Record actual task core/priority and snapshot addresses/capabilities.

Use bounded in-memory aggregate counters or supported trace; no printing per
row/pixel or live SD traffic. Compare probe-on/off overhead and repeat order/boot
conditions. Preserve state/pixel oracles and account for every valid completion.
This is an attribution experiment, not an affinity change plus several fixes.

1. If row/native waits dominate delayed completion windows, investigate exclusion
   and wake ordering while preserving stock row/primitive semantics.
2. If delays occur outside that lock and increase with PSRAM work, isolate memory
   placement/traffic next; do not conclude cache contention from elapsed time alone.
3. If runnable delay dominates, use actual scheduler evidence to select one
   affinity/priority change rather than copying LVGL task defaults.
4. If sequence/lease counters reveal lost completion or early reuse, treat that
   correctness finding as a stopping point before performance tuning.

## 6. Primary-source navigation

Pinned adapter source directory: [esp_lvgl_adapter](https://github.com/espressif/esp-iot-solution/tree/6958385313b0e4fc1f3de259b1d677fca7d7d236/components/display/tools/esp_lvgl_adapter).
Within it: `src/adapter/esp_lv_adapter.c` (worker/start),
`src/display/bridge/v9/lvgl_bridge_v9.c` (submit/wait/callbacks/flush),
`src/display/bridge/common/display_bridge_common.c` (pipeline/cache/VSYNC),
`include/esp_lv_adapter.h` (configuration), and `CMakeLists.txt` (feature detection).
Exact file URLs and hashes are in provenance.json and the parent source ledger.

Official [IDF5.5.5 MIPI callback contracts](https://github.com/espressif/esp-idf/blob/v5.5.5/components/esp_lcd/dsi/include/esp_lcd_mipi_dsi.h)
were checked against the installed header. The versioned HTML guide failed to
open; the versioned official source supplied the needed API contract instead.
No claim of binary compatibility or interrupt-core placement is made without
a build and actual panel initialization. Those remain future LCD qualification.
