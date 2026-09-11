// R1 comparison of real stock classes with original accessors applied to an
// independent logical image. No P4 generic controller or pixel codec is linked.
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstring>
#include <vector>
#include <type_traits>
#include "canvas.h"
#include "dispdrivers/vga2controller.h"
#include "dispdrivers/vga4controller.h"
#include "dispdrivers/vga8controller.h"
#include "dispdrivers/vga16controller.h"
#include "dispdrivers/vga64controller.h"
#include "oracle.hpp"

namespace {
constexpr int W = 64, H = 16;
int failures = 0, checks = 0;
void check(bool ok, int depth, char const *operation) {
  ++checks;
  if (!ok) ++failures;
  std::printf("%s VGA%d %s\n", ok ? "PASS" : "FAIL", depth, operation);
}
template<class Base> struct Probe : Base {
  using fabgl::VGAPalettedController::swapBuffers;
  std::uint8_t *visible(int y) { return (std::uint8_t *)this->m_viewPortVisible[y]; }
  fabgl::RGB888 color(int i) {
    if constexpr (std::is_same_v<Base, fabgl::VGA64Controller>)
      return fabgl::RGB888((i & 3) * 85, ((i >> 2) & 3) * 85, ((i >> 4) & 3) * 85);
    else return fabgl::RGB888(this->m_palette[i].R * 85, this->m_palette[i].G * 85, this->m_palette[i].B * 85);
  }
};
using Image = std::array<int, W * H>;

void encode(int depth, std::uint8_t *row, int x, int value, int sync) {
  using namespace stock_oracle;
  switch (depth) {
    case 2: VGA2_SETPIXELINROW(row, x, value); break;
    case 4: VGA4_SETPIXELINROW(row, x, value); break;
    case 8: VGA8_SETPIXELINROW(row, x, value); break;
    case 16: VGA16_SETPIXELINROW(row, x, value); break;
    case 64: VGA_PIXELINROW(row, x) = value | sync; break;
  }
}
int stride(int depth) { return depth == 64 ? W : W * (depth == 2 ? 1 : depth == 4 ? 2 : depth == 8 ? 3 : 4) / 8; }

template<class C> void compare(C &c, Image const &expected, int depth, char const *name) {
  // Four spare oracle bytes permit the original PAL8 32-bit access over the
  // final 24-bit group. Actual controller allocation remains upstream's own.
  std::vector<std::uint8_t> row(stride(depth) + 4);
  bool equal = true;
  for (int y = 0; y < H; ++y) {
    std::fill(row.begin(), row.end(), 0);
    for (int x = 0; x < W; ++x) encode(depth, row.data(), x, expected[y * W + x], c.createBlankRawPixel());
    if (std::memcmp(row.data(), c.getScanline(y), stride(depth))) {
      if (equal) {
        std::printf("Mismatch VGA%d %s row %d expected/actual:", depth, name, y);
        for (int b = 0; b < stride(depth); ++b)
          std::printf(" %02x/%02x", row[b], c.getScanline(y)[b]);
        std::puts("");
      }
      equal = false;
    }
  }
  check(equal, depth, name);
}

template<class C> void seed(C &c, fabgl::Canvas &cv, Image &im, int depth) {
  cv.reset();
  for (int y = 0; y < H; ++y) for (int x = 0; x < W; ++x) {
    im[y * W + x] = (x + y * 3) % depth;
    cv.setPixel(x, y, c.color(im[y * W + x]));
  }
}

void scroll(Image &im, int x1, int y1, int x2, int y2, int dx, int dy, int bg) {
  Image before = im;
  for (int y = y1; y <= y2; ++y) for (int x = x1; x <= x2; ++x) {
    int sx = x - dx, sy = y - dy;
    im[y * W + x] = sx >= x1 && sx <= x2 && sy >= y1 && sy <= y2 ? before[sy * W + sx] : bg;
  }
}

template<class Base> void exercise(int depth) {
  Probe<Base> c;
  c.begin();
  c.enableBackgroundPrimitiveExecution(false);
  c.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync", W, H, false);
  check(c.getViewPortWidth() == W && c.getViewPortHeight() == H, depth, "dimensions");
  fabgl::Canvas cv(&c);
  Image im{};
  seed(c, cv, im, depth);
  compare(c, im, depth, "packed pixels across groups");
  check(c.visible(0) == c.getScanline(0), depth, "single-buffer alias");
  if (depth == 8) {
    std::uint8_t golden[] = {0x77, 0x39, 0x05};
    check(!std::memcmp(c.getScanline(0), golden, 3), depth, "stock 01234567 bytes 773905");
  }
  if (depth == 64) {
    std::uint8_t golden[] = {0xc2, 0xc3, 0xc0, 0xc1};
    check(!std::memcmp(c.getScanline(0), golden, 4), depth, "stock sync bits and x XOR 2 lanes");
  }
  for (int bg : {0, depth - 1}) {
    cv.setBrushColor(c.color(bg)); cv.clear(); im.fill(bg);
    compare(c, im, depth, "clear/fill");
  }
  // Exercise all stock paint selections using the real row-paint path.
  const fabgl::PaintMode modes[] = {fabgl::PaintMode::Set, fabgl::PaintMode::OR, fabgl::PaintMode::AND,
    fabgl::PaintMode::XOR, fabgl::PaintMode::Invert, fabgl::PaintMode::NoOp, fabgl::PaintMode::ANDNOT, fabgl::PaintMode::ORNOT};
  for (auto mode : modes) {
    seed(c, cv, im, depth); int paint = depth - 1;
    fabgl::PaintOptions options; options.mode = mode;
    cv.setPaintOptions(options);
    cv.setPenColor(c.color(paint)); cv.drawLine(3, 5, 57, 5);
    for (int x = 3; x <= 57; ++x) {
      auto &v = im[5 * W + x];
      switch (mode) {
        case fabgl::PaintMode::Set: v = paint; break;
        case fabgl::PaintMode::OR: v |= paint; break;
        case fabgl::PaintMode::AND: v &= paint; break;
        case fabgl::PaintMode::XOR: v ^= paint; break;
        case fabgl::PaintMode::Invert: v ^= depth - 1; break;
        case fabgl::PaintMode::NoOp: break;
        case fabgl::PaintMode::ANDNOT: v &= ~paint; break;
        case fabgl::PaintMode::ORNOT: v |= (~paint & (depth - 1)); break;
      }
    }
    char label[40]; std::snprintf(label, sizeof(label), "paint selection %u", unsigned(mode));
    compare(c, im, depth, label);
  }
  // Full-width scrolling must change row-table order, not copy logical rows.
  for (int dy : {-3, 3}) {
    seed(c, cv, im, depth); auto row = c.getScanline(dy < 0 ? 3 : 0);
    cv.setBrushColor(c.color(depth - 1)); cv.setScrollingRegion(0, 0, W - 1, H - 1); cv.scroll(0, dy);
    scroll(im, 0, 0, W - 1, H - 1, 0, dy, depth - 1);
    compare(c, im, depth, "full-width VScroll");
    check(c.getScanline(dy < 0 ? 0 : 3) == row, depth, "VScroll permutes row pointers");
  }
  for (bool aligned : {true, false}) for (int delta : {-3, 3}) for (bool vertical : {true, false}) {
    seed(c, cv, im, depth);
    int x1 = aligned ? 8 : 3, x2 = aligned ? 55 : 58;
    cv.setBrushColor(c.color(depth - 1)); cv.setScrollingRegion(x1, 2, x2, 13);
    cv.scroll(vertical ? 0 : delta, vertical ? delta : 0);
    scroll(im, x1, 2, x2, 13, vertical ? 0 : delta, vertical ? delta : 0, depth - 1);
    char label[100];
    std::snprintf(label, sizeof(label), "%s partial viewport %s scroll %+d; outside preserved",
      aligned ? "aligned" : "unaligned", vertical ? "vertical" : "horizontal", delta);
    compare(c, im, depth, label);
  }
  for (int offset : {-3, 3}) {
    seed(c, cv, im, depth); Image before = im;
    cv.copyRect(8, 4, 8 + offset, 4 + offset, 40, 8);
    for (int y = 0; y < 8; ++y) for (int x = 0; x < 40; ++x)
      im[(4 + offset + y) * W + 8 + offset + x] = before[(4 + y) * W + 8 + x];
    compare(c, im, depth, "overlapping copyRect");
  }
  // Nurples-shaped case: 96x32 bitmap through a 46x1 inclusive viewport.
  seed(c, cv, im, depth);
  std::vector<std::uint8_t> bitmap(96 * 32, 0xff);
  fabgl::Bitmap bm(96, 32, bitmap.data(), fabgl::PixelFormat::RGBA2222);
  cv.setClippingRect(fabgl::Rect(9, 0, 54, 0)); cv.drawBitmap(-11, -7, &bm);
  for (int x = 9; x <= 54; ++x) im[x] = depth - 1;
  compare(c, im, depth, "oversized bitmap in one-row viewport");
  // Native software-sprite background/readback representation is not the
  // physical packed row. Public capture is always opaque RGBA2222.
  cv.reset(); std::vector<std::uint8_t> capture(W * H);
  fabgl::Bitmap captured(W, H, capture.data(), fabgl::PixelFormat::RGBA2222);
  cv.copyToBitmap(0, 0, &captured);
  bool captureOK = true;
  for (int i = 0; i < W * H; ++i) {
    auto rgb = c.color(im[i]);
    auto expected = 0xc0 | ((rgb.B / 85) << 4) | ((rgb.G / 85) << 2) | (rgb.R / 85);
    captureOK &= capture[i] == expected;
  }
  check(captureOK, depth, "public RGBA2222 capture");
  seed(c, cv, im, depth);
  std::uint8_t glyph[] = {0x81, 0x42, 0x24, 0x18};
  cv.setPenColor(c.color(depth - 1));
  cv.drawGlyph(5, 4, 8, 4, glyph);
  for (int y = 0; y < 4; ++y) for (int x = 0; x < 8; ++x)
    if (glyph[y] & (0x80 >> x)) im[(y + 4) * W + x + 5] = depth - 1;
  compare(c, im, depth, "glyph through native pixel path");
  seed(c, cv, im, depth);
  std::vector<std::uint8_t> square(6 * 4, 0xff);
  fabgl::Bitmap small(6, 4, square.data(), fabgl::PixelFormat::RGBA2222);
  float identity[] = {1, 0, 0, 0, 1, 0, 0, 0, 1};
  cv.drawTransformedBitmap(7, 6, &small, identity, identity);
  for (int y = 6; y < 10; ++y) for (int x = 7; x < 13; ++x) im[y * W + x] = depth - 1;
  compare(c, im, depth, "transformed bitmap in task context");
  seed(c, cv, im, depth);
  fabgl::Sprite sprite; sprite.addBitmap(&small); sprite.moveTo(7, 6);
  sprite.visible = true; sprite.hardware = false;
  c.setSprites(&sprite, 1);
  bool backgroundOK = sprite.savedBackground && sprite.savedBackgroundWidth == 6 && sprite.savedBackgroundHeight == 4;
  if (backgroundOK) for (int y = 0; y < 4; ++y) for (int x = 0; x < 6; ++x) {
    int native = im[(6 + y) * W + 7 + x];
    if (depth == 64) native |= c.createBlankRawPixel();
    backgroundOK &= sprite.savedBackground[y * 6 + x] == native;
  }
  check(backgroundOK, depth, "software-sprite native byte-per-pixel background");
  c.removeSprites();
  compare(c, im, depth, "software-sprite native background restoration");
  // No output worker exists in R1. Invoke the original protected swap body
  // directly to compare plane identities, without claiming asynchronous fences.
  c.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync", W, H, true);
  auto drawing = c.getScanline(0), visible = c.visible(0);
  check(drawing != visible, depth, "double-buffer distinct planes");
  c.swapBuffers();
  check(c.getScanline(0) == visible && c.visible(0) == drawing, depth, "original swap exchanges planes");
  c.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync", 63, 15, false);
  check(c.getViewPortWidth() == 48 && c.getViewPortHeight() == 12, depth, "original width/height quanta");
  c.end();
  std::printf("VGA%d completed\n", depth);
}
} // namespace

int main() {
  exercise<fabgl::VGA2Controller>(2); exercise<fabgl::VGA4Controller>(4);
  exercise<fabgl::VGA8Controller>(8); exercise<fabgl::VGA16Controller>(16);
  exercise<fabgl::VGA64Controller>(64);
  std::printf("Native-row comparisons: %d checks, %d failures\n", checks, failures);
  return failures ? 1 : 0;
}
