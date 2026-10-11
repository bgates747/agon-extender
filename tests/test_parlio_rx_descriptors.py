"""Execute the pinned/derived RX descriptor callback, not a rewritten counter.

Model GDMA metadata, CPU/DMA cache visibility and interrupt coalescing. This
does not prove wire timing; native payload/physical fixtures own that boundary.
"""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT/'agents/build001/native-tools/esp-idf/components/esp_driver_parlio/src/parlio_rx.c'
spec = importlib.util.spec_from_file_location('patch_parlio_rx', ROOT/'vdp/video/extender/transport/patch_parlio_rx.py')
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)

def callback(text):
    start = text.index('static bool parlio_rx_one_desc_done_callback(') if 'static bool parlio_rx_one_desc_done_callback(' in text else text.index('static bool parlio_rx_default_desc_done_callback(')
    return text[start:text.index('static esp_err_t parlio_rx_create_dma_link(', start)]

PREFIX = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef int esp_err_t;
typedef void *gdma_channel_handle_t;
typedef int gdma_lli_owner_t;
#define ESP_OK 0
#define GDMA_LLI_OWNER_CPU 0
#define GDMA_LLI_OWNER_DMA 1
#define SOC_CACHE_INTERNAL_MEM_VIA_L1CACHE 1
#define ESP_CACHE_MSYNC_FLAG_DIR_M2C 1
#define ESP_EARLY_LOGW(...) ((void)0)
#define portENTER_CRITICAL_ISR(...) ((void)0)
#define portEXIT_CRITICAL_ISR(...) ((void)0)
typedef struct {struct {bool abnormal_eof;} flags;} gdma_event_data_t;
typedef struct {bool under_using;} delimiter;
typedef struct {void *delimiter,*data; size_t recv_bytes;} parlio_rx_event_data_t;
typedef struct unit {
 void *dma_link; unsigned curr_node_id,node_num; unsigned int_mem_align;
 struct {delimiter *delimiter; size_t recv_bytes,tot_trans_size;
         struct {bool infinite,indirect_mount;} flags;} curr_trans;
 struct {bool (*on_partial_receive)(struct unit*,parlio_rx_event_data_t*,void*);} cbs;
 void *user_data; unsigned char *usr_recv_buf; void *stash_buf[2];
} *parlio_rx_unit_handle_t;
static unsigned char cpu[3][4096],wire[3][4096],received[12288];
static size_t lengths[3]; static int owners[3],owner_error,partials,syncs;
void *gdma_link_get_buffer(void *list,unsigned i){(void)list;assert(i<3);return cpu[i];}
size_t gdma_link_get_length(void *list,unsigned i){(void)list;assert(i<3);return lengths[i];}
esp_err_t gdma_link_get_owner(void *list,unsigned i,gdma_lli_owner_t *o){
 (void)list;assert(i<3);if(owner_error)return 1;*o=owners[i];return ESP_OK;
}
esp_err_t esp_cache_msync(void *p,size_t n,int flag){
 assert(flag==1);for(int i=0;i<3;i++)if(p==cpu[i]){
  assert(n>=lengths[i] && n<=sizeof cpu[i]);memcpy(cpu[i],wire[i],n);++syncs;return 0;
 }assert(0);return 1;
}
bool partial(struct unit *u,parlio_rx_event_data_t *e,void *ctx){
 (void)u;(void)ctx;unsigned i=0;while(i<3&&e->data!=cpu[i])++i;assert(i<3);
 assert(e->recv_bytes==lengths[i] && !memcmp(cpu[i],wire[i],lengths[i]));++partials;return true;
}
static struct unit setup(unsigned nodes,const size_t *lens,size_t total){
 struct unit u={0};u.node_num=nodes;u.int_mem_align=64;u.curr_trans.tot_trans_size=total;
 u.usr_recv_buf=received;u.cbs.on_partial_receive=partial;
 memset(cpu,0,sizeof cpu);memset(wire,0,sizeof wire);memset(owners,0,sizeof owners);
 owner_error=partials=syncs=0;
 for(unsigned i=0;i<nodes;i++){lengths[i]=lens[i];memset(wire[i],17+i,lens[i]);}
 if(nodes>1 && lens[nodes-1]<64)u.stash_buf[0]=cpu[nodes-1];
 return u;
}
'''
MAIN = r'''
int main(void){
 gdma_event_data_t event={0};unsigned cases=0;
 size_t tail[]={576,15};struct unit u=setup(2,tail,591);
 parlio_rx_default_desc_done_callback(NULL,&event,&u);
 if(u.curr_trans.recv_bytes!=591 || partials!=2 || syncs!=2)return 71;
 ++cases;
 const size_t shapes[][3]={{2048,2048,0},{4032,64,1},{576,15,0},{64,0,0},{1,0,0}};
 const unsigned counts[]={2,3,2,1,1};
 for(unsigned s=0;s<5;s++)for(int split=0;split<2;split++){
  size_t total=0;for(unsigned i=0;i<counts[s];i++)total+=shapes[s][i];
  u=setup(counts[s],shapes[s],total);
  if(split){for(unsigned i=1;i<u.node_num;i++)owners[i]=GDMA_LLI_OWNER_DMA;
   assert(parlio_rx_default_desc_done_callback(NULL,&event,&u));
   assert(u.curr_trans.recv_bytes==shapes[s][0]);
   for(unsigned i=1;i<u.node_num;i++)owners[i]=GDMA_LLI_OWNER_CPU;
  }
  parlio_rx_default_desc_done_callback(NULL,&event,&u);
  assert(u.curr_trans.recv_bytes==total && partials==(int)counts[s] && syncs==partials);
  unsigned before=partials;
  assert(!parlio_rx_default_desc_done_callback(NULL,&event,&u));
  assert(partials==(int)before && u.curr_trans.recv_bytes==total);++cases;
 }
 // Short EOF is retained, including after a stale duplicate DONE.
 size_t short_length[]={295};u=setup(1,short_length,591);
 assert(parlio_rx_default_desc_done_callback(NULL,&event,&u));
 assert(u.curr_trans.recv_bytes==295);
 assert(!parlio_rx_default_desc_done_callback(NULL,&event,&u));
 assert(u.curr_trans.recv_bytes==295);++cases;
 // An uncompleted or unreadable descriptor contributes no invented bytes.
 for(int error=0;error<2;error++){
  u=setup(2,tail,591);owners[0]=GDMA_LLI_OWNER_DMA;owner_error=error;
  assert(!parlio_rx_default_desc_done_callback(NULL,&event,&u));
  assert(!u.curr_trans.recv_bytes && !partials);++cases;
 }
 // Infinite RX keeps the upstream one-descriptor callback behavior.
 u=setup(2,tail,591);u.curr_trans.flags.infinite=true;
 assert(parlio_rx_default_desc_done_callback(NULL,&event,&u));
 assert(u.curr_trans.recv_bytes==576 && partials==1);++cases;
 u=setup(2,tail,591);event.flags.abnormal_eof=true;
 assert(!parlio_rx_default_desc_done_callback(NULL,&event,&u));
 assert(!u.curr_trans.recv_bytes && !partials);++cases;
 printf("PASS %u actual-source finite descriptor/cache/coalescing/short/stale/infinite cases\n",cases);
 return 0;
}
'''

class ParlioDescriptors(unittest.TestCase):
    def execute(self, source):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); c = p/'rx.c'; exe = p/'rx'
            c.write_text(PREFIX + callback(source) + MAIN)
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-parameter',
                            '-fsanitize=address,undefined',str(c),'-o',str(exe)],check=True)
            return subprocess.run([str(exe)],capture_output=True,text=True)
    def test_pinned_negative(self):
        r=self.execute(SDK.read_text());self.assertEqual(r.returncode,71,r.stderr)
    def test_derived(self):
        r=self.execute(patch.derive(SDK.read_bytes()));self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('PASS 16',r.stdout)
    def test_reject_changed_sdk(self):
        with self.assertRaises(AssertionError):patch.derive(SDK.read_bytes()+b'\n')

if __name__=='__main__':unittest.main()
