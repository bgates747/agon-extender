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
static bool filterLive,filterEnabled;
struct Counter {bool live,channel,enabled,running,watch,cleared;int raw,edge,level,positive,negative,high,low;};
static Counter counters[2];
static bool counterRunning;
static int clockStopRace;
static bool countersLive(){return counters[0].live||counters[1].live;}
static void running(){counterRunning=counters[0].running||counters[1].running;}
static Counter& unit(void*u){auto i=(reinterpret_cast<std::uintptr_t>(u)-11)/10;assert(i<2);return counters[i];}
static Counter& channel(void*u){auto i=(reinterpret_cast<std::uintptr_t>(u)-12)/10;assert(i<2);return counters[i];}
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
int gpio_new_pin_glitch_filter(gpio_pin_glitch_filter_config_t const*c,void**u){
 assert(c->gpio_num==14&&c->clk_src==GLITCH_FILTER_CLK_SRC_DEFAULT&&!filterLive);
 if(fails())return ESP_FAIL;
 filterLive=true;*u=reinterpret_cast<void*>(4);return ESP_OK;
}
int gpio_glitch_filter_enable(void*){assert(filterLive&&!filterEnabled);if(fails())return ESP_FAIL;filterEnabled=true;return ESP_OK;}
int gpio_glitch_filter_disable(void*){assert(filterEnabled&&!enabled&&!txLive);if(fails())return ESP_FAIL;filterEnabled=false;return ESP_OK;}
int gpio_del_glitch_filter(void*){assert(filterLive&&!filterEnabled&&!enabled&&!txLive);if(fails())return ESP_FAIL;filterLive=false;return ESP_OK;}
void*heap_caps_aligned_alloc(std::size_t a,std::size_t n,int caps){
 assert(a==64&&!allocation);
#ifdef AGON_EXTENDER_EXEXT_STREAM
 assert(caps==(MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
#else
 assert(caps==(MALLOC_CAP_INTERNAL|MALLOC_CAP_DMA|MALLOC_CAP_8BIT));
#endif
if(fails())return nullptr;
 requested=n;allocation=std::malloc(n);return allocation;
}
void heap_caps_free(void*p){assert(p&&p==allocation&&!enabled&&!txLive&&!rxLive&&!delLive&&!watch&&!filterLive&&!filterEnabled);std::free(p);allocation=nullptr;}
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
 assert(c->clk_in_gpio_num==14&&c->clk_out_gpio_num==-1&&c->valid_gpio_num==16&&c->flags.free_clk);
 assert(c->ext_clk_freq_hz==10000000&&c->exp_clk_freq_hz==10000000&&c->max_recv_size==requested);
 for(unsigned i=0;i<16;++i)assert(c->data_gpio_nums[i]==(i<8?pins[i]:-1));
 if(fails())return ESP_FAIL;
 watch=false;rxLive=true;*u=reinterpret_cast<void*>(2);return 0;
}
int parlio_new_rx_level_delimiter(parlio_rx_level_delimiter_config_t const*c,void**u){
 assert(c->valid_sig_line_id==15&&c->sample_edge==PARLIO_SAMPLE_EDGE_NEG&&c->flags.active_low_en&&c->eof_data_len==requested);
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

int pcnt_new_unit(pcnt_unit_config_t const*c,void**u){
 assert(c->low_limit==-32768&&c->high_limit==32767&&c->flags.accum_count);
 if(fails())return ESP_FAIL;
 unsigned i=0;while(i<2&&counters[i].live)++i;assert(i<2);
 counters[i]={};counters[i].live=true;counters[i].raw=7;*u=reinterpret_cast<void*>(11+i*10);return ESP_OK;
}
int pcnt_new_channel(void*u,pcnt_chan_config_t const*c,void**v){
 auto&x=unit(u);assert(x.live&&!x.channel&&!x.enabled);
 assert((c->edge_gpio_num==16&&c->level_gpio_num==-1)||(c->edge_gpio_num==14&&c->level_gpio_num==16));
 if(fails())return ESP_FAIL;
 x.channel=true;x.edge=c->edge_gpio_num;x.level=c->level_gpio_num;*v=reinterpret_cast<void*>(reinterpret_cast<std::uintptr_t>(u)+1);return ESP_OK;
}
int pcnt_channel_set_edge_action(void*u,int p,int n){auto&x=channel(u);assert(n==1&&(p==0||p==1));if(fails())return ESP_FAIL;x.positive=p;x.negative=n;return ESP_OK;}
int pcnt_channel_set_level_action(void*u,int h,int l){auto&x=channel(u);assert((h==0||h==2)&&l==0);if(fails())return ESP_FAIL;x.high=h;x.low=l;return ESP_OK;}
int pcnt_unit_add_watch_point(void*u,int n){auto&x=unit(u);assert(n==32767&&!x.enabled);if(fails())return ESP_FAIL;x.watch=true;return ESP_OK;}
int pcnt_unit_enable(void*u){auto&x=unit(u);assert(x.live&&x.watch&&!x.enabled);if(fails())return ESP_FAIL;x.enabled=true;return ESP_OK;}
int pcnt_unit_clear_count(void*u){auto&x=unit(u);assert(x.enabled&&!x.running&&x.watch);if(fails())return ESP_FAIL;x.raw=0;x.cleared=true;return ESP_OK;}
int pcnt_unit_start(void*u){auto&x=unit(u);assert(x.enabled&&!x.running&&x.cleared&&valid==1);if(fails())return ESP_FAIL;x.running=true;running();return ESP_OK;}
int pcnt_unit_get_count(void*u,int*n){auto&x=unit(u);assert(x.enabled);if(fails())return ESP_FAIL;*n=x.raw;return ESP_OK;}
int pcnt_unit_stop(void*u){auto&x=unit(u);assert(x.enabled&&x.running);if(fails())return ESP_FAIL;
 if(x.edge==14&&clockStopRace){
  if(clockStopRace==1)++x.raw;
  else for(auto&v:counters)if(v.running&&v.edge==16)v.raw+=2;
  clockStopRace=0;
 }
 x.running=false;running();return ESP_OK;}
int pcnt_unit_disable(void*u){auto&x=unit(u);assert(x.enabled&&!x.running);if(fails())return ESP_FAIL;x.enabled=false;return ESP_OK;}
int pcnt_del_channel(void*u){auto&x=channel(u);assert(x.channel&&!x.enabled);if(fails())return ESP_FAIL;x.channel=false;return ESP_OK;}
// Partial unit destruction cannot safely retry in pinned IDF; its permanent
// failure/reset case is tested separately by p4_valid_counter_test.cpp.
int pcnt_del_unit(void*u){auto&x=unit(u);assert(x.live&&!x.channel&&!x.enabled);x.live=false;return ESP_OK;}

static void reset(){
 assert(!allocation&&!enabled&&!txLive&&!rxLive&&!delLive&&!watch&&!outputs&&!countersLive()&&!counterRunning&&!filterLive&&!filterEnabled);
 for(auto&x:counters)x={};
 clockStopRace=0;
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
static void signal(bool high){
 if(valid!=int(high))for(auto&x:counters)if(x.running&&x.edge==16)x.raw+=high?x.positive:x.negative;
 valid=high;if(watch)edge(edgeContext);
}
static void clockEdges(unsigned n){
 for(auto&x:counters)if(x.running&&x.edge==14&&(valid?x.high:x.low)==PCNT_CHANNEL_LEVEL_ACTION_KEEP)x.raw+=int(n)*x.negative;
}
static void completed(bool tx,std::size_t n){
 if(tx){parlio_tx_done_event_data_t e;tc.on_trans_done(reinterpret_cast<void*>(1),&e,context);}
 else {parlio_rx_event_data_t e{reinterpret_cast<void*>(3),dma,n};rc.on_receive_done(reinterpret_cast<void*>(2),&e,context);}
}
int main(){unsigned cases=0;
 for(bool tx:{false,true})for(unsigned n:{1,2,3,7,255,256,257,1024,4095,4096})for(bool late:{false,true}){
  reset();auto h=admitted(n,tx);P p(pins,14,16,15,0);std::vector<std::uint8_t>b(n+2,0xa5);
  for(unsigned i=0;i<n;++i)if(tx)b[i+1]=std::uint8_t(i*73+17);
  assert(p.arm(h,true,tx,b.data()+1,n,n,0,100)==R::pending&&ready==0&&!watch&&counterRunning);
  if(tx)assert(std::memcmp(dma,b.data()+1,n)==0);else for(unsigned i=0;i<n;++i)dma[i]=std::uint8_t(i*73+17);
  signal(false);clockEdges(n);
  if(tx&&!late){completed(tx,n);assert(p.poll(1)==R::pending&&allocation&&ready==0);}
  // Callback may arrive before or after VALID deasserts; PCNT proves the
  // independently counted record without any GPIO interrupt handler.
  signal(true);clockEdges(16);if(!tx||late){assert(p.poll(2)==R::pending);completed(tx,n);}
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
  if(kind<2)continue; // Missing/extra physical edges have dedicated PCNT cases below.
  reset();auto h=admitted(8,tx);P p(pins,14,16,15,0);std::uint8_t b[8];std::memset(b,0xa5,8);
  assert(p.arm(h,true,tx,b,8,8,0,100)==R::pending);
  if(kind==0)signal(true); // End without start.
  else {signal(false);clockEdges(8);if(kind==1)signal(false);else signal(true);}
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
  signal(false);clockEdges(8);signal(true);
  if(tx){parlio_tx_done_event_data_t e;tc.on_trans_done(reinterpret_cast<void*>(99),&e,context);}
  else {parlio_rx_event_data_t e{reinterpret_cast<void*>(3),dma,8};rc.on_receive_done(reinterpret_cast<void*>(99),&e,context);}
  assert(p.poll(1)==R::fault&&!allocation);++cases;
 }
 // A fixed-count RX callback needs its exact unit/buffer/delimiter and
 // length. Missing GPIO IRQ delivery cannot fail a valid record, while GPIO
 // levels/edges alone without that callback must time out without publication.
 for(int kind:{0,1,2,3,4,5}){
  reset();auto h=admitted(8,false);P p(pins,14,16,15,0);std::uint8_t b[8];std::memset(b,0xa5,8);
  assert(p.arm(h,true,false,b,8,8,0,100)==R::pending&&!watch);
  signal(false);clockEdges(8);signal(true);
  if(kind<5){
   parlio_rx_event_data_t e{reinterpret_cast<void*>(3),dma,8};
   if(kind==0)e.recv_bytes=7;
   if(kind==1)e.recv_bytes=9;
   if(kind==3)e.data=dma+1;
   if(kind==4)e.delimiter=reinterpret_cast<void*>(99);
   rc.on_receive_done(reinterpret_cast<void*>(kind==2?99:2),&e,context);
   assert(p.poll(1)==R::fault);
  }else{
   assert(p.poll(1)==R::pending&&allocation&&ready==0);
   assert(p.poll(100)==R::timeout);
  }
  for(auto v:b)assert(v==0xa5);
  assert(!allocation&&!enabled&&!watch&&!outputs);++cases;
 }
 // A TX callback and inactive VALID alone cannot certify peer consumption.
 // Hardware counts both polarities without any GPIO interrupt handler.
 for(int edges:{0,1,3,4}){
  reset();auto h=admitted(1,true);P p(pins,14,16,15,0);std::uint8_t b[1]{17};
  assert(p.arm(h,true,true,b,1,1,0,100)==R::pending&&!watch&&counterRunning);
  for(int i=0;i<edges;++i)signal(i%2!=0);
  completed(true,1);
  if(edges<2){assert(p.poll(1)==R::pending);assert(p.poll(100)==R::timeout);}
  else assert(p.poll(1)==R::fault);
  assert(!allocation&&!outputs&&!countersLive());++cases;
 }
 for(bool tx:{false,true}){reset();auto h=admitted(1,tx);P p(pins,14,16,15,0);std::uint8_t b[1]{};
  int before=op;assert(p.arm(h,true,tx,b,1,1,0,2001)==R::rejected&&op==before);++cases;}
 // Fixed EOF must not hide a short/overlong/unfinished or repeated record.
 for(int kind:{0,1,2,3,4,5}){
  reset();auto h=admitted(8,false);P p(pins,14,16,15,0);std::uint8_t b[8];std::memset(b,0xa5,8);
  assert(p.arm(h,true,false,b,8,8,0,100)==R::pending);
  if(kind!=0){signal(false);clockEdges(kind==1?7:kind==2?9:8);}
  completed(false,8);
  if(kind==3){assert(p.poll(1)==R::pending&&allocation);signal(true);assert(p.poll(2)==R::complete);}
  else {
   if(kind!=4)signal(true);
   if(kind==5){signal(false);signal(true);}
   auto r=p.poll(1);
   if(kind==2||kind==5)assert(r==R::fault);
   else {assert(r==R::pending);assert(p.poll(100)==R::timeout);}
   for(auto v:b)assert(v==0xa5);
  }
  assert(!allocation&&!outputs&&!countersLive());++cases;
 }
 // A late clock during freeze or a whole extra VALID pulse between counter
 // stops cannot pass. VALID remains live until after CLOCK is frozen.
 for(int race:{1,2}){
  reset();auto h=admitted(8,false);P p(pins,14,16,15,0);std::uint8_t b[8];std::memset(b,0xa5,8);
  assert(p.arm(h,true,false,b,8,8,0,100)==R::pending);
  signal(false);clockEdges(8);signal(true);completed(false,8);clockStopRace=race;
  assert(p.poll(1)==R::fault&&!allocation&&!countersLive());
  for(auto v:b)assert(v==0xa5);
  ++cases;
 }
 // Fail every SDK/allocation operation in successful start and cleanup traces.
 for(bool tx:{false,true}){
  reset();auto h=admitted(8,tx);std::uint8_t b[8]{};P count(pins,14,16,15,0);
  assert(count.arm(h,true,tx,b,8,8,0,100)==R::pending);signal(false);clockEdges(8);signal(true);completed(tx,8);
  assert(count.poll(1)==R::complete);const int total=op;
  for(int i=0;i<total;++i){
   reset();h=admitted(8,tx);P p(pins,14,16,15,0);std::memset(b,0xa5,8);fail=i;
   auto r=p.arm(h,true,tx,b,8,8,0,100);
   if(r==R::pending){signal(false);clockEdges(8);signal(true);completed(tx,8);r=p.poll(1);}
   assert(r==R::fault||r==R::cleanupFault);
   if(r==R::cleanupFault){assert(allocation);for(auto v:b)assert(v==0xa5);fail=-1;assert(p.cancel()==R::fault);}
   assert(!allocation&&!enabled&&!watch&&!outputs);++cases;
  }
 }
 reset();std::cout<<"PASS "<<cases<<" actual native payload cases: both directions, exact lengths, guards, wrap, late completion, invalid edges, cleanup fault injection, retained storage\n";
}
