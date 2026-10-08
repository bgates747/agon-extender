// Paired ownership sequencers. The modeled adapters assert electrical output
// ownership at EVERY change, not merely final state. This cannot qualify pins.
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
extern "C" {
#include "emos_parallel_handover.h"
}
#include "extender/transport/p4_parallel_handover.hpp"
#include "extender/input/usb_key_queue.hpp"
using P = agon::extender::transport::P4ParallelHandover;
struct Adapter {
  unsigned mask=0, completed=0, action=0, delay=0;
  unsigned backlog=3, keyboard=0, delivered=0;
  bool fenced=true, brokenRelease=false, quietBlocked=false, run=false;
};
struct Pair {
  t_emosParallelHandover e{}; P p;
  Adapter ea,pa;
  bool reverse, v=true,c=false, payload=false, ended=false;
  unsigned progress=0, latency, peerLatency, steps=0, blocks=0, etime=0,ptime=0;
  unsigned lastE=255,lastP=255; bool timeouts=true;
  Pair(bool rev,unsigned delay,unsigned peerDelay=0):reverse(rev),latency(delay),peerLatency(peerDelay) {emos_parallel_handover_init(&e);}
  void pins() {
    if (ea.mask & pa.mask) {
      std::cerr<<"contending masks "<<ea.mask<<" "<<pa.mask<<" phases "
               <<unsigned(e.phase)<<" "<<unsigned(p.phase())<<" at "<<steps<<"\n";
      std::abort();
    }
  }
  void action(Adapter &a,unsigned request,bool isE) {
    // Signals acknowledge COMPLETION only. No inherited RELEASED/ARMED bits.
    if(request==EPH_WAIT) return;
    if(request==EPH_LIVE) {a.fenced=false; return;}
    if(request!=a.action) {
      a.action=request; a.delay=isE?latency:peerLatency; a.completed=0;
      if(request!=EPH_RUN) a.run=false;
      a.fenced=true;
    }
    if(request==EPH_RUN) {a.run=true;return;}
    if(a.delay) {--a.delay;return;}
    switch(request) {
      case EPH_FENCE:
        // Already serialized bytes drain; newly arriving keys are held.
        if(a.backlog) --a.backlog;
        else if(!a.quietBlocked) a.completed=EPH_QUIET;
        break;
      case EPH_RELEASE:
        if(a.brokenRelease) break;
        a.mask=0; a.completed=EPH_RELEASED; break;
      case EPH_ARM:
        assert(a.fenced);
        a.mask=(isE != reverse)?255:0; a.completed=EPH_ARMED;break;
      case EPH_RUN: a.run=true;break;
      case EPH_RESTORE:
        a.mask=isE?5:10; a.completed=EPH_UART_UP;break;
      default: std::abort();
    }
    pins();
  }
  void cancelE() {
    emos_parallel_handover_cancel(&e);ea.action=0;ea.completed=0;ea.run=false;
    payload=false; ended=false;
  }
  void cancelP() {p.cancel();pa.action=0;pa.completed=0;pa.run=false;}
  void resetE() {
    // Hardware reset disables output drivers; retained peer state is untouched.
    ea=Adapter{}; emos_parallel_handover_init(&e);v=true;c=false;
    payload=false;ended=false;lastE=255; pins();
  }
  void resetP() {pa=Adapter{};p=P{};lastP=255;pins();}
  bool idle() const {return e.phase==EPH_UART && p.phase()==P::uart;}
  void tick(unsigned schedule=0) {
    ++steps;
    // Bounded polling with independent task delays. A stuck phase cancels;
    // adapter failure cannot acknowledge release or re-enable UART.
    if(e.phase!=lastE) {lastE=e.phase;etime=steps;}
    if(unsigned(p.phase())!=lastP) {lastP=p.phase();ptime=steps;}
    if(timeouts && steps-etime>160) {cancelE();etime=steps;}
    if(timeouts && steps-ptime>180) {cancelP();ptime=steps;}
    // A queued physical key is not injected directly into the UART serializer.
    if(steps%7==0) ++pa.keyboard;
    if(!pa.fenced && p.phase()==P::uart && e.phase==EPH_UART) {
      pa.delivered+=pa.keyboard;pa.keyboard=0;
    }
    if(schedule!=1) {
      unsigned inputs=ea.completed | (p.readyN()?EPH_READY_HIGH:0);
      action(ea,emos_parallel_handover_step(&e,inputs),true);
      if(e.phase!=EPH_BLOCK) {v=e.validN;c=e.clockHigh;}
    }
    if(schedule!=2) {
      unsigned inputs=(v?P::validHigh:0)|(c?P::clockHigh:0);
      if(pa.completed&EPH_QUIET) inputs|=P::quiet;
      if(pa.completed&EPH_RELEASED) inputs|=P::released;
      if(pa.completed&EPH_ARMED) inputs|=P::armed;
      if(pa.completed&EPH_DONE) inputs|=P::done;
      if(pa.completed&EPH_UART_UP) inputs|=P::uartUp;
      action(pa,p.step(inputs),false);
    }
    if(e.phase==EPH_BLOCK && p.phase()==P::block && ea.run && pa.run && !ended) {
      if(!payload) {payload=true;progress=0;++blocks;}
      assert(ea.mask==(reverse?0u:255u));assert(pa.mask==(reverse?255u:0u));
      v=false; c=(progress%2)!=0;
      if(++progress==12) {
        v=true;c=true;ended=true;payload=false;
        // Exact-length block runner completion stops/releases P4 first. Its
        // READY high is emitted by p.step after the completed bit, never DMA.
        pa.mask=0;pa.completed=EPH_DONE;
      }
    }
    if(ended && p.readyN() && e.phase==EPH_BLOCK) ea.completed=EPH_DONE;
    pins();
    if(std::getenv("TRACE")) std::cerr<<steps<<" phases "<<unsigned(e.phase)<<","<<unsigned(p.phase())<<" levels "<<c<<v<<p.readyN()<<" actions "<<ea.action<<","<<pa.action<<" done "<<ea.completed<<","<<pa.completed<<" masks "<<ea.mask<<","<<pa.mask<<"\n";
  }
  void settle(unsigned limit=1200) {
    for(unsigned i=0;i<limit && !idle();++i) tick(i%5==0?1:i%7==0?2:0);
    assert(idle());tick();
    assert(ea.mask==5 && pa.mask==10);assert(!ea.fenced && !pa.fenced);
  }
  void begin() {
    assert(idle());assert(p.begin());assert(emos_parallel_handover_begin(&e));
    // No stale adapter result from the preceding block/bootstrap.
    ea.completed=pa.completed=0;ea.action=pa.action=0;
    ea.backlog=4;pa.backlog=5;ended=false;payload=false;progress=0;
  }
};
int main(int argc,char **argv) {
  unsigned cases=0;
  for(bool reverse:{false,true}) for(unsigned latency:{0u,1u,3u}) for(unsigned peerLatency:{0u,1u,3u,9u}) {
    Pair a(reverse,latency,peerLatency);a.settle();
    for(unsigned repeat=0;repeat<3;++repeat) {
      a.begin();a.settle();assert(!a.e.failed && !a.p.failed());
      assert(a.blocks==repeat+1);assert(a.pa.delivered>0);++cases;
    }
    // Reboot/cancel each endpoint at every step of a real successful exchange.
    Pair sample(reverse,latency,peerLatency);sample.settle();sample.begin();
    unsigned duration=0;while(!sample.idle()){sample.tick();++duration;assert(duration<300);}
    for(unsigned cut=0;cut<=duration;++cut) for(unsigned fault=0;fault<4;++fault) {
      Pair b(reverse,latency,peerLatency);b.settle();b.begin();
      for(unsigned i=0;i<cut;++i)b.tick();
      if(fault==0)b.resetE();else if(fault==1)b.resetP();
      else if(fault==2)b.cancelE();else b.cancelP();
      b.settle();++cases;
    }
    // Adapter release failure must never be treated as release completion.
    for(bool who:{false,true}) {
      Pair b(reverse,latency,peerLatency);b.settle();b.begin();
      (who?b.ea:b.pa).brokenRelease=true;
      for(unsigned i=0;i<700;++i)b.tick();
      assert(!b.idle()); assert(b.ea.fenced && b.pa.fenced);assert(b.blocks==0);
      (who?b.ea:b.pa).brokenRelease=false;b.settle();++cases;
    }
    // Either peer can be absent/stalled. No successful block or opposing drive.
    for(unsigned who:{1u,2u}) {
      Pair b(reverse,latency,peerLatency);b.settle();b.begin();
      for(unsigned i=0;i<500;++i)b.tick(who);
      assert(b.blocks==0);b.settle();++cases;
    }
    Pair busy(reverse,latency,peerLatency);busy.settle();busy.begin();
    assert(!busy.p.begin());assert(!emos_parallel_handover_begin(&busy.e));++cases;

    // Empty software/FIFO backlog alone is not QUIET: a shifting final byte
    // or partial incoming packet must withhold the adapter's acknowledgement.
    for(bool who:{false,true}) {
      Pair drain(reverse,latency,peerLatency);drain.settle();drain.begin();
      auto &adapter=who?drain.ea:drain.pa;adapter.quietBlocked=true;
      for(unsigned i=0;i<50;++i)drain.tick();
      assert(adapter.backlog==0);assert(drain.blocks==0);
      assert(adapter.mask==(who?5u:10u));
      adapter.quietBlocked=false;drain.settle();
      assert(!drain.e.failed && !drain.p.failed());++cases;
    }

    // Reuse the actual P4 key queue: press/release order survives a successful
    // handover. The adapter stops consuming it while fenced, rather than
    // clearing held-key state or synthesizing a disconnect on suspension.
    agon::extender::input::UsbKeyQueue keys;
    std::vector<agon::extender::input::ProcessedKey> expected;
    Pair keyboard(reverse,latency,peerLatency);keyboard.settle();keyboard.begin();
    for(unsigned i=0;i<4;++i) {
      agon::extender::input::ProcessedKey key{};
      key.virtual_key=static_cast<std::uint8_t>(i/2+1);key.down=(i%2)==0;
      expected.push_back(key);assert(keys.push(key));
    }
    while(!keyboard.idle()) {keyboard.tick();assert(!keys.empty());}
    for(auto want:expected) {
      agon::extender::input::ProcessedKey got;
      assert(keys.pop(got));assert(got.virtual_key==want.virtual_key && got.down==want.down);
    }
    assert(keys.empty());assert(keys.releaseAll());assert(keys.empty());++cases;
  }
  // Exact host transition vectors for the compiled-eZ80 ABI check. These are
  // supplementary to the behavioral checks above, not independent semantics.
  if(argc==2) {
    std::ofstream f(argv[1]);
    for(unsigned state=0;state<16;++state) for(unsigned flags=0;flags<8;++flags)
      for(unsigned input=0;input<64;++input) {
        t_emosParallelHandover e{BYTE(state),BYTE(flags&1),BYTE((flags>>1)&1),BYTE((flags>>2)&1)};
        auto result=emos_parallel_handover_step(&e,BYTE(input));
        f<<state<<' '<<flags<<' '<<input<<' '<<unsigned(result)<<' '
         <<unsigned(e.phase)<<' '<<unsigned(e.validN)<<' '<<unsigned(e.clockHigh)<<' '
         <<unsigned(e.failed)<<'\n';
      }
  }
  std::cout<<"PASS "<<cases<<" paired handover cases; both directions, delayed adapters, reset/cancel at every step, release failures, absent peers, repeated blocks, queued input\n";
}
