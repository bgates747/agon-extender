"""Compile actual query helper controls/mutants; no target or emulator."""
from pathlib import Path
import argparse,json,subprocess,shutil
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True)
source=Path(__file__).resolve().parent;header=(source/'uart0_cursor.hpp').read_text()
mutants={'no-fresh-flag-clear':header.replace('    io.clear_cursor();','    // no clear'),
         'ignore-coordinates':header.replace('return io.x()==x&&io.y()==y;','return true;'),
         'ignore-fresh-completion':header.replace('if(io.cursor_ready())','if(true)'),
         'retry-refused-query':header.replace('if(!io.write(request,sizeof(request)))return false;', 'if(!io.write(request,sizeof(request)))if(!io.write(request,sizeof(request)))return false;')}
rows=[]
for name,h in [('control',header),*mutants.items()]:
 d=a.output/name;d.mkdir();(d/'uart0_cursor.hpp').write_text(h);shutil.copyfile(source/'test_uart0_cursor.cpp',d/'test.cpp')
 cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(d/'test.cpp'),'-o',str(d/'check')]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);(d/'compile.log').write_text(r.stdout+r.stderr);assert r.returncode==0,name
 r=subprocess.run([str(d/'check')],capture_output=True,text=True,timeout=30);(d/'run.log').write_text(r.stdout+r.stderr)
 assert (r.returncode==0)==(name=='control'),(name,r.returncode)
 rows.append({'name':name,'compiled':True,'returncode':r.returncode,'expected_pass':name=='control'})
report={'passed':True,'cases':['zero/nonzero/mixed coordinates','stale flag','wrong coordinate','position refusal','query refusal','cancellation','24bit wrap','timeout across wrap','stopped-clock fuse'],'negative_controls':rows,'no_hardware':True}
(a.output/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
