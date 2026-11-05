// NET-003: Ethernet lifecycle owns start/stop; this worker alone owns TCP/Peer.
// Console copies bounded mailboxes under a short lock, never waits on socket IO.
#pragma once
#include "api.hpp"
#include "peer.hpp"
#include "mailbox.hpp"
#include <atomic>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_timer.h>
namespace agon::extender::network::messages {
class Runtime {
    portMUX_TYPE mutex_=portMUX_INITIALIZER_UNLOCKED;
    Mailbox mailbox_;
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
            const bool close=mailbox_.takeCloseRequest();
            mailbox_.beginWork(command,n,generation);
            portEXIT_CRITICAL(&mutex_);
            if(close){
                peer_.stop(socket);
                portENTER_CRITICAL(&mutex_);mailbox_.completeClose();portEXIT_CRITICAL(&mutex_);
            }
            if(n){
                const auto length=peer_.request(command,n,reply,socket,now(),!lost_.load());
                portENTER_CRITICAL(&mutex_);
                mailbox_.completeWork(generation,reply,length);
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
        mailbox_.workerStopped();
        portEXIT_CRITICAL(&mutex_);
    }
    bool submit(const uint8_t*p,unsigned n) noexcept {
        if(!p||n<AGON_NET_HEADER||n>AGON_NET_BODY||!worker_.load()||stopping_.load())return false;
        portENTER_CRITICAL(&mutex_);
        const bool accept=mailbox_.submitUart(p,n);
        portEXIT_CRITICAL(&mutex_);return accept;
    }
    unsigned take(uint8_t*out) noexcept {
        portENTER_CRITICAL(&mutex_);
        const auto n=mailbox_.takeUart(out);
        portEXIT_CRITICAL(&mutex_);return n;
    }
    // Console-owner-only netp hooks. These do not acquire pads or select a
    // display route. A physical coordinator must own the epoch around offers.
    MailboxResult openParallel(uint32_t&token) noexcept {
        token=0;if(!worker_.load()||stopping_.load())return MailboxResult::fault;
        portENTER_CRITICAL(&mutex_);const auto r=mailbox_.openParallel(token);
        portEXIT_CRITICAL(&mutex_);return r;
    }
    MailboxResult submitParallel(uint32_t token,const uint8_t*p,unsigned n) noexcept {
        if(!worker_.load()||stopping_.load())return MailboxResult::fault;
        portENTER_CRITICAL(&mutex_);const auto r=mailbox_.submitParallel(token,p,n);
        portEXIT_CRITICAL(&mutex_);return r;
    }
    MailboxResult canSubmitParallel(uint32_t token) noexcept {
        portENTER_CRITICAL(&mutex_);const auto r=mailbox_.canSubmitParallel(token);
        portEXIT_CRITICAL(&mutex_);return r;
    }
    MailboxResult offerParallel(uint32_t token,unsigned capacity,const uint8_t*&p,unsigned&n) noexcept {
        portENTER_CRITICAL(&mutex_);const auto r=mailbox_.offerParallel(token,capacity,p,n);
        portEXIT_CRITICAL(&mutex_);return r;
    }
    MailboxResult finishParallel(uint32_t token,bool complete,bool padsReleased) noexcept {
        portENTER_CRITICAL(&mutex_);const auto r=mailbox_.finishParallel(token,complete,padsReleased);
        portEXIT_CRITICAL(&mutex_);return r;
    }
    MailboxResult releaseParallel(uint32_t token) noexcept {
        portENTER_CRITICAL(&mutex_);
        if(!worker_.load())mailbox_.completeStoppedClose();
        const auto r=mailbox_.releaseParallel(token);
        portEXIT_CRITICAL(&mutex_);return r;
    }
};
inline Runtime runtime;
} // namespace agon::extender::network::messages
