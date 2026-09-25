#!/usr/bin/env python3
"""Offline integrity check for an extracted installation package; never execute it."""
import argparse
import hashlib
from pathlib import Path
import yaml


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def verify(root):
    root=root.resolve()
    def member(name):
        p=root/name
        if Path(name).is_absolute() or '..' in Path(name).parts or p.is_symlink() or not p.is_file() or root not in p.resolve().parents:
            raise ValueError('invalid/missing package member: '+name)
        return p
    manifest=yaml.safe_load(member('bundle.yaml').read_text())
    if manifest['schema_version']!=1 or manifest['selection']!='unselected':raise ValueError('unexpected package selection')
    baseline=yaml.safe_load(member(manifest['baseline']).read_text())
    if baseline['baseline']['status']!='qualified':raise ValueError('not an accepted installation')
    required={'p4/firmware.bin','p4/firmware.factory.bin','p4/bootloader.bin','p4/partitions.bin','p4/boot_app0.bin','p4/flash-layout.json','sd/emos/sdserve.bin','sd/extender/install/em-v019.bin','scripts/sdcard.py','scripts/keyboard.py','scripts/screen_text.py','scripts/reset_agon.py','scripts/reset_bridge.py','INSTALL.md','NOTICES.md','baseline.yaml','builds/p4.yaml','builds/emos.yaml','builds/listener.yaml'}
    if not required.issubset(manifest['files']):raise ValueError('missing required inventory')
    for name,record in manifest['files'].items():
        f=member(name)
        if sha(f)!=record['sha256'] or f.stat().st_size!=record['size_bytes']:raise ValueError('inventory mismatch: '+name)
    checks={}
    for line in member('SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        if name in checks:raise ValueError('duplicate checksum member')
        checks[name]=digest
        if sha(member(name))!=digest:raise ValueError('checksum mismatch: '+name)
    actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file()}
    if actual!=set(checks)|{'SHA256SUMS'} or set(checks)!=set(manifest['files'])|{'bundle.yaml'}:raise ValueError('unexpected or unlisted files')
    import json
    layout=json.loads(member('p4/flash-layout.json').read_text());factory=member('p4/firmware.factory.bin').read_bytes()
    if layout['factory_offset']!='0x0' or layout['chip']!='esp32p4':raise ValueError('unexpected flash target')
    for offset,name in layout['segments'].items():
        data=member('p4/'+name).read_bytes();start=int(offset,16)
        if factory[start:start+len(data)]!=data:raise ValueError('factory mismatch')
    rom=member('sd/extender/install/em-v019.bin').read_bytes()
    if len(rom)>131072 or hashlib.sha256(rom.ljust(131072,b'\xff')).hexdigest()!=manifest['expected_emos_rom']['sha256']:raise ValueError('ROM mismatch')
    mapping={'p4':('uart-excom-console','p4/firmware.bin'),'emos':('agon-emos','sd/extender/install/em-v019.bin'),'listener':('sdserve','sd/emos/sdserve.bin')}
    for name,(artifact,payload) in mapping.items():
        build=yaml.safe_load(member('builds/'+name+'.yaml').read_text())
        entry=next(x for x in baseline['artifacts'] if x['artifact_id']==artifact)
        if entry['build_id']!=build['build']['build_id'] or entry['identity']!=build['build']['source_identity']:raise ValueError('baseline/build disagreement')
        if build['build']['build_id'].encode() not in member(payload).read_bytes():raise ValueError('embedded identity missing')
        if not any(x['sha256']==sha(member(payload)) for x in build['outputs']):raise ValueError('build/output mismatch')
    p4=yaml.safe_load(member('builds/p4.yaml').read_text())
    for role in ('application','bootloader'):
        pin=p4['silicon_configs'][role];cfg=member('builds/'+role+'-sdkconfig.h')
        if sha(cfg)!=pin['sha256'] or (pin['minimum'],pin['maximum'])!=(100,199):raise ValueError('silicon pin mismatch')
        for key,value in [('MIN',100),('MAX',199)]:
            if f'#define CONFIG_ESP32P4_REV_{key}_FULL {value}\n' not in cfg.read_text():raise ValueError('incompatible silicon configuration')
    return len(checks)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);a=p.parse_args()
    print(f'PASS: {verify(a.root)} package files; manifest, identities, ROM and flash segments agree')
