// Standalone type scaffold around an unchanged FabGL scanline function.
// This does not reproduce the complete Sprite lifecycle or claim ABI equivalence.
#include <stdint.h>
#include <algorithm>
#include "esp_attr.h"
#include "stock_sprite_probe.h"
#include "nurples_art.h"
namespace strip_fabgl {
enum class PixelFormat { RGBA8888, RGBA2222 };
enum class PaintMode { SET, XOR };
struct Bitmap { int width, height; PixelFormat format; const uint8_t *data; };
struct Sprite {
    int x, y; Bitmap *frame;
    struct { PaintMode mode = PaintMode::SET; } paintOptions;
    Bitmap *getFrame() { return frame; }
};
class VGAPalettedController {
    uint8_t m_HVSync = 0;
public:
    void rawDrawSpriteScanline(uint8_t *, Sprite *, int, int, int);
};
#include "stock_sprite_body.inc"
}
extern "C" unsigned stock_probe_population(unsigned frame) {
    static const unsigned populations[] = {1, 8, 16, 32};
    return populations[std::min(frame / 600, 3u)];
}
extern "C" void stock_probe_compose(uint8_t *strip, unsigned first_y,
                                    unsigned rows, unsigned frame) {
    using namespace strip_fabgl;
    const unsigned count = stock_probe_population(frame);
    Bitmap images[4]; Sprite sprites[32];
    for (unsigned i = 0; i < 4; ++i)
        images[i] = {16, 16, PixelFormat::RGBA2222, nurples_art[i]};
    for (unsigned i = 0; i < count; ++i) {
        sprites[i].x = (frame * 2 + i * 37) % (512 - 16);
        sprites[i].y = (frame + i * 23) % (384 - 16);
        sprites[i].frame = &images[i % 4];
    }
    VGAPalettedController painter;
    alignas(8) uint8_t signal[512];
    for (unsigned row = 0; row < rows; ++row) {
        int y = first_y + row - 48;
        if (y < 0 || y >= 384) continue;
        bool covered = false;
        for (unsigned i = 0; i < count; ++i)
            covered |= y >= sprites[i].y && y < sprites[i].y + 16;
        if (!covered) continue;
        uint8_t *pixels = strip + row * 848 * 3 + 168 * 3;
        // Only sprite-covered spans need the RGB888/RGB222 adapter.
        // Initialize every span BEFORE any draw, preserving overlap and XOR.
        // Expanding repeated overlapping spans is harmless: all draws are done.
        for (unsigned i = 0; i < count; ++i) {
            if (y < sprites[i].y || y >= sprites[i].y + 16) continue;
            for (int x = sprites[i].x; x < sprites[i].x + 16; ++x)
                signal[x ^ 2] = (pixels[x*3] >> 6 << 4) |
                                (pixels[x*3+1] >> 6 << 2) | (pixels[x*3+2] >> 6);
        }
        for (unsigned i = 0; i < count; ++i)
            painter.rawDrawSpriteScanline(signal, &sprites[i], y, 512, 384);
        for (unsigned i = 0; i < count; ++i) {
            if (y < sprites[i].y || y >= sprites[i].y + 16) continue;
            for (int x = sprites[i].x; x < sprites[i].x + 16; ++x) {
                uint8_t p = signal[x ^ 2];
                pixels[x*3] = ((p >> 4) & 3) * 85;
                pixels[x*3+1] = ((p >> 2) & 3) * 85;
                pixels[x*3+2] = (p & 3) * 85;
            }
        }
    }
}
