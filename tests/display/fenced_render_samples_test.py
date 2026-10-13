#!/usr/bin/env python3
"""Actual-controller ordered fence samples; host checks are not target timing."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
GL=ROOT/'vdp/vendor/vdp-gl/src'
RUNTIME=ROOT/'docs/tasks/PORT-003/stock-backend-r2/runtime'
ROW=ROOT/'docs/tasks/PORT-003/stock-backend-r1'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--sanitize',action='store_true')
    args=parser.parse_args()
    sources=[GL/'dispdrivers'/(n+'controller.cpp') for n in ('vgabase','vgapaletted','vga2','vga4','vga8','vga16','vga64')]
    sources += [GL/(n+'.cpp') for n in ('canvas','displaycontroller','codepages','fabfonts')]
    sources += [ROOT/'vdp/video/extender/port/stock_render_utils.cpp']
    sources += [ROOT/'vdp/video/extender/display'/(n+'.cpp') for n in ('stock_native_access','stock_scanline','stock_runtime_controller','p4_rgb888_controller','presentation_snapshot_pool')]
    sources += [Path(__file__).with_suffix('.cpp')]
    includes=[HERE/'compat',RUNTIME/'compat',ROW/'compat',ROOT/'docs/tasks/PORT-003/phase-c/tests/compat',ROOT/'docs/tasks/PORT-003/phase-b/tests/compat',GL,ROOT/'vdp/video']
    with tempfile.TemporaryDirectory(prefix='fenced-render-samples-') as tmp:
        binary=Path(tmp)/'check'
        subprocess.run(['g++','-std=c++17','-O1','-g','-pthread','-ffunction-sections','-fdata-sections','-Wl,--gc-sections',
                        *(['-fsanitize=address,undefined','-fno-omit-frame-pointer'] if args.sanitize else []),
                        '-DFABGL_EMULATED','-DAGON_EXTENDER_STOCK_RUNTIME','-DAGON_EXTENDER_DIRECT_RGB888','-DAGON_EXTENDER_RENDER_BENCHMARK=1',
                        *['-I'+str(p) for p in includes],'-include',str(RUNTIME/'compat/host_preinclude.hpp'),*map(str,sources),'-o',str(binary)],check=True)
        result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=20)
        if result.returncode:print(result.stderr,end='');result.check_returncode()
    report=json.loads(result.stdout)
    assert report['descriptor_bytes']<=1024
    clean=report['clean'];assert clean['render_schema']==2 and len(clean['windows'][0]['phases'])==6
    samples=clean['windows'][0]['render_fences']
    assert samples['samples_complete'] and samples['count']==3 and samples['capacity']==4096
    assert len(samples['cumulative_render_us'])==3 and samples['cumulative_render_us']==sorted(samples['cumulative_render_us'])
    assert not report['unfenced']['windows'][0]['render_fences']['enabled']
    source=(ROOT/'vdp/video/vdu_sys.h').read_text()
    handler=source.split('void VDUStreamProcessor::sendScreenPixel',1)[1].split('// VDU 23, 0, &94',1)[0]
    assert handler.index('RenderFenceRequest')<handler.index('waitPlotCompletion()')<handler.index('context->getPixel')<handler.index('sendScrPixelPacket()')
    drain=(GL/'displaycontroller.cpp').read_text().split('void IRAM_ATTR BitmappedDisplayController::processPrimitives()',1)[1].split('void BitmappedDisplayController::setSprites',1)[0]
    assert drain.index('render.finish(count,false,true)')<drain.index('renderFenceAtQuiescentFlush')<drain.index('resumeBackgroundPrimitiveExecution()')<drain.index('addPrimitive(p)')
    print('PASS: actual queued worker+foreground sums; scoped/task/nested request ownership; closed-only raw JSON; reset, capacity, wrap, DB rejection; unchanged schema2/six phases; sanitize='+str(args.sanitize))

if __name__=='__main__':main()
