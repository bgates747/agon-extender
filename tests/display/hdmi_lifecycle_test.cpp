// Test actual sink implementation, including its persistent submission worker.
// Inspect private state only here to assert DMA ownership isn't discarded.
#include "hdmi_lifecycle_host.hpp"
#include <future>
#include <iostream>
#define private public
#include "extender/display/hdmi_output.hpp"
#undef private
#include "extender/display/rolling/bridge.h"
#include "extender/display/rolling/strip_probe.h"

using namespace agon::extender::display;
using namespace std::chrono_literals;
extern "C" void strip_async_read(strip_async_stats *p){*p={};p->faults=hdmi_host::faults;}
extern "C" void strip_probe_read(strip_probe_stats *p){*p={};}
extern "C" void strip_fault_read(strip_fault_stats *p){*p={};}
extern "C" unsigned agon_scanout_front(){return hdmi_host::front;}
extern "C" void agon_scanout_reset(){hdmi_host::faults=0;}
bool agon_scanout_stage(fabgl::P4Rgb888Controller *,unsigned i,int,int){hdmi_host::staged=i;return true;}
void agon_scanout_commit(){}

template<class F> void await(F condition) {
  const auto end=std::chrono::steady_clock::now()+2s;
  while(!condition() && std::chrono::steady_clock::now()<end)std::this_thread::yield();
  assert(condition());
}
template<class T> T completed(std::future<T> &f){assert(f.wait_for(2s)==std::future_status::ready);return f.get();}
static void close(HdmiOutput &output) {
  output.cleanup();
  if(output.direct_task_){vTaskDeleteWithCaps(output.direct_task_);output.direct_task_=nullptr;}
  assert(hdmi_host::live.empty());assert(!output.ready() && !output.outputSize());
}
static bool callback(void *) {return false;}

static void cancelled_swap(bool old) {
  HdmiOutput output;assert(output.start());int owner{};
  assert(output.bindFrameCallback(callback,&owner));
  auto storage=output.panelStorage();assert(storage.count==2);
  auto swap=std::async(std::launch::async,[&]{return storage.swap(storage.context,1);});
  await([&]{return output.direct_state_.load()==HdmiOutput::Submitted;});
  assert(output.ownership_.pending());
  output.unbindFrameCallback(&owner); // no further scanout completions
  if(old) {
    assert(swap.wait_for(40ms)==std::future_status::timeout);
    host_frame(output.panel_); // release the broken waiter so the test can exit
    std::cout<<"Reproduced old cancellation hang\n";
  }
  assert(!completed(swap));
  if(!old)assert(output.ownership_.pending()); // cancellation isn't DMA release
  close(output);
}

static void failed_panel_borrow(bool old) {
  HdmiOutput output;assert(output.start());
  output.ownership_.submitted(1);hdmi_host::faults=1;
  auto borrow=std::async(std::launch::async,[&]{return output.panelStorage();});
  if(old) {
    assert(borrow.wait_for(40ms)==std::future_status::timeout);
    output.panel_->selected=1;host_frame(output.panel_);
    assert(completed(borrow).count==2);
    std::cout<<"Reproduced old faulted-panel borrow hang\n";
  } else {
    assert(completed(borrow).count==0);
    assert(output.ownership_.pending());
    assert(output.needsMode(848,480));
    assert(output.selectMode(848,480)); // same carrier must recover faulted DMA
    assert(output.panelStorage().count==2 && !output.ownership_.pending());
  }
  close(output);
}

int main(int argc,char **) {
  const bool old=argc>1;
  cancelled_swap(old);failed_panel_borrow(old);
  if(old)return 0;
  // Every public acquisition step unwinds and allows a later start. The panel
  // creation substitute models the SDK's documented all-or-nothing return;
  // SDK-internal partial allocations are not exercised by this test.
  for(const char *step: {"power","i2c","io0","io1","io2","dsi","panel",
                         "buffers","reset","callback","init","task"}) {
    HdmiOutput output;hdmi_host::inject(step);assert(!output.start());
    assert(hdmi_host::fail_count==0);assert(hdmi_host::live.empty());
    assert(!output.ready() && !output.outputSize());
    assert(output.start());close(output);
  }
  {HdmiOutput output;hdmi_host::inject("panel",1,ESP_ERR_NO_MEM);
    assert(output.start());assert(output.panelStorage().count==1);close(output);}
  {HdmiOutput output;hdmi_host::inject("panel",2,ESP_ERR_NO_MEM);
    assert(!output.start());assert(hdmi_host::live.empty());assert(output.start());close(output);}
  {HdmiOutput output;hdmi_host::suppress_start_frame=true;
    assert(!output.start());hdmi_host::suppress_start_frame=false;
    assert(hdmi_host::live.empty());assert(output.start());close(output);}
  {HdmiOutput output;assert(output.start());int owner{},other{};
    assert(output.bindFrameCallback(callback,&owner));
    output.unbindFrameCallback(&other);assert(!output.direct_cancelled_);
    assert(!output.selectMode(512,384));output.unbindFrameCallback(&owner);
    for(int i=0;i<10;++i){assert(output.selectMode(512,384));assert(output.width()==684);
      assert(output.selectMode(848,480));assert(output.width()==848);}
    // Requested carrier creation failure leaves no borrowed storage. Rebuilding
    // the former carrier uses the same selectMode path owned by vdu_mode fallback.
    hdmi_host::inject("init");assert(!output.selectMode(512,384));
    assert(!output.ready() && hdmi_host::live.empty());
    assert(output.selectMode(848,480));assert(output.panelStorage().count==2);
    close(output);}
  {HdmiOutput output;assert(output.start());auto storage=output.panelStorage();
    auto swap=std::async(std::launch::async,[&]{return storage.swap(storage.context,1);});
    await([&]{return output.direct_state_.load()==HdmiOutput::Submitted;});
    assert(swap.wait_for(20ms)==std::future_status::timeout);
    host_frame(output.panel_);assert(completed(swap));
    assert(output.ownership_.writable(false)==1);
    // A contained scanout failure also releases the swap waiter, without
    // pretending that the old front has been acknowledged by physical DMA.
    auto failing=std::async(std::launch::async,[&]{return storage.swap(storage.context,0);});
    await([&]{return output.direct_state_.load()==HdmiOutput::Submitted;});
    hdmi_host::faults=1;assert(!completed(failing));assert(output.ownership_.pending());
    close(output);}
  {HdmiOutput output;assert(output.start());auto storage=output.panelStorage();
    hdmi_host::inject("draw");
    auto swap=std::async(std::launch::async,[&]{return storage.swap(storage.context,1);});
    assert(!completed(swap));assert(!output.ownership_.pending());close(output);}
  {HdmiOutput output;assert(output.start());int owner{};
    assert(output.bindFrameCallback(callback,&owner));auto storage=output.panelStorage();
    std::promise<void> entered,release;auto released=release.get_future().share();
    hdmi_host::after_draw=[&]{entered.set_value();released.wait();};
    auto swap=std::async(std::launch::async,[&]{return storage.swap(storage.context,1);});
    auto entry=entered.get_future();assert(entry.wait_for(2s)==std::future_status::ready);
    output.unbindFrameCallback(&owner);
    assert(output.direct_state_.load()==HdmiOutput::Requested);
    assert(swap.wait_for(20ms)==std::future_status::timeout);
    release.set_value();assert(!completed(swap));hdmi_host::after_draw={};
    assert(output.ownership_.pending());close(output);}
  {HdmiOutput output;assert(output.start());auto storage=output.panelStorage();
    // The worker can also be waiting for a prior native buffer selection,
    // before it has submitted the direct request being cancelled.
    output.ownership_.submitted(1);const auto before=hdmi_host::draws.load();
    auto swap=std::async(std::launch::async,[&]{return storage.swap(storage.context,0);});
    await([&]{return output.direct_state_.load()==HdmiOutput::Requested;});
    output.unbindFrameCallback(nullptr);assert(!completed(swap));
    assert(hdmi_host::draws.load()==before && output.ownership_.pending());close(output);}
  for(const char *step: {"power","i2c","io2","dsi","panel","buffers","reset","callback","init"}) {
    HdmiOutput output;assert(output.start());hdmi_host::inject(step);
    assert(!output.selectMode(512,384));assert(hdmi_host::live.empty());
    assert(output.direct_task_); // persistent worker survives failed configuration
    assert(output.selectMode(848,480));assert(output.panelStorage().count==2);close(output);
  }
  std::cout<<"PASS: real HDMI sink cancellation, fault recovery, startup failure and repeated carrier lifecycle\n";
}
