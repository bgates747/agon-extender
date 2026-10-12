#!/usr/bin/env python3
"""Prepare an offline, CLI-invoked indexed/PPA comparison; no bench access.

Frozen SCAN executables and resident fixtures are inputs, never rebuilt here.
Autoexec payloads contain setup only. Generated MOS batches are separate files
and must be invoked explicitly after positive CLI admission.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tarfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def batch(lines):
    return ('\r\n'.join(lines) + '\r\n').encode('ascii')


def prepare(root, fixture_plan, builds, rollback, output, campaign):
    if not re.fullmatch(r'r07-[a-z0-9-]{1,32}', campaign):
        raise ValueError('campaign must be r07- plus at most32 lowercase letters/digits/hyphens')
    output.mkdir(parents=True, exist_ok=False)
    scan = load_module('scan_config', root/'tests/performance/scan/build.py')
    codec = load_module('render_codec', root/'tests/performance/render_load/codec.py')
    generate = load_module('render_generate', root/'tests/performance/render_load/generate.py')
    prior = json.loads(fixture_plan.read_text())
    resident = json.loads((root/'tests/performance/render_load/resident-suite.json').read_text())
    record = {'campaign': campaign, 'state': 'offline-prepared-not-deployed',
              'source_commit': None, 'fixture_build': prior['fixture_build'],
              'fixture_source': prior['fixture_source'], 'files': {}, 'cases': [],
              'resident_files': [], 'firmware': {},
              'clock': {'prt_counts_per_second_nominal': 72000,
                        'counts_per_60hz_budget': 1200, 'mos_units_per_second_nominal': 120},
              'launch_policy': 'Explicit MOS EXEC only; never autoexec/reset launch'}
    def put(name, data, sd_path=None):
        path = output/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        record['files'][name] = {'bytes': len(data), 'sha256': digest(data), 'sd_path': sd_path}
    results = '/agents/extender/results/'+campaign
    for label in ('baseline', 'candidate'):
        build = builds[label]
        m = json.loads((build/'manifest.json').read_text())
        assert json.loads((build/'validation.json').read_text())['result'] == 'PASS'
        assert not m['source_dirty'] and m['source_snapshot_verified']
        assert not any(m.get(k, False) for k in ('parallel_boot_candidate', 'parallel_probe_candidate', 'parallel_data_check', 'exext_stream'))
        expected = 'linear-physical-rgb222' if label=='candidate' else 'rgb888-panel-direct-except-private-320x240'
        assert m['display_inputs']['render_storage'] == expected
        if record['source_commit'] is None:
            record['source_commit'] = m['source_commit']
            first_source = (build/'source-inputs.json').read_bytes()
        else:
            assert record['source_commit'] == m['source_commit']
            assert first_source == (build/'source-inputs.json').read_bytes()
        record['firmware'][label] = {'build_id': m['build_id'],
                                      'manifest_sha256': digest((build/'manifest.json').read_bytes())}
        label_root = results+'/'+label
        tag = int.from_bytes(hashlib.sha256((campaign+label).encode()).digest()[:3], 'little') or 1
        lines = ['EMOS EXCOM --keep-display']
        for case in (3, 7, 8, 9):
            entry = next(e for e in prior['cases'] if e['case']==case)
            assert digest((root/entry['binary']).read_bytes()) == entry['binary_sha256']
            target = label_root+f'/t{case:02}.bin'
            cfg = scan.config(case, entry['frames'], entry['warmup'], target,
                              extra_flags=4, window_tag=tag)
            cfg_name = f'{label}/t{case:02}.cfg'
            put(cfg_name, cfg, entry['sd_config'])
            record['cases'].append({**entry, 'variant': label, 'window_tag': tag,
                                   'configuration': cfg_name, 'configuration_sha256': digest(cfg),
                                   'result': target})
            lines += ['CD '+str(Path(entry['sd_binary']).parent),
                      'LOAD '+Path(entry['sd_binary']).name, 'RUN']
        lines += ['CD /', 'EMOS LEGACY', 'ECHO R07 finite suite complete', 'EMOS sdserve --fast /']
        put(label+'/suite20.txt', batch(lines), label_root+'/suite20.txt')
        fixture = next(e for e in resident['files'] if e['role']=='benchmark')
        for mode in (20, 136):
            sub = label_root+f'/hw{mode}'
            data = next(e for e in resident['files'] if e['sd_path'].endswith(f'/data{mode}.rle'))
            chart = next(e for e in resident['files'] if e['role']=='colour-chart' and e['mode']==mode)
            hw_tag = int.from_bytes(hashlib.sha256((campaign+label+str(mode)).encode()).digest()[:3], 'little') or 1
            plan = codec.plan(data['sd_path'], sub+'/results.bin', mode, generate.MODES[mode], hw_tag, 54, 55)
            put(f'{label}/hw{mode}/plan.bin', plan, sub+'/plan.bin')
            put(f'{label}/hardware{mode}.txt', batch(['EMOS EXCOM --keep-display', 'CD '+sub,
                  'LOAD '+fixture['sd_path'], 'RUN .', 'CD /', 'EMOS LEGACY',
                  'EMOS sdserve --fast /']), label_root+f'/hardware{mode}.txt')
            put(f'{label}/chart{mode}.txt', batch(['EMOS EXCOM --keep-display', 'LOAD '+chart['sd_path'],
                  'RUN .', 'EMOS LEGACY', 'EMOS sdserve --fast /']), label_root+f'/chart{mode}.txt')
            for e in (fixture, data, chart):
                if e not in record['resident_files']:
                    record['resident_files'].append(e)
    # Setup selects the P4 route before its mode. Ordinary EXCOM resets P4 to
    # mode0, so later explicit batches must preserve this mode with --keep-display.
    # No LOAD/RUN/EXEC belongs in root startup; reset alone starts no test.
    for mode in (20, 136):
        data = batch(['SET KEYBOARD 1', 'EMOS KEYINPUT extender', 'EMOS EXCOM', f'VDU 22 {mode}'])
        assert not any(token in data.upper() for token in (b'LOAD ', b'RUN', b'EXEC '))
        put(f'startup-mode{mode}.txt', data)
    segments = {0x2000:'bootloader/bootloader.bin', 0x8000:'partition_table/partition-table.bin',
                0xf000:'ota_data_initial.bin', 0x20000:'agon_extender.bin'}
    archive = output/'firmware.tar.gz'
    with tarfile.open(archive, 'w:gz', compresslevel=1) as tar:
        for label, build in {**builds, 'rollback': rollback}.items():
            m = json.loads((build/'manifest.json').read_text())
            artifacts = {Path(a['path']).resolve(): a for a in m['artifacts']}
            actual = {int(k, 0):v for k,v in json.loads((build/'build/flasher_args.json').read_text())['flash_files'].items()}
            assert actual == segments
            rec = record['firmware'].setdefault(label, {'build_id': m['build_id']})
            rec['segments'] = []
            for offset, name in segments.items():
                path = build/'build'/name
                a = artifacts[path.resolve()]
                assert path.stat().st_size == a['bytes'] and digest(path.read_bytes()) == a['sha256']
                tar.add(path, arcname=label+'/'+name)
                rec['segments'].append({'offset':hex(offset), 'path':name,
                                        'bytes':a['bytes'], 'sha256':a['sha256']})
            for name in ('manifest.json', 'validation.json', 'source-inputs.json', 'source.tar.gz', 'sdkconfig', 'dependencies.lock'):
                tar.add(build/name, arcname=label+'/'+name)
    with tarfile.open(archive, 'r:gz') as tar:
        for label, rec in record['firmware'].items():
            for s in rec['segments']:
                assert digest(tar.extractfile(label+'/'+s['path']).read()) == s['sha256']
    record['archive'] = {'path': archive.name, 'sha256': digest(archive.read_bytes()), 'bytes': archive.stat().st_size}
    (output/'plan.json').write_text(json.dumps(record, indent=2)+'\n')
    for name, e in record['files'].items():
        assert digest((output/name).read_bytes()) == e['sha256']
    print('Offline package passes: same-source firmware pair, exact rollback, four finite cases, resident controls, setup-only startup and explicit CLI batches.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--fixture-plan', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--rollback', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--campaign', required=True)
    a = p.parse_args()
    prepare(a.root.resolve(), a.fixture_plan.resolve(),
            {'baseline':a.baseline.resolve(), 'candidate':a.candidate.resolve()},
            a.rollback.resolve(), a.output.resolve(), a.campaign)


if __name__=='__main__':
    main()
