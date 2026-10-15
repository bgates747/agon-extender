import importlib.util
from pathlib import Path
import unittest
import tempfile
import json
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('mode_adapters',ROOT/'qualification/render_modes.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class DirectoryClosure(unittest.TestCase):
    def test_admission_starts_offline_listener_from_confirmed_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            a=object.__new__(m.Adapter);a.b=Mock();a.m=Mock();a.checked=Mock()
            a.b.config={'p4':'http://test'};a.b.state={}
            a.m.get.side_effect=[dict(online=False,pending=False),dict(online=False)]
            c=a.m.SDClient.return_value;c.download.return_value=m.mode_startup(0)
            with unittest.mock.patch.object(m.time,'sleep'):
                a.admit(Path(directory),confirmed_cli=True)
            self.assertEqual([call.args[0] for call in a.b.key_command.call_args_list],
                             ['EMOS LEGACY','EMOS sdserve --fast /'])
            c.rpc.assert_called_once_with(11)
            a.b.fast_start.assert_called_once()
            self.assertTrue(json.loads((Path(directory)/'admission.json').read_text())['listener_online'])

    def test_admission_reuses_online_listener_without_typing(self):
        with tempfile.TemporaryDirectory() as directory:
            a=object.__new__(m.Adapter);a.b=Mock();a.m=Mock();a.checked=Mock()
            a.b.config={};a.m.get.return_value=dict(online=True,pending=False)
            a.admit(Path(directory))
            a.b.fast_connect.assert_called_once()
            a.b.key_command.assert_not_called()

    def test_admission_does_not_guess_cli_or_discard_pending_request(self):
        with tempfile.TemporaryDirectory() as directory:
            a=object.__new__(m.Adapter);a.b=Mock();a.m=Mock()
            a.b.config={};a.b.state={};a.m.get.return_value=dict(online=False,pending=False)
            with self.assertRaisesRegex(RuntimeError,'confirmed CLI'):a.admit(Path(directory))
            journal=Path(directory)/'journal.json';journal.write_text('{"pending":"retained"}')
            a.b.state['fast_journal']=str(journal)
            with self.assertRaisesRegex(RuntimeError,'Uncertain SD'):a.admit(Path(directory),True)
            a.b.key_command.assert_not_called()
            self.assertEqual(json.loads(journal.read_text())['pending'],'retained')

    def test_startup_replacement_keeps_listener_and_verifies_both_files_before_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            a=object.__new__(m.Adapter)
            a.b=Mock();a.m=Mock();a.m.absent.return_value=True
            a.b.fast_read.side_effect=[b'old',b'old',b'new',b'old']
            a.replace_startup(b'new','/agents/extender/backups/startup/example.txt',Path(directory)/'old.txt')
            a.b.fast_exit.assert_not_called()
            a.b.move.assert_not_called()
            a.b.fast_connect().upload.assert_called_once_with('/autoexec.txt',b'new',True,fast=True)
            a.b.fast_connect().rpc.assert_called_once_with(10,b'\x03'+m.path_payload('/autoexec.txt'))

    def test_uncertain_startup_activation_preserves_backup_and_journal(self):
        with tempfile.TemporaryDirectory() as directory:
            a=object.__new__(m.Adapter)
            a.b=Mock();a.m=Mock();a.m.absent.return_value=True
            a.b.fast_read.side_effect=[b'old',b'old']
            a.b.fast_connect().upload.side_effect=TimeoutError('uncertain activation')
            with self.assertRaises(TimeoutError):
                a.replace_startup(b'new','/agents/extender/backups/startup/example.txt',Path(directory)/'old.txt')
            a.b.fast_connect().rpc.assert_not_called()
            a.b.fast_exit.assert_not_called()

    def test_physical_collection_retains_sidecars_without_downloading_raw(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            adapter=object.__new__(m.Adapter)
            adapter.package=folder
            (folder/'plan.json').write_text('{}')
            (folder/'run.cfg').write_bytes(b'configuration')
            job=dict(id='rgb888-m0-c1-r1',renderer='rgb888',mode=0,
                     case='bitmap-light',repeat=1,game=False,smoke=False,
                     result='/agents/extender/results/example/records.bin',
                     config_local='run.cfg',config_remote='/agents/extender/results/example/run.cfg',
                     command_remote='/agents/extender/results/example/run.txt')
            adapter.p=dict(jobs=[job])
            adapter.c=dict(collection='physical-card')
            adapter.state=dict(staged=True,plan_sha256=m.sha(b'{}'),identity='verified-image')
            adapter.select_renderer=Mock();adapter.mode=Mock();adapter.checked=Mock()
            adapter.b=Mock();adapter.b.config={}
            adapter.b.fast_read.return_value=b'configuration'
            adapter.m=Mock();adapter.m.absent.return_value=True
            adapter.m.get.side_effect=[dict(open=0),dict(available=True),dict(open=0),dict(available=True)]
            receipt=folder/'receipt.json'
            self.assertEqual(adapter.run(job['id'],receipt,folder),0)
            adapter.b.fast_read.assert_called_once_with(job['config_remote'])
            result=json.loads(receipt.read_text())
            self.assertFalse(result['validated'])
            self.assertTrue(result['collection_pending'])
            self.assertEqual(result['result_remote'],job['result'])
            self.assertEqual(len(result['sidecar_sha256']),4)
            for name,digest in result['sidecar_sha256'].items():
                self.assertEqual(digest,m.sha((folder/name).read_bytes()))

    def test_changed_package_stops_before_any_bench_operation(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter=object.__new__(m.Adapter)
            adapter.package=Path(directory)
            (adapter.package/'plan.json').write_text('{}')
            adapter.state={'staged':True,'plan_sha256':'old-package'}
            with self.assertRaisesRegex(RuntimeError,'different package'):
                adapter.run('unused',Path(directory)/'receipt',Path(directory))

    def test_mode_startup_returns_to_legacy_without_launching_a_fixture(self):
        for mode in m.MODES:
            lines=m.mode_startup(mode).decode().splitlines()
            self.assertEqual(lines[-1],'EMOS LEGACY --keep-display')
            self.assertLess(lines.index('EMOS LEGACY'),lines.index('EMOS EXCOM'))
            self.assertLess(lines.index('EMOS EXCOM'),lines.index('VDU 22 '+str(mode)))
            self.assertFalse(any(s.startswith(('LOAD ','RUN','EXEC ')) for s in lines))

    def test_every_nested_parent_precedes_its_child(self):
        paths=m.directory_closure([
            dict(remote='/extender/render-qualification-r01/m136/c8/fixture.bin'),
            dict(remote='/agents/extender/results/rq-example/indexed-m136-c8-r3/run.cfg')])
        self.assertIn('/extender/render-qualification-r01/m136',paths)
        self.assertNotIn('/extender',paths)
        self.assertNotIn('/agents/extender/results',paths)
        self.assertEqual(len(paths),len(set(paths)))
        for i,path in enumerate(paths):
            parent=str(Path(path).parent)
            if parent in paths:self.assertLess(paths.index(parent),i)


if __name__=='__main__':unittest.main()
