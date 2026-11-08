#!/usr/bin/env python3
"""Build only the finite EMOS-owned async echo isolation, never deploy/run."""
import argparse, datetime, hashlib, json, os, shutil, subprocess, time
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--toolchain',type=Path,required=True)
 p.add_argument('--uart-source',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 select=p.add_mutually_exclusive_group()
 select.add_argument('--uart0-carry',action='store_true',help='Build separately selected finite UART0 cursor isolation; old fixture unchanged')
 select.add_argument('--uart0-reserve',action='store_true',help='Build new MODE/cursor logical overlap owner isolation; no GP')
 a=p.parse_args();root=Path(__file__).resolve().parents[3]
 output=a.output.resolve();output.mkdir(exist_ok=False,parents=True)
 work=output/'work';src=work/'src';(src/'agon').mkdir(parents=True)
 inputs={
 'main.cpp':root/('tests/fixtures/network/uart0_reserve_repeat.cpp' if a.uart0_reserve else 'tests/fixtures/network/uart0_carry_repeat.cpp' if a.uart0_carry else 'tests/fixtures/network/async_repeat.cpp'),
 'async_carrier.hpp':root/'tests/fixtures/network/async_carrier.hpp',
 'endpoint.hpp':root/'tests/fixtures/network/endpoint.hpp',
 'repeat_matrix.hpp':root/'tests/fixtures/network/repeat_matrix.hpp',
 'mode_lifecycle.hpp':root/'tests/fixtures/scroll/mode_lifecycle.hpp',
 'mos_io.asm':root/'tests/fixtures/controller/mos_io.asm',
 'net_callback.asm':root/'include/agon/net_callback.asm',
 'agon/net.h':root/'include/agon/net.h',
 'agon/net_async.h':root/'include/agon/net_async.h',
 'u1_tx.c':a.uart_source/'src/u1_tx.c',
 'u1_tx.h':a.uart_source/'include/u1_tx.h',
 'u1_emit.src':a.uart_source/'src/u1_emit.src',
 }
 if a.uart0_carry:inputs['uart0_cursor.hpp']=root/'tests/fixtures/network/uart0_cursor.hpp'
 if a.uart0_reserve:inputs['uart0_reply_burst.hpp']=root/'tests/fixtures/network/uart0_reply_burst.hpp'
 for name,file in inputs.items():shutil.copyfile(file,src/name)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
 identity=('netasync-uart0-reserve-r01-b' if a.uart0_reserve else 'netasync-uart0-carry-r01-b' if a.uart0_carry else 'netasync-r01-b')+stamp
 (src/'build_identity.h').write_text('#define NETPROBE_BUILD_ID "'+identity+'"\n')
 (work/'Makefile').write_text('NAME=netasync\nLDHAS_ARG_PROCESSING=1\nLDHAS_EXIT_HANDLER=0\nAGONDEV_TOOLCHAIN='+str(a.toolchain.resolve())+'\ninclude $(AGONDEV_TOOLCHAIN)/config/makefile.inc\nCFLAGS += -Isrc -Wall -Wextra -Werror\nCXXFLAGS += -Isrc -std=c++17 -fno-exceptions -fno-rtti -Wall -Wextra -Werror\n')
 report=dict(build_id=identity,scope='native compile/link only, no invocation',
  source_commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
  inputs={str(file):hashlib.sha256(file.read_bytes()).hexdigest() for file in inputs.values()},
  records=176,sessions=4,irq_complete=0,uart0_cursor_queries=(352 if a.uart0_carry else 0),uart0_reply_bursts=(352 if a.uart0_reserve else 0),query_kinds=(["MODE","cursor"] if a.uart0_reserve else []),native_budget_nominal_seconds=(60 if a.uart0_carry or a.uart0_reserve else 120))
 start=time.monotonic()
 try:
  with (output/'build.log').open('w') as log:
   subprocess.run(['make','-j1','-C',str(work)],env=dict(os.environ,PATH=str(a.toolchain.resolve()/'bin')+os.pathsep+os.environ['PATH']),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
  shutil.copyfile(work/'bin/netasync.bin',output/'netasync.bin')
  b=(output/'netasync.bin').read_bytes();report['binary']=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest());report['passed']=True
 finally:
  report['seconds']=time.monotonic()-start;(output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report))
if __name__=='__main__':main()
