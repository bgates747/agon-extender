#!/usr/bin/env python3
"""Exercise actual HDMI service scheduling with the existing host substrate."""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GL = ROOT / "vdp/vendor/vdp-gl/src"
RUNTIME = ROOT / "docs/tasks/PORT-003/stock-backend-r2/runtime"
ROW = ROOT / "docs/tasks/PORT-003/stock-backend-r1"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-rows", action="store_true")
    parser.add_argument("--startup-trace", action="store_true", help="also check the diagnostic renderer against ordinary native output")
    parser.add_argument("--palette-dma", type=Path, metavar="GENERATED_DPI_C",
                        help="exercise the row service and native DMA using this build's generated esp_lcd_panel_dpi.c")
    args = parser.parse_args()
    if args.palette_dma and not args.native_rows:
        parser.error("--palette-dma needs --native-rows")
    if args.startup_trace and not args.native_rows:
        parser.error("--startup-trace needs --native-rows")
    sources = [GL / "dispdrivers" / (name + "controller.cpp")
               for name in ("vgabase", "vgapaletted", "vga2", "vga4",
                            "vga8", "vga16", "vga64")]
    sources += [GL / (name + ".cpp")
                for name in ("canvas", "displaycontroller", "codepages", "fabfonts")]
    sources += [ROOT / "vdp/video/extender/port/stock_render_utils.cpp"]
    sources += [ROOT / "vdp/video/extender/display" / (name + ".cpp")
                for name in ("stock_native_access", "stock_scanline",
                             "stock_runtime_controller", "stock_p4_service",
                             "presentation_snapshot_pool", "p4_rgb888_controller")]
    sources.append(HERE / ("native_scanout_palette_test.cpp" if args.palette_dma else "hdmi_frame_scheduling_test.cpp"))
    includes = [HERE / "compat", RUNTIME / "compat", ROW / "compat",
                ROOT / "docs/tasks/PORT-003/phase-c/tests/compat",
                ROOT / "docs/tasks/PORT-003/phase-b/tests/compat",
                GL, ROOT / "vdp/video"]
    with tempfile.TemporaryDirectory(prefix="hdmi-scheduling-") as directory:
        binary = Path(directory) / "check"
        if args.palette_dma:
            tmp = Path(directory)
            # The C fixture models ESP-IDF types, semaphores, clock and GDMA registers.
            for header in ("esp_err.h", "esp_lcd_types.h", "esp_timer.h", "esp_heap_caps.h",
                           "freertos/FreeRTOS.h", "freertos/task.h", "freertos/semphr.h",
                           "freertos/queue.h", "hal/dw_gdma_ll.h"):
                stub = tmp / header
                stub.parent.mkdir(parents=True, exist_ok=True)
                stub.touch()
            dpi = args.palette_dma.read_text()
            begin = dpi.index("bool mipi_dsi_dma_trans_done_cb(")
            end = dpi.index("void mipi_dsi_bridge_isr_handler(", begin)
            (tmp / "palette_dma_rearm.inc").write_text(dpi[begin:end])
            driver = tmp / "native_handoff.o"
            subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-Wno-unused-parameter",
                            "-DAGON_TEST_PALETTE_DMA",
                            *(["-DAGON_EXTENDER_NATIVE_STARTUP_TRACE"] if args.startup_trace else []),
                            "-I" + str(tmp), "-I" + str(ROOT / "vdp/video/extender/display/native_scanout"),
                            "-c", str(HERE / "native_scanout_handoff_test.c"), "-o", str(driver)], check=True)
            sources.append(driver)
        subprocess.run([
            "g++", "-std=c++17", "-O1", "-g", "-pthread",
            "-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections",
            "-DFABGL_EMULATED", "-DAGON_EXTENDER_STOCK_RUNTIME",
            "-DAGON_EXTENDER_HDMI",
            "-DAGON_EXTENDER_NATIVE_SCANOUT" if args.native_rows else "-DAGON_EXTENDER_DIRECT_RGB888",
            *(["-DAGON_EXTENDER_NATIVE_STARTUP_TRACE"] if args.startup_trace else []),
            *(["-DAGON_TEST_PALETTE_DMA", "-I" + str(HERE)] if args.palette_dma else []),
            *["-I" + str(path) for path in includes],
            "-include", str(RUNTIME / "compat/host_preinclude.hpp"),
            *map(str, sources), "-o", str(binary)], check=True)
        if args.palette_dma:
            # The diagnostic captures epoch one once per boot. Start a fresh
            # process for each release point, then replace the mode in-process.
            for frame in (2, 3, 4) if args.startup_trace else (4,):
                subprocess.run([str(binary), str(frame)], check=True, timeout=15)
        else:
            subprocess.run([str(binary)], check=True, timeout=15)
    if not args.palette_dma:
        print("PASS: actual HDMI service presents after native swap, keeps clock independent, and joins shutdown")


if __name__ == "__main__":
    main()
