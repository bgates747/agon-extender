# C3 — NINA P4 display capture review

## Executive summary

**Useful confirmation of buffer ownership and short display exclusion; no
missing Extender optimization established.** NINA takes an owned RGB565 LVGL
snapshot under the display lock, then releases that lock before copying, JPEG
encoding and HTTP sending. Extender already keeps transmission outside its
native drawing and snapshot-pool locks. NINA serves occasional lossy screenshots,
not continuous lossless palette frames, so its architecture supplies no matching
FPS or mainboard comparison.

The second useful lesson is to reserve large long-lived buffers before heap
fragmentation. Extender already preallocates snapshot slots. NINA still creates
a snapshot per request and can allocate fallback encoder buffers. Its source
comment attributing an extra copy to DMA alignment is not sufficient evidence:
our IDF5.5.5 JPEG allocator explicitly aligns output, but uses ordinary PSRAM
allocation for input. Do not add such a copy or cache flush to Extender.

Two concrete source concerns limit diagnostic reuse: screenshot send errors are
ignored when declaring success, and deletion from the performance timer hash
table can hide a colliding live entry. No upstream patch or hardware reproduction
was attempted. **Next avenue:** retain existing P01c/d lock/copy/send attribution,
including buffer residency and allocation fallback counts; review C4 next if
authorized. No build, firmware test, flash, reset or new timing measurement.

## 1. Scope and sources

Frozen contract1dfba3f. NINA revision
`c7b34400f7373cad94caee7493413a8ec5b58864`; source hashes in
[provenance.json](provenance.json). Inspected screenshot handler, selected
performance instrumentation, JPEG utility registration, dependency/default
configuration and host-test documentation. Not a full application, BSP, LVGL
renderer, network stress suite or PPA audit. Our installed JPEG driver is
IDF5.5.5; NINA's actual built dependency graph was not reproduced.

## 2. Capture and lifetime trace

| Stage | NINA source behavior | Implication for Extender |
|---|---|---|
| Boot reservation | Persistent encoder plus input reserve screen_size squared times2 and512KiB output | Avoids repeated large allocations; comment reports past fragmentation failures, not our measured failure |
| Admission | Screenshot mutex,5000ms acquisition timeout | Serializes shared buffers; not a60Hz queue or bounded total request duration |
| Capture | Display lock,5000ms acquisition timeout; lv_snapshot_take; unlock | Snapshot production still occupies display exclusion; timeout does not bound time held |
| Copy | Row-by-row RGB565 stride-aware copy into encoder input, then destroy snapshot | Separate lifetime and packed stride; adds read/write traffic outside display lock |
| Encode | RGB565, YUV422, quality90; synchronous process call, possible output retry | Lossy accelerator path differs from our lossless RGB222 stream |
| Send | HTTP response using encoded storage while screenshot mutex remains held | Slow client delays next screenshot but does not directly retain display lock |
| Cleanup | Destroy outstanding snapshot, free temporary input/output, release screenshot mutex | Persistent buffers survive requests; failure paths converge on cleanup |

Source: [web_handlers_display.c][screen], lines513–702. The startup-before-display
allocation order is asserted in its comment, not independently traced through
application boot here. Failed/missing/undersized input uses a temporary buffer;
missing output uses a temporary half-raw-size buffer. Retry with raw-size output
occurs only on ESP_ERR_INVALID_STATE and when no temporary output already exists.
It is not a universal resize-until-success loop. Snapshot allocation itself
remains per-request; permanent encoder storage does not make capture allocation-free.

## 3. Cache/DMA qualification

NINA reports that directly feeding snapshot data produced stale/banded images;
this is the upstream author's observation, not our independent reproduction or
a proven diagnosis. The copy also normalizes row stride and changes allocation
and lifetime, so alignment is not the only variable.

Official [Espressif JPEG documentation][jpeg] requires suitable output-buffer
alignment and stable input through processing. Its published performance table
is codec-only, without other application modules, and is not screenshot or web
FPS. Stable HTML resolved to6.1. Installed5.5.5
`components/esp_driver_jpeg/jpeg_encode.c` provides our version-specific check:

1. `jpeg_alloc_encoder_mem`370–389 rounds/aligned-allocates OUTPUT in PSRAM;
   INPUT uses heap_caps_calloc with PSRAM capability, without explicit alignment.
2. Processing writes back input cache, and invalidates DMA-produced output
   after completion. These belong to the driver/accelerator boundary.
3. ESP_ERR_INVALID_STATE has multiple sources, including encoded-output overflow
   and header-alignment checks. The application's retry treats it as overflow;
   that classification is broader than our inspected SDK contract.

This does not establish an upstream image bug. It prevents copying an explanatory
comment into a new requirement for our CPU snapshot and Ethernet path. Preserve
the existing C1 DMA-boundary findings; no additional copy/flush is justified.

## 4. Diagnostics and source concerns

1. **False send success:** screenshot handler689 ignores httpd_resp_send's return,
   logs success and sets ret=ESP_OK. A failed send can therefore be reported as
   successful. This limits reliance on application logs, not the legitimacy of
   its ownership design.
2. **Timer collision/deletion defect:** perf_monitor.c81–127 uses linear probing
   and stops lookup at an empty slot. Stop deletes an entry by setting key=NULL.
   If A and B collide, B is stored after A; stopping A leaves a hole, so stopping
   B terminates early and loses the measurement. This is a deterministic source
   counterexample; frequency in NINA's real pointer layout was not measured.
3. **Concurrency not certified:** timer table and counters have no visible
   protection in these helpers. Being task-context-only does not establish
   single-writer access across cores. Actual callers were not exhaustively
   audited. The failed-allocation hook's volatile increment is not atomic under
   concurrent callers; ROM UART printing also has a cost even without malloc.
4. **Instrumentation placement:** counters/start times reside in PSRAM. Monitoring
   PSRAM contention using those counters adds memory traffic. Useful heap totals,
   minima and largest-free-block sampling exist, but they are not automatically
   low-overhead or per-operation allocation accounting.
5. **Dependency caution:** manifest pins esp_lvgl_port2.8/LVGL9.5 and uses hosted
   Wi-Fi components plus an in-tree BSP. Defaults request PSRAM XIP and allow
   network allocations there. These differ from our retained build; do not copy
   them as throughput settings. Its IDF6-only callback comment must not override
   C1's actual installed5.5.5 header inspection.

No issue was modified or sent upstream. Host-test shims explicitly are not an
ESP-IDF/RTOS implementation; host passing tests would not prove actual lock,
cache or sustained-output performance. The separate network stress harness
was not run or fully audited.

## 5. Disposition and proposed discriminating check

NINA's core ownership separation already exists locally. A rewrite to imitate
its single screenshot mutex would not remove our native row preparation costs,
and could reduce overlap. Its JPEG output does not meet our raw/palette fidelity
contract. Boot reservation is worth retaining, not newly introducing.

Existing P01c/d should, when authorized, separately attribute native/display
lock wait and hold, snapshot production, conversion/copy, allocation fallbacks
and network send. Reuse current deterministic controls and oracles; keep
measurements bounded, outside live logging, and overhead-checked. Record actual
capabilities/addresses rather than inferring them from comments or requests.
No new experiment is authorized by this source review. C4/C5 and then RLE retain
the agreed sequencing. No new milliseconds/FPS or speedup percentages to report.

[screen]: https://github.com/chvvkumar/ESP32-P4-NINA-Display/blob/c7b34400f7373cad94caee7493413a8ec5b58864/main/web_handlers_display.c
[jpeg]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/jpeg.html
