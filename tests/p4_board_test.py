"""Board allocation failures and emitted compile-time transport contracts."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from p4_board import apply_sdk_overrides, load_board, render_header, validate_board
from build_p4 import checked_tools


class BoardTest(unittest.TestCase):
    def test_unsupported_boards_and_compositions_fail(self):
        for name, profile in (("../p4-pc", "p4-console"), ("unknown", "p4-console"),
                              ("p4-pc", "p4-mos-recovery"),
                              ("p4-pc", "p4-port008-nonrelease-qualification")):
            with self.subTest(name=name, profile=profile), self.assertRaises(SystemExit):
                load_board(name, profile)

    def test_duplicate_reserved_missing_header_and_sensing_fail(self):
        original, _ = load_board("p4-pc", "p4-console")
        for mutate in (
            lambda b: b["transport"]["data"].__setitem__(1, 17),
            lambda b: b["transport"]["data"].__setitem__(0, 26),
            lambda b: b["transport"]["data"].__setitem__(0, 0),
            lambda b: b["requires_disconnected_sensing"].clear(),
            lambda b: b["header"]["gpio_pins"].__setitem__("17", 1),
            lambda b: b["ethernet"].__setitem__("mdc", 17),
            lambda b: b["sdkconfig_overrides"].__setitem__("CONFIG_UNREVIEWED", "y"),
            lambda b: b["transport"]["data"].__setitem__(0, True),
        ):
            board = deepcopy(original)
            mutate(board)
            with self.subTest(board=board), self.assertRaises(SystemExit):
                validate_board(board, "p4-pc", "p4-console")

    def test_sdk_overrides_replace_disabled_and_enabled_lines(self):
        config = "# CONFIG_USB_HOST_HUBS_SUPPORTED is not set\nCONFIG_OTHER=y\n"
        result = apply_sdk_overrides(config, {"CONFIG_USB_HOST_HUBS_SUPPORTED": "y"})
        self.assertEqual(result.count("CONFIG_USB_HOST_HUBS_SUPPORTED"), 1)
        self.assertIn("CONFIG_USB_HOST_HUBS_SUPPORTED=y\n", result)
        self.assertIn("CONFIG_OTHER=y\n", result)
        self.assertEqual(apply_sdk_overrides(config, {}), config)

    def test_generated_cpp_preserves_uart_roles_and_fences_only_selected_pins(self):
        # Explicit tuples are review oracles, independent of the generator.
        for name, uart, data, fence_count in (
            ("p4-devkit", (12, 22, 11, 23), (22, 12, 23, 11, 32, 10, 33, 9), 14),
            ("p4-pc", (18, 17, 20, 19), (17, 18, 19, 20, 32, 33, 36, 46), 11),
        ):
            with self.subTest(board=name), tempfile.TemporaryDirectory() as temporary:
                work = Path(temporary)
                board, _ = load_board(name, "p4-console")
                (work / "board.hpp").write_text(render_header(board))
                checks = '#include "board.hpp"\nusing namespace agon::extender::board;\n'
                checks += f"static_assert(kFencePins.size()=={fence_count});\n"
                for key, value in zip(("Tx", "Rx", "Rts", "Cts"), uart):
                    checks += f"static_assert(kUart{key}=={value});\n"
                for index, value in enumerate(data):
                    checks += f"static_assert(kDataPins[{index}]=={value});\n"
                checks += "int main() {}\n"
                (work / "check.cpp").write_text(checks)
                subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                                str(work / "check.cpp"), "-o", str(work / "check")], check=True)

    def test_bad_host_tools_fail_before_build(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(SystemExit, "toolchain"):
            checked_tools(Path(directory), Path(directory))


if __name__ == "__main__":
    unittest.main()
