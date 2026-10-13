#!/usr/bin/env python3
"""Actual-controller host snapshots with the PIE selector absent, =0 and =1.

Host checks qualify row/source bounds and selection, never P4 speed or ISA.
Use scroll_copy_test.py for the independently bounded vector-read model.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
GL=ROOT/'vdp/vendor/vdp-gl/src'
RUNTIME=ROOT/'docs/tasks/PORT-003/stock-backend-r2/runtime'
ROW=ROOT/'docs/tasks/PORT-003/stock-backend-r1'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scroll-fast',action='store_true')
    args=parser.parse_args()
    sources=[GL/'dispdrivers'/(name+'controller.cpp') for name in
             ('vgabase','vgapaletted','vga2','vga4','vga8','vga16','vga64')]
    sources += [GL/(name+'.cpp') for name in ('canvas','displaycontroller','codepages','fabfonts')]
    sources += [ROOT/'vdp/video/extender/port/stock_render_utils.cpp']
    sources += [ROOT/'vdp/video/extender/display'/(name+'.cpp') for name in
                ('stock_native_access','stock_scanline','stock_runtime_controller',
                 'p4_rgb888_controller','presentation_snapshot_pool')]
    sources += [Path(__file__).with_suffix('.cpp')]
    includes=[HERE/'compat',RUNTIME/'compat',ROW/'compat',
              ROOT/'docs/tasks/PORT-003/phase-c/tests/compat',
              ROOT/'docs/tasks/PORT-003/phase-b/tests/compat',GL,ROOT/'vdp/video']
    flags=['-std=c++17','-O1','-g','-pthread','-ffunction-sections','-fdata-sections','-Wl,--gc-sections',
           '-fsanitize=address,undefined','-fno-omit-frame-pointer',
           '-DFABGL_EMULATED','-DAGON_EXTENDER_STOCK_RUNTIME','-DAGON_EXTENDER_DIRECT_RGB888',
           '-DAGON_EXTENDER_INDEXED_PPA=1','-DAGON_EXTENDER_INDEXED_FRAME_SNAPSHOT=1',
           '-DAGON_EXTENDER_SW_VISIBLE_SNAPSHOT=1',
           *(['-DAGON_EXTENDER_SCROLL_FAST=1'] if args.scroll_fast else []),
           *['-I'+str(path) for path in includes],'-include',str(RUNTIME/'compat/host_preinclude.hpp')]
    with tempfile.TemporaryDirectory(prefix='indexed-snapshot-copy-') as temporary:
        work=Path(temporary)
        for selector in (None,0,1):
            chosen=flags+([] if selector is None else ['-DAGON_EXTENDER_INDEXED_SNAPSHOT_PIE='+str(selector)])
            binary=work/('check-'+str(selector))
            subprocess.run(['g++',*chosen,*map(str,sources),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True,timeout=30)
            # The default/explicit-zero object must contain no candidate call
            # or entry point. Enabled host object uses libc, not fake PIE.
            symbols=subprocess.check_output(['nm','-C',str(binary)],text=True)
            assert ('P4Color64Controller::copyLinearSnapshotRowPie' in symbols)==(selector==1)
    print('PASS: actual-controller ASAN/UBSAN absent/=0/=1; default/zero candidate API absent')


if __name__=='__main__':main()
