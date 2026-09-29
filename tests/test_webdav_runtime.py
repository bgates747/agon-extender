"""Local admission/card-ownership checks; no hardware or network access."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class RuntimeTests(unittest.TestCase):
    def test_admission_and_media(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("admission_peer_test", "p4_local_files_test", "envelope_test"):
                exe=Path(directory)/name
                subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                    "-fsanitize=address,undefined", "-g", "-I"+str(ROOT/"vdp/video"),
                    str(ROOT/"tests/storage"/(name+".cpp")), "-o", str(exe)],check=True)
                subprocess.run([str(exe)],check=True,timeout=30)

if __name__=='__main__': unittest.main()
