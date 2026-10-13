// Exact fence semantics against the actual queued controller. Host wall times
// qualify exclusion/accounting only, never P4 performance or scheduler fairness.
#include <cassert>
#include <array>
#include <chrono>
#include <future>
#include <iostream>
#include <thread>
#include "canvas.h"
#include "extender/display/stock_runtime_controller.hpp"
using namespace agon::extender::display;
using namespace agon_bench;
using namespace std::chrono_literals;
class Controller : public StockBoundController<fabgl::P4Rgb888Controller> {
 public:
  ~Controller() override {
    // Pinned upstream allocates its mouse Sprite in the constructor but its
    // destructor deletes only the queue. Host-only leak cleanup after teardown.
    end();delete mouseCursor();
  }
};
void *noAllocation(std::size_t,unsigned){return nullptr;}
int main() {
  static_assert(FenceSampleCapacity*sizeof(std::uint32_t)==16384);
  FenceSamples allocation_failure;
  assert(!allocation_failure.prepare(noAllocation));
  allocation_failure.sample(0,1);
  assert(allocation_failure.windows[0].errors.load()&FenceAllocation);
  Controller controller;
  controller.begin();
  controller.setResolution("\"64x32\" 1 64 68 72 80 32 34 36 40 -HSync -VSync",64,32,false);
  controller.resumeBackgroundPrimitiveExecution();controller.bindNativeAliases();
  assert(controller.isViewPortAllocated());controller.drain();
  fabgl::Canvas canvas(&controller);
  std::array<unsigned char,12> m={'B','0','0','9',1,0,39,0,1,12,0,0};
  auto reset=[&]{m[5]=0;marker(m.data(),m.size());};
  auto open=[&](unsigned id=39){m[5]=1;m[6]=id;marker(m.data(),m.size());};
  auto close=[&]{m[5]=2;marker(m.data(),m.size());};
  auto fence=[&]{RenderFenceRequest request(true);canvas.waitCompletion(false);};
  open();
  canvas.waitCompletion(false); // ordinary flush must not seed a fence sample
  assert(fence_samples.windows[0].count==0);
  fence();assert(fence_samples.windows[0].count==1); // seed
  assert(fence_samples.windows[0].pending==0);
  assert(fence_samples.at(0,0)==render_windows[0].rendering_us);
  assert(json().find("\"cumulative_render_us\":null")!=std::string::npos);
  std::uint8_t pixels[]={0xff,0xc3,0xcc,0xf0};
  fabgl::Bitmap bitmap(2,2,pixels,fabgl::PixelFormat::RGBA2222);
  fabgl::Primitive p;p.cmd=fabgl::PrimitiveCmd::DrawBitmap;
  p.bitmapDrawingInfo=fabgl::BitmapDrawingInfo(2,2,&bitmap);
  for(unsigned i=0;i<17;++i)controller.addPrimitive(p);
  controller.drain(); // deterministic worker contribution before this fence
  for(unsigned i=0;i<17;++i)controller.addPrimitive(p);
  // The foreground fence observes committed worker AND foreground operations,
  // including final show. Native wait is separately excluded from rendering.
  std::unique_lock native(stockNativeMutex());
  auto flushing=std::async(std::launch::async,[&]{fence();});
  assert(flushing.wait_for(20ms)==std::future_status::timeout);
  native.unlock();flushing.get();
  assert(fence_samples.windows[0].count==2);
  assert(render_windows[0].kinds[unsigned(RenderKind::Bitmap)].calls==34);
  assert(render_windows[0].foreground_primitive_calls>=17);
  assert(render_windows[0].foreground_primitive_calls<render_windows[0].primitive_calls);
  const auto second=fence_samples.at(0,1);
  assert(second==render_windows[0].rendering_us);
  assert(second>=fence_samples.at(0,0));
  controller.drain(); // post-fence Refresh cannot rewrite the preceding sample
  assert(fence_samples.at(0,1)==second);
  fence();assert(fence_samples.windows[0].count==3);
  close();const auto clean=json();
  assert(clean.find("\"samples_complete\":true")!=std::string::npos);
  assert(clean.find("\"cumulative_render_us\":null")==std::string::npos);
  // The global claim precedes each request's per-window pending publication.
  // It also keeps late queued-render boundary errors provisional until retirement.
  outstanding.fetch_add(1);
  assert(json().find("\"samples_complete\":false")!=std::string::npos);
  assert(json().find("\"cumulative_render_us\":null")!=std::string::npos);
  outstanding.fetch_sub(1);
  // Independent legacy/output phase drops remain evidence, not render errors.
  for(auto &phase:windows[0].phases)phase.drops=1;
  const auto output_partial=json();
  assert(output_partial.find("\"samples_complete\":true")!=std::string::npos);
  assert(output_partial.find("\"boundary_drops\":1")!=std::string::npos);
  for(auto &phase:windows[0].phases)phase.drops=0;
  // Actual queued-render errors and overflow still prevent qualification.
  render_windows[0].boundary_drops=1;
  assert(json().find("\"samples_complete\":false")!=std::string::npos);
  render_windows[0].boundary_drops=0;
  render_overflow=true;
  assert(json().find("\"samples_complete\":false")!=std::string::npos);
  render_overflow=false;
  // A flush on another task must not consume a live parser-task request.
  reset();open();
  {RenderFenceRequest request(true);
    std::async(std::launch::async,[&]{canvas.waitCompletion(false);}).get();
    assert(fence_samples.windows[0].count==0);
    canvas.waitCompletion(false);
  }
  assert(fence_samples.windows[0].count==1&&fence_samples.windows[0].errors==0);
  // Nested requests are invalid, but their flush cannot consume the parent.
  reset();open();
  {RenderFenceRequest outer(true);
    {RenderFenceRequest inner(true);canvas.waitCompletion(false);}
    assert(fence_samples.windows[0].count==0);
    canvas.waitCompletion(false);
  }
  assert(fence_samples.windows[0].count==1);
  assert(fence_samples.windows[0].errors.load()&FenceRequestInvariant);
  reset();open();{RenderFenceRequest missing(true);}
  assert(fence_samples.windows[0].errors.load()&FenceMissingBoundary);
  reset();open();
  {RenderFenceRequest duplicate(true);canvas.waitCompletion(false);canvas.waitCompletion(false);}
  assert(fence_samples.windows[0].count==1);
  assert(fence_samples.windows[0].errors.load()&FenceRequestInvariant);
  // Close while a scoped request remains alive: no raw partial array exposed.
  reset();open();
  {RenderFenceRequest crossing(true);close();
    assert(json().find("\"cumulative_render_us\":null")!=std::string::npos);
    canvas.waitCompletion(false);
  }
  assert(fence_samples.windows[0].count==0);
  assert(fence_samples.windows[0].errors.load()&FenceBoundary);
  // Existing outstanding ownership, not a new mutex, gates reset recycling.
  reset();open();std::future<void> resetting;
  const auto previous_generation=fence_samples.generation.load();
  {RenderFenceRequest held(true);
    auto r=m;r[5]=0;
    resetting=std::async(std::launch::async,[r]{marker(r.data(),r.size());});
    const auto deadline=std::chrono::steady_clock::now()+2s;
    while(active.load()&&std::chrono::steady_clock::now()<deadline)std::this_thread::yield();
    assert(active.load()==0);
    assert(resetting.wait_for(20ms)==std::future_status::timeout);
  }
  resetting.get();assert(outstanding==0&&used==0&&fence_samples.used()==0);
  assert(fence_samples.generation.load()==previous_generation+1);
  open();fence();assert(fence_samples.windows[0].count==1);
  // An obsolete reset generation cannot write into a reused slot token.
  reset();open();
  {RenderFenceRequest stale(true);fence_samples.generation.fetch_add(1);
    canvas.waitCompletion(false);}
  assert(fence_samples.windows[0].count==0);
  assert(fence_samples.windows[0].errors.load()&FenceBoundary);
  // Exhaustion and cumulative wrapping preserve raw evidence but invalidate it.
  reset();open();
  for(unsigned i=0;i<FenceSampleCapacity;++i)fence_samples.sample(0,i);
  fence_samples.sample(0,FenceSampleCapacity);
  assert(fence_samples.used()==FenceSampleCapacity);
  assert(fence_samples.windows[0].count==FenceSampleCapacity);
  assert(fence_samples.windows[0].errors.load()&FenceExhausted);
  close();assert(json().find("\"samples_complete\":false")!=std::string::npos);
  reset();open();fence_samples.sample(0,UINT32_MAX-1);fence_samples.sample(0,1);
  assert(fence_samples.windows[0].errors.load()&FenceCounterOverflow);
  reset();open();{RenderFenceRequest db(false);canvas.waitCompletion(false);}
  assert(fence_samples.windows[0].count==0);
  {RenderFenceRequest changed(true);renderFenceAtQuiescentFlush(false);}
  assert(fence_samples.windows[0].errors.load()&FenceIneligible);
  reset();open(9);fence(); // unfenced game remains aggregate-only
  assert(!fence_samples.windows[0].enabled&&fence_samples.windows[0].count==0);
  close();
  std::cout<<"{\"descriptor_bytes\":"<<sizeof(fence_samples.windows)
           <<",\"clean\":"<<clean<<",\"unfenced\":"<<json()<<"}";
}
