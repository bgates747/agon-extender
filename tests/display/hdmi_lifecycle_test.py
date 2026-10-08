#!/usr/bin/env python3
"""Compile the real HDMI sink with controlled SDK/renderer substitutes.

No hardware or emulator is used. Physical DMA timing and SDK internals are
outside this model; existing strip/service tests cover their own boundaries.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'vdp/video/extender/display/hdmi_output.cpp'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--old-control', action='store_true')
    parser.add_argument('--ppa-scale-320', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    utc = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = dict(start_utc=utc(), scope='host lifecycle, no physical timing claim',
                  source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
                  old_control=args.old_control, passed=False)
    result['test_inputs'] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in (Path(__file__), HERE/'hdmi_lifecycle_test.cpp',
                                         HERE/'hdmi_lifecycle_host.hpp',
                                         SOURCE.with_suffix('.hpp'))}
    start = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix='hdmi-lifecycle-') as name:
            temp = Path(name)
            # These are the only substituted API surfaces. HdmiOutput and its
            # geometry/ownership/storage/rolling headers compile unchanged.
            for header in ('esp_heap_caps.h', 'esp_lcd_panel_ops.h',
                           'esp_lcd_mipi_dsi.h', 'esp_lcd_panel_io.h',
                           'esp_ldo_regulator.h', 'esp_lcd_lt8912b.h',
                           'esp_log.h', 'esp_timer.h', 'driver/i2c_master.h',
                           'freertos/FreeRTOS.h', 'freertos/task.h',
                           'freertos/idf_additions.h',
                           'extender/display/stock_runtime_controller.hpp',
                           'extender/display/presentation_snapshot_pool.hpp'):
                path = temp / header
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('#include "hdmi_lifecycle_host.hpp"\n')
            binary = temp / 'check'
            subprocess.run([
                'g++', '-std=c++17', '-O1', '-g', '-pthread',
                '-Wall', '-Wextra', '-Wno-unused-variable', '-Wno-unused-parameter',
                '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                '-DAGON_EXTENDER_HDMI', '-DAGON_EXTENDER_HDMI_AUTO',
                '-DAGON_EXTENDER_DIRECT_RGB888', '-DAGON_EXTENDER_ROLLING_SCANOUT',
                *(['-DAGON_EXTENDER_HDMI_PPA_320'] if args.ppa_scale_320 else []),
                '-I'+str(temp), '-I'+str(HERE), '-I'+str(ROOT/'vdp/video'),
                str(args.source), str(HERE/'hdmi_lifecycle_test.cpp'),
                '-o', str(binary)], check=True)
            subprocess.run([str(binary), *(['old'] if args.old_control else [])],
                           check=True, timeout=30)
            result['passed'] = True
    finally:
        result.update(end_utc=utc(), duration_seconds=time.monotonic()-start)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result))


if __name__ == '__main__':
    main()
