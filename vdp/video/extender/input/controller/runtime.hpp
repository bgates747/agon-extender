// P4 adapter: one socket worker, HTTP admission/status, no eZ80 output.
#pragma once
#if !defined(ESP_PLATFORM)
#error "Controller runtime requires ESP-IDF"
#endif
#include "receiver.hpp"
#include "appliance.hpp"
#include <atomic>
#include <mutex>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <esp_http_server.h>
#include <esp_random.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <lwip/sockets.h>
#include "http_peer.hpp"
namespace agon::extender::controller {
class Runtime {
 public:
  bool start(){
    if(worker_.load())return !link_lost_.load();
    int fd=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP);if(fd<0)return false;
    sockaddr_in local{};local.sin_family=AF_INET;local.sin_addr.s_addr=INADDR_ANY;
    if(bind(fd,reinterpret_cast<sockaddr*>(&local),sizeof(local))<0){::close(fd);return false;}
    socklen_t length=sizeof(local);
    if(getsockname(fd,reinterpret_cast<sockaddr*>(&local),&length)<0||
       fcntl(fd,F_SETFL,O_NONBLOCK)<0){::close(fd);return false;}
    {std::lock_guard<std::mutex>lock(mutex_);core_.begin(random64());appliance_=Appliance{};port_=ntohs(local.sin_port);}
    socket_=fd;stopping_=false;link_lost_=false;
    TaskHandle_t task{};
    if(xTaskCreate(&entry,"controller-udp",6144,this,2,&task)!=pdPASS){
      ::close(fd);socket_=-1;
      std::lock_guard<std::mutex>lock(mutex_);core_.invalidate(Fault::Link);port_=0;
      return false;
    }
    worker_.store(task);return true;
  }
  void linkLost()noexcept{link_lost_=true;}
  bool applianceRequest(const std::uint8_t*p){
    std::lock_guard<std::mutex>lock(mutex_);return appliance_.request(p,core_,now());
  }
  bool applianceTake(std::uint8_t*out){
    std::lock_guard<std::mutex>lock(mutex_);return appliance_.take(out,core_,now());
  }
  void stop(){
    stopping_=true;
    while(worker_.load())vTaskDelay(1);
    std::lock_guard<std::mutex>lock(mutex_);core_.invalidate(Fault::Link);appliance_=Appliance{};port_=0;
  }
  bool routes(httpd_handle_t server){
    for(auto route: {Route{"/controller/status",HTTP_GET,&status},
                    Route{"/controller/open",HTTP_POST,&open},
                    Route{"/controller/close",HTTP_POST,&close}}){
      httpd_uri_t uri{};uri.uri=route.name;uri.method=route.method;uri.handler=route.handler;uri.user_ctx=this;
      if(httpd_register_uri_handler(server,&uri)!=ESP_OK){
        // Admission is optional: remove partial controller registration without
        // tearing down keyboard/video/storage routes on the shared HTTP owner.
        httpd_unregister_uri_handler(server,"/controller/status",HTTP_GET);
        httpd_unregister_uri_handler(server,"/controller/open",HTTP_POST);
        httpd_unregister_uri_handler(server,"/controller/close",HTTP_POST);
        return false;
      }
    }
    return true;
  }
 private:
  struct Route{const char*name;httpd_method_t method;esp_err_t(*handler)(httpd_req_t*);};
  static std::uint64_t now(){return esp_timer_get_time()/1000;}
  static std::uint64_t random64(){std::uint64_t v;esp_fill_random(&v,sizeof(v));return v?v:1;}
  static Runtime& owner(httpd_req_t*r){return *static_cast<Runtime*>(r->user_ctx);}
  static esp_err_t respond(httpd_req_t*r,int code,const char*body){
    httpd_resp_set_status(r,code==200?"200 OK":code==409?"409 Conflict":code==410?"410 Gone":code==503?"503 Service Unavailable":"400 Bad Request");
    httpd_resp_set_type(r,"application/json");httpd_resp_set_hdr(r,"Cache-Control","no-store");
    return httpd_resp_send(r,body,HTTPD_RESP_USE_STRLEN);
  }
  static bool body(httpd_req_t*r,std::uint8_t*out,unsigned size){
    char intent[4]{};
    if(r->content_len!=size||httpd_req_get_hdr_value_len(r,"Origin")||
       httpd_req_get_hdr_value_str(r,"X-Agon-Controller",intent,sizeof(intent))!=ESP_OK||std::strcmp(intent,"1"))return false;
    unsigned have=0;const auto start=now();
    while(have<size){auto n=httpd_req_recv(r,reinterpret_cast<char*>(out+have),size-have);
      if(n<=0||now()-start>1000)return false;
      have+=unsigned(n);}
    return true;
  }
  static esp_err_t status(httpd_req_t*r){
    auto&self=owner(r);Snapshot s;unsigned port;
    {std::lock_guard<std::mutex>lock(self.mutex_);s=self.core_.snapshot(now());port=self.port_;}
    char out[768];
    snprintf(out,sizeof(out),"{\"protocol\":1,\"instance\":\"%016llx\",\"session\":\"%016llx\",\"udp_port\":%u,\"active\":%s,\"valid\":%s,\"fault\":%u,\"sequence\":%lu,\"edge_ack\":%lu,\"queued\":%lu,\"received\":%lu,\"rejected\":%lu,\"age_ms\":%llu,\"sticks\":[%d,%d,%d,%d],\"triggers\":[%u,%u],\"held\":%u}",
      (unsigned long long)s.instance,(unsigned long long)s.session,port,s.active?"true":"false",s.valid?"true":"false",unsigned(s.fault),
      (unsigned long)s.sequence,(unsigned long)s.edge_ack,(unsigned long)s.queued,(unsigned long)s.received,(unsigned long)s.rejected,
      (unsigned long long)(s.valid?now()-s.last_state:0),s.state.sticks[0],s.state.sticks[1],s.state.sticks[2],s.state.sticks[3],s.state.triggers[0],s.state.triggers[1],s.state.held);
    return respond(r,200,out);
  }
  static esp_err_t open(httpd_req_t*r){
    std::uint8_t data[24]{};if(!body(r,data,sizeof(data))||get32(data+20))return respond(r,400,"{\"error\":\"invalid open\"}");
    sockaddr_storage peer{};socklen_t length=sizeof(peer);std::uint32_t address;
    if(getpeername(httpd_req_to_sockfd(r),reinterpret_cast<sockaddr*>(&peer),&length)<0||
       !httpPeerIPv4(peer,length,address))return respond(r,400,"{\"error\":\"IPv4 required\"}");
    auto&self=owner(r);int result;std::uint64_t session;
    {std::lock_guard<std::mutex>lock(self.mutex_);
      result=self.link_lost_.load()||!self.worker_.load()?503:self.core_.open(get64(data),get64(data+8),
        {address,get16(data+16)},get16(data+18),random64(),now());session=self.core_.snapshot(now()).session;}
    if(result!=200)return respond(r,result,"{\"error\":\"admission refused\"}");
    char out[100];snprintf(out,sizeof(out),"{\"session\":\"%016llx\",\"timeout_ms\":%u}",(unsigned long long)session,get16(data+18));
    return respond(r,200,out);
  }
  static esp_err_t close(httpd_req_t*r){
    std::uint8_t data[16];if(!body(r,data,sizeof(data)))return respond(r,400,"{\"error\":\"invalid close\"}");
    auto&self=owner(r);int result;
    {std::lock_guard<std::mutex>lock(self.mutex_);result=self.core_.close(get64(data),get64(data+8));}
    return respond(r,result,result==200?"{\"closed\":true}":"{\"error\":\"wrong session\"}");
  }
  static void entry(void*p){static_cast<Runtime*>(p)->run();}
  void run(){
    while(!stopping_.load()){
      if(link_lost_.load()){std::lock_guard<std::mutex>lock(mutex_);core_.invalidate(Fault::Link);}
      {std::lock_guard<std::mutex>lock(mutex_);core_.expire(now());}
      for(unsigned i=0;i<8&&!link_lost_.load();++i){
        std::uint8_t data[MaxPacket+1];sockaddr_in peer{};socklen_t length=sizeof(peer);
        int n=recvfrom(socket_,data,sizeof(data),0,reinterpret_cast<sockaddr*>(&peer),&length);
        if(n<0)break;
        Packet p;if(!decode(data,unsigned(n),p))continue;
        std::array<std::uint8_t,40>ack;bool send;
        {std::lock_guard<std::mutex>lock(mutex_);send=core_.receive(p,{peer.sin_addr.s_addr,ntohs(peer.sin_port)},now(),ack);}
        if(send)sendto(socket_,ack.data(),ack.size(),0,reinterpret_cast<sockaddr*>(&peer),length);
      }
      const auto ticks=pdMS_TO_TICKS(2);vTaskDelay(ticks?ticks:1);
    }
    ::close(socket_);socket_=-1;worker_=nullptr;vTaskDelete(nullptr);
  }
  Receiver core_;Appliance appliance_;std::mutex mutex_;
  std::atomic<bool>stopping_{false},link_lost_{false};
  std::atomic<TaskHandle_t>worker_{nullptr};int socket_=-1;unsigned port_{};
};
inline Runtime runtime;
}
