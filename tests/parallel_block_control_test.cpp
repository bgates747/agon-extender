// Actual EMOS foreground/ISR + P4 control owner. Only UART and physical
// adapter completions are scripted. No native GPIO/timing/throughput claim.
#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
extern "C" {
#include "emos_console.h"
#include "emos_parallel_handover.h"
#include "emos_keyboard.h"
volatile BYTE emosVduBackend,emos_key_faulted;
BYTE vdp_protocol_data[16];
}
#include "extender/transport/parallel_control.hpp"
#include "extender/transport/console_session.hpp"
#include "extender/input/usb_key_queue.hpp"
using P=agon::extender::transport::P4ParallelHandover;
using Owner=agon::extender::transport::ParallelControl;
using Packet=std::array<BYTE,16>;
static Owner peer;
static t_emosParallelHandover e;
static t_parallelSession session;
static std::array<BYTE,4096> storage;
static BYTE irq=1,reserved=1,tick;
static uint32_t now=100;
static unsigned sends,clock_reads,cases;
static bool missing,frozen,fail_send,duplicate;
static int corrupt=-1;
static unsigned bit;
static bool reseal;
extern "C" BYTE emos_keyboard_parallel_reserved(void){return irq && reserved;}
extern "C" BYTE emos_keyboard_clock(void){++clock_reads;if(!frozen)tick+=2;return tick;}
extern "C" BYTE emos_keyboard_lock(void){BYTE old=irq;irq=0;return old;}
extern "C" void emos_keyboard_unlock(BYTE enabled){irq=enabled;}
extern "C" BYTE emos_keyboard_send(const BYTE *,UINT16){assert(false);return EMOS_KEY_BUSY;}
extern "C" void emos_vdp_effect(BYTE){assert(false);}
static void receive(Packet p,unsigned length=16){
  BYTE old=emos_keyboard_lock();emos_console_packet(CONSOLE_REPLY,p.data(),length);emos_keyboard_unlock(old);
}
extern "C" BYTE emos_keyboard_parallel_send(const BYTE *p,UINT16 n){
  assert(irq && reserved);++sends;
  if(fail_send)return EMOS_KEY_BUSY;
  if(n==3){const BYTE prefix[]={23,0,CONSOLE_OPCODE};assert(!std::memcmp(p,prefix,3));return EMOS_KEY_OK;}
  assert(n==16);Packet reply{};
  if(!peer.request(p,now,0x12345678,reply.data()))return EMOS_KEY_OK;
  if(missing)return EMOS_KEY_OK;
  auto original=reply;
  if(corrupt>=0){reply[corrupt]^=1u<<bit;if(reseal)parallel_session_seal(reply.data());}
  receive(reply,15);receive(reply);
  if(duplicate){original[10]^=0x20;parallel_session_seal(original.data());receive(original);}
  return EMOS_KEY_OK;
}
static void recover(P &p){
  for(auto flags:std::array<BYTE,5>{P::released|P::validHigh,P::validHigh,0,P::validHigh,P::validHigh|P::uartUp})p.step(flags);
  assert(p.phase()==P::uart);
}
static void reset(){
  peer=Owner{};recover(peer.handover);peer.provide(storage.data(),storage.size());
  e={EPH_UART,1,0,1};session={};irq=reserved=1;emos_key_faulted=0;tick=0;now=100;
  sends=clock_reads=0;missing=frozen=fail_send=duplicate=reseal=false;corrupt=-1;
  BYTE txn[4]={1,2,3,4};assert(emos_parallel_session_negotiate(&e,&session,txn));sends=0;
}
static Packet offer(unsigned length=256,unsigned direction=0){
  Packet p{};p[0]='E';p[1]='X';p[2]=2;p[3]=PARALLEL_OFFER;
  std::memcpy(p.data()+4,session.bytes,4);
  unsigned seq=(session.bytes[4]|(unsigned(session.bytes[5])<<8))+1;
  p[8]=BYTE(seq);p[9]=BYTE(seq>>8);p[10]=BYTE(length);p[11]=BYTE(length>>8);p[12]=BYTE(direction);
  parallel_session_seal(p.data());return p;
}
static bool take(){BYTE *buffer=nullptr,direction=99;size_t length=0;return peer.takeCompleted(buffer,length,direction);}
static void runPhysical(){
  // Simulated COMPLETED operations drive the actual paired sequencers. This
  // intentionally does not claim UART drain or peripheral completion happened.
  BYTE ed=0,pd=0,ea=0,pa=0;bool ended=false;
  for(unsigned loops=0;loops<100;++loops){
    BYTE action=emos_parallel_handover_step(&e,BYTE(ed|(peer.handover.readyN()?EPH_READY_HIGH:0)));
    if(action!=EPH_WAIT && action!=ea){ed=0;ea=action;}
    if(action==EPH_FENCE)ed=EPH_QUIET;
    else if(action==EPH_RELEASE)ed=EPH_RELEASED;
    else if(action==EPH_ARM)ed=EPH_ARMED;
    else if(action==EPH_RESTORE)ed=EPH_UART_UP;
    BYTE f=(e.validN?P::validHigh:0)|(e.clockHigh?P::clockHigh:0)|pd;
    auto a=peer.handover.step(f);
    if(a!=P::wait && a!=pa){pd=0;pa=a;}
    if(a==P::fence)pd=P::quiet;
    else if(a==P::release)pd=P::released;
    else if(a==P::arm)pd=P::armed;
    else if(a==P::restore)pd=P::uartUp;
    if(e.phase==EPH_BLOCK && peer.handover.phase()==P::block){ended=true;pd=P::done;}
    if(ended && peer.handover.readyN() && e.phase==EPH_BLOCK)ed=EPH_DONE;
    peer.expire(++now);assert(peer.pending());assert(!take());
    if(e.phase==EPH_UART && peer.handover.phase()==P::uart)return;
  }
  assert(false);
}
static void start(Packet const &p){
  assert(emos_parallel_block_offer(&e,&session,3,p.data()));
  assert(peer.pending() && e.phase==EPH_DRAIN && peer.handover.phase()==P::drain);
  assert(!std::memcmp(peer.descriptor(),p.data(),16));assert(!take());
}
static void returned(BYTE status=0){runPhysical();assert(peer.payloadReturned(status,now));assert(!take());}
int main(){
  // Repeated blocks, both directions, smallest/packet/boundary lengths. Preserve
  // actual queued key press/release order through all phase/result waits.
  for(unsigned direction:{0u,1u})for(unsigned length:{1u,2u,255u,256u,4095u,4096u}){
    reset();agon::extender::input::UsbKeyQueue keys;
    for(unsigned down:{1u,0u}){agon::extender::input::ProcessedKey key{};key.virtual_key=42;key.down=down;assert(keys.push(key));}
    for(unsigned repeat=0;repeat<3;++repeat){
      auto p=offer(length,direction);start(p);auto same=p;Packet ack{};
      assert(!peer.request(same.data(),now,7,ack.data()));assert(!peer.provide(storage.data(),storage.size()));
      assert(!emos_parallel_block_complete(&e,&session,p.data(),0));assert(!peer.payloadReturned(0,now));
      returned();assert(!keys.empty());duplicate=true;
      assert(emos_parallel_block_complete(&e,&session,p.data(),0));assert(irq==1);
      assert(!peer.request(p.data(),now,7,ack.data())); // receipt still owns buffer
      BYTE *data=nullptr,dir=99;size_t n=0;
      assert(peer.takeCompleted(data,n,dir));assert(data==storage.data() && n==length && dir==direction);
      assert(!take());assert(session.phase==3 && peer.session.phase==3);++cases;
    }
    for(unsigned down:{1u,0u}){agon::extender::input::ProcessedKey key{};assert(keys.pop(key));assert(key.virtual_key==42 && key.down==bool(down));}
    assert(keys.empty());
  }
  // Every reply bit, including recomputed-CRC semantic alterations. Payload
  // failure status=1 is legitimate but still must prevent success publication.
  for(bool completion:{false,true})for(int field=0;field<16;++field)for(unsigned b=0;b<8;++b)for(bool crc:{false,true}){
    reset();auto p=offer();if(completion){start(p);returned();}
    corrupt=field;bit=b;reseal=crc;
    bool accepted=completion ? emos_parallel_block_complete(&e,&session,p.data(),0)
                             : emos_parallel_block_offer(&e,&session,3,p.data());
    // Recomputing the checksum cancels an alteration of the CRC bytes itself.
    assert(accepted==(crc && field>=14));
    if(!accepted)assert(session.phase==0 && e.phase==EPH_RETURN_RELEASE);
    ++cases;
  }
  // Wrong incoming completion fields cannot mutate the P4 pending descriptor.
  for(int field=0;field<14;++field)for(unsigned b=0;b<8;++b){
    reset();auto p=offer();start(p);returned();Packet request=p,reply{};
    request[3]=PARALLEL_COMPLETE;request[field]^=1u<<b;parallel_session_seal(request.data());
    bool accepted=peer.request(request.data(),now,7,reply.data());
    assert(accepted==(field==13 && b==0));
    if(!accepted){assert(peer.pending() && !std::memcmp(peer.descriptor(),p.data(),16));assert(!take());}
    else assert(!take() && peer.session.phase==0);
    ++cases;
  }
  for(unsigned local:{0u,1u})for(unsigned remote:{0u,1u}){
    reset();auto p=offer();start(p);returned(BYTE(remote));
    bool ok=emos_parallel_block_complete(&e,&session,p.data(),BYTE(local));
    assert(ok==(!local && !remote));assert(take()==ok);
    if(!ok)assert(session.phase==0 && peer.session.phase==0 && peer.handover.phase()==P::uart);
    ++cases;
  }
  reset();auto failedOffer=offer();start(failedOffer);returned();e.failed=1;
  assert(!emos_parallel_block_complete(&e,&session,failedOffer.data(),0));
  assert(!take() && session.phase==0 && peer.session.phase==0);++cases;
  for(bool completion:{false,true})for(unsigned failure=0;failure<4;++failure){
    reset();auto p=offer();if(completion){start(p);returned();}
    if(failure==0)missing=true;
    if(failure==1)missing=frozen=true;
    if(failure==2)fail_send=true;
    if(failure==3)reserved=0;
    assert(!(completion ? emos_parallel_block_complete(&e,&session,p.data(),0)
                        : emos_parallel_block_offer(&e,&session,3,p.data())));
    assert(clock_reads<262150);assert(irq==1);
    if(failure!=3)assert(session.phase==0);
    ++cases;
  }
  for(uint32_t at:{100u,0xfffffff0u})for(bool afterReturn:{false,true}){
    reset();now=at;auto p=offer();start(p);if(afterReturn)returned();
    peer.expire(now+1999);assert(peer.pending());peer.expire(now+2000);
    assert(!peer.pending() && !take() && peer.session.phase==0 && peer.handover.phase()==P::recoveryRelease);++cases;
  }
  // Deadline advances only on an observed, timely phase change; late progress
  // cannot revive an expired block. Cancellation revokes even an unread receipt.
  reset();auto p=offer();start(p);peer.handover.step(P::quiet);
  peer.expire(now+1999);peer.expire(now+3998);assert(peer.pending());
  peer.expire(now+3999);assert(!peer.pending());++cases;
  reset();p=offer();start(p);peer.handover.step(P::quiet);peer.expire(now+2000);assert(!peer.pending());++cases;
  reset();p=offer();start(p);returned();assert(emos_parallel_block_complete(&e,&session,p.data(),0));peer.cancel();assert(!take());++cases;
  reset();p=offer();start(p);returned();peer.handover.cancel();peer.expire(now);
  assert(!peer.pending() && peer.session.phase==0 && !take());
  assert(!peer.provide(storage.data(),storage.size()));++cases;
  reset();p=offer();start(p);returned();assert(emos_parallel_block_complete(&e,&session,p.data(),0));
  peer.handover.cancel();assert(!take());++cases;
  // No buffer/capacity or no reservation/mode/active session: refuse admission.
  for(unsigned failure=0;failure<7;++failure){
    reset();p=offer();if(failure==0)peer.provide(nullptr,0);if(failure==1)peer.provide(storage.data(),255);
    if(failure==2)reserved=0;
    if(failure==3)session.phase=0;
    if(failure==4)emos_console_owned=1;
    if(failure==5){p[10]=p[11]=0;parallel_session_seal(p.data());}
    assert(!emos_parallel_block_offer(&e,&session,failure==6?1:3,p.data()));assert(!peer.pending());emos_console_owned=0;++cases;
  }
  std::cout<<"PASS "<<cases<<" paired block-control cases; no GPIO timing claim\n";
}
