#!/usr/bin/env python3
"""Build the focused browser typing P4 bundle; never flash or edit SD media.
EMOS and the SD application are independently identified by their manifests.
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
    selection = json.loads((ROOT/'vdp/pio/p4-browser-typing-source-selection.json').read_text())
    if selection.get('retired'):
        parser.error('Browser keyboard capture is retired; see docs/tasks/REMOTE-001.md. Use the recorded historical commit to reproduce earlier evidence.')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        parser.error('output directory already exists')
    identity_path = ROOT/'vdp/pio/p4-browser-typing-identity.json'
    if not identity_path.is_file():
        parser.error('fixture identity approval is pending; no identified bundle can be built')
    identity = json.loads(identity_path.read_text())
    source_identity, status = identity['source_identity'], identity['status']
    if status not in ('draft','experimental','candidate') or not re.fullmatch(
            r'browser-keyboard-probe-r(?:0[1-9]|[1-9][0-9]+)', source_identity):
        parser.error('invalid keyboard fixture identity/status')
    before = {'commit':git('rev-parse','HEAD'), 'dirty':bool(git('status','--porcelain')),
              'source_sha256':snapshot()}
    if status != 'draft' and before['dirty']:
        parser.error('deployable builds require clean committed inputs')
    now = datetime.now(timezone.utc)
    build_id = source_identity+now.strftime('-b%Y-%m-%d-%H-%M-%SZ')
    output.mkdir(parents=True)
    with (output/'p4-build.log').open('w') as log:
        subprocess.run([str(ROOT/'.venv/bin/pio'),'run','-d',str(ROOT/'vdp'),'-e','p4-browser-typing'],
                       cwd=ROOT, env=dict(os.environ, AGON_EXTENDER_BUILD_ID=build_id),
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    after = {'commit':git('rev-parse','HEAD'), 'dirty':bool(git('status','--porcelain')),
             'source_sha256':snapshot()}
    if before != after:
        raise SystemExit('source changed during build; no bundle frozen')
    files = []
    for suffix in ('bin','elf','factory.bin'):
        source = ROOT/('vdp/.pio/build/p4-browser-typing/firmware.'+suffix)
        verify_embedded_identity(source, source_identity, build_id, status)
        target = output/(build_id+'.'+suffix)
        shutil.copyfile(source,target)
        files.append({'filename':target.name,'sha256':sha(target),'size_bytes':target.stat().st_size})
    (output/'autoexec.txt').write_bytes(b'VDU 22 3\r\nLOAD /bin/EMBOOT.BIN\r\nRUN\r\n'
                                      b'LOAD /bin/BTYPE.BIN\r\nRUN\r\nEMOS KEYINPUT\r\n')
    manifest = {'schema_version':1,'build':{'artifact_id':identity['artifact_id'],
                'source_identity':source_identity,'build_id':build_id,'status':status,
                'variant':'focused-typing','created_at':now.isoformat()},'provenance':before,'outputs':files,
                'baud_rate':1152000,
                'admission':'US locale then matched General Poll; browser opt-in and focus',
                'keyboard_session':'one controller, bounded queue, two-second lease',
                'requires':'BTYPE SD application and EMOS v0.1.9 shared resident keyboard/text UART',
                'notes':['Local build only; hardware qualification and human emulator review are separate.']}
    (output/'build-manifest.yaml').write_text(yaml.safe_dump(manifest,sort_keys=False))
    print('P4 build PASS; bundle: '+str(output))


if __name__ == '__main__':
    main()
