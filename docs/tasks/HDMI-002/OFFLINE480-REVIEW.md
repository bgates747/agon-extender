# Wider rolling scanout — offline review

The old runtime can stop a safe three-buffer refill sequence prematurely. A
host test reproduces its overlap fault while neither its time limit nor its
buffer-generation check has failed. The proposed correction permits one waiting
refill, still with only one DMA2D operation in flight. This is a demonstrated
code limitation and a plausible explanation of the wider-mode failure, **not
proof of the physical blue screen's cause**. Hardware validation is pending;
the Author assigned the bench to another project.

## Scope and source authority

1. Official mode/swap semantics remain those in
   [Agon screen modes](../../../../../agon-docs/docs/vdp/Screen-Modes.md), commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. No VDU/API, EMOS, game, palette,
   resolution, clock or mode-selection changes are part of this tranche.
2. The pinned ESP-IDF baseline is
   `b774170ff46c393eeb5e495ea37936038d3f4f4f` (5.5.5).
   [DPI driver](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_lcd/dsi/esp_lcd_panel_dpi.c),
   [DW-GDMA driver](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_hw_support/dma/dw_gdma.c),
   [DMA2D driver](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_hw_support/dma/dma2d.c), and
   [asynchronous framebuffer copy](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_lcd/src/esp_async_fbcpy.c)
   define the inspected callback, descriptor and lifetime behavior.
3. The local implementation is
   [strip runtime](../../../vdp/video/extender/display/rolling/strip_runtime.inc)
   and its [isolated DPI generator](../../../vdp/video/extender/display/rolling/patch_dpi.py).
   The generator still hash-checks and derives exactly one translation unit;
   official source/SDK checkouts remain unmodified.
4. Espressif's [cache synchronization guidance](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/system/mm_sync.html)
   supplies supporting context; pinned source controls the implementation.
   DW-GDMA's descriptor getters return uncached addresses, so no missing
   descriptor-cache flush was established here. Existing pixel cache handoffs
   remain necessary and unchanged.

## Geometry and available time

Both carriers retain 34.285714 MHz pixels and 1,104×517 total timing. A physical
line is nominally 32.2 µs; a 32-row strip spans 1,030.4 µs. These calculations
describe signal geometry, **not measured interrupt deadlines**: FIFO prefetch,
interrupt latency and bus contention can change callback spacing.

| Property | 684×384 carrier, mode 20 | 848×480 carrier, mode 96 |
|---|---:|---:|
| Active 32-row blocks/frame | 12 | 15 |
| SRAM slots | 3 | 3 |
| Active bytes/slot | 65,664 | 81,408 |
| Bytes scanned/frame, RGB888 | 787,968 | 1,221,120 |
| Logical background bytes copied/frame | 589,824 (512×384) | 1,221,120 (848×480) |
| Nominal interval between active block retirements | 1,030.4 µs | 1,030.4 µs |
| Nominal time until a retired slot is needed again | 2,060.8 µs | 2,060.8 µs |
| Vertical blank interval | 4,282.6 µs | 1,191.4 µs |
| Existing callback-to-ready guard | 1,600 µs | 1,600 µs |

The AUTO build reserves the 244,224-byte maximum allocation for both carriers.
The wider game fixture still draws the original 512×384 game, but its logical
canvas is 848×480; DMA2D therefore copies 107.03% more background bytes per frame
than mode 20. The new queue does not reduce that traffic or create more bandwidth.

## Findings

O-F01 — **Premature overlap abort reproduced.** The old scheduler permits no
waiting refill. If block 3 takes 1,130 µs to refill, the request for block 4
arrives after about 1,030 µs and aborts immediately. Block 3 is not needed until
the next block boundary, and a shorter following copy can safely catch up.
The old code's abort produces the same combination seen in retained evidence:
a contained fault with no late-generation or over-budget count. However the
physical run did not retain its overlap counter after the stop, so this remains
a hypothesis for that event. The saved maximum refill was 1,130 µs.

O-F02 — **Fault ordering was lost.** A deliberate scanout stop can itself starve
DSI and cause an underrun. Previously the HTTP status omitted overlap, cache,
invalid-block and sequence detail and retained no first reason. A responsive
HTTP endpoint and a blue image do not establish a CPU crash or prove that raw
memory bandwidth was the initiating failure.

O-F03 — **Sequence mismatch was counted but allowed to restart.** The generated
driver previously rearmed all descriptors even if the number of received block
events disagreed with the geometry. After a missed/coalesced event, software's
slot generation may no longer describe DMA consumption. The candidate contains
this mismatch instead of silently advancing ownership. This is host-tested
safety behavior; no recorded physical sequence error is claimed.

O-F04 — **Teardown must suppress waiting work.** With the new queue, stopping
must prevent another copy or ready-slot publication after teardown begins,
while joining the one active DMA2D transaction before releasing memory. Tests
exercise cancellation and avoid using a deleted DSI handle from late completion.
No new task, timer or ISR allocation is introduced.

Both descriptor layouts are integral, aligned and within the existing 15-block
limit. Both block counts divide evenly across three slots. No four-bit overflow
or missing descriptor-cache flush was found. This does not rule out hardware
prefetch effects, coalesced interrupts, bus contention or an independent problem
in the previously failed mode transition.

## Candidate behavior

1. Keep one DMA2D copy active and at most one refill waiting. A tiny critical
   section protects request ownership; copying, cache synchronization and sprite
   composition stay outside it. A further request or a missed generation still
   stops scanout. No unbounded queue or concurrent fbcpy handles are added.
2. Count waiting time in the unchanged 1,600-µs limit, measured from the original
   refill request. Publish a slot's ready generation only after all work and the
   limit check pass. An expired/cancelled slot is never advertised as ready.
3. Start a waiting copy from the previous EOF callback. The pinned DMA2D driver
   releases RX/TX channels before invoking user EOF; the single retained fbcpy
   descriptor set can then be reused. This does not authorize multiple clients
   concurrently using fbcpy's static transaction configuration.
4. Retain the first observed fault atomically; a subsequent DSI underrun cannot
   overwrite it. HTTP and periodic serial status report its reason/detail,
   queue count and maximum waiting time, with existing detailed counters.
   Code numbers are defined in
   [strip_probe.h](../../../vdp/video/extender/display/rolling/strip_probe.h):
   0 none, 1 cache, 2 deadline, 3 queue overflow, 4 copy submission, 5 generation,
   6 invalid descriptor, 7 underrun, 8 sequence. A reader racing the short
   publication sees 0 until the first reason is fully published.
   `first_error` is the SDK error for cache/submission, elapsed microseconds for
   deadline, requested generation tag for queue overflow/late generation,
   observed block count for sequence, and 0 for invalid descriptor/underrun.

## Validation boundary

The [runtime regression](../../../tests/display/rolling_runtime_test.py) includes
the maintained C implementation and extracts the generated full-frame callback
verbatim. Simulated DMA completes at controlled times, with the same single
transaction lifetime as pinned IDF. The old source reproduces the premature
abort; the candidate completes the same delayed sequence in both geometries.
It also exercises 1,024 frames per geometry with periodic delayed copies and
row-content checks, queue overflow, true deadline miss including queue time,
unsafe slot reuse, cache/submission failure, fault ordering, lost block sequence,
and stopping with a waiting copy. Address/undefined-behavior sanitizers pass.

These tests cannot reproduce physical AXI/FIFO/cache/IRQ timing. The old blue
screen and native-mode transition still require hardware checks when the Author
returns the bench. Retained evidence and logs are under the ignored
`agents/hdmi002/offline480` silo. No installed-state record or production
selection is changed.

## Build and closeout

Experimental **rgb-001-r09-b2026-10-07-22-25-41Z** compiles and passes native
source/link/configuration validation. Factory SHA256:
`70da9fca3f51ecff9812bd85d9237a20210bfd71ac4b58bf4251d97ce84fe376`.
The source snapshot and all manifest artifacts pass hash verification. This is
an unflashed development build, not an installed or qualified release.

| Check | Outcome | Scope |
|---|---|---|
| Retained old runtime, delayed-copy control | Expected early abort reproduced | Demonstrates the limitation before the remedy |
| Actual runtime and generated frame callback, ASAN/UBSAN | Pass | Both geometries;1024 simulated frames each plus fault cases |
| Existing scene/mailbox/pixel checks, ASAN/UBSAN | Pass | Fixed848/684/512 and AUTO, immutable sprites and composition |
| Existing HDMI service scheduling | Pass | Swap/frame ownership and joined service shutdown |
|12 build-selection/metadata checks | Pass | Experimental profile and driver/source selection |
| Full target build and native validator | Pass | Actual RISC-V compilation, derivative identity and link closure |
| Physical Nurples/mode transitions/input | **Pending** | Bench occupied; no hardware accessed |

The runtime test's `--report` writes source identities, UTC start/end and host
wall-clock seconds durably; the final retained run takes about0.83seconds for
compile plus simulation. This is not game or DMA performance. Runtime and build
logs, before-source copies and exact build inputs remain in the evidence silo.
Existing source work stays uncommitted. Another project's shared bench handoff
was preserved unchanged.
