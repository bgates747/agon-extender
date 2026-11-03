#include "p4_upload_coordinator.hpp"
#include <driver/gpio.h>
namespace agon::extender::transport {
using H=P4ParallelHandover;using U=P4ParallelUpload;using M=P4UploadMailbox;
bool P4UploadCoordinator::releasePads() noexcept {
  bool okay=true;
  for(int p:data_){
    const auto pin=gpio_num_t(p);
    if(gpio_reset_pin(pin)!=ESP_OK)okay=false;
    if(gpio_set_direction(pin,GPIO_MODE_INPUT)!=ESP_OK)okay=false;
    if(gpio_pullup_dis(pin)!=ESP_OK)okay=false;
    if(gpio_pulldown_dis(pin)!=ESP_OK)okay=false;
  }
  return okay;
}
P4UploadCoordinator::Result P4UploadCoordinator::fence() noexcept {
  handover_.cancel();fenced_=true;
  if(payload_ && payload_->cancel()==U::Result::cleanupFault){
    uploadMailbox.state.store(M::cleanupFault,std::memory_order_release);
    return Result::cleanupFault;
  }
  // Existing boot owner may perform reciprocal recovery only after this
  // native leaf really stopped/released. Never manufacture a UART grant.
  physical_=false;payload_.reset();parking_.reset();
  uploadMailbox.outcome.store(unsigned(U::Result::fault));
  uploadMailbox.state.store(M::refused,std::memory_order_release);
  return Result::recovery;
}
P4UploadCoordinator::Result P4UploadCoordinator::poll(std::uint32_t now,
    bool boundary,bool empty) noexcept {
  if(xPortGetCoreID()!=core_)return Result::exclusive;
  auto &m=uploadMailbox;auto state=m.status();auto &h=handover_;
  if(state==M::cleanupFault)return Result::cleanupFault;
  if(!physical_){
    // The worker cannot destroy source storage while the console owns a DMA
    // unit. Even a refused request retires through this same console owner.
    if(m.cancel.load(std::memory_order_acquire) && state!=M::free && state!=M::loading){
      if(payload_ && payload_->cancel()==U::Result::cleanupFault){
        m.state.store(M::cleanupFault,std::memory_order_release);return Result::cleanupFault;
      }
      payload_.reset();parking_.reset();
      if(!m.source.release()){m.state.store(M::cleanupFault,std::memory_order_release);return Result::cleanupFault;}
      m.state.store(M::free,std::memory_order_release);return Result::uart;
    }
    if(state==M::queued){
      // Reserve descriptors without changing shared data outputs. No offer is
      // sent until the worker observes this actual prepared result.
      // Recovery leaves failed=true as historical payload outcome. Only the
      // recovered UART phase admits preparation; begin() below clears that
      // history, exactly as the existing P4 handover admit() already does.
      if(h.phase()!=H::uart)return Result::uart;
      payload_.emplace(data_,clock_,valid_,ready_,core_);
      auto r=payload_->prepare(m.source);
      m.outcome.store(unsigned(r));
      m.state.store(r==U::Result::prepared?M::prepared:
          r==U::Result::cleanupFault?M::cleanupFault:M::refused,std::memory_order_release);
      return r==U::Result::cleanupFault?Result::cleanupFault:Result::uart;
    }
    if(state!=M::offered)return Result::uart;
    // Initial C0/V0 is emitted by EMOS only AFTER it validates the file request,
    // reserves its serializer, drains UART and releases all eight data pads.
    // Until then normal UART decoding continues, so explicit refusal can arrive.
    if(gpio_get_level(gpio_num_t(clock_)) || gpio_get_level(gpio_num_t(valid_)))return Result::uart;
    // A held peer release request immediately fences NEW UART producers.
    // The drain phase below still requires actual boundary/empty before park;
    // returning uart here would keep pumping keys into an already parked peer.
    if(!admit_ || !admit_(now,m.job,std::uint32_t(m.source.size())) || !h.begin())return fence();
    parking_.emplace(tx_,rx_,rts_,cts_,core_);
    physical_=true;parked_=released_=restored_=fenced_=false;
    phase_=h.phase();phaseAt_=now;m.state.store(M::active,std::memory_order_release);
  }
  if(fenced_)return fence();
  if(h.failed())return fence();
  // Only the payload phase includes SD-write pauses. Handover phases retain
  // their short bounded deadline; late phase changes cannot renew an old one.
  if(std::uint32_t(now-phaseAt_)>=(phase_==H::block?600000U:2000U))return fence();
  if(h.phase()!=phase_){phase_=h.phase();phaseAt_=now;}
  std::uint8_t done=0;
  const bool valid=gpio_get_level(gpio_num_t(valid_));
  const bool clock=gpio_get_level(gpio_num_t(clock_));
  if(valid)done|=H::validHigh;
  if(clock)done|=H::clockHigh;
  if(h.phase()==H::drain){
    if(!boundary || !empty || valid || clock)return Result::drain;
    auto r=parking_->park(boundary,true);
    if(r==P4UartParking::Result::fault)return fence();
    if(r!=P4UartParking::Result::ready)return Result::drain;
    parked_=true;done|=H::quiet;
  }
  if(h.phase()==H::entryRelease){
    if(!parked_ || !releasePads())return fence();
    released_=true;done|=H::released;
  }
  if(h.phase()==H::localArm){
    if(payload_->result()==U::Result::prepared &&
        payload_->arm(parked_,m.source.size(),now,600000)!=U::Result::pending)return fence();
    done|=H::armed;released_=false;
  }
  if(h.phase()==H::block){
    auto r=m.cancel.load(std::memory_order_acquire)?payload_->cancel():payload_->poll(now);
    if(r==U::Result::cleanupFault)return fence();
    if(r!=U::Result::pending){
      // A known short/error file is still allowed the reciprocal UART return.
      // The worker separately checks physical outcome and the SD terminal reply.
      m.outcome.store(unsigned(r));released_=true;done|=H::done;
    }
  }
  if(h.phase()==H::recoveryUart){
    if(!released_ || clock || !valid)return fence();
    if(!restored_){
      if(parking_->restore(released_,true)!=P4UartParking::Result::ready)return fence();
      restored_=true;
    }
    done|=H::uartUp;
  }
  h.step(done);
  if(h.failed())return fence();
  if(gpio_set_level(gpio_num_t(ready_),h.readyN())!=ESP_OK)return fence();
  if(h.phase()==H::uart){
    if(!restored_)return fence();
    physical_=false;m.state.store(M::returned,std::memory_order_release);
    return Result::uart;
  }
  return h.phase()==H::drain?Result::drain:Result::exclusive;
}
}
