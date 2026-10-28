"""Fail-closed SDK backport generation and board-selection guard."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SDK_SOURCE = ROOT / "agents/build001/native-tools/esp-idf/components/usb/hcd_dwc.c"
RECIPE = ROOT / "vdp/native/usb_fsls_only.cmake"
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p4_build import check_usb_hcd_derivative


def generate(output: Path) -> str:
    subprocess.run(["cmake", f"-DUSB_HCD_SOURCE={SDK_SOURCE}",
                    f"-DUSB_HCD_OUTPUT={output}", "-P", str(RECIPE)],
                   check=True, capture_output=True)
    return output.read_text()


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

    def test_validator_rejects_changes_anywhere_in_complete_derivative(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "patched.c"
            text = generate(output)
            check_usb_hcd_derivative(SDK_SOURCE, output)
            for altered in (text + "\n// unrelated change\n",
                            text.replace("if (!done || is_in || is_ctrl)",
                                         "if ((is_in == done) || is_ctrl)"),
                            text.replace("ls_error.stage", "ls_error.frame")):
                self.assertNotEqual(altered, text)
                output.write_text(altered)
                with self.assertRaisesRegex(SystemExit, "complete bounded"):
                    check_usb_hcd_derivative(SDK_SOURCE, output)

    def test_ls_error_snapshot_lifecycle_and_task_only_publication(self):
        # The executable register/lifecycle cases live in test_usb_ls_registers;
        # keep these source-bound ownership checks beside the build gates.
        with tempfile.TemporaryDirectory() as temporary:
            text = generate(Path(temporary) / "patched.c")
            isr = text.split("static hcd_pipe_event_t _intr_hdlr_chan(", 1)[1]
            isr = isr.split("static void intr_hdlr_main(", 1)[0]
            before_decode = isr.split("usb_dwc_hal_chan_decode_intr(chan_obj)", 1)[0]
            self.assertIn("pipe->ep_char.type == USB_DWC_XFER_TYPE_CTRL", before_decode)
            self.assertIn("pipe->ep_char.ls_via_fs_hub", before_decode)
            self.assertIn("ls_before_decode.hcint = chan_obj->regs->hcint_reg.val", before_decode)
            self.assertIn("ls_before_decode.hctsiz = chan_obj->regs->hctsiz_reg.val", before_decode)
            self.assertIn("if (ls_before_decode.hsphy_type != 0)", before_decode)
            self.assertEqual(before_decode.count(".val;"), 8)
            self.assertNotIn("ESP_LOG", isr)
            error = isr.split("case USB_DWC_HAL_CHAN_EVENT_ERROR: {", 1)[1]
            error = error.split("case USB_DWC_HAL_CHAN_EVENT_HALT_REQ:", 1)[0]
            self.assertLess(error.index("pipe->extender_ls_error = ls_before_decode"),
                            error.index("_buffer_parse(pipe)"))
            dequeue = text.split("urb_t *hcd_urb_dequeue(", 1)[1]
            dequeue = dequeue.split("esp_err_t hcd_urb_abort(", 1)[0]
            before_unlock, after_unlock = dequeue.split("    HCD_EXIT_CRITICAL();", 1)
            self.assertNotIn("ESP_LOG", before_unlock)
            self.assertNotIn("pipe->", after_unlock)
            self.assertNotIn("chan_obj->", after_unlock)
            self.assertEqual(after_unlock.count("ESP_LOGE("), 1)


if __name__ == "__main__":
    unittest.main()
