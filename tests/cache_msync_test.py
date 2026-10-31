"""Exercise actual pinned SDK API/helper bodies; bound range work, not elapsed time.
Controlled HAL/RTOS stand-ins observe critical ranges and validation. The old
SDK is a negative control. This does not simulate cache hardware or IRQ timing.
"""
from pathlib import Path
import argparse,importlib.util,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_p4,p4_cache_msync
spec=importlib.util.spec_from_file_location('extractor',ROOT/'docs/tasks/PORT-003/phase-e/scripts/run-official-mode-lifecycle.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
HARNESS=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#define CONFIG_ESP_MM_CACHE_MSYNC_C2M_CHUNKED_OPS 1
#define CONFIG_ESP_MM_CACHE_MSYNC_C2M_CHUNKED_OPS_MAX_LEN 16384
#define SOC_CACHE_WRITEBACK_SUPPORTED 1
#define ESP_OK 0
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_CACHE_MSYNC_FLAG_DIR_M2C 1
#define ESP_CACHE_MSYNC_FLAG_DIR_C2M 2
#define ESP_CACHE_MSYNC_FLAG_TYPE_INST 4
#define ESP_CACHE_MSYNC_FLAG_TYPE_DATA 8
#define ESP_CACHE_MSYNC_FLAG_UNALIGNED 16
#define ESP_CACHE_MSYNC_FLAG_INVALIDATE 32
#define ESP_RETURN_ON_FALSE_ISR(c,err,...) do {if(!(c))return err;}while(0)
#define ESP_EARLY_LOGV(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
typedef int esp_err_t;typedef int cache_type_t;
enum {CACHE_TYPE_DATA=1,CACHE_TYPE_INSTRUCTION=2};
static int s_spinlock,s_mutex,depth,locks,unlocks;static bool isr,yieldable=true;
static size_t max_inv,max_wb,total_inv,total_wb,inv_calls,wb_calls;
static uint32_t next_inv,next_wb;
static bool xPortInIsrContext(void){return isr;}
static bool xPortCanYield(void){return !isr && yieldable && !depth;}
static void esp_os_enter_critical_safe(int *p){assert(p==&s_spinlock);++depth;}
static void esp_os_exit_critical_safe(int *p){assert(p==&s_spinlock && depth);--depth;}
static void _lock_acquire(int *p){assert(p==&s_mutex);++locks;}
static void _lock_release(int *p){assert(p==&s_mutex);++unlocks;}
static bool cache_hal_vaddr_to_cache_level_id(uint32_t addr,size_t size,uint32_t *level,uint32_t *id){
 *level=2;*id=0;return addr>=0x40000000 && addr<=0x44000000 && size<=0x44000000-addr;
}
static uint32_t cache_hal_get_cache_line_size(uint32_t l,cache_type_t t){(void)l;(void)t;return 64;}
static bool cache_hal_invalidate_addr(uint32_t addr,size_t size){
 assert(depth && addr==next_inv);next_inv+=size;total_inv+=size;++inv_calls;if(size>max_inv)max_inv=size;return true;
}
static bool cache_hal_writeback_addr(uint32_t addr,size_t size){
 assert(depth && addr==next_wb);next_wb+=size;total_wb+=size;++wb_calls;if(size>max_wb)max_wb=size;return true;
}
@FUNCTIONS@
static void reset_state(uint32_t address){
 assert(depth==0);locks=unlocks=0;max_inv=max_wb=total_inv=total_wb=inv_calls=wb_calls=0;
 next_inv=next_wb=address;isr=false;yieldable=true;
}
int main(void){
 const uint32_t addr=0x40000000;const size_t plane=848*480*3;
 reset_state(addr);
 assert(esp_cache_msync((void*)(uintptr_t)addr,plane,ESP_CACHE_MSYNC_FLAG_DIR_M2C)==ESP_OK);
 if(max_inv>16384){puts("REPRODUCED: whole-plane task invalidation inside one critical section");return 40;}
 for(unsigned n=0;n<5;++n){
  const size_t sizes[]={0,64,16384,16448,848*480*3};size_t size=sizes[n];
  for(int flags=1;flags<=3;++flags){
   reset_state(addr);int selected=flags==1?ESP_CACHE_MSYNC_FLAG_DIR_M2C:ESP_CACHE_MSYNC_FLAG_DIR_C2M|(flags==3?ESP_CACHE_MSYNC_FLAG_INVALIDATE:0);
   assert(esp_cache_msync((void*)(uintptr_t)addr,size,selected)==ESP_OK);
   assert(!depth && locks==1 && unlocks==1);
   assert(total_inv==((flags==1 || flags==3)?size:0));assert(total_wb==(flags!=1?size:0));
   assert(max_inv<=16384 && max_wb<=16384);
  }
 }
 // ISR and non-yieldable M2C retain the original unsplit behavior/mutex policy.
 for(int kind=0;kind<3;++kind){
  reset_state(addr);isr=kind==0;yieldable=kind!=1;if(kind==2)depth=1;
  assert(esp_cache_msync((void*)(uintptr_t)addr,plane,ESP_CACHE_MSYNC_FLAG_DIR_M2C)==ESP_OK);
  assert(inv_calls==1 && max_inv==plane && locks==0 && unlocks==0);if(kind==2)--depth;
 }
 // Complete original validation must run before any chunk/cache work.
 struct {uint32_t addr;size_t size;int flags;} invalid[]={
  {0,64,1},{addr,65,1},{addr+1,64,1},{addr,64,3},
  {addr,64,ESP_CACHE_MSYNC_FLAG_TYPE_INST|ESP_CACHE_MSYNC_FLAG_TYPE_DATA},
  {0xfffffff0,64,1},{0x43ffffc0,128,1}};
 for(unsigned i=0;i<sizeof(invalid)/sizeof(invalid[0]);++i){
  reset_state(invalid[i].addr);
  assert(esp_cache_msync((void*)(uintptr_t)invalid[i].addr,invalid[i].size,invalid[i].flags)==ESP_ERR_INVALID_ARG);
  assert(!inv_calls && !wb_calls && !locks && !unlocks && !depth);
 }
 puts("PASS actual API/helpers: contiguous bounded task ranges; C2M/M2C/post-write invalidation; preserved ISR/non-yieldable and complete-range validation");
}
'''
def run(source,folder):
 names=['s_c2m_ops','s_invalidate_ops','s_acquire_mutex_from_task_context','s_release_mutex_from_task_context','esp_cache_msync']
 text=source.read_text();functions=[e.extract_function_text(source,n)[0] for n in names if n+'(' in text]
 cpp=folder/'test.c';cpp.write_text(HARNESS.replace('@FUNCTIONS@','\n'.join(functions)));binary=folder/'test'
 subprocess.run(['gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Wno-pointer-to-int-cast','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(cpp),'-o',str(binary)],check=True)
 return subprocess.run([str(binary)],text=True,capture_output=True,timeout=20)
def main():
 p=argparse.ArgumentParser();p.add_argument('--report',type=Path);a=p.parse_args();results={}
 with tempfile.TemporaryDirectory(prefix='cache-msync-') as tmp:
  t=Path(tmp);component=p4_cache_msync.prepare(build_p4.IDF,t/'project');p4_cache_msync.verify(build_p4.IDF,t/'project')
  for label,source,expected in [('old',build_p4.IDF/'components/esp_mm/esp_cache_msync.c',40),('current',component/'esp_cache_msync.c',0)]:
   folder=t/label;folder.mkdir();r=run(source,folder);print(r.stdout,end='');print(r.stderr,end='');assert r.returncode==expected,(label,r.returncode,expected)
   results[label]={'exit_code':r.returncode,'passed':True,'expected_exit_code':expected,'stdout':r.stdout}
  # Reject unexpected or altered files anywhere in the generated component.
  (component/'unexpected.c').write_text('/* rejected */')
  try:p4_cache_msync.verify(build_p4.IDF,t/'project')
  except ValueError:results['extra_source_rejected']=True
  else:raise AssertionError('Unexpected component source accepted')
 if a.report:a.report.write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
