// Real boot pad adapters; deterministic SDK/register boundary, not electricity.
#include "p4_uart_sdk_fake.hpp"
#include "extender/transport/p4_boot_release.hpp"
#include "extender/transport/p4_boot_startup.hpp"
#include <cassert>
#include <iostream>
extern "C" {
#include "emos_parallel_handover.h"
#include "eZ80.h"
volatile BYTE hostPcDr,hostPcDdr,hostPcAlt1,hostPcAlt2;
volatile BYTE hostPdDr,hostPdDdr,hostPdAlt1,hostPdAlt2;
volatile BYTE hostUart1Ier,hostUart1Mctl;
}
using H=agon::extender::transport::P4ParallelHandover;
using B=agon::extender::transport::P4BootRelease;
constexpr std::array<int,8> data{{17,18,19,20,32,33,36,46}};
static int core=0,failOperation=-1,operation=0;
static unsigned pMask=0,eMask=0;
static int directions[50]{},levels[50]{};
static bool armed=false;
static void ownership(){assert(!(pMask & eMask));}
static bool fails(){return operation++==failOperation;}
int xPortGetCoreID(){return core;}
int gpio_set_direction(int pin,int mode){
 if(fails())return ESP_FAIL;
 if(pin==15 && mode==GPIO_MODE_OUTPUT){assert(levels[pin]==1);assert(!pMask);armed=true;}
 directions[pin]=mode;
 for(unsigned i=0;i<data.size();++i)if(data[i]==pin){
  if(mode==GPIO_MODE_INPUT)pMask&=~(1u<<i);else pMask|=1u<<i;
 }ownership();return ESP_OK;
}
int gpio_reset_pin(int pin){
 if(fails())return ESP_FAIL;
 directions[pin]=GPIO_MODE_INPUT;
 for(unsigned i=0;i<data.size();++i)if(data[i]==pin)pMask&=~(1u<<i);
 ownership();return ESP_OK;
}
int gpio_set_level(int pin,int v){
 if(fails())return ESP_FAIL;
 if(pin==15 && !v){assert(armed);assert(!pMask);}
 levels[pin]=v;return ESP_OK;
}
int gpio_get_level(int pin){assert(pin==14||pin==16);return pin==14?!!(hostPdDr&0x20):!!(hostPdDr&0x80);}
int gpio_pullup_dis(int){return fails()?ESP_FAIL:ESP_OK;}
int gpio_pulldown_dis(int){return fails()?ESP_FAIL:ESP_OK;}
void esp_rom_gpio_connect_in_signal(int value,int sig,bool inv){assert(value==GPIO_MATRIX_CONST_ONE_INPUT && !inv && (sig==10||sig==11));}
extern "C" void emos_parallel_io_configure(UINT24 ddr,UINT24 a1,UINT24 a2){
 assert(!eMask); // boot requires reset/exclusive release, never normal traffic.
 hostPdDdr=(hostPdDdr&0x4f)|(ddr&0xb0);
 hostPdAlt1=(hostPdAlt1&0x4f)|(a1&0xb0);hostPdAlt2=(hostPdAlt2&0x4f)|(a2&0xb0);
 if((ddr&0xb0)==0x10)assert((hostPdDr&0xb0)==0x90); // latch preload C0V1.
}
extern "C" void emos_parallel_io_write_control(UINT24 bits){
 hostPdDr=(hostPdDr&0x4f)|(bits&0xb0)|0x10;
}
static void resetRegisters(){
 hostPcDdr=255;hostPcAlt1=hostPcAlt2=0;hostPdDr=0x4b;
 hostPdDdr=0x4f;hostPdAlt1=hostPdAlt2=0x4b;hostUart1Ier=5;hostUart1Mctl=0;
}
struct Pair {
 H p;B b{data,15,14,16,0};t_emosParallelHandover e{};
 bool eUp=false,pUp=false;
 unsigned eWait=0,pWait=0;int eLast=-1,pLast=-1;
 Pair(){pMask=eMask=0;armed=false;operation=0;failOperation=-1;core=0;
  resetRegisters();emos_parallel_boot_fence(&e);assert(b.begin(p));
  assert(hostUart1Ier==0 && hostUart1Mctl==16);
  assert(hostPdDdr==0x5f && hostPdAlt1==0x4b && hostPdAlt2==0x4b);
 }
 void etick(){
  if(eLast==e.phase)++eWait;else{eLast=e.phase;eWait=0;}
  // Owner deadline model, as in the retained handover harness. No timer in
  // the physical leaves; expiration releases and retries, never forces UART.
  if(e.phase!=EPH_UART && eWait>80){resetE();eWait=0;}
  if(directions[15]==GPIO_MODE_OUTPUT && !levels[15])hostPdDr&=~0x10;else hostPdDr|=0x10;
  auto a=emos_parallel_boot_poll(&e,eUp);
  if(a==EPH_RESTORE){assert(pMask==0);eMask=5;hostPcAlt2=3;hostPcDdr=0xfb;eUp=true;ownership();}
  else if(a==EPH_RELEASE){eMask=0;eUp=false;hostPcDdr=255;hostPcAlt1=hostPcAlt2=0;emos_parallel_boot_fence(&e);}
 }
 void ptick(){
  if(pLast==p.phase())++pWait;else{pLast=p.phase();pWait=0;}
  if(p.phase()!=H::uart && pWait>80){resetP();pWait=0;}
  auto r=b.poll(p,pUp);
  if(r==B::restore){assert((eMask&~5u)==0);pMask=10;pUp=true;ownership();}
  else if(r==B::fault){pMask=0;pUp=false;assert(b.begin(p));}
 }
 bool live()const{return e.phase==EPH_UART && p.phase()==H::uart;}
 void tick(unsigned n,unsigned ed,unsigned pd){if(n%ed==0)etick();if(n%pd==0)ptick();}
 void resetE(){eMask=0;eUp=false;resetRegisters();emos_parallel_boot_fence(&e);ownership();}
 void resetP(){pMask=0;pUp=false;assert(b.begin(p));ownership();}
};
int main(){unsigned cases=0;
 for(unsigned ed:{1,2,7})for(unsigned pd:{1,3,9}){
  Pair x;for(unsigned n=0;n<1000&&!x.live();++n)x.tick(n,ed,pd);assert(x.live());++cases;
  for(unsigned at=0;at<35;++at)for(bool re:{false,true}){
   Pair q;for(unsigned n=0;n<at;++n)q.tick(n,ed,pd);if(re)q.resetE();else q.resetP();
   for(unsigned n=at;n<4000&&!q.live();++n)q.tick(n,ed,pd);
   assert(q.live());++cases;
  }
 }
 // An absent or old peer at a fixed level never grants both UART outputs.
 for(int ready:{0,1}){
  Pair q;directions[15]=GPIO_MODE_INPUT;
  for(int n=0;n<100;++n){hostPdDr=(hostPdDr&~0x10)|(ready?0x10:0);
   auto a=emos_parallel_boot_poll(&q.e,0);assert(a!=EPH_RESTORE&&a!=EPH_LIVE);}
  assert(!eMask);++cases;
 }
 for(int valid:{0,1})for(int clock:{0,1}){
  Pair q;hostPdDr=(hostPdDr&~0xa0)|(valid?0x80:0)|(clock?0x20:0);
  for(int n=0;n<100;++n)assert(q.b.poll(q.p,true)!=B::live);
  assert(!pMask);++cases;
 }
 // Inject failure at each actual SDK operation of begin. Never advertise low.
 Pair count;const int total=operation;
 for(int op=0;op<total;++op){Pair q;operation=0;failOperation=op;armed=false;
  assert(!q.b.begin(q.p));assert(q.b.poll(q.p,false)==B::fault);assert(!armed);++cases;}
 {Pair q;auto before=operation;core=1;assert(!q.b.begin(q.p));assert(operation==before);
  assert(q.b.poll(q.p,false)==B::fault);assert(operation==before);core=0;++cases;}
 {Pair q;failOperation=operation;assert(q.b.poll(q.p,false)==B::fault);
  assert(directions[15]==GPIO_MODE_INPUT && !pMask);++cases;}
 {Pair q;q.ptick();q.p.cancel();auto before=operation;
  assert(q.b.poll(q.p,false)==B::fault);assert(operation==before);++cases;}
 // Withdraw a completion when actual eZ80 data pins are not released.
 {Pair q;hostPcAlt2=3;assert(emos_parallel_boot_poll(&q.e,1)==EPH_RELEASE);
  assert(q.e.phase==EPH_RETURN_RELEASE);++cases;}
 // Actual startup coordinator: asynchronous EMOS polling and real restore gate.
 for(unsigned stride:{1,3,9})for(bool restoreFails:{false,true}){
  Pair q;
  agon::extender::transport::P4BootStartup startup(data,15,14,16,0);
  assert(startup.begin(0));bool live=false;unsigned restores=0;
  for(unsigned now=0;now<7000&&!live;++now){
   if(now%stride==0){
    hostPdDr=(hostPdDr&~0x10)|(levels[15]?0x10:0);
    auto action=emos_parallel_boot_poll(&q.e,q.eUp);
    if(action==EPH_RESTORE){eMask=5;q.eUp=true;ownership();}
   }
   live=startup.poll(now,[&](){++restores;
    // EMOS asserted VALID after reciprocal all-input release.
    assert(hostPdDr&0x80);
    pMask=10;ownership();return !restoreFails;});
   if(restoreFails && restores)break;
  }
  assert(restores==1);
  if(restoreFails)assert(!live&&!pMask);else assert(live);
  ++cases;
 }
 // Absent peer, clock rollover and wrong core: no restore on a timer.
 for(unsigned level:{0,0x80,0x20,0xa0}){
  Pair q;hostPdDr=(hostPdDr&~0xa0)|level;
  agon::extender::transport::P4BootStartup startup(data,15,14,16,0);
  const std::uint32_t start=0xfffff000;assert(startup.begin(start));
  for(unsigned n=0;n<7000;++n)assert(!startup.poll(start+n,[](){assert(false);return true;}));
  assert(!pMask);++cases;
 }
 {Pair q;agon::extender::transport::P4BootStartup startup(data,15,14,16,0);
  core=1;auto before=operation;assert(!startup.begin(0));
  assert(!startup.poll(3000,[](){assert(false);return true;}));assert(before==operation);core=0;++cases;}
 std::cout<<"PASS "<<cases<<" paired physical boot-adapter cases; held recovery, asymmetric polling, one-board resets, missing peers, GPIO failure and output ownership\n";
}
