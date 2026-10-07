#!/usr/bin/env python3
"""One ordinary reset pulse using the accepted Pi transistor circuit.

JSON configuration (kept outside Git): chip, gpio, and ssh argv for remote use.
Use --local on the Pi host; the GPIO mapping remains explicit and private.
The caller initiates the operation. No automatic retry or Extender reset.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.request import urlopen


def status(url):
    with urlopen(url.rstrip('/') + '/keyboard/status', timeout=5) as response:
        return json.load(response)


def wait_boot(url, old_boot, timeout):
    deadline = time.monotonic() + timeout
    last = 'no response'
    while time.monotonic() < deadline:
        try:
            last = status(url)
            if (last.get('boot') != old_boot and last.get('ready') and
                    last.get('physical_neutral') and not last.get('pending') and
                    not last.get('held')):
                return last
        except Exception as error:
            last = repr(error)
        time.sleep(0.2)
    raise TimeoutError(f'Agon boot/connectivity verification deadline exceeded: {last}')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--local',action='store_true')
    p.add_argument('--verify-url', help='P4 HTTP base URL used to verify a fresh EMOS boot and Extender input')
    p.add_argument('--verify-timeout', type=float, default=60)
    a=p.parse_args();c=json.loads(a.config.read_text());gpio=int(c['gpio']);chip=c['chip']
    if not 0<=gpio<=53 or not re.fullmatch('gpiochip[0-9]+',chip):raise ValueError('Invalid GPIO selection')
    if not a.local and (not isinstance(c.get('ssh'),list) or not c['ssh'] or c['ssh'][0]!='ssh'):raise ValueError('Expected SSH argv')
    before = status(a.verify_url) if a.verify_url else None
    script=f'''set -euo pipefail
trap 'pinctrl set {gpio} ip pd' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP
timeout --kill-after=1s 2s gpioset -c {chip} -C agon-reset -b pull-down -t 100ms,0 {gpio}=1
pinctrl set {gpio} ip pd
echo '100 ms reset pulse sent and GPIO released.'
'''
    subprocess.run((['sudo','-n','bash','-s'] if a.local else c['ssh']+['sudo -n bash -s']),input=script,text=True,check=True,timeout=15)
    if not a.verify_url:
        print('PULSE-ONLY COMPLETE — the caller owns subsequent boot/application verification.')
        return
    print('Attempting to verify a fresh EMOS boot and working Extender keyboard input.', flush=True)
    after = wait_boot(a.verify_url, before['boot'], a.verify_timeout)
    print(f"AGON RESET VERIFIED — fresh boot {after['boot']} has working Extender input.")

if __name__=='__main__':main()
