"""Paired actual EMOS/P4 upload coordinators; fake SDK, byte I/O and parking."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from p4_block_coordinator_test import prepare_sdk

ROOT = Path(__file__).resolve().parents[1]
EMOS = Path(os.environ.get("AGON_EMOS_ROOT", ROOT.parent / "agon-emos"))


class UploadPairTests(unittest.TestCase):
    def test_paired_coordinators(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            prepare_sdk(directory)
            includes = [f"-I{directory}", f"-I{EMOS / 'tests/host'}",
                        f"-I{EMOS / 'src'}", f"-I{EMOS / 'src_fatfs'}", f"-I{ROOT / 'vdp/video'}"]
            flags = ["-Wall", "-Wextra", "-Werror", "-Wno-endif-labels",
                     "-ffunction-sections", "-fdata-sections", "-DMOS_DEFINES_H=1", "-DEMOS_BUSY=31", "-DEMOS_UNAVAILABLE=35",
                     "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
            objects = []
            for name in ("emos_parallel_upload", "emos_parallel_handover"):
                target = directory / (name + ".o")
                subprocess.run(["cc", "-std=c17", *flags, *includes, "-include", "eZ80.h",
                                "-c", str(EMOS / "src" / (name + ".c")), "-o", str(target)], check=True)
                objects.append(str(target))
            source = directory / "pair.cpp"
            prefix = (ROOT / "tests/p4_parallel_upload_test.cpp").read_text().split("int main(){")[0]
            source.write_text(prefix + (ROOT / "tests/parallel_upload_pair_test.cpp").read_text())
            executable = directory / "pair"
            subprocess.run(["c++", "-std=c++17", *flags, "-DAGON_EXTENDER_UPLOAD_TEST",
                            *includes, str(source), *objects,
                            *[str(ROOT / "vdp/video/extender/transport" / (name + ".cpp"))
                              for name in ("p4_parallel_upload", "p4_upload_coordinator", "p4_parallel_handover")],
                            "-Wl,--gc-sections", "-o", str(executable)], check=True)
            subprocess.run([str(executable)], check=True, timeout=45)


if __name__ == "__main__":
    unittest.main()
