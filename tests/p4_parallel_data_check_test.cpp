#include <cassert>
#include <cstring>
#include <vector>
#include <cstdio>
#include "extender/transport/p4_parallel_data_check.hpp"
using namespace agon::extender::transport;
using H=P4ParallelHandover;
static void boot(ParallelControl &c) {
 for(auto bits:std::initializer_list<unsigned>{H::released,H::validHigh,0,H::validHigh,H::uartUp})c.handover.step(bits);
 assert(c.handover.phase()==H::uart);c.session.phase=PARALLEL_SESSION_ACTIVE;
 const uint8_t s[]={1,2,3,4,0,0};memcpy(c.session.bytes,s,6);
}
static void physical(ParallelControl &c) {
 for(auto bits:std::initializer_list<unsigned>{H::quiet,H::released,0,H::validHigh,H::validHigh|H::clockHigh,
               H::validHigh|H::clockHigh|H::armed,H::done,H::validHigh,0,H::validHigh,H::uartUp})c.handover.step(bits);
 assert(c.handover.phase()==H::uart);assert(c.payloadReturned(1));
}
static void offer(ParallelControl &c,P4ParallelDataCheck &e,unsigned n,unsigned direction) {
 uint8_t d[16]={'E','X',PARALLEL_WIRE_VERSION,PARALLEL_OFFER,1,2,3,4,1,0,uint8_t(n),uint8_t(n>>8),uint8_t(direction),0,0,0},reply[16];
 parallel_control_pad(d);assert(c.request(d,0,0,reply));assert(e.acceptedOffer());
}
static P4ParallelDataCheck::Snapshot complete(ParallelControl &c,P4ParallelDataCheck &e,unsigned n,unsigned direction) {
 P4ParallelDataCheck::Snapshot s;assert(e.retire()&&!e.takeSnapshot(s));physical(c);
 assert(!c.pending() && e.retire()&&e.takeSnapshot(s));
 assert(s.length==n && s.direction==direction);assert(!e.takeSnapshot(s));return s;
}
int main(){unsigned cases=0;
 for(unsigned n:{1u,16u,17u,255u,1024u,4096u})for(unsigned dir:{0u,1u})for(bool corrupt:{false,true}) {
  ParallelControl c;boot(c);P4ParallelDataCheck e(c,P4ParallelDataCheck::Mode::independentDirections);assert(e.begin());
  offer(c,e,n,dir);uint8_t*p;size_t cap;assert(c.payloadBuffer(p,cap));
  uint32_t fnv=2166136261u;
  for(unsigned i=0;i<n;++i){const auto v=uint8_t((i*73)^((i/8)*29)^(i/256)^105);fnv=(fnv^v)*16777619u;
   if(dir)assert(p[i]==v);else p[i]=v;}
  // Independently checked first bytes and fixed1024byte fingerprint.
  if(n>=4){assert(p[0]==0x69&&p[1]==0x20&&p[2]==0xfb&&p[3]==0xb2);}
  if(n==1024)assert(fnv==0xcfb78805u);
  if(corrupt)p[n/2]^=1;
  auto s=complete(c,e,n,dir);assert(s.independent&&s.length==n);
  assert(s.mismatches==(corrupt?1u:0u));assert(s.firstMismatch==(corrupt?n/2:n));
  assert(s.preparedFnv==(dir?fnv:0));if(!corrupt)assert(s.fnv==fnv);
  if(corrupt){assert(s.actual==p[n/2]&&s.expected==uint8_t(p[n/2]^1));}
  e.cancel();assert(!e.takeSnapshot(s));++cases;
 }
 // Existing echo mode still rejects reverse without retained data.
 {ParallelControl c;boot(c);P4ParallelDataCheck e(c);assert(e.begin());
  uint8_t d[16]={'E','X',PARALLEL_WIRE_VERSION,PARALLEL_OFFER,1,2,3,4,1,0,1,0,1,0,0,0},r[16];parallel_control_pad(d);assert(c.request(d,0,0,r));assert(!e.acceptedOffer());++cases;}
 printf("%u independent/echo endpoint lifecycle, source, corruption and bounds cases passed\n",cases);
}
