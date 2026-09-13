#include "extender/telemetry/latest.hpp"
#include <cassert>
#include <cstdio>
using namespace agon::extender::telemetry;
static void put(uint8_t *p,uint32_t n){for(unsigned i=0;i<4;++i)p[i]=n>>(8*i);}
static void seal(uint8_t *p){put(p+136,crc32(p,136));}
int main(){
 Latest latest;uint8_t p[140]{};p[0]='R';p[1]='T';p[2]=2;p[80]=6;p[82]=12;p[83]=16;put(p+4,123);put(p+8,5);seal(p);
 assert(!latest.snapshot().online(0));
 for(unsigned n=0;n<140;++n)assert(!latest.receive(p,n,100));
 assert(latest.receive(p,140,100));
 const auto original=latest.snapshot();
 assert(original.online(599)&&!original.online(600));
 assert(original.age(99)==0); // Clock sampled just before the copied receive stamp.
 for(unsigned byte=0;byte<140;++byte){p[byte]^=1;assert(!latest.receive(p,140,150));p[byte]^=1;}
 assert(!latest.receive(p,140,200)); // Duplicate never refreshes age.
 assert(latest.snapshot().received==1&&latest.snapshot().seen==100);
 put(p+8,4);seal(p);assert(!latest.receive(p,140,200));
 put(p+8,6);seal(p);assert(latest.receive(p,140,200));
 p[51]=1;seal(p);assert(!latest.receive(p,140,201));p[51]=0;
 p[79]=1;seal(p);assert(!latest.receive(p,140,201));p[79]=0;
 // A new run can restart its sequence, then advance across uint32 wrap.
 put(p+4,124);put(p+8,0xffffffff);seal(p);assert(latest.receive(p,140,0xfffffff0));
 put(p+8,0);seal(p);assert(latest.receive(p,140,0xfffffff8));
 assert(latest.snapshot().age(8)==16);
 p[24]=99;assert(latest.snapshot().bytes[24]!=99); // Core owns the copy.
 latest.reset();assert(!latest.snapshot().online(8));
 std::puts("PASS: complete CRC snapshots, stale/duplicate rejection, clock/frame wrap, reset, copy isolation");
}
