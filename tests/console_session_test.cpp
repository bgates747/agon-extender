#include <cassert>
#include <cstring>
#include "extender/transport/console_session.hpp"
using agon::extender::transport::ConsoleSession;
int main() {
  uint8_t p[16]={'E','X',1,CONSOLE_PREPARE,1,0,0,0,0,0,0,0,1,0,0,0},reply[16];
  console_seal(p);const auto original=p[14];ConsoleSession s;
  for(unsigned byte=0;byte<16;++byte)for(unsigned bit=0;bit<8;++bit) {
    uint8_t bad[16];std::memcpy(bad,p,16);bad[byte]^=1<<bit;
    assert(!s.request(bad,1,0x12345678,reply));assert(!s.active());
  }
  assert(p[14]==original && s.request(p,2,0x12345678,reply));assert(!s.active());
  assert(console_valid(reply) && reply[3]==0x81 && reply[8]==0x78 && reply[11]==0x12);
  std::memcpy(p+8,reply+8,4);p[3]=CONSOLE_COMMIT;console_seal(p);
  uint8_t stale[16];std::memcpy(stale,p,16);stale[4]=2;console_seal(stale);
  assert(!s.request(stale,3,0,reply) && !s.active());
  assert(s.request(p,3,0,reply) && s.active());
  assert(!s.request(p,4,0,reply)); // no replayed commit
  p[3]=CONSOLE_LEAVE;console_seal(p);assert(s.request(p,5,0,reply) && !s.active());
  p[3]=CONSOLE_PREPARE;std::memset(p+8,0,4);console_seal(p);
  assert(s.request(p,0xFFFFFFF0,99,reply));
  std::memcpy(p+8,reply+8,4);p[3]=CONSOLE_COMMIT;console_seal(p);
  assert(!s.request(p,2000,0,reply) && !s.active()); // elapsed time wraps safely
  p[3]=CONSOLE_PREPARE;std::memset(p+8,0,4);console_seal(p);
  assert(s.request(p,3000,100,reply));
  std::memcpy(p+8,reply+8,4);p[3]=CONSOLE_ABORT;console_seal(p);
  assert(s.request(p,3001,0,reply) && !s.active());
  p[3]=CONSOLE_COMMIT;console_seal(p);assert(!s.request(p,3002,0,reply));
}
