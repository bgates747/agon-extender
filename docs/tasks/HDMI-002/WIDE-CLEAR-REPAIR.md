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

## r21 result and r22 scope

1. R21 source d6fe9604/app9bdab7d9 passes native build, complete source/config
   comparison, application-only full-flash readback and actual CLI/startup proof.
   Isolated cycles0–3 pass. The fifth96 selection and dwell pass, but VDU12
   aborts1632µs (copy maximum1544µs, queue maximum484µs), budget1/underrun1,
   frame7007 stopped. The run stops at60.53 host-monotonic seconds. No320,
   raw-sector or complete-suite case runs. C2M chunking alone is insufficient.
2. Agon-only reset restores actual CLI twice but leaves the native fault/frame
   unchanged. P4 clean initialization thenAgon reset restores actual CLI twice,
   unchanged108Bstartup and fault-free mode0. No firmware change or test replay
   occurs during recovery. Keep the exact candidate/readbacks and both failures.
3. Pinned SDK esp_cache_msync still invalidates entire M2C planes and the
   INVALIDATE tail of C2M calls inside single critical sections. PPA's blend
   driver invokes full-row M2C before DMA; HdmiPpaIndexed invalidates again
   after blocking PPA completion. Treat this as an intentional upstream policy
   incompatible with the local deadline hypothesis, not an upstream correctness
   defect. No critical-section elapsed duration has been measured.
4. R22 retains r21 features and C2M selection. A project-owned pinned esp_mm
   derivative adds task invalidation chunking using the existing16KiB quantum.
   Preserve complete original validation before chunking, its one task mutex,
   ISR/non-yieldable paths, synchronization completion before buffer publication,
   all output ownership and1600µs/DMA guards. No EMOS/mainboard/startup change.
5. Pin all27 component files and the exact patch. Generate only in a fresh
   native project; keep the SDK pristine. Native validation must prove complete
   bytes, sole cache compile action, archive and ELF reachability. Host actual
   API/helper tests require the old full-plane negative control, contiguous
   bounded ranges, flags/overflow/alignment rejection and unchanged ISR/critical
   behavior. They do not measure hardware timing or prove cache coherence.
6. Freeze a new controlled source/build and independently verify installation.
   Require staged8wide cycles,12cursor/scaler cases and canonical25checks before
   handback for actual visual review. Retain/recover a first failure; no weaker
   guard, discarded informative failure or success claim from source alone.

## Current execution boundary

The [r22 preparation record](R22-PREPARATION.json) verifies clean source72bd4de0,
native build/compiled validation and independent comparison of5537 inputs.
Application1789856B/4a7277e7 is retained locally, not installed. Only six owned
recipe/metadata files differ from r21; the sole modified SDK source is the
pinned cache derivative. Twenty-two build tests and actual API/helper sanitizer
checks pass, including the original whole-plane negative control. Renderer,
USB, cursor/scaler source, flags, effective SDK settings and partition layout
remain identical. Actual cache hardware, deadline and optical proof remain.

The Author withdrew bench access while r22 built; the offline preparation
record remains immutable evidence of that boundary. On 2026-11-01 the Author
reports the bench restored and authorizes resuming testing and independent
work. Re-establish actual CLI, startup and installed component identities before
the r22 application-only installation. Then run the declared staged and complete
checks with first-fault preservation and standing recovery. Preserve normal
startup, unchanged companion firmware, exact rollback and the separate actual
Author visual-review gate. No automatic test invocation follows reset.
