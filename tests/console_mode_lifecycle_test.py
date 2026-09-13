"""Exercise real ExCom control + retained vdu_mode at the lifecycle boundary.

The established mode harness supplies controlled display/context seams. This
checks ordering and protocol effects, not native pixels or physical P4 health.
The negative control restores N002's raw changeMode call and must be rejected.
"""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'docs/tasks/PORT-003/phase-e/scripts/run-official-mode-lifecycle.py'
spec = importlib.util.spec_from_file_location('mode_lifecycle', RUNNER)
lifecycle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lifecycle)

HARNESS = r'''
#include <algorithm>
#include "extender/transport/console_session.hpp"
using namespace agon::extender::transport;
uint32_t millis() { return 100; }
uint32_t esp_random() { return 1234; }
struct ControlOutput {
  ConsoleSession session;
  std::vector<uint8_t> bytes;
  void write(uint8_t b) { bytes.push_back(b); events.emplace_back("control.byte"); }
  void write(const uint8_t *p, size_t n) { for(size_t i=0;i<n;++i)write(p[i]); }
} stream;
ControlOutput *console_stream = &stream;

@CONTROL@

int main() {
  Context context; context.charWidth=80; context.charHeight=60;
  VDUStreamProcessor processor(&context);
  finalMode=0; finalWidth=640; finalHeight=480; finalDepth=16;
  uint8_t request[CONSOLE_SIZE] = {'E','X',1,CONSOLE_PREPARE,1};
  request[12]=1; console_seal(request);
  for(unsigned cycle=0;cycle<2;++cycle) {
    events.clear(); stream.bytes.clear(); scriptedAttempts={{0,0}}; attemptIndex=0;
    request[3]=CONSOLE_PREPARE; request[4]=cycle+1;
    std::fill_n(request+8,4,0); console_seal(request);
    consoleControl(&processor,request);
    const auto reset=std::find(events.begin(),events.end(),"contexts.reset-all");
    const auto reply=std::find(events.begin(),events.end(),"control.byte");
    const auto mode=std::find(events.begin(),events.end(),"packet.send-mode");
    if(reset==events.end() || mode==events.end() || !(reset<mode && mode<reply)) {
      std::cerr << "prepare acknowledged without complete retained mode lifecycle\n";
      return 40;
    }
    if(attemptIndex!=1 || stream.bytes.size()!=CONSOLE_SIZE+2 ||
       stream.bytes[0]!=CONSOLE_REPLY || stream.bytes[1]!=CONSOLE_SIZE ||
       stream.session.active() || !console_valid(stream.bytes.data()+2)) return 41;
    std::copy_n(stream.bytes.data()+10,4,request+8);
    request[3]=CONSOLE_COMMIT; console_seal(request);
    events.clear(); consoleControl(&processor,request);
    if(!stream.session.active() || attemptIndex!=1 ||
       std::find(events.begin(),events.end(),"contexts.reset-all")!=events.end()) return 42;
    request[3]=CONSOLE_LEAVE; console_seal(request); consoleControl(&processor,request);
    if(stream.session.active()) return 43;
  }
  // A retaining preparation must ACK without changing mode/context/scene.
  request[3]=CONSOLE_PREPARE_KEEP; request[4]=3;
  std::fill_n(request+8,4,0); console_seal(request);
  events.clear(); stream.bytes.clear(); consoleControl(&processor,request);
  if(stream.bytes.size()!=CONSOLE_SIZE+2 ||
     stream.bytes[5]!=(CONSOLE_PREPARE_KEEP|0x80) || attemptIndex!=1 ||
     std::find(events.begin(),events.end(),"contexts.reset-all")!=events.end()) return 45;
  auto count=stream.bytes.size();
  request[3]=CONSOLE_PREPARE; // wrong CRC: no mode change or ACK
  consoleControl(&processor,request);
  if(attemptIndex!=1 || stream.bytes.size()!=count) return 44;
}
'''


class ConsoleModeLifecycleTests(unittest.TestCase):
    def test_prepare_initializes_context_before_ack_and_repeat(self):
        source, _ = lifecycle.harness_source(ROOT / 'vdp')
        source = source[:source.index('int main(')]
        # R2 selected the active depth controller through this accessor. The
        # inherited standalone harness still owns one controlled fake display.
        marker='std::unique_ptr<FakeController> _VGAController(new FakeController());'
        source=source.replace(marker,marker+'\nFakeController *activeDisplayController() { return _VGAController.get(); }')
        control, *_ = lifecycle.extract_function_text(
            ROOT / 'vdp/video/extender/transport/console_hardware.inc', 'consoleControl')
        with tempfile.TemporaryDirectory() as tmp:
            for label, body, expected in (
                ('current', control, 0),
                ('n002', control.replace('processor->vdu_mode(0)', 'changeMode(0)'), 40),
            ):
                cpp, binary = Path(tmp)/(label+'.cpp'), Path(tmp)/label
                cpp.write_text(source+HARNESS.replace('@CONTROL@',body))
                subprocess.run(['c++','-std=c++17','-Wall','-Wextra',
                                '-fsanitize=address,undefined','-fno-sanitize-recover=all',
                                '-I'+str(ROOT/'vdp/video'),str(cpp),'-o',str(binary)],
                               check=True, capture_output=True, text=True)
                result = subprocess.run([str(binary)],capture_output=True,text=True)
                self.assertEqual(result.returncode, expected, result.stdout+result.stderr)


if __name__ == '__main__':
    unittest.main()
