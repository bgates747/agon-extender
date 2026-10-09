"""Compile actual maintained owners; exercise the framed callback boundary."""
from pathlib import Path
import os, subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
EMOS=Path(os.environ.get('AGON_EMOS_ROOT',ROOT.parent/'agon-emos'))
class ParallelControlTests(unittest.TestCase):
 def test_owners(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);obj=d/'console.o';hand=d/'handover.o';exe=d/'control'
   flags=['-Wall','-Wextra','-Werror','-Wno-endif-labels','-ffunction-sections','-fdata-sections',
          '-fsanitize=address,undefined','-fno-sanitize-recover=all']
   inc=[f'-I{EMOS/"tests/host"}',f'-I{EMOS/"src"}',f'-I{ROOT/"vdp/video"}']
   for source,out in [('emos_console.c',obj),('emos_parallel_handover.c',hand)]:
    subprocess.run(['cc','-std=c17',*flags,*inc,'-c',str(EMOS/'src'/source),'-o',str(out)],check=True)
   subprocess.run(['c++','-std=c++17',*flags,*inc,str(obj),str(hand),
     str(ROOT/'tests/parallel_control_test.cpp'),str(ROOT/'vdp/video/extender/transport/p4_parallel_handover.cpp'),
     '-Wl,--gc-sections','-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=20)
if __name__=='__main__':unittest.main()
