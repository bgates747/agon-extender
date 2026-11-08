"""Finite actual-C and source-boundary controls; no IRQ/ISA/device run."""
from pathlib import Path
import argparse,subprocess,json,sys
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();O=a.output.resolve();O.mkdir(exist_ok=False)
R=Path(__file__).resolve().parents[3];S=R/'agents/net004/cpu-accounting-fit-r04/source';U=R.parent/'MechAgon/.runtime/goal001/turn-work-size-check-r01/owner/u1'
steps=[]
def run(name,cmd):
 with (O/(name+'.log')).open('x') as f:r=subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT,timeout=30)
 steps.append(dict(name=name,returncode=r.returncode));assert r.returncode==0,(name,O/(name+'.log'))
common=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-endif-labels','-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
run('lifecycle-build',common+['-I'+str(R/'include/agon/cpu_accounting'),R/'include/agon/cpu_accounting/accounting.c',R/'tests/network/cpu_accounting/lifecycle.c','-o',O/'lifecycle'])
for n in range(9):run('lifecycle-'+str(n),[O/'lifecycle',str(n)])
fake=O/'fake';fake.mkdir();(fake/'ff.h').write_text('enum {FR_OK=0,FR_TIMEOUT=15,FR_INVALID_PARAMETER=19};\n');(fake/'ez80f92.h').write_text('extern unsigned char test_ier;\n#define UART1_IER test_ier\n')
flags=['-DMOS_DEFINES_H','-DEMOS_UART1_APP=1','-DEMOS_UART0_RFC25=1','-DEMOS_CPU_ACCOUNTING=1','-DEMOS_BUSY=31','-DEMOS_UNSAFE_CALLER=32','-DEMOS_UNAVAILABLE=35','-include',str(R.parent/'agon-emos/tests/host/defines.h'),'-I'+str(fake),'-I'+str(R.parent/'agon-emos/tests/host'),'-I'+str(S/'src')]
for n in ('emos_net','emos_neta'):run(n,common+flags+['-c',S/'src'/f'{n}.c','-o',O/f'{n}.o'])
run('composition-build',common+['-I'+str(R/'include'),'-I'+str(U/'include'),Path(__file__).with_name('composition.c'),U/'src/u1_tx.c',O/'emos_net.o',O/'emos_neta.o','-o',O/'composition'])
run('composition-lifetimes',[O/'composition'])
for n in range(1,11):run('composition-admission-'+str(n),[O/'composition',str(n)])
# Deliberate source regressions must fail checks. These do not emulate ISR time.
def hooks(src):
 x=src/'interrupts.asm';t=x.read_text();assert 'CALL _emos_neta_uart0_enter\n            EMOS_CPU 1' in t
 assert 'CALL _emos_neta_uart0_exit\n            EMOS_CPU 0x81' in t
 assert '_i2c_handler:\n            EMOS_CPU_INVALID' in t
 t=(src/'emos_uart0_rfc25_io.asm').read_text();assert t.count('CALL _emos_neta_uart0_exit\n            EMOS_CPU 0x81')==4
 assert t.count('jr uart0_cpu_tail')==2
 t=(src/'emos_keyboard_io.asm').read_text();b=t[t.index('_emos_keyboard_irq_entry:'):t.index('emos_keyboard_tick_entry:')]
 assert b.index('EMOS_CPU 2')<b.index('CALL emos_uart0_rx_first')<b.index('EMOS_CPU 0x82')
 assert b.rindex('CALL emos_uart0_reserve_leave')<b.index('EMOS_CPU 0x82')
 t=(src/'handlers.asm').read_text();assert t.count('EMOS_CPU_INVALID')==3
hooks(S/'src')
# Poison cannot touch shared marker scratch; marker is native and timer-only.
t=(R/'include/agon/cpu_accounting/accounting.s').read_text();b=t[t.index('poison:'):t.index('; Independent foreground')]
assert '_agon_cpu_record+13' in b and 'event' not in b and 'sample' not in b
b=t[t.index('marker:'):];assert 'call _' not in b and ' ei' not in b and 'reti' not in b.lower()
for bad in ['0xd0','0xd5','0xc0','0xc5','0x9e']:assert bad not in b.lower()
for op in ['push af','push bc','push de','push hl','push ix','push iy',"ex af,af'",'exx','pop ix','pop iy']:assert op in b
assert 'ld (_agon_cpu_record+22),hl' not in b,'24-bit store would overwrite class'
assert '54001' in b and 'jp c,clock_bad' in b and 'scf' in b
(O/'result.json').write_text(json.dumps(dict(passed=True,actual_C_lifecycle=9,actual_C_composition=11,steps=steps,scope='native C under explicit peripheral stubs and source boundary controls; no IRQ/ISA/timer execution'),indent=2))
