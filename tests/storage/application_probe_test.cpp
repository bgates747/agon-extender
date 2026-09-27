#include <cassert>
#include "extender/diagnostics/admission/peer.hpp"
using namespace agon::extender::storage;
int main(){
 AdmissionProbe p;uint8_t r[240]{},out[240],prefix[28]{};unsigned seq=0;
 sd_header(r,4,19,++seq,1,0,28);r[46]=1;sd_seal(r);p.receive(r,48,0,17,23);assert(p.take(out)==48&&out[46]==13);
 memcpy(prefix,out+20,8);sd_put32(prefix+8,19);sd_put32(prefix+16,19);sd_put32(prefix+20,19);prefix[24]=2;
 for(unsigned direction=3;direction<=4;++direction){
  prefix[25]=direction;sd_put32(prefix+12,0);
  const char *local="/agents/extender/results/a05-in.bin",*remote=direction==3?"/p4/source.bin":"/p4/output.bin";
  const char *src=direction==3?remote:local,*dst=direction==3?local:remote;
  uint8_t desc[248]{};unsigned sl=strlen(src),dl=strlen(dst),length=sl+dl+8;
  desc[0]=direction;sd_put16(desc+2,sl);sd_put16(desc+4,dl);memcpy(desc+8,src,sl);memcpy(desc+8+sl,dst,dl);
  sd_header(r,4,19,++seq,5,0,36+length);memcpy(r+20,prefix,28);sd_put16(r+48,length);sd_put16(r+50,0);sd_put32(r+52,sd_crc(desc,length));memcpy(r+56,desc,length);sd_seal(r);
  assert(p.receive(r,56+length,0,0,0));assert(p.take(out)==48 && out[13]==0);memcpy(prefix,out+20,28);
  assert(!p.arm(1,0)&&p.application.blocked);
  sd_header(r,4,19,++seq,4,0,28);memcpy(r+20,prefix,28);sd_seal(r);p.receive(r,48,0,0,0);assert(p.take(out)==48);
  uint32_t sid=sd_crc(prefix,28);if(!sid)sid=1;unsigned fs=0;
  auto send=[&](unsigned op,unsigned len){sd_header(r,1,sid,++fs,op,0,len);sd_seal(r);assert(p.receive(r,20+len,0,0,0));unsigned n=p.take(out);assert(n>=20 && out[13]==0);return n;};
  send(1,0);
  if(direction==3){
   sd_put32(r+20,0);sd_put16(r+24,212);r[26]=14;memcpy(r+27,remote,14);assert(send(4,21)==236);assert(sd_u32(out+20)==1027);for(unsigned i=0;i<212;i++)assert(out[24+i]==uint8_t(i*17+3));
  }else{
   uint8_t bytes[1027];for(unsigned i=0;i<1027;i++)bytes[i]=i*17+3;
   sd_put32(r+20,19);sd_put32(r+24,1027);sd_put32(r+28,sd_crc(bytes,1027));r[32]=14;memcpy(r+33,remote,14);send(5,27);
   for(unsigned at=0;at<1027;){unsigned n=1027-at;if(n>212)n=212;sd_put32(r+20,19);sd_put32(r+24,at);memcpy(r+28,bytes+at,n);send(6,n+8);at+=n;}
   sd_put32(r+20,19);send(7,4);send(8,4);assert(p.application.complete==1);
  }
  sd_header(r,4,19,++seq,10,0,28);memcpy(r+20,prefix,28);sd_seal(r);p.receive(r,48,0,0,0);p.take(out);assert(!p.application.active);
 }
}
