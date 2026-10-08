"""Run both maintained handover cores against delayed/failed hardware adapters."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EMOS = Path(os.environ.get("AGON_EMOS_ROOT", ROOT.parent / "agon-emos"))

class HandoverTests(unittest.TestCase):
    def test_paired(self):
        with tempfile.TemporaryDirectory() as td:
            obj, exe = Path(td) / "emos.o", Path(td) / "paired"
            flags = ["-Wall", "-Wextra", "-Werror", "-pedantic"]
            includes = [f"-I{EMOS / 'tests/host'}", f"-I{EMOS / 'src'}"]
            subprocess.run(["cc", "-std=c17", *flags, *includes, "-c",
                            str(EMOS / "src/emos_parallel_handover.c"), "-o", str(obj)], check=True)
            subprocess.run(["c++", "-std=c++17", *flags, *includes,
                            f"-I{ROOT / 'vdp/video'}", str(obj),
                            str(ROOT / "tests/parallel_handover_test.cpp"),
                            str(ROOT / "vdp/video/extender/transport/p4_parallel_handover.cpp"),
                            "-o", str(exe)], check=True)
            args = [str(exe)]
            if os.environ.get("HANDOVER_VECTORS"):
                args.append(os.environ["HANDOVER_VECTORS"])
            subprocess.run(args, check=True)

if __name__ == "__main__":
    unittest.main()
