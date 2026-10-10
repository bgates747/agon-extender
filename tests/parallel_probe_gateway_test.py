"""Actual private resident bounds validation; physical probe call is modeled."""
from pathlib import Path
import subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
EMOS=ROOT.parent/'agon-emos'
HARNESS=r'''
#define _GNU_SOURCE
#include <sys/mman.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>
#include "emos_uart_flow.h"
#include "uart.h"
volatile BYTE serialFlags,uart1_keyboard_owned;
static unsigned calls;
static BYTE outcome=1;
BYTE emos_keyboard_lock(void){return 1;}
void emos_keyboard_unlock(BYTE b){(void)b;}
BYTE open_UART1(UART *s){(void)s;assert(0);return 0;}
void close_UART1(void){assert(0);}
BYTE uart1_claim_rts(void){assert(0);return 0;}
BYTE uart1_try_get(BYTE *p){(void)p;assert(0);return 0;}
BYTE uart1_try_put(BYTE b){(void)b;assert(0);return 0;}
BYTE uart1_receive_ready(BYTE b){(void)b;assert(0);return 0;}
UINT24 emos_read24(const BYTE *p){return p[0]|((UINT24)p[1]<<8)|((UINT24)p[2]<<16);}
static void put24(BYTE *p,UINT24 n){p[0]=n;p[1]=n>>8;p[2]=n>>16;}
BYTE emos_parallel_probe(BYTE *p,UINT16 n,BYTE reverse){
 assert((uintptr_t)p>=0xb0000 && (uintptr_t)p+n+16<=0xb8000 && n && n<=4096 && reverse<=1);
 ++calls;return outcome;
}
int main(void){
 assert(mmap((void*)0xb0000,0x8000,PROT_READ|PROT_WRITE,
  MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0)==(void*)0xb0000);
 t_emosGatewayRequest *r=(void*)0xb0000;BYTE *in=(void*)0xb0100;
 put24(r->input,0xb0100);put24(r->inputLength,2);in[0]=6;
 const unsigned lengths[]={1,2,255,256,4096};unsigned cases=0;
 for(unsigned reverse=0;reverse<2;++reverse)for(unsigned j=0;j<5;++j){
  unsigned n=lengths[j];in[1]=reverse;
  // Exact end boundary is accepted; one byte past it is not.
  put24(r->output,0xb8000-n-16);put24(r->outputCapacity,n+16);
  assert(emos_uartdiag_gateway(r)==0&&emos_read24(r->outputLength)==n+16);++cases;
  unsigned before=calls;put24(r->output,0xb8001-n-16);
  assert(emos_uartdiag_gateway(r)==19&&calls==before);++cases;
 }
 const unsigned invalid[]={0,1,16,4113,0xffffff};
 for(unsigned j=0;j<5;++j){put24(r->output,0xb0200);put24(r->outputCapacity,invalid[j]);
  unsigned before=calls;assert(emos_uartdiag_gateway(r)==19&&calls==before);++cases;}
 put24(r->outputCapacity,32);
 const unsigned addresses[]={0,0xaffff,0xb7fff,0xb8000,0xffffff};
 for(unsigned j=0;j<5;++j){put24(r->output,addresses[j]);unsigned before=calls;
  assert(emos_uartdiag_gateway(r)==19&&calls==before);++cases;}
 put24(r->output,0xb0200);in[1]=2;unsigned before=calls;
 assert(emos_uartdiag_gateway(r)==19&&calls==before);++cases;in[1]=0;
 for(unsigned n=0;n<4;++n)if(n!=2){put24(r->inputLength,n);before=calls;
  assert(emos_uartdiag_gateway(r)==19&&calls==before);++cases;}
 put24(r->inputLength,2);outcome=0;
 assert(emos_uartdiag_gateway(r)==35);++cases;
 printf("PASS %u actual private gateway bounds/failure cases; no hardware\n",cases);
}
'''
class GatewayTests(unittest.TestCase):
 def test_bounds(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);(d/'test.c').write_text(HARNESS);exe=d/'test'
   (d/'ff.h').write_text('enum { FR_OK=0,FR_INVALID_PARAMETER=19 };\n')
   subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-endif-labels',
    '-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast','-fsanitize=undefined',
    '-DEMOS_PARALLEL_PROBE=1','-DEMOS_BUSY=31','-DEMOS_UNAVAILABLE=35',
    '-DMOS_DEFINES_H','-include',str(EMOS/'tests/host/defines.h'),'-I'+str(d),'-I'+str(EMOS/'tests/host'),'-I'+str(EMOS/'src'),
    str(EMOS/'src/emos_uart_flow.c'),str(d/'test.c'),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=10)
if __name__=='__main__':unittest.main()
