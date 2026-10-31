# Rolling scanout cache synchronization accommodation

P4 rolling scanout needs interrupts admitted while output tasks synchronize
large HDMI planes. Pinned ESP-IDF 5.5.5 provides task C2M writeback chunking,
but deliberately keeps M2C and post-writeback invalidation as whole-range
critical sections. This is a local real-time constraint, not an upstream cache
correctness defect. The r21 physical clear regression still aborts with the
C2M option enabled; the additional invalidation accommodation needs physical
qualification under the unchanged 1600 µs/DMA guards.

1. `derivative.json` pins SDK commit b774170ff46c393eeb5e495ea37936038d3f4f4f,
   all 27 component files, the original/derived cache source and exact patch.
   `scripts/p4_cache_msync.py` copies the component into the disposable native
   project and changes only `esp_cache_msync.c`. The SDK remains read-only.
2. Task-owned invalidation uses the existing configured 16 KiB C2M quantum.
   The original API still validates the entire range, flags, overflow and
   alignment before any cache work and holds its existing task mutex for the
   complete call. Each task chunk retains the original cache critical section.
3. ISR and non-yieldable callers retain the original single invalidation.
   Rolling ISR callbacks read PSRAM planes and write separate SRAM strip slots;
   they do not write a task's private HDMI output plane. Tasks must still
   complete synchronization before publishing their output buffer to DMA.
4. This selection applies only to explicit rolling builds. The native validator
   verifies every copied byte, the sole cache compile action, its archive
   membership and its ELF link. Ordinary non-rolling builds retain SDK source.
5. Host tests compile actual SDK API/helper bodies with controlled HAL/RTOS
   stand-ins and an old-source negative control. They establish range work and
   retained dispatch/validation, not cache hardware behavior or interrupt time.
6. Remove/review the derivative when Espressif supplies suitable invalidation
   chunking or the SDK/ownership changes. Requalify cache coherence, output
   lifetime and physical deadlines before choosing any replacement or quantum.

The bounded research and physical gates remain in
[the wide-clear task record](../../../docs/tasks/HDMI-002/WIDE-CLEAR-REPAIR.md).
