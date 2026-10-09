"""Actual native adapter + handover + egress; only IDF boundaries are modeled."""
from pathlib import Path
from datetime import datetime, timezone
from time import monotonic
import subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class NativePayloadTests(unittest.TestCase):
 def test_native_payload(self):
  start=datetime.now(timezone.utc).isoformat();clock=monotonic()
  try:
   with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    for header in ('driver/parlio_rx.h','driver/parlio_tx.h','driver/gpio.h',
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
