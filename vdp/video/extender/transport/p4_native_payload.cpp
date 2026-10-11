#include "p4_native_payload.hpp"
#include <cstring>
#include <driver/gpio.h>
#include <esp_heap_caps.h>
#include <freertos/FreeRTOS.h>
#include <cstdio>
#if defined(AGON_EXTENDER_EXEXT_STREAM)
#include <esp_rom_gpio.h>
#include <esp_private/gpio.h>
#include <soc/parlio_periph.h>
#include <soc/io_mux_reg.h>
#endif
namespace agon::extender::transport {
// EX05: game assets left internal DMA memory too fragmented for the next
// PARLIO descriptor list. P4 GDMA supports cache-aligned PSRAM payloads; keep
// descriptors/control in SDK-owned internal memory, but do not spend another
// 4KiB of that scarce pool on a transient payload. The pinned RX driver splits
// and synchronizes cached buffers; TX performs its own C2M synchronization.
// Earlier qualification profiles retain their measured internal allocation.
#if defined(AGON_EXTENDER_EXEXT_STREAM)
constexpr unsigned payloadCaps = MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT;
#else
constexpr unsigned payloadCaps = MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT;
#endif
static_assert(std::atomic<std::size_t>::is_always_lock_free &&
              std::atomic<unsigned>::is_always_lock_free &&
              std::atomic<bool>::is_always_lock_free,"ISR publication must be lock-free");
bool IRAM_ATTR P4NativePayload::receiveDone(parlio_rx_unit_handle_t unit,
    parlio_rx_event_data_t const* e,void* context) noexcept {
  auto& p=*static_cast<P4NativePayload*>(context);
  if(!p.accepting_.load(std::memory_order_acquire))return false;
  if(unit!=p.rx_ || e->data!=p.dma_ || e->delimiter!=p.delimiter_ || p.done_.load())
    p.edges_.fetch_or(4,std::memory_order_release);
  p.completed_.store(e->recv_bytes,std::memory_order_relaxed);
  p.done_.store(true,std::memory_order_release);return false;
}
bool IRAM_ATTR P4NativePayload::transmitDone(parlio_tx_unit_handle_t unit,
    parlio_tx_done_event_data_t const*,void* context) noexcept {
  auto& p=*static_cast<P4NativePayload*>(context);
  if(!p.accepting_.load(std::memory_order_acquire))return false;
  if(unit!=p.tx_ || p.done_.load())p.edges_.fetch_or(4,std::memory_order_release);
  p.completed_.store(p.length_,std::memory_order_relaxed);
  p.done_.store(true,std::memory_order_release);return false;
}
bool P4NativePayload::setReadyN(bool high) noexcept {
  return gpio_set_level(static_cast<gpio_num_t>(ready_),high?1:0)==ESP_OK;
}
P4NativePayload::Result P4NativePayload::arm(P4ParallelHandover const& h,
    bool parked,bool transmit,std::uint8_t* buffer,std::size_t capacity,
    std::size_t length,std::uint32_t now,std::uint32_t timeout) noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if((result_!=Result::idle
#if defined(AGON_EXTENDER_EXEXT_STREAM)
      && result_!=Result::complete
#endif
     ) || !parked || h.failed() || h.phase()!=P4ParallelHandover::localArm ||
      !buffer || !length || length>4096 || capacity<length || !timeout || timeout>2000 ||
      !gpio_get_level(static_cast<gpio_num_t>(clock_)) ||
      !gpio_get_level(static_cast<gpio_num_t>(valid_)))return Result::rejected;
  // No GPIO/peripheral mutation before every bound and ownership check passes.
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  keepResources_=true;
#endif
  handover_=&h;buffer_=buffer;length_=length;transmit_=transmit;began_=now;timeout_=timeout;
  result_=Result::pending;edges_.store(0);done_.store(false);completed_.store(0);
  accepting_.store(true,std::memory_order_release);
  if(!setReadyN(true))return finish(Result::fault);
  if(transmit_) {
    auto r=egress_.begin(buffer,length,now,timeout);
    if(r!=ParallelTxResult::pending) {
      return finish(r==ParallelTxResult::cleanupFault?Result::cleanupFault:Result::fault);
    }
  } else {
    // Reuse the proved byte-count EOF rather than the P4 level-inactive EOF
    // which failed physically in r07/r08. Independent hardware counters
    // prove exactly N active CLOCK edges and one complete VALID pulse.
    if(!startReceive() || !setReadyN(false))return finish(Result::fault);
  }
  return result_;
}
#if defined(AGON_EXTENDER_EXEXT_STREAM)
bool P4NativePayload::attachDataPins(bool transmit) noexcept {
  // ExExt retains disabled SDK units between blocks to avoid allocating GDMA
  // descriptors after game assets consume internal DMA RAM. UART restoration
  // resets these pads, so replay the pinned IDF5.5.5 PARLIO GPIO routing only
  // AFTER actual parking/admission. P4 has exactly one group and unit per
  // direction; another target must supply its own adapter, not assume index0.
  static_assert(SOC_PARLIO_GROUPS==1 && SOC_PARLIO_TX_UNITS_PER_GROUP==1 &&
                SOC_PARLIO_RX_UNITS_PER_GROUP==1,"P4-only retained unit mapping");
  const auto &g=parlio_periph_signals.groups[0];
  for(std::size_t i=0;i<pins_.size();++i) {
    const auto pin=gpio_num_t(pins_[i]);
    if(transmit) {
      gpio_func_sel(pin,PIN_FUNC_GPIO);
      esp_rom_gpio_connect_out_signal(pin,g.tx_units[0].data_sigs[i],false,false);
    } else {
      if(gpio_input_enable(pin)!=ESP_OK)return false;
      esp_rom_gpio_connect_in_signal(pin,g.rx_units[0].data_sigs[i],false);
    }
  }
  if(gpio_input_enable(gpio_num_t(clock_))!=ESP_OK ||
     gpio_input_enable(gpio_num_t(valid_))!=ESP_OK)return false;
  esp_rom_gpio_connect_in_signal(clock_,transmit?g.tx_units[0].clk_in_sig:
      g.rx_units[0].clk_in_sig,false);
  return true;
}
#endif
bool P4NativePayload::start(std::uint8_t const* data,std::size_t length) noexcept {
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  if(!dma_)dma_=static_cast<std::uint8_t*>(heap_caps_aligned_alloc(64,4096,payloadCaps));
#else
  dma_=static_cast<std::uint8_t*>(heap_caps_aligned_alloc(64,length,payloadCaps));
#endif
  if(!dma_)return false;
  std::memcpy(dma_,data,length);
  // PORT-008 DI05: observed extra CLOCK edges skipped TX bytes. The P4's
  // fixed pin filter rejects sub-two-sample pulses before PARLIO; it does not
  // alter the eZ80 protocol. Keep its lifetime inside this admitted native leaf.
  gpio_pin_glitch_filter_config_t filter{};
  filter.gpio_num=static_cast<gpio_num_t>(clock_);filter.clk_src=GLITCH_FILTER_CLK_SRC_DEFAULT;
  if(!clockFilter_ && gpio_new_pin_glitch_filter(&filter,&clockFilter_)!=ESP_OK)return false;
  if(gpio_glitch_filter_enable(clockFilter_)!=ESP_OK)return false;
  clockFilterEnabled_=true;
  parlio_tx_unit_config_t config{};
  for(auto& pin:config.data_gpio_nums)pin=GPIO_NUM_NC;
  for(std::size_t i=0;i<pins_.size();++i)config.data_gpio_nums[i]=static_cast<gpio_num_t>(pins_[i]);
  config.clk_src=PARLIO_CLK_SRC_EXTERNAL;config.clk_in_gpio_num=static_cast<gpio_num_t>(clock_);
  config.input_clk_src_freq_hz=config.output_clk_freq_hz=10000000;
  config.clk_out_gpio_num=config.valid_gpio_num=GPIO_NUM_NC;
  config.data_width=8;config.trans_queue_depth=1;config.max_transfer_size=
#if defined(AGON_EXTENDER_EXEXT_STREAM)
      4096;
#else
      length;
#endif
  config.shift_edge=PARLIO_SHIFT_EDGE_NEG;config.bit_pack_order=PARLIO_BIT_PACK_ORDER_LSB;
  if(!tx_) {
    if(parlio_new_tx_unit(&config,&tx_)!=ESP_OK)return false;
    parlio_tx_event_callbacks_t callbacks{};callbacks.on_trans_done=transmitDone;
    if(parlio_tx_unit_register_event_callbacks(tx_,&callbacks,this)!=ESP_OK)return false;
  }
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  if(!attachDataPins(true))return false;
#endif
  if(parlio_tx_unit_enable(tx_)!=ESP_OK)return false;
  enabled_=true;
  parlio_transmit_config_t transfer{};
  // IDF retains idle data even after disable. Hold the final byte, never zero,
  // until EMOS's latched VALID release; GPIO detach then provides high impedance.
  transfer.idle_value=dma_[length-1];transfer.flags.queue_nonblocking=true;
  return parlio_tx_unit_transmit(tx_,dma_,length*8,&transfer)==ESP_OK
#if !defined(AGON_EXTENDER_PARALLEL_DATA_CHECK) && !defined(AGON_EXTENDER_EXEXT_STREAM)
      && validCounter_.begin()
#endif
      ;
}
bool P4NativePayload::startReceive() noexcept {
  // Fixed-count EOF matches the earlier physical RX prototype. PCNT, not
  // a synthetic EOF or task-level pin sample, rejects short/extra records.
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  if(!dma_)dma_=static_cast<std::uint8_t*>(heap_caps_aligned_alloc(64,4096,payloadCaps));
#else
  dma_=static_cast<std::uint8_t*>(heap_caps_aligned_alloc(64,length_,payloadCaps));
#endif
  if(!dma_)return false;
  parlio_rx_unit_config_t config{};
  for(auto& pin:config.data_gpio_nums)pin=GPIO_NUM_NC;
  for(std::size_t i=0;i<pins_.size();++i)config.data_gpio_nums[i]=static_cast<gpio_num_t>(pins_[i]);
  config.data_width=8;config.trans_queue_depth=1;config.max_recv_size=
#if defined(AGON_EXTENDER_EXEXT_STREAM)
      4096;
#else
      length_;
#endif
  config.dma_burst_size=64;config.clk_src=PARLIO_CLK_SRC_EXTERNAL;
  config.ext_clk_freq_hz=config.exp_clk_freq_hz=10000000;
  config.clk_in_gpio_num=static_cast<gpio_num_t>(clock_);config.clk_out_gpio_num=GPIO_NUM_NC;
  config.valid_gpio_num=static_cast<gpio_num_t>(valid_);config.flags.free_clk=true;
  if(!rx_) {
    if(parlio_new_rx_unit(&config,&rx_)!=ESP_OK)return false;
    parlio_rx_event_callbacks_t callbacks{};callbacks.on_receive_done=receiveDone;
    if(parlio_rx_unit_register_event_callbacks(rx_,&callbacks,this)!=ESP_OK)return false;
  }
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  if(!attachDataPins(false))return false;
#endif
  parlio_rx_level_delimiter_config_t delimiter{};
  delimiter.valid_sig_line_id=PARLIO_RX_UNIT_MAX_DATA_WIDTH-1;
  delimiter.sample_edge=PARLIO_SAMPLE_EDGE_NEG;delimiter.bit_pack_order=PARLIO_BIT_PACK_ORDER_LSB;
  delimiter.flags.active_low_en=true;delimiter.eof_data_len=length_;
  if(parlio_new_rx_level_delimiter(&delimiter,&delimiter_)!=ESP_OK)return false;
  if(parlio_rx_unit_enable(rx_,true)!=ESP_OK)return false;
  enabled_=true;
  parlio_receive_config_t receive{};receive.delimiter=delimiter_;
  return parlio_rx_unit_receive(rx_,dma_,length_,&receive)==ESP_OK
#if !defined(AGON_EXTENDER_PARALLEL_DATA_CHECK) && !defined(AGON_EXTENDER_EXEXT_STREAM)
      && clockCounter_.beginClock(clock_,length_) && validCounter_.begin()
#endif
      ;
}
ParallelTxProgress P4NativePayload::progress() noexcept {
  const bool done=done_.load(std::memory_order_acquire);
  const auto edges=edges_.load(std::memory_order_acquire);
  const auto bytes=done?completed_.load(std::memory_order_relaxed):0;
  const auto status=(edges&4)?ParallelTxStatus::failed:done?ParallelTxStatus::complete:ParallelTxStatus::pending;
  const bool exact=done && bytes==length_ && !(edges&4);
#if defined(AGON_EXTENDER_PARALLEL_DATA_CHECK) || defined(AGON_EXTENDER_EXEXT_STREAM)
  // Qualified fixed-length composition, also reused by ordinary ExExt: DMA
  // completion proves clocks occurred; inactive VALID permits retirement.
  // This does not prove pulse/edge counts or payload integrity. Retained
  // diagnostic MOSlets compare every byte; ordinary VDU is a byte stream.
  // Keep the separate strict edge-count qualification composition unchanged.
  return {status,bytes,exact,exact && bool(gpio_get_level(gpio_num_t(valid_)))};
#else
  if(!transmit_) {
    // Freeze CLOCK first with VALID inactive, while its edge counter still
    // runs. Any qualified edge after CLOCK freezes needs a new VALID pulse,
    // which the subsequent VALID stop/re-read rejects. Reversing this order
    // would leave a gap for a short extra VALID pulse between the two stops.
    const auto clocks=clockCounter_.sample(exact);
    const auto valid=validCounter_.sample(clocks.ended);
    return {clocks.failed || valid.failed?ParallelTxStatus::failed:status,bytes,valid.started,clocks.ended && valid.ended};
  }
  const auto proof=validCounter_.sample(exact);
  return {proof.failed?ParallelTxStatus::failed:status,bytes,proof.started,proof.ended};
#endif
}
bool P4NativePayload::stop() noexcept {
  // PCNT owns no application callback, but failed stop/delete still retains
  // this owner and DMA. Its finite capture window is bounded by the native deadline.
  bool okay=true;
#if !defined(AGON_EXTENDER_PARALLEL_DATA_CHECK) && !defined(AGON_EXTENDER_EXEXT_STREAM)
  okay=validCounter_.cleanup();
  if(!clockCounter_.cleanup())okay=false;
#endif
  if(enabled_) {
    auto status=transmit_?parlio_tx_unit_disable(tx_):parlio_rx_unit_disable(rx_);
    if(status==ESP_OK)enabled_=false;else okay=false;
  }
  if(!enabled_
#if defined(AGON_EXTENDER_EXEXT_STREAM)
     && !keepResources_
#endif
    ) {
    if(tx_) {if(parlio_del_tx_unit(tx_)==ESP_OK)tx_=nullptr;else okay=false;}
    if(rx_) {if(parlio_del_rx_unit(rx_)==ESP_OK)rx_=nullptr;else okay=false;}
  }
  if(!enabled_
#if !defined(AGON_EXTENDER_EXEXT_STREAM)
     && !rx_
#endif
     && delimiter_) {if(parlio_del_rx_delimiter(delimiter_)==ESP_OK)delimiter_=nullptr;else okay=false;}
  // Do not remove CLOCK filtering while the TX peripheral may still run.
  // Failed cleanup retains this object and DMA until cancel() can retry.
  if(clockFilter_ && !enabled_
#if !defined(AGON_EXTENDER_EXEXT_STREAM)
     && !tx_
#endif
    ) {
    if(clockFilterEnabled_) {
      if(gpio_glitch_filter_disable(clockFilter_)==ESP_OK)clockFilterEnabled_=false;else okay=false;
    }
    if(!clockFilterEnabled_
#if defined(AGON_EXTENDER_EXEXT_STREAM)
       && !keepResources_
#endif
      ) {
      if(gpio_del_glitch_filter(clockFilter_)==ESP_OK)clockFilter_=nullptr;else okay=false;
    }
  }
  const bool stopped=okay && !clockFilterEnabled_ && !enabled_ && !delimiter_
#if defined(AGON_EXTENDER_EXEXT_STREAM)
      && (keepResources_ || (!clockFilter_ && !tx_ && !rx_));
#else
      && !clockFilter_ && !tx_ && !rx_;
#endif
  if(stopped)accepting_.store(false,std::memory_order_release);
  // Keep DMA through pad-release proof and RX publication. A cleanup fault
  // retains storage and callback context until the owner retries cancel().
  return stopped;
}
void P4NativePayload::discardBuffer() noexcept {
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  if(keepResources_)return;
#endif
  if(dma_){heap_caps_free(dma_);dma_=nullptr;}
}
bool P4NativePayload::releaseDataPins() noexcept {
  bool okay=true;
  for(int pin:pins_) {
    const auto gpio=static_cast<gpio_num_t>(pin);
    // Try input fencing even when mux reset fails; attempt every pad.
    if(gpio_reset_pin(gpio)!=ESP_OK)okay=false;
    if(gpio_set_direction(gpio,GPIO_MODE_INPUT)!=ESP_OK)okay=false;
    if(gpio_pullup_dis(gpio)!=ESP_OK)okay=false;
    if(gpio_pulldown_dis(gpio)!=ESP_OK)okay=false;
  }
  return okay;
}
P4NativePayload::Result P4NativePayload::finish(Result outcome) noexcept {
  // EX06: report the first failed leaf's retained facts before cleanup. USB
  // stdout only, after failure; no probe/counter or successful payload cost.
  if(outcome!=Result::complete && result_==Result::pending)
    printf("Parallel native outcome=%u tx=%u requested=%u done=%u bytes=%u callback_fault=%u clock=%d valid=%d\n",
      unsigned(outcome),unsigned(transmit_),unsigned(length_),unsigned(done_.load()),
      unsigned(completed_.load()),unsigned(edges_.load()),
      gpio_get_level(gpio_num_t(clock_)),gpio_get_level(gpio_num_t(valid_)));
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  if(outcome!=Result::complete)keepResources_=false;
#endif
  const bool stopped=stop(),released=releaseDataPins();
  if(!stopped || !released || !setReadyN(true))return result_=Result::cleanupFault;
  if(outcome==Result::complete && !transmit_)std::memcpy(buffer_,dma_,length_);
  discardBuffer();
  return result_=outcome;
}
P4NativePayload::Result P4NativePayload::poll(std::uint32_t now) noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if(result_!=Result::pending)return result_;
  if(handover_->failed() || (handover_->phase()!=P4ParallelHandover::localArm &&
      handover_->phase()!=P4ParallelHandover::block))return finish(Result::fault);
  if(transmit_) {
    auto r=egress_.poll(now);
    if(r==ParallelTxResult::pending)return result_;
    if(r!=ParallelTxResult::complete)
      printf("Parallel native TX result=%u requested=%u done=%u bytes=%u callback_fault=%u clock=%d valid=%d\n",
        unsigned(r),unsigned(length_),unsigned(done_.load()),unsigned(completed_.load()),
        unsigned(edges_.load()),gpio_get_level(gpio_num_t(clock_)),gpio_get_level(gpio_num_t(valid_)));
    const auto outcome=r==ParallelTxResult::complete?Result::complete:
        r==ParallelTxResult::cleanupFault?Result::cleanupFault:
        r==ParallelTxResult::timeout?Result::timeout:Result::fault;
#if defined(AGON_EXTENDER_EXEXT_STREAM)
    if(outcome!=Result::complete)return finish(outcome);
#endif
    if(r!=ParallelTxResult::cleanupFault)discardBuffer();
    return result_=outcome;
  }
  if(std::uint32_t(now-began_)>=timeout_)return finish(Result::timeout);
  const auto p=progress();
  // Fixed-count hardware EOF alone cannot prove the record ended or reject
  // extra clocks. Both PCNT proofs must freeze successfully before publish.
  if(p.status==ParallelTxStatus::failed || p.bytes>length_)return finish(Result::fault);
  if(p.status==ParallelTxStatus::pending)return result_;
  if(p.bytes!=length_)return finish(Result::fault);
  if(!p.ended)return result_;
  // The caller still withholds this block until matched UART completion status.
  return finish(Result::complete);
}
P4NativePayload::Result P4NativePayload::cancel() noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if(result_==Result::idle)return Result::idle;
  return finish(Result::fault);
}
}
