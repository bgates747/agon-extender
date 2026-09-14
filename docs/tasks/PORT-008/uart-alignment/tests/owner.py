"""Compile maintained owner bytes with deterministic driver seams, no emulator."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,argparse
TASK=Path(__file__).resolve().parents[1];ROOT=TASK.parents[3];src=ROOT/'vdp/video/extender'
parser=argparse.ArgumentParser()
parser.add_argument('refill',type=int,choices=[0,1]);parser.add_argument('serial_reply',type=int,choices=[0,1],nargs='?',default=0)
parser.add_argument('--control',choices=['no-refill','no-serial-reply'])
args=parser.parse_args()

with tempfile.TemporaryDirectory() as d:
 p=Path(d)
 for n in ('transport','input','diagnostics'):
  shutil.copytree(src/n,p/n)
 if args.control:
  owner=p/'transport/console_hardware.inc';text=owner.read_text()
  old,new=('if(s.count) {','if(s.count && !transmitting) {') if args.control=='no-refill' else ('if(!s.count) {','if(true) {')
  assert text.count(old)==1,'Control seam changed; review before substituting'
  owner.write_text(text.replace(old,new))
 (p/'input/p4_usb_host.hpp').write_text('// USB boundary supplied by the harness.\n')
 shutil.copy2(TASK/'tests/stubs/Stream.h',p/'Stream.h')
 shutil.copytree(TASK/'tests/stubs/driver',p/'driver')
 for n in ('driver/gpio.h','hal/uart_ll.h','esp_random.h'):
  f=p/n;f.parent.mkdir(exist_ok=True);f.write_text('// Boundary declared in harness.\n')
 binary=p/'owner-test'
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+d,str(TASK/'tests/owner.cpp'),'-o',str(binary)],check=True)
 for scenario in range(4):subprocess.run([str(binary),str(scenario),str(args.refill),str(args.serial_reply)],check=True)
