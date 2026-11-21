"""Exercise the pinned driver's real EOF gate and stop function, with modeled MMIO and time."""
from pathlib import Path
import runpy
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "vdp/video/extender/display/full_frame"
DPI = ROOT / "agents/build001/native-tools/esp-idf/components/esp_lcd/dsi/esp_lcd_panel_dpi.c"


def main():
    driver = runpy.run_path(str(ADAPTER / "patch_dpi.py"))["derive"](DPI.read_bytes())
    callback = driver.split("bool mipi_dsi_dma_trans_done_cb(", 1)[1]
    gate = callback[callback.index("    if (atomic_load"):callback.index("    uint8_t fb_index")]
    model = (Path(__file__).with_suffix(".c")).read_text()
    with tempfile.TemporaryDirectory() as folder:
        for label, hook, expected in [("candidate", gate, 0), ("always-rearm", "", 1)]:
            source = Path(folder) / f"{label}.c"
            source.write_text(model.replace("/* actual EOF gate */", hook))
            binary = source.with_suffix("")
            subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(ADAPTER),
                            str(source), "-o", str(binary)], check=True)
            result = subprocess.run([str(binary)], timeout=5)
            if result.returncode != expected:
                raise RuntimeError(f"{label} returned {result.returncode}, expected {expected}")
            print(f"{label}: expected result {expected}")


if __name__ == "__main__":
    main()
