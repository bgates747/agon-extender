"""Verify browser pixel allocation and carrier policy in the native HDMI selection."""
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
VIDEO = HERE.parents[1] / "vdp/video"

with tempfile.TemporaryDirectory(prefix="native-scanout-services-") as tmp:
    binary = Path(tmp) / "check"
    subprocess.run([
        "g++", "-std=c++17", "-O1", "-pthread", "-DAGON_EXTENDER_HDMI_AUTO",
        "-DAGON_EXTENDER_NATIVE_SCANOUT", "-DAGON_EXTENDER_SNAPSHOT_MUTEX",
        "-I" + str(VIDEO), str(HERE / "native_scanout_services_test.cpp"),
        str(VIDEO / "extender/display/presentation_snapshot_pool.cpp"),
        str(VIDEO / "extender/network/opaque_message.cpp"),
        str(VIDEO / "extender/web/browser_video_provider.cpp"),
        "-o", str(binary)
    ], check=True)
    subprocess.run([str(binary)], check=True)
