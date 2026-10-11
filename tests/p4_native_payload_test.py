"""Actual native adapter + handover + egress; only IDF boundaries are modeled."""
from pathlib import Path
from datetime import datetime, timezone
from time import monotonic
import subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class NativePayloadTests(unittest.TestCase):
 def test_exext_psram_payload(self):
  """Actual ExExt leaf: cached payload placement, EOF/pad fence and failure retention."""
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp)
   for header in ('driver/parlio_rx.h','driver/parlio_tx.h','driver/gpio.h',
                  'driver/gpio_filter.h','esp_attr.h','esp_heap_caps.h','freertos/FreeRTOS.h'):
    p=d/header;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('#include "p4_native_sdk_fake.hpp"\n')
   prefix=(ROOT/'tests/p4_native_payload_test.cpp').read_text().split('int main(){')[0]
   source=d/'exext.cpp';source.write_text(prefix+'''
int main(){unsigned cases=0;
 for(bool tx:{false,true})for(unsigned n:{1,255,256,257,3456,4095,4096}){
  reset();auto h=admitted(n,tx);P p(pins,14,16,15,0);
  std::vector<std::uint8_t>b(n+2,0xa5);
  for(unsigned i=0;i<n;++i)if(tx)b[i+1]=std::uint8_t(i*73+17);
  assert(p.arm(h,true,tx,b.data()+1,n,n,0,100)==R::pending);
  assert(!counterRunning&&ready==0);
  if(tx)assert(std::memcmp(dma,b.data()+1,n)==0);
  else for(unsigned i=0;i<n;++i)dma[i]=std::uint8_t(i*73+17);
  signal(false);clockEdges(n);completed(tx,n);
  assert(p.poll(1)==R::pending&&allocation); // completion alone cannot release
  signal(true);assert(p.poll(2)==R::complete&&!allocation&&!outputs);
  assert(b.front()==0xa5&&b.back()==0xa5);
  for(unsigned i=0;i<n;++i)assert(b[i+1]==std::uint8_t(i*73+17));
  ++cases;
 }
 for(bool tx:{false,true})for(int f=0;f<32;++f){
  reset();auto h=admitted(4096,tx);P p(pins,14,16,15,0);
  std::vector<std::uint8_t>b(4096,0xa5);fail=f;
  (void)p.arm(h,true,tx,b.data(),b.size(),b.size(),0,100);
  fail=-1;(void)p.cancel();assert(!allocation&&!outputs&&!enabled);
  ++cases;
 }
 reset();std::cout<<"PASS "<<cases<<" ExExt PSRAM payload/retention cases\\n";
}
''')
   exe=d/'exext'
   subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic',
    '-DAGON_EXTENDER_EXEXT_STREAM','-fsanitize=address,undefined','-fno-sanitize-recover=all',
    f'-I{d}',f'-I{ROOT/"tests"}',f'-I{ROOT/"vdp/video"}',str(source),
    *[str(ROOT/'vdp/video/extender/transport'/(s+'.cpp')) for s in
      ('p4_native_payload','p4_parallel_handover','p4_parallel_egress')],
    '-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=20)
 def test_native_payload(self):
  start=datetime.now(timezone.utc).isoformat();clock=monotonic()
  try:
   with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    for header in ('driver/pulse_cnt.h','driver/parlio_rx.h','driver/parlio_tx.h','driver/gpio.h','driver/gpio_filter.h',
                   'esp_attr.h','esp_heap_caps.h','freertos/FreeRTOS.h'):
     p=d/header;p.parent.mkdir(parents=True,exist_ok=True)
     p.write_text('#include "p4_native_sdk_fake.hpp"\n')
    sources=['tests/p4_native_payload_test.cpp']+[
     'vdp/video/extender/transport/'+name+'.cpp' for name in
     ('p4_native_payload','p4_parallel_handover','p4_parallel_egress')]
    exe=d/'native'
    subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic',
     '-fsanitize=address,undefined','-fno-sanitize-recover=all',
     f'-I{d}',f'-I{ROOT/"tests"}',f'-I{ROOT/"vdp/video"}',
     *[str(ROOT/s) for s in sources],'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True,timeout=20)
  finally:
   print(f'Native payload suite: start={start}, end={datetime.now(timezone.utc).isoformat()}, '
         f'elapsed={monotonic()-clock:.6f} s; host correctness, not GPIO timing')
if __name__=='__main__':unittest.main()
