"""Finite linked-leaf interpreter with explicit recorder stub, not an IRQ emulator."""
import argparse,copy,json,re,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('elf','app','toolchain','source','output'):p.add_argument('--'+k,type=Path,required=True)
a=p.parse_args();B=a.toolchain/'bin'
sys.path.insert(0,str(a.source/'projects/emos'))
from verify_parallel import instructions,disassemble_global_extent

def symbols(elf):
 t=subprocess.check_output([str(B/'ez80-none-elf-nm'),'-n',str(elf)],text=True)
 return {v[2]:int(v[0],16) for l in t.splitlines() if len(v:=l.split())==3 and re.fullmatch('[0-9a-fA-F]+',v[0])}
def binary(elf,out):
 subprocess.run([str(B/'ez80-none-elf-objcopy'),'-O','binary',str(elf),str(out)],check=True)
 return out.read_bytes()
s=symbols(a.elf);x=symbols(a.app);raw=binary(a.elf,a.output.with_suffix('.rom.bin'));app=binary(a.app,a.output.with_suffix('.app.bin'))
used=s['rodata_end']+s['___data_len'];assert len(raw)==used
assert s['_emos_cpu_target']==s['_emos_cpu_dispatch']+1>=0xb0000
# The four RAM bytes are initialized data, not read from uninitialized BSS.
load=s['rodata_end']+s['_emos_cpu_dispatch']-s['___data_start']
assert raw[load:load+4]==b'\xc3'+s['_emos_cpu_none'].to_bytes(3,'little')
none=raw[s['_emos_cpu_none']:s['_emos_cpu_none']+4];assert none==bytes.fromhex('e3 23 e3 c9')

# Every association/removal publishes a single24-bit target instruction. The
# opcode byte is initialized once and is never part of a lifecycle write.
atomic_target_stores={}
for name in ('_emos_neta_open','_emos_neta_close','_emos_neta_abort'):
 rows=instructions(disassemble_global_extent(B/'ez80-none-elf-objdump',a.elf,name))
 hits=[(op,arg) for _,op,arg in rows if hex(s['_emos_cpu_target']) in arg]
 assert len(hits)==1 and hits[0][0]=='ld' and hits[0][1].replace(' ','') in tuple('('+hex(s['_emos_cpu_target'])+'),'+r for r in ('hl','de','iy','ix')), (name,hits)
 atomic_target_stores[name]=hits[0]

call=lambda n:b'\xcd'+s[n].to_bytes(3,'little')
mark=lambda e:call('_emos_cpu_dispatch')+bytes([e])
counts={1:1,0x81:2,2:1,0x82:1,3:1,0x83:1,4:1,0x84:1,255:4}
for e,n in counts.items():assert raw.count(mark(e))==n,(e,n)
def tails(buf):assert buf.count(call('_emos_neta_uart0_exit')+mark(0x81))==2
tails(raw)
bad=raw.replace(call('_emos_neta_uart0_exit')+mark(0x81),mark(0x81)+call('_emos_neta_uart0_exit'),1)
try:tails(bad)
except AssertionError:pass
else:raise AssertionError('moved exit marker accepted')
base=0x40000;veneer=x['_agon_cpu_service_entry']-base
assert app[veneer:veneer+8]==b'\xc3'+x['_agon_neta_service'].to_bytes(3,'little')+b'\xc3'+x['_agon_cpu_inline_entry'].to_bytes(3,'little')
entry=x['_agon_cpu_entry']-base
assert app[entry]==app[entry+4]==0xc3
marker=int.from_bytes(app[entry+1:entry+4],'little')-base
assert app[marker:marker+16]==bytes.fromhex('f5c5d5e5dde5fde508f5d9c5d5e5d908')
assert bytes.fromhex('08d9e1d1c1d9f108fde1dde1e1d1c1f1c9') in app[marker:]
# Use actual linked instructions; reject every operation outside this leaf set.
start=x['_agon_cpu_inline_entry'];end=x['inline_poison']+12
text=subprocess.check_output([str(B/'ez80-none-elf-objdump'),'-d','--start-address='+hex(start),'--stop-address='+hex(end),str(a.app)],text=True)
(a.output.parent/'adapter-disassembly.txt').write_text(text)
rows=instructions(text);code={v[0]:(rows[i+1][0] if i+1<len(rows) else end,v[1],v[2].split(';')[0].strip()) for i,v in enumerate(rows)}
# Validate linked decode/consume/save shape, independently of model results.
assert [op for _,op,_ in rows[:15]]==['push','push','push','ld','add','ld','ld','inc','ld','pop','pop','cp','jr','call','pop']
assert rows[5][2].replace(' ','') in ('hl,(ix+0x9)','hl,(ix+9)')
assert rows[8][2].replace(' ','') in ('(ix+0x9),hl','(ix+9),hl')

def target(arg):
 vals=re.findall(r'0x([0-9a-f]+)',arg);assert vals,arg;return int(vals[-1],16)
def model(event,seed,iff,inject=None,unassociated=False):
 regs={n:(0x310000+i*0x12345+seed*37)&0xffffff for i,n in enumerate(('af','bc','de','hl','ix','iy','af2','bc2','de2','hl2'))}
 regs['af']&=0xffff;regs['af2']&=0xffff;regs['sp']=0x90000;regs['iff']=iff
 memory={};observed=[];poison=x['_agon_cpu_record']+13
 def put24(at,v):
  for i in range(3):memory[at+i]=(v>>(8*i))&255
 def get24(at):return sum(memory.get(at+i,0)<<(8*i) for i in range(3))
 def push(v):regs['sp']-=3;put24(regs['sp'],v)
 def pop():v=get24(regs['sp']);regs['sp']+=3;return v
 original=regs.copy();memory[0x88000]=event;push(0x88000)
 def run_leaf(pc,interrupt=False):
  initial_sp=regs['sp'];step=0
  while True:
   assert step<40,'leaf exceeded finite instruction bound'
   if not interrupt and inject==step:
    saved=regs.copy();prior=dict(memory);push(0x88100);memory[0x88100]=255
    ret=run_leaf(start,True);assert ret==0x88101 and regs==saved
    assert memory[poison]==1
    # Only poison and nested stack/return storage may differ.
    assert all(v==prior[k] for k,v in memory.items() if k in prior and not (regs['sp']-32<=k<regs['sp']) and k not in (poison,0x88100))
   if unassociated and not interrupt:
    # Actual four linked opcodes above: EX(SP),HL;INC HL;EX(SP),HL;RET.
    assert none==bytes.fromhex('e323e3c9');v=get24(regs['sp']);put24(regs['sp'],v+1)
    return pop()
   nxt,op,arg=code[pc];arg=arg.replace(' ','');step+=1;pc=nxt
   if op=='push':push(regs[arg])
   elif op=='pop':regs[arg]=pop()
   elif op=='ld':
    if re.fullmatch(r'ix,(?:0x)?0+',arg):regs['ix']=0
    elif arg in ('hl,(ix+0x9)','hl,(ix+9)'):regs['hl']=get24(regs['ix']+9)
    elif arg=='a,(hl)':regs['af']=(memory[regs['hl']]<<8)|(regs['af']&255)
    elif arg in ('(ix+0x9),hl','(ix+9),hl'):put24(regs['ix']+9,regs['hl'])
    elif re.fullmatch(r'a,(?:0x)?0*1',arg):regs['af']=0x100|(regs['af']&255)
    elif arg.endswith(',a'):
     addr=target(arg);assert addr==poison;memory[addr]=(regs['af']>>8)&255
    else:raise AssertionError(('unadmitted linked LD',arg))
   elif op=='add':
    assert arg=='ix,sp';regs['ix']=(regs['ix']+regs['sp'])&0xffffff
    regs['af']=(regs['af']&0xff00)|0x11 # flags are caller-clobbered, restored from stack
   elif op=='inc':assert arg=='hl';regs['hl']=(regs['hl']+1)&0xffffff
   elif op=='cp':
    assert arg in ('a,0xff','0xff','255');v=(regs['af']>>8)&255
    regs['af']=(regs['af']&0xff00)|(0x40 if v==255 else 1)
   elif op=='jr':
    assert arg.startswith('z,')
    if regs['af']&0x40:
     # objdump prints this JR's target modulo16bits; decode the actual signed
     # linked displacement, retaining the executing24-bit address.
     delta=app[nxt-base-1];pc=nxt+(delta if delta<128 else delta-256)
   elif op=='call':
    assert target(arg)==x['_agon_cpu_entry'];observed.append((regs['af']>>8)&255)
    # Explicit unchanged all-register/IFF recorder stub; no timer arithmetic run.
   elif op=='ret':
    assert regs['sp']==initial_sp;return pop()
   else:raise AssertionError(('unadmitted linked operation',op,arg))
 ret=run_leaf(start);assert ret==0x88001 and regs==original
 assert observed==([] if event==255 or unassociated else [event])
 assert (memory.get(poison,0)==1)==(event==255 or inject is not None)
 return True
cases=0
for seed in (0,11):
 for iff in (False,True):
  for ev in (1,2,3,4,6,7,0x81,0x82,0x83,0x84,0x86,255):model(ev,seed,iff);cases+=1
  for boundary in range(16):model(0x81,seed,iff,inject=boundary);cases+=1
  model(1,seed,iff,unassociated=True);cases+=1
# Actual object bytes, size and scope are retained, not silently called ISA/IRQ execution.
a.output.write_text(json.dumps(dict(passed=True,rom_used=used,rom_limit=131072,rom_free=131072-used,rom_delta=used-130952,bss=s['___bss_len'],data=s['___data_len'],inline_leaf_cases=cases,marker_counts=counts,atomic_target_stores=atomic_target_stores,scope='actual linked shape + finite leaf interpreter, explicit unchanged recorder stub; no native recorder/IRQ/timer execution or timing claim',native_size=subprocess.check_output([str(B/'ez80-none-elf-size'),str(a.app)],text=True)),indent=2))
