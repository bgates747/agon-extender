"""Real linked application helper with portable P4 card service, no hardware."""
from pathlib import Path
import subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
EMOS=ROOT.parent/'agon-emos'
class ApplicationCardTests(unittest.TestCase):
 def test_paired_card_engine(self):
  with tempfile.TemporaryDirectory() as d:
   work=Path(d);objects=[]
   for source,name in [(EMOS/'lib/sdapp/sdapp.c','app'),(EMOS/'projects/sdserve/src/service.c','engine'),(EMOS/'tests/sdserve_host/fs.c','fs')]:
    obj=work/(name+'.o');objects.append(str(obj))
    extra=['-Dservice_progress=fs_progress_callback'] if name=='fs' else []
    subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-g','-fsanitize=address,undefined','-I'+str(EMOS/'tests/sdserve_host'),'-I'+str(EMOS/'projects/sdserve/src'),*extra,'-c',str(source),'-o',str(obj)],check=True)
   exe=work/'test'
   subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-g','-fsanitize=address,undefined','-I'+str(ROOT/'vdp/video'),'-I'+str(EMOS/'lib/sdapp'),str(ROOT/'tests/storage/webdav/application_card_test.cpp'),*objects,'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=30)
