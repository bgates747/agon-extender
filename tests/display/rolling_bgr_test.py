#!/usr/bin/env python3
"""Exact stock/direct-BGR scanout golden checks; no bench or speed claims."""
from pathlib import Path
import subprocess, tempfile
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"vdp/video/extender/display/rolling"
with tempfile.TemporaryDirectory(prefix="rolling-bgr-") as tmp:
    temp=Path(tmp)
    for variant in ("baseline","candidate"):
        directory=temp/variant;directory.mkdir()
        for name in ("scene.hpp","scene_bgr.hpp","strip_config.h"):
            # GCC can coalesce identical pragma-once copies by content; the
            # different prefix forces two independently compiled namespaces.
            (directory/name).write_text("// Isolated "+variant+" copy.\n"+
                                        (SOURCE/name).read_text())
    exe=temp/"golden"
    subprocess.run(["g++","-std=c++17","-O2","-g","-Wall","-Wextra",
                    "-fsanitize=address,undefined","-fno-omit-frame-pointer",
                    "-I"+str(temp),"-I"+str(ROOT/"vdp"),
                    "-I"+str(ROOT/"vdp/video"),
                    str(Path(__file__).with_suffix(".cpp")),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True,timeout=60)
