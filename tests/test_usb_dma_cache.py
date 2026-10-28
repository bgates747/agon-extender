"""Execute the selected HCD cache helper; no ESP-IDF build or hardware required."""
from pathlib import Path
import os
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SDK_SOURCE = ROOT / "agents/build001/native-tools/esp-idf/components/usb/hcd_dwc.c"
RECIPE = ROOT / "vdp/native/usb_fsls_only.cmake"


def cache_helper(source, name):
    """Retain the actual helper body, rather than duplicating its predicates."""
    match = re.search(r"static inline void cache_sync_data_buffer\([^)]*\)\s*\{", source)
    if match is None:
        raise AssertionError("SDK cache helper definition is absent")
    start, position, depth = match.start(), match.end(), 1
    while depth and position < len(source):
        depth += (source[position] == "{") - (source[position] == "}")
        position += 1
    if depth:
        raise AssertionError("SDK cache helper has an unterminated body")
    return source[start:position].replace("cache_sync_data_buffer", name, 1)


HARNESS = r"""
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

/* Only the helper's external types/API are replaced. Its implementation below
 * is extracted directly from the SDK and the generated build input. The flags
 * use esp_cache.h's public values; absent direction means C2M in this SDK. */
#define ESP_CACHE_MSYNC_FLAG_INVALIDATE (1u << 0)
#define ESP_CACHE_MSYNC_FLAG_UNALIGNED (1u << 1)
#define ESP_CACHE_MSYNC_FLAG_DIR_C2M (1u << 2)
#define ESP_CACHE_MSYNC_FLAG_DIR_M2C (1u << 3)
#define USB_B_ENDPOINT_ADDRESS_EP_DIR_MASK 0x80u
#define USB_DWC_XFER_TYPE_CTRL 0
#define ESP_OK 0
typedef int esp_err_t;
typedef struct { struct { unsigned bEndpointAddress; int type; } ep_char; } pipe_t;
typedef struct {
    struct { void *data_buffer; size_t data_buffer_size; int num_bytes; } transfer;
} urb_t;
static unsigned calls;
static void *observed_buffer;
static size_t observed_size;
static uint32_t observed_flags;
static esp_err_t esp_cache_msync(void *buffer, size_t size, uint32_t flags)
{
    ++calls;
    observed_buffer = buffer;
    observed_size = size;
    observed_flags = flags;
    return ESP_OK;
}

__ORIGINAL_HELPER__
__SELECTED_HELPER__

#define REQUIRE(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "cache contract failed at line %d: %s\n", __LINE__, #condition); \
        return 1; \
    } \
} while (0)

int main(void)
{
    unsigned char buffers[2][2048] = {{0}};
    urb_t urb = {.transfer = {.data_buffer = buffers[0], .data_buffer_size = 64, .num_bytes = 7}};
    pipe_t pipe = {.ep_char = {.bEndpointAddress = 0x81, .type = 3}};

    /* Prove this regression distinguishes the original SDK's missing IN clean,
     * rather than accepting either selection or just inspecting patch text. */
    calls = 0;
    original_cache_sync_data_buffer(&pipe, &urb, false);
    REQUIRE(calls == 0);
    calls = 0;
    selected_cache_sync_data_buffer(&pipe, &urb, false);
    REQUIRE(calls == 1);
    REQUIRE((observed_flags & ESP_CACHE_MSYNC_FLAG_DIR_M2C) == 0);

    unsigned cases = 0;
    for (int type = 0; type < 4; ++type) {
        for (unsigned direction = 0; direction < 2; ++direction) {
            for (unsigned done = 0; done < 2; ++done) {
                pipe.ep_char.type = type;
                pipe.ep_char.bEndpointAddress = 1u | (direction ? 0x80u : 0u);
                urb.transfer.data_buffer = buffers[cases % 2];
                urb.transfer.data_buffer_size = 64u * (cases + 1u);
                calls = 0;
                observed_buffer = NULL;
                observed_size = 0;
                observed_flags = UINT32_MAX;
                selected_cache_sync_data_buffer(&pipe, &urb, done != 0);

                const bool expected_sync = !done || direction || type == USB_DWC_XFER_TYPE_CTRL;
                REQUIRE(calls == (unsigned)expected_sync);
                if (expected_sync) {
                    REQUIRE(observed_buffer == urb.transfer.data_buffer);
                    /* Use full allocated buffer ownership, not requested bytes. */
                    REQUIRE(observed_size == urb.transfer.data_buffer_size);
                    REQUIRE(observed_size != (size_t)urb.transfer.num_bytes);
                    if (done) {
                        REQUIRE(observed_flags == ESP_CACHE_MSYNC_FLAG_DIR_M2C);
                    } else {
                        REQUIRE((observed_flags & ESP_CACHE_MSYNC_FLAG_DIR_M2C) == 0);
                        REQUIRE((observed_flags & ESP_CACHE_MSYNC_FLAG_UNALIGNED) != 0);
                        REQUIRE((observed_flags & ESP_CACHE_MSYNC_FLAG_INVALIDATE) == 0);
                        REQUIRE((observed_flags & ~(ESP_CACHE_MSYNC_FLAG_DIR_C2M |
                                                   ESP_CACHE_MSYNC_FLAG_UNALIGNED)) == 0);
                    }
                }
                ++cases;
            }
        }
    }
    REQUIRE(cases == 16);
    puts("HCD cache ownership: 16 selected cases and original IN regression passed");
    return 0;
}
"""


class UsbDmaCacheTest(unittest.TestCase):
    def test_generated_helper_cleans_in_before_dma_and_preserves_completion(self):
        original = SDK_SOURCE.read_text()
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            selected = work / "selected-hcd.c"
            generation = subprocess.run(
                ["cmake", f"-DUSB_HCD_SOURCE={SDK_SOURCE}",
                 f"-DUSB_HCD_OUTPUT={selected}", "-P", str(RECIPE)],
                capture_output=True, text=True)
            self.assertEqual(generation.returncode, 0, generation.stdout + generation.stderr)
            self.assertEqual(SDK_SOURCE.read_text(), original)
            harness = HARNESS.replace(
                "__ORIGINAL_HELPER__", cache_helper(original, "original_cache_sync_data_buffer")
            ).replace(
                "__SELECTED_HELPER__", cache_helper(selected.read_text(), "selected_cache_sync_data_buffer")
            )
            source, executable = work / "cache-contract.c", work / "cache-contract"
            source.write_text(harness)
            compilation = subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-fsanitize=address,undefined", str(source), "-o", str(executable)],
                capture_output=True, text=True)
            self.assertEqual(compilation.returncode, 0, compilation.stdout + compilation.stderr)
            # The managed runner may use ptrace, which prevents LeakSanitizer's
            # process scan. This allocation-free harness still uses ASan/UBSan.
            environment = dict(os.environ)
            previous = environment.get("ASAN_OPTIONS", "")
            environment["ASAN_OPTIONS"] = previous + (":" if previous else "") + "detect_leaks=0"
            result = subprocess.run([str(executable)], capture_output=True, text=True,
                                    env=environment)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("16 selected cases and original IN regression passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
