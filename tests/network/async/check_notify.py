#!/usr/bin/env python3
"""Finite source/host/native notification checks; normal Pi build lease required.

No ROM build, target, emulator or installation. The original header is an exact
retained baseline, never fetched from an assumed current source revision.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--emos',type=Path,required=True)
p.add_argument('--uart',type=Path,required=True)
p.add_argument('--toolchain',type=Path,required=True)
p.add_argument('--baseline-header',type=Path,required=True)
p.add_argument('--host-includes',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
R=Path(__file__).resolve().parents[3]
E=a.emos.resolve();U=a.uart.resolve();T=a.toolchain.resolve();O=a.output.resolve();H=a.host_includes.resolve()
O.mkdir(parents=True,exist_ok=False)
report=dict(passed=False,scope='actual SDK/core/owner C with fake hardware; native compile/link only',steps=[],inputs={})
start=time.monotonic()

def pin(path):
    data=path.read_bytes()
    return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())

def run(label,argv,cwd=R):
    step=dict(label=label,argv=list(map(str,argv)));report['steps'].append(step)
    with (O/(label+'.log')).open('x') as f:
        result=subprocess.run(argv,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,
                              timeout=180,env=dict(os.environ,PATH=str(T/'bin')+os.pathsep+os.environ['PATH']))
    step['returncode']=result.returncode
    if result.returncode:raise RuntimeError(label+' failed; retained log')

try:
    inputs=[R/'include/agon/net.h',R/'include/agon/net_async.h',a.baseline_header.resolve(),
            Path(__file__),R/'tests/network/async/composition.c',R/'tests/network/async/notify.c',
            E/'src/emos_net.c',E/'src/emos_neta.c',H/'defines.h',
            U/'src/u1_tx.c',U/'include/u1_tx.h',U/'src/u1_emit.src']
    for f in inputs:report['inputs'][str(f)]=pin(f)
    baseline=a.baseline_header.read_bytes()
    assert hashlib.sha256(baseline).hexdigest()=='27cfa5a52884a3f0d14cce8810613e43d63dffe860bee5e56a7fa856fc367d21', 'Unexpected baseline; reconcile exact SDK first'
    fake=O/'fake';fake.mkdir()
    (fake/'ff.h').write_text('enum {FR_OK=0,FR_TIMEOUT=15,FR_INVALID_PARAMETER=19};\n')
    (fake/'ez80f92.h').write_text('extern unsigned char test_ier;\n#define UART1_IER test_ier\n')
    common=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-endif-labels',
            '-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast','-Wno-misleading-indentation',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
    flags=['-DMOS_DEFINES_H','-DEMOS_UART1_APP=1','-DEMOS_UART0_RFC25=1',
           '-DEMOS_BUSY=31','-DEMOS_UNSAFE_CALLER=32','-DEMOS_UNAVAILABLE=35',
           '-include',str(H/'defines.h'),'-I'+str(fake),
           '-I'+str(H),'-I'+str(E/'src')]
    for name in ('emos_net','emos_neta'):
        run(name,common+flags+['-c',str(E/'src'/f'{name}.c'),'-o',str(O/f'{name}.o')])
    for name in ('composition','notify'):
        run(name+'-link',common+['-I'+str(R/'include'),'-I'+str(U/'include'),
            str(R/'tests/network/async'/f'{name}.c'),str(U/'src/u1_tx.c'),
            str(O/'emos_net.o'),str(O/'emos_neta.o'),'-o',str(O/name)])
        run(name+'-run',[str(O/name)])

    # Same physical source/header paths and flags for the paired baseline/OFF
    # builds. Keep all outputs before replacing only this disposable header.
    work=O/'native-work';(work/'src').mkdir(parents=True)
    inc=work/'include';(inc/'agon').mkdir(parents=True)
    shutil.copyfile(R/'include/agon/net.h',inc/'agon/net.h')
    for src in ('u1_tx.c','u1_emit.src'):shutil.copyfile(U/'src'/src,work/'src'/src)
    main='''/* Link-only, never RUN. */
#ifdef APP_NOTIFY
static volatile unsigned char wake;
#define AGON_NETA_NOTIFY(c) ((void)(c),wake=1)
#endif
#include <agon/net_async.h>
static agon_neta_client client;
int main(void){
    unsigned char address[6]={127,0,0,1,1,1};
    int r=agon_neta_begin(&client);
    if(!r){r=agon_net_submit(&client.net,AGON_NET_CONNECT,address,6);
        if(!r)r=agon_neta_progress(&client);
        if(!r)r=agon_net_take(&client.net);
        if(!r)r=agon_neta_close(&client);}
    return r;
}
'''
    (work/'src/main.c').write_text(main)
    for name,header,on in [('baseline',baseline,False),('off',(R/'include/agon/net_async.h').read_bytes(),False),
                           ('on',(R/'include/agon/net_async.h').read_bytes(),True)]:
        for sub in ('obj','bin'):
            if (work/sub).exists():shutil.rmtree(work/sub)
        (inc/'agon/net_async.h').write_bytes(header)
        (work/'Makefile').write_text('NAME=notify\nAGONDEV_TOOLCHAIN='+str(T)+
            '\ninclude $(AGONDEV_TOOLCHAIN)/config/makefile.inc\nCFLAGS += -I'+str(inc)+
            ' -I'+str(U/'include')+' -Wall -Wextra -Werror -fstack-usage'+(' -DAPP_NOTIFY' if on else '')+'\n')
        run(name+'-native',['make','-j1'],work)
        dest=O/name;dest.mkdir()
        shutil.copytree(work/'obj',dest/'obj');shutil.copytree(work/'bin',dest/'bin')
        run(name+'-elf',[str(T/'bin/ez80-none-elf-ld'),'-defsym=RAM_START=0x40000',
            '-defsym=RAM_SIZE=0x70000','-defsym=_has_exit_handler=0','-Map='+str(dest/'native.map'),
            '-T',str(T/'config/linker.conf'),'-o',str(dest/'native.elf'),
            *map(str,sorted((work/'obj').glob('*.o'))),'-L'+str(T/'lib'),'-lagon'])
        run(name+'-size',[str(T/'bin/ez80-none-elf-size'),str(dest/'native.elf')])
        run(name+'-listing',[str(T/'bin/ez80-none-elf-objdump'),'-dr',str(dest/'obj/main.o')])
        for file in (dest/'bin/notify.bin',dest/'obj/main.o',dest/'obj/u1_tx.o',dest/'obj/u1_emit.o'):
            report.setdefault('native',{}).setdefault(name,{})[file.name]=pin(file)
    assert (O/'baseline/bin/notify.bin').read_bytes()==(O/'off/bin/notify.bin').read_bytes(), 'Default binary changed'
    for obj in ('main.o','u1_tx.o','u1_emit.o'):
        assert (O/'baseline/obj'/obj).read_bytes()==(O/'off/obj'/obj).read_bytes(), 'Default object changed: '+obj
    for obj in ('u1_tx.o','u1_emit.o'):
        assert (O/'off/obj'/obj).read_bytes()==(O/'on/obj'/obj).read_bytes(), 'Generic core/emitter changed: '+obj
    report['default_binary_and_objects_exact']=True
    report['on_core_and_emitter_objects_exact']=True
    report['passed']=True
finally:
    report['elapsed_seconds']=time.monotonic()-start
    (O/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],elapsed_seconds=report['elapsed_seconds'])))
