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
    # HAL is a project-local component too. A transitive BEFORE include on the
    # PPA target does not precede another consumer's direct HAL dependency
    # (esp-dl exposed this in the full build). Override the component that owns
    # the headers so all consumers see one consistent API, without editing IDF.
    for name in ('esp_driver_ppa','hal'):
        shutil.copytree(idf/'components'/name,project/'components'/name,
                        ignore=shutil.ignore_patterns('test_apps'))
    component=project/'components/esp_driver_ppa'
    for entry in metadata['files']:
        src=derived/entry['path']
        if sha(src)!=entry['derived_sha256']:raise ValueError('PPA CLUT derived mismatch: '+entry['path'])
        dst=project/entry['path']
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    return component
