// Reuse the existing native/SDK/register donor. Exercise actual EMOS NP control
// encoding/parser/binding against actual P4 ParallelService and mailbox; only
// byte clocks, UART delivery and scheduler/SDK hardware are modeled.
#include "extender/network/messages/parallel_service.hpp"
#include <memory>
using NetMailbox=agon::extender::network::messages::Mailbox;
using NetService=agon::extender::network::messages::ParallelService<NetMailbox>;
static NetMailbox networkMailbox;
static std::unique_ptr<NetService> netp;
extern "C" {
#include "defines.h"
#include "emos_netp_transport.h"
BYTE emos_uart0_async_owned(void){return 0;}
}
// BODY
int main(){
 setup(142,false);reserved=0;
 netp=std::make_unique<NetService>(peer,networkMailbox);
 assert(!emos_netp_link_open()&&emos_netp_token&&!reserved);
 auto token=emos_netp_token;
 BYTE command[142]{},destination[142]{},work[142]{};unsigned bytes;uint32_t generation;uint16_t required;
 uint32_t query=0;unsigned count=0;
 for(unsigned payload:{0U,1U,127U,128U}){
  for(unsigned i=0;i<142;++i)command[i]=BYTE(i*53+payload);
  memcpy(command,"NM\001",3);command[3]=3;
  agon_net_put32(command+4,token);agon_net_put32(command+8,++query);
  command[12]=payload;command[13]=0;peerData.resize(14+payload);
  assert(!emos_netp_link_submit(command,14+payload)&&!reserved);
  // Let the actual P4 physical return retire before a worker takes its command.
  for(unsigned i=0;i<4;++i)synchronize();
  assert(networkMailbox.beginWork(work,bytes,generation)&&bytes==14+payload);
  assert(!memcmp(work,command,bytes));work[3]|=0x80;work[12]=0;work[13]=3;
  networkMailbox.completeWork(generation,work,14);peerData.resize(14);
  assert(!emos_netp_link_take(destination,sizeof(destination),&required)&&required==14&&!memcmp(destination,work,14));
  for(unsigned i=0;i<4;++i)synchronize();
  // A minimal POLL returns the echoed binary body, including max142 reverse.
  command[3]=2;agon_net_put32(command+8,++query);command[12]=0;
  peerData.resize(14);assert(!emos_netp_link_submit(command,14));
  for(unsigned i=0;i<4;++i)synchronize();
  assert(networkMailbox.beginWork(work,bytes,generation)&&bytes==14);
  work[3]|=0x80;work[12]=payload;work[13]=2;
  for(unsigned i=0;i<payload;++i)work[14+i]=BYTE(i*53+payload);
  networkMailbox.completeWork(generation,work,14+payload);
  memset(destination,0x5a,sizeof(destination));
  assert(emos_netp_link_take(destination,13,&required)==130&&required==14+payload&&!reserved);
  for(auto c:destination)assert(c==0x5a);
  peerData.resize(14+payload);
  assert(!emos_netp_link_take(destination,sizeof(destination),&required)&&required==14+payload&&!memcmp(destination,work,required));
  for(unsigned i=0;i<4;++i)synchronize();
  ++count;
 }
 assert(emos_netp_link_release()==31&&emos_netp_token==token&&!reserved);
 assert(networkMailbox.takeCloseRequest());networkMailbox.completeClose();
 assert(!emos_netp_link_release()&&!emos_netp_token&&!reserved&&h()->phase==EPH_UART);
 assert(peer.session.phase==PARALLEL_SESSION_IDLE);
 std::cout<<"PASS "<<count<<" actual EMOS NP parser/binding/P4 physical-service pairs, both directions and no-consume/positive close; no electrical timing\n";
}
