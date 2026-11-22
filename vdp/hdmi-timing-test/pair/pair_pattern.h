/* The live pattern owns the complete 848-pixel BGR888 row. Each four-pixel
 * group occupies three aligned words. Emit each destination byte once,
 * including the side code and the live/primed corner marker. */
#pragma once
#include <stdbool.h>
#include <stdint.h>

static inline uint32_t *pair_write_groups(uint32_t *dst, unsigned groups, uint32_t rgb)
{
    const uint32_t first = rgb | (rgb << 24);
    const uint32_t middle = (rgb >> 8) | (rgb << 16);
    const uint32_t last = (rgb >> 16) | (rgb << 8);
    while (groups--) {
        *dst++ = first;
        *dst++ = middle;
        *dst++ = last;
    }
    return dst;
}

static inline void pair_pattern_fill(uint8_t *out, unsigned frame, unsigned pair, bool primed)
{
    static const uint32_t bars[] = {
        0x000000, 0xff0000, 0x00ff00, 0x0000ff,
        0xffff00, 0xff00ff, 0x00ffff, 0xffffff
    };
    // Reserve the rightmost 72 pixels for two nine-bit numbers (LSB first).
    // Bar widths are rounded to groups of four pixels for aligned CPU writes.
    const unsigned code_start = 194;
    const unsigned marker_bar = (frame / 60) & 1 ? 6 : 0;
    for (unsigned local_y = 0; local_y < 2; ++local_y) {
        uint32_t *dst = (uint32_t *)(out + local_y * 848 * 3);
        const unsigned y = pair * 2 + local_y;
        for (unsigned i = 0; i < 8; ++i) {
            const unsigned start = (i * 212) / 8;
            const unsigned end = i == 7 ? code_start : ((i + 1) * 212) / 8;
            if (y < 24 && i == marker_bar) {
                dst = pair_write_groups(dst, 2, bars[i]);
                dst = pair_write_groups(dst, 20, primed ? 0xffaa00 : 0x00ff00);
                dst = pair_write_groups(dst, end - start - 22, bars[i]);
            } else {
                dst = pair_write_groups(dst, end - start, bars[i]);
            }
        }
        const unsigned code = (frame << 9) | y;
        for (unsigned bit = 0; bit < 18; ++bit)
            dst = pair_write_groups(dst, 1, code & (1u << bit) ? 0xffffff : 0);
    }
}
