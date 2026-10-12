"""Generate a hash-pinned PPA CLUT component without changing the selected SDK."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
INPUTS=ROOT/'vdp/compat/ppa_clut'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare(idf,project):
    metadata=json.loads((INPUTS/'backport.json').read_text())
    if subprocess.check_output(['git','-C',str(idf),'rev-parse','HEAD'],text=True).strip()!=metadata['base_idf_commit']:
        raise ValueError('PPA CLUT SDK commit mismatch')
    derived=project/'clut-derived'
    for entry in metadata['files']:
        src=idf/entry['path'];dst=derived/entry['path']
        if sha(src)!=entry['base_sha256']:raise ValueError('PPA CLUT base mismatch: '+entry['path'])
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    subprocess.run(['patch','--batch','--fuzz=0','-p1','-d',str(derived),'-i',str(INPUTS/'clut-backport.patch')],check=True,stdout=subprocess.DEVNULL)
    component=project/'components/esp_driver_ppa'
    shutil.copytree(idf/'components/esp_driver_ppa',component,ignore=shutil.ignore_patterns('test_apps'))
    for entry in metadata['files']:
        src=derived/entry['path']
        if sha(src)!=entry['derived_sha256']:raise ValueError('PPA CLUT derived mismatch: '+entry['path'])
        relative=entry['path'].removeprefix('components/')
        dst=component/relative.removeprefix('esp_driver_ppa/') if relative.startswith('esp_driver_ppa/') else component/'overlay/hal'/Path(relative).name
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    with (component/'CMakeLists.txt').open('a') as f:
        f.write('\ntarget_include_directories(${COMPONENT_LIB} BEFORE PUBLIC "${CMAKE_CURRENT_LIST_DIR}/overlay")\n')
    return component
