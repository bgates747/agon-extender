#!/usr/bin/env python3
"""Exercise actual refill completion/phase publication with a controlled clock.

This validates deadline boundaries and the first-failed-job snapshot, not DMA,
cache coherence, interrupt delivery or physical elapsed time.
"""
from pathlib import Path
import subprocess,tempfile,json
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'vdp/video/extender/display/rolling/strip_runtime.inc').read_text()
header=(ROOT/'vdp/video/extender/display/rolling/strip_probe.h').read_text()
def body(name):
    start=source.index(name);start=source.rfind('\n',0,start)+1
    opening=source.index('{',start);depth=1;end=opening+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]
code=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <assert.h>
#include <stdio.h>
#define STRIP_REFILL_LIMIT_US 1600
#define STRIP_INJECT_LATE_TAG 0
#define STRIP_ROWS 32
#define ESP_CACHE_MSYNC_FLAG_DIR_M2C 1
#define ESP_CACHE_MSYNC_FLAG_DIR_C2M 2
'''+header.replace('#pragma once','')+r'''
static atomic_uint strip_faults,strip_copy_us,strip_copy_max,strip_compose_total,strip_compose_max;
static atomic_uint strip_refills,strip_total_us,strip_max_us,strip_over_budget;
static atomic_uint strip_ready_tag[3];static int64_t strip_ready_time[3];
static atomic_uint strip_budget_available,strip_budget_queue,strip_budget_prepare;
static atomic_uint strip_budget_source,strip_budget_submit,strip_budget_finish;
static atomic_bool strip_stopping;
static int64_t strip_copy_begin,strip_source_begin,strip_source_end,strip_submit_begin;
static struct {unsigned slot,block,tag;int64_t begin;} strip_job;
static unsigned char storage[64];static unsigned char *strip_buffers[]={storage,storage,storage};
static unsigned strip_bytes=64;static unsigned release_count,aborted_error,sync_calls;
static bool sync_ok=true;
static int64_t times[8];static unsigned now_index;
static int64_t esp_timer_get_time(void){assert(now_index<8);return times[now_index++];}
static void strip_max(atomic_uint *p,unsigned v){if(v>atomic_load(p))atomic_store(p,v);}
static bool strip_sync(void *p,unsigned n,unsigned f){(void)p;(void)n;(void)f;++sync_calls;return sync_ok;}
static void strip_release_job(void){++release_count;}
static void strip_abort(unsigned reason,unsigned error){assert(reason==STRIP_FAULT_BUDGET);++strip_faults;aborted_error=error;}
static void agon_scanout_compose(void *p,unsigned a,unsigned n){(void)p;(void)a;(void)n;}
static void esp_rom_delay_us(unsigned n){(void)n;assert(0);}
'''+body('static void strip_finish(void) {')+'\n'+body('void strip_budget_read(')+r'''
static void setup(unsigned finish){
 strip_faults=strip_stopping=0;strip_job.slot=0;strip_job.block=2;strip_job.tag=42;strip_job.begin=0;
 strip_copy_begin=100;strip_source_begin=150;strip_source_end=450;strip_submit_begin=500;
 now_index=0;times[0]=800;times[1]=840;times[2]=860;times[3]=finish;times[4]=finish+1;
 release_count=aborted_error=sync_calls=0;sync_ok=true;strip_ready_tag[0]=UINT32_MAX;
}
int main(void){
 strip_budget_stats out;strip_budget_read(&out);assert(out.available==0&&out.queue_us==0&&out.finish_us==0);
 setup(1600);strip_finish();strip_budget_read(&out);
 assert(strip_faults==0&&strip_over_budget==0&&out.available==0&&strip_ready_tag[0]==42&&release_count==1);
 setup(1700);strip_finish();strip_budget_read(&out);
 assert(strip_faults==1&&strip_over_budget==1&&aborted_error==1700&&strip_ready_tag[0]==UINT32_MAX&&release_count==1);
 assert(out.available==1&&out.queue_us==100&&out.prepare_us==100&&out.source_cache_us==300);
 assert(out.submit_to_callback_us==300&&out.finish_us==900);
 assert(out.queue_us+out.prepare_us+out.source_cache_us+out.submit_to_callback_us+out.finish_us==aborted_error);
 setup(1900);strip_finish();strip_budget_read(&out);assert(out.finish_us==900&&aborted_error==1900);
 strip_budget_available=0;setup(1601);strip_finish();strip_budget_read(&out);
 assert(out.available==1&&out.finish_us==801&&aborted_error==1601);
 strip_budget_available=0;setup(1700);sync_ok=false;strip_finish();strip_budget_read(&out);
 assert(out.available==0&&release_count==1&&sync_calls==1&&strip_ready_tag[0]==UINT32_MAX);
 puts("Actual strip_finish: strict1600us boundary, same-job phase sum, first-failure retention, cache-failure nonpublication PASS");
}
'''
with tempfile.TemporaryDirectory(prefix='strip-budget-') as directory:
    p=Path(directory);(p/'test.c').write_text(code)
    subprocess.run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p/'test.c'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True)
print(json.dumps({'passed':True,'scope':'actual completion and read API; controlled host clock, not physical timing'}))
