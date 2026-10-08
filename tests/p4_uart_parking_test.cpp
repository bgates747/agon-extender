// Real maintained adapter, fake only IDF's hardware boundary.
#include "extender/transport/p4_uart_parking.hpp"
#include <cassert>
#include <string>
#include <vector>
#include <iostream>
using Parking=agon::extender::transport::P4UartParking;
using R=Parking::Result;
uart_dev_t hardware;
static int core=0,critical=0,txStatus=ESP_OK,rxStatus=ESP_OK,failPin=-1;
static bool shiftIdle=true,restoreFails=false;
static std::size_t buffered=0;
static unsigned fifo=0;
static std::vector<std::string> io;
int xPortGetCoreID(){return core;}
void enterCritical(portMUX_TYPE*){assert(!critical);critical=1;}
void exitCritical(portMUX_TYPE*){assert(critical);critical=0;}
int uart_wait_tx_done(int u,int wait){assert(u==1 && wait==0 && !critical);return txStatus;}
int uart_get_buffered_data_len(int u,std::size_t*n){assert(u==1 && critical);*n=buffered;return rxStatus;}
unsigned uart_ll_get_rxfifo_len(uart_dev_t*){assert(critical);return fifo;}
bool uart_ll_is_tx_idle(uart_dev_t*){assert(critical);return shiftIdle;}
int gpio_set_direction(int pin,int mode){assert(mode==GPIO_MODE_INPUT);io.push_back("release"+std::to_string(pin));return pin==failPin?ESP_FAIL:ESP_OK;}
void esp_rom_gpio_connect_in_signal(int value,int sig,bool inv){assert(value==GPIO_MATRIX_CONST_ONE_INPUT && !inv);io.push_back("isolate"+std::to_string(sig));}
int uart_set_pin(int u,int tx,int rx,int rts,int cts){assert(u==1 && tx==18 && rx==17 && rts==20 && cts==19);io.push_back("restore");return restoreFails?ESP_FAIL:ESP_OK;}
static Parking fresh(){io.clear();return Parking(18,17,20,19,0);}
static void parked(const std::vector<std::string>& v){assert((v==std::vector<std::string>{"isolate10","isolate11","release18","release20"}));}
int main(){
 unsigned cases=0;
 for(int boundary=0;boundary<2;++boundary)for(int peer=0;peer<2;++peer)
 for(int cpu=0;cpu<2;++cpu)for(int tx=0;tx<3;++tx)
 for(int ring=0;ring<2;++ring)for(int hw=0;hw<2;++hw)for(int idle=0;idle<2;++idle){
  auto p=fresh();core=cpu;txStatus=tx;buffered=ring;fifo=hw;shiftIdle=idle;
  auto r=p.park(boundary,peer);
  bool admit=boundary && peer && cpu==0;
  if(admit && tx==ESP_FAIL)assert(r==R::fault && io.empty());
  else if(!admit || tx!=ESP_OK || ring || hw || !idle)assert(r==R::busy && io.empty());
  else {assert(r==R::ready);parked(io);
   assert(p.park(true,true)==R::ready && io.size()==4);
   assert(p.restore(false,true)==R::busy && p.restore(true,false)==R::busy && io.size()==4);
   core=1;assert(p.restore(true,true)==R::busy && io.size()==4);core=0;
   assert(p.restore(true,true)==R::ready && io.back()=="restore");
  }assert(!critical);++cases;
 }
 core=0;txStatus=ESP_OK;buffered=0;fifo=0;shiftIdle=true;
 for(int pin:{18,20}){
  auto p=fresh();failPin=pin;assert(p.park(true,true)==R::fault);parked(io);
  failPin=-1;assert(p.restore(true,true)==R::fault && p.park(true,true)==R::fault);++cases;
 }
 auto p=fresh();assert(p.park(true,true)==R::ready);io.clear();restoreFails=true;
 assert(p.restore(true,true)==R::fault && io.front()=="restore");
 io.erase(io.begin());parked(io);restoreFails=false;assert(p.restore(true,true)==R::fault);++cases;
 auto q=fresh();rxStatus=ESP_FAIL;assert(q.park(true,true)==R::fault && io.empty());++cases;
 std::cout<<"PASS "<<cases<<" native UART adapter cases; shift-register/RX fences, core affinity, release ordering, restore failure\n";
}
