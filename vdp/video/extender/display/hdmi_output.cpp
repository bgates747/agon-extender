#include "extender/display/rolling/task_memory.hpp"
#include "extender/diagnostics/render_benchmark.hpp"
#include "esp_heap_caps.h"
// HDMI-001 uses the visually accepted P4PC-001 r06/r09 timing, not the generic
// Olimex 64 MHz preset. IDF 5.5.5 on P4 v1.3 has no hardware VSYNC interrupt:
// its callback is a whole-frame DMA completion proxy. Rendering remains on the
// task in the normal output path. The explicitly selected rolling experiment
// additionally copies strips by DMA2D and paints immutable sprite snapshots in
// completion callbacks; it never enters the mutable native renderer there.
#include "extender/display/hdmi_output.hpp"
#include "extender/display/stock_runtime_controller.hpp"
#include "extender/display/presentation_snapshot_pool.hpp"
#include "esp_lcd_lt8912b.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/task.h"
#include <algorithm>
#include <cstring>
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
#include "extender/display/rolling/bridge.h"
#include "extender/display/rolling/strip_probe.h"
#endif

namespace agon::extender::display {
namespace {
constexpr char kTag[] = "ext-hdmi";

static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
              "Scanout ISR requires lock-free 32-bit counters");
}

HdmiOutput &hdmiOutput() { static HdmiOutput output; return output; }

void HdmiOutput::cleanup() {
  ready_ = false;
  output_size_.store(0, std::memory_order_release);
  if (panel_) { esp_lcd_panel_del(panel_); panel_ = nullptr; }
#ifdef AGON_EXTENDER_HDMI_PPA_320
  scaler_.reset();
#endif
  for (auto &io : io_) if (io) { esp_lcd_panel_io_del(io); io = nullptr; }
  if (dsi_) { esp_lcd_del_dsi_bus(dsi_); dsi_ = nullptr; }
  if (i2c_) { i2c_del_master_bus(i2c_); i2c_ = nullptr; }
  if (phy_power_) { esp_ldo_release_channel(phy_power_); phy_power_ = nullptr; }
#ifdef AGON_EXTENDER_BENCH_OFF
  for(auto *buffer:buffers_) if(buffer)heap_caps_free(buffer);
#endif
  buffers_[0] = buffers_[1] = nullptr;
  buffer_count_ = 0;
  ownership_.reset();
  report_updates_ = report_submissions_ = report_swap_drops_ = 0;
  report_conversion_us_ = report_cache_us_ = report_wait_us_ = report_conversion_max_us_ = 0;
  buffer_width_[0] = buffer_width_[1] = 0;
  buffer_height_[0] = buffer_height_[1] = 0;
  scanouts_.store(0, std::memory_order_relaxed);
  interrupt_core_.store(UINT32_MAX, std::memory_order_relaxed);
}

bool HdmiOutput::start() {
  if (ready_) return true;
#ifdef AGON_EXTENDER_BENCH_OFF
  // Retain the same RGB888 allocation while deliberately starting no DSI DMA.
  for(auto &buffer:buffers_)buffer=static_cast<std::uint8_t *>(heap_caps_aligned_calloc(64,1,bufferBytes(),MALLOC_CAP_SPIRAM));
  if(!buffers_[0]||!buffers_[1]){cleanup();return false;}
  buffer_count_=2;ready_=true;
#ifdef AGON_EXTENDER_DIRECT_RGB888
  if(!startDirectSubmitter()){cleanup();return false;}
#endif
  return true;
#endif
  // IDF allocates both the DSI and DMA interrupt on this calling core. The
  // submission task must share core 1 so its metadata publication cannot race
  // the driver's snapshot of cur_fb_index in an ISR executing on another core.
  if (xPortGetCoreID() != 1) {
    ESP_LOGE(kTag, "HDMI initialization must run on core 1");
    return false;
  }
  auto failed = [this](esp_err_t error, char const *operation) {
    ESP_LOGE(kTag, "%s: %s", operation, esp_err_to_name(error));
    cleanup();
    return false;
  };
#ifdef AGON_EXTENDER_HDMI_PPA_320
  if(!scaler_.initialize())return failed(ESP_ERR_NO_MEM,"PPA snapshot/client allocation");
#endif
  esp_ldo_channel_config_t power{};
  power.chan_id = 3;
  power.voltage_mv = 2500;
  auto error = esp_ldo_acquire_channel(&power, &phy_power_);
  if (error != ESP_OK) return failed(error, "DSI PHY power");

  i2c_master_bus_config_t i2c_config{};
  i2c_config.i2c_port = I2C_NUM_0;
  i2c_config.sda_io_num = GPIO_NUM_7;
  i2c_config.scl_io_num = GPIO_NUM_8;
  i2c_config.clk_source = I2C_CLK_SRC_DEFAULT;
  i2c_config.flags.enable_internal_pullup = true;
  error = i2c_new_master_bus(&i2c_config, &i2c_);
  if (error != ESP_OK) return failed(error, "LT8912B I2C bus");
  constexpr std::uint8_t addresses[] = {0x48, 0x49, 0x4a};
  for (unsigned i = 0; i < 3; ++i) {
    esp_lcd_panel_io_i2c_config_t io_config{};
    io_config.scl_speed_hz = 400000;
    io_config.dev_addr = addresses[i];
    io_config.control_phase_bytes = 1;
    io_config.lcd_cmd_bits = 8;
    io_config.lcd_param_bits = 8;
    io_config.flags.disable_control_phase = true;
    error = esp_lcd_new_panel_io_i2c(i2c_, &io_config, &io_[i]);
    if (error != ESP_OK) return failed(error, "LT8912B register bank");
  }

  esp_lcd_dsi_bus_config_t bus_config{};
  bus_config.bus_id = 0;
  bus_config.num_data_lanes = 2;
  bus_config.phy_clk_src = MIPI_DSI_PHY_CLK_SRC_DEFAULT;
  bus_config.lane_bit_rate_mbps = timing_.lane_mbps;
  error = esp_lcd_new_dsi_bus(&bus_config, &dsi_);
  if (error != ESP_OK) return failed(error, "DSI bus");

  esp_lcd_dpi_panel_config_t dpi{};
  dpi.virtual_channel = 0;
  dpi.dpi_clk_src = MIPI_DSI_DPI_CLK_SRC_PLL_F240M;
  dpi.dpi_clock_freq_mhz = timing_.pixel_mhz;
  dpi.in_color_format = LCD_COLOR_FMT_RGB888;
  dpi.out_color_format = LCD_COLOR_FMT_RGB888;
  dpi.num_fbs = 2;
  dpi.video_timing.h_size = width();
  dpi.video_timing.v_size = height();
  dpi.video_timing.hsync_pulse_width = timing_.h_sync;
  dpi.video_timing.hsync_back_porch = timing_.h_back;
  dpi.video_timing.hsync_front_porch = timing_.h_front;
  dpi.video_timing.vsync_pulse_width = timing_.v_sync;
  dpi.video_timing.vsync_back_porch = timing_.v_back;
  dpi.video_timing.vsync_front_porch = timing_.v_front;
  dpi.flags.disable_lp = true;
  // We expand straight into panel memory. DMA2D would add a copy and an
  // intermediate format; it does not expand stock RGB222/palette storage.
  dpi.flags.use_dma2d = false;

  lt8912b_vendor_config_t vendor{};
  vendor.video_timing.hfp = timing_.h_front;
  vendor.video_timing.hs = timing_.h_sync;
  vendor.video_timing.hbp = timing_.h_back;
  vendor.video_timing.hact = width();
  vendor.video_timing.htotal = timing_.hTotal();
  vendor.video_timing.vfp = timing_.v_front;
  vendor.video_timing.vs = timing_.v_sync;
  vendor.video_timing.vbp = timing_.v_back;
  vendor.video_timing.vact = height();
  vendor.video_timing.vtotal = timing_.vTotal();
  vendor.video_timing.h_polarity = timing_.h_positive;
  vendor.video_timing.v_polarity = timing_.v_positive;
  vendor.video_timing.vic = timing_.vic;
  vendor.video_timing.aspect_ratio = width() == 512
      ? LT8912B_ASPECT_RATION_4_3 : LT8912B_ASPECT_RATION_16_9;
  // Integer value is used only by the disabled bridge-internal test pattern.
  vendor.video_timing.pclk_mhz = static_cast<unsigned>(timing_.pixel_mhz+0.5f);
  vendor.mipi_config.dsi_bus = dsi_;
  vendor.mipi_config.dpi_config = &dpi;
  vendor.mipi_config.lane_num = 2;
  esp_lcd_panel_dev_config_t panel_config{};
  panel_config.bits_per_pixel = 24;
  panel_config.rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB;
  panel_config.reset_gpio_num = -1; // board bridge uses the driver's software reset
  panel_config.vendor_config = &vendor;
  esp_lcd_panel_lt8912b_io_t io_all{io_[0], io_[1], io_[2]};
  error = esp_lcd_new_panel_lt8912b(&io_all, &panel_config, &panel_);
  if (error == ESP_ERR_NO_MEM) {
    // IDF's failure path frees every partially allocated framebuffer and DMA
    // descriptor. Retry one panel buffer only after that clean failure.
    panel_ = nullptr;
    dpi.num_fbs = 1;
    ESP_LOGW(kTag, "Two HDMI buffers unavailable; retrying one (tearing possible)");
    error = esp_lcd_new_panel_lt8912b(&io_all, &panel_config, &panel_);
  }
  if (error != ESP_OK) return failed(error, "RGB888 panel buffers");
  buffer_count_ = dpi.num_fbs;
  void *buffer0{}, *buffer1{};
  error = buffer_count_ == 2
      ? esp_lcd_dpi_panel_get_frame_buffer(panel_, 2,
          &buffer0, &buffer1, static_cast<void **>(nullptr))
      : esp_lcd_dpi_panel_get_frame_buffer(panel_, 1,
          &buffer0, static_cast<void **>(nullptr));
  if (error != ESP_OK) return failed(error, "Panel buffer addresses");
  buffers_[0] = static_cast<std::uint8_t *>(buffer0);
  buffers_[1] = static_cast<std::uint8_t *>(buffer1);
  error = esp_lcd_panel_reset(panel_);
  if (error != ESP_OK) return failed(error, "LT8912B reset");
  esp_lcd_dpi_panel_event_callbacks_t callbacks{};
  callbacks.on_frame_buf_complete = frameComplete;
  error = esp_lcd_dpi_panel_register_event_callbacks(panel_, &callbacks, this);
  if (error != ESP_OK) return failed(error, "Scanout callback");
  error = esp_lcd_panel_init(panel_);
  if (error != ESP_OK) return failed(error, "LT8912B/DPI initialization");
  const auto first_frame_deadline = esp_timer_get_time() + 100000;
  while (interrupt_core_.load(std::memory_order_acquire) == UINT32_MAX &&
         esp_timer_get_time() < first_frame_deadline) vTaskDelay(1);
  if (interrupt_core_.load(std::memory_order_acquire) != 1)
    return failed(ESP_ERR_INVALID_STATE, "DSI DMA callback absent or on an unexpected core");
  portENTER_CRITICAL(&callback_mux_);
  ownership_.reset();
  portEXIT_CRITICAL(&callback_mux_);
  ready_ = true;
  output_size_.store(unsigned(width()) << 16 | unsigned(height()),std::memory_order_release);
#ifdef AGON_EXTENDER_DIRECT_RGB888
  if(!startDirectSubmitter()) return failed(ESP_ERR_NO_MEM,"Direct framebuffer submission task");
#endif
  report_started_ = esp_timer_get_time();
  report_scanouts_ = scanouts_.load(std::memory_order_relaxed);
  ESP_LOGI(kTag, "%dx%d RGB888, %.6fMHz pixel/two %uMbps lanes, %dx%d total, %.6fHz calculated; %u buffers/%u bytes",
           width(), height(), double(timing_.pixel_mhz), timing_.lane_mbps,
           timing_.hTotal(), timing_.vTotal(), timing_.refreshHz(),
           buffer_count_, static_cast<unsigned>(buffer_count_ * bufferBytes()));
  ESP_LOGI(kTag, "DSI/DMA IRQ and submission core 1; frame DMA completion is the vblank proxy on v1.3 silicon");
  return true;
}


bool HdmiOutput::needsMode(int w,int h) const {
#ifdef AGON_EXTENDER_HDMI_AUTO
  auto next=selectHdmiTiming(w,h);
  // Rebuild a faulted panel even when the requested carrier is unchanged.
  // The caller first joins both renderers and retires all borrowed pointers.
  return !ready_ || scanoutFailed() || next.width!=timing_.width || next.height!=timing_.height;
#else
  (void)w;(void)h;return false;
#endif
}
bool HdmiOutput::selectMode(int w,int h) {
#ifdef AGON_EXTENDER_HDMI_AUTO
  if(!needsMode(w,h))return true;
  if(!direct_task_ || frame_context_ || direct_state_.load()!=Idle)return false;
  requested_timing_=selectHdmiTiming(w,h);
  configure_state_.store(1,std::memory_order_release);
  xTaskNotifyGive(direct_task_);
  while(configure_state_.load(std::memory_order_acquire)==1)vTaskDelay(1);
  bool ok=configure_state_.load(std::memory_order_acquire)==2;
  configure_state_.store(0,std::memory_order_release);
  return ok;
#else
  (void)w;(void)h;return ready_;
#endif
}

bool HdmiOutput::bindFrameCallback(FrameCallback callback, void *context) {
  if (!ready_ || !callback || !context) return false;
  portENTER_CRITICAL(&callback_mux_);
  const bool available = frame_context_ == nullptr || frame_context_ == context;
  if (available) { frame_callback_ = callback; frame_context_ = context; }
  portEXIT_CRITICAL(&callback_mux_);
  return available;
}

void HdmiOutput::unbindFrameCallback(void *expected_context) {
  portENTER_CRITICAL(&callback_mux_);
#ifdef AGON_EXTENDER_DIRECT_RGB888
  // OFF uses the software clock and has no bound hardware callback, but its
  // detached drawing drain still needs to cancel a waiting logical swap.
  if(frame_context_==expected_context || frame_context_==nullptr)
    direct_cancelled_.store(true,std::memory_order_release);
#endif
  if (frame_context_ == expected_context) {
    frame_callback_ = nullptr; frame_context_ = nullptr;
#ifdef AGON_EXTENDER_DIRECT_RGB888
    direct_cancelled_.store(true,std::memory_order_release);
#endif
  }
  portEXIT_CRITICAL(&callback_mux_);
}

bool IRAM_ATTR HdmiOutput::frameComplete(esp_lcd_panel_handle_t,
                                        esp_lcd_dpi_panel_event_data_t *, void *context) {
  auto &output = *static_cast<HdmiOutput *>(context);
  output.interrupt_core_.store(xPortGetCoreID(), std::memory_order_release);
  output.scanouts_.fetch_add(1, std::memory_order_relaxed);
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
  agon_bench::scanout();
#endif
  bool task_woken = false;
  portENTER_CRITICAL_ISR(&output.callback_mux_);
  if (output.ownership_.pending()
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
      && (!output.rolling() || output.ownership_.submittedIndex()==agon_scanout_front())
#endif
      ) {
    // IDF snapshots the selected index and starts that frame's DMA before
    // entering this callback. Same-core task/ISR exclusion means pending can
    // only describe a selection made before this interrupt began. The old
    // front is now reusable. Metadata published after an interrupt safely
    // waits for the next one, occasionally repeating one complete frame.
    output.ownership_.frameComplete();
#ifdef AGON_EXTENDER_DIRECT_RGB888
    if(output.direct_state_.load(std::memory_order_relaxed)==Submitted)
      output.direct_state_.store(Complete,std::memory_order_release);
#endif
  }
  if (output.frame_callback_) task_woken = output.frame_callback_(output.frame_context_);
  portEXIT_CRITICAL_ISR(&output.callback_mux_);
  return task_woken;
}

bool HdmiOutput::scanoutFailed() const {
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  if (rolling()) {
    strip_async_stats status{};
    strip_async_read(&status);
    // An underrun observation alone is not an acknowledged DMA stop. Use the
    // runtime's contained-abort counter, not its first diagnostic reason.
    return status.faults != 0;
  }
#endif
  return false;
}

bool HdmiOutput::waitForSubmittedBuffer(std::atomic<bool> &stopping) {
  const auto started = esp_timer_get_time();
  for (;;) {
    if (stopping.load(std::memory_order_acquire) || scanoutFailed()) return false;
    portENTER_CRITICAL(&callback_mux_);
    const bool pending = ownership_.pending();
    portEXIT_CRITICAL(&callback_mux_);
    if (!pending) break;
    // Leave drawing, parser and logical frame progression running. A stalled
    // panel must never cause a buffer to be reused unsafely or block detach.
    vTaskDelay(1);
  }
  report_wait_us_ += esp_timer_get_time() - started;
  return true;
}

bool HdmiOutput::publish(StockRuntimeController &controller, std::atomic<bool> &stopping) {
#if defined(AGON_EXTENDER_BENCH_HOLD) || (defined(AGON_EXTENDER_BENCH_OFF) && !defined(AGON_EXTENDER_BENCH_CONVERT_OFF))
  return ready_ && !stopping.load();
#endif
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
  agon_bench::Scope conversion(agon_bench::Conversion);const auto conversion_token=conversion.token;int frame_id=-1;
#endif
  if (xPortGetCoreID() != 1) {
    ESP_LOGE(kTag, "HDMI publication must run on core 1");
    return false;
  }
#ifdef AGON_EXTENDER_DIRECT_RGB888
  if(controller.panelStorage()) {
    if(!ready_ || stopping.load(std::memory_order_acquire)) return false;
    const auto started=esp_timer_get_time();
    AGON_STOCK_NATIVE_GUARD;
    int marker=-1;
    const unsigned index=controller.preparePanelFrame(marker);
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
    if(rolling() && !agon_scanout_stage(static_cast<fabgl::P4Rgb888Controller *>(&controller.paletted()),index,
        controller.display().getViewPortWidth(),controller.display().getViewPortHeight()))return false;
#endif
    const auto prepared=esp_timer_get_time();
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    conversion.finish();
#ifndef AGON_EXTENDER_BENCH_OFF
    agon_bench::Scope cache(agon_bench::Cache);
#endif
#endif
#ifndef AGON_EXTENDER_BENCH_OFF
    // IDF recognizes its own pixel allocation: write back/select only. The VDP
    // already rendered here, with the panel stride; no row reader or memcpy.
    auto error=esp_lcd_panel_draw_bitmap(panel_,0,0,width(),height(),buffers_[index]);
    if(error!=ESP_OK) return false;
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
    if(rolling()) agon_scanout_commit();
#endif
    if(!controller.display().isDoubleBuffered()) {
      portENTER_CRITICAL(&callback_mux_);ownership_.submitted(index);portEXIT_CRITICAL(&callback_mux_);
    }
    ++report_submissions_;
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    agon_bench::update(conversion_token,marker);cache.finish();
#endif
#endif
    const auto finished=esp_timer_get_time();
    ++report_updates_;report_conversion_us_+=prepared-started;
    report_cache_us_+=finished-prepared;
    report_conversion_max_us_=std::max(report_conversion_max_us_,std::uint64_t(prepared-started));
    report(finished);return true;
  }
#endif
  if (!ready_ || stopping.load(std::memory_order_acquire) || !waitForSubmittedBuffer(stopping)) return false;
  auto &display = controller.display();
  const int width = display.getViewPortWidth();
  const int height = display.getViewPortHeight();
  bool scaled=false;
#ifdef AGON_EXTENDER_HDMI_PPA_320
  scaled=width==320 && height==240 && this->width()==848 && this->height()==480;
#endif
  const auto geometry = centeredHdmiGeometry(scaled?width*2:width, scaled?height*2:height,
                                             this->width(), this->height());
  if (!geometry.valid() || width > static_cast<int>(kPresentationSnapshotMaximumWidth)) return false;
  // Always use independent HDMI front/back for PPA, including single-buffered
  // logical modes. The logical swap counter remains owned by stock VDP.
  const bool doubled = (scaled || display.isDoubleBuffered()) && buffer_count_ == 2;
  if(scaled && !doubled)return false; // never PPA-write a scanned front
  portENTER_CRITICAL(&callback_mux_);
  const unsigned target = ownership_.writable(doubled);
  portEXIT_CRITICAL(&callback_mux_);
  auto *destination = buffers_[target];
  const auto started = esp_timer_get_time();
  const auto visible_generation = stockVisibleGeneration();
  const bool clear = buffer_width_[target] != width || buffer_height_[target] != height;
  if (clear) std::memset(destination, 0, bufferBytes());
  auto *image=destination;
  std::size_t image_stride=stride();
  auto image_geometry=geometry;
#ifdef AGON_EXTENDER_HDMI_PPA_320
  if(scaled) {
    image=scaler_.source();image_stride=320*3;
    image_geometry=centeredHdmiGeometry(320,240,320,240);
  }
#endif
  alignas(8) std::uint8_t signal[kPresentationSnapshotMaximumWidth];
  // Even cropped-out rows run in stock order. This preserves the existing
  // stock Copper cursor without adding indexed/Copper feature work.
  for (int y = 0; y < height; ++y) {
    if (stopping.load(std::memory_order_acquire)) return false;
    const bool direct = controller.rgb888Storage();
    if (direct) {
      const int destination_y = image_geometry.destination_y + y - image_geometry.source_y;
      // RGB-001 geometries fit wholly inside720p. Copy already-rendered BGR888
      // rows under the same native exclusion and generation check as stock.
      // Overlay rows use the stock decorator; there is no full-image expansion.
      controller.prepareRgb888Row(y, image + destination_y * image_stride +
          image_geometry.destination_x * kHdmiBytesPerPixel, signal);
    } else controller.prepareRow(y, signal);
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    if(y==0){unsigned a=0,b=0;bool valid=(signal[0^2]&63)==63&&(signal[1^2]&63)==0&&(signal[18^2]&63)==0&&(signal[19^2]&63)==63;
      for(int i=0;i<8;++i){a|=((signal[(2+i)^2]&63)!=0)<<i;b|=((signal[(10+i)^2]&63)!=0)<<i;}
      if(valid&&(a^b)==255&&a<40)frame_id=a;
    }
#endif
    if (y < image_geometry.source_y || y >= image_geometry.source_y + image_geometry.height) continue;
    if (direct) continue;
    const int destination_y = image_geometry.destination_y + y - image_geometry.source_y;
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
    agon_bench::Scope expand(agon_bench::Expand);
#endif
    expandSignalRowToHdmi(signal,
        image + destination_y * image_stride + image_geometry.destination_x * kHdmiBytesPerPixel,
        image_geometry.source_x, image_geometry.width);
  }
  auto conversion_finished = esp_timer_get_time();
  if (doubled && visible_generation != stockVisibleGeneration()) {
    // A logical swap during a row pass can mix two source images. Keep the
    // complete HDMI front and retry at the next ordinary frame opportunity.
    // No logical drawing, swap, counter or vblank waits are delayed here.
    ++report_swap_drops_;
    report(conversion_finished);
    return false;
  }
#ifdef AGON_EXTENDER_HDMI_PPA_320
  // The decorated source is now private and coherent. Native drawing/swapping
  // can continue during this SDK wait. No live row/sprite pointer is borrowed.
  if(scaled) {
    if(stopping.load(std::memory_order_acquire) || !scaler_.scale(destination,bufferBytes()))return false;
    conversion_finished=esp_timer_get_time();
    if(stopping.load(std::memory_order_acquire))return false;
  }
#endif
  const auto conversion_us = static_cast<std::uint64_t>(conversion_finished - started);
#ifdef AGON_EXTENDER_BENCH_CONVERT_OFF
  // Supplemental fixed-source control: OFF retains equal RGB888 allocations
  // and software60Hz logical opportunities but creates no DSI/DMA scanout.
  // Run the identical row reader/expander, then finish without panel submission.
  // Conversion scopes count attempts; accepted HDMI submissions remain zero.
  // Keep the original OFF drawing-only control and ordinary builds unchanged.
  // Record initialized borders just as normal publication does. The first
  // diagnostic build omitted this and incorrectly memset all720p pixels on
  // EVERY attempt; its controls are invalid for the scanout comparison.
  buffer_width_[target] = width;
  buffer_height_[target] = height;
  if (doubled) {
    // Alternate the same two allocations without a DMA ownership wait. This
    // advances memory-only ownership, not the physical scanout/update counters.
    portENTER_CRITICAL(&callback_mux_);
    ownership_.submitted(target);
    ownership_.frameComplete();
    portEXIT_CRITICAL(&callback_mux_);
  }
  (void)conversion_us;
  return true;
#endif
  // A pointer anywhere inside a panel-owned framebuffer takes IDF's direct
  // path: cache writeback and selection, without a pixel memcpy or DMA2D copy.
  // The driver flushes complete rows, so borders initialized once are retained.
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
  conversion.finish();agon_bench::Scope cache(agon_bench::Cache);
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  if(rolling() && !agon_scanout_stage(nullptr,target,geometry.width,geometry.height))return false;
#endif
  const auto error = esp_lcd_panel_draw_bitmap(panel_, 0,
      clear ? 0 : geometry.destination_y, this->width(),
      clear ? this->height() : geometry.destination_y + geometry.height, destination);
  if (error != ESP_OK) { ESP_LOGE(kTag, "Framebuffer submission: %s", esp_err_to_name(error)); return false; }
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  if(rolling()) agon_scanout_commit();
#endif
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
  agon_bench::update(conversion_token,frame_id);cache.finish();
#endif
  const auto submitted_at = esp_timer_get_time();
  buffer_width_[target] = width;
  buffer_height_[target] = height;
  ++report_updates_;
  ++report_submissions_;
  report_conversion_us_ += conversion_us;
  report_conversion_max_us_ = std::max(report_conversion_max_us_, conversion_us);
  report_cache_us_ += submitted_at - conversion_finished;
  if (doubled) {
    portENTER_CRITICAL(&callback_mux_);
    ownership_.submitted(target);
    portEXIT_CRITICAL(&callback_mux_);
    // Publish pending only AFTER draw_bitmap has flushed data and selected the
    // driver buffer. An ISR between that selection and this metadata store
    // delays release for one frame; it cannot release the scanned front early.
    if (!waitForSubmittedBuffer(stopping)) return false;
  }
  report(esp_timer_get_time());
  return true;
}

#ifdef AGON_EXTENDER_DIRECT_RGB888
bool HdmiOutput::startDirectSubmitter() {
  if(direct_task_) return true;
  return agon::extender::createVideoWorker(directSubmitEntry,"hdmi-swap",4096,this,6,&direct_task_,1)==pdPASS;
}

Rgb888PanelStorage HdmiOutput::panelStorage() {
  if(!ready_ || !direct_task_)return {};
  // Mode preparation has joined the old output/drawing service. Finish any
  // outstanding native selection before assigning the physical front/back.
  std::atomic<bool> never_stop{};
  if(!waitForSubmittedBuffer(never_stop))return {};
  // Borrowing changes the contents/geometry independently of ordinary output.
  // Invalidate its border bookkeeping so a later native mode cannot reuse a
  // stale size and leave the borrowed image in its letterbox margins.
  buffer_width_[0]=buffer_width_[1]=0;
  buffer_height_[0]=buffer_height_[1]=0;
  portENTER_CRITICAL(&callback_mux_);
  const auto front=ownership_.writable(false);
  portEXIT_CRITICAL(&callback_mux_);
  direct_cancelled_.store(false,std::memory_order_release);
  return {{buffers_[0],buffers_[1]},buffer_count_,front,width(),height(),stride(),this,directSwap};
}

bool HdmiOutput::directSwap(void *context,unsigned target) {
  auto &self=*static_cast<HdmiOutput*>(context);
  if(!self.ready_ || target>=self.buffer_count_ ||
     self.direct_cancelled_.load(std::memory_order_acquire) || self.scanoutFailed())return false;
  self.direct_target_=target;
  self.direct_state_.store(Requested,std::memory_order_release);
  xTaskNotifyGive(self.direct_task_);
  for(;;) {
    const bool abandoned=self.direct_cancelled_.load(std::memory_order_acquire) || self.scanoutFailed();
    portENTER_CRITICAL(&self.callback_mux_);
    auto state=self.direct_state_.load(std::memory_order_acquire);
    // HDMI02-L: after Submitted, the worker has finished every panel access.
    // Cancellation/fault can now release the drawing waiter without waiting for
    // an IRQ which may never arrive. Requested must still join the worker;
    // changing it to Idle here could race a live draw_bitmap call and teardown.
    // Keep ownership_.pending intact: only actual DMA completion or joined
    // panel deletion permits the old front to be reused.
    if(abandoned && state==Submitted) {
      self.direct_state_.store(Failed,std::memory_order_release);
      state=Failed;
    }
    if(state==Complete || state==Failed) {
      self.direct_state_.store(Idle,std::memory_order_release);
      portEXIT_CRITICAL(&self.callback_mux_);
      return state==Complete && !abandoned;
    }
    portEXIT_CRITICAL(&self.callback_mux_);
    // Native exclusion stays held, but the independent core1 submitter and the
    // hardware frame clock remain runnable. No guessed reuse deadline.
    vTaskDelay(1);
  }
}

void HdmiOutput::directSubmitEntry(void *context) {
  auto &self=*static_cast<HdmiOutput*>(context);
  for(;;) {
    ulTaskNotifyTake(pdTRUE,portMAX_DELAY);
    if(self.configure_state_.load(std::memory_order_acquire)==1) {
      self.cleanup();
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
      agon_scanout_reset();
#endif
      self.timing_=self.requested_timing_;
      self.configure_state_.store(self.start()?2:3,std::memory_order_release);
      continue;
    }
    if(self.direct_state_.load(std::memory_order_acquire)!=Requested)continue;
    if(!self.waitForSubmittedBuffer(self.direct_cancelled_) || self.direct_cancelled_.load()) {
      self.direct_state_.store(Failed,std::memory_order_release);continue;
    }
    const auto target=self.direct_target_;
#if defined(AGON_EXTENDER_RENDER_BENCHMARK) && !defined(AGON_EXTENDER_BENCH_OFF)
    agon_bench::Scope cache(agon_bench::Cache);
#endif
#ifndef AGON_EXTENDER_BENCH_OFF
    if(esp_lcd_panel_draw_bitmap(self.panel_,0,0,self.width(),self.height(),self.buffers_[target])!=ESP_OK) {
      self.direct_state_.store(Failed,std::memory_order_release);continue;
    }
#endif
#ifdef AGON_EXTENDER_BENCH_OFF
    // Preserve next-vblank semantics on the software clock without DMA.
    const auto edge=std::uint32_t(StockFrameCounter{});
    while(std::uint32_t(StockFrameCounter{})==edge && !self.direct_cancelled_.load(std::memory_order_acquire))vTaskDelay(1);
    if(self.direct_cancelled_.load(std::memory_order_acquire)) {
      self.direct_state_.store(Failed,std::memory_order_release);continue;
    }
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
    if(self.rolling()) agon_scanout_commit(); // native swap staged the back-buffer scene before waiting
#endif
    // Driver selection and this metadata store share core1 with the DMA ISR.
    // An interrupt between them merely defers acknowledgment to the next one.
    portENTER_CRITICAL(&self.callback_mux_);
    self.ownership_.submitted(target);
    self.direct_state_.store(Submitted,std::memory_order_release);
#ifdef AGON_EXTENDER_BENCH_OFF
    self.ownership_.frameComplete();
    self.direct_state_.store(Complete,std::memory_order_release);
#endif
    portEXIT_CRITICAL(&self.callback_mux_);
  }
}
#endif

void HdmiOutput::report(std::int64_t now) {
  const auto elapsed = now - report_started_;
  if (elapsed < 10000000 || !report_updates_) return;
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  if (rolling()) {
  strip_probe_stats strips{};strip_async_stats copy{};
  strip_probe_read(&strips);strip_async_read(&copy);
  strip_fault_stats fault{};strip_fault_read(&fault);
  ESP_LOGI(kTag,"rolling blocks=%u frames=%u invalid=%u underruns=%u sequence=%u refill_max=%uus over=%u copy_max=%u compose_max=%u late=%u overlap=%u faults=%u lead_min=%u free_internal=%u first_fault=%u first_error=%u queued=%u queue_wait_max=%u",
    strips.blocks,strips.frames,strips.invalid,strips.underruns,strips.sequence_errors,
    strips.max_us,strips.over_budget,copy.copy_max_us,copy.compose_max_us,copy.late,copy.overlap,copy.faults,
    copy.min_ready_lead_us,(unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
    unsigned(fault.first_fault),unsigned(fault.first_error),unsigned(fault.queued),unsigned(fault.queue_wait_max_us));
  }
#endif
  const auto scanouts = scanouts_.load(std::memory_order_relaxed);
  ESP_LOGI(kTag, "window %.3fs: updates %.3f/s submissions %.3f/s scanout %.3fHz; convert wall mean/max %.3f/%.3fms cache %.3fms wait %.3fms swap-drops %u",
      elapsed / 1000000.0, report_updates_ * 1000000.0 / elapsed,
      report_submissions_ * 1000000.0 / elapsed,
      (scanouts - report_scanouts_) * 1000000.0 / elapsed,
      report_conversion_us_ / (1000.0 * report_updates_), report_conversion_max_us_ / 1000.0,
      report_cache_us_ / (1000.0 * report_updates_), report_wait_us_ / (1000.0 * report_updates_),
      static_cast<unsigned>(report_swap_drops_));
  report_started_ = now;
  report_scanouts_ = scanouts;
  report_updates_ = report_submissions_ = 0;
  report_swap_drops_ = 0;
  report_conversion_us_ = report_cache_us_ = report_wait_us_ = report_conversion_max_us_ = 0;
}
} // namespace agon::extender::display
