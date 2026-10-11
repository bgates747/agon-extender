#!/usr/bin/env python3
"""Bounded DevKit reverse pinwalk, reusing USB-ROM setup and HW-002 capture.

Both boards powered; Pi reset transistor holds Agon GPIO as reset-state inputs.
Never release Agon reset without independently verifying P4 outputs released.
No flash, SD changes, arbitrary GPIO sweep or automatic retry. This isolated
Author-approved diagnostic is not a supported EMOS transport bypass.
Register offsets: retained ESP-IDF5.5.5 ESP32-P4 hw_ver1 gpio_reg.h/io_mux_reg.h.
Host-paced pulses are for attribution, not calibrated speed measurements.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from urllib.request import urlopen
import zipfile

from esptool.targets.esp32p4 import ESP32P4ROM

ROOT = Path(__file__).resolve().parents[4]
GPIO, MUX = 0x500e0000, 0x500e1000
RATE, SAMPLES = 100000, 6000000

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')

def http(url, path):
    with urlopen(url.rstrip('/') + path, timeout=3) as response:
        return json.load(response)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--reset-config', type=Path, required=True)
    p.add_argument('--probe-map', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--run', action='store_true', required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    cfg = json.loads(a.config.read_text())
    reset = json.loads(a.reset_config.read_text())
    line, chip = int(reset['gpio']), reset['chip']
    assert 0 <= line <= 53 and re.fullmatch(r'gpiochip[0-9]+', chip)
    board_path = ROOT / 'vdp/build/boards/p4-devkit.json'
    board = json.loads(board_path.read_text())['transport']
    targets = [(f'data{i}', pin, i+1) for i, pin in enumerate(board['data'])]
    targets += [('READY_N', board['ready'], 9), ('CLOCK', board['clock'], 10),
                ('VALID_N', board['valid'], 11)]
    pins = list(dict.fromkeys([x[1] for x in targets] + board['isolation']))
    assert [x[1] for x in targets] == [22,12,23,11,32,10,33,9,20,14,13]
    assert len(pins) == 14 and not set(pins) & {24,25,26,27}
    probe_map = json.loads(a.probe_map.read_text())['channels']
    sdk = ROOT / 'agents/build001/native-tools/esp-idf/components/soc/esp32p4/register/hw_ver1/soc'
    header = (sdk / 'gpio_reg.h').read_text()
    for name, offset in [('OUT',4),('OUT_W1TS',8),('OUT_W1TC',12),
                         ('OUT1',16),('OUT1_W1TS',20),('OUT1_W1TC',24),
                         ('ENABLE',32),('ENABLE_W1TS',36),('ENABLE_W1TC',40),
                         ('ENABLE1',44),('ENABLE1_W1TS',48),('ENABLE1_W1TC',52),('PIN0',116)]:
        match = re.search(r'^#define GPIO_'+name+r'_REG \(DR_REG_GPIO_BASE \+ (0x[0-9a-f]+)\)', header, re.M)
        assert match and int(match[1],16) == offset, name
    port = str(Path(cfg['port']).resolve(strict=True))
    props = dict(x.split('=',1) for x in subprocess.check_output(
        ['udevadm','info','--query=property','--name',port], text=True).splitlines() if '=' in x)
    assert props['ID_SERIAL_SHORT'] == cfg['serial']
    initial = http(cfg['p4'], '/keyboard/status')
    assert initial['ready'] and initial['physical_neutral'] and not initial['held'] and not initial['pending']
    record = dict(started_utc=datetime.now(timezone.utc).isoformat(), initial_keyboard=initial,
                  targets=targets, observed_probes=probe_map, flash_changed=False, SD_changed=False,
                  tool_sha256=sha(__file__), board_sha256=sha(board_path),
                  gpio_header_sha256=sha(sdk/'gpio_reg.h'), states=[], recovery_complete=False)
    save(a.output/'manifest.local.json', record)
    mask0 = sum(1<<n for n in pins if n<32)
    mask1 = sum(1<<(n-32) for n in pins if n>=32)
    hold = esp = capture = None
    safe = False
    hold_log = capture_log = None

    def verify_inputs():
        assert esp.read_reg(GPIO+0x20)&mask0 == 0
        assert esp.read_reg(GPIO+0x2c)&mask1 == 0
        return {str(n): (esp.read_reg(GPIO+(0x3c if n<32 else 0x40)) >> (n%32)) & 1 for n in pins}

    def release_all():
        esp.write_reg(GPIO+0x28, mask0)
        esp.write_reg(GPIO+0x34, mask1)
        return verify_inputs()

    def reset_held():
        assert hold.poll() is None, 'Agon reset holder exited'
        level = subprocess.check_output(['sudo','-n','pinctrl','lev',str(line)], text=True).strip()
        assert level == '1', 'Pi reset transistor drive not asserted'

    try:
        hold_log = (a.output/'reset-hold.log').open('wb')
        hold = subprocess.Popen(['sudo','-n','gpioset','--banner','-c',chip,'-C','agon-reversewalk',
                                 '-b','pull-down',f'{line}=1'], stdout=hold_log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        record['reset_hold_process_group'] = hold.pid
        save(a.output/'manifest.local.json',record)
        time.sleep(.3)
        reset_held()
        print('Agon reset hold asserted and checked; entering P4 ROM.',flush=True)
        esp = ESP32P4ROM(port)
        esp.connect(mode='usb_reset', attempts=1)
        assert 'ESP32-P4' in esp.get_chip_description() and 'v1.3' in esp.get_chip_description()
        release_all()
        for n in pins:
            esp.write_reg(GPIO+0x558+4*n,0x500)
            # Software GPIO function1/input enabled; internal pulls and sleep off.
            esp.write_reg(MUX+4+4*n,0x1200,0x7382)
            assert esp.read_reg(GPIO+0x558+4*n)&0xfff == 0x500
            assert esp.read_reg(MUX+4+4*n)&0x7382 == 0x1200
        record['inputs_before'] = verify_inputs()
        safe = True
        capture_dir = a.output/'capture'
        capture_dir.mkdir()
        spec = importlib.util.spec_from_file_location('retained_capture',ROOT/'docs/tasks/AUDIT-005/scripts/capture_trace.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        connection = module.discover(capture_dir)
        raw = capture_dir/'logic.raw'
        args = ['sigrok-cli','--loglevel','2','--driver','fx2lafw:conn='+connection,
                '--config',f'samplerate={RATE}','--channels',','.join(f'D{i}' for i in range(8)),
                '--samples',str(SAMPLES),'--output-format','binary','--output-file',str(raw)]
        record['capture_argv'] = args
        capture_log = (capture_dir/'sigrok.log').open('wb')
        capture = subprocess.Popen(args,stdout=capture_log,stderr=subprocess.STDOUT)
        begin = time.monotonic()
        while not raw.exists() or raw.stat().st_size < 65536:
            if capture.poll() is not None or time.monotonic()-begin > 8:
                raise RuntimeError('No delivered samples; no test output enabled')
            time.sleep(.05)
        assert capture.poll() is None
        record['delivered_before_drive'] = raw.stat().st_size
        print('Delivered samples verified; pulsing eleven known P4 GPIOs once.',flush=True)
        for name,n,count in targets:
            reset_held()
            verify_inputs()
            offset, bit = (0,1<<n) if n<32 else (12,1<<(n-32))
            # Preload high, force push-pull only for this pin, then enable it.
            esp.write_reg(GPIO+8+offset,bit)
            esp.write_reg(GPIO+0x74+4*n,0,4)
            safe = False
            esp.write_reg(GPIO+0x24+(0 if n<32 else 12),bit)
            samples=[]
            try:
                for pulse in range(count):
                    esp.write_reg(GPIO+12+offset,bit)
                    time.sleep(.05)
                    low=(esp.read_reg(GPIO+(0x3c if n<32 else 0x40))>>(n%32))&1
                    esp.write_reg(GPIO+8+offset,bit)
                    time.sleep(.05)
                    high=(esp.read_reg(GPIO+(0x3c if n<32 else 0x40))>>(n%32))&1
                    samples.append([low,high])
            finally:
                esp.write_reg(GPIO+0x28+(0 if n<32 else 12),bit)
                verify_inputs()
                safe=True
            row=dict(signal=name,gpio=n,pulses=count,input_low_high=samples,
                     pad_readback_pass=all(x==[0,1] for x in samples),host_s=time.monotonic()-begin)
            record['states'].append(row)
            save(a.output/'manifest.local.json',record)
            print(f'{name}: GPIO{n}, {count} pulses, pad readback={row["pad_readback_pass"]}',flush=True)
            time.sleep(.25)
        record['inputs_after'] = release_all()
        safe=True
        record['outputs_released_host_seconds_after_capture_launch']=time.monotonic()-begin
        save(a.output/'manifest.local.json',record)
        print('All P4 outputs released; finishing the retained 60-second capture.',flush=True)
        record['capture_exit'] = capture.wait(timeout=80)
        record['samples'] = raw.stat().st_size
        assert record['capture_exit']==0 and record['samples']==SAMPLES, 'Incomplete acquisition; no replay'
        metadata=('[global]\nsigrok version=0.5.2\n[device 1]\ncapturefile=logic-1\n'
                  'total probes=8\nsamplerate=100 kHz\ntotal analog=0\nunitsize=1\n'
                  + ''.join(f'probe{i+1}=D{i}\n' for i in range(8)))
        digest=sha(raw)
        with zipfile.ZipFile(capture_dir/'logic.sr','w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('version','2');z.writestr('metadata',metadata);z.write(raw,'logic-1-1')
        with zipfile.ZipFile(capture_dir/'logic.sr') as z:
            assert z.testzip() is None and hashlib.sha256(z.read('logic-1-1')).hexdigest()==digest
        record['sample_sha256']=digest
        record['acquisition_pass']=True
    except BaseException as error:
        record['error']=repr(error)
        raise
    finally:
        if capture is not None and capture.poll() is None:
            capture.terminate();capture.wait(timeout=5)
        if capture_log is not None: capture_log.close()
        if esp is not None:
            try:
                record['inputs_before_normal_restart']=release_all()
                safe=True
                esp.hard_reset();esp._port.close()
                # Normal app initializes while Agon stays reset, then its UART
                # ownership follows the unchanged original startup on release.
                deadline=time.monotonic()+20
                while True:
                    reset_held()
                    try:
                        record['normal_service_before_release']=http(cfg['p4'],'/keyboard/status')
                        break
                    except (OSError,ValueError):
                        if time.monotonic()>deadline: raise RuntimeError('P4 service did not return; Agon remains held')
                        time.sleep(.2)
            except BaseException as recovery_error:
                safe=False
                record['recovery_error']=repr(recovery_error)
        if hold is not None and safe:
            subprocess.run(['sudo','-n','kill','-TERM','--',f'-{hold.pid}'],check=True,timeout=5)
            hold.wait(timeout=5)
            subprocess.run(['sudo','-n','pinctrl','set',str(line),'ip','pd'],check=True,timeout=5)
            record['Agon_reset_released']=True
            deadline=time.monotonic()+65
            while time.monotonic()<deadline:
                try:
                    s=http(cfg['p4'],'/keyboard/status')
                    if s['ready'] and s['physical_neutral'] and not s['held'] and not s['pending']:
                        record['final_keyboard']=s;record['recovery_complete']=True;break
                except (OSError,ValueError):pass
                time.sleep(.2)
        elif hold is not None:
            record['Agon_reset_left_asserted']=hold.poll() is None
            print('Agon remains held in reset; verify P4 release before manual recovery.',flush=True)
        if hold_log is not None:hold_log.close()
        record['ended_utc']=datetime.now(timezone.utc).isoformat()
        save(a.output/'manifest.local.json',record)
        print(json.dumps({k:record[k] for k in ('acquisition_pass','recovery_complete','error','recovery_error','Agon_reset_left_asserted') if k in record}),flush=True)
    if not record['recovery_complete']:
        raise RuntimeError('Recovery incomplete; see retained manifest and reset-hold boundary')

if __name__=='__main__':
    def interrupted(signum,frame):
        raise KeyboardInterrupt(f'Signal {signum}; ordered GPIO release required')
    signal.signal(signal.SIGTERM,interrupted)
    main()
