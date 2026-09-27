#include <cassert>
#include "extender/diagnostics/admission/peer.hpp"
using namespace agon::extender::storage;
int main(){
 AdmissionProbe p;uint8_t r[48]{},out[48];
 sd_header(r,4,1,1,1,0,28);r[46]=1;sd_seal(r);
 assert(p.receive(r,48,0,17,23));assert(p.take(out)==48&&out[46]==5);
 r[12]=2;r[46]=0;memcpy(r+20,out+20,8);sd_put32(r+28,1);sd_seal(r);
 assert(p.receive(r,48,10,0,0));assert(p.take(out)==48&&out[13]==1);
 assert(p.arm(1,11));assert(p.receive(r,48,12,0,0));p.take(out);assert(out[32]&&out[44]==1);
 memcpy(r,out,48);r[3]=4;r[12]=3;r[36]=1;sd_seal(r);
 assert(p.receive(r,48,13,0,0));p.take(out);assert(p.decides==1);
 r[12]=10;r[13]=7;sd_seal(r);p.receive(r,48,14,0,0);p.take(out);assert(p.closes==1&&p.last==7);
 assert(!p.arm(1,300));assert(!p.arm(4,15));
 r[12]=2;r[13]=0;memset(r+32,0,16);sd_seal(r);p.receive(r,48,400,0,0);p.take(out);
 assert(p.arm(2,401));p.receive(r,48,402,0,0);p.take(out);assert(sd_u32(out+16)!=(sd_crc_update(sd_crc_update(0xffffffffU,out,16),out+20,28)^0xffffffffU));
}
