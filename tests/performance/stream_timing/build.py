#!/usr/bin/env python3
"""Build an exact-EMOS-bound timing application; no deployment/emulator changes."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from payloads import manifest, stream

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
NAMES={'ST_FLUSH':'_emos_parallel_route_write_stream',
       'ST_UART':'_emos_stream_timing_uart','ST_LAST_RAW':'_emos_stream_timing_last_raw',
       'ST_BACKEND':'_emosVduBackend','ST_FAULT':'_emos_key_faulted','ST_OWNED':'_emos_exext_owned'}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('toolchain','emos-elf','emos-bin','output'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args()
 build_id='port-008-stream-timing-r01-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
 for name in ('toolchain','emos_elf','emos_bin','output'):setattr(a,name,getattr(a,name).resolve())
 if a.output.exists():p.error('output must be a fresh directory')
 image=a.emos_bin.read_bytes()
 if not 0<len(image)<=131072:p.error('EMOS image exceeds physical ROM')
 with tempfile.TemporaryDirectory() as tmp:
  derived=Path(tmp)/'MOS.bin'
  subprocess.run([str(a.toolchain/'bin/ez80-none-elf-objcopy'),'-O','binary',str(a.emos_elf),str(derived)],check=True)
  if derived.read_bytes()!=image:p.error('EMOS ELF and binary do not match')
 text=subprocess.check_output([str(a.toolchain/'bin/ez80-none-elf-nm'),'-n',str(a.emos_elf)],text=True)
 symbols={v[2]:int(v[0],16) for line in text.splitlines() if len(v:=line.split())==3}
 binding={key:symbols[value] for key,value in NAMES.items()}
 if any(not 0<=binding[k]<131072 for k in ('ST_FLUSH','ST_UART')):p.error('private entry outside ROM')
 if any(not 0x0BC000<=binding[k]<0x0C0000 for k in ('ST_LAST_RAW','ST_BACKEND','ST_FAULT','ST_OWNED')):p.error('resident state outside expected MOS RAM')
 h=2166136261
 for b in image.ljust(131072,b'\xff'):h=((h^b)*16777619)&0xffffffff
 (a.output/'src').mkdir(parents=True);(a.output/'include').mkdir()
 shutil.copy2(HERE/'main.cpp',a.output/'src/main.cpp')
 shutil.copy2(HERE/'counter.asm',a.output/'src/counter.asm')
 (a.output/'include/binding.inc').write_text(f'.equ ST_LAST_RAW,0x{binding["ST_LAST_RAW"]:06X}\n')
 for name in ('prt.asm','entries.asm'):
  content=(HERE.parent/'ez80'/name).read_text()
  if name=='prt.asm':content=content.replace('ld a,007h','ld a,00fh').replace('/16','/256')
  (a.output/'src'/name).write_text(content)
 (a.output/'include/binding.hpp').write_text('#pragma once\n'+''.join(f'#define {k} 0x{v:06X}UL\n' for k,v in binding.items())+f'#define ST_ROM_FNV 0x{h:08X}UL\n#define ST_BUILD_ID "{build_id}"\n')
 (a.output/'Makefile').write_text('NAME=stream\nRAM_START=0xB0000\nRAM_SIZE=0x8000\nLDHAS_ARG_PROCESSING=1\nLDHAS_EXIT_HANDLER=0\ninclude $(shell agondev-config --makefile)\nCXXFLAGS += -std=c++17 -fno-delete-null-pointer-checks\nASMFLAGS += -Iinclude\n')
 env=dict(os.environ);env['PATH']=str(a.toolchain/'bin')+os.pathsep+env.get('PATH','')
 subprocess.run(['make','-C',str(a.output)],env=env,check=True)
 binary=(a.output/'bin/stream.bin').read_bytes()
 if len(binary)>=32768 or binary[0x40:0x45]!=b'MOS\x00\x01':p.error('invalid ADL MOSlet header/size')
 for item in manifest():(a.output/f"stream-{item['wire_bytes']}.bin").write_bytes(stream(item['wire_bytes']))
 record=dict(schema=1,build_id=build_id,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  status='compiled; no physical timing or byte-integrity result',divider=256,
  nominal_hz=18432000,range_seconds=65535*256/18432000,
  header_bytes=11,payloads=manifest(),binding=binding,rom_fnv1a=h,
  emos_sha256=hashlib.sha256(image).hexdigest(),emos_elf_sha256=hashlib.sha256(a.emos_elf.read_bytes()).hexdigest(),
  fixture_layout='MOSlet at 0xB0000, 32 KiB including BSS/stack/heap',
  fixture_sha256=hashlib.sha256((a.output/'bin/stream.bin').read_bytes()).hexdigest())
 (a.output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record,indent=2))
if __name__=='__main__':main()
