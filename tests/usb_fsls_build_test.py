"""Fail-closed SDK backport generation and board-selection guard."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SDK_SOURCE = ROOT / "agents/build001/native-tools/esp-idf/components/usb/hcd_dwc.c"
RECIPE = ROOT / "vdp/native/usb_fsls_only.cmake"


class UsbFslsBuildTest(unittest.TestCase):
    def test_known_sdk_derivative_and_rejection_of_changed_dependency(self):
        original = SDK_SOURCE.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            source, output = work / "hcd.c", work / "patched.c"
            source.write_bytes(original)
            command = ["cmake", f"-DUSB_HCD_SOURCE={source}",
                       f"-DUSB_HCD_OUTPUT={output}", "-P", str(RECIPE)]
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertNotEqual(output.read_bytes(), original)
            output.unlink()
            source.write_bytes(original + b"\n// changed dependency\n")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unreviewed USB HCD source", result.stderr)
            self.assertFalse(output.exists())

    def test_devkit_fsls_request_rejected_before_build_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "uncreated"
            result = subprocess.run(
                [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/build_p4.py"),
                 "--profile", "p4-console", "--board", "p4-devkit",
                 "--usb-fsls-only", "--output", str(output)],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires p4-pc / p4-console", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
