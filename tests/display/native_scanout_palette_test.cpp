// Link the stock service and controllers to the C DMA handoff fixture.
// Observe the tagged slot before every modeled DMA retirement, including
// interrupts that arrive inside the worker's penultimate-block wait.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
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
static unsigned first_live;
static bool black_image;
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
      if (frame >= first_live && !black_image && x >= left && x < left + 640) {
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

#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
static agon_native_trace_t saved{};

static void check_saved_trace() {
  agon_native_trace_t trace{};
  assert(agon_native_get_startup_trace(&trace));
  assert(std::memcmp(&saved, &trace, sizeof(trace)) == 0);
}
#endif

extern "C" void palette_frame_complete(unsigned completed) {
  // At the first successful rearm the P4 permits mode preparation/binding.
  assert(hdmiOutput().emitFrame() == (completed > 1));
  assert(uint32_t(frame_counter) == completed - 1);
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
  // Called by the generated DMA callback after it has reselected the list
  // and enabled the channel. Keep the exact first receipt for the next mode.
  if (saved.epoch) {
    check_saved_trace();
  } else if (completed < first_live) {
    agon_native_trace_t unseen{};
    assert(!agon_native_get_startup_trace(&unseen));
  } else {
    assert(completed == first_live && agon_native_get_startup_trace(&saved));
    assert(saved.epoch == 1 && saved.target_armed && saved.target_frame == first_live);
    assert(saved.site == NR_SITE_REARM && saved.rearmed && !saved.fault);
    assert(saved.retired == carrier_height / strip_rows);
    assert(saved.slot_frame == first_live && saved.slot_block == 0 && saved.slot_ready);
    assert(saved.row_cursor == ((unsigned(NR_ROW_EXPAND) << 16) | (strip_rows / scale - 1)));
    const auto *stamp = saved.stamp;
    assert(nr_admission(saved.row_cursor, stamp) == NR_ADMIT_LIVE && saved.limit_us == 1600);
    assert(stamp[NR_T_RETIRE_12] == 0 && stamp[NR_T_CACHE_SKIP] == UINT32_MAX);
    assert(stamp[NR_T_RENDER_BEGIN] <= stamp[NR_T_RENDER_END]);
    assert(stamp[NR_T_RENDER_END] <= stamp[NR_T_CACHE_BEGIN]);
    assert(stamp[NR_T_CACHE_BEGIN] < stamp[NR_T_CACHE_END]);
    assert(stamp[NR_T_CACHE_END] <= stamp[NR_T_PUBLISHED] && stamp[NR_T_PUBLISHED] <= saved.limit_us);
    assert(stamp[NR_T_PUBLISHED] <= stamp[NR_T_DECISION] && stamp[NR_T_DECISION] != UINT32_MAX);
  }
#endif
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
    assert(!setup_locked.load() && "native row attempted during palette setup");
    Base::traceNativeRow(y,rewind,row,cursor);
  }
#endif
};

template<class Depth, size_t N>
static void exercise(const uint8_t (&palette)[N], unsigned factor, bool double_buffered,
                     unsigned live_frame, bool all_black) {
  colours = N;
  mode_palette = palette;
  scale = factor;
  first_live = live_frame;
  black_image = all_black;
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
      canvas.setBrushColor(colourLookup[palette[all_black ? 0 : pattern(x,y)]]);
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
  // Release the real mutex in the middle of the preceding black frame. The
  // row-zero latch must delay live pixels until the whole next frame.
  palette_dma_advance_to(first_live - 1,5);
  palette_dma_check_black_hold();
  resume.set_value();
  setup.get();
  palette_dma_advance_to(5,0);
  for (auto count : checked_pixels) assert(count == carrier_width*carrier_height);
  service.detach();
  palette_dma_stop();
  controller.end();
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
  check_saved_trace();  // Includes unbind, worker join, slot free and controller teardown.
#endif
  std::printf("PASS %ux%u/%zu %s at %ux%u: first live frame %u (%s). "
              "Checked all %u BGR pixels per frame, including borders, across five frames (%ux).\n",
              width,height,N,double_buffered?"double":"single",carrier_width,carrier_height,first_live,
              all_black?"all black":"tiles",checked_pixels[first_live],factor);
}

int main(int argc, char **argv) {
  assert(argc == 2);
  const unsigned first = std::atoi(argv[1]);
  assert(first >= 2 && first <= 4);
  if (first == 4) {
    exercise<fabgl::VGA4Controller>(defaultPalette04,2,true,first,false);
    exercise<fabgl::VGA16Controller>(defaultPalette10,1,false,2,false);
  } else {
    exercise<fabgl::VGA16Controller>(defaultPalette10,1,false,first,first == 3);
    exercise<fabgl::VGA4Controller>(defaultPalette04,2,true,4,false);
  }
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
  std::printf("PASS epoch 1 frame %u block 0: published after %u modeled us, rearmed at %u; "
              "identical sealed bytes through mode and panel replacement.\n",
              saved.target_frame,saved.stamp[NR_T_PUBLISHED],saved.stamp[NR_T_DECISION]);
#endif
}
