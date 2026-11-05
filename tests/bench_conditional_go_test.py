"""Real owner validator with local evidence and injected lease/process observers.

No real scheduler, /proc observation, serial, HTTP or invocation in these checks.
"""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import bench_conditional_go as receiver


class OwnerEvidenceTests(unittest.TestCase):
    def write(self, path, value):
        path.write_text(json.dumps(value))
        return str(path)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        epoch, mono = time.time(), time.monotonic_ns()
        self.bench = dict(owner='linux-extender', request='physical', generation=36, lease='b'*32)
        self.paths = {key: str(self.root/key) for key in (
            'marker_path', 'guard_heartbeat_path', 'start_message_path',
            'start_delivery_path', 'go_message_path', 'go_delivery_path')}
        self.ready = dict(epoch=epoch, monotonic_ns=mono, bridge_pid=10,
            controller_pid=11, registration_deadline_monotonic_ns=mono+80_000_000_000)
        self.arm = dict(expected=dict(schema='mechagon-native-go-v1', owner='mechagon',
            request='fresh', plan_path=str(self.root/'plan.json'), plan_sha256='selected',
            bench=self.bench, ready_path=str(self.root/'ready.json'), native_sha256='native',
            native_arguments=['selected']), paths=self.paths,
            plan_path=str(self.root/'plan.json'), plan_sha256='selected',
            pi_assert_prefix=['pi'], bench_assert_argv=['bench'], source_thread='driver',
            manager_thread='manager', receiver_thread='extender', receiver_mailbox='linux-extender',
            mailbox=str(self.root), start_delivery_prefix='start-', go_delivery_prefix='go-',
            process_terms=dict(bridge='bridge', controller='controller'),
            loaded_receipt=str(self.root/'loaded.json'), graphics_receipt=str(self.root/'graphics.json'),
            graphics_expected=dict(disposable_ids=[1000, 1001]), required_sources={})
        self.marker = dict(self.arm['expected'], **{k:v for k,v in self.paths.items() if k!='marker_path'},
            lease='a'*32, generation=3, ready_epoch=epoch, ready_monotonic_ns=mono,
            bridge_pid=10, controller_pid=11, bridge_start_ticks=20, controller_start_ticks=21,
            registration_deadline_monotonic_ns=mono+80_000_000_000,
            issued_epoch=epoch, issued_monotonic_ns=mono,
            durable_message_id='2026-11-05_mechagon_selected',
            accepted_start_delivery_id='start-'+'a'*32, accepted_delivery_id='go-'+'a'*32)
        self.pi = dict(owner='mechagon', request='fresh', lease='a'*32, generation=3,
            workload='test', plan=self.arm['plan_path'],
            granted=datetime.now(timezone.utc).isoformat())
        self.write(self.root/'ready.json', self.ready)
        self.write(self.root/'loaded.json', dict(native_loaded_not_invoked=True, actual_cli=True))
        self.write(self.root/'graphics.json', dict(exclusive_whole_sprite_engine=True,
            incoming_global_active_count=0, incoming_slot_hardware=False,
            incoming_slots_no_frames=True, no_competing_feature_writer=True,
            logical_coordinates=True, cursor_enabled=True, cursor_flashing=True,
            disposable_ids=[1000, 1001]))
        self.write(Path(self.paths['guard_heartbeat_path']), dict(epoch=epoch,monotonic=mono/1e9,
            processes={'10':dict(start_ticks=20), '11':dict(start_ticks=21)}))
        for label, target, identity in [('start','manager','start-'+'a'*32),
                                        ('go','extender','go-'+'a'*32)]:
            message=('Durable '+self.marker['durable_message_id']+'\n').encode()
            Path(self.paths[label+'_message_path']).write_bytes(message)
            self.write(Path(self.paths[label+'_delivery_path']), dict(phase='accepted',
                source='driver',target=target,delivery_id=identity,transport='pi-unix-app-server',
                method='turn/steer',message_sha256=hashlib.sha256(message).hexdigest()))
        core={k:v for k,v in self.marker.items() if k not in
              ('durable_message_id','accepted_start_delivery_id','accepted_delivery_id')}
        meta=dict(author='mechagon',recipient='linux-extender',status='published',
                  message_id=self.marker['durable_message_id'])
        (self.root/(meta['message_id']+'.md')).write_text('---\n'+''.join(
            k+': '+json.dumps(v)+'\n' for k,v in meta.items())+'---\n\n'+json.dumps(dict(conditional_go=core)))
        self.plan = dict(unit='selected.service')

    def check(self):
        def assertion(argv): return self.pi if argv[0]=='pi' else self.bench
        with patch.object(receiver,'plan_inputs',return_value=self.plan), \
             patch.object(receiver,'assert_owner',side_effect=assertion), \
             patch.object(receiver,'check_process') as process:
            result=receiver.validate(self.arm,self.marker)
            self.assertEqual(process.call_count,2)
            return result

    def test_complete_existing_receipts_validate_without_device_access(self):
        self.assertEqual(self.check()['request'],'fresh')

    def test_wrong_actual_pi_request_is_refused(self):
        self.pi['request']='stale'
        with self.assertRaises(ValueError): self.check()

    def test_wrong_actual_bench_token_is_refused(self):
        # Keep marker/expected unchanged, change only the observed actual lease.
        self.bench=copy.deepcopy(self.bench);self.bench['lease']='c'*32
        with self.assertRaises(ValueError): self.check()

    def test_queued_delivery_is_refused(self):
        path=Path(self.paths['go_delivery_path']);data=json.loads(path.read_text());data['phase']='queued'
        self.write(path,data)
        with self.assertRaises(ValueError): self.check()

    def test_durable_mail_cannot_substitute_another_request(self):
        path=self.root/(self.marker['durable_message_id']+'.md')
        path.write_text(path.read_text().replace('"fresh"','"other"'))
        with self.assertRaises(ValueError): self.check()

    def test_marker_cannot_extend_original_deadline(self):
        self.marker['registration_deadline_monotonic_ns']+=1
        with self.assertRaises(ValueError): self.check()

    def test_stale_heartbeat_is_refused(self):
        path=Path(self.paths['guard_heartbeat_path']);data=json.loads(path.read_text());data['epoch']-=10
        self.write(path,data)
        with self.assertRaises(ValueError): self.check()

    def test_actual_source_drift_is_refused(self):
        source=self.root/'source.py';source.write_text('pass\n')
        self.arm['required_sources']={str(source):receiver.digest(source)}
        self.plan=dict(schema='mechagon-qualification-plan-v1', executable=True,
            input_sha256={str(source):receiver.digest(source),
            self.arm['loaded_receipt']:receiver.digest(self.arm['loaded_receipt']),
            self.arm['graphics_receipt']:receiver.digest(self.arm['graphics_receipt'])},
            ready_file=self.arm['expected']['ready_path'], native=dict(sha256='native',arguments=['selected']),
            native_go=self.paths)
        self.write(Path(self.arm['plan_path']),self.plan)
        self.arm['plan_sha256']=receiver.digest(self.arm['plan_path'])
        receiver.plan_inputs(self.arm)
        source.write_text('changed\n')
        with self.assertRaises(ValueError):receiver.plan_inputs(self.arm)

    def test_real_process_parser_requires_start_identity_role_and_unit(self):
        process=self.root/'10';process.mkdir()
        fields=['R']+['0']*21;fields[19]='20'
        (process/'stat').write_text('10 (python) '+' '.join(fields))
        (process/'cmdline').write_bytes(b'python\0-m\0bridge\0')
        (process/'cgroup').write_text('0::/user.slice/selected.service\n')
        receiver.check_process(10,20,'bridge','selected.service',proc_root=self.root)
        for ticks,role,unit in ((21,'bridge','selected.service'),
                               (20,'other','selected.service'),(20,'bridge','other.service')):
            with self.subTest(ticks=ticks,role=role,unit=unit),self.assertRaises(ValueError):
                receiver.check_process(10,ticks,role,unit,proc_root=self.root)
        fields[0]='Z';(process/'stat').write_text('10 (python) '+' '.join(fields))
        with self.assertRaises(ValueError):
            receiver.check_process(10,20,'bridge','selected.service',proc_root=self.root)


if __name__=='__main__': unittest.main()
