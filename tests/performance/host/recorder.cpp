#include "frame_records.hpp"
#include <cassert>
using namespace agon_frame_records;
int main() {
 Recorder r;assert(!r.begin(0,0));r.reset();assert(r.begin(0,100));assert(r.end(0,120,145));assert(!r.get(0));
 assert(r.stop());auto p=r.get(0);assert(p && p->submitted_us==20 && p->completed_us==45 && p->drain_us==25);
 assert(!r.begin(1,200));assert(r.fault());r.reset();
 assert(r.begin(0,0xfffffff0));assert(r.end(0,5,15));assert(r.stop());assert(r.get(0)->completed_us==31);
 r.reset();assert(!r.end(0,1,2));assert(r.fault());
 r.reset();assert(!r.begin(1,0));
 r.reset();assert(r.begin(0,0));assert(!r.stop());
 r.reset();for(unsigned i=0;i<Capacity;i++){assert(r.begin(i,i));assert(r.end(i,i+1,i+2));}
 assert(!r.begin(Capacity,1000));assert(r.fault());
 r.reset();assert(r.stop());assert(!r.get(0));
}
