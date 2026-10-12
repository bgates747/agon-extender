// Actual-controller host proof; checkpoints affect temporary source copies only.
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <future>
#include <iostream>
#include <mutex>
#include <thread>
#include "canvas.h"
#include "extender/display/stock_runtime_controller.hpp"
#include "extender/display/mode_transaction.hpp"
using namespace agon::extender::display;
using namespace std::chrono_literals;
namespace {
struct Pause {
  std::mutex mutex;std::condition_variable cv;bool armed{},entered{},released{};
  void arm(){std::lock_guard lock(mutex);armed=true;entered=false;released=false;}
  void hit(){std::unique_lock lock(mutex);if(!armed)return;armed=false;entered=true;cv.notify_all();cv.wait(lock,[&]{return released;});}
  void wait(){std::unique_lock lock(mutex);assert(cv.wait_for(lock,2s,[&]{return entered;}));}
  void release(){{std::lock_guard lock(mutex);released=true;}cv.notify_all();}
};
Pause primitive_pause,row_pause,wake_pause,feed_hidden_pause,feed_visible_pause;
std::atomic<bool> feed_hidden_seen{},feed_visible_seen{};
std::atomic<bool> feed_mode{};
std::atomic<unsigned> feed_primitives{};
struct Wake {
  std::atomic<unsigned> count{};std::atomic<bool> live{true};std::condition_variable cv;
  static void notify(void *context) noexcept {
    auto &self=*static_cast<Wake *>(context);assert(self.live.load());
    self.count.fetch_add(1,std::memory_order_release);self.cv.notify_one();
  }
};
class Controller : public StockBoundController<fabgl::P4Color64Controller> {
 public:using fabgl::BitmappedDisplayController::hideSprites;
  using fabgl::BitmappedDisplayController::showSprites;
};
}
void agon_visibility_after_primitive(bool refresh){
  primitive_pause.hit();
  if(feed_mode.load(std::memory_order_relaxed)){
    unsigned done=feed_primitives.fetch_add(1,std::memory_order_relaxed)+1;
    // Deterministic HOST-ONLY schedule: pause after one real hidden primitive,
    // then after its next real RefreshSprites and original native unlock. The
    // Author-approved product callback/scheduler/guard are not modified here.
    if(done>=128 && !refresh && !feed_hidden_seen.exchange(true))feed_hidden_pause.hit();
    if(refresh && feed_hidden_seen.load() && !feed_visible_seen.exchange(true))feed_visible_pause.hit();
  }
}
void agon_visibility_after_row(){row_pause.hit();}
void agon_visibility_before_wake(){wake_pause.hit();}
int main(){
  fabgl::BitmappedDisplayController::queueSize=16;
  Controller c;c.begin();c.setResolution("\"64x32\" 1 64 68 72 80 32 34 36 40 -HSync -VSync",64,32,false);
  c.resumeBackgroundPrimitiveExecution();c.bindNativeAliases();
  fabgl::Canvas canvas(&c);canvas.setBrushColor(0,0,0);canvas.clear();c.drain();
  assert(c.linearStorage());
  std::array<std::uint8_t,2048> image;std::atomic<bool> stopping{};
  auto capture_into=[&](auto &buffer){AGON_STOCK_NATIVE_GUARD;return c.copyLinearFrameUnderNativeGuard(buffer.data(),false,stopping);};
  auto capture=[&]{return capture_into(image);};
  std::uint8_t whites[]={0xff,0xff,0xff,0xff},blues[]={0xf0,0xf0,0xf0,0xf0};
  fabgl::Bitmap white(2,2,whites,fabgl::PixelFormat::RGBA2222),blue(2,2,blues,fabgl::PixelFormat::RGBA2222);
  fabgl::Sprite sprite;sprite.addBitmap(&white);sprite.hardware=0;sprite.visible=1;sprite.allowDraw=1;sprite.moveTo(4,4);
  c.display().setSprites(&sprite,1);c.drain();
  fabgl::Rect update(0,0,63,31);
  auto enqueue=[&](int x){fabgl::Primitive p;p.cmd=fabgl::PrimitiveCmd::DrawBitmap;p.bitmapDrawingInfo=fabgl::BitmapDrawingInfo(x,8,&blue);c.addPrimitive(p);};
  Wake wake;int owner{};assert(stockBindSoftwareSnapshotWake(&owner,Wake::notify,&wake));
  int foreign{};assert(!stockBindSoftwareSnapshotWake(&foreign,Wake::notify,&wake));
  auto hidden=[&]{
    image.fill(0xa5);assert(!capture());assert(!capture());assert(!capture());
    assert(std::all_of(image.begin(),image.end(),[](auto b){return b==0xa5;}));
    std::array<std::uint8_t,64> row{};c.prepareLinearRow(4,row.data(),false);assert((row[4]&63)==0);
  };
  // V01 -- actual worker erased state, coalescing and completed pixels.
  primitive_pause.arm();enqueue(20);auto worker=std::async(std::launch::async,[&]{return c.drain();});
  primitive_pause.wait();hidden();assert(wake.count==0);primitive_pause.release();assert(worker.get()==1);
  assert(wake.count==1 && capture() && (image[4*64+4]&63)==63 && (image[8*64+20]&63)==48);
  c.drain();assert(wake.count==1); // no pending request, no duplicate wake
  // V02 -- actual foreground flush follows the identical readiness/wake rules.
  primitive_pause.arm();enqueue(22);auto foreground=std::async(std::launch::async,[&]{canvas.waitCompletion(false);});
  primitive_pause.wait();hidden();assert(wake.count==1);primitive_pause.release();foreground.get();
  assert(wake.count==2 && capture() && (image[4*64+4]&63)==63 && (image[8*64+22]&63)==48);c.drain();
  // Notification may occur inside an OUTER recursive render-probe guard. It
  // only wakes; actual output waits native and succeeds AFTER the outer unlock.
  std::promise<void> attempting;std::future<bool> after_outer;
  {
    AGON_STOCK_NATIVE_GUARD;c.hideSprites(update);hidden();unsigned before=wake.count;
    c.showSprites(update);assert(wake.count==before+1);
    after_outer=std::async(std::launch::async,[&]{attempting.set_value();std::array<std::uint8_t,2048> copy{};return capture_into(copy);});
    attempting.get_future().wait();assert(after_outer.wait_for(20ms)==std::future_status::timeout);
  }
  assert(after_outer.get());
  // V03 -- a writer cannot change any later source row during a whole copy.
  row_pause.arm();image.fill(0xa5);auto copying=std::async(std::launch::async,capture);
  row_pause.wait();enqueue(24);auto writer=std::async(std::launch::async,[&]{return c.drain();});
  assert(writer.wait_for(20ms)==std::future_status::timeout);row_pause.release();assert(copying.get());
  assert((image[8*64+24]&63)==0 && (image[4*64+4]&63)==63);assert(writer.get()==1);
  // Native was released before simulated downstream PPA/DMA work begins.
  auto later=std::async(std::launch::async,[]{AGON_STOCK_NATIVE_GUARD;return true;});
  assert(later.wait_for(500ms)==std::future_status::ready && later.get());
  // V04 -- actual full queue blocks its producer while that producer owns
  // foreground. Output does not acquire foreground, avoiding that lock cycle.
  for(int n=0;n<16;++n)enqueue(26);
  std::promise<void> producing;auto producer=std::async(std::launch::async,[&]{producing.set_value();enqueue(28);});
  producing.get_future().wait();assert(producer.wait_for(20ms)==std::future_status::timeout);
  assert(!stockForegroundMutex().try_lock());
  auto independent=std::async(std::launch::async,capture);
  assert(independent.wait_for(500ms)==std::future_status::ready && independent.get());
  auto draining=std::async(std::launch::async,[&]{return c.drain();});producer.get();draining.get();c.drain();
  // Cancellation waits for a notification already in native exclusion. The
  // test-only checkpoint is BEFORE the nonblocking callback, not inside it.
  {AGON_STOCK_NATIVE_GUARD;c.hideSprites(update);}hidden();wake_pause.arm();
  auto showing=std::async(std::launch::async,[&]{c.showSprites(update);});wake_pause.wait();
  auto cancellation=std::async(std::launch::async,[&]{stockCancelSoftwareSnapshotWake(&owner);});
  assert(cancellation.wait_for(20ms)==std::future_status::timeout);wake_pause.release();showing.get();cancellation.get();
  unsigned canceled_count=wake.count;wake.live=false;
  {AGON_STOCK_NATIVE_GUARD;c.hideSprites(update);}hidden();c.showSprites(update);
  assert(wake.count==canceled_count); // no callback can touch the retired context
  stockCancelSoftwareSnapshotWake(&foreign); // must not affect any later owner
  // Actual transaction ordering: preparing a replacement keeps the old owner;
  // retirement cancels it before committed activation binds the new owner.
  Wake next;int next_owner{},former_owner{};
  assert(stockBindSoftwareSnapshotWake(&former_owner,Wake::notify,&next));
  PreparedModeCandidate<int,int,int> replacement;
  replacement.width=64;replacement.height=32;replacement.refresh_hz=60;
  assert(prepareModeCandidate(replacement,[]{return std::make_unique<int>(1);},
      [](int &){return true;},[](int &){return std::make_unique<int>(2);},
      []{return std::make_unique<int>(3);},[](int &,int &){return true;}));
  assert(!stockBindSoftwareSnapshotWake(&next_owner,Wake::notify,&next));
  bool activated=false,published=false;
  commitPreparedMode(std::move(replacement),
      [&]{stockCancelSoftwareSnapshotWake(&former_owner);},[](int &){},
      [&](int &){assert(stockBindSoftwareSnapshotWake(&next_owner,Wake::notify,&next));activated=true;},
      [&](auto &&){published=true;});
  assert(activated && published);
  stockCancelSoftwareSnapshotWake(&former_owner); // late old teardown is harmless
  {AGON_STOCK_NATIVE_GUARD;stockRequestSoftwareSnapshotWake();stockSoftwareSpritesShown();}
  assert(next.count==1);next.count=0;
  c.showSprites(update);assert(next.count==0); // no stale pending request on bind
  // V05 -- continuously fed actual queue with regular stock RefreshSprites.
  // Producer blocks under foreground on queue capacity; output remains separate.
  constexpr unsigned feed_total=4096;
  std::atomic<bool> producer_done{},worker_done{},output_done{};
  std::atomic<unsigned> accepted{},middle_accepted{},attempts{},drain_calls{};
  for(int n=0;n<16;++n)enqueue(30);
  {AGON_STOCK_NATIVE_GUARD;c.hideSprites(update);}image.fill(0xa5);assert(!capture());
  std::mutex output_mutex;
  std::promise<void> captured_middle;auto captured_middle_future=captured_middle.get_future();
  std::atomic<bool> captured_middle_once{};
  feed_hidden_pause.arm();feed_visible_pause.arm();
  feed_mode=true;
  auto feeding=std::async(std::launch::async,[&]{
    for(unsigned n=0;n<feed_total;++n){enqueue(30);if(n%16==15)c.display().refreshSprites();}
    producer_done=true;
  });
  auto fed_worker=std::async(std::launch::async,[&]{
    for(;;){auto count=c.drain();++drain_calls;if(producer_done.load() && count==0)break;}
    worker_done=true;
  });
  feed_hidden_pause.wait();hidden();unsigned notification_baseline=next.count;
  auto output=std::async(std::launch::async,[&]{
    std::array<std::uint8_t,2048> copy{};unsigned observed=notification_baseline;
    while(!output_done.load()){
      std::unique_lock lock(output_mutex);
      next.cv.wait_for(lock,20ms,[&]{return output_done.load() || next.count.load()!=observed;});
      if(output_done.load())break;observed=next.count.load();lock.unlock();
      ++attempts;
      if(capture_into(copy)){
        assert((copy[4*64+4]&63)==63);++accepted;
        unsigned done=feed_primitives.load();if(done>=128 && done<feed_total-128 && !worker_done.load()) {
          ++middle_accepted;if(!captured_middle_once.exchange(true))captured_middle.set_value();
        }
      }
    }
  });
  feed_hidden_pause.release();feed_visible_pause.wait();
  assert(captured_middle_future.wait_for(2s)==std::future_status::ready);
  feed_visible_pause.release();
  assert(feeding.wait_for(4s)==std::future_status::ready);feeding.get();
  assert(fed_worker.wait_for(4s)==std::future_status::ready);fed_worker.get();feed_mode=false;
  output_done=true;next.cv.notify_one();output.get();
  assert(accepted>0 && middle_accepted>0 && next.count>0);
  unsigned streaming_wakes=next.count,streaming_accepted=accepted,streaming_middle=middle_accepted,streaming_attempts=attempts;
  // Honest no-show boundary: bitmap-only stock work emits no completion until
  // the original drain's final show. An infinite no-show drain cannot progress.
  {AGON_STOCK_NATIVE_GUARD;c.hideSprites(update);}hidden();unsigned before_no_show=next.count;
  for(int n=0;n<16;++n)enqueue(32);
  primitive_pause.arm();auto no_show=std::async(std::launch::async,[&]{return c.drain();});
  primitive_pause.wait();assert(next.count==before_no_show);hidden();primitive_pause.release();assert(no_show.get()==16);
  assert(next.count==before_no_show+1 && capture());
  // Static/no-SW and HW-only paths still admit snapshots with a generic hidden flag.
  c.display().setSprites(static_cast<fabgl::Sprite *>(nullptr),0);c.hideSprites(update);assert(capture());
  sprite.hardware=1;c.display().setSprites(&sprite,1);c.hideSprites(update);assert(capture());
  sprite.hardware=0;sprite.visible=0;c.hideSprites(update);assert(capture());
  sprite.visible=1;sprite.allowDraw=0;c.hideSprites(update);assert(capture());
  c.display().setSprites(static_cast<fabgl::Sprite *>(nullptr),0);c.drain();
  stockCancelSoftwareSnapshotWake(&next_owner);next.live=false;
  std::cout<<"PASS V01..V05: worker+foreground pixels/sentinel; coalesced wake; outer native waits; writer exclusion; real full-queue producer; cancellation/context lifetime\n";
  std::cout<<"STREAMING "<<streaming_wakes<<" "<<streaming_attempts<<" "<<streaming_accepted<<" "<<streaming_middle<<" "<<drain_calls.load()<<"\n";
  std::cout<<"LIMIT: deterministic test-only post-unlock schedule proves a capture opportunity; uncontrolled fairness is unqualified; infinite no-show drain remains stale\n";
}
