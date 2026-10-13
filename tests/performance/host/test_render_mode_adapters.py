import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('mode_adapters',ROOT/'qualification/render_modes.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class DirectoryClosure(unittest.TestCase):
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
