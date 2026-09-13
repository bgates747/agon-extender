"""Compile maintained owner bytes with deterministic driver seams, no emulator."""
from pathlib import Path
import tempfile,shutil,subprocess,sys
TASK=Path(__file__).resolve().parents[1];ROOT=TASK.parents[3];src=ROOT/'vdp/video/extender'
with tempfile.TemporaryDirectory() as d:
 p=Path(d)
 for n in ('transport','input','diagnostics'):
  shutil.copytree(src/n,p/n)
 (p/'input/p4_usb_host.hpp').write_text('// USB boundary supplied by the harness.\n')
 shutil.copy2(TASK/'tests/stubs/Stream.h',p/'Stream.h')
 shutil.copytree(TASK/'tests/stubs/driver',p/'driver')
 for n in ('driver/gpio.h','hal/uart_ll.h','esp_random.h'):
  f=p/n;f.parent.mkdir(exist_ok=True);f.write_text('// Boundary declared in harness.\n')
 binary=p/'owner-test'
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+d,str(TASK/'tests/owner.cpp'),'-o',str(binary)],check=True)
 for scenario in range(3):subprocess.run([str(binary),str(scenario),sys.argv[1]],check=True)
