#!/usr/bin/env python3
"""Finite actual-source UART1 app/EMOS composition + native link size checks.
Caller must hold its normal Pi build lease. No emulator/target/deployment.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,time,shutil
p=argparse.ArgumentParser();p.add_argument('--emos',type=Path,required=True);p.add_argument('--uart',type=Path,required=True);p.add_argument('--toolchain',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
R=Path(__file__).resolve().parents[3];E=a.emos.resolve();U=a.uart.resolve();T=a.toolchain.resolve();O=a.output.resolve();O.mkdir(parents=True,exist_ok=False)
report=dict(passed=False,scope='actual app/core/EMOS C with fake UART, plus linked eZ80 size; no physical claim',steps=[],inputs={});start=time.monotonic()
def run(label,cmd,cwd=R):
 step=dict(label=label,argv=list(map(str,cmd)));report['steps'].append(step)
 with (O/(label+'.log')).open('x') as f:r=subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 step['returncode']=r.returncode
 if r.returncode:raise RuntimeError(label+' failed; see '+str(O/(label+'.log')))
try:
 for f in [R/'include/agon/net.h',R/'include/agon/net_async.h',Path(__file__),R/'tests/network/async/composition.c',R/'tests/network/async/native.c',E/'src/emos_net.c',E/'src/emos_neta.c',U/'src/u1_tx.c',U/'include/u1_tx.h',U/'src/u1_emit.src']:
  report['inputs'][str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
 fake=O/'fake';fake.mkdir();(fake/'ff.h').write_text('enum {FR_OK=0,FR_TIMEOUT=15,FR_INVALID_PARAMETER=19};\n')
 (fake/'ez80f92.h').write_text('extern unsigned char test_ier;\n#define UART1_IER test_ier\n')
 common=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-endif-labels','-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
 flags=['-DMOS_DEFINES_H','-DEMOS_UART1_APP=1','-DEMOS_UART0_RFC25=1','-DEMOS_BUSY=31','-DEMOS_UNSAFE_CALLER=32','-DEMOS_UNAVAILABLE=35','-include',str(R.parent/'agon-emos/tests/host/defines.h'),'-I'+str(fake),'-I'+str(R.parent/'agon-emos/tests/host'),'-I'+str(E/'src')]
 for n in ('emos_net','emos_neta'):run(n,common+flags+['-c',str(E/'src'/f'{n}.c'),'-o',str(O/f'{n}.o')])
 run('composition-link',common+['-I'+str(R/'include'),'-I'+str(U/'include'),str(R/'tests/network/async/composition.c'),str(U/'src/u1_tx.c'),str(O/'emos_net.o'),str(O/'emos_neta.o'),'-o',str(O/'composition')])
 run('composition-run',[str(O/'composition')])
 # Existing synchronous actual C peer/P4 test is a regression control.
 run('sync-endpoint',common+flags[:1]+flags[3:]+['-c',str(E/'src/emos_net.c'),'-o',str(O/'sync.o')])
 run('sync-peer-link',['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie','-I'+str(R/'vdp/video'),'-I'+str(R/'include'),str(R/'tests/network/messages/peer_test.cpp'),str(O/'sync.o'),'-o',str(O/'sync-peer')])
 run('sync-peer-run',[str(O/'sync-peer')])
 # A link-only program retains all adapter functions and core in application RAM.
 app=O/'native';(app/'src').mkdir(parents=True)
 for src,name in [(R/'tests/network/async/native.c','main.c'),(U/'src/u1_tx.c','u1_tx.c'),(U/'src/u1_emit.src','u1_emit.src')]:shutil.copyfile(src,app/'src'/name)
 (app/'Makefile').write_text('NAME=neta\nAGONDEV_TOOLCHAIN='+str(T)+'\ninclude $(AGONDEV_TOOLCHAIN)/config/makefile.inc\nCFLAGS += -I'+str(R/'include')+' -I'+str(U/'include')+' -Wall -Wextra -Werror\n')
 run('native-link',['make','-j1'],app)
 for obj in sorted((app/'obj').glob('*.o')):
  raw=subprocess.check_output([str(T/'bin/ez80-none-elf-size'),str(obj)],text=True);(O/(obj.stem+'-size.txt')).write_text(raw)
 run('native-elf',[str(T/'bin/ez80-none-elf-ld'),'-defsym=RAM_START=0x40000','-defsym=RAM_SIZE=0x70000','-defsym=_has_exit_handler=0','-Map='+str(O/'native.map'),'-T',str(T/'config/linker.conf'),'-o',str(O/'native.elf'),*map(str,sorted((app/'obj').glob('*.o'))),'-L'+str(T/'lib'),'-lagon'])
 (O/'native-size.txt').write_text(subprocess.check_output([str(T/'bin/ez80-none-elf-size'),str(O/'native.elf')],text=True))
 # Prove default hook additions retain actual synchronous object bytes.
 for variant in ('sync-current','sync-before'):
  folder=O/variant;(folder/'src').mkdir(parents=True)
  shutil.copyfile(R/'tests/network/async/native_sync.c',folder/'src/main.c')
  inc=R/'include'
  if variant=='sync-before':
   inc=folder/'include';(inc/'agon').mkdir(parents=True)
   old=subprocess.check_output(['git','show','72d59b9c:include/agon/net.h'],cwd=R)
   (inc/'agon/net.h').write_bytes(old)
  (folder/'Makefile').write_text('NAME=sync\nAGONDEV_TOOLCHAIN='+str(T)+'\ninclude $(AGONDEV_TOOLCHAIN)/config/makefile.inc\nCFLAGS += -I'+str(inc)+' -Wall -Wextra -Werror\n')
  run(variant+'-link',['make','-j1'],folder)
  (O/(variant+'-size.txt')).write_text(subprocess.check_output([str(T/'bin/ez80-none-elf-size'),str(folder/'obj/main.o')],text=True))
 assert (O/'sync-current/obj/main.o').read_bytes()==(O/'sync-before/obj/main.o').read_bytes(),'Default synchronous object changed'
 report['synchronous_object_unchanged']=True
 report['passed']=True
finally:
 report['elapsed_seconds']=time.monotonic()-start;(O/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],elapsed_seconds=report['elapsed_seconds'])))
