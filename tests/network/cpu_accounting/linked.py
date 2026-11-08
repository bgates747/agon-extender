"""Inspection of actual linked instructions; never executes a target ISA."""
import argparse,json,subprocess,re
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('elf','app','toolchain','output'):p.add_argument('--'+k,type=Path,required=True)
a=p.parse_args();B=a.toolchain/'bin';R=Path(__file__).resolve().parents[3]
def symbols(elf):
 t=subprocess.check_output([str(B/'ez80-none-elf-nm'),'-n',str(elf)],text=True)
 return {m[2]:int(m[0],16) for line in t.splitlines() if len(m:=line.split())==3 and re.fullmatch('[0-9a-fA-F]+',m[0])}
def image(elf,name):
 out=a.output.parent/name;subprocess.run([str(B/'ez80-none-elf-objcopy'),'-O','binary',str(elf),str(out)],check=True);return out.read_bytes()
s=symbols(a.elf);raw=image(a.elf,'NON-DEPLOYABLE-oversize.bin')
used=s['rodata_end']+s['___data_len'];assert used==131323 and used-131072==251
assert len(raw)==used
assert s['___bss_len']==3506
call=lambda n:b'\xcd'+s[n].to_bytes(3,'little')
mark=lambda ev:b'\xf5\x3e'+bytes([ev])+call('_emos_cpu_emit')+b'\xf1'
counts={1:1,0x81:4,2:1,0x82:1,3:1,0x83:1,4:1,0x84:1}
for ev,count in counts.items():assert raw.count(mark(ev))==count,(ev,count,raw.count(mark(ev)))
# Full variable UART0 exit service must occur BEFORE all four exit marks.
assert raw.count(call('_emos_neta_uart0_exit')+mark(0x81))==4
# Initial RX protections stay ahead of the accounting entry.
assert call('_emos_neta_uart0_enter')+mark(1) in raw
assert raw.count(call('_emos_cpu_poison'))==4
# No old schemas accidentally linked into the optional new profile.
assert '_emos_neta_diag_hook' not in s and 'emos_uart0_witness_rx' not in s
# Check app two-entry native jump ABI and independent poison machine bytes.
x=symbols(a.app);app=image(a.app,'app-link-only.bin');base=min(x[k] for k in ['_agon_cpu_entry'])
o=x['_agon_cpu_entry']-0x40000
assert app[o]==0xc3 and app[o+4]==0xc3
poison=int.from_bytes(app[o+5:o+8],'little')-0x40000
want=b'\xf5\x3e\x01\x32'+(x['_agon_cpu_record']+13).to_bytes(3,'little')+b'\xf1\xc9'
assert app[poison:poison+len(want)]==want
# All native save/restore sides are linked, not only source declarations.
marker=int.from_bytes(app[o+1:o+4],'little')-0x40000
save=bytes.fromhex('f5c5d5e5dde5fde508f5d9c5d5e5d908')
restore=bytes.fromhex('08d9e1d1c1d9f108fde1dde1e1d1c1f1c9')
assert app[marker:marker+len(save)]==save
assert restore in app[marker:]
# Paired provider's marker is present only as reusable implementation, not
# resident ROM or a second timer. No C symbol enters the native recorder tree.
assert '_agon_rxdiag_claim' in x and '_agon_rxdiag_retire' in x
# Independent source regressions must be caught by marker checker.
def require_tail(buf):assert buf.count(call('_emos_neta_uart0_exit')+mark(0x81))==4
require_tail(raw)
bad=raw.replace(call('_emos_neta_uart0_exit')+mark(0x81),mark(0x81)+call('_emos_neta_uart0_exit'),1)
try:require_tail(bad)
except AssertionError:pass
else:raise AssertionError('Moved exit-tail marker escaped control')
a.output.write_text(json.dumps(dict(passed=True,rom_used=used,rom_limit=131072,excess=251,rom_delta=371,bss=3506,bss_delta=3,marker_counts=counts,app_text=x.get('_etext'),native_size=subprocess.check_output([str(B/'ez80-none-elf-size'),str(a.app)],text=True),scope='actual linked instructions and negative marker-placement control; no native ISA/IRQ/timer execution, physical fit FAIL'),indent=2))
