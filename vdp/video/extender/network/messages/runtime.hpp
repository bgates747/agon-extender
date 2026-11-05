// NET-003: Ethernet lifecycle owns start/stop; this worker alone owns TCP/Peer.
// Console copies bounded mailboxes under a short lock, never waits on socket IO.
#pragma once
#include "api.hpp"
#include "peer.hpp"
#include <atomic>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_timer.h>
namespace agon::extender::network::messages {
class Runtime {
    portMUX_TYPE mutex_=portMUX_INITIALIZER_UNLOCKED;
    uint8_t command_[AGON_NET_BODY]{},reply_[AGON_NET_BODY]{};
    unsigned commandLength_{},replyLength_{};
    uint32_t generation_{};
    bool processing_{};
    std::atomic<bool> stopping_{false},lost_{true};
    std::atomic<TaskHandle_t> worker_{nullptr};
    Peer peer_;
    static uint32_t now(){return uint32_t(esp_timer_get_time()/1000);}
    static void entry(void*p){static_cast<Runtime*>(p)->run();}
    void run(){
        TcpClient socket;
        while(!stopping_.load()){
            uint8_t command[AGON_NET_BODY],reply[AGON_NET_BODY];unsigned n;uint32_t generation;
            portENTER_CRITICAL(&mutex_);
            n=commandLength_;generation=generation_;
            if(n){std::memcpy(command,command_,n);commandLength_=0;processing_=true;}
            portEXIT_CRITICAL(&mutex_);
            if(n){
                const auto length=peer_.request(command,n,reply,socket,now(),!lost_.load());
                portENTER_CRITICAL(&mutex_);
                if(generation==generation_){
                    if(length)std::memcpy(reply_,reply,length);
                    replyLength_=length;processing_=false;
                }
                portEXIT_CRITICAL(&mutex_);
            }
            peer_.tick(socket,now(),!lost_.load());
            const auto ticks=pdMS_TO_TICKS(2);vTaskDelay(ticks?ticks:1);
        }
        peer_.stop(socket);worker_.store(nullptr);vTaskDelete(nullptr);
    }
public:
    bool start(){
        if(worker_.load())return !stopping_.load();
        stopping_=false;lost_=false;TaskHandle_t task=nullptr;
        if(xTaskCreate(entry,"net-messages",4096,this,4,&task)!=pdPASS){lost_=true;return false;}
        worker_=task;return true;
    }
    void linkLost(){lost_=true;}
    void stop(){
        lost_=true;stopping_=true;
        while(worker_.load())vTaskDelay(1);
        portENTER_CRITICAL(&mutex_);
        commandLength_=replyLength_=0;processing_=false;++generation_;
        portEXIT_CRITICAL(&mutex_);
    }
    bool submit(const uint8_t*p,unsigned n) noexcept {
        if(!p||n<AGON_NET_HEADER||n>AGON_NET_BODY||!worker_.load()||stopping_.load())return false;
        portENTER_CRITICAL(&mutex_);
        // Explicit CONNECT supersedes prior local completion. Generation binds
        // publication so an old worker result cannot overwrite the new reply.
        const bool replace=p[3]==AGON_NET_CONNECT;
        const bool accept=replace||(!commandLength_&&!replyLength_&&!processing_);
        if(accept){
            if(replace){++generation_;replyLength_=0;processing_=false;}
            std::memcpy(command_,p,n);commandLength_=n;
        }
        portEXIT_CRITICAL(&mutex_);return accept;
    }
    unsigned take(uint8_t*out) noexcept {
        portENTER_CRITICAL(&mutex_);
        const auto n=replyLength_;if(n)std::memcpy(out,reply_,n);replyLength_=0;
        portEXIT_CRITICAL(&mutex_);return n;
    }
};
inline Runtime runtime;
} // namespace agon::extender::network::messages
