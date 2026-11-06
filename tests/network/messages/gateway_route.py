#!/usr/bin/env python3
"""Exercise public netp SDK requests through actual EMOS gateway validation.

Reuse the component owner's resident-gateway harness/extraction, replacing only
its leaf with an admission recorder. The physical carrier is not exercised.
This closes the gap where the pipeline called the inner netp endpoint directly.
Caller owns normal compiler admission. No device/emulator access.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--emos-source',required=True,type=Path)
p.add_argument('--output',required=True,type=Path)
a=p.parse_args();root=Path(__file__).resolve().parents[3]
a.output.mkdir(parents=True,exist_ok=False)
donor=root.parent/'agon-emos/tests/test_emos_resident_gateway.py'
spec=importlib.util.spec_from_file_location('gateway_donor',donor)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=(a.emos_source/'src/emos.c').read_text()
helpers=s[s.index('static UINT16 emos_read16'):s.index('static void emos_print_identity')]
i=helpers.index('static void emos_write16');j=helpers.index('static void emos_write24',i)
helpers=helpers[:i]+helpers[j:]
gateway=s[s.index('static BOOL emos_range_overlaps_module'):s.index('BYTE emos_application_enter')]
leaf=r'''
#define EMOS_NETWORK_PARALLEL 1
static unsigned netpCalls;
static UINT24 emos_netp_gateway(t_emosGatewayRequest*r) {
    assert(emosBusy);++netpCalls;
    BYTE*input=(void*)(uintptr_t)emos_read24(r->input);
    if(input[0])return 31; /* Observe dispatch without admitting leaf work. */
    BYTE*out=(void*)(uintptr_t)emos_read24(r->output);
    memcpy(out,"NP\1\1\x78\x56\x34\x12",8);r->outputLength[0]=8;return 0;
}
'''
harness=r'''
static unsigned sdk_call(uint8_t*r){return emos_gateway((t_emosGatewayRequest*)r);}
#define AGON_NET_CALL(r) sdk_call(r)
#include <agon/net_parallel.h>
int main(void){
    assert(mmap((void*)0x40000,0x20000,PROT_READ|PROT_WRITE,
           MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void*)0x40000);
    agon_netp_client*c=(void*)0x40000;unsigned length;uint8_t*out=(void*)0x42000;
    assert(agon_netp_open(c)==0&&c->token==0x12345678&&netpCalls==1);
    /* The original physical failure: nonzero name padding must refuse before
     * leaf admission, rather than treating netp as net or silently truncating. */
    c->request[5]=3;
    assert(emos_gateway((t_emosGatewayRequest*)c->request)==19&&netpCalls==1);
    uint8_t packet[20]={'N','M',1,1};agon_net_put32(packet+4,c->token);
    agon_net_put32(packet+8,1);packet[12]=6;
    assert(agon_netp_submit(c,packet,20)==31&&netpCalls==2&&!c->pending);
    assert(agon_netp_take(c,out,142,&length)==31&&netpCalls==3);
    assert(agon_netp_release(c)==31&&netpCalls==4&&c->token==0x12345678);
    puts("Public SDK OPEN/SUBMIT/TAKE/RELEASE route through actual gateway; malformed length refuses before leaf");
}
'''
# Put leaf after numeric helpers, before actual gateway dispatch.
source=a.output/'gateway.c';source.write_text(m.PREAMBLE+helpers+leaf+gateway+harness)
cmd=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-endif-labels',
     '-Wno-misleading-indentation','-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast',
     '-fsanitize=undefined','-I'+str(root.parent/'agon-emos/tests/host'),
     '-iquote'+str(a.emos_source/'src'),'-I'+str(root/'include'),str(source),'-o',str(a.output/'gateway')]
start=time.monotonic();report={'passed':False,'inputs':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in (donor,a.emos_source/'src/emos.c',root/'include/agon/net_parallel.h')}}
try:
    subprocess.run(cmd,check=True,timeout=180)
    subprocess.run([str(a.output/'gateway')],check=True,timeout=10)
    report['passed']=True
finally:
    report['seconds']=time.monotonic()-start
    (a.output/'run.json').write_text(json.dumps(report,indent=2)+'\n')
