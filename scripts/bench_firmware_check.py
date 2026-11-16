#!/usr/bin/env python3
"""Compare requested firmware against recorded Olimex installation evidence.

Host-only: does not inspect hardware, obtain a lease, or authorize a flash.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / 'agents/bench-scheduler/installed-firmware.json'
COMPONENTS = {'vdp': ('native_vdp', 'native_vdp_sha256'),
              'emos': ('emos', 'emos_rom_sha256'),
              'p4': ('p4', 'p4_app_sha256')}


def compare(inventory, requirements):
    results = []
    for component, artifact in requirements:
        data = artifact.read_bytes()
        required = hashlib.sha256(data).hexdigest()
        record_name, hash_name = COMPONENTS[component]
        record = inventory.get(record_name) or {}
        installed = inventory.get('components', {}).get(hash_name)
        receipt = record.get('verification_receipt') or record.get('verification')
        receipt_path = Path(receipt) if receipt else None
        if receipt_path and not receipt_path.is_absolute():
            receipt_path = ROOT / receipt_path
        valid = (not inventory.get('pending_operation') and installed and
                 record.get('sha256') == installed and receipt_path and
                 receipt_path.is_file())
        state = 'unknown' if not valid else ('match' if installed == required else 'different')
        results.append({'component': component, 'artifact': str(artifact),
                        'required_sha256': required, 'recorded_sha256': installed,
                        'record_status': record.get('status'),
                        'verification_receipt': str(receipt_path) if receipt_path else None,
                        'result': state})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument('--require', action='append', required=True, metavar='COMPONENT=ARTIFACT',
                        help='Repeat for vdp, emos or p4; ARTIFACT is the exact required binary')
    args = parser.parse_args()
    requirements = []
    seen = set()
    for item in args.require:
        name, sep, path = item.partition('=')
        if not sep or name not in COMPONENTS or not path or name in seen:
            parser.error('Use each of vdp=PATH, emos=PATH or p4=PATH at most once')
        seen.add(name)
        requirements.append((name, Path(path)))
    try:
        inventory = json.loads(args.inventory.read_text())
        results = compare(inventory, requirements)
    except (OSError, ValueError, TypeError) as error:
        print(f'Cannot assess firmware: {error}', file=sys.stderr)
        return 2
    print(json.dumps({'basis': 'recorded installation evidence, not a live device check',
                      'note': 'Confirm no intervening write and current custody; unknown is not a match.',
                      'results': results}, indent=2))
    return 0 if all(item['result'] == 'match' for item in results) else 1


if __name__ == '__main__':
    sys.exit(main())
