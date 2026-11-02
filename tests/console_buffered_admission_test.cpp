// Actual ConsoleStream, queue and physical control. Only SDK/Arduino I/O is fake.
#include <cassert>
#include <cstdio>
#include <vector>
#include "extender/transport/console_stream.hpp"
using namespace agon::extender::transport;
static unsigned clockNow,sleeps,uartReads;
unsigned millis(){return clockNow++;}
void vTaskDelay(unsigned n){assert(n==1);++sleeps;}
int uart_read_bytes(int,void *p,unsigned n,int){++uartReads;if(n)*static_cast<uint8_t*>(p)=0xa7;return n?1:0;}
esp_err_t uart_get_buffered_data_len(int,std::size_t *n){*n=1;return ESP_OK;}
using H=P4ParallelHandover;
static void start(ConsoleStream &s){
 uint8_t p[16]={'E','X',1,CONSOLE_PREPARE},r[16];p[4]=1;p[12]=1;console_seal(p);
 assert(s.session.request(p,0,17,r));p[3]=CONSOLE_COMMIT;p[8]=17;console_seal(p);assert(s.session.request(p,1,0,r));
 for(unsigned b:std::initializer_list<unsigned>{H::released,H::validHigh,0,H::validHigh,H::uartUp})s.parallel.handover.step(b);
 assert(s.parallel.handover.phase()==H::uart);s.parallel.session.phase=PARALLEL_SESSION_ACTIVE;
 const uint8_t identity[]={1,2,3,4,0,0};memcpy(s.parallel.session.bytes,identity,6);assert(s.parallelVdu.begin());
 uint8_t request[16]={'E','X',PARALLEL_WIRE_VERSION,PARALLEL_STREAM_START};memcpy(request+4,identity,6);parallel_control_pad(request);
 assert(s.parallelVdu.request(request,r,true));clockNow=sleeps=uartReads=0;
}
static void offer(ConsoleStream &s,const std::vector<uint8_t>&data){
 auto &c=s.parallel;unsigned sequence=unsigned(c.session.bytes[4]|unsigned(c.session.bytes[5])<<8)+1;
 uint8_t p[16]={'E','X',PARALLEL_WIRE_VERSION,PARALLEL_OFFER},r[16];memcpy(p+4,c.session.bytes,4);
 p[8]=uint8_t(sequence);p[9]=uint8_t(sequence>>8);p[10]=uint8_t(data.size());p[11]=uint8_t(data.size()>>8);parallel_control_pad(p);
 assert(s.parallelVdu.canOffer(p)&&c.request(p,0,0,r)&&s.parallelVdu.acceptedOffer());
 uint8_t *buffer{};size_t capacity{};assert(c.payloadBuffer(buffer,capacity)&&capacity>=data.size());memcpy(buffer,data.data(),data.size());
}
static void physicalReturn(ConsoleStream&s){
 for(unsigned b:std::initializer_list<unsigned>{H::quiet,H::released,0,H::validHigh,H::validHigh|H::clockHigh,H::validHigh|H::clockHigh|H::armed,H::done,H::validHigh,0,H::validHigh,H::uartUp})s.parallel.handover.step(b);
 assert(s.parallel.payloadReturned(1));
}
static void feed(ConsoleStream&s,const std::vector<uint8_t>&data){offer(s,data);physicalReturn(s);assert(s.parallelVdu.retire());}
static void queuedAdmission(bool availableFirst){
 ConsoleStream s;start(s);std::vector<uint8_t> original(256);for(unsigned i=0;i<original.size();++i)original[i]=uint8_t(i);feed(s,original);
 unsigned consumed=0,calls=0,phase=0;bool offered=false,sawUnretired=false;
 s.progress=[&](){
  ++calls;auto available=s.parallelVdu.available();uint8_t scratch[4]{};
  assert(s.available()==0&&s.read()==-1&&s.peek()==-1&&s.readBytes(scratch,4)==0);
  assert(s.parallelVdu.available()==available); // callback cannot recursively parse
  if(!offered&&consumed>=17){assert(consumed<=17+s.progressQuantum);assert(available>0);offer(s,{0xe7});offered=true;phase=1;}
  else if(phase==1){physicalReturn(s);sawUnretired=true;phase=2;assert(!s.parallel.pending()&&!s.parallel.uartTransitionAllowed());}
  else if(phase==2){assert(s.parallelVdu.retire());phase=3;}
 };
 std::vector<uint8_t> got;unsigned blocked=0;
 while(got.size()<257){
  auto before=s.parallelVdu.available();
  const bool readable=!availableFirst || s.available()>0;
  int b=readable?s.read():-1;
  if(availableFirst&&readable)assert(b>=0); // stock top-level parser casts directly to uint8_t
  if(b<0){++blocked;assert(s.parallelVdu.available()==before);continue;}
  got.push_back(uint8_t(b));++consumed;
 }
 original.push_back(0xe7);assert(got==original&&offered&&sawUnretired&&blocked==2&&phase==3&&!uartReads&&!sleeps);
 assert(calls>=4&&s.progressRemaining<=s.progressQuantum);
}
static void bulkAndPeek(){
 ConsoleStream s;start(s);std::vector<uint8_t> data(4096);for(unsigned i=0;i<data.size();++i)data[i]=uint8_t(i*73);
 feed(s,data);feed(s,data);unsigned calls=0;s.progress=[&](){++calls;};
 s.setup[2]=11;s.setup[3]=12;s.pos=2;s.cached=13;
 assert(s.peek()==11&&s.peek()==11);uint8_t prefix[3];assert(s.readBytes(prefix,3)==3&&prefix[0]==11&&prefix[1]==12&&prefix[2]==13);
 assert(s.parallelVdu.available()==8192);
 std::vector<uint8_t> got(8192);assert(s.readBytes(got.data(),got.size())==got.size());
 assert(calls==128);assert(std::equal(data.begin(),data.end(),got.begin())&&std::equal(data.begin(),data.end(),got.begin()+4096));
 assert(!uartReads&&!sleeps);auto before=calls;assert(!s.readBytes(static_cast<uint8_t*>(nullptr),1)&&!s.readBytes(got.data(),0)&&calls==before);
}
static void pendingAndFailure(){
 ConsoleStream s;start(s);feed(s,{1,2});offer(s,{3});unsigned calls=0;
 s.progress=[&](){if(++calls==4){physicalReturn(s);assert(s.parallelVdu.retire());}};
 uint8_t got[3]{};assert(s.readBytes(got,3)==3&&calls==4&&got[0]==1&&got[1]==2&&got[2]==3&&!sleeps);
 ConsoleStream reset;start(reset);feed(reset,{5});
 reset.progress=[&](){reset.transportLost();assert(reset.progressing&&reset.read()==-1&&reset.peek()==-1);};
 assert(reset.read()==-1&&!reset.parallelVdu.active()&&!reset.parallelVdu.available()&&!reset.progressing&&!reset.progressRemaining);
 ConsoleStream fault;start(fault);feed(fault,{9});fault.progress=[&](){fault.fail("peer fault");};
 assert(fault.read()==-1&&fault.parallelVdu.available()==1);assert(fault.readBytes(got,3)==0);
 ConsoleStream timeout;start(timeout);timeout.progress=[](){};assert(timeout.readBytes(got,1)==0&&clockNow>=200&&sleeps>0);
}
static void uartUnchanged(){
 ConsoleStream s;unsigned calls=0;s.progress=[&](){++calls;};s.setup[0]=9;s.pos=0;
 assert(s.read()==9&&s.peek()==0&&calls==0);s.transportLost();assert(s.read()==-1&&calls==0);
}
int main(){queuedAdmission(false);queuedAdmission(true);bulkAndPeek();pendingAndFailure();uartUnchanged();puts("PASS: actual buffered admission, native/staging gates, byte order, bulk/cache/peek, recursion, reset, fault, timeout and UART separation");}
