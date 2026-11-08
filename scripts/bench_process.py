#!/usr/bin/env python3
"""Durable host process evidence; no bench authority or device access on import.

The supervisor, rather than the agent, records the actual wait() result. Tool
handles are optional correlation data, never the source of a process exit code.
Call verification in the same native process namespace as execution. Child
tools that create separate groups must retain and verify their own journals.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def read(path):
    return json.loads(Path(path).read_text())


def record(path, value):
    """Publish one immutable, fsynced record; never overwrite old evidence."""
    path = Path(path)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def identity(pid):
    path = Path('/proc') / str(pid)
    fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
    return dict(pid=int(pid), ppid=int(fields[1]), pgid=int(fields[2]),
                start=fields[19], state=fields[0],
                boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                pid_namespace=os.readlink('/proc/self/ns/pid'))


def members(pgid):
    rows = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            row = identity(int(path.name))
        except (FileNotFoundError, ProcessLookupError):
            continue
        if row['pgid'] == pgid and row['state'] != 'Z':
            rows.append(row)
    return rows


def verify_child(folder, expected_argv, *, legacy=False):
    """Verify existing parent-written journals without inventing a tool result.

    Legacy mode is an explicit reconciliation of the former child_control
    format. Its records predate namespace fields, so the caller must obtain
    the native host view separately. No process is launched or killed here.
    """
    folder = Path(folder)
    start = read(folder / 'child-started.json')
    terminal = read(folder / 'child-terminal.json')
    if not expected_argv or start['argv'] != list(expected_argv):
        raise ValueError('Child argv differs from the selected operation')
    if type(start['pid']) is not int or start['pid'] <= 1:
        raise ValueError('Invalid child identity')
    if start['pgid'] != start['pid'] or terminal['pid'] != start['pid']:
        raise ValueError('Mismatched child/group terminal identity')
    if start['boot'] != Path('/proc/sys/kernel/random/boot_id').read_text().strip():
        raise ValueError('Different host boot; reconcile the old run explicitly')
    if not legacy and start.get('pid_namespace') != os.readlink('/proc/self/ns/pid'):
        raise ValueError('Different process namespace; use the execution host view')
    if not str(start['start']).isdigit():
        raise ValueError('Missing process start identity')
    if (terminal['returncode'] != 0 or type(terminal['returncode']) is not int
            or terminal.get('timed_out', False) or terminal.get('cancelled', False)):
        raise ValueError('Child did not complete successfully; no success inferred')
    if not (terminal['direct_child_joined'] is True
            and terminal['group_terminal'] is True
            and terminal['live_group_members'] == []):
        raise ValueError('Child or group was not joined')
    if members(start['pgid']):
        raise ValueError('Recorded process group is live')
    return dict(source='parent-written-wait-result', started=str(folder/'child-started.json'),
                terminal=str(folder/'child-terminal.json'), child_pid=start['pid'],
                actual_returncode=terminal['returncode'], all_joined=True,
                legacy_reconciliation=legacy,
                external_tool_exit='not required or inferred')


def block(folder, *, owner, lease, phase, reason, next_action):
    value = dict(epoch=time.time(), state='blocked', owner=owner, lease=lease,
                 phase=phase, reason=reason, next_action=next_action,
                 custody_retained=True, notification_required=True)
    record(Path(folder)/'blocked.json', value)
    print('BENCH BLOCKED: '+reason+'; next action: '+next_action, file=sys.stderr, flush=True)
    return value


def run(argv, folder, seconds, *, grace=3, owner, lease, phase, next_action,
        unattended=False, notify_argv=None):
    """One selected foreground child; durably retain failure before returning."""
    if seconds <= 0 or grace <= 0 or not argv:
        raise ValueError('Positive bounds and an explicit argv are required')
    if unattended and not notify_argv:
        raise ValueError('Unattended work requires a preselected failure notification command')
    if notify_argv is not None and (not isinstance(notify_argv, list) or not notify_argv
            or not all(isinstance(arg, str) and arg for arg in notify_argv)):
        raise ValueError('Notification must be an explicit argv array, never shell text')
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    previous = {}
    cancelled = False
    timed_out = False
    child = None
    result = None
    problem = None

    def interrupted(signum, _frame):
        nonlocal cancelled
        cancelled = True
        raise InterruptedError('Supervisor cancelled by signal '+str(signum))

    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        previous[sig] = signal.signal(sig, interrupted)
    try:
        record(folder/'supervisor-started.json', dict(**identity(os.getpid()),
               epoch=time.time(), owner=owner, lease=lease, phase=phase,
               timeout_seconds=seconds, argv=list(argv), next_action=next_action,
               unattended=unattended, failure_notify_argv=notify_argv))
        with (folder/'output.log').open('xb') as output:
            try:
                child = subprocess.Popen(argv, stdout=output, stderr=subprocess.STDOUT,
                                         start_new_session=True)
                record(folder/'child-started.json', dict(**identity(child.pid), argv=list(argv)))
                result = child.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                problem = 'Original process deadline expired; no replay'
            except BaseException as error:
                problem = repr(error)
            finally:
                # Ignore additional cancellation while joining only our group.
                for sig in previous:
                    signal.signal(sig, signal.SIG_IGN)
                if child is not None:
                    if child.poll() is not None and members(child.pid):
                        problem = 'Child exited with live descendants; group cleanup required'
                    if child.poll() is None or members(child.pid):
                        try:
                            os.killpg(child.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        end = time.monotonic()+grace
                        while time.monotonic() < end and (child.poll() is None or members(child.pid)):
                            time.sleep(.02)
                        if child.poll() is None or members(child.pid):
                            try:
                                os.killpg(child.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                    try:
                        child.wait(timeout=grace)
                    except subprocess.TimeoutExpired:
                        problem = 'Child did not join after kill; retain custody and reconcile'
                    live = members(child.pid)
                    record(folder/'child-terminal.json', dict(pid=child.pid,
                           returncode=child.returncode, direct_child_joined=child.poll() is not None,
                           live_group_members=live, group_terminal=not live,
                           timed_out=timed_out, cancelled=cancelled, epoch=time.time()))
                    if live:
                        problem = 'Owned process group remains live'
        success = child is not None and result == 0 and not problem and not cancelled
        if success:
            try:
                proof = verify_child(folder, argv)
            except Exception as error:
                problem = 'Completion evidence verification failed: '+repr(error)
            else:
                record(folder/'complete.json', dict(epoch=time.time(), state='completed', proof=proof))
                return 0
        block(folder, owner=owner, lease=lease, phase=phase,
              reason=problem or 'Child exit '+str(child.returncode if child else None),
              next_action=next_action)
        if notify_argv:
            notification_status = run(notify_argv, folder/'failure-notification', 15,
                grace=1, owner=owner, lease=lease, phase='failure-notification',
                next_action='Notification failed: use existing mailbox/steering route; retain custody')
            record(folder/'notification-result.json', dict(epoch=time.time(),
                   helper_completed=notification_status == 0,
                   helper_status=notification_status, recipient_read='not inferred',
                   evidence=str(folder/'failure-notification')))
        return 1
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def status(folder):
    """Host status only. A completed process is not a physical bench handback."""
    folder = Path(folder)
    if (folder/'blocked.json').exists():
        value = read(folder/'blocked.json')
        if (folder/'notification-result.json').exists():
            value['notification'] = read(folder/'notification-result.json')
        return value
    start = read(folder/'supervisor-started.json')
    if (folder/'complete.json').exists():
        child = read(folder/'child-started.json')
        try:
            proof = verify_child(folder, child['argv'])
        except (ValueError, OSError, KeyError, TypeError) as error:
            return dict(state='evidence-unverified', reason=str(error),
                        owner=start['owner'], lease=start['lease'],
                        next_action='Inspect original journals in the native execution namespace; do not infer success',
                        physical_release='separate verification required')
        return dict(state='process-completed', physical_release='separate verification required',
                    proof=proof)
    try:
        current = identity(start['pid'])
        alive = all(current[k] == start[k] for k in ('boot', 'start', 'pid_namespace'))
    except (FileNotFoundError, ProcessLookupError):
        alive = False
    return dict(state='running' if alive else 'interrupted-unreconciled',
                owner=start['owner'], lease=start['lease'], phase=start['phase'],
                next_action=start['next_action'], custody_retained=True,
                notification_required=not alive)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    launch = sub.add_parser('run')
    launch.add_argument('--out', required=True, type=Path)
    launch.add_argument('--seconds', required=True, type=float)
    for name in ('owner', 'lease', 'phase', 'next-action'):
        launch.add_argument('--'+name, required=True)
    launch.add_argument('--unattended', action='store_true')
    launch.add_argument('--failure-notify-json', type=Path,
                        help='Pinned existing authorized host-notification argv JSON; no shell')
    launch.add_argument('argv', nargs=argparse.REMAINDER)
    inspect = sub.add_parser('verify')
    inspect.add_argument('--out', required=True, type=Path)
    inspect.add_argument('--argv-json', required=True, type=Path)
    inspect.add_argument('--legacy', action='store_true')
    view = sub.add_parser('status')
    view.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.operation == 'verify':
        print(json.dumps(verify_child(args.out, read(args.argv_json), legacy=args.legacy)))
        return 0
    if args.operation == 'status':
        result = status(args.out)
        print(json.dumps(result, indent=2))
        return 0 if result['state'] in ('running', 'process-completed') else 2
    argv = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
    return run(argv, args.out, args.seconds, owner=args.owner, lease=args.lease,
               phase=args.phase, next_action=args.next_action, unattended=args.unattended,
               notify_argv=read(args.failure_notify_json) if args.failure_notify_json else None)


if __name__ == '__main__':
    sys.exit(main())
