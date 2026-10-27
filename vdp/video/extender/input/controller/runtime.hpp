// P4 adapter: one socket worker, HTTP admission/status, no eZ80 output.
#pragma once
#if !defined(ESP_PLATFORM)
#error "Controller runtime requires ESP-IDF"
#endif
#include "receiver.hpp"
#include "appliance.hpp"
#include "usb_host.hpp"
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
    {std::lock_guard<std::mutex>lock(mutex_);
      if(!initialized_){core_.begin(random64());appliance_=Appliance{};initialized_=true;}
      port_=ntohs(local.sin_port);}
    if(!usb_started_){
      usb_.diagnostics(&usbDiagnostics);
      usb_started_=usb_.start(&usbEvent,this);
      if(!usb_started_)printf("USB F310 client startup failed; LAN controller retained\n");
    }
    socket_=fd;stopping_=false;link_lost_=false;
    TaskHandle_t task{};
    // INPUT-002 scheduling control, not yet physically validated. Priority2
    // in installed27d93dcc sits below the continuously runnable priority3
    // parser on core0 and priority6 output on core1. Measured UDP service
    // gaps cluster around53ms, although ICMP remains sub-ms. Priority4 lets
    // this bounded eight-packet worker preempt the parser, while remaining
    // below drawing/output. Retain the2ms block; do not busy-spin or raise it
    // above video. Compare against the unchanged installed build before
    // attributing the observed lag to starvation or promoting this policy.
    if(xTaskCreate(&entry,"controller-udp",6144,this,4,&task)!=pdPASS){
      ::close(fd);socket_=-1;
      std::lock_guard<std::mutex>lock(mutex_);if(!local_.owns(core_))core_.invalidate(Fault::Link);port_=0;
      return false;
    }
    worker_.store(task);return true;
  }
  void linkLost()noexcept{link_lost_=true;}
  bool applianceRequest(const std::uint8_t*p){
    std::lock_guard<std::mutex>lock(mutex_);
    if(p[0]=='C'&&p[1]=='I'&&p[2]==CONTROLLER_CARRIER_VERSION&&p[3]==1&&
       controller_u32(p+4)&&controller_u16(p+12)&&!p[14]&&!p[15]){
      const auto timestamp=now();
      local_.rearm(core_,controller_u32(p+4),timestamp);local_.tick(core_,timestamp,random64());
    }
    return appliance_.request(p,core_,now());
  }
  bool applianceTake(std::uint8_t*out){
    std::lock_guard<std::mutex>lock(mutex_);return appliance_.take(out,core_,now());
  }
  void stop(){
    stopping_=true;
    while(worker_.load())vTaskDelay(1);
    std::lock_guard<std::mutex>lock(mutex_);
    // Ethernet loss invalidates a LAN owner, not a locally attached USB pad.
    if(!local_.owns(core_)){core_.invalidate(Fault::Link);appliance_=Appliance{};}
    port_=0;
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
  static void usbEvent(void*context,unsigned event,const State*state){
    auto&self=*static_cast<Runtime*>(context);std::lock_guard<std::mutex>lock(self.mutex_);
    if(event==0)self.local_.connect(self.core_);
    else if(event==1)self.local_.disconnect(self.core_);
    else if(event==2)self.local_.fail(self.core_);
    else if(event==4&&state)self.local_.report(*state);
    self.local_.tick(self.core_,now(),random64());
  }
  static void usbDiagnostics(const UsbDiagnostics*value,void*context){
    auto&self=*static_cast<Runtime*>(context);std::lock_guard<std::mutex>lock(self.mutex_);self.usb_status_=*value;
  }
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
    auto&self=owner(r);Snapshot s;unsigned port;UsbDiagnostics usb;bool local;
    {std::lock_guard<std::mutex>lock(self.mutex_);s=self.core_.snapshot(now());port=self.port_;usb=self.usb_status_;local=self.local_.owns(self.core_);}
    char out[1600];
    snprintf(out,sizeof(out),"{\"protocol\":1,\"instance\":\"%016llx\",\"session\":\"%016llx\",\"udp_port\":%u,\"active\":%s,\"valid\":%s,\"fault\":%u,\"sequence\":%lu,\"edge_ack\":%lu,\"queued\":%lu,\"received\":%lu,\"rejected\":%lu,\"age_ms\":%llu,\"sticks\":[%d,%d,%d,%d],\"triggers\":[%u,%u],\"held\":%u}",
      (unsigned long long)s.instance,(unsigned long long)s.session,port,s.active?"true":"false",s.valid?"true":"false",unsigned(s.fault),
      (unsigned long)s.sequence,(unsigned long)s.edge_ack,(unsigned long)s.queued,(unsigned long)s.received,(unsigned long)s.rejected,
      (unsigned long long)(s.valid?now()-s.last_state:0),s.state.sticks[0],s.state.sticks[1],s.state.sticks[2],s.state.sticks[3],s.state.triggers[0],s.state.triggers[1],s.state.held);
    const auto used=std::strlen(out);
    // Append source diagnostics while preserving the existing LAN fields.
    snprintf(out+used-1,sizeof(out)-used+1,",\"source\":\"%s\",\"usb\":{\"running\":%s,\"attached\":%s,\"valid\":%s,\"vid\":%u,\"pid\":%u,\"speed\":%u,\"address\":%u,\"interface\":%u,\"endpoint\":%u,\"packet\":%u,\"interval\":%u,\"reports\":%u,\"ignored\":%u,\"fault\":%u,\"report_age_ms\":%llu}}",
      s.active?(local?"usb":"lan"):"none",usb.running?"true":"false",usb.attached?"true":"false",usb.valid?"true":"false",
      usb.vid,usb.pid,usb.speed,usb.address,usb.interface,usb.endpoint,usb.packet,usb.interval,usb.reports,usb.ignored,usb.fault,
      (unsigned long long)(usb.last_report_ms?now()-usb.last_report_ms:0));
    const auto end=std::strlen(out);
    snprintf(out+end-2,sizeof(out)-end+2,",\"malformed\":%u,\"dpad_conflicts\":%u,\"anomaly_kind\":%u,\"anomaly_bytes\":%u,\"anomaly_hex\":\"%s\"}}",
      usb.malformed,usb.dpad_conflicts,usb.anomaly_kind,usb.anomaly_bytes,usb.anomaly_hex);
    return respond(r,200,out);
  }
  static esp_err_t open(httpd_req_t*r){
    std::uint8_t data[24]{};if(!body(r,data,sizeof(data))||get32(data+20))return respond(r,400,"{\"error\":\"invalid open\"}");
    sockaddr_storage peer{};socklen_t length=sizeof(peer);std::uint32_t address;
    if(getpeername(httpd_req_to_sockfd(r),reinterpret_cast<sockaddr*>(&peer),&length)<0||
       !httpPeerIPv4(peer,length,address))return respond(r,400,"{\"error\":\"IPv4 required\"}");
    auto&self=owner(r);int result;std::uint64_t session;
    {std::lock_guard<std::mutex>lock(self.mutex_);
      const bool local_reserved=self.local_.owns(self.core_)||
        (self.local_.ready()&&!self.core_.snapshot(now()).active);
      result=self.link_lost_.load()||!self.worker_.load()?503:local_reserved?409:self.core_.open(get64(data),get64(data+8),
        {address,get16(data+16)},get16(data+18),random64(),now());session=self.core_.snapshot(now()).session;}
    if(result!=200)return respond(r,result,"{\"error\":\"admission refused\"}");
    char out[100];snprintf(out,sizeof(out),"{\"session\":\"%016llx\",\"timeout_ms\":%u}",(unsigned long long)session,get16(data+18));
    return respond(r,200,out);
  }
  static esp_err_t close(httpd_req_t*r){
    std::uint8_t data[16];if(!body(r,data,sizeof(data)))return respond(r,400,"{\"error\":\"invalid close\"}");
    auto&self=owner(r);int result;
    {std::lock_guard<std::mutex>lock(self.mutex_);result=self.local_.owns(self.core_)?409:self.core_.close(get64(data),get64(data+8));}
    return respond(r,result,result==200?"{\"closed\":true}":"{\"error\":\"wrong session\"}");
  }
  static void entry(void*p){static_cast<Runtime*>(p)->run();}
  void run(){
    while(!stopping_.load()){
      if(link_lost_.load()){std::lock_guard<std::mutex>lock(mutex_);if(!local_.owns(core_))core_.invalidate(Fault::Link);}
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
  UsbSource local_;UsbHost usb_;UsbDiagnostics usb_status_{};bool initialized_{},usb_started_{};
  std::atomic<bool>stopping_{false},link_lost_{false};
  std::atomic<TaskHandle_t>worker_{nullptr};int socket_=-1;unsigned port_{};
};
inline Runtime runtime;
}
