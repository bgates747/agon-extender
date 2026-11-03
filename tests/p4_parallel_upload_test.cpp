// Execute the actual PSRAM source and loop-DMA leaf against SDK/GPIO models.
// This proves ownership and bytes in a model, never physical PSRAM timing.
#include "p4_native_sdk_fake.hpp"
#include "extender/transport/p4_parallel_upload.hpp"
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <vector>
#include <unistd.h>
#include <sys/wait.h>
using namespace agon::extender::transport;
using U=P4ParallelUpload;using R=U::Result;
constexpr std::array<int,8> pins{{17,18,19,20,32,33,36,46}};
NativeParlioSignals parlio_periph_signals={{{{{{},100}},{{{},200}}}}};
static int core,op,fail=-1,valid=1,clockLevel=1,ready=1;
static bool unitLive,enabled,outputs,filterLive,filterEnabled,mutationBeforePark;
static bool parked;
static bool deleteFails;
static bool closeDuringClockRead;
static unsigned deletes;
static void *allocation;
static std::size_t allocated,logical,cycle,clocked;
static const std::uint8_t *dma;
static unsigned byteChecks;
struct Counter{bool live,channel,enabled,running,cleared,gated;int count;};
static Counter counters[2];
static bool fails(){return op++==fail;}
static Counter& counter(void *p){auto n=(reinterpret_cast<std::uintptr_t>(p)-11)/10;assert(n<2);return counters[n];}
int xPortGetCoreID(){return core;}
int gpio_get_level(int p){assert(p==14||p==16);return p==14?clockLevel:valid;}
int gpio_set_level(int p,int n){assert(p==15&&parked);if(fails())return ESP_FAIL;ready=n;return ESP_OK;}
int gpio_reset_pin(int p){assert(p!=14&&p!=16&&parked);if(fails())return ESP_FAIL;outputs=false;return ESP_OK;}
int gpio_set_direction(int,int n){assert(n==GPIO_MODE_INPUT&&parked);return fails()?ESP_FAIL:ESP_OK;}
int gpio_pullup_dis(int){return fails()?ESP_FAIL:ESP_OK;}
int gpio_pulldown_dis(int){return fails()?ESP_FAIL:ESP_OK;}
int gpio_func_sel(int,int n){assert(n==PIN_FUNC_GPIO);if(!parked)mutationBeforePark=true;return fails()?ESP_FAIL:ESP_OK;}
void esp_rom_gpio_connect_out_signal(int,int,bool a,bool b){assert(!a&&!b);outputs=true;if(!parked)mutationBeforePark=true;}
void *heap_caps_aligned_alloc(std::size_t a,std::size_t n,int caps){
 assert(a==64&&n%64==0&&caps==(MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT)&&!allocation);
 if(fails())return nullptr;
 allocation=std::aligned_alloc(a,n);allocated=n;return allocation;
}
void heap_caps_free(void *p){assert(p==allocation&&!unitLive&&!enabled);std::free(p);allocation=nullptr;}
int parlio_new_tx_unit(parlio_tx_unit_config_t const *c,void **p){
 assert(!unitLive&&c->data_width==8&&c->trans_queue_depth==1);
 for(int n:c->data_gpio_nums)assert(n==GPIO_NUM_NC); // no data pin touched before park
 assert(c->clk_src==PARLIO_CLK_SRC_EXTERNAL&&c->clk_in_gpio_num==14);
 assert(c->max_transfer_size==allocated&&c->shift_edge==PARLIO_SHIFT_EDGE_NEG);
 if(fails())return ESP_FAIL;
 unitLive=true;*p=reinterpret_cast<void*>(1);return ESP_OK;
}
int parlio_tx_unit_enable(void*){assert(parked&&!enabled);if(fails())return ESP_FAIL;enabled=true;return ESP_OK;}
int parlio_tx_unit_disable(void*){assert(enabled);if(fails())return ESP_FAIL;enabled=false;return ESP_OK;}
int parlio_del_tx_unit(void*){
 assert(!enabled);++op;++deletes;
 if(deleteFails)return ESP_FAIL;
 unitLive=false;return ESP_OK;
}
int parlio_tx_unit_transmit(void*,void const *p,std::size_t bits,parlio_transmit_config_t const *c){
 assert(enabled&&p==allocation&&bits==allocated*8&&bits%512==0);
 assert(c->flags.loop_transmission&&c->flags.queue_nonblocking);
 assert(c->idle_value==static_cast<std::uint8_t const*>(p)[logical-1]);
 if(fails())return ESP_FAIL;
 dma=static_cast<std::uint8_t const*>(p);cycle=bits/8;return ESP_OK;
}
int gpio_new_pin_glitch_filter(gpio_pin_glitch_filter_config_t const *c,void **p){
 assert(c->gpio_num==14&&!filterLive);if(fails())return ESP_FAIL;
 filterLive=true;*p=reinterpret_cast<void*>(3);return ESP_OK;
}
int gpio_glitch_filter_enable(void*){assert(filterLive&&!filterEnabled);if(fails())return ESP_FAIL;filterEnabled=true;return ESP_OK;}
int gpio_glitch_filter_disable(void*){assert(filterEnabled&&!enabled);if(fails())return ESP_FAIL;filterEnabled=false;return ESP_OK;}
int gpio_del_glitch_filter(void*){assert(filterLive&&!filterEnabled&&!enabled);if(fails())return ESP_FAIL;filterLive=false;return ESP_OK;}
int pcnt_new_unit(pcnt_unit_config_t const *c,void **p){
 assert(c->high_limit==32767&&c->flags.accum_count);if(fails())return ESP_FAIL;
 unsigned i=0;while(i<2&&counters[i].live)++i;assert(i<2);counters[i]={};counters[i].live=true;
 *p=reinterpret_cast<void*>(11+i*10);return ESP_OK;
}
int pcnt_new_channel(void *p,pcnt_chan_config_t const *c,void **out){
 auto &x=counter(p);assert(x.live);if(fails())return ESP_FAIL;x.channel=true;
 x.gated=c->level_gpio_num==16;assert(c->edge_gpio_num==(x.gated?14:16));*out=p;return ESP_OK;
}
int pcnt_channel_set_edge_action(void*,int,int){return fails()?ESP_FAIL:ESP_OK;}
int pcnt_channel_set_level_action(void*,int,int){return fails()?ESP_FAIL:ESP_OK;}
int pcnt_unit_add_watch_point(void*,int n){assert(n==32767);return fails()?ESP_FAIL:ESP_OK;}
int pcnt_unit_enable(void *p){if(fails())return ESP_FAIL;counter(p).enabled=true;return ESP_OK;}
int pcnt_unit_clear_count(void *p){if(fails())return ESP_FAIL;counter(p).count=0;counter(p).cleared=true;return ESP_OK;}
int pcnt_unit_start(void *p){assert(counter(p).cleared);if(fails())return ESP_FAIL;counter(p).running=true;return ESP_OK;}
int pcnt_unit_get_count(void *p,int *out){
 if(fails())return ESP_FAIL;
 auto &x=counter(p);*out=x.count;
 if(closeDuringClockRead&&x.gated){
  // The last CLOCK and VALID closure can occur after this sampled CLOCK value
  // but before the caller reads its separate VALID counter.
  closeDuringClockRead=false;++x.count;++clocked;valid=1;
  for(auto &c:counters)if(c.running&&!c.gated)++c.count;
 }
 return ESP_OK;
}
int pcnt_unit_stop(void *p){if(fails())return ESP_FAIL;counter(p).running=false;return ESP_OK;}
int pcnt_unit_disable(void *p){assert(!counter(p).running);if(fails())return ESP_FAIL;counter(p).enabled=false;return ESP_OK;}
int pcnt_del_channel(void *p){assert(!counter(p).enabled);if(fails())return ESP_FAIL;counter(p).channel=false;return ESP_OK;}
// Destructive SDK delete failure is separately covered by the retained counter
// suite. Do not simulate a recoverable delete when the pinned SDK can half-free.
int pcnt_del_unit(void *p){assert(!counter(p).enabled&&!counter(p).channel);++op;counter(p).live=false;return ESP_OK;}
static std::uint8_t pattern(std::size_t i){return std::uint8_t(i*73+(i>>8)*19+17);}
static FILE *spool(std::size_t n){
 FILE *f=std::tmpfile();assert(f);std::vector<std::uint8_t> b(65536);
 for(std::size_t at=0;at<n;){auto count=std::min(b.size(),n-at);
  for(std::size_t i=0;i<count;++i)b[i]=pattern(at+i);
  assert(std::fwrite(b.data(),1,count,f)==count);at+=count;
 }std::rewind(f);return f;
}
static void signal(bool high){
 if(valid!=int(high))for(auto &x:counters)if(x.running&&!x.gated)++x.count;
 valid=high;
}
static void clocks(std::size_t n,bool check=true){
 assert(enabled&&dma&&ready==0&&valid==0);
 for(auto &x:counters)if(x.running&&x.gated)x.count+=int(n);
 if(check)for(std::size_t i=0;i<n;++i){assert(dma[(clocked+i)%cycle]==pattern(clocked+i));++byteChecks;}
 clocked+=n;
}
static void reset(){
 assert(!allocation&&!unitLive&&!enabled&&!filterLive&&!filterEnabled&&!outputs);
 for(auto &x:counters){assert(!x.live);x={};}
 core=op=0;fail=-1;valid=clockLevel=ready=1;parked=mutationBeforePark=false;
 logical=cycle=clocked=allocated=0;dma=nullptr;
 deleteFails=false;deletes=0;
 closeDuringClockRead=false;
}
int main(){unsigned cases=0;byteChecks=0;
 for(std::size_t n:{1U,63U,64U,65U,4095U,4096U,65535U,65536U,65537U,1100000U}){
  reset();logical=n;auto f=spool(n);P4UploadSource source;
  assert(source.load(f,n));std::fclose(f);assert(source.allocated()==((n+63)&~std::size_t(63)));
  U u(pins,14,16,15,0);assert(u.prepare(source)==R::prepared&&!outputs&&!mutationBeforePark);
  assert(source.borrowed()&&!source.release());
  auto before=op;assert(u.arm(false,n,0,30000)==R::rejected&&op==before);
  parked=true;assert(u.arm(true,n+1,0,30000)==R::rejected&&op==before);
  assert(u.arm(true,n,UINT32_MAX-10,30000)==R::pending&&outputs&&ready==0);
  assert(u.poll(UINT32_MAX-9)==R::pending); // initial VALID high is not completion
  signal(false);
  for(std::size_t at=0;at<n;){auto count=std::min(std::size_t(512),n-at);
   clocks(count);at+=count;
   assert(u.poll(1)==R::pending); // arbitrarily many paused SD-write intervals
   assert(u.poll(2)==R::pending&&clocked==at&&source.borrowed());
  }
  assert(u.poll(3)==R::pending&&enabled); // N clocks alone cannot release pins
  signal(true);assert(u.poll(4)==R::complete&&!outputs&&!enabled&&ready==1);
  assert(!source.borrowed()&&source.release());++cases;
 }
 // Closure between the two counter reads must wait for the next coherent poll.
 for(std::size_t n:{1U,65537U,1100000U}){
  reset();logical=n;auto file=spool(n);P4UploadSource s;
  assert(s.load(file,n));std::fclose(file);U u(pins,14,16,15,0);
  assert(u.prepare(s)==R::prepared);parked=true;
  assert(u.arm(true,n,0,100)==R::pending);signal(false);clocks(n-1);
  closeDuringClockRead=true;
  assert(u.poll(1)==R::pending&&enabled&&s.borrowed());
  assert(u.poll(2)==R::complete&&!outputs&&!enabled&&s.release());++cases;
 }
 // Maximum capacity and its last byte without a giant per-byte model loop.
 reset();logical=P4UploadSource::maximumBytes;auto f=spool(logical);P4UploadSource max;
 assert(max.load(f,logical));std::fclose(f);U large(pins,14,16,15,0);
 assert(large.prepare(max)==R::prepared);parked=true;
 assert(large.arm(true,logical,0,600000)==R::pending);signal(false);
 assert(dma[logical-1]==pattern(logical-1));clocks(logical,false);signal(true);
 assert(large.poll(1)==R::complete&&max.release());++cases;
 // Invalid/short/extra source and allocation refusal happen before any pins.
 for(unsigned kind=0;kind<5;++kind){
  reset();auto bad=spool(kind==1?64:65);P4UploadSource s;
  if(kind==0)fail=op;
  assert(!s.load(bad,kind==2?64:kind==3?0:kind==4?P4UploadSource::maximumBytes+1:65));
  std::fclose(bad);assert(!s.size()&&!outputs&&s.release());++cases;
 }
 for(unsigned kind=0;kind<4;++kind){
  reset();logical=65537;auto file=spool(logical);P4UploadSource s;
  assert(s.load(file,logical));std::fclose(file);U u(pins,14,16,15,0);
  assert(u.prepare(s)==R::prepared);parked=true;
  assert(u.arm(true,logical,0,100)==R::pending);signal(false);
  if(kind!=3)clocks(kind==0?logical-1:kind==1?logical+1:logical,false);
  if(kind==2){signal(true);signal(false);signal(true);} // extra VALID pulse
  else if(kind!=3)signal(true);
  auto r=u.poll(kind==3?100:1);
  assert(r==(kind==0?R::shortPayload:kind==3?R::timeout:R::fault));
  assert(!outputs&&!enabled&&s.release());++cases;
 }
 // Inject a one-shot SDK failure at each preparation/arm/stop/release call.
 // Source must remain borrowed whenever cleanup reports uncertainty.
 for(int fault=0;fault<130;++fault){
  reset();logical=65537;auto file=spool(logical);P4UploadSource s;
  assert(s.load(file,logical));std::fclose(file);U u(pins,14,16,15,0);
  fail=op+fault;auto r=u.prepare(s);
  if(r==R::prepared){parked=true;r=u.arm(true,logical,0,100);}
  if(r==R::pending){signal(false);clocks(logical,false);signal(true);r=u.poll(1);}
  if(r==R::cleanupFault)assert(s.borrowed()&&!s.release());
  fail=-1;assert(u.cancel()==R::fault);assert(!s.borrowed()&&s.release());++cases;
 }
 // A destructive SDK delete failure requires reset. Prove no unsafe retry and
 // retained source in a separate process; process exit models hardware reset.
 // _Exit deliberately avoids pretending that C++ destruction retires DMA.
 reset();auto child=fork();assert(child>=0);
 if(child==0){
  logical=65537;auto file=spool(logical);P4UploadSource s;
  assert(s.load(file,logical));std::fclose(file);U u(pins,14,16,15,0);
  assert(u.prepare(s)==R::prepared);parked=true;
  assert(u.arm(true,logical,0,100)==R::pending);signal(false);
  clocks(logical,false);signal(true);deleteFails=true;
  assert(u.poll(1)==R::cleanupFault&&!enabled&&!outputs&&deletes==1);
  assert(s.borrowed()&&!s.release());deleteFails=false;
  assert(u.cancel()==R::cleanupFault&&deletes==1&&s.borrowed());
  std::_Exit(0);
 }
 int status=0;assert(waitpid(child,&status,0)==child&&WIFEXITED(status)&&WEXITSTATUS(status)==0);++cases;
 reset();std::cout<<"PASS "<<cases<<" whole-file upload cases, "<<byteChecks
  <<" modeled payload bytes checked; no physical rate claim\n";
}
