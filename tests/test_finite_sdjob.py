"""Portable paired control/engine qualification, no emulator or bench access."""
from pathlib import Path
import subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
EMOS=ROOT.parent/'agon-emos'
class FiniteJobTests(unittest.TestCase):
 def test_actual_utility_peer_and_engine(self):
  with tempfile.TemporaryDirectory() as directory:
   work=Path(directory);objects=[]
   for source,name,extra in [(EMOS/'projects/sdjob/src/job.c','job',[]),
                            (EMOS/'projects/sdserve/src/service.c','engine',[]),
                            (EMOS/'tests/sdserve_host/fs.c','fs',['-Dservice_progress=fs_progress_callback'])]:
    obj=work/(name+'.o');objects.append(str(obj))
    subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',
      '-g','-fsanitize=address,undefined','-I'+str(EMOS/'tests/sdserve_host'),*extra,'-c',str(source),'-o',str(obj)],check=True)
   for name in ('finite_job_test','runtime_channel_test'):
    exe=work/name
    extra=[] if name=='finite_job_test' else [str(ROOT/'vdp/video/extender/storage/webdav'/s) for s in ('adapter.cpp','wire_backend.cpp','connection.cpp')]
    subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-g','-fsanitize=address,undefined','-pthread',
     '-I'+str(ROOT/'vdp/video'),str(ROOT/'tests/storage/webdav'/(name+'.cpp')),*extra,*objects,'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True,timeout=30)
