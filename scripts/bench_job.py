#!/usr/bin/env python3
"""Launch a detached bench command; review result.json later, without polling.

Uses argv directly, never a shell. Does not retry, reset or infer device success.
The wrapped command must verify its operation before returning zero. Job folders
must be fresh and should be ignored machine-local paths. A missing terminal
result after host loss is unknown, never success.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def worker(folder):
    spec = json.loads((folder / 'request.json').read_text())
    result = dict(started_at=stamp(), status='running', pid=os.getpid())
    save(folder / 'result.json', result)
    start = time.monotonic()
    try:
        code = subprocess.call(spec['argv'], cwd=spec['cwd'], stdin=subprocess.DEVNULL)
        result.update(exit_code=code, status='success' if code == 0 else 'failure')
    except BaseException:
        traceback.print_exc()
        result.update(exit_code=None, status='failure')
    result.update(ended_at=stamp(), elapsed_seconds=time.monotonic() - start)
    save(folder / 'result.json', result)
    print(json.dumps(result), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    folder = args.output.resolve()
    if args.worker:
        worker(folder)
        return
    command = args.command
    if command[:1] == ['--']:
        command = command[1:]
    if not command:
        parser.error('provide command after --')
    folder.mkdir(parents=True, exist_ok=False)
    save(folder / 'request.json', dict(argv=command, cwd=str(Path.cwd()), submitted_at=stamp()))
    with (folder / 'output.log').open('xb') as log:
        proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                                 '--worker', '--output', str(folder)],
                                stdin=subprocess.DEVNULL, stdout=log,
                                stderr=subprocess.STDOUT, start_new_session=True,
                                close_fds=True)
    save(folder / 'launch.json', dict(pid=proc.pid, launched_at=stamp()))
    print(f'Launched PID {proc.pid}. Review {folder / "result.json"} later; no monitoring started.')


if __name__ == '__main__':
    main()
