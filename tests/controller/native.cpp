#include "extender/input/controller/receiver.hpp"
#include <cassert>
#include <random>
#include <vector>
using namespace agon::extender::controller;
extern "C" {
void* cr_new(){auto*r=new Receiver;r->begin(123);return r;}
void cr_delete(void*p){delete static_cast<Receiver*>(p);}
int cr_open(void*p,unsigned address,unsigned port,unsigned timeout,unsigned long long nonce,unsigned long long now,unsigned long long token){
  return static_cast<Receiver*>(p)->open(123,nonce,{address,std::uint16_t(port)},timeout,token,now);
}
int cr_receive(void*p,const unsigned char*bytes,unsigned length,unsigned address,unsigned port,unsigned long long now,unsigned char*out){
  Packet packet;if(!decode(bytes,length,packet))return -1;
  std::array<std::uint8_t,40>ack;
  if(!static_cast<Receiver*>(p)->receive(packet,{address,std::uint16_t(port)},now,ack))return 0;
  std::copy(ack.begin(),ack.end(),out);return 40;
}
unsigned cr_field(void*p,unsigned field,unsigned long long now){
  auto&s=static_cast<Receiver*>(p)->snapshot(now);
  switch(field){case 0:return s.active;case 1:return s.valid;case 2:return s.sequence;
    case 3:return s.edge_ack;case 4:return s.queued;case 5:return unsigned(s.fault);
    case 6:return s.state.held;case 7:return std::uint16_t(s.state.sticks[0]);case 8:return s.state.triggers[0];default:return s.received;}
}
unsigned cr_consume(void*p,unsigned*out){
  Edge e;if(!static_cast<Receiver*>(p)->consume(e))return 0;
  out[0]=e.sequence;out[1]=e.control;out[2]=e.down;return 1;
}
int cr_close(void*p){return static_cast<Receiver*>(p)->close(123,456);}
void cr_link(void*p){static_cast<Receiver*>(p)->invalidate(Fault::Link);}
}
#ifdef CONTROLLER_NATIVE_MAIN
int main(){
  // Malformed wire corpus exercises the same bounded decoder as P4.
  std::mt19937 gen(17);Packet out;
  for(unsigned i=0;i<100000;++i){std::vector<std::uint8_t>b(gen()%256);
    for(auto&v:b)v=gen();
    // Half the corpus reaches fields beyond the magic/header checks.
    if(i%2&&b.size()>=44){
      b[0]='A';b[1]='G';b[2]='C';b[3]='P';b[4]=1;b[5]=StateKind;
      put16(b.data()+6,b.size());put32(b.data()+28,0);
      b[36]=Raw8;b[37]=(b.size()-44)/8;
    }
    decode(b.data(),b.size(),out);}
  Receiver r;r.begin(123);assert(r.open(123,1,{1,2},250,456,0)==200);
  Packet p{};p.instance=123;p.session=456;p.sequence=1;p.count=16;
  std::array<std::uint8_t,40>ack;
  for(unsigned batch=0;batch<8;++batch){
    p.sequence=batch+1;for(unsigned i=0;i<16;++i)p.edges[i]={batch*16+i+1,0,std::uint8_t(i%2==0)};
    assert(r.receive(p,{1,2},batch,ack));
  }
  assert(r.snapshot(8).queued==128);p.sequence=9;p.count=1;p.edges[0]={129,0,1};
  assert(r.receive(p,{1,2},9,ack));assert(!r.snapshot(9).valid&&r.snapshot(9).fault==Fault::Overflow);
  assert(!r.receive(p,{1,2},10,ack));
}
#endif
