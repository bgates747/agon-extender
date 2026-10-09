// Maintained reset leaves; fake only SDK/Arduino byte boundaries, no bench.
#include <cassert>
#include <vector>
#include "extender/transport/p4_uart_reset.hpp"
#include "extender/transport/console_stream.hpp"
#include "extender/storage/application/mailbox.hpp"
using namespace agon::extender::transport;
static int core=0,maskResult=0,flushResult=0,queueResult=pdPASS,idleResult=0;
static std::vector<int> calls;
int xPortGetCoreID(){return core;}
esp_err_t uart_disable_intr_mask(int port,unsigned mask){
 assert(port==UART_NUM_1&&mask==(UART_INTR_TX_DONE|UART_INTR_TXFIFO_EMPTY));
 calls.push_back(1);return maskResult;
}
uart_dev_t hardware;
void uart_ll_txfifo_rst(uart_dev_t *hw){assert(hw==&hardware);calls.push_back(2);}
esp_err_t uart_flush_input(int port){assert(port==UART_NUM_1);calls.push_back(3);return flushResult;}
int xQueueReset(void *q){assert(q==&hardware);calls.push_back(4);return queueResult;}
esp_err_t uart_wait_tx_done(int port,int ticks){assert(port==UART_NUM_1&&!ticks);calls.push_back(5);return idleResult;}
esp_err_t uart_get_buffered_data_len(int,std::size_t *n){*n=1;return ESP_OK;}
int uart_read_bytes(int,void *p,unsigned,int){*static_cast<unsigned char*>(p)=0xaa;return 1;}
static void console_make(std::uint8_t *p,unsigned op,unsigned transaction,unsigned nonce,unsigned result){
 std::memset(p,0,CONSOLE_SIZE);p[0]='E';p[1]='X';p[2]=1;p[3]=op;p[12]=1;p[13]=result;
 for(unsigned i=0;i<4;++i){p[4+i]=transaction>>(8*i);p[8+i]=nonce>>(8*i);}console_seal(p);
}
int main(){
 for(int owner:{0,1})for(int mask:{0,1})for(int flush:{0,1})for(int queue:{0,1}){
  core=owner;maskResult=mask;flushResult=flush;queueResult=queue?pdPASS:0;calls.clear();
  bool ok=discardConsoleUart(&hardware);
  if(owner)assert(!ok&&calls.empty());
  else if(mask)assert(!ok&&(calls==std::vector<int>{1}));
  else if(flush)assert(!ok&&(calls==std::vector<int>{1,2,3}));
  else assert(ok==bool(queue)&&(calls==std::vector<int>{1,2,3,4}));
 }
 core=0;calls.clear();assert(!discardConsoleUart(nullptr)&&calls.empty());
 for(int owner:{0,1})for(int idle:{ESP_OK,ESP_FAIL}){
  core=owner;idleResult=idle;calls.clear();assert(consoleUartResetIdle()==(!owner&&!idle));
  assert(calls==(owner?std::vector<int>{}:std::vector<int>{5}));
 }
 ConsoleStream stream;std::uint8_t p[CONSOLE_SIZE],r[CONSOLE_SIZE];
 console_make(p,CONSOLE_PREPARE,17,0,0);assert(stream.session.request(p,1,33,r));
 console_make(p,CONSOLE_COMMIT,17,33,0);assert(stream.session.request(p,2,0,r));
 std::uint8_t setup[]{1,2,3,4};stream.feed(setup);assert(stream.read()==1);
 stream.cached=0xaa;assert(stream.write(0xff)==1);stream.fail("old error");
 stream.transportLost();assert(!stream.session.active()&&stream.pos==4&&stream.cached==-1);
 assert(!stream.count&&!stream.read_pos&&!stream.failure&&!stream.available()&&stream.read()==-1);
 assert(!stream.session.request(p,3,0,r)); // old commit cannot grant new epoch
 console_make(p,CONSOLE_PREPARE,18,0,0);assert(stream.session.request(p,4,34,r));
 console_make(p,CONSOLE_COMMIT,18,34,0);assert(stream.session.request(p,5,0,r));
 assert(stream.read()==0xaa); // fresh lease reads only newly provided UART data
 using agon::extender::storage::application::Mailbox;
 Mailbox q;std::uint8_t h[48]{},out[240];
 sd_header(h,4,1,1,1,0,28);h[44]=2;h[46]=1;sd_seal(h);
 assert(q.receive(h,48,1,false)&&q.owned&&q.requestSize==48);
 auto old=q.generation;q.requestSize=0;q.working=true;
 q.transportLost();assert(!q.owned&&!q.working&&!q.requestSize&&!q.responseSize);
 assert(!q.complete(old,h,48,true));
 assert(q.receive(h,48,2,false));auto fresh=q.generation;q.requestSize=0;q.working=true;
 assert(!q.complete(old,h,48,true));assert(q.working&&q.owned&&!q.closing);
 assert(q.complete(fresh,h,48,false)&&q.take(out)==48&&!std::memcmp(h,out,48));
 assert(!q.complete(fresh,h,48,false)); // duplicate worker completion rejected
 q.working=true;assert(q.complete(fresh,h,48,true)&&q.take(out)==48&&!q.owned);
}
