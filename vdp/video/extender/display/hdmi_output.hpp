// Fixed 720p HDMI sink. One joined stock-output task calls publish; the panel
// and its buffers persist across logical mode changes. No browser snapshot is
// created here. RGB-001 may borrow its pixel planes through an explicit DMA-
// acknowledged swap contract; ordinary native output retains row expansion.
#pragma once
#include <atomic>
#include <cstdint>
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_mipi_dsi.h"
#include "esp_lcd_panel_io.h"
#include "esp_ldo_regulator.h"
#include "driver/i2c_master.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "extender/display/hdmi_geometry.hpp"
#include "extender/display/hdmi_buffer_ownership.hpp"
#include "extender/display/rgb888_panel_storage.hpp"

namespace agon::extender::display {
class StockRuntimeController;

class HdmiOutput {
 public:
  using FrameCallback = bool (*)(void *);
  bool start();
  bool ready() const noexcept { return ready_; }
  bool bindFrameCallback(FrameCallback callback, void *context);
  // Join any callback already executing before releasing its owner's context.
  // A stale service cannot unbind the replacement service's callback.
  void unbindFrameCallback(void *expected_context);
  bool publish(StockRuntimeController &controller, std::atomic<bool> &stopping);
#ifdef AGON_EXTENDER_DIRECT_RGB888
  Rgb888PanelStorage panelStorage();
  void allowDirectSwaps() { direct_cancelled_.store(false,std::memory_order_release); }
#endif
 private:
  static bool frameComplete(esp_lcd_panel_handle_t,
                            esp_lcd_dpi_panel_event_data_t *, void *);
  bool waitForSubmittedBuffer(std::atomic<bool> &stopping);
  void cleanup();
  void report(std::int64_t now);
#ifdef AGON_EXTENDER_DIRECT_RGB888
  static void directSubmitEntry(void *);
  static bool directSwap(void *, unsigned);
  bool startDirectSubmitter();
  TaskHandle_t direct_task_{};
  // One requester is serialized by native exclusion. Neither the submitter
  // nor its DMA acknowledgment acquires that exclusion.
  enum DirectState : unsigned { Idle, Requested, Submitted, Complete, Failed };
  std::atomic<unsigned> direct_state_{Idle};
  std::atomic<bool> direct_cancelled_{};
  unsigned direct_target_{};
#endif

  bool ready_{};
  esp_ldo_channel_handle_t phy_power_{};
  i2c_master_bus_handle_t i2c_{};
  esp_lcd_panel_io_handle_t io_[3]{};
  esp_lcd_dsi_bus_handle_t dsi_{};
  esp_lcd_panel_handle_t panel_{};
  std::uint8_t *buffers_[2]{};
  unsigned buffer_count_{};
  HdmiBufferOwnership ownership_;
  int buffer_width_[2]{}, buffer_height_[2]{};
  std::atomic<std::uint32_t> scanouts_{};
  std::atomic<std::uint32_t> interrupt_core_{UINT32_MAX};
  portMUX_TYPE callback_mux_ = portMUX_INITIALIZER_UNLOCKED;
  FrameCallback frame_callback_{};
  void *frame_context_{};
  std::int64_t report_started_{};
  std::uint32_t report_scanouts_{};
  std::uint32_t report_updates_{}, report_submissions_{};
  std::uint32_t report_swap_drops_{};
  std::uint64_t report_conversion_us_{}, report_cache_us_{}, report_wait_us_{};
  std::uint64_t report_conversion_max_us_{};
};

HdmiOutput &hdmiOutput();
} // namespace agon::extender::display
