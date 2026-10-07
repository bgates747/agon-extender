#!/usr/bin/env python3
"""Stage one familiar-art visual review and hold it for Author inspection.

No benchmark executable/data is edited. The readiness tag opens only after the
eZ80's first public pixel-query fence completes. Diagnostic phase counts are
readiness evidence, not performance results for this deliberately slow fixture.
"""
import argparse
import json
from pathlib import Path
import time
import urllib.request

from render_load import Bench, digest, utc
from sdcard import RemoteError


def status(bench, path):
    with urllib.request.urlopen(bench.config['p4'] + path, timeout=5) as response:
        return json.load(response)


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def absent(error):
    return isinstance(error, RemoteError) and error.status == 6 and error.detail in (b'\x04', b'\x05')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--bench-evidence', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--mode', type=int, choices=(20, 8, 136), required=True)
    parser.add_argument('--endpoint', choices=('p4', 'mainboard'), default='p4')
    args = parser.parse_args()
    manifest = json.loads((args.build / 'manifest.json').read_text())
    selected = manifest['modes'][str(args.mode)]
    binary = args.build / ('mode' + str(args.mode)) / selected['binary']
    data = binary.read_bytes()
    assert len(data) == selected['bytes'] and digest(data) == selected['sha256']
    assert len(data) < 0x30000 and data[64:69] == b'MOS\0\1'
    bench = Bench(args.config, args.bench_evidence)
    assert status(bench, '/sd/status')['online'] and status(bench, '/keyboard/status')['ready']
    installed = json.loads(Path(bench.config['installation_record']).read_text())
    assert installed['renderer'] == 'rgb888' and installed['variant'] == 'normal'
    image = json.loads(Path(installed['manifest']).read_text())
    assert image['display_inputs']['render_storage'] == 'rgb888-panel-direct'
    args.evidence.mkdir(parents=True, exist_ok=True)
    run = args.evidence / ('RGB-001-' + utc())
    run.mkdir()
    record = dict(scope='visual-only familiar-art correctness; no benchmark timings',
                  outcome='preparing', mode=args.mode, endpoint=args.endpoint, started_utc=utc(),
                  fixture_build_id=manifest['build_id'], fixture_sha256=selected['sha256'],
                  manifest_sha256=digest((args.build / 'manifest.json').read_bytes()),
                  host_sha256=digest(Path(__file__).read_bytes()), p4_installation=installed,
                  controls=manifest['controls'], assets=manifest['assets'])
    write(run / 'run.json', record)
    (run / 'controller.py').write_bytes(Path(__file__).read_bytes())
    (run / 'manifest.json').write_bytes((args.build / 'manifest.json').read_bytes())
    (run / 'reference.png').write_bytes((binary.parent / 'reference.png').read_bytes())
    parent = '/extender/' + manifest['build_id'].split('-b', 1)[0]
    remote = parent + '/' + manifest['build_id']
    client = bench.fast_connect()
    try:
        _, attr = client.stat_entry(remote)
        assert attr & 16
    except RemoteError as error:
        if not absent(error):
            raise
        try:
            _, attr = client.stat_entry(parent)
            assert attr & 16
            parent_exists = True
        except RemoteError as parent_error:
            if not absent(parent_error):
                raise
            parent_exists = False
        bench.fast_exit()
        if not parent_exists:
            bench.mkdir(parent)
        bench.mkdir(remote)
        bench.fast_start()
        client = bench.fast_connect()
    target = remote + '/mode' + str(args.mode) + '.bin'
    try:
        client.stat_entry(target)
    except RemoteError as error:
        if not absent(error):
            raise
        bench.fast_put_new(target, data)
    else:
        assert digest(bench.fast_read(target)) == selected['sha256']
    route = 'EXCOM' if args.endpoint == 'p4' else 'LEGACY'
    startup = ('SET KEYBOARD 1\nEMOS KEYINPUT extender\nEMOS ' + route + '\nVDU 22 ' +
               str(args.mode) + '\nLOAD ' + target +
               '\nRUN .\nEMOS LEGACY\nEMOS sdserve --fast /\n').encode('ascii')
    bench.startup(startup)
    bench.fast_exit()
    (run / 'startup.txt').write_bytes(startup)
    record.update(outcome='starting', deployed_path=target, startup_sha256=digest(startup))
    write(run / 'run.json', record)
    bench.reset()
    if args.endpoint == 'mainboard':
        # The stock mainboard VDP does not publish the P4 diagnostic carrier.
        # Keep the exact executable unchanged for this control. Verified SD
        # bytes/startup and input admission establish staging, while the Author
        # must confirm actual first-pose completion and motion on its monitor.
        time.sleep(10)
        keyboard = status(bench, '/keyboard/status')
        listener = status(bench, '/sd/status')
        assert keyboard['ready'] and not listener['online']
        record.update(outcome='running-awaiting-mainboard-visual-confirmation',
                      visual_acceptance='pending', staged_utc=utc(),
                      runtime_readiness='Author visual confirmation required; stock VDP has no P4 first-pose telemetry',
                      keyboard=keyboard,
                      terminal_state='Mainboard route; two poses/s; P pause, Space step, Escape exit. Hold for Author reply.')
        write(run / 'run.json', record)
        write(args.evidence / 'current.json', dict(run=str(run), mode=args.mode,
                                                   endpoint=args.endpoint, outcome=record['outcome']))
        print('Exact familiar-art executable staged on mainboard; holding for Author runtime confirmation.', flush=True)
        return
    print('Familiar game art mode' + str(args.mode) + ' booted; waiting for its completed first pose.', flush=True)
    limit = time.monotonic() + 75
    try:
        while time.monotonic() < limit:
            telemetry = status(bench, '/diagnostics/render-benchmark')
            windows = [w for w in telemetry['windows']
                       if w['tag'] == selected['readiness_tag'] and
                       w['id'] == selected['readiness_case_id'] and not w['end_us']]
            if len(windows) == 1:
                display = status(bench, '/display/status')
                assert display['mode'] == args.mode and display['render_memory'] == 'panel-direct'
                assert display['double_buffered'] == selected['double_buffered']
                record.update(outcome='running-awaiting-visual-reply', visual_acceptance='pending',
                              ready_utc=utc(), display=display,
                              terminal_state='Two poses/s; P pauses, Space steps, Escape exits. Hold for Author reply.')
                write(run / 'run.json', record)
                write(args.evidence / 'current.json', dict(run=str(run), mode=args.mode,
                                                          outcome=record['outcome']))
                print('Familiar-art mode' + str(args.mode) + ' ready; holding for Author reply.', flush=True)
                break
            time.sleep(.2)
        else:
            raise RuntimeError('First-pose fence readiness not observed; leave state for diagnosis')
    except Exception as error:
        record.update(outcome='failed-left-for-diagnosis', failure=repr(error))
        write(run / 'run.json', record)
        raise
    finally:
        if bench.sd:
            bench.sd.lock.close()
            bench.sd = None


if __name__ == '__main__':
    main()
