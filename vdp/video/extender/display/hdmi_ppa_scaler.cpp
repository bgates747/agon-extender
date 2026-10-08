// The pinned ESP-IDF5.5.5 SRM implementation supplies bilinear filtering.
// Reuse its cache/transaction contract; no custom scaling or sprite algorithm.
#include "extender/display/hdmi_ppa_scaler.hpp"
#include "driver/ppa.h"
#include "esp_heap_caps.h"
#include "esp_cache.h"
#include "sdkconfig.h"
#include <algorithm>

namespace agon::extender::display {
bool HdmiPpaScaler::initialize() {
  if(source_ && client_)return true;
  const auto alignment=std::max(CONFIG_CACHE_L1_CACHE_LINE_SIZE,CONFIG_CACHE_L2_CACHE_LINE_SIZE);
  source_=static_cast<std::uint8_t *>(heap_caps_aligned_alloc(alignment,320*240*3,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
  if(!source_)return false;
  ppa_client_config_t config{};config.oper_type=PPA_OPERATION_SRM;config.max_pending_trans_num=1;
  ppa_client_handle_t client{};
  if(ppa_register_client(&config,&client)!=ESP_OK){reset();return false;}
  client_=client;return true;
}
void HdmiPpaScaler::reset() {
  if(client_)ppa_unregister_client(static_cast<ppa_client_handle_t>(client_));
  client_=nullptr;heap_caps_free(source_);source_=nullptr;
}
bool HdmiPpaScaler::scale(std::uint8_t *output,std::size_t bytes) {
  if(!client_ || !source_ || bytes!=848*480*3)return false;
  // Preserve CPU-cleared sidebars before the driver invalidates the output.
  if(esp_cache_msync(output,bytes,ESP_CACHE_MSYNC_FLAG_DIR_C2M)!=ESP_OK)return false;
  ppa_srm_oper_config_t op{};
  op.in.buffer=source_;op.in.pic_w=op.in.block_w=320;op.in.pic_h=op.in.block_h=240;
  op.in.srm_cm=PPA_SRM_COLOR_MODE_RGB888;
  op.out.buffer=output;op.out.buffer_size=bytes;op.out.pic_w=848;op.out.pic_h=480;
  op.out.block_offset_x=104;op.out.srm_cm=PPA_SRM_COLOR_MODE_RGB888;
  op.rotation_angle=PPA_SRM_ROTATION_ANGLE_0;op.scale_x=op.scale_y=2.0f;
  op.mode=PPA_TRANS_MODE_BLOCKING;
  if(ppa_do_scale_rotate_mirror(static_cast<ppa_client_handle_t>(client_),&op)!=ESP_OK)return false;
  // Future CPU reads and the driver's C2M submission must see only PPA bytes.
  return esp_cache_msync(output,bytes,ESP_CACHE_MSYNC_FLAG_DIR_M2C)==ESP_OK;
}
}
