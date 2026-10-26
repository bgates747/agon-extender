#!/usr/bin/env python3
"""Finite local socket control campaign. Does not connect to P4 or Agon.

The test reflector deliberately has no firmware timing model. This campaign
checks source scheduling and instrumentation overhead on the selected host.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

from test_controller_probe import peer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--rates', type=int, nargs='+', default=[60, 120, 240])
    args = parser.parse_args()
    if len(set(args.rates)) != len(args.rates):
        parser.error('Duplicate rates would overwrite run paths')
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic_ns()
    stamp = datetime.now(timezone.utc).isoformat()
    root = Path(__file__).resolve().parents[1]
    results = []
    current = None
    interrupted = False

    def cancel(_sig, _frame):
        nonlocal interrupted
        interrupted = True
        if current is not None:
            current.terminate()

    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)
    for hz in args.rates:
        if interrupted:
            break
        folder = args.output/f'hz{hz}'
        with peer() as (url, state), (args.output/f'hz{hz}.log').open('x') as log:
            current = subprocess.Popen([sys.executable, str(root/'scripts/controller_probe.py'),
                       '--url', url, '--output', str(folder), '--hz', str(hz),
                       '--seconds', str(args.seconds), '--pattern', 'triangle'],
                       stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
            try:
                code = current.wait(timeout=args.seconds+10)
            finally:
                if current.poll() is None:
                    current.terminate()
                    current.wait(timeout=3)
                current = None
            result = json.loads((folder/'summary.json').read_text()) if (folder/'summary.json').exists() else {}
            results.append(dict(hz=hz, exit_code=code, reflected=len(state['received']), summary=result))
    final = dict(scope='Oryx/Linux loopback control only; no P4 timing model or end-to-end latency',
                 started_utc=stamp, finished_utc=datetime.now(timezone.utc).isoformat(),
                 elapsed_seconds=(time.monotonic_ns()-started)/1e9,
                 interrupted=interrupted, results=results)
    (args.output/'campaign.json').write_text(json.dumps(final, indent=2)+'\n')
    print(json.dumps(final, indent=2), flush=True)
    return 0 if not interrupted and all(r['exit_code'] == 0 for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
