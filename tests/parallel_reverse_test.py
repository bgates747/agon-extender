"""Execute actual EMOS C and EDP C++ cores in one deterministic wire model."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EMOS = Path(os.environ.get("AGON_EMOS_ROOT", ROOT.parent / "agon-emos"))


class PairedReverseTests(unittest.TestCase):
    def test_paired_cores(self):
        with tempfile.TemporaryDirectory() as directory:
            obj = Path(directory) / "emos.o"
            exe = Path(directory) / "paired"
            includes = [f"-I{EMOS / 'tests/host'}", f"-I{EMOS / 'src'}"]
            warnings = ["-Wall", "-Wextra", "-Werror", "-pedantic"]
            subprocess.run(["cc", "-std=c17", *warnings, *includes, "-c",
                            str(EMOS / "src/emos_parallel_engine.c"), "-o", str(obj)], check=True)
            subprocess.run(["c++", "-std=c++17", *warnings, *includes,
                            f"-I{ROOT / 'vdp/video'}", str(obj),
                            str(ROOT / "tests/parallel_reverse_test.cpp"),
                            str(ROOT / "vdp/video/extender/transport/p4_parallel_egress.cpp"),
                            "-o", str(exe)], check=True)
            result = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            self.assertIn("paired reverse-core cases", result.stdout)
            print(result.stdout, end="")


if __name__ == "__main__":
    unittest.main()
