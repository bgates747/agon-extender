"""Actual boot pad leaves and handover cores; fake only register/SDK boundaries."""
from pathlib import Path
import os, subprocess, tempfile, unittest
from datetime import datetime, timezone
from functools import wraps
from time import monotonic
ROOT=Path(__file__).resolve().parents[1]
EMOS=Path(os.environ.get('AGON_EMOS_ROOT',ROOT.parent/'agon-emos'))
def timed(fn):
 @wraps(fn)
 def run(self):
  start=datetime.now(timezone.utc).isoformat();clock=monotonic()
  try:return fn(self)
  finally:
   print(f'Boot adapter suite: start={start}, end={datetime.now(timezone.utc).isoformat()}, '
         f'elapsed={monotonic()-clock:.6f} s (host compile/test, not GPIO performance)')
 return run
class BootTests(unittest.TestCase):
 @timed
 def test_paired_adapters(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);flags=['-Wall','-Wextra','-Werror','-pedantic','-Wno-endif-labels',
    '-ffunction-sections','-fsanitize=address,undefined','-fno-sanitize-recover=all']
   for header in ('driver/uart.h','driver/gpio.h','freertos/FreeRTOS.h',
                  'esp_rom_gpio.h','soc/uart_periph.h'):
    p=d/header;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('#include "p4_uart_sdk_fake.hpp"\n')
   inc=[f'-I{d}',f'-I{ROOT/"tests"}',f'-I{EMOS/"tests/host"}',
        f'-I{EMOS/"src"}',f'-I{ROOT/"vdp/video"}']
   objects=[]
   for source in ['emos_parallel_boot','emos_parallel_handover']:
    obj=d/(source+'.o');objects.append(str(obj))
    subprocess.run(['cc','-std=c17',*flags,*inc,'-include','eZ80.h','-c',str(EMOS/'src'/(source+'.c')),
                    '-o',str(obj)],check=True)
   exe=d/'boot'
   subprocess.run(['c++','-std=c++17',*flags,*inc,*objects,
    str(ROOT/'tests/parallel_boot_release_test.cpp'),
    str(ROOT/'vdp/video/extender/transport/p4_boot_release.cpp'),
    str(ROOT/'vdp/video/extender/transport/p4_parallel_handover.cpp'),
    '-Wl,--gc-sections','-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=20)
if __name__=='__main__':unittest.main()
