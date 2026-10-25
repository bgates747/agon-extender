// Pure bounded controller receiver. Caller serializes operations; no I/O/UART.
#pragma once
#include "wire.hpp"
namespace agon::extender::controller {
struct Endpoint {
  std::uint32_t address{};std::uint16_t port{};
  bool operator==(Endpoint b)const{return address==b.address&&port==b.port;}
};
enum class Fault:std::uint32_t { None=0, Closed=1, Timeout=2, Link=3, Overflow=4, Source=5 };
struct Snapshot {
  State state{};bool active{},valid{};
  std::uint64_t instance{},session{},last_state{};
  std::uint32_t sequence{},edge_ack{},received{},rejected{},queued{},consumed{};
  Fault fault=Fault::None;
};
class Receiver {
 public:
  void begin(std::uint64_t instance){*this=Receiver{};snapshot_.instance=instance;}
  void expire(std::uint64_t now){
    if(snapshot_.active&&now>=last_fresh_&&now-last_fresh_>=timeout_)invalidate(Fault::Timeout);
  }
  // Same open nonce/arguments is idempotent while active, never a lease refresh.
  int open(std::uint64_t instance,std::uint64_t nonce,Endpoint endpoint,unsigned timeout,
           std::uint64_t token,std::uint64_t now){
    expire(now);
    if(instance!=snapshot_.instance||!nonce||!token||!endpoint.port||timeout<50||timeout>2000)return 400;
    if(snapshot_.active)return nonce==nonce_&&endpoint==endpoint_&&timeout==timeout_?200:409;
    if(nonce==nonce_)return 410;
    nonce_=nonce;endpoint_=endpoint;timeout_=timeout;last_fresh_=now;
    const auto epoch=snapshot_.instance; snapshot_=Snapshot{};
    snapshot_.instance=epoch;snapshot_.session=token;snapshot_.active=true;
    snapshot_.fault=Fault::None;head_=size_=0;return 200;
  }
  int close(std::uint64_t instance,std::uint64_t session){
    if(instance!=snapshot_.instance||!session||session!=snapshot_.session)return 409;
    if(snapshot_.active)invalidate(Fault::Closed);
    return 200;
  }
  void invalidate(Fault fault){
    snapshot_.active=snapshot_.valid=false;snapshot_.state=State{};
    snapshot_.fault=fault;head_=size_=0;snapshot_.queued=0;
  }
  const Snapshot& snapshot(std::uint64_t now){expire(now);return snapshot_;}
  // Initialization from first held state does not manufacture press events.
  bool receive(const Packet&p,Endpoint source,std::uint64_t now,
               std::array<std::uint8_t,40>&ack){
    expire(now);
    if(!snapshot_.active||p.instance!=snapshot_.instance||p.session!=snapshot_.session||!(source==endpoint_)){
      ++snapshot_.rejected;return false;
    }
    if(p.sequence<=snapshot_.sequence){
      ++snapshot_.rejected;
      if(p.sequence==snapshot_.sequence){ack=reply(p,snapshot_.edge_ack);return true;}
      return false;
    }
    if(p.age>50){++snapshot_.rejected;return false;}
    unsigned fresh=0;
    auto next=snapshot_.edge_ack;
    for(unsigned i=0;i<p.count;++i){
      const auto&e=p.edges[i];
      if(e.sequence<=next)continue;
      if(e.sequence!=next+1)break;
      ++fresh;next=e.sequence;
    }
    if(size_+fresh>Capacity){invalidate(Fault::Overflow);ack=reply(p,0,unsigned(Fault::Overflow));return true;}
    for(unsigned i=0;i<p.count;++i){
      auto e=p.edges[i];if(e.sequence<=snapshot_.edge_ack)continue;
      if(e.sequence!=snapshot_.edge_ack+1)break;
      queue_[(head_+size_)%Capacity]=e;++size_;snapshot_.edge_ack=e.sequence;
    }
    snapshot_.state=p.state;snapshot_.valid=true;snapshot_.sequence=p.sequence;
    snapshot_.last_state=last_fresh_=now;++snapshot_.received;snapshot_.queued=size_;
    ack=reply(p,snapshot_.edge_ack);return true;
  }
  bool consume(Edge&e){
    if(!size_)return false;
    e=queue_[head_];head_=(head_+1)%Capacity;--size_;
    snapshot_.queued=size_;++snapshot_.consumed;return true;
  }
  bool peek(unsigned index,Edge&e)const{
    if(index>=size_)return false;
    e=queue_[(head_+index)%Capacity];return true;
  }
  bool retire(std::uint32_t acknowledged){
    if(acknowledged>snapshot_.edge_ack)return false;
    Edge edge;
    while(size_&&queue_[head_].sequence<=acknowledged)consume(edge);
    return true;
  }
 private:
  Snapshot snapshot_{};
  Endpoint endpoint_{};
  std::uint64_t nonce_{},last_fresh_{};
  unsigned timeout_=250,head_{},size_{};
  std::array<Edge,Capacity>queue_{};
};
}
