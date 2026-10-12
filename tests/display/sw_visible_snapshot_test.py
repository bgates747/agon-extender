#!/usr/bin/env python3
"""Prove SW snapshot readiness with actual stock paths and bounded concurrency.

Only temporary source copies receive scheduling checkpoints. Product code and
native guards stay intact. Host timings are synchronization checks, not P4 data.
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
GL=ROOT/'vdp/vendor/vdp-gl/src'
RUNTIME=ROOT/'docs/tasks/PORT-003/stock-backend-r2/runtime'
ROW=ROOT/'docs/tasks/PORT-003/stock-backend-r1'
HEADER='vdp/vendor/vdp-gl/src/displaycontroller.h'
CPP='vdp/vendor/vdp-gl/src/displaycontroller.cpp'
ADAPTER='vdp/video/extender/display/stock_runtime_controller.hpp'
NATIVE_H='vdp/video/extender/display/stock_native_access.hpp'
NATIVE_CPP='vdp/video/extender/display/stock_native_access.cpp'

def main():
    service=(ROOT/'vdp/video/extender/display/stock_p4_service.cpp').read_text()
    prepare=service[service.index('bool StockP4Service::prepare('):service.index('void StockP4Service::activate(')]
    activate=service[service.index('void StockP4Service::activate('):service.index('bool StockP4Service::attach(')]
    detach=service[service.index('void StockP4Service::detach('):service.index('void StockP4Service::drawEntry(')]
    assert 'stockBindSoftwareSnapshotWake' not in prepare
    assert activate.index('stockBindSoftwareSnapshotWake') < activate.index('active_.store(true')
    assert detach.index('stockCancelSoftwareSnapshotWake') < detach.index('suspendBackgroundPrimitiveExecution') < detach.index('deleteVideoWorker')
    mode=(ROOT/'vdp/video/agon_screen.h').read_text()
    commit=mode[mode.index('commitPreparedMode(std::move(candidate),'):]
    assert commit.index('_stockFrameService->detach()') < commit.index('service.activate()')
    print('PASS: service binding follows committed activation; cancellation precedes join/delete')
    modified={path:(ROOT/path).read_text() for path in (HEADER,CPP,ADAPTER,NATIVE_H,NATIVE_CPP)}
    with tempfile.TemporaryDirectory(prefix='sw-wake-candidate-') as temp:
        temp=Path(temp);gl=temp/'src';shutil.copytree(GL,gl)
        (gl/'displaycontroller.h').write_text(modified[HEADER])
        cpp=modified[CPP]
        anchor='''    execPrimitive(prim, updateRect, false);
#endif
  }'''
        assert cpp.count(anchor)==1
        (gl/'displaycontroller.cpp').write_text(cpp.replace(anchor,'''    execPrimitive(prim, updateRect, false);
#endif
    agon_visibility_after_primitive(prim.cmd==fabgl::PrimitiveCmd::RefreshSprites);
  }'''))
        display=temp/'video/extender/display';display.mkdir(parents=True)
        (temp/'video/extender/diagnostics').symlink_to(ROOT/'vdp/video/extender/diagnostics',target_is_directory=True)
        adapter=modified[ADAPTER]
        anchor='''      this->execPrimitive(prim, updateRect, false);
#endif
      ++count;'''
        assert adapter.count(anchor)==1
        adapter=adapter.replace(anchor,'''      this->execPrimitive(prim, updateRect, false);
#endif
      agon_visibility_after_primitive(prim.cmd==fabgl::PrimitiveCmd::RefreshSprites);
      ++count;''')
        anchor='''        this->copyLinearRow(y, destination + std::size_t(y) * width, decorate);'''
        assert adapter.count(anchor)==1
        adapter=adapter.replace(anchor,anchor+'\n        agon_visibility_after_row();')
        (display/'stock_runtime_controller.hpp').write_text(adapter)
        (display/'stock_native_access.hpp').write_text(modified[NATIVE_H])
        cpp=modified[NATIVE_CPP]
        anchor='  software_snapshot_wake(software_snapshot_context);'
        assert cpp.count(anchor)==1
        (display/'stock_native_access.cpp').write_text(cpp.replace(anchor,'  agon_visibility_before_wake();\n'+anchor))
        hooks=temp/'hooks.hpp';hooks.write_text('void agon_visibility_after_primitive(bool);\nvoid agon_visibility_after_row();\nvoid agon_visibility_before_wake();\n')
        includes=[temp/'video',ROOT/'tests/display/compat',RUNTIME/'compat',ROW/'compat',ROOT/'docs/tasks/PORT-003/phase-c/tests/compat',ROOT/'docs/tasks/PORT-003/phase-b/tests/compat',gl,ROOT/'vdp/video']
        flags=['-std=c++17','-O1','-g','-pthread','-DFABGL_EMULATED','-DAGON_EXTENDER_STOCK_RUNTIME','-DAGON_EXTENDER_DIRECT_RGB888','-DAGON_EXTENDER_INDEXED_PPA=1','-DAGON_EXTENDER_INDEXED_FRAME_SNAPSHOT=1',
            *['-I'+str(path) for path in includes],'-include',str(RUNTIME/'compat/host_preinclude.hpp'),'-include',str(hooks)]
        # Explicit =0 must remove every feature API/getter/call, not merely skip
        # an implementation behind a still-declared callback contract.
        for source in (gl/'displaycontroller.cpp',display/'stock_native_access.cpp'):
            disabled=subprocess.check_output(['g++',*flags,'-DAGON_EXTENDER_SW_VISIBLE_SNAPSHOT=0','-E','-P',str(source)],text=True)
            for name in ('softwareSpritesVisibleForSnapshot','stockBindSoftwareSnapshotWake','stockRequestSoftwareSnapshotWake','stockSoftwareSpritesShown'):
                assert name not in disabled,(str(source),name)
        sources=[gl/'dispdrivers'/(name+'controller.cpp') for name in ('vgabase','vgapaletted','vga2','vga4','vga8','vga16','vga64')]
        sources += [gl/(name+'.cpp') for name in ('canvas','displaycontroller','codepages','fabfonts')]
        sources += [ROOT/'vdp/video/extender/port/stock_render_utils.cpp',display/'stock_native_access.cpp']
        sources += [ROOT/'vdp/video/extender/display'/(name+'.cpp') for name in ('stock_scanline','stock_runtime_controller','p4_rgb888_controller','presentation_snapshot_pool')]
        sources += [Path(__file__).with_suffix(".cpp")]
        binary=temp/'check'
        subprocess.run(['g++',*flags,'-DAGON_EXTENDER_SW_VISIBLE_SNAPSHOT=1','-ffunction-sections','-fdata-sections','-Wl,--gc-sections',*map(str,sources),'-o',str(binary)],check=True)
        runs=[]
        for repeat in range(3):
            result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=20)
            if result.returncode:
                print(result.stdout,end='');print(result.stderr,end='')
                raise RuntimeError('Actual-controller test failed: '+str(result.returncode))
            print(result.stdout,end='')
            counts=[int(n) for n in next(line for line in result.stdout.splitlines() if line.startswith('STREAMING ')).split()[1:]]
            runs.append(dict(zip(('notifications','capture_attempts','accepted_captures','accepted_during_feed','worker_drain_calls'),counts)))
    print("PASS: value-aware feature-off preprocessing and three actual-controller concurrency/lifetime runs")
    print(json.dumps({'host_only':True,'streaming_repeats':runs,
        'limits':'Deterministic test-only post-native-unlock schedule; uncontrolled host fairness, generic infinite no-show progress, P4 timing, HDMI and double-buffer remain unqualified'},sort_keys=True))

if __name__=='__main__':main()
