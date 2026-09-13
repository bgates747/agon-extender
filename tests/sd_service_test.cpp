#include <cassert>
#include <cstring>
#include "extender/storage/sd_service.hpp"
using agon::extender::storage::SdService;
int main() {
  SdService s;unsigned n=99;unsigned char req[240]{},other[240]{},out[240]{};
  sd_header(req,SD_REQUEST,3,1,SD_HELLO,0,0);sd_seal(req);
  assert(s.post(req,20,out,n,0)==503 && n==0);
  sd_header(other,SD_PRESENCE,11,0,0,0,0);sd_seal(other);
  assert(s.receive(other,20,0) && s.online(0));
  assert(s.post(req,20,out,n,1)==202);
  assert(s.take(out,1)==20 && !std::memcmp(out,req,20));
  assert(s.take(out,399)==0);
  assert(s.take(out,401)==20); // Lost response retransmits the identical request.
  assert(s.post(req,20,out,n,402)==202);
  req[12]=SD_STAT;sd_seal(req);assert(s.post(req,20,out,n,402)==409);
  req[12]=SD_HELLO;sd_put32(req+8,2);sd_seal(req);
  assert(s.post(req,20,out,n,402)==409); // Queue cannot grow behind pending I/O.
  sd_header(other,SD_RESPONSE,3,1,SD_HELLO,0,0);sd_seal(other);
  assert(s.receive(other,20,410));
  sd_put32(req+8,1);sd_seal(req);
  assert(s.post(req,20,out,n,411)==200 && n==20 && out[3]==SD_RESPONSE);
  assert(s.take(out,900)==0); // Cached completion is not another UART operation.
  assert(!s.receive(other,20,412)); // Late duplicate is harmless.
  assert(!s.online(5410));
  assert(s.post(req,20,out,n,5410)==200); // Completion survives lease expiry.
  sd_header(other,SD_PRESENCE,12,0,0,0,0);sd_seal(other);
  assert(s.receive(other,20,5500));
  assert(s.post(req,20,out,n,5501)==202); // New boot invalidated old cached result.
  sd_header(other,SD_RESPONSE,4,1,SD_HELLO,0,0);sd_seal(other);
  assert(!s.receive(other,20,5502)); // Wrong host session cannot complete it.
  other[0]^=1;assert(!s.receive(other,20,5502));
  sd_header(other,SD_PRESENCE,13,0,0,0,0);sd_seal(other);
  assert(s.receive(other,20,0xfffffff0U));
  assert(s.online(10) && !s.online(6000)); // Millisecond wrap is bounded.
}
