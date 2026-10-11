#!/usr/bin/env python3
"""Build an exact-EMOS-bound timing application; no deployment/emulator changes."""
import argparse
import datetime
import hashlib
import json
import os
import re
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
 p.add_argument('--phase',action='store_true',help='ExExt phase recorder composition')
 p.add_argument('--emos-objects',type=Path,help='retained original C objects required with --phase')
 for name in ('toolchain','emos-elf','emos-bin','output'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args()
 build_id=('port-008-phase-timing-r01-b' if a.phase else 'port-008-stream-timing-r01-b')+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
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
 names=dict(NAMES)
 if a.phase:
  if not a.emos_objects:p.error('--phase requires --emos-objects')
  names.pop('ST_UART');names.pop('ST_LAST_RAW')
  names.update(ST_ARMED='_emos_phase_armed',ST_HOOK='_emos_phase_reserve_begin',ST_OFFER='_offer')
 binding={key:symbols[value] for key,value in names.items()}
 if any(not 0<=binding[k]<131072 for k in (('ST_FLUSH','ST_HOOK') if a.phase else ('ST_FLUSH','ST_UART'))):p.error('private entry outside ROM')
 if any(not 0x0BC000<=binding[k]<0x0C0000 for k in (('ST_ARMED','ST_OFFER','ST_BACKEND','ST_FAULT','ST_OWNED') if a.phase else ('ST_LAST_RAW','ST_BACKEND','ST_FAULT','ST_OWNED'))):p.error('resident state outside expected MOS RAM')
 h=2166136261
 for b in image.ljust(131072,b'\xff'):h=((h^b)*16777619)&0xffffffff
 (a.output/'src').mkdir(parents=True);(a.output/'include').mkdir()
 shutil.copy2(HERE/'main.cpp',a.output/'src/main.cpp')
 counter=(HERE/'counter.asm').read_text()
 if a.phase:
  counter=counter[:counter.index('_st_wire_read:')]
  shutil.copy2(HERE/'phase.asm',a.output/'src/phase.asm')
 (a.output/'src/counter.asm').write_text(counter)
 (a.output/'include/binding.inc').write_text(''.join(f'.equ {k},0x{binding[k]:06X}\n' for k in (('ST_ARMED','ST_HOOK','ST_OFFER','ST_FLUSH') if a.phase else ('ST_LAST_RAW','ST_FLUSH'))))
 for name in ('prt.asm','entries.asm'):
  content=(HERE.parent/'ez80'/name).read_text()
  if name=='prt.asm':content=content.replace('ld a,007h','ld a,00fh').replace('/16','/256')
  (a.output/'src'/name).write_text(content)
 (a.output/'include/binding.hpp').write_text('#pragma once\n'+''.join(f'#define {k} 0x{v:06X}UL\n' for k,v in binding.items())+('#define ST_PHASE 1\n#define ST_UART 0UL\n' if a.phase else '')+f'#define ST_ROM_FNV 0x{h:08X}UL\n#define ST_BUILD_ID "{build_id}"\n')
 (a.output/'Makefile').write_text('NAME=stream\nRAM_START=0xB0000\nRAM_SIZE=0x8000\nLDHAS_ARG_PROCESSING=1\nLDHAS_EXIT_HANDLER=0\ninclude $(shell agondev-config --makefile)\nCXXFLAGS += -std=c++17 -fno-delete-null-pointer-checks\nASMFLAGS += -Iinclude\n')
 env=dict(os.environ);env['PATH']=str(a.toolchain/'bin')+os.pathsep+env.get('PATH','')
 subprocess.run(['make','-C',str(a.output)],env=env,check=True)
 linked=re.findall(r'^\s+(0x[0-9a-f]+)\s+(_\w+)\s*$',(a.output/'bin/stream.map').read_text(),re.M)
 (a.output/'nm.txt').write_text(''.join(f'{int(addr,16):08x} T {name}\n' for addr,name in linked))
 binary=(a.output/'bin/stream.bin').read_bytes()
 phase_sites={}
 if a.phase:
  fsyms={name:int(addr,16) for addr,name in linked}
  vector=fsyms['_phase_record']
  if binary[0x20:0x24]!=bytes(4):p.error('private header vector padding is occupied')
  binary=binary[:0x20]+bytes([0xc3])+vector.to_bytes(3,'little')+binary[0x24:]
  (a.output/'bin/stream.bin').write_bytes(binary)
  for unit in ('emos_exext','emos_parallel_coordinator'):
   obj=a.emos_objects/(unit+'.o')
   ot=subprocess.check_output([str(a.toolchain/'bin/ez80-none-elf-nm'),'-n',str(obj)],text=True)
   osyms={v[2]:int(v[0],16) for line in ot.splitlines() if len(v:=line.split())==3 and v[1].lower()=='t'}
   bases={symbols[n]-off for n,off in osyms.items() if n in symbols}
   if len(bases)!=1:p.error('object/final text mapping is ambiguous')
   base=bases.pop()
   relocs=subprocess.check_output([str(a.toolchain/'bin/ez80-none-elf-objdump'),'-r',str(obj)],text=True)
   for line in relocs.splitlines():
    v=line.split()
    if len(v)!=3 or not v[2].startswith('_emos_phase_'):continue
    operand=base+int(v[0],16);target=symbols[v[2]]
    if image[operand-1:operand+3]!=bytes([0xcd])+target.to_bytes(3,'little'):p.error('probe relocation does not match final CALL')
    phase_sites[str(operand+3)]=v[2].removeprefix('_emos_phase_')
  if len(phase_sites)!=16 or len(set(phase_sites.values()))!=16:p.error('expected sixteen unique phase boundaries')
  (a.output/'phase-sites.json').write_text(json.dumps(phase_sites,indent=2)+'\n')
 if len(binary)>=32768 or binary[0x40:0x45]!=b'MOS\x00\x01':p.error('invalid ADL MOSlet header/size')
 for item in manifest():(a.output/f"stream-{item['wire_bytes']}.bin").write_bytes(stream(item['wire_bytes']))
 record=dict(schema=1,phase=a.phase,phase_sites=phase_sites,private_vector=0xB0020 if a.phase else None,build_id=build_id,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  status='compiled; no physical timing or byte-integrity result',divider=256,
  nominal_hz=18432000,range_seconds=65535*256/18432000,
  header_bytes=11,payloads=manifest(),binding=binding,rom_fnv1a=h,
  emos_sha256=hashlib.sha256(image).hexdigest(),emos_elf_sha256=hashlib.sha256(a.emos_elf.read_bytes()).hexdigest(),
  fixture_layout='MOSlet at 0xB0000, 32 KiB including BSS/stack/heap',
  fixture_sha256=hashlib.sha256((a.output/'bin/stream.bin').read_bytes()).hexdigest())
 (a.output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record,indent=2))
if __name__=='__main__':main()
