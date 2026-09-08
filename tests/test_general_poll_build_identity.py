"""A successful link must not publish stale boot identity as a new candidate."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    'prepare_general_poll', Path(__file__).resolve().parents[1] / 'scripts/prepare_general_poll.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EmbeddedIdentityTests(unittest.TestCase):
    def test_reject_stale_and_unterminated_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'firmware.bin'
            for data in (b'probe-r01\0old-build\0draft\0',
                         b'probe-r01\0new-build-extra\0candidate\0'):
                image.write_bytes(data)
                with self.assertRaises(ValueError):
                    module.verify_embedded_identity(image, 'probe-r01', 'new-build', 'candidate')

    def test_accept_exact_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'firmware.bin'
            image.write_bytes(b'probe-r01\0new-build\0candidate\0')
            module.verify_embedded_identity(image, 'probe-r01', 'new-build', 'candidate')
