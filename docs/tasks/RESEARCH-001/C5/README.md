# C5 — P4 Vectrex source review

## Executive summary

**Interesting specialized sparse renderer, not a demonstrated full-frame
streaming solution.** It avoids repainting stable vector lines, keeps descriptors
and task stacks in internal memory, and drops pending application frames. These
reduce work or latency but do not establish our512×384×64-colour60Hz goal.

The inspected cross-core handoff has check/claim races: volatile slot state does
not make the producer's reuse and renderer's acquisition atomic. “Newest” is
selected by slot index rather than a frame sequence. Its DISPLAY FPS counter
increments before waiting for VSYNC and before checking whether there is any
frame to render. That counter cannot prove unique completed frames per second.
No hardware reproduction or upstream modification was attempted.

**Disposition:** retain explicit frame ownership, outcome accounting and the
principle of avoiding redundant work; do not copy this handoff or treat its
FPS display as parity evidence. All five candidate source reviews now have
dispositions. Next review can address the deferred AGM/RLE avenue; no codec
implementation or benchmark begins automatically. No builds, flashes, resets,
firmware tests or ROM downloads occurred.

## 1. Scope and identity

Contract60cb017. Repository malbanGit/ESP32_P4_Vectrex, revision
`caf2d9b77e1c9eaa5b7f8805fc0172650dbea051`. Inspected main.c frame pipeline,
relevant definitions/configuration and README; supporting HDMI/audio files
retained in source provenance, not exhaustively audited. Scope excludes CPU
emulation accuracy, all rasterizers, panel driver completion and audio timing.
[provenance.json](provenance.json) preserves source hashes.

## 2. Work and ownership comparison

| Mechanism | Source behavior | Relevance/limit |
|---|---|---|
| Logical frames | Three internal-memory slots, up to1000 vector lines each | Small descriptors differ from complete pixel snapshots |
| Display buffers | Two physical framebuffer pointers; per-buffer line history | Logical slots are not three display framebuffers |
| Producer | Marks READY, discards an encountered older pending slot, selects FREE or READY storage | Explicit frame loss; not every emulated frame is rendered |
| Consumer | Binary VSYNC semaphore; scans READY slots and keeps highest matching index | Slot index is not chronological generation |
| Redraw | Match old/new lines, erase removed lines, repair overlapping stable lines, draw new lines | Saves writes for sparse/stable scenes; full-screen changes gain much less |
| Tasks | Renderer core0 priority3; application core1 priority7; audio core1 priority20 | Different workload; source comments report audio interference, not matched timing evidence |
| Presentation | Swap pointers, submit panel bitmap, release logical slot | Panel submission does not independently prove physical display completion |

main.c194–238 defines slots/history;814–913 publishes/reuses;1000–1067 selects;
1110 onward matches/propagates damage;1359–1376 submits;1540–1572 creates tasks.
The damage-repair phase includes nested overlap searches and propagation. The
whole algorithm is not guaranteed linear-time merely because matching uses
a hash table. It depends on vector-scene structure and maintained per-buffer
history, not an arbitrary VDP bitmap command stream.

## 3. Concrete source concerns

1. **Check/claim race:** producer tests a slot READY before setting it FREE;
   renderer tests READY before setting RENDERING. Renderer can claim between
   producer check and store, then producer can free/rebuild its active slot.
   Conversely, renderer can select a slot that producer reuses before the claim.
   No common mutex, critical section or atomic compare/exchange protects these
   inspected transitions. Volatile does not provide exclusive ownership or
   publication ordering for the nonvolatile line data. This is a source-level
   unsafe interleaving, not an observed device failure in this task.
2. **Newest selection unproved:** the highest READY index wins; reused slots
   have no monotonic generation. Producer's cleanup loop breaks on the first
   READY entry even when that entry is its current build slot. Comments about
   newest/oldest therefore do not constitute a freshness guarantee.
3. **FPS counter scope:** DISPLAY FPS increments at1031, before VSYNC wait and
   the no-ready-frame continue. It counts renderer iterations, including those
   without a submitted frame. EMU FPS counts application frame-end calls, whose
   duration depends on game behavior; the source explicitly warns about that.
   Neither proves distinct visible frames or exact nominal60Hz completion.
4. **Cache comments are not contracts:** DRAM placement does not itself pin a
   palette permanently in L1. No proof of cache residency or isolation follows
   from the placement annotation.

Official [IDF SMP documentation][smp] describes cross-core synchronization and
atomic operations. Stable HTML resolves to6.1; upstream reports IDF5.5.1. No
newer SDK behavior is assumed as a fix for these source-level check/store races.
A VSYNC semaphore synchronizes the ISR and renderer; it does not serialize the
producer's slot-reuse decisions.

## 4. Performance claims and evidence boundary

README describes360MHz CPU/200MHz PSRAM, YUV422 physical display output and
selective line erasure instead of full clears. Its “halving” claim relative to
RGB888 is arithmetically inaccurate:2 rather than3 bytes per pixel is a one-third
reduction, not one-half. Physical panel scanout is not browser Ethernet output.
Claims that a full clear is infeasible are workload observations, not a measured
bandwidth limit applicable to our smaller resolution.

No comparable single-operation milliseconds, rendered-frame distribution,
stock-mainboard baseline or continuous browser delivery result was established.
Therefore no performance percentage or port recommendation is justified.
The emulator remains an interesting separate future project, not scope for this
review or permission to run downloaded firmware/ROMs.

## 5. Consolidated five-candidate disposition

| Candidate | Retain | Do not infer/adopt |
|---|---|---|
| C1 LVGL adapter | Explicit memory capabilities, CPU/DMA ownership, wait attribution | Generic cache flushing or a demonstrated throughput fix |
| C2 micro-mp3 | Controlled independent-worker experiment structure | Bus causality from oversubscription; unchanged failure-prone harness |
| C3 NINA | Owned capture outside display lock; long-lived buffer reservation | JPEG screenshot throughput as lossless streaming parity |
| C4 GMF | Bounded stage ownership and separate drop/completion accounting | Pacing after production as saved rendering work |
| C5 Vectrex | Avoid redundant work where semantics permit; explicit generations needed | Unsafe slot handoff, sparse workload FPS as full-frame proof |

No candidate establishes that our remaining slowdown is unavoidable. None
provides a qualified drop-in fix. Existing P01/P02 attribution and P06 independent
output controls remain the applicable measurements. Source-only dispositions
satisfy the five-candidate prerequisite; deferred AGM/RLE review can now resume
when authorized. The cadence/interpolation ideas remain fallback considerations,
not a weakened acceptance target. Stop for Author review.

[smp]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/system/freertos_idf.html

Primary source: [pinned main.c](https://github.com/malbanGit/ESP32_P4_Vectrex/blob/caf2d9b77e1c9eaa5b7f8805fc0172650dbea051/main/main.c).
Related definitions and README are under the same pinned repository revision.
