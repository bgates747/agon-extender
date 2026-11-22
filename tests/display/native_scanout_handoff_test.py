#!/usr/bin/env python3
"""Execute the native C handoff with modeled DSI IRQ/clock/cache, without a board."""
import argparse
from pathlib import Path
import subprocess
import tempfile
import sys

root = Path(__file__).resolve().parents[2]
native = root / "vdp/video/extender/display/native_scanout"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idf", type=Path, required=True, help="pinned ESP-IDF 5.5.5 root")
    parser.add_argument("--startup-trace", action="store_true",
                        help="also run per-boot diagnostic freeze and mode change cases")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for header in ("esp_err.h", "esp_lcd_types.h", "esp_timer.h", "esp_heap_caps.h",
                       "freertos/FreeRTOS.h", "freertos/task.h", "freertos/semphr.h",
                       "freertos/queue.h", "hal/dw_gdma_ll.h"):
            f = tmp / header
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("// Symbols modeled by native_scanout_handoff_test.c\n")
        dpi = tmp / "esp_lcd_panel_dpi.c"
        subprocess.run([sys.executable, str(native / "patch_dpi.py"),
                        str(args.idf / "components/esp_lcd/dsi/esp_lcd_panel_dpi.c"),
                        str(dpi)],check=True)
        derived = dpi.read_text()
        assert "heap_caps_calloc(1, fb_size" not in derived
        assert "esp_async_fbcpy_install(" not in derived
        assert "nr_mark(dpi_panel,b,b < NR_SLOTS)" in derived
        eof = derived[derived.index("bool mipi_dsi_dma_trans_done_cb"):derived.index("void mipi_dsi_bridge_isr_handler")]
        assert eof.index("native_frame(") < eof.index("dw_gdma_channel_enable_ctrl(chan, true)") < eof.index("dpi_panel->on_frame_buf_complete(")
        free = derived[derived.index("static esp_err_t dpi_panel_del(esp_lcd_panel_t *panel)\n{"):]
        assert free.index("agon_dpi_stop(panel)") < free.index("dw_gdma_del_channel") < free.index("native_free(")
        gdma = (args.idf / "components/esp_hw_support/dma/dw_gdma.c").read_text()
        irq = gdma[gdma.index("uint32_t intr_status = dw_gdma_ll_channel_get_intr_status"):]
        assert irq.index("chan->cbs.on_invalid_block(") < irq.index("chan->cbs.on_block_trans_done(") < irq.index("chan->cbs.on_full_trans_done(")
        binary = tmp / "native_handoff"
        compiler = ["cc","-std=c11","-Wall","-Wextra","-Werror","-Wno-unused-function",
                        "-I",str(tmp),"-I",str(native),str(Path(__file__).with_suffix(".c")),
                        "-o",str(binary)]
        subprocess.run(compiler, check=True)
        subprocess.run([str(binary)], check=True)
        if args.startup_trace:
            subprocess.run(compiler + ["-DAGON_EXTENDER_NATIVE_STARTUP_TRACE=1"], check=True)
            for height in (480, 384):
                for case in ("success", "withheld", "wake-lock", "reader-lock", "drawing-lock",
                             "compose", "expand", "cache", "publish", "first-fault", "other-fault",
                             "budget-edge", "budget-pre", "budget-valid"):
                    # Each process starts in boot epoch 1. Each case also drives epoch 2.
                    subprocess.run([str(binary), str(height), case], check=True)

if __name__ == "__main__":
    main()
