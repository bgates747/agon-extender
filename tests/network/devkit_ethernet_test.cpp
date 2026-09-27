#include "extender/network/devkit_ethernet.hpp"
#include <cassert>
#include <future>
#include <chrono>
using agon::extender::network::DevkitEthernet;
int main() {
 unsigned events=0;
 auto count=[](void *p,DevkitEthernet::Event) noexcept {++*static_cast<unsigned*>(p);};
 DevkitEthernet first, second;
 assert(!first.start(nullptr,nullptr));
 assert(first.start(count,&events));
 assert(first.start(count,&events));assert(ETH.starts==1);
 assert(!second.start(count,&events));
 second.stop();assert(ETH.stops==0);
 auto old=Network.handlers.begin()->second;
 old(OTHER_EVENT,{});assert(events==0);
 for(auto event:{ARDUINO_EVENT_ETH_START,ARDUINO_EVENT_ETH_CONNECTED,ARDUINO_EVENT_ETH_GOT_IP,
                 ARDUINO_EVENT_ETH_LOST_IP,ARDUINO_EVENT_ETH_DISCONNECTED,ARDUINO_EVENT_ETH_STOP})old(event,{});
 assert(events==6);assert(first.hasIP()&&first.linkUp());
 assert(first.lease().address=="test-address");
 first.stop();assert(Network.handlers.empty());assert(!first.hasIP());
 old(ARDUINO_EVENT_ETH_GOT_IP,{});assert(events==6);
 assert(second.start(count,&events));
 old(ARDUINO_EVENT_ETH_GOT_IP,{});assert(events==6); // no stale delivery to new owner
 auto current=Network.handlers.begin()->second;
 current(ARDUINO_EVENT_ETH_GOT_IP,{});assert(events==7);
 second.stop();
 ETH.fail=true;assert(!first.start(count,&events));assert(Network.handlers.empty());
 ETH.fail=false;Network.fail=true;assert(!first.start(count,&events));Network.fail=false;
 assert(first.start(count,&events));first.stop();
 // Callback in flight must finish before stop returns. No actual network task.
 struct Block {std::promise<void> entered,release;};
 Block block;
 auto callback=[](void *p,DevkitEthernet::Event) noexcept {
  auto &b=*static_cast<Block*>(p);b.entered.set_value();b.release.get_future().wait();
 };
 assert(first.start(callback,&block));
 auto pending=Network.handlers.begin()->second;
 auto dispatch=std::async(std::launch::async,[&]{pending(ARDUINO_EVENT_ETH_GOT_IP,{});});
 block.entered.get_future().wait();
 auto stopped=std::async(std::launch::async,[&]{first.stop();});
 assert(stopped.wait_for(std::chrono::milliseconds(20))==std::future_status::timeout);
 block.release.set_value();dispatch.get();stopped.get();
 pending(ARDUINO_EVENT_ETH_GOT_IP,{}); // must not call dead callback context
 assert(Network.handlers.empty());
}
