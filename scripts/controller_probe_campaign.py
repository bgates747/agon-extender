#!/usr/bin/env python3
"""Finite rate comparison using the same individual deterministic source.

No resets, firmware changes, Agon input, retries, takeover or automatic resume.
A failed/partial/cancelled case stops further dispatch. Output is a NEW directory.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import signal
import time

from controller_probe import run, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--rates', type=int, nargs='+', default=[60, 120, 240])
    parser.add_argument('--seconds', type=float, default=30, help='Per rate, excluding admission/close')
    parser.add_argument('--timeout-ms', type=int, default=250)
    parser.add_argument('--pattern', choices=('step', 'triangle'), default='triangle')
    args = parser.parse_args()
    if not args.rates or len(set(args.rates)) != len(args.rates):
        parser.error('Rates must be nonempty and unique')
    args.output.mkdir(parents=True, exist_ok=False)
    stamp = datetime.now(timezone.utc).isoformat()
    start = time.monotonic_ns()
    stopped = False

    def cancel(_sig, _frame):
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)
    results = []
    error = None
    try:
        for hz in args.rates:
            if stopped:
                break
            result = run(args.url, args.output/f'hz{hz}', hz=hz, seconds=args.seconds,
                         timeout_ms=args.timeout_ms, name=args.pattern, stop=lambda: stopped)
            results.append(dict(hz=hz, summary=result))
            print(json.dumps(dict(hz=hz, **result)), flush=True)
            if result['outcome'] != 'pass':
                break
    except (OSError, ValueError) as exc:
        error = str(exc)
    outcome = ('fail' if error or any(r['summary']['outcome'] == 'fail' for r in results)
               else 'aborted' if stopped else 'partial' if len(results) != len(args.rates) or
               any(r['summary']['outcome'] != 'pass' for r in results) else 'pass')
    final = dict(started_utc=stamp, finished_utc=datetime.now(timezone.utc).isoformat(),
                 elapsed_seconds=(time.monotonic_ns()-start)/1e9,
                 outcome=outcome, error=error, requested_rates=args.rates,
                 seconds_per_case=args.seconds, timeout_ms=args.timeout_ms,
                 scope='Host scheduling / P4 ACK only; no EMOS consumption or visible output',
                 results=results)
    write_json(args.output/'campaign.json', final)
    print(json.dumps(final, indent=2), flush=True)
    return 0 if outcome == 'pass' else 130 if outcome == 'aborted' else 1


if __name__ == '__main__':
    raise SystemExit(main())
