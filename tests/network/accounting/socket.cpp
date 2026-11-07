// Actual TcpClient with link-wrapped POSIX calls, not a LAN/hardware probe.
#include "extender/network/messages/tcp_client.hpp"
#include "extender/network/messages/accounting.hpp"
#include <sys/socket.h>
#include <atomic>
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <iostream>
#include <thread>
using namespace agon::extender::network::messages;
static std::atomic<std::int64_t> clockUs{100};
static int receiveMode,sendMode;
extern "C" std::int64_t esp_timer_get_time(){return clockUs.fetch_add(10);}
extern "C" int __wrap_socket(int,int,int){return 42;}
extern "C" int __wrap_fcntl(int,int,...){return 0;}
extern "C" int __wrap_connect(int,const sockaddr*,socklen_t){return 0;}
extern "C" int __wrap_close(int){return 0;}
extern "C" ssize_t __wrap_recv(int,void *p,size_t n,int){
 if(receiveMode==0){errno=EAGAIN;return -1;}
 if(receiveMode==1)return 0;
 if(receiveMode==2){assert(n>=1);static_cast<unsigned char*>(p)[0]=0xA5;return 1;}
 errno=EIO;return -1;
}
extern "C" ssize_t __wrap_send(int,const void*,size_t n,int){
 if(sendMode==0){errno=EAGAIN;return -1;}if(sendMode==1)return n;
 errno=EIO;return -1;
}
int main(){
 TcpClient c;assert(c.start("127.0.0.1",1234)==Result::Ok);unsigned char b[2]={0x5A};
 auto r=c.read(b,2);assert(r.state==IoState::WouldBlock&&r.size==0);
 receiveMode=2;r=c.read(b,2);assert(r.state==IoState::Progress&&r.size==1&&b[0]==0xA5);
 receiveMode=1;r=c.read(b,2);assert(r.state==IoState::Closed&&r.size==0);
 receiveMode=3;r=c.read(b,2);assert(r.state==IoState::Error&&r.size==0);
 auto w=c.write(b,1);assert(w.state==IoState::WouldBlock&&w.size==0);
 sendMode=1;w=c.write(b,1);assert(w.state==IoState::Progress&&w.size==1);
 sendMode=2;w=c.write(b,1);assert(w.state==IoState::Error&&w.size==0);
 c.close();
 std::cout<<"actual-socket-events=4read/3write bytes=A5,1 no-retry\n";
#if defined(AGON_EXTENDER_NM_ACCOUNTING)
 {accounting::Scope live(accounting::Metric::PeerRequest);std::cout<<accounting::json()<<'\n';}
 auto work=[](){for(unsigned i=0;i<100;++i){accounting::Scope s(accounting::Metric::PeerTick);s.result(0);}};
 std::thread a(work),d(work);a.join();d.join();
 std::cout<<accounting::json()<<'\n';
#endif
}
