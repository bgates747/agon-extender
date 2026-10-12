// RESEARCH-007 diagnostic semantics against the actual queued controller.
#include <cassert>
#include <algorithm>
#include <array>
#include <chrono>
#include <future>
#include <iostream>
#include <thread>
#include "canvas.h"
#include "extender/display/stock_runtime_controller.hpp"
using namespace agon::extender::display;
using namespace std::chrono_literals;

int main() {
  StockBoundController<fabgl::P4Rgb888Controller> controller;
  controller.begin();
  controller.setResolution("\"64x32\" 1 64 68 72 80 32 34 36 40 -HSync -VSync",64,32,false);
  controller.resumeBackgroundPrimitiveExecution();
  controller.bindNativeAliases();
  assert(controller.isViewPortAllocated());
  controller.drain(); // discard setup work before the window
  unsigned char marker[12]={'B','0','0','9',1,1,3,0,1,12,0,0};
  agon_bench::marker(marker,12);
  std::uint8_t pixels[]={0xff,0xc3,0xcc,0xf0};
  fabgl::Bitmap bitmap(2,2,pixels,fabgl::PixelFormat::RGBA2222);
  fabgl::Primitive primitive;
  primitive.cmd=fabgl::PrimitiveCmd::DrawBitmap;
  primitive.bitmapDrawingInfo=fabgl::BitmapDrawingInfo(2,2,&bitmap);
  controller.addPrimitive(primitive);
  primitive.cmd=fabgl::PrimitiveCmd::VScroll;primitive.ivalue=1;controller.addPrimitive(primitive);
  primitive.cmd=fabgl::PrimitiveCmd::RefreshSprites;controller.addPrimitive(primitive);
  primitive.cmd=fabgl::PrimitiveCmd::Flush;controller.addPrimitive(primitive);
  std::unique_lock lock(stockNativeMutex());
  std::promise<void> launched;
  auto work=std::async(std::launch::async,[&]{launched.set_value();return controller.drain();});
  launched.get_future().wait();
  assert(work.wait_for(25ms)==std::future_status::timeout);
  lock.unlock();assert(work.get()==4);
  auto &r=agon_bench::render_windows[0];
  assert(r.drains==1 && r.empty_drains==0 && r.primitive_calls==4);
  assert(r.native_wait_us>=15000);
  assert(r.kinds[unsigned(agon_bench::RenderKind::Bitmap)].calls==1);
  assert(r.kinds[unsigned(agon_bench::RenderKind::Scroll)].calls==1);
  assert(r.kinds[unsigned(agon_bench::RenderKind::RefreshSprites)].calls==1);
  assert(r.kinds[unsigned(agon_bench::RenderKind::Other)].calls==1);
  assert(r.kinds[unsigned(agon_bench::RenderKind::FinalSprites)].calls==1);
  std::uint32_t sum=0;
  for(auto &kind:r.kinds)sum+=kind.us.load();
  assert(r.rendering_us==sum && r.rendering_us<r.native_wait_us);
  assert(controller.drain()==0 && r.empty_drains==1);
  controller.suspendBackgroundPrimitiveExecution();
  assert(controller.drain()==0 && r.refused_drains==1 && r.drains==2);
  controller.resumeBackgroundPrimitiveExecution();
  {
    agon_bench::RenderBatch crossing;
    crossing.operation(agon_bench::RenderKind::Bitmap,1,4,14);
    marker[5]=2;agon_bench::marker(marker,12);
    const auto previous=r.rendering_us.load();
    crossing.finish(1);
    assert(r.boundary_drops==1 && r.rendering_us==previous);
  }
  marker[5]=1;marker[6]=4;marker[8]=2;agon_bench::marker(marker,12);
  {agon_bench::RenderBatch disabled;assert(!disabled.enabled());}
  assert(agon_bench::render_windows[1].drains==0);
  marker[5]=2;agon_bench::marker(marker,12);
  marker[5]=0;agon_bench::marker(marker,12);assert(agon_bench::used==0);
  // RESET must not recycle sidecar slot zero while an older drain owns it.
  marker[5]=1;marker[8]=1;agon_bench::marker(marker,12);
  agon_bench::RenderBatch held;
  auto reset_marker=std::array<unsigned char,12>{};
  std::copy(marker,marker+12,reset_marker.begin());reset_marker[5]=0;
  auto reset=std::async(std::launch::async,[&]{agon_bench::marker(reset_marker.data(),12);});
  assert(reset.wait_for(10ms)==std::future_status::timeout);
  held.finish(0);reset.get();
  assert(agon_bench::used==0 && agon_bench::outstanding==0);
  for(unsigned i=0;i<=agon_bench::RenderWindowCapacity;++i) {
    marker[5]=1;marker[6]=i;marker[8]=1;agon_bench::marker(marker,12);
    {agon_bench::RenderBatch probe;probe.finish(0,true);}
    marker[5]=2;agon_bench::marker(marker,12);
  }
  assert(agon_bench::render_overflow && agon_bench::outstanding==0);
  assert(agon_bench::render_windows[0].boundary_drops==0);
  std::cout<<agon_bench::json();
}
