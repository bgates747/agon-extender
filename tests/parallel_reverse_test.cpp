// Executes both maintained endpoint cores. This wire model deliberately does
// not stand in for PARLIO timing, UART handover or electrical qualification.
#include <cassert>
#include <algorithm>
#include <cstdio>
#include <vector>
#include "extender/transport/p4_parallel_egress.hpp"
extern "C" {
#include "emos_parallel.h"
}
using namespace agon::extender::transport;

struct Wire : ParallelTxBackend {
  t_emosParallelEngine em{};
  P4ParallelEgress p4{*this};
  std::vector<unsigned char> source;
  ParallelTxProgress tx{ParallelTxStatus::pending, 0, false, false};
  bool ready{true}, valid{true}, clock{true}, released{}, stopped{};
  bool failStart{}, failStop{}, failRelease{}, failReady{}, silent{};
  bool nested{}, injectFault{}, lagCompletion{};
  unsigned startCalls{}, writes{}, falls{}, rises{}, samples{}, ticks{};
  unsigned tickStep{1};
  unsigned calls{}, cleanupOrder{};
  std::size_t shifted{};

  bool start(std::uint8_t const *p, std::size_t n) noexcept override {
    ++startCalls; source.assign(p,p+n); released=stopped=false;
    return !failStart;
  }
  ParallelTxProgress progress() noexcept override { return tx; }
  bool stop() noexcept override { stopped=true; cleanupOrder=++calls; return !failStop; }
  bool releaseDataPins() noexcept override {
    assert(cleanupOrder==calls); ++calls; released=true; return !failRelease;
  }
  bool setReadyN(bool high) noexcept override {
    // During completion READY must be the last operation, after stop/release.
    if(high && stopped) assert(released);
    ready=high; return !failReady;
  }
  static BYTE readReady(void *v) {
    auto &w=*static_cast<Wire *>(v);
    if(!w.silent) w.p4.poll(w.ticks);
    return w.ready;
  }
  static void writeData(void *v, BYTE) { ++static_cast<Wire *>(v)->writes; }
  static void control(void *v, BYTE vn, BYTE ch) {
    auto &w=*static_cast<Wire *>(v);
    if(!vn) w.tx.started=true;
    if(vn && !w.valid) w.tx.ended=true;
    if(!vn && w.clock && !ch) {
      ++w.falls;
      assert(w.shifted<w.source.size()); ++w.shifted;
    }
    if(!vn && !w.clock && ch) {
      ++w.rises;
      if(w.shifted==w.source.size() && !w.lagCompletion)
        w.tx={ParallelTxStatus::complete,w.shifted,true,false};
    }
    w.valid=vn; w.clock=ch;
    // Only poll at control boundaries in this model; separate tests omit all
    // intermediate polls to check the latched-edge interface.
    if(!w.silent) w.p4.poll(w.ticks);
  }
  static BYTE readData(void *v) {
    auto &w=*static_cast<Wire *>(v);
    assert(!w.valid && w.clock && !w.released);
    assert(w.shifted==w.samples+1); ++w.samples;
    if(w.nested) {
      w.nested=false; BYTE out=0;
      assert(emos_parallel_engine_read(&w.em,readData,&out,1)==EMOS_PARALLEL_BUSY);
      assert(emos_parallel_engine_write(&w.em,nullptr,1)==EMOS_PARALLEL_BUSY);
      assert(emos_parallel_engine_close(&w.em)==EMOS_PARALLEL_BUSY);
    }
    if(w.injectFault && w.samples==3) w.em.firstFault=EMOS_PARALLEL_PEER_NOT_READY;
    return w.source[w.shifted-1];
  }
  static UINT32 readTicks(void *v) {
    auto &w=*static_cast<Wire *>(v); auto t=w.ticks; w.ticks+=w.tickStep; return t;
  }
  inline static const t_emosParallelWireOps ops{readReady,writeData,control,readTicks};
  void init() {
    assert(emos_parallel_engine_configure(&em,&ops,this,4096,100,100,15)==0);
    assert(emos_parallel_engine_open(&em)==0);
  }
};

int main() {
  unsigned cases=0;
  for(unsigned n : {1,2,3,7,255,256,257,1024,4095,4096}) {
    for(unsigned seed : {0,17,255}) {
      Wire w; w.init(); w.nested=true;
      std::vector<BYTE> input(n), output(n+2,0xa5);
      for(unsigned i=0;i<n;++i) input[i]=static_cast<BYTE>((i*73)^seed^(i>>8));
      assert(w.p4.begin(input.data(),n,0,1000)==ParallelTxResult::pending);
      assert(emos_parallel_engine_read(&w.em,Wire::readData,output.data()+1,n)==0);
      assert(std::equal(input.begin(),input.end(),output.begin()+1));
      assert(output.front()==0xa5 && output.back()==0xa5);
      assert(w.samples==n && w.falls==n && w.rises==n && w.writes==0);
      assert(w.em.recordsCompleted==1 && w.em.bytesCompleted==n && !w.em.busy);
      assert(w.p4.result()==ParallelTxResult::complete && w.ready && w.released);
      ++cases;
    }
  }
  BYTE data[8]={0,255,0x55,0xaa,1,2,3,4};
  // Bounds/config/ownership: no wire mutation, buffer access or pin admission.
  { Wire w; w.init(); auto c=w.calls;
    for(auto n : {0,4097}) {
      assert(emos_parallel_engine_read(&w.em,Wire::readData,data,n)==EMOS_PARALLEL_INVALID);
      assert(w.p4.begin(data,n,0,10)==ParallelTxResult::invalid); ++cases;
    }
    assert(emos_parallel_engine_read(&w.em,nullptr,data,1)==EMOS_PARALLEL_INVALID);
    assert(emos_parallel_engine_read(&w.em,Wire::readData,nullptr,1)==EMOS_PARALLEL_INVALID);
    assert(w.p4.begin(nullptr,1,0,10)==ParallelTxResult::invalid);
    assert(w.p4.begin(data,1,0,0)==ParallelTxResult::invalid);
    assert(w.p4.begin(data,1,0,0x80000000U)==ParallelTxResult::invalid);
    assert(w.startCalls==0 && w.calls==c);
    assert(emos_parallel_engine_close(&w.em)==0);
    assert(emos_parallel_engine_read(&w.em,Wire::readData,data,1)==EMOS_PARALLEL_NOT_OWNED);
    ++cases;
  }
  // No peer: both running tick and frozen tick must terminate without clocks.
  for(auto step : {0,1}) { Wire w; w.init(); w.tickStep=step; w.ticks=0xfffffff0U;
    assert(emos_parallel_engine_read(&w.em,Wire::readData,data,1)==EMOS_PARALLEL_ADMISSION_TIMEOUT);
    assert(!w.falls && !w.em.busy && w.em.recordsCompleted==0);
    assert(emos_parallel_engine_read(&w.em,Wire::readData,data,1)==EMOS_PARALLEL_ADMISSION_TIMEOUT);
    ++cases;
  }
  { Wire w; w.init(); w.injectFault=true; BYTE out[8]={};
    assert(w.p4.begin(data,8,0,1000)==ParallelTxResult::pending);
    assert(emos_parallel_engine_read(&w.em,Wire::readData,out,8)==EMOS_PARALLEL_PEER_NOT_READY);
    assert(w.samples==3 && out[2]==0 && w.em.bytesCompleted==0 && !w.em.busy);
    assert(w.p4.poll(1000)==ParallelTxResult::timeout); assert(w.released); ++cases;
  }
  // Completion may be published before VALID releases, or afterwards.
  for(bool lag : {false,true}) { Wire w;
    assert(w.p4.begin(data,8,0,100)==ParallelTxResult::pending);
    assert(w.p4.begin(data,1,0,100)==ParallelTxResult::busy);
    w.tx={ParallelTxStatus::complete,8,true,false};
    assert(w.p4.poll(1)==ParallelTxResult::pending && !w.released && !w.ready);
    w.tx.ended=true;
    if(lag) {w.tx.status=ParallelTxStatus::pending; assert(w.p4.poll(2)==ParallelTxResult::pending);}
    w.tx.status=ParallelTxStatus::complete;
    assert(w.p4.poll(3)==ParallelTxResult::complete && w.released); ++cases;
  }
  { Wire w; assert(w.p4.begin(data,8,0,100)==ParallelTxResult::pending);
    w.tx={ParallelTxStatus::complete,8,true,true}; // entire block between polls
    assert(w.p4.poll(1)==ParallelTxResult::complete); ++cases;
  }
  for(unsigned fault=0;fault<7;++fault) { Wire w;
    w.failStart=fault==0; w.failStop=fault==1; w.failRelease=fault==2; w.failReady=fault==3;
    auto r=w.p4.begin(data,8,0xfffffff0U,32);
    if(r==ParallelTxResult::pending) {
      if(fault==4) w.tx={ParallelTxStatus::complete,7,true,true};
      if(fault==5) w.tx={ParallelTxStatus::complete,9,true,true};
      if(fault==6) w.tx={ParallelTxStatus::pending,0,false,true};
      r=w.p4.poll(fault>=4?0xfffffff1U:0x10U);
    }
    auto expected=fault==1||fault==2||fault==3?ParallelTxResult::cleanupFault:
      fault==4?ParallelTxResult::shortBlock:ParallelTxResult::backendFault;
    assert(r==expected && w.stopped && w.released);
    if(fault==1||fault==2) assert(!w.ready);
    assert(w.p4.begin(data,1,0,20)==expected); ++cases;
  }
  { Wire w; assert(w.p4.begin(data,8,0xfffffff0U,32)==ParallelTxResult::pending);
    assert(w.p4.poll(0xfU)==ParallelTxResult::pending);
    assert(w.p4.poll(0x10U)==ParallelTxResult::timeout); ++cases;
  }
  // DMA never completes after the read: EMOS must reject the whole block.
  { Wire w; w.init(); w.lagCompletion=true;
    assert(w.p4.begin(data,8,0,1000)==ParallelTxResult::pending);
    assert(emos_parallel_engine_read(&w.em,Wire::readData,data,8)==EMOS_PARALLEL_COMPLETION_TIMEOUT);
    assert(w.em.recordsCompleted==0 && !w.em.busy && w.valid);
    assert(w.p4.abort()==ParallelTxResult::backendFault && w.released); ++cases;
  }
  std::printf("PASS %u paired reverse-core cases (simulated wires; no hardware timing claim)\n", cases);
}
