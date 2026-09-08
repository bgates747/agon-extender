#include "uart_flow_peer.hpp"
#include <cassert>
#include <cstring>
#include <initializer_list>
using S=UartFlowPeer::State;
using A=UartFlowPeer::Action;
static const auto* req=reinterpret_cast<const uint8_t*>(UartFlowPeer::request);
static UartFlowPeer to_return_hold(uint32_t base=0) {
  UartFlowPeer p; p.since=base;
  assert(p.tick(base,true,true,nullptr,0)==A::none);
  p.tick(base+10,false,true,nullptr,0);
  assert(p.tick(base+1010,false,true,nullptr,0)==A::allow_forward);
  assert(p.tick(base+1011,false,true,req,3)==A::none);
  assert(p.tick(base+1012,true,true,req+3,3)==A::stop_forward);
  assert(p.tick(base+1013,true,true,nullptr,0)==A::queue_ack);
  return p;
}
int main() {
  for (uint32_t base: {0U, 0xFFFFF000U}) {
    auto p=to_return_hold(base);
    assert(p.tick(base+1513,true,false,nullptr,0)==A::none);
    p.tick(base+2013,false,false,nullptr,0);
    assert(p.tick(base+2014,false,true,nullptr,0)==A::ack_sent);
    assert(p.tick(base+3214,true,true,nullptr,0)==A::queue_blocked);
    assert(p.tick(base+4214,true,false,nullptr,0)==A::cancel_tx);
    assert(p.tick(base+9214,true,true,nullptr,0)==A::passed);
    assert(p.tick(base+9215,true,true,req,1)==A::failed);
    assert(p.tick(base+20000,true,true,nullptr,0)==A::none && p.state==S::fail);
  }
  { UartFlowPeer p; assert(p.tick(180000,true,true,nullptr,0)==A::failed); }
  { UartFlowPeer p; assert(p.tick(0,true,true,req,1)==A::failed); }
  { auto p=to_return_hold(); assert(p.tick(1014,true,true,nullptr,0)==A::failed); }
  { auto p=to_return_hold(); assert(p.tick(1113,false,false,nullptr,0)==A::failed); }
  { auto p=to_return_hold(); assert(p.tick(4013,true,false,nullptr,0)==A::failed); }
  { auto p=to_return_hold(); p.tick(2013,false,false,nullptr,0); assert(p.tick(5013,false,false,nullptr,0)==A::failed); }
  { auto p=to_return_hold(); p.tick(2013,false,false,nullptr,0); p.tick(2014,false,true,nullptr,0);
    assert(p.tick(5014,false,true,nullptr,0)==A::failed); }
  { auto p=to_return_hold(); p.state=S::blocked_return; assert(p.tick(2013,true,true,nullptr,0)==A::failed); }
  { auto p=to_return_hold(); p.state=S::blocked_return; assert(p.tick(2013,false,false,nullptr,0)==A::failed); }
  { auto p=to_return_hold(); p.fail("UART error"); assert(p.tick(2000,false,true,nullptr,0)==A::none); }
  { UartFlowPeer p; p.tick(0,false,true,nullptr,0); p.tick(1000,false,true,nullptr,0);
    uint8_t wrong='X'; assert(p.tick(1001,false,true,&wrong,1)==A::failed); }
  { UartFlowPeer p; p.tick(0,false,true,nullptr,0); p.tick(1000,false,true,nullptr,0);
    assert(p.tick(1001,false,true,req,7)==A::failed); }
}
