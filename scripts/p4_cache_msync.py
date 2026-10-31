"""Generate/verify the pinned rolling cache component; leave ESP-IDF pristine."""
from pathlib import Path
import hashlib,json,shutil,subprocess

ROOT=Path(__file__).resolve().parents[1]
INPUTS=ROOT/'vdp/compat/cache_msync'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def metadata():
    m=json.loads((INPUTS/'derivative.json').read_text())
    if sha(INPUTS/'cache-invalidation.patch')!=m['patch_sha256']:
        raise ValueError('Cache patch identity changed')
    return m

def prepare(idf: Path,project: Path) -> Path:
    m=metadata()
    if subprocess.check_output(['git','-C',str(idf),'rev-parse','HEAD'],text=True).strip()!=m['base_idf_commit']:
        raise ValueError('Cache SDK commit mismatch')
    source=idf/m['source']
    if sha(source)!=m['base_sha256']:raise ValueError('Cache SDK source differs')
    component=project/'components/esp_mm'
    shutil.copytree(source.parent,component,ignore=shutil.ignore_patterns('test_apps'))
    subprocess.run(['patch','--batch','--fuzz=0','-p1','-d',str(component),'-i',str(INPUTS/'cache-invalidation.patch')],check=True,stdout=subprocess.DEVNULL)
    verify(idf,project)
    return component

def verify(idf: Path,project: Path) -> dict:
    m=metadata();original=idf/'components/esp_mm';component=project/'components/esp_mm'
    if sha(idf/m['source'])!=m['base_sha256']:raise ValueError('Cache SDK source differs')
    original_files={str(p.relative_to(original)):sha(p) for p in original.rglob('*')
                    if p.is_file() and 'test_apps' not in p.relative_to(original).parts}
    if original_files!=m['base_files']:raise ValueError('Cache SDK component inventory differs')
    expected=dict(m['base_files']);expected['esp_cache_msync.c']=m['derived_sha256']
    actual={str(p.relative_to(component)):sha(p) for p in component.rglob('*') if p.is_file()}
    if actual!=expected:raise ValueError('Cache component differs from complete pinned derivative')
    return {'base_idf_commit':m['base_idf_commit'],'recipe_sha256':sha(INPUTS/'derivative.json'),
            'files':[{'path':p,'sha256':v} for p,v in sorted(actual.items())]}
