// Developmental controller LAN protocol 1. Explicit bytes, never a C-struct ABI.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
namespace agon::extender::controller {
constexpr std::size_t Header=32, MaxEdges=16, Capacity=128, MaxPacket=176;
constexpr std::uint8_t StateKind=1, AckKind=2, FaultKind=3;
constexpr std::uint8_t Raw8=1, Native=2;
struct Edge { std::uint32_t sequence{}; std::uint8_t control{},down{}; };
struct State {
  std::array<std::int16_t,4> sticks{};
  std::array<std::uint8_t,2> triggers{};
  std::uint16_t held{};
};
struct Packet {
  std::uint64_t instance{},session{};
  std::uint32_t sequence{};
  std::uint16_t age{};
  State state;
  std::uint8_t profile{},count{};
  std::array<Edge,MaxEdges> edges{};
};
inline std::uint16_t get16(const std::uint8_t*p){return p[0]|(std::uint16_t(p[1])<<8);}
inline std::uint32_t get32(const std::uint8_t*p){return get16(p)|(std::uint32_t(get16(p+2))<<16);}
inline std::uint64_t get64(const std::uint8_t*p){return get32(p)|(std::uint64_t(get32(p+4))<<32);}
inline void put16(std::uint8_t*p,std::uint16_t v){p[0]=v;p[1]=v>>8;}
inline void put32(std::uint8_t*p,std::uint32_t v){put16(p,v);put16(p+2,v>>16);}
inline void put64(std::uint8_t*p,std::uint64_t v){put32(p,v);put32(p+4,v>>32);}
inline bool validHeld(std::uint16_t v){
  return !(v&0x8000) && (v&0x1800)!=0x1800 && (v&0x6000)!=0x6000;
}
inline bool decode(const std::uint8_t*p,std::size_t n,Packet&out){
  if(n<44||n>MaxPacket||p[0]!='A'||p[1]!='G'||p[2]!='C'||p[3]!='P'||
     p[4]!=1||p[5]!=StateKind||get16(p+6)!=n||get32(p+28))return false;
  Packet v{};v.instance=get64(p+8);v.session=get64(p+16);v.sequence=get32(p+24);
  if(!v.instance||!v.session||!v.sequence)return false;
  v.state.held=get16(p+32);v.age=get16(p+34);v.profile=p[36];v.count=p[37];
  if(!validHeld(v.state.held)||v.count>MaxEdges)return false;
  const auto analog=v.profile==Raw8?6:v.profile==Native?10:0;
  if(!analog||n!=Header+6+analog+8*v.count)return false;
  const auto*a=p+38;
  for(unsigned i=0;i<4;++i)v.state.sticks[i]=v.profile==Raw8?
    std::int16_t(int(a[i])*257-32768):std::int16_t(int(get16(a+i*2))>=32768?int(get16(a+i*2))-65536:int(get16(a+i*2)));
  v.state.triggers={a[analog-2],a[analog-1]};
  for(unsigned i=0;i<v.count;++i){
    const auto*e=a+analog+i*8;
    v.edges[i]={get32(e),e[4],e[5]};
    if(!v.edges[i].sequence||e[4]>=15||e[5]>1||get16(e+6))return false;
    if(i&&(v.edges[i-1].sequence==UINT32_MAX||v.edges[i].sequence!=v.edges[i-1].sequence+1))return false;
  }
  out=v;return true;
}
inline std::array<std::uint8_t,40> reply(const Packet&p,std::uint32_t acknowledged,std::uint32_t fault=0){
  std::array<std::uint8_t,40>b{};b[0]='A';b[1]='G';b[2]='C';b[3]='P';
  b[4]=1;b[5]=fault?FaultKind:AckKind;put16(b.data()+6,b.size());
  put64(b.data()+8,p.instance);put64(b.data()+16,p.session);put32(b.data()+24,p.sequence);
  put32(b.data()+32,p.sequence);put32(b.data()+36,fault?fault:acknowledged);return b;
}
}
