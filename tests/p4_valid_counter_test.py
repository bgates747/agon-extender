"""Pinned-IDF PCNT edge proof model: overflow, freeze race, and failure ownership."""
from pathlib import Path
from datetime import datetime, timezone
from time import monotonic
import subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class ValidCounterTests(unittest.TestCase):
 def test_valid_counter(self):
  start=datetime.now(timezone.utc).isoformat();clock=monotonic()
  try:
   with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    for header in ('driver/pulse_cnt.h','driver/gpio.h','freertos/FreeRTOS.h'):
     p=d/header;p.parent.mkdir(parents=True,exist_ok=True)
     p.write_text('#include "p4_native_sdk_fake.hpp"\n')
    exe=d/'counter'
    subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic',
     '-fsanitize=address,undefined','-fno-sanitize-recover=all',
     f'-I{d}',f'-I{ROOT/"tests"}',f'-I{ROOT/"vdp/video"}',
     str(ROOT/'tests/p4_valid_counter_test.cpp'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True,timeout=20)
  finally:
   print(f'PCNT VALID suite: start={start}, end={datetime.now(timezone.utc).isoformat()}, '
         f'elapsed={monotonic()-clock:.6f} s; host correctness, not GPIO timing')
if __name__=='__main__':unittest.main()
