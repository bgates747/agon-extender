# Wide-screen clear deadline repair

The r20 cursor/scaler regression discovers a native mode96 clear abort before
any320-mode case runs. Staged hardware checks keep96 selection healthy and
reproduce the fault immediately after VDU12. The next candidate enables the
pinned SDK's existing interruptible cache-writeback selection for rolling
scanout. Keep all1600µs/DMA guards, cursor/scaler changes and rollback evidence.

## Evidence and bounded research

The [portable r20 failure record](R20-CLEAR-FAILURE.json) retains exact build,
installation, counters, completed recovery and original evidence hashes.

1. Installed r20 source8687f542/app5eca39c4 passes build/readback/CLI/startup.
   Case1 completes96→3→96; case2 keeps mode3 healthy but faults after returning
   to96, clearing and printing/reading a prompt:2164µs refill,1629µs copy,
   528µs queue wait. The runner stops all input; no320/raw/full-suite case runs.
2. After standing recovery, a separate four-cycle diagnostic samples selection,
   clear, text and glyph readback separately. Initial0→96 and its clear pass.
   The next3→96 selection and dwell pass, then VDU12 faults immediately:
   1634µs refill,1558µs copy; budget1/underrun1. Preserve both failures.
3. Pinned ESP-IDF5.5.5 b774170f, components/esp_mm/esp_cache_msync.c, holds a
   critical section during C2M writeback. Its Kconfig explicitly documents
   disabled interrupts during large writebacks and provides
   CONFIG_ESP_MM_CACHE_MSYNC_C2M_CHUNKED_OPS to admit interrupts between chunks.
   r20's SDK configuration leaves it disabled. Native indexed/PPA and the DPI
   direct-buffer path can write back an848×480×3-byte plane. No critical-section
   duration has been measured; the source mechanism is a bounded hypothesis
   until the physical candidate removes the reproducible failure.
4. The SDK warns about an ISR accessing the same buffer while a task's chunked
   operation is interrupted. Rolling strip_start reads the HDMI PSRAM source,
   performs cache synchronization and DMA2D copies into separate SRAM slots;
   strip composition writes those SRAM slots. Frame callbacks update metadata
   and notify workers. None writes the PSRAM plane being flushed by the task.
   Preserve acknowledged front/back ownership and existing live single-buffer
   tearing semantics. Revisit this selection if an ISR gains PSRAM writes.
5. The selected existing SDK chunker serializes task cache calls, releases its
   cache critical section between chunks, and retains the original ISR path.
   Choose16KiB, a multiple of the64-byte cache alignment, for the task quantum.
   This bounds one task-held interval; physical deadline validation remains
   mandatory. M2C invalidation and all data-integrity operations remain intact.

## Work and gates

1. Record r20's failure and completed recovery; leave startup and EMOS/onboard
   VDP unchanged. Preserve exact r19/r20 app images and complete readbacks.
2. Apply the existing SDK settings only in the rolling-scanout build branch:
   C2M chunking enabled and max length0x4000. The maintained native validator
   must verify both actual compiled macros; test rejection of disabled,
   missing/malformed and unqualified larger quantum settings.
3. Freeze a clean r20-based r21 source/build. All P4 C++/display/USB bytes in
   source, feature flags, tools, dependencies, memory policy and partition
   layout stay identical; only builder/validator source and those two effective
   SDK settings change. Independently verify composition and application flash.
4. First repeat staged wide selection/clear/text/readback, then the12 cursor/
   scaler cases including8/9/136 and96→3, then complete canonical paired
   qualification. Stop on first real fault and use standing recovery; never
   weaken1600µs or discard diagnostic failures to obtain a pass.
5. Verify normal CLI/cursors, entry modes, startup and support cleanup. Actual
   Author cursor-flash, mode8 height/aspect and other native visual review
   remain required. Do not change production selection/tag before acceptance.
