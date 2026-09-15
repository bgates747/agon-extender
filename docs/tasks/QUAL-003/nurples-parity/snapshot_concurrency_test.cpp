// Concurrent immutable-lease regression; not a simulation of RTOS priorities.
#include <atomic>
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <thread>
#include "extender/display/presentation_snapshot_pool.hpp"
namespace d = agon::extender::display;
int main() {
 d::PresentationSnapshotPool p({nullptr, [](void*,size_t n){return std::malloc(n);},
  [](void*,void* v){std::free(v);}}, d::SnapshotPixelFormat::RGB222,0,false,true);
 assert(p.enabled());std::atomic<bool> done{false};unsigned received=0;
 std::thread consumer([&]{
  uint64_t last=0;
  while (!done.load() || received==0) {
   d::PresentationSnapshotLease lease;
   if (!p.tryAcquireLatest(last,lease)) {std::this_thread::yield();continue;}
   auto v=lease.view();assert(v.generation>last && v.payload_bytes==32);last=v.generation;
   unsigned char saved[32];std::memcpy(saved,v.data,32);
   std::this_thread::yield();assert(std::memcmp(saved,v.data,32)==0);
   for(auto b:saved) { assert(b==saved[0]); }
   ++received;
  }
 });
 for(unsigned i=1;i<=20000;++i) {
  d::MutableSnapshotView v{};
  if(p.tryBegin(8,4,i*16667ULL,v)!=d::SnapshotBeginResult::Ok) {std::this_thread::yield();continue;}
  std::memset(v.packed_pixels,i%64,32);p.finish(d::CompositionResult::Ok,16667);
 }
 done.store(true);consumer.join();assert(received>0);
}
