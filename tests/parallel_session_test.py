"""Paired maintained session owners; emit exact EMOS vectors for linked checks."""
from pathlib import Path
import os, subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
EMOS=Path(os.environ.get('AGON_EMOS_ROOT',ROOT.parent/'agon-emos'))
class ParallelSessionTests(unittest.TestCase):
 def test_mirrored_lifecycle(self):
  self.assertEqual((ROOT/'vdp/video/extender/transport/parallel_session.h').read_bytes(),
                   (EMOS/'src/emos_parallel_session.h').read_bytes())
 def test_real_owners(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);obj=d/'console.o';hand=d/'handover.o';exe=d/'session'
   flags=['-Wall','-Wextra','-Werror','-Wno-endif-labels','-ffunction-sections','-fdata-sections',
          '-fsanitize=address,undefined','-fno-sanitize-recover=all']
   inc=[f'-I{EMOS/"tests/host"}',f'-I{EMOS/"src"}',f'-I{ROOT/"vdp/video"}']
   subprocess.run(['cc','-std=c17',*flags,*inc,'-c',str(EMOS/'src/emos_console.c'),'-o',str(obj)],check=True)
   subprocess.run(['cc','-std=c17',*flags,*inc,'-c',str(EMOS/'src/emos_parallel_handover.c'),'-o',str(hand)],check=True)
   subprocess.run(['c++','-std=c++17',*flags,*inc,str(obj),str(hand),
     str(ROOT/'tests/parallel_session_test.cpp'),str(ROOT/'vdp/video/extender/transport/p4_parallel_handover.cpp'),
     '-Wl,--gc-sections','-o',str(exe)],check=True)
   args=[str(exe)]
   if os.environ.get('SESSION_VECTORS'):args.append(os.environ['SESSION_VECTORS'])
   subprocess.run(args,check=True)
if __name__=='__main__':unittest.main()
