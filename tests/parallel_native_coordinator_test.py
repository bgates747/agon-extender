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
  if os.environ.get("AGON_NETWORK_PARALLEL"):
   self.skipTest("NETP uses NP admission; exercise retained EX donor in the probe pairing")
  self.run_pair(False)
 def test_qualification_pair(self):
  self.run_pair(True)
 def test_network_pair(self):
  if not os.environ.get("AGON_NETWORK_PARALLEL"):self.skipTest("optional NETP composition")
  self.run_pair(False,True)
 def run_pair(self,probe,network=False):
  clock=monotonic()
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);prepare_sdk(d)
   (d/'ez80f92.h').write_text('#include "eZ80.h"\n')
   (d/'ff.h').write_text('enum {FR_OK=0,FR_TIMEOUT=15,FR_INVALID_PARAMETER=19};\n')
   flags=['-Wall','-Wextra','-Werror','-Wno-endif-labels','-ffunction-sections','-fdata-sections',
    '-fsanitize=address,undefined','-fno-sanitize-recover=all',
    '-DMOS_DEFINES_H=1','-DMOS_AGONDEV_LOWERCASE_EZ80_H=1','-DEMOS_BUSY=31','-DEMOS_UNAVAILABLE=35']
   if probe:flags+=['-DEMOS_PARALLEL_PROBE=1']
   netp=bool(os.environ.get('AGON_NETWORK_PARALLEL'))
   if netp:flags+=['-DEMOS_NETWORK_PARALLEL=1']
   inc=[f'-I{d}',f'-I{ROOT.parent/"agon-emos/tests/host"}',f'-I{EMOS/"src"}',f'-I{ROOT/"vdp/video"}']
   objects=[]
   units=['emos_console','emos_parallel_handover','emos_parallel_boot','emos_parallel_startup',
          'emos_parallel_native','emos_parallel_coordinator']
   if netp:units+=['emos_parallel_upload']
   if network:units+=['emos_netp_link']
   for name in units:
    obj=d/(name+'.o');objects.append(str(obj))
    subprocess.run(['cc','-std=c17',*flags,*inc,'-include','eZ80.h',
     '-DEMOS_PARALLEL_NATIVE_COORDINATOR=1','-c',str(EMOS/'src'/(name+'.c')),'-o',str(obj)],check=True)
   prefix=(ROOT/'tests/p4_native_payload_test.cpp').read_text().split('int main(){')[0]
   prefix=prefix.replace('static H admitted(', '[[maybe_unused]] static H admitted(')
   uart=(ROOT/'tests/p4_block_coordinator_test.cpp').read_text().split('static void boot(')[0]
   body=(ROOT/'tests/parallel_native_coordinator_test.cpp').read_text()
   extra=''
   if network:
    extra,main=(ROOT/'tests/parallel_network_pair_test.cpp').read_text().split('// BODY\n')
    body=body.replace('int main(){','int retained_donor_cases(){')
    body=body.rstrip()[:-1]+' return 0;\n}\n'
    body=body.replace('if(owner)result=owner->poll(++now,true,true);',
                      'if(owner){result=owner->poll(++now,true,true);if(netp)assert(netp->retire());}')
    body=body.replace('assert(peer.request(p,now,0x12340000+(++challengeSerial),reply));',
                      'if(netp&&netp->ownsControl(p))assert(netp->request(p,reply,true,now));else assert(peer.request(p,now,0x12340000+(++challengeSerial),reply));')
    body+='\n'+main
   source=d/'pair.cpp';source.write_text(prefix+uart+extra+body)
   exe=d/'pair'
   subprocess.run(['c++','-std=c++17',*flags,*inc,*objects,str(source),
    *[str(ROOT/'vdp/video/extender/transport'/(s+'.cpp')) for s in
    ('p4_block_coordinator','p4_native_payload','p4_uart_parking','p4_parallel_handover','p4_parallel_egress')],
    '-Wl,--gc-sections','-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=30)
  print(f'Paired native coordinator host compile/test: {monotonic()-clock:.6f} seconds; no electrical timing')
if __name__=='__main__':unittest.main()
