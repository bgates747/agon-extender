# C4 — GMF esp_player handoff and pacing review

## Executive summary

**GMF manages overload through bounded handoffs, blocking and selective video
frame discard; it does not demonstrate a missing rendering-speed optimization.**
Extender already has bounded snapshot ownership. The useful distinction is
which work may be skipped: stale presentation snapshots may be superseded,
whereas VDP commands and game rendering cannot be dropped to claim parity.

GMF's player acquires a decoded frame before pacing it, and retains ownership
through the renderer call. Therefore its pacing does not avoid the cost of
producing that frame. This differs from our deferred fallback, which must pace
snapshot admission before expensive composition. Its millisecond/tick timing
and early-release tolerance are not a precise60Hz cadence implementation.

**Next avenue:** retain explicit produced/leased/superseded/sent accounting and
measure wait separately from active work under existing P01/P02/P06. Do not
import the player or adopt its task priorities/cache policy. No new performance
measurements or proven Extender defect. C5 remains the next source candidate,
pending review; RLE stays afterward. No build, flash, reset or firmware test.

## 1. Scope and provenance

Contract94e6aee. Espressif esp-gmf commit
`4e477b7c5352a54e9a64cdafe3839abbaf143940`, esp_player1.0.6.
Read player_data_bus.c, player_sync.c, player_video_render.c, defaults/manifest,
plus official bus documentation, bus factory, OAL allocation and public renderer
header/implementation. Hashes in [provenance.json](provenance.json).

This is a bounded source review, not full codec/backend/ISR/queue qualification.
The manifest permits dependency version ranges; same-tree sources describe the
reviewed implementation, not proof of a resolved production build. No matching
mainboard/Extender workload or render-latency distribution exists here. Vendor
400/250MHz codec figures cannot predict our360/200MHz application behavior.

## 2. Handoff and pressure

| Stage | Inspected behavior | Consequence |
|---|---|---|
| Timestamp metadata | Fixed-capacity queue holds PTS and remaining bytes under mutex | Bounded storage; not the payload queue itself |
| Write | Acquire delegates to underlying bus; release publishes metadata, unlocks, then releases payload | No metadata mutex held over underlying publish wait; atomicity depends on producer/reset contracts |
| Read | Acquire payload first, then consume matching metadata under mutex | Partial reads can consume several metadata entries; underflow logs and resets PTS to zero |
| Failure | Full metadata queue returns failure; failed payload release rolls back metadata tail count | No magical lossless overload recovery; caller contract matters |
| Reset/destruction | Metadata reset and inner reset are separate; wrapper destroy frees its queue/mutex, not inner bus | Requires lifecycle coordination; do not infer concurrent-reset safety |
| Render | Acquire input with maximum wait; pace/check/drop; stream write; release input | Holds a payload during pacing, so upstream can back up |

Official [data-bus guide][busdoc] distinguishes copying byte ringbuffers from
block/pointer handoffs. The inspected factory dispatches to these different
implementations. Consequently, generic acquire/release names do not establish
zero-copy behavior or bounded blocking. This review does not certify the
underlying implementations' every race or allocation path.

Player defaults put video decode on core0 and render on core1, priority5, external
stacks requested. OAL malloc/calloc explicitly request PSRAM when
CONFIG_SPIRAM_BOOT_INIT is enabled; no automatic internal fallback appears in
those branches. That is policy, not evidence memory contention disappeared.

## 3. Clock and discard behavior

1. **Seek/stop:** render gates reject frames during seek/stop; acquired payloads
   are released. This is deliberate discontinuity handling, not a faster render.
2. **Audio master:** video older than audio render PTS by the configured delay
   threshold is discarded. Audio-master smoothness can therefore coexist with
   missing video frames.
3. **System anchor:** maps media PTS to a wall-clock anchor, waits for early
   frames, reanchors when over1000ms late, and drops sufficiently late frames
   during speed>1 playback. Threshold is at least30ms. The reanchor branch
   precedes the accelerated-drop branch; it is not a universal late-frame drop.
4. **FPS helper:** truncates1000/fps to integer milliseconds, uses RTOS-tick wall
   time and vTaskDelay, and accepts an interval already at70% of its target.
   At a requested60fps the stored interval is16ms, not16.667ms. This source
   arithmetic is not a measured realized frame rate.
5. **More than one pacing layer:** player skips its FPS helper when its master
   clock gate is active. Separately, renderer stream_write performs its own
   rate control when stream fps is nonzero, using write count/time and tolerance.
   Do not assume one delay is the entire pacing contract.

Source functions: `sync_master_clock_pace`, `player_sync_wait_for_next_frame`,
`player_sync_video_render_frame`, `player_sync_video_fps_sync`; renderer
`video_render_stream_rate_control`. Player supplies stream `.cached=false`;
renderer holds its stream mutex across processing in this mode. Its cached mode
can instead allocate/grow and copy into retained storage, but the inspected
player does not select that mode. Backend presentation completion remains
distinct from a successful processing call; full backend ownership certification
is outside this review.

## 4. Limits worth preserving

1. Player ignores the return of esp_video_render_stream_write before releasing
   its input. A processing failure is not necessarily propagated as a failed
   player job here; count actual outcomes rather than calls.
2. Metadata rollback after releasing the mutex relies on surrounding producer
   ordering; multiple simultaneous writers/reset interleavings were not proved
   safe. This is an unqualified reuse assumption, not a demonstrated stock bug.
3. Maximum waits are used in the wrapper and render port. A bounded queue does
   not itself provide bounded latency; abort/stop and backend behavior matter.
4. The source's modified-MIT license requires separate review before importing
   code. This task imports no firmware source into product code.

## 5. Application to our next measurements

Retain Extender's immutable leases and bounded latest-frame policy. For a slow
consumer, account separately for snapshots produced, unavailable/deferred,
superseded before leasing, leased, sent, failed and still owned. Preserve every
VDP command and the deterministic rendering oracle. Measure where production
waits and whether that wait blocks drawing, rather than interpreting browser
FPS as game-render FPS. No measured speedup or mainboard percentage is claimed.

The Author's selectable-cadence fallback remains under P06e. GMF reinforces
that pacing after production and dropping after decode cannot reclaim work
already spent. If that fallback is later selected, schedule capture admission
first, with fractional/absolute timing appropriate to the chosen target rather
than copying this player's integer-ms tolerance. No implementation authorized.

[busdoc]: https://github.com/espressif/esp-gmf/blob/4e477b7c5352a54e9a64cdafe3839abbaf143940/docs/en/gmf-framework/gmf-core/gmf-core-databus.rst

Primary source root: [pinned esp-gmf](https://github.com/espressif/esp-gmf/tree/4e477b7c5352a54e9a64cdafe3839abbaf143940).
Player paths: `packages/esp_player/src/sync/`, `src/video/player_video_render.c`,
`src/core/private_inc/player_defaults_cfg.h`; renderer paths:
`packages/esp_video_render/{include/esp_video_render.h,src/esp_video_render.c}`;
bus/OAL paths: `gmf_core/{data_bus/esp_gmf_new_databus.c,oal/esp_gmf_oal_mem.c}`.
