"""Run AUDIT-010 RP06 mode prepare/commit failure and source contracts."""

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ModeTransactionTests(unittest.TestCase):
    def test_every_preparation_failure_preserves_live_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "mode-transaction-test"
            subprocess.run(
                [
                    "c++", "-std=c++17", "-O1", "-g", "-Wall", "-Wextra",
                    "-Werror", "-fsanitize=address,undefined",
                    "-fno-sanitize-recover=all", "-I" + str(ROOT / "vdp/video"),
                    str(ROOT / "tests/mode_transaction_test.cpp"), "-o", str(binary),
                ],
                check=True,
            )
            subprocess.run([str(binary)], check=True)

    def test_selected_facade_uses_no_fail_commit_and_truthful_fallback(self):
        screen = (ROOT / "vdp/video/agon_screen.h").read_text()
        vdu = (ROOT / "vdp/video/vdu.h").read_text()
        service = (ROOT / "vdp/video/extender/display/stock_p4_service.cpp").read_text()
        prepare = screen.index("prepareModeCandidate(candidate")
        commit = screen.index("commitPreparedMode(std::move(candidate)")
        retire = screen.index("_stockFrameService->detach()", commit)
        bind = screen.index("controller.bindNativeAliases()", retire)
        activate = screen.index("service.activate()", bind)
        publish = screen.index("_stockController = std::move", activate)
        self.assertLess(prepare, commit)
        self.assertLess(retire, bind)
        self.assertLess(bind, activate)
        self.assertLess(activate, publish)
        self.assertIn("if (!self.active_.load", service)
        self.assertNotIn("videoMode = 1;\n\t\t\tchangeMode(1);", vdu)


if __name__ == "__main__":
    unittest.main()
