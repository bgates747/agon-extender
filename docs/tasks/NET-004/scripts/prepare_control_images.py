"""Prepare local identified carrier-control images. NO device/network access.

The actual later incoming record must establish the UART pair and untouched
suffix before these bytes may be installed. A changed/unknown suffix requires
bounded preservation, never an inferred FF fill or redundant full-flash backup.
"""
from pathlib import Path
import argparse
import json
from image_span import compose, digest, extend_verified_prefix

ROOT = Path(__file__).resolve().parents[4]
UART = 'd9bcb1a2b277e4dcec808d46a33d53879ea4ac4f3e35d69f80345d3c9ac4043e'
BASE = '02addd547f3af3a00cf4fb975ef9d259f2e48d0ded64ef80a053f9b4de10ccf9'
FILTER = '37ba69e3648ea2e7663d071149acc057fab64f8546af3d784afa711505f8e38e'
ROM_BASE = '8270ecd709138fe5ae617a91d5d365eeede0738025d5043fc790541b19b8f281'
ROM_UART = 'a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca'


def prepare(output):
    output = Path(output)
    prefix_path = ROOT / 'agents/net004/uart1-physical-r01/install-p4/independent-app-sectors.bin'
    older_path = ROOT / 'agents/net004/return-edge-physical-r01/install-p4/independent-app-sectors.bin'
    current = extend_verified_prefix(prefix_path.read_bytes(),
        '83a7284f20e4edb0794f86e287b23da16e7a85a7770945eca1ee6f5437fdd9f6',
        older_path.read_bytes(), 'ec7d66d304517da4c72dfce1b2cff1b50f8e4185c72ceba73169e8bc06371124')
    inputs = {}
    for name, source, expected in (
        ('baseline', 'agents/net004/p4-return-edge-r03', BASE),
        ('filter', 'agents/net004/p4-valid-filter-r02', FILTER),
        ('uart', 'agents/net004/p4-uart1-r01', UART)):
        directory = ROOT / source
        manifest = json.loads((directory / 'manifest.json').read_text())
        validation = json.loads((directory / 'validation.json').read_text())
        data = (directory / 'build/agon_extender.bin').read_bytes()
        if (manifest['source_dirty'] or validation['result'] != 'PASS' or
                digest(data) != expected or not manifest['network_messages'] or
                bool(manifest['network_parallel']) != (name != 'uart')):
            raise ValueError('Exact identified component composition required: ' + name)
        inputs[name] = dict(directory=directory, app=data, hash=expected, manifest=manifest)
    if current[:len(inputs['uart']['app'])] != inputs['uart']['app']:
        raise ValueError('Composed incoming UART prefix differs')
    old = older_path.read_bytes()
    if old[:len(inputs['baseline']['app'])] != inputs['baseline']['app']:
        raise ValueError('Known-installed baseline prefix differs')
    table = (inputs['baseline']['directory'] / 'build/partition_table/partition-table.bin').read_bytes()
    for record in inputs.values():
        if (record['directory'] / 'build/partition_table/partition-table.bin').read_bytes() != table:
            raise ValueError('Partition bytes differ; no table install allowed')
    output.mkdir(parents=True, exist_ok=False)
    (output / 'incoming-uart-full-span.bin').write_bytes(current)
    plan = dict(schema='extender-independent-retained-images-v1',
        scope='Local bytes only; later actual incoming identity/suffix admission mandatory',
        p4_application_offset=131072, full_touched_span=len(current),
        incoming_full_span_sha256=digest(current),
        incoming_qualification='Known56 verified1761280B prefix plus proven untouched4096B suffix from45; actual later owner must confirm unchanged, not a fresh device read.',
        partition_table_sha256=digest(table), selections={})
    for name in ('baseline', 'filter'):
        record = inputs[name]
        composed = compose(record['app'], record['hash'], current, digest(current), len(current))
        (output / (name + '-sectors.bin')).write_bytes(composed['payload'])
        plan['selections'][name] = dict(app_sha256=record['hash'], app_bytes=len(record['app']),
            span=composed['span'], payload_sha256=composed['payload_sha256'],
            tail_bytes=composed['tail_bytes'], build_id=record['manifest']['build_id'],
            source_commit=record['manifest']['source_commit'])
    plan['selections']['restore-uart'] = dict(app_sha256=UART, app_bytes=len(inputs['uart']['app']),
        span=len(current), payload_sha256=digest(current),
        note='Restore the entire maximum touched span, including bytes beyond the shorter UART image/sector prefix.',
        build_id=inputs['uart']['manifest']['build_id'], source_commit=inputs['uart']['manifest']['source_commit'])
    for name, source, expected in (
        ('baseline', 'agents/net004/emos-control-tx-diag-r01/ROM.bin', ROM_BASE),
        ('restore-uart', 'agents/net004/emos-uart-rfc25-r02/ROM.bin', ROM_UART)):
        path = ROOT / source
        data = path.read_bytes()
        if len(data) != 131072 or digest(data) != expected:
            raise ValueError('Owner-retained ROM identity differs')
        plan.setdefault('emos', {})[name] = dict(source=source, bytes=len(data), sha256=expected)
    (output / 'images.json').write_text(json.dumps(plan, indent=2) + '\n')
    return plan


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan = prepare(args.output)
    print(json.dumps(dict(scope=plan['scope'], full_touched_span=plan['full_touched_span'], selections=plan['selections']), indent=2))
