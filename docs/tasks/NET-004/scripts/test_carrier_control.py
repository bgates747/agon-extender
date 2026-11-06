"""Device-free admission contract checks; never open USB or use live registry."""
import copy
import unittest
from carrier_control import validate_binding, TASK, FIXTURES, UNFILTERED_P4, FILTERED_P4, PARALLEL_EMOS


class Admission(unittest.TestCase):
    def setUp(self):
        self.grant = dict(owner='linux-extender', task=TASK, generation=57,
                          request='fresh-request', lease='a' * 32)
        self.context = dict(self.grant, operator='linux-extender', central_owner='linux-extender',
                            components=dict(p4_app_sha256=UNFILTERED_P4, emos_rom_sha256=PARALLEL_EMOS),
                            source_pins_sha256='b' * 64)
        self.prepared = dict(schema='extender-carrier-control-prepared-v1', case='plain', carrier='parallel',
            full_fixture_readback_match=True, installed_components=copy.deepcopy(self.context['components']),
            actual_cli=True, callback_zero=True, legacy_zero=True, entry_mode=0,
            source_pins_sha256='b' * 64, fixture_sha256=FIXTURES['plain'],
            fixture_remote='/extender/network/independent-r01/plain.bin',
            result_remote='/agents/extender/results/independent-r01/plain.txt')

    def reject(self, context=None, grant=None, prepared=None):
        with self.assertRaises(RuntimeError):
            validate_binding(context or self.context, grant or self.grant, prepared or self.prepared)

    def test_baseline_accepts_only_its_exact_case(self):
        validate_binding(self.context, self.grant, self.prepared)
        wrong = dict(self.prepared, fixture_sha256=FIXTURES['graphics'])
        self.reject(prepared=wrong)

    def test_operator_transfer_and_release_revoke_control(self):
        for change in (dict(operator='mechagon'), dict(released=True), dict(pending_commands=True)):
            self.reject(context=dict(self.context, **change))
        self.reject(grant=dict(self.grant, task='RENDER-001'))
        self.reject(grant=dict(self.grant, generation=56))
        self.reject(context=dict(self.context, lease='c' * 32))

    def test_uart_pair_cannot_be_mislabelled_as_parallel(self):
        wrong = copy.deepcopy(self.context)
        wrong['components']['p4_app_sha256'] = 'd' * 64
        candidate = dict(self.prepared, installed_components=wrong['components'])
        self.reject(context=wrong, prepared=candidate)
        self.reject(prepared=dict(self.prepared, carrier='uart'))

    def test_unverified_or_unclean_stage_refuses(self):
        for key in ('full_fixture_readback_match', 'actual_cli', 'callback_zero', 'legacy_zero'):
            self.reject(prepared=dict(self.prepared, **{key: False}))
        self.reject(prepared=dict(self.prepared, source_pins_sha256='e' * 64))
        self.reject(prepared=dict(self.prepared, entry_mode=20))

    def test_sd_namespace_and_traversal_refuse(self):
        self.reject(prepared=dict(self.prepared, result_remote='/progress.log'))
        self.reject(prepared=dict(self.prepared, fixture_remote='/extender/network/independent-r01/../old.bin'))

    def test_filtered_case_requires_exact_candidate_and_retirement(self):
        context = copy.deepcopy(self.context)
        context['components']['p4_app_sha256'] = FILTERED_P4
        prepared = dict(self.prepared, case='filtered-graphics', fixture_sha256=FIXTURES['graphics'],
                        installed_components=context['components'])
        self.reject(context=context, prepared=prepared)
        prepared['unfiltered_failure_retired'] = True
        validate_binding(context, self.grant, prepared)
        self.reject(prepared=prepared)

# Exercise the actual parent dispatch and retirement path with isolated fake
# serial/keyboard/echo actors. No live device, network socket or lease helper.
import hashlib
import json
from pathlib import Path
import queue
import tempfile
import time
from unittest.mock import patch
import carrier_control as parent


class ParentRetirement(unittest.TestCase):
    def exercise(self, terminal):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            fixture = base / 'fixture.bin'
            fixture.write_bytes(b'isolated fixture')
            digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
            pins = base / 'pins.json'
            pins.write_text(json.dumps({'inputs': {str(fixture): dict(bytes=16, sha256=digest)}}))
            grant = dict(owner='linux-extender', task=TASK, generation=57, request='fresh', lease='a' * 32)
            grantpath = base / 'grant.json'
            grantpath.write_text(json.dumps(grant))
            context = dict(grant, grant=str(grantpath), operator='linux-extender', central_owner='linux-extender',
                components=dict(p4_app_sha256=UNFILTERED_P4, emos_rom_sha256=PARALLEL_EMOS),
                source_pins=str(pins), source_pins_sha256=hashlib.sha256(pins.read_bytes()).hexdigest(),
                url='http://isolated.invalid', ports=['isolated-main', 'isolated-p4'], echo_bind='127.0.0.1')
            prepared = dict(schema='extender-carrier-control-prepared-v1', case='plain', carrier='parallel',
                full_fixture_readback_match=True, installed_components=context['components'], actual_cli=True,
                callback_zero=True, legacy_zero=True, entry_mode=0, source_pins_sha256=context['source_pins_sha256'],
                fixture_local=str(fixture), fixture_sha256=digest,
                fixture_remote='/extender/network/independent-test/plain.bin',
                result_remote='/agents/extender/results/independent-test/plain.txt')
            cp, pp = base / 'context.json', base / 'prepared.json'
            cp.write_text(json.dumps(context)); pp.write_text(json.dumps(prepared))
            samples = queue.Queue()
            commands, actors, opened = [], [], []

            class Serial:
                def __init__(self, name): self.main = name == 'isolated-main'; self.closed = False
                def __enter__(self): opened.append(self); return self
                def __exit__(self, *_): self.closed = True
                def read(self, _):
                    if self.main:
                        try: return samples.get(timeout=.002)
                        except queue.Empty: return b''
                    time.sleep(.002)
                    return b''

            class Keyboard:
                def __init__(self, *_): self.command = ''; self.state = {}; self.lock = self
                def close(self): pass
                def status(self): return dict(ready=True, physical_neutral=True, held=0, pending=0, locale=1, caps=False)
                def open(self, _): pass
                def cancel(self): pass
                def send(self, events):
                    if len(events) == 1:
                        self.command += chr(events[0][0]); return
                    commands.append(self.command)
                    if self.command.startswith('VDU ') and self.command != 'VDU 2':
                        samples.put(b'Extender independent carrier observer\r\n/ *')
                    elif self.command.startswith('LOAD '): samples.put(b'\r\n/ *')
                    elif self.command.startswith('RUN ') and terminal:
                        samples.put(b'Network echo probe PASS\r\n/ *')

            class Peer:
                def __init__(self, argv, **kwargs):
                    self.returncode = None; self.terminated = False; actors.append(self)
                    out = Path(argv[argv.index('--output') + 1]); out.mkdir()
                    (out / 'run.json').write_text(json.dumps(dict(passed=True, records=[dict(bytes=n) for n in parent.SIZES])))
                    kwargs['stdout'].write('Ready: one client\n'); kwargs['stdout'].flush()
                def poll(self): return self.returncode
                def wait(self, timeout=None):
                    if self.returncode is None: self.returncode = 0
                    return self.returncode
                def terminate(self): self.terminated = True; self.returncode = -15
                def kill(self): self.terminated = True; self.returncode = -9

            class Socket:
                def __enter__(self): return self
                def __exit__(self, *_): pass
                def bind(self, _): pass

            def command(argv, **kwargs):
                return type('Result', (), dict(returncode=1 if argv[0] == 'fuser' else 0))()

            clock = [0]
            def monotonic(): clock[0] += 2; return clock[0]
            out = base / 'output'
            with patch.object(parent, 'FIXTURES', dict(parent.FIXTURES, plain=digest)), \
                 patch.object(parent, 'Keyboard', Keyboard), \
                 patch.object(parent, 'text_events', lambda char, *_: [(ord(char), 1)]), \
                 patch.object(parent, 'open_passive_serial', lambda name, **kwargs: Serial(name)), \
                 patch.object(parent.subprocess, 'run', command), \
                 patch.object(parent.subprocess, 'Popen', Peer), \
                 patch.object(parent.socket, 'socket', Socket), \
                 patch.object(parent.time, 'monotonic', monotonic):
                if terminal: parent.run(cp, pp, out)
                else:
                    with self.assertRaises(TimeoutError): parent.run(cp, pp, out)
            receipt = json.loads((out / 'actors.json').read_text())
            self.assertEqual(sum(command.startswith('RUN ') for command in commands), 1)
            self.assertTrue(receipt['serial_readers_joined'])
            self.assertTrue(receipt['peer_joined'])
            self.assertTrue(all(serial.closed for serial in opened))
            self.assertEqual(receipt['passed'], terminal)
            self.assertEqual(receipt['actual_native_cli'], terminal)
            self.assertEqual(receipt['preserve_RAM_before_LOAD'], not terminal)
            self.assertEqual(actors[0].terminated, not terminal)

    def test_actual_parent_pass_is_one_dispatch_and_joins(self): self.exercise(True)
    def test_actual_parent_timeout_joins_without_replay(self): self.exercise(False)


if __name__ == '__main__':
    unittest.main()
