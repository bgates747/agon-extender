#include "mode0_pattern.h"

#include <string.h>

// The standalone image embeds the frozen VDU bitmap's decoded, opaque AABBGGRR
// samples in flash. Only setup reads the asset. The interrupt uses internal RAM.
extern const uint8_t _binary_mode0_rgba2222_bin_start[];

void mode0_render_reference(uint8_t *frame)
{
    enum { width = 640, height = 480, margin = 104, channels = 3 };
    const uint8_t *source = _binary_mode0_rgba2222_bin_start;
    uint8_t *out = frame;
    for (unsigned y = 0; y < height; ++y) {
        memset(out, 0, margin * channels);
        out += margin * channels;
        for (unsigned x = 0; x < width; ++x) {
            uint8_t pixel = *source++;
            *out++ = ((pixel >> 4) & 3u) * 85u;
            *out++ = ((pixel >> 2) & 3u) * 85u;
            *out++ = (pixel & 3u) * 85u;
        }
        memset(out, 0, margin * channels);
        out += margin * channels;
    }
}
