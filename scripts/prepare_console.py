#!/usr/bin/env python3
"""Build P4 ExCom UART console firmware locally; never flash or edit SD media.

The USB composition uses the retained serializer and requires EMOS extender admission.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import io
import html
from urllib.parse import urlsplit
import yaml
from prepare_visible_text import ROOT, git, sha, snapshot, verify_embedded_identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--reset-url', help='Optional operator reset bridge URL; local manifest only')
    parser.add_argument('--admission-probe', action='store_true', help='Explicit temporary A04 hardware peer; never production')
    parser.add_argument('--staged-webdav', action='store_true', help='Enable experimental Legacy finite-job WebDAV runtime')
    parser.add_argument('--lcd', action='store_true', help='Enable experimental V2 DSI landscape output')
    parser.add_argument('--lcd-pattern', action='store_true', help='Bench-only DSI hardware color bars; requires --lcd')
    parser.add_argument('--lcd-framebuffer-pattern', action='store_true', help='Bench-only CPU-written RGB888 bars; requires --lcd')
    parser.add_argument('--lcd-legacy-timing', action='store_true', help='Bench-only IDF5.4.1 host timing comparison; requires static framebuffer pattern')
    args = parser.parse_args()
    if args.lcd_legacy_timing and not args.lcd_framebuffer_pattern:
        parser.error('--lcd-legacy-timing requires --lcd-framebuffer-pattern')
    if args.lcd_framebuffer_pattern and (not args.lcd or args.lcd_pattern):
        parser.error('--lcd-framebuffer-pattern requires --lcd and excludes --lcd-pattern')
    if args.lcd_pattern and not args.lcd:
        parser.error('--lcd-pattern requires --lcd')
    if args.staged_webdav and args.admission_probe:
        parser.error('runtime and diagnostic admission peer are mutually exclusive')
    if args.reset_url and urlsplit(args.reset_url).scheme not in ('http','https'):
        parser.error('reset URL must use HTTP(S)')
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        parser.error('output directory already exists')
    identity_path = ROOT/'vdp/pio/p4-console-identity.json'
    if not identity_path.is_file():
        parser.error('fixture identity approval is pending; no identified bundle can be built')
    identity = json.loads(identity_path.read_text())
    source_identity, status = identity['source_identity'], identity['status']
    if status not in ('draft','experimental','candidate') or not re.fullmatch(
            r'uart-excom-console-r(?:0[1-9]|[1-9][0-9]+)', source_identity):
        parser.error('invalid keyboard fixture identity/status')
    before = {'commit':git('rev-parse','HEAD'), 'dirty':bool(git('status','--porcelain')),
              'source_sha256':snapshot()}
    if before['dirty']:
        parser.error('deployable builds require clean committed inputs')
    now = datetime.now(timezone.utc)
    build_id = source_identity+now.strftime('-b%Y-%m-%d-%H-%M-%SZ')
    output.mkdir(parents=True)
    # Export committed inputs: no retained task snapshots or old object files.
    source_root = output/'source'
    source_root.mkdir()
    archive = subprocess.check_output(['git','archive','HEAD','vdp'], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as archive_file:
        archive_file.extractall(source_root, filter='data')
    project = source_root/'vdp'
    if args.reset_url:
        page = project/'video/extender/web/index.html'
        page.write_text(page.read_text().replace('name="agon-reset-url" content=""',
            'name="agon-reset-url" content="'+html.escape(args.reset_url, quote=True)+'"'))
    if args.admission_probe:
        config=project/'video/extender/diagnostics/admission/config.hpp'
        config.write_text(config.read_text().replace('AGON_EXTENDER_ADMISSION_PROBE 0','AGON_EXTENDER_ADMISSION_PROBE 1'))
    if args.staged_webdav:
        config=project/'video/extender/storage/webdav/runtime.hpp'
        config.write_text(config.read_text().replace('AGON_EXTENDER_STAGED_WEBDAV 0','AGON_EXTENDER_STAGED_WEBDAV 1'))
    if args.lcd:
        config=project/'video/extender/display/lcd/config.hpp'
        config.write_text(config.read_text().replace('AGON_EXTENDER_LCD 0','AGON_EXTENDER_LCD 1'))
    if args.lcd_pattern:
        config.write_text(config.read_text().replace('AGON_EXTENDER_LCD_PATTERN 0','AGON_EXTENDER_LCD_PATTERN 1'))
    if args.lcd_framebuffer_pattern:
        config.write_text(config.read_text().replace('AGON_EXTENDER_LCD_PATTERN 0','AGON_EXTENDER_LCD_PATTERN 2'))
    if args.lcd_legacy_timing:
        config.write_text(config.read_text().replace('AGON_EXTENDER_LCD_LEGACY_TIMING 0','AGON_EXTENDER_LCD_LEGACY_TIMING 1'))
    # Reuse downloaded tools only, never build products or managed source trees.
    (project/'.pio').mkdir()
    packages = ROOT/'vdp/.pio/packages'
    if packages.is_dir():
        (project/'.pio/packages').symlink_to(packages)
    clean_env = {key:value for key,value in os.environ.items()
                 if not key.startswith('AGON_EXTENDER_')}
    with (output/'p4-build.log').open('w') as log:
        subprocess.run([str(ROOT/'.venv/bin/pio'),'run','-v','-d',str(project),'-e','p4-console'],
                       cwd=source_root, env=dict(clean_env, AGON_EXTENDER_BUILD_ID=build_id),
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    after = {'commit':git('rev-parse','HEAD'), 'dirty':bool(git('status','--porcelain')),
             'source_sha256':snapshot()}
    if before != after:
        raise SystemExit('source changed during build; no bundle frozen')
    # The separately configured bootloader must target the same physical silicon.
    # An application-only sdkconfig hash missed a rev3 bootloader in R01-07.
    silicon_configs = {}
    for name, relative in (
        ('application', '.pio/build/p4-console/config/sdkconfig.h'),
        ('bootloader', '.pio/build/p4-console/bootloader/config/sdkconfig.h'),
    ):
        config = project / relative
        text = config.read_text()
        for setting, value in (('CONFIG_ESP32P4_REV_MIN_FULL', 100),
                               ('CONFIG_ESP32P4_REV_MAX_FULL', 199)):
            if f'#define {setting} {value}\n' not in text:
                raise SystemExit(f'{name} silicon mismatch: expected {setting}={value}')
        silicon_configs[name] = {'sha256': sha(config), 'minimum': 100, 'maximum': 199}
    files = []
    for suffix in ('bin','elf','factory.bin'):
        source = project/('.pio/build/p4-console/firmware.'+suffix)
        verify_embedded_identity(source, source_identity, build_id, status)
        target = output/(build_id+'.'+suffix)
        shutil.copyfile(source,target)
        files.append({'filename':target.name,'sha256':sha(target),'size_bytes':target.stat().st_size})
    lock = ROOT/'vdp/pio/p4-console-dependencies.lock'
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
    managed = project/'managed_components'
    dependency_files = {str(p.relative_to(managed)):sha(p) for p in sorted(managed.rglob('*'))
                        if p.is_file() and '.git' not in p.parts}
    assets = {}
    application = (project/'.pio/build/p4-console/firmware.bin').read_bytes()
    selection = json.loads((project/'pio/p4-console-source-selection.json').read_text())
    for relative in selection['embedded_text_files']:
        asset = project/relative
        if asset.read_bytes() + b'\0' not in application:
            raise SystemExit('built image does not embed asset: '+relative)
        assets[relative] = sha(asset)
    for name in ('partitions.bin', 'bootloader.bin'):
        source = project/'.pio/build/p4-console'/name
        shutil.copyfile(source, output/name)
        files.append({'filename':name,'sha256':sha(source),'size_bytes':source.stat().st_size})
    tool_versions = subprocess.check_output([str(ROOT/'.venv/bin/pio'), 'pkg', 'list',
        '-d',str(project),'-e','p4-console'], text=True)
    (output/'tool-versions.txt').write_text(tool_versions)
    manifest = {'schema_version':1,'build':{'artifact_id':identity['artifact_id'],
                'source_identity':source_identity,'build_id':build_id,'status':status,
                'created_at':now.isoformat()},'lcd':args.lcd,'lcd_legacy_timing':args.lcd_legacy_timing,'lcd_pattern':args.lcd_pattern,'lcd_framebuffer_pattern':args.lcd_framebuffer_pattern,'staged_webdav':args.staged_webdav,'admission_probe':args.admission_probe,'reset_url':args.reset_url,'provenance':before,'outputs':files,
                'managed_component_sha256':dependency_files, 'embedded_asset_sha256':assets,
                'effective_sdkconfig_sha256':sha(project/'pio/p4-console.sdkconfig'),
                'silicon_configs':silicon_configs,
                'scope':'Explicit ExCom ordinary UART console, native USB input and retained browser video',
                'host_phy':'dedicated P4 HS USB_DP/USB_DN, separate from USB Serial/JTAG',
                'notes':['UART1 1152000/8N1 RTS/CTS; no physical deployment or SD edits by this builder.',
                         'UK/US printable/editing-key subset with held-key cleanup.',
                         'Native USB and explicit browser keyboard ownership; retained browser reset UI.',
                         'Host tests and build do not qualify physical wiring or USB enumeration.']}
    (output/'build-manifest.yaml').write_text(yaml.safe_dump(manifest,sort_keys=False))
    print('P4 build PASS; bundle: '+str(output))


if __name__ == '__main__':
    main()
