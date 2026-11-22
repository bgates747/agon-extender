// Stock-native producer for the pinned pre-v3 P4/IDF 5.5.5 DPI unit. The
// hardware follows one descriptor per 32 rows. Each future descriptor stays
// INVALID until the worker has finished the tagged slot and made it DMA-visible.
// Unlike an after-the-fact software tag check this also guards delayed IRQs.
static portMUX_TYPE nr_mux = portMUX_INITIALIZER_UNLOCKED;
static agon_native_stats_t nr_stats, nr_fault_receipt;

bool agon_native_get_last_fault(agon_native_stats_t *out)
{
    if (!out) return false;
    portENTER_CRITICAL(&nr_mux);
    *out = nr_fault_receipt;
    portEXIT_CRITICAL(&nr_mux);
    return out->fault != AGON_NATIVE_OK;
}

void agon_native_get_stats(agon_native_stats_t *out)
{
    if (!out) return;
    portENTER_CRITICAL(&nr_mux);
    *out = nr_stats;
    portEXIT_CRITICAL(&nr_mux);
}

static void nr_max(uint32_t *dest, uint32_t v) { if (*dest < v) *dest = v; }

static void nr_mark(esp_lcd_dpi_panel_t *d, unsigned block, bool valid)
{
    dw_gdma_block_markers_t marker = {
        .is_valid = valid, .is_last = block + 1 == d->native.ring.count,
        .en_trans_done_intr = true,
    };
    dw_gdma_lli_set_block_markers(dw_gdma_link_list_get_item(d->link_lists[0], block), marker);
}

// Called with nr_mux held. First reason survives later IRQs and shutdown.
static void nr_fail(esp_lcd_dpi_panel_t *d, enum agon_native_fault fault, nr_tag tag,
                    uint32_t queue_us, uint32_t render_us, uint32_t sync_us)
{
    if (!nr_stats.fault) {
        nr_stats.fault = fault;
        nr_stats.fault_frame = tag.frame;
        nr_stats.fault_block = tag.block;
        nr_stats.fault_queue_us = queue_us;
        nr_stats.fault_render_us = render_us;
        nr_stats.fault_sync_us = sync_us;
        nr_stats.fault_elapsed_us = queue_us + render_us + sync_us;
        nr_fault_receipt = nr_stats;
    }
    d->native.phase = NR_FAULT;
    if (d->dma_chan) dw_gdma_channel_enable_ctrl(d->dma_chan, false);
}

static bool nr_live(const native_state *s)
{
    return s->phase == NR_RUNNING || s->phase == NR_DRAINING;
}

static bool IRAM_ATTR native_invalid(dw_gdma_channel_handle_t ch, const dw_gdma_break_event_data_t *ev, void *ctx)
{
    (void)ch;
    esp_lcd_dpi_panel_t *d = ctx;
    portENTER_CRITICAL_ISR(&nr_mux);
    if (nr_live(&d->native)) {
        nr_ring *r = &d->native.ring;
        nr_tag bad = {r->frame, r->retired};
        // Hardware reports the actual invalid descriptor. IRQ can lag software's
        // expected ordinal. Use the actual identity in the failure receipt.
        for (unsigned i = 0; i < r->count; ++i) {
            if (dw_gdma_link_list_get_item(d->link_lists[0],i) == ev->invalid_lli) {
                bad.block = i;
                break;
            }
        }
        ++nr_stats.invalid;
        nr_fail(d, AGON_NATIVE_INVALID, bad, 0, 0, 0);
    }
    portEXIT_CRITICAL_ISR(&nr_mux);
    return false;
}

static void native_underrun(esp_lcd_dpi_panel_t *d)
{
    portENTER_CRITICAL_ISR(&nr_mux);
    if (nr_live(&d->native)) {
        ++nr_stats.underruns;
        nr_fail(d, AGON_NATIVE_UNDERRUN, (nr_tag){d->native.ring.frame,d->native.ring.retired},0,0,0);
    }
    portEXIT_CRITICAL_ISR(&nr_mux);
}

static bool IRAM_ATTR native_block_done(dw_gdma_channel_handle_t ch,
                                        const dw_gdma_trans_done_event_data_t *ev, void *ctx)
{
    (void)ch; (void)ev;
    esp_lcd_dpi_panel_t *d = ctx;
    native_state *s = &d->native;
    nr_request job = { .retired_at = esp_timer_get_time() };
    BaseType_t higher = pdFALSE;
    portENTER_CRITICAL_ISR(&nr_mux);
    if (nr_live(s)) {
        nr_tag old = {s->ring.frame,s->ring.retired};
        if (!nr_retire(&s->ring, &old, &job.tag)) {
            ++nr_stats.rejected;
            nr_fail(d, AGON_NATIVE_SEQUENCE, old, 0, 0, 0);
        } else {
            ++nr_stats.blocks;
            nr_mark(d,old.block,false);
            if (old.block + 1 < s->ring.count) {
                nr_tag next = nr_advance(old,1,s->ring.count);
                if (!nr_ready(&s->ring,next)) {
                    ++nr_stats.rejected;
                    nr_fail(d,AGON_NATIVE_SEQUENCE,next,0,0,0);
                } else {
                    uint32_t lead = (uint32_t)(job.retired_at - s->ready_at[next.block % NR_SLOTS]);
                    if (lead < nr_stats.min_lead_us) nr_stats.min_lead_us = lead;
                }
            }
            if (nr_live(s)) {
                if (xQueueSendFromISR(s->queue,&job,&higher) != pdTRUE) {
                    ++nr_stats.rejected;
                    nr_fail(d,AGON_NATIVE_QUEUE,job.tag,0,0,0);
                } else {
                    nr_max(&nr_stats.max_queue,uxQueueMessagesWaitingFromISR(s->queue));
                    vTaskNotifyGiveFromISR(s->worker,&higher);
                }
            }
        }
    }
    portEXIT_CRITICAL_ISR(&nr_mux);
    return higher == pdTRUE;
}

static bool native_frame(esp_lcd_dpi_panel_t *d)
{
    bool rearm = false;
    portENTER_CRITICAL_ISR(&nr_mux);
    native_state *s = &d->native;
    if (s->phase == NR_DRAINING) {
        // The IDF channel has completed the last block. Do not set CHEN again.
        s->phase = NR_EOF;
    } else if (s->phase == NR_RUNNING) {
        if (nr_next_frame(&s->ring)) {
            // The final block interrupt cannot observe slot 0's reuse: the
            // pinned DPI driver arms the new list in this frame callback.
            uint32_t lead = (uint32_t)(esp_timer_get_time() - s->ready_at[0]);
            if (lead < nr_stats.min_lead_us) nr_stats.min_lead_us = lead;
            ++nr_stats.frames;
            rearm = true;
        } else {
            ++nr_stats.rejected;
            nr_fail(d,AGON_NATIVE_SEQUENCE,(nr_tag){s->ring.frame + 1,0},0,0,0);
        }
    }
    portEXIT_CRITICAL_ISR(&nr_mux);
    return rearm;
}

static void native_do_job(esp_lcd_dpi_panel_t *d, nr_request job)
{
    native_state *s = &d->native;
    // FIFO order means last frame's final native row has been read before its
    // block-0 successor reaches this worker. Release drawing at the third-last
    // block retirement, separate from the penultimate-retirement sampling gate.
    // Delayed service shortens that gap; retain the measured minimum.
    int64_t woke = 0;
    if (job.tag.block == 0) {
        xSemaphoreTake(s->reader_mutex,portMAX_DELAY);
        portENTER_CRITICAL(&nr_mux);
        bool allowed = nr_live(s) && nr_can_write(&s->ring,job.tag) && !s->exit_worker;
        portEXIT_CRITICAL(&nr_mux);
        if (allowed && s->reading && s->draw_wake) {
            s->draw_wake(s->ctx);
            woke = esp_timer_get_time();
            portENTER_CRITICAL(&nr_mux);
            ++nr_stats.ticks;
            portEXIT_CRITICAL(&nr_mux);
        }
        xSemaphoreGive(s->reader_mutex);
    }
    for (;;) {
        portENTER_CRITICAL(&nr_mux);
        const bool live = nr_live(s) && !s->exit_worker;
        const bool sample = nr_may_sample(&s->ring,job.tag);
        portEXIT_CRITICAL(&nr_mux);
        if (!live) return;
        // At startup the previous frame had no reader to wake. Use the
        // retired slot now, while the worker can still beat frame rearm.
        if (sample || (job.tag.block == 0 && !woke)) break;
        // A later block IRQ releases the next frame's top rows. Never block
        // the interrupt or take the drawing/native mutex while awaiting it.
        ulTaskNotifyTake(pdTRUE,portMAX_DELAY);
    }
    const unsigned slot = job.tag.block % NR_SLOTS;
    const unsigned bytes = NR_ROWS * d->h_pixels * 3;
    xSemaphoreTake(s->reader_mutex, portMAX_DELAY);
    portENTER_CRITICAL(&nr_mux);
    bool owned = nr_live(s) && !s->exit_worker && nr_can_write(&s->ring,job.tag);
    if (!owned && nr_live(s) && !s->exit_worker) {
        ++nr_stats.rejected;
        nr_fail(d,AGON_NATIVE_SEQUENCE,job.tag,0,0,0);
    }
    const int64_t start = esp_timer_get_time();
    if (owned && woke) {
        uint32_t gap = (uint32_t)(start-woke);
        if (gap < nr_stats.min_draw_gap_us) nr_stats.min_draw_gap_us = gap;
    }
    portEXIT_CRITICAL(&nr_mux);
    if (!owned) {
        xSemaphoreGive(s->reader_mutex);
        return;
    }
    bool ok = true;
    bool changed = false;
    if (job.tag.block == 0) s->reading = s->render != NULL;
    if (s->reading) {
        const bool was_black = s->black[slot];
        ok = s->render(s->ctx,s->pixels[slot],job.tag.block * NR_ROWS,NR_ROWS,
                       d->h_pixels,d->v_pixels,slot,job.tag.frame,&s->black[slot]);
        changed = !was_black || !s->black[slot];
    } else if (!s->black[slot]) {
        memset(s->pixels[slot],0,bytes);
        s->black[slot] = true;
        changed = true;
    }
    xSemaphoreGive(s->reader_mutex);
    int64_t stored = esp_timer_get_time();
    esp_err_t sync = ESP_OK;
    if (ok && changed) sync = esp_cache_msync(s->pixels[slot],bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M);
    portENTER_CRITICAL(&nr_mux);
    int64_t finished = esp_timer_get_time();
    uint32_t q = (uint32_t)(start - job.retired_at);
    uint32_t render = (uint32_t)(stored - start), vis = (uint32_t)(finished - stored);
    uint64_t elapsed = (uint64_t)(finished - job.retired_at);
    if (nr_live(s)) {
        enum agon_native_fault fault = AGON_NATIVE_OK;
        if (!ok || sync != ESP_OK) {
            fault = ok ? AGON_NATIVE_CACHE : AGON_NATIVE_RENDER;
        } else if (!nr_can_write(&s->ring,job.tag)) {
            fault = AGON_NATIVE_SEQUENCE;
        } else {
            // Allow 16us for fence + final noncached marker write. The timestamp
            // after arming checks this proposed reserve on the actual target.
            finished = esp_timer_get_time();
            elapsed = (uint64_t)(finished-job.retired_at);
            if (elapsed > NR_LIMIT_US - 16 || !nr_publish(&s->ring,job.tag,elapsed)) {
                fault = AGON_NATIVE_BUDGET;
            } else {
                __atomic_thread_fence(__ATOMIC_SEQ_CST);
                nr_mark(d,job.tag.block,true);
                finished = esp_timer_get_time();
                elapsed = (uint64_t)(finished-job.retired_at);
                if (elapsed > NR_LIMIT_US) {
                    nr_mark(d,job.tag.block,false);
                    fault = AGON_NATIVE_BUDGET;
                } else {
                    s->ready_at[slot] = finished;
                    ++nr_stats.ready;
                }
            }
        }
        vis = (uint32_t)(finished-stored);
        nr_max(&nr_stats.max_queue_us,q); nr_max(&nr_stats.max_render_us,render);
        nr_max(&nr_stats.max_sync_us,vis);
        if (elapsed > nr_stats.max_refill_us) {
            nr_stats.max_refill_us = elapsed > UINT32_MAX ? UINT32_MAX : (uint32_t)elapsed;
            nr_stats.worst_frame = job.tag.frame; nr_stats.worst_block = job.tag.block;
            nr_stats.worst_queue_us = q; nr_stats.worst_render_us = render; nr_stats.worst_sync_us = vis;
        }
        unsigned bin = elapsed < NR_LIMIT_US ? elapsed / 100 : 16;
        ++nr_stats.histogram[bin];
        if (fault != AGON_NATIVE_OK) {
            ++nr_stats.rejected;
            nr_fail(d,fault,job.tag,q,render,vis);
        }
    }
    portEXIT_CRITICAL(&nr_mux);
}

static void native_worker(void *ctx)
{
    esp_lcd_dpi_panel_t *d = ctx;
    native_state *s = &d->native;
    for (;;) {
        ulTaskNotifyTake(pdTRUE,portMAX_DELAY);
        portENTER_CRITICAL(&nr_mux);
        bool exit = s->exit_worker;
        portEXIT_CRITICAL(&nr_mux);
        if (exit) break;
        nr_request job;
        while (xQueueReceive(s->queue,&job,0) == pdTRUE) native_do_job(d,job);
        // The gate inside native_do_job also consumes task notifications.
        // Check shutdown again after draining, before any blocking wait.
        portENTER_CRITICAL(&nr_mux);
        exit = s->exit_worker;
        portEXIT_CRITICAL(&nr_mux);
        if (exit) break;
    }
    xSemaphoreGive(s->joined);
    vTaskSuspend(NULL);
}

esp_err_t agon_native_bind(esp_lcd_panel_handle_t panel, void *context,
                           agon_native_render_t render, agon_native_wake_t wake)
{
    if (!panel || !context || !render || !wake) return ESP_ERR_INVALID_ARG;
    esp_lcd_dpi_panel_t *d = __containerof(panel,esp_lcd_dpi_panel_t,base);
    native_state *s = &d->native;
    xSemaphoreTake(s->reader_mutex,portMAX_DELAY);
    portENTER_CRITICAL(&nr_mux);
    bool available = s->phase == NR_RUNNING;
    portEXIT_CRITICAL(&nr_mux);
    if (s->render) available = false;
    if (available) {
        s->ctx = context; s->draw_wake = wake; s->render = render;
        s->reading = false;
    }
    xSemaphoreGive(s->reader_mutex);
    return available ? ESP_OK : ESP_ERR_INVALID_STATE;
}

void agon_native_unbind(esp_lcd_panel_handle_t panel)
{
    esp_lcd_dpi_panel_t *d = __containerof(panel,esp_lcd_dpi_panel_t,base);
    native_state *s = &d->native;
    xSemaphoreTake(s->reader_mutex,portMAX_DELAY);
    s->reading = false; s->render = NULL; s->draw_wake = NULL; s->ctx = NULL;
    xSemaphoreGive(s->reader_mutex);
}

bool agon_native_failed(esp_lcd_panel_handle_t panel)
{
    esp_lcd_dpi_panel_t *d = __containerof(panel,esp_lcd_dpi_panel_t,base);
    portENTER_CRITICAL(&nr_mux);
    bool failed = d->native.phase == NR_FAULT;
    portEXIT_CRITICAL(&nr_mux);
    return failed;
}

static esp_err_t native_allocate(esp_lcd_dpi_panel_t *d)
{
    native_state *s = &d->native;
    nr_prime(&s->ring,d->v_pixels / NR_ROWS);
    const size_t bytes = d->h_pixels * NR_ROWS * 3u;
    for (unsigned i = 0; i < NR_SLOTS; ++i) {
        s->pixels[i] = heap_caps_aligned_calloc(64,1,bytes,MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT);
        if (!s->pixels[i]) return ESP_ERR_NO_MEM;
        ESP_RETURN_ON_ERROR(esp_cache_msync(s->pixels[i],bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M),TAG,"prime native slot");
        s->black[i] = true;
    }
    s->queue = xQueueCreate(NR_SLOTS,sizeof(nr_request));
    s->joined = xSemaphoreCreateBinary();
    s->reader_mutex = xSemaphoreCreateMutex();
    if (!s->queue || !s->joined || !s->reader_mutex) return ESP_ERR_NO_MEM;
    if (xTaskCreatePinnedToCore(native_worker,"native-rows",6144,d,6,&s->worker,1) != pdPASS) {
        s->worker = NULL;
        return ESP_ERR_NO_MEM;
    }
    portENTER_CRITICAL(&nr_mux);
    const uint32_t epoch = nr_stats.epoch + 1;
    nr_stats = (agon_native_stats_t){.epoch=epoch, .width=d->h_pixels,.height=d->v_pixels,.min_lead_us=UINT32_MAX,.min_draw_gap_us=UINT32_MAX};
    portEXIT_CRITICAL(&nr_mux);
    return ESP_OK;
}

static esp_err_t native_stop_dma(esp_lcd_panel_handle_t panel)
{
    esp_lcd_dpi_panel_t *d = __containerof(panel,esp_lcd_dpi_panel_t,base);
    native_state *s = &d->native;
    portENTER_CRITICAL(&nr_mux);
    if (s->phase == NR_RUNNING) s->phase = NR_DRAINING;
    bool never_started = s->phase == NR_IDLE;
    portEXIT_CRITICAL(&nr_mux);
    if (never_started) return ESP_OK;
    int id;
    ESP_RETURN_ON_ERROR(dw_gdma_channel_get_id(d->dma_chan,&id),TAG,"DSI DMA channel");
    const TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&nr_mux);
        bool terminal = s->phase == NR_EOF || s->phase == NR_FAULT;
        portEXIT_CRITICAL(&nr_mux);
        if (terminal && !(DW_GDMA_LL_GET_HW(0)->chen0.val & (1U << id))) return ESP_OK;
        vTaskDelay(1);
    } while (xTaskGetTickCount() - start < pdMS_TO_TICKS(100));
    return ESP_ERR_TIMEOUT;
}

esp_err_t agon_dpi_stop(esp_lcd_panel_handle_t panel)
{
    esp_lcd_dpi_panel_t *d = __containerof(panel,esp_lcd_dpi_panel_t,base);
    native_state *s = &d->native;
    // Both caller-initiated stop and IDF construction error take this path.
    // Stop must succeed before worker shutdown, interrupt removal, or free.
    ESP_RETURN_ON_ERROR(native_stop_dma(&d->base),TAG,"native channel still active");
    if (s->worker) {
        portENTER_CRITICAL(&nr_mux);
        s->exit_worker = true;
        portEXIT_CRITICAL(&nr_mux);
        xTaskNotifyGive(s->worker);
        if (!xSemaphoreTake(s->joined,pdMS_TO_TICKS(100))) return ESP_ERR_TIMEOUT;
        vTaskDelete(s->worker); s->worker = NULL;
    }
    return ESP_OK;
}

static void native_free(esp_lcd_dpi_panel_t *d)
{
    native_state *s = &d->native;
    if (s->queue) vQueueDelete(s->queue);
    if (s->reader_mutex) vSemaphoreDelete(s->reader_mutex);
    if (s->joined) vSemaphoreDelete(s->joined);
    for (unsigned i = 0; i < NR_SLOTS; ++i) heap_caps_free(s->pixels[i]);
}
