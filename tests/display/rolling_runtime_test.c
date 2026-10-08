// Host regression of the actual rolling runtime, not a second scheduler.
// Fake DMA only supplies event times and copies bytes. It cannot model AXI,
// interrupt latency, FIFO depth or cache coherence on the physical P4.
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "bridge.h"

typedef int esp_err_t;
enum {ESP_OK, ESP_FAIL, ESP_ERR_NO_MEM, ESP_ERR_TIMEOUT, ESP_ERR_INVALID_STATE};
enum {MALLOC_CAP_INTERNAL=1, MALLOC_CAP_DMA=2, MALLOC_CAP_8BIT=4};
enum {ESP_CACHE_MSYNC_FLAG_DIR_M2C=1, ESP_CACHE_MSYNC_FLAG_DIR_C2M=2,
      ESP_CACHE_MSYNC_FLAG_INVALIDATE=4, LCD_COLOR_FMT_RGB888=24};
typedef void *esp_async_fbcpy_handle_t;
typedef void *dw_gdma_channel_handle_t;
typedef struct {int unused;} esp_async_fbcpy_config_t;
typedef struct {int unused;} esp_async_fbcpy_event_data_t;
typedef struct {int unused;} dw_gdma_trans_done_event_data_t;
typedef struct {void *invalid_lli;} dw_gdma_break_event_data_t;
typedef bool (*CopyDone)(esp_async_fbcpy_handle_t,esp_async_fbcpy_event_data_t*,void*);
typedef struct {
    const void *src_buffer; void *dst_buffer;
    size_t src_buffer_size_x,src_buffer_size_y,dst_buffer_size_x,dst_buffer_size_y;
    size_t src_offset_x,src_offset_y,dst_offset_x,dst_offset_y,copy_size_x,copy_size_y;
    struct {int color_type_id;} pixel_format_unique_id;
} esp_async_fbcpy_trans_desc_t;
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL_SAFE(p) ((void)(p))
#define portEXIT_CRITICAL_SAFE(p) ((void)(p))
#define ESP_RETURN_ON_ERROR(expr,...) do{esp_err_t e=(expr);if(e)return e;}while(0)

static int64_t now_us;
static bool dma_active,channel_enabled=true;
static unsigned submits,cache_fail,submit_fail,compositions;
static esp_async_fbcpy_trans_desc_t transfer;
static CopyDone completion;
static void *completion_arg;
static agon_scanout_frame scene;
static bool scheduled;
static int64_t dma_done_at;
static void complete_at(int64_t time);
static int64_t esp_timer_get_time(void) {return now_us;}
static void esp_rom_delay_us(unsigned us) {now_us+=us;}
static void vTaskDelay(int ticks) {if(dma_active)complete_at(now_us+100);else now_us+=ticks*1000;}
static int esp_cache_msync(void *p,size_t n,unsigned flags) {
    (void)p;(void)n;(void)flags;if(cache_fail){--cache_fail;return ESP_FAIL;}return ESP_OK;
}
static void *heap_caps_aligned_calloc(size_t a,size_t n,size_t s,unsigned caps) {
    (void)caps;void *p=NULL;assert(posix_memalign(&p,a,n*s)==0);memset(p,0,n*s);return p;
}
static void heap_caps_free(void *p) {free(p);}
static int dw_gdma_channel_enable_ctrl(void *channel,bool enabled) {
    assert(channel);channel_enabled=enabled;return ESP_OK;
}
static int esp_async_fbcpy_install(const esp_async_fbcpy_config_t *c,void **handle) {
    (void)c;*handle=(void*)1;return ESP_OK;
}
static int esp_async_fbcpy_uninstall(void *handle) {assert(handle&&!dma_active);return ESP_OK;}
static int esp_async_fbcpy(void *handle,esp_async_fbcpy_trans_desc_t *t,CopyDone cb,void *arg) {
    assert(handle&&!dma_active);if(submit_fail){--submit_fail;return ESP_FAIL;}
    dma_active=true;transfer=*t;completion=cb;completion_arg=arg;++submits;
    dma_done_at=now_us+((scheduled&&submits%31==0)?1130:500);return ESP_OK;
}
static void complete_at(int64_t time) {
    assert(dma_active&&time>=now_us);now_us=time;
    for(size_t row=0;row<transfer.copy_size_y;++row)
        memcpy((uint8_t*)transfer.dst_buffer+((row+transfer.dst_offset_y)*transfer.dst_buffer_size_x+transfer.dst_offset_x)*3,
               (const uint8_t*)transfer.src_buffer+((row+transfer.src_offset_y)*transfer.src_buffer_size_x+transfer.src_offset_x)*3,
               transfer.copy_size_x*3);
    // Pinned DMA2D frees its channels before invoking user EOF (dma2d.c).
    dma_active=false;CopyDone cb=completion;void *arg=completion_arg;cb((void*)1,NULL,arg);
}
agon_scanout_frame agon_scanout_latch(void) {return scene;}
void agon_scanout_compose(uint8_t *p,unsigned y,unsigned rows) {
    (void)p;(void)y;(void)rows;++compositions;
}

#include "strip_runtime.inc"

#ifndef EXPECT_OLD_ABORT
typedef struct {bool is_valid,is_last,en_trans_done_intr;} dw_gdma_block_markers_t;
typedef dw_gdma_block_markers_t *dw_gdma_link_list_handle_t;
typedef struct {
    unsigned cur_fb_index,h_pixels,v_pixels;int base;void *user_ctx;
    dw_gdma_link_list_handle_t link_lists[2];
    bool (*on_frame_buf_complete)(int*,void*,void*);
    bool (*on_vsync)(int*,void*,void*);
} esp_lcd_dpi_panel_t;
static void *dw_gdma_link_list_get_item(dw_gdma_link_list_handle_t list,int i) {return list+i;}
static void dw_gdma_lli_set_block_markers(void *item,dw_gdma_block_markers_t m) {*(dw_gdma_block_markers_t*)item=m;}
static void dw_gdma_channel_use_link_list(void *channel,dw_gdma_link_list_handle_t list) {(void)channel;assert(list);}
#define STRIP_ACTIVE(p) 1
#define STRIP_COUNT(p) ((p)->v_pixels/STRIP_ROWS)
#include "frame_callback.inc"
#endif

static uint8_t *background;
static void setup(unsigned width,unsigned height) {
    now_us=0;submits=0;compositions=0;cache_fail=submit_fail=0;channel_enabled=true;scheduled=false;
    background=calloc(width*height,3);assert(background);
    for(unsigned y=0;y<height;++y)memset(background+y*width*3,y%251,width*3);
    scene=(agon_scanout_frame){0,0,0,(int)width,(int)height};
    assert(strip_configure(background,background,width*height*3,width,height)==ESP_OK);
    assert(strip_prime_and_check()==ESP_OK);now_us=0;
}
static void done(unsigned us) {now_us=us;strip_block_done((void*)2,NULL,NULL);}
static void cleanup(void) {assert(strip_shutdown()==ESP_OK);free(background);}

static void tolerated_delay(unsigned width,unsigned height) {
    setup(width,height);
    done(1030); // retired0; fill block3; one DMA transaction
    done(2060); // retired1; block3 still has1030us before reuse
#ifdef EXPECT_OLD_ABORT
    assert(atomic_load(&strip_overlap)==1&&atomic_load(&strip_faults)==1);
    assert(!atomic_load(&strip_late)&&!atomic_load(&strip_over_budget));
    complete_at(2160);cleanup();puts("Reproduced premature overlap abort below the refill limit");
#else
    assert(!atomic_load(&strip_faults));
    complete_at(2160); // 1130us for block3: safe in three-slot ring
    assert(atomic_load(&strip_ready_tag[0])==3&&dma_active);
    complete_at(2960); // queued block4 finished before it is needed
    done(3090);assert(!atomic_load(&strip_faults));complete_at(3590);
    assert(atomic_load(&strip_ready_tag[1])==4&&atomic_load(&strip_ready_tag[2])==5);
    assert(atomic_load(&strip_queued)==1);cleanup();
#endif
}

#ifndef EXPECT_OLD_ABORT
static void frames(unsigned width,unsigned height) {
    setup(width,height);scheduled=true;
    dw_gdma_block_markers_t markers[15]={};
    esp_lcd_dpi_panel_t panel={.h_pixels=width,.v_pixels=height,.link_lists={markers,markers}};
    int64_t t=0;
    for(unsigned frame=0;frame<1024;++frame) {
        for(unsigned block=0;block<height/32;++block) {
            t+=1030;
            while(dma_active&&dma_done_at<=t)complete_at(dma_done_at);
            unsigned slot=block%3;
            for(unsigned row=0;row<32;++row) {
                uint8_t *p=strip_buffers[slot]+row*width*3;
                assert(p[0]==(block*32+row)%251&&p[width*3-1]==p[0]);
            }
            done(t);
        }
        mipi_dsi_dma_trans_done_cb((void*)2,NULL,&panel);
        assert(!atomic_load(&strip_faults)&&atomic_load(&strip_frames_done)==frame+1);
        t+=(517-height)*32; // nominal blank interval, not a bus/FIFO simulation
    }
    while(dma_active)complete_at(dma_done_at);
    assert(atomic_load(&strip_queued)>0&&!atomic_load(&strip_sequence_errors));
    cleanup();
}
#endif

int main(void) {
    tolerated_delay(848,480);tolerated_delay(684,384);
#ifndef EXPECT_OLD_ABORT
    frames(848,480);frames(684,384);
    setup(848,480);done(1030);done(2060);complete_at(2160);
    complete_at(3761); // includes queue time: 1701us, not just1601us DMA
    assert(atomic_load(&strip_over_budget)==1&&atomic_load(&strip_ready_tag[1])==UINT32_MAX);
    assert(atomic_load(&strip_first_fault)==STRIP_FAULT_BUDGET);cleanup();

    setup(848,480);done(1030);done(2060);done(3090);
    assert(atomic_load(&strip_late)==1&&!channel_enabled);complete_at(3200);
    assert(!dma_active);cleanup();

    setup(684,384);done(1030);done(2060);strip_stop();
    unsigned before=submits,painted=compositions;complete_at(2160);
    assert(submits==before&&compositions==painted&&!dma_active);
    assert(atomic_load(&strip_ready_tag[0])==UINT32_MAX);cleanup();

    setup(848,480);cache_fail=1;done(1030);
    assert(atomic_load(&strip_first_fault)==STRIP_FAULT_CACHE);
    strip_note_underrun();assert(atomic_load(&strip_first_fault)==STRIP_FAULT_CACHE);cleanup();

    setup(684,384);submit_fail=1;done(1030);
    assert(atomic_load(&strip_first_fault)==STRIP_FAULT_SUBMIT&&!dma_active);cleanup();

    setup(848,480);strip_fill(0,3,0);strip_fill(1,4,0);strip_fill(2,5,0);
    assert(atomic_load(&strip_first_fault)==STRIP_FAULT_OVERLAP);complete_at(100);cleanup();

    setup(684,384);dw_gdma_block_markers_t m[15]={};
    esp_lcd_dpi_panel_t panel={.h_pixels=684,.v_pixels=384,.link_lists={m,m}};
    mipi_dsi_dma_trans_done_cb((void*)2,NULL,&panel);
    assert(atomic_load(&strip_first_fault)==STRIP_FAULT_SEQUENCE&&!atomic_load(&strip_frames_done));cleanup();

    setup(848,480);strip_note_underrun();strip_invalid_block((void*)2,NULL,NULL);
    assert(atomic_load(&strip_first_fault)==STRIP_FAULT_UNDERRUN);
    assert(atomic_load(&strip_invalid)==1);cleanup();
    puts("PASS: actual rolling queue, deadline, reuse and fault/teardown paths");
#endif
}
