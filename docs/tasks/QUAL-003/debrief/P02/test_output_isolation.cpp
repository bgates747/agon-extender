#define NP_TRACE_HOST
#define AGON_EXTENDER_OUTPUT_ISOLATION
#include "extender/diagnostics/output_isolation.hpp"
#include <cassert>
#include <vector>
#include <thread>
using namespace agon_output_isolation;
int main(){
 uint8_t n[8]={'P','0','2',2,1,2,3,4};
 assert(begin(n));assert(mode==Mode::Discard);assert(!begin(n));
 {Scope a(Phase::Compose);a.finish(196608);}
 {Scope b(Phase::Send);}
 assert(totals[0].calls==1&&totals[0].units==196608&&totals[2].failures==1);
 std::atomic<bool> entered{};
 std::thread t([&]{Scope a(Phase::Compose);entered=true;std::this_thread::sleep_for(std::chrono::milliseconds(10));a.finish(10);});
 while(!entered){std::this_thread::yield();}
 stop(n);t.join();
 assert(!invalid&&in_flight==0&&totals[0].calls==2&&mode==Mode::Normal);
 n[3]=4;assert(!begin(n));assert(mode==Mode::Normal);n[3]=3;assert(begin(n));stop(n);
 PrebuiltSlots cache;std::vector<uint8_t> a(512*384,0),b(a.size()),c(a.size()),d(a.size());
 assert(cache.prepare(a.data(),512,384));assert(a[0]==3&&a[512*16]==60);
 a[0]=42;assert(cache.prepare(a.data(),512,384)&&a[0]==42); // no recopy
 cache.invalidate(a.data());assert(cache.prepare(a.data(),512,384)&&a[0]==3);
 assert(cache.prepare(b.data(),512,384));assert(cache.prepare(c.data(),512,384));assert(!cache.prepare(d.data(),512,384));
 assert(!cache.prepare(a.data(),1025,384));assert(cache.prepare(a.data(),256,384));
}
