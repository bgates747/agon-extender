// Functional test of the actual service, queued native swap and frame counter.
// Only the physical HDMI sink and existing FreeRTOS host substrate are faked;
// forced worker barriers make the scheduling/lifetime cases reproducible.
#include <array>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <future>
#include <mutex>
#include <thread>
#include "canvas.h"
#include "extender/display/stock_p4_service.hpp"
#include "extender/display/hdmi_output.hpp"
#include "extender/display/mode_transaction.hpp"

using namespace agon::extender::display;
using namespace std::chrono_literals;

struct Barrier {
  std::mutex mutex;
  std::condition_variable condition;
  bool entered{}, released{};
  void hold() {
    std::unique_lock lock(mutex);
    entered = true;
    condition.notify_all();
    condition.wait(lock, [&] { return released; });
  }
  void awaitEntry() {
    std::unique_lock lock(mutex);
    assert(condition.wait_for(lock, 3s, [&] { return entered; }));
  }
  void release() {
    std::lock_guard lock(mutex);
    released = true;
    condition.notify_all();
  }
};

template<class Predicate> void await(Predicate predicate) {
  auto const deadline = std::chrono::steady_clock::now() + 3s;
  while (!predicate() && std::chrono::steady_clock::now() < deadline)
    std::this_thread::yield();
  assert(predicate());
}

struct Controller : StockBoundController<fabgl::VGA64Controller> {
  std::atomic<Barrier *> before_drain{};
  std::atomic<bool> drained{};
  std::size_t drain() override {
    if (auto barrier = before_drain.exchange(nullptr)) barrier->hold();
    auto const count = StockBoundController<fabgl::VGA64Controller>::drain();
    drained = true;
    return count;
  }
};

int main() {
  Controller controller;
  controller.begin();
  controller.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync",
                           64, 16, true);
  assert(controller.isViewPortAllocated() && controller.isDoubleBuffered());
  fabgl::Canvas canvas(&controller);
  Allocator allocator{nullptr,
      [](void *, std::size_t bytes) -> void * { return std::malloc(bytes); },
      [](void *, void *memory) { std::free(memory); }};
  StockP4Service service(allocator);
  assert(service.startClock() && service.attach(controller));
  StockFrameCounter counter;
  counter = 0;
  auto const old_generation = stockVisibleGeneration();

  Barrier draw, output;
  controller.before_drain = &draw;
  hdmiOutput().observer = [&](StockRuntimeController &source,
                              std::atomic<bool> &) {
    // A direct ISR output notification fails here while drawing is held.
    assert(controller.drained.load());
    assert(stockVisibleGeneration() == old_generation + 1);
    alignas(8) std::array<std::uint8_t, 64> signal{};
    source.prepareRow(2, signal.data());
    assert((signal[2 ^ 2] & 63) == 3); // the new front contains red
    output.hold();
    return true;
  };

  canvas.setPixel(2, 2, fabgl::RGB888(255, 0, 0));
  hdmi_test_enqueued = 0;
  auto swap = std::async(std::launch::async, [&] { canvas.swapBuffers(); });
  await([&] { return hdmi_test_enqueued.load() != 0; });
  assert(hdmiOutput().emitFrame());
  draw.awaitEntry();
  assert(std::uint32_t(counter) == 1);
  assert(hdmiOutput().emitFrame() && hdmiOutput().emitFrame());
  assert(std::uint32_t(counter) == 3);
  assert(hdmiOutput().publications == 0);
  draw.release();
  output.awaitEntry();
  assert(swap.wait_for(3s) == std::future_status::ready);
  swap.get();

  // A blocked sink never becomes the frame-clock owner.
  assert(hdmiOutput().emitFrame() && hdmiOutput().emitFrame());
  assert(std::uint32_t(counter) == 5);

  auto detach = std::async(std::launch::async, [&] { service.detach(); });
  await([&] { return !hdmiOutput().callbackBound(); });
  assert(!hdmiOutput().emitFrame());
  assert(std::uint32_t(counter) == 5);
  assert(detach.wait_for(20ms) == std::future_status::timeout);
  output.release();
  assert(detach.wait_for(3s) == std::future_status::ready);
  detach.get();
  assert(host_stale_notifications == 0);
  hdmiOutput().observer = {};

  // Panel mode stages a completed back BEFORE the next physical boundary.
  // No emitFrame is needed to reach the submission callback, and no parser
  // acknowledgment is allowed until the fake LCD owner releases the old front.
  struct Panel {
    std::array<std::uint8_t,96*32*3> pixels[2]{};
    Barrier dma;
    static bool swap(void *context,unsigned index) {
      assert(index==1);static_cast<Panel*>(context)->dma.hold();return true;
    }
  } panel;
  StockBoundController<fabgl::P4Rgb888Controller> direct;
  direct.bindPanelStorage({{panel.pixels[0].data(),panel.pixels[1].data()},2,0,96,32,96*3,&panel,Panel::swap});
  direct.begin();direct.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync",64,16,true);
  assert(direct.isViewPortAllocated());direct.bindNativeAliases();
  fabgl::Canvas dc(&direct);
  StockP4Service direct_service(allocator);
  assert(direct_service.startClock() && direct_service.attach(direct));counter=0;
  dc.setPixel(2,2,fabgl::RGB888(255,0,0));
  auto direct_swap=std::async(std::launch::async,[&]{dc.swapBuffers();});
  panel.dma.awaitEntry(); // fails if staging waits for the next clock edge
  assert(std::uint32_t(counter)==0);
  assert(direct_swap.wait_for(20ms)==std::future_status::timeout);
  assert(hdmiOutput().emitFrame()); // independent clock can still progress
  assert(std::uint32_t(counter)==1);
  panel.dma.release();
  assert(direct_swap.wait_for(3s)==std::future_status::ready);direct_swap.get();
  // No second emitFrame was needed: one refresh opportunity is sufficient.
  assert(std::uint32_t(counter)==1);
  direct_service.detach();direct.end();
  assert(host_stale_notifications==0);

  // A prepared-service failure must relinquish its controller before the
  // screen-mode owner clears the partial candidate and resumes the old mode.
  // Exercise both real task-creation failures with borrowed pixel allocations.
  for(int fail_after : {0,1}) {
    using Candidate=PreparedModeCandidate<StockRuntimeController,fabgl::Canvas,StockP4Service>;
    Candidate candidate;candidate.refresh_hz=60;candidate.width=64;candidate.height=16;
    host_creation_fail_after=fail_after;
    const bool prepared=prepareModeCandidate(candidate,
      [&]()->std::unique_ptr<StockRuntimeController>{
        auto *r=new StockBoundController<fabgl::P4Rgb888Controller>();
        r->bindPanelStorage({{panel.pixels[0].data(),panel.pixels[1].data()},2,0,96,32,96*3,&panel,Panel::swap});return std::unique_ptr<StockRuntimeController>(r);
      },
      [](StockRuntimeController &r){r.paletted().begin();r.paletted().setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync",64,16,false);return r.display().isViewPortAllocated();},
      [](StockRuntimeController &r){return std::make_unique<fabgl::Canvas>(&r.paletted());},
      [&]{return std::make_unique<StockP4Service>(allocator);},
      [](StockP4Service &s,StockRuntimeController &r){return s.startClock() && s.prepare(r);});
    assert(!prepared);candidate.service.reset();candidate.canvas.reset();candidate.controller.reset();
    assert(host_stale_notifications==0);
  }
}
