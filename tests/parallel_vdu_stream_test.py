"""Actual ordinary ExExt queue/control owner, with modeled physical completion."""
from pathlib import Path
import subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class ParallelVduTest(unittest.TestCase):
 def test_stream(self):
  with tempfile.TemporaryDirectory() as tmp:
   exe=Path(tmp)/'stream'
   subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic',
    '-fsanitize=address,undefined','-fno-sanitize-recover=all',f'-I{ROOT/"vdp/video"}',
    str(ROOT/'tests/parallel_vdu_stream_test.cpp'),
    str(ROOT/'vdp/video/extender/transport/p4_parallel_handover.cpp'),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=30)
if __name__=='__main__':unittest.main()
