"""Execute the actual Stream/queue and nested control-dispatch gate."""
from pathlib import Path
import resource,subprocess,tempfile,unittest
from p4_transport_reset_test import SDK,STREAM,method
ROOT=Path(__file__).resolve().parents[1]
HEADER=ROOT/'vdp/video/extender/transport/console_stream.hpp'
HARDWARE=ROOT/'vdp/video/extender/transport/console_hardware.inc'
class AdmissionTests(unittest.TestCase):
 def test_actual_stream_and_previous_empty_only_regression(self):
  resource.setrlimit(resource.RLIMIT_CORE,(0,0))
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);(d/'Stream.h').write_text(STREAM)
   (d/'sdk.hpp').write_text(SDK+'\nunsigned millis();void vTaskDelay(unsigned);\n')
   (d/'driver').mkdir();(d/'driver/uart.h').write_text('#include "sdk.hpp"\n')
   header=HEADER.read_text()
   for old in (False,True,"available"):
    selected=header.replace('if(!progressRemaining || !parallelVdu.available() ||','if(!parallelVdu.available() ||') if old is True else header
    if old=="available":
     start=selected.index('  int available() override {')
     before=selected[:start];after=selected[start:]
     after=after.replace('    if(parallelVdu.active() && !parallelReadReady())return 0;','',1)
     selected=before+after
    if old:self.assertNotEqual(selected,header)
    # Replace only the outer header; its queue/session/handover includes stay real.
    include=d/'extender/transport';include.mkdir(parents=True,exist_ok=True);(include/'console_stream.hpp').write_text(selected)
    source=(ROOT/'tests/console_buffered_admission_test.cpp').read_text()
    src=d/'test.cpp';src.write_text(source);exe=d/'test'
    subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-DAGON_EXTENDER_EXEXT_STREAM','-fsanitize=address,undefined','-fno-sanitize-recover=all',f'-I{d}',f'-I{HEADER.parent}',f'-I{ROOT/"vdp/video"}',str(src),str(HEADER.parent/'p4_parallel_handover.cpp'),'-o',str(exe)],check=True)
    result=subprocess.run([str(exe)],capture_output=True,timeout=10)
    if old:self.assertNotEqual(result.returncode,0);self.assertIn(b'b>=0' if old=='available' else b'consumed<=17+s.progressQuantum',result.stderr)
    else:self.assertEqual(result.returncode,0,result.stderr.decode());print(result.stdout.decode().strip())
 def test_nested_dispatch_defers_console_but_keeps_controller(self):
  gate=method(HARDWARE,'auto dispatchControl=[&]()')
  source='''#include <cassert>
#include <cstdint>
unsigned calls;bool consoleControl(void*,uint8_t*){++calls;return true;}
bool dispatch(bool parseCommands,unsigned version){uint8_t incoming[19]{};incoming[5]=version;void *processor=nullptr;
'''+gate+''';return dispatchControl();}
int main(){for(unsigned version:{1u,2u,3u,4u,255u}){calls=0;assert(dispatch(false,version)==(version!=1));assert(calls==(version!=1));calls=0;assert(dispatch(true,version)&&calls==1);}}
'''
  source='#include <initializer_list>\n'+source
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'gate.cpp';p.write_text(source);exe=p.with_suffix('');subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
  recognition=HARDWARE.read_text().split('auto dispatchControl=[&]()',1)[1].split('if(!parseCommands)return;',1)[0]
  self.assertEqual(recognition.count('dispatchControl()'),2)
if __name__=='__main__':unittest.main()
