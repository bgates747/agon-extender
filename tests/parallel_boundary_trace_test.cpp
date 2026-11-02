#define AGON_EXTENDER_PARALLEL_BOUNDARY_TRACE 1
#define NP_TRACE_HOST 1
#include "parallel_boundary_trace.hpp"
#include <cassert>
#include <thread>
using namespace agon_parallel_boundary;
int main(){
 auto copy=std::make_unique<Snapshot>();
 assert(!snapshot(*copy));start();assert(!snapshot(*copy));assert(prepare());assert(prepare());start();assert(!snapshot(*copy));
 {Adjustment wrong(123);assert(!observing());}
 {Adjustment a(57600);a.tag(194,4086);assert(observing());
  acquired(46000);acquired(2);
  std::thread other([]{assert(!observing());});other.join();
 }
 uint8_t packet[16]{};packet[8]=7;packet[10]=1;
 offer(packet);offer(packet);accepted();retired();stop();
 assert(snapshot(*copy));assert(copy->adjustment_count==1 && copy->offer_count==1);
 assert(copy->adjusts[0].calls==2 && copy->adjusts[0].wait_total==46002 && copy->adjusts[0].wait_max==46000);
 assert(copy->offers[0].attempts==2 && copy->offers[0].accepted && copy->offers[0].retired);
 assert(json().find("46002")!=std::string::npos);
 start();for(int i=0;i<65;++i){Adjustment a(57600);a.tag(2,1);}stop();assert(snapshot(*copy));assert(copy->adjustment_count==64 && copy->dropped==1);
 start();{Adjustment a(57600);stop();}assert(snapshot(*copy));assert(copy->invalid);
 puts("PASS: task-filtered bounded records, aggregate waits, offer retries, STOP publication, overflow and invalid live STOP");
}
