#!/usr/bin/env python3
"""Source-pinned owner adapter for one explicitly armed physical invocation.

No board access while waiting. The reviewed local arm descriptor selects every
path, identity and invocation argv; a peer marker cannot supply a command.
Arming still requires actual owner authorization/custody. This tool neither
grants resources nor changes startup/firmware, resets, reconnects or retries.
NET-003/PHYSICAL.md owns its experimental scope; not a production runner.
"""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

from conditional_go import (accepted_delivery, read_json, record, require_fields,
                            validate_window, wait_once)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''): result.update(block)
    return result.hexdigest()


def assert_owner(command):
    # These are source-selected host lease helpers, not target-access commands.
    result = subprocess.run(command, capture_output=True, text=True, timeout=3,
                            check=True)
    return json.loads(result.stdout)


def published_go(path, marker, owner, recipient):
    with Path(path).open('rb') as stream: raw = stream.read(16385)
    if len(raw) > 16384: raise ValueError('Durable GO exceeds 16KiB')
    pre, header, body = raw.decode().split('---\n', 2)
    if pre: raise ValueError('Malformed durable GO')
    meta = dict((key, json.loads(value)) for key, value in
                (line.split(': ', 1) for line in header.splitlines()))
    require_fields(meta, dict(author=owner, recipient=recipient, status='published',
        message_id=marker['durable_message_id']), 'Durable GO')
    core = {key: value for key, value in marker.items() if key not in
            ('durable_message_id', 'accepted_start_delivery_id', 'accepted_delivery_id')}
    require_fields(json.loads(body), dict(conditional_go=core), 'Published conditional GO')


def latest_heartbeat(path):
    # Read only the tail of the existing bounded guard trace, never resample or
    # restamp it. The sender waits until both required processes appear there.
    with Path(path).open('rb') as stream:
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(max(0, size - 16384))
        lines = stream.read(16384).splitlines()
    # A concurrent final write may be incomplete. Select the last complete JSON
    # line; its original timestamp must still meet the freshness check.
    for line in reversed(lines):
        try: value = json.loads(line)
        except (ValueError, UnicodeError): continue
        if isinstance(value, dict): return value
    raise ValueError('No complete guard heartbeat')


def check_process(pid, expected_ticks, command_term, unit, *, proc_root=Path('/proc')):
    if type(pid) is not int or pid <= 0: raise ValueError('Invalid producer PID')
    root = proc_root/str(pid)
    if root.stat().st_uid != os.getuid(): raise ValueError('Producer has different owner')
    stat = (root/'stat').read_text().rsplit(') ', 1)[1].split()
    if stat[0] in ('Z', 'X') or int(stat[19]) != expected_ticks:
        raise ValueError('Producer stopped or PID identity changed')
    if command_term.encode() not in (root/'cmdline').read_bytes().split(b'\0'):
        raise ValueError('Producer command differs')
    groups = (root/'cgroup').read_text().splitlines()
    if not any(line.startswith('0::') and line.endswith('/'+unit) for line in groups):
        raise ValueError('Producer left selected qualification unit')


def plan_inputs(arm):
    if digest(arm['plan_path']) != arm['plan_sha256']:
        raise ValueError('Selected plan changed')
    plan = read_json(arm['plan_path'], limit=131072)
    require_fields(plan, dict(schema='mechagon-qualification-plan-v1', executable=True),
                   'Executable owner-selected plan')
    for path, expected in plan['input_sha256'].items():
        if digest(path) != expected: raise ValueError('Pinned input changed: '+path)
    for path, expected in arm['required_sources'].items():
        if plan['input_sha256'].get(path) != expected or digest(path) != expected:
            raise ValueError('Owner source is not pinned by selected plan: '+path)
    for key in ('loaded_receipt', 'graphics_receipt'):
        if arm[key] not in plan['input_sha256']:
            raise ValueError('Owner baseline is not pinned by selected plan: '+key)
    require_fields(plan, dict(ready_file=arm['expected']['ready_path']), 'Plan')
    require_fields(plan['native'], dict(sha256=arm['expected']['native_sha256'],
        arguments=arm['expected']['native_arguments']), 'Native selection')
    require_fields(plan['native_go'], arm['paths'], 'Relay paths')
    return plan


def validate(arm, marker):
    require_fields(marker, arm['expected'], 'Selected GO')
    require_fields(marker, {key: value for key, value in arm['paths'].items()
                            if key != 'marker_path'}, 'Selected evidence paths')
    if not re.fullmatch(r'[a-f0-9]{32}', marker['lease']):
        raise ValueError('Invalid actual Pi token')
    plan = plan_inputs(arm)
    pi = assert_owner(arm['pi_assert_prefix'] + ['--lease', marker['lease']])
    require_fields(pi, dict(owner=marker['owner'], request=marker['request'],
        lease=marker['lease'], generation=marker['generation'], workload='test',
        plan=arm['plan_path']), 'Actual Pi admission')
    age = time.time() - datetime.fromisoformat(pi['granted']).timestamp()
    if not 0 <= age < 120: raise ValueError('Insufficient original whole-Pi budget')
    bench = assert_owner(arm['bench_assert_argv'])
    require_fields(bench, marker['bench'], 'Actual bench admission')
    for label, target, identity in (
            ('start', arm['manager_thread'], marker['accepted_start_delivery_id']),
            ('go', arm['receiver_thread'], marker['accepted_delivery_id'])):
        expected_id = (arm['start_delivery_prefix'] if label == 'start' else
                       arm['go_delivery_prefix']) + marker['lease']
        if identity != expected_id: raise ValueError('Delivery ID differs')
        message = Path(arm['paths'][label+'_message_path']).read_bytes()
        if len(message) > 8192: raise ValueError('Notification exceeds 8KiB')
        accepted_delivery(read_json(arm['paths'][label+'_delivery_path']), message,
            source=arm['source_thread'], target=target, delivery_id=expected_id)
        if label == 'go' and marker['durable_message_id'].encode() not in message:
            raise ValueError('GO alert does not bind the published mail')
    mid = marker['durable_message_id']
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,200}', mid): raise ValueError('Invalid mail ID')
    published_go(Path(arm['mailbox'])/(mid+'.md'), marker,
                 arm['expected']['owner'], arm['receiver_mailbox'])
    ready = read_json(arm['expected']['ready_path'])
    # Ready may precede the guard's first one-second sample containing the two
    # producers. Observe that SAME trace for at most two seconds; this is not a
    # retry of GO or any target operation. The original deadline still governs.
    observe_until = time.monotonic()+2
    while True:
        heartbeat = latest_heartbeat(arm['paths']['guard_heartbeat_path'])
        if all(str(marker[label+'_pid']) in heartbeat['processes']
               for label in ('bridge', 'controller')): break
        if time.monotonic() >= observe_until:
            raise ValueError('Required producer absent from guard evidence')
        time.sleep(0.05)
    if not (0 <= time.time()-heartbeat['epoch'] <= 3 and
            0 <= time.monotonic()-heartbeat['monotonic'] <= 3):
        raise ValueError('Guard heartbeat stale')
    for label in ('bridge', 'controller'):
        pid, ticks = marker[label+'_pid'], marker[label+'_start_ticks']
        if heartbeat['processes'].get(str(pid), {}).get('start_ticks') != ticks:
            raise ValueError('Producer not in current guard evidence')
        check_process(pid, ticks, arm['process_terms'][label], plan['unit'])
    loaded = read_json(arm['loaded_receipt'])
    require_fields(loaded, dict(native_loaded_not_invoked=True, actual_cli=True),
                   'Retained loaded state')
    graphics = read_json(arm['graphics_receipt'])
    require_fields(graphics, dict(exclusive_whole_sprite_engine=True,
        incoming_global_active_count=0, incoming_slot_hardware=False,
        incoming_slots_no_frames=True, no_competing_feature_writer=True,
        logical_coordinates=True, cursor_enabled=True, cursor_flashing=True),
        'Retained graphics baseline')
    require_fields(graphics, arm['graphics_expected'], 'Owned graphics resources')
    validate_window(marker, ready)  # Last, after every potentially slow check.
    return dict(epoch=time.time(), request=marker['request'], lease=marker['lease'],
                plan_sha256=arm['plan_sha256'], registration_deadline_monotonic_ns=
                ready['registration_deadline_monotonic_ns'], bench_generation=bench['generation'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arm', type=Path, required=True)
    parser.add_argument('--arm-sha256', required=True)
    args = parser.parse_args()
    if os.geteuid() == 0: parser.error('Receiver is not a root target-access route')
    if digest(args.arm) != args.arm_sha256: parser.error('Owner arm descriptor changed')
    arm = read_json(args.arm)
    require_fields(arm, dict(schema='bench-conditional-go-arm-v1', wait_seconds=180),
                   'Explicit owner arm')
    plan_inputs(arm)  # Source/files only; no target or process launched.
    bench = assert_owner(arm['bench_assert_argv'])
    require_fields(bench, arm['expected']['bench'], 'Arm bench custody')
    if Path(arm['go_record']).exists(): parser.error('Native GO already recorded; no rearm')
    cancelled, invoking = [False], [False]
    def cancel(_signal, _frame):
        cancelled[0] = True
        if invoking[0]: raise KeyboardInterrupt('Owner receiver interrupted during invocation')
    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)

    def invoke(marker):
        # The source-selected leaf alone has target access. Its fresh record
        # binds this exact validated marker; marker text never supplies argv.
        invoking[0] = True
        validate_window(marker, read_json(arm['expected']['ready_path']))
        record(arm['go_record'], dict(explicit_go=True, request=marker['request'],
            pi_lease=marker['lease'], plan_path=arm['plan_path'],
            plan_sha256=arm['plan_sha256'], ready_path=arm['expected']['ready_path'],
            conditional_marker=marker))
        with (Path(arm['output'])/'invocation.log').open('xb') as log:
            result = subprocess.run(arm['invocation_argv'], stdout=log,
                stderr=subprocess.STDOUT, timeout=280)
        if result.returncode: raise RuntimeError('Owned invocation leaf failed; no replay')
        return dict(exit_code=0, evidence=arm['invocation_receipt'])

    wait_once(arm['paths']['marker_path'], arm['output'], arm['wait_seconds'],
              lambda marker: validate(arm, marker), invoke,
              cancelled=lambda: cancelled[0])


if __name__ == '__main__': main()
