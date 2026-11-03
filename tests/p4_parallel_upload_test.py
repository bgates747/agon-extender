"""Run actual whole-file PSRAM/native DMA source through modeled IDF edges."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import tempfile
from time import monotonic
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ParallelUploadTests(unittest.TestCase):
    def test_source_and_native_loop(self):
        started = datetime.now(timezone.utc).isoformat()
        clock = monotonic()
        try:
            with tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                for header in (
                    "driver/parlio_tx.h", "driver/gpio_filter.h", "driver/gpio.h",
                    "driver/pulse_cnt.h", "freertos/FreeRTOS.h", "esp_heap_caps.h",
                    "esp_rom_gpio.h", "esp_private/gpio.h", "soc/parlio_periph.h",
                    "soc/io_mux_reg.h",
                ):
                    path = directory / header
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('#include "p4_native_sdk_fake.hpp"\n')
                executable = directory / "upload"
                subprocess.run([
                    "c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                    "-DAGON_EXTENDER_UPLOAD_TEST", "-fsanitize=address,undefined",
                    "-fno-sanitize-recover=all", f"-I{directory}",
                    f"-I{ROOT / 'tests'}", f"-I{ROOT / 'vdp/video'}",
                    str(ROOT / "tests/p4_parallel_upload_test.cpp"),
                    str(ROOT / "vdp/video/extender/transport/p4_parallel_upload.cpp"),
                    "-o", str(executable),
                ], check=True)
                subprocess.run([str(executable)], check=True, timeout=45)
        finally:
            print(f"Whole-file upload host check: start={started}, "
                  f"end={datetime.now(timezone.utc).isoformat()}, "
                  f"elapsed={monotonic()-clock:.6f} s; modeled SDK, not GPIO timing")


if __name__ == "__main__":
    unittest.main()
