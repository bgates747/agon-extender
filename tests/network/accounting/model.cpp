#include "extender/network/messages/accounting_model.hpp"
#include <cassert>
#include <cstdint>
#include <limits>
using namespace agon::extender::network::messages::accounting;
int main(){
 Model m;m.begin(Metric::PeerRequest,0);m.begin(Metric::PeerTick,5);
 assert(m.snapshot(6).rows[unsigned(Metric::PeerRequest)].active==1);
 m.end(Metric::PeerTick,5,15,0);m.end(Metric::PeerRequest,0,20,17,Outcome::Ok,30);
 auto s=m.snapshot(21);assert(s.epochUs==0&&!s.clockInvalid&&!s.lifecycleInvalid);
 assert(s.rows[unsigned(Metric::PeerRequest)].elapsedUs==20&&s.rows[unsigned(Metric::PeerTick)].elapsedUs==10);
 // Their sum is30 over21 wall units: overlapping inclusive spans are not CPU.
 assert(s.rows[unsigned(Metric::PeerRequest)].highwater==30);
 m.event(Metric::SocketRead,22,23,0,Outcome::WouldBlock);
 m.event(Metric::SocketRead,23,24,0,Outcome::Closed);
 m.event(Metric::SocketRead,24,25,0,Outcome::Error);
 s=m.snapshot(26);auto &r=s.rows[unsigned(Metric::SocketRead)];
 assert(r.calls==3&&r.units==0&&r.wouldBlock==1&&r.closed==1&&r.errors==1);
 m.event(Metric::TxEnqueue,30,29,0);assert(m.snapshot(31).clockInvalid);
 m.end(Metric::TxEnqueue,32,33,0);assert(m.snapshot(34).lifecycleInvalid);
 Model sat;const auto max=std::numeric_limits<std::uint64_t>::max();
 sat.event(Metric::Submit,0,max,max);sat.event(Metric::Submit,0,1,1);
 auto t=sat.snapshot(max);assert(t.saturated&&t.rows[0].units==max&&t.rows[0].elapsedUs==max);
 assert(t.rows[0].calls==2);return 0;
}
