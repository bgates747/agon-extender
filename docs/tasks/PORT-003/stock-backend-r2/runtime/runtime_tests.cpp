#include <array>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <cstdlib>
#include <future>
#include <mutex>
#include <thread>
#include "canvas.h"
#include "extender/display/stock_p4_service.hpp"

using namespace agon::extender::display;
using namespace std::chrono_literals;
namespace {
unsigned checks{};
void check(bool value,char const *label) {
  ++checks;std::printf("%s %s\n",value?"PASS":"FAIL",label);std::fflush(stdout);
  if(!value) std::abort();
}
template<class F> void await(F predicate,char const *label) {
  auto until=std::chrono::steady_clock::now()+3s;
  bool ready=false;
  do { ready=predicate(); if(!ready) std::this_thread::yield(); }
  while(!ready&&std::chrono::steady_clock::now()<until);
  check(ready,label);
}
struct Barrier {
  std::mutex mutex;std::condition_variable cv;bool entered{},released{};
  void hold() {std::unique_lock lock(mutex);entered=true;cv.notify_all();cv.wait(lock,[&]{return released;});}
  void wait() {std::unique_lock lock(mutex);check(cv.wait_for(lock,3s,[&]{return entered;}),"forced scheduling barrier reached");}
  void release() {std::lock_guard lock(mutex);released=true;cv.notify_all();}
};
struct BlockingController:StockBoundController<fabgl::VGA64Controller> {
  std::atomic<Barrier *> block{};
  std::uint8_t *visible(int y) { return const_cast<std::uint8_t *>(m_viewPortVisible[y]); }
  std::size_t drain() override {
    if(block.load()) phase_c_after_receive=[&] {
      if(auto b=block.exchange(nullptr)) {
        // Forced pause after dequeue with native exclusion held. The original
        // private setPixelAt implementation still executes after release.
        StockNativeGuard guard(stockNativeMutex());b->hold();
      }
    };
    return StockBoundController<fabgl::VGA64Controller>::drain();
  }
};
struct BlockingOutput : StockBoundController<fabgl::VGA4Controller> {
  Barrier *row{};
  void prepareRow(int y,std::uint8_t *signal) override {
    AGON_STOCK_NATIVE_GUARD;
    if(row) {auto b=row;row=nullptr;b->hold();}
    StockBoundController<fabgl::VGA4Controller>::prepareRow(y,signal);
  }
};
void setup(StockRuntimeController &c,bool dbl=false) {
  c.display().begin();
  c.display().setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync",64,16,dbl);
  c.display().enableBackgroundPrimitiveTimeout(false);
}
Allocator allocator() {return {nullptr,[](void *,std::size_t n)->void *{return std::malloc(n);},[](void *,void *p){std::free(p);}};}

void gateAndClock() {
  StockExecutionGate gate;
  check(!gate.beginWorker(),"initial stock suspension blocks worker");
  gate.resume();check(gate.beginWorker(),"worker admission opens after resume");
  check(!gate.beginWorker(),"a second worker cannot enter an active pass");
  auto suspended=std::async(std::launch::async,[&]{gate.suspend();});
  await([&]{return gate.suspended();},"suspension is published before active pass is joined");
  check(suspended.wait_for(0ms)!=std::future_status::ready,"suspender waits for active worker");
  gate.endWorker();suspended.get();
  check(!gate.beginWorker(),"no check/start gap after foreground suspension");
  gate.suspend();gate.resume();check(!gate.beginWorker(),"nested suspension remains effective");
  gate.resume();check(gate.beginWorker(),"balanced resume restores admission");gate.endWorker();

  StockClock clock;StockFrameCounter counter;counter=UINT32_MAX-1;
  clock.start(100,16667);
  check(clock.observe(100+16667-1)==0,"clock does not advance before its edge");
  check(clock.observe(100+16667*3)==3&&std::uint32_t(counter)==1,"late callback accounts elapsed ticks with register wrap");
  check(clock.delayedTicks()==2&&clock.maximumLatenessUs()==33334,"clock exposes missed-delivery count and lateness");
  check(clock.observe(100+16667*3)==0,"a repeated observation does not replay a tick");
  {
    StockNativeGuard native(stockNativeMutex());
    StockNativeGuard foreground(stockForegroundMutex());
    auto independent=std::async(std::launch::async,[&]{return clock.observe(100+16667*63);});
    check(independent.wait_for(1s)==std::future_status::ready,"clock never waits for native or foreground exclusion");
    check(independent.get()==60&&std::uint32_t(counter)==61,"sixty further edges advance while drawing/output ownership is held");
  }
}

void queueAndRows() {
  BlockingController c;setup(c);fabgl::Canvas canvas(&c);
  canvas.setPixel(3,2,fabgl::RGB888(255,0,0));
  canvas.setPixel(4,2,fabgl::RGB888(0,255,0));
  Barrier between;
  auto drawing=std::async(std::launch::async,[&]{
    phase_c_after_receive=[&]{between.hold();}; // original FIFO has already popped one command
    return c.drain();
  });
  between.wait();
  alignas(8) std::uint8_t signal[64];
  auto output=std::async(std::launch::async,[&]{c.prepareRow(0,signal);});
  check(output.wait_for(1s)==std::future_status::ready,"output progresses inside an unfinished drain with queued work remaining");output.get();
  auto flush=std::async(std::launch::async,[&]{canvas.waitCompletion(false);});
  // The active pass still owns the popped primitive; synchronous flush must
  // wait and may not overtake it with the next queued primitive.
  check(flush.wait_for(20ms)!=std::future_status::ready,"immediate flush cannot overtake a popped worker primitive");
  between.release();drawing.get();flush.get();
  auto red=canvas.getPixel(3,2),green=canvas.getPixel(4,2);
  check(red.R==255&&red.G==0&&green.G==255&&green.R==0,"worker and immediate flush preserve actual FIFO pixel effects");
  c.display().enableBackgroundPrimitiveExecution(false);

  StockBoundController<fabgl::VGA16Controller> palette;setup(palette);
  palette.display().enableBackgroundPrimitiveExecution(false);
  fabgl::Canvas pc(&palette);pc.setPixel(0,12,fabgl::RGB888(255,255,255));
  palette.createPalette(17);palette.setItemInPalette(17,15,fabgl::RGB888(255,0,0));
  std::uint16_t spans[]={0,0,2,0,14,17};palette.updateSignalList(spans,3);
  palette.prepareRow(0,signal);palette.prepareRow(12,signal);
  std::uint16_t shortList[]={0,0};palette.updateSignalList(shortList,1);
  palette.prepareRow(13,signal); // prior Copper cursor referenced the retired tail
  std::array<std::uint8_t,64> rgb{};
  palette.prepareRow(12,signal);
  StockScanlineController<fabgl::VGA16Controller>::normalizeRow(signal,rgb.data(),64);
  check(rgb[0]==63,"palette-list retirement rebinds Copper before the next native row");
  palette.deletePalette(17); // preserve upstream delete-all behavior; no secondary palette at teardown
}

void swapAndPayloads() {
  BlockingController c;setup(c,true);fabgl::Canvas canvas(&c);
  auto oldDrawing=c.getScanline(0),oldVisible=c.visible(0);
  canvas.setPixel(2,2,fabgl::RGB888(255,0,0));
  alignas(8) std::uint8_t signal[64];std::array<std::uint8_t,64> rgb{};
  c.prepareRow(2,signal);
  StockScanlineController<fabgl::VGA64Controller>::normalizeRow(signal,rgb.data(),64);
  check(rgb[2]==0,"double-buffer immediate drawing leaves visible native rows unchanged");
  auto swap=std::async(std::launch::async,[&]{canvas.swapBuffers();});
  check(swap.wait_for(20ms)!=std::future_status::ready,"explicit swap waits for worker notification");
  c.drain();swap.get();
  check(c.getScanline(0)==oldVisible&&c.visible(0)==oldDrawing,"queued original swap exchanges native plane tables");
  c.prepareRow(2,signal);
  StockScanlineController<fabgl::VGA64Controller>::normalizeRow(signal,rgb.data(),64);
  check(rgb[2]==3,"row output uses the newly visible plane after explicit swap");
  c.enableBackgroundPrimitiveExecution(false);
  c.setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync",64,16,false);
  c.enableBackgroundPrimitiveExecution(true);
  canvas.setPenColor(fabgl::RGB888(255,255,255));c.drain();
  fabgl::Point path[]{{2,3},{20,3}};
  canvas.drawPath(path,2);
  path[0]={2,9};path[1]={20,9};
  c.drain();
  check(canvas.getPixel(10,3).R==255&&canvas.getPixel(10,9).R==0,"queued path survives mutation of its caller's original array");
  canvas.drawPath(path,2);
  c.enableBackgroundPrimitiveExecution(false);
  check(canvas.getPixel(10,9).R==255,"stock disable flush executes and frees pending dynamic data");
  c.enableBackgroundPrimitiveExecution(true);
  auto reuse=std::async(std::launch::async,[&] {
    for(int i=0;i<FABGLIB_PRIMITIVES_DYNBUFFERS_SIZE;++i) {
      canvas.drawPath(path,2);c.drain();
    }
  });
  check(reuse.wait_for(3s)==std::future_status::ready,"queued paths reuse more than the entire stock payload pool without exhaustion");
  reuse.get();
  c.enableBackgroundPrimitiveExecution(false);
}

void snapshotLeases() {
  std::size_t bytes{};
  auto alloc=allocator();alloc.context=&bytes;
  alloc.allocate=[](void *p,std::size_t n)->void *{*static_cast<std::size_t *>(p)+=n;return std::malloc(n);};
  PresentationSnapshotPool pool(alloc,SnapshotPixelFormat::RGB222,0,false,true);
  check(bytes==3*1024*768,"packed snapshot pool allocates one byte per pixel per slot");
  PresentationSnapshotLease retained,latest;
  for(int i=0;i<3;++i) {
    MutableSnapshotView view{};check(pool.tryBegin(64,16,i,view)==SnapshotBeginResult::Ok,"direct RGB222 producer admitted");
    check(view.pixels==nullptr&&view.packed_pixels!=nullptr,"packed producer cannot accidentally write RGB888 pixels");
    std::fill_n(view.packed_pixels,64*16,std::uint8_t(i+1));
    check(pool.finish(CompositionResult::Ok,16667)==SnapshotFinishResult::Published,"packed image publishes without conversion");
    if(i==0) check(pool.tryAcquireLatest(0,retained),"network lease acquires completed image");
    else {
      check(!pool.tryAcquireLatest(i,latest),"existing single-consumer lease contract is retained");
      check(retained.view().data[500]==1,"leased RGB222 data remains immutable across later publications");
    }
  }
  MutableSnapshotView view{};
  check(pool.tryBegin(64,16,4,view)==SnapshotBeginResult::Ok,"producer remains independent of an outstanding network lease");
  MutableSnapshotView second{};
  check(pool.tryBegin(64,16,5,second)==SnapshotBeginResult::ProducerBusy,"another output request skips an occupied producer without waiting");
  pool.finish(CompositionResult::InvalidRegion,16667);
  retained.release();
  check(pool.tryAcquireLatest(0,latest)&&latest.view().payload_bytes==1024&&latest.view().stride_bytes==64&&latest.view().data[500]==3,"consumer acquires latest complete packed image after release; partial image cancelled");
}

void serviceLifetime() {
  StockP4Service service(allocator());StockFrameCounter count;
  check(service.startClock(),"real service starts its separate clock through the host SDK model");
  BlockingController c;setup(c);fabgl::Canvas canvas(&c);
  check(service.attach(c),"real service creates independent drawing/output tasks");
  PresentationSnapshotLease retained;
  await([&]{return service.snapshotPool().tryAcquireLatest(0,retained);},"real output task publishes original scanlines");
  Barrier drawing; c.block.store(&drawing);
  canvas.setPixel(5,5,fabgl::RGB888(255,0,0));drawing.wait();
  auto before=std::uint32_t(count);
  // Retain network ownership while native drawing is blocked.
  PresentationSnapshotLease next;
  check(!service.snapshotPool().tryAcquireLatest(retained.view().generation,next),"a held network lease does not admit a second consumer");
  await([&]{return std::uint32_t(count)-before>=3;},"60 Hz clock advances during an intentionally blocked native primitive");
  auto stop=std::async(std::launch::async,[&]{service.detach();});
  check(stop.wait_for(20ms)!=std::future_status::ready,"mode detach waits for native owners before freeing rows");
  before=std::uint32_t(count);
  await([&]{return std::uint32_t(count)-before>=2;},"clock continues while teardown waits for the primitive");
  drawing.release();stop.get();
  auto old=retained.view().data[0];
  c.end();
  before=std::uint32_t(count);
  await([&]{return std::uint32_t(count)-before>=2;},"clock continues with no native controller attached");
  check(retained.view().data[0]==old,"network lease survives native mode destruction");
  retained.release();next.release();
  auto replacement=std::make_unique<BlockingOutput>();setup(*replacement);
  Barrier row;replacement->row=&row;
  service.snapshotPool().tryAcquireLatest(UINT64_MAX,next); // request fresh output
  check(service.attach(*replacement),"service reattaches a different original depth");
  row.wait();
  auto detach=std::async(std::launch::async,[&]{service.detach();});
  check(detach.wait_for(20ms)!=std::future_status::ready,"mode detach waits for an active original output row");
  before=std::uint32_t(count);
  await([&]{return std::uint32_t(count)-before>=2;},"clock advances while output holds native state during detach");
  row.release();detach.get();replacement.reset();
  check(host_stale_notifications.load()==0,"callback join prevents notifications to retired task handles");

}
void overlayLifetime() {
  BlockingOutput c;setup(c);fabgl::Sprite sprite;
  std::uint8_t pixels[16];std::fill_n(pixels,16,0xc3); // opaque RGBA2222 red
  auto bitmap=std::make_unique<fabgl::Bitmap>(4,4,pixels,fabgl::PixelFormat::RGBA2222);
  sprite.addBitmap(bitmap.get());sprite.hardware=true;sprite.visible=true;sprite.moveTo(1,1);
  c.setSprites(&sprite,1);c.drain();
  Barrier row;c.row=&row;
  alignas(8) std::uint8_t signal[64];std::array<std::uint8_t,64> rgb{};
  auto output=std::async(std::launch::async,[&]{c.prepareRow(2,signal);});
  row.wait();
  auto retire=std::async(std::launch::async,[&]{c.removeSprites();sprite.clearBitmaps();bitmap.reset();});
  check(retire.wait_for(20ms)!=std::future_status::ready,"sprite retirement waits for the native row retaining its frames");
  row.release();output.get();retire.get();
  StockScanlineController<fabgl::VGA4Controller>::normalizeRow(signal,rgb.data(),64);
  check(rgb[2]==3,"in-flight row completes with the original sprite before retirement");
  c.prepareRow(2,signal);
  StockScanlineController<fabgl::VGA4Controller>::normalizeRow(signal,rgb.data(),64);
  check(rgb[2]==0,"next native row no longer accesses the retired sprite or bitmap");
  c.enableBackgroundPrimitiveExecution(false);
}

void failureUnwind() {
  StockP4Service service(allocator());BlockingController c;setup(c);StockFrameCounter counter;
  check(service.startClock(),"clock starts before worker-allocation fault injection");
  host_creation_fail_after=0;
  check(!service.attach(c),"drawing-task allocation failure returns cleanly");
  host_creation_fail_after=1;
  check(!service.attach(c),"output-task allocation failure joins its already-created drawing task");
  auto before=std::uint32_t(counter);
  await([&]{return std::uint32_t(counter)-before>=2;},"clock survives failed task creation");
  check(service.attach(c),"same native controller can retry after both allocation failures");
  service.detach();
  check(host_stale_notifications.load()==0,"allocation-failure unwind leaves no retired notification targets");
  auto failing=allocator();failing.allocate=[](void *,std::size_t)->void *{return nullptr;};
  StockP4Service noStorage(failing);
  check(!noStorage.snapshotPool().enabled(),"snapshot allocation failure retains no publishable storage");
  // One independent clock owner at a time in production. No need to start the
  // deliberately unusable second service to verify unavailable storage.
}

} // namespace
int main() {
  gateAndClock();queueAndRows();swapAndPayloads();snapshotLeases();serviceLifetime();overlayLifetime();failureUnwind();
  std::printf("Stock runtime comparisons: %u checks, 0 failures\n",checks);
}
