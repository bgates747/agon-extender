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
Application1789856B/4a7277e7 was retained locally at that offline boundary. Only six owned
recipe/metadata files differ from r21; the sole modified SDK source is the
pinned cache derivative. Twenty-two build tests and actual API/helper sanitizer
checks pass, including the original whole-plane negative control. Renderer,
USB, cursor/scaler source, flags, effective SDK settings and partition layout
remain identical. Actual cache hardware, deadline and optical proof remain.

The Author withdrew bench access while r22 built; the offline preparation
record remains immutable evidence of that boundary. On 2026-11-01 the Author
reports the bench restored and authorizes resuming testing and independent
work. Fresh actual CLI, startup, complete EMOS ROM and listener identities pass.
Application-only installation independently verifies the exact app and unchanged
bytes outside its erase sectors. The third staged wide clear fails; the
[r22 failure record](R22-CLEAR-FAILURE.json) preserves the result and completed
standing recovery. No320/raw/full-suite case runs. Normal startup and companion
firmware remain unchanged. No automatic test invocation follows reset.

## R22 result and bounded phase diagnostic

1. The first two isolated cycles complete. Third96 selection/dwell passes;
   VDU12 faults1671µs against the unchanged1600µs guard. Copy maximum1551µs,
   queue maximum489µs, frame1064 stops. These maxima need not describe the same
   refill. Task writeback/invalidation chunking has not removed the failure.
2. Agon-only reset restores actual CLI but not stopped scanout. P4 clean
   initialization followed by Agon reset restores advancing fault-free mode0,
   USB devices and two actual CLI/listener/read/EXIT exchanges. Startup remains
   the exact108 bytes. No failed workload is replayed during recovery.
3. Pinned SDK `components/esp_lcd/src/esp_async_fbcpy.c` synchronizes descriptors,
   requests a sibling RX/TX pair through DMA2D and calls the user callback at
   receive EOF. `components/esp_hw_support/dma/dma2d.c` may queue requests when
   channels are unavailable; it frees channels before the user callback. The
   PPA BLEND driver also uses DMA2D and PSRAM. This source establishes shared
   resources, not measured queue, bus or IRQ contention.
4. `strip_start` performs destination and source cache operations before that
   API call. Existing copy timing starts before those operations, so it cannot
   isolate hardware transfer time. Prepare r23 from exact r22 with additive
   failed-refill phase evidence only: queue, preparation, source cache,
   API-submit-to-callback and completion work. All five durations must refer
   to the same failed refill and sum to its retirement-to-ready elapsed time.
   API-submit-to-callback includes driver setup/admission, DMA and IRQ delivery;
   do not describe it as measured hardware transfer time.
5. Retain r22 configuration, renderer, USB/input, cursor/scaler behavior,
   ownership and all deadline/abort checks. Publish only the first budget
   failure through the existing read-only status route; no per-refill logging,
   allocations, new service or extra IRQ exclusion. Use a larger bounded JSON
   buffer and retain overflow rejection. Phase timing itself has overhead;
   this is a diagnostic candidate, not a proposed timing fix or visual pass.
6. Freeze and independently compare that three-file source delta, build and
   verify an app-only installation. Run the separately identified staged wide
   diagnostic, stop on its first fault and preserve/recover it. Only passing
   earlier gates allows cursor/scaler or canonical qualification. Use measured
   phases to choose the next bounded remedy; do not shrink chunks or increase
   the guard without evidence.

## R23 result and driver-phase diagnostic

1. [The r23 diagnostic record](R23-CLEAR-DIAGNOSTIC.json) verifies source4a480eeb,
   app7f3b8101, native validation, exact three-file delta and complete app-only
   readback. Fourth isolated clear faults1726µs after three completed cycles.
   Same-job phases are queue6, preparation59, source-cache22,
   submit-to-callback1534 and finish105µs; their sum equals1726. No320/raw/full
   case runs. Agon-first and paired recovery restore actual CLI and mode0.
2. The source-cache call does not dominate this failed refill. Existing task
   chunking is not established as a remedy; retain it unchanged for isolation.
   The1534µs interval includes SDK descriptor synchronization, pool admission,
   transfer, IRQ delivery and driver cleanup. It cannot identify bus contention
   or delayed interrupt delivery independently.
3. Prepare r24 with a hash-pinned derivative of the exact selected SDK
   `esp_lcd/src/esp_async_fbcpy.c` (SHA256
   `6174cb19c4630769fe2dc9ed37f3d17abacc2d99d9743f1a35a0eb278e12e702`).
   Add read-only timestamp hooks after descriptor synchronization, on job
   selection, before DMA start and at the driver's completion callback. Filter
   by the one rolling-job context; other users of the copy API remain ignored.
   Do not change transactions, queues, priorities, bursts or cache operations.
4. Split the same failed refill's API interval into descriptor preparation,
   admission, channel setup, DMA-start-to-driver-callback and final callback
   handoff. Their sum must equal the outer API-to-strip-callback interval.
   The DMA interval still includes interrupt delivery/driver cleanup; retain
   that limitation explicitly. No per-transaction logging or new interrupt.
5. Generate only in the rolling build output. Verify complete derivative
   bytes, sole copy-source compile action and archive/ELF linkage; reject
   stale/duplicate/missing source. Keep the SDK pristine. Extend actual-body
   host checks for context filtering, phase order, both sums, strict deadline
   boundary and first-failure retention. Freeze clean source and compare all
   unrequested inputs/options before app-only deployment and staged diagnosis.
6. Stop/preserve/recover the next fault. Choose one bounded timing remedy from
   measured phases; do not change the1600µs guard or claim optical acceptance.
