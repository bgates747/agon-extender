#!/usr/bin/env python3
"""One ordinary reset pulse using the accepted Pi transistor circuit.

JSON configuration (kept outside Git): ssh = complete SSH argv, chip, gpio.
The caller initiates the operation. No automatic retry or Extender reset.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());gpio=int(c['gpio']);chip=c['chip']
    if not 0<=gpio<=53 or not re.fullmatch('gpiochip[0-9]+',chip):raise ValueError('Invalid GPIO selection')
    if not isinstance(c['ssh'],list) or not c['ssh'] or c['ssh'][0]!='ssh':raise ValueError('Expected SSH argv')
    script=f'''set -euo pipefail
trap 'pinctrl set {gpio} ip pd' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP
timeout --kill-after=1s 2s gpioset -c {chip} -C agon-reset -b pull-down -t 100ms,0 {gpio}=1
pinctrl set {gpio} ip pd
echo '100 ms reset pulse sent and GPIO released. Boot success requires separate observation.'
'''
    subprocess.run(c['ssh']+['sudo -n bash -s'],input=script,text=True,check=True,timeout=15)

if __name__=='__main__':main()
