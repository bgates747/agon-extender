#include "p4_parallel_upload.hpp"
#include <cstring>
#include <esp_heap_caps.h>
#include <esp_rom_gpio.h>
#include <esp_private/gpio.h>
#include <soc/parlio_periph.h>
#include <soc/io_mux_reg.h>

namespace agon::extender::transport {
bool P4UploadSource::load(FILE *spool,std::size_t length) noexcept {
  if(data_ || borrowed_ || !spool || !length || length>maximumBytes)return false;
  // IDF5.5.5 checks PSRAM address/bit-length alignment. Submit a padded DMA
  // cycle, but EMOS clocks only logical length bytes. Padding is never payload.
  // In particular, 1/65535/65537-byte files cannot use an unaligned DMA cycle.
  allocated_=(length+63U)&~std::size_t(63U);
  data_=static_cast<std::uint8_t*>(heap_caps_aligned_alloc(
      64,allocated_,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
  if(!data_){allocated_=0;return false;}
  if(std::fread(data_,1,length,spool)!=length || std::fgetc(spool)!=EOF ||
      std::ferror(spool)){release();return false;}
  std::memset(data_+length,0,allocated_-length);
  length_=length;return true;
}
bool P4UploadSource::release() noexcept {
  if(borrowed_)return false;
  if(data_)heap_caps_free(data_);
  data_=nullptr;length_=allocated_=0;return true;
}
P4ParallelUpload::Result P4ParallelUpload::prepare(P4UploadSource &s) noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if(result_!=Result::idle || !s.data_ || !s.length_ || s.borrowed_ ||
      s.length_>P4UploadSource::maximumBytes)return Result::rejected;
  source_=&s;s.borrowed_=true;result_=Result::prepared;
  parlio_tx_unit_config_t config{};
  for(auto &p:config.data_gpio_nums)p=GPIO_NUM_NC;
  config.clk_src=PARLIO_CLK_SRC_EXTERNAL;
  config.clk_in_gpio_num=gpio_num_t(clock_);
  config.clk_out_gpio_num=config.valid_gpio_num=GPIO_NUM_NC;
  config.input_clk_src_freq_hz=config.output_clk_freq_hz=10000000;
  config.data_width=8;config.trans_queue_depth=1;
  config.max_transfer_size=s.allocated_;
  config.shift_edge=PARLIO_SHIFT_EDGE_NEG;
  config.bit_pack_order=PARLIO_BIT_PACK_ORDER_LSB;
  if(parlio_new_tx_unit(&config,&tx_)!=ESP_OK)return finish(Result::fault);
  return result_;
}
P4ParallelUpload::Result P4ParallelUpload::arm(bool parked,
    std::size_t admittedLength,std::uint32_t now,std::uint32_t timeoutMs) noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if(result_!=Result::prepared || !parked || admittedLength!=source_->length_ ||
      !timeoutMs || timeoutMs>600000 || !gpio_get_level(gpio_num_t(clock_)) ||
      !gpio_get_level(gpio_num_t(valid_)))return Result::rejected;
  began_=now;timeout_=timeoutMs;admitted_=true;result_=Result::pending;
  if(gpio_set_level(gpio_num_t(ready_),1)!=ESP_OK)return finish(Result::fault);
  // The sole P4 TX unit was reserved with NC data pins before admission.
  // Attach it only after the coordinator's actual UART park completes.
  static_assert(SOC_PARLIO_GROUPS==1 && SOC_PARLIO_TX_UNITS_PER_GROUP==1,
                "P4-only upload TX matrix");
  const auto &g=parlio_periph_signals.groups[0];
  padsTouched_=true;
  for(std::size_t i=0;i<pins_.size();++i){
    if(gpio_func_sel(gpio_num_t(pins_[i]),PIN_FUNC_GPIO)!=ESP_OK)return finish(Result::fault);
    esp_rom_gpio_connect_out_signal(pins_[i],g.tx_units[0].data_sigs[i],false,false);
  }
  gpio_pin_glitch_filter_config_t filter{};
  filter.gpio_num=gpio_num_t(clock_);filter.clk_src=GLITCH_FILTER_CLK_SRC_DEFAULT;
  if(gpio_new_pin_glitch_filter(&filter,&filter_)!=ESP_OK ||
      gpio_glitch_filter_enable(filter_)!=ESP_OK)return finish(Result::fault);
  filterEnabled_=true;
  // Consumer repair r01: sustained uploads observed extra VALID edges while
  // the received prefix stayed exact. CLOCK was filtered, VALID was not.
  // Apply IDF5.5.5's same two-IO_MUX-cycle hardware filter to VALID before
  // either PCNT route is started. This rejects only sub-two-cycle pulses;
  // real premature closures/extra VALID intervals still fail exact proof.
  // This is a bounded electrical-noise experiment, not proof of its origin.
  filter.gpio_num=gpio_num_t(valid_);
  if(gpio_new_pin_glitch_filter(&filter,&validFilter_)!=ESP_OK ||
      gpio_glitch_filter_enable(validFilter_)!=ESP_OK)return finish(Result::fault);
  validFilterEnabled_=true;
  clocks_.emplace(valid_,core_);validEdges_.emplace(valid_,core_);
  if(!clocks_->beginUploadClock(clock_,source_->length_) ||
      !validEdges_->begin())return finish(Result::fault);
  if(parlio_tx_unit_enable(tx_)!=ESP_OK)return finish(Result::fault);
  enabled_=true;
  parlio_transmit_config_t transfer{};
  transfer.flags.loop_transmission=true;transfer.flags.queue_nonblocking=true;
  transfer.idle_value=source_->data_[source_->length_-1];
  // Loop mode bypasses P4's 0x7FFFF-bit non-loop frame limit. It deliberately
  // has NO on_trans_done callback. CLOCK/VALID hardware proof ends this leaf.
  if(parlio_tx_unit_transmit(tx_,source_->data_,source_->allocated_*8,&transfer)!=ESP_OK ||
      gpio_set_level(gpio_num_t(ready_),0)!=ESP_OK)return finish(Result::fault);
  return result_;
}
P4ParallelUpload::Result P4ParallelUpload::poll(std::uint32_t now) noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if(result_!=Result::pending)return result_;
  if(std::uint32_t(now-began_)>=timeout_)return finish(Result::timeout);
  // Freeze CLOCK first while VALID's counter still observes a late new pulse.
  // Hardware counts bytes; there is no ISR or software round trip per byte.
  // RU05-F02: snapshot physical closure BEFORE either counter read. The last
  // CLOCK/VALID edges can occur between those reads. Passing true to both
  // unconditionally can call an ordinary in-flight final byte "short".
  // Defer both freezes to a poll that began with VALID high, retaining strict
  // CLOCK-first then VALID freeze and all extra-edge/short-count checks.
  const bool closed=gpio_get_level(gpio_num_t(valid_));
  const auto clock=clocks_->sample(closed);
  if(clock.failed)return finish(Result::fault);
  const auto valid=validEdges_->sample(closed);
  if(valid.failed)return finish(Result::fault);
  if(valid.ended && !clock.ended)return finish(Result::shortPayload);
  if(clock.ended && valid.ended)return finish(Result::complete);
  return result_;
}
bool P4ParallelUpload::stop() noexcept {
  bool okay=true;
  if(enabled_){
    if(parlio_tx_unit_disable(tx_)==ESP_OK)enabled_=false;else okay=false;
  }
  if(!enabled_ && tx_ && !deleteFailed_){
    if(parlio_del_tx_unit(tx_)==ESP_OK)tx_=nullptr;
    else {
      // Pinned IDF5.5.5 parlio_destroy_tx_unit frees the interrupt, PM lock,
      // channel and queues without clearing their pointers before later
      // fallible deletes. Retrying can double-free a partially destroyed unit.
      // Fence pads and retain source/owner until hardware reset, not retry.
      deleteFailed_=true;okay=false;
    }
  }
  if(clocks_){if(clocks_->cleanup())clocks_.reset();else okay=false;}
  if(validEdges_){if(validEdges_->cleanup())validEdges_.reset();else okay=false;}
  if(!enabled_ && filterEnabled_){
    if(gpio_glitch_filter_disable(filter_)==ESP_OK)filterEnabled_=false;else okay=false;
  }
  if(!enabled_ && !filterEnabled_ && filter_){
    if(gpio_del_glitch_filter(filter_)==ESP_OK)filter_=nullptr;else okay=false;
  }
  if(!enabled_ && validFilterEnabled_){
    if(gpio_glitch_filter_disable(validFilter_)==ESP_OK)validFilterEnabled_=false;else okay=false;
  }
  if(!enabled_ && !validFilterEnabled_ && validFilter_){
    if(gpio_del_glitch_filter(validFilter_)==ESP_OK)validFilter_=nullptr;else okay=false;
  }
  return okay && !enabled_ && !tx_ && !clocks_ && !validEdges_ && !filter_ && !validFilter_;
}
bool P4ParallelUpload::releasePads() noexcept {
  if(!padsTouched_)return true;
  bool okay=true;
  for(int p:pins_){
    const auto pin=gpio_num_t(p);
    if(gpio_reset_pin(pin)!=ESP_OK)okay=false;
    if(gpio_set_direction(pin,GPIO_MODE_INPUT)!=ESP_OK)okay=false;
    if(gpio_pullup_dis(pin)!=ESP_OK)okay=false;
    if(gpio_pulldown_dis(pin)!=ESP_OK)okay=false;
  }
  if(okay)padsTouched_=false;
  return okay;
}
P4ParallelUpload::Result P4ParallelUpload::finish(Result outcome) noexcept {
  if(clocks_)observedClocks_=clocks_->observedCount();
  if(validEdges_)observedValid_=validEdges_->observedCount();
  const bool stopped=stop(),released=releasePads();
  // Never advertise reusable pins or release borrowed PSRAM after any failed
  // DMA/counter/filter/pad cleanup. The owning coordinator must retain us.
  if(!stopped || !released ||
      (admitted_ && gpio_set_level(gpio_num_t(ready_),1)!=ESP_OK))
    return result_=Result::cleanupFault;
  if(source_){source_->borrowed_=false;source_=nullptr;}
  return result_=outcome;
}
P4ParallelUpload::Result P4ParallelUpload::cancel() noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if(result_==Result::idle)return result_;
  return finish(Result::fault);
}
}
