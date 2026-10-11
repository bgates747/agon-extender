#include "p4_block_coordinator.hpp"
#include <driver/gpio.h>
#include <cstdio>
namespace agon::extender::transport {
using H=P4ParallelHandover;
using N=P4NativePayload;
bool P4BlockCoordinator::releasePads() noexcept {
  bool okay=true;
  for(int pin:data_) {
    if(gpio_set_direction(gpio_num_t(pin),GPIO_MODE_INPUT)!=ESP_OK)okay=false;
    if(gpio_reset_pin(gpio_num_t(pin))!=ESP_OK)okay=false;
    if(gpio_pullup_dis(gpio_num_t(pin))!=ESP_OK)okay=false;
    if(gpio_pulldown_dis(gpio_num_t(pin))!=ESP_OK)okay=false;
  }
  return okay;
}
P4BlockCoordinator::Result P4BlockCoordinator::fail(const char *why) noexcept {
  // Always retain the first failure after the payload owner has refused work.
  // This USB-only error has no per-byte cost and is not qualification tracing.
  if(!recovering_)printf("Parallel failure stage=%s phase=%u pending=%u session=%u native=%u\n",why,unsigned(control_.handover.phase()),control_.pending(),unsigned(control_.session.phase),payload_?unsigned(payload_->result()):255u);
  // Retain the native object, DMA and callback context until its real cleanup
  // succeeds. Boot recovery must not replace this with optimistic GPIO reset.
  control_.cancel();recovering_=true;
  if(payload_ && payload_->cancel()==N::Result::cleanupFault)return Result::cleanupFault;
  payload_.reset();active_=false;
  return Result::recovery;
}
void P4BlockCoordinator::recovered() noexcept {
  if(!recovering_ || xPortGetCoreID()!=core_ || active_ || payload_ ||
     control_.handover.phase()!=H::uart)return;
  parking_.emplace(tx_,rx_,rts_,cts_,core_);
  parked_=released_=restored_=recovering_=false;
}
P4BlockCoordinator::Result P4BlockCoordinator::poll(std::uint32_t now,
    bool boundary,bool empty) noexcept {
  if(xPortGetCoreID()!=core_)return Result::exclusive;
  auto &h=control_.handover;
  if(recovering_)return payload_?fail():Result::recovery;
  control_.expire(now);
  if(!active_) {
    if(!control_.pending() || h.phase()!=H::drain)
      return h.phase()==H::uart?Result::uart:Result::recovery;
    active_=true;parked_=released_=restored_=false;
    // Prior object reached complete and was retired only after clean return.
    payload_.emplace(data_,clock_,valid_,ready_,core_);
  }
  if(!control_.pending() || h.failed())return fail("control expired/cancelled");
  std::uint8_t done=0;
  const bool valid=gpio_get_level(gpio_num_t(valid_));
  const bool clock=gpio_get_level(gpio_num_t(clock_));
  if(valid)done|=H::validHigh;
  if(clock)done|=H::clockHigh;
  if(h.phase()==H::drain) {
    // C=0,V=0 is EMOS's held release request, emitted AFTER its TEMT/packet
    // boundary and all-eight-pad release. An ACK alone is never peer quiet.
    if(!boundary || !empty || valid || clock)return Result::drain;
    const auto parked=parking_->park(boundary,true);
    if(parked==P4UartParking::Result::fault)return fail("UART park");
    if(parked!=P4UartParking::Result::ready)return Result::drain;
    parked_=true;done|=H::quiet;
  }
  if(h.phase()==H::entryRelease) {
    if(!parked_ || !releasePads())return fail("entry release");
    released_=true;done|=H::released;
  }
  if(h.phase()==H::localArm) {
    if(payload_->result()==N::Result::idle) {
      const auto *d=control_.descriptor();
      std::uint8_t *buffer;std::size_t capacity;
      if(!d || !control_.payloadBuffer(buffer,capacity))return fail("payload buffer");
      const auto length=std::size_t(d[10])|(std::size_t(d[11])<<8);
      if(payload_->arm(h,parked_,d[12]==1,buffer,capacity,length,now,2000)!=N::Result::pending)
        return fail("native arm");
    }
    done|=H::armed;released_=false;
  }
  if(h.phase()==H::block) {
    const auto r=payload_->poll(now);
    if(r==N::Result::complete){released_=true;done|=H::done;}
    else if(r!=N::Result::pending)return fail("native completion");
  }
  if(h.phase()==H::recoveryUart) {
    // This phase follows EMOS's fresh C=0,V=0 request and C=0,V=1 UART-up
    // acknowledgement, observed by the SAME handover after native pad release.
    if(!released_ || clock || !valid)return fail("UART return levels");
    if(!restored_) {
      if(parking_->restore(released_,true)!=P4UartParking::Result::ready)return fail("UART restore");
      restored_=true;
    }
    done|=H::uartUp;
  }
  h.step(done);
  if(h.failed())return fail("handover step");
  if(gpio_set_level(gpio_num_t(ready_),h.readyN())!=ESP_OK)return fail("READY output");
  if(h.phase()==H::uart) {
    if(!restored_ || !control_.payloadReturned(0,now))return fail("payload returned");
    payload_.reset();active_=false;
    return Result::uart;
  }
  return h.phase()==H::drain?Result::drain:Result::exclusive;
}
}
