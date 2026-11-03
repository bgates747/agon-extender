"""Real foreground file policy and P4 engine; modeled physical callback."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EMOS = Path(os.environ.get("AGON_EMOS_ROOT", ROOT.parent / "agon-emos"))


class UploadFilePolicyTests(unittest.TestCase):
    def test_file_policy(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            probe = directory / "service.c"
            probe.write_text('#include "'+str(EMOS / 'projects/sdserve/src/service.c')+'"\n'+'''
static unsigned crc_calls;
void __attribute__((no_instrument_function)) __cyg_profile_func_enter(void *f,void *caller) {
    (void)caller;if(f==(void *)sd_crc_update)++crc_calls;
}
void __attribute__((no_instrument_function)) __cyg_profile_func_exit(void *f,void *caller) {(void)f;(void)caller;}
unsigned __attribute__((no_instrument_function)) test_crc_calls(void) {return crc_calls;}
''')
            flags = ["-Wall", "-Wextra", "-Werror", "-Wno-misleading-indentation",
                     "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
            objects = []
            for name, source in (("service", probe), ("fs", EMOS / "tests/sdserve_host/fs.c")):
                obj = directory / (name + ".o")
                subprocess.run(["cc", "-std=c17", *flags, "-DSDSERVE_PARALLEL_UPLOAD=1",
                                "-finstrument-functions", "-fno-inline",
                                f"-I{EMOS / 'tests/sdserve_host'}", "-c", str(source), "-o", str(obj)], check=True)
                objects.append(str(obj))
            executable = directory / "engine"
            subprocess.run(["c++", "-std=c++17", *flags,
                            f"-I{ROOT / 'vdp/video'}", f"-I{EMOS / 'tests/sdserve_host'}",
                            str(ROOT / "tests/storage/parallel_upload_engine_test.cpp"),
                            *objects, "-o", str(executable)], check=True)
            subprocess.run([str(executable), str(directory / "disk")], check=True, timeout=45)


if __name__ == "__main__":
    unittest.main()
