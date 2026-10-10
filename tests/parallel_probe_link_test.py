"""Actual-ELF selection and activation-owner negative controls; no bench."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[1]
EMOS=ROOT.parent/'agon-emos'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('probe','native','ordinary','toolchain'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args()
    checks=0
    def check(image,profile,success,reason=''):
        nonlocal checks
        r=subprocess.run([sys.executable,str(EMOS/'projects/emos'/('verify_parallel'+profile+'.py')),
            '--source',str(EMOS),'--elf',str(image),'--nm',str(a.toolchain/'bin/ez80-none-elf-nm'),
            '--objdump',str(a.toolchain/'bin/ez80-none-elf-objdump')],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        assert (r.returncode==0)==success and reason in r.stdout,r.stdout
        checks+=1;print(('PASS' if success else 'REFUSED')+' '+profile+': '+r.stdout.strip())
    check(a.probe,'_probe',True)
    check(a.native,'_native',True)
    check(a.ordinary,'',True)
    check(a.probe,'_native',False,'unreviewed activation caller')
    check(a.native,'_probe',False,'unreviewed activation caller')
    check(a.probe,'',False,'ordinary image links private native payload symbols')
    with a.probe.open('rb') as f:
        e=ELFFile(f);symbols={s.name:s for s in e.get_section_by_name('.symtab').iter_symbols()}
        def offset(name):
            s=symbols[name];section=e.get_section(s['st_shndx'])
            return s['st_value']+section['sh_offset']-section['sh_addr']
        original=a.probe.read_bytes()
        gate=symbols['_emos_parallel_probe']['st_value']
        coordinate=symbols['_emos_parallel_native_coordinate']['st_value']
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'mutant.elf'
            # Break the gateway's actual sole call, leaving linked symbols intact.
            call=bytes((0xcd,))+gate.to_bytes(3,'little')
            at=original.index(call,offset('_emos_uartdiag_gateway'))
            data=bytearray(original);data[at+1:at+4]=(gate+1).to_bytes(3,'little');target.write_bytes(data)
            check(target,'_probe',False,'qualification activation escaped its sole MOSlet gateway owner')
            # Manufacture an extra activation call by redirecting a real call
            # inside the probe's orchestration, rather than editing the symbol table.
            negotiate=symbols['_emos_parallel_session_negotiate']['st_value']
            call=bytes((0xcd,))+negotiate.to_bytes(3,'little')
            at=original.index(call,offset('_emos_parallel_probe'))
            data=bytearray(original);data[at+1:at+4]=coordinate.to_bytes(3,'little');target.write_bytes(data)
            check(target,'_probe',False,'unreviewed activation caller')
    print(f'PASS {checks} actual-ELF private qualification/profile controls')

if __name__=='__main__':main()
