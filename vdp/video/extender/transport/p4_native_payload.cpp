#include "p4_native_payload.hpp"
#include <cstring>
#include <driver/gpio.h>
#include <esp_heap_caps.h>
#include <freertos/FreeRTOS.h>
namespace agon::extender::transport {
static_assert(std::atomic<std::size_t>::is_always_lock_free &&
              std::atomic<unsigned>::is_always_lock_free &&
              std::atomic<bool>::is_always_lock_free,"ISR publication must be lock-free");
void IRAM_ATTR P4NativePayload::validEdge(void* context) noexcept {
  auto& p=*static_cast<P4NativePayload*>(context);
  if(!p.accepting_.load(std::memory_order_acquire))return;
  const unsigned bit=gpio_get_level(static_cast<gpio_num_t>(p.valid_))?2:1;
  const auto old=p.edges_.fetch_or(bit,std::memory_order_acq_rel);
  // A single record permits exactly one falling then one rising edge. GPIO
  // interrupts can coalesce short pulses: absence of an edge is a timeout,
  // never permission to infer one from the final inactive level.
  if((bit==2 && !(old&1)) || (old&bit))p.edges_.fetch_or(4,std::memory_order_release);
}
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
bool P4NativePayload::watchValid() noexcept {
  // Share an installed GPIO ISR service; never uninstall another owner's service.
  auto error=gpio_install_isr_service(0);
  if(error!=ESP_OK && error!=ESP_ERR_INVALID_STATE)return false;
  if(gpio_set_intr_type(static_cast<gpio_num_t>(valid_),GPIO_INTR_ANYEDGE)!=ESP_OK)return false;
  if(gpio_isr_handler_add(static_cast<gpio_num_t>(valid_),validEdge,this)!=ESP_OK)return false;
  watching_=true;return true;
}
bool P4NativePayload::setReadyN(bool high) noexcept {
  return gpio_set_level(static_cast<gpio_num_t>(ready_),high?1:0)==ESP_OK;
}
P4NativePayload::Result P4NativePayload::arm(P4ParallelHandover const& h,
    bool parked,bool transmit,std::uint8_t* buffer,std::size_t capacity,
    std::size_t length,std::uint32_t now,std::uint32_t timeout) noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if(result_!=Result::idle || !parked || h.failed() || h.phase()!=P4ParallelHandover::localArm ||
      !buffer || !length || length>4096 || capacity<length || !timeout || timeout>0x7fffffffU ||
      !gpio_get_level(static_cast<gpio_num_t>(clock_)) ||
      !gpio_get_level(static_cast<gpio_num_t>(valid_)))return Result::rejected;
  // No GPIO/peripheral mutation before every bound and ownership check passes.
  handover_=&h;buffer_=buffer;length_=length;transmit_=transmit;began_=now;timeout_=timeout;
  result_=Result::pending;edges_.store(0);done_.store(false);completed_.store(0);
  accepting_.store(true,std::memory_order_release);
  if(!setReadyN(true))return finish(Result::fault);
  if(transmit_) {
    auto r=egress_.begin(buffer,length,now,timeout);
    if(r!=ParallelTxResult::pending) {
      if(r!=ParallelTxResult::cleanupFault)discardBuffer();
      return result_=r==ParallelTxResult::cleanupFault?Result::cleanupFault:Result::fault;
    }
  } else if(!startReceive() || !watchValid() || !setReadyN(false))return finish(Result::fault);
  return result_;
}
bool P4NativePayload::start(std::uint8_t const* data,std::size_t length) noexcept {
  dma_=static_cast<std::uint8_t*>(heap_caps_aligned_alloc(64,length,MALLOC_CAP_INTERNAL|MALLOC_CAP_DMA|MALLOC_CAP_8BIT));
  if(!dma_)return false;
  std::memcpy(dma_,data,length);
  parlio_tx_unit_config_t config{};
  for(auto& pin:config.data_gpio_nums)pin=GPIO_NUM_NC;
  for(std::size_t i=0;i<pins_.size();++i)config.data_gpio_nums[i]=static_cast<gpio_num_t>(pins_[i]);
  config.clk_src=PARLIO_CLK_SRC_EXTERNAL;config.clk_in_gpio_num=static_cast<gpio_num_t>(clock_);
  config.input_clk_src_freq_hz=config.output_clk_freq_hz=10000000;
  config.clk_out_gpio_num=config.valid_gpio_num=GPIO_NUM_NC;
  config.data_width=8;config.trans_queue_depth=1;config.max_transfer_size=length;
  config.shift_edge=PARLIO_SHIFT_EDGE_NEG;config.bit_pack_order=PARLIO_BIT_PACK_ORDER_LSB;
  if(parlio_new_tx_unit(&config,&tx_)!=ESP_OK)return false;
  parlio_tx_event_callbacks_t callbacks{};callbacks.on_trans_done=transmitDone;
  if(parlio_tx_unit_register_event_callbacks(tx_,&callbacks,this)!=ESP_OK ||
      parlio_tx_unit_enable(tx_)!=ESP_OK)return false;
  enabled_=true;
  parlio_transmit_config_t transfer{};
  // IDF retains idle data even after disable. Hold the final byte, never zero,
  // until EMOS's latched VALID release; GPIO detach then provides high impedance.
  transfer.idle_value=dma_[length-1];transfer.flags.queue_nonblocking=true;
  return parlio_tx_unit_transmit(tx_,dma_,length*8,&transfer)==ESP_OK && watchValid();
}
bool P4NativePayload::startReceive() noexcept {
  // Sentinel distinguishes exact length from overlong VALID-qualified records.
  dma_=static_cast<std::uint8_t*>(heap_caps_aligned_alloc(64,length_+1,MALLOC_CAP_INTERNAL|MALLOC_CAP_DMA|MALLOC_CAP_8BIT));
  if(!dma_)return false;
  parlio_rx_unit_config_t config{};
  for(auto& pin:config.data_gpio_nums)pin=GPIO_NUM_NC;
  for(std::size_t i=0;i<pins_.size();++i)config.data_gpio_nums[i]=static_cast<gpio_num_t>(pins_[i]);
  config.data_width=8;config.trans_queue_depth=1;config.max_recv_size=length_+1;
  config.dma_burst_size=64;config.clk_src=PARLIO_CLK_SRC_EXTERNAL;
  config.ext_clk_freq_hz=config.exp_clk_freq_hz=10000000;
  config.clk_in_gpio_num=static_cast<gpio_num_t>(clock_);config.clk_out_gpio_num=GPIO_NUM_NC;
  config.valid_gpio_num=static_cast<gpio_num_t>(valid_);config.flags.free_clk=false;
  if(parlio_new_rx_unit(&config,&rx_)!=ESP_OK)return false;
  parlio_rx_level_delimiter_config_t delimiter{};
  delimiter.valid_sig_line_id=PARLIO_RX_UNIT_MAX_DATA_WIDTH-1;
  delimiter.sample_edge=PARLIO_SAMPLE_EDGE_NEG;delimiter.bit_pack_order=PARLIO_BIT_PACK_ORDER_LSB;
  delimiter.flags.active_low_en=true;
  if(parlio_new_rx_level_delimiter(&delimiter,&delimiter_)!=ESP_OK)return false;
  parlio_rx_event_callbacks_t callbacks{};callbacks.on_receive_done=receiveDone;
  if(parlio_rx_unit_register_event_callbacks(rx_,&callbacks,this)!=ESP_OK ||
      parlio_rx_unit_enable(rx_,true)!=ESP_OK)return false;
  enabled_=true;
  parlio_receive_config_t receive{};receive.delimiter=delimiter_;
  return parlio_rx_unit_receive(rx_,dma_,length_+1,&receive)==ESP_OK;
}
ParallelTxProgress P4NativePayload::progress() noexcept {
  const bool done=done_.load(std::memory_order_acquire);
  const auto edges=edges_.load(std::memory_order_acquire);
  return {(edges&4)?ParallelTxStatus::failed:done?ParallelTxStatus::complete:ParallelTxStatus::pending,
          done?completed_.load(std::memory_order_relaxed):0,bool(edges&1),bool(edges&2)};
}
bool P4NativePayload::stop() noexcept {
  bool okay=true;
  if(watching_) {
    if(gpio_isr_handler_remove(static_cast<gpio_num_t>(valid_))==ESP_OK)watching_=false;
    else okay=false;
  }
  if(enabled_) {
    auto status=transmit_?parlio_tx_unit_disable(tx_):parlio_rx_unit_disable(rx_);
    if(status==ESP_OK)enabled_=false;else okay=false;
  }
  if(!enabled_) {
    if(tx_) {if(parlio_del_tx_unit(tx_)==ESP_OK)tx_=nullptr;else okay=false;}
    if(rx_) {if(parlio_del_rx_unit(rx_)==ESP_OK)rx_=nullptr;else okay=false;}
    if(!rx_ && delimiter_) {if(parlio_del_rx_delimiter(delimiter_)==ESP_OK)delimiter_=nullptr;else okay=false;}
  }
  const bool stopped=okay && !enabled_ && !tx_ && !rx_ && !delimiter_ && !watching_;
  if(stopped)accepting_.store(false,std::memory_order_release);
  // Keep DMA through pad-release proof and RX publication. A cleanup fault
  // retains storage and callback context until the owner retries cancel().
  return stopped;
}
void P4NativePayload::discardBuffer() noexcept {
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
    if(r!=ParallelTxResult::cleanupFault)discardBuffer();
    return result_=r==ParallelTxResult::complete?Result::complete:
        r==ParallelTxResult::cleanupFault?Result::cleanupFault:
        r==ParallelTxResult::timeout?Result::timeout:Result::fault;
  }
  if(std::uint32_t(now-began_)>=timeout_)return finish(Result::timeout);
  const auto p=progress();
  if(p.status==ParallelTxStatus::failed || p.bytes>length_ || (p.ended&&!p.started))return finish(Result::fault);
  if(!p.started || !p.ended || p.status==ParallelTxStatus::pending)return result_;
  if(p.bytes!=length_)return finish(Result::fault);
  // The caller still withholds this block until matched UART completion status.
  return finish(Result::complete);
}
P4NativePayload::Result P4NativePayload::cancel() noexcept {
  if(xPortGetCoreID()!=core_)return Result::wrongOwner;
  if(result_==Result::idle)return Result::idle;
  return finish(Result::fault);
}
}
