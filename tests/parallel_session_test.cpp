// Execute real EMOS/P4 session owners; no GPIO or UART traffic is generated.
#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
extern "C" {
#include "emos_parallel_handover.h"
}
#include "extender/transport/p4_parallel_handover.hpp"
#include "extender/transport/console_session.hpp"
using P=agon::extender::transport::P4ParallelHandover;
using Packet=std::array<unsigned char,16>;
static unsigned char reserved=1;
extern "C" unsigned char emos_keyboard_parallel_reserved(void){return reserved;}
static std::ofstream vectors;
static unsigned cases=0;
static void dump(const unsigned char *p,unsigned n){for(unsigned i=0;i<n;i++)vectors<<unsigned(p[i])<<' ';}
static unsigned char call(unsigned op,t_emosParallelHandover &h,t_parallelSession &s,
                          Packet a={},Packet b={},unsigned char mode=3){
  Packet out;out.fill(0xa5);auto hb=h;auto sb=s;unsigned char r=0;
  if(op==1)r=emos_parallel_session_start(&h,&s,a.data(),out.data());
  if(op==2)r=emos_parallel_session_accept(&h,&s,a.data(),out.data());
  if(op==3)r=emos_parallel_session_admit(&h,mode,&s,a.data(),b.data());
  if(op==4)emos_parallel_session_cancel(&h,&s);
  if(vectors.is_open()){
    vectors<<op<<' '<<unsigned(reserved)<<' '<<unsigned(mode)<<' ';
    dump(reinterpret_cast<unsigned char *>(&hb),4);dump(reinterpret_cast<unsigned char *>(&sb),11);
    dump(a.data(),16);dump(b.data(),16);Packet before;before.fill(0xa5);dump(before.data(),16);
    vectors<<unsigned(r)<<' ';dump(reinterpret_cast<unsigned char *>(&h),4);
    dump(reinterpret_cast<unsigned char *>(&s),11);dump(out.data(),16);vectors<<'\n';
  }
  ++cases;return r;
}
static P ready(){P p;for(auto c:std::array<unsigned char,5>{P::released|P::validHigh,P::validHigh,0,P::validHigh,P::validHigh|P::uartUp})p.step(c);assert(p.phase()==P::uart);return p;}
static t_emosParallelHandover eh(){return {EPH_UART,1,0,1};}
static void seal(Packet &p){parallel_session_seal(p.data());}
static Packet tx(unsigned n){Packet p{};p[0]=n;p[1]=n>>8;return p;}
static Packet offer(const t_parallelSession &s,unsigned length,unsigned dir){
  Packet p{};p[0]='E';p[1]='X';p[2]=2;p[3]=2;std::memcpy(p.data()+4,s.bytes,4);
  p[8]=1;p[10]=length;p[11]=length>>8;p[12]=dir;seal(p);return p;
}
static bool peer(P &p,t_parallelSession &s,const Packet &r,const Packet &n,Packet &out,unsigned mode=3){
  auto old=s;Packet sentinel;sentinel.fill(0xa5);out=sentinel;
  bool ok=p.sessionRequest(mode,s,r.data(),n.data(),out.data());
  if(!ok){assert(!std::memcmp(&old,&s,11));assert(out==sentinel);}++cases;return ok;
}
int main(int argc,char **argv){
  static_assert(sizeof(t_parallelSession)==11);static_assert(sizeof(t_emosParallelHandover)==4);
  if(argc==2)vectors.open(argv[1]);
  Packet nonce=tx(0x1234),request{},reply{},commit{},ack{};
  auto h=eh();P p=ready();t_parallelSession e{},s{};
  auto eold=e;reserved=0;assert(!call(1,h,e,tx(1)));assert(!std::memcmp(&e,&eold,11));reserved=1;
  h.phase=EPH_RETURN_REQUEST;assert(!call(1,h,e,tx(1)));h=eh();assert(!call(1,h,e));
  assert(call(1,h,e,tx(1))==1);parallel_session_begin(&eold,tx(1).data(),request.data());
  assert(e.phase==1);assert(!call(1,h,e,tx(2))); // no nested prepare
  P cold;t_parallelSession coldstate{};assert(!peer(cold,coldstate,request,nonce,reply));
  for(unsigned mode:{0u,1u,2u,4u,255u})assert(!peer(p,s,request,nonce,reply,mode));
  assert(!peer(p,s,request,Packet{},reply));
  for(unsigned i=0;i<16;i++)for(unsigned bit=0;bit<8;bit++){
    auto bad=request;bad[i]^=1u<<bit;assert(!peer(p,s,bad,nonce,reply));
    if(i<14){seal(bad);if(i==4||i==5||i==6||i==7)continue;assert(!peer(p,s,bad,nonce,reply));}
  }
  assert(peer(p,s,request,nonce,reply));assert(s.phase==4);auto prepareReply=reply;
  for(unsigned i=0;i<16;i++)for(unsigned bit=0;bit<8;bit++){
    auto bad=reply;bad[i]^=1u<<bit;auto before=e;assert(!call(2,h,e,bad));assert(!std::memcmp(&before,&e,11));
    if(i<8||i==12||i==13){seal(bad);assert(!call(2,h,e,bad));}
  }
  Packet zero=reply;std::memset(zero.data()+8,0,4);seal(zero);assert(!call(2,h,e,zero));
  reserved=0;assert(!call(2,h,e,reply));reserved=1;
  assert(call(2,h,e,reply)==2);commit=reply;commit[3]=3;seal(commit);assert(!call(2,h,e,reply));
  for(unsigned i=0;i<16;i++)for(unsigned bit=0;bit<8;bit++){
    auto bad=commit;bad[i]^=1u<<bit;assert(!peer(p,s,bad,nonce,reply));
    if(i<14){seal(bad);assert(!peer(p,s,bad,nonce,reply));}
  }
  assert(peer(p,s,commit,nonce,reply));auto commitReply=reply;
  assert(!peer(p,s,commit,nonce,ack));assert(!call(3,h,e,offer(e,1,0),ack));
  for(unsigned i=0;i<16;i++)for(unsigned bit=0;bit<8;bit++){
    auto bad=commitReply;bad[i]^=1u<<bit;assert(!call(2,h,e,bad));
    if(i<14){seal(bad);assert(!call(2,h,e,bad));}
  }
  assert(call(2,h,e,commitReply)==3);assert(!call(2,h,e,commitReply));
  assert(!std::memcmp(e.bytes,s.bytes,6));
  // Full exchange, each direction and boundary length, then actual block gates.
  for(unsigned dir:{0u,1u})for(unsigned len:{1u,2u,255u,256u,4095u,4096u}){
    h=eh();p=ready();e={};s={};assert(call(1,h,e,tx(7)));
    eold={};parallel_session_begin(&eold,tx(7).data(),request.data());
    assert(peer(p,s,request,nonce,reply));assert(call(2,h,e,reply)==2);
    commit=reply;commit[3]=3;seal(commit);assert(peer(p,s,commit,nonce,reply));assert(call(2,h,e,reply)==3);
    auto block=offer(e,len,dir);assert(p.sessionAdmit(3,s,block.data(),ack.data()));
    reserved=0;assert(!call(3,h,e,block,ack));reserved=1;
    assert(!call(3,h,e,block,ack,2));assert(call(3,h,e,block,ack));assert(e.bytes[4]==1 && s.bytes[4]==1);
    assert(!call(3,h,e,block,ack));assert(!p.sessionAdmit(3,s,block.data(),ack.data()));
    call(4,h,e);p.sessionCancel(s);assert(e.phase==0 && s.phase==0 && !e.bytes[4] && !s.bytes[4]);
    assert(h.phase==EPH_RETURN_RELEASE && p.phase()==P::recoveryRelease);
    h=eh();p=ready();assert(!call(3,h,e,block,ack));assert(!p.sessionAdmit(3,s,block.data(),ack.data()));
    assert(call(1,h,e,tx(8)));eold={};parallel_session_begin(&eold,tx(8).data(),request.data());
    assert(!peer(p,s,request,nonce,reply));auto next=tx(0x5678);assert(peer(p,s,request,next,reply));
    assert(!call(2,h,e,prepareReply));assert(call(2,h,e,reply)==2);
    assert(!call(2,h,e,commitReply));call(4,h,e);p.sessionCancel(s);
  }
  // Cancel at every session phase; retained nonce must never grant a block.
  for(unsigned phase=0;phase<=4;phase++){
    h=eh();p=ready();e={};s={};e.phase=s.phase=phase;
    std::memcpy(e.bytes,nonce.data(),4);std::memcpy(s.bytes,nonce.data(),4);
    e.bytes[4]=s.bytes[4]=19;call(4,h,e);p.sessionCancel(s);
    assert(e.phase==0 && s.phase==0 && !e.bytes[4] && !s.bytes[4]);
    h=eh();p=ready();auto block=offer(e,1,0);
    assert(!call(3,h,e,block,ack));assert(!p.sessionAdmit(3,s,block.data(),ack.data()));
    assert(!call(2,h,e,commitReply));
  }
  // Capability negotiation cannot be mistaken for the existing v1 console.
  agon::extender::transport::ConsoleSession console;
  Packet untouched;untouched.fill(0xa5);auto before=untouched;
  assert(!console.request(request.data(),0,1,untouched.data()));assert(untouched==before);
  std::cout<<"PASS "<<cases<<" session-owner checks; prepare/commit, admission, malformed/stale/replayed records, reservation, release and cancellation\n";
}
