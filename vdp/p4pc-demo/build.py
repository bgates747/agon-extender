"""Build a prepared P4-PC experiment with the project-local native ARM tools."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import yaml

root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser()
p.add_argument('--workspace',type=Path,default=root/'agents/p4pc-demo')
p.add_argument('--build-dir',type=Path)
p.add_argument('action',nargs='?',default='build',choices=['build','reconfigure','size'])
a=p.parse_args(); work=a.workspace.resolve()
idf=root/'agents/build001/native-tools/esp-idf'
commit=subprocess.check_output(['git','-C',str(idf),'rev-parse','HEAD'],text=True).strip()
if commit!='b774170ff46c393eeb5e495ea37936038d3f4f4f':raise SystemExit('Expected pinned ESP-IDF 5.5.5')
project=work/'project'
lock=project/'dependencies.lock'
if lock.exists():
    # P4PC-001 r08 exposed stale absolute local paths after copying a lock:
    # the component manager compiled r06's port instead of the patched r08
    # source. Retain registry versions/hashes, rebase only the known copied
    # Olimex local components, and audit actual compiled component paths below.
    graph=yaml.safe_load(lock.read_text());changed=False
    for dependency in graph['dependencies'].values():
        source=dependency.get('source',{})
        if source.get('type')!='local':continue
        previous=str(source['path'])
        marker='/project/components/esp-bsp/components/'
        if marker not in previous:raise SystemExit('Unrecognized local dependency path')
        suffix=previous.split(marker,1)[1]
        selected=(project/'components/esp-bsp/components'/suffix).resolve()
        if not selected.is_relative_to(project.resolve()) or not selected.is_dir():
            raise SystemExit('Local dependency escapes/misses prepared project')
        if str(selected)!=previous:source['path']=str(selected);changed=True
    if changed:
        before=work/'dependencies-before-rebase.lock'
        if not before.exists():shutil.copyfile(lock,before)
        lock.write_text(yaml.safe_dump(graph,sort_keys=False))
env=os.environ.copy()
env.update(IDF_PATH=str(idf),IDF_TOOLS_PATH=str(work/'tools'),
           IDF_PYTHON_ENV_PATH=str(work/'python-env'),ESP_IDF_VERSION='5.5')
env['ESP_ROM_ELF_DIR']=str(work/'tools/tools/esp-rom-elfs/20241011')
bins=[str(x) for x in (work/'tools/tools').glob('**/bin') if x.is_dir()]
env['PATH']=os.pathsep.join([str(work/'python-env/bin'),*bins,env['PATH']])
build=a.build_dir.resolve() if a.build_dir else work/'build'
subprocess.run([str(work/'python-env/bin/python'),str(idf/'tools/idf.py'),
                '-C',str(project),'-B',str(build),a.action],env=env,check=True)
description=json.loads((build/'project_description.json').read_text())
for name,component in description['build_component_info'].items():
    directory=Path(component['dir']).resolve()
    if not any(directory.is_relative_to(base.resolve()) for base in (project,idf,build)):
        raise SystemExit(f'Compiled component {name} came from outside selected source trees: {directory}')
print('Compiled component source paths verified against prepared project and pinned IDF.')
