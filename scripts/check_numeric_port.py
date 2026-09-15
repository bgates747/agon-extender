#!/usr/bin/env python3
"""Bounded numeric review tripwire and sanitized regressions; no rebaselining."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
REVIEW = Path('docs/dependencies/reviewed/numeric-conversions.json')


def check_inputs(root, review):
    if review.get('schema_version') != 1 or not review.get('review_reference'):
        raise ValueError('Missing supported schema/review reference')
    inputs = review.get('inputs')
    if not isinstance(inputs, dict) or not inputs:
        raise ValueError('Empty numeric review inputs')
    errors = []
    for name, digest in sorted(inputs.items()):
        path = Path(name)
        if path.is_absolute() or '..' in path.parts:
            raise ValueError('Review paths must be repository-relative')
        target = root / path
        if not target.is_file():
            errors.append(f'missing: {name}')
        elif hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            errors.append(f'changed: {name}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional run report; use ignored agents/')
    args = parser.parse_args()
    started = time.monotonic()
    report = dict(started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  scope='bounded numeric review and host regressions, not target qualification',
                  passed=False, tests=[])
    try:
        review = json.loads((ROOT / REVIEW).read_text())
        report['review_sha256'] = hashlib.sha256((ROOT / REVIEW).read_bytes()).hexdigest()
        report['drift'] = check_inputs(ROOT, review)
        if report['drift']:
            raise RuntimeError('\n'.join(report['drift']) + '\nReconcile using numeric-upstream-import-r01; do not blindly refresh hashes.')
        with tempfile.TemporaryDirectory(prefix='numeric-port-') as temp:
            binary = str(Path(temp) / 'fixed')
            commands = [
                ('fixed_compile', ['c++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                 '-fsanitize=undefined,float-cast-overflow', '-fno-sanitize-recover=all',
                 '-Ivdp/video', 'tests/fixed_conversion_test.cpp', '-o', binary]),
                ('fixed', [binary]),
                ('parser', [sys.executable, 'tests/numeric_parser_test.py']),
                ('renderer', [sys.executable, 'tests/numeric_renderer_test.py']),
            ]
            for name, command in commands:
                before = time.monotonic()
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                entry = dict(name=name, exit_code=result.returncode,
                             elapsed_seconds=time.monotonic()-before,
                             stdout=result.stdout, stderr=result.stderr)
                report['tests'].append(entry)
                print(f'{name}: exit {result.returncode}\n{result.stdout}', flush=True)
                if result.returncode:
                    raise RuntimeError(f'{name} failed: {result.stderr}')
        # Detect edits during the test run, not just before it.
        if check_inputs(ROOT, review) or hashlib.sha256((ROOT / REVIEW).read_bytes()).hexdigest() != report['review_sha256']:
            raise RuntimeError('Reviewed inputs changed during validation')
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        print(str(error), file=sys.stderr)
    finally:
        report['elapsed_seconds'] = time.monotonic()-started
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2)+'\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
