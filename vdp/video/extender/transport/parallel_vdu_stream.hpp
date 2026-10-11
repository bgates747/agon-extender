// PORT-008 ordinary ExExt queue binding. One retained-parser task owns this
// object and the native coordinator; DMA bytes stay provisional until receipt.
// UART control is separate. No VDU parser, ISR or network writer lives here.
#pragma once
#include <array>
#include <algorithm>
#include "parallel_control.hpp"
namespace agon::extender::transport {
class ParallelVduStream final {
 public:
  explicit ParallelVduStream(ParallelControl &owner):owner_(owner) {}
  bool begin() { return owner_.provide(payload_.data(),payload_.size()); }
  bool active() const { return active_; }
  std::size_t available() const { return rxCount_; }
  std::size_t pending() const { return txCount_; }
  int read() {
    if(!rxCount_)return -1;
    auto b=rx_[rxAt_];rxAt_=(rxAt_+1)%rx_.size();--rxCount_;return b;
  }
  std::size_t read(std::uint8_t *p,std::size_t n) {
    n=std::min(n,rxCount_);std::size_t used=0;
    while(used<n) {
      auto part=std::min(n-used,rx_.size()-rxAt_);
      std::memcpy(p+used,rx_.data()+rxAt_,part);
      rxAt_=(rxAt_+part)%rx_.size();rxCount_-=part;used+=part;
    }
    return used;
  }
  bool write(std::uint8_t b) {
    if(txCount_==tx_.size())return false;
    tx_[(txAt_+txCount_)%tx_.size()]=b;++txCount_;return true;
  }
  // Operations use the negotiated six-byte session/sequence, not a bare mode
  // byte. START must be explicitly requested after a live console lease.
  bool request(const std::uint8_t *p,std::uint8_t *reply,bool consoleActive) {
    if(!consoleActive || !owner_.uartTransitionAllowed() ||
       owner_.session.phase!=PARALLEL_SESSION_ACTIVE ||
       p[0]!='E' || p[1]!='X' || p[2]!=PARALLEL_WIRE_VERSION ||
       std::memcmp(p+4,owner_.session.bytes,6) || p[10] || p[11] || p[12] || p[13])return false;
    const auto crc=console_crc(p);
    if(p[14]!=std::uint8_t(crc) || p[15]!=std::uint8_t(crc>>8))return false;
    if(p[3]==PARALLEL_STREAM_START) {
      if(active_ || rxCount_ || txCount_)return false;
      active_=true;
    } else if(p[3]==PARALLEL_STREAM_STOP) {
      if(!active_ || rxCount_ || waiting_)return false;
      // A nonzero STOP acknowledgement keeps the stream open for a final
      // reverse block. This closes the key-arrival race between POLL and STOP.
      // Only the zero-pending acknowledgement commits the UART transition.
      if(!txCount_)active_=false;
    } else if(p[3]!=PARALLEL_STREAM_POLL || !active_)return false;
    std::memcpy(reply,p,16);reply[3]|=0x80;
    const auto n=std::min<std::size_t>(txCount_,payload_.size());
    reply[10]=std::uint8_t(n);reply[11]=std::uint8_t(n>>8);
    parallel_session_seal(reply);return true;
  }
  bool canOffer(const std::uint8_t *d) const {
    const auto n=std::size_t(d[10])|(std::size_t(d[11])<<8);
    return active_ && !waiting_ && n && n<=payload_.size() &&
      (d[12]==0 ? n<=rx_.size()-rxCount_ : d[12]==1 && n<=txCount_);
  }
  bool acceptedOffer() {
    const auto *d=owner_.descriptor();if(!d || !canOffer(d))return false;
    const auto n=std::size_t(d[10])|(std::size_t(d[11])<<8);
    if(d[12])for(std::size_t i=0;i<n;++i)payload_[i]=tx_[(txAt_+i)%tx_.size()];
    waiting_=true;return true;
  }
  bool retire() {
    if(!waiting_)return true;
    std::uint8_t *p{},direction{};std::size_t n{};
    if(!owner_.takeCompleted(p,n,direction))return true;
    waiting_=false;
    if(p!=payload_.data() || !n || n>payload_.size())return false;
    if(direction) {
      if(n>txCount_)return false;
      txAt_=(txAt_+n)%tx_.size();txCount_-=n;
    } else {
      if(n>rx_.size()-rxCount_)return false;
      for(std::size_t i=0;i<n;++i)rx_[(rxAt_+rxCount_+i)%rx_.size()]=p[i];
      rxCount_+=n;
    }
    return true;
  }
  void cancel() {active_=waiting_=false;rxAt_=rxCount_=txAt_=txCount_=0;}
 private:
  ParallelControl &owner_;
  std::array<std::uint8_t,4096> payload_{};
  std::array<std::uint8_t,8192> rx_{},tx_{};
  std::size_t rxAt_{},rxCount_{},txAt_{},txCount_{};
  bool active_{},waiting_{};
};
}
