#include "p4_native_sdk_fake.hpp"
#include "extender/transport/p4_native_payload.hpp"
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <vector>
using P=agon::extender::transport::P4NativePayload;
using H=agon::extender::transport::P4ParallelHandover;
using R=P::Result;
constexpr std::array<int,8> pins{{17,18,19,20,32,33,36,46}};
static int core,op,fail=-1,ready=1,valid=1,clockLevel=1;
static bool enabled,txLive,rxLive,delLive,outputs,watch;
static void* allocation;static std::size_t requested;
static void(*edge)(void*);static void*edgeContext;
static parlio_tx_event_callbacks_t tc;static parlio_rx_event_callbacks_t rc;
static void*context;static std::uint8_t* dma;
static std::size_t size;static unsigned idle;
static bool fails(){return op++==fail;}
int xPortGetCoreID(){return core;}
int gpio_get_level(int p){assert(p==14||p==16);return p==14?clockLevel:valid;}
int gpio_set_level(int p,int v){assert(p==15);if(fails())return ESP_FAIL;ready=v;return 0;}
int gpio_install_isr_service(int f){assert(f==0);return fails()?ESP_FAIL:ESP_ERR_INVALID_STATE;}
int gpio_set_intr_type(int p,int t){assert(p==16&&t==GPIO_INTR_ANYEDGE);return fails()?ESP_FAIL:0;}
int gpio_isr_handler_add(int p,void(*f)(void*),void*c){assert(p==16);if(fails())return ESP_FAIL;watch=true;edge=f;edgeContext=c;return 0;}
int gpio_isr_handler_remove(int p){assert(p==16);if(fails())return ESP_FAIL;watch=false;return 0;}
int gpio_reset_pin(int){if(fails())return ESP_FAIL;outputs=false;return 0;}
int gpio_set_direction(int,int m){assert(m==GPIO_MODE_INPUT);if(fails())return ESP_FAIL;outputs=false;return 0;}
int gpio_pullup_dis(int){return fails()?ESP_FAIL:0;}
int gpio_pulldown_dis(int){return fails()?ESP_FAIL:0;}
void*heap_caps_aligned_alloc(std::size_t a,std::size_t n,int caps){
 assert(a==64&&caps==7&&!allocation);if(fails())return nullptr;
 requested=n;allocation=std::malloc(n);return allocation;
}
void heap_caps_free(void*p){assert(p&&p==allocation&&!enabled&&!txLive&&!rxLive&&!delLive&&!watch);std::free(p);allocation=nullptr;}
int parlio_new_tx_unit(parlio_tx_unit_config_t const*c,void**u){
 assert(c->data_width==8&&c->trans_queue_depth==1&&c->clk_src==PARLIO_CLK_SRC_EXTERNAL);
 assert(c->clk_in_gpio_num==14&&c->clk_out_gpio_num==-1&&c->valid_gpio_num==-1);
 assert(c->input_clk_src_freq_hz==10000000&&c->output_clk_freq_hz==10000000);
 assert(c->shift_edge==PARLIO_SHIFT_EDGE_NEG);
 for(unsigned i=0;i<16;++i)assert(c->data_gpio_nums[i]==(i<8?pins[i]:-1));
 if(fails())return ESP_FAIL;
 txLive=true;outputs=true;*u=reinterpret_cast<void*>(1);return 0;
}
int parlio_tx_unit_register_event_callbacks(void*,parlio_tx_event_callbacks_t const*c,void*x){if(fails())return ESP_FAIL;tc=*c;context=x;return 0;}
int parlio_tx_unit_enable(void*){if(fails())return ESP_FAIL;enabled=true;return 0;}
int parlio_tx_unit_disable(void*){if(fails())return ESP_FAIL;enabled=false;return 0;}
int parlio_del_tx_unit(void*){assert(!enabled);if(fails())return ESP_FAIL;txLive=false;return 0;}
int parlio_tx_unit_transmit(void*,void const*p,std::size_t bits,parlio_transmit_config_t const*c){
 assert(bits%8==0&&requested==bits/8&&p==allocation&&c->flags.queue_nonblocking);
 if(fails())return ESP_FAIL;
 dma=const_cast<std::uint8_t*>(static_cast<std::uint8_t const*>(p));size=bits/8;idle=c->idle_value;
 assert(idle==dma[size-1]);return 0;
}
int parlio_new_rx_unit(parlio_rx_unit_config_t const*c,void**u){
 assert(c->data_width==8&&c->trans_queue_depth==1&&c->clk_src==PARLIO_CLK_SRC_EXTERNAL);
 assert(c->clk_in_gpio_num==14&&c->clk_out_gpio_num==-1&&c->valid_gpio_num==16&&!c->flags.free_clk);
 assert(c->ext_clk_freq_hz==10000000&&c->exp_clk_freq_hz==10000000&&c->max_recv_size==requested);
 for(unsigned i=0;i<16;++i)assert(c->data_gpio_nums[i]==(i<8?pins[i]:-1));
 if(fails())return ESP_FAIL;
 watch=false;rxLive=true;*u=reinterpret_cast<void*>(2);return 0;
}
int parlio_new_rx_level_delimiter(parlio_rx_level_delimiter_config_t const*c,void**u){
 assert(c->valid_sig_line_id==15&&c->sample_edge==PARLIO_SAMPLE_EDGE_NEG&&c->flags.active_low_en);
 if(fails())return ESP_FAIL;
 delLive=true;*u=reinterpret_cast<void*>(3);return 0;
}
int parlio_rx_unit_register_event_callbacks(void*,parlio_rx_event_callbacks_t const*c,void*x){if(fails())return ESP_FAIL;rc=*c;context=x;return 0;}
int parlio_rx_unit_enable(void*,bool b){assert(b);if(fails())return ESP_FAIL;enabled=true;return 0;}
int parlio_rx_unit_disable(void*){if(fails())return ESP_FAIL;enabled=false;return 0;}
int parlio_del_rx_unit(void*){assert(!enabled);if(fails())return ESP_FAIL;rxLive=false;return 0;}
int parlio_del_rx_delimiter(void*){assert(!rxLive);if(fails())return ESP_FAIL;delLive=false;return 0;}
int parlio_rx_unit_receive(void*,void*p,std::size_t n,parlio_receive_config_t const*c){
 assert(p==allocation&&n==requested&&c->delimiter==reinterpret_cast<void*>(3));
 if(fails())return ESP_FAIL;
 dma=static_cast<std::uint8_t*>(p);size=n;return 0;
}
static void reset(){
 assert(!allocation&&!enabled&&!txLive&&!rxLive&&!delLive&&!watch&&!outputs);
 core=0;op=0;fail=-1;ready=valid=clockLevel=1;edge=nullptr;edgeContext=context=nullptr;tc={};rc={};
}
static H admitted(unsigned n,bool tx){
 H h;h.step(H::released);h.step(H::validHigh);h.step(0);h.step(H::validHigh);h.step(H::uartUp);
 assert(h.phase()==H::uart);
 std::uint8_t session[6]={1,2,3,4,0,0};
 std::uint8_t offer[16]={'E','X',2,2,1,2,3,4,1,0,std::uint8_t(n),std::uint8_t(n>>8),std::uint8_t(tx),0,0,0},ack[16];
 auto crc=console_crc(offer);offer[14]=crc;offer[15]=crc>>8;
 assert(h.admit(PARALLEL_EXEXT,session,offer,ack));
 h.step(H::quiet);h.step(H::released);h.step(0);h.step(H::validHigh);h.step(H::validHigh|H::clockHigh);
 assert(h.phase()==H::localArm);return h;
}
static void signal(bool high){valid=high;assert(watch);edge(edgeContext);}
static void completed(bool tx,std::size_t n){
 if(tx){parlio_tx_done_event_data_t e;tc.on_trans_done(reinterpret_cast<void*>(1),&e,context);}
 else {parlio_rx_event_data_t e{reinterpret_cast<void*>(3),dma,n};rc.on_receive_done(reinterpret_cast<void*>(2),&e,context);}
}
int main(){unsigned cases=0;
 for(bool tx:{false,true})for(unsigned n:{1,2,3,7,255,256,257,1024,4095,4096})for(bool late:{false,true}){
  reset();auto h=admitted(n,tx);P p(pins,14,16,15,0);std::vector<std::uint8_t>b(n+2,0xa5);
  for(unsigned i=0;i<n;++i)if(tx)b[i+1]=std::uint8_t(i*73+17);
  assert(p.arm(h,true,tx,b.data()+1,n,n,0,100)==R::pending&&ready==0&&watch);
  if(tx)assert(std::memcmp(dma,b.data()+1,n)==0);else for(unsigned i=0;i<n;++i)dma[i]=std::uint8_t(i*73+17);
  signal(false);
  if(!late){completed(tx,n);assert(p.poll(1)==R::pending&&allocation&&ready==0);}
  signal(true);if(late){assert(p.poll(2)==R::pending);completed(tx,n);}
  assert(p.poll(3)==R::complete&&ready==1&&!outputs&&!allocation);
  for(unsigned i=0;i<n;++i)assert(b[i+1]==std::uint8_t(i*73+17));
  assert(b.front()==0xa5&&b.back()==0xa5);
  // A retained callback cannot revive this one-shot operation after cleanup.
  completed(tx,n);assert(p.poll(4)==R::complete);
  assert(p.arm(h,true,tx,b.data(),n,n,5,100)==R::rejected);++cases;
 }
 for(bool tx:{false,true}){
  reset();auto h=admitted(8,tx);P p(pins,14,16,15,0);std::uint8_t b[8]{};
  int before=op;core=1;assert(p.arm(h,true,tx,b,8,8,0,100)==R::wrongOwner&&op==before);core=0;
  assert(p.arm(h,false,tx,b,8,8,0,100)==R::rejected&&op==before);
  H noGrant;assert(p.arm(noGrant,true,tx,b,8,8,0,100)==R::rejected&&op==before);
  for(unsigned n:{0,9,4097})assert(p.arm(h,true,tx,b,8,n,0,100)==R::rejected&&op==before);
  valid=0;assert(p.arm(h,true,tx,b,8,8,0,100)==R::rejected&&op==before);valid=1;
  assert(p.arm(h,true,tx,b,8,8,0xfffffffe,5)==R::pending);
  before=op;core=1;assert(p.poll(4)==R::wrongOwner&&op==before);assert(p.cancel()==R::wrongOwner&&op==before);core=0;
  assert(p.poll(1)==R::pending);assert(p.poll(3)==R::timeout&&!allocation&&ready==1);++cases;
 }
 for(bool tx:{false,true})for(int kind:{0,1,2,3,4}){
  reset();auto h=admitted(8,tx);P p(pins,14,16,15,0);std::uint8_t b[8];std::memset(b,0xa5,8);
  assert(p.arm(h,true,tx,b,8,8,0,100)==R::pending);
  if(kind==0)signal(true); // End without start.
  else {signal(false);if(kind==1)signal(false);else signal(true);}
  if(kind==2)completed(tx,7);else if(kind==3)completed(tx,9);else if(kind==4){completed(tx,8);completed(tx,8);}
  auto expected=(tx&&(kind==2||kind==3))?R::complete:R::fault;
  assert(p.poll(1)==expected);
  if(!tx)for(auto v:b)assert(v==0xa5);
  ++cases;
 }
 for(bool tx:{false,true}){
  reset();auto h=admitted(8,tx);P p(pins,14,16,15,0);std::uint8_t b[8]{};
  assert(p.arm(h,true,tx,b,8,8,0,100)==R::pending);
  h.cancel();assert(p.poll(1)==R::fault&&!allocation&&!outputs);++cases;
 }
 for(bool tx:{false,true}){
  reset();auto h=admitted(8,tx);P p(pins,14,16,15,0);std::uint8_t b[8]{};
  assert(p.arm(h,true,tx,b,8,8,0,100)==R::pending);
  signal(false);signal(true);
  if(tx){parlio_tx_done_event_data_t e;tc.on_trans_done(reinterpret_cast<void*>(99),&e,context);}
  else {parlio_rx_event_data_t e{reinterpret_cast<void*>(3),dma,8};rc.on_receive_done(reinterpret_cast<void*>(99),&e,context);}
  assert(p.poll(1)==R::fault&&!allocation);++cases;
 }
 // Fail every SDK/allocation operation in successful start and cleanup traces.
 for(bool tx:{false,true}){
  reset();auto h=admitted(8,tx);std::uint8_t b[8]{};P count(pins,14,16,15,0);
  assert(count.arm(h,true,tx,b,8,8,0,100)==R::pending);signal(false);signal(true);completed(tx,8);
  assert(count.poll(1)==R::complete);const int total=op;
  for(int i=0;i<total;++i){
   reset();h=admitted(8,tx);P p(pins,14,16,15,0);std::memset(b,0xa5,8);fail=i;
   auto r=p.arm(h,true,tx,b,8,8,0,100);
   if(r==R::pending){signal(false);signal(true);completed(tx,8);r=p.poll(1);}
   assert(r==R::fault||r==R::cleanupFault);
   if(r==R::cleanupFault){assert(allocation);for(auto v:b)assert(v==0xa5);fail=-1;assert(p.cancel()==R::fault);}
   assert(!allocation&&!enabled&&!watch&&!outputs);++cases;
  }
 }
 reset();std::cout<<"PASS "<<cases<<" actual native payload cases: both directions, exact lengths, guards, wrap, late completion, invalid edges, cleanup fault injection, retained storage\n";
}
