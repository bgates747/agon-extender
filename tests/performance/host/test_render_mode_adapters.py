import importlib.util
from pathlib import Path
import unittest
import tempfile

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('mode_adapters',ROOT/'qualification/render_modes.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class DirectoryClosure(unittest.TestCase):
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
