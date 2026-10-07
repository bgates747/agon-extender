#!/usr/bin/env python3
"""Collect deferred benchmark checkpoints from an explicitly mounted Agon SD.

This tool never contacts either board, writes to the card or selects a mount.
Closed windows are preparation evidence until the raw records pass validation.
Existing local raw files must match; conflicting evidence is never overwritten.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/performance/render_load'))
from codec import decode
from generate import MODES


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def card_path(root, remote):
    parts = PurePosixPath(remote)
    if not parts.is_absolute() or '..' in parts.parts:
        raise ValueError('Invalid recorded SD path')
    path = root.joinpath(*parts.parts[1:]).resolve()
    if not path.is_relative_to(root):
        raise ValueError('SD path escapes the supplied card root')
    return path


def preserve(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Existing evidence differs: ' + str(path))
    else:
        with path.open('xb') as output:
            output.write(data)


def check_identity(meta, result):
    geometry = MODES[meta['mode']]
    expected = (meta['mode'], meta['tag'], *geometry[:3])
    actual = (result['mode'], result['tag'], result['width'], result['height'], result['colours'])
    if actual != expected or result['build_id'] != meta['fixture']['build_id']:
        raise ValueError('Raw mode/tag/geometry/fixture identity differs')


def validate(meta, raw, telemetry, failure=None):
    result = decode(raw)
    check_identity(meta, result)
    if [case['id'] for case in result['cases']] != list(range(meta['first'], meta['end'])):
        raise ValueError('Missing, extra or reordered case checkpoints')
    if failure is not None:
        header = decode(failure)
        if len(failure) != 128 or any(header[k] != result[k] for k in
                                      ('mode', 'tag', 'width', 'height', 'colours', 'build_id')):
            raise ValueError('Invalid failure receipt identity')
    bad = sum(frame['status'] != 0 for case in result['cases'] for frame in case['frames'])
    short = [case['id'] for case in result['cases'] if len(case['frames']) < 64]
    truncated = [case['id'] for case in result['cases'] if case['truncated']]
    errors = [case['id'] for case in result['cases'] if case['error']]
    if meta['endpoint'] == 'p4' and meta.get('telemetry_required', True):
        if telemetry is None or telemetry['overflow'] or telemetry['open'] or telemetry['output'] != meta['variant']:
            raise ValueError('Missing, overflowing, open or mismatched P4 telemetry')
        windows = [window for window in telemetry['windows'] if window['tag'] == meta['tag']]
        if [window['id'] for window in windows] != list(range(meta['first'], meta['end'])):
            raise ValueError('P4 window selection/order differs')
        for case, window in zip(result['cases'], windows):
            if window['end_us'] <= window['start_us'] or window['flags'] != case['flags']:
                raise ValueError('Unclosed or uncorrelated P4 window')
    outcome = 'fail' if failure is not None or errors else 'partial' if bad or short or truncated else 'pass'
    fields = dict(outcome=outcome, returned_cases=len(result['cases']), bad_frames=bad,
                  short_cases=short, truncated_cases=truncated, error_cases=errors,
                  result_sha256=digest(raw))
    if failure is not None:
        fields.update(failure_code=failure[19], failure_sha256=digest(failure))
    return result, fields


def collect(root, evidence, receipt_path):
    root = root.resolve(strict=True)
    if not root.is_dir() or not (root / 'autoexec.txt').is_file():
        raise ValueError('Supply the mounted Agon card root containing autoexec.txt')
    if receipt_path.exists():
        raise ValueError('Preserve the existing collection receipt; choose a fresh path')
    receipt = dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   source_sha256=digest(Path(__file__).read_bytes()), outcome='running', runs=[])
    write(receipt_path, receipt)
    for folder in sorted(evidence.glob('BENCH-009-*')):
        path = folder / 'run.json'
        if not path.exists():
            continue
        meta = json.loads(path.read_text())
        deferred_failure = meta.get('outcome') == 'fail' and meta.get('result_retrieval') == 'deferred-sd-mount'
        if meta.get('outcome') != 'measured-awaiting-local-results' and not deferred_failure:
            continue
        original = path.read_bytes()
        entry = dict(run=folder.name, outcome='invalid')
        started = time.monotonic()
        try:
            for name, field in [('plan.bin', 'plan_sha256'), ('startup.txt', 'startup_sha256')]:
                if digest((folder / name).read_bytes()) != meta[field]:
                    raise ValueError('Retained invocation hash differs: ' + name)
            raw = None
            if 'results.bin' in meta['sd_files']:
                raw = card_path(root, meta['sd_results_path']).read_bytes()
                if len(raw) != meta['sd_files']['results.bin']['bytes']:
                    raise ValueError('SD result size differs from completed-run STAT')
            failure = None
            if 'failure.bin' in meta['sd_files']:
                failure = card_path(root, meta['sd_failure_path']).read_bytes()
                if len(failure) != meta['sd_files']['failure.bin']['bytes']:
                    raise ValueError('SD failure size differs from completed-run STAT')
            telemetry_path = folder / 'telemetry.json'
            telemetry = json.loads(telemetry_path.read_text()) if telemetry_path.exists() else None
            suffix = meta.get('recovery_result_suffix', '') if deferred_failure else ''
            if raw is not None:
                preserve(folder / ('results' + suffix + '.bin'), raw)
            if failure is not None:
                preserve(folder / ('failure' + suffix + '.bin'), failure)
            if deferred_failure:
                # The recovery invocation can share the original tag/plan. Its
                # records never qualify the interrupted measurement, regardless
                # of frame counts or the newer diagnostic window's success.
                fields = dict(outcome='fail', collection_scope='Retained failed or recovery-only records; excluded from performance comparison')
                if raw is not None:
                    result = decode(raw)
                    check_identity(meta, result)
                    preserve(folder / ('decoded' + suffix + '.json'), (json.dumps(result, indent=2) + '\n').encode())
                    fields['retained_result_sha256'] = digest(raw)
                if failure is not None:
                    check_identity(meta, decode(failure))
                    if len(failure) != 128:
                        raise ValueError('Invalid failure receipt size')
                    fields.update(failure_code=failure[19], failure_sha256=digest(failure))
                if raw is None and failure is None:
                    raise ValueError('No recorded result or failure file')
            elif raw is not None:
                result, fields = validate(meta, raw, telemetry, failure)
                preserve(folder / 'decoded.json', (json.dumps(result, indent=2) + '\n').encode())
            elif failure is not None:
                check_identity(meta, decode(failure))
                if len(failure) != 128:
                    raise ValueError('Invalid failure receipt size')
                fields = dict(outcome='fail', returned_cases=0, failure_code=failure[19],
                              failure_sha256=digest(failure))
            else:
                raise ValueError('No recorded result or failure file')
            # Preserve the terminal deferred receipt before appending collection
            # validation. Do not replace an operator-interrupted or failed run.
            preserve(folder / 'run-before-local-collection.json', original)
            meta.update(fields, retrieval_seconds=time.monotonic() - started,
                        result_retrieval='local-sd-mount', local_collection_receipt=str(receipt_path),
                        collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
            meta.pop('validation_pending', None)
            write(path, meta)
            entry.update(fields, bytes=len(raw) if raw is not None else 0, seconds=meta['retrieval_seconds'])
        except Exception as error:
            entry['failure'] = repr(error)
            # Leave the deferred receipt pending and retain any copied bytes.
            # A collection error cannot turn missing/corrupt data into a pass.
        receipt['runs'].append(entry)
        write(receipt_path, receipt)
    receipt.update(outcome='pass' if receipt['runs'] and all(r['outcome'] == 'pass' for r in receipt['runs']) else 'partial',
                   finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    write(receipt_path, receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sd-root', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    receipt = collect(args.sd_root, args.evidence, args.receipt)
    print(json.dumps(dict(outcome=receipt['outcome'], runs=len(receipt['runs']))))
    return 0 if receipt['outcome'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
