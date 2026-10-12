/* SPDX-License-Identifier: Apache-2.0
 * RESEARCH-007 ppa-clut-benchmark-r01: standalone, finite CPU/PPA conversion
 * comparison. Reuses the upstream CLUT backport; no HDMI, Agon transport,
 * keyboard, networking or SD. This image cannot provide ordinary P4 services.
 * Timing includes each path's required publication/completion, not correctness
 * checks, input generation, NVS storage or printing. PPA BLEND reads TWO inputs.
 */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "cpu.h"
#include "driver/ppa.h"
#include "esp_cache.h"
#include "esp_cpu.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs.h"
#include "nvs_flash.h"

#ifndef RESEARCH007_BUILD_ID
#define RESEARCH007_BUILD_ID "UNVERSIONED-DO-NOT-DEPLOY"
#endif
enum { CASES=6, METHODS=4, SAMPLES=32, WARMUPS=4, GUARD=64 };
enum { SIGNAL_CPU, LINEAR_CPU, LINEAR_PPA, REORDER_PPA };
typedef struct { unsigned w,h,top; uint32_t caps; const char *region; } case_t;
static const case_t cases[CASES]={
    {320,32,32,MALLOC_CAP_INTERNAL,"SRAM"}, {512,32,32,MALLOC_CAP_INTERNAL,"SRAM"},
    {320,32,32,MALLOC_CAP_SPIRAM,"PSRAM"}, {512,32,32,MALLOC_CAP_SPIRAM,"PSRAM"},
    {320,240,0,MALLOC_CAP_SPIRAM,"PSRAM"}, {512,384,0,MALLOC_CAP_SPIRAM,"PSRAM"},
};
static const char *methods[METHODS]={"cpu_signal","cpu_linear","ppa_linear","reorder_ppa"};
typedef struct { uint32_t prepare_us,operation_us,publish_us,total_us,elapsed_cycles; } timing_t;
typedef struct {
    uint32_t schema,sequence;
    uint64_t duration_us;
    char build[80];
    timing_t timings[CASES][METHODS][SAMPLES];
} stored_t;
static stored_t *results;
static nvs_handle_t storage;

static void *allocate(size_t bytes, uint32_t caps) {
    return heap_caps_aligned_calloc(64,1,bytes,caps|MALLOC_CAP_DMA|MALLOC_CAP_8BIT);
}
static uint8_t content(unsigned x,unsigned y,unsigned generation) {
    // Covers all256 bytes, including sync bits. The CLUT repeats each64 entries
    // because the legacy CPU expansion intentionally ignores the upper2 bits.
    return (uint8_t)(x+17*y+13*generation);
}
static void fill_source(uint8_t *src,unsigned w,unsigned rows,unsigned top,
                        unsigned generation,int shuffled) {
    for (unsigned y=top;y<rows;++y)
        for (unsigned x=0;x<w;++x) src[y*w+(shuffled?(x^2):x)]=content(x,y,generation);
}
static esp_err_t verify(const case_t *c,const uint8_t *out,const uint8_t *src,
                        unsigned generation,int shuffled) {
    for (unsigned y=0;y<c->h;++y) for (unsigned x=0;x<c->w;++x) {
        const uint8_t v=content(x,y+c->top,generation);
        const uint8_t *p=out+(y*c->w+x)*3;
        if (p[0]!=((v>>4)&3)*85 || p[1]!=((v>>2)&3)*85 || p[2]!=(v&3)*85) {
            printf("BENCH_ERROR,pixels,%u,%u,%02x%02x%02x\n",x,y,p[2],p[1],p[0]);return ESP_FAIL;
        }
    }
    for (unsigned i=0;i<GUARD;++i) if (out[c->w*c->h*3+i]!=0xA5) {
        printf("BENCH_ERROR,guard,%u\n",i);return ESP_FAIL;
    }
    for (unsigned y=0;y<c->h+c->top;++y) for (unsigned x=0;x<c->w;++x)
        if (src[y*c->w+(shuffled?(x^2):x)]!=content(x,y,generation)) {
            printf("BENCH_ERROR,input,%u,%u\n",x,y);return ESP_FAIL;
        }
    return ESP_OK;
}

// A local cleanup macro keeps errors finite and machine-readable; no abort/reset
// loop is allowed to conceal the failing case or overwrite its serial evidence.
#define TRY(call) do { error=(call); if(error!=ESP_OK) { \
    printf("BENCH_ERROR,line,%u,%s\n",__LINE__,esp_err_to_name(error));goto cleanup; } } while(0)
static esp_err_t run_case(unsigned id,ppa_client_handle_t client) {
    const case_t *c=&cases[id];
    const unsigned src_bytes=c->w*(c->h+c->top), block_bytes=c->w*c->h;
    const unsigned out_bytes=block_bytes*3, alloc_bytes=out_bytes+GUARD;
    uint8_t *src=allocate(src_bytes,MALLOC_CAP_SPIRAM);
    uint8_t *stage=allocate(block_bytes,MALLOC_CAP_SPIRAM);
    uint8_t *mask=allocate(block_bytes,MALLOC_CAP_SPIRAM);
    uint8_t *out=allocate(alloc_bytes,c->caps);
    esp_err_t error=ESP_ERR_NO_MEM;
    if(!src || !stage || !mask || !out) goto cleanup;
    TRY(esp_cache_msync(mask,block_bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M));
    ppa_blend_oper_config_t op={
        .in_bg={.buffer=src,.pic_w=c->w,.pic_h=c->h+c->top,.block_w=c->w,
                .block_h=c->h,.block_offset_y=c->top,.blend_cm=PPA_BLEND_COLOR_MODE_L8},
        .in_fg={.buffer=mask,.pic_w=c->w,.pic_h=c->h,.block_w=c->w,.block_h=c->h,
                .blend_cm=PPA_BLEND_COLOR_MODE_A8},
        .out={.buffer=out,.buffer_size=alloc_bytes,.pic_w=c->w,.pic_h=c->h,
              .blend_cm=PPA_BLEND_COLOR_MODE_RGB888},
        .bg_alpha_update_mode=PPA_ALPHA_NO_CHANGE,.fg_alpha_update_mode=PPA_ALPHA_NO_CHANGE,
        .mode=PPA_TRANS_MODE_BLOCKING,
    };
    for(unsigned round=0;round<WARMUPS+SAMPLES;++round) {
        const unsigned generation=round+id*61;
        for(unsigned order=0;order<METHODS;++order) {
            const unsigned method=(round+order)%METHODS;
            const int shuffled=method==SIGNAL_CPU || method==REORDER_PPA;
            fill_source(src,c->w,c->h+c->top,0,generation,shuffled);
            TRY(esp_cache_msync(src,src_bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M));
            // Dirty the selected CPU cache lines, as drawing would, but keep
            // physical input initialized for the whole-buffer integrity check.
            fill_source(src,c->w,c->h+c->top,c->top,generation,shuffled);
            memset(out,0xCC,out_bytes);memset(out+out_bytes,0xA5,GUARD);
            TRY(esp_cache_msync(out,alloc_bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M));
            op.in_bg.buffer=method==REORDER_PPA?stage:src;
            op.in_bg.pic_h=method==REORDER_PPA?c->h:c->h+c->top;
            op.in_bg.block_offset_y=method==REORDER_PPA?0:c->top;

            const uint32_t cycles_start=esp_cpu_get_cycle_count();
            const int64_t start=esp_timer_get_time();
            if(method==REORDER_PPA) cpu_reorder(src+c->top*c->w,stage,block_bytes);
            const int64_t prepared=esp_timer_get_time();
            if(method==SIGNAL_CPU) cpu_signal(src+c->top*c->w,out,c->w,c->h);
            else if(method==LINEAR_CPU) cpu_linear(src+c->top*c->w,out,c->w,c->h);
            else error=ppa_do_blend(client,&op);
            const int64_t converted=esp_timer_get_time();
            // CPU stores must be published for DMA. PPA completes in memory
            // and its driver already invalidated output; no redundant flush.
            if(method<=LINEAR_CPU) error=esp_cache_msync(out,alloc_bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M);
            const int64_t finished=esp_timer_get_time();
            const uint32_t cycles=esp_cpu_get_cycle_count()-cycles_start;
            if(error!=ESP_OK) goto cleanup;
            if(round>=WARMUPS) results->timings[id][method][round-WARMUPS]=(timing_t){
                prepared-start,converted-prepared,finished-converted,finished-start,cycles};
            // All physical-memory verification is outside the measured region.
            TRY(esp_cache_msync(out,alloc_bytes,ESP_CACHE_MSYNC_FLAG_DIR_M2C));
            // CPU-only paths left selected input dirty with identical values;
            // the prepublished physical copy is the integrity baseline.
            TRY(esp_cache_msync(src,src_bytes,ESP_CACHE_MSYNC_FLAG_DIR_M2C));
            TRY(verify(c,out,src,generation,shuffled));
        }
        vTaskDelay(1); // between rounds only; scheduler delays inside calls remain measured
    }
    error=ESP_OK;
cleanup:
    heap_caps_free(out);heap_caps_free(mask);heap_caps_free(stage);heap_caps_free(src);
    return error;
}
#undef TRY

static void emit(const stored_t *data,const char *kind) {
    printf("BENCH_BEGIN,%s,%"PRIu32",%s,%u,%u,%u\n",data->build,data->sequence,kind,CASES,METHODS,SAMPLES);
    for(unsigned m=0;m<METHODS;++m) printf("BENCH_METHOD,%u,%s\n",m,methods[m]);
    for(unsigned c=0;c<CASES;++c) {
        printf("BENCH_CASE,%u,%u,%u,%u,%s\n",c,cases[c].w,cases[c].h,cases[c].top,cases[c].region);
        for(unsigned m=0;m<METHODS;++m) for(unsigned s=0;s<SAMPLES;++s) {
            const timing_t *t=&data->timings[c][m][s];
            printf("BENCH_ROW,%u,%u,%u,%"PRIu32",%"PRIu32",%"PRIu32",%"PRIu32",%"PRIu32"\n",
                   c,m,s,t->prepare_us,t->operation_us,t->publish_us,t->total_us,t->elapsed_cycles);
        }
    }
    printf("BENCH_DONE,%s,%"PRIu32",%"PRIu64",%u\n",data->build,data->sequence,data->duration_us,CASES*METHODS*SAMPLES);
    fflush(stdout);
}
static esp_err_t run(ppa_client_handle_t client) {
    ++results->sequence;
    printf("BENCH_RUNNING,%s,%"PRIu32",clock=esp_timer_us,cpu_mhz=360\n",RESEARCH007_BUILD_ID,results->sequence);
    const int64_t start=esp_timer_get_time();
    for(unsigned c=0;c<CASES;++c) {
        const esp_err_t e=run_case(c,client);
        if(e!=ESP_OK) { printf("BENCH_FAIL,%s,%"PRIu32",case=%u,%s\n",RESEARCH007_BUILD_ID,results->sequence,c,esp_err_to_name(e));return e; }
    }
    results->duration_us=esp_timer_get_time()-start;
    esp_err_t e=nvs_set_blob(storage,"result",results,sizeof(*results));
    if(e==ESP_OK)e=nvs_commit(storage);
    if(e!=ESP_OK) { printf("BENCH_FAIL,%s,%"PRIu32",storage,%s\n",RESEARCH007_BUILD_ID,results->sequence,esp_err_to_name(e));return e; }
    printf("BENCH_STORED,%s,%"PRIu32",%u\n",results->build,results->sequence,(unsigned)sizeof(*results));
    emit(results,"fresh");return ESP_OK;
}
void app_main(void) {
    setvbuf(stdout,NULL,_IOLBF,0);
    // bench_nvs occupies 64KiB of the hash-pinned product table's unused
    // reserved tail at0xE20000. Never initialize/erase ordinary product NVS.
    esp_err_t e=nvs_flash_init_partition("bench_nvs");
    if(e==ESP_ERR_NVS_NO_FREE_PAGES || e==ESP_ERR_NVS_NEW_VERSION_FOUND) {
        e=nvs_flash_erase_partition("bench_nvs");
        if(e==ESP_OK)e=nvs_flash_init_partition("bench_nvs");
    }
    if(e==ESP_OK)e=nvs_open_from_partition("bench_nvs","r07",NVS_READWRITE,&storage);
    results=heap_caps_calloc(1,sizeof(*results),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
    ppa_client_handle_t client=NULL;
    const ppa_client_config_t config={.oper_type=PPA_OPERATION_BLEND,.max_pending_trans_num=1};
    if(!results)e=ESP_ERR_NO_MEM;
    if(e==ESP_OK)e=ppa_register_client(&config,&client);
    if(e!=ESP_OK) { printf("BENCH_FAIL,%s,0,initialization,%s\n",RESEARCH007_BUILD_ID,esp_err_to_name(e));return; }
    color_pixel_argb8888_data_t palette[256];
    for(unsigned i=0;i<256;++i) palette[i]=(color_pixel_argb8888_data_t){
        .r=(i&3)*85,.g=((i>>2)&3)*85,.b=((i>>4)&3)*85,.a=255};
    e=ppa_set_color_lookup_table(PPA_CLUT_BLEND_BG,palette,256);
    if(e!=ESP_OK) { printf("BENCH_FAIL,%s,0,palette,%s\n",RESEARCH007_BUILD_ID,esp_err_to_name(e));return; }
    size_t bytes=sizeof(*results);
    if(nvs_get_blob(storage,"result",results,&bytes)!=ESP_OK || bytes!=sizeof(*results) ||
       results->schema!=1 || strncmp(results->build,RESEARCH007_BUILD_ID,sizeof(results->build))!=0) memset(results,0,sizeof(*results));
    results->schema=1;snprintf(results->build,sizeof(results->build),"%s",RESEARCH007_BUILD_ID);
    vTaskDelay(pdMS_TO_TICKS(4000)); // allow the USB console collector to attach
    run(client);
    for(;;) {
        printf("BENCH_READY,d=dump durable result,r=rerun\n");fflush(stdout);
        int ch;
        do { ch=getchar();if(ch==EOF){clearerr(stdin);vTaskDelay(pdMS_TO_TICKS(100));} } while(ch!='d' && ch!='r');
        if(ch=='r')run(client);
        else {
            bytes=sizeof(*results);
            if(nvs_get_blob(storage,"result",results,&bytes)==ESP_OK && bytes==sizeof(*results) &&
               results->schema==1 && strncmp(results->build,RESEARCH007_BUILD_ID,sizeof(results->build))==0)emit(results,"stored");
            else printf("BENCH_FAIL,%s,0,no_saved_result\n",RESEARCH007_BUILD_ID);
        }
    }
}
