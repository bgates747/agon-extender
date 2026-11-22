// Link the stock service and controllers to the C DMA handoff fixture.
// Observe the tagged slot before every modeled DMA retirement, including
// interrupts that arrive inside the worker's penultimate-block wait.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <future>
#include <mutex>
#include "canvas.h"
#include "extender/display/stock_p4_service.hpp"
#include "extender/display/hdmi_output.hpp"
using fabgl::RGB888;
#include "agon_palette.h"

using namespace agon::extender::display;
static constexpr unsigned carrier_width = 848, carrier_height = 480, strip_rows = 32;
static unsigned colours, scale, checked_pixels[5];
static const uint8_t *mode_palette;
static StockFrameCounter frame_counter;
static std::atomic<bool> setup_locked{};

static unsigned pattern(unsigned x, unsigned y) {
  // Offset both axes and use an odd-sized tile to expose half-pixel shifts in 2x output.
  return (1 + x / 13 + y / 7) % colours;
}

extern "C" void palette_check_strip(unsigned frame, unsigned block, const uint8_t *pixels) {
  assert(frame < 5 && checked_pixels[frame] == block * strip_rows * carrier_width);
  const unsigned left = (carrier_width - 640) / 2;
  for (unsigned row = 0; row < strip_rows; ++row) {
    for (unsigned x = 0; x < carrier_width; ++x) {
      uint8_t physical = 0;
      if (frame == 4 && x >= left && x < left + 640) {
        const unsigned y = block * strip_rows + row;
        physical = mode_palette[pattern((x-left) / scale, y / scale)];
      }
      // Agon palette IDs encode 2-bit R,G,B in bits 5..0. The DSI slot uses B,G,R bytes.
      assert(pixels[0] == (physical & 3) * 85);
      assert(pixels[1] == ((physical >> 2) & 3) * 85);
      assert(pixels[2] == (physical >> 4) * 85);
      pixels += 3;
      ++checked_pixels[frame];
    }
  }
}

extern "C" void palette_frame_complete(unsigned completed) {
  // At the first successful rearm the P4 permits mode preparation/binding.
  assert(hdmiOutput().emitFrame() == (completed > 1));
  assert(uint32_t(frame_counter) == completed - 1);
}

template<class Depth> struct Controller : StockBoundController<Depth> {
  using fabgl::VGAPalettedController::swapBuffers;
  using Base = StockBoundController<Depth>;
  void prepareRow(int y, uint8_t *row) override {
    assert(!setup_locked.load() && "native row attempted during palette setup");
    Base::prepareRow(y,row);
  }
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
  void traceNativeRow(int y, bool rewind, uint8_t *row, uint32_t *cursor) override {
    if (setup_locked.load())
      std::fprintf(stderr,"frame 2 block 0 attempted source row %d while setup owns stockNativeMutex()\n",y);
    assert(!setup_locked.load() && "native row attempted during palette setup");
    Base::traceNativeRow(y,rewind,row,cursor);
  }
#endif
};

template<class Depth, size_t N>
static void exercise(const uint8_t (&palette)[N], unsigned factor, bool double_buffered) {
  colours = N;
  mode_palette = palette;
  scale = factor;
  frame_counter = 0;
  for (auto &count : checked_pixels) count = 0;
  const unsigned width = 640 / scale, height = carrier_height / scale;
  char modeline[128];
  std::snprintf(modeline,sizeof(modeline),"\"test\" 1 %u %u %u %u %u %u %u %u -HSync -VSync",
                width,width+4,width+8,width+16,height,height+2,height+4,height+8);
  palette_dma_start();
  palette_dma_advance_to(1,0);

  Controller<Depth> controller;
  controller.begin();
  controller.setResolution(modeline,width,height,double_buffered);
  assert(controller.getViewPortWidth() == int(width) && controller.getViewPortHeight() == int(height));
  controller.bindNativeAliases();
  controller.enableBackgroundPrimitiveExecution(false);
  auto install = [&] {
    for (size_t i = 0; i < N; ++i) controller.setPaletteItem(i,colourLookup[palette[i]]);
    controller.updateRGB2PaletteLUT();
  };
  install();
  fabgl::Canvas canvas(&controller);
  for (unsigned y = 0; y < height; y += 7) {
    for (unsigned x = 0; x < width; x += 13) {
      canvas.setBrushColor(colourLookup[palette[pattern(x,y)]]);
      canvas.fillRectangle(x,y,std::min(x+12,width-1),std::min(y+6,height-1));
    }
  }
  if (double_buffered) controller.swapBuffers();

  PresentationSnapshotPool metadata;
  StockP4Service service(metadata);
  assert(service.startClock() && service.prepare(controller));
  service.activate();
  std::promise<void> held, resume;
  auto setup = std::async(std::launch::async,[&] {
    {
      std::lock_guard lock(stockNativeMutex());
      setup_locked = true;
      // Make partial palette publication visible independently of the already painted image.
      controller.setPaletteItem(1, RGB888(0,0,255));
      held.set_value();
      resume.get_future().wait();
      install();
      setup_locked = false;
    }
    service.finishModeSetup();
  });
  held.get_future().wait();
  // Keep the real mutex across rearm into frames 2 and 3. Finish setup in
  // the middle of frame 3 after its top rows were filled in the old state.
  palette_dma_advance_to(3,5);
  resume.set_value();
  setup.get();
  palette_dma_advance_to(5,0);
  for (auto count : checked_pixels) assert(count == carrier_width*carrier_height);
  service.detach();
  palette_dma_stop();
  controller.end();
  std::printf("PASS %ux%u/%zu %s at %ux%u: frames 0,1 bootstrap black; 2,3 bound black; "
              "frame 4 all %u BGR pixels match independent tile oracle incl. borders (%ux). "
              "Public frame count %u.\n",width,height,N,double_buffered?"double":"single",
              carrier_width,carrier_height,checked_pixels[4],factor,uint32_t(frame_counter));
}

int main() {
  exercise<fabgl::VGA16Controller>(defaultPalette10,1,false);
  exercise<fabgl::VGA4Controller>(defaultPalette04,2,true);
}
