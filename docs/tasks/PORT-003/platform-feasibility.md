# Pinned ESP32-P4 display-backend feasibility

This document records compile-time facilities visible in the pinned PORT-003
environment. It does not claim that firmware was compiled, flashed, timed, or
qualified on hardware during Review Gate 1.

## Pinned platform

- PlatformIO platform: pioarduino `55.03.311`.
- Arduino/ESP-IDF library bundle: `5.5.5+sha.b774170ff46`.
- ESP-IDF PlatformIO package: `3.50505` (ESP-IDF 5.5.5).
- Board profile: `olimex_esp32_p4_devkit`.
- Frameworks: Arduino plus ESP-IDF, C++17.
- Qualified Rev-D1 board setting inherited from setup: 360 MHz CPU, 16 MiB
  flash, and 32 MiB PSRAM at 200 MHz.

The evidence generator fingerprints the five exact P4 headers below. Paths are
relative to the pinned pioarduino architecture library package:

- `esp32p4/include/esp_lcd/rgb/include/esp_lcd_panel_rgb.h`
- `esp32p4/include/esp_lcd/dsi/include/esp_lcd_mipi_dsi.h`
- `esp32p4/include/heap/include/esp_heap_caps.h`
- `esp32p4/include/esp_mm/include/esp_cache.h`
- `esp32p4/include/esp_timer/include/esp_timer.h`

Their hashes and matched declarations are in
`generated/display-evidence.yaml`.

## Logical framebuffer memory

The capability heap exposes explicit external-PSRAM, internal-memory,
DMA-descriptor, cache-alignment, and ordinary byte-addressable capabilities.
Aligned capability allocation and allocation-failure reporting are available.

The largest stock native logical frame is modest compared with 32 MiB PSRAM:

| Representative storage | One frame | Two frames |
|---|---:|---:|
| 1024×768 at 1 bit/pixel | 96 KiB | 192 KiB |
| 1024×768 at 2 bits/pixel | 192 KiB | 384 KiB |
| 640×480 at 4 bits/pixel | 150 KiB | 300 KiB |
| 640×240 or 320×480 at 8 bits/pixel | 150 KiB | 300 KiB |
| 1024×768 RGB565 presentation | 1.50 MiB | 3.00 MiB |
| 1024×768 RGB888 presentation | 2.25 MiB | 4.50 MiB |

These arithmetic sizes establish capacity, not bandwidth or latency. Large
logical and presentation buffers should prefer PSRAM. Task stacks, queues,
small synchronization objects, and any data explicitly required by a hardware
engine should request the corresponding internal/DMA/cache capabilities.

`esp_cache_msync()` is available for explicit cache synchronization. Whether
a particular sink requires writeback, invalidation, alignment, or a bounce
buffer must be decided by that sink's maintained driver contract and proven by
a target test. The logical renderer must not apply broad cache operations by
habit.

## Sink-independent frame clock

The pinned `esp_timer` API supports periodic timers and task- or ISR-dispatched
callbacks. The proposed frame clock needs only a short callback that records a
tick and wakes a renderer task; it does not require rendering inside the timer
callback.

This is sufficient to create nominal 60, 70, and 75 Hz logical cadence when no
physical display is attached. It is not proof of deadline accuracy under full
rendering, encoding, network, and peripheral load. Drift, jitter, backlog, and
per-tick service behavior belong in target qualification.

## Potential physical frame consumers

The P4 RGB panel API exposes:

- one to three driver-owned screen-sized framebuffers;
- preferential PSRAM framebuffer allocation;
- double-buffer shorthand;
- paired internal-memory bounce buffers;
- refresh-on-demand and no-framebuffer modes;
- VSYNC, draw-buffer-complete, frame-buffer-complete, and bounce-fill
  callbacks; and
- access to driver-owned framebuffer addresses.

Its callbacks run in ISR context. They are suitable for recording completion
and waking sink work, not for running the retained VDP renderer or defining the
global logical frame clock.

The P4 MIPI-DSI DPI API exposes driver-owned framebuffers, configurable input
and output color formats, optional DMA2D copies, framebuffer-complete and VSYNC
callbacks, and access to framebuffer addresses. This makes a future local
display adapter plausible without making MIPI-DSI part of the core controller.

Neither API is selected or implemented by PORT-003 Review Gate 1. The initial
network/browser sink likewise remains separate. All are consumers of the same
logical presentation service.

## Scheduling and synchronization implications

The retained renderer already uses FreeRTOS queues and task notifications. A
P4 frame-service task can therefore preserve the high-level queue contract
without retaining the old ISR executor. The proposed implementation must
still replace these old assumptions:

- work performed directly from the VGA VSYNC ISR;
- interrupt-safe queue reads as the normal render path;
- task affinity used to make a classic Xtensa cycle counter comparable;
- frame budgets calculated from VGA blanking intervals; and
- the physical ISR as the owner of queue consumption.

The strict P4 executor uses task-context rendering through unchanged upstream
queue-depth waits and swap notifications, plus short project-state locks and
bounded sink queues. Exact core affinity, priority, stack, and queue sizes are
measurements to make during implementation, not constants to guess at this
gate.

## Feasibility conclusion

The pinned platform contains the required substrates for a sink-neutral
logical framebuffer service: capability-aware memory, periodic timing,
FreeRTOS synchronization, cache maintenance, and multiple maintained physical
frame-consumer APIs. No header-level blocker was found.

That conclusion is deliberately narrow. It does not establish that the whole
retained renderer compiles on P4, that full-frame composition meets every
cadence, or that RGB/MIPI/network delivery works. Those claims require the
phased compile and target gates in `qualification-plan.md`.
