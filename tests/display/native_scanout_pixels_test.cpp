// Compare the real stock paletted row routines + P4 strip producer against
// independent full logical rasters captured in stock row order. No timing oracle.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "canvas.h"
#include "extender/display/stock_scanline.hpp"
#include "extender/display/native_row_composer.hpp"

using agon::extender::display::NativeRowComposer;

template<class Depth> class TestController : public agon::extender::display::StockScanlineController<Depth> {
 public:
  using fabgl::VGAPalettedController::swapBuffers;
};

template<class Depth>
void exercise(int colours, int width, int height, int carrier_width, int carrier_height,
              bool double_buffer, bool copper) {
  TestController<Depth> controller;
  controller.begin();
  controller.enableBackgroundPrimitiveExecution(false);
  char modeline[160];
  std::snprintf(modeline, sizeof(modeline), "\"%dx%d\" 1 %d %d %d %d %d %d %d %d -HSync -VSync",
                width, height, width, width+4, width+8, width+16, height, height+2, height+4, height+8);
  controller.setResolution(modeline, width, height, double_buffer);
  assert(controller.getViewPortWidth() == width && controller.getViewPortHeight() == height);
  fabgl::Canvas canvas(&controller);
  NativeRowComposer producer;
  assert(producer.configure(width, height, carrier_width, carrier_height));
  const int strip_height = 32, strip_bytes = carrier_width * strip_height * 3;
  std::array<std::vector<uint8_t>,3> slots;
  std::array<bool,3> slot_black{}; // All slots initially contain another geometry.
  for (auto &slot : slots) slot.assign(strip_bytes + 32, 0xb5);
  alignas(8) std::array<uint8_t,NativeRowComposer::maximum_width> signal{};
  std::vector<uint8_t> reference(width * height);
  std::array<uint8_t,4> sprite_data{0xc3,0xff,0xcc,0xf0};
  fabgl::Bitmap bitmap(2, 2, sprite_data.data(), fabgl::PixelFormat::RGBA2222);
  fabgl::Sprite sprite;
  sprite.addBitmap(&bitmap); sprite.hardware = true; sprite.visible = true;
  sprite.moveTo(width / 2, height / 2);
  controller.setSprites(&sprite, 1);
  if (copper) {
    controller.createPalette(17);
    for (int entry = 0; entry < colours; ++entry)
      controller.setItemInPalette(17, entry, fabgl::RGB888(255, (entry & 3)*85, 0));
    std::uint16_t list[]{0,17,5,0,53,17,144,0,205,17};
    controller.updateSignalList(list, 5);
  }
  const int rx = width == 320 && height == 240 ? 2 : 1;
  const int ry = height == 240 && (width == 320 || width == 640) ? 2 : 1;
  const int left = (carrier_width - width * rx) / 2;
  const int top = (carrier_height - height * ry) / 2;
  unsigned long long checked = 0;
  for (int frame = 0; frame < 2; ++frame) {
    canvas.setBrushColor(frame ? fabgl::Color::BrightWhite : fabgl::Color::Black);
    canvas.clear();
    for (int y = 0; y < height; ++y)
      for (int x = y % 7; x < width; x += 7)
        canvas.setPixel(x, y, fabgl::RGB888((x & 3)*85, (y & 3)*85, ((x ^ y) & 3)*85));
    if (double_buffer) controller.swapBuffers();
    for (int y = 0; y < height; ++y) {
      controller.prepareStockRowQuiescent(y, signal.data());
      for (int x = 0; x < width; ++x) reference[y*width+x] = signal[x^2] & 63;
    }
    int previous_y = -1, sampled = 0;
    for (int y0 = 0; y0 < carrier_height; y0 += strip_height) {
      const auto slot = (y0 / strip_height) % 3;
      uint8_t *pixels = slots[slot].data() + 16;
      const bool rendered = producer.fill(pixels, y0, strip_height, slot, slot_black[slot],
        [&](int y, bool first_cropped, uint8_t *row) {
          assert(previous_y < 0 || y == previous_y+1);
          if (first_cropped) controller.rewindCroppedScanline();
          controller.prepareStockRowQuiescent(y, row);
          ++sampled; previous_y = y;
        });
      assert(rendered);
      for (int row = 0; row < strip_height; ++row) {
        for (int x = 0; x < carrier_width; ++x) {
          const int xx = x-left, yy = y0+row-top;
          const uint8_t c = xx>=0 && xx<width*rx && yy>=0 && yy<height*ry
              ? reference[(yy/ry)*width+xx/rx] : 0;
          const auto *p = pixels+3*(row*carrier_width+x);
          assert(p[0]==(c>>4)*85 && p[1]==((c>>2)&3)*85 && p[2]==(c&3)*85);
          ++checked;
        }
      }
      assert(std::all_of(slots[slot].begin(),slots[slot].begin()+16,[](uint8_t b){return b==0xb5;}));
      assert(std::all_of(slots[slot].end()-16,slots[slot].end(),[](uint8_t b){return b==0xb5;}));
    }
    assert(sampled == std::min(height, carrier_height / ry));
  }
  std::printf("PASS %dx%d/%d %s -> %dx%d, %llu RGB pixels, two frames\n",
              width,height,colours,double_buffer?"double":"single",carrier_width,carrier_height,checked);
  controller.removeSprites();
  controller.end();
}

// A nonzero sentinel in a range promised already black makes an otherwise
// invisible duplicate zero store observable. Exercise the dirty path with the
// real old pixels from the preceding geometry on the same physical slots.
void borderOwnership() {
  constexpr unsigned rows = 32;
  constexpr unsigned width = 684;
  constexpr unsigned height = 384;
  constexpr unsigned bytes = rows * width * 3;
  constexpr uint8_t sentinel = 0xc7;
  std::array<std::vector<uint8_t>, 3> pixels;
  std::array<bool, 3> black{true, true, true};
  NativeRowComposer composer;
  auto white = [](int, bool, uint8_t *signal) { std::fill_n(signal, 512, 63); };
  assert(composer.configure(512, 384, width, height));
  unsigned untouched = 0;
  for (unsigned slot = 0; slot < 3; ++slot) {
    pixels[slot].assign(bytes, sentinel);
    assert(composer.fill(pixels[slot].data(), slot * rows, rows, slot, black[slot], white));
    assert(!black[slot]);
    for (unsigned y = 0; y < rows; ++y) {
      for (unsigned x = 0; x < width; ++x) {
        const bool border = x < 86 || x >= 86 + 512;
        const auto *pixel = pixels[slot].data() + (y * width + x) * 3;
        for (unsigned c = 0; c < 3; ++c) {
          assert(pixel[c] == (border ? sentinel : 255));
          if (border) ++untouched;
        }
      }
    }
  }
  assert(untouched == 3 * rows * (width - 512) * 3);

  // None of the three slots has had time to become idle/blank. For the
  // incoming 320x200 mode, the first 92 physical rows must be fully cleared.
  assert(composer.configure(320, 200, width, height));
  for (unsigned slot = 0; slot < 3; ++slot) {
    assert(composer.fill(pixels[slot].data(), slot * rows, rows, slot, black[slot], white));
    assert(black[slot] == (slot < 2));
    for (unsigned y = 0; y < rows; ++y) {
      for (unsigned x = 0; x < width; ++x) {
        const bool inside = slot * rows + y >= 92 && x >= 182 && x < 182 + 320;
        const auto *pixel = pixels[slot].data() + (y * width + x) * 3;
        for (unsigned c = 0; c < 3; ++c) assert(pixel[c] == (inside ? 255 : 0));
      }
    }
  }
  std::printf("PASS first clean 512x384 bind skipped %u border-byte stores, dirty 320x200 same-carrier rebind cleared only residual image/borders\n", untouched);
}

#include "native_scanout_overlay_fixture.hpp"

int main() {
  exerciseOverlayMarkers(320,240,848,480);
  exerciseOverlayMarkers(512,384,684,384);
  borderOwnership();
  for (bool doubled : {false,true}) {
    exercise<fabgl::VGA2Controller>(2,320,240,848,480,doubled,true);
    exercise<fabgl::VGA4Controller>(4,320,240,848,480,doubled,true);
    exercise<fabgl::VGA16Controller>(16,320,240,848,480,doubled,true);
    exercise<fabgl::VGA64Controller>(64,320,240,848,480,doubled,false);
  }
  exercise<fabgl::VGA64Controller>(64,512,384,684,384,false,false);
  exercise<fabgl::VGA16Controller>(16,640,240,848,480,false,true);
  exercise<fabgl::VGA16Controller>(16,320,200,684,384,true,true);
  exercise<fabgl::VGA16Controller>(16,1024,768,848,480,false,true);
  exercise<fabgl::VGA4Controller>(4,640,512,848,480,true,true);
  exercise<fabgl::VGA4Controller>(4,640,256,684,384,true,true);
  exercise<fabgl::VGA16Controller>(16,640,480,848,480,false,true);
}
