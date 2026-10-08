# Full684 internal-memory diagnosis and remedy

## Executive summary

The allocation failure is proven and the latest684×384 candidate completes the
marked3600-update hardware Nurples run and normal cleanup. It retains22691bytes
of internal RAM during gameplay, compared with83bytes before the remedy.
Ordinary malloc now prefers PSRAM and the unchanged primitive queue's payload
also lives there; RTOS controls and scanout DMA storage remain internal.
The game sustains nominal60 updates/s with57% median active-work headroom and
no recorded timing or scanout faults. The ordinary game's menu, loaded mode
changes, keyboard Escape and return to a responsive MOS prompt also pass.
The latest candidate is left installed for Author play review. Automatic Agon
SD admission after exit still rejects in ExCom; switching through EMOS to Legacy
restores access without reset. This is experimental evidence, not production
promotion or a claim of broad gameplay/service qualification.

## Evidence and source contract

1. Diagnostic build `rgb-001-r04-b2026-10-07-14-56-40Z`, factory SHA256
   `3c6f4f8f93102969172e57380e54c04b956b39c8c894a143f93836562a7a3bb6`,
   changes only the explicit IDF allocation-failure-abort configuration relative
   to the prior full684 candidate's runtime behavior. Compiled configuration and
   all flash segments verify. The retained hardware-r03 deterministic game is
   unchanged, with a new output directory/tag. This deliberate abort run is
   diagnostic evidence, not a performance sample.
2. Serial and a core preserved before factory recovery identify
   `createBitmapFromBuffer → make_shared_psram<Bitmap> → _Sp_counted_base`
   mutex construction, `pthread_mutex_init → xQueueCreateMutex → pvPortMalloc`.
   Requested size84bytes; capability mask0x804 means internal,8-bit-capable RAM.
   The crash task is processLoop, not an interrupt. This substantiates the
   allocation mechanism suspected in [the earlier failures](FULL-WIDE-RESULTS.md).
3. Pinned IDF5.5.5 commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`:
   `components/freertos/heap_idf.c` explicitly requests internal RAM for RTOS
   objects. `components/pthread/pthread.c` creates the mutex's semaphore there;
   failed creation returns EAGAIN. Toolchain14.2.0's selected RISC-V C++ library
   uses `_S_mutex` for shared-pointer control blocks. Its gthread initialization
   wrapper discards the failure return. No toolchain, SDK or stock-VDP workaround
   is introduced here; the remedy must supply sufficient internal memory.
4. IDF `components/heap/heap_caps.c` selects ordinary malloc placement by
   `CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL`. A value0 prefers PSRAM for nonzero
   ordinary allocations, with documented fallback; it does not move explicitly
   internal allocations. The previously tested1024-byte threshold still allowed
   small objects to consume the internal heap. The reserve remains32768bytes.
5. Official buffered-command contract, reference agon-docs commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`:
   [buffer blocks and bitmap creation](../../../../../agon-docs/docs/vdp/Buffered-Commands-API.md),
   implemented by [buffer ownership](../../../vdp/video/buffers.h),
   [PSRAM allocator](../../../vdp/video/types.h), and
   [bitmap creation](../../../vdp/video/vdu_sprites.h).
   Buffer lifetime, bytes, commands, shared ownership and synchronization remain
   unchanged. Reference checkout source was not modified (an existing untracked
   desktop metadata file was left alone).

The ignored evidence silo is `agents/sprite001/integration/wide684/alloc-diagnosis`;
it retains serial, raw core, exact-ELF decode, source/build identities and SD
preservation records. The earlier848 image is a service-recovery image only:
Author explicitly reports it does not provide acceptable hardware Nurples.

## Validation boundary

Use the existing3600-update marked hardware Nurples fixture, then verify ordinary
service access and clean buffer destruction/return. Preserve the old trajectory
checkpoints and compare eZ80 active-work budget separately from P4 scanout.
Restore original startup/configuration, leave only a successfully tested candidate
installed, and identify that exact image before requesting manual gameplay.
Remaining steps and authorization belong to [HDMI-002](../HDMI-002.md), not this
results record. Wider qualification and production promotion remain separate.

## First placement result and mode-transition boundary

The0-byte ordinary-malloc preference candidate
`rgb-001-r04-b2026-10-07-15-09-19Z` completes the marked3600-update game at nominal
60/s and exits normally, with no scanout faults or HTTP failures. Median active
work42.875% of a frame; p95 53.25%. This fixes the demonstrated cleanup failure,
but only3835bytes of internal memory remain during gameplay. Original startup
and fixture configuration were restored/readback verified before the next candidate.

The timing fixture deliberately omits the ordinary game's mode changes. Stock
single-buffer primitive queues contain1024 ×18-byte elements; retained-old/new
controller staging can require another18432-byte payload with assets still
loaded. The first placement pass alone therefore does not establish ordinary
interactive readiness.

The second bounded P4 accommodation moves only each primitive queue's payload to
PSRAM. Its `StaticQueue_t` stays internal; IDF's unchanged xQueueCreateStatic and
vQueueDeleteWithCaps own queue construction/destruction. Capacity, item bytes,
FIFO order, task scheduling, three scanout slots and all stock drawing remain
unchanged. P4 StockBoundController::drain calls getPrimitive from the drawing
task; the classic VGA getPrimitiveISR path is not used in this composition.
The adapter is compiled only for physical P4 rolling builds. Default/host and
upstream reference trees are unchanged. The adapter pairs static queue creation
with pinned IDF's implementation of `vQueueDeleteWithCaps`: it retrieves both
static buffers, deletes the queue and frees both through `heap_caps_free`.
Review this implementation dependency when updating IDF; capability choices need
not match between control and payload. No upstream allocation-failure patch is
introduced.

## Comparable deterministic runs

Worst internal-memory headroom first. All three runs use the same hardware
Nurples companion and3600-update trajectory; the old83-byte control suppresses
aggregate P4 timing markers and is not a fully matched diagnostic run.

| Measurement | Original684 control | PSRAM-first malloc | Plus PSRAM queue payload |
|---|---:|---:|---:|
| Build timestamp,2026-10-07 UTC | 13:47:13 | 15:09:19 | 15:27:40 |
| Internal free RAM during loaded capture, bytes | 83 | 3835 | **22691** |
| Aggregate P4 timing markers | Disabled after marked-run failure | Enabled | Enabled |
| Measured game updates | 3600 | 3600 | 3600 |
| Game update rate, nominal updates/s | 60 | 60 | 60 |
| Median active work, percent of60Hz budget | 43.000% | 42.875% | **43.000%** |
| Active-work p95, percent of60Hz budget | 53.250% | 53.250% | **53.333%** |
| Median active-work headroom | 57.000% | 57.125% | **57.000%** |
| Fault / late timing rows | 0 / 0 | 0 / 0 | 0 / 0 |
| Ordinary buffer cleanup | P4 crash | Pass | Pass |

Compared with the first placement remedy, queue placement adds18856 internal
bytes. Median active work changes by+0.125 percentage points of the frame budget
(+0.292% relative to42.875%). This single-run difference does not establish a
performance regression or improvement; the remedy targets memory reliability.
All3600 records match the retained original control in update number, state,
phase, actor/projectile counts, map row and RNG state. This is the existing
trajectory, not a32-sprite stress qualification.

The final build is `rgb-001-r04-b2026-10-07-15-27-40Z`, factory SHA256
`8a0bcbe2f591f0728629fffe0cf7894fb5cd71b39fe5dfa8c2d1e036a3fc3cd6`.
Independent flash readback verifies all four segments. Heap allocation abort is
off in this candidate. The result file SHA256 is
`da31b162d86dc0eed95c652f5522a1c9d925fd36eb134cb38cfeb1ba3ddcc16c`.
Exact manifests, logs and originals are retained in the ignored
`agents/sprite001/integration/wide684/queue-headroom` evidence directory;
the Agon result remains at `/agents/extender/results/spr01-w684-queue/nurples3600.bin`.

## Timing scope and output checks

1. eZ80 timing uses nominal72000 PRT counts/s and120 raw MOS units/s, observed
   in increments of2. The current calibration observes35733 PRT counts over60
   raw MOS units. Nominal conversion is retained for comparability, not asserted
   as externally calibrated wall time. A60Hz budget is1200 PRT counts.
2. Active work median516 counts (7.167ms), p95640 (8.889ms), maximum842
   (11.694ms,70.167% of budget). Total loop median1191 counts, maximum1193;
   no over-budget sequence. Final drain43counts. Percent headroom is100 minus
   active-work budget percentage; it is not a rendering-completion measurement.
3. The P4 aggregate window lasts60.059452s, with3608 output updates/scanouts.
   Six full10s serial windows show60.067–60.071Hz. Maximum observed strip refill
   902µs, copy814µs, sprite composition277µs, minimum ready lead1121µs.
   Invalid-block, underrun, sequence, late, overlap and fault counters stay zero.
4. P4 draw phase totals15.166s (maximum5.919ms per observation); HDMI preparation
   totals1.565s (maximum1.047ms); cache phase0.556s (maximum0.468ms).
   These are separately scoped P4 phases, not eZ80 loop time or wire latency.
5. The fixture emits aggregate-window markers but no frame-ID pixels. Therefore
   `marker_valid=0` and `marker_invalid=3608` denote absent per-frame IDs, not
   scanout corruption. No distinct rendered-game-frame rate is inferred.
6. No browser video client is connected during these tests. Host renderer
   regression, ASan/UBSan rolling scene/ownership tests and11 build-selection
   tests pass; physical build/source/silicon/configuration checks pass.
   This does not qualify browser streaming, all video modes or long-duration play.

## Ordinary-game smoke and handback

The Pi independently reads and hashes the existing36493-byte
`/mystuff/arcade/nurples-hardware.bin` before running it:
`3ba82ef604cb75fdd35b42ff5890504a3c4e74c28bfc7f83b7208130276cfcd1`.
The test uses normal EMOS commands and the admitted remote keyboard path;
it modifies no game bytes or assets and performs no reset during gameplay/exit.

| Gate | Evidence / result |
|---|---|
| Ordinary title and joystick choice | Pixel-derived screen text shows the actual joystick prompt; P4 reports mode8,320×240 |
| Start and loaded mode transition | Actual start prompt observed; Enter enters mode20,512×384, RGB888 panel-direct rendering |
| Loaded gameplay and input | Twelve-second ordinary smoke; P4 responsive, keyboard ready with zero held/pending keys |
| Escape and buffer cleanup | Actual “Thank you for playing” screen and MOS prompt observed; original mode0 restored; no P4 reset/panic |
| CLI operation | ECHO command produces its separate output and returns to the prompt |
| Automatic SD access in ExCom after exit | HTTP503; rejected as ineligible, with phase1/idle and no valid recent admission poll; unresolved, not a service pass |
| Recovery through supported EMOS command | `EMOS LEGACY`, then HEAD `/autoexec.txt` returns200 without resetting either processor |

The smoke script's overall assertion fails at its final ExCom HEAD check. Retain
that failure alongside the passing preceding gates and the separate Legacy
recovery receipt; do not relabel the original run as an unqualified pass. Serial
shows no scanout fault, allocation failure or panic; observed internal free RAM
is at least22519bytes during this smoke and returns to88707 after exit. That
supports recovery from the former memory crash, but does not prove the cause of
the separate ExCom admission failure. Its investigation stays bounded under
HDMI02-M02c; no speculative EMOS or transport patch is made here.

Original38-byte startup and128-byte fixture configuration are restored by full
readback; their SHA256 values remain respectively
`7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5` and
`1128fc600505f64cc334fcbff61d0e031be90416b864ce05c4ec52a15cb62d4f`.
Ordinary software/hardware game binaries, assets and EMOS remain unchanged.
The latest684 candidate remains installed at an idle Legacy MOS prompt for
manual `EMOS EXCOM`, then loading/running the hardware game from
`/mystuff/arcade`. The foreground listener is stopped. The old848 image is not
the playtest handback. Author review of this exact memory remedy, longer play,
the previously noticed slight tearing, other modes and production promotion
remain outstanding.

## Author play review and pause follow-up

The Author subsequently calls the output beautiful. A thin horizontal tear
remains about one-fifth down, roughly one scanline high. This supersedes the
earlier approximate one-third location as the latest observation, without
establishing whether the line is fixed in time or a moving tear. The requested
temporary game-only P pause/resume experiment is scoped in
[SPRITE-001](../SPRITE-001.md). Keep the tested P4 image unchanged for that
comparison. Broad qualification and an agreed production version remain
promotion dependencies; positive gameplay review does not silently promote an
experimental image or waive the remaining service/tearing questions.

The subsequent Author comparison finds that the tear disappears when paused,
while hardware Nurples on mainboard VDP has no observed tear. This narrows the
investigation to update/scanout interaction; it does not identify which update
or synchronization boundary causes the tear. P4 scanout and hardware-sprite
composition continue during the pause. The background remains single-buffered.

Ordinary Nurples in ExCom now shows laser bolts up to the top of the playfield.
The Author suspects hardware-sprite selection. A source check against the
installed archive finds separate software/hardware paths and no implicit
conversion; ordinary binary preservation was verified during deployment.
Live flags were not read, so a retained global prefer-hardware setting from
another program remains unexcluded. Full observations and the precise reset
semantics are recorded in [SPRITE-001](../SPRITE-001.md). No bench state was
changed to collect this source review.

The later Author-requested rollback to the pre-hardware-sprite full848 build
reproduces the upper-playfield laser visibility defect with the unchanged
ordinary Nurples binary. This confirms the newer full684 combination's visible
improvement, without isolating which firmware change produced it. See the
comparison record in [SPRITE-001](../SPRITE-001.md). The earlier848 build remains
installed for this comparison; the tested full684 return image is retained.

Subsequent Author-requested restoration/test returns the exact full684 image to
the bench. A five-second ordinary Nurples run exits to mode0,640×480 with an
80×60 text grid. Full logical farewell text is present in readback. The fixed
684×384 output center-crops48 pixels (six text rows) from each vertical edge;
the earlier848×480 output fits mode0 without cropping. This explains the reported
missing upper text without implicating game cleanup. Full684 remains installed
at the post-game ExCom prompt. [SPRITE-001](../SPRITE-001.md) retains the bounded
diagnostic, capture limitations and output-policy boundary; no code remedy yet.
The Author visually confirms this reproduction and the six-row count.
