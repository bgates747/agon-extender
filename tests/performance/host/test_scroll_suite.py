"""Offline runner tests: synthetic peer, monotonic clock and genuine CSV parsing.

No network, keyboard, serial, SD card or hardware helper is invoked.
"""
import copy
import fcntl
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('scroll_suite', ROOT/'scripts/run_scroll_suite.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Clock:
    def __init__(self):
        self.now = 0.0
        self.waits = []
        self.early = False

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.waits.append(seconds)
        self.now += seconds/4 if self.early else seconds
        self.early = False


def plan(root):
    package = root/'fixture/package'
    package.mkdir(parents=True)
    (package/'scroll.bin').write_bytes(b'offline dummy executable')
    for i in range(8):
        (package/f'c{i:02d}.vdu').write_bytes(b'offline dummy pattern')
    (package/'scroll.cfg').write_text('320 240 32 600 8 64 1 /agents/extender/results/scroll-test.csv\n')
    manifest = dict(fixture='pattern-scroll-r03', mode=8, width=320, height=240,
                    margin=32, steps=600, colours=64, instrument=1,
                    files={p.name: m.sha(p) for p in package.iterdir()})
    path = root/'fixture/manifest.json'
    path.write_text(json.dumps(manifest))
    return dict(schema=1, ready=True, settle_seconds=1, bench_lock=str(root/'bench.lock'),
        fixtures={'m8': dict(manifest=str(path), sha256=m.sha(path), sd_directory='/extender/scroll-r01')},
        adapter=dict(qualified=True, argv=['unused-simulated-adapter'], inputs={str(path): m.sha(path)}),
        jobs=[dict(id='mb-up-01', target='mb', case='full-up', fixture='m8'),
              dict(id='ext-left-01', target='ext', case='partial-left', fixture='m8')])


class Peer:
    def __init__(self, clock):
        self.clock, self.calls = clock, []
        self.state = dict(fresh=True, route='mb', foreground='cli', cli_visible=True,
            epochs=dict(agon='agon-boot-1', p4='p4-boot-1'), startup_sha256='f'*64,
            modes=dict(mb=dict(number=0, width=640, height=480, colours=16),
                       ext=dict(number=20, width=512, height=384, colours=64)))
        self.fail = self.timeout = self.bad_receipt = self.bad_counts = False
        self.change = None
        self.snapshots = 0

    def call(self, r):
        self.calls.append((r['action'], self.clock.time(), copy.deepcopy(r)))
        action = r['action']
        if action == 'snapshot':
            self.snapshots += 1
        if self.change:
            self.change(self, r)
        reply = {key: r[key] for key in ('schema', 'run_id', 'sequence', 'action')}
        reply['capabilities'] = list(m.CAPABILITIES)
        if action == 'select_route':
            self.state['route'] = r['target']
        elif action == 'select_mode':
            self.state['modes'][r['target']] = copy.deepcopy(r['mode'])
        elif action == 'launch':
            self.state['foreground'] = 'application'
            self.state['cli_visible'] = False
            reply['accepted_job'] = r['job']['id']
        elif action == 'completion':
            if self.timeout:
                raise TimeoutError('simulated missing completion')
            job, f = r['job'], r['fixture']
            self.state.update(foreground='cli', cli_visible=True)
            artifact = Path(r['evidence'])/'result.csv'
            lines = ['case,source,mode,width,height,margin,instrument,updates,mos_ticks,missed_slots,metric,value_us,count_or_crossing']
            for metric in range(1, 13):
                count = f['steps'] if metric in (9, 11) else 256 if metric == 8 else 0
                if self.bad_counts and metric == 9:
                    count -= 1
                row = [job['case'], 0 if job['target'] == 'mb' else 1,
                       f['mode'], f['width'], f['height'], f['margin'], f['instrument'],
                       f['steps'], 1200, 0, metric, 123, count]
                lines.append(','.join(map(str, row)))
            lines += ['SUITE,16777210,14,20', 'FAIL incomplete' if self.fail else 'PASS complete']
            artifact.write_text('\n'.join(lines)+'\n')
            reply.update(job_id=job['id'], result=r['result'], fixture_sha256=f['files']['scroll.bin'],
                config_sha256=f['files']['scroll.cfg'], inputs_verified=True,
                artifact=str(artifact), result_sha256=m.sha(artifact), validated=not self.fail)
            if self.bad_receipt:
                reply['job_id'] = 'another-run'
        elif action == 'notify':
            reply['shown_targets'] = ['mb', 'ext']
        reply['snapshot'] = copy.deepcopy(self.state)
        return reply


class SuiteTests(unittest.TestCase):
    def exercise(self, change=None, expected=0, **flags):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = plan(root)
            clock = Clock()
            peer = Peer(clock)
            for key, value in flags.items():
                setattr(peer, key, value)
            if change:
                change(p, peer, clock)
            initial = copy.deepcopy(peer.state)
            rc = m.Coordinator(p, root/'run', peer, clock.time, clock.sleep).run()
            self.assertEqual(rc, expected)
            summary = json.loads((root/'run/summary.json').read_text())
            return p, peer, clock, summary, initial

    def test_success_restores_both_modes_and_route_and_retains_raw_evidence(self):
        p, peer, clock, summary, initial = self.exercise()
        self.assertEqual(peer.state, initial)
        self.assertTrue(summary['restored'])
        self.assertEqual(summary['state'], 'complete')
        self.assertEqual([r['appliance_mos_ticks'] for r in summary['jobs']], [20, 20])
        self.assertEqual(peer.calls[-1][0], 'notify')
        self.assertNotIn('autoexec', json.dumps([r[2] for r in peer.calls]).lower())
        for index, (action, at, request) in enumerate(peer.calls):
            if action == 'launch':
                last_mode = max(t for a, t, r in peer.calls[:index] if a == 'select_mode')
                self.assertGreaterEqual(at-last_mode, 1)

    def test_matching_mode_skips_switch_and_delay(self):
        def setup(p, peer, clock):
            peer.state['modes']['mb'] = dict(number=8, width=320, height=240, colours=64)
            p['jobs'][1].update(target='mb')
        _, peer, clock, summary, _ = self.exercise(setup)
        self.assertFalse(clock.waits)
        self.assertNotIn('select_mode', [r[0] for r in peer.calls])

    def test_early_sleep_return_still_waits_full_second(self):
        _, peer, clock, _, _ = self.exercise(lambda p, peer, c: setattr(c, 'early', True))
        launch = next(at for action, at, r in peer.calls if action == 'launch')
        self.assertGreaterEqual(launch, 1)
        self.assertGreater(len(clock.waits), 4)

    def test_reset_during_settling_stops_without_launch_cleanup_or_notification(self):
        def setup(p, peer, clock):
            def reset(peer, request):
                if request['action'] == 'snapshot' and peer.snapshots == 2:
                    peer.state['epochs']['agon'] = 'agon-boot-2'
            peer.change = reset
        _, peer, _, summary, _ = self.exercise(setup, expected=1)
        self.assertEqual(peer.calls[-1][0], 'snapshot')
        self.assertNotIn('launch', [r[0] for r in peer.calls])
        self.assertFalse(summary['restored'])

    def test_timeout_does_not_replay_or_type_any_followup_command(self):
        _, peer, _, summary, _ = self.exercise(expected=1, timeout=True)
        self.assertEqual(peer.calls[-1][0], 'completion')
        self.assertEqual(sum(a == 'launch' for a, _, _ in peer.calls), 1)
        self.assertFalse(summary['restored'])
        self.assertEqual(summary['pending']['action'], 'completion')

    def test_wrong_job_receipt_stops_without_cleanup(self):
        _, peer, _, summary, _ = self.exercise(expected=1, bad_receipt=True)
        self.assertEqual(peer.calls[-1][0], 'completion')
        self.assertFalse(summary['restored'])

    def test_actual_csv_counts_override_claimed_pass(self):
        _, peer, _, summary, _ = self.exercise(expected=1, bad_counts=True)
        self.assertEqual(peer.calls[-1][0], 'completion')
        self.assertEqual(summary['jobs'], [])

    def test_known_failed_test_restores_and_reports_failure_without_next_job(self):
        _, peer, _, summary, initial = self.exercise(expected=1, fail=True)
        self.assertEqual(len(summary['jobs']), 1)
        self.assertFalse(summary['jobs'][0]['passed'])
        self.assertEqual(peer.state, initial)
        self.assertEqual(peer.calls[-1][2]['outcome'], 'failed')

    def test_double_buffered_entry_is_gated_before_mutation(self):
        def setup(p, peer, clock):
            peer.state['modes']['ext']['number'] = 149
        _, peer, _, _, _ = self.exercise(setup, expected=1)
        self.assertEqual([r[0] for r in peer.calls], ['snapshot'])

    def test_startup_change_stops_further_commands(self):
        def setup(p, peer, clock):
            def changed(peer, request):
                if request['action'] == 'select_mode':
                    peer.state['startup_sha256'] = 'a'*64
            peer.change = changed
        _, peer, _, _, _ = self.exercise(setup, expected=1)
        self.assertEqual(peer.calls[-1][0], 'select_mode')

    def test_not_ready_plan_never_calls_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);p = plan(root);p['ready'] = False
            peer = Peer(Clock())
            with self.assertRaises(ValueError):
                m.Coordinator(p, root/'run', peer).run()
            self.assertFalse(peer.calls)
            self.assertFalse((root/'run').exists())

    def test_bench_lock_prevents_second_coordinator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);p = plan(root);peer = Peer(Clock())
            with Path(p['bench_lock']).open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaises(BlockingIOError):
                    m.Coordinator(p, root/'run', peer).run()
            self.assertFalse(peer.calls)

    def test_short_settling_delay_is_rejected_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = plan(Path(tmp));p['settle_seconds'] = .99
            with self.assertRaises(ValueError):
                m.validate(p)

    def test_plan_generation_and_check_never_start_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);p = plan(root)
            path = root/'stopped-plan.json'
            manifest = p['fixtures']['m8']['manifest']
            with patch('subprocess.run', side_effect=AssertionError('No adapter or subprocess allowed')):
                with patch('sys.argv', ['runner', '--fixture-manifest', manifest, '--write-plan', str(path)]):
                    self.assertEqual(m.main(), 0)
                generated = json.loads(path.read_text())
                self.assertFalse(generated['ready'])
                self.assertFalse(generated['adapter']['qualified'])
                self.assertEqual(len(generated['jobs']), 16)
                with patch('sys.argv', ['runner', '--plan', str(path), '--check']):
                    self.assertEqual(m.main(), 0)

    def test_keyboard_ready_without_visible_cli_does_not_authorize_launch(self):
        _, peer, _, _, _ = self.exercise(
            lambda p, peer, clock: peer.state.update(cli_visible=False), expected=1)
        self.assertEqual([r[0] for r in peer.calls], ['snapshot'])

    def test_notification_must_preserve_restored_state(self):
        def setup(p, peer, clock):
            def changed(peer, request):
                if request['action'] == 'notify':
                    peer.state['route'] = 'ext'
            peer.change = changed
        _, peer, _, summary, _ = self.exercise(setup, expected=1)
        self.assertEqual(peer.calls[-1][0], 'notify')
        self.assertFalse(summary['restored'])

    def test_changed_manifest_is_rejected_before_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);p = plan(root);peer = Peer(Clock())
            manifest = Path(p['fixtures']['m8']['manifest'])
            manifest.write_text(manifest.read_text()+'\n')
            with self.assertRaises(ValueError):
                m.Coordinator(p, root/'run', peer).run()
            self.assertFalse(peer.calls)


if __name__ == '__main__':
    unittest.main()
