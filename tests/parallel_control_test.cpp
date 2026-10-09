// Actual EMOS foreground exchange + ISR dispatcher, actual P4 control owner.
// UART bytes are scripted here; no GPIO, electrical or throughput claim.
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
using P=agon::extender::transport::P4ParallelHandover;
using Owner=agon::extender::transport::ParallelControl;
using Packet=std::array<BYTE,16>;
static Owner peer;
static BYTE irq=1,tick,reserved=1;
static unsigned sends,clock_reads,cases;
static bool frozen,missing,duplicate,fail_send,drop_reservation;
static int corrupt=-1;
static unsigned corrupt_bit;
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
  assert(n==16 && parallel_session_valid(p));
  Packet reply{};assert(peer.request(p,100,0x12345678,reply.data()));
  if(missing)return EMOS_KEY_OK;
  auto original=reply;
  if(corrupt>=0){reply[corrupt]^=1u<<corrupt_bit;if(reseal)parallel_session_seal(reply.data());}
  receive(reply,15); // malformed frame length cannot publish a reply
  receive(reply);
  if(duplicate){original[8]^=0x20;parallel_session_seal(original.data());receive(original);}
  if(drop_reservation)reserved=0;
  return EMOS_KEY_OK;
}
static P ready(){P p;for(auto c:std::array<BYTE,5>{P::released|P::validHigh,P::validHigh,0,P::validHigh,P::validHigh|P::uartUp})p.step(c);assert(p.phase()==P::uart);return p;}
static void reset(){peer=Owner{};peer.handover=ready();irq=reserved=1;emos_key_faulted=0;tick=0;sends=clock_reads=0;frozen=missing=duplicate=fail_send=drop_reservation=reseal=false;corrupt=-1;}
static void negotiate(bool expected){
  t_emosParallelHandover h{EPH_UART,1,0,1};t_parallelSession s{};
  BYTE transaction[4]={1,2,3,4};
  assert(bool(emos_parallel_session_negotiate(&h,&s,transaction))==expected);
  assert(irq==1);assert(!emosVduBackend && !emos_console_owned);
  if(expected){assert(s.phase==3 && peer.session.phase==3);assert(!std::memcmp(s.bytes,peer.session.bytes,6));}
  else if(sends){assert(s.phase==0 && h.phase==EPH_RETURN_RELEASE);}
  else assert(s.phase==0 && h.phase==EPH_UART);
  // No wait remains: an unsolicited late reply cannot advance the lifecycle.
  Packet late{};late[0]='E';late[1]='X';late[2]=2;late[3]=0x83;late[4]=1;late[12]=3;parallel_session_seal(late.data());receive(late);
  assert(s.phase==(expected?3:0));++cases;
}
int main(){
  reset();negotiate(true);assert(sends==4);
  reset();duplicate=true;negotiate(true); // first complete reply is immutable
  for(unsigned i=0;i<16;++i)for(unsigned bit=0;bit<8;++bit){
    reset();corrupt=i;corrupt_bit=bit;negotiate(false);
    // CRC-correct altered semantic fields must still be refused; prepare's
    // fresh challenge itself has no prior identity to compare against.
    if(i<8 || i==12 || i==13){reset();corrupt=i;corrupt_bit=bit;reseal=true;negotiate(false);}
  }
  reset();missing=true;negotiate(false);assert(clock_reads<1000);
  reset();missing=frozen=true;negotiate(false);assert(clock_reads<262150);
  reset();fail_send=true;negotiate(false);assert(sends==1);
  reset();drop_reservation=true;negotiate(false);
  reset();reserved=0;negotiate(false);assert(!sends);
  reset();emos_console_owned=1;
  t_emosParallelHandover held{EPH_UART,1,0,1};t_parallelSession held_session{};BYTE held_txn[4]={1};
  assert(!emos_parallel_session_negotiate(&held,&held_session,held_txn));
  assert(!sends && held.phase==EPH_UART && held_session.phase==0);
  emos_console_owned=0;++cases;
  // Exact P4 staged deadline, clock wrap, failed commit after expiry, cold boot.
  for(uint32_t start:{0u,0xfffffff0u}){
    reset();t_parallelSession e{};Packet request{},reply{},commit{};BYTE txn[4]={1};
    assert(parallel_session_begin(&e,txn,request.data()));
    Owner cold;reply.fill(0xa5);auto sentinel=reply;
    assert(!cold.request(request.data(),start,7,reply.data()));assert(reply==sentinel);
    assert(peer.request(request.data(),start,7,reply.data()));
    assert(parallel_session_accept(&e,reply.data(),commit.data())==2);
    peer.expire(start+1999);assert(peer.session.phase==4);
    peer.expire(start+2000);assert(peer.session.phase==0 && peer.handover.phase()==P::recoveryRelease);
    assert(!peer.request(commit.data(),start+2000,8,reply.data()));
    assert(peer.handover.readyN());++cases;
  }
  // In-place prepare reply -> commit is supported without memcpy overlap.
  t_parallelSession s{};Packet p{};BYTE txn[4]={1},nonce[4]={2};
  parallel_session_begin(&s,txn,p.data());t_parallelSession other{};Packet reply{};
  parallel_session_peer(&other,p.data(),nonce,reply.data());
  assert(parallel_session_accept(&s,reply.data(),reply.data())==2);assert(reply[3]==3);
  std::cout<<"PASS "<<cases<<" paired foreground/ISR and P4 expiry cases\n";
}
