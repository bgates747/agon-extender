// Private PORT-008 hardware edge proof for the pinned IDF 5.5.5/P4 composition.
// Capture begins with VALID high while READY is withheld. Count both edge
// polarities in hardware; freeze only after exact TX completion, then require
// count=2 and VALID high again. beginClock instead counts falling CLOCK edges
// only while VALID is low, requiring exactly1..4096 at VALID-high closure.
// RX freezes CLOCK first while its separate VALID counter still runs, then
// freezes VALID; a later qualified CLOCK needs another VALID pulse to be caught.
// The proof covers edges through each counter stop, not unbounded future edges.
//
// A raw 16-bit counter can wrap back to2. Use the driver's 32-bit accumulator
// and explicit 32767 high-limit watchpoint: pulse_cnt.c504-540 compensates a
// pending overflow before its ISR runs. A 32767 limit keeps raw 2 inside that
// compensation window; a tiny limit such as 3 does not. The native caller MUST
// check its <=2000ms deadline before polling: pinned P4 APB 90 MHz bounds the
// accepted window below 180 million sampled edges, below signed 32-bit overflow.
#pragma once
#include <cstddef>
#include <driver/gpio.h>
#include <driver/pulse_cnt.h>
#include <freertos/FreeRTOS.h>
namespace agon::extender::transport {
class P4ValidCounter final {
 public:
  struct Proof { bool failed,started,ended; };
  P4ValidCounter(int pin,int core) noexcept:pin_(pin),core_(core) {}
  P4ValidCounter(P4ValidCounter const&)=delete;
  P4ValidCounter& operator=(P4ValidCounter const&)=delete;
  bool begin() noexcept {return beginCounter(pin_,false,2);}
  bool beginClock(int clock,std::size_t expected) noexcept {
    // A distinct CLOCK and admitted byte bound are required before mutation.
    if(clock<0 || clock==pin_ || !expected || expected>4096)return false;
    return beginCounter(clock,true,expected);
  }
  Proof sample(bool exactDmaComplete) noexcept {
    if(xPortGetCoreID()!=core_ || failed_ || !unit_)return {true,false,false};
    if(frozen_)return {false,true,true};
    int count=-1;
    if(pcnt_unit_get_count(unit_,&count)!=ESP_OK || count<0 || count>targetCount_){fail();return {true,false,false};}
    if(count<targetCount_ || !exactDmaComplete)return {false,count!=0,false};
    if(!gpio_get_level(gpio_num_t(pin_))) {
      // Exact CLOCK length is often reached before EMOS releases VALID.
      if(gated_)return {false,true,false};
      fail();return {true,true,false};
    }
    if(pcnt_unit_stop(unit_)!=ESP_OK){fail();return {true,true,false};}
    started_=false;
    // Freeze before the final read so a late extra edge cannot race acceptance.
    if(pcnt_unit_get_count(unit_,&count)!=ESP_OK || count!=targetCount_ || !gpio_get_level(gpio_num_t(pin_))) {
      fail();return {true,true,false};
    }
    frozen_=true;return {false,true,true};
  }
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
  // Private failure receipt only; never substitutes for sample/freeze proof.
  int diagnosticCount() noexcept {
    int count=-1;
    return unit_ && enabled_ && pcnt_unit_get_count(unit_,&count)==ESP_OK?count:-1;
  }
#endif
  bool cleanup() noexcept {
    if(xPortGetCoreID()!=core_ || deleteFailed_)return false;
    bool okay=true;
    if(started_) {if(pcnt_unit_stop(unit_)==ESP_OK)started_=false;else okay=false;}
    if(!started_ && enabled_) {if(pcnt_unit_disable(unit_)==ESP_OK)enabled_=false;else okay=false;}
    if(!enabled_ && channel_) {if(pcnt_del_channel(channel_)==ESP_OK)channel_=nullptr;else okay=false;}
    if(!channel_ && unit_) {
      if(pcnt_del_unit(unit_)==ESP_OK)unit_=nullptr;
      else {
        // IDF 5.5.5 pcnt_destroy deletes its PM lock before esp_intr_free but
        // does not null that handle on a later failure. Retain this owner and
        // DMA; retrying deletion could double-delete a partial SDK resource.
        deleteFailed_=true;okay=false;
      }
    }
    return okay && !unit_ && !channel_ && !enabled_ && !started_;
  }
 private:
  bool beginCounter(int edgePin,bool gated,std::size_t target) noexcept {
    if(xPortGetCoreID()!=core_ || unit_ || failed_ || !gpio_get_level(gpio_num_t(pin_)))return false;
    gated_=gated;targetCount_=static_cast<int>(target);
    pcnt_unit_config_t config{};config.low_limit=-32768;config.high_limit=32767;
    config.flags.accum_count=true;
    if(pcnt_new_unit(&config,&unit_)!=ESP_OK)return fail();
    pcnt_chan_config_t channel{};channel.edge_gpio_num=edgePin;channel.level_gpio_num=gated?pin_:-1;
    if(pcnt_new_channel(unit_,&channel,&channel_)!=ESP_OK)return fail();
    // IDF enables pulls on both edge and control GPIOs. Restore the external
    // bias contract for CLOCK and VALID immediately; input matrix fanout keeps
    // the separate PARLIO and VALID-counter input routes intact.
    if(gpio_pullup_dis(gpio_num_t(edgePin))!=ESP_OK || gpio_pulldown_dis(gpio_num_t(edgePin))!=ESP_OK ||
       (gated && (gpio_pullup_dis(gpio_num_t(pin_))!=ESP_OK || gpio_pulldown_dis(gpio_num_t(pin_))!=ESP_OK)) ||
       pcnt_channel_set_edge_action(channel_,gated?PCNT_CHANNEL_EDGE_ACTION_HOLD:PCNT_CHANNEL_EDGE_ACTION_INCREASE,PCNT_CHANNEL_EDGE_ACTION_INCREASE)!=ESP_OK ||
       pcnt_channel_set_level_action(channel_,gated?PCNT_CHANNEL_LEVEL_ACTION_HOLD:PCNT_CHANNEL_LEVEL_ACTION_KEEP,PCNT_CHANNEL_LEVEL_ACTION_KEEP)!=ESP_OK ||
       pcnt_unit_add_watch_point(unit_,32767)!=ESP_OK)return fail();
    if(pcnt_unit_enable(unit_)!=ESP_OK)return fail();
    enabled_=true;
    // Watchpoints take effect after clear. Counter is still stopped, and EMOS
    // cannot start its record until the native owner subsequently lowers READY.
    if(pcnt_unit_clear_count(unit_)!=ESP_OK || !gpio_get_level(gpio_num_t(pin_)) ||
       pcnt_unit_start(unit_)!=ESP_OK)return fail();
    started_=true;
    int count=-1;
    if(pcnt_unit_get_count(unit_,&count)!=ESP_OK || count || !gpio_get_level(gpio_num_t(pin_)))return fail();
    return true;
  }
  bool fail() noexcept {failed_=true;return false;}
  int pin_,core_,targetCount_{2};
  pcnt_unit_handle_t unit_{};
  pcnt_channel_handle_t channel_{};
  bool enabled_{},started_{},frozen_{},failed_{},deleteFailed_{},gated_{};
};
}
