#!/usr/bin/env python3
"""Bounded integrity tests against a generated runtime package, no hardware."""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_installation import verify

p=argparse.ArgumentParser();p.add_argument('package',type=Path);a=p.parse_args()
assert verify(a.package)>0

def rehash(root):
    # Simulate consistent checksums from a faulty packager: semantic checks must
    # still reject contradictory identities and flash layout.
    path=root/'bundle.yaml';m=yaml.safe_load(path.read_text())
    for name in m['files']:
        f=root/name;m['files'][name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size_bytes':f.stat().st_size}
    path.write_text(yaml.safe_dump(m,sort_keys=False))
    (root/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(root))+'\n' for f in sorted(root.rglob('*')) if f.is_file() and f.name!='SHA256SUMS'))

with tempfile.TemporaryDirectory() as tmp:
    for case in ('tamper','missing','extra','symlink','identity'):
        root=Path(tmp)/case;shutil.copytree(a.package,root)
        f=root/'sd/emos/sdserve.bin'
        if case=='tamper':f.write_bytes(f.read_bytes()+b'x')
        elif case=='missing':f.unlink()
        elif case=='extra':(root/'surprise.bin').write_bytes(b'x')
        elif case=='symlink':f.unlink();f.symlink_to(a.package.resolve()/'sd/emos/sdserve.bin')
        else:
            path=root/'baseline.yaml';m=yaml.safe_load(path.read_text());m['artifacts'][0]['build_id']='incorrect';path.write_text(yaml.safe_dump(m));rehash(root)
        try:verify(root)
        except ValueError:pass
        else:raise AssertionError('accepted '+case)
print('PASS: intact package and five rejection cases')
