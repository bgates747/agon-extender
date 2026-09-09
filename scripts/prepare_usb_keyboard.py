#!/usr/bin/env python3
"""Build native P4 USB keyboard acquisition locally; never flash or edit SD media.

The debug-only composition does not initialize Agon UART or change EMOS.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import yaml
from prepare_visible_text import ROOT, git, sha, snapshot, verify_embedded_identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        parser.error('output directory already exists')
    identity_path = ROOT/'vdp/pio/p4-usb-keyboard-identity.json'
    if not identity_path.is_file():
        parser.error('fixture identity approval is pending; no identified bundle can be built')
    identity = json.loads(identity_path.read_text())
    source_identity, status = identity['source_identity'], identity['status']
    if status not in ('draft','experimental','candidate') or not re.fullmatch(
            r'usb-keyboard-probe-r(?:0[1-9]|[1-9][0-9]+)', source_identity):
        parser.error('invalid keyboard fixture identity/status')
    before = {'commit':git('rev-parse','HEAD'), 'dirty':bool(git('status','--porcelain')),
              'source_sha256':snapshot()}
    if status != 'draft' and before['dirty']:
        parser.error('deployable builds require clean committed inputs')
    now = datetime.now(timezone.utc)
    build_id = source_identity+now.strftime('-b%Y-%m-%d-%H-%M-%SZ')
    output.mkdir(parents=True)
    with (output/'p4-build.log').open('w') as log:
        subprocess.run([str(ROOT/'.venv/bin/pio'),'run','-d',str(ROOT/'vdp'),'-e','p4-usb-keyboard'],
                       cwd=ROOT, env=dict(os.environ, AGON_EXTENDER_BUILD_ID=build_id),
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    after = {'commit':git('rev-parse','HEAD'), 'dirty':bool(git('status','--porcelain')),
             'source_sha256':snapshot()}
    if before != after:
        raise SystemExit('source changed during build; no bundle frozen')
    files = []
    for suffix in ('bin','elf','factory.bin'):
        source = ROOT/('vdp/.pio/build/p4-usb-keyboard/firmware.'+suffix)
        verify_embedded_identity(source, source_identity, build_id, status)
        target = output/(build_id+'.'+suffix)
        shutil.copyfile(source,target)
        files.append({'filename':target.name,'sha256':sha(target),'size_bytes':target.stat().st_size})
    lock = ROOT/'vdp/pio/p4-usb-keyboard-dependencies.lock'
    dependencies = yaml.safe_load(lock.read_text())
    baseline = yaml.safe_load((ROOT/'vdp/dependencies.lock').read_text())['dependencies']
    for name, original in baseline.items():
        selected = dependencies['dependencies'].get(name, {})
        if any(original.get(field) != selected.get(field) for field in ('version','component_hash')):
            raise SystemExit('unrelated dependency drift: '+name)
    hid = dependencies['dependencies']['espressif/usb_host_hid']
    if hid['version'] != '1.2.1':
        raise SystemExit('unexpected HID driver version')
    shutil.copyfile(lock, output/'dependencies.lock')
    files.append({'filename':'dependencies.lock','sha256':sha(lock),'size_bytes':lock.stat().st_size})
    managed = ROOT/'vdp/managed_components'
    dependency_files = {str(p.relative_to(managed)):sha(p) for p in sorted(managed.rglob('*'))
                        if p.is_file() and '.git' not in p.parts}
    manifest = {'schema_version':1,'build':{'artifact_id':identity['artifact_id'],
                'source_identity':source_identity,'build_id':build_id,'status':status,
                'created_at':now.isoformat()},'provenance':before,'outputs':files,
                'managed_component_sha256':dependency_files,
                'scope':'One native USB HID boot keyboard, debug console acquisition only',
                'host_phy':'dedicated P4 HS USB_DP/USB_DN, separate from USB Serial/JTAG',
                'notes':['No UART initialization, EMOS deployment or SD changes.',
                         'US processed-key subset; unmapped usage IDs are reported.',
                         'No typematic, LEDs, locale selection, browser or video.',
                         'Host tests and build do not qualify physical wiring or USB enumeration.']}
    (output/'build-manifest.yaml').write_text(yaml.safe_dump(manifest,sort_keys=False))
    print('P4 build PASS; bundle: '+str(output))


if __name__ == '__main__':
    main()
