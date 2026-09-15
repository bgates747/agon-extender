#define AGON_EXTENDER_REFRESH_TRACE 1
#define NP_TRACE_HOST 1
#include "extender/diagnostics/refresh_trace.hpp"
#include <cassert>
#include <array>
using namespace agon_refresh_trace;
int main(){
 std::array<Sample,Capacity+1> s{};s.back()={123,456};
 uint8_t nonce[8]={1,2,3,4,5,6,7,8},wrong[8]={};Recorder r;
 assert(!r.begin(nonce,nullptr));assert(r.begin(nonce,s.data()));
 assert(!r.begin(wrong,s.data()));
 r.enqueue(10);r.enqueue(20);r.complete(30);r.complete(40);
 assert(!r.stop(wrong));assert(r.active);assert(r.stop(nonce));
 assert(!r.invalid && r.maximum_pending==2 && r.completed==2);
 assert(s[0].enqueue_us==10 && s[0].complete_us==30);
 r.enqueue(50);r.complete(60);assert(r.submitted==2 && r.completed==2);
 assert(r.begin(nonce,s.data()));r.complete(1);assert(r.stop(nonce)&&r.invalid);
 assert(r.begin(nonce,s.data()));r.enqueue(1);assert(r.stop(nonce)&&r.invalid);
 assert(r.begin(nonce,s.data()));
 for(unsigned i=0;i<Capacity+3;++i){r.enqueue(i);r.complete(i+1);}
 assert(r.stop(nonce)&&r.invalid && r.submitted==Capacity+3);
 assert(s.back().enqueue_us==123 && s.back().complete_us==456);
 marker(nonce,8);assert(!recorder.active);
 uint8_t start[16]={'N','P','T','R','A','C','E','1'};
 std::memcpy(start+8,nonce,8);marker(start,16);assert(recorder.active);
 uint8_t stop[16]={'N','P','T','R','A','C','E','0'};
 marker(stop,16);assert(recorder.active);std::memcpy(stop+8,nonce,8);
 marker(stop,16);assert(!recorder.active);
 std::puts("refresh trace bounds, identity, balance and marker checks passed");
}
