#!/usr/bin/env python3
"""Native host ownership/pixel checks for the experimental scanout snapshot."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix="rolling-scene-") as tmp:
    exe=Path(tmp)/"test"
    for geometry in ([], ["-DAGON_EXTENDER_HDMI_512X384=1"], ["-DAGON_EXTENDER_HDMI_684X384=1"], ["-DAGON_EXTENDER_HDMI_AUTO=1"]):
        subprocess.run(["g++","-std=c++17","-O1","-g","-Wall","-Wextra",
                        "-fsanitize=address,undefined", *geometry,
                        "-I"+str(root/"vdp/video"),str(Path(__file__).with_suffix(".cpp")),"-o",str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
