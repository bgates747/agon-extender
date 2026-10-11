// PORT-008 F02c2b1. Real admission leaves + sequencers, no GPIO/SDK model here.
#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
extern "C" {
#include "emos_parallel_handover.h"
}
#include "extender/transport/p4_parallel_handover.hpp"
#include "extender/transport/console_session.hpp"
using P = agon::extender::transport::P4ParallelHandover;
using Body=std::array<uint8_t,16>;
using Session=std::array<uint8_t,6>;
static size_t cases=0;
static std::ofstream vectors;
// CRC-free carrier: padding is ignored, never an integrity check.
static void seal(Body &b) { b[14]=b[15]=0; }
static Body offer(unsigned len=1,unsigned direction=0,unsigned seq=1) {
  Body b{'E','X',PARALLEL_WIRE_VERSION,2,0x12,0x34,0x56,0x78,uint8_t(seq),uint8_t(seq>>8),uint8_t(len),uint8_t(len>>8),uint8_t(direction),0,0,0};seal(b);return b;
}
static Body ack(Body b) {b[3]=0x82;seal(b);return b;}
static Session initial() {return {0x12,0x34,0x56,0x78,0,0};}
static void ready(P &p) {
  p.step(P::released|P::validHigh); p.step(P::validHigh);
  p.step(0);p.step(P::validHigh);p.step(P::uartUp|P::validHigh);
  assert(p.phase()==P::uart);
}
static bool echeck(unsigned mode,unsigned phase,Session &s,const Body &o,const Body &a,bool expected) {
  t_emosParallelHandover h{uint8_t(phase),1,0,1};auto before=s;auto prior=h;
  auto ok=emos_parallel_handover_admit(&h,uint8_t(mode),s.data(),o.data(),a.data());
  assert(bool(ok)==expected);
  if(ok) {assert(h.phase==EPH_DRAIN && !h.failed);assert(s[4]==o[8]&&s[5]==o[9]);}
  else {assert(!memcmp(&prior,&h,sizeof(h)));assert(before==s);}
  if(vectors) {
    vectors<<mode<<' '<<phase<<' ';for(auto v:before)vectors<<unsigned(v)<<' ';
    for(auto v:o)vectors<<unsigned(v)<<' ';
    for(auto v:a)vectors<<unsigned(v)<<' ';
    vectors<<expected<<'\n';
  }
  ++cases;return ok;
}
static void reject(const Body &o,Session s=initial(),unsigned mode=3) {
  P p;ready(p);Body a; a.fill(0xa5);auto before=s;
  assert(!p.admit(uint8_t(mode),s.data(),o.data(),a.data()));
  assert(s==before&&p.phase()==P::uart&&p.readyN());for(auto v:a)assert(v==0xa5);++cases;
  echeck(mode,EPH_UART,s,o,ack(o),false);
}
static void roundtrip(unsigned direction) {
  P p; ready(p); auto ps=initial(),es=ps;Body reply{};auto o=offer(4096,direction);
  t_emosParallelHandover e{EPH_UART,1,0,0};
  assert(p.admit(3,ps.data(),o.data(),reply.data()));
  assert(emos_parallel_handover_admit(&e,3,es.data(),o.data(),reply.data()));
  unsigned ec=0,pc=0;bool erun=false,prun=false;
  for(unsigned tick=0;tick<100;++tick) {
    const auto ea=emos_parallel_handover_step(&e,uint8_t(ec|(p.readyN()?EPH_READY_HIGH:0)));
    const auto pa=p.step(uint8_t(pc|(e.validN?P::validHigh:0)|(e.clockHigh?P::clockHigh:0)));
    // Model completed adapter operations, one step after their requests.
    // No drain flag is fabricated by admission; both must request it here.
    if(ea==EPH_FENCE)ec=EPH_QUIET;
    if(ea==EPH_RELEASE)ec=EPH_RELEASED;
    if(ea==EPH_ARM)ec=EPH_ARMED;
    if(ea==EPH_RUN){erun=true;ec=EPH_DONE;}
    if(ea==EPH_RESTORE)ec=EPH_UART_UP;
    if(pa==P::fence)pc=P::quiet;
    if(pa==P::release)pc=P::released;
    if(pa==P::arm)pc=P::armed;
    if(pa==P::run){prun=true;pc=P::done;}
    if(pa==P::restore)pc=P::uartUp;
    if(e.phase==EPH_UART && p.phase()==P::uart) {
      assert(erun&&prun&&!e.failed&&!p.failed());
      // The exact previous offer remains rejected AFTER actual normal return.
      assert(!p.admit(3,ps.data(),o.data(),reply.data()));
      assert(!emos_parallel_handover_admit(&e,3,es.data(),o.data(),reply.data()));
      // A subsequent sequence, with a different descriptor, is admissible.
      o=offer(1,direction^1,2);assert(p.admit(3,ps.data(),o.data(),reply.data()));
      assert(emos_parallel_handover_admit(&e,3,es.data(),o.data(),reply.data()));
      ++cases;return;
    }
  }
  assert(false && "admitted pair failed to return to UART");
}
int main(int argc,char **argv) {
  if(argc==2)vectors.open(argv[1]);
  roundtrip(0);roundtrip(1);
  for(unsigned dir=0;dir<2;++dir)for(unsigned len=1;len<=4096;++len) {
    P p;ready(p);auto ps=initial(),es=ps;auto o=offer(len,dir);Body a{};
    assert(p.admit(3,ps.data(),o.data(),a.data()));assert(a==ack(o));
    assert(p.phase()==P::drain);++cases;echeck(3,EPH_UART,es,o,a,true);
    // A grant cannot skip drain just because its ACK is valid.
    assert(p.step(P::validHigh)==P::fence);
    t_emosParallelHandover h{EPH_DRAIN,1,0,0};assert(emos_parallel_handover_step(&h,EPH_READY_HIGH)==EPH_FENCE);
    // Replaying after return to UART fails. Neither side consumes twice.
    if(len==1) {p.cancel();ready(p);auto saved=ps;assert(!p.admit(3,ps.data(),o.data(),a.data()));assert(saved==ps);++cases;echeck(3,EPH_UART,es,o,a,false);}
  }
  for(unsigned mode=0;mode<256;++mode)if(mode!=3)reject(offer(),initial(),mode);
  for(unsigned len:{0u,4097u,65535u})reject(offer(len));
  for(unsigned d=2;d<256;++d)reject(offer(1,d));
  for(unsigned seq:{0u,2u,256u,65535u})reject(offer(1,0,seq));
  for(unsigned phase=0;phase<14;++phase)if(phase!=EPH_UART) {auto s=initial();auto o=offer();echeck(3,phase,s,o,ack(o),false);}
  // Metadata still governs admission; legal length/direction changes are not
  // corruption-detected. Padding in offers and ACKs has no effect at all.
  auto original=offer(27,1);auto originalAck=ack(original);
  for(unsigned i=0;i<16;++i)for(unsigned bit=0;bit<8;++bit) {
    auto bad=original;bad[i]^=uint8_t(1u<<bit);
    const bool legal=i==10 || (i==11 && bit<4) || (i==12 && bit==0) || i>=14;
    P p;ready(p);auto ps=initial();Body reply{};
    assert(p.admit(3,ps.data(),bad.data(),reply.data())==legal);++cases;
    auto es=initial();echeck(3,EPH_UART,es,bad,ack(bad),legal);
    es=initial();echeck(3,EPH_UART,es,bad,originalAck,i>=14);
    auto changed=originalAck;changed[i]^=uint8_t(1u<<bit);
    es=initial();echeck(3,EPH_UART,es,original,changed,i>=14);
  }
  // A historical format2 peer cannot admit, even with an otherwise valid body.
  auto old=original;old[2]=2;reject(old);
  Session zero{};reject(offer(),zero);
  auto s=initial();s[0]^=1;reject(offer(),s);
  s=initial();s[4]=255;s[5]=255;reject(offer(1,0,0),s);reject(offer(1,0,1),s);
  for(unsigned last:{254u,255u,256u,65534u}) {
    auto es=initial();es[4]=uint8_t(last);es[5]=uint8_t(last>>8);auto ps=es;
    auto o=offer(4096,1,last+1);Body a{};P p;ready(p);assert(p.admit(3,ps.data(),o.data(),a.data()));++cases;
    echeck(3,EPH_UART,es,o,a,true);
  }
  // Reset phase is not an UART release proof, even with valid old RAM identity.
  {P p;auto ps=initial();auto o=offer();Body a{};assert(!p.admit(3,ps.data(),o.data(),a.data()));++cases;}
  // Current compatible console rejects the entire new version, rather than
  // interpreting a parallel descriptor as a prepare/commit or changing lease.
  agon::extender::transport::ConsoleSession console;
  {auto o=offer();Body a{};assert(!console.request(o.data(),0,42,a.data()));assert(!console.active());++cases;}
  {auto o=offer();o[2]=1;o[12]=1;seal(o);reject(o);}
  std::cout<<"PASS "<<cases<<" paired admission checks; all lengths/directions, replay, wrap, malformed ACKs, mode and recovery gates\n";
}
