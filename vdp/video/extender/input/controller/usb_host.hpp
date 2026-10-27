// P4-owned, F310-only XInput client on the already installed USB host library.
// ESP-IDF 5.5.5 API/example contracts; all client operations run on this task.
// USB callbacks retain reports; neither callbacks nor this task write UART.
#pragma once
#include "usb_f310.hpp"
#include <usb/usb_host.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <atomic>
#include <cstdio>
#include <cstring>
namespace agon::extender::controller {
struct UsbDiagnostics {
  bool running{},attached{},valid{};
  unsigned address{},vid{},pid{},speed{},interface{},endpoint{},packet{},interval{},reports{},ignored{},fault{};
  unsigned malformed{},dpad_conflicts{},anomaly_bytes{},anomaly_kind{};
  char anomaly_hex[129]{};
  std::uint64_t last_report_ms{};
};
class UsbHost {
 public:
  // The sink copies state/lifecycle under the runtime mutex. A null state
  // with event0 connects, event1 disconnects, event2 faults, event3 heartbeats.
  using Sink=void(*)(void*,unsigned,const State*);
  bool start(Sink sink,void*context){
    if(started_.load())return true;
    sink_=sink;context_=context;
    TaskHandle_t task{};
    if(xTaskCreate(&entry,"controller-usb",5120,this,4,&task)!=pdPASS)return false;
    started_=true;return true;
  }
 private:
  static void entry(void*p){static_cast<UsbHost*>(p)->run();}
  static void event(const usb_host_client_event_msg_t*e,void*p){
    auto&self=*static_cast<UsbHost*>(p);
    if(e->event==USB_HOST_CLIENT_EVENT_DEV_GONE){
      if(e->dev_gone.dev_hdl==self.device_){
        self.gone_=true;self.diag_.attached=self.diag_.valid=false;
        self.sink_(self.context_,1,nullptr);
      }
    }else if(e->event==USB_HOST_CLIENT_EVENT_NEW_DEV){
      if(self.pending_count_<8)self.pending_[self.pending_count_++]=e->new_dev.address;
      else self.fail(1,"device event overflow");
    }
  }
  static void complete(usb_transfer_t*t){
    auto&self=*static_cast<UsbHost*>(t->context);self.inflight_=false;
    if(self.gone_)return;
    if(t->status!=USB_TRANSFER_STATUS_COMPLETED){self.fail(2,"input transfer");return;}
    State state{};const auto result=decodeF310(t->data_buffer,t->actual_num_bytes,state);
    if(result==UsbReport::invalid){
      ++self.diag_.malformed;self.retainAnomaly(t,1);
      self.fail(3,"malformed input report");return;
    }
    if(result==UsbReport::ignored){++self.diag_.ignored;return;}
    if(f310DpadConflict(t->data_buffer[2])){
      ++self.diag_.dpad_conflicts;self.retainAnomaly(t,2);
    }
    ++self.diag_.reports;self.diag_.last_report_ms=esp_timer_get_time()/1000;self.diag_.valid=true;
    if(self.diag_.reports==1){
      printf("USB F310 FIRST REPORT bytes=%d data=",t->actual_num_bytes);
      for(int i=0;i<t->actual_num_bytes;++i)printf("%02x",t->data_buffer[i]);
      printf("\n");
    }
    self.sink_(self.context_,4,&state);
  }
  void retainAnomaly(const usb_transfer_t*t,unsigned kind){
    // Retain one bounded raw report for HTTP diagnosis, without logging each
    // contact transition or adding bytes to the EMOS controller carrier.
    diag_.anomaly_kind=kind;diag_.anomaly_bytes=t->actual_num_bytes;
    const auto n=std::size_t(t->actual_num_bytes)<64?std::size_t(t->actual_num_bytes):64;
    for(std::size_t i=0;i<n;++i)snprintf(diag_.anomaly_hex+i*2,3,"%02x",t->data_buffer[i]);
    diag_.anomaly_hex[n*2]=0;
  }
  void fail(unsigned code,const char*where){
    if(!diag_.fault)printf("USB F310 FAIL %s code=%u\n",where,code);
    diag_.fault=code;diag_.valid=false;sink_(context_,2,nullptr);
  }
  bool ok(esp_err_t value,const char*where){
    if(value==ESP_OK)return true;
    printf("USB F310 ERROR %s: %s\n",where,esp_err_to_name(value));return false;
  }
  void inspect(unsigned address){
    usb_device_handle_t dev{};
    if(device_&&address==diag_.address)return;
    if(!ok(usb_host_device_open(client_,address,&dev),"device open"))return;
    const usb_device_desc_t*d{};const usb_config_desc_t*c{};usb_device_info_t info{};
    if(!ok(usb_host_get_device_descriptor(dev,&d),"device descriptor")||
       !ok(usb_host_get_active_config_descriptor(dev,&c),"configuration descriptor")||
       !ok(usb_host_device_info(dev,&info),"device info")){
      usb_host_device_close(client_,dev);return;
    }
    printf("USB DEVICE address=%u vid=%04x pid=%04x speed=%u config_bytes=%u interfaces=%u\n",
      address,d->idVendor,d->idProduct,unsigned(info.speed),c->wTotalLength,c->bNumInterfaces);
    if(d->idVendor!=0x046d||(d->idProduct!=0xc21d&&d->idProduct!=0xc216)||device_){
      usb_host_device_close(client_,dev);return;
    }
    const auto*bytes=reinterpret_cast<const std::uint8_t*>(c);
    printf("USB F310 CONFIG data=");
    for(unsigned i=0;i<c->wTotalLength;++i)printf("%02x",bytes[i]);
    printf("\n");
    F310Interface selected{};
    if(d->idProduct!=0xc21d||!f310Interface(bytes,c->wTotalLength,selected)){
      printf("USB F310 UNSUPPORTED: requires XInput interface ff/5d/01\n");
      usb_host_device_close(client_,dev);return;
    }
    if(!ok(usb_host_interface_claim(client_,dev,selected.number,0),"interface claim")){
      usb_host_device_close(client_,dev);return;
    }
    usb_transfer_t*transfer{};
    if(!ok(usb_host_transfer_alloc(selected.packet,0,&transfer),"input allocation")){
      usb_host_interface_release(client_,dev,selected.number);usb_host_device_close(client_,dev);return;
    }
    device_=dev;transfer_=transfer;gone_=false;inflight_=false;
    diag_={};diag_.running=diag_.attached=true;
    diag_.address=address;diag_.vid=d->idVendor;diag_.pid=d->idProduct;diag_.speed=unsigned(info.speed);
    diag_.interface=selected.number;diag_.endpoint=selected.endpoint;
    diag_.packet=selected.packet;diag_.interval=selected.interval;
    transfer_->device_handle=device_;transfer_->bEndpointAddress=selected.endpoint;
    transfer_->callback=complete;transfer_->context=this;transfer_->num_bytes=selected.packet;
    sink_(context_,0,nullptr);
    printf("USB F310 READY interface=%u endpoint=%02x packet=%u interval=%u\n",
      selected.number,selected.endpoint,selected.packet,selected.interval);
  }
  void remove(){
    if(!device_)return;
    // Flush outstanding transfers, then let handle_events deliver their
    // callbacks before releasing the claimed interface/transfer storage.
    if(inflight_){
      if(!flushing_){
        usb_host_endpoint_halt(device_,diag_.endpoint);
        usb_host_endpoint_flush(device_,diag_.endpoint);flushing_=true;
      }
      return;
    }
    sink_(context_,1,nullptr);diag_.attached=diag_.valid=false;
    if(!ok(usb_host_interface_release(client_,device_,diag_.interface),"interface release"))return;
    usb_host_transfer_free(transfer_);transfer_=nullptr;
    if(!ok(usb_host_device_close(client_,device_),"device close"))return;
    device_=nullptr;gone_=flushing_=false;diag_.address=0;
    printf("USB F310 DISCONNECTED: controller invalidated\n");
  }
  void run(){
    usb_host_client_config_t config{};config.max_num_event_msg=8;
    config.async.client_event_callback=event;config.async.callback_arg=this;
    if(!ok(usb_host_client_register(&config,&client_),"client register")){
      fail(4,"client register");vTaskDelete(nullptr);return;
    }
    diag_.running=true;
    // Registration does not replay NEW_DEV in pinned IDF. Inspect cached
    // addresses too, so hotplug before DHCP/HTTP startup is supported.
    std::uint8_t addresses[8]{};int count{};
    if(ok(usb_host_device_addr_list_fill(8,addresses,&count),"existing devices"))
      for(int i=0;i<count;++i)inspect(addresses[i]);
    for(;;){
      const auto result=usb_host_client_handle_events(client_,0);
      if(result!=ESP_OK&&result!=ESP_ERR_TIMEOUT)fail(5,"client events");
      if(gone_)remove();
      while(pending_count_&&(!gone_||!device_)){
        const auto address=pending_[--pending_count_];inspect(address);
      }
      if(device_&&!gone_&&!diag_.fault&&!inflight_){
        transfer_->num_bytes=diag_.packet;
        if(ok(usb_host_transfer_submit(transfer_),"input submit"))inflight_=true;
        else fail(6,"input submit");
      }
      // XInput may report only changes. A live USB task/claimed device keeps
      // the last state, as a keyboard does; last_report_ms remains separate.
      // Stopping this task stops renewal and Receiver expires within250ms.
      if(device_&&!gone_&&!diag_.fault&&diag_.valid)sink_(context_,3,nullptr);
      // Publish diagnostics through the same sink's separate retained copy.
      if(publish_)publish_(&diag_,context_);
      const auto ticks=pdMS_TO_TICKS(8);vTaskDelay(ticks?ticks:1);
    }
  }
 public:
  using Publish=void(*)(const UsbDiagnostics*,void*);
  void diagnostics(Publish callback){publish_=callback;}
 private:
  Sink sink_{};Publish publish_{};void*context_{};
  std::atomic<bool>started_{};UsbDiagnostics diag_{};
  usb_host_client_handle_t client_{};usb_device_handle_t device_{};usb_transfer_t*transfer_{};
  unsigned pending_count_{};std::uint8_t pending_[8]{};
  bool gone_{},inflight_{},flushing_{};
};
}
