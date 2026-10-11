"""Execute pinned channel_destroy with an IRQ at group/clock retirement.

The peripheral/IRQ leaves model the captured FWBUG-015 hazard; the destruction
body is taken from the actual pinned/derived driver, not reimplemented here.
"""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/'vdp/video/extender/display/rolling/patch_dw_gdma.py'
spec=importlib.util.spec_from_file_location('patch_dw_gdma',PATCH)
patch=importlib.util.module_from_spec(spec);spec.loader.exec_module(patch)
SDK=ROOT/'agents/build001/native-tools/esp-idf/components/esp_hw_support/dma/dw_gdma.c'

def body(text):
    start=text.index('static esp_err_t channel_destroy(')
    end=text.index('\nesp_err_t dw_gdma_new_channel(',start)
    return text[start:end]

class DmaLifetime(unittest.TestCase):
    def execute(self,source):
        harness=r'''
#include <stdlib.h>
#include <stdio.h>
typedef int esp_err_t;
#define ESP_OK 0
struct channel {void *group; void *intr;};
typedef struct channel dw_gdma_channel_t;
static int registered,clock_on,group_count,reads,freed;
static void irq(void){ if(registered){++reads;if(!clock_on)exit(71);} }
static void esp_intr_free(void*p){(void)p;irq();registered=0;freed++;}
static void channel_unregister_from_group(dw_gdma_channel_t*p){
 (void)p;if(--group_count==0)clock_on=0;irq();
}
'''+body(source)+r'''
int main(void){
 for(int group=0;group<2;group++)for(int intr=0;intr<2;intr++)
 for(int other=0;other<2;other++){
  registered=intr;clock_on=1;group_count=group+other;freed=reads=0;
  dw_gdma_channel_t *p=calloc(1,sizeof *p);p->group=group?(void*)1:NULL;p->intr=intr?(void*)1:NULL;
  if(channel_destroy(p)!=ESP_OK || registered || freed!=intr)return 72;
  if(group_count!=other)return 73;
 }
 puts("PASS eight actual-source teardown/IRQ lifetime cases");return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'lifetime.c';binary=Path(d)/'lifetime';src.write_text(harness)
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(src),'-o',str(binary)],check=True)
            return subprocess.run([str(binary)],capture_output=True,text=True)
    def test_pinned_negative(self):
        result=self.execute(SDK.read_text());self.assertEqual(result.returncode,71,result.stderr)
    def test_derived_lifetime(self):
        result=self.execute(patch.derive(SDK.read_bytes()));self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PASS eight',result.stdout)
    def test_reject_unreviewed_sdk(self):
        with self.assertRaises(AssertionError):patch.derive(SDK.read_bytes()+b'\n')

if __name__=='__main__':unittest.main()
