// Prepended shared SDK/parking model. No endpoint handover state is forced
// live: actual startup/foreground C and P4 coordinator advance the handshake.
extern "C" {
#include "eZ80.h"
#include "emos_console.h"
#include "emos_console_wire.h"
#include "emos_parallel_handover.h"
#include "emos_keyboard.h"
#include "emos_parallel.h"
#include "uart.h"
volatile BYTE hostPcDr,hostPcDdr,hostPcAlt1,hostPcAlt2;
volatile BYTE hostPdDr,hostPdDdr,hostPdAlt1,hostPdAlt2;
volatile BYTE hostUart1Ier,hostUart1Mctl;
volatile BYTE emosVduBackend,emos_key_faulted,emos_key_source,uart1_keyboard_owned;
BYTE vdp_protocol_data[16];
}
#include <memory>
static agon::extender::transport::ParallelControl peer;
static std::unique_ptr<C> owner;
static t_parallelSession session;
static std::vector<BYTE> peerData,localData;
static BYTE irq=1,reserved=1,tick;
static unsigned now,cases,parks,unparks,releases,closeCalls,faults,clocks;
static int faultPhase=-1,stallPhase=-1;
static bool frozen,missing,corrupt,unparkFailure,parkFailure,nativeFailure,releaseFailure,nested;
static unsigned parkDelay;
static CR result;
static t_emosParallelHandover *h(){return emos_parallel_boot_handover();}
static void synchronize(){
 valid=bool(hostPdDr&0x80);clockLevel=bool(hostPdDr&0x20);
 if(owner)result=owner->poll(++now,true,true);
 else {
  BYTE done=(valid?H::validHigh:0)|(clockLevel?H::clockHigh:0);
  if(peer.handover.phase()==H::recoveryRelease)done|=H::released;
  if(peer.handover.phase()==H::recoveryUart)done|=H::uartUp;
  peer.handover.step(done);ready=peer.handover.readyN();
 }
 hostPdDr=(hostPdDr&~0x10)|(ready?0x10:0);
}
extern "C" BYTE emos_keyboard_clock(){++clocks;if(!frozen)tick+=2;return tick;}
extern "C" BYTE emos_keyboard_deadline_step(t_emosDeadline *d){
 // Advance the modeled peer once per foreground poll. The real linked eZ80
 // tests separately execute the production timer/fuse with register timing.
 if(h()->phase!=stallPhase)synchronize();
 if(h()->phase==stallPhase){
  bool high=stallPhase==EPH_ENTRY_ACK||stallPhase==EPH_ENTRY_ARM||stallPhase==EPH_RETURN_REQUEST;
  hostPdDr=(hostPdDr&~0x10)|(high?0x10:0);
 }
 if(h()->phase==faultPhase)emos_key_faulted=1;
 emos_parallel_boot_tick();
 if(owner&&h()->phase>=EPH_DRAIN)assert(!faults&&!closeCalls);
 BYTE t=emos_keyboard_clock(),delta=BYTE(t-d->last);
 if(delta){d->elapsed+=delta;d->last=t;d->budget=262144;}
 else if(!--d->budget)return 0;
 return d->elapsed<600;
}
extern "C" BYTE emos_keyboard_lock(){BYTE old=irq;irq=0;return old;}
extern "C" void emos_keyboard_unlock(BYTE b){irq=b;}
extern "C" void emos_parallel_io_write_control(UINT24 b){hostPdDr=(hostPdDr&0x5f)|(b&0xa0);}
extern "C" void emos_parallel_io_configure(UINT24 d,UINT24 a,UINT24 b){
 hostPdDdr=(hostPdDdr&0x4f)|(d&0xb0);hostPdAlt1=(hostPdAlt1&0x4f)|(a&0xb0);hostPdAlt2=(hostPdAlt2&0x4f)|(b&0xb0);
}
extern "C" BYTE emos_keyboard_transport_claim(){assert(emos_parallel_boot_uart_allowed());uart1_keyboard_owned=1;return 0;}
extern "C" void emos_keyboard_transport_release(){uart1_keyboard_owned=0;}
extern "C" void uart1_keyboard_close(){++closeCalls;uart1_keyboard_owned=0;}
extern "C" void emos_keyboard_fault(){++faults;emos_key_faulted=1;}
extern "C" BYTE emos_keyboard_parallel_reserved(){return irq&&reserved==1&&uart1_keyboard_owned==1&&!emos_key_faulted;}
extern "C" BYTE emos_keyboard_parallel_park(){
 ++parks;assert(irq&&reserved==1&&h()->phase==EPH_DRAIN);
 if(parkDelay){--parkDelay;return UART_POLL_EMPTY;}
 if(parkFailure)return UART_POLL_ERROR;
 uart1_keyboard_owned=2;hostUart1Ier=0;hostUart1Mctl=UART_MCTL_LOOP;
 hostPcDdr=255;hostPcAlt1=hostPcAlt2=0;return UART_POLL_READY;
}
extern "C" BYTE emos_keyboard_parallel_unpark(){
 ++unparks;assert(irq&&reserved==1&&h()->phase==EPH_RETURN_UART&&emos_parallel_boot_uart_allowed());
 assert(hostPcDdr==255&&hostPcAlt1==0&&hostPcAlt2==0&&!outputs&&!allocation);
 if(unparkFailure)return UART_POLL_ERROR;
 uart1_keyboard_owned=1;return UART_POLL_READY;
}
extern "C" BYTE emos_keyboard_parallel_release(){
 ++releases;assert(irq&&reserved==1&&uart1_keyboard_owned==1&&h()->phase==EPH_UART);
 if(releaseFailure)return UART_POLL_ERROR;
 reserved=0;return UART_POLL_READY;
}
extern "C" BYTE emos_keyboard_send(const BYTE*,UINT16){assert(false);return 1;}
extern "C" void emos_vdp_effect(BYTE){assert(false);}
extern "C" BYTE emos_keyboard_parallel_send(const BYTE*p,UINT16 n){
 assert(irq&&reserved==1&&uart1_keyboard_owned==1);
 if(n==3)return 0;
 assert(n==16);BYTE reply[16];
 assert(peer.request(p,now,0x12345678,reply));
 if(nested&&p[3]==PARALLEL_COMPLETE){
  assert(!emos_parallel_boot_block_begin());
  assert(!emos_parallel_native_coordinate(&session,p,localData.data(),localData.size()));
 }
 if(missing)return 0;
 if(corrupt){reply[10]^=1;parallel_session_seal(reply);}
 BYTE old=emos_keyboard_lock();emos_console_packet(CONSOLE_REPLY,reply,16);emos_keyboard_unlock(old);return 0;
}
extern "C" BYTE emos_parallel_native_bytes(BYTE*b,UINT24 n,BYTE reverse){
 assert(irq&&reserved==1&&h()->phase==EPH_BLOCK&&peer.handover.phase()==H::block);
 assert(n==peerData.size()&&watch&&allocation);
 if(nativeFailure)return EMOS_PARALLEL_NOT_OWNED;
 signal(false);hostPdDr&=~0x80;
 if(reverse)std::memcpy(b,dma,n);else std::memcpy(dma,b,n);
 completed(reverse,n);signal(true);hostPdDr|=0x80;
 assert(owner->poll(++now,true,true)==CR::exclusive&&!allocation&&!outputs);
 return EMOS_PARALLEL_OK;
}
static void setup(unsigned n,bool reverse){
 owner.reset();reset();peer={};session={};irq=reserved=1;tick=250;now=0;clocks=0;
 parks=unparks=releases=closeCalls=faults=0;faultPhase=stallPhase=-1;
 frozen=missing=corrupt=unparkFailure=parkFailure=nativeFailure=releaseFailure=nested=false;parkDelay=0;
 uartIdle=true;uartRestored=false;ring=fifo=restores=0;emos_key_faulted=0;uart1_keyboard_owned=0;
 hostPcDdr=255;hostPcAlt1=hostPcAlt2=0;hostPdDr=0x4b;hostPdDdr=hostPdAlt1=hostPdAlt2=0;
 emos_parallel_boot_start();emos_parallel_boot_connect();
 assert(h()->phase==EPH_UART&&peer.handover.phase()==H::uart&&emos_parallel_boot_uart_allowed());
 uart1_keyboard_owned=1;peerData.assign(n,0xa5);localData.assign(n,0xa5);
 for(unsigned i=0;i<n;++i)(reverse?peerData:localData)[i]=BYTE(73*i+17);
 assert(peer.provide(peerData.data(),peerData.size()));
 owner=std::make_unique<C>(peer,pins,14,16,15,18,17,20,19,0);
 BYTE txn[4]={1,2,3,4};assert(emos_parallel_session_negotiate(h(),&session,txn));
}
static std::array<BYTE,16> admit(bool reverse){
 std::array<BYTE,16>d{'E','X',2,PARALLEL_OFFER};
 std::memcpy(d.data()+4,session.bytes,4);d[8]=BYTE(session.bytes[4]+1);
 d[10]=BYTE(localData.size());d[11]=BYTE(localData.size()>>8);d[12]=reverse;
 parallel_session_seal(d.data());assert(emos_parallel_block_offer(h(),&session,PARALLEL_EXEXT,d.data()));return d;
}
static void failed(){
 assert((!releases||releaseFailure)&&reserved==1&&session.phase==PARALLEL_SESSION_IDLE);
 assert(hostPcDdr==255&&!hostPcAlt1&&!hostPcAlt2&&hostUart1Ier==0&&hostUart1Mctl==UART_MCTL_LOOP);
 assert(!emos_parallel_boot_uart_allowed());
 // P4 may still own DMA after a remote failure; expire then release it.
 owner->poll(now+3000,true,true);owner->poll(now+3001,true,true);
 assert(!allocation&&!outputs&&!watch);++cases;
}
int main(){
 (void)console_seal;(void)console_valid;
 for(bool reverse:{false,true})for(unsigned n:{1,2,255,256,4096}){
  setup(n,reverse);
  for(unsigned round=0;round<2;++round){reserved=1;auto d=admit(reverse);parkDelay=3;nested=true;
   assert(emos_parallel_native_coordinate(&session,d.data(),localData.data(),n));
   assert(releases==round+1&&unparks==round+1&&!faults&&!closeCalls);
   assert(!std::memcmp(peerData.data(),localData.data(),n));
   BYTE*out,direction;size_t length;assert(peer.takeCompleted(out,length,direction)&&out==peerData.data()&&length==n&&direction==reverse);
   assert(!peer.takeCompleted(out,length,direction));++cases;
  }
 }
 // Invalid inputs and interrupt-disabled/nested ownership: no park or pin mutation.
 for(unsigned refusal=0;refusal<10;++refusal){
  setup(8,false);auto d=admit(false);BYTE*b=localData.data();unsigned capacity=8;
  if(refusal==0)irq=0;
  if(refusal==1)reserved=2;
  if(refusal==2)capacity=7;
  if(refusal==3)b=nullptr;
  if(refusal==4){d[10]=0;parallel_session_seal(d.data());}
  if(refusal==5){d[11]=17;parallel_session_seal(d.data());}
  if(refusal==6)d[14]^=1;
  if(refusal==7){d[12]=2;parallel_session_seal(d.data());}
  if(refusal==8){d[4]^=1;parallel_session_seal(d.data());}
  if(refusal==9){BYTE old=emos_keyboard_lock();assert(!emos_parallel_boot_block_begin());emos_keyboard_unlock(old);reserved=0;}
  BYTE before=hostPdDr;assert(!emos_parallel_native_coordinate(&session,d.data(),b,capacity));
  assert(!parks&&!unparks&&!releases&&before==hostPdDr&&!allocation);peer.cancel();++cases;
 }
 for(bool reverse:{false,true})for(unsigned failure=0;failure<7;++failure){
  setup(8,reverse);auto d=admit(reverse);
  if(failure==0)parkFailure=true;
  if(failure==1)nativeFailure=true;
  if(failure==2)unparkFailure=true;
  if(failure==3)missing=true;
  if(failure==4)corrupt=true;
  if(failure==5)emos_key_faulted=1;
  if(failure==6)releaseFailure=true;
  assert(!emos_parallel_native_coordinate(&session,d.data(),localData.data(),8));
  // An already faulted contender is rejected before ownership is accepted.
  if(failure==5){assert(!parks&&!unparks&&!releases);peer.cancel();++cases;}
  else failed();
 }
 for(bool stoppedClock:{false,true})for(int phase:{EPH_DRAIN,EPH_ENTRY_ACK,EPH_ENTRY_CLEAR,EPH_ENTRY_ARM,EPH_RETURN_ACK,EPH_RETURN_REQUEST,EPH_RETURN_PEER}){
  setup(8,false);auto d=admit(false);stallPhase=phase;frozen=stoppedClock;
  if(phase==EPH_DRAIN)parkDelay=300000;
  assert(!emos_parallel_native_coordinate(&session,d.data(),localData.data(),8));failed();
 }
 for(bool reverse:{false,true})for(int phase:{EPH_DRAIN,EPH_ENTRY_RELEASE,EPH_ENTRY_ACK,EPH_ENTRY_CLEAR,EPH_ENTRY_ARM,EPH_LOCAL_ARM,EPH_BLOCK,EPH_BLOCK_RELEASE,EPH_RETURN_ACK,EPH_RETURN_REQUEST,EPH_RETURN_UART,EPH_RETURN_PEER}){
  setup(8,reverse);auto d=admit(reverse);faultPhase=phase;
  assert(!emos_parallel_native_coordinate(&session,d.data(),localData.data(),8));failed();
 }
 owner.reset();reset();std::cout<<"PASS "<<cases<<" paired native coordinator cases; actual C owners/status + P4 adapters, modeled assembly/UART scheduling\n";
}
