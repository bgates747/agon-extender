#!/usr/bin/env python3
"""Run original-controller concurrent host fixtures and real P4 link proof."""
import argparse
import json
import shlex
import subprocess
from pathlib import Path
from verify_binding import ROOT,HERE,R1,verify,sha,CONTROLLERS
from run import call,stamp,target_args,EXPECTED_OBSERVATIONS

IDENTITY='stock-backend-binding-r03'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,default=ROOT/'agents/stock-backend-r2')
    args=parser.parse_args()
    build=IDENTITY+'-b'+stamp();out=args.output_root.resolve()/build
    out.mkdir(parents=True,exist_ok=False)
    result={'identity':IDENTITY,'build':build,'run':'PORT-003-'+stamp(),'status':'experimental',
        'scope':'actual native/service code with host task/timer substrate; P4 compile/relocatable link only',
        'source_checkpoint':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_verification':verify()}
    print(out,flush=True)
    gl=ROOT/'vdp/vendor/vdp-gl/src'
    shared=[gl/f'dispdrivers/{s}controller.cpp' for s in CONTROLLERS]
    shared += [gl/(s+'.cpp') for s in ('canvas','displaycontroller','codepages','fabfonts')]
    shared += [ROOT/'vdp/video/extender/port/stock_render_utils.cpp']
    shared += [ROOT/'vdp/video/extender/display'/(s+'.cpp') for s in
        ('stock_scanline','stock_native_access','stock_runtime_controller','stock_p4_service','presentation_snapshot_pool','cursor_position_adapter','screen_facade_adapter')]
    host=['g++','-std=c++17','-O1','-g','-pthread','-ffunction-sections','-fdata-sections',
          '-DFABGL_EMULATED','-DAGON_EXTENDER_STOCK_RUNTIME',
          '-I'+str(HERE/'compat'),'-I'+str(R1/'compat'),
          '-I'+str(ROOT/'docs/tasks/PORT-003/phase-c/tests/compat'),
          '-I'+str(ROOT/'docs/tasks/PORT-003/phase-b/tests/compat'),
          '-I'+str(gl),'-I'+str(ROOT/'vdp/video'),'-include',str(HERE/'compat/host_preinclude.hpp')]
    target,cwd,database_hash=target_args()
    target=[str(ROOT/'vdp/video/extender/port/stock_task_context.hpp') if a==str(R1/'task_context.hpp') else a for a in target if a!='-DAGON_EXTENDER_STOCK_ROWS_PROOF']+['-DAGON_EXTENDER_STOCK_RUNTIME']
    # The SCons database supplies the Arduino/vendor flags. Its selected boot
    # entry predates native USB; use the installed console component database
    # to verify the two additional USB include directories, without rerunning
    # either build-system generator or installing anything.
    component_database=ROOT/'vdp/.pio/build/p4-console/compile_commands.json'
    console_entry=next(e for e in json.loads(component_database.read_text()) if e['file'].endswith('p4_console.cpp'))
    component_flags=console_entry.get('arguments') or shlex.split(console_entry['command'])
    for include in ('vdp/managed_components/espressif__usb_host_hid/include',
                    'vdp/.pio/packages/framework-espidf/components/usb/include'):
        flag='-I'+str(ROOT/include)
        assert flag in component_flags and (ROOT/include).is_dir(),include
        target.append(flag)
    result['console_component_database_sha256']=sha(component_database.read_bytes())
    result['compile_database_sha256']=database_hash
    result['compilers']={name:subprocess.check_output([flags[0],'--version'],text=True).splitlines()[0]
        for name,flags in [('host',host),('target',target)]}
    (out/'local-commands.json').write_text(json.dumps({'host':host,'target':target,'target_directory':str(cwd)},indent=2)+'\n')
    dependencies=set()
    for kind,flags,working,fixture in [('host',host,ROOT,'runtime_tests.cpp'),('target',target,cwd,'target_probe.cpp')]:
        sources=shared+[HERE/fixture];objects=[]
        for source in sources:
            obj=out/f'{kind}-{source.stem}.o';dep=obj.with_suffix('.d')
            call(flags+['-MMD','-MF',str(dep),'-c',str(source),'-o',str(obj)],working,obj.with_suffix('.log'))
            objects.append(str(obj))
            for p in shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1]):dependencies.add((working/p).resolve())
        if kind=='host':
            binary=out/'runtime-tests'
            call(['g++','-pthread','-Wl,--gc-sections',*objects,'-o',str(binary)],ROOT,out/'host-link.log')
            call([str(binary)],ROOT,out/'runtime-tests.log')
            lines=(out/'runtime-tests.log').read_text().splitlines()
            assert lines[-1].startswith('Stock runtime comparisons:') and '0 failures' in lines[-1]
            result['host']={'passed':sum(s.startswith('PASS ') for s in lines),'checks':lines[:-1],
                'summary':lines[-1],'sha256':sha(binary.read_bytes())}
            for name,source,expected in [('native-regression',R1/'native_rows.cpp',(0,1)),
                                          ('scanline-regression',HERE.parent/'scanline_tests.cpp',(0,))]:
                obj=out/(name+'.o');dep=out/(name+'.d');binary=out/name
                call(flags+['-MMD','-MF',str(dep),'-c',str(source),'-o',str(obj)],working,out/(name+'-compile.log'))
                for p in shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1]):dependencies.add((working/p).resolve())
                call(['g++','-pthread','-Wl,--gc-sections',*objects[:-1],str(obj),'-o',str(binary)],ROOT,out/(name+'-link.log'))
                code=call([str(binary)],ROOT,out/(name+'.log'),expected=expected)
                lines=(out/(name+'.log')).read_text().splitlines()
                failures={line for line in lines if line.startswith('FAIL ')}
                assert (code==1 and failures==EXPECTED_OBSERVATIONS) if name=='native-regression' else (code==0 and not failures)
                result[name]={'passed':sum(line.startswith('PASS ') for line in lines),
                              'inherited_observations':sorted(failures),'sha256':sha(binary.read_bytes())}
        else:
            dsp=ROOT/'vdp/.pio/build/p4-console/esp-idf/espressif__esp-dsp/libespressif__esp-dsp.a'
            binary=out/'stock-runtime-p4.o'
            call([target[0],'-r','-nostdlib',*objects,str(dsp),'-o',str(binary)],ROOT,out/'target-link.log')
            nm=Path(target[0]).with_name('riscv32-esp-elf-nm')
            undefined=subprocess.check_output([str(nm),'-uC',str(binary)],text=True)
            (out/'target-undefined.txt').write_text(undefined)
            for forbidden in ('fabgl::','dspm::','agon::extender::display::','GPIOStream','esp_intr_alloc','xthal_','i2s'):
                assert forbidden not in undefined,forbidden
            # The binding now deliberately imports real task/timer/pthread APIs.
            result['target']={'translation_units':len(sources),'sha256':sha(binary.read_bytes()),
                'format':'RISC-V relocatable; not bootable','remaining_dependencies':undefined.splitlines()}
            console=ROOT/'vdp/video/extender/boot/p4_console.cpp'
            console_object=out/'console-integration.o';console_dep=out/'console-integration.d'
            call(flags+['-MMD','-MF',str(console_dep),'-c',str(console),'-o',str(console_object)],working,out/'console-integration.log')
            for p in shlex.split(console_dep.read_text().replace('\\\n',' ').split(':',1)[1]): dependencies.add((working/p).resolve())
            integrated=out/'console-native-binding.o'
            call([target[0],'-r','-nostdlib',str(binary),str(console_object),str(dsp),'-o',str(integrated)],ROOT,out/'console-link.log')
            imports=subprocess.check_output([str(nm),'-uC',str(integrated)],text=True)
            (out/'console-undefined.txt').write_text(imports)
            for forbidden in ('fabgl::','dspm::','P4DisplayController','LogicalFrameService','P4FrameService','PresentationCompositor'):
                assert forbidden not in imports,forbidden
            result['console_integration']={'sha256':sha(integrated.read_bytes()),
                'boundary':'ordinary console translation unit plus original display closure; network/USB/SDK imports remain; not bootable or selected for deployment'}
        print(kind+' runtime checks complete',flush=True)
    local={str(p):sha(p.read_bytes()) for p in sorted(dependencies) if p.is_file()}
    (out/'local-dependencies.json').write_text(json.dumps(local,indent=2)+'\n')
    result['project_dependencies']={str(p.relative_to(ROOT)):local[str(p)] for p in sorted(dependencies)
        if str(p) in local and p.is_relative_to(ROOT) and '.pio' not in p.parts}
    result['proof_files']={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(HERE.rglob('*'))
        if p.is_file() and p.suffix in ('.py','.cpp','.hpp','.h')}
    (out/'source.patch').write_bytes(subprocess.check_output(['git','diff','--binary'],cwd=ROOT))
    for relative in result['project_dependencies'].keys() | result['proof_files'].keys():
        saved=out/'source'/relative;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes((ROOT/relative).read_bytes())
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['host']['summary']);print(out)


if __name__=='__main__':main()
