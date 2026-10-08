#!/usr/bin/env python3
"""Compile the maintained C runtime with a deterministic asynchronous DMA stub."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]
RUNTIME=ROOT/'vdp/video/extender/display/rolling'

def run(args):
    with tempfile.TemporaryDirectory(prefix='rolling-runtime-') as temp:
        d=Path(temp)
        for name in ('esp_async_fbcpy.h','esp_timer.h','esp_heap_caps.h','esp_rom_sys.h'):
            (d/name).write_text('// Host API supplied by rolling_runtime_test.c\n')
        source=d/'test.c';source.write_text(Path(__file__).with_suffix('.c').read_text())
        if args.old_runtime:
            (d/'strip_runtime.inc').write_bytes(args.old_runtime.read_bytes())
        else:
            sdk=ROOT/'agents/build001/native-tools/esp-idf/components/esp_lcd/dsi/esp_lcd_panel_dpi.c'
            derived=d/'derived.c'
            subprocess.run([sys.executable,str(RUNTIME/'patch_dpi.py'),str(sdk),str(derived)],check=True)
            # Exercise the generated, maintained full-frame callback verbatim.
            callback=re.search(r'bool mipi_dsi_dma_trans_done_cb\(.*?(?=\nvoid mipi_dsi_bridge_isr_handler)',derived.read_text(),re.S)
            assert callback
            (d/'frame_callback.inc').write_text(callback.group())
        binary=d/'check'
        subprocess.run(['gcc','-std=gnu11','-O1','-g','-Wall','-Wextra',
                        '-Wno-unused-function','-Wno-unused-parameter',
                        '-fsanitize=address,undefined','-fno-omit-frame-pointer',
                        '-DAGON_EXTENDER_HDMI_AUTO',
                        *(['-DEXPECT_OLD_ABORT'] if args.old_runtime else []),
                        '-I'+str(d),'-I'+str(RUNTIME),str(source),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True,timeout=60)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--old-runtime',type=Path,help='Retained pre-fix file; require the reproduced early abort')
    p.add_argument('--report',type=Path,help='Durable host-only result and wall-clock duration')
    args=p.parse_args()
    utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
    runtime=args.old_runtime or RUNTIME/'strip_runtime.inc'
    record={'start_utc':utc(),'scope':'host simulation, no physical timing claim',
            'runtime_sha256':hashlib.sha256(runtime.read_bytes()).hexdigest(),
            'test_sha256':hashlib.sha256(Path(__file__).with_suffix('.c').read_bytes()).hexdigest(),
            'old_abort_control':bool(args.old_runtime),'passed':False}
    start=time.monotonic()
    try:
        run(args);record['passed']=True
    finally:
        record.update(end_utc=utc(),duration_seconds=time.monotonic()-start)
        if args.report:
            args.report.parent.mkdir(parents=True,exist_ok=True)
            args.report.write_text(json.dumps(record,indent=2)+'\n')
        print(json.dumps(record))

if __name__=='__main__':main()
