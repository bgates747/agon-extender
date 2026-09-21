#include <fstream>
#include <vector>
#include <string>
#include <cassert>
#include "delta_encoder.hpp"
using namespace std;
int main(int argc,char**argv){
 assert(argc==2);string root=argv[1];vector<uint8_t>prev(frame_delta::capacity),tmp(prev.size()),enc(prev.size()+14),full(enc.size());
 frame_delta::Encoder e;e.previous=prev.data();e.scratch=tmp.data();e.encoded=enc.data();
 ofstream list(root+"/cases.tsv");unsigned serial=0;uint32_t seq=100;
 auto send=[&](string label,vector<uint8_t>p,unsigned w,bool reset){
  if(reset)e.reset();uint8_t h[32]={};memcpy(h,"EVF1",4);h[4]=1;h[5]=32;h[6]=2;h[7]=3;
  rle2::put32(h+8,seq);h[12]=w;h[13]=w>>8;unsigned hh=p.size()/w;h[14]=hh;h[15]=hh>>8;rle2::put32(h+16,w);rle2::put32(h+20,p.size());rle2::put32(h+24,16667);
  auto f=rle2::encode_auto(p.data(),p.size(),full.data(),full.size(),true);size_t fs=f&&f.bytes<p.size()?f.bytes:p.size();
  size_t ds=e.prepare(h,p.data(),p.size(),fs);vector<uint8_t>wire(h,h+32);
  if(ds){wire[2]='D';rle2::put32(wire.data()+28,e.sequence);wire.insert(wire.end(),enc.begin(),enc.begin()+ds);}
  else if(fs<p.size()){wire[2]='R';wire.insert(wire.end(),full.begin(),full.begin()+fs);}
  else wire.insert(wire.end(),p.begin(),p.end());
  string n=to_string(serial++);ofstream out(root+"/"+n+".wire",ios::binary);out.write((char*)wire.data(),wire.size());ofstream expected(root+"/"+n+".pixels",ios::binary);expected.write((char*)p.data(),p.size());
  list<<n<<'\t'<<label<<'\t'<<reset<<'\t'<<(ds?'D':'F')<<'\n';
  e.commit(h,p.data(),p.size(),ds);seq+=3;return ds;
 };
 vector<uint8_t>p(64*64);for(size_t i=0;i<p.size();++i)p[i]=(i*13+i/64)%64;
 assert(!send("first",p,64,true));p[5]=0;p[10]=63;assert(send("changed-to-black",p,64,false));assert(send("unchanged",p,64,false));
 for(int i=0;i<120;++i)send("periodic",p,64,false);
 assert(!send("reconnect",p,64,true));assert(!send("dimensions",p,32,false));
 uint32_t seed=777;for(auto&v:p){seed=seed*1664525+1013904223;v=(seed>>24)&63;}
 assert(!send("noise-full-fallback",p,32,false));seq=0xffffffff;send("wrap-base",p,32,false);p[100]^=1;assert(send("wrap-delta",p,32,false));
 assert(!send("send-failure-recovery",p,32,true));
}
