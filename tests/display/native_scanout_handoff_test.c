// Model IRQ and memory primitives only. Scheduling, joins, generation checking,
// fault latching, bank gating, and cache-before-LLI use the production driver.
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define TAG ""
#define ESP_OK 0
#define ESP_FAIL 1
#define ESP_ERR_NO_MEM 2
#define ESP_ERR_TIMEOUT 3
#define ESP_ERR_INVALID_STATE 4
#define ESP_ERR_INVALID_ARG 5
#define IRAM_ATTR
#define ESP_RETURN_ON_ERROR(e, tag, msg) do { int error = (e); if (error) return error; } while (0)
#define portMAX_DELAY UINT32_MAX
#define pdTRUE 1
#define pdPASS 1
#define pdFALSE 0
#define pdMS_TO_TICKS(n) (n)
#define ESP_CACHE_MSYNC_FLAG_DIR_C2M 1
#define MALLOC_CAP_INTERNAL 1
#define MALLOC_CAP_DMA 2
#define MALLOC_CAP_8BIT 4
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(p) ((void)(p))
#define portEXIT_CRITICAL(p) ((void)(p))
#define portENTER_CRITICAL_ISR(p) ((void)(p))
#define portEXIT_CRITICAL_ISR(p) ((void)(p))
#define __containerof(p,t,f) ((t *)((char *)(p)-offsetof(t,f)))
typedef int esp_err_t, portMUX_TYPE, BaseType_t;
typedef unsigned TickType_t;
typedef struct queue_model *QueueHandle_t;
typedef struct semaphore_model { bool token; } *SemaphoreHandle_t;
typedef void *TaskHandle_t;
typedef struct { int dummy; } esp_lcd_panel_t;
typedef esp_lcd_panel_t *esp_lcd_panel_handle_t;
typedef struct { bool is_valid, is_last, en_trans_done_intr; } dw_gdma_block_markers_t;
typedef struct { dw_gdma_block_markers_t desc[15]; } *dw_gdma_link_list_handle_t;
typedef struct { bool enabled; } *dw_gdma_channel_handle_t;
typedef struct { int dummy; } dw_gdma_trans_done_event_data_t;
typedef struct { dw_gdma_block_markers_t *invalid_lli; } dw_gdma_break_event_data_t;

#include "native_state.h"
typedef struct {
    esp_lcd_panel_t base;
    native_state native;
    dw_gdma_channel_handle_t dma_chan;
    dw_gdma_link_list_handle_t link_lists[1];
    unsigned h_pixels, v_pixels;
} esp_lcd_dpi_panel_t;
struct queue_model { unsigned get,count; nr_request requests[3]; };
static struct { struct { uint32_t val; } chen0; } regs;
#define DW_GDMA_LL_GET_HW(i) (&regs)
static int64_t clock_us;
static uint32_t ticks;
static void (*wait_irq)(void);
static void (*delay_event)(void);
static int frees, cache_calls, render_calls, wakes;
static bool sync_error, enable_join = true;
static unsigned long_render_us;
static esp_lcd_dpi_panel_t *current;
static int64_t last_wake;
static unsigned checked_wake_gaps;
static uint32_t last_render_frame;
static unsigned expected_y;
static uint32_t *dirty_slot_mark;
static void *last_sync;
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
// The clock and IRQs advance synchronously in the simulated core-1 task.
static void (*trace_cache_irq)(void);
static unsigned trace_reader_take;
static void (*trace_reader_irq)(void);
#endif
static int64_t esp_timer_get_time(void) { return clock_us; }
static int esp_cache_msync(void *p, size_t n, int flags) {
    assert(p && n && flags == ESP_CACHE_MSYNC_FLAG_DIR_C2M);
    ++cache_calls; clock_us += 4; last_sync = p;
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
    if (trace_cache_irq) trace_cache_irq();
#endif
    return sync_error ? ESP_FAIL : ESP_OK;
}
static void *heap_caps_aligned_calloc(size_t a, size_t n, size_t sz, int caps) {
    assert(a==64 && caps==7); return calloc(n,sz);
}
static void heap_caps_free(void *p) { if(p) ++frees; free(p); }
static SemaphoreHandle_t xSemaphoreCreateBinary(void) { return calloc(1,sizeof(struct semaphore_model)); }
static SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    SemaphoreHandle_t m = xSemaphoreCreateBinary(); m->token=true; return m;
}
static int xSemaphoreTake(SemaphoreHandle_t m, unsigned wait) {
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
    if (trace_reader_take && m == current->native.reader_mutex && --trace_reader_take == 0)
        trace_reader_irq();
#endif
    (void)wait; if (!m->token) return false; m->token=false; return true;
}
static void xSemaphoreGive(SemaphoreHandle_t m) { m->token=true; }
static void vSemaphoreDelete(SemaphoreHandle_t m) { free(m); }
static QueueHandle_t xQueueCreate(unsigned count, size_t size) {
    assert(count==3 && size==sizeof(nr_request)); return calloc(1,sizeof(struct queue_model));
}
static int xQueueSendFromISR(QueueHandle_t q,const nr_request *r, int *higher) {
    if(q->count==3) return false;
    q->requests[(q->get+q->count++)%3] = *r; *higher=true; return true;
}
static unsigned uxQueueMessagesWaitingFromISR(QueueHandle_t q) { return q->count; }
static int xQueueReceive(QueueHandle_t q,nr_request *r,unsigned wait) {
    (void)wait; if(!q->count)return false;
    *r=q->requests[q->get];q->get=(q->get+1)%3; --q->count;return true;
}
static void vQueueDelete(QueueHandle_t q) { free(q); }
static int xTaskCreatePinnedToCore(void (*fn)(void *),const char *n,int stack,void *p,int prio,void **task,int core) {
    (void)fn;(void)n;(void)stack;assert(prio==6 && core==1);*task=p;return pdPASS;
}
static void vTaskSuspend(void *p) { (void)p; }
static void vTaskDelete(void *p) { assert(p); }
static void vTaskNotifyGiveFromISR(void *t, int *higher) { assert(t); *higher=true; }
static void xTaskNotifyGive(void *t) {
    esp_lcd_dpi_panel_t *d=t;
    if(d->native.exit_worker && enable_join) xSemaphoreGive(d->native.joined);
}
static void ulTaskNotifyTake(int clear,unsigned wait) {
    (void)clear; (void)wait; assert(wait_irq); wait_irq();
}
static TickType_t xTaskGetTickCount(void) { return ticks; }
static void vTaskDelay(unsigned t) { ticks+=t; if(delay_event) delay_event(); }
static int dw_gdma_channel_get_id(dw_gdma_channel_handle_t ch,int *id) { assert(ch);*id=0;return ESP_OK; }
static void dw_gdma_channel_enable_ctrl(dw_gdma_channel_handle_t ch, bool enable) {
    ch->enabled=enable; regs.chen0.val=enable;
}
static dw_gdma_block_markers_t *dw_gdma_link_list_get_item(dw_gdma_link_list_handle_t list,unsigned b) {
    assert(b<15);return &list->desc[b];
}
static void dw_gdma_lli_set_block_markers(dw_gdma_block_markers_t *d, dw_gdma_block_markers_t value) {
    if (dirty_slot_mark && value.is_valid) {
        assert(last_sync == (void*)dirty_slot_mark);
        dirty_slot_mark=NULL;
    }
    *d=value;
}
#include "native_runtime.inc"
static void fresh(esp_lcd_dpi_panel_t *d,unsigned w,unsigned h) {
    memset(d,0,sizeof(*d)); d->dma_chan=calloc(1,sizeof(*d->dma_chan));
    d->link_lists[0]=calloc(1,sizeof(*d->link_lists[0]));
    d->h_pixels=w;d->v_pixels=h;current=d;last_wake=0;checked_wake_gaps=0;expected_y=0;last_render_frame=0;
    assert(native_allocate(d)==ESP_OK);
    for(unsigned i=0;i<d->native.ring.count;i++) nr_mark(d,i,i<3);
    d->native.phase=NR_RUNNING;dw_gdma_channel_enable_ctrl(d->dma_chan,true);
}
static void dispose(esp_lcd_dpi_panel_t *d) {
    d->native.phase=NR_EOF;regs.chen0.val=0;assert(!agon_dpi_stop(&d->base));
    native_free(d);free(d->dma_chan);free(d->link_lists[0]);
}
static void tick_block(void) {
    esp_lcd_dpi_panel_t *d=current;
    assert(d->native.ring.retired<d->native.ring.count);
    assert(d->link_lists[0]->desc[d->native.ring.retired].is_valid);
    clock_us+=1000;
    native_block_done(d->dma_chan,NULL,d);
    assert(d->native.phase==NR_RUNNING);
}
static void drawing(void *ctx) {
    esp_lcd_dpi_panel_t *d=ctx;
    assert(d->native.ring.retired==d->native.ring.count-2);
    last_wake=clock_us; ++wakes;
}
static bool render(void *ctx,uint8_t *p,unsigned y,unsigned rows,unsigned w,unsigned h,unsigned slot,uint32_t frame,bool *slot_black) {
    if (!long_render_us) assert(*slot_black == (frame == 1 && y < NR_ROWS * NR_SLOTS));
    *slot_black = false;
    esp_lcd_dpi_panel_t *d=ctx;
    assert(rows==32 && w==d->h_pixels && h==d->v_pixels && slot==(y/32)%3);
    assert(d->native.ring.retired%3!=slot || d->native.ring.retired==d->native.ring.count);
    assert(p==d->native.pixels[slot] && nr_can_write(&d->native.ring,(nr_tag){frame,y/32}));
    if(!long_render_us) {
        if(y==0 && last_wake) { assert(clock_us-last_wake>=1000); ++checked_wake_gaps; }
        if (y==0) { assert(!last_render_frame || frame==last_render_frame+1); last_render_frame=frame; }
        assert(y==expected_y); expected_y=(expected_y+rows)%h;
    }
    ++render_calls; p[0]=(uint8_t)y; dirty_slot_mark=(uint32_t *)p;
    last_sync=NULL;clock_us+=10+long_render_us;return true;
}
static void normal(unsigned w,unsigned h) {
    esp_lcd_dpi_panel_t d; fresh(&d,w,h); unsigned initial_render=render_calls, initial_wakes=wakes;
    assert(agon_native_bind(&d.base,&d,render,drawing)==ESP_OK);
    assert(agon_native_bind(&d.base,&d,render,drawing)==ESP_ERR_INVALID_STATE);
    wait_irq=tick_block;
    for(unsigned f=0;f<5;f++) {
        while(d.native.ring.retired<d.native.ring.count) {
            tick_block();
            nr_request req;
            while (xQueueReceive(d.native.queue,&req,0)) native_do_job(&d,req);
        }
        if (f == 0) {
            // Model a first slot ready only seven microseconds before rearm.
            // All earlier intra-frame slots had more lead than this seam.
            assert(nr_stats.min_lead_us > 7);
            d.native.ready_at[0] = clock_us - 7;
        }
        assert(native_frame(&d)); assert(nr_stats.frames==f+1);
        assert(nr_stats.min_lead_us <= 7);
    }
    assert(render_calls-initial_render==4*d.native.ring.count+3);
    assert(wakes-initial_wakes==4 && checked_wake_gaps==4);
    assert(nr_stats.min_draw_gap_us>=1000 && nr_stats.max_refill_us<=1600);
    assert(!nr_stats.fault && nr_stats.blocks==5*d.native.ring.count);
    agon_native_unbind(&d.base);assert(!d.native.render);dispose(&d);
}
static unsigned blank_callbacks;
static bool keep_black(void *ctx,uint8_t *p,unsigned y,unsigned rows,unsigned w,unsigned h,unsigned slot,
                       uint32_t frame,bool *slot_black) {
    (void)ctx; (void)p; (void)y; (void)rows; (void)w; (void)h; (void)slot; (void)frame;
    assert(*slot_black);
    ++blank_callbacks;
    return true;
}
// Once the worker loses this service window, both remaining block IRQs and
// the end-of-list callback run before the worker can resume.
static void finish_startup_frame(void) {
    assert(current->native.ring.frame == 1);
    assert(current->native.ring.retired == current->native.ring.count - 2);
    tick_block();
    tick_block();
    native_frame(current);
}

static void prepare_startup_handoff(esp_lcd_dpi_panel_t *d, agon_native_render_t renderer) {
    const unsigned blocks = d->native.ring.count;
    nr_request job;
    wait_irq = tick_block;
    // HdmiOutput permits binding only after the first successful rearm.
    while (d->native.ring.retired < blocks) {
        tick_block();
        while (xQueueReceive(d->native.queue,&job,0)) native_do_job(d,job);
    }
    assert(native_frame(d));
    assert(agon_native_bind(&d->base,d,renderer,drawing) == ESP_OK);
    while (d->native.ring.retired < blocks - 3) {
        tick_block();
        while (xQueueReceive(d->native.queue,&job,0)) native_do_job(d,job);
    }
    tick_block(); // Third-last block retired. The target request is queued.
}

static void startup_handoff(unsigned w, unsigned h, bool withhold) {
    esp_lcd_dpi_panel_t d;
    fresh(&d,w,h);
    const unsigned blocks = d.native.ring.count;
    const nr_tag top = {2,0};
    nr_request job;
    const unsigned prior_callbacks = blank_callbacks;
    prepare_startup_handoff(&d,keep_black);
    assert(xQueueReceive(d.native.queue,&job,0) && nr_equal(job.tag,top));
    assert(!d.native.reading && nr_can_write(&d.native.ring,top));
    assert(!d.link_lists[0]->desc[0].is_valid);
    wait_irq = finish_startup_frame;
    if (!withhold) native_do_job(&d,job);
    if (d.native.ring.retired == blocks - 2) finish_startup_frame();
    wait_irq = NULL;

    assert(nr_stats.blocks == 2 * blocks && nr_stats.max_queue == 2);
    assert(nr_stats.ticks == 0 && nr_stats.invalid == 0 && nr_stats.underruns == 0);
    if (withhold) {
        assert(nr_stats.frames == 1 && nr_stats.ready == 2 * blocks - 3);
        assert(nr_stats.fault == AGON_NATIVE_SEQUENCE && nr_stats.rejected == 1);
        assert(nr_stats.fault_frame == 2 && nr_stats.fault_block == 0);
        assert(!regs.chen0.val && !d.link_lists[0]->desc[0].is_valid);
        assert(blank_callbacks == prior_callbacks);
    } else {
        assert(nr_stats.frames == 2 && nr_stats.ready == 2 * blocks - 2);
        assert(nr_stats.fault == AGON_NATIVE_OK && nr_stats.rejected == 0);
        assert(nr_ready(&d.native.ring,top) && d.link_lists[0]->desc[0].is_valid);
        assert(regs.chen0.val && blank_callbacks == prior_callbacks + 1);
    }
    agon_native_unbind(&d.base);
    dispose(&d);
}

static void prime_only(void) {
    esp_lcd_dpi_panel_t d;
    const int before = cache_calls;
    fresh(&d,684,384);
    assert(cache_calls == before + NR_SLOTS);
    assert(agon_native_bind(&d.base,&d,keep_black,drawing) == ESP_OK);
    wait_irq = tick_block;
    for (unsigned frame=0; frame<2; ++frame) {
        while (d.native.ring.retired < d.native.ring.count) {
            tick_block();
            nr_request job;
            while (xQueueReceive(d.native.queue,&job,0)) native_do_job(&d,job);
        }
        assert(native_frame(&d));
    }
    assert(blank_callbacks > d.native.ring.count && cache_calls == before + NR_SLOTS);
    agon_native_unbind(&d.base);
    dispose(&d);
}
static void stop_frame(void) {
    assert(current->native.phase==NR_DRAINING);
    assert(!native_frame(current));regs.chen0.val=0;delay_event=NULL;
}
static void negative(void) {
    esp_lcd_dpi_panel_t d; fresh(&d,684,384);
    unsigned calls=render_calls;
    native_do_job(&d,(nr_request){.tag={0,1}, .retired_at=clock_us});
    assert(nr_stats.fault==AGON_NATIVE_SEQUENCE && calls==(unsigned)render_calls);
    dispose(&d);
    fresh(&d,684,384);
    dw_gdma_break_event_data_t ev={.invalid_lli=&d.link_lists[0]->desc[3]};
    native_invalid(d.dma_chan,&ev,&d);
    assert(nr_stats.fault==AGON_NATIVE_INVALID && nr_stats.fault_block==3 && !regs.chen0.val);
    dispose(&d);
    // Reaching frame EOF with a missing block interrupt cannot recycle the LL.
    fresh(&d,684,384);
    assert(!native_frame(&d));
    assert(nr_stats.fault==AGON_NATIVE_SEQUENCE && !regs.chen0.val);
    dispose(&d);
    // Genuine underrun is distinct from timer and invalid-descriptor failures.
    fresh(&d,848,480);
    native_underrun(&d);
    assert(nr_stats.underruns==1 && nr_stats.fault==AGON_NATIVE_UNDERRUN);
    dispose(&d);
    // Cache failure after the producer writes bytes must leave future LLI invalid.
    fresh(&d,684,384);
    tick_block();
    nr_request flush;
    assert(xQueueReceive(d.native.queue,&flush,0));
    d.native.black[flush.tag.block%NR_SLOTS] = false;
    sync_error = true; native_do_job(&d,flush); sync_error = false;
    assert(nr_stats.fault==AGON_NATIVE_CACHE && !d.link_lists[0]->desc[flush.tag.block].is_valid);
    dispose(&d);
    fresh(&d,684,384);
    assert(agon_native_bind(&d.base,&d,render,drawing)==ESP_OK);
    d.native.reading=true; long_render_us=1700; tick_block();
    nr_request req;
    assert(xQueueReceive(d.native.queue,&req,0));
    native_do_job(&d,req);
    assert(nr_stats.fault==AGON_NATIVE_BUDGET && !d.link_lists[0]->desc[req.tag.block].is_valid);
    assert(nr_stats.fault_render_us>=1700 && !regs.chen0.val);
    long_render_us=0;dirty_slot_mark=NULL;dispose(&d);
    fresh(&d,848,480);
    agon_native_stats_t receipt; assert(agon_native_get_last_fault(&receipt));
    assert(receipt.fault==AGON_NATIVE_BUDGET && receipt.epoch+1==nr_stats.epoch);
    unsigned before=frees;
    assert(agon_dpi_stop(&d.base)==ESP_ERR_TIMEOUT && frees==(int)before && d.native.worker);
    delay_event=stop_frame;enable_join=false;
    assert(agon_dpi_stop(&d.base)==ESP_ERR_TIMEOUT && d.native.worker && frees==(int)before);
    enable_join=true;assert(!agon_dpi_stop(&d.base));
    assert(!d.native.worker && frees==(int)before);
    native_free(&d);assert(frees==(int)before+3);free(d.dma_chan);free(d.link_lists[0]);
}
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
static agon_native_trace_t decision;
static bool interrupt_render;

static void frame_decision(void) {
    assert(!agon_native_get_startup_trace(&decision));
    finish_startup_frame();
    // Take the reference copy while the interrupted worker is still suspended.
    assert(agon_native_get_startup_trace(&decision));
}

static bool traced_render(void *ctx, uint8_t *pixels, unsigned y, unsigned rows,
                          unsigned w, unsigned h, unsigned slot, uint32_t frame, bool *black) {
    (void)ctx; (void)rows; (void)w; (void)h;
    assert(frame == 2 && y == 0 && slot == 0);
    uint32_t *cursor = agon_native_trace_row_cursor();
    assert(cursor);
    agon_native_trace_row(cursor,NR_ROW_COMPOSE,7);
    clock_us += 10;
    if (interrupt_render) frame_decision();
    // The interrupted renderer still holds its original cursor pointer.
    agon_native_trace_row(cursor,NR_ROW_EXPAND,7);
    pixels[0] = 1;
    *black = false;
    return true;
}

static void check_preserved(void) {
    agon_native_trace_t now;
    assert(agon_native_get_startup_trace(&now));
    assert(memcmp(&now,&decision,sizeof now) == 0);
}

static void retire_panel(esp_lcd_dpi_panel_t *d) {
    agon_native_unbind(&d->base);
    if (d->native.phase == NR_RUNNING) delay_event = stop_frame;
    assert(agon_dpi_stop(&d->base) == ESP_OK && !d->native.worker && !regs.chen0.val);
    native_free(d);
    free(d->dma_chan);
    free(d->link_lists[0]);
}

struct trace_case {
    const char *name;
    // Verify where the worker was when EOF sealed the record.
    enum nr_trace_event reached;
    enum nr_trace_event unseen;
};
static const struct trace_case trace_cases[] = {
    {"success",     NR_T_PUBLISHED,      NR_T_GATE_WAIT},
    {"withheld",    NR_T_ENQUEUED,       NR_T_DEQUEUED},
    {"wake-lock",   NR_T_WAKE_LOCK_WAIT, NR_T_WAKE_LOCK_HELD},
    {"reader-lock", NR_T_READ_LOCK_WAIT, NR_T_READ_LOCK_HELD},
    {"render",      NR_T_RENDER_BEGIN,   NR_T_RENDER_END},
    {"cache",       NR_T_CACHE_BEGIN,    NR_T_CACHE_END},
};

static void test_startup_trace(unsigned height,const char *scenario) {
    const unsigned width = height == 480 ? 848 : 684;
    esp_lcd_dpi_panel_t d;
    fresh(&d,width,height);
    assert(!agon_native_get_startup_trace(&decision));
    if (strcmp(scenario,"first-fault") == 0) {
        native_underrun(&d);
        assert(agon_native_get_startup_trace(&decision));
        assert(decision.site == NR_SITE_UNDERRUN && decision.fault == AGON_NATIVE_UNDERRUN);
        assert(decision.stamp[NR_T_RETIRE_12] == UINT32_MAX && !decision.rearmed);
    } else {
        const struct trace_case *c = NULL;
        for (size_t i=0; i<sizeof trace_cases / sizeof trace_cases[0]; ++i)
            if (strcmp(scenario,trace_cases[i].name) == 0) c = &trace_cases[i];
        assert(c);
        prepare_startup_handoff(&d,traced_render);
        const bool success = c->reached == NR_T_PUBLISHED;
        const bool withheld = c->unseen == NR_T_DEQUEUED;
        if (c->reached == NR_T_WAKE_LOCK_WAIT) trace_reader_take = 1;
        if (c->reached == NR_T_READ_LOCK_WAIT) trace_reader_take = 2;
        trace_reader_irq = frame_decision;
        interrupt_render = c->reached == NR_T_RENDER_BEGIN;
        if (c->reached == NR_T_CACHE_BEGIN) trace_cache_irq = frame_decision;
        nr_request target;
        if (!withheld) {
            assert(xQueueReceive(d.native.queue,&target,0));
            assert(nr_equal(target.tag,(nr_tag){2,0}));
            native_do_job(&d,target);
        }
        if (success || withheld) frame_decision();
        trace_cache_irq = NULL;
        trace_reader_irq = NULL;
        assert(decision.epoch == 1 && decision.site == NR_SITE_REARM);
        assert(decision.rearmed == success);
        assert(decision.fault == (success ? AGON_NATIVE_OK : AGON_NATIVE_SEQUENCE));
        assert(decision.retired == d.native.ring.count);
        assert(decision.slot_frame == 2 && decision.slot_block == 0 && decision.slot_ready == success);
        assert(decision.queue_depth == (withheld ? 3u : 2u));
        assert(decision.stamp[NR_T_RETIRE_12] == 0);
        assert(decision.stamp[NR_T_RETIRE_13] >= 1000);
        assert(decision.stamp[NR_T_RETIRE_14] == decision.stamp[NR_T_RETIRE_13] + 1000);
        assert(decision.stamp[NR_T_DECISION] == decision.stamp[NR_T_RETIRE_14]);
        assert(decision.stamp[c->reached] != UINT32_MAX && decision.stamp[c->unseen] == UINT32_MAX);
        if (c->reached == NR_T_RENDER_BEGIN || c->reached == NR_T_CACHE_BEGIN || success) {
            assert(decision.stamp[NR_T_GATE_BYPASS] != UINT32_MAX);
            enum nr_trace_row_phase phase = interrupt_render ? NR_ROW_COMPOSE : NR_ROW_EXPAND;
            assert(decision.row_cursor == (((uint32_t)phase << 16) | 7));
        }
        if (withheld) {
            assert(xQueueReceive(d.native.queue,&target,0));
            native_do_job(&d,target);  // Run the delayed task after its EOF.
        }
    }
    check_preserved();
    retire_panel(&d);
    fresh(&d,height == 480 ? 684 : 848,height == 480 ? 384 : 480);
    assert(nr_stats.epoch == 2);
    check_preserved();
    // Drive epoch 2 through its own 2:0 decision and first fault. Neither is
    // allowed to replace the boot receipt kept after the old DMA slots free.
    prepare_startup_handoff(&d,keep_black);
    nr_request target;
    assert(xQueueReceive(d.native.queue,&target,0) && nr_equal(target.tag,(nr_tag){2,0}));
    native_do_job(&d,target);
    finish_startup_frame();
    assert(d.native.ring.frame == 2);
    native_underrun(&d);
    check_preserved();
    retire_panel(&d);
    printf("PASS startup trace %ux%u %s: identical after worker resumption and opposite-carrier rearm/fault.\n",
           width,height,scenario);
}
#endif

int main(int argc,char **argv) {
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
    if (argc == 3) {
        unsigned height = (unsigned)atoi(argv[1]);
        assert(height == 384 || height == 480);
        test_startup_trace(height,argv[2]);
        return 0;
    }
#endif
    (void)argv;
    assert(argc == 1);
    normal(684,384);normal(848,480);prime_only();negative();
    startup_handoff(684,384,true); startup_handoff(848,480,true);
    startup_handoff(684,384,false); startup_handoff(848,480,false);
    puts("Native DMA handoff: both carriers, 5 wraps each, draw/wait phase, cache-before-valid, no repeated clean-slot sync, stale tag, hardware invalid LLI, late worker, joined stop and timeout retention passed.");
    return 0;
}
