"""Execute the pinned SDK's actual TX DMA setup against constrained memory.
The original fails large arrays; the derivative uses its existing PSRAM option.
No physical/DMA correctness or throughput claim follows from this host model.
"""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT/'agents/build001/native-tools/esp-idf/components'
PATCH = ROOT/'vdp/video/extender/transport/patch_parlio_upload.py'
spec = importlib.util.spec_from_file_location('patch_parlio_upload', PATCH)
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)


def function(text, name):
    start = text.index(name)
    begin = text.index('{', start)
    depth = 1
    end = begin + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


class DescriptorTests(unittest.TestCase):
    def test_exact_derivative_compile_archive_and_link_are_required(self):
        sys.path.insert(0, str(ROOT/'scripts'))
        from validate_p4_build import check_upload_tx_linkage
        with tempfile.TemporaryDirectory() as temp:
            build = Path(temp)
            derivative = build/'upload-parlio/parlio_tx.c'
            derivative.parent.mkdir()
            derivative.write_text(patch.derive((SDK/'esp_driver_parlio/src/parlio_tx.c').read_bytes()))
            commands = [{'file': str(derivative), 'output': 'tx.o'}]
            archive = 'esp-idf/esp_driver_parlio/libesp_driver_parlio.a'
            ninja = f'build {archive}: archive tx.o\nbuild agon_extender.elf: link {archive}\n'
            check_upload_tx_linkage(commands, ninja, build, True)
            for enabled, actions, edges in ((False, commands, ninja), (True, [], ninja),
                    (True, commands*2, ninja), (True, commands, ninja.replace('tx.o', 'wrong.o')),
                    (True, commands, f'build {archive}: archive tx.o\n')):
                with self.subTest(enabled=enabled, actions=actions, edges=edges), self.assertRaises(SystemExit):
                    check_upload_tx_linkage(actions, edges, build, enabled)
            derivative.write_text(derivative.read_text()+' ')
            with self.assertRaises(SystemExit):
                check_upload_tx_linkage(commands, ninja, build, True)
            check_upload_tx_linkage([], '', build, False)

    def test_sdk_setup_with_scarce_internal_ram(self):
        original = (SDK/'esp_driver_parlio/src/parlio_tx.c').read_bytes()
        derived = patch.derive(original)
        with self.assertRaises(ValueError):
            patch.derive(original+b' ')
        setup = function(original.decode(), 'static esp_err_t parlio_tx_unit_init_dma(')
        modified = function(derived, 'static esp_err_t parlio_tx_unit_init_dma(')
        count = function((SDK/'esp_hw_support/dma/esp_dma_utils.c').read_text(), 'size_t esp_dma_calculate_node_count(')
        prefix = r'''
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#define CONFIG_IDF_TARGET_ESP32P4 1
#define ESP_OK 0
#define ESP_ERR_NO_MEM 1
#define GDMA_CHANNEL_DIRECTION_TX 1
#define GDMA_TRIG_PERIPH_PARLIO 1
#define GDMA_MAKE_TRIGGER(a,b) 0
#define MAX(a,b) ((a)>(b)?(a):(b))
#define PARLIO_DMA_DESCRIPTOR_BUFFER_MAX_SIZE 4095
#define PARLIO_DMA_DESC_ALIGNMENT 8
#define PARLIO_DMA_LINK_NUM 2
#define ESP_RETURN_ON_ERROR(call,...) do{int error=(call);if(error)return error;}while(0)
#define ESP_RETURN_ON_FALSE(test,result,...) do{if(!(test))return result;}while(0)
typedef int esp_err_t;
typedef struct {int direction;struct {bool isr_cache_safe;} flags;} gdma_channel_alloc_config_t;
typedef struct {bool auto_update_desc,owner_check,eof_till_data_popped;} gdma_strategy_config_t;
typedef struct {unsigned max_data_burst_size;bool access_ext_mem;} gdma_transfer_config_t;
typedef struct {size_t item_alignment,num_items;struct {bool items_in_ext_mem;} flags;} gdma_link_list_config_t;
typedef struct {size_t max_transfer_size;unsigned dma_burst_size;} parlio_tx_unit_config_t;
typedef struct {int dma_chan,dma_link[2];size_t int_mem_align,ext_mem_align;} parlio_tx_unit_t;
static unsigned calls;static size_t last_nodes;static bool all_external,fail_psram;
static int PARLIO_GDMA_NEW_CHANNEL(const gdma_channel_alloc_config_t *c,int *p){assert(c->direction==1);*p=1;return 0;}
static int gdma_connect(int c,int t){(void)c;(void)t;return 0;}
static int gdma_apply_strategy(int c,const gdma_strategy_config_t *s){(void)c;assert(!s->auto_update_desc&&!s->owner_check&&s->eof_till_data_popped);return 0;}
static int gdma_config_transfer(int c,const gdma_transfer_config_t *t){(void)c;assert(t->access_ext_mem);return 0;}
static int gdma_get_alignment_constraints(int c,size_t *a,size_t *b){(void)c;*a=4;*b=64;return 0;}
static int gdma_new_link_list(const gdma_link_list_config_t *c,int *p){
 ++calls;last_nodes=c->num_items;all_external &= c->flags.items_in_ext_mem;
 assert(c->item_alignment==8);
 if((!c->flags.items_in_ext_mem && c->num_items*16>4096) || (c->flags.items_in_ext_mem&&fail_psram))return ESP_ERR_NO_MEM;
 *p=1;return 0;
}
'''
        main = r'''
int main(void){
 const size_t sizes[]={1,65537,1100000,32U*1024*1024};unsigned cases=0;
 for(unsigned i=0;i<4;++i){
  parlio_tx_unit_config_t c={.max_transfer_size=(sizes[i]+63)&~(size_t)63};parlio_tx_unit_t u={0};
  calls=0;all_external=true;fail_psram=false;
  int old=original_setup(&u,&c);assert(old==(i<2?ESP_OK:ESP_ERR_NO_MEM));++cases;
  calls=0;all_external=true;
  assert(derived_setup(&u,&c)==ESP_OK&&calls==2&&all_external);
  assert(last_nodes==(c.max_transfer_size+4031)/4032);++cases;
  calls=0;fail_psram=true;assert(derived_setup(&u,&c)==ESP_ERR_NO_MEM&&calls==1);++cases;
 }
 printf("PASS %u actual SDK TX setup cases; old internal limit, PSRAM lists, bounded allocation refusal\n",cases);
}
'''
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            source = path/'setup.c'
            source.write_text(prefix+count+setup.replace('parlio_tx_unit_init_dma(', 'original_setup(')+modified.replace('parlio_tx_unit_init_dma(', 'derived_setup(')+main)
            subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(source),'-o',str(path/'setup')],check=True)
            subprocess.run([str(path/'setup')],check=True,timeout=10)


if __name__ == '__main__':
    unittest.main()
