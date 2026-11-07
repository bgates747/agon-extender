// Execute the actual Runtime/Peer/TcpClient under host task/socket adapters.
// No LAN, UART, hardware or scheduler worker is created outside this process.
#include "extender/network/messages/runtime.hpp"
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <thread>
#include <sys/socket.h>
#include <cerrno>
using namespace agon::extender::network::messages;
static void(*taskEntry)(void*);static void *taskArg;
static std::atomic<std::int64_t> clockUs{100};
extern "C" std::int64_t esp_timer_get_time(){return clockUs.fetch_add(10);}
int xTaskCreate(void(*entry)(void*),const char*,unsigned,void*arg,unsigned,TaskHandle_t*out){taskEntry=entry;taskArg=arg;*out=&taskArg;return pdPASS;}
void vTaskDelay(unsigned){std::this_thread::sleep_for(std::chrono::milliseconds(1));}
void vTaskDelete(void*){}
extern "C" int __wrap_socket(int,int,int){return 42;}
extern "C" int __wrap_fcntl(int,int,...){return 0;}
extern "C" int __wrap_connect(int,const sockaddr*,socklen_t){return 0;}
extern "C" int __wrap_close(int){return 0;}
extern "C" ssize_t __wrap_recv(int,void*,size_t,int){errno=EAGAIN;return -1;}
extern "C" ssize_t __wrap_send(int,const void*,size_t n,int){return n;}
int main(){
 Runtime r;assert(r.start());
 unsigned char command[AGON_NET_HEADER+6]={};
 command[0]='N';command[1]='M';command[2]=1;command[3]=AGON_NET_CONNECT;
 command[4]=1;command[8]=1;command[12]=6;
 unsigned char ip[6]={127,0,0,1,0xD2,4};std::memcpy(command+AGON_NET_HEADER,ip,6);
 assert(r.submit(command,sizeof(command)));
 std::thread worker(taskEntry,taskArg);
 unsigned char reply[AGON_NET_BODY]={};unsigned n=0;
 for(unsigned i=0;i<1000&&!n;++i){n=r.take(reply);if(!n)vTaskDelay(1);}
 assert(n==AGON_NET_HEADER&&reply[3]==(AGON_NET_CONNECT|0x80)&&reply[13]==AGON_NET_CONNECTED);
 assert(std::memcmp(reply+4,command+4,8)==0);
 r.stop();worker.join();
 std::cout<<"actual-runtime-connect-reply=";
 for(unsigned i=0;i<n;++i){const char h[]="0123456789abcdef";std::cout<<h[reply[i]>>4]<<h[reply[i]&15];}
 std::cout<<" stopped/joined\n";
#if defined(AGON_EXTENDER_NM_ACCOUNTING)
 std::cout<<accounting::json()<<'\n';
#endif
}
