"""Actual EMOS foreground/startup/console and P4 native coordinator pairing.

SDK, registers, IRQ scheduling, byte-clock assembly and UART boundary calls are
modeled here. Separate linked-eZ80 suites execute the real assembly/adapters.
"""
from pathlib import Path
from time import monotonic
import os,subprocess,tempfile,unittest
from p4_block_coordinator_test import prepare_sdk
ROOT=Path(__file__).resolve().parents[1]
EMOS=Path(os.environ.get('AGON_EMOS_ROOT',ROOT.parent/'agon-emos'))
class NativePairTest(unittest.TestCase):
 def test_pair(self):
  clock=monotonic()
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);prepare_sdk(d)
   flags=['-Wall','-Wextra','-Werror','-Wno-endif-labels','-ffunction-sections','-fdata-sections',
    '-fsanitize=address,undefined','-fno-sanitize-recover=all']
   inc=[f'-I{d}',f'-I{EMOS/"tests/host"}',f'-I{EMOS/"src"}',f'-I{ROOT/"vdp/video"}']
   objects=[]
   for name in ('emos_console','emos_parallel_handover','emos_parallel_boot','emos_parallel_startup',
                'emos_parallel_native','emos_parallel_coordinator'):
    obj=d/(name+'.o');objects.append(str(obj))
    subprocess.run(['cc','-std=c17',*flags,*inc,'-include','eZ80.h',
     '-DEMOS_PARALLEL_NATIVE_COORDINATOR=1','-c',str(EMOS/'src'/(name+'.c')),'-o',str(obj)],check=True)
   prefix=(ROOT/'tests/p4_native_payload_test.cpp').read_text().split('int main(){')[0]
   prefix=prefix.replace('static H admitted(', '[[maybe_unused]] static H admitted(')
   uart=(ROOT/'tests/p4_block_coordinator_test.cpp').read_text().split('static void boot(')[0]
   source=d/'pair.cpp';source.write_text(prefix+uart+(ROOT/'tests/parallel_native_coordinator_test.cpp').read_text())
   exe=d/'pair'
   subprocess.run(['c++','-std=c++17',*flags,*inc,*objects,str(source),
    *[str(ROOT/'vdp/video/extender/transport'/(s+'.cpp')) for s in
    ('p4_block_coordinator','p4_native_payload','p4_uart_parking','p4_parallel_handover','p4_parallel_egress')],
    '-Wl,--gc-sections','-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=30)
  print(f'Paired native coordinator host compile/test: {monotonic()-clock:.6f} seconds; no electrical timing')
if __name__=='__main__':unittest.main()
