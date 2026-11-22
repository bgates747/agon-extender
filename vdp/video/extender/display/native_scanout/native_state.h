// Per-DPI-panel storage. The SDK owns the container through IRQ/worker join.
#pragma once
#include "native_ring.h"
#include "native_scanout.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "hal/dw_gdma_ll.h"
#include <string.h>

enum nr_phase { NR_IDLE, NR_RUNNING, NR_DRAINING, NR_EOF, NR_FAULT };
typedef struct { nr_tag tag; int64_t retired_at; } nr_request;
typedef struct {
    nr_ring ring;
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
    bool trace_boot_epoch;
#endif
    enum nr_phase phase;
    uint8_t *pixels[NR_SLOTS];
    int64_t ready_at[NR_SLOTS];
    bool black[NR_SLOTS];
    TaskHandle_t worker;
    QueueHandle_t queue;
    SemaphoreHandle_t reader_mutex, joined;
    bool exit_worker;
    // Accessed only under reader_mutex; the worker begins a binding at row 0.
    bool reading;
    void *ctx;
    agon_native_render_t render;
    agon_native_wake_t draw_wake;
} native_state;
