#include <cassert>
#include <cstring>
#include <vector>
#include <cstdio>
#include "extender/transport/parallel_vdu_stream.hpp"
using namespace agon::extender::transport;
using H=P4ParallelHandover;
static void boot(ParallelControl &c) {
 for(auto b:std::initializer_list<unsigned>{H::released,H::validHigh,0,H::validHigh,H::uartUp})c.handover.step(b);
 assert(c.handover.phase()==H::uart);c.session.phase=PARALLEL_SESSION_ACTIVE;
 const uint8_t s[]={1,2,3,4,0,0};memcpy(c.session.bytes,s,6);
}
static bool command(ParallelControl &c,ParallelVduStream &s,unsigned op,uint8_t *r,bool lease=true) {
 uint8_t p[16]={'E','X',2,uint8_t(op)};memcpy(p+4,c.session.bytes,6);parallel_session_seal(p);
 return s.request(p,r,lease);
}
static void block(ParallelControl &c,ParallelVduStream &s,std::vector<uint8_t> &bytes,bool reverse) {
 auto seq=unsigned(c.session.bytes[4]|(unsigned(c.session.bytes[5])<<8))+1;
 uint8_t d[16]={'E','X',2,PARALLEL_OFFER};memcpy(d+4,c.session.bytes,4);
 d[8]=uint8_t(seq);d[9]=uint8_t(seq>>8);d[10]=uint8_t(bytes.size());d[11]=uint8_t(bytes.size()>>8);d[12]=reverse;
 parallel_session_seal(d);uint8_t reply[16];assert(s.canOffer(d));assert(c.request(d,0,0,reply));assert(s.acceptedOffer());
 uint8_t *p;size_t cap;assert(c.payloadBuffer(p,cap));
 if(reverse)assert(!memcmp(p,bytes.data(),bytes.size()));else memcpy(p,bytes.data(),bytes.size());
 const auto before=s.available(),out=s.pending();assert(s.retire());assert(s.available()==before && s.pending()==out);
 for(auto b:std::initializer_list<unsigned>{H::quiet,H::released,0,H::validHigh,H::validHigh|H::clockHigh,
     H::validHigh|H::clockHigh|H::armed,H::done,H::validHigh,0,H::validHigh,H::uartUp})c.handover.step(b);
 assert(c.payloadReturned(0,1));assert(s.retire());assert(s.available()==before && s.pending()==out);
 d[3]=PARALLEL_COMPLETE;parallel_session_seal(d);assert(c.request(d,1,0,reply));assert(s.retire());
 assert(s.available()==before+(reverse?0:bytes.size()));assert(s.pending()==out-(reverse?bytes.size():0));
}
int main() {
 unsigned cases=0;ParallelControl c;boot(c);ParallelVduStream s(c);assert(s.begin());uint8_t r[16];
 assert(!command(c,s,PARALLEL_STREAM_START,r,false));assert(!s.active());
 assert(command(c,s,PARALLEL_STREAM_START,r));assert(s.active());
 assert(!command(c,s,PARALLEL_STREAM_START,r));++cases;
 // Deliberately split an upload/VDU command at every relevant block boundary;
 // the consumer sees precisely the original byte stream, including zeroes.
 for(unsigned n:{1u,2u,3u,17u,255u,256u,1024u,4096u}) {
  std::vector<uint8_t> p(n);for(unsigned i=0;i<n;++i)p[i]=uint8_t(i*73u+(i>>8));
  block(c,s,p,false);assert(!command(c,s,PARALLEL_STREAM_STOP,r));
  std::vector<uint8_t> got(n);assert(s.read(got.data(),n)==n && got==p);assert(s.read()==-1);++cases;
 }
 // A reverse block can contain partial/multiple packets; ordering is retained
 // across wrap and only a matched receipt retires bytes.
 for(unsigned n:{1u,4u,16u,255u,256u,4096u}) {
  std::vector<uint8_t> p(n);for(unsigned i=0;i<n;++i){p[i]=uint8_t(i^0x81);assert(s.write(p[i]));}
  assert(command(c,s,PARALLEL_STREAM_POLL,r));assert(unsigned(r[10]|(unsigned(r[11])<<8))==n);
  assert(command(c,s,PARALLEL_STREAM_STOP,r)&&s.active());
  assert(unsigned(r[10]|(unsigned(r[11])<<8))==n);block(c,s,p,true);++cases;
 }
 assert(command(c,s,PARALLEL_STREAM_STOP,r));assert(!s.active());
 assert(!command(c,s,PARALLEL_STREAM_POLL,r));++cases;
 assert(command(c,s,PARALLEL_STREAM_START,r));
 std::vector<uint8_t> full(4096,0xa5);block(c,s,full,false);block(c,s,full,false);
 uint8_t d[16]={'E','X',2,PARALLEL_OFFER};d[10]=1;
 assert(!s.canOffer(d));s.cancel();assert(!s.active() && !s.available() && !s.pending());++cases;
 printf("PASS %u actual queue/admission/receipt/split-stream/backpressure cases\n",cases);
}
