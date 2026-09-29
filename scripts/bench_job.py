#!/usr/bin/env python3
"""Launch a detached bench command; review result.json later, without polling.

Uses argv directly, never a shell. Does not retry, reset or infer device success.
The wrapped command must verify its operation before returning zero. Job folders
must be fresh and should be ignored machine-local paths. A missing terminal
result after host loss is unknown, never success.

An optional JSON hook file may provide ``success`` and ``failure`` argv arrays.
The selected hook runs after the wrapped command terminates. A hardware failure
hook must restore the test driver's durable failure identity after any alert
player output so the alert cannot become the final visible result. The hook is
a notification/visibility adapter, not the authority for the verdict.
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


def read_hooks(path):
    if path is None:
        return {}
    document = json.loads(path.read_text())
    if not isinstance(document, dict):
        raise ValueError('terminal hook file must contain an object')
    unknown = set(document) - {'success', 'failure'}
    if unknown:
        raise ValueError(f'unknown terminal hook keys: {sorted(unknown)}')
    for name, command in document.items():
        if (not isinstance(command, list) or not command or
                not all(isinstance(item, str) and item for item in command)):
            raise ValueError(f'{name} hook must be a nonempty argv string array')
    return document


def worker(folder):
    spec = json.loads((folder / 'request.json').read_text())
    result = dict(started_at=stamp(), status='running', pid=os.getpid())
    save(folder / 'result.json', result)
    start = time.monotonic()
    command_code = None
    command_started = time.monotonic()
    try:
        command_code = subprocess.call(
            spec['argv'], cwd=spec['cwd'], stdin=subprocess.DEVNULL)
        result.update(command_exit_code=command_code,
                      command_status='success' if command_code == 0 else 'failure')
    except BaseException:
        traceback.print_exc()
        result.update(command_exit_code=None, command_status='failure')
    result['command_elapsed_seconds'] = time.monotonic() - command_started
    hook_name = 'success' if command_code == 0 else 'failure'
    hook_code = None
    hook_elapsed = None
    hook = spec.get('terminal_hooks', {}).get(hook_name)
    if hook:
        hook_started = time.monotonic()
        try:
            hook_code = subprocess.call(
                hook, cwd=spec['cwd'], stdin=subprocess.DEVNULL)
        except BaseException:
            traceback.print_exc()
        hook_elapsed = time.monotonic() - hook_started
    status = 'success' if command_code == 0 and (hook is None or hook_code == 0) else 'failure'
    result.update(exit_code=command_code, status=status,
                  terminal_hook=hook_name if hook else None,
                  terminal_hook_exit_code=hook_code,
                  terminal_hook_elapsed_seconds=hook_elapsed,
                  ended_at=stamp(), elapsed_seconds=time.monotonic() - start)
    save(folder / 'result.json', result)
    print(json.dumps(result), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--terminal-hooks', type=Path,
                        help='JSON object containing success/failure argv arrays')
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
    try:
        hooks = read_hooks(args.terminal_hooks)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    save(folder / 'request.json', dict(argv=command, cwd=str(Path.cwd()),
                                       submitted_at=stamp(), terminal_hooks=hooks))
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
