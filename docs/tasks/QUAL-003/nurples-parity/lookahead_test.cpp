// Ownership and starvation regression checks for opt-in output lookahead.
#include <cassert>
#include <cstdlib>
#include <iostream>
#include "extender/display/presentation_snapshot_pool.hpp"
namespace d = agon::extender::display;
struct Memory { int calls{}, live{}; };
void *allocate(void *p, std::size_t n) {
  auto &m=*static_cast<Memory*>(p);++m.calls;
  void *v=std::malloc(n);if(v)++m.live;return v;
}
void release(void *p, void *v) {if(v){--static_cast<Memory*>(p)->live;std::free(v);}}
void finish(d::PresentationSnapshotPool &p) {
  assert(p.finish(d::CompositionResult::Ok,16667)==d::SnapshotFinishResult::Published);
}
int main() {
  for(bool ahead : {false,true}) {
    Memory m;
    {
      d::PresentationSnapshotPool p({&m,allocate,release},d::SnapshotPixelFormat::RGB222,0,true,true,ahead);
      assert(p.enabled() && m.calls==3 && m.live==3);
      d::MutableSnapshotView w;
      d::PresentationSnapshotLease first,blocked,second,reconnect;
      assert(p.tryBegin(16,4,0,w)==d::SnapshotBeginResult::NotRequested);
      assert(!p.tryAcquireLatest(0,first));
      assert(p.tryBegin(16,4,1,w)==d::SnapshotBeginResult::Ok);
      w.packed_pixels[0]=0x11;finish(p);
      assert(p.tryAcquireLatest(0,first));
      if(!ahead) {
        assert(p.tryBegin(16,4,2,w)==d::SnapshotBeginResult::NotRequested);
        first.release();
        assert(p.tryBegin(16,4,3,w)==d::SnapshotBeginResult::NotRequested);
        continue;
      }
      assert(p.tryBegin(16,4,2,w)==d::SnapshotBeginResult::Ok);
      w.packed_pixels[0]=0x22;
      assert(first.view().data[0]==0x11);
      assert(!p.tryAcquireLatest(1,blocked)); // held lease cannot rearm active producer
      finish(p);
      for(int i=0;i<100;++i) {
        assert(!p.tryAcquireLatest(1,blocked));
        assert(p.tryBegin(16,4,3+i,w)==d::SnapshotBeginResult::NotRequested);
      }
      assert(first.view().data[0]==0x11);first.release();
      assert(p.tryAcquireLatest(1,second));
      assert(second.view().generation==2 && second.view().data[0]==0x22);
      assert(p.tryBegin(16,4,104,w)==d::SnapshotBeginResult::Ok);
      w.packed_pixels[0]=0x33;
      second.release(); // disconnect with a future producer already active
      assert(p.tryAcquireLatest(0,reconnect)); // reconnect leases retained bytes
      assert(reconnect.view().generation==2 && reconnect.view().data[0]==0x22);
      finish(p);
      assert(p.tryBegin(16,4,105,w)==d::SnapshotBeginResult::NotRequested);
      assert(reconnect.view().data[0]==0x22);reconnect.release();
      assert(p.tryBegin(16,4,106,w)==d::SnapshotBeginResult::NotRequested);
      assert(p.metrics().publications==3 && m.calls==3 && m.live==3);
    }
    assert(m.live==0);
  }
  std::cout << "lookahead ownership/demand=pass\n";
}
