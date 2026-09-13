// BENCH-001 bounded latest snapshot. Caller owns synchronization.
#pragma once
#include <cstdint>
#include <cstring>
namespace agon::extender::telemetry {
constexpr unsigned SnapshotSize=140;
inline std::uint32_t u32(const std::uint8_t *p) {
  return std::uint32_t(p[0])|(std::uint32_t(p[1])<<8)|(std::uint32_t(p[2])<<16)|(std::uint32_t(p[3])<<24);
}
inline std::uint32_t crc32(const std::uint8_t *p,unsigned n) {
  std::uint32_t c=~0u;
  while(n--) {c^=*p++;for(unsigned bit=0;bit<8;++bit)c=(c>>1)^(0xedb88320u&std::uint32_t(-int(c&1)));}
  return ~c;
}
struct Snapshot {
  std::uint8_t bytes[SnapshotSize]{};
  std::uint32_t seen{},received{};
  bool valid{};
  std::uint32_t age(std::uint32_t now) const {
    const auto elapsed=std::int32_t(now-seen);return elapsed<0?0:std::uint32_t(elapsed);
  }
  bool online(std::uint32_t now) const {return valid && age(now)<500;}
};
class Latest {
 public:
  bool receive(const std::uint8_t *p,unsigned n,std::uint32_t now) {
    if(n!=SnapshotSize || p[0]!='R' || p[1]!='T' || p[2]!=2 ||
       p[51] || p[79] || p[80]!=6 || (p[81]&0xc0) || p[82]!=12 || p[83]!=16 ||
       crc32(p,136)!=u32(p+136))return false;
    if(value_.valid && u32(p+4)==u32(value_.bytes+4) &&
       std::int32_t(u32(p+8)-u32(value_.bytes+8))<=0)return false;
    std::memcpy(value_.bytes,p,n);value_.seen=now;++value_.received;value_.valid=true;
    return true;
  }
  Snapshot snapshot() const {return value_;}
  void reset() {value_.valid=false;}
 private:
  Snapshot value_;
};
}
