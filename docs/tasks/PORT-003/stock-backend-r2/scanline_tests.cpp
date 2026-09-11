// Original packed scanline/Copper/decorator execution, with caller-owned rows.
// Deliberately quiescent: this fixture does not claim concurrent native access.
#include <array>
#include <cstdio>
#include <cstring>
#include <type_traits>
#include "canvas.h"
#include "extender/display/stock_scanline.hpp"

namespace {
constexpr int W = 64, H = 16;
int checks = 0, failures = 0;
void check(bool ok, int depth, char const *name) {
  ++checks; if (!ok) ++failures;
  std::printf("%s VGA%d %s\n", ok ? "PASS" : "FAIL", depth, name);
}
template<class Depth> struct Probe : agon::extender::display::StockScanlineController<Depth> {
  fabgl::RGB888 color(int i) {
    if constexpr (std::is_same_v<Depth, fabgl::VGA64Controller>)
      return fabgl::RGB888((i & 3) * 85, ((i >> 2) & 3) * 85, ((i >> 4) & 3) * 85);
    else return fabgl::RGB888(this->m_palette[i].R * 85, this->m_palette[i].G * 85, this->m_palette[i].B * 85);
  }
  fabgl::Sprite *mouse() { return this->mouseCursor(); }
  using fabgl::VGAPalettedController::swapBuffers;
};
int packed(fabgl::RGB888 c) { return (c.R >> 6) | ((c.G >> 6) << 2) | ((c.B >> 6) << 4); }

template<class Depth> void exercise(int depth) {
  Probe<Depth> c; c.begin(); c.enableBackgroundPrimitiveExecution(false);
  c.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync", W, H);
  fabgl::Canvas cv(&c);
  for (int y = 0; y < H; ++y) for (int x = 0; x < W; ++x)
    cv.setPixel(x, y, c.color((x + y * 3) % depth));
  alignas(8) std::array<std::uint8_t, W + 16> signal;
  std::array<std::uint8_t, W> row;
  auto render = [&](int y) {
    signal.fill(0x5a);
    c.prepareStockRowQuiescent(y, signal.data() + 8);
    c.normalizeRow(signal.data() + 8, row.data(), W);
    bool guards = true;
    for (int i = 0; i < 8; ++i) guards &= signal[i] == 0x5a && signal[W + 8 + i] == 0x5a;
    return guards;
  };
  bool base = true, guards = true;
  for (int y = 0; y < H; ++y) {
    guards &= render(y);
    for (int x = 0; x < W; ++x) base &= row[x] == packed(c.color((x + y * 3) % depth));
  }
  check(base, depth, "original packed row expansion and RGB222 normalization");
  check(guards, depth, "output row allocation boundaries");
  if (depth < 64) {
    c.createPalette(17);
    for (int i = 0; i < depth; ++i) c.setItemInPalette(17, i, fabgl::RGB888(255, 0, 0));
    std::uint16_t list[] = {0, 17, 3, 0, 5, 17, 8, 0};
    c.updateSignalList(list, 4);
    bool copper = true;
    for (int repeat = 0; repeat < 2; ++repeat) for (int y = 0; y < H; ++y) {
      render(y);
      for (int x = 0; x < W; ++x)
        copper &= row[x] == (y >= 3 && y < 8 ? 3 : packed(c.color((x + y * 3) % depth)));
    }
    check(copper, depth, "Copper zero span, boundaries, final span and frame restart");
    auto rgb = cv.getPixel(9, 4);
    check(packed(rgb) == packed(c.color((9 + 4 * 3) % depth)), depth, "readback retains palette zero beneath Copper");
    // Delete a specific palette using the original path, not the known-problem
    // delete-all iteration. No upstream fix is selected by this fixture.
    c.deletePalette(17); render(0); render(4);
    check(row[9] == packed(c.color((9 + 4 * 3) % depth)), depth, "deleted palette's spans return to palette zero");
    std::uint16_t normal[] = {0, 0}; c.updateSignalList(normal, 1);
  }
  std::uint8_t white = 0xff, red = 0xc3, blue = 0xf0;
  fabgl::Bitmap textBitmap(1, 1, &white, fabgl::PixelFormat::RGBA2222);
  fabgl::Bitmap spriteBitmap(1, 1, &red, fabgl::PixelFormat::RGBA2222);
  fabgl::Bitmap mouseBitmap(1, 1, &blue, fabgl::PixelFormat::RGBA2222);
  fabgl::Sprite text, sprite;
  text.addBitmap(&textBitmap); text.moveTo(10, 5); text.visible = true; text.hardware = true;
  text.paintOptions.mode = fabgl::PaintMode::XOR;
  c.setTextCursor(&text); render(0); render(5);
  check(row[10] == (packed(c.color((10 + 5 * 3) % depth)) ^ 63), depth, "original text cursor XOR");
  sprite.addBitmap(&spriteBitmap); sprite.moveTo(10, 5); sprite.visible = true; sprite.hardware = true;
  c.setSprites(&sprite, 1); render(0); render(5);
  check(row[10] == 3, depth, "hardware sprite follows text cursor");
  c.mouse()->addBitmap(&mouseBitmap); c.mouse()->moveTo(10, 5); c.mouse()->visible = true;
  render(0); render(5);
  check(row[10] == 48, depth, "mouse follows hardware sprite");
  c.mouse()->visible = false; c.mouse()->clearBitmaps();
  c.removeSprites(); c.setTextCursor(nullptr);
  render(0); render(5);
  check(row[10] == packed(c.color((10 + 5 * 3) % depth)), depth, "decorators leave native framebuffer unchanged");
  c.end();
}
} // namespace

int main() {
  exercise<fabgl::VGA2Controller>(2); exercise<fabgl::VGA4Controller>(4);
  exercise<fabgl::VGA8Controller>(8); exercise<fabgl::VGA16Controller>(16);
  exercise<fabgl::VGA64Controller>(64);
  std::printf("Stock scanline comparisons: %d checks, %d failures\n", checks, failures);
  return failures != 0;
}
