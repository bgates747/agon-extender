"""Review tripwire rejects modified, missing and invalid inventories."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('numeric_gate', ROOT/'scripts/check_numeric_port.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class ReviewGate(unittest.TestCase):
    def test_changed_and_missing_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root/'guard.hpp'
            path.write_bytes(b'guarded')
            review = dict(schema_version=1, review_reference='review',
                          inputs={'guard.hpp': hashlib.sha256(path.read_bytes()).hexdigest()})
            self.assertEqual(gate.check_inputs(root, review), [])
            path.write_bytes(b'upstream import removed guard')
            self.assertEqual(gate.check_inputs(root, review), ['changed: guard.hpp'])
            path.unlink()
            self.assertEqual(gate.check_inputs(root, review), ['missing: guard.hpp'])

    def test_invalid_inventory(self):
        for inputs in ({}, {'../outside':'hash'}, {'/outside':'hash'}):
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                gate.check_inputs(ROOT, dict(schema_version=1, review_reference='review', inputs=inputs))


if __name__ == '__main__':
    unittest.main()
