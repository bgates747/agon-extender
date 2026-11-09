// NET-008 test-only CRC32 framing. Smith explicitly authorizes CRC at the
// P4/Pi5 endpoints of these modem transfers; this is not EMOS control framing.
#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
namespace n8bw {
constexpr size_t payload_size=1024,header_size=16,max_frame=1040;
constexpr uint32_t up_salt=0x13579bdf,down_salt=0x2468ace0;
inline uint32_t crc(const void *data,size_t n,uint32_t seed=0) {
 uint32_t c=~seed;const auto *p=static_cast<const uint8_t *>(data);
 for(size_t i=0;i<n;++i){c^=p[i];for(int b=0;b<8;++b)c=(c>>1)^(0xedb88320u&uint32_t(-int32_t(c&1)));}
 return ~c;
}
inline void put(uint8_t *p,uint32_t n){for(int i=0;i<4;++i)p[i]=uint8_t(n>>(i*8));}
inline uint32_t get(const uint8_t *p){return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);}
inline void pattern(uint8_t *p,size_t n,uint32_t seq,uint32_t salt) {
 uint32_t x=(seq*0x9e3779b9u)^salt;
 for(size_t i=0;i<n;++i){x^=x<<13;x^=x>>17;x^=x<<5;p[i]=uint8_t(x>>24);if(p[i]==0x2b)p[i]=0x2c;}
}
inline size_t frame(uint8_t *out,uint32_t seq,const void *data,size_t n) {
 if(n>payload_size)return 0;
 memcpy(out,"N8BW",4);put(out+4,seq);put(out+8,uint32_t(n));
 if(n)memcpy(out+16,data,n);
 put(out+12,crc(out+16,n,crc(out,12)));return 16+n;
}
inline bool valid(const uint8_t *p,size_t n) {
 return n>=16&&!memcmp(p,"N8BW",4)&&get(p+8)<=payload_size&&n==16+get(p+8)&&get(p+12)==crc(p+16,n-16,crc(p,12));
}
}
