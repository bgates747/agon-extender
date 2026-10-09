// The runner prepends the existing native SDK model from its leaf fixture.
// Actual coordinator/parking/native/sequencer code is linked, not replaced.
#include "extender/transport/p4_block_coordinator.hpp"
using C=agon::extender::transport::P4BlockCoordinator;
using CR=C::Result;
uart_dev_t hardware;
static bool uartIdle=true,uartRestored=false;
static unsigned ring=0,fifo=0,restores=0;
static int critical=0;
void enterCritical(portMUX_TYPE*){assert(!critical);critical=1;}
void exitCritical(portMUX_TYPE*){assert(critical);critical=0;}
int uart_wait_tx_done(int u,int wait){assert(u==1&&!wait);return uartIdle?ESP_OK:ESP_ERR_TIMEOUT;}
int uart_get_buffered_data_len(int u,std::size_t*n){assert(u==1&&critical);*n=ring;return ESP_OK;}
unsigned uart_ll_get_rxfifo_len(uart_dev_t*){assert(critical);return fifo;}
bool uart_ll_is_tx_idle(uart_dev_t*){assert(critical);return uartIdle;}
void esp_rom_gpio_connect_in_signal(int value,int,bool invert){assert(value==GPIO_MATRIX_CONST_ONE_INPUT&&!invert);}
int uart_set_pin(int u,int tx,int rx,int rts,int cts){
 assert(u==1&&tx==18&&rx==17&&rts==20&&cts==19);
 if(fails())return ESP_FAIL;
 uartRestored=true;++restores;return ESP_OK;
}
static void boot(agon::extender::transport::ParallelControl &c,std::uint8_t *b,unsigned n){
 auto &h=c.handover;
 h.step(H::released);h.step(H::validHigh);h.step(0);h.step(H::validHigh);h.step(H::uartUp);
 assert(h.phase()==H::uart&&c.provide(b,n));
 c.session.phase=PARALLEL_SESSION_ACTIVE;
 const std::uint8_t session[]={1,2,3,4,0,0};std::memcpy(c.session.bytes,session,6);
}
static void offer(agon::extender::transport::ParallelControl &c,unsigned n,bool tx,
                  std::uint8_t *d,unsigned sequence=1,unsigned now=0){
 const std::uint8_t start[16]={'E','X',2,2,1,2,3,4,std::uint8_t(sequence),0,
   std::uint8_t(n),std::uint8_t(n>>8),std::uint8_t(tx),0,0,0};
 std::memcpy(d,start,16);parallel_session_seal(d);std::uint8_t reply[16];
 assert(c.request(d,now,0,reply)&&reply[3]==PARALLEL_ACK);
}
static void complete(agon::extender::transport::ParallelControl &c,std::uint8_t*d,
                     std::uint8_t *b,unsigned n,bool tx,unsigned now){
 std::uint8_t reply[16];d[3]=PARALLEL_COMPLETE;parallel_session_seal(d);
 assert(c.request(d,now,0,reply)&&reply[3]==PARALLEL_COMPLETE_ACK&&!reply[13]);
 std::uint8_t *out,direction;std::size_t length;
 assert(c.takeCompleted(out,length,direction)&&out==b&&length==n&&direction==tx);
}
static void drive(C &owner,bool tx,unsigned n,std::uint8_t*b,unsigned &now){
 valid=0;clockLevel=0;assert(owner.poll(++now,true,true)==CR::exclusive); // park
 assert(owner.poll(++now,true,true)==CR::exclusive); // release
 assert(owner.poll(++now,true,true)==CR::exclusive&&ready==0); // request
 valid=1;assert(owner.poll(++now,true,true)==CR::exclusive&&ready==1);
 clockLevel=1;assert(owner.poll(++now,true,true)==CR::exclusive);
 assert(owner.poll(++now,true,true)==CR::exclusive&&ready==0&&watch); // arm
 if(!tx)for(unsigned i=0;i<n;++i)dma[i]=std::uint8_t(73*i+17);
 signal(false);completed(tx,n);
 assert(owner.poll(++now,true,true)==CR::exclusive&&allocation); // hold last byte
 signal(true);assert(owner.poll(++now,true,true)==CR::exclusive&&ready==1&&!allocation);
 assert(!uartRestored); // DMA end is NOT permission to restore UART
 clockLevel=0;valid=1;assert(owner.poll(++now,true,true)==CR::exclusive);
 valid=0;assert(owner.poll(++now,true,true)==CR::exclusive&&ready==0);
 valid=1;assert(owner.poll(++now,true,true)==CR::exclusive);
 assert(owner.poll(++now,true,true)==CR::uart&&uartRestored&&ready==1);
 for(unsigned i=0;i<n;++i)assert(b[i]==std::uint8_t(73*i+17));
}
int main(){unsigned cases=0;
 for(bool tx:{false,true})for(unsigned n:{1,2,255,256,4096}) {
  reset();clockLevel=0;uartIdle=true;uartRestored=false;ring=fifo=restores=0;
  agon::extender::transport::ParallelControl c;std::vector<std::uint8_t>b(n,0xa5);
  if(tx)for(unsigned i=0;i<n;++i)b[i]=std::uint8_t(73*i+17);
  boot(c,b.data(),n);C owner(c,pins,14,16,15,18,17,20,19,0);std::uint8_t d[16];
  unsigned now=0;
  for(unsigned sequence=1;sequence<=2;++sequence) {
   offer(c,n,tx,d,sequence);uartRestored=false;
   assert(owner.poll(++now,true,true)==CR::drain); // peer has not released
   valid=0;
   int before=op;core=1;assert(owner.poll(++now,true,true)==CR::exclusive&&op==before);core=0;
   assert(owner.poll(++now,false,true)==CR::drain&&op==before);
   assert(owner.poll(++now,true,false)==CR::drain&&op==before);
   uartIdle=false;assert(owner.poll(++now,true,true)==CR::drain&&op==before);uartIdle=true;
   ring=1;assert(owner.poll(++now,true,true)==CR::drain&&op==before);ring=0;
   fifo=1;assert(owner.poll(++now,true,true)==CR::drain&&op==before);fifo=0;
   drive(owner,tx,n,b.data(),now);
   assert(c.pending());std::uint8_t *out=nullptr,direction=0;std::size_t length=0;
   assert(!c.takeCompleted(out,length,direction)); // not yet matched
   complete(c,d,b.data(),n,tx,now);++cases;
  }
  assert(restores==2&&!allocation&&!outputs);
 }
 // Genuine wrap: admission starts before UINT32 wrap; expiration crosses it.
 for(unsigned start:{0u,0xfffffff0u}) {
  reset();clockLevel=0;agon::extender::transport::ParallelControl c;std::uint8_t b[8]{},d[16];
  boot(c,b,8);C owner(c,pins,14,16,15,18,17,20,19,0);offer(c,8,false,d,1,start);
  assert(owner.poll(start,true,true)==CR::drain);
  assert(owner.poll(start+1999,true,true)==CR::drain);
  assert(owner.poll(start+2000,true,true)==CR::recovery);
  assert(c.handover.failed()&&!c.pending());++cases;
 }
 // Fail every SDK operation in the complete parking/native/return trace.
 // Unlike a leaf test, faults must revoke admission and never publish a receipt.
 for(bool tx:{false,true}) {
  reset();clockLevel=0;uartRestored=false;
  agon::extender::transport::ParallelControl countControl;std::uint8_t b[8],d[16];
  for(unsigned i=0;i<8;++i)b[i]=std::uint8_t(73*i+17);
  boot(countControl,b,8);C count(countControl,pins,14,16,15,18,17,20,19,0);
  offer(countControl,8,tx,d);unsigned now=0;drive(count,tx,8,b,now);const int total=op;
  complete(countControl,d,b,8,tx,now);
  for(int failure=0;failure<total;++failure) {
   reset();clockLevel=0;uartRestored=false;ring=fifo=0;
   agon::extender::transport::ParallelControl c;std::memset(b,0xa5,8);
   boot(c,b,8);C owner(c,pins,14,16,15,18,17,20,19,0);offer(c,8,tx,d);fail=failure;now=0;
   CR r=CR::exclusive;
   auto poll=[&](){r=owner.poll(++now,true,true);return r==CR::exclusive;};
   valid=0;
   bool proceed=poll()&&poll()&&poll();
   if(proceed){valid=1;proceed=poll();}
   if(proceed){clockLevel=1;proceed=poll()&&poll();}
   if(proceed){if(!tx)for(unsigned i=0;i<8;++i)dma[i]=std::uint8_t(73*i+17);
    signal(false);completed(tx,8);proceed=poll();}
   if(proceed){signal(true);proceed=poll();}
   if(proceed){clockLevel=0;valid=1;proceed=poll();}
   if(proceed){valid=0;proceed=poll();}
   if(proceed){valid=1;proceed=poll();}
   if(proceed)poll();
   assert(r==CR::recovery||r==CR::cleanupFault);
   assert(c.handover.failed()&&!c.pending());
   // A failure after an actual restore must not be treated as completed UART.
   std::uint8_t *out=nullptr,direction;std::size_t length;
   assert(!c.takeCompleted(out,length,direction));
   fail=-1;
   assert(owner.poll(++now,true,true)==CR::recovery);
   assert(!allocation&&!enabled&&!txLive&&!rxLive&&!delLive&&!watch&&!outputs);++cases;
  }
 }
 // Cancellation in every physical phase, plus a stuck cleanup attempt.
 for(bool timeout:{false,true})for(bool tx:{false,true})for(unsigned stage=0;stage<13;++stage) {
  reset();clockLevel=0;uartRestored=false;ring=fifo=0;
  agon::extender::transport::ParallelControl c;std::uint8_t b[8]{},d[16];
  boot(c,b,8);C owner(c,pins,14,16,15,18,17,20,19,0);offer(c,8,tx,d);
  unsigned now=0;valid=0;
  for(unsigned step=0;step<stage;++step) {
   if(step==3)valid=1;
   if(step==4)clockLevel=1;
   if(step==6){signal(false);completed(tx,8);}
   if(step==7)signal(true);
   if(step==8){clockLevel=0;valid=1;}
   if(step==9)valid=0;
   if(step==10)valid=1;
   owner.poll(++now,true,true);
  }
  if(timeout){
   // Observe the last transition before expiring that phase's own deadline.
   owner.poll(++now,true,true);now+=2000;
  } else c.cancel();
  if(allocation) {
   fail=op;assert(owner.poll(++now,true,true)==CR::cleanupFault&&allocation);
   // Repeated failure retains callback/DMA lifetime, and never runs boot cleanup.
   fail=op;assert(owner.poll(++now,true,true)==CR::cleanupFault&&allocation);
   fail=-1;
  }
  assert(owner.poll(++now,true,true)==CR::recovery);
  assert(!allocation&&!enabled&&!watch&&!outputs&&!c.pending()&&c.handover.failed());++cases;
 }
 // Ordinary console changes revoke only dormant capability: the UART grant
 // and ready level must survive. Pending payload/receipt cannot be bypassed.
 {
  reset();clockLevel=0;uartRestored=false;
  agon::extender::transport::ParallelControl c;std::uint8_t b[8],d[16];
  for(unsigned i=0;i<8;++i)b[i]=std::uint8_t(73*i+17);
  assert(!c.uartTransitionAllowed()&&!c.revokeUartCapability());
  boot(c,b,8);assert(c.uartTransitionAllowed()&&c.revokeUartCapability());
  assert(c.handover.phase()==H::uart&&c.session.phase==PARALLEL_SESSION_IDLE);
  c.session.phase=PARALLEL_SESSION_ACTIVE;c.session.bytes[4]=c.session.bytes[5]=0;
  C owner(c,pins,14,16,15,18,17,20,19,0);offer(c,8,true,d);unsigned now=0;
  assert(!c.uartTransitionAllowed()&&!c.revokeUartCapability());
  drive(owner,true,8,b,now);assert(!c.uartTransitionAllowed());
  std::uint8_t reply[16];d[3]=PARALLEL_COMPLETE;parallel_session_seal(d);
  assert(c.request(d,now,0,reply));assert(!c.revokeUartCapability());
  std::uint8_t*out,direction;std::size_t length;assert(c.takeCompleted(out,length,direction));
  assert(c.revokeUartCapability()&&c.handover.phase()==H::uart&&ready==1);++cases;
 }
 reset();
 std::cout<<"PASS "<<cases<<" native coordinator cases; both directions, repeated blocks, real adapters, SDK failures, cancellation and wrap\n";
}
