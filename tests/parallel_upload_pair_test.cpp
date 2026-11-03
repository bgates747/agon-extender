// Appended to the actual upload SDK model by the Python runner. Both real
// endpoint coordinators advance; only parking, byte I/O and scheduler are fake.
#include "extender/transport/p4_upload_coordinator.hpp"
#include "extender/storage/sd_service.hpp"
#include <memory>
extern "C" {
#include "eZ80.h"
#include "emos_parallel_upload.h"
#include "emos_parallel_handover.h"
#include "emos_keyboard.h"
#include "uart.h"
volatile BYTE hostPcDr,hostPcDdr,hostPcAlt1,hostPcAlt2;
volatile BYTE hostPdDr,hostPdDdr,hostPdAlt1,hostPdAlt2;
volatile BYTE hostUart1Ier,hostUart1Mctl;
volatile BYTE emos_key_faulted,emos_key_source,uart1_keyboard_owned;
}
using C=P4UploadCoordinator;using CR=C::Result;using M=P4UploadMailbox;
static P4ParallelHandover peer;
static t_emosParallelHandover local;
static std::unique_ptr<C> owner;
static agon::extender::storage::SdService queue;
static bool irq=true,reserved,bootBlock;
static unsigned now,parks,unparks,releases,rawCalls,drainDelay;
static void synchronize(){
 auto newValid=bool(hostPdDr&0x80);signal(newValid);
 clockLevel=bool(hostPdDr&0x20);
 if(owner){
  const bool drain=drainDelay&&!valid&&!clockLevel;
  auto result=owner->poll(++now,true,!drain);
  if(drain){
   --drainDelay;assert(result==CR::drain&&owner->ownsPhysical()&&!parks&&!outputs);
  }
 }
 hostPdDr=BYTE((hostPdDr&~0x10)|(ready?0x10:0));
}
namespace agon::extender::transport {
P4UartParking::Result P4UartParking::park(bool boundary,bool quiet) noexcept {
 assert(boundary&&quiet&&!valid&&!clockLevel);parked=true;++parks;return Result::ready;
}
P4UartParking::Result P4UartParking::restore(bool dataReleased,bool peerReleased) noexcept {
 assert(dataReleased&&peerReleased&&!outputs&&!enabled&&!clockLevel&&valid);
 return Result::ready;
}
}
extern "C" t_emosParallelHandover *emos_parallel_boot_handover(){return &local;}
extern "C" BYTE emos_parallel_boot_block_begin(){assert(!bootBlock&&local.phase==EPH_DRAIN);bootBlock=true;return 1;}
extern "C" void emos_parallel_boot_block_end(BYTE okay){
 if(okay){assert(local.phase==EPH_UART&&!local.failed);bootBlock=false;}
 else {local.failed=1;local.phase=EPH_RETURN_RELEASE;}
}
extern "C" BYTE emos_keyboard_lock(){auto old=irq;irq=false;return old;}
extern "C" void emos_keyboard_unlock(BYTE old){irq=old;}
extern "C" BYTE emos_keyboard_parallel_reserve(){
 if(reserved)return UART_POLL_UNAVAILABLE;
 reserved=true;return UART_POLL_READY;
}
extern "C" BYTE emos_keyboard_parallel_park(){
 assert(reserved);hostPcDdr=255;hostPcAlt1=hostPcAlt2=0;
 hostUart1Ier=0;hostUart1Mctl=UART_MCTL_LOOP;return UART_POLL_READY;
}
extern "C" BYTE emos_keyboard_parallel_unpark(){
 assert(reserved&&local.phase==EPH_RETURN_UART);++unparks;
 hostUart1Ier=5;hostUart1Mctl=0;return UART_POLL_READY;
}
extern "C" BYTE emos_keyboard_parallel_release(){
 assert(reserved&&hostUart1Mctl==0);reserved=false;++releases;return UART_POLL_READY;
}
extern "C" BYTE emos_keyboard_clock(){return BYTE(now);}
extern "C" BYTE emos_keyboard_deadline_step(t_emosDeadline *d){
 synchronize();return ++d->elapsed<200;
}
extern "C" void emos_parallel_io_write_control(UINT24 bits){
 hostPdDr=BYTE((hostPdDr&0x4f)|bits|(ready?0x10:0));
 // Count VALID transitions at the register write, without a task/ISR latency
 // assumption. GPIO ready remains owned by the P4 native leaf/coordinator.
 signal(bool(bits&0x80));clockLevel=bool(bits&0x20);
}
extern "C" BYTE emos_parallel_upload_bytes(BYTE *buffer,UINT24 n){
 assert(reserved&&bootBlock&&hostUart1Mctl==UART_MCTL_LOOP);
 assert(n&&n<=512&&ready==0&&clockLevel==1&&!valid&&irq);
 for(unsigned i=0;i<n;++i)buffer[i]=dma[(clocked+i)%cycle];
 clocks(n);++rawCalls;return 0;
}
static bool admission(std::uint32_t time,std::uint32_t id,std::uint32_t length){
 return queue.admitBulk(time,id,length);
}
static void boot(){
 peer=P4ParallelHandover{};
 using H=P4ParallelHandover;
 peer.step(H::released);peer.step(H::validHigh);peer.step(0);
 peer.step(H::validHigh);peer.step(H::uartUp);assert(peer.phase()==H::uart);
 // Real boot recovery leaves failed=1 as the OLD payload outcome. Admission
 // must use the recovered UART phase, then clear history through real begin().
 local={EPH_UART,1,0,1};hostPcDdr=255;hostPcAlt1=hostPcAlt2=0;
 hostPdDdr=0x10;hostPdAlt1=hostPdAlt2=0;hostPdDr=0x90;
 hostUart1Ier=5;hostUart1Mctl=0;irq=true;reserved=bootBlock=false;
 now=parks=unparks=releases=rawCalls=0;drainDelay=1;valid=1;clockLevel=0;
 queue=agon::extender::storage::SdService{};
 owner=std::make_unique<C>(peer,pins,14,16,15,18,17,20,19,0,admission);
}
int main(){unsigned cases=0;
 for(unsigned n:{1U,63U,64U,65U,511U,512U,513U,4096U,65535U,65536U,65537U,1100000U}){
  reset();boot();logical=n;auto file=spool(n);
  assert(uploadMailbox.load(file,n,73));std::fclose(file);
  synchronize();assert(uploadMailbox.status()==M::prepared&&!outputs);
  assert(uploadMailbox.offer());
  std::uint8_t presence[20],request[28],wire[240],reply[28];unsigned out=0;
  sd_header_mode(presence,SD_PRESENCE,101,0,0,0,0,1);sd_seal(presence);
  assert(queue.receive(presence,20,now));auto token=queue.claim(now);assert(token);
  sd_header_mode(request,SD_REQUEST,111,1,SD_PARALLEL_WRITE,0,8,1);
  sd_put32(request+20,73);sd_put32(request+24,n);sd_seal(request);
  assert(queue.postOwned(token,request,28,wire,out,now)==202);
  assert(queue.take(wire,now)==28);
  assert(emos_parallel_upload_begin(n)==0&&bootBlock&&reserved);
  assert(emos_parallel_upload_begin(n)!=0); // no nested admission
  assert(uploadMailbox.status()==M::active&&parks==1&&unparks==0&&ready==0);
  std::uint8_t slice[514];std::memset(slice,0xa5,sizeof(slice));
  assert(emos_parallel_upload_read(slice,0)!=0);
  assert(emos_parallel_upload_read(slice,513)!=0);
  irq=false;assert(emos_parallel_upload_read(slice,1)!=0&&!irq);irq=true;
  auto old=hostUart1Mctl;hostUart1Mctl=0;
  assert(emos_parallel_upload_read(slice,1)!=0);hostUart1Mctl=old;
  assert(!rawCalls&&!clocked); // every refusal left the payload untouched
  unsigned received=0;
  while(received<n){
   auto count=std::min(512U,n-received);
   assert(emos_parallel_upload_read(slice+1,count)==0);
   assert(slice[0]==0xa5&&slice[count+1]==0xa5);
   for(unsigned i=0;i<count;++i)assert(slice[i+1]==pattern(received+i));
   received+=count;std::memset(slice,0xa5,sizeof(slice));
   auto clocksBefore=clocked;
   now+=17;synchronize(); // SD-write pause, no UART presence for long files
   assert(uploadMailbox.status()==M::active&&clocked==clocksBefore&&enabled);
   assert(queue.postOwned(token,request,28,wire,out,now)==202);
   assert(queue.take(wire,now)==0); // whole-file operation never retransmitted
  }
  assert(emos_parallel_upload_end(0)==0);
  assert(!bootBlock&&!reserved&&unparks==1&&releases==1);
  assert(uploadMailbox.status()==M::returned&&!outputs&&!enabled);
  assert(uploadMailbox.outcome.load()==unsigned(R::complete));
  assert(peer.phase()==P4ParallelHandover::uart&&local.phase==EPH_UART);
  assert(rawCalls==(n+511)/512&&clocked==n&&parks==1);
  sd_header_mode(reply,SD_RESPONSE,111,1,SD_PARALLEL_WRITE,0,8,1);
  sd_put32(reply+20,73);sd_put32(reply+24,n);sd_seal(reply);
  assert(queue.receive(reply,28,now)&&queue.postOwned(token,request,28,wire,out,now)==200);
  uploadMailbox.retire();synchronize();assert(uploadMailbox.status()==M::free&&!allocation);
  owner.reset();++cases;
 }
 // A historical failed bit at recovered UART is permitted above; an actual
 // unrecovered phase still refuses NEW admission and never touches data pads.
 reset();boot();local.phase=EPH_RETURN_RELEASE;
 assert(emos_parallel_upload_begin(1)!=0&&!reserved&&!bootBlock);++cases;
 logical=65;auto blocked=spool(logical);peer.cancel();
 assert(uploadMailbox.load(blocked,logical,73));std::fclose(blocked);
 synchronize();assert(uploadMailbox.status()==M::queued&&!unitLive&&!outputs);
 uploadMailbox.retire();synchronize();assert(uploadMailbox.status()==M::free);
 owner.reset();++cases;
 // A utility SD-write error ends the single admission early. Both processors
 // perform reciprocal UART return, but P4 preserves shortPayload as failure.
 reset();boot();logical=65537;auto partial=spool(logical);
 assert(uploadMailbox.load(partial,logical,73));std::fclose(partial);synchronize();
 assert(uploadMailbox.offer());std::uint8_t p[28],o[240];unsigned out=0;
 sd_header_mode(p,SD_PRESENCE,101,0,0,0,0,1);sd_seal(p);assert(queue.receive(p,20,now));
 auto token=queue.claim(now);assert(token);
 sd_header_mode(p,SD_REQUEST,111,1,SD_PARALLEL_WRITE,0,8,1);
 sd_put32(p+20,73);sd_put32(p+24,logical);sd_seal(p);
 assert(queue.postOwned(token,p,28,o,out,now)==202&&queue.take(o,now)==28);
 assert(emos_parallel_upload_begin(logical)==0);std::uint8_t b[512];
 assert(emos_parallel_upload_read(b,512)==0);
 assert(emos_parallel_upload_end(0)!=0); // incomplete file cannot claim success
 assert(emos_parallel_upload_end(1)==0);
 assert(uploadMailbox.status()==M::returned&&uploadMailbox.outcome.load()==unsigned(R::shortPayload));
 assert(!bootBlock&&!reserved&&unparks==1&&peer.phase()==P4ParallelHandover::uart);
 uploadMailbox.retire();synchronize();assert(uploadMailbox.status()==M::free&&!allocation);
 owner.reset();++cases;
 reset();std::cout<<"PASS "<<cases<<" paired upload coordinators; one admission/park, retained slices, exact bytes and clean UART return\n";
}
