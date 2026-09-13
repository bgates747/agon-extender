#!/usr/bin/env python3
"""Temporary USB-ROM input ownership for HW-002 pinwalking; never flash.

Do not start the Agon walk until inputs-ready.json exists and passes. Keep this
one serial connection open. An explicit resume marker is required after the
capture/quiet tail before restarting the installed P4 application.
"""
import argparse,json,os,subprocess,time
from pathlib import Path
from esptool.targets.esp32p4 import ESP32P4ROM
p=argparse.ArgumentParser();p.add_argument('--port',required=True);p.add_argument('--serial',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
port=Path(a.port);resolved=port.resolve(strict=True)
props=dict(x.split('=',1) for x in subprocess.check_output(['udevadm','info','--query=property','--name',str(resolved)],text=True).splitlines() if '=' in x)
normalize=lambda s:s.replace(':','').lower()
assert normalize(props['ID_SERIAL_SHORT'])==normalize(a.serial)
assert os.access(port,os.R_OK|os.W_OK)
esp=ESP32P4ROM(str(port));esp.connect(mode='usb_reset',attempts=1)
chip=esp.get_chip_description();assert 'ESP32-P4' in chip and 'v1.3' in chip,chip
# IDF5.5.5 ESP32-P4 hw_ver1: GPIO at HPPERIPH1+0x20000, IO_MUX+0x21000.
gpio=0x500e0000;iomux=0x500e1000
pins=[22,12,23,11,32,10,33,9] # physical PC0..PC7 order, NOT analyzer channels
low=sum(1<<n for n in pins if n<32);high=sum(1<<(n-32) for n in pins if n>=32)
esp.write_reg(gpio+0x28,low);esp.write_reg(gpio+0x34,high) # output-enable W1TC
for n in pins:
 esp.write_reg(gpio+0x558+4*n,0x500) # GPIO256, output-enable from disabled GPIO_ENABLE
 esp.write_reg(iomux+4+4*n,0x1200,0x7200) # GPIO function1, input enabled

def verify():
 assert esp.read_reg(gpio+0x20)&low==0 and esp.read_reg(gpio+0x2c)&high==0
 result=[]
 for n in pins:
  matrix=esp.read_reg(gpio+0x558+4*n);mux=esp.read_reg(iomux+4+4*n)
  assert matrix&0xfff==0x500 and mux&0x7200==0x1200,(n,matrix,mux)
  result.append(dict(gpio=n,matrix=matrix,mux=mux,output_enabled=False,input_enabled=True))
 return dict(chip=chip,inputs=result,flash_changed=False,application_running=False)
(a.output/'inputs-ready.json').write_text(json.dumps(verify(),indent=2)+'\n')
print('All eight P4 endpoints verified as inputs; ROM held. No flash change.',flush=True)
while not (a.output/'resume-installed-app').exists():time.sleep(.5)
(a.output/'inputs-before-resume.json').write_text(json.dumps(verify(),indent=2)+'\n')
esp.hard_reset();esp._port.close()
(a.output/'resumed.json').write_text(json.dumps(dict(explicit_resume=True,flash_changed=False))+'\n')
print('Explicitly resumed installed P4 application.',flush=True)
