#!/usr/bin/env python3
"""Read-only local-card verification of the permanent rendering suite."""
import argparse
import datetime
import json
from pathlib import Path

from render_load_collect import card_path, digest

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / 'tests/performance/render_load/resident-suite.json'


def verify(sd_root, catalog):
    root = sd_root.resolve(strict=True)
    if not (root / 'autoexec.txt').is_file():
        raise ValueError('Supply the mounted Agon SD root containing autoexec.txt')
    data = catalog.read_bytes()
    selected = json.loads(data)
    receipt = dict(identity=selected['identity'], catalog_sha256=digest(data),
                   source_sha256=digest(Path(__file__).read_bytes()),
                   checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), files=[])
    seen = set()
    for expected in selected['files']:
        remote = expected['sd_path']
        if remote in seen:
            raise ValueError('Duplicate catalogued SD path: ' + remote)
        seen.add(remote)
        entry = dict(sd_path=remote, expected_bytes=expected['bytes'], expected_sha256=expected['sha256'])
        try:
            raw = card_path(root, remote).read_bytes()
            entry.update(bytes=len(raw), sha256=digest(raw),
                         outcome='pass' if len(raw) == expected['bytes'] and digest(raw) == expected['sha256'] else 'fail')
        except (OSError, ValueError) as error:
            entry.update(outcome='fail', failure=str(error))
        receipt['files'].append(entry)
    receipt['outcome'] = 'pass' if receipt['files'] and all(f['outcome'] == 'pass' for f in receipt['files']) else 'fail'
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sd-root', type=Path, required=True)
    parser.add_argument('--catalog', type=Path, default=DEFAULT_CATALOG)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    # Reserve the receipt before checking; never replace prior evidence.
    with args.receipt.open('x') as output:
        receipt = verify(args.sd_root, args.catalog)
        json.dump(receipt, output, indent=2)
        output.write('\n')
    print(json.dumps(dict(identity=receipt['identity'], outcome=receipt['outcome'], files=len(receipt['files']))))
    return 0 if receipt['outcome'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
